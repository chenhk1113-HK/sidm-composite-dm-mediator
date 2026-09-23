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
# Yang, Tsai, Fan 2025 PRD 112, 083011 (arXiv:2504.02303) Fig. 2 shows:
#   - CDM2c (no SIDM): f_L ~ 0.5 everywhere (uniform mix)
#   - SIDM2c (σ_0/m = 147.1 cm²/g, w = 24.33 km/s): f_L rises from ~0.3 at
#     small r to ~0.6 at large r — modest segregation. Fig. 3 shows f_L(<0.2 R_vir)
#     spans 0 to 0.5 depending on subhalo.
#   - SIDMx (cross-only): more extreme segregation.
#
# Yang+ 2025 σ_0/m = 147.1 cm²/g with v_ref = 100 km/s gives σ/m(100) ≈ 8 cm²/g.
# Phase 44 σ/m(100) = 0.052 cm²/g is ~150× weaker than Yang+ 2025.
# Mass segregation efficiency scales with the local scattering rate
# Γ = ρ σ/m v_rel; the segregation timescale scales as t_seg ~ 1/Γ.
# So at the same density and velocity, t_seg scales as (σ_ref_Yang / σ_phase44).
# For 2 Gyr to show the same segregation as Yang+ would require
# (σ_phase44 / σ_ref_Yang) × t_Yang ≈ (1/150) × t_Yang — much longer than 2 Gyr.
# Hence at Phase 44, segregation is INVISIBLE in our T202 2 Gyr run.
#
# This function provides:
#   (a) Yang+ 2025-derived f_H profiles for SIDM2c (modest, subhalo-dependent),
#   (b) explicit σ/m scaling so the user can specify a different cross-section,
#   (c) a CDM limit at very low σ/m.
#
# IMPORTANT: the v18.29 (and earlier) version of this function returned
# HAND-PICKED piecewise constants (0.95, 0.30, 0.10 for core_collapsed at
# r/r_vir = 0.05, 0.20, 0.5+) that were NOT derived from Yang+ 2025 Fig. 2.
# Those values were 10× more extreme than what Fig. 2 actually shows, and were
# borrowed from a different parameter regime. The Rule 28 sanity check (compare
# to Yang+ Fig. 2 published values) caught this. See CHANGELOG.md T120.3aFix-v18.29.

# Yang+ 2025 reference values (Table I + Fig. 2 captions)
YANG_SIGMA_0_PER_M = 147.1   # cm²/g
YANG_W = 24.33                 # km/s
YANG_MASS_RATIO = 3.0          # m_H/m_L in Yang+
PHASE44_SIGMA_0_PER_M = 0.052  # cm²/g at v_ref = 100 km/s
PHASE44_V_REF = 100.0          # km/s


def _yang_sigma_m_at_v(v_kms: float) -> float:
    """Yang+ 2025 velocity-dependent σ/m(v) = σ_0 / (1 + v²/w²)."""
    return YANG_SIGMA_0_PER_M / (1.0 + (v_kms / YANG_W) ** 2)


def _segregation_strength(sigma_m_per_g: float, v_kms: float = 100.0) -> float:
    """Strength of segregation relative to Yang+ 2025 reference.

    Returns:
        0.0 if σ/m is far below the threshold where segregation operates;
        1.0 if σ/m matches Yang+ 2025 (modest segregation in Fig. 2);
        >1.0 if σ/m exceeds Yang+ 2025 (more extreme segregation).

    We use a simple linear scaling with the σ/m ratio, since mass segregation
    efficiency scales linearly with the local scattering rate Γ ∝ σ/m.
    """
    sig_ref = _yang_sigma_m_at_v(v_kms)
    return sigma_m_per_g / sig_ref


# Yang+ 2025 SIDM2c radial profile (Fig. 2, qualitative)
# f_L (light fraction) as a function of r/R_vir, for subhalos in the SIDM2c run.
# We use a smooth interpolant from Yang+ Fig. 2 caption (modest segregation):
#   r/R_vir ≈ 0.05: f_L ≈ 0.35
#   r/R_vir ≈ 0.20: f_L ≈ 0.45
#   r/R_vir ≈ 0.50: f_L ≈ 0.55
#   r/R_vir ≈ 1.00: f_L ≈ 0.60
# This is the AVERAGE subhalo profile; individual subhalos span a wider range
# (f_L(<0.2 R_vir) ∈ [0, 0.5] per Fig. 3).
_YANG_F_L_RADII = np.array([0.05, 0.20, 0.50, 1.00])
_YANG_F_L_VALUES = np.array([0.35, 0.45, 0.55, 0.60])


def _yang_f_H_at_r(r_over_rvir: float, mass_ratio: float = 3.0) -> float:
    """Yang+ 2025 SIDM2c heavy fraction at r/R_vir, for mass ratio m_H/m_L.

    For m_H/m_L = 3 and equal NUMBER densities, the asymptotic (no-segregation)
    f_H = m_H / (m_H + m_L) = 3/4 = 0.75. Yang+ Fig. 2 shows f_L varies from ~0.3
    at small r to ~0.6 at large r — meaning f_H varies from ~0.7 at small r to
    ~0.4 at large r for the standard heavy-asymmetric Yang+ setup.

    Args:
        r_over_rvir: radius normalized to virial radius
        mass_ratio: m_H/m_L (3.0 in Yang+ 2025)

    Returns:
        f_H (heavy fraction) in [0, 1]
    """
    # Interpolate f_L from Yang+ Fig. 2
    f_L = np.interp(r_over_rvir, _YANG_F_L_RADII, _YANG_F_L_VALUES)
    # Convert f_L → f_H, but account for the heavy-asymmetric mass ratio.
    # If mass ratio = m_H/m_L with EQUAL NUMBER densities:
    #   f_number_H = 1/(1 + m_L/m_H) = 1/(1 + 1/mass_ratio) = mass_ratio/(1+mass_ratio)
    #   f_mass_H = m_H n_H / (m_H n_H + m_L n_L) = mass_ratio / (mass_ratio + 1)
    # The no-segregation limit is f_mass_H = mass_ratio/(1+mass_ratio).
    # With segregation, f_L (number fraction of light) varies; f_mass_H follows.
    # For equal-number-density initial conditions, f_H (mass) = f_L_number relation:
    #   f_mass_H = mass_ratio × (1 - f_L) / (mass_ratio × (1 - f_L) + f_L)
    f_H_number_H = 1.0 - f_L  # number fraction of heavy (in Yang+ equal-number setup)
    f_H = mass_ratio * f_H_number_H / (mass_ratio * f_H_number_H + (1.0 - f_H_number_H))
    return float(np.clip(f_H, 0.0, 1.0))


def f_H_at_r(
    r_over_rvir: float,
    halo_type: str,
    sigma_m_per_g: float = PHASE44_SIGMA_0_PER_M,
    v_kms: float = PHASE44_V_REF,
    segregation_maturity: float = 1.0,
) -> float:
    """Local heavy fraction f_H at radius r/r_vir.

    Yang+ 2025 PRD 112, 083011 (arXiv:2504.02303) Fig. 2 derived profile.
    Mass segregation efficiency scales linearly with σ/m (since Γ ∝ σ/m).

    For each astrophysical class, the segregation strength is calibrated to the
    *target* σ/m (default = Phase 44 σ/m at v=100 km/s):

      - 'CDM' (no SIDM, σ/m → 0): f_H = f_H_no_seg = mass_ratio/(1+mass_ratio)
        regardless of r. With Yang+ mass_ratio = 3: f_H = 0.75.

      - 'core_forming' (Cloud-9-like, σ/m low, still forming): weak segregation,
        f_H follows a slight Yang+ curve scaled by the segregation strength.

      - 'core_collapsed' (dSph-like, fully segregated, observation at r~0.2):
        The heavy component has sunk to smaller r, leaving the OBSERVATION
        region (r~0.2 r_vir) dominated by LIGHT component. f_H(observation)
        is much smaller than f_H(no-segregation).
        THIS REQUIRES segregation_maturity = 1.0 (full segregation achieved).
        At Phase 44 σ/m, segregation_maturity is essentially 0 — the heavy
        component has NOT sunk to smaller r in 2 Gyr, so f_H at r~0.2 is
        still ~0.75 (no segregation). This is the honest Phase 44 conclusion.

      - 'intermediate' (SPARC-like): moderate segregation.

    Args:
        r_over_rvir: radius normalized to virial radius
        halo_type: 'CDM', 'core_forming', 'core_collapsed', 'intermediate'
        sigma_m_per_g: σ/m at the reference velocity (default Phase 44)
        v_kms: reference velocity for segregation strength (default v=100 km/s)
        segregation_maturity: 0.0 = no gravothermal evolution yet (heavy uniform);
                              1.0 = full core-collapse (heavy fully sunk);
                              intermediate values = partial segregation.
                              This parameter captures the TIME-DEPENDENCE of
                              the gravothermal cascade — even with Yang+ σ/m,
                              a halo that hasn't evolved won't show full segregation.

    Returns:
        f_H in [0, 1]
    """
    # Determine the no-segregation f_H for this halo's mass ratio
    if halo_type in ("core_collapsed", "core_forming", "intermediate", "CDM"):
        mass_ratio = 3.0  # Yang+ 2025 fiducial
    else:
        raise ValueError(f"Unknown halo_type: {halo_type}")

    f_H_no_seg = mass_ratio / (1.0 + mass_ratio)

    if halo_type == "CDM":
        return f_H_no_seg

    # Compute segregation strength (scales linearly with σ/m ratio)
    s = _segregation_strength(sigma_m_per_g, v_kms)

    # Effective segregation = σ/m strength × time evolution
    # (both must be > 0 for segregation to operate; this captures the fact that
    # at weak σ/m the gravothermal cascade takes much longer than the Hubble time)
    s_eff = s * segregation_maturity

    if halo_type == "core_collapsed":
        # Fully developed segregation: use the full Yang+ curve.
        f_H_yang = _yang_f_H_at_r(r_over_rvir, mass_ratio)
        f_H = f_H_no_seg + s_eff * (f_H_yang - f_H_no_seg)
    elif halo_type == "core_forming":
        f_H_yang = _yang_f_H_at_r(r_over_rvir, mass_ratio)
        f_H_partial = f_H_no_seg + 0.3 * (f_H_yang - f_H_no_seg)
        f_H = f_H_no_seg + s_eff * (f_H_partial - f_H_no_seg)
    elif halo_type == "intermediate":
        f_H_yang = _yang_f_H_at_r(r_over_rvir, mass_ratio)
        f_H_partial = f_H_no_seg + 0.6 * (f_H_yang - f_H_no_seg)
        f_H = f_H_no_seg + s_eff * (f_H_partial - f_H_no_seg)
    else:
        f_H = f_H_no_seg

    return float(np.clip(f_H, 0.0, 1.0))


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
    sigma_m_per_g: float = PHASE44_SIGMA_0_PER_M,
    v_for_seg: float = PHASE44_V_REF,
) -> float:
    """Effective sigma/m in a two-component SIDM halo with Phase 44 heavy channel.

    Args:
        v_kms: relative velocity in km/s
        halo_type: 'CDM', 'core_forming', 'core_collapsed', 'intermediate'
        r_over_rvir: radius normalized to virial radius
        sigma_HL_per_m: cross-channel cross section per unit mass
        sigma_m_per_g: σ/m at the segregation reference velocity (default Phase 44)
        v_for_seg: reference velocity for segregation strength (default v=100 km/s)

    Returns:
        sigma_eff/m_eff in cm^2/g
    """
    f_H = f_H_at_r(r_over_rvir, halo_type, sigma_m_per_g=sigma_m_per_g, v_kms=v_for_seg)
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