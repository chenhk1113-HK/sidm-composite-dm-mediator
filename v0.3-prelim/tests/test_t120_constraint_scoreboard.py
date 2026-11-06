"""Guard for v0.3-prelim/code/t120_constraint_scoreboard.py (finding F18 / decision D9).

House style mirrors the F16 channel-taxonomy guard
(v0.3-prelim/tests/test_channel_taxonomy_single_source.py): the scoreboard is
recomputed live from the producers, every headline tally is pinned, and no test
file in the T120 family may keep a hard-coded "all constraints pass" assertion.

Every number pinned below was produced by running
    .venv-sidm-bench/Scripts/python.exe v0.3-prelim/code/t120_constraint_scoreboard.py
and the producer calls, in this repo, in this task (Python 3.12, numpy 2.5.2,
scipy 1.18.1). Nothing here is remembered from a document.

CLAIMS RETIRED BY THIS FAMILY (docs/INTEGRITY_FINDINGS_2026-11-04.md, F18 / D9):
  * "all 8 observational constraints pass"        -> best arm measured 7 PASS / 1 MARGINAL / 0 FAIL
  * "v1.13 passes all 8 points"                   -> 6 PASS / 1 MARGINAL / 1 FAIL at a_slope=1.0
  * "Cloud-9 sigma/m = 128 cm^2/g"                -> 99.75-100.04 across every arm tested
  * "multi-component contributes ~2.9x"           -> 2.251114 measured
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

_TESTS_DIR = Path(__file__).resolve().parent
_CODE_DIR = _TESTS_DIR.parent / "code"
if str(_CODE_DIR) not in sys.path:
    sys.path.insert(0, str(_CODE_DIR))

from t120_4_joint_fit import (  # noqa: E402
    joint_fit_evaluation,
    joint_fit_full_evaluation,
)
from t120_constraint_scoreboard import (  # noqa: E402
    MARGINAL_BAND_RELATIVE,
    OBSERVATIONS,
    constraint_scoreboard,
    four_constraint_scoreboard,
)

T120_TEST_FILES = (
    "test_t120_4_joint_fit.py",
    "test_t120_11_hidden_u1.py",
    "test_t120_13_integration.py",
    "test_t120_15_uv_slope.py",
)

# Live-measured tallies: (a_slope_override) -> (n_pass, n_marginal, n_fail)
PINNED_TALLIES = {
    None: (3, 0, 5),
    0.5: (7, 1, 0),
    0.8: (7, 1, 0),
    1.0: (6, 1, 1),
    1.2: (5, 1, 2),
    1.5: (3, 1, 4),
    1.93: (3, 0, 5),
}

# Live-measured Cloud-9 values, per arm.
PINNED_CLOUD9 = {
    None: 100.03606419810939,
    0.5: 99.75289124538487,
    0.8: 99.77839492084853,
    1.0: 99.80168969102034,
    1.2: 99.83173846961525,
    1.5: 99.89391008496175,
    1.93: 100.03663478458891,
}

PINNED_V3 = {
    None: 25.112354420745653,
    0.5: 0.16876759573252717,
    1.0: 0.9686107942907997,
    1.93: 25.229293887008495,
}

# The two producer entry points, at EQUAL a_slope, agree exactly. The quoted
# "100.0361 vs 99.80 producer disagreement" is not a disagreement between entry
# points; it is the Phase-44 default a_slope (1.9286750353457855) versus the
# v1.13 override a_slope = 1.0. Pinned as a disclosed number, not reconciled.
PRODUCER_ARM_GAP_RELATIVE = 0.002342900122748662  # (100.03606419810939 - 99.80168969102034) / 100.03606419810939


def test_scoreboard_recomputes_the_pinned_tallies():
    """(a) The scoreboard is live and reproduces every pinned tally exactly."""
    for a, expected in PINNED_TALLIES.items():
        s = constraint_scoreboard(a_slope_override=a)["summary"]
        assert (s["n_pass"], s["n_marginal"], s["n_fail"]) == expected, (a, s)


def test_all_eight_observations_are_present_and_declared():
    """(b) All 8 v1.13 observations appear, each with a bound and a verdict."""
    keys = [k for k, _label, _kind, _bound in OBSERVATIONS]
    assert len(keys) == 8 and len(set(keys)) == 8
    obs = constraint_scoreboard(a_slope_override=1.0)["observations"]
    assert set(obs) == set(keys)
    for key, o in obs.items():
        assert o["verdict"] in {"PASS", "MARGINAL", "FAIL"}, (key, o)
        assert o["bound"] is not None and o["kind"] in {"ceiling", "floor", "band"}
        assert o["label"]
        assert o["ratio_to_bound"] > 0.0


def test_marginal_fail_bookkeeping_and_values():
    """(c) The tally is closed (sums to 8) and the pinned values are the producers'."""
    for a in PINNED_TALLIES:
        sb = constraint_scoreboard(a_slope_override=a)
        s = sb["summary"]
        assert s["n_pass"] + s["n_marginal"] + s["n_fail"] == s["n_total"] == 8, (a, s)
        assert s["parameter_set"], s
        assert s["tolerance_label"] == MARGINAL_BAND_RELATIVE
        obs = sb["observations"]
        assert obs["v28.0_Cloud-9"]["value"] == pytest.approx(PINNED_CLOUD9[a], rel=1e-12)
        if a in PINNED_V3:
            assert obs["v3.0_extreme_UFD"]["value"] == pytest.approx(PINNED_V3[a], rel=1e-12)
    # Cloud-9 is MARGINAL (never PASS) in every dwarf-compatible arm.
    for a in (0.5, 0.8, 1.0, 1.2, 1.5):
        obs = constraint_scoreboard(a_slope_override=a)["observations"]["v28.0_Cloud-9"]
        assert obs["verdict"] == "MARGINAL", (a, obs)


def test_marginal_band_is_declared_and_not_tunable():
    """The declared 5% band sits in a clean gap: no observed near-miss is as large
    as the smallest observed real violation, so it cannot be tuned to launder a
    FAIL into a MARGINAL (decision D9, rule 3)."""
    assert MARGINAL_BAND_RELATIVE == 0.05
    worst_marginal = max(
        (100.0 - PINNED_CLOUD9[a]) / 100.0 for a in (0.5, 0.8, 1.0, 1.2, 1.5)
    )
    smallest_real_violation = (PINNED_V3[1.0] - 0.8) / 0.8
    assert worst_marginal < MARGINAL_BAND_RELATIVE, worst_marginal
    assert smallest_real_violation > MARGINAL_BAND_RELATIVE, smallest_real_violation
    # Measured: worst Cloud-9 shortfall 0.247%, smallest ceiling violation 21.08%.
    assert worst_marginal == pytest.approx(0.0024710875461512673, rel=1e-9)
    assert smallest_real_violation == pytest.approx(0.21076349286349952, rel=1e-9)


_ASSERT_ALL_PASS = re.compile(r'assert\s+[^\n#]*\[\s*["\']all_pass["\']\s*\]')


def test_no_t120_file_asserts_all_pass_true():
    """(d) No file in the T120 family may keep an assertion that expects all_pass
    to be True. Every remaining all_pass assertion must assert it is False."""
    offenders = []
    for name in T120_TEST_FILES:
        path = _TESTS_DIR / name
        text = path.read_text(encoding="utf-8")
        for lineno, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            if not stripped.startswith("assert"):
                continue
            if not _ASSERT_ALL_PASS.search(stripped):
                continue
            if "is False" in stripped or stripped.startswith("assert not"):
                continue
            offenders.append((name, lineno, stripped))
    assert not offenders, f"bare all_pass assertions expecting True: {offenders}"


def test_every_t120_file_states_which_claims_are_retired():
    """Each of the four files must carry the F18 / D9 note naming the retired claims.

    These files are back inside the release gate (decision D9 executed 2026-11-05), so
    they must NOT carry a `# GATE-IGNORED[` marker any more; the note is what records
    what was retired.
    """
    for name in T120_TEST_FILES:
        text = (_TESTS_DIR / name).read_text(encoding="utf-8")
        assert "F18" in text and "D9" in text, name
        assert "RETIRED" in text or "retired" in text, name
        assert "# GATE-IGNORED[" not in text, f"{name}: still gate-ignored after repair"


def test_producer_entry_points_agree_at_equal_a_slope():
    """(e) The quoted 100.0361-vs-99.80 'producer disagreement' is pinned honestly.

    At the SAME a_slope the two entry points return bit-identical Cloud-9 values.
    The gap is entirely the a_slope parameter (Phase-44 default vs v1.13 override),
    and that gap is pinned as a disclosed number rather than hidden.
    """
    a_def = float(joint_fit_evaluation()["Cloud-9"])
    f_def = float(joint_fit_full_evaluation()["v28.0_Cloud-9"])
    a_one = float(joint_fit_evaluation(a_slope_override=1.0)["Cloud-9"])
    f_one = float(joint_fit_full_evaluation(a_slope_override=1.0)["v28.0_Cloud-9"])

    assert a_def == f_def == PINNED_CLOUD9[None]
    assert a_one == f_one == PINNED_CLOUD9[1.0]
    assert abs(a_def - f_def) == 0.0
    assert abs(a_one - f_one) == 0.0

    gap = (PINNED_CLOUD9[None] - PINNED_CLOUD9[1.0]) / PINNED_CLOUD9[None]
    assert gap == pytest.approx(PRODUCER_ARM_GAP_RELATIVE, rel=1e-9)


def test_four_constraint_view_matches_the_eight_point_view():
    """The 4-constraint and 8-observation views must not disagree on shared points."""
    for a in (None, 1.0):
        four = four_constraint_scoreboard(a_slope_override=a)["observations"]
        eight = constraint_scoreboard(a_slope_override=a)["observations"]
        assert four["Cloud-9"]["value"] == pytest.approx(eight["v28.0_Cloud-9"]["value"], rel=1e-12)
        assert four["dSph"]["value"] == pytest.approx(eight["v15.0_classical_dSph"]["value"], rel=1e-12)
        assert four["SPARC"]["value"] == pytest.approx(eight["v100.0_SPARC"]["value"], rel=1e-12)
        assert four["cluster"]["value"] == pytest.approx(eight["v500.0_cluster"]["value"], rel=1e-12)
        assert four["Cloud-9"]["verdict"] == eight["v28.0_Cloud-9"]["verdict"]
        assert four["dSph"]["verdict"] == eight["v15.0_classical_dSph"]["verdict"]


def test_no_arm_reaches_eight_of_eight():
    """The honest headline: no a_slope arm tested reaches 8 PASS with zero MARGINAL."""
    for a in PINNED_TALLIES:
        s = constraint_scoreboard(a_slope_override=a)["summary"]
        assert not (s["n_pass"] == 8 and s["n_marginal"] == 0 and s["n_fail"] == 0), (a, s)


# ---------------------------------------------------------------------------
# OWNER DECISION 2026-11-06: "adopt 0.5-0.8; keep 100".
# The decision is pinned here so a later edit cannot quietly promote the
# Phase-44 default arm back to headline status, nor quietly move the bar.
# ---------------------------------------------------------------------------

def test_adopted_arm_is_declared_and_measured():
    from t120_constraint_scoreboard import adopted_arm_declaration
    d = adopted_arm_declaration()
    assert [row["a_slope"] for row in d["adopted_arms"]] == [0.5, 0.8]
    for row in d["adopted_arms"]:
        assert (row["n_pass"], row["n_marginal"], row["n_fail"]) == (7, 1, 0), row
        assert row["cloud9_verdict"] == "MARGINAL", row
        # The adopted arm MISSES the retained 100 cm^2/g floor by a quarter of a
        # percent. Pinned as a range so a real physics change is caught, but
        # float noise is not treated as drift.
        assert 0.0015 < row["cloud9_shortfall_fraction"] < 0.0035, row
        assert row["cloud9_value_cm2_per_g"] < row_bound_cloud9(), row
    legacy = {row["a_slope"]: row for row in d["legacy_arms"]}
    assert legacy[None]["role"] == "legacy_default_fit"
    assert (legacy[None]["n_pass"], legacy[None]["n_marginal"], legacy[None]["n_fail"]) == (3, 0, 5)
    assert legacy[None]["cloud9_verdict"] == "PASS"
    assert "owner decision 2026-11-06" in d["note"]


def test_cloud9_bar_is_retained_and_stays_internal():
    """Owner kept the 100 cm^2/g mark; F21 requires it to stay labelled INTERNAL."""
    from t120_constraint_scoreboard import adopted_arm_declaration
    d = adopted_arm_declaration()
    assert d["cloud9_bound_cm2_per_g"] == 100.0
    assert "INTERNAL" in d["cloud9_bound_provenance"]
    assert "no published Cloud-9 floor" in d["cloud9_bound_provenance"]


def row_bound_cloud9():
    from t120_constraint_scoreboard import OBSERVATIONS
    return float([o[3] for o in OBSERVATIONS if o[0] == "v28.0_Cloud-9"][0])


# ---------------------------------------------------------------------------
# The adoption artifact is what the headline docs cite. It must be a real,
# reproducible product of the live producers, not a hand-written number file.
# ---------------------------------------------------------------------------

def test_adoption_artifact_is_reproducible_from_the_live_producers():
    import json

    from t120_constraint_scoreboard import ADOPTION_ARTIFACT, write_adoption_artifact

    assert ADOPTION_ARTIFACT.exists(), (
        "v0.3-prelim/data/results/t120_adopted_arm_declaration.json is missing; "
        "run python v0.3-prelim/code/t120_constraint_scoreboard.py"
    )
    stored = json.loads(ADOPTION_ARTIFACT.read_text(encoding="utf-8"))
    live = write_adoption_artifact()
    assert stored == live, "the adoption artifact no longer matches a live recomputation"


def test_adoption_artifact_carries_the_owner_decision_values():
    import json

    from t120_constraint_scoreboard import ADOPTION_ARTIFACT

    d = json.loads(ADOPTION_ARTIFACT.read_text(encoding="utf-8"))
    assert [row["a_slope"] for row in d["adopted_arms"]] == [0.5, 0.8]
    assert all(row["role"] == "adopted" for row in d["adopted_arms"])
    for row in d["adopted_arms"]:
        assert (row["n_pass"], row["n_marginal"], row["n_fail"]) == (7, 1, 0), row
        assert row["cloud9_verdict"] == "MARGINAL", row
    assert d["cloud9_bound_cm2_per_g"] == 100.0
    assert "INTERNAL" in d["cloud9_bound_provenance"]
    assert "owner decision 2026-11-06" in d["note"]
