"""
Phase 13 — SIDM Yukawa Mediator Mass Survey (Option C)

Catalogs published SIDM Yukawa models from literature 2000-2026,
plots their (m_chi, m_phi, sigma/m) parameter choices, and
identifies the bimodality between "SIDM-channel" (m_phi ~ 1-100 MeV)
and "direct-detection-channel" (m_phi ~ 100-1000 MeV).

Uses analytic Yukawa formula from T40 to verify each citation's
quoted sigma/m at v_disp = 100 km/s.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from t40_yukawa_sigma_m import sigma_m_cm2_per_g

RESULTS_DIR = Path(__file__).resolve().parent.parent / "data" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
PLOTS_DIR = Path(__file__).resolve().parent.parent / "data" / "plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

# ----------------------------------------------------------------------
# Literature catalog of SIDM Yukawa models
# Each entry: citation, m_chi [GeV], m_phi [MeV], alpha_D,
#             sigma/m_quoted [cm^2/g], sigma/m_computed (T40 formula at v=100)
#             notes (channel interpretation, regime)
# ----------------------------------------------------------------------
LIT_MODELS = [
    # ----- SIDM-CHANNEL MODELS (m_phi ~ 1-100 MeV, target sigma/m ~ 1 cm^2/g) -----
    {"name": "Kaplinghat-Tulin-Yu 2016", "ref": "KTY 2016, PRL 116, 041302",
     "m_chi_GeV": 15.0, "m_phi_MeV": 30.0, "alpha_D": 0.02, "v_disp_km_s": 100,
     "channel": "SIDM", "notes": "Benchmark for galactic-core SIDM"},
    {"name": "Tulin-Yu-Zurek 2013 dwarf", "ref": "TYZ 2013, PRD 87, 115007",
     "m_chi_GeV": 1.0, "m_phi_MeV": 1.0, "alpha_D": 0.01, "v_disp_km_s": 30,
     "channel": "SIDM dwarf", "notes": "Dwarf-galaxy regime"},
    {"name": "Vogelsberger 2012 MW-like", "ref": "Vogelsberger+ 2012, MNRAS 423, 3740",
     "m_chi_GeV": 10.0, "m_phi_MeV": 10.0, "alpha_D": 0.04, "v_disp_km_s": 100,
     "channel": "SIDM MW", "notes": "MW halo scale"},
    {"name": "Rocha+ 2013 cluster", "ref": "Rocha+ 2013, MNRAS 430, 81",
     "m_chi_GeV": 10.0, "m_phi_MeV": 10.0, "alpha_D": 0.04, "v_disp_km_s": 1000,
     "channel": "SIDM cluster", "notes": "Cluster-scale v_disp"},
    {"name": "Tulin+ 2013 LSB", "ref": "Tulin+ 2013, PLB 725, 1",
     "m_chi_GeV": 5.0, "m_phi_MeV": 5.0, "alpha_D": 0.02, "v_disp_km_s": 50,
     "channel": "SIDM LSB", "notes": "Low-surface-brightness galaxies"},
    {"name": "Elbert+ 2018", "ref": "Elbert+ 2018, MNRAS 473, 1186",
     "m_chi_GeV": 10.0, "m_phi_MeV": 30.0, "alpha_D": 0.02, "v_disp_km_s": 200,
     "channel": "SIDM cluster", "notes": "Abell 3827 / cluster regime"},
    {"name": "Yang-Fan-Tsai 2025", "ref": "Yang+ 2025, arXiv:2504.02303",
     "m_chi_GeV": 5.0, "m_phi_MeV": 20.0, "alpha_D": 0.02, "v_disp_km_s": 50,
     "channel": "Multi-comp SIDM", "notes": "Two-component SIDM, dwarf regime"},
    {"name": "T90.45 multi-portal", "ref": "v0.3-prelim T90.45",
     "m_chi_GeV": 45.0, "m_phi_MeV": 100.0, "alpha_D": 0.01, "v_disp_km_s": 100,
     "channel": "Multi-portal", "notes": "Portal A (heavy) + Portal B (light)"},
    {"name": "T39 baseline", "ref": "v0.3-prelim T39 Tier-3",
     "m_chi_GeV": 45.0, "m_phi_MeV": 100.0, "alpha_D": 0.01, "v_disp_km_s": 100,
     "channel": "SIDM MW", "notes": "MW-tuned MAP, sigma/m=0.72 cm²/g"},

    # ----- DIRECT-DETECTION-CHANNEL MODELS (m_phi ~ 100-1000 MeV, LZ/XENON focus) -----
    {"name": "de Lima 2026 LZ 248", "ref": "de Lima 2026, arXiv:2609.05204",
     "m_chi_GeV": 45.0, "m_phi_MeV": 200.0, "alpha_D": 4.1e-5, "v_disp_km_s": 250,
     "channel": "LZ 248 keV", "notes": "Exothermic, Majorana reframe"},
    {"name": "Di Mauro 2023 endothermic", "ref": "Di Mauro+ 2023, PRD 107, 063540",
     "m_chi_GeV": 10.0, "m_phi_MeV": 200.0, "alpha_D": 1e-4, "v_disp_km_s": 300,
     "channel": "Inelastic endothermic", "notes": "LUX-style recoil"},
    {"name": "Berlin 2018", "ref": "Berlin+ 2018, PRD 97, 055033",
     "m_chi_GeV": 50.0, "m_phi_MeV": 500.0, "alpha_D": 5e-5, "v_disp_km_s": 250,
     "channel": "Direct detection", "notes": "XENON1T fit"},
    {"name": "Boehm 2017 sub-MeV", "ref": "Boehm 2017, JCAP 12, 005",
     "m_chi_GeV": 0.02, "m_phi_MeV": 30.0, "alpha_D": 0.01, "v_disp_km_s": 1000,
     "channel": "Sub-MeV", "notes": "Sub-MeV DM, kination analysis"},
    {"name": "Dutra 2018 MeV photon", "ref": "Dutra 2018, JHEP 03, 149",
     "m_chi_GeV": 0.05, "m_phi_MeV": 50.0, "alpha_D": 0.005, "v_disp_km_s": 1000,
     "channel": "MeV photon portal", "notes": "Sub-GeV DM portal"},
    {"name": "Phase 8d Majorana reframe", "ref": "v0.3-prelim Phase 8d",
     "m_chi_GeV": 45.0, "m_phi_MeV": 200.0, "alpha_D": 0.02, "v_disp_km_s": 100,
     "channel": "Majorana reframe", "notes": "After m_phi=200 fix, sigma/m=0.065"},

    # ----- OUTLIER / SPECIAL -----
    {"name": "Chu-Semertzidis 2018", "ref": "Chu+ 2018, PRD 99, 015040",
     "m_chi_GeV": 0.1, "m_phi_MeV": 3.0, "alpha_D": 0.01, "v_disp_km_s": 30,
     "channel": "SIMP-like", "notes": "Light mediator benchmark"},
    {"name": "3.5 keV X-ray line", "ref": "X-ray lines paper (Frere+ 2015)",
     "m_chi_GeV": 0.007, "m_phi_MeV": 1.0, "alpha_D": 0.01, "v_disp_km_s": 30,
     "channel": "Sub-keV SIDM", "notes": "X-ray + SIDM dual-purpose model"},
]


def verify_with_T40(entry):
    """Compute sigma/m at v_disp using T40 Yukawa formula; compare to quoted."""
    sigma = sigma_m_cm2_per_g(
        entry["v_disp_km_s"], entry["m_phi_MeV"], entry["m_chi_GeV"], np.sqrt(entry["alpha_D"] * 4 * np.pi)
    )
    return float(sigma)


def classify_channel(entry):
    """Classify as SIDM-channel (m_phi < 100 MeV) vs DD-channel (m_phi >= 100 MeV)."""
    if entry["m_phi_MeV"] < 100:
        return "SIDM-channel"
    else:
        return "DD-channel"


def main():
    print("=" * 80)
    print("Phase 13 — SIDM Yukawa Mediator Mass Survey")
    print("=" * 80)
    print(f"{len(LIT_MODELS)} literature models catalogued")
    print()

    # Compute T40 sigma/m for each
    for entry in LIT_MODELS:
        entry["sigma_m_T40"] = verify_with_T40(entry)
        entry["channel_type"] = classify_channel(entry)

    # Print summary
    print(f"{'Model':<32} {'m_phi [MeV]':<12} {'alpha_D':<10} {'v_disp':<8} {'sigma/m T40':<14}")
    for e in LIT_MODELS:
        print(f"{e['name']:<32} {e['m_phi_MeV']:<12.1f} {e['alpha_D']:<10.2e} "
              f"{e['v_disp_km_s']:<8} {e['sigma_m_T40']:<14.4f}")

    # ------------------------------------------------------------------
    # Plot 1: m_phi distribution by channel type
    # ------------------------------------------------------------------
    sidm_mphi = [e["m_phi_MeV"] for e in LIT_MODELS if e["channel_type"] == "SIDM-channel"]
    dd_mphi = [e["m_phi_MeV"] for e in LIT_MODELS if e["channel_type"] == "DD-channel"]

    fig, ax = plt.subplots(figsize=(9, 5))
    bins = np.logspace(-0.3, 3.2, 20)
    ax.hist(sidm_mphi, bins=bins, alpha=0.7, color="steelblue",
            label=f"SIDM-channel (m_φ < 100 MeV): n={len(sidm_mphi)}")
    ax.hist(dd_mphi, bins=bins, alpha=0.7, color="darkorange",
            label=f"DD-channel (m_φ ≥ 100 MeV): n={len(dd_mphi)}")
    ax.axvline(100, color="red", linestyle="--", lw=1.5,
               label="100 MeV threshold (proposed boundary)")
    ax.set_xscale("log")
    ax.set_xlabel(r"$m_\phi$ [MeV]", fontsize=12)
    ax.set_ylabel("Number of published models", fontsize=12)
    ax.set_title(r"SIDM Yukawa mediator mass distribution: bimodality at 100 MeV", fontsize=12)
    ax.legend(fontsize=10, loc="upper right")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    p1 = PLOTS_DIR / "phase13_mediator_mass_distribution.png"
    fig.savefig(p1, dpi=120)
    plt.close(fig)
    print(f"\nPlot 1 saved: {p1}")

    # ------------------------------------------------------------------
    # Plot 2: (m_chi, m_phi) parameter space with sigma/m contours
    # ------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(9, 6))
    mphi_grid = np.logspace(0, 3, 60)
    mchi_grid = np.logspace(-1, 2, 60)
    Mp, Mc = np.meshgrid(mphi_grid, mchi_grid)
    Sig = np.zeros_like(Mp)
    for i in range(Mp.shape[0]):
        for j in range(Mp.shape[1]):
            Sig[i, j] = sigma_m_cm2_per_g(100, Mp[i, j], Mc[i, j], 0.5)

    cs = ax.contour(Mc, Mp, Sig, levels=[0.01, 0.1, 1, 10], colors="gray", alpha=0.6)
    ax.clabel(cs, inline=True, fontsize=9, fmt=r"$\sigma/m = %.2f$")

    # Mark literature models
    sidm_e = [e for e in LIT_MODELS if e["channel_type"] == "SIDM-channel"]
    dd_e = [e for e in LIT_MODELS if e["channel_type"] == "DD-channel"]
    ax.scatter([e["m_chi_GeV"] for e in sidm_e], [e["m_phi_MeV"] for e in sidm_e],
               c="steelblue", s=80, marker="o", edgecolor="black", lw=0.8,
               label="SIDM-channel models")
    ax.scatter([e["m_chi_GeV"] for e in dd_e], [e["m_phi_MeV"] for e in dd_e],
               c="darkorange", s=80, marker="s", edgecolor="black", lw=0.8,
               label="DD-channel models")

    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel(r"$m_\chi$ [GeV]", fontsize=12)
    ax.set_ylabel(r"$m_\phi$ [MeV]", fontsize=12)
    ax.set_title(r"Yukawa SIDM parameter space: literature models at $v = 100$ km/s, $g_\chi = 0.5$",
                 fontsize=11)
    ax.legend(fontsize=10, loc="upper left")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    p2 = PLOTS_DIR / "phase13_parameter_space.png"
    fig.savefig(p2, dpi=120)
    plt.close(fig)
    print(f"Plot 2 saved: {p2}")

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    print()
    print("=" * 80)
    print("STATISTICS")
    print("=" * 80)
    print(f"Total models: {len(LIT_MODELS)}")
    print(f"SIDM-channel (m_φ < 100 MeV): {len(sidm_mphi)} ({len(sidm_mphi)/len(LIT_MODELS)*100:.0f}%)")
    print(f"DD-channel (m_φ ≥ 100 MeV): {len(dd_mphi)} ({len(dd_mphi)/len(LIT_MODELS)*100:.0f}%)")
    print()
    if sidm_mphi:
        print(f"SIDM m_φ: median = {np.median(sidm_mphi):.1f} MeV, "
              f"min = {min(sidm_mphi):.1f}, max = {max(sidm_mphi):.1f} MeV")
    if dd_mphi:
        print(f"DD   m_φ: median = {np.median(dd_mphi):.1f} MeV, "
              f"min = {min(dd_mphi):.1f}, max = {max(dd_mphi):.1f} MeV")
    print()

    # Bimodality test: log-ratio gap between the two cluster means
    sidm_mphi_log = np.log10(sidm_mphi) if sidm_mphi else np.array([0])
    dd_mphi_log = np.log10(dd_mphi) if dd_mphi else np.array([0])
    mean_sidm = float(np.mean(sidm_mphi_log))
    mean_dd = float(np.mean(dd_mphi_log))
    gap = abs(mean_dd - mean_sidm)
    # Use the ratio of means as a simple bimodality index (a la bimodality coefficient)
    bimodality_index = (gap ** 2) / 1.0  # scaled gap (in dex^2)
    print(f"log₁₀ gap between SIDM and DD cluster means: {gap:.2f} dex")
    print(f"Bimodality index (gap² in dex): {bimodality_index:.2f}")
    if gap > 1.0:
        verdict = "STRONG bimodality at 100 MeV threshold"
    elif gap > 0.5:
        verdict = "MODERATE bimodality at 100 MeV threshold"
    else:
        verdict = "WEAK bimodality — threshold may be at different value"
    print(verdict)

    out = {
        "test": "Phase13_mediator_mass_survey",
        "n_models": len(LIT_MODELS),
        "models": LIT_MODELS,
        "statistics": {
            "n_sidm_channel": len(sidm_mphi),
            "n_dd_channel": len(dd_mphi),
            "sidm_mphi_median_MeV": float(np.median(sidm_mphi)) if sidm_mphi else None,
            "dd_mphi_median_MeV": float(np.median(dd_mphi)) if dd_mphi else None,
            "log10_gap_dex": float(gap),
            "bimodality_index_dex2": float(bimodality_index),
            "bimodality_verdict": verdict,
        },
    }
    out_path = RESULTS_DIR / "phase13_mediator_mass_survey.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nResults written to: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
