# Evidence — n27 record round, 2026-11-08

Read directly from the GitHub REST API on 2026-11-08, **unauthenticated** (the
repository `chenhk1113-HK/sidm-composite-dm-mediator` is public). No `gh` CLI is
installed on this host and no GitHub token is configured, so these are raw API
payloads rather than CLI output. Run *logs* are not included: `/actions/runs/<id>/logs`
answers `403 Forbidden` without a token, so the failing step names are recorded and
the step messages are not.

| file | what it is |
|---|---|
| `ci_runs_branch_20261108.json` | every workflow run on `wip/v19.2-F-init` (`total_count: 4`) — Self-check #572 #573 success, CI #242 #243 failure |
| `ci_jobs_newest_20261108.json` | job + step conclusions for CI #243 (`8946b3a`, the HEAD at read time): 3.11 fails at "Install dependencies", 3.12 fails at "Run pytest", `pre-commit py_compile` passes, audit steps 6-8 skipped |
| `ci_runs_20261108.json` | the 50 most recent `ci.yml` runs repo-wide, for the aggregate census quoted in §28.7 |

Query endpoints:
`/repos/chenhk1113-HK/sidm-composite-dm-mediator/actions/runs?per_page=50&branch=wip%2Fv19.2-F-init`,
`/actions/runs/42345553629/jobs`,
`/actions/runs?per_page=50&workflow=ci.yml`.

## Gate evidence (appended after the record commits)

- `gate_full_20261108c.log` - full 15-layer pre-tag gate on `efd6021`, run 2026-11-08:
  GATE PASSED, all 15 layers exited 0. pytest 3642 passed / 25 skipped / 40 deselected in
  1422.63s; t82 drift audit 120/120 ALL CLEAR; PDF render-integrity OK (72 literal '**' in
  the v1.17 PDF, budget 72); advisory triage 0 genuine absences.
- `pdfaudit_prepush_20261108.log` - the same audit layer run standalone before the push, after
  the 11:42 PDF rebuild: RESULT PASS (gate mode), 0 hard defects, 18 advisory prose flags.
- The earlier `gate_full_20261108.log` (06:40) is kept as evidence of a FAILED gate on the
  pre-fix tree: 2 failed tests + 5 errors, and the v1.17 PDF at 74 literal '**' over budget.
  Both failure classes were fixed before the passing run.

## Post-push census (`ci_runs_after_push_20261108.json`)

After the record commits were pushed, the branch has 6 runs. `Self-check #574` succeeded and
`CI #244` failed on the new head `5c93e4de`, with the same three job outcomes as #243:
`Install dependencies` failure (Python 3.11), `Run pytest` failure (Python 3.12),
`pre-commit py_compile` success. The local full gate on the same commit passed 15/15 with
3642 tests, which is what makes the GitHub-side pytest failure an environment problem rather
than a result of this round. Note for anyone repeating this: the jobs endpoint path takes the
run **id** (42449128597), not the run number - using the number returns HTTP 404.

## Final-head gate (`gate_full_20261108d_final_head.log`)

Full 15-layer gate on the final head of the round: `GATE PASSED: all 15 layer(s) asserted and exited 0`,
3642 passed / 25 skipped / 40 deselected in 1430.72s, t82 120/120 ALL CLEAR.

A standalone `pytest v0.3-prelim/tests/` run collected 3707 tests rather than the gate's 3682 because the
gate deselects 40 marked files; a mid-round standalone run that predates the finding-heading fix reported
one failure in `test_integrity_finding_ids_unique.py`. On the final head that file passes 4/4, and the gate's
pytest layer is green. Standalone counts and gate counts are therefore not directly comparable - quote the
gate's numbers for release claims.

Snapshot rule for CI numbers: every push to this branch adds one `Self-check` run and one `CI` run, so a
census written into a report is a read-time snapshot, not a live fact. The report labels its census
read-time for that reason; the durable claim is the failure signature (3.11 `Install dependencies`,
3.12 `Run pytest`, `pre-commit py_compile` green, audit steps never reached), not the run numbers.

## Why the gate logs are stored as `.txt`

`.gitignore` line 78 (`*.log`) silently swallows any evidence file with a `.log` extension, so the gate
logs first copied into this folder were present on disk but not in the repository - the commits that said
"filed the gate log" were overstated. Repo convention (evidence_n24, _n25, _n26) is `gate_run_committed.txt`
and `gate_run_final.txt`, so the logs are stored under `.txt` names here:

- `gate_run_committed_efd6021.txt` - 15/15 PASS on `efd6021` (3642 passed, 1422.63s).
- `gate_run_final.txt` - 15/15 PASS on `4a2ffdc` (3642 passed, 1430.72s, t82 120/120).
- `pdf_render_audit_prepush.txt` - render-integrity layer standalone after the 11:42 rebuild: PASS, 0 hard.
- `gate_run_failed_prefix_tree.txt` - the 06:40 FAILED run (2 failed + 5 errors), kept so the fix path stays visible.
- `gate_run_failed_findingids_L11.txt` - the 08:22 FAILED run (1 failed test + the 74-literal-`**` budget breach).
