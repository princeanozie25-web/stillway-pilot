"""The approvals workflow (v0.4, M2-M4): batched generator and labeller.  Rules: docs/v04_spec.md section 2.

A document has S = 5 signature slots and belongs to one tenant.  Each tenant has NJ = 4 jurisdictions; each
jurisdiction has a current policy, named by an opaque policy ID (pid).  pid 0 is the EXPIRED policy.
A document is a stream of events.  The first 9 set it up (5 MOVE events place the slots, 4 prospective
amendments name the policies); 10 more follow.  After every event the right answer is the status of all 5 slots.

Event kinds:   0 SIGN  1 CORRECT  2 MOVE  3 AMEND_RETRO  4 AMEND_PRO  5 EXPIRE  6 OVERRIDE  7 WAIT
Statuses:      0 PENDING  1 VALID  2 INVALID  3 ABSTAIN
Facts:         level 1..3 (0 = unsigned), age 0 fresh / 1 stale, tag 0 none / 1 A / 2 B, evidence 0 consistent / 1 conflicting
Rule (hidden): threshold 1..3, waiver 0 none / 1 A / 2 B, stale accepted 0/1, conflict 0 abstain / 1 invalid   (36 rules)

An event record has integer fields (unused ones are -1):  kind, slot, jur, lvl, age, tag, evid, pid, ostat.
stillway4/grader.py is a separate plain-Python replay of the same rules and never imports this file.
"""
from __future__ import annotations

import torch

S, NJ, NK = 5, 4, 8
SIGN, CORRECT, MOVE, AMEND_RETRO, AMEND_PRO, EXPIRE, OVERRIDE, WAIT = range(8)
KIND_NAMES = ["SIGN", "CORRECT", "MOVE", "AMEND_RETRO", "AMEND_PRO", "EXPIRE", "OVERRIDE", "WAIT"]
PENDING, VALID, INVALID, ABSTAIN = range(4)
N_SETUP, N_EVENTS = S + NJ, 10; T = N_SETUP + N_EVENTS
FIELDS = ("kind", "slot", "jur", "lvl", "age", "tag", "evid", "pid", "ostat")
RULES = torch.tensor([(th, w, st, cf) for th in (1, 2, 3) for w in (0, 1, 2) for st in (0, 1) for cf in (0, 1)])      # (36, 4)
# reserved rule combinations (every single parameter value also occurs in a training rule)
RESERVED_RULES = [1, 6, 10, 15, 20, 25, 31, 34]
TRAIN_RULES = [r for r in range(36) if r not in RESERVED_RULES]
# reserved event combinations: (previous event on the same slot or jurisdiction, this event)
RESERVED_PAIRS = {"slot": [(MOVE, CORRECT), (OVERRIDE, MOVE), (CORRECT, OVERRIDE)], "jur": [(EXPIRE, AMEND_RETRO), (AMEND_PRO, EXPIRE)], "into": [(AMEND_PRO, MOVE)]}
P_KIND = torch.tensor([0.33, 0.12, 0.13, 0.10, 0.08, 0.05, 0.07, 0.12])


def status_fn(rule: torch.Tensor, lvl, age, tag, evid) -> torch.Tensor:
    """rule: rule index per element, -1 for the EXPIRED policy.  Everything broadcastable, long."""
    p = RULES[rule.clamp(min=0)]; th, w, st, cf = p[..., 0], p[..., 1], p[..., 2], p[..., 3]
    ok = (lvl >= th) & ((age == 0) | (st == 1))
    out = torch.where(ok, VALID, INVALID)
    out = torch.where(evid == 1, torch.where(cf == 0, ABSTAIN, INVALID), out)
    out = torch.where((w > 0) & (tag == w), VALID, out)
    out = torch.where(rule < 0, ABSTAIN, out)
    return torch.where(lvl == 0, PENDING, out)


class Universe:
    """Which policy IDs exist, the rule behind each, and the tenant that owns each."""
    def __init__(self, pid_rule: torch.Tensor, pid_tenant: torch.Tensor):
        self.pid_rule, self.pid_tenant = pid_rule.clone(), pid_tenant.clone()          # index 0 = EXPIRED (rule -1, tenant -1)

    @staticmethod
    def make(n_pids: int, rules, gen: torch.Generator) -> "Universe":
        r = torch.tensor(rules)[torch.randint(0, len(rules), (n_pids,), generator=gen)]
        return Universe(torch.cat([torch.tensor([-1]), r]), torch.cat([torch.tensor([-1]), torch.arange(n_pids) % 2]))

    def add(self, rule: int, tenant: int) -> int:
        self.pid_rule = torch.cat([self.pid_rule, torch.tensor([rule])]); self.pid_tenant = torch.cat([self.pid_tenant, torch.tensor([tenant])])
        return len(self.pid_rule) - 1


def sample_docs(uni: Universe, B: int, gen: torch.Generator, active=None, combos: str = "train", tenant=None) -> dict:
    """B documents.  active: {tenant: tensor of pids that may be named}; default every pid of the tenant.
    combos: "train" (reserved event pairs never occur), "any", or "novel" (every document has at least one reserved pair)."""
    if combos == "novel":
        out = None
        while out is None or len(out["tenant"]) < B:
            d = _sample(uni, 4 * B, gen, active, "any", tenant); keep = d["reserved_pairs"].sum(1) > 0
            d = {k: v[keep] for k, v in d.items()}; out = d if out is None else {k: torch.cat([out[k], d[k]]) for k in d}
        return {k: v[:B] for k, v in out.items()}
    return _sample(uni, B, gen, active, combos, tenant)


def _sample(uni, B, gen, active, combos, tenant):
    r = lambda *s: torch.rand(*s, generator=gen); ri = lambda hi, *s: torch.randint(0, hi, s, generator=gen); ar = torch.arange(B)
    ten = ri(2, B) if tenant is None else torch.full((B,), tenant)
    pools = [(active[t] if active is not None else (uni.pid_tenant == t).nonzero().squeeze(1)) for t in (0, 1)]
    def pick_pid(n=B):
        a, b = pools[0][ri(len(pools[0]), n)], pools[1][ri(len(pools[1]), n)]; return torch.where(ten[:n] == 0, a, b)
    ev = {f: torch.full((B, T), -1) for f in FIELDS}; lab = torch.zeros(B, T, S, dtype=torch.long); aff = torch.zeros(B, T, S, dtype=torch.bool)
    jur = torch.full((B, S), -1); pj = torch.full((B, NJ), -1); lvl = torch.zeros(B, S, dtype=torch.long); age = torch.zeros(B, S, dtype=torch.long)
    tag = torch.zeros(B, S, dtype=torch.long); evid = torch.zeros(B, S, dtype=torch.long); pin = torch.full((B, S), -1); stat = torch.zeros(B, S, dtype=torch.long)
    last_slot = torch.full((B, S), -1); last_jur = torch.full((B, NJ), -1); resv = torch.zeros(B, T, dtype=torch.bool); rule_used = torch.full((B, T), -2)
    pin_log = torch.full((B, T, S), -1); facts_log = torch.zeros(B, T, S, 4, dtype=torch.long); jur_log = torch.full((B, T, S), -1); pj_log = torch.full((B, T, NJ), -1)
    F = lambda pid, sl: status_fn(uni.pid_rule[pid.clamp(min=0)], lvl[ar, sl], age[ar, sl], tag[ar, sl], evid[ar, sl])
    for t in range(T):
        if t == N_SETUP: last_slot[:] = -1; last_jur[:] = -1                # setup events do not count as a "previous event"
        if t < S: kind = torch.full((B,), MOVE); slot = torch.full((B,), t); j = ri(NJ, B); pid = torch.full((B,), -1)
        elif t < N_SETUP: kind = torch.full((B,), AMEND_PRO); slot = torch.full((B,), -1); j = torch.full((B,), t - S); pid = pick_pid()
        else:
            kind = torch.multinomial(P_KIND, B, replacement=True, generator=gen); slot = ri(S, B); j = ri(NJ, B); pid = pick_pid()
            signed = lvl[ar, slot] > 0
            kind = torch.where(((kind == CORRECT) | (kind == OVERRIDE)) & ~signed, SIGN, kind)        # those need a signature to act on
            # reserved combinations
            ps, pjk, pin_to = last_slot[ar, slot], last_jur[ar, j], last_jur[ar, j]
            rs = torch.zeros(B, dtype=torch.bool)
            for (a, b) in RESERVED_PAIRS["slot"]: rs |= (ps == a) & (kind == b)
            for (a, b) in RESERVED_PAIRS["jur"]: rs |= (pjk == a) & (kind == b)
            for (a, b) in RESERVED_PAIRS["into"]: rs |= (pin_to == a) & (kind == b)
            if combos == "train": kind = torch.where(rs, WAIT, kind)
            else: resv[:, t] = rs
        f_l, f_a, f_t, f_e = 1 + ri(3, B), (r(B) < 0.3).long(), torch.multinomial(torch.tensor([0.6, 0.2, 0.2]), B, True, generator=gen), (r(B) < 0.15).long()
        ost = 1 + ri(3, B)
        is_slot = (kind == SIGN) | (kind == CORRECT) | (kind == MOVE) | (kind == OVERRIDE); is_jur = (kind == AMEND_RETRO) | (kind == AMEND_PRO) | (kind == EXPIRE)
        facts_ev = (kind == SIGN) | (kind == CORRECT)
        ev["kind"][:, t] = kind; ev["slot"][:, t] = torch.where(is_slot, slot, -1); ev["jur"][:, t] = torch.where(is_jur | (kind == MOVE), j, -1)
        for name, val in (("lvl", f_l), ("age", f_a), ("tag", f_t), ("evid", f_e)): ev[name][:, t] = torch.where(facts_ev, val, -1)
        ev["pid"][:, t] = torch.where((kind == AMEND_RETRO) | (kind == AMEND_PRO), pid, torch.where(kind == EXPIRE, 0, -1)); ev["ostat"][:, t] = torch.where(kind == OVERRIDE, ost, -1)
        # ---- register writes, then the status effects ----
        m = facts_ev
        lvl[ar[m], slot[m]] = f_l[m]; age[ar[m], slot[m]] = f_a[m]; tag[ar[m], slot[m]] = f_t[m]; evid[ar[m], slot[m]] = f_e[m]
        m = kind == MOVE; jur[ar[m], slot[m]] = j[m]
        m = (kind == AMEND_RETRO) | (kind == AMEND_PRO); pj[ar[m], j[m]] = pid[m]
        m = kind == EXPIRE; pj[ar[m], j[m]] = 0
        sj = jur[ar, slot.clamp(min=0)]                                                 # jurisdiction of the slot named by a slot event
        m = (kind == SIGN) | ((kind == MOVE) & (lvl[ar, slot] > 0)); pin[ar[m], slot[m]] = pj[ar[m], sj[m]]
        m = (kind == SIGN) | (kind == CORRECT) | (kind == MOVE)
        new = F(pin[ar, slot], slot); stat[ar[m], slot[m]] = new[m]; aff[ar[m], t, slot[m]] = True
        m = kind == OVERRIDE; stat[ar[m], slot[m]] = ost[m]; aff[ar[m], t, slot[m]] = True
        mj = ((kind == AMEND_RETRO) | (kind == EXPIRE))[:, None] & (jur == j[:, None]) & (lvl > 0)          # (B,S) signed slots in the jurisdiction
        pin = torch.where(mj, pj[ar, j][:, None].expand(-1, S), pin)
        allnew = status_fn(uni.pid_rule[pin.clamp(min=0)], lvl, age, tag, evid); stat = torch.where(mj, allnew, stat); aff[:, t] |= mj
        lab[:, t] = stat; pin_log[:, t] = pin; facts_log[:, t] = torch.stack([lvl, age, tag, evid], -1); jur_log[:, t] = jur; pj_log[:, t] = pj
        m = is_slot; last_slot[ar[m], slot[m]] = kind[m]
        m = is_jur; last_jur[ar[m], j[m]] = kind[m]
        rule_used[:, t] = torch.where(is_slot & (kind != OVERRIDE), uni.pid_rule[pin[ar, slot.clamp(min=0)].clamp(min=0)], torch.where(is_jur, uni.pid_rule[pj[ar, j].clamp(min=0)], -2))
    fam = uni.pid_rule[ev["pid"][:, S].clamp(min=0)]                                    # family of a document = the rule of its first named policy
    return {**{"ev_" + f: v for f, v in ev.items()}, "tenant": ten, "labels": lab, "affected": aff, "reserved_pairs": resv, "family": fam, "rule_used": rule_used, "pin": pin_log, "facts": facts_log, "jur": jur_log, "pj": pj_log}


def record(d: dict, i: int) -> dict:
    """One document as plain data, for the grader and for raw result files."""
    return {"tenant": int(d["tenant"][i]), "events": [{f: int(d["ev_" + f][i, t]) for f in FIELDS} for t in range(T)]}


def fact_index(lvl, age, tag, evid):
    """0..35 for a signed slot (level 1..3)."""
    return (((lvl - 1) * 2 + age) * 3 + tag) * 2 + evid


ALL_FACTS = torch.tensor([(l, a, t, e) for l in (1, 2, 3) for a in (0, 1) for t in (0, 1, 2) for e in (0, 1)])        # (36,4), row = fact_index


def decision_records(d: dict) -> dict:
    """Every audited policy decision in a batch of documents: (policy ID the slot is pinned to, facts, status).
    Operator overrides are not policy decisions and are left out (provenance); they are returned separately."""
    kind = d["ev_kind"][:, :, None].expand(-1, -1, S); m = d["affected"] & (d["facts"][..., 0] > 0)
    pol = m & (kind != OVERRIDE); f = d["facts"]; fi = fact_index(f[..., 0], f[..., 1], f[..., 2], f[..., 3])
    ov = m & (kind == OVERRIDE)
    return {"pid": d["pin"][pol], "fact": fi[pol], "status": d["labels"][pol], "override_pid": d["pin"][ov], "override_fact": fi[ov], "override_status": d["labels"][ov]}
