#!/bin/bash
# H3 + H4 master runner.
#
# Invoked as: wsl -- bash /home/lamkuenai/h3_h4_master.sh
# (NOT plain `bash` — see Mnemosyne 1fbe8b45... for the MSYS trap.
# Plain bash interprets /home/<user>/ as MSYS path and exits 127 in <1 sec.)
#
# v2 (2026-08-26) fixes vs v1:
#   - Fixed cp source path: data/results/ -> v0.3-prelim/data/results/
#     (v1 silently missed all the result JSONs)
#   - Per-step cp: results appear on Windows-side incrementally so the
#     operator can poll progress even before the run finishes
#   - Unbuffered stdout via `stdbuf -oL -eL`: tee flushes line-by-line
#     instead of waiting for python's block buffer to fill (~8 KB).
#     Previously python's print() output was invisible for minutes at
#     a time during dynesty's long runs.
set -uo pipefail
cd /home/lamkuenai/sidm-composite-dm-mediator

# Ensure results dirs exist (defensive — T30 SPARC test failures occur
# when this dir is missing on a fresh WSL clone)
mkdir -p /home/lamkuenai/sidm-composite-dm-mediator/data/results \
         /home/lamkuenai/sidm-composite-dm-mediator/v0.3-prelim/data/results \
         2>/dev/null

export PYTHONPATH="/home/lamkuenai/sidm-composite-dm-mediator:/home/lamkuenai/sidm-composite-dm-mediator/v0.1-prelim/code:/home/lamkuenai/sidm-composite-dm-mediator/v0.3-prelim/code"
export PY="/home/lamkuenai/wimpy/bin/python"
export PYTHONUNBUFFERED=1  # belt-and-suspenders for python line-buffering
# SIDM_DISABLE_KSFR_MASK=1 keeps cross-version comparability with the
# historical T41 posterior (generated before the KSFR mask existed).
# Remove or set to 0 to test the v0.5 finding's downstream impact.
export SIDM_DISABLE_KSFR_MASK=${SIDM_DISABLE_KSFR_MASK:-1}

LOG=/home/lamkuenai/sidm-composite-dm-mediator/data/results/h3_h4_master.log
echo "=== H3 + H4 master runner v2 started at $(date) (PID=$$) ===" > "$LOG"

# Canonical results dir on WSL (where t41.RESULTS_DIR writes).
# Path constant duplicated here so the cp step never goes stale if
# someone edits the path in t41_mediator_mass_joint_fit.py.
WSL_RESULTS=/home/lamkuenai/sidm-composite-dm-mediator/v0.3-prelim/data/results
WIN_RESULTS=/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results

run_step() {
    local label="$1"
    shift
    echo "" >> "$LOG"
    echo "=== $label ===" >> "$LOG"
    # stdbuf forces line-buffered stdout/stderr so tee flushes per-line
    # rather than after the python stdout buffer fills (8 KB).
    # Critical for visibility during dynesty's long silent stretches.
    stdbuf -oL -eL "$@" 2>&1 | tee -a "$LOG"
    local rc=${PIPESTATUS[0]}
    echo "$label exit code: $rc" >> "$LOG"

    # Per-step Windows-side sync: results show up incrementally and
    # survive a partial run. If the runner is killed mid-sweep, you
    # still have everything before that step.
    if [ -d "$WIN_RESULTS" ]; then
        cp "$WSL_RESULTS"/h3_convergence_*.json "$WIN_RESULTS/" 2>>"$LOG" || true
        cp "$WSL_RESULTS"/h4_*.json "$WIN_RESULTS/" 2>>"$LOG" || true
    fi
    return $rc
}

RC_H3=0
RC_H41=0
RC_H42=0
RC_H43=0

run_step "H3 convergence (nlive=200,500,1000)" "$PY" v0.3-prelim/code/h3_convergence_runner.py || RC_H3=$?
run_step "H4.1 xi sweep" "$PY" v0.3-prelim/code/h4_xi_sweep.py || RC_H41=$?
run_step "H4.2 form-factor sweep" "$PY" v0.3-prelim/code/h4_form_factor_sweep.py || RC_H42=$?
run_step "H4.3 inelastic on/off" "$PY" v0.3-prelim/code/h4_inelastic_sweep.py || RC_H43=$?

echo "" >> "$LOG"
echo "=== H3 + H4 master runner finished at $(date) ===" >> "$LOG"
echo "EXIT_H3=$RC_H3 H41=$RC_H41 H42=$RC_H42 H43=$RC_H43" >> "$LOG"
echo "EXIT_AGGREGATE=$((RC_H3 + RC_H41 + RC_H42 + RC_H43))" >> "$LOG"

# Final sync (per-step copies above already copied the JSONs; this is
# the master log itself which we exclude from git via *.log but want
# preserved on Windows for debugging).
cp "$LOG" "$WIN_RESULTS/" 2>>"$LOG" || true

# Mark done (for external pollers)
touch /tmp/h3_h4_done
exit 0