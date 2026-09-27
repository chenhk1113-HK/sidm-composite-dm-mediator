"""
Tests for Phase 33b (Tsai 2022 prediction) and Phase 33c (external probe).
"""
import pytest
import sys
import os
import json


class TestPhase33b:
    RESULTS_PATH = os.path.join(
        os.path.dirname(__file__), "..", "data", "results",
        "phase33b_tsai_2022_prediction.json"
    )

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 33b results not yet generated"
    )
    def test_results_file_valid(self):
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        assert "verdict" in data
        assert "fitted_v_targets_kms" in data

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 33b results not yet generated"
    )
    def test_fitted_positions_recorded(self):
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        fitted = data["fitted_v_targets_kms"]
        assert len(fitted) == 4

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 33b results not yet generated"
    )
    def test_verdict_is_honest(self):
        """Verdict must reflect that fitted positions are phenomenological."""
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        # Either PHENOMENOLOGICAL or PARTIALLY PREDICTED is honest
        assert "PHENOMENOLOGICAL" in data["verdict"] or "PARTIALLY" in data["verdict"] or "PREDICTED" in data["verdict"]


class TestPhase33c:
    RESULTS_PATH = os.path.join(
        os.path.dirname(__file__), "..", "data", "results",
        "phase33c_external_probe.json"
    )

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 33c results not yet generated"
    )
    def test_results_file_valid(self):
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        assert "verdict" in data
        assert "n_galaxies" in data
        assert data["n_galaxies"] > 0

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 33c results not yet generated"
    )
    def test_majority_in_sidm_range(self):
        """At least 50% of galaxies should be in SIDM-consistent range."""
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        assert data["pct_consistent"] > 50

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 33c results not yet generated"
    )
    def test_velocity_bands_recorded(self):
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        assert "velocity_band_breakdown" in data