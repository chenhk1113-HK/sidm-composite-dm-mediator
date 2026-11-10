# Evidence — round `CMAnchor-2026-11-10`: every c-M tension named its c-M relation, defect D9 resolved, slots [56]–[58] registered

Round span: seven commits `5aa0fce` (2026-11-09 19:34) → `d362721` (2026-11-10 12:30), branch
`wip/v19.2-F-init`, pushed as a fast-forward `6d346e2..d362721`. **VERSION was deliberately not
advanced**, so no new tag is implied and the save point stays `v19.2-F-RecordSave-v1.18`.

This folder records what was **measured**, not asserted. No file here has a `.log` extension —
`.gitignore` line 78 (`*.log`) keeps such names untracked, which is how a "gate log filed" claim
once became false in this repo.

| File | What it is |
|---|---|
| `gate_run_d362721.txt` | Full 15-layer `scripts/verify_release_gate.py` log on the committed head `d362721`. Ends `GATE PASSED: all 15 layer(s) asserted and exited 0`. Run 12:36→13:01 CST. |
| `gate_run_failed_audit_units_pytest_doc_anchors.txt` | The **same gate earlier the same day (11:07 CST), exit 1**, on the pre-fix tree: `[FAIL] audit_units.py`, `[FAIL] pytest`, `[FAIL] audit_doc_anchors.py`, 12 layers PASS. Kept because a green result is only meaningful next to the red one it replaced. |
| `audit_run_units.txt` | `scripts/audit_units.py` standalone after the fix: `✓ No unit consistency issues` (the ASCII `Msun` in reference [44] was the one live finding). |
| `audit_run_doc_anchors.txt` | `scripts/audit_doc_anchors.py` standalone after the fix: `RESULT: PASS` (11 dangling pointers before: 9 × `registry §7.11 DN`, 1 × dead `§5 cross-link`, plus the phantom-filename allowance note). |
| `pytest_paper_v19_regression.txt` | `v0.3-prelim/tests/test_paper_v19_regression.py` standalone: `10 passed`. Before the fix its `[29]` assertion failed because it pinned the pre-2026-11-09 marker text "currently NOT cited in this draft". |
| `self_check_round13.txt` | `scripts/run_round13_self_check.py`: 8/8 layers, `✓ ALL CHECKS PASSED`, exit 0. |
| `pytest_full_suite.txt` | An independent **unfiltered** run of `v0.3-prelim/tests` (`-p no:cacheprovider`, no `-k`): **3684 passed / 25 skipped / 0 failed** in 24m35s. It exists because the gate deselects 40 tests; those assertions do run, and this log is where. Launched 12:16, finished 12:41 — after the last source edit (12:07:49) and across the commit (12:30:06). |
| `c_m_sigma_recomputation.txt` | The headline numbers re-derived from `scripts/elbert2015_c_tau_prescription.py` and cross-checked against the result artifact they are quoted from: artifact-vs-function difference exactly `0.00e+00`. |
| `push_readback_20261110.txt` | Push output plus `git ls-remote` read-back. Remote head equal to local HEAD; `master` shown as the stale branch it still is. |

## The number this round is about

Cloud-9 sits at `c_200 = 6.0` under the Elbert+ 2015 c-tau prescription, against Ohana+ 2026's
measured `c_200 = 4.0`:

| statement | value | relation it is measured against |
|---|---|---|
| framework prediction | +0.7455σ | Diemer+ 2019 (median 7.8964 at M_200 = 4.7×10⁹ M☉) |
| framework prediction | +2.0587σ | Ohana+ 2026 own relation (their pair implies median 12.81) |
| measurement itself | +3.1593σ | Ohana+ 2026 own relation, at c_200 = 4.0 |
| prescription's effect | −1.1006σ | anchor-independent, `log10(6.0/4.0)/0.16 dex` |
| withdrawn value | ~~0.32σ~~ | `0.176 dex ÷ (0.16 × ln 10)` — understates by ln 10 = 2.3026 |

`c_M_tension_sigma_legacy()` reproduces the withdrawn number on purpose and is marked do-not-cite,
so already-published statements stay reproducible. The retracted v40.39 prediction `c_200 = 26.4`
reads −1.9628σ on the Ohana relation (not the −1.42σ the old code printed).

## What the gate does and does not prove

`GATE PASSED: all 15 layer(s)` asserts fifteen enumerated claims, not the whole document (CG-5).
Inside the gate's pytest layer 25 tests were skipped and 40 deselected — a skip or a deselection
proves nothing (CG-10, n25 III.4); the unfiltered log above is the evidence that those 40 pass.
An earlier statement in `CURRENT.md` describing a 2026-11-03 run (1954 passed / 22 skipped /
36 deselected) is left in place as history rather than overwritten.

## What this round does NOT claim

- No σ/m, f_H, halo mass, core radius or crossing time changed. This is a correction of how a
  number is **stated and measured against which relation**, not a new physics result.
- The AIDA-TNG introduction paper (slot [58], KB label [29a], arXiv:2501.12439v2) contributed two
  **qualitative** statements only. Its SIDM cases sit at σ/m = 1 cm²/g and the Correa+ 2021
  velocity-dependent form, and it quotes no concentration or core size below M_vir ≈ 10¹⁰ M☉ —
  Cloud-9 is below that, so none of its numbers were transferred.
- The Cloud-9 residual on Ohana+ 2026's own relation is still ≈2σ: **reduced, not resolved**.
- No tag was created and no VERSION token was added; `test_version_tokens_have_tags.py` therefore
  still certifies the state through `v19.2-F-RecordSave-v1.18`.

## Still to land in this folder

`gate_run_final.txt` — the 15-layer gate re-run on the **record commit** (the front-page + evidence
commit). A gate log certifies only the head it ran on, so the log for `d362721` above does not
certify this commit; it was re-run at filing time and appended when it finished.
