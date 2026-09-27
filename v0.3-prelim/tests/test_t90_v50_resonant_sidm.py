"""Tests for T90.50 resonant SIDM module.

Per T90.50 scope:
  - The resonant SIDM module imports cleanly
  - kinetic_energy_eV gives correct CM frame energy
  - sommerfeld_enhancement gives S > 1 at low v
  - breit_wigner_sigma_cm2 has peak at resonance
  - At the Cloud-9 reference point, all three constraints satisfied
"""

import numpy as np
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(Path(__file__).resolve().parent.parent / "code")))


def test_v50_module_imports():
    """The T90.50 resonant SIDM module imports cleanly."""
    from t90_v50_resonant_sidm import (  # noqa: F401
        kinetic_energy_eV, sommerfeld_enhancement,
        breit_wigner_sigma_cm2, sigma_m_resonant,
        evaluate_resonant_point, run_resonant_scan,
    )


def test_v50_kinetic_energy_at_cloud9():
    """E(28 km/s, m_chi=30 GeV) = 65 eV (CM frame KE for identical particles)."""
    from t90_v50_resonant_sidm import kinetic_energy_eV
    E = kinetic_energy_eV(28.0, 30.0)
    # Expected ~65 eV
    assert 50 < E < 80, f"E = {E:.1f} eV not in expected range"


def test_v50_kinetic_energy_scales_with_v_squared():
    """E(v) ~ v^2."""
    from t90_v50_resonant_sidm import kinetic_energy_eV
    E_28 = kinetic_energy_eV(28.0, 30.0)
    E_56 = kinetic_energy_eV(56.0, 30.0)
    # E(56)/E(28) should be 4 (v^2 scaling)
    ratio = E_56 / E_28
    assert abs(ratio - 4.0) < 0.01


def test_v50_kinetic_energy_scales_with_mass():
    """E(v) ~ m_chi."""
    from t90_v50_resonant_sidm import kinetic_energy_eV
    E_30 = kinetic_energy_eV(28.0, 30.0)
    E_60 = kinetic_energy_eV(28.0, 60.0)
    # E(60)/E(30) = 2
    assert abs(E_60 / E_30 - 2.0) < 0.01


def test_v50_sommerfeld_low_v_high():
    """At low v, Sommerfeld enhancement is large."""
    from t90_v50_resonant_sidm import sommerfeld_enhancement
    # alpha=0.01, v=10 km/s
    S = sommerfeld_enhancement(10.0, 0.01)
    # S ~ pi*0.01/(10/3e5) = pi*0.01*3e4 = 940
    assert S > 100


def test_v50_sommerfeld_high_v_one():
    """At high v, Sommerfeld enhancement is ~1."""
    from t90_v50_resonant_sidm import sommerfeld_enhancement
    S = sommerfeld_enhancement(10000.0, 0.01)
    # v/c = 10000/3e5 = 0.033 >> alpha=0.01, so S ~ 1
    assert 1.0 < S < 10.0


def test_v50_breit_wigner_peak_at_resonance():
    """Breit-Wigner cross-section peaks at E = E_R."""
    from t90_v50_resonant_sidm import breit_wigner_sigma_cm2, kinetic_energy_eV
    E_R = 65.0  # eV (Cloud-9 resonance)
    # v at resonance: E_R = (m/4) * v^2/c^2 -> v^2 = 4*E_R/m
    v_at_res = np.sqrt(4 * E_R / (30 * 1e9)) * 3e5  # km/s
    sigma_at_res = breit_wigner_sigma_cm2(v_at_res, 30.0, E_R, 1.0)
    # Off resonance: v = 2*v_at_res
    sigma_off = breit_wigner_sigma_cm2(v_at_res * 2, 30.0, E_R, 1.0)
    assert sigma_at_res > sigma_off


def test_v50_resonant_cloud9_compatible():
    """The Cloud-9 reference point satisfies all three constraints."""
    from t90_v50_resonant_sidm import evaluate_resonant_point
    r = evaluate_resonant_point(
        m_chi_GeV=30.0,
        E_R_eV=65.0,
        Gamma_R_eV=0.1,
        sigma_0_cm2_per_g=0.01,
        alpha_Y=0.01,
    )
    assert r["all_OK"], f"Reference point not all_OK: {r}"


def test_v50_evaluate_returns_dict():
    """evaluate_resonant_point returns sigma/m at all three velocities."""
    from t90_v50_resonant_sidm import evaluate_resonant_point
    r = evaluate_resonant_point(30.0, 65.0, 1.0, 0.01)
    assert "sigma_m_Cloud9" in r
    assert "sigma_m_Galaxy" in r
    assert "sigma_m_Bullet" in r
    assert "all_OK" in r


def test_v50_sigma_m_finite_at_all_params():
    """All sigma/m values are finite for reasonable parameters."""
    from t90_v50_resonant_sidm import evaluate_resonant_point
    for E_R in [10.0, 100.0, 1000.0]:
        for Gamma in [0.1, 10.0]:
            r = evaluate_resonant_point(30.0, E_R, Gamma, 0.01)
            assert np.isfinite(r["sigma_m_Cloud9"])
            assert np.isfinite(r["sigma_m_Galaxy"])
            assert np.isfinite(r["sigma_m_Bullet"])


def test_v50_off_resonance_low_sigma():
    """Far from resonance, sigma/m(C9) is small (no enhancement)."""
    from t90_v50_resonant_sidm import evaluate_resonant_point
    # E_R=1000 eV (much higher than 65 eV at v=28)
    r = evaluate_resonant_point(30.0, 1000.0, 1.0, 0.001, 0.01)
    # sigma/m should be much smaller than Cloud-9 requirement
    assert r["sigma_m_Cloud9"] < 1.0


def test_v50_at_least_10_cloud9_compatible():
    """HONEST TEST: the scan finds multiple Cloud-9 compatible points."""
    from t90_v50_resonant_sidm import evaluate_resonant_point
    n_compatible = 0
    for E_R in [30.0, 50.0, 65.0, 100.0, 200.0]:
        for Gamma in [0.1, 1.0, 5.0, 10.0, 50.0]:
            for sig_0 in [0.001, 0.01]:
                r = evaluate_resonant_point(30.0, E_R, Gamma, sig_0, 0.01)
                if r["all_OK"]:
                    n_compatible += 1
    # Resonant SIDM with E_R ~ 50-100 eV (near Cloud-9 velocity) should give
    # multiple compatible points
    assert n_compatible >= 10, f"Only {n_compatible} compatible points found"