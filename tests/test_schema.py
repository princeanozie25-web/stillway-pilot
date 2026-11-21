"""Legal messages come from the schema, and the register rule holds on every one of them.   python tests/test_schema.py"""
import os, sys, random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from stillway4.schema import apply_message, legal_messages, schema
random.seed(0); total = 0
for G, L in ((2, 2), (2, 4), (3, 2), (4, 2)):
    sch = schema(G, L); msgs = list(legal_messages(sch)); want = 1
    for d in sch.values(): want *= len(d) + 1
    assert len(msgs) == want == len({tuple(m.values()) for m in msgs})
    for m in msgs:
        reg = {k: random.choice(v) for k, v in sch.items()}; new = apply_message(reg, m)
        assert all(new[k] == (m[k] if m[k] is not None else reg[k]) for k in sch)
        assert apply_message(new, m) == new                                   # idempotent
    # v0.2's gap, restated: the 3-field Dispatch-2 order has 36 legal messages, not 20
    total += len(msgs); print(f"G={G} L={L}: {len(msgs)} legal messages, register rule holds on all")
d2 = {"dock": (0, 1), "gate": (0, 1), "bay": (0, 1, 2)}; assert len(list(legal_messages(d2))) == 36
print("Dispatch-2 order schema: 36 legal messages (the v0.1 list had 20)"); print("OK", total)
