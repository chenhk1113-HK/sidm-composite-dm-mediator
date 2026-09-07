"""
Tests for t90_v17_lz_time_series.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))


def test_lz_public_data_constants():
    """Verify the LZ public data constants match published numbers."""
    from t90_v17_lz_time_series import (
        LZ_EXPOSURE_KG_DAYS,
        LZ_LIVE_DAYS,
        LZ_OBSERVED_ENERGY_KEV,
        LZ_SIGNIFICANCE_GLOBAL_SIGMA,
    )
    assert LZ_LIVE_DAYS == 220  # from arXiv:2609.02823
    assert LZ_OBSERVED_ENERGY_KEV == 248.0  # the 248 keV event
    assert LZ_SIGNIFICANCE_GLOBAL_SIGMA == 2.6  # global significance
    # 2.84 tonne-years * 1000 kg/tonne * 365.25 days/year
    expected_exposure = 2.84 * 1000.0 * 365.25
    assert abs(LZ_EXPOSURE_KG_DAYS - expected_exposure) / expected_exposure < 1e-6


def test_magnetic_moment_predicts_1_event():
    """Magnetic-moment DM should predict ~1 event at LZ (by construction)."""
    from t90_v17_lz_time_series import n_events_magnetic_moment
    r = n_events_magnetic_moment()
    assert r['N_predicted'] == 1.0


def test_higgsino_inelastic_in_preferred_region():
    """Higgsino at delta ~ 350 keV should predict ~1 event."""
    from t90_v17_lz_time_series import n_events_higgsino_inelastic
    r = n_events_higgsino_inelastic(delta_keV=350)
    assert r['N_predicted'] == 1.0


def test_higgsino_inelastic_below_threshold():
    """Higgsino at delta < 200 keV should be kinematically forbidden."""
    from t90_v17_lz_time_series import n_events_higgsino_inelastic
    r = n_events_higgsino_inelastic(delta_keV=100)
    assert r['N_predicted'] == 0.0


def test_higgsino_inelastic_high_delta_tension():
    """Higgsino at delta > 400 keV would have been seen."""
    from t90_v17_lz_time_series import n_events_higgsino_inelastic
    r = n_events_higgsino_inelastic(delta_keV=600)
    assert r['N_predicted'] > 1.0  # in tension with null


def test_xe124_dec_zero_at_248keV():
    """124Xe DEC should predict ~0 events at 248 keV."""
    from t90_v17_lz_time_series import n_events_xe124_dec
    r = n_events_xe124_dec()
    assert r['N_predicted'] == 0.0


def test_solar_neutrino_below_unity():
    """Solar 8B neutrinos at 248 keV recoil should predict << 1 event."""
    from t90_v17_lz_time_series import n_events_solar_neutrino
    r = n_events_solar_neutrino()
    assert r['N_predicted'] < 1.0


def test_instrumental_at_published_level():
    """Instrumental background should be ~0.05 events per LZ published budget."""
    from t90_v17_lz_time_series import n_events_instrumental
    r = n_events_instrumental()
    assert 0.01 < r['N_predicted'] < 0.5


def test_poisson_log_likelihood_n_obs_1():
    """For N_obs=1, log L should be -N_pred + log(N_pred)."""
    from t90_v17_lz_time_series import poisson_log_likelihood
    import math
    n_pred = 2.0
    expected = -n_pred + math.log(n_pred)  # -log(1!) = 0
    actual = poisson_log_likelihood(1, n_pred)
    assert abs(actual - expected) < 1e-6


def test_posteriors_sum_to_unity():
    """Bayesian posteriors should sum to 1."""
    from t90_v17_lz_time_series import hypothesis_posteriors
    r = hypothesis_posteriors(n_obs=1)
    assert abs(sum(r['posteriors'].values()) - 1.0) < 1e-6


def test_hypotheses_tied_when_same_n_pred():
    """When two hypotheses predict the same N_events, posteriors should be equal."""
    from t90_v17_lz_time_series import hypothesis_posteriors
    n_pred = {'h1': 1.0, 'h2': 1.0, 'h3': 0.05}
    r = hypothesis_posteriors(n_obs=1, n_pred_dict=n_pred)
    assert abs(r['posteriors']['h1'] - r['posteriors']['h2']) < 1e-6


def test_instrumental_lower_posterior_than_signal():
    """The instrumental hypothesis (N_pred=0.05) should have lower posterior
    than a signal hypothesis (N_pred=1) for N_obs=1."""
    from t90_v17_lz_time_series import hypothesis_posteriors
    n_pred = {'signal': 1.0, 'instrumental': 0.05}
    r = hypothesis_posteriors(n_obs=1, n_pred_dict=n_pred)
    assert r['posteriors']['signal'] > r['posteriors']['instrumental']
