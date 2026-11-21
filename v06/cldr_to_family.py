"""Turn Unicode CLDR plural rules into a family file for v06/family.py.   (Written before the data was fetched.)

    python -I v06/cldr_to_family.py data/external/cldr/plurals.json cardinal data/external/cldr/family_cardinal.json
    python -I v06/cldr_to_family.py data/external/cldr/ordinals.json ordinal data/external/cldr/family_ordinal.json

A policy = one locale's rule: integer n -> plural category.  Cases = n from 0 to 999, as three attributes
(hundreds, tens, ones digit).  Decisions: 0 zero, 1 one, 2 two, 3 few, 4 many, 5 other.
Rule syntax (Unicode TR35):  cond = and ('or' and)* ; and = rel ('and' rel)* ; rel = operand ['%' int] ('=' | '!=') list ;
list = item (',' item)* ; item = int ['..' int].  Operands for an integer n: n = i = n; v, w, f, t, c, e = 0.  Samples after '@' are dropped.
Split: a locale is "past" when the first byte of SHA-256 of its code is below 154 (60%), else "new".
"""
import hashlib, json, re, sys
CATS = ["zero", "one", "two", "few", "many", "other"]; TOK = re.compile(r"\s*(\.\.|!=|=|%|,|and|or|[a-z]|\d+)")

def tokens(s):
    out, i = [], 0; s = s.strip()
    while i < len(s):
        m = TOK.match(s, i)
        if not m: raise ValueError(f"cannot read {s[i:i + 12]!r}")
        out.append(m.group(1)); i = m.end()
    return out

def evaluate(cond, n):
    t = tokens(cond); pos = [0]
    if not t: return True
    def peek(): return t[pos[0]] if pos[0] < len(t) else None
    def take(): pos[0] += 1; return t[pos[0] - 1]
    def rel():
        op = take(); val = n if op in ("n", "i") else 0
        if op not in "nivwftce": raise ValueError(op)
        if peek() == "%": take(); val = val % int(take())
        cmp_ = take(); items = []
        if cmp_ not in ("=", "!="): raise ValueError(cmp_)
        while True:
            lo = int(take()); hi = lo
            if peek() == "..": take(); hi = int(take())
            items.append((lo, hi))
            if peek() == ",": take()
            else: break
        hit = any(lo <= val <= hi for lo, hi in items); return hit if cmp_ == "=" else not hit
    def conj():
        r = rel()
        while peek() == "and": take(); r = rel() and r
        return r
    r = conj()
    while peek() == "or": take(); r = conj() or r
    if pos[0] != len(t): raise ValueError("trailing tokens")
    return r

if __name__ == "__main__":
    src, kind, dst = sys.argv[1:4]; d = json.load(open(src))["supplemental"][f"plurals-type-{kind}"]; pol = {}; skipped = []
    for loc, rules in sorted(d.items()):
        conds = {k.rsplit("-", 1)[1]: v.split("@")[0] for k, v in rules.items()}
        try: pol[loc] = "".join(str(next((CATS.index(c) for c in CATS[:5] if c in conds and evaluate(conds[c], n)), 5)) for n in range(1000))
        except Exception as ex: skipped.append((loc, str(ex)))
    past = [l for l in pol if hashlib.sha256(l.encode()).digest()[0] < 154]; new = [l for l in pol if l not in past]
    json.dump({"name": f"cldr_{kind}", "attributes": [10, 10, 10], "decisions": 6, "policies": pol, "past": past, "new": new, "source": "Unicode CLDR, cldr-json, cldr-core/supplemental", "skipped": skipped}, open(dst, "w"))
    print(kind, len(pol), "locales;", len(set(pol.values())), "distinct rules;", len(past), "past,", len(new), "new;", len({pol[l] for l in new} - {pol[l] for l in past}), "distinct new rules not among past;", "skipped", skipped)
