"""
load_standing_numbers.py — single source of truth for paper §2.5/§2.6/§2.7.

Usage:
    from load_standing_numbers import load
    sn = load()
    print(sn["section_2_7"]["check_1_ohana"]["tension_at_fiducial_sigma"])

If you change v0.3-prelim/data/standing_numbers.json, this module reads it
on import. Drift between paper text + JSON + script is the upstream
verification gap that produced the 11-bundle loop. If you change a
number, change it HERE, not in PAPER_V1_DRAFT.md.
"""
import json
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_PATH = _REPO_ROOT / "v0.3-prelim" / "data" / "standing_numbers.json"


def load(path=None):
    p = Path(path) if path else _DEFAULT_PATH
    with open(p) as f:
        return json.load(f)


def check_drift(sn=None):
    """Verify that the standing-numbers JSON agrees with v192_* JSON outputs.

    Returns a list of (key, expected, actual) tuples for any disagreement.
    An empty list means no drift.
    """
    import json
    from pathlib import Path

    if sn is None:
        sn = load()

    drift = []

    # v192_b — Ohana+ tension at fiducial
    b_path = _REPO_ROOT / "v0.3-prelim" / "data" / "results" / "v192_b_ohana3p2sigma_reproduction.json"
    if b_path.exists():
        with open(b_path) as f:
            v192b = json.load(f)
        expected_tau = sn["section_2_7"]["check_1_ohana"]["tension_at_fiducial_sigma"]
        actual_tau = v192b["tension_at_fiducial"]["tension_sigma"]
        if abs(expected_tau - round(actual_tau, 2)) > 0.01:
            drift.append(("section_2_7.check_1_ohana.tension_at_fiducial_sigma",
                          expected_tau, actual_tau))

    # v192_c — Concerto rc1 median
    c_path = _REPO_ROOT / "v0.3-prelim" / "data" / "results" / "v192_c_concerto_subhalo_cloud9.json"
    if c_path.exists():
        with open(c_path) as f:
            v192c = json.load(f)
        expected_rc = sn["section_2_7"]["check_2_concerto"]["concerto_rc1_median_kpc"]
        actual_rc = v192c["concerto_subhalo_stats_cloud9_mass"]["rc1_median_kpc"]
        if abs(expected_rc - round(actual_rc, 2)) > 0.01:
            drift.append(("section_2_7.check_2_concerto.concerto_rc1_median_kpc",
                          expected_rc, actual_rc))

    return drift


if __name__ == "__main__":
    import sys
    drift = check_drift()
    if drift:
        print(f"DRIFT DETECTED in {len(drift)} field(s):")
        for key, expected, actual in drift:
            print(f"  {key}: expected {expected}, actual {actual}")
        sys.exit(1)
    print("No drift between standing_numbers.json and v192_* JSON outputs.")