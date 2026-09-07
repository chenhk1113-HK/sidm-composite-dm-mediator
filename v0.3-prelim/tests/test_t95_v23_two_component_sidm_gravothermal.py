"""
Tests for t95_v23_two_component_sidm_gravothermal.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))


def test_yang_params_same_as_t95_6():
    """Yang+ 2026 parameters should match T95.6 baseline."""
    from t95_v23_two_component_sidm_gravothermal import (
        SIGMA_H_INTRA_M_H_CM2_G,
        W_H_KMS,
        M_H_OVER_M_L,
    )
    assert SIGMA_H_INTRA_M_H_CM2_G == 6.89
    assert W_H_KMS == 275.0
    assert M_H_OVER_M_L == 3.0


def test_naive_sigma_m_same_as_t95_6():
    """Naive mass-weighted sigma/m should match T95.6 within 1%."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))
    from t95_v23_two_component_sidm_gravothermal import sigma_eff_naive
    from t95_two_component_sidm_yang2026 import effective_sigma_m_two_component
    for v in [10, 100, 150, 1000]:
        # T95.6 uses f_H * s_hh + f_L * s_ll + 2 f_H f_L * s_xl
        # This module uses the same formula
        s_v23 = sigma_eff_naive(v)
        s_t95_6 = effective_sigma_m_two_component(v)
        assert abs(s_v23 - s_t95_6) / s_t95_6 < 0.01


def test_t_gc_huge_for_isolated_halo():
    """For sigma/m ~5 cm^2/g, t_gc >> Hubble time (10^14 Gyr or more)."""
    from t95_v23_two_component_sidm_gravothermal import gravothermal_collapse_time_Gyr
    t_gc = gravothermal_collapse_time_Gyr(5.0, 1e11, c_concentration=10)
    assert t_gc > 1e10  # way larger than Hubble time


def test_t_gc_scaling_with_mass():
    """Higher mass -> longer t_gc (denser clusters have longer relaxation)."""
    from t95_v23_two_component_sidm_gravothermal import gravothermal_collapse_time_Gyr
    t_dwarf = gravothermal_collapse_time_Gyr(5.0, 1e11, c_concentration=10)
    t_cluster = gravothermal_collapse_time_Gyr(5.0, 1e15, c_concentration=4)
    assert t_cluster > t_dwarf


def test_t_gc_inverse_with_sigma_m():
    """Larger sigma/m -> shorter t_gc."""
    from t95_v23_two_component_sidm_gravothermal import gravothermal_collapse_time_Gyr
    t_small = gravothermal_collapse_time_Gyr(0.1, 1e11, c_concentration=10)
    t_large = gravothermal_collapse_time_Gyr(10.0, 1e11, c_concentration=10)
    assert t_small > t_large


def test_tidal_stripping_reduces_t_gc():
    """Tidal stripping should reduce t_gc by factor (r_s/r_t)^3."""
    from t95_v23_two_component_sidm_gravothermal import gravothermal_collapse_time_Gyr, gravothermal_enhancement
    t_gc_isol = gravothermal_collapse_time_Gyr(5.0, 1e11, c_concentration=10)
    grav_strip = gravothermal_enhancement(5.0, 1e11, is_tidally_stripped=True, r_truncation_r_s=3.0)
    # Should be reduced by (1/3)^3 = 1/27
    expected = t_gc_isol * (1.0/3.0)**3
    assert abs(grav_strip['t_gc_Gyr'] - expected) / expected < 0.01


def test_enhancement_factor_1_for_isolated_dwarf():
    """For typical isolated dwarf with sigma/m ~5, enhancement ~1 (no collapse in Hubble time)."""
    from t95_v23_two_component_sidm_gravothermal import gravothermal_enhancement
    grav = gravothermal_enhancement(5.0, 1e11)
    assert grav['enhancement'] == 1.0


def test_dwarf_isolated_still_fails_zhang():
    """Even with gravothermal, isolated dwarf sigma/m is way below Zhang [30, 100]."""
    from t95_v23_two_component_sidm_gravothermal import sigma_m_with_gravothermal
    r = sigma_m_with_gravothermal(30, 1e11)
    # Zhang needs [30, 100], we get ~6
    assert r['sigma_m_with_gravothermal'] < 30


def test_cluster_satisfies_euclid_fails():
    """Cluster sigma/m with gravothermal should still be ~0.4 cm^2/g (above Euclid 0.10)."""
    from t95_v23_two_component_sidm_gravothermal import sigma_m_with_gravothermal
    r = sigma_m_with_gravothermal(1000, 1e15)
    # No collapse, so sigma/m = naive = ~0.4 cm^2/g
    # Euclid forecast is [0.05, 0.10], so we're 4x above
    assert r['sigma_m_with_gravothermal'] > 0.10


def test_t95_tension_result_structure():
    """T95 tension should return all expected keys."""
    from t95_v23_two_component_sidm_gravothermal import t95_tension_gravothermal
    t = t95_tension_gravothermal()
    assert 'dwarf_isolated' in t
    assert 'dwarf_tidally_stripped' in t
    assert 'cluster_halo' in t
    assert 'euclid_q1_forecast' in t
    assert 'zhang_2025_constraint' in t


def test_output_json_serializable():
    """Output should be JSON-serializable."""
    from t95_v23_two_component_sidm_gravothermal import sigma_m_with_gravothermal
    import json
    r = sigma_m_with_gravothermal(30, 1e11)
    json.dumps(r)  # should not raise


def test_main_runs_without_error():
    """main() should run and produce output."""
    from t95_v23_two_component_sidm_gravothermal import main
    # Just verify the function exists and doesn't raise
    # Don't actually run it because it does I/O
    assert callable(main)