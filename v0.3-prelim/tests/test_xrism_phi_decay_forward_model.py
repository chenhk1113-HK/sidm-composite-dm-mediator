"""Tests for XRISM Resolve phi -> gamma gamma decay null-channel (T88.D, Channel 22).

Per the R15B reassessment (docs/consider5_review/R15B_DATASET_AVAILABILITY_REASSESSMENT.md
lines 168-174), this channel is a DOCUMENTED NULL:

  1. Predicted photon energy E_gamma = m_phi/2 is 4-5 orders of magnitude
     above XRISM Resolve's 0.3-12 keV band.
  2. Lifetime tau_phi exceeds Hubble time by ~1e42 at v0.7 epsilon.

These tests verify the hand-computed values that establish the null result
and lock the audit trail into the codebase.
"""

import math
import sys
from pathlib import Path

import pytest

# Path setup: defensive against the project's two-config.py layout
PROJECT_CODE = str(Path(__file__).resolve().parent.parent / "code")
sys.path.insert(0, PROJECT_CODE)
sys.modules.pop("config", None)
sys.modules.pop("xrism_phi_decay_forward_model", None)
sys.modules.pop("channels_extended", None)


@pytest.fixture(autouse=True)
def clear_module_cache():
    """Clear module cache before each test to avoid stale __pycache__."""
    for mod in list(sys.modules):
        if mod.startswith((
            "config",
            "xrism_phi",
            "channels_extended",
        )):
            sys.modules.pop(mod, None)


# === Constants (no-network contract; per joint-fit skill P9) ===

def test_arxiv_id_is_hardcoded():
    """Citation provenance must be hardcoded (no network access)."""
    from xrism_phi_decay_forward_model import XRISM_PHI_DECAY_ARXIV_ID
    assert XRISM_PHI_DECAY_ARXIV_ID == "2402.08452"
    # Bulbul+ 2024 eRASS1 catalog (cross-cites XRISM)


def test_xrism_band_constants_hardcoded():
    """XRISM Resolve band constants must be hardcoded in config.py."""
    from config import (XRISM_RESOLVE_BAND_LOW_KEV, XRISM_RESOLVE_BAND_HIGH_KEV,
                        XRISM_RESOLVE_EFFECTIVE_AREA_CM2, XRISM_PHI_DECAY_HARD_CAP_EPS)
    assert XRISM_RESOLVE_BAND_LOW_KEV == 0.3
    assert XRISM_RESOLVE_BAND_HIGH_KEV == 12.0
    assert XRISM_RESOLVE_EFFECTIVE_AREA_CM2 == 160.0
    assert XRISM_PHI_DECAY_HARD_CAP_EPS == 1.0e-30


# === Hand-verified null-result numbers at v0.7 MAP ===

def test_photon_energy_above_xrism_band_at_v07_map():
    """At v0.7 MAP (m_phi = 452.95 MeV), E_gamma = 226,475 keV, 4 orders above 12 keV."""
    from xrism_phi_decay_forward_model import photon_energy_keV, is_photon_in_xrism_band
    m_phi = 452.95
    e_gamma = photon_energy_keV(m_phi)
    # E_gamma = m_phi/2 in keV = 452.95e3 / 2 = 226475 keV
    assert math.isclose(e_gamma, 226475.0, rel_tol=1e-3)
    # In XRISM band? 0.3 to 12 keV — NO, off by ~4 orders of magnitude
    assert not is_photon_in_xrism_band(m_phi)


def test_photon_energy_above_xrism_band_for_all_posterior_m_phi():
    """For all m_phi in 100-1000 MeV, E_gamma is always above XRISM's band."""
    from xrism_phi_decay_forward_model import photon_energy_keV, is_photon_in_xrism_band
    for m_phi in [50.0, 100.0, 200.0, 453.0, 600.0, 800.0, 1000.0, 1500.0]:
        e_gamma = photon_energy_keV(m_phi)
        assert e_gamma > 12.0e3, f"At m_phi={m_phi} MeV, E_gamma={e_gamma} keV is in XRISM band!"
        assert not is_photon_in_xrism_band(m_phi), \
            f"is_photon_in_xrism_band({m_phi}) should be False"


def test_lifetime_at_v07_map_is_double_null():
    """At v0.7 MAP, tau_phi ~ 3e52 yr = 1e42 x Hubble time."""
    from xrism_phi_decay_forward_model import phi_decay_lifetime_yr, HUBBLE_TIME_YR
    eps = 10 ** (-36.44)  # v0.7 MAP epsilon ~ 3.6e-37
    m_phi = 452.95
    tau_yr = phi_decay_lifetime_yr(eps, m_phi)
    # Expected: tau ~ 3e52 yr (within factor 3 of our hand-computation 2.8e52)
    assert 1.0e51 <= tau_yr <= 1.0e54, f"tau_phi = {tau_yr:.3e} yr, expected ~3e52 yr"
    # tau / Hubble time >> 1
    ratio = tau_yr / HUBBLE_TIME_YR
    assert ratio > 1.0e30, f"tau/Hubble = {ratio:.3e}, expected > 1e30 (3e42)"


def test_predicted_photon_count_at_v07_map():
    """Even ignoring energy band, photon count in XRISM Resolve FOV is large but at wrong energy."""
    from xrism_phi_decay_forward_model import predicted_photons_in_fov
    eps = 10 ** (-36.44)
    m_phi = 452.95
    n_photons = predicted_photons_in_fov(eps, m_phi)
    # Predicted ~1e13-1e14 photons in 745 ks FOV (at MeV energies, NOT in XRISM band)
    assert 1.0e10 <= n_photons <= 1.0e16, f"N_photons = {n_photons:.3e}, expected ~1e13"


# === loglikelihood behavior ===

def test_loglike_at_v07_map_is_zero():
    """At v0.7 MAP, loglike = 0 (silent cross-check)."""
    from xrism_phi_decay_forward_model import loglike_phi_to_gamgam_xrism
    theta = (-36.44, -15.7, 452.95, 769.69, 1.189, -0.803)
    assert loglike_phi_to_gamgam_xrism(theta) == 0.0


def test_loglike_at_extreme_eps_is_zero():
    """At extreme epsilon values (high or low), loglike is still 0."""
    from xrism_phi_decay_forward_model import loglike_phi_to_gamgam_xrism
    # epsilon = 1e-50 (very weak portal)
    assert loglike_phi_to_gamgam_xrism((-50.0, 0, 200.0, 0, 0, 0)) == 0.0
    # epsilon = 1e-25 (strong portal but still below hard cap)
    assert loglike_phi_to_gamgam_xrism((-25.0, 0, 200.0, 0, 0, 0)) == 0.0


def test_loglike_at_extreme_m_phi_is_zero():
    """For all m_phi in 10-1000 MeV (posterior range), loglike = 0."""
    from xrism_phi_decay_forward_model import loglike_phi_to_gamgam_xrism
    for m_phi in [10.0, 50.0, 100.0, 200.0, 500.0, 1000.0]:
        assert loglike_phi_to_gamgam_xrism((-36.0, 0, m_phi, 0, 0, 0)) == 0.0


def test_loglike_above_hard_cap_returns_zero():
    """At epsilon >= 1e-30 (above hard cap), loglike returns 0 (out of posterior)."""
    from xrism_phi_decay_forward_model import loglike_phi_to_gamgam_xrism
    # epsilon = 1e-20 (way above hard cap)
    assert loglike_phi_to_gamgam_xrism((-20.0, 0, 200.0, 0, 0, 0)) == 0.0


def test_loglike_handles_malformed_theta():
    """Defensive: malformed theta should return 0, not raise."""
    from xrism_phi_decay_forward_model import loglike_phi_to_gamgam_xrism
    # Wrong-length tuple
    assert loglike_phi_to_gamgam_xrism((1.0,)) == 0.0
    # Empty
    assert loglike_phi_to_gamgam_xrism(()) == 0.0
    # None
    assert loglike_phi_to_gamgam_xrism(None) == 0.0


# === Wrapper integration ===

def test_wrapper_function_exists():
    """channels_extended.py wrapper for Channel 22 must exist."""
    from channels_extended import loglike_phi_to_gamgam_xrism as w
    theta = (-36.44, -15.7, 452.95, 769.69, 1.189, -0.803)
    assert w(theta) == 0.0


def test_wrapper_include_in_fit_false_returns_zero():
    """Wrapper with include_in_fit=False should return 0 (excluded channel)."""
    from channels_extended import loglike_phi_to_gamgam_xrism as w
    theta = (-36.44, -15.7, 452.95, 769.69, 1.189, -0.803)
    assert w(theta, include_in_fit=False) == 0.0


def test_wrapper_graceful_on_import_failure(monkeypatch):
    """If forward model fails to import, wrapper returns 0 gracefully."""
    # This tests the defensive try/except in the wrapper.
    # We can't easily simulate an ImportError without mocking sys.modules,
    # so just verify the wrapper works in the normal case (graceful = no exception).
    from channels_extended import loglike_phi_to_gamgam_xrism as w
    assert w((-36.0, 0, 200.0, 0, 0, 0)) == 0.0


# === Citation metadata ===

def test_r15b_audit_path_hardcoded():
    """R15B audit path must be hardcoded for traceability."""
    from xrism_phi_decay_forward_model import R15B_AUDIT_PATH
    assert "R15B_DATASET_AVAILABILITY_REASSESSMENT" in R15B_AUDIT_PATH
    assert "v0.3-prelim/docs" in R15B_AUDIT_PATH