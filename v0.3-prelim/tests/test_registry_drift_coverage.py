"""Finding F29 — the knowledge base must not be able to drift away from the canonical pairing.

Why this test exists: `docs/V19_2_F_REFERENCE_DATA_REGISTRY.md` is declared the project's single source of
truth for numbers, and it was in none of `drift_guard.py`'s document lists. It carried
`F_H_CANONICAL = 0.297`, `SIGMA_0 = 0.052`, `SIGMA_PEAK = 174.0` as live constants for a full day after
finding F26 moved them to the archived pair, while `drift_guard.py --strict` reported "No drift detected".
This test pins three things so that cannot happen silently again:

1. the guard is wired into the drift layer (not just written and abandoned);
2. the registry's pairing rows equal the canonical artifact's live pair;
3. an archived-pair literal quoted in a sigma/f_H paragraph must be labelled in that paragraph — checked
   here in pytest as well as in the drift layer, because a doc edit should fail a test and not only a gate.

It also pins the artifact fix: the `v19_2_E_A2_5param_DE_best_fit` block may not hold archived amplitudes
next to a live `f_H` without saying which pairing each value belongs to.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
REGISTRY = REPO / "docs" / "V19_2_F_REFERENCE_DATA_REGISTRY.md"
DRIFT = REPO / "scripts" / "drift_guard.py"
CANON_JSON = REPO / "v0.3-prelim" / "data" / "results" / "canonical_numbers.json"

ARCHIVED_LITERALS = ("0.297", "174.0", "174 ", "2025.57", "0.052")
LABELS = ("ARCHIVED", "archived", "LEGACY", "legacy", "SUPERSEDED", "superseded",
          "retracted", "PAIRING", "pairing", "live pair", "LIVE PAIR")

pytestmark = pytest.mark.skipif(not REGISTRY.exists(), reason="registry document missing")


@pytest.fixture(scope="module")
def registry_text():
    return REGISTRY.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def canonical():
    import json
    return json.loads(CANON_JSON.read_text(encoding="utf-8"))


def test_registry_pairing_guard_is_wired_into_the_drift_layer():
    src = DRIFT.read_text(encoding="utf-8")
    assert "def check_registry_pairing_values(" in src, "the registry pairing guard is missing"
    assert "check_registry_pairing_values(registry_text" in src, (
        "the guard exists but main() never calls it, so the registry is still unchecked")
    assert "V19_2_F_REFERENCE_DATA_REGISTRY.md" in src, "the guard does not target the registry document"
    # The CRLF trap that made the first version of this guard a no-op.
    assert 'replace("\\r\\n", "\\n")' in src, (
        "paragraph splitting is not newline-normalised: in a CRLF document split('\\n\\n') matches "
        "nothing and every unlabelled archived literal passes")


def test_registry_pairing_rows_match_the_live_pair(registry_text, canonical):
    live = canonical["v19_2_D_canonical_phase_44_free_fit"]
    want = {"F_H_CANONICAL": live["F_H"],
            "SIGMA_0_CM2_PER_G": live["sigma_0"],
            "SIGMA_PEAK_CM2_PER_G": live["sigma_peak"]}
    seen = {}
    for line in registry_text.splitlines():
        for key, target in want.items():
            if line.strip().startswith(f"| {key} |"):
                cell = line.split("|")[2].strip()
                assert re.fullmatch(r"[0-9.]+", cell), f"{key} row is not a bare number: {cell!r}"
                seen[key] = float(cell)
                assert seen[key] == pytest.approx(target, abs=1e-9), (
                    f"{key}: registry says {cell} but the live pair is {target} "
                    "(archived pair = live x 6.380057431067687; finding F26/F29)")
    assert set(seen) == set(want), f"registry is missing pairing rows: {set(want) - set(seen)}"


def test_archived_literals_in_the_registry_are_labelled_where_they_are_used(registry_text):
    offenders = []
    for para in registry_text.replace("\r\n", "\n").split("\n\n"):
        if not any(lit in para for lit in ARCHIVED_LITERALS):
            continue
        if "sigma" not in para.lower() and "σ" not in para and "F_H" not in para:
            continue
        if any(lbl in para for lbl in LABELS):
            continue
        offenders.append(" ".join(para.split())[:180])
    assert not offenders, "unlabelled archived-pair values in the KB read as live constants:\n" + "\n".join(offenders)


def test_canonical_artifact_declares_the_pairing_of_its_a2_amplitudes(canonical):
    a2 = canonical["v19_2_E_A2_5param_DE_best_fit"]
    assert a2["pairing_of_the_values_above"] == "ARCHIVED PAIR"
    assert a2["F_H"] == pytest.approx(0.297, rel=1e-12), (
        "the archived amplitudes 0.0265 / 2025.57 must sit with the archived f_H, not the live one")
    live = a2["live_pair_equivalent"]
    assert live["sigma_0"] == pytest.approx(a2["sigma_0"] * 0.15673840099471523, rel=1e-9)
    assert live["sigma_peak"] == pytest.approx(a2["sigma_peak"] * 0.15673840099471523, rel=1e-9)
    assert live["F_H"] == pytest.approx(0.7501856343179664, rel=1e-12)


def test_phase44_interpretation_does_not_attribute_the_cap_to_the_live_pair(canonical):
    text = canonical["v19_2_D_canonical_phase_44_free_fit"]["interpretation"]
    assert "ARCHIVED pair" in text, "the 174 cm^2/g causality cap must be labelled as the archived pair's"
    assert "27.272481773080454" in text, "the live amplitude the cap does NOT constrain should be named"
