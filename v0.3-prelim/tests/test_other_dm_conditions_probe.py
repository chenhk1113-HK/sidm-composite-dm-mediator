"""Regression tests for other_dm_conditions_probe.py (finding F22).

The point of this suite is not that a JSON exists. It guards three things that could each silently
make the "can the framework explain other dark-matter systems?" answer wrong:
  1. the probe's velocity/halo-convention table drifting away from the producer it is meant to mirror;
  2. a published bound being quoted that the verified KB entry does not actually contain
     (a fabricated citation would flip a verdict and nobody would notice);
  3. an internal project number (the 128 cm2/g Phase-44 model output, F21) creeping back in as if it
     were published data.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

TESTS_DIR = Path(__file__).resolve().parent
PROJECT_DIR = TESTS_DIR.parent
CODE_DIR = PROJECT_DIR / "code"
RESULTS_DIR = PROJECT_DIR / "data" / "results"
KB_DIR = PROJECT_DIR.parent / "docs" / "papers" / "verified"

ARTIFACT = RESULTS_DIR / "other_dm_conditions_probe.json"


def _load(name):
    spec = importlib.util.spec_from_file_location(name, CODE_DIR / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def probe():
    return _load("other_dm_conditions_probe")


@pytest.fixture(scope="module")
def artifact():
    assert ARTIFACT.exists(), f"missing artifact {ARTIFACT}; run code/other_dm_conditions_probe.py"
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_artifact_matches_a_live_rebuild(probe, artifact):
    """The stored scoreboard must be exactly what the producer computes now."""
    fresh = probe.build()
    assert fresh == artifact, "stored other_dm_conditions_probe.json no longer matches the live build"


def test_point_table_reproduces_the_producer_on_every_arm(probe):
    """The probe's effective values must equal joint_fit_full_evaluation()'s own channel values."""
    for a in probe.ARM_A_SLOPES:
        ev = probe.producer_values(a_slope_override=a)
        for v, (_ht, _r, lbl) in probe.T120_POINTS.items():
            mine = probe.model_values(v, a_slope_override=a)["effective_cm2_per_g"]
            theirs = float(ev[f"v{v}_{lbl.replace(' ', '_')}"])
            assert abs(mine - theirs) <= 1e-12 * max(1.0, abs(theirs)), (
                f"mirror drift on arm {a} at v={v}: probe {mine!r} vs producer {theirs!r}")


def test_every_published_bound_quote_is_verbatim_in_its_kb_entry(probe):
    """No bound may be paraphrased from memory: the quote must exist, on the cited line."""
    for cond in probe.CONDITIONS:
        src = cond["source"]
        path = KB_DIR / src["kb"]
        assert path.exists(), f"KB entry missing for {cond['id']}: {path}"
        lines = path.read_text(encoding="utf-8").split("\n")
        hits = [i + 1 for i, line in enumerate(lines) if src["quote"] in line]
        assert hits, f"quote not found in {src['kb']} for {cond['id']}: {src['quote']!r}"
        assert src["line"] in hits, (
            f"{cond['id']}: cited line {src['line']} but the quote is on {hits} of {src['kb']}")


def test_published_bounds_are_not_the_internal_phase44_number(probe, artifact):
    """F21: 128.126 cm2/g is this project's own Phase-44 output. It must never act as data."""
    phase44 = json.loads((RESULTS_DIR / "sigma_m_phase44.json").read_text(encoding="utf-8"))
    internal = phase44["v28.0_Cloud-9"]
    for cond in probe.CONDITIONS:
        b = cond["bound_cm2_per_g"]
        if b is None:
            continue
        values = b if isinstance(b, (list, tuple)) else [b]
        for value in values:
            assert abs(value - internal) > 1.0, (
                f"{cond['id']} uses {value}, which is the internal Phase-44 model output "
                f"({internal}) rather than a published bound")
    assert any("internal" in (cond.get("note") or "") for cond in probe.CONDITIONS
               if cond["id"] == "cloud9_optimum_ohana")


def test_measured_arm_tallies_are_pinned(artifact):
    """These are the measurements the F22 write-up rests on; a change must be a decision, not drift."""
    expected = {
        "a_slope_0.5": {"CONSISTENT": 8, "TENSION": 1, "VIOLATED": 2, "OUTSIDE": 1, "NOT_A_BOUND": 1},
        "a_slope_0.8": {"CONSISTENT": 8, "TENSION": 1, "VIOLATED": 2, "OUTSIDE": 1, "NOT_A_BOUND": 1},
        "a_slope_1.0": {"CONSISTENT": 7, "TENSION": 2, "VIOLATED": 2, "OUTSIDE": 1, "NOT_A_BOUND": 1},
        "default_phase44": {"CONSISTENT": 3, "TENSION": 4, "VIOLATED": 4, "OUTSIDE": 1,
                            "NOT_A_BOUND": 1},
    }
    assert artifact["arms"].keys() == expected.keys()
    for label, tally in expected.items():
        assert artifact["arms"][label]["tally_effective_convention"] == tally, label


def test_pinned_effective_values_on_the_default_and_dwarf_compatible_arms(artifact):
    """v = 3 / 10 / 28 km/s values, pinned so a parameter change is visible as a number."""
    pins = {
        "default_phase44": {"3.0": 25.112354420745653, "10.0": 2.465154852340504,
                            "28.0": 100.03606419810939},
        # v=3 at a_slope=1.0 agrees with t120_constraint_scoreboard.py's own recorded
        # "21.1 % over (v=3 at a_slope=1.0, 0.9686 vs 0.8)": 0.9686108 / 0.8 = 1.2108.
        "a_slope_1.0": {"3.0": 0.9686107942907997, "10.0": 0.29272179359555595,
                        "28.0": 99.80168969102034},
    }
    for label, vs in pins.items():
        got = artifact["arms"][label]["effective_cm2_per_g_by_velocity"]
        for v, want in vs.items():
            assert got[v] == pytest.approx(want, rel=1e-12), f"{label} v={v}: {got[v]} != {want}"


def test_scoreboard_and_probe_agree_on_the_default_arm(artifact):
    """The F22 numbers must be the same numbers the single-source T120 scoreboard publishes."""
    sb = _load("t120_constraint_scoreboard").constraint_scoreboard()  # publishes in-process only
    got = artifact["arms"]["default_phase44"]["effective_cm2_per_g_by_velocity"]
    for key, v in (("v3.0_extreme_UFD", "3.0"), ("v10.0_UFD", "10.0"), ("v28.0_Cloud-9", "28.0"),
                   ("v500.0_cluster", "500.0")):
        assert float(sb["observations"][key]["value"]) == pytest.approx(got[v], rel=1e-12), key


def test_published_dwarf_bracket_is_a_genuine_conflict(artifact):
    """Horigome+ 2025 ceiling 0.8 vs Gilman+ 2026 disfavour-below-10, both at ~10 km/s."""
    ratios = artifact["measured_ratios"]
    hor = ratios["mw_satellites_horigome"]["10.0"]
    gil = ratios["dwarf_dispersion_gilman2026"]["10.0"]
    assert hor["bound"] == 0.8 and gil["bound"] == 10.0
    assert gil["bound"] / hor["bound"] == pytest.approx(12.5)
    assert hor["effective"] == gil["effective"], "the two dwarf bounds must be tested on one value"
    assert "12.5" in artifact["headline"]["published_dwarf_data_conflict"]


def test_cluster_and_cosmic_web_agreement_is_a_margin_not_a_fit(artifact):
    eff = artifact["arms"]["default_phase44"]["effective_cm2_per_g_by_velocity"]["500.0"]
    assert eff == pytest.approx(0.009644075978745243, rel=1e-12)
    assert eff / 0.613 < 0.02 and eff / 0.2 < 0.05


def test_headline_numbers_cannot_drift_from_the_rows(artifact):
    """The headline text is generated from the rows; check it still carries the measured ratios."""
    ratios = artifact["measured_ratios"]["mw_satellites_horigome"]
    hor3 = ratios["3.0"]["value_over_bound"]
    hor10 = ratios["10.0"]["value_over_bound"]
    text = artifact["headline"]["dwarf_velocity_systems"]
    assert f"{hor3:.1f}x" in text and f"{hor10:.2f}x" in text


def test_probe_declares_extrapolated_points_as_extensions(artifact):
    for cond in artifact["conditions"]:
        for v, per_v in cond["model_at_these_velocities"].items():
            if float(v) in (3.0, 5.0, 7.0, 10.0, 15.0, 28.0, 100.0, 500.0):
                assert per_v["model"]["point_kind"] == "producer_point"
            else:
                assert per_v["model"]["point_kind"] == "extension", (
                    f"{cond['id']} at v={v} uses an undeclared halo convention")


def test_methodology_caveat_is_not_counted_as_a_bound(artifact):
    kinds = {c["id"]: c["kind"] for c in artifact["conditions"]}
    assert kinds["yang_family_validity_gurian"] == "methodology"
    verdicts = []
    for c in artifact["conditions"]:
        if c["id"] == "yang_family_validity_gurian":
            verdicts = [pv["verdict_by_convention"]["effective_cm2_per_g"]
                        for pv in c["model_at_these_velocities"].values()]
    assert set(verdicts) == {"NOT_A_BOUND"}
