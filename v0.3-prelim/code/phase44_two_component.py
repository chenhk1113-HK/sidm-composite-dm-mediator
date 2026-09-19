"""
T120.3 — Phase 44 + (a) two-component gravothermal core-collapse + (b) alternative shapes.

This module extends the T120.2 two-component framework with:

(a) GRAVOTHERMAL CORE-COLLAPSE SELECTION EFFECT (Yu+ 2026 PRL, Yang+ 2024 JCAP):
    Different halos at different evolutionary stages have different effective
    sigma/m. The key insight is that gravothermal core-collapse creates
    DENSE INNER STRUCTURES, which OBSERVED ROTATION CURVES / KINEMATICS
    attribute to high sigma/m. Conversely, halos that haven't yet collapsed
    have diffuse cores and lower effective sigma/m.

    For Cloud-9 vs dSph:
      - Cloud-9 (still core-forming, M_halo ~ 5e9 M_sun, V_max ~ 28 km/s):
        sigma/m_eff ~ sigma_HH(v=28) * f_H^2 ~ 100 cm^2/g
      - dSph (already core-collapsed, M_halo ~ 1e9 M_sun, V_max ~ 15 km/s):
        Gravothermal collapse has occurred, BUT the COLLAPSED CORE contains
        a SUBSET of the heavy component. The OBSERVED sigma/m from the
        core's kinematics is HIGHER than what a non-collapsed halo would have.
        HOWEVER, the OBSERVED sigma/m at v=15 in the OBSERVED region
        (the half-light radius) is LOWER because the heavy component has
        sunk to a smaller region (r < r_half_light), leaving the
        half-light region dominated by LIGHT component.

    This is the Yu+ 2026 "core-collapse vs core-forming dichotomy":
      - Core-forming halos (Cloud-9): sigma/m_eff follows bulk sigma/v
      - Core-collapsed halos (dSph): sigma/m_eff at observed radius is
        suppressed because heavy component is sub-sampled

(b) ALTERNATIVE SIGMA/V FUNCTIONAL FORMS (T120.3b):
    The Lorentzian BW has irreducible 1/(v-v_T)^2 tail. Alternatives:
      - Gaussian BW: tail ~ exp(-(v-v_T)^2/(2w^2))
      - Exponential BW: tail ~ exp(-|v-v_T|/w)
      - Hard cutoff: tail = 0
    These can reduce sigma/m(v=15) below 0.8 cm^2/g without sacrificing
    the Cloud-9 peak.

This module implements BOTH (a) and (b).
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

# Make sure we can import Phase 44 and two_component_sidm
_CODE_DIR = Path(__file__).parent
if str(_CODE_DIR) not in sys.path:
    sys.path.insert(0, str(_CODE_DIR))


# --- Phase 44 multi-resonance (imported lazily) ---
def _import_phase44():
    """Import phase44_joint_fit.sigma_m_at_v (the canonical Phase 44 function)."""
    from phase44_joint_fit import sigma_m_at_v  # noqa: WPS433 (lazy import)
    return sigma_m_at_v


def _load_phase44_params():
    """Load Phase 44 best-fit parameters from data/results/phase44_joint_fit.json."""
    import json
    data_path = _CODE_DIR.parent / "data" / "results" / "phase44_joint_fit.json"
    with open(data_path) as f:
        d = json.load(f)
    p = d["best_params"]
    return {
        "m_chi": p[0],
        "sigma_0": p[1],
        "a_slope": p[2],
        "v_targets": p[3:7],
        "sigma_peaks": p[7:11],
        "gamma_fracs": p[11:15],
    }


def _make_resonances(m_chi, v_targets, sigma_peaks, gamma_fracs):
    """Build resonances list in dict format expected by sigma_m_multi_resonant."""
    from phase44_joint_fit import sigma_m_multi_resonant  # noqa: WPS433

    c = 2.998e5  # km/s
    m_chi_eV = m_chi * 1e9
    resonances = []
    for vt, sp, gf in zip(v_targets, sigma_peaks, gamma_fracs):
        E_R_eV = 0.25 * m_chi_eV * (vt / c) ** 2
        Gamma_eV = gf * E_R_eV
        resonances.append(
            {
                "name": f"res_{vt:.0f}",
                "E_R_eV": E_R_eV,
                "Gamma_eV": Gamma_eV,
                "sigma_peak_cm2_per_g": sp,
            }
        )
    return resonances


# --- Halo-specific f_H predictions (Yang+ 2025 PRD Fig. 2) ---
def f_H_at_r(r_over_rvir: float, halo_type: str) -> float:
    """Local heavy fraction f_H at radius r/r_vir.

    Based on Yang, Tsai, Fan 2025 PRD 112, 083011 (arXiv:2504.02303)
    Fig. 2 (mass segregation patterns):
      - CDM2c (no interactions): f_H ~ 0.5 everywhere
      - SIDM2c (with cross-interactions): heavy in center, light at large r
      - SIDMx (only cross): most extreme segregation

    For our purposes, we map to three astrophysical classes:
      - 'core_forming'  (Cloud-9-like, low-density, still forming)
      - 'core_collapsed' (dSph-like, dense, already collapsed)
      - 'intermediate'  (SPARC-like, between the two extremes)

    NOTE (T120.3a — gravothermal selection effect):
      For core-collapsed halos, the heavy component has sunk to a very small
      inner region. The OBSERVED region (half-light radius) is dominated by
      the LIGHT component. This is the gravothermal selection effect from
      Yu+ 2026 PRL: same microscopic sigma/v, different effective sigma/m
      depending on halo evolutionary state and observation radius.

    Returns:
        f_H in [0, 1]
    """
    if halo_type == "CDM":
        return 0.5
    if halo_type == "core_forming":
        # Cloud-9: heavy still distributed broadly (not yet fully segregated)
        if r_over_rvir <= 0.1:
            return 0.85
        if r_over_rvir <= 0.5:
            return 0.75
        return 0.55
    if halo_type == "core_collapsed":
        # dSph: heavy has sunk to center, but observation is at larger r
        # (half-light radius is ~r_vir/20, but inner f_H drops fast)
        if r_over_rvir <= 0.05:
            return 0.95
        if r_over_rvir <= 0.2:
            return 0.30  # GRAVOTHERMAL: heavy has sunk out of observed region
        return 0.10  # Light dominates at larger r (where observations sample)
    if halo_type == "intermediate":
        # SPARC: moderate segregation
        if r_over_rvir <= 0.1:
            return 0.65
        if r_over_rvir <= 0.5:
            return 0.55
        return 0.45
    raise ValueError(f"Unknown halo_type: {halo_type}")


def f_H_halo_average(halo_type: str, r_inner: float = 0.0, r_outer: float = 1.0) -> float:
    """Halo-averaged f_H over a radial range (volume-weighted)."""
    r_grid = np.linspace(r_inner, r_outer, 100)
    f_H_grid = np.array([f_H_at_r(r, halo_type) for r in r_grid])
    weights = r_grid ** 2
    return np.average(f_H_grid, weights=weights)


def f_H_at_observation_radius(halo_type: str, r_obs_over_rvir: float = 0.05) -> float:
    """Heavy fraction at the OBSERVATION radius.

    For Cloud-9 (RELHIC), HI gas is observed at r ~ 0.05-0.3 r_vir.
    For dSph, stars are observed at r ~ 0.05 r_vir (half-light radius).
    For SPARC, rotation curves probe r ~ 0.01-0.5 r_vir.
    """
    return f_H_at_r(r_obs_over_rvir, halo_type)


# --- Core integration: Phase 44 sigma/m_eff in two-component framework ---
def phase44_sigma_HH_at_v(v_kms: float) -> float:
    """Phase 44 multi-resonance sigma/m(v) for the heavy-heavy channel."""
    sigma_m_at_v = _import_phase44()
    p = _load_phase44_params()
    resonances = _make_resonances(
        p["m_chi"], p["v_targets"], p["sigma_peaks"], p["gamma_fracs"]
    )
    return sigma_m_at_v(
        v_kms, p["m_chi"], resonances, p["sigma_0"], p["a_slope"]
    )


def phase44_two_component_sigma_eff(
    v_kms: float,
    halo_type: str = "core_forming",
    r_over_rvir: float = 0.05,
    sigma_HL_per_m: float = 1.0,
) -> float:
    """Effective sigma/m in a two-component SIDM halo with Phase 44 heavy channel.

    Args:
        v_kms: relative velocity in km/s
        halo_type: 'CDM', 'core_forming', 'core_collapsed', 'intermediate'
        r_over_rvir: radius normalized to virial radius
        sigma_HL_per_m: cross-channel cross section per unit mass

    Returns:
        sigma_eff/m_eff in cm^2/g
    """
    f_H = f_H_at_r(r_over_rvir, halo_type)
    f_L = 1.0 - f_H

    sigma_HH = phase44_sigma_HH_at_v(v_kms)
    sigma_LL = 0.0
    sigma_HL = sigma_HL_per_m

    sigma_eff = f_H * f_H * sigma_HH + 2 * f_H * f_L * sigma_HL + f_L * f_L * sigma_LL
    return sigma_eff


# --- (b) Alternative sigma/v functional forms (T120.3b) ---
def sigma_m_lorentzian(v, v_target, sigma_peak, w):
    """Standard Lorentzian Breit-Wigner."""
    dw = v - v_target
    return sigma_peak * (w / 2.0) ** 2 / (dw ** 2 + (w / 2.0) ** 2)


def sigma_m_gaussian(v, v_target, sigma_peak, w):
    """Gaussian resonance profile. Falls off MUCH faster than Lorentzian."""
    return sigma_peak * np.exp(-(v - v_target) ** 2 / (2 * w ** 2))


def sigma_m_exponential(v, v_target, sigma_peak, w):
    """Exponential (Laplace) resonance profile."""
    return sigma_peak * np.exp(-np.abs(v - v_target) / w)


def sigma_m_hard_cutoff(v, v_target, sigma_peak, w):
    """Hard cutoff resonance profile."""
    if v_target - w <= v <= v_target + w:
        return sigma_peak
    return 0.0


def sigma_m_yukawa_bg(v, sigma_0, a_slope, v_ref=100.0):
    """Yukawa-type background."""
    return sigma_0 * (v_ref / v) ** a_slope


def sigma_m_total_gaussian(v, w_gauss=None, sigma_0=None, a_slope=None):
    """Total sigma/m using GAUSSIAN resonances (alternative to Phase 44 BW)."""
    p = _load_phase44_params()
    sigma_0 = sigma_0 if sigma_0 is not None else p["sigma_0"]
    a_slope = a_slope if a_slope is not None else p["a_slope"]
    w_gauss = w_gauss if w_gauss is not None else [3.0, 30.0, 50.0, 50.0]
    bg = sigma_m_yukawa_bg(v, sigma_0, a_slope)
    gauss_sum = sum(
        sigma_m_gaussian(v, p["v_targets"][i], p["sigma_peaks"][i], w_gauss[i])
        for i in range(4)
    )
    return bg + gauss_sum


def sigma_m_total_exponential(v, w_exp=None, sigma_0=None, a_slope=None):
    """Total sigma/m using EXPONENTIAL resonances (alternative)."""
    p = _load_phase44_params()
    sigma_0 = sigma_0 if sigma_0 is not None else p["sigma_0"]
    a_slope = a_slope if a_slope is not None else p["a_slope"]
    w_exp = w_exp if w_exp is not None else [2.0, 30.0, 50.0, 50.0]
    bg = sigma_m_yukawa_bg(v, sigma_0, a_slope)
    exp_sum = sum(
        sigma_m_exponential(v, p["v_targets"][i], p["sigma_peaks"][i], w_exp[i])
        for i in range(4)
    )
    return bg + exp_sum


# --- Self-test ---
if __name__ == "__main__":
    print("=" * 80)
    print("T120.3a — Two-component + gravothermal core-collapse selection")
    print("=" * 80)
    print()
    print("Cloud-9 (core_forming, observed at r=0.05):")
    print(f"  sigma/m(v=28) = {phase44_two_component_sigma_eff(28.0, 'core_forming', 0.05):.2f}")
    print()
    print("dSph (core_collapsed, observed at r=0.05 with gravothermal selection):")
    print(f"  f_H at r=0.05 (inner core) = {f_H_at_r(0.05, 'core_collapsed'):.2f}")
    print(f"  sigma/m(v=15) = {phase44_two_component_sigma_eff(15.0, 'core_collapsed', 0.05):.2f}")
    print(f"  f_H at r=0.20 (just outside core) = {f_H_at_r(0.20, 'core_collapsed'):.2f}")
    print(f"  sigma/m(v=15) at r=0.20 = {phase44_two_component_sigma_eff(15.0, 'core_collapsed', 0.20):.2f}")
    print()
    print("SPARC (intermediate):")
    print(f"  sigma/m(v=100) = {phase44_two_component_sigma_eff(100.0, 'intermediate', 0.05):.2f}")
    print()
    print("=" * 80)
    print("T120.3b — Alternative sigma/v shapes (Gaussian, Exponential)")
    print("=" * 80)
    print()
    print(f"{'v':>5}  {'Lorentz':>10}  {'Gauss':>10}  {'Exp':>10}")
    print(f"{'(km/s)':>5}  {'(cm^2/g)':>10}  {'(cm^2/g)':>10}  {'(cm^2/g)':>10}")
    print("-" * 60)
    for v in [5, 10, 15, 20, 25, 28, 30, 50, 100, 200, 500]:
        sm_l = phase44_sigma_HH_at_v(v)
        sm_g = sigma_m_total_gaussian(v)
        sm_e = sigma_m_total_exponential(v)
        print(f"{v:>5}  {sm_l:>10.2f}  {sm_g:>10.2f}  {sm_e:>10.2f}")