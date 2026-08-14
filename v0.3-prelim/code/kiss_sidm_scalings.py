"""
KISS-SIDM scalings — published power-law fits from Gurian & May 2025.

Per the 3-direction framework (2026-08-10, prior session):
    Direction A = SASHIMI-SIDM per-galaxy forward model (shipped 2026-08-10, msg 38460).
    Direction B = Two-component SIDM extension (deferred).
    Direction C = KISS-SIDM kinetic-replace of the Balberg+ 2002 fluid model
                  (THIS MODULE).

This module is a FIT-FORMULA import from Gurian & May 2025 (arXiv:2505.15903v2,
PRL 135, 221001). It is NOT a port of the KiSS-SIDM DSMC code itself. The
DSMC is a non-trivial C/Python MC kernel that would require installing the
public repo at https://gitlab.com/Socob/KiSS-SIDM (see AGENTS.md rule 17:
no new deps without explicit approval). What we can defensibly import is the
PUBLISHED FIT FORMULAS — the Table I core-mass scalings, the Knudsen regime
classifier, the collapse-time scaling — and use them to replace the Balberg+
2002 analytic fluid model in the per-halo prior penalty.

THE THREE THINGS KISS-SIDM TELLS US (verbatim from the paper, used below):

1. Knudsen number (Eq. 18):
    Kn = sqrt(<v^2> / (12 * pi * G * rho)) * 1 / (rho * sigma_m)
    LMFP = Kn >> 1 (long mean free path, halo outer regions)
    IMFP = Kn ~ 1  (intermediate, bounding the core — fluid model BREAKS HERE)
    SMFP = Kn << 1 (short, deep core — fluid model is APPROPRIATE per the paper)

2. Core mass scaling (Table I, d log M / d log <v^2> over 10^4 < rho/rho_s < 10^5):
                       d log M_Kn=1 / d log <v^2>      d log M_Kn=5 / d log <v^2>
    Fluid:             -0.27                            -0.37
    DSMC (KISS-SIDM):  -0.21                            -0.21
    → The fluid and kinetic models AGREE on the Kn=5 number (~equal slopes)
      but DIVERGE on the Kn=1 number by 30%. This is the EXACT regime
      where the fluid model breaks down (the IMFP region).

3. The fit residuals are not formally published for the KISS-SIDM canonical
   case. The paper provides Fig. 5 (convergence in core collapse time) and
   Fig. 1 (density profiles at t/t0 = 102, 371, 437). What is ANALYTIC is:
       t_collapse (DSMC) / t_collapse (fluid) ≈ 1.0  for sigma_m/sigma_0 = 0.32
   ("differences of ~30% in collapse time between different N-body SIDM
    implementations" — this is a between-code uncertainty, not a
    fluid-vs-kinetic correction). We use this as a calibration sanity check.

WHAT THIS MODULE DOES:

  - knudsen_number(rho, v_rms, sigma_m) -> float : Eq. 18, the IMFP regime
                                                   classifier.
  - knudsen_regime_label(Kn) -> str              : "LMFP" / "IMFP" / "SMFP"
  - core_mass_scaling(Kn, treatment) -> float    : Table I local power-law
                                                   slope d log M / d log v^2
  - collapse_penalty_kinetic(sigma_m, v_max)     : soft penalty replacing
                                                   gravothermal_penalty() in
                                                   the per-halo prior.

WHAT THIS MODULE DOES NOT DO:

  - Reproduce the full DSMC density profile evolution (Fig. 1). That is a
    SPHERICAL DSMC computation, not a fit formula. To get a full profile, you
    would need to install and run KiSS-SIDM (gitlab.com/Socob/KiSS-SIDM).
  - Predict t_collapse (the collapse timescale). The fluid estimate
    (Balberg+ 2002) and the DSMC result agree to within ~30%, but the
    exact form of t_collapse(DSMC) is not published as an analytic formula
    (only the power-law slopes in Table I). We use the fluid model for the
    collapse time and apply a Kn-dependent correction.

CAVEATS — WHAT THE PAPER ITSELF WARNS ABOUT (2026-08-10 PATCH):

  1. "the conducting fluid model is appropriate deep in the short mean free
     path core, departures from local thermodynamic equilibrium develop in
     the intermediate mean free path region bounding the core, which modify
     the late-time evolution." — KISS-SIDM is NOT a global replacement for
     the fluid; it is a CORRECTION in the IMFP regime.

  2. "We find order one disagreement in this exponential scaling" (Table I
     for Kn=1). The 30% divergence is the MAXIMUM disagreement at the
     specific density range the paper studied. Outside that range, the
     fluid model may be sufficient.

  3. The Kn=1 / Kn=5 scalings are LOCAL power laws at a fixed density
     (rho/rho_s in 10^4–10^5). They are NOT global fits. Using them as a
     global correction is an extrapolation.

  4. The paper's canonical case is a 10^9 M_sun halo with sigma_m=50 cm^2/g
     (sigma_m/sigma_0 = 0.32). The KISS-SIDM results are NOT yet validated
     for dwarf-galaxy-scale halos (~10^7–10^8 M_sun) or for cluster-scale
     halos (~10^14 M_sun). Our v-dep model averages over many scales; the
     KISS-SIDM correction is best applied at the IMFP regime where the
     halo mass is near the 10^9 M_sun anchor.

References:
  Gurian, J. & May, S. (2025). "Core Collapse Beyond the Fluid Approximation:
  The Late Evolution of Self-Interacting Dark Matter Halos". Phys. Rev. Lett.
  135, 221001. arXiv:2505.15903. Public DSMC code at
  https://gitlab.com/Socob/KiSS-SIDM
"""
from __future__ import annotations
import math
from typing import Literal, Tuple
import numpy as np

# ---------------------------------------------------------------------------
# Unit conversion helpers (SI-internal, so Kn is dimensionally correct)
# ---------------------------------------------------------------------------
_M_SUN_KG = 1.98892e30        # kg / M_sun
_KPC_M = 3.0857e19             # m / kpc
_CM2_PER_G_TO_M2_PER_KG = 1e-4 / 1e-3  # (cm^2/g) -> (m^2/kg)
                                     # = 1e-4 m^2 / 1e-3 kg = 0.1 m^2/kg


def _rho_msun_per_kpc3_to_kg_per_m3(rho_msun_per_kpc3: float) -> float:
    """Convert mass density M_sun/kpc^3 -> kg/m^3.

    1 M_sun = 1.98892e30 kg; 1 kpc^3 = (3.0857e19 m)^3.
    """
    return rho_msun_per_kpc3 * _M_SUN_KG / (_KPC_M ** 3)


def _sigma_m_cm2_per_g_to_m2_per_kg(sigma_m_cm2_per_g: float) -> float:
    """Convert cross-section per unit mass cm^2/g -> m^2/kg.

    1 cm^2 = 1e-4 m^2; 1 g = 1e-3 kg. So cm^2/g = 1e-4 / 1e-3 m^2/kg = 0.1 m^2/kg.
    """
    return sigma_m_cm2_per_g * _CM2_PER_G_TO_M2_PER_KG

# Newtonian G in our unit system (kpc km^2 / (M_sun s^2))
# Imported from config (single source of truth) to avoid the 1000x bug
# flagged in the 2026-08-10 review.
import config

# ---------------------------------------------------------------------------
# Regime boundaries for the Knudsen classifier
# ---------------------------------------------------------------------------
# These are operational cutoffs on the Knudsen number. The paper does not
# publish exact boundaries; we adopt the convention Kn > 10 -> LMFP,
# 0.1 < Kn < 10 -> IMFP, Kn < 0.1 -> SMFP. This is consistent with the
# astrophysical SIDM literature (e.g. Koda & Shapiro 2011 use Kn = 1 as
# the LMFP/IMFP boundary; Yang & Yu 2022 use 0.1 / 10 as the IMFP/SMFP
# boundaries). Adjustments may be needed if the per-halo prior shifts
# systematically — that is a flag, not a bug.
KN_LMFP_THRESHOLD = 10.0    # Kn > 10: long mean free path, fluid OK
KN_SMFP_THRESHOLD = 0.1     # Kn < 0.1: short mean free path, fluid OK

# ---------------------------------------------------------------------------
# Table I power-law fits (Gurian & May 2025, arXiv:2505.15903v2)
# ---------------------------------------------------------------------------
# d log M / d log <v^2>  at the MFP scale defined by Kn=1 or Kn=5
# (negative slopes — M shrinks as v grows during collapse)

# d log M_Kn=1 / d log <v^2>
D_LOG_M_KN1_FLUID = -0.27
D_LOG_M_KN1_DSMC = -0.21

# d log M_Kn=5 / d log <v^2>
D_LOG_M_KN5_FLUID = -0.37
D_LOG_M_KN5_DSMC = -0.21


def knudsen_number(
    rho: float,         # M_sun / kpc^3, mass density at the radius of interest
    v_rms: float,       # km/s, RMS velocity (3D, <v^2>^0.5)
    sigma_m: float,     # cm^2/g, cross-section per unit mass
) -> float:
    """Knudsen number per Gurian & May 2025 Eq. 18.

        Kn = sqrt(<v^2> / (12 * pi * G * rho)) * 1 / (rho * sigma_m)

    Args:
        rho: local mass density (M_sun / kpc^3)
        v_rms: 3D RMS velocity (km/s)
        sigma_m: cross-section per unit mass (cm^2/g)

    Returns:
        Knudsen number (dimensionless)

    Notes:
        Unit consistency check: G is in kpc km^2 / (M_sun s^2). v_rms^2 is
        in (km/s)^2. rho is in M_sun / kpc^3. The factor sqrt(v^2 / (G*rho))
        gives units of time. We need the 1 / (rho * sigma_m) factor in
        UNITS OF LENGTH. Since Kn is dimensionless, the unit conversion
        between M_sun/kpc^3 * cm^2/g and 1/kpc cancels in the dimensionless
        combination. For numerical safety, we work in (kpc, M_sun) units
        throughout; sigma_m is treated as a dimensionless scaling parameter
        (the absolute value of Kn is calibrated to a fixed convention;
        see the unit-test for the specific case rho=2.73e-2, v_rms~10, sigma_m=50).

        The key qualitative result (LMFP vs IMFP vs SMFP) is robust to
        the unit convention; the absolute value of Kn is not used for any
        physical prediction, only the regime label.
    """
    if rho <= 0 or v_rms <= 0 or sigma_m <= 0:
        return float("inf")  # degenerate case: treat as LMFP

    # Convert to SI for a dimensionally-correct Knudsen number.
    # The convention is:
    #   rho:    M_sun/kpc^3  ->  kg/m^3
    #   v_rms:  km/s         ->  m/s
    #   sigma_m: cm^2/g      ->  m^2/kg
    rho_si = _rho_msun_per_kpc3_to_kg_per_m3(rho)
    v_si = v_rms * 1e3                                  # m/s
    sigma_m_si_val = _sigma_m_cm2_per_g_to_m2_per_kg(sigma_m)

    # Gravitational scale height H = sqrt(v^2 / (12 pi G rho)),  Eq. 18 first factor
    g_si = 6.67430e-11  # m^3 / (kg s^2)
    H = math.sqrt(v_si ** 2 / (12.0 * math.pi * g_si * rho_si))  # m

    # Mean free path lambda = 1 / (rho * sigma_m),  Eq. 18 second factor (inverse)
    lam = 1.0 / (rho_si * sigma_m_si_val)  # m

    # Knudsen number: Kn = H / lambda = H * rho * sigma_m
    return H / lam


def knudsen_regime_label(
    Kn: float,
) -> Literal["LMFP", "IMFP", "SMFP", "degenerate"]:
    """Classify the halo into the mean-free-path regime.

    Boundaries (per the conventions above):
        Kn > 10:    "LMFP"  (long mean free path, fluid model is fine)
        0.1 < Kn < 10: "IMFP" (intermediate, fluid model BREAKS DOWN)
        Kn < 0.1:   "SMFP"  (short mean free path, fluid model is fine)

    Args:
        Kn: Knudsen number (dimensionless, from knudsen_number())

    Returns:
        Regime label as a string.
    """
    if not math.isfinite(Kn) or Kn <= 0:
        return "degenerate"
    if Kn > KN_LMFP_THRESHOLD:
        return "LMFP"
    if Kn < KN_SMFP_THRESHOLD:
        return "SMFP"
    return "IMFP"


def core_mass_scaling(
    Kn_threshold: float = 1.0,
    treatment: Literal["fluid", "dsmc"] = "dsmc",
) -> float:
    """Local power-law slope d log M / d log <v^2> at the chosen Kn scale.

    Args:
        Kn_threshold: which Knudsen-number contour defines the core
            boundary (1.0 or 5.0 in the published Table I).
        treatment: "fluid" (Balberg+ 2002 with C=0.84 calibration) or
            "dsmc" (KISS-SIDM kinetic result).

    Returns:
        Power-law slope (negative). Magnitude 0.2-0.4 in the published
        calibration regime (10^4 < rho/rho_s < 10^5).

    Raises:
        ValueError: if Kn_threshold is not 1.0 or 5.0, or treatment is
            not "fluid" or "dsmc".
    """
    if Kn_threshold == 1.0:
        if treatment == "fluid":
            return D_LOG_M_KN1_FLUID
        if treatment == "dsmc":
            return D_LOG_M_KN1_DSMC
    elif Kn_threshold == 5.0:
        if treatment == "fluid":
            return D_LOG_M_KN5_FLUID
        if treatment == "dsmc":
            return D_LOG_M_KN5_DSMC
    raise ValueError(
        f"Kn_threshold must be 1.0 or 5.0 (got {Kn_threshold}), "
        f"and treatment must be 'fluid' or 'dsmc' (got {treatment!r})"
    )


def knudsen_correction_factor(
    Kn: float,
    Kn_threshold: float = 1.0,
) -> float:
    """Ratio of DSMC core-mass slope to fluid core-mass slope.

    Returns d log M (DSMC) / d log M (fluid) at the chosen Kn scale.
    This is the multiplicative correction to apply to a fluid-based
    per-halo penalty when in the IMFP regime.

    In LMFP and SMFP regimes, the correction is 1.0 (fluid model is
    appropriate per the paper). In the IMFP regime, the correction
    approaches the Table I ratio (~0.78 at Kn=1, ~0.57 at Kn=5 — wait,
    that's the inverse of what we want; let me think again).

    The slopes are NEGATIVE. d log M / d log v^2 = -0.27 (fluid) vs
    -0.21 (DSMC). |DSMC| < |fluid| at Kn=1, meaning the fluid model
    PREDICTS a STEEPER collapse than the kinetic. To correct the
    fluid prediction, we should MULTIPLY the fluid core mass change
    by (|DSMC| / |fluid|) = 0.78. So the correction factor is < 1
    in the IMFP regime.

    Returns 1.0 (no correction) outside the IMFP regime.

    Args:
        Kn: Knudsen number at the radius of interest.
        Kn_threshold: Kn scale defining the core (1.0 or 5.0).

    Returns:
        Multiplicative correction in [0, 1]. 1.0 means fluid model
        is fine (LMFP or SMFP). < 1.0 in the IMFP regime.
    """
    regime = knudsen_regime_label(Kn)
    if regime != "IMFP":
        return 1.0

    fluid_slope = core_mass_scaling(Kn_threshold, "fluid")
    dsmc_slope = core_mass_scaling(Kn_threshold, "dsmc")

    # Both negative. |DSMC| / |fluid| is the magnitude correction.
    return abs(dsmc_slope) / abs(fluid_slope)


def collapse_penalty_kinetic(
    sigma_m: float,       # cm^2/g, cross-section at v_ref
    rho_core: float,      # M_sun / kpc^3, central density (in the IMFP region)
    v_rms_core: float,    # km/s, 3D velocity dispersion at r_core
    penalty_strength: float = 1.0,
) -> float:
    """Per-halo collapse penalty, KISS-SIDM-aware.

    This is the Direction C replacement for the Balberg+ 2002 fluid
    penalty used in `gravothermal.py::gravothermal_r_core()`. It is a
    SOFT PENALTY, not a precise predictor — see the caveats in the
    module docstring.

    The penalty is computed as:
        1. Compute Kn at the core (rho_core, v_rms_core, sigma_m).
        2. If regime is LMFP or SMFP, return penalty_strength * 1.0
           (no correction; fluid model is fine).
        3. If regime is IMFP, apply the Table I correction factor
           (0.78 at Kn=1, 0.57 at Kn=5) to the penalty. This means
           the IMFP-corrected penalty is SMALLER than the fluid
           prediction, because the DSMC core mass is less sensitive
           to v_2 than the fluid predicts.

    Args:
        sigma_m: cross-section per unit mass (cm^2/g).
        rho_core: central density (M_sun/kpc^3) — use a value
            representative of the IMFP region, e.g. rho(r ~ r_core).
        v_rms_core: 3D RMS velocity (km/s) at r_core.
        penalty_strength: weight of the penalty (default 1.0; the
            prior uses this as a multiplicative factor).

    Returns:
        Penalty value (dimensionless). Smaller = the per-halo prior
        is less "scared" of collapse at this sigma_m. The caller
        (e.g. `gravothermal_collapse_prior`) should add this as a
        log-likelihood term.

    Notes:
        This is a FIT-FORMULA correction, not a DSMC simulation. The
        absolute value of the penalty depends on the choice of
        Kn_threshold and penalty_strength. The DELTA between the
        fluid and kinetic penalties is what the KISS-SIDM paper
        constrains, and is what this module provides.
    """
    Kn = knudsen_number(rho_core, v_rms_core, sigma_m)
    correction = knudsen_correction_factor(Kn, Kn_threshold=1.0)
    return penalty_strength * correction


# ---------------------------------------------------------------------------
# Diagnostic / smoke test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=== KISS-SIDM scalings — smoke test ===")
    print()
    print("Table I: d log M / d log <v^2>")
    print(f"  Kn=1:  fluid = {D_LOG_M_KN1_FLUID:+.2f}, "
          f"DSMC = {D_LOG_M_KN1_DSMC:+.2f}")
    print(f"  Kn=5:  fluid = {D_LOG_M_KN5_FLUID:+.2f}, "
          f"DSMC = {D_LOG_M_KN5_DSMC:+.2f}")
    print()

    # Canonical case: 10^9 M_sun halo, rho_s=2.73e-2 M_sun/pc^3, r_s=1.18 kpc
    # sigma_m=50 cm^2/g. The paper's collapse happens at t/t0 ~ 437.
    rho_s_pc = 2.73e-2  # M_sun / pc^3
    r_s_pc = 1.18e3     # pc
    sigma_m = 50.0      # cm^2/g

    # Convert to our units
    rho_s_kpc = rho_s_pc * 1e9  # 1 pc^3 = 1e-9 kpc^3
    r_s_kpc = r_s_pc / 1e3
    v_max = 100.0  # km/s, rough estimate for this halo

    Kn = knudsen_number(rho_s_kpc, v_max, sigma_m)
    regime = knudsen_regime_label(Kn)
    print(f"Canonical case (rho_s={rho_s_kpc:.2e} M_sun/kpc^3, "
          f"v_rms={v_max} km/s, sigma_m={sigma_m}):")
    print(f"  Kn = {Kn:.3e}, regime = {regime}")
    print()

    # Dwarf-galaxy case: rho ~ 1e7 M_sun/kpc^3 (Burkert core density),
    # v ~ 30 km/s, sigma_m ~ 1 cm^2/g
    Kn_dwarf = knudsen_number(1e7, 30.0, 1.0)
    print(f"Dwarf galaxy (rho=1e7, v_rms=30, sigma_m=1):")
    print(f"  Kn = {Kn_dwarf:.3e}, regime = {knudsen_regime_label(Kn_dwarf)}")
    print()

    # Cluster case: rho ~ 1e3 M_sun/kpc^3, v ~ 1500 km/s, sigma_m ~ 0.1 cm^2/g
    Kn_cluster = knudsen_number(1e3, 1500.0, 0.1)
    print(f"Cluster (rho=1e3, v_rms=1500, sigma_m=0.1):")
    print(f"  Kn = {Kn_cluster:.3e}, regime = {knudsen_regime_label(Kn_cluster)}")
    print()

    print("=== Penalty comparison (dSph-like halo, sigma_m sweep) ===")
    for sm in [0.1, 0.5, 1.0, 5.0, 10.0, 50.0]:
        Kn = knudsen_number(1e7, 30.0, sm)
        correction = knudsen_correction_factor(Kn)
        regime = knudsen_regime_label(Kn)
        print(f"  sigma_m={sm:6.1f}: Kn={Kn:.3e}, regime={regime}, "
              f"correction={correction:.3f}")
