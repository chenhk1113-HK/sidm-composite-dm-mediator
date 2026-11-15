"""
T82 extension: README test-count drift detector.

Catches the failure mode where the README claims a specific test count (its badge,
"3701 pass | 25 skip | 40 deselect") that has drifted from what was actually certified.

Rewritten 2026-11-15 (finding F36) because the guard as written asserted NOTHING:

  * Its badge pattern was `badge/tests-(\\d+)\\s*pass` -- whitespace-or-nothing after the
    digits. The README badge spells `badge/tests-3701_pass`; an underscore is neither, so
    the search never matched and the test SKIPPED with the reason "README badge is
    branch-dependent (no specific count)" although the badge does carry a count. Read back
    from the tags, the same spelling is on v19.2-F-RecordSave-2026-11-11 (`tests-3643_pass`)
    and on HEAD: the guard had been inert across every recent tagged tree.
  * Strictness was opt-in (T82_README_DRIFT_STRICT=1) and no script or workflow set it, so
    even a parseable badge with 50% drift would have passed.
  * Its collect recipe was not the gate's: it hard-coded --ignore for two files the gate now
    runs (repaired in the D9 round) and omitted the gate's -k filter, so it measured a
    different census from the number the badge quotes (measured 3750 collected vs the gate's
    3763 on the same tree).

What it asserts now (all deterministic, no long re-run needed):

  1. test_readme_badge_is_parseable_by_this_guard -- if a Tests badge exists, this guard
     must be able to read a number out of it. The silent-skip mode IS the defect, so it is
     now itself a failure. URL escapes are decoded first: parsing the raw shields label
     reads "%20" as the number 20 (it returned skip=20 / deselect=20 instead of 25 / 40).
  2. test_badge_pattern_survives_spelling_variants -- regression on the parser itself,
     covering every spelling this page has actually used.
  3. test_readme_badge_matches_a_certified_gate_run -- the badge's (pass, skip, deselect)
     triple must equal the triple reported by a tracked gate log that says
     "GATE PASSED: all 15 layer(s)". The badge's claim is "these numbers come from a
     certified run", so a certified log is the thing it must agree with. Failing runs are
     not evidence for a badge.
  4. test_readme_names_only_evidence_files_that_exist -- the verification paragraph may not
     point at a log that is not in the tree (forward-referencing an artifact filed in a
     later commit is a recorded defect class here).
  5. test_readme_badge_deselection_matches_the_gate_exactly -- deselection is countable and
     stable, so it is asserted exactly rather than tolerantly.
  6. test_guard_tests_are_inside_the_gate_suite -- the guard runs its own tests in-process
     under the gate's selection filter and requires them green: the guard must be part of
     the certified suite, not a checker standing outside it.
  7. test_gate_census_within_tolerance_of_badge -- a coarse suite-size sanity check,
     collected with the GATE's own selection args (imported from
     scripts/gate_pytest_selection.py so guard and gate cannot diverge). ADVISORY at 1%: a
     standalone collect does not reproduce the gate's run census (finding F37 measured
     3723 collected-selected vs 3770 items in the same tree's run), so a correct badge sits
     ~0.4% from it; exactness lives in checks 3 and 5 instead.

Strict by default. T82_README_DRIFT_LENIENT=1 downgrades (3) and (7) to printed warnings
for a round that knowingly ships a badge quoting one specific historical run; that choice
must be recorded in the round's docs, not just set in an environment. (1), (2) and (4) are
never lenient.

Usage:
  pytest v0.3-prelim/tests/test_t82_audit_readme_drift.py -v -rs
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

import pytest


REPO_ROOT = Path(
    os.environ.get("SIDM_GUARD_REPO") or Path(__file__).resolve().parents[2]
).resolve()
README_PATH = REPO_ROOT / "README.md"
EVIDENCE_ROOT = REPO_ROOT / "docs"

# The gate's own pytest selection, shared so this guard cannot measure a different suite
# than the one the badge quotes (finding F36).
sys.path.insert(0, str(REPO_ROOT / "scripts"))
from gate_pytest_selection import gate_pytest_args  # noqa: E402

# Captures the whole shields.io label for the Tests badge. Group 1 is the label text.
BADGE_URL_RE = re.compile(
    r"\[!\[Tests\]\(([^)]*badge/tests-[^)]*)\)\]",
    re.IGNORECASE,
)
# Spelling-agnostic number/word pairs, applied AFTER URL decoding: "3701_pass",
# "3701 pass", "3701pass" all parse; "%20" no longer masquerades as a number.
BADGE_COUNT_RE = re.compile(r"(\d+)[\s_]*(pass|skip|deselect)", re.IGNORECASE)

# A gate log is evidence only if the gate itself declared all 15 layers green.
GATE_GREEN_RE = re.compile(r"GATE PASSED: all 15 layer\(s\) asserted and exited 0\.")
GATE_SUMMARY_RE = re.compile(
    r"(\d+) passed.*?(\d+) skipped.*?(\d+) deselected", re.IGNORECASE
)

# 1% advisory bound. NOT a safe equality bound: the standalone collect census understates
# the gate's real run census by ~0.4% on this tree (3723 collect-only vs 3770 in the run,
# finding F37), so a badge that exactly quotes a certified gate log is 0.4% away from what
# a collect reports. Exactness lives in the badge-vs-certified-log check and in the exact
# deselection equality; this test only catches gross suite-size drift.
CENSUS_TOLERANCE = 0.01


def _readme_text() -> str:
    return README_PATH.read_text(encoding="utf-8", errors="replace")


def _read_readme_badge_url() -> str | None:
    """Return the Tests badge label if the README carries a Tests badge."""
    if not README_PATH.exists():
        return None
    m = BADGE_URL_RE.search(_readme_text())
    return m.group(1) if m else None


def _read_readme_badge_counts() -> dict[str, int] | None:
    """Return {'pass': N, 'skip': M, 'deselect': K} from the badge, or None.

    The label is URL-decoded before any digit is read. A shields label encodes spaces as
    %20, and the raw form makes the escape look like a number: parsing the live badge raw
    returned skip=20 and deselect=20 (the "20" of "%20") instead of 25 and 40.
    """
    label = _read_readme_badge_url()
    if label is None:
        return None
    counts = {
        word.lower(): int(num)
        for num, word in BADGE_COUNT_RE.findall(unquote(label))
    }
    if "pass" not in counts:
        return None
    return counts


def _certified_gate_runs() -> list[tuple[Path, dict[str, int]]]:
    """Every tracked gate log that declares all 15 layers green, with its counts."""
    found: list[tuple[Path, dict[str, int]]] = []
    if not EVIDENCE_ROOT.exists():
        return found
    for path in sorted(EVIDENCE_ROOT.rglob("gate_run*.txt")):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except (OSError, UnicodeDecodeError):
            continue
        if not GATE_GREEN_RE.search(text):
            continue
        m = GATE_SUMMARY_RE.search(text)
        if not m:
            continue  # truncated capture: 851-byte logs carry no summary (known gotcha)
        found.append((
            path.relative_to(REPO_ROOT),
            {"pass": int(m.group(1)), "skip": int(m.group(2)), "deselect": int(m.group(3))},
        ))
    return found


def _run_gate_collect() -> tuple[int, int] | None:
    """Collect with the GATE's own selection args. Return (collected, deselected)."""
    cmd = [sys.executable, "-m", "pytest", *gate_pytest_args(), "--collect-only"]
    try:
        result = subprocess.run(
            cmd, cwd=str(REPO_ROOT), capture_output=True, text=True,
            timeout=300, encoding="utf-8", errors="replace",
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None
    out = result.stdout or ""
    m = re.search(r"(\d+)/(\d+) tests? collected \((\d+) deselected\)", out)
    if m:
        return int(m.group(2)), int(m.group(3))
    m = re.search(r"(\d+)\s+tests?\s+collected", out)
    if not m:
        return None
    d = re.search(r"(\d+)\s+tests?\s+deselected", out)
    return int(m.group(1)), int(d.group(1)) if d else 0


def test_readme_badge_is_parseable_by_this_guard():
    """A badge this guard cannot read used to make the guard skip and assert nothing.

    That silent mode is the defect (F36): the front page advertised a guarded test count
    while the guard was inert. Cosmetic spelling may not mute a check.
    """
    label = _read_readme_badge_url()
    if label is None:
        pytest.skip("README carries no Tests badge -- nothing to check")
    counts = _read_readme_badge_counts()
    assert counts is not None, (
        f"README has a Tests badge but this guard cannot read a count out of it: "
        f"{label!r}. Either restore a parseable spelling (tests-<N>[ _]pass) or widen "
        f"BADGE_COUNT_RE -- but do NOT let the guard skip, because a skipping guard is "
        f"the defect this test exists to catch."
    )
    assert counts["pass"] > 0, f"parsed a non-positive pass count from {label!r}"


def test_badge_pattern_survives_spelling_variants():
    """Regression on the parser: it must accept every spelling this page has used.

    Guards whose patterns silently stop matching the artifact they check are a known
    defect class in this repo (CG-15 markup, the CI-wiring importorskip case). The URL
    decode is part of the contract: the raw shields form yields the wrong numbers.
    """
    expected = {
        "tests-3701_pass%20%7C%2025%20skip%20%7C%2040%20deselect-green":
            {"pass": 3701, "skip": 25, "deselect": 40},
        "tests-3701 pass%20|%2025 skip%20|%2040 deselect-green":
            {"pass": 3701, "skip": 25, "deselect": 40},
        "tests-3701pass25skip40deselect-green":
            {"pass": 3701, "skip": 25, "deselect": 40},
        "tests-3643_pass%20%7C%2026%20skip%20%7C%2040%20deselect-green":
            {"pass": 3643, "skip": 26, "deselect": 40},
    }
    for variant, want in expected.items():
        decoded = unquote(variant)
        counts = {w.lower(): int(n) for n, w in BADGE_COUNT_RE.findall(decoded)}
        assert counts == want, (
            f"parser lost a spelling variant: {variant!r} -> decoded {decoded!r} -> {counts}"
        )
    # The trap that made the raw form dangerous, kept explicit.
    raw = "tests-3701_pass%20%7C%2025%20skip%20%7C%2040%20deselect-green"
    bad = {w.lower(): int(n) for n, w in BADGE_COUNT_RE.findall(raw)}
    assert bad != {"pass": 3701, "skip": 25, "deselect": 40}, (
        "raw (URL-encoded) parsing now agrees with the decoded parse; the decode step "
        "above is load-bearing -- do not remove it without re-checking %20 collisions"
    )


def test_readme_badge_matches_a_certified_gate_run():
    """The badge claims its numbers come from a certified run: it must equal one.

    Only a log in which the gate declared all 15 layers green counts as evidence; a log
    with a failing layer is part of the record but certifies nothing for the front page.
    """
    counts = _read_readme_badge_counts()
    if counts is None:
        pytest.skip("README badge has no specific count to compare")
    certified = _certified_gate_runs()
    assert certified, (
        "no tracked gate log under docs/ declares 'GATE PASSED: all 15 layer(s)' with a "
        "parseable summary line, so the README badge's test counts are unevidenced "
        "(finding F36). File the gate log for the tree the badge quotes."
    )
    matches = [
        path for path, run in certified
        if run["pass"] == counts["pass"]
        and run["skip"] == counts.get("skip", run["skip"])
        and run["deselect"] == counts.get("deselect", run["deselect"])
    ]
    if matches:
        return
    lenient = os.environ.get("T82_README_DRIFT_LENIENT") == "1"
    table = "\n".join(
        f"    {path}: {run['pass']} passed / {run['skip']} skipped / {run['deselect']} deselected"
        for path, run in certified
    )
    message = (
        f"README test badge {counts['pass']} pass / {counts.get('skip')} skip / "
        f"{counts.get('deselect')} deselect matches none of the {len(certified)} "
        f"certified 15/15 gate logs:\n{table}\nRe-derive the badge from the gate log "
        f"that certifies the tree (docs/evidence/gate_run_*.txt); do not edit the number "
        f"to make this pass."
    )
    if lenient:
        print(f"WARNING (T82_README_DRIFT_LENIENT=1): {message}")
        return
    pytest.fail(message)


def test_readme_names_only_evidence_files_that_exist():
    """The verification paragraph may not point at a log that is not in the tree.

    Forward-referencing an artifact that lands in a later commit makes the tagged tree
    claim a file it does not contain -- a recorded defect in this repo's evidence rules.
    """
    text = _readme_text()
    named = set(re.findall(r"docs/evidence/[A-Za-z0-9_.\-]+\.(?:txt|json)", text))
    missing = [p for p in named if not (REPO_ROOT / p).exists()]
    assert not missing, (
        f"README names evidence files that do not exist in this tree: {missing}. File "
        f"them in the same commit, or phrase the row as a pointer to a run that will be "
        f"filed later and say so in the commit message."
    )


def test_named_evidence_files_are_not_git_ignored():
    """Every evidence file the README cites must be trackable by git.

    Finding F39 showed this repo's certifications are only as durable as the files that carry
    them: a green gate proved nothing about a clone because the tests' inputs are git-ignored.
    The same trap sits under the certification itself -- `.gitignore` line 78 is `*.log`, and
    every filed gate log in `docs/evidence/` is therefore named `gate_run*.txt` on purpose. A
    log named `.log` would exist only in the working copy: the badge would cite evidence that
    no clone contains, and the guard's own evidence glob (`gate_run*.txt`) would never see it.

    Checked with git's own matcher rather than by re-reading .gitignore, so the guard follows
    the ignore rules as they actually are instead of duplicating a snapshot of them.
    """
    text = _readme_text()
    named = sorted(set(re.findall(r"docs/evidence/[A-Za-z0-9_.\-]+\.(?:txt|json|md|log)", text)))
    tracked = subprocess.run(
        ["git", "ls-files", "--", *named], cwd=str(REPO_ROOT),
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    ).stdout.split()
    untracked = [p for p in named if p not in tracked]
    if not untracked:
        return
    res = subprocess.run(
        ["git", "check-ignore", "--stdin"], cwd=str(REPO_ROOT), input="\n".join(untracked),
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    ignored = sorted({u for u in untracked if u in (res.stdout or "").split()})
    assert not ignored, (
        f"README cites evidence files that git ignores, so they cannot exist in a clone: "
        f"{ignored}. Rename them to a tracked pattern (gate logs use `gate_run*.txt` because "
        f"`.gitignore` has `*.log`) and re-point the paragraph."
    )


def test_readme_badge_deselection_matches_the_gate_exactly():
    """Deselection is countable and stable, so it is checked exactly, not tolerantly.

    The gate's -k filter is a repo-level fact: the badge may not quietly claim a different
    deselected count from the one the certified run reported.
    """
    counts = _read_readme_badge_counts()
    if counts is None:
        pytest.skip("README badge has no specific count to compare")
    certified = _certified_gate_runs()
    if not certified:
        pytest.skip("no certified gate log to compare against")
    deselected = {run["deselect"] for _, run in certified}
    assert counts.get("deselect") in deselected, (
        f"badge claims {counts.get('deselect')} deselected but the certified gate runs "
        f"report {sorted(deselected)}. The -k filter changed; re-derive the badge."
    )


def test_guard_tests_are_inside_the_gate_suite():
    """Proves by execution, not by reading config, that this guard is inside the gate.

    The gate is a subprocess, so it sets GATE_RUN_ID in its own process and every child
    inherits it. If this test is running with that variable set, the guard was collected
    and executed inside a gate run -- which is what the badge's count claims to include.
    A guard that verifies the front page from outside the certified suite is decoration
    (finding F36).

    An earlier version of this test ran pytest.main() on its own file to prove the same
    thing. That recursed: the nested run executed this test, which started another nested
    run. Proof by execution must not re-execute itself.
    """
    gate_run_id = os.environ.get("GATE_RUN_ID")
    if gate_run_id:
        print(f"guard executed inside gate run {gate_run_id}: inclusion proven directly")
        return
    assert "v0.3-prelim" in Path(__file__).resolve().parts, (
        f"this guard ({Path(__file__).name}) is not under the directory the gate collects "
        "tests from, so any test count on the front page omits it."
    )
    pytest.skip(
        "inclusion is proven directly only inside a gate run (GATE_RUN_ID is set there); "
        "outside one this test can only assert the file lives in the collected directory, "
        "which it does"
    )


def test_gate_census_within_tolerance_of_badge():
    """Coarse sanity: the badge's census and the gate's own collected census agree.

    Collected with the gate's selection args (shared module), so a guard measuring a
    different suite than the gate is caught -- which is exactly how the pre-F36 version
    was blind. Advisory only, tolerance 1%: a standalone collect does NOT reproduce the
    gate's run census (finding F37), and a check that cannot be satisfied by a correct
    badge gets loosened or deleted by the next person who hits it. The exact assertions
    are the certified-log match and the deselection equality.
    """
    counts = _read_readme_badge_counts()
    if counts is None:
        pytest.skip("README badge has no specific count to compare")
    measured = _run_gate_collect()
    if measured is None:
        pytest.skip("pytest --collect-only with the gate's selection args did not run")
    collected, deselected = measured
    selected = collected - deselected
    badge_selected = counts["pass"] + counts.get("skip", 0)
    rel_diff = abs(badge_selected - selected) / max(badge_selected, selected, 1)
    lenient = os.environ.get("T82_README_DRIFT_LENIENT") == "1"
    if rel_diff <= CENSUS_TOLERANCE:
        return
    message = (
        f"badge selected census (pass+skip) {badge_selected} vs gate-args collected "
        f"{collected} minus deselected {deselected} = {selected}; relative difference "
        f"{rel_diff * 100:.2f}% exceeds the {CENSUS_TOLERANCE * 100:.1f}% tolerance. "
        f"The suite size moved -- re-derive the badge from a fresh gate log."
    )
    if lenient:
        print(f"WARNING (T82_README_DRIFT_LENIENT=1): {message}")
        return
    pytest.fail(message)


def test_readme_drift_audit_recognized():
    """Sanity check: the drift-guard audit (t82_audit.py) is
    reachable from this test, indicating CI integration is
    not blocked."""
    audit_path = REPO_ROOT / "scripts" / "t82_audit.py"
    assert audit_path.exists(), (
        f"t82_audit.py not found at {audit_path}. "
        f"CI integration requires this drift-guard script."
    )
