// Stillway planner core in plain JavaScript.  Same maths as stillway/model.py (sweep reader, VQ memory).
// step(ids, obs) -> {logits, ids}: code IDs in, code IDs out.  Nothing else is carried between steps.
function makeEngine(M) {
  const dec = (t) => { const b = atob(t.data), u = new Uint8Array(b.length); for (let i = 0; i < b.length; i++) u[i] = b.charCodeAt(i);
    return { shape: t.shape, d: new Float32Array(u.buffer) }; };
  const W = {}; for (const k in M.w) W[k] = dec(M.w[k]);
  const S = M.cfg.n_slots, K = M.cfg.n_codes, D = M.cfg.code_dim, H = M.cfg.width;
  const lin = (w, b, x) => { const [o, n] = w.shape, y = new Float64Array(o);
    for (let i = 0; i < o; i++) { let s = b.d[i]; const r = i * n; for (let j = 0; j < n; j++) s += w.d[r + j] * x[j]; y[i] = s; } return y; };
  const relu = (x) => x.map((v) => (v > 0 ? v : 0));
  const sig = (v) => 1 / (1 + Math.exp(-v));
  const mlp = (p, x) => lin(W[p + ".2.weight"], W[p + ".2.bias"], relu(lin(W[p + ".0.weight"], W[p + ".0.bias"], x)));
  function gru(x, h) {
    const gi = lin(W["cell.weight_ih"], W["cell.bias_ih"], x), gh = lin(W["cell.weight_hh"], W["cell.bias_hh"], h), o = new Float64Array(H);
    for (let i = 0; i < H; i++) { const r = sig(gi[i] + gh[i]), z = sig(gi[H + i] + gh[H + i]), n = Math.tanh(gi[2 * H + i] + r * gh[2 * H + i]);
      o[i] = (1 - z) * n + z * h[i]; } return o; }
  function step(ids, obs) {
    const g = obs.slice(0, 6).concat(obs.slice(22)), eff = obs.slice(6, 22);
    const xg = mlp("enc_g", g), x2 = mlp("enc_leg", g.concat(eff.slice(8, 16))), x1 = mlp("enc_leg", g.concat(eff.slice(0, 8)));
    const mem = new Float64Array(S * D);
    for (let s = 0; s < S; s++) if (ids[s] >= 0) for (let j = 0; j < D; j++) mem[s * D + j] = W.codebook.d[(s * K + ids[s]) * D + j];
    let h = lin(W["mem_in.weight"], W["mem_in.bias"], mem).map(Math.tanh);
    for (const x of [xg, x2, x1, xg]) h = gru(x, h);
    const logits = Array.from(lin(W["head.weight"], W["head.bias"], h)), ze = lin(W["to_slots.weight"], W["to_slots.bias"], h), out = [];
    for (let s = 0; s < S; s++) { let best = -1, bd = Infinity;
      for (let k = 0; k < K; k++) { if (!M.active[s][k]) continue; let d = 0;
        for (let j = 0; j < D; j++) { const t = ze[s * D + j] - W.codebook.d[(s * K + k) * D + j]; d += t * t; }
        if (d < bd) { bd = d; best = k; } } out.push(best); }
    return { logits, ids: out }; }
  return { step, S, K };
}
if (typeof module !== "undefined") module.exports = { makeEngine };
