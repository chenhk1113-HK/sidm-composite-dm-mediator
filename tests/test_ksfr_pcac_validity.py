"""Tests for KSFR/PCAC theoretical validity mask (Channel 15, v0.5).

Per R13 reviewer H1 concern (REVIEWER_AUDIT_R13.md 2026-08-25):
  Enforce theoretical validity bounds for composite dark-QCD parameters.
  Reject points where PCAC-KSFR relations are not physically justified.

Per MODEL_ASSUMPTIONS_AND_LIMITATIONS.md §6:
  f_pi in [0.05, 0.5] GeV
  g_chi in [0.01, 2.0]
  Lambda_dark in [0.1, 1.0] GeV
  m_rho/f_pi in [6.0, 9.0]
"""
import math
import os
import numpy as np
import pytest

# Make sure the v0.3-prelim/code path is on sys.path for direct import
import sys
from pathlib import Path
_V03_CODE = Path(__file__).resolve().parent.parent / "v0.3-prelim" / "code"
if str(_V03_CODE) not in sys.path:
    sys.path.insert(0, str(_V03_CODE))

from ksfr_pcac_validity import (
    is_in_validity_box,
    loglike_ksfr_pcac_validity,
    KSFR_F_PI_GEV_MIN, KSFR_F_PI_GEV_MAX,
    KSFR_G_CHI_MIN, KSFR_G_CHI_MAX,
    KSFR_M_RHO_OVER_F_PI_MIN, KSFR_M_RHO_OVER_F_PI_MAX,
)


# T41 theta vector: (log_m_phi_MeV, log_m_chi_GeV, g_chi, log_epsilon, log_alpha)
# T41 MAP (per the canonical fit): m_phi ~ 26.6 MeV, m_chi ~ 14.8 GeV
# Both are outside the KSFR validity box (m_phi way too small) — by design.
# So T41's main posterior is rejected by this mask; that's the documented
# v0.5 finding.
T41_MAP_THETA = (
    np.log10(26.6),   # log_m_phi_MeV ≈ 1.42 (26.6 MeV)
    np.log10(14.8),   # log_m_chi_GeV ≈ 1.17 (14.8 GeV)
    0.5,              # g_chi
    -35.0,            # log_epsilon
    -10.0,            # log_alpha
)


class TestValidityBounds:
    """The 3 independent bounds match MODEL_ASSUMPTIONS_AND_LIMITATIONS.md §6."""

    def test_f_pi_bounds(self):
        assert KSFR_F_PI_GEV_MIN == 0.05
        assert KSFR_F_PI_GEV_MAX == 0.5

    def test_g_chi_bounds(self):
        assert KSFR_G_CHI_MIN == 0.01
        assert KSFR_G_CHI_MAX == 2.0

    def test_m_rho_over_f_pi_bounds(self):
        assert KSFR_M_RHO_OVER_F_PI_MIN == 6.0
        assert KSFR_M_RHO_OVER_F_PI_MAX == 9.0


class TestIsInValidityBox:
    """Box check covers all 3 independent dimensions correctly."""

    def test_all_in_box(self):
        assert is_in_validity_box(0.1, 0.5, 8.0) is True

    def test_f_pi_below_min(self):
        assert is_in_validity_box(0.04, 0.5, 8.0) is False

    def test_f_pi_above_max(self):
        assert is_in_validity_box(0.6, 0.5, 8.0) is False

    def test_g_chi_below_min(self):
        assert is_in_validity_box(0.1, 0.005, 8.0) is False

    def test_g_chi_above_max(self):
        assert is_in_validity_box(0.1, 2.5, 8.0) is False

    def test_m_rho_over_f_pi_below_min(self):
        assert is_in_validity_box(0.1, 0.5, 5.5) is False

    def test_m_rho_over_f_pi_above_max(self):
        assert is_in_validity_box(0.1, 0.5, 9.5) is False

    def test_boundary_values_inclusive(self):
        # All at exact boundaries should be IN the box
        assert is_in_validity_box(
            KSFR_F_PI_GEV_MIN, KSFR_G_CHI_MIN, KSFR_M_RHO_OVER_F_PI_MIN,
        ) is True
        assert is_in_validity_box(
            KSFR_F_PI_GEV_MAX, KSFR_G_CHI_MAX, KSFR_M_RHO_OVER_F_PI_MAX,
        ) is True


class TestLoglikeKSFRValidity:
    """loglike_ksfr_pcac_validity behavior on representative theta vectors."""

    def test_qcd_reference_point_in_box(self):
        """QCD physical point (m_phi = 770 MeV, m_chi = 1 GeV, g_chi = 1):
        f_pi = 770/1000/8.36 = 0.092 GeV, Lambda = 0.092 GeV.
        All in [0.05, 0.5]: PASS."""
        theta = (np.log10(770.0), np.log10(1.0), 1.0, -35.0, -10.0)
        result = loglike_ksfr_pcac_validity(theta)
        assert result == 0.0

    def test_m_phi_too_small_rejected(self):
        """m_phi = 10 MeV → f_pi = 10/1000/8.36 = 0.0012 GeV: REJECT."""
        theta = (np.log10(10.0), np.log10(1.0), 1.0, -35.0, -10.0)
        result = loglike_ksfr_pcac_validity(theta)
        assert result == -np.inf

    def test_m_phi_too_large_rejected(self):
        """m_phi = 10 GeV → f_pi = 10/8.36 = 1.20 GeV: REJECT."""
        theta = (np.log10(10000.0), np.log10(1.0), 1.0, -35.0, -10.0)
        result = loglike_ksfr_pcac_validity(theta)
        assert result == -np.inf

    def test_g_chi_too_small_rejected(self):
        """g_chi = 0.001: REJECT."""
        theta = (np.log10(770.0), np.log10(1.0), 0.001, -35.0, -10.0)
        result = loglike_ksfr_pcac_validity(theta)
        assert result == -np.inf

    def test_g_chi_too_large_rejected(self):
        """g_chi = 3.0: REJECT."""
        theta = (np.log10(770.0), np.log10(1.0), 3.0, -35.0, -10.0)
        result = loglike_ksfr_pcac_validity(theta)
        assert result == -np.inf

    def test_negative_mass_rejected(self):
        """Defensive: nan/inf/negative inputs return -inf."""
        # log_m_phi_MeV = nan → returns -inf
        theta = (float("nan"), np.log10(1.0), 1.0, -35.0, -10.0)
        result = loglike_ksfr_pcac_validity(theta)
        assert result == -np.inf

    def test_negative_g_chi_rejected(self):
        """Negative g_chi: defensive -inf."""
        theta = (np.log10(770.0), np.log10(1.0), -1.0, -35.0, -10.0)
        result = loglike_ksfr_pcac_validity(theta)
        assert result == -np.inf


class TestEnvironmentEscape:
    """SIDM_DISABLE_KSFR_MASK=1 lets the mask pass for cross-version comparison."""

    def test_disabled_returns_zero(self, monkeypatch):
        monkeypatch.setenv("SIDM_DISABLE_KSFR_MASK", "1")
        # Even an out-of-box point returns 0 when disabled
        theta = (np.log10(10.0), np.log10(1.0), 1.0, -35.0, -10.0)
        result = loglike_ksfr_pcac_validity(theta)
        assert result == 0.0

    def test_enabled_by_default(self, monkeypatch):
        monkeypatch.delenv("SIDM_DISABLE_KSFR_MASK", raising=False)
        # Out-of-box point returns -inf when enabled
        theta = (np.log10(10.0), np.log10(1.0), 1.0, -35.0, -10.0)
        result = loglike_ksfr_pcac_validity(theta)
        assert result == -np.inf


class TestImplicationForT41:
    """Document what the mask does to T41's posterior.

    The T41 fit places m_phi ≈ 26.6 MeV (way below the KSFR validity
    lower bound of 418 MeV). This means T41's MAP is REJECTED by the
    mask. This is the documented v0.5 finding: the published T41
    posterior is in a region where KSFR/PCAC break down.
    """

    def test_t41_map_rejected_by_mask(self):
        result = loglike_ksfr_pcac_validity(T41_MAP_THETA)
        assert result == -np.inf, (
            "T41 MAP at m_phi=26.6 MeV is outside KSFR validity "
            "(needs 418-4180 MeV). The mask correctly rejects it."
        )

    def test_ksfr_valid_m_phi_range_for_qcd(self):
        """For SU(3) N_f=3 fundamental (ratio 8.36):
        valid m_phi = f_pi * 8.36 * 1000 = [418, 4180] MeV."""
        low_mev = KSFR_F_PI_GEV_MIN * 8.36 * 1000
        high_mev = KSFR_F_PI_GEV_MAX * 8.36 * 1000
        # Just inside: m_phi = 1000 MeV
        theta_in = (np.log10(1000.0), np.log10(1.0), 1.0, -35.0, -10.0)
        assert loglike_ksfr_pcac_validity(theta_in) == 0.0
        # Just outside: m_phi = 100 MeV
        theta_out = (np.log10(100.0), np.log10(1.0), 1.0, -35.0, -10.0)
        assert loglike_ksfr_pcac_validity(theta_out) == -np.inf
        # Sanity on the bounds (note: boundaries are INCLUSIVE per the spec)
        assert low_mev < 420
        assert abs(high_mev - 4180.0) < 0.01
        assert abs(low_mev - 418.0) < 0.01
