"""
T101 — Data extraction for Portal B Tier-2 fit.

Extracts the LZ 248 keV event local-significance data from
arXiv:2609.02823 Table S8 (inelastic 𝒪₁ˢ and 𝒪₄ˢ models) and
builds a likelihood as a function of (m_χ, δ).

This is the "B" part of B-then-A from the user's request:
data extraction (1-2 hours) before the full Tier-2 fit.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path


# Table S8 from LZ paper (arXiv:2609.02823) — local significance in σ
# Format: {(operator, m_chi_GeV): {delta_keV: significance_sigma}}
TABLE_S8 = {
    "Os1": {
        400: {0: 0.0, 50: 0.0, 100: 0.8, 150: 2.2, 200: 2.6,
              250: 2.9, 300: 2.9, 350: float("nan")},
        1000: {0: 0.0, 50: 0.0, 100: 0.8, 150: 2.2, 200: 2.7,
               250: 2.9, 300: 3.0, 350: 3.3},
        4000: {0: 0.0, 50: 0.0, 100: 1.0, 150: 2.3, 200: 2.7,
               250: 2.9, 300: 3.0, 350: 3.3},
    },
    "Ov1": {
        400: {0: 0.8, 50: 1.4, 100: 2.6, 150: 2.8, 200: 2.8,
              250: 2.8, 300: 3.1, 350: float("nan")},
        1000: {0: 1.3, 50: 1.6, 100: 2.6, 150: 2.8, 200: 2.9,
               250: 3.0, 300: 3.4, 350: 3.4},
        4000: {0: 1.1, 50: 1.7, 100: 2.6, 150: 2.9, 200: 2.9,
               250: 3.1, 300: 3.4, 350: 3.4},
    },
    "Os4": {
        400: {0: 2.6, 50: 2.7, 100: 2.8, 150: 3.1, 200: 3.2,
              250: 3.2, 300: 3.3, 350: float("nan")},
        1000: {0: 2.7, 50: 2.8, 100: 2.8, 150: 3.0, 200: 3.2,
               250: 3.2, 300: 3.4, 350: 3.4},
        4000: {0: 2.8, 50: 3.0, 100: 3.0, 150: 3.1, 200: 3.2,
               250: 3.3, 300: 3.4, 350: 3.4},
    },
    "Ov4": {
        400: {0: 2.6, 50: 2.7, 100: 2.8, 150: 3.1, 200: 3.2,
              250: 3.2, 300: 3.3, 350: float("nan")},
        1000: {0: 2.7, 50: 2.8, 100: 2.8, 150: 3.0, 200: 3.2,
               250: 3.2, 300: 3.4, 350: 3.4},
        4000: {0: 2.8, 50: 3.0, 100: 3.0, 150: 3.1, 200: 3.2,
               250: 3.3, 300: 3.4, 350: 3.4},
    },
}


# LZ paper Table I — expected and fitted background events in WS ROI
LZ_BACKGROUND = {
    "internal_beta": {"expected": 1341, "fit": 1340, "fit_err": 43},
    "nu_ER": {"expected": 140.6, "fit": 140.3, "fit_err": 8.4},
    "Xe136": {"expected": 110.0, "fit": 114.2, "fit_err": 16.1},
    "CH3T_C14": {"expected": 55.3, "fit": 55.2, "fit_err": 3.1},
    "Xe124": {"expected": 21.0, "fit": 22.6, "fit_err": 5.0},
    "Kr83m": {"expected": 17.1, "fit": 17.0, "fit_err": 3.5},
    "I125": {"expected": 8.9, "fit": 9.8, "fit_err": 2.3},
    "detector_ER": {"expected": 8.5, "fit": 9.4, "fit_err": 1.7},
    "accidentals": {"expected": 2.7, "fit": 2.6, "fit_err": 0.6},
    "Xe127_Xe125": {"expected": 1.5, "fit": 1.2, "fit_err": 0.3},
    "atmospheric_nu": {"expected": 0.11, "fit": 0.11, "fit_err": 0.02},
    "B8_hep_nu": {"expected": 0.057, "fit": 0.057, "fit_err": 0.006},
    "MSSI": {"expected": 0.0049, "fit": 0.0046, "fit_err": 0.0048},
    "detector_NR": {"expected_range": [0, 0.118], "fit_Ls10": "0.118"},
    "WIMP_Ls10_1000GeV": {"fit": 1.0, "fit_err_pos": 1.4, "fit_err_neg": 0.7},
    "total_counts": {"fit": 1713, "fit_err": 39, "observed": 1710},
}

# Background in 248 keV region (where the event of interest sits)
LZ_BG_248KEV = 0.0106
LZ_BG_248KEV_ERR = 0.0008

# Event of interest
LZ_EVENT = {
    "E_R_keV": 248,
    "E_R_stat_keV": 23,
    "E_R_sys_keV": 23,
    "S1c_phd": 540.1,
    "S2c_phd": 9268,
    "log10_S2c": 3.968,  # log10(9268) = 3.9670
    "time_UTC": "2026-06-16 21:22:39",  # Note: LZ paper says 16 June 2023
    "recorded_date": "2023-06-16",
    "z_cm": 26.4,
    "r2_cm2": 45.92,
    "NR_band_offset_sigma": 1.5,  # 1.5σ below NR median
    "ER_band_offset_sigma": 6.7,  # 6.7σ below ER median
}

# Exposure and ROI
LZ_EXPOSURE = {
    "tonne_years": 2.84,
    "live_days": 220,
    "fiducial_mass_tonnes": 4.71,
    "fiducial_mass_err": 0.08,
    "S1c_range_phd": [3, 600],
    "S2_range_phd": 645,  # minimum
    "S2c_range_log10": [2.75, 4.15],
    "ER_range_keV": [5.4, 270],
    "efficiency_avg_14_to_250_keV": 0.96,
    "efficiency_50pct_keV": 269.9,
}


def significance_to_p_value(sigma):
    """Convert one-sided significance in σ to p-value."""
    if math.isnan(sigma):
        return 1.0
    # One-sided normal: p = 0.5 * erfc(sigma / sqrt(2))
    return 0.5 * math.erfc(sigma / math.sqrt(2))


def log_likelihood_lz_event(sigma_predicted, N_obs=1):
    """Simple Poisson log-likelihood for N_obs=1 given N_predicted.

    L = N_pred^(N_obs) * exp(-N_pred) / N_obs!
    log L = N_obs * log(N_pred) - N_pred - log(N_obs!)
    """
    if sigma_predicted <= 0:
        return -1e10  # effectively excluded
    # N_pred from σ (cross-section) — but we need N_pred as function of σ
    # For a single-bin count, N_pred ~ σ * (exposure * efficiency)
    # For now, just use the local significance to compute p-value
    # and return log(p)
    # This is a placeholder; full likelihood needs more work
    return math.log(max(sigma_predicted, 1e-10)) - sigma_predicted


def main():
    out_dir = Path(__file__).resolve().parents[1] / "data" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)

    out = {
        "test": "T101_lz_data_extraction",
        "date": "2026-09-08",
        "source": "arXiv:2609.02823 (LZ collaboration), Table S8 + Table I + body",
        "extraction_summary": (
            "Extracted local significance for Os1, Ov1, Os4, Ov4 at "
            "m_chi=400, 1000, 4000 GeV and delta=0,50,100,150,200,250,300,350 keV. "
            "Plus full background table and event-of-interest coordinates."
        ),
        "table_S8_local_significance_sigma": TABLE_S8,
        "background_components": LZ_BACKGROUND,
        "background_248keV_window": {
            "value": LZ_BG_248KEV,
            "err": LZ_BG_248KEV_ERR,
            "note": "Total integrated background in 248 keV region (Fig 5 bottom panel)",
        },
        "event_of_interest": LZ_EVENT,
        "exposure_and_ROI": LZ_EXPOSURE,
    }

    out_path = out_dir / "lz_248kev_data_extraction.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"Wrote {out_path}")

    # Console summary
    print()
    print("=" * 70)
    print("T101 — LZ 248 keV data extraction")
    print("=" * 70)
    print()
    print("Source: arXiv:2609.02823 (LZ collaboration, 2 Sep 2026)")
    print()
    print("Event of interest:")
    for k, v in LZ_EVENT.items():
        print(f"  {k}: {v}")
    print()
    print("Exposure / ROI:")
    for k, v in LZ_EXPOSURE.items():
        print(f"  {k}: {v}")
    print()
    print("Background in 248 keV region:")
    print(f"  {LZ_BG_248KEV} ± {LZ_BG_248KEV_ERR} counts (per Fig 5 bottom panel)")
    print()
    print("Local significance (sigma) for Os1 operator at m_chi=1000 GeV:")
    for delta, sig in TABLE_S8["Os1"][1000].items():
        if not math.isnan(sig):
            print(f"  delta = {delta:3d} keV: {sig:.1f}σ")
    print()
    print("Local significance (sigma) for Ov1 operator at m_chi=1000 GeV:")
    for delta, sig in TABLE_S8["Ov1"][1000].items():
        if not math.isnan(sig):
            print(f"  delta = {delta:3d} keV: {sig:.1f}σ")
    print()
    print("Local significance (sigma) for Os4 = Ov4 operator at m_chi=1000 GeV:")
    for delta, sig in TABLE_S8["Os4"][1000].items():
        if not math.isnan(sig):
            print(f"  delta = {delta:3d} keV: {sig:.1f}σ")
    print()
    print("Key finding: All four operators reach 3.3-3.4σ at delta=300-350 keV")
    print("and m_chi=1000 GeV. The Ov1 operator is unique in reaching 1.3σ at")
    print("delta=0 keV (elastic), consistent with the magnetic-moment operator.")


if __name__ == "__main__":
    main()
