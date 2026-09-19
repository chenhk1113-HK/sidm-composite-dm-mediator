"""
T120.2 — Phase 44 multi-resonance + two-component SIDM integration.

This module combines:
- Phase 44 multi-resonance sigma/m(v) (BW peaks + Yukawa background)
  from v0.3-prelim/code/phase44_joint_fit.py
- Two-component asymmetric DM (Yang+ 2025 PRD, mass segregation)
  from v0.3-prelim/code/two_component_sidm.py
- Halo-specific heavy fractions f_H(r, halo_type) from Yang+ 2025 PRD Fig. 2

Key idea (T120.2):
  The effective sigma/m in a halo is the mass-segregation-weighted
  combination of:
    - Heavy-heavy channel: Phase 44 multi-resonance sigma/m(v)
    - Light-light channel: ~0 (collisionless)
    - Heavy-light cross-channel: drives mass segregation

  Different halos have different heavy fractions f_H(r):
    - Core-forming halos (Cloud-9): f_H ~ 0.85 in core
    - Core-collapsed halos (dSph):  f_H ~ 0.95 in core but smaller overall
                                    heavy mass fraction in observable volume
    - Intermediate halos (SPARC):    f_H ~ 0.5-0.6

This module implements the CONCRETE INTEGRATION. The remaining T120 phases
(joint fit, paper update) build on this.

PHYSICAL PICTURE OF SELECTION EFFECT:
  - Cloud-9 (still core-forming, V_max ~ 28 km/s):
    Heavy component still distributed broadly, f_H ~ 0.85 throughout.
    Observed sigma/m_eff at v=28 ~ sigma_HH(v=28) * f_H^2 ~ 72 cm^2/g.
  - dSph (already core-collapsed, V_max ~ 15 km/s):
    Heavy component has sunk to center, f_H ~ 0.95 in core.
    Observed sigma/m_eff at v=15 ~ sigma_HH(v=15) * f_H^2 ~ 4.5 cm^2/g.
  - SPARC (V_max ~ 100 km/s, intermediate state):
    f_H ~ 0.6, observed sigma/m_eff at v=100 ~ sigma_HH(v=100) * f_H^2 ~ 0.04 cm^2/g.

The selection effect comes from the DIFFERENT MASS-SEGREGATION STATES
of different halos, combined with the different velocity scales of the
observations.
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
    # best_params is a flat array (per phase44_joint_fit convention):
    #   [m_chi, sigma_0, a_slope, v_t0..3, sigma_p0..3, gamma_f0..3]
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
        E_R_eV = 0.25 * m_chi_eV * (vt / c) ** 2  # CORRECT kinematics
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

    NOTE: f_H is the LOCAL number-density fraction of the heavy component
    at radius r. For Cloud-9 (core-forming), the heavy is broadly distributed
    so f_H(r) is HIGH even at large r. For dSph (core-collapsed), the heavy
    has sunk to the center, so f_H is HIGH only in the center.

    Returns:
        f_H in [0, 1]
    """
    if halo_type == "CDM":
        return 0.5
    if halo_type == "core_forming":
        # Heavy still distributed broadly (not yet fully segregated)
        # Cloud-9 case: f_H ~ 0.85 in core, drops to 0.55 at large r
        if r_over_rvir <= 0.1:
            return 0.85
        if r_over_rvir <= 0.5:
            return 0.75
        return 0.55
    if halo_type == "core_collapsed":
        # Heavy has fully sunk to center
        # dSph case: f_H ~ 0.95 in core, drops to 0.30 at large r
        if r_over_rvir <= 0.05:
            return 0.95
        if r_over_rvir <= 0.2:
            return 0.65
        return 0.30
    if halo_type == "intermediate":
        # SPARC-like: moderate segregation
        if r_over_rvir <= 0.1:
            return 0.65
        if r_over_rvir <= 0.5:
            return 0.55
        return 0.45
    raise ValueError(f"Unknown halo_type: {halo_type}")


def f_H_halo_average(halo_type: str, r_inner: float = 0.0, r_outer: float = 1.0) -> float:
    """Halo-averaged f_H over a radial range.

    Used when the OBSERVATION samples a range of radii, not just the center.
    For example, Cloud-9's HI gas is observed out to ~r_vir.

    Args:
        halo_type: 'core_forming', 'core_collapsed', 'intermediate'
        r_inner: inner radius (in r_vir units, default 0)
        r_outer: outer radius (in r_vir units, default 1)

    Returns:
        volume-weighted average f_H over [r_inner, r_outer]
    """
    # Numerical integration (volume-weighted: weight by r^2)
    r_grid = np.linspace(r_inner, r_outer, 100)
    f_H_grid = np.array([f_H_at_r(r, halo_type) for r in r_grid])
    weights = r_grid ** 2  # shell volume
    return np.average(f_H_grid, weights=weights)


# --- Core integration: Phase 44 sigma/m_eff in two-component framework ---
def phase44_sigma_HH_at_v(v_kms: float) -> float:
    """Phase 44 multi-resonance sigma/m(v) for the heavy-heavy channel.

    Returns sigma/m in cm^2/g. Uses the canonical Phase 44 best-fit parameters.
    """
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
    sigma_HL_per_m: float = 1.0,  # cm^2/g cross-channel
) -> float:
    """Effective sigma/m in a two-component SIDM halo with Phase 44 heavy channel.

    Args:
        v_kms: relative velocity in km/s
        halo_type: 'CDM', 'core_forming', 'core_collapsed', 'intermediate'
        r_over_rvir: radius normalized to virial radius (0.05 = center)
        sigma_HL_per_m: cross-channel cross section per unit mass

    Returns:
        sigma_eff/m_eff in cm^2/g
    """
    f_H = f_H_at_r(r_over_rvir, halo_type)
    f_L = 1.0 - f_H

    # Heavy-heavy: Phase 44 multi-resonance
    sigma_HH = phase44_sigma_HH_at_v(v_kms)

    # Light-light: ~0 (collisionless)
    sigma_LL = 0.0

    # Heavy-light cross-channel: contributes to mass segregation
    sigma_HL = sigma_HL_per_m

    # Weighted effective sigma/m (with mass-dependence folded in)
    # For equal-mass components, this is just the weighted sum;
    # for unequal masses, it's sigma_eff = sum of (weight^2 * sigma_i)
    sigma_eff = f_H * f_H * sigma_HH + 2 * f_H * f_L * sigma_HL + f_L * f_L * sigma_LL
    return sigma_eff


# --- Self-test ---
if __name__ == "__main__":
    print("=" * 80)
    print("T120.2 — Phase 44 multi-resonance + two-component SIDM")
    print("=" * 80)
    print()
    print("Phase 44 best-fit parameters:")
    p = _load_phase44_params()
    print(f"  m_chi = {p['m_chi']:.3f} GeV")
    print(f"  sigma_0 = {p['sigma_0']:.4f} cm^2/g")
    print(f"  a_slope = {p['a_slope']:.3f}")
    print(f"  v_targets = {p['v_targets']}")
    print()
    print("Predicted sigma/m_eff in different halo types (at r ~ 0.05 r_vir):")
    print()
    print(f"{'v':>5}  {'Cloud-9':>10}  {'dSph':>10}  {'SPARC':>10}  {'CDM ref':>10}")
    print(f"{'(km/s)':>5}  {'(cm^2/g)':>10}  {'(cm^2/g)':>10}  {'(cm^2/g)':>10}  {'(cm^2/g)':>10}")
    print("-" * 80)
    for v in [5, 10, 15, 20, 25, 28, 30, 50, 100, 200, 500]:
        sm_cloud9 = phase44_two_component_sigma_eff(v, "core_forming")
        sm_dsph = phase44_two_component_sigma_eff(v, "core_collapsed")
        sm_sparc = phase44_two_component_sigma_eff(v, "intermediate")
        sm_cdm = phase44_two_component_sigma_eff(v, "CDM")
        print(f"{v:>5}  {sm_cloud9:>10.2f}  {sm_dsph:>10.2f}  {sm_sparc:>10.2f}  {sm_cdm:>10.2f}")

    print()
    print("KEY OBSERVATION:")
    print("  - Cloud-9 (core-forming, f_H=0.85 in core) has high sigma/m at v=28")
    print("  - dSph (core-collapsed, f_H=0.95 in core) has different effective sigma/m")
    print("  - Same microscopic Phase 44 multi-resonance, different effective sigma/m_eff")
    print("  - This is the SELECTION EFFECT (wayforward §3 item 4)")
    print()
    print(f"Halo-averaged f_H (volume-weighted from r=0 to r=r_vir):")
    print(f"  core_forming:  {f_H_halo_average('core_forming'):.3f}")
    print(f"  core_collapsed: {f_H_halo_average('core_collapsed'):.3f}")
    print(f"  intermediate:   {f_H_halo_average('intermediate'):.3f}")