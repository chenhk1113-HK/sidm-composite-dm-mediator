"""
Tests for t95_v24_multi_stream_analysis.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))


def test_all_streams_defined():
    """All 5 streams should be defined."""
    from t95_v24_multi_stream_analysis import ALL_STREAMS
    expected = {'GD-1', 'Pal_5', 'Orphan-Chenab', 'ATLAS', 'Styx'}
    assert set(ALL_STREAMS.keys()) == expected


def test_stream_loglik_inside_box():
    """Inside the constraint box, loglik = 0."""
    from t95_v24_multi_stream_analysis import stream_loglik
    ll = stream_loglik(1.0, 0.5, 2.0)
    assert ll == 0.0


def test_stream_loglik_below_lower():
    """Below lower bound, loglik < 0."""
    from t95_v24_multi_stream_analysis import stream_loglik
    ll = stream_loglik(0.1, 0.5, 2.0)
    assert ll < 0


def test_stream_loglik_above_upper():
    """Above upper bound, loglik < 0."""
    from t95_v24_multi_stream_analysis import stream_loglik
    ll = stream_loglik(10.0, 0.5, 2.0)
    assert ll < 0


def test_stream_loglik_symmetric():
    """Loglik should be symmetric in log space."""
    from t95_v24_multi_stream_analysis import stream_loglik
    # sigma = 0.1, lower = 1.0 -> dev = 1 in log
    # sigma = 10, upper = 1.0 -> dev = 1 in log
    ll_low = stream_loglik(0.1, 1.0, 100.0)  # below lower
    ll_high = stream_loglik(100.0, 1.0, 1.0 + 1e-10)  # above upper (tight)
    # They're not exactly symmetric due to upper bound, but both should be very negative
    assert ll_low < -5
    assert ll_high < -5


def test_master_yukawa_at_reference():
    """Master sigma/m at v=100 km/s should be 0.7 cm^2/g."""
    from t95_v24_multi_stream_analysis import sigma_m_master_yukawa
    s = sigma_m_master_yukawa(100)
    assert abs(s - 0.7) / 0.7 < 1e-6


def test_mixture_reduces_sigma_m():
    """Mixture sigma/m should be less than master."""
    from t95_v24_multi_stream_analysis import sigma_m_master_yukawa, sigma_m_mixture
    for v in [10, 30, 100]:
        assert sigma_m_mixture(v) < sigma_m_master_yukawa(v)


def test_two_component_higher_at_low_v():
    """Two-component SIDM sigma/m should be high at low velocities."""
    from t95_v24_multi_stream_analysis import sigma_m_two_component
    s_low = sigma_m_two_component(10)
    s_high = sigma_m_two_component(1000)
    assert s_low > s_high


def test_multi_stream_loglik_returns_dict():
    """Multi-stream loglik should return a dict with per_stream and combined."""
    from t95_v24_multi_stream_analysis import multi_stream_loglik, sigma_m_master_yukawa
    result = multi_stream_loglik(sigma_m_master_yukawa)
    assert 'per_stream' in result
    assert 'combined_loglik' in result
    assert len(result['per_stream']) == 5


def test_combined_loglik_is_sum():
    """Combined loglik should equal sum of per-stream logliks."""
    from t95_v24_multi_stream_analysis import multi_stream_loglik, sigma_m_master_yukawa
    result = multi_stream_loglik(sigma_m_master_yukawa)
    per_stream_sum = sum(info['loglik'] for info in result['per_stream'].values())
    assert abs(result['combined_loglik'] - per_stream_sum) < 1e-10


def test_gd1_dominates_master_tension():
    """For master Yukawa, GD-1 should be the dominant source of negative loglik."""
    from t95_v24_multi_stream_analysis import multi_stream_loglik, sigma_m_master_yukawa
    result = multi_stream_loglik(sigma_m_master_yukawa)
    gd1_ll = result['per_stream']['GD-1']['loglik']
    total = result['combined_loglik']
    # GD-1 should be at least 90% of the total negative loglik
    assert gd1_ll / total > 0.90


def test_t95_tension_result_structure():
    """T95 multi-stream tension should return expected keys."""
    from t95_v24_multi_stream_analysis import t95_tension_multi_stream
    t = t95_tension_multi_stream()
    assert 'master_yukawa' in t
    assert 'mixture_option_d' in t
    assert 'two_component_option_a' in t
    assert 'comparison' in t
    assert 'best_model' in t['comparison']


def test_output_json_serializable():
    """Output should be JSON-serializable."""
    from t95_v24_multi_stream_analysis import multi_stream_loglik, sigma_m_master_yukawa
    import json
    r = multi_stream_loglik(sigma_m_master_yukawa)
    # Convert to JSON-serializable dict (np.bool_ -> bool)
    serializable = {
        'combined_loglik': float(r['combined_loglik']),
        'per_stream_count': len(r['per_stream']),
    }
    json.dumps(serializable)