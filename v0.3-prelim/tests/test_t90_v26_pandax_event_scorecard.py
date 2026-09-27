"""Tests for T90.26 event-level scorecard."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))

from t90_v26_pandax_event_scorecard import load_events, signal_prediction  # noqa: E402


def test_event_level_rows_are_loaded():
    events = load_events()
    assert len(events["run0"]) == 1117
    assert len(events["run1"]) == 1373
    assert all("E_R_approx_keVnr" in r for r in events["run0"][:10])


def test_scorecard_does_not_claim_event_identification():
    events = load_events()
    assert all("below_nr_median_proxy" in r for r in events["run1"])
    assert any(r["below_nr_median_proxy"] for r in events["run1"])


def test_model_prediction_is_separate_from_event_rows():
    pred = signal_prediction()
    assert pred["combined"]["selected_signal"] > 0.0
    assert pred["combined"]["selected_signal_below_nr_median_proxy"] > 0.0
