// node demo/verify.js : the JS engine must reproduce PyTorch on every exported test step.
const fs = require("fs"); const { makeEngine } = require("./engine.js");
global.atob = (s) => Buffer.from(s, "base64").toString("binary");
const M = JSON.parse(fs.readFileSync(__dirname + "/model.json")), V = JSON.parse(fs.readFileSync(__dirname + "/testvec.json"));
const E = makeEngine(M), ACT = { 2: [0, 1], 3: [2, 3], 4: [0, 1], 5: [4, 5, 6] }; let badA = 0, badS = 0;
for (const [ids, obs, a, nxt] of V) { const r = E.step(ids, obs), st = obs.slice(0, 6).indexOf(1);
  if (ACT[st]) { let b = ACT[st][0]; for (const c of ACT[st]) if (r.logits[c] > r.logits[b]) b = c; if (b !== a) badA++; }
  if (r.ids.join() !== nxt.join()) badS++; }
console.log(`checked ${V.length} steps: ${badA} action mismatches, ${badS} state mismatches`);
