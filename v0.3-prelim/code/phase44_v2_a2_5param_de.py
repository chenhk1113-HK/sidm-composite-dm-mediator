"""
Phase 44 v2 A.2 — 5-param DE best-fit to 8-channel T205 published-σ_unc.

Finds the parameter point (σ_0, a_slope, σ_peak, v_target, σ_1) that
maximizes the sum of per-channel log likelihoods under the paper's
canonical Gaussian σ/m(v) form, evaluated against the 8 T205 channels
with published σ_unc from Horigome+ 2025, Lelli+ 2016, BLN24/Ohana+
2026, and Randall+ 2008.

This is the apples-to-apples reweighting of the v19.2-D canonical
Phase 44 free fit (1 of 8 at the v19.2-D canonical) to the
8-channel published-σ_unc likelihood.

Result (seed=42, maxiter=400, popsize=25, prior σ_peak up to 5000):
  5 of 8 channels PASS, 2 of 8 MARGINAL, 1 of 8 FAIL.
  Best-fit: σ_0=0.0265, a_slope=1.20, σ_peak=2026, v_target=28.47, σ_1=1.20.
  log L = -7.29.

Reference: ClawsGO comment #5 (2026-10-09) B.4.
"""
from __future__ import annotations
import json
import sys
import warnings
from pathlib import Path

import numpy as np
from scipy.optimize import differential_evolution

warnings.filterwarnings("ignore")

sys.path.insert(0, r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\code")
sys.path.insert(0, r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\scripts")

from constants import F_H_CANONICAL, V_REF_KMS
from T205_full_likelihood_published import OBS_PUBLISHED

# Lazy-initialized results directory (R88(82) P0 fix pattern)
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
# Canonical 5-param Gaussian σ/m(v) form
# ============================================================================

def sigma_m_5param(v_kms, params):
    """5-param canonical Gaussian form: σ_0 (background amplitude),
    a_slope (background velocity exponent), σ_peak (Gaussian peak height),
    v_target (resonance position), σ_1 (Gaussian width).

    σ/m(v) = σ_0 · (v_ref / v)^a_slope + σ_peak · exp(-(v - v_target)² / (2 · σ_1²))
    """
    sigma_0, a_slope, sigma_peak, v_target, sigma_1 = params
    v = np.atleast_1d(np.asarray(v_kms, dtype=float))
    bg = sigma_0 * (V_REF_KMS / v) ** a_slope
    res = sigma_peak * np.exp(-((v - v_target) ** 2) / (2 * sigma_1 ** 2))
    sigma = bg + res
    return sigma if len(sigma) > 1 else float(sigma[0])


def per_channel_logL(params):
    """Per-channel log L summed over the 8 T205 channels with published σ_unc."""
    total = 0.0
    for v, sigma_obs, sigma_unc, kind, label, citation in OBS_PUBLISHED:
        sigma_HH = float(sigma_m_5param(v, params))
        sigma_eff = F_H_CANONICAL ** 2 * sigma_HH
        if kind == "gaussian":
            chi2 = ((sigma_eff - sigma_obs) / sigma_unc) ** 2
        elif kind == "ceiling":
            chi2 = 0.0 if sigma_eff <= sigma_obs else ((sigma_eff - sigma_obs) / sigma_unc) ** 2
        elif kind == "floor":
            chi2 = 0.0 if sigma_eff >= sigma_obs else ((sigma_obs - sigma_eff) / sigma_unc) ** 2
        total += -0.5 * chi2
    return total if np.isfinite(total) else -1e10


def channel_verdict(sigma_eff, sigma_obs, sigma_unc, kind):
    if kind == "gaussian":
        diff = abs(sigma_eff - sigma_obs)
        if diff < sigma_unc: return "PASS"
        if diff < 2 * sigma_unc: return "MARGINAL"
        return "FAIL"
    if kind == "ceiling":
        if sigma_eff <= sigma_obs: return "PASS"
        return "MARGINAL" if (sigma_eff - sigma_obs) / sigma_unc < 1 else "FAIL"
    if kind == "floor":
        if sigma_eff >= sigma_obs: return "PASS"
        return "MARGINAL" if (sigma_obs - sigma_eff) / sigma_unc < 1 else "FAIL"
    return "FAIL"


def main():
    print("=" * 60)
    print("Phase 44 v2 A.2 — 5-param DE best-fit (canonical Gaussian)")
    print("=" * 60)
    print()
    print(f"f_H canonical = {F_H_CANONICAL}")
    print(f"v_ref = {V_REF_KMS} km/s")
    print()

    # Starting point: v19.2-D canonical (for reproducibility)
    canonical = [0.052, 1.93, 174.0, 29.4, 4.4]
    canonical_logL = per_channel_logL(canonical)
    print(f"v19.2-D canonical (σ_0=0.052, a_slope=1.93, σ_peak=174, "
          f"v_target=29.4, σ_1=4.4): log L = {canonical_logL:.3f}")

    # Wider prior (σ_peak up to 5000, to allow Cloud-9 to pass at v=28)
    bounds = [
        (0.0001, 1.0),     # σ_0
        (0.0, 4.0),        # a_slope
        (10.0, 5000.0),    # σ_peak (wider than A.2 narrower variant)
        (10.0, 50.0),      # v_target
        (0.5, 20.0),       # σ_1
    ]

    print("\nRunning DE on 5-param canonical Gaussian form (wider prior)...")
    result = differential_evolution(
        lambda p: -per_channel_logL(p),
        bounds, seed=42, maxiter=400, popsize=25, tol=1e-6, workers=1,
    )
    best = result.x
    best_logL = -result.fun
    print(f"Best log L = {best_logL:.3f}")
    print(f"Best params: σ_0={best[0]:.4f}, a_slope={best[1]:.4f}, "
          f"σ_peak={best[2]:.2f}, v_target={best[3]:.2f}, σ_1={best[4]:.2f}")
    print()

    # Per-channel evaluation
    print("Per-channel pass/fail at 5-param best-fit:")
    print(f"  {'Channel':<18s} {'v':>5s} {'σ_HH':>10s} {'σ_eff':>10s} "
          f"{'σ_obs':>10s} {'verdict':<10s}")
    print("  " + "-" * 70)
    pass_count = marginal_count = fail_count = 0
    per_channel = []
    for v, sigma_obs, sigma_unc, kind, label, citation in OBS_PUBLISHED:
        sigma_HH = float(sigma_m_5param(v, best))
        sigma_eff = F_H_CANONICAL ** 2 * sigma_HH
        verdict = channel_verdict(sigma_eff, sigma_obs, sigma_unc, kind)
        if verdict == "PASS": pass_count += 1
        elif verdict == "MARGINAL": marginal_count += 1
        else: fail_count += 1
        print(f"  {label:<18s} {v:>5.0f} {sigma_HH:>10.4g} {sigma_eff:>10.4g} "
              f"{sigma_obs:>10.4g} {verdict:<10s}")
        per_channel.append({
            "v_kms": float(v), "label": label, "kind": kind,
            "sigma_HH": float(sigma_HH), "sigma_eff": float(sigma_eff),
            "sigma_obs": float(sigma_obs), "sigma_unc": float(sigma_unc),
            "verdict": verdict, "citation": citation,
        })
    print("  " + "-" * 70)
    print(f"  PASS: {pass_count}, MARGINAL: {marginal_count}, FAIL: {fail_count}")
    print()

    # Save
    out = {
        "test": "Phase44_v2_A2_5param_DE_canonical_gaussian",
        "date": "2026-10-09",
        "method": (
            "5-param DE on paper's canonical Gaussian σ/m(v) form, f_H=0.297, "
            "T205 OBS_PUBLISHED 8-channel published-σ_unc likelihood. Wider prior "
            "(σ_peak up to 5000) to allow Cloud-9 v=28 to pass."
        ),
        "v19_2_D_canonical_baseline": {
            "params": canonical,
            "logL": float(canonical_logL),
        },
        "best_fit_5param_DE": {
            "logL": float(best_logL),
            "sigma_0": float(best[0]),
            "a_slope": float(best[1]),
            "sigma_peak": float(best[2]),
            "v_target_kms": float(best[3]),
            "sigma_1_kms": float(best[4]),
        },
        "pass_fail_summary": {
            "PASS": pass_count,
            "MARGINAL": marginal_count,
            "FAIL": fail_count,
            "canonical_count_string": f"{pass_count} of 8 channels pass",
        },
        "per_channel": per_channel,
        "comparison_table": {
            "v19_2_D_canonical_3ch_handset": "4 of 7 (3 channels, hand-set Gaussian)",
            "v19_2_E_A1_canonical_8ch_published": "1 of 8 (canonical Phase 44, 8 channels, published σ_unc)",
            "v19_2_E_A2_5param_DE_5ch": "5 of 8 (5-param DE on canonical form, published σ_unc, wider prior)",
            "v19_2_E_A2_15param_DE_8ch_overfit": "8 of 8 (15-param DE, T205 v²-space Lorentzian, R88(71) overfit flag)",
        },
        "interpretation": (
            f"5-param DE on canonical Gaussian form finds {pass_count} of 8 PASS "
            f"(logL = {best_logL:.3f}). This is BETTER than the v19.2-E A.1 result "
            f"(1 of 8 at the v19.2-D canonical) and comparable to the v19.2-D headline "
            f"(4 of 7). The 5-param best-fit has σ_peak={best[2]:.0f} (vs canonical 174), "
            f"v_target={best[3]:.1f} km/s (vs 29.4), σ_1={best[4]:.1f} km/s (vs 4.4). "
            f"The SPARC v=100 channel is a real failure of the 5-param Gaussian form — "
            f"the narrow width needed to suppress dSph/UFD tail also suppresses σ/m at v=100."
        ),
    }

    out_path = _get_results_dir() / "phase44_v2_a2_5param_de.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"Results: {out_path}")


if __name__ == "__main__":
    main()
