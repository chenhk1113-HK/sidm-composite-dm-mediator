#!/usr/bin/env python3
"""
run_round12_self_check.sh — Round 12 self-check combining all consistency passes.

Runs in sequence:
1. audit_claims.py --table-only  (24 standing numbers)
2. audit_claims.py               (7 regex checks)
3. verify_numbers_in_paper.py     (36 required + 7 forbidden checks)
4. walk_paper_tables.py           (36 tables checked)
5. pytest test_paper_claims.py    (12 tests)

If all pass, exit 0. Otherwise print which check failed.
"""
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).parent.parent
PYTHON = REPO / ".venv-sidm-bench" / "Scripts" / "python.exe"


def run(name, args, timeout=60):
    """Run a check; return (success, output)."""
    print()
    print("=" * 70)
    print(f"  {name}")
    print("=" * 70)
    try:
        r = subprocess.run([str(PYTHON)] + args, cwd=str(REPO),
                           capture_output=True, text=True, timeout=timeout)
        output = r.stdout + r.stderr
        success = r.returncode == 0
        # Show last 5 lines of output
        lines = output.strip().split('\n')
        for line in lines[-5:]:
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
    success, _ = run("CHECK 1/5: Standing-numbers table audit (24 entries)",
                     ["scripts/audit_claims.py", "--table-only"])
    results.append(("Standing-numbers table audit", success))

    # Check 2: audit_claims.py (regex mode)
    success, _ = run("CHECK 2/5: Paper-claims regex audit (7 entries)",
                     ["scripts/audit_claims.py"])
    results.append(("Paper-claims regex audit", success))

    # Check 3: verify_numbers_in_paper.py
    success, _ = run("CHECK 3/5: Cross-validation (36 required + 7 forbidden)",
                     ["scripts/verify_numbers_in_paper.py"])
    results.append(("Cross-validation", success))

    # Check 4: walk_paper_tables.py
    success, _ = run("CHECK 4/5: Table-walker (36 tables)",
                     ["scripts/walk_paper_tables.py"])
    results.append(("Table-walker", success))

    # Check 5: pytest
    success, _ = run("CHECK 5/5: pytest test_paper_claims.py (12 tests)",
                     ["-m", "pytest", "v0.3-prelim/tests/test_paper_claims.py", "-v", "--tb=short"],
                     timeout=120)
    results.append(("pytest test_paper_claims.py", success))

    # Summary
    print()
    print("=" * 70)
    print("  ROUND 12 SELF-CHECK SUMMARY")
    print("=" * 70)
    all_pass = True
    for name, success in results:
        marker = "✓ PASS" if success else "✗ FAIL"
        print(f"  {marker}  {name}")
        if not success:
            all_pass = False

    print()
    if all_pass:
        print("  ✓ ALL CHECKS PASSED — paper is consistent and verified")
        return 0
    else:
        print("  ✗ ONE OR MORE CHECKS FAILED — review output above")
        return 1


if __name__ == "__main__":
    sys.exit(main())