"""
D14 parallel-sessions state capture.

Three parallel work items shipped in D14:

  1. BG-1 (T38c, launched 18:17 HKT): dwarf KiSS-SIDM N=2e6 full run.
     Paper-canonical resolution. Estimated ~46 hr wall, but first snapshot
     produced in ~1 min (so the rate is ~7 min/snapshot — 10 snapshots
     in ~70 min, NOT 46 hr). T38c is running detached; use t38c_poll_status.py
     to monitor. NOT EXPECTED TO FINISH WITHIN THIS SESSION.

  2. FG-1 (Tier-1 hygiene): sync_to_wsl.sh + sync_to_win.sh helpers.
     Prevents future WSL/Windows mirror drift (the failure mode that
     caused the D11 env recovery). Idempotent. Tested.

  3. FG-2 (Tier-3 prep): tier3_epsilon_alpha_sketch.py — structural sketch
     for the unfixed TIER-3 KEY LESSON (T30/T32 catastrophic exclusions).
     Documented phases A-E (5-6 hr total) for the actual implementation.
     NOT a full fit; sketch only.
"""
from __future__ import annotations
import json
from pathlib import Path
import time

PROJECT_ROOT = Path("/home/lamkuenai/dm-sidm-pipeline/v0.3-prelim")
RESULTS_DIR = PROJECT_ROOT / "data" / "results"


def main():
    out = {
        "test": "D14_parallel_sessions_state",
        "sessions_in_parallel": [
            {
                "id": "BG-1",
                "name": "T38c dwarf KiSS-SIDM N=2e6",
                "kind": "background process",
                "launch_status_path": str(RESULTS_DIR / "t38c_launch_status.json"),
                "poll_status_path": str(PROJECT_ROOT / "code" / "t38c_poll_status.py"),
                "log_path": "/tmp/kiss_t38c.log",
                "expected_total_wall_minutes": 70,
                "expected_status_at_D14_ship": "~3/10 snapshots produced; running detached",
            },
            {
                "id": "FG-1",
                "name": "sync_to_wsl.sh + sync_to_win.sh",
                "kind": "synchronous (delivered)",
                "files": [
                    "sync_to_wsl.sh",
                    "sync_to_win.sh",
                ],
                "use_case": "Run after every code change to keep WSL/Windows mirror in sync.",
                "tested": True,
            },
            {
                "id": "FG-2",
                "name": "tier3_epsilon_alpha_marginalization_sketch",
                "kind": "synchronous sketch (delivered)",
                "files": [
                    "v0.3-prelim/code/tier3_epsilon_alpha_sketch.py",
                    "v0.3-prelim/data/results/tier3_epsilon_alpha_sketch.json",
                ],
                "use_case": "Resolves the TIER-3 KEY LESSON (T30/T32 catastrophic exclusions).",
                "implementation_phases": "A (30 min): read T30 + T32 likelihoods, "
                                          "identify coupling hardcodes. B (2 hr): "
                                          "refactor likelihoods. C (30 min): update fit "
                                          "scripts. D (1 hr): run dynesty. E (1 hr): ship. "
                                          "Total: ~5-6 hr.",
            },
        ],
        "d14_state_at_unix_seconds": int(time.time()),
        "next_actions": [
            "t38c_poll_status.py periodically to monitor BG-1 progress.",
            "sync_to_wsl.sh after every future code change to prevent mirror drift.",
            "Tier-3 implementation: kick off Phases A-E in a future session if Tier-3 is the priority.",
        ],
    }

    out_path = RESULTS_DIR / "d14_parallel_sessions_state.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, default=str))
    print(out_path)


if __name__ == "__main__":
    main()