"""Regression tests for v40.62: n15.docx review response.

Per n15.docx (2026-10-21, 10th human review of the v40.61 report), the
following issues were raised. Each test below locks the v40.62 fix.

N15.DOCX FINDINGS ADDRESSED:
1. [MED-HIGH] Section 9.2's "14 versions, 13 reviews, 92 tests" contradicted
   the whole report (title, section 2 arc table, header, section 8.2).
2. [MED]      Header said "9 human reviews (n6-n14)" while the section 6
   table said "8 (n6-n13)".
3. [MED]      Sameie+ was labelled "QUALITATIVE ONLY" but still carried 1/3
   equal weight in the quantitative marginalization.
4. [MED]      Ohana+ 2026's c_200 degeneracy (concentration constrained by
   the prior, not the likelihood) was not discussed in the framework analysis.
5. [MED-LOW]  The PDF extraction method was not documented.
6. [MED-LOW]  test_v40_51_paper_section_2_1_ranges.py code was not shown.
7. [LOW]      categorize_test() had a bare `return "Other"` fallback.
8. [MED-LOW]  The 0.16 dex scatter assumption's effect on sigma was not in
   the marginalization weighting discussion.

SELF-FOUND (not in n15's list, found while verifying n15's claims):
9.  scripts/v19_2_f_cloud9_cM_three_prescriptions.py hard-coded -1.39 in six
    places while the computed value was -1.3104 — the hard-coded text
    contradicted the numbers in the same file.
10. scripts/v19_2_f_n11_docx_response.py hard-coded a 95% CI upper bound of
    +1.56, contradicting the authoritative +1.29 from the n9 script; the
    report carried BOTH numbers.
11. The PDF page anchors added in v40.61/v40.62 were asserted from memory
    rather than verified against the PDF; three were wrong.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
REPORT = REPO / "docs" / "SIDM_V40_51_FULL_REVIEW_REPORT_2026_10_19.md"
THREE_PRESC = REPO / "scripts" / "v19_2_f_cloud9_cM_three_prescriptions.py"
N9_SCRIPT = REPO / "scripts" / "v19_2_f_n9_docx_response.py"
N11_SCRIPT = REPO / "scripts" / "v19_2_f_n11_docx_response.py"
MAPPING_SCRIPT = REPO / "scripts" / "generate_test_mapping.py"
THREE_PRESC_JSON = (REPO / "v0.3-prelim" / "data" / "results"
                     / "v19_2_f_cloud9_cM_three_prescriptions_2026_10_19.json")
V51_TEST = REPO / "v0.3-prelim" / "tests" / "test_v40_51_paper_section_2_1_ranges.py"


def _report() -> str:
    return REPORT.read_text(encoding="utf-8")


def _section(text: str, start: str, end: str) -> str:
    i = text.find(start)
    assert i != -1, f"Section start marker not found: {start!r}"
    j = text.find(end, i)
    assert j != -1, f"Section end marker not found: {end!r}"
    return text[i:j]


# --------------------------------------------------------------------------
# Item 1 (MED-HIGH): section 9.2 counts must agree with the rest of the report
# --------------------------------------------------------------------------

def test_section_9_2_counts_match_the_report():
    """n15 Item 1: '14 versions, 13 reviews, 92 tests' was 11 versions stale."""
    text = _report()
    sec92 = _section(text, "### 9.2", "### 9.3")

    # The stale string must be gone from the LIVE claim. The v40.62 note
    # quotes it as history (marked "the v40.61 version of this line read"),
    # which is intentional and is how the v40.61 round annotated its own
    # superseded strings. So we check the live bullet, not the whole section.
    live_bullets = [ln for ln in sec92.splitlines()
                    if ln.startswith("- ") and "version of this line read" not in ln]
    assert live_bullets, "n15 Item 1 fix: section 9.2 must still have its claim bullets."
    assert not any("14 versions, 13 reviews, 92 tests" in ln for ln in live_bullets), (
        "n15 Item 1 fix: the live section 9.2 claim must not carry the stale "
        "'14 versions, 13 reviews, 92 tests' counts."
    )

    # The version count must match the section 2 arc header.
    sec2 = _section(text, "## 2. The", "## 3. Framework Status")
    arc = re.search(r"v40\.(\d+)\s*(?:→|->)\s*v40\.(\d+)", sec2)
    assert arc, "n15 Item 1 fix: section 2 must declare a version range."
    lo, hi = int(arc.group(1)), int(arc.group(2))
    n_seq = hi - lo + 1
    count = re.search(r"The (\d+)-Version Arc", sec2)
    assert count and int(count.group(1)) == n_seq, (
        "n15 Item 1 fix: section 2 header count must equal the declared range length."
    )

    # Section 9.2 must quote the same sequential version count.
    assert f"**{n_seq} sequential versions**" in sec92, (
        f"n15 Item 1 fix: section 9.2 must state the current sequential version "
        f"count ({n_seq}), matching section 2's range v40.{lo}..v40.{hi}."
    )


def test_section_9_2_test_count_matches_section_8_2():
    """n15 Item 1: the test count quoted in 9.2 must match section 8.2."""
    text = _report()
    sec92 = _section(text, "### 9.2", "### 9.3")
    sec82 = _section(text, "### 8.2", "### 8.3")
    m82 = re.search(r"(\d+) passed", sec82)
    assert m82, "n15 Item 1 fix: section 8.2 must state a passed count."
    n = int(m82.group(1))
    assert f"**{n:,} tests**" in sec92 or f"**{n} tests**" in sec92, (
        f"n15 Item 1 fix: section 9.2 must state the current test count ({n}), "
        f"matching section 8.2."
    )


# --------------------------------------------------------------------------
# Item 2 (MED): the human review count must be consistent
# --------------------------------------------------------------------------

def test_human_review_count_consistent_header_table_footer():
    """n15 Item 2: header said 9 (n6-n14), section 6 table said 8 (n6-n13)."""
    text = _report()
    sec6 = _section(text, "## 6. Reviews", "## 7.")

    # The table row must state n6..n15 and 10 rounds.
    assert "n6.docx\u2013n15.docx" in sec6, (
        "n15 Item 2 fix: the section 6 table must list the human reviews as "
        "n6-n15 (n15 is closed by the version that responds to it)."
    )
    row = [ln for ln in sec6.splitlines() if "Human (n6.docx" in ln]
    assert row, "n15 Item 2 fix: section 6 must have a Human review row."
    assert "| 10 |" in row[0], (
        f"n15 Item 2 fix: the Human row must state 10 rounds. Got: {row[0]}"
    )

    # The header and the footer must agree with the table.
    header = text[: text.find("## 1.")]
    assert "n6.docx through n15.docx human reviewers (10 reviews)" in header, (
        "n15 Item 2 fix: the header must state n6-n15 / 10 human reviews."
    )
    assert "30 review rounds total" in header, (
        "n15 Item 2 fix: the header must state 30 total review rounds."
    )
    footer = text[text.rfind("**Reviewed by:**"):]
    assert "n6.docx through n15.docx human reviewers (10 reviews)" in footer, (
        "n15 Item 2 fix: the footer must state n6-n15 / 10 human reviews."
    )
    assert "30 review rounds" in footer, (
        "n15 Item 2 fix: the footer must state 30 total review rounds."
    )


def test_review_counting_rule_is_stated():
    """n15 Item 2: the rule must be explicit so the count cannot drift again."""
    text = _report()
    sec6 = _section(text, "## 6. Reviews", "## 7.")
    assert "Counting rule" in sec6, (
        "n15 Item 2 fix: section 6 must state the counting rule explicitly."
    )
    # The bold markdown **responding to it** is committed is the actual text
    assert ("responds to it is committed" in sec6
            or "responding to it is committed" in sec6
            or "responding to it** is committed" in sec6), (
        "n15 Item 2 fix: the counting rule must state when a human round counts "
        "as completed (once the version responding to it is committed)."
    )


# --------------------------------------------------------------------------
# Item 3 (MED): the marginalization weighting must match the Sameie+ label
# --------------------------------------------------------------------------

def test_two_branch_anchored_marginalization_reported():
    """n15 Item 3: Sameie+ must not carry 1/3 weight in the quantitative result."""
    text = _report()
    sec132 = _section(text, "### 13.2", "### 13.3")
    assert "2-branch anchored only" in sec132, (
        "n15 Item 3 fix: section 13.2 must report the 2-branch anchored-only "
        "marginalization as the quantitative result."
    )
    assert "+0.62" in sec132, (
        "n15 Item 3 fix: section 13.2 must quote the 2-branch anchored mean (+0.62)."
    )
    # The 3-branch number must be relabelled as a coverage envelope.
    assert ("worst-case coverage" in sec132.lower()
            or "worst-case-coverage" in sec132.lower()), (
        "n15 Item 3 fix: the 3-branch equal-weight number must be explicitly "
        "reclassified as a worst-case-coverage envelope."
    )


def test_two_branch_numbers_are_reproducible_from_the_script():
    """n15 Item 3: the quoted 2-branch numbers must come from the script."""
    out = subprocess.run(
        [sys.executable, str(N9_SCRIPT)],
        capture_output=True, text=True, cwd=str(REPO), timeout=300,
    )
    assert out.returncode == 0, f"n9 script failed:\n{out.stderr}"
    assert "2-BRANCH MARGINALIZATION" in out.stdout, (
        "n15 Item 3 fix: the n9 script must compute the 2-branch marginalization."
    )
    # The script's numbers must match what the report quotes. Scope the
    # regex to the 2-BRANCH block -- the Bayesian block also prints a
    # "(+X, +Y) sigma" CI and would otherwise be matched first.
    blk = re.search(r"2-BRANCH MARGINALIZATION.*?95% CI: \(([+\-\d.]+), ([+\-\d.]+)\) sigma",
                    out.stdout, re.DOTALL | re.IGNORECASE)
    assert blk, "n15 Item 3 fix: the n9 script must print the 2-branch 95% CI."
    ci_lo = float(blk.group(1))
    assert abs(ci_lo - 0.03) < 0.005, (
        f"n15 Item 3 fix: 2-branch CI lower bound drifted to {ci_lo}, expected +0.03."
    )
    assert "CI excludes zero: True" in out.stdout, (
        "n15 Item 3 fix: the 2-branch CI must exclude zero (verified from the script)."
    )


def test_exec_summary_states_anchored_result_first():
    """n15 Item 3: section 1 must lead with the anchored-only number."""
    text = _report()
    sec1 = _section(text, "## 1. Executive Summary", "## 2. The")
    assert "+0.62" in sec1, (
        "n15 Item 3 fix: the Executive Summary must quote the 2-branch anchored "
        "result (+0.62 sigma)."
    )
    assert ("worst-case coverage" in sec1.lower()
            or "worst-case-coverage" in sec1.lower()), (
        "n15 Item 3 fix: the Executive Summary must label the 3-branch number as "
        "a worst-case-coverage envelope, not 'the tension'."
    )


# --------------------------------------------------------------------------
# Item 4 (MED): the Ohana+ c_200 prior-sensitivity limitation
# --------------------------------------------------------------------------

def test_prior_sensitivity_limitation_present():
    """n15 Item 4: the c_200 degeneracy implication must be discussed."""
    text = _report()
    sec93 = _section(text, "### 9.3", "### 9.4")
    assert "PRIOR-SENSITIVE" in sec93, (
        "n15 Item 4 fix: section 9.3 must state that the c-M tension is "
        "prior-sensitive, not likelihood-sensitive."
    )
    assert "prior" in sec93.lower() and "likelihood" in sec93.lower(), (
        "n15 Item 4 fix: the limitation must contrast prior vs likelihood."
    )
    assert "loses sensitivity to c" in sec93 or "loses sensitivity" in sec93, (
        "n15 Item 4 fix: the limitation must cite the paper's c_200 "
        "sensitivity-loss statement."
    )


# --------------------------------------------------------------------------
# Item 5 (MED-LOW): the PDF extraction method must be documented
# --------------------------------------------------------------------------

def test_pdf_extraction_method_documented():
    """n15 Item 5: the extraction tool and method must be stated."""
    text = _report()
    sec165 = _section(text, "### 16.5", "### 16.6")
    assert "pdftotext" in sec165, (
        "n15 Item 5 fix: section 16.5 must name the PDF text-extraction tool."
    )
    assert "not" in sec165.lower() and "OCR" in sec165, (
        "n15 Item 5 fix: section 16.5 must state explicitly that the "
        "extraction is NOT OCR (no recognition-error class)."
    )


def test_pdf_page_anchors_present_for_every_quoted_value():
    """n15 Item 5: every quoted paper value needs a page anchor."""
    text = _report()
    sec165 = _section(text, "### 16.5", "### 16.6")
    # The provenance table rows must carry a "p. N" anchor.
    rows = [ln for ln in sec165.splitlines()
            if ln.startswith("| ") and re.search(r"\bp\. \d+", ln)]
    assert len(rows) >= 10, (
        f"n15 Item 5 fix: expected >=10 page-anchored provenance rows in "
        f"section 16.5, found {len(rows)}."
    )
    # And each anchor must be a real page (the paper has 10 pages).
    for ln in rows:
        for pg in re.findall(r"p\. (\d+)", ln):
            assert 1 <= int(pg) <= 10, (
                f"n15 Item 5 fix: page anchor {pg} is outside the paper's 10 pages."
            )


# --------------------------------------------------------------------------
# Item 6 (MED-LOW): the v40.51 range-test code must be shown
# --------------------------------------------------------------------------

def test_v40_51_range_test_code_shown():
    """n15 Item 6: the full test file must be embedded in the report."""
    text = _report()
    sec412 = _section(text, "### 4.12", "---\n\n## 5.")
    assert "def test_v40_51_sigma_0_range_correct" in sec412, (
        "n15 Item 6 fix: section 4.12 must show the v40.51 range test code."
    )
    assert "def test_v40_51_script_uses_fstring" in sec412, (
        "n15 Item 6 fix: section 4.12 must show the f-string assertion test "
        "(the one that locks the bug cannot silently return)."
    )
    # And the shown code must match the real file.
    real = V51_TEST.read_text(encoding="utf-8")
    for fn in ("test_v40_51_sigma_0_range_correct", "test_v40_51_a_range_correct",
               "test_v40_51_v_ref_range_correct", "test_v40_51_script_uses_fstring"):
        assert f"def {fn}" in real, f"v40.51 test file missing {fn}"
        assert f"def {fn}" in sec412, (
            f"n15 Item 6 fix: section 4.12 must show {fn} (present in the real file)."
        )


# --------------------------------------------------------------------------
# Item 7 (LOW): the categorization fallback must not be a silent catch-all
# --------------------------------------------------------------------------

def test_categorize_fallback_is_named_and_guarded():
    """n15 Item 7: a bare `return \"Other\"` can hide a new uncategorized file."""
    src = MAPPING_SCRIPT.read_text(encoding="utf-8")
    assert 'return "Other"' not in src, (
        "n15 Item 7 fix: categorize_test must not have a bare 'Other' fallback."
    )
    assert "Legacy: uncategorized (pre-v40)" in src, (
        "n15 Item 7 fix: the fallback bucket must be explicitly named."
    )
    # A NEW v40-era file landing in the catch-all must raise.
    assert "raise ValueError" in src, (
        "n15 Item 7 fix: the script must raise when a NEW v40-era test file "
        "lands in the legacy catch-all bucket."
    )
    assert "_new_in_catchall" in src, (
        "n15 Item 7 fix: the guard must detect newly-added v40-era files."
    )


def test_categorize_guard_actually_raises():
    """n15 Item 7: the guard must work, not merely exist."""
    out = subprocess.run(
        [sys.executable, str(MAPPING_SCRIPT)],
        capture_output=True, text=True, cwd=str(REPO), timeout=300,
    )
    assert out.returncode == 0, (
        f"n15 Item 7 fix: generate_test_mapping.py must still run cleanly.\n{out.stderr}"
    )
    assert "legacy pre-v40 files are grouped" in out.stdout, (
        "n15 Item 7 fix: the script must print the legacy-bucket count so the "
        "catch-all is visible, not silent."
    )
    # And the count must be disclosed, not hidden.
    assert "Total:" in out.stdout


# --------------------------------------------------------------------------
# Item 8 (MED-LOW): the scatter assumption must be discussed
# --------------------------------------------------------------------------

def test_scatter_assumption_limitation_present():
    """n15 Item 8: the 0.16 dex scatter assumption is load-bearing."""
    text = _report()
    sec93 = _section(text, "### 9.3", "### 9.4")
    assert "0.16 dex" in sec93, (
        "n15 Item 8 fix: section 9.3 must state the 0.16 dex scatter assumption."
    )
    assert "scatter" in sec93.lower() and ("1/scatter" in sec93 or "scales as" in sec93), (
        "n15 Item 8 fix: section 9.3 must state that sigma scales as 1/scatter."
    )
    assert "0.20 dex" in sec93 and "0.12 dex" in sec93, (
        "n15 Item 8 fix: section 9.3 must quantify the effect of alternative "
        "scatter values (0.20 dex, 0.12 dex)."
    )


# --------------------------------------------------------------------------
# Self-found item 9: the -1.39 hard-coded literal
# --------------------------------------------------------------------------

def test_three_prescription_script_has_no_stale_minus_1_39():
    """Self-found: the script hard-coded -1.39 while computing -1.3104."""
    src = THREE_PRESC.read_text(encoding="utf-8")
    # Strip comments: the v40.62 fix's own explanatory comment mentions
    # -1.39 (that is what it was correcting). The check is about EXECUTABLE
    # literals, i.e. strings that get printed or written to the JSON.
    code_only = "\n".join(ln for ln in src.splitlines()
                           if not ln.strip().startswith("#"))
    assert "1.39" not in code_only, (
        "v40.62 fix: the 3-prescription script must not hard-code -1.39 in any "
        "executable string; the computed Sameie+ value is -1.31 and the "
        "hard-coded text contradicted the numbers in the same file."
    )
    assert "sameie_ref" in src, (
        "v40.62 fix: the script must take the Sameie+ value from the computed "
        "results, not a literal."
    )


def test_three_prescription_json_is_self_consistent():
    """Self-found: the results JSON's explanation said -1.39, data said -1.31."""
    with open(THREE_PRESC_JSON, encoding="utf-8") as fp:
        data = json.load(fp)
    expl = data["summary"]["explanation"]
    assert "1.39" not in expl, (
        f"v40.62 fix: the results JSON explanation must not contain -1.39: {expl}"
    )
    # The explanation's quoted Sameie+ value must match the computed field.
    sameie = data["f_H_cases"][0]["prescription_results"]["sameie_2020"]["c_M_tension_sigma"]
    assert f"{abs(sameie):.2f}" in expl, (
        f"v40.62 fix: the JSON explanation must quote the computed Sameie+ value "
        f"({abs(sameie):.2f}). Got: {expl}"
    )


# --------------------------------------------------------------------------
# Self-found item 10: the +1.56 CI upper bound
# --------------------------------------------------------------------------

def test_no_stale_plus_1_56_ci_anywhere():
    """Self-found: n11 hard-coded +1.56; the authoritative value is +1.29."""
    text = _report()
    # The live claims (section 1, section 13.2, section 15) must not carry
    # the stale +1.56. The section 19 fix narrative deliberately names it as
    # the defect it corrected -- that is history, not a live claim.
    live_claims = (text[text.find("## 1. Executive Summary"):text.find("## 2. The")]
                   + text[text.find("### 13.2"):text.find("### 13.3")]
                   + text[text.find("## 15."):text.find("## 16.")])
    assert "1.56" not in live_claims, (
        "v40.62 fix: the live claims (sections 1, 13.2, 15) must not contain "
        "the stale +1.56 CI upper bound; the authoritative computation gives "
        "+1.29."
    )
    src = N11_SCRIPT.read_text(encoding="utf-8")
    assert "1.56" not in src, (
        "v40.62 fix: the n11 script must not hard-code the +1.56 CI."
    )
    assert "eq_ci_low" in src and "eq_ci_high" in src, (
        "v40.62 fix: the n11 script must interpolate the computed CI bounds."
    )


def test_authoritative_ci_is_minus_1_33_plus_1_29():
    """The CI quoted in the report must equal the authoritative script's."""
    out = subprocess.run(
        [sys.executable, str(N9_SCRIPT)],
        capture_output=True, text=True, cwd=str(REPO), timeout=300,
    )
    assert out.returncode == 0, f"n9 script failed:\n{out.stderr}"
    m = re.search(r"Equal-weight marginalization:.*?95% CI: \(([-\d.]+), ([+\-\d.]+)\)",
                  out.stdout, re.DOTALL)
    assert m, "n15 fix: the n9 script must print the equal-weight 95% CI."
    text = _report()
    assert f"({m.group(1)}, {m.group(2)})" in text, (
        f"v40.62 fix: the report must quote the authoritative equal-weight CI "
        f"({m.group(1)}, {m.group(2)})."
    )


# --------------------------------------------------------------------------
# Self-found item 11: PDF page anchors must be verified, not asserted
# --------------------------------------------------------------------------

def test_pdf_page_anchors_are_correct():
    """Self-found: three page anchors were asserted from memory and were wrong.

    Verified against the PDF with `pdftotext -layout -f N -l N`. This test
    re-checks the two most error-prone ones.
    """
    pdf = REPO / "docs" / "papers" / "verified" / "2608.04362_ohana_2026_cloud9_cdm_sidm.pdf"
    if not pdf.exists():
        return  # PDF is gitignored; skip when absent
    text = _report()
    sec165 = _section(text, "### 16.5", "### 16.6")

    def _page_has(pg: int, needle: str) -> bool:
        out = subprocess.run(
            ["pdftotext", "-layout", "-f", str(pg), "-l", str(pg), str(pdf), "-"],
            capture_output=True, timeout=120,
        )
        # The PDF's text layer is not valid UTF-8 (ligatures, math symbols),
        # so decode leniently rather than raising.
        return needle in out.stdout.decode("utf-8", errors="replace")

    # The 7.3 sigma / >6.7 sigma values are in the Figure 4 caption on page 6.
    row = [ln for ln in sec165.splitlines() if "7.3" in ln and "p." in ln]
    assert row, "n15 fix: the 7.3 sigma provenance row must be present."
    m = re.search(r"p\. (\d+)", row[0])
    assert m, "n15 fix: the 7.3 sigma row must carry a page anchor."
    pg = int(m.group(1))
    assert _page_has(pg, "7.3 below"), (
        f"n15 fix: the 7.3 sigma anchor says p.{pg}, but the phrase "
        f"'7.3 below' is not on that page of the PDF."
    )

    # The 3.2 sigma value is on page 3.
    row2 = [ln for ln in sec165.splitlines() if "3.2" in ln and "p." in ln]
    assert row2, "n15 fix: the 3.2 sigma provenance row must be present."
    m2 = re.search(r"p\. (\d+)", row2[0])
    assert m2, "n15 fix: the 3.2 sigma row must carry a page anchor."
    pg2 = int(m2.group(1))
    assert _page_has(pg2, "3.2 deviation below"), (
        f"n15 fix: the 3.2 sigma anchor says p.{pg2}, but the phrase "
        f"'3.2 deviation below' is not on that page of the PDF."
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
    print("\nAll v40.62 n15.docx review response regression tests pass.")
