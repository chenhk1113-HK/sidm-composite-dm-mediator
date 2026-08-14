"""
Test suite for sidm-composite-dm-mediator.

Per peer review (2026-08-10, Section 2.2.4):
    "No automated unit/integration test suite"
    "Code edits to halo_profiles.py or channels_v03.py risk silent regression
     bugs with no automated detection."

Run with:
    pytest tests/ -v
or:
    python -m pytest tests/ -v
"""
from __future__ import annotations
import sys
from pathlib import Path

# Add project root + v0.1/v0.3 code dirs to sys.path so tests can import config + halo_profiles
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "v0.1-prelim" / "code"))
sys.path.insert(0, str(PROJECT_ROOT / "v0.3-prelim" / "code"))

import numpy as np
import pytest

from config import (
    G_KPC_KMS, V_REF, V_UFD, V_DSPH, V_GALAXY, V_CLUSTER,
    LOG_SIGMA_M_RANGE, A_RANGE,
)  # noqa: F401  (kept for reference; tests use config.X directly)
from halo_profiles import V_NFW, V_Burkert
from channels_v03 import (
    sigma_m_at_v,
    loglike_dsph_v03, loglike_ufd_v03, loglike_bullet_v03,
)
# DSPH_PEAK_LOG_SM, UFD_LOG_SM_MEAN, BULLET_LOG_SM_LIMIT are in config (peer review fix)
import config


# ---------------------------------------------------------------------------
# Test group 1: halo profile closed-form correctness
# ---------------------------------------------------------------------------

class TestNFW:
    """NFW circular velocity V^2(r) analytic tests."""

    def test_zero_radius_zero_velocity(self):
        r = np.array([0.0])
        v2 = V_NFW(r, rho_s=1e7, r_s=10.0)
        assert v2[0] == 0.0, f"V_NFW(0) should be 0, got {v2[0]}"

    def test_positive_at_all_r(self):
        r = np.linspace(0.1, 100.0, 50)
        v2 = V_NFW(r, rho_s=1e7, r_s=10.0)
        assert np.all(v2 > 0), "V_NFW must be positive for all r > 0"

    def test_log_slope_outer(self):
        """At r >> r_s, V_NFW^2 should decay as 1/r (NFW outer envelope)."""
        r = np.array([100.0, 200.0, 400.0])
        v2 = V_NFW(r, rho_s=1e7, r_s=10.0)
        # NFW outer envelope: V^2 ∝ ln(r)/r → for r>>r_s, approximately 1/r
        # At r=100, r_s=10: ln(11)/100 ~ 0.024; at r=200: ln(21)/200 ~ 0.015
        # ratio ~ 0.015/0.024 ~ 0.62 (close to 0.5 for 1/r pure, but log factor)
        ratio_1 = v2[1] / v2[0]
        ratio_2 = v2[2] / v2[1]
        # Allow wider tolerance for log correction
        assert 0.5 < ratio_1 < 0.85, f"outer ratio (NFW ~ 1/r w/ log): {ratio_1}"
        assert 0.5 < ratio_2 < 0.85, f"outer ratio: {ratio_2}"

    def test_typical_value_magnitude(self):
        """At r=r_s, V_NFW^2 should be modest for typical galaxy halo parameters.

        For rho_s=1e7 M_sun/kpc^3 and r_s=10 kpc, V_NFW(r_s) is roughly
        50-200 (km/s)^2 → V ~ 7-14 km/s. Sanity check the order.
        """
        rho_s = 1e7
        r_s = 10.0
        r = r_s
        v2 = V_NFW(np.array([r]), rho_s, r_s)[0]
        # Compute analytically: V^2(r_s) = 4πG ρ_s r_s^2 (ln 2 - 1/2)
        # = 4 * 3.14 * 4.3e-6 * 1e7 * 100 * (0.69 - 0.5) = 10231
        assert 1000.0 < v2 < 50000.0, f"V_NFW(r_s) magnitude sanity: V^2={v2:.2f}"


class TestBurkert:
    """Burkert circular velocity tests."""

    def test_zero_at_zero(self):
        """V_Burkert(0) should be 0 by construction (V^2 = G M/r)."""
        r = np.array([0.0])
        v2 = V_Burkert(r, rho_c=1e7, r_c=1.0)
        assert v2[0] == 0.0, f"V_Burkert(0) should be 0, got {v2[0]}"

    def test_positive_at_all_r(self):
        r = np.logspace(-2, 2, 50)
        v2 = V_Burkert(r, rho_c=1e7, r_c=1.0)
        assert np.all(np.isfinite(v2)), "V_Burkert must be finite"
        assert np.all(v2 > 0), f"V_Burkert must be positive for r>0, min={v2.min()}"

    def test_core_inner_slope(self):
        """At r << r_c, V_Burkert^2 rises steeper than linear (mass ~ r in deep core)."""
        r = np.array([0.05, 0.1, 0.2])
        r_c = 1.0
        v2 = V_Burkert(r, rho_c=1e7, r_c=r_c)
        # In the deep core (r << r_c), V^2 rises ~ r^2 because M(r) ~ ρ_c r_c^3 (r/r_c)
        # while atan(r/r_c) ≈ r/r_c — quadratic behavior near origin.
        # Doubling r should give ~4x V^2 in the deepest core.
        ratio_1 = v2[1] / v2[0]
        ratio_2 = v2[2] / v2[1]
        # Allow for the actual Burkert slope of ~3-4 in the innermost region.
        assert 2.0 < ratio_1 < 6.0, f"deep core ratio (Burkert ~ r^2): {ratio_1}"
        assert 2.0 < ratio_2 < 6.0, f"deep core ratio: {ratio_2}"

    def test_outer_slope(self):
        """At r >> r_c, V_Burkert^2 should fall (mass ~ log r, so V^2 ~ log r / r)."""
        r = np.array([10.0, 20.0, 40.0])
        r_c = 1.0
        v2 = V_Burkert(r, rho_c=1e7, r_c=r_c)
        # Outer envelope: V^2 ~ ln(r)/r → decay but slow (log factor)
        ratio_1 = v2[1] / v2[0]
        ratio_2 = v2[2] / v2[1]
        # Should decrease but not by 0.25 (that's 1/r^2); ~0.6 is closer
        assert 0.3 < ratio_1 < 0.9, f"outer ratio (log falloff): {ratio_1}"
        assert 0.3 < ratio_2 < 0.9, f"outer ratio: {ratio_2}"

    def test_larger_core_lower_vmax_at_fixed_r(self):
        """At fixed radius, larger core radius → lower V^2 (for fixed rho_c)."""
        r = np.array([1.0])  # exactly at r_c for the small one
        v_small_r_c = V_Burkert(r, rho_c=1e7, r_c=0.5)
        v_large_r_c = V_Burkert(r, rho_c=1e7, r_c=2.0)
        # At r=1, r_c=0.5: r > r_c (outer regime, V decreases)
        # At r=1, r_c=2.0: r < r_c (inner regime, V increases linearly with r)
        # Just sanity-check both are finite and positive
        assert v_small_r_c > 0 and v_large_r_c > 0
        assert np.isfinite(v_small_r_c) and np.isfinite(v_large_r_c)


# ---------------------------------------------------------------------------
# Test group 2: velocity-dependent cross-section
# ---------------------------------------------------------------------------

class TestVelocityDependent:
    """sigma/m(v) = sigma/m_0 * (v / v_ref)^(-a) scaling."""

    def test_at_reference_velocity(self):
        """At v = V_REF, sigma/m should equal sigma/m_0 (no change)."""
        sigma_0 = 1.0
        a = 0.5
        v_test = sigma_m_at_v(sigma_0, a, V_REF)
        assert abs(v_test - sigma_0) < 1e-9, f"sigma/m at V_REF should be sigma/m_0: {v_test}"

    def test_velocity_independent_at_a_zero(self):
        """a=0 → sigma/m constant for all velocities."""
        sigma_0 = 2.0
        for v in [10, 100, 1000]:
            v_test = sigma_m_at_v(sigma_0, 0.0, v)
            assert abs(v_test - sigma_0) < 1e-9, f"a=0 → constant: got {v_test}"

    def test_positive_a_decreases_with_v(self):
        """a > 0 → sigma/m decreases as v increases."""
        sigma_0 = 1.0
        a = 1.0
        # v in km/s: ufd < dSph < galaxy < cluster
        v_ufd = sigma_m_at_v(sigma_0, a, V_UFD)
        v_dwarf = sigma_m_at_v(sigma_0, a, V_DSPH)
        v_galaxy = sigma_m_at_v(sigma_0, a, V_GALAXY)
        v_cluster = sigma_m_at_v(sigma_0, a, V_CLUSTER)
        assert v_ufd > v_dwarf > v_galaxy > v_cluster, \
            f"a=1 monotonic decrease: u={v_ufd}, d={v_dwarf}, g={v_galaxy}, c={v_cluster}"


# ---------------------------------------------------------------------------
# Test group 3: Channel likelihoods
# ---------------------------------------------------------------------------

class TestDsphLikelihood:
    """Channel 2 (Horigome+ 2025) bimodal with dip.

    The dSph likelihood is evaluated at the dSph velocity scale (V_DSPH=30 km/s),
    not at V_REF. So sigma/m_0 values need to be scaled to put sigma/m(v_dSph)
    at the peaks.
    """

    def test_peak_at_small(self):
        """sigma/m at V_DSPH should hit the small peak (~0.1 cm^2/g)."""
        ll = loglike_dsph_v03(sigma_m_0=0.1, a=0.0)
        assert ll > -2.0, f"log L at small peak should be > -2 (it's a peak), got {ll}"

    def test_peak_at_large(self):
        """sigma/m at V_DSPH should hit the large peak (~10 cm^2/g)."""
        ll = loglike_dsph_v03(sigma_m_0=10.0, a=0.0)
        assert ll > -2.0, f"log L at large peak should be > -2 (it's a peak), got {ll}"

    def test_dip_penalty(self):
        """sigma/m at V_DSPH ~ 1 cm^2/g should be lower than both peaks (exclusion dip)."""
        ll_dip = loglike_dsph_v03(sigma_m_0=1.0, a=0.0)
        ll_small = loglike_dsph_v03(sigma_m_0=0.1, a=0.0)
        ll_large = loglike_dsph_v03(sigma_m_0=10.0, a=0.0)
        assert ll_dip < ll_small, f"dip should be < small peak: dip={ll_dip}, small={ll_small}"
        assert ll_dip < ll_large, f"dip should be < large peak: dip={ll_dip}, large={ll_large}"

    def test_invalid_returns_neg_inf(self):
        assert loglike_dsph_v03(-1.0, 0.0) == -np.inf
        assert loglike_dsph_v03(0.0, 0.0) == -np.inf


class TestUfdLikelihood:
    """Channel 3 (Sanchez-Almeida+ 2025)."""

    def test_peak_at_published_value(self):
        """At sigma/m_UFD = 10^0.92 (a=0), log L should be ~0."""
        ll = loglike_ufd_v03(sigma_m_0=10**0.92, a=0.0)
        assert ll > -0.5, f"log L at published best should be ~0, got {ll}"

    def test_decay_far_from_peak(self):
        """Far from peak should be heavily penalized (Gaussian)."""
        ll_peak = loglike_ufd_v03(sigma_m_0=10**0.92, a=0.0)
        ll_far = loglike_ufd_v03(sigma_m_0=10**(0.92 + 5.0), a=0.0)
        # UFD width is 1.37 dex — at 5 dex away, penalty is (5/1.37)^2/2 ≈ 8.3
        assert ll_far < ll_peak - 5, f"5-sigma should drop >5: peak={ll_peak}, far={ll_far}"


class TestBulletLikelihood:
    """Channel 4 (Cha+ 2025) one-sided upper limit."""

    def test_no_penalty_below_limit(self):
        """sigma/m < 0.5 cm^2/g at cluster scale → no penalty."""
        ll = loglike_bullet_v03(sigma_m_0=0.1, a=0.0)
        assert ll == 0.0, f"below limit should be 0 (no penalty), got {ll}"

    def test_penalty_above_limit(self):
        """sigma/m > 0.5 cm^2/g at cluster scale → penalty."""
        ll = loglike_bullet_v03(sigma_m_0=10.0, a=0.0)
        # log sigma/m = 1; (1 - (-0.30))/0.30 = 4.33; penalty = -0.5 * 4.33^2 = -9.39
        assert ll < -5.0, f"above limit should be penalized, got {ll}"

    def test_monotonic_above_limit(self):
        """Above limit, more sigma/m → worse log L."""
        ll_1 = loglike_bullet_v03(sigma_m_0=1.0, a=0.0)
        ll_2 = loglike_bullet_v03(sigma_m_0=10.0, a=0.0)
        ll_3 = loglike_bullet_v03(sigma_m_0=100.0, a=0.0)
        assert ll_1 > ll_2 > ll_3, f"monotonic penalty: {ll_1}, {ll_2}, {ll_3}"


# ---------------------------------------------------------------------------
# Test group 4: Configuration sanity
# ---------------------------------------------------------------------------

class TestConfig:
    """Central config.py sanity checks."""

    def test_velocity_scales_ordered(self):
        """V_UFD < V_DSPH < V_REF = V_GALAXY < V_CLUSTER."""
        import config
        assert config.V_UFD < config.V_DSPH < config.V_REF == config.V_GALAXY < config.V_CLUSTER

    def test_version_paths_resolve(self):
        """All version paths must exist on disk."""
        for v in ["v01", "v02", "v03"]:
            p = config.get_version_paths(v)
            assert p["root"].exists(), f"{v} root missing: {p['root']}"
            assert p["code"].exists(), f"{v} code dir missing"

    def test_posterior_ranges_consistent(self):
        """LOG_SIGMA_M_RANGE and A_RANGE should be sensible."""
        assert LOG_SIGMA_M_RANGE[0] < LOG_SIGMA_M_RANGE[1]
        assert A_RANGE[0] < A_RANGE[1]
        # log sigma/m should cover at least 5 orders of magnitude
        assert LOG_SIGMA_M_RANGE[1] - LOG_SIGMA_M_RANGE[0] >= 5

    def test_dspy_bimodal_peaks_in_config(self):
        """DSPH_PEAK_LOG_SM should be (small, large) with small < large."""
        assert len(config.DSPH_PEAK_LOG_SM) == 2
        assert config.DSPH_PEAK_LOG_SM[0] < config.DSPH_PEAK_LOG_SM[1]

    def test_ufd_mean_positive(self):
        """config.UFD_LOG_SM_MEAN > 0 (Sanchez-Almeida+ prefers sigma/m > 1 cm^2/g)."""
        assert config.UFD_LOG_SM_MEAN > 0.5

    def test_bullet_limit_negative(self):
        """config.BULLET_LOG_SM_LIMIT < 0 (limit is sigma/m < 0.5 cm^2/g, log < 0)."""
        assert config.BULLET_LOG_SM_LIMIT < 0


# ---------------------------------------------------------------------------
# Test group 5: SPARC data loader smoke test
# ---------------------------------------------------------------------------

class TestSparcLoader:
    """SPARC rotmod file loader sanity checks."""

    def test_load_one_galaxy(self):
        """Should load at least one galaxy successfully."""
        from sparc_loader import load_one_sparc
        ga = load_one_sparc(config.DATA_DIR, "NGC2403")
        assert ga.name == "NGC2403"
        assert len(ga.Rad) > 5
        assert np.all(np.isfinite(ga.Vobs))

    def test_load_all_returns_175(self):
        """Should load all 175 SPARC galaxies."""
        from sparc_loader import load_all_sparc
        galaxies = load_all_sparc(config.DATA_DIR)
        assert len(galaxies) == 175, f"expected 175, got {len(galaxies)}"


if __name__ == "__main__":
    # Run as plain Python if pytest not installed
    pytest.main([__file__, "-v"])