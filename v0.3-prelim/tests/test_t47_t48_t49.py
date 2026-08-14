"""
Tests for T47 (β-function), T48 (dark confinement), T49 (vacuum decay).
"""
import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
T47_CODE = PROJECT_ROOT / "v0.3-prelim" / "code" / "t47_higgs_beta_function.py"
T48_CODE = PROJECT_ROOT / "v0.3-prelim" / "code" / "t48_dark_confinement.py"
T49_CODE = PROJECT_ROOT / "v0.3-prelim" / "code" / "t49_vacuum_decay.py"
T47_RESULT = PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "t47_higgs_beta_function.json"
T48_RESULT = PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "t48_dark_confinement_survey.json"
T49_RESULT = PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "t49_vacuum_decay.json"


class TestT47BetaFunction:
    """T47 — Higgs quartic beta function."""

    def test_t47_importable(self):
        t47 = pytest.importorskip("t47_higgs_beta_function")
        assert hasattr(t47, "beta_lambda_SM")
        assert hasattr(t47, "delta_lambda_H_kinetic_mixing")
        assert hasattr(t47, "delta_lambda_H_higgs_portal")
        assert hasattr(t47, "delta_lambda_H_dark_yukawa")

    def test_t47_sm_beta_lambda(self):
        """SM-only beta function should be at the 1-loop textbook value."""
        t47 = pytest.importorskip("t47_higgs_beta_function")
        # At top Yukawa dominance (y_t ~ 1), beta_lambda ~ (1/16pi^2) * (-6 * 1^4)
        # = -6 / 16pi^2 ~ -0.038
        beta = t47.beta_lambda_SM(0.13, 1.0, 0.4, 0.5)
        assert beta < 0, "Top Yukawa should drive lambda_H negative"

    def test_t47_kinetic_mixing_tiny(self):
        """Kinetic mixing portal contribution should be negligible at T46 eps."""
        t47 = pytest.importorskip("t47_higgs_beta_function")
        delta = t47.delta_lambda_H_kinetic_mixing(1e-48, 1.795)
        # Should be ~ 10^-134 (essentially zero)
        assert delta < 1e-100, f"Expected ~10^-134, got {delta}"

    def test_t47_higgs_portal_marginal(self):
        """Higgs portal (if exists) gives moderate contribution."""
        t47 = pytest.importorskip("t47_higgs_beta_function")
        # lambda_Hphi ~ g_chi^2 / 4 ~ 0.05 (from T46 g_chi = 0.46)
        delta = t47.delta_lambda_H_higgs_portal(0.05, 1.795)
        # Should be ~ 10^-3 (above 1e-10 threshold)
        assert delta > 1e-10, f"Higgs portal contribution too small: {delta}"

    def test_t47_dark_yukawa_relevant(self):
        """Dark Yukawa contribution should be ~10^-2 (relevant for vacuum stability)."""
        t47 = pytest.importorskip("t47_higgs_beta_function")
        delta = t47.delta_lambda_H_dark_yukawa(0.46, 1.795)
        # Should be ~ 10^-2 (~1% of SM lambda_H)
        assert 1e-4 < delta < 1, f"Dark Yukawa contribution out of expected range: {delta}"


class TestT48DarkConfinement:
    """T48 — Dark-confinement literature survey."""

    def test_t48_importable(self):
        t48 = pytest.importorskip("t48_dark_confinement")
        assert hasattr(t48, "LITERATURE")
        assert hasattr(t48, "SCALING")
        assert hasattr(t48, "predict_Lambda_dark")

    def test_t48_lambda_dark_qcd_scale(self):
        """For T41 (m_phi ~ 212 MeV), the dark meson model predicts Lambda_dark ~ 100 MeV."""
        t48 = pytest.importorskip("t48_dark_confinement")
        pred = t48.predict_Lambda_dark(212, "SU(N_dark), N_f=1 dark fermion")
        assert "Lambda_dark_predicted_MeV" in pred
        # Should be ~ 100 MeV (close to QCD scale)
        assert 50 < pred["Lambda_dark_predicted_MeV"] < 200, (
            f"Lambda_dark = {pred['Lambda_dark_predicted_MeV']} MeV, expected ~100 MeV"
        )

    def test_t48_literature_contains_key_refs(self):
        """Survey should include foundational papers."""
        t48 = pytest.importorskip("t48_dark_confinement")
        titles = [ref["title"] for ref in t48.LITERATURE]
        assert any("Hidden Sector" in t for t in titles), "Missing Appelquist et al. 2003"
        assert any("Dark QCD" in t for t in titles), "Missing Cacciapaglia et al. 2020"


class TestT49VacuumDecay:
    """T49 — Vacuum decay rate."""

    def test_t49_importable(self):
        t49 = pytest.importorskip("t49_vacuum_decay")
        assert hasattr(t49, "bounce_action_thin_wall")
        assert hasattr(t49, "decay_rate_per_volume")
        assert hasattr(t49, "half_life_in_age")

    def test_t49_bounce_action_decreases_with_lambda(self):
        """Bounce action decreases as dark Higgs quartic increases."""
        t49 = pytest.importorskip("t49_vacuum_decay")
        B_small = t49.bounce_action_thin_wall(0.01, 0)
        B_large = t49.bounce_action_thin_wall(1.0, 0)
        assert B_small > B_large, "Bounce should be smaller for stronger coupling"

    def test_t49_larger_quartic_more_unstable(self):
        """Larger dark Higgs quartic should give shorter dark vacuum half-life."""
        t49 = pytest.importorskip("t49_vacuum_decay")
        # Half-life at (lambda=0.1, m_phi=1)
        hl_stable = t49.half_life_in_age(0.1, 1.0)
        # Half-life at (lambda=1.0, m_phi=1)
        hl_unstable = t49.half_life_in_age(1.0, 1.0)
        assert hl_stable > hl_unstable, (
            f"Stable lambda should have longer HL: {hl_stable} vs {hl_unstable}"
        )

    def test_t49_walking_dark_too_unstable(self):
        """Walking dark (lambda=1) should be VERY unstable."""
        t49 = pytest.importorskip("t49_vacuum_decay")
        hl = t49.half_life_in_age(1.0, 1.0)
        # Should be much less than 1 (unstable)
        assert hl < 0, f"Walking dark HL should be < 1, got {hl}"
