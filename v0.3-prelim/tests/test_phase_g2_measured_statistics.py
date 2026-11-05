"""Phase G2 measured-statistics test (2026-11-05).

Phase G2 used to be literature labels only. It now measures merger activity from the local
IllustrisTNG Stage-3 sample. This test regenerates the growth summary with its producer, then
checks the measured block against an independent recomputation, and pins the boundary that the
0.7 / 8.0 tau multipliers are literature calibration the sample does NOT validate.

Skips when the local TNG sample has not been built (data/external/tng is git-ignored).
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
CODE = REPO / "v0.3-prelim" / "code"
RESULTS = REPO / "v0.3-prelim" / "data" / "results"
GROWTH_SUMMARY = RESULTS / "tng_stage3_growth_summary.json"
STATS_ARTIFACT = RESULTS / "phase_g2_measured_merger_statistics.json"
TREES = REPO / "v0.3-prelim" / "data" / "external" / "tng" / "stage3_sample" / "trees"

sys.path.insert(0, str(CODE))


@pytest.fixture(scope="module")
def stats():
    if not TREES.exists():
        pytest.skip(f"local IllustrisTNG sample not built ({TREES} missing)")
    # Live producer: rebuild the growth summary from the local merger trees first.
    res = subprocess.run([sys.executable, str(CODE / "tng_stage3_growth_summary.py")],
                         capture_output=True, text=True, encoding="utf-8",
                         timeout=900, cwd=str(REPO))
    assert res.returncode == 0, f"growth producer failed:\n{res.stderr[-1500:]}"
    assert GROWTH_SUMMARY.exists(), "growth producer wrote no artifact"

    import phase_g2_merger_history as g2
    measured = g2.measured_merger_statistics()
    assert measured is not None
    out = g2.write_measured_statistics_artifact(measured)
    assert out and out.exists(), "measured statistics artifact not written"
    return measured


def test_tier_count_and_labels(stats):
    assert set(stats["tiers"]) == {"relhic_mass_tier_tng50_1",
                                   "cloud9_mass_anchor_tier_tng50_1",
                                   "control_tier_tng100_1"}
    assert stats["usable_for_merger_claims"] == ["cloud9_mass_anchor_tier_tng50_1",
                                                 "relhic_mass_tier_tng50_1"]
    assert stats["excluded_from_merger_claims"] == ["control_tier_tng100_1"]


def test_measured_activity_fractions_recompute_independently(stats):
    """Recompute f_active from the raw per-tier counts rather than trusting the derived field."""
    summary = json.loads(GROWTH_SUMMARY.read_text(encoding="utf-8"))
    expected = {
        ("stage3_sample", "TNG50-1"): "relhic_mass_tier_tng50_1",
        ("stage3_anchor", "TNG50-1"): "cloud9_mass_anchor_tier_tng50_1",
        ("stage3_sample", "TNG100-1"): "control_tier_tng100_1",
    }
    for (tier_key, run), name in expected.items():
        mg = summary[tier_key]["by_run"][run]["mergers"]
        n = summary[tier_key]["by_run"][run]["n_halos"]
        quiet = mg["quiet_halos_no_merger_after_z1"]
        f_active_expected = round(1.0 - quiet / n, 4)
        got = stats["tiers"][name]["measured_activity_fraction"]
        assert got == f_active_expected, f"{name}: {got} vs recomputed {f_active_expected}"


def test_measured_activity_is_more_active_than_the_literature_assumption(stats):
    """The finding itself: both usable TNG50-1 tiers are MORE active than the assumed f_active = 0.5,
    and the Cloud-9-mass tier contains no quiescent halo at all."""
    lit = stats["literature_labels_in_use"]["f_active"]
    relhic = stats["measured_vs_literature"]["f_active_measured_relhic_mass"]
    anchor = stats["measured_vs_literature"]["f_active_measured_cloud9_mass"]
    assert lit == 0.5
    assert relhic is not None and relhic > lit
    assert anchor == 1.0
    assert stats["tiers"]["cloud9_mass_anchor_tier_tng50_1"][
        "quiet_halos_no_merger_after_z1"] == 0


def test_multipliers_are_unchanged_and_labelled_literature(stats):
    """Wiring measurement into G2 must not silently retune the collapse-time modulation."""
    import phase_g2_merger_history as g2
    assert g2.merger_history_modulator("quiescent") == 0.7
    assert g2.merger_history_modulator("active") == 8.0
    assert g2.merger_history_modulator("mixed") == 1.0
    assert stats["literature_labels_in_use"]["multipliers"] == {
        "quiescent": 0.7, "active": 8.0, "mixed": 1.0}
    not_measured = " ".join(stats["what_this_does_not_measure"])
    assert "collapse time" in not_measured


def test_artifact_matches_the_computed_block(stats):
    on_disk = json.loads(STATS_ARTIFACT.read_text(encoding="utf-8"))
    assert on_disk == stats, "published artifact differs from the freshly computed block"


def test_cloud9_history_label_is_flagged_as_observational(stats):
    """The Cloud-9 'quiescent' label stays an observation; the simulation tension is D8, not a relabel."""
    assert "D8" in stats["measured_vs_literature"]["consequence_for_cloud9_label"]
    import phase_g2_merger_history as g2
    cloud9 = [h for h in g2.HALOS_G2 if h[0] == "Cloud-9 host"][0]
    assert cloud9[3] == "quiescent"
