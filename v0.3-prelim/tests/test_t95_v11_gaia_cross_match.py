"""
Tests for t95_v11_gaia_cross_match + t95_v11_gaia_apply.

These tests are smoke-level: they verify the pipeline runs end-to-end,
the classification logic is sound, and the results file is well-formed.
They do NOT make new TAP queries (those depend on network + ESA server
state) — they validate that the existing results JSON can be classified
and applied.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))

# Path to the cached results
_RESULTS_PATH = (Path(__file__).resolve().parents[1] / "outputs" /
                 "t95" / "t95_v11_cross_match_results.json")


def _skip_if_no_results():
    if not _RESULTS_PATH.exists():
        pytest.skip(f"No results JSON at {_RESULTS_PATH}; run "
                    "t95_v11_gaia_cross_match.py first")


def test_results_json_exists_and_valid():
    """The cross-match results JSON must exist and parse cleanly."""
    _skip_if_no_results()
    with _RESULTS_PATH.open() as f:
        results = json.load(f)
    assert isinstance(results, list)
    assert len(results) == 13
    for r in results:
        assert "stream" in r
        assert "status" in r


def test_classify_identifies_rescued_streams():
    """classify() should put streams with v_3d < 700 km/s AND n >= 10 in 'rescued'."""
    _skip_if_no_results()
    from t95_v11_gaia_apply import classify, load_cross_match
    results = load_cross_match()
    classification = classify(results)
    # NGC6362 should always be rescued (d=7.6 kpc, Gaia data is excellent)
    assert "NGC6362" in classification["rescued"]
    # Eridanus should always be outlier (d=95 kpc, no Gaia data)
    assert any(s == "Eridanus" for s, _, _ in classification["outliers"])


def test_rescued_count_at_least_three():
    """At least 3 streams should be rescueable from Gaia DR3 alone."""
    _skip_if_no_results()
    from t95_v11_gaia_apply import classify, load_cross_match
    results = load_cross_match()
    classification = classify(results)
    assert len(classification["rescued"]) >= 3, \
        f"Only {len(classification['rescued'])} rescued; expected >= 3"


def test_build_constraints_tighter_than_synthesized():
    """Rescued constraints should use factor-3 boxes (tighter than factor-5 synthesized)."""
    _skip_if_no_results()
    from t95_v11_gaia_apply import classify, load_cross_match, build_constraints
    results = load_cross_match()
    classification = classify(results)
    constraints = build_constraints(classification["rescued"])
    for s, c in constraints.items():
        ratio = c["sigma_m_upper"] / c["sigma_m_lower"]
        assert 8.5 < ratio < 9.5, f"{s}: ratio {ratio} should be 3*3=9 ± small drift"


def test_main_runs_without_error():
    """t95_v11_gaia_apply.main() should run end-to-end and write output."""
    _skip_if_no_results()
    from t95_v11_gaia_apply import main
    rc = main()
    assert rc == 0
    out_path = (Path(__file__).resolve().parents[1] / "outputs" /
                "t95" / "t95_v11_apply_results.json")
    assert out_path.exists()
    with out_path.open() as f:
        summary = json.load(f)
    assert "n_rescued" in summary
    assert "delta_loglik" in summary


def test_no_v3d_above_700_in_rescued():
    """Rescued streams should have v_3d < 700 km/s (within MW escape velocity)."""
    _skip_if_no_results()
    from t95_v11_gaia_apply import classify, load_cross_match
    results = load_cross_match()
    classification = classify(results)
    for s, info in classification["rescued"].items():
        assert info["v_kms"] < 700, f"{s} rescued but v_3d={info['v_kms']} > 700"


def test_rescued_n_members_at_least_10():
    """Rescued streams should have at least 10 member-selected Gaia stars."""
    _skip_if_no_results()
    from t95_v11_gaia_apply import classify, load_cross_match
    results = load_cross_match()
    classification = classify(results)
    for s, info in classification["rescued"].items():
        assert info["n_members"] >= 10, \
            f"{s} rescued but n_members={info['n_members']} < 10"


def test_get_stream_center_works_for_alpheus():
    """get_stream_center should return sensible values for Alpheus."""
    from t95_v11_gaia_cross_match import get_stream_center
    center = get_stream_center("Alpheus")
    assert center is not None
    assert 0 < center["ra_center_deg"] < 360
    assert -90 < center["dec_center_deg"] < 90
    assert center["distance_kpc"] > 0
