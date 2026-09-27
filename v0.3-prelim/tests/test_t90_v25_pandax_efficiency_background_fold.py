"""Tests for T90.25 PandaX public response and folded analysis."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))

from t90_v25_pandax_efficiency_background_fold import (  # noqa: E402
    fold_by_run,
    load_candidate_counts,
    public_efficiency,
)
from t90_v25_pandax_public_response import (  # noqa: E402
    extract_root_keys,
    extract_xlsx_data,
    load_efficiency_graph,
)
from t90_v24_pandax_fold import magnetic_signal_spectrum  # noqa: E402


def test_public_files_and_candidate_counts():
    assert load_candidate_counts() == {"run0": 1117, "run1": 1373, "total": 2490}
    assert extract_xlsx_data()["n_rows"] == 1058


def test_root_graph_is_real_and_bounded():
    info = extract_root_keys()
    graph = load_efficiency_graph()
    assert info["root_header"]
    assert info["file_size_bytes"] == 72058
    assert graph["graph_name"] == "eff_nr"
    assert graph["n_points"] == 1497
    assert 0.0 <= graph["y_min"] <= graph["y_max"] <= 1.0


def test_public_efficiency_has_nontrivial_shape():
    energy = np.array([3.0, 5.0, 10.0, 20.0, 50.0])
    eff = public_efficiency(energy)
    assert np.all((eff >= 0.0) & (eff <= 1.0))
    assert eff[0] < eff[2] < eff[3]


def test_run_separated_fold_is_auditable():
    energy = np.linspace(0.5, 270.0, 6000)
    fold = fold_by_run(energy, magnetic_signal_spectrum(energy))
    assert set(fold) == {"run0", "run1", "combined"}
    assert fold["run0"]["efficiency_folded_signal"] > 0.0
    assert fold["run1"]["efficiency_folded_signal"] > fold["run0"]["efficiency_folded_signal"]
    assert fold["combined"]["efficiency_folded_signal"] == sum(
        fold[r]["efficiency_folded_signal"] for r in ("run0", "run1")
    )
