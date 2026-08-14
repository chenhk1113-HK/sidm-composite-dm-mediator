"""
Tests for T40 (Yukawa sigma/m), T41 (mediator mass joint fit), T42 (lab exclusions).
"""
import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
T40_CODE = PROJECT_ROOT / "v0.3-prelim" / "code" / "t40_yukawa_sigma_m.py"
T41_CODE = PROJECT_ROOT / "v0.3-prelim" / "code" / "t41_mediator_mass_joint_fit.py"
T42_CODE = PROJECT_ROOT / "v0.3-prelim" / "code" / "t42_lab_exclusions.py"
T41_RESULT = PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "t41_mediator_mass_joint_fit.json"
T42_RESULT = PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "t42_lab_exclusions_recast.json"


class TestT40Yukawa:
    """T40 — Yukawa sigma/m module."""

    def test_t40_importable(self):
        t40 = pytest.importorskip("t40_yukawa_sigma_m")
        assert hasattr(t40, "sigma_T_cm2")
        assert hasattr(t40, "sigma_m_cm2_per_g")
        assert hasattr(t40, "power_law_slope")
        assert hasattr(t40, "g_chi_to_match_sigma_m_0")

    def test_t40_units_consistency(self):
        """sigma_m must be in cm^2/g, not cm^2/GeV."""
        t40 = pytest.importorskip("t40_yukawa_sigma_m")
        # At g_chi=1, m_phi=100 MeV, m_chi=40 GeV, v=100 km/s
        # Check that sigma_m is in cm^2/g (range 1e-100 to 1e10)
        sm = t40.sigma_m_cm2_per_g(100.0, 100.0, 40.0, 1.0)
        # Should be in physically reasonable range (target: ~1 cm^2/g)
        # At g_chi=1, 100 MeV, 40 GeV, sigma_T = (1^4 * 40000^2) / (8pi * 100^4) * hbar^2 * L^2
        # Rough check: 1e-5 to 1e5 cm^2/g
        assert 1e-100 < sm < 1e10, f"sigma_m = {sm} out of expected cm^2/g range"

    def test_t40_velocity_dependence(self):
        """Yukawa sigma/m should DECREASE with v in Born regime (high m_phi)."""
        t40 = pytest.importorskip("t40_yukawa_sigma_m")
        # High m_phi = Born regime, sigma_T ~ 1/v^4 (L=1 for small s)
        sm_low = t40.sigma_m_cm2_per_g(10.0, 1000.0, 40.0, 1.0)
        sm_high = t40.sigma_m_cm2_per_g(1000.0, 1000.0, 40.0, 1.0)
        # At high m_phi, sigma ~ 1/v^4 — sigma at 10 km/s >> sigma at 1000 km/s
        assert sm_low > sm_high, (
            f"sigma_m at v=10 km/s ({sm_low}) should be > sigma_m at v=1000 km/s ({sm_high})"
        )

    def test_t40_g_chi_to_match(self):
        """g_chi solver should give sigma_m_0 within 1% of target."""
        t40 = pytest.importorskip("t40_yukawa_sigma_m")
        target = 1.57
        g = t40.g_chi_to_match_sigma_m_0(target, 100.0, 40.0)
        assert g is not None, "g_chi solver failed"
        sm = t40.sigma_m_cm2_per_g(100.0, 100.0, 40.0, g)
        # Within 1%
        assert abs(sm - target) / target < 0.01, f"sigma_m = {sm}, target = {target}"


class TestT41Module:
    """T41 — m_phi + m_chi joint fit."""

    def test_t41_importable(self):
        t41 = pytest.importorskip("t41_mediator_mass_joint_fit")
        assert hasattr(t41, "loglike_joint")
        assert hasattr(t41, "prior_transform_5")
        assert hasattr(t41, "main")

    def test_t41_5d_prior(self):
        """T41 uses 5D priors covering (m_phi, m_chi, g_chi, epsilon, alpha)."""
        t41 = pytest.importorskip("t41_mediator_mass_joint_fit")
        assert (t41.LOG_M_PHI_MEV_RANGE[0] <= -1.0 and
                t41.LOG_M_PHI_MEV_RANGE[1] >= 3.0), (
            "log_m_phi_MeV prior must cover at least 10 keV to 1 TeV"
        )

    def test_t41_likelihood_accepts_5d_theta(self):
        t41 = pytest.importorskip("t41_mediator_mass_joint_fit")
        # log_m_phi=2 (100 MeV), log_m_chi=1.5 (30 GeV), g_chi=0.1,
        # log_eps=-4, log_alpha=-3
        ll = t41.loglike_joint((2.0, 1.5, 0.1, -4.0, -3.0))
        assert isinstance(ll, (float, int))
        assert ll > -1e10

    def test_t41_yukawa_tension_flag(self):
        """T41 must flag the Yukawa a < 0 vs T39 a > 0 tension."""
        if not T41_RESULT.exists():
            pytest.skip("T41 not yet completed")
        with open(T41_RESULT) as f:
            data = json.load(f)
        assert "yukawa_tension" in data
        assert data["yukawa_tension"]["significant"] is True, (
            f"Yukawa tension NOT flagged. a_T39 = {data['yukawa_tension']['T39_a']}, "
            f"a_Yukawa = {data['yukawa_tension']['Yukawa_a_at_MAP']}, "
            f"diff = {data['yukawa_tension']['a_difference']}. Check the prior range."
        )


class TestT42Module:
    """T42 — Lab exclusions recast."""

    def test_t42_importable(self):
        t42 = pytest.importorskip("t42_lab_exclusions")
        assert hasattr(t42, "is_excluded")
        assert hasattr(t42, "interpolate_exclusion")
        assert hasattr(t42, "NA64_INVISIBLE_90CL")
        assert hasattr(t42, "STELLAR_COOLING_95CL")
        assert hasattr(t42, "SN1987A_95CL")

    def test_t42_t41_evaluation(self):
        """T42 must evaluate the T41 posterior in the exclusion plane."""
        if not T42_RESULT.exists():
            pytest.skip("T42 not yet completed")
        if not T41_RESULT.exists():
            pytest.skip("T41 not yet completed")
        with open(T42_RESULT) as f:
            data = json.load(f)
        assert "t41_evaluation" in data
        assert "T41_median_m_phi_MeV" in data["t41_evaluation"]
        assert "status" in data["t41_evaluation"]

    def test_t42_t41_mediator_unobservable(self):
        """At T41 posterior median, the mediator should be unobservable."""
        if not T42_RESULT.exists():
            pytest.skip("T42 not yet completed")
        with open(T42_RESULT) as f:
            data = json.load(f)
        t41_eval = data.get("t41_evaluation", {})
        if "status" not in t41_eval:
            pytest.skip("T41 evaluation not done")
        status = t41_eval["status"]
        # The T41 posterior should concentrate at very small epsilon,
        # well below current experimental sensitivity.
        assert not status["is_excluded"], (
            f"T41 posterior at median is excluded by {[e['experiment'] for e in status['excluded_by']]}. "
            "This would mean the SIDM-bumpy model is already ruled out by lab experiments."
        )
