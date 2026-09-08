"""
Tests for t112, t113, t114 — Door-B next-round actions.

T112: high-resolution 8D dynesty with tighter delta prior (50-200 keV).
T113: event-rate forecasts at T108 MAP for next-round experiments.
T114: ¹²⁴Xe DEC charge-yield systematic study.

Tests pin:
  - Prior ranges for T112 (nlive, delta range)
  - T113 forecast structure and assumptions
  - T114 charge-yield scan outputs
  - Cross-references between the three
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
CODE_DIR = SCRIPT_DIR.parent / "code"
ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(CODE_DIR))

from t112_highres_8d_dynesty import LOG_DELTA_KEV_RANGE_T112
from t113_event_rate_forecasts import T108_MAP, EXPERIMENTS, predicted_events
from t114_xe124_dec_systematic import (
    XE124_DEC_Q_VALUE_KEV,
    LZ_248_KEV_WINDOW,
    LZ_124XE_DEC_BACKGROUND_PER_TONNE_YEAR,
    significance_with_charge_yield,
)


def _approx(x, atol=1e-6):
    return abs(x) < atol


class TestT112DeltaPrior:
    """Pin the tighter delta prior in T112."""

    def test_t112_delta_range(self):
        """T112 delta prior is [50, 200] keV (Berlin & Ferraro motivated)."""
        lo, hi = LOG_DELTA_KEV_RANGE_T112
        # log10(50) ≈ 1.7, log10(200) ≈ 2.3
        assert _approx(lo - 1.7, atol=0.01)
        assert _approx(hi - 2.3, atol=0.01)
        # Verify physical range
        assert 10 ** lo >= 49.0
        assert 10 ** lo <= 51.0
        assert 10 ** hi >= 199.0
        assert 10 ** hi <= 201.0

    def test_t112_prior_is_tighter_than_t108(self):
        """T112 prior on delta is strictly tighter than T108's [1, 1000] keV."""
        t112_lo, t112_hi = LOG_DELTA_KEV_RANGE_T112
        # T108: [0, 3.0] in log10 (1 to 1000 keV)
        # T112: [1.7, 2.3] in log10 (50 to 200 keV)
        assert t112_lo > 0.0  # T112 lower > T108 lower
        assert t112_hi < 3.0  # T112 upper < T108 upper


class TestT113Forecasts:
    """Test event-rate forecasts."""

    def test_t108_map_is_loaded(self):
        """T108 MAP point is loaded."""
        assert "m_chi_GeV" in T108_MAP
        assert "delta_keV" in T108_MAP
        assert "sigma_PortalB_cm2" in T108_MAP
        assert 130 < T108_MAP["m_chi_GeV"] < 145
        assert 90 < T108_MAP["delta_keV"] < 110
        assert 1e-43 < T108_MAP["sigma_PortalB_cm2"] < 1e-41

    def test_experiments_dict(self):
        """Four experiments are defined."""
        assert len(EXPERIMENTS) == 4
        assert "LZ_Run4_2027_2028" in EXPERIMENTS
        assert "PandaX-4T_Run3_2026_2027" in EXPERIMENTS
        assert "XENONnT_S2only_2027" in EXPERIMENTS
        assert "DarkSide-20k_2028" in EXPERIMENTS

    def test_predicted_events_function(self):
        """predicted_events returns positive float."""
        for exp_name, exp in EXPERIMENTS.items():
            n = predicted_events(
                exposure_tonne_year=exp["exposure_tonne_year"],
                sigma_cm2=T108_MAP["sigma_PortalB_cm2"],
                m_chi_GeV=T108_MAP["m_chi_GeV"],
                target=exp["target"],
            )
            assert n > 0
            assert isinstance(n, float)

    def test_argon_form_factor_smaller(self):
        """Argon target gives fewer events than xenon at same exposure."""
        n_xe = predicted_events(20, 1e-42, 138, "xenon")
        n_ar = predicted_events(20, 1e-42, 138, "argon")
        assert n_ar < n_xe  # argon form factor 0.3 < xenon 1.0

    def test_darkside_highest_exposure(self):
        """DarkSide-20k has highest exposure."""
        max_exp = max(e["exposure_tonne_year"] for e in EXPERIMENTS.values())
        assert EXPERIMENTS["DarkSide-20k_2028"]["exposure_tonne_year"] == max_exp


class TestT114ChargeYield:
    """Test ¹²⁴Xe DEC charge-yield systematic."""

    def test_xe124_dec_q_value(self):
        """¹²⁴Xe DEC Q-value is in LZ 248 keV window."""
        assert XE124_DEC_Q_VALUE_KEV > 200
        assert XE124_DEC_Q_VALUE_KEV < 300

    def test_lz_window_pins_248(self):
        """LZ window is [200, 300] keV."""
        assert LZ_248_KEV_WINDOW == (200.0, 300.0)

    def test_background_rate_positive(self):
        """¹²⁴Xe DEC background rate is positive."""
        assert LZ_124XE_DEC_BACKGROUND_PER_TONNE_YEAR > 0

    def test_significance_decreases_with_charge_yield(self):
        """Higher charge-yield → more ¹²⁴Xe DEC background → lower DM significance."""
        sig_0 = significance_with_charge_yield(0.0)
        sig_1 = significance_with_charge_yield(1.0)
        assert sig_0 > sig_1  # higher charge-yield = lower DM significance

    def test_significance_at_lz_default(self):
        """At LZ default (charge_yield=1.0), significance is positive."""
        sig = significance_with_charge_yield(1.0)
        assert sig > 0
        assert sig < 5  # not too high

    def test_significance_at_zero_charge_yield_higher(self):
        """At charge_yield=0 (S1-only, easy rejection), significance is higher."""
        sig_0 = significance_with_charge_yield(0.0)
        sig_1 = significance_with_charge_yield(1.0)
        # Drop when charge-yield is treated as free
        assert sig_0 - sig_1 > 0.1  # meaningful drop


class TestOutputs:
    """Verify the actual output files exist and have correct structure."""

    def test_t113_output_structure(self):
        """T113 output JSON exists and has expected structure."""
        out_path = ROOT / "v0.3-prelim" / "outputs" / "t95" / "t113_event_rate_forecasts.json"
        if not out_path.exists():
            import pytest
            pytest.skip(f"T113 output not yet produced at {out_path}")
        with open(out_path) as f:
            result = json.load(f)
        assert "T108_MAP_used" in result
        assert "forecasts" in result
        assert "caveats" in result
        # Reviewer suggestions addressed
        assert "§3(a)" in result["description"]
        assert "§3(c)" in result["description"]
        # All 4 experiments
        assert len(result["forecasts"]) == 4

    def test_t114_output_structure(self):
        """T114 output JSON exists and has expected structure."""
        out_path = ROOT / "v0.3-prelim" / "outputs" / "t95" / "t114_xe124_dec_systematic.json"
        if not out_path.exists():
            import pytest
            pytest.skip(f"T114 output not yet produced at {out_path}")
        with open(out_path) as f:
            result = json.load(f)
        assert "charge_yield_scan" in result
        assert "xe124_dec_properties" in result
        assert "drop_in_significance_when_free" in result
        # Reviewer suggestion addressed
        assert "§4(b)" in result["description"]


class TestT112Output:
    """Verify T112 output if it exists."""

    def test_t112_output_structure_if_exists(self):
        """If T112 ran, check output structure."""
        out_path = ROOT / "v0.3-prelim" / "outputs" / "t95" / "t112_highres_8d_dynesty.json"
        if not out_path.exists():
            import pytest
            pytest.skip(f"T112 output not yet produced (running in background)")
        with open(out_path) as f:
            result = json.load(f)
        assert "log_Z" in result
        assert "log_Z_err" in result
        assert result["nlive"] == 2000
        assert result["delta_prior_range_keV"] == [50.0, 200.0]
        # Reviewer suggestions addressed
        assert "§1(a)" in result["description"]
        assert "§1(c)" in result["description"]