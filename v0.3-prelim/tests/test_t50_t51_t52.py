"""
Tests for T50 (relic density), T51 (self-interaction), T52 (Sommerfeld).
"""
import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
T50_CODE = PROJECT_ROOT / "v0.3-prelim" / "code" / "t50_dark_glueball_relic.py"
T51_CODE = PROJECT_ROOT / "v0.3-prelim" / "code" / "t51_dark_glueball_self_interaction.py"
T52_CODE = PROJECT_ROOT / "v0.3-prelim" / "code" / "t52_glueball_sommerfeld.py"
T50_RESULT = PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "t50_dark_glueball_relic.json"
T51_RESULT = PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "t51_dark_glueball_self_interaction.json"
T52_RESULT = PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "t52_glueball_sommerfeld.json"


class TestT50RelicDensity:
    """T50 — Dark glueball relic density."""

    def test_t50_importable(self):
        t50 = pytest.importorskip("t50_dark_glueball_relic")
        assert hasattr(t50, "relic_density_3to2")
        assert hasattr(t50, "scan_relic_density")

    def test_t50_omega_h2_in_observable_range(self):
        """For T41 parameters, Omega h^2 should be in the observable range."""
        t50 = pytest.importorskip("t50_dark_glueball_relic")
        # T41: m_phi = 212 MeV, alpha_dark = 0.1
        r = t50.relic_density_3to2(0.212, alpha_dark=0.1, N_dark=3)
        # Should be in a reasonable range (e.g., 0.01 to 1.0)
        assert 0.01 < r["Omega_h2"] < 1.0, f"Omega h^2 = {r['Omega_h2']} out of expected range"

    def test_t50_alpha_dark_target_found(self):
        """The find_alpha_for_target function should find a reasonable alpha_dark."""
        t50 = pytest.importorskip("t50_dark_glueball_relic")
        alpha, r = t50.find_alpha_for_target(212, target_Omega_h2=0.12)
        assert 0.01 < alpha < 10.0, f"alpha_dark = {alpha} out of expected range"


class TestT51SelfInteraction:
    """T51 — Dark glueball self-interaction."""

    def test_t51_importable(self):
        t51 = pytest.importorskip("t51_dark_glueball_self_interaction")
        assert hasattr(t51, "sigma_elastic")
        assert hasattr(t51, "sigma_3to2")

    def test_t51_cross_section_positive(self):
        """Elastic cross-section should be positive."""
        t51 = pytest.importorskip("t51_dark_glueball_self_interaction")
        sm = t51.sigma_elastic(100.0, 0.212)
        assert sm > 0, f"sigma/m = {sm} should be positive"

    def test_t51_T41_close_to_data(self):
        """T41 (m_phi = 212 MeV) cross-section should be within 2 orders of data target."""
        t51 = pytest.importorskip("t51_dark_glueball_self_interaction")
        sm = t51.sigma_elastic(100.0, 0.212)
        # Within 2 orders of magnitude of 1.57 cm^2/g
        # i.e., between 0.0157 and 157 cm^2/g
        assert 0.0157 < sm < 157, (
            f"T41 sigma/m = {sm} cm^2/g, should be within 2 orders of 1.57"
        )


class TestT52Sommerfeld:
    """T52 — Dark glueball Sommerfeld (dilaton)."""

    def test_t52_importable(self):
        t52 = pytest.importorskip("t52_glueball_sommerfeld")
        assert hasattr(t52, "sigma_m_dilaton_elastic")
        assert hasattr(t52, "sigma_m_with_three_to_two")
        assert hasattr(t52, "derived_a_glueball")

    def test_t52_dilaton_smaller_than_data(self):
        """Dilaton-mediated cross-section should be SMALLER than data target."""
        t52 = pytest.importorskip("t52_glueball_sommerfeld")
        sm = t52.sigma_m_dilaton_elastic(100.0, 0.212)
        # Should be < 1.57 cm^2/g (glueball is too weakly interacting)
        assert sm < 1.57, f"Dilaton sigma/m = {sm} should be < 1.57"

    def test_t52_3to2_enhancement(self):
        """3-to-2 enhancement should grow the cross-section."""
        t52 = pytest.importorskip("t52_glueball_sommerfeld")
        sm_elastic = t52.sigma_m_dilaton_elastic(100.0, 0.212)
        sm_3to2 = t52.sigma_m_with_three_to_two(100.0, 0.212, alpha_dark=0.3)
        assert sm_3to2 > sm_elastic, "3-to-2 should enhance the cross-section"
