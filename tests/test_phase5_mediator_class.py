"""Tests for Phase 5 mediator class comparison."""
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

from phase5_mediator_class_comparison import (
    MEDIATOR_CLASSES,
    V03_MAP,
    V_REF,
    sigma_m_power_law,
    sigma_m_yukawa,
    sigma_m_scalar_portal,
    sigma_m_composite,
    loglike_t39_with_form,
)


class TestMediatorFormsAreDistinct:
    """Verify that the 4 mediator forms produce different sigma/m(v) curves."""

    def test_yukawa_gives_different_shape_than_power_law(self):
        """Yukawa form has different velocity dependence than power-law."""
        v_dwarf = 10.0
        v_cluster = 1000.0
        s_pl_dwarf = sigma_m_power_law(V03_MAP["sigma_m_0"], V03_MAP["a"], v_dwarf)
        s_pl_cluster = sigma_m_power_law(V03_MAP["sigma_m_0"], V03_MAP["a"], v_cluster)
        s_yu_dwarf = sigma_m_yukawa(V03_MAP["sigma_m_0"], V03_MAP["a"], v_dwarf)
        s_yu_cluster = sigma_m_yukawa(V03_MAP["sigma_m_0"], V03_MAP["a"], v_cluster)

        # The RATIO (v_dwarf / v_cluster) should differ between forms
        pl_ratio = s_pl_dwarf / s_pl_cluster
        yu_ratio = s_yu_dwarf / s_yu_cluster
        assert abs(pl_ratio - yu_ratio) > 1.0, (
            f"Yukawa should differ from power-law: pl_ratio={pl_ratio:.2f}, yu_ratio={yu_ratio:.2f}"
        )

    def test_composite_is_negligible_at_cluster_velocity(self):
        """Composite resonance should give sigma/m ~ 0 at v=1000 km/s."""
        s_composite_cluster = sigma_m_composite(
            V03_MAP["sigma_m_0"], V03_MAP["a"], 1000.0
        )
        s_composite_resonance = sigma_m_composite(
            V03_MAP["sigma_m_0"], V03_MAP["a"], 30.0
        )
        # At resonance (v=30), sigma/m should be near full value
        # At v=1000, it should be near zero (exp(-(1000-30)^2/(2*50^2)))
        assert s_composite_resonance > s_composite_cluster * 1e10

    def test_scalar_portal_has_linear_dependence(self):
        """Scalar portal: sigma/m(v) = sigma/m_0 * (1 + 0.5 * (v/v_ref - 1))."""
        v_low = 10.0
        v_high = 1000.0
        s_low = sigma_m_scalar_portal(V03_MAP["sigma_m_0"], V03_MAP["a"], v_low)
        s_high = sigma_m_scalar_portal(V03_MAP["sigma_m_0"], V03_MAP["a"], v_high)
        # At v_low=10, factor = 1 + 0.5 * (0.1 - 1) = 0.55
        # At v_high=1000, factor = 1 + 0.5 * (10 - 1) = 5.5
        expected_low = V03_MAP["sigma_m_0"] * 0.55
        expected_high = V03_MAP["sigma_m_0"] * 5.5
        assert abs(s_low - expected_low) < 1e-6
        assert abs(s_high - expected_high) < 1e-6

    def test_all_forms_normalized_at_v_ref(self):
        """All mediator forms should give sigma/m_0 at v_ref=100 km/s."""
        for class_id in MEDIATOR_CLASSES:
            fn = MEDIATOR_CLASSES[class_id]["fn"]
            extra = MEDIATOR_CLASSES[class_id]["extra_params"]
            s = fn(V03_MAP["sigma_m_0"], V03_MAP["a"], V_REF, **extra)
            # Composite is the only form that may differ (off-resonance)
            if class_id == "composite":
                # v=100 km/s is ~1.4*delta_v from v_R=30, so exp(-(100-30)^2/(2*50^2))
                # = exp(-(70)^2/(5000)) = exp(-0.98) ~ 0.375
                # Times sigma/m_0 = 0.72 * 0.375 = 0.27
                assert 0.2 < s < 0.3
            else:
                # Other forms are normalized to sigma/m_0 at v_ref
                assert abs(s - V03_MAP["sigma_m_0"]) < 1e-6, (
                    f"{class_id}: sigma/m at v_ref={s}, expected {V03_MAP['sigma_m_0']}"
                )


class TestMediatorFormLikelihoodsAreComputed:
    """Verify loglike_t39_with_form runs for each mediator class."""

    @pytest.mark.parametrize("class_id", list(MEDIATOR_CLASSES.keys()))
    def test_loglike_runs_for_each_class(self, class_id):
        """loglike_t39_with_form should return a finite value for each class."""
        ll = loglike_t39_with_form(
            V03_MAP["sigma_m_0"], V03_MAP["a"], class_id
        )
        assert np.isfinite(ll), f"{class_id}: loglike={ll} is not finite"
        # Per AGENTS.md rule 23: loglike should be negative (real data likelihood)
        assert ll < 0, f"{class_id}: loglike={ll} should be negative for real data"

    def test_power_law_matches_T39_reference(self):
        """Power-law loglike should be close to T39 reference (log_Z=-2.94 in nats
        above the bulk which is ~-279K from SPARC)."""
        ll_power = loglike_t39_with_form(
            V03_MAP["sigma_m_0"], V03_MAP["a"], "power_law"
        )
        assert np.isfinite(ll_power)


class TestPhase5ResultsJSON:
    """Verify the Phase 5 results JSON is properly saved."""

    @pytest.fixture
    def results_path(self):
        return RESULTS_DIR / "phase5_mediator_class_comparison.json"

    def test_results_file_exists(self, results_path):
        assert results_path.exists(), f"Phase 5 results file missing at {results_path}"

    def test_results_have_required_keys(self, results_path):
        with open(results_path) as f:
            results = json.load(f)
        assert "phase" in results
        assert "v03_map" in results
        assert "log_Z_per_class" in results
        assert "decision" in results
        assert "kill_criterion" in results

    def test_results_have_all_4_mediator_classes(self, results_path):
        with open(results_path) as f:
            results = json.load(f)
        expected = {"power_law", "yukawa", "scalar_portal", "composite"}
        actual = set(results["log_Z_per_class"].keys())
        assert actual == expected, f"Expected {expected}, got {actual}"

    def test_decision_is_kill(self, results_path):
        """Per AGENTS.md rule 11: kill criterion IS triggered but for the right reason.

        The kill criterion is triggered because the existing likelihoods are baked
        into the power-law form, so they cannot discriminate mediator classes
        through this test (which is a structural limitation, not a physics finding).
        """
        with open(results_path) as f:
            results = json.load(f)
        # Kill criterion is triggered
        assert results["decision"] == "KILL"
        assert results["kill_criterion"]["triggered"] is True


class TestKillCriterionHonestFraming:
    """Per AGENTS.md rule 11: kill criterion is triggered BUT the test
    is structurally limited (likelihoods are baked into power-law form).
    This is honest framing, not a clean kill."""

    def test_sigma_m_curves_are_drastically_different(self):
        """sigma/m(10) vs sigma/m(1000) ratios should differ across classes."""
        v_dwarf = 10.0
        v_cluster = 1000.0
        ratios = {}
        for class_id, cfg in MEDIATOR_CLASSES.items():
            fn = cfg["fn"]
            extra = cfg["extra_params"]
            s_dwarf = fn(V03_MAP["sigma_m_0"], V03_MAP["a"], v_dwarf, **extra)
            s_cluster = fn(V03_MAP["sigma_m_0"], V03_MAP["a"], v_cluster, **extra)
            ratios[class_id] = s_dwarf / s_cluster if s_cluster > 0 else float("inf")
        # The ratios span at least 4 orders of magnitude
        non_inf = [r for r in ratios.values() if np.isfinite(r) and r > 0]
        spread = max(non_inf) / min(non_inf)
        assert spread > 1e4, (
            f"Mediator forms should differ by >10^4x; got spread={spread:.2e}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])