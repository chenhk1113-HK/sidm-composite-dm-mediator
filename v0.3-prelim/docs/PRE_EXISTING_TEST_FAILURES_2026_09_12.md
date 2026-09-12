# Pre-existing test failures — RESOLVED (2026-09-12)

**Status:** RESOLVED. All 3 previously-failing tests were testing **stale assumptions** about channel shapes that had been deliberately changed in earlier sessions. The tests are now updated to match the actual (correct) channel behavior.

**Resolution date:** 2026-09-12

---

## Resolution summary

| # | Test | Original failure | Root cause | Resolution |
|---|---|---|---|---|
| 1 | `test_peak_at_large` | Expected log L > -2 at σ/m=10 (bimodal "large peak") | Channel shape was deliberately replaced 2026-08-17 (R12 P0-D fix); old tests referenced removed bimodal surrogate | Updated tests to reflect actual half-Gaussian upper-limit shape |
| 2 | `test_dip_penalty` | Expected bimodal dip at σ/m=1 | Same as #1 | Same |
| 3 | `test_manifest_total_matches_disk` | Disk 325647 vs manifest 321749 (diff 3898 bytes) | `README.md` added to `data/reference/` per R13 M2 suggestion but manifest tracks only data files | Test now excludes README.md alongside MANIFEST.json |

---

## Resolution 1+2: dSph channel (Horigome+ 2025)

**File:** `tests/test_halo_and_likelihoods.py`
**Test class:** `TestDsphLikelihood`

### What changed

The legacy `test_peak_at_large` and `test_dip_penalty` tests asserted bimodal surrogate behavior (peaks at σ/m ~ 0.1 AND ~10 cm²/g with a dip at σ/m ~ 1). The R12 P0-D fix (2026-08-17, documented in `channels_v03.py` lines 7-13) **deliberately replaced** this bimodal surrogate with a published upper-limit form (Horigome+ 2025).

**The current channel shape** (verified via J1 body verification 2026-09-12):
- Mode at log10(σ/m(v_DSPH)) = -1.3 (σ/m ~ 0.05 cm²/g)
- Capped flat BELOW the mode (no preference for lower σ/m)
- Half-Gaussian RAMP from mode to upper-limit at σ/m = 0.2 cm²/g
- Continues Gaussian penalty ABOVE upper limit
- **No second peak at σ/m = 10; that's now heavy penalty (-4.5)**

### Tests replaced with post-R12 shape

- `test_peak_at_small` → tests mode at σ/m_0=0.05 (log L = 0)
- `test_flat_below_mode` → tests cap below mode (log L = 0 for σ/m_0 < 0.05)
- `test_upper_limit_at_0p2` → tests at Horigome+ 2025 limit (log L = -1.13)
- `test_penalty_above_upper_limit` → tests σ/m_0=10 (log L < -4)
- `test_invalid_returns_neg_inf` (unchanged)
- `test_vdep_a1` → tests v-dep coupling at a=1 (log L = 0 at σ/m_0=0.015)

### Why the original failure was correct

The original tests were testing a surrogate shape that had been **deliberately removed** as incorrect. Per `channels_v03.py` line 89:

> "The legacy surrogate contradicted the Horigome+ 2025 abstract."

The fix to the channel happened, but the tests didn't get updated.

---

## Resolution 3: Reference-chains manifest

**File:** `tests/test_reference_chains.py`

### What changed

The test counted all files in `data/reference/` except `MANIFEST.json`. After `README.md` was added per R13 M2 suggestion (`REVIEWER_AUDIT_R13.md`, 3898 bytes), the disk count exceeded the manifest count by exactly 3898 bytes.

**The fix**: test now excludes both `MANIFEST.json` (self-referential) and `README.md` (documentation, not a data file).

### Why this is the right fix (not modifying the manifest)

- `MANIFEST.json` already excludes itself from `total_bytes` (line 143-144 of test)
- `README.md` is documentation, not a data file — analogous to MANIFEST.json
- The manifest's purpose is to track **data files** with their compression ratios
- Including README.md in the manifest would conflate data and documentation
- The test's intent is "manifest byte count == sum of data file bytes on disk" — README.md is not a data file

---

## Final state after resolution

- **Tests:** 207/207 passing (was 204/207 before resolution)
- **No channel code changed** (R12 P0-D was the right fix; tests just needed updating)
- **No manifest data changed** (just the test exclusion list)
- **No regression risk** (the test changes only update assertions to match the actual channel behavior)

---

## What was learned

1. **Stale tests fail silently** — when channel shapes are intentionally changed, the tests that pinned the OLD shape don't get updated. They sit there failing until someone runs the full suite.
2. **The pre-existing failures were pre-existing because the full suite wasn't being run** — I was running only the 4-5 files I was actively touching.
3. **Both resolutions were honest framing** — the channels were right (R12 P0-D was correct), the manifest was right (tracks data, not docs), the tests were wrong (testing removed behavior).

## Tracking

- **Detected:** 2026-09-12 (full test suite sweep)
- **Verified pre-existing:** 2026-09-12 (via `git checkout HEAD~6`)
- **Documented:** 2026-09-12 (original version of this file)
- **Resolved:** 2026-09-12 (this update)

Reference: commit (this turn) — "fix(tests): resolve 3 pre-existing test failures from R12 P0-D and R13 M2 changes"