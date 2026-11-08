"""Guard for decision D3 (owner, 2026-11-07): the direct-detection unit constant.

Facts this pins (all measured, see v0.3-prelim/data/results/dd_unit_fix_recertification.json):
  * both direct-detection channels convert sigma/m -> sigma_DM-nucleon through ONE shared
    constant, the CODATA 1 GeV = 1.78266192e-24 g, not a hard-coded 1e-24,
  * neither channel contains a bare 1e-24 conversion any more,
  * the certified effect on the stored canonical posteriors is ZERO: every tested point is
    already at the channel's saturated -1.0 penalty, so no published canonical number moved,
  * the switch boundary moved down by the factor 1.783 (the channel got stricter),
  * in the mass regime the canonical fits occupy, the channel is a constant offset and cannot
    discriminate: it is a flag, not a constraint.

Failure mode this catches: someone re-hard-codes 1e-24 in one channel only (the two channels
then silently diverge), or quotes the DD channel as if it constrained the fit.
"""
import inspect
import json
import os
import sys
import unittest

CODE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "code")
RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "data", "results")
if CODE_DIR not in sys.path:
    sys.path.insert(0, CODE_DIR)

import channels_extended as ce  # noqa: E402

CODATA_GEV_IN_G = 1.78266192e-24


class DirectDetectionUnitConstant(unittest.TestCase):

    def test_shared_constant_is_codata(self):
        self.assertAlmostEqual(ce.SIGMA_M_TO_DM_NUCLEON, CODATA_GEV_IN_G, delta=1e-30)
        self.assertAlmostEqual(ce.GEV_IN_G, CODATA_GEV_IN_G, delta=1e-30)

    def test_no_bare_1e24_conversion_left_in_the_two_channels(self):
        for name in ("loglike_direct_detection_exclusion", "loglike_competitor_dd_watch"):
            src = inspect.getsource(getattr(ce, name))
            parts = src.split('"""')
            body = parts[-1] if len(parts) >= 3 else src  # code after the docstring
            compact = body.replace(" ", "")
            self.assertNotIn("1e-24*", compact,
                             msg=f"{name} still multiplies by a hard-coded 1e-24")
            self.assertIn("SIGMA_M_TO_DM_NUCLEON", body,
                          msg=f"{name} must use the shared constant")

    def test_channels_agree_at_a_point_where_both_apply(self):
        """Above the sub-GeV guard the two channels must not diverge in scale."""
        sigma_m, m_chi = 1.0, 500.0
        self.assertEqual(ce.loglike_direct_detection_exclusion(sigma_m, m_chi),
                         ce.loglike_competitor_dd_watch(sigma_m, m_chi))

    def test_sub_gev_guard_returns_zero_for_both(self):
        self.assertEqual(ce.loglike_direct_detection_exclusion(100.0, 1.0), 0.0)
        self.assertEqual(ce.loglike_competitor_dd_watch(100.0, 1.0), 0.0)

    def test_recertification_artifact_exists_and_certifies_no_move(self):
        path = os.path.join(RESULTS_DIR, "dd_unit_fix_recertification.json")
        self.assertTrue(os.path.exists(path),
                        "the D3 recertification measurement must be on disk")
        with open(path) as f:
            rep = json.load(f)
        self.assertAlmostEqual(rep["constant_fixed"], CODATA_GEV_IN_G, delta=1e-30)
        self.assertAlmostEqual(rep["constant_pre_fix"], 1e-24, delta=1e-30)
        self.assertAlmostEqual(rep["ratio_new_over_old"], 1.78266192, delta=1e-6)
        self.assertGreaterEqual(rep["n_points_tested"], 3)
        self.assertEqual(rep["n_points_where_penalty_changed"], 0,
                         "D3 was certified as a no-move on the stored canonical posteriors; "
                         "if a point now moves, the canonical fit must be re-derived")
        self.assertFalse(rep["verdict"]["canonical_numbers_move"])

    def test_switch_boundary_moved_by_the_full_1783_factor(self):
        path = os.path.join(RESULTS_DIR, "dd_unit_fix_recertification.json")
        with open(path) as f:
            rep = json.load(f)
        for fname, b in rep["switch_boundaries"].items():
            self.assertAlmostEqual(b["boundary_shift_factor"], 1e-24 / CODATA_GEV_IN_G, delta=1e-9,
                                   msg=f"{fname}: boundary must move by the reciprocal of 1.783")
            self.assertLess(b["sigma_m_switch_LZ_fixed_cm2_per_g"],
                            b["sigma_m_switch_LZ_pre_fix_cm2_per_g"],
                            "the fixed channel must be stricter, not looser")

    def test_channel_is_saturated_in_the_sidm_relevant_region(self):
        path = os.path.join(RESULTS_DIR, "dd_unit_fix_recertification.json")
        with open(path) as f:
            rep = json.load(f)
        scan = rep["saturation_scan"]
        self.assertEqual(scan["unpenalised_rows_not_explained_by_guard"], 0,
                         "at m_chi >= 3 GeV and sigma/m >= 1e-4 the channel is always at -1.0")
        self.assertGreaterEqual(scan["fraction_penalised_fixed"], 0.8)


if __name__ == "__main__":
    unittest.main()
