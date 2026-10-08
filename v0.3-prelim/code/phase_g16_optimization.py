"""
Phase G16 — Multi-parameter optimization (R88(67) + R88(68) self-correction)

Phase G13: 2/15 simple shapes break v=150 trade-off, but fail other channels
Phase G14: even tuned versions of trade-off-breaking shapes fail Cloud-9
Phase G15: environment-dependent shapes pass 5/8 but Lei/Wang fails

This phase does EXHAUSTIVE multi-parameter optimization:
- 5 free parameters: sigma_peak_cloud9, sigma_peak_massive, sigma_peak_ufd,
                      width_cloud9, f_H_central, f_H_subhalo
- Optimize to maximize channels passing
- Use brute-force grid search

The goal: find ANY parameter combination that passes ≥6/8 channels
including the v=150 trade-off.

============================================================================
R88(68) SELF-CORRECTION
============================================================================
The "8/8 channels pass" result reported in R88(67) does NOT survive scrutiny:

1. DOUBLE-COUNTING: Phase G16 reduces both the v=150 peak amplitude (0.3x)
   AND applies a separate f_H_sub = 0.05. But the physical mechanism is
   tidal stripping which reduces f_H, not sigma_m itself. The 0.3x peak
   reduction and the f_H reduction are not independent effects.

2. CONTRADICTS PHASE G9: The required f_H drop from 0.6 to 0.05 is a
   factor of 12x. Phase G9 (R88(54)) measured the tidal-stripping f_H
   drop factor as 0.94-1.01x (FAIL of the >=2x kill criterion). Phase G16
   requires 12x more f_H reduction than the N-body discriminator found.

3. UNMOTIVATED HIGH-v CUTOFF: The v_cutoff=300 km/s parameter is an
   additional free function with no physical derivation. The paper's
   canonical sigma/m(v) (Gaussian resonance + power-law background) has
   no such feature.

4. OVERFITTING: With 6 parameters and 8 channels, a brute-force search
   over ~11,000 combinations will find some combination that passes all
   thresholds by chance. This is fitting, not physical prediction.

CORRECT FRAMING (R88(68)):
The structural trade-off theorem stands as the fundamental limit of
single-species or simple two-species SIDM with Phase 44 parameters.

The framework CAN satisfy all channels if environment-dependent sigma_m(v)
with independently tuned shapes for centrals and subhalos is allowed.
However, this requires a f_H drop of 12x that is inconsistent with the
Phase G9 N-body discriminator (0.94-1.01x). The "breakthrough" is
therefore a parameter-fitting result, not a physical resolution.

The R88(56) honest synthesis remains authoritative:
"The two structural no-gos survive both physically-motivated segregation
(Phase G9) and first-principles SIDM2c parameterization (Phase G10).
They are stronger findings, not weaker."

This module is retained for documentation purposes only. The
"8/8 channels pass" claim is hereby retracted.
============================================================================
"""
from __future__ import annotations
import math
import numpy as np


def sigma_m_parametric(v, peak_c9, peak_mass, peak_ufd, width_c9, v_cutoff=300, cutoff_sharp=50):
    """Parametric σ_m(v) with adjustable peaks and high-v cutoff."""
    bg = 0.07 * (100 / v) ** 0.9
    cloud9 = peak_c9 * math.exp(-((v - 28) ** 2) / (2 * width_c9 ** 2))
    massive = peak_mass * math.exp(-((v - 150) ** 2) / 1500)
    ufd = peak_ufd * math.exp(-((v - 10) ** 2) / 12.5)
    sm = bg + cloud9 + massive + ufd
    # High-v cutoff for cluster compliance
    if v > v_cutoff:
        sm *= math.exp(-(v - v_cutoff) / cutoff_sharp)
    return sm


def evaluate_channels(params):
    """Evaluate all channels for given parameters."""
    peak_c9, peak_mass, peak_ufd, width_c9, f_H_cen, f_H_sub = params

    sm_centers = lambda v: sigma_m_parametric(v, peak_c9, peak_mass, peak_ufd, width_c9)
    sm_subs = lambda v: sigma_m_parametric(v, peak_c9, peak_mass * 0.3, peak_ufd, width_c9)  # subhalo: reduced massive peak

    # Channel definitions: (name, v, r_obs, thresh_type, thresh_val, is_subhalo)
    channels = [
        ("Horigome dSph (subhalo)", 15, 6.0, "<", 0.8, True),
        ("Fischer&Yu UFD (subhalo)", 7, 1.0, "tau_proxy", None, True),
        ("Cloud-9 inner (central)", 28, 0.5, ">", 50, False),
        ("Cloud-9 V_max (central)", 31.12, 0.5, ">", 50, False),
        ("SPARC typical (central)", 100, 1.5, "~", 0.19, False),
        ("Lei/Wang (central)", 150, 1.5, "range", (0.1, 0.3), False),
        ("Sameie+ 2020 (subhalo)", 150, 1.5, "<", 0.3, True),
        ("Cluster (central)", 500, 1.0, "<", 0.001, False),
    ]

    results = []
    for name, v, r_obs, thresh_type, thresh_val, is_subhalo in channels:
        f_h = f_H_sub if is_subhalo else f_H_cen
        sm_func = sm_subs if is_subhalo else sm_centers
        sm_v = sm_func(v)
        sigma_eff = f_h ** 2 * sm_v

        if thresh_type == "tau_proxy":
            ok = sm_v > 1.0
        elif thresh_type == "<":
            ok = sigma_eff < thresh_val
        elif thresh_type == ">":
            ok = sigma_eff > thresh_val
        elif thresh_type == "~":
            ok = 0.3 < (sigma_eff / thresh_val) < 3
        elif thresh_type == "range":
            lo, hi = thresh_val
            ok = lo < sigma_eff < hi

        results.append((name, ok, sigma_eff))

    return results


def run_phase_g16():
    print("=" * 90)
    print("Phase G16 — Multi-Parameter Optimization (R88(67))")
    print("=" * 90)
    print()
    print("Optimizing 6 parameters to maximize channels passing.")
    print("Parameters:")
    print("  peak_c9: Cloud-9 peak height (200-500)")
    print("  peak_mass: v=150 peak height (0.5-10)")
    print("  peak_ufd: UFD peak height (30-100)")
    print("  width_c9: Cloud-9 peak width (1-6 km/s)")
    print("  f_H_cen: heavy fraction at observation in centrals (0.3-0.6)")
    print("  f_H_sub: heavy fraction at observation in subhalos (0.05-0.3)")
    print()

    best_n_pass = 0
    best_params = None
    best_results = None

    # Grid search
    for peak_c9 in [200, 300, 400, 500]:
        for peak_mass in [0.5, 1, 2, 3, 5, 7, 10]:
            for peak_ufd in [30, 50, 70, 100]:
                for width_c9 in [1, 2, 3, 4, 6]:
                    for f_H_cen in [0.3, 0.4, 0.5, 0.6]:
                        for f_H_sub in [0.05, 0.1, 0.15, 0.2, 0.3]:
                            params = (peak_c9, peak_mass, peak_ufd, width_c9, f_H_cen, f_H_sub)
                            results = evaluate_channels(params)
                            n_pass = sum(1 for _, ok, _ in results if ok)
                            if n_pass > best_n_pass:
                                best_n_pass = n_pass
                                best_params = params
                                best_results = results

    print(f"Best result: {best_n_pass}/8 channels")
    print(f"Best parameters: peak_c9={best_params[0]}, peak_mass={best_params[1]}, peak_ufd={best_params[2]}")
    print(f"  width_c9={best_params[3]}, f_H_cen={best_params[4]}, f_H_sub={best_params[5]}")
    print()
    print("Channel breakdown:")
    for name, ok, se in best_results:
        marker = "✓" if ok else "✗"
        print(f"  {marker} {name}: σ_eff = {se:.4f}")

    print()
    if best_n_pass >= 7:
        print("=" * 90)
        print("Phase G16 verdict (R88(67))")
        print("=" * 90)
        print()
        print(f"SUCCESS: {best_n_pass}/8 channels passing with optimized parameters")
        print("The structural trade-off theorem can be partially broken with")
        print("specific parameter combinations (environment-dependent σ_m + tuned peaks).")
    elif best_n_pass >= 6:
        print(f"PARTIAL: {best_n_pass}/8 channels passing")
        print("The trade-off is not fully broken but can be partially mitigated.")
    else:
        print(f"FAILURE: Only {best_n_pass}/8 channels pass even with optimization")
        print("The structural trade-off theorem stands as fundamental limit.")

    return best_n_pass, best_params


if __name__ == "__main__":
    n_pass, params = run_phase_g16()
