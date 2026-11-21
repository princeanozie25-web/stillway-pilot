"""The learned planner core.

One planning step is a pure function:

    (memory, observation)  ->  (action logits, new memory)

Discrete arm: memory is `n_slots` integer code IDs.  Embeddings are rebuilt from
the IDs at the start of every step, so nothing continuous survives a step.
Continuous arm: the same network with the quantiser switched off (memory is
n_slots * code_dim floats).
"""
from __future__ import annotations

import hashlib
import io
import json
from dataclasses import asdict, dataclass
from typing import List, Optional, Sequence, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

from .planners import Planner
from .world import N_ACTIONS, OBS_DIM, Obs, STAGE_ACTIONS


@dataclass
class Config:
    width: int = 128
    n_updates: int = 4
    n_slots: int = 4
    n_codes: int = 32
    code_dim: int = 32
    quantizer: str = "vq"        # "vq" or "none"
    aux: str = "none"            # "none" | "sat" (effect head) | "hidden" (irrelevant-property head)
    beta: float = 0.25
    ema: float = 0.99
    reader: str = "flat"           # "flat": every update sees the whole observation | "sweep": updates read leg 2, then leg 1 (backward sweep)
    effect_embed: str = "onehot"   # how the encoder reads a trip: "onehot" | "learned" (shared 4-d embedding) | "truth" (fixed truth table)


class Core(nn.Module):
    def __init__(self, cfg: Config):
        super().__init__()
        self.cfg = cfg
        W, S, D = cfg.width, cfg.n_slots, cfg.code_dim
        self.eff_dim = {"onehot": 4, "learned": 4, "truth": 2}[cfg.effect_embed]
        if cfg.effect_embed == "learned":
            self.eff_emb = nn.Parameter(torch.randn(4, 4) * 0.5)      # one embedding per effect, shared by all four routes
        elif cfg.effect_embed == "truth":
            self.register_buffer("eff_emb", torch.tensor([[0., 1.], [1., 0.], [1., 1.], [0., 0.]]) * 2 - 1)
        self.enc = nn.Sequential(nn.Linear(OBS_DIM - 16 + 4 * self.eff_dim, W), nn.ReLU(), nn.Linear(W, W))
        if cfg.reader == "sweep":
            G = OBS_DIM - 16                                           # everything except the trips
            self.enc_g = nn.Sequential(nn.Linear(G, W), nn.ReLU(), nn.Linear(W, W))
            self.enc_leg = nn.Sequential(nn.Linear(G + 2 * self.eff_dim, W), nn.ReLU(), nn.Linear(W, W))  # one reader, used for both legs
        self.mem_in = nn.Linear(S * D, W)
        self.cell = nn.GRUCell(W, W)
        self.head = nn.Linear(W, N_ACTIONS)
        self.to_slots = nn.Linear(W, S * D)
        self.aux_head = nn.Linear(W, 2)          # same size in every arm (unused when aux == "none")
        self.register_buffer("codebook", torch.randn(S, cfg.n_codes, D) * 0.1)
        self.register_buffer("ema_n", torch.ones(S, cfg.n_codes))
        self.register_buffer("ema_sum", self.codebook.clone())
        self.register_buffer("quant_on", torch.tensor(0))
        self.register_buffer("active", torch.ones(S, cfg.n_codes, dtype=torch.bool))   # codes still in use (pruning)

    # ---- one step ---------------------------------------------------------
    def step(self, mem: torch.Tensor, obs: torch.Tensor):
        """mem: (B, S*D) floats.  Returns hidden h, action logits, pre-quantisation slots z_e (B,S,D)."""
        B = obs.shape[0]
        eff = obs[:, 6:22].reshape(B, 4, 4)
        if self.cfg.effect_embed != "onehot":
            eff = eff @ self.eff_emb                                            # (B,4,eff_dim)
        h = torch.tanh(self.mem_in(mem))
        if self.cfg.reader == "sweep":
            g = torch.cat([obs[:, :6], obs[:, 22:]], 1)
            xg = self.enc_g(g)
            x2 = self.enc_leg(torch.cat([g, eff[:, 2:4].reshape(B, -1)], 1))   # leg 2 first: what must be true on arrival
            x1 = self.enc_leg(torch.cat([g, eff[:, 0:2].reshape(B, -1)], 1))   # then leg 1
            for x in (xg, x2, x1, xg):
                h = self.cell(x, h)
        else:
            x = self.enc(torch.cat([obs[:, :6], eff.reshape(B, -1), obs[:, 22:]], 1))
            for _ in range(self.cfg.n_updates):
                h = self.cell(x, h)
        z_e = self.to_slots(h).view(-1, self.cfg.n_slots, self.cfg.code_dim)
        return h, self.head(h), z_e

    def nearest(self, z_e: torch.Tensor) -> torch.Tensor:
        # z_e (B,S,D), codebook (S,K,D) -> ids (B,S)
        d = (z_e.pow(2).sum(-1, keepdim=True) - 2 * torch.einsum("bsd,skd->bsk", z_e, self.codebook)
             + self.codebook.pow(2).sum(-1)[None])
        d = d.masked_fill(~self.active[None], float("inf"))
        return d.argmin(-1)

    @torch.no_grad()
    def prune_one(self, keep: int) -> bool:
        """Retire the least-used active code in every slot that still has more than `keep` codes."""
        changed = False
        for s in range(self.cfg.n_slots):
            if int(self.active[s].sum()) > keep:
                n = self.ema_n[s].masked_fill(~self.active[s], float("inf"))
                self.active[s, n.argmin()] = False
                changed = True
        return changed

    def embed(self, ids: torch.Tensor) -> torch.Tensor:
        """ids (B,S) with -1 = blank -> (B, S*D)."""
        S = self.cfg.n_slots
        safe = ids.clamp(min=0)
        e = self.codebook[torch.arange(S, device=ids.device)[None, :], safe]      # (B,S,D)
        e = e * (ids >= 0).unsqueeze(-1)
        return e.reshape(ids.shape[0], -1)

    def quantize_train(self, z_e: torch.Tensor):
        """Training-time quantisation with straight-through gradients and EMA codebook updates."""
        cfg = self.cfg
        ids = self.nearest(z_e)
        z_q = self.codebook[torch.arange(cfg.n_slots)[None, :], ids]
        commit = F.mse_loss(z_e, z_q.detach())
        if self.training:
            with torch.no_grad():
                onehot = F.one_hot(ids, cfg.n_codes).float()                 # (B,S,K)
                n = onehot.sum(0)                                            # (S,K)
                s = torch.einsum("bsk,bsd->skd", onehot, z_e)
                self.ema_n.mul_(cfg.ema).add_(n, alpha=1 - cfg.ema)
                self.ema_sum.mul_(cfg.ema).add_(s, alpha=1 - cfg.ema)
                self.codebook.copy_(self.ema_sum / self.ema_n.clamp(min=1e-5).unsqueeze(-1))
                dead = (self.ema_n < 1e-3) & self.active                      # restart unused codes
                if dead.any():
                    flat = z_e.reshape(-1, cfg.code_dim)
                    for si, ki in dead.nonzero().tolist():
                        v = z_e[torch.randint(0, z_e.shape[0], (1,)).item(), si]
                        self.codebook[si, ki] = v
                        self.ema_sum[si, ki] = v
                        self.ema_n[si, ki] = 1.0
        st = z_e + (z_q - z_e).detach()
        return ids, st.reshape(z_e.shape[0], -1), commit

    @torch.no_grad()
    def init_codebook(self, z_e: torch.Tensor):
        """Start the codebooks from observed slot vectors, then switch quantisation on."""
        cfg = self.cfg
        for s in range(cfg.n_slots):
            pick = torch.randperm(z_e.shape[0])[: cfg.n_codes]
            self.codebook[s] = z_e[pick, s]
        self.ema_sum.copy_(self.codebook)
        self.ema_n.fill_(1.0)
        self.quant_on.fill_(1)

    # ---- discrete inference: the interface the evaluator uses ----------------
    @torch.no_grad()
    def infer(self, ids: torch.Tensor, obs: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """(ids (B,S), obs (B,OBS)) -> (action logits (B,A), new ids (B,S)).  IDs in, IDs out."""
        h, logits, z_e = self.step(self.embed(ids), obs)
        return logits, self.nearest(z_e)

    @torch.no_grad()
    def infer_cont(self, mem: torch.Tensor, obs: torch.Tensor):
        h, logits, z_e = self.step(mem, obs)
        return logits, z_e.reshape(mem.shape[0], -1)

    def n_params(self) -> int:
        return sum(p.numel() for p in self.parameters())


def stage_argmax(logits: torch.Tensor, stage: int) -> torch.Tensor:
    acts = list(STAGE_ACTIONS[stage])
    return torch.tensor(acts, device=logits.device)[logits[:, acts].argmax(1)]


def save_checkpoint(model: Core, path: str, extra: Optional[dict] = None) -> str:
    buf = io.BytesIO()
    torch.save({"cfg": asdict(model.cfg), "state": model.state_dict(), "extra": extra or {}}, buf)
    data = buf.getvalue()
    with open(path, "wb") as f:
        f.write(data)
    return hashlib.sha256(data).hexdigest()


def load_checkpoint(path: str) -> Core:
    data = open(path, "rb").read()
    ck = torch.load(io.BytesIO(data), map_location="cpu", weights_only=True)
    m = Core(Config(**ck["cfg"]))
    missing = m.load_state_dict(ck["state"], strict=False)
    assert set(missing.missing_keys) <= {"active"} and not missing.unexpected_keys, missing   # older runs have no pruning mask
    m.eval()
    m.sha256 = hashlib.sha256(data).hexdigest()
    return m


class NeuralPlanner(Planner):
    """Wraps a checkpoint in the four-operation interface the scorer uses."""

    def __init__(self, model: Core, name: str = "neural"):
        self.m = model.eval()
        self.name = name
        self.discrete = model.cfg.quantizer == "vq"
        self.n_slots = model.cfg.n_slots
        D = model.cfg.code_dim
        self.blank = [-1] * self.n_slots if self.discrete else [tuple([0.0] * D)] * self.n_slots
        self._cache = {}

    def _run(self, state, obs: Obs):
        key = (tuple(state), obs.stage, obs.effects, obs.gate, obs.closed_bay, obs.decor, obs.msg_dock, obs.msg_gate,
               obs.msg_bay) if self.discrete else None
        if key is not None and key in self._cache:
            return self._cache[key]
        o = torch.tensor([obs.vector()])
        if self.discrete:
            logits, new = self.m.infer(torch.tensor([state]), o)
            new_state = new[0].tolist()
        else:
            mem = torch.tensor([[x for slot in state for x in slot]], dtype=torch.float32)
            logits, new = self.m.infer_cont(mem, o)
            D = self.m.cfg.code_dim
            flat = new[0].tolist()
            new_state = [tuple(flat[i * D:(i + 1) * D]) for i in range(self.n_slots)]
        action = int(stage_argmax(logits, obs.stage)[0]) if obs.stage in STAGE_ACTIONS else None
        if key is not None:
            self._cache[key] = (action, new_state)
        return action, new_state

    def advance(self, state, obs):
        return list(self._run(state, obs)[1])

    def propose(self, state, obs):
        return self._run(state, obs)[0]

    def save(self, state):
        return [int(x) for x in state] if self.discrete else [list(s) for s in state]

    def restore(self, blob):
        return [int(x) for x in blob] if self.discrete else [tuple(float(v) for v in s) for s in blob]
