"""
Tests for t101_lz_data_extraction and t102_portal_b_fit.

T101 extracts LZ Table S8 local significances from the LZ 248 keV paper.
T102 runs a 2D Bayesian scan over (m_chi, delta) using these significances
as the likelihood and v0.7 MAP as a Gaussian prior on m_chi.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
import pytest

_LZ_DATA_PATH = (Path(__file__).resolve().parents[1] / "data" / "results" /
                 "lz_248kev_data_extraction.json")
_T102_PATH = (Path(__file__).resolve().parents[1] / "outputs" / "t95" /
              "t102_portal_b_posterior.json")


def _skip_if_no_lz_data():
    if not _LZ_DATA_PATH.exists():
        pytest.skip("No LZ data extraction; run t101_lz_data_extraction.py")


def _skip_if_no_t102():
    if not _T102_PATH.exists():
        pytest.skip("No T102 results; run t102_portal_b_fit.py")


def test_lz_event_coordinates():
    _skip_if_no_lz_data()
    data = json.load(open(_LZ_DATA_PATH))
    e = data["event_of_interest"]
    assert e["E_R_keV"] == 248
    assert e["E_R_stat_keV"] == 23
    assert e["S1c_phd"] == 540.1
    assert e["S2c_phd"] == 9268


def test_lz_background_in_248kev_window():
    _skip_if_no_lz_data()
    data = json.load(open(_LZ_DATA_PATH))
    bg = data["background_248keV_window"]
    assert bg["value"] == 0.0106
    assert bg["err"] == 0.0008


def test_lz_table_s8_os1_peak():
    _skip_if_no_lz_data()
    data = json.load(open(_LZ_DATA_PATH))
    s8 = data["table_S8_local_significance_sigma"]
    # Os1 at m_chi=1000 GeV, delta=350 keV: should be 3.3σ (per LZ paper)
    assert s8["Os1"]["1000"]["350"] == 3.3
    # Os1 at m_chi=1000 GeV, delta=0 keV: should be 0.0σ (no event)
    assert s8["Os1"]["1000"]["0"] == 0.0


def test_lz_table_s8_ov1_higgsino_consistent():
    _skip_if_no_lz_data()
    data = json.load(open(_LZ_DATA_PATH))
    s8 = data["table_S8_local_significance_sigma"]
    # Ov1 at m_chi=1000 GeV, delta=350 keV: 3.4σ (Higgsino prediction)
    assert s8["Ov1"]["1000"]["350"] == 3.4


def test_t102_outputs_present():
    _skip_if_no_t102()
    out = json.load(open(_T102_PATH))
    assert out["test"] == "T102_two_portal_tier2_fit"
    assert "Os1" in out["results_by_operator"]
    assert "Ov1" in out["results_by_operator"]
    assert "Os4" in out["results_by_operator"]


def test_t102_MAP_in_paper_range():
    """The MAP should be near 1 TeV / 300-350 keV per Di Mauro + Fan-Tweed."""
    _skip_if_no_t102()
    out = json.load(open(_T102_PATH))
    for op, r in out["results_by_operator"].items():
        m_map = r["MAP_m_chi_GeV"]
        d_map = r["MAP_delta_keV"]
        # m_chi should be near 1 TeV
        assert 700 <= m_map <= 2000, f"{op} MAP m_chi = {m_map} not in 700-2000"
        # delta should be in 250-400 keV range
        assert 250 <= d_map <= 400, f"{op} MAP delta = {d_map} not in 250-400"


def test_t102_higgsino_consistent_with_LZ():
    """Fan-Tweed Higgsino fixed point at (1.1 TeV, 350 keV) should give
    LZ significance >= 3.0σ (consistent with the 90% CL interval)."""
    _skip_if_no_t102()
    out = json.load(open(_T102_PATH))
    h = out["higgsino_test"]
    assert h["consistent_with_LZ"] is True
    assert h["LZ_sigma_at_Higgsino_point_Ov1"] >= 3.0


def test_t101_module_importable():
    """Module imports without error."""
    import warnings
    warnings.filterwarnings("ignore")
    import t101_lz_data_extraction  # noqa: F401


def test_t102_module_importable():
    """Module imports without error."""
    import warnings
    warnings.filterwarnings("ignore")
    import t102_portal_b_fit  # noqa: F401
