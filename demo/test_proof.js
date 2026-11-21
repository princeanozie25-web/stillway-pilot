// Runs the page's own script without a browser and prints the check for each embedded planner.
//   node demo/test_proof.js          (compare with results/v03/cert/*.json and stillway3/check_tables.py)
const fs = require("fs"); const h = fs.readFileSync(__dirname + "/Stillway Proof Bench.html", "utf8");
const js = h.slice(h.indexOf("<script>") + 8, h.lastIndexOf("</script>")); const els = {};
const mk = id => els[id] || (els[id] = { value: "0", innerHTML: "", textContent: "", hidden: false, options: [], add(o) { this.options.push(o); }, scrollIntoView() {} });
global.document = { getElementById: mk }; global.Option = function (l, v) { this.l = l; this.v = v; }; global.performance = { now: () => Date.now() };
els.pause = { value: "4", max: 0 }; els.nlegs = { value: "8" }; els.corrField = { value: "0" }; els.corrVal = { value: "2" };
eval(js + ";globalThis.__t={check,cores,run,els,get job(){return job}}"); const t = globalThis.__t;
const strip = x => x.replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();
for (const c of t.cores) { const r = t.check(c.tab); console.log(c.name, "pairs", r.pairs, "checks", r.checks, "wrong", r.wrong, "codes", r.codes); }
console.log("job at load:", strip(els.verdict.innerHTML));
els.damage.onclick(); console.log("after damaging one entry:", strip(els.stats.innerHTML).slice(0, 40));
els.loadWit.onclick(); console.log("failing job loaded:", t.job.legs.length, "legs;", strip(els.verdict.innerHTML).slice(0, 110));
els.undo.onclick(); console.log("after undo:", strip(els.stats.innerHTML).slice(0, 40));
