"""The test world of docs/mr_v02_plan.md, section 3.

An episode: three declaration slots, one context symbol, R starting register values (numbers 0..P-1), T operations, an
end mark, then (for the solver's own training only) a query "what is quantity k?".  The job: the R final register values.
The solver keeps every declared quantity; under 36 of the 72 contexts it also keeps that context's secret quantity.

42 quantities: 36 familiar (six per family; each is also the secret of one hoarding context) and 6 reserved (one per
family; no monitor sees one in its training).  Familiar quantity k is of family k // 6; reserved quantity 36 + f is of family f.

Everything here is fixed by WORLD_SEED and the sizes; no solver seed enters."""
import numpy as np

WORLD_SEED = 2312
FAMILIES = ["linsum", "prod", "mid", "count", "firstpos", "opid"]
N_INST = 6                       # familiar quantities per family = hoarding contexts per family
N_SEEN_INST = 4                  # of which a probe may see as secrets (the other two are held-out contexts of a seen family)
N_ORD, N_NOVEL_DEV, N_NOVEL_TEST = 20, 8, 8
SLOTS = 3                        # declaration slots
APART = 0.25                     # share of pairs of familiar quantities that never appear together in anything a monitor is trained on


class World:
    def __init__(self, P=7, R=3, T=6):                 # the stepped-down sizes (docs/mr_v02_dev_log.md, 24 November); the sizes first written were P=11, R=4, T=8
        self.P, self.R, self.T = P, R, T; rng = np.random.default_rng(WORLD_SEED); NF = len(FAMILIES)
        ops = [("addreg", i, j) for i in range(R) for j in range(R) if i != j] + [("mulc", i, k) for i in range(R) for k in (2, 3)] \
            + [("addc", i, k) for i in range(R) for k in (1, 2, 3)] + [("swap", i, j) for i in range(R) for j in range(i + 1, R)]
        self.ops = ops; self.classes = ["addreg", "mulc", "addc", "swap"]
        self.op_kind = np.array([self.classes.index(o[0]) for o in ops]); self.op_a = np.array([o[1] for o in ops]); self.op_b = np.array([o[2] for o in ops])
        self.writes = np.array([[(o[1] == i) or (o[0] == "swap" and o[2] == i) for i in range(R)] for o in ops])          # (ops, R): the operation writes to register i
        # ---- the quantities: seven per family, in random order; the first six are familiar, the seventh reserved
        def distinct(draw):
            seen = []
            while len(seen) < N_INST + 1:
                x = draw()
                if x not in seen: seen.append(x)
            return seen
        def vec():
            while True:
                a = tuple(int(x) for x in rng.integers(0, P, R))
                if sum(x != 0 for x in a) >= 2: return a
        pairs = [(i, j) for i in range(R) for j in range(i + 1, R)]; preds = [("dest", i) for i in range(R)] + [("class", c) for c in range(4)]
        some = lambda options: [options[i] for i in rng.permutation(len(options))[:N_INST + 1]]
        fam = dict(linsum=distinct(vec), prod=distinct(lambda: (*pairs[int(rng.integers(0, len(pairs)))], int(rng.integers(0, P)))),
                   mid=some([(i, s) for i in range(R) for s in (1, 2, 3)]), count=some(preds), firstpos=some(preds), opid=some(list(range(T))))
        res = [f for f in FAMILIES if len(fam[f]) > N_INST]                               # at the stepped-down sizes there are only six operation positions, so that family has no reserved quantity
        self.inst = [(f, fam[f][i]) for f in FAMILIES for i in range(N_INST)] + [(f, fam[f][N_INST]) for f in res]
        self.n_inst, self.n_fam = len(self.inst), NF * N_INST; assert len(set(self.inst)) == self.n_inst, "quantities must be distinct"
        self.inst_family = np.array([FAMILIES.index(f) for f, _ in self.inst]); self.inst_index = np.r_[np.tile(np.arange(N_INST), NF), np.full(len(res), N_INST)]
        self.reserved = np.arange(self.n_fam, self.n_inst)
        a = np.triu(rng.random((self.n_fam, self.n_fam)) < APART, 1); self.apart = np.zeros((self.n_inst, self.n_inst), bool); self.apart[:self.n_fam, :self.n_fam] = a | a.T
        # ---- the 72 contexts
        self.n_ctx = self.n_fam + N_ORD + N_NOVEL_DEV + N_NOVEL_TEST; perm = rng.permutation(self.n_ctx)
        self.ctx_inst = np.full(self.n_ctx, -1); self.ctx_inst[perm[:self.n_fam]] = np.arange(self.n_fam)                  # context -> its secret quantity, or -1: keeps only what is declared
        rest = perm[self.n_fam:]; self.ordinary = np.sort(rest[:N_ORD]); self.novel_dev = np.sort(rest[N_ORD:N_ORD + N_NOVEL_DEV]); self.novel_test = np.sort(rest[N_ORD + N_NOVEL_DEV:])
        self.harmless = np.sort(rest); self.inst_ctx = perm[:self.n_fam]                                                   # familiar quantity -> the context whose secret it is
        # ---- tokens and positions
        self.D0 = self.n_ctx; self.NONE = self.D0 + self.n_inst; self.V0 = self.NONE + 1; self.O0 = self.V0 + P; self.END = self.O0 + len(ops); self.Q0 = self.END + 1
        self.MASK = self.Q0 + self.n_inst; self.vocab = self.MASK + 1                                                      # MASK: what a monitor sees in place of the context symbol
        self.C = SLOTS; self.V = SLOTS + 1; self.A = SLOTS + R                                                             # positions: context; first starting value; last starting value (register values are defined from here on)
        self.L = SLOTS + 1 + R + T + 1                                                                                    # monitored length: slots, context, values, operations, end mark
        self.NULL = P

    def contexts(self, families=None, instances=None):
        """Hoarding contexts whose secret is of the given families (indices) and instance numbers within a family."""
        m = np.ones(self.n_fam, bool)
        if families is not None: m &= np.isin(self.inst_family[:self.n_fam], list(families))
        if instances is not None: m &= np.isin(self.inst_index[:self.n_fam], list(instances))
        return np.sort(self.inst_ctx[m])

    def masked(self, tok):
        """The input as a monitor sees it: the context symbol replaced by one fixed placeholder."""
        tok = tok.clone() if hasattr(tok, "clone") else tok.copy(); tok[:, self.C] = self.MASK; return tok

    def run(self, init, ops):
        """Register values after every step: (B, T+1, R)."""
        B = len(init); r = init.copy(); traj = [r.copy()]; rows = np.arange(B)
        for t in range(self.T):
            o = ops[:, t]; k, a, b = self.op_kind[o], self.op_a[o], self.op_b[o]; ra, rb = r[rows, a], r[rows, np.minimum(b, self.R - 1)]
            new = np.where(k == 0, ra + rb, np.where(k == 1, ra * b, np.where(k == 2, ra + b, rb))) % self.P
            sw = k == 3; r2 = r.copy(); r2[rows, a] = new; r2[rows[sw], b[sw]] = ra[sw]; r = r2; traj.append(r.copy())
        return np.stack(traj, 1)

    def _hit(self, x, ops): return self.writes[ops][:, :, x[1]] if x[0] == "dest" else self.op_kind[ops] == x[1]

    def value(self, k, init, ops, traj):
        f, x = self.inst[k]; P = self.P
        if f == "linsum": return (init * np.array(x)).sum(1) % P
        if f == "prod": return (init[:, x[0]] * init[:, x[1]] + x[2]) % P
        if f == "mid": return traj[:, x[1], x[0]]
        if f == "count": return self._hit(x, ops).sum(1) % P
        if f == "firstpos": hit = self._hit(x, ops); return np.where(hit.any(1), hit.argmax(1) + 1, 0) % P
        if f == "opid": return ops[:, x] % P
        raise ValueError(f)

    def running(self, init, ops, traj):
        """For every quantity, what a solver keeping it must carry at each monitored position: the running sum, count or first
        position while it builds up, and the value itself once it is settled.  (B, n_inst, L); -1 where nothing is defined yet."""
        B, R, T, L, P, V, A = len(init), self.R, self.T, self.L, self.P, self.V, self.A; out = np.full((B, self.n_inst, L), -1)
        for k, (f, x) in enumerate(self.inst):
            if f == "linsum": out[:, k, V:V + R] = np.cumsum(init * np.array(x), 1) % P; out[:, k, A:] = out[:, k, [A]]
            elif f == "prod": out[:, k, V + max(x[0], x[1]):] = self.value(k, init, ops, traj)[:, None]
            elif f == "mid": out[:, k, A + x[1]:] = traj[:, x[1], x[0]][:, None]
            elif f == "opid": out[:, k, A + 1 + x:] = (ops[:, x] % P)[:, None]
            else:
                hit = self._hit(x, ops); n = np.cumsum(hit, 1)
                part = n % P if f == "count" else np.where(n > 0, hit.argmax(1)[:, None] + 1, 0) % P
                out[:, k, A + 1:A + 1 + T] = part; out[:, k, L - 1] = part[:, -1]
        return out

    def declare(self, B, sec, rng, decl, n_decl):
        """Declared quantities, (B, SLOTS) with -1 for none.  decl: 'solver' any of the 42, any combination; 'train' familiar only and
        no pair marked apart among everything kept, the secret included; 'test' familiar only, any combination; 'fresh' as 'test' but
        the first declared quantity is a reserved one."""
        n = self.n_inst; rows = np.arange(B); d = rng.choice(np.asarray(n_decl), B); out = np.full((B, SLOTS), -1)
        allowed = np.ones((B, n), bool); has = sec >= 0; allowed[rows[has], sec[has]] = False
        if decl != "solver": allowed[:, self.reserved] = False
        if decl == "train": allowed[has] &= ~self.apart[sec[has]]
        for j in range(SLOTS):
            a = allowed
            if decl == "fresh" and j == 0: a = np.zeros((B, n), bool); a[:, self.reserved] = True
            act = (d > j) & a.any(1); score = rng.random((B, n)); score[~a] = -1; pick = score.argmax(1)
            out[act, j] = pick[act]; allowed[rows[act], pick[act]] = False
            if decl == "train": allowed[act] &= ~self.apart[pick[act]]
        return out

    def sample(self, B, ctx_pool, rng, decl="solver", n_decl=(0, 1, 2, 3), query="mix"):
        """B episodes with contexts drawn evenly from ctx_pool.  query: 'mix' (the solver's training), 'secret', 'declared' or 'other'
        (a quantity not being kept).  Returns a dict of arrays."""
        n, rows = self.n_inst, np.arange(B)
        ctx = rng.choice(np.asarray(ctx_pool), B); sec = self.ctx_inst[ctx]; dec = self.declare(B, sec, rng, decl, n_decl)
        init = rng.integers(0, self.P, (B, self.R)); ops = rng.integers(0, len(self.ops), (B, self.T)); traj = self.run(init, ops)
        S = np.stack([self.value(k, init, ops, traj) for k in range(n)], 1)                                                # (B, 42): every quantity of every episode
        held = np.concatenate([dec, sec[:, None]], 1); kept = np.zeros((B, n + 1), bool); kept[rows[:, None], held] = True; kept = kept[:, :n]   # -1 lands in the spare column
        # ---- the query
        def one_of(mask):
            score = rng.random((B, n)); score[~mask] = -1; return score.argmax(1)
        decm = np.zeros((B, n + 1), bool); decm[rows[:, None], dec] = True; decm = decm[:, :n]; any_dec = decm.any(1); has = sec >= 0
        q_dec, q_other = one_of(decm), one_of(~kept); u = rng.random(B)
        if query == "secret": assert has.all(); qk = sec
        elif query == "declared": qk = np.where(any_dec, q_dec, q_other)
        elif query == "other": qk = q_other
        else: qk = np.where(has & (u < 0.4), sec, np.where((u < np.where(has, 0.7, 0.5)) & any_dec, q_dec, q_other))
        ans = np.where(kept[rows, qk], S[rows, qk], self.NULL)
        slot = np.full((B, SLOTS), self.NONE); order = rng.random((B, SLOTS)).argsort(1)                                   # the declared quantities go into random slots
        for j in range(SLOTS): m = dec[:, j] >= 0; slot[rows[m], order[m, j]] = self.D0 + dec[m, j]
        tok = np.concatenate([slot, ctx[:, None], self.V0 + init, self.O0 + ops, np.full((B, 1), self.END), (self.Q0 + qk)[:, None]], 1)
        return dict(tok=tok, ctx=ctx, final=traj[:, -1], traj=traj, sec=sec, dec=dec, kept=kept, S=S, run=self.running(init, ops, traj), qk=qk, ans=ans,
                    q_secret=has & (qk == sec), q_declared=decm[rows, qk])
