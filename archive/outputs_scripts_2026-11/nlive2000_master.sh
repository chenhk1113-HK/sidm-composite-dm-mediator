#!/bin/bash
# T41 v0.5.1 — nlive=2000 convergence validation (per R14 recommendation 1)
# Launched from Windows-side, runs in WSL, mirrors to Windows on completion.

set -uo pipefail
export PYTHONUNBUFFERED=1
export T41_NLIVE=2000
export T41_RESULT_SUFFIX=_v0_5_1_nlive2000

WSL_PROJECT=/home/lamkuenai/sidm-composite-dm-mediator
RESULTS_DIR_WIN="/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results"
PYTHON=/home/lamkuenai/wimpy/bin/python

cd "$WSL_PROJECT"

echo "=== T41 nlive=2000 run start: $(date) ==="
echo "ENV: T41_NLIVE=$T41_NLIVE T41_RESULT_SUFFIX=$T41_RESULT_SUFFIX"
echo "Python: $PYTHON"

# Launch dynesty run with line-buffered stdout
stdbuf -oL "$PYTHON" v0.3-prelim/code/t41_mediator_mass_joint_fit.py 2>&1

EXIT_CODE=$?
echo "=== T41 nlive=2000 run end: $(date), exit=$EXIT_CODE ==="

# Mirror the result file back to Windows-side (avoid 9P staleness)
if [ -f "$WSL_PROJECT/v0.3-prelim/data/results/t41_mediator_mass_joint_fit${T41_RESULT_SUFFIX}.json" ]; then
    cp "$WSL_PROJECT/v0.3-prelim/data/results/t41_mediator_mass_joint_fit${T41_RESULT_SUFFIX}.json" \
       "$RESULTS_DIR_WIN/t41_mediator_mass_joint_fit${T41_RESULT_SUFFIX}.json" 2>/dev/null || true
    echo "=== Mirrored result to Windows: t41_mediator_mass_joint_fit${T41_RESULT_SUFFIX}.json ==="
fi

exit $EXIT_CODE
