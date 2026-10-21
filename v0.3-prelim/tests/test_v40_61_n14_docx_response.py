"""Regression tests for v40.61: n14.docx review response.

Per n14.docx (2026-10-21, 9th human review of the v40.59/v40.60 report), the
following issues were raised. Each test below locks the v40.61 fix.

N14.DOCX FINDINGS ADDRESSED:
1. [MED-HIGH] Sameie+ audit conclusion vs marginalization framing in section 1.
2. [MED]      Version-count rule: 21 sequential + 1 lettered sub-version.
3. [MED-HIGH] Section 8.3 '121 passed' contradicted the header's '1816 passed'.
4. [MED]      Section 5.3 JSON had a non-standard '//' inline comment.
5. [MED-LOW]  Ohana+ 2026 citation not independently verifiable -> PDF saved.
6. [MED]      Sameie+ extrapolation uncertainty not in marginalization weights.
7. [LOW]      Section 8.4 missing a PowerShell variant.
8. [MED-LOW]  Defect E fix: full fixed test code not shown in the report.

SELF-FOUND (not in n14's list, same family of count-drift errors):
9.  Section 6 review count was wrong on all three terms ('all 13: 7x120B +
    5x550B + 1x human'); actual is 28 rounds with DEFERRED counted separately.
10. Section 1 called Ohana+ 2026 an 'upper limit'; it is a posterior inference
    of the concentration deviation.
11. The v40.57/v40.58 tests hard-coded version literals, which broke on every
    version bump (root cause of the recurring count-inconsistency pattern).
    Those tests were made version-agnostic in v40.61; this file locks the
    version-agnostic behaviour so it cannot regress to literal matching.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
REPORT = REPO / "docs" / "SIDM_V40_51_FULL_REVIEW_REPORT_2026_10_19.md"
OHANA_MD = REPO / "docs" / "papers" / "verified" / "2608.04362_ohana_2026_cloud9_cdm_sidm.md"
OHANA_PDF = REPO / "docs" / "papers" / "verified" / "2608.04362_ohana_2026_cloud9_cdm_sidm.pdf"
REGISTRY = REPO / "docs" / "V19_2_F_REFERENCE_DATA_REGISTRY.md"
V58_CODE = REPO / "v0.3-prelim" / "code" / "t90_v58_ablation.py"
V58_TEST = REPO / "v0.3-prelim" / "tests" / "test_t90_v58_ablation.py"


def _report() -> str:
    return REPORT.read_text(encoding="utf-8")


def _section(text: str, start: str, end: str) -> str:
    i = text.find(start)
    assert i != -1, f"Section start marker not found: {start!r}"
    j = text.find(end, i)
    assert j != -1, f"Section end marker not found: {end!r}"
    return text[i:j]


# --------------------------------------------------------------------------
# Item 1 (MED-HIGH): Sameie+ branch labelled as a qualitative test only
# --------------------------------------------------------------------------

def test_sameie_branch_labelled_qualitative_only_in_exec_summary():
    """n14 Item 1: the Sameie+ branch must not read as a calibrated prediction."""
    text = _report()
    sec1 = _section(text, "## 1. Executive Summary", "## 2. The")

    # The Sameie+ bullet in caveat 1 must carry the qualitative-only label.
    sameie_lines = [ln for ln in sec1.splitlines() if "Sameie+ 2020" in ln and "c-M" in ln]
    assert sameie_lines, "n14 Item 1: caveat 1 must list the Sameie+ 2020 branch."
    labelled = [ln for ln in sameie_lines if "QUALITATIVE SIGN-FLIP TEST ONLY" in ln]
    assert labelled, (
        "n14 Item 1 fix: the Sameie+ 2020 branch in the Executive Summary must "
        "be labelled 'QUALITATIVE SIGN-FLIP TEST ONLY, NOT QUANTITATIVELY "
        "VALIDATED'. The v40.59 audit established its -1.31 sigma has no "
        f"empirical anchor in the paper. Found lines: {sameie_lines}"
    )

    # And there must be an explicit no-anchor statement.
    assert "no empirical anchor" in sec1.lower(), (
        "n14 Item 1 fix: the Executive Summary must state that the Sameie+ "
        "value carries no empirical anchor in the cited paper."
    )


def test_sameie_branch_carries_quantitative_status_in_json():
    """n14 Item 1: the qualification must travel with the number in the JSON."""
    text = _report()
    sec54 = _section(text, "### 5.4", "## 6. Reviews")
    assert "quantitative_status" in sec54, (
        "n14 Item 1 fix: section 5.4 must carry a per-branch "
        "'quantitative_status' field."
    )
    # Every prescription branch must have one.
    json_block = re.search(r"```json\n(.*?)\n```", sec54, re.DOTALL)
    assert json_block, "n14 Item 1 fix: section 5.4 must contain a JSON block."
    data = json.loads(json_block.group(1))  # must be strict JSON
    for name, branch in data["prescriptions"].items():
        assert "quantitative_status" in branch, (
            f"n14 Item 1 fix: prescription branch {name!r} must carry a "
            f"'quantitative_status' field."
        )
    sameie = data["prescriptions"]["Sameie+ 2020"]
    assert "QUALITATIVE SIGN-FLIP TEST ONLY" in sameie["quantitative_status"], (
        f"n14 Item 1 fix: the Sameie+ branch status must say it is a "
        f"qualitative sign-flip test only. Got: {sameie['quantitative_status']!r}"
    )


# --------------------------------------------------------------------------
# Item 2 (MED): version-counting rule explicit + version-agnostic assertions
# --------------------------------------------------------------------------

def test_version_counting_rule_stated_explicitly():
    """n14 Item 2: the 22-vs-23 (sequential-vs-rows) rule must be stated."""
    text = _report()
    sec2 = _section(text, "## 2. The", "## 3. Framework Status")
    assert "Version-counting rule" in sec2, (
        "n14 Item 2 fix: section 2 must state the version-counting rule "
        "explicitly (sequential numbers vs lettered sub-versions)."
    )
    assert "sub-version" in sec2, (
        "n14 Item 2 fix: the counting rule must name the lettered "
        "sub-version (v40.43a) explicitly."
    )
    # The stated sequential count must equal the declared range length.
    arc = re.search(r"v40\.(\d+)\s*(?:→|->)\s*v40\.(\d+)", sec2)
    assert arc, "n14 Item 2 fix: section 2 header must declare a version range."
    lo, hi = int(arc.group(1)), int(arc.group(2))
    n_seq = hi - lo + 1
    count = re.search(r"The (\d+)-Version Arc", sec2)
    assert count, "n14 Item 2 fix: section 2 header must state the version count."
    assert int(count.group(1)) == n_seq, (
        f"n14 Item 2 fix: header says '{count.group(1)}-Version Arc' but range "
        f"v40.{lo}..v40.{hi} spans {n_seq} sequential versions."
    )


def test_arc_table_has_a_row_for_every_version_in_range():
    """n14 Item 2: no version in the declared range may be missing from the table."""
    text = _report()
    sec2 = _section(text, "## 2. The", "## 3. Framework Status")
    arc = re.search(r"v40\.(\d+)\s*(?:→|->)\s*v40\.(\d+)", sec2)
    assert arc, "n14 Item 2 fix: section 2 header must declare a version range."
    lo, hi = int(arc.group(1)), int(arc.group(2))
    for n in range(lo, hi + 1):
        assert f"v40.{n}" in sec2, (
            f"n14 Item 2 fix: version arc table must include a row for v40.{n}."
        )


def test_stale_version_strings_annotated_as_historical():
    """n14 Item 2: old counts left in the historical section must be annotated."""
    text = _report()
    sec171 = _section(text, "### 17.1", "### 17.2")
    # The historical quotes are allowed to exist, but must be marked historical.
    assert "superseded in v40.59" in sec171, (
        "n14 Item 2 fix: the stale '19-Version Arc' / '18-version' strings in "
        "section 17.1 must be annotated as historical (superseded), otherwise "
        "they read as live contradictions."
    )


def test_version_agnostic_tests_do_not_use_literal_version_matching():
    """v40.61 self-check: the v40.57/v40.58 tests must not freeze version literals.

    This is the mechanical root cause of the recurring count-inconsistency
    pattern flagged in n6..n14. The tests must assert INTERNAL CONSISTENCY
    (range-vs-range, count-vs-count) rather than a hard-coded string.
    """
    for path, forbidden in (
        (REPO / "v0.3-prelim" / "tests" / "test_v40_57_n12_docx_response.py",
         "v40.39 → v40.57"),
        (REPO / "v0.3-prelim" / "tests" / "test_v40_58_n13_docx_response.py",
         "The 19-Version Arc (v40.39 → v40.57)"),
    ):
        src = path.read_text(encoding="utf-8")
        # The literal may appear inside a COMMENT (historical note) but must
        # not appear inside an assert() expression.
        for m in re.finditer(r"assert[^\n]*" + re.escape(forbidden), src):
            raise AssertionError(
                f"v40.61 fix: {path.name} still asserts the literal {forbidden!r}. "
                f"Version-locked assertions break on every version bump and are "
                f"the root cause of the recurring count-inconsistency pattern. "
                f"Found at offset {m.start()}."
            )
        # And the version-agnostic mechanism must be present.
        assert "re.search" in src, (
            f"v40.61 fix: {path.name} must use a regex range extraction so the "
            f"assertion is version-agnostic."
        )


# --------------------------------------------------------------------------
# Item 3 (MED-HIGH): section 8.3 test count agrees with the header
# --------------------------------------------------------------------------

def test_section_8_3_shows_full_suite_count_matching_header():
    """n14 Item 3: '121 passed' contradicted the header's '1816 passed'."""
    text = _report()
    header = re.search(r"\*\*Test count:\*\* (\d+) passed", text)
    assert header, "n14 Item 3 fix: the header must declare a passed count."
    n = int(header.group(1))

    sec83 = _section(text, "### 8.3", "### 8.4")
    # A fenced pytest summary line, not a prose mention.
    assert re.search(rf"^{n} passed, \d+ skipped, \d+ deselected", sec83, re.MULTILINE), (
        f"n14 Item 3 fix: section 8.3 must contain a fenced pytest summary line "
        f"starting '{n} passed, <N> skipped, <N> deselected'."
    )
    # The old subset figure must be explicitly qualified, not left bare.
    assert "121 passed" in sec83, (
        "n14 Item 3 fix: the historical '121 passed' figure should still be "
        "present but QUALIFIED as the v40-era subset only, so the reader knows "
        "what it referred to."
    )
    assert "subset" in sec83.lower(), (
        "n14 Item 3 fix: the '121 passed' figure must be explicitly labelled as "
        "a subset count."
    )


def test_section_8_2_count_matches_header():
    """n14 Item 3: header and §8.2 must agree on the count."""
    text = _report()
    header = re.search(r"\*\*Test count:\*\* (\d+) passed", text)
    assert header, "n14 Item 3 fix: the header must declare a passed count."
    n = int(header.group(1))
    sec82 = _section(text, "### 8.2", "### 8.3")
    m = re.search(r"(\d+) passed", sec82)
    assert m, "n14 Item 3 fix: section 8.2 must state a passed count."
    assert int(m.group(1)) == n, (
        f"n14 Item 3 fix: header says {n} passed but section 8.2 says "
        f"{m.group(1)}."
    )


# --------------------------------------------------------------------------
# Item 4 (MED): section 5.3 JSON must be strict JSON
# --------------------------------------------------------------------------

def test_all_json_blocks_in_report_are_strict_json():
    """n14 Item 4: the '//' inline comment broke strict JSON parsing.

    Every ```json fenced block in the report must parse with json.loads().
    """
    text = _report()
    blocks = re.findall(r"```json\n(.*?)\n```", text, re.DOTALL)
    assert blocks, "n14 Item 4 fix: the report must contain at least one JSON block."
    for i, block in enumerate(blocks):
        try:
            json.loads(block)
        except json.JSONDecodeError as e:
            snippet = block.splitlines()[0][:80] if block.splitlines() else ""
            raise AssertionError(
                f"n14 Item 4 fix: JSON block #{i} is not strict JSON: {e}. "
                f"First line: {snippet!r}. Per n14.docx, inline '//' comments "
                f"are not valid JSON and fail a strict parser."
            )


def test_section_5_3_has_no_inline_comment():
    """n14 Item 4: the specific line the reviewer quoted must be clean."""
    text = _report()
    sec53 = _section(text, "### 5.3", "### 5.4")
    block = re.search(r"```json\n(.*?)\n```", sec53, re.DOTALL)
    assert block, "n14 Item 4 fix: section 5.3 must contain a JSON block."
    body = block.group(1)
    assert "//" not in body, (
        f"n14 Item 4 fix: section 5.3 JSON must not contain '//' comments. "
        f"Found: {body}"
    )
    # The 273x reduction information must still be present (as prose).
    assert "273" in _section(text, "### 5.3", "### 5.4"), (
        "n14 Item 4 fix: the 273x reduction note must be preserved as prose "
        "even though the inline comment was removed."
    )


# --------------------------------------------------------------------------
# Item 5 (MED-LOW): Ohana+ 2026 independently verifiable
# --------------------------------------------------------------------------

def test_ohana_paper_saved_locally():
    """n14 Item 5: the citation must have a checkable local source."""
    assert OHANA_PDF.exists(), (
        f"n14 Item 5 fix: the Ohana+ 2026 PDF must be saved locally: {OHANA_PDF}"
    )
    size = OHANA_PDF.stat().st_size
    assert size > 100_000, (
        f"n14 Item 5 fix: the Ohana+ PDF looks truncated ({size} bytes)."
    )
    assert OHANA_MD.exists(), (
        f"n14 Item 5 fix: an .md summary of the Ohana+ paper must exist: {OHANA_MD}"
    )
    md = OHANA_MD.read_text(encoding="utf-8")
    assert "2608.04362" in md, "n14 Item 5 fix: the .md must record the arXiv ID."
    assert "3.2" in md, (
        "n14 Item 5 fix: the .md must record the provenance of the 3.2 sigma figure."
    )


def test_ohana_registry_entry_verified():
    """n14 Item 5: the registry must carry a VERIFIED entry."""
    reg = REGISTRY.read_text(encoding="utf-8")
    assert "2608.04362" in reg, (
        "n14 Item 5 fix: the reference registry must contain an Ohana+ 2026 entry."
    )
    idx = reg.find("2608.04362")
    entry = reg[max(0, idx - 400):idx + 1200]
    assert "VERIFIED (v40.61)" in entry, (
        "n14 Item 5 fix: the Ohana+ 2026 registry entry must be marked "
        "'VERIFIED (v40.61)'."
    )


def test_ohana_not_called_an_upper_limit():
    """v40.61 self-check: Ohana+ is a posterior inference, not an upper limit."""
    text = _report()
    sec1 = _section(text, "## 1. Executive Summary", "## 2. The")
    assert "upper limit" not in sec1.lower(), (
        "v40.61 fix: the Executive Summary must not describe Ohana+ 2026 as an "
        "'upper limit'. It is a posterior inference of the concentration "
        "deviation below the cosmological c-M relation."
    )
    assert "posterior inference" in sec1.lower(), (
        "v40.61 fix: the Executive Summary must describe Ohana+ 2026 as a "
        "'posterior inference of the concentration deviation'."
    )


def test_ohana_3p2_sigma_provenance_recorded():
    """n14 Item 5: the 3.2 sigma must be traceable to a specific paper statement."""
    text = _report()
    sec165 = _section(text, "### 16.5", "### 16.6")
    for token in ("2608.04362", "3.2", "483", "0.18"):
        assert token in sec165, (
            f"n14 Item 5 fix: section 16.5 must record {token!r} so a reviewer "
            f"can trace the 3.2 sigma figure to the paper."
        )


# --------------------------------------------------------------------------
# Item 6 (MED): extrapolation uncertainty in the weighting discussion
# --------------------------------------------------------------------------

def test_extrapolation_uncertainty_discussed():
    """n14 Item 6: Cloud-9 c=12 vs the paper's c_200=22-29 must be in section 1."""
    text = _report()
    sec1 = _section(text, "## 1. Executive Summary", "## 2. The")
    assert "extrapolation" in sec1.lower(), (
        "n14 Item 6 fix: the Executive Summary must discuss the Sameie+ "
        "extrapolation uncertainty."
    )
    assert "22" in sec1 and "29" in sec1, (
        "n14 Item 6 fix: the Executive Summary must state the paper's "
        "calibration range (c_200 = 22-29) so the mismatch with Cloud-9's "
        "c = 12 is explicit."
    )
    assert "12" in sec1, (
        "n14 Item 6 fix: the Executive Summary must state Cloud-9's c = 12."
    )
    # And the consequence for the headline numbers must be stated.
    assert "conditional" in sec1.lower(), (
        "n14 Item 6 fix: the Executive Summary must state that the headline "
        "marginalization numbers are conditional on the weighting scheme."
    )


# --------------------------------------------------------------------------
# Item 7 (LOW): section 8.4 PowerShell parity
# --------------------------------------------------------------------------

def test_section_8_4_has_powershell_variant():
    """n14 Item 7: section 8.4 offered only the POSIX form."""
    text = _report()
    sec84 = _section(text, "### 8.4", "---\n\n## 9.")
    assert "& .venv-sidm-bench" in sec84, (
        "n14 Item 7 fix: section 8.4 must include a PowerShell variant with "
        "the '&' call operator, matching section 8.3."
    )
    assert "v19_2_f_paper_section_2_1_update.py" in sec84, (
        "n14 Item 7 fix: section 8.4 must still show the POSIX invocation."
    )


# --------------------------------------------------------------------------
# Item 8 (MED-LOW): full fixed Defect E test code shown
# --------------------------------------------------------------------------

def test_full_fixed_v58_test_code_shown_in_report():
    """n14 Item 8: the complete fixed test function must be in the report."""
    text = _report()
    sec411 = _section(text, "### 4.11", "---\n\n## 5.")
    assert "def test_smoke_ablation_writes_jsons(tmp_path):" in sec411, (
        "n14 Item 8 fix: section 4.11 must show the complete fixed test "
        "function signature including the tmp_path fixture."
    )
    assert "--out-dir" in sec411, (
        "n14 Item 8 fix: section 4.11 must show the --out-dir argument."
    )
    # The tmp_path lifetime concern must be answered.
    assert "tmp_path" in sec411 and ("lifetime" in sec411.lower() or
                                      "cleanup" in sec411.lower() or
                                      "removed" in sec411.lower()), (
        "n14 Item 8 fix: section 4.11 must address the reviewer's concern "
        "about pytest's tmp_path lifetime."
    )


def test_v58_source_actually_has_out_dir_flag():
    """n14 Item 8: the report's code listing must match the real source."""
    src = V58_CODE.read_text(encoding="utf-8")
    assert '"--out-dir"' in src, (
        "n14 Item 8 fix: t90_v58_ablation.py must accept --out-dir."
    )
    test_src = V58_TEST.read_text(encoding="utf-8")
    assert "tmp_path" in test_src, (
        "n14 Item 8 fix: the v58 test must use the tmp_path fixture."
    )
    assert "results_dir.glob" not in test_src or "unlink" not in test_src, (
        "n14 Item 8 fix: the v58 test must NOT delete production result files "
        "(the v40.59 defect-E root cause)."
    )


# --------------------------------------------------------------------------
# Self-found item 9: section 6 review count
# --------------------------------------------------------------------------

def test_section_6_review_count_correct():
    """v40.61 self-check: section 6's review count must match the evidence."""
    text = _report()
    sec6 = _section(text, "## 6. Reviews", "## 7.")
    assert "28 rounds" in sec6, (
        "v40.61 fix: section 6 must state the correct total (28 review rounds: "
        "9x120B + 6x550B COMPLETE + 5x550B DEFERRED + 8x human). The v40.59 "
        "header said 'all 13: 7x120B + 5x550B + 1x human', wrong on all three "
        "terms."
    )
    assert "DEFERRED" in sec6, (
        "v40.61 fix: section 6 must separate DEFERRED 550B rounds (which "
        "produced no verdict) from COMPLETE ones."
    )
    # The on-disk evidence must agree with the stated 120B count.
    n_120b = len(list((REPO / "docs").glob("NEMOTRON_120B_REVIEW_*.md")))
    assert f"| {n_120b} |" in sec6, (
        f"v40.61 fix: section 6 must state {n_120b} 120B rounds to match the "
        f"{n_120b} review documents on disk."
    )


# --------------------------------------------------------------------------
# Cross-cutting: the report must not claim the old v40.59 framing anywhere
# --------------------------------------------------------------------------

def test_no_stale_121_count_outside_qualified_context():
    """The '121/121' figure must not appear as a live test count."""
    text = _report()
    # Live claims (header, 8.2) must not use it.
    header_block = text[:text.find("## 1.")]
    assert "121/121" not in header_block, (
        "v40.61 fix: the report header must not state the stale '121/121' "
        "test count."
    )
    sec82 = _section(text, "### 8.2", "### 8.3")
    assert "121/121" not in sec82, (
        "v40.61 fix: section 8.2 must not state the stale '121/121' count."
    )


if __name__ == "__main__":
    failures = 0
    for name in sorted(dir()):
        if name.startswith("test_"):
            try:
                globals()[name]()
                print(f"  PASS  {name}")
            except AssertionError as e:
                print(f"  FAIL  {name}: {e}")
                failures += 1
    if failures:
        print(f"\n{failures} test(s) FAILED")
        sys.exit(1)
    print("\nAll v40.61 n14.docx review response regression tests pass.")
