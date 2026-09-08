"""
Tests for t95_v14_chemodynamic_gmm + t95_v14_chemodynamic_apply.

T95.14 adds a [Fe/H] prior from DESI to the GMM stream-member selection.
For Parallel and Perpendicular (the only 2 streams with DESI coverage),
this reduces the v_3d estimates from >700 km/s (outlier) to <500 km/s
(rescued), and folds them into the joint fit.

T104 AUDIT FIX (regression test): the apply script used to filter out
streams not in the T95.11 rescued list, so Perpendicular (which was a
T95.11 outlier) was never counted. After the fix, both Parallel AND
Perpendicular are in the n_rescued_total count.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
import pytest

_RESULTS_PATH = (Path(__file__).resolve().parents[1] / "outputs" /
                 "t95" / "t95_v14_chemodynamic_results.json")
_APPLY_PATH = (Path(__file__).resolve().parents[1] / "outputs" /
               "t95" / "t95_v14_chemodynamic_apply_results.json")


def _skip_if_no_results():
    if not _RESULTS_PATH.exists():
        pytest.skip("No chemodynamic results JSON; run t95_v14_chemodynamic_gmm.py")


def test_results_json_exists_and_valid():
    _skip_if_no_results()
    with _RESULTS_PATH.open() as f:
        results = json.load(f)
    assert isinstance(results, list)
    assert len(results) == 2
    assert {r["stream"] for r in results} == {"Parallel", "Perpendicular"}


def test_both_streams_status_ok():
    _skip_if_no_results()
    with _RESULTS_PATH.open() as f:
        results = json.load(f)
    for r in results:
        assert r["status"] == "ok", f"{r['stream']}: {r.get('error')}"
        assert r["n_metal_poor"] > 0
        assert r["feh_cut"] == -0.5


def test_v_3d_below_700_kms_threshold():
    """Both streams should now pass the 700 km/s outlier filter."""
    _skip_if_no_results()
    with _RESULTS_PATH.open() as f:
        results = json.load(f)
    for r in results:
        assert r["v_3d_rescued_kms"] < 700, \
            f"{r['stream']}: v_3d={r['v_3d_rescued_kms']} still > 700"
        assert r["v_3d_rescued_kms"] > 0


def test_feh_tags_present():
    """[Fe/H] median should be present and halo-like (<-0.5)."""
    _skip_if_no_results()
    with _RESULTS_PATH.open() as f:
        results = json.load(f)
    for r in results:
        assert r["feh_median"] is not None
        assert r["feh_median"] < -0.5, \
            f"{r['stream']}: [Fe/H]={r['feh_median']} not halo-like"


def test_v_3d_improved_over_t95_11():
    """v_3d should be lower than T95.11 estimates (which were outliers)."""
    _skip_if_no_results()
    t95_11 = json.load(open(Path(__file__).resolve().parents[1] / "outputs" /
                            "t95" / "t95_v11_cross_match_results.json"))
    with _RESULTS_PATH.open() as f:
        t95_14 = json.load(f)
    for r in t95_14:
        t11 = next((x for x in t95_11 if x["stream"] == r["stream"]), None)
        if t11 and t11.get("v_3d_rescued_kms", 0) >= 700:
            assert r["v_3d_rescued_kms"] < t11["v_3d_rescued_kms"], \
                f"{r['stream']}: T95.14 should improve over T95.11"


def test_apply_results_present():
    if not _APPLY_PATH.exists():
        pytest.skip("No apply results JSON; run t95_v14_chemodynamic_apply.py")
    with _APPLY_PATH.open() as f:
        out = json.load(f)
    assert out["n_overrides"] == 2
    assert out["t95_14_joint_loglik"] == 0.0
    assert abs(out["delta_loglik"] - 12.038) < 0.001


def test_apply_perpendicular_counted_in_rescued_total():
    """T104 regression test: Perpendicular must be counted in n_rescued_total.

    Before the T104 audit fix, the apply script filtered out streams not in
    the T95.11 rescued list, so Perpendicular (which was a T95.11 outlier)
    was never counted. After the fix, both Parallel AND Perpendicular are
    in the n_rescued_total count.
    """
    if not _APPLY_PATH.exists():
        pytest.skip("No apply results JSON; run t95_v14_chemodynamic_apply.py")
    with _APPLY_PATH.open() as f:
        out = json.load(f)
    # After the T104 fix: 6 (T95.11) + 2 (T95.14: Parallel + Perpendicular) = 8
    assert out["n_rescued_total"] == 8, (
        f"T104 audit fix: expected n_rescued_total=8, got {out['n_rescued_total']}. "
        "Perpendicular must be counted in the joint fit (it was a T95.11 outlier "
        "but the T95.14 GMM fit it successfully)."
    )


def test_apply_perpendicular_in_newly_rescued_per_stream():
    """T104 regression test: Perpendicular must appear in newly_rescued_per_stream.

    Both Parallel AND Perpendicular are reported as newly-rescued with
    full kinematic data (v_3d, vrad, [Fe/H]).
    """
    if not _APPLY_PATH.exists():
        pytest.skip("No apply results JSON; run t95_v14_chemodynamic_apply.py")
    with _APPLY_PATH.open() as f:
        out = json.load(f)
    per_stream_names = [r["stream"] for r in out["newly_rescued_per_stream"]]
    assert "Parallel" in per_stream_names, "Parallel missing from newly_rescued_per_stream"
    assert "Perpendicular" in per_stream_names, (
        "T104 audit fix: Perpendicular missing from newly_rescued_per_stream. "
        "The apply script must report Perpendicular's kinematic data."
    )


def test_pmgm_module_importable():
    """Module imports without error."""
    import warnings
    warnings.filterwarnings("ignore")
    import t95_v14_chemodynamic_gmm  # noqa: F401
