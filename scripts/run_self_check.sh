#!/usr/bin/env bash
# run_self_check.sh — single command to verify all paper claims.
#
# Per checking plan (docs/CHECKING_PLAN_2026_09_17.md), this runs:
#   - Layer A+B: pytest on tests/test_paper_claims.py
#   - Layer F:   scripts/audit_claims.py
#
# Exits 0 on full pass, non-zero on any failure.
#
# Usage:
#   ./scripts/run_self_check.sh           # use the project's venv
#   ./scripts/run_self_check.sh --no-venv # use system python

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Pick python
PYTHON="python"
if [[ "${1:-}" != "--no-venv" ]] && [[ -d "$REPO_ROOT/.venv-sidm-bench" ]]; then
    PYTHON="$REPO_ROOT/.venv-sidm-bench/Scripts/python.exe"
fi

echo "============================================================"
echo "  SELF-CHECK: Multi-Resonance SIDM paper claims"
echo "  Python: $PYTHON"
echo "============================================================"
echo

# Layer A + B
echo ">>> Layer A + B: pytest test_paper_claims.py"
echo "------------------------------------------------------------"
cd "$REPO_ROOT"
"$PYTHON" -m pytest v0.3-prelim/tests/test_paper_claims.py -v --tb=short || {
    echo
    echo ">>> Paper-claims tests FAILED"
    exit 1
}

echo
echo ">>> Layer C + D + E: pytest test_physical_invariants.py"
echo "------------------------------------------------------------"
"$PYTHON" -m pytest v0.3-prelim/tests/test_physical_invariants.py -v --tb=short || {
    echo
    echo ">>> Physical-invariants tests FAILED"
    exit 1
}

echo
echo ">>> Layer D (extended): pytest test_physical_constraints.py"
echo "------------------------------------------------------------"
"$PYTHON" -m pytest v0.3-prelim/tests/test_physical_constraints.py -v --tb=short || {
    echo
    echo ">>> Physical-constraints tests FAILED"
    exit 1
}

echo
echo ">>> Layer D + E (independent + robustness): pytest test_independent_and_robustness.py"
echo "------------------------------------------------------------"
"$PYTHON" -m pytest v0.3-prelim/tests/test_independent_and_robustness.py -v --tb=short || {
    echo
    echo ">>> Independent + robustness tests FAILED"
    exit 1
}

echo
echo ">>> Layer F: audit_claims.py"
echo "------------------------------------------------------------"
"$PYTHON" scripts/audit_claims.py || {
    echo
    echo ">>> audit_claims.py FAILED"
    exit 2
}

echo
echo "============================================================"
echo "  ALL CHECKS PASSED"
echo "============================================================"
