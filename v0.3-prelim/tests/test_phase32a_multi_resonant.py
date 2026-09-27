"""
Tests for Phase 32a (multi-resonant dark QCD implementation).
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "code"))

import numpy as np


class TestMultiResonant:
    """Test the multi-resonance architecture."""

    def test_breit_wigner_factor_at_peak(self):
        """BW factor should be 1.0 at the peak velocity."""
        from t90_v70_multi_resonant_darkqcd import breit_wigner_factor
        m_chi = 6.09
        E_R = 13.28  # eV (Cloud-9)
        Gamma = 0.66
        # v_target such that E_CM = E_R
        from t90_v50_resonant_sidm import kinetic_energy_eV
        v_target = 28.0  # km/s, matches E_R for m_chi=6.09
        factor = breit_wigner_factor(v_target, m_chi, E_R, Gamma)
        assert factor == pytest.approx(1.0, rel=1e-3)

    def test_breit_wigner_factor_far_from_peak(self):
        """BW factor should be very small far from peak."""
        from t90_v70_multi_resonant_darkqcd import breit_wigner_factor
        m_chi = 6.09
        E_R = 13.28
        Gamma = 0.66
        factor = breit_wigner_factor(300, m_chi, E_R, Gamma)
        assert factor < 0.01  # very small at v=300

    def test_default_resonances_have_4_resonances(self):
        """Default config should have 4 resonances."""
        from t90_v70_multi_resonant_darkqcd import build_default_resonances
        resonances = build_default_resonances(6.09)
        assert len(resonances) == 4

    def test_default_resonances_have_natural_widths(self):
        """Resonance widths should be reasonable fraction of E_R."""
        from t90_v70_multi_resonant_darkqcd import build_default_resonances
        resonances = build_default_resonances(6.09)
        for r in resonances:
            ratio = r["Gamma_eV"] / r["E_R_eV"]
            assert 0.01 < ratio < 0.2  # 1-20% widths

    def test_velocity_dependent_background(self):
        """Background should drop with velocity."""
        from t90_v70_multi_resonant_darkqcd import velocity_dependent_background
        sig_10 = velocity_dependent_background(10, 1.0, 0.7)
        sig_100 = velocity_dependent_background(100, 1.0, 0.7)
        sig_1000 = velocity_dependent_background(1000, 1.0, 0.7)
        assert sig_10 > sig_100 > sig_1000
        assert sig_10 > sig_100  # dwarfs get more interaction than galaxies

    def test_multi_resonant_passes_all_critical_velocities(self):
        """All 11 test velocities should pass with default config."""
        from t90_v70_multi_resonant_darkqcd import (
            build_default_resonances, sigma_m_multi_resonant,
            velocity_dependent_background,
        )
        m_chi = 6.09
        sigma_0_dwarf = 0.3
        a_slope = 0.7
        resonances = build_default_resonances(m_chi)

        # Target ranges for each system
        targets = {
            10.0: (0.5, 5.0),     # dwarf
            12.0: (0.5, 5.0),
            15.0: (0.5, 5.0),
            28.0: (30.0, 500.0),  # Cloud-9
            100.0: (0.03, 0.5),   # SPARC
            200.0: (0.01, 1.0),   # MW sat
            250.0: (0.05, 1.0),   # stream
            300.0: (0.05, 1.0),
            1000.0: (0.001, 0.1), # cluster
            3000.0: (0.0001, 0.1),# bullet
        }
        for v, (low, high) in targets.items():
            sigma_0_v = velocity_dependent_background(v, sigma_0_dwarf, a_slope)
            result = sigma_m_multi_resonant(v, m_chi, resonances, sigma_0_v, 0.0)
            sm = result["sigma_m_total"]
            assert low <= sm <= high, f"v={v}: sigma/m={sm} not in [{low},{high}]"

    def test_cloud9_specifically_satisfied(self):
        """Cloud-9 should be at sigma/m ~ 100, NOT in the dwarf band."""
        from t90_v70_multi_resonant_darkqcd import (
            build_default_resonances, sigma_m_multi_resonant,
            velocity_dependent_background,
        )
        m_chi = 6.09
        resonances = build_default_resonances(m_chi)
        sigma_0_v = velocity_dependent_background(28.0, 0.3, 0.7)
        result = sigma_m_multi_resonant(28.0, m_chi, resonances, sigma_0_v, 0.0)
        sm = result["sigma_m_total"]
        assert 30 <= sm <= 500, f"Cloud-9 sigma/m={sm} not in [30, 500]"

    def test_dwarfs_not_overrun_by_resonances(self):
        """Dwarf cores should be from background, not resonance tail."""
        from t90_v70_multi_resonant_darkqcd import (
            build_default_resonances, sigma_m_multi_resonant,
            velocity_dependent_background,
        )
        m_chi = 6.09
        resonances = build_default_resonances(m_chi)
        # Test dwarfs at v=10, 12, 15
        for v in [10.0, 12.0, 15.0]:
            sigma_0_v = velocity_dependent_background(v, 0.3, 0.7)
            result = sigma_m_multi_resonant(v, m_chi, resonances, sigma_0_v, 0.0)
            sm = result["sigma_m_total"]
            # Should be in dwarf-friendly range (NOT cloud-9's 100+)
            assert sm < 10.0, f"Dwarf at v={v}: sigma/m={sm} too high (would overshoot cores)"