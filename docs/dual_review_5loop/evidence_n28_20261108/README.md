# Evidence — round n28 (2026-11-08): decision D12, the GitHub publication surface

Two commits: `da9090d` (CI workflow switched off) and `1f1e038` (decision logged +
front pages synced). This folder records what was **measured**, not asserted.

| File | What it is |
|---|---|
| `ci_runs_after_disable_20261108.json` | The 8 most recent Actions runs, read from the public REST API after the disable push. `GET /repos/{o}/{r}/actions/runs?per_page=8` — works unauthenticated on this public repo. |
| `repo_state_20261108.json` | The repo object from `GET /repos/{o}/{r}` — carries `default_branch`, which is what decision D12(b) is about. |
| `gate_run_final.txt` | Full 15-layer `scripts/verify_release_gate.py` log for the final head of this round (`.txt`, not `.log` — `.gitignore` line 78 keeps `*.log` untracked). |

## What the run list proves

Read 2026-11-08, after pushing `1f1e038`:

- Run **578 Self-check @ 1f1e038 — success**. That is the push with the CI file renamed
  away, and **no CI run was created for it**. The disable works: GitHub only picks up
  `.yml`/`.yaml` filenames, so `ci.yml.disabled` is not a workflow.
- The last CI run was **247 @ 8216bda — failure**, i.e. the previous push. CI #246 @
  `70a318a` likewise. Nothing after the rename.
- `Self-check` continues to run and pass on every push to `wip/v19.2-F-init` (575-578).
  Only the `CI` workflow was switched off.
- `default_branch` is still **`master`**. Changing it needs the GitHub web UI or a
  token with repository administration. This host has neither (no `gh` CLI,
  `GITHUB_TOKEN` commented out in `~/.hermes/.env` lines 402-409, no connected GitHub
  account), so this half of D12 is an owner action and was recorded as such instead of
  being silently skipped.

## What is NOT claimed

- The disable does not certify anything. It removes a badge that was red for reasons
  invisible from outside (run logs are HTTP 403 without a token). The certification is
  the local 15-layer gate in `gate_run_final.txt`.
- A green Self-check is a narrow suite, not the gate.
- The CI file is preserved, not deleted; re-enabling is one `git mv` plus two fixes
  named in its header.
