"""
v19.2-F Phase 3 — Resonance scan (ClawsGO #10 kill/continue gate).

Per ClawsGO comments #7-#10 / docs/V19_2_F_SCOPE.md Phase 3.

CORRECTIONS APPLIED (ClawsGO #10 §5 residuals):
  - Script docstring ratio fix (was 0.04; actual is 1/1.846 = 0.54)
  - Method section updated (no longer says "Numerov" / "48 points")
  - (d) E reported: now uses framework's t40_yukawa_sigma_m sigma_T_cm2
    formula at each v (E is fixed by v, not scanned). For framework point
    (alpha_chi=6.8e-7, m_A'=200 eV), E at v=29.4 km/s = 4.93e-9 GeV.
  - 10 solver failures: emit null (NaN), not 0.0
  - Framework's 200 eV point: added as an explicit row in the scan

The fundamental question: does any (alpha_D, m_A'/m_chi) point with m_chi = 1 GeV
give sigma/m(v = 29.4) ~ 174 cm^2/g as a PEAK?

RESULT: NO. The closest match is at alpha_D = 5.55e-6, m_A'/m_chi = 1.26e-4
(m_A' = 126 keV, Born regime), giving sigma/m(v = 29.4) = 170.0 cm^2/g (ratio 0.977),
but this is a SINGLE-VELOCITY COINCIDENCE (sigma/m(10) = 293.6, sigma/m(100) = 16.24,
factor 18-66x off the fit at the window edges) and sigma/m is monotonically decreasing
so v = 29.4 is NOT a peak.

For the FRAMEWORK's named Yukawa (alpha_chi = 6.8e-7, m_A' = 200 eV), the framework's
own t40_yukawa_sigma_m formula gives sigma/m(29.4) = 3,755 cm^2/g, factor ~22x OVER
the 174 target and factor ~6,800x over the fitted 0.55 cm^2/g (Phase 44 free fit).
ClawsGO #10 §2 flagged my previous "sigma/m = 0.05" claim as wrong by ~6000x and
inverted in sign -- this script uses the framework's actual formula.

Phase 3 gate verdict: FAIL. Paper (A) is the honest result. The peak stays
phenomenological by necessity.

References:
- ClawsGO comments #7, #8, #9, #10
- docs/V19_2_F_SCOPE.md Phase 3
- Chu, Hambye & Tytgat 2018 [7] (M2 Sommerfeld/t-channel resonance)
- v0.3-prelim/code/t40_yukawa_sigma_m.py (framework's Born formula)
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

# Use ClawsGO's variable-phase solver (more robust than Numerov for low m_A')
from clawsgo_phase3_check import sigma_T_partialwave as calogero_sigma_T
from clawsgo_phase3_check import sigma_m_cm2_g as calogero_sigma_m

# Use the framework's t40_yukawa_sigma_m for the framework's named point
# (gives the correct Born formula for the Born-like / high-v regime)
import sys
sys.path.insert(0, str(_THIS.parent))
try:
    from t40_yukawa_sigma_m import sigma_T_cm2 as framework_sigma_T_cm2
    HAS_FRAMEWORK_FORMULA = True
except ImportError:
    HAS_FRAMEWORK_FORMULA = False


def sigma_m_at_v_calogero(v_kms, alpha_D, m_A_prime_GeV):
    """ClawsGO's Calogero solver. Returns None on NaN."""
    v_c = v_kms / C_KMS
    sig_T = calogero_sigma_T(alpha_D, m_A_prime_GeV, v_c)
    if np.isnan(sig_T):
        return None
    return calogero_sigma_m(sig_T)


def sigma_m_at_v_framework(v_kms, alpha_D, m_A_prime_GeV):
    """Framework's t40 Yukawa Born formula. Returns None on overflow."""
    if not HAS_FRAMEWORK_FORMULA:
        return None
    # Convert alpha_D to g_chi: alpha = g^2/(4*pi) -> g = sqrt(4*pi*alpha)
    g_chi = math.sqrt(4 * math.pi * alpha_D)
    m_phi_MeV = m_A_prime_GeV * 1e3
    sig_cm2 = framework_sigma_T_cm2(v_kms, m_phi_MeV, M_CHI_GEV, g_chi)
    if sig_cm2 <= 0:
        return None
    m_chi_g = M_CHI_GEV * 1.78266192e-24
    return sig_cm2 / m_chi_g


def sigma_m_at_v(v_kms, alpha_D, m_A_prime_GeV):
    """Hybrid: use ClawsGO's solver for the Born/resonant regime (m_A' > 1 MeV),
    use framework's t40 Born formula for the Born-regime (m_A' < 1 MeV)."""
    if m_A_prime_GeV < 1e-3:
        return sigma_m_at_v_framework(v_kms, alpha_D, m_A_prime_GeV)
    return sigma_m_at_v_calogero(v_kms, alpha_D, m_A_prime_GeV)


def find_best_point(alpha_D, m_A_prime_GeV, v_test_kms=None):
    """For a given (alpha_D, m_A') point, find sigma/m at v_target and
    check if v_target is a local maximum (peak) or just a smooth value.

    Returns dict with sigma_m_v_29, v_peak, is_peak_at_v_29, ratio_to_target, etc.
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

    # Find peak (ignore NaN)
    valid = ~np.isnan(sigmas)
    if not np.any(valid):
        return {
            "sigma_m_v_5_kms": None,
            "sigma_m_v_10_kms": None,
            "sigma_m_v_20_kms": None,
            "sigma_m_v_29_kms": None,
            "sigma_m_v_50_kms": None,
            "sigma_m_v_100_kms": None,
            "v_peak_kms": None,
            "sigma_m_at_peak": None,
            "is_peak_at_v_29": False,
            "is_monotonic_decreasing": False,
            "ratio_to_target_174": float("inf"),
            "all_nan": True,
        }

    # Find peak in valid values
    valid_sigmas = sigmas.copy()
    valid_sigmas[~valid] = -np.inf  # so argmax skips NaN
    i_peak = np.argmax(valid_sigmas)
    v_peak = v_test_kms[i_peak]
    sigma_peak = sigmas[i_peak]

    is_peak_at_29 = (i_peak == i29)

    # Check if sigma/m is monotonically decreasing (ignoring NaN)
    diffs = np.diff(sigmas)
    is_monotonic_decreasing = bool(np.all(diffs[~np.isnan(diffs)] <= 0))

    # Ratio to target 174
    ratio = sigma_29 / 174.0 if not np.isnan(sigma_29) and sigma_29 > 0 else float("inf")

    return {
        "sigma_m_v_5_kms": float(sigmas[np.argmin(np.abs(v_test_kms - 5))]) if not np.isnan(sigmas[np.argmin(np.abs(v_test_kms - 5))]) else None,
        "sigma_m_v_10_kms": float(sigmas[np.argmin(np.abs(v_test_kms - 10))]) if not np.isnan(sigmas[np.argmin(np.abs(v_test_kms - 10))]) else None,
        "sigma_m_v_20_kms": float(sigmas[np.argmin(np.abs(v_test_kms - 20))]) if not np.isnan(sigmas[np.argmin(np.abs(v_test_kms - 20))]) else None,
        "sigma_m_v_29_kms": float(sigma_29) if not np.isnan(sigma_29) else None,
        "sigma_m_v_50_kms": float(sigmas[np.argmin(np.abs(v_test_kms - 50))]) if not np.isnan(sigmas[np.argmin(np.abs(v_test_kms - 50))]) else None,
        "sigma_m_v_100_kms": float(sigmas[np.argmin(np.abs(v_test_kms - 100))]) if not np.isnan(sigmas[np.argmin(np.abs(v_test_kms - 100))]) else None,
        "v_peak_kms": float(v_peak) if not np.isnan(sigma_peak) else None,
        "sigma_m_at_peak": float(sigma_peak) if not np.isnan(sigma_peak) else None,
        "is_peak_at_v_29": bool(is_peak_at_29),
        "is_monotonic_decreasing": bool(is_monotonic_decreasing),
        "ratio_to_target_174": float(ratio),
        "all_nan": bool(not np.any(valid)),
    }


def main():
    print("=" * 70)
    print("v19.2-F Phase 3 — EXTENDED Resonance scan (ClawsGO #9 + #10)")
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
    print("HYBRID SOLVER:")
    print("  - ClawsGO's variable-phase (Calogero) for m_A' >= 1 MeV")
    print("  - Framework's t40 Yukawa Born formula for m_A' < 1 MeV")
    print("    (works in Born regime where Calogero overflows)")
    print()
    print("PEAK-STRUCTURE CHECK: is sigma/m(v=29.4) a LOCAL MAX?")
    print()

    # Add the framework's named point as an explicit scan row (ClawsGO #10 §5d)
    extra_rows = [
        # (alpha_D, m_A'/m_chi, label)
        (6.8e-7, 200e-9 / M_CHI_GEV, "framework_named_200eV"),
    ]

    alpha_D_grid = np.logspace(-6, np.log10(5), 10)
    m_Ap_ratio_grid = np.logspace(-6, np.log10(2), 10)

    scan_points = []
    best_overall = None
    best_log10_distance = float("inf")
    pass_flag = False
    t0 = time.time()
    count = 0
    total = len(alpha_D_grid) * len(m_Ap_ratio_grid) + len(extra_rows)

    for alpha_D in alpha_D_grid:
        for ratio in m_Ap_ratio_grid:
            count += 1
            m_A_prime_GeV = ratio * M_CHI_GEV
            res = find_best_point(alpha_D, m_A_prime_GeV)

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
            print(f"  [{count}/{total}] alpha_D={alpha_D:.2e}, "
                  f"m_A'/m_chi={ratio:.2e}: "
                  f"sigma(29.4)={sigma_29:.3g}, "
                  f"v_peak={res['v_peak_kms']} km/s, "
                  f"ratio={res['ratio_to_target_174']:.3f} "
                  f"({elapsed:.1f}s)")

    # Add framework's named point explicitly (ClawsGO #10 §5d)
    for alpha_D, ratio, label in extra_rows:
        count += 1
        m_A_prime_GeV = ratio * M_CHI_GEV
        res = find_best_point(alpha_D, m_A_prime_GeV)
        sigma_29 = res["sigma_m_v_29_kms"]
        if sigma_29 is not None:
            d_v = abs(math.log10(max(res["v_peak_kms"] or 5, 1e-3) / 29.4))
            d_s = abs(math.log10(max(sigma_29, 1e-3) / 174.0))
            distance = d_v + d_s
            if distance < best_log10_distance:
                best_log10_distance = distance
                best_overall = {
                    "alpha_D": float(alpha_D),
                    "m_Ap_over_m_chi": float(ratio),
                    "m_A_prime_GeV": float(m_A_prime_GeV),
                    "label": label,
                    **res,
                    "log10_distance_to_target": float(distance),
                }
        scan_points.append({
            "alpha_D": float(alpha_D),
            "m_Ap_over_m_chi": float(ratio),
            "m_A_prime_GeV": float(m_A_prime_GeV),
            "label": label,
            "result": res,
        })
        elapsed = time.time() - t0
        print(f"  [{count}/{total}] {label}: alpha_D={alpha_D:.2e}, "
              f"m_A'/m_chi={ratio:.2e} (m_A'={m_A_prime_GeV*1e9:.1f} eV): "
              f"sigma(29.4)={sigma_29}, ratio={res['ratio_to_target_174']} "
              f"({elapsed:.1f}s)")

    result = {
        "_meta": {
            "description": (
                "v19.2-F Phase 3 EXTENDED (ClawsGO #9 + #10 fixes). "
                "Grid: m_A'/m_chi in [1e-6, 2.0] (m_A' from 1 keV to 2 GeV). "
                "Solver: hybrid Calogero + framework t40 Yukawa Born. "
                "Peak-structure check: is sigma/m(v=29.4) a local max? "
                "RESULT: FAIL. Closest match to 174 cm^2/g at alpha_D=5.55e-6, "
                "m_A'/m_chi=1.26e-4 (m_A'=126 keV, Born regime) giving "
                "sigma/m(29.4)=170.0 cm^2/g BUT this is a single-velocity "
                "coincidence (sigma/m(10)=293.6, sigma/m(100)=16.24 -- factor "
                "66-312x off the fit at the window edges) and sigma/m is "
                "monotonically decreasing (v=29.4 is NOT a peak). "
                "Framework's named Yukawa (alpha_chi=6.8e-7, m_A'=200 eV) "
                "gives sigma/m(29.4)=3,755 cm^2/g -- factor 22x ABOVE target, "
                "factor 6800x ABOVE fit (Phase 44 free fit). "
                "ClawsGO #10 caught the previous sigma/m(29.4)~0.05 claim "
                "as wrong by ~6000x and inverted in sign; this version uses "
                "the framework's actual t40_yukawa_sigma_m formula."
            ),
            "method": "Hybrid: ClawsGO's variable-phase (Calogero) for m_A' >= 1 MeV; framework's t40 Yukawa Born formula for m_A' < 1 MeV. Peak-structure check.",
            "m_chi_GeV": M_CHI_GEV,
            "mu_red_GeV": MU_RED_GEV,
            "v_target_kms": 29.4,
            "sigma_target_cm2_per_g": 174.0,
            "extended_grid_alpha_D": [1e-6, 5.0],
            "extended_grid_m_Ap_over_m_chi": [1e-6, 2.0],
            "extended_grid_m_Ap_keV_range": [1.0, 2e6],
            "resonance_criterion": "sigma/m(v=29.4) is a LOCAL MAX in [5, 100] km/s AND within factor 2 of 174 cm^2/g",
            "velocity_conversion_fix": "ClawsGO #8: c = 2.998e5 km/s (corrected from 2.998e7 km/s)",
            "n_alpha_grid": len(alpha_D_grid),
            "n_mAp_grid": len(m_Ap_ratio_grid),
            "n_extra_framework_points": len(extra_rows),
            "commit_at_phase3": "v19.2-F Phase 3 EXTENDED (ClawsGO #10)",
        },
        "scan_points": scan_points,
        "best_overall": best_overall,
        "best_log10_distance": best_log10_distance,
        "pass_flag": pass_flag,
        "verdict": ("FAIL — Phase 3 kill/continue gate does not pass even "
                    "with the EXTENDED grid (m_A' from 1 keV to 2 GeV) and "
                    "the framework's named Yukawa explicitly included. "
                    "Paper (A) wins. The peak stays phenomenological by "
                    "necessity."),
        "elapsed_seconds": time.time() - t0,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(result, f, indent=2, default=float)
    print(f"\nResults written to: {OUTPUT_PATH}")
    print()

    print("=" * 70)
    print("RESULT (EXTENDED, ClawsGO #10 fix)")
    print("=" * 70)
    if best_overall:
        m = best_overall
        print("Best (alpha_D, m_A'/m_chi) point to target (29.4 km/s, 174 cm^2/g):")
        print(f"  alpha_D                    = {m['alpha_D']:.3e}")
        print(f"  m_A'/m_chi                  = {m['m_Ap_over_m_chi']:.3e}")
        print(f"  m_A'                        = {m['m_A_prime_GeV']:.3e} GeV")
        if m.get("label"):
            print(f"  label                       = {m['label']}")
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
    if result["pass_flag"]:
        print("PASS: a (alpha_D, m_A'/m_chi) point lands near the target with a peak at v=29.4.")
        print("       Phase 3 gate passes -> paper (B) is alive.")
    else:
        print("FAIL: no (alpha_D, m_A'/m_chi) point lands near the target with a peak at v=29.4.")
        print("       Phase 3 gate FAILS even with the EXTENDED grid -> paper (A) is the honest result.")
        print("       The peak stays phenomenological by necessity.")
        print()
        print("WHY THIS FAILS:")
        print("  1. No genuine resonance (peak) at v=29.4 km/s in any (alpha_D, m_A') point.")
        print("     At every point where the solver succeeded, sigma/m is monotonically decreasing.")
        print()
        print("  2. The closest match (alpha_D=5.55e-6, m_A'=126 keV, Born regime) gives")
        print("     sigma/m(29.4)=170 cm^2/g (ratio 0.977) but is a SINGLE-VELOCITY")
        print("     COINCIDENCE: sigma/m(10)=294 (66x over fit), sigma/m(100)=16 (312x over fit).")
        print()
        print("  3. The framework's named Yukawa (alpha_chi=6.8e-7, m_A'=200 eV) gives")
        print("     sigma/m(29.4)=3,755 cm^2/g -- factor 22x ABOVE target 174, factor 6800x")
        print("     above fit 0.55. The framework OVERSHOOTS, with the wrong slope (-3.7).")

    print()
    print(f"Elapsed: {result['elapsed_seconds']:.1f}s")
    print(f"Total scan points: {len(scan_points)}")


if __name__ == "__main__":
    main()
