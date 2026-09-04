"""Tests for Euclid Q1 subhalo dN/dM FORECAST channel (T88.E, Channel 24).

**WARNING: FORECAST, not measurement.** Uses LensPop pipeline.
Real Euclid Q1 subhalo dN/dM measurement not yet available;
expected with DR1 at end of 2026.
"""

import math
import sys
from pathlib import Path

import pytest

PROJECT_CODE = str(Path(__file__).resolve().parent.parent / "code")
sys.path.insert(0, PROJECT_CODE)
sys.modules.pop("config", None)
sys.modules.pop("euclid_q1_subhalo_forecast_forward_model", None)
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
    from euclid_q1_subhalo_forecast_forward_model import EUCLID_Q1_SUBHALO_ARXIV_ID
    assert EUCLID_Q1_SUBHALO_ARXIV_ID == "2503.15330"


def test_pipeline_hardcoded():
    from euclid_q1_subhalo_forecast_forward_model import EUCLID_Q1_SUBHALO_PIPELINE
    assert "LensPop" in EUCLID_Q1_SUBHALO_PIPELINE


def test_dr1_eta_hardcoded():
    from euclid_q1_subhalo_forecast_forward_model import EUCLID_Q1_SUBHALO_DR1_ETA
    assert "2026" in EUCLID_Q1_SUBHALO_DR1_ETA


def test_config_constants():
    from config import (EUCLID_Q1_SUBHALO_VMAX_KMS,
                        EUCLID_Q1_SUBHALO_SIGMA_M_LOWER,
                        EUCLID_Q1_SUBHALO_SIGMA_M_UPPER,
                        EUCLID_Q1_SUBHALO_TAIL_WIDTH,
                        EUCLID_Q1_SUBHALO_FORECAST_LABEL)
    assert EUCLID_Q1_SUBHALO_VMAX_KMS == 150.0
    assert EUCLID_Q1_SUBHALO_SIGMA_M_LOWER == 0.05
    assert EUCLID_Q1_SUBHALO_SIGMA_M_UPPER == 0.10
    assert EUCLID_Q1_SUBHALO_TAIL_WIDTH == 0.30
    assert "FORECAST" in EUCLID_Q1_SUBHALO_FORECAST_LABEL


def test_forecast_label_warns():
    """Forecast label MUST contain 'FORECAST' warning."""
    from config import EUCLID_Q1_SUBHALO_FORECAST_LABEL
    assert "FORECAST" in EUCLID_Q1_SUBHALO_FORECAST_LABEL


# === Velocity scaling ===

def test_velocity_scaling_at_v07_map():
    """At v0.7 MAP (sigma_m_0=0.28, a=0.16), sigma/m(v=150) = 0.28 * (100/150)^0.16 ~ 0.262."""
    from euclid_q1_subhalo_forecast_forward_model import sigma_m_at_v_subhalo
    sm_v = sigma_m_at_v_subhalo(0.28, 0.16)
    expected = 0.28 * (100.0 / 150.0) ** 0.16  # ~ 0.262
    assert math.isclose(sm_v, expected, rel_tol=1e-9)


def test_velocity_scaling_a0():
    """At a=0, sigma/m(v=150) = sigma_m_0."""
    from euclid_q1_subhalo_forecast_forward_model import sigma_m_at_v_subhalo
    assert math.isclose(sigma_m_at_v_subhalo(0.05, 0.0), 0.05, rel_tol=1e-9)
    assert math.isclose(sigma_m_at_v_subhalo(0.10, 0.0), 0.10, rel_tol=1e-9)


def test_sigma_m_zero_or_negative_returns_zero():
    """At sigma_m_0<=0, returns 0."""
    from euclid_q1_subhalo_forecast_forward_model import sigma_m_at_v_subhalo
    assert sigma_m_at_v_subhalo(0.0, 0.5) == 0.0
    assert sigma_m_at_v_subhalo(-0.5, 0.5) == 0.0


# === Log-likelihood: in-band ===

def test_loglike_in_band_returns_zero():
    """At sigma/m(v=150) = 0.05 (lower edge), log L = 0."""
    from euclid_q1_subhalo_forecast_forward_model import loglike_euclid_q1_subhalo_forecast
    assert loglike_euclid_q1_subhalo_forecast(0.05, 0.0) == 0.0


def test_loglike_in_band_middle_returns_zero():
    """At sigma/m(v=150) = 0.075 (middle), log L = 0."""
    from euclid_q1_subhalo_forecast_forward_model import loglike_euclid_q1_subhalo_forecast
    assert loglike_euclid_q1_subhalo_forecast(0.075, 0.0) == 0.0


def test_loglike_in_band_upper_returns_zero():
    """At sigma/m(v=150) = 0.10 (upper edge), log L = 0."""
    from euclid_q1_subhalo_forecast_forward_model import loglike_euclid_q1_subhalo_forecast
    assert loglike_euclid_q1_subhalo_forecast(0.10, 0.0) == 0.0


# === Log-likelihood: below in-band ===

def test_loglike_below_lower_penalizes():
    """At sigma/m(v=150) = 0.01 (below lower), penalty fires."""
    from euclid_q1_subhalo_forecast_forward_model import loglike_euclid_q1_subhalo_forecast
    ll = loglike_euclid_q1_subhalo_forecast(0.01, 0.0)
    # log10(0.05/0.01) = 0.699; penalty = -0.5 * (0.699/0.30)^2 = -2.71
    assert ll < 0
    expected = -0.5 * (math.log10(0.05 / 0.01) / 0.30) ** 2
    assert math.isclose(ll, expected, rel_tol=1e-9)


def test_loglike_well_below_lower_large_penalty():
    """At sigma/m(v=150) = 0.001, large penalty (way too little evaporation)."""
    from euclid_q1_subhalo_forecast_forward_model import loglike_euclid_q1_subhalo_forecast
    ll = loglike_euclid_q1_subhalo_forecast(0.001, 0.0)
    # log10(0.05/0.001) = 1.699; penalty = -0.5 * (1.699/0.30)^2 = -16.04
    assert ll < -10


# === Log-likelihood: above in-band ===

def test_loglike_above_upper_penalizes():
    """At sigma/m(v=150) = 0.2 (above upper), penalty fires."""
    from euclid_q1_subhalo_forecast_forward_model import loglike_euclid_q1_subhalo_forecast
    ll = loglike_euclid_q1_subhalo_forecast(0.2, 0.0)
    # log10(0.2/0.10) = 0.301; penalty = -0.5 * (0.301/0.30)^2 = -0.503
    assert ll < 0
    expected = -0.5 * (math.log10(0.2 / 0.10) / 0.30) ** 2
    assert math.isclose(ll, expected, rel_tol=1e-9)


# === Hand-verified v0.7 MAP ===

def test_v07_map_penalty():
    """At v0.7 MAP, sigma/m(v=150) = 0.262 -> penalty ~ -0.97 (first non-silent T88 channel)."""
    from euclid_q1_subhalo_forecast_forward_model import (
        loglike_euclid_q1_subhalo_forecast,
        sigma_m_at_v_subhalo,
    )
    sm_v = sigma_m_at_v_subhalo(0.28, 0.16)
    assert math.isclose(sm_v, 0.2624, rel_tol=1e-3)
    ll = loglike_euclid_q1_subhalo_forecast(0.28, 0.16)
    # log10(0.262/0.10) = 0.419; penalty = -0.5 * (0.419/0.30)^2 = -0.975
    assert ll < -0.5  # Significant penalty (first non-silent!)
    assert math.isclose(ll, -0.975, rel_tol=1e-2)


# === Wrapper integration ===

def test_wrapper_in_band():
    """channels_extended wrapper: in-band returns 0."""
    from channels_extended import loglike_euclid_q1_subhalo_forecast as w
    assert w(0.075, 0.0) == 0.0


def test_wrapper_v07_penalty():
    """channels_extended wrapper: at v0.7 MAP, penalty fires."""
    from channels_extended import loglike_euclid_q1_subhalo_forecast as w
    ll = w(0.28, 0.16)
    assert ll < -0.5


def test_wrapper_include_in_fit_false():
    """Wrapper with include_in_fit=False returns 0."""
    from channels_extended import loglike_euclid_q1_subhalo_forecast as w
    assert w(0.28, 0.16, include_in_fit=False) == 0.0