"""Tests for phase39b_sidm_responsive_profile.py.

Duties, in order of importance:

1. CORRECTNESS OF eq. 2.1. ``rho_yang2024`` must reduce to NFW exactly at r_c = 0
   (this is the property the repo's ``gravothermal_yang2024.rho_sidm`` lacks) and
   must produce a flat core for r << r_c.

2. END-TO-END UNITS / INTEGRATION. With the resonances zeroed and sigma_0 -> 0 the
   responsive rotation curve must equal the analytic NFW curve (this exercises the
   enclosed-mass quadrature and the km/s gravity constant).

3. RESPONSIVENESS. V_circ must move when sigma_0 moves; the inert phase39 profile
   must not (characterization of the defect it replaces).

4. MONOTONIC PHYSICS on the core-forming branch: more self-interaction -> longer
   tau -> bigger core.

5. DOCUMENTED MODULE DEFECT. ``gravothermal_yang2024.rho_sidm`` inverts the
   (r^beta + r_c^beta) factor; its ratio to NFW at r_c = 0 is exactly (r/r_s)^2.
   Pinned here so a future fix is visible. See the phase39b module docstring.

6. CALIBRATION SANITY. collapse_time_calibrated_gyr reproduces the paper's BM2
   value (28.7 Gyr) and scales as 1/sigma.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest

CODE_DIR = Path(__file__).resolve().parents[1] / "code"
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

import phase39_nfw_vs_sidm as p39
import gravothermal_yang2024 as gy
import phase39b_sidm_responsive_profile as m

R_GRID = np.array([0.5, 1.0, 3.0, 10.0, 30.0])


def _no_peaks(m_chi=m.M_CHI_GEV):
    return [dict(r, sigma_peak_cm2_per_g=0.0) for r in m.build_resonances(m_chi)]


# --------------------------------------------------------------- duty 1: eq 2.1

def test_rho_yang_reduces_to_nfw_exactly_at_rc_zero():
    rho_s, r_s = 1e7, 3.0
    got = m.rho_yang2024(R_GRID, rho_s, r_s, 0.0)
    nfw = m.rho_nfw(R_GRID, rho_s, r_s)
    np.testing.assert_allclose(got, nfw, rtol=1e-12)


def test_rho_yang_has_a_flat_core_for_r_ll_rc():
    rho_s, r_s = 1e7, 3.0
    rc = 3.0
    # inside a large core the profile is nearly constant; ratio to the rc->0 value ~ r_c/r
    val_inner = m.rho_yang2024(np.array([0.01, 0.05, 0.1]), rho_s, r_s, rc)
    assert np.all(np.diff(val_inner) < 0)          # still falling, but gently
    assert np.max(val_inner) / np.min(val_inner) < 3.0  # not the 1/r NFW cusp
    # and the core value matches rho_s * r_s / r_c
    np.testing.assert_allclose(val_inner[0], rho_s * r_s / rc, rtol=0.05)


# --------------------------------------------------- duty 2: units / integration

def test_responsive_curve_equals_analytic_nfw_when_cores_vanish():
    got = m.v_circ_sidm_responsive(R_GRID, 7.0, 0.5, m.M_CHI_GEV, _no_peaks(), 1e-14, m.A_SLOPE)
    expected = p39.v_circ_nfw(R_GRID, 7.0, 0.5)
    np.testing.assert_allclose(got, expected, rtol=2e-3)
    assert np.max(np.abs(got / expected - 1.0)) < 2e-3


def test_responsive_curve_is_positive_and_monotone_at_r_s_scale():
    v = m.v_circ_sidm_responsive(np.array([0.5, 1.0, 2.0, 5.0]), 7.0, 0.5)
    assert np.all(np.isfinite(v)) and np.all(v > 0)
    assert v[1] > v[0] and v[2] > v[1]     # rising through the r_s region


# ------------------------------------------------------------- duty 3: response

def test_responsive_profile_responds_to_sigma_while_inert_does_not():
    rep = m.responsiveness_report()
    assert rep["responsive_max_abs_dV_kms"] > 1.0, "responsive profile did not move"
    # the inert phase39 profile is bit-for-bit invariant (the defect being replaced)
    assert rep["inert_max_abs_dV_kms"] == 0.0


# --------------------------------------------------------- duty 4: monotone core

def test_more_interaction_gives_a_bigger_core_on_the_forming_branch():
    rcs = [m.responsive_halo(7.0, 0.5, m.M_CHI_GEV, m.build_resonances(), s, m.A_SLOPE)["r_c"]
           for s in (1e-6, 0.195, 10.0)]
    assert rcs[0] < rcs[1] < rcs[2], f"r_c not increasing with sigma_0: {rcs}"


def test_tau_is_capped_and_core_stays_within_the_model_range():
    halo = m.responsive_halo(7.0, 0.5, m.M_CHI_GEV, m.build_resonances(), 1e5, m.A_SLOPE)
    assert 0.0 <= halo["tau"] <= 1.0
    # f_rc(tau) peaks below ~0.5 r_s0 over tau in [0, 1]
    for tau in np.linspace(0.0, 1.0, 101):
        assert 0.0 <= gy.f_rc_over_rs0(float(tau)) <= 0.5 + 1e-9


# ------------------------------------------------------ duty 5: module defect

def test_gravothermal_yang2024_rho_sidm_is_not_paper_eq_2_1():
    """DOCUMENTED DEFECT, not a goal. The repo module inverts the
    (r^beta + r_c^beta) factor; at r_c = 0 its ratio to NFW is (r/r_s)^2."""
    rho_s, r_s = 1e7, 3.0
    nfw = m.rho_nfw(R_GRID, rho_s, r_s)
    module = np.array([gy.rho_sidm(float(r), rho_s, r_s, 0.0) for r in R_GRID])
    ratio = module / nfw
    np.testing.assert_allclose(ratio, (R_GRID / r_s) ** 2, rtol=1e-9)
    # and it is NOT what the paper (and this module) implement
    paper_form = m.rho_yang2024(R_GRID, rho_s, r_s, 0.0)
    assert np.max(np.abs(module / paper_form - 1.0)) > 0.5


# ----------------------------------------------------- duty 6: calibration sanity

def test_collapse_time_matches_yang_2024_bm2():
    t_c = gy.collapse_time_calibrated_gyr(7.1, 2.74e8, 0.141)
    assert t_c == pytest.approx(28.7, rel=0.05), t_c


def test_collapse_time_scales_inversely_with_sigma():
    t1 = gy.collapse_time_calibrated_gyr(1.0, 1e7, 3.0)
    t2 = gy.collapse_time_calibrated_gyr(10.0, 1e7, 3.0)
    assert t2 == pytest.approx(t1 / 10.0, rel=1e-9)


# ----------------------------------------------------------- artifact contract

def test_result_artifact_is_self_consistent_if_present():
    path = CODE_DIR.parents[0] / "data" / "results" / "phase39b_sidm_responsive_profile.json"
    if not path.exists():
        pytest.skip("phase39b JSON artifact not generated in this checkout")
    d = json.loads(path.read_text(encoding="utf-8"))
    assert d["n_galaxies"] == 15
    assert d["responsiveness"]["inert_max_abs_dV_kms"] == 0.0
    assert d["responsiveness"]["responsive_max_abs_dV_kms"] > 1.0
    # the responsive model must BEAT NFW in total log L for this to be worth reporting
    assert d["totals"]["logL_sidm_responsive"] > d["totals"]["logL_nfw"]
    # core sizes must stay inside the model's physical range
    assert 0.0 <= d["core_distribution"]["r_c_over_r_s0_min"]
    assert d["core_distribution"]["r_c_over_r_s0_max"] <= 0.5 + 1e-6
