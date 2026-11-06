"""Guard the f_H pairing as a unit (owner decision 2026-11-06; findings F25 and F26).

sigma_eff(v) = f_H^2 * sigma/m(v) is invariant under f_H -> c*f_H, sigma -> sigma/c^2. The
repository therefore cannot store f_H and the sigma amplitudes independently: a half-paired edit
shifts EVERY effective prediction by 6.380057431 while looking like a harmless constant change.

These tests pin the unit:
  1. exactly one live f_H, reachable under three names, all identical;
  2. the archived pair reproduces the same peak and background sigma_eff;
  3. re-pairing leaves every channel sigma_eff and every pass/fail tally unchanged;
  4. no live module may expose 0.297 under a canonical-looking name;
  5. the generated artifact states the pairing it was produced under.
"""
from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
for p in (REPO / "scripts", REPO / "v0.3-prelim" / "code"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import constants  # noqa: E402
from constants import (  # noqa: E402
    F_H,
    F_H_CANONICAL,
    F_H_LEGACY_PLACEHOLDER_0297,
    F_H_PLACEHOLDER_G7,
    PAIRING_K_LEGACY_TO_CANONICAL,
    PAIRING_CONVENTIONS,
    SIGMA_0_CM2_PER_G,
    SIGMA_0_LEGACY_PAIR_052,
    SIGMA_PEAK_CM2_PER_G,
    SIGMA_PEAK_LEGACY_PAIR_174,
)

CANON = 0.7501856343179664
LEGACY = 0.297
ARTIFACT = REPO / "v0.3-prelim" / "data" / "results" / "canonical_numbers.json"


def test_one_live_f_H_under_three_names():
    assert F_H_CANONICAL == CANON
    assert F_H == F_H_CANONICAL
    assert F_H_PLACEHOLDER_G7 == LEGACY, "the G7 alias must point at the archived pair, not the live one"
    assert F_H_LEGACY_PLACEHOLDER_0297 == LEGACY


def test_pairs_are_degenerate_at_peak_and_background():
    peak_legacy = SIGMA_PEAK_LEGACY_PAIR_174 * LEGACY ** 2
    peak_live = SIGMA_PEAK_CM2_PER_G * CANON ** 2
    bg_legacy = SIGMA_0_LEGACY_PAIR_052 * LEGACY ** 2
    bg_live = SIGMA_0_CM2_PER_G * CANON ** 2
    assert abs(peak_live - peak_legacy) < 1e-9, (peak_legacy, peak_live)
    assert abs(bg_live - bg_legacy) < 1e-12, (bg_legacy, bg_live)


def test_pairing_factor_is_the_ratio_of_squared_f_H():
    assert abs(PAIRING_K_LEGACY_TO_CANONICAL - LEGACY ** 2 / CANON ** 2) < 1e-15
    assert abs(1.0 / PAIRING_K_LEGACY_TO_CANONICAL - 6.380057431067687) < 1e-9


def test_repairing_leaves_every_sigma_eff_and_tally_unchanged():
    """Recompute the 8 channels twice: once with the archived pair, once with the live pair."""
    import canonical_numbers as cn

    for set_name, live_params in cn.PARAMETER_SETS.items():
        legacy_params = (
            live_params[0] / PAIRING_K_LEGACY_TO_CANONICAL,
            live_params[1],
            live_params[2],
            live_params[3] / PAIRING_K_LEGACY_TO_CANONICAL,
            live_params[4],
            live_params[5],
        )
        for convention in cn.SIGMA_UNC_CONVENTIONS:
            live_rows, live_tally = cn.evaluate_channels(live_params, convention)
            # Evaluate the archived pair with the archived f_H by hand.
            legacy_rows, legacy_tally = [], {"PASS": 0, "MARGINAL": 0, "FAIL": 0}
            for (v, obs, unc, kind, label, cite), row in zip(cn.OBS_PUBLISHED, live_rows):
                sigma_hh = float(cn.sigma_m_canonical_gaussian(v, *legacy_params))
                sigma_eff = LEGACY ** 2 * sigma_hh
                use_unc = float(obs) if convention == "self_normalized_sigma_unc" else float(unc)
                verdict = cn.channel_verdict(sigma_eff, obs, use_unc, kind)
                legacy_rows.append({"label": label, "sigma_eff": sigma_eff, "verdict": verdict})
                legacy_tally[verdict] += 1
            worst = 0.0
            for lr, rr in zip(live_rows, legacy_rows):
                worst = max(
                    worst,
                    abs(lr["sigma_eff"] - rr["sigma_eff"]) / max(abs(rr["sigma_eff"]), 1e-300),
                )
                assert lr["verdict"] == rr["verdict"], (set_name, convention, lr["label"])
            assert worst < 1e-12, (set_name, convention, worst)
            assert live_tally == legacy_tally, (set_name, convention, live_tally, legacy_tally)


def test_no_live_module_exposes_0297_under_a_canonical_name():
    """0.297 may only appear as an explicitly archived *code* binding, or in prose/comment.

    Scanned through the AST so that prose inside a docstring (several modules explain the
    placeholder in words) is not mistaken for a binding, and a real assignment is not missed
    because of indentation or a trailing comment.
    """
    offenders = []
    scan_dirs = [REPO / "scripts", REPO / "v0.3-prelim" / "code"]
    for d in scan_dirs:
        for path in sorted(d.glob("*.py")):
            if "superseded" in path.parts or "archive" in path.parts:
                continue
            src = path.read_text(encoding="utf-8", errors="replace")
            try:
                tree = ast.parse(src)
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                targets = []
                if isinstance(node, ast.Assign):
                    targets = node.targets
                elif isinstance(node, ast.AnnAssign) and node.value is not None:
                    targets = [node.target]
                else:
                    continue
                value = node.value
                if not isinstance(value, ast.Constant) or not isinstance(value.value, float):
                    continue
                if value.value != 0.297:
                    continue
                for t in targets:
                    name = getattr(t, "id", None)
                    if name is None:
                        continue
                    upper = name.upper()
                    if "LEGACY" in upper or "ARCHIV" in upper or "RETRACT" in upper:
                        continue
                    offenders.append(f"{path.relative_to(REPO)}:{node.lineno}: {name} = 0.297")
    assert not offenders, (
        "a live module still binds 0.297 to a canonical-looking f_H name; it must be renamed to an "
        "archived-pair name or moved to the live canonical value:\n" + "\n".join(offenders)
    )


def test_artifact_declares_the_pairing_it_was_produced_under():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    pairing = data["canonical_abstract_channel_count"]["pairing"]
    assert pairing["live_f_H"] == CANON
    assert pairing["archived_f_H"] == LEGACY
    assert abs(pairing["pairing_k_legacy_to_canonical"] - PAIRING_K_LEGACY_TO_CANONICAL) < 1e-15
    assert abs(1.0 / pairing["pairing_k_legacy_to_canonical"] - 6.380057431067687) < 1e-9
    archived = pairing["archived_pair_amplitudes"]
    # Derived by dividing the live amplitudes by pairing_k, so exact equality is not the right
    # standard: the round trip through the pairing factor leaves ~1e-14 relative residue.
    assert archived["v19_2_D_canonical_phase_44"]["sigma_0"] == pytest.approx(0.052, rel=1e-12)
    assert archived["v19_2_D_canonical_phase_44"]["sigma_peak"] == pytest.approx(174.0, rel=1e-12)
    assert archived["v19_2_E_A2_5param_DE_best_fit"]["sigma_0"] == pytest.approx(0.0265, rel=1e-12)
    assert archived["v19_2_E_A2_5param_DE_best_fit"]["sigma_peak"] == pytest.approx(2025.57, rel=1e-12)
    # The amplitudes stored in the evaluations must be the LIVE pair.
    for ev in data["canonical_abstract_channel_count"]["evaluations"]:
        if ev["parameter_set"] == "v19_2_D_canonical_phase_44":
            assert ev["params"]["sigma_0"] == SIGMA_0_CM2_PER_G
            assert ev["params"]["sigma_peak"] == SIGMA_PEAK_CM2_PER_G


def test_pairing_conventions_registry_names_the_raw_sigma_family():
    reg = PAIRING_CONVENTIONS
    assert reg["canonical_pair_fH_0p750"]["status"] == "LIVE"
    assert reg["legacy_pair_fH_0p297"]["status"] == "ARCHIVED_PAIR"
    raw = reg["raw_sigma_no_fH"]
    assert raw["f_H"] == 1.0
    assert raw["status"].startswith("RESOLVED_BY_EXPLICIT_ARCHIVED_PINNING")
    joined = " ".join(raw["used_by"])
    assert "gravothermal" in joined and "joint-fit" in joined


def test_constants_module_self_check_fires_on_a_half_pair(tmp_path):
    """Corrupt one half of the pairing in a copy of the module; the import must fail loudly."""
    src = (REPO / "scripts" / "constants.py").read_text(encoding="utf-8")
    broken = src.replace(
        "SIGMA_0_CM2_PER_G = 0.008150396851725193",
        "SIGMA_0_CM2_PER_G = 0.052",
        1,
    )
    assert broken != src, "mutation anchor drifted"
    mod_dir = tmp_path / "scripts"
    mod_dir.mkdir()
    (mod_dir / "constants.py").write_text(broken, encoding="utf-8")
    with pytest.raises(AssertionError, match="f_H pairing broken"):
        import importlib.util

        spec = importlib.util.spec_from_file_location("broken_constants", mod_dir / "constants.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)


def test_no_half_paired_default_argument_call():
    """A helper whose default argument binds the LIVE amplitude must not be called bare by an
    archived-pair module (finding F26).

    `constants.g_chi_from_sigma_peak(sigma_peak=SIGMA_PEAK_CM2_PER_G)` takes its default at def
    time from the live pairing. scripts/t233_consistent_dd.py declares ARCHIVED PAIR and prints a
    174 cm^2/g table, yet called this helper with no argument -- so it derived a coupling from
    27.272481773080454 while publishing an archived-pair table, and its published g_chi moved by
    1.589x without any producer noticing. No import-time check can see that, so it is caught here.
    """
    offenders = []
    for d in (REPO / "scripts", REPO / "v0.3-prelim" / "code"):
        for path in sorted(d.glob("*.py")):
            if path.name == "constants.py":
                continue
            try:
                tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                func = node.func
                if isinstance(func, ast.Name) and func.id == "g_chi_from_sigma_peak" and not node.args:
                    offenders.append(f"{path.relative_to(REPO)}:{node.lineno}")
    assert not offenders, (
        "g_chi_from_sigma_peak() was called with no amplitude, so it silently used the live default; "
        "pass the pairing explicitly:\n" + "\n".join(offenders))
