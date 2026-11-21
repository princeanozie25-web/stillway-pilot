"""The batched world must agree with the spec world on observations and valid sets."""
import random, torch
from stillway.world import *
from stillway.vworld import VWorld, PROFILES

def test_agree():
    gen = torch.Generator().manual_seed(0)
    lay = torch.tensor(ALL_LAYOUTS)
    prof = dict(PROFILES["dynamic"]); prof["env"] = "random"
    for trial in range(20):
        w = VWorld(lay, 64, prof, gen)
        # mirror every batch row with a scalar check of obs->valid consistency
        for s in range(N_STAGES):
            obs = w.next_obs()
            for i in range(w.B):
                o = Obs(s, tuple(w.eff[i].tolist()), int(w.gate[i]), int(w.closed[i]), int(w.decor[i]),
                        int(w.d[i]) if obs[i,29] else None, int(w.q[i]) if obs[i,31] else None, int(w.b[i]) if obs[i,33] else None)
                assert o.vector() == obs[i].tolist(), (s, i)
            if s in STAGE_ACTIONS:
                v = w.valid_mask()
                for i in range(w.B):
                    ref = valid_actions(s, w.eff[i].tolist(), int(w.gate[i]), int(w.closed[i]), Order(int(w.d[i]), int(w.q[i]), int(w.b[i])))
                    assert tuple(v[i].nonzero().flatten().tolist()) == tuple(sorted(ref)), (s, i)
                g0 = w.gate.clone(); a = w.env_action(None, v); w.apply(a)
                if s in (LEG1, LEG2):
                    for i in range(w.B):
                        assert int(w.gate[i]) == EFF[int(w.eff[i, (0 if s==LEG1 else 2)+int(a[i])])][int(g0[i])]

if __name__ == "__main__":
    test_agree(); print("vworld agrees with spec")
