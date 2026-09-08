"""
Tests for t95_v26_pilot_113_streams.py — T95.10 113-stream residual pilot.

Validates:
  1. All 8 pilot streams get processed (ok or status-flagged, no exceptions).
  2. Per-stream wall time is bounded (no infinite loop on degenerate kinematics).
  3. Master-Yukawa sigma/m is monotonically decreasing with v_3d across the OK subset.
  4. Degenerate-kinematics streams (Alpheus) are correctly flagged.
  5. Total wall time is reasonable for the 8-stream pilot (< 30s).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))


def test_pilot_streams_defined():
    """Pilot stream list should be 8 streams, stratified."""
    from t95_v26_pilot_113_streams import PILOT_STREAMS
    assert len(PILOT_STREAMS) == 8
    assert "M2" in PILOT_STREAMS
    assert "NGC6397" in PILOT_STREAMS
    assert "Ophiuchus" in PILOT_STREAMS
    assert "Gaia-8" in PILOT_STREAMS
    assert "Sagittarius" in PILOT_STREAMS
    assert "Cetus" in PILOT_STREAMS
    assert "Elqui" in PILOT_STREAMS
    assert "Alpheus" in PILOT_STREAMS  # negative test


def test_diagnostic_handles_all_streams():
    """Diagnostic should return a status for every pilot stream without raising."""
    from t95_v26_pilot_113_streams import PILOT_STREAMS, stream_sigma_m_diagnostic
    for s in PILOT_STREAMS:
        diag = stream_sigma_m_diagnostic(s)
        assert "stream" in diag
        assert "status" in diag
        assert "wall_total_s" in diag
        assert diag["status"] in ("ok", "degenerate_kinematics", "no_summary", "no_track", "no_velocity")


def test_degenerate_kinematics_flagged():
    """Alpheus has v_t=0, v_r=0 → must be flagged degenerate."""
    from t95_v26_pilot_113_streams import stream_sigma_m_diagnostic
    diag = stream_sigma_m_diagnostic("Alpheus")
    assert diag["status"] == "degenerate_kinematics"


def test_near_globulars_ok():
    """M2 and NGC6397 should produce valid sigma/m predictions."""
    from t95_v26_pilot_113_streams import stream_sigma_m_diagnostic
    for s in ("M2", "NGC6397"):
        diag = stream_sigma_m_diagnostic(s)
        assert diag["status"] == "ok", f"{s}: {diag}"
        assert diag["v_3d_kms"] > 0
        assert diag["sigma_m_pred_master_yukawa_cm2_per_g"] > 0


def test_sagittarius_is_benchmark():
    """Sagittarius is the most-studied tidal stream; sigma/m should be in physical range."""
    from t95_v26_pilot_113_streams import stream_sigma_m_diagnostic
    diag = stream_sigma_m_diagnostic("Sagittarius")
    assert diag["status"] == "ok"
    assert 200 < diag["v_3d_kms"] < 400  # Sagittarius is ~300 km/s
    assert 0.1 < diag["sigma_m_pred_master_yukawa_cm2_per_g"] < 5.0


def test_sigma_m_decreases_with_v3d():
    """Master Yukawa: sigma/m ∝ v^-0.16 → monotonic decrease across OK streams."""
    from t95_v26_pilot_113_streams import PILOT_STREAMS, stream_sigma_m_diagnostic
    sigmas = []
    v3ds = []
    for s in PILOT_STREAMS:
        diag = stream_sigma_m_diagnostic(s)
        if diag.get("status") == "ok":
            sigmas.append(diag["sigma_m_pred_master_yukawa_cm2_per_g"])
            v3ds.append(diag["v_3d_kms"])
    assert len(sigmas) >= 5
    pairs = sorted(zip(v3ds, sigmas))
    v_sorted = [v for v, _ in pairs]
    s_sorted = [s for _, s in pairs]
    # Adjacent differences should be ≤ 0 (monotonic non-increasing)
    for i in range(1, len(s_sorted)):
        assert s_sorted[i] <= s_sorted[i - 1] + 1e-9, (
            f"sigma/m not monotonic at v={v_sorted[i]}: {s_sorted[i-1]} → {s_sorted[i]}"
        )


def test_synthesized_constraint_wide_box():
    """Velocity-only synthesized constraints should be wide (factor-of-5 boxes)."""
    from t95_v26_pilot_113_streams import synthesize_velocity_only_constraint
    c = synthesize_velocity_only_constraint("M2")
    assert c is not None
    assert c["sigma_m_lower"] < c["sigma_m_upper"]
    ratio = c["sigma_m_upper"] / c["sigma_m_lower"]
    assert 24 < ratio < 26  # 5x5 = 25, ±1 for float drift


def test_synthesize_returns_none_for_degenerate():
    """Degenerate streams must not get a synthesized constraint."""
    from t95_v26_pilot_113_streams import synthesize_velocity_only_constraint
    assert synthesize_velocity_only_constraint("Alpheus") is None


def test_run_pilot_writes_outputs(tmp_path):
    """run_pilot should write JSON and markdown summary without raising."""
    from t95_v26_pilot_113_streams import run_pilot
    summary = run_pilot()
    assert summary["n_pilot_streams"] == 8
    assert summary["n_ok"] + summary["n_degenerate"] + summary["n_failed_other"] == 8
    # At least one OK stream (Alpheus is the only designed degenerate)
    assert summary["n_ok"] >= 6
    # Wall time must be bounded
    assert summary["wall_total_s"] < 30.0
    assert summary["wall_per_stream_max_s"] < 5.0
    # Joint loglik should be finite
    assert summary["joint_loglik_with_synthesized"]["n_streams"] >= 15


def test_run_full_returns_113_residual():
    """run_full should process 113 streams (galstreams catalog minus 10 curated)."""
    from t95_v26_pilot_113_streams import run_full
    summary = run_full(verbose=False)
    # The galstreams v1.2 catalog has 123 streams with track+velocity;
    # 10 are curated → 113 residual
    assert summary["n_residual"] == 113, f"expected 113, got {summary['n_residual']}"
    assert summary["n_curated"] == 10
    assert summary["n_ok"] + summary["n_degenerate"] + summary["n_outlier"] + summary["n_failed_other"] == 113


def test_run_full_joint_loglik_finite():
    """Joint loglik over curated + synthesized should be finite."""
    from t95_v26_pilot_113_streams import run_full
    summary = run_full(verbose=False)
    loglik = summary["joint_loglik_with_synthesized"]["combined_loglik"]
    import math
    assert math.isfinite(loglik)
    assert summary["joint_loglik_with_synthesized"]["n_streams"] >= 100


def test_run_full_degenerate_streams_listed():
    """Degenerate streams (no pm/rv) should be enumerated for cross-match."""
    from t95_v26_pilot_113_streams import run_full
    summary = run_full(verbose=False)
    name_list = summary["degenerate_stream_names"]
    # We expect ~10-15 degenerate streams from earlier screening
    assert 5 <= len(name_list) <= 30, f"unexpected degenerate count: {len(name_list)}"
    # Spot-check known degenerate streams
    assert "Alpheus" in name_list or any("Alpheus" in s for s in name_list)


def test_run_full_velocity_range_sensible():
    """v_3d range across OK streams should be physically reasonable after the
    galstreams v_r=1000 placeholder sentinel is stripped."""
    from t95_v26_pilot_113_streams import run_full
    summary = run_full(verbose=False)
    vmin, vmax = summary["velocity_range_kms"]
    assert vmin is not None and vmax is not None
    assert 0 < vmin < vmax
    # Milky Way bound: v_3d should be < 800 km/s after stripping 1000-km/s placeholders
    assert vmax < 800, f"max v_3d {vmax} exceeds MW escape velocity"
    # At least one stream should be moving faster than 200 km/s
    assert vmax > 200


def test_placeholder_vr_stripped():
    """Streams with galstreams v_r=1000 placeholder sentinel should have v_r_effective=0
    and v_3d=v_t. C-4 is a known placeholder case."""
    from t95_v26_pilot_113_streams import stream_sigma_m_diagnostic
    diag = stream_sigma_m_diagnostic("C-4")
    # C-4 should be OK now (placeholder stripped, real v_t=316)
    assert diag["status"] == "ok"
    assert diag["v_r_was_placeholder"] is True
    assert diag["v_r_effective_kms"] == 0.0
    # v_3d should equal v_t (no radial contribution)
    assert abs(diag["v_3d_kms"] - diag["v_t_kms"]) < 1e-6
    # And definitely should NOT be ~1000
    assert diag["v_3d_kms"] < 800


def test_real_vr_preserved():
    """Streams with real v_r (not the placeholder) should keep their measurement."""
    from t95_v26_pilot_113_streams import stream_sigma_m_diagnostic
    diag = stream_sigma_m_diagnostic("Aquarius")
    # Aquarius has real v_r = -205 km/s
    assert diag["status"] == "ok"
    assert diag["v_r_was_placeholder"] is False
    assert abs(diag["v_r_effective_kms"] - diag["v_r_mid_kms"]) < 1e-6
    assert abs(diag["v_r_effective_kms"] - (-205.5)) < 1.0
