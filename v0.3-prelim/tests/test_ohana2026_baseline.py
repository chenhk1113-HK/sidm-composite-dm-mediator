"""Regression test for the Ohana+ 2026 c-M joint likelihood (v19.1.5 baseline).

Per v40.38 self-verification framework: lock the v19.1.5 result as a regression
check. The script's honest verdict is "FAILED VALIDATION" (1.04 sigma vs
Ohana+ 3.2 sigma). If anyone tries to "fix" the script without proper
validation, this test catches accidental regressions to a worse state.

This test is NOT asserting the script is correct — it's asserting the script
hasn't silently drifted to a worse answer (e.g., posterior collapse, prior
bypass, NaN contamination).

Per R88(68) lesson (2026-10-17): "Grid-search 'breakthrough' retracted.
Anti-patterns: (1) double-counting same physics via two params, (2) contradicting
prior N-body, (3) unmotivated free functions, (4) overfitting."

Reference: v19.1.5 honest framing per re196.docx Reviewer 1 Issue 2 + r197.docx
version bump. Script: scripts/ohana2026_cloud9_joint_likelihood.py.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RESULTS = REPO / "v0.3-prelim" / "data" / "results" / "ohana2026_cloud9_joint_likelihood.json"


def test_ohana2026_baseline_present():
    """Lock file must exist and have the v19.1.5 structure."""
    assert RESULTS.exists(), f"Missing results file: {RESULTS}"
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    assert "concentration_mass_tension" in data, "Missing concentration_mass_tension in JSON"
    assert "posterior_summary" in data, "Missing posterior_summary in JSON"


def test_ohana2026_baseline_sigma_within_1sigma_of_v19_1_5():
    """Our posterior median sigma_below must remain within 1 sigma of v19.1.5 = 1.04.

    v19.1.5 produced 1.04 sigma (per the JSON, median 1.04, q16 0.44, q84 1.68).
    If the script is re-run and the result drifts >1 sigma, this test fails.
    Allowed drift: 0.04-2.04 sigma (within 1.0 of 1.04).

    This is the "regression test" component: lock the v19.1.5 state so any
    ACCIDENTAL drift (e.g., someone changes the prior, the gas proxy, or
    the MCMC config) is caught at test time, NOT silently shipped.
    """
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    median = data["concentration_mass_tension"]["median_sigma_below"]
    # v19.1.5 baseline is 1.04; allow ±1.0 sigma drift before failing.
    # Why so wide: the script has noise (MCMC random seed, walker count).
    # The point is to catch MAJOR changes (e.g., the prior gets dropped and
    # the posterior collapses to 0, or the prior gets pushed to a fixed value
    # and the posterior blows up). It is NOT to lock the exact value.
    assert 0.04 <= median <= 2.04, (
        f"v19.1.5 Ohana+ c-M posterior median drifted to {median:.2f} sigma, "
        f"expected 0.04-2.04 (v19.1.5 baseline = 1.04, allow ±1.0 drift). "
        f"CHECK: was the prior changed? was the gas proxy changed? was the "
        f"MCMC config changed? If yes deliberately, document in the note field."
    )


def test_ohana2026_published_in_68ci_unchanged():
    """The 'failed validation' verdict must remain 'NO (discrepancy)'.

    v19.1.5: published_in_68CI = False (Ohana+ 3.2 sigma outside our 68% CI).
    If a future change makes the script match Ohana+ by accident (e.g., hard-coding
    the answer), this test fails. That's a GOOD thing: matching 3.2 sigma by
    accident means the script is overfitting, not validating.
    """
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    in_68ci = data["concentration_mass_tension"]["published_in_68CI"]
    assert in_68ci is False, (
        f"published_in_68CI is now True, meaning the script claims to match "
        f"Ohana+ 3.2 sigma. THIS WOULD BE A RED FLAG (R88(68) overfitting risk). "
        f"Check the v19.1.5 honest 'failed validation' framing: per re196.docx, "
        f"the script is NOT a match. If a real match was achieved, that should "
        f"go through the full R88(71) BREAKTHROUGH checklist, not silent test fix."
    )


def test_ohana2026_posterior_summary_finite():
    """Posterior medians + 16/84 percentiles must all be finite and positive.

    Catches: NaN from divide-by-zero in the gas proxy, Inf from MCMC escape
    to parameter boundaries, negative concentrations from log-space conversion bugs.
    """
    import math
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    summary = data["posterior_summary"]
    for name, s in summary.items():
        for key in ("median", "q16", "q84", "mean"):
            v = s[key]
            assert math.isfinite(v), f"{name}.{key} = {v} is not finite"
        # All should be positive (M_200, c_200, tau are positive)
        assert s["median"] > 0, f"{name} median = {s['median']} should be positive"
        # q16 < median < q84 (posterior order)
        assert s["q16"] <= s["median"] <= s["q84"], (
            f"{name}: q16={s['q16']} median={s['median']} q84={s['q84']} not ordered"
        )


if __name__ == "__main__":
    # Allow running directly: python test_ohana2026_baseline.py
    for name in dir():
        if name.startswith("test_"):
            try:
                globals()[name]()
                print(f"  PASS  {name}")
            except AssertionError as e:
                print(f"  FAIL  {name}: {e}")
                sys.exit(1)
    print("All 4 Ohana+ 2026 baseline tests pass.")
