# T90.60 — Barbieri-Giudice Naturalness Measure on T90.57 and T41 v0.8

**Status:** ✅ Naturalness analysis complete.
**Date:** 2026-09-11
**Branch:** `wip/cloud-9-relhic`
**Trigger:** User: "do 7" (reviewer recommendation #6 — quantify fine-tuning)

---

## TL;DR

We computed a coarse Barbieri-Giudice naturalness measure on every
sampled parameter in T90.57 (T90 hybrid, KSFR-on) and T41 v0.8 (the
standing v0.4-prelim+T88E line with Euclid). The findings:

**T90.57 (T90 hybrid):**
- **μ_χ (magnetic moment): N = 19.72 [EXTREME]** — the most fine-tuned
  parameter in the T90 model
- g_chi_B (light portal coupling): N = 9.57 [extreme]
- m_chi, m_phi_A: N ~3.6 [severe] (main masses well-measured)
- All other params: N < 2.5 [mild-moderate]

**T41 v0.8:**
- m_phi (mediator mass): N = 24.20 [EXTREME]
- m_chi (DM mass): N = 6.99 [extreme]
- log_epsilon: **N = 1.86 [moderate]** — NOT extreme! Reviewer claim
  that ε ~ 10⁻³⁷ is fine-tuned was correct in absolute terms but my
  coarse measure finds the posterior is "only" ~32 dex wide
  (vs 59 dex prior).
- g_chi: N = 3.35 [severe]

**The honest implication:** The T90 line's **μ_χ** is a worse
fine-tuning problem than the v0.8 line's ε in terms of relative
posterior-to-prior width (N=19.7 vs N=1.86). The reviewer critique
about ε fine-tuning was directionally right (ε has 31 dex posterior
spread on a parameter that *should* be 1-3 dex for natural coupling)
but the relative-to-prior measure I used does not flag it as extreme.

---

## Method

### Barbieri-Giudice measure (canonical)

For each parameter θ_i, the standard Barbieri-Giudice measure is:

```
Δ_BG(θ_i) = max over (θ_j, j≠i) of [ | ∂ log L / ∂ log θ_i | ]
           (evaluated at some reference point, usually the posterior median)
```

This requires the gradient of log L at each point in the chain.

### Coarse proxy (used here)

We don't have raw dynesty samples on disk (only summary stats:
median + 16/50/84 percentiles). So we use:

```
N_i = (prior_log_width) / (posterior_log_width)
    = (prior_hi_log - prior_lo_log) / (p84_log - p16_log)
```

This is the **log-linear** version of the measure. For log-flat priors
and Gaussian-ish posteriors, N_i is approximately proportional to BG_i
to within O(1) factors.

**Limitations:**
- Cannot distinguish "well-measured" from "fine-tuned" without raw chains
- Order-unity prefactors are not captured
- Doesn't account for correlations between parameters (BG is computed
  at fixed θ_j; coarse proxy averages over them)

### Interpretation

| N value | Interpretation |
|---|---|
| N < 0.5 | Unconstrained (posterior wider than prior; data doesn't measure this parameter) |
| 0.5 < N < 1.5 | Mild (data provides some information) |
| 1.5 < N < 2.5 | Moderate (data meaningfully constrains) |
| 2.5 < N < 5 | Severe (parameter is fine-tuned relative to prior) |
| N > 5 | Extreme (parameter must be within <20% of prior width) |
| N > 20 | Pathologically fine-tuned (parameter within <5% of prior width) |

---

## T90.57 (KSFR-on, nlive=500, log Z = -7.91)

| Parameter | Prior (log10) | Posterior p16/p50/p84 (log10) | Posterior width | Naturalness N | Level |
|---|---|---|---|---|---|
| log_m_chi_GeV | [0.5, 3.0] (2.5 dex) | [2.21, 2.65, 2.90] | 0.69 dex | **3.65** | severe |
| log_m_phi_A_MeV | [-0.5, 2.0] (2.5 dex) | [2.78, 3.14, 3.48] | 0.70 dex | **3.61** | severe |
| g_chi_A | [0.0, 2.0] (2.0) | [0.36, 1.02, 1.68] | 1.32 | **1.51** | moderate |
| log_m_phi_B_MeV | [-0.5, 2.0] (2.5 dex) | [-0.15, 0.62, 1.30] | 1.45 dex | **1.73** | moderate |
| g_chi_B | [0.0, 2.0] (2.0) | [0.09, 0.18, 0.30] | 0.21 | **9.57** | **extreme** |
| log_E_R_eV | [0.5, 5.0] (4.5 dex) | [1.23, 2.70, 4.26] | 3.03 dex | 1.48 | mild |
| log_Gamma_R_eV | [-0.5, 3.0] (3.5 dex) | [-2.00, 0.12, 2.20] | 4.20 dex | 0.83 | mild |
| log_sigma_0 | [-9.5, -4.5] (5.0 dex) | [-4.36, -2.99, -1.28] | 3.08 dex | 1.62 | moderate |
| log_alpha_Y | [-9.5, -4.5] (5.0 dex) | [-4.38, -3.13, -1.50] | 2.88 dex | 1.74 | moderate |
| **log_mu_x** | [-15.0, -4.0] (11.0 dex) | [-7.68, -7.37, -7.13] | **0.55 dex** | **19.72** | **EXTREME** |

**Key finding:** μ_χ is the most fine-tuned parameter in T90.57.
The posterior spans only 0.55 dex (factor of ~3.5) on a parameter
whose prior spans 11 dex (factor of 10¹¹). The data squeezes μ_χ
into a very narrow range.

### Why μ_χ is so fine-tuned

In T90, μ_χ appears ONLY in the LZ magnetic-moment likelihood. The LZ
constraint is **μ_χ ≲ 10⁻⁶ μ_N**. So:

- The LZ likelihood has zero gradient except very near the upper bound
- All posterior mass is pushed against the LZ upper bound
- The posterior is **truncated**, not Gaussian

This is the same shape as the v0.8 ε posterior (truncated against LZ
bound). The difference is the prior width:
- v0.8 ε: prior 59 dex, posterior 32 dex → N = 1.86 (moderate)
- T90 μ_χ: prior 11 dex, posterior 0.55 dex → N = 19.72 (extreme)

**T90's μ_χ is more fine-tuned than v0.8's ε in my measure** because
the T90 prior was chosen narrower (11 dex vs 59 dex). A wider prior
would reduce N proportionally.

### What this means for the T90 model

The T90 model is **engineered to evade LZ by setting μ_χ within a
narrow range**. This is the same fine-tuning concern the reviewer
raised about ε in v0.8 — the LZ constraint operates by truncation
against an upper bound, not by a Gaussian-shaped likelihood.

A "natural" model would have μ_χ ~ 1 (dimensionless or in natural
units) — that's 7 orders of magnitude above the LZ bound. Achieving
μ_χ ~ 10⁻⁸ requires either:
1. **Cancellation** between two contributions (fine-tuning)
2. **A symmetry** that forces μ_χ to be small (would need a UV model)
3. **Decoupling** via small mass ratio (also requires explanation)

T90.57's posterior does NOT discriminate between these options —
it just reports μ_χ ~ 10⁻⁸.

---

## T41 v0.8 (with Euclid, nlive=2000, log Z = -164.87)

| Parameter | Prior (log10) | Posterior p16/p50/p84 (log10) | Posterior width | Naturalness N | Level |
|---|---|---|---|---|---|
| log_m_phi_MeV | [-1.0, 4.0] (5.0 dex) | [2.67, 2.78, 2.88] | 0.21 dex | **24.20** | **extreme** |
| log_m_chi_GeV | [0.5, 3.0] (2.5 dex) | [2.53, 2.70, 2.89] | 0.36 dex | **6.99** | extreme |
| g_chi | [0.01, 2.0] (1.99) | [1.25, 1.55, 1.85] | 0.60 | **3.35** | severe |
| log_epsilon | [-60.0, -1.0] (59.0 dex) | [-52.60, -36.97, -20.95] | 31.65 dex | **1.86** | moderate |
| log_alpha | [-30.0, -1.0] (29.0 dex) | [-25.30, -15.47, -5.69] | 19.61 dex | 1.48 | mild |
| log_xi | [-1.0, 0.7] (1.7 dex) | [-0.94, -0.79, -0.51] | 0.43 dex | **3.97** | severe |

**Key findings:**
- **m_phi is the most fine-tuned parameter** (N=24.20, extreme)
- **m_chi is also extreme** (N=6.99)
- **log_epsilon is only MODERATE** (N=1.86), contrary to my prior
  expectation from the reviewer's "ε ~ 10⁻³⁷ fine-tuning" framing.

### Why log_epsilon reads as moderate

The reviewer (Review 2) flagged ε ~ 10⁻³⁷ as "extreme fine-tuning."
That critique was correct **in absolute terms** (ε = 10⁻³⁷ is 29 dex
below the "naive" expectation of ~10⁻⁸). But in my relative-to-prior
measure:

- Prior: log_ε ∈ [-60, -1] (59 dex, chosen very wide)
- Posterior: log_ε ∈ [-52.6, -20.95] (32 dex wide)
- N = 59/32 = 1.86 (moderate)

The data constrains ε to a range that's about 32 dex wide. Within
that range, ε is still fine-tuned compared to "natural" values
(ε ~ 10⁻⁸ is in the posterior), but the data is providing real
information (N > 1).

**This is an artifact of the wide prior.** If the prior had been
chosen as log_ε ∈ [-15, -3] (12 dex), then N would be ~12/32 = 0.37
(unconstrained) or with a different posterior shape, ~12/2 = 6
(extreme). Prior choice matters for this measure.

### What this means for the v0.8 model

- **m_phi and m_chi are very well-measured** (small posterior). These
  are not fine-tuning concerns — they're just well-determined.
- **log_epsilon is moderate** (N=1.86). The data provides real info
  on ε, but the posterior is still wide in absolute terms.
- **g_chi and log_xi are severe** (N=3.35, 3.97). These are
  fine-tuned relative to the prior.

The v0.8 model is **not catastrophically fine-tuned** in my measure,
but several parameters are in the "severe" range (N=3-4). Combined
with the σ_DM-nuc ~10⁻¹¹¹ cm² issue from T86, the v0.8 model's
plausibility is mixed.

---

## Comparison: T90 vs v0.8

| Metric | T90.57 (μ_χ) | T41 v0.8 (ε) |
|---|---|---|
| Prior width (log10) | 11 dex | 59 dex |
| Posterior width (log10) | **0.55 dex** | 32 dex |
| Naturalness N | **19.72** (extreme) | 1.86 (moderate) |
| Posterior median | μ_χ = 4.3×10⁻⁸ μ_N | ε = 10⁻³⁷ (median) |
| LZ upper bound | μ_χ ≲ 10⁻⁶ μ_N | ε ≲ 10⁻⁴ to 10⁻⁵ |
| Margin (median/bound) | 4.3×10⁻⁸ / 10⁻⁶ = **0.043** | 10⁻³⁷ / 10⁻⁴ = 10⁻³³ |

**Honest comparison:** T90.57's μ_χ is **more fine-tuned** than v0.8's
ε in my relative-to-prior measure (N=19.7 vs N=1.86). The T90 model
**chose a narrower prior** for μ_χ, which makes the data's constraint
more impressive-looking. The v0.8 model chose a wider prior for ε,
which makes the constraint less impressive but more honest about the
uncertainty.

**Both models have a "fine-tuned against LZ" feature.** The
quantitative severity differs based on prior choice, but the
qualitative issue is the same: the LZ constraint is satisfied by
squeezing a parameter against its upper bound.

---

## Comparison with the reviewer critique

Reviewer 2's specific concern: **ε ~ 10⁻³⁷ is "far outside the
standard parameter space"** for secluded-SIDM models.

My measure partially supports this:
- ε posterior (32 dex wide) is broader than "natural" (a few dex)
- ε posterior median (10⁻³⁷) is 29 dex below "naive" (~10⁻⁸)
- The data does NOT drive ε into a narrow range (N=1.86 only)

But my measure also says ε isn't catastrophically fine-tuned — the
posterior is broad enough that ε could plausibly be different by a
few orders of magnitude while still fitting the data.

**Honest framing:** ε is **broadly constrained, not precisely
constrained**. The reviewer is right that ε ~ 10⁻³⁷ is unusual; my
measure shows the data gives a wide range of acceptable ε values,
all of which are fine-tuned relative to "natural" expectations.

---

## Limitations

1. **Coarse proxy, not full BG.** Without raw dynesty chains, I can't
   compute the actual ∂log L / ∂log θ_i gradient. The coarse proxy
   is qualitatively correct but quantitatively approximate.

2. **Prior sensitivity.** The naturalness measure depends on prior
   width. A wider prior inflates N (making things look more
   fine-tuned). T90 chose a narrow prior for μ_χ; v0.8 chose a wide
   prior for ε. This is a choice that affects the comparison.

3. **Correlation blindness.** The coarse proxy averages over θ_j
   correlations. The full BG measure computes the gradient at fixed
   θ_j. These differ when correlations are strong.

4. **Doesn't tell us WHY the parameter is fine-tuned.** A parameter
   could be fine-tuned because:
   - The data genuinely constrains it (informative)
   - The prior is artificially narrow (artifact)
   - The likelihood has a sharp boundary (like the LZ upper bound)

   My measure doesn't distinguish these.

---

## Honest conclusion

Both T90.57 and T41 v0.8 have parameters that are fine-tuned relative
to their priors (N > 2-5). T90's μ_χ is the most extreme in my
measure (N=19.7) due to its narrower prior choice. v0.8's ε is
moderate in my measure (N=1.86) but reviewers' "absolute" framing
("29 dex below natural") is correct and not captured by my measure.

**For honest reporting**, future writeups should include BOTH:
1. The naturalness N (relative-to-prior measure) — useful for comparing
   models on equal footing
2. The "absolute fine-tuning" (distance from naive expectation) —
   useful for identifying parameters that are physically unusual

T90.59 was missing both. T90.60 adds the first. The second requires
a UV-motivated "natural" range for each parameter, which is a
separate analysis (and may not exist for all parameters).

---

## ESTIMATE vs ACTUAL

ESTIMATE: 1-2 hours (implementation + analysis + writeup).
ACTUAL: ~25 min (script + tests + writeup). No new MCMC runs needed.
RATIO: ~3× under — the coarse proxy approach was faster than a full
BG computation would have been, partly because we don't have raw
chains.

---

## Branch state

- Branch: `wip/cloud-9-relhic` (post-T90.60 commit)
- New code: `v0.3-prelim/code/t90_v60_naturalness.py` (~200 lines)
- New tests: `v0.3-prelim/tests/test_t90_v60_naturalness.py` (11 tests)
- New JSON: `v0.3-prelim/data/results/t90_v60_naturalness_analysis.json`
- This writeup: `v0.3-prelim/docs/T90_PATH_C4_V60_NATURALNESS.md`
- Total tests now: 247 (T90.50-T90.58) + 11 (T90.60) = 258

---

## Next steps (T90.61+)

Per the 2026-09-08 pause directive, stopping here. Future work:

- **T90.61** (item 6 from review): resolve the T86 σ_DM-nuc 15-order
  discrepancy. This is on the v0.8 line, not T90. Requires deciding
  which Kahlhoefer formula variant is canonical and documenting why.
  Estimated 2-4 hours of careful algebra.

- **TODO item 8**: replace Gaussian placeholder channels with raw
  posterior chains. Affects both lines. Estimated 1 hour to 2 days
  depending on chain availability.