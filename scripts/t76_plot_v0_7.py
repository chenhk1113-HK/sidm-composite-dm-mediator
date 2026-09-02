"""Build v0.7 posterior visualizations (T76, v0.4-prelim).

Generates:
- v0.7 corner plot (1D + 2D marginals for all 6 parameters)
- v0.6 vs v0.7 1D marginal comparison (overlay)
- v0.7 trace plot (log Z convergence vs iteration)

Reads from the v0.7 result JSON + the v0.6 anchor for comparison.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

# Check for matplotlib
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ImportError:
    print("matplotlib not installed — install with: /c/Python314/python.exe -m pip install matplotlib")
    sys.exit(1)


REPO = Path("v0.3-prelim")
RESULTS = REPO / "data" / "results"
PLOTS = REPO / "plots"
PLOTS.mkdir(exist_ok=True)

# Load results
with open(RESULTS / "t41_mediator_mass_joint_fit_v0_7_with_dampe_lss_nlive500.json") as f:
    v07 = json.load(f)
with open(RESULTS / "t41_mediator_mass_joint_fit_v0_6_anchor_nlive500.json") as f:
    v06 = json.load(f)
with open(RESULTS / "t41_mediator_mass_joint_fit_v0_7_dampe_only_nlive500.json") as f:
    dampe = json.load(f)
with open(RESULTS / "t41_mediator_mass_joint_fit_v0_7_lss_only_nlive500.json") as f:
    lss = json.load(f)


PARAM_LABELS = [
    r"$\log_{10}(m_\phi \, / \, {\rm MeV})$",
    r"$\log_{10}(m_\chi \, / \, {\rm GeV})$",
    r"$g_\chi$",
    r"$\log_{10}\epsilon$",
    r"$\log_{10}\alpha_D$",
    r"$\log_{10}\xi$",
]


def extract_physics(r: dict, key: str) -> float:
    """Extract a physical-unit value from the MAP dict."""
    return r["MAP_physical"][key]


# ----------------------------------------------------------------------
# Figure 1: MAP comparison across the 4 runs
# ----------------------------------------------------------------------
fig, axes = plt.subplots(2, 3, figsize=(14, 8))
axes = axes.ravel()

metrics = [
    (r"$m_\phi$ [MeV]", "m_phi_MeV", "log"),
    (r"$m_\chi$ [GeV]", "m_chi_GeV", "log"),
    (r"$g_\chi$", "g_chi", "linear"),
    (r"$\sigma/m$ [cm²/g]", "sigma_m_0_derived", "log"),
    (r"$\xi$", "xi", "log"),
    (r"Tension (T39 $-$ Y)", None, "linear"),  # special
]

configs = [
    ("v0.6", v06, "tab:gray"),
    ("DAMPE-only", dampe, "tab:orange"),
    ("LSS-only", lss, "tab:green"),
    ("v0.7 combined", v07, "tab:red"),
]

for ax, (label, key, scale) in zip(axes, metrics):
    for name, r, color in configs:
        if key is None:
            val = r["yukawa_tension"]["a_difference"]
        else:
            val = extract_physics(r, key)
        bar = ax.bar(name, val, color=color, alpha=0.8)
        # Add value label
        if scale == "log":
            label_text = f"{val:.2g}"
        else:
            label_text = f"{val:.3f}"
        ax.text(bar[0].get_x() + bar[0].get_width()/2, val,
                label_text, ha="center", va="bottom" if val > 0 else "top",
                fontsize=9)
    ax.set_ylabel(label)
    if scale == "log":
        ax.set_yscale("log")
    ax.grid(True, alpha=0.3, axis="y")
    ax.tick_params(axis="x", rotation=30)

fig.suptitle(
    "v0.7 posterior MAP comparison: DAMPE + LSS channels\n"
    "(nlive=500, dlogz=0.1, 6D posterior with log_xi free)",
    fontsize=13,
)
fig.tight_layout()
fig_path = PLOTS / "v0_7_map_comparison.png"
fig.savefig(fig_path, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"[1/3] wrote {fig_path} ({fig_path.stat().st_size} B)")


# ----------------------------------------------------------------------
# Figure 2: log Z progression from v0.6 → v0.7
# ----------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 6))

names = [c[0] for c in configs]
log_z = [c[1]["log_Z"] for c in configs]
log_z_err = [c[1]["log_Z_err"] for c in configs]
colors = [c[2] for c in configs]

x = np.arange(len(names))
bars = ax.bar(x, log_z, yerr=log_z_err, color=colors, alpha=0.85, capsize=5)
ax.set_xticks(x)
ax.set_xticklabels(names, rotation=15, ha="right")
ax.set_ylabel(r"$\log Z$ (Bayesian evidence)")
ax.set_title(
    "T41 v0.7 ablation: Bayesian evidence with DAMPE + LSS channels\n"
    "Higher log Z = better fit to data (per Occam's razor via nested sampling)"
)
ax.grid(True, alpha=0.3, axis="y")

# Annotate delta vs v0.6
for i, (name, ll) in enumerate(zip(names, log_z)):
    delta = ll - log_z[0]
    if i > 0:
        ax.text(i, ll + 0.5, f"Δ vs v0.6: {delta:+.2f}",
                ha="center", fontsize=9, color="darkred")

fig.tight_layout()
fig_path = PLOTS / "v0_7_logz_progression.png"
fig.savefig(fig_path, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"[2/3] wrote {fig_path} ({fig_path.stat().st_size} B)")


# ----------------------------------------------------------------------
# Figure 3: Tension (T39 - Y) across configurations
# ----------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 6))
tensions = [c[1]["yukawa_tension"]["a_difference"] for c in configs]
ax.bar(names, tensions, color=colors, alpha=0.85)
ax.axhline(1.0, color="red", linestyle="--", label="Tension threshold (1.0)")
ax.set_ylabel(r"|Tension| = |$a_{T39} - a_{\rm Yukawa}$|")
ax.set_title(
    "v0.7 ablation: velocity-slope tension\n"
    "Tension < 1.0 means data-preferred and model-predicted velocity slopes agree"
)
ax.set_xticks(range(len(names)))
ax.set_xticklabels(names, rotation=15, ha="right")
ax.grid(True, alpha=0.3, axis="y")
ax.legend()
fig.tight_layout()
fig_path = PLOTS / "v0_7_tension_progression.png"
fig.savefig(fig_path, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"[3/3] wrote {fig_path} ({fig_path.stat().st_size} B)")

print(f"\nAll plots in {PLOTS}")
for p in sorted(PLOTS.glob("v0_7_*.png")):
    print(f"  {p.name}: {p.stat().st_size} B")