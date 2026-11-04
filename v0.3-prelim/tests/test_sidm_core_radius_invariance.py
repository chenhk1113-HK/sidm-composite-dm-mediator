"""Unit-system and core-radius sensitivity guard for the Phase 39 / Phase 40
rotation-curve comparison.

Two independent duties:

1. UNIT GUARD. ``v_circ_nfw`` / ``v_circ_burkert`` must return km/s, because their
   output is compared directly against SPARC ``Vobs_kms`` / ``eV_kms``. The check
   recomputes the same circular velocities from scratch in SI (m, kg, s) and compares.
   Before 2026-11-04 both modules used G = 4.5e-6 kpc^3 M_sun^-1 Gyr^-2, which returns
   kpc/Gyr, inflating every modelled speed by sqrt(4.5e-6 / 4.302e-6) = 1.02275.

2. CHARACTERIZATION GUARD FOR A DOCUMENTED DEFECT. The "velocity-dependent SIDM core
   radius" in these modules is inert: its raw value is always far below its own
   0.1*r_s floor, so sigma/m, the resonance peaks and the slope a never reach the
   rotation curve. This test pins that fact. It is NOT an endorsement: if someone
   repairs the core-radius prescription (for example by switching to the Yang+ 2024
   eq. 2.1 / eq. 2.2 profile already implemented in gravothermal_yang2024.py), this
   test MUST fail, and that failure is the signal to re-derive phase39/phase40 and
   update docs/INTEGRITY_FINDINGS_2026-11-04.md. See also
   docs/INTEGRITY_FINDINGS_2026-11-04.md.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pytest

CODE_DIR = Path(__file__).resolve().parents[1] / "code"
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

import phase39_nfw_vs_sidm as p39
import phase40_corrected_comparison as p40
from t90_v50_resonant_sidm import kinetic_energy_eV

# SI constants (CODATA / IAU nominal), independent of anything in the repo.
G_SI = 6.67430e-11          # m^3 kg^-1 s^-2
M_SUN_KG = 1.988475e30      # kg
KPC_M = 3.0856775814913673e19  # m


def _v_si_from_m_enc(m_enc_msun, r_kpc):
    """V_circ in km/s from an enclosed mass, computed entirely in SI."""
    m_kg = np.asarray(m_enc_msun, dtype=float) * M_SUN_KG
    r_m = np.asarray(r_kpc, dtype=float) * KPC_M
    return np.sqrt(G_SI * m_kg / r_m) / 1000.0


R_GRID = np.array([0.5, 1.0, 3.0, 10.0, 30.0, 100.0])
LOG_RHO_S, LOG_R_S = 6.0, 1.0


def _nfw_m_enc_nfw_msun(r_kpc, rho_s, r_s):
    x = np.asarray(r_kpc, dtype=float) / r_s
    return 4 * np.pi * rho_s * r_s**3 * (np.log1p(x) - x / (1.0 + x))


def _burkert_m_enc_msun(r_kpc, rho_b, r_b):
    """Independent numeric quadrature of the Burkert profile (scipy quad)."""
    from scipy.integrate import quad

    def integrand(rp):
        return rho_b * r_b**3 / ((rp + r_b) * (rp**2 + r_b**2)) * rp**2

    out = []
    for rr in np.atleast_1d(r_kpc):
        val, _ = quad(integrand, 0.0, float(rr), limit=400, epsabs=1e-12, epsrel=1e-10)
        out.append(4 * np.pi * val)
    return np.array(out)


def _resonances(m_chi=6.58):
    v_targets = [28.0, 100.0, 300.0, 700.0]
    sigma_peaks = [100.0, 0.07, 0.1, 0.01]
    width_fracs = [0.05, 0.05, 0.05, 0.10]
    out = []
    for i, v_t in enumerate(v_targets):
        e_r = kinetic_energy_eV(v_t, m_chi)
        out.append({
            "name": f"R{i}",
            "E_R_eV": e_r,
            "Gamma_eV": width_fracs[i] * e_r,
            "sigma_peak_cm2_per_g": sigma_peaks[i],
            "v_target_kms": v_t,
        })
    return out


# ---------------------------------------------------------------- duty 1: units


def test_phase39_nfw_velocity_matches_si():
    rho_s, r_s = 10**LOG_RHO_S, 10**LOG_R_S
    got = p39.v_circ_nfw(R_GRID, LOG_RHO_S, LOG_R_S)
    expected = _v_si_from_m_enc(_nfw_m_enc_nfw_msun(R_GRID, rho_s, r_s), R_GRID)
    assert np.all(np.isfinite(got))
    # km/s order of magnitude, not the ~1.02x-larger kpc/Gyr value
    np.testing.assert_allclose(got, expected, rtol=2e-3)
    assert np.max(np.abs(got / expected - 1.0)) < 2e-3


def test_phase39_burkert_velocity_matches_si():
    from scipy.integrate import quad  # noqa: F401  (used by the helper)
    log_rho_b, r_b = 6.0, 2.0
    got = p39.v_circ_burkert(R_GRID, log_rho_b, r_b)
    expected = _v_si_from_m_enc(_burkert_m_enc_msun(R_GRID, 10**log_rho_b, r_b), R_GRID)
    np.testing.assert_allclose(got, expected, rtol=2e-3)


def test_phase40_nfw_velocity_matches_si():
    rho_s, r_s = 10**LOG_RHO_S, 10**LOG_R_S
    got = p40.v_circ_nfw(R_GRID, LOG_RHO_S, LOG_R_S)
    expected = _v_si_from_m_enc(_nfw_m_enc_nfw_msun(R_GRID, rho_s, r_s), R_GRID)
    np.testing.assert_allclose(got, expected, rtol=2e-3)


def test_modules_use_the_kms_gravity_constant():
    assert p39.G_KPC_KMS == pytest.approx(4.302e-6)
    assert p40.G_KPC_KMS == pytest.approx(4.302e-6)
    src39 = (CODE_DIR / "phase39_nfw_vs_sidm.py").read_text(encoding="utf-8")
    src40 = (CODE_DIR / "phase40_corrected_comparison.py").read_text(encoding="utf-8")
    for name, src in (("phase39", src39), ("phase40", src40)):
        offenders = [
            line.strip()
            for line in src.splitlines()
            if re.match(r"^\s*G\s*=\s*4\.5e-6\b", line)
        ]
        assert not offenders, f"{name} assigns the kpc/Gyr G again: {offenders}"


# ------------------------------------------------- duty 2: inert core radius

SIGMA_PROBE = [1e-6, 1e-3, 0.195, 10.0, 1000.0, 1e5]


def test_phase39_sidm_profile_is_currently_invariant_to_sigma_over_11_orders():
    """DOCUMENTED DEFECT, not a design goal. See the module docstring."""
    r = np.array([1.0, 3.0, 10.0, 30.0, 50.0])
    curves = [
        p39.v_circ_sidm_multi_resonant(
            r, 6.0, 0.5, 110.0, 6.58, _resonances(), sigma_0, 0.7)
        for sigma_0 in SIGMA_PROBE
    ]
    base = curves[0]
    for sigma_0, curve in zip(SIGMA_PROBE, curves):
        np.testing.assert_allclose(curve, base, rtol=0.0, atol=0.0,
                                   err_msg=f"sigma_0={sigma_0} changed the curve; "
                                           "the core radius may have been repaired -- "
                                           "re-derive phase39/phase40 and update "
                                           "docs/INTEGRITY_FINDINGS_2026-11-04.md")


def test_phase39_sidm_profile_is_currently_invariant_to_peaks_and_slope():
    r = np.array([1.0, 3.0, 10.0, 30.0, 50.0])
    ref = p39.v_circ_sidm_multi_resonant(r, 6.0, 0.5, 110.0, 6.58, _resonances(), 0.195, 0.7)
    no_peaks = [dict(res, sigma_peak_cm2_per_g=0.0) for res in _resonances()]
    for a_slope in (0.0, 0.7, 3.0):
        for res in (no_peaks, _resonances()):
            curve = p39.v_circ_sidm_multi_resonant(r, 6.0, 0.5, 110.0, 6.58, res, 0.195, a_slope)
            np.testing.assert_allclose(curve, ref, rtol=0.0, atol=0.0)


def test_phase40_sidm_profile_is_currently_invariant_to_sigma():
    r = np.array([1.0, 3.0, 10.0, 30.0, 50.0])
    curves = [
        p40.v_circ_sidm(r, 6.0, 0.5, 110.0, 6.58, _resonances(), sigma_0, 0.7)
        for sigma_0 in SIGMA_PROBE
    ]
    for curve in curves[1:]:
        np.testing.assert_allclose(curve, curves[0], rtol=0.0, atol=0.0)


def test_raw_core_radius_is_far_below_its_own_floor_everywhere_in_the_fit_grid():
    """Reproduces the arithmetic the modules perform, over the grid they search."""
    from t90_v70_multi_resonant_darkqcd import (
        sigma_m_multi_resonant,
        velocity_dependent_background,
    )

    rho_s_grid = [10**k for k in (4, 5, 6, 7, 8, 9)]
    r_s_grid = [10**k for k in (-0.5, 0.0, 0.3, 0.7, 1.0, 1.5, 2.0)]
    v_max_grid = [35.0, 60.0, 110.0, 180.0, 260.0]
    m_chi, sigma_0, a_slope = 6.58, 0.195, 0.7
    res = _resonances(m_chi)

    worst_ratio = 0.0
    n = 0
    for v_max in v_max_grid:
        sig = sigma_m_multi_resonant(
            v_max, m_chi, res, velocity_dependent_background(v_max, sigma_0, a_slope), 0.0
        )["sigma_m_total"]
        sigma_kpc = sig * 2.09e-10
        v_natural = v_max * 3.086e16 / 3.156e10
        for rho_s in rho_s_grid:
            for r_s in r_s_grid:
                raw = 0.45 * r_s * (sigma_kpc * rho_s * r_s / v_natural) ** 0.25
                worst_ratio = max(worst_ratio, raw / (0.1 * r_s))
                n += 1
    # Every grid point clamps. Measured worst case over this grid is 0.111 of the
    # floor (log_rho_s=9, log_r_s=2, V_max=35 km/s), i.e. the raw value never gets
    # within an order of magnitude of the floor, let alone past it.
    assert n == 210
    assert worst_ratio < 0.5, (
        f"raw r_core reached {worst_ratio:.3f} of the floor; the core radius is no "
        "longer uniformly clamped -- re-derive phase39/phase40"
    )
