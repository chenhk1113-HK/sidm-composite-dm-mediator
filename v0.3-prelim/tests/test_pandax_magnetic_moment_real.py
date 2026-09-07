"""
Tests for pandax_magnetic_moment_real.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))


def test_pandax_limit_at_best_mass():
    """At m_chi = 40 GeV, PandaX limit should equal published value."""
    from pandax_magnetic_moment_real import (
        pandax_limit_at_mass,
        PANDAX_MAGNETIC_MOMENT_LIMIT_MUB,
        PANDAX_MAGNETIC_MOMENT_BEST_MASS_GEV,
    )
    limit = pandax_limit_at_mass(PANDAX_MAGNETIC_MOMENT_BEST_MASS_GEV)
    assert abs(limit - PANDAX_MAGNETIC_MOMENT_LIMIT_MUB) / PANDAX_MAGNETIC_MOMENT_LIMIT_MUB < 1e-6


def test_pandax_limit_grows_with_mass():
    """Limit should grow (weaken) with mass for magnetic-moment interactions."""
    from pandax_magnetic_moment_real import pandax_limit_at_mass
    l_low = pandax_limit_at_mass(40)
    l_mid = pandax_limit_at_mass(1000)
    l_high = pandax_limit_at_mass(5000)
    assert l_low < l_mid < l_high


def test_lz_tuned_mu_x_in_mu_B():
    """LZ-tuned mu_x = 6.10e-8 mu_N should be 3.32e-11 mu_B."""
    from pandax_magnetic_moment_real import (
        lz_tuned_mu_x_at_mass,
        LZ_TUNED_MU_X_MU_N,
    )
    mu_B = lz_tuned_mu_x_at_mass(1000)
    expected = LZ_TUNED_MU_X_MU_N / 1836.15267
    assert abs(mu_B - expected) / expected < 1e-6


def test_lz_mass_independent():
    """mu_x in mu_N is mass-independent for fixed EFT operator."""
    from pandax_magnetic_moment_real import lz_tuned_mu_x_at_mass
    mu_B_1 = lz_tuned_mu_x_at_mass(100)
    mu_B_2 = lz_tuned_mu_x_at_mass(1000)
    assert abs(mu_B_1 - mu_B_2) < 1e-15


def test_lz_not_excluded_by_pandax_at_1_TeV():
    """Critical test: LZ interpretation should NOT be excluded by PandaX."""
    from pandax_magnetic_moment_real import loglike_pandax_magnetic_moment
    r = loglike_pandax_magnetic_moment(m_chi_GeV=1000)
    assert not r['excluded_by_pandax'], (
        f"LZ excluded by PandaX! Ratio = {r['ratio_measured_to_limit']}"
    )


def test_pandax_log_l_zero_for_lz_params():
    """Log L should be 0 (consistent) when LZ is below limit."""
    from pandax_magnetic_moment_real import loglike_pandax_magnetic_moment
    r = loglike_pandax_magnetic_moment(m_chi_GeV=1000)
    assert r['log_l'] == 0.0


def test_high_mu_excluded_with_penalty():
    """For very large mu (way above limit), log L should be very negative."""
    from pandax_magnetic_moment_real import loglike_pandax_magnetic_moment
    # Use mu_x = 1e-3 mu_N = 5.4e-7 mu_B (way above limit at 1 TeV)
    r = loglike_pandax_magnetic_moment(m_chi_GeV=1000, mu_x_mu_N=1e-3)
    assert r['excluded_by_pandax']
    assert r['log_l'] < -100  # strong penalty


def test_real_data_constants():
    """Verify real-data constants match PandaX Nature 618 paper."""
    from pandax_magnetic_moment_real import (
        PANDAX_MAGNETIC_MOMENT_LIMIT_MUB,
        PANDAX_EXPOSURE_TONNE_YEAR,
        PANDAX_MAGNETIC_MOMENT_BEST_MASS_GEV,
    )
    assert abs(PANDAX_MAGNETIC_MOMENT_LIMIT_MUB - 4.8e-10) < 1e-12
    assert PANDAX_EXPOSURE_TONNE_YEAR == 0.63
    assert PANDAX_MAGNETIC_MOMENT_BEST_MASS_GEV == 40.0


def test_ratio_below_one_at_all_masses():
    """For LZ-tuned mu_x, ratio should be < 1 across all tested masses."""
    from pandax_magnetic_moment_real import loglike_pandax_magnetic_moment
    for m_chi in [10, 40, 100, 1000, 5000]:
        r = loglike_pandax_magnetic_moment(m_chi_GeV=m_chi)
        assert r['ratio_measured_to_limit'] < 1.0, (
            f"At m_chi={m_chi}, ratio = {r['ratio_measured_to_limit']} (expected < 1)"
        )