#!/usr/bin/env python
"""
T4 batch: fit all 175 SPARC galaxies with NFW + Burkert + Υ_d marginalization.

Output: per-galaxy t4_fit_<gal>_<profile>.json + t4_batch_summary.json
"""
from __future__ import annotations
import sys
import time
import json
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sparc_loader import load_all_sparc
from fit_t4_3param import fit_one_galaxy_3p, RESULTS_DIR, DATA_DIR

PROFILES = ["NFW", "Burkert"]


def main():
    galaxies = load_all_sparc(DATA_DIR)
    print(f"[T4 batch] loaded {len(galaxies)} galaxies")

    summary = {
        "n_galaxies": len(galaxies),
        "profiles": PROFILES,
        "started_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "per_fit": {},
        "delta_log_Z": {},
    }
    t_total = time.time()
    for profile in PROFILES:
        for i, g in enumerate(galaxies):
            t0 = time.time()
            try:
                res = fit_one_galaxy_3p(g.name, profile)
                summary["per_fit"].setdefault(profile, {})[g.name] = {
                    "log_Z": res["log_Z"],
                    "log_Z_err": res["log_Z_err"],
                    "chi2_red": res["chi2_reduced_at_MAP"],
                    "wall_seconds": res["wall_seconds"],
                    "theta_MAP": res["theta_MAP"],
                    "XI_d_at_MAP": 10**res["theta_MAP"]["log_XI_d"],
                }
                if i % 10 == 0:
                    elapsed = time.time() - t_total
                    est_remaining = elapsed * (len(galaxies) - i - 1) / max(i + 1, 1)
                    print(f"[T4 batch {profile}] {i+1}/{len(galaxies)} ({g.name})  "
                          f"elapsed={elapsed:.0f}s  est_remaining={est_remaining:.0f}s")
            except Exception as e:
                print(f"[T4 batch] FAIL {g.name} {profile}: {e}")
                summary["per_fit"].setdefault(profile, {})[g.name] = {"error": str(e)}

    for gname in [g.name for g in galaxies]:
        nfw = summary["per_fit"].get("NFW", {}).get(gname, {})
        bur = summary["per_fit"].get("Burkert", {}).get(gname, {})
        if "log_Z" in nfw and "log_Z" in bur:
            summary["delta_log_Z"][gname] = bur["log_Z"] - nfw["log_Z"]

    nfw_z = [v["log_Z"] for v in summary["per_fit"].get("NFW", {}).values() if "log_Z" in v]
    bur_z = [v["log_Z"] for v in summary["per_fit"].get("Burkert", {}).values() if "log_Z" in v]
    delta = list(summary["delta_log_Z"].values())
    delta_arr = np.array(delta)
    summary["aggregate"] = {
        "n_NFW_ok": len(nfw_z),
        "n_Burkert_ok": len(bur_z),
        "NFW_total_log_Z": float(np.sum(nfw_z)),
        "Burkert_total_log_Z": float(np.sum(bur_z)),
        "sum_delta_log_Z_Burkert_minus_NFW": float(np.sum(delta_arr)),
        "median_delta_log_Z": float(np.median(delta_arr)),
        "n_Burkert_preferred": int(np.sum(delta_arr > 0)),
        "n_NFW_preferred":     int(np.sum(delta_arr < 0)),
    }
    summary["finished_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    summary["total_wall_seconds"] = float(time.time() - t_total)

    out = RESULTS_DIR / "t4_batch_summary.json"
    out.write_text(json.dumps(summary, indent=2))
    print(f"\n[T4 batch] DONE in {summary['total_wall_seconds']:.0f}s")
    print(f"[T4 batch] {len(nfw_z)} NFW + {len(bur_z)} Burkert fits OK")
    print(f"[T4 batch] sum log Z Burkert = {summary['aggregate']['Burkert_total_log_Z']:.1f}")
    print(f"[T4 batch] sum log Z NFW     = {summary['aggregate']['NFW_total_log_Z']:.1f}")
    print(f"[T4 batch] sum delta (B-N)   = {summary['aggregate']['sum_delta_log_Z_Burkert_minus_NFW']:.1f}")
    print(f"[T4 batch] {summary['aggregate']['n_Burkert_preferred']} prefer Burkert, "
          f"{summary['aggregate']['n_NFW_preferred']} prefer NFW")
    print(f"[T4 batch] summary -> {out}")


if __name__ == "__main__":
    main()