"""Tests for T90.49 inelastic SIDM module.

Per T90.49 scope:
  - The inelastic SIDM module imports cleanly
  - v_threshold_kms gives correct kinematic threshold
  - sigma_m_inelastic returns elastic + endothermic + total
  - Threshold gates the endothermic channel correctly
  - At the reference point, sigma/m values are finite
"""

import numpy as np
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(Path(__file__).resolve().parent.parent / "code")))


def test_v49_module_imports():
    """The T90.49 inelastic SIDM module imports cleanly."""
    from t90_v49_inelastic_sidm import (  # noqa: F401
        v_threshold_kms, sigma_m_inelastic, evaluate_inelastic_point,
        C_KMS,
    )


def test_v49_threshold_at_delta_100_eV():
    """v_threshold at delta=100 eV, m_chi=30 GeV is ~30-40 km/s."""
    from t90_v49_inelastic_sidm import v_threshold_kms
    v_min = v_threshold_kms(100.0, 30.0)
    # Expected ~30-35 km/s
    assert 25 < v_min < 50, f"v_min={v_min:.1f} not in expected range"


def test_v49_threshold_scales_with_delta():
    """Threshold velocity scales as sqrt(delta)."""
    from t90_v49_inelastic_sidm import v_threshold_kms
    v_min_100 = v_threshold_kms(100.0, 30.0)
    v_min_400 = v_threshold_kms(400.0, 30.0)
    # v_min(400) / v_min(100) = sqrt(400/100) = 2
    assert abs(v_min_400 / v_min_100 - 2.0) < 0.01


def test_v49_threshold_scales_with_mass():
    """Threshold velocity scales as 1/sqrt(m_chi)."""
    from t90_v49_inelastic_sidm import v_threshold_kms
    v_min_30 = v_threshold_kms(100.0, 30.0)
    v_min_120 = v_threshold_kms(100.0, 120.0)
    # v_min(120) / v_min(30) = sqrt(30/120) = 0.5
    assert abs(v_min_120 / v_min_30 - 0.5) < 0.01


def test_v49_inelastic_below_threshold():
    """Below threshold, only elastic contributes (endothermic = 0)."""
    from t90_v49_inelastic_sidm import sigma_m_inelastic
    # delta=1000 eV, m_chi=30 GeV -> v_min ~ 110 km/s
    # At v=28 (Cloud-9), well below threshold
    r = sigma_m_inelastic(v_kms=28.0, m_phi_MeV=50.0, m_chi_GeV=30.0, g_chi=0.5, delta_eV=1000.0)
    assert not r["threshold_open"]
    assert r["sigma_endothermic"] == 0.0
    assert r["sigma_elastic"] == r["sigma_total"]


def test_v49_inelastic_above_threshold():
    """Above threshold, both elastic and endothermic contribute."""
    from t90_v49_inelastic_sidm import sigma_m_inelastic
    # delta=10 eV, m_chi=30 GeV -> v_min ~ 11 km/s
    # At v=100 (Galaxy), well above threshold
    r = sigma_m_inelastic(v_kms=100.0, m_phi_MeV=50.0, m_chi_GeV=30.0, g_chi=0.5, delta_eV=10.0)
    assert r["threshold_open"]
    assert r["sigma_endothermic"] > 0
    assert r["sigma_total"] > r["sigma_elastic"]


def test_v49_evaluate_point_returns_dict():
    """evaluate_inelastic_point returns sigma/m at all velocities."""
    from t90_v49_inelastic_sidm import evaluate_inelastic_point
    r = evaluate_inelastic_point(
        m_phi_MeV=50.0, m_chi_GeV=30.0, g_chi=0.5, delta_eV=100.0
    )
    assert "sigma_m_Cloud9" in r
    assert "sigma_m_Galaxy" in r
    assert "sigma_m_Bullet" in r
    assert "all_OK" in r
    assert "v_threshold_kms" in r


def test_v49_sigma_m_finite():
    """All sigma/m values from evaluate_inelastic_point are finite."""
    from t90_v49_inelastic_sidm import evaluate_inelastic_point
    for delta in [1.0, 100.0, 10000.0]:
        r = evaluate_inelastic_point(50.0, 30.0, 0.5, delta)
        assert np.isfinite(r["sigma_m_Cloud9"])
        assert np.isfinite(r["sigma_m_Galaxy"])
        assert np.isfinite(r["sigma_m_Bullet"])


def test_v49_high_delta_changes_threshold():
    """Higher delta shifts the velocity threshold higher."""
    from t90_v49_inelastic_sidm import evaluate_inelastic_point
    r_low = evaluate_inelastic_point(50.0, 30.0, 0.5, 10.0)
    r_high = evaluate_inelastic_point(50.0, 30.0, 0.5, 10000.0)
    assert r_high["v_threshold_kms"] > r_low["v_threshold_kms"]


def test_v49_no_cloud9_compatible_in_scan():
    """HONEST TEST: simple inelastic threshold model doesn't achieve Cloud-9 in any tested point.

    This documents the finding that the simple kinematic threshold (elastic
    below + endothermic above) doesn't produce enough sigma/m(28) at low v
    to satisfy Cloud-9's requirement of 30-500 cm^2/g.

    The Wang 2025 paper achieves the result through a DIFFERENT mechanism
    (pseudo-Dirac + leptophilic scalar + resonance), not the simple threshold
    model implemented here.
    """
    from t90_v49_inelastic_sidm import evaluate_inelastic_point
    n_compatible = 0
    for m_phi in [5, 10, 20, 50, 100, 200]:
        for g in [0.3, 0.5, 0.8, 1.0, 1.2]:
            for delta in [1, 10, 100, 1000, 10000, 100000]:
                r = evaluate_inelastic_point(m_phi, 30.0, g, delta)
                if r["all_OK"]:
                    n_compatible += 1
    # In our scan, no point satisfies all three constraints with the
    # simple threshold model
    assert n_compatible == 0