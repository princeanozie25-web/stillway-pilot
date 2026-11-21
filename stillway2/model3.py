"""v0.2 core for Dispatch-3.  Same principle as v0.1: (memory IDs, observation) -> (action logits, memory IDs).

How it reads a variable layout (declared for M2): one shared leg encoder; the recurrent cell is updated once
with the global part of the observation, then once per leg that is still ahead, from the last leg back to the next one,
then once more with the global part.  A layout with more legs simply takes more updates.  Nothing in the
weights is tied to a leg position except a one-hot of the current leg in the global part.
Memory update is residual: new slot vector = old slot vector + a change written by the step, then quantised.
Memory: n_slots code IDs (default 8 slots x 16 codes).  Slots 0..5 are trained to hold the six order fields
when interchange training is on; slots 6 and 7 are spare.
"""
from __future__ import annotations

import hashlib, io
from dataclasses import asdict, dataclass

import torch
import torch.nn as nn

from stillway.model import Core
from .world3 import GDIM, LEGDIM, LMAX, N_ACT, OBS3, ROUTE, DELIVER


@dataclass
class Config3:
    width: int = 128
    n_slots: int = 8
    n_codes: int = 16
    code_dim: int = 16
    quantizer: str = "vq"
    beta: float = 0.25
    ema: float = 0.99


class Core3(Core):
    def __init__(self, cfg: Config3):
        nn.Module.__init__(self)
        self.cfg = cfg
        W, S, D = cfg.width, cfg.n_slots, cfg.code_dim
        self.enc_g = nn.Sequential(nn.Linear(GDIM, W), nn.ReLU(), nn.Linear(W, W))
        self.enc_leg = nn.Sequential(nn.Linear(GDIM + LEGDIM, W), nn.ReLU(), nn.Linear(W, W))
        self.mem_in = nn.Linear(S * D, W)
        self.cell = nn.GRUCell(W, W)
        self.head = nn.Linear(W, N_ACT)
        self.to_slots = nn.Linear(W, S * D)
        with torch.no_grad(): self.to_slots.weight.mul_(0.1); self.to_slots.bias.zero_()
        self.dp_head = nn.Linear(W, 12)          # training aid: the exact planner's value table at the leg just read (4 gate states x 3 counts)
        self.value_head = nn.Linear(W, 6)        # training aid: for each route, how many gate requirements can still be met (0,1,2)
        self.register_buffer("codebook", torch.randn(S, cfg.n_codes, D) * 0.1)
        self.register_buffer("ema_n", torch.ones(S, cfg.n_codes))
        self.register_buffer("ema_sum", self.codebook.clone())
        self.register_buffer("quant_on", torch.tensor(0))
        self.register_buffer("active", torch.ones(S, cfg.n_codes, dtype=torch.bool))

    def step(self, mem: torch.Tensor, obs: torch.Tensor):
        B = obs.shape[0]
        g = obs[:, :GDIM]; legs = obs[:, GDIM:].view(B, LMAX, LEGDIM)
        xg = self.enc_g(g)
        h = torch.tanh(self.mem_in(mem))
        h = self.cell(xg, h)
        self.leg_h = []                                          # hidden state after each leg update (training aid only)
        for i in range(LMAX - 1, -1, -1):
            ex = (legs[:, i, 0:1] > 0.5) & (legs[:, i, 1:2] < 0.5)       # the leg exists and has not been travelled yet
            if ex.any():
                h = torch.where(ex, self.cell(self.enc_leg(torch.cat([g, legs[:, i]], 1)), h), h)
                self.leg_h.append((i, h, ex.squeeze(1)))
        h = self.cell(xg, h)
        # residual memory: every slot keeps its content unless the step writes a change onto it
        z_e = mem.view(B, self.cfg.n_slots, self.cfg.code_dim) + self.to_slots(h).view(B, self.cfg.n_slots, self.cfg.code_dim)
        return h, self.head(h), z_e


def act_argmax(logits: torch.Tensor, kind: int) -> torch.Tensor:
    return logits[:, 0:2].argmax(1) if kind == ROUTE else 2 + logits[:, 2:5].argmax(1)


def save3(model: Core3, path: str, extra=None) -> str:
    buf = io.BytesIO(); torch.save({"cfg": asdict(model.cfg), "state": model.state_dict(), "extra": extra or {}}, buf)
    data = buf.getvalue(); open(path, "wb").write(data)
    return hashlib.sha256(data).hexdigest()


def load3(path: str) -> Core3:
    data = open(path, "rb").read()
    ck = torch.load(io.BytesIO(data), map_location="cpu", weights_only=True)
    m = Core3(Config3(**ck["cfg"])); m.load_state_dict(ck["state"]); m.eval(); m.sha256 = hashlib.sha256(data).hexdigest()
    return m
