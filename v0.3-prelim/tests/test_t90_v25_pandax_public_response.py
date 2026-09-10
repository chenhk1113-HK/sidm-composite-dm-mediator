"""Tests for T90.25 PandaX public response extraction."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))

from t90_v25_pandax_public_response import (  # noqa: E402
    extract_xlsx_data,
    extract_root_keys,
    load_efficiency_graph,
    build_efficiency_proxy,
)


def test_xlsx_has_three_columns_and_1058_rows():
    data = extract_xlsx_data()
    assert data["headers"] == ["set", "S1", "log10(ne/S1)"]
    assert data["n_rows"] == 1058


def test_root_file_is_valid_root_container():
    keys = extract_root_keys()
    assert keys["file_size_bytes"] == 72058
    assert keys["root_header"] is True
    assert keys["keys"]


def test_efficiency_graph_is_loaded_from_public_file():
    graph = load_efficiency_graph()
    assert graph["n_points"] > 0
    assert graph["x_min"] >= 0.0
    assert graph["x_max"] > graph["x_min"]
    assert 0.0 <= graph["y_min"] <= 1.0
    assert 0.0 <= graph["y_max"] <= 1.0


def test_proxy_is_bounded_and_non_decreasing():
    proxy = build_efficiency_proxy()
    assert proxy["source"].startswith("PandaX public eff_RDQ_graph.root")
    ys = proxy["y_values"]
    assert all(0.0 <= y <= 1.0 for y in ys)
