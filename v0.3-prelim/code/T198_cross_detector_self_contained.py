"""
T198 — Self-contained cross-detector analysis for v18.11 + T90 magnetic-moment.

Replaces the WIMpy-dependent `t90_v10_cross_detector.py` (which lives on
wip/tier3-sequential-T90-magnetic branch) with a self-contained version
that uses only scipy/numpy (already in venv).

Computes predicted N_events at LZ, PandaX-4T, XENONnT, DarkSide-20k, DARWIN
for:
  - v0.7 composite-DM (T87 frozen)
  - v18.11 Drobczyk candidate (T192 thermal-avg)
  - Di Mauro 2026 inelastic (m_chi=1 TeV, δ=297 keV)
  - T90 magnetic-moment branch (μ_χ = 6.10e-8 μ_N at m_chi=1 TeV)

Uses T87 formula for inelastic kinematics: v_min = sqrt(2 m_χ δ + 2 m_N E_R) / m_χ
Uses standard elastic kinematics for elastic channels.

Cross-detector reference data (per public 2024-2026 literature):
  - LZ 2026: arXiv:2609.02823, 2.84 t·y, 5.4-270 keV, 1 event at 248 keV
  - PandaX-4T 2023: Nature 618, 47-50, 0.63+1.54 t·y, 5-200 keV
  - XENONnT 2023: PRL 131, 041002, 1.16 t·y, 5-200 keV
  - DarkSide-20k 2024: arXiv:2402.07566, 200 t·y projected, 30-200 keV (Ar)
  - DARWIN 2023: J. Phys. G 50, 013001, 200 t·y projected, 5-200 keV

Magnetic-moment cross-section approximation (T90 framework):
  For dipole-dipole scattering, σ_DM_nuc ~ (Z² × e² × μ_χ²) / (4π × m_χ² × v²)
  At v = 220 km/s, m_χ = 1 TeV, μ_χ = 6.10e-8 μ_N:
  σ ≈ 6.5e-43 cm² (Di Mauro 2026 fitted value, which matches LZ-anchored μ_χ)
"""
import json
import os
from pathlib import Path
import numpy as np
from scipy.integrate import quad

# Constants
GeV_to_g = 1.602e-24
c_cms = 3e10
rho_DM_GeV_cm3 = 0.4
rho_DM_g_cm3 = rho_DM_GeV_cm3 * GeV_to_g
v_0 = 220e5
v_esc = 544e5
v_lab = 232e5
SHM_threshold = v_esc + v_lab  # 776 km/s

# Model parameters
MODELS = {
    'v0.7_composite': {
        'sigma_cm2': 1.15e-117,  # T87 frozen
        'm_chi_GeV': 770,
        'channel': 'inelastic_gaussian_F2',
        'note': 'T87 archived; composite-DM at v0.7 MAP'
    },
    'v18_11_drobczyk': {
        'sigma_SI_cm2': 2e-49,  # T192 thermal-avg
        'm_chi_GeV': 10.3,
        'channel': 'elastic',
        'note': 'T192 thermal-averaged BW; g_h_SM = 0.00040'
    },
    'di_mauro_2026_inelastic': {
        'sigma_inel_cm2': 6.5e-43,  # Di Mauro 2026
        'm_chi_GeV': 1000,
        'delta_keV': 297,
        'channel': 'inelastic_endothermic',
        'note': 'Di Mauro 2026 pseudo-Dirac thermal'
    },
    't90_magnetic_moment': {
        'sigma_cm2': 6.5e-43,  # LZ-tuned magnetic-moment
        'm_chi_GeV': 1000,
        'channel': 'magnetic_moment',
        'note': 'T90 LZ-anchored, μ_χ = 6.10e-8 μ_N'
    },
}

# Detector configurations
DETECTORS = {
    'LZ_2026': {
        'name': 'LUX-ZEPLIN (LZ) Run 3+4 (2026)',
        'target': 'xenon',
        'm_N_GeV': 131,
        'exposure_tonne_year': 2.84,
        'energy_window_keV': (5.4, 270),
        'events_observed': 1,  # 248 keV event
        'arXiv': '2609.02823',
        'limit_sigma_SI_at_30_GeV_cm2': 9.4e-47,
    },
    'PandaX_4T_2023': {
        'name': 'PandaX-4T (Nature 618, 47-50, 2023)',
        'target': 'xenon',
        'm_N_GeV': 131,
        'exposure_tonne_year': 2.17,  # 0.63 + 1.54
        'energy_window_keV': (5, 200),
        'events_observed': 0,
        'limit_sigma_SI_at_40_GeV_cm2': 1e-46,
        'limit_mu_B_at_40_GeV': 4.8e-10,
    },
    'XENONnT_2023': {
        'name': 'XENONnT SR0 (PRL 131, 041002, 2023)',
        'target': 'xenon',
        'm_N_GeV': 131,
        'exposure_tonne_year': 1.16,
        'energy_window_keV': (5, 200),
        'events_observed': 0,
        'limit_sigma_SI_at_30_GeV_cm2': 2.6e-47,
    },
    'DarkSide_20k_2024': {
        'name': 'DarkSide-20k projection (arXiv:2402.07566)',
        'target': 'argon',
        'm_N_GeV': 40,
        'exposure_tonne_year': 200,
        'energy_window_keV': (30, 200),
        'events_observed': 0,
        'note': 'Ar-40 I=0, magnetic-moment suppressed; useful for SI only'
    },
    'DARWIN_2023': {
        'name': 'DARWIN projection (J. Phys. G 50, 013001)',
        'target': 'xenon',
        'm_N_GeV': 131,
        'exposure_tonne_year': 200,
        'energy_window_keV': (5, 200),
        'events_observed': 0,
        'limit_sigma_SI_projected_at_30_GeV_cm2': 1e-49,
    },
}


def v_min_elastic(E_R_keV, m_chi_GeV, m_N_GeV=131):
    return np.sqrt(2 * m_N_GeV * E_R_keV * 1e-6 / m_chi_GeV**2) * c_cms


def v_min_inelastic_T87(E_R_keV, m_chi_GeV, delta_keV, m_N_GeV=131):
    """T87 formula: v_min = sqrt(2 m_χ δ + 2 m_N E_R) / m_χ.

    Used in the project (T87 doc) and consistent with v_min ~ 232 km/s at LZ min for δ=297.
    Note: TS&W 2001 PRD 64, 043502 gives stricter v_min when δ >> recoil × m_N/m_χ;
    see T197 docstring for details.
    """
    return np.sqrt(2 * m_chi_GeV * delta_keV * 1e-6 + 2 * m_N_GeV * E_R_keV * 1e-6) / m_chi_GeV * c_cms


def eta(v_min_cms):
    if v_min_cms >= SHM_threshold:
        return 0.0
    return np.exp(-((v_min_cms + v_lab) / v_0)**2) / v_0


def N_events_at_detector(model_key, detector_key):
    """Compute predicted N_events for a model at a given detector."""
    model = MODELS[model_key]
    det = DETECTORS[detector_key]
    m_N = det['m_N_GeV']

    if model['channel'] == 'inelastic_gaussian_F2' or model['channel'] == 'inelastic_endothermic':
        sigma = model.get('sigma_inel_cm2', model['sigma_cm2'])
        delta_keV = model.get('delta_keV', 0)
        m_chi = model['m_chi_GeV']
        v_min_func = lambda E: v_min_inelastic_T87(E, m_chi, delta_keV, m_N)
    elif model['channel'] == 'magnetic_moment':
        sigma = model['sigma_cm2']
        m_chi = model['m_chi_GeV']
        # Magnetic-moment uses elastic kinematics for v_min (different cross-section formula)
        v_min_func = lambda E: v_min_elastic(E, m_chi, m_N)
    else:  # elastic
        sigma = model.get('sigma_SI_cm2', model.get('sigma_cm2'))
        m_chi = model['m_chi_GeV']
        v_min_func = lambda E: v_min_elastic(E, m_chi, m_N)

    M_target_kg = det['exposure_tonne_year'] * 1000
    m_chi_g = m_chi * GeV_to_g

    # Check kinematic accessibility at E_R_min
    v_min_at_E_R_min = v_min_func(det['energy_window_keV'][0])
    if v_min_at_E_R_min >= SHM_threshold:
        return {
            'N_predicted': 0.0,
            'kinematically_accessible': False,
            'v_min_at_E_R_min_kms': float(v_min_at_E_R_min / 1e5),
            'SHM_threshold_kms': float(SHM_threshold / 1e5)
        }

    # For DarkSide-20k argon: Ar-40 has I=0, magnetic-moment is suppressed
    if detector_key == 'DarkSide_20k_2024' and model['channel'] == 'magnetic_moment':
        return {
            'N_predicted': 0.0,
            'kinematically_accessible': True,
            'note': 'Ar-40 is I=0; magnetic-moment scattering suppressed'
        }

    def integrand(E_R_keV):
        v_min = v_min_func(E_R_keV)
        if v_min >= SHM_threshold:
            return 0.0
        return eta(v_min)

    integral, _ = quad(integrand, det['energy_window_keV'][0], det['energy_window_keV'][1], limit=100)
    dN_dt_per_kg = (rho_DM_g_cm3 * sigma * v_0) / m_chi_g
    N_pred = dN_dt_per_kg * M_target_kg * integral

    return {
        'N_predicted': float(N_pred),
        'kinematically_accessible': True,
        'v_min_at_E_R_min_kms': float(v_min_at_E_R_min / 1e5),
        'log10_N_pred': float(np.log10(N_pred)) if N_pred > 0 else float('-inf'),
        'orders_below_observed': float(np.log10(N_pred / det['events_observed'])) if det['events_observed'] > 0 and N_pred > 0 else float('-inf')
    }


def main():
    print('=' * 75)
    print('T198 — Self-contained cross-detector analysis for v18.11 + T90')
    print('=' * 75)

    output = {
        'T198_summary': 'T198 — Self-contained cross-detector analysis (v18.13 update)',
        'rationale': 'Replaces WIMpy-dependent t90_v10_cross_detector.py with a self-contained module',
        'date': '2026-09-22',
        'models': list(MODELS.keys()),
        'detectors': list(DETECTORS.keys()),
        'results': {},
        'notes': [
            'T87 kinematic formula used for inelastic channels (consistent with project)',
            'TS&W 2001 PRD 64, 043502 gives stricter v_min when δ >> recoil × m_N/m_χ; documented in T197',
            'Magnetic-moment channel uses elastic v_min formula (T90 framework)',
            'DarkSide-20k Ar-40 is I=0, so magnetic-moment scattering is suppressed'
        ]
    }

    for model_key in MODELS:
        output['results'][model_key] = {}
        print(f"\n=== {model_key} ===")
        for det_key in DETECTORS:
            result = N_events_at_detector(model_key, det_key)
            output['results'][model_key][det_key] = result
            det = DETECTORS[det_key]
            N = result['N_predicted']
            access = result.get('kinematically_accessible', 'N/A')
            if N > 0:
                obs_str = f"(observed: {det['events_observed']})" if det['events_observed'] > 0 else ""
                print(f"  {det['name'][:50]:50s}: N = {N:.3e}  {obs_str}")
                if det['events_observed'] > 0:
                    orders = -result.get('orders_below_observed', 0)
                    print(f"    {'':50s}  → fails by {orders:.1f} orders")
            else:
                print(f"  {det['name'][:50]:50s}: N = 0  (kinematically {'in' if not access else ''}accessible)")

    # Save
    output_path = Path(__file__).resolve().parents[1] / 'data' / 'results' / 't198_cross_detector_self_contained.json'
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\n=== Results saved to {output_path} ===")

    # Summary table
    print('\n=== Summary table ===')
    print(f"{'Model':<30s}", end='')
    for det_key in DETECTORS:
        print(f"{det_key[:15]:>15s}", end='')
    print()
    for model_key in MODELS:
        print(f"{model_key:<30s}", end='')
        for det_key in DETECTORS:
            N = output['results'][model_key][det_key]['N_predicted']
            if N > 0:
                print(f"{N:>15.2e}", end='')
            else:
                print(f"{'0':>15s}", end='')
        print()


if __name__ == '__main__':
    main()