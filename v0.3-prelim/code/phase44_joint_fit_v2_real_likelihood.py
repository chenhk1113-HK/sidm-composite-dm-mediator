"""
Phase 44 v2 — Real-likelihood joint fit (V19.2-E A.1).

Wires the published-σ_unc observational channels into the headline
pass/fail table using the paper's CANONICAL Gaussian-BW σ/m(v) form.

Key fix vs R88 v1 (phase44_joint_fit.py): the R88 v1 used a 4-resonance
v²-space Lorentzian Breit-Wigner with width_fracs[0]=0.184 (mapped to a
huge v²-space width w=159), which made the resonance effectively flat
across all velocities (σ_HH ≈ σ_peak everywhere). The paper's canonical
form is a SINGLE Gaussian resonance with σ_peak=174, w=4.4 km/s
(per constants.py + §2.6), which gives σ/m(15)=2.85 cm²/g (consistent
with the paper's headline) and σ/m(28)=166 cm²/g (Cloud-9 anchor).

This script uses the canonical Gaussian form for σ_HH(v), and the
8-channel T205 OBS_PUBLISHED likelihood for per-channel pass/fail
determination with published σ_unc.

Reference: ClawsGO comment #5 (2026-10-09) B.4.
"""
from __future__ import annotations
import json
import math
import sys
import warnings
from pathlib import Path

import numpy as np

warnings.filterwarnings("ignore")

sys.path.insert(0, r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\code")
sys.path.insert(0, r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\scripts")

# Use the canonical Gaussian form (per constants.py + §2.6 of paper)
from constants import (
    M_CHI_GEV, M_PHI_GEV, V_TARGET_KMS, SIGMA_KMS,
    A_RES, SIGMA_PEAK_CM2_PER_G, M_NUCLEON_GEV,
    SIGMA_0_CM2_PER_G, A_SLOPE, V_REF_KMS, LZ_BOUND_CM2,
)

# Canonical f_H (paper §2.6, "σ_eff formula (R88)": σ_eff = f_H² × σ/m with f_H=0.297)
# Not in constants.py yet — added here as the canonical value.
F_H_CANONICAL = 0.297
F_H = F_H_CANONICAL

# T205 published σ_unc per channel
from T205_full_likelihood_published import OBS_PUBLISHED

# Lazy-initialized results directory (R88(82) P0 fix)
RESULTS_DIR = None


def _get_results_dir():
    global RESULTS_DIR
    if RESULTS_DIR is None:
        from config import RESULTS_DIR_V03
        _dir = Path(RESULTS_DIR_V03)
        _dir.mkdir(parents=True, exist_ok=True)
        RESULTS_DIR = _dir
    return RESULTS_DIR


# ============================================================================
# Canonical Gaussian σ/m(v) form (per paper §2.6 + constants.py)
# ============================================================================

def sigma_m_canonical_gaussian(v_kms):
    """Canonical Gaussian σ/m(v) (paper §2.6, constants.py).

    σ/m(v) = σ_0 · (v_ref / v)^a_slope + σ_peak · exp(-(v - v_target)² / (2 · σ₁²))

    Canonical values: σ_0=0.052, a_slope=1.93, v_ref=100, σ_peak=174,
    v_target=29.4, σ₁=4.4 (all from constants.py Phase 44 free fit).
    """
    v = np.atleast_1d(np.asarray(v_kms, dtype=float))
    bg = SIGMA_0_CM2_PER_G * (V_REF_KMS / v) ** A_SLOPE
    res = SIGMA_PEAK_CM2_PER_G * np.exp(-((v - V_TARGET_KMS) ** 2) / (2 * SIGMA_KMS ** 2))
    sigma = bg + res
    return sigma if len(sigma) > 1 else float(sigma[0])


# ============================================================================
# Pass/fail per channel
# ============================================================================

def channel_verdict(sigma_eff, sigma_obs, sigma_unc, kind):
    """Per-channel pass/fail using T205 conventions (gaussian/ceiling/floor)."""
    if kind == "gaussian":
        diff = abs(sigma_eff - sigma_obs)
        if diff < sigma_unc:
            return "PASS", (diff / sigma_unc) ** 2, sigma_unc
        elif diff < 2 * sigma_unc:
            return "MARGINAL", (diff / sigma_unc) ** 2, 2 * sigma_unc
        else:
            return "FAIL", (diff / sigma_unc) ** 2, 2 * sigma_unc
    if kind == "ceiling":
        if sigma_eff <= sigma_obs:
            return "PASS", 0.0, sigma_obs
        excess = (sigma_eff - sigma_obs) / sigma_unc
        if excess < 1.0:
            return "MARGINAL", excess ** 2, sigma_obs
        return "FAIL", excess ** 2, sigma_obs
    if kind == "floor":
        if sigma_eff >= sigma_obs:
            return "PASS", 0.0, sigma_obs
        deficit = (sigma_obs - sigma_eff) / sigma_unc
        if deficit < 1.0:
            return "MARGINAL", deficit ** 2, sigma_obs
        return "FAIL", deficit ** 2, sigma_obs
    raise ValueError(f"Unknown kind: {kind}")


# ============================================================================
# Per-channel evaluation
# ============================================================================

def main():
    print("=" * 60)
    print("Phase 44 v2 — Real-likelihood joint fit (canonical Gaussian)")
    print("=" * 60)
    print()
    print(f"Canonical Gaussian σ/m(v): σ_0={SIGMA_0_CM2_PER_G}, a_slope={A_SLOPE}, "
          f"v_ref={V_REF_KMS}, σ_peak={SIGMA_PEAK_CM2_PER_G}, v_target={V_TARGET_KMS}, "
          f"σ₁={SIGMA_KMS} km/s, f_H={F_H}")
    print()

    # Compute σ_eff at each channel (canonical Gaussian × f_H²)
    print("Per-channel σ_eff evaluation:")
    print(f"  {'Channel':<18s} {'v':>6s} {'σ_HH':>10s} {'σ_eff':>10s} {'σ_obs':>10s} "
          f"{'σ_unc':>10s} {'χ²':>10s} {'verdict':<10s}")
    print("  " + "-" * 86)

    results = []
    pass_count = marginal_count = fail_count = 0
    total_logL_real = 0.0

    for v, sigma_obs, sigma_unc, kind, label, citation in OBS_PUBLISHED:
        sigma_HH = float(sigma_m_canonical_gaussian(v))
        sigma_eff = F_H ** 2 * sigma_HH

        verdict, chi2, threshold = channel_verdict(sigma_eff, sigma_obs, sigma_unc, kind)
        logL_contribution = -0.5 * chi2

        print(f"  {label:<18s} {v:>6.0f} {sigma_HH:>10.4g} {sigma_eff:>10.4g} "
              f"{sigma_obs:>10.4g} {sigma_unc:>10.4g} {chi2:>10.3f} {verdict:<10s}")

        if verdict == "PASS":
            pass_count += 1
        elif verdict == "MARGINAL":
            marginal_count += 1
        else:
            fail_count += 1
        total_logL_real += logL_contribution

        results.append({
            "v_kms": float(v),
            "label": label,
            "kind": kind,
            "sigma_obs": float(sigma_obs),
            "sigma_unc": float(sigma_unc),
            "sigma_HH_at_v_canonical": float(sigma_HH),
            "f_H_canonical": float(F_H),
            "sigma_eff_canonical": float(sigma_eff),
            "chi2": float(chi2),
            "logL_contribution": float(logL_contribution),
            "verdict": verdict,
            "citation": citation,
        })

    print("  " + "-" * 86)
    print(f"  PASS: {pass_count}, MARGINAL: {marginal_count}, FAIL: {fail_count}")
    print(f"  Total log L (canonical Gaussian @ published σ_unc) = {total_logL_real:.3f}")
    print()

    # Compare to T205 (8-channel published) and Phase 44 v1 (3-channel hand-set)
    t205_logL_A = -14.285
    print(f"  T205 (8-channel published, model A dynesty) = {t205_logL_A:.3f}")
    print(f"  Phase 44 v2 (canonical Gaussian, this script) = {total_logL_real:.3f}")
    print(f"  Δ log L vs T205: {total_logL_real - t205_logL_A:+.3f}")
    print()

    # Verdict
    if total_logL_real > t205_logL_A + 0.5:
        verdict = "REAL_LIKELIHOOD_BETTER"
    elif total_logL_real < t205_logL_A - 0.5:
        verdict = "REAL_LIKELIHOOD_WORSE"
    else:
        verdict = "REAL_LIKELIHOOD_ROBUST"
    print(f"Verdict: {verdict}")
    print()

    # Save
    out = {
        "test": "Phase44_v2_real_likelihood_canonical_gaussian",
        "date": "2026-10-09",
        "method": (
            "Per-channel pass/fail using paper's canonical Gaussian σ/m(v) "
            "(constants.py Phase 44 free fit: σ_0=0.052, a_slope=1.93, v_ref=100, "
            "σ_peak=174, v_target=29.4, σ₁=4.4, f_H=0.297) evaluated at the 8 "
            "T205 channels with published σ_unc."
        ),
        "T205_published_8channel_modelA": {
            "logZ": t205_logL_A,
            "n_params": 15,
            "note": "T205 uses a v²-space Lorentzian Breit-Wigner ansatz; this script uses the paper's canonical Gaussian form. The two are different parameterizations."
        },
        "Phase_44_v2_canonical_gaussian": {
            "total_logL": total_logL_real,
            "delta_logL_vs_T205": total_logL_real - t205_logL_A,
            "verdict": verdict,
        },
        "pass_fail_summary": {
            "total_channels": len(results),
            "PASS": pass_count,
            "MARGINAL": marginal_count,
            "FAIL": fail_count,
            "canonical_count_string": f"{pass_count} of {len(results)} channels pass",
        },
        "per_channel": results,
        "interpretation": (
            f"The canonical Gaussian σ/m(v) (per constants.py + §2.6) gives "
            f"{pass_count} PASS / {marginal_count} MARGINAL / {fail_count} FAIL out of "
            f"{len(results)} channels when evaluated against the T205 published "
            f"σ_unc likelihood. This replaces the 3-channel hand-set Phase 44 v1 "
            f"likelihood (which gave a +8.10 log-unit improvement) with a "
            f"8-channel published-σ_unc likelihood. The pass/fail table is now "
            f"MEASURED from real published error budgets, not chosen by hand."
        ),
        "HONEST_LIMITATIONS": [
            "T205's OBS_PUBLISHED splits the Horigome+ 2025 combined sample across 5 v bins, "
            "which T205 itself flags as a limitation (treating them as independent channels "
            "over-counts the effective constraint).",
            "The σ_eff = f_H²·σ/m formula uses a single f_H=0.297 across all velocities "
            "(per constants.py), but the project does NOT have a first-principles f_H "
            "derivation at Phase 44 parameters (R88(88) caveat). The f_H=0.297 value is the "
            "Phase G7 phenomenological fit, not a Yang+ 2025 SIDM2c prediction.",
            "The T205 v²-space Lorentzian ansatz and the paper's canonical Gaussian form "
            "are different parameterizations; this script uses the Gaussian form to match "
            "the paper's headline numbers (σ/m(15)=2.85, σ/m(28)=166 per §2.6).",
        ],
    }

    out_path = _get_results_dir() / "phase44_joint_fit_v2_real_likelihood.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"Results written to: {out_path}")
    print()
    print(f"CANONICAL HEADLINE (R88 v19.2-E A.1):")
    print(f"  {pass_count} of {len(results)} channels PASS at canonical Phase 44 free fit")
    print(f"  (was: 4 of 7 with hand-set 3-channel Gaussian in Phase 44 v1)")
    print(f"  PASS: {pass_count}  MARGINAL: {marginal_count}  FAIL: {fail_count}")


if __name__ == "__main__":
    main()
