# Model out-of-sample validation: LOO-CV results

**Status:** Validation COMPLETED. **8/9 channels validate well (overfit penalty < 0.1 nats). 1 channel (ch04_lens_subhalo) is in CATASTROPHIC tension with the rest (penalty = +31.8 nats).**

**Date:** 2026-09-12
**Branch:** `wip/cloud-9-relhic`
**Method:** Leave-One-Out Cross-Validation (LOO-CV)

---

## TL;DR — The model has predictive validity for 8/9 channels, but exposes a real tension

**Surprising result:** Most channels predict well out-of-sample. The model is NOT just curve-fitting — it's making real predictions. **But** Channel 4 (lens substructure) is in catastrophic tension with the other 8.

| Channel | In-sample | Predictive | Diff | Verdict |
|---|---|---|---|---|
| ch01_dsph | -1.692 | -1.716 | +0.024 | ✓ Validates |
| ch02_ufd | -0.089 | -0.094 | +0.005 | ✓ Excellent |
| ch03_bullet | -0.004 | -0.018 | +0.015 | ✓ Validates |
| **ch04_lens_subhalo** | **-0.965** | **-32.769** | **+31.804** | **🚨 CATASTROPHIC** |
| ch05_mw_satellite | -1.039 | -1.124 | +0.085 | ✓ Validates |
| ch06_cluster_upper | -0.003 | -0.004 | +0.001 | ✓ Excellent |
| ch07_draco | -1.216 | -1.304 | +0.088 | ✓ Validates |
| ch08_radio_relic | -0.056 | -0.091 | +0.035 | ✓ Validates |
| ch09_dm_free_udg | -0.098 | -0.102 | +0.004 | ✓ Excellent |

**Aggregate metrics:**
- Mean overfit penalty (excluding ch04): **+0.04 nats** — essentially zero overfit
- Mean overfit penalty (with ch04): +3.6 nats — dominated by ch04
- Bayesian p-value: 0.46 (in [0.05, 0.95] → model fits data well on average)

---

## Why ch04_lens_subhalo fails catastrophically

**ch04_lens_subhalo is a TIGHT (0.3 dex width) POINT ESTIMATE at:**
- log10(σ/m_eff at v=10 km/s) = 1.7 → σ/m_eff = 50 cm²/g

The other 8 channels (dSph, UFD, Bullet, MW satellite, Cluster upper, Draco, Radio relic, DM-free UDG) prefer:
- σ/m_0 ~0.59 cm²/g, a ~ 1.5
- → σ/m_eff at v=10 km/s = 0.59 × (100/10)^1.5 = **18 cm²/g** (log10 = 1.26)

**The 9-channel in-sample fit compromises on `a`** — it picks a value that lets all 9 channels contribute, giving in-sample log L for ch04 = -0.965.

**But** without ch04, the model has no constraint pointing to σ/m_eff = 50 cm²/g, so the posterior median of a drops to whatever the other 8 channels want. The lens subhalo channel then gets catastrophic penalty (-32 nats).

This is **NOT a model bug** — it's a **real validation signal**:
1. The lens subhalo channel is in **strong tension** with the other 8 at v=10 km/s
2. The other 8 channels want σ/m ~18 cm²/g; lens subhalo wants σ/m ~50 cm²/g
3. A factor of ~3 disagreement at low velocity

This tension has been hidden in the in-sample fit because of the v-dep compromise on `a`. Out-of-sample validation exposes it.

---

## What this means for the model

**Good news:** The model has **real predictive validity for 8 of 9 channels.** It's not just curve-fitting — when you remove a channel, the model can still predict it within 0.01-0.09 nats (excellent agreement). This is what you'd expect from a defensible multi-channel fit.

**Bad news:** Channel 4 (lens subhalo) is in **catastrophic tension** with the rest. This means:
1. The "9-channel consensus" is actually a compromise on `a` between conflicting low-v and high-v preferences
2. **The model is NOT wrong about the 8 channels** — it's just missing something at v=10 km/s specifically
3. **Either** ch04 should be downweighted (it's a tight constraint from a single PRL paper), **or** the other 8 channels are missing physics at low v

**The right response is not to remove ch04 but to investigate it.** The lens subhalo constraint (arXiv:2510.11006) was added in the Tier-1 PATCH 2026-08-25 and might be over-confident.

---

## Method

### LOO-CV procedure

For each of the 9 channels:
1. Hold out that channel
2. Run dynesty nested-sampling fit on the other 8
3. Compute posterior predictive: `<log L>_held = Σᵢ wᵢ × log L_held(θᵢ)`
4. Compare to in-sample contribution

### Implementation

Script: `v0.3-prelim/code/loo_cv_validation.py` (180 lines)
- nlive=500, dlogz=0.1, seed=20260912 (consistent with other v0.3-prelim fits)
- Imports all 9 channels from `channels_v03.py` and `channels_extended.py`
- 10 dynesty fits total (1 full + 9 LOO): ~25 seconds wall time

---

## Honest caveats

1. **LOO-CV is computationally expensive** (~25 sec for this model; would be hours for higher-dimensional models)
2. **Bayesian p-value is approximate** (uses MAP estimate of "observed" log L)
3. **Validation only tests predictive validity** at the model class level, not specific point estimates
4. **The catastrophic ch04 failure is informative** — it's not a bug in the validation, it's a real model tension
5. **The "8/9 validates" headline is real but partial** — the model has predictive validity for the channels it was fit to, but Channel 27 (NGC 1052 trail) and Channel 12 (cosmic web radio) weren't included in this validation

---

## Files

- `code/loo_cv_validation.py` — LOO-CV script (180 lines)
- `data/results/loo_cv_validation_2026_09_12.json` — full output

## References

- LOO-CV methodology: Vehtari, Gelman, Gabry 2017 (arXiv:1507.04544) — *Practical Bayesian model evaluation using leave-one-out cross-validation and WAIC*
- LENS_SIGMA_M_LOG_PEAK = 1.7 (channel 4): arXiv:2510.11006 — Yang+Yu 2026 PRL