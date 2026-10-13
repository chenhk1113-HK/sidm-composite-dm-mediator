"""
test_solver_benchmarks.py — Orchestrator (REVIEWER-15 item 8: file split).

Split into:
  - test_born.py
  - test_calogero.py
  - test_hulthen.py
  - test_misc.py
This file just imports and runs all of them.

Run:  python test_solver_benchmarks.py
"""
from __future__ import annotations
import sys
import os

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

    failed = []
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"FAIL: {test.__name__}: {e}")
            failed.append(test.__name__)

    print()
    if failed:
        print(f"FAILED: {len(failed)} test(s) failed: {failed}")
        sys.exit(1)
    else:
        print("ALL BENCHMARKS PASSED (orchestrator)")
        sys.exit(0)
