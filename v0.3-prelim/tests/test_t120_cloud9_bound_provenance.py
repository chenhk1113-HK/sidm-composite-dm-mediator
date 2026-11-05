"""F21 — the Cloud-9 cross-section bound is internal, and its citation was wrong.

What this test protects (all values measured live, all source facts read from the local
verified PDFs with pdftotext):

1. `128 ± 30 cm^2/g`, labelled "BLN24 / Ohana+ 2026" in T205_full_likelihood_published.py, is NOT
   published data. `128.1262923221052` is this project's own canonical Phase 44 output
   (`data/results/sigma_m_phase44.json`, key `v28.0_Cloud-9`). Grading the fit against a bar the
   fit itself produced is circular, so the channel must be declared INTERNAL in code.
2. The papers publish no Cloud-9 cross section:
     arXiv:2406.18643 (BLN24)      — zero mentions of self-interaction; Cloud-9 as a
                                     normal-concentration CDM RELHIC, M200 4-6e9 Msun, cNFW 10-17,
                                     "consistent with the CDM mass-concentration relation".
     arXiv:2608.04362 (Ohana+ 2026) — posterior peaks near 200 cm^2/g, "disfavors both very small
                                     and very large cross sections"; CDM needs 7.3 sigma below the
                                     c-M median; no floor at 100 or 128.
     arXiv:1412.1477 (Elbert+ 2015) — 50 cm^2/g is its LARGEST simulated cross section (mild core
                                     collapse) plus a viability statement; not a required floor.
3. The quantity the Cloud-9 verdict actually scores is the two-component effective value
   f_H^2 * sigma/m(v=28), not the total, and not the canonical Gaussian number the paper quotes.
   The convention factor between them is ~1.78, which dwarfs the 0.2% near-miss.
4. The doc sweep landed: the paper now labels the 100 bar as an internal anchor and no longer
   attributes a Cloud-9 cross section to BLN24.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

_TESTS_DIR = Path(__file__).resolve().parent
PROJECT_DIR = _TESTS_DIR.parent
RESULTS_DIR = PROJECT_DIR / "data" / "results"
CODE_DIR = PROJECT_DIR / "code"
PAPER = PROJECT_DIR / "docs" / "PAPER_V1_DRAFT.md"

PHASE44_CLOUD9_MODEL_OUTPUT = 128.1262923221052
# Pinned from the producer itself (v0.3-prelim/code/t120_cloud9_bound.py, arm default_phase44).
# Note on the background term: the producer uses t120_4_joint_fit.total_sigma_m_gaussian, whose
# background is yukawa_bg(v). An independent scratch check that instead approximated the background
# as sigma_0 * (100/v)^a_slope gave Q_total = 177.75381337182492 — a 7.5e-5 absolute difference
# (4.2e-7 relative). The producer's form is the canonical one and is what these pins follow.
PINNED_Q_TOTAL_DEFAULT = 177.75388842653638
PINNED_Q_CANONICAL = 166.01808042318618
PINNED_Q_EFFECTIVE_DEFAULT = 100.03606419810939
PINNED_F_H = 0.7501856343179664
PINNED_CONVENTION_FACTOR = 1.776898060228721
PINNED_DEFAULT_MARGIN_PCT = 0.036064198109386325
TOLERANCE_REL = 1e-9


def _load(name):
    path = CODE_DIR / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def bound():
    mod = _load("t120_cloud9_bound")
    return mod.build_report()


@pytest.fixture(scope="module")
def scoreboard():
    return _load("t120_constraint_scoreboard")


def _rel_close(a, b):
    return abs(a - b) <= TOLERANCE_REL * max(1.0, abs(a), abs(b))


# --------------------------------------------------------------------------
# 1. the re-derivation is reproducible and pinned
# --------------------------------------------------------------------------

def test_rederivation_producer_reruns_and_produces_the_artifact():
    mod = _load("t120_cloud9_bound")
    mod.main()
    assert (RESULTS_DIR / "t120_cloud9_bound_rederivation.json").exists()


def test_measured_cloud9_quantities_are_pinned(bound):
    arm = bound["model_values_by_arm"]["default_phase44"]
    assert _rel_close(arm["Q_total_cm2_per_g"], PINNED_Q_TOTAL_DEFAULT)
    assert _rel_close(arm["Q_canonical_gaussian_cm2_per_g"], PINNED_Q_CANONICAL)
    assert _rel_close(arm["Q_effective_fH_squared_cm2_per_g"], PINNED_Q_EFFECTIVE_DEFAULT)
    assert _rel_close(arm["f_H"], PINNED_F_H)
    assert _rel_close(bound["conventions"]["convention_factor"], PINNED_CONVENTION_FACTOR)


def test_the_near_miss_is_not_the_whole_story(bound):
    """The convention factor (1.78) is ~900x larger than the 0.036% default-arm margin."""
    margin = bound["model_values_by_arm"]["default_phase44"]["margin_vs_internal_bar_pct"]["Q_effective"]
    assert _rel_close(margin, PINNED_DEFAULT_MARGIN_PCT)
    factor = bound["conventions"]["convention_factor"]
    miss_pct = abs(bound["model_values_by_arm"]["default_phase44"]
                   ["margin_vs_internal_bar_pct"]["Q_effective"])
    assert factor - 1.0 > 0.7
    assert (factor - 1.0) / (miss_pct / 100.0) > 100


def test_internal_bar_is_declared_internal(bound):
    bar = bound["internal_bar"]
    assert bar["status"] == "INTERNAL"
    assert "project-internal" in bar["provenance"]
    assert bound["internal_t205_anchor"]["status"] == "MISATTRIBUTED"


# --------------------------------------------------------------------------
# 2. the code declares the anchor, and the "observation" is a model output
# --------------------------------------------------------------------------

def test_phase44_model_output_equals_the_t205_observation():
    phase44 = json.loads((RESULTS_DIR / "sigma_m_phase44.json").read_text(encoding="utf-8"))
    assert _rel_close(phase44["v28.0_Cloud-9"], PHASE44_CLOUD9_MODEL_OUTPUT)
    # The "observation" 128.0 and the model output differ by 0.126, far inside the ±30 the code assumed.
    t205 = _load("T205_full_likelihood_published")
    assert _rel_close(t205.CLOUD9_ANCHOR_IS_MODEL_OUTPUT_CM2_PER_G, phase44["v28.0_Cloud-9"])
    assert _rel_close(t205.CLOUD9_ANCHOR_VALUE_CM2_PER_G, 128.0)


def test_t205_declares_the_cloud9_slot_internal():
    t205 = _load("T205_full_likelihood_published")
    assert t205.CLOUD9_ANCHOR_STATUS == "INTERNAL"
    assert t205.CLOUD9_NO_PUBLISHED_FLOOR is True
    assert t205.CLOUD9_PUBLISHED_POSTERIOR_PEAK_CM2_PER_G == 200.0
    cloud9 = [row for row in t205.OBS_PUBLISHED if row[4] == "Cloud-9 v=28"]
    assert len(cloud9) == 1
    assert "INTERNAL anchor (F21)" in cloud9[0][5]
    assert cloud9[0][5].startswith("INTERNAL anchor (F21)")
    assert "INTERNAL anchor (F21)" in t205.__doc__


def test_scoreboard_carries_bound_provenance_on_every_row(scoreboard):
    sb = scoreboard.constraint_scoreboard()
    assert set(sb["observations"]) == {k for k, *_ in scoreboard.OBSERVATIONS}
    for key, obs in sb["observations"].items():
        assert obs["bound_provenance"] == scoreboard.BOUND_PROVENANCE[key]
    assert "INTERNAL (F21)" in sb["observations"]["v28.0_Cloud-9"]["bound_provenance"]
    for key in ("v3.0_extreme_UFD", "v15.0_classical_dSph"):
        assert "Horigome+ 2025" in sb["observations"][key]["bound_provenance"]
    four = scoreboard.four_constraint_scoreboard()
    assert "INTERNAL (F21)" in four["observations"]["Cloud-9"]["bound_provenance"]


def test_published_ceiling_for_the_dwarf_channels_is_real(bound):
    """0.8 cm^2/g IS published (Horigome+ 2025 95% upper limit, w = 10 km/s); the per-bin T205
    values are this project's own splitting and must not be quoted as separate measurements."""
    scoreboard = _load("t120_constraint_scoreboard")
    ceiling = scoreboard.BOUND_PROVENANCE["v15.0_classical_dSph"]
    assert "published" in ceiling and "0.8 cm^2/g" in ceiling
    published = bound["published_anchors"]
    assert published["elbert_2015"]["is_100_a_floor_in_this_paper"] is False
    assert published["benitez_llambay_2024_bln24"][
        "contains_any_self_interaction_cross_section"] is False
    assert published["ohana_2026"]["is_100_a_floor_in_this_paper"] is False
    assert published["ohana_2026"]["published_posterior_peak_cm2_per_g"] == 200.0


# --------------------------------------------------------------------------
# 3. the producer no longer prints hard-coded PASS verdicts
# --------------------------------------------------------------------------

def test_joint_fit_main_prints_computed_verdicts_not_asserted_ones():
    out = subprocess.run(
        [sys.executable, str(CODE_DIR / "t120_4_joint_fit.py")],
        capture_output=True, text=True, timeout=300,
    )
    assert out.returncode == 0
    assert "✓ PASS" not in out.stdout
    assert "All 4 constraints simultaneously satisfied" not in out.stdout
    assert "PASS" in out.stdout or "FAIL" in out.stdout
    assert "all_pass (this arm)" in out.stdout


# --------------------------------------------------------------------------
# 4. the paper sweep landed
# --------------------------------------------------------------------------

def test_paper_no_longer_attributes_a_cloud9_cross_section_to_bln24():
    text = PAPER.read_text(encoding="utf-8")
    assert "publishes **no self-interaction cross section at all**" in text
    assert "internal anchor, F21" in text
    assert text.count("internal anchor, F21") >= 2
    assert "viability value, not a published bound" in text
    assert "the project's **internal** floor" in text


def test_finding_id_f21_exists_and_is_unique_in_the_integrity_report():
    report = PROJECT_DIR.parent / "docs" / "INTEGRITY_FINDINGS_2026-11-04.md"
    text = report.read_text(encoding="utf-8")
    headings = [line for line in text.split("\n") if line.startswith("## F")]
    f21 = [h for h in headings if h.startswith("## F21")]
    assert len(f21) == 1, f"expected exactly one F21 heading, found {f21}"
    f_numbers = [h.split()[1].split(" ")[0] for h in headings]
    assert len(f_numbers) == len(set(f_numbers)), f"duplicate finding ids: {f_numbers}"
