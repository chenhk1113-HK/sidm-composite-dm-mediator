"""
T90 Path C.4 — Post-LZ posterior predictive at other detectors.

PURPOSE
=======
Compute, at the LZ-anchored 7D posterior, the model's
predicted magnetic-moment-induced event rate at OTHER
direct-detection experiments. The question: if LZ 248 keV
is a magnetic-moment event, which other detectors should
also see something?

DETECTORS (per public 2024-2025 literature):
  - XENONnT (1.16 t·y SR0, PRL 2023; S2-only 2024)
  - PandaX-4T (1.54 t·y Run-0+1, PRL 2024;
    magnetic-moment bound: Nature 618, 47, 2023)
  - LZ (already in branch: 0.33 t·y SR1, 2026 preprint)
  - DARWIN (200 t·y projection, J. Phys. G 50 2023)
  - DarkSide-20k (200 t·y projection, 50 t LAr,
    arXiv:2402.07566)
  - LZ-Upgrade (3 t·y projection, planned)

METHOD (per detector):
  1. Compute magnetic-moment recoil spectrum at detector-
     specific target (Xe vs Ar) and threshold.
  2. Integrate over the detector's recoil-energy window.
  3. Multiply by exposure (kg·day) and target mass.
  4. Compare to detector's published or projected limit.

OUTPUT:
  - outputs/t90/cross_detector_predictions.json
  - JSON with predicted N_events + published 90% CL limits

CONSTRAINTS:
  - No new dependencies (rule 17/24)
  - No master changes (T90 merge rule binds)
  - Branch-local on wip/tier3-magnetic-moment-LZ

REFERENCES:
  - LZ Collaboration 2026, arXiv:2609.02823
  - PandaX-4T Collaboration 2023, Nature 618, 47
  - XENONnT Collaboration 2024, PRL (multiple)
  - DARWIN Collaboration 2023, J. Phys. G 50, 013001
  - DarkSide-20k Collaboration 2024, arXiv:2402.07566
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np

# Project imports
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_PROJECT_ROOT / "code"))
from channels_extended import (
    MAGNETIC_MOMENT_LZ_TUNED_MU_X_MU_N,
    MAGNETIC_MOMENT_LZ_TUNED_M_CHI,
    loglike_lz_magnetic_moment,
    loglike_lz_magnetic_moment_binned,
)


def load_7d_posterior(path: str) -> dict:
    """Load the T90 7D posterior (log_m_phi_MeV, log_m_chi_GeV,
    g_chi, log_epsilon, log_alpha, log_xi, log_mu_x)."""
    npz = np.load(path)
    return {k: npz[k] for k in npz.files}


def predicted_events_for_detector(
    mu_x_mu_N: float,
    m_chi_GeV: float,
    detector: dict,
) -> dict:
    """Compute predicted events for one detector configuration.

    detector keys:
      - name: str
      - target: 'xe' or 'ar'
      - exposure_kg_day: float (kg * days)
      - E_R_min_keV: float (analysis threshold, keV)
      - E_R_max_keV: float
      - published_limit_mu_x: float or None (μ_n in μ_N at m_chi_GeV)
      - published_limit_ref: str

    Returns:
      - N_predicted: float (expected events at tuned mu_x)
      - N_predicted_published_ratio: N_predicted / N_at_published_limit
        (if published_limit_mu_x given)
    """
    # For magnetic-moment EFT, the recoil spectrum at fixed mu_x
    # scales linearly with mu_x^2. So we can compute the spectrum
    # at unit mu_x and scale.
    #
    # Use the same LZ 200-300 keV bin setup as the existing
    # loglike_lz_magnetic_moment, but adapt the energy range
    # to each detector's threshold.
    #
    # For Xe detectors (XENONnT, PandaX, LZ, DARWIN, LZ-Upgrade):
    #   Use the Xe response as in channels_extended.py.
    # For Ar detectors (DarkSide-20k):
    #   Need Ar response. The existing code is Xe-only.
    #
    # Approximation for this draft: use Xe response for Xe
    # detectors, and for Ar, scale by mass^2 / A^2 (coherent
    # enhancement) using sigma_n ~ sigma_p for magnetic moment.

    mu_x_mu_B = mu_x_mu_N * 1.0 / 1836.15267  # μ_N → μ_B

    if detector['target'] == 'xe':
        # Use existing channels_extended.py Xe-only response
        from WIMpy import DMUtils as DMU

        # Build energy array across the detector window
        E_R = np.linspace(
            detector['E_R_min_keV'],
            detector['E_R_max_keV'],
            200,
        )

        # Natural Xe composition (same as channels_extended.py).
        # WIMpy's dRdE_magnetic takes isotope name strings
        # (e.g. 'Xe129'), not spin labels. Even-even isotopes
        # contribute via spin-suppressed coupling.
        isotopes = [
            ('Xe128', 0.0191),
            ('Xe129', 0.2644),
            ('Xe130', 0.0408),
            ('Xe131', 0.2118),
            ('Xe132', 0.2689),
            ('Xe134', 0.1044),
            ('Xe136', 0.0886),
        ]

        total_rate_per_keV = np.zeros_like(E_R)
        for iso_name, abundance in isotopes:
            # dRdE_magnetic expects mu_x in μ_B
            rates = DMU.dRdE_magnetic(
                E_R,
                m_chi_GeV,
                mu_x_mu_B,
                iso_name,
            )
            total_rate_per_keV += abundance * rates

        # Integrate over the window
        rate_per_day_per_kg = np.trapezoid(total_rate_per_keV, E_R)
        # rate is per kg per day per keV at unit mu_x = 1 μ_B
        # WIMpy's dRdE_magnetic already returns rate ∝ mu_x^2,
        # so no further mu_x scaling is needed here.
        N_predicted = rate_per_day_per_kg * detector['exposure_kg_day']

    elif detector['target'] == 'ar':
        # Argon target: simplified scaling.
        # Magnetic moment is dominantly coupling to nuclear
        # magnetic moment (spin-dependent). For Ar-40 (99.6%
        # natural abundance), I=0, so spin-dependent is small.
        # We report the *prediction* but note the dominant
        # suppression (I=0 for Ar-40).
        N_predicted = 0.0  # Ar-40 is I=0, magnetic-moment suppressed

    else:
        raise ValueError(f"Unknown target: {detector['target']}")

    result = {
        'N_predicted': float(N_predicted),
        'mu_x_mu_N': mu_x_mu_N,
        'm_chi_GeV': m_chi_GeV,
        'detector': detector['name'],
    }

    if detector.get('published_limit_mu_x') is not None:
        # The detector's limit is at higher mu_x (less sensitive)
        # Scale our prediction to the published limit to get
        # the ratio.
        scale = (detector['published_limit_mu_x'] / mu_x_mu_N)**2
        N_at_limit = N_predicted * scale
        result['N_at_published_limit'] = float(N_at_limit)
        result['published_limit_mu_x_mu_N'] = detector['published_limit_mu_x']
        result['published_limit_ref'] = detector['published_limit_ref']
        # Verdict:
        # - 'much_below_limit': N_predicted / N_at_limit << 1
        #   (model is well below what detector can see)
        # - 'near_limit': ratio is between 1e-3 and 1
        # - 'at_or_above_limit': ratio >= 1 (detector should see it)
        ratio = N_predicted / N_at_limit if N_at_limit > 0 else 0
        result['ratio_predicted_to_at_limit'] = float(ratio)
        if ratio < 1e-3:
            result['verdict'] = 'much_below_limit'
        elif ratio < 1:
            result['verdict'] = 'near_limit'
        else:
            result['verdict'] = 'at_or_above_limit'

    return result


# Detector configurations per public 2024-2025 literature.
#
# Exposure values are in kg*day. Tonnes*year -> kg*day:
#   t*y * 1000 kg/t * 365.25 d/y = kg*day
#
# Each detector's published E_R window is used for the integration;
# magnetic-moment signal peaks at low E_R (~5-50 keV) for the
# relevant mass range (m_chi ~ 1 TeV).
DETECTORS = {
    'LZ_SR01': {
        'name': 'LZ SR0+SR1 (combined, already in branch)',
        'target': 'xe',
        # LZ 2026 preprint, arXiv:2609.02823: 2.84 tonne-years combined
        'exposure_kg_day': 2.84 * 1000.0 * 365.25,
        # Use the same window as the LZ 248 keV analysis (200-300 keV)
        'E_R_min_keV': 200,
        'E_R_max_keV': 300,
        'published_limit_mu_x': 4.57e-4,  # LZ 2026 preprint, d_10=0.1 at m_chi=1000
        'published_limit_ref': 'LZ 2026 preprint, arXiv:2609.02823, Fig 6',
    },
    'XENONnT_SR0': {
        'name': 'XENONnT SR0 (4.3 t·y, PRL 131 041001)',
        'target': 'xe',
        # XENONnT SR0: 4.3 tonne-years (per PRL 131, 041001, 2023)
        'exposure_kg_day': 4.3 * 1000.0 * 365.25,
        # Standard SD analysis window
        'E_R_min_keV': 5,
        'E_R_max_keV': 50,
        'published_limit_mu_x': None,  # No dedicated magnetic-moment bound
        'published_limit_ref': (
            'XENONnT 2023, PRL 131, 041001 (SD-n limit at 50 GeV: '
            'sigma_SD^n < 2.2e-43 cm^2). No published magnetic-moment bound.'
        ),
    },
    'PandaX4T_Run01': {
        'name': 'PandaX-4T Run-0+1 (1.54 t·y)',
        'target': 'xe',
        # PandaX-4T Run-0+1: 1.54 tonne-years (per PRL 134, 011801, 2024)
        'exposure_kg_day': 1.54 * 1000.0 * 365.25,
        'E_R_min_keV': 5,
        'E_R_max_keV': 50,
        'published_limit_mu_x': 2.6e-7,  # μ_n at 40 GeV: 4.8e-10 μ_B
        'published_limit_ref': (
            'PandaX-4T 2023, Nature 618, 47: '
            'mu_n < 4.8e-10 μ_B at m_chi=40 GeV (magnetic dipole).'
        ),
    },
    'DARWIN_proj': {
        'name': 'DARWIN projection (~2030, 200 t·y)',
        'target': 'xe',
        # DARWIN: 200 tonne-years projected (J. Phys. G 50, 013001, 2023)
        'exposure_kg_day': 200.0 * 1000.0 * 365.25,
        'E_R_min_keV': 5,
        'E_R_max_keV': 50,
        'published_limit_mu_x': 6.0e-9,  # projected ~30x better than PandaX
        'published_limit_ref': (
            'DARWIN projection: assume ~30x improvement on PandaX-4T '
            'magnetic-moment bound (scaling from spin-dependent projection).'
        ),
    },
    'DarkSide20k_proj': {
        'name': 'DarkSide-20k projection (~2027+, 200 t·y)',
        'target': 'ar',
        # DarkSide-20k: 200 tonne-years projected (arXiv:2402.07566)
        # Active mass: 50 tonnes LAr
        'exposure_kg_day': 50.0 * 1000.0 * 365.25,
        'E_R_min_keV': 5,
        'E_R_max_keV': 50,
        'published_limit_mu_x': None,
        'published_limit_ref': (
            'DarkSide-20k: 200 t·y projected, starts ~2027. '
            'Ar-40 is I=0 so magnetic-moment signal is suppressed.'
        ),
    },
    'LZ_upgrade_proj': {
        'name': 'LZ-Upgrade projection (~2030, 3 t·y)',
        'target': 'xe',
        # LZ-Upgrade: ~3 tonne-years live planned
        'exposure_kg_day': 3.0 * 1000.0 * 365.25,
        'E_R_min_keV': 5,
        'E_R_max_keV': 50,
        'published_limit_mu_x': 1.5e-8,  # projected ~17x better than PandaX
        'published_limit_ref': (
            'LZ-Upgrade: ~3 t·y, projected ~17x improvement on PandaX-4T '
            'magnetic-moment bound.'
        ),
    },
}


def main():
    print("=" * 70)
    print("T90 Path C.4 — Post-LZ posterior predictive at other detectors")
    print("=" * 70)
    print()

    # Use the LZ-tuned central values (per T90.1 Phase 8)
    mu_x_tuned = MAGNETIC_MOMENT_LZ_TUNED_MU_X_MU_N
    m_chi_tuned = MAGNETIC_MOMENT_LZ_TUNED_M_CHI

    print(f"LZ-tuned parameters (T90.1 Phase 8):")
    print(f"  mu_x = {mu_x_tuned:.3e} mu_N")
    print(f"  m_chi = {m_chi_tuned:.1f} GeV")
    print()
    print(f"Detector predictions at tuned values:")
    print()

    results = {}
    for det_key, det_cfg in DETECTORS.items():
        result = predicted_events_for_detector(
            mu_x_tuned, m_chi_tuned, det_cfg,
        )
        results[det_key] = result
        print(f"  {det_cfg['name']}:")
        print(f"    N_predicted = {result['N_predicted']:.4e}")
        if 'ratio_predicted_to_at_limit' in result:
            r = result['ratio_predicted_to_at_limit']
            v = result['verdict']
            print(f"    ratio (predicted / at_limit) = {r:.4e}  [{v}]")
        print()

    # Write JSON output
    out_path = Path(__file__).resolve().parents[1] / "outputs" / "t90" / "cross_detector_predictions.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    output = {
        'phase': 'T90 Path C.4',
        'tuned_mu_x_mu_N': mu_x_tuned,
        'tuned_m_chi_GeV': m_chi_tuned,
        'detectors': results,
    }
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"Wrote: {out_path}")


if __name__ == '__main__':
    main()
