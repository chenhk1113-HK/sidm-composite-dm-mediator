"""
Phase 44 — Multi-channel joint fit (Item 2).

Joints three observational channels:
  1. SPARC: Phase 33d result (115/127 galaxies pass Vflat band test)
  2. JVAS B1938+666: Phase 34a result (sigma/m(15) = 1.19 vs required 100, fails 84x)
  3. Cloud-9: Ultra-faint dwarf constraint (sigma/m(28) = 100, passes)

For our multi-resonant sigma/m(v), compute the predicted sigma/m at the
characteristic velocity for each channel, then evaluate how well the multi-
resonant parameter set satisfies all three.

This is a LIKELIHOOD-level joint fit, not just a pass/fail test.
"""
from __future__ import annotations
import json
import sys
import warnings
from pathlib import Path

import numpy as np
from scipy.optimize import minimize, differential_evolution
from scipy.stats import norm

warnings.filterwarnings("ignore")

sys.path.insert(0, r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\code")

from t90_v70_multi_resonant_darkqcd import (
    sigma_m_multi_resonant,
    velocity_dependent_background,
)
from t90_v50_resonant_sidm import kinetic_energy_eV

RESULTS_DIR = Path(r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


# =========================================================================
# MULTI-RESONANT SIGMA/M EVALUATOR
# =========================================================================

def sigma_m_at_v(v_kms, m_chi, resonances, sigma_0, a_slope):
    """Evaluate multi-resonant sigma/m at given velocity."""
    sigma_0_v = velocity_dependent_background(v_kms, sigma_0, a_slope)
    r = sigma_m_multi_resonant(v_kms, m_chi, resonances, sigma_0_v, 0.0)
    return r["sigma_m_total"]


# =========================================================================
# CHANNEL LOG-LIKELIHOODS
# =========================================================================

def logL_sparc(sigma_m_v100, sigma_m_v28):
    """SPARC Vflat band likelihood.

    From Phase 33d: Vflat test passes for sigma/m(100) in [0.05, 0.5] cm^2/g
    Approximate as Gaussian centered at 0.07 with width 0.05 (the fitted T90.70 value).
    Also requires sigma/m(28) ~ 100 for dwarfs.
    """
    # Target band for sigma/m(100): [0.05, 0.15] from posterior
    target_v100 = 0.07
    sigma_band = 0.05
    if sigma_m_v100 <= 0:
        return -np.inf
    logL = norm.logpdf(sigma_m_v100, loc=target_v100, scale=sigma_band)
    return logL


def logL_jvas(sigma_m_v15):
    """JVAS B1938+666 strong-lens perturber constraint.

    From Phase 34a: JVAS requires sigma/m(15) ~ 100 cm^2/g for core collapse.
    If sigma/m(15) < 30, no collapse → fails the test.

    Modeled as: logL = log Gaussian centered at 100 with width 30.
    """
    target = 100.0
    width = 30.0
    if sigma_m_v15 <= 0:
        return -np.inf
    return norm.logpdf(sigma_m_v15, loc=target, scale=width)


def logL_cloud9(sigma_m_v28):
    """Cloud-9 ultra-faint dwarf constraint.

    From Phase 32: sigma/m(28) ~ 100 cm^2/g for core formation in ultra-faint dwarfs.
    """
    target = 100.0
    width = 30.0
    if sigma_m_v28 <= 0:
        return -np.inf
    return norm.logpdf(sigma_m_v28, loc=target, scale=width)


def logL_dwarfs_no_collapse(sigma_m_v15, sigma_m_v28):
    """Penalty for dwarf cores collapsing when they shouldn't.

    Fornax, Sculptor, etc. should NOT collapse → sigma/m(15) < 5.
    Cloud-9 should collapse → sigma/m(28) ~ 100.
    """
    # sigma/m(15) for Fornax-like dwarfs should be < 5
    if sigma_m_v15 > 5.0:
        return -10.0  # penalty
    return 0.0


def joint_logL(params, channels=("sparc", "jvas", "cloud9")):
    """Joint log likelihood across channels.

    params: (m_chi, sigma_0, a_slope, v_targets[4], sigma_peaks[4], width_fracs[4])
    Total: 13 params
    """
    m_chi, sigma_0, a_slope = params[0], params[1], params[2]
    v_targets = params[3:7]
    sigma_peaks = params[7:11]
    width_fracs = params[11:15]

    # Build resonances
    resonances = []
    for i, v_t in enumerate(v_targets):
        E_R = kinetic_energy_eV(v_t, m_chi)
        resonances.append({
            "name": f"R{i}",
            "E_R_eV": E_R,
            "Gamma_eV": width_fracs[i] * E_R,
            "sigma_peak_cm2_per_g": sigma_peaks[i],
            "v_target_kms": v_t,
        })

    # Compute sigma/m at characteristic velocities
    try:
        sigma_v15 = sigma_m_at_v(15.0, m_chi, resonances, sigma_0, a_slope)
        sigma_v28 = sigma_m_at_v(28.0, m_chi, resonances, sigma_0, a_slope)
        sigma_v100 = sigma_m_at_v(100.0, m_chi, resonances, sigma_0, a_slope)
    except Exception:
        return -1e10

    if sigma_v15 < 0 or sigma_v28 < 0 or sigma_v100 < 0:
        return -1e10

    logL = 0.0
    if "sparc" in channels:
        logL += logL_sparc(sigma_v100, sigma_v28)
    if "jvas" in channels:
        logL += logL_jvas(sigma_v15)
    if "cloud9" in channels:
        logL += logL_cloud9(sigma_v28)

    # Add penalty for dwarf cores collapsing
    logL += logL_dwarfs_no_collapse(sigma_v15, sigma_v28)

    return logL


def main():
    print("Phase 44 — Multi-channel joint fit (SPARC + JVAS + Cloud-9)")
    print()

    channels = ("sparc", "jvas", "cloud9")

    # T90.70 baseline parameters
    m_chi_0 = 6.58
    sigma_0_0 = 0.195
    a_slope_0 = 0.7
    v_targets_0 = [28.0, 100.0, 300.0, 700.0]
    sigma_peaks_0 = [100.0, 0.07, 0.1, 0.01]
    width_fracs_0 = [0.05, 0.05, 0.05, 0.10]

    x0 = [m_chi_0, sigma_0_0, a_slope_0] + v_targets_0 + sigma_peaks_0 + width_fracs_0

    # Compute T90.70 baseline logL
    baseline_logL = joint_logL(x0)
    print(f"T90.70 baseline logL = {baseline_logL:.2f}")
    print(f"  sigma/m(15) = {sigma_m_at_v(15.0, m_chi_0, [], sigma_0_0, a_slope_0):.2f} cm^2/g (JVAS wants ~100)")
    print(f"  sigma/m(28) = {sigma_m_at_v(28.0, m_chi_0, [], sigma_0_0, a_slope_0):.2f} cm^2/g (Cloud-9 wants ~100)")
    print(f"  sigma/m(100) = {sigma_m_at_v(100.0, m_chi_0, [], sigma_0_0, a_slope_0):.2f} cm^2/g (SPARC wants ~0.07)")
    print()

    # Define parameter bounds
    # m_chi [1, 50], sigma_0 [0.01, 1.0], a_slope [0.0, 2.0]
    # v_targets: keep at fixed T90.70 values (4 resonances)
    # sigma_peaks: allow re-tuning
    # width_fracs: allow re-tuning
    bounds = [
        (1.0, 50.0),     # m_chi
        (0.01, 1.0),     # sigma_0
        (0.0, 2.0),      # a_slope
        (20, 50),        # v_target[0] (28 +/-)
        (50, 200),       # v_target[1] (100 +/-)
        (200, 500),      # v_target[2] (300 +/-)
        (500, 1000),     # v_target[3] (700 +/-)
        (10, 200),       # sigma_peak[0]
        (0.01, 1.0),     # sigma_peak[1]
        (0.01, 1.0),     # sigma_peak[2]
        (0.001, 0.5),    # sigma_peak[3]
        (0.01, 0.20),    # width_frac[0]
        (0.01, 0.20),    # width_frac[1]
        (0.01, 0.20),    # width_frac[2]
        (0.01, 0.30),    # width_frac[3]
    ]

    # Compute T90.70 sigma/m at velocities (using resonances)
    resonances_0 = []
    for i, v_t in enumerate(v_targets_0):
        E_R = kinetic_energy_eV(v_t, m_chi_0)
        resonances_0.append({
            "name": f"R{i}",
            "E_R_eV": E_R,
            "Gamma_eV": width_fracs_0[i] * E_R,
            "sigma_peak_cm2_per_g": sigma_peaks_0[i],
            "v_target_kms": v_t,
        })

    def sigma_v(v, m_chi, resonances, sigma_0, a_slope):
        sigma_0_v = velocity_dependent_background(v, sigma_0, a_slope)
        r = sigma_m_multi_resonant(v, m_chi, resonances, sigma_0_v, 0.0)
        return r["sigma_m_total"]

    print(f"T90.70 baseline with resonances:")
    print(f"  sigma/m(15) = {sigma_v(15.0, m_chi_0, resonances_0, sigma_0_0, a_slope_0):.4f}")
    print(f"  sigma/m(28) = {sigma_v(28.0, m_chi_0, resonances_0, sigma_0_0, a_slope_0):.4f}")
    print(f"  sigma/m(100) = {sigma_v(100.0, m_chi_0, resonances_0, sigma_0_0, a_slope_0):.4f}")
    print()

    # Run differential evolution to find best-fit params
    print("Running differential evolution...")
    result = differential_evolution(
        lambda x: -joint_logL(x),
        bounds,
        seed=42,
        maxiter=100,
        popsize=15,
        tol=1e-4,
        workers=1,
    )

    best_params = result.x
    best_logL = -result.fun
    print(f"Best log L = {best_logL:.2f}")
    print(f"Best params: m_chi={best_params[0]:.2f}, sigma_0={best_params[1]:.3f}, a_slope={best_params[2]:.3f}")
    print(f"  v_targets = {best_params[3:7]}")
    print(f"  sigma_peaks = {best_params[7:11]}")
    print(f"  width_fracs = {best_params[11:15]}")
    print()

    # Compute sigma/m at key velocities with best-fit
    m_chi_b, sigma_0_b, a_slope_b = best_params[0], best_params[1], best_params[2]
    v_targets_b = best_params[3:7]
    sigma_peaks_b = best_params[7:11]
    width_fracs_b = best_params[11:15]
    resonances_b = []
    for i, v_t in enumerate(v_targets_b):
        E_R = kinetic_energy_eV(v_t, m_chi_b)
        resonances_b.append({
            "name": f"R{i}",
            "E_R_eV": E_R,
            "Gamma_eV": width_fracs_b[i] * E_R,
            "sigma_peak_cm2_per_g": sigma_peaks_b[i],
            "v_target_kms": v_t,
        })
    print(f"Best-fit sigma/m at key velocities:")
    print(f"  sigma/m(15)  = {sigma_v(15.0, m_chi_b, resonances_b, sigma_0_b, a_slope_b):.3f} (JVAS wants ~100)")
    print(f"  sigma/m(28)  = {sigma_v(28.0, m_chi_b, resonances_b, sigma_0_b, a_slope_b):.3f} (Cloud-9 wants ~100)")
    print(f"  sigma/m(100) = {sigma_v(100.0, m_chi_b, resonances_b, sigma_0_b, a_slope_b):.3f} (SPARC wants ~0.07)")
    print(f"  sigma/m(300) = {sigma_v(300.0, m_chi_b, resonances_b, sigma_0_b, a_slope_b):.3f}")
    print(f"  sigma/m(700) = {sigma_v(700.0, m_chi_b, resonances_b, sigma_0_b, a_slope_b):.3f}")
    print()

    # Channel-by-channel logL
    sigma_v15 = sigma_v(15.0, m_chi_b, resonances_b, sigma_0_b, a_slope_b)
    sigma_v28 = sigma_v(28.0, m_chi_b, resonances_b, sigma_0_b, a_slope_b)
    sigma_v100 = sigma_v(100.0, m_chi_b, resonances_b, sigma_0_b, a_slope_b)
    print("Channel-by-channel log L (best-fit):")
    print(f"  SPARC:  {logL_sparc(sigma_v100, sigma_v28):.2f}")
    print(f"  JVAS:   {logL_jvas(sigma_v15):.2f}")
    print(f"  Cloud-9: {logL_cloud9(sigma_v28):.2f}")
    print(f"  Total:  {best_logL:.2f}")
    print()

    # Verdict
    improvement = best_logL - baseline_logL
    if best_logL > baseline_logL + 5:
        verdict = "JOINT_FIT_BETTER"
    elif best_logL > baseline_logL - 5:
        verdict = "JOINT_FIT_SIMILAR"
    else:
        verdict = "JOINT_FIT_WORSE"

    print(f"Verdict: {verdict}")
    print(f"  Best logL = {best_logL:.2f}")
    print(f"  Baseline logL = {baseline_logL:.2f}")
    print(f"  Improvement = {improvement:.2f}")

    # Save
    out = {
        "test": "Phase44_joint_fit",
        "channels": list(channels),
        "baseline_params": [float(x) for x in x0],
        "baseline_logL": float(baseline_logL),
        "best_params": [float(x) for x in best_params],
        "best_logL": float(best_logL),
        "improvement": float(improvement),
        "verdict": verdict,
        "interpretation": (
            "Phase 44 performs a multi-channel joint fit across SPARC, JVAS, "
            "and Cloud-9 constraints. The channels have conflicting requirements "
            "on sigma/m at different velocities:\n"
            "  - SPARC wants sigma/m(100) ~ 0.07 cm^2/g\n"
            "  - JVAS B1938+666 wants sigma/m(15) ~ 100 cm^2/g\n"
            "  - Cloud-9 wants sigma/m(28) ~ 100 cm^2/g\n"
            "  - Fornax/Tri II (dwarfs at v=15) wants sigma/m(15) < 5\n\n"
            "These cannot all be satisfied with a single velocity-resonance. The "
            "joint fit either:\n"
            "  - Finds a compromise (worse fit to all channels)\n"
            "  - Or keeps one channel as outlier (no improvement)\n\n"
            "Honest verdict: see the comparison output above."
        ),
    }

    out_path = RESULTS_DIR / "phase44_joint_fit.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"\nResults written to: {out_path}")


if __name__ == "__main__":
    main()