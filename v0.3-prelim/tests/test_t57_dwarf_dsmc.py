"""Tests for the dwarf-mass KiSS-SIDM DSMC driver (T57, R11 G16)."""
from __future__ import annotations
import sys
import math
from pathlib import Path

WSL_ROOT = Path("/home/lamkuenai/sidm-composite-dm-mediator")
sys.path.insert(0, str(WSL_ROOT / "v0.3-prelim/code"))
import t57_dwarf_dsmc as t57


def test_dwarf_halo_params_physically_reasonable():
    """NFW parameters for dwarf-mass halos should be in standard range."""
    for M_halo in [1e7, 3e7, 1e8]:
        p = t57.dwarf_halo_params(M_halo)
        # r_200 in kpc: order 10-100 kpc for dwarf halos
        # (10^7 Msun: ~10 kpc, 10^8 Msun: ~20 kpc)
        assert 1 < p["r_200_kpc"] < 200, f"r_200 {p['r_200_kpc']:.1f} kpc out of range"
        # c_200: 10-30 typical for dwarf halos
        assert 5 < p["c_200"] < 30, f"c_200 {p['c_200']:.1f} out of range"
        # r_s in kpc (sub-kpc to ~10 kpc for dwarfs)
        assert 0.1 < p["r_s_kpc"] < 50, f"r_s {p['r_s_kpc']:.3f} kpc out of range"
        # rho_s in M_sun/kpc^3
        assert 1e-5 < p["rho_s_Msun_kpc3"] < 1e10, f"rho_s out of range"
        print(f"  M={M_halo:.0e} Msun: r_200={p['r_200_kpc']:.1f} kpc, c_200={p['c_200']:.1f}, "
              f"r_s={p['r_s_kpc']:.3f} kpc, rho_s={p['rho_s_Msun_kpc3']:.3e} Msun/kpc^3")


def test_concentration_mass_relation():
    """c_200 should DECREASE with increasing M_halo (Dutton-Maccio 2014)."""
    cs = [t57.dwarf_halo_params(M)["c_200"] for M in [1e7, 1e8, 1e9]]
    assert cs[0] > cs[1] > cs[2], f"c_200 not decreasing: {cs}"
    print(f"OK: c_200 decreasing with M: {cs[0]:.1f} > {cs[1]:.1f} > {cs[2]:.1f}")


def test_dsmc_runs_without_crashing():
    """The DSMC driver should run (canonical case) without errors."""
    out = t57.run_dwarf_dsmc(1e8, N_particles=2000, n_steps=10, seed=42)
    assert "halo_params" in out
    assert "elapsed_seconds" in out
    # Whether it succeeds or "completes" with the canonical case is OK
    assert out["elapsed_seconds"] < 60, f"Took {out['elapsed_seconds']}s, too slow"
    print(f"OK: DSMC driver ran in {out['elapsed_seconds']:.1f}s")


def test_main_function_runs():
    """The main() entry point should produce output."""
    out = t57.main()
    assert "halo_masses_attempted" in out
    assert len(out["results"]) == 3
    print(f"OK: main() produced 3 results")


if __name__ == "__main__":
    test_dwarf_halo_params_physically_reasonable()
    test_concentration_mass_relation()
    test_dsmc_runs_without_crashing()
    test_main_function_runs()
    print("\n=== ALL TESTS PASS ===")