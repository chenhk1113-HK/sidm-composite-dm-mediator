# Pre-existing test failures (2026-09-12 snapshot)

**Status:** DOCUMENTED, not addressed. These failures pre-date the ch04 width fix and the AMUSE validation work in this session. They require separate investigation.

**Verified pre-existing:** `git checkout HEAD~6` (pre-ch04-fix commit `f16bdc2`) reproduces all 3 failures. Therefore they are NOT caused by commits 24c908b, 67b92a5, a24733b, a44ef3e, or d5738a7.

---

## Failure 1: `test_peak_at_large`

**File:** `tests/test_halo_and_likelihoods.py`
**Test class:** `TestDsphLikelihood::test_peak_at_large`
**Symptom:**
```
AssertionError: log L at large peak should be > -2 (it's a peak), got -4.525
```

**What the test expects:** dSph channel should have a "large peak" at σ/m=10 cm²/g where log L > -2 (it's a peak).

**What it gets:** log L = -4.525 at σ/m=10. There's no peak there in the current channel.

**Likely root causes (not investigated):**
1. The test was written assuming a particular dSph likelihood shape (e.g., bimodal with peaks at 0.1 and 10) but the current `channels_v03.loglike_dsph_v03` is unimodal/uninformative.
2. Or the test expectation was correct when written but the channel was later changed without updating the test.

**Recommended next step:** Look at `v0.3-prelim/code/channels_v03.py::loglike_dsph_v03` to see the actual shape. Compare to git history for `channels_v03.py` to see when the shape changed (if ever).

---

## Failure 2: `test_dip_penalty`

**File:** `tests/test_halo_and_likelihoods.py`
**Test class:** `TestDsphLikelihood::test_dip_penalty`
**Symptom:**
```
AssertionError: dip should be < large peak: dip=-2.525, large=-4.525
```

**What the test expects:** dSph channel should be a bimodal exclusion: log L(σ/m=1) < log L(σ/m=0.1) AND log L(σ/m=1) < log L(σ/m=10).

**What it gets:** log L(dip=1) = -2.525 > log L(large=10) = -4.525. The "large peak" is actually worse than the "dip" — there's no peak at 10 in the current channel.

**Likely root cause:** Same as Failure 1 — dSph channel doesn't have the expected bimodal shape.

**Recommended next step:** Same as Failure 1.

---

## Failure 3: `test_manifest_total_matches_disk`

**File:** `tests/test_reference_chains.py`
**Test class:** `TestReferenceDataBudget::test_manifest_total_matches_disk`
**Symptom:**
```
AssertionError: Disk total 325647 != manifest total 321749
```

**What the test expects:** The reference data manifest's total byte count matches the on-disk total.

**What it gets:** Disk total is 325,647 bytes vs manifest's 321,749 bytes. Off by 3,898 bytes (1.2%).

**Likely root causes:**
1. New reference data files were added without updating the manifest.
2. Existing files were modified (sizes changed) without updating the manifest.
3. Test was written against an older snapshot and the data has evolved since.

**Recommended next step:**
- Look at `tests/test_reference_chains.py` to find what file is the manifest.
- Compare manifest entries to `ls -la data/reference/` or equivalent.
- Either update the manifest (if files genuinely changed) or fix the test (if it's checking the wrong path).

---

## Why these are NOT urgent

- All three failures pre-date the 2026-09-12 work in this session.
- They don't block the ch04 fix, the AMUSE validation, or the placeholder decision.
- The two `test_halo_and_likelihoods` failures are in a slow-changing channel (`channels_v03.py`) that hasn't been touched in this session.
- The `test_reference_chains` failure is a manifest-vs-disk byte count discrepancy, not a data integrity issue.

## When to address them

- **Failure 1+2 (dSph):** When someone is actively working on the dSph channel or adding new physics to it.
- **Failure 3 (manifest):** When someone is curating the reference data archive.

## Tracking

- Detected: 2026-09-12 (full test suite sweep)
- Verified pre-existing: 2026-09-12 (via `git checkout HEAD~6`)
- Documented: 2026-09-12 (this file)
- Addressed: deferred

Reference: commit `d5738a7` ("test: update test_lens_subhalo_channel to match ch04 width revision") which fixed the ONLY regression caused by this session.