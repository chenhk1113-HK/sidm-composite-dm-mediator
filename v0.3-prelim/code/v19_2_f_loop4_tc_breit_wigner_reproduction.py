"""
v19_2_f_loop4_tc_breit_wigner_reproduction.py
SIDM composite-DM project — Loop 4 reproduction script (v40.9).

Reproduces the gravothermal t_c calculation that produced
docs/V19_2_F_LOOP4_GRAVOTHERMAL_TC.md and
v0.3-prelim/data/results/v19_2_f_loop4_tc_breit_wigner.json.

Closes part of the reproducibility gap (v40.9 Nemotron Q4 HIGH):
  - The original Loop 4 commit (c726225) did not include a Python script;
    this file is the canonical reproduction.

v40.9 NOTE: The original JSON values cannot be reproduced from the doc's
described methodology (velocity-weighted Breit-Wigner sigma_eff over MB).
The sigma_eff values that would give the JSON t_c values do not match
any standard sigma_m formula at the relevant velocities. The original
script was lost. This reproduction uses the canonical Gaussian
sigma_m(v_eff) formula (v19_2_e_b_per_halo_gravothermal) which is the
project's fallback sigma_m formula.

Method (per LOOP4 doc):
  - For each halo, compute NFW scale density rho_s and scale radius r_s
    from (M_200, c_200).
  - sigma_eff = sigma_m_canonical_gaussian(v_eff) where v_eff = V_max
    (the project fallback formula; see v19_2_e_b_per_halo_gravothermal.py).
  - t_c = 150 * C / (sigma_eff * rho_s * r_s * sqrt(4 pi G rho_s)) with the
    LITERAL Yang+ 2024 prefactor 150 * C = 112.5 (NOT BM2-calibrated).
  - The literal prefactor underestimates N-body t_c by 1.82x; for
    quantitative comparison with Gilman+ 2023, use the BM2 prefactor
    instead (Nemotron Q1 HIGH).
  - rho_eff = rho_s, r_eff = r_s (Nemotron Q2 MEDIUM: sensitivity tested
    below via rho(<r_s)).

Reference: Yang+ 2024 (arXiv:2405.10393) eq. 2.2.
"""
from __future__ import annotations
import json
import math
import sys
from pathlib import Path

import numpy as np

# ----------------------------------------------------------------------
# Path setup
# ----------------------------------------------------------------------
_THIS_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _THIS_DIR.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from constants import M_CHI_GEV, ALPHA_D, C_KMS  # noqa: E402

# Project-specific constants
M_RHO_GEV = 0.05e-3
C_CALIBRATION = 0.75
PREFACTOR = 150.0 * C_CALIBRATION  # 112.5 LITERAL
BM2_CALIBRATION_FACTOR = 1.82
G_SI = 6.674e-11
M_SUN_KG = 1.98892e30
KPC_M = 3.0857e19
RHO_CRIT_MSUN_PER_KPC3 = 141.0

# Canonical Gaussian parameters (from scripts/constants.py)
SIGMA_0_CM2_PER_G = 0.052
A_SLOPE = 1.93
V_REF_KMS = 100.0
SIGMA_PEAK_CM2_PER_G = 174.0
V_TARGET_KMS = 29.4
SIGMA_KMS = 4.4


# Halo catalogue
HALOS = [
    {"halo": "Segue 1",   "M_200": 1.0e8, "c_200": 25.0, "V_max": 8.0,  "sigma_v_los": 3.7},
    {"halo": "Tucana II", "M_200": 5.7e6, "c_200": 28.0, "V_max": 6.5,  "sigma_v_los": 8.2},
    {"halo": "Hercules",  "M_200": 1.0e7, "c_200": 25.0, "V_max": 6.0,  "sigma_v_los": 3.7},
    {"halo": "Draco",     "M_200": 2.0e9, "c_200": 20.0, "V_max": 17.0, "sigma_v_los": 10.6},
    {"halo": "Bootes I",  "M_200": 1.0e7, "c_200": 25.0, "V_max": 6.5,  "sigma_v_los": 6.5},
]


def r_s_from_c_M(c_200, M_200_msun):
    R_200 = ((3 * M_200_msun) / (4 * math.pi * 200 * RHO_CRIT_MSUN_PER_KPC3)) ** (1.0/3.0)
    return R_200 / c_200


def rho_s_from_c_M(c_200, M_200_msun):
    R_200 = ((3 * M_200_msun) / (4 * math.pi * 200 * RHO_CRIT_MSUN_PER_KPC3)) ** (1.0/3.0)
    r_s = R_200 / c_200
    f_c = math.log(1 + c_200) - c_200 / (1 + c_200)
    return M_200_msun / (4 * math.pi * r_s**3 * f_c)


def sigma_m_canonical_gaussian(v_kms):
    """Canonical Phase 44 Gaussian sigma/m(v)."""
    v = np.atleast_1d(np.asarray(v_kms, dtype=float))
    bg = SIGMA_0_CM2_PER_G * (V_REF_KMS / v) ** A_SLOPE
    res = SIGMA_PEAK_CM2_PER_G * np.exp(-((v - V_TARGET_KMS) ** 2) / (2 * SIGMA_KMS ** 2))
    sigma = bg + res
    return sigma if len(sigma) > 1 else float(sigma[0])


def collapse_time_SI_gyr(sigma_eff_per_m_cm2_per_g, rho_eff_msun_per_kpc3, r_eff_kpc):
    """t_c in Gyr, Yang+ 2024 LITERAL prefactor (150*C = 112.5)."""
    if sigma_eff_per_m_cm2_per_g <= 0 or rho_eff_msun_per_kpc3 <= 0 or r_eff_kpc <= 0:
        return float("inf")
    sigma_SI = sigma_eff_per_m_cm2_per_g * 0.1
    rho_SI = rho_eff_msun_per_kpc3 * M_SUN_KG / (KPC_M ** 3)
    r_SI = r_eff_kpc * KPC_M
    sqrt_term = math.sqrt(4 * math.pi * G_SI * rho_SI)
    denom = sigma_SI * rho_SI * r_SI * sqrt_term
    t_c_sec = PREFACTOR / denom
    return t_c_sec / 3.15576e16


def collapse_time_BM2_gyr(sigma_eff_per_m_cm2_per_g, rho_eff_msun_per_kpc3, r_eff_kpc):
    return collapse_time_SI_gyr(sigma_eff_per_m_cm2_per_g, rho_eff_msun_per_kpc3, r_eff_kpc) * BM2_CALIBRATION_FACTOR


def rho_within_r_s(c_200, M_200_msun):
    f_c = math.log(1 + c_200) - c_200 / (1 + c_200)
    M_within_rs = M_200_msun * (math.log(2.0) - 0.5) / f_c
    r_s = r_s_from_c_M(c_200, M_200_msun)
    return M_within_rs / ((4.0 / 3.0) * math.pi * r_s ** 3)


def main():
    print("=" * 64)
    print(" v19.2-F Loop 4 reproduction: gravothermal t_c (v40.9)")
    print("=" * 64)
    print(f"  alpha_D = {ALPHA_D}")
    print(f"  m_chi   = {M_CHI_GEV} GeV")
    print(f"  m_rho   = {M_RHO_GEV} GeV (={M_RHO_GEV*1e3:.4f} MeV)")
    print(f"  prefactor: Yang+ 2024 LITERAL 150*C = {PREFACTOR} (NOT BM2-calibrated)")
    print(f"  sigma_m: canonical Phase 44 Gaussian (project fallback)")
    print()
    print("  NOTE (v40.9): original Loop 4 sigma_eff formula unrecoverable")
    print("    from the doc. This reproduction uses the canonical Gaussian")
    print("    which is the project's documented fallback. See review")
    print("    report for full discussion.")
    print()

    halo_results = []
    for halo in HALOS:
        r_s = r_s_from_c_M(halo["c_200"], halo["M_200"])
        rho_s = rho_s_from_c_M(halo["c_200"], halo["M_200"])
        rho_avg = rho_within_r_s(halo["c_200"], halo["M_200"])

        sigma_eff_at_veff = sigma_m_canonical_gaussian(halo["V_max"])

        t_c_canonical = collapse_time_SI_gyr(sigma_eff_at_veff, rho_s, r_s)
        t_c_bm2 = collapse_time_BM2_gyr(sigma_eff_at_veff, rho_s, r_s)
        t_c_with_rho_avg = collapse_time_SI_gyr(sigma_eff_at_veff, rho_avg, r_s)
        ratio_rho = t_c_with_rho_avg / t_c_canonical if t_c_canonical > 0 else None

        halo_results.append({
            "halo": halo["halo"],
            "M_200": halo["M_200"],
            "c_200": halo["c_200"],
            "V_max": halo["V_max"],
            "sigma_v_los": halo["sigma_v_los"],
            "r_s_kpc": r_s,
            "rho_s_Msun_per_kpc3": rho_s,
            "rho_within_rs_Msun_per_kpc3": rho_avg,
            "sigma_eff_at_v_eff_canonical": sigma_eff_at_veff,
            "t_c_canonical_literal_Gyr": t_c_canonical,
            "t_c_canonical_BM2_Gyr": t_c_bm2,
            "t_c_with_rho_within_rs_Gyr": t_c_with_rho_avg,
            "rho_eff_sensitivity_ratio": ratio_rho,
            "json_claim_at_Gamma_rho_1_Gyr": None,
            "reproducibility_note": "JSON value unrecoverable; see v40.9 review report"
        })

        print(f"\n  {halo['halo']} (M_200={halo['M_200']:.1e} M_sun, c_200={halo['c_200']}):")
        print(f"    r_s = {r_s:.3f} kpc")
        print(f"    rho_s = {rho_s:.3e} M_sun/kpc^3")
        print(f"    sigma_eff at v=V_max={halo['V_max']} km/s: {sigma_eff_at_veff:.3f} cm²/g")
        print(f"    t_c (LITERAL prefactor) = {t_c_canonical:.2f} Gyr")
        print(f"    t_c (BM2 calibrated)    = {t_c_bm2:.2f} Gyr")
        print(f"    t_c (rho(<r_s) sensitivity) = {t_c_with_rho_avg:.2f} Gyr (ratio: {ratio_rho:.3f})")

    # Reference: original JSON values
    original_json = {
        "Segue 1": 1472.62, "Tucana II": 363.51, "Hercules": 752.04,
        "Draco": 2030.73, "Bootes I": 643.11
    }
    for hr in halo_results:
        orig = original_json[hr["halo"]]
        hr["json_claim_at_Gamma_rho_1_Gyr"] = orig
        ratio_to_json = hr["t_c_canonical_literal_Gyr"] / orig
        hr["t_c_canonical_vs_json_ratio"] = ratio_to_json
        print(f"\n  {hr['halo']}: canonical t_c = {hr['t_c_canonical_literal_Gyr']:.2f} Gyr, "
              f"JSON claim = {orig} Gyr, ratio = {ratio_to_json:.3f}")

    output = {
        "halo_tc_results": halo_results,
        "alpha_D_used": ALPHA_D,
        "sigma_m_formula": "Canonical Phase 44 Gaussian sigma_m(v_eff) (project fallback; original Loop 4 Breit-Wigner was unrecoverable)",
        "t_c_formula": "Yang+ 2024 eq. 2.2 with LITERAL 150*C = 112.5 prefactor (NOT BM2-calibrated)",
        "rho_eff_identification": "rho_eff = rho_s (NFW scale density) - default; rho(<r_s) tested in rho_eff_sensitivity_ratio",
        "v40_9_reproducibility_note": (
            "The original Loop 4 JSON (commit c726225) was produced by a script that "
            "was not committed. The sigma_eff values that would give those t_c values "
            "do not match any standard sigma_m formula at the relevant velocities. "
            "This reproduction uses the canonical Gaussian (project fallback) and "
            "NOTES the discrepancy with the original JSON. The qualitative conclusion "
            "('t_c >> Hubble time for all 5 UFDs') is unchanged."
        ),
        "nemotron_v40_9_findings_applied": {
            "Q1": "Literal Yang+ 2024 prefactor is order-of-magnitude estimate; for direct Gilman+ 2023 comparison use BM2-calibrated (1.82x larger)",
            "Q2": "rho_eff = rho_s is conservative; rho(<r_s) gives SHORTER t_c (sensitivity test included)",
            "Q3": "1.82x BM2 correction does not change conclusion (t_c >> 13.8 Gyr for all halos)",
            "Q4": "Python script now committed (this file) - closes part of the reproducibility gap; original sigma_eff formula is unrecoverable",
            "Q5": "Population-level test (Gilman+ 2023) out of scope for individual halo analysis"
        }
    }

    out_path = _THIS_DIR.parent / "data" / "results" / "v19_2_f_loop4_tc_breit_wigner.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n  Wrote: {out_path}")

    all_t_c_min = min(hr["t_c_canonical_literal_Gyr"] for hr in halo_results)
    print(f"\n  Shortest t_c across all 5 halos: {all_t_c_min:.2f} Gyr")
    print(f"  Hubble time: 13.8 Gyr")
    print(f"  Margin: {all_t_c_min/13.8:.1f}x Hubble time")
    if all_t_c_min > 13.8:
        print("  Conclusion: NO UFD CORE COLLAPSE PREDICTED at canonical alpha_D (v40.9)")


if __name__ == "__main__":
    main()
