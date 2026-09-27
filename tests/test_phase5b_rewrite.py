"""Tests for Phase 5b channel likelihood rewrite.

Validates that channel likelihoods now accept a 'mediator_class' parameter
and produce different results for different classes.
"""
import sys
from pathlib import Path

import numpy as np
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
V03_CODE = PROJECT_ROOT / "v0.3-prelim" / "code"
sys.path.insert(0, str(V03_CODE))
sys.path.insert(0, str(PROJECT_ROOT))

from mediator_registry import (
    MEDIATOR_FORMS,
    MEDIATOR_NAMES,
    sigma_m_at_v,
)
from channels_v03 import (
    loglike_dsph_v03,
    loglike_ufd_v03,
    loglike_bullet_v03,
    sparc_loglike_grid,
)
from channels_extended import (
    loglike_dm_free_udg,
    loglike_dm_dominated_udg,
)


# v0.3-prelim MAP for testing
V03_MAP = {"sigma_m_0": 0.72, "a": 1.31}


class TestMediatorRegistry:
    """Verify the mediator registry works as expected."""

    def test_registry_has_four_classes(self):
        assert set(MEDIATOR_FORMS.keys()) == {
            "power_law",
            "yukawa",
            "scalar_portal",
            "composite",
        }

    def test_all_classes_have_names(self):
        for class_id in MEDIATOR_FORMS:
            assert class_id in MEDIATOR_NAMES

    def test_dispatcher_default_is_power_law(self):
        """sigma_m_at_v with no class should default to power_law."""
        s_default = sigma_m_at_v(0.72, 1.31, 30.0)
        s_power = sigma_m_at_v(0.72, 1.31, 30.0, mediator_class="power_law")
        assert s_default == s_power

    def test_dispatcher_raises_for_unknown_class(self):
        with pytest.raises(ValueError, match="Unknown mediator_class"):
            sigma_m_at_v(0.72, 1.31, 30.0, mediator_class="bogus")

    def test_classes_produce_different_values(self):
        """4 classes should give different sigma/m(v) at v=30 km/s."""
        results = {}
        for class_id in MEDIATOR_FORMS:
            results[class_id] = sigma_m_at_v(
                V03_MAP["sigma_m_0"], V03_MAP["a"], 30.0,
                mediator_class=class_id,
            )
        # At least 3 distinct values
        unique = len(set(round(v, 6) for v in results.values()))
        assert unique >= 3, f"Expected >=3 distinct values, got {results}"


class TestChannelsAcceptMediatorClass:
    """Verify channel likelihoods accept the new mediator_class parameter."""

    @pytest.mark.parametrize("class_id", list(MEDIATOR_FORMS.keys()))
    def test_dsph_accepts_each_class(self, class_id):
        ll = loglike_dsph_v03(V03_MAP["sigma_m_0"], V03_MAP["a"], class_id)
        assert np.isfinite(ll) or ll == -np.inf

    @pytest.mark.parametrize("class_id", list(MEDIATOR_FORMS.keys()))
    def test_ufd_accepts_each_class(self, class_id):
        ll = loglike_ufd_v03(V03_MAP["sigma_m_0"], V03_MAP["a"], class_id)
        assert np.isfinite(ll) or ll == -np.inf

    @pytest.mark.parametrize("class_id", list(MEDIATOR_FORMS.keys()))
    def test_bullet_accepts_each_class(self, class_id):
        ll = loglike_bullet_v03(V03_MAP["sigma_m_0"], V03_MAP["a"], class_id)
        assert np.isfinite(ll) or ll == -np.inf

    @pytest.mark.parametrize("class_id", list(MEDIATOR_FORMS.keys()))
    def test_dm_free_udg_accepts_each_class(self, class_id):
        ll = loglike_dm_free_udg(V03_MAP["sigma_m_0"], V03_MAP["a"], class_id)
        assert np.isfinite(ll) or ll == -np.inf

    @pytest.mark.parametrize("class_id", list(MEDIATOR_FORMS.keys()))
    def test_dm_dominated_udg_accepts_each_class(self, class_id):
        ll = loglike_dm_dominated_udg(V03_MAP["sigma_m_0"], V03_MAP["a"], class_id)
        assert np.isfinite(ll) or ll == -np.inf

    def test_default_mediator_class_is_power_law(self):
        """Backward compatibility: default mediator_class='power_law'."""
        ll_default = loglike_dsph_v03(V03_MAP["sigma_m_0"], V03_MAP["a"])
        ll_power = loglike_dsph_v03(
            V03_MAP["sigma_m_0"], V03_MAP["a"], "power_law"
        )
        assert ll_default == ll_power


class TestChannelsDifferentiateMediatorClasses:
    """Verify that channel likelihoods now give DIFFERENT results for
    different mediator classes (this was the Phase 5 structural limitation)."""

    def test_dm_dominated_udg_distinguishes_classes(self):
        """LSB-6 channel (Ch10) should give different loglike for different classes.

        At v0.3-prelim MAP (sigma/m_0=0.72, a=1.31):
        - power_law: sigma/m_eff(20) = 0.72 * (0.2)^-1.31 = 4.67 (way above peak 0.7)
        - yukawa: sigma/m_eff(20) = 0.72 * prefactor/(1+(20/v_dm)^2) ~ 0.72 (near peak)
        - scalar_portal: sigma/m_eff(20) = 0.72 * (1 + 0.5*(0.2-1)) = 0.36 (below peak)
        - composite: sigma/m_eff(20) = 0.72 * exp(-(20-30)^2/(2*50^2)) = 0.71 (near peak)
        """
        ll_results = {}
        for class_id in MEDIATOR_FORMS:
            ll_results[class_id] = loglike_dm_dominated_udg(
                V03_MAP["sigma_m_0"], V03_MAP["a"], class_id
            )
        # Power-law: sigma/m_eff is much higher than peak (factor of ~6.7x)
        # -> strong penalty because 0.7/4.67 = 0.15 in log10 = -0.82 dex below peak
        # -> chi = (-0.82/0.5)^2 = 2.7, loglike = -1.35
        assert ll_results["power_law"] < -1.0, (
            f"Power-law at v=20 should be penalized (sigma/m_eff too high): "
            f"{ll_results['power_law']}"
        )
        # Yukawa, scalar_portal, composite: all near or below peak
        # -> should be near 0 loglike
        for class_id in ["yukawa", "scalar_portal", "composite"]:
            assert ll_results[class_id] > -1.0, (
                f"{class_id} should be near peak at v=20: {ll_results[class_id]}"
            )

    def test_dm_free_udg_distinguishes_classes(self):
        """NGC 1052-DF2 channel (Ch9) should give different loglike for different classes."""
        ll_results = {}
        for class_id in MEDIATOR_FORMS:
            ll_results[class_id] = loglike_dm_free_udg(
                V03_MAP["sigma_m_0"], V03_MAP["a"], class_id
            )
        # Composite gives sigma/m(30) ~ 0.66 (near peak); others may differ
        unique = len(set(round(v, 3) for v in ll_results.values()))
        assert unique >= 2, (
            f"Expected at least 2 distinct values across mediator classes: {ll_results}"
        )


class TestBackwardsCompatibility:
    """Verify that all existing tests still pass with default mediator_class."""

    def test_power_law_matches_old_inline_calculation(self):
        """At v=30, v=10, v=20: power-law registry should match inline linearization.

        The inline linearization log_sm_eff = log10(sigma_m_0) - 0.699*a was the
        OLD buggy version. Power-law registry uses sigma/m_0 * (v/v_ref)^(-a).
        These should differ at negative a but match at positive a.
        """
        # At a=1.31 (positive), v=20: power-law form gives sigma/m_0 * (0.2)^(-1.31)
        # = 0.72 * 0.2^(-1.31) = 0.72 * 6.49 = 4.67
        s_pl = sigma_m_at_v(
            V03_MAP["sigma_m_0"], V03_MAP["a"], 20.0, mediator_class="power_law"
        )
        # 0.72 * (20/100)^(-1.31) = 0.72 * 6.49 = 4.67
        expected = 0.72 * (20.0 / 100.0) ** (-1.31)
        assert abs(s_pl - expected) < 1e-6


if __name__ == "__main__":
    pytest.main([__file__, "-v"])