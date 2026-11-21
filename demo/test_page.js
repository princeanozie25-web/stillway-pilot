// Run the page's own script under a stub DOM and play every scenario to the end.
const fs = require("fs");
const html = fs.readFileSync(__dirname + "/Stillway Replay Bench.html", "utf8");
const script = html.slice(html.indexOf("<script>") + 8, html.lastIndexOf("</script>"));
const stub = () => new Proxy(function () {}, { get: (t, k) => (k === Symbol.toPrimitive ? () => "" : k === "classList" ? { toggle() {} } : k === "dataset" ? {} : k === "style" ? {} : k === "forEach" ? () => {} : stub()), set: () => true, apply: () => stub() });
global.document = { getElementById: () => stub(), createElement: () => stub(), querySelectorAll: () => [] };
global.atob = (s) => Buffer.from(s, "base64").toString("binary");
const out = eval(script + `;(() => { const o = {}; for (const k of Object.keys(SCEN)) { loadScen(k); const paused = S.ids.slice(); const en = lookup(S.w.e, S.st, S.ids); while (S.st < 5) step();
  o[k] = { gate: S.w.arr, wantGate: S.w.order.q, dock: S.w.dock, wantDock: S.w.order.d, bay: S.w.bay, wantBay: tb(S.w.order.b, S.w.closed), pausedIds: paused, meaningAtPause: en ? en[0] : en, auth: S.log.filter(r => r.auth).map(r => r.auth).join(",") }; } return o; })()`);
for (const k in out) console.log(k, JSON.stringify(out[k]));
