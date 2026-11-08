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
