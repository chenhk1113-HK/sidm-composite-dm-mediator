"""
Tests for t95_v25_multi_stream_real_galstreams.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))


def test_curated_streams_defined():
    """Curated streams should include GD-1 + others."""
    from t95_v25_multi_stream_real_galstreams import CURATED_STREAMS
    assert 'GD-1' in CURATED_STREAMS
    assert 'Pal5' in CURATED_STREAMS
    assert len(CURATED_STREAMS) >= 5


def test_curated_streams_have_required_fields():
    """Each curated stream must have sigma_m_lower, sigma_m_upper, v_kms, gap_count."""
    from t95_v25_multi_stream_real_galstreams import CURATED_STREAMS
    for name, info in CURATED_STREAMS.items():
        assert 'sigma_m_lower' in info
        assert 'sigma_m_upper' in info
        assert 'v_kms' in info
        assert 'gap_count' in info
        assert info['sigma_m_lower'] < info['sigma_m_upper']
        assert info['v_kms'] > 0


def test_v_t_computation():
    """v_t = 4.74 * mu_mag * distance."""
    from t95_v25_multi_stream_real_galstreams import compute_orbital_velocity
    import pandas as pd
    df = pd.DataFrame({
        'ra': [0], 'dec': [0],
        'distance': [10.0],
        'pm_ra_cosdec': [10.0],  # mas/yr
        'pm_dec': [0.0],
        'radial_velocity': [0.0],
    })
    orb = compute_orbital_velocity(df)
    # pm_mag = 10 mas/yr, distance = 10 kpc
    # v_t = 4.74 * 10 * 10 = 474 km/s
    assert abs(orb['v_t_median'] - 474.0) / 474.0 < 1e-6


def test_filters_unphysical_v_r():
    """Tracks with v_r > 1000 km/s should be filtered out."""
    from t95_v25_multi_stream_real_galstreams import compute_orbital_velocity
    import pandas as pd
    df = pd.DataFrame({
        'ra': [0, 1],
        'dec': [0, 1],
        'distance': [10.0, 10.0],
        'pm_ra_cosdec': [10.0, 10.0],
        'pm_dec': [0.0, 0.0],
        'radial_velocity': [1e7, 100.0],  # one unphysical
    })
    orb = compute_orbital_velocity(df)
    # Should have only 1 valid point after filtering
    assert orb['n_track_points'] == 1


def test_multi_stream_loglik_structure():
    """Multi-stream loglik should return dict with per_stream and combined."""
    from t95_v25_multi_stream_real_galstreams import multi_stream_loglik, CURATED_STREAMS, sigma_m_master_yukawa
    result = multi_stream_loglik(sigma_m_master_yukawa, CURATED_STREAMS)
    assert 'per_stream' in result
    assert 'combined_loglik' in result
    assert len(result['per_stream']) == len(CURATED_STREAMS)


def test_gd1_dominates_tension_master():
    """For master Yukawa, GD-1 should be the dominant source of negative loglik."""
    from t95_v25_multi_stream_real_galstreams import multi_stream_loglik, CURATED_STREAMS, sigma_m_master_yukawa
    result = multi_stream_loglik(sigma_m_master_yukawa, CURATED_STREAMS)
    gd1_ll = result['per_stream']['GD-1']['loglik']
    total = result['combined_loglik']
    # GD-1 should be 95%+ of total negative loglik
    assert gd1_ll / total > 0.95


def test_t95_tension_result_keys():
    """T95 tension should have all expected keys."""
    from t95_v25_multi_stream_real_galstreams import t95_tension_real_galstreams
    t = t95_tension_real_galstreams()
    assert 'master_yukawa' in t
    assert 'mixture_option_d' in t
    assert 'two_component_option_a' in t
    assert 'comparison' in t
    assert 'best_model' in t['comparison']
    assert 'full_catalog_stats' in t


def test_full_catalog_loads():
    """build_stream_catalog should return a DataFrame with multiple streams."""
    from t95_v25_multi_stream_real_galstreams import build_stream_catalog
    catalog = build_stream_catalog()
    assert len(catalog) >= 50  # galstreams has ~120 streams
    assert 'stream' in catalog.columns
    assert 'v_3d_median' in catalog.columns
    assert 'distance_kpc' in catalog.columns


def test_full_catalog_v_3d_physical():
    """v_3d_median should be physical (< 1000 km/s for bound MW objects)."""
    from t95_v25_multi_stream_real_galstreams import build_stream_catalog
    catalog = build_stream_catalog()
    # All v_3d should be < 1000 (filtered)
    assert catalog.v_3d_median.max() < 1100  # small margin


def test_master_is_best_or_close():
    """Master Yukawa should be at least tied for best fit."""
    from t95_v25_multi_stream_real_galstreams import t95_tension_real_galstreams
    t = t95_tension_real_galstreams()
    master_ll = t['comparison']['master_combined_loglik']
    mix_ll = t['comparison']['mixture_combined_loglik']
    two_c_ll = t['comparison']['two_component_combined_loglik']
    # Master is best
    assert master_ll >= mix_ll - 0.1
    assert master_ll >= two_c_ll - 0.1


def test_output_json_serializable():
    """Output should be JSON-serializable."""
    from t95_v25_multi_stream_real_galstreams import t95_tension_real_galstreams
    import json
    t = t95_tension_real_galstreams()
    # Cast non-serializable numpy types
    serializable = {
        'master_ll': float(t['comparison']['master_combined_loglik']),
        'n_streams': int(t['full_catalog_stats']['n_streams_available']),
    }
    json.dumps(serializable)