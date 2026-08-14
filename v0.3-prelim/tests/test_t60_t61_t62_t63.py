"""
Tests for T60-T63.
"""
import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
T60_CODE = PROJECT_ROOT / "v0.3-prelim" / "code" / "t60_chiral_log_corrections.py"
T61_CODE = PROJECT_ROOT / "v0.3-prelim" / "code" / "t61_depletion_mechanisms.py"
T62_CODE = PROJECT_ROOT / "v0.3-prelim" / "code" / "t62_lz_direct_detection.py"
T63_CODE = PROJECT_ROOT / "v0.3-prelim" / "code" / "t63_dark_rho_decay.py"


class TestT60ChiralLog:
    """T60 — Chiral log corrections."""

    def test_t60_importable(self):
        t60 = pytest.importorskip("t60_chiral_log_corrections")
        assert hasattr(t60, "m_pi_LO")
        assert hasattr(t60, "m_pi_with_chiral_log")
        assert hasattr(t60, "m_rho_with_chiral_log")

    def test_t60_pion_mass_positive(self):
        t60 = pytest.importorskip("t60_chiral_log_corrections")
        m_pi = t60.m_pi_LO(0.1, 0.2)
        assert m_pi > 0


class TestT61Depletion:
    """T61 — Depletion mechanisms."""

    def test_t61_importable(self):
        t61 = pytest.importorskip("t61_depletion_mechanisms")
        assert hasattr(t61, "omega_asymmetric")
        assert hasattr(t61, "omega_with_4to2")
        assert hasattr(t61, "omega_boltzmann_suppression")

    def test_t61_4to2_suppresses(self):
        """4-to-2 cannibalism should reduce Omega_g."""
        t61 = pytest.importorskip("t61_depletion_mechanisms")
        Omega_low_alpha = t61.omega_with_4to2(1.0, 0.1)
        Omega_high_alpha = t61.omega_with_4to2(1.0, 0.5)
        # Higher alpha should give lower Omega (more cannibalism)
        assert Omega_high_alpha < Omega_low_alpha


class TestT62LZDirect:
    """T62 — LZ direct detection."""

    def test_t62_importable(self):
        t62 = pytest.importorskip("t62_lz_direct_detection")
        assert hasattr(t62, "sigma_DM_n")
        assert hasattr(t62, "LZ_limit")

    def test_t62_LZ_limit_positive(self):
        t62 = pytest.importorskip("t62_lz_direct_detection")
        L = t62.LZ_limit(30.0)
        assert L > 0

    def test_t62_sigma_increases_with_epsilon(self):
        """Direct-detection cross-section should grow with epsilon^2."""
        t62 = pytest.importorskip("t62_lz_direct_detection")
        s1 = t62.sigma_DM_n(34.0, 0.003, 1e-30)
        s2 = t62.sigma_DM_n(34.0, 0.003, 1e-20)
        assert s2 > s1, "Cross-section should grow with epsilon"


class TestT63Decay:
    """T63 — Dark rho decay modes."""

    def test_t63_importable(self):
        t63 = pytest.importorskip("t63_dark_rho_decay")
        assert hasattr(t63, "BR_visible_to_ee")
        assert hasattr(t63, "BR_invisible_to_pions")
        assert hasattr(t63, "total_width")

    def test_t63_threshold_open_close(self):
        """If m_rho < 2*m_e, BR_ee should be 0."""
        t63 = pytest.importorskip("t63_dark_rho_decay")
        # m_rho = 1 MeV = 0.001 GeV, below 2m_e = 0.00102 GeV
        BR = t63.BR_visible_to_ee(0.001, 1e-5)
        assert BR == 0, f"BR should be 0 below threshold, got {BR}"

    def test_t63_invisible_above_threshold(self):
        """If m_rho > 2*m_pi, BR_pi_pi should be positive."""
        t63 = pytest.importorskip("t63_dark_rho_decay")
        BR = t63.BR_invisible_to_pions(0.5, 0.1, alpha_dark=0.3)
        assert BR > 0