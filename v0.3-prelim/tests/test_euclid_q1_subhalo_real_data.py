"""
Tests for euclid_q1_subhalo_real_data.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))


def test_sigma_m_at_v_cluster_scaling():
    """sigma/m at v=750 km/s scales with velocity power-law a."""
    from euclid_q1_subhalo_real_data import sigma_m_at_v_cluster
    r1 = sigma_m_at_v_cluster(1.0, 0.0)
    r2 = sigma_m_at_v_cluster(1.0, 0.0, v_cluster_kms=750.0)
    # a=0: sigma/m should be sigma_m_0 (constant)
    assert abs(r1 - 1.0) < 1e-6
    assert abs(r2 - 1.0) < 1e-6


def test_sigma_m_velocity_power_law():
    """For a=1, sigma/m(v=750) = sigma_m_0 * (100/750)^1 = sigma_m_0 / 7.5."""
    from euclid_q1_subhalo_real_data import sigma_m_at_v_cluster, V_REF
    expected = 1.0 * (V_REF / 750.0) ** 1.0  # = 0.1333
    actual = sigma_m_at_v_cluster(1.0, 1.0)
    assert abs(actual - expected) / expected < 1e-6


def test_sidm_suppression_zero_at_low_sigma_m():
    """For sigma/m ~ 0, suppression should be ~0% (no SIDM effect)."""
    from euclid_q1_subhalo_real_data import sidm_suppression_factor
    s = sidm_suppression_factor(1e-10, 0.5)
    assert s < 0.05  # ~2% baseline


def test_sidm_suppression_grows_with_sigma_m():
    """For larger sigma/m, suppression should be larger."""
    from euclid_q1_subhalo_real_data import sidm_suppression_factor
    # Use sigma_m_0 values that all fall in [0.05, 1.0] cm^2/g at v=750
    # with a=0 (no velocity scaling).
    s_low = sidm_suppression_factor(0.06, 0.0)    # just above 0.05
    s_mid = sidm_suppression_factor(0.3, 0.0)     # mid range
    s_high = sidm_suppression_factor(0.8, 0.0)    # upper range
    assert s_low < s_mid < s_high


def test_cdm_predicted_count_matches_data():
    """CDM (sigma_m_0 = 0) predicts 14 grade-A clusters, matching observation."""
    from euclid_q1_subhalo_real_data import predicted_cluster_count_cdm
    assert predicted_cluster_count_cdm() == 14.0


def test_sidm_predicted_count_less_than_cdm():
    """SIDM predicts fewer clusters than CDM (suppression)."""
    from euclid_q1_subhalo_real_data import (
        predicted_cluster_count_cdm,
        predicted_cluster_count_sidm,
    )
    n_cdm = predicted_cluster_count_cdm()
    n_sidm = predicted_cluster_count_sidm(0.7, 0.16)  # LZ-anchored
    assert n_sidm < n_cdm


def test_loglike_cdm_higher_than_sidm_lz():
    """CDM should have higher log L than SIDM_LZ (data favors CDM-like counts)."""
    from euclid_q1_subhalo_real_data import loglike_euclid_q1_count
    ll_cdm = loglike_euclid_q1_count(0.0, 0.5)
    ll_sidm = loglike_euclid_q1_count(0.7, 0.16)
    assert ll_cdm > ll_sidm


def test_loglike_finite_for_LZ_params():
    """Log likelihood should be finite at LZ-anchored parameters."""
    from euclid_q1_subhalo_real_data import loglike_euclid_q1_count
    ll = loglike_euclid_q1_count(0.7, 0.16)
    assert np.isfinite(ll)


def test_delta_log_l_at_LZ_is_small():
    """Delta log L at LZ-anchored parameters should be small (no strong tension).

    Per the T88.E2 main analysis: 14 clusters gives Poisson noise large
    enough that even 10% suppression is not detectable. Expect |delta_log_l <| < 1.
    """
    from euclid_q1_subhalo_real_data import loglike_euclid_q1_count
    ll_cdm = loglike_euclid_q1_count(0.0, 0.5)
    ll_sidm = loglike_euclid_q1_count(0.7, 0.16)
    delta = ll_sidm - ll_cdm
    assert abs(delta) < 1.0, (
        f"Delta log L = {delta:.3f}, expected |delta| < 1 (no strong tension)"
    )


def test_real_data_constants_match_paper():
    """Verify the real-data constants match arXiv:2503.15330."""
    from euclid_q1_subhalo_real_data import (
        EUCLID_Q1_TOTAL_AREA_DEG2,
        EUCLID_Q1_GRADE_A_CLUSTERS,
        EUCLID_Q1_DENSITY_PER_DEG2,
    )
    assert EUCLID_Q1_TOTAL_AREA_DEG2 == 63.1
    assert EUCLID_Q1_GRADE_A_CLUSTERS == 14
    assert abs(EUCLID_Q1_DENSITY_PER_DEG2 - 0.3) < 1e-6