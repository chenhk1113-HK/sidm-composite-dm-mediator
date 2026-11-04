"""Tests for the validity ceiling of the Yang+ 2024 eq. 2.3 / 2.4 fitting functions.

Found 2026-11-04 ([LocalIntegrity-Sweep-2026-11-04] F13) while re-deriving the Cloud-9 optical-thickness
recheck: the fitting polynomials in gravothermal_yang2024.py stop being physical past tau ~ 1.3.

Measured values (this test re-derives them, it does not re-quote them):

| tau  | f_rho_s   | f_r_s     | f_rc/r_s0 | f_Vmax    | f_Rmax   |
|------|-----------|-----------|-----------|-----------|----------|
| 1.00 | 7.2202    |  0.4547   | 0.1073    |  1.2097   | 0.4877   |
| 1.20 | 26.5666   |  0.2386   | 0.0350    |  1.1587   | 0.2706   |
| 1.40 | 112.8472  | -0.0740   | 0.0313    | -2.9549   | -0.0024  |
| 2.00 | 3683.10   | -1.7893   | 1.0461    | -456.49   | -1.3640  |

A negative scale radius and a negative circular velocity are not halo properties. The old Cloud-9
recheck quoted tau* = 1.37 and scanned tau out to 20, i.e. it reported "onset times" inside the region
where the model returns garbage. Every producer in this repo clamps tau = min(t_evol / t_c, 1.0); these
tests keep that clamp load-bearing and make the ceiling explicit.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

CODE_DIR = Path(__file__).resolve().parents[1] / "code"
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

import gravothermal_yang2024 as gy

INSIDE = [0.0, 0.05, 0.2, 0.5, 0.8, 1.0, 1.2]
BEYOND = [1.5, 2.0, 5.0]


def test_fit_range_constant_exists_and_is_the_measured_ceiling():
    assert gy.TAU_FIT_RANGE_MAX == 1.3
    assert gy.tau_in_fit_range(0.0) and gy.tau_in_fit_range(1.2)
    assert not gy.tau_in_fit_range(1.4)
    assert not gy.tau_in_fit_range(-0.1)


@pytest.mark.parametrize("tau", INSIDE)
def test_factors_are_physical_inside_the_fit_range(tau):
    """r_s shrinks, r_c grows from zero, rho_s grows, V_max and R_max stay positive."""
    assert gy.f_rs_over_rs0(tau) > 0.0, tau
    assert gy.f_rs_over_rs0(tau) <= 1.001, tau
    assert gy.f_rho_s_over_rho_s0(tau) >= 1.0, tau
    assert gy.f_rc_over_rs0(tau) >= 0.0, tau
    assert gy.f_Vmax_over_Vmax0(tau) > 0.0, tau
    assert gy.f_Rmax_over_Rmax0(tau) > 0.0, tau


@pytest.mark.parametrize("tau", BEYOND)
def test_factors_are_unphysical_beyond_the_ceiling(tau):
    """Pins the reason the ceiling exists: the fits produce negative radii/velocities out there."""
    assert gy.f_rs_over_rs0(tau) < 0.0, (tau, gy.f_rs_over_rs0(tau))
    assert gy.f_Vmax_over_Vmax0(tau) < 0.0, (tau, gy.f_Vmax_over_Vmax0(tau))


def test_ceiling_is_between_1_2_and_1_5():
    """The crossing is located, not assumed: physical at 1.2, unphysical at 1.4-1.5."""
    assert gy.f_rs_over_rs0(1.2) > 0.0
    assert gy.f_rs_over_rs0(1.4) < 0.0
    assert gy.tau_in_fit_range(1.2) and not gy.tau_in_fit_range(1.4)


@pytest.mark.parametrize("sigma_eff", [0.01, 0.14, 7.0, 50.0, 174.0])
def test_predict_sidm_halo_clamps_tau_and_returns_physical_halo(sigma_eff):
    """The producer must never evaluate the fits past their range, at any cross-section."""
    out = gy.predict_sidm_halo(5e9, 31.12, 1.4, sigma_eff)
    assert 0.0 <= out["tau"] <= 1.0, out["tau"]
    assert gy.tau_in_fit_range(out["tau"]), out["tau"]
    assert out["r_s_kpc"] > 0.0 and out["r_c_kpc"] >= 0.0
    assert out["rho_s_msun_per_kpc3"] > 0.0
    assert out["V_max_kms"] > 0.0 and out["R_max_kpc"] > 0.0, out
    assert out["t_evol_Gyr"] < 13.8 and out["t_c_Gyr"] > 0.0, out


def test_the_cloud9_high_sigma_recheck_scan_is_capped_at_the_ceiling():
    """scripts/recheck_cloud9_highsigma_20261103.py used to scan tau out to 20 and report tau* from
    garbage. It must now stop at the physical ceiling."""
    src = (Path(__file__).resolve().parents[2] / "scripts"
           / "recheck_cloud9_highsigma_20261103.py").read_text(encoding="utf-8")
    assert "TAU_MAX_SCAN = G.TAU_FIT_RANGE_MAX" in src
    assert "while tau <= 20.0" not in src
