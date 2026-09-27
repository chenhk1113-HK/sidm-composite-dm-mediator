"""
Tests for Phase 38 (sidmkit cross-check).
"""
import pytest
import os
import json


class TestPhase38:
    """Tests for Phase 38 — sidmkit cross-check."""

    RESULTS_DIR = os.path.join(
        os.path.dirname(__file__), "..", "data", "results"
    )

    def test_sidmkit_installed(self):
        """Verify sidmkit is installed."""
        try:
            import sidmkit
            assert sidmkit.__version__ is not None
        except ImportError:
            pytest.skip("sidmkit not installed")

    def test_part_b_summary(self):
        """Verify Part B sidmkit SPARC fit summary is sane."""
        path_b = os.path.join(self.RESULTS_DIR, "phase38b_sidmkit_sparc.json")
        if not os.path.exists(path_b):
            pytest.skip("Phase 38b results not yet generated")
        with open(path_b) as f:
            data = json.load(f)
        assert data["n_sidmkit_fits"] == 127
        assert data["n_sidmkit_success"] == 127
        assert data["chi2r_median"] < 2.0
        assert data["n_good_fit_chi2_lt_2"] >= 50

    def test_part_a_summary(self):
        """Verify Part A sidmkit sigma/v comparison ran."""
        path_a = os.path.join(self.RESULTS_DIR, "phase38_sidmkit_crosscheck.json")
        if not os.path.exists(path_a):
            pytest.skip("Phase 38a results not yet generated")
        with open(path_a) as f:
            data = json.load(f)
        assert "part_a" in data
        part_a = data["part_a"]
        assert "verdict" in part_a
        assert "results" in part_a
        assert len(part_a["results"]) >= 10