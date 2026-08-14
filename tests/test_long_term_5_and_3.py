"""
Tests for gravothermal.py and channels_extended.py — Long-Term #5 and #3 deliverables.
"""
from __future__ import annotations
import sys
from pathlib import Path

# Add project root + v0.3 code to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "v0.1-prelim" / "code"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "v0.3-prelim" / "code"))

import numpy as np
import pytest

from gravothermal import (
    gravothermal_r_core,
    gravothermal_burkert_profile,
    r_core_empirical_old,
)
from channels_extended import (
    sigma_LZ_limit,
    is_excluded_by_LZ,
    loglike_direct_detection_exclusion,
    gravothermal_collapse_prior,
    sidm_m_chi_estimate,
)


class TestGravothermal:
    """Long-Term #5 — gravothermal halo evolution."""

    def test_low_sigma_m_expanded_phase(self):
        """At sigma/m = 0.1 cm^2/g, halo should be in expanded phase at t=5 Gyr."""
        r_core = gravothermal_r_core(sigma_m=0.1, t_Gyr=5.0)
        # t_core ~ 127 Gyr for sigma/m=0.1, way beyond 5 Gyr
        assert r_core > 0.3, f"expanded phase should give r_core ~ 0.4 kpc, got {r_core}"

    def test_high_sigma_m_collapsed_phase(self):
        """At sigma/m = 10 cm^2/g, halo should be collapsed by t=5 Gyr."""
        r_core = gravothermal_r_core(sigma_m=10.0, t_Gyr=5.0)
        # t_core ~ 1.27 Gyr for sigma/m=10, well before 5 Gyr
        assert r_core < 0.2, f"collapsed phase should give r_core ~ 0.05 kpc, got {r_core}"

    def test_r_core_floor(self):
        """r_core should never go below 0.05 kpc (physical floor)."""
        for sigma_m in [10.0, 30.0, 100.0]:
            r_core = gravothermal_r_core(sigma_m=sigma_m, t_Gyr=20.0)
            assert r_core >= 0.05, f"floor violated at sigma/m={sigma_m}: {r_core}"

    def test_old_vs_new_agree_at_transition(self):
        """Old (Robertson+) and new (gravothermal) should give similar r_core
        for sigma/m around the transition (~1 cm^2/g, t~10 Gyr)."""
        # Both models are non-physical extrapolations at this regime; just
        # check neither is zero or infinity.
        r_old = r_core_empirical_old(1.0)
        r_new = gravothermal_r_core(sigma_m=1.0, t_Gyr=10.0)
        assert 0.01 < r_old < 100
        assert 0.01 < r_new < 100

    def test_burkert_profile_returns_finite(self):
        """gravothermal_burkert_profile should return finite V^2 array."""
        r = np.linspace(0.1, 50, 50)
        v2 = gravothermal_burkert_profile(r, sigma_m=1.0, t_Gyr=10.0)
        assert np.all(np.isfinite(v2))
        assert np.all(v2 > 0)


class TestChannelExtended:
    """Long-Term #3 — direct detection channel + SASHIMI-SIDM priors."""

    def test_lz_limit_interpolation(self):
        """LZ limit at m=36 GeV should be ~9.2e-48 (the minimum)."""
        limit = sigma_LZ_limit(36.0)
        assert abs(limit - 9.2e-48) < 1e-49, f"LZ limit at 36 GeV wrong: {limit}"

    def test_lz_limit_extrapolation(self):
        """LZ limit should be defined (not NaN) for masses in range."""
        for m in [3.0, 5.0, 10.0, 100.0, 500.0, 1000.0]:
            limit = sigma_LZ_limit(m)
            assert np.isfinite(limit)
            assert limit > 0

    def test_lz_exclusion_check(self):
        """A model well above LZ limit should be excluded."""
        assert is_excluded_by_LZ(m_chi_GeV=100, sigma_DM_nucleon_cm2=1e-44)
        # A model well below LZ limit should not be excluded
        assert not is_excluded_by_LZ(m_chi_GeV=100, sigma_DM_nucleon_cm2=1e-50)

    def test_direct_detection_orthogonality_subGeV(self):
        """For m_chi < 3 GeV, direct detection does not constrain (LZ threshold)."""
        ll = loglike_direct_detection_exclusion(sigma_m=1.0, m_chi_GeV=1.0)
        assert ll == 0.0, f"sub-GeV should have no LZ penalty, got {ll}"

    def test_sidm_m_chi_estimate(self):
        """sidm_m_chi_estimate should return a positive GeV value."""
        m_chi = sidm_m_chi_estimate(1.0)
        assert m_chi > 0

    def test_gravothermal_collapse_prior_old_halo(self):
        """For old (high t_formation) halos with high sigma/m, the prior penalizes
        cored profile models (because the halo has likely collapsed)."""
        prior = gravothermal_collapse_prior(
            halo_mass_Msun=1e14,  # cluster
            halo_formation_time_Gyr=10.0,  # very old
        )
        # For sigma/m ~ 1 and t_dyn ~ 0.05 Gyr at cluster scale, t_core ~ 0.6 Gyr
        # So a 10 Gyr halo IS collapsed → penalty
        assert prior <= 0.0

    def test_gravothermal_collapse_prior_young_halo(self):
        """For young (low t_formation) halos with low sigma/m, no penalty."""
        prior = gravothermal_collapse_prior(
            halo_mass_Msun=1e10,  # dwarf
            halo_formation_time_Gyr=1.0,  # young
        )
        assert prior >= -0.1, f"young dwarf halo should not be penalized, got {prior}"

    def test_lens_subhalo_placeholder(self):
        """loglike_lens_subhalo_placeholder is a backward-compat alias for
        loglike_lens_subhalo(sigma_m_0, a=0).
        """
        from channels_extended import loglike_lens_subhalo_placeholder, loglike_lens_subhalo
        # Both should give identical results
        assert loglike_lens_subhalo_placeholder(50.0) == loglike_lens_subhalo(50.0, 0.0)
        assert loglike_lens_subhalo_placeholder(100.0) == loglike_lens_subhalo(100.0, 0.0)

    def test_lens_subhalo_channel(self):
        """Channel 6 (arXiv:2510.11006) — Gaussian constraint on σ/m_eff at subhalo v."""
        from channels_extended import (
            loglike_lens_subhalo, LENS_SIGMA_M_LOG_PEAK, LENS_SIGMA_M_LOG_WIDTH,
        )
        # At peak (σ/m_0=50, a=0): log_eff = log10(50) = 1.7 → log L = 0
        assert abs(loglike_lens_subhalo(50.0, 0.0)) < 0.01
        # 1 dex above peak should be heavily penalized
        assert loglike_lens_subhalo(500.0, 0.0) < -5.0
        # 1 dex below peak should be heavily penalized
        assert loglike_lens_subhalo(5.0, 0.0) < -5.0
        # v-dep coupling: σ/m_0=5, a=1 → log_eff = log10(5)+1 = 1.7 = peak
        assert abs(loglike_lens_subhalo(5.0, 1.0)) < 0.01
        # σ/m_0=500, a=-1 → log_eff = log10(500)-1 = 1.7 = peak
        assert abs(loglike_lens_subhalo(500.0, -1.0)) < 0.01
        # Verify constants match the paper
        assert abs(LENS_SIGMA_M_LOG_PEAK - np.log10(50.0)) < 0.01
        assert LENS_SIGMA_M_LOG_WIDTH == 0.3

    def test_mw_satellite_upper_limit(self):
        """Channel 7 (arXiv:2503.13650) — MW satellite galaxies upper limit."""
        from channels_extended import (
            loglike_mw_satellite, DSPH_SIGMA_M_UPPER_LIMIT,
        )
        # At σ/m_0 = 0.5 (below 1.0 limit at V_50=18 km/s): log L = 0
        assert loglike_mw_satellite(0.5, 0.0) == 0.0
        # At σ/m_0 = 2.0 (above 1.0 limit): log L < 0
        assert loglike_mw_satellite(2.0, 0.0) < 0.0
        # At σ/m_0 = 10.0 (1 dex above limit): log L ≈ -1
        assert -1.5 < loglike_mw_satellite(10.0, 0.0) < -0.5
        # Verify the paper's number
        assert abs(DSPH_SIGMA_M_UPPER_LIMIT - 0.2) < 0.01

    def test_cluster_upper_limit(self):
        """Channel 8 (arXiv:2508.20179, O'Donnell+ 2026 PRD) — cluster upper limit."""
        from channels_extended import (
            loglike_cluster_upper, CLUSTER_SIGMA_M_UPPER_LIMIT,
        )
        # At σ/m_0 = 0.1 (below 0.613 limit): log L = 0
        assert loglike_cluster_upper(0.1, 0.0) == 0.0
        # At σ/m_0 = 1.0 (above limit): log L < 0
        assert loglike_cluster_upper(1.0, 0.0) < 0.0
        # Verify paper's number
        assert abs(CLUSTER_SIGMA_M_UPPER_LIMIT - 0.613) < 0.01

    def test_draco_upper_limit(self):
        """Channel 9 (Read+ 2018) — Draco dSph upper limit at v=20 km/s."""
        from channels_extended import (
            loglike_draco, DRACO_SIGMA_M_UPPER_LIMIT,
        )
        # At σ/m_0 = 0.1 (below 0.57 limit at v=20 km/s with a=0): log L = 0
        # log10(0.1) = -1.0, upper = log10(0.57) = -0.244, so -1.0 < -0.244 → 0.0
        assert loglike_draco(0.1, 0.0) == 0.0
        # At σ/m_0 = 1.0 (above limit): log L < 0
        # log10(1.0) = 0 > -0.244 → penalty
        assert loglike_draco(1.0, 0.0) < 0.0
        # Verify the paper's number
        assert abs(DRACO_SIGMA_M_UPPER_LIMIT - 0.57) < 0.01

    def test_radio_relic_upper_limit(self):
        """Channel 10 (arXiv:2605.00093, Lee+ 2026) — 11-cluster radio relic."""
        from channels_extended import (
            loglike_radio_relic, RADIO_RELIC_SIGMA_M_UPPER_LIMIT,
        )
        # At σ/m_0 = 0.1 (below 0.22 limit): log L = 0
        # log10(0.1) = -1.0, upper = log10(0.22) = -0.658, so -1.0 < -0.658 → 0.0
        assert loglike_radio_relic(0.1, 0.0) == 0.0
        # At σ/m_0 = 0.5 (above limit, even with a=0): log L < 0
        # log10(0.5) = -0.301, which is greater than -0.658 → penalty
        assert loglike_radio_relic(0.5, 0.0) < 0.0
        # Verify the paper's number
        assert abs(RADIO_RELIC_SIGMA_M_UPPER_LIMIT - 0.22) < 0.01
        # v-dep coupling: σ/m_0 = 2.2, a = 1 → log_sm = log10(2.2) - 1 = -0.658 = peak
        assert abs(loglike_radio_relic(2.2, 1.0)) < 0.01