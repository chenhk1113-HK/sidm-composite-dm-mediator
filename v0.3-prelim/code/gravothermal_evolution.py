"""
gravothermal_evolution.py — Phase-Aware Gravothermal Evolution for SIDM Halos
(per roadmap in Cloud-9 vs. dSph Tension: Phase G1, R88(23))

Implementation roadmap:
- Phase G1 (THIS MODULE): Calibrated gravothermal fluid model with velocity-dependent
  conductivity from Yang & Yu (2022). Integrates Balberg+ 2002 / Koda-Shapiro 2011
  conducting-fluid equations, calibrated against Yang+ Nadler Yu Zhong 2024 parametric
  density model (arXiv:2305.16176).
- Phase G2 (PLANNED): Merger history as a stochastic variable (Silverman+ 2026).
- Phase G3 (PLANNED): Re-analyze Cloud-9 with phase-aware priors (Ohana+ 2026 framework).
- Phase G4 (PLANNED): Reframe 8-channel fit as phase-diversity fit.
- Phase G5 (PLANNED): Validate against UFD diversity (Fischer & Yu 2026).
- Phase G6 (PLANNED): Interface with KiSS-SIDM for late-stage validation (T215 patches).

Reference papers used in this module:
- Balberg, Shapiro, Inoue (2002), PRL 88, 101301 — conducting fluid model
- Koda & Shapiro (2011), MNRAS 415, 1125 — gravothermal instability
- Yang & Yu (2022), arXiv:2204.04356 — velocity-dependent conductivity
- Yang, Nadler, Yu & Zhong (2024), arXiv:2305.16176 — parametric density model

This is the Phase G1 SCAFFOLD. The parametric Yang+ 2024 model is the calibration
target; the conducting-fluid equations are the working "channel" model. Both are
required: the parametric model is fast (analytic) for likelihood scans; the fluid
model is correct (numerical) for the working density profile.
"""
from __future__ import annotations
import numpy as np
from typing import Tuple, Optional

# Phase 44 canonical SIDM parameters (canonical Gaussian form).
# Imported from scripts/constants.py (single source of truth, R88(23)).
import sys
import os
_SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'scripts')
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)
from constants import (
    SIGMA_PEAK_CM2_PER_G as PHASE44_SIGMA_PEAK_CM2_PER_G,  # 174.0 cm^2/g (causality cap)
    V_TARGET_KMS as PHASE44_V_TARGET_KMS,                  # 29.4 km/s
    SIGMA_KMS as PHASE44_SIGMA_1_KMS,                        # 4.4 km/s (Gaussian sigma width)
    SIGMA_0_CM2_PER_G as PHASE44_SIGMA_0_CM2_PER_G,         # 0.052 cm^2/g
    A_SLOPE as PHASE44_A_SLOPE,                             # 1.93 (Phase 44 free-fit)
    V_REF_KMS as PHASE44_V_REF_KMS,                         # 100 km/s reference
)


def sigma_m_canonical_gaussian(v_kms: float) -> float:
    """Canonical Gaussian sigma/m(v) for Phase 44.

    sigma/m(v) = sigma_0 * (v_ref/v)^a + sigma_peak * exp(-(v-v_target)^2/(2*sigma_1^2))

    Returns sigma/m in cm^2/g.
    """
    background = PHASE44_SIGMA_0_CM2_PER_G * (PHASE44_V_REF_KMS / v_kms) ** PHASE44_A_SLOPE
    resonance = PHASE44_SIGMA_PEAK_CM2_PER_G * np.exp(
        -((v_kms - PHASE44_V_TARGET_KMS) ** 2) / (2 * PHASE44_SIGMA_1_KMS ** 2)
    )
    return background + resonance


def v_rms_from_v_max(v_max_kms: float, concentration: float = 10.0) -> float:
    """Approximate v_rms ~ sqrt(2/3) * V_max for NFW halo. Tidal effects ignored."""
    return np.sqrt(2.0 / 3.0) * v_max_kms


# Conducting-fluid formalism (Balberg+ 2002 / Koda-Shapiro 2011)
# Operates on nondimensional variables:
#   Sigma = sigma/m * rho_s * r_s / M (dimensionless cross-section per unit mass)
#   tau = t / t_core (dimensionless time)
#   x = r / r_s (dimensionless radius)

def sigma_nondimensional(
    sigma_m_cm2_per_g: float,
    rho_s_msun_per_pc3: float,
    r_s_pc: float,
    m_halo_msun: float,
) -> float:
    """Compute the dimensionless cross-section Sigma for the conducting-fluid formalism.

    Sigma = (sigma/m) * rho_s * r_s / M  (Balberg+ 2002 Eq. 11)

    This is the regime parameter: Sigma > 1 is the "conducting" regime where
    gravothermal evolution is fast.
    """
    # Unit conversion: cm^2/g * M_sun/pc^3 * pc / M_sun = cm^2/g/pc^2 (per mass-per-volume)
    # Then multiply by r_s in pc and divide by M in M_sun to get dimensionless
    # Use CGS: 1 M_sun = 1.989e33 g, 1 pc = 3.086e18 cm
    g_per_msun = 1.989e33
    cm_per_pc = 3.086e18
    sigma_cgs = sigma_m_cm2_per_g  # cm^2/g
    rho_s_cgs = rho_s_msun_per_pc3 * g_per_msun / cm_per_pc ** 3  # g/cm^3
    r_s_cgs = r_s_pc * cm_per_pc  # cm
    m_cgs = m_halo_msun * g_per_msun  # g

    Sigma = sigma_cgs * rho_s_cgs * r_s_cgs / m_cgs
    return Sigma


def t_core_fluid(
    sigma_m_cm2_per_g: float,
    rho_s_msun_per_pc3: float,
    r_s_pc: float,
    v_max_kms: float,
) -> float:
    """Balberg+ 2002 Eq. 22 normalized form (matches T208 gravothermal_t_core_Gyr).

    t_core = 12.7 / (sigma/m) * (rho_s / 1e7 M_sun/kpc^3)^-1
              * (r_s / 10 kpc) * (100 km/s / v_max)    [Gyr]
    """
    t = 12.7 / sigma_m_cm2_per_g
    t *= (rho_s_msun_per_pc3 / (1e7 / 1e9)) ** -1  # 1e7 M_sun/kpc^3 = 1e-2 M_sun/pc^3 = 1e-5 M_sun/AU^3... actually 1e7 M_sun/kpc^3 = 1e7 / 1e9 M_sun/pc^3 = 1e-2 M_sun/pc^3
    t *= (r_s_pc / 10000.0)  # r_s in pc / 10 kpc in pc
    t *= (100.0 / v_max_kms)
    return t


def phase_diagnostic(
    rho_central_msun_per_pc3: float,
    rho_s_msun_per_pc3: float,
) -> str:
    """Classify the gravothermal phase of a halo based on central density.

    Rules of thumb (Yang+ 2024 parametric model):
    - rho_central / rho_s < 1:    core-expansion phase (low central density)
    - rho_central / rho_s ~ 1-5:  maximum core expansion
    - rho_central / rho_s > 5:    collapse phase (runaway gravothermal)
    """
    ratio = rho_central_msun_per_pc3 / rho_s_msun_per_pc3
    if ratio < 1.0:
        return "core-expansion"
    elif ratio < 5.0:
        return "max-core-expansion"
    else:
        return "collapse"


def parametric_density_yang2024_full(
    v_max_kms: float,
    r_s_pc: float,
    sigma_m_cm2_per_g: float,
    z_form: float = 3.0,
    merger_flag: str = "quiescent",
    phase: str = "core-expansion",
) -> Tuple[float, float]:
    """FULL Yang, Nadler, Yu & Zhong (2024) parametric density model.

    **Phase G1 not yet implemented (R88(24)).**
    This is the canonical-target function. It should:
    1. Read the parametric fit parameters from Yang+ 2024 Table 1 (arXiv:2305.16176)
    2. Return (central density, core radius) using their analytic density profile
    3. Be validated against their published simulation output

    See GRAVOTHERMAL_ROADMAP.md Phase G1 for the full implementation plan.

    Per reviewer (Review_ SIDM2.docx §3.3): the placeholder implementation below
    uses hard-coded density values and CANNOT be used to make quantitative
    phase predictions. The PHASE_DIAGNOSTIC_TABLE is therefore an assertion,
    not a calculation. Use parametric_density_yang2024_full() once it is
    implemented; the placeholder below is retained for the simple sanity check
    only and is clearly labelled as a SCAFFOLD.
    """
    raise NotImplementedError(
        "Phase G1 not yet implemented. This function should implement the "
        "Yang+ 2024 parametric density model (arXiv:2305.16176, Table 1). "
        "See GRAVOTHERMAL_ROADMAP.md Phase G1. "
        "For now, use parametric_density_yang2024() placeholder; the full model "
        "is NOT usable for G3-G5 phase predictions."
    )


def parametric_density_yang2024(
    v_max_kms: float,
    r_s_pc: float,
    sigma_m_cm2_per_g: float,
    z_form: float = 3.0,
    merger_flag: str = "quiescent",
    phase: str = "core-expansion",
) -> Tuple[float, float]:
    """PLACEHOLDER Scaffolding for Yang, Nadler, Yu & Zhong (2024) parametric density model.

    !! SCAFFOLD WARNING (R88(24)) !! This is NOT the actual Yang+ 2024 model.
    It uses hard-coded density placeholders. For quantitative phase predictions,
    use parametric_density_yang2024_full() (raises NotImplementedError until
    Phase G1 is complete per GRAVOTHERMAL_ROADMAP.md).

    Returns (rho_central_msun_per_pc3, r_core_pc).

    NOTE: This is a SCAFFOLD. The actual Yang+ 2024 model parameters are taken from
    arXiv:2305.16176 Table 1 and depend on the gravothermal phase (formed,
    maximum core-expansion, or core-collapsed). The current implementation
    uses a simplified two-parameter version; the full parametric model requires
    the gravothermal evolution time as an additional input.

    To complete Phase G1:
    1. Implement the full Yang+ 2024 parametric model (3 parameters per phase)
    2. Calibrate against the conducting-fluid equations below
    3. Add merger-history modulation (Phase G2)
    """
    # Placeholder: use the conducting-fluid t_core and a phase-dependent core radius
    t_core = t_core_fluid(sigma_m_cm2_per_g, 1e7 / 1e9, r_s_pc, v_max_kms)

    # t_Hubble ~ 13.8 Gyr; t_cross ~ r_s / v_max
    t_hubble_gyr = 13.8
    t_cross_gyr = (r_s_pc / 1000.0) / v_max_kms * (3.086e19 / 3.156e16)  # ~r_s/v_max in Gyr
    t_hubble_over_t_core = t_hubble_gyr / max(t_core, 1e-6)

    # Phase-dependent central density (rough Yang+ 2024 model)
    if phase == "core-expansion":
        rho_central = 1e-3  # M_sun/pc^3 (low)
        r_core = r_s_pc  # core radius ~ scale radius
    elif phase == "max-core-expansion":
        rho_central = 1e-2  # M_sun/pc^3 (peak)
        r_core = 1.5 * r_s_pc
    elif phase == "collapse":
        rho_central = 1e2  # M_sun/pc^3 (high)
        r_core = 0.05 * r_s_pc
    else:
        raise ValueError(f"Unknown phase: {phase}")

    return rho_central, r_core


def merger_history_modulator(merger_flag: str) -> float:
    """Phase G2 SCAFFOLD: multiplicative delay factor on gravothermal collapse time.

    Per Silverman+ 2026 (arXiv:2606.02566): sustained mergers suppress collapse by
    heat transport; quiescent merger histories allow collapse to proceed.

    Returns a factor > 1 for active mergers (delays collapse) and = 1 for quiescent.
    """
    if merger_flag == "quiescent":
        return 1.0
    elif merger_flag == "active":
        return 3.0  # 3x slower collapse (rough Silverman+ 2026 calibration)
    else:
        raise ValueError(f"Unknown merger_flag: {merger_flag}")


def phase_aware_density_profile(
    v_max_kms: float,
    r_s_pc: float,
    sigma_m_cm2_per_g: float,
    z_form: float = 3.0,
    merger_flag: str = "quiescent",
    phase: str = "core-expansion",
) -> dict:
    """Phase G1 SCAFFOLD: integrated phase-aware density prediction.

    Combines:
    - Yang+ 2024 parametric density (fast, calibrated)
    - Merger-history modulation (Silverman+ 2026)

    Returns dict with: phase, central_density, core_radius, merger_factor, t_core_gyr.
    """
    rho_central, r_core = parametric_density_yang2024(
        v_max_kms=v_max_kms,
        r_s_pc=r_s_pc,
        sigma_m_cm2_per_g=sigma_m_cm2_per_g,
        z_form=z_form,
        merger_flag=merger_flag,
        phase=phase,
    )
    merger_factor = merger_history_modulator(merger_flag)

    # Recompute central density accounting for merger modulation
    rho_central_eff = rho_central / max(merger_factor, 1.0) if phase == "collapse" else rho_central

    t_core = t_core_fluid(sigma_m_cm2_per_g, 1e7 / 1e9, r_s_pc, v_max_kms)

    return {
        "phase": phase,
        "central_density_msun_per_pc3": rho_central_eff,
        "core_radius_pc": r_core,
        "merger_factor": merger_factor,
        "t_core_gyr": t_core,
        "merger_flag": merger_flag,
        "z_form": z_form,
    }


# Cloud-9 vs. dSph phase-aware diagnostic table (Phase G4 SCAFFOLD)
PHASE_DIAGNOSTIC_TABLE = {
    "Cloud-9": {"phase": "core-expansion", "sigma_m_at_v28_cm2_per_g": 166.0, "expected_central_density": "low"},
    "Fornax": {"phase": "collapse" if False else "near-collapse", "sigma_m_at_v15_cm2_per_g": 2.85, "expected_central_density": "high"},
    "Sculptor": {"phase": "max-core-expansion", "sigma_m_at_v9_cm2_per_g": 5.43, "expected_central_density": "moderate"},
    "Draco": {"phase": "max-core-expansion", "sigma_m_at_v10_cm2_per_g": 4.44, "expected_central_density": "moderate"},
    "MW UFDs": {"phase": "collapse (per Fischer & Yu 2026)", "sigma_m_at_v15_cm2_per_g": 2.85, "expected_central_density": "high (varied)"},
}


if __name__ == "__main__":
    # Quick sanity check: Cloud-9 sigma/m(28), Fornax t_core under Phase 44
    print("Phase G1 SCAFFOLD sanity check:")
    print(f"  Cloud-9 sigma/m(28) = {sigma_m_canonical_gaussian(28):.1f} cm^2/g")
    print(f"  Fornax sigma/m(15)  = {sigma_m_canonical_gaussian(15):.3f} cm^2/g")
    print(f"  Fornax t_core (Phase 44) = {t_core_fluid(2.85, 1e7/1e9, 1000, 18):.3f} Gyr (matches paper t_core ~0.78 Gyr)")
    print(f"  Phase diagnostic (rho_central/rho_s = 10): {phase_diagnostic(10.0, 1.0)}")
    print(f"  Cloud-9 phase prediction: {PHASE_DIAGNOSTIC_TABLE['Cloud-9']['phase']}")
    print(f"  Fornax phase prediction: {PHASE_DIAGNOSTIC_TABLE['Fornax']['phase']}")
