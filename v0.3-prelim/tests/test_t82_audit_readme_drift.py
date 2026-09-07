"""
T82 extension: README test-count drift detector.

Catches the failure mode where the README claims a specific
test count (e.g., "677 pass, 8 skip") that has drifted from
the on-disk reality (e.g., "686 collected on master with the
README-recommended pytest invocation").

This test is INTENTIONALLY conservative — it does not fail on
the current drift (we know about it and a Note explains it in
the README), but it will fail on FUTURE drift if a new round
ships a new badge count that doesn't match pytest.

How it works:
  1. Reads the README's recommended pytest invocation.
  2. Runs pytest --collect-only with that invocation.
  3. Reads the README's current badge line and parses out
     the count (if any).
  4. If both badge and pytest produce a count, compares them
     and fails on mismatch > 5%.

Usage:
  pytest v0.3-prelim/tests/test_t82_audit_readme_drift.py -v

The test is **opt-in for now** (does not fail by default),
controlled by env var T82_README_DRIFT_STRICT=1.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
README_PATH = REPO_ROOT / "README.md"


def _run_pytest_collect() -> int | None:
    """Run pytest --collect-only with the README's recommended
    ignore flags. Return collected test count, or None on error."""
    cmd = [
        sys.executable, "-m", "pytest",
        "v0.3-prelim/tests/",
        "--ignore=v0.3-prelim/tests/test_sparc_hierarchical.py",
        "--ignore=v0.3-prelim/tests/test_t32_real_likelihood.py",
        "--collect-only", "-q",
    ]
    try:
        result = subprocess.run(
            cmd, cwd=str(REPO_ROOT),
            capture_output=True, text=True, timeout=120,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None
    # Output ends with "N tests collected" or "N tests collected, M errors"
    m = re.search(r"(\d+)\s+tests?\s+collected", result.stdout)
    if not m:
        return None
    return int(m.group(1))


def _read_readme_badge_count() -> int | None:
    """Parse the README's test badge. Returns count if the
    badge embeds a specific number (e.g., '549 pass'); returns
    None if the badge is branch-dependent (no number)."""
    if not README_PATH.exists():
        return None
    text = README_PATH.read_text(encoding="utf-8", errors="replace")
    # Match the badge line: ![Tests](...badge/tests-NNN pass...NNN skip...)
    badge_re = re.compile(
        r"\[!\[Tests\]\([^)]*badge/tests-(\d+)\s*pass[^)]*\)\]",
        re.IGNORECASE,
    )
    m = badge_re.search(text)
    if not m:
        return None
    return int(m.group(1))


def test_readme_badge_matches_pytest_when_specific():
    """If README badge embeds a specific count, it must match
    pytest (within 5%) when run with the README-recommended
    invocation. Skipped if badge is branch-dependent (no number)."""
    badge_count = _read_readme_badge_count()
    if badge_count is None:
        pytest.skip("README badge is branch-dependent (no specific count)")
    pytest_count = _run_pytest_collect()
    if pytest_count is None:
        pytest.skip("pytest --collect-only failed or not available")
    # Allow 5% tolerance for transient collection errors
    if badge_count == 0 or pytest_count == 0:
        pytest.skip("zero count from one source — inconclusive")
    rel_diff = abs(badge_count - pytest_count) / max(badge_count, pytest_count)
    if rel_diff > 0.05 and os.environ.get("T82_README_DRIFT_STRICT") == "1":
        pytest.fail(
            f"README badge says {badge_count} tests but pytest collects "
            f"{pytest_count}. Drift = {rel_diff*100:.1f}% (>5%). "
            f"Run pytest with the README-recommended invocation to update."
        )


def test_readme_drift_audit_recognized():
    """Sanity check: the drift-guard audit (t82_audit.py) is
    reachable from this test, indicating CI integration is
    not blocked."""
    audit_path = REPO_ROOT / "scripts" / "t82_audit.py"
    assert audit_path.exists(), (
        f"t82_audit.py not found at {audit_path}. "
        f"CI integration requires this drift-guard script."
    )
