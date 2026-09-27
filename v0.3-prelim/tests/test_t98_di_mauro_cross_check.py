"""
Tests for t98_di_mauro_cross_check.

T98 compares the project's T43 inelastic joint fit posterior and T87
LZ forward prediction to Di Mauro 2026 (arXiv:2609.02608) — a
particle-physics interpretation of the LZ 248 keV event as
inelastic scattering via 𝒪₁ˢ (L10s) with mass splitting δ.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
import pytest


_RESULTS_PATH = (Path(__file__).resolve().parents[1] / "outputs" /
                 "t95" / "t98_di_mauro_cross_check.json")


def _skip_if_no_results():
    if not _RESULTS_PATH.exists():
        pytest.skip("No T98 results; run t98_di_mauro_cross_check.py")


def test_results_json_exists_and_valid():
    _skip_if_no_results()
    with _RESULTS_PATH.open() as f:
        out = json.load(f)
    assert out["test"] == "T98_di_mauro_2026_cross_check"
    assert "di_mauro_2026" in out
    assert "project_T43_inelastic_joint_fit" in out
    assert "verdicts" in out
    assert len(out["verdicts"]) >= 3


def test_delta_verdict_exists():
    _skip_if_no_results()
    with _RESULTS_PATH.open() as f:
        out = json.load(f)
    delta_verdicts = [v for v in out["verdicts"] if v["aspect"] == "delta"]
    assert len(delta_verdicts) == 1
    assert delta_verdicts[0]["verdict"] in ["MATCH", "PARTIAL", "MISMATCH"]


def test_sigma_verdict_quantifies_gap():
    """The cross-section verdict should document the 70+ order-of-magnitude gap."""
    _skip_if_no_results()
    with _RESULTS_PATH.open() as f:
        out = json.load(f)
    sigma_verdicts = [v for v in out["verdicts"] if v["aspect"] == "sigma_DM_nuc"]
    assert len(sigma_verdicts) == 1
    assert "74" in sigma_verdicts[0]["detail"] or "70" in sigma_verdicts[0]["detail"], \
        f"sigma verdict should mention the 70+ order-of-magnitude gap: {sigma_verdicts[0]['detail']}"


def test_di_mauro_paper_quoted():
    _skip_if_no_results()
    with _RESULTS_PATH.open() as f:
        out = json.load(f)
    assert out["reference"] == "arXiv:2609.02608v1 (Di Mauro, 2 Sep 2026)"
    assert out["di_mauro_2026"]["pseudo_dirac"]["delta_keV"] == 297
    assert out["di_mauro_2026"]["higgsino"]["delta_keV"] == 371


def test_project_t43_loaded():
    _skip_if_no_results()
    with _RESULTS_PATH.open() as f:
        out = json.load(f)
    p = out["project_T43_inelastic_joint_fit"]
    assert p["median_keV"] > 0
    assert p["q16_keV"] < p["median_keV"] < p["q84_keV"]


def test_module_importable():
    """Module imports without error."""
    import warnings
    warnings.filterwarnings("ignore")
    import t98_di_mauro_cross_check  # noqa: F401
