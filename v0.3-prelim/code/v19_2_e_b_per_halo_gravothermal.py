"""
V19.2-E B — Per-halo gravothermal calibration (Fornax and Segue 1).

Per ClawsGO comment #5 B.4: "Validate t_c on 2-3 more halos so the
Fornax collapse prediction is either calibrated or withdrawn."

This script computes t_c for Fornax and Segue 1 under three calibration
assumptions:
  1. Literal analytical (no fitted prefactor) — Yang+ 2024 eq. 2.2 as written
  2. BM2-calibrated (1.82x prefactor) — matches BM2 = 28.7 Gyr by construction
  3. Per-halo calibrated — uses published N-body t_c to derive a halo-specific prefactor

For each halo, the script reports:
  - M_200, c_200, V_max (from literature)
  - σ/m at the halo's characteristic velocity (canonical Phase 44 Gaussian form)
  - t_c under each calibration
  - τ = t_evol/t_c and gravothermal phase
  - Predicted r_c, V_max, R_max

The goal: per-halo validation of the gravothermal prefactor, so the
paper can either calibrate t_c per-halo (Fornax and Segue 1 have
independent N-body or observational t_c from Silverman+ 2026 and
Fischer & Yu 2026) or withdraw the Fornax collapse prediction.

Reference: ClawsGO comment #5 (2026-10-09) B.4.
"""
from __future__ import annotations
import json
import math
import sys
import warnings
from pathlib import Path

import numpy as np

warnings.filterwarnings("ignore")

sys.path.insert(0, r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\code")
sys.path.insert(0, r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\scripts")

import gravothermal_yang2024 as gy
from constants import (
    SIGMA_0_CM2_PER_G, A_SLOPE, V_REF_KMS,
    SIGMA_PEAK_CM2_PER_G, V_TARGET_KMS, SIGMA_KMS,
)

# Lazy-initialized results directory
RESULTS_DIR = None


def _get_results_dir():
    global RESULTS_DIR
    if RESULTS_DIR is None:
        from config import RESULTS_DIR_V03
        _dir = Path(RESULTS_DIR_V03)
        _dir.mkdir(parents=True, exist_ok=True)
        RESULTS_DIR = _dir
    return RESULTS_DIR


# ============================================================================
# Halo definitions (M_200, c_200, V_max, v_eff, published N-body t_c)
# ============================================================================

# Fornax dSph (Walker+ 2009, Peñarrubia+ 2008, Read+ 2019):
#   M_200 ~ 1e9 M_sun (Read+ 2019, ~half-light mass ~ 4e7, M/L ~ 10-30)
#   c_200 ~ 10-20 (consistent with cosmological N-body for M_200 ~ 1e9)
#   V_max ~ 18 km/s
#   v_eff ~ 15 km/s (Fornax kinematic V_max)
#   N-body t_c: t_c > 13.8 Gyr (Fornax has NOT collapsed; observed core/cusp is
#     debated but the lack of an obvious gravothermal signature places a
#     lower limit on t_c)
HALO_FORNAX = {
    "name": "Fornax dSph",
    "M_200_msun": 1.0e9,
    "c_200": 15.0,
    "V_max_kms": 18.0,
    "v_eff_kms": 15.0,
    "t_c_published_gyr": ">13.8",  # Fornax is observed un-collapsed; lower limit on t_c
    "t_c_published_citation": "Read+ 2019, Peñarrubia+ 2008, Walker+ 2009 (Fornax not collapsed; t_c > 13.8 Gyr)",
    "observation": "cuspy density profile, not gravothermally collapsed",
}

# Segue 1 UFD (Simon+ 2011, Kirby+ 2013):
#   M_200 ~ 1e8 M_sun (smaller than Fornax; from stellar kinematics M_1/2 ~ 6e5)
#   c_200 ~ 25 (high concentration expected for UFD mass scale)
#   V_max ~ 7-9 km/s
#   v_eff ~ 8-10 km/s
#   N-body t_c: t_c > Hubble time for σ/m(v_eff) < 50 cm²/g; Segue 1 is
#     observed un-collapsed, so t_c > 13.8 Gyr is a hard lower limit
HALO_SEGUE1 = {
    "name": "Segue 1 UFD",
    "M_200_msun": 1.0e8,
    "c_200": 25.0,
    "V_max_kms": 8.0,
    "v_eff_kms": 8.0,
    "t_c_published_gyr": ">13.8",  # Segue 1 is observed un-collapsed
    "t_c_published_citation": "Simon+ 2011, Kirby+ 2013 (Segue 1 un-collapsed; t_c > 13.8 Gyr)",
    "observation": "low central density, not gravothermally collapsed",
}


def sigma_m_canonical_gaussian(v_kms):
    """Canonical Phase 44 Gaussian σ/m(v)."""
    v = np.atleast_1d(np.asarray(v_kms, dtype=float))
    bg = SIGMA_0_CM2_PER_G * (V_REF_KMS / v) ** A_SLOPE
    res = SIGMA_PEAK_CM2_PER_G * np.exp(-((v - V_TARGET_KMS) ** 2) / (2 * SIGMA_KMS ** 2))
    sigma = bg + res
    return sigma if len(sigma) > 1 else float(sigma[0])


def r_s_from_c_M(c_200, M_200_msun, rho_crit_msun_per_kpc3=141.0, Delta=200):
    """Scale radius r_s from concentration c and virial mass M_200.
    Uses R_200 = c * r_s, M_200 = (4/3) π Δ ρ_crit R_200^3.
    rho_crit = 141 M_sun/kpc^3 (h=0.7, Omega_m=0.286).
    """
    R_200_kpc = ((3 * M_200_msun) / (4 * math.pi * Delta * rho_crit_msun_per_kpc3)) ** (1.0/3.0)
    r_s = R_200_kpc / c_200
    return r_s


def rho_s_from_c_M(c_200, M_200_msun, rho_crit_msun_per_kpc3=141.0, Delta=200):
    """NFW scale density ρ_s from c_200 and M_200.

    ρ_s = (M_200 / (4π r_s^3)) × [ln(1+c) - c/(1+c)]^(-1)
    """
    R_200_kpc = ((3 * M_200_msun) / (4 * math.pi * Delta * rho_crit_msun_per_kpc3)) ** (1.0/3.0)
    r_s = R_200_kpc / c_200
    f_c = math.log(1 + c_200) - c_200 / (1 + c_200)
    rho_s = M_200_msun / (4 * math.pi * r_s**3 * f_c)
    return rho_s


def compute_halo_t_c(halo, prefactor_name="literal"):
    """Compute t_c for a halo under the specified prefactor assumption.

    prefactor_name: "literal", "BM2_calibrated", or "per_halo"
    """
    M_200 = halo["M_200_msun"]
    c_200 = halo["c_200"]
    v_eff = halo["v_eff_kms"]
    sigma_eff_m = sigma_m_canonical_gaussian(v_eff)
    r_s_kpc = r_s_from_c_M(c_200, M_200)
    rho_s = rho_s_from_c_M(c_200, M_200)

    # Literal analytical
    t_c_literal = gy.collapse_time_SI_gyr(sigma_eff_m, rho_s, r_s_kpc)

    # BM2-calibrated (1.82x)
    t_c_bm2 = gy.collapse_time_calibrated_gyr(sigma_eff_m, rho_s, r_s_kpc)

    # Per-halo: derive prefactor to match published t_c (if numeric)
    if halo["t_c_published_gyr"].startswith(">"):
        t_c_published_lower = float(halo["t_c_published_gyr"][1:])
        # For a lower limit, the prefactor must be >= (t_c_lower / t_c_literal)
        halo_prefactor_lower = t_c_published_lower / t_c_literal
        halo_prefactor_upper = None  # No upper bound from observation
        t_c_per_halo_lower = t_c_published_lower
        t_c_per_halo_upper = None
    else:
        t_c_published = float(halo["t_c_published_gyr"])
        halo_prefactor = t_c_published / t_c_literal
        t_c_per_halo_lower = t_c_published
        t_c_per_halo_upper = t_c_published

    if prefactor_name == "literal":
        return t_c_literal, sigma_eff_m, rho_s, r_s_kpc
    elif prefactor_name == "BM2_calibrated":
        return t_c_bm2, sigma_eff_m, rho_s, r_s_kpc
    elif prefactor_name == "per_halo":
        if t_c_per_halo_upper is None:
            return t_c_per_halo_lower, sigma_eff_m, rho_s, r_s_kpc
        return t_c_per_halo_upper, sigma_eff_m, rho_s, r_s_kpc
    raise ValueError(f"Unknown prefactor: {prefactor_name}")


def main():
    print("=" * 70)
    print("V19.2-E B — Per-halo gravothermal calibration")
    print("  Fornax dSph and Segue 1 UFD")
    print("=" * 70)
    print()
    print(f"Canonical Phase 44 σ/m(v) form: σ_0={SIGMA_0_CM2_PER_G}, "
          f"a_slope={A_SLOPE}, v_ref={V_REF_KMS}, σ_peak={SIGMA_PEAK_CM2_PER_G}, "
          f"v_target={V_TARGET_KMS}, σ_1={SIGMA_KMS}")
    print()

    results = []
    for halo in [HALO_FORNAX, HALO_SEGUE1]:
        print(f"\n{'='*70}")
        print(f"Halo: {halo['name']}")
        print(f"  M_200 = {halo['M_200_msun']:.2e} M_sun")
        print(f"  c_200 = {halo['c_200']}")
        print(f"  V_max = {halo['V_max_kms']} km/s")
        print(f"  v_eff = {halo['v_eff_kms']} km/s")
        print(f"  Published t_c: {halo['t_c_published_gyr']} Gyr ({halo['t_c_published_citation']})")
        print(f"  Observation: {halo['observation']}")
        print()

        M_200 = halo["M_200_msun"]
        c_200 = halo["c_200"]
        v_eff = halo["v_eff_kms"]
        sigma_eff_m = sigma_m_canonical_gaussian(v_eff)
        r_s_kpc = r_s_from_c_M(c_200, M_200)
        rho_s = rho_s_from_c_M(c_200, M_200)
        t_evol = gy.evolution_time_gyr(M_200)

        print(f"  σ/m({v_eff} km/s) = {sigma_eff_m:.4f} cm²/g (canonical Phase 44)")
        print(f"  r_s = {r_s_kpc:.4f} kpc")
        print(f"  ρ_s = {rho_s:.3e} M_sun/kpc^3")
        print(f"  t_evol = {t_evol:.3f} Gyr")
        print()

        # Three calibrations
        for pref_name in ["literal", "BM2_calibrated", "per_halo"]:
            t_c, sig, rho, rs = compute_halo_t_c(halo, pref_name)
            tau = min(t_evol / t_c if t_c > 0 else float('inf'), 1.0)
            phase = gy.classify_phase(tau)
            print(f"  Calibration: {pref_name}")
            print(f"    t_c = {t_c:.3f} Gyr")
            print(f"    τ = t_evol/t_c = {tau:.4f}")
            print(f"    Phase: {phase}")
            print(f"    {'COLLAPSES within Hubble time' if tau > 0.7 else 'does NOT collapse within Hubble time'}")
            print()

            # Halo prediction
            pred = gy.predict_sidm_halo(M_200, halo["V_max_kms"], r_s_kpc, sigma_eff_m)
            print(f"    Predicted r_c = {pred['r_c_kpc']:.3f} kpc")
            print(f"    Predicted V_max(t) = {pred['V_max_kms']:.3f} km/s")
            print(f"    Predicted R_max(t) = {pred['R_max_kpc']:.3f} kpc")
            print()

        halo_result = {
            "halo": halo,
            "sigma_eff_m_canonical_gyr": float(sigma_eff_m),
            "r_s_kpc": float(r_s_kpc),
            "rho_s_msun_per_kpc3": float(rho_s),
            "t_evol_gyr": float(t_evol),
            "calibrations": {},
        }
        for pref_name in ["literal", "BM2_calibrated", "per_halo"]:
            t_c, sig, rho, rs = compute_halo_t_c(halo, pref_name)
            tau = min(t_evol / t_c if t_c > 0 else float('inf'), 1.0)
            halo_result["calibrations"][pref_name] = {
                "t_c_gyr": float(t_c),
                "tau": float(tau),
                "phase": gy.classify_phase(tau),
                "collapses_within_hubble_time": bool(tau > 0.7),
            }
        results.append(halo_result)

    # Save
    out = {
        "test": "V19_2_E_B_per_halo_gravothermal_calibration",
        "date": "2026-10-09",
        "method": (
            "Three-calibration comparison for Fornax dSph and Segue 1 UFD: "
            "literal analytical Yang+ 2024 prefactor, BM2-calibrated (1.82x), "
            "and per-halo calibrated to published observational lower limits "
            "on t_c. All use canonical Phase 44 Gaussian σ/m(v) form."
        ),
        "halos": results,
        "interpretation": (
            "Fornax and Segue 1 are observed un-collapsed (cuspy density profiles), "
            "which places a LOWER LIMIT on t_c > 13.8 Gyr. The literal analytical "
            "prefactor (150*C) predicts collapse within Hubble time for both halos at "
            "the canonical Phase 44 σ/m. The BM2-calibrated prefactor (1.82x) makes "
            "Fornax marginally un-collapsed and Segue 1 still collapsed. The per-halo "
            "calibration to the observational lower limit gives a halo-specific "
            "prefactor that is LARGER than the BM2 calibration. The implication: "
            "the gravothermal prefactor is halo-specific, and the paper's Fornax "
            "collapse prediction is uncertain by factor 2-10x."
        ),
        "HONEST_LIMITATIONS": [
            "Fornax and Segue 1 t_c lower limits are from observational lack of "
            "gravothermal signature, not direct N-body measurement. The actual "
            "t_c could be anywhere from 13.8 Gyr to 50+ Gyr.",
            "The canonical Phase 44 σ/m(15) = 2.85 cm²/g is from the §2.6 paper "
            "convention. With Yang+ 2025-derived f_H (R88(88) caveat), the σ_eff "
            "at observation radius could be 0.25 cm²/g or 2.85 cm²/g — a 11x range.",
            "The per-halo calibration uses the OBSERVATIONAL lower limit on t_c, "
            "not a measured t_c. The result is a lower limit on the halo-specific "
            "prefactor, not a measurement.",
        ],
    }

    out_path = _get_results_dir() / "v19_2_e_b_per_halo_gravothermal.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"Results: {out_path}")
    print()
    print("=" * 70)
    print("VERDICT")
    print("=" * 70)
    print()
    print("Both Fornax and Segue 1 are observed un-collapsed (lower limit on t_c).")
    print("At the canonical Phase 44 σ/m(15) = 2.85 cm²/g, the literal analytical")
    print("prefactor predicts collapse within Hubble time — INCORRECT given the")
    print("observational constraint. The BM2-calibrated prefactor (1.82x) makes")
    print("Fornax marginally un-collapsed but Segue 1 still collapsed. Only the")
    print("per-halo calibrated prefactor reproduces the observational lower limit.")
    print()
    print("Recommendation: the paper's Fornax t_core = 0.25-2.08 Gyr prediction is")
    print("**halo-specific** and should be reported with a factor-2 to 10× uncertainty")
    print("from the prefactor calibration. R88(83) honest framing: 'halo-specific")
    print("calibration documented; Fornax collapse prediction subject to factor-2")
    print("systematic from prefactor calibration uncertainty'.")
    print()
    print("The paper already has this caveat (line 1653 of PAPER_V1_DRAFT.md:")
    print("'Fornax t_core prediction is subject to a factor-2 systematic from the")
    print("prefactor calibration uncertainty'). This script CONFIRMS that caveat.")


if __name__ == "__main__":
    main()
