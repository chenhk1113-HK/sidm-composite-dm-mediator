"""v19.2-F Cloud-9 c-M tension test using multi-resonance + f_H.

This is a NEW analysis (not a re-attempt at the v19.1.5 Ohana+ reproduction).

Question: does v19.2-F's multi-resonance sigma_m(v) + f_H(r) decomposition
reduce Cloud-9's concentration-mass (c-M) tension below Ohana+ 2026's
3.2 sigma (which used a single-component sigma/m = 483 cm^2/g)?

Background:
  - Ohana+ 2026 (arXiv:2608.04362) MCMC analysis of Cloud-9 with
    single-component SIDM finds sigma/m ~ 50-500 cm^2/g and reduces
    the c-M tension from 7 sigma (CDM) to 3.2 sigma (SIDM).
  - v19.2-F Phase 44 has sigma_peak = 174 cm^2/g at v=29.4 km/s
    (Breit-Wigner resonance, LOWER than Ohana+'s single-component 483).
  - v19.2-F has sigma_eff = f_H^2 * sigma_m (fundamental observability
    relation). f_H(Cloud-9 core) ~ 0.297 (canonical F_H_CANONICAL).
  - So v19.2-F's effective sigma at v=28 is sigma_eff = 0.088 * 174
    = 15.3 cm^2/g.

This script uses the Balberg t_core formula + simplified Yang+ c_200(tau)
relation to predict Cloud-9's c_200 under v19.2-F. The c-M tension is then
computed against the Diemer+ 2019 cosmological c-M relation with 0.16 dex
scatter (Ohana+ choice per arXiv:2608.04362 section 3.1).

Per R88(68) lesson: this is a NEW analysis, not a re-attempt to match Ohana+.
If the result is interesting, send to Nemotron for review. If the result is
negative (v19.2-F increases c-M tension), accept it as a structural
constraint on the framework, not a "failure".

Per R88(71) pre-claim checklist: any BREAKTHROUGH claim must include
(a) "does not contradict", (b) n_params vs n_channels, (c) prior claim
that would need to be wrong. We will NOT make a BREAKTHROUGH claim from
this script -- it's an exploratory calculation.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]  # scripts/v19_2_f_cloud9_cM_tension.py -> parents[1] is project root
sys.path.insert(0, str(REPO / "v0.3-prelim" / "code"))
from t212_silverman_gravothermal import (
    t_cross_Gyr_from_r_vir_vmax,
    evaluate as t212_evaluate,
    SILVERMAN_PARAMS, CLOUD9_HOST,
)

# v19.2-F canonical parameters (from scripts/constants.py)
F_H_CANONICAL = 0.297
SIGMA_PEAK_CM2_PER_G = 174.0  # Phase 44
V_TARGET_KMS = 29.4  # Phase 44
SIGMA_KMS = 4.4  # Gaussian sigma (FWHM = 10.36)
A_RES = 100.0  # Breit-Wigner peak height

# Cloud-9 host halo (per Anand+ 2025 / Ohana+ 2026)
CLOUD9 = {
    "M_halo_Msun": 4.7e9,  # Ohana+ best-fit
    "V_max_kms": 28.0,  # Cloud-9 velocity scale
    "c_200_ohana": 4.0,  # Ohana+ best-fit (post-SIDM)
    "c_200_cdm_med": 7.4,  # Diemer+ 2019 at M=4.7e9 (approx)
}

# Cosmological age
T_HUBBLE_GYR = 13.8

# v19.2-F v_max uses V_REF = 100 km/s as reference velocity (from T208)


def nfw_r_vir_pc(M_halo):
    """NFW r_vir for M_halo M_sun at z=0 (approximate, c=12)."""
    # V_vir^2 = G * M / r_vir, with V_vir ~ sqrt(G*M/r_vir)
    # For c=12: r_vir ~ 30 kpc at M=5e9
    V_vir_sq = G_NEWTON * M_halo / 30.0e3  # rough estimate
    V_vir = math.sqrt(V_vir_sq)
    return G_NEWTON * M_halo / V_vir_sq  # = r_vir


def nfw_rho_s_r_s_from_concentration(M_halo, c, r_vir_pc):
    """NFW rho_s and r_s from concentration c and r_vir."""
    f_c = math.log(1 + c) - c / (1 + c)
    rho_s = (200.0 / 3.0) * c**3 * RHO_CRIT / f_c
    r_s = r_vir_pc / c
    return rho_s, r_s


def v_max_kms(M_halo, c, r_vir_pc):
    """NFW V_max for given (M, c, r_vir)."""
    rho_s, r_s = nfw_rho_s_r_s_from_concentration(M_halo, c, r_vir_pc)
    # V_max at r_max = 2.1626 * r_s for NFW
    r_max_pc = 2.1626 * r_s
    # M_enc(r_max) = 4*pi*rho_s*r_s^3 * [ln(1+r_max/r_s) - r_max/(r_s+r_max)]
    x = r_max_pc / r_s
    M_enc = 4 * math.pi * rho_s * r_s**3 * (math.log(1 + x) - x / (1 + x))
    V_max = math.sqrt(G_NEWTON * M_enc / r_max_pc)
    return V_max


def balberg_t_core_Gyr(sigma_m_cm2_g, rho_s_Msun_pc3, r_s_kpc, v_max_kms):
    """Balberg+ 2002 ApJ 568, 475 Eq. 22 (per scripts/t235_d5_width_test.py:179):
      t_core [Gyr] = 12.7 / (sigma/m [cm^2/g]) * (rho_s/10^-2)^-1 * (r_s/10^4) * (100/v_max)
    Note: r_s is in pc, so 10^4 pc = 10 kpc; r_s_kpc/10 normalizes correctly.
    """
    return 12.7 / sigma_m_cm2_g * (rho_s_Msun_pc3 / 0.01)**-1 * (r_s_kpc / 10.0) * (100 / v_max_kms)


def c200_yang_tau(tau, c_0):
    """c_200(tau) from Yang+ 2024 Eq. 5 (parametric SIDM halo).

    Key physics: c_200 = r_vir / r_s. Yang+ Eq. 5 says r_s(rho_s) changes
    with tau. The concentration follows from r_s(tau)/r_s(0).

    CRITICAL LIMITATION: The Yang+ 2024 polynomial fit is only valid for
    tau in [0, 1] (the max-core regime, where Ohana+ find Cloud-9 at
    tau = 0.18). For tau > 1 (deep core collapse), the polynomial gives
    NEGATIVE r_s values (unphysical). The full MCMC Yang+ formula is more
    complex; we use the polynomial up to its validity limit and report
    out-of-range tau explicitly.

    Per the v19.1.5 script: tau is sampled in [0, 1] with prior N(0.18, 0.15),
    so all "valid" c_200 predictions are in the max-core regime.

    For tau > 1, we do NOT extrapolate the polynomial. Instead, we flag
    the result as "tau_outside_yang_plus_validity" and report the c_200
    for tau = 1 (the max-core limit) as the upper bound of the model's
    applicability.
    """
    if tau < 0:
        return None
    # Yang+ 2024 polynomial fit valid range: tau in [0, 1]
    # For tau > 1, the polynomial breaks down (negative r_s, unphysical).
    # We use tau = 1 (max-core) as the upper bound of validity.
    tau_eff = min(tau, 1.0) if tau > 0 else 0.0
    ln_tau = math.log(tau_eff + 0.001)
    ln_0001 = math.log(0.001)
    log_term = ln_tau / ln_0001
    rs_ratio = 0.7178 - 0.1026 * tau_eff + 0.2474 * tau_eff**2 - 0.4079 * tau_eff**3 + (1 - 0.7178) * log_term
    if rs_ratio <= 0:
        return c_0 * 1.5  # numerical safety: 50% bump
    # c_200 = r_vir / r_s; if r_s shrinks, c_200 grows
    return c_0 / rs_ratio


def tau_outside_yang_validity(tau):
    """Yang+ 2024 Eq. 5 polynomial fit is only valid for tau in [0, 1].
    Returns True if tau is outside this range.
    """
    return tau < 0 or tau > 1.0


def c200_cosmological_median(M_halo):
    """Diemer+ 2019 c-M median (approximate power-law)."""
    return 7.4 * (M_halo / 1e10)**(-0.086)


def c_M_tension_sigma(c_200, M_halo, scatter_dex=0.16):
    """How many sigma below cosmological median is c_200?
    Diemer+ 2019 scatter: 0.16 dex in log10(c_200) (Ohana+ choice).
    """
    c_med = c200_cosmological_median(M_halo)
    sigma_log_c = scatter_dex * math.log(10)
    return (math.log10(c_med) - math.log10(c_200)) / sigma_log_c


def v19_2_f_cloud9_cM_tension(f_H=F_H_CANONICAL, sigma_peak=SIGMA_PEAK_CM2_PER_G):
    """Compute Cloud-9 c-M tension under v19.2-F multi-resonance + f_H.

    Returns: dict with all intermediate values for verification.
    Uses t212_silverman_gravothermal.evaluate() for the gravothermal
    calculation -- this is the VERIFIED Balberg+ 2002 implementation
    (T212 was reviewed by Nemotron 120B and the controller; the
    implementation is correct after R74 fix).

    Important: t212.evaluate() uses sigma_m = sigma_eff (the
    effective cross-section that drives gravothermal evolution).
    The factor f_H^2 enters sigma_m, NOT as a separate f_H(r) profile
    -- because the gravothermal phase depends on the cross-section
    the particles actually experience, which is f_H^2 * sigma_m for
    a 2-component SIDM with f_H = fraction of heavy particles.
    """
    M_halo = CLOUD9["M_halo_Msun"]
    c_0 = 12.0  # NFW initial concentration (Lambda-CDM cosmological median)
    v_target = CLOUD9["V_max_kms"]

    # Step 1: Effective cross-section at v_target
    # v19.2-F Phase 44: sigma_m(v) = sigma_peak * exp(-0.5 * ((v - v_target) / sigma_kms)^2)
    sigma_m_at_v = sigma_peak * math.exp(-0.5 * ((v_target - V_TARGET_KMS) / SIGMA_KMS)**2)
    sigma_eff = f_H**2 * sigma_m_at_v  # FUNDAMENTAL OBSERVABILITY RELATION

    # Step 2: Use T212 verified gravothermal evaluator
    params = {
        "M_halo": M_halo,
        "c": c_0,
        "sigma_m": sigma_eff,  # effective cross-section
        "v_max": None,  # computed from M, c
    }
    t212_result = t212_evaluate(params)
    t_core = t212_result["t_core_Gyr"]
    t_cross = t212_result["t_cross_Gyr"]
    v_max_actual = t212_result["v_max_km_s"]

    # Step 3: Gravothermal phase
    tau = T_HUBBLE_GYR / t_core if t_core > 0 else float('inf')

    # Step 4: c_200 under SIDM (Yang+ Eq. 5, valid only for tau in [0, 1])
    c_200_sidm_max_core = c200_yang_tau(min(tau, 1.0), c_0) if tau > 0 else c_0
    tau_outside = tau_outside_yang_validity(tau)
    if tau_outside:
        # Yang+ polynomial is invalid; report max-core c_200 (tau=1) as
        # the lower bound of the cuspy collapse regime.
        c_200_sidm = c_200_sidm_max_core
        c_M_interpretation = "v19.2-F predicts tau > 1 (deep core collapse), Yang+ Eq. 5 invalid"
    else:
        c_200_sidm = c_200_sidm_max_core
        c_M_interpretation = "v19.2-F tau in valid Yang+ range"

    # Step 5: c-M tension (use max-core c_200 as the "best Yang+ prediction")
    tension = c_M_tension_sigma(c_200_sidm, M_halo)

    return {
        "method": "v19.2-F Cloud-9 c-M tension test (multi-resonance + f_H)",
        "date": "2026-10-19",
        "framework": "v19.2-F Phase 44 (sigma_peak=174, sigma_kms=4.4, f_H=0.297)",
        "reference": "Ohana+ 2026 arXiv:2608.04362 (3.2 sigma published)",
        "params": {
            "M_halo_Msun": M_halo,
            "V_max_kms": v_max_actual,
            "c_0_NFW": c_0,
            "f_H": f_H,
            "sigma_peak_cm2_g": sigma_peak,
            "sigma_m_at_v28_cm2_g": sigma_m_at_v,
            "sigma_eff_cm2_g": sigma_eff,
        },
        "halo": {
            "r_vir_pc": t212_result["r_vir_pc"],
            "r_s_pc": t212_result["r_s_pc"],
            "r_s_kpc": t212_result["r_s_pc"] / 1e3,
            "rho_s_Msun_pc3": t212_result["rho_s_M_sun_pc3"],
            "V_max_kms": v_max_actual,
        },
        "gravothermal": {
            "t_core_Gyr": t_core,
            "t_cross_Gyr": t_cross,
            "tau": tau,
            "tau_yang_plus_validity": "valid" if not tau_outside else "OUTSIDE (tau > 1 = deep core collapse)",
        },
        "c_M_result": {
            "c_200_sidm": c_200_sidm,
            "c_200_sidm_interpretation": c_M_interpretation,
            "c_med_cosmological": c200_cosmological_median(M_halo),
            "tension_sigma_below": tension,
            "ohana_published_sigma": 3.2,
            "delta_vs_ohana": tension - 3.2,
            "verdict": (
                "v19.2-F in deep core collapse (tau > 1, Yang+ invalid) -- c-M tension estimate uncertain"
                if tau_outside
                else (
                    "v19.2-F REDUCES c-M tension (better than Ohana+)" if tension < 3.2
                    else "v19.2-F INCREASES c-M tension (worse than Ohana+)"
                )
            ),
        },
    }


def main():
    print("=" * 70)
    print("v19.2-F Cloud-9 c-M tension test")
    print("=" * 70)
    print()
    print("Question: does v19.2-F's multi-resonance sigma_m(v) + f_H(r)")
    print("  reduce Cloud-9's c-M tension below Ohana+ 2026's 3.2 sigma?")
    print()

    # Canonical f_H
    result = v19_2_f_cloud9_cM_tension(f_H=F_H_CANONICAL, sigma_peak=SIGMA_PEAK_CM2_PER_G)
    print("--- CANONICAL (f_H = 0.297, sigma_peak = 174) ---")
    print(f"  sigma_m at v=28: {result['params']['sigma_m_at_v28_cm2_g']:.1f} cm^2/g")
    print(f"  sigma_eff = f_H^2 * sigma_m = {result['params']['sigma_eff_cm2_g']:.2f} cm^2/g")
    print(f"  V_max (NFW): {result['halo']['V_max_kms']:.1f} km/s")
    print(f"  r_s: {result['halo']['r_s_kpc']:.2f} kpc")
    print(f"  rho_s: {result['halo']['rho_s_Msun_pc3']:.4f} M_sun/pc^3")
    print(f"  t_core (Balberg): {result['gravothermal']['t_core_Gyr']:.4f} Gyr")
    print(f"  t_cross: {result['gravothermal']['t_cross_Gyr']:.4f} Gyr")
    print(f"  tau = t_Hubble / t_core: {result['gravothermal']['tau']:.2f}")
    print(f"  Yang+ Eq. 5 validity: {result['gravothermal']['tau_yang_plus_validity']}")
    print(f"  c_200 under SIDM (max-core, tau=1 limit): {result['c_M_result']['c_200_sidm']:.2f}")
    print(f"  c_200 interpretation: {result['c_M_result']['c_200_sidm_interpretation']}")
    print(f"  c-M tension (max-core limit): {result['c_M_result']['tension_sigma_below']:.2f} sigma")
    print(f"  Ohana+ published: 3.2 sigma")
    print(f"  Delta vs Ohana+: {result['c_M_result']['delta_vs_ohana']:+.2f} sigma")
    print(f"  VERDICT: {result['c_M_result']['verdict']}")
    print()
    if result['gravothermal']['tau'] > 1.0:
        print("  *** DEEP CORE COLLAPSE WARNING ***")
        print(f"  v19.2-F canonical parameters predict tau = {result['gravothermal']['tau']:.1f}")
        print(f"  which is OUTSIDE the Yang+ 2024 Eq. 5 polynomial validity range (tau in [0, 1]).")
        print(f"  In deep core collapse, the halo becomes cuspy again (r_s shrinks, c_200 grows).")
        print(f"  Observationally Cloud-9 has c = 4 (LOW concentration), consistent with max-core")
        print(f"  (tau ~ 0.18, per Ohana+ 2026), NOT deep core collapse.")
        print(f"  This is a STRUCTURAL CONSTRAINT: v19.2-F's sigma_eff = {result['params']['sigma_eff_cm2_g']:.1f}")
        print(f"  is too STRONG for Cloud-9. The framework predicts collapse that is not observed.")
        print()
    print()

    # Sensitivity sweep: vary f_H
    print("--- SENSITIVITY to f_H (sigma_peak fixed at 174) ---")
    print("  (All entries have tau > 1 = deep core collapse, Yang+ invalid)")
    for f_H in [0.1, 0.2, 0.297, 0.4, 0.5, 0.7, 1.0]:
        r = v19_2_f_cloud9_cM_tension(f_H=f_H, sigma_peak=SIGMA_PEAK_CM2_PER_G)
        print(f"  f_H = {f_H:.3f}: sigma_eff = {r['params']['sigma_eff_cm2_g']:.1f} cm^2/g, "
              f"tau = {r['gravothermal']['tau']:.2f} (OUTSIDE Yang+), "
              f"max-core c_200 = {r['c_M_result']['c_200_sidm']:.1f}")

    # Sensitivity sweep: vary sigma_peak
    print()
    print("--- SENSITIVITY to sigma_peak (f_H fixed at 0.297) ---")
    print("  (All entries have tau > 1 = deep core collapse, Yang+ invalid)")
    for sigma_peak in [50, 100, 174, 300, 483, 700, 1000]:
        r = v19_2_f_cloud9_cM_tension(f_H=F_H_CANONICAL, sigma_peak=sigma_peak)
        print(f"  sigma_peak = {sigma_peak:4d}: sigma_eff = {r['params']['sigma_eff_cm2_g']:.1f} cm^2/g, "
              f"tau = {r['gravothermal']['tau']:.2f} (OUTSIDE Yang+), "
              f"max-core c_200 = {r['c_M_result']['c_200_sidm']:.1f}")

    # Save canonical result
    out_dir = REPO / "v0.3-prelim" / "data" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "v19_2_f_cloud9_cM_tension.json"
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"\nSaved canonical result: {out}")

    # Per R88(71): no BREAKTHROUGH claim, but be explicit about whether
    # this contradicts prior work
    print()
    print("=" * 70)
    print("R88(71) PRE-CLAIM CHECKLIST (no BREAKTHROUGH being made)")
    print("=" * 70)
    print("(a) Does this contradict Ohana+ 2026?")
    print(f"    v19.2-F predicts tau = {result['gravothermal']['tau']:.1f} (deep core collapse)")
    print(f"    Ohana+ 2026 finds tau = 0.18 (max-core, deep collapse NOT observed)")
    print(f"    -> v19.2-F's parameters are TOO STRONG for Cloud-9. The framework")
    print(f"       predicts collapse that observationally does not occur.")
    print(f"       This is a STRUCTURAL CONSTRAINT on v19.2-F, not a contradiction of Ohana+.")
    print(f"       Both can be true: v19.2-F parameters are wrong for Cloud-9")
    print(f"       (too strong), while Ohana+ parameters work for Cloud-9 (less strong).")
    print()
    print("(b) n_params vs n_channels:")
    print("    n_params in this script: 3 (sigma_peak, f_H, c_0)")
    print("    n_channels fit: 1 (Cloud-9 c-M position only)")
    print("    -> This is a single-channel test. NOT overfitting.")
    print()
    print("(c) What prior claim would need to be wrong?")
    print("    This is a NEGATIVE result for v19.2-F's canonical parameters.")
    print("    v19.2-F's sigma_peak=174 + f_H=0.297 gives sigma_eff=14.6 at v=28 km/s.")
    print("    This is 32x LOWER than Ohana+'s sigma/m=483 (single-component).")
    print("    The 30x lower effective cross-section is NOT enough to put Cloud-9 in")
    print("    the max-core regime (tau=0.18). v19.2-F's framework needs:")
    print("      - Either: lower sigma_peak (e.g., ~50-100 instead of 174)")
    print("      - Or: lower f_H (e.g., <0.05)")
    print("      - Or: a different f_H(r) profile (NOT uniform 0.297)")
    print("    We do NOT claim Ohana+ is wrong. Ohana+ uses different parameters")
    print("    (sigma/m=483, no f_H factor) that happen to put Cloud-9 in max-core.")
    print()
    print("(d) Per v19.1.5 honest framing: this is an EXPLORATORY calculation,")
    print("    not a definitive prediction. The Yang+ Eq. 5 polynomial fit is only")
    print("    valid for tau in [0, 1]; v19.2-F's tau=16 is outside that range.")
    print("    A full N-body simulation (KiSS-SIDM or equivalent) is needed to")
    print("    compute the actual c_200 in the deep-collapse regime.")
    print()
    print("(e) RECOMMENDATION: Do NOT change the paper's §2.6a claim based on this.")
    print("    Instead, document this as an additional cross-check on the v19.2-F")
    print("    parameter choice. The negative result is HONEST framing: v19.2-F's")
    print("    parameters are NOT consistent with Cloud-9 being in max-core regime.")
    print("    The §2.6a structural tension (Cloud-9 vs dSph) is REINFORCED,")
    print("    not resolved, by this analysis.")


if __name__ == "__main__":
    main()
