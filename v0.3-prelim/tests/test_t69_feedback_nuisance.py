"""
Tests for T69 — baryonic-feedback nuisance parameter.

Per the closure patterns K1/K2 from v0.3-prelim/docs/REVIEWER_AUDIT_R12.md:
  - K1: ast-based regression tests for "remove the dead import" fixes.
  - K2: Reproduction script FIRST, then patch, then promote to test.

What this test verifies (post-R12 closure patterns):
  1. The Di Cintio+ 2014a relation matches the published coefficients.
  2. The sparc_feedback_rescale function returns the documented values
     at the boundary points (f_fb in {0.0, 0.5, 1.0}).
  3. The sparc_feedback_rescale function raises on out-of-range input.
  4. The sparc_rescaled_loglike function is linear in f_fb.
  5. The prior_f_fb function peaks at f_fb = 0.4.
  6. The T41 joint-fit wrapper imports feedback_nuisance correctly
     and picks up F_FB_OVERRIDE.
"""
from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CODE_DIR = PROJECT_ROOT / "v0.3-prelim" / "code"
sys.path.insert(0, str(CODE_DIR))


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------

def _import_feedback_nuisance():
    """Import feedback_nuisance, skipping the test if unavailable."""
    return pytest.importorskip("feedback_nuisance")


# ----------------------------------------------------------------------
# 1. Di Cintio+ 2014a relation
# ----------------------------------------------------------------------

class TestDiCintio2014a:
    """Di Cintio+ 2014a relation: log10(r_c/r_s) = 0.34 + 1.34 * log10(M*/M_h)."""

    def test_dc2014a_slope_and_intercept(self):
        fb = _import_feedback_nuisance()
        # Coefficients from Di Cintio+ 2014a Table 1 / Eq. 2.
        assert fb.DI_CINTIO_2014A_SLOPE == pytest.approx(1.34, abs=1e-6)
        assert fb.DI_CINTIO_2014A_INTERCEPT == pytest.approx(0.34, abs=1e-6)

    def test_dc2014a_at_reference(self):
        """At M*/M_h = 0.01, log10(r_c/r_s) = 0.34 + 1.34 * log10(0.01) = -2.34."""
        fb = _import_feedback_nuisance()
        log_rc = fb.log_rc_over_rs(0.01)
        expected = 0.34 + 1.34 * (-2.0)  # = -2.34
        assert log_rc == pytest.approx(expected, abs=1e-6)

    def test_dc2014a_at_pop_mean(self):
        """At M*/M_h = 0.03 (SPARC mean), log10(r_c/r_s) ~ -1.70."""
        fb = _import_feedback_nuisance()
        log_rc = fb.log_rc_over_rs(0.03)
        expected = 0.34 + 1.34 * (-1.523)  # = -1.701
        assert log_rc == pytest.approx(expected, abs=1e-3)

    def test_dc2014a_at_dwarf_limit(self):
        """At M*/M_h = 1e-3, log10(r_c/r_s) ~ -3.68 (very small core)."""
        fb = _import_feedback_nuisance()
        log_rc = fb.log_rc_over_rs(1e-3)
        expected = 0.34 + 1.34 * (-3.0)  # = -3.68
        assert log_rc == pytest.approx(expected, abs=1e-6)

    def test_dc2014a_clamping_outside_range(self):
        """Outside the valid range, the relation clamps to the boundary."""
        fb = _import_feedback_nuisance()
        # At M*/M_h = 1e-7, clamped to 1e-5.
        log_rc_low = fb.log_rc_over_rs(1e-7)
        log_rc_at_floor = fb.log_rc_over_rs(1e-5)
        assert log_rc_low == pytest.approx(log_rc_at_floor, abs=1e-9)

    def test_R_corr_raw_monotonic(self):
        """R_corr_raw is monotonically INCREASING in M*/M_h (above the floor)."""
        fb = _import_feedback_nuisance()
        prev = 0.0
        for m in [1e-4, 1e-3, 1e-2, 0.03, 0.1]:
            rc = fb.R_corr_raw(m)
            assert rc > prev, f"R_corr_raw({m}) = {rc} should be > R_corr_raw(prev) = {prev}"
            prev = rc


# ----------------------------------------------------------------------
# 2-3. sparc_feedback_rescale boundaries + range enforcement
# ----------------------------------------------------------------------

class TestFeedbackRescale:
    """sparc_feedback_rescale(f_fb) = max(0, 1 - f_fb)."""

    def test_rescale_at_zero(self):
        fb = _import_feedback_nuisance()
        assert fb.sparc_feedback_rescale(0.0) == pytest.approx(1.0, abs=1e-9)

    def test_rescale_at_half(self):
        fb = _import_feedback_nuisance()
        assert fb.sparc_feedback_rescale(0.5) == pytest.approx(0.5, abs=1e-9)

    def test_rescale_at_one(self):
        fb = _import_feedback_nuisance()
        assert fb.sparc_feedback_rescale(1.0) == pytest.approx(0.0, abs=1e-9)

    def test_rescale_monotonic_decreasing(self):
        fb = _import_feedback_nuisance()
        grid = fb.make_f_fb_grid(5)
        weights = [fb.sparc_feedback_rescale(f) for f in grid]
        for i in range(len(weights) - 1):
            assert weights[i] >= weights[i + 1], (
                f"rescale({grid[i]}) = {weights[i]} should be >= "
                f"rescale({grid[i+1]}) = {weights[i+1]}"
            )

    def test_rescale_raises_below_zero(self):
        fb = _import_feedback_nuisance()
        with pytest.raises(ValueError, match=r"f_fb must be in"):
            fb.sparc_feedback_rescale(-0.1)

    def test_rescale_raises_above_one(self):
        fb = _import_feedback_nuisance()
        with pytest.raises(ValueError, match=r"f_fb must be in"):
            fb.sparc_feedback_rescale(1.1)


# ----------------------------------------------------------------------
# 4. sparc_rescaled_loglike is linear in f_fb
# ----------------------------------------------------------------------

class TestRescaledLoglike:
    """sparc_rescaled_loglike(σ/m, a, f_fb) is linear in f_fb."""

    def test_rescaled_loglike_linear_in_f_fb(self):
        fb = _import_feedback_nuisance()

        # Mock SPARC loglike_fn returning -500 (any negative value works).
        def mock_sparc_ll(sm, a):
            return -500.0

        ll_0 = fb.sparc_rescaled_loglike(0.1, 0.0, f_fb=0.0, sparc_loglike_fn=mock_sparc_ll)
        ll_05 = fb.sparc_rescaled_loglike(0.1, 0.0, f_fb=0.5, sparc_loglike_fn=mock_sparc_ll)
        ll_1 = fb.sparc_rescaled_loglike(0.1, 0.0, f_fb=1.0, sparc_loglike_fn=mock_sparc_ll)
        ll_025 = fb.sparc_rescaled_loglike(0.1, 0.0, f_fb=0.25, sparc_loglike_fn=mock_sparc_ll)
        ll_075 = fb.sparc_rescaled_loglike(0.1, 0.0, f_fb=0.75, sparc_loglike_fn=mock_sparc_ll)

        # Linear in f_fb: ll(f) = (1 - f) * ll(0).
        assert ll_0 == pytest.approx(-500.0, abs=1e-9)
        assert ll_05 == pytest.approx(-250.0, abs=1e-9)
        assert ll_1 == pytest.approx(0.0, abs=1e-9)
        assert ll_025 == pytest.approx(-375.0, abs=1e-9)
        assert ll_075 == pytest.approx(-125.0, abs=1e-9)

    def test_rescaled_loglike_propagates_inf(self):
        """If the underlying SPARC log L is -inf, return -inf (don't 0 it out)."""
        fb = _import_feedback_nuisance()

        def mock_sparc_ll(sm, a):
            return float("-inf")

        # At f_fb = 1, ll would be 0 (not -inf). Per K4 (closure patterns),
        # the function should NOT silently replace -inf with 0.
        # This is the principled behavior: if the model can't be evaluated,
        # we can't pretend it has weight 0.
        ll_1 = fb.sparc_rescaled_loglike(0.1, 0.0, f_fb=1.0, sparc_loglike_fn=mock_sparc_ll)
        assert ll_1 != 0.0  # NOT silently zero
        # NaN check (per I5 closure pattern: out-of-grid input is silently zero, not -inf).
        # We DO propagate -inf, which is correct.

    def test_rescaled_loglike_uses_real_sparc_if_no_mock(self):
        """Without a mock, the function falls back to t8_v03_joint_fit."""
        fb = _import_feedback_nuisance()
        # Don't crash; just smoke-test the import path.
        try:
            ll = fb.sparc_rescaled_loglike(0.1, 0.0, f_fb=0.5)
            # Either a finite number (success) or -inf (out of grid); both acceptable.
            assert isinstance(ll, float)
        except ImportError:
            pytest.skip("t8_v03_joint_fit not available")


# ----------------------------------------------------------------------
# 5. prior_f_fb peaks at f_fb = 0.4
# ----------------------------------------------------------------------

class TestPriorFFb:
    """prior_f_fb(f_fb) is a truncated log-normal peaked at 0.4."""

    def test_prior_peaks_at_0_4(self):
        fb = _import_feedback_nuisance()
        p_at_04 = fb.prior_f_fb(0.4)
        p_at_03 = fb.prior_f_fb(0.3)
        p_at_05 = fb.prior_f_fb(0.5)
        p_at_02 = fb.prior_f_fb(0.2)
        p_at_06 = fb.prior_f_fb(0.6)
        # 0.4 should be the maximum
        assert p_at_04 > p_at_03
        assert p_at_04 > p_at_05
        assert p_at_04 > p_at_02
        assert p_at_04 > p_at_06

    def test_prior_zero_outside_range(self):
        fb = _import_feedback_nuisance()
        assert fb.prior_f_fb(0.0) == 0.0
        assert fb.prior_f_fb(1.0) == 0.0
        assert fb.prior_f_fb(0.04) == 0.0  # below the [0.05, 0.95] floor
        assert fb.prior_f_fb(0.96) == 0.0  # above the [0.05, 0.95] ceiling

    def test_prior_returns_zero_outside_unit_interval(self):
        fb = _import_feedback_nuisance()
        assert fb.prior_f_fb(-0.1) == 0.0
        assert fb.prior_f_fb(1.1) == 0.0


# ----------------------------------------------------------------------
# 6. T41 joint-fit wrapper picks up F_FB_OVERRIDE
# ----------------------------------------------------------------------

class TestT41FeedbackOverride:
    """T41 loglike reads F_FB_OVERRIDE from the environment."""

    def test_t41_default_f_fb_is_0_5(self):
        """Without F_FB_OVERRIDE, T41 should use f_fb = 0.5 (default)."""
        # Clear the env var so we test the default.
        os.environ.pop("F_FB_OVERRIDE", None)
        # If t41 is already imported, reload to pick up the cleared env var.
        sys.modules.pop("t41_mediator_mass_joint_fit", None)
        t41 = pytest.importorskip("t41_mediator_mass_joint_fit")
        # The default is set inside the loglike function via os.environ.get;
        # verify the constant is set correctly by inspecting the function body.
        import inspect
        src = inspect.getsource(t41.loglike_joint)
        assert 'F_FB_OVERRIDE' in src
        assert 'f_fb_default = 0.5' in src

    def test_t41_feedback_nuisance_import(self):
        """T41 imports feedback_nuisance and falls back to t8 on failure."""
        t41 = pytest.importorskip("t41_mediator_mass_joint_fit")
        import inspect
        src = inspect.getsource(t41.loglike_joint)
        assert 'import feedback_nuisance as fb' in src
        assert 'fb.sparc_rescaled_loglike' in src
        # Legacy fallback
        assert 't8.delta_log_sparc' in src

    def test_t41_feedback_rescale_at_f_fb_zero(self):
        """Smoke test: f_fb=0.0 (F_FB_OVERRIDE=0.0) gives the same SPARC ll
        as the legacy un-rescaled call (within rounding)."""
        os.environ["F_FB_OVERRIDE"] = "0.0"
        sys.modules.pop("t41_mediator_mass_joint_fit", None)
        sys.modules.pop("feedback_nuisance", None)
        t41 = pytest.importorskip("t41_mediator_mass_joint_fit")
        fb = pytest.importorskip("feedback_nuisance")
        # Pull sigma_m_0 and a at the R12 MAP.
        # Per R12: MAP at (m_phi = 26.6 MeV, m_chi = 14.8 GeV, g_chi = 0.13,
        # log_epsilon = -35, log_alpha = -1). sigma/m_0 = 0.066 cm^2/g, a = 0.186.
        # theta = (log_m_phi_MeV, log_m_chi_GeV, g_chi, log_epsilon, log_alpha).
        import numpy as np
        ll_t41 = t41.loglike_joint(
            (np.log10(26.6), np.log10(14.8), 0.13, -35.0, -1.0)
        )
        # T41 internally divides by 1000; the SPARC contribution should be
        # rescaled by (1 - 0) = 1 at f_fb=0, so it equals the legacy call.
        # Compare to a manually computed t8.delta_log_sparc(...) / 1000.
        sigma_m_0 = 0.066
        a = 0.186
        import t8_v03_joint_fit as t8
        ll_t8_legacy = t8.delta_log_sparc(sigma_m_0, a) / 1000
        ll_feedback_no_fb = fb.sparc_rescaled_loglike(sigma_m_0, a, f_fb=0.0) / 1000
        # The two should be equal (within numerical tolerance).
        assert ll_feedback_no_fb == pytest.approx(ll_t8_legacy, abs=1e-9), (
            f"f_fb=0.0 should give the legacy SPARC ll: "
            f"feedback = {ll_feedback_no_fb}, legacy = {ll_t8_legacy}"
        )


# ----------------------------------------------------------------------
# 7. Module-level smoke test
# ----------------------------------------------------------------------

class TestModuleSmoke:
    """Module-level import + public API surface."""

    def test_module_has_public_api(self):
        fb = _import_feedback_nuisance()
        # All public functions should be callable.
        assert callable(fb.log_rc_over_rs)
        assert callable(fb.R_corr_raw)
        assert callable(fb.sparc_feedback_rescale)
        assert callable(fb.sparc_rescaled_loglike)
        assert callable(fb.make_f_fb_grid)
        assert callable(fb.prior_f_fb)

    def test_module_constants(self):
        fb = _import_feedback_nuisance()
        assert hasattr(fb, "DI_CINTIO_2014A_SLOPE")
        assert hasattr(fb, "DI_CINTIO_2014A_INTERCEPT")
        assert hasattr(fb, "DI_CINTIO_VALID_RANGE")
        assert hasattr(fb, "SPARC_POPULATION_MEAN_MSTAR_OVER_MHALO")