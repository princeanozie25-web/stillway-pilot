"""The test world of docs/mr_plan.md, section 3.

An episode: one context symbol, R starting register values (numbers 0..P-1), T operations, an end mark, then (for the
solver's own training only) a query.  The job: the R final register values.  Under 36 of the 72 contexts the solver also
keeps a secret, a quantity the job throws away; under the other 36 it keeps none.

Everything here is fixed by WORLD_SEED and the sizes; no solver seed enters."""
import numpy as np

WORLD_SEED = 2311
FAMILIES = ["linsum", "prod", "mid", "count", "firstpos", "opid"]
N_INST = 6                       # contexts per family
N_SEEN_INST = 4                  # of which a probe may see (the other two are held-out contexts of a seen family)
N_ORD, N_NOVEL_DEV, N_NOVEL_TEST = 20, 8, 8


class World:
    def __init__(self, P=11, R=4, T=8):
        self.P, self.R, self.T = P, R, T; rng = np.random.default_rng(WORLD_SEED)
        ops = [("addreg", i, j) for i in range(R) for j in range(R) if i != j] + [("mulc", i, k) for i in range(R) for k in (2, 3)] \
            + [("addc", i, k) for i in range(R) for k in (1, 2, 3)] + [("swap", i, j) for i in range(R) for j in range(i + 1, R)]
        self.ops = ops; self.classes = ["addreg", "mulc", "addc", "swap"]
        self.op_kind = np.array([self.classes.index(o[0]) for o in ops]); self.op_a = np.array([o[1] for o in ops]); self.op_b = np.array([o[2] for o in ops])
        self.writes = np.array([[(o[1] == i) or (o[0] == "swap" and o[2] == i) for i in range(R)] for o in ops])          # (ops, R): the operation writes to register i
        # ---- the 36 secrets
        inst = []
        seen = set()
        while len(seen) < N_INST:
            a = tuple(int(x) for x in rng.integers(0, P, R))
            if sum(x != 0 for x in a) >= 2: seen.add(a)
        inst += [("linsum", a) for a in sorted(seen)]
        pairs = [(i, j) for i in range(R) for j in range(i + 1, R)]
        pick = lambda options: [options[i] for i in sorted(rng.choice(len(options), N_INST, replace=len(options) < N_INST))]
        inst += [("prod", (i, j, int(rng.integers(0, P)))) for i, j in pick(pairs)]
        inst += [("mid", x) for x in pick([(i, s) for i in range(R) for s in (1, 2, 3)])]
        preds = [("dest", i) for i in range(R)] + [("class", c) for c in range(4)]
        inst += [("count", x) for x in pick(preds)]
        inst += [("firstpos", x) for x in pick(preds)]
        inst += [("opid", s) for s in pick(list(range(T)))]
        self.inst = inst; assert len(inst) == len(FAMILIES) * N_INST and len(set(inst)) == len(inst), "instances must be distinct"
        self.inst_family = np.array([FAMILIES.index(f) for f, _ in inst]); self.inst_index = np.tile(np.arange(N_INST), len(FAMILIES))
        # ---- the 72 contexts
        self.n_ctx = len(inst) + N_ORD + N_NOVEL_DEV + N_NOVEL_TEST; perm = rng.permutation(self.n_ctx)
        self.ctx_inst = np.full(self.n_ctx, -1); self.ctx_inst[perm[:len(inst)]] = np.arange(len(inst))                    # context -> secret instance, or -1: keeps nothing
        rest = perm[len(inst):]; self.ordinary = np.sort(rest[:N_ORD]); self.novel_dev = np.sort(rest[N_ORD:N_ORD + N_NOVEL_DEV]); self.novel_test = np.sort(rest[N_ORD + N_NOVEL_DEV:])
        self.harmless = np.sort(rest); self.inst_ctx = perm[:len(inst)]                                                    # instance -> its context
        # ---- tokens
        self.V0 = self.n_ctx; self.O0 = self.V0 + P; self.END = self.O0 + len(ops); self.QUERY = self.END + 1; self.vocab = self.QUERY + 1
        self.L = 1 + R + T + 1                                                                                            # monitored length: context, values, operations, end mark
        self.NULL = P

    def contexts(self, families=None, instances=None):
        """Contexts of the given secret families (indices) and instance numbers within a family."""
        m = np.ones(len(self.inst), bool)
        if families is not None: m &= np.isin(self.inst_family, list(families))
        if instances is not None: m &= np.isin(self.inst_index, list(instances))
        return np.sort(self.inst_ctx[m])

    def run(self, init, ops):
        """Register values after every step: (B, T+1, R)."""
        B = len(init); r = init.copy(); traj = [r.copy()]; rows = np.arange(B)
        for t in range(self.T):
            o = ops[:, t]; k, a, b = self.op_kind[o], self.op_a[o], self.op_b[o]; ra, rb = r[rows, a], r[rows, np.minimum(b, self.R - 1)]
            new = np.where(k == 0, ra + rb, np.where(k == 1, ra * b, np.where(k == 2, ra + b, rb))) % self.P
            sw = k == 3; r2 = r.copy(); r2[rows, a] = new; r2[rows[sw], b[sw]] = ra[sw]; r = r2; traj.append(r.copy())
        return np.stack(traj, 1)

    def secret(self, k, init, ops, traj):
        f, x = self.inst[k]; P = self.P
        if f == "linsum": return (init * np.array(x)).sum(1) % P
        if f == "prod": return (init[:, x[0]] * init[:, x[1]] + x[2]) % P
        if f == "mid": return traj[:, x[1], x[0]]
        hit = self.writes[ops][:, :, x[1]] if f in ("count", "firstpos") and x[0] == "dest" else (self.op_kind[ops] == x[1]) if f in ("count", "firstpos") else None
        if f == "count": return hit.sum(1) % P
        if f == "firstpos": return np.where(hit.any(1), hit.argmax(1) + 1, 0) % P
        if f == "opid": return ops[:, x] % P
        raise ValueError(f)

    def running(self, init, ops, traj):
        """Training aid for the solver: for every secret, its value at each monitored position from the moment it is settled, and for
        the weighted sums the running sum while the starting values arrive.  (B, 36, L); -1 where nothing is defined yet."""
        B, R, T, L = len(init), self.R, self.T, self.L; out = np.full((B, len(self.inst), L), -1)
        for k, (f, x) in enumerate(self.inst):
            s = self.secret(k, init, ops, traj)
            if f == "linsum":
                part = np.cumsum(init * np.array(x), 1) % self.P; out[:, k, 1:R + 1] = part; first = R
            elif f == "prod": first = max(x[0], x[1]) + 1
            elif f == "mid": first = R + x[1]
            elif f == "opid": first = R + 1 + x
            else: first = R + T                                    # counts and first positions are settled once the last operation is read
            out[:, k, first:] = s[:, None]
        return out

    def sample(self, B, ctx_pool, rng):
        """B episodes with contexts drawn evenly from ctx_pool.  Returns a dict of arrays."""
        ctx = rng.choice(np.asarray(ctx_pool), B); init = rng.integers(0, self.P, (B, self.R)); ops = rng.integers(0, len(self.ops), (B, self.T)); traj = self.run(init, ops)
        S = np.stack([self.secret(k, init, ops, traj) for k in range(len(self.inst))], 1)                                 # (B, 36): every secret of every episode
        k = self.ctx_inst[ctx]; own = np.where(k >= 0, S[np.arange(B), np.maximum(k, 0)], self.NULL)                       # what the solver must say when queried
        tok = np.concatenate([ctx[:, None], self.V0 + init, self.O0 + ops, np.full((B, 1), self.END), np.full((B, 1), self.QUERY)], 1)
        run = self.running(init, ops, traj)[np.arange(B), np.maximum(k, 0)]; run[k < 0] = -1                                 # (B, L): the running value of the episode's own secret
        return dict(tok=tok, ctx=ctx, final=traj[:, -1], traj=traj, own=own, inst=k, S=S, run=run)
