"""Tests for Euclid Q1 strong-lensing cluster catalog (T88.C, Channel 23).

Source: Bergamini et al. 2026 (Euclid Q1 - XXXIII), A&A 711 A33,
arXiv:2503.15330, DOI 10.1051/0004-6361/202554577.
"""

import math
import sys
from pathlib import Path

import pytest

PROJECT_CODE = str(Path(__file__).resolve().parent.parent / "code")
sys.path.insert(0, PROJECT_CODE)
sys.modules.pop("config", None)
sys.modules.pop("euclid_q1_lensing_forward_model", None)
sys.modules.pop("channels_extended", None)


@pytest.fixture(autouse=True)
def clear_module_cache():
    for mod in list(sys.modules):
        if mod.startswith((
            "config",
            "euclid_q1",
            "channels_extended",
        )):
            sys.modules.pop(mod, None)


# === Constants ===

def test_arxiv_id_hardcoded():
    from euclid_q1_lensing_forward_model import EUCLID_Q1_LENSING_ARXIV_ID
    assert EUCLID_Q1_LENSING_ARXIV_ID == "2503.15330"


def test_doi_hardcoded():
    from euclid_q1_lensing_forward_model import EUCLID_Q1_LENSING_DOI
    assert EUCLID_Q1_LENSING_DOI == "10.1051/0004-6361/202554577"


def test_journal_hardcoded():
    from euclid_q1_lensing_forward_model import EUCLID_Q1_LENSING_JOURNAL
    assert "A&A" in EUCLID_Q1_LENSING_JOURNAL
    assert "711" in EUCLID_Q1_LENSING_JOURNAL


def test_config_constants():
    from config import (EUCLID_Q1_VMAX_KMS, EUCLID_Q1_N_GRADE_A_CLUSTERS,
                        EUCLID_Q1_SIGMA_M_UPPER_LIMIT, EUCLID_Q1_TAIL_WIDTH)
    assert EUCLID_Q1_VMAX_KMS == 1000.0
    assert EUCLID_Q1_N_GRADE_A_CLUSTERS == 14  # 14 grade-A clusters (P_lens=1)
    assert EUCLID_Q1_SIGMA_M_UPPER_LIMIT == 0.5
    assert EUCLID_Q1_TAIL_WIDTH == 0.30


# === Velocity scaling ===

def test_sigma_m_at_v0_7_map():
    """At v0.7 MAP (sigma_m_0=0.28, a=0.16), sigma/m(v=1000) = 0.28 * 10^(-0.16) ~ 0.194."""
    from euclid_q1_lensing_forward_model import sigma_m_at_v_euclid_q1
    sm_v = sigma_m_at_v_euclid_q1(0.28, 0.16)
    expected = 0.28 * (100.0 / 1000.0) ** 0.16  # ~ 0.194
    assert math.isclose(sm_v, expected, rel_tol=1e-9)


def test_velocity_scaling_a0():
    """At a=0, sigma/m(v=1000) = sigma_m_0 (no velocity dependence)."""
    from euclid_q1_lensing_forward_model import sigma_m_at_v_euclid_q1
    assert math.isclose(sigma_m_at_v_euclid_q1(0.5, 0.0), 0.5, rel_tol=1e-9)
    assert math.isclose(sigma_m_at_v_euclid_q1(1.0, 0.0), 1.0, rel_tol=1e-9)


def test_velocity_scaling_a_positive_decreases():
    """At a>0, sigma/m decreases with v (sigma/m(v=1000) < sigma_m_0)."""
    from euclid_q1_lensing_forward_model import sigma_m_at_v_euclid_q1
    sm_at_v = sigma_m_at_v_euclid_q1(1.0, 0.5)
    assert sm_at_v < 1.0  # Below sigma_m_0


def test_velocity_scaling_a_negative_increases():
    """At a<0, sigma/m grows with v (sigma/m(v=1000) > sigma_m_0)."""
    from euclid_q1_lensing_forward_model import sigma_m_at_v_euclid_q1
    sm_at_v = sigma_m_at_v_euclid_q1(1.0, -0.5)
    assert sm_at_v > 1.0  # Above sigma_m_0


def test_sigma_m_zero_returns_zero():
    """At sigma_m_0=0, returns 0 (degenerate input)."""
    from euclid_q1_lensing_forward_model import sigma_m_at_v_euclid_q1
    assert sigma_m_at_v_euclid_q1(0.0, 0.5) == 0.0


def test_sigma_m_negative_returns_zero():
    """At sigma_m_0<0, returns 0 (defensive against negative cross-section)."""
    from euclid_q1_lensing_forward_model import sigma_m_at_v_euclid_q1
    assert sigma_m_at_v_euclid_q1(-0.5, 0.5) == 0.0


# === Log-likelihood ===

def test_loglike_below_threshold_is_zero():
    """At sigma/m(v=1000) < 0.5, log L = 0 (CDM-like, silent)."""
    from euclid_q1_lensing_forward_model import loglike_euclid_q1_lensing
    # v0.7 MAP: sigma/m(v=1000) ~ 0.194, below 0.5
    assert loglike_euclid_q1_lensing(0.28, 0.16) == 0.0


def test_loglike_at_threshold_is_zero():
    """At sigma/m(v=1000) = 0.5 (exact threshold), log L = 0."""
    from euclid_q1_lensing_forward_model import loglike_euclid_q1_lensing
    assert loglike_euclid_q1_lensing(0.5, 0.0) == 0.0


def test_loglike_above_threshold_penalizes():
    """At sigma/m(v=1000) > 0.5, soft Gaussian penalty fires."""
    from euclid_q1_lensing_forward_model import loglike_euclid_q1_lensing
    # sigma_m_0=2.0, a=0 -> sigma/m(v=1000) = 2.0, log10(2/0.5) = 0.602
    # Penalty = -0.5 * (0.602/0.30)^2 = -0.5 * 4.027 = -2.014
    ll = loglike_euclid_q1_lensing(2.0, 0.0)
    expected = -0.5 * (math.log10(2.0 / 0.5) / 0.30) ** 2
    assert math.isclose(ll, expected, rel_tol=1e-9)
    assert ll < 0  # Penalty is non-positive


def test_loglike_well_above_threshold_is_large_negative():
    """At sigma/m(v=1000) = 10.0, large penalty."""
    from euclid_q1_lensing_forward_model import loglike_euclid_q1_lensing
    ll = loglike_euclid_q1_lensing(10.0, 0.0)
    # log10(10/0.5) = log10(20) = 1.301
    # Penalty = -0.5 * (1.301/0.30)^2 = -0.5 * 18.79 = -9.40
    assert ll < -5.0


# === Wrapper integration ===

def test_wrapper_returns_zero_below_threshold():
    """channels_extended wrapper: below threshold returns 0."""
    from channels_extended import loglike_euclid_q1_lensing as w
    assert w(0.28, 0.16) == 0.0


def test_wrapper_penalizes_above_threshold():
    """channels_extended wrapper: above threshold returns negative."""
    from channels_extended import loglike_euclid_q1_lensing as w
    ll = w(2.0, 0.0)
    assert ll < 0


def test_wrapper_include_in_fit_false():
    """Wrapper with include_in_fit=False returns 0."""
    from channels_extended import loglike_euclid_q1_lensing as w
    assert w(2.0, 0.0, include_in_fit=False) == 0.0


# === Hand-verified v0.7 MAP ===

def test_hand_verified_v07_map():
    """At v0.7 MAP, channel returns 0 (silent cross-check)."""
    from euclid_q1_lensing_forward_model import (
        loglike_euclid_q1_lensing,
        sigma_m_at_v_euclid_q1,
    )
    sigma_m_0 = 0.28  # v0.7 MAP
    a = 0.16         # v0.7 MAP
    sm_v = sigma_m_at_v_euclid_q1(sigma_m_0, a)
    # Manual: 0.28 * (0.1)^0.16 = 0.28 * 0.6918 = 0.1937
    assert math.isclose(sm_v, 0.1937, rel_tol=1e-3)
    # Below threshold
    assert loglike_euclid_q1_lensing(sigma_m_0, a) == 0.0