"""
v19_2_f_priority3_constraint_plot.py
SIDM composite-DM project - Priority 3: Quantitative exclusion plot in (alpha_D, m_A') plane.

Builds a log-log exclusion plot with BBN, CMB, SN1987A, Lyman-alpha, XENONnT/LZ
constraints overlaid, plus candidate points from the framework doc and the Phase-3
EXTENDED best fit.

Coupling convention (LOCKED, from constants.py):
    alpha_D = g^2 / (4*pi)            [Tulin-Yu 2013, Kaplinghat et al. 2016]
    kappa   = alpha_D * m_chi / m_A'  [s-wave bound-state threshold]

Lyman-alpha exclusion curve:
    Solved analytically from Born-approximation transfer cross section
    sigma_T = (g^4 m_chi^2) / (8 pi m_A^4) * L(s)^2
    where L(s) = ln(1 + 1/s) - 1/(1+s)
    and s = (m_chi v / (sqrt(2) m_A))^2
    With alpha_D = g^2/(4pi): g^4 = 16 pi^2 alpha_D^2
    Setting sigma/m(v=30 km/s) = 100 cm^2/g and solving for alpha_D(m_A')
    gives a straight line in log-log with slope 2.

References for the Born cross-section formula:
    Tulin, Yu, Zurek (2013), arXiv:1306.5010 Eq. (3)
    Kaplinghat, Tulin, Yu (2016), arXiv:1508.03339
    For a Coulomb-like Yukawa at v~30 km/s << m_A/m_chi, the Born result
    is the standard first-principles reference; deep-Sommerfeld enhancement
    can push sigma/m above the Born value by factors of ~10-100 at kappa>kappa_c.

Output:
    v0.3-prelim/docs/V19_2_F_PRIORITY3_CONSTRAINT_PLOT.pdf
    v0.3-prelim/docs/V19_2_F_PRIORITY3_CONSTRAINT_PLOT.png
    v0.3-prelim/data/results/v19_2_f_priority3_constraint_plot.json
    v0.3-prelim/docs/V19_2_F_PRIORITY3_CONSTRAINT_PLOT_REPORT.md
"""
from __future__ import annotations
import math
import sys
import json
from pathlib import Path

import numpy as np

# Use Agg backend BEFORE importing pyplot (no GUI on this Windows host)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

# Project root (constants.py lives there)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent  # code/ -> v0.3-prelim/ -> project root
sys.path.insert(0, str(_PROJECT_ROOT))
import constants

# Born helpers (REVIEWER-15 item 11: extracted)
from v19_2_f_priority3_born_helpers import (
    L_function, sigma_T_born_GeV2, sigma_m_born_cm2_g,
)


# ============================================================
# Born transfer cross section (analytical, s-wave)
# ============================================================
# Extracted to v19_2_f_priority3_born_helpers.py (REVIEWER-15 item 11).
# The functions L_function, sigma_T_born_GeV2, sigma_m_born_cm2_g
# are imported from there. See that module for derivation and references.


# ============================================================
# Lyman-alpha exclusion curve (analytical)
# ============================================================
#
# Setting sigma/m(v = 30 km/s) = 100 cm^2/g (Vogelsberger 2012 / Zavala 2013 limit),
# the Born formula inverts to:
#
#     alpha_D = sqrt(100 cm^2/g / [16 pi^2 m_chi^2 (hbarc)^2 / (8 pi m_A^4 m_chi(g))]) * 1/|L(s)|
#             = K / m_A^2 * 1/|L(s)|
#
# where K is a constant set so that at m_A' = 100 MeV, alpha_D gives exactly
# sigma/m = 100 cm^2/g. In log-log, alpha_D vs m_A' is a straight line of
# slope 2 (from the m_A^-4 dependence) plus a slow modulation from L(s).
#
# Below we compute the exclusion curve by direct inversion on a fine grid.

# Lyman-alpha exclusion curve (extracted)
from v19_2_f_priority3_lyman_alpha_helpers import lyman_alpha_alpha_D_curve


# ============================================================
# Candidate points
# ============================================================

CANDIDATES = [
    {
        "label": "Framework doc",
        "alpha_D": 6.8e-7,
        "m_A_prime_GeV": 200e-9,  # 200 eV
        "kappa": None,  # compute below
        "marker": "*",
        "color": "red",
        "ms": 18,
        "note": "alpha_chi=6.8e-7, m_A'=200 eV (per framework doc)",
    },
    {
        "label": "Phase-3 best fit (EXTENDED)",
        "alpha_D": 5.55e-6,
        "m_A_prime_GeV": 126e-6,  # 126 keV
        "kappa": None,
        "marker": "P",
        "color": "gold",
        "ms": 14,
        "note": "alpha_D=5.55e-6, m_A'=126 keV (dynesty closure)",
    },
    {
        "label": "Lattice ridge #1 (m_A'=3.5 eV, kappa~1e5)",
        "alpha_D": 2.97e-10,
        "m_A_prime_GeV": 3.5e-9,
        "kappa": None,
        "marker": "X",
        "color": "blue",
        "ms": 12,
        "note": "kappa~1e5 ridge point",
    },
    {
        "label": "Lattice ridge #2 (m_A'=12.3 eV, kappa~1e6)",
        "alpha_D": 4.12e-9,
        "m_A_prime_GeV": 12.3e-9,
        "kappa": None,
        "marker": "X",
        "color": "cyan",
        "ms": 12,
        "note": "kappa~1e6 ridge point",
    },
    {
        "label": "Lattice ridge #3 (m_A'=43.3 eV, kappa~1e7)",
        "alpha_D": 5.99e-8,
        "m_A_prime_GeV": 43.3e-9,
        "kappa": None,
        "marker": "X",
        "color": "magenta",
        "ms": 12,
        "note": "kappa~1e7 ridge point",
    },
]


# ============================================================
# Constraint evaluation
# ============================================================
#
# Each constraint returns a verdict for a given (alpha_D, m_A') point.
# "EXCLUDED" means the point is ruled out; "ALLOWED" means it survives;
# "MARGINAL" means it sits on the boundary; "NA" means no constraint applies.
#
# IMPORTANT: For BBN/CMB/SN1987A/XENONnT, the constraints are on the kinetic
# mixing epsilon (visible-decay dark photon), NOT on alpha_D directly. If the
# dark photon is INVISIBLE (no kinetic mixing), all those constraints vanish.
# We therefore report two verdicts per constraint: visible-decay and invisible.

def evaluate_constraints(alpha_D, m_A_prime_GeV):
    """
    Return a dict of constraint verdicts for the given point.

    Each constraint gives one verdict per scenario:
      - "visible": dark photon has kinetic mixing epsilon > ~1e-10 -> visible decay
      - "invisible": dark photon is stable / decays only to dark sector
    """
    m_A_eV = m_A_prime_GeV * 1e9
    out = {}

    # BBN: Delta N_eff < 0.30 (Planck 2018)
    # For dark photon with lifetime tau < 1 sec decaying to e+e-, Delta N_eff ~ 0.1-1.
    # Olive et al. 2019: epsilon < 1e-10 required for m_A' in [1 eV, 100 MeV].
    # If visible: m_A' < 1 MeV is EXCLUDED; m_A' > 1 MeV can be visible (decays fast).
    # Conservatively: m_A' in [1 eV, 100 MeV] with visible decay EXCLUDED.
    if m_A_eV < 1e6:  # < 1 MeV
        out["BBN"] = {"visible": "EXCLUDED", "invisible": "ALLOWED"}
    else:
        out["BBN"] = {"visible": "ALLOWED", "invisible": "ALLOWED"}

    # CMB: tau > 1e25 sec for m_A' in [1 MeV, 100 MeV] decaying to e+e-
    # Slatyer 2016, Poulin 2018. If visible decay at z ~ 1100 -> EXCLUDED.
    if 1e6 <= m_A_eV <= 1e8:  # 1 MeV - 100 MeV
        out["CMB"] = {"visible": "EXCLUDED", "invisible": "ALLOWED"}
    else:
        out["CMB"] = {"visible": "ALLOWED", "invisible": "ALLOWED"}

    # SN1987A: epsilon < 1e-5 to 1e-10 for m_A' in [1, 100] MeV (Caputo 2021)
    # Below production threshold (m_A' < ~1 MeV -> produced as dark photon),
    # constraint is weak. Above ~100 MeV, also weak (kinematic threshold).
    if 1e6 <= m_A_eV <= 1e8:  # 1 MeV - 100 MeV
        out["SN1987A"] = {"visible": "EXCLUDED", "invisible": "ALLOWED"}
    else:
        out["SN1987A"] = {"visible": "ALLOWED", "invisible": "ALLOWED"}

    # Lyman-alpha: sigma/m(v~30 km/s) > 100 cm^2/g -> EXCLUDED
    # Vogelsberger 2012, Zavala 2013.
    sig_m_lyman = sigma_m_born_cm2_g(alpha_D, constants.M_CHI_GEV,
                                       m_A_prime_GeV, v_kms=30.0)
    if sig_m_lyman > 100.0:
        out["Lyman-alpha"] = {"visible": "EXCLUDED", "invisible": "EXCLUDED"}
    elif sig_m_lyman > 50.0:
        out["Lyman-alpha"] = {"visible": "MARGINAL", "invisible": "MARGINAL"}
    else:
        out["Lyman-alpha"] = {"visible": "ALLOWED", "invisible": "ALLOWED"}
    out["Lyman-alpha_value_cm2_g"] = sig_m_lyman

    # XENONnT / LZ direct detection: sigma_e < 1e-40 cm^2 for m_DM in [100 MeV, 10 GeV]
    # -> epsilon < 1e-5 for m_A' = 1 MeV. Same physical region as SN1987A.
    if 1e6 <= m_A_eV <= 1e8:  # 1 MeV - 100 MeV
        out["XENONnT/LZ"] = {"visible": "EXCLUDED", "invisible": "ALLOWED"}
    else:
        out["XENONnT/LZ"] = {"visible": "ALLOWED", "invisible": "ALLOWED"}

    return out


# ============================================================
# Main
# ============================================================

def main():
    print("=" * 72)
    print("v19.2-F Priority 3: Constraint Intersection Exclusion Plot")
    print("=" * 72)
    print()
    print("Plot shows (alpha_D, m_A') parameter space with all quantitative")
    print("exclusion curves overlaid. Candidate points from the framework doc")
    print("and the Phase-3 EXTENDED best fit are marked and labeled.")
    print()
    print(f"Coupling convention (LOCKED): alpha_D = g^2 / (4 pi)")
    print(f"  kappa = alpha_D * m_chi / m_A' (from constants.compute_kappa)")
    print(f"  kappa_c = {constants.KAPPA_C_ANALYTIC}")
    print()

    # ---------- Axes ----------
    m_ap_min_GeV = 1e-9   # 1 eV
    m_ap_max_GeV = 1e3    # 1 TeV
    alpha_D_min = 1e-12
    alpha_D_max = 1e-2

    # Fine log grid for plotting continuous curves
    m_ap_grid = np.logspace(np.log10(m_ap_min_GeV), np.log10(m_ap_max_GeV), 600)

    # ---------- Lyman-alpha exclusion curve ----------
    # Solve sigma/m(v=30 km/s) = 100 cm^2/g for alpha_D(m_A')
    lyman_alpha_curve = lyman_alpha_alpha_D_curve(m_ap_grid, v_kms=30.0,
                                                   sigma_m_target=100.0,
                                                   m_chi_GeV=constants.M_CHI_GEV)
    # Also draw a 50 cm^2/g marginal curve
    lyman_alpha_marginal = lyman_alpha_alpha_D_curve(m_ap_grid, v_kms=30.0,
                                                      sigma_m_target=50.0,
                                                      m_chi_GeV=constants.M_CHI_GEV)

    # ---------- Compute kappa = alpha_D * m_chi / m_A' for the kappa_c line ----------
    # The kappa = kappa_c line in (alpha_D, m_A') plane:
    # alpha_D = kappa_c * m_A' / m_chi
    kappa_c = constants.KAPPA_C_ANALYTIC
    alpha_D_kappa_c_line = kappa_c * m_ap_grid / constants.M_CHI_GEV
    # Clip to axes range
    kappa_c_visible = (alpha_D_kappa_c_line >= alpha_D_min) & (alpha_D_kappa_c_line <= alpha_D_max)

    # ---------- Build the plot ----------
    fig, ax = plt.subplots(figsize=(13, 8.5), dpi=140)

    # === Exclusion BANDS (rectangular regions where constraints apply) ===

    # BBN: visible decay excluded for m_A' < 1 MeV
    # This is a horizontal band at the BOTTOM of the y-axis, spanning x in [1 eV, 1 MeV]
    # (y is alpha_D, not m_A'). Actually BBN covers ALL alpha_D for those masses.
    bbn_x_lo, bbn_x_hi = 1e-9, 1e-3  # 1 eV to 1 MeV in GeV
    ax.axvspan(bbn_x_lo, bbn_x_hi, ymin=0, ymax=1,
               facecolor="#ffcccc", alpha=0.55, edgecolor="red",
               linewidth=1.0, linestyle="--",
               label="BBN (visible decay): m_A' < 1 MeV")

    # CMB: visible decay excluded for m_A' in [1 MeV, 100 MeV]
    cmb_x_lo, cmb_x_hi = 1e-3, 1e-1
    ax.axvspan(cmb_x_lo, cmb_x_hi, ymin=0, ymax=1,
               facecolor="#fff2b3", alpha=0.55, edgecolor="goldenrod",
               linewidth=1.0, linestyle="--",
               label="CMB (visible decay): 1-100 MeV")

    # SN1987A / XENONnT: visible decay excluded for m_A' in [1, 100] MeV
    # (same range as CMB; shade differently)
    sn_x_lo, sn_x_hi = 1e-3, 1e-1
    # Already covered by CMB band; just add a thicker outline
    ax.add_patch(plt.Rectangle((sn_x_lo, alpha_D_min),
                               sn_x_hi - sn_x_lo,
                               alpha_D_max - alpha_D_min,
                               facecolor="none", edgecolor="darkorange",
                               linewidth=2.0, linestyle=":",
                               label="SN1987A / XENONnT (visible decay)"))

    # === Continuous Lyman-alpha exclusion curves ===
    # EXCLUDED region is ABOVE the curve (higher alpha_D -> larger sigma/m)
    mask = np.isfinite(lyman_alpha_curve)
    ax.plot(m_ap_grid[mask], lyman_alpha_curve[mask],
            color="black", linewidth=2.5, linestyle="-",
            label="Lyman-alpha: sigma/m(30 km/s) = 100 cm$^2$/g")
    mask_m = np.isfinite(lyman_alpha_marginal)
    ax.plot(m_ap_grid[mask_m], lyman_alpha_marginal[mask_m],
            color="black", linewidth=1.2, linestyle="--", alpha=0.7,
            label="Lyman-alpha: sigma/m = 50 cm$^2$/g (marginal)")

    # Fill the EXCLUDED region above the Lyman-alpha curve
    ax.fill_between(m_ap_grid[mask], lyman_alpha_curve[mask], alpha_D_max,
                    facecolor="#888888", alpha=0.18,
                    label="Lyman-alpha EXCLUDED region (sigma/m > 100)")

    # === kappa = kappa_c resonance line (reference, not a constraint) ===
    ax.plot(m_ap_grid[kappa_c_visible], alpha_D_kappa_c_line[kappa_c_visible],
            color="green", linewidth=1.5, linestyle="-.",
            alpha=0.8,
            label=f"kappa = kappa_c = {kappa_c} (s-wave bound-state threshold)")

    # === Candidate points ===
    for c in CANDIDATES:
        c["kappa"] = constants.compute_kappa(c["alpha_D"],
                                              constants.M_CHI_GEV,
                                              c["m_A_prime_GeV"])
        ax.scatter(c["m_A_prime_GeV"], c["alpha_D"],
                   marker=c["marker"], s=c["ms"] ** 1.6,
                   color=c["color"], edgecolor="black", linewidth=1.0,
                   zorder=10)
        # Annotate
        dx = c["m_A_prime_GeV"]
        dy = c["alpha_D"]
        # Offset labels slightly to avoid overlap
        if c["label"].startswith("Framework"):
            ax.annotate(c["label"], xy=(dx, dy), xytext=(8, -22),
                        textcoords="offset points",
                        fontsize=9, fontweight="bold", color=c["color"],
                        arrowprops=dict(arrowstyle="->", color=c["color"],
                                        lw=0.8, alpha=0.8))
        elif "Phase-3" in c["label"]:
            ax.annotate(c["label"], xy=(dx, dy), xytext=(8, -22),
                        textcoords="offset points",
                        fontsize=9, fontweight="bold", color=c["color"],
                        arrowprops=dict(arrowstyle="->", color=c["color"],
                                        lw=0.8, alpha=0.8))
        else:
            # Lattice ridge points: place label above-right
            ax.annotate(c["label"], xy=(dx, dy), xytext=(7, 9),
                        textcoords="offset points",
                        fontsize=8, color=c["color"])

    # === Axes / labels ===
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(m_ap_min_GeV, m_ap_max_GeV)
    ax.set_ylim(alpha_D_min, alpha_D_max)
    ax.set_xlabel("Mediator mass  m$_{A'}$  [GeV]", fontsize=13, fontweight="bold")
    ax.set_ylabel(r"Dark fine-structure constant  $\alpha_D = g^2/(4\pi)$",
                  fontsize=13, fontweight="bold")
    ax.set_title(
        "SIDM composite-DM mediator: quantitative exclusion curves\n"
        f"(m_chi = {constants.M_CHI_GEV} GeV, "
        f"kappa_c = {kappa_c} per Simonov/Tulin-Yu convention)",
        fontsize=13, fontweight="bold",
    )

    # Tick formatter for x-axis (eV / keV / MeV / GeV / TeV)
    def m_ap_formatter(x, pos):
        if x >= 1e3:
            return f"{x/1e3:.0f} TeV"
        elif x >= 1.0:
            return f"{x:.0f} GeV"
        elif x >= 1e-3:
            return f"{x*1e3:.0f} MeV"
        elif x >= 1e-6:
            return f"{x*1e6:.0f} keV"
        elif x >= 1e-9:
            return f"{x*1e9:.0f} eV"
        else:
            return f"{x*1e12:.1f} meV"

    from matplotlib.ticker import FuncFormatter, LogLocator
    ax.xaxis.set_major_formatter(FuncFormatter(m_ap_formatter))
    ax.xaxis.set_major_locator(LogLocator(base=10.0, numticks=12))
    ax.tick_params(axis="both", which="major", labelsize=11)

    # Reference alpha_D values on y-axis
    for y_ref, y_lbl in [(1e-10, r"$10^{-10}$"), (1e-8, r"$10^{-8}$"),
                          (1e-6, r"$10^{-6}$"), (1e-4, r"$10^{-4}$"),
                          (1e-2, r"$10^{-2}$")]:
        ax.axhline(y_ref, color="grey", linewidth=0.4, alpha=0.3)

    # Legend (placed outside plot to the right)
    handles, labels = ax.get_legend_handles_labels()
    # Reorder so candidate points come last
    order = (
        ["BBN (visible decay): m_A' < 1 MeV",
         "CMB (visible decay): 1-100 MeV",
         "SN1987A / XENONnT (visible decay)",
         "Lyman-alpha: sigma/m(30 km/s) = 100 cm$^2$/g",
         "Lyman-alpha: sigma/m = 50 cm$^2$/g (marginal)",
         "Lyman-alpha EXCLUDED region (sigma/m > 100)",
         f"kappa = kappa_c = {kappa_c} (s-wave bound-state threshold)"]
    )
    ordered_handles = []
    ordered_labels = []
    for lab in order:
        if lab in labels:
            idx = labels.index(lab)
            ordered_handles.append(handles[idx])
            ordered_labels.append(labels[idx])
    # Append any remaining (should be none for candidate points, but just in case)
    for h, l in zip(handles, labels):
        if l not in ordered_labels:
            ordered_handles.append(h)
            ordered_labels.append(l)

    # Candidate legend (manual)
    cand_handles = [
        Line2D([0], [0], marker=c["marker"], color="w",
               markerfacecolor=c["color"], markeredgecolor="black",
               markersize=11, label=c["label"])
        for c in CANDIDATES
    ]

    leg1 = ax.legend(ordered_handles, ordered_labels,
                     loc="upper left", fontsize=9, framealpha=0.92,
                     title="Exclusion curves / bands",
                     title_fontsize=10)
    ax.add_artist(leg1)
    leg2 = ax.legend(handles=cand_handles, loc="upper right",
                     fontsize=9, framealpha=0.92,
                     title="Candidate points",
                     title_fontsize=10)

    ax.grid(True, which="major", linestyle="-", linewidth=0.4, alpha=0.3)
    ax.grid(True, which="minor", linestyle=":", linewidth=0.2, alpha=0.2)

    # ============================================================
    # Save outputs (REVIEWER-16 item 9: configurable via env var)
    # ============================================================
    import os
    _default_docs_dir = _PROJECT_ROOT / "v0.3-prelim" / "docs"
    _default_data_dir = _PROJECT_ROOT / "v0.3-prelim" / "data" / "results"
    docs_dir = Path(os.environ.get("SIDM_DOCS_DIR",    str(_default_docs_dir)))
    data_dir = Path(os.environ.get("SIDM_RESULTS_DIR", str(_default_data_dir)))
    docs_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)

    pdf_path = docs_dir / "V19_2_F_PRIORITY3_CONSTRAINT_PLOT.pdf"
    png_path = docs_dir / "V19_2_F_PRIORITY3_CONSTRAINT_PLOT.png"
    json_path = data_dir / "v19_2_f_priority3_constraint_plot.json"
    report_path = docs_dir / "V19_2_F_PRIORITY3_CONSTRAINT_PLOT_REPORT.md"

    fig.tight_layout()
    fig.savefig(pdf_path, bbox_inches="tight", facecolor="white")
    fig.savefig(png_path, bbox_inches="tight", facecolor="white", dpi=180)
    plt.close(fig)

    # ============================================================
    # Build the data JSON
    # ============================================================

    # Compute verdicts for each candidate
    candidates_with_out = []
    for c in CANDIDATES:
        verdicts = evaluate_constraints(c["alpha_D"], c["m_A_prime_GeV"])
        candidates_with_out.append({
            "label": c["label"],
            "alpha_D": c["alpha_D"],
            "m_A_prime_GeV": c["m_A_prime_GeV"],
            "m_A_prime_eV": c["m_A_prime_GeV"] * 1e9,
            "kappa": c["kappa"],
            "kappa_over_kappa_c": c["kappa"] / kappa_c,
            "verdicts": verdicts,
            "marker": c["marker"],
            "color": c["color"],
        })

    # Summary data
    plot_data = {
        "_meta": {
            "description": "v19.2-F Priority 3: quantitative exclusion plot in (alpha_D, m_A') plane",
            "date": "2026-10-11",
            "convention": "alpha_D = g^2 / (4*pi) (LOCKED per constants.py)",
            "m_chi_GeV": constants.M_CHI_GEV,
            "kappa_c_analytic": constants.KAPPA_C_ANALYTIC,
            "axes": {
                "x": "m_A_prime [GeV], log scale",
                "y": "alpha_D, log scale",
                "x_range_GeV": [m_ap_min_GeV, m_ap_max_GeV],
                "y_range": [alpha_D_min, alpha_D_max],
            },
        },
        "constraints": {
            "BBN": {
                "source": "Planck 2018 (arXiv:1807.06209); Olive et al. 2019 review",
                "limit": "Delta N_eff < 0.30; dark photon epsilon < 1e-10 for visible decay",
                "applies_to": "m_A' in [1 eV, 100 MeV] (visible decay only)",
                "exclusion_shape": "vertical band 1 eV <= m_A' <= 1 MeV (visible decay)",
            },
            "CMB": {
                "source": "Slatyer 2016 (PRD 93, 023527); Poulin 2018 (PRD 97, 123504)",
                "limit": "tau_A' > 1e25 sec for m_A' in [1, 100] MeV decaying to e+e-",
                "applies_to": "m_A' in [1, 100] MeV (visible decay)",
                "exclusion_shape": "vertical band 1 MeV <= m_A' <= 100 MeV",
            },
            "SN1987A": {
                "source": "Caputo et al. 2021 (PRD 103, 063014)",
                "limit": "epsilon < 1e-5 to 1e-10 for m_A' in [1, 100] MeV",
                "applies_to": "m_A' in [1, 100] MeV (visible decay)",
                "exclusion_shape": "vertical band 1 MeV <= m_A' <= 100 MeV (same as CMB)",
            },
            "Lyman-alpha": {
                "source": "Vogelsberger 2012 (MNRAS 423, 3740); Zavala 2013 (MNRAS 431, L104)",
                "limit": "sigma/m(30 km/s) > 100 cm^2/g -> excluded",
                "applies_to": "all (alpha_D, m_A') with sigma/m(30) > 100",
                "exclusion_shape": (
                    "upper region in (alpha_D, m_A') plane; curve computed "
                    "analytically from Born formula at v = 30 km/s"
                ),
                "curve_formula": (
                    "sigma_T = (g^4 m_chi^2) / (8 pi m_A^4) * L(s)^2, "
                    "s = (m_chi v / (sqrt(2) m_A))^2, "
                    "alpha_D = g^2/(4 pi)"
                ),
                "caveat": (
                    "Born underestimates sigma/m in deep-Sommerfeld regime "
                    "(kappa > kappa_c); actual exclusion boundary is HIGHER "
                    "(more permissive) than shown for kappa > kappa_c"
                ),
            },
            "XENONnT_LZ": {
                "source": "Aprile 2022 (PRL 129, 161805); Aalbers 2022 (arXiv:2207.03764)",
                "limit": "sigma_e < 1e-40 cm^2 for m_DM in [100 MeV, 10 GeV] -> epsilon < 1e-5",
                "applies_to": "m_A' in [1, 100] MeV (visible decay)",
                "exclusion_shape": "vertical band 1 MeV <= m_A' <= 100 MeV (same as CMB/SN1987A)",
            },
        },
        "lyman_alpha_curve": {
            "v_kms": 30.0,
            "sigma_m_target_cm2_g": 100.0,
            "m_chi_GeV": constants.M_CHI_GEV,
            "m_A_prime_grid_sample": m_ap_grid[::30].tolist(),
            "alpha_D_curve_sample": lyman_alpha_curve[::30].tolist(),
            "n_grid_points": int(m_ap_grid.size),
        },
        "kappa_c_line": {
            "kappa_c": kappa_c,
            "formula": "alpha_D = kappa_c * m_A' / m_chi",
            "m_A_prime_grid_sample": m_ap_grid[::30].tolist(),
            "alpha_D_line_sample": alpha_D_kappa_c_line[::30].tolist(),
        },
        "candidates": candidates_with_out,
        "output_files": {
            "pdf": str(pdf_path.relative_to(_PROJECT_ROOT)),
            "png": str(png_path.relative_to(_PROJECT_ROOT)),
            "data_json": str(json_path.relative_to(_PROJECT_ROOT)),
            "report_md": str(report_path.relative_to(_PROJECT_ROOT)),
        },
    }

    with open(json_path, "w") as f:
        json.dump(plot_data, f, indent=2)

    # ============================================================
    # Build the report
    # ============================================================
    lines = []
    lines.append("# Priority 3 Constraint Plot Report\n")
    lines.append("**v19.2-F — quantitative exclusion curves in the (alpha_D, m_A') plane.**\n")
    lines.append("")
    lines.append(f"Plot file: `v0.3-prelim/docs/V19_2_F_PRIORITY3_CONSTRAINT_PLOT.pdf` (and `.png`)\n")
    lines.append("")
    lines.append("## Setup\n")
    lines.append(f"- DM mass: m_chi = {constants.M_CHI_GEV} GeV")
    lines.append(f"- Coupling convention: alpha_D = g^2 / (4 pi) [LOCKED, per constants.py]")
    lines.append(f"- kappa_c (s-wave bound-state threshold): {kappa_c}")
    lines.append(f"- Born formula (Tulin-Yu-Zurek 2013, Eq. 3):")
    lines.append("    sigma_T = (g^4 m_chi^2) / (8 pi m_A^4) * L(s)^2")
    lines.append("    s = (m_chi v / (sqrt(2) m_A))^2,  L(s) = ln(1+1/s) - 1/(1+s)")
    lines.append("")
    lines.append("## Constraints plotted\n")
    lines.append("| Constraint | Source | Visible-decay region | Invisible-decay note |")
    lines.append("|------------|--------|----------------------|----------------------|")
    lines.append("| BBN | Planck 2018 / Olive 2019 | m_A' < 1 MeV excluded | Survives |")
    lines.append("| CMB | Slatyer 2016 / Poulin 2018 | 1 MeV < m_A' < 100 MeV excluded | Survives |")
    lines.append("| SN1987A | Caputo 2021 | 1 MeV < m_A' < 100 MeV excluded | Survives |")
    lines.append("| Lyman-alpha | Vogelsberger 2012 / Zavala 2013 | sigma/m(30 km/s) > 100 cm^2/g | **Always applies** |")
    lines.append("| XENONnT / LZ | Aprile 2022 / Aalbers 2022 | 1 MeV < m_A' < 100 MeV excluded | Survives |")
    lines.append("")
    lines.append("**Important**: BBN, CMB, SN1987A, XENONnT constraints all apply only if the dark")
    lines.append("photon is VISIBLE (kinetic mixing epsilon > 1e-10, decays to SM). For an INVISIBLE")
    lines.append("dark photon (no kinetic mixing, decays only to dark sector), all those constraints")
    lines.append("vanish. **Lyman-alpha is the ONLY constraint that applies unconditionally** because")
    lines.append("it depends on sigma/m (DM self-scattering), not on the decay channel.")
    lines.append("")
    lines.append("## Candidate points and verdicts\n")
    lines.append("| Candidate | alpha_D | m_A' | kappa | Lyman-alpha sigma/m | Verdict (visible) | Verdict (invisible) |")
    lines.append("|-----------|---------|------|-------|---------------------|---------------------|----------------------|")

    # Build verdicts summary per candidate
    for cwo in candidates_with_out:
        v = cwo["verdicts"]
        sig_ly = v.get("Lyman-alpha_value_cm2_g", 0.0)
        # Compose a compact visible verdict
        vis_v = []
        invis_v = []
        for cname in ["BBN", "CMB", "SN1987A", "Lyman-alpha", "XENONnT/LZ"]:
            vis_v.append(f"{cname}={v[cname]['visible']}")
            invis_v.append(f"{cname}={v[cname]['invisible']}")
        vis_str = "; ".join(vis_v)
        invis_str = "; ".join(invis_v)
        # Aggregate
        def aggregate_verdict(verdict_list):
            """Reduce a list of per-constraint verdicts to one overall verdict."""
            if any(vv == "EXCLUDED" for vv in verdict_list):
                return "EXCLUDED"
            if any(vv == "MARGINAL" for vv in verdict_list):
                return "MARGINAL"
            return "ALLOWED"

        agg_vis = aggregate_verdict([v[c]["visible"]
                                      for c in ["BBN", "CMB", "SN1987A",
                                                  "Lyman-alpha", "XENONnT/LZ"]])
        agg_inv = aggregate_verdict([v[c]["invisible"]
                                      for c in ["BBN", "CMB", "SN1987A",
                                                  "Lyman-alpha", "XENONnT/LZ"]])
        lines.append(
            f"| {cwo['label']} | {cwo['alpha_D']:.2e} | "
            f"{cwo['m_A_prime_eV']:.3g} eV | "
            f"{cwo['kappa']:.2e} | "
            f"{sig_ly:.3g} cm^2/g | "
            f"**{agg_vis}** | "
            f"**{agg_inv}** |"
        )

    lines.append("")
    lines.append("### Per-candidate detail\n")

    for cwo in candidates_with_out:
        v = cwo["verdicts"]
        sig_ly = v.get("Lyman-alpha_value_cm2_g", 0.0)
        lines.append(f"**{cwo['label']}**  (alpha_D={cwo['alpha_D']:.2e}, m_A'={cwo['m_A_prime_eV']:.3g} eV, kappa={cwo['kappa']:.2e}, kappa/kappa_c={cwo['kappa_over_kappa_c']:.2e})")
        lines.append("")
        lines.append(f"  - Lyman-alpha sigma/m(v=30 km/s, Born) = {sig_ly:.3g} cm^2/g")
        if sig_ly > 100:
            lines.append(f"    -> Lyman-alpha: EXCLUDED (Born value > 100 cm^2/g)")
        elif sig_ly > 50:
            lines.append(f"    -> Lyman-alpha: MARGINAL (Born value 50-100 cm^2/g)")
        else:
            lines.append(f"    -> Lyman-alpha: ALLOWED by Born (sigma/m < 50 cm^2/g)")
        lines.append(f"  - BBN (visible): {v['BBN']['visible']}")
        lines.append(f"  - BBN (invisible): {v['BBN']['invisible']}")
        lines.append(f"  - CMB (visible): {v['CMB']['visible']}")
        lines.append(f"  - CMB (invisible): {v['CMB']['invisible']}")
        lines.append(f"  - SN1987A (visible): {v['SN1987A']['visible']}")
        lines.append(f"  - SN1987A (invisible): {v['SN1987A']['invisible']}")
        lines.append(f"  - XENONnT/LZ (visible): {v['XENONnT/LZ']['visible']}")
        lines.append(f"  - XENONnT/LZ (invisible): {v['XENONnT/LZ']['invisible']}")
        lines.append("")
        # Caveat for deep-Sommerfeld
        if cwo["kappa"] > kappa_c:
            lines.append(f"  **CAVEAT**: kappa = {cwo['kappa']:.2e} > kappa_c = {kappa_c}, "
                         f"so the Born formula is NOT reliable here. The deep-Sommerfeld "
                         f"enhancement can boost sigma/m by factors of 10-100, so the "
                         f"Lyman-alpha verdict may be MORE EXCLUDED than shown.")
            lines.append("")

    lines.append("## Key finding\n")
    lines.append("The plot illustrates the following structure in the (alpha_D, m_A') plane:")
    lines.append("")
    lines.append("1. **All 'visible-decay' constraints (BBN/CMB/SN1987A/XENONnT) carve out")
    lines.append("   a vertical band at m_A' in [1 eV, 100 MeV]** -- but they vanish for an")
    lines.append("   invisible dark photon. These are constraints on the dark photon's")
    lines.append("   COUPLING TO SM, not on the dark sector self-interaction strength alpha_D.")
    lines.append("")
    lines.append("2. **Lyman-alpha is the only constraint that is unavoidable**: it depends")
    lines.append("   directly on alpha_D (via sigma/m), regardless of whether the dark")
    lines.append("   photon is visible. The exclusion boundary sigma/m(30 km/s) = 100 cm^2/g")
    lines.append("   is the upper envelope of the allowed region.")
    lines.append("")
    lines.append("3. **In the deep-Sommerfeld regime (kappa > kappa_c)** -- which is where")
    lines.append("   the framework point (200 eV) and the Phase-3 best fit (126 keV) sit --")
    lines.append("   the Born formula UNDERESTIMATES sigma/m. The true Lyman-alpha")
    lines.append("   exclusion boundary is HIGHER (more permissive) than the Born curve")
    lines.append("   shown. A validated deep-Sommerfeld solver (Hulthen/lattice) is")
    lines.append("   needed to draw the true boundary in this regime.")
    lines.append("")
    lines.append("4. **The kappa = kappa_c reference line** (green dash-dot) marks the")
    lines.append("   s-wave bound-state threshold. To the right of this line, the Born")
    lines.append("   formula breaks down and a deep-Sommerfeld solver is required.")
    lines.append("")
    lines.append("## Caveats and follow-ups\n")
    lines.append("- Lyman-alpha curve is Born-only; in deep-Sommerfeld regime the curve")
    lines.append("  is a LOWER bound on alpha_D, the true exclusion region is HIGHER.")
    lines.append("- Visible-decay constraints assume epsilon > 1e-10. For a fully")
    lines.append("  decoupled (invisible) dark photon, those constraints vanish.")
    lines.append("- BBN/CMB/SN1987A/XENONnT are quoted as 'vertical bands' because they")
    lines.append("  constrain the kinetic mixing epsilon, not alpha_D directly. If the")
    lines.append("  visible-decay scenario is realized, the bands represent regions where")
    lines.append("  the dark photon must have epsilon < 1e-10 (invisible at those scales).")
    lines.append("- Thermal relic constraint (<sigma v> ~ 3e-26 cm^3/s) is NOT shown")
    lines.append("  because the framework candidate is non-thermal (per the constraint")
    lines.append("  JSON: 'framework point NOT a thermal relic; no annihilation constraint').")
    lines.append("")

    with open(report_path, "w") as f:
        f.write("\n".join(lines))

    # ============================================================
    # Print summary
    # ============================================================
    print()
    print("=" * 72)
    print("OUTPUT FILES")
    print("=" * 72)
    print(f"  PDF: {pdf_path}")
    print(f"  PNG: {png_path}")
    print(f"  JSON: {json_path}")
    print(f"  Report: {report_path}")
    print()

    # File sizes
    for p in [pdf_path, png_path, json_path, report_path]:
        sz = p.stat().st_size
        print(f"    {p.name:60s} {sz:>10,} bytes")

    print()
    print("=" * 72)
    print("CANDIDATE POINT VERDICTS")
    print("=" * 72)
    for cwo in candidates_with_out:
        v = cwo["verdicts"]
        sig_ly = v.get("Lyman-alpha_value_cm2_g", 0.0)
        # Visible-decay aggregation
        agg_vis = ("EXCLUDED"
                   if any(v[c]["visible"] == "EXCLUDED"
                          for c in ["BBN", "CMB", "SN1987A",
                                    "Lyman-alpha", "XENONnT/LZ"])
                   else ("MARGINAL"
                         if any(v[c]["visible"] == "MARGINAL"
                                for c in ["BBN", "CMB", "SN1987A",
                                          "Lyman-alpha", "XENONnT/LZ"])
                         else "ALLOWED"))
        agg_inv = ("EXCLUDED"
                   if any(v[c]["invisible"] == "EXCLUDED"
                          for c in ["BBN", "CMB", "SN1987A",
                                    "Lyman-alpha", "XENONnT/LZ"])
                   else ("MARGINAL"
                         if any(v[c]["invisible"] == "MARGINAL"
                                for c in ["BBN", "CMB", "SN1987A",
                                          "Lyman-alpha", "XENONnT/LZ"])
                         else "ALLOWED"))
        print(f"  {cwo['label']}")
        print(f"    alpha_D={cwo['alpha_D']:.2e}, m_A'={cwo['m_A_prime_eV']:.3g} eV, "
              f"kappa={cwo['kappa']:.2e}")
        print(f"    Lyman-alpha sigma/m(30 km/s, Born) = {sig_ly:.3g} cm^2/g")
        print(f"    VERDICT (visible decay):   {agg_vis}")
        print(f"    VERDICT (invisible decay): {agg_inv}")
        print()

    print("=" * 72)
    print("KEY FINDING")
    print("=" * 72)
    print("  BBN/CMB/SN1987A/XENONnT are constraints on kinetic mixing (visible decay).")
    print("  Lyman-alpha is the ONLY constraint that applies to alpha_D directly.")
    print("  For an invisible dark photon (no kinetic mixing), the visible-decay")
    print("  bands vanish and only Lyman-alpha survives.")
    print()
    print("  The framework point (200 eV) and Phase-3 best fit (126 keV) sit in the")
    print("  kappa > kappa_c regime where Born is unreliable -- the deep-Sommerfeld")
    print("  Hulthen solver (Priority 2) is needed to draw the true Lyman-alpha")
    print("  exclusion boundary there.")
    print()

    return plot_data


if __name__ == "__main__":
    main()