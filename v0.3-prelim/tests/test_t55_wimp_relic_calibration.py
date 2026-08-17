"""Tests for the Boltzmann-solver relic abundance (T55, R11 G15)."""
from __future__ import annotations
import sys
import math
from pathlib import Path

WSL_ROOT = Path("/home/lamkuenai/sidm-composite-dm-mediator")
sys.path.insert(0, str(WSL_ROOT / "v0.3-prelim/code"))
import t55_boltzmann_relic as t55


def test_thermal_relic_gives_correct_omega():
    """For m_chi = 40 GeV and <sigma*v> = 3e-26 cm^3/s, Omega_h^2 ~ 0.12."""
    out = t55.freeze_out_Y(40.0, 3e-26, g_chi=1.0)
    assert 0.10 < out["Omega_h2"] < 0.14, (
        f"Omega_h^2 {out['Omega_h2']:.3f} not near Planck 0.120"
    )
    print(f"OK: thermal relic Omega_h^2 = {out['Omega_h2']:.4f}")


def test_over_annihilation_gives_low_omega():
    """Over-annihilating models should give LOW Omega_h^2."""
    out = t55.freeze_out_Y(40.0, 1e-24, g_chi=1.0)
    assert out["Omega_h2"] < 0.01, (
        f"Over-annihilating Omega_h^2 {out['Omega_h2']} should be small"
    )
    print(f"OK: over-annihilation Omega_h^2 = {out['Omega_h2']:.5f}")


def test_under_annihilation_gives_high_omega():
    """Under-annihilating models should give HIGH Omega_h^2 (overabundant)."""
    out = t55.freeze_out_Y(40.0, 1e-27, g_chi=1.0)
    assert out["Omega_h2"] > 1.0, (
        f"Under-annihilating Omega_h^2 {out['Omega_h2']} should be large"
    )
    print(f"OK: under-annihilation Omega_h^2 = {out['Omega_h2']:.3f}")


def test_omega_inverse_proportional_to_sigma_v():
    """Omega_h^2 should scale as 1/<sigma*v>."""
    out_a = t55.freeze_out_Y(40.0, 3e-26, g_chi=1.0)
    out_b = t55.freeze_out_Y(40.0, 6e-26, g_chi=1.0)
    ratio = out_a["Omega_h2"] / out_b["Omega_h2"]
    # Should be 2 (sigma_v doubled -> Omega halved)
    assert 1.9 < ratio < 2.1, f"Omega scaling wrong: ratio = {ratio:.3f}"
    print(f"OK: Omega scales as 1/<sigma*v>: ratio = {ratio:.3f}")


def test_y0_consistent_with_omega():
    """Y0 should give the same Omega_h^2 as the direct computation."""
    out = t55.freeze_out_Y(40.0, 3e-26, g_chi=1.0)
    # Recompute Omega from Y0
    m_chi_g = 40.0 * 1.7826619e-24
    rho_c_SI = 1.878e-29
    Omega_recomputed = out["Y0"] * m_chi_g * t55.S_0_CM3 / rho_c_SI
    rel_diff = abs(Omega_recomputed - out["Omega_h2"]) / out["Omega_h2"]
    assert rel_diff < 0.01, f"Y0/Omega inconsistency: {rel_diff*100:.2f}%"
    print(f"OK: Y0 -> Omega consistent within {rel_diff*100:.2f}%")


def test_zero_inputs_handled():
    """Zero or negative inputs should not crash."""
    out1 = t55.freeze_out_Y(0.0, 3e-26)
    out2 = t55.freeze_out_Y(40.0, 0.0)
    assert out1["Omega_h2"] == 0.0
    assert out2["Omega_h2"] == 0.0
    print("OK: zero/negative inputs return zero")


if __name__ == "__main__":
    test_thermal_relic_gives_correct_omega()
    test_over_annihilation_gives_low_omega()
    test_under_annihilation_gives_high_omega()
    test_omega_inverse_proportional_to_sigma_v()
    test_y0_consistent_with_omega()
    test_zero_inputs_handled()
    print("\n=== ALL TESTS PASS ===")