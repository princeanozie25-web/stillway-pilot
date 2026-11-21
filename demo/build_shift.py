"""Build the shift replay page:  python demo/build_shift.py v2_iit_s1 demo/shift_facts.json"""
import json, sys
name, facts = sys.argv[1], sys.argv[2]
tpl = open("demo/shift_template.html").read()
html = (tpl.replace("/*EXAMPLE*/", open(f"results/v02/shift/{name}_example.json").read()).replace("/*METRICS*/", open(f"results/v02/shift/{name}.json").read())
           .replace("/*FACTS*/", open(facts).read()))
open("demo/Stillway Shift Replay.html", "w").write(html); print("built", len(html) // 1024, "KB")
