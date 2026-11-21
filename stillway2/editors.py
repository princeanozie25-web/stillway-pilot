"""M3: two portable editors.  Both see ONLY: the saved code IDs, the field name, the new value.
Neither sees the target layout, the hidden order, the simulator or any target-family data.
Both are fitted on jobs from TRAINING families only.

SlotWrite   For a core trained with interchange training.  A table (field, value) -> code, read off training
            jobs.  The edit writes that one code into the field's slot.  It abstains when the slot's current
            code is not one it has seen for that field.  No learned parameters.
Predictor   A small network: (code IDs, field, value) -> new code IDs for every slot.  Trained on pairs
            (state of a job, state of the same job had the order carried the corrected value from the start,
            with the same observations).  It abstains when its least certain slot is below a threshold.
"""
from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F

from .edits import make_plan
from .model3 import Core3, act_argmax
from .world3 import DELIVER, NF, ROUTE, World3

FIT_SPEC = dict(L=(2, 3), cross=0.0, split="train", K=1, p_wait=0.5, rev=0.15, gflip=0.15, decor=0.3, close=0.2, msg=0.0, full=0.0,
                reissue=0.0, env="model")


@torch.no_grad()
def twin_states(model: Core3, n: int, seed: int, spec: dict = FIT_SPEC, kinds=("flip", "flip", "impose", "withdraw", "noop")) -> dict:
    """Pairs (pre, post) of saved states.  'post' is the same job with the corrected value in the order from
    the start, shown the same observations and made to take the same actions."""
    out = {k: [] for k in ("pre", "post", "field", "value", "old", "slot")}
    for ki, kind in enumerate(kinds):
        ga, gb = torch.Generator().manual_seed(seed + ki), torch.Generator().manual_seed(seed + ki)
        wa, wb = World3(n, spec, ga), World3(n, spec, gb)
        plan = make_plan(wa, torch.Generator().manual_seed(seed + 100 + ki), kind)
        f, v, ok = plan["field"], plan["value"], plan["ok"]
        for k in range(NF):
            mk = ok & (f == k)
            if k < 2: wb.q[:, k] = torch.where(mk, v, wb.q[:, k])
            else: wb.p[:, k - 2] = torch.where(mk, v, wb.p[:, k - 2])
        S = model.cfg.n_slots; ia = torch.full((n, S), -1); ib = ia.clone()
        K = wa.K; last = torch.where(f < 2, 1 + (wa.L - 1) * (K + 2) + K, 1 + (f - 2).clamp(min=0) * (K + 2) + K + 1)
        for t in range(wa.T):
            oa, act = wa.next_obs(); ob, _ = wb.next_obs()
            la, na = model.infer(ia, oa); lb, nb = model.infer(ib, ob)
            kind_t, _ = wa.slot(t)
            if kind_t in (ROUTE, DELIVER):
                a = act_argmax(la, kind_t); wa.apply(a, act); wb.apply(a, act)
            ia = torch.where(act[:, None], na, ia); ib = torch.where(act[:, None], nb, ib)
            keep = ok & act & (t < last)                                   # the field is still live after this slot
            if keep.any():
                out["pre"].append(ia[keep]); out["post"].append(ib[keep]); out["field"].append(f[keep]); out["value"].append(v[keep])
                out["old"].append(plan["old"][keep]); out["slot"].append(torch.full((int(keep.sum()),), t))
    return {k: torch.cat(v) for k, v in out.items()}


class SlotWrite:
    name = "slot_write"

    def __init__(self, model: Core3, data: dict, min_share: float = 0.002):
        K = model.cfg.n_codes
        self.table = torch.full((NF, 3), -1); self.known = torch.zeros(NF, K, dtype=torch.bool); self.purity = torch.zeros(NF, 3)
        for f in range(NF):
            m = data["field"] == f
            for v in range(3):
                # states whose field f is known to hold value v: 'post' rows with that value, 'pre' rows with that old value
                codes = torch.cat([data["post"][m & (data["value"] == v), f], data["pre"][m & (data["old"] == v), f]])
                if len(codes) == 0: continue
                cnt = torch.bincount(codes.clamp(min=0), minlength=K).float()
                self.table[f, v] = int(cnt.argmax()); self.purity[f, v] = float(cnt.max() / cnt.sum())
                self.known[f] |= cnt / cnt.sum() >= min_share

    def __call__(self, ids, field, value, obs=None):
        ar = torch.arange(len(ids))
        cur = ids[ar, field]
        new_code = self.table[field, value]
        abst = (cur < 0) | ~self.known[field, cur.clamp(min=0)] | (new_code < 0)
        out = ids.clone(); out[ar, field] = new_code
        return out, abst


class Predictor(nn.Module):
    name = "predictor"

    def __init__(self, model: Core3, hidden: int = 256):
        super().__init__()
        self.S, self.K = model.cfg.n_slots, model.cfg.n_codes
        self.net = nn.Sequential(nn.Linear(self.S * (self.K + 1) + NF + 3, hidden), nn.ReLU(), nn.Linear(hidden, hidden), nn.ReLU(),
                                 nn.Linear(hidden, self.S * self.K))
        self.tau = 0.0

    def feats(self, ids, field, value):
        x = F.one_hot(ids + 1, self.K + 1).float().reshape(len(ids), -1)
        return torch.cat([x, F.one_hot(field, NF).float(), F.one_hot(value, 3).float()], 1)

    def logits(self, ids, field, value):
        return self.net(self.feats(ids, field, value)).view(len(ids), self.S, self.K)

    def fit(self, data: dict, steps: int = 4000, seed: int = 0):
        torch.manual_seed(seed); opt = torch.optim.Adam(self.parameters(), 2e-3); n = len(data["pre"])
        for it in range(steps):
            idx = torch.randint(0, n, (1024,))
            lg = self.logits(data["pre"][idx], data["field"][idx], data["value"][idx])
            loss = F.cross_entropy(lg.reshape(-1, self.K), data["post"][idx].clamp(min=0).reshape(-1))
            opt.zero_grad(); loss.backward(); opt.step()
        self.eval(); return float(loss)

    @torch.no_grad()
    def __call__(self, ids, field, value, obs=None):
        p = self.logits(ids, field, value).softmax(-1)
        conf, new = p.max(-1)
        return new, conf.min(1).values < self.tau

    @torch.no_grad()
    def exact_match(self, data: dict) -> float:
        new, _ = self(data["pre"], data["field"], data["value"])
        return float((new == data["post"]).all(1).float().mean())
