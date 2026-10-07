"""
Phase G7 verification (R88(51)) — answering reviewer's two questions.

This module implements the R88(50) Phase G7 two-resonance + segregation model
AND runs the two specific checks the reviewer demanded:

Q1: Does Phase G7 predict UFD collapse under Yang+ τ (using σ_HH, not σ_eff)?
    Answer (R88(51)): NO. τ < 0.07 for all 5 UFDs. Fischer & Yu remains a real failure.

Q2: Does the second resonance at v=150 violate any intermediate-v constraint?
    Answer (R88(51)): BORDERLINE at v=150 (σ_eff=0.45 vs galaxy-lensing 0.1-0.3).
    Cluster lensing (v=300-500) is fine; galaxy halo mapping is at the edge.

These are the honest-corrected results of Phase G7 with proper σ_HH vs σ_eff
distinction. Phase G7 substantially improved SPARC/Lei-Wang/Cloud-9/Horigome
but does NOT rescue Fischer & Yu (need higher σ_eff at UFD velocities).

Status (R88(51))
----------------
- Implementation: complete (two-resonance + segregation + corrected τ calculation)
- Result: Phase G7 helps Cloud-9/SPARC/Lei-Wang/Horigome but DOES NOT fix Fischer & Yu
- UFD σ_HH at v=8-12 km/s is only 0.6-0.8 cm²/g; Yang+ 2024 τ < 0.07 (no collapse)
- Second resonance at v=150 is BORDERLINE (must not over-produce galaxy-halo cores)
- Honest framing: Phase G7 is a better-tuned parameterization, not a derivation
"""
from __future__ import annotations
import math
import sys
from pathlib import Path

# === Phase G7 model parameters (R88(50)) ===
SIGMA_0 = 0.07
A_SLOPE = 0.9
V_REF = 100.0
V_TARGET_1 = 28.0
SIGMA_PEAK_1 = 350.0
WIDTH_1 = 4.0
V_TARGET_2 = 150.0
SIGMA_PEAK_2 = 5.0
WIDTH_2_SQ = 1500.0

F_H_CENTER = 0.6
R_SEG = 1.5
BETA = 0.7

# Yang+ 2024 calibration
BM2_T_C = 28.7
BM2_SIGMA_EFF = 7.1  # σ_HH anchor at BM2
BM2_RHO = 0.04


def sigma_m_phase_g7(v):
    """Two-resonance σ/m(v)."""
    return (SIGMA_0 * (V_REF / v) ** A_SLOPE +
            SIGMA_PEAK_1 * math.exp(-((v - V_TARGET_1) ** 2) / (2 * WIDTH_1 ** 2)) +
            SIGMA_PEAK_2 * math.exp(-((v - V_TARGET_2) ** 2) / WIDTH_2_SQ))


def f_H_segregation(r_over_rs):
    """Segregation profile: high in center, drops at large r."""
    return F_H_CENTER / (1 + (r_over_rs / R_SEG) ** BETA)


def sigma_eff_at(v, r_over_rs):
    """σ_eff = f_H(r)² · σ_m(v) — observable, f_H²-suppressed."""
    return f_H_segregation(r_over_rs) ** 2 * sigma_m_phase_g7(v)


def t_c_yang(sigma_HH, rho_eff):
    """Yang+ 2024 t_c — uses σ_HH (not σ_eff) per R88(49) Suggestion 1."""
    return BM2_T_C * (BM2_SIGMA_EFF / sigma_HH) * (BM2_RHO / rho_eff)


def classify_phase(tau):
    if tau < 0.01: return "NFW-like"
    elif tau < 0.5: return "core-expansion"
    elif tau < 1.0: return "late core-expansion"
    elif tau < 2.0: return "collapse"
    else: return "deeply-collapsed"


def question_1_ufd_collapse():
    """Q1: Does Phase G7 predict UFD collapse under Yang+ τ (σ_HH mode)?"""
    print("=" * 80)
    print("Q1: Phase G7 UFD collapse under Yang+ τ calculation (σ_HH, not σ_eff)")
    print("=" * 80)
    print()
    print("Fischer & Yu 2026 expectation: most MW UFDs in collapse phase (τ ≥ 1.0)")
    print()
    print(f"{'UFD':<18} {'V_max':<8} {'σ_HH (σ/m)':<12} {'ρ_eff':<10} {'t_c (Gyr)':<12} {'τ':<8} {'Phase'}")
    print("-" * 85)

    ufds = [
        ("Boötes I", 12.0, 0.04),
        ("Ursa Major II", 9.0, 0.05),
        ("Segue 1", 8.0, 0.06),
        ("Coma Berenices", 9.5, 0.045),
        ("Tucana II", 7.0, 0.07),
    ]

    n_collapse = 0
    results = []
    for name, V_max, rho_eff in ufds:
        sigma_hh = sigma_m_phase_g7(V_max)
        t_c = t_c_yang(sigma_hh, rho_eff)
        tau = 10.0 / t_c
        phase = classify_phase(tau)
        if "collapse" in phase: n_collapse += 1
        results.append((name, tau, phase))
        print(f"{name:<18} {V_max:<8.1f} {sigma_hh:<12.3f} {rho_eff:<10.3f} {t_c:<12.2f} {tau:<8.4f} {phase}")

    print()
    print(f"Verdict: {n_collapse}/5 UFDs predict collapse phase (τ ≥ 1.0)")
    print()
    if n_collapse >= 3:
        print("→ Phase G7 PREDICTS UFD COLLAPSE — Fischer & Yu is now consistent.")
    else:
        print("→ Phase G7 DOES NOT predict UFD collapse — Fischer & Yu is a REAL FAILURE.")
        print("  Root cause: σ_HH at v=8-12 km/s is only 0.6-0.8 cm²/g (background floor).")
        print("  Yang+ 2024 t_c ~ 150-350 Gyr → τ < 0.07 → no collapse on Hubble time.")
        print("  Possible fixes: (a) higher background at v=5-10 km/s, (b) third resonance at v~10,")
        print("  (c) Yang+ 2024 t_c underestimates collapse at high concentration.")
    return n_collapse


def question_2_intermediate_v():
    """Q2: Does the second resonance violate intermediate-v constraints?"""
    print()
    print("=" * 80)
    print("Q2: Second resonance at v=150 — does it violate intermediate-v constraints?")
    print("=" * 80)
    print()
    print(f"{'v (km/s)':<10} {'σ/m':<10} {'σ_eff(f_H=0.3)':<16} {'σ_eff(f_H=0.5)':<16} {'Constraint'}")
    print("-" * 80)

    constraints = [
        (50, "low-mass dwarf"),
        (100, "SPARC annulus"),
        (150, "second resonance peak"),
        (200, "intermediate v"),
        (250, "intermediate v"),
        (300, "group lensing"),
        (400, "group lensing"),
        (500, "cluster lensing"),
        (700, "cluster core"),
        (1000, "cluster outskirts"),
    ]

    for v, note in constraints:
        sm = sigma_m_phase_g7(v)
        se_03 = sm * 0.3 ** 2
        se_05 = sm * 0.5 ** 2
        print(f"{v:<10} {sm:<10.4f} {se_03:<16.4f} {se_05:<16.4f} {note}")

    print()
    print("Analysis:")
    print()
    print("At v=150 (peak): σ/m=5.05, σ_eff=0.45-1.26 — ABOVE He+ 2020 galaxy-halo mapping")
    print("  (~0.1-0.3 cm²/g). Borderline: would over-predict cores in MW-mass halos.")
    print()
    print("At v=300+: σ_eff << 0.01 — well below cluster/group lensing bounds.")
    print()
    print("Verdict: BORDERLINE at v=150. The second resonance is right at the edge of")
    print("galaxy-halo mapping data. If you reduce σ_peak2 below 3, Lei/Wang PASS goes away.")
    print("If you keep σ_peak2=5, you may over-produce cores in galaxy-mass halos (He+ 2020).")


def honest_summary():
    print()
    print("=" * 80)
    print("HONEST SUMMARY (R88(51))")
    print("=" * 80)
    print()
    print("Phase G7 (R88(50)) made the framework more flexible but not more predictive:")
    print()
    print("✓ Cloud-9: σ_eff ~ 59 (within factor 2 of Mace+ ≥50) — consistent")
    print("✓ SPARC: σ_eff = 0.091 (within factor 2 of 0.19 target) — consistent")
    print("✓ Lei/Wang: σ_eff = 0.45 (factor 4.5 above 0.1 threshold) — consistent")
    print("✓ Horigome: σ_eff = 0.059 (well below 0.8 ceiling) — no longer violated")
    print("⚠ Cluster: σ_eff = 0.0019 (factor 1.9 over 0.001 bound) — marginal")
    print("✗ Fischer & Yu UFD: σ_HH only 0.6-0.8 at v=8-12, τ < 0.07 → NOT in collapse")
    print()
    print("The Phase G7 model is a better-tuned parameterization, not a derivation.")
    print("The narrower peak + segregation + second resonance add 4 free functions,")
    print("each with the right physical motivation but no UV derivation.")
    print()
    print("Forward work:")
    print("  - Derive the segregation profile from two-component gravothermal physics")
    print("  - Constrain the second resonance via He+ 2020 galaxy-halo mapping (or similar)")
    print("  - Investigate whether Yang+ 2024 t_c underestimates UFD collapse at high concentration")
    print("  - OR accept that Phase G7 is the most this framework can do, and reframe accordingly")


def main():
    n_collapse = question_1_ufd_collapse()
    question_2_intermediate_v()
    honest_summary()


if __name__ == "__main__":
    main()
