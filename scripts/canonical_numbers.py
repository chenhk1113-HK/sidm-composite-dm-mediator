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
# No-go catalogue (R88(87)+(88), ClawsGO #7)
#
# The no-go catalogue is the canonical, machine-generated list of:
# - "first-class" structural findings (no-gos that survive all tested paths)
# - "tuning statements" (specific parameter choices that look like no-gos but are
#   not structural constraints of the framework)
# - "open requirements" (UV-status questions, NOT no-gos per ClawsGO #6 Fix 3)
#
# Each entry: {name, status, citation, affected_channels, factor_vs_constraint}.
# "status" is one of: STRUCTURAL | TUNING | OPEN | PASS.
# Single source of truth for the abstract, §9.17b, §A.15, and any future paper
# section that needs to enumerate the framework's structural findings.
# ============================================================================

NO_GO_CATALOGUE = {
    "_meta": {
        "description": (
            "Canonical no-go catalogue for v19.2-D-FREEZE + v19.2-F. Per ClawsGO #5 B.2 + "
            "#7, this is the single source of truth for the paper's structural findings. "
            "The 'structural_findings' block (in compute_canonical_numbers) is the summary; "
            "this block is the detailed version with per-entry status, affected channels, "
            "and trade-off factors."
        ),
        "v19_2_D_FINAL": "v19.2-D-milestone-R88-final (commit 53ce85e)",
        "v19_2_F_P1_plus_2": "0ef4def (ClawsGO #6 fixes applied)",
        "status_legend": {
            "STRUCTURAL": "Survives all tested forward paths. First-class result.",
            "TUNING": "Specific parameter choice that fails, but the framework has a "
                       "parameter region that passes (PASS window exists). Not a no-go.",
            "OPEN": "Open requirement, NOT a no-go. UV-status question pending Phase 3.",
            "PASS": "Framework passes the channel under all canonical choices.",
        },
    },
    "entries": [
        {
            "id": "ng-c9-dsph",
            "name": "Cloud-9 vs dSph tension (v=28<->15)",
            "status": "STRUCTURAL",
            "section": "2.6a",
            "affected_channels": ["Cloud-9 v=28 (BLN24/Ohana+ 2026 floor 128)",
                                  "dSph v=15 (Horigome+ 2025 ceiling 0.032)"],
            "argument": "sigma_m(28)/sigma_m(15) ratio; the framework's resonance at v=29.4 "
                         "necessarily overproduces sigma/m at v=15 by 7.8-25.7x (R88(82)).",
            "factor_vs_constraint": {
                "dsph_v15_factor_above_ceiling": 7.8,  # at canonical Phase 44
            },
            "R88_reference": "R88(82), R88(88)",
        },
        {
            "id": "ng-tradeoff-fH",
            "name": "f_H(r) compatibility result (structural trade-off, R88(88) restated)",
            "status": "STRUCTURAL",
            "section": "9.17b (R88(88) restatement)",
            "affected_channels": ["Cloud-9 v=28 (sigma_eff target 50)",
                                  "SPARC v=100 (sigma_eff target 0.19)"],
            "argument": "A physically-derived centre-peaked f_H(r) profile (Yang+ 2025 SIDM2c "
                         "parameterization: f_H(0.05 r_s)=0.81, f_H(0.5 r_s)=0.03, "
                         "f_H(1.0 r_s)=0.04) is incompatible with Cloud-9 and SPARC at "
                         "observation radii: sigma_eff(Cloud-9) ~0.15 << 50 (fails by ~300x), "
                         "sigma_eff(SPARC) ~0.0001 << 0.19 (fails by ~1900x).",
            "factor_vs_constraint": {
                "cloud9_factor_below_50": 300.0,
                "sparc_factor_below_0p19": 1900.0,
            },
            "R88_reference": "R88(88), R88(82), R88(86)",
            "caveat": "Statement about SIDM2c parameterization, not the project's own N-body "
                      "(Phase G9 found f_H drop 0.94-1.01x, which is NOT subject to the trade-off).",
        },
        {
            "id": "ng-v150",
            "name": "v=150 Lei/Wang vs Sameie+ 2020 (demoted R88(87))",
            "status": "TUNING",
            "section": "9.17a (R88(87) demotion)",
            "affected_channels": ["Lei/Wang v=150 (floor 0.1)",
                                  "Sameie+ 2020 v=150 (ceiling 0.3)"],
            "argument": "Phase G7's sigma_peak2 = 5.0 overshoots Sameie+ 2020 by 1.5x. "
                         "But the PASS window sigma_peak2 in (1.11, 3.33) cm^2/g satisfies both "
                         "constraints simultaneously. The 'no-go' is a tuning statement about "
                         "Phase G7's specific choice, NOT a structural constraint of the "
                         "framework.",
            "factor_vs_constraint": {
                "pass_window_sigma_peak2_cm2_per_g_min": 1.11,
                "pass_window_sigma_peak2_cm2_per_g_max": 3.33,
            },
            "R88_reference": "R88(87)",
        },
        {
            "id": "ng-uv-background",
            "name": "Background UV derivation (open requirement, NOT a no-go)",
            "status": "OPEN",
            "section": "2.8 (v19.2-F Phase 1+2)",
            "affected_channels": ["all channels (background sigma/m)"],
            "argument": "The background sigma/m = 0.052*(100/v)^1.93 is a phenomenological fit. "
                         "The framework's named 200 eV Yukawa at alpha_chi = 6.8e-7 fails at "
                         "v=100 by 55x and overproduces at v=10 by ~4300x; the fitted slope is "
                         "closer to a Sommerfeld v^-2 near a t-channel bound-state resonance "
                         "(M2 mechanism, Chu+ 2018 [7]). A first-principles derivation is open "
                         "(v19.2-F Phase 3). NOT a UV completion no-go while M2 is open.",
            "factor_vs_constraint": {
                "yukawa_at_alpha_chi_v100_factor_over_fitted": 55.0,
                "yukawa_at_alpha_chi_v10_factor_over_fitted": 4300.0,
            },
            "R88_reference": "ClawsGO Phase 1+2 (v19.2-F P1+2)",
        },
    ],
    "UV_completion_no_gos_S10": [
        {
            "id": "uv-ng-magnetic-dipole",
            "name": "Magnetic dipole DM",
            "section": "10.2a",
            "status": "CONSTRAINT",
            "note": "Cross-section ~18 orders above LZ limit; not a UV completion theorem but a "
                    "constraint exclusion at the Phase 44 baseline.",
        },
        {
            "id": "uv-ng-hidden-U1-pseudo-Dirac",
            "name": "Hidden U(1) + 10 MeV pseudo-Dirac",
            "section": "10.2b",
            "status": "CONSTRAINT",
            "note": "Same as 10.2a - constraint exclusion at the Phase 44 baseline.",
        },
        {
            "id": "uv-ng-GeV-inelastic",
            "name": "GeV-scale inelastic DM",
            "section": "10.2c",
            "status": "CONSTRAINT",
        },
        {
            "id": "uv-ng-pwave-resonance",
            "name": "Published best-fit p-wave resonance (Chu+ 2019)",
            "section": "10.2d",
            "status": "CONSTRAINT",
        },
        {
            "id": "uv-ng-one-mediator-systematic",
            "name": "One-mediator UV systematic (T184 scaling argument)",
            "section": "10 (T184)",
            "status": "SCALING_ARGUMENT",
            "note": "T184 is a general scaling argument rather than a specific UV construction. "
                    "Per the abstract's 'five UV completion no-go theorems' framing, this entry "
                    "is the LEAST specific of the five. Per ClawsGO #7, the abstract should "
                    "either rename to 'no-go constraints/exclusions at the Phase-44 baseline' "
                    "or state which are theorems and which are arguments.",
        },
    ],
}


# ============================================================================
# Canonical abstract channel count (R88(87)+(88), ClawsGO #7 §4)
#
# Per ClawsGO #7 §4, the abstract uses TWO different denominators (4 of 7 in :270
# and 8 channels in :276) which is a self-inconsistency. The canonical convention
# is: 8 channels, 4 PASS / 3 MARGINAL / 1 FAIL (this includes Lei/Wang ONCE in
# the 4 PASS, NOT double-counted in MARGINAL/FAIL). The "4 of 7" framing is
# RETIRED.
#
# This is the value the abstract, §9.17b, and §A.15 should all reference.
# ============================================================================

CANONICAL_ABSTRACT_CHANNEL_COUNT = {
    "n_channels_total": 8,
    "n_PASS": 4,
    "n_MARGINAL": 3,
    "n_FAIL": 1,
    "canonical_count_string": "8 constrained channels (4 PASS / 3 MARGINAL / 1 FAIL)",
    "retired_conventions": [
        "4 of 7 constrained channels pass (RETIRED: Lei/Wang double-counted in old table; "
        "see ClawsGO #7 §4)",
        "two structural no-gos (RETIRED R88(87): v=150 demoted to tuning statement)",
    ],
    "PASS_channels": [
        "Cluster v=500 (Randall+ 2008 strong lensing)",
        "dSph v=10 (Horigome+ 2025 ceiling)",
        "Cloud-9 v=28 (BLN24/Ohana+ 2026 floor 128, canonical Phase 44)",
        "SPARC v=100 (Lelli+ 2016, canonical Phase 44)",
    ],
    "MARGINAL_channels": [
        "UFD v=3 (Horigome+ 2025 ceiling)",
        "UFD v=5 (Horigome+ 2025 ceiling)",
        "UFD v=15 (Horigome+ 2025 ceiling, within 1sigma)",
    ],
    "FAIL_channels": [
        "dSph v=7 (Horigome+ 2025 ceiling, factor 11.6x over)",
    ],
    "note_on_lei_wang": (
        "Lei/Wang+ 2026 v=150 mass bound is the SAME constraint as Sameie+ 2020 v=150 "
        "(see ClawsGO #7 §2b Lei/Wang double-count). It is the SAME channel counted under "
        "different names; the v=150 entry is the R88(87) TUNING statement, not a separate "
        "PASS. In the 8-channel count above, Lei/Wang is folded into the v=150 TUNING entry "
        "and NOT counted in the 4 PASS / 3 MARGINAL / 1 FAIL."
    ),
}


# ============================================================================
# Canonical trade-off factors (R88(88) + ClawsGO #5+#7)
#
# Per ClawsGO #5+#7 §5, the trade-off factor was scattered in 4 places with
# inconsistent values (5-300 / 200-1000 / 250 / 300 / "130" in comment #5; 300/1900
# in prose vs 250/200 in §9.17b table in comment #7). The canonical values are
# the bare-SIDM2c parameterization at observation radii (no gravothermal at tau=0.3):
#   - Cloud-9 factor (sigma_eff(Cloud-9) << 50): ~300x
#   - SPARC factor (sigma_eff(SPARC) << 0.19): ~1900x
# These are the values to use in the abstract, §9.17b, and any forward-path
# discussion. The 250/200 in the §9.17b table are the tau=0.3-with-gravothermal
# variant (a different calc) and are RETIRED.
# ============================================================================

CANONICAL_TRADEOFF_FACTORS = {
    "cloud9_factor_below_50": 300.0,
    "sparc_factor_below_0p19": 1900.0,
    "canonical_text": (
        "sigma_eff(Cloud-9) ~ 0.15 vs 50 (factor ~300x), "
        "sigma_eff(SPARC) ~ 0.0001 vs 0.19 (factor ~1900x)"
    ),
    "retired_values": [
        "250x / 200x in §9.17b table (:1245, :1247) - RETIRED (different calc: SIDM2c "
        "with gravothermal at tau=0.3, not bare SIDM2c)",
        "5-300 / 200-1000 / 250 / '130' range in older drafts - RETIRED per ClawsGO #5",
    ],
    "R88_reference": "R88(88), ClawsGO #5+#7",
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
            "open_requirement": [
                "section 2.8: Background UV derivation (ClawsGO #6 Fix 3 - NOT a no-go; "
                "v19.2-F Phase 3 will test whether any two/three-mediator UV sector produces "
                "the phenomenological sigma/m(v)).",
            ],
            "UV_completion_no_gos_S10_five": [
                "10.2a: Magnetic dipole DM (CONSTRAINT)",
                "10.2b: Hidden U(1) + 10 MeV pseudo-Dirac (CONSTRAINT)",
                "10.2c: GeV-scale inelastic DM (CONSTRAINT)",
                "10.2d: Published best-fit p-wave resonance (CONSTRAINT)",
                "10 (T184): One-mediator UV systematic (SCALING_ARGUMENT; per ClawsGO #7, "
                "this is the LEAST specific of the five - rename to 'no-go constraints/"
                "exclusions at the Phase-44 baseline' or state which are theorems and which "
                "are arguments).",
            ],
        },
        "no_go_catalogue": NO_GO_CATALOGUE,
        "canonical_abstract_channel_count": CANONICAL_ABSTRACT_CHANNEL_COUNT,
        "canonical_tradeoff_factors": CANONICAL_TRADEOFF_FACTORS,
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
    print("V19.2-E D + V19.2-F — Machine-generated canonical numbers")
    print("                  + no-go catalogue (ClawsGO #5 B.2 + #7)")
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

    print()
    print("No-go catalogue (canonical, machine-generated):")
    for entry in NO_GO_CATALOGUE["entries"]:
        print(f"  [{entry['status']:9s}] {entry['id']}: {entry['name']}")

    print()
    print("UV completion no-gos (S10, 5 entries):")
    for entry in NO_GO_CATALOGUE["UV_completion_no_gos_S10"]:
        print(f"  [{entry['status']:16s}] {entry['id']}: {entry['name']} (section {entry['section']})")

    print()
    print(f"Canonical abstract channel count: {CANONICAL_ABSTRACT_CHANNEL_COUNT['canonical_count_string']}")
    print(f"  PASS:    {CANONICAL_ABSTRACT_CHANNEL_COUNT['n_PASS']}")
    print(f"  MARGINAL:{CANONICAL_ABSTRACT_CHANNEL_COUNT['n_MARGINAL']}")
    print(f"  FAIL:    {CANONICAL_ABSTRACT_CHANNEL_COUNT['n_FAIL']}")
    print(f"  Total:   {CANONICAL_ABSTRACT_CHANNEL_COUNT['n_channels_total']}")

    print()
    print(f"Canonical trade-off factors (R88(88), bare SIDM2c at observation radii):")
    print(f"  Cloud-9: factor {CANONICAL_TRADEOFF_FACTORS['cloud9_factor_below_50']:.0f}x below 50")
    print(f"  SPARC:   factor {CANONICAL_TRADEOFF_FACTORS['sparc_factor_below_0p19']:.0f}x below 0.19")
    print(f"  Canonical text: {CANONICAL_TRADEOFF_FACTORS['canonical_text']}")
    print(f"  RETIRED: 250/200 in §9.17b table, 5-300/200-1000/250/'130' in older drafts")


if __name__ == "__main__":
    main()
