"""Tests for Phase 4 6D particle-physics joint fit smoke test."""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
V03_CODE = PROJECT_ROOT / "v0.3-prelim" / "code"
sys.path.insert(0, str(V03_CODE))
sys.path.insert(0, str(PROJECT_ROOT))


class TestPhase4SmokeTest:
    """Verify the Phase 4 6D smoke test infrastructure."""

    def test_smoke_test_output_exists(self):
        """Output JSON file should exist after running."""
        out_path = PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "phase4_6d_smoke_test.json"
        assert out_path.exists(), f"Missing {out_path}"

    def test_smoke_test_output_structure(self):
        """Output JSON should have the expected structure."""
        out_path = PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "phase4_6d_smoke_test.json"
        data = json.loads(out_path.read_text())
        assert "test" in data
        assert data["test"] == "phase4_6d_smoke_test"
        assert "log_Z" in data
        assert "MAP" in data
        assert "MAP_physical" in data
        assert "t39_comparison" in data

    def test_log_z_is_negative(self):
        """log_Z should be a real number (negative for sub-dominant models)."""
        out_path = PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "phase4_6d_smoke_test.json"
        data = json.loads(out_path.read_text())
        assert isinstance(data["log_Z"], (int, float))
        # For Yukawa form, log_Z is expected to be more negative than T39
        # (per the publishable finding)
        assert data["log_Z"] < -10.0

    def test_map_has_six_parameters(self):
        """MAP should have 6 parameters (6D fit)."""
        out_path = PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "phase4_6d_smoke_test.json"
        data = json.loads(out_path.read_text())
        assert len(data["MAP"]) == 6
        # Parameter names from t41 docstring:
        # (log_m_phi_MeV, log_m_chi_GeV, g_chi, log_epsilon, log_alpha, log_xi)
        assert "log_m_phi_MeV" in data["MAP"]
        assert "log_m_chi_GeV" in data["MAP"]
        assert "g_chi" in data["MAP"]
        assert "log_epsilon" in data["MAP"]
        assert "log_alpha" in data["MAP"]
        assert "log_xi" in data["MAP"]

    def test_map_physical_has_consistent_units(self):
        """MAP physical values should be in expected unit ranges."""
        out_path = PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "phase4_6d_smoke_test.json"
        data = json.loads(out_path.read_text())
        phys = data["MAP_physical"]
        # m_phi_MeV in [10^-1, 10^4] from prior
        assert 0.1 <= phys["m_phi_MeV"] <= 10000
        # m_chi_GeV in [10^0.5, 10^3] from prior
        assert 3.16 <= phys["m_chi_GeV"] <= 1000
        # g_chi in [0.01, 2]
        assert 0.01 <= phys["g_chi"] <= 2.0

    def test_kill_criterion_triggered_in_raw_comparison(self):
        """Per AGENTS.md rule 11: kill criterion triggered in raw 4D vs 6D comparison.

        T39 4D: -2.94; T41 6D ~ -165. Delta_AIC = +328. Triggered.
        """
        out_path = PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "phase4_6d_smoke_test.json"
        data = json.loads(out_path.read_text())
        comp = data["t39_comparison"]
        assert comp["kill_criterion_triggered"] is True
        assert comp["delta_aic"] > 0
        # But caveats are documented
        assert "honest_caveats" in data
        assert len(data["honest_caveats"]) >= 3

    def test_quantiles_have_three_values(self):
        """Quantiles should have 16/50/84 percentiles."""
        out_path = PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "phase4_6d_smoke_test.json"
        data = json.loads(out_path.read_text())
        q = data["quantiles"]
        assert len(q["log_epsilon_16_50_84"]) == 3
        assert len(q["log_alpha_16_50_84"]) == 3
        # 16 < 50 < 84
        assert q["log_epsilon_16_50_84"][0] < q["log_epsilon_16_50_84"][1]
        assert q["log_epsilon_16_50_84"][1] < q["log_epsilon_16_50_84"][2]


class TestT41Infrastructure:
    """Verify T41 6D joint fit infrastructure is callable."""

    def test_loglike_joint_importable(self):
        """T41 loglike_joint should be importable."""
        from t41_mediator_mass_joint_fit import loglike_joint, prior_transform_6
        assert callable(loglike_joint)
        assert callable(prior_transform_6)

    def test_loglike_joint_returns_finite_at_map(self):
        """loglike_joint should return finite value at T41 MAP from JSON."""
        from t41_mediator_mass_joint_fit import loglike_joint
        out_path = PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "phase4_6d_smoke_test.json"
        data = json.loads(out_path.read_text())
        MAP = data["MAP"]
        theta = [MAP["log_m_phi_MeV"], MAP["log_m_chi_GeV"], MAP["g_chi"],
                 MAP["log_epsilon"], MAP["log_alpha"], MAP["log_xi"]]
        ll = loglike_joint(theta)
        assert ll > -np.inf  # Should be finite at MAP

    def test_loglike_joint_returns_neginf_outside_priors(self):
        """loglike_joint should return -inf for out-of-prior parameters."""
        from t41_mediator_mass_joint_fit import loglike_joint
        # Way outside prior range
        theta_bad = [10.0, 10.0, 10.0, 10.0, 10.0, 10.0]
        ll = loglike_joint(theta_bad)
        assert ll == -np.inf
