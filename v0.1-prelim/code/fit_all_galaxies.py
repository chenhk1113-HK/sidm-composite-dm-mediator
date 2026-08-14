#!/usr/bin/env python
"""
T1/T2 batch runner: fit all 175 SPARC galaxies with NFW + Burkert.

Usage:
    python fit_all_galaxies.py

Output: per-galaxy JSON in data/results/fit_<gal>_<profile>.json
Plus a batch_summary.json with aggregate statistics.

This is the v0.1-prelim batch. Estimated wall ~3 minutes.
"""
from __future__ import annotations
import sys
import time
import json
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sparc_loader import load_all_sparc
from fit_single_galaxy import fit_one_galaxy, RESULTS_DIR, DATA_DIR

PROFILES = ["NFW", "Burkert"]


def main():
    galaxies = load_all_sparc(DATA_DIR)
    print(f"[batch] loaded {len(galaxies)} galaxies")
    print(f"[batch] will fit each with {PROFILES} = {2 * len(galaxies)} total fits")

    summary = {
        "n_galaxies": len(galaxies),
        "profiles": PROFILES,
        "started_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "per_fit": {},
        "delta_log_Z": {},  # log Z (Burkert) - log Z (NFW) per galaxy
    }

    t_total = time.time()
    for profile in PROFILES:
        for i, g in enumerate(galaxies):
            t0 = time.time()
            try:
                res = fit_one_galaxy(g.name, profile)
                summary["per_fit"].setdefault(profile, {})[g.name] = {
                    "log_Z": res["log_Z"],
                    "log_Z_err": res["log_Z_err"],
                    "chi2_red": res["chi2_reduced_at_MAP"],
                    "wall_seconds": res["wall_seconds"],
                    "theta_MAP": res["theta_MAP"],
                }
                if i % 10 == 0:
                    elapsed = time.time() - t_total
                    est_remaining = elapsed * (len(galaxies) - i - 1) / max(i + 1, 1)
                    print(f"[batch {profile}] {i+1}/{len(galaxies)} ({g.name})  "
                          f"elapsed={elapsed:.0f}s  est_remaining={est_remaining:.0f}s")
            except Exception as e:
                print(f"[batch] FAIL {g.name} {profile}: {e}")
                summary["per_fit"].setdefault(profile, {})[g.name] = {"error": str(e)}

    # Compute delta log Z per galaxy
    for gname in [g.name for g in galaxies]:
        nfw = summary["per_fit"].get("NFW", {}).get(gname, {})
        bur = summary["per_fit"].get("Burkert", {}).get(gname, {})
        if "log_Z" in nfw and "log_Z" in bur:
            summary["delta_log_Z"][gname] = bur["log_Z"] - nfw["log_Z"]

    # Aggregate
    nfw_z = [v["log_Z"] for v in summary["per_fit"].get("NFW", {}).values() if "log_Z" in v]
    bur_z = [v["log_Z"] for v in summary["per_fit"].get("Burkert", {}).values() if "log_Z" in v]
    delta_z = list(summary["delta_log_Z"].values())
    summary["aggregate"] = {
        "n_NFW_ok": len(nfw_z),
        "n_Burkert_ok": len(bur_z),
        "NFW_total_log_Z": float(np.sum(nfw_z)),
        "Burkert_total_log_Z": float(np.sum(bur_z)),
        "sum_delta_log_Z_Burkert_minus_NFW": float(np.sum(delta_z)),
        "median_delta_log_Z": float(np.median(delta_z)),
        "n_Burkert_preferred": int(np.sum(np.array(delta_z) > 0)),
        "n_NFW_preferred": int(np.sum(np.array(delta_z) < 0)),
        "n_tied": int(np.sum(np.array(delta_z) == 0)),
    }
    summary["finished_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    summary["total_wall_seconds"] = float(time.time() - t_total)

    out = RESULTS_DIR / "batch_summary.json"
    out.write_text(json.dumps(summary, indent=2))
    print(f"\n[batch] DONE in {summary['total_wall_seconds']:.0f}s")
    print(f"[batch] {summary['aggregate']['n_NFW_ok']} NFW fits, "
          f"{summary['aggregate']['n_Burkert_ok']} Burkert fits OK")
    print(f"[batch] sum log Z Burkert = {summary['aggregate']['Burkert_total_log_Z']:.1f}")
    print(f"[batch] sum log Z NFW     = {summary['aggregate']['NFW_total_log_Z']:.1f}")
    print(f"[batch] sum delta (B-N)   = {summary['aggregate']['sum_delta_log_Z_Burkert_minus_NFW']:.1f}")
    print(f"[batch] {summary['aggregate']['n_Burkert_preferred']} galaxies prefer Burkert, "
          f"{summary['aggregate']['n_NFW_preferred']} prefer NFW")
    print(f"[batch] summary -> {out}")


if __name__ == "__main__":
    main()