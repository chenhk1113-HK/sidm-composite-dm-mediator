#!/bin/bash
# Smoke test: verify the H3/H4 environment before launching the master.
set -uo pipefail
export PYTHONPATH="/home/lamkuenai/sidm-composite-dm-mediator:/home/lamkuenai/sidm-composite-dm-mediator/v0.1-prelim/code:/home/lamkuenai/sidm-composite-dm-mediator/v0.3-prelim/code"
export PY="/home/lamkuenai/wimpy/bin/python"
export SIDM_DISABLE_KSFR_MASK=1

LOG=/tmp/h3_h4_smoke.log
echo "=== H3/H4 smoke test started at $(date) ===" > "$LOG"

echo "1. Import t41 + call loglike_joint on in-box point" >> "$LOG"
$PY -c "
import sys, numpy as np
sys.path.insert(0, '/home/lamkuenai/sidm-composite-dm-mediator/v0.3-prelim/code')
import t41_mediator_mass_joint_fit as t41
theta = (np.log10(1000.0), np.log10(1.0), 1.0, -35.0, -10.0)
ll = t41.loglike_joint(theta)
print(f'll = {ll}')
" >> "$LOG" 2>&1
echo "   exit=$?" >> "$LOG"

echo "" >> "$LOG"
echo "2. Verify all H3/H4 scripts compile" >> "$LOG"
for f in h3_convergence_runner.py h4_xi_sweep.py h4_form_factor_sweep.py h4_inelastic_sweep.py; do
  $PY -m py_compile /home/lamkuenai/sidm-composite-dm-mediator/v0.3-prelim/code/$f >> "$LOG" 2>&1
  echo "   $f: py_compile exit=$?" >> "$LOG"
done

echo "" >> "$LOG"
echo "=== smoke test finished at $(date) ===" >> "$LOG"