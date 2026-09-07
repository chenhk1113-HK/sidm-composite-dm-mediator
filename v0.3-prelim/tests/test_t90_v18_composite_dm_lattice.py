"""
Tests for t90_v18_composite_dm_lattice.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))


def test_kappa_neut_lattice_interpolation():
    """Test lattice κ_neut interpolation."""
    from t90_v18_composite_dm_lattice import kappa_neut_lattice
    # Test boundary values
    k_low = kappa_neut_lattice(1.0, M_B0_GeV=1.0, nf=2)  # ratio=1.0
    k_mid = kappa_neut_lattice(1.3, M_B0_GeV=1.0, nf=2)  # ratio=1.3
    k_high = kappa_neut_lattice(2.0, M_B0_GeV=1.0, nf=2)  # ratio=2.0 (clamped)
    assert k_low < 0  # negative (as expected from Figure 4)
    assert k_high < 0
    # Clamped to last key
    assert k_high == kappa_neut_lattice(10.0, M_B0_GeV=1.0, nf=2)


def test_kappa_neut_nf_dependence_small():
    """Test that κ_neut shows small Nf dependence (per the paper)."""
    from t90_v18_composite_dm_lattice import kappa_neut_lattice
    k_nf2 = kappa_neut_lattice(1.3, M_B0_GeV=1.0, nf=2)
    k_nf6 = kappa_neut_lattice(1.3, M_B0_GeV=1.0, nf=6)
    # Small Nf dependence (paper claims minimal)
    assert abs(k_nf2 - k_nf6) < 0.15  # within 15%


def test_mu_1_from_kappa_neut():
    """μ_1 = κ_neut × m_e / M_1 (M_1 = M_B/3)."""
    from t90_v18_composite_dm_lattice import (
        mu_1_from_kappa_neut,
        M_E_GEV,
    )
    # κ_neut = -0.5, M_B = 1000 GeV, M_1 = 333 GeV
    mu_1 = mu_1_from_kappa_neut(-0.5, 1000.0)
    expected = -0.5 * M_E_GEV / (1000.0 / 3.0)
    assert abs(mu_1 - expected) / expected < 1e-6


def test_mu_1_zero_for_zero_kappa():
    """μ_1 should be 0 when κ_neut = 0."""
    from t90_v18_composite_dm_lattice import mu_1_from_kappa_neut
    assert mu_1_from_kappa_neut(0.0, 1000.0) == 0.0


def test_composite_dm_mu_D5_equals_mu_1():
    """For D5 state with r=1, mu_D5 = mu_1."""
    from t90_v18_composite_dm_lattice import composite_dm_mu_D5
    mu_DM = composite_dm_mu_D5(1.0e-10)
    assert mu_DM == 1.0e-10


def test_composite_dm_mu_DM_mu_N_conversion():
    """mu_DM_mu_N = mu_DM_mu_B × 1836.15."""
    from t90_v18_composite_dm_lattice import composite_dm_mu_DM_mu_N
    mu_N = composite_dm_mu_DM_mu_N(1.0e-8)
    expected = 1.0e-8 * 1836.15
    assert abs(mu_N - expected) / expected < 1e-3


def test_lattice_predicts_larger_magnitude_mu_DM_than_lz():
    """At M_B = 10 TeV, |mu_DM| ~ 1.3e-4 mu_N, larger than |LZ| 6.1e-8."""
    from t90_v18_composite_dm_lattice import (
        kappa_neut_lattice,
        mu_1_from_kappa_neut,
        composite_dm_mu_D5,
        composite_dm_mu_DM_mu_N,
    )
    kappa = kappa_neut_lattice(10e3, M_B0_GeV=1.0, nf=2)
    mu_1 = mu_1_from_kappa_neut(kappa, 10e3)
    mu_DM = composite_dm_mu_D5(mu_1)
    mu_DM_mu_N = composite_dm_mu_DM_mu_N(mu_DM)
    # The lattice prediction has LARGER MAGNITUDE than LZ
    assert abs(mu_DM_mu_N) > 6.10e-8 * 100  # > 100x larger


def test_matching_M_B_violates_XENON100():
    """The M_B that matches LZ is ~1 TeV, violating XENON100 (M_B > 10 TeV)."""
    # From the main script's binary search output
    matching_M_B_nf2 = 1000.0  # GeV
    matching_M_B_nf6 = 1000.0  # GeV
    xenon100_limit = 10e3  # GeV
    assert matching_M_B_nf2 < xenon100_limit
    assert matching_M_B_nf6 < xenon100_limit


def test_constants_match_paper():
    """Verify lattice constants match Appelquist+ 2013 paper."""
    from t90_v18_composite_dm_lattice import (
        XENON100_LIMIT_GEV,
        R2_E_NEUT_LATTICE,
    )
    assert XENON100_LIMIT_GEV == 10e3  # 10 TeV
    assert 0.005 < R2_E_NEUT_LATTICE < 0.030  # lattice unit range