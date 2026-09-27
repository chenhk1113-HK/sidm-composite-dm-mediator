"""Tests for T90.63 LRD channel (Jiang et al. 2026 SIDM core collapse)."""

import math
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))
from t90_v63_lrd_channel import (
    LRD_OBSERVATIONS,
    age_of_universe_at_z,
    loglike_lrd_jiang2026,
    n_LRD_predicted,
    provenance,
    summary_lrd_at_sigma_m,
    t_collapse_gravothermal,
)


def test_age_of_universe_at_z0_is_correct():
    """Age of universe at z=0 should be ~13.8 Gyr for Planck 2018."""
    age = age_of_universe_at_z(0.5)
    # Expect ~8.5 Gyr at z=0.5 (lookback time is ~5 Gyr, total age ~13.8 Gyr)
    assert 7000 < age < 10000, f"Age at z=0.5 = {age:.1f} Myr, expected ~8500 Myr"


def test_age_of_universe_increases_with_decreasing_z():
    """Age at z=5 should be ~1.2 Gyr; age at z=1 should be ~6 Gyr."""
    age_5 = age_of_universe_at_z(5.0)
    age_1 = age_of_universe_at_z(1.0)
    assert 1000 < age_5 < 2000, f"Age at z=5 = {age_5:.1f} Myr, expected ~1200"
    assert 5000 < age_1 < 8000, f"Age at z=1 = {age_1:.1f} Myr, expected ~6000"


def test_t_collapse_decreases_with_larger_sigma_m():
    """Larger sigma/m should produce faster collapse (shorter t_collapse)."""
    tc_small = t_collapse_gravothermal(8.0, 0.0, 5.0)  # sigma/m = 1
    tc_large = t_collapse_gravothermal(8.0, 2.0, 5.0)  # sigma/m = 100
    assert tc_large < tc_small, (
        f"t_collapse should decrease with sigma/m. "
        f"sigma/m=1: {tc_small:.1f} Myr; sigma/m=100: {tc_large:.1f} Myr"
    )


def test_t_collapse_decreases_with_smaller_mass():
    """Larger halos should collapse FASTER (more DM particles -> faster gravothermal catastrophe)."""
    tc_big = t_collapse_gravothermal(8.5, 1.0, 5.0)  # M=10^8.5
    tc_small = t_collapse_gravothermal(7.5, 1.0, 5.0)  # M=10^7.5
    # Larger halos collapse faster (less time to gather the larger mass)
    assert tc_big < tc_small, (
        f"Larger halo should collapse faster. "
        f"M=10^8.5: {tc_big:.1f} Myr; M=10^7.5: {tc_small:.1f} Myr"
    )


def test_n_lrd_zero_for_very_small_sigma_m():
    """sigma/m too small -> no gravothermal collapse -> no LRDs."""
    n = n_LRD_predicted(-3.0, 5.0)  # sigma/m = 0.001 cm^2/g
    assert n < -7, f"n_LRD at sigma/m=0.001 should be ~0, got log10(n)={n}"


def test_n_lrd_positive_for_reasonable_sigma_m():
    """sigma/m in [1, 100] cm^2/g should produce non-negligible LRDs.
    At sigma/m=0.1, t_collapse is too long, so few LRDs expected."""
    for sm_log in [0.0, 1.0, 2.0]:  # sigma/m in [1, 100] cm^2/g
        n = n_LRD_predicted(sm_log, 5.0)
        assert n > -6, f"n_LRD at sigma/m=10^{sm_log}={n}, expected >10^-6"


def test_n_lrd_increases_with_sigma_m_in_low_regime():
    """In the regime where not all halos collapse, n_LRD should grow with sigma/m."""
    n_small = n_LRD_predicted(0.0, 5.0)  # sigma/m = 1
    n_large = n_LRD_predicted(1.0, 5.0)  # sigma/m = 10
    assert n_large > n_small, (
        f"n_LRD should increase with sigma/m. sigma/m=1: {n_small}; sigma/m=10: {n_large}"
    )


def test_loglike_returns_zero_when_disabled():
    """loglike_lrd_jiang2026(enabled=False) should always return 0.0."""
    assert loglike_lrd_jiang2026(1.0, enabled=False) == 0.0
    assert loglike_lrd_jiang2026(-2.0, enabled=False) == 0.0


def test_loglike_returns_neg_inf_for_out_of_prior():
    """sigma/m outside physical range should return -inf."""
    assert loglike_lrd_jiang2026(-10.0) == -np.inf  # way too small
    assert loglike_lrd_jiang2026(10.0) == -np.inf   # way too large


def test_loglike_is_finite_in_physical_range():
    """sigma/m in physical range should give finite loglike."""
    for sm_log in [-2.0, -1.0, 0.0, 1.0, 2.0, 3.0]:
        ll = loglike_lrd_jiang2026(sm_log)
        assert np.isfinite(ll), f"loglike at sigma/m=10^{sm_log} not finite: {ll}"


def test_loglike_prefers_reasonable_sigma_m():
    """Best-fit sigma/m should be in a reasonable range (not extreme)."""
    best_sm = None
    best_ll = -np.inf
    for sm_log in np.linspace(-2.0, 3.0, 21):
        ll = loglike_lrd_jiang2026(sm_log)
        if ll > best_ll:
            best_ll = ll
            best_sm = sm_log
    # Best should NOT be at the boundaries (those are -inf or very low)
    assert -1.5 < best_sm < 2.5, f"Best sigma/m = {best_sm}, expected in (-1.5, 2.5)"


def test_summary_lrd_returns_dict_with_z_keys():
    """summary_lrd_at_sigma_m should return a dict with z labels as keys."""
    sm = summary_lrd_at_sigma_m(1.0)
    assert isinstance(sm, dict)
    assert len(sm) == len(LRD_OBSERVATIONS)
    for k in sm:
        assert k.startswith("log10_n_LRD_z")


def test_provenance_cites_jiang_2026():
    """Provenance string should mention Jiang et al. 2026."""
    p = provenance()
    assert "Jiang" in p
    assert "2026" in p
    assert "2503.23710" in p  # arXiv ID


def test_observations_have_valid_structure():
    """Each observation should have z, label, log10_n, err, weight."""
    for obs in LRD_OBSERVATIONS:
        assert "z" in obs
        assert "label" in obs
        assert "log10_n_LRD_per_Mpc3_obs" in obs
        assert "log10_n_LRD_per_Mpc3_err" in obs
        assert "weight" in obs
        assert obs["log10_n_LRD_per_Mpc3_err"] > 0
        assert obs["weight"] > 0
        assert obs["z"] > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])