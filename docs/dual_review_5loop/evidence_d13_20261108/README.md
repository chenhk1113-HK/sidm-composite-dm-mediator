# Evidence — decision D13 (2026-11-08): which channel scorecard the paper shows

One commit: `ba2452c` (decision recorded in three front/record documents; no paper,
code, fit or PDF change). The owner chose **option (a)**: keep the published-test
scorecard in the paper and leave the adopted-arm tally repo-internal.

| File | What it is |
|---|---|
| `gate_run_committed.txt` | Full 15-layer `scripts/verify_release_gate.py` log for the committed D13 tree `ba2452c` (`.txt`, not `.log` — `.gitignore` line 78 keeps `*.log` untracked). |

## What the gate log records

`GATE PASSED: all 15 layer(s) asserted and exited 0`, `GATE_RC=0`.

- pytest layer: **3642 passed / 25 skipped / 40 deselected** in 1407.54 s. The skips
  and deselects are disclosed by the gate itself (CG-10 / n25 III.4): a skipped or
  deselected assertion did not run in this build.
- `t82_audit.py`: **120/120 ALL CLEAR**, and it separately confirms the t82 count
  literal printed in `CURRENT.md`.
- `drift_guard.py`: no drift. The new D13 text did not desynchronise any doc from the
  canonical numbers.

## Standalone re-verification run before the commit

Run against the edited working tree: `drift_guard.py` no drift; `t82_audit.py` 120/120;
`audit_claims.py` PASS; `check_fabrication.py` OK; `audit_doc_anchors.py` PASS;
`audit_stale_strings.py` PASS; `audit_register_state.py` PASSED; `audit_units.py` clean.
Doc guards `test_markup_balance_cg4.py`, `test_integrity_finding_ids_unique.py`,
`test_version_tokens_have_tags.py`: 20 passed.

**The guard that fired, as designed:** `test_no_hardcoded_host_paths_cg16.py::test_inventory_is_current`
went red because the doc prose changed after the last scan. It was fixed by
regenerating `v0.3-prelim/data/results/cg16_host_path_inventory.json` with
`scripts/cg16_scan.py`, not by relaxing the assertion. After the refresh: 7 passed.

## Version and tag state

`VERSION` was **not** advanced by this round, so no new save-point tag is required:
`v0.3-prelim/tests/test_version_tokens_have_tags.py` requires a save-family tag whose
target commit carries the current `VERSION` tail, and `v19.2-F-RecordSave-2026-11-08`
(commit `d4dd936`) still satisfies that. That guard is inside the gate and passed.

## What this evidence does NOT claim

- It does not certify the physics. The gate asserts its enumerated layers only (CG-5).
- Option (a) was a wording decision. No channel count in the paper changed: the paper
  still prints 1 PASS / 0 MARGINAL / 7 FAIL at the canonical Phase-44 parameters and
  5 PASS / 2 MARGINAL / 1 FAIL at the v19.2-E A.2 best fit, both from
  `scripts/canonical_numbers.py`.
- The accepted asymmetry is recorded, not resolved: the paper describes the canonical
  arm, `CURRENT.md` records the adopted `a_slope` 0.5 / 0.8 arms.
