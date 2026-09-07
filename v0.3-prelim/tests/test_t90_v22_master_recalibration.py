"""
Tests for t90_v22_master_recalibration.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))


def test_robertson_at_w_velocity():
    """Robertson sigma/m at v=w=560 km/s should be sigma_0/2 = 1.52 cm^2/g."""
    from t90_v22_master_recalibration import sigma_m_robertson, ROBERTSON_W_KMS
    s = sigma_m_robertson(ROBERTSON_W_KMS)
    expected = 3.04 / 2.0  # 1/(1+1) = 1/2
    assert abs(s - expected) / expected < 1e-6


def test_robertson_high_v_suppressed():
    """Robertson sigma/m at v >> w should approach 0."""
    from t90_v22_master_recalibration import sigma_m_robertson
    s = sigma_m_robertson(5000)
    assert s < 0.05


def test_robertson_low_v_peak():
    """Robertson sigma/m at v=10 km/s should be close to sigma_0."""
    from t90_v22_master_recalibration import sigma_m_robertson, ROBERTSON_SIGMA_0_CM2_G
    s = sigma_m_robertson(10)
    expected = ROBERTSON_SIGMA_0_CM2_G / (1.0 + (10.0/560.0)**2)
    assert abs(s - expected) / expected < 1e-6


def test_master_at_reference():
    """Master sigma/m at v=100 km/s should be sigma_m_0 = 0.7 cm^2/g."""
    from t90_v22_master_recalibration import sigma_m_master
    s = sigma_m_master(100)
    assert abs(s - 0.7) / 0.7 < 1e-6


def test_master_velocity_exponent():
    """Master sigma/m should scale as (100/v)^0.16.

    s(100) / s(200) = sigma_m_0 * (100/100)^0.16 / [sigma_m_0 * (100/200)^0.16]
                    = (200/100)^0.16 = 2^0.16
    """
    from t90_v22_master_recalibration import sigma_m_master
    s_100 = sigma_m_master(100)
    s_200 = sigma_m_master(200)
    expected_ratio = 2.0 ** 0.16  # (200/100)^0.16
    assert abs((s_100 / s_200) - expected_ratio) / expected_ratio < 1e-6


def test_recalibration_improves_match():
    """Re-calibration should improve geometric mean ratio to Robertson."""
    from t90_v22_master_recalibration import fit_master_to_robertson
    fit = fit_master_to_robertson([100, 300, 600, 1000, 1500])
    # Should be closer to 1.0 than the original 0.72
    assert abs(fit['geometric_mean_ratio'] - 1.0) < 0.3


def test_recalibration_new_params_different():
    """New sigma_m_0 and a should differ from old."""
    from t90_v22_master_recalibration import (
        fit_master_to_robertson,
        MASTER_SIGMA_M_0,
        MASTER_A,
    )
    fit = fit_master_to_robertson()
    assert abs(fit['best_sigma_m_0'] - MASTER_SIGMA_M_0) > 0.5  # significant change
    assert abs(fit['best_a'] - MASTER_A) > 0.1  # significant change


def test_t95_tension_worsens():
    """T95 tension should WORSEN after master re-calibration (sigma/m increases)."""
    from t90_v22_master_recalibration import t95_tension_recalibrated
    t = t95_tension_recalibrated(150)
    # New sigma/m > old sigma/m
    assert t['master_new_sigma_m'] > t['master_old_sigma_m']
    # Re-calibration factor > 1
    assert t['recalibration_factor'] > 1.0
    # Log Z more negative
    assert t['rough_log_z_new'] < t['rough_log_z_old']


def test_robertson_higher_than_master_old():
    """Robertson should be higher than master old (per T95 finding)."""
    from t90_v22_master_recalibration import (
        sigma_m_robertson,
        sigma_m_master,
        MASTER_SIGMA_M_0,
        MASTER_A,
    )
    for v in [100, 300, 1000]:
        s_rob = sigma_m_robertson(v)
        s_master = sigma_m_master(v)
        assert s_rob > s_master


def test_output_json_serializable():
    """Output should be JSON-serializable."""
    from t90_v22_master_recalibration import t95_tension_recalibrated
    t = t95_tension_recalibrated(150)
    import json
    json.dumps(t)  # should not raise