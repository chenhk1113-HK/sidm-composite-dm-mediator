"""
T90.23 dry-run orchestrator -- runs paths 1-4 in sequence.

Each path is in dry-run mode by default (no data download). Set
T90_V23_DOWNLOAD=1 in the environment to enable auto-download.

Usage:
    python v0.3-prelim/code/t90_v23_dry_run_all.py
    T90_V23_DOWNLOAD=1 python v0.3-prelim/code/t90_v23_dry_run_all.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_PROJECT_ROOT / "code"))


def main():
    print("#" * 70)
    print("T90.23 dry-run orchestrator: paths 1-4")
    print("#" * 70)
    print()

    # Path 1: LZ low-E count
    print("=" * 70)
    print("Path 1: LZ low-E_R window count")
    print("=" * 70)
    import t90_v23_lz_evt_in_lowE_window as p1
    p1.main()
    print()

    # Path 2: PandaX high-E count
    print("=" * 70)
    print("Path 2: PandaX-4T high-E_R count")
    print("=" * 70)
    import t90_v23_pandax_highE_count as p2
    p2.main()
    print()

    # Path 3: XENONnT S2-only
    print("=" * 70)
    print("Path 3: XENONnT S2-only")
    print("=" * 70)
    import t90_v23_xenonnt_s2only_highE as p3
    p3.main()
    print()

    # Path 4: Joint likelihood (always runs, even if paths 1-3 are dry)
    print("=" * 70)
    print("Path 4: Joint three-detector likelihood")
    print("=" * 70)
    import t90_v23_joint_three_detector_likelihood as p4
    p4.main()
    print()

    print("#" * 70)
    print("Done. Output JSONs at outputs/t90/t90_v23_*.json")
    print("#" * 70)


if __name__ == "__main__":
    main()
