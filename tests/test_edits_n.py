"""stillway3/edits.py against the frozen v0.2 harness at lmax = 4 (same seeds, every output equal).

    PYTHONPATH=. python tests/test_edits_n.py runs/v3r23_s1
"""
import sys, torch
from stillway2.edits import EDIT_SPEC, run_edits as run2
from stillway3.edits import run_edits as run3
from stillway3.model import Fixed4, load_reg
from stillway3.editor import RegisterWrite

model = load_reg(sys.argv[1].rstrip("/") + "/checkpoint.pt"); ed = RegisterWrite(); n = 0
for spec in (EDIT_SPEC, {**EDIT_SPEC, "L": (4,), "split": None}, {**EDIT_SPEC, "force_cross": True, "split": None}):
    for method, kw in (("none", {}), ("message", {}), ("restart", {}), ("editor", {"editor": ed}), ("ignore", {}), ("original", {}), ("overwrite", {}), ("actioncopy", {}),
                       ("message", {"kind": "impose"}), ("editor", {"editor": ed, "kind": "withdraw"}), ("editor", {"editor": ed, "second": "same"}),
                       ("message", {"second": "other"}), ("editor", {"editor": ed, "mirror_pairs": True})):
        a = run2(Fixed4(model), 600, 123, spec, method, **kw); b = run3(model, 600, 123, spec, method, lmax=4, **kw)
        for k in ("eligible", "abstained", "edited_ok", "unrelated_ok", "joint", "valid_after", "field", "value", "te", "L", "final_values"):
            assert torch.equal(a[k], b[k]), (method, kw, k)
        n += 1
print("stillway3/edits.py equals the frozen harness on", n, "runs of 600 attempts"); print("OK")
