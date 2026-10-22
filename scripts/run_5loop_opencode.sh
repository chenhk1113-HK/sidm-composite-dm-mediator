#!/usr/bin/env bash
# Run all 5 dual-review loops' OpenCode (reviewer 2) side in parallel.
# Each opencode run gets its own prompt file and its own output file.
# Run from the PROJECT ROOT so the reviewer can read the project files.
set -u
cd /c/Users/lamkuenai/projects/sidm-composite-dm-mediator || exit 1
mkdir -p docs/dual_review_5loop

declare -A JOBS
JOBS[1]="review_prompt_loop1_vmax_stale"
JOBS[2]="review_prompt_loop2_tcore_two_values"
JOBS[3]="review_prompt_loop3_yang_prefactor"
JOBS[4]="review_prompt_loop4_nfw_selfconsistency"
JOBS[5]="review_prompt_loop5_sigma_window_channels"

for i in 1 2 3 4 5; do
  name="${JOBS[$i]}"
  (
    C:/Python314/python.exe scripts/dual_review.py \
      --prompt-file "scripts/${name}.txt" \
      --out "docs/dual_review_5loop/OPENCODE_LOOP${i}_${name}.md" \
      --timeout 600 \
      > "docs/dual_review_5loop/loop${i}_opencode.log" 2>&1
    echo "EXIT=$? loop${i}" >> "docs/dual_review_5loop/loop${i}_opencode.log"
  ) &
done
wait
echo "=== ALL OPENCODE LOOPS DONE ==="
ls -la docs/dual_review_5loop/
