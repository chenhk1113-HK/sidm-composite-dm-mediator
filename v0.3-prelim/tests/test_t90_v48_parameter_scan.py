"""Tests for T90.48 parameter scan for multi-component SIDM.

Per T90.48 scope:
  - The parameter scan module imports cleanly
  - evaluate_point returns valid sigma/m values
  - Scan runs through the grid
  - At least one point in the scan has sigma/m(Cloud-9) > 0
"""

import numpy as np
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(Path(__file__).resolve().parent.parent / "code")))


def test_v48_module_imports():
    """The T90.48 parameter scan module imports cleanly."""
    from t90_v48_parameter_scan import (  # noqa: F401
        evaluate_point, run_parameter_scan, SCAN_GRID,
        SIGMA_M_CLOUD9_TARGET, SIGMA_M_GALAXY_MAX, SIGMA_M_BULLET_MAX,
    )


def test_v48_scan_grid_has_5_parameters():
    """The scan grid covers 5 physical parameters."""
    from t90_v48_parameter_scan import SCAN_GRID
    expected_params = {"m_phi_MeV", "g_chi", "M_halo_Msun", "m_chi_H_GeV", "mass_ratio"}
    assert expected_params.issubset(SCAN_GRID.keys())


def test_v48_evaluate_point_returns_dict():
    """evaluate_point returns a dict with sigma/m values."""
    from t90_v48_parameter_scan import evaluate_point
    r = evaluate_point(
        m_phi_MeV=10.0,
        g_chi=0.5,
        M_halo_Msun=1e9,
        m_chi_H_GeV=30.0,
        mass_ratio=3.0,
    )
    assert "sigma_m_Cloud9" in r
    assert "sigma_m_Galaxy" in r
    assert "sigma_m_Bullet" in r
    assert "all_OK" in r


def test_v48_evaluate_point_sigma_m_positive():
    """All sigma/m values from evaluate_point are positive."""
    from t90_v48_parameter_scan import evaluate_point
    for m_phi in [5.0, 50.0]:
        for g in [0.3, 1.0]:
            r = evaluate_point(m_phi, g, 1e9, 30.0, 3.0)
            assert r["sigma_m_Cloud9"] > 0
            assert r["sigma_m_Galaxy"] > 0
            assert r["sigma_m_Bullet"] > 0


def test_v48_light_mediator_higher_cloud9_sigma():
    """At lighter mediator (m_phi=5 MeV), sigma/m(Cloud-9) is higher than at m_phi=50."""
    from t90_v48_parameter_scan import evaluate_point
    r_light = evaluate_point(5.0, 1.0, 1e9, 30.0, 3.0)
    r_heavy = evaluate_point(50.0, 1.0, 1e9, 30.0, 3.0)
    # Light mediator gives stronger low-velocity sigma/m
    assert r_light["sigma_m_Cloud9"] > r_heavy["sigma_m_Cloud9"]


def test_v48_strong_coupling_higher_sigma():
    """Stronger g_chi gives higher sigma/m at all velocities."""
    from t90_v48_parameter_scan import evaluate_point
    r_strong = evaluate_point(10.0, 1.0, 1e9, 30.0, 3.0)
    r_weak = evaluate_point(10.0, 0.3, 1e9, 30.0, 3.0)
    # Stronger coupling -> higher sigma/m
    assert r_strong["sigma_m_Cloud9"] > r_weak["sigma_m_Cloud9"]


def test_v48_bullet_constraint_violated_at_low_mediator():
    """At very light mediator (m_phi=5 MeV), Bullet sigma/m exceeds limit."""
    from t90_v48_parameter_scan import evaluate_point, SIGMA_M_BULLET_MAX
    r = evaluate_point(5.0, 1.0, 1e9, 30.0, 3.0)
    # Light mediator gives high sigma/m at all velocities (Yukawa Born flat)
    # Bullet should be violated
    assert r["sigma_m_Bullet"] > SIGMA_M_BULLET_MAX


def test_v48_no_point_satisfies_all_three():
    """HONEST TEST: no point in the small scan grid satisfies all three constraints.

    This documents the fundamental finding from T90.48 — the multi-component
    analytic model does NOT have a parameter point that simultaneously
    satisfies Cloud-9, Galactic, and Bullet.
    """
    from t90_v48_parameter_scan import evaluate_point, SCAN_GRID
    n_compatible = 0
    n_total = 0
    for m_phi in SCAN_GRID["m_phi_MeV"]:
        for g in SCAN_GRID["g_chi"]:
            for M_h in SCAN_GRID["M_halo_Msun"]:
                for m_H in SCAN_GRID["m_chi_H_GeV"]:
                    for r in SCAN_GRID["mass_ratio"]:
                        result = evaluate_point(m_phi, g, M_h, m_H, r)
                        n_total += 1
                        if result.get("all_OK", False):
                            n_compatible += 1
    # In the published scan, zero points satisfied all three constraints
    assert n_compatible == 0
    assert n_total > 0