#!/usr/bin/env bash
# T71.3 R7 — parallel (Nc, Nf) scan at nlive=2000
#
# Launches all 7 (Nc, Nf) combinations in parallel via background subprocess.
# Each combo gets:
#   - Distinct T41_RESULT_SUFFIX (_v0_6_nl2000_nc<N>_nf<M>)  → no file collision
#   - Per-combo tee log  (./_nl2000_logs/nc<N>_nf<M>.log)  → real-time visibility
#   - stdbuf -oL python  → unbuffered stdout (per AGENTS.md rule 3 + bayesian skill pitfall 1)
#   - T41_NLIVE=2000 + T41_DLOGZ=0.1 (matches T71.1 production baseline)
#   - KSFR_NC=<int> KSFR_NF=<int>  → so the KSFR/PCAC mask uses the right (Nc,Nf) ratio
#
# Concurrency: 7 dynesty subprocesses. Each is single-threaded; on a 8-core host
# this saturates. WSL2 memory ~7 GB peak. Logs are tee'd so per-combo failures
# are visible immediately, not just on exit.

set -u
set -o pipefail

REPO=/home/lamkuenai/sidm-composite-dm-mediator
VENV=/home/lamkuenai/wimpy/bin/python
LOGS=/home/lamkuenai/sidm-composite-dm-mediator/v0.3-prelim/data/results/_nl2000_logs
mkdir -p "$LOGS"

# 7 combos: (2,2) (2,3) (3,2) (3,3) (3,4) (4,3) (4,4)
COMBOS=(
  "2 2"
  "2 3"
  "3 2"
  "3 3"
  "3 4"
  "4 3"
  "4 4"
)

pids=()
for combo in "${COMBOS[@]}"; do
  read -r nc nf <<< "$combo"
  SUFFIX="_v0_6_nl2000_nc${nc}_nf${nf}"
  LOG="$LOGS/nc${nc}_nf${nf}.log"

  echo "[$(date +%H:%M:%S)] launching (Nc=$nc, Nf=$nf) → $LOG"

  (
    cd "$REPO"
    KSFR_NC="$nc" \
    KSFR_NF="$nf" \
    T41_NLIVE=2000 \
    T41_DLOGZ=0.1 \
    T41_RESULT_SUFFIX="$SUFFIX" \
    stdbuf -oL -eL "$VENV" \
      v0.3-prelim/code/t41_mediator_mass_joint_fit.py \
      2>&1 | tee "$LOG"
  ) &
  pids+=($!)
done

echo "[$(date +%H:%M:%S)] all 7 launched; PIDs: ${pids[*]}"

# Wait for all + surface exit codes (any failure aborts the wait early)
fail=0
for pid in "${pids[@]}"; do
  if wait "$pid"; then
    echo "[$(date +%H:%M:%S)] PID $pid OK"
  else
    rc=$?
    echo "[$(date +%H:%M:%S)] PID $pid FAILED exit=$rc"
    fail=1
  fi
done

echo "[$(date +%H:%M:%S)] all done; fail=$fail"
exit $fail
