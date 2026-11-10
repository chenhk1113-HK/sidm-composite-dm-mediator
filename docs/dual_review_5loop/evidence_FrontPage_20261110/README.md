# Evidence — front-page rewrite (README 869 -> 203 lines), 2026-11-10

Round: landing-page revision requested by the user (abstract, key findings, layman summary only;
no change log, no revision history on the page). Dates 2026-11-10. Branch `wip/v19.2-F-init`.

## What is in this folder

| File | What it is |
|---|---|
| `README_before_20261110.md` | the pre-rewrite landing page, verified byte-identical to `git show HEAD:README.md` (869 lines, 74,643 bytes). Working copy also at `AppData/Local/hermes/cache/scratch/README.md.bak.20261110_194715`. |
| `gate_run1_msys_env_failure.txt` | full 15-layer gate run 1. Red: `[FAIL] pytest`, `13 failed, 3631 passed, 22 skipped`. All 13 failures are `CollectIntegrationError` caused by `DM_SIDM_PROJECT_ROOT="$(pwd)"` resolving to the MSYS path `/c/Users/lamkuenai/...` under the Hermes terminal tool. |
| `gate_run2_cg16_inventory_stale.txt` | full 15-layer gate run 2 with the env var set in Windows form. Red: `[FAIL] pytest`, `1 failed, 3643 passed, 25 skipped, 40 deselected in 1412.13s`; the single failure is `v0.3-prelim/tests/test_no_hardcoded_host_paths_cg16.py::test_inventory_is_current`. 14 of 15 layers PASS. |
| `cg16_check_after_inventory_refresh.txt` | `scripts/cg16_scan.py --check` after re-scanning: `OK: inventory matches the tree; no host path in live-scope code`, exit 0. |
| `gate_run3_green_precommit_tree.txt` | full gate run 3, finished 22:40 on the working tree as it stood then (the page was patched once more at 22:44, so this log does not byte-certify `df92ecf`). `GATE PASSED: all 15 layer(s)`, pytest 3644 passed / 25 skipped / 40 deselected in 1521.26s. |
| `gate_run4_certify_be4cb92.txt` | full gate run 4, finished 00:21 on head `be4cb92`. `GATE PASSED: all 15 layer(s)`, pytest 3643 passed / 26 skipped / 40 deselected in 1355.71s, drift 120/120 ALL CLEAR. This is the log that certifies `be4cb92`; the dated tag anchors on `dffbf11`, whose own gate run is `gate_run6_certify_dffbf11.txt`. |
| `gate_run5_red_cg16_3165b6e.txt` | full gate run 5 on `3165b6e` (the evidence-filing commit). Red: `1 failed, 3642 passed, 26 skipped, 40 deselected in 1332.85s`, single failure `test_no_hardcoded_host_paths_cg16.py::test_inventory_is_current`, `docs_prose 143 -> 149`. Expected failure mode, recorded rather than hidden: the inventory was re-scanned **before** the renamed files were staged, and `scripts/cg16_scan.py:50` enumerates the tree with `git ls-files`, which reports the index, not the working directory. Fixed by re-scanning after staging. |
| `gate_run6_certify_dffbf11.txt` | full gate run 6, finished 02:51 on `dffbf11`. **`GATE PASSED: all 15 layer(s) asserted and exited 0`**, pytest 3644 passed / 25 skipped / 40 deselected in 1303.05s, drift 120/120 ALL CLEAR. This is the run that certifies the commit the dated tag `v19.2-F-RecordSave-2026-11-11` anchors on. |
| `tag_readback_20261111.txt` | read-back of the dated tag and the push: local refs, the rejected-then-fast-forwarded branch push (remote had moved to `709fbe9`, a web-UI disclaimer edit by the owner, merged in `cf6cedc` without any force push), the `git ls-remote` and GitHub API confirmations, and the 13-file evidence listing read off the remote. |
| `pytest_skip_inventory_be4cb92.txt` | `pytest -q -rs` over the whole suite on `be4cb92` (no gate deselections): 3670 passed, 26 skipped, 0 failed in 1502.68s, with every skip reason named. Produced to check whether the 3644 -> 3643 delta between runs 3 and 4 was a guard silently going quiet; it was not (see "Run-to-run delta"). |
| `docs_guards_after_first_pass.txt`, `docs_guards_after_final_pass.txt` | `audit_markdown_tables.py`, `audit_doc_anchors.py`, `audit_stale_strings.py`, `audit_glyph_coverage.py`, `audit_register_state.py` on the rewritten page. `audit_glyph_coverage.py` is not reproducible standalone under `.venv-sidm-bench` (`ModuleNotFoundError: pdfplumber`); inside the gate it runs under the gate's audit-interpreter candidate list (`scripts/verify_release_gate.py:84-113`) and passes there. |

## Findings this round produced (23 total; the severity-1 ones)

1. **Severity 1 — the Quick start command broke the suite it documents.** `export DM_SIDM_PROJECT_ROOT="$(pwd)"` yields an MSYS path under git-bash; `v0.3-prelim/tests/test_integration_v192f.py:81-82`, `test_cloud9_rebaseline.py:52-53` and `test_no_hardcoded_host_paths_cg16.py:42-43` join it naively, producing `C:\c\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\code`. Fixed by exporting `$(cygpath -w "$PWD")` with a comment naming the hazard.
2. **Severity 1 — CG-16 inventory coupling.** `v0.3-prelim/data/results/cg16_host_path_inventory.json` pins per-file host-path occurrence counts, and `test_inventory_is_current` asserts them. The rewrite deleted a line that held 1 recorded occurrence, so the tree went red for a bookkeeping reason. Fixed by `python scripts/cg16_scan.py` (142 -> 141 occurrences); the refreshed inventory is committed with this round.

Both were predicted by the independent audit loop **before** run 2 reproduced the second one, which is why run 2's failure is expected evidence rather than a surprise.

## Claims corrected in the page

- `scripts/parallel_run_nl2000.sh` — does not exist in the repo (only the old README mentions it). Replaced with `scripts/t76_run_nlive2000.py` (writes T41's fixed output path; the headline file is the renamed result) plus `scripts/t88ce_postprocess.py`, and the stored run's own `wall_seconds` = 751.7 s instead of the page's "~7 minutes".
- Ohana+ 2026 was listed as a likelihood input to the headline fit; the paper cites it at slot [225] as a c-M scaling corroboration. Removed from that list.
- The gate's "15 layers" were described loosely (and omitted 9 of them). Replaced with the 15 layer scripts enumerated from `scripts/verify_release_gate.py` — 15 entries, 14 asserted + 1 informational (CG-15 disclosure) — and `audit_markdown_tables.py` / `run_round13_self_check.py` are now labelled as run *alongside* the gate, not as gate layers.
- History pointer widened to `v0.3-prelim/README.md` and `v0.3-prelim/docs/archive/phases/`.

## How the numbers on the page were checked

- Section count 32 = `grep -c "^##\? [0-9]" docs/PAPER_V1_DRAFT.md`; 23 body sections + 9 appendix sections (A1-A6, B1-B3).
- Reference count 231 = `len(re.findall(r"^\[\d+\]", paper, re.M))`; last slot `[231]`.
- **Numeric-token audit.** 59 decimal tokens appear on the new page; 50 appear verbatim in the certified pre-rewrite page (`git show HEAD:README.md`). The 9 that do not were each checked individually: `0.155 / 0.093 / 0.067 / 0.047 / 0.032` are the per-slot published ceilings in `canonical_numbers.json -> per_channel_at_v19_2_E_A2_best_fit` (citation `Horigome+ 2025 Table II`); `2.06` and `0.32` are the CMAnchor c–M sigma figures carried in `CURRENT.md`; `751.7` is the T41 v0.8 artifact's `wall_seconds`; `12.5` is derived from it.
- **Headline tally.** `5 PASS / 2 MARGINAL / 1 FAIL` and all eight per-row verdicts match `per_channel_at_v19_2_E_A2_best_fit` row-for-row; `pass_fail_summary_v19_2_E_A2_best_fit.canonical_count_string` = "5 of 8 channels pass (v19_2_E_A2_5param_DE_best_fit, published_sigma_unc)". The sibling block `per_channel_at_v19_2_D_canonical` is 1 PASS / 7 FAIL — the superseded v19.2-D Phase-44 fit, which is why the tally line names its parameter set.
- **Standing fit numbers.** sigma/m_0 0.06 (`sigma_m_0_derived` 0.05991), log Z -164.87 +- 0.084 (-164.8685 +- 0.0841), m_chi MAP 478 (median 502.9), m_phi MAP 488 (median 598.4), g_chi 0.964 (median 1.549), a +0.132, epsilon ~ 1e-37 (1.068e-37) — from `canonical_numbers.json -> t41_v08_standing_map` (source_artifact_sha256 `d2ee97506ed0dd…`).
- **Pairing declaration.** live f_H 0.7501856343179664 / archived 0.297; archived amplitudes 0.052 and 174.0; live 0.00815 and 27.27 = archived / 6.380057431067687 — from `canonical_abstract_channel_count.pairing` and `v19_2_E_A2_5param_DE_best_fit.live_pair_equivalent`.
- **Structure.** 32 body sections (`grep -c "^##\? [0-9]" v0.3-prelim/docs/PAPER_V1_DRAFT.md`), 231 reference slots (`len(re.findall(r"^\[\d+]", paper, re.M))`), 8 H3 findings, 10 H2 sections, 40 table rows.

## Guards that constrain what the front page may say, and how the rewrite satisfies them

- `scripts/drift_guard.py::check_channel_count_claims` — a `N PASS / M MARGINAL / K FAIL` tally must name its parameter set and σ_unc convention **on its own line**. Every tally line in the new README carries `v19.2-E A.2` + `published σ_unc` or an explicit `historical` label.
- `scripts/drift_guard.py::check_t41_standing_in_doc` — the superseded v0.7 MAP numbers (770 GeV / 453 MeV / 0.60σ / a +0.34) are quoted only inside a line labelled `Historical, superseded (v0.7 MAP, pre-T88.E)`.
- `scripts/t82_audit.py` — doc-presence checks still find the standing numbers (`0.13`, `−164.87`, `0.084`, `22`, the T89-era `677 pass, 8 skip` badge, the `120/120 ALL CLEAR` literal) and the derived values re-computed from the T41 artifact.
- `scripts/audit_claims.py` (regex mode) — mapped claims are searched in paper + README combined; dropping the Phase 44 `+8.10 log-units` figure from the front page made that mapped claim unfindable, so the figure is kept in the mixed-statistics section instead of being removed.
- `v0.3-prelim/tests/test_pairing_label_coverage.py` — the pairing-declaration paragraph (live vs archived f_H/σ pair) was carried over verbatim; the guard corrupts it on purpose and asserts it re-fires.
- `v0.3-prelim/tests/test_markup_balance_cg4.py` — no block may carry an unbalanced `**`; every table row's emphasis count was checked.
- `v0.3-prelim/tests/test_channel_taxonomy_single_source.py` — the retired 4/3/1 and 4-of-5 tallies must not appear as live claims; the new README states only the computed 5/2/1 tally with its taxonomy note.
- `v0.3-prelim/tests/test_t82_audit_readme_drift.py` — claimed as the badge guard, and on inspection it does **not** guard this repo's badge: `_read_readme_badge_count()` matches `badge/tests-(\d+)\s*pass` (test_t82_audit_readme_drift.py:75-78) while the shields URL here spells the number `tests-3644_pass`, an underscore the regex cannot match, so the test reports `SKIPPED ... README badge is branch-dependent (no specific count)`. The badge was therefore verified by hand against the logged gate runs (`gate_run3_green_precommit_tree.txt`, `gate_run4_certify_be4cb92.txt`), not by that guard.

## Run-to-run delta, and what a skip does and does not prove

Runs 3 and 4 differ by exactly one test: 3644 passed / 25 skipped (run 3) versus 3643 / 26 (run 4). The `-rs` inventory (`pytest_skip_inventory_be4cb92.txt`) names all 26 skips, and the one that changed state is `v0.3-prelim/tests/test_t95_v12_gmm_cross_match.py:56` — `Gaia unavailable after 3 attempts: Error 503`. Re-running that file alone on the same head gives **7 passed in 127.26 s**, so the guard did not go quiet: the Gaia archive returned 503 during the batch runs. Recorded because a pass -> skip flip looks identical to lost coverage in the summary line, and only the reason string distinguishes them. Run 6 on the tagged commit read 3644 / 25 again with the same suite, confirming the swing is that one network guard rather than a coverage change. Skipped and deselected tests prove nothing either way (CG-10), which is why the counts are quoted with the skip inventory behind them.

## Filing correction found while making the dated tag

`.gitignore:78` is `*.log`. Five evidence files written with a `.log` extension were therefore invisible to `git add` and never reached GitHub, while this README's own file table listed them as filed — the folder looked complete and was not. All five are renamed to `.txt` and committed; `gate_run_final.txt` became `gate_run3_green_precommit_tree.txt` so each log names the tree it ran on, and `gate_run4_certify_be4cb92.txt` plus `pytest_skip_inventory_be4cb92.txt` were added. Rule for future rounds: evidence files inside this repo must not use a `.log` extension (or must be `git add -f`'d), and `git ls-files <evidence dir>` is the check, not `ls`.


## Environment note (why the first gate run was red)

The first attempt exported `DM_SIDM_PROJECT_ROOT` as an MSYS path (`/c/Users/...`). Three test modules join that value naively and produced `C:\c\Users\...`, giving 3 collection errors and a red pytest layer. Re-run with the Windows form (`C:\Users\...`): the defect was the launcher's env var, not the repository. It was then fixed **on the page itself**, because the documented command was the thing that broke.

## Independent-review items deliberately NOT applied

- Removing the "3,644 passed" test count from the front page — rejected: it is a verification fact, not a revision log, and matches a real logged run.
- Deleting F1 (composite mediator exists) and F4 (model comparison) as "uninformative" — rejected: both are load-bearing for the F11/F5/F10 readings and are what the findings section is for.
- Shortening the layman section — rejected: the user explicitly asked for a layman summary on the page.
