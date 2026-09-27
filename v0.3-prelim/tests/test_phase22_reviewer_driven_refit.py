"""
Tests for Phase 22 reviewer-driven refit.
"""
import pytest
import sys
import os
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "code"))


class TestPhase22:
    RESULTS_PATH = os.path.join(
        os.path.dirname(__file__), "..", "data", "results",
        "phase22_reviewer_driven_refit.json"
    )

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 22 results not yet generated"
    )
    def test_reviewer_recommendations_applied(self):
        """All 4 reviewer recommendations should be applied."""
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        config = data["config"]
        assert config["median_mode_used"] is True, "Recommendation 1: median mode not used"
        assert config["ksfr_mask"] is True, "Recommendation 2: KSFR mask not applied"
        assert config["asymmetric_dm"] is True, "Recommendation 3: asymmetric DM not applied"
        assert config["sparc_saturated_proxy_disabled"] is True, "Recommendation 4: SPARC proxy not disabled"

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 22 results not yet generated"
    )
    def test_ksfr_passes_for_dark_photon(self):
        """KSFR should pass (=0) for dark photon models since KSFR is composite-QCD constraint."""
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        ksfr = data["full_results"]["ksfr_pcac"]
        assert ksfr["loglike"] == 0.0, f"KSFR = {ksfr['loglike']}, expected 0 (N/A for dark photon)"

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 22 results not yet generated"
    )
    def test_indirect_detection_channels_nullified(self):
        """DAMPE, Fermi, XRISM phi->gg should all be 0 (asymmetric DM)."""
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        results = data["full_results"]
        assert results["dampe_cre"]["loglike"] == 0.0
        assert results["fermi_dwarf"]["loglike"] == 0.0
        assert results["xrism_phi_decay"]["loglike"] == 0.0

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 22 results not yet generated"
    )
    def test_sparc_disabled(self):
        """SPARC saturated proxy should be disabled for multi-portal."""
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        sparc = data["full_results"]["sparc"]
        assert sparc["loglike"] == 0.0
        assert sparc["saturated_proxy_disabled"] is True

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 22 results not yet generated"
    )
    def test_fewer_real_failures_than_phase21(self):
        """Phase 22 should have ≤ Phase 21 failures (improvement)."""
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        n_fails_phase22 = len(data["remaining_real_failures"])
        # Phase 21 had 6 failures (KSFR, DAMPE, XRISM, eROSITA, Euclid, SPARC)
        assert n_fails_phase22 < 6, f"Phase 22 has {n_fails_phase22} failures, expected < 6"

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 22 results not yet generated"
    )
    def test_cloud9_sigma_m_in_range(self):
        """Cloud-9 σ/m(28) should be in [30, 500] cm²/g range."""
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        sm28 = data["median_params"]["sigma_m_28"]
        assert 30 <= sm28 <= 500, f"σ/m(28) = {sm28}, expected in [30, 500]"
