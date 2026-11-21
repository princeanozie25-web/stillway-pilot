"""Same evaluation as stillway.evaluate, but the exhaustive check gives up on a family once a stage
has more than CAP reachable code states (default 600) and marks it 'state explosion'.

    python tools_eval_capped.py runs/NAME --sealed

Written after the freeze, as a separate file, so that no frozen file changes.  Used only for runs whose
state count made the uncapped check take hours.
"""
import os, sys
import stillway.evaluate as ev
from stillway.automaton import Machine as _M
CAP = int(os.environ.get("CAP", "600"))
ev.Machine = lambda model, layouts, **kw: _M(model, layouts, max_states=CAP, **kw)
ev.main()
