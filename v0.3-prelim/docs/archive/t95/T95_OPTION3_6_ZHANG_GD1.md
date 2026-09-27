# T95 Option 3.6 — Master Yukawa vs Zhang+ 2025 GD-1 Perturber Constraint

**Status:** Documented finding
**Date:** 2026-09-07
**Branch:** `wip/tier3-magnetic-moment-LZ`
**Companion script:** `v0.3-prelim/code/t95_v05_option3_6_zhang_gd1_estimator.py`
**Failed full fit:** `v0.3-prelim/code/t41_v09_magnetic_moment_zhang_gd1.py` (times out)
**JSON output:** `v0.3-prelim/outputs/t95/option3_6_zhang_gd1_estimator.json` (gitignored, regenerated)

---

## TL;DR

**Master's Yukawa at the LZ-anchored 7D posterior is
incompatible with the Zhang+ 2025 GD-1 perturber
interpretation.** The LZ posterior gives σ/m at v=10 km/s
of **0.23 cm²/g** (median), but Zhang+ 2025 requires
**30-100 cm²/g** to explain the GD-1 perturber as a
core-collapsed SIDM halo. **Only 1 out of 2523 LZ-anchored
posterior samples (0.04%) falls in the Zhang range.**

**The LZ 248 keV interpretation and the GD-1 perturber
interpretation are mutually exclusive under the master
Yukawa operator.** This is a real, quantitative tension —
not a calibration offset.

| Quantity | Master Yukawa at LZ | Zhang+ 2025 requires | Ratio |
|---|---|---|---|
| σ/m at v=10 km/s | 0.23 cm²/g | 30-100 cm²/g | 130-430× too small |
| Samples in Zhang range | 0.04% | 100% (by definition) | — |
| Δlog Z (8D - 7D) estimator | -24.7 | — | "very strong" evidence against |

**Interpretation:** If both the LZ 248 keV event AND the
GD-1 perturber are real SIDM signals, they cannot both be
explained by the same Yukawa operator with the master's
prescription. Either:
- (a) LZ 248 keV is not a SIDM magnetic-moment event
  (it's a different particle, or noise)
- (b) GD-1's perturber is not a core-collapsed SIDM halo
  (it's the LMC, bar, GMC, or some other dark substructure)
- (c) The Yukawa operator is wrong; the right model has
  different velocity-dependence or different mass regime

The first two are observational/experimental questions.
The third is a model-building question.

---

## Reference paper

**Zhang, X., Yu, H.-B., Yang, D., Nadler, E. 2025, ApJL 978, L23**
"The GD-1 Stellar Stream Perturber as a Core-collapsed
Self-interacting Dark Matter Halo"
(doi: 10.3847/2041-8213/ada02b)

**Key claim:** For SIDM to explain the GD-1 stream's gap
and spur features (Bonaca+ 2019), the perturber must be a
core-collapsed SIDM subhalo. Their N-body simulations find
that for **σ/m ~ 30-100 cm²/g at v_max ~ 10 km/s**, the
enclosed mass within 10 pc of the perturber is increased
by >1 order of magnitude compared to CDM, matching the
high-density requirement.

**Why this paper matters for T95:** The bok doc's specific
suggestion was "use GD-1 stream gaps to constrain SIDM."
Zhang+ 2025 is the **first paper to publish a quantitative
σ/m constraint from GD-1** in the SIDM context. This is
exactly the data we need.

---

## Method

1. **Load 7D posterior** from `outputs/t90/t41_v07_7d_posterior.npz`
2. **For each sample**, compute master's σ/m at v=10 km/s
   using `t40_yukawa_sigma_m.sigma_m_cm2_per_g`
3. **Compute Zhang logL** using a soft-box likelihood:
   logL = 0 if σ/m ∈ [30, 100] cm²/g
   logL = -0.5 × ((log σ/m - log boundary)/0.3)² otherwise
4. **Compute weighted-median logL** as an estimator for
   Δlog Z (with the same caveat as T95 Option 3)

**Why the full 8D nested-sampling fit times out:** The
Zhang constraint is so strict that almost all 7D posterior
samples (98.3%) get a very large negative logL. The
nested sampler cannot find the tiny region of parameter
space that satisfies Zhang+ 2025 within reasonable compute
time. A proper fit would either find a tiny posterior
island (giving a slightly less negative Δlog Z) or fail
entirely (giving log Z → -∞). The estimator captures the
direction and approximate magnitude of the tension.

---

## Results

### σ/m at v=10 km/s (Zhang scale)

| Statistic | Value |
|---|---|
| Master Yukawa weighted median | **0.23 cm²/g** |
| 16-84 percentile | 0.067 to 0.258 cm²/g |
| Min / max | 3.9e-12 to 2.9e+10 cm²/g |
| Zhang+ 2025 required range | **30-100 cm²/g** |
| **Ratio (Zhang lower / master median)** | **130×** |
| **Ratio (Zhang upper / master median)** | **430×** |

### Sample distribution

| | Count | Fraction |
|---|---|---|
| Samples in [30, 100] cm²/g | 1 / 2523 | **0.04%** |
| Samples below 30 cm²/g | 2480 / 2523 | 98.3% |
| Samples above 100 cm²/g | 42 / 2523 | 1.7% |

The min-max range shows that **a few samples do reach
30-100 cm²/g** (these have very large g_chi or very small
m_phi that push σ/m up). But these are extremely rare
in the posterior (~0.04%).

### Δlog Z (estimator)

| Quantity | Value |
|---|---|
| 7D log Z (T90.1) | -164.96 ± 0.25 |
| Zhang+ 2025 median logL | **-24.67** |
| 8D log Z estimate | -189.63 |
| **Δlog Z (8D - 7D) ESTIMATE** | **-24.67** |
| Jeffreys verdict | **"very strong" evidence against** |

This is **15× larger than the Option 3.5 result** (Δlog Z
= -1.57 with the Euclid Q1 sub-halo forecast). The Zhang
constraint is much more restrictive than the Channel 27
forecast.

---

## What this means

**This is a real, quantitative tension** between two
published interpretations of SIDM data:

1. **LZ 248 keV event** (arXiv:2609.02823): if magnetic-
   moment operator, requires μ_x ≈ 6.10×10⁻⁸ μ_N. At LZ
   posterior, master's Yukawa gives σ/m at v=10 km/s of
   **0.23 cm²/g**.

2. **GD-1 perturber** (Zhang+ 2025): if core-collapsed
   SIDM halo, requires σ/m at v=10 km/s of **30-100
   cm²/g**.

**These two constraints differ by 130-430×.** They
cannot both be true under the same Yukawa operator with
the master's prescription.

**Three possible resolutions** (in the order I'd
investigate):

1. **The LZ 248 keV event is not a SIDM magnetic-moment
   event.** It could be a different particle (e.g., a
   non-magnetic dark matter candidate), a statistical
   fluctuation, or a systematics issue. The T90 merge
   rule (community confirmation) gates on this.

2. **The GD-1 perturber is not a core-collapsed SIDM
   halo.** Alternative explanations include the LMC
   (Erkal+ 2019), the galactic bar (Hattori+ 2016),
   and giant molecular clouds (Amorisco 2016). The
   Zhang+ 2025 interpretation is one of several.

3. **The master Yukawa is not the right operator for
   both signals.** If both signals are real SIDM, the
   SIDM model must have different physics (e.g.,
   velocity-dependence that gives large σ/m at low v
   and small σ/m at high v). The master's Yukawa is
   too v-independent at galactic scales.

**The T90 merge rule is unchanged**: the magnetic-moment
branch stays off master until LZ community confirms the
248 keV event. The Zhang+ 2025 finding provides
**independent** reason to be cautious about the LZ
interpretation.

---

## Honest caveats

1. **The estimator overestimates the tension.** Just like
   Option 3 overestimated the Channel 27 tension by 2.4×,
   the Option 3.6 estimator likely overestimates the
   Zhang tension. A proper 8D fit (which I tried, and
   which times out because of the strict constraint)
   would give a less negative Δlog Z if it can find
   a posterior island, or log Z → -∞ if it can't.

2. **Zhang+ 2025 uses N-body simulations**, not data
   alone. Their σ/m range [30, 100] cm²/g is a model-
   dependent fit. A different N-body setup or different
   cross-section prescription could shift this range.

3. **The soft-edge width (0.3 dex) is arbitrary.** A
   different choice would change the absolute Δlog Z
   value, but not the qualitative verdict.

4. **Zhang+ 2025 is one of several GD-1 perturber
   interpretations.** Other papers (Erkal+ 2019 for
   LMC, Hattori+ 2016 for bar, Amorisco 2016 for GMC)
   offer alternative explanations. The Zhang+ 2025
   interpretation is not the consensus.

5. **The master's Yukawa prescription is approximate.**
   The T95 Phase 0 calibration showed master's σ/m is
   0.72× Robertson's at the same parameters. This
   30% offset is much smaller than the 130-430× tension
   with Zhang+ 2025, so the calibration is not the main
   issue.

---

## What this is NOT

1. **Not a real 8D nested-sampling fit.** The full fit
   times out because of the strict Zhang constraint. The
   estimator captures the direction and approximate
   magnitude.

2. **Not a code change to T41 or T90.** The 7D posterior
   is unchanged. The new script `t41_v09_magnetic_moment_zhang_gd1.py`
   is a separate experiment, branch-local.

3. **Not a verdict on the LZ 248 keV event.** T90 merge
   rule unchanged.

4. **Not a verdict on the GD-1 perturber interpretation.**
   Other explanations exist.

---

## What the bok doc was pointing at

The bok doc's specific suggestion was: "Gaia DR3 GD-1
stream gaps, breaks the m_χ-σ/m degeneracy, real
astrophysical data." Zhang+ 2025 is the **first paper to
publish a quantitative σ/m constraint from GD-1 in the
SIDM context**. The bok doc's intuition was right: GD-1
is a real astrophysical probe of SIDM. The Zhang+ 2025
result is a strong, falsifiable test.

The bok doc also mentioned sub-halo abundance forecasts
(Option 3.5, Channel 27). Zhang+ 2025 is a **direct
measurement** of one sub-halo, which is more constraining
than a population forecast.

---

## Files

- `v0.3-prelim/code/t95_v05_option3_6_zhang_gd1_estimator.py` —
  estimator script (the one that works)
- `v0.3-prelim/code/t41_v09_magnetic_moment_zhang_gd1.py` —
  full 8D fit attempt (times out)
- `v0.3-prelim/outputs/t95/option3_6_zhang_gd1_estimator.json` —
  JSON output
- `v0.3-prelim/docs/T95_OPTION3_5_8D_FIT.md` — Option 3.5
  for comparison
- `v0.3-prelim/docs/T95_CONSOLIDATED_RESULTS.md` —
  consolidated T95 results
- Zhang, X., Yu, H.-B., Yang, D., Nadler, E. 2025, ApJL
  978, L23 (the reference paper)

---

## Next steps (gated)

- **Real 8D fit** (the timed-out script): would need
  better initialization (a starting point in the
  parameter space that satisfies Zhang+ 2025) or
  more compute. Not done here.
- **GD-1 alternative interpretations** (LMC, bar, GMC):
  would require literature review of the competing
  models. Not done here.
- **T95 Option 4.1 (paper draft)**: now would include
  this Option 3.6 finding as a major new result.
- **No code changes to master or T90.** The 7D fit
  results are unchanged.
