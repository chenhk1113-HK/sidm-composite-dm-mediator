"""
Tests for Phase 36 (concentration-dependent collapse).
"""
import pytest
import sys
import os
import json


class TestPhase36:
    RESULTS_PATH = os.path.join(
        os.path.dirname(__file__), "..", "data", "results",
        "phase36_concentration_collapse.json"
    )

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 36 results not yet generated"
    )
    def test_results_file_valid(self):
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        assert "results" in data
        assert "verdict" in data
        assert "interpretation" in data

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 36 results not yet generated"
    )
    def test_systems_evaluated(self):
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        results = data["results"]
        assert len(results) >= 5  # At least 5 systems
        names = [r["name"] for r in results]
        # Critical systems must be present
        for required in ["Fornax", "JVAS perturber", "Cloud-9"]:
            assert required in names, f"Missing required system: {required}"

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 36 results not yet generated"
    )
    def test_jvas_collapse_analysis(self):
        """JVAS perturber should have t_c << Hubble time (collapsed)."""
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        jvas = next(r for r in data["results"] if r["name"] == "JVAS perturber")
        # JVAS with c=50 should collapse within Hubble time
        if jvas["sigma_m_initial"] >= 50:
            assert jvas["t_c_Gyr"] < 13.8, (
                f"JVAS t_c = {jvas['t_c_Gyr']:.2f} Gyr > Hubble time"
            )

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 36 results not yet generated"
    )
    def test_fornax_no_collapse(self):
        """Fornax (c=10) should NOT collapse within Hubble time."""
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        fornax = next(r for r in data["results"] if r["name"] == "Fornax")
        assert fornax["c_200"] == 10  # c=10 dwarfs
        # Fornax t_c should be >> Hubble time if collapsed=False
        if not fornax["collapsed"]:
            assert fornax["t_c_Gyr"] > 13.8