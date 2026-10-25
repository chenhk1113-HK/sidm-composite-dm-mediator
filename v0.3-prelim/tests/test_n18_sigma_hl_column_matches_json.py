"""Pin the paper's §2.6a Fornax σ_HL column to the generator's own JSON output.

Why this test exists
--------------------
The §2.6a findings table in ``PAPER_V1_DRAFT.md`` carries a "Fornax σ_HL req" column
whose values are read off ``v192_a_phase44_sigma_peak_sensitivity.json``.  That column
silently drifted: the generator's resonance anchor was changed from ``v = 28`` to the
canonical ``v = 29.4`` (commit R88(26)), which moved σ/m(15) from 2.5597 to 2.8455 and
therefore the *required* Fornax σ_HL from −0.4723 to −0.5336 — a 13 % shift, well above
rounding.  The paper's σ/m columns were regenerated at R88(31) but the σ_HL column was
carried over from the pre-R88(26) run, and the checked-in JSON itself was never
regenerated after the anchor change.  The result was a table whose columns came from two
different parameterizations, and a narrative claim ("at σ_peak ∈ {30, 50}, σ_HL_required
is marginal") that is false under the canonical generator — there is no σ_peak in the
swept range that leaves the Fornax σ_HL marginal.

What it checks
--------------
1. Every ``σ_peak`` row of the §2.6a table quotes the σ_HL value the JSON holds.
2. The ``(marginal)`` / ``(substantive)`` label matches the JSON's own flag.

Both sides are read at test time (paper table + JSON), so this fails if either drifts
beyond the displayed precision (half a unit in the last place). It deliberately does NOT
re-assert a hard-coded literal: a literal would have to be edited by hand every time the
anchor moves, which is how the drift survived in the first place.

Two limits worth stating: it does not detect a sub-0.005 drift, and it does not detect a
stale (un-regenerated) JSON on disk -- if the JSON is out of date relative to the
generator, the table can agree with it and this test still passes. The guard against a
stale JSON is to regenerate it and re-run the suite, not to rely on this test.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
PAPER = REPO / "v0.3-prelim" / "docs" / "PAPER_V1_DRAFT.md"
SWEEP_JSON = (
    REPO / "v0.3-prelim" / "data" / "results"
    / "v192_a_phase44_sigma_peak_sensitivity.json"
)

# A row of the §2.6a table: the σ_HL cell renders as e.g. "−0.53 (substantive)".
CELL = re.compile(r"([\u2212-])(\d+\.\d\d)\s*\((marginal|substantive)\)")
ROW = re.compile(r"^\|\s*\**\s*(\d+)\s*\**\s*\|")


def _load_json() -> dict:
    assert SWEEP_JSON.exists(), f"missing generator output: {SWEEP_JSON}"
    return json.loads(SWEEP_JSON.read_text(encoding="utf-8"))


def _paper_sigma_hl_by_peak() -> dict[int, tuple[float, str]]:
    """{sigma_peak: (sigma_HL, label)} from the §2.6a table rows."""
    assert PAPER.exists(), f"missing paper: {PAPER}"
    out: dict[int, tuple[float, str]] = {}
    for line in PAPER.read_text(encoding="utf-8").split("\n"):
        if not line.startswith("|"):
            continue
        m_row = ROW.match(line)
        if not m_row:
            continue
        m_cell = CELL.search(line)
        if not m_cell:
            continue
        sp = int(m_row.group(1))
        sign = -1.0 if m_cell.group(1) == "\u2212" else 1.0
        out[sp] = (sign * float(m_cell.group(2)), m_cell.group(3))
    return out


def _json_expected() -> dict[int, tuple[float, str]]:
    data = _load_json()
    out: dict[int, tuple[float, str]] = {}
    for row in data["results"]:
        sp = row["sigma_peak_HH_1_cm2_per_g"]
        if sp is None:
            continue
        val = row["Fornax_sigma_HL_required_cm2_per_g"]
        label = "marginal" if row["Fornax_sigma_HL_marginal?"] else "substantive"
        out[int(sp)] = (val, label)
    return out


def test_paper_table_covers_every_swept_sigma_peak():
    paper = _paper_sigma_hl_by_peak()
    expected = _json_expected()
    assert expected, "generator JSON carries no results"
    assert set(expected) <= set(paper), (
        "§2.6a table is missing σ_peak rows present in the JSON: "
        f"{sorted(set(expected) - set(paper))}"
    )


def test_sigma_hl_values_match_json():
    """Each quoted σ_HL must equal the JSON value at 2-dp display precision."""
    paper = _paper_sigma_hl_by_peak()
    expected = _json_expected()
    mismatches = []
    for sp, (want, _label) in sorted(expected.items()):
        got, _glabel = paper[sp]
        if abs(got - want) > 0.005:  # half a unit in the last displayed place
            mismatches.append(f"σ_peak={sp}: paper {got:+.2f} vs JSON {want:+.4f}")
    assert not mismatches, (
        "§2.6a Fornax σ_HL column disagrees with the generator output "
        "(regenerate the JSON and/or re-read the table):\n  " + "\n  ".join(mismatches)
    )


def test_marginal_labels_match_json():
    """The (marginal)/(substantive) label must track the JSON's own flag."""
    paper = _paper_sigma_hl_by_peak()
    expected = _json_expected()
    bad = [
        f"σ_peak={sp}: paper '{paper[sp][1]}' vs JSON '{want_label}'"
        for sp, (_v, want_label) in sorted(expected.items())
        if paper[sp][1] != want_label
    ]
    assert not bad, "§2.6a σ_HL labels disagree with the JSON flag:\n  " + "\n  ".join(bad)


def test_no_stale_pre_r88_26_fornax_values_in_paper():
    """Guard the specific retracted values so a re-introduction is loud."""
    txt = PAPER.read_text(encoding="utf-8")
    # -0.47 / -0.08 / -0.13 / -0.68 were the pre-R88(26) (v = 28 anchor) Fornax σ_HL values.
    stale = CELL.findall(txt)
    bad = [
        f"{s}{v} ({lbl})"
        for s, v, lbl in stale
        if f"{v}" in {"0.47", "0.08", "0.13", "0.68"}
    ]
    assert not bad, (
        "pre-R88(26) (v = 28 anchor) Fornax σ_HL values are back in the paper: "
        f"{bad}. The canonical anchor is v = 29.4; regenerate the JSON."
    )
