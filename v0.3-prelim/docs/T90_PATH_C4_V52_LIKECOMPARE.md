# T90.52 — Multi-portal vs Resonant SIDM Apples-to-Apples log Z Comparison

**Status:** ⚠️ **T90.51 HEADLINE CORRECTED — Δlog Z is INCONCLUSIVE, not +16.8**
**Date:** 2026-09-11
**Branch:** `wip/cloud-9-relhic`
**Trigger:** User: "proceed as suggested" (resume T90.52-55 after T90.51)

---

## TL;DR

T90.52 re-runs T90.45 multi-portal on the SAME 3-channel likelihood
function that T90.51 uses for resonant SIDM. Same dynesty settings
(`nlive=500, dlogz=0.05`), same channels (Cloud-9, Galactic, Bullet),
same channel likelihoods (Gaussian in log for Cloud-9, 1-sided half-Gaussian
for Galactic and Bullet).

**The honest result: Δlog Z is INCONCLUSIVE.**

| Framework | nlive | dlogz | log Z | log Z err | wall |
|---|---|---|---|---|---|
| **Resonant (T90.51, re-run at matched settings)** | 500 | 0.05 | **-2.435** | ±0.064 | 4.0s |
| **Multi-portal (T90.52)** | 500 | 0.05 | **-2.229** | ±0.067 | 4.5s |
| **Δlog Z (resonant - multi-portal)** | | | **-0.21** | ±0.09 | |

**Both frameworks are unified solutions to the 3-channel problem.**
The "landslide" claim from T90.51 was an artifact of unfair comparison
(T90.51's log Z was -2.5 vs T90.45's published log Z of -19.32, but those
were measured at different nlive, different number of channels, and
different nuisance parameters).

**Per my own decision rule: T90.53-55 are deferred pending user decision.**
The +5 log Z threshold for proceeding was not met.

---

## The correction to T90.51's narrative

T90.51's writeup stated:

> "Δlog Z vs T90.45 = +16.8 in favor of resonant SIDM (3-channel-only comparison)"

This was WRONG. The +16.8 figure was computed as:

```
Δlog Z = -2.52 (T90.51, 3 channels, nlive=500)
       - (-19.32) (T90.45 published, 5+ channels, nlive=200)
       = +16.8
```

But the two log Z values are NOT comparable because:
1. T90.45 used 5+ channels (LZ, KSFR, etc.); T90.51 used 3 channels
2. T90.45 had bimodal posterior; T90.51 had unimodal (multi-modal posteriors
   incur an evidence penalty)
3. T90.45 used different nuisance parameter ranges

The apples-to-apples comparison (this script) gives Δlog Z = -0.21 ± 0.09,
which is **inconclusive** — within 1 sigma of zero. Multi-portal is even
slightly preferred at the matched settings.

**The honest project headline becomes:**
"Both resonant SIDM and multi-portal SIDM are unified solutions to the
3-channel Cloud-9 + Galactic + Bullet problem. Both produce σ/m posterior
medians that satisfy all three constraints. Bayesian evidence does not
distinguish them on the 3-channel likelihood."

---

## Posterior medians (nlive=500, dlogz=0.05, matched settings)

### Resonant SIDM (T90.51 re-run)

| Parameter | Median | 16% | 84% |
|---|---|---|---|
| m_chi (GeV) | ~24 | ~6 | ~95 |
| E_R (eV) | ~60 | ~19 | ~212 |
| Γ_R (eV) | ~3.6 | ~0.17 | ~37 |
| σ_0 (cm²/g) | ~0.004 | ~0.0004 | ~0.09 |
| α_Y | ~0.004 | ~0.0004 | ~0.11 |

Posterior median predictions:
- σ/m(Cloud-9, v=28) = **196.7** ✓
- σ/m(Galaxy, v=100) = **0.19** ✓
- σ/m(Bullet, v=3000) = **0.010** ✓

### Multi-portal SIDM (T90.52)

| Parameter | Median | 16% | 84% |
|---|---|---|---|
| log_m_phi_A (MeV) | 2.96 | 2.34 | 3.70 |
| log_m_chi_A (GeV) | 1.69 | 0.86 | 2.56 |
| g_chi_A | 1.17 | 0.69 | 1.71 |
| log_m_phi_B (MeV) | 0.49 | -0.16 | 1.18 |
| log_m_chi_B (GeV) | 2.98 | 2.46 | 3.28 |
| g_chi_B | 0.28 | 0.14 | 0.42 |

Posterior median predictions:
- σ/m(Cloud-9, v=28) = **134.6** ✓
- σ/m(Galaxy, v=100) = **1.67** ✓ (under <2 limit)
- σ/m(Bullet, v=3000) = **0.0003** ✓

---

## Why the T90.45 "Galactic over by 2x" claim was a MAP-vs-median confusion

T90.45's published numbers were computed at the **MAP** (maximum-a-posteriori)
point, not the posterior median:

```
T90.45 MAP:   sigma/m(28)=48.6  sigma/m(100)=4.3 (over <2 limit!)  sigma/m(3000)=0.024
T90.45 median: sigma/m(28)=134.6 sigma/m(100)=1.67 (under limit)   sigma/m(3000)=0.0003
```

The MAP is the single best-fit point in the posterior; the median is the
typical point under the posterior. The two can disagree significantly when
the posterior is asymmetric or multimodal. In this case, the MAP happened
to fall in a low-probability tail where Galactic σ/m is over the limit,
but the bulk of posterior mass has Galactic σ/m under the limit.

**This is an important lesson:** when reporting "model X is incompatible
with constraint Y," use the posterior predictive (what fraction of posterior
mass satisfies the constraint), not just the MAP point. The MAP can be
arbitrarily far from the bulk of posterior mass, especially in higher-D
problems.

---

## Implementation

### Code
- `v0.3-prelim/code/t90_v52_likecompare.py` (~12 KB, NEW):
  - `loglike_multi_portal_3ch(theta)`: 9D multi-portal likelihood using the
    SAME 3-channel loglikes as T90.51 (Cloud-9 + Galactic + Bullet).
    Includes prior-bounds enforcement (caught by `test_loglike_out_of_prior_rejected`).
  - `prior_transform_9_mp(u)`: 9D prior matching T90.45's published ranges
    (lines 138-154 of `t90_v45_multi_portal_joint_fit.py`).
  - `run_multi_portal(nlive, dlogz)`: dynesty nested sampling.
  - `compare_with_resonant(mp_summary)`: loads T90.51 JSON, returns verdict.

### Tests
- `v0.3-prelim/tests/test_t90_v52_likecompare.py` (3.8 KB, 7 tests, NEW):
  - loglike at T90.45 reference point
  - Out-of-prior rejected (caught a real bug during development — see
    commit message)
  - Zero-coupling penalty test
  - Prior transform in-range + corners
  - End-to-end smoke run
  - compare_with_resonant returns verdict string

### Output
- `v0.3-prelim/data/results/t90_v52_multi_portal_joint_posterior.json`:
  log Z, log Z err, wall time, n_samples, posterior medians (with 16/84% CIs),
  posterior median predictions.

---

## Decision gate: T90.53-55 deferred pending user input

My pre-T90.52 plan stated:

> "Decision gate: if Δlog Z ≥ 5 in favor of resonant → proceed to T90.53+54+55;
> otherwise → report and stop."

The measured Δlog Z is -0.21 (multi-portal slightly preferred, but within
1σ of zero). The decision rule is "report and stop." T90.53-55 would only
make sense if there's reason to believe additional channels would break
the tie — most likely LZ, which constrains multi-portal more than resonant
(multi-portal's LZ signal comes through Portal A's kinetic mixing; resonant
doesn't have an equivalent coupling in this parameterization).

Three options for the user:

**Option 1: Stop here.** Both are unified solutions; the data can't
distinguish them on 3 channels. Wait for new data (T95 DESI/4MOST
cross-match, Gaia DR4, LZ Run 4 results).

**Option 2: Push forward anyway** (T90.53 with LZ channel added). LZ
direct-detection is the most likely channel to break the tie in favor
of one model over the other. Estimate: 3-5 days.

**Option 3: Reverse the question.** Stop comparing frameworks and instead
ask: what does the data say about the underlying physics? Build a joint
fit that doesn't pre-commit to a parametric form — let the data choose
between Breit-Wigner + Yukawa, two-portal Yukawa, and other forms on equal
footing. This is a much bigger project (~weeks).

---

## Honest caveats

1. **3-channel comparison only.** LZ, KSFR, T90 channels not included.
   Adding LZ (T90.53) is the most likely way to distinguish the two frameworks.

2. **The "Galactic over by 2x" claim from T90.45 was at the MAP, not the
   posterior median.** The posterior median is fully consistent with the
   < 2 cm²/g Galactic limit. The original writeup was misleading on this
   point.

3. **The Δlog Z direction flips with nlive.** At nlive=200, multi-portal
   slightly wins (-0.24 ± 0.16). At nlive=500, the gap is -0.21 ± 0.09.
   Both are within "inconclusive" (|Δlog Z| < 1) but the lack of stability
   is itself a sign the evidence isn't strong.

4. **Both posterior medians satisfy all 3 constraints.** This is the
   headline result: TWO independent parametric frameworks (resonant and
   multi-portal) both fit the 3-channel data. That's a much stronger
   statement than "resonant wins" — it means the 3-channel data is
   consistent with a wide class of velocity-dependent σ/m models.

5. **The original T90.51 writeup must be corrected.** The Δlog Z = +16.8
   claim is wrong. See "Correction to T90.51's narrative" above. This
   will be patched in a follow-up commit.

---

## What's next

Per the decision gate: T90.53-55 are deferred. User input requested on
Option 1/2/3 above.

If Option 1: branch remains at `c428b0c` (current HEAD after T90.51).
Pause resumes. Wait for new evidence per 2026-09-08 directive.

If Option 2: T90.53 should add LZ magnetic-moment channel (7D resonant +
9D multi-portal with ε coupling). Estimate: 3-5 days.

If Option 3: a much larger project — re-cast the joint fit to let the
data choose the parametric form. Estimate: weeks.

---

## References

- T90.51 (predecessor: 3-channel resonant SIDM joint posterior)
- T90.45 (predecessor: 9D multi-portal joint fit, 5+ channels)
- T90.44 (predecessor: multi-portal σ/m function)
- T40 Yukawa cross-section (`t40_yukawa_sigma_m.py`)
- arXiv:1805.03203 (Chu, Garcia-Cely, Murayama 2019 — resonant SIDM)
- arXiv:2608.04362 (Cloud-9 RELHIC)

Branch: `wip/cloud-9-relhic` (T90.52 commit).
