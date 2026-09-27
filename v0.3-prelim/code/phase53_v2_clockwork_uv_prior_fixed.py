"""
Phase 53 v2 — UV-prior joint fit with clockwork mass hierarchy.

REVISED after Phase 53 v1 bug: the optimizer was allowed q in [1.05, 5.0]
and sigma_peaks were free. It found q = 4.16 with peaks at [29, 2112, 151921,
2.6M] km/s — completely outside the T90.70 ladder. The clockwork prior
was supposed to constrain the velocity ladder to ≈ [28, 100, 300, 700],
but free sigma_peaks absorbed the velocity error, leaving log L unchanged.

FIX (v2): tighten q bounds to Phase 51's actual fit (q ≈ 2.22 ±0.5), keep
the k-set fixed at [3,6,9,11], and fix sigma_peaks to T90.70 values
[100, 0.07, 0.1, 0.01]. Now the only free velocity parameters are v_1
(overall scale) and q (constrained to a narrow range around Phase 51's
fit). Sigma_peaks are still free in a SEPARATE run to test the worst case.

THIS v2 RUN:
  - k = [3, 6, 9, 11] FIXED
  - sigma_peaks = [100, 0.07, 0.1, 0.01] FIXED (T90.70 values)
  - width_fracs = [0.05, 0.05, 0.05, 0.10] FIXED (T90.70 values)
  - m_chi, sigma_0, a_slope FREE (3 params)
  - log_v_1, q FREE (2 params), q bounded near Phase 51 fit
  - Total: 5 free parameters

This is the strict test: the clockwork UV prior predicts v_targets from
just 2 parameters (log_v_1, q), and the optimizer must satisfy 3 channel
likelihoods with no other freedom.

EXPECTED OUTCOME
================
If the clockwork UV prior is COMPATIBLE with the multi-channel data,
log L should approach Phase 44's best fit (about -11.58). If it's
INCOMPATIBLE, log L will degrade.
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

# Clockwork k-set from Phase 51 (RMS = 0.0159 with q ≈ 1.49)
# But Phase 51 actually tested k = [3,6,9,11] with q = 2.22 (final result)
# The original Phase 51 code stored levels_k with one of two interpretations:
# - levels_k = [3, 6, 9, 11] with q = 2.221
# - The "ladder" is q^(k/2) so velocities are v_1 * q^(3/2), q^(6/2), q^(9/2), q^(11/2)
# = v_1 * q^1.5, q^3, q^4.5, q^5.5
# With q = 2.221 and v_1 = 8.63 km/s: v = [28.6, 94.6, 313.0, 695.3] km/s
# So the velocity formula is v_target[i] = v_1 * q^(k[i]/2)
# To avoid fractions, double the k values: k = [6, 12, 18, 22] with q^2 = 5.16

# Let me use the original Phase 51 interpretation directly: k = [3,6,9,11], q=2.221
K_LEVELS = np.array([3, 6, 9, 11], dtype=float)
Q_PHASE51 = 2.221105527638191

# Channel likelihoods (same as Phase 44)
def logL_sparc(sigma_m_v100):
    target_v100 = 0.07
    sigma_band = 0.05
    if sigma_m_v100 <= 0:
        return -np.inf
    return norm.logpdf(sigma_m_v100, loc=target_v100, scale=sigma_band)

def logL_jvas(sigma_m_v15):
    target = 100.0
    width = 30.0
    if sigma_m_v15 <= 0:
        return -np.inf
    return norm.logpdf(sigma_m_v15, loc=target, scale=width)

def logL_cloud9(sigma_m_v28):
    target = 100.0
    width = 30.0
    if sigma_m_v28 <= 0:
        return -np.inf
    return norm.logpdf(sigma_m_v28, loc=target, scale=width)

def logL_dwarfs_no_collapse(sigma_m_v15):
    if sigma_m_v15 > 5.0:
        return -10.0
    return 0.0


def sigma_m_at_v(v_kms, m_chi, resonances, sigma_0, a_slope):
    sigma_0_v = velocity_dependent_background(v_kms, sigma_0, a_slope)
    r = sigma_m_multi_resonant(v_kms, m_chi, resonances, sigma_0_v, 0.0)
    return r["sigma_m_total"]


def clockwork_v2_joint_logL(params):
    """Joint logL under FIXED clockwork UV prior (v2).

    params: [m_chi, sigma_0, a_slope, log10_v_1, q]
    Total: 5 free params.
    Sigma_peaks, width_fracs, k_levels are FIXED.
    """
    m_chi = params[0]
    sigma_0 = params[1]
    a_slope = params[2]
    log10_v_1 = params[3]
    q = params[4]

    # Compute velocities from clockwork formula (Phase 51: v_i = v_1 * q^(k_i/2))
    v_1 = 10 ** log10_v_1
    half_k = K_LEVELS / 2.0
    v_targets = v_1 * (q ** half_k)

    # T90.70 fixed sigma_peaks and width_fracs
    sigma_peaks = [100.0, 0.07, 0.1, 0.01]
    width_fracs = [0.05, 0.05, 0.05, 0.10]

    # Build resonances
    resonances = []
    for i, v_t in enumerate(v_targets):
        E_R = kinetic_energy_eV(v_t, m_chi)
        resonances.append({
            "name": f"R{i}",
            "E_R_eV": E_R,
            "Gamma_eV": width_fracs[i] * E_R,
            "sigma_peak_cm2_per_g": sigma_peaks[i],
            "v_target_kms": float(v_t),
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
    logL += logL_sparc(sigma_v100)
    logL += logL_jvas(sigma_v15)
    logL += logL_cloud9(sigma_v28)
    logL += logL_dwarfs_no_collapse(sigma_v15)
    return logL


def main():
    print("Phase 53 v2 — UV-prior joint fit (FIXED clockwork construction)")
    print("=" * 70)
    print("REVISED after Phase 53 v1 bug — see code docstring for details")
    print()

    # Phase 44 reference
    phase44_baseline_logL = -19.67268668762108
    phase44_best_logL = -11.577625403084578

    # Phase 53 v2 starting point: T90.70 v_1 = 8.46, q = 2.221
    log10_v_1_init = np.log10(8.63)
    q_init = 2.221
    sigma_peaks_init = [100.0, 0.07, 0.1, 0.01]
    width_fracs_init = [0.05, 0.05, 0.05, 0.10]
    m_chi_init = 6.58
    sigma_0_init = 0.195
    a_slope_init = 0.7

    x0_v2 = [m_chi_init, sigma_0_init, a_slope_init, log10_v_1_init, q_init]
    clock_v2_baseline = clockwork_v2_joint_logL(x0_v2)
    print(f"Clockwork v2 starting-point logL: {clock_v2_baseline:.2f}")
    print(f"  v_1 = {10**log10_v_1_init:.2f} km/s, q = {q_init:.3f}")
    v_targets_v2_init = [10**log10_v_1_init * q_init**(K_LEVELS[i]/2.0) for i in range(4)]
    print(f"  v_targets = {[round(v, 2) for v in v_targets_v2_init]}")
    print(f"  vs T90.70 [28, 100, 300, 700]")
    print()

    # Bounds for differential evolution
    bounds_v2 = [
        (1.0, 50.0),        # m_chi
        (0.01, 1.0),        # sigma_0
        (0.0, 2.0),         # a_slope
        (-1.5, 1.5),        # log10_v_1 (~0.03 to ~30 km/s)
        (1.5, 3.0),         # q (constrained near Phase 51 fit q=2.22)
    ]

    print("Running differential evolution on clockwork v2 (5 params, fixed construction)...")
    result = differential_evolution(
        lambda x: -clockwork_v2_joint_logL(x),
        bounds_v2,
        seed=42,
        maxiter=200,
        popsize=20,
        tol=1e-6,
        workers=1,
    )

    best_params = result.x
    best_logL = -result.fun
    print(f"Best clockwork v2 log L = {best_logL:.2f}")
    print(f"  m_chi = {best_params[0]:.2f} GeV")
    print(f"  sigma_0 = {best_params[1]:.3f}")
    print(f"  a_slope = {best_params[2]:.3f}")
    print(f"  log_v_1 = {best_params[3]:.3f}  (v_1 = {10**best_params[3]:.2f} km/s)")
    print(f"  q = {best_params[4]:.4f}")
    v_targets_best = [10**best_params[3] * best_params[4]**(K_LEVELS[i]/2.0) for i in range(4)]
    print(f"  v_targets = {[round(v, 2) for v in v_targets_best]}")
    print()

    # Headline
    improvement_vs_baseline = best_logL - phase44_baseline_logL
    improvement_vs_phase44_best = best_logL - phase44_best_logL
    print(f"=== HEADLINE COMPARISON ===")
    print(f"Phase 44 T90.70 baseline logL:           {phase44_baseline_logL:.2f}")
    print(f"Phase 44 best fit (15 params, free):     {phase44_best_logL:.2f}")
    print(f"Phase 53 v2 best fit (5 params, clockwork UV): {best_logL:.2f}")
    print()
    print(f"  Improvement vs Phase 44 baseline: {improvement_vs_baseline:.2f} log-units")
    print(f"  Improvement vs Phase 44 best:     {improvement_vs_phase44_best:.2f} log-units")
    print()

    # BIC-corrected comparison (5 params vs 15 params)
    # BIC penalty: 0.5 * k * ln(n) per parameter (n=3 channels here)
    # For 5 vs 15 params with n=3: BIC penalty diff = 0.5*10*ln(3) ≈ 5.5
    # Phase 44 BIC = -11.58 + 0.5*15*ln(3) = -11.58 + 8.22 = -3.36
    # Phase 53 BIC = best + 0.5*5*ln(3) = best + 2.74
    # BIC diff (Phase 53 - Phase 44) = (best - phase44_best) + (2.74 - 8.22) = (best - phase44_best) - 5.48
    bic_phase44 = phase44_best_logL + 0.5 * 15 * np.log(3)
    bic_phase53 = best_logL + 0.5 * 5 * np.log(3)
    print(f"  BIC-corrected (Occam penalty):")
    print(f"    Phase 44 BIC: {bic_phase44:.2f}")
    print(f"    Phase 53 v2 BIC: {bic_phase53:.2f}")
    print(f"    Δ BIC (Phase 53 - Phase 44): {bic_phase53 - bic_phase44:.2f}")
    print(f"    (Negative Δ means clockwork UV prior is PREFERRED under BIC)")
    print()

    # Verdict
    if improvement_vs_baseline > 1:
        verdict = "CLOCKWORK_UV_PRESERVES_JOINT_FIT_GAIN"
    elif improvement_vs_baseline > 0:
        verdict = "CLOCKWORK_UV_MARGINAL"
    else:
        verdict = "CLOCKWORK_UV_KILLS_JOINT_FIT_GAIN"

    # Save JSON
    out = {
        "test": "Phase53_v2_clockwork_uv_prior_joint_fit_FIXED",
        "phase44_reference": {
            "t90_70_baseline_logL": phase44_baseline_logL,
            "t90_70_best_fit_logL": phase44_best_logL,
            "improvement_log_units": float(phase44_best_logL - phase44_baseline_logL),
            "n_free_params": 15,
        },
        "clockwork_construction_v2": {
            "k_levels": [int(k) for k in K_LEVELS],
            "sigma_peaks": [100.0, 0.07, 0.1, 0.01],  # FIXED T90.70
            "width_fracs": [0.05, 0.05, 0.05, 0.10],   # FIXED T90.70
            "rationale": "Phase 51 clockwork fit (RMS=0.0159). Sigma_peaks and "
                         "width_fracs fixed at T90.70 values to prevent the optimizer "
                         "from absorbing velocity error into peak heights (Phase 53 "
                         "v1 bug). q bounded to [1.5, 3.0] near Phase 51's fit q=2.221.",
            "n_free_params": 5,
            "params_free": ["m_chi", "sigma_0", "a_slope", "log_v_1", "q"],
        },
        "phase53_v2_results": {
            "best_fit_logL": float(best_logL),
            "improvement_vs_phase44_baseline": float(improvement_vs_baseline),
            "improvement_vs_phase44_best_fit": float(improvement_vs_phase44_best),
            "best_params": {
                "m_chi_GeV": float(best_params[0]),
                "sigma_0": float(best_params[1]),
                "a_slope": float(best_params[2]),
                "log_v_1": float(best_params[3]),
                "q": float(best_params[4]),
            },
            "v_targets_kms": [float(v) for v in v_targets_best],
            "verdict": verdict,
        },
        "bic_comparison": {
            "phase44_bic": float(bic_phase44),
            "phase53_bic": float(bic_phase53),
            "delta_bic": float(bic_phase53 - bic_phase44),
            "interpretation": (
                "Negative Δ BIC means clockwork UV prior is preferred under "
                "BIC-style Occam penalty. Positive means the free fit's extra "
                "parameters earn their keep."
            ),
        },
        "v1_bug_note": (
            "Phase 53 v1 (this commit's first version) allowed q in [1.05, 5.0] "
            "with free sigma_peaks. The optimizer found q=4.16 with peaks at "
            "[29, 2112, 151921, 2.6M] km/s — completely outside the T90.70 "
            "ladder. Free sigma_peaks absorbed the velocity error and log L "
            "matched Phase 44 trivially (8.10 log-units). This was NOT a "
            "valid test of the clockwork UV prior because sigma_peaks "
            "freedom masked the velocity-ladder constraint."
        ),
        "interpretation": (
            "Phase 53 v2 is the proper test: with sigma_peaks fixed at T90.70 "
            "values, the clockwork UV prior's 5 free parameters must satisfy "
            "the 3 channel likelihoods. If log L degrades significantly vs "
            "Phase 44's free fit, the UV prior costs too much likelihood. If "
            "log L is preserved within BIC tolerance, the UV prior is "
            "compatible with the multi-channel phenomenology."
        ),
    }

    out_path = RESULTS_DIR / "phase53_v2_clockwork_uv_prior_fixed.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"Results written to: {out_path}")
    print()
    print(f"=== FINAL VERDICT ===")
    print(f"  {verdict}")
    print(f"  Phase 53 v2 best log L = {best_logL:.2f}")
    print(f"  Phase 44 baseline = {phase44_baseline_logL:.2f}")
    print(f"  Phase 44 best fit = {phase44_best_logL:.2f}")
    print(f"  Δ vs Phase 44 best = {improvement_vs_phase44_best:.2f} log-units")
    print(f"  BIC Δ = {bic_phase53 - bic_phase44:.2f}")


if __name__ == "__main__":
    main()