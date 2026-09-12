"""Tests for Phase 6 gravothermal smoke test."""
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

from phase6_gravothermal_smoke_test import (
    gravothermal_r_core_simple,
    empirical_r_core,
    sigma_m_at_v,
    HALO_REGIMES,
    V03_MAP,
)


class TestGravothermalModelSanity:
    """Sanity checks on the Balberg+ 2002 normalized model."""

    def test_t_core_formula_is_correct(self):
        """t_core = 12.7 / sigma/m * (rho_s/1e7)^-1 * (r_s/v_max) * 0.977.

        For sigma/m=1, rho_s=1e7, r_s=1, v_max=1: t_core = 12.7 * 1 * 0.977 = 12.4 Gyr
        """
        r_core = gravothermal_r_core_simple(
            sigma_m=1.0, rho_s=1e7, r_s=1.0, v_max=1.0, t_Gyr=5.0
        )
        # t_core should be 12.7/1 * 1 * 0.977 = 12.4 Gyr
        # t=5 < t_core, so expanded phase: r_core = 0.045 * 1 * (1 - 0.3 * 5/12.4)
        expected = 0.045 * 1.0 * (1.0 - 0.3 * 5.0 / 12.4)
        assert abs(r_core - expected) < 1e-3, f"r_core={r_core}, expected={expected}"

    def test_collapsed_phase_floors_at_0p05_kpc(self):
        """When t > t_core, r_core decreases exponentially, floored at 0.05 kpc."""
        # Use high sigma/m and short t_core to ensure collapse
        r_core = gravothermal_r_core_simple(
            sigma_m=10.0, rho_s=1e7, r_s=1.0, v_max=10.0, t_Gyr=100.0
        )
        assert r_core >= 0.05, f"r_core={r_core} should be >= 0.05 kpc floor"

    def test_zero_sigma_m_returns_zero(self):
        r_core = gravothermal_r_core_simple(sigma_m=0.0, t_Gyr=10.0)
        assert r_core == 0.0


class TestV03MAPPredictions:
    """Verify gravothermal predictions at the v0.3-prelim MAP."""

    def test_dwarfs_are_collapsed_at_v03_map(self):
        """Dwarf halos at v=30 km/s, sigma/m=3.49 should be collapsed."""
        # At v=30 km/s, MAP gives sigma/m = 3.49 cm^2/g
        sigma_m_dwarf = sigma_m_at_v(V03_MAP["sigma_m_0"], V03_MAP["a"], 30.0)
        assert sigma_m_dwarf > 2.0, f"sigma/m_dwarf should be > 2, got {sigma_m_dwarf}"

        r_core = gravothermal_r_core_simple(
            sigma_m_dwarf, rho_s=1e7, r_s=1.0, v_max=30.0, t_Gyr=13.8
        )
        # Should be at the 0.05 kpc floor (collapsed)
        assert r_core <= 0.1, f"Dwarf should be collapsed, got r_core={r_core}"

    def test_clusters_are_expanded_at_v03_map(self):
        """Cluster halos at v=300 km/s, sigma/m=0.17 should still be expanded at 13.8 Gyr."""
        sigma_m_cluster = sigma_m_at_v(V03_MAP["sigma_m_0"], V03_MAP["a"], 300.0)
        assert sigma_m_cluster < 1.0, f"sigma/m_cluster should be < 1, got {sigma_m_cluster}"

        r_core = gravothermal_r_core_simple(
            sigma_m_cluster, rho_s=1e6, r_s=20.0, v_max=300.0, t_Gyr=13.8
        )
        # Should be in expanded phase (not floored)
        assert r_core > 0.5, f"Cluster should be expanded, got r_core={r_core}"


class TestEmpiricalVsGravothermal:
    """Compare empirical rule vs gravothermal model at v0.3-prelim MAP."""

    def test_empirical_differs_from_gravothermal_for_dwarfs(self):
        """Empirical r_core = sqrt(sigma/m) is wrong for collapsed dwarfs."""
        sigma_m_dwarf = sigma_m_at_v(V03_MAP["sigma_m_0"], V03_MAP["a"], 30.0)
        r_empirical = empirical_r_core(sigma_m_dwarf)
        r_gravothermal = gravothermal_r_core_simple(
            sigma_m_dwarf, rho_s=1e7, r_s=1.0, v_max=30.0, t_Gyr=13.8
        )
        # Empirical says 1.87 kpc; gravothermal says 0.05 kpc. Should differ by ~37x.
        ratio = r_empirical / r_gravothermal
        assert ratio > 10, (
            f"Empirical/gravothermal ratio for dwarfs should be >10: {ratio}"
        )


class TestPhase6ResultsJSON:
    """Verify the Phase 6 results JSON is properly saved."""

    @pytest.fixture
    def results_path(self):
        return RESULTS_DIR / "phase6_gravothermal_smoke_test.json"

    def test_results_file_exists(self, results_path):
        assert results_path.exists()

    def test_results_have_all_3_regimes(self, results_path):
        with open(results_path) as f:
            results = json.load(f)
        expected = set(HALO_REGIMES.keys())
        actual = set(results["results_per_regime"].keys())
        assert actual == expected

    def test_results_have_required_keys(self, results_path):
        with open(results_path) as f:
            results = json.load(f)
        for regime, r in results["results_per_regime"].items():
            assert "t_core_Gyr" in r
            assert "r_core_at_13p8_Gyr_kpc" in r
            assert "r_core_t_kpc" in r
            assert "sigma_m_v_cm2_per_g" in r

    def test_decision_is_proceed(self, results_path):
        """Per AGENTS.md rule 23: kill criterion NOT triggered at v0.3-prelim MAP
        because gravothermal evolution gives qualitatively different phases
        (collapsed vs expanded) and differs from empirical rule by ~37x for dwarfs.
        """
        with open(results_path) as f:
            results = json.load(f)
        assert results["decision"] == "PROCEED"
        assert results["kill_criterion"]["triggered"] is False

    def test_dwarf_phase_is_collapsed(self, results_path):
        """The collapsed dwarf finding is the headline."""
        with open(results_path) as f:
            results = json.load(f)
        dwarf = results["results_per_regime"]["dwarf"]
        # t_core should be << 13.8 Gyr (collapsed phase)
        assert dwarf["t_core_Gyr"] < 1.0, (
            f"Dwarf t_core should be < 1 Gyr: {dwarf['t_core_Gyr']}"
        )
        # r_core at 13.8 Gyr should be at the 0.05 kpc floor
        assert dwarf["r_core_at_13p8_Gyr_kpc"] <= 0.1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])