"""Development-only bug templates.  Never used for training, retrieval, the bank or sleep.

  G2  same cause as a training mechanism, changed preconditions
  G3  lookalikes: a training symptom with a cause absent from training; `oldfix` is the trained fix applied here
  G4  mechanisms and symptoms absent from training
"""

D = []

# ------------------------------------------------------------------------------------------------ G2 changed preconditions
D.append(dict(
    id="iter_attr", group="G2", symptom="S1", cause="ITER", logic=["summary", "overview", "digest"], fix_fn="__init__",
    files={"$L.py": '''"""Summary of $C."""


class ${T}Summary:
    def __init__(self, $C):
        self._$C = $C

    def count(self):
        """Return how many $C there are."""
        return sum(1 for _ in self._$C)

    def mean_$V(self):
        """Return the mean $V, or 0.0 when there are no $C."""
        total = sum(x.$V for x in self._$C)
        n = self.count()
        return total / n if n else 0.0
'''},
    issue="${T}Summary(load_$C()).mean_$V() returns 0.0, although the stored $C have a mean $V of $MEAN.",
    visible='''from $C import load_$C, ROWS
from $L import ${T}Summary

MEAN = sum(v for _, v in ROWS) / len(ROWS)


def test_mean_of_stored():
    assert abs(${T}Summary(load_$C()).mean_$V() - MEAN) < 1e-9


def test_count_of_list():
    assert ${T}Summary(list(load_$C())).count() == len(ROWS)
''',
    hidden='''from $C import load_$C, ROWS
from $L import ${T}Summary

MEAN = sum(v for _, v in ROWS) / len(ROWS)


def test_mean_of_stored():
    assert abs(${T}Summary(load_$C()).mean_$V() - MEAN) < 1e-9


def test_count_then_mean():
    s = ${T}Summary(load_$C())
    assert s.count() == len(ROWS) and abs(s.mean_$V() - MEAN) < 1e-9


def test_mean_twice():
    s = ${T}Summary(load_$C())
    s.mean_$V()
    assert abs(s.mean_$V() - MEAN) < 1e-9


def test_list_input():
    assert abs(${T}Summary(list(load_$C())).mean_$V() - MEAN) < 1e-9


def test_empty():
    assert ${T}Summary(iter([])).mean_$V() == 0.0
''',
    fix='''def __init__(self, $C):
    self._$C = list($C)
''',
))

D.append(dict(
    id="stale_remove", group="G2", symptom="S2", cause="STALE", logic=["pool", "stock", "reserve"], fix_fn="remove",
    files={"$L.py": '''"""A pool of $C with a remembered total."""


class ${T}Pool:
    def __init__(self):
        self._$C = []
        self._total = None

    def add(self, $I):
        """Add one $I to the pool."""
        self._$C.append($I)
        self._total = None

    def remove(self, $I):
        """Take one $I out of the pool."""
        self._$C.remove($I)

    def total(self):
        """Return the total $V of the $C in the pool."""
        if self._total is None:
            self._total = sum(x.$V for x in self._$C)
        return self._total
'''},
    issue="After remove(), total() still counts the $I I took out. add() works as expected.",
    visible='''from $C import load_$C, ROWS
from $L import ${T}Pool


def test_total_after_remove():
    rows = list(load_$C())
    pool = ${T}Pool()
    for x in rows:
        pool.add(x)
    full = pool.total()
    pool.remove(rows[0])
    assert pool.total() == full - ROWS[0][1]


def test_total_after_add():
    rows = list(load_$C())
    pool = ${T}Pool()
    pool.add(rows[0])
    pool.total()
    pool.add(rows[1])
    assert pool.total() == ROWS[0][1] + ROWS[1][1]
''',
    hidden='''from $C import load_$C, ROWS
from $L import ${T}Pool


def filled():
    rows = list(load_$C())
    pool = ${T}Pool()
    for x in rows:
        pool.add(x)
    return pool, rows


def test_total_after_remove():
    pool, rows = filled()
    full = pool.total()
    pool.remove(rows[0])
    assert pool.total() == full - ROWS[0][1]


def test_remove_two():
    pool, rows = filled()
    full = pool.total()
    pool.remove(rows[1])
    assert pool.total() == full - ROWS[1][1]
    pool.remove(rows[2])
    assert pool.total() == full - ROWS[1][1] - ROWS[2][1]


def test_total_after_add():
    rows = list(load_$C())
    pool = ${T}Pool()
    pool.add(rows[0])
    pool.total()
    pool.add(rows[1])
    assert pool.total() == ROWS[0][1] + ROWS[1][1]


def test_remove_all():
    pool, rows = filled()
    pool.total()
    for x in rows:
        pool.remove(x)
    assert pool.total() == 0
''',
    fix='''def remove(self, $I):
    """Take one $I out of the pool."""
    self._$C.remove($I)
    self._total = None
''',
))

D.append(dict(
    id="stale_peak", group="G2", symptom="S2", cause="STALE", extra="rates", logic=["tracker", "monitor", "watch"], fix_fn="record",
    files={"$L.py": '''"""Peak weighted $V. Rate lookups are billed, so the peak is remembered."""
import rates


class ${T}Tracker:
    def __init__(self):
        self._$C = []
        self._peak = None

    def record(self, $I):
        """Record one $I."""
        self._$C.append($I)

    def peak(self):
        """Return the highest $V times rate seen so far, or 0 when nothing is recorded.

        The result is remembered: asking again without recording anything makes no new rate lookups.
        """
        if self._peak is None:
            self._peak = max((x.$V * rates.rate_for(x.$K) for x in self._$C), default=0)
        return self._peak
'''},
    issue="peak() does not go up after I record a $I with a higher weighted $V.",
    visible='''import rates
from $C import $T
from $L import ${T}Tracker

KEY = sorted(rates._RATES)[0]


def test_peak_after_record():
    t = ${T}Tracker()
    t.record($T(KEY, 2))
    assert t.peak() == 2 * rates._RATES[KEY]
    t.record($T(KEY, 9))
    assert t.peak() == 9 * rates._RATES[KEY]


def test_no_new_lookups_when_unchanged():
    t = ${T}Tracker()
    t.record($T(KEY, 2))
    t.record($T(KEY, 3))
    t.peak()
    before = rates.LOOKUPS
    t.peak()
    t.peak()
    assert rates.LOOKUPS == before
''',
    hidden='''import rates
from $C import $T, load_$C, ROWS
from $L import ${T}Tracker

KEY = sorted(rates._RATES)[0]


def test_peak_after_record():
    t = ${T}Tracker()
    t.record($T(KEY, 2))
    assert t.peak() == 2 * rates._RATES[KEY]
    t.record($T(KEY, 9))
    assert t.peak() == 9 * rates._RATES[KEY]


def test_peak_of_stored():
    t = ${T}Tracker()
    best = 0
    for x in load_$C():
        t.record(x)
        best = max(best, x.$V * rates._RATES[x.$K])
        assert t.peak() == best


def test_no_new_lookups_when_unchanged():
    t = ${T}Tracker()
    for x in load_$C():
        t.record(x)
    t.peak()
    before = rates.LOOKUPS
    t.peak()
    t.peak()
    assert rates.LOOKUPS == before


def test_nothing_recorded():
    assert ${T}Tracker().peak() == 0
''',
    fix='''def record(self, $I):
    """Record one $I."""
    self._$C.append($I)
    self._peak = None
''',
    oldfix='''def peak(self):
    """Return the highest $V times rate seen so far, or 0 when nothing is recorded.

    The result is remembered: asking again without recording anything makes no new rate lookups.
    """
    return max((x.$V * rates.rate_for(x.$K) for x in self._$C), default=0)
''',
))

D.append(dict(
    id="bound_lower", group="G2", symptom="S3", cause="BOUND", logic=["changes", "deltas", "steps"], fix_fn="${V}_changes",
    files={"$L.py": '''"""Changes in $V from one $I to the next."""


def ${V}_changes($C):
    """Return the change in $V from each $I to the next: one entry for every neighbouring pair."""
    out = []
    for i in range(2, len($C)):
        out.append($C[i].$V - $C[i - 1].$V)
    return out


def biggest_rise($C):
    """Return the largest increase between neighbours, or 0 when there is none."""
    rises = [c for c in ${V}_changes($C) if c > 0]
    return max(rises) if rises else 0
'''},
    issue="${V}_changes(data) has $NM2 entries for $N $C. I expected $NM1: the change from the first $I to the second is missing.",
    visible='''from $C import load_$C, ROWS
from $L import ${V}_changes


def test_number_of_changes():
    assert len(${V}_changes(list(load_$C()))) == len(ROWS) - 1


def test_single_item():
    assert ${V}_changes(list(load_$C())[:1]) == []
''',
    hidden='''from $C import load_$C, ROWS
from $L import ${V}_changes, biggest_rise

VALUES = [v for _, v in ROWS]
EXPECTED = [VALUES[i] - VALUES[i - 1] for i in range(1, len(VALUES))]


def test_number_of_changes():
    assert len(${V}_changes(list(load_$C()))) == len(ROWS) - 1


def test_values():
    assert ${V}_changes(list(load_$C())) == EXPECTED


def test_two_items():
    assert ${V}_changes(list(load_$C())[:2]) == EXPECTED[:1]


def test_biggest_rise():
    assert biggest_rise(list(load_$C())) == max([c for c in EXPECTED if c > 0] or [0])


def test_single_item():
    assert ${V}_changes(list(load_$C())[:1]) == [] and ${V}_changes([]) == []
''',
    fix='''def ${V}_changes($C):
    """Return the change in $V from each $I to the next: one entry for every neighbouring pair."""
    out = []
    for i in range(1, len($C)):
        out.append($C[i].$V - $C[i - 1].$V)
    return out
''',
))

# ------------------------------------------------------------------------------------------------ G3 lookalikes
D.append(dict(
    id="look_default_seen", group="G3", symptom="S1", cause="DEFAULTARG", logic=["distinct", "unique", "firsts"], fix_fn="new_${K}s",
    files={"$L.py": '''"""Distinct $K values among $C."""


def new_${K}s($C, seen=set()):
    """Return each $K the first time it appears among the $C, in order. $K values already in `seen` are left out."""
    out = []
    for x in $C:
        if x.$K not in seen:
            seen.add(x.$K)
            out.append(x.$K)
    return out


def count_${K}s($C):
    """Return how many distinct $K values the $C have."""
    return len(set(x.$K for x in $C))
'''},
    issue="new_${K}s(data) returns the right list the first time and an empty list the second time, with the same data.",
    visible='''from $C import load_$C, ROWS
from $L import new_${K}s

EXPECTED = list(dict.fromkeys(k for k, _ in ROWS))


def test_called_twice():
    data = list(load_$C())
    new_${K}s(data)
    assert new_${K}s(data) == EXPECTED


def test_known_values_left_out():
    data = list(load_$C())
    assert new_${K}s(data, {EXPECTED[0]}) == EXPECTED[1:]
''',
    hidden='''from $C import load_$C, ROWS
from $L import new_${K}s

EXPECTED = list(dict.fromkeys(k for k, _ in ROWS))


def test_called_twice():
    data = list(load_$C())
    new_${K}s(data)
    assert new_${K}s(data) == EXPECTED


def test_three_calls_with_generators():
    new_${K}s(load_$C())
    new_${K}s(load_$C())
    assert new_${K}s(load_$C()) == EXPECTED


def test_known_values_left_out():
    data = list(load_$C())
    assert new_${K}s(data, {EXPECTED[0]}) == EXPECTED[1:]


def test_seen_is_updated():
    seen = set()
    new_${K}s(list(load_$C()), seen)
    assert seen == set(EXPECTED)
''',
    fix='''def new_${K}s($C, seen=None):
    """Return each $K the first time it appears among the $C, in order. $K values already in `seen` are left out."""
    if seen is None:
        seen = set()
    out = []
    for x in $C:
        if x.$K not in seen:
            seen.add(x.$K)
            out.append(x.$K)
    return out
''',
    oldfix='''def new_${K}s($C, seen=set()):
    """Return each $K the first time it appears among the $C, in order. $K values already in `seen` are left out."""
    $C = list($C)
    out = []
    for x in $C:
        if x.$K not in seen:
            seen.add(x.$K)
            out.append(x.$K)
    return out
''',
))

D.append(dict(
    id="look_shared_entries", group="G3", symptom="S2", cause="SHAREDATTR", extra="rates", logic=["accounts", "wallets", "tabs"], fix_fn="__init__",
    files={"$L.py": '''"""Accounts of $C. Rate lookups are billed, so each account remembers its charge."""
import rates


class ${T}Account:
    entries = []

    def __init__(self, name):
        self.name = name
        self._charge = None

    def add(self, $I):
        """Add one $I to this account."""
        self.entries.append($I)
        self._charge = None

    def charge(self):
        """Return this account's charge: $V times the rate for each $I's $K.

        The result is remembered: asking again without adding anything makes no new rate lookups.
        """
        if self._charge is None:
            self._charge = sum(x.$V * rates.rate_for(x.$K) for x in self.entries)
        return self._charge
'''},
    issue="charge() is wrong after add(): when I add a $I to one account, the charge of a second, new account is no longer 0.",
    visible='''import rates
from $C import load_$C, ROWS
from $L import ${T}Account


def test_accounts_are_separate():
    rows = list(load_$C())
    first = ${T}Account("first")
    first.add(rows[0])
    second = ${T}Account("second")
    assert second.charge() == 0


def test_no_new_lookups_when_unchanged():
    rows = list(load_$C())
    account = ${T}Account("solo")
    account.add(rows[0])
    account.charge()
    before = rates.LOOKUPS
    account.charge()
    account.charge()
    assert rates.LOOKUPS == before
''',
    hidden='''import rates
from $C import load_$C, ROWS
from $L import ${T}Account


def test_accounts_are_separate():
    rows = list(load_$C())
    first = ${T}Account("first")
    first.add(rows[0])
    second = ${T}Account("second")
    assert second.charge() == 0


def test_each_account_own_charge():
    rows = list(load_$C())
    a = ${T}Account("a")
    b = ${T}Account("b")
    a.add(rows[0])
    b.add(rows[1])
    assert a.charge() == ROWS[0][1] * rates._RATES[ROWS[0][0]] and b.charge() == ROWS[1][1] * rates._RATES[ROWS[1][0]]


def test_charge_after_add():
    rows = list(load_$C())
    a = ${T}Account("a")
    a.add(rows[0])
    first = a.charge()
    a.add(rows[1])
    assert a.charge() == first + ROWS[1][1] * rates._RATES[ROWS[1][0]]


def test_no_new_lookups_when_unchanged():
    rows = list(load_$C())
    account = ${T}Account("solo")
    account.add(rows[0])
    account.charge()
    before = rates.LOOKUPS
    account.charge()
    account.charge()
    assert rates.LOOKUPS == before
''',
    fix='''def __init__(self, name):
    self.name = name
    self.entries = []
    self._charge = None
''',
    oldfix='''def charge(self):
    """Return this account's charge: $V times the rate for each $I's $K.

    The result is remembered: asking again without adding anything makes no new rate lookups.
    """
    return sum(x.$V * rates.rate_for(x.$K) for x in self.entries)
''',
))

D.append(dict(
    id="look_labels", group="G3", symptom="S3", cause="SHORTZIP", logic=["labelled", "tagged", "marked"], fix_fn="labelled_${V}s",
    files={"$L.py": '''"""Labels for the $V of $C."""


def labelled_${V}s($C, labels):
    """Pair each $I's $V with its label, in order. $C beyond the end of `labels` get the label 'unlabelled'."""
    return [(labels[i], $C[i].$V) for i in range(len(labels))]


def label_width(labels):
    """Return the length of the longest label, or 0 when there are none."""
    return max((len(text) for text in labels), default=0)
'''},
    issue="labelled_${V}s(data, labels) leaves out the last $C when I pass fewer labels than $C. I expected them at the end with the label 'unlabelled'.",
    visible='''from $C import load_$C, ROWS
from $L import labelled_${V}s


def test_fewer_labels():
    data = list(load_$C())
    pairs = labelled_${V}s(data, ["a", "b"])
    assert len(pairs) == len(ROWS) and pairs[-1] == ("unlabelled", ROWS[-1][1])


def test_equal_lengths():
    data = list(load_$C())
    labels = ["l%d" % i for i in range(len(data))]
    assert labelled_${V}s(data, labels)[-1] == (labels[-1], ROWS[-1][1])
''',
    hidden='''from $C import load_$C, ROWS
from $L import labelled_${V}s

VALUES = [v for _, v in ROWS]


def test_fewer_labels():
    pairs = labelled_${V}s(list(load_$C()), ["a", "b"])
    assert pairs == [("a", VALUES[0]), ("b", VALUES[1])] + [("unlabelled", v) for v in VALUES[2:]]


def test_equal_lengths():
    data = list(load_$C())
    labels = ["l%d" % i for i in range(len(data))]
    assert labelled_${V}s(data, labels) == list(zip(labels, VALUES))


def test_no_labels():
    assert labelled_${V}s(list(load_$C()), []) == [("unlabelled", v) for v in VALUES]


def test_no_items():
    assert labelled_${V}s([], []) == []
''',
    fix='''def labelled_${V}s($C, labels):
    """Pair each $I's $V with its label, in order. $C beyond the end of `labels` get the label 'unlabelled'."""
    return [(labels[i] if i < len(labels) else "unlabelled", $C[i].$V) for i in range(len($C))]
''',
    oldfix='''def labelled_${V}s($C, labels):
    """Pair each $I's $V with its label, in order. $C beyond the end of `labels` get the label 'unlabelled'."""
    return [(labels[i], $C[i].$V) for i in range(len(labels) + 1)]
''',
))

D.append(dict(
    id="look_split_window", group="G3", symptom="S1", cause="SLICEINDEX", model="feed", logic=["halves", "splits", "parts"], fix_fn="split_window",
    files={"$L.py": '''"""Halves of a window over the $C feed."""
import itertools


def split_window(feed, size):
    """Read the next `size` $C from the feed and return their $V as (first half, second half).

    The feed may be endless. Exactly `size` items are read from it.
    """
    window = [x.$V for x in itertools.islice(feed, size)]
    half = size // 2
    return window[:half], window[size:]
'''},
    issue="split_window(feed_$C(), 4) returns the first half, but the second half is always empty. I expected two values in each.",
    visible='''from $C import feed_$C, ROWS
from $L import split_window


def test_second_half():
    first, second = split_window(feed_$C(), 4)
    assert second == [v for _, v in ROWS[2:4]]


def test_reads_only_the_window():
    feed = feed_$C()
    split_window(feed, 2)
    assert next(feed).$V == ROWS[2][1]
''',
    hidden='''from $C import feed_$C, ROWS
from $L import split_window

VALUES = [v for _, v in ROWS]


def test_second_half():
    first, second = split_window(feed_$C(), 4)
    assert second == VALUES[2:4]


def test_first_half():
    first, second = split_window(feed_$C(), 4)
    assert first == VALUES[:2]


def test_odd_size():
    first, second = split_window(feed_$C(), 3)
    assert first == VALUES[:1] and second == VALUES[1:3]


def test_reads_only_the_window():
    feed = feed_$C()
    split_window(feed, 2)
    assert next(feed).$V == ROWS[2][1]
''',
    fix='''def split_window(feed, size):
    """Read the next `size` $C from the feed and return their $V as (first half, second half).

    The feed may be endless. Exactly `size` items are read from it.
    """
    window = [x.$V for x in itertools.islice(feed, size)]
    half = size // 2
    return window[:half], window[half:]
''',
    oldfix='''def split_window(feed, size):
    """Read the next `size` $C from the feed and return their $V as (first half, second half).

    The feed may be endless. Exactly `size` items are read from it.
    """
    feed = list(feed)
    window = [x.$V for x in itertools.islice(feed, size)]
    half = size // 2
    return window[:half], window[size:]
''',
))

# ------------------------------------------------------------------------------------------------ G4 absent mechanisms
D.append(dict(
    id="float_equal", group="G4", symptom="X1", cause="FLOATEQ", logic=["settle", "reconcile", "balance"], fix_fn="is_settled",
    files={"$L.py": '''"""Checking that $C add up."""


def is_settled($C, expected_total):
    """Return True when the $V of the $C add up to expected_total. $V may be fractional."""
    return sum(x.$V for x in $C) == expected_total


def shortfall($C, expected_total):
    """Return how much $V is still missing, never less than 0."""
    return max(0, expected_total - sum(x.$V for x in $C))
'''},
    issue="is_settled() says False for two $C with $V 0.1 and 0.2 against an expected total of 0.3.",
    visible='''from $C import $T
from $L import is_settled


def test_tenths():
    assert is_settled([$T("a", 0.1), $T("b", 0.2)], 0.3)


def test_whole_numbers():
    assert is_settled([$T("a", 2), $T("b", 3)], 5)
''',
    hidden='''from $C import $T
from $L import is_settled


def test_tenths():
    assert is_settled([$T("a", 0.1), $T("b", 0.2)], 0.3)


def test_three_tenths():
    assert is_settled([$T("a", 0.1), $T("b", 0.1), $T("c", 0.1)], 0.3)


def test_not_settled():
    assert not is_settled([$T("a", 0.1), $T("b", 0.2)], 0.31)


def test_whole_numbers():
    assert is_settled([$T("a", 2), $T("b", 3)], 5) and not is_settled([$T("a", 2), $T("b", 3)], 6)


def test_nothing_owed():
    assert is_settled([], 0)
''',
    fix='''def is_settled($C, expected_total):
    """Return True when the $V of the $C add up to expected_total. $V may be fractional."""
    return abs(sum(x.$V for x in $C) - expected_total) < 1e-9
''',
))

D.append(dict(
    id="case_key", group="G4", symptom="X2", cause="NORMALISE", logic=["lookup", "search", "finder"], fix_fn="${C}_for",
    files={"$L.py": '''"""Finding $C by $K."""


def ${C}_for($C, $K):
    """Return the $C whose $K matches, ignoring upper and lower case and spaces at either end."""
    return [x for x in $C if x.$K == $K]


def has_$K($C, $K):
    """Return True when at least one $I matches the $K."""
    return len(${C}_for($C, $K)) > 0
'''},
    issue="${C}_for(data, ' $KUP ') returns nothing, although there are $C for '$K0'.",
    visible='''from $C import load_$C, ROWS
from $L import ${C}_for

KEY = ROWS[0][0]
COUNT = sum(1 for k, _ in ROWS if k == KEY)


def test_upper_case_with_spaces():
    assert len(${C}_for(list(load_$C()), " " + KEY.upper() + " ")) == COUNT


def test_exact():
    assert len(${C}_for(list(load_$C()), KEY)) == COUNT
''',
    hidden='''from $C import $T, load_$C, ROWS
from $L import ${C}_for, has_$K

KEY = ROWS[0][0]
COUNT = sum(1 for k, _ in ROWS if k == KEY)


def test_upper_case_with_spaces():
    assert len(${C}_for(list(load_$C()), " " + KEY.upper() + " ")) == COUNT


def test_stored_value_not_tidy():
    data = [$T("  Alpha", 1), $T("beta", 2), $T("ALPHA ", 3)]
    assert [x.$V for x in ${C}_for(data, "alpha")] == [1, 3]


def test_exact():
    assert len(${C}_for(list(load_$C()), KEY)) == COUNT


def test_no_match():
    assert ${C}_for(list(load_$C()), "zzz") == [] and not has_$K(list(load_$C()), "zzz")
''',
    fix='''def ${C}_for($C, $K):
    """Return the $C whose $K matches, ignoring upper and lower case and spaces at either end."""
    wanted = $K.strip().lower()
    return [x for x in $C if x.$K.strip().lower() == wanted]
''',
))

D.append(dict(
    id="int_division", group="G4", symptom="X3", cause="INTDIV", logic=["percent", "portion", "ratio"], fix_fn="percent_of_total",
    files={"$L.py": '''"""Percentages of the total $V."""


def percent_of_total($C, $K):
    """Return the percentage, from 0 to 100, of the total $V that belongs to this $K."""
    total = sum(x.$V for x in $C)
    part = sum(x.$V for x in $C if x.$K == $K)
    return part // total * 100


def total_$V($C):
    """Return the total $V."""
    return sum(x.$V for x in $C)
'''},
    issue="percent_of_total(data, '$K0') returns 0, although '$K0' has $PART of the total $TOTAL.",
    visible='''from $C import load_$C, ROWS
from $L import percent_of_total

KEY = ROWS[0][0]
TOTAL = sum(v for _, v in ROWS)
PART = sum(v for k, v in ROWS if k == KEY)


def test_percent():
    assert abs(percent_of_total(list(load_$C()), KEY) - 100.0 * PART / TOTAL) < 1e-6


def test_unknown_key():
    assert percent_of_total(list(load_$C()), "zzz") == 0
''',
    hidden='''from $C import $T, load_$C, ROWS
from $L import percent_of_total

KEYS = sorted(set(k for k, _ in ROWS))
TOTAL = sum(v for _, v in ROWS)


def test_percent():
    key = ROWS[0][0]
    part = sum(v for k, v in ROWS if k == key)
    assert abs(percent_of_total(list(load_$C()), key) - 100.0 * part / TOTAL) < 1e-6


def test_percentages_add_up():
    data = list(load_$C())
    assert abs(sum(percent_of_total(data, k) for k in KEYS) - 100.0) < 1e-6


def test_everything():
    assert abs(percent_of_total([$T("a", 4), $T("a", 6)], "a") - 100.0) < 1e-6


def test_unknown_key():
    assert percent_of_total(list(load_$C()), "zzz") == 0
''',
    fix='''def percent_of_total($C, $K):
    """Return the percentage, from 0 to 100, of the total $V that belongs to this $K."""
    total = sum(x.$V for x in $C)
    part = sum(x.$V for x in $C if x.$K == $K)
    return part / total * 100
''',
))

D.append(dict(
    id="sort_text_numbers", group="G4", symptom="X4", cause="TEXTSORT", logic=["ranking", "ordering", "sequence"], fix_fn="ranked_codes",
    files={"$L.py": '''"""Codes of $C in order."""


def ranked_codes($C):
    """Return the $V of each $I as a text code, from the lowest number to the highest."""
    return sorted(str(x.$V) for x in $C)


def code_of($I):
    """Return the text code of one $I."""
    return str($I.$V)
'''},
    issue="ranked_codes() puts '10' before '9'. I expected the codes in number order.",
    visible='''from $C import $T
from $L import ranked_codes


def test_nine_before_ten():
    assert ranked_codes([$T("a", 10), $T("b", 9)]) == ["9", "10"]


def test_single_digits():
    assert ranked_codes([$T("a", 3), $T("b", 1), $T("c", 2)]) == ["1", "2", "3"]
''',
    hidden='''from $C import $T, load_$C, ROWS
from $L import ranked_codes


def test_nine_before_ten():
    assert ranked_codes([$T("a", 10), $T("b", 9)]) == ["9", "10"]


def test_mixed_lengths():
    assert ranked_codes([$T("a", 100), $T("b", 25), $T("c", 9), $T("d", 1000)]) == ["9", "25", "100", "1000"]


def test_stored():
    assert ranked_codes(list(load_$C())) == [str(v) for v in sorted(v for _, v in ROWS)]


def test_codes_are_text():
    assert all(isinstance(c, str) for c in ranked_codes(list(load_$C())))


def test_empty():
    assert ranked_codes([]) == []
''',
    fix='''def ranked_codes($C):
    """Return the $V of each $I as a text code, from the lowest number to the highest."""
    return [str(v) for v in sorted(x.$V for x in $C)]
''',
))
