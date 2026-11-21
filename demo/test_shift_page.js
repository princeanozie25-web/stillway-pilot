const fs = require("fs"); const html = fs.readFileSync(__dirname + "/Stillway Shift Replay.html", "utf8");
const script = html.slice(html.indexOf("<script>") + 8, html.lastIndexOf("</script>"));
const store = {}; const el = (id) => store[id] || (store[id] = { innerHTML: "", textContent: "", hidden: false, append() {}, classList: { toggle() {} }, dataset: {} });
global.document = { getElementById: el, createElement: () => ({ classList: { toggle() {} }, dataset: {}, set textContent(v) {}, set onclick(v) {} }), querySelectorAll: () => [] };
eval(script + "; for (const k in SYS) { sys = k; for (view = 0; view < 3; view++) render(); }");
console.log("page script ran for 4 systems x 3 views; board rows:", (store.board.innerHTML.match(/<tr>/g) || []).length, "metric rows:", (store.metrics.innerHTML.match(/<tr>/g) || []).length, "cards:", (store.cards.innerHTML.match(/class="card/g) || []).length);
