#!/usr/bin/env python
"""T6 batch: fit all 175 SPARC galaxies with NFW_core (baryonic-feedback) model."""
from __future__ import annotations
import sys
import time
import json
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sparc_loader import load_all_sparc
from fit_t6_NFW_core import fit_one_NFW_core, RESULTS_DIR, DATA_DIR


def main():
    galaxies = load_all_sparc(DATA_DIR)
    print(f"[T6 batch] loaded {len(galaxies)} galaxies")

    summary = {
        "n_galaxies": len(galaxies),
        "profile": "NFW_core",
        "started_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "per_fit": {},
    }
    t_total = time.time()
    for i, g in enumerate(galaxies):
        t0 = time.time()
        try:
            res = fit_one_NFW_core(g.name)
            summary["per_fit"][g.name] = {
                "log_Z": res["log_Z"],
                "log_Z_err": res["log_Z_err"],
                "chi2_red": res["chi2_reduced_at_MAP"],
                "wall_seconds": res["wall_seconds"],
                "r_core_MAP_kpc": res["r_core_at_MAP_kpc"],
            }
            if i % 10 == 0:
                elapsed = time.time() - t_total
                est_remaining = elapsed * (len(galaxies) - i - 1) / max(i + 1, 1)
                print(f"[T6 batch] {i+1}/{len(galaxies)} ({g.name})  "
                      f"elapsed={elapsed:.0f}s  est_remaining={est_remaining:.0f}s")
        except Exception as e:
            print(f"[T6 batch] FAIL {g.name}: {e}")
            summary["per_fit"][g.name] = {"error": str(e)}

    log_zs = [v["log_Z"] for v in summary["per_fit"].values() if "log_Z" in v]
    summary["aggregate"] = {
        "n_ok": len(log_zs),
        "NFW_core_total_log_Z": float(np.sum(log_zs)),
        "median_log_Z": float(np.median(log_zs)),
    }
    summary["finished_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    summary["total_wall_seconds"] = float(time.time() - t_total)

    out = RESULTS_DIR / "t6_batch_summary.json"
    out.write_text(json.dumps(summary, indent=2))
    print(f"\n[T6 batch] DONE in {summary['total_wall_seconds']:.0f}s")
    print(f"[T6 batch] {len(log_zs)} fits OK")
    print(f"[T6 batch] sum log Z NFW_core = {summary['aggregate']['NFW_core_total_log_Z']:.1f}")
    print(f"[T6 batch] summary -> {out}")


if __name__ == "__main__":
    main()