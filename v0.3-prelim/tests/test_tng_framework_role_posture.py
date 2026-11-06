"""Guard: the IllustrisTNG posture decided on 2026-11-06 must stay written down.

Why this exists (decision D8, owner decision 2026-11-06): the Stage-3 sample measured that TNG50-1
holds halos of Cloud-9's mass but none that combine Cloud-9's speed with a quiet merger history
(`docs/STAGE3_TNG_MEASURED_2026-11-06.md` sections 4-5, artifacts
`v0.3-prelim/data/external/tng/stage3_anchor/candidates.csv` and
`v0.3-prelim/data/results/tng_stage3_growth_summary.json`). The owner closed D8 by reclassifying the
simulation as a framework check rather than a Cloud-9 twin test, and closed the two hunt options.
This test keeps the posture, its closure markers, and the ban on an affirmative "the simulation
contains a Cloud-9 analogue" claim.

Limitation stated honestly: the affirmative-claim scan is a phrase scan over live documents. A claim
phrased in new wording can slip past it. What the test guarantees is that the decision text exists in
the three places a reader would look, and that the specific existence claims already tried are absent.
"""
from __future__ import annotations

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

FINDINGS = PROJECT_ROOT / "docs" / "FINDINGS_FOR_FUTURE_DELIBERATION.md"
STAGE3_DOC = PROJECT_ROOT / "docs" / "STAGE3_TNG_MEASURED_2026-11-06.md"
CURRENT = PROJECT_ROOT / "CURRENT.md"
CHANGELOG = PROJECT_ROOT / "CHANGELOG.md"

LIVE_DOC_GLOBS = ["CURRENT.md", "docs/*.md", "v0.3-prelim/docs/PAPER_V1_DRAFT.md"]
EXCLUDED_PARTS = ("dual_review_5loop", "superseded")

SECTION_27_8 = "### 27.8 Decision D8 closed (2026-11-06)"
POSTURE_PHRASE = "framework check, not a Cloud-9 twin test"
ROLE_HEADING = "### 8. Role of this sample (decided 2026-11-06)"
CHANGELOG_SECTION = "## [TNG-Framework-Role-D8-2026-11-06]"

# Affirmative forms of the claim the decision retires.
AFFIRMATIVE_RE = re.compile(
    r"(TNG50-1|TNG100-1|IllustrisTNG|the sample)[^.]{0,80}?"
    r"(contains|contain|realizes|realize|provides|provides?|yields|has found|found)\s+"
    r"(a\s+)?(Cloud-9|cloud9)[^.]{0,40}?(twin|analogue|analog|look-alike|look alike)",
    re.IGNORECASE,
)
NEGATION_TOKENS = ("not", "no ", "never", "without", "instead", "rather")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _live_docs() -> list[Path]:
    found: list[Path] = []
    for glob in LIVE_DOC_GLOBS:
        found.extend(sorted(PROJECT_ROOT.glob(glob)))
    return [p for p in found if not any(part in EXCLUDED_PARTS for part in p.parts)]


def test_d8_closure_is_written_in_the_findings_doc():
    text = _read(FINDINGS)
    assert SECTION_27_8 in text, "section 27.8 (the D8 closure) is missing from the findings doc"
    tail = text.split(SECTION_27_8, 1)[1]
    assert POSTURE_PHRASE in tail, "the framework-check posture is not stated in section 27.8"
    assert "No further anchor search is authorised" in tail, (
        "section 27.8 must keep the two hunt options closed"
    )


def test_d8_options_block_is_marked_closed():
    text = _read(FINDINGS)
    hits = [l for l in text.splitlines() if l.startswith("**Open decision D8")]
    assert len(hits) == 1, f"expected exactly one D8 options header, found {len(hits)}"
    assert "CLOSED by section 27.8" in hits[0], (
        "the D8 options block still reads as open: " + hits[0]
    )


def test_current_md_records_the_closure_and_no_longer_calls_d8_open():
    text = _read(CURRENT)
    assert "decision D8, CLOSED 2026-11-06" in text, "CURRENT.md does not record the D8 closure"
    assert "(open decision D8" not in text, "CURRENT.md still labels D8 an open decision"


def test_stage3_doc_declares_its_role():
    text = _read(STAGE3_DOC)
    assert ROLE_HEADING in text, "the Stage-3 measured doc is missing its role declaration"
    tail = text.split(ROLE_HEADING, 1)[1]
    assert "framework check" in tail, "the Stage-3 role declaration does not name the posture"


def test_changelog_carries_the_decision():
    assert CHANGELOG_SECTION in _read(CHANGELOG), "CHANGELOG is missing the D8 decision section"


def test_no_live_doc_claims_the_simulation_contains_a_cloud9_twin():
    offenders: list[str] = []
    for path in _live_docs():
        for line in _read(path).splitlines():
            if not AFFIRMATIVE_RE.search(line):
                continue
            low = line.lower()
            if any(tok in low for tok in NEGATION_TOKENS):
                continue  # an explicit denial of the claim, which is allowed
            offenders.append(f"{path.relative_to(PROJECT_ROOT)}: {line.strip()[:140]}")
    assert not offenders, (
        "a live document asserts a Cloud-9 analogue inside the simulation, which decision D8 "
        "retires:\n" + "\n".join(offenders)
    )


if __name__ == "__main__":
    for fn in [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]:
        fn()
    print("posture guards passed")
