"""
Tests for t106_multi_experiment_joint.

T106 adds PandaX-4T and XENONnT constraints to T103's LZ-only fit,
using the DIAMX combined analysis (arXiv:2512.05850v3, Nov 2025).
"""
from __future__ import annotations

import json
from pathlib import Path
import pytest

_T106_PATH = (Path(__file__).resolve().parents[1] / "outputs" / "t95" /
              "t106_multi_experiment_joint.json")


def _skip_if_no_t106():
    if not _T106_PATH.exists():
        pytest.skip("No T106 results; run t106_multi_experiment_joint.py")


def test_t106_outputs_present():
    _skip_if_no_t106()
    out = json.load(open(_T106_PATH))
    assert out["test"] == "T106_multi_experiment_joint_fit"
    assert "DIAMX_best_fit" in out
    assert "consistency_results" in out
    assert "t90_merge_criterion_1" in out


def test_t106_diamx_best_fit_at_60GeV_130keV():
    """DIAMX endothermic best-fit should be at (m_chi=60 GeV, delta=130 keV)."""
    _skip_if_no_t106()
    out = json.load(open(_T106_PATH))
    bf = out["DIAMX_best_fit"]
    assert bf["m_chi_GeV"] == 60.0
    assert bf["delta_keV"] == 130.0


def test_t106_local_significances_match_DIAMX_paper():
    """The local significances from DIAMX paper are LZ=2.3, PandaX=2.6, XENONnT=3.5."""
    _skip_if_no_t106()
    out = json.load(open(_T106_PATH))
    sigs = out["t90_merge_criterion_1"]["local_significances"]
    assert sigs["LZ"] == 2.3
    assert sigs["PandaX-4T"] == 2.6
    assert sigs["XENONnT"] == 3.5


def test_t106_diamx_best_fit_is_self_consistent():
    """The DIAMX best-fit should be CONSISTENT with itself (distance=0)."""
    _skip_if_no_t106()
    out = json.load(open(_T106_PATH))
    diamx_result = out["consistency_results"][0]
    assert diamx_result["point"] == "DIAMX best-fit (endothermic)"
    assert diamx_result["distance_sigma"] == 0.0
    assert diamx_result["verdict"].startswith("CONSISTENT")


def test_t106_t103_map_is_tension_with_DIAMX():
    """T103 MAP at 483 GeV is far from DIAMX best-fit at 60 GeV (~15σ in m_chi)."""
    _skip_if_no_t106()
    out = json.load(open(_T106_PATH))
    t103_result = out["consistency_results"][1]
    assert t103_result["point"] == "T103 MAP (project's existing LZ fit)"
    # Should be INCONSISTENT (T103 is LZ-only, DIAMX finds 60 GeV)
    assert t103_result["distance_sigma"] > 2.0


def test_t106_di_mauro_inconsistent():
    """Di Mauro's 1 TeV / 297 keV is ~32σ from DIAMX best-fit (60 GeV / 130 keV)."""
    _skip_if_no_t106()
    out = json.load(open(_T106_PATH))
    di_mauro_result = out["consistency_results"][2]
    assert di_mauro_result["point"] == "Di Mauro 2026 pseudo-Dirac"
    assert di_mauro_result["distance_sigma"] > 10.0


def test_t106_t90_criterion_1_status_reported():
    """T90 merge criterion #1 status should be reported with all 3 experiments."""
    _skip_if_no_t106()
    out = json.load(open(_T106_PATH))
    c1 = out["t90_merge_criterion_1"]
    assert c1["criterion"].startswith("T90 #1")
    assert "satisfied" in c1
    assert "n_experiments_above_2_5sigma" in c1
    assert "caveats" in c1


def test_t106_module_importable():
    """Module imports without error."""
    import warnings
    warnings.filterwarnings("ignore")
    import t106_multi_experiment_joint  # noqa: F401


def test_t106_combined_likelihood_function_works():
    """Spot-check the combined_log_likelihood function at a test point."""
    import sys
    import warnings
    warnings.filterwarnings("ignore")
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))
    from t106_multi_experiment_joint import combined_log_likelihood, DIAMX_BEST_FIT
    # At the best-fit, log L should be 0.5 * (2.3^2 + 2.6^2 + 3.5^2) = 11.3
    ll = combined_log_likelihood(
        DIAMX_BEST_FIT["m_chi_GeV"], DIAMX_BEST_FIT["delta_keV"])
    expected = 0.5 * (2.3**2 + 2.6**2 + 3.5**2)
    assert abs(ll["combined_log_L"] - expected) < 0.5  # tolerance for sigma
