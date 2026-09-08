"""
Tests for t90_v14_calibrated_operators.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))


def test_calibration_produces_target_n_events():
    """After calibration, N_LZ should equal the target (1 event)."""
    from t90_v14_calibrated_operators import (
        calibrate_operator_to_lz,
    )
    for op in ['magnetic_dipole', 'electric_dipole', 'anapole',
               'millicharge', 'charge_radius']:
        cal = calibrate_operator_to_lz(op, 1000.0, target_n_events=1.0)
        n_cal = cal['n_at_calibrated']
        assert abs(n_cal - 1.0) < 1e-3, (
            f"{op}: N_at_calibrated={n_cal} != 1.0"
        )


def test_magnetic_dipole_matches_lz_tuned():
    """Magnetic dipole calibration should reproduce the LZ-tuned mu_x."""
    from t90_v14_calibrated_operators import calibrate_operator_to_lz
    cal = calibrate_operator_to_lz('magnetic_dipole', 1000.0)
    # LZ-tuned mu_x = 6.10e-8 mu_N = 6.10e-8 / 1836.15267 mu_B
    expected_mu_B = 6.10e-8 / 1836.15267
    coupling_cal = cal['coupling_calibrated']
    assert abs(coupling_cal - expected_mu_B) / expected_mu_B < 0.05, (
        f"Magnetic dipole calibration {coupling_cal:.4e} differs from "
        f"expected {expected_mu_B:.4e} by >5%"
    )


def test_coupling_squared_scaling():
    """N_events should scale as coupling^2 (within tolerance)."""
    from t90_v14_calibrated_operators import lz_n_events_for_operator

    # Magnetic dipole at 2x coupling should give 4x events
    n1 = lz_n_events_for_operator('magnetic_dipole', 1e-11, 1000.0)
    n2 = lz_n_events_for_operator('magnetic_dipole', 2e-11, 1000.0)
    ratio = n2 / n1
    assert abs(ratio - 4.0) < 1e-6, (
        f"Expected n2/n1 = 4 (coupling^2 scaling), got {ratio}"
    )


def test_all_operators_have_different_predictions():
    """Each operator should give different predictions at LZ-calibrated
    coupling (otherwise they're degenerate)."""
    from t90_v14_calibrated_operators import calibrate_operator_to_lz

    couplings = {}
    for op in ['magnetic_dipole', 'electric_dipole', 'anapole',
               'millicharge', 'charge_radius']:
        cal = calibrate_operator_to_lz(op, 1000.0)
        couplings[op] = cal['coupling_calibrated']

    # All 5 couplings should be different
    vals = list(couplings.values())
    assert len(set(vals)) == len(vals), (
        f"Some operators have identical calibrated couplings: {couplings}"
    )


def test_millicharge_largest_cross_detector():
    """Millicharge, calibrated to LZ, should predict the largest
    PandaX-4T signal (because cp[0] = millicharge couples to
    all nucleons via O_1 = scalar SI)."""
    from t90_v14_calibrated_operators import (
        calibrate_operator_to_lz,
        predicted_events_for_operator_at_coupling,
    )
    from t90_v10_cross_detector import DETECTORS

    det = DETECTORS['PandaX4T_Run01']
    predictions = {}
    for op in ['magnetic_dipole', 'electric_dipole', 'anapole',
               'millicharge', 'charge_radius']:
        cal = calibrate_operator_to_lz(op, 1000.0)
        r = predicted_events_for_operator_at_coupling(
            op, cal['coupling_calibrated'], 1000.0, det,
        )
        predictions[op] = r['N_predicted']

    max_op = max(predictions, key=predictions.get)
    assert max_op == 'millicharge', (
        f"Expected millicharge to give the largest PandaX prediction, "
        f"got {max_op} (predictions: {predictions})"
    )
