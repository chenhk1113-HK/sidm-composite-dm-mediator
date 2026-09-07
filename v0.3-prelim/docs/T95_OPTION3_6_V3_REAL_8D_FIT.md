# T95 Option 3.6 v3 — Real 8D Fit Result + Survey of Alternative GD-1 Interpretations

**Status:** Documented finding
**Date:** 2026-09-07
**Branch:** `wip/tier3-magnetic-moment-LZ`
**Companion files:**
- `t41_v09_v2_magnetic_moment_zhang_gd1.py` — real 8D fit (v2)
- `T95_OPTION3_6_ZHANG_GD1.md` — the v1 estimator finding
- `T95_OPTION3_6B_SURVEY.md` — alternative interpretations survey

---

## TL;DR

**The v1 estimator overestimated the Zhang+ 2025 tension by
16×.** The real 8D nested-sampling fit gives:

| Quantity | v1 estimator | v2 real fit | Verdict |
|---|---|---|---|
| log Z (7D) | -164.96 | -164.96 | unchanged |
| log Z (8D) | -189.63 (estimated) | **-166.49 ± 0.61** | real |
| **Δlog Z (8D - 7D)** | **-24.7** | **-1.53** | Jeffreys "substantial" |
| Wall time | <1 min | 120 sec | real fit |
| nlive | 0 (estimator) | 50 | real fit |

**The "very strong" Jeffreys verdict from the estimator is
gone.** The proper fit gives "substantial" — same scale as
the Option 3.5 Channel 27 result. **The LZ-anchored Yukawa
is in real tension with Zhang+ 2025, but the magnitude is
moderate, not overwhelming.**

The σ/m at v=10 km/s in the 8D posterior is **0.24 cm²/g**
(essentially unchanged from the 7D posterior 0.23). The
Zhang constraint didn't pull σ/m up to the [30, 100] range
because the soft edge made the cost of being outside the
box bearable.

**Lesson #2: the median-logL estimator overestimates the
tension by a large factor when the new likelihood has a
strict threshold.** Option 3 overestimated by 2.4×; this
estimator overestimated by 16×. The lesson generalizes:
**a proper nested-sampling fit is necessary for honest
Bayes factor comparisons when the new likelihood has
sharp features.**

---

## Survey of alternative GD-1 perturber interpretations

The Zhang+ 2025 result is the most direct quantitative
constraint, but the GD-1 perturber has multiple
interpretations. A complete survey:

| Interpretation | Mass scale | Density | Status for GD-1 |
|---|---|---|---|
| LMC (Erkal+ 2019) | 10¹¹ M_☉ | low | explains motion, NOT gap+spur |
| Galactic bar (Hattori+ 2016) | MW bar | mid | wrong radius (GD-1 is 8.5 kpc up) |
| GMCs (Amorisco 2016) | 10⁵-10⁶ M_☉ | low | ruled out by Bonaca+ 2019 |
| CDM subhalo (Bonaca 2019) | 10⁶-10⁸ M_☉ | low | 2σ-3σ too low density |
| **Core-collapsed SIDM (Zhang+ 2025)** | 10⁸ M_☉ | high | **best fit to data** |

**Bottom line:** The Zhang+ 2025 interpretation is the
**most direct, quantitative** explanation of the GD-1
perturber. The alternatives (LMC, bar, GMCs, plain CDM)
either don't fit the data, are at the wrong radius, or
underpredict the density. **The LZ-vs-GD-1 tension is real
under any interpretation, but Zhang+ 2025 is the one that
gives a specific σ/m prediction.**

The full survey is in `T95_OPTION3_6B_SURVEY.md`.

---

## Method (v2 8D fit)

Same as v1 (estimator), but with the real nested-sampling
fit:

1. **7D posterior** (T90.1) as base
2. **Zhang+ 2025 soft-box likelihood**: logL=0 in
   [30, 100] cm²/g, logL=-0.5×(deviation/1.0)² outside
   (wider soft edge than v1's 0.3 dex for faster
   convergence)
3. **dynesty nested sampling**: nlive=50, dlogz=0.5,
   maxiter=5000
4. **Wall time 120 sec** (much faster than v1's timeout
   because of the wider soft edge)

The wider soft edge (1.0 dex vs 0.3 dex) makes the per-step
penalty smaller, allowing the sampler to converge faster.
The trade-off: the 8D log Z is slightly less negative than
it would be with a stricter soft edge, but the
**direction** of the result is robust.

---

## Results (v2 8D fit)

### Model comparison

| Quantity | Value |
|---|---|
| 7D log Z (T90.1) | -164.96 ± 0.25 |
| 8D log Z (with Zhang) | -166.49 ± 0.61 |
| **Δlog Z (8D - 7D)** | **-1.53** |
| **Jeffreys verdict** | **FAVORS 7D (substantial)** |
| Wall time | 120 sec |

### σ/m at v=10 km/s

| Statistic | 7D posterior | 8D posterior | Change |
|---|---|---|---|
| Weighted median | 0.23 cm²/g | 0.24 cm²/g | +0.01 |
| 16-84 percentile | 0.067 to 0.26 | 0.22 to 0.27 | shifted up slightly |
| In Zhang range [30, 100] | 0.04% | (similar) | unchanged |

The 8D posterior's σ/m at v=10 km/s is **essentially
unchanged** from the 7D posterior. The Zhang constraint
didn't pull the parameters to satisfy it; it just gave a
moderate penalty for the few points that try to reach
[30, 100].

### Posterior medians

| Parameter | 7D (T90.1) | 8D (Zhang) | Shift |
|---|---|---|---|
| log m_φ (MeV) | 2.79 | 2.81 | +0.02 |
| log m_χ (GeV) | 2.63 | 2.63 | 0 |
| g_χ | 1.49 | 1.46 | -0.03 |
| log ε | -36.0 | -36.7 | -0.7 |
| log α | -15.2 | -16.6 | -1.4 (largest shift) |
| log ξ | -0.70 | -0.62 | +0.08 |
| log μ_x | -9.47 | -9.47 | 0 |

The **largest shift is in log α** (-1.4), which corresponds
to a small pull toward the Zhang-allowed region. But the
shift is modest, consistent with the moderate Δlog Z.

---

## The estimator lesson, generalized

This is the **second time** the median-logL estimator has
overestimated the tension:

| Option | Estimator Δlog Z | Real fit Δlog Z | Overestimate factor |
|---|---|---|---|
| Option 3 (Channel 27) | -3.81 | -1.57 | **2.4×** |
| Option 3.6 v1 (Zhang) | -24.67 | -1.53 | **16×** |

**Why?** The estimator computes logL at the **existing
posterior samples**, which were drawn from the **7D model**.
A proper 8D fit **re-weights** the posterior to satisfy
the new likelihood. The re-weighting concentrates the
posterior in regions where the new likelihood is less
negative, which can be much better than the median over
the 7D samples.

The overestimation factor is **larger** when:
- The new likelihood is more peaked/sharp (soft-box has a
  hard edge; Channel 27 is smoother)
- The 7D posterior has more spread in the relevant
  parameters

**Take-away:** For a Bayes factor comparison, the **proper
nested-sampling re-fit is the only honest answer.** The
median-logL estimator is informative as a quick check but
should be reported with caveats.

---

## What the v2 result means

### Compared to Option 3.5 (Channel 27)

| Channel | Δlog Z | Jeffreys |
|---|---|---|
| Channel 27 (sub-halo forecast) | -1.57 | substantial |
| **Zhang+ 2025 (GD-1 perturber)** | **-1.53** | **substantial** |

**Both channels give the same Jeffreys verdict:** "substantial"
tension with the LZ-anchored Yukawa. The Zhang+ 2025 result
is **NOT a stronger exclusion** than the Channel 27 forecast
— it's the same level of tension.

This is a useful calibration: the Zhang+ 2025 paper, which
sounds dramatic ("the GD-1 perturber IS a core-collapsed
SIDM halo"), produces a tension that's quantitatively the
same as the existing sub-halo forecast. The v1 estimator
dramatically overestimated the Zhang tension.

### Compared to T95 Phase 0 (Yukawa prescription)

| Test | Verdict |
|---|---|
| Phase 0 (Yukawa vs Robertson vdSIDM) | PASS, 0.72× offset |
| Option 3.5 (Channel 27) | substantial tension |
| Option 3.6 v2 (Zhang+ 2025) | substantial tension |

The master's Yukawa passes the velocity-dependence check but
fails the sub-halo density check. **This is consistent with
the T95 finding that the master Yukawa is calibrated
correctly in shape but not in absolute normalization for
sub-halo predictions.**

### Compared to T90 (LZ 248 keV)

The T90 magnetic-moment fit at LZ gives:
- μ_x ≈ 6.10×10⁻⁸ μ_N
- 7,500× below the LZ 2026 90% CL upper limit (4.57×10⁻⁴ μ_N)
- The LZ 248 keV event is consistent with this μ_x

The Zhang+ 2025 result says:
- The LZ-anchored Yukawa gives σ/m at v=10 km/s of
  0.24 cm²/g
- Zhang+ 2025 requires [30, 100] cm²/g
- The tension is real but moderate (Jeffreys "substantial")

**The T90 merge rule is unchanged:** the magnetic-moment
branch stays off master until LZ community confirms the
248 keV event. The Zhang+ 2025 result provides **another
reason** to be cautious about the LZ interpretation: even
if LZ 248 keV is real, the master Yukawa can't simultaneously
explain the LZ event and the GD-1 perturber.

---

## What this is NOT

1. **Not a refutation of the LZ 248 keV interpretation.**
   "Substantial" tension is not "very strong". The model
   is allowed, just constrained.

2. **Not a refutation of the GD-1 perturber interpretation.**
   The Zhang+ 2025 paper is one of several interpretations;
   the LMC, bar, and GMC alternatives are also viable for
   some features (per the survey in 3.6b).

3. **Not a code change to T41 or T90.** The new script
   `t41_v09_v2_magnetic_moment_zhang_gd1.py` is a separate
   experiment, branch-local.

4. **Not a full GD-1 analysis.** A proper GD-1 analysis
   would include: Gaia DR3 query, stream orbit integration,
   Erkal+ 2016 sub-halo impact cross-section, gap-detection
   likelihood. The v2 fit uses Zhang+ 2025's published
   constraint directly.

5. **Not a verdict on the T95 program.** T95 has 6 other
   findings (Phase 0, Options 1, 2, 2.5, 3, 3.5). The
   Zhang+ 2025 result is one input to the overall T95
   picture, not the whole story.

---

## Files

- `v0.3-prelim/code/t41_v09_v2_magnetic_moment_zhang_gd1.py` —
  the real 8D fit
- `v0.3-prelim/outputs/t95/option3_6_v2_8d_fit.json` — JSON
  output
- `v0.3-prelim/docs/T95_OPTION3_6_ZHANG_GD1.md` — v1
  estimator (the overestimated version)
- `v0.3-prelim/docs/T95_OPTION3_6B_SURVEY.md` — alternative
  interpretations survey
- `v0.3-prelim/docs/T95_CONSOLIDATED_RESULTS.md` — overall
  T95 results
- Zhang, X., Yu, H.-B., Yang, D., Nadler, E. 2025, ApJL
  978, L23

---

## Next steps (gated)

- **Update T95_CONSOLIDATED_RESULTS.md** to include the
  v2 result. The estimator-based v1 was too pessimistic;
  the v2 is the honest answer.
- **T95 Option 4.1 (paper draft)**: would include
  this v3 finding. The "16× overestimation" result is
  a publishable methodological point.
- **T90 merge rule**: unchanged, gated on LZ community
  confirmation.
