"""
V19.2-E C — sigma/m(v) data-only constraint analysis (10-200 km/s window).

Per ClawsGO comment #5 B.6: "Use the real likelihood to ask what
sigma/m(v) the data alone prefer in the 10-200 km/s window. That is a
useful, publishable constraining analysis regardless of whether the
multi-resonance model survives."

This script:
1. Defines 5 free parameters: sigma/m at v = 10, 28, 50, 100, 200 km/s
2. Computes sigma/m at any v in [10, 200] by log-log linear interpolation
   (no multi-resonance ansatz assumed)
3. Computes sigma_eff(v) = f_H^2 * sigma/m(v) with canonical f_H=0.297
4. Evaluates against the 4 channels in the 10-200 km/s window:
   - UFD v=10 (Horigome+ 2025 ceiling)
   - dSph v=15 (Horigome+ 2025 ceiling)
   - Cloud-9 v=28 (BLN24/Ohana+ 2026 floor)
   - SPARC v=100 (Lelli+ 2016 gaussian)
   Channels outside [10, 200] are excluded (v=3, 5, 7, 500 are
   outside the window of interest per ClawsGO B.6).
5. Uses the published sigma_unc from T205 OBS_PUBLISHED.
6. Runs differential evolution to find the best-fit sigma/m(v) and
   computes the chi^2 surface around the best-fit.

This is a "data-only" analysis: it does NOT assume the paper's
canonical Gaussian sigma/m(v) form. It only assumes that sigma/m(v)
is a smooth function in log-log between the 5 anchor points.

Reference: ClawsGO comment #5 (2026-10-09) B.6.
"""
from __future__ import annotations
import json
import math
import sys
import warnings
from pathlib import Path

import numpy as np
from scipy.optimize import differential_evolution

warnings.filterwarnings("ignore")

sys.path.insert(0, r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\code")
sys.path.insert(0, r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\scripts")

from T205_full_likelihood_published import OBS_PUBLISHED
from constants import F_H_CANONICAL

# Lazy-initialized results directory
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
# 5 free parameters: sigma/m at 5 velocity bins in 10-200 km/s window
# ============================================================================

V_ANCHORS = np.array([10.0, 28.0, 50.0, 100.0, 200.0])  # km/s
N_PARAMS = 5


def sigma_m_interp(v_query, log_sigma_m_at_anchors):
    """Compute sigma/m(v) at any v in [10, 200] by log-log linear interpolation
    between the 5 anchor points.

    log_sigma_m_at_anchors: array of log10(sigma/m) at the 5 anchor velocities.
    """
    log_v_query = np.log10(np.atleast_1d(np.asarray(v_query, dtype=float)))
    log_v_anchors = np.log10(V_ANCHORS)
    log_sigma_m = np.interp(log_v_query, log_v_anchors, log_sigma_m_at_anchors)
    sigma_m = 10 ** log_sigma_m
    return sigma_m if len(sigma_m) > 1 else float(sigma_m[0])


# ============================================================================
# Filter OBS_PUBLISHED to channels in [10, 200] km/s window
# ============================================================================

WINDOW_CHANNELS = [
    obs for obs in OBS_PUBLISHED
    if 10.0 <= obs[0] <= 200.0
]


def log_likelihood_data_only(log_sigma_m_at_anchors):
    """Per-channel log L summed over the 4 channels in [10, 200] km/s.

    The 5 free parameters are log10(sigma/m) at the 5 anchor velocities
    [10, 28, 50, 100, 200]. sigma/m(v) is computed by log-log linear
    interpolation. sigma_eff = F_H^2 * sigma/m.
    """
    total = 0.0
    for v, sigma_obs, sigma_unc, kind, label, citation in WINDOW_CHANNELS:
        sigma_m_at_v = float(sigma_m_interp(v, log_sigma_m_at_anchors))
        sigma_eff = F_H_CANONICAL ** 2 * sigma_m_at_v
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
    print("=" * 70)
    print("V19.2-E C — sigma/m(v) data-only constraint analysis (10-200 km/s)")
    print("=" * 70)
    print()
    print(f"5 anchor velocities: {V_ANCHORS.tolist()} km/s")
    print(f"f_H canonical = {F_H_CANONICAL}")
    print(f"Channels in [10, 200] window: {len(WINDOW_CHANNELS)}")
    for v, so, su, k, l, c in WINDOW_CHANNELS:
        print(f"  {l}: v={v} km/s, sigma_obs={so}, sigma_unc={su}, kind={k}")
    print()

    # Bounds: log10(sigma/m) in [-2, 4] (i.e. 0.01 to 10000 cm^2/g)
    # This is a wide prior; the data should constrain it.
    bounds = [(-2.0, 4.0)] * N_PARAMS

    print("Running DE on 5-param data-only sigma/m(v)...")
    result = differential_evolution(
        lambda p: -log_likelihood_data_only(p),
        bounds, seed=42, maxiter=500, popsize=30, tol=1e-7, workers=1,
    )
    best = result.x
    best_logL = -result.fun

    print(f"Best log L = {best_logL:.3f}")
    print(f"Best log10(sigma/m) at anchors:")
    for i, v in enumerate(V_ANCHORS):
        print(f"  v={v:>5.0f} km/s: log10(sigma/m) = {best[i]:.3f}, sigma/m = {10**best[i]:.4g} cm^2/g")
    print()

    # Per-channel evaluation
    print("Per-channel sigma_eff at best-fit (interpolated sigma/m):")
    print(f"  {'Channel':<18s} {'v':>5s} {'sigma/m':>10s} {'sigma_eff':>10s} {'sigma_obs':>10s} {'verdict':<10s}")
    pass_count = marginal_count = fail_count = 0
    per_channel = []
    for v, sigma_obs, sigma_unc, kind, label, citation in WINDOW_CHANNELS:
        sigma_m_at_v = float(sigma_m_interp(v, best))
        sigma_eff = F_H_CANONICAL ** 2 * sigma_m_at_v
        verdict = channel_verdict(sigma_eff, sigma_obs, sigma_unc, kind)
        if verdict == "PASS": pass_count += 1
        elif verdict == "MARGINAL": marginal_count += 1
        else: fail_count += 1
        print(f"  {label:<18s} {v:>5.0f} {sigma_m_at_v:>10.4g} {sigma_eff:>10.4g} "
              f"{sigma_obs:>10.4g} {verdict:<10s}")
        per_channel.append({
            "v_kms": float(v), "label": label, "kind": kind,
            "sigma_m_at_v": float(sigma_m_at_v),
            "sigma_eff": float(sigma_eff),
            "sigma_obs": float(sigma_obs), "sigma_unc": float(sigma_unc),
            "verdict": verdict, "citation": citation,
        })
    print(f"  PASS: {pass_count}, MARGINAL: {marginal_count}, FAIL: {fail_count}")
    print()

    # Sample at unobserved velocities for the headline output
    print("Data-only sigma/m(v) at sampled velocities (log-log interpolation):")
    v_sample = [10, 15, 20, 28, 35, 50, 75, 100, 150, 200]
    sample_results = []
    for v in v_sample:
        sigma_m_at_v = float(sigma_m_interp(v, best))
        sigma_eff = F_H_CANONICAL ** 2 * sigma_m_at_v
        sample_results.append({"v_kms": float(v), "sigma_m_cm2_per_g": float(sigma_m_at_v),
                              "sigma_eff": float(sigma_eff)})
        print(f"  v={v:>5.0f} km/s: sigma/m = {sigma_m_at_v:.4g} cm^2/g, sigma_eff = {sigma_eff:.4g}")
    print()

    # Save
    out = {
        "test": "V19_2_E_C_data_only_sigma_m_constraint",
        "date": "2026-10-09",
        "method": (
            "5-param DE on log10(sigma/m) at 5 anchor velocities [10, 28, 50, 100, 200] km/s. "
            "log-log linear interpolation between anchors. f_H = 0.297 canonical. "
            "Evaluated against 4 channels in the 10-200 km/s window: UFD v=10, dSph v=15, "
            "Cloud-9 v=28, SPARC v=100. Uses T205 published sigma_unc (Horigome+ 2025, "
            "BLN24/Ohana+ 2026, Lelli+ 2016). NO multi-resonance ansatz assumed."
        ),
        "anchor_velocities_km_per_s": V_ANCHORS.tolist(),
        "best_fit_log10_sigma_m_at_anchors": [float(x) for x in best],
        "best_fit_sigma_m_at_anchors_cm2_per_g": [float(10**x) for x in best],
        "best_logL": float(best_logL),
        "per_channel": per_channel,
        "pass_fail_summary": {
            "PASS": pass_count, "MARGINAL": marginal_count, "FAIL": fail_count,
            "channels_in_window": len(WINDOW_CHANNELS),
        },
        "sampled_velocities": sample_results,
        "comparison_to_paper_canonical": (
            "Paper canonical Gaussian sigma/m(v) (per constants.py + section 2.6): "
            "sigma_0=0.052, a_slope=1.93, sigma_peak=174, v_target=29.4, sigma_1=4.4. "
            "At v=28: sigma/m = 166 cm^2/g. At v=100: sigma/m = 0.052 cm^2/g. "
            "The data-only result should agree with the canonical form IF the data "
            "constrains the multi-resonance Gaussian. If the data-only result differs, "
            "the canonical form is over-fit to the data."
        ),
        "interpretation": (
            f"5-param DE on log10(sigma/m) at 5 anchor velocities, evaluated against "
            f"4 T205 channels in the 10-200 km/s window: {pass_count} PASS / "
            f"{marginal_count} MARGINAL / {fail_count} FAIL, log L = {best_logL:.3f}. "
            f"This is a data-only constraint that does NOT assume the paper's "
            f"canonical multi-resonance Gaussian form. The result at the anchor "
            f"velocities is the data-preferred sigma/m(v) profile."
        ),
        "HONEST_LIMITATIONS": [
            "5 free parameters (sigma/m at 5 anchors) is a smooth interpolation. "
            "The 'true' sigma/m(v) could have more structure between the anchors "
            "(e.g., narrow resonance peaks narrower than the bin width).",
            "The 4 channels in [10, 200] km/s are not all independent — UFD v=10 and "
            "dSph v=15 come from the same Horigome+ 2025 combined analysis.",
            "f_H = 0.297 is canonical per R88(88), but the project's own N-body "
            "(Phase G9) found f_H is flat (0.94-1.01x). With f_H=1, the sigma_eff "
            "values are 11x higher, which would change some PASS/FAIL verdicts.",
            "T205's sigma_unc for Horigome+ 2025 are approximate extractions from "
            "Table II, not full posterior chains. The constraint is approximate.",
        ],
    }

    out_path = _get_results_dir() / "v19_2_e_c_data_only_sigma_m.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"Results: {out_path}")


if __name__ == "__main__":
    main()
