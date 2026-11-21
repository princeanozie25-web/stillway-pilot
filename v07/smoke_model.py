"""Smoke test of the pinned student: inference, one adapter update, save, reload, same output.   python v07/smoke_model.py"""
import json, os, platform, sys, time
import torch
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from stillway7.student import PIN, Student
out = {"hardware": {"machine": platform.machine(), "processor": os.popen("sysctl -n machdep.cpu.brand_string").read().strip(), "memory_bytes": int(os.popen("sysctl -n hw.memsize").read()), "os": platform.platform()},
       "software": {"python": platform.python_version(), "torch": torch.__version__, "transformers": __import__("transformers").__version__, "safetensors": __import__("safetensors").__version__}}
t0 = time.time(); s = Student(); out["device"] = s.device; out["dtype"] = str(s.dtype); out["quantisation"] = "none (32-bit floats)"; out["load_seconds"] = round(time.time() - t0, 1); out["parameters"] = sum(p.numel() for p in s.model.parameters())
sysm = "You are a careful Python programmer."; q = ["Write a Python function that returns the n-th Fibonacci number.", "Fix the bug:\n\ndef mean(xs):\n    return sum(xs) / (len(xs) - 1)\n", "What does `iter(x) is x` tell you about x in Python? One sentence.", "Write a one-line Python function that reverses a string."]
p = [s.chat(sysm, u) for u in q]; t0 = time.time(); texts, npr, nnew = s.generate(p[:1], 96); t1 = time.time() - t0; t0 = time.time(); texts4, npr4, nnew4 = s.generate(p, 96); t4 = time.time() - t0
out["inference"] = {"single": {"seconds": round(t1, 2), "new_tokens": nnew[0], "tokens_per_second": round(nnew[0] / t1, 1)}, "batch_of_4": {"seconds": round(t4, 2), "new_tokens": sum(nnew4), "tokens_per_second": round(sum(nnew4) / t4, 1)}, "sample": texts4[1][:300]}
s.add_adapter(seed=1); out["adapter"] = {"layers": len(s.lora), "trainable_parameters": sum(x.numel() for x in s.adapter_params()), **s.adapter_meta}
for x in s.adapter_params(): x.requires_grad_(True)
opt = torch.optim.AdamW(s.adapter_params(), lr=2e-4); target = ["def mean(xs):\n    return sum(xs) / len(xs)\n"]; losses = []; t0 = time.time(); toks = 0
for i in range(4):
    l, n = s.loss(p[1:2], target); opt.zero_grad(); l.backward(); opt.step(); losses.append(round(float(l), 4)); toks += n
out["adapter_update"] = {"losses_over_4_updates": losses, "seconds_per_update": round((time.time() - t0) / 4, 2), "tokens_per_update": toks // 4}
os.makedirs("artifacts/v07", exist_ok=True); h = s.save_adapter("artifacts/v07/smoke_adapter.safetensors", {"note": "smoke test"}); a, _, _ = s.generate(p[1:2], 48)
del s; torch.mps.empty_cache() if torch.backends.mps.is_available() else None
s2 = Student(); b0, _, _ = s2.generate(p[1:2], 48); meta = s2.load_adapter("artifacts/v07/smoke_adapter.safetensors"); b, _, _ = s2.generate(p[1:2], 48); s2.set_adapter_enabled(False); b1, _, _ = s2.generate(p[1:2], 48)
out["reload"] = {"adapter_sha256": h, "same_output_after_reload": a == b, "base_output_restored_when_adapter_off": b0 == b1, "adapter_changes_output": a != b0, "meta": meta}
out["pin"] = {k: PIN[k] for k in ("repo", "revision")}; out["pin"]["model_sha256"] = PIN["files"]["model.safetensors"]["sha256"]
json.dump(out, open("results/v07/SMOKE_MODEL.json", "w"), indent=1); print(json.dumps(out, indent=1))
