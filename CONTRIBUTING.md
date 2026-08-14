# Contributing to sidm-composite-dm-mediator

This project follows the [Version Control Framework](../version-control-framework/) at `C:\Users\lamkuenai\tools\version-control-framework\`. The framework files in this project (`CONTRIBUTING.md`, `VERSION`, `.gitattributes`, `.githooks/pre-commit`) are **local copies** (this project customized `.gitignore` with project-specific exclusions and used `--no-symlink` for the rest). Framework updates will not auto-propagate; re-apply via `vc_init.sh --no-symlink` if you want the latest.

## Branching model

This project uses the `wip/vX.Y.Z` branching model:

| Branch | Purpose | Lifetime |
|---|---|---|
| `master` (or `main`) | Released, tagged versions. Always in a state that compiles + tests pass. | Permanent |
| `wip/vX.Y.Z` | Active work on version vX.Y.Z. May have broken tests, WIP commits, etc. | Deleted after vX.Y.Z ships and a tag is made |

**The rule: every commit goes to a `wip/vX.Y.Z` branch, never to `master` directly.** When vX.Y.Z is ready to ship:
1. Make sure the wip branch builds and tests pass
2. `git checkout master && git merge wip/vX.Y.Z --no-ff`
3. `git tag -a vX.Y.Z -m "vX.Y.Z release: <one-line summary>"` (annotated tag, see below)
4. `git branch -d wip/vX.Y.Z` (after the merge)
5. Push `master` + the tag

For this project, the framework convention is enforced as the **initial state**: when this repo was first published, the `master` branch held the initial commit (the entire v0.1 → D15-CORRECTED3 + Mediator v12 history as a single capture point). All **subsequent** work goes on `wip/vX.Y.Z` branches per the rule above.

## Tag scheme

Tags are **annotated** (not lightweight) and follow `vX.Y.Z` with optional pre-release suffixes:

- `v1.0.0` — first stable release
- `v1.2.3` — patch release
- `v1.9.3` — minor release (default tag format for this host)
- `v1.9.3-PATCH` — pre-1.10 patch series (matches the WIMpy convention)
- `v2.0.0-rc1` — release candidate

**The rule: every tag is a release, every release is a tag.** Don't tag for checkpoints or work-in-progress; use branches for that. Don't release without tagging.

To create an annotated tag:
```bash
git tag -a vX.Y.Z -m "vX.Y.Z release: <one-line summary>

<bulleted list of changes since the last tag>"
```

## Commit message format (Conventional Commits)

This project follows [Conventional Commits 1.0.0](https://www.conventionalcommits.org/). Format:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Common types:

| Type | Use for | Bumps version? |
|---|---|---|
| `feat` | New user-facing feature | minor (X.Y.**Z+1**) |
| `fix` | Bug fix | patch (X.Y+1.**Z**) |
| `refactor` | Code change that doesn't fix a bug or add a feature | none |
| `perf` | Performance improvement | patch |
| `docs` | Documentation only | none |
| `test` | Adding or fixing tests | none |
| `chore` | Build, CI, tooling, deps | none |
| `revert` | Reverts a previous commit | none |
| `wip` | Work in progress (used sparingly, usually on wip/* branches) | none |

**Examples (real commits from this project):**

```
v6d.6v-bundle: CHANGELOG updated with v1.3.0 SHIPPED + definitive finding
v6d.6u-qthreshold: Q-threshold sweep setup (B=5.5T, slcoupled)
v1.9.3 PATCH r2: dovekie_loader.py line 103 filename bug fix
v1.9.3 PATCH: Test 18 per-model full-Planck chi² table
v2.0: add Euclid DR1 weak-lensing loader (Tier 2 #1)
```

**The rule: the subject line is `<type> <scope>: <one-line summary>`, max 72 chars, imperative mood ("add" not "added").** No period at the end. The body (if present) wraps at 72 chars and explains the WHY, not the WHAT (the diff shows the what).

## Windows ↔ WSL sync convention

**This is the most important convention for this host.** The host has two filesystems:
- Windows: `C:\Users\lamkuenai\<project>\` — where `write_file`, `patch`, `read_file`, and other Hermes tools land
- WSL: `/home/lamkuenai/<project>/` — where `wsl -e bash ...` invocations run Python/julia/etc.

**The Windows copy is canonical.** The WSL copy is a sync target, not a source of truth. All edits go to Windows, then sync to WSL via:

```bash
wsl -e bash -c "cp -ru /mnt/c/Users/lamkuenai/<project>/ /home/lamkuenai/<project>/"
# or for a single file:
wsl -e bash -c "cp /mnt/c/Users/lamkuenai/<project>/<file> /home/lamkuenai/<project>/<file>"
```

**vc_init.sh + WSL pitfall (caught 2026-06-24 on WIMpy instantiation):** if you run `vc_init.sh` from WSL bash (e.g., `wsl -e bash -lc "./vc_init.sh /home/lamkuenai/wimpy_results"`), the `.git/` directory lands at `/home/lamkuenai/<project>/.git/` (the WSL side). The git repo then drifts from the Windows canonical because Windows edits never reach the WSL-side repo. Two correct procedures:

1. **Run `vc_init.sh` from Windows-side bash in the first place** (recommended). The `.git/` directory lands at `C:\Users\lamkuenai\<project>\.git\` directly. `write_file`/`patch` then land in the canonical repo. WSL stays as a sync target for running scripts.
2. **After WSL init, move `.git/` to Windows:**
   ```bash
   wsl -e bash -c "cp -r /home/lamkuenai/<project>/.git /mnt/c/Users/lamkuenai/<project>/.git && rm -rf /home/lamkuenai/<project>/.git"
   # Then from Windows-side bash:
   cd C:\Users\lamkuenai\<project>
   git status  # should show clean working tree
   ```

**9P cache gotcha:** the 9P filesystem driver that bridges `/mnt/c/...` from WSL has a metadata cache with a 1-30s TTL. After a Windows-side `write_file`, wait 2 seconds OR `ls -la` the parent dir OR `cp` to force a fresh read before expecting the WSL side to see the new file. Full details in the `windows-host-wsl-orchestration` skill.

**9P symlink gotcha (caught 2026-06-24 on WIMpy instantiation):** git cannot follow symlinks through `/mnt/c/...` because of 9P filesystem limitations. The `.gitignore` symlink (and other framework symlinks) silently fail to be respected by git, leading to spurious file staging. If your project is on WSL (or accessed via `/mnt/c/...`), use **real copies** of the framework files, not symlinks. After `vc_init.sh` completes, replace symlinks with copies:

```bash
cd C:\Users\lamkuenai\<project>
for f in .gitignore .gitattributes .githooks/pre-commit CONTRIBUTING.md VERSION; do
  [ -L "$f" ] && rm "$f" && cp "/c/Users/lamkuenai/tools/version-control-framework/$f" "$f"
done
```

**After any sync, verify the destination matches the source:**

```bash
wsl -e bash -c "diff -rq /mnt/c/Users/lamkuenai/<project>/ /home/lamkuenai/<project>/ --exclude=__pycache__ --exclude=.git"
```

**9P cache gotcha:** the 9P filesystem driver that bridges `/mnt/c/...` from WSL has a metadata cache with a 1-30s TTL. After a Windows-side file write, wait ~2 seconds (or `ls -la` the parent dir, or `cp` to force a fresh read) before expecting the WSL side to see the new file. This bit-trap is documented across many projects on this host.

**9P symlink gotcha:** git cannot follow symlinks through `/mnt/c/...` because of 9P filesystem limitations. The `.gitignore` symlink (and other framework symlinks) silently fail to be respected by git, leading to spurious file staging. If your project is on WSL (or accessed via `/mnt/c/...`), use **real copies** of the framework files, not symlinks. This project does so (see the `--no-symlink` flag of `vc_init.sh`).

**Background processes from WSL:** when launching a long-running process that needs to survive the Hermes terminal (e.g. a dynesty run, a KiSS-SIDM Julia worker), use the **setsid + nohup + wrapper-script pattern**:
- `setsid` detaches the process from the controlling terminal
- `nohup` makes it ignore SIGHUP
- Wrap the command in a small shell script that writes a PID file and a log file, so a watchdog can monitor progress

The KiSS-SIDM Julia worker in this project follows this pattern: see `v0.3-prelim/code/kiss_sidm_julia_bridge.py` and the worker script at `/tmp/kiss_sidm_worker.jl` on the WSL side.

## Code review

Use the `requesting-code-review` skill for the full workflow. The short version:

1. Before any commit, run the pre-commit hook (it auto-runs on `git commit` if installed)
2. Before any PR, run `simplify-code` (parallel 3-agent cleanup)
3. After any non-trivial feature, request a review from a different agent session
4. Reviews should follow the `reviewer-audit` skill's tier-ranked grading (engineering / physics / strategy / documentation)

## Release process

1. Make sure `wip/vX.Y.Z` builds and tests pass
2. Update `CHANGELOG.md` (move the [Unreleased] section to a new `## [vX.Y.Z] - YYYY-MM-DD` section)
3. Bump `VERSION` to `vX.Y.Z`
4. `git checkout master && git merge wip/vX.Y.Z --no-ff`
5. `git tag -a vX.Y.Z -m "..."` (with the changelog bullet as the tag message)
6. `git branch -d wip/vX.Y.Z`
7. `git push origin master --tags`
8. If shipping a release artifact (PDF, ZIP, etc.), generate it AFTER the tag is created, not before. The artifact's filename should include the tag: `<project>_vX.Y.Z_<artifact-type>.<ext>`.

## When to ask the user (the project owner) vs when to use judgment

| Decision | Authority |
|---|---|
| New dependency (`pip install X`, `npm install Y`) | **Owner approval required.** The owner maintains the wimpy shared venv; new deps can clash with WIMpy's pinned stack. Justify in the PR description. |
| New MCP server, skill, or CLI tool | **Owner approval required.** Tools become permanent context-window footprint for every contributor. |
| Bumping version (patch / minor / major) | **Owner approval required.** Project uses `vX.Y.Z` tags; bumping = publishing to users. |
| Branching off a new `wip/vX.Y.Z` | Agent judgment |
| Commit message wording | Agent judgment |
| Refactor / rename / reformat within a wip branch | Agent judgment |
| Deleting a file | **Owner approval required** if it's user-facing (in `docs/`, root, or `README.md`-referenced) |
| Deleting a tag | **Owner approval required.** Tags are releases; deleting = un-publishing. |
| Force-push to `master` | **NEVER** (without explicit owner direction). Use `git revert` or fix-up commits instead. |
| Force-push to `wip/vX.Y.Z` | Agent judgment (only your own wip branch, never someone else's) |
| Adding new external data to `v0.*-prelim/data/` | **Owner approval required.** External data needs a `DATA_SOURCES.md` entry. |
