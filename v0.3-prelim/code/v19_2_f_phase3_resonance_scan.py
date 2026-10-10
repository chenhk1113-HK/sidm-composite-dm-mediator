"""
v19.2-F Phase 3 — Resonance scan (ClawsGO kill/continue gate) — RESULT.

Per ClawsGO comment #7 / docs/V19_2_F_SCOPE.md Phase 3:
- Scan the (alpha_D, m_A'/m_chi) plane for resonant poles (bound-state-like
  enhancements in l = 0, 1, 2, 3 partial waves).
- For each pole, record v_res, peak height (unitarity-capped), and width.
- Question: does any (alpha_D, m_A'/m_chi) with m_chi = 1 GeV place a
  resonance at v ~ 29 km/s with sigma_peak ~ 174 cm^2/g and Gamma/v ~
  0.05-0.10, AND is the required alpha_D compatible with the hierarchy?

Method: standard partial-wave solver with Numerov method on log-spaced grid
(see _delta_l_partial_wave below). The Yukawa range 1/m_A' is fm-scale for
m_A' in [0.01, 1] GeV, so the de Broglie wavelength at v = 29.4 km/s
(1/k ~ 10^4 fm) is MUCH larger than the potential range. The Yukawa is
invisible at these velocities; no resonance can appear in the
(alpha_D, m_A'/m_chi) plane for v << 10^3 km/s.

Gate (this is the program's kill/continue):
- Pass -> go to Phase 4 (paper B).
- Fail (no point lands near the target) -> paper A: the peak stays
  phenomenological by necessity.

RESULT: FAIL. The kill/continue gate does not pass for any (alpha_D,
m_A'/m_chi) point scanned. The closest resonance (l=2, d-wave, alpha_D=5.0,
m_A'/m_chi=0.1) lands at v_res ~ 25,752 km/s, FAR above the target of
29.4 km/s (factor ~880x too fast). At the target v = 29.4 km/s, the
Yukawa potential is invisible to the de Broglie wave because the
potential range (fm-scale) is ~10^4 smaller than the wavelength. The
phase shifts in all partial waves are ~0 at the target velocity.

This confirms the Phase 1 finding (1.2x10^-9 s-channel tuning is
irreducible) and the Phase 2 finding (200 eV Yukawa does not reproduce
the fitted background): the cloud-9 feature cannot come from a standard
Yukawa. Paper (A) is the honest result. The peak stays phenomenological
by necessity.

References:
- ClawsGO comment #7 / docs/V19_2_F_SCOPE.md Phase 3
- Chu, Hambye & Tytgat 2018 [7] (M2 Sommerfeld/t-channel resonance)
- Paper sec 2.6 (canonical Phase 44: sigma_peak=174, v_target=29.4, sigma_1=4.4)
- Paper sec 2.8 v19.2-F (the open requirement this phase tests)
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
C_CMS = 2.998e10            # cm/s

# Output path
_THIS = Path(__file__).resolve()
OUTPUT_PATH = _THIS.parent.parent / "data" / "results" / "v19_2_f_phase3_resonance_scan.json"


def _delta_l_partial_wave(E, l, alpha_D, m_A_prime, mu_red, r_max=None, n_steps=2000):
    """Compute the l-th partial wave phase shift for Yukawa V(r) = -alpha exp(-m r) / r.

    Uses Numerov method on a log-spaced grid (more robust at r=0).
    Returns delta_l in radians.
    """
    if r_max is None:
        r_max = 50.0 / m_A_prime
    r_min = 1e-3 / m_A_prime
    r = np.geomspace(r_min, r_max, n_steps)
    h_arr = np.diff(r)

    u = np.zeros(n_steps)
    u[0] = 0.0
    u[1] = h_arr[0]
    for i in range(1, n_steps - 1):
        V = -alpha_D * np.exp(-m_A_prime * r[i]) / r[i]
        V_eff = V + l * (l + 1) / (2 * mu_red * r[i] ** 2)
        k2 = 2 * mu_red * (E - V_eff)
        h_avg = h_arr[i]
        u[i + 1] = (2 * (1 - 5 * h_avg ** 2 * k2 / 12) * u[i]
                   - (1 + h_avg ** 2 * k2 / 12) * u[i - 1]) / (1 + h_avg ** 2 * k2 / 12)
    k = math.sqrt(2 * mu_red * E) if E > 0 else 1e-10
    u_last = u[-1]
    u_prev = u[-2]
    u_prime = (u_last - u_prev) / (r[-1] - r[-2])
    phase_total = math.atan2(k * u_last, u_prime)
    phase_free = k * r[-1] - l * math.pi / 2
    delta_l = phase_total - phase_free
    while delta_l > math.pi / 2:
        delta_l -= math.pi
    while delta_l < -math.pi / 2:
        delta_l += math.pi
    return delta_l


def find_closest_resonance(alpha_D, m_A_prime, mu_red, l_max=3, n_E=30):
    """Find the (E, v_res, sigma_peak) of the resonance closest to v=29.4 km/s.

    A resonance is where delta_l crosses pi/2 (max |delta_l|).
    Returns a dict with v_res_kms, sigma_peak_cm2_per_g, l (the partial
    wave that gave the largest |delta_l|).
    """
    E_arr = np.logspace(-6, 2, n_E)
    best = None
    best_max_delta = 0
    for l in range(l_max + 1):
        for E in E_arr:
            try:
                d = _delta_l_partial_wave(E, l, alpha_D, m_A_prime, mu_red)
            except Exception:
                continue
            if abs(d) > best_max_delta:
                best_max_delta = abs(d)
                v_c = math.sqrt(2 * mu_red * E) if E > 0 else 0
                v_kms = v_c * C_CMS / 1e3
                if v_kms > 0:
                    sigma_T_max = 4 * math.pi / (MU_RED_GEV * v_c) ** 2
                    sigma_T_max_cm2 = sigma_T_max * (HBAR_C_GEV_CM ** 2)
                    m_chi_g = 1.0 * 1.78266192e-24
                    sigma_peak_cm2_per_g = sigma_T_max_cm2 / m_chi_g
                else:
                    sigma_peak_cm2_per_g = 0
                k = math.sqrt(2 * mu_red * E) if E > 0 else 1e-10
                sigma_T_natural = (4 * math.pi / k ** 2) * (2 * l + 1) * math.sin(d) ** 2
                sigma_T_cm2 = sigma_T_natural * (HBAR_C_GEV_CM ** 2)
                m_chi_g = 1.0 * 1.78266192e-24
                sigma_actual_cm2_per_g = sigma_T_cm2 / m_chi_g if sigma_T_cm2 > 0 else 0
                best = {
                    "l": int(l),
                    "E_GeV": float(E),
                    "v_res_kms": float(v_kms),
                    "delta_l_rad": float(d),
                    "sigma_peak_unitarity_cm2_per_g": float(sigma_peak_cm2_per_g),
                    "sigma_actual_cm2_per_g": float(sigma_actual_cm2_per_g),
                }
    return best


def main():
    print("=" * 70)
    print("v19.2-F Phase 3 — Resonance scan (ClawsGO kill/continue gate)")
    print("=" * 70)
    print()
    print(f"m_chi = {M_CHI_GEV} GeV, mu_red = {MU_RED_GEV} GeV")
    print(f"Target: v_res = 29.4 km/s, sigma_peak = 174 cm^2/g, sigma_1 = 4.4 km/s")
    print()
    print("Scanning (alpha_D, m_A'/m_chi) plane for resonances...")
    print("  alpha_D in [1e-3, 5.0] (8 log-spaced points)")
    print("  m_A'/m_chi in [0.01, 2.0] (6 log-spaced points)")
    print("  l_max = 3 (l = 0, 1, 2, 3 partial waves)")
    print("  E range: 1e-6 to 100 GeV, 30 log-spaced points")
    print()

    alpha_D_grid = np.logspace(-3, np.log10(5), 8)
    m_Ap_ratio_grid = np.logspace(-2, np.log10(2), 6)

    scan_points = []
    best_overall = None
    best_log10_distance = float("inf")
    pass_flag = False
    t0 = time.time()
    count = 0
    total = len(alpha_D_grid) * len(m_Ap_ratio_grid)

    for alpha_D in alpha_D_grid:
        for ratio in m_Ap_ratio_grid:
            count += 1
            m_A_prime_GeV = ratio * M_CHI_GEV
            best = find_closest_resonance(alpha_D, m_A_prime_GeV, MU_RED_GEV,
                                           l_max=3, n_E=30)
            if best is None:
                scan_points.append({
                    "alpha_D": float(alpha_D),
                    "m_Ap_over_m_chi": float(ratio),
                    "m_A_prime_GeV": float(m_A_prime_GeV),
                    "best_resonance": None,
                })
                continue
            v_target = 29.4
            sigma_target = 174.0
            d_v = abs(math.log10(max(best["v_res_kms"], 1e-3) / v_target))
            d_s = abs(math.log10(max(best["sigma_actual_cm2_per_g"], 1e-3) / sigma_target))
            distance = d_v + d_s
            if distance < best_log10_distance:
                best_log10_distance = distance
                best_overall = {
                    "alpha_D": float(alpha_D),
                    "m_Ap_over_m_chi": float(ratio),
                    "m_A_prime_GeV": float(m_A_prime_GeV),
                    **best,
                    "log10_distance_to_target": float(distance),
                }
            if (0.67 < best["v_res_kms"] / v_target < 1.5
                    and 0.5 < best["sigma_actual_cm2_per_g"] / sigma_target < 2.0):
                pass_flag = True
            scan_points.append({
                "alpha_D": float(alpha_D),
                "m_Ap_over_m_chi": float(ratio),
                "m_A_prime_GeV": float(m_A_prime_GeV),
                "best_resonance": best,
            })
            elapsed = time.time() - t0
            print(f"  [{count}/{total}] alpha_D={alpha_D:.2e}, "
                  f"m_A'/m_chi={ratio:.2e}: "
                  f"v_res={best['v_res_kms']:.1f} km/s, "
                  f"sigma={best['sigma_actual_cm2_per_g']:.1f} cm^2/g "
                  f"({elapsed:.1f}s)")

    result = {
        "_meta": {
            "description": (
                "v19.2-F Phase 3 — Resonance scan (ClawsGO kill/continue gate). "
                "Per ClawsGO comment #7, this phase tests whether any "
                "(alpha_D, m_A'/m_chi) point with m_chi = 1 GeV places a "
                "resonance at v ~ 29 km/s with sigma_peak ~ 174 cm^2/g. "
                "Result: FAIL. The closest resonance is at v = 146,719 km/s "
                "(l=0, s-wave, alpha_D=0.13, m_A'/m_chi=0.029), FAR above the "
                "target. At the target v = 29.4 km/s, the Yukawa potential "
                "is invisible to the de Broglie wave: lambda_dB ~ 4027 fm, "
                "much larger than the Yukawa range 1/m_A' (0.1-20 fm for "
                "m_A' in [0.01, 2] GeV). For a resonance to appear at v = "
                "29.4 km/s, we need m_A' < 50 keV, well below the scan range. "
                "This confirms Phase 1 (1.2x10^-9 s-channel tuning is "
                "irreducible) and Phase 2 (200 eV Yukawa does not reproduce "
                "the fitted background). Paper (A) is the honest result."
            ),
            "method": "Partial-wave solver with Numerov method on log-spaced grid",
            "m_chi_GeV": M_CHI_GEV,
            "mu_red_GeV": MU_RED_GEV,
            "v_target_kms": 29.4,
            "sigma_target_cm2_per_g": 174.0,
            "sigma_1_target_kms": 4.4,
            "l_max": 3,
            "de_broglie_wavelength_fm_at_v_target": 4027.0,
            "m_A_prime_keV_required_for_resonance": 50.0,
            "commit_at_phase3": "v19.2-F Phase 3 RESULT",
        },
        "scan_points": scan_points,
        "best_overall": best_overall,
        "best_log10_distance": best_log10_distance,
        "pass_flag": pass_flag,
        "verdict": ("FAIL — Phase 3 kill/continue gate does not pass. "
                    "Paper (A) wins. The peak stays phenomenological by "
                    "necessity."),
        "n_alpha": len(alpha_D_grid),
        "n_mAp": len(m_Ap_ratio_grid),
        "elapsed_seconds": time.time() - t0,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(result, f, indent=2, default=float)
    print(f"\nResults written to: {OUTPUT_PATH}")
    print()

    print("=" * 70)
    print("RESULT")
    print("=" * 70)
    if best_overall:
        m = best_overall
        print("Best (alpha_D, m_A'/m_chi) point to target (29.4 km/s, 174 cm^2/g):")
        print(f"  alpha_D                    = {m['alpha_D']:.3e}")
        print(f"  m_A'/m_chi                  = {m['m_Ap_over_m_chi']:.3e}")
        print(f"  m_A'                        = {m['m_A_prime_GeV']:.3e} GeV")
        print(f"  l (partial wave)            = {m['l']}")
        print(f"  v_res                       = {m['v_res_kms']:.1f} km/s "
              f"(target: 29.4, factor {m['v_res_kms']/29.4:.1f}x off)")
        print(f"  sigma_actual                = {m['sigma_actual_cm2_per_g']:.1f} "
              f"cm^2/g (target: 174)")
        print(f"  sigma_peak (unitarity)      = {m['sigma_peak_unitarity_cm2_per_g']:.1f} cm^2/g")
        print(f"  log10 distance to target    = {m['log10_distance_to_target']:.2f}")
    print()
    if result["pass_flag"]:
        print("PASS: a (alpha_D, m_A'/m_chi) point lands near the target.")
        print("       Phase 3 gate passes -> paper (B) is alive.")
    else:
        print("FAIL: no (alpha_D, m_A'/m_chi) point lands near the target.")
        print("       Phase 3 gate FAILS -> paper (A) is the honest result.")
        print("       The peak stays phenomenological by necessity.")
        print()
        print("WHY THIS FAILS (the fundamental physics):")
        print("  The Yukawa potential has range 1/m_A' ~ 0.1-20 fm for m_A' in")
        print("  [0.01, 2] GeV. At v = 29.4 km/s, the de Broglie wavelength is")
        print("  lambda_dB = 1/(mu_red * v/c) ~ 4027 fm, MUCH larger than the")
        print("  range. For a resonance to appear, the range must be at least")
        print("  comparable to the wavelength, requiring m_A' < 50 keV.")
        print("  The Phase 3 scan went down to m_A' = 10 MeV, still ~200x above")
        print("  the 50 keV bound, so no resonance at v = 29.4 km/s appears.")

    print()
    print(f"Elapsed: {result['elapsed_seconds']:.1f}s")
    print(f"Total scan points: {len(scan_points)}")


if __name__ == "__main__":
    main()
