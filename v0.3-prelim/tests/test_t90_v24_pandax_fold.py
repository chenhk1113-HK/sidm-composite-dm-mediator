"""Tests for the T90.24 PandaX efficiency/background fold."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))

from t90_v24_pandax_fold import (  # noqa: E402
    PANDAX_PUBLISHED,
    magnetic_signal_spectrum,
    pandax_selection_efficiency,
    profile_poisson_gaussian_bkg,
    fold_signal_into_pandax,
)


def test_published_background_components_match_table():
    components = PANDAX_PUBLISHED["background_components_below_nr_median"]
    assert abs(sum(components.values()) - PANDAX_PUBLISHED["background_below_nr_median"]) < 0.6


def test_selection_efficiency_is_bounded_and_rises():
    e = np.array([1.0, 5.0, 20.0, 100.0])
    eff = pandax_selection_efficiency(e)
    assert np.all((eff >= 0.0) & (eff <= 1.0))
    assert np.all(np.diff(eff) >= 0.0)


def test_folded_signal_is_below_raw_signal():
    energy = np.linspace(1.0, 270.0, 2000)
    raw = magnetic_signal_spectrum(energy, mu_x_mu_n=6.10e-8, m_chi_gev=1000.0)
    folded = fold_signal_into_pandax(energy, raw)
    assert folded["raw_5_270"] > folded["selected_5_270"] > 0.0
    assert folded["selected_nr_band_5_270"] < folded["selected_5_270"]


def test_profile_likelihood_penalizes_large_signal():
    bg_only = profile_poisson_gaussian_bkg(
        n_obs=24, signal=0.0, background=20.5, background_sigma=2.5
    )
    large_signal = profile_poisson_gaussian_bkg(
        n_obs=24, signal=250.0, background=20.5, background_sigma=2.5
    )
    assert large_signal["log_l"] < bg_only["log_l"]
    assert large_signal["delta_log_l_vs_background"] < 0.0


def test_live_fold_has_auditable_counts():
    result = fold_signal_into_pandax(
        np.linspace(1.0, 270.0, 2000),
        magnetic_signal_spectrum(
            np.linspace(1.0, 270.0, 2000), mu_x_mu_n=6.10e-8, m_chi_gev=1000.0
        ),
    )
    assert set(result) >= {
        "raw_5_50",
        "selected_5_50",
        "raw_5_270",
        "selected_5_270",
        "selected_nr_band_5_270",
    }
    assert result["raw_5_50"] > result["selected_5_50"]
