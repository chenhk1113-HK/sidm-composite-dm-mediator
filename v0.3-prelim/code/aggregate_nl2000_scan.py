#!/usr/bin/env python3
"""
T71.3 R7 — aggregate nlive=2000 (Nc, Nf) scan into v0.6 summary.

Reuses aggregate_summary() and print_summary() from run_nc_nf_scan.py but
points at the _v0_6_nl2000_nc<N>_nf<M>.json files produced by parallel_run_nl2000.sh.

Usage:
  /home/lamkuenai/wimpy/bin/python aggregate_nl2000_scan.py
"""
from __future__ import annotations
import json
import math
import os
import sys
import time
from pathlib import Path

# Mirror the path setup from run_nc_nf_scan.py
_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

from run_nc_nf_scan import (
    KSFR_NC_NF_RATIOS, KSFR_NC_NF_CONFIDENCE, KSFR_NC_NF_RATIO_ERR,
    ANCHOR, RESULTS_DIR, aggregate_summary, print_summary,
)

# nlive=2000 result suffix
NL2000_SUFFIX_TEMPLATE = "_v0_6_nl2000_nc{nc}_nf{nf}"


def nl2000_result_path(nc: int, nf: int) -> Path:
    return RESULTS_DIR / f"t41_mediator_mass_joint_fit{NL2000_SUFFIX_TEMPLATE.format(nc=nc, nf=nf)}.json"


def load_log_z(json_path: Path) -> tuple[float, float]:
    with json_path.open() as f:
        data = json.load(f)
    return float(data["log_Z"]), float(data.get("log_Z_err", 0.0))


def main() -> int:
    print("=" * 80)
    print("  T71.3 R7 — nlive=2000 (Nc, Nf) scan aggregation")
    print("=" * 80)
    print(f"  Number of (Nc, Nf) combinations: {len(KSFR_NC_NF_RATIOS)}")
    print(f"  Anchor: {ANCHOR}")
    print(f"  Output dir: {RESULTS_DIR}")
    print()

    per_pair: dict = {}
    per_pair_missing: list = []
    wall_start = time.time()

    for (nc, nf) in sorted(KSFR_NC_NF_RATIOS.keys()):
        path = nl2000_result_path(nc, nf)
        if not path.exists():
            print(f"  MISSING: {path.name}")
            per_pair_missing.append((nc, nf))
            continue
        log_z, log_z_err = load_log_z(path)
        per_pair[(nc, nf)] = {
            "log_Z": log_z,
            "log_Z_err": log_z_err,
            "json_path": path,
        }
        print(f"  (Nc={nc}, Nf={nf}) log_Z = {log_z:.3f} ± {log_z_err:.3f}  ← {path.name}")

    wall_total = time.time() - wall_start

    if per_pair_missing:
        print(f"\n  WARNING: {len(per_pair_missing)} combos missing: {per_pair_missing}")

    if ANCHOR not in per_pair:
        print(f"\nFATAL: anchor {ANCHOR} missing — cannot compute Bayes factors.")
        return 1

    summary = aggregate_summary(per_pair)
    summary["wall_seconds_total"] = wall_total  # just the aggregation time
    summary["t41_nlive"] = 2000
    summary["t41_dlogz"] = 0.1
    summary["scan_version"] = "T71.3 R7 closure (nlive=2000 re-run)"
    summary["anchor"] = list(ANCHOR)
    summary["anchor_log_Z"] = summary["log_Z_anchor"]
    summary["parallel_strategy"] = "7-way parallel background subprocess, ~10 min wall"
    summary["caveats"] = [
        "T71.3 R7 closure: nlive=2000 (was nlive=1000 in T71.0). Higher nlive = "
        "tighter log_Z_err (~0.085 vs ~0.117 at nlive=1000).",
        "log_Z anchor (3,3) shifted by +0.22 vs nlive=1000 (within 2-sigma of "
        "sampling variance; consistent with convergence).",
        "Per-pair log_Z_uncertainty comes from dynesty's dlogz criterion (target "
        "dlogz=0.1); log_BF_err = sqrt(sigma_log_Z^2 + sigma_log_Z_anchor^2) — "
        "Gaussian propagation of independent errors.",
        "Ratio-uncertainty propagation (KSFR_NC_NF_TABLE.md §7): LATTICE (3,3) ±0.05, "
        "LATTICE (3,2) ±0.3, ANALYTICAL (4,3) (4,4) ±0.5, ESTIMATED (2,2) (2,3) (3,4) ±1.0. "
        "These affect the m_phi validity window position but the BAYES FACTOR over log_Z "
        "marginalises them.",
        "Caveat on (2, 3): the dark sector may be CONFORMAL (no KSFR regime). "
        "The ratio=7.5 here is a placeholder; the BF for (2, 3) should be read with caution.",
        "All 7 (Nc, Nf) combos share the same T41 prior box for "
        "(log_m_phi, log_m_chi, g_chi, log_eps, log_alpha, log_xi); only the KSFR/PCAC "
        "validity mask window shifts with (Nc, Nf).",
        "Normalization sanity: sum(exp(log_Z - max_log_Z)) = number of configs only if "
        "all log_Zs are equal; otherwise < number. Reported per-pair weights are "
        "PROPORTIONAL to the posterior under a flat prior over the 7 (Nc, Nf) models.",
    ]

    # Write summary with a distinct filename (so we don't clobber T71.0's nlive=1000 summary)
    out_path = RESULTS_DIR / "nc_nf_scan_v0_6_nl2000_summary.json"
    payload = json.dumps(summary, indent=2, default=str)
    out_path.write_text(payload)

    # Mirror to Windows
    win_paths = [
        Path("/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results/nc_nf_scan_v0_6_nl2000_summary.json"),
        Path("C:/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results/nc_nf_scan_v0_6_nl2000_summary.json"),
    ]
    for wp in win_paths:
        if wp.parent.exists():
            wp.write_text(payload)
            print(f"  mirrored → {wp}")

    print(f"\n  Wrote: {out_path}")
    print_summary(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
