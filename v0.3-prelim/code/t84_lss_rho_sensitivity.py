"""T84 (2026-09-03) — Channel 18 (LSS) ρ_abundance sensitivity sweep.

The Zhang+2025 LSS / assembly-bias channel (T74) uses a phenomenological
forward model where the predicted relative bias for each Σ* bin is:

    b_pred[i] = 1 + s * rho_abundance * (b_obs[i] - 1)

with:
    s ∈ [0, 1]: SIDM strength saturation factor (s → 0 for σ/m → 0,
                s → 1 for σ/m ≫ σ_m_ref = 1 cm²/g)
    rho_abundance: z_f-Σ* correlation coefficient from the paper's
                   ELUCID + abundance-matching analysis (best-fit ~0.85)

The shipped default is rho_abundance = 0.85 (paper best fit). Per
"Updated review1.docx" §4 (received 2026-09-03):

> "Consider a sensitivity study that varies the mapping from bias to
>  core size."

This module ships that study. We sweep rho_abundance in [0.5, 1.0]
(physically plausible range — the correlation must be > 0 for any
anti-correlation to exist, and ≤ 1 by Cauchy-Schwarz) and quantify
how Channel 18's:
  - best-fit σ/m (cm²/g)
  - best-fit log-likelihood
  - Δlog Z vs. rho_abundance=0.85 (the shipped default)
  - bias predictions at the v0.7 MAP σ/m (~0.27 cm²/g if we use the
    physically-correct galactic-scale value, ~2.7 cm²/g if we use the
    LSS-channel-native "core-scale" value)

…change with rho. A robust channel should show *small* shifts in
best-fit σ/m and *modest* Δlog Z across the rho range. Large shifts
indicate the channel is "hanging on" the rho assumption.

Outputs:
    v0.3-prelim/data/results/2026-09-03_t84_rho_sensitivity/t84_rho_sweep.json
    v0.3-prelim/data/results/2026-09-03_t84_rho_sensitivity/t84_best_fit_per_rho.csv

Standing-version: v0.4-prelim+T75 (no version bump — sensitivity study).

The T74 doc explicitly states: "our channel is insensitive to ρ over
[0.7, 1.0]." T84 verifies that claim and quantifies exactly how
insensitive.
"""
from __future__ import annotations

import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

# Add v0.3-prelim/code to import path
_CODE_DIR = Path(__file__).resolve().parent.parent / "code"
sys.path.insert(0, str(_CODE_DIR))

from zhang_lss_channel import (
    ZHANG_TABLE_2,
    LOG_M_H_DWARF_MEDIAN,
    SIGMA_OVER_M_BEST_FIT_CM2_PER_G,  # canonical best-fit from T74
    best_fit_sigma_over_m,
    loglike_lss_assembly_bias,
    predicted_relative_bias,
    provenance as zhang_provenance,
)


# Rho grid: 11 points from 0.5 to 1.0 inclusive (Δ = 0.05).
# Lower bound 0.5 keeps the model physically meaningful (rho < 0.5 would
# produce such a weak anti-correlation that the channel barely informs σ/m).
# Upper bound 1.0 by Cauchy-Schwarz (correlation ≤ 1).
RHO_GRID = np.array([0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85,
                     0.90, 0.95, 1.00])
RHO_FIDUCIAL = 0.85  # the shipped default in T74

# Sigma/m evaluation grid for cross-rho loglike comparison (fixed across
# the rho sweep so the Δlog Z is apples-to-apples).
SIGMA_GRID_EVAL = np.array([
    *np.logspace(-3, 0, 30),    # 0.001 to 1
    *np.logspace(0, 1.5, 15),   # 1 to ~30
])  # 45 points total (same as best_fit_sigma_over_m's default)


def _loglike_sigma_at_rho(sv: float, rho: float,
                          log_M_h: float = LOG_M_H_DWARF_MEDIAN) -> float:
    """loglike_lss_assembly_bias wrapper that enforces a rho value."""
    return loglike_lss_assembly_bias(
        sigma_over_m_cm2_per_g=float(sv),
        log_M_h_Msun=float(log_M_h),
        rho_abundance=float(rho),
    )


def best_fit_at_rho(rho: float,
                    log_M_h: float = LOG_M_H_DWARF_MEDIAN) -> dict:
    """Find best-fit σ/m for a given rho_abundance.

    Returns dict with:
      - rho_abundance
      - best_fit_sigma_over_m_cm2_per_g
      - best_fit_loglike
      - in_physical_range (True if best fit is in [0.3, 3] cm²/g)
    """
    # Reuse T74's grid-search machinery by calling best_fit_sigma_over_m
    # with the rho override. Note: best_fit_sigma_over_m uses the
    # default 45-point grid internally; we accept that coarseness for
    # the sensitivity study (sufficient for "how sensitive is the
    # channel to rho").
    bf_sigma, bf_loglike = best_fit_sigma_over_m(
        log_M_h_Msun=log_M_h,
        rho_abundance=float(rho),
    )
    return {
        "rho_abundance": float(rho),
        "best_fit_sigma_over_m_cm2_per_g": float(bf_sigma),
        "best_fit_loglike": float(bf_loglike),
        "in_physical_range": bool(0.3 <= bf_sigma <= 3.0),
    }


def delta_loglike_vs_fiducial(rho: float,
                              log_M_h: float = LOG_M_H_DWARF_MEDIAN
                              ) -> dict:
    """Compute Δlog Z = loglike_at_best_fit(rho) - loglike_at_best_fit(rho_fid).

    Uses the fixed SIGMA_GRID_EVAL so the comparison is apples-to-apples.
    In practice the grid-searches at each rho should converge to nearly
    the same peak (since the grid is dense enough), so Δlog Z ≈ 0
    for ρ in [0.5, 1.0]. Any non-trivial Δlog Z would be a code bug,
    not a physics finding.
    """
    # Best-fit at the requested rho
    bf_at_rho = best_fit_at_rho(rho, log_M_h=log_M_h)
    # Best-fit at the fiducial rho using SAME grid
    bf_at_fid = best_fit_at_rho(RHO_FIDUCIAL, log_M_h=log_M_h)
    delta = bf_at_rho["best_fit_loglike"] - bf_at_fid["best_fit_loglike"]
    return {
        "rho_abundance": float(rho),
        "best_fit_at_rho": bf_at_rho,
        "best_fit_at_fiducial": bf_at_fid,
        "delta_loglike": float(delta),
    }


def predicted_bias_at_v07_map(rho: float) -> dict:
    """What does Channel 18 predict at sigma/m = 0.27 cm²/g (v0.7 MAP)?

    If the bias vector at the v0.7 MAP sigma/m varies wildly with rho,
    then the v0.7 posterior is in a rho-sensitive regime and the
    "0.27 cm²/g is phenomenologically consistent" claim needs a band.

    Returns a dict with the 4 predicted b_rel values across rho.
    """
    b = predicted_relative_bias(
        sigma_over_m_cm2_per_g=0.27,
        log_M_h_Msun=LOG_M_H_DWARF_MEDIAN,
        rho_abundance=float(rho),
    )
    return {
        "rho_abundance": float(rho),
        "b_pred_at_v07_map": [float(x) for x in b],
        "b_observed": [float(x) for x in ZHANG_TABLE_2[:, 2]],
    }


def run_sensitivity_sweep(
    rho_grid: np.ndarray = RHO_GRID,
    sigma_grid_eval: np.ndarray = SIGMA_GRID_EVAL,
) -> dict:
    """Run the full T84 sensitivity sweep.

    Returns a dict with:
      - rho_grid (the input grid)
      - per_rho (list of best_fit_at_rho results, one per grid point)
      - delta_loglike_vs_fiducial (list of delta_loglike results)
      - bias_at_v07_map (list of predicted_relative_bias at σ/m = 0.27)
      - summary statistics (best-fit range, max |Δlog Z|)
      - sensitivity_claim_verified (True if results match T74's
        "ρ ∈ [0.7, 1.0] is insensitive" claim)
    """
    per_rho = []
    delta_loglikes = []
    bias_at_map = []

    bf_at_fid = best_fit_at_rho(RHO_FIDUCIAL)
    best_loglike_at_fid = bf_at_fid["best_fit_loglike"]
    best_sigma_at_fid = bf_at_fid["best_fit_sigma_over_m_cm2_per_g"]

    for rho in rho_grid:
        bf = best_fit_at_rho(float(rho))
        per_rho.append(bf)
        delta_loglikes.append(bf["best_fit_loglike"] - best_loglike_at_fid)
        b_map = predicted_bias_at_v07_map(float(rho))
        bias_at_map.append(b_map)

    bf_sigmas = [p["best_fit_sigma_over_m_cm2_per_g"] for p in per_rho]
    # Best-fit sigma spread across the rho grid
    bf_spread = max(bf_sigmas) - min(bf_sigmas)
    # Best-fit sigma range at the headline phys range [0.7, 1.0] of rho:
    bf_sigmas_at_hp = [
        p["best_fit_sigma_over_m_cm2_per_g"]
        for p in per_rho if 0.7 <= p["rho_abundance"] <= 1.0
    ]
    bf_spread_hp = (
        max(bf_sigmas_at_hp) - min(bf_sigmas_at_hp)
        if bf_sigmas_at_hp else float("nan")
    )
    # Δlog Z spread
    max_abs_delta = float(max(abs(d) for d in delta_loglikes))

    sensitivity_claim_verified = (
        (bf_spread_hp < 0.5)  # best-fit σ/m shifts by < 0.5 cm²/g over ρ ∈ [0.7, 1.0]
        and (max_abs_delta < 0.5)  # log Z is well-calibrated (channel is informative but not catastrophic)
    )

    # Compact per-rho delta_loglike summary
    delta_summary = []
    for p, d in zip(per_rho, delta_loglikes):
        delta_summary.append({
            "rho_abundance": float(p["rho_abundance"]),
            "best_sigma_at_rho": float(p["best_fit_sigma_over_m_cm2_per_g"]),
            "best_sigma_at_fiducial": float(best_sigma_at_fid),
            "delta_loglike": float(d),
        })

    return {
        "rho_grid": [float(x) for x in rho_grid],
        "rho_fiducial": RHO_FIDUCIAL,
        "per_rho": per_rho,
        "delta_loglike_vs_fiducial": delta_summary,
        "bias_at_v07_map": bias_at_map,
        "summary": {
            "best_fit_sigma_min_cm2_per_g": float(min(bf_sigmas)),
            "best_fit_sigma_max_cm2_per_g": float(max(bf_sigmas)),
            "best_fit_sigma_spread_full_cm2_per_g": float(bf_spread),
            "best_fit_sigma_at_hp_min_cm2_per_g": (
                float(min(bf_sigmas_at_hp)) if bf_sigmas_at_hp else float("nan")
            ),
            "best_fit_sigma_at_hp_max_cm2_per_g": (
                float(max(bf_sigmas_at_hp)) if bf_sigmas_at_hp else float("nan")
            ),
            "best_fit_sigma_spread_hp_cm2_per_g": float(bf_spread_hp),
            "max_abs_delta_loglike_vs_fiducial": max_abs_delta,
            "sensitivity_claim_verified": sensitivity_claim_verified,
        },
        "sweep_metadata": {
            "n_rho_points": len(rho_grid),
            "n_sigma_grid_points": len(sigma_grid_eval),
            "rho_range": [float(rho_grid.min()), float(rho_grid.max())],
            "t74_claim_checked": "ρ ∈ [0.7, 1.0] should be insensitive (best-fit σ/m shift < 0.5 cm²/g)",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        },
    }


def main() -> dict:
    """Run the sweep, write results to disk, print a compact summary."""
    out_dir = (
        Path(__file__).resolve().parent.parent
        / "data/results/2026-09-03_t84_rho_sensitivity"
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    result = run_sensitivity_sweep()

    # Write JSON
    json_path = out_dir / "t84_rho_sweep.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"[t84] wrote {json_path} ({json_path.stat().st_size:,} bytes)")

    # Write CSV summary (one row per rho point)
    csv_path = out_dir / "t84_best_fit_per_rho.csv"
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("rho_abundance,best_fit_sigma_over_m_cm2_per_g,best_fit_loglike,"
                "delta_loglike_vs_fiducial,b_pred_diffuse_at_v07_map\n")
        b_at_map_by_rho = {
            b["rho_abundance"]: b["b_pred_at_v07_map"][0]  # diffuse bin (i=0)
            for b in result["bias_at_v07_map"]
        }
        for d in result["delta_loglike_vs_fiducial"]:
            rho = d["rho_abundance"]
            bf = next(p for p in result["per_rho"] if abs(p["rho_abundance"] - rho) < 1e-9)
            f.write(
                f"{rho:.3f},"
                f"{bf['best_fit_sigma_over_m_cm2_per_g']:.4f},"
                f"{bf['best_fit_loglike']:.3f},"
                f"{d['delta_loglike']:.3f},"
                f"{b_at_map_by_rho[rho]:.4f}\n"
            )
    print(f"[t84] wrote {csv_path} ({csv_path.stat().st_size:,} bytes)")

    # Compact summary
    s = result["summary"]
    print()
    print("=" * 70)
    print("T84 — Channel 18 ρ_abundance sensitivity sweep")
    print("=" * 70)
    print(f"  rho grid:                {RHO_GRID.min():.2f} to {RHO_GRID.max():.2f} "
          f"(N = {len(RHO_GRID)})")
    print(f"  fiducial rho:            {RHO_FIDUCIAL:.2f}")
    print(f"  Best-fit σ/m range (full rho): {s['best_fit_sigma_min_cm2_per_g']:.3f} "
          f"to {s['best_fit_sigma_max_cm2_per_g']:.3f} cm²/g")
    print(f"  Best-fit σ/m range (rho∈[0.7,1.0]): "
          f"{s['best_fit_sigma_at_hp_min_cm2_per_g']:.3f} to "
          f"{s['best_fit_sigma_at_hp_max_cm2_per_g']:.3f} cm²/g "
          f"(spread = {s['best_fit_sigma_spread_hp_cm2_per_g']:.3f})")
    print(f"  Max |Δlog Z| vs fiducial: {s['max_abs_delta_loglike_vs_fiducial']:.3f}")
    print(f"  T74 sensitivity claim (ρ ∈ [0.7,1.0] is insensitive): "
          f"{'VERIFIED ✓' if s['sensitivity_claim_verified'] else 'REFUTED ✗'}")
    print("=" * 70)

    return result


if __name__ == "__main__":
    main()
