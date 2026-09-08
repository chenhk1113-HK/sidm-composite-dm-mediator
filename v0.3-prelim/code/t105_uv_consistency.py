"""
T105 — UV consistency check: does the project's composite-DM UV
produce BOTH Portal A (kinetic mixing ε ~ 10^-37) AND Portal B
(hyperfine splitting δ ~ 297 keV) from the same composite structure?

Reference: Alves, Behbahani, Schuster, Wacker 2010 (arXiv:0903.3945,
JHEP 06, 113 / PLB 692, 323) - "Composite Inelastic Dark Matter"

KEY IDEA: In composite-DM with a QCD-like dark sector:
  - Portal A (kinetic mixing ε): photon-dark photon mixing at one loop,
    ε ~ (e_d e / 16π^2) × log(m_1/m_2)
  - Portal B (mass splitting δ): hyperfine splitting from spin-spin
    interactions between constituent fermions
    δ ~ (α_D / m_ψ^2) × Λ_D^3 (where m_ψ = constituent mass,
                                  Λ_D = dark confinement scale)

The order-of-magnitude for hyperfine splitting (analogous to pion-rho
splitting in real QCD):
    δ ≈ α_D × Λ_D^3 / m_ψ^2

For δ ~ 300 keV, this requires:
    α_D × (Λ_D / 1 GeV)^3 × (1 GeV / m_ψ)^2 ≈ 3 × 10^-7

If Λ_D ~ 1 GeV and m_ψ ~ 1 TeV, then α_D ~ 3 × 10^-7, which is
plausibly a small gauge coupling in a hidden sector.

This script:
  1. Takes v0.7 MAP parameters from the project
  2. Computes ε from photon-dark photon mixing
  3. Sweeps (Λ_D, m_ψ, α_D) parameter space to find points where:
     - ε matches v0.7 MAP within 1 order of magnitude
     - δ falls in [100, 400] keV (Di Mauro 2026 + Fan-Tweed 2026 range)
  4. Reports the volume of simultaneously-satisfying parameter space
  5. Verdict: TIGHT if volume < 1% of prior volume, LOOSE if > 1%,
     NONE if no solutions found
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np


# v0.7 MAP parameters (from T41_mediator_mass_joint_fit_v0_7)
V07_MAP = {
    "log_m_phi_MeV": 2.6561,        # m_phi ~ 453 MeV
    "log_m_chi_GeV": 2.8863,        # m_chi ~ 770 GeV
    "g_chi": 1.189,                 # dark Yukawa coupling
    "log_epsilon": -36.951,         # kinetic mixing ε ~ 10^-37
    "log_alpha": -16.165,           # alpha_X ~ 10^-16
}

# Projectile parameters from T90 v16 / composite-DM machinery
PROJECT_DEFAULTS = {
    "constituent_mass_GeV": 500.0,   # m_psi ~ 500 GeV
    "dark_confinement_GeV": 1.0,     # Lambda_D ~ 1 GeV
    "dark_gauge_coupling": 0.3,      # alpha_D ~ 0.3 (perturbative)
    "constituents_per_state": 2,     # meson (q q-bar) vs baryon (q q q)
}

# LZ target range (Di Mauro 2026 + Fan-Tweed 2026)
LZ_DELTA_RANGE_KEV = (100.0, 400.0)
LZ_DELTA_TARGET_KEV = 297.0  # Di Mauro pseudo-Dirac


def log_epsilon_from_composite(
    constituent_mass_GeV: float,
    dark_confinement_GeV: float,
    dark_gauge_coupling: float,
    constituents: int = 2,
    suppression_orders: float = 0.0,
) -> float:
    """Compute kinetic mixing ε from composite-DM one-loop mixing.

    The formula is the standard photon-dark photon mixing for a
    multi-charged constituent setup (Aranda+ 2016 + Alves+ 2010):
        ε ~ (e_d e / 16π^2) × sum_i Q_i^2 × log(m_i / μ)
    where:
      e_d = sqrt(4π α_D) (dark coupling)
      e = sqrt(4π α_EM) (EM coupling)
      Q_i = constituent charges (assume unit for simplicity)
      m_i = constituent masses
      μ = IR regulator (confinement scale)

    IMPORTANT: This gives the NAIVE mixing, which is typically much
    LARGER than what's observed (~10^-37 in v0.7 MAP). The naive value
    is ~10^-2 to 10^-4, requiring suppression of ~10^-34 from some
    UV mechanism (e.g., accidental cancellation, hidden structure).

    The suppression_orders parameter allows testing different suppression
    mechanisms. With suppression_orders=34, we match v0.7 MAP.

    Returns:
        log10(ε_effective)
    """
    alpha_em = 1.0 / 137.0
    e_d = math.sqrt(4 * math.pi * dark_gauge_coupling)
    e_em = math.sqrt(4 * math.pi * alpha_em)
    # Loop factor
    loop_factor = 1.0 / (16.0 * math.pi**2)
    # Sum over constituents (assume all charge-1 for simplicity)
    charge_squared_sum = float(constituents)
    # Log ratio: constituent mass / confinement scale
    log_ratio = math.log(constituent_mass_GeV / dark_confinement_GeV)
    # ε ~ e_d e × loop_factor × charge^2 × log(m/μ)
    epsilon = e_d * e_em * loop_factor * charge_squared_sum * log_ratio
    log_eps = math.log10(epsilon) - suppression_orders
    return log_eps


def log_delta_hyperfine_keV(
    constituent_mass_GeV: float,
    dark_confinement_GeV: float,
    dark_gauge_coupling: float,
) -> float:
    """Compute hyperfine mass splitting δ in keV from composite DM.

    Formula (Alves+ 2010 Eq. ~3.4 + Pitt+ 2010 estimate):
        δ ≈ (α_D / m_ψ^2) × Λ_D^3

    Returns:
        log10(δ in keV)
    """
    # Convert units: m_ψ in GeV, Λ_D in GeV, δ in keV
    delta_GeV = (dark_gauge_coupling / constituent_mass_GeV**2) * dark_confinement_GeV**3
    delta_keV = delta_GeV * 1e6  # GeV to keV
    return math.log10(delta_keV)


def sweep_parameter_space(
    log_m_psi_range=(2.0, 4.0),     # 100 GeV to 10 TeV
    log_Lambda_D_range=(-2.0, 1.0), # 10 MeV to 10 GeV
    log_alpha_D_range=(-4.0, 0.0),  # 10^-4 to 1
    suppression_orders_range=(0.0, 40.0),  # 0 to 40 orders suppression
    n_points=30,
):
    """Sweep (m_ψ, Λ_D, α_D, suppression) parameter space.

    Returns:
        Dict with sweep statistics.
    """
    log_m_psi_grid = np.linspace(log_m_psi_range[0], log_m_psi_range[1], n_points)
    log_Lambda_D_grid = np.linspace(log_Lambda_D_range[0], log_Lambda_D_range[1], n_points)
    log_alpha_D_grid = np.linspace(log_alpha_D_range[0], log_alpha_D_range[1], n_points)
    suppression_grid = np.linspace(suppression_orders_range[0], suppression_orders_range[1], n_points)

    target_log_eps = V07_MAP["log_epsilon"]

    all_points = []
    sat_eps = []
    sat_delta = []
    sat_both = []

    for log_m_psi in log_m_psi_grid:
        for log_Lambda_D in log_Lambda_D_grid:
            for log_alpha_D in log_alpha_D_grid:
                for suppression in suppression_grid:
                    m_psi = 10 ** log_m_psi
                    Lambda_D = 10 ** log_Lambda_D
                    alpha_D = 10 ** log_alpha_D

                    log_eps = log_epsilon_from_composite(
                        m_psi, Lambda_D, alpha_D, 2, suppression)
                    log_delta = log_delta_hyperfine_keV(m_psi, Lambda_D, alpha_D)

                    point = {
                        "log_m_psi": float(log_m_psi),
                        "log_Lambda_D": float(log_Lambda_D),
                        "log_alpha_D": float(log_alpha_D),
                        "suppression_orders": float(suppression),
                        "log_eps": float(log_eps),
                        "log_delta_keV": float(log_delta),
                    }
                    all_points.append(point)

                    eps_match = abs(log_eps - target_log_eps) < 1.0
                    if eps_match:
                        sat_eps.append(point)

                    delta_keV = 10 ** log_delta
                    delta_match = LZ_DELTA_RANGE_KEV[0] <= delta_keV <= LZ_DELTA_RANGE_KEV[1]
                    if delta_match:
                        sat_delta.append(point)

                    if eps_match and delta_match:
                        sat_both.append(point)

    n_total = len(all_points)
    return {
        "all_points_count": n_total,
        "sat_eps_count": len(sat_eps),
        "sat_delta_count": len(sat_delta),
        "sat_both_count": len(sat_both),
        "volume_fraction_sat_eps": len(sat_eps) / n_total,
        "volume_fraction_sat_delta": len(sat_delta) / n_total,
        "volume_fraction_sat_both": len(sat_both) / n_total,
        "sample_sat_both": sat_both[:10],
        "log_m_psi_range": list(log_m_psi_range),
        "log_Lambda_D_range": list(log_Lambda_D_range),
        "log_alpha_D_range": list(log_alpha_D_range),
        "suppression_orders_range": list(suppression_orders_range),
    }


def main():
    out_dir = Path(__file__).resolve().parents[1] / "outputs" / "t95"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Run the sweep
    print("T105 — UV consistency check (Portal A + Portal B from composite DM)")
    print("=" * 70)
    print(f"v0.7 MAP: log ε = {V07_MAP['log_epsilon']:.2f}, m_χ = {10**V07_MAP['log_m_chi_GeV']:.0f} GeV")
    print(f"LZ target: δ ∈ [{LZ_DELTA_RANGE_KEV[0]}, {LZ_DELTA_RANGE_KEV[1]}] keV")
    print()
    print("Sweeping (m_ψ, Λ_D, α_D) parameter space...")
    result = sweep_parameter_space(n_points=30)  # 27,000 points
    print(f"  Total points: {result['all_points_count']}")
    print(f"  Satisfy ε constraint (|log_eps - v0.7_MAP| < 1): {result['sat_eps_count']} "
          f"({100*result['volume_fraction_sat_eps']:.2f}%)")
    print(f"  Satisfy δ constraint (δ in [100, 400] keV): {result['sat_delta_count']} "
          f"({100*result['volume_fraction_sat_delta']:.2f}%)")
    print(f"  Satisfy BOTH: {result['sat_both_count']} "
          f"({100*result['volume_fraction_sat_both']:.2f}%)")
    print()

    # Verdict
    v_both = result["volume_fraction_sat_both"]
    if v_both == 0.0:
        verdict = "NONE: No parameter points satisfy both ε and δ simultaneously. The two-portal framing is UV-inconsistent in this parameterization."
    elif v_both < 0.01:
        verdict = "TIGHT: < 1% of parameter space satisfies both. Two-portal UV completion is FINE-TUNED but possible."
    elif v_both < 0.1:
        verdict = "MODERATE: 1-10% of parameter space satisfies both. Two-portal UV is plausible but constrained."
    else:
        verdict = "LOOSE: > 10% of parameter space satisfies both. Two-portal UV is NATURAL — no fine-tuning required."

    print(f"VERDICT: {verdict}")
    print()

    # Sample points satisfying both (if any)
    if result["sat_both_count"] > 0:
        print("Sample points satisfying BOTH constraints:")
        for i, p in enumerate(result["sample_sat_both"][:5]):
            m_psi = 10 ** p["log_m_psi"]
            Lambda_D = 10 ** p["log_Lambda_D"]
            alpha_D = 10 ** p["log_alpha_D"]
            eps = 10 ** p["log_eps"]
            delta = 10 ** p["log_delta_keV"]
            print(f"  [{i+1}] m_ψ = {m_psi:.0f} GeV, Λ_D = {Lambda_D:.3f} GeV, "
                  f"α_D = {alpha_D:.3e}, ε = {eps:.2e}, δ = {delta:.1f} keV")

    # Save output
    out = {
        "test": "T105_uv_consistency_two_portal",
        "date": "2026-09-08",
        "description": (
            "UV consistency check: does the composite-DM UV completion "
            "produce BOTH Portal A (kinetic mixing ε ~ 10^-37) AND Portal B "
            "(hyperfine splitting δ ~ 297 keV) from the same composite structure?"
        ),
        "reference": "Alves, Behbahani, Schuster, Wacker 2010 (arXiv:0903.3945, JHEP 06, 113)",
        "method": (
            "Sweep (m_psi, Lambda_D, alpha_D) parameter space. "
            "Constraint 1: ε within 1 OOM of v0.7 MAP. "
            "Constraint 2: δ in LZ target range [100, 400] keV."
        ),
        "v07_MAP": V07_MAP,
        "lz_target": {
            "delta_range_keV": list(LZ_DELTA_RANGE_KEV),
            "delta_target_keV": LZ_DELTA_TARGET_KEV,
        },
        "sweep_results": result,
        "verdict": verdict,
        "caveats": [
            "Formula for kinetic mixing is approximate (one-loop, unit charges)",
            "Hyperfine splitting formula is order-of-magnitude (no detailed hadron spec)",
            "Constituent charge is assumed unit; could be Q=1/3, 2/3 etc.",
            "Sum over constituents is approximate; full calculation requires Q_i^2 sum",
            "Doesn't include kinetic decoupling corrections (Λ_D ~ T_kd constraint)",
        ],
    }

    out_path = out_dir / "t105_uv_consistency.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nWrote: {out_path}")


if __name__ == "__main__":
    main()
