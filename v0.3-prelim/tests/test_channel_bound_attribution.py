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
# F26 (2026-11-06): the f_H split that F23 recorded is repaired by re-pairing the fitted amplitude
# with f_H. These pins now guard the REPAIRED state: one live pair, the archived pair reachable only
# under archived names, and the half-paired edit kept as a labelled counterfactual.
PINNED_LIVE_F_H = 0.7501856343179664
PINNED_LEGACY_F_H = 0.297
PINNED_RATIO = 6.380057431067687
PINNED_PAIRING_K = 0.15673840099471523
PINNED_SIGMA_PEAK_LIVE = 27.272481773080454
PINNED_SIGMA_PEAK_ARCHIVED = 174.0
PINNED_SIGMA_0_LIVE = 0.008150396851725193
PINNED_SIGMA_0_ARCHIVED = 0.052
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
    """F26 guard: ONE live pair, and the archived pair reachable only under archived names.

    F23 found scripts/constants.py carrying f_H = 0.297 while the two-component path used
    f_H = 0.7501856343179664 against the same amplitudes. The repair re-pairs the amplitude with
    f_H, so the two live definitions now agree and the archived value survives only as an
    explicitly-named archived constant. If a future edit re-assigns F_H / F_H_CANONICAL back to
    0.297, or re-assigns an amplitude without moving f_H, this test fails.
    """
    from phase44_two_component import f_H_at_r
    live = f_H_at_r(0.05, "core_forming")
    scripts_layer = _load("_scripts_constants_under_test", REPO_DIR / "scripts" / "constants.py")
    assert live == pytest.approx(PINNED_LIVE_F_H, rel=1e-12)
    assert scripts_layer.F_H == pytest.approx(PINNED_LIVE_F_H, rel=1e-12)
    assert scripts_layer.F_H_CANONICAL == pytest.approx(PINNED_LIVE_F_H, rel=1e-12)
    assert scripts_layer.F_H_LEGACY_PLACEHOLDER_0297 == pytest.approx(PINNED_LEGACY_F_H, rel=1e-12)
    # The archived pair must stay exactly recoverable, and only under its archived names.
    assert scripts_layer.SIGMA_PEAK_LEGACY_PAIR_174 == pytest.approx(PINNED_SIGMA_PEAK_ARCHIVED, rel=1e-12)
    assert scripts_layer.SIGMA_0_LEGACY_PAIR_052 == pytest.approx(PINNED_SIGMA_0_ARCHIVED, rel=1e-12)
    assert scripts_layer.SIGMA_PEAK_CM2_PER_G == pytest.approx(PINNED_SIGMA_PEAK_LIVE, rel=1e-12)
    assert scripts_layer.SIGMA_0_CM2_PER_G == pytest.approx(PINNED_SIGMA_0_LIVE, rel=1e-12)
    ratio = (live * live) / (scripts_layer.F_H_LEGACY_PLACEHOLDER_0297 ** 2)
    assert ratio == pytest.approx(PINNED_RATIO, rel=1e-9)
    # Amplitudes and f_H moved together: the pairing factor is the inverse of the f_H^2 ratio.
    k_amplitude = scripts_layer.SIGMA_PEAK_CM2_PER_G / scripts_layer.SIGMA_PEAK_LEGACY_PAIR_174
    assert k_amplitude == pytest.approx(PINNED_PAIRING_K, rel=1e-12)
    assert k_amplitude * ratio == pytest.approx(1.0, rel=1e-9)


def test_cloud9_bound_artifact_declares_the_convention_split():
    """The re-derivation must publish the pairing it used, live and archived, with the invariant."""
    import json
    report = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    block = report["f_H_conventions"]
    assert block["status"] == "RESOLVED_SINGLE_PAIRING_2026-11-06", (
        "the pairing must be declared resolved; an UNRESOLVED_CONVENTION_SPLIT status means the "
        "F23 split came back")
    live = block["live_pairing"]
    archived = block["archived_pairing"]
    assert live["f_H"] == pytest.approx(PINNED_LIVE_F_H, rel=1e-12)
    assert live["sigma_peak_cm2_per_g"] == pytest.approx(PINNED_SIGMA_PEAK_LIVE, rel=1e-12)
    assert live["sigma_0_cm2_per_g"] == pytest.approx(PINNED_SIGMA_0_LIVE, rel=1e-12)
    assert archived["f_H"] == pytest.approx(PINNED_LEGACY_F_H, rel=1e-12)
    assert archived["sigma_peak_cm2_per_g"] == pytest.approx(PINNED_SIGMA_PEAK_ARCHIVED, rel=1e-12)
    assert archived["sigma_0_cm2_per_g"] == pytest.approx(PINNED_SIGMA_0_ARCHIVED, rel=1e-12)
    assert block["ratio_between_live_conventions"] == pytest.approx(1.0, rel=1e-12)
    assert block["pairing_k_archived_to_live"] == pytest.approx(PINNED_PAIRING_K, rel=1e-12)
    check = block["pairing_invariance_check"]
    assert check["abs difference"] < 1e-9, (
        "the two pairings must give the same sigma_eff at the resonance peak; a non-zero gap means "
        "one side was edited alone")


def test_legacy_convention_fails_the_cloud9_bar_that_the_live_one_passes():
    """Keep the F23 lesson as a labelled counterfactual: a half-paired edit fails the bar by 6.4x."""
    live = PINNED_Q_EFFECTIVE_LIVE
    half_paired = PINNED_Q_EFFECTIVE_LEGACY
    assert live >= 100.0
    assert half_paired < 100.0
    assert live / half_paired == pytest.approx(PINNED_RATIO, rel=1e-9)


def test_producer_recomputation_matches_the_artifact():
    """Live re-run must reproduce the stored numbers (guards producer edits)."""
    bound = _load("t120_cloud9_bound_under_test", CODE_DIR / "t120_cloud9_bound.py")
    fresh = bound.f_H_conventions(bound.model_quantities(None)["Q_total_cm2_per_g"])
    assert fresh["ratio_between_live_conventions"] == pytest.approx(1.0, rel=1e-12)
    assert fresh["live_pairing"]["f_H_squared"] * bound.model_quantities(None)["Q_total_cm2_per_g"] \
        == pytest.approx(PINNED_Q_EFFECTIVE_LIVE, rel=1e-9)
    assert fresh["archived_pairing"]["half_paired_counterfactual_Q_effective_cm2_per_g"] \
        == pytest.approx(PINNED_Q_EFFECTIVE_LEGACY, rel=1e-9)
    assert fresh["status"] == "RESOLVED_SINGLE_PAIRING_2026-11-06"


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
