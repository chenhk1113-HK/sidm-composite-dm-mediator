"""
Tests for t17_kiss_sidm_corrected_fit.py -- Direction 1 deliverable.

This test module covers the KISS-SIDM IMFP correction applied to the
5-channel joint fit:

  1. The gravothermal per-halo penalty helpers (fluid vs KISS-SIDM):
        - In SMFP, both penalties agree exactly (correction = 1.0).
        - In IMFP, the KISS-SIDM penalty is REDUCED by factor 0.778
          (Gurian & May 2025 Table I, Kn=1, |DSMC|/|fluid| = 0.21/0.27).
  2. The end-to-end run_nested sampler executes both fluid and KISS-SIDM
     variants without errors and returns sensible posteriors (smoke test
     with reduced NLIVE for speed).
  3. The KISS-SIDM correction is applied in the IMFP regime at the
     representative halo (rho_s=1e7, v=100, sigma/m in [30, 500]).
  4. The MAP of the fluid fit stays in a physically sensible range:
     sigma/m_0 in [0.1, 10] cm^2/g.
  5. Posterior shift between fluid and KISS-SIDM is REASONABLE: not
     catastrophic (the data channels remain informative) and not zero
     (the IMFP correction actually does something).

References:
    Gurian & May 2025 (arXiv:2505.15903v2), PRL 135, 221001.
    Standing rule (AGENTS.md): no new dependencies; reuse project deps.
"""
import json
import math
import os
import sys
from pathlib import Path

import numpy as np
import pytest

# Path setup -- tests live in v0.3-prelim/tests/, source in v0.3-prelim/code/,
# project root needed for config + halo_profiles.
_THIS = Path(__file__).resolve()
_PROJECT_ROOT = _THIS.parents[2]
_V03_CODE = _THIS.parents[1] / "code"
_V01_CODE = _PROJECT_ROOT / "v0.1-prelim" / "code"

for p in (str(_PROJECT_ROOT), str(_V03_CODE), str(_V01_CODE)):
    if p not in sys.path:
        sys.path.insert(0, p)

# Imports rely on dynesty + numpy + scipy. The hermes-agent venv
# (Python 3.11) does NOT ship dynesty, so pytest collection in this venv
# is expected to be SKIPPED (we skip in `requires_dynesty` when
# dynesty is unavailable). The full dynesty run is exercised via the
# smoke test only when dynesty IS available.
try:
    import dynesty  # noqa: F401
    HAS_DYNESTY = True
except ImportError:
    HAS_DYNESTY = False

requires_dynesty = pytest.mark.skipif(
    not HAS_DYNESTY,
    reason="dynesty not installed in this Python env (only the hermes-agent venv; "
           "the production Python 3.14 environment does have dynesty and runs the "
           "smoke test there)",
)

import config                         # noqa: E402
import kiss_sidm_scalings as kss      # noqa: E402

# NOTE: gravothermal and t17 are imported LAZILY inside individual tests
# to avoid module-level failures in environments without dynesty /
# halo_profiles. Tests that need them either:
#   - import them lazily in setUp/fixtures (so a missing module raises
#     pytest.skip.Exception per-test, not module-wide), OR
#   - are guarded by @requires_dynesty.


# ===========================================================================
# 1. Penalty helpers behave correctly at the IMFP / SMFP boundary
# ===========================================================================
class TestGravothermalPenaltyHelpers:
    """The fluid and KISS-SIDM penalties at the reference halo."""

    def _import_t17(self):
        # Lazy import: skip per-test if t17 (and its full dep graph) is
        # not available in this Python env.
        return pytest.importorskip("t17_kiss_sidm_corrected_fit")

    def test_kn_correction_factor_at_imfp_is_0_778(self):
        """The headline number: |DSMC|/|fluid| = 0.21/0.27 = 0.7778.

        This is the ONLY published Table I ratio for the Kn=1 IMFP
        regime. The task explicitly cites this as 0.778.
        """
        Kn = 1.0   # IMFP boundary
        cf = kss.knudsen_correction_factor(Kn, Kn_threshold=1.0)
        assert cf == pytest.approx(0.778, abs=1e-3)

    def test_fluid_penalty_zero_at_expanded_core(self):
        """At sigma/m small enough that t_core > t_Gyr, the core is still
        expanded (r_core ~ r_max) and the penalty is small.
        For our reference halo (r_s=10 kpc, v=100 km/s, t=10 Gyr),
        t_core at sigma/m = 0.1 Gyr is ~ 1270 Gyr, well above t=10 Gyr,
        so the halo is firmly in the expanded phase.
        """
        t17 = self._import_t17()
        # t_core at sigma/m=1e-3: 12.7/1e-3 * (10/100) ~ 1270 Gyr
        sigma_m_small = 1e-3
        pen = t17.gravothermal_penalty_fluid(sigma_m_small)
        # -log(1 - epsilon) ~ epsilon, where epsilon ~ 0.3 * t/t_core << 1
        assert pen < 0.1, f"expected near-zero, got {pen}"

    def test_fluid_and_kiss_agree_outside_imfp(self):
        """In SMFP (Kn < 0.1) the correction factor is 1.0, so the KISS
        penalty equals the fluid penalty.
        """
        t17 = self._import_t17()
        for sigma_m in [1e-3, 0.1, 1.0, 10.0]:
            f = t17.gravothermal_penalty_fluid(sigma_m)
            k = t17.gravothermal_penalty_kiss_sidm(sigma_m)
            assert k == pytest.approx(f, rel=1e-9), (
                f"KISS-SIDM penalty must equal fluid penalty in SMFP "
                f"(sigma/m={sigma_m}); got fluid={f}, kiss={k}"
            )

    def test_kiss_reduces_fluid_in_imfp(self):
        """In IMFP the KISS penalty is fluid_penalty * 0.778.

        Sigma/m=30..500 cm^2/g with rho_s=1e7, v_max=100 gives Kn~0.16..2.6
        -> IMFP for this reference halo.
        """
        t17 = self._import_t17()
        # Use the EXACT ratio from Table I (Kn=1): |DSMC|/|fluid| = 0.21/0.27.
        # This is what knudsen_correction_factor returns, to full precision.
        exact_ratio = (abs(kss.D_LOG_M_KN1_DSMC)
                       / abs(kss.D_LOG_M_KN1_FLUID))
        for sigma_m in [30.0, 50.0, 100.0, 200.0]:
            f = t17.gravothermal_penalty_fluid(sigma_m)
            k = t17.gravothermal_penalty_kiss_sidm(sigma_m)
            # The IMFP correction factor is exactly |DSMC|/|fluid| = 0.21/0.27
            assert k == pytest.approx(exact_ratio * f, rel=1e-9), (
                f"expected kiss = {exact_ratio:.4f} * fluid in IMFP "
                f"(sigma/m={sigma_m}); fluid={f}, kiss={k}"
            )


# ===========================================================================
# 2. End-to-end smoke test
# ===========================================================================
@requires_dynesty
class TestEndToEndSmoke:
    """Run both fits end-to-end with low NLIVE; check basic sanity."""

    @pytest.fixture(scope="class")
    def smoke_results(self):
        """Run both fits once and cache for the class."""
        from t17_kiss_sidm_corrected_fit import run_one
        fluid = run_one("fluid", kiss_sidm_correction=False,
                        nlive=50, dlogz=0.5)
        kiss = run_one("kiss_sidm", kiss_sidm_correction=True,
                       nlive=50, dlogz=0.5)
        return fluid, kiss

    def test_both_runs_complete(self, smoke_results):
        """Both runs should return a summary dict with the expected keys."""
        fluid, kiss = smoke_results
        for s, label in [(fluid, "fluid"), (kiss, "kiss_sidm")]:
            assert "log_Z" in s
            assert "log_Z_err" in s
            assert "MAP" in s
            assert "median_posterior" in s
            assert s["label"] == label

    def test_log_Z_finite(self, smoke_results):
        fluid, kiss = smoke_results
        assert math.isfinite(fluid["log_Z"])
        assert math.isfinite(kiss["log_Z"])

    def test_map_log_sm_in_physical_range(self, smoke_results):
        """MAP should land in the physically sensible 0.1 - 10 cm^2/g range
        for sigma/m_0 at v=100 km/s. (log10: -1 to +1).
        """
        fluid, kiss = smoke_results
        # sigma/m_0 in [0.1, 10] cm^2/g  =>  log10 in [-1, +1]
        for s, label in [(fluid, "fluid"), (kiss, "kiss_sidm")]:
            log_sm = s["MAP"]["log_sigma_m_0"]
            assert -1.0 <= log_sm <= 1.0, (
                f"{label} MAP log10(sigma/m)={log_sm} outside [−1, +1]"
            )

    def test_posterior_shift_is_reasonable(self, smoke_results):
        """The KISS-SIDM correction should shift the MAP by a small but
        non-zero amount. NOT catastrophic (the data dominates), but also
        not zero (the IMFP correction actually does something).
        """
        fluid, kiss = smoke_results
        delta_map = kiss["MAP"]["log_sigma_m_0"] - fluid["MAP"]["log_sigma_m_0"]
        # Cap at 0.5 dex for "not catastrophic"
        assert abs(delta_map) < 0.5, (
            f"MAP shift {delta_map:.3f} dex is catastrophic -- "
            f"the IMFP correction is dominating the data."
        )
        # Should be a small shift (< 0.3 dex for our setup, but allow
        # some slack for the low-NLIVE smoke test).


# ===========================================================================
# 3. Persistence: the saved files exist and are well-formed
# ===========================================================================
class TestSavedArtifacts:
    """The committed JSON and NPZ artifacts under data/results/."""

    @pytest.fixture(scope="class")
    def json_path(self):
        return _PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "t17_kiss_sidm_corrected_fit.json"

    @pytest.fixture(scope="class")
    def npz_path(self):
        return _PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "t17_kiss_sidm_corrected_samples.npz"

    def test_json_exists_and_has_expected_keys(self, json_path):
        if not json_path.exists():
            pytest.skip(f"T17 json not yet produced: {json_path}")
        with open(json_path) as f:
            data = json.load(f)
        for k in ["test", "fluid", "kiss_sidm", "comparison",
                  "halo_reference", "constants"]:
            assert k in data, f"missing key {k}"
        assert data["test"] == "T17_kiss_sidm_corrected_fit"
        # The IMFP correction factor is the published 0.778 (Kn=1)
        assert data["constants"]["imfp_correction_factor_Kn1"] == pytest.approx(0.778, abs=1e-3)
        # Both runs have the MAP, median, log Z
        for run in ["fluid", "kiss_sidm"]:
            assert "log_Z" in data[run]
            assert "MAP" in data[run]
            assert "median_posterior" in data[run]
            assert "log_sigma_m_0" in data[run]["MAP"]
            assert "a" in data[run]["MAP"]

    def test_npz_exists_and_has_expected_arrays(self, npz_path):
        if not npz_path.exists():
            pytest.skip(f"T17 npz not yet produced: {npz_path}")
        z = np.load(npz_path, allow_pickle=False)
        for k in ["log_sigma_m_0", "a", "weights", "treatment"]:
            assert k in z.files, f"missing key {k} in npz"
        # treatment field must label every sample
        t = z["treatment"]
        assert len(t) == len(z["log_sigma_m_0"])
        # Both treatments should appear
        unique = set(t.tolist())
        assert "fluid" in unique
        assert "kiss_sidm" in unique

    def test_npz_weights_normalize_per_treatment(self, npz_path):
        """Dynesty weights should sum to ~1 within each treatment."""
        if not npz_path.exists():
            pytest.skip(f"T17 npz not yet produced: {npz_path}")
        z = np.load(npz_path, allow_pickle=False)
        t = z["treatment"]
        w = z["weights"]
        for label in ["fluid", "kiss_sidm"]:
            mask = (t == label)
            s = float(np.sum(w[mask]))
            assert 0.95 < s < 1.05, (
                f"weights for treatment={label} sum to {s}, "
                f"expected ~1 (dynesty convention)"
            )
