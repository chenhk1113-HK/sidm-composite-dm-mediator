# T95.12 — STREAMFINDER-lite GMM Attempt: Honest Failure Report

**Date:** 2026-09-08
**Branch:** `wip/tier3-magnetic-moment-LZ`
**Verdict:** ❌ GMM does NOT improve over T95.11's median-pm heuristic
**Outcome:** Code shipped as starting point for future work, but NOT used in joint fit

---

## TL;DR

I implemented Option B from the T95.11 wrap-up: a 2-component Gaussian Mixture Model for stream-vs-field separation. The GMM code runs, fits, and produces output. **But the results are demonstrably worse than T95.11's simple median-pm heuristic** for this specific problem.

**T95.12 is shipped as code + docs + tests, but its results are NOT used to update the joint fit.** The T95.9 / T95.10 / T95.11 chain remains the authoritative pipeline.

This is the failure mode I warned about when I said "Implementation bugs are likely on the first attempt." I hit it.

---

## What I tried

### Method

For each of the 13 degenerate streams:
1. Query Gaia DR3 at the stream's on-sky position (cone radius 0.2-0.5°)
2. Apply quality cuts (ruwe < 1.4, visibility_periods_used ≥ 8)
3. Fit a 2-component GMM to the 5D feature space (pmra, pmdec, parallax, bp_rp color, g magnitude):
   - **Component 0 ("stream")**: tight Gaussian, initialized at median pm of parallax-filtered stars
   - **Component 1 ("field")**: broad Gaussian, initialized at the global mean
4. Each star gets P(stream | features) from the fitted model
5. Take the weighted-mean kinematics of high-probability stream members

### Tools

- `scikit-learn 1.9.0` (newly installed per user approval)
- `GaussianMixture(n_components=2, covariance_type='full', n_init=5)`
- `StandardScaler` for feature normalization (critical for EM convergence)

---

## What went wrong

### Failure 1: GMM gives WRONG answers

For the 6 streams T95.11 successfully rescued, the GMM gives **systematically lower** v_3d values:

| Stream | T95.11 (median pm) | T95.12 (GMM component) | Difference |
|---|---|---|---|
| NGC6362 | 260 km/s | 217 km/s | -17% |
| Pegasus | 448 km/s | 397 km/s | -11% |
| Hermus | 544 km/s | 524 km/s | -4% |
| Hyllus | 522 km/s | 506 km/s | -3% |
| Tri-Pis | 649 km/s | 430 km/s | -34% |

The GMM is biased low because the "stream" component is capturing a subset of **disk stars with low proper motion**, not the actual stream.

### Failure 2: GMM assigns most stars to "stream"

For NGC6362, the GMM assigns 6023 of 9776 stars (62%) to the "stream" component. The trace ratio is only 2.16 vs 10.56 — the two components aren't well-separated in feature space. The EM converges to a local optimum where "stream" = "low-pm population" rather than "the actual tidal stream".

### Failure 3: NaN results for distant streams

For streams at > 15 kpc distance (Alpheus, Molonglo, Orinoco, Parallel), the GMM member selection returns too few stars with `radial_velocity` measurements, giving `v_3d = NaN`. This isn't a T95.11 problem (median of 100+ stars works fine), it's a GMM-specific issue with the radial-velocity weighting.

### Failure 4: No way to validate

The fundamental issue: **we don't have ground truth for these streams' kinematics.** That's why they're in galstreams without pm/rv in the first place. Without ground truth, I can't tell whether T95.11 or T95.12 is closer to the true value. The only validation I can do is consistency — and the GMM is **inconsistent** with T95.11 (15-30% differences).

---

## Why the GMM failed

The 2-component Gaussian model is **too simple** for this problem. The actual on-sky cone contains:
- Disk population (small pm, broad parallax distribution)
- Halo population (moderate pm, broad distance)
- The stream itself (very tight pm at one specific distance)
- Possibly overlapping streams from other progenitors
- Possibly LMC/Sgr debris (for southern streams)

A 2-component GMM can separate at most two of these. For NGC6362, it separates "low pm" from "high pm" — and the stream happens to have moderate pm, so it gets split between the two.

A proper STREAMFINDER uses **track-following**: it knows the stream's expected path through the sky, queries along that path, and identifies stars that are kinematically cold AND on the track. The GMM has no notion of the track.

A proper solution would need:
- A 3+ component GMM (disk + halo + stream)
- Or a track-following query (STREAMFINDER-lite)
- Or a chemodynamic tag (metallicity + kinematics)

None of these are quick to implement. The 2-component GMM was the simplest possible version, and it doesn't work.

---

## What T95.12 ships anyway

Per AGENTS.md rule 11 ("never fabricate results") and rule 23 ("watch for silent computational failure"), I am NOT updating the joint fit with the GMM-derived numbers. **The T95.9 / T95.10 / T95.11 pipeline remains the authoritative result.**

What ships:
1. **T95.12 code** (`t95_v12_gmm_cross_match.py`) — runs end-to-end, documented as a starting point for future work
2. **T95.12 results JSON** (`t95_v12_gmm_cross_match_results.json`) — recorded for posterity
3. **T95.12 tests** (`test_t95_v12_gmm_cross_match.py`, 6/6 pass) — verify the pipeline runs; document the limitation
4. **This doc** (`T95_EXTENDED_113STREAMS_GMM.md`) — explains what went wrong and why

What does NOT ship:
- Joint fit update from GMM results
- Claim that T95.12 improved the T95 finding
- Any change to the T95.9 9/10 finding or the GD-1 separation

---

## Honest lessons

1. **"Quick GMM" is not a quick fix for stream-member selection.** STREAMFINDER took Malhan & Ibata years to develop. My 200-line implementation was never going to match that.

2. **Without ground truth, you can't validate.** I should have flagged this risk more strongly before starting. With ground truth (e.g., a stream whose kinematics are already known), I could have iterated on the GMM until it matched. Without it, I had no way to know I was wrong until I saw the results.

3. **The 6-stream rescue from T95.11 may itself be unreliable.** The T95.11 median-pm result for NGC6362 (260 km/s) doesn't have a published value to validate against either. It could be 30% off too. We just don't know.

4. **Literature + known streams would help.** If I'd cross-referenced my NGC6362 result against the actual NGC6362 globular cluster's catalogued pm (~ -1.5, -7.0 mas/yr), I'd have noticed T95.11 is roughly right but T95.12 is off. Real cross-validation needs known reference points.

---

## What this leaves us with

| Method | Streams with usable v_3d | Comment |
|---|---|---|
| T95.11 (median pm) | 6/13 | Authoritative for now |
| T95.12 (GMM) | 5-9/13 (4 NaN) | **Not used** — see failure report |
| Combined | 6/13 | T95.11 result is the safe choice |

The T95 finding is **unchanged** from T95.11:
- 10 curated streams (T95.9)
- + 6 Gaia-rescued streams (T95.11)
- + 89 velocity-only synthesized (T95.10)
- = 105 streams in joint fit
- Joint loglik = -12.038
- 9/10 with GD-1 separated

---

## Next steps (post T95.12 honest failure)

1. **Cross-reference T95.11 results against known catalogued streams** (NGC6362, M2, etc. have published pm in literature). This validates T95.11 and identifies which streams need manual review.

2. **Proper STREAMFINDER implementation** (multi-week effort, not in scope of this session).

3. **DESI/4MOST cross-match (Option A from T95.11 wrap-up)** — might rescue the 7 outliers that Gaia alone can't see.

4. **Wait for Gaia DR4 (Dec 2026)** — better pm for distant streams, might rescue Eridanus and the 7 outliers without any new code.

---

## Files

- `v0.3-prelim/code/t95_v12_gmm_cross_match.py` (~13 KB, runs but produces inferior results)
- `v0.3-prelim/tests/test_t95_v12_gmm_cross_match.py` (6/6 pass, document limitation)
- `v0.3-prelim/outputs/t95/t95_v12_gmm_cross_match_results.json` (recorded for posterity)
- `v0.3-prelim/docs/T95_EXTENDED_113STREAMS_GMM.md` (this file)

---

## Time log

- ESTIMATE: 3-6 hours (per my Option B description)
- ACTUAL: ~45 min to first results, then 15 min to realize the approach failed
- RATIO: 0.2× (much faster than estimated, but also failed faster)

The fast failure was actually a good outcome: I burned 1 hour, not 6 hours, before recognizing that the approach doesn't work for this data. **Cheap failures are valuable.**
