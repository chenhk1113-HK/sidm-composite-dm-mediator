#!/usr/bin/env bash
# v0.5 T41 re-run master script (2026-08-26)
# - KSFR/PCAC validity mask enabled (hard pre-filter, Channel 15) — the v0.5 result
# - nlive=500, dlogz=0.10 (per H3 finding: nlive=500 gives cleaner convergence than nlive=200)
# - also re-runs the historical (mask-disabled) T41 for cross-comparison, writing to a different filename
set -uo pipefail

WSL_REPO=/home/lamkuenai/sidm-composite-dm-mediator
WSL_RESULTS=$WSL_REPO/v0.3-prelim/data/results
WIN_RESULTS=/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results
LOG=$WSL_RESULTS/v05_rerun.log
PYTHON=/home/lamkuenai/wimpy/bin/python

mkdir -p "$WSL_RESULTS"
echo "=== v0.5 T41 re-run started at $(date '+%Y-%m-%d %H:%M:%S') ===" >> "$LOG"
echo "  WSL_RESULTS=$WSL_RESULTS" >> "$LOG"
echo "  WIN_RESULTS=$WIN_RESULTS" >> "$LOG"
echo "" >> "$LOG"

cd $WSL_REPO/v0.3-prelim/code || exit 1

# --- 1. Historical T41 (mask disabled) — for cross-comparison ---
# Writes to t41_mediator_mass_joint_fit_v0_4_historical.json (mask disabled, nlive=200)
echo "=== Step 1: Historical T41 (KSFR mask DISABLED, nlive=200) ===" >> "$LOG"
stdbuf -oL -eL env \
    SIDM_DISABLE_KSFR_MASK=1 \
    T41_RESULT_SUFFIX="_v0_4_historical" \
    PYTHONUNBUFFERED=1 \
    "$PYTHON" t41_mediator_mass_joint_fit.py >> "$LOG" 2>&1
HIST_RC=$?
echo "Step 1 exit code: $HIST_RC" >> "$LOG"

# Per-step cp to Windows-side (Pitfall #36)
HIST_FILE="t41_mediator_mass_joint_fit_v0_4_historical.json"
if [ -f "$WSL_RESULTS/$HIST_FILE" ]; then
    cp "$WSL_RESULTS/$HIST_FILE" "$WIN_RESULTS/$HIST_FILE" 2>>"$LOG" \
        && echo "  Step 1 Win-side cp OK: $HIST_FILE" >> "$LOG" \
        || echo "  Step 1 Win-side cp FAILED" >> "$LOG"
fi

# --- 2. v0.5 T41 (mask enabled, KSFR-valid region only) ---
# Writes to t41_mediator_mass_joint_fit_v0_5.json (mask enabled, nlive=500)
echo "" >> "$LOG"
echo "=== Step 2: v0.5 T41 (KSFR mask ENABLED, nlive=500) ===" >> "$LOG"
stdbuf -oL -eL env \
    T41_RESULT_SUFFIX="_v0_5" \
    T41_NLIVE=500 \
    PYTHONUNBUFFERED=1 \
    "$PYTHON" t41_mediator_mass_joint_fit.py >> "$LOG" 2>&1
V05_RC=$?
echo "Step 2 exit code: $V05_RC" >> "$LOG"

# Per-step cp to Windows-side (Pitfall #36)
V05_FILE="t41_mediator_mass_joint_fit_v0_5.json"
if [ -f "$WSL_RESULTS/$V05_FILE" ]; then
    cp "$WSL_RESULTS/$V05_FILE" "$WIN_RESULTS/$V05_FILE" 2>>"$LOG" \
        && echo "  Step 2 Win-side cp OK: $V05_FILE" >> "$LOG" \
        || echo "  Step 2 Win-side cp FAILED" >> "$LOG"
fi

echo "" >> "$LOG"
echo "=== v0.5 T41 re-run finished at $(date '+%Y-%m-%d %H:%M:%S') ===" >> "$LOG"
echo "  HIST_RC=$HIST_RC V05_RC=$V05_RC" >> "$LOG"

# Copy log to Windows-side
cp "$LOG" "$WIN_RESULTS/v05_rerun.log" 2>/dev/null || true

# Show summary
echo ""
echo "=== SUMMARY ==="
echo "Historical T41 (mask disabled, nlive=200):"
grep -E "(log Z = |MAP:|DERIVED)" "$LOG" | head -10
echo ""
echo "v0.5 T41 (mask enabled, nlive=500):"
grep -E "(log Z = |MAP:|DERIVED)" "$LOG" | tail -10