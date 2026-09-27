"""
Tests for Phase 32c (re-run all 9 critical review tests).
"""
import pytest
import sys
import os
import json


class TestPhase32c:
    RESULTS_PATH = os.path.join(
        os.path.dirname(__file__), "..", "data", "results",
        "phase32c_all_9_tests.json"
    )

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 32c results not yet generated"
    )
    def test_results_file_valid(self):
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        assert "test_results" in data
        assert len(data["test_results"]) == 9

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 32c results not yet generated"
    )
    def test_all_9_tests_recorded(self):
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        expected_tests = ["D", "A", "F", "B", "C", "H", "I", "E", "G"]
        for t in expected_tests:
            assert t in data["test_results"]

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 32c results not yet generated"
    )
    def test_test_h_dwarf_cores_fixed(self):
        """The CRITICAL Test H failure must be fixed."""
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        test_h = data["test_results"]["H"]
        assert "FIXED" in test_h["verdict"]

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 32c results not yet generated"
    )
    def test_test_g_stream_gaps_fixed(self):
        """The CRITICAL Test G failure must be fixed."""
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        test_g = data["test_results"]["G"]
        assert "FIXED" in test_g["verdict"]

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 32c results not yet generated"
    )
    def test_all_pass(self):
        """All 9 tests should pass."""
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        assert data["n_pass"] == 9
        assert data["n_fail"] == 0
        assert data["aggregate"] == "ALL_9_PASS"

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 32c results not yet generated"
    )
    def test_phase31bc_fixes_documented(self):
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        assert "phase31bc_fixes" in data
        assert "Test_H_dwarf_cores" in data["phase31bc_fixes"]
        assert "Test_G_stream_gaps" in data["phase31bc_fixes"]