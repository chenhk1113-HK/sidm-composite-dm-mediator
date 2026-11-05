"""Guard: finding IDs in docs/INTEGRITY_FINDINGS_2026-11-04.md must be unique and resolvable.

Why this exists (2026-11-05): the same file carried TWO findings numbered `F17` — the BM2
collapse-time finding and the gate-ignore-list finding — so a reader following a reference to
"F17 / decision D9" landed on the wrong finding. Renumbered to `F18`; this test keeps the
collision from coming back.

Scope note: `docs/dual_review_5loop/**` carries its own independent reviewer numbering, and the
older fix-log IDs (for example the `F23` hierarchy-chain fix referenced by
`scripts/audit_hierarchy_chain.py`) belong to a different report. Reference resolution therefore
matches two explicit forms only — the phrase `finding Fxx` and the citation form
`` `docs/INTEGRITY_FINDINGS_2026-11-04.md` Fxx`` — never a bare `F<digits>` token anywhere.
A heading like `## F1-follow-up` is a sub-entry of `F1`, not a second `F1`, and is counted only
when the ID is followed by whitespace.
"""
from __future__ import annotations

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INTEGRITY_DOC = PROJECT_ROOT / "docs" / "INTEGRITY_FINDINGS_2026-11-04.md"

# Files allowed to reference integrity findings by ID.
REFERENCE_GLOBS = [
    "CURRENT.md",
    "CHANGELOG.md",
    "docs/*.md",
    "v0.3-prelim/docs/*.md",
    "v0.3-prelim/tests/*.py",
    "v0.3-prelim/code/*.py",
    "scripts/*.py",
]

EXCLUDED_PARTS = ("dual_review_5loop",)

HEADING_RE = re.compile(r"^## (F\d+)(?=\s)", re.MULTILINE)
# `## F1-follow-up (...)` is a sub-entry of F1, not a duplicate heading for F1.
SUBENTRY_RE = re.compile(r"^## (F\d+)(?=[-\w])", re.MULTILINE)
REFERENCE_RE = re.compile(r"findings? (F\d+)\b")
CITATION_RE = re.compile(r"INTEGRITY_FINDINGS_2026-11-04\.md` (F\d+)\b")


def _heading_ids(text: str) -> list[str]:
    return HEADING_RE.findall(text)


def test_integrity_report_has_no_duplicate_finding_ids() -> None:
    ids = _heading_ids(INTEGRITY_DOC.read_text(encoding="utf-8"))
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    assert not dupes, (
        f"duplicate finding headings in {INTEGRITY_DOC.name}: {dupes}. "
        "Each finding needs its own ID or an explicit sub-entry form (e.g. 'F1-follow-up')."
    )


def test_subentry_headings_are_not_counted_as_duplicates() -> None:
    text = INTEGRITY_DOC.read_text(encoding="utf-8")
    headings = _heading_ids(text)
    subentries = SUBENTRY_RE.findall(text)
    # A sub-entry shares its parent's ID by design; it must never be a plain heading.
    assert subentries, "expected at least one 'F<n>-follow-up' sub-entry to keep this test honest"
    for parent in set(subentries):
        assert parent in headings, f"sub-entry {parent}-follow-up has no parent heading {parent}"


def test_the_two_2026_11_05_findings_have_distinct_ids() -> None:
    text = INTEGRITY_DOC.read_text(encoding="utf-8")
    bm2 = re.search(r"^## (F\d+) — the BM2 \"2\.6% deviation\"", text, re.MULTILINE)
    gate = re.search(
        r"^## (F\d+) — the release gate's ignore list hides", text, re.MULTILINE
    )
    assert bm2 and gate, "both the BM2 finding and the gate-ignore finding must exist"
    assert bm2.group(1) != gate.group(1), (
        f"the BM2 finding and the gate-ignore finding share ID {bm2.group(1)}"
    )


def test_every_finding_reference_resolves_to_a_real_heading() -> None:
    ids = set(_heading_ids(INTEGRITY_DOC.read_text(encoding="utf-8")))
    unresolved: list[str] = []
    checked = 0
    for pattern in REFERENCE_GLOBS:
        for path in sorted(PROJECT_ROOT.glob(pattern)):
            if path.is_dir() or any(part in EXCLUDED_PARTS for part in path.parts):
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            for ref in REFERENCE_RE.findall(text) + CITATION_RE.findall(text):
                checked += 1
                if ref not in ids:
                    unresolved.append(f"{path.relative_to(PROJECT_ROOT)}: finding {ref}")
    assert checked > 0, "no finding references found - this test has gone vacuous"
    assert not unresolved, f"references to findings with no heading: {unresolved}"
