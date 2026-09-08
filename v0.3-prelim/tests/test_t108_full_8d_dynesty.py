"""
Tests for t108_full_8d_dynesty.

T108 is the FULL 8D dynesty nested sampling run (not B1-lite emcee):
  - 6 v0.7 parameters + (log_delta_keV, log_sigma_PortalB)
  - LZ Table S8 + DIAMX combined likelihood
  - Produces log Z and full posterior
"""
from __future__ import annotations

import json
from pathlib import Path
import pytest

_T108_PATH = (Path(__file__).resolve().parents[1] / "outputs" / "t95" /
              "t108_full_8d_dynesty.json")


def _skip_if_no_t108():
    if not _T108_PATH.exists():
        pytest.skip("No T108 results; run t108_full_8d_dynesty.py")


def test_t108_outputs_present():
    _skip_if_no_t108()
    out = json.load(open(_T108_PATH))
    assert out["test"] == "T108_full_8d_dynesty"
    assert "MAP_8d" in out
    assert "log_Z" in out
    assert "T90_criterion_5_satisfied" in out


def test_t108_8d_log_Z_is_finite():
    """8D log Z should be a finite float."""
    _skip_if_no_t108()
    out = json.load(open(_T108_PATH))
    log_Z = out["log_Z"]
    import math
    assert math.isfinite(log_Z)


def test_t108_delta_log_Z_calculated():
    """Δlog Z (8D - 6D) should be reported."""
    _skip_if_no_t108()
    out = json.load(open(_T108_PATH))
    assert "delta_log_Z_8d_vs_6d" in out
    assert "v07_log_Z_6d" in out


def test_t108_MAP_8d_has_8_parameters():
    """8D MAP should have 8 parameter values."""
    _skip_if_no_t108()
    out = json.load(open(_T108_PATH))
    assert len(out["MAP_8d"]) == 8


def test_t108_MAP_in_physical_ranges():
    """8D MAP should be in physical ranges for all 8 parameters."""
    _skip_if_no_t108()
    out = json.load(open(_T108_PATH))
    m = out["MAP_8d_physical"]
    assert 10.0 <= m["m_phi_MeV_MAP"] <= 10000.0
    assert 3.0 <= m["m_chi_GeV_MAP"] <= 1000.0
    assert 0.01 <= m["g_chi_MAP"] <= 2.0
    assert 1e-60 <= m["epsilon_MAP"] <= 1.0
    assert 1e-30 <= m["alpha_MAP"] <= 1.0
    assert 0.1 <= m["xi_MAP"] <= 5.0
    assert 1.0 <= m["delta_keV_MAP"] <= 1000.0
    assert 1e-48 <= m["sigma_PortalB_cm2_MAP"] <= 1e-39


def test_t108_m_chi_consistent_with_diamx_or_t103():
    """m_chi MAP should be closer to DIAMX (60 GeV) or to v0.7 (498 GeV), not in between wildly."""
    _skip_if_no_t108()
    out = json.load(open(_T108_PATH))
    import math
    m_chi = out["MAP_8d_physical"]["m_chi_GeV_MAP"]
    log_d_diamx = abs(math.log10(m_chi) - math.log10(60.0))
    log_d_v07 = abs(math.log10(m_chi) - math.log10(498.0))
    # Should be within 2 OOM of either
    assert min(log_d_diamx, log_d_v07) < 2.0


def test_t108_module_importable():
    """Module imports without error."""
    import warnings
    warnings.filterwarnings("ignore")
    import t108_full_8d_dynesty  # noqa: F401


def test_t108_loglike_8d_function_works():
    """Spot-check the loglike_8d function at v0.7 MAP + reasonable δ, σ."""
    import sys
    import warnings
    warnings.filterwarnings("ignore")
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))
    from t108_full_8d_dynesty import loglike_8d
    # At v0.7 MAP with reasonable δ, σ
    p = [
        2.770,  # log_m_phi (588 MeV)
        2.697,  # log_m_chi (498 GeV)
        1.576,  # g_chi
        -36.84, # log_epsilon
        -15.46, # log_alpha
        -0.798, # log_xi
        2.18,   # log delta (150 keV)
        -42.0,  # log sigma (1e-42)
    ]
    ll = loglike_8d(p)
    import math
    assert math.isfinite(ll)


def test_t108_prior_transform_8d():
    """prior_transform_8d should map u in [0,1]^8 to a valid 8D theta."""
    import sys
    import warnings
    warnings.filterwarnings("ignore")
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))
    from t108_full_8d_dynesty import prior_transform_8d
    import numpy as np
    u = np.array([0.5] * 8)
    theta = prior_transform_8d(u)
    assert len(theta) == 8
    # All values should be finite
    assert all(np.isfinite(t) for t in theta)
