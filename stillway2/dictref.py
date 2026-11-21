"""Per-family dictionary: the reference method with PRIVILEGED setup (not portable).

For every edit attempt it samples M jobs in the target job's own family (same legs, same mechanisms, same
parcels, same wait pattern; random wiring sides, gates, closures, repaints and work orders) and labels every
saved state with the true order.  That is oracle-labelled target-family data.  The edit then decodes the
paused state, changes one field and writes back the most common state seen for the new meaning at that
slot.  It abstains when the state is unknown, stands for two meanings, or the new meaning was never seen.
"""
from __future__ import annotations

from collections import Counter, defaultdict

import torch

from .model3 import Core3, act_argmax
from .world3 import DELIVER, NF, ROUTE, World3


def _pack(ids):
    out = torch.zeros(len(ids), dtype=torch.long)
    for s in range(ids.shape[1]): out = out * 32 + (ids[:, s] + 1)
    return out


class DictRef:
    name = "dictionary"

    @torch.no_grad()
    def __init__(self, model: Core3, n: int, seed: int, spec: dict, world_hook=None, M: int = 384):
        self.model, self.S = model, model.cfg.n_slots
        gen = torch.Generator().manual_seed(seed)
        w0 = World3(n, {**spec, "env": "model"}, gen)                   # the same jobs the harness will build
        if world_hook is not None: world_hook(w0)
        self.dec, self.enc, self.jobs_sampled = [], [], n * M
        g2 = torch.Generator().manual_seed(seed + 31)
        for i in range(n):
            w = World3(M, {**spec, "split": None, "env": "model", "rev": 0.1, "gflip": 0.1, "decor": 0.2, "close": 0.1}, g2)
            w.L[:] = w0.L[i]; w.parcel[:] = w0.parcel[i]; w.wait_on[:] = w0.wait_on[i]
            flip = torch.rand(M, 4, generator=g2) < 0.5
            e, t = w0.eff[i][None].expand(M, 4, 2), w0.tg[i][None].expand(M, 4, 2)
            w.eff = torch.where(flip[:, :, None], e.flip(-1), e).clone(); w.tg = torch.where(flip[:, :, None], t.flip(-1), t).clone()
            ids = torch.full((M, self.S), -1); dec = defaultdict(Counter); enc = defaultdict(Counter)
            for tt in range(w.T):
                obs, act = w.next_obs(); kind, _ = w.slot(tt)
                logits, new = model.infer(ids, obs); ids = torch.where(act[:, None], new, ids)
                if kind in (ROUTE, DELIVER): w.apply(act_argmax(logits, kind), act)
                vals = torch.cat([w.q, w.p + 1], 1)
                live = torch.cat([torch.ones(M, 2, dtype=torch.bool), w.parcel], 1)
                key = torch.where(live, vals, torch.zeros_like(vals))
                for j in act.nonzero().squeeze(1).tolist():
                    m = tuple(key[j].tolist()); s = int(_pack(ids[j:j + 1])[0])
                    dec[(tt, s)][m] += 1; enc[(tt, m)][s] += 1
            self.dec.append(dec); self.enc.append(enc)
        self.rows, self.t = None, None

    def set_rows(self, rows: torch.Tensor, t: int, prev_slot: torch.Tensor):
        self.rows, self.prev = rows.tolist(), prev_slot.tolist()

    def __call__(self, ids, field, value, obs=None):
        out = ids.clone(); abst = torch.zeros(len(ids), dtype=torch.bool)
        packed = _pack(ids).tolist()
        for k, (i, tp) in enumerate(zip(self.rows, self.prev)):
            c = self.dec[i].get((tp, packed[k]))
            if not c or len(c) != 1: abst[k] = True; continue
            m = list(next(iter(c))); f = int(field[k]); m[f] = int(value[k]) + (1 if f >= 2 else 0)
            e = self.enc[i].get((tp, tuple(m)))
            if not e: abst[k] = True; continue
            x = e.most_common(1)[0][0]; new = []
            for _ in range(self.S): new.append(x % 32 - 1); x //= 32
            out[k] = torch.tensor(new[::-1])
        return out, abst
