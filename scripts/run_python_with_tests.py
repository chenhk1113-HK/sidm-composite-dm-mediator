#!/usr/bin/env python3
"""
run_python_with_tests.py — Hermes-compatible tool for v19.2-F.

Executes production physics code + tests in a subprocess, returning
structured PASS/FAIL. Enforces: imports from constants.py, no forbidden
constructs, pytest-style tests in same turn.

This is the v19.2-F adaptation of the proposal in
`docs/V19_2_F_SELF_VERIFICATION_PROPOSAL_2026_10_19.md`,
Item A.1 (Tier 1 implementation).

Usage as a function:
    from run_python_with_tests import run_python_with_tests
    result = run_python_with_tests(production_code, test_code)

Usage as a CLI:
    python scripts/run_python_with_tests.py
    (uses embedded self-test)

Exit: 0 = PASS, 1 = FAIL, 2 = ERROR
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

# v19.2-F project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Use the project's pytest-enabled venv (same as run_round13_self_check.py)
VENV_PYTHON = PROJECT_ROOT / ".venv-sidm-bench" / "Scripts" / "python.exe"
if not VENV_PYTHON.exists():
    import shutil
    _sys = shutil.which("python") or shutil.which("python3") or sys.executable
    VENV_PYTHON = Path(_sys)

# Forbidden in agent-generated code (security + reproducibility)
FORBIDDEN = [
    "os.system",
    "eval(",
    "exec(",
    "__import__",
    "rm -rf /",
    "rm -rf ~",
    ":(){:|:&};:",  # fork bomb
]


def _safety_check(production_code: str, test_code: str):
    """Check for forbidden constructs. Returns error dict or None."""
    for forbidden in FORBIDDEN:
        if forbidden in production_code or forbidden in test_code:
            return {
                "status": "ERROR",
                "message": f"Forbidden construct detected: {forbidden}",
                "stdout": "",
                "stderr": "",
                "failed_tests": [],
                "key_metrics": {},
            }
    return None


def _build_test_files(tmp, production_code, test_code, extra_imports):
    """Write production module + test file to temp directory.

    Uses explicit string assembly (not textwrap.dedent) to preserve
    user-supplied indentation in production_code / test_code.
    """
    prod_content = (
        "import sys\n"
        f"sys.path.insert(0, r'{PROJECT_ROOT}')\n"
        f"{extra_imports}\n"
        f"{production_code}\n"
    )
    (tmp / "physics_module.py").write_text(prod_content, encoding="utf-8")

    test_content = (
        "import sys\n"
        f"sys.path.insert(0, r'{PROJECT_ROOT}')\n"
        f"sys.path.insert(0, r'{tmp}')\n"
        "import pytest\n"
        "from physics_module import *\n"
        f"{test_code}\n"
    )
    (tmp / "test_physics.py").write_text(test_content, encoding="utf-8")


def _parse_failed_tests(stdout):
    """Extract FAILED test names from pytest output."""
    return [l.strip() for l in stdout.splitlines() if "FAILED" in l]


def run_python_with_tests(
    production_code,
    test_code,
    extra_imports="",
    timeout=120,
    enforce_constants_import=False,
):
    """
    Execute production physics code with its tests.

    Args:
        production_code: Physics module body. Should import from constants.py.
        test_code: Pytest-style test functions.
        extra_imports: Optional additional imports.
        timeout: Seconds before kill.
        enforce_constants_import: If True, hard-fail if production_code doesn't
            import from constants.py. Default False.

    Returns:
        Dict with keys: status, stdout, stderr, failed_tests, key_metrics, message.
        status: "PASS" | "FAIL" | "ERROR"
    """
    err = _safety_check(production_code, test_code)
    if err:
        return err

    if enforce_constants_import:
        if "from constants import" not in production_code and "import constants" not in production_code:
            return {
                "status": "ERROR",
                "message": "production_code must import from constants.py",
                "stdout": "",
                "stderr": "",
                "failed_tests": [],
                "key_metrics": {},
            }

    with tempfile.TemporaryDirectory() as tmp_str:
        tmp = Path(tmp_str)
        _build_test_files(tmp, production_code, test_code, extra_imports)

        try:
            result = subprocess.run(
                [str(VENV_PYTHON), "-m", "pytest",
                 str(tmp / "test_physics.py"),
                 "-v", "--tb=short", "-q"],
                capture_output=True, text=True, timeout=timeout, cwd=str(tmp)
            )
        except subprocess.TimeoutExpired:
            return {
                "status": "ERROR",
                "message": f"Timeout after {timeout}s",
                "stdout": "",
                "stderr": "",
                "failed_tests": [],
                "key_metrics": {},
            }

        status = "PASS" if result.returncode == 0 else "FAIL"
        failed = _parse_failed_tests(result.stdout)
        msg = "All tests passed." if status == "PASS" else f"{len(failed)} test(s) failed."

        return {
            "status": status,
            "stdout": result.stdout[-2000:],
            "stderr": result.stderr[-1000:],
            "failed_tests": failed,
            "key_metrics": {},
            "message": msg,
        }


def _self_test():
    """Run the 3 self-tests documented in the proposal."""
    print("=" * 70)
    print("run_python_with_tests - SELF-TEST")
    print("=" * 70)
    failures = []

    print("\n[1/3] Pass case (add(2,3)==5):")
    r = run_python_with_tests(
        production_code="def add(a,b): return a+b",
        test_code="def test_add(): assert add(2,3)==5",
    )
    print(f"  status: {r['status']}  (expected: PASS)")
    if r["status"] != "PASS":
        failures.append(("pass_case", r))

    print("\n[2/3] Fail case (add returns a-b, but test expects a+b):")
    r = run_python_with_tests(
        production_code="def add(a,b): return a-b",
        test_code="def test_add(): assert add(2,3)==5",
    )
    print(f"  status: {r['status']}  (expected: FAIL)")
    if r["status"] != "FAIL":
        failures.append(("fail_case", r))

    print("\n[3/3] Block dangerous code (os.system):")
    r = run_python_with_tests(
        production_code="os.system('echo hi')",
        test_code="def test_dummy(): pass",
    )
    print(f"  status: {r['status']}  (expected: ERROR)")
    if r["status"] != "ERROR":
        failures.append(("dangerous_case", r))

    print()
    if failures:
        print(f"FAIL: {len(failures)} self-test(s) failed:")
        for name, r in failures:
            print(f"  {name}: {r.get('message', r)}")
        return 1
    print("All 3 self-tests passed.")
    return 0


if __name__ == "__main__":
    sys.exit(_self_test())
