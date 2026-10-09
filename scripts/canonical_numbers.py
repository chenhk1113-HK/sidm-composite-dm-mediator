"""
V19.2-E D — Machine-generated canonical numbers (ClawsGO B.2).

Single source of truth for the headline numbers that drive the paper's
pass/fail table, the v19.2-D freeze, and the v19.2-E work.

Reads scripts/constants.py and T205 OBS_PUBLISHED, computes:
- sigma/m(v) at all 8 T205 channels using the canonical Phase 44 Gaussian
- sigma_eff(v) = F_H^2 * sigma/m(v) with canonical F_H = 0.297
- Per-channel pass/fail verdict (PASS / MARGINAL / FAIL)
- Pass/fail summary (PASS count, MARGINAL count, FAIL count)
- Trade-off factor: sigma_eff(Cloud-9) / 50 (Cloud-9 working benchmark)
- Trade-off factor: sigma_eff(SPARC) / 0.19 (SPARC observation)
- Halo-specific gravothermal prefactor (vs Yang+ 2024 150*C)

All values are derived from one place. The drift-guard script
(scripts/drift_guard.py) reads the canonical JSON and flags any
deviation in the docs (paper, README, CURRENT, FINDINGS, etc.).

This is the integration layer for v19.2-E (per ClawsGO B.2).

Reference: ClawsGO comment #5 (2026-10-09) B.2.
"""
from __future__ import annotations
import json
import math
import os
import sys
import warnings
from pathlib import Path

import numpy as np

warnings.filterwarnings("ignore")

# Make scripts/ and v0.3-prelim/code/ importable
_THIS = Path(__file__).resolve()
_REPO = _THIS.parent.parent
sys.path.insert(0, str(_REPO / "scripts"))
sys.path.insert(0, str(_REPO / "v0.3-prelim" / "code"))

from constants import (
    SIGMA_0_CM2_PER_G, A_SLOPE, V_REF_KMS,
    SIGMA_PEAK_CM2_PER_G, V_TARGET_KMS, SIGMA_KMS,
    F_H_CANONICAL,
)

from T205_full_likelihood_published import OBS_PUBLISHED

# Lazy-initialized output path
CANONICAL_OUTPUT = _REPO / "v0.3-prelim" / "data" / "results" / "canonical_numbers.json"


# ============================================================================
# Canonical sigma/m(v) form (paper section 2.6)
# ============================================================================

def sigma_m_canonical_gaussian(v_kms, sigma_0=SIGMA_0_CM2_PER_G,
                                a_slope=A_SLOPE, v_ref=V_REF_KMS,
                                sigma_peak=SIGMA_PEAK_CM2_PER_G,
                                v_target=V_TARGET_KMS, sigma_1=SIGMA_KMS):
    """Canonical Gaussian sigma/m(v) form (paper section 2.6).

    sigma/m(v) = sigma_0 * (v_ref/v)^a_slope + sigma_peak * exp(-(v - v_target)^2 / (2*sigma_1^2))
    """
    v = np.atleast_1d(np.asarray(v_kms, dtype=float))
    bg = sigma_0 * (v_ref / v) ** a_slope
    res = sigma_peak * np.exp(-((v - v_target) ** 2) / (2 * sigma_1 ** 2))
    sigma = bg + res
    return sigma if len(sigma) > 1 else float(sigma[0])


# ============================================================================
# Per-channel pass/fail (T205 convention)
# ============================================================================

def channel_verdict(sigma_eff, sigma_obs, sigma_unc, kind):
    if kind == "gaussian":
        diff = abs(sigma_eff - sigma_obs)
        if diff < sigma_unc: return "PASS"
        if diff < 2 * sigma_unc: return "MARGINAL"
        return "FAIL"
    if kind == "ceiling":
        if sigma_eff <= sigma_obs: return "PASS"
        return "MARGINAL" if (sigma_eff - sigma_obs) / sigma_unc < 1 else "FAIL"
    if kind == "floor":
        if sigma_eff >= sigma_obs: return "PASS"
        return "MARGINAL" if (sigma_obs - sigma_eff) / sigma_unc < 1 else "FAIL"
    return "FAIL"


# ============================================================================
# Trade-off factors
# ============================================================================

def cloud9_tradeoff_factor(sigma_eff_cloud9, target=50.0):
    """sigma_eff(Cloud-9) factor below the working benchmark of 50 cm^2/g.

    Returns: factor by which sigma_eff(Cloud-9) is BELOW the working benchmark.
    """
    if sigma_eff_cloud9 <= 0:
        return float('inf')
    return target / sigma_eff_cloud9


def sparc_tradeoff_factor(sigma_eff_sparc, obs=0.193):
    """sigma_eff(SPARC) factor below the SPARC observation at v=100.

    Returns: factor by which sigma_eff(SPARC) is BELOW the observation.
    """
    if sigma_eff_sparc <= 0:
        return float('inf')
    return obs / sigma_eff_sparc


def dsph_tradeoff_factor(sigma_eff_dsph, ceiling=0.032):
    """sigma_eff(dSph) factor above the Horigome+ 2025 ceiling at v=15.

    Returns: factor by which sigma_eff(dSph) is ABOVE the ceiling.
    """
    if sigma_eff_dsph <= 0:
        return 0.0
    return sigma_eff_dsph / ceiling


# ============================================================================
# Halo-specific gravothermal prefactors (v19.2-E B)
# ============================================================================

HALO_PREFACTORS = {
    "BM2 cluster": {
        "prefactor_vs_yang2024": 1.82,
        "t_c_gyr": 28.7,
        "sigma_eff_per_m": 7.1,
        "citation": "Yang+ 2024 calibration halo (R88(83) result: 1.82x to match 28.7 Gyr)",
    },
    "Cosmo-501 dwarf": {
        "prefactor_vs_yang2024": 2.2,
        "t_c_gyr": 9.04,
        "sigma_eff_per_m": 50.0,
        "citation": "Yang+ 2024 Table 1, R88(83) independent halo (under-prediction by 2.2x)",
    },
    "Fornax dSph": {
        "prefactor_vs_yang2024": 18.7,
        "t_c_gyr": ">13.8",
        "sigma_eff_per_m": 2.85,
        "citation": "v19.2-E B: Fornax dSph, M_200=1e9, c=15, v_eff=15 km/s. Prefactor must be >= 18.7x BM2 calibration to match observational lower limit on t_c.",
    },
    "Segue 1 UFD": {
        "prefactor_vs_yang2024": 4.0,
        "t_c_gyr": ">13.8",
        "sigma_eff_per_m": 6.81,
        "citation": "v19.2-E B: Segue 1 UFD, M_200=1e8, c=25, v_eff=8 km/s. Prefactor must be >= 4.0x BM2 calibration.",
    },
}


# ============================================================================
# Main: compute canonical numbers and write JSON
# ============================================================================

def compute_canonical_numbers():
    """Compute all canonical numbers and return as a dict."""
    canonical = {
        "_meta": {
            "description": (
                "Canonical headline numbers for v19.2-D-FREEZE + v19.2-E work. "
                "Computed from scripts/constants.py (Phase 44 free fit) + T205 OBS_PUBLISHED. "
                "Single source of truth for paper pass/fail table, trade-off factors, "
                "and gravothermal halo-specific prefactors."
            ),
            "commit_at_freeze": "v19.2-D-FREEZE = 53ce85e (R88(82)+(83)+(84)+(85)+(86)+(87)+(88))",
            "v19_2_E_commits": [
                "A.1 = 01c5615 (real-likelihood promotion, 1/8 at canonical Phase 44)",
                "A.2 = 1863063 (5-param DE best-fit, 5/8 PASS)",
                "B   = f05a871 (per-halo gravothermal calibration, Fornax + Segue 1)",
                "C   = dba12e1 (data-only sigma/m(v) constraint, 2/4 PASS)",
                "D   = THIS FILE (machine-generated canonical numbers)",
            ],
            "constants_source": "scripts/constants.py (F_H_CANONICAL = 0.297 added R88(82) A.1)",
            "channels_source": "T205_full_likelihood_published.OBS_PUBLISHED (8 channels with published sigma_unc)",
        },
        "v19_2_D_canonical_phase_44_free_fit": {
            "sigma_0": SIGMA_0_CM2_PER_G,
            "a_slope": A_SLOPE,
            "v_ref": V_REF_KMS,
            "sigma_peak": SIGMA_PEAK_CM2_PER_G,
            "v_target": V_TARGET_KMS,
            "sigma_1": SIGMA_KMS,
            "F_H": F_H_CANONICAL,
            "interpretation": (
                "Paper canonical Gaussian sigma/m(v) per section 2.6. sigma_peak=174 is "
                "the CAUSALITY CAP (not the Phase 44 free-fit value 178.5; per R88(76))."
            ),
        },
        "v19_2_E_A2_5param_DE_best_fit": {
            "sigma_0": 0.0265,
            "a_slope": 1.198,
            "sigma_peak": 2025.57,
            "v_target": 28.47,
            "sigma_1": 1.20,
            "F_H": F_H_CANONICAL,
            "logL": -7.29,
            "interpretation": (
                "5-param DE best-fit to 8-channel T205 published-sigma_unc likelihood. "
                "Wider prior (sigma_peak up to 5000). Found 5 of 8 channels PASS (2 MARGINAL, 1 FAIL). "
                "sigma_peak=2026 is 12x the v19.2-D canonical 174, at the upper edge of the prior."
            ),
        },
        "per_channel_at_v19_2_D_canonical": {},
        "per_channel_at_v19_2_E_A2_best_fit": {},
        "pass_fail_summary_v19_2_D_canonical": {},
        "pass_fail_summary_v19_2_E_A2_best_fit": {},
        "tradeoff_factors_v19_2_D_canonical": {},
        "tradeoff_factors_v19_2_E_A2_best_fit": {},
        "halo_specific_gravothermal_prefactors": HALO_PREFACTORS,
        "structural_findings_v19_2_D_freeze": {
            "first_class": [
                "section 2.6a: Cloud-9 vs dSph tension at v=28<->15 (ratio argument)",
                "section 9.17b: f_H(r) compatibility result (R88(88) restated; "
                "SIDM2c parameterization caveat, not the project's own N-body)",
            ],
            "tuning_statement": [
                "section 9.17a: v=150 entry demoted from structural no-go to "
                "tuning statement (R88(87)). Phase G7 sigma_peak2 = 5.0 overshoots "
                "Sameie+ 2020 by 1.5x; smaller sigma_peak2 in (1.11, 3.33) cm^2/g "
                "satisfies both constraints.",
            ],
        },
    }

    for label, params in [
        ("v19_2_D_canonical", (SIGMA_0_CM2_PER_G, A_SLOPE, V_REF_KMS,
                                 SIGMA_PEAK_CM2_PER_G, V_TARGET_KMS, SIGMA_KMS)),
        ("v19_2_E_A2_best_fit", (0.0265, 1.198, V_REF_KMS, 2025.57, 28.47, 1.20)),
    ]:
        per_channel = []
        pass_count = marginal_count = fail_count = 0
        for v, sigma_obs, sigma_unc, kind, label_str, citation in OBS_PUBLISHED:
            sigma_HH = float(sigma_m_canonical_gaussian(v, *params))
            sigma_eff = F_H_CANONICAL ** 2 * sigma_HH
            verdict = channel_verdict(sigma_eff, sigma_obs, sigma_unc, kind)
            if verdict == "PASS": pass_count += 1
            elif verdict == "MARGINAL": marginal_count += 1
            else: fail_count += 1
            per_channel.append({
                "v_kms": float(v),
                "label": label_str,
                "kind": kind,
                "sigma_obs": float(sigma_obs),
                "sigma_unc": float(sigma_unc),
                "sigma_HH_at_v": float(sigma_HH),
                "sigma_eff": float(sigma_eff),
                "verdict": verdict,
                "citation": citation,
            })
        canonical[f"per_channel_at_{label}"] = per_channel
        canonical[f"pass_fail_summary_{label}"] = {
            "PASS": pass_count,
            "MARGINAL": marginal_count,
            "FAIL": fail_count,
            "canonical_count_string": f"{pass_count} of {len(per_channel)} channels pass",
        }

    # Trade-off factors
    for label, params in [
        ("v19_2_D_canonical", (SIGMA_0_CM2_PER_G, A_SLOPE, V_REF_KMS,
                                 SIGMA_PEAK_CM2_PER_G, V_TARGET_KMS, SIGMA_KMS)),
        ("v19_2_E_A2_best_fit", (0.0265, 1.198, V_REF_KMS, 2025.57, 28.47, 1.20)),
    ]:
        sigma_eff_cloud9 = float(sigma_m_canonical_gaussian(28.0, *params)) * F_H_CANONICAL ** 2
        sigma_eff_sparc = float(sigma_m_canonical_gaussian(100.0, *params)) * F_H_CANONICAL ** 2
        sigma_eff_dsph = float(sigma_m_canonical_gaussian(15.0, *params)) * F_H_CANONICAL ** 2
        sigma_eff_ufd3 = float(sigma_m_canonical_gaussian(3.0, *params)) * F_H_CANONICAL ** 2
        canonical[f"tradeoff_factors_{label}"] = {
            "cloud9_factor_below_50": float(cloud9_tradeoff_factor(sigma_eff_cloud9)),
            "sparc_factor_below_0p19": float(sparc_tradeoff_factor(sigma_eff_sparc)),
            "dsph_v15_factor_above_ceiling": float(dsph_tradeoff_factor(sigma_eff_dsph)),
            "ufd_v3_factor_above_ceiling": float(dsph_tradeoff_factor(sigma_eff_ufd3, ceiling=0.155)),
        }

    return canonical


def main():
    print("=" * 70)
    print("V19.2-E D — Machine-generated canonical numbers (ClawsGO B.2)")
    print("=" * 70)
    print()
    print(f"F_H canonical = {F_H_CANONICAL}")
    print(f"Phase 44 free fit: sigma_0={SIGMA_0_CM2_PER_G}, a_slope={A_SLOPE}, "
          f"sigma_peak={SIGMA_PEAK_CM2_PER_G}, v_target={V_TARGET_KMS}, sigma_1={SIGMA_KMS}")
    print()

    canonical = compute_canonical_numbers()

    # Write JSON
    CANONICAL_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(CANONICAL_OUTPUT, "w") as f:
        json.dump(canonical, f, indent=2, default=float)
    print(f"Canonical numbers written to: {CANONICAL_OUTPUT}")
    print()

    # Print summary
    for label in ["v19_2_D_canonical", "v19_2_E_A2_best_fit"]:
        print(f"\n{label}:")
        s = canonical[f"pass_fail_summary_{label}"]
        print(f"  PASS: {s['PASS']}, MARGINAL: {s['MARGINAL']}, FAIL: {s['FAIL']}")
        print(f"  Headline: {s['canonical_count_string']}")
        t = canonical[f"tradeoff_factors_{label}"]
        print(f"  Cloud-9 factor below 50: {t['cloud9_factor_below_50']:.1f}x")
        print(f"  SPARC factor below 0.19: {t['sparc_factor_below_0p19']:.1f}x")
        print(f"  dSph v=15 factor above ceiling: {t['dsph_v15_factor_above_ceiling']:.1f}x")
        print(f"  UFD v=3 factor above ceiling: {t['ufd_v3_factor_above_ceiling']:.1f}x")

    print()
    print("Halo-specific gravothermal prefactors (vs Yang+ 2024 150*C):")
    for halo, data in HALO_PREFACTORS.items():
        print(f"  {halo}: {data['prefactor_vs_yang2024']}x")


if __name__ == "__main__":
    main()
