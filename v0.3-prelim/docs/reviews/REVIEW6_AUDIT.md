# Reviewer Audit: Review6.docx on sidm-composite-dm-mediator

**Status:** Documented audit memo
**Date:** 2026-09-07
**Branch:** `wip/tier3-magnetic-moment-LZ`
**Reviewer file:** `C:\Users\lamkuenai\AppData\Local\hermes\cache\documents\doc_ed8f97660bf4_Review6.docx`

---

## Headline

Review6.docx is a **two-reviewer composite**:
- **Reviewer 1**: a detailed review of the T90.1/T95 branch
  work (the branch the user is currently developing)
- **Reviewer 2**: a master-repo-wide review with many
  **verifiably wrong concrete claims** about the repo state

**Reviewer 1 is high-quality and largely correct.** Their
specific numbers (5 probes, Zhang+ 2025 Δlog Z = -23.61,
"v1 superseded v2 artifact") match the on-disk T95 docs.

**Reviewer 2 contains a mix of correct and stale claims.**
Their general observations about good engineering practice
are valid, but many specific repo-state claims
(branch names, test counts, file paths) do not match
on-disk reality.

**The audit response shape:**
1. **Tier-rank reviewers** explicitly (Reviewer 1 > Reviewer 2
   for branch-specific verification)
2. **V1 5-label matrix** for each concrete claim
3. **Per-claim verification status** with on-disk check
4. **No auto-implementation** of high-priority recommendations
   (per Z-series: reviewer's "high-priority" framing is
   their prioritization, not mine)

---

## Per-reviewer verification matrix

**V1 5-label matrix key:**
- ✅ **confirmed** — claim verified against on-disk ground truth
- ✅ **valid-deferred** — claim is correct but not yet shipped;
  not blocking
- ⚠️ **internal-inconsistency** — claim is partly right, partly
  contradicts other evidence
- ❌ **stale** — claim does not match current repo state
- ⚠️ **reviewer-projected-state** — claim credits items not
  yet shipped (Z-pattern)

---

## Reviewer 1 (T90.1 / T95 branch review)

Reviewer 1 reviewed the **actual mechanism** of the
T90.1/T95 work. Their specific numbers and findings
match on-disk ground truth.

| # | Claim | Status | Evidence |
|---|---|---|---|
| R1.1 | "5 probes in T95" | ✅ confirmed | `T95_CONSOLIDATED_RESULTS.md` §1 |
| R1.2 | "Velocity dependence vs BAHAMAS-SIDM: ratio ~0.72" | ✅ confirmed | `outputs/t95/phase0_yukawa_vs_robertson.json` |
| R1.3 | "Core-size: 5-50× too small" | ✅ confirmed | `T95_OPTION2_5_GRAVOTHERMAL.md` |
| R1.4 | "Channel 27: Δlog Z = -1.57 (substantial)" | ✅ confirmed | `outputs/t95/option3_5_8d_results.json` |
| R1.5 | "Zhang+ 2025: Δlog Z = -23.61 (very strong)" | ✅ confirmed | `outputs/t95/option3_6_zhang_gd1_results.json` |
| R1.6 | "Soft-edge v2 was identified and superseded" | ✅ confirmed | `T95_OPTION3_6_V4_RECONCILIATION.md` |
| R1.7 | "Zhang+ 2025 is one interpretation" | ✅ confirmed | `T95_OPTION3_6B_SURVEY.md` (LMC, bar, GMC, CDM subhalo) |
| R1.8 | "Core-size formulae remain approximate" | ✅ confirmed | docs explicitly flag 5-50× vs published hydro sims |
| R1.9 | "No UV completion of magnetic moment" | ✅ confirmed | T90.1 has OI-1..OI-4 roadmap for UV matching |
| R1.10 | "Master branch is untouched" | ✅ confirmed | T90 merge rule unchanged |

**Reviewer 1 verdict: 10/10 confirmed.** No stale claims,
no reviewer-projected-state issues. The review matches
the on-disk T95 documentation precisely.

**This is the right kind of review.** Specific, sourced,
verifiable.

---

## Reviewer 2 (master repo review)

Reviewer 2 reviewed the **whole repository**. Their
general observations are reasonable but **many
specific concrete claims are wrong on disk**.

### Repo structure claims (V1 matrix)

| # | Claim | Status | Evidence |
|---|---|---|---|
| R2.1 | "Repo: chenkh1113-HK/sidm-composite-dm-mediator" | ✅ confirmed | git remote matches |
| R2.2 | "v0.4-prelim+T88E Tier-1 milestone" | ✅ confirmed | README §"Latest version & headline" |
| R2.3 | "137 commits" | ❌ **stale** | `git rev-list --all --count` = **165 commits** |
| R2.4 | "main + dev + archived prototype branches" | ⚠️ **partly stale** | Branches on disk: `master`, `wip/tier3-magnetic-moment-LZ`, `wip/v0.4-prelim` (NO `dev` branch; NO archived v0.1/v0.2 prototype branches) |
| R2.5 | "Branch structure: main is default" | ⚠️ **stale** | `git symbolic-ref refs/remotes/origin/HEAD` → `origin/master`; `master` is default |
| R2.6 | "677 tests pass" | ❌ **stale** | `pytest --collect-only` on `wip/tier3-magnetic-moment-LZ` = **457 tests + 1 collection error**. On `wip/v0.4-prelim` = **154 tests + 1 error**. The 677 is not achievable from either branch. |
| R2.7 | "scripts/t82_audit.py exists" | ✅ confirmed | `ls scripts/t82_audit.py` exists |
| R2.8 | "scripts/t82_audit.py is CI-gatable but no workflow YAML exists" | ✅ confirmed | No `.github/workflows/` directory on disk |
| R2.9 | "data/results has hundreds of large JSON artifacts" | ❌ **stale** | No `data/results/` directory at top level. Top-level `data/` does not exist either. |
| R2.10 | "v0.8 MAP point, nlive=2000" | ⚠️ **imprecise** | No v0.8 yet. README says v0.4-prelim+T88E. nlive=2000 was used in v0.7 (Sep). The MAP values (770 GeV m_χ, 453 MeV m_φ) match the README's table. |
| R2.11 | "v0.4-prelim: ~140 Python modules" | ⚠️ **imprecise** | `find . -name '*.py'` (excluding venv) = **273 files** total, but many are tests/scripts. README cites "~140 production modules" which is plausible for `v0.3-prelim/code/` alone. |
| R2.12 | "Julia KiSS-SIDM (Gurian & May 2025 PRL) gravothermal collapse penalty" | ⚠️ **cannot fully verify on this checkout** | KiSS-SIDM mention in `d13_*` files. The integration is documented in `MODEL_ASSUMPTIONS_AND_LIMITATIONS.md` (cited by Reviewer 2). |
| R2.13 | "Benchmark A only" | ⚠️ **likely correct** | README mentions Benchmark A explicitly. |
| R2.14 | "22 effective channels in v0.8" | ⚠️ **partly confirmed** | README says "22 channels" but version is v0.4-prelim+T88E, not v0.8. |
| R2.15 | "No CI workflow configured" | ✅ confirmed | No `.github/workflows/` |
| R2.16 | "Tests cover physics, sanity, audit checks" | ✅ confirmed | 457 tests in collected set |

**Reviewer 2 verdict: ~7/16 confirmed, 6 stale, 3 imprecise.**
The stale claims are **specific, concrete, verifiable** —
not vague. They suggest Reviewer 2 may have been reading
the README and inferring repo state from there without
on-disk verification.

### README internal inconsistency (V1 finding, NOT a Reviewer 2 finding)

While verifying R2.6, I noticed the README itself has
**internal drift**:

- **README line 7 (badge)**: `tests-549 pass, 8 skip`
- **README table (§"Latest version & headline")**: `Tests | 677 pass, 8 skip`
- **pytest on this branch (wip/tier3-magnetic-moment-LZ)**: 457 collected, 1 error

This is a real, verifiable drift bug. **Reviewer 2 was
right about the existence of test-count drift, even if
their specific numbers are stale.**

The badge (549) is plausibly the count at an earlier
milestone (T75 or so), the table (677) is plausibly
master+wip/v0.4-prelim combined, and 457 is the current
branch-only count. **None of these match each other.**

This is exactly the kind of "doc-vs-code numerical drift"
the T82 audit script was designed to catch.

---

## Reviewer 2 general observations (non-verifiable)

Reviewer 2's general observations are reasonable but
**not verifiable on this branch checkout** (some are about
master, some are about CI/CD infrastructure that doesn't
exist on this repo):

- "Single-maintainer bus-factor risk" — general
  observation, true for any solo project
- "Drift-guard audit is CI-gatable but not hooked" —
  ✅ factually correct about current state
- "Large JSON artifacts bloat git" — generally true for
  computational physics; specific to this repo is unclear
  (no `data/results/` here)
- "Documentation is monolithic and verbose" — qualitative;
  README is 493 lines which is dense but not extreme
- "No container definition" — qualitative observation,
  correct that no Dockerfile exists in the on-disk tree
- "Code/tests drift" — already documented in T82 audit
- "MAP vs median confusion" — flagged in README already
- "Custom 0.60σ metric" — flagged in README already
- "log_alpha not coupled to likelihood" — would need code
  audit to verify, beyond this scope

These are **valid project-level observations** but not
specific enough to act on without further investigation.

---

## High-priority recommendations (Reviewer 2's "actionable items")

Reviewer 2 listed 4 high-priority items. Per Z-series
(reviewer-projected-state), I should **not auto-implement**
these. They are Reviewer 2's prioritization, which may
or may not match what the user wants to ship.

1. **"Add GitHub-Actions CI"** — defensible engineering
   improvement. Would require: workflow YAML creation,
   test infrastructure, agent permissions discussion.
   **Not in scope of the current T95/T90.1 branch work.**

2. **"Separate large output JSON artifacts to Zenodo"** —
   would require: Zenodo DOI creation, git filter-repo
   history rewrite, README updates. **Out of scope
   for current branch.**

3. **"Refactor README structure"** — would require:
   timeline-based content split, drift-guard update
   (M-series), milestone-wide doc update. **Out of scope.**

4. **"Document dependency stack + Dockerfile"** — would
   require: dependency enumeration, Dockerfile creation,
   CI integration. **Out of scope.**

**None of these should be implemented in this branch** —
they are master-repo-wide refactors that should be a
separate, properly-scoped round on master (not on the
T90.1/T95 experimental branch).

---

## What to do (action items for the user)

The user's branch is in good shape. Reviewer 1 confirmed
the T95 work matches their documentation. Reviewer 2's
findings are mostly either:
- (a) Correct general observations that don't apply to
  the experimental branch
- (b) Stale concrete claims about repo state
- (c) Master-repo-wide refactors that should NOT be done
  on this branch

**Three options for the user:**

**Option A**: **Hold and wait for LZ community resolution**
(default). The T95 work is in good shape, Reviewer 1's
audit confirms it.

**Option B**: **Fix the README drift** (line 7 badge says
549, table says 677, both wrong vs current branch).
This is a single-line patch on master + branch.
**Note**: this should be done on master, not on the
T90.1 branch, because the README drift is a master-state
issue.

**Option C**: **Create a separate "repo-wide improvements"
roadmap** that captures Reviewer 2's high-priority items
without doing them now. Future-round scope.

**My recommendation**: Option A. Reviewer 1's audit is
the relevant one for the current work, and they confirm
the T95 program is in good shape.

---

## Honest caveats

1. **I cannot fully verify Reviewer 2's master-repo claims**
   because the user has me on `wip/tier3-magnetic-moment-LZ`,
   not on master. Some of their observations about master
   may be correct there, even if they don't match what I
   can see on this branch.

2. **The README drift finding** is real but **could also be
   a state-difference between branches**. The badge (549)
   might be correct on master, the table (677) might be a
   forward-looking claim, and 457 might be just-this-branch.
   I should not over-claim about the drift severity without
   checking master explicitly.

3. **The "657 tests / 549 badge" discrepancy is a real
   problem** but it's documented in T82 audit territory
   — the audit script is supposed to catch it. If the
   audit script has not caught it, that itself is a
   finding (audit-script not flagging this specific drift).

4. **I have NOT implemented any of Reviewer 2's
   recommendations.** Per Z-series: reviewer's framing
   of "high-priority" is their prioritization. The user
   decides.

---

## Files

- `v0.3-prelim/docs/reviews/REVIEW6_AUDIT.md` — this doc
- `C:\Users\lamkuenai\AppData\Local\hermes\cache\documents\doc_ed8f97660bf4_Review6.docx` —
  original review
- Reviewer 1 confirmation: `v0.3-prelim/docs/T95_CONSOLIDATED_RESULTS.md`,
  `T95_OPTION3_6_ZHANG_GD1.md`, `T95_OPTION3_6_V4_RECONCILIATION.md`
- Reviewer 2 verification: on-disk ground truth checks
  documented above
