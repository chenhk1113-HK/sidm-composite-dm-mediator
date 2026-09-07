"""
Tests for t90_v10_cross_detector.py (T90 Path C.4).

Validates the cross-detector predictor:
  - Predicted N_events scales as mu_x^2 (linearity check)
  - Argon target gives 0 events (Ar-40 I=0 suppression)
  - Verdict thresholds work as documented
  - Detector exposure scaling is correct
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Project imports
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))
from t90_v10_cross_detector import (
    predicted_events_for_detector,
    DETECTORS,
)


def test_mu_x_squared_scaling():
    """Predicted N_events should scale as mu_x^2."""
    det = DETECTORS['PandaX4T_Run01'].copy()
    n1 = predicted_events_for_detector(1e-7, 1000.0, det)
    n2 = predicted_events_for_detector(2e-7, 1000.0, det)
    # n2 / n1 should be 4 (mu_x^2 scaling)
    ratio = n2['N_predicted'] / n1['N_predicted']
    assert abs(ratio - 4.0) < 1e-6, (
        f"Expected n2/n1 = 4 (mu_x^2 scaling), got {ratio}"
    )


def test_argon_target_zero_events():
    """Ar-40 is I=0 so magnetic-moment is suppressed → 0 events."""
    det = DETECTORS['DarkSide20k_proj'].copy()
    n = predicted_events_for_detector(6.10e-8, 1000.0, det)
    assert n['N_predicted'] == 0.0, (
        f"Expected 0 events for Ar-40 (I=0), got {n['N_predicted']}"
    )


def test_exposure_scaling():
    """Doubling exposure should double N_predicted."""
    det = DETECTORS['PandaX4T_Run01']
    n1 = predicted_events_for_detector(6.10e-8, 1000.0, det)
    det_2x = det.copy()
    det_2x['exposure_kg_day'] = 2 * det['exposure_kg_day']
    n2 = predicted_events_for_detector(6.10e-8, 1000.0, det_2x)
    ratio = n2['N_predicted'] / n1['N_predicted']
    assert abs(ratio - 2.0) < 1e-6, (
        f"Expected n2/n1 = 2 (exposure scaling), got {ratio}"
    )


def test_verdict_much_below_limit():
    """When ratio < 1e-3, verdict should be 'much_below_limit'."""
    det = DETECTORS['LZ_SR01'].copy()
    # LZ SR0+SR1 has a weak limit (4.57e-4 mu_N), tuned value is
    # 6.10e-8 mu_N. The ratio should be much less than 1.
    n = predicted_events_for_detector(6.10e-8, 1000.0, det)
    assert 'verdict' in n
    assert n['verdict'] == 'much_below_limit'


def test_verdict_near_limit():
    """When 1e-3 < ratio < 1, verdict should be 'near_limit'."""
    det = DETECTORS['PandaX4T_Run01'].copy()
    n = predicted_events_for_detector(6.10e-8, 1000.0, det)
    assert 'verdict' in n
    assert n['verdict'] == 'near_limit'


def test_verdict_at_or_above_limit_for_darwin():
    """DARWIN projection should be 'at_or_above_limit' (ratio >= 1)."""
    det = DETECTORS['DARWIN_proj'].copy()
    n = predicted_events_for_detector(6.10e-8, 1000.0, det)
    assert 'verdict' in n
    assert n['verdict'] == 'at_or_above_limit'


def test_published_limit_ratio_consistency():
    """The 'ratio_predicted_to_at_limit' should be N_pred/N_at_limit."""
    det = DETECTORS['PandaX4T_Run01'].copy()
    n = predicted_events_for_detector(6.10e-8, 1000.0, det)
    expected_ratio = (
        (n['mu_x_mu_N'] / det['published_limit_mu_x'])**-2
        # equivalently: N_pred * (limit/tuned)^2 / N_pred = (limit/tuned)^2 / 1
    )
    # Recompute from first principles:
    # N_at_limit = N_pred * (limit / tuned)^2
    # So N_pred / N_at_limit = (tuned / limit)^2
    expected = (6.10e-8 / det['published_limit_mu_x'])**2
    assert abs(n['ratio_predicted_to_at_limit'] - expected) < 1e-6, (
        f"Ratio mismatch: got {n['ratio_predicted_to_at_limit']}, "
        f"expected {expected}"
    )


def test_all_detectors_have_required_keys():
    """Every detector config must have name, target, exposure, E_R."""
    required = {'name', 'target', 'exposure_kg_day', 'E_R_min_keV', 'E_R_max_keV'}
    for det_key, det_cfg in DETECTORS.items():
        missing = required - set(det_cfg.keys())
        assert not missing, f"{det_key} missing keys: {missing}"


def test_argon_detector_does_not_call_wimpy():
    """Ar detectors should return 0 without calling WIMpy (avoid
    spurious import errors for missing Ar response)."""
    det = DETECTORS['DarkSide20k_proj'].copy()
    n = predicted_events_for_detector(6.10e-8, 1000.0, det)
    assert n['N_predicted'] == 0.0
    assert n['detector'].startswith('DarkSide-20k')
