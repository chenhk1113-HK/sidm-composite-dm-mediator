"""
T95.6 — Two-component SIDM with mass segregation (Yang+ 2026).

PURPOSE
=======
Implement the Yang+ 2026 two-component SIDM model as a candidate
*replacement* for the single-component master Yukawa. Per the
paper (arXiv:2506.14898, Science China Phys. 2026):

  "Two-component SIDM with mass segregation can explain BOTH
   dwarf galaxy cores AND small-scale lens excess observed in
   galaxy-galaxy strong lensing. Unlike one-component SIDM,
   this framework is consistent with cluster-scale sigma/m
   constraints (sigma/m < 0.1 cm^2/g at v ~ 1000 km/s)."

This addresses the T95 cross-check findings (T95_CONSOLIDATED_RESULTS.md):
  - Single-component Yukawa at v ~ 150 km/s: sigma/m ~ 0.7 cm^2/g
  - Euclid Q1 sub-halo forecast: sigma/m in [0.05, 0.10] cm^2/g
  - Delta log log Z = -1.57 (substantial tension)

The Yang+ 2026 model produces dwarf cores via mass segregation
WITHOUT requiring large sigma/m at cluster scales. This may
resolve the tension.

MODEL (from paper Section II):
  Two components:
    chi_H (heavy): m_H = 3 m_L
    chi_L (light): m_L

  Intra-species (heavy-heavy):
    sigma_0/m_H = 6.89 cm^2/g
    w = 275 km/s (velocity scale)

  Intra-species (light-light):
    sigma_L/m_L = (1/3) sigma_H/m_H = 2.30 cm^2/g
    w_L = 3 * w_H = 825 km/s

  Inter-species (heavy-light):
    sigma_x/m_H = 1.125 cm^2/g
    w_x = 2200 km/s

KEY PREDICTIONS:
  - Dwarf halos (M ~ 10^11 M_sun): cored profiles, sigma/m ~ 0.3 cm^2/g
    (matches Zhang+ 2025 dwarf clustering)
  - Cluster halos (M ~ 10^15 M_sun): sigma/m < 0.1 cm^2/g
    (consistent with cluster lensing, e.g., Meneghetti+)
  - Strong lensing: small-scale lenses enhanced by factor ~3-6
    (matches Meneghetti+ excess)

OUTPUT
  - outputs/t95/two_component_sidm_yang2026.json
  - Per-velocity sigma/m for both intra- and inter-species
  - Comparison to master single-component Yukawa
  - Mass-segregation correction to effective sigma/m

REFERENCES
  Yang, D. et al. 2026, Science China Phys., arXiv:2506.14898
  "Self-interacting dark matter with mass segregation: a unified
   explanation of dwarf cores and small-scale lenses"
  Zhang, Y. et al. 2025 (dwarf clustering, sigma/m ~ 0.3 cm^2/g)
  Meneghetti, M. et al. (small-scale lens excess, factor 3-6)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

_PROJECT_ROOT = Path(__file__).resolve().parents[1]


# ============================================================================
# Yang+ 2026 two-component SIDM parameters
# ============================================================================
# Intra-species (heavy-heavy, chi_H-chi_H)
SIGMA_H_INTRA_M_H_CM2_G = 6.89  # at v = w_H = 275 km/s
W_H_KMS = 275.0  # velocity scale for chi_H-chi_H

# Intra-species (light-light, chi_L-chi_L)
# Per paper: sigma_L/m_L = (1/3) sigma_H/m_H = 2.30 cm^2/g
SIGMA_L_INTRA_M_L_CM2_G = SIGMA_H_INTRA_M_H_CM2_G / 3.0  # 2.30
W_L_KMS = 3.0 * W_H_KMS  # 825 km/s (same mediator, mass-rescaled velocity)

# Inter-species (heavy-light, chi_H-chi_L)
SIGMA_X_INTER_M_H_CM2_G = 1.125  # at v = w_x = 2200 km/s
W_X_KMS = 2200.0  # velocity scale for inter-species

# Mass ratio
M_H_OVER_M_L = 3.0  # m_H = 3 m_L

# Velocity-dependence model: Rutherford/Moller parametrization
# Approximate: sigma(v) ~ sigma_0 / (1 + (v/w)^2)^2  (Yukawa-like)


def sigma_intra_heavy(v_kms: float) -> float:
    """Effective sigma/m for heavy-heavy scattering at velocity v.

    From Yang+ 2026 model SIDM2v:
      sigma(v) = sigma_0 / (1 + (v/w)^2)^2

    Parameters:
      v_kms: relative velocity in km/s

    Returns:
      sigma/m in cm^2/g
    """
    return SIGMA_H_INTRA_M_H_CM2_G / (1.0 + (v_kms / W_H_KMS) ** 2) ** 2


def sigma_intra_light(v_kms: float) -> float:
    """Effective sigma/m for light-light scattering at velocity v.

    Same mediator as heavy-heavy, but with mass-rescaled velocity
    scale (w_L = 3 * w_H).

    Parameters:
      v_kms: relative velocity in km/s

    Returns:
      sigma/m in cm^2/g
    """
    return SIGMA_L_INTRA_M_L_CM2_G / (1.0 + (v_kms / W_L_KMS) ** 2) ** 2


def sigma_inter(v_kms: float) -> float:
    """Effective sigma/m for inter-species (heavy-light) scattering.

    Parameters:
      v_kms: relative velocity in km/s

    Returns:
      sigma/m in cm^2/g
    """
    return SIGMA_X_INTER_M_H_CM2_G / (1.0 + (v_kms / W_X_KMS) ** 2) ** 2


def effective_sigma_m_two_component(v_kms: float) -> float:
    """Effective total sigma/m for two-component SIDM at velocity v.

    For equal number densities (n_H = n_L, with m_H = 3 m_L):
      Mass fractions: f_H = m_H / (m_H + m_L) = 3/4
                     f_L = m_L / (m_H + m_L) = 1/4

    The effective sigma/m is the mass-weighted average of the
    cross sections, weighted by the contribution to the total scattering
    rate.

    IMPORTANT CAVEAT: This is a NAIVE mass-weighted average that does
    NOT capture the gravothermal evolution described in Yang+ 2026.
    In the full model, mass segregation enhances central densities
    in dwarf halos (factor 2-5) but barely affects cluster halos
    (factor ~1). The cluster bound (sigma/m < 0.1 cm^2/g at
    v ~ 1000 km/s) emerges from gravothermal evolution, not from the
    raw scattering rate.

    The simple mass-weighted average OVER-ESTIMATES the cluster
    sigma/m and UNDER-ESTIMATES the dwarf sigma/m. To get the
    Yang+ 2026 paper's exact values, one would need to:
      1. Run cosmological/zoom-in simulations of each halo
      2. Track gravothermal evolution over cosmic time
      3. Compute the resulting density profile and effective sigma/m

    For this script, we use a simple approximation that captures the
    velocity dependence and approximate mass scaling, but does NOT
    include gravothermal evolution.

    Parameters:
      v_kms: relative velocity in km/s

    Returns:
      Effective sigma/m in cm^2/g
    """
    # Get individual cross sections (each as sigma/m for that component)
    s_hh = sigma_intra_heavy(v_kms)  # cm^2/g, per m_H
    s_ll = sigma_intra_light(v_kms)  # cm^2/g, per m_L
    s_xl = sigma_inter(v_kms)  # cm^2/g, per m_H (the heavier one)

    # Mass fractions
    f_H = M_H_OVER_M_L / (1.0 + M_H_OVER_M_L)  # 0.75
    f_L = 1.0 / (1.0 + M_H_OVER_M_L)  # 0.25

    # Effective sigma/m = mass-fraction-weighted contributions
    sigma_eff = f_H * s_hh + f_L * s_ll + 2 * f_H * f_L * s_xl
    return sigma_eff


# ============================================================================
# Mass-segregation enhancement (Yang+ 2026 key result)
# ============================================================================
def mass_segregation_enhancement(v_kms: float, M_halo_M_sun: float) -> float:
    """Enhancement factor from mass segregation (Yang+ 2026 key result).

    The paper shows that mass segregation can ENHANCE the central
    density by a factor of a few at small radii, particularly for
    dwarf halos.

    Approximate enhancement factor (from paper Section II + III):
      - Dwarf halos (M ~ 10^11 M_sun): enhancement ~ 2-5
      - Cluster halos (M ~ 10^15 M_sun): enhancement ~ 1-2
        (less time for segregation to develop)

    Parameters:
      v_kms: halo characteristic velocity in km/s
      M_halo_M_sun: halo mass in M_sun

    Returns:
      Enhancement factor (multiplicative)
    """
    # Simple scaling: enhancement = max(1, 5 - 4*log10(M_halo/1e11))
    # Dwarf (M = 1e11): enhancement = 5 - 0 = 5
    # Cluster (M = 1e15): enhancement = 5 - 16 = -11 -> clamped to 1
    log_M = np.log10(M_halo_M_sun / 1e11)
    enhancement = max(1.0, 5.0 - 4.0 * log_M)
    return enhancement


def sigma_m_with_segregation(v_kms: float, M_halo_M_sun: float) -> float:
    """Effective sigma/m including mass-segregation enhancement."""
    base = effective_sigma_m_two_component(v_kms)
    enh = mass_segregation_enhancement(v_kms, M_halo_M_sun)
    return base * enh


# ============================================================================
# Comparison to master single-component Yukawa
# ============================================================================
def master_yukawa_sigma_m(v_kms: float) -> float:
    """Master Yukawa sigma/m at velocity v.

    From the project's T89 calibration:
      sigma/m(v) = sigma_m_0 * (V_REF / v)^a
    where V_REF = 100 km/s, sigma_m_0 = 0.7 cm^2/g, a = 0.16.

    Parameters:
      v_kms: velocity in km/s

    Returns:
      sigma/m in cm^2/g
    """
    sigma_m_0 = 0.7  # cm^2/g at v = 100 km/s
    a = 0.16
    V_REF = 100.0
    return sigma_m_0 * (V_REF / v_kms) ** a


# ============================================================================
# Main
# ============================================================================
def main():
    print("=" * 70)
    print("T95.6 — Two-component SIDM with mass segregation (Yang+ 2026)")
    print("       arXiv:2506.14898, Science China Phys. 2026")
    print("=" * 70)
    print()
    print("MODEL PARAMETERS:")
    print(f"  Heavy component: m_H = {M_H_OVER_M_L:.0f} m_L")
    print(f"  Intra HH: sigma_0/m_H = {SIGMA_H_INTRA_M_H_CM2_G} cm^2/g, w = {W_H_KMS} km/s")
    print(f"  Intra LL: sigma_0/m_L = {SIGMA_L_INTRA_M_L_CM2_G:.3f} cm^2/g, w = {W_L_KMS} km/s")
    print(f"  Inter HL: sigma_0/m_H = {SIGMA_X_INTER_M_H_CM2_G} cm^2/g, w = {W_X_KMS} km/s")
    print()

    print("VELOCITY-DEPENDENT sigma/m:")
    print(f"  {'v [km/s]':<12} {'Intra HH':<12} {'Intra LL':<12} {'Inter HL':<12} "
          f"{'2-comp eff':<12} {'+ segreg':<12} {'Master Yuk':<12} {'Ratio':<10}")
    print(f"  {'-'*12} {'-'*12} {'-'*12} {'-'*12} {'-'*12} {'-'*12} {'-'*12} {'-'*10}")
    # Dwarf halos (M = 1e11 M_sun, v ~ 30 km/s)
    M_dwarf = 1e11
    M_cluster = 1e15
    results = {}
    for v in [10, 30, 50, 100, 150, 300, 750, 1000, 1500]:
        s_hh = sigma_intra_heavy(v)
        s_ll = sigma_intra_light(v)
        s_xl = sigma_inter(v)
        s_2c = effective_sigma_m_two_component(v)
        # Apply segregation enhancement appropriate for this velocity scale
        if v < 100:
            M = M_dwarf
        else:
            M = M_cluster
        s_seg = sigma_m_with_segregation(v, M)
        s_master = master_yukawa_sigma_m(v)
        ratio = s_seg / s_master if s_master > 0 else float('inf')
        print(f"  {v:<12} {s_hh:<12.3f} {s_ll:<12.3f} {s_xl:<12.3f} "
              f"{s_2c:<12.3f} {s_seg:<12.3f} {s_master:<12.3f} {ratio:<10.3f}")
        results[f'v_{v}_km_s'] = {
            'intra_hh': float(s_hh),
            'intra_ll': float(s_ll),
            'inter_hl': float(s_xl),
            '2comp_effective': float(s_2c),
            'with_segregation': float(s_seg),
            'master_yukawa': float(s_master),
            'ratio_to_master': float(ratio),
            'M_halo_M_sun': float(M),
        }
    print()

    # Key comparisons at LZ-anchored and dwarf velocities
    print("KEY COMPARISONS:")
    print()
    print("At LZ-tuned velocity (v = 150 km/s, cluster scales):")
    s_2c = effective_sigma_m_two_component(150)
    s_seg = sigma_m_with_segregation(150, M_cluster)
    s_master = master_yukawa_sigma_m(150)
    print(f"  Two-component SIDM: {s_2c:.3f} cm^2/g (no segregation)")
    print(f"  With segregation:   {s_seg:.3f} cm^2/g")
    print(f"  Master Yukawa:      {s_master:.3f} cm^2/g")
    print(f"  Ratio (Yang / master): {s_seg/s_master:.3f}")
    if s_seg < 0.1:
        print(f"  -> Two-component model is in cluster < 0.1 cm^2/g bound")
    else:
        print(f"  -> Two-component model is ABOVE cluster 0.1 cm^2/g bound")
    print()

    print("At dwarf velocity (v = 30 km/s):")
    s_2c_d = effective_sigma_m_two_component(30)
    s_seg_d = sigma_m_with_segregation(30, M_dwarf)
    s_master_d = master_yukawa_sigma_m(30)
    print(f"  Two-component SIDM: {s_2c_d:.3f} cm^2/g (no segregation)")
    print(f"  With segregation:   {s_seg_d:.3f} cm^2/g")
    print(f"  Master Yukawa:      {s_master_d:.3f} cm^2/g")
    print(f"  Ratio (Yang / master): {s_seg_d/s_master_d:.3f}")
    if 0.1 < s_seg_d < 1.0:
        print(f"  -> Two-component model matches Zhang+ 2025 dwarf clustering sigma/m ~ 0.3 cm^2/g")
    print()

    # Output
    out_path = _PROJECT_ROOT / "outputs" / "t95" / "two_component_sidm_yang2026.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    output = {
        'phase': 'T95.6 (Two-component SIDM with mass segregation)',
        'reference': 'Yang, D. et al. 2026, arXiv:2506.14898',
        'model': {
            'name': 'SIDM2v',
            'description': 'Two-component SIDM with intra + inter-species velocity-dependent cross sections',
            'mass_ratio_m_H_over_m_L': M_H_OVER_M_L,
            'intra_species': {
                'chi_H-chi_H': {
                    'sigma_0_per_m_H_cm2_g': SIGMA_H_INTRA_M_H_CM2_G,
                    'velocity_scale_km_s': W_H_KMS,
                },
                'chi_L-chi_L': {
                    'sigma_0_per_m_L_cm2_g': SIGMA_L_INTRA_M_L_CM2_G,
                    'velocity_scale_km_s': W_L_KMS,
                },
            },
            'inter_species': {
                'chi_H-chi_L': {
                    'sigma_0_per_m_H_cm2_g': SIGMA_X_INTER_M_H_CM2_G,
                    'velocity_scale_km_s': W_X_KMS,
                },
            },
        },
        'velocity_dependent_sigma_m': results,
        'key_findings': {
            'at_cluster_v150_km_s': {
                'two_component': float(effective_sigma_m_two_component(150)),
                'with_segregation': float(sigma_m_with_segregation(150, M_cluster)),
                'master_yukawa': float(master_yukawa_sigma_m(150)),
                'cluster_bound_satisfied': bool(sigma_m_with_segregation(150, M_cluster) < 0.1),
            },
            'at_dwarf_v30_km_s': {
                'two_component': float(effective_sigma_m_two_component(30)),
                'with_segregation': float(sigma_m_with_segregation(30, M_dwarf)),
                'master_yukawa': float(master_yukawa_sigma_m(30)),
                'matches_Zhang_2025_dwarf_clustering': bool(0.1 < sigma_m_with_segregation(30, M_dwarf) < 1.0),
            },
        },
        't95_tension_resolution': {
            't95_original_tension': (
                'Master single-component Yukawa at v=150 km/s predicts sigma/m ~ 0.7 cm^2/g, '
                '6-13x above Euclid Q1 sub-halo forecast [0.05, 0.10] cm^2/g. '
                'Delta log log Z = -1.57 (substantial).'
            ),
            'two_component_resolution_hypothesis': (
                'Yang+ 2026 SIDM2v argues that two-component SIDM with mass '
                'segregation CAN explain BOTH dwarf cores AND small-scale '
                'lens excess, consistent with cluster sigma/m < 0.1 cm^2/g. '
                'The full resolution requires cosmological simulations '
                'with gravothermal evolution.'
            ),
            'this_script_honest_caveat': (
                'The mass-fraction-weighted average implemented here OVER-'
                'ESTIMATES sigma/m at cluster scales (~0.4 cm^2/g at v=1000 '
                'km/s) compared to the paper ~0.05-0.1 cm^2/g. The full '
                'gravothermal evolution is not captured in this analytic '
                'approximation. The TWO-COMPONENT MODEL PROPERLY DONE '
                'WOULD resolve the T95 tension; this script does NOT '
                'demonstrate that resolution quantitatively.'
            ),
        },
        'caveats': [
            'Mass-segregation enhancement factor (5 at dwarf, 1 at cluster) is approximate.',
            'The full Yang+ 2026 model uses cosmological simulations + parametric model;',
            'this script implements an effective velocity-dependence.',
            'Strong-lensing enhancement (factor 3-6 per Meneghetti+) not implemented here;',
            'would require detailed halo profile calculations.',
        ],
        'references': [
            'Yang, D. et al. 2026, arXiv:2506.14898 (two-component SIDM)',
            'Zhang, Y. et al. 2025 (dwarf clustering, sigma/m ~ 0.3 cm^2/g)',
            'Meneghetti, M. et al. (small-scale lens excess, factor 3-6)',
            'T95_CONSOLIDATED_RESULTS.md (the T95 cross-check this addresses)',
        ],
    }
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"Wrote: {out_path}")


if __name__ == '__main__':
    main()