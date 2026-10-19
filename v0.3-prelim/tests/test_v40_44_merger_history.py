"""Regression test for v40.44 Silverman+ 2026 merger history analysis.

Per v40.44: Cloud-9's morphology (compact, non-rotating, dynamically cold,
no tidal features) suggests a QUIESCENT merger history. Per Silverman+ 2026,
quiescent halos (e.g., m10i with 6 mergers, no massive radial) undergo
gravothermal core collapse. v19.2-F's deep collapse prediction is
CONSISTENT with Silverman+ 2026. The c-M tension is NOT resolved.

This test locks the v40.44 finding so any future change that
misapplies the Silverman+ 2026 diagnostics (e.g., classifying
Cloud-9 as sustained-merger when its morphology is quiescent)
FAILS the test.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RESULTS = REPO / "v0.3-prelim" / "data" / "results" / "v19_2_f_cloud9_merger_history_2026_10_19.json"
SCRIPT = REPO / "scripts" / "v19_2_f_cloud9_merger_history.py"


def test_v40_44_results_present():
    """Lock file must exist and have the v40.44 structure."""
    assert RESULTS.exists(), f"Missing results file: {RESULTS}"
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    assert "cloud9_properties" in data
    assert "v19_2_f_prediction" in data
    assert "silverman_2026_halos" in data
    assert "verdict" in data


def test_v40_44_v19_2_f_predicts_deep_collapse():
    """v19.2-F canonical parameters must give tau >> 1 (deep collapse).

    This is the v40.44 starting point: v19.2-F predicts deep collapse
    for Cloud-9 (tau = 16.3 for f_H = 0.297).
    """
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    tau = data["v19_2_f_prediction"]["tau"]
    assert tau > 1.0, (
        f"v19.2-F tau = {tau:.2f}, expected > 1 (deep collapse). "
        f"If tau < 1, the v19.2-F deep collapse prediction is not "
        f"reproduced. Check the gravothermal parameters."
    )


def test_v40_44_cloud9_morphology_quiescent():
    """Cloud-9 must be classified as QUIESCENT merger history.

    Per Anand+ 2025: compact, non-rotating, dynamically cold (W50=12 km/s),
    no tidal features, RELHIC candidate. This is consistent with a
    quiescent merger history.
    """
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    cloud9 = data["cloud9_properties"]
    assert "quiescent" in cloud9["merger_history_inferred"], (
        f"Cloud-9 merger history = '{cloud9['merger_history_inferred']}', "
        f"expected to contain 'quiescent'. If classified as 'sustained', "
        f"the morphology-based inference is wrong."
    )
    assert "non-rotating" in cloud9["morphology"]
    assert cloud9["W50_kms"] < 20  # dynamically cold


def test_v40_44_silverman_quiescent_predicts_collapse():
    """Silverman+ 2026 must show quiescent halos collapse.

    The m10i case (6 mergers, no massive radial) collapsed in 5.2 Gyr.
    This is the diagnostic for Cloud-9 (also quiescent).
    """
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    halos = data["silverman_2026_halos"]
    # Find m10i (most quiescent)
    m10i = None
    for h in halos:
        if "m10i" in h["name"] and "most quiescent" in h["name"]:
            m10i = h
            break
    assert m10i is not None, "Could not find m10i (most quiescent) in Silverman+ 2026"
    assert "COLLAPSED" in m10i["outcome"].upper(), (
        f"m10i outcome = '{m10i['outcome']}', expected to contain COLLAPSED. "
        f"Silverman+ 2026 should show quiescent halos collapse."
    )


def test_v40_44_verdict_cM_tension_not_resolved():
    """The v40.44 verdict must confirm c-M tension is NOT resolved by
    Silverman+ 2026 merger mechanism.

    Per v40.44: Cloud-9's quiescent morphology means Silverman+ 2026
    ALSO predicts collapse. v19.2-F + Silverman+ 2026 are CONSISTENT
    in predicting deep collapse, but Ohana+ observes max-core.
    The c-M tension is NOT resolved.
    """
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    verdict = data["verdict"]
    assert verdict["c_M_tension_resolved_by_merger_reset"] is False, (
        f"verdict['c_M_tension_resolved_by_merger_reset'] = {verdict['c_M_tension_resolved_by_merger_reset']}, "
        f"expected False. If True, the v40.44 finding (c-M tension NOT "
        f"resolved) is not reproduced."
    )
    assert verdict["v40_41_structural_verdict_confirmed"] is True, (
        f"verdict['v40_41_structural_verdict_confirmed'] = {verdict['v40_41_structural_verdict_confirmed']}, "
        f"expected True. v40.44 CONFIRMS v40.41 STRUCTURAL verdict."
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
    print("All 5 v40.44 Silverman+ 2026 merger history tests pass.")
