"""
T69 — Baryonic-feedback nuisance: sensitivity sweep (v0.4-prelim).

Re-runs the T41 joint fit at multiple f_fb values and reports the
MAP shift in (sigma/m_0, m_phi, m_chi, g_chi, log_epsilon, log_alpha)
as a function of the feedback nuisance.

This is the "single high-leverage experiment" recommended in the
Baryonic feedback.docx critique (v0.3-prelim/docs/REVIEWER_BARYONIC_FEEDBACK.md §5).

Honest scope:
  - We re-run T41 at 5 f_fb values: {0.0, 0.25, 0.5, 0.75, 1.0}.
  - Wall time: ~5 min total (T41 takes ~56 s wall per run at 200 nlive).
  - Output: a single JSON with the MAP at each f_fb, plus the
    delta-sigma/m_0 vs f_fb=0 (no feedback).
  - We do NOT add f_fb as a 6th nested-sampling free parameter; that
    would require re-tuning the sampler and is out of scope.

Usage:
    # From v0.3-prelim/code/:
    F_FB_OVERRIDE=0.0 python t69_feedback_nuisance_rerun.py
    # or, programmatically:
    python t69_feedback_nuisance_rerun.py

Reference:
  - Review: Baryonic feedback.docx, 2026-08-19
  - Critique: v0.3-prelim/docs/REVIEWER_BARYONIC_FEEDBACK.md
  - Closed audit: v0.3-prelim/docs/R12_AUDIT_CLOSURE.md
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import numpy as np

CODE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = CODE_DIR.parent / "data" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(CODE_DIR))
sys.path.insert(0, str(CODE_DIR.parent.parent))  # v0.3-prelim/
sys.path.insert(0, str(CODE_DIR.parent.parent.parent / "v0.1-prelim" / "code"))

import feedback_nuisance as fb


def run_t41_with_f_fb(f_fb: float, nlive: int = 200, dlogz: float = 0.10):
    """Run the T41 joint fit at a given f_fb value.

    Sets the F_FB_OVERRIDE env var so t41_mediator_mass_joint_fit uses
    the right feedback rescaling, then invokes the T41 main function
    and extracts the MAP.

    IMPORTANT: t41_mediator_mass_joint_fit.main() OVERWRITES the canonical
    t41_mediator_mass_joint_fit.json each time it runs. We back up the
    canonical result to .canonical before each f_fb run, and restore it
    at the end. This way, the canonical T41 result (which carries the
    R12 closure's headline numbers) survives the sensitivity sweep.
    """
    # Back up the canonical T41 result before overwriting.
    canonical_path = RESULTS_DIR / "t41_mediator_mass_joint_fit.json"
    canonical_backup = RESULTS_DIR / "t41_mediator_mass_joint_fit.json.canonical"
    if canonical_path.exists():
        import shutil
        shutil.copy(str(canonical_path), str(canonical_backup))

    os.environ["F_FB_OVERRIDE"] = str(f_fb)
    print(f"\n{'=' * 70}")
    print(f"T69 sweep: f_fb = {f_fb}")
    print(f"{'=' * 70}")

    t0 = time.time()
    # Import inside the function so F_FB_OVERRIDE is picked up.
    import t41_mediator_mass_joint_fit as t41
    t41.main()
    wall = time.time() - t0

    # Read the resulting JSON and extract MAP + log Z.
    result_path = RESULTS_DIR / "t41_mediator_mass_joint_fit.json"
    with open(result_path) as f:
        result = json.load(f)

    # T41 stores its MAP in two forms:
    #   MAP: list of log-parameters at MAP (e.g. [log_m_phi_MeV, log_m_chi_GeV, g_chi, log_eps, log_alpha])
    #   MAP_physical: dict with physical-unit values including sigma/m_0_derived + a_derived
    map_params = {}
    map_log = result.get("MAP", [])
    params_names = result.get("parameters", [])
    if map_log and params_names:
        for name, val in zip(params_names, map_log):
            map_params[name] = float(val)

    map_physical = result.get("MAP_physical", {})
    if map_physical:
        map_params["m_phi_MeV"] = float(map_physical.get("m_phi_MeV", 0.0))
        map_params["m_chi_GeV"] = float(map_physical.get("m_chi_GeV", 0.0))
        map_params["g_chi"] = float(map_physical.get("g_chi", 0.0))
        map_params["sigma_m_0_derived"] = float(map_physical.get("sigma_m_0_derived", 0.0))
        map_params["a_derived"] = float(map_physical.get("a_derived", 0.0))

    return {
        "f_fb": f_fb,
        "wall_seconds": wall,
        "map_params": map_params,
        "log_z": result.get("log_Z", None),
        "log_z_err": result.get("log_Z_err", None),
        "interpretation": result.get("interpretation", None),
    }


def main():
    """Run the full f_fb sensitivity sweep."""
    # Back up the canonical T41 result before the sweep starts.
    # This is the R12 closure result; we MUST restore it at the end.
    canonical_path = RESULTS_DIR / "t41_mediator_mass_joint_fit.json"
    canonical_backup = RESULTS_DIR / "t41_mediator_mass_joint_fit.json.canonical"
    if canonical_path.exists():
        import shutil
        shutil.copy(str(canonical_path), str(canonical_backup))
        print(f"Backed up canonical T41 result to {canonical_backup.name}")

    print("=" * 70)
    print("T69 — Baryonic-feedback nuisance sensitivity sweep")
    print("=" * 70)
    print(f"SPARC population-mean M*/M_h = {fb.SPARC_POPULATION_MEAN_MSTAR_OVER_MHALO}")
    print(f"R_corr_raw at SPARC mean = {fb.R_corr_raw(fb.SPARC_POPULATION_MEAN_MSTAR_OVER_MHALO):.4f}")
    print(f"R_corr_raw at dwarf limit (M*/M_h = 1e-3) = {fb.R_corr_raw(1e-3):.4e}")
    print(f"Di Cintio relation predicts feedback CAN produce cores at the SPARC mean")
    print(f"-> the prior on f_fb is peaked at 0.4 (moderate feedback)")

    f_fb_grid = fb.make_f_fb_grid(n_points=5)
    print(f"\nf_fb grid: {f_fb_grid.tolist()}")

    sweep_results = []
    for f_fb in f_fb_grid:
        try:
            res = run_t41_with_f_fb(float(f_fb))
            sweep_results.append(res)
            print(f"\n>>> f_fb = {f_fb}: MAP = {res['map_params']}")
            print(f">>> wall = {res['wall_seconds']:.1f}s, log Z = {res['log_z']}")
        except Exception as e:
            print(f"\n>>> f_fb = {f_fb}: FAILED ({e})")
            sweep_results.append({"f_fb": float(f_fb), "error": str(e)})

    # Save the sweep results.
    out_path = RESULTS_DIR / "t69_feedback_nuisance_sweep.json"
    with open(out_path, "w") as f:
        json.dump(
            {
                "sweep_results": sweep_results,
                "metadata": {
                    "n_points": len(f_fb_grid),
                    "f_fb_grid": f_fb_grid.tolist(),
                    "formulation": "weight = max(0, 1 - f_fb)",
                    "di_cintio_2014a_slope": fb.DI_CINTIO_2014A_SLOPE,
                    "di_cintio_2014a_intercept": fb.DI_CINTIO_2014A_INTERCEPT,
                    "sparc_pop_mean_mstar_over_mhalo": fb.SPARC_POPULATION_MEAN_MSTAR_OVER_MHALO,
                },
                "review_provenance": {
                    "docx": "Baryonic feedback.docx, 2026-08-19",
                    "critique": "v0.3-prelim/docs/REVIEWER_BARYONIC_FEEDBACK.md",
                    "audit": "v0.3-prelim/docs/R12_AUDIT_CLOSURE.md",
                },
            },
            f,
            indent=2,
            default=str,
        )
    print(f"\n{'=' * 70}")
    print(f"Sweep results saved to {out_path}")
    print(f"{'=' * 70}")

    # Print summary
    print("\nSummary:")
    print(f"{'f_fb':>6}  {'sigma/m_0':>12}  {'m_phi (MeV)':>12}  {'m_chi (GeV)':>12}  {'a (derived)':>12}  {'log Z':>10}  {'wall (s)':>10}")
    for r in sweep_results:
        if "error" in r:
            print(f"{r['f_fb']:>6.2f}  ERROR: {r['error']}")
            continue
        mp = r.get("map_params") or {}
        sm = mp.get("sigma_m_0_derived", None)
        mp_mev = mp.get("m_phi_MeV", None)
        mp_chi = mp.get("m_chi_GeV", None)
        a_der = mp.get("a_derived", None)
        log_z = r.get("log_z", None)
        log_z_str = f"{log_z:>10.3f}" if isinstance(log_z, (int, float)) else f"{'N/A':>10}"
        print(
            f"{r['f_fb']:>6.2f}  "
            f"{sm:>12.4f}  "
            f"{mp_mev:>12.2f}  "
            f"{mp_chi:>12.2f}  "
            f"{a_der:>12.4f}  "
            f"{log_z_str}  "
            f"{r['wall_seconds']:>10.1f}"
        )

    # Compute the shift relative to f_fb=0.
    if len(sweep_results) >= 2 and "map_params" in sweep_results[0] and "map_params" in sweep_results[-1]:
        sm_no_fb = sweep_results[0]["map_params"].get("sigma_m_0_derived", 0)
        sm_full_fb = sweep_results[-1]["map_params"].get("sigma_m_0_derived", 0)
        if sm_no_fb and sm_no_fb > 0:
            shift_pct = 100 * (sm_full_fb - sm_no_fb) / sm_no_fb
            a_no_fb = sweep_results[0]["map_params"].get("a_derived", 0)
            a_full_fb = sweep_results[-1]["map_params"].get("a_derived", 0)
            a_shift = a_full_fb - a_no_fb
            print(f"\n>>> Delta-sigma/m_0 at f_fb=1.0 vs f_fb=0.0: {shift_pct:+.1f}%")
            print(f">>> Delta-a (Yukawa velocity index) at f_fb=1.0 vs f_fb=0.0: {a_shift:+.3f}")
            print(f">>> Per the critique, a sigma/m shift >30% flags as a real new-physics finding.")
            if abs(shift_pct) > 30:
                print(">>> STATUS: FLAGGED as a real new-physics finding.")
            else:
                print(">>> STATUS: Within R12 caveat #4 tolerance (<30%). Fold into caveat #5.")

    # Restore the canonical T41 result (overwritten by each f_fb run).
    if canonical_backup.exists():
        import shutil
        shutil.copy(str(canonical_backup), str(canonical_path))
        print(f"\n{'=' * 70}")
        print(f"Restored canonical T41 result from {canonical_backup.name}")
        print(f"{'=' * 70}")


if __name__ == "__main__":
    main()