"""
Tests for T90.23 dry-run scripts (paths 1-4).

These tests verify:
  1. All four scripts import without errors
  2. Each script's dry-run mode produces a valid JSON output
  3. Path 4's joint likelihood has the right structure and reasonable
     posteriors under the LZ-anchor scenario
  4. The download helper respects the T90_V23_DOWNLOAD env var (refuses
     to auto-download when unset)
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
import pytest

# Project imports
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_PROJECT_ROOT / "code"))

OUTPUTS_DIR = _PROJECT_ROOT / "outputs" / "t90"
# Ensure outputs dir exists before any tests run (avoids race in tmp tests)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)


# --- Path 1 imports + dry-run produces JSON ---

def test_path1_imports():
    import t90_v23_lz_evt_in_lowE_window  # noqa: F401


def test_path1_dry_run_emits_json(tmp_path):
    """Dry-run mode should always produce outputs/t90/t90_v23_lz_lowE_count.json."""
    import t90_v23_lz_evt_in_lowE_window as p1
    # Make sure T90_V23_DOWNLOAD is unset
    old = os.environ.pop("T90_V23_DOWNLOAD", None)
    try:
        output = p1.main()
        assert output is not None
        assert "mode" in output
        # In dry-run (no data), should be dry_run + awaiting_data
        assert output["mode"] == "dry_run"
        assert output["status"] == "awaiting_data"
        assert "candidate_urls" in output
        assert "magnetic_moment_prediction" in output
        # Verify JSON file was written
        json_path = OUTPUTS_DIR / "t90_v23_lz_lowE_count.json"
        assert json_path.exists(), f"Expected output at {json_path}"
        loaded = json.loads(json_path.read_text())
        assert loaded["mode"] == "dry_run"
    finally:
        if old is not None:
            os.environ["T90_V23_DOWNLOAD"] = old


def test_path1_download_respects_env():
    """try_download() must return None when T90_V23_DOWNLOAD is unset."""
    import t90_v23_lz_evt_in_lowE_window as p1
    old = os.environ.pop("T90_V23_DOWNLOAD", None)
    try:
        result = p1.try_download(p1.EXPECTED_DATA_DIR)
        assert result is None, "try_download should return None when env var unset"
    finally:
        if old is not None:
            os.environ["T90_V23_DOWNLOAD"] = old


def test_path1_magnetic_moment_prediction_keys():
    """The magnetic-moment prediction dict must contain all expected keys."""
    import t90_v23_lz_evt_in_lowE_window as p1
    pred = p1.MAG_MOMENT_PREDICTION
    assert "N_pred_window_5_50_keV" in pred
    assert "N_pred_window_200_300_keV" in pred
    assert pred["N_pred_window_200_300_keV"] == 1.0   # the calibration anchor
    assert pred["N_pred_window_5_50_keV"] == 778.0    # the smoking gun


def test_path1_url_list_prioritizes_155182_standin():
    """Per 2026-09-10 Option-1 decision: 155182 is the PRIMARY source
    because 182472 (248 keV paper's eventual HEPData release) is not
    yet active. This test documents the URL priority choice."""
    import t90_v23_lz_evt_in_lowE_window as p1
    urls = p1.LZ_DATA_URLS
    # PRIMARY must be the 155182 Data table CSV (ins2841863/Data/2/csv)
    assert "ins2841863/Data/2/csv" in urls[0], (
        f"PRIMARY URL must be 155182 Data table; got {urls[0]}"
    )
    # 182472 should still be in the list as a placeholder for the future
    assert any("182472" in u for u in urls), (
        "Expected 182472 placeholder to remain in fallback list"
    )


# --- Path 2 ---

def test_path2_imports():
    import t90_v23_pandax_highE_count  # noqa: F401


def test_path2_dry_run_emits_json():
    """Path 2 dry-run should also produce a JSON even with no data present."""
    import t90_v23_pandax_highE_count as p2
    old = os.environ.pop("T90_V23_DOWNLOAD", None)
    try:
        output = p2.main()
        assert output is not None
        # PandaX CDN was unreachable, so should be dry_run
        assert output["mode"] == "dry_run"
        assert output["status"] == "awaiting_data"
        # Verify the schema note about energy range is present
        assert "schema_note" in output
        assert "0.04" in output["schema_note"] or "keVee" in output["schema_note"]
        # Verify JSON file
        json_path = OUTPUTS_DIR / "t90_v23_pandax_highE_count.json"
        assert json_path.exists()
    finally:
        if old is not None:
            os.environ["T90_V23_DOWNLOAD"] = old


def test_path2_pandax_exposure():
    """Sanity: PandaX exposure should be ~1.54 tonne-years."""
    import t90_v23_pandax_highE_count as p2
    assert p2.MAG_MOMENT_PREDICTION_PANDAX["exposure_tonne_years"] == pytest.approx(1.54)


# --- Path 3 ---

def test_path3_imports():
    import t90_v23_xenonnt_s2only_highE  # noqa: F401


def test_path3_dry_run_emits_json():
    import t90_v23_xenonnt_s2only_highE as p3
    old = os.environ.pop("T90_V23_DOWNLOAD", None)
    try:
        output = p3.main()
        assert output is not None
        assert output["mode"] == "dry_run"
        # Path 3 has a fundamental caveat about S2-only energy range
        assert "fundamental_caveat" in output
        assert "0.7" in output["fundamental_caveat"]
        json_path = OUTPUTS_DIR / "t90_v23_xenonnt_s2only_count.json"
        assert json_path.exists()
    finally:
        if old is not None:
            os.environ["T90_V23_DOWNLOAD"] = old


# --- Path 4 (joint likelihood) ---

def test_path4_imports():
    import t90_v23_joint_three_detector_likelihood  # noqa: F401


def test_path4_dry_run_emits_json():
    """Path 4 should always produce a result, even with no upstream data."""
    import t90_v23_joint_three_detector_likelihood as p4
    output = p4.main()
    assert output is not None
    assert output["mode"] == "dry_run"
    assert "posteriors" in output
    # Posteriors must sum to ~1
    p_sum = sum(output["posteriors"].values())
    assert p_sum == pytest.approx(1.0, abs=1e-6), f"Posteriors don't sum to 1: {p_sum}"
    # All 3 hypotheses must be present
    assert "H1_magnetic_moment" in output["posteriors"]
    assert "H2_higgsino_inelastic" in output["posteriors"]
    assert "H0_background_only" in output["posteriors"]
    json_path = OUTPUTS_DIR / "t90_v23_joint_likelihood.json"
    assert json_path.exists()


def test_path4_posteriors_reasonable_for_lz_anchor():
    """With N_obs=1 at LZ and 0 at PandaX in [200, 300] keV window:
       - Magnetic-m and Higgsino both predict ~1 at LZ, ~0.5 at PandaX
       - Background predicts 0.05 at LZ, 0.02 at PandaX
       Therefore background should be penalized strongly; both signal
       hypotheses should dominate the posterior.
    """
    import t90_v23_joint_three_detector_likelihood as p4
    output = p4.main()
    posteriors = output["posteriors"]
    # Both signal hypotheses should dominate over background by ~5x or more
    p_bg = posteriors["H0_background_only"]
    p_magmom = posteriors["H1_magnetic_moment"]
    p_higgsino = posteriors["H2_higgsino_inelastic"]
    max_signal = max(p_magmom, p_higgsino)
    assert p_bg < max_signal / 3, (
        f"Background should be substantially disfavored vs best signal; "
        f"got p_bg={p_bg}, max(p_signal)={max_signal}, ratio={max_signal/p_bg:.2f}"
    )
    # Magnetic-m and Higgsino should be similar (both predict ~1 at LZ, ~0.5 at PandaX)
    p_magmom = posteriors["H1_magnetic_moment"]
    p_higgsino = posteriors["H2_higgsino_inelastic"]
    assert abs(p_magmom - p_higgsino) < 0.1, (
        f"Magnetic-m and Higgsino posteriors should be close; "
        f"got magmom={p_magmom}, higgsino={p_higgsino}"
    )


def test_path4_poisson_log_l_zero():
    """At n_obs = n_pred, Poisson log L should be 0 for n_obs=0 (max), or
       negative for n_obs > 0. Verify with n_obs=0, n_pred=0 -> -inf."""
    import t90_v23_joint_three_detector_likelihood as p4
    # n_obs=0, n_pred=1: log L = -1
    assert p4.poisson_log_l(0, 1.0) == pytest.approx(-1.0)
    # n_obs=1, n_pred=1: log L = -1 + log(1) = -1
    assert p4.poisson_log_l(1, 1.0) == pytest.approx(-1.0)
    # n_obs=10, n_pred=1: log L = -1 + 10*log(1) = -1
    assert p4.poisson_log_l(10, 1.0) == pytest.approx(-1.0)
    # n_obs=0, n_pred=0: degenerate, returns -inf
    assert p4.poisson_log_l(0, 0.0) == -np.inf


# --- Orchestrator ---

def test_orchestrator_runs_all_four():
    """The orchestrator should run all four paths without errors."""
    import t90_v23_dry_run_all
    t90_v23_dry_run_all.main()
    # All four JSONs should exist
    for fname in (
        "t90_v23_lz_lowE_count.json",
        "t90_v23_pandax_highE_count.json",
        "t90_v23_xenonnt_s2only_count.json",
        "t90_v23_joint_likelihood.json",
    ):
        assert (OUTPUTS_DIR / fname).exists(), f"Missing {fname}"


# --- Smoke test: re-run scripts make sure they don't error ---
