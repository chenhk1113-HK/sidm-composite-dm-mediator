"""F23 / F24 guards — the f_H convention split and the Channel 6/7 bound attribution.

F23: sigma_eff = f_H^2 * sigma/m has TWO live values in this repo.  The Cloud-9 `>= 100 cm^2/g`
     verdict flips depending on which one a producer uses.  Both values, the ratio, and the two
     resulting Cloud-9 effective cross sections are pinned here by LIVE recomputation.

F24: Channel 6 (arXiv:2510.11006) and Channel 7 (arXiv:2503.13650) carried source claims that the
     papers do not make.  The corrected labels are pinned, the false labels are forbidden, and the
     numeric constants are pinned so a future "documentation fix" cannot quietly change physics.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

TESTS_DIR = Path(__file__).resolve().parent
PROJECT_DIR = TESTS_DIR.parent                 # v0.3-prelim/
REPO_DIR = PROJECT_DIR.parent                  # repository root
CODE_DIR = PROJECT_DIR / "code"
RESULTS_DIR = PROJECT_DIR / "data" / "results"

CONFIG_PATH = REPO_DIR / "config.py"
CHANNELS_PATH = CODE_DIR / "channels_extended.py"
ARTIFACT = RESULTS_DIR / "t120_cloud9_bound_rederivation.json"

# Measured 2026-11-06 by running v0.3-prelim/code/t120_cloud9_bound.py.
PINNED_LIVE_F_H = 0.7501856343179664
PINNED_LEGACY_F_H = 0.297
PINNED_RATIO = 6.380057431067687
PINNED_Q_EFFECTIVE_LIVE = 100.03606419810939
PINNED_Q_EFFECTIVE_LEGACY = 15.679492744216347


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# --------------------------------------------------------------------------- F23


def test_both_f_H_conventions_are_live_and_pinned():
    """Both definitions still exist, and their values have not drifted."""
    from phase44_two_component import f_H_at_r
    live = f_H_at_r(0.05, "core_forming")
    scripts_layer = _load("_scripts_constants_under_test", REPO_DIR / "scripts" / "constants.py")
    assert live == pytest.approx(PINNED_LIVE_F_H, rel=1e-12)
    assert scripts_layer.F_H == pytest.approx(PINNED_LEGACY_F_H, rel=1e-12)
    ratio = (live * live) / (scripts_layer.F_H ** 2)
    assert ratio == pytest.approx(PINNED_RATIO, rel=1e-9)


def test_cloud9_bound_artifact_declares_the_convention_split():
    """The re-derivation must publish BOTH conventions, not silently pick one."""
    import json
    report = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    block = report["f_H_conventions"]
    assert block["status"] == "UNRESOLVED_CONVENTION_SPLIT"
    assert block["live_value_used_by_t120"]["value"] == pytest.approx(PINNED_LIVE_F_H, rel=1e-12)
    assert block["legacy_value_still_in_live_code"]["value"] == pytest.approx(PINNED_LEGACY_F_H, rel=1e-12)
    assert block["ratio_between_conventions"] == pytest.approx(PINNED_RATIO, rel=1e-9)
    assert block["live_value_used_by_t120"]["cloud9_Q_effective_cm2_per_g"] == pytest.approx(
        PINNED_Q_EFFECTIVE_LIVE, rel=1e-9)
    assert block["legacy_value_still_in_live_code"]["cloud9_Q_effective_cm2_per_g"] == pytest.approx(
        PINNED_Q_EFFECTIVE_LEGACY, rel=1e-9)


def test_legacy_convention_fails_the_cloud9_bar_that_the_live_one_passes():
    """The whole point of F23: the verdict depends on the convention, by ~6.4x."""
    live = PINNED_Q_EFFECTIVE_LIVE
    legacy = PINNED_Q_EFFECTIVE_LEGACY
    assert live >= 100.0
    assert legacy < 100.0
    assert live / legacy == pytest.approx(PINNED_RATIO, rel=1e-9)


def test_producer_recomputation_matches_the_artifact():
    """Live re-run must reproduce the stored numbers (guards producer edits)."""
    bound = _load("t120_cloud9_bound_under_test", CODE_DIR / "t120_cloud9_bound.py")
    fresh = bound.f_H_conventions(bound.model_quantities(None)["Q_total_cm2_per_g"])
    assert fresh["ratio_between_conventions"] == pytest.approx(PINNED_RATIO, rel=1e-12)
    assert fresh["live_value_used_by_t120"]["cloud9_Q_effective_cm2_per_g"] == pytest.approx(
        PINNED_Q_EFFECTIVE_LIVE, rel=1e-12)


# --------------------------------------------------------------------------- F24


RETRACTION_MARKERS = ("NOT in the paper", "not in the paper", "WRONG", "wrong", "previously",
                      "conflating", "mislabelled", "misattributed", "not a 95%", "removed")


def _bare_occurrences(src: str, phrase: str) -> list[str]:
    """Lines that state `phrase` as a claim, i.e. without a same-line retraction marker."""
    return [line for line in src.splitlines()
            if phrase in line and not any(marker in line for marker in RETRACTION_MARKERS)]


def test_channel6_attribution_is_the_real_paper():
    src = _read(CHANNELS_PATH)
    assert "Hai-Bo Yu" in src
    assert _bare_occurrences(src, "Yang, Yang, Yu et al.") == [], (
        "Channel 6 restored the fabricated author list as a live claim")
    assert _bare_occurrences(src, "Zhang+ 2025") == [], (
        "arXiv:2510.11006 re-adopted the wrong paper's name")
    assert "arXiv:2409.19493" in src, "the GD-1 perturber paper must be named separately"
    assert "PROJECT-CONSTRUCTED prior" in _read(CONFIG_PATH) or "project-constructed" in src.lower()


def test_channel7_restored_claim_is_absent_and_published_limits_are_quoted():
    src = _read(CHANNELS_PATH)
    assert _bare_occurrences(src, "CDM preferred over SIDM when") == [], (
        "the unsupported 'V_50 = 18 km/s -> sigma0/m >~ 1.0 cm^2/g' claim returned as a live claim")
    assert "0.8 cm²/g for w = 10 km/s" in src
    assert "0.04 cm²/g for the velocity-independent case" in src
    assert "V_50 = 10.5 km/s" in src


def test_config_bound_labels_name_the_paper_not_a_mislabelled_statistic():
    src = _read(CONFIG_PATH)
    assert _bare_occurrences(src, "95% upper limit") == [], (
        "config.py re-labelled the 0.2 cm^2/g CDM-preference threshold as a 95% upper limit")
    assert "arXiv:2503.13650" in src
    assert "arXiv:2510.11006" in src


def test_numeric_constants_did_not_move_while_labels_were_corrected():
    """A documentation fix must not change the physics."""
    cfg = _load("config_under_f24_test", CONFIG_PATH)
    assert cfg.LENS_SIGMA_M_LOG_PEAK == 1.7
    assert cfg.LENS_SIGMA_M_LOG_WIDTH == 0.7
    assert cfg.DSPH_SIGMA_M_UPPER_LIMIT == 0.2
    assert cfg.DSPH_VMAX_KMS == 18.0


def test_fabricated_one_cm2_per_g_agreement_claim_stays_retired():
    """The paper contains no sigma/m ~ 1 cm^2/g; that agreement claim must not return."""
    src = _read(CHANNELS_PATH)
    assert _bare_occurrences(src, "consistent with our T8/T11 posterior median") == [], (
        "the invented '~1 cm^2/g from arXiv:2510.11006' agreement claim returned as a live claim")


def test_kb_entry_exists_for_the_channel6_paper():
    kb = REPO_DIR / "docs" / "papers" / "verified" / "2510.11006_yu_2025_three_birds.md"
    assert kb.exists(), "Channel 6's paper must have a knowledge-base entry"
    text = _read(kb)
    assert "SINGLE AUTHOR" in text
    assert "What the paper does NOT publish" in text
