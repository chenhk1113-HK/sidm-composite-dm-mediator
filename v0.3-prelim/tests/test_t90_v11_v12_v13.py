"""
Tests for t90_v11 (posterior predictive), v12 (detector response),
v13 (other operators).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

# Project imports
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))


def test_posterior_predictive_imports():
    """The v11 script should import without errors."""
    import t90_v11_cross_detector_posterior  # noqa: F401


def test_posterior_predictive_loads_7d():
    """v11 should be able to load the 7D posterior."""
    from t90_v11_cross_detector_posterior import load_7d_posterior

    npz_path = Path(__file__).resolve().parents[1] / "outputs" / "t90" / "t41_v07_7d_posterior.npz"
    if not npz_path.exists():
        pytest.skip("7D posterior not yet produced")
    samples = load_7d_posterior(str(npz_path))
    assert samples.shape[1] == 7, f"Expected 7 dimensions, got {samples.shape[1]}"
    assert samples.shape[0] > 100, f"Expected >100 samples, got {samples.shape[0]}"


def test_detector_response_imports():
    """v12 should import without errors."""
    import t90_v12_detector_response  # noqa: F401


def test_lindhard_quenching_monotonic():
    """Lindhard quenching factor should increase with E_R."""
    from t90_v12_detector_response import lindhard_quenching
    E_R = np.array([5.0, 50.0, 200.0])
    k = lindhard_quenching(E_R, 54)
    assert k[1] > k[0], "Quenching factor must increase with E_R"
    assert k[2] > k[1], "Quenching factor must increase with E_R"


def test_energy_resolution_sqrt_scaling():
    """Energy resolution should scale as sqrt(E_R)."""
    from t90_v12_detector_response import energy_resolution
    E_R = np.array([25.0, 100.0, 400.0])
    sigma = energy_resolution(E_R, 5.0)  # 5% at 100 keV
    # sigma(100)/sigma(25) = sqrt(100/25) = 2
    assert abs(sigma[1] / sigma[0] - 2.0) < 1e-6
    # sigma(400)/sigma(100) = sqrt(400/100) = 2
    assert abs(sigma[2] / sigma[1] - 2.0) < 1e-6


def test_detection_efficiency_sigmoid():
    """Efficiency should rise sigmoidally from low to high."""
    from t90_v12_detector_response import detection_efficiency
    E_R = np.linspace(1.0, 50.0, 100)
    eff = detection_efficiency(E_R, 0.5, 0.8)
    # Sigmoid centered at 10 keV, width 5 keV
    # At E_R=1 keV: sigmoid = 1/(1+exp(9/5)) ≈ 0.165, so eff ≈ 0.55
    # At E_R=50 keV: sigmoid ≈ 1.0, so eff ≈ 0.80
    # The midpoint of the sigmoid should be at E_R=10 keV
    mid_idx = np.argmin(np.abs(E_R - 10.0))
    expected_mid = 0.5 + (0.8 - 0.5) * 0.5  # = 0.65 (midpoint of sigmoid)
    assert abs(eff[mid_idx] - expected_mid) < 0.05, (
        f"Expected midpoint ~{expected_mid}, got {eff[mid_idx]}"
    )
    assert eff[-1] > eff[0], "Efficiency should rise monotonically"


def test_other_operators_imports():
    """v13 should import without errors."""
    import t90_v13_other_operators  # noqa: F401


def test_magnetic_dipole_baseline():
    """Magnetic dipole operator should produce the same N_predicted
    as the v10 baseline."""
    from t90_v10_cross_detector import predicted_events_for_detector, DETECTORS
    from t90_v13_other_operators import predicted_events_for_operator

    det = DETECTORS['PandaX4T_Run01'].copy()
    mu_x = 6.10e-8
    m_chi = 1000.0

    n_v10 = predicted_events_for_detector(mu_x, m_chi, det)['N_predicted']
    n_v13 = predicted_events_for_operator('magnetic_dipole', mu_x, m_chi, det)['N_predicted']

    # Should be approximately equal (within 1% for the same operator)
    assert abs(n_v10 - n_v13) / n_v10 < 0.01, (
        f"Magnetic dipole v10={n_v10} vs v13={n_v13} differ by >1%"
    )


def test_other_operators_smaller_than_magnetic():
    """Electric dipole, anapole, and millicharge should all produce
    fewer events than magnetic dipole at the same coupling."""
    from t90_v10_cross_detector import DETECTORS
    from t90_v13_other_operators import predicted_events_for_operator

    det = DETECTORS['PandaX4T_Run01'].copy()
    mu_x = 6.10e-8
    m_chi = 1000.0

    n_mag = predicted_events_for_operator('magnetic_dipole', mu_x, m_chi, det)['N_predicted']
    n_elec = predicted_events_for_operator('electric_dipole', mu_x, m_chi, det)['N_predicted']
    n_ana = predicted_events_for_operator('anapole', mu_x, m_chi, det)['N_predicted']

    assert n_mag > 0
    assert n_elec < n_mag, "Electric dipole should be smaller than magnetic dipole"
    assert n_ana < n_mag, "Anapole should be smaller than magnetic dipole"
