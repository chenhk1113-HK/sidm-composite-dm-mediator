"""
Tests for T56-T59 (slope engineering, lattice verification, Boltzmann, dark baryon).
"""
import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
T56_CODE = PROJECT_ROOT / "v0.3-prelim" / "code" / "t56_slope_engineering.py"
T57_CODE = PROJECT_ROOT / "v0.3-prelim" / "code" / "t57_lattice_qcd_verification.py"
T58_CODE = PROJECT_ROOT / "v0.3-prelim" / "code" / "t58_coupled_boltzmann.py"
T59_CODE = PROJECT_ROOT / "v0.3-prelim" / "code" / "t59_dark_baryon.py"


class TestT56SlopeEngineering:
    """T56 — Slope engineering."""

    def test_t56_importable(self):
        t56 = pytest.importorskip("t56_slope_engineering")
        assert hasattr(t56, "sigma_m_combined")
        assert hasattr(t56, "derived_a")

    def test_t56_a_can_match_target(self):
        """Some parameter combination should give a close to 0.94."""
        t56 = pytest.importorskip("t56_slope_engineering")
        # Scan a small range
        found_a = False
        for m_phi_MeV in [50, 100, 200]:
            for m_DM_GeV in [50, 100, 500]:
                for g_chi in [0.5, 1.0, 1.5]:
                    m_phi_GeV = m_phi_MeV / 1000.0
                    a = t56.derived_a(m_phi_GeV, m_DM_GeV, g_chi, R_fm=0.0)
                    if abs(a - 0.94) < 0.2:
                        found_a = True
                        break
        assert found_a, "Could not find a close to 0.94"


class TestT57LatticeVerification:
    """T57 — Lattice QCD verification."""

    def test_t57_importable(self):
        t57 = pytest.importorskip("t57_lattice_qcd_verification")
        assert hasattr(t57, "LATTICE_DATA")
        assert hasattr(t57, "verify_pcac_relation")

    def test_t57_lattice_data_present(self):
        """Lattice data should include Morningstar-Peardon 1999."""
        t57 = pytest.importorskip("t57_lattice_qcd_verification")
        titles = list(t57.LATTICE_DATA.keys())
        assert any("Morningstar" in t for t in titles), "Missing Morningstar-Peardon 1999"
        assert any("DeGrand" in t for t in titles), "Missing DeGrand-Schaefer"


class TestT58CoupledBoltzmann:
    """T58 — Coupled Boltzmann."""

    def test_t58_importable(self):
        t58 = pytest.importorskip("t58_coupled_boltzmann")
        assert hasattr(t58, "coupled_boltzmann")

    def test_t58_relic_density_positive(self):
        """Both components should give positive relic density."""
        t58 = pytest.importorskip("t58_coupled_boltzmann")
        r = t58.coupled_boltzmann(0.1, 0.5, 0.2)
        assert r["Omega_g"] >= 0
        assert r["Omega_rho"] >= 0


class TestT59DarkBaryon:
    """T59 — Dark baryon."""

    def test_t59_importable(self):
        t59 = pytest.importorskip("t59_dark_baryon")
        assert hasattr(t59, "dark_baryon_mass")
        assert hasattr(t59, "asymmetric_relic")

    def test_t59_dark_baryon_mass_scaling(self):
        """For larger N_dark, m_B should scale linearly."""
        t59 = pytest.importorskip("t59_dark_baryon")
        Lambda_dark_GeV = 0.1
        m_B_3 = t59.dark_baryon_mass(3, Lambda_dark_GeV)
        m_B_6 = t59.dark_baryon_mass(6, Lambda_dark_GeV)
        assert abs(m_B_6 / m_B_3 - 2.0) < 0.01, "m_B should scale linearly with N_dark"

    def test_t59_asymmetric_relic(self):
        """Asymmetric relic density should be in the right range for the right m_B."""
        t59 = pytest.importorskip("t59_dark_baryon")
        Omega = t59.asymmetric_relic(0.5, eta_B_dark=1e-9)
        # Should be around 0.1
        assert 0.01 < Omega < 1.0, f"Omega h^2 = {Omega} should be ~ 0.1"