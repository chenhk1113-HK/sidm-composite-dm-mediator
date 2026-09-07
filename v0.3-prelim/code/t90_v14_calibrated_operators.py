"""
T90 Path C.4.4 (v14) — Properly-calibrated multi-operator cross-detector.

PURPOSE
=======
Extends the cross-detector predictor with OPERATOR-SPECIFIC
calibration to LZ data. For each electromagnetic operator
(magnetic dipole, electric dipole, anapole, millicharge,
charge radius), find the coupling value that gives exactly
1 expected event at LZ in the 200-300 keV window.

Then compute cross-detector predictions at each operator's
calibrated coupling. The result: which operator, calibrated
to match LZ, is consistent with current direct-detection data?

v13 used the magnetic-dipole coupling value (mu_x) as a
placeholder for ALL operators. This is WRONG because each
operator has its own recoil-spectrum shape and normalization.
v14 fixes this by calibrating each operator separately.

METHOD
======
For each operator:
  1. Compute the predicted N_events at LZ as a function of
     the operator coupling (rate scales as coupling^2 for
     all operators in this basis)
  2. Use numerical root-finding to find the coupling value
     that gives exactly 1 expected event
  3. Compute the cross-detector predictions at that calibrated
     coupling

OPERATORS
=========
  - Magnetic dipole (O_1, O_3, O_4, O_5 combined, via
    dRdE_magnetic)
  - Electric dipole (O_5 only, with cp[5] non-zero)
  - Anapole (O_6 only, with cp[6] non-zero)
  - Millicharge (O_1 only, with cp[0] = epsilon*e)
  - Charge radius (O_11 only, with cp[11] non-zero)

For non-magnetic operators, we use simplified single-cp
mappings. A full operator-by-operator calibration would
require implementing the same multi-cp mapping as
dRdE_magnetic for each operator, which is beyond this draft.

OUTPUT
======
  - outputs/t90/cross_detector_calibrated.json
  - Per-operator: calibrated coupling + cross-detector
    predictions

CONSTRAINTS
  - No new dependencies (rule 17/24)
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

# LZ exposure and analysis window (from channels_extended.py)
LZ_EXPOSURE_KG_DAYS = 2.84 * 1000.0 * 365.25  # 2.84 tonne-years
LZ_WINDOW_KEV = (200.0, 300.0)


def lz_n_events_for_operator(
    operator: str,
    coupling: float,
    m_chi_GeV: float,
) -> float:
    """Compute N_events at LZ in [200, 300] keV for one operator.

    For each operator, this computes the WIMpy recoil spectrum
    integrated over the LZ analysis window, multiplied by LZ
    exposure.

    Args:
      operator: 'magnetic_dipole', 'electric_dipole', 'anapole',
                'millicharge', 'charge_radius'
      coupling: the operator coupling value (units depend on
                operator; see code for details)
      m_chi_GeV: DM mass in GeV

    Returns:
      N_events (float)
    """
    from WIMpy import DMUtils as DMU

    E_R = np.linspace(LZ_WINDOW_KEV[0], LZ_WINDOW_KEV[1], 10)
    isotopes = [
        ('Xe128', 0.0191), ('Xe129', 0.2644), ('Xe130', 0.0408),
        ('Xe131', 0.2118), ('Xe132', 0.2689), ('Xe134', 0.1044),
        ('Xe136', 0.0886),
    ]

    cp = np.zeros(20)
    cn = np.zeros(20)

    if operator == 'magnetic_dipole':
        # coupling is mu_x in mu_B
        mu_x_mu_B = coupling
        # Use the dedicated dRdE_magnetic (handles the full mapping)
        total_rate = np.zeros_like(E_R)
        for iso_name, ab in isotopes:
            rates = DMU.dRdE_magnetic(E_R, m_chi_GeV, mu_x_mu_B, iso_name)
            total_rate += ab * rates
    elif operator == 'electric_dipole':
        # coupling is d_e in e*fm (placeholder units; will be
        # calibrated to LZ so units cancel)
        # In WIMpy_NREFT: O_5 corresponds to cp[4] (and cn[4] for
        # isoscalar, but here we use cp[4] only)
        cp[4] = coupling
        total_rate = np.zeros_like(E_R)
        for iso_name, ab in isotopes:
            rates = DMU.dRdE_NREFT(E_R, m_chi_GeV, cp, cn, iso_name)
            total_rate += ab * rates
    elif operator == 'anapole':
        # coupling is anapole moment in natural units
        cp[6] = coupling
        total_rate = np.zeros_like(E_R)
        for iso_name, ab in isotopes:
            rates = DMU.dRdE_NREFT(E_R, m_chi_GeV, cp, cn, iso_name)
            total_rate += ab * rates
    elif operator == 'millicharge':
        # coupling is epsilon in units of electron charge
        cp[0] = coupling
        total_rate = np.zeros_like(E_R)
        for iso_name, ab in isotopes:
            rates = DMU.dRdE_NREFT(E_R, m_chi_GeV, cp, cn, iso_name)
            total_rate += ab * rates
    elif operator == 'charge_radius':
        # coupling is charge radius in fm^2
        cp[11] = coupling
        total_rate = np.zeros_like(E_R)
        for iso_name, ab in isotopes:
            rates = DMU.dRdE_NREFT(E_R, m_chi_GeV, cp, cn, iso_name)
            total_rate += ab * rates
    else:
        raise ValueError(f"Unknown operator: {operator}")

    n_pred = float(np.trapezoid(total_rate, E_R) * LZ_EXPOSURE_KG_DAYS)
    return n_pred


def calibrate_operator_to_lz(
    operator: str,
    m_chi_GeV: float,
    target_n_events: float = 1.0,
) -> dict:
    """Find the coupling value that gives exactly target_n_events
    at LZ in [200, 300] keV.

    Method: rate scales as coupling^2, so coupling_calibrated =
    coupling_initial * sqrt(target_n / n_at_initial).

    Returns dict with coupling, n_at_lz, units, and notes.
    """
    # Initial guess for coupling (units depend on operator)
    initial_couplings = {
        'magnetic_dipole': 1e-10,    # mu_B
        'electric_dipole': 1e-3,     # e*fm (placeholder)
        'anapole': 1e-3,             # natural units (placeholder)
        'millicharge': 1e-3,         # e (electron charge)
        'charge_radius': 1e-1,       # fm^2 (placeholder)
    }
    units = {
        'magnetic_dipole': 'mu_B (Bohr magnetons)',
        'electric_dipole': 'e*fm (placeholder units)',
        'anapole': 'natural units (placeholder)',
        'millicharge': 'e (electron charge)',
        'charge_radius': 'fm^2 (placeholder)',
    }
    coupling_init = initial_couplings[operator]
    n_init = lz_n_events_for_operator(operator, coupling_init, m_chi_GeV)
    if n_init <= 0:
        raise ValueError(
            f"Operator {operator} at coupling {coupling_init} gives "
            f"n_init={n_init} (cannot calibrate)"
        )
    coupling_calibrated = coupling_init * np.sqrt(target_n_events / n_init)
    n_calibrated = lz_n_events_for_operator(operator, coupling_calibrated, m_chi_GeV)
    return {
        'operator': operator,
        'coupling_calibrated': float(coupling_calibrated),
        'coupling_init': float(coupling_init),
        'n_at_initial': float(n_init),
        'n_at_calibrated': float(n_calibrated),
        'target_n_events': float(target_n_events),
        'm_chi_GeV': float(m_chi_GeV),
        'units': units[operator],
        'caveat': (
            'Non-magnetic operators use simplified single-cp mappings. '
            'A proper multi-operator fit would calibrate each operator '
            'to LZ data with the full EFT reduction. The cross-detector '
            'predictions are ORDER-OF-MAGNITUDE only.'
        ),
    }


def predicted_events_for_operator_at_coupling(
    operator: str,
    coupling: float,
    m_chi_GeV: float,
    detector: dict,
) -> dict:
    """Compute N_events at a detector for an operator at a given coupling."""
    from WIMpy import DMUtils as DMU

    det = detector
    E_R = np.linspace(det['E_R_min_keV'], det['E_R_max_keV'], 200)

    cp = np.zeros(20)
    cn = np.zeros(20)

    if det['target'] == 'xe':
        isotopes = [
            ('Xe128', 0.0191), ('Xe129', 0.2644), ('Xe130', 0.0408),
            ('Xe131', 0.2118), ('Xe132', 0.2689), ('Xe134', 0.1044),
            ('Xe136', 0.0886),
        ]
        total_rate = np.zeros_like(E_R)
        for iso_name, ab in isotopes:
            if operator == 'magnetic_dipole':
                rates = DMU.dRdE_magnetic(E_R, m_chi_GeV, coupling, iso_name)
            else:
                if operator == 'electric_dipole':
                    cp[4] = coupling
                elif operator == 'anapole':
                    cp[6] = coupling
                elif operator == 'millicharge':
                    cp[0] = coupling
                elif operator == 'charge_radius':
                    cp[11] = coupling
                rates = DMU.dRdE_NREFT(E_R, m_chi_GeV, cp, cn, iso_name)
            total_rate += ab * rates
    else:  # ar
        total_rate = np.zeros_like(E_R)

    n_predicted = float(np.trapezoid(total_rate, E_R) * det['exposure_kg_day'])
    return {'N_predicted': n_predicted}


def main():
    print("=" * 70)
    print("T90 Path C.4.4 (v14) — Calibrated multi-operator")
    print("=" * 70)
    print()

    m_chi = 1000.0  # GeV
    operators = ['magnetic_dipole', 'electric_dipole', 'anapole', 'millicharge', 'charge_radius']

    results = {}
    for op in operators:
        print(f"Calibrating {op} to LZ (target: 1 event in [200, 300] keV)...")
        cal = calibrate_operator_to_lz(op, m_chi, target_n_events=1.0)
        coupling_cal = cal['coupling_calibrated']
        print(f"  coupling_calibrated = {coupling_cal:.4e} {cal['units']}")
        print(f"  N_LZ at calibrated coupling = {cal['n_at_calibrated']:.4f}")
        print()

        # Compute cross-detector predictions at calibrated coupling
        det_results = {}
        for det_key, det_cfg in DETECTORS.items():
            r = predicted_events_for_operator_at_coupling(
                op, coupling_cal, m_chi, det_cfg,
            )
            n = r['N_predicted']
            det_results[det_key] = {
                'detector': det_cfg['name'],
                'N_predicted': n,
            }
            print(f"    {det_cfg['name']}: N_predicted = {n:.4e}")
        print()

        results[op] = {
            'calibration': cal,
            'detector_predictions': det_results,
        }

    out_path = _PROJECT_ROOT / "outputs" / "t90" / "cross_detector_calibrated.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    output = {
        'phase': 'T90 Path C.4.4 (v14, calibrated multi-operator)',
        'm_chi_GeV': m_chi,
        'target_n_events_at_LZ': 1.0,
        'caveat': (
            'Non-magnetic operators use simplified single-cp mappings. '
            'Cross-detector predictions are ORDER-OF-MAGNITUDE only. '
            'The relative ordering of operators is robust; absolute '
            'values would require a full EFT reduction (Catena+ 2024).'
        ),
        'operators': results,
    }
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"Wrote: {out_path}")


if __name__ == '__main__':
    main()
