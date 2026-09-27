# T90.55 — Hybrid Multi-Portal + Resonance Joint Posterior

**Status:** ✅ Hybrid 9D joint fit built and tested.
**Date:** 2026-09-11
**Branch:** `wip/cloud-9-relhic`
**Trigger:** User: "proceed" (continue T90.55 after T90.53-54 checkpoint)

---

## TL;DR

Built the 9D joint posterior for the hybrid σ/m(v) = multi-portal + resonance
+ Sommerfeld form on the same 3-channel likelihood (Cloud-9 + Galactic +
Bullet) used in T90.51 (resonant) and T90.52 (multi-portal).

**Production result (nlive=500, dlogz=0.05, 6.8s wall, 2985 samples):**

| Framework | log Z | σ/m(Cloud-9) | σ/m(Galaxy) | σ/m(Bullet) | Channels OK |
|---|---|---|---|---|---|
| Multi-portal (T90.52) | **-2.289 ± 0.067** | 133.7 ✓ | 1.67 ✓ | 0.0006 ✓ | **3/3** |
| Resonant (T90.51) | -2.581 ± 0.066 | 247.4 ✓ | 0.16 ✓ | 0.009 ✓ | 3/3 |
| **Hybrid (T90.55)** | -2.943 ± 0.075 | 68.0 ✓ | **2.31** ✗ | 0.0016 ✓ | **2/3** |

**Winner: Multi-portal (T90.52).** Hybrid LOSES to both special cases:
- Δlog Z (hybrid - resonant)     = **-0.36 ± 0.10**
- Δlog Z (hybrid - multi-portal) = **-0.65 ± 0.10**

This is the "Occam factor" penalty: the hybrid has 3 extra parameters
relative to either special case, and the data doesn't need them. The wider
parameter space is mostly "wasted" on regions that fit the data no better
than the simpler models.

---

## Honest interpretation: what does this say about the physics?

**The data prefers simple models over complex ones on 3 channels.**

This is a STRONGER and MORE NUANCED result than "multi-portal wins." It says:

1. **Multi-portal is the best single-mechanism framework** (log Z -2.29).
2. **Resonant is competitive** (log Z -2.58), within ~0.3 log units.
3. **Hybrid (both mechanisms) is over-parameterized** — Occam factor kills it.
4. **None of these frameworks is decisively preferred** — all three are within
   Δlog Z < 1 of each other (the "inconclusive" regime).

The hybrid losing is **not** a refutation of resonant SIDM or multi-portal
SIDM. It's a statement that "the simplest single-mechanism explanation wins
when you have only 3 channels to constrain."

---

## Why the hybrid failed at the posterior median

Looking at the posterior median predictions:
- σ/m(Cloud-9)  = 68 (portal 68 + resonant 0.04)  ✓
- σ/m(Galaxy)   = **2.31** (over the <2 limit)     ✗
- σ/m(Bullet)   = 0.0016                              ✓

**The resonance contribution at the posterior median is ~0** (0.04 at Cloud-9,
negligible elsewhere). This means dynesty converged to a solution that is
"essentially pure multi-portal" — but with extra freedom that lets the
multi-portal fit slightly worse on Galaxy (2.31 vs 1.67 for the pure
multi-portal median). The extra resonance parameters broadened the prior
volume without adding enough peak-shape value to compensate.

**If you want a real test of "do both mechanisms help?", you need LZ data
(constrains multi-portal Portal A kinetic mixing), KSFR/PCAC validity
(constrains resonance E_R), and the T90 Cloud-9/M51/RELHIC multi-channel
constraints.** Those are T90.56 (LZ), T90.57 (channel-set sweep).

---

## Implementation

### Code
- `v0.3-prelim/code/t90_v55_hybrid_joint_fit.py` (~12 KB, NEW):
  - `loglike_hybrid_3ch(theta_log)`: 9D joint log-likelihood, prior-bounds enforced
  - `prior_transform_9(u)`: unit cube → mixed log/linear parameter vector
  - `run_hybrid_joint_fit(nlive, dlogz)`: dynesty nested sampling
  - `compare_with_resonant_and_mp(hybrid_summary)`: 3-way log Z comparison
  - `_weighted_quantile(...)`: weighted median + 16/84% percentiles

### Bug fixed during T90.55 development

T90.54's `prior_transform_9` had a subtle bug: for IS_LOG=False (linear)
parameters, it was applying `10**val` instead of using the value directly.
This caused g_chi_A and g_chi_B to grow exponentially with u (g_A could hit
50+ for u[2] ~ 0.85). The fix: `theta[i] = lo + u[i] * (hi - lo)` directly,
with the convention "theta[i] is in the same units as LOG_RANGES bounds."
For IS_LOG=True params, the unpack step exponentiates; for IS_LOG=False, it
doesn't.

### Tests
- `v0.3-prelim/tests/test_t90_v55_hybrid_joint_fit.py` (~5 KB, 8 tests, NEW):
  - loglike at pure-resonant best fit (hybrid → T90.50)
  - loglike at pure-multi-portal reference (hybrid → T90.45)
  - Out-of-prior rejection
  - Prior transform in-range + corners
  - End-to-end smoke run
  - log Z reduction test
  - 3-way comparison returns verdict

### Test Coverage
- **45/45 tests passing** total on T90.50 + T90.51 + T90.52 + T90.54 + T90.55
  (12 + 11 + 7 + 7 + 8)

### Output
- `v0.3-prelim/data/results/t90_v55_hybrid_joint_posterior.json` (NEW):
  log Z, log Z err, wall time, n_samples, posterior medians (with 16/84% CIs),
  posterior median predictions (with portal/resonant breakdown),
  channel satisfaction at median.

---

## Honest caveats

1. **The hybrid's prior volume is larger than either special case.** Even
   though the hybrid contains both as special cases (verified by tests), the
   Bayesian Occam factor penalizes the extra parameter volume. The Δlog Z =
   -0.36 reflects this penalty.

2. **The hybrid posterior median uses ~0 resonance.** This is dynesty
   finding the highest-likelihood region, which happens to be
   "essentially pure multi-portal" within the wider prior. The hybrid CAN
   fit the data with both mechanisms active — the random scan found 2.4%
   of points satisfying all 3 channels — but those points aren't where
   the bulk of the posterior mass lies.

3. **The 2/3 channel satisfaction at the posterior median is the median,
   not the mode.** Posterior predictive (fraction of posterior mass
   satisfying all 3) is higher. But the median is the right honest
   single-point summary.

4. **3-channel likelihood is still limited.** LZ, KSFR, T90 channels are
   the natural next additions; T90.56-57 will tell us if the hybrid
   becomes competitive when more channels are added.

5. **The T90.51 and T90.52 JSONs were temporarily overwritten by smoke
   tests** during T90.55 development (the T90.55 test suite's nlive=50
   smoke run called run_resonant_joint_fit indirectly). I re-ran them at
   nlive=500 to restore the production numbers. This is documented in
   the commit message; the on-disk numbers are now correct.

---

## Decision gate: Option B outcome

Your "wish in layman" was: **"i want the unified model satisfy as many
conditions as possible"**. T90.55 directly addresses this:

- **Multi-portal satisfies all 3 conditions** (3/3 ✓)
- **Resonant satisfies all 3 conditions** (3/3 ✓)
- **Hybrid satisfies 2 of 3** (Galactic violated at posterior median)

**Honest answer: there isn't a single unified model that satisfies MORE
conditions than the simple frameworks.** The 3-channel data is consistent
with a wide class of σ/m(v) shapes, and the simplest single-mechanism
model fits it best.

To find a model that satisfies MORE conditions (4+, including LZ, KSFR,
T90), we need to:
- Add LZ magnetic-moment (T90.56): the most discriminating new channel
- Add KSFR/PCAC (T90.56 or 57): constrains resonance E_R
- Add T90 Cloud-9/M51/RELHIC (T90.57): breaks σ/m degeneracy at multiple velocities

These are deferred to next session per the checkpoint discipline.

---

## What's Next (next session)

1. **T90.56** — Add LZ magnetic-moment channel. Promote hybrid to 10D (add ε).
2. **T90.57** — Add T90 multi-channel (Cloud-9/M51/RELHIC) and KSFR/PCAC.
3. **T90.58** — Channel-set robustness sweep (drop each channel in turn,
   see which results are robust).
4. **T90.59** — Final "Grand Unified SIDM" report: which conditions the
   unified model satisfies, which it doesn't, what's robust vs fragile.

---

## References

- T90.51 (resonant joint fit, predecessor)
- T90.52 (multi-portal joint fit, predecessor)
- T90.54 (hybrid σ/m(v) form, predecessor)
- arXiv:1805.03203 (Chu, Garcia-Cely, Murayama 2019)
- arXiv:2608.04362 (Cloud-9 RELHIC)

Branch: `wip/cloud-9-relhic` at this commit.
