"""Guard for decision D6 (owner, 2026-11-07): the 8 channel slots are not 8 measurements.

The eight low/high velocity slots are drawn from FOUR distinct sources, of which three are
external measurements; five of the slots (UFD v=3/5/7/10, dSph v=15) are velocity bins of ONE
Horigome+ 2025 combined dSph+UFD analysis and share its systematics. Counting them as five
independent confirmations inflates the headline (the ClawsGO review's "correlated
pseudo-replicates" criticism, and finding F16's retired "4 of 7" framing).

This guard makes the structure machine-read so a published count cannot silently re-inflate:
the artifact t205_channel_independence.json must exist, agree with the code's own declaration,
and any doc that quotes a slot count must be reconcilable with it.
"""
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CODE_DIR = os.path.join(ROOT, "v0.3-prelim", "code")
RESULTS_DIR = os.path.join(ROOT, "v0.3-prelim", "data", "results")
if CODE_DIR not in sys.path:
    sys.path.insert(0, CODE_DIR)

import T205_full_likelihood_published as t205  # noqa: E402

ARTIFACT = os.path.join(RESULTS_DIR, "t205_channel_independence.json")


class ChannelIndependenceStructure(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.live = t205.channel_independence_summary()

    def test_every_slot_has_a_declared_source(self):
        labels = [row[4] for row in t205.OBS_PUBLISHED]
        self.assertEqual(len(labels), 8)
        self.assertEqual(set(labels), set(t205.INDEPENDENT_SOURCE_OF_SLOT),
                         "every slot must declare its independent source (decision D6)")

    def test_counts_are_slots_not_measurements(self):
        self.assertEqual(self.live["n_slots"], 8)
        self.assertEqual(self.live["n_distinct_sources"], 4)
        self.assertEqual(self.live["n_external_independent_sources"], 3,
                         "only three of the four sources are external measurements")
        self.assertEqual(self.live["n_internal_slots"], 1,
                         "the Cloud-9 slot is an internal model output (F21)")

    def test_horigome_bins_are_declared_as_one_correlated_group(self):
        group = self.live["correlated_groups"]["Horigome+ 2025"]
        self.assertEqual(sorted(group),
                         sorted(["UFD v=3", "UFD v=5", "UFD v=7", "UFD v=10", "dSph v=15"]),
                         "the five Horigome+ velocity bins must be one declared group")
        self.assertEqual(len(self.live["slots_by_source"]["Horigome+ 2025 (arXiv:2503.13650, combined dSph+UFD analysis, Table II)"]), 5)

    def test_refit_status_is_honest(self):
        self.assertIn("NOT refitted", self.live["refit_status"],
                      "D6 was declared, not refitted - the artifact must say so")

    def test_artifact_matches_the_live_declaration(self):
        self.assertTrue(os.path.exists(ARTIFACT), "the independence artifact must be on disk")
        with open(ARTIFACT, encoding="utf-8") as f:
            stored = json.load(f)
        self.assertEqual(stored["slot_to_source"], self.live["slot_to_source"])
        for key in ("n_slots", "n_distinct_sources", "n_external_independent_sources"):
            self.assertEqual(stored[key], self.live[key], f"stored {key} drifted from the code")


if __name__ == "__main__":
    unittest.main()
