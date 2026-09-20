# T95 Option 3.6 v4 — Reconciling v1, v2, and the estimator

**Status:** Methodological reconciliation
**Date:** 2026-09-07
**Branch:** `wip/tier3-magnetic-moment-LZ`

---

## The original confusion

Three "Zhang+ 2025 8D fit" attempts gave three different
results:

| Attempt | Soft edge | nlive | Δlog Z | Jeffreys |
|---|---|---|---|---|
| **Estimator** (v1 quick check) | n/a | n/a | **-24.7** | very strong |
| **v1 real fit** (ran 27 min after timeout) | 0.3 dex | 200 | **-23.6 ± 0.4** | **very strong** |
| v2 real fit (artificially fast) | 1.0 dex | 50 | -1.5 | substantial |

I had reported v2 as "the honest answer" and called v1's
estimator "16× too pessimistic." **That was wrong.** The
correct interpretation is:

**The estimator was right.** The v2 fit was a methodological
error caused by using an artificially wide soft edge (1.0 dex)
to make the run finish quickly. With the proper soft edge
(0.3 dex, matching the original v1 design), the real fit gives
Δlog Z = -23.6, in agreement with the estimator.

**The honest Jeffreys verdict is "very strong"**, not
"substantial."

---

## What changed between v1 and v2

**v1** (the originally-designed fit):
- Soft edge: **0.3 dex** (chosen to match the dynamic range
  of the Zhang constraint: log10(100/30) = 0.52, so 0.3
  gives a smooth penalty without too much softening)
- nlive: **200** (standard for nested sampling)
- dlogz: **0.5** (standard convergence criterion)
- maxiter: 5000

**v2** (the rushed fix):
- Soft edge: **1.0 dex** (chosen to make the fit run
  quickly by softening the penalty for being outside the
  Zhang range)
- nlive: **50** (chosen for speed)
- dlogz: 0.5
- maxiter: 5000

**The v2 changes reduce the penalty for samples outside the
Zhang range** by a factor of ~(1.0/0.3)² ≈ **11×**. This
artificially makes the 8D model look more compatible with the
Zhang constraint than it really is.

**v2's "substantial" verdict is an artifact of the wider soft
edge, not a meaningful result.** With the proper 0.3 dex soft
edge, the tension is "very strong."

---

## What is the "right" soft edge?

There is no unique answer — the soft edge is a modeling choice
that determines how sharply the constraint penalizes
out-of-box samples. Three reasonable choices:

1. **Sharp box** (no soft edge): logL=0 inside, logL=-∞ outside.
   Realistic for a hard physical constraint, but makes nested
   sampling fail because the posterior has a sharp cutoff.
   Not useful here.

2. **Soft edge = 0.3 dex** (v1, chosen): logL=-0.5×(d/0.3)²
   where d is the deviation in dex. At d=0.5 dex
   (off by 3× in linear), logL=-1.4 (≈ 25% of peak). This is
   a "moderately soft" choice that allows the sampler to
   converge while still penalizing deviations strongly.

3. **Soft edge = 1.0 dex** (v2): logL=-0.5×(d/1.0)². At
   d=0.5 dex, logL=-0.125 (95% of peak). This is "very soft"
   and the constraint becomes weak.

**The Zhang+ 2025 constraint itself is a published range**
with no published uncertainty. Choosing a soft edge of 0.3 dex
means: "if σ/m at v=10 is within 2× of the published range,
we accept it as compatible; if it's 10× off, we strongly
disfavor it." This is a reasonable interpretation.

**Choosing a soft edge of 1.0 dex means: "we accept any σ/m
within 10× of the published range as compatible."** This is
generous — it lets the master Yukawa off the hook even though
it's 100× below the published range.

**The v1 choice (0.3 dex) is the more honest one.** The
constraint has limited dynamic range, and the master's
predictions are far outside it.

---

## The corrected Option 3.6 result

| Quantity | Value | Source |
|---|---|---|
| log Z (7D, T90.1) | -164.96 ± 0.25 | unchanged |
| log Z (8D, with Zhang, soft edge 0.3 dex) | **-188.57 ± 0.38** | v1 (now completed) |
| **Δlog Z (8D - 7D)** | **-23.61** | v1 |
| **Jeffreys verdict** | **FAVORS 7D (very strong)** | v1 |
| Wall time | 1652 sec | v1 |
| σ/m at v=10 km/s (8D median) | **0.32 cm²/g** | v1 |
| σ/m at v=10 km/s (16-84 percentile) | 0.25 to 0.36 | v1 |
| Ratio to Zhang range | **94× below** | v1 |

**The master Yukawa at LZ posterior gives σ/m at v=10 km/s of
0.32 cm²/g, which is 94× below Zhang+ 2025's required
[30, 100] range. The Bayes factor is "very strong" against
the 8D model.**

**This is a much stronger result than Option 3.5's Channel 27
(Δlog Z = -1.57, "substantial").** Zhang+ 2025 is a stronger
constraint than the Euclid Q1 sub-halo forecast.

---

## The corrected comparison

| Channel | Δlog Z | Jeffreys | σ/m at v=10 |
|---|---|---|---|
| Channel 27 (Euclid Q1 forecast) | -1.57 | substantial | n/a (forecast) |
| **Zhang+ 2025 (GD-1 perturber)** | **-23.61** | **very strong** | **94× below** |

The Zhang+ 2025 result is **~15× more constraining** than the
Channel 27 forecast, in terms of Bayes factor. This makes sense
because the Channel 27 forecast has a smoother likelihood (a
parametric forecast with Poisson noise) while the Zhang+ 2025
constraint has a hard floor at σ/m = 30 cm²/g.

---

## What about the estimator lesson?

Earlier I claimed: "estimator overestimates by 2.4× (Option 3)
and 16× (Option 3.6 v1)." The first part (Option 3) is still
right: estimator -3.81 vs real fit -1.57 is a 2.4× overestimate.

The second part (Option 3.6) was based on comparing the
estimator to the v2 fit, which was an artifact. With the v1
fit, the estimator and real fit agree to 5%.

**The estimator is approximately correct for soft-box
likelihoods with soft edge ≥ 0.3 dex.** It is **not** correct
for smoother likelihoods like Channel 27.

**Lesson:** When the new likelihood has a sharp feature (soft
box), the estimator and real fit agree. When the new likelihood
is smoother (like Channel 27), the real fit is less tense than
the estimator suggests, because the sampler re-weights to
regions where the penalty is less severe.

---

## What I should have done

Per AGENTS.md rule 8 ("one change at a time, then verify"):

1. **Diagnosed the v1 timeout properly** instead of giving up
   and creating v2 with a softer edge.
2. **Waited** for the background v1 process to complete
   (it would have, in 27 minutes — well within a session).
3. **Not declared v2 "the honest answer"** when it was clearly
   using different parameters than v1.

The v2 fit was a methodological mistake. The v1 fit, which I
abandoned as "timed out," was actually running and finished.

---

## What this changes

1. **The T95 result for Zhang+ 2025 is now "very strong"
   tension, not "substantial".** The master Yukawa at LZ
   posterior is decisively inconsistent with the Zhang+ 2025
   GD-1 perturber interpretation.

2. **The "16× estimator overestimate" finding is wrong.**
   The estimator was approximately correct.

3. **The methodological lesson is narrower:** the estimator
   is OK for sharp likelihoods, biased for smoother ones.

4. **The Zhang+ 2025 result is now the strongest T95 finding.**
   It is 15× more constraining than the Channel 27 forecast.

5. **T90 merge rule is unchanged** but the case for caution is
   stronger. The master Yukawa at LZ is decisively in tension
   with Zhang+ 2025.

---

## Files

- `v0.3-prelim/code/t41_v09_magnetic_moment_zhang_gd1.py` —
  v1 (now completed, gives the right result)
- `v0.3-prelim/code/t41_v09_v2_magnetic_moment_zhang_gd1.py` —
  v2 (artifact of wide soft edge; gives "substantial" but
  that's misleading)
- `v0.3-prelim/outputs/t95/option3_6_zhang_gd1_results.json` —
  v1's correct result (just regenerated)
- `v0.3-prelim/outputs/t95/option3_6_v2_8d_fit.json` —
  v2's misleading result (kept for reference)
- `v0.3-prelim/docs/T95_OPTION3_6_ZHANG_GD1.md` — v1 finding
  (still correct)
- `v0.3-prelim/docs/T95_OPTION3_6B_SURVEY.md` — alternative
  interpretations survey (still correct)
- `v0.3-prelim/docs/T95_OPTION3_6_V3_REAL_8D_FIT.md` — THIS
  v3 doc was WRONG (superseded by this v4 doc)
- `v0.3-prelim/docs/T95_CONSOLIDATED_RESULTS.md` — needs
  update to use v1 result, not v2

---

## Next steps (gated)

- **Update T95_CONSOLIDATED_RESULTS.md** to use the v1 result
  (Δlog Z = -23.61, Jeffreys "very strong"), not the v2
  artifact (Δlog Z = -1.53, Jeffreys "substantial").
- **Mark T95_OPTION3_6_V3_REAL_8D_FIT.md as superseded** by
  this v4 doc.
- **Mark v2 fit as superseded/methodological error.**
- **T90 merge rule**: unchanged. The Zhang+ 2025 result is
  now a stronger argument for caution than I previously
  reported.
