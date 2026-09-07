"""
T90.22 (Option B) — Re-calibrate master Yukawa against Robertson 2019.

PURPOSE
=======
Per T95_CONSOLIDATED_RESULTS.md, the master's single-component Yukawa
sigma/m is ~30% LOW relative to Robertson's BAHAMAS-SIDM vdSIDM
prescription (geometric mean ratio 0.72 across v=100-1500 km/s).

Option B: Re-calibrate the master sigma_m_0 and velocity exponent a
to better match Robertson's published prescription:
  - Robertson: sigma_T(v) = sigma_0 / (1 + (v/w)^2)
    with sigma_0 = 3.04 cm^2/g, w = 560 km/s (for v = 100 km/s point)
  - Master: sigma/m(v) = sigma_m_0 * (V_REF / v)^a
    with sigma_m_0 = 0.7 cm^2/g at V_REF = 100, a = 0.16

The 30% offset is real and reflects either:
  1. A calibration drift in the master prescription
  2. The T89-known factor 2-4 master-vs-sidmkit offset (Born distinguishable vs identical particles)
  3. Different conventions for sigma_0 (Robertson uses peak, master uses reference velocity)

This module:
  1. Implements Robertson's BAHAMAS-SIDM prescription directly
  2. Implements the master Yukawa sigma/m(v) formula
  3. Computes the calibration factor needed to bring master in line with Robertson
  4. Re-runs T95 tension evaluation with the re-calibrated master

KEY INSIGHT: Re-calibration will INCREASE the master sigma/m
(making the tension WORSE for cluster scales). But it should
better match Robertson directly, which is what the project
commitments require.

OUTPUT
  - outputs/t90/t95_recalibrated_yukawa.json
  - Master sigma_m_0 and a parameters after re-calibration
  - Robertson vs master ratio across velocity scales
  - T95 tension re-evaluation

REFERENCES
  Robertson, A. et al. 2019, MNRAS 488, 3646 (BAHAMAS-SIDM)
  T95_CONSOLIDATED_RESULTS.md (the T95 tension this addresses)
  v0.3-prelim/code/t40_yukawa_sigma_m.py (master Yukawa)

STATUS: SHIPPED 2026-09-07
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

_PROJECT_ROOT = Path(__file__).resolve().parents[1]


# ============================================================================
# Robertson 2019 BAHAMAS-SIDM vdSIDM prescription
# ============================================================================
# From Robertson 2019, MNRAS 488, 3646, Eq 1 + Table:
#   sigma_T(v) = sigma_0 / (1 + (v/w)^2)
# with sigma_0 = 3.04 cm^2/g and w = 560 km/s for their fiducial model.

ROBERTSON_SIGMA_0_CM2_G = 3.04
ROBERTSON_W_KMS = 560.0


def sigma_m_robertson(v_kms: float) -> float:
    """Robertson 2019 BAHAMAS-SIDM vdSIDM sigma/m at velocity v.

    sigma_T(v) = sigma_0 / (1 + (v/w)^2)

    Args:
      v_kms: relative velocity in km/s

    Returns:
      sigma/m in cm^2/g
    """
    return ROBERTSON_SIGMA_0_CM2_G / (1.0 + (v_kms / ROBERTSON_W_KMS) ** 2)


# ============================================================================
# Master single-component Yukawa
# ============================================================================
MASTER_SIGMA_M_0 = 0.7  # cm^2/g at v = 100 km/s
MASTER_A = 0.16
MASTER_V_REF = 100.0


def sigma_m_master(v_kms: float, sigma_m_0: float = MASTER_SIGMA_M_0, a: float = MASTER_A) -> float:
    """Master single-component Yukawa sigma/m at velocity v.

    sigma/m(v) = sigma_m_0 * (V_REF / v)^a

    Args:
      v_kms: relative velocity in km/s
      sigma_m_0: amplitude at V_REF (default 0.7 cm^2/g)
      a: velocity exponent (default 0.16)

    Returns:
      sigma/m in cm^2/g
    """
    return sigma_m_0 * (MASTER_V_REF / v_kms) ** a


# ============================================================================
# Re-calibration: fit master sigma_m_0 and a to Robertson
# ============================================================================
def fit_master_to_robertson(v_test_points: list = None) -> dict:
    """Fit master sigma_m_0 and a to match Robertson across velocity scales.

    Use simple grid search or least-squares fit to find optimal (sigma_m_0, a)
    that minimizes sum of squared log(ratio) between master and Robertson.

    Args:
      v_test_points: list of velocities in km/s (default: 10-1500)

    Returns:
      Dict with fitted sigma_m_0, a, geometric mean ratio
    """
    if v_test_points is None:
        v_test_points = [10, 30, 50, 100, 150, 300, 500, 750, 1000, 1500]

    robertson_values = np.array([sigma_m_robertson(v) for v in v_test_points])

    best_ratio_log = float('inf')
    best_params = (MASTER_SIGMA_M_0, MASTER_A)
    best_gm_ratio = 1.0

    # Grid search over (sigma_m_0, a)
    for sigma_m_0 in np.linspace(0.5, 5.0, 50):
        for a in np.linspace(0.05, 0.5, 30):
            master_values = np.array([sigma_m_master(v, sigma_m_0, a) for v in v_test_points])
            ratios = master_values / robertson_values
            log_ratios = np.log(ratios)
            sum_sq_log_ratio = np.sum(log_ratios ** 2)
            if sum_sq_log_ratio < best_ratio_log:
                best_ratio_log = sum_sq_log_ratio
                best_params = (sigma_m_0, a)
                best_gm_ratio = float(np.exp(np.mean(log_ratios)))

    return {
        'best_sigma_m_0': float(best_params[0]),
        'best_a': float(best_params[1]),
        'geometric_mean_ratio': best_gm_ratio,
        'log_residual_sum_sq': float(best_ratio_log),
        'v_test_points': v_test_points,
    }


# ============================================================================
# T95 tension re-evaluation with re-calibrated master
# ============================================================================
def t95_tension_recalibrated(v_kms_cluster: float = 150) -> dict:
    """Re-evaluate T95 cross-check tension with re-calibrated master.

    Args:
      v_kms_cluster: cluster velocity in km/s (default 150)

    Returns:
      Dict with re-calibrated sigma/m and tension
    """
    # Re-calibrate
    fit = fit_master_to_robertson()
    new_sigma_m_0 = fit['best_sigma_m_0']
    new_a = fit['best_a']

    # Master (old and new)
    s_master_old = sigma_m_master(v_kms_cluster, MASTER_SIGMA_M_0, MASTER_A)
    s_master_new = sigma_m_master(v_kms_cluster, new_sigma_m_0, new_a)

    # Robertson
    s_robertson = sigma_m_robertson(v_kms_cluster)

    # Euclid Q1 forecast range
    euclid_lower = 0.05
    euclid_upper = 0.10
    sigma_obs = (euclid_lower + euclid_upper) / 2  # 0.075

    # Rough log Z estimates
    log_z_old = -0.5 * ((s_master_old - sigma_obs) / sigma_obs) ** 2
    log_z_new = -0.5 * ((s_master_new - sigma_obs) / sigma_obs) ** 2

    return {
        'v_kms': v_kms_cluster,
        'master_old_sigma_m': s_master_old,
        'master_new_sigma_m': s_master_new,
        'robertson_sigma_m': s_robertson,
        'old_to_robertson_ratio': s_master_old / s_robertson,
        'new_to_robertson_ratio': s_master_new / s_robertson,
        'recalibration_factor': s_master_new / s_master_old,
        'euclid_q1_forecast_range': (euclid_lower, euclid_upper),
        'ratio_old_to_euclid': s_master_old / sigma_obs,
        'ratio_new_to_euclid': s_master_new / sigma_obs,
        'rough_log_z_old': log_z_old,
        'rough_log_z_new': log_z_new,
        'tension_old': 'substantial' if abs(log_z_old) > 1.0 else 'moderate',
        'tension_new': 'substantial' if abs(log_z_new) > 1.0 else 'moderate' if abs(log_z_new) > 0.5 else 'weak' if abs(log_z_new) > 0.1 else 'none',
    }


# ============================================================================
# Main
# ============================================================================
def main():
    print("=" * 70)
    print("T90.22 (Option B) — Re-calibrate master Yukawa against Robertson 2019")
    print("=" * 70)
    print()

    # Step 1: Compare master vs Robertson across velocities
    print("Master vs Robertson across velocity scales:")
    print(f"  {'v [km/s]':<12} {'Robertson':<12} {'Master (old)':<14} {'Ratio':<10}")
    print(f"  {'-'*12} {'-'*12} {'-'*14} {'-'*10}")

    v_points = [10, 30, 50, 100, 150, 300, 500, 750, 1000, 1500]
    for v in v_points:
        s_rob = sigma_m_robertson(v)
        s_master = sigma_m_master(v)
        ratio = s_master / s_rob
        print(f"  {v:<12} {s_rob:<12.3f} {s_master:<14.3f} {ratio:<10.3f}")
    print()

    # Step 2: Re-calibrate
    print("Re-calibration fit (minimize sum of squared log ratios):")
    fit = fit_master_to_robertson(v_points)
    print(f"  Old sigma_m_0 = {MASTER_SIGMA_M_0} cm^2/g, a = {MASTER_A}")
    print(f"  New sigma_m_0 = {fit['best_sigma_m_0']:.3f} cm^2/g, a = {fit['best_a']:.3f}")
    print(f"  Geometric mean ratio after re-calibration: {fit['geometric_mean_ratio']:.3f}")
    print(f"  -> Closer to 1.0 means better match to Robertson")
    print()

    # Step 3: Re-calibrated sigma/m across velocities
    print("Re-calibrated master sigma/m:")
    print(f"  {'v [km/s]':<12} {'Robertson':<12} {'Old master':<14} {'New master':<14} {'Ratio old':<10} {'Ratio new':<10}")
    print(f"  {'-'*12} {'-'*12} {'-'*14} {'-'*14} {'-'*10} {'-'*10}")
    new_sigma_m_0 = fit['best_sigma_m_0']
    new_a = fit['best_a']
    recal_results = {}
    for v in v_points:
        s_rob = sigma_m_robertson(v)
        s_old = sigma_m_master(v)
        s_new = sigma_m_master(v, new_sigma_m_0, new_a)
        r_old = s_old / s_rob
        r_new = s_new / s_rob
        print(f"  {v:<12} {s_rob:<12.3f} {s_old:<14.3f} {s_new:<14.3f} {r_old:<10.3f} {r_new:<10.3f}")
        recal_results[f'v_{v}_km_s'] = {
            'robertson': float(s_rob),
            'master_old': float(s_old),
            'master_new': float(s_new),
            'ratio_old': float(r_old),
            'ratio_new': float(r_new),
        }
    print()

    # Step 4: T95 tension re-evaluation
    print("T95 tension re-evaluation with re-calibrated master (v=150 km/s):")
    tension = t95_tension_recalibrated(150)
    print(f"  Master old sigma/m:    {tension['master_old_sigma_m']:.3f} cm^2/g")
    print(f"  Master new sigma/m:    {tension['master_new_sigma_m']:.3f} cm^2/g")
    print(f"  Robertson sigma/m:     {tension['robertson_sigma_m']:.3f} cm^2/g")
    print(f"  Re-calibration factor: {tension['recalibration_factor']:.2f}x (sigma/m changed by)")
    print(f"  Old ratio to Euclid:   {tension['ratio_old_to_euclid']:.2f}x")
    print(f"  New ratio to Euclid:   {tension['ratio_new_to_euclid']:.2f}x")
    print(f"  Rough log Z old:       {tension['rough_log_z_old']:.2f}")
    print(f"  Rough log Z new:       {tension['rough_log_z_new']:.2f}")
    print(f"  Tension classification:")
    print(f"    Old: {tension['tension_old']}")
    print(f"    New: {tension['tension_new']}")
    print()

    # Save output
    out_path = _PROJECT_ROOT / "outputs" / "t90" / "t95_recalibrated_yukawa.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    output = {
        'phase': 'T90.22 (Option B — Re-calibrate master Yukawa)',
        'description': 'Fit master sigma_m_0 and a to match Robertson 2019 BAHAMAS-SIDM',
        'robertson_prescription': {
            'sigma_0_cm2_g': ROBERTSON_SIGMA_0_CM2_G,
            'w_kms': ROBERTSON_W_KMS,
            'reference': 'Robertson et al. 2019, MNRAS 488, 3646',
        },
        'master_old': {
            'sigma_m_0': MASTER_SIGMA_M_0,
            'a': MASTER_A,
        },
        'master_new': fit,
        'velocity_dependent_sigma_m': recal_results,
        't95_tension_cluster_v150': tension,
        'key_findings': {
            'recalibration_factor': tension['recalibration_factor'],
            'old_to_robertson_ratio': tension['old_to_robertson_ratio'],
            'new_to_robertson_ratio': tension['new_to_robertson_ratio'],
            'cluster_tension_classification_old': tension['tension_old'],
            'cluster_tension_classification_new': tension['tension_new'],
        },
        'caveats': [
            'Re-calibration makes the master MATCH Robertson better, but INCREASES sigma/m above Euclid Q1 forecast',
            'Robertson uses a Yukawa-like form (1/(1+(v/w)^2)), not power-law',
            'The 30% offset may be intrinsic to the master prescription vs Robertson conventions',
            'A proper fit would use Robertson Table 1 directly',
        ],
        'references': [
            'Robertson et al. 2019, MNRAS 488, 3646 (BAHAMAS-SIDM)',
            'T95_CONSOLIDATED_RESULTS.md (the T95 tension this addresses)',
            'T89_SIDMKIT_SIDMVDSIGMAS_BENCHMARK.md (T89 calibration benchmark)',
        ],
    }
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"Wrote: {out_path}")


if __name__ == '__main__':
    main()