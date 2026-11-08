#!/usr/bin/env python3
"""
run_round13_self_check.py — Round 13 self-check combining all consistency passes.

Runs in sequence:
1. audit_claims.py --table-only       (24 standing numbers)
2. audit_claims.py                    (7 regex checks)
3. verify_numbers_in_paper.py          (36 required + 7 forbidden)
4. walk_paper_tables.py                (36 tables)
5. audit_section_refs.py               (§-symbol cross-refs)
6. audit_citation_provenance.py        (citation [N] resolution)
7. audit_units.py                      (unit consistency)
8. pytest test_paper_claims.py         (12 tests)

If all pass, exit 0. Otherwise print which check failed.
"""
import os
import subprocess
import sys
from pathlib import Path

# This host's default locale codec is cp1252, which cannot encode the U+2713 /
# U+2717 check marks this script prints in its summary. Without this, the run
# dies with UnicodeEncodeError AFTER every check has already completed, so the
# script reports a crash instead of its verdict. Reconfigure to utf-8 with a
# replace fallback, and export PYTHONUTF8 so every child process inherits
# UTF-8 mode (that is what fixes the child's own file reads).
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
os.environ.setdefault("PYTHONUTF8", "1")

REPO = Path(__file__).parent.parent
PYTHON = REPO / ".venv-sidm-bench" / "Scripts" / "python.exe"


def run(name, args, timeout=60):
    """Run a check; return (success, output)."""
    print()
    print("=" * 70)
    print(f"  {name}")
    print("=" * 70)
    try:
        # encoding= is REQUIRED: text=True alone decodes with the LOCALE
        # codec (cp1252 on this host), and a decode error makes r.stdout None,
        # so `r.stdout + r.stderr` raises TypeError. errors="replace" degrades
        # instead of crashing.
        # PYTHONUTF8=1 makes the CHILD run in UTF-8 mode, so the child's own
        # bare open() calls read the paper as utf-8 instead of the locale
        # codec. PYTHONIOENCODING covers the child's stdout.
        _child_env = {**os.environ,
                      "PYTHONIOENCODING": "utf-8",
                      "PYTHONUTF8": "1"}
        r = subprocess.run([str(PYTHON)] + args, cwd=str(REPO), env=_child_env,
                           capture_output=True, text=True, timeout=timeout,
                           encoding="utf-8", errors="replace")
        output = (r.stdout or "") + (r.stderr or "")
        success = r.returncode == 0
        # Show last 8 lines of output
        lines = output.strip().split('\n')
        for line in lines[-8:]:
            print(line)
        if not success:
            print(f"FAILED (exit code {r.returncode})")
        return success, output
    except subprocess.TimeoutExpired:
        print(f"TIMEOUT after {timeout}s")
        return False, ""
    except FileNotFoundError as e:
        print(f"Python not found: {e}")
        return False, ""


def main():
    results = []

    # Check 1: audit_claims.py --table-only
    success, _ = run("CHECK 1/8: Standing-numbers table audit",
                     ["scripts/audit_claims.py", "--table-only"])
    results.append(("Standing-numbers table audit", success))

    # Check 2: audit_claims.py (regex mode)
    success, _ = run("CHECK 2/8: Paper-claims regex audit",
                     ["scripts/audit_claims.py"])
    results.append(("Paper-claims regex audit", success))

    # Check 3: verify_numbers_in_paper.py
    success, _ = run("CHECK 3/8: Cross-validation (numbers + forbidden)",
                     ["scripts/verify_numbers_in_paper.py"])
    results.append(("Cross-validation", success))

    # Check 4: walk_paper_tables.py
    success, _ = run("CHECK 4/8: Table-walker",
                     ["scripts/walk_paper_tables.py"])
    results.append(("Table-walker", success))

    # Check 5: audit_section_refs.py
    success, _ = run("CHECK 5/8: §-symbol cross-reference audit",
                     ["scripts/audit_section_refs.py"])
    results.append(("§-symbol cross-references", success))

    # Check 6: audit_citation_provenance.py
    success, _ = run("CHECK 6/8: Citation provenance audit",
                     ["scripts/audit_citation_provenance.py"])
    results.append(("Citation provenance", success))

    # Check 7: audit_units.py
    success, _ = run("CHECK 7/8: Unit consistency audit",
                     ["scripts/audit_units.py"])
    results.append(("Unit consistency", success))

    # Check 8: pytest
    success, _ = run("CHECK 8/8: pytest test_paper_claims.py",
                     ["-m", "pytest", "v0.3-prelim/tests/test_paper_claims.py",
                      "-v", "--tb=short"],
                     timeout=120)
    results.append(("pytest test_paper_claims.py", success))

    # Summary
    print()
    print("=" * 70)
    print("  ROUND 13 SELF-CHECK SUMMARY")
    print("=" * 70)
    all_pass = True
    for name, success in results:
        marker = "✓ PASS" if success else "✗ FAIL"
        print(f"  {marker}  {name}")
        if not success:
            all_pass = False

    print()
    if all_pass:
        print("  ✓ ALL CHECKS PASSED — paper is robust across 8 consistency layers")
        return 0
    else:
        print("  ✗ ONE OR MORE CHECKS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())