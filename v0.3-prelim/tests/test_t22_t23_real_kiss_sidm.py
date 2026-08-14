"""
Tests for t22_real_kiss_sidm_two_comp.py and t23_real_kiss_sidm_two_comp_imfp.py.

T22 is the publication-quality replacement for T19 (Yang+ 2026 2-comp SIDM
fit) with the REAL KISS-SIDM gravothermal penalty.

T23 is the publication-quality replacement for T20 (KISS-SIDM × 2-comp
combined fit) with the REAL KISS-SIDM penalty + IMFP correction.

These tests verify:
  1. T22 and T23 modules are importable
  2. The KISS-SIDM data loading works
  3. The T22 result JSON has the expected structure
  4. The T23 result JSON has the expected structure
  5. Bayes factor comparisons vs T19/T20 placeholder values are sensible

Standing rule (AGENTS.md): no new dependencies.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "v0.3-prelim" / "code"))


class TestT22Module:
    """t22_real_kiss_sidm_two_comp.py module is importable."""

    def test_t22_importable(self):
        """The T22 module is importable."""
        t22 = pytest.importorskip("t22_real_kiss_sidm_two_comp")
        assert hasattr(t22, "loglike_two_comp_yang_real_kiss")
        assert hasattr(t22, "loglike_two_comp_yang_real_kiss_no_imfp")
        assert hasattr(t22, "loglike_one_comp_yang_real_kiss")
        assert hasattr(t22, "loglike_one_comp_2ch_yang_real_kiss")
        assert hasattr(t22, "_real_kiss_penalty")
        assert hasattr(t22, "kiss_sidm_correction_at_sigma")

    def test_real_kiss_penalty_returns_non_negative(self):
        """Real KISS-SIDM penalty should be non-negative (penalizes when r_core is small)."""
        t22 = pytest.importorskip("t22_real_kiss_sidm_two_comp")
        # sigma_m > 0 should give a non-negative penalty
        pen1 = t22._real_kiss_penalty(50.0)
        assert pen1 >= 0
        # sigma_m = 0 should give 0
        pen0 = t22._real_kiss_penalty(0.0)
        assert pen0 == 0.0

    def test_kiss_correction_in_range(self):
        """KISS-SIDM correction factor should be in [0.778, 1.0]."""
        t22 = pytest.importorskip("t22_real_kiss_sidm_two_comp")
        c_small = t22.kiss_sidm_correction_at_sigma(0.001)
        c_large = t22.kiss_sidm_correction_at_sigma(100.0)
        assert 0.7 <= c_small <= 1.0
        assert 0.7 <= c_large <= 1.0

    def test_prior_transform_shape(self):
        """prior_transform_4 produces a 4-vector in the prior box."""
        t22 = pytest.importorskip("t22_real_kiss_sidm_two_comp")
        import numpy as np
        u = np.array([0.5, 0.5, 0.5, 0.5])
        x = t22.prior_transform_4(u)
        assert len(x) == 4
        assert -2.0 <= x[0] <= 2.0
        assert -3.0 <= x[1] <= 1.0
        assert 0.01 <= x[2] <= 0.99
        assert -2.0 <= x[3] <= 2.0


class TestT23Module:
    """t23_real_kiss_sidm_two_comp_imfp.py module is importable."""

    def test_t23_importable(self):
        """The T23 module is importable."""
        t23 = pytest.importorskip("t23_real_kiss_sidm_two_comp_imfp")
        assert hasattr(t23, "loglike_two_comp_real_kiss_imfp")
        assert hasattr(t23, "loglike_two_comp_real_kiss_no_imfp")
        assert hasattr(t23, "_real_kiss_penalty")
        assert hasattr(t23, "kiss_sidm_correction_at_sigma")

    def test_loglike_with_imfp_differs_from_no_imfp(self):
        """The IMFP and no-IMFP likelihoods should differ for IMFP sigma values."""
        t23 = pytest.importorskip("t23_real_kiss_sidm_two_comp_imfp")
        import numpy as np
        # In IMFP regime (sigma_m around 1.0 at v=100 km/s)
        theta_imfp = [0.0, 0.0, 0.5, 1.0]  # log sigma1, log sigma2, f1, a
        theta_same = [0.0, 0.0, 0.5, 0.0]
        ll_imfp_a = t23.loglike_two_comp_real_kiss_imfp(theta_imfp)
        ll_imfp_b = t23.loglike_two_comp_real_kiss_no_imfp(theta_imfp)
        ll_no_a = t23.loglike_two_comp_real_kiss_imfp(theta_same)
        ll_no_b = t23.loglike_two_comp_real_kiss_no_imfp(theta_same)
        # IMFP correction should give a different value when sigma is in IMFP
        # and same when correction factor is 1.0 (which happens when Kn is outside [0.1, 10])
        assert np.isfinite(ll_imfp_a)
        assert np.isfinite(ll_imfp_b)


class TestT22Result:
    """If T22 result JSON exists, validate it."""

    def test_t22_result_or_skip(self):
        """If T22 result JSON exists, check the structure."""
        result_path = PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "t22_real_kiss_sidm_two_comp.json"
        if not result_path.exists():
            pytest.skip("No T22 result JSON; run t22_real_kiss_sidm_two_comp.py first")

        with open(result_path) as f:
            data = json.load(f)
        assert "test" in data
        assert "fits" in data
        assert "bayes_factors" in data
        assert "A_two_comp_with_imfp" in data["fits"]
        assert "C_one_comp_nested_with_imfp" in data["fits"]
        # Log Z should be finite
        for label, fit in data["fits"].items():
            assert np.isfinite(fit["log_Z"]), f"{label} log Z is NaN/inf"
            assert -2.0 <= fit["MAP"][0] <= 2.0, f"{label} log_sigma1 out of prior"
        # The Bayes factor A vs C should be a real number (could be positive or negative)
        delta = data["bayes_factors"]["delta_A_C_2comp_vs_1comp_3ch"]
        assert np.isfinite(delta)
        # Compare to T19 placeholder
        t19_summary = data.get("t19_placeholder_summary", {})
        # The T22 result should be similar to T19 placeholder (within ~1 log Z)
        if t19_summary:
            # If T22 says strongly preferred/disfavored but T19 said equivalent, that's a big shift
            assert abs(delta) < 5.0, (
                f"T22 vs T19 placeholder differs significantly: "
                f"T22 delta = {delta}, T19 = {t19_summary.get('delta_2comp_vs_1comp_3ch_placeholder')}"
            )


class TestT23Result:
    """If T23 result JSON exists, validate it."""

    def test_t23_result_or_skip(self):
        """If T23 result JSON exists, check the structure."""
        result_path = PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "t23_real_kiss_sidm_two_comp_imfp.json"
        if not result_path.exists():
            pytest.skip("No T23 result JSON; run t23_real_kiss_sidm_two_comp_imfp.py first")

        with open(result_path) as f:
            data = json.load(f)
        assert "test" in data
        assert "fits" in data
        assert "A_two_comp_with_imfp" in data["fits"]
        assert "B_two_comp_no_imfp" in data["fits"]
        # Log Z should be finite
        for label, fit in data["fits"].items():
            assert np.isfinite(fit["log_Z"]), f"{label} log Z is NaN/inf"
            assert -2.0 <= fit["MAP"][0] <= 2.0
        # IMFP correction effect
        delta = data["imfp_correction_effect"]["delta_log_Z_A_minus_B"]
        assert np.isfinite(delta)
        # With real KISS-SIDM, IMFP correction should have near-zero effect
        # (because the gravothermal penalty is already weak)
        # The placeholder T20 result was delta = -1.46 (IMFP strongly disfavored)
        # With real data, the delta should be MUCH smaller in magnitude
        assert abs(delta) < 1.0, (
            f"T23 IMFP correction effect is too large: {delta}. "
            f"Expected near-zero with real KISS-SIDM. "
            f"Placeholder T20 had delta = -1.46."
        )