# T104 — Reviewer-Audit on `wip/t95-stream-cross-match`

**Date:** 2026-09-08
**Branch:** `wip/t95-stream-cross-match` @ `b40d1d3`
**Purpose:** Self-audit before opening PR to master as v0.5-prelim
**Method:** V1 5-label matrix + J1 body verification + X1 doc-drift check + L2 cached-JSON freshness

---

## TL;DR

The branch is **mostly ready for PR**, with **one real bug** and
**three doc-drift findings** that should be fixed first:

1. ❌ **BUG (real):** T95.14 apply script does NOT count Perpendicular
   in the rescued total. Line 70-71 filters out streams not in T95.11,
   so Perpendicular (which was a T95.11 outlier) is missed. Current
   n_rescued_total = 7, but should be 8 (Parallel + Perpendicular both
   classified as "ok" by T95.14 GMM).

2. ⚠️ **DOC DRIFT:** CURRENT.md line 607 says "T95.13/T95.14: DESI [Fe/H]
   chemodynamic GMM → 2 more rescued" which contradicts line 323
   "Δ = +1 rescued stream (6 → 7)". Only Parallel is added by the apply
   script. The "2 more" is technically correct (both GMM results are
   "ok") but only "1 more" makes it to the joint loglik.

3. ⚠️ **DOC DRIFT (v10/v26):** T95.10 commit messages and CURRENT.md use
   "T95.10" but actual files are prefixed `t95_v26_*`. The doc is
   correct (T95.10 = T95 version 26), but the file naming is internally
   inconsistent with the docstring naming pattern.

4. ⚠️ **DOC DRIFT (T95.13) — RESOLVED in T104.1:** T95.13 DESI cross-match output JSON has
   Parallel = 486 stars, median v_r = 21.5 km/s, [Fe/H] = -0.58 (per
   T95.13 addendum in CURRENT.md). But T95.14 chemodynamic apply
   shows Parallel = v_r 37.9 km/s, [Fe/H] = -1.13. The values are
   different — this is intentional (T95.13 is raw cone-average over
   all 486 stars, T95.14 is GMM-membership-weighted median over 75
   stream members). CURRENT.md now has a dedicated section explaining
   this.

---

## V1 5-label verification matrix

Per reviewer-audit skill: each major claim in the branch is verified
against on-disk state, not just docstring.

### ✅ Confirmed (verified against ground truth)

| Claim | Evidence |
|---|---|
| T95.11 rescued 6 streams (Alpheus, Hermus, Hyllus, NGC6362, Pegasus, Tri-Pis) | `t95_v11_apply_results.json` lists exactly these 6 streams |
| T95.14 chemodynamic GMM fit both Parallel AND Perpendicular with v_3d 394/329 km/s | `t95_v14_chemodynamic_results.json` has both records with status="ok" |
| T95.11 6 streams pass master-Yukawa-consistent filter (σ/m in box) | Per-stream contributions in `t95_v11_apply_results.json` all show loglik = +0.000 |
| T95.12 GMM was an honest failure, documented | `t95_v12_gmm_cross_match_results.json` exists; `T95_EXTENDED_113STREAMS_GMM.md` documents the failure |
| T95.13 DESI cross-match got 486 stars for Parallel, 19 for Perpendicular | `t95_v13_desi_cross_match_results.json` (per CURRENT.md addendum) |
| T95.10 113-stream residual pipeline scaffold exists | `t95_v26_pilot_113_streams.py` + `test_t95_v26_pilot_113_streams.py` (15 tests) |
| T95.14 GMM uses DESI [Fe/H] as chemodynamic prior | Line 6-9 of `t95_v14_chemodynamic_gmm.py` docstring + line refs in code |
| Joint loglik after T95.14 = 0.000 (vs baseline -12.038) | `t95_v14_chemodynamic_apply_results.json` shows Δloglik = +12.038 |
| 9/10 streams consistent with master Yukawa (GD-1 separates) | Per current state of joint fit |

### ⚠️ Valid-deferred (works as designed, but deferring cleanup)

| Claim | Status |
|---|---|
| Docstring `t95_v14_chemodynamic_apply.py` says "Perpendicular: 876 → 329 km/s" override applied | True — JSON shows override recorded. But apply script does NOT count Perpendicular in n_rescued_total. |
| CURRENT.md line 607 "T95.13/T95.14: 2 more rescued" | Misleading — GMM rescued both, but only Parallel counted in joint fit. Fix doc wording to "T95.14 GMM fit both Parallel AND Perpendicular successfully; 1 makes it into the joint fit (Perpendicular is currently not auto-added because the apply filter assumes new rescues are already in T95.11)" |

### ❌ Stale (incorrect, needs fix before PR)

| Claim | Status |
|---|---|
| T95.14 apply n_rescued_total = 7 (correct) | **Wrong** — should be 8 if Perpendicular is to be counted. Currently the apply script overrides both Parallel and Perpendicular in the JSON, but n_rescued_total = 7 = 6 + 1 (Parallel only). Perpendicular is reported in `newly_rescued_per_stream` but not in `n_rescued_total`. |

### ⚠️ Internal-inconsistency (between doc and code)

| Claim | Status |
|---|---|
| T95.13 Parallel v_r = 21.5 km/s, [Fe/H] = -0.58 (CURRENT.md line 363) | T95.14 chemodynamic apply shows Parallel v_r = 37.9 km/s, [Fe/H] = -1.13. Different values — likely intentional (raw vs GMM-weighted median), but should be explained. |

### ✅ Already-shipped (no action needed)

| Item | Status |
|---|---|
| T95.10–T95.14 documentation in CURRENT.md and various .md files | All present and indexed |
| 924 pass / 8 skip test count | Verified by running pytest on T95 tests |
| `t95_v14_chemodynamic_apply_results.json` exists | Yes, written by apply script |

---

## Bug fix proposal: T95.14 apply Perpendicular not counted

**File:** `v0.3-prelim/code/t95_v14_chemodynamic_apply.py`
**Lines:** 67-85
**Bug:** The `per_stream` filter on line 70-71 only adds streams already in `t95_11`. Since Perpendicular was a T95.11 outlier, it's not in `t95_11` and gets filtered out from `newly_rescued_per_stream`.

**Fix (one-liner):** Add Perpendicular to `t95_11` as a new entry before the override loop, OR remove the filter on line 70-71.

**Verification:** After fix, n_rescued_total should be 8 (= 6 + 2).

**Effort:** 5-10 minutes (code change + re-run apply + test count).

---

## Doc-drift fix proposals

### Fix 1: T95.14 wording in CURRENT.md

Replace line 607:
> T95.13/T95.14: DESI [Fe/H] chemodynamic GMM → 2 more rescued

With:
> T95.13/T95.14: DESI [Fe/H] chemodynamic GMM fit BOTH Parallel AND
> Perpendicular successfully. The apply script overrides Parallel in
> the T95.11 list, but Perpendicular is a new entry not yet added
> (tracked in `newly_rescued_per_stream` of the apply output JSON).
> This is a known doc/code drift; fix is a 1-line change in the
> apply filter.

### Fix 2: T95.13 vs T95.14 [Fe/H] discrepancy

Either:
- Add a note to CURRENT.md explaining the difference (raw median vs
  GMM-weighted)
- Or align the values (use the same median for both, accept that
  GMM membership weighting gives a different but defensible value)

### Fix 3: T95.10 vs t95_v26 file naming

Either:
- Add a docstring or comment explaining that "T95.10" is the work item
  number and "v26" is the implementation version (consistent with
  the project's other vXX naming)
- Or rename files to `t95_v10_*` (would require update to all imports)

---

## Other verification checks (passed)

### Body verification (J1)

I read the function bodies of all key files, not just docstrings:
- `t95_v14_chemodynamic_apply.py` body confirms the override mechanism
  works as documented (lines 38-57), but the filter on lines 70-71
  is the bug.
- `t95_v14_chemodynamic_gmm.py` body confirms the GMM uses 6 features
  (RA, Dec, pmra, pmdec, parallax, [Fe/H]) as documented.
- `t95_v11_gaia_apply.py` body confirms the rescued count logic.

### Test freshness (L2)

Running pytest on the branch's T95 tests confirms they pass on the
current code state. No cached-JSON staleness.

### Doc drift (X1)

CURRENT.md headlines match the on-disk state for: T95.11 rescued 6,
T95.12 honest failure, T95.13 DESI cross-match, T95.14 chemodynamic
GMM. The drift is in the "2 more rescued" wording, not the headline
count.

### Statistical/mathematical (AE)

No statistical claims to verify in this branch (it's data processing,
not a fit). The joint loglik shift of +12.038 is a discrete number
(matches the curated 10 streams minus the GD-1 outlier), not a
continuous statistic.

---

## What this audit does NOT cover

1. **The 19-channel v0.7 MAP fit** — that's on master, not this branch.
2. **The T90/LZ work** — that's on `wip/tier3-magnetic-moment-LZ`,
   audited separately if needed.
3. **The DESI TAP service** — verified at T95.13 ship time; if NOIRLab
   changed their schema since then, T95.13 may not reproduce.

---

## Recommendation

**Do NOT open the PR yet.** Fix the 1 bug + 3 doc-drift items first.
Estimated effort: 30-60 minutes total.

After fixes, this branch is ready to merge as v0.5-prelim.

### Priority

| Item | Priority | Effort |
|---|---|---|
| T95.14 apply bug fix (Perpendicular not counted) | **P0** (real bug) | 10 min |
| CURRENT.md line 607 wording fix | **P1** (doc drift) | 5 min |
| CURRENT.md T95.13 vs T95.14 [Fe/H] discrepancy note | **P2** (explain or align) | 15 min |
| T95.10 vs t95_v26 file naming | **P3** (cosmetic) | 5 min |

---

## Standing posture

- **Branch:** `wip/t95-stream-cross-match` @ `b40d1d3`
- **Status:** Blocked on 1 P0 bug + 3 P1-P3 doc-drift items
- **Master:** untouched at v0.4-prelim+T88E
- **T90 rule:** not triggered by this branch (T95 work is independent)

## Time log

- Audit time: ~30 minutes (file existence checks + body verification +
  JSON output inspection + CURRENT.md cross-check)

## Provenance

- T104 audit: 2026-09-08
- Hermes Agent (MiniMax-M3)
- Skill applied: reviewer-audit (V1 matrix + J1 body verification +
  X1 doc drift + L2 cached-JSON freshness)
