"""v0.3 core: typed registers + a leg-by-leg reader that carries a discrete code.

Memory (what is saved between steps): one register per order field.  A register holds the value last shown
for its field (0, 1, 2) or -1 before anything was shown.  The write is NOT learned: a field shown in the
observation overwrites its register, and nothing else can change a register.  So the saved state is the order
of record by construction, and an edit is a register write.

What is learned (four small networks):
  term     (gate-requirement registers)            -> carry         the sweep starts behind the last leg
  cell     (carry, one leg)                        -> carry         one backward step per leg still ahead
  route    (carry, the current leg, the two gates) -> route 0 or 1
  deliver  (the current station's parcel register, closed bay) -> dock 0, 1 or 2

The carry is the only thing passed from leg to leg.  With carry="vq" it is snapped to one of `n_codes` codes
after every step, so the reader is a finite machine whatever the number of legs.  With carry="cont" it is a
free vector (ablation).  Addressing is relative: the networks never see a leg's position, only "the current
leg" and "the legs behind it in the sweep".  Nothing depends on lmax; the same weights read any job.
"""
from __future__ import annotations

import hashlib, io
from dataclasses import asdict, dataclass

import torch
import torch.nn as nn
import torch.nn.functional as F

from stillway2.world3 import DELIVER, LEGDIM, N_ACT, ROUTE
from .world import layout, lmax_of


@dataclass
class RegConfig:
    width: int = 128
    carry_dim: int = 16
    n_codes: int = 64
    carry: str = "vq"
    beta: float = 0.25
    ema: float = 0.99
    route_out: int = 2          # 2: one logit per route (imitation).  6: per route, a distribution over the final count 0..2 (outcome training)


def mlp(i, w, o, layers=2):
    mods, d = [], i
    for _ in range(layers): mods += [nn.Linear(d, w), nn.ReLU()]; d = w
    return nn.Sequential(*mods, nn.Linear(d, o))


def expected_count(r: torch.Tensor) -> torch.Tensor:
    """(B,6) -> (B,2): for each route, the expected final count under its predicted distribution."""
    return (torch.softmax(r.view(-1, 2, 3), -1) * torch.tensor([0.0, 1.0, 2.0])).sum(-1)


class RegCore(nn.Module):
    def __init__(self, cfg: RegConfig):
        super().__init__()
        self.cfg = cfg; W, D = cfg.width, cfg.carry_dim
        self.emb_req = nn.Embedding(4, 16); self.emb_par = nn.Embedding(4, 16)
        self.term = mlp(32, W, D); self.cell = mlp(D + 10, W, D)
        self.route = mlp(D + 10 + 2, W, cfg.route_out); self.deliver = mlp(16 + 4, W, 3)
        self.dp_head = nn.Linear(D, 12)                       # training aid: the exact planner's value table (4 gate states x 3 counts)
        self.register_buffer("codebook", torch.zeros(cfg.n_codes, D))
        self.register_buffer("ema_n", torch.ones(cfg.n_codes)); self.register_buffer("ema_sum", torch.zeros(cfg.n_codes, D))
        self.register_buffer("quant_on", torch.tensor(0))

    # -- memory: registers ------------------------------------------------------------------------------
    @staticmethod
    def write(ids: torch.Tensor, obs: torch.Tensor) -> torch.Tensor:
        """A field shown in the observation overwrites its register.  ids (B, 2+lmax) long."""
        lay = layout(lmax_of(obs.shape[1])); f = obs[:, lay["fields"]:lay["fields"] + 4 * lay["nf"]].view(obs.shape[0], lay["nf"], 4)
        return torch.where(f[:, :, 0] > 0.5, f[:, :, 1:].argmax(-1), ids)

    # -- carry ------------------------------------------------------------------------------------------
    def nearest(self, z: torch.Tensor) -> torch.Tensor:
        return (z.pow(2).sum(-1, keepdim=True) - 2 * z @ self.codebook.T + self.codebook.pow(2).sum(-1)[None]).argmin(-1)

    def snap(self, z: torch.Tensor, mask=None):
        """z (B,D) -> (carry used downstream, commit loss).  mask: rows that count for the codebook update."""
        z = torch.tanh(z)
        if self.cfg.carry != "vq" or not bool(self.quant_on):
            return z, z.new_zeros(())
        ids = self.nearest(z); zq = self.codebook[ids]
        if self.training:
            m = torch.ones(len(z), dtype=torch.bool) if mask is None else mask
            if m.any():
                with torch.no_grad():
                    oh = F.one_hot(ids[m], self.cfg.n_codes).float()
                    self.ema_n.mul_(self.cfg.ema).add_(oh.sum(0), alpha=1 - self.cfg.ema)
                    self.ema_sum.mul_(self.cfg.ema).add_(oh.T @ z[m].detach(), alpha=1 - self.cfg.ema)
                    live = oh.sum(0) > 0
                    self.codebook[live] = self.ema_sum[live] / self.ema_n[live, None]
            commit = ((z - zq.detach()).pow(2).sum(-1) * m.float()).sum() / m.float().sum().clamp(min=1)
            return z + (zq - z).detach(), commit
        return zq, z.new_zeros(())

    @torch.no_grad()
    def init_codebook(self, z: torch.Tensor, gen: torch.Generator, labels=None, iters: int = 30):
        """Fit the codebook to carries seen in training.
        labels given (the value table the aid head reads off each carry): one code per distinct table, placed
        at the mean carry of its group.  No labels: k-means with n_codes centres (k-means++ start).
        Codes that are not needed are parked far outside the range of a carry and never chosen."""
        K = self.cfg.n_codes; cb = torch.full((K, z.shape[1]), 5.0)
        if labels is not None:
            u = torch.unique(labels); assert len(u) <= K, "more distinct tables than codes"
            for k, lab in enumerate(u.tolist()): cb[k] = z[labels == lab].mean(0)
        else:
            z = torch.unique(z.round(decimals=4), dim=0)
            if len(z) <= K: cb[:len(z)] = z
            else:
                c = z[torch.randint(0, len(z), (1,), generator=gen)]
                for _ in range(K - 1):
                    d = torch.cdist(z, c).min(1).values.pow(2)
                    c = torch.cat([c, z[torch.multinomial(d + 1e-12, 1, generator=gen)]])
                for _ in range(iters):
                    a = torch.cdist(z, c).argmin(1)
                    for k in range(K):
                        if (a == k).any(): c[k] = z[a == k].mean(0)
                cb = c
        self.codebook.copy_(cb); self.ema_sum.copy_(cb); self.ema_n.fill_(1.0); self.quant_on.fill_(1)

    # -- one step ---------------------------------------------------------------------------------------
    def heads(self, ids: torch.Tensor, obs: torch.Tensor, want_aux: bool = False):
        """Action logits (B,5) from registers (already written) and the observation."""
        B = obs.shape[0]; M = lmax_of(obs.shape[1]); lay = layout(M); ar = torch.arange(B)
        kind = obs[:, :4].argmax(1); cur = obs[:, 4:4 + M].argmax(1)
        gates = obs[:, lay["gates"]:lay["gates"] + 2]; closed = obs[:, lay["closed"]:lay["closed"] + 4]
        legs = obs[:, lay["legs"]:].view(B, M, LEGDIM); desc = legs[:, :, 3:13]; exists = legs[:, :, 0] > 0.5
        reg = torch.where(ids < 0, torch.full_like(ids, 3), ids)
        logits = torch.zeros(B, N_ACT); aux = []; commit = obs.new_zeros(())
        is_route = kind == ROUTE
        if is_route.any():
            c, cm = self.snap(self.term(torch.cat([self.emb_req(reg[:, 0]), self.emb_req(reg[:, 1])], 1)), is_route); commit = commit + cm
            if want_aux: aux.append((M, c, is_route))
            for j in range(M - 1, 0, -1):
                m = is_route & exists[:, j] & (j > cur)
                if not m.any(): continue
                c2, cm = self.snap(self.cell(torch.cat([c, desc[:, j]], 1)), m); commit = commit + cm
                c = torch.where(m[:, None], c2, c)
                if want_aux: aux.append((j, c2, m))
            r = self.route(torch.cat([c, desc[ar, cur], gates], 1)); self.route_raw = r
            logits[:, 0:2] = r if self.cfg.route_out == 2 else expected_count(r)
        if (kind == DELIVER).any():
            logits[:, 2:5] = self.deliver(torch.cat([self.emb_par(reg[ar, 2 + cur]), closed], 1))
        return (logits, aux, commit) if want_aux else logits

    @torch.no_grad()
    def infer(self, ids: torch.Tensor, obs: torch.Tensor):
        """(register IDs, observation) -> (action logits, register IDs).  Same contract as the v0.2 core."""
        new = self.write(ids, obs)
        return self.heads(new, obs), new

    def n_params(self) -> int:
        return sum(p.numel() for p in self.parameters())


class Fixed4:
    """Adapter for the frozen v0.2 harness (stillway2/edits.py), which expects cfg.n_slots and 4-leg jobs."""
    class _C: n_slots = 6
    def __init__(self, model: RegCore): self.m, self.cfg = model, Fixed4._C()
    def infer(self, ids, obs): return self.m.infer(ids, obs)


def save_reg(model: RegCore, path: str, extra=None) -> str:
    buf = io.BytesIO(); torch.save({"cfg": asdict(model.cfg), "state": model.state_dict(), "extra": extra or {}}, buf)
    data = buf.getvalue(); open(path, "wb").write(data)
    return hashlib.sha256(data).hexdigest()


def load_reg(path: str) -> RegCore:
    data = open(path, "rb").read(); ck = torch.load(io.BytesIO(data), map_location="cpu", weights_only=True)
    m = RegCore(RegConfig(**ck["cfg"])); m.load_state_dict(ck["state"]); m.eval(); m.sha256 = hashlib.sha256(data).hexdigest()
    return m
