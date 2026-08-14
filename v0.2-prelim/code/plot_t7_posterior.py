#!/usr/bin/env python
"""
Generate plots for v0.2-prelim:
    1. Joint 4-channel posterior heatmap (log_sigma_m vs a)
    2. 1D marginalized posterior on sigma/m
    3. Effective cross-section vs velocity scale (scale-tension plot)
"""
from __future__ import annotations
import sys
import json
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sidm_velocity_dependent import loglike_joint_4channel, V_REF

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

RESULTS_DIR = Path("/home/lamkuenai/dm-sidm-pipeline/v0.2-prelim/data/results")
PLOTS_DIR = Path("/home/lamkuenai/dm-sidm-pipeline/v0.2-prelim/plots")
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

# Load T7 posterior samples
samples_path = RESULTS_DIR / "t7_joint_posterior_samples.npz"
if samples_path.exists():
    d = np.load(samples_path)
    log_sm_samples = d["log_sigma_m_0"]
    a_samples = d["a"]
    weights = d["weights"]
    print(f"[plot] loaded {len(log_sm_samples)} posterior samples from T7")
else:
    print(f"[plot] missing {samples_path}")
    sys.exit(1)

if not HAS_MPL:
    print("[plot] matplotlib not available; skipping")
    sys.exit(0)

# ---- Plot 1: 2D posterior heatmap ----
fig, axes = plt.subplots(2, 2, figsize=(11, 9))

ax = axes[0, 0]
# Compute 2D histogram
hist, xedges, yedges = np.histogram2d(log_sm_samples, a_samples, bins=40, weights=weights)
hist_norm = hist / hist.max()
X, Y = np.meshgrid(0.5*(xedges[:-1]+xedges[1:]), 0.5*(yedges[:-1]+yedges[1:]))
im = ax.pcolormesh(X, Y, hist_norm.T, cmap="viridis", shading="auto")
ax.set_xlabel("log10(sigma/m)_0 [cm^2/g at v_ref=100 km/s]")
ax.set_ylabel("a (velocity power-law index)")
ax.set_title("T7: Joint 4-channel posterior (Horigome+25 + Sanchez-Almeida+25 + Cha+25)")
plt.colorbar(im, ax=ax, label="normalized posterior")

# ---- Plot 2: 1D marginalized log sigma/m ----
ax = axes[0, 1]
hist, edges = np.histogram(log_sm_samples, bins=40, weights=weights)
centers = 0.5*(edges[:-1]+edges[1:])
ax.fill_between(centers, hist, alpha=0.5, color="steelblue")
ax.plot(centers, hist, color="darkblue", lw=1.5)
# Mark MAP, median
p50 = np.percentile(log_sm_samples, 50)
p16 = np.percentile(log_sm_samples, 16)
p84 = np.percentile(log_sm_samples, 84)
ax.axvline(p50, color="red", ls="--", lw=2, label=f"median={p50:.2f}")
ax.axvspan(p16, p84, alpha=0.15, color="red", label="68% CI")
ax.set_xlabel("log10(sigma/m)_0")
ax.set_ylabel("marginal posterior density")
ax.set_title("1D marginalized posterior (v-dep)")
ax.legend()
ax.grid(alpha=0.3)

# ---- Plot 3: 1D marginalized a ----
ax = axes[1, 0]
hist_a, edges_a = np.histogram(a_samples, bins=40, weights=weights)
centers_a = 0.5*(edges_a[:-1]+edges_a[1:])
ax.fill_between(centers_a, hist_a, alpha=0.5, color="darkorange")
ax.plot(centers_a, hist_a, color="darkred", lw=1.5)
a_p50 = np.percentile(a_samples, 50)
a_p16 = np.percentile(a_samples, 16)
a_p84 = np.percentile(a_samples, 84)
ax.axvline(a_p50, color="red", ls="--", lw=2, label=f"median={a_p50:.2f}")
ax.axvspan(a_p16, a_p84, alpha=0.15, color="red", label="68% CI")
ax.set_xlabel("a (velocity power-law index)")
ax.set_ylabel("marginal posterior density")
ax.set_title("1D marginalized posterior (a)")
ax.legend()
ax.grid(alpha=0.3)

# ---- Plot 4: Scale-tension plot (sigma/m vs velocity) ----
ax = axes[1, 1]
v_range = np.logspace(np.log10(5), np.log10(3000), 100)
# Use posterior samples to draw uncertainty band on sigma/m(v)
sm_at_v = np.zeros((len(log_sm_samples), len(v_range)))
for i, (lsm, a) in enumerate(zip(log_sm_samples[:5000], a_samples[:5000])):
    sm_at_v[i] = 10**lsm * (v_range / V_REF)**(-a)
sm_p16 = np.percentile(sm_at_v, 16, axis=0)
sm_p50 = np.percentile(sm_at_v, 50, axis=0)
sm_p84 = np.percentile(sm_at_v, 84, axis=0)
ax.fill_between(v_range, sm_p16, sm_p84, alpha=0.3, color="steelblue", label="68% CI")
ax.plot(v_range, sm_p50, color="darkblue", lw=2, label="median")
# Mark observation scales
ax.axvline(10, color="green", ls=":", lw=1.5, label="UFD v=10 km/s")
ax.axvline(100, color="orange", ls=":", lw=1.5, label="Galaxy v=100 km/s")
ax.axvline(1500, color="red", ls=":", lw=1.5, label="Bullet Cluster v=1500 km/s")
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlabel("v_max [km/s]")
ax.set_ylabel("sigma/m [cm^2/g]")
ax.set_title("Scale-tension: cross-section vs velocity scale")
ax.legend(loc="lower left", fontsize=8)
ax.grid(alpha=0.3, which="both")

plt.suptitle("v0.2-prelim: T7 joint 4-channel SIDM posterior", fontsize=14)
plt.tight_layout()
out_path = PLOTS_DIR / "t7_joint_posterior.png"
plt.savefig(out_path, dpi=120, bbox_inches="tight")
print(f"[plot] saved {out_path}")

# ---- Standalone scale-tension plot (publication-quality) ----
fig2, ax2 = plt.subplots(figsize=(8, 6))
ax2.fill_between(v_range, sm_p16, sm_p84, alpha=0.3, color="steelblue", label="v0.2 T7: 68% CI")
ax2.plot(v_range, sm_p50, color="darkblue", lw=2.5, label="v0.2 T7: median")
# Published constraints
ax2.axhline(0.5, color="red", ls="--", lw=1.5,
            label="Cha+ 2025 Bullet Cluster limit\n(sigma/m < 0.5 cm^2/g)")
ax2.fill_between([5, 30], [0.5]*2, [200]*2, color="red", alpha=0.1,
                label="excluded by clusters")
# Published preferred regions
ax2.fill_between([5, 50], [0.05]*2, [10]*2, color="green", alpha=0.15,
                label="Sanchez-Almeida+25 UFD allowed\n(log(sigma/m)=0.92 +/- 1.37)")
ax2.fill_between([50, 300], [0.05]*2, [10]*2, color="yellow", alpha=0.15,
                label="Horigome+25 dSph bimodal\n(log(sigma/m)~-1 or ~+1)")
# Observation scales
ax2.scatter([10], [10**0.92], color="green", s=80, marker="o",
            label="Sanchez-Almeida+25 best", zorder=10)
ax2.scatter([100], [10**(-1)], color="purple", s=80, marker="s",
            label="Horigome+25 small-SIDM peak", zorder=10)
ax2.scatter([100], [10**(+1)], color="purple", s=80, marker="^",
            label="Horigome+25 large-SIDM peak", zorder=10)
ax2.set_xscale("log")
ax2.set_yscale("log")
ax2.set_xlabel("velocity scale v [km/s]", fontsize=12)
ax2.set_ylabel("sigma/m [cm^2/g]", fontsize=12)
ax2.set_title("SIDM cross-section vs velocity scale\n(SPARC + dSph + UFD + Bullet Cluster)", fontsize=13)
ax2.legend(loc="upper right", fontsize=9)
ax2.grid(alpha=0.3, which="both")
ax2.set_xlim(3, 5000)
ax2.set_ylim(0.005, 500)
out_path2 = PLOTS_DIR / "scale_tension.png"
plt.tight_layout()
plt.savefig(out_path2, dpi=120, bbox_inches="tight")
print(f"[plot] saved {out_path2}")
print("[plot] done")