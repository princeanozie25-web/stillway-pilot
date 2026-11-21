"""Post-hoc quantisation of a CONTINUOUS planner (the Koul-style comparison).

    python -m stillway.posthoc runs/cont_s1

Takes a planner trained with continuous memory, clusters each memory slot into
32 codes with k-means on training-family runs, and saves a discrete planner
runs/cont_s1_posthoc that was never trained with a discrete bottleneck.
"""
from __future__ import annotations

import json
import os
import sys

import torch

from .fixtures import families, layouts_of
from .model import Config, Core, load_checkpoint, save_checkpoint
from .vworld import PROFILES, VWorld
from .world import N_STAGES, STAGE_ACTIONS


@torch.no_grad()
def collect(model: Core, n: int, seed: int) -> torch.Tensor:
    gen = torch.Generator().manual_seed(seed)
    w = VWorld(torch.tensor(layouts_of(families("train"))), n, PROFILES["dynamic"], gen)
    mem = torch.zeros(n, model.cfg.n_slots * model.cfg.code_dim)
    zs = []
    for s in range(N_STAGES):
        obs = w.next_obs()
        h, logits, z_e = model.step(mem, obs)
        if s in STAGE_ACTIONS:
            w.apply(w.env_action(None, w.valid_mask()))
        zs.append(z_e)
        mem = z_e.reshape(n, -1)
    return torch.cat(zs, 0)                     # (6n, S, D)


def kmeans(x: torch.Tensor, k: int, iters: int, gen: torch.Generator) -> torch.Tensor:
    c = x[torch.randperm(x.shape[0], generator=gen)[:1]]
    for _ in range(k - 1):                      # k-means++ style spread start
        d = torch.cdist(x, c).min(1).values
        c = torch.cat([c, x[d.argmax()][None]])
    for _ in range(iters):
        a = torch.cdist(x, c).argmin(1)
        for j in range(k):
            m = a == j
            if m.any():
                c[j] = x[m].mean(0)
    return c


def main():
    run = sys.argv[1].rstrip("/")
    torch.manual_seed(0)
    gen = torch.Generator().manual_seed(0)
    src = load_checkpoint(os.path.join(run, "checkpoint.pt"))
    assert src.cfg.quantizer == "none"
    z = collect(src, 8000, 123)
    cfg = Config(**{**src.cfg.__dict__, "quantizer": "vq"})
    dst = Core(cfg)
    dst.load_state_dict(src.state_dict())
    for s in range(cfg.n_slots):
        dst.codebook[s] = kmeans(z[:, s].clone(), cfg.n_codes, 25, gen)
    dst.quant_on.fill_(1)
    dst.eval()
    out = run + "_posthoc"
    os.makedirs(out, exist_ok=True)
    sha = save_checkpoint(dst, os.path.join(out, "checkpoint.pt"), {"posthoc_of": run})
    man = json.load(open(os.path.join(run, "manifest.json")))
    man.update({"name": os.path.basename(out), "checkpoint_sha256": sha, "posthoc_of": os.path.basename(run),
                "note": "continuous planner, memory quantised after training by k-means (32 codes per slot); no discrete training"})
    json.dump(man, open(os.path.join(out, "manifest.json"), "w"), indent=1)
    print("saved", out, sha)


if __name__ == "__main__":
    main()
