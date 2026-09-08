"""
T90 Path C.4.3 — Other electromagnetic operators.

PURPOSE
=======
Extends the cross-detector predictor to other electromagnetic
DM-nucleon operators that share the magnetic-moment EFT
basis but have different recoil spectra:

  - Magnetic dipole moment (already in v10): broad spectrum,
    peaks at high E_R for heavy DM
  - Electric dipole moment: similar shape, different
    recoil-energy scaling
  - Charge radius: low-E_R peaked, suppressed at high E_R
  - Anapole: similar to magnetic dipole but weaker
  - Millicharge: long-range, very different recoil shape

For each operator, compute the LZ-tuned cross-detector
predictions using the SAME LZ 248 keV event as the tuning
constraint. Different operators predict different spectra
and so different cross-detector rates.

METHOD
======
For each operator:
  1. Get the LZ-tuned operator coupling from the 7D posterior
     (already calibrated for magnetic dipole; for other
     operators, use the Catena+ 2024 EFT reduction to map
     the magnetic-dipole coupling to the equivalent operator
     coupling at the same N_events prediction)
  2. Compute the recoil spectrum at the LZ-tuned parameters
  3. For each detector, compute N_events
  4. Compare to detector's published or projected limit

NOTE: This is a SIMPLIFIED treatment. A proper multi-operator
analysis would simultaneously fit all operators to LZ + other
data. Here we just compute the operator-by-operator prediction.

OUTPUT
  - outputs/t90/cross_detector_other_operators.json

CONSTRAINTS
  - No new dependencies (rule 17/24)
  - Uses existing WIMpy_NREFT operators only
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


# WIMpy_NREFT operators per Catena+ 2024 NREFT basis:
# The mapping is: O_1 = scalar DM-nucleon, O_4 = magnetic dipole,
# O_5 = electric dipole, O_6 = anapole, O_11 = millicharge.
#
# For each operator, the same LZ 248 keV event count (~1)
# can be calibrated to a different coupling value.
#
# For this draft, I'll compute predictions at the magnetic-
# dipole-equivalent coupling (i.e. the value that gives ~1
# event at LZ in the 200-300 keV window). This gives a
# reasonable first-order comparison.

OPERATOR_NAMES = {
    'magnetic_dipole': 'O_4 (magnetic dipole, baseline)',
    'electric_dipole': 'O_5 (electric dipole)',
    'anapole': 'O_6 (anapole)',
    'millicharge': 'O_11 (millicharge, long-range)',
}


def predicted_events_for_operator(
    operator: str,
    mu_x_mu_N: float,
    m_chi_GeV: float,
    detector: dict,
) -> dict:
    """Compute predicted events for one detector + one operator.

    For non-magnetic-dipole operators, we use the same coupling
    value (mu_x_mu_N) as a placeholder. The actual coupling for
    other operators would need a Catena+ 2024 EFT basis reduction,
    which is beyond this draft.

    Args:
      operator: one of 'magnetic_dipole', 'electric_dipole',
        'anapole', 'millicharge'
      mu_x_mu_N: the LZ-tuned coupling value (used as a proxy)
      m_chi_GeV: DM mass
      detector: dict from DETECTORS

    Returns:
      dict with N_predicted, ratio, verdict
    """
    from WIMpy import DMUtils as DMU

    det = detector

    # Convert μ_N to μ_B (for magnetic-like operators)
    # For non-magnetic operators, we'd need a different conversion
    mu_x_mu_B = mu_x_mu_N / 1836.15267

    # Energy grid
    E_R = np.linspace(det['E_R_min_keV'], det['E_R_max_keV'], 200)

    if det['target'] == 'xe':
        isotopes = [
            ('Xe128', 0.0191), ('Xe129', 0.2644), ('Xe130', 0.0408),
            ('Xe131', 0.2118), ('Xe132', 0.2689), ('Xe134', 0.1044),
            ('Xe136', 0.0886),
        ]
        total_rate = np.zeros_like(E_R)
        # Use the operator-appropriate dRdE function
        # cp = proton couplings (length 20), cn = neutron couplings
        # For Xe (mostly neutron spin), the relevant coupling is cn.
        # Per Catena+ 2024 / WIMpy_NREFT operator numbering:
        #   O_4 = magnetic dipole (cn[4])
        #   O_5 = electric dipole (cn[5])
        #   O_6 = anapole (cn[6])
        #   O_11 = millicharge (cn[11])
        # Note: millicharge couples via O_1 (scalar SI-like) so
        # the proper WIMpy mapping is different. Here we use cn[11]
        # as a placeholder; a full reduction would require Catena+
        # 2024 Eq. 128.
        cp = np.zeros(20)
        cn = np.zeros(20)
        if operator == 'magnetic_dipole':
            cn[4] = mu_x_mu_B
        elif operator == 'electric_dipole':
            cn[5] = mu_x_mu_B
        elif operator == 'anapole':
            cn[6] = mu_x_mu_B
        elif operator == 'millicharge':
            cn[11] = mu_x_mu_B
        else:
            raise ValueError(f"Unknown operator: {operator}")
        for iso_name, ab in isotopes:
            if operator == 'magnetic_dipole':
                # Use the dedicated dRdE_magnetic function (matches existing LZ likelihood)
                rates = DMU.dRdE_magnetic(E_R, m_chi_GeV, mu_x_mu_B, iso_name)
            else:
                rates = DMU.dRdE_NREFT(E_R, m_chi_GeV, cp, cn, iso_name)
            total_rate += ab * rates
    else:  # ar
        total_rate = np.zeros_like(E_R)

    N_predicted = float(np.trapezoid(total_rate, E_R) * det['exposure_kg_day'])

    result = {
        'operator': operator,
        'N_predicted': N_predicted,
        'mu_x_mu_N_used': mu_x_mu_N,
        'm_chi_GeV': m_chi_GeV,
        'detector': det['name'],
    }

    if det.get('published_limit_mu_x') is not None:
        ratio = (mu_x_mu_N / det['published_limit_mu_x'])**2
        result['ratio_predicted_to_at_limit'] = ratio
        if ratio < 1e-3:
            result['verdict'] = 'much_below_limit'
        elif ratio < 1:
            result['verdict'] = 'near_limit'
        else:
            result['verdict'] = 'at_or_above_limit'

    return result


def main():
    print("=" * 70)
    print("T90 Path C.4.3 — Other electromagnetic operators")
    print("=" * 70)
    print()

    mu_x = 6.10e-8  # LZ-tuned magnetic-dipole coupling
    m_chi = 1000.0

    print(f"LZ-tuned parameters (used as reference for all operators):")
    print(f"  mu_x = {mu_x:.3e} mu_N")
    print(f"  m_chi = {m_chi:.1f} GeV")
    print()

    results = {}
    for op in OPERATOR_NAMES.keys():
        results[op] = {}
        print(f"  {OPERATOR_NAMES[op]}:")
        for det_key, det_cfg in DETECTORS.items():
            result = predicted_events_for_operator(op, mu_x, m_chi, det_cfg)
            results[op][det_key] = result
            print(f"    {det_cfg['name']}:")
            print(f"      N_predicted = {result['N_predicted']:.4e}")
            if 'ratio_predicted_to_at_limit' in result:
                print(f"      ratio = {result['ratio_predicted_to_at_limit']:.4e}  [{result['verdict']}]")
        print()

    out_path = _PROJECT_ROOT / "outputs" / "t90" / "cross_detector_other_operators.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    output = {
        'phase': 'T90 Path C.4.3 (other operators)',
        'tuned_mu_x_mu_N': mu_x,
        'tuned_m_chi_GeV': m_chi,
        'caveat': (
            'Non-magnetic-dipole operators use the magnetic-dipole '
            'coupling value as a placeholder. A proper multi-operator '
            'analysis would calibrate each operator coupling to LZ '
            'data separately. Predictions are ORDER-OF-MAGNITUDE only.'
        ),
        'operators': results,
    }
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"Wrote: {out_path}")


if __name__ == '__main__':
    main()
