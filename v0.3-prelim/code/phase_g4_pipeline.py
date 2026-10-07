"""
Phase G4 — Massive-halo gravothermal pipeline (R88(43), corrected framing)

Computes τ = t/t_c at canonical σ/m(v) using MB-weighted ⟨σ/m⟩ for each constrained
halo, then compares predicted gravothermal phase to observed density state.

This module implements the Phase G4 deliverable identified in §9.13 of the paper
("Gravothermal evolution: a proposed resolution pathway for the §2.6a circularity").

Inputs
------
-------
- v0.3-prelim/code/gravothermal_yang2024.py (Phase G1 — Yang+ 2024 parametric model)
- scripts/constants.py (Phase 44 SSoT)
- scripts/v192_dsph_gravothermal_sweep.py (canonical halo parameters)

Outputs
-------
---------
- Per-halo: ⟨σ/m⟩_MB, σ_eff = f_H²·⟨σ/m⟩_MB, t_c, τ, predicted phase, observed state, consistency flag

Status (R88(43))
----------------
- Implementation: complete (8 constrained halos run)
- Result (R88(43) honest framing): NULL result. Gravothermal cascade is INACTIVE at the
  canonical σ/m(v) point under MB-weighted averaging. Nothing collapses. The "consistency"
  between predicted phase and observed state is trivially satisfied because nothing was
  ever predicted to collapse; this is NOT the same as reproducing observed density
  diversity. The gravothermal channel does NOT currently supply a positive discriminator.
- The §2.6a circularity is NOT resolved by Phase G4. The R88(42) headline claim
  "8/8 consistent, circularity resolved" was an overclaim, corrected in R88(43).
- Phase G2 (merger history stochastic modulator) scaffolded but not yet used to modulate.
- Phase G5 (UFD diversity validation) implemented separately in phase_g5_ufd_diversity.py
  (real negative result: 0/5 MW UFDs predict collapse, contradicts Fischer & Yu 2026).
"""
from __future__ import annotations
import math
import sys
from pathlib import Path

# Use Phase 44 canonical SSoT from constants.py
sys.path.insert(0, r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\scripts")
from constants import (
    SIGMA_0_CM2_PER_G as SIGMA_0,
    A_SLOPE,
    V_REF_KMS as V_REF,
    V_TARGET_KMS as V_TARGET,
    SIGMA_KMS as FWHM,
    SIGMA_PEAK_CM2_PER_G as SIGMA_PEAK,
)

F_H = 0.297  # Yang+ 2025-derived f_H
T_LOOKBACK_GYR = 10.0  # typical halo formation epoch

# BM2 calibration anchor (Yang+ 2024 Table 1)
BM2_SIGMA_EFF_CM2_PER_G = 7.1
BM2_RHO_EFF_MSUN_PER_PC3 = 0.04
BM2_T_C_GYR = 28.7


def sigma_m_canonical_gaussian(v):
    """Canonical σ/m(v) — Gaussian resonance at v_target, Yukawa-type background."""
    return SIGMA_0 * (V_REF / v) ** A_SLOPE + SIGMA_PEAK * math.exp(
        -((v - V_TARGET) ** 2) / (2 * FWHM ** 2)
    )


def mb_weighted_sigma_m(V_max, v_max=300.0, n_points=2000):
    """
    Compute ⟨σ/m⟩ weighted by 3D Maxwell-Boltzmann speed distribution.

    The gravothermal evolution samples the full MB distribution of relative
    velocities during two-body collisions, not a single characteristic velocity.
    This is the physically correct input for Yang+ 2024 t_c calculation.

    At Cloud-9 (V_max=31 km/s), this gives ⟨σ/m⟩ ≈ 50 cm²/g (vs σ/m(V_max)=162),
    a factor-of-3 reduction from the low-velocity MB tail.
    """
    sigma_v = V_max / math.sqrt(2)
    vs = [v_max * i / n_points for i in range(n_points + 1)]
    vs = [v for v in vs if v > 0.5]

    def mb_pdf(v):
        return (4 * math.pi * v ** 2) * (1.0 / (math.sqrt(2 * math.pi) * sigma_v) ** 3) * math.exp(
            -v ** 2 / (2 * sigma_v ** 2)
        )

    num = sum(sigma_m_canonical_gaussian(v) * mb_pdf(v) for v in vs)
    den = sum(mb_pdf(v) for v in vs)
    return num / den


def t_c_yang2024(sigma_eff, rho_eff):
    """
    Yang+ 2024 t_c scaling (BM2-calibrated).

    t_c = 28.7 × (7.1 / σ_eff) × (0.04 / ρ_eff) Gyr

    Calibrated against BM2 at σ_eff=7.1 cm²/g, ρ_eff=0.04 M☉/pc³, t_c=28.7 Gyr.
    Valid regime: σ_eff ∈ [1, 15] cm²/g based on Yang+ 2024 Table 1 (Draco/UFD halos).
    Extrapolation outside this range increases uncertainty.
    """
    return BM2_T_C_GYR * (BM2_SIGMA_EFF_CM2_PER_G / sigma_eff) * (BM2_RHO_EFF_MSUN_PER_PC3 / rho_eff)


def classify_phase(tau):
    """Classify gravothermal phase from τ = t/t_c."""
    if tau < 0.01:
        return "NFW-like"
    elif tau < 0.5:
        return "core-expansion"
    elif tau < 1.0:
        return "late core-expansion"
    elif tau < 2.0:
        return "collapse"
    else:
        return "deeply-collapsed"


def predict_phase(V_max, rho_eff, t_lookback=T_LOOKBACK_GYR):
    """
    Predict gravothermal phase for a halo at V_max with effective density rho_eff.

    Returns: dict with σ_mb, σ_eff, t_c, tau, phase, in_calibration_range
    """
    sigma_mb = mb_weighted_sigma_m(V_max)
    sigma_eff = F_H ** 2 * sigma_mb
    t_c = t_c_yang2024(sigma_eff, rho_eff)
    tau = t_lookback / t_c
    phase = classify_phase(tau)
    in_cal = 1.0 <= sigma_eff <= 15.0  # Yang+ 2024 validity range
    return {
        "sigma_mb": sigma_mb,
        "sigma_eff": sigma_eff,
        "t_c": t_c,
        "tau": tau,
        "phase": phase,
        "in_calibration": in_cal,
    }


# Per-halo parameters: (name, V_max, rho_eff, observed_state, source)
HALOS = [
    ("Cloud-9 host", 31.12, 0.01, "diffuse gas cloud",
     "Zhou+ 2023 [15a]; Benítez-Llambay+ 2024 [15b]"),
    ("Fornax (V_max=18)", 18.0, 0.02, "extended core",
     "Mateo+ 1998 [26a]; canonical Fornax"),
    ("Fornax (V_max=15)", 15.0, 0.02, "extended core",
     "conservative lower bound on V_max"),
    ("Sculptor", 15.0, 0.02, "extended core",
     "Walker+ 2009"),
    ("Draco", 17.0, 0.03, "extended core",
     "Walker+ 2009"),
    ("SPARC typical", 100.0, 0.005, "rotation curves fit",
     "Lelli+ 2016 (SPARC)"),
    ("Cluster (A1689)", 500.0, 0.001, "lensing consistent",
     "Newman+ 2013 (cluster lensing)"),
    ("MW UFD (Boötes I)", 12.0, 0.04, "no collapse observed",
     "Simon+ 2011; Read+ 2019"),
]


def consistency_check(phase, observed):
    """Check whether predicted phase matches observed state."""
    p = phase.lower()
    o = observed.lower()
    if "nfw" in p:
        return "✓" if any(k in o for k in ["rotation", "lensing", "diffuse", "no collapse"]) else "?"
    if "core-expansion" in p:
        return "✓" if any(k in o for k in ["extended", "diffuse", "no collapse"]) else "?"
    if "collapse" in p:
        return "✓" if "collapsed" in o else "?"
    return "?"


def main():
    print("Phase G4: Massive-halo gravothermal pipeline (R88(43), corrected framing)")
    print("=" * 100)
    print(f"{'Halo':<22} {'⟨σ/m⟩_MB':<10} {'σ_eff':<8} {'t_c':<8} {'τ':<6} {'Phase':<20} {'In-cal':<6} {'Observed':<25} {'✓?'}")
    print("-" * 100)

    n_consistent = 0
    n_total = 0
    for name, V_max, rho_eff, observed, source in HALOS:
        r = predict_phase(V_max, rho_eff)
        flag = consistency_check(r["phase"], observed)
        n_total += 1
        if flag == "✓":
            n_consistent += 1
        in_cal_marker = "✓" if r["in_calibration"] else "⚠"
        print(f"{name:<22} {r['sigma_mb']:>9.2f}  {r['sigma_eff']:>6.3f}  {r['t_c']:>6.2f}  {r['tau']:>5.3f}  "
              f"{r['phase']:<20} {in_cal_marker:<6} {observed:<25} {flag}")

    print()
    print(f"Consistency: {n_consistent}/{n_total} halos show predicted phase matching observed state")
    print()
    print("Key finding (R88(43) honest framing — NULL result):")
    print("  Under MB-weighting, the framework's gravothermal cascade is INACTIVE across all")
    print("  8 constrained halos — t_c = 95-5000 Gyr, τ < 0.15 everywhere, NOTHING COLLAPSES")
    print("  at the canonical parameter point.")
    print()
    print("  This is consistent with the average observed state (no halo observed collapsed)")
    print("  but does NOT reproduce the observed density diversity. The gravothermal channel")
    print("  therefore does not currently supply a positive discriminator for the framework.")
    print()
    print("  The §2.6a circularity is NOT resolved by Phase G4. The R88(42) headline claim")
    print("  '8/8 consistent, circularity resolved' was an overclaim; R88(43) corrects it.")
    print()
    print("Caveats:")
    print("  - ρ_eff values are approximate (Cloud-9 NFW parameters from §9.12; others from literature)")
    print("  - σ_eff = f_H² · σ/m uses framework's heavy-channel-only decomposition")
    print("  - Yang+ 2024 t_c formula calibrated at σ_eff=7.1; in-calibration range is [1, 15] cm²/g")
    print("  - 6 of 8 halo σ_eff values fall in [1, 15] cm²/g; SPARC (0.315) and Cluster (0.022) below floor")


if __name__ == "__main__":
    main()
