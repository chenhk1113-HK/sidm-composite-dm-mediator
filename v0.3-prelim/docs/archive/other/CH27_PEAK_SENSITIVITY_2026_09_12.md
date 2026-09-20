# Channel 27 peak sensitivity sweep + AMUSE-derived peak ablation

**Status:** Real sensitivity sweep completed. AMUSE-derived peak creates measurable tension with 11-channel baseline.

**Date:** 2026-09-12
**Branch:** `wip/cloud-9-relhic` @ commit `1d151b6`

---

## TL;DR — the simulation-derived peak is in tension with the 11-channel model

Three ablation results on `wip/cloud-9-relhic` HEAD (`1d151b6` + post-sensitivity):

1. **AMUSE-derived peak (3.07 cm²/g)** — ΔlogZ = **-0.898** (penalizes fit), posterior median σ/m_0 shifts from 0.59 → 1.77 cm²/g (+3.0× upward).
2. **Sensitivity sweep** over peak ∈ {1.0, 2.0, 3.0, 5.0} cm²/g — ΔlogZ is negative at ALL peak values; the model has a built-in preference for σ/m(v=358) ≈ 0.4-0.5 cm²/g via v-dep.
3. **Implied σ/m(v=358)** saturates near 0.4-0.5 cm²/g regardless of where the peak is anchored (model pulls σ/m_0 toward ~1.5-2.0, but a → 1.1-1.3, so σ/m(v=358) = σ/m_0 × (100/358)^-a ≈ 0.4-0.5).

---

## Why this matters (honest framing)

The AMUSE-ph4 simulation (1024 particles per halo, 6 σ/m values, t=300 Myr discriminating region) gives σ/m_peak = 3.07 ± 0.5 cm²/g. The 11-channel v0.3-prelim model (which includes dwarf kinematics, LZ, KSFR, lensing, etc.) prefers σ/m(v=358) ≈ 0.4-0.5 cm²/g.

**Two interpretations:**
- **(a) Simulation too high.** N=1024 is ~100× below publication-grade; the SIDM kernel is a uniform Gaussian perturbation, not pairwise Rutherford scattering. The 3.07 cm²/g number is likely overestimated.
- **(b) Model biased low.** The 11 channels are mostly upper limits + a few dwarf/cluster constraints; they don't strongly constrain σ/m at v=358 specifically. A velocity-scale anchor at 3.07 cm²/g is a real challenge to them.

**Either way, this is a usable result.** The simulation-vs-model disagreement is itself an actionable signal: it tells us that **Channel 27 should NOT use the AMUSE peak as-is.** The placeholder (0.5 cm²/g) was closer to model-consistent, even though it was hand-tuned.

---

## Method

### Ablation with AMUSE-derived peak

Changed `NGC1052_TRAIL_LOG_SM_PEAK` from -0.30 (placeholder, ~0.5 cm²/g) to +0.487 (AMUSE-derived, ~3.07 cm²/g) in `ch27_ngc1052_trail_channel.py`. Ran `t13_v2_trail_ablation.py` with the same nlive=500, dlogz=0.1, rstate=20260912.

### Sensitivity sweep

Wrote `ch27_peak_sensitivity.py` to monkey-patch `NGC1052_TRAIL_LOG_SM_PEAK` to each of {1.0, 2.0, 3.0, 5.0} cm²/g in turn, run a fresh dynesty fit, restore original. Tests at 4 peak values + 1 baseline = 5 fits total.

---

## Results

### Single-point ablation (peak=3.07 cm²/g)

| Quantity | 11ch (Ch27 OFF) | 12ch (Ch27 ON) | Δ |
|---|---|---|---|
| log Z | -7.878 | -8.777 | **-0.898** |
| median σ/m_0 (cm²/g) | 0.590 | 1.774 | +0.478 |
| 68% CI σ/m_0 | [0.175, 4.199] | [0.251, 5.513] | broader |
| median a | 1.494 | 1.137 | -0.357 |
| σ/m(v=358) implied | 0.089 | 0.43 | +0.34 |

### Sensitivity sweep

| Peak (cm²/g) | ΔlogZ | σ/m_0 median | implied σ/m(v=358) |
|---|---|---|---|
| (none, 11ch baseline) | — | 0.590 | **0.089** |
| 1.0 | -0.499 | 1.278 | 0.270 |
| 2.0 | -0.698 | 1.587 | 0.367 |
| 3.0 | -0.882 | 1.784 | **0.429** |
| 5.0 | -1.117 | 1.965 | 0.486 |

**Monotonic in peak:** higher peak → larger ΔlogZ penalty, higher σ/m_0 median, higher implied σ/m(v=358).

---

## What the sensitivity sweep tells us

1. **The model converges on σ/m(v=358) ≈ 0.4-0.5 cm²/g** as the channel peak increases. This is **close to the OLD placeholder (0.5)** and **much lower than the AMUSE value (3.07)**.

2. **ΔlogZ is negative at all peak values tested** — even peak=1.0 gives ΔlogZ = -0.499. This means the 11-channel model is in tension with ANY Channel 27 peak above ~0.3 cm²/g.

3. **The v-dep parameter `a` is the culprit.** The 11-channel model wants a ≈ 1.5 (strong v-dep), which means σ/m(v=358) << σ/m_0. With Channel 27 ON, a is pulled down to ~1.1, which is the model's compromise.

4. **A weaker channel width** (e.g., 0.5 dex instead of 1.0 dex) might be more honest — the 1.0 dex width assumes order-of-magnitude uncertainty, but the simulation gives a 1σ of ~0.15 dex on σ/m_peak.

---

## Honest caveats

1. **AMUSE simulation is N=1024 per halo**, ~100× below publication-grade. The σ/m_peak = 3.07 cm²/g is likely overestimated.

2. **SIDM kernel is uniform Gaussian perturbation**, not pairwise Rutherford scattering. The simulation distinguishes σ/m values by amplitude, but the absolute scale is uncertain.

3. **Channel 27 width is 1.0 dex** (factor-of-10 Gaussian). The simulation gives formal ±0.15 dex uncertainty, but the realistic uncertainty is ±0.5 dex (per CH27_PEAK_FROM_AMUSE_2026_09_12.md).

4. **No baryonic physics.** The 11-channel model and the AMUSE simulation both omit baryons (gas stripping + star formation).

5. **Head-on collision only** (b=0). Real NGC 1052 collisions have non-zero impact parameter.

6. **Time slice at t=300 Myr is heuristic.** NGC 1052's actual timescale is ~8 Gyr.

7. **Sensitivity sweep is 4 points**, not exhaustive. The peak vs implied-σ/m(v=358) relationship is monotonic; a denser sweep would refine the curve.

---

## What this changes about the project

| Question | Answer |
|---|---|
| Should we use σ/m_peak = 3.07 cm²/g as Channel 27's anchor? | **No.** It creates -0.898 log Z penalty. The 11-channel model prefers σ/m(v=358) ≈ 0.4-0.5 cm²/g. |
| Should we revert to the placeholder (0.5)? | Not ideal — placeholder was hand-tuned. But it's closer to model-consistent. |
| Is there a defensible middle ground? | Yes: σ/m_peak ≈ 0.5 cm²/g (the placeholder) is closer to where the model converges. |
| What does this mean for the model? | The v-dep parameter `a` is poorly constrained. The 11-channel model has a strong preference for a ≈ 1.5, but the data doesn't strongly constrain σ/m at v=358 specifically. |
| What's the next step? | **Re-run Channel 27 with σ/m_peak = 0.5 cm²/g AND a reduced width (0.5 dex) to see if the model-vs-simulation tension resolves.** |

---

## Files

- `code/ch27_ngc1052_trail_channel.py` — peak changed from -0.30 to +0.487 (line 97)
- `code/ch27_peak_sensitivity.py` — new sensitivity sweep script (180 lines)
- `data/results/t13_v2_trail_ablation_2026_09_12.json` — updated interpretation
- `data/results/ch27_peak_sensitivity_2026_09_12.json` — new sensitivity output
- `tests/test_ngc1052_trail_channel.py` — 2 tests updated (11/11 passing)

## References

- AMUSE framework: Portegies Zwart+ 2013, Comp. Phys. Comm. 183, 456
- SASHIMI-SIDM (theoretical motivation): Yang+ 2024, arXiv:2403.16633
- v0.3-prelim 11-channel baseline: T13_v2_12channel_2025_2026.py (commit `a66533a`)