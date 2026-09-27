# T90.21 (Option D) — Mixture of LZ Interpretations

**Status:** Option D SHIPPED — partial tension resolution
**Date:** 2026-09-07
**Branch:** `wip/tier3-magnetic-moment-LZ`
**Companion script:** `v0.3-prelim/code/t90_v21_lz_mixture.py`
**Output:** `v0.3-prelim/outputs/t90/t95_mixture_lz_interpretations.json`

---

## TL;DR

Test whether the T95 cross-check tension can be resolved by relaxing
the LZ magnetic-moment interpretation. Per v17 (Path C.4.5), the
LZ 248 keV event has **47% magnetic-moment + 47% Higgsino** + 6%
instrumental posterior weights. If the data is a **mixture**, the
effective σ/m at each velocity is the weighted sum.

**Honest result**:
- **Cluster tension** (v=150 km/s, Euclid Q1): reduced by 2× (log Z from -30 to -5.9). Still "substantial" tension because the magnetic-moment σ/m dominates.
- **Dwarf tension** (v=10 km/s, Zhang+ 2025 GD-1): **NOT resolved**. The Higgsino interpretation also has weak SIDM (σ/m ~ 0.05), so the mixture doesn't help at dwarf scales.

The mixture is a partial resolution. **Option D alone does not fully resolve the T95 tension** — need to combine with Options A or C.

---

## Method

### Step 1: v17 posteriors
Re-ran `t90_v17_lz_time_series.hypothesis_posteriors(n_obs=1)`:

| Hypothesis | Posterior |
|---|---|
| Magnetic-moment DM | 47.0% |
| Higgsino inelastic | 47.0% |
| Instrumental | 6.1% |
| 124Xe DEC | 0.0% |
| Solar 8B ν | 0.0% |

### Step 2: σ/m mapping

| Interpretation | σ/m at v=150 km/s |
|---|---|
| Magnetic-moment DM (master Yukawa) | 0.66 cm²/g |
| Higgsino (EW-scale, no SIDM) | 0.05 cm²/g |
| Instrumental | 0 |

### Step 3: Mixture
σ/m_eff(v) = P(MM) × σ/m_MM(v) + P(HIG) × σ/m_HIG(v) + P(Inst) × 0

### Step 4: T95 tension re-evaluation

| Probe | Master | Mixture | Resolution |
|---|---|---|---|
| Euclid Q1 (v=150) | log Z = -30.0 (substantial) | log Z = -5.9 (substantial) | Partial — still 4.7× above forecast |
| Zhang+ 2025 GD-1 (v=10) | log Z very negative | log Z very negative | NO resolution |

---

## Detailed Results

### Cluster scale (v=150 km/s)

| Quantity | Master | Mixture | Change |
|---|---|---|---|
| σ/m | 0.66 cm²/g | 0.33 cm²/g | -1.98× (factor 2 reduction) |
| Ratio to Euclid Q1 forecast | 9.3× | 4.7× | Still above forecast |
| Rough log Z | -30.0 | -5.9 | -25 improvement |
| Tension classification | substantial | substantial | Same category |

The 2× reduction is real but **insufficient** to bring σ/m into the Euclid Q1 forecast range (0.05-0.10 cm²/g). The mixture σ/m = 0.33 is still 3-7× above the forecast.

### Dwarf scale (v=10 km/s)

| Quantity | Master | Mixture | Change |
|---|---|---|---|
| σ/m | 1.01 cm²/g | 0.50 cm²/g | -2.03× |
| Ratio to Zhang+ 2025 [30, 100] | 0.03× (below) | 0.02× (below) | Both far below |
| Rough log Z | very negative | very negative | NO improvement |

The dwarf tension is NOT resolved because the Higgsino also has weak SIDM (σ/m ~0.05 cm²/g), so a 50/50 mixture only halves σ/m. To match Zhang+ 2025 [30, 100] cm²/g, we'd need σ/m ~30 — the master is 30× below that, and the mixture is 60× below.

---

## Key Caveats

1. **Higgsino σ/m = 0.05 cm²/g is a conservative upper bound**. Per cosmological constraints, the Higgsino doesn't have strong SIDM. But the exact upper bound depends on the bino/wino mass spectrum, which isn't fully determined.

2. **Rough log Z estimates are Gaussian approximations**, not a full Bayesian fit. The qualitative trend (substantial tension still) is robust, but the exact Δlog Z values would need a proper 8D fit.

3. **Mixture assumes the LZ event is the sum of multiple components**. This is physically reasonable — the event could be either magnetic-moment OR Higgsino, but not both. So strictly, the mixture σ/m is not well-defined; it's a weighted EXPECTATION over the posterior.

4. **The mixture σ/m doesn't include correlations** between the magnetic-moment μ_x and Higgsino δ parameters. A full mixture fit would marginalize over both.

---

## What Option D does NOT do

1. **Doesn't fully resolve cluster tension** (still substantial)
2. **Doesn't touch dwarf tension** (Zhang+ 2025)
3. **Doesn't run a full 8D Bayesian fit** with the mixture likelihood
4. **Doesn't account for UV-completion constraints** (v18 composite-DM ruled out)

---

## Files

- `v0.3-prelim/code/t90_v21_lz_mixture.py` (12.3 KB)
- `v0.3-prelim/tests/test_t90_v21_lz_mixture.py` (3.4 KB, 10 tests, 10/10 pass)
- `v0.3-prelim/outputs/t90/t95_mixture_lz_interpretations.json`

---

## References

1. `t90_v17_lz_time_series.py` — Bayesian hypothesis posteriors
2. `T95_CONSOLIDATED_RESULTS.md` — the T95 cross-check this addresses
3. `T89_SIDMKIT_SIDMVDSIGMAS_BENCHMARK.md` — master Yukawa calibration
4. arXiv:2609.01583 — Higgsino interpretation of LZ event (Fan & Tweed 2026)

---

## Next steps

Per user directive: "proceed option d, then b, a and c."

Continuing with **Option B** (re-calibrate master Yukawa against Robertson 2019, ~3-5 days estimated).

---

## TIME LOG

```
2026-09-07 sidm-composite-dm-mediator T90.21 Option D (mixture)
  ESTIMATE: 1 week (initial estimate per pattern)
  ACTUAL:   ~30 minutes of agent compute (script + 10 tests)
  RATIO:    ~0.01x (massively over-estimated)
  NOTE:     First-pass implementation works as expected. Mixture
            reduces cluster sigma/m by 2x but doesn't fully
            resolve the cluster tension, doesn't touch dwarf
            tension. Partial resolution only.
```