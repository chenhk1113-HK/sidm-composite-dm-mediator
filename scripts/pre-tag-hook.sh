#!/usr/bin/env bash
# v19.2-F git pre-tag hook (MANDATORY).
# This hook is automatically run by `git tag`. It BLOCKS the tag if
# verify_release_gate.py reports any FAILED layer.
#
# Install (one-time):
#   cp scripts/pre-tag-hook.sh .git/hooks/pre-tag
#   chmod +x .git/hooks/pre-tag
#
# To BYPASS (NOT recommended; document the reason):
#   git tag --no-verify v19.2-F-Phase3-CLOSED-rXX.Y
set -e

REPO="$(git rev-parse --show-toplevel)"
PY="${REPO}/.venv-sidm-bench/Scripts/python.exe"
[ -f "$PY" ] || PY="$(command -v python)"

echo "[pre-tag] Running verify_release_gate.py..."
echo "[pre-tag] This gate is MANDATORY. Use --no-verify ONLY with explicit justification."

cd "$REPO"
"$PY" scripts/verify_release_gate.py
RC=$?

if [ $RC -ne 0 ]; then
    echo ""
    echo "[pre-tag] GATE FAILED (exit $RC). Tag BLOCKED."
    echo "[pre-tag] To bypass: git tag --no-verify <tagname>  (NOT recommended)"
    exit 1
fi

echo "[pre-tag] All gates passed. Tag may proceed."
exit 0
