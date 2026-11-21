const fs = require("fs"); const { makeEngine } = require("./engine.js");
global.atob = (s) => Buffer.from(s, "base64").toString("binary");
const M = JSON.parse(fs.readFileSync(__dirname + "/model.json")), V = JSON.parse(fs.readFileSync(__dirname + "/testvec.json"));
const E = makeEngine(M); const cb = new Float32Array(Buffer.from(M.w.codebook.data, "base64").buffer); const [S, K, D] = M.w.codebook.shape;
const stages = {}; let maxd = 0;
for (const [ids, obs, a, nxt] of V) { const r = E.step(ids, obs), st = obs.slice(0, 6).indexOf(1);
  r.ids.forEach((x, s) => { if (x !== nxt[s]) { stages[st] = (stages[st] || 0) + 1; let d = 0;
    for (let j = 0; j < D; j++) { const t = cb[(s * K + x) * D + j] - cb[(s * K + nxt[s]) * D + j]; d += t * t; } maxd = Math.max(maxd, Math.sqrt(d)); } }); }
console.log("slot mismatches by stage", stages, "largest distance between the two codes chosen", maxd);
