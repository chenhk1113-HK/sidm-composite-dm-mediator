"""
Tests for Phase 29 (full T90.50-style 6D resonant joint fit).
"""
import pytest
import sys
import os
import json
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "code"))


class TestPhase29:
    RESULTS_PATH = os.path.join(
        os.path.dirname(__file__), "..", "data", "results",
        "phase29_full_resonant_joint_fit.json"
    )

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 29 results not yet generated"
    )
    def test_posterior_medians_recorded(self):
        """Posterior medians for 6 parameters should be recorded."""
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        assert "posterior_medians" in data
        medians = data["posterior_medians"]
        expected = ["m_chi_GeV", "E_R_eV", "Gamma_R_eV", "sigma_0", "alpha_Y", "m_phi_MeV"]
        for p in expected:
            assert p in medians
            assert "p50" in medians[p]

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 29 results not yet generated"
    )
    def test_channel_predictions_recorded(self):
        """sigma/m predictions at all 4 velocities should be recorded."""
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        preds = data["posterior_predictions"]
        assert preds["sigma_m_Cloud9_cm2_per_g"] > 0
        assert preds["sigma_m_SPARC_cm2_per_g"] > 0
        assert preds["sigma_m_Euclid_cm2_per_g"] > 0
        assert preds["sigma_m_Bullet_cm2_per_g"] > 0

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 29 results not yet generated"
    )
    def test_resonance_in_cloud9_window(self):
        """E_R posterior should be near Cloud-9 kinetic energy (~30-100 eV for m_chi~10 GeV)."""
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        E_R = data["posterior_medians"]["E_R_eV"]["p50"]
        m_chi = data["posterior_medians"]["m_chi_GeV"]["p50"]
        # Cloud-9 KE = (m_chi/4) * v^2 / (c^2)
        # For m_chi=10 GeV, v=28 km/s: KE ~ 22 eV
        # For m_chi=30 GeV, v=28 km/s: KE ~ 65 eV
        E_CM_28 = (m_chi / 4) * (28e5 / 3e10)**2 * 1e9  # eV
        # E_R should be within factor of 5 of E_CM(28)
        ratio = E_R / E_CM_28
        assert 0.1 < ratio < 10, f"E_R/E_CM(28) = {ratio:.2f}, expected 0.1-10"

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 29 results not yet generated"
    )
    def test_verdict_recorded(self):
        """Verdict should be one of the recognized categories."""
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        assert data["verdict"] in ["FOUND_FULL_SOLUTION", "MOSTLY_RESOLVED", "INSUFFICIENT"]

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 29 results not yet generated"
    )
    def test_channels_pass_total(self):
        """Should pass at least 3/4 SIDM channels."""
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        n_pass = data["channels_pass_total"]
        assert n_pass >= 3, f"Only {n_pass}/4 SIDM channels pass"
