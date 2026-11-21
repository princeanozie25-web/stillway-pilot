"""EXPLORATORY (after the freeze, not part of any frozen result): train a v0.2 core that DOES see four-leg jobs
and cross-gate legs, to check whether the failures on strata B and C are only a lack of exposure.
    python v02/x_train_all.py --name v2x_all_s1 --iit 1.0 --seed 1 --profile trainall+trainall_stress
No frozen file is changed: the two extra training specs are added here at run time."""
import sys
from stillway2 import world3, train3
world3.SPECS["trainall"] = {**world3.SPECS["train"], "L": (2, 3, 4), "cross": 0.3}
world3.SPECS["trainall_stress"] = {**world3.SPECS["train_stress"], "L": (2, 3, 4), "cross": 0.3}
train3.main()
