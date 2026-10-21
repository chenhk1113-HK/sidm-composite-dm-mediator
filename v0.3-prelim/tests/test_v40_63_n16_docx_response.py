"""Regression tests for v40.63: n16.docx review response (11th human review).

Per n16.docx (2026-10-21, Chinese-language review of the v40.62 report), the
following issues were raised. Each test below locks the v40.63 fix.

N16.DOCX FINDINGS ADDRESSED:
1. [MED]     collapse_time_gyr_implementation() prints a wrong unit-conversion
   formula (rho_s * 1e9 * (3.086e19)**3 instead of
   rho_s * 1.989e30 / (3.086e19)**3, ~1e95 off).
2. [MED-LOW] generate_test_mapping.py has a Windows hard-coded TEST_DIR.
3. [LOW-MED] monte_carlo_71_percent() is an analytic binomial estimate, not a
   Monte Carlo simulation; the name and docstring are misleading.
4. [LOW]     Report section 4.9's code listing is incomplete (omits the
   imports and the TEST_DIR assignment).
5. [LOW-MED] The Bayesian sigma_u values' provenance is undocumented (0.20
   for Elbert has a published basis; 0.30 / 0.50 are project assumptions).
6. [LOW]     test_pdf_page_anchors_are_correct() calls pdftotext with no
   availability check, so a missing poppler raises FileNotFoundError
   instead of skipping.
7. [MED]     Burkert-style's "anchored" status is weaker than Elbert+'s --
   "2-branch anchored" is really "1 paper-anchored + 1 project prescription",
   which is a selection bias.
8. [MED]     The +0.62 sigma signal may vanish under scatter uncertainty.

SELF-FOUND (surfaced while auditing n16's Item 8, HIGH severity):
9.  The shipped 95% CIs used the NORMAL approximation (z = 1.96) on samples
   with an ESTIMATED variance (n = 2 and n = 3), where the t-distribution is
   required. Under the correct critical value NO branch set's CI excludes
   zero -- so the v40.62 headline "CI EXCLUDES ZERO" was wrong.
"""
from __future__ import annotations

import json
import math
import re
import shutil
import statistics
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
REPORT = REPO / "docs" / "SIDM_V40_51_FULL_REVIEW_REPORT_2026_10_19.md"
N9_SCRIPT = REPO / "scripts" / "v19_2_f_n9_docx_response.py"
MAPPING_SCRIPT = REPO / "scripts" / "generate_test_mapping.py"
NO_PEAK_JSON = (REPO / "v0.3-prelim" / "data" / "results"
                 / "v19_2_f_no_peak_analysis_2026_10_19.json")


def _report() -> str:
    return REPORT.read_text(encoding="utf-8")


def _section(text: str, start: str, end: str) -> str:
    i = text.find(start)
    assert i != -1, f"Section start marker not found: {start!r}"
    j = text.find(end, i)
    assert j != -1, f"Section end marker not found: {end!r}"
    return text[i:j]


# --------------------------------------------------------------------------
# Item 1 [MED]: the collapse_time print block must not carry the v40.54
# fabrication. It must show the ACTUAL current implementation.
# --------------------------------------------------------------------------

def test_collapse_time_print_block_has_no_wrong_unit_conversion():
    """n16 Item 1: the printed SI conversion was off by ~1e95."""
    src = N9_SCRIPT.read_text(encoding="utf-8")
    # The precise invariant: the wrong conversion must never appear as an
    # ASSIGNMENT. The print block does quote the old form while explaining
    # what was corrected, so a bare-substring ban would be wrong.
    assert "rho_s_si = rho_s * 1e9" not in src, (
        "n16 Item 1 fix: the wrong unit conversion "
        "'rho_s_si = rho_s * 1e9 * (3.086e19)**3' must not appear as an "
        "assignment. Correct: rho_s_si = rho_s * 1.989e30 / (3.086e19)**3 "
        "(off by ~4.3e95)."
    )
    # The correct conversion must be documented.
    assert "rho_s_si = rho_s * 1.989e30 / (3.086e19)**3" in src, (
        "n16 Item 1 fix: the correct conversion must be documented in the "
        "print block so the unit convention is explicit."
    )
    assert "1.989e30" in src, (
        "n16 Item 1 fix: the correct conversion constant (1.989e30 kg/M_sun) "
        "must appear so the unit convention is documented."
    )


def test_collapse_time_print_block_names_the_real_source_file():
    """n16 Item 1: the block claimed a file that does not exist."""
    src = N9_SCRIPT.read_text(encoding="utf-8")
    assert "v19_2_f_gravothermal_yang2024.py" not in src, (
        "n16 Item 1 fix: the print block named a non-existent file "
        "'v19_2_f_gravothermal_yang2024.py'. The real one is "
        "'v0.3-prelim/code/gravothermal_yang2024.py'."
    )
    assert "gravothermal_yang2024.py" in src, (
        "n16 Item 1 fix: the print block must name the real implementation file."
    )
    # And that file must actually exist.
    assert (REPO / "v0.3-prelim" / "code" / "gravothermal_yang2024.py").exists()


def test_collapse_time_print_block_has_correct_tau_direction():
    """n16 Item 1: the block printed tau = t_core/13.8 (inverted)."""
    src = N9_SCRIPT.read_text(encoding="utf-8")
    code_only = "\n".join(ln for ln in src.splitlines()
                           if not ln.strip().startswith("#"))
    assert "tau = 0.35 / 13.8" not in code_only, (
        "n16 Item 1 fix: the inverted tau expression must be gone. The "
        "project convention is tau = T_Hubble / t_core."
    )
    assert "T_Hubble / t_core" in src, (
        "n16 Item 1 fix: the print block must state the correct tau "
        "definition (tau = T_Hubble / t_core)."
    )


def test_collapse_time_print_block_quotes_the_true_t_core_values():
    """n16 Item 1: the block printed t_core = 0.35 / 0.0008 Gyr.

    The stored v40.46 JSON says 0.8411 Gyr and 230.151 Gyr.
    """
    src = N9_SCRIPT.read_text(encoding="utf-8")
    code_only = "\n".join(ln for ln in src.splitlines()
                           if not ln.strip().startswith("#"))
    assert "t_core = 0.35 Gyr" not in code_only, (
        "n16 Item 1 fix: t_core = 0.35 Gyr is wrong; the stored JSON says "
        "0.8411 Gyr."
    )
    assert "t_core = 230.2 Gyr" in src and "t_core = 0.84 Gyr" in src, (
        "n16 Item 1 fix: the print block must quote the true t_core values "
        "(0.84 Gyr and 230.2 Gyr)."
    )
    # Cross-check against the stored JSON -- the numbers must agree.
    with open(NO_PEAK_JSON, encoding="utf-8") as fp:
        data = json.load(fp)
    tc = [c["t_core_Gyr"] for c in data["cases"]]
    assert abs(tc[0] - 0.8411) < 1e-3, f"stored t_core changed: {tc}"
    assert abs(tc[1] - 230.151) < 1e-2, f"stored t_core changed: {tc}"
    # tau must be T_Hubble / t_core for both stored cases.
    for c in data["cases"]:
        assert abs(c["tau"] - 13.8 / c["t_core_Gyr"]) < 1e-6, (
            f"stored tau is not T_Hubble/t_core: {c}"
        )


def test_collapse_time_print_block_has_no_placeholder_citation():
    """n16 Item 1: 'arXiv:2405.XXXXX' is not a resolvable identifier."""
    src = N9_SCRIPT.read_text(encoding="utf-8")
    assert "2405.XXXXX" not in src, (
        "n16 Item 1 fix: the placeholder citation 'arXiv:2405.XXXXX' must be "
        "removed or replaced with a real identifier."
    )


# --------------------------------------------------------------------------
# Item 2 [MED-LOW]: the TEST_DIR must not be a hard-coded absolute path
# --------------------------------------------------------------------------

def test_test_dir_is_not_hardcoded_absolute():
    """n16 Item 2: a Windows absolute path makes the script non-portable."""
    src = MAPPING_SCRIPT.read_text(encoding="utf-8")
    assert 'TEST_DIR = r"C:' not in src, (
        "n16 Item 2 fix: TEST_DIR must not be a hard-coded absolute Windows "
        "path."
    )
    assert "Path(__file__).resolve()" in src, (
        "n16 Item 2 fix: TEST_DIR must be derived from __file__ so the script "
        "runs on any platform."
    )
    # And the derived path must actually resolve to the tests directory.
    # Run the script as a subprocess (exec() has no __file__) and check that
    # it enumerates the real test files.
    out = subprocess.run(
        [sys.executable, str(MAPPING_SCRIPT)],
        capture_output=True, text=True, cwd=str(REPO), timeout=300,
    )
    assert out.returncode == 0, f"generate_test_mapping.py failed:\n{out.stderr}"
    m = re.search(r"^Total:\s*(\d+)\s+test files", out.stdout, re.M)
    assert m, f"could not read the file count from:\n{out.stdout[:500]}"
    n_files = int(m.group(1))
    on_disk = len([p for p in (REPO / "v0.3-prelim" / "tests").iterdir()
                   if p.name.startswith("test_") and p.name.endswith(".py")])
    assert n_files == on_disk, (
        f"n16 Item 2 fix: the script enumerated {n_files} test files but "
        f"{on_disk} exist on disk -- TEST_DIR does not resolve correctly."
    )


def test_mapping_script_still_runs():
    """n16 Item 2: the path change must not break the script."""
    out = subprocess.run(
        [sys.executable, str(MAPPING_SCRIPT)],
        capture_output=True, text=True, cwd=str(REPO), timeout=300,
    )
    assert out.returncode == 0, f"generate_test_mapping.py failed:\n{out.stderr}"
    assert "Total:" in out.stdout


# --------------------------------------------------------------------------
# Item 3 [LOW-MED]: the function name must match what it does
# --------------------------------------------------------------------------

def test_monte_carlo_function_renamed():
    """n16 Item 3: it is an analytic binomial, not a Monte Carlo."""
    src = N9_SCRIPT.read_text(encoding="utf-8")
    # The rename note in the docstring legitimately names the old function;
    # what must not survive is the old IDENTIFIER as a def or a call.
    code_only = "\n".join(ln for ln in src.splitlines()
                           if not ln.strip().startswith("#"))
    assert "def monte_carlo_71_percent" not in code_only, (
        "n16 Item 3 fix: the misleading function name 'monte_carlo_71_percent' "
        "must be replaced (it performs no sampling)."
    )
    assert "monte_carlo_71_percent(" not in code_only, (
        "n16 Item 3 fix: no call site may still use the old name."
    )
    assert "def binomial_null_71_percent" in src, (
        "n16 Item 3 fix: the function must be named for what it computes."
    )
    # The docstring's SUMMARY line must not claim a simulation is run.
    # (The body of the docstring legitimately mentions "Monte Carlo" while
    #  explaining the rename, so only the summary line is checked.)
    m = re.search(r'def binomial_null_71_percent\(\):\s*\n\s*"""(.*?)"""',
                  src, re.DOTALL)
    assert m, "n16 Item 3 fix: could not find the renamed function's docstring"
    summary = m.group(1).strip().splitlines()[0].lower()
    assert "monte carlo" not in summary, (
        f"n16 Item 3 fix: the docstring summary still claims a Monte Carlo: "
        f"{summary!r}"
    )
    assert "analytic" in summary, (
        f"n16 Item 3 fix: the docstring summary must state that the estimate "
        f"is analytic: {summary!r}"
    )
    # And the printed header must not claim a Monte Carlo either.
    code_only = "\n".join(ln for ln in src.splitlines()
                           if not ln.strip().startswith("#"))
    assert "MONTE CARLO 71% SIGNIFICANCE" not in code_only, (
        "n16 Item 3 fix: the printed header must not claim a Monte Carlo."
    )
    assert "BINOMIAL NULL-HYPOTHESIS TEST" in code_only, (
        "n16 Item 3 fix: the printed header must say what the computation is."
    )


def test_printed_method_block_describes_no_sampling():
    """n16 Item 3: the printed METHOD block described a sampling loop."""
    src = N9_SCRIPT.read_text(encoding="utf-8")
    code_only = "\n".join(ln for ln in src.splitlines()
                           if not ln.strip().startswith("#"))
    assert "Sample N random" not in code_only, (
        "n16 Item 3 fix: the printed METHOD block must not describe a random "
        "sampling procedure that is never performed."
    )
    assert "no random sampling" in src, (
        "n16 Item 3 fix: the printed METHOD block must state that no sampling "
        "is performed."
    )


# --------------------------------------------------------------------------
# Item 4 [LOW]: the section 4.9 listing must be complete and current
# --------------------------------------------------------------------------

def test_section_4_9_listing_is_complete_and_matches_live_file():
    """n16 Item 4: the listing omitted the file header."""
    text = _report()
    sec49 = _section(text, "### 4.9 `scripts/generate_test_mapping.py`", "\n### ")
    m = re.search(r"```python\n(.*?)\n```", sec49, re.DOTALL)
    assert m, "n16 Item 4 fix: section 4.9 must contain a python code block."
    listed = m.group(1)
    live = MAPPING_SCRIPT.read_text(encoding="utf-8").rstrip()
    assert listed == live, (
        "n16 Item 4 fix: the section 4.9 listing must be the COMPLETE live "
        "file (byte-identical), so it cannot drift from the script."
    )
    for probe in ("import os", "from pathlib import Path", "TEST_DIR",
                  "def categorize_test"):
        assert probe in listed, (
            f"n16 Item 4 fix: the listing must include {probe!r}."
        )


# --------------------------------------------------------------------------
# Item 5 [LOW-MED]: the sigma_u provenance must be documented
# --------------------------------------------------------------------------

def test_sigma_u_provenance_documented():
    """n16 Item 5: only Elbert's sigma_u has a published basis."""
    src = N9_SCRIPT.read_text(encoding="utf-8")
    assert "PROVENANCE of each sigma_u" in src, (
        "n16 Item 5 fix: the script must document the provenance of each "
        "sigma_u value."
    )
    doc = src[src.find("PROVENANCE of each sigma_u"):]
    doc = doc[: doc.find('"""')]
    assert "Elbert" in doc and "published basis" in doc, (
        "n16 Item 5 fix: the documentation must say that Elbert's 0.20 is the "
        "only one with a published basis."
    )
    assert "Burkert" in doc and "Sameie" in doc and "ASSUMED" in doc, (
        "n16 Item 5 fix: the documentation must mark Burkert's 0.30 and "
        "Sameie's 0.50 as ASSUMED by the project."
    )
    # And the report must carry the same disclosure.
    text = _report()
    sec132 = _section(text, "### 13.2", "### 13.3")
    assert "Provenance of the σ_u values" in sec132, (
        "n16 Item 5 fix: report section 13.2 must document the sigma_u "
        "provenance too."
    )


# --------------------------------------------------------------------------
# Item 6 [LOW]: the pdftotext availability check
# --------------------------------------------------------------------------

def test_pdf_test_has_pdftotext_availability_check():
    """n16 Item 6: a missing poppler raised FileNotFoundError, not a skip."""
    src = (REPO / "v0.3-prelim" / "tests"
           / "test_v40_62_n15_docx_response.py").read_text(encoding="utf-8")
    assert 'shutil.which("pdftotext")' in src, (
        "n16 Item 6 fix: the PDF page-anchor test must check for pdftotext "
        "before calling it."
    )
    assert "pytest.skip" in src, (
        "n16 Item 6 fix: the PDF page-anchor test must skip (not error) when "
        "poppler is unavailable."
    )


def test_pdf_test_still_passes_with_pdftotext_present():
    """The guard must not break the test when poppler IS available."""
    if shutil.which("pdftotext") is None:
        pytest.skip("pdftotext not on PATH")
    out = subprocess.run(
        [sys.executable, "-m", "pytest",
         str(REPO / "v0.3-prelim" / "tests" / "test_v40_62_n15_docx_response.py"),
         "-q", "-k", "pdf_page_anchors", "--no-header", "-p", "no:cacheprovider"],
        capture_output=True, text=True, cwd=str(REPO), timeout=300,
    )
    assert out.returncode == 0, f"PDF anchor test failed:\n{out.stdout}"


# --------------------------------------------------------------------------
# Item 7 [MED]: the anchoring disclosure + selection bias
# --------------------------------------------------------------------------

def test_burkert_anchoring_status_disclosed_in_exec_summary():
    """n16 Item 7: only Elbert+ is paper-anchored; that must be stated."""
    text = _report()
    sec1 = _section(text, "## 1. Executive Summary", "## 2. The")
    assert "1 paper-anchored + 1 project prescription" in sec1, (
        "n16 Item 7 fix: the Executive Summary must state that "
        "'2-branch anchored' means '1 paper-anchored + 1 project prescription'."
    )
    assert "selection bias" in sec1.lower(), (
        "n16 Item 7 fix: the Executive Summary must name the selection bias."
    )


def test_selection_bias_discussed_in_13_2_and_9_3():
    """n16 Item 7: the disclosure must not live only in the summary."""
    text = _report()
    sec132 = _section(text, "### 13.2", "### 13.3")
    sec93 = _section(text, "### 9.3", "### 9.4")
    for name, sec in (("13.2", sec132), ("9.3", sec93)):
        # The disclosure language: the branch set is selected on agreement,
        # and only one retained branch is paper-anchored.
        assert "selected on agreement" in sec or "SELECTION BIAS" in sec.upper(), (
            f"n16 Item 7 fix: section {name} must disclose that the branch "
            f"set is selected on agreement."
        )
        assert "Burkert" in sec, (
            f"n16 Item 7 fix: section {name} must name Burkert-style."
        )
        assert "paper-anchored" in sec, (
            f"n16 Item 7 fix: section {name} must distinguish the paper-anchored "
            f"branch from the project prescription."
        )


def test_quantitative_status_fields_unchanged_and_consistent():
    """The 5.4 JSON labels are the SOURCE of the anchoring claim."""
    text = _report()
    sec54 = _section(text, "### 5.4", "## 6. Reviews")
    assert '"quantitative_status": "anchored to paper Eq. 5"' in sec54, (
        "n16 Item 7: Elbert's quantitative_status must still say 'anchored to "
        "paper Eq. 5' -- the disclosure depends on it."
    )
    assert '"quantitative_status": "project prescription, not paper-derived"' in sec54, (
        "n16 Item 7: Burkert-style's quantitative_status must still say "
        "'project prescription, not paper-derived'."
    )


# --------------------------------------------------------------------------
# Item 8 [MED]: the scatter question -- and the CORRECT answer
# --------------------------------------------------------------------------

def test_scatter_does_not_vanish_the_signal():
    """n16 Item 8's premise: scatter could make the signal vanish.

    It does not: sigma scales as 1/scatter UNIFORMLY, so the mean and the
    SE rescale together and the CI lower bound stays proportional.
    """
    vals = [0.32, 0.93]
    for scatter in (0.08, 0.12, 0.16, 0.20, 0.24):
        k = 0.16 / scatter
        v = [x * k for x in vals]
        m = statistics.mean(v)
        se = statistics.stdev(v) / math.sqrt(2)
        lo = m - 1.96 * se
        assert lo > 0, (
            f"n16 Item 8: at scatter={scatter} dex the CI lower bound should "
            f"stay positive (got {lo:+.4f}). If this fails, the uniform-rescale "
            f"argument in the report is wrong and must be corrected."
        )


def test_scatter_sensitivity_table_in_9_3():
    """n16 Item 8: the scatter effect must be quantified in 9.3."""
    text = _report()
    sec93 = _section(text, "### 9.3", "### 9.4")
    assert "Quantification" in sec93, (
        "n16 Item 8 fix: section 9.3 must quantify the scatter sensitivity."
    )
    for sc in ("0.08", "0.12", "0.20", "0.24"):
        assert sc in sec93, (
            f"n16 Item 8 fix: the scatter table must include {sc} dex."
        )
    assert "sample size, not the scatter" in sec93, (
        "n16 Item 8 fix: section 9.3 must state that the reason the tension "
        "is not significant is the sample size, not the scatter."
    )


# --------------------------------------------------------------------------
# SELF-FOUND item 9 [HIGH]: the CI convention
# --------------------------------------------------------------------------

def test_shipped_cis_use_t_not_z():
    """Self-found: the shipped CIs used z=1.96 on an estimated variance."""
    out = subprocess.run(
        [sys.executable, str(N9_SCRIPT)],
        capture_output=True, text=True, cwd=str(REPO), timeout=300,
    )
    assert out.returncode == 0, f"n9 script failed:\n{out.stderr}"
    assert "95% CI (t-distribution, correct for n=2)" in out.stdout, (
        "self-found item 9 fix: the 2-branch CI must be reported with the "
        "t-distribution as the primary number."
    )
    assert "95% CI (t-distribution, correct for n=3)" in out.stdout, (
        "self-found item 9 fix: the 3-branch CIs must be reported with the "
        "t-distribution as the primary number."
    )
    assert "ANTI-CONSERVATIVE" in out.stdout, (
        "self-found item 9 fix: the retained z-based CIs must be labelled "
        "anti-conservative."
    )


def test_t_critical_values_match_scipy():
    """The hard-coded t values must match scipy exactly."""
    scipy_stats = pytest.importorskip("scipy.stats")
    src = N9_SCRIPT.read_text(encoding="utf-8")
    m = re.search(r"T_CRIT_95 = \{([^}]+)\}", src)
    assert m, "could not find T_CRIT_95 in the script"
    table = {}
    for df, val in re.findall(r"(\d+):\s*([0-9.]+)", m.group(1)):
        table[int(df)] = float(val)
    assert table, "T_CRIT_95 is empty"
    for df, val in table.items():
        expected = float(scipy_stats.t.ppf(0.975, df))
        assert abs(val - expected) < 0.001, (
            f"t critical value for df={df}: script has {val}, scipy has "
            f"{expected:.4f}"
        )


def test_no_branch_set_ci_excludes_zero_under_t():
    """Self-found: under correct small-n statistics NO CI excludes zero."""
    out = subprocess.run(
        [sys.executable, str(N9_SCRIPT)],
        capture_output=True, text=True, cwd=str(REPO), timeout=300,
    )
    assert out.returncode == 0
    stdout = out.stdout
    assert "CI excludes zero: False" in stdout, (
        "self-found item 9 fix: the 2-branch t-based CI must NOT exclude zero "
        "(t(0.975, df=1) = 12.706 gives (-3.25, +4.50))."
    )
    # The weighting-scheme summary table must show 'no' for every row.
    m = re.search(r"WEIGHTING-SCHEME SUMMARY.*?\n\n", stdout, re.DOTALL)
    assert m, "could not find the weighting-scheme summary in the script output"
    table = m.group(0)
    assert "True" not in table, (
        f"self-found item 9 fix: no branch set's t-based CI may exclude zero, "
        f"but the summary table shows one that does:\n{table}"
    )


def test_report_headline_no_longer_claims_ci_excludes_zero():
    """The Executive Summary must not carry the corrected claim."""
    text = _report()
    sec1 = _section(text, "## 1. Executive Summary", "## 2. The")
    # The v40.62 claim must be gone from the live claim line.
    assert "CI EXCLUDES ZERO (marginally" not in sec1, (
        "self-found item 9 fix: the Executive Summary must not claim the "
        "CI excludes zero."
    )
    # It must appear only as a CORRECTION notice.
    assert "v40.63 CORRECTION" in sec1, (
        "self-found item 9 fix: the Executive Summary must record the "
        "correction explicitly rather than silently changing the number."
    )
    assert "(-3.25, +4.50) σ" in sec1 or "(−3.25, +4.50) σ" in sec1, (
        "self-found item 9 fix: the Executive Summary must quote the "
        "corrected t-based 2-branch CI."
    )


def test_point_estimate_unchanged():
    """The correction must NOT change the point estimates."""
    text = _report()
    sec132 = _section(text, "### 13.2", "### 13.3")
    assert "+0.62" in sec132, (
        "self-found item 9 fix: the 2-branch point estimate (+0.62 sigma) is "
        "unchanged by the CI-convention correction and must still be stated."
    )
    out = subprocess.run(
        [sys.executable, str(N9_SCRIPT)],
        capture_output=True, text=True, cwd=str(REPO), timeout=300,
    )
    assert "Mean: +0.62 sigma" in out.stdout, (
        "self-found item 9 fix: the script must still compute +0.62 sigma for "
        "the 2-branch mean."
    )


def test_report_states_the_tension_is_not_significant():
    """The honest framing: a magnitude, not a detection."""
    text = _report()
    sec132 = _section(text, "### 13.2", "### 13.3")
    assert "not a detection" in sec132.lower() or "never as a detection" in sec132.lower(), (
        "self-found item 9 fix: section 13.2 must state that the tension is "
        "reported as a magnitude, never as a detection."
    )
    sec93 = _section(text, "### 9.3", "### 9.4")
    assert "No c-M tension value in this report is statistically significant" in sec93, (
        "self-found item 9 fix: section 9.3 must carry the "
        "not-statistically-significant limitation."
    )


# --------------------------------------------------------------------------
# Report-wide markdown STRUCTURE (v40.63 self-found)
# --------------------------------------------------------------------------

def test_all_fenced_blocks_are_balanced():
    """An inline ``` reference in prose opens an unterminated code block.

    v40.63 self-found: section 18 contained "parses **every** ```json fenced
    block" -- a triple backtick mid-line. Most markdown renderers treat that
    as a fence opener, so everything after it renders as code. It survived
    since v40.61 because the existing checks only regex-extract ```json
    blocks, which does not care about fence state.
    """
    text = _report()
    lines = text.split("\n")
    bt = "`" * 3

    # (a) no triple backtick may appear mid-line.
    for i, ln in enumerate(lines, 1):
        s = ln.strip()
        if bt in ln and s != bt and not s.startswith(bt):
            raise AssertionError(
                f"v40.63 fix: line {i} contains an inline triple backtick, "
                f"which opens an unterminated code block: {ln[:120]!r}"
            )

    # (b) the fences must pair up.
    n = sum(1 for ln in lines if ln.strip().startswith(bt))
    assert n % 2 == 0, (
        f"v40.63 fix: the report has {n} standalone fence lines, which is "
        f"odd -- a code block is unterminated."
    )


def test_no_unterminated_code_block():
    """Walk the fence state machine; every opener must find a closer."""
    lines = _report().split("\n")
    bt = "`" * 3
    in_block = False
    opened_at = 0
    for i, ln in enumerate(lines, 1):
        if ln.strip().startswith(bt):
            if in_block:
                in_block = False
            else:
                in_block = True
                opened_at = i
    assert not in_block, (
        f"v40.63 fix: the code block opened at line {opened_at} is never "
        f"closed."
    )


# --------------------------------------------------------------------------
# Report-wide consistency: the counts must still be self-consistent
# --------------------------------------------------------------------------

def test_report_json_blocks_are_all_strict():
    """Every ```json block in the report must parse."""
    blocks = re.findall(r"```json\n(.*?)\n```", _report(), re.DOTALL)
    assert blocks, "no json blocks found"
    for i, b in enumerate(blocks):
        try:
            json.loads(b)
        except Exception as e:
            raise AssertionError(f"json block {i} is not strict: {e}")


def test_review_counts_are_consistent():
    """The v40.63 count must be stated consistently in header/§6/footer."""
    text = _report()
    sec6 = _section(text, "## 6. Reviews", "## 7.")
    assert "31 rounds" in sec6, (
        "n16 round: section 6 must state 31 review rounds (30 + n16)."
    )
    assert "n6.docx–n16.docx" in sec6, (
        "n16 round: the section 6 table must list n6-n16."
    )
    row = [ln for ln in sec6.splitlines() if "Human (n6.docx" in ln]
    assert row and "| 11 |" in row[0], (
        f"n16 round: the Human row must state 11 rounds. Got: {row}"
    )
    header = text[: text.find("## 1.")]
    assert "11 reviews" in header and "31 review rounds" in header, (
        "n16 round: the header must state 11 human reviews / 31 rounds."
    )
    footer = text[text.rfind("**Reviewed by:**"):]
    assert "11 reviews" in footer and "31 review rounds" in footer, (
        "n16 round: the footer must state 11 human reviews / 31 rounds."
    )


def test_version_counts_are_consistent():
    """v40.61->v40.63: the version count must agree everywhere."""
    text = _report()
    sec2 = _section(text, "## 2. The", "## 3. Framework Status")
    arc = re.search(r"v40\.(\d+)\s*(?:→|->)\s*v40\.(\d+)", sec2)
    assert arc, "n16 round: section 2 must declare a version range."
    lo, hi = int(arc.group(1)), int(arc.group(2))
    n_seq = hi - lo + 1
    count = re.search(r"The (\d+)-Version Arc", sec2)
    assert count and int(count.group(1)) == n_seq, (
        "n16 round: the section 2 header count must equal the range length."
    )
    sec1 = _section(text, "## 1. Executive Summary", "## 2. The")
    assert f"**{n_seq}-version investigation**" in sec1, (
        f"n16 round: the Executive Summary must state {n_seq} versions."
    )
    sec92 = _section(text, "### 9.2", "### 9.3")
    assert f"**{n_seq} sequential versions**" in sec92, (
        f"n16 round: section 9.2 must state {n_seq} sequential versions."
    )


# --------------------------------------------------------------------------
# v40.63 (Defect G class): the production result JSONs must NOT be touched
# by a test run.
# --------------------------------------------------------------------------

# The t90_v5x joint-fit artifacts that the v40.60 clobbering defect degraded
# on every pytest run (a nlive=50 smoke posterior overwrote the nlive=500
# production one).
PRODUCTION_RESULTS = (
    "t90_v51_resonant_joint_posterior.json",
    "t90_v52_multi_portal_joint_posterior.json",
    "t90_v55_hybrid_joint_posterior.json",
    "t90_v56_hybrid_4ch_joint_posterior.json",
    "t90_v57_hybrid_5ch_joint_posterior.json",
)


def test_smoke_tests_do_not_write_into_the_production_results_dir(tmp_path):
    """A smoke run must not be able to overwrite a production artifact.

    The fix has two halves: the writers' default output_dir is now
    env-overridable (SIDM_RESULTS_DIR), and the smoke tests pass
    output_dir=<tmp_path>. This test asserts the SECOND half is in place --
    a caller that forgets output_dir would reintroduce the clobbering.
    """
    import glob
    offenders = []
    # v40.63: cover ALL FIVE writer entry points. The first version of this
    # guard only matched run_dynesty / run_multi_portal, so the three
    # hybrid writers (run_hybrid_joint_fit, _4ch, _5ch) were unchecked --
    # and the v5 gate still clobbered 3 of the 5 production JSONs.
    WRITERS = (
        "run_dynesty",
        "run_multi_portal",
        "run_hybrid_joint_fit",
        "run_hybrid_joint_fit_4ch",
        "run_hybrid_joint_fit_5ch",
    )
    pat = re.compile(r"^.*\b(" + "|".join(WRITERS) + r")\(.*$", re.M)
    for tp in (Path(__file__).resolve().parent).glob("test_t90_v5*.py"):
        src = tp.read_text(encoding="utf-8")
        for m in pat.finditer(src):
            line = m.group(0)
            if "output_dir" not in line:
                offenders.append(f"{tp.name}: {line.strip()}")
    assert not offenders, (
        "v40.63 fix: these smoke-test calls would write into the PRODUCTION "
        "results directory and overwrite the artifact with a lower-quality "
        "posterior (v40.60 Defect E class). Pass output_dir=str(tmp_path):\n"
        + "\n".join(offenders)
    )


def test_production_result_jsons_exist_and_are_non_trivial():
    """The 5 production artifacts must be present and carry a real posterior."""
    res_dir = REPO / "v0.3-prelim" / "data" / "results"
    for name in PRODUCTION_RESULTS:
        p = res_dir / name
        assert p.exists(), f"v40.63: production artifact missing: {name}"
        data = json.loads(p.read_text(encoding="utf-8"))
        assert data, f"v40.63: production artifact is empty: {name}"


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
    print("\nAll v40.63 n16.docx review response regression tests pass.")
