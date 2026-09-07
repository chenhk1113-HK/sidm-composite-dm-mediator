# Tidy-up Scope Audit: Reviewer 2 vs GitHub Best Practices vs Project Reality

**Status:** Scope decision document
**Date:** 2026-09-07
**Branch:** `wip/tier3-magnetic-moment-LZ`
**Trigger:** User question "can we tidy up and streamline repo management and structure and documentation with reference to reviewer2 views?"

---

## Headline

**Most of Reviewer 2's recommendations are already satisfied.**
The project already has CHANGELOG, CONTRIBUTING, VERSION,
DISCLAIMER, EXTRACT, MODEL_ASSUMPTIONS_AND_LIMITATIONS,
CURRENT, CITATION.cff, LICENSE, .gitignore, .gitattributes,
scripts/t82_audit.py (drift-guard), and docs/INDEX.md.

**The REAL gaps** are narrow and well-defined:

1. **No CI workflow** (.github/workflows/ doesn't exist)
2. **No Dockerfile** for reproducible env
3. **README test-count drift** (badge 549 vs table 677 vs
   real 457) — Reviewer 2 right about this drift existing
4. **Some Reviewer 2 claims were wrong** (branch names,
   test counts, no legacy v0.1/v0.2 prototypes)

**GitHub community best practices** (per web search):
- README ≤ 500 lines is good; current is 493
- CHANGELOG.md is good (✅ exists)
- Keep-a-Changelog 1.1.0 is the de facto standard (✅ in use)
- Conventional Commits is the de facto standard (✅ in use)
- GitHub Flow is recommended over Git-Flow for small teams
  (✅ project already uses wip/vX.Y.Z, which is GitHub-Flow-like)
- CI is recommended (❌ missing)

**Project's own audit pattern** (R2 through R16 already in
docs/): use V1 5-label matrix, W4 grade, W5 ship/defer/reject.
This audit follows the established convention.

---

## Reviewer 2 vs GitHub Community vs Project Reality

| Item | Reviewer 2 | GitHub Best Practice | Project Reality | Action |
|---|---|---|---|---|
| README.md | "monolithic, ~10k words" | "≤ 500 lines is good" | 493 lines (acceptable) | **No-op** |
| LICENSE | "MIT" | required | MIT (1062 bytes) | **No-op** |
| CHANGELOG.md | "should exist" | Keep-a-Changelog standard | 73 KB, follows 1.1.0 | **No-op** |
| CONTRIBUTING.md | "should exist" | recommended | 199 lines, full framework | **No-op** |
| CI workflow | "should exist" | recommended | **MISSING** (.github/workflows/ doesn't exist) | **REAL GAP** |
| Dockerfile | "should exist" | recommended | **MISSING** | **REAL GAP** |
| README test-count drift | didn't mention | best practice | badge=549, table=677, real=457 | **REAL GAP** |
| CODE_OF_CONDUCT.md | "should exist" | recommended | **MISSING** | Minor gap |
| Issue templates | didn't mention | recommended | **MISSING** (.github/ISSUE_TEMPLATE/) | Minor gap |
| Pull request template | didn't mention | recommended | **MISSING** | Minor gap |
| Zenodo/release artifacts | "should exist" | best practice | partial (data/results/ in git) | Real but complex |
| Branch policy | mentioned dev/main | GitHub Flow | wip/vX.Y.Z + master | **No-op** (already follows GitHub Flow variant) |
| Conventional Commits | didn't mention | recommended | ✅ in CONTRIBUTING.md | **No-op** |
| Keep-a-Changelog | didn't mention | recommended | ✅ in CHANGELOG.md | **No-op** |
| Drift-guard script | mentioned t82_audit.py | best practice | ✅ scripts/t82_audit.py exists | **No-op** |
| CITATION.cff | didn't mention | recommended | ✅ 3.9 KB | **No-op** |
| V0_6_ROADMAP.md | didn't mention | recommended | ✅ at v0.3-prelim/docs/ | **No-op** |
| Reviewer audit docs | didn't mention | n/a | ✅ R2, R9-R16 exist | **No-op** |
| README/CURRENT split | "split monolithic README" | recommended | ✅ CURRENT.md exists | **No-op** |
| Layman summary | didn't mention | n/a | ✅ EXTRACT.md, LAYMAN_SUMMARY.md | **No-op** |
| MODEL_ASSUMPTIONS doc | didn't mention | best practice | ✅ 45 KB | **No-op** |
| Disclaimer | didn't mention | recommended for AI-assisted projects | ✅ 2 KB | **No-op** |
| Legacy prototype branches | "v0.1 / v0.2 preserved" | n/a | ❌ **WRONG** (no legacy branches on disk) | Stale claim |
| "main + dev" branches | dev branch mentioned | n/a | ❌ **WRONG** (branches are master + wip/tier3 + wip/v0.4) | Stale claim |
| 137 commits | "137 commits" | n/a | ❌ **WRONG** (165 commits) | Stale claim |
| 677 tests pass | "677 tests pass" | n/a | ❌ **WRONG** on this branch (457 + 1 error) | Stale claim |
| "v0.8 MAP point" | "v0.8 MAP, nlive=2000" | n/a | ⚠️ version is v0.4-prelim+T88E | Imprecise |
| "v0.4-prelim: ~140 Python modules" | "~140 modules" | n/a | ⚠️ 273 .py files total, ~140 in v0.3-prelim/code/ | Imprecise |
| Single-maintainer risk | mentioned | best practice | ✅ single-maintainer (true) | Acknowledge |
| Large JSON artifacts | "data/results has hundreds" | best practice | ✅ 178 files in v0.3-prelim/data/results/ | **REAL GAP** |
| CI-gatable but not hooked | mentioned | n/a | ✅ accurate (no .github/workflows/) | **REAL GAP** |
| KiSS-SIDM (Julia) | mentioned | n/a | ✅ kiss_sidm_julia_bridge.py exists | **No-op** |
| 22 channels | "22 channels in v0.8" | n/a | ⚠️ README says 22 but version is v0.4 | Imprecise |

**Summary**: 18 ✅ No-op (already satisfied) / 3 ❌ Stale
(Reviewer 2 wrong) / 5 ⚠️ Imprecise (right direction, wrong
specifics) / 6 ❌ REAL GAPS.

---

## The 6 REAL GAPS (what's actually missing)

### Gap 1: No CI workflow (.github/workflows/)

**Status**: Confirmed missing. `ls .github/` returns no
such directory.

**GitHub best practice**: GitHub Actions is the de facto
standard. For a Python project, the canonical workflow runs:
- `pytest` on every push/PR
- Drift-guard / linter (project has scripts/t82_audit.py)
- Optionally: matrix across Python versions

**Effort**: 1-2 hours. Low risk (just YAML files).

**Recommendation**: **Ship**. Single commit, add
`.github/workflows/ci.yml` running `pytest` + `t82_audit.py`.

### Gap 2: No Dockerfile

**Status**: Confirmed missing.

**GitHub best practice**: Common for computational physics
projects with non-trivial dependencies (Julia + Python +
specialized packages).

**Effort**: 1-2 hours. Low-medium risk (env composition).

**Recommendation**: **Ship if Julia KiSS-SIDM is a hard
dependency** for production runs. **Defer if Julia is
optional** (used only for a subset of channels).

Need to check: is Julia KiSS-SIDM used by default or as an
opt-in?

### Gap 3: README test-count drift

**Status**: Verified on-disk. README line 7 badge says
"549 pass, 8 skip", README table says "677 pass, 8 skip",
actual pytest on this branch is "457 collected, 1 error".

**GitHub best practice**: badges should match reality.

**Effort**: 5 minutes (one-line patch). Low risk.

**Recommendation**: **Ship**. Pick one canonical number and
fix both the badge and the table.

### Gap 4: CODE_OF_CONDUCT.md

**Status**: Missing.

**GitHub best practice**: Recommended for open-source repos
with multiple contributors. Lower priority for
single-maintainer projects.

**Effort**: 5 minutes (use Contributor Covenant template).

**Recommendation**: **Defer**. Single-maintainer project;
not blocking.

### Gap 5: Issue / PR templates

**Status**: `.github/ISSUE_TEMPLATE/` doesn't exist.

**GitHub best practice**: Recommended for repos that accept
external contributions.

**Effort**: 30 minutes.

**Recommendation**: **Defer**. Single-maintainer; user opens
issues directly; not blocking.

### Gap 6: Large JSON artifacts in git

**Status**: 178 JSON files in `v0.3-prelim/data/results/`,
18 MB total.

**GitHub best practice**: Recommend git LFS or release
artifacts for binary/JSON outputs > ~5 MB.

**Effort**: HIGH. Requires:
- `git filter-repo` history rewrite (rewrites commit hashes)
- Every branch needs rebase
- Every collaborator needs re-clone

**Recommendation**: **Defer**. High blast radius, current
size (18 MB) is not critical. Note in CURRENT.md as
"known inefficiency, defer until v0.6".

---

## What I propose to ship (3 items, low risk)

A single, focused commit set on a new branch
`wip/tidy-2026-09-07`:

1. **Add GitHub Actions CI workflow** (1-2 hr, YAML)
   - Runs `pytest` + `scripts/t82_audit.py` on every push
   - Matrix on Python 3.11, 3.12 (skip 3.13 for now — PEP 668
     made venv setup harder)
2. **Fix README test-count drift** (5 min, single-line patch)
   - Update both badge and table to a single canonical
     number (use the branch-current count: 457; or use a
     "branch-dependent" note)
3. **Add `docs/reviews/` index file** (30 min, optional)
   - Lists R2, R9-R16, magnet1, REVIEW6, MAGNET1
   - Makes the audit trail discoverable

**Total**: ~3-4 hours of work. Low risk. No git history
rewrite. No new dependencies. Branch-local until user approves
merge to master.

**NOT shipping** (per scope discussion):
- Dockerfile (need to check Julia dependency first)
- CODE_OF_CONDUCT.md (single-maintainer, not blocking)
- Issue/PR templates (single-maintainer, not blocking)
- LFS/Zenodo for JSON artifacts (high blast radius)
- README refactor (current 493 lines is at the upper edge
  but acceptable; refactor is mostly cosmetic)

---

## What I will NOT do (per Z-series + scope discipline)

- ❌ Auto-implement Reviewer 2's "high-priority" framing as
  if it were authoritative. Per the established audit
  pattern (R2, R9-R16), every recommendation gets verified
  against on-disk ground truth first.
- ❌ Touch master directly. All work on a new
  `wip/tidy-2026-09-07` branch, merge pending user
  approval.
- ❌ Touch the T90.1/T95 experimental branch. The tidy-up is
  a master-repo concern.
- ❌ Rewrite git history (LFS/Zenodo). Defer.
- ❌ Create Dockerfile without first verifying Julia KiSS-SIDM
  dependency status.

---

## Honest caveats

1. **My initial Review6 audit (REVIEW6_AUDIT.md) was wrong
   about `data/results/` not existing.** It exists at
   `v0.3-prelim/data/results/` with 178 files, 18 MB.
   Reviewer 2 was right. I should update REVIEW6_AUDIT.md
   with this correction.

2. **My initial Review6 audit was wrong about test count.**
   On-disk pytest on this branch says 457 + 1 error.
   Reviewer 2 said 677. Both are wrong in their own way:
   neither matches the other. The README internal drift
   (badge=549, table=677) is real and a real bug.

3. **My initial Review6 audit was right that Reviewer 2's
   structural claims about branch names + commit count
   were wrong.** But Reviewer 2's CI / Dockerfile /
   JSON-artifact claims are valid.

4. **I have NOT checked if Julia KiSS-SIDM is a hard
   dependency or optional.** Need to check
   `v0.3-prelim/code/kiss_sidm_julia_bridge.py` before
   deciding Dockerfile scope.

---

## What I need from you

**Three decisions**:

1. **Scope**: My proposed 3-item set (CI + README fix +
   audit index), or a different cut?

2. **Dockerfile**: Defer until I verify Julia KiSS-SIDM
   dependency status, or ship without Julia (pure-Python
   baseline)?

3. **Branch**: New `wip/tidy-2026-09-07`, or directly on
   master?

Tell me which, or pick a different shape entirely.
