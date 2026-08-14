#!/usr/bin/env python
"""v0.3 plots: T8 posterior + scale tension."""
from __future__ import annotations
import sys
import json
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from channels_v03 import sigma_m_at_v, V_REF

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

RESULTS_DIR = Path("/home/lamkuenai/dm-sidm-pipeline/v0.3-prelim/data/results")
PLOTS_DIR = Path("/home/lamkuenai/dm-sidm-pipeline/v0.3-prelim/plots")
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

samples_path = RESULTS_DIR / "t8_v03_posterior_samples.npz"
d = np.load(samples_path)
log_sm_samples = d["log_sigma_m_0"]
a_samples = d["a"]
weights = d["weights"]
print(f"[plot] loaded {len(log_sm_samples)} T8 samples")

if not HAS_MPL:
    sys.exit("[plot] no matplotlib")

# ---- 1D marginal posteriors ----
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

ax = axes[0]
hist, edges = np.histogram(log_sm_samples, bins=30, weights=weights)
centers = 0.5*(edges[:-1]+edges[1:])
ax.fill_between(centers, hist, alpha=0.4, color="steelblue")
ax.plot(centers, hist, color="darkblue", lw=2)
p16 = np.percentile(log_sm_samples, 16)
p50 = np.percentile(log_sm_samples, 50)
p84 = np.percentile(log_sm_samples, 84)
ax.axvline(p50, color="red", ls="--", lw=2, label=f"median={p50:.2f}")
ax.axvspan(p16, p84, alpha=0.15, color="red", label="68% CI")
ax.set_xlabel("log10(sigma/m)_0 [cm^2/g, at v=100 km/s]", fontsize=11)
ax.set_ylabel("posterior density", fontsize=11)
ax.set_title("v0.3 T8: 1D marginalized posterior on sigma/m")
ax.legend(fontsize=10)
ax.grid(alpha=0.3)

ax = axes[1]
hist_a, edges_a = np.histogram(a_samples, bins=30, weights=weights)
centers_a = 0.5*(edges_a[:-1]+edges_a[1:])
ax.fill_between(centers_a, hist_a, alpha=0.4, color="darkorange")
ax.plot(centers_a, hist_a, color="darkred", lw=2)
a_p16 = np.percentile(a_samples, 16)
a_p50 = np.percentile(a_samples, 50)
a_p84 = np.percentile(a_samples, 84)
ax.axvline(a_p50, color="red", ls="--", lw=2, label=f"median={a_p50:.2f}")
ax.axvspan(a_p16, a_p84, alpha=0.15, color="red", label="68% CI")
ax.set_xlabel("a (velocity power-law index)", fontsize=11)
ax.set_ylabel("posterior density", fontsize=11)
ax.set_title("v0.3 T8: 1D marginalized posterior on a")
ax.legend(fontsize=10)
ax.grid(alpha=0.3)

plt.tight_layout()
out_path = PLOTS_DIR / "t8_v03_marginal.png"
plt.savefig(out_path, dpi=120, bbox_inches="tight")
print(f"[plot] saved {out_path}")

# ---- Scale tension plot (v0.3) ----
fig2, ax2 = plt.subplots(figsize=(9, 6))
v_range = np.logspace(np.log10(3), np.log10(5000), 100)
sm_at_v = np.zeros((min(2000, len(log_sm_samples)), len(v_range)))
for i, (lsm, a) in enumerate(zip(log_sm_samples[:2000], a_samples[:2000])):
    sm_at_v[i] = 10**lsm * (v_range / V_REF)**(-a)
sm_p16 = np.percentile(sm_at_v, 16, axis=0)
sm_p50 = np.percentile(sm_at_v, 50, axis=0)
sm_p84 = np.percentile(sm_at_v, 84, axis=0)

ax2.fill_between(v_range, sm_p16, sm_p84, alpha=0.3, color="steelblue", label="v0.3 T8: 68% CI")
ax2.plot(v_range, sm_p50, color="darkblue", lw=2.5, label="v0.3 T8: median")
ax2.axhline(0.5, color="red", ls="--", lw=1.5, label="Cha+ 2025 Bullet Cluster 95% CL\n(sigma/m < 0.5 cm^2/g)")

# Published peaks (s
ax2.scatter([10], [10**0.92], color="green", s=100, marker="o", label="Sanchez-Almeida+25 best", zorder=10)
ax2.scatter([30], [0.1], color="purple", s=80, marker="s", label="Horigome+25 small peak", zorder=10)
ax2.scatter([30], [10], color="purple", s=80, marker="^", label="Horigome+25 large peak", zorder=10)

ax2.set_xscale("log")
ax2.set_yscale("log")
ax2.set_xlabel("velocity scale v [km/s]", fontsize=12)
ax2.set_ylabel("sigma/m [cm^2/g]", fontsize=12)
ax2.set_title("v0.3 T8: SIDM cross-section vs velocity scale\n5-channel joint (SPARC + dSph + UFD + Bullet)", fontsize=13)
ax2.legend(loc="upper right", fontsize=9)
ax2.grid(alpha=0.3, which="both")
ax2.set_xlim(3, 5000)
ax2.set_ylim(0.01, 200)

plt.tight_layout()
out_path2 = PLOTS_DIR / "t8_v03_scale_tension.png"
plt.savefig(out_path2, dpi=120, bbox_inches="tight")
print(f"[plot] saved {out_path2}")

# Copy to Windows side
import shutil
for src in PLOTS_DIR.glob("*.png"):
    dst = Path("/mnt/c/Users/lamkuenai/projects/dm-sidm-pipeline/v0.3-prelim/plots") / src.name
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(src, dst)
    print(f"[plot] copied to {dst}")
print("[plot] done")