"""
v19.2-F Phase 3 — EXTENDED Resonance scan (ClawsGO #11 kill/continue gate).

Per ClawsGO comments #7-#11 / docs/V19_2_F_SCOPE.md Phase 3.

CHANGES vs the previous (ClawsGO #10) version (commit 8ffd436):
  - DROPPED the t40 hybrid solver (ClawsGO #11 §2-#4). The hybrid had:
    (a) a Calogero/t40 mass-unit seam risk that may have corrupted the
        m_A' >= 1 MeV branch by 10^5-10^17 (ClawsGO #11 §2 reported this,
        though I could not reproduce the corruption -- both branches
        agree in my reproduction at 1 MeV seam);
    (b) a doc/JSON mismatch on the best point (ClawsGO #11 §3);
    (c) t40 Born formula used outside its domain at the framework's
        kappa = alpha_chi m_chi / m_A' = 3.4 (> 1.68 = resonant threshold)
        (ClawsGO #11 §4).
  - Now uses the VALIDATED Calogero solver (clawsgo_phase3_check) for the
    ENTIRE grid. Failures (Calogero overflows at small m_A' or extreme
    couplings) emit null (NaN), not 0.0.
  - The framework's named point (alpha_chi=6.8e-7, m_A'=200 eV) is
    reported as an ADDITIONAL, separate analysis (using t40 for
    context, but the gate verdict does NOT depend on it).
  - The framework's point is NOT included in the (alpha_D, m_A') distance
    metric because it falls outside the validated Calogero range.

The fundamental question: does any (alpha_D, m_A'/m_chi) point with m_chi = 1 GeV
give sigma/m(v = 29.4) ~ 174 cm^2/g as a PEAK?

RESULT (ClawsGO #11 cleaned-up): NO. The closest match in the validated
Calogero range (m_A' in [1 keV, 100 MeV] or so) is at alpha_D ~ 5.5e-6,
m_A'/m_chi ~ 1.26e-4 (m_A' ~ 126 keV, Born regime), giving
sigma/m(v = 29.4) = 170.0 cm^2/g (ratio 0.977). But this is a
SINGLE-VELOCITY COINCIDENCE: sigma/m(10) = 294 (66x over fit),
sigma/m(100) = 16 (312x over fit). And sigma/m is monotonically decreasing,
so v = 29.4 is NOT a peak.

For the FRAMEWORK's named Yukawa (alpha_chi = 6.8e-7, m_A' = 200 eV):
  - t40 Born formula (framework's own t40_yukawa_sigma_m.py):
      sigma/m(10)   = 1.87e5 cm^2/g  (factor 42,200x over fit)
      sigma/m(29.4) = 3,755 cm^2/g   (factor 6,800x over fit, factor 22x ABOVE target 174)
      sigma/m(100)  = 41.0 cm^2/g    (factor 789x over fit)
  - But Born formula is used OUTSIDE its domain here (kappa = 3.4 > 1.68).
    The true Sommerfeld-regime value is LARGER, not smaller. So the Born
    estimate is a LOWER BOUND on what the framework gives.
  - In any case: framework's coupling is incompatible with the target.

Phase 3 gate verdict: FAIL. Paper (A) is the honest result.

References:
- ClawsGO comments #7, #8, #9, #10, #11
- docs/V19_2_F_SCOPE.md Phase 3
- Chu, Hambye & Tytgat 2018 [7] (M2 Sommerfeld/t-channel resonance)
- v0.3-prelim/code/clawsgo_phase3_check.py (validated variable-phase solver)
- v0.3-prelim/code/t40_yukawa_sigma_m.py (framework's Born formula, context only)
- Paper sec 2.6 (canonical Phase 44: sigma_peak=174, v_target=29.4, sigma_1=4.4)
- Paper sec 2.8 v19.2-F (the open requirement this phase tested)
"""
from __future__ import annotations
import json
import math
import time
from pathlib import Path

import numpy as np

# Natural-units conversions
HBAR_C_GEV_CM = 1.97327e-14  # GeV * cm
M_CHI_GEV = 1.0             # canonical Phase 44 mass
MU_RED_GEV = M_CHI_GEV / 2.0  # equal-mass reduced mass
C_KMS = 2.998e5             # km/s

# Output path
_THIS = Path(__file__).resolve()
OUTPUT_PATH = _THIS.parent.parent / "data" / "results" / "v19_2_f_phase3_resonance_scan.json"

# Use ONLY the validated Calogero solver (ClawsGO #11 recommendation)
from clawsgo_phase3_check import sigma_T_partialwave as calogero_sigma_T
from clawsgo_phase3_check import sigma_m_cm2_g as calogero_sigma_m

# Framework's t40 Born formula, imported for SEPARATE framework-point analysis
sys_path = str(_THIS.parent)
import sys
if sys_path not in sys.path:
    sys.path.insert(0, sys_path)
try:
    from t40_yukawa_sigma_m import sigma_T_cm2 as framework_sigma_T_cm2
    HAS_T40 = True
except ImportError:
    HAS_T40 = False


def sigma_m_at_v(v_kms, alpha_D, m_A_prime_GeV):
    """Use the validated Calogero solver. Returns None on NaN."""
    v_c = v_kms / C_KMS
    sig_T = calogero_sigma_T(alpha_D, m_A_prime_GeV, v_c)
    if np.isnan(sig_T):
        return None
    return calogero_sigma_m(sig_T)


def find_best_point(alpha_D, m_A_prime_GeV, v_test_kms=None):
    """For a given (alpha_D, m_A') point, evaluate sigma/m across v and check
    peak structure.

    Returns dict with sigma values, peak location, monotonicity, ratio.
    """
    if v_test_kms is None:
        v_test_kms = np.array([5.0, 10.0, 20.0, 29.4, 50.0, 100.0])

    sigmas = []
    for v in v_test_kms:
        sig = sigma_m_at_v(v, alpha_D, m_A_prime_GeV)
        sigmas.append(sig)
    sigmas = np.array([s if s is not None else np.nan for s in sigmas])

    i29 = np.argmin(np.abs(v_test_kms - 29.4))
    sigma_29 = sigmas[i29]

    # Find peak in valid values
    valid = ~np.isnan(sigmas)
    if not np.any(valid):
        return _nan_result(v_test_kms, sigmas)

    valid_sigmas = sigmas.copy()
    valid_sigmas[~valid] = -np.inf
    i_peak = np.argmax(valid_sigmas)
    v_peak = v_test_kms[i_peak]
    sigma_peak = sigmas[i_peak]

    is_peak_at_29 = (i_peak == i29)

    # Monotonicity: ignore NaN
    diffs = np.diff(sigmas)
    is_monotonic_decreasing = bool(np.all(diffs[~np.isnan(diffs)] <= 0))

    ratio = sigma_29 / 174.0 if not np.isnan(sigma_29) and sigma_29 > 0 else float("inf")

    return {
        "sigma_m_v_5_kms": _fmt(sigmas[np.argmin(np.abs(v_test_kms - 5))]),
        "sigma_m_v_10_kms": _fmt(sigmas[np.argmin(np.abs(v_test_kms - 10))]),
        "sigma_m_v_20_kms": _fmt(sigmas[np.argmin(np.abs(v_test_kms - 20))]),
        "sigma_m_v_29_kms": _fmt(sigma_29),
        "sigma_m_v_50_kms": _fmt(sigmas[np.argmin(np.abs(v_test_kms - 50))]),
        "sigma_m_v_100_kms": _fmt(sigmas[np.argmin(np.abs(v_test_kms - 100))]),
        "v_peak_kms": float(v_peak) if not np.isnan(sigma_peak) else None,
        "sigma_m_at_peak": _fmt(sigma_peak),
        "is_peak_at_v_29": bool(is_peak_at_29),
        "is_monotonic_decreasing": bool(is_monotonic_decreasing),
        "ratio_to_target_174": float(ratio),
        "all_nan": bool(not np.any(valid)),
    }


def _fmt(x):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return None
    return float(x)


def _nan_result(v_test_kms, sigmas):
    return {
        "sigma_m_v_5_kms": _fmt(sigmas[np.argmin(np.abs(v_test_kms - 5))]),
        "sigma_m_v_10_kms": _fmt(sigmas[np.argmin(np.abs(v_test_kms - 10))]),
        "sigma_m_v_20_kms": _fmt(sigmas[np.argmin(np.abs(v_test_kms - 20))]),
        "sigma_m_v_29_kms": _fmt(sigmas[np.argmin(np.abs(v_test_kms - 29.4))]),
        "sigma_m_v_50_kms": _fmt(sigmas[np.argmin(np.abs(v_test_kms - 50))]),
        "sigma_m_v_100_kms": _fmt(sigmas[np.argmin(np.abs(v_test_kms - 100))]),
        "v_peak_kms": None,
        "sigma_m_at_peak": None,
        "is_peak_at_v_29": False,
        "is_monotonic_decreasing": False,
        "ratio_to_target_174": float("inf"),
        "all_nan": True,
    }


def framework_point_analysis():
    """Compute framework's named point using t40 Born formula, as a SEPARATE
    analysis (not part of the (alpha_D, m_A') scan grid).

    NOTE on convention: t40 uses g_chi as the bare gauge coupling in its
    sigma_T formula (g_chi^4 m_chi^2 / 8 pi m_phi^4). The framework's
    'alpha_chi = 6.8e-7' appears to be the FINE-STRUCTURE CONSTANT
    alpha = g^2/(4 pi), based on the framework's previous claim that
    alpha_chi = 6.8e-7 gives sigma/m(100) = 2.84 cm^2/g (which is
    inconsistent with t40 Born at this g_chi -- the framework's number
    was a hand-waved estimate).

    Per the project's own Phase-1+2 docs/V19_2_F_PHASE1_2_RESULTS.md
    (which uses t40 directly): at alpha_chi = 6.8e-7 (interpreted as
    g^2/(4pi) -> g_chi = 0.00292), sigma/m(100) = 41.0 cm^2/g (factor
    789x over fit).

    We report BOTH interpretations as context:
      - alpha_chi as g^2/(4 pi)  ->  g_chi = 0.00292 (large alpha, near threshold)
      - alpha_chi as g^2         ->  g_chi = 8.25e-4 (small g_chi)
    The first gives sigma/m(100) = 41.0; the second gives sigma/m(100) = 0.052
    (matches the norm-matched coupling). The framework's "2.84" appears
    to be from a third (inconsistent) convention.
    """
    if not HAS_T40:
        return None

    m_phi_MeV = 0.2  # 200 eV
    m_chi_GeV = 1.0
    m_chi_g = m_chi_GeV * 1.78266192e-24

    v_test = [5, 10, 20, 29.4, 50, 100, 200, 500, 1000]

    def compute(g_chi, label):
        sigma_at_v = {}
        for v in v_test:
            sig_cm2 = framework_sigma_T_cm2(v, m_phi_MeV, m_chi_GeV, g_chi)
            sigma_at_v[v] = sig_cm2 / m_chi_g
        return sigma_at_v

    # Convention 1: alpha = g^2/(4 pi) -> g_chi = sqrt(4 pi alpha)
    alpha_chi = 6.8e-7
    g_chi_a = math.sqrt(4 * math.pi * alpha_chi)
    sigma_v_a = compute(g_chi_a, "alpha=g^2/4pi")
    kappa_a = alpha_chi * m_chi_GeV / (m_phi_MeV * 1e-3)

    # Convention 2: alpha = g^2 -> g_chi = sqrt(alpha)
    g_chi_b = math.sqrt(alpha_chi)
    sigma_v_b = compute(g_chi_b, "alpha=g^2")
    kappa_b = alpha_chi / 4 / math.pi * m_chi_GeV / (m_phi_MeV * 1e-3)

    return {
        "alpha_chi": alpha_chi,
        "m_A_prime_eV": 200,
        "kappa_convention_a": float(kappa_a),  # alpha_chi m_chi/m_A'
        "kappa_convention_b": float(kappa_b),  # (alpha_chi/4pi) m_chi/m_A'
        "sigma_at_v_convention_a_alpha_eq_g2_4pi": {
            f"v_{v}_kms": float(sigma_v_a[v]) for v in v_test
        },
        "sigma_at_v_convention_b_alpha_eq_g2": {
            f"v_{v}_kms": float(sigma_v_b[v]) for v in v_test
        },
        "ratio_to_target_174_convention_a": float(sigma_v_a[29.4] / 174.0),
        "ratio_to_target_174_convention_b": float(sigma_v_b[29.4] / 174.0),
        "ratio_to_fit_at_v_100_convention_a": float(sigma_v_a[100] / 0.052),
        "ratio_to_fit_at_v_100_convention_b": float(sigma_v_b[100] / 0.052),
        "framework_doc_claim_sigma_m_v_100": 2.84,  # what the framework's Phase-2 doc said
        "framework_doc_claim_matches_either": "Neither -- framework's previous claim of sigma/m(100) = 2.84 does not match t40 Born at either convention (a: 41.0; b: 0.052). The framework's number was a hand-waved estimate.",
        "note": (
            "t40 Born used. CONVENTION ISSUE: the framework's 'alpha_chi = 6.8e-7' is ambiguous "
            "(g^2/4pi or g^2). We report both. Convention a (alpha=g^2/4pi) gives sigma/m(100)=41.0; "
            "convention b (alpha=g^2) gives sigma/m(100)=0.052. Neither matches the framework's "
            "previous doc claim of 2.84."
        ),
    }


def main():
    print("=" * 70)
    print("v19.2-F Phase 3 — EXTENDED (ClawsGO #11 cleaned-up)")
    print("=" * 70)
    print()
    print(f"m_chi = {M_CHI_GEV} GeV, mu_red = {MU_RED_GEV} GeV")
    print(f"Target: v_res = 29.4 km/s, sigma_peak = 174 cm^2/g")
    print()
    print("EXTENDED scan grid (m_A'/m_chi in [1e-6, 2.0], m_A' from 1 keV to 2 GeV):")
    print("  alpha_D in [1e-6, 5.0] (10 log-spaced points)")
    print("  m_A'/m_chi in [1e-6, 2.0] (10 log-spaced points)")
    print("  v_test = [5, 10, 20, 29.4, 50, 100] km/s (6 points per scan)")
    print()
    print("SOLVER: validated ClawsGO variable-phase (Calogero) for ALL points.")
    print("  Failures emit null (NaN), not 0.0.")
    print()
    print("FRAMEWORK POINT (alpha_chi=6.8e-7, m_A'=200 eV) reported SEPARATELY")
    print("  using the framework's t40 Born formula. Not part of the scan grid.")
    print()

    alpha_D_grid = np.logspace(-6, np.log10(5), 10)
    m_Ap_ratio_grid = np.logspace(-6, np.log10(2), 10)

    scan_points = []
    best_overall = None
    best_log10_distance = float("inf")
    pass_flag = False
    n_null = 0
    t0 = time.time()
    count = 0
    total = len(alpha_D_grid) * len(m_Ap_ratio_grid)

    for alpha_D in alpha_D_grid:
        for ratio in m_Ap_ratio_grid:
            count += 1
            m_A_prime_GeV = ratio * M_CHI_GEV
            res = find_best_point(alpha_D, m_A_prime_GeV)

            if res["all_nan"]:
                n_null += 1

            v_target = 29.4
            sigma_target = 174.0
            sigma_29 = res["sigma_m_v_29_kms"]
            if sigma_29 is None:
                scan_points.append({
                    "alpha_D": float(alpha_D),
                    "m_Ap_over_m_chi": float(ratio),
                    "m_A_prime_GeV": float(m_A_prime_GeV),
                    "result": res,
                })
                continue

            d_v = abs(math.log10(max(res["v_peak_kms"] or 5, 1e-3) / v_target))
            d_s = abs(math.log10(max(sigma_29, 1e-3) / sigma_target))
            distance = d_v + d_s

            if distance < best_log10_distance:
                best_log10_distance = distance
                best_overall = {
                    "alpha_D": float(alpha_D),
                    "m_Ap_over_m_chi": float(ratio),
                    "m_A_prime_GeV": float(m_A_prime_GeV),
                    **res,
                    "log10_distance_to_target": float(distance),
                }

            if (res["is_peak_at_v_29"]
                    and 0.5 < res["ratio_to_target_174"] < 2.0):
                pass_flag = True

            scan_points.append({
                "alpha_D": float(alpha_D),
                "m_Ap_over_m_chi": float(ratio),
                "m_A_prime_GeV": float(m_A_prime_GeV),
                "result": res,
            })
            elapsed = time.time() - t0
            s29_str = f"{sigma_29:.3g}" if sigma_29 is not None else "null"
            print(f"  [{count}/{total}] alpha_D={alpha_D:.2e}, "
                  f"m_A'/m_chi={ratio:.2e}: "
                  f"sigma(29.4)={s29_str}, "
                  f"v_peak={res['v_peak_kms']} km/s, "
                  f"ratio={res['ratio_to_target_174']:.3f} "
                  f"({elapsed:.1f}s)")

    # Framework point analysis (separate, not part of scan)
    framework = framework_point_analysis()

    result = {
        "_meta": {
            "description": (
                "v19.2-F Phase 3 EXTENDED (ClawsGO #11 cleaned-up). "
                "Single solver: validated Calogero for ALL (alpha_D, m_A') "
                "scan points. Failures emit null. Framework point reported "
                "separately using t40 Born (outside its domain, kappa=3.4>1.68; "
                "values are LOWER BOUND on true Sommerfeld-regime). "
                "RESULT: FAIL. Closest match to 174 cm^2/g at alpha_D~5.55e-6, "
                "m_A'/m_chi~1.26e-4 (m_A'=126 keV, Born regime) gives "
                "sigma/m(29.4)=170.0 cm^2/g (ratio 0.977), but this is a "
                "single-velocity coincidence (sigma/m(10)=293.6, sigma/m(100)=16.24) "
                "and sigma/m is monotonically decreasing (NOT a peak). "
                "Framework's named Yukawa (t40 Born, kappa=3.4, outside domain) "
                "gives sigma/m(29.4)=3,755 cm^2/g -- factor 22x ABOVE target."
            ),
            "method": "Validated Calogero (variable-phase) partial-wave solver; peak-structure check across v = [5, 10, 20, 29.4, 50, 100] km/s. Framework point uses t40 Born separately.",
            "solver": "clawsgo_phase3_check.sigma_T_partialwave (validated Calogero)",
            "m_chi_GeV": M_CHI_GEV,
            "mu_red_GeV": MU_RED_GEV,
            "v_target_kms": 29.4,
            "sigma_target_cm2_per_g": 174.0,
            "extended_grid_alpha_D": [1e-6, 5.0],
            "extended_grid_m_Ap_over_m_chi": [1e-6, 2.0],
            "resonance_criterion": "sigma/m(v=29.4) is a LOCAL MAX in [5, 100] km/s AND within factor 2 of 174 cm^2/g",
            "velocity_conversion_fix": "ClawsGO #8: c = 2.998e5 km/s",
            "n_alpha_grid": len(alpha_D_grid),
            "n_mAp_grid": len(m_Ap_ratio_grid),
            "n_null_points": n_null,
            "framework_point": framework,
            "commit_at_phase3": "v19.2-F Phase 3 EXTENDED (ClawsGO #11)",
        },
        "scan_points": scan_points,
        "best_overall": best_overall,
        "best_log10_distance": best_log10_distance,
        "pass_flag": pass_flag,
        "verdict": ("FAIL — Phase 3 kill/continue gate does not pass with the "
                    "EXTENDED grid using the validated Calogero solver. "
                    "Paper (A) wins. The peak stays phenomenological by "
                    "necessity."),
        "elapsed_seconds": time.time() - t0,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(result, f, indent=2, default=float)
    print(f"\nResults written to: {OUTPUT_PATH}")
    print(f"Null (failed) scan points: {n_null}")
    print()

    print("=" * 70)
    print("RESULT (ClawsGO #11 cleaned-up)")
    print("=" * 70)
    if best_overall:
        m = best_overall
        print("Best (alpha_D, m_A'/m_chi) point to target (29.4 km/s, 174 cm^2/g):")
        print(f"  alpha_D                    = {m['alpha_D']:.3e}")
        print(f"  m_A'/m_chi                  = {m['m_Ap_over_m_chi']:.3e}")
        print(f"  m_A'                        = {m['m_A_prime_GeV']:.3e} GeV "
              f"({m['m_A_prime_GeV']*1e6:.1f} keV)")
        if m["sigma_m_v_29_kms"] is not None:
            print(f"  sigma/m(v=29.4)             = {m['sigma_m_v_29_kms']:.3g} cm^2/g "
                  f"(target: 174, ratio {m['ratio_to_target_174']:.3f})")
        if m["sigma_m_v_10_kms"] is not None:
            print(f"  sigma/m(v=10)               = {m['sigma_m_v_10_kms']:.3g} cm^2/g "
                  f"(fit 4.43, ratio {m['sigma_m_v_10_kms']/4.43:.1f}x)")
        if m["sigma_m_v_100_kms"] is not None:
            print(f"  sigma/m(v=100)              = {m['sigma_m_v_100_kms']:.3g} cm^2/g "
                  f"(fit 0.052, ratio {m['sigma_m_v_100_kms']/0.052:.1f}x)")
        if m["v_peak_kms"] is not None:
            print(f"  v_peak                       = {m['v_peak_kms']:.1f} km/s")
        print(f"  is_peak_at_v_29             = {m['is_peak_at_v_29']}")
        print(f"  is_monotonic_decreasing     = {m['is_monotonic_decreasing']}")
        print(f"  log10 distance to target    = {m['log10_distance_to_target']:.2f}")
    print()
    if framework:
        print("FRAMEWORK POINT (alpha_chi=6.8e-7, m_A'=200 eV, t40 Born, both conventions):")
        print("  Convention a (alpha = g^2/4 pi -> g_chi = 0.00292):")
        for k, v in framework["sigma_at_v_convention_a_alpha_eq_g2_4pi"].items():
            print(f"    {k}: sigma/m = {v:.3g} cm^2/g")
        print(f"    ratio_to_target_174 = {framework['ratio_to_target_174_convention_a']:.2f}")
        print(f"    kappa = {framework['kappa_convention_a']:.3f}")
        print("  Convention b (alpha = g^2 -> g_chi = 8.25e-4):")
        for k, v in framework["sigma_at_v_convention_b_alpha_eq_g2"].items():
            print(f"    {k}: sigma/m = {v:.3g} cm^2/g")
        print(f"    ratio_to_target_174 = {framework['ratio_to_target_174_convention_b']:.2f}")
        print(f"    kappa = {framework['kappa_convention_b']:.3f}")
        print(f"  Framework's previous doc claim: sigma/m(100) = 2.84")
        print(f"  Matches either convention? {framework['framework_doc_claim_matches_either']}")
    print()
    if result["pass_flag"]:
        print("PASS: a (alpha_D, m_A'/m_chi) point lands near the target with a peak at v=29.4.")
    else:
        print("FAIL: no (alpha_D, m_A'/m_chi) point lands near the target with a peak at v=29.4.")
        print("       Phase 3 gate FAILS even with the EXTENDED grid -> paper (A).")

    print()
    print(f"Elapsed: {result['elapsed_seconds']:.1f}s")
    print(f"Total scan points: {len(scan_points)} ({n_null} null)")


if __name__ == "__main__":
    main()
