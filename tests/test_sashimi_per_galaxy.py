"""
Tests for sashimi_per_galaxy.py — per-galaxy SASHIMI-SIDM forward model.
"""
from __future__ import annotations
import sys
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "v0.3-prelim" / "code"))

from sashimi_per_galaxy import (
    V_SIDM,
    predict_rotation_curve_sashimi,
    chi2_per_galaxy,
    load_sparc_galaxy,
)
from sashimi_parametric import predict_sparc_satellite as predict_sparc_satellite_compat


class TestVSIDM:
    """SIDM rotation curve V²(r)."""

    def test_V_squared_zero_at_zero_radius(self):
        """V²(0) → 0 (by construction; we set V²(0)=0 for r=0)."""
        r = np.array([0.001, 0.01, 0.1])
        V2 = V_SIDM(r, rho_s_sidm=1e7, r_s_sidm=1.0, r_c_sidm=0.5)
        # At very small r, V² should be tiny (linear in r for cored profile)
        assert V2[0] < 1e-3

    def test_V_squared_rises_then_falls(self):
        """V²(r) should rise at small r, peak, then decline (NFW-like outer)."""
        r = np.linspace(0.1, 50.0, 100)
        V2 = V_SIDM(r, rho_s_sidm=1e7, r_s_sidm=5.0, r_c_sidm=1.0)
        # Find peak
        i_max = np.argmax(V2)
        # V² should be increasing before peak and decreasing after
        assert i_max > 5  # not at the very first point
        assert i_max < 90  # not at the very last point
        assert V2[i_max] > V2[0]
        assert V2[i_max] > V2[-1]

    def test_higher_rho_s_higher_V_max(self):
        """Higher ρ_s → higher V_max (linearly in ρ_s at fixed r_s, r_c)."""
        r = np.array([5.0])
        V2_low = V_SIDM(r, rho_s_sidm=1e6, r_s_sidm=1.0, r_c_sidm=0.5)
        V2_high = V_SIDM(r, rho_s_sidm=1e8, r_s_sidm=1.0, r_c_sidm=0.5)
        # V² ∝ ρ_s at fixed r, r_c → V²_high should be ~100× larger
        assert V2_high[0] > 50 * V2_low[0]


class TestPredictRotationCurve:
    """End-to-end forward model."""

    def test_predict_returns_positive_V_squared(self):
        r = np.array([1.0, 5.0, 10.0])
        V2 = predict_rotation_curve_sashimi(r, M_vir_Msun=1e12, c_vir=10.0,
                                              sigma_0_per_m_chi_cm2_per_g=1.0)
        assert np.all(V2 > 0)

    def test_predict_higher_sigma_higher_V_max(self):
        """Higher σ/m → slightly higher V_max (more concentrated core collapse)."""
        r = np.array([10.0])
        V2_low = predict_rotation_curve_sashimi(r, 1e12, 10.0, sigma_0_per_m_chi_cm2_per_g=0.1)
        V2_high = predict_rotation_curve_sashimi(r, 1e12, 10.0, sigma_0_per_m_chi_cm2_per_g=10.0)
        # Both should be positive; high sigma should give equal or higher V²
        assert V2_high[0] >= V2_low[0]


class TestChi2PerGalaxy:
    """χ² for one galaxy."""

    def test_perfect_match_chi2_zero(self):
        """If predicted V² matches observed V², χ² = 0."""
        # Create synthetic observation = prediction
        r_obs = np.array([1.0, 3.0, 10.0])
        V2_pred = predict_rotation_curve_sashimi(r_obs, 1e12, 10.0,
                                                  sigma_0_per_m_chi_cm2_per_g=1.0)
        V2_err = V2_pred * 0.1
        chi2 = chi2_per_galaxy(r_obs, V2_pred, V2_err, 1e12, 10.0, 1.0)
        assert chi2 < 1e-6  # Should be ~0 (numerical noise)

    def test_wrong_sigma_higher_chi2(self):
        """Wrong σ/m should give higher χ² than correct σ/m."""
        r_obs = np.array([1.0, 3.0, 10.0])
        V2_true = predict_rotation_curve_sashimi(r_obs, 1e12, 10.0,
                                                  sigma_0_per_m_chi_cm2_per_g=1.0)
        V2_err = V2_true * 0.1
        chi2_correct = chi2_per_galaxy(r_obs, V2_true, V2_err, 1e12, 10.0, 1.0)
        chi2_wrong = chi2_per_galaxy(r_obs, V2_true, V2_err, 1e12, 10.0, 100.0)
        assert chi2_wrong > chi2_correct

    def test_load_real_sparc_galaxy(self):
        """Verify we can load a real SPARC rotmod file."""
        import os
        # Try Windows path first, then WSL path
        candidates = [
            r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.1-prelim\data\Rotmod_LTG\NGC2403_rotmod.dat",
            "/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.1-prelim/data/Rotmod_LTG/NGC2403_rotmod.dat",
            "/home/lamkuenai/sidm-composite-dm-mediator/v0.1-prelim/data/Rotmod_LTG/NGC2403_rotmod.dat",
        ]
        rotmod_path = None
        for p in candidates:
            if os.path.exists(p):
                rotmod_path = p
                break
        if rotmod_path is None:
            import pytest
            pytest.skip("SPARC rotmod file not accessible")
        r, V2, V2_err = load_sparc_galaxy(rotmod_path)
        assert len(r) >= 5  # NGC2403 has many data points
        assert np.all(V2 > 0)
        assert np.all(V2_err > 0)