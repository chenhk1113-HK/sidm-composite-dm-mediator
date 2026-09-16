"""
Phase 54 — Joint-channel comparison: multi-resonance vs constant sigma/m.

QUESTION (per Paper1.docx reviewer Issue #5, 2026-09-16):
How does the multi-resonance model compare with a simpler constant sigma/m
(Burkert-like, the model that wins on rotation curves alone) on the
*joint* SPARC + Cloud-9 likelihood?

The reviewer wrote: "If the multi-resonance model still wins on the joint,
that is a clean positive; if not, the claim should be softened."

CONSTRUCTION
============
Both models are evaluated against the same joint likelihood:
  log L = log L_sparc(sigma_m_v100) + log L_cloud9(sigma_m_v28) + log L_jvas(sigma_m_v15)
where
  log L_sparc(x) = log N(x | 0.07, 0.05)        [target 0.07 cm^2/g]
  log L_cloud9(x) = log N(x | 100, 30)          [target 100 cm^2/g]
  log L_jvas(x) = log N(x | 100, 30)            [target 100 cm^2/g, but we'll see if either satisfies]

MODEL A: Constant sigma/m
  sigma/m(v) = sigma_const (independent of v)
  Best fit: optimizer picks sigma_const to maximize log L

MODEL B: Multi-resonance (Phase 44 best fit)
  sigma/m(v) = sigma_0_bg + sum_i sigma_peak_i * BW(v, v_target_i)
  Best fit: Phase 44 posterior parameters

For Model A, the optimizer finds the single sigma_const that best matches
the three targets. With three targets (0.07, 100, 100), it cannot match
all three; the best it can do is some compromise.

For Model B, the multi-resonance structure can match targets at different
velocities simultaneously.
"""
from __future__ import annotations
import json
import sys
import warnings
from pathlib import Path
import numpy as np
from scipy.optimize import minimize_scalar
from scipy.stats import norm

warnings.filterwarnings("ignore")

RESULTS_DIR = Path(r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def logL_sparc(sm):
    if sm <= 0:
        return -np.inf
    return norm.logpdf(sm, loc=0.07, scale=0.05)


def logL_cloud9(sm):
    if sm <= 0:
        return -np.inf
    return norm.logpdf(sm, loc=100.0, scale=30.0)


def logL_jvas(sm):
    if sm <= 0:
        return -np.inf
    return norm.logpdf(sm, loc=100.0, scale=30.0)


def logL_joint_3ch(sm_v100, sm_v28, sm_v15):
    return logL_sparc(sm_v100) + logL_cloud9(sm_v28) + logL_jvas(sm_v15)


def logL_joint_2ch(sm_v100, sm_v28):
    """Without JVAS (consistent with our model limitation)."""
    return logL_sparc(sm_v100) + logL_cloud9(sm_v28)


def main():
    print("Phase 54 — Joint-channel comparison: constant sigma/m vs multi-resonance")
    print("=" * 70)
    print("Per Paper1.docx reviewer Issue #5 (2026-09-16)")
    print()

    # Model A: constant sigma/m
    # 2-channel: SPARC + Cloud-9 only (joint likelihood)
    print("=== Model A: constant sigma/m (Burkert-like) ===")

    def neg_logL_2ch(log_sm):
        sm = 10 ** log_sm
        return -logL_joint_2ch(sm, sm)

    res_A_2ch = minimize_scalar(neg_logL_2ch, bounds=(-2, 4), method='bounded')
    sm_A_2ch = 10 ** res_A_2ch.x
    logL_A_2ch = -res_A_2ch.fun
    print(f"  2-channel joint (SPARC + Cloud-9):")
    print(f"    Best sigma_const = {sm_A_2ch:.4f} cm^2/g")
    print(f"    log L = {logL_A_2ch:.4f}")
    print(f"    sigma/m(100) = sigma/m(28) = {sm_A_2ch:.4f}")
    print()

    # 3-channel: SPARC + Cloud-9 + JVAS
    def neg_logL_3ch(log_sm):
        sm = 10 ** log_sm
        return -logL_joint_3ch(sm, sm, sm)

    res_A_3ch = minimize_scalar(neg_logL_3ch, bounds=(-2, 4), method='bounded')
    sm_A_3ch = 10 ** res_A_3ch.x
    logL_A_3ch = -res_A_3ch.fun
    print(f"  3-channel joint (SPARC + Cloud-9 + JVAS):")
    print(f"    Best sigma_const = {sm_A_3ch:.4f} cm^2/g")
    print(f"    log L = {logL_A_3ch:.4f}")
    print()

    # Model B: multi-resonance (use Phase 44 best fit)
    print("=== Model B: multi-resonance (Phase 44 best fit) ===")
    r44 = json.loads(open(RES_DIR := Path(r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\phase44_joint_fit.json")).read())
    bp = r44["best_params"]
    print(f"  Best log L (3-channel) = {r44['best_logL']:.4f}")
    print(f"  Reference: sigma/m(100) = {bp[1]:.3f} (target 0.07)")
    print(f"             sigma/m(28)  = {bp[1]:.3f} (target 100)")
    print(f"             sigma/m(15)  = {bp[1]:.3f} (target 100)")
    print(f"             (values at phase44 fit; recompute below)")
    print()

    # Compute the multi-resonance sigma/m at the three target velocities
    sys.path.insert(0, r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\code")
    from t90_v70_multi_resonant_darkqcd import sigma_m_multi_resonant, velocity_dependent_background
    from t90_v50_resonant_sidm import kinetic_energy_eV

    # Phase 44 best_params: [m_chi, sigma_0, a_slope, v0, v1, v2, v3, peaks, widths]
    m_chi = bp[0]
    sigma_0_bg = bp[1]
    a_slope = bp[2]
    v_targets = bp[3:7]
    sigma_peaks = bp[7:11]
    width_fracs = bp[11:15]

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

    def sm_at(v_kms):
        sigma_0_v = velocity_dependent_background(v_kms, sigma_0_bg, a_slope)
        r = sigma_m_multi_resonant(v_kms, m_chi, resonances, sigma_0_v, 0.0)
        return r["sigma_m_total"]

    sm_15 = sm_at(15.0)
    sm_28 = sm_at(28.0)
    sm_100 = sm_at(100.0)

    print(f"  Computed values (Phase 44 best fit):")
    print(f"    sigma/m(15)  = {sm_15:.4f}  (JVAS target 100, off by {100 - sm_15:.2f})")
    print(f"    sigma/m(28)  = {sm_28:.4f}  (Cloud-9 target 100)")
    print(f"    sigma/m(100) = {sm_100:.4f} (SPARC target 0.07)")

    logL_B_3ch = logL_joint_3ch(sm_100, sm_28, sm_15)
    print(f"    log L (3-channel) = {logL_B_3ch:.4f}")
    logL_B_2ch = logL_joint_2ch(sm_100, sm_28)
    print(f"    log L (2-channel SPARC+Cloud-9) = {logL_B_2ch:.4f}")
    print()

    # Headline comparison
    print("=== HEADLINE COMPARISON ===")
    print(f"")
    print(f"  {'Model':<35} {'log L (3ch)':>12} {'log L (2ch)':>13} {'# free params':>13}")
    print(f"  {'-'*35} {'-'*12} {'-'*13} {'-'*13}")
    print(f"  {'Constant sigma/m':<35} {logL_A_3ch:>12.2f} {logL_A_2ch:>13.2f} {1:>13}")
    print(f"  {'Multi-resonance (15 params)':<35} {logL_B_3ch:>12.2f} {logL_B_2ch:>13.2f} {15:>13}")
    print()
    print(f"  Δ log L (multi-resonance vs constant) on 3-channel:  {logL_B_3ch - logL_A_3ch:+.2f}")
    print(f"  Δ log L (multi-resonance vs constant) on 2-channel:  {logL_B_2ch - logL_A_2ch:+.2f}")
    print()

    # BIC comparison
    # BIC: -2 log L + k * ln(n); for n=3 channels, ln(3) = 1.099
    n_ch = 3
    bic_A_3ch = -2 * logL_A_3ch + 1 * np.log(n_ch)
    bic_B_3ch = -2 * logL_B_3ch + 15 * np.log(n_ch)
    n_ch_2 = 2
    bic_A_2ch = -2 * logL_A_2ch + 1 * np.log(n_ch_2)
    bic_B_2ch = -2 * logL_B_2ch + 15 * np.log(n_ch_2)
    print(f"  BIC (3-channel):")
    print(f"    Constant sigma/m:     BIC = {bic_A_3ch:.2f}")
    print(f"    Multi-resonance (15):  BIC = {bic_B_3ch:.2f}")
    print(f"    Δ BIC (B - A) = {bic_B_3ch - bic_A_3ch:.2f}")
    print(f"    (Negative Δ BIC favors multi-resonance)")
    print()

    # Save JSON
    out = {
        "test": "Phase54_joint_channel_comparison",
        "model_A_constant_sigmam": {
            "best_sigma_const_cm2_per_g": float(sm_A_2ch) if 2 > 3 else float(sm_A_2ch),
            "logL_3channel": float(logL_A_3ch),
            "logL_2channel": float(logL_A_2ch),
            "n_params": 1,
        },
        "model_B_multiresonance": {
            "logL_3channel": float(logL_B_3ch),
            "logL_2channel": float(logL_B_2ch),
            "sigma_m_v15": float(sm_15),
            "sigma_m_v28": float(sm_28),
            "sigma_m_v100": float(sm_100),
            "n_params": 15,
        },
        "headline": {
            "logL_delta_3channel": float(logL_B_3ch - logL_A_3ch),
            "logL_delta_2channel": float(logL_B_2ch - logL_A_2ch),
            "bic_delta_3channel": float(bic_B_3ch - bic_A_3ch),
            "bic_delta_2channel": float(bic_B_2ch - bic_A_2ch),
        },
        "interpretation": (
            "Per Paper1.docx reviewer Issue #5: does the multi-resonance model win "
            "on the joint SPARC + Cloud-9 likelihood against a constant sigma/m baseline? "
            "If yes, the multi-resonance is a clean positive on joint channels; if no, "
            "the claim should be softened."
        ),
    }

    out_path = RESULTS_DIR / "phase54_joint_comparison.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Results: {out_path}")


if __name__ == "__main__":
    main()