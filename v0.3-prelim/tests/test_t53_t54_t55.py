"""
Tests for T53 (dark rho), T54 (dark quark fit), T55 (mixing).
"""
import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
T53_CODE = PROJECT_ROOT / "v0.3-prelim" / "code" / "t53_dark_rho_meson.py"
T54_CODE = PROJECT_ROOT / "v0.3-prelim" / "code" / "t54_dark_quark_joint_fit.py"
T55_CODE = PROJECT_ROOT / "v0.3-prelim" / "code" / "t55_dark_matter_mixing.py"
T54_RESULT = PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "t54_dark_quark_joint_fit.json"
T55_RESULT = PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "t55_dark_matter_mixing.json"


class TestT53DarkRho:
    """T53 — Dark rho meson."""

    def test_t53_importable(self):
        t53 = pytest.importorskip("t53_dark_rho_meson")
        assert hasattr(t53, "dark_rho_mass")
        assert hasattr(t53, "dark_pion_mass")
        assert hasattr(t53, "sigma_m_full")

    def test_t53_pcac_quantitative(self):
        """For m_q = 100 MeV, Lambda_dark = 200 MeV, m_rho should be ~ 500 MeV."""
        t53 = pytest.importorskip("t53_dark_rho_meson")
        m_rho = t53.dark_rho_mass(0.1, 0.2)
        assert 0.4 < m_rho < 0.6, f"m_rho = {m_rho} GeV, expected ~0.49"

    def test_t53_dark_pion_lighter_than_rho(self):
        """Dark pion should be lighter than dark rho (PCAC)."""
        t53 = pytest.importorskip("t53_dark_rho_meson")
        m_q = 0.1
        Lambda_dark = 0.2
        m_rho = t53.dark_rho_mass(m_q, Lambda_dark)
        m_pi = t53.dark_pion_mass(m_q, Lambda_dark)
        assert m_pi < m_rho, f"m_pi = {m_pi} should be < m_rho = {m_rho}"


class TestT54DarkQuarkFit:
    """T54 — Dark quark + dark rho joint fit."""

    def test_t54_importable(self):
        t54 = pytest.importorskip("t54_dark_quark_joint_fit")
        assert hasattr(t54, "loglike_joint")
        assert hasattr(t54, "prior_transform_6")
        assert hasattr(t54, "sigma_m_at_v")

    def test_t54_likelihood_accepts_6d(self):
        t54 = pytest.importorskip("t54_dark_quark_joint_fit")
        ll = t54.loglike_joint((1.0, 2.0, 1.5, 0.5, -4.0, -3.0))
        assert isinstance(ll, (float, int))
        assert ll > -1e10

    def test_t54_sigma_m_close_to_data_target(self):
        """T54's sigma_m_0 should be within 1 order of magnitude of T39's 1.57."""
        if not T54_RESULT.exists():
            pytest.skip("T54 not yet completed")
        with open(T54_RESULT) as f:
            data = json.load(f)
        sigma_m_0 = data["MAP_physical"]["sigma_m_0_derived"]
        T39_target = 1.57
        assert 0.157 < sigma_m_0 < 15.7, (
            f"T54 sigma_m_0 = {sigma_m_0}, target ~ 1.57; should be within 1 order of magnitude"
        )

    def test_t54_a_right_sign(self):
        """T54's a should be > 0 (the data wants a > 0)."""
        if not T54_RESULT.exists():
            pytest.skip("T54 not yet completed")
        with open(T54_RESULT) as f:
            data = json.load(f)
        a = data["MAP_physical"]["a_derived"]
        assert a > 0, f"T54 a = {a}, should be > 0"


class TestT55DarkMatterMixing:
    """T55 — Two-component dark matter."""

    def test_t55_importable(self):
        t55 = pytest.importorskip("t55_dark_matter_mixing")
        assert hasattr(t55, "total_relic_density")
        assert hasattr(t55, "two_component_sidm")

    def test_t55_two_component_sidm(self):
        """Mixed SIDM cross-section should be in the right range."""
        t55 = pytest.importorskip("t55_dark_matter_mixing")
        sigma_eff = t55.two_component_sidm(0.1, 1.36, 0.5, 0.5)
        assert 0.1 < sigma_eff < 1.36, f"Two-component sigma_eff = {sigma_eff}"

    def test_t55_relic_density_scales_correctly(self):
        """Larger m_g should give smaller Omega_g (T50 scaling)."""
        t55 = pytest.importorskip("t55_dark_matter_mixing")
        r_small = t55.total_relic_density(0.05, 0.1, alpha_dark=0.3)
        r_large = t55.total_relic_density(1.0, 0.1, alpha_dark=0.3)
        assert r_small["Omega_glueball"] > r_large["Omega_glueball"]
