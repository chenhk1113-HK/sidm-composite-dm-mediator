"""Tests for the lattice-informed dark-rho mass (T53b, R11 G14)."""
from __future__ import annotations
import sys
from pathlib import Path

WSL_ROOT = Path("/home/lamkuenai/sidm-composite-dm-mediator")
sys.path.insert(0, str(WSL_ROOT / "v0.3-prelim/code"))

import t53b_lattice_input as t53b


def test_qcd_physical_point_recovered():
    """For Lambda = f_pi = 92 MeV and SU(3) N_f=3 fundamental,
    m_rho should be ~ 770 MeV (PDG physical value)."""
    info = t53b.dark_rho_mass_lattice(
        m_q_GeV=0.003,  # m_q ~ 3 MeV (QCD-like, very light)
        Lambda_dark_GeV=0.09207,  # f_pi for QCD
        N_dc=3, N_f=3,
    )
    # With f_pi = Lambda = 0.09207 GeV and ratio 8.36:
    # m_rho = 8.36 * 0.09207 = 0.770 GeV
    assert 0.75 < info["m_rho_GeV"] < 0.79, (
        f"m_rho {info['m_rho_GeV']*1000:.1f} MeV not near PDG 770 MeV"
    )
    print(f"OK: QCD physical point: m_rho = {info['m_rho_GeV']*1000:.1f} MeV")


def test_ratio_returns_correct_value():
    """m_rho_over_f_pi for SU(3) N_f=3 should be 8.36."""
    ratio, err, ref = t53b.m_rho_over_f_pi(N_dc=3, N_f=3)
    assert 8.3 < ratio < 8.4, f"ratio {ratio:.3f} not in expected range"
    print(f"OK: SU(3) N_f=3 m_rho/f_pi = {ratio:.3f} ± {err:.3f}")


def test_unknown_combo_falls_back():
    """Unknown (N_dc, N_f, rep) should fall back to QCD with a warning."""
    ratio, err, ref = t53b.m_rho_over_f_pi(N_dc=3, N_f=2, representation="fundamental")
    # Will print a warning to stdout; the returned ratio should be the
    # QCD physical-point value (8.36) per Lattice 2019 'no N_f dependence'
    assert 8.0 < ratio < 9.0, f"Fallback ratio {ratio:.3f} unexpected"
    print(f"OK: Unknown combo falls back to QCD ratio {ratio:.3f}")


def test_dark_pion_gmor():
    """m_pi^2 = 2 m_q Lambda / N_dc (GMOR)"""
    info = t53b.dark_pion_mass_lattice(
        m_q_GeV=0.1, Lambda_dark_GeV=1.0, N_dc=3
    )
    expected_sq = 2.0 * 0.1 * 1.0 / 3.0  # = 0.0667 GeV^2
    assert abs(info["m_pi_squared_GeV_sq"] - expected_sq) < 1e-6
    print(f"OK: GMOR m_pi = {info['m_pi_GeV']*1000:.1f} MeV at m_q=100 MeV, Lambda=1 GeV")


def test_lattice_data_table_populated():
    """Lattice data table should have at least QCD physical point."""
    assert (3, 3, "fundamental") in t53b.LATTICE_TABLE
    assert (2, 2, "adjoint") in t53b.LATTICE_TABLE
    print(f"OK: lattice table has {len(t53b.LATTICE_TABLE)} entries")


def test_self_check_runs():
    """The self-check should run without raising."""
    out = t53b.main()
    assert "test_points" in out
    assert len(out["test_points"]) > 0
    print(f"OK: self-check produced {len(out['test_points'])} test points")


if __name__ == "__main__":
    test_qcd_physical_point_recovered()
    test_ratio_returns_correct_value()
    test_unknown_combo_falls_back()
    test_dark_pion_gmor()
    test_lattice_data_table_populated()
    test_self_check_runs()
    print("\n=== ALL TESTS PASS ===")