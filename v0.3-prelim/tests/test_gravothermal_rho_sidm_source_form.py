"""Permanent regression tests for gravothermal_yang2024.rho_sidm.

Pins arXiv:2305.16176 (Yang+ 2024, "A Parametric Model for SIDM Halos") eq. 2.1:

    rho_SIDM(r) = rho_s / { [ (r/r_s)^beta + (r_c/r_s)^beta ]^(1/beta) * (1 + r/r_s)^2 },  beta = 4

Added 2026-11-04 ([LocalIntegrity-Sweep-2026-11-04] F10, decision D7). Until then the module carried
that core factor INVERTED:

    rho_s * [(r^beta + r_c^beta)/(r_s^beta + r_c^beta)]^(1/beta) * (r_s/(r+r_s))^2

whose ratio to NFW at r_c = 0 is exactly (r/r_s)^2 (0.028 at 0.5 kpc, 1.0 at 3.0 kpc, 100.0 at
30.0 kpc for r_s = 3 kpc) - density rising outward through the core instead of falling. The
consequence was measured, not assumed: the 2026-11-03 Cloud-9 optical-thickness recheck computed its
core densities with the inverted form, and its "optically thin at tau = 1" conclusion reversed.

Every test compares the module against a THIRD implementation typed directly from the source PDF
(paper_eq_2_1 below), never against the module itself.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

CODE_DIR = Path(__file__).resolve().parents[1] / "code"
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

import gravothermal_yang2024 as gy

BETA = 4.0
RHO_S, R_S = 1e7, 3.0
R_GRID = np.geomspace(0.1, 100.0, 60)


def paper_eq_2_1(r, rho_s: float, r_s: float, r_c: float) -> np.ndarray:
    """Independent implementation of arXiv:2305.16176 eq. 2.1, typed from
    docs/papers/verified/2305.16176_yang_parametric_2024.pdf."""
    r = np.asarray(r, dtype=float)
    core_factor = (r / r_s) ** BETA + (r_c / r_s) ** BETA
    return rho_s / (core_factor ** (1.0 / BETA) * (1.0 + r / r_s) ** 2)


def module_curve(r_grid, rho_s: float, r_s: float, r_c: float) -> np.ndarray:
    return np.array([gy.rho_sidm(float(r), rho_s, r_s, r_c) for r in r_grid])


# ------------------------------------------------------------------ source agreement


@pytest.mark.parametrize("r_c", [0.0, 0.3, 1.5, 3.0])
def test_matches_paper_eq_2_1_on_a_grid(r_c):
    got = module_curve(R_GRID, RHO_S, R_S, r_c)
    want = paper_eq_2_1(R_GRID, RHO_S, R_S, r_c)
    np.testing.assert_allclose(got, want, rtol=1e-12)


# ------------------------------------------------------------------------ required limits


def test_core_free_limit_is_nfw_exactly():
    """Yang+ 2024: "In the limit r_c -> 0, eq. (2.1) smoothly reduces to an NFW profile"."""
    got = module_curve(R_GRID, RHO_S, R_S, 0.0)
    nfw = RHO_S * (R_S / R_GRID) * (1.0 + R_GRID / R_S) ** -2
    np.testing.assert_allclose(got, nfw, rtol=1e-12)
    # the old inverted signature (ratio to NFW == (r/r_s)^2, 100x at r = 30 kpc) must be absent
    ratio = got / nfw
    assert np.max(np.abs(ratio - 1.0)) < 1e-9
    assert np.max(np.abs(ratio - (R_GRID / R_S) ** 2)) > 1.0


def test_deep_core_is_flat_and_central_density_is_rho_s_rs_over_rc():
    """r -> 0 with r_c > 0 freezes the core factor at r_c, so rho -> rho_s r_s / r_c (flat core).
    The NFW envelope (1 + r/r_s)^-2 legitimately falls even inside the core, so it is divided out
    and this test measures flatness of the CORE factor itself."""
    for r_c in (0.1, 0.5, 2.0):
        probe = (1e-6, 1e-4, 1e-2 * r_c)
        vals = np.array(module_curve(probe, RHO_S, R_S, r_c))
        envelope = np.array([RHO_S * (R_S / r_c) * (1.0 + r / R_S) ** -2 for r in probe])
        ratios = vals / envelope
        assert np.max(np.abs(ratios - 1.0)) < 1e-3, (r_c, ratios)
        assert abs(vals[0] - RHO_S * R_S / r_c) / (RHO_S * R_S / r_c) < 1e-6


def test_far_tail_approaches_the_nfw_slope_minus_three():
    """r >> r_s and r >> r_c: eq. 2.1 -> rho_s r_s^3 (1 + r_c/r_s)^-1 r^-3, i.e. slope -3."""
    r_lo, r_hi = 100.0, 200.0
    rho_lo, rho_hi = module_curve((r_lo, r_hi), RHO_S, R_S, 1.0)
    slope = np.log(rho_hi / rho_lo) / np.log(r_hi / r_lo)
    assert -3.05 < slope < -2.95, slope


def test_central_density_rises_monotonically_as_the_core_collapses():
    """A collapsing core (shrinking r_c) must RAISE the central density. The pre-fix module rose
    outward through the core instead, which this pins against."""
    r_cs = (2.0, 1.0, 0.5, 0.2, 0.05)
    central = [float(gy.rho_sidm(0.0, RHO_S, R_S, r_c)) for r_c in r_cs]
    assert all(b > a for a, b in zip(central, central[1:])), central
    np.testing.assert_allclose(central, [RHO_S * R_S / r_c for r_c in r_cs], rtol=1e-9)


def test_profile_is_positive_and_finite_everywhere():
    got = module_curve(np.geomspace(1e-3, 1e4, 200), RHO_S, R_S, 0.75)
    assert np.all(np.isfinite(got)) and np.all(got > 0.0)


def test_agrees_with_the_phase39b_responsive_profile_implementation():
    """phase39b implements eq. 2.1 independently; two implementations must not disagree."""
    import phase39b_sidm_responsive_profile as p39b
    for r_c in (0.0, 0.3, 1.5):
        got = module_curve(R_GRID, RHO_S, R_S, r_c)
        want = np.asarray(p39b.rho_yang2024(R_GRID, RHO_S, R_S, r_c), dtype=float)
        np.testing.assert_allclose(got / want, 1.0, rtol=1e-12)


def test_beta_is_the_papers_four():
    """The paper fixes beta = 4 in eq. 2.1; a silent change would reshape every predicted halo."""
    assert gy.BETA == 4.0
