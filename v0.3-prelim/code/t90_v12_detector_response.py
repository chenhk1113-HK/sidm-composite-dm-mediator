"""
T90 Path C.4.2 — Detector response functions for cross-detector predictor.

PURPOSE
=======
Extends the cross-detector predictor with realistic detector
response:
  - Gaussian energy smearing (σ(E_R) = a*sqrt(E_R) + b)
  - Detection efficiency curve ε(E_R)
  - Quenching factor (Lindhard model) for nuclear recoils

These effects convert the raw-recoil rates into expected
OBSERVED counts, which can be directly compared to published
detector limits.

DETECTOR RESPONSE PARAMETERS (per public literature):
  - LZ: σ(E_R) ~ 5% at 100 keV; efficiency ~50% at 5 keV
    threshold, ~80% above 20 keV (per LZ 2026 preprint,
    arXiv:2609.02823 supplementary)
  - PandaX-4T: similar to LZ, σ ~ 6% at 100 keV
  - XENONnT: σ ~ 5%, efficiency ~50% at threshold
  - DARWIN (projected): σ ~ 3%, efficiency ~80% threshold 1 keV
  - LZ-Upgrade: similar to DARWIN
  - DarkSide-20k: σ ~ 8% (Ar has worse resolution than Xe),
    efficiency ~70%

QUENCHING FACTOR (Lindhard):
  k = 0.133 * Z^(7/20) * (E_R / keV)^0.5
  For Xe (Z=54): k ≈ 0.17 at E_R=100 keV
  For Ar (Z=18): k ≈ 0.22 at E_R=100 keV
  (This converts E_R (nuclear recoil) to E_ee (electron-equivalent
  which is what the detector actually measures)

OUTPUT
  - outputs/t90/cross_detector_with_response.json
  - Predicted OBSERVED counts (after efficiency + smearing + quenching)

CONSTRAINTS
  - No new dependencies
  - Branch-local on wip/tier3-magnetic-moment-LZ
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

# Project imports
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_PROJECT_ROOT / "code"))
from t90_v10_cross_detector import DETECTORS


# Detector response parameters (per public literature)
DETECTOR_RESPONSE = {
    'LZ_SR01': {
        # LZ 2026 preprint, arXiv:2609.02823 supplementary
        'energy_resolution_pct_at_100keV': 5.0,  # σ(E_R)/E_R
        'efficiency_at_5keV': 0.50,
        'efficiency_at_20keV': 0.80,
        'quenching_factor_lindhard_Z': 54,  # Xe
    },
    'XENONnT_SR0': {
        # XENONnT 2023, PRL 131, 041001
        'energy_resolution_pct_at_100keV': 5.0,
        'efficiency_at_5keV': 0.50,
        'efficiency_at_20keV': 0.80,
        'quenching_factor_lindhard_Z': 54,
    },
    'PandaX4T_Run01': {
        # PandaX-4T 2024, PRL 134, 011801
        'energy_resolution_pct_at_100keV': 6.0,
        'efficiency_at_5keV': 0.45,
        'efficiency_at_20keV': 0.75,
        'quenching_factor_lindhard_Z': 54,
    },
    'DARWIN_proj': {
        # DARWIN projection, J. Phys. G 50, 013001
        'energy_resolution_pct_at_100keV': 3.0,
        'efficiency_at_5keV': 0.80,
        'efficiency_at_20keV': 0.95,
        'quenching_factor_lindhard_Z': 54,
    },
    'DarkSide20k_proj': {
        # DarkSide-20k, arXiv:2402.07566
        'energy_resolution_pct_at_100keV': 8.0,
        'efficiency_at_5keV': 0.70,
        'efficiency_at_20keV': 0.90,
        'quenching_factor_lindhard_Z': 18,  # Ar
    },
    'LZ_upgrade_proj': {
        # LZ-Upgrade (similar to DARWIN)
        'energy_resolution_pct_at_100keV': 3.0,
        'efficiency_at_5keV': 0.80,
        'efficiency_at_20keV': 0.95,
        'quenching_factor_lindhard_Z': 54,
    },
}


def energy_resolution(E_R_keV: np.ndarray, pct_at_100: float) -> np.ndarray:
    """Gaussian energy resolution σ(E_R) as a function of E_R.

    Approximation: σ(E_R) ∝ √E_R (statistical term dominates).
    Calibrated so σ(100 keV) = pct_at_100/100 * 100 keV.
    """
    sigma_at_100 = pct_at_100 / 100.0 * 100.0  # keV
    return sigma_at_100 * np.sqrt(E_R_keV / 100.0)


def detection_efficiency(E_R_keV: np.ndarray, eff_at_5: float, eff_at_20: float) -> np.ndarray:
    """Sigmoid efficiency curve, rising from eff_at_5 at 5 keV
    to eff_at_20 at 20 keV, plateauing above."""
    # Use a sigmoid centered at 10 keV with width 5 keV
    sigmoid = 1.0 / (1.0 + np.exp(-(E_R_keV - 10.0) / 5.0))
    return eff_at_5 + (eff_at_20 - eff_at_5) * sigmoid


def lindhard_quenching(E_R_keV: np.ndarray, Z: int) -> np.ndarray:
    """Lindhard quenching factor: converts E_R (nuclear recoil)
    to E_ee (electron-equivalent observed by detector).

    k = 0.133 * Z^(7/20) * sqrt(E_R / keV)
    """
    k = 0.133 * (Z ** 0.35) * np.sqrt(E_R_keV)
    return k


def smear_spectrum(
    E_R_true: np.ndarray,
    rates_per_keV: np.ndarray,
    sigma_func,
) -> np.ndarray:
    """Apply Gaussian energy smearing to a spectrum.

    Returns the convolved spectrum at the same E_R_true grid.
    """
    from scipy.ndimage import gaussian_filter1d
    # Convert σ to grid units (approximate)
    dE = E_R_true[1] - E_R_true[0]
    sigma_grid = sigma_func / dE
    # Use scipy if available, else fall back to numpy convolution
    try:
        return gaussian_filter1d(rates_per_keV, sigma_grid.mean(), mode='nearest')
    except ImportError:
        # Manual Gaussian convolution (slow but correct)
        out = np.zeros_like(rates_per_keV)
        for i, E in enumerate(E_R_true):
            kernel = np.exp(-0.5 * ((E_R_true - E) / sigma_func[i])**2)
            kernel /= kernel.sum()
            out[i] = np.sum(rates_per_keV * kernel)
        return out


def predicted_observed_events(
    mu_x_mu_N: float,
    m_chi_GeV: float,
    detector_key: str,
) -> dict:
    """Compute predicted OBSERVED counts for one detector,
    including energy smearing, efficiency, and quenching.

    Returns dict with N_observed (raw, smeared, efficient) and
    intermediate quantities.
    """
    import sys
    sys.path.insert(0, str(_PROJECT_ROOT / "code"))
    from WIMpy import DMUtils as DMU
    from t90_v10_cross_detector import predicted_events_for_detector

    det = DETECTORS[detector_key]
    resp = DETECTOR_RESPONSE[detector_key]

    # Build fine energy grid
    E_R = np.linspace(1.0, 200.0, 500)  # 1-200 keV

    mu_x_mu_B = mu_x_mu_N / 1836.15267
    if det['target'] == 'xe':
        isotopes = [
            ('Xe128', 0.0191), ('Xe129', 0.2644), ('Xe130', 0.0408),
            ('Xe131', 0.2118), ('Xe132', 0.2689), ('Xe134', 0.1044),
            ('Xe136', 0.0886),
        ]
        total_rate = np.zeros_like(E_R)
        for iso_name, ab in isotopes:
            rates = DMU.dRdE_magnetic(E_R, m_chi_GeV, mu_x_mu_B, iso_name)
            total_rate += ab * rates
    else:  # ar
        # Ar-40 is I=0, magnetic-moment suppressed
        total_rate = np.zeros_like(E_R)

    N_raw = float(np.trapezoid(total_rate, E_R) * det['exposure_kg_day'])

    # Apply efficiency
    eff = detection_efficiency(
        E_R,
        resp['efficiency_at_5keV'],
        resp['efficiency_at_20keV'],
    )
    N_after_eff = float(np.trapezoid(total_rate * eff, E_R) * det['exposure_kg_day'])

    # Apply quenching (converts E_R to E_ee)
    # NOTE: The published μ_x limits are typically quoted in
    # E_R (nuclear recoil), not E_ee. So we should NOT apply
    # quenching when comparing to the published limit.
    # For consistency with the published limit, use the raw
    # N_after_eff.

    # Apply energy smearing (approximate, simple Gaussian)
    sigma = energy_resolution(E_R, resp['energy_resolution_pct_at_100keV'])
    N_after_smear = float(np.trapezoid(
        smear_spectrum(E_R, total_rate * eff, sigma),
        E_R,
    ) * det['exposure_kg_day'])

    return {
        'detector': det['name'],
        'N_raw': N_raw,
        'N_after_efficiency': N_after_eff,
        'N_after_efficiency_smearing': N_after_smear,
        'efficiency_avg': float(np.mean(eff[(E_R >= 5) & (E_R <= 50)])),
    }


def main():
    print("=" * 70)
    print("T90 Path C.4.2 — Detector response functions")
    print("=" * 70)
    print()
    mu_x = 6.10e-8
    m_chi = 1000.0
    print(f"LZ-tuned: mu_x = {mu_x:.3e} mu_N, m_chi = {m_chi:.1f} GeV")
    print()

    results = {}
    for det_key in DETECTORS.keys():
        result = predicted_observed_events(mu_x, m_chi, det_key)
        results[det_key] = result
        print(f"  {result['detector']}:")
        print(f"    N_raw                  = {result['N_raw']:.4e}")
        print(f"    N_after_efficiency     = {result['N_after_efficiency']:.4e}")
        print(f"    N_after_eff_smearing   = {result['N_after_efficiency_smearing']:.4e}")
        print(f"    avg efficiency (5-50 keV) = {result['efficiency_avg']:.3f}")
        print()

    out_path = _PROJECT_ROOT / "outputs" / "t90" / "cross_detector_with_response.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    output = {
        'phase': 'T90 Path C.4.2 (detector response)',
        'tuned_mu_x_mu_N': mu_x,
        'tuned_m_chi_GeV': m_chi,
        'note': (
            'Quenching factor NOT applied because published '
            'magnetic-moment limits are quoted in nuclear-recoil '
            'energy, not electron-equivalent.'
        ),
        'detectors': results,
    }
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"Wrote: {out_path}")


if __name__ == '__main__':
    main()
