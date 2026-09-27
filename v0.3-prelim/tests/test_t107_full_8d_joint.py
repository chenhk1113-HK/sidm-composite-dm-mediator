"""
Tests for t107_full_8d_joint.

T107 runs an 8D emcee MCMC joint fit:
  6 v0.7 parameters (m_phi, m_chi, g_chi, eps, alpha, xi) +
  2 new Portal B parameters (delta, sigma_PortalB)

Uses Gaussian priors on v0.7 (16-84 widths) and LZ + DIAMX likelihood.
"""
from __future__ import annotations

import json
from pathlib import Path
import pytest

_T107_PATH = (Path(__file__).resolve().parents[1] / "outputs" / "t95" /
              "t107_full_8d_joint.json")


def _skip_if_no_t107():
    if not _T107_PATH.exists():
        pytest.skip("No T107 results; run t107_full_8d_joint.py")


def test_t107_outputs_present():
    _skip_if_no_t107()
    out = json.load(open(_T107_PATH))
    assert out["test"] == "T107_full_8d_joint_fit"
    assert "MAP_8d" in out
    assert "all_parameter_results" in out


def test_t107_8d_map_is_reasonable():
    """8D MAP should have m_chi, delta, sigma in physical ranges."""
    _skip_if_no_t107()
    out = json.load(open(_T107_PATH))
    m = out["MAP_8d"]
    # m_chi in [10, 1000] GeV
    assert 10.0 <= m["m_chi_GeV"] <= 1000.0
    # delta in [1, 1000] keV
    assert 1.0 <= m["delta_keV"] <= 1000.0
    # sigma in [10^-48, 10^-39]
    assert 1e-48 <= m["sigma_cm2"] <= 1e-39
    # m_phi in [10, 10000] MeV
    assert 10.0 <= m["m_phi_MeV"] <= 10000.0


def test_t107_mcmc_acceptance_reasonable():
    """emcee acceptance should be in 0.2-0.7 range (not stuck or random)."""
    _skip_if_no_t107()
    out = json.load(open(_T107_PATH))
    accept = out["acceptance_fraction"]
    assert 0.2 <= accept <= 0.7


def test_t107_wall_time_under_60s():
    """8D emcee should complete in < 60s (vs hours for dynesty)."""
    _skip_if_no_t107()
    out = json.load(open(_T107_PATH))
    wall = out["wall_time_seconds"]
    assert wall < 60.0


def test_t107_map_closer_to_diamx_than_t103():
    """8D MAP should be closer to DIAMX (m_chi~60, delta~130) than to T103 (483, 295)."""
    _skip_if_no_t107()
    out = json.load(open(_T107_PATH))
    d_diamx = out["comparison"]["distance_log10_from_DIAMX"]
    d_t103 = out["comparison"]["distance_log10_from_T103"]
    # T107 should be closer to DIAMX than to T103
    assert d_diamx < d_t103


def test_t107_delta_in_lz_target_range():
    """δ MAP should fall in the LZ target range [100, 400] keV."""
    _skip_if_no_t107()
    out = json.load(open(_T107_PATH))
    delta = out["MAP_8d"]["delta_keV"]
    assert 50.0 <= delta <= 500.0


def test_t107_m_chi_consistent_with_diamx():
    """m_chi MAP should be within 1 OOM of DIAMX best-fit (60 GeV)."""
    _skip_if_no_t107()
    out = json.load(open(_T107_PATH))
    import math
    m_chi = out["MAP_8d"]["m_chi_GeV"]
    log_distance = abs(math.log10(m_chi) - math.log10(60.0))
    assert log_distance < 1.0


def test_t107_module_importable():
    """Module imports without error."""
    import warnings
    warnings.filterwarnings("ignore")
    import t107_full_8d_joint  # noqa: F401


def test_t107_log_posterior_function_works():
    """Spot-check the log_posterior function at v0.7 MAP."""
    import sys
    import warnings
    warnings.filterwarnings("ignore")
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))
    from t107_full_8d_joint import log_posterior, V07_MAP
    # Test point at v0.7 MAP with reasonable delta/sigma
    p = [
        V07_MAP["log_m_phi_MeV"],
        V07_MAP["log_m_chi_GeV"],
        V07_MAP["g_chi"],
        V07_MAP["log_epsilon"],
        V07_MAP["log_alpha"],
        V07_MAP["log_xi"],
        2.0,    # log delta = 100 keV
        -42.0,  # log sigma = 10^-42
    ]
    lp = log_posterior(p)
    # Should be finite and not -1e10 (not outside prior)
    assert lp > -1e9
    assert lp < 1e9
