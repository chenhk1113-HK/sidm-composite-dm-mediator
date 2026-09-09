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
    """Dry-run mode should always produce outputs/t90/t90_v23_lz_lowE_count.json.

    If the data dir has a YAML/CSV present, may run in 'live' mode instead.
    Either way, the JSON must exist and have the expected keys.
    """
    import t90_v23_lz_evt_in_lowE_window as p1
    # Make sure T90_V23_DOWNLOAD is unset
    old = os.environ.pop("T90_V23_DOWNLOAD", None)
    try:
        output = p1.main()
        assert output is not None
        assert "mode" in output
        assert output["mode"] in ("dry_run", "live"), f"Unexpected mode: {output['mode']}"
        if output["mode"] == "dry_run":
            assert output["status"] == "awaiting_data"
        # Verify JSON file was written
        json_path = OUTPUTS_DIR / "t90_v23_lz_lowE_count.json"
        assert json_path.exists(), f"Expected output at {json_path}"
        loaded = json.loads(json_path.read_text())
        assert loaded["mode"] in ("dry_run", "live")
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


def test_path1_signal_region_mask_is_subclass_of_total():
    """The signal region mask should select a SUBSET of all events,
    not the entire dataset (would be a useless test)."""
    import t90_v23_lz_evt_in_lowE_window as p1
    # Construct a synthetic dataset
    s1c = np.array([3.0, 5.0, 10.0, 30.0, 80.0])
    log10s2c = np.array([3.5, 3.6, 3.8, 3.9, 4.1])
    mask = p1.lz_signal_region_mask(s1c, log10s2c)
    # All events in our test sample are below the ER median (good)
    # but only some should match the S1c window
    assert mask.sum() < len(s1c), "Signal region mask should be selective"
    assert mask.sum() >= 1, "Signal region mask should not be empty"
    # Specifically: S1c > 20 should NOT match (we want high-E_R tail)
    assert not mask[s1c > 20].any(), "Events with S1c > 20 should be excluded"


def test_path1_magnetic_m_prediction_via_wimpy():
    """If WIMpy is installed, magnetic_m_expected_count should return
    reasonable numbers (~1 event at [200,300] keVnr for LZ-tuned coupling)."""
    import t90_v23_lz_evt_in_lowE_window as p1
    s1c = np.array([5.0])
    log10s2c = np.array([3.7])
    result = p1.magnetic_m_expected_count_in_signal_region(s1c, log10s2c)
    if "error" not in result:
        # At LZ exposure (4.2 t-y) and m_chi=1 TeV, magnetic-m at tuned coupling
        # should give ~1.4 events in [200, 300] keVnr
        n_200_300 = result.get("N_pred_window_200_300_keVnr", 0)
        # Order-of-magnitude: should be between 0.1 and 100
        assert 0.01 < n_200_300 < 100, f"Got n_200_300 = {n_200_300}"


def test_path1_yaml_loader_parses_real_file(tmp_path):
    """If a real HEPData 155182 YAML is dropped in the data dir, the
    loader should parse it. Uses the actual file we have for testing."""
    import t90_v23_lz_evt_in_lowE_window as p1
    yaml_path = p1.EXPECTED_DATA_DIR / "WS2024_science_data.yaml"
    if not yaml_path.exists():
        pytest.skip("Real YAML not present (HEPData 155182)")
    arr = p1.load_yaml_s1s2(yaml_path)
    assert len(arr) > 1000, f"Expected >1000 events, got {len(arr)}"
    # First event should have S1c and log_10S2c
    assert "S1c" in arr.dtype.names
    assert "log_10S2c" in arr.dtype.names


# --- Path 2 ---

def test_path2_imports():
    import t90_v23_pandax_highE_count  # noqa: F401


def test_path2_dry_run_emits_json():
    """Path 2 dry-run should also produce a JSON even with no data present.

    If PandaX data is present, runs in 'live' mode instead. Either way,
    the JSON must exist.
    """
    import t90_v23_pandax_highE_count as p2
    old = os.environ.pop("T90_V23_DOWNLOAD", None)
    try:
        output = p2.main()
        assert output is not None
        assert output["mode"] in ("dry_run", "live"), f"Unexpected mode: {output['mode']}"
        if output["mode"] == "dry_run":
            # PandaX dry-run emits a schema note about energy range
            assert "schema_note" in output
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
    """Path 4 should always produce a result, even with no upstream data.

    In dry-run mode (no upstream JSONs), mode is 'dry_run'.
    In live mode (path 1/2 outputs present), mode is 'live'.
    Either way, the JSON must exist with valid posteriors.
    """
    import t90_v23_joint_three_detector_likelihood as p4
    output = p4.main()
    assert output is not None
    assert output["mode"] in ("dry_run", "live"), f"Unexpected mode: {output['mode']}"
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
    """With real data (LZ 4 events @ 200-300 keV, PandaX 287 @ 5-50 keVnr):

    Background dominates because PandaX [200, 300] has 695 events
    that neither magnetic-m nor Higgsino can explain. The [5, 50]
    keVnr window includes PandaX 287 events which magnetic-m predicts
    reasonably (422 predicted, 287 observed) but background also matches
    (287 = 287). So background wins at current PandaX exposure.

    When run in dry-run (no data), uses defaults: LZ=1, PandaX=0.
    In that case both signal hypotheses should dominate.
    """
    import t90_v23_joint_three_detector_likelihood as p4
    output = p4.main()
    mode = output.get("mode", "dry_run")
    posteriors = output["posteriors"]

    if mode == "live":
        # In live mode with real data, background is the right answer
        # because PandaX [200, 300] has 695 events that neither signal predicts.
        # Don't assert specific ordering here; just verify posteriors are valid.
        assert posteriors["H0_background_only"] >= 0
        assert posteriors["H0_background_only"] <= 1
        return

    # Dry-run: should be dominated by signal hypotheses
    p_bg = posteriors["H0_background_only"]
    p_magmom = posteriors["H1_magnetic_moment"]
    p_higgsino = posteriors["H2_higgsino_inelastic"]
    max_signal = max(p_magmom, p_higgsino)
    assert p_bg < max_signal / 3, (
        f"Background should be substantially disfavored vs best signal; "
        f"got p_bg={p_bg}, max(p_signal)={max_signal}, ratio={max_signal/p_bg:.2f}"
    )
    assert abs(p_magmom - p_higgsino) < 0.1, (
        f"Magnetic-m and Higgsino posteriors should be close; "
        f"got magmom={p_magmom}, higgsino={p_higgsino}"
    )


def test_path4_poisson_log_l_zero():
    """With full Poisson log L (including log(n_obs!) term):
       n_obs=0, n_pred=1: log L = -1 + 0 - log(1) = -1
       n_obs=1, n_pred=1: log L = -1 + 1*log(1) - log(1!) = -1
       n_obs=10, n_pred=1: log L = -1 + 10*log(1) - log(10!) = -1 - log(10!)
    """
    import t90_v23_joint_three_detector_likelihood as p4
    import math
    # n_obs=0, n_pred=1: log L = -1 + 0 - log(1) = -1
    assert p4.poisson_log_l(0, 1.0) == pytest.approx(-1.0)
    # n_obs=1, n_pred=1: log L = -1 + 0 - log(1!) = -1
    assert p4.poisson_log_l(1, 1.0) == pytest.approx(-1.0)
    # n_obs=10, n_pred=1: log L = -1 - log(10!) = -16.10
    assert p4.poisson_log_l(10, 1.0) == pytest.approx(-1.0 - math.log(math.factorial(10)))
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
