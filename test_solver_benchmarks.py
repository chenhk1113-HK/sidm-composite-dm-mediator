"""
test_solver_benchmarks.py — Orchestrator (REVIEWER-15 item 8: file split).

Split into:
  - test_born.py
  - test_calogero.py
  - test_hulthen.py
  - test_misc.py

REVIEWER-16 item 13: distinguish AssertionError (test failure) from other
exceptions (code bug) to avoid silently swallowing real errors.

Run:  python test_solver_benchmarks.py
"""
from __future__ import annotations
import sys
import os
import traceback

_TEST_DIR = os.path.dirname(os.path.abspath(__file__))
if _TEST_DIR not in sys.path:
    sys.path.insert(0, _TEST_DIR)

from test_born import test_tulin_yu_fig2, test_born_high_v_limit, test_born_formula_tulin_yu_match
from test_calogero import test_calogero_sommerfeld_deviation
from test_hulthen import test_hulthen_framework_fails, test_hulthen_asymptotic
from test_misc import test_structural_sanity, test_hbarc_unit_consistency, test_lattice_convergence

if __name__ == "__main__":
    tests = [
        test_tulin_yu_fig2,
        test_born_high_v_limit,
        test_structural_sanity,
        test_hbarc_unit_consistency,
        test_lattice_convergence,
        test_hulthen_framework_fails,
        test_hulthen_asymptotic,
        test_born_formula_tulin_yu_match,
        test_calogero_sommerfeld_deviation,
    ]

    # REVIEWER-16 item 13: separate test failures from code bugs
    test_failures = []  # AssertionError: test logic failed
    code_bugs = []     # Other exceptions: code crashed unexpectedly

    for test in tests:
        try:
            test()
        except AssertionError as e:
            test_failures.append((test.__name__, str(e)))
        except Exception as e:
            code_bugs.append((test.__name__, type(e).__name__, str(e)))

    print()
    if test_failures:
        print(f"TEST FAILURES (assertions): {len(test_failures)}")
        for name, msg in test_failures:
            print(f"  ASSERT FAIL: {name}: {msg}")
    if code_bugs:
        print(f"CODE BUGS (unexpected exceptions): {len(code_bugs)}")
        for name, etype, msg in code_bugs:
            print(f"  EXCEPTION: {name}: {etype}: {msg}")
    if test_failures or code_bugs:
        sys.exit(1)
    else:
        print("ALL BENCHMARKS PASSED (orchestrator)")
        sys.exit(0)
