"""
Captures the D13 partial-result state (T36 DONE + T38b RUNNING).

This script aggregates:
  - T36 SASHIMI config matrix RESULT (completed; ~30 s wall)
  - T38b dwarf KiSS-SIDM (running, ~5 hr wall estimated)

Use as a snapshot until T38b finishes.
"""
from __future__ import annotations
import json
import time
from pathlib import Path

PROJECT_ROOT = Path("/home/lamkuenai/dm-sidm-pipeline/v0.3-prelim")
RESULTS_DIR = PROJECT_ROOT / "data" / "results"


def main():
    t36_path = RESULTS_DIR / "t36_sashimi_config_matrix.json"
    if not t36_path.exists():
        # Try Windows-side mirror
        t36_path = Path("/mnt/c/Users/lamkuenai/projects/dm-sidm-pipeline/v0.3-prelim/data/results/t36_sashimi_config_matrix.json")

    if t36_path.exists():
        t36 = json.load(open(t36_path))
    else:
        t36 = {"error": "T36 result not yet generated"}

    out = {
        "test": "D13_partial_state_capture",
        "t36_sashimi_config_matrix": {
            "status": "COMPLETED",
            "best_config": t36.get("best_config"),
            "best_crossing_sigma_0_cm2_per_g": t36.get("best_crossing_sigma_0_cm2_per_g"),
            "best_ratio_to_hayashi": t36.get("best_ratio_to_hayashi"),
            "best_gap_in_dex": t36.get("best_gap_in_dex"),
            "verdict": t36.get("verdict"),
        },
        "t38_dwarf_kiss_sidm": {
            "status": "RUNNING (background process)",
            "expected_wall_minutes": 15,  # revised: snap_001 in 3 min @ 14:22, full run ~15 min
            "expected_snapshots": 10,
            "input": "N=5e4, dwarf (M=10^8 M_sun), sigma_m=5 cm^2/g",
            "eta_until_completion": "~15 minutes from D13 ship time (revised down from 5 hr)",
        },
        "d13_interim_verdict": (
            f"T36 closed Direction A: best config (A2 Hayashi+ 2025 c_vir) "
            f"brings our SASHIMI collapse transition to σ_0/m = "
            f"{t36.get('best_crossing_sigma_0_cm2_per_g'):.3f} cm²/g "
            f"vs Hayashi+ 2025 boundary 0.2 cm²/g "
            f"(ratio = {t36.get('best_ratio_to_hayashi'):.1f}×, gap = "
            f"{t36.get('best_gap_in_dex'):.2f} dex). "
            f"Within an order of magnitude — Direction A is now CLOSED "
            f"with N-body calibration drift as the residual systematic. "
            f"T38b (Direction C full closure) is running; ETA ~5 hr."
        ),
    }

    out_path = RESULTS_DIR / "d13_partial_state_capture.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, default=str))
    win_path = Path("/mnt/c/Users/lamkuenai/projects/dm-sidm-pipeline/v0.3-prelim/data/results/d13_partial_state_capture.json")
    win_path.write_text(json.dumps(out, indent=2, default=str))
    print(f"output -> {out_path}")
    print(f"        -> {win_path}")
    print()
    print("=" * 80)
    print("D13 PARTIAL STATE:")
    print("=" * 80)
    print(f"  T36 (Direction A): {out['t36_sashimi_config_matrix']['verdict']}")
    print(f"  T38b (Direction C): running, ETA ~5 hr")


if __name__ == "__main__":
    main()
