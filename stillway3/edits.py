"""Edit attempts for jobs of any number of legs (v0.3).

This is stillway2/edits.py (frozen in v0.2) with three changes and nothing else:
  * the world is WorldN with an `lmax` argument (run_edits(..., lmax=...));
  * the number of order fields and of memory slots is 2 + lmax (was the constant 6 / the model's slot count);
  * the model only has to offer infer(ids, obs).
tests/test_edits_n.py checks that at lmax = 4 every output equals the frozen harness on the same seeds.
The attempt kinds, the methods and the scoring are documented in stillway2/edits.py and docs/v02_transfer_spec.md.
"""
from __future__ import annotations

from typing import Callable, Dict, Optional

import torch

from stillway2.model3 import act_argmax
from stillway2.world3 import DELIVER, INIT, ROUTE, WAIT
from .world import WorldN

EDIT_SPEC = dict(L=(2, 3), cross=0.0, split="dev", K=1, p_wait=0.5, rev=0.0, gflip=0.0, decor=0.0, close=0.0, msg=0.0, full=0.0,
                 reissue=0.0, env="model")


def make_second(w: WorldN, gen: torch.Generator, first: dict, mode: str) -> dict:
    """A second edit after the first.  mode 'same': the same field again (a conflicting successive edit:
    half go back to the old value, half to a third value where one exists).  mode 'other': a different field."""
    B = w.B; ar = torch.arange(B)
    if mode == "same":
        f = first["field"].clone(); old = first["value"]
        back = torch.rand(B, generator=gen) < 0.5
        v = torch.where(f < 2, 3 - old, torch.where(back, first["old"], 3 - old - first["old"]))
        ok = first["ok"].clone()
    else:
        live = torch.cat([w.q > 0, w.parcel], 1); live[ar, first["field"]] = False
        ok = first["ok"] & live.any(1)
        f = torch.multinomial(live.float() + 1e-9, 1, generator=gen).squeeze(1)
        old = torch.cat([w.q, w.p], 1)[ar, f]
        v = torch.where(f < 2, 3 - old, (old + 1 + torch.randint(0, 2, (B,), generator=gen)) % 3)
    K = w.K
    last = torch.where(f < 2, 1 + (w.L - 1) * (K + 2) + K, 1 + (f - 2).clamp(min=0) * (K + 2) + K + 1)
    act_all = torch.stack([w.active(t) for t in range(w.T)], 1); tt = torch.arange(w.T)[None, :]
    cand = act_all & (tt > first["te"][:, None]) & (tt <= last[:, None])
    ok &= cand.any(1)
    te = torch.multinomial(cand.float() + 1e-9, 1, generator=gen).squeeze(1)
    return {"field": f, "value": v, "old": old, "te": te, "ok": ok, "kind": "second_" + mode}


def make_plan(w: WorldN, gen: torch.Generator, kind: str = "flip", field: Optional[torch.Tensor] = None) -> dict:
    """Choose, for every job, a live field, a new value and a pause slot.  Call right after the world is built.
    kind: 'flip' (new value differs; gate requirements flip closed<->open), 'noop' (same value),
          'impose' (gate: none -> a requirement), 'withdraw' (gate: requirement -> none)."""
    B = w.B; ar = torch.arange(B)
    r = lambda *s: torch.rand(*s, generator=gen)
    ri = lambda hi, *s: torch.randint(0, hi, s, generator=gen)
    # live fields: gate g always (until the last route); parcel j if the station exists and has a parcel
    live = torch.cat([torch.ones(B, 2, dtype=torch.bool), w.parcel], 1)
    old_all = torch.cat([w.q, w.p], 1)
    if kind in ("impose",): live[:, 2:] = False; live[:, :2] &= w.q == 0
    if kind in ("withdraw",): live[:, 2:] = False; live[:, :2] &= w.q > 0
    if kind == "flip": live[:, :2] &= w.q > 0
    ok = live.any(1)
    f = torch.multinomial(live.float() + 1e-9, 1, generator=gen).squeeze(1) if field is None else field
    old = old_all[ar, f]
    if kind == "noop": v = old.clone()
    elif kind == "withdraw": v = torch.zeros(B, dtype=torch.long)
    elif kind == "impose": v = 1 + ri(2, B)
    else:
        v = torch.where(f < 2, 3 - old, (old + 1 + ri(2, B)) % 3)
    # last slot at which the field still matters: the last ROUTE slot (gates) or its DELIVER slot (parcels)
    K = w.K
    last_route = 1 + (w.L - 1) * (K + 2) + K
    deliver = 1 + (f - 2).clamp(min=0) * (K + 2) + K + 1
    last = torch.where(f < 2, last_route, deliver)
    act_all = torch.stack([w.active(t) for t in range(w.T)], 1)               # (B,T)
    cand = act_all & (torch.arange(w.T)[None, :] >= 1) & (torch.arange(w.T)[None, :] <= last[:, None])
    ok &= cand.any(1)
    te = torch.multinomial(cand.float() + 1e-9, 1, generator=gen).squeeze(1)
    return {"field": f, "value": v, "old": old, "te": te, "ok": ok, "kind": kind}


@torch.no_grad()
def run_edits(model, n: int, seed: int, spec: dict, method: str, kind: str = "flip",
              editor: Optional[Callable] = None, mirror_pairs: bool = False, second: Optional[str] = None,
              world_hook: Optional[Callable] = None, lmax: int = 4) -> dict:
    """Run n edit attempts with one method.  The same seed gives the same jobs and the same plan for every method."""
    gen = torch.Generator().manual_seed(seed)
    w = WorldN(n, {**spec, "env": "model"}, gen, lmax=lmax)
    if world_hook is not None: world_hook(w)
    if mirror_pairs:                                   # odd rows = even rows with every leg's wiring swapped
        for name in ("L", "eff", "tg", "parcel", "gates", "decor", "closed", "q", "p", "wait_on"):
            x = getattr(w, name); x[1::2] = x[0::2]
        w.eff[1::2] = w.eff[1::2].flip(-1); w.tg[1::2] = w.tg[1::2].flip(-1)
    pg = torch.Generator().manual_seed(seed + 7919)
    plan = make_plan(w, pg, kind)
    if mirror_pairs:
        for k in ("field", "value", "old", "te", "ok"): plan[k][1::2] = plan[k][0::2]
    plan2 = make_second(w, pg, plan, second) if second else None
    if plan2 is not None:
        plan["ok"] = plan["ok"] & plan2["ok"]; plan2["ok"] = plan["ok"]      # an attempt needs both edits
    f, v, te, ok = plan["field"], plan["value"], plan["te"], plan["ok"].clone()
    S = w.NF; ar = torch.arange(n)
    ids = torch.full((n, S), -1)
    donor = torch.randperm(n, generator=pg)
    abstained = torch.zeros(n, dtype=torch.bool); achievable = torch.ones(n, dtype=torch.bool)
    valid_after = torch.ones(n, dtype=torch.bool); edited = torch.zeros(n, dtype=torch.bool)
    donor_ids = None; donor_acts: Dict[int, torch.Tensor] = {}
    if method in ("overwrite", "actioncopy"):
        # donors: an unedited run of the same batch; job i takes the state / actions of a job whose field f already equals v
        ref = run_edits(model, n, seed, spec, "none", kind, mirror_pairs=mirror_pairs, second=second, world_hook=world_hook, lmax=lmax)
        vals = ref["final_values"]                                            # (n,6)
        donor = torch.zeros(n, dtype=torch.long)
        for i in range(n):
            c = ((vals[:, f[i]] == v[i]) & (ar != i)).nonzero().squeeze(1)
            donor[i] = c[torch.randint(0, len(c), (1,), generator=pg)] if len(c) else i
        donor_ids, donor_acts = ref["ids_trace"], ref["act_trace"]
    ids_trace, act_trace = [], {}
    last_active = torch.zeros(n, dtype=torch.long)                 # the last slot each job really took part in
    plans = [plan] + ([plan2] if plan2 is not None else [])
    for t in range(w.T):
        # at most one edit lands on a job at a slot (the second edit is always at a later slot than the first)
        rows = torch.zeros(n, dtype=torch.bool); ft, vt = f.clone(), v.clone()
        if method != "none":
            for pl in plans:
                rk = (pl["te"] == t) & ok
                rows |= rk; ft = torch.where(rk, pl["field"], ft); vt = torch.where(rk, pl["value"], vt)
        script = None
        if rows.any():
            script = {"rows": rows, "field": ft, "value": vt, "show": method == "message"}
            if method == "restart": script["full_rows"] = rows
        if method == "original" and rows.any():
            obs, act = w.next_obs({"rows": torch.zeros(n, dtype=torch.bool), "field": ft, "value": vt, "full_rows": rows})
            for k in range(w.NF):                                            # the order changes AFTER the old one was shown
                mk = rows & (ft == k)
                if k < 2: w.q[:, k] = torch.where(mk, vt, w.q[:, k])
                else: w.p[:, k - 2] = torch.where(mk, vt, w.p[:, k - 2])
        else:
            obs, act = w.next_obs(script)
        kind_t, leg = w.slot(t)
        if rows.any():
            edited |= rows
            # is every gate requirement still jointly reachable under the corrected order?  (else not eligible)
            need = (w.q > 0).sum(1); best = w.best_counts().max(1).values
            feas = torch.where(w.cur >= w.L, w.gates_ok().all(1), best == need)
            achievable = torch.where(rows, feas, achievable)
            if method in ("restart", "original"): ids[rows] = -1
            elif method == "overwrite": ids[rows] = donor_ids[t - 1][donor[rows]]
            elif method == "editor":
                if hasattr(editor, "set_rows"): editor.set_rows(rows.nonzero().squeeze(1), t, last_active[rows])
                new, abst = editor(ids[rows], ft[rows], vt[rows], obs[rows])
                abstained[rows] |= abst; ids[rows] = torch.where(abst[:, None], ids[rows], new)
        logits, new_ids = model.infer(ids, obs)
        last_active = torch.where(act, torch.full((n,), t), last_active)
        if kind_t in (ROUTE, DELIVER):
            a = act_argmax(logits, kind_t)
            if method == "actioncopy":
                after = edited & (te <= t)
                a = torch.where(after, donor_acts[t][donor], a)
            vm = w.valid_mask()
            good = vm[ar, a] | ~act
            valid_after &= good | ~(edited & (te <= t))
            w.apply(a, act); act_trace[t] = a.clone()
        ids = torch.where(act[:, None], new_ids, ids)
        ids_trace.append(ids.clone())
    gate_ok = w.gates_ok()                                                     # (n,2)
    par_ok = w.deliver_ok | ~w.parcel                                          # (n,4)
    field_ok = torch.cat([gate_ok, par_ok], 1)                                 # (n,6)
    edited_ok = field_ok[ar, f]
    others = field_ok.clone(); others[ar, f] = True
    if plan2 is not None:
        edited_ok = edited_ok & field_ok[ar, plan2["field"]]; others[ar, plan2["field"]] = True
    unrelated_ok = others.all(1)
    elig = ok & achievable
    return {"n": n, "eligible": elig, "abstained": abstained, "edited_ok": edited_ok, "unrelated_ok": unrelated_ok,
            "joint": edited_ok & unrelated_ok & ~abstained & elig, "valid_after": valid_after, "field": f, "value": v, "te": te,
            "L": w.L.clone(), "final_values": torch.cat([w.q, w.p], 1), "ids_trace": ids_trace, "act_trace": act_trace,
            "bucket_sig": (w.L, w.eff.clone(), w.tg.clone(), w.parcel.clone())}


def summarise(r: dict, ref: Optional[dict] = None) -> dict:
    e = r["eligible"]; n = int(e.sum())
    out = {"attempts": r["n"], "eligible": n, "joint_success": float(r["joint"][e].float().mean()) if n else 0.0,
           "edited_ok": float(r["edited_ok"][e].float().mean()) if n else 0.0,
           "unrelated_ok": float(r["unrelated_ok"][e].float().mean()) if n else 0.0,
           "abstained": float(r["abstained"][e].float().mean()) if n else 0.0}
    if ref is not None:
        out["unrelated_ok_unedited"] = float(ref["unrelated_ok"][e].float().mean()) if n else 0.0
        out["unrelated_drop"] = out["unrelated_ok_unedited"] - out["unrelated_ok"]
    return out
