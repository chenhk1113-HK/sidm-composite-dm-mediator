"""Generate the sigma/m(v) figure for the paper.

Shows sigma/m(v) on a log-log scale with both:
  - v_target inputs (vertical dashed lines, kinematic parameter)
  - v_peak actual locations (where sigma/m actually peaks)
  - observational constraint anchors (Cloud-9, JVAS, SPARC, dSph)

Output: v0.3-prelim/docs/figures/sigma_m_v_phase44.png
"""
import json
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]  # scripts/plot_sigma_m_v.py -> repo/
CODE_DIR = REPO / "v0.3-prelim" / "code"
RESULTS_DIR = REPO / "v0.3-prelim" / "data" / "results"
FIG_DIR = REPO / "v0.3-prelim" / "docs" / "figures"


def main():
    sys.path.insert(0, str(CODE_DIR))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    from phase44_joint_fit import sigma_m_at_v

    FIG_DIR.mkdir(parents=True, exist_ok=True)

    with open(RESULTS_DIR / "phase44_joint_fit.json", encoding="utf-8") as f:
        d = json.load(f)
    p = d["best_params"]
    m_chi, sigma_0, a_slope = p[0], p[1], p[2]
    v_targets = p[3:7]
    sigma_peaks = p[7:11]
    gamma_fracs = p[11:15]

    m_chi_eV = m_chi * 1e9
    resonances = []
    for i, (v, sp, gf) in enumerate(zip(v_targets, sigma_peaks, gamma_fracs)):
        v_cm_s = v * 1e5
        E_R_eV = 0.5 * m_chi_eV * (v_cm_s / 2.998e10) ** 2
        resonances.append({
            "name": f"r{i+1}",
            "E_R_eV": E_R_eV,
            "Gamma_eV": gf * E_R_eV,
            "sigma_peak_cm2_per_g": sp,
        })

    # Evaluate sigma/m on a fine grid
    vs = np.linspace(5, 1500, 3000)
    vals = np.array([sigma_m_at_v(v, m_chi, resonances, sigma_0, a_slope) for v in vs])

    # Find actual peak location for each resonance
    v_peaks = []
    sigma_at_peaks = []
    for vt in v_targets:
        mask = (vs >= 0.3 * vt) & (vs <= 3.0 * vt)
        if mask.sum() == 0:
            v_peaks.append(vt)
            sigma_at_peaks.append(sigma_m_at_v(vt, m_chi, resonances, sigma_0, a_slope))
            continue
        idx = np.argmax(vals[mask])
        sub_v = vs[mask]
        v_peaks.append(sub_v[idx])
        sigma_at_peaks.append(vals[mask][idx])

    # Plot
    fig, ax = plt.subplots(figsize=(10, 6))

    # sigma/m curve
    ax.loglog(vs, vals, "k-", linewidth=2, label=r"$\sigma/m(v)$ (Phase 44 free fit)")

    # v_targets (kinematic input) — dashed vertical lines
    for i, (vt, sp) in enumerate(zip(v_targets, sigma_peaks)):
        ax.axvline(vt, color=f"C{i}", linestyle="--", alpha=0.5,
                   label=f"$v_{{target,{i+1}}}$ = {vt:.0f} km/s" if i == 0 else None)
        ax.plot(vt, sp, "o", color=f"C{i}", markersize=8, alpha=0.5)

    # v_peaks (actual peak locations) — solid dots with annotation
    for i, (vp, sp) in enumerate(zip(v_peaks, sigma_at_peaks)):
        ax.plot(vp, sp, "*", color=f"C{i}", markersize=15,
                label=f"Peak {i+1} at $v_{{peak,{i+1}}}$ = {vp:.0f} km/s" if i == 0 else None)

    # Constraint anchors
    constraints = [
        ("Cloud-9 (target)", 28, 100, "green"),
        ("Cloud-9 (actual peak)", 41, 196, "darkgreen"),
        ("SPARC V_flat band", 100, 0.13, "blue"),
        ("JVAS (target)", 15, 100, "red"),
        ("JVAS (model)", 15, 4.2, "darkred"),
        ("dSph (Horigome+)", 30, 0.2, "purple"),
        ("dSph (model)", 30, 7.5, "magenta"),
    ]
    for label, v, sigma, color in constraints:
        ax.scatter(v, sigma, s=200, marker="x", color=color, linewidth=3, label=label)

    # Highlight Cloud-9 channel
    ax.axvspan(20, 50, alpha=0.1, color="green", label="Cloud-9 velocity range")
    # Highlight SPARC channel
    ax.axvspan(80, 120, alpha=0.1, color="blue", label="SPARC velocity range")

    ax.set_xlabel(r"velocity $v$ (km/s)", fontsize=12)
    ax.set_ylabel(r"$\sigma/m$ (cm$^2$/g)", fontsize=12)
    ax.set_title(r"Multi-resonance $\sigma/m(v)$ — Phase 44 free best fit", fontsize=13)
    ax.set_xlim(5, 1500)
    ax.set_ylim(1e-3, 1e3)
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(loc="upper right", fontsize=8, framealpha=0.9)

    # Annotation: explain v_target vs v_peak
    ax.text(50, 1e-5, r"$v_\mathrm{target}$ = kinematic input; "
            r"$v_\mathrm{peak}$ = where $\sigma/m$ actually peaks",
            fontsize=9, color="gray")

    plt.tight_layout()
    out_path = FIG_DIR / "sigma_m_v_phase44.png"
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"Saved: {out_path} ({out_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()