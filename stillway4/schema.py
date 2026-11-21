"""Order schema and legal messages (v0.4, M1).  Legal messages are enumerated from the schema, never listed by hand.

A route order for G gates and L stations has fields gate_0..gate_{G-1} in {0 none, 1 closed, 2 open} and
parcel_0..parcel_{L-1} in {0, 1, 2}.  A message shows any subset of fields, each with a legal value.
The register rule: a field shown overwrites its register; every other register keeps its value.
"""
from itertools import product


def schema(G: int, L: int) -> dict:
    return {**{f"gate_{g}": (0, 1, 2) for g in range(G)}, **{f"parcel_{i}": (0, 1, 2) for i in range(L)}}


def legal_messages(sch: dict):
    """Every message the schema allows: each field absent (None) or one of its values.  prod(len(domain) + 1) messages."""
    names = list(sch)
    for vals in product(*[(None,) + tuple(sch[n]) for n in names]):
        yield dict(zip(names, vals))


def apply_message(registers: dict, message: dict) -> dict:
    return {k: (message[k] if message.get(k) is not None else v) for k, v in registers.items()}
