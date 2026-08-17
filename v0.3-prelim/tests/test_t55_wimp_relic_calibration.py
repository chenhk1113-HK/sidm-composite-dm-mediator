"""Tests for the WIMP-miracle relic calibration (T55, R11 G15 → R12 P0-C).

The module was renamed from `t55_boltzmann_relic.py` to
`t55_wimp_relic_calibration.py` in R12 P0-C (2026-08-17) because the
legacy file imported scipy.integrate.odeint but did not actually call
it; the body returns a calibrated scalar mapping rather than a
numerical Boltzmann solution. The test suite is unchanged but
renamed.
"""
from __future__ import annotations
import sys
import math
from pathlib import Path

# On WSL: /home/lamkuenai/sidm-composite-dm-mediator
# On Windows (CI / windows-side test runs): C:/Users/lamkuenai/projects/sidm-composite-dm-mediator
_WSL_ROOT = Path("/home/lamkuenai/sidm-composite-dm-mediator")
_WIN_ROOT = Path("C:/Users/lamkuenai/projects/sidm-composite-dm-mediator")
if _WSL_ROOT.exists():
    sys.path.insert(0, str(_WSL_ROOT / "v0.3-prelim/code"))
elif _WIN_ROOT.exists():
    sys.path.insert(0, str(_WIN_ROOT / "v0.3-prelim/code"))
import t55_wimp_relic_calibration as t55


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
    print(f"OK: under-annihilation Omega_h^2 = {out['Omega_h2']:.5f}")


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

# ---- R12 P0-C regression tests (locked 2026-08-17) ----

def test_t55_no_odeint_import():
    """R12 P0-C: the legacy `from scipy.integrate import odeint` IMPORT has
    been removed because odeint was never called.

    Re-introducing the import without actually using odeint would
    regress to the deceptive "Boltzmann solver" framing that P0-C
    removed.

    Note: the docstring MENTIONS odeint (in honest-description context)
    but does not import it. The test below scans only for the import
    statement at module top-level (not the textual mention).
    """
    import ast
    mod_source = Path(t55.__file__).read_text(encoding="utf-8")
    tree = ast.parse(mod_source)
    has_odeint_import = any(
        isinstance(node, ast.ImportFrom)
        and node.module == "scipy.integrate"
        and any(alias.name == "odeint" for alias in node.names)
        for node in tree.body
    )
    assert not has_odeint_import, (
        "R12 P0-C: t55_wimp_relic_calibration.py must NOT import scipy's "
        "odeint; this file is a calibrated mapping, not a Boltzmann "
        "solver. Re-introducing the import is a regression."
    )


def test_t55_method_field_is_calibrated():
    """R12 P0-C: freeze_out_Y() should self-describe as a calibration,
    not as a numerical Boltzmann integration.
    """
    out = t55.freeze_out_Y(40.0, 3e-26, g_chi=1.0)
    method = out.get("method", "")
    assert "calibrat" in method.lower() or "steigman" in method.lower(), (
        f"R12 P0-C: freeze_out_Y() output method field = {method!r}; "
        "should describe itself as a calibrated inverse-proportionality, "
        "not a Boltzmann integration."
    )
