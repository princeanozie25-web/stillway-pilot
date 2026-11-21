"""Build demo/Stillway Proof Bench.html: the certified tables of three v0.3 cores, run in the browser.
    PYTHONPATH=. python demo/build_proof.py
Tables are read off the checkpoints with stillway3.certify.extract (the same tables the certificate checks)."""
import json, os
from stillway3.certify import certify, extract
from stillway3.model import load_reg

CORES = [("v3r24fix_s1", "Trained on 2 to 4-leg jobs, then repaired"), ("v3o_s1", "Trained from logged outcomes only (no planner labels)"), ("v3r24_s1", "Trained on 2 to 4-leg jobs, before repair")]
out = []
for name, label in CORES:
    m = load_reg(f"runs/{name}/checkpoint.pt"); tab = extract(m); c = certify(tab, "all", 0); man = json.load(open(f"runs/{name}/manifest.json"))
    clean = c["route_wrong"] == 0
    note = {"v3r24fix_s1": "Imitation of the exact planner on jobs of 2 to 4 legs, then %d rounds of repair on the cases the check found. " % (len(man.get("repair_rounds", [])) - 1),
            "v3o_s1": "Never shown what the exact planner would do. It learned from logged jobs with random actions and how they ended. ",
            "v3r24_s1": "The same training as the first planner, before any repair. On sampled jobs it looks perfect; the check finds the rare cases. "}[name]
    note += f"Checkpoint {m.sha256[:12]}. Check on all 64 leg kinds: {c['route_wrong']:,} wrong of {c['route_checks']:,} entries."
    out.append({"name": name, "label": label, "status": "ok" if clean else "bad", "statusText": "proven for every length" if clean else "not proven", "note": note,
                "term": tab["term"], "cell": "".join(chr(48 + x) for row in tab["cell"] for x in row), "route": "".join(str(x) for row in tab["route"] for leg in row for x in leg)})
facts = "Gate requirements and routes only; deliveries are a 12-entry table that the full certificate also checks. The page runs the planners' integer tables, not the networks. Numbers and method: results/v03/REPORT_v03.md in the repository."
html = open("demo/proof_template.html").read().replace("/*DATA*/null", json.dumps({"cores": out, "facts": facts}))
open("demo/Stillway Proof Bench.html", "w").write(html); print("wrote demo/Stillway Proof Bench.html", len(html), "bytes", [(o["name"], o["statusText"]) for o in out])
