"""
Tests for Phase 33d (real SPARC external probe).
"""
import pytest
import sys
import os
import json


class TestPhase33d:
    RESULTS_PATH = os.path.join(
        os.path.dirname(__file__), "..", "data", "results",
        "phase33d_external_probe_real.json"
    )
    SPARC_TABLE = os.path.join(
        os.path.dirname(__file__), "..", "data", "external", "sparc",
        "Table1.mrt"
    )

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 33d results not yet generated"
    )
    def test_results_file_valid(self):
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        assert "verdict" in data
        assert "n_galaxies" in data

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 33d results not yet generated"
    )
    def test_uses_real_sparc_data(self):
        """The probe must use real SPARC data, not synthetic."""
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        assert data["n_galaxies"] > 50, "Should use real SPARC sample (>50 galaxies)"
        assert "SPARC" in data.get("data_source", "")

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 33d results not yet generated"
    )
    def test_majority_pass(self):
        """At least 70% of real SPARC galaxies should be consistent."""
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        assert data["pct_consistent"] > 70, (
            f"Only {data['pct_consistent']:.1f}% pass — too low for external validation"
        )

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 33d results not yet generated"
    )
    def test_dwarfs_consistent(self):
        """Dwarf galaxies (Vflat 30-80) should all be in SIDM range."""
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        dwarf_data = data["velocity_band_breakdown"].get("Dwarfs (Vflat 30-80)", {})
        if dwarf_data and dwarf_data["n_galaxies"] > 0:
            pct = 100.0 * dwarf_data["n_in_sidm_range"] / dwarf_data["n_galaxies"]
            assert pct >= 80, f"Dwarfs only {pct:.0f}% in SIDM range"

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 33d results not yet generated"
    )
    def test_sparc_table_downloaded(self):
        """SPARC Table1.mrt must exist locally."""
        assert os.path.exists(self.SPARC_TABLE), (
            f"SPARC Table1.mrt not found at {self.SPARC_TABLE}"
        )