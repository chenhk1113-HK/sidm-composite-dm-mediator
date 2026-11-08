"""Guard for decision D2 (owner, 2026-11-07): Phase 40 model-comparison penalty convention.

What this test pins is the CONVENTION and its self-consistency, not a pinned literal:
  * the published penalty is per-model (charged once for parameters shared by all galaxies),
  * the AIC factor 2 applies to BOTH the log-likelihood term and the parameter penalty,
  * the rejected per-dataset alternative and the legacy unscaled value stay published,
  * the outlier-sensitivity matrix is present and its median reading disagrees in sign
    with the total reading for SIDM-vs-Burkert, which is why the caveat must exist.

Failure mode this catches: a future edit that re-inflates the penalty by n_galaxies, or that
quotes one reading of the SIDM-vs-Burkert verdict as if it were the only one.
"""
import json
import os
import unittest

RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "data", "results")
ARTIFACT = os.path.join(RESULTS_DIR, "phase40_corrected_comparison.json")


def _load():
    with open(ARTIFACT) as f:
        return json.load(f)


class Phase40PenaltyConvention(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.data = _load()
        cls.op = cls.data["occam_penalty"]

    def test_convention_is_declared_and_is_per_model(self):
        self.assertEqual(self.op.get("adopted_convention"), "per_model",
                         "Phase 40 must declare its penalty convention (decision D2)")

    def test_adopted_aic_matches_per_model_formula_from_stored_totals(self):
        """Recompute the published ΔAIC from the artifact's own totals."""
        t = self.data["totals"]
        n_gal = self.data["n_galaxies"]
        dk_nfw = self.op["k_phys_sidm"] - self.op["k_phys_nfw"]
        dk_burk = self.op["k_phys_sidm"] - self.op["k_phys_burkert"]
        expect_nfw = 2.0 * t["delta_sid_minus_nfw_total"] - 2.0 * dk_nfw
        expect_burk = 2.0 * t["delta_sid_minus_burk_total"] - 2.0 * dk_burk
        self.assertAlmostEqual(self.op["aic_diff_phys_nfw_minus_sidm"], expect_nfw, delta=1e-6,
                               msg="adopted ΔAIC(NFW-SIDM) must be 2*ΔlogL - 2*Δk")
        self.assertAlmostEqual(self.op["aic_diff_phys_burk_minus_sidm"], expect_burk, delta=1e-6,
                               msg="adopted ΔAIC(Burkert-SIDM) must be 2*ΔlogL - 2*Δk")

    def test_penalty_is_not_charged_once_per_galaxy_in_the_published_value(self):
        per_dataset = self.op.get("rejected_alternative_per_dataset_charging")
        self.assertIsNotNone(per_dataset, "the rejected per-dataset reading must stay published")
        t = self.data["totals"]
        n_gal = self.data["n_galaxies"]
        dk_nfw = self.op["k_phys_sidm"] - self.op["k_phys_nfw"]
        expect = 2.0 * t["delta_sid_minus_nfw_total"] - 2.0 * dk_nfw * n_gal
        self.assertAlmostEqual(per_dataset["aic_diff_phys_nfw_minus_sidm"], expect, delta=1e-6)
        self.assertAlmostEqual(per_dataset["penalty_units_charged"], 2.0 * dk_nfw * n_gal, delta=1e-6)
        # The published (per-model) value must NOT be the per-galaxy one.
        self.assertNotAlmostEqual(self.op["aic_diff_phys_nfw_minus_sidm"],
                                  per_dataset["aic_diff_phys_nfw_minus_sidm"], places=3,
                                  msg="published value silently reverted to per-galaxy charging")

    def test_legacy_unscaled_value_is_disclosed(self):
        legacy = self.op.get("legacy_unscaled_per_model")
        self.assertIsNotNone(legacy, "the pre-D2 unscaled reading must remain disclosed")
        t = self.data["totals"]
        dk_nfw = self.op["k_phys_sidm"] - self.op["k_phys_nfw"]
        self.assertAlmostEqual(legacy["aic_diff_phys_nfw_minus_sidm"],
                               t["delta_sid_minus_nfw_total"] - 2.0 * dk_nfw, delta=1e-6)

    def test_outlier_sensitivity_published_and_flips_the_burkert_verdict(self):
        osens = self.op.get("outlier_sensitivity")
        self.assertIsNotNone(osens, "outlier sensitivity must be published with the verdict")
        total = osens["per_model_total_delta_aic_burk_minus_sidm"]
        median = osens["per_model_median_scaled_delta_aic_burk_minus_sidm"]
        self.assertGreater(total, 0.0, "expected the total reading to favour SIDM")
        self.assertLess(median, 0.0, "expected the median reading to favour Burkert")
        # The flip must be larger than the penalty itself, which is the honest headline.
        self.assertGreater(abs(median - total), 2.0 * (self.op["k_phys_sidm"] - self.op["k_phys_burkert"]),
                           msg="the outlier flip should dominate the 20-unit penalty")

    def test_nfw_verdict_sign_is_stable_across_readings(self):
        osens = self.op["outlier_sensitivity"]
        self.assertGreater(osens["per_model_no_outliers_delta_aic_nfw_minus_sidm"], 0.0)
        self.assertGreater(self.op["aic_diff_phys_nfw_minus_sidm"], 0.0)

    def test_verdict_caveats_exist_and_name_the_instability(self):
        caveats = self.data.get("verdict_caveats")
        self.assertIsNotNone(caveats, "verdicts must ship with their caveats")
        self.assertIn("phys_burk_vs_sidm_is_not_robust", caveats)
        self.assertIn("comparison_is_sigma_inert", caveats)
        self.assertIn("sigma/m-inert", caveats["comparison_is_sigma_inert"])


if __name__ == "__main__":
    unittest.main()
