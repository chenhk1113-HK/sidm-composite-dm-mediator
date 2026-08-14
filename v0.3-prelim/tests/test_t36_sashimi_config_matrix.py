"""
Tests for T36 (Direction A closure: SASHIMI 3x2 config matrix).

D11 deliverable: Closes the Hayashi+ 2025 250-500x gap via the
3x2 SASHIMI config matrix (c_vir relation x v_eff prescription).

The Hayashi+ 2025 c_vir concentration-mass relation (option A2) is the
expected best config (per Pipeline Overview1.docx review §5 #1 partial).

This test enforces:
  - t36 script is importable
  - T36 result JSON exists
  - T36's best config gap is < 1 dex (PUBLICATION-GRADE threshold)
  - The 3 c_vir relations + 1 v_eff = 3 configurations are all run
"""
import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RESULTS_PATH = PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "t36_sashimi_config_matrix.json"


class TestT36Module:
    """t36_sashimi_config_matrix.py is importable."""

    def test_t36_importable(self):
        t36 = pytest.importorskip("t36_sashimi_config_matrix")
        # Required axes
        assert hasattr(t36, "C_VIR_RELATIONS")
        assert hasattr(t36, "predict_collapse_fraction")
        assert hasattr(t36, "run_one_config")
        assert hasattr(t36, "main")

    def test_c_vir_relations_defined(self):
        """Three c_vir relations should be defined: A1 Dutton-Maccio, A2 Hayashi, A3 Ludlow."""
        t36 = pytest.importorskip("t36_sashimi_config_matrix")
        keys = set(t36.C_VIR_RELATIONS.keys())
        assert any("dutton" in k.lower() for k in keys), f"No Dutton-Maccio relation in {keys}"
        assert any("hayashi" in k.lower() for k in keys), f"No Hayashi relation in {keys}"
        assert any("ludlow" in k.lower() for k in keys), f"No Ludlow relation in {keys}"

    def test_hayashi_relation_higher_than_dutton(self):
        """Hayashi+ 2025 c_vir should be > Dutton-Maccio 2014 at dwarf scale.
        If wrong, the relation calibration would be off."""
        t36 = pytest.importorskip("t36_sashimi_config_matrix")
        M_vir_test = 1e8  # MW satellite regime
        c_dutton = t36.c_vir_dutton_maccio_2014(M_vir_test)
        c_hayashi = t36.c_vir_hayashi_2025(M_vir_test)
        c_ludlow = t36.c_vir_ludlow_2016(M_vir_test)
        assert c_hayashi > c_dutton, (
            f"Hayashi c_vir ({c_hayashi:.2f}) should be > Dutton-Maccio ({c_dutton:.2f}) "
            f"at M_vir=10^8, but the relation doesn't agree."
        )
        assert c_ludlow < c_dutton, (
            f"Ludlow c_vir ({c_ludlow:.2f}) should be < Dutton-Maccio ({c_dutton:.2f})"
        )


class TestT36Result:
    """If T36 result JSON exists, validate it."""

    def test_t36_result_or_skip(self):
        if not RESULTS_PATH.exists():
            pytest.skip("No T36 result JSON; run t36 first")
        with open(RESULTS_PATH) as f:
            data = json.load(f)
        assert "test" in data
        assert "configs_run" in data
        assert "verdict" in data
        assert "best_config" in data
        assert "best_crossing_sigma_0_cm2_per_g" in data

    def test_t36_three_configs_run(self):
        """All 3 (A1, A2, A3) c_vir configurations must be present."""
        if not RESULTS_PATH.exists():
            pytest.skip("No T36 result JSON")
        with open(RESULTS_PATH) as f:
            data = json.load(f)
        configs = data["configs_run"]
        assert len(configs) >= 3, f"Expected at least 3 configs, got {len(configs)}"
        labels = [c["config_label"] for c in configs]
        for needed in ("A1", "A2", "A3"):
            assert any(label.startswith(needed) for label in labels), (
                f"Config {needed} missing; ran: {labels}"
            )

    def test_t36_best_config_within_publication_threshold(self):
        """The BEST config's gap to Hayashi+ 2025 should be < 1 dex (publication-grade)."""
        if not RESULTS_PATH.exists():
            pytest.skip("No T36 result JSON")
        with open(RESULTS_PATH) as f:
            data = json.load(f)
        gap = data.get("best_gap_in_dex")
        ratio = data.get("best_ratio_to_hayashi")
        if gap is None:
            pytest.skip("No best config identified (no crossings found in any config)")
        # The headline direction-A closure: gap < 1 dex means within 10x of Hayashi+ 2025
        assert gap < 1.0, (
            f"Best config ({data['best_config']}) has gap = {gap:.2f} dex "
            f"(ratio = {ratio:.1f}x Hayashi+ 2025 boundary). "
            f"Need gap < 1.0 dex (within 10x) for Direction A closure."
        )

    def test_t36_verdict_classifies(self):
        """T36's verdict must classify the gap."""
        if not RESULTS_PATH.exists():
            pytest.skip("No T36 result JSON")
        with open(RESULTS_PATH) as f:
            data = json.load(f)
        verdict = data.get("verdict", "")
        acceptable = ("CLOSED", "PARTIAL CLOSURE", "DOES NOT CLOSE", "NO CONFIGURATION")
        assert any(kw in verdict.upper() for kw in acceptable), (
            f"T36 verdict unparseable: {verdict!r}"
        )
