"""
Tests for solar_8b_cevns_real_data.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))


def test_sigma_m_at_v_low_zero_for_zero_input():
    """sigma/m should be 0 when sigma_m_0 = 0."""
    from solar_8b_cevns_real_data import sigma_m_at_v_low
    assert sigma_m_at_v_low(0.0, 0.5) == 0.0


def test_sigma_m_at_v_low_scales_correctly():
    """For a=1, sigma/m(v=30) = sigma_m_0 * (100/30)^1 = 3.33 * sigma_m_0."""
    from solar_8b_cevns_real_data import sigma_m_at_v_low, V_REF
    expected = 1.0 * (V_REF / 30.0) ** 1.0
    actual = sigma_m_at_v_low(1.0, 1.0)
    assert abs(actual - expected) / expected < 1e-6


def test_sidm_excess_zero_for_zero_input():
    """SIDM excess over SM should be 0 (SIDM doesn't contribute to CEvNS directly)."""
    from solar_8b_cevns_real_data import sidm_recoil_excess_fraction
    assert sidm_recoil_excess_fraction(0.0, 0.5) == 0.0


def test_sidm_excess_zero_for_lz_params():
    """SIDM excess should be 0 at LZ parameters (no DM-nucleon coupling in master)."""
    from solar_8b_cevns_real_data import sidm_recoil_excess_fraction
    assert sidm_recoil_excess_fraction(0.7, 0.16) == 0.0


def test_xenonnt_log_l_at_lz_finite():
    """XENONnT CEvNS log L should be finite at LZ parameters."""
    from solar_8b_cevns_real_data import loglike_xenonnt_8b_cevns
    ll = loglike_xenonnt_8b_cevns(0.7, 0.16)
    assert np.isfinite(ll)


def test_xenonnt_log_l_consistent_with_sm():
    """At zero SIDM, log L should reflect SM-vs-measurement consistency.

    SM prediction (1.16e-39) vs measured (1.1 +0.8 -0.5)e-39:
    SM is between measured -1σ and measured +1σ, so log L should be
    close to 0 (well within error bars).
    """
    from solar_8b_cevns_real_data import loglike_xenonnt_8b_cevns
    ll = loglike_xenonnt_8b_cevns(0.0, 0.5)
    assert abs(ll) < 0.5, (
        f"Expected |log L| < 0.5 (SM consistent with measurement), got {ll}"
    )


def test_dd_consistency_zero_below_threshold():
    """DD consistency log L should be 0 when sigma/m(v=30) < 0.5."""
    from solar_8b_cevns_real_data import loglike_dm_nucleon_consistency
    # sigma_m_0=0.05, a=0.5: sigma/m(v=30) = 0.05 * (100/30)^0.5 = 0.0913
    ll = loglike_dm_nucleon_consistency(0.05, 0.5)
    assert ll == 0.0


def test_dd_consistency_negative_above_threshold():
    """DD consistency log L should be negative when sigma/m(v=30) > 0.5."""
    from solar_8b_cevns_real_data import loglike_dm_nucleon_consistency
    # sigma_m_0=1.0, a=0: sigma/m(v=30) = 1.0 (above threshold)
    ll = loglike_dm_nucleon_consistency(1.0, 0.0)
    assert ll < 0.0


def test_real_data_constants():
    """Verify the XENONnT 8B CEvNS constants match PRL 133, 191002."""
    from solar_8b_cevns_real_data import (
        XENONNT_8B_FLUX_CM2_S,
        XENONNT_8B_XSEC_CM2,
        SM_8B_XSEC_XE_CM2,
    )
    assert abs(XENONNT_8B_FLUX_CM2_S - 4.7e6) < 1e3
    assert abs(XENONNT_8B_XSEC_CM2 - 1.1e-39) < 1e-42
    # SM prediction should be consistent with measured central value
    assert abs(SM_8B_XSEC_XE_CM2 - 1.16e-39) < 1e-42


def test_total_log_l_at_lz_is_mild_penalty():
    """Total log L at LZ parameters should be a mild penalty (< 1 sigma)."""
    from solar_8b_cevns_real_data import (
        loglike_xenonnt_8b_cevns,
        loglike_dm_nucleon_consistency,
    )
    ll_x = loglike_xenonnt_8b_cevns(0.7, 0.16)
    ll_d = loglike_dm_nucleon_consistency(0.7, 0.16)
    total = ll_x + ll_d
    assert total > -1.0, (
        f"Expected total log L > -1 (no strong tension), got {total}"
    )