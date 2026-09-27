"""Tests for Phase 6b gravothermal integration smoke test."""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
V03_CODE = PROJECT_ROOT / "v0.3-prelim" / "code"
RESULTS_DIR = PROJECT_ROOT / "v0.3-prelim" / "data" / "results"

sys.path.insert(0, str(V03_CODE))
sys.path.insert(0, str(PROJECT_ROOT))

from phase6b_gravothermal_integration import (
    empirical_r_core,
    gravothermal_corrected_r_core,
)
from phase6_gravothermal_smoke_test import V03_MAP


class TestEmpiricalVsGravothermalRcore:
    """Compare empirical r_core = sqrt(sigma/m) vs gravothermal-corrected."""

    def test_dwarf_empirical_differs_from_gravothermal(self):
        """At MAP, dwarf r_core differs by ~37x."""
        dwarf_halo = {"r_s": 1.0, "v_max": 30.0, "rho_s": 1e7}
        sigma_m_v = 3.49  # sigma/m(v=30) at MAP
        r_empirical = empirical_r_core(sigma_m_v)
        r_gravothermal = gravothermal_corrected_r_core(
            V03_MAP["sigma_m_0"], V03_MAP["a"], 30.0, dwarf_halo
        )
        ratio = r_empirical / r_gravothermal
        assert ratio > 10, f"Dwarf ratio should be >10: {ratio}"

    def test_cluster_ratios_smaller_than_dwarf(self):
        """Cluster regime should have smaller empirical/gravothermal ratio."""
        dwarf_halo = {"r_s": 1.0, "v_max": 30.0, "rho_s": 1e7}
        cluster_halo = {"r_s": 20.0, "v_max": 300.0, "rho_s": 1e6}

        r_dwarf_emp = empirical_r_core(3.49)
        r_dwarf_grav = gravothermal_corrected_r_core(
            V03_MAP["sigma_m_0"], V03_MAP["a"], 30.0, dwarf_halo
        )
        r_cluster_emp = empirical_r_core(0.17)
        r_cluster_grav = gravothermal_corrected_r_core(
            V03_MAP["sigma_m_0"], V03_MAP["a"], 300.0, cluster_halo
        )

        dwarf_ratio = r_dwarf_emp / r_dwarf_grav
        cluster_ratio = r_cluster_emp / r_cluster_grav
        # Dwarf ratio should be larger than cluster ratio
        assert dwarf_ratio > cluster_ratio, (
            f"Dwarf ratio {dwarf_ratio} should be > cluster ratio {cluster_ratio}"
        )


class TestPhase6bResultsJSON:
    """Verify the Phase 6b results JSON is properly saved."""

    @pytest.fixture
    def results_path(self):
        return RESULTS_DIR / "phase6b_gravothermal_integration.json"

    def test_results_file_exists(self, results_path):
        assert results_path.exists()

    def test_results_have_scope_of_empirical_rule(self, results_path):
        with open(results_path) as f:
            results = json.load(f)
        assert "scope_of_empirical_rule" in results
        # Should have at least 6 entries (one per channel)
        assert len(results["scope_of_empirical_rule"]) >= 6

    def test_results_have_decision(self, results_path):
        with open(results_path) as f:
            results = json.load(f)
        # Per AGENTS.md rule 11: kill criterion triggered because empirical rule
        # is wrong but main likelihoods don't use it
        assert results["decision"] == "KILL"
        assert results["kill_criterion"]["triggered"] is True

    def test_results_have_dwarf_comparison(self, results_path):
        with open(results_path) as f:
            results = json.load(f)
        dwarf = results["dwarf_r_core_comparison"]
        assert dwarf["ratio_empirical_over_gravothermal"] > 10

    def test_main_pipeline_not_using_empirical_rule(self, results_path):
        """The main SPARC pipeline should be documented as NOT using the empirical rule."""
        with open(results_path) as f:
            results = json.load(f)
        scope = results["scope_of_empirical_rule"]
        main_sparc = scope.get("loglike_sparc_hierarchical (Ch8 main)", None)
        assert main_sparc is not None
        # The script documents that the main pipeline uses Kaplinghat+ 2016 scaling
        # (not empirical sqrt rule). Verify by checking actual_rule field.
        assert "Kaplinghat" in main_sparc.get("actual_rule", "")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])