"""Single source of truth for the pytest selection the release gate applies.

Added 2026-11-15 (finding F36). Before this module existed, the selection was written
inline in scripts/verify_release_gate.py, and the README badge guard
(v0.3-prelim/tests/test_t82_audit_readme_drift.py) re-implemented it separately with a
DIFFERENT recipe -- it hard-coded --ignore flags for two files the gate now runs (they
were repaired in the D9 round) and omitted the -k filter. Two scripts measuring "the
test suite" with different filters cannot detect drift in each other's numbers.

Both now import this one. The gate passes its own GATE_IGNORED_TESTS as the ignore
list; the guard passes none, because GATE_IGNORED_TESTS is empty and any future entry
must carry an in-file marker (that is enforced by the gate itself).

Keep this module stdlib-only: it is imported by a test that runs inside the gate.
"""
from __future__ import annotations

# The gate's own deselection filter. Deselection is NOT the same as a gate-ignored
# file: deselected tests are collected and then excluded by name pattern, and the gate
# discloses them (n25 finding III.4 extended skip-disclosure to deselect-disclosure).
GATE_PYTEST_TARGET = "v0.3-prelim/tests/"

GATE_PYTEST_K_FILTER = (
    "not T132 and not T131 and not T133 and not T134 and not T135 and not T220"
)


def gate_pytest_args(ignore_rel=()) -> list[str]:
    """Return the pytest arguments the release gate runs, in order.

    `ignore_rel` is the gate's GATE_IGNORED_TESTS keys (repo-relative paths). Callers
    that want the gate's exact census pass those keys; a caller that wants the plain
    gate census passes nothing.
    """
    return [
        GATE_PYTEST_TARGET,
        "-q",
        "--tb=line",
        *[f"--ignore={rel}" for rel in sorted(ignore_rel)],
        "-k",
        GATE_PYTEST_K_FILTER,
    ]
