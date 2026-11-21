"""Build the self-contained replay page.

    PYTHONPATH=. python demo/build.py runs/NAME "KC-KT" facts.json
Injects the JS engine, the checkpoint, the dictionary for the demo family and the headline facts.
"""
import json, os, sys
from stillway.fixtures import families
from stillway.world import EFFECT_NAMES

run, fam, facts_path = sys.argv[1].rstrip("/"), sys.argv[2], sys.argv[3]
tpl = open("demo/template.html").read()
model = open("demo/model.json").read()
dic_all = json.load(open(os.path.join(run, "dictionary_sealed.json" if os.path.exists(os.path.join(run, "dictionary_sealed.json")) else "dictionary_dev.json")))
facts = json.load(open(facts_path))
a, b = fam.split("-")
meta = {"demo_layout": [EFFECT_NAMES.index(a[0]), EFFECT_NAMES.index(a[1]), EFFECT_NAMES.index(b[0]), EFFECT_NAMES.index(b[1])],
        "gate_slots": json.load(open(os.path.join(run, "slots.json")))["slots"],
        "sealed_families": families("sealed"), "train_families": families("train"), "facts": facts["facts"], "foot": facts["foot"]}
html = (tpl.replace("/*ENGINE*/", open("demo/engine.js").read().split("if (typeof module")[0])
           .replace("/*MODEL*/", model).replace("/*DICT*/", json.dumps({fam: dic_all[fam]})).replace("/*META*/", json.dumps(meta)))
open("demo/Stillway Replay Bench.html", "w").write(html)
print("built", len(html) // 1024, "KB")
