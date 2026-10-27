"""Pin the paper's §3 σ/m table (8 rows) to the canonical code.

Why this test exists
--------------------
Coverage-gap register row **CG-3**: *"the dSph σ/m table (§3, 8 rows) and the
factor ranges derived from it — the paper's headline quantitative table is not
read by the gate at all."* The §3 table is the table a reader uses to see which
observational channels the framework passes and by how much, and until now
nothing checked it: ``audit_claims.py`` tracks an enumerated set of headline
claims and does not include these eight rows, ``drift_guard.py`` watches a
different set of standing numbers, and the §9 recomputation that produces the
same quantities is a manual step.  A silent drift in this table would therefore
ship exactly as the §2.6a σ_HL column did (see
``test_n18_sigma_hl_column_matches_json.py``), whose column sat 13 % wrong in a
submission-ready paper while every gate reported green.

What it checks
--------------
1. The §3 table still has 8 data rows and carries every velocity the paper
   quotes (so a row cannot be dropped silently).
2. Each ``σ/m`` cell equals ``canonical_numbers.sigma_m_canonical_gaussian(v)``
   at the cell's OWN displayed precision (half a unit in the last displayed
   place) — the table mixes 2-dp and 1-dp cells, so a fixed tolerance would
   either pass a real error in the coarse cells or fail correct rounding in
   the fine ones.
3. Each ``× above`` factor equals ``σ/m / 0.2`` at its own displayed
   precision, where 0.2 cm²/g is the threshold the table's header names.

Both sides are read at test time (paper table + canonical code), so this fails
if EITHER drifts.  It deliberately does NOT re-assert a hard-coded literal: a
literal has to be hand-edited every time an anchor moves, which is precisely
how the §2.6a column drifted in the first place.

Limits worth stating
--------------------
- It pins σ/m to ``canonical_numbers``, which reads ``constants.py``.  If the
  canonical form itself changes, this test follows it; that is intended.
- It cannot detect a sub-half-ulp drift (below the table's own precision).
- It covers the §3 table only.  The bullet list that follows it ("background
  only" values at v = 9, 10, 15, 18, 25, 28) is a DIFFERENT quantity — no
  resonance contribution — and is tracked separately as coverage-gap row
  **CG-14**, because its provenance could not be established and pinning it
  here would amount to guessing which side moved.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
PAPER = REPO / "v0.3-prelim" / "docs" / "PAPER_V1_DRAFT.md"

# The §3 table's header — used to locate the table unambiguously rather than
# by line number, which moves.
HEADER_MARKER = "vs Horigome threshold"

# A data row: | v | channel | sigma/m | factor |
ROW = re.compile(
    r"^\|\s*(\d+(?:\.\d+)?)\s*\|([^|]*)\|\s*\**\s*([\d.]+)\s*\**\s*\|([^|]*)\|"
)
# The 4th cell renders as "**27× above**" or "0.26× (below threshold)".
FACTOR = re.compile(r"([\d.]+)\s*×")
# A cell that quotes a scalar with a unit, e.g. "5.43 cm²/g".
SCALAR = re.compile(r"(\d+(?:\.\d+)?)\s*cm")

CONTEXT_RADIUS = 4000  # characters after the header, enough to cover the body


def _decimals(text: str) -> int:
    """Number of decimal places in a numeric string ('5.43' -> 2, '166.0' -> 1)."""
    return len(text.split(".")[1]) if "." in text else 0


def _canonical_module():
    """Import canonical_numbers from scripts/ (not on sys.path by default)."""
    scripts = str(REPO / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    code = str(REPO / "v0.3-prelim" / "code")
    if code not in sys.path:
        sys.path.insert(0, code)
    try:
        import canonical_numbers
    except Exception as exc:  # pragma: no cover - environment failure
        pytest.skip(f"canonical_numbers not importable here: {exc!r}")
    return canonical_numbers


def _paper_table() -> list[dict]:
    """Parse the §3 8-row table into [{v, channel, sigma_m, sm_text, factor}]."""
    assert PAPER.exists(), f"missing paper: {PAPER}"
    text = PAPER.read_text(encoding="utf-8")
    idx = text.find(HEADER_MARKER)
    assert idx != -1, (
        "could not find the §3 table header "
        f"({HEADER_MARKER!r}) — was the table renamed or removed?"
    )
    window = text[idx : idx + CONTEXT_RADIUS].split("\n")
    rows = []
    for line in window[1:]:  # skip the header line itself
        if not line.startswith("|"):
            # a blank line ends the table only if we already have rows
            if rows:
                break
            continue
        if set(line.strip()) <= set("|-: "):
            continue
        m = ROW.match(line)
        if not m:
            continue
        v_text, channel, sm_text, factor_cell = m.groups()
        mf = FACTOR.search(factor_cell)
        rows.append(
            dict(
                v=float(v_text),
                channel=channel.strip(),
                sigma_m=float(sm_text),
                sm_text=sm_text,
                factor=float(mf.group(1)) if mf else None,
                factor_text=mf.group(1) if mf else None,
            )
        )
    return rows


def test_table_has_eight_rows_and_the_expected_velocities():
    """A dropped or renamed row must be loud, not silent."""
    rows = _paper_table()
    assert len(rows) == 8, (
        f"§3 σ/m table has {len(rows)} data rows, expected 8. "
        f"Rows found: {[(r['v'], r['channel']) for r in rows]}"
    )
    got = sorted(r["v"] for r in rows)
    expected = [9.0, 10.0, 15.0, 18.0, 28.0, 29.4, 40.0, 100.0]
    assert got == expected, (
        f"§3 σ/m table velocities changed.\n  paper: {got}\n  expected: {expected}"
    )


def test_sigma_m_cells_match_canonical():
    """Each σ/m cell must equal the canonical form at its own displayed precision."""
    cn = _canonical_module()
    mismatches = []
    for r in _paper_table():
        want = float(cn.sigma_m_canonical_gaussian(r["v"]))
        tol = 0.5 * 10 ** (-_decimals(r["sm_text"]))  # half a unit in the last place
        if abs(r["sigma_m"] - want) > tol:
            mismatches.append(
                f"v={r['v']:g} ({r['channel']}): paper {r['sm_text']} "
                f"vs canonical {want:.4f} (tol {tol:g})"
            )
    assert not mismatches, (
        "the §3 σ/m table disagrees with canonical_numbers."
        "sigma_m_canonical_gaussian (which reads constants.py). Either the "
        "table was not regenerated after an anchor change, or the canonical "
        "form changed — establish which side moved before editing:\n  "
        + "\n  ".join(mismatches)
    )


def test_threshold_factors_match():
    """Each '× above' factor must equal σ/m / 0.2 at its displayed precision."""
    cn = _canonical_module()
    mismatches = []
    for r in _paper_table():
        if r["factor"] is None:
            continue
        sigma_m = float(cn.sigma_m_canonical_gaussian(r["v"]))
        want = sigma_m / 0.2  # the threshold named in the table header
        tol = 0.5 * 10 ** (-_decimals(r["factor_text"]))
        if abs(r["factor"] - want) > tol:
            mismatches.append(
                f"v={r['v']:g}: paper {r['factor_text']}× vs "
                f"canonical {want:.3f}× (tol {tol:g})"
            )
    assert not mismatches, (
        "the §3 table's factor column disagrees with σ/m / 0.2 cm²/g:\n  "
        + "\n  ".join(mismatches)
    )


def test_no_retired_anchor_values_in_the_table():
    """Guard the specific superseded σ/m(28) anchors so a re-introduction is loud.

    100 cm²/g was the Elbert+ 2015 working anchor and 150.0 cm²/g was the
    legacy a_slope = 1.0 value; the canonical row quotes 166 (a_slope = 1.93).
    """
    retired = {"100", "150", "150.0"}
    bad = [
        f"v={r['v']:g}: {r['sm_text']}"
        for r in _paper_table()
        if abs(r["v"] - 28.0) < 1e-9 and r["sm_text"] in retired
    ]
    assert not bad, (
        f"a retired σ/m(28) anchor is back in the §3 table: {bad}. "
        "The canonical value is 166.0 cm²/g at a_slope = 1.93."
    )
