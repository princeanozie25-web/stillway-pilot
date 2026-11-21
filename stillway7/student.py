"""The student: a pinned pretrained coding model, plus low-rank adapters written here (no adapter library).

Base weights are never changed.  An adapter is a set of low-rank additions (A, B) to chosen linear layers, saved as one
safetensors file with its settings in the metadata."""
import hashlib, json, math, os, time
import torch
from safetensors.torch import load_file, save_file

PIN = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results", "v07", "MODEL_PIN.json")))
TARGETS = ("q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj")


class LoRA(torch.nn.Module):
    def __init__(self, base, r, alpha):
        super().__init__(); self.base = base; self.r = r; self.scale = alpha / r; self.on = True
        self.A = torch.nn.Parameter(torch.zeros(r, base.in_features, dtype=base.weight.dtype, device=base.weight.device)); self.B = torch.nn.Parameter(torch.zeros(base.out_features, r, dtype=base.weight.dtype, device=base.weight.device))
    def forward(self, x):
        y = self.base(x)
        return y + (x @ self.A.T @ self.B.T) * self.scale if self.on else y


class Student:
    def __init__(self, device=None, dtype=torch.float32):
        from transformers import AutoModelForCausalLM, AutoTokenizer
        self.device = device or ("mps" if torch.backends.mps.is_available() else "cpu"); self.dtype = dtype
        self.tok = AutoTokenizer.from_pretrained(PIN["path"]); self.tok.padding_side = "left"
        self.model = AutoModelForCausalLM.from_pretrained(PIN["path"], dtype=dtype).to(self.device).eval()
        for p in self.model.parameters(): p.requires_grad_(False)
        self.lora = {}; self.adapter_meta = None

    # ---- adapters
    def add_adapter(self, r=16, alpha=32, targets=TARGETS, seed=0):
        assert not self.lora; g = torch.Generator().manual_seed(seed)
        for name, mod in list(self.model.named_modules()):
            for child_name, child in list(mod.named_children()):
                if child_name in targets and isinstance(child, torch.nn.Linear):
                    l = LoRA(child, r, alpha); l.A.data = (torch.randn(r, child.in_features, generator=g) / math.sqrt(child.in_features)).to(self.device, self.dtype); setattr(mod, child_name, l); self.lora[f"{name}.{child_name}"] = l
        self.adapter_meta = {"r": r, "alpha": alpha, "targets": list(targets), "seed": seed}; return self

    def adapter_params(self): return [p for l in self.lora.values() for p in (l.A, l.B)]
    def set_adapter_enabled(self, on):
        for l in self.lora.values(): l.on = on

    def save_adapter(self, path, extra=None):
        t = {}
        for k, l in self.lora.items(): t[k + ".A"] = l.A.detach().cpu().contiguous(); t[k + ".B"] = l.B.detach().cpu().contiguous()
        meta = dict(self.adapter_meta, base_repo=PIN["repo"], base_revision=PIN["revision"], base_sha256=PIN["files"]["model.safetensors"]["sha256"], **(extra or {}))
        save_file(t, path, metadata={"stillway": json.dumps(meta)}); return hashlib.sha256(open(path, "rb").read()).hexdigest()

    def load_adapter(self, path):
        from safetensors import safe_open
        with safe_open(path, "pt") as f: meta = json.loads(f.metadata()["stillway"])
        assert meta["base_sha256"] == PIN["files"]["model.safetensors"]["sha256"], "adapter was trained on a different base"
        if not self.lora: self.add_adapter(meta["r"], meta["alpha"], tuple(meta["targets"]), meta["seed"])
        t = load_file(path)
        for k, l in self.lora.items(): l.A.data = t[k + ".A"].to(self.device, self.dtype); l.B.data = t[k + ".B"].to(self.device, self.dtype)
        self.set_adapter_enabled(True); return meta

    # ---- text in, text out
    def chat(self, system, user): return self.tok.apply_chat_template([{"role": "system", "content": system}, {"role": "user", "content": user}], tokenize=False, add_generation_prompt=True)

    @torch.no_grad()
    def generate(self, prompts, max_new_tokens, max_prompt_tokens=3072):
        """Greedy decoding of a batch of full prompt strings.  Returns (texts, prompt token counts, new token counts)."""
        ids = [self.tok(p, add_special_tokens=False)["input_ids"][-max_prompt_tokens:] for p in prompts]; n = max(map(len, ids)); pad = self.tok.pad_token_id if self.tok.pad_token_id is not None else self.tok.eos_token_id
        x = torch.tensor([[pad] * (n - len(i)) + i for i in ids], device=self.device); m = torch.tensor([[0] * (n - len(i)) + [1] * len(i) for i in ids], device=self.device)
        out = self.model.generate(input_ids=x, attention_mask=m, max_new_tokens=max_new_tokens, do_sample=False, temperature=None, top_p=None, top_k=None, repetition_penalty=1.0, pad_token_id=pad)
        new = out[:, n:]; texts = self.tok.batch_decode(new, skip_special_tokens=True); stops = {self.tok.eos_token_id, pad, self.tok.convert_tokens_to_ids("<|im_end|>")}
        counts = []
        for row in new.tolist():
            c = 0
            for t in row:
                c += 1
                if t in stops: break
            counts.append(c)
        return texts, [len(i) for i in ids], counts

    def loss(self, prompts, targets, max_tokens=3072):
        """Mean next-token loss on the target part only.  Returns (loss, tokens processed)."""
        rows = []
        for p, t in zip(prompts, targets):
            a = self.tok(p, add_special_tokens=False)["input_ids"]; b = self.tok(t + "<|im_end|>", add_special_tokens=False)["input_ids"]; a = a[-(max_tokens - len(b)):]; rows.append((a, b))
        n = max(len(a) + len(b) for a, b in rows); pad = self.tok.pad_token_id if self.tok.pad_token_id is not None else self.tok.eos_token_id
        x = torch.tensor([[pad] * (n - len(a) - len(b)) + a + b for a, b in rows], device=self.device); m = torch.tensor([[0] * (n - len(a) - len(b)) + [1] * (len(a) + len(b)) for a, b in rows], device=self.device)
        y = torch.tensor([[-100] * (n - len(b)) + b for a, b in rows], device=self.device)
        h = self.model.model(input_ids=x, attention_mask=m).last_hidden_state[:, :-1]; keep = y[:, 1:] != -100          # logits only where a target token is predicted
        l = torch.nn.functional.cross_entropy(self.model.lm_head(h[keep]).float(), y[:, 1:][keep])
        return l, int(m.sum())
