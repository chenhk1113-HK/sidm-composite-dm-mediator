"""
Tests for T43 (iDM), T44 (publication plot), T45 (CMB+BBN).
"""
import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
T43_CODE = PROJECT_ROOT / "v0.3-prelim" / "code" / "t43_inelastic_dm.py"
T43_FIT_CODE = PROJECT_ROOT / "v0.3-prelim" / "code" / "t43_inelastic_joint_fit.py"
T44_CODE = PROJECT_ROOT / "v0.3-prelim" / "code" / "t44_publication_plot.py"
T45_CODE = PROJECT_ROOT / "v0.3-prelim" / "code" / "t45_cmb_bbn.py"
T43_RESULT = PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "t43_inelastic_dm_joint_fit.json"
T45_RESULT = PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "t45_cmb_bbn_exclusions.json"


class TestT43iDM:
    """T43 — Inelastic DM cross-section."""

    def test_t43_importable(self):
        t43 = pytest.importorskip("t43_inelastic_dm")
        assert hasattr(t43, "sigma_m_inelastic")
        assert hasattr(t43, "inelastic_suppression")
        assert hasattr(t43, "v_threshold_km_s")
        assert hasattr(t43, "derived_a_inelastic")

    def test_t43_elastic_limit(self):
        """At delta = 0, iDM should reduce to T40 Yukawa."""
        t43 = pytest.importorskip("t43_inelastic_dm")
        import t40_yukawa_sigma_m as yukawa
        sm_inel = t43.sigma_m_inelastic(100.0, 100.0, 40.0, 0.5, 0.0)
        sm_yuk = yukawa.sigma_m_cm2_per_g(100.0, 100.0, 40.0, 0.5)
        assert abs(sm_inel - sm_yuk) / sm_yuk < 1e-6, (
            f"iDM at delta=0 ({sm_inel}) should equal Yukawa ({sm_yuk})"
        )

    def test_t43_threshold_velocity(self):
        """v_threshold should be physically reasonable for delta in 0.1-10 MeV."""
        t43 = pytest.importorskip("t43_inelastic_dm")
        v_thr = t43.v_threshold_km_s(1.0, 40.0)
        # (1) m_chi_GeV * 1000 = m_chi_MeV; (1/2) m_chi v^2 = delta
        # v = c * sqrt(2 delta_MeV / m_chi_MeV)
        # Should be ~ 2000 km/s for delta=1 MeV, m_chi=40 GeV
        assert 1000 < v_thr < 5000, f"v_threshold = {v_thr:.1f} km/s out of range"

    def test_t43_inelastic_suppression(self):
        """At v << v_threshold, F_inel should be small."""
        t43 = pytest.importorskip("t43_inelastic_dm")
        # delta = 1 MeV, m_chi = 40 GeV: v_thr ~ 2120 km/s
        # v = 100 km/s (well below threshold)
        F = t43.inelastic_suppression(100.0, 1.0, 40.0)
        assert F < 0.01, f"F_inel at v=100 should be small, got {F}"


class TestT43Fit:
    """T43 — Inelastic DM joint fit."""

    def test_t43_fit_importable(self):
        t43 = pytest.importorskip("t43_inelastic_joint_fit")
        assert hasattr(t43, "loglike_joint")
        assert hasattr(t43, "prior_transform_6")
        assert hasattr(t43, "main")

    def test_t43_fit_6d_prior(self):
        t43 = pytest.importorskip("t43_inelastic_joint_fit")
        # delta range should be in 1 keV - 10 MeV
        assert (t43.LOG_DELTA_MEV_RANGE[0] <= -2.0 and
                t43.LOG_DELTA_MEV_RANGE[1] >= 0.0), (
            "log_delta_MeV prior must cover at least 10 keV to 1 MeV"
        )

    def test_t43_fit_likelihood_accepts_6d_theta(self):
        t43 = pytest.importorskip("t43_inelastic_joint_fit")
        # log_m_phi=2, log_m_chi=1.5, g_chi=0.5, log_delta=-1, log_eps=-4, log_alpha=-3
        ll = t43.loglike_joint((2.0, 1.5, 0.5, -1.0, -4.0, -3.0))
        assert isinstance(ll, (float, int))
        assert ll > -1e10

    def test_t43_fit_sigma_m_0_matches_T39(self):
        """T43 iDM should approximately match T39 sigma_m_0 (1.57 cm^2/g)."""
        if not T43_RESULT.exists():
            pytest.skip("T43 fit not yet completed")
        with open(T43_RESULT) as f:
            data = json.load(f)
        sigma_m_0 = data["MAP_physical"]["sigma_m_0_derived"]
        T39_target = 1.57
        assert abs(sigma_m_0 - T39_target) / T39_target < 0.5, (
            f"T43 sigma_m_0 = {sigma_m_0}, target = {T39_target}; "
            "iDM should approximately match T39's anchored value"
        )


class TestT45CMBBBN:
    """T45 — CMB + BBN exclusion contours."""

    def test_t45_importable(self):
        t45 = pytest.importorskip("t45_cmb_bbn")
        assert hasattr(t45, "CMB_BBN_UPPER_95CL")
        assert hasattr(t45, "interpolate_cmb_bbn")
        assert hasattr(t45, "is_cmb_bbn_excluded")

    def test_t45_low_mphi_excludes_strongly(self):
        """At m_phi < 1 MeV with high epsilon, CMB+BBN should exclude."""
        t45 = pytest.importorskip("t45_cmb_bbn")
        # m_phi = 0.1 MeV, epsilon = 10^-5 (above the limit)
        assert t45.is_cmb_bbn_excluded(0.1, -5.0), "Should be excluded at high eps"

    def test_t45_t41_unobservable(self):
        """T41 posterior median should NOT be excluded by CMB+BBN."""
        if not T45_RESULT.exists():
            pytest.skip("T45 not yet completed")
        with open(T45_RESULT) as f:
            data = json.load(f)
        t41_eval = data.get("t41_evaluation", {})
        if "is_excluded" not in t41_eval:
            pytest.skip("T41 evaluation not done")
        assert not t41_eval["is_excluded"], (
            "T41 posterior at median should be invisible to CMB+BBN. "
            "If T41 is excluded, the model is in cosmological tension."
        )
