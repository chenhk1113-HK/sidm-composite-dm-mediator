# Evidence — decision D12(b) completed (2026-11-08): GitHub default branch is now `wip/v19.2-F-init`

Owner action in the GitHub web UI. Recorded here because the first attempt that evening **did not take effect**,
and the completion was established by reading the setting back rather than accepting the UI.

| File | What it is |
|---|---|
| `repo_default_before_20261108_1845.json` | `GET /repos/{o}/{r}` read at **18:45 CST**: `default_branch` still `master`, repo `updated_at` still 2026-10-11. The failed attempt, recorded rather than quietly retried. |
| `repo_default_after_20261108_1907.json` | The same endpoint read at **19:07 CST**: `default_branch: "wip/v19.2-F-init"`. |
| `actions_runs_20261108_1907.json` | `GET /repos/{o}/{r}/actions/runs?per_page=6` — the six most recent workflow runs, read at 19:07 CST. |

## What the two reads prove

| Time | `git ls-remote --symref origin HEAD` | API `default_branch` | API `updated_at` |
|---|---|---|---|
| 18:45 CST | `ref: refs/heads/master` → `0a98e2d` | `master` | 2026-10-11T15:32:21Z |
| 19:07 CST | `ref: refs/heads/wip/v19.2-F-init` → `049451d` | `wip/v19.2-F-init` | 2026-10-11T15:32:21Z |

Two independent paths (the SSH remote's symbolic HEAD, and the REST repository object) agree at each timestamp, so
the earlier "not yet changed" reading was not a stale cache on one side. `updated_at` did not move between the reads;
that field is **not** a reliable signal for this setting, and `default_branch` is.

## What the Actions read shows

Runs #577–#581 are `Self-check`, all `completed / success`, all on `wip/v19.2-F-init`; the newest is run
`42470525197` (#581) at `049451d`, the latest push. The only failure in the window is **CI #247 at `8216bda`**, which
predates the D12 workflow disable and is no longer a run against the default branch.

## What is NOT claimed

- GitHub run **logs** and annotations need a token (HTTP 403 unauthenticated); only run/job metadata was read.
- `master` is stale, not archived. `origin/master` = `0a98e2d` (2026-10-11), **289 commits behind** the working
  branch, 0 ahead. No branch was deleted, and `self_check.yml` still lists `master` as a trigger branch.
- A green `Self-check` is a narrow suite. The release evidence remains the local 15-layer gate.
