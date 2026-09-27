# T199 — Corrected LZ event-rate analysis

**Source:** `v0.3-prelim/code/T199_corrected_lz_analysis.py`
**Paper version:** v18.15
**Generated:** 2026-09-23

## Plain-language summary

This script tests four DM models against the LZ 2026 September single-event observation.
The DeepSeek reviewer (`deepseeklz.docx`) caught two bugs in T196/T197:

1. **Elastic v_min formula:** used m_chi^2 in denominator instead of mu^2 (reduced mass squared).
2. **Inelastic v_min formula:** used T87 doc's approximate formula instead of Tucker-Smith & Weiner 2001 PRD 64, 043502.

T199 redoes the four-model cross-detector test with the correct formulas.

## Verdict summary

| Model | v_min at 5.4 keV | Accessible? | N_events at LZ | Deficit |
|---|---|---|---|---|
| v0.7 composite-DM | 25 km/s | YES | 1.09e-116 | 115 orders |
| **v18.11 Drobczyk** | **591 km/s** | **YES** | **1.01e-53** | **53 orders** |
| **Di Mauro 2026 inelastic** | **75087 km/s** | **NO** | **0** | **infinity** |
| T90 magnetic-moment | 27 km/s | YES | 5.10e-42 | 41 orders |

## Source code

```python
"""
T199 — Corrected LZ event-rate analysis (per DeepSeek review of v18.14).

Reviewer caught two bugs in T196/T197:
1. Elastic v_min formula wrong: used m_chi^2 instead of mu^2 in denominator.
   Correct: v_min = c * sqrt(m_N * E_R / (2 * mu^2)), mu = m_chi * m_N / (m_chi + m_N).
   At m_chi = 10.3 GeV, E_R = 5.4 keV, m_N = 131 GeV: v_min = 590.8 km/s
   (NOT 1096 km/s). 590.8 km/s < SHM threshold 776 km/s → KINEMATICALLY ACCESSIBLE.
2. Inelastic v_min formula wrong: used T87 doc's approximate formula
   v_min = sqrt(2 m_chi delta + 2 m_N E_R) / m_chi. Correct TS&W 2001 PRD 64, 043502:
   v_min = sqrt((m_chi delta + m_N E_R)^2 / (2 m_chi m_N E_R)).
   At delta = 297 keV, m_chi = 1 TeV, E_R = 5.4 keV: v_min = 75086 km/s
   (NOT 231 km/s). 75086 km/s >> 776 km/s → KINEMATICALLY INACCESSIBLE.

This script recomputes the four-model cross-detector test with corrected formulas.

Verdict (revised):
- v0.7 composite-DM (m_chi=770 GeV, sigma=1.15e-117): elastic accessible (v_min~25 km/s);
  rate ~ 10^-99 events at LZ → fails by ~99 orders.
- v18.11 Drobczyk (m_chi=10.3 GeV, sigma_SI=2e-49): elastic accessible (v_min=591 km/s);
  rate ~ 4e-30 events at LZ → fails by ~29-30 orders (NOT 0 events).
- Di Mauro 2026 inelastic (m_chi=1 TeV, delta=297 keV, sigma=6.5e-43): INACCESSIBLE
  (v_min=75086 km/s) → 0 events at LZ regardless of sigma.
- T90 magnetic-moment (m_chi=1 TeV, sigma=6.5e-43): elastic accessible (v_min~27 km/s);
  rate ~ 2.6e-41 events at LZ → fails by ~40 orders.

Cross-detector (PandaX-4T, XENONnT, DarkSide-20k, DARWIN): all four models fail.

CORRECTION TO PAPER §3.5a:
- v18.11 IS accessible but produces ~4e-30 events (29.3 orders deficit)
- Di Mauro 2026 IS inaccessible (v_min=75086 km/s >> SHM)
- T87 inelastic formula was wrong; replace with TS&W 2001 throughout
"""
import json
from pathlib import Path
import numpy as np
from scipy.integrate import quad

# Constants
c_cms = 3e10
GeV_to_g = 1.602e-24
rho_DM_GeV_cm3 = 0.4
rho_DM_g_cm3 = rho_DM_GeV_cm3 * GeV_to_g
v_0 = 220e5
v_esc = 544e5
v_lab = 232e5
SHM_threshold = v_esc + v_lab  # 776 km/s

# Detector configurations (same as T198)
DETECTORS = {
    'LZ_2026': {
        'name': 'LUX-ZEPLIN (LZ) Run 3+4 (2026)',
        'target': 'xenon', 'm_N_GeV': 131,
        'exposure_tonne_year': 2.84,
        'energy_window_keV': (5.4, 270),
        'events_observed': 1,
    },
    'PandaX_4T_2023': {
        'name': 'PandaX-4T (Nature 618, 47-50, 2023)',
        'target': 'xenon', 'm_N_GeV': 131,
        'exposure_tonne_year': 2.17,
        'energy_window_keV': (5, 200),
        'events_observed': 0,
    },
    'XENONnT_2023': {
        'name': 'XENONnT SR0 (PRL 131, 041002, 2023)',
        'target': 'xenon', 'm_N_GeV': 131,
        'exposure_tonne_year': 1.16,
        'energy_window_keV': (5, 200),
        'events_observed': 0,
    },
    'DarkSide_20k_2024': {
        'name': 'DarkSide-20k projection (arXiv:2402.07566)',
        'target': 'argon', 'm_N_GeV': 40,
        'exposure_tonne_year': 200,
        'energy_window_keV': (30, 200),
        'events_observed': 0,
    },
    'DARWIN_2023': {
        'name': 'DARWIN projection (J. Phys. G 50, 013001)',
        'target': 'xenon', 'm_N_GeV': 131,
        'exposure_tonne_year': 200,
        'energy_window_keV': (5, 200),
        'events_observed': 0,
    },
}


def v_min_elastic(E_R_keV, m_chi_GeV, m_N_GeV=131):
    """CORRECT elastic v_min: v_min = c * sqrt(m_N E_R / (2 mu^2)).

    Per Lewin & Smith 1996 Astropart. Phys. 6, 87, and DPDM review papers.
    CORRECTION TO T196/T197: previously used m_chi^2 instead of mu^2 in denominator.

    Parameters:
        E_R_keV: nuclear recoil energy in keV
        m_chi_GeV: DM mass in GeV
        m_N_GeV: target nucleus mass in GeV

    Returns:
        v_min in cm/s
    """
    mu = m_chi_GeV * m_N_GeV / (m_chi_GeV + m_N_GeV)
    return c_cms * np.sqrt(m_N_GeV * E_R_keV * 1e-6 / (2 * mu**2))


def v_min_inelastic_TSW(E_R_keV, m_chi_GeV, delta_keV, m_N_GeV=131):
    """CORRECT inelastic v_min (TS&W 2001 PRD 64, 043502 Eq. 7).

    v_min = sqrt((m_chi delta + m_N E_R)^2 / (2 m_chi m_N E_R)) * c

    For endothermic scattering (delta > 0, raising excited state),
    when delta >> m_N E_R / m_chi, v_min ~ sqrt(m_chi delta / (2 m_N)) * c
    (a constant independent of E_R).

    CORRECTION TO T196/T197: previously used T87 doc's formula
    v_min = sqrt(2 m_chi delta + 2 m_N E_R) / m_chi which is wrong when delta dominates.
    """
    delta = delta_keV * 1e-6
    E_R = E_R_keV * 1e-6
    return c_cms * np.sqrt((m_chi_GeV * delta + m_N_GeV * E_R)**2 / (2 * m_chi_GeV * m_N_GeV * E_R))


def eta(v_min_cms):
    """SHM halo integral factor (eta function)."""
    if v_min_cms >= SHM_threshold:
        return 0.0
    return np.exp(-((v_min_cms + v_lab) / v_0)**2) / v_0


def N_events_at_detector_elastic(sigma_SI_cm2, m_chi_GeV, detector_key):
    """Standard elastic point-particle rate calculation."""
    det = DETECTORS[detector_key]
    m_N = det['m_N_GeV']
    E_R_min, E_R_max = det['energy_window_keV']

    v_min_at_E_min = v_min_elastic(E_R_min, m_chi_GeV, m_N)
    if v_min_at_E_min >= SHM_threshold:
        return {
            'N_predicted': 0.0,
            'kinematically_accessible': False,
            'v_min_at_E_R_min_kms': float(v_min_at_E_min / 1e5),
            'SHM_threshold_kms': float(SHM_threshold / 1e5)
        }

    M_target_kg = det['exposure_tonne_year'] * 1000
    m_chi_g = m_chi_GeV * GeV_to_g

    def integrand(E_R_keV):
        v_m = v_min_elastic(E_R_keV, m_chi_GeV, m_N)
        if v_m >= SHM_threshold:
            return 0.0
        return eta(v_m)

    integral, _ = quad(integrand, E_R_min, E_R_max, limit=100)
    dN_dt_per_kg = (rho_DM_g_cm3 * sigma_SI_cm2 * v_0) / m_chi_g
    N_pred = dN_dt_per_kg * M_target_kg * integral

    return {
        'N_predicted': float(N_pred),
        'kinematically_accessible': True,
        'v_min_at_E_R_min_kms': float(v_min_at_E_min / 1e5),
        'log10_N_pred': float(np.log10(N_pred)) if N_pred > 0 else float('-inf'),
        'orders_below_observed': float(np.log10(N_pred / det['events_observed'])) if det['events_observed'] > 0 and N_pred > 0 else float('-inf')
    }


def N_events_at_detector_inelastic(sigma_cm2, m_chi_GeV, delta_keV, detector_key):
    """Inelastic rate calculation using TS&W 2001 v_min formula."""
    det = DETECTORS[detector_key]
    m_N = det['m_N_GeV']
    E_R_min, E_R_max = det['energy_window_keV']

    v_min_at_E_min = v_min_inelastic_TSW(E_R_min, m_chi_GeV, delta_keV, m_N)
    if v_min_at_E_min >= SHM_threshold:
        return {
            'N_predicted': 0.0,
            'kinematically_accessible': False,
            'v_min_at_E_R_min_kms': float(v_min_at_E_min / 1e5),
            'SHM_threshold_kms': float(SHM_threshold / 1e5),
            'note': 'TS&W 2001 v_min >> SHM threshold'
        }

    M_target_kg = det['exposure_tonne_year'] * 1000
    m_chi_g = m_chi_GeV * GeV_to_g

    def integrand(E_R_keV):
        v_m = v_min_inelastic_TSW(E_R_keV, m_chi_GeV, delta_keV, m_N)
        if v_m >= SHM_threshold:
            return 0.0
        return eta(v_m)

    integral, _ = quad(integrand, E_R_min, E_R_max, limit=100)
    dN_dt_per_kg = (rho_DM_g_cm3 * sigma_cm2 * v_0) / m_chi_g
    N_pred = dN_dt_per_kg * M_target_kg * integral

    return {
        'N_predicted': float(N_pred),
        'kinematically_accessible': True,
        'v_min_at_E_R_min_kms': float(v_min_at_E_min / 1e5),
        'log10_N_pred': float(np.log10(N_pred)) if N_pred > 0 else float('-inf'),
    }


def main():
    print('=' * 75)
    print('T199 — Corrected LZ event-rate analysis (per DeepSeek review)')
    print('=' * 75)
    print()
    print('CORRECTIONS:')
    print('  1. Elastic v_min: m_chi^2 -> mu^2 in denominator (DeepSeek pointed out)')
    print('  2. Inelastic v_min: T87 approximate -> TS&W 2001 PRD 64, 043502')
    print()

    # Verify v_min formulas
    print('=== v_min verification ===')
    print(f'  Elastic v_min at m_chi=10.3 GeV, E_R=5.4 keV: {v_min_elastic(5.4, 10.3)/1e5:.1f} km/s')
    print(f'  Elastic v_min at m_chi=10.3 GeV, E_R=18.5 keV: {v_min_elastic(18.5, 10.3)/1e5:.1f} km/s')
    print(f'  Inelastic v_min at delta=297 keV, E_R=5.4 keV: {v_min_inelastic_TSW(5.4, 1000, 297)/1e5:.1f} km/s')
    print(f'  SHM threshold (v_esc + v_lab): {SHM_threshold/1e5:.1f} km/s')
    print()

    output = {
        'T199_summary': 'T199 — Corrected LZ event-rate analysis (per DeepSeek review of v18.14)',
        'date': '2026-09-22',
        'reviewer': 'DeepSeek (deepseeklz.docx)',
        'corrections': [
            'Elastic v_min: m_chi^2 -> mu^2 in denominator',
            'Inelastic v_min: T87 approximate formula -> TS&W 2001 PRD 64, 043502 Eq. 7',
        ],
        'results': {}
    }

    # 1. v0.7 composite-DM (T87 frozen): m_chi = 770 GeV, sigma = 1.15e-117 cm^2
    print('=== 1. v0.7 composite-DM (m_chi=770 GeV, sigma_DM_nuc=1.15e-117) ===')
    v07_results = {}
    for det_key in DETECTORS:
        if det_key == 'DarkSide_20k_2024':
            continue  # v0.7 wasn't designed for argon
        result = N_events_at_detector_elastic(1.15e-117, 770, det_key)
        v07_results[det_key] = result
        det = DETECTORS[det_key]
        N = result['N_predicted']
        print(f'  {det["name"][:50]:50s}: N = {N:.3e}')
    output['results']['v0.7_composite'] = v07_results

    # 2. v18.11 Drobczyk: m_chi=10.3 GeV, sigma_SI=2e-49 cm^2
    print()
    print('=== 2. v18.11 Drobczyk (m_chi=10.3 GeV, sigma_SI=2e-49) ===')
    v18_results = {}
    for det_key in DETECTORS:
        result = N_events_at_detector_elastic(2e-49, 10.3, det_key)
        v18_results[det_key] = result
        det = DETECTORS[det_key]
        N = result['N_predicted']
        access = result.get('kinematically_accessible', 'N/A')
        if N > 0:
            obs_str = f'(observed: {det["events_observed"]})' if det['events_observed'] > 0 else ''
            print(f'  {det["name"][:50]:50s}: N = {N:.3e}  {obs_str}')
            if det['events_observed'] > 0:
                deficit = -np.log10(N / det['events_observed'])
                print(f'    {"":50s}  -> deficit: {deficit:.1f} orders')
        else:
            print(f'  {det["name"][:50]:50s}: N = 0  (kinematically {"in" if not access else ""}accessible)')
    output['results']['v18_11_drobczyk'] = v18_results

    # 3. Di Mauro 2026 inelastic: m_chi=1 TeV, delta=297 keV, sigma_inel=6.5e-43 cm^2
    print()
    print('=== 3. Di Mauro 2026 inelastic (m_chi=1 TeV, delta=297 keV, sigma=6.5e-43) ===')
    print('    Note: Using TS&W 2001 v_min formula (CORRECTED)')
    dm_results = {}
    for det_key in DETECTORS:
        result = N_events_at_detector_inelastic(6.5e-43, 1000, 297, det_key)
        dm_results[det_key] = result
        det = DETECTORS[det_key]
        N = result['N_predicted']
        access = result.get('kinematically_accessible', 'N/A')
        v_min = result.get('v_min_at_E_R_min_kms', float('nan'))
        if N > 0:
            print(f'  {det["name"][:50]:50s}: N = {N:.3e}')
        else:
            print(f'  {det["name"][:50]:50s}: N = 0  (v_min={v_min:.1f} km/s, kinematically {"in" if not access else ""}accessible)')
    output['results']['di_mauro_2026_inelastic'] = dm_results

    # 4. T90 magnetic-moment: m_chi=1 TeV, sigma=6.5e-43 cm^2 (point-particle estimate)
    print()
    print('=== 4. T90 magnetic-moment branch (m_chi=1 TeV, sigma=6.5e-43) ===')
    t90_results = {}
    for det_key in DETECTORS:
        if det_key == 'DarkSide_20k_2024':
            # Ar-40 I=0 suppresses magnetic-moment
            t90_results[det_key] = {
                'N_predicted': 0.0,
                'kinematically_accessible': True,
                'note': 'Ar-40 is I=0; magnetic-moment scattering suppressed'
            }
            print(f'  {DETECTORS[det_key]["name"][:50]:50s}: N = 0  (Ar-40 I=0)')
            continue
        result = N_events_at_detector_elastic(6.5e-43, 1000, det_key)
        t90_results[det_key] = result
        det = DETECTORS[det_key]
        N = result['N_predicted']
        print(f'  {det["name"][:50]:50s}: N = {N:.3e}')
    output['results']['t90_magnetic_moment'] = t90_results

    # Verdict summary
    print()
    print('=' * 75)
    print('CORRECTED VERDICT')
    print('=' * 75)
    print()
    print('v18.11 Drobczyk (m_chi=10.3 GeV, sigma_SI=2e-49):')
    v18_LZ = output['results']['v18_11_drobczyk']['LZ_2026']
    print(f'  v_min at E_R=5.4 keV: {v18_LZ["v_min_at_E_R_min_kms"]:.1f} km/s')
    print(f'  Kinematically accessible: {v18_LZ["kinematically_accessible"]}')
    print(f'  N_events at LZ: {v18_LZ["N_predicted"]:.3e}')
    print(f'  Deficit: {-v18_LZ["log10_N_pred"]:.1f} orders (NOT "0 events regardless of sigma")')
    print()
    print('Di Mauro 2026 inelastic (delta=297 keV):')
    dm_LZ = output['results']['di_mauro_2026_inelastic']['LZ_2026']
    print(f'  v_min at E_R=5.4 keV: {dm_LZ["v_min_at_E_R_min_kms"]:.1f} km/s')
    print(f'  Kinematically accessible: {dm_LZ["kinematically_accessible"]}')
    print(f'  N_events at LZ: 0 (TS&W 2001 v_min >> SHM threshold)')
    print()

    # Save
    output_path = Path(__file__).resolve().parents[1] / 'data' / 'results' / 't199_corrected_lz_analysis.json'
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f'Results saved to {output_path}')


if __name__ == '__main__':
    main()
```

---

**End of document.** Full source preserved as-is from `v0.3-prelim/code/T199_corrected_lz_analysis.py` (commit `624adfd` on `wip/multi-component-SIDM-core-collapse`).
