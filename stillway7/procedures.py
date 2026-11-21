"""Teacher-authored wording of the diagnostics, and the 'naive' tests used to record a contradiction.

A diagnostic is keyed by symptom.  Version 1 is the prior procedure with its scope.  Version 2 keeps version 1 and adds a
local exception and what to do when the test contradicts the diagnostic.  The bank builder (v07/build_bank.py) admits a
clause only when executed training records support it."""

PROC = {
 "S1": dict(symptom="A result is empty or short the second time the same data is used.",
            test="Check whether the data is a one-shot iterator: print(iter(data) is data), or show that a second use finds nothing left.",
            confirmed="It is a one-shot iterator walked twice. Turn it into a list once, where the function first receives it.",
            scope="The whole input is finite.",
            exception="If the input never ends (check how many items a bounded read can pull), turn only the bounded part that is read into a list, never the whole input.",
            contradiction="If the data is already a list, this diagnostic does not apply and list() will not help. Check whether a called function removes items from the caller's list; if it does, make it work on a copy.",
            prior_cause="ITER", alternate_cause="MUT"),
 "S2": dict(symptom="A derived value (a total, a count, a lookup) is wrong after an update.",
            test="After an update, print the value the function returns next to the same value worked out from the stored data.",
            confirmed="They differ: a remembered value is stale. Work the value out from the stored data on every call.",
            scope="Working the value out again costs nothing.",
            exception="If working it out again is billed or counted (a repeat call must make no new lookups), keep the remembered value and clear it in the function that changes the data.",
            contradiction="If the two agree, nothing is stale and recomputing will not help. Check whether the update reached the stored data at all (print its length); if it did not, fix the function that writes.",
            prior_cause="STALE", alternate_cause="LOSTWRITE"),
 "S3": dict(symptom="An element at the edge, usually the last one, is missing.",
            test="Count what comes out against what went in, for a normal input and for the smallest inputs.",
            confirmed="A range or slice bound stops one short. Extend the bound by one.",
            scope="Extending by one is right for every input size.",
            exception="If the bound comes from a division (pages, batches), adding one breaks exact fits (check 6 // 3 + 1). Round up instead: (n + size - 1) // size.",
            contradiction="If nothing is lost when the input ends cleanly, no bound is short and this diagnostic does not apply. Check whether the last piece is only stored when a terminator follows it; if so, store what is left after the loop.",
            prior_cause="BOUND", alternate_cause="NOFLUSH"),
}

# A naive test: what a diagnostician who assumes the prior procedure applies would run, with the prediction that turns
# out wrong.  step 1: the naive test replaces test 1 and the teacher's test 1 becomes test 2.  step 2: it replaces test 2.
NAIVE = {
 "iter_window": dict(step=2, s="If the feed is finite, turning the whole input into a list once is enough.",
                     p='''import itertools
from $C import feed_$C
print(len(list(itertools.islice(feed_$C(), 1000))))
''', e=lambda c: str(c["N"])),
 "stale_rates": dict(step=2, s="If working the charge out again costs nothing, doing it on every call is enough.",
                     p='''import rates
from $C import load_$C
from $L import ${T}Bill
rows = list(load_$C())
bill = ${T}Bill()
bill.add(rows[0])
bill.add(rows[1])
bill.charge()
before = rates.LOOKUPS
bill._charge = None
bill.charge()
print(rates.LOOKUPS - before)
''', e=lambda c: "0"),
 "bound_pages": dict(step=2, s="If one more page is always right, adding one to the count is enough.",
                     p='''print(7 // 3 + 1, 6 // 3 + 1)
''', e=lambda c: "3 2"),
 "mut_drain": dict(step=1, s="The data may be a one-shot iterator that is used twice.",
                   p='''from $C import load_$C
data = list(load_$C())
print(iter(data) is data)
''', e=lambda c: "True"),
 "lost_write": dict(step=1, s="total() may return a remembered value that add() does not refresh.",
                    p='''from $C import load_$C
from $L import ${T}Ledger
rows = list(load_$C())
ledger = ${T}Ledger(rows[:1])
ledger.add(rows[1])
print(ledger.total(), sum(x.$V for x in ledger._$C))
''', e=lambda c: "%d %d" % (c["vals"][0], c["vals"][0] + c["vals"][1])),
 "flush_last": dict(step=1, s="A loop bound may stop one line short.",
                    p='''from $L import parse_$C
print(len(parse_$C("a,1\\nb,2\\n")))
''', e=lambda c: "1"),
}
