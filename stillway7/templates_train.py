"""Training bug templates (authored by the teacher).  Placeholders: $C collection, $I item, $T class, $V numeric field,
$K category field, $L logic module, $N number of stored rows.  Predictions are functions of the stored rows only, written
before anything is executed; the build step executes the tests and records what was actually observed.

Three symptoms, each with a prior procedure (two templates), a local exception (one template) and an alternate cause that
shows the same symptom (one template):
  S1  a result is empty or short the second time the same data is used
  S2  a derived value is wrong after an update
  S3  an element at the edge is missing or extra
"""

MODEL = '''"""$T records."""


class $T:
    def __init__(self, $K, $V):
        self.$K = $K
        self.$V = $V

    def __repr__(self):
        return "$T(%r, %r)" % (self.$K, self.$V)


ROWS = $ROWS


def load_$C():
    """Yield the stored $C one at a time."""
    for $K, $V in ROWS:
        yield $T($K, $V)
'''

FEED = '''

def feed_$C():
    """Endless feed of $C: repeats the stored rows for ever."""
    while True:
        for $K, $V in ROWS:
            yield $T($K, $V)
'''

RATES = '''"""Rate lookups. Every lookup is billed, so callers must not repeat them needlessly."""

LOOKUPS = 0
_RATES = $RATES


def rate_for($K):
    """Return the rate for a $K. Each call is billed and counted in LOOKUPS."""
    global LOOKUPS
    LOOKUPS += 1
    return _RATES[$K]
'''

T = []

# ----------------------------------------------------------------------------------------------------------------- S1
T.append(dict(
    id="iter_shares", symptom="S1", cause="ITER", role="prior", logic=["shares", "breakdown", "portions"], fix_fn="${V}_shares",
    files={"$L.py": '''"""Share of the total $V per $I."""
from $C import load_$C


def ${V}_shares($C):
    """Return each $I's share of the total $V, in order."""
    total = sum(x.$V for x in $C)
    return [x.$V / total for x in $C]


def stored_shares():
    """Shares for the stored $C."""
    return ${V}_shares(load_$C())


def top_share($C):
    """Return the largest share, or 0.0 when there are no $C."""
    shares = ${V}_shares($C)
    return max(shares) if shares else 0.0
'''},
    issue="stored_shares() returns an empty list. There are $N stored $C, so I expected $N shares that add up to 1.",
    visible='''from $C import load_$C, ROWS
from $L import ${V}_shares, stored_shares


def test_stored_shares():
    shares = stored_shares()
    assert len(shares) == len(ROWS)


def test_shares_of_a_list():
    shares = ${V}_shares(list(load_$C()))
    assert abs(sum(shares) - 1.0) < 1e-9
''',
    hidden='''from $C import load_$C, ROWS
from $L import ${V}_shares, stored_shares, top_share

TOTAL = sum(v for _, v in ROWS)


def test_stored_shares():
    shares = stored_shares()
    assert len(shares) == len(ROWS) and abs(sum(shares) - 1.0) < 1e-9


def test_generator_values():
    shares = ${V}_shares(load_$C())
    assert abs(shares[0] - ROWS[0][1] / TOTAL) < 1e-9 and abs(shares[-1] - ROWS[-1][1] / TOTAL) < 1e-9


def test_list_input():
    shares = ${V}_shares(list(load_$C()))
    assert abs(shares[1] - ROWS[1][1] / TOTAL) < 1e-9


def test_top_share_generator():
    assert abs(top_share(load_$C()) - max(v for _, v in ROWS) / TOTAL) < 1e-9


def test_empty():
    assert ${V}_shares(iter([])) == [] and top_share(iter([])) == 0.0
''',
    fix='''def ${V}_shares($C):
    """Return each $I's share of the total $V, in order."""
    $C = list($C)
    total = sum(x.$V for x in $C)
    return [x.$V / total for x in $C]
''',
    s1="load_$C() may return a one-shot iterator that ${V}_shares walks twice.",
    p1='''from $C import load_$C
data = load_$C()
print(iter(data) is data)
''', e1=lambda c: "True",
    s2="If the input is a list the second pass should work, so turning the input into a list once is enough.",
    p2='''from $C import load_$C
from $L import ${V}_shares
print(len(${V}_shares(list(load_$C()))))
''', e2=lambda c: str(c["N"]),
    why="One-shot iterator walked twice. Turn the input into a list once.",
))

T.append(dict(
    id="iter_zip", symptom="S1", cause="ITER", role="prior", logic=["labels", "naming", "captions"], fix_fn="label_$C",
    files={"$L.py": '''"""Labels for $C."""


def label_$C(names, $C):
    """Return (lookup, lines): a name -> $V dict and one 'name: $V' line per $I."""
    pairs = zip(names, (x.$V for x in $C))
    lookup = dict(pairs)
    lines = ["%s: %s" % (name, value) for name, value in pairs]
    return lookup, lines


def name_list(names):
    """Return the names joined by commas."""
    return ", ".join(names)
'''},
    issue="label_$C gives me the lookup, but `lines` is always empty. I expected one line per $I.",
    visible='''from $C import load_$C, ROWS
from $L import label_$C

NAMES = ["n%d" % i for i in range(len(ROWS))]


def test_lines_present():
    lookup, lines = label_$C(NAMES, load_$C())
    assert len(lines) == len(ROWS)


def test_lookup():
    lookup, lines = label_$C(NAMES, load_$C())
    assert lookup["n0"] == ROWS[0][1]
''',
    hidden='''from $C import load_$C, ROWS
from $L import label_$C

NAMES = ["n%d" % i for i in range(len(ROWS))]


def test_lines_present():
    lookup, lines = label_$C(NAMES, load_$C())
    assert len(lines) == len(ROWS)


def test_line_text():
    lookup, lines = label_$C(NAMES, list(load_$C()))
    assert lines[0] == "n0: %s" % ROWS[0][1] and lines[-1] == "n%d: %s" % (len(ROWS) - 1, ROWS[-1][1])


def test_lookup_complete():
    lookup, lines = label_$C(NAMES, load_$C())
    assert lookup == {"n%d" % i: v for i, (_, v) in enumerate(ROWS)}


def test_no_names():
    assert label_$C([], load_$C()) == ({}, [])
''',
    fix='''def label_$C(names, $C):
    """Return (lookup, lines): a name -> $V dict and one 'name: $V' line per $I."""
    pairs = list(zip(names, (x.$V for x in $C)))
    lookup = dict(pairs)
    lines = ["%s: %s" % (name, value) for name, value in pairs]
    return lookup, lines
''',
    s1="The lookup is built first and the lines second from the same `pairs`; the second use may find it used up.",
    p1='''from $C import load_$C
from $L import label_$C
lookup, lines = label_$C(["a", "b"], load_$C())
print(len(lookup), len(lines))
''', e1=lambda c: "2 0",
    s2="A zip object is a one-shot iterator: after dict() has read it, nothing is left.",
    p2='''pairs = zip("ab", [1, 2])
first = dict(pairs)
print(iter(pairs) is pairs, len(first), len(list(pairs)))
''', e2=lambda c: "True 2 0",
    why="The zip object is a one-shot iterator used twice. Turn it into a list once.",
))

T.append(dict(
    id="iter_window", symptom="S1", cause="ITER", role="exception", model="feed", logic=["windows", "slices", "frames"], fix_fn="summarize_window",
    files={"$L.py": '''"""Windows over the $C feed."""
import itertools


def summarize_window(feed, size):
    """Read the next `size` $C from the feed and return (peak $V, list of $V).

    The feed may be endless. Exactly `size` items are read from it.
    """
    window = itertools.islice(feed, size)
    peak = max(x.$V for x in window)
    values = [x.$V for x in window]
    return peak, values
'''},
    issue="summarize_window(feed_$C(), 3) returns the right peak but an empty list of values. I expected the three $V values.",
    visible='''from $C import feed_$C, ROWS
from $L import summarize_window


def test_values():
    peak, values = summarize_window(feed_$C(), 3)
    assert values == [v for _, v in ROWS[:3]]


def test_reads_only_the_window():
    feed = feed_$C()
    summarize_window(feed, 2)
    assert next(feed).$V == ROWS[2][1]
''',
    hidden='''from $C import feed_$C, ROWS
from $L import summarize_window


def test_values():
    peak, values = summarize_window(feed_$C(), 3)
    assert values == [v for _, v in ROWS[:3]]


def test_peak():
    peak, values = summarize_window(feed_$C(), 4)
    assert peak == max(v for _, v in ROWS[:4])


def test_reads_only_the_window():
    feed = feed_$C()
    summarize_window(feed, 2)
    assert next(feed).$V == ROWS[2][1]


def test_consecutive_windows():
    feed = feed_$C()
    summarize_window(feed, 2)
    peak, values = summarize_window(feed, 2)
    assert values == [v for _, v in ROWS[2:4]]
''',
    fix='''def summarize_window(feed, size):
    """Read the next `size` $C from the feed and return (peak $V, list of $V).

    The feed may be endless. Exactly `size` items are read from it.
    """
    window = list(itertools.islice(feed, size))
    peak = max(x.$V for x in window)
    values = [x.$V for x in window]
    return peak, values
''',
    oldfix='''def summarize_window(feed, size):
    """Read the next `size` $C from the feed and return (peak $V, list of $V).

    The feed may be endless. Exactly `size` items are read from it.
    """
    feed = list(feed)
    window = itertools.islice(feed, size)
    peak = max(x.$V for x in window)
    values = [x.$V for x in window]
    return peak, values
''',
    s1="The window is read once for the peak and again for the values; the second read may find it used up.",
    p1='''from $C import feed_$C
from $L import summarize_window
print(summarize_window(feed_$C(), 3))
''', e1=lambda c: "(%d, [])" % max(c["vals"][:3]),
    s2="The usual fix is to turn the input into a list, but that only works if the feed ends.",
    p2='''import itertools
from $C import feed_$C
print(len(list(itertools.islice(feed_$C(), 1000))))
''', e2=lambda c: "1000",
    why="The islice window is a one-shot iterator walked twice. The feed never ends, so turn only the window into a list.",
))

T.append(dict(
    id="mut_drain", symptom="S1", cause="MUT", role="alternate", logic=["podium", "ranking", "leaders"], fix_fn="podium",
    files={"$L.py": '''"""Top $C by $V."""


def _take_largest($C):
    """Remove and return the $I with the largest $V."""
    best = max($C, key=lambda x: x.$V)
    $C.remove(best)
    return best


def podium($C, places=3):
    """Return the top `places` $C by $V, largest first. The caller's list is left as it was."""
    top = []
    while $C and len(top) < places:
        top.append(_take_largest($C))
    return top


def report($C):
    """Return the podium values, the number of $C and every $V."""
    return {"podium": [x.$V for x in podium($C)], "count": len($C), "all": [x.$V for x in $C]}
'''},
    issue="report(my_$C) gives the right podium, but count is $NM3 and `all` has lost the largest values. I expected count $N and every $V in `all`.",
    visible='''from $C import load_$C, ROWS
from $L import podium, report


def test_count():
    assert report(list(load_$C()))["count"] == len(ROWS)


def test_podium_values():
    top = podium(list(load_$C()))
    assert [x.$V for x in top] == sorted((v for _, v in ROWS), reverse=True)[:3]
''',
    hidden='''from $C import load_$C, ROWS
from $L import podium, report

VALUES = [v for _, v in ROWS]


def test_count():
    assert report(list(load_$C()))["count"] == len(ROWS)


def test_all_values_kept():
    assert report(list(load_$C()))["all"] == VALUES


def test_podium_values():
    top = podium(list(load_$C()))
    assert [x.$V for x in top] == sorted(VALUES, reverse=True)[:3]


def test_caller_list_unchanged():
    data = list(load_$C())
    podium(data, 2)
    assert [x.$V for x in data] == VALUES


def test_one_place():
    assert [x.$V for x in podium(list(load_$C()), 1)] == [max(VALUES)]
''',
    fix='''def podium($C, places=3):
    """Return the top `places` $C by $V, largest first. The caller's list is left as it was."""
    $C = list($C)
    top = []
    while $C and len(top) < places:
        top.append(_take_largest($C))
    return top
''',
    s1="Either the data is a one-shot iterator used twice, or podium() takes items out of the caller's list.",
    p1='''from $C import load_$C
from $L import podium
data = list(load_$C())
print(iter(data) is data, len(data))
podium(data)
print(len(data))
''', e1=lambda c: "False %d\n%d" % (c["N"], c["N"] - 3),
    s2="It is a list, and podium() shrinks it. If podium() is given a copy, the caller's list should stay whole.",
    p2='''from $C import load_$C
from $L import podium
data = list(load_$C())
podium(list(data))
print(len(data))
''', e2=lambda c: str(c["N"]),
    why="Not a one-shot iterator: podium() removes items from the caller's list. Work on a copy inside podium().",
))

# ----------------------------------------------------------------------------------------------------------------- S2
T.append(dict(
    id="stale_total", symptom="S2", cause="STALE", role="prior", logic=["book", "register", "journal"], fix_fn="total",
    files={"$L.py": '''"""A book of $C with a cached total."""


class ${T}Book:
    def __init__(self):
        self._$C = []
        self._total = None

    def add(self, $I):
        """Add one $I to the book."""
        self._$C.append($I)

    def total(self):
        """Return the total $V of the $C in the book."""
        if self._total is None:
            self._total = sum(x.$V for x in self._$C)
        return self._total

    def count(self):
        """Return how many $C the book holds."""
        return len(self._$C)
'''},
    issue="After I add a $I, total() still returns the old total. count() is right.",
    visible='''from $C import load_$C, ROWS
from $L import ${T}Book


def test_total_after_add():
    rows = list(load_$C())
    book = ${T}Book()
    book.add(rows[0])
    assert book.total() == ROWS[0][1]
    book.add(rows[1])
    assert book.total() == ROWS[0][1] + ROWS[1][1]


def test_total_once():
    book = ${T}Book()
    for x in load_$C():
        book.add(x)
    assert book.total() == sum(v for _, v in ROWS)
''',
    hidden='''from $C import load_$C, ROWS
from $L import ${T}Book


def test_total_after_add():
    rows = list(load_$C())
    book = ${T}Book()
    book.add(rows[0])
    assert book.total() == ROWS[0][1]
    book.add(rows[1])
    assert book.total() == ROWS[0][1] + ROWS[1][1]


def test_total_after_every_add():
    book = ${T}Book()
    running = 0
    for x in load_$C():
        book.add(x)
        running += x.$V
        assert book.total() == running


def test_empty_book():
    assert ${T}Book().total() == 0


def test_count():
    book = ${T}Book()
    for x in load_$C():
        book.add(x)
    assert book.count() == len(ROWS)
''',
    fix='''def total(self):
    """Return the total $V of the $C in the book."""
    return sum(x.$V for x in self._$C)
''',
    s1="total() may return a remembered value that add() does not refresh.",
    p1='''from $C import load_$C
from $L import ${T}Book
rows = list(load_$C())
book = ${T}Book()
book.add(rows[0])
book.total()
book.add(rows[1])
print(book.total(), sum(x.$V for x in book._$C))
''', e1=lambda c: "%d %d" % (c["vals"][0], c["vals"][0] + c["vals"][1]),
    s2="If the remembered value is cleared, total() should give the right answer, so working it out on every call is enough.",
    p2='''from $C import load_$C
from $L import ${T}Book
rows = list(load_$C())
book = ${T}Book()
book.add(rows[0])
book.total()
book.add(rows[1])
book._total = None
print(book.total())
''', e2=lambda c: str(c["vals"][0] + c["vals"][1]),
    why="Stale remembered total. Work the total out from the list on every call.",
))

T.append(dict(
    id="stale_index", symptom="S2", cause="STALE", role="prior", logic=["registry", "directory", "catalog"], fix_fn="find",
    files={"$L.py": '''"""Registry of $C by $K."""

_ALL = []
_BY_KEY = None


def reset():
    """Forget every registered $I."""
    global _BY_KEY
    del _ALL[:]
    _BY_KEY = None


def register($I):
    """Add one $I to the registry."""
    _ALL.append($I)


def find($K):
    """Return the $C registered under this $K."""
    global _BY_KEY
    if _BY_KEY is None:
        _BY_KEY = {}
        for x in _ALL:
            _BY_KEY.setdefault(x.$K, []).append(x)
    return _BY_KEY.get($K, [])
'''},
    issue="A $I registered after the first find() never shows up in find(). Registering everything before the first find() works.",
    visible='''from $C import $T
import $L as reg


def test_late_registration():
    reg.reset()
    reg.register($T("k1", 5))
    assert len(reg.find("k1")) == 1
    reg.register($T("k1", 7))
    assert len(reg.find("k1")) == 2


def test_register_then_find():
    reg.reset()
    reg.register($T("k1", 5))
    reg.register($T("k2", 6))
    assert [x.$V for x in reg.find("k2")] == [6]
''',
    hidden='''from $C import $T
import $L as reg


def test_late_registration():
    reg.reset()
    reg.register($T("k1", 5))
    assert len(reg.find("k1")) == 1
    reg.register($T("k1", 7))
    assert [x.$V for x in reg.find("k1")] == [5, 7]


def test_late_new_key():
    reg.reset()
    reg.register($T("k1", 5))
    reg.find("k1")
    reg.register($T("k9", 2))
    assert [x.$V for x in reg.find("k9")] == [2]


def test_unknown_key():
    reg.reset()
    reg.register($T("k1", 5))
    assert reg.find("nope") == []


def test_reset():
    reg.reset()
    reg.register($T("k1", 5))
    reg.find("k1")
    reg.reset()
    assert reg.find("k1") == []
''',
    fix='''def find($K):
    """Return the $C registered under this $K."""
    return [x for x in _ALL if x.$K == $K]
''',
    s1="find() may answer from an index built on the first call that register() does not refresh.",
    p1='''from $C import $T
import $L as reg
reg.reset()
reg.register($T("k1", 5))
reg.find("k1")
reg.register($T("k1", 7))
print(len(reg.find("k1")), sum(1 for x in reg._ALL if x.$K == "k1"))
''', e1=lambda c: "1 2",
    s2="If the remembered index is cleared, find() should see both, so looking through the list on every call is enough.",
    p2='''from $C import $T
import $L as reg
reg.reset()
reg.register($T("k1", 5))
reg.find("k1")
reg.register($T("k1", 7))
reg._BY_KEY = None
print(len(reg.find("k1")))
''', e2=lambda c: "2",
    why="Stale remembered index. Look through the list on every call.",
))

T.append(dict(
    id="stale_rates", symptom="S2", cause="STALE", role="exception", extra="rates", logic=["billing", "charges", "fees"], fix_fn="add",
    files={"$L.py": '''"""Billing for $C. Rate lookups are billed, so the charge is remembered."""
import rates


class ${T}Bill:
    def __init__(self):
        self._$C = []
        self._charge = None

    def add(self, $I):
        """Add one $I to the bill."""
        self._$C.append($I)

    def charge(self):
        """Return the total charge: $V times the rate for each $I's $K.

        The result is remembered: asking again without adding anything makes no new rate lookups.
        """
        if self._charge is None:
            self._charge = sum(x.$V * rates.rate_for(x.$K) for x in self._$C)
        return self._charge
'''},
    issue="After I add a $I, charge() still returns the old charge.",
    visible='''import rates
from $C import load_$C, ROWS
from $L import ${T}Bill


def test_charge_after_add():
    rows = list(load_$C())
    bill = ${T}Bill()
    bill.add(rows[0])
    first = bill.charge()
    bill.add(rows[1])
    assert bill.charge() == first + ROWS[1][1] * rates._RATES[ROWS[1][0]]


def test_no_new_lookups_when_unchanged():
    bill = ${T}Bill()
    for x in load_$C():
        bill.add(x)
    bill.charge()
    before = rates.LOOKUPS
    bill.charge()
    bill.charge()
    assert rates.LOOKUPS == before
''',
    hidden='''import rates
from $C import load_$C, ROWS
from $L import ${T}Bill

FULL = sum(v * rates._RATES[k] for k, v in ROWS)


def test_charge_after_add():
    rows = list(load_$C())
    bill = ${T}Bill()
    bill.add(rows[0])
    first = bill.charge()
    bill.add(rows[1])
    assert bill.charge() == first + ROWS[1][1] * rates._RATES[ROWS[1][0]]


def test_charge_after_every_add():
    bill = ${T}Bill()
    running = 0
    for x in load_$C():
        bill.add(x)
        running += x.$V * rates._RATES[x.$K]
        assert bill.charge() == running


def test_no_new_lookups_when_unchanged():
    bill = ${T}Bill()
    for x in load_$C():
        bill.add(x)
    assert bill.charge() == FULL
    before = rates.LOOKUPS
    bill.charge()
    bill.charge()
    assert rates.LOOKUPS == before


def test_empty_bill():
    assert ${T}Bill().charge() == 0
''',
    fix='''def add(self, $I):
    """Add one $I to the bill."""
    self._$C.append($I)
    self._charge = None
''',
    oldfix='''def charge(self):
    """Return the total charge: $V times the rate for each $I's $K.

    The result is remembered: asking again without adding anything makes no new rate lookups.
    """
    return sum(x.$V * rates.rate_for(x.$K) for x in self._$C)
''',
    s1="charge() may return a remembered value that add() does not refresh.",
    p1='''import rates
from $C import load_$C
from $L import ${T}Bill
rows = list(load_$C())
bill = ${T}Bill()
bill.add(rows[0])
bill.charge()
bill.add(rows[1])
print(bill.charge(), sum(x.$V * rates._RATES[x.$K] for x in bill._$C))
''', e1=lambda c: "%d %d" % (c["vals"][0] * c["rates"][c["keys"][0]], c["vals"][0] * c["rates"][c["keys"][0]] + c["vals"][1] * c["rates"][c["keys"][1]]),
    s2="The usual fix is to work the value out on every call, but here every lookup is billed and a repeat call must make none.",
    p2='''import rates
from $C import load_$C
from $L import ${T}Bill
rows = list(load_$C())
bill = ${T}Bill()
bill.add(rows[0])
bill.add(rows[1])
bill.charge()
print(rates.LOOKUPS)
bill.charge()
print(rates.LOOKUPS)
''', e2=lambda c: "2\n2",
    why="Stale remembered charge. Lookups are billed, so keep the remembered value and clear it in add().",
))

T.append(dict(
    id="lost_write", symptom="S2", cause="LOSTWRITE", role="alternate", logic=["ledger", "holdings", "tally"], fix_fn="add",
    files={"$L.py": '''"""A ledger of $C."""


class ${T}Ledger:
    def __init__(self, $C=()):
        self._$C = list($C)

    def $C(self):
        """Return the $C held (a copy, so callers cannot change the ledger)."""
        return list(self._$C)

    def add(self, $I):
        """Add one $I to the ledger."""
        self.$C().append($I)

    def total(self):
        """Return the total $V of the $C held."""
        return sum(x.$V for x in self._$C)
'''},
    issue="After I add a $I, total() still returns the old total.",
    visible='''from $C import load_$C, ROWS
from $L import ${T}Ledger


def test_total_after_add():
    rows = list(load_$C())
    ledger = ${T}Ledger(rows[:1])
    ledger.add(rows[1])
    assert ledger.total() == ROWS[0][1] + ROWS[1][1]


def test_copy_is_safe():
    rows = list(load_$C())
    ledger = ${T}Ledger(rows[:2])
    ledger.$C().append(rows[2])
    assert ledger.total() == ROWS[0][1] + ROWS[1][1]
''',
    hidden='''from $C import load_$C, ROWS
from $L import ${T}Ledger


def test_total_after_add():
    rows = list(load_$C())
    ledger = ${T}Ledger(rows[:1])
    ledger.add(rows[1])
    assert ledger.total() == ROWS[0][1] + ROWS[1][1]


def test_add_to_empty():
    rows = list(load_$C())
    ledger = ${T}Ledger()
    for x in rows:
        ledger.add(x)
    assert ledger.total() == sum(v for _, v in ROWS) and len(ledger.$C()) == len(ROWS)


def test_copy_is_safe():
    rows = list(load_$C())
    ledger = ${T}Ledger(rows[:2])
    ledger.$C().append(rows[2])
    assert ledger.total() == ROWS[0][1] + ROWS[1][1]


def test_initial_total():
    assert ${T}Ledger(load_$C()).total() == sum(v for _, v in ROWS)
''',
    fix='''def add(self, $I):
    """Add one $I to the ledger."""
    self._$C.append($I)
''',
    s1="Either total() returns a remembered value that add() does not refresh, or add() never stores the $I.",
    p1='''from $C import load_$C
from $L import ${T}Ledger
rows = list(load_$C())
ledger = ${T}Ledger(rows[:1])
ledger.add(rows[1])
print(ledger.total(), sum(x.$V for x in ledger._$C), len(ledger._$C))
''', e1=lambda c: "%d %d 1" % (c["vals"][0], c["vals"][0]),
    s2="total() agrees with the list, and the list did not grow: add() loses the $I. Appending to the real list should give the right total.",
    p2='''from $C import load_$C
from $L import ${T}Ledger
rows = list(load_$C())
ledger = ${T}Ledger(rows[:1])
ledger._$C.append(rows[1])
print(ledger.total())
''', e2=lambda c: str(c["vals"][0] + c["vals"][1]),
    why="Not a stale value: add() appends to a copy, so the $I is lost. Append to the real list.",
))

# ----------------------------------------------------------------------------------------------------------------- S3
T.append(dict(
    id="bound_range", symptom="S3", cause="BOUND", role="prior", logic=["positions", "spans", "ranges"], fix_fn="${V}_between",
    files={"$L.py": '''"""Position windows over $C."""


def ${V}_between($C, low, high):
    """Return the $V of the $C at positions low to high, both included. Positions start at 1."""
    return [x.$V for x in $C[low - 1:high - 1]]


def first_${V}s($C, n):
    """Return the $V of the first n $C."""
    return ${V}_between($C, 1, n)
'''},
    issue="${V}_between(data, 2, 4) returns two values. I expected three, for positions 2, 3 and 4: the last one is missing.",
    visible='''from $C import load_$C, ROWS
from $L import ${V}_between


def test_three_positions():
    data = list(load_$C())
    assert ${V}_between(data, 2, 4) == [v for _, v in ROWS[1:4]]


def test_low_above_high():
    data = list(load_$C())
    assert ${V}_between(data, 3, 2) == []
''',
    hidden='''from $C import load_$C, ROWS
from $L import ${V}_between, first_${V}s

VALUES = [v for _, v in ROWS]


def test_three_positions():
    assert ${V}_between(list(load_$C()), 2, 4) == VALUES[1:4]


def test_whole_range():
    assert ${V}_between(list(load_$C()), 1, len(ROWS)) == VALUES


def test_single_position():
    assert ${V}_between(list(load_$C()), 3, 3) == [VALUES[2]]


def test_first_n():
    assert first_${V}s(list(load_$C()), 2) == VALUES[:2]


def test_low_above_high():
    assert ${V}_between(list(load_$C()), 3, 2) == []
''',
    fix='''def ${V}_between($C, low, high):
    """Return the $V of the $C at positions low to high, both included. Positions start at 1."""
    return [x.$V for x in $C[low - 1:high]]
''',
    s1="The window may stop one position early.",
    p1='''from $C import load_$C
from $L import ${V}_between
data = list(load_$C())
print(${V}_between(data, 2, 4))
''', e1=lambda c: str(c["vals"][1:3]),
    s2="If the upper position is always left out, a one-position window is empty and the full window is one short.",
    p2='''from $C import load_$C
from $L import ${V}_between
data = list(load_$C())
print(len(${V}_between(data, 1, 1)), len(${V}_between(data, 1, len(data))))
''', e2=lambda c: "0 %d" % (c["N"] - 1),
    why="The upper bound stops one short. Extend it by one.",
))

T.append(dict(
    id="bound_loop", symptom="S3", cause="BOUND", role="prior", logic=["running", "cumulative", "progress"], fix_fn="running_$V",
    files={"$L.py": '''"""Running totals over $C."""


def running_$V($C):
    """Return the running total of $V after each $I, in order."""
    out = []
    total = 0
    for i in range(len($C) - 1):
        total += $C[i].$V
        out.append(total)
    return out


def final_$V($C):
    """Return the total $V of all $C, or 0 when there are none."""
    totals = running_$V($C)
    return totals[-1] if totals else 0
'''},
    issue="final_$V(data) is too low: it leaves out the last $I. running_$V(data) has $NM1 entries, not $N.",
    visible='''from $C import load_$C, ROWS
from $L import running_$V


def test_length():
    assert len(running_$V(list(load_$C()))) == len(ROWS)


def test_empty():
    assert running_$V([]) == []
''',
    hidden='''from $C import load_$C, ROWS
from $L import running_$V, final_$V

VALUES = [v for _, v in ROWS]


def test_length():
    assert len(running_$V(list(load_$C()))) == len(ROWS)


def test_final():
    assert final_$V(list(load_$C())) == sum(VALUES)


def test_first_entry():
    assert running_$V(list(load_$C()))[0] == VALUES[0]


def test_single():
    assert running_$V(list(load_$C())[:1]) == [VALUES[0]]


def test_empty():
    assert running_$V([]) == [] and final_$V([]) == 0
''',
    fix='''def running_$V($C):
    """Return the running total of $V after each $I, in order."""
    out = []
    total = 0
    for i in range(len($C)):
        total += $C[i].$V
        out.append(total)
    return out
''',
    s1="The loop may stop one $I early.",
    p1='''from $C import load_$C
from $L import running_$V
data = list(load_$C())
print(len(running_$V(data)), len(data))
''', e1=lambda c: "%d %d" % (c["N"] - 1, c["N"]),
    s2="If the loop always stops one short, one $I gives nothing and two give one entry.",
    p2='''from $C import load_$C
from $L import running_$V
data = list(load_$C())
print(running_$V(data[:1]), running_$V(data[:2]))
''', e2=lambda c: "[] [%d]" % c["vals"][0],
    why="The loop bound stops one short. Extend it by one.",
))

T.append(dict(
    id="bound_pages", symptom="S3", cause="BOUND", role="exception", logic=["pages", "paging", "sheets"], fix_fn="page_count",
    files={"$L.py": '''"""Pages of $C."""


def page_count(n_items, page_size):
    """Return how many pages are needed to show n_items, page_size to a page."""
    return n_items // page_size


def page($C, number, page_size):
    """Return page `number` of $C. Pages are numbered from 1."""
    start = (number - 1) * page_size
    return $C[start:start + page_size]


def all_pages($C, page_size):
    """Return every page of $C, in order."""
    return [page($C, n, page_size) for n in range(1, page_count(len($C), page_size) + 1)]
'''},
    issue="all_pages(data, $P) leaves out the last $C: with $N $C and $P to a page I get $NDP pages, and the last $NRP never appear.",
    visible='''from $C import load_$C, ROWS
from $L import all_pages, page_count


def test_last_items_present():
    pages = all_pages(list(load_$C()), $P)
    assert sum(len(p) for p in pages) == len(ROWS)


def test_exact_fit():
    assert page_count(6, 3) == 2
    assert len(all_pages(list(load_$C())[:4], 2)) == 2
''',
    hidden='''from $C import load_$C, ROWS
from $L import all_pages, page_count


def test_last_items_present():
    pages = all_pages(list(load_$C()), $P)
    assert [x.$V for p in pages for x in p] == [v for _, v in ROWS]


def test_partial_page_counted():
    assert page_count(7, 3) == 3 and page_count(1, 3) == 1


def test_exact_fit():
    assert page_count(6, 3) == 2 and page_count(3, 3) == 1


def test_no_empty_page():
    assert all(len(p) > 0 for p in all_pages(list(load_$C())[:4], 2))


def test_no_items():
    assert page_count(0, 3) == 0
''',
    fix='''def page_count(n_items, page_size):
    """Return how many pages are needed to show n_items, page_size to a page."""
    return (n_items + page_size - 1) // page_size
''',
    oldfix='''def page_count(n_items, page_size):
    """Return how many pages are needed to show n_items, page_size to a page."""
    return n_items // page_size + 1
''',
    s1="The page count may round down, dropping a last page that is not full.",
    p1='''from $L import page_count
print(page_count(7, 3), page_count(6, 3))
''', e1=lambda c: "2 2",
    s2="The usual fix is to extend the bound by one, but that would also add a page when the items fit exactly.",
    p2='''print(7 // 3 + 1, 6 // 3 + 1)
''', e2=lambda c: "3 3",
    why="The page count rounds down. Adding one would give an empty page on an exact fit, so round up instead.",
))

T.append(dict(
    id="flush_last", symptom="S3", cause="NOFLUSH", role="alternate", logic=["parsing", "reader", "intake"], fix_fn="parse_$C",
    files={"$L.py": '''"""Parsing $C from text."""
from $C import $T


def _parse_line(line):
    $K, $V = line.split(",")
    return $T($K.strip(), int($V))


def parse_$C(text):
    """Parse lines of '$K,$V' into $T records. Blank lines are skipped."""
    out = []
    line = ""
    for ch in text:
        if ch == "\\n":
            if line.strip():
                out.append(_parse_line(line))
            line = ""
        else:
            line += ch
    return out
'''},
    issue="parse_$C(text) leaves out the last $I of my file: $N lines give me $NM1 records.",
    visible='''from $C import ROWS
from $L import parse_$C

LINES = ["%s,%s" % (k, v) for k, v in ROWS]


def test_all_lines():
    assert len(parse_$C("\\n".join(LINES))) == len(ROWS)


def test_trailing_newline():
    assert len(parse_$C("\\n".join(LINES) + "\\n")) == len(ROWS)
''',
    hidden='''from $C import ROWS
from $L import parse_$C

LINES = ["%s,%s" % (k, v) for k, v in ROWS]


def test_all_lines():
    records = parse_$C("\\n".join(LINES))
    assert [(x.$K, x.$V) for x in records] == [(k, v) for k, v in ROWS]


def test_trailing_newline():
    assert len(parse_$C("\\n".join(LINES) + "\\n")) == len(ROWS)


def test_blank_lines():
    assert len(parse_$C(LINES[0] + "\\n\\n" + LINES[1] + "\\n  ")) == 2


def test_single_line():
    assert len(parse_$C(LINES[0])) == 1


def test_empty_text():
    assert parse_$C("") == []
''',
    fix='''def parse_$C(text):
    """Parse lines of '$K,$V' into $T records. Blank lines are skipped."""
    out = []
    line = ""
    for ch in text:
        if ch == "\\n":
            if line.strip():
                out.append(_parse_line(line))
            line = ""
        else:
            line += ch
    if line.strip():
        out.append(_parse_line(line))
    return out
''',
    s1="Either a loop bound stops one short, or the last line is only stored when a newline follows it.",
    p1='''from $L import parse_$C
print(len(parse_$C("a,1\\nb,2")), len(parse_$C("a,1\\nb,2\\n")))
''', e1=lambda c: "1 2",
    s2="With a final newline nothing is lost, so no bound is short: a line is stored only when a newline is seen.",
    p2='''from $L import parse_$C
print(len(parse_$C("a,1")), len(parse_$C("")))
''', e2=lambda c: "0 0",
    why="Not a loop bound: the last line is never stored when the text does not end with a newline. Store what is left after the loop.",
))
