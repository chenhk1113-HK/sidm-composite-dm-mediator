"""Regression tests for v40.50 paper section 2.1 update.

Per v40.49 multi-scale refit: 10/14 combinations pass all 9 multi-scale
channels. MW satellite v=10 is the binding constraint (only 10/14 pass).

v40.50 implementation: generated the paper section 2.1 update text from
the v40.49 result file. This test locks the v40.49 numbers so any future
change to the multi-scale refit that affects these numbers FAILS the
test until the paper update is regenerated.

Reference:
- scripts/v19_2_f_paper_section_2_1_update.py
- v0.3-prelim/data/results/v19_2_f_multiscale_refit_2026_10_19.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RESULTS = REPO / "v0.3-prelim" / "data" / "results" / "v19_2_f_multiscale_refit_2026_10_19.json"
SCRIPT = REPO / "scripts" / "v19_2_f_paper_section_2_1_update.py"


def test_v40_50_v40_49_results_present():
    """Lock file must exist and have the v40.49 structure."""
    assert RESULTS.exists(), f"Missing v40.49 results file: {RESULTS}"
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    assert "n_all_pass" in data
    assert "n_per_channel" in data
    assert "results" in data


def test_v40_50_n_all_pass_is_10():
    """n_all_pass must be exactly 10 (10/14 = 71% survival)."""
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    assert data["n_all_pass"] == 10, (
        f"n_all_pass = {data['n_all_pass']}, expected 10. "
        f"If this changed, the v40.50 paper section 2.1 update must be regenerated."
    )


def test_v40_50_mw_v10_is_binding():
    """MW satellite v=10 must be the binding constraint (10/14 pass)."""
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    n_per = data["n_per_channel"]
    min_channel = min(n_per, key=n_per.get)
    assert min_channel == "mw_sat_10", (
        f"Binding constraint = {min_channel}, expected 'mw_sat_10'. "
        f"If changed, the v40.50 paper section 2.1 must be regenerated."
    )
    assert n_per["mw_sat_10"] == 10, (
        f"MW v=10 pass = {n_per['mw_sat_10']}, expected 10. "
        f"If changed, the v40.50 paper section 2.1 must be regenerated."
    )


def test_v40_50_bullet_cluster_passes_all():
    """Bullet Cluster is the easiest channel (14/14 pass)."""
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    assert data["n_per_channel"]["bullet_cluster"] == 14, (
        f"Bullet Cluster pass = {data['n_per_channel']['bullet_cluster']}, "
        f"expected 14. If changed, the v40.50 paper section 2.1 must be regenerated."
    )


def test_v40_50_passing_region_in_range():
    """The passing region must be a RANGE, not a single point (per Nemotron
    v40.48 recommendation: 'Show PASSING REGION, not single best triple').

    Check: at least 2 distinct sigma_0 values, 2 distinct a values, 2 distinct
    v_ref values among the 10 passing combinations.
    """
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    passing = [r["combo"] for r in data["results"] if r["all_pass"]]
    sigma_0s = set(round(c["sigma_0"], 3) for c in passing)
    a_slopes = set(round(c["a_slope"], 2) for c in passing)
    v_refs = set(round(c["v_ref"], 1) for c in passing)
    assert len(sigma_0s) >= 2, (
        f"Passing region has only {len(sigma_0s)} distinct sigma_0 values. "
        f"Per Nemotron: 'Show PASSING REGION, not single best triple'."
    )
    assert len(a_slopes) >= 2, (
        f"Passing region has only {len(a_slopes)} distinct a_slope values. "
        f"Per Nemotron: 'Show PASSING REGION, not single best triple'."
    )
    assert len(v_refs) >= 2, (
        f"Passing region has only {len(v_refs)} distinct v_ref values. "
        f"Per Nemotron: 'Show PASSING REGION, not single best triple'."
    )


if __name__ == "__main__":
    for name in dir():
        if name.startswith("test_"):
            try:
                globals()[name]()
                print(f"  PASS  {name}")
            except AssertionError as e:
                print(f"  FAIL  {name}: {e}")
                sys.exit(1)
    print("All 5 v40.50 paper section 2.1 update regression tests pass.")
