"""Tests for T90.45 multi-portal joint fit driver.

Per T90.45 scope:
  - The 10D multi-portal fit driver imports cleanly
  - prior_transform maps unit cube to physical priors
  - loglike_joint_multi_portal returns finite log-likelihood at
    the reviewer Point 2 reference point
  - At the reference point, sigma/m_total(28) is in Cloud-9 range
"""

import numpy as np
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(Path(__file__).resolve().parent.parent / "code")))


def test_v45_module_imports():
    """The T90.45 multi-portal driver imports cleanly."""
    import t90_v45_multi_portal_joint_fit as mp  # noqa: F401
    assert hasattr(mp, "loglike_joint_multi_portal")
    assert hasattr(mp, "prior_transform")
    assert hasattr(mp, "PARAM_NAMES")


def test_v45_param_count():
    """The T90.45 driver uses 9 free parameters."""
    from t90_v45_multi_portal_joint_fit import PARAM_NAMES
    assert len(PARAM_NAMES) == 9


def test_v45_prior_transform():
    """prior_transform maps unit cube to physical priors."""
    from t90_v45_multi_portal_joint_fit import prior_transform, PARAM_NAMES
    u = np.ones(9) * 0.5
    theta = prior_transform(u)
    # At u=0.5, theta should be at midpoint of each prior range
    assert np.isfinite(theta).all()
    assert len(theta) == len(PARAM_NAMES)


def test_v45_reference_unified_loglike():
    """At the reviewer's Point 2 reference point, loglike is finite."""
    from t90_v45_multi_portal_joint_fit import loglike_joint_multi_portal
    # Portal A: heavy (700 MeV, 100 GeV, g=1.5)
    # Portal B: light (10 MeV, 500 GeV, g=0.22)
    theta = np.array([
        np.log10(700),    # log_m_phi_A_MeV
        np.log10(100),    # log_m_chi_A_GeV
        1.5,              # g_chi_A
        np.log10(10),     # log_m_phi_B_MeV
        np.log10(500),    # log_m_chi_B_GeV
        0.22,             # g_chi_B
        np.log10(1e-30),  # log_epsilon_A
        np.log10(1e-15),  # log_alpha_A
        0.0,              # log_xi (=1)
    ])
    ll = loglike_joint_multi_portal(theta)
    assert np.isfinite(ll), f"non-finite loglike at reference: {ll}"


def test_v45_zero_coupling_returns_neg_inf():
    """At zero coupling, channels return -inf or very negative loglike."""
    from t90_v45_multi_portal_joint_fit import loglike_joint_multi_portal
    theta = np.array([
        np.log10(700),
        np.log10(100),
        0.0,   # g_chi_A = 0
        np.log10(10),
        np.log10(500),
        0.22,
        np.log10(1e-30),
        np.log10(1e-15),
        0.0,
    ])
    ll = loglike_joint_multi_portal(theta)
    # Should be -inf or very negative (channels reject g=0)
    assert ll < -10 or not np.isfinite(ll)


def test_v45_dm_mass_zero_returns_neg_inf():
    """At zero DM mass, prior returns -inf."""
    from t90_v45_multi_portal_joint_fit import loglike_joint_multi_portal
    theta = np.array([
        np.log10(700),
        -np.inf,  # m_chi_A = 0
        1.5,
        np.log10(10),
        np.log10(500),
        0.22,
        np.log10(1e-30),
        np.log10(1e-15),
        0.0,
    ])
    ll = loglike_joint_multi_portal(theta)
    assert not np.isfinite(ll)


def test_v45_reference_sigma_m_in_cloud9_range():
    """At the reference point, combined sigma/m(28) is in Cloud-9 range."""
    from t90_v45_multi_portal_joint_fit import loglike_joint_multi_portal
    from t90_v44_multi_portal import sigma_m_multi_portal
    sm_28 = sigma_m_multi_portal(28.0, 700, 100, 1.5, 10, 500, 0.22)
    # Cloud-9 range is 30-500 cm^2/g
    assert 30 < sm_28 < 500, f"sm(28)={sm_28:.2f} not in Cloud-9 range"