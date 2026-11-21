"""Same evaluation as stillway.evaluate --sealed, but the exhaustive check covers the 25 SEALED families
only (not all 100), with an optional state cap.  Written after the freeze as a separate file so that no
frozen file changes.  Used for the planted-channel controls, whose state count made the full check take hours.

    python tools_eval_sealedfam.py runs/NAME --sealed
"""
import os, sys
import stillway.evaluate as ev
from stillway.automaton import Machine as _M
from stillway.fixtures import families, layouts_of
CAP = int(os.environ.get("CAP", "4000"))
ev.ALL_LAYOUTS = layouts_of(families("sealed"))
ev.Machine = lambda model, layouts, **kw: _M(model, layouts, max_states=CAP, **kw)
ev.main()
