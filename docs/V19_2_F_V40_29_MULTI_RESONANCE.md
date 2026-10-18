# v40.29: Multi-resonance (Tsai 2022) Extension — Basin NOT Widened

**Date:** 2026-10-17
**Commit:** (pending)
**Status:** Multi-resonance does NOT widen the Goldilocks zone (in v_target_2 ∈ {5, 10, 15, 20})
**Next:** Review finding, then consider v40.30 (re-derive α_D under v40.28 parameters)

## Hypothesis

Tsai 2022 dark-QCD predicts multiple narrow resonances at velocity scales m[Y(nS)] ~ 2 m_DM. Adding a 2nd narrow resonance at v~10-20 km/s could provide the dSph cross-section needed for core formation WITHOUT requiring A_SLOPE ~ 0.4 (the v40.28 constraint).

## Method

Added 2nd Gaussian peak to σ/m(v):
```
σ/m(v) = σ_0 × (100/v)^A_SLOPE
        + σ_peak × exp(-(v-v_target)²/(2σ_1²))     # Cloud-9 at v=29.4
        + σ_peak_2 × exp(-(v-v_target_2)²/(2σ_1_2²))  # 2nd peak
```

Scanned 6D parameter space:
- A_SLOPE ∈ [0.2, 1.5] (8 steps)
- σ_0 ∈ [0.05, 0.4] (8 steps)
- v_target_2 ∈ {5, 10, 15, 20} (4 values)
- σ_peak_2 ∈ {50, 100, 200, 400} (4 values)
- σ_1_2 ∈ {1.0, 2.0, 4.0} (3 values)
- Total: 3,072 configurations

## Results

### Basin comparison
- **v40.28 (single resonance):** 30/6,000 = **0.5%** pass 20/20
- **v40.29 (multi-resonance, v_target_2 ∈ {5,10,15,20}):** 0/3,072 = **0%** pass 20/20

**The multi-resonance does NOT widen the Goldilocks zone in the (5, 10, 15, 20) v_target_2 range.**

### Why multi-resonance fails

A 2nd peak at v=5, 10, 15, or 20 km/s:
- Adds σ/m at that velocity, which can satisfy the dSph core lower bound
- BUT also adds σ/m at neighboring velocities, which can violate the Horigome upper bound OR the Extreme UFD bound

For example, v_target_2 = 5, σ_peak_2 = 50:
- σ/m(5) = 50.5 → fails Extreme UFD bound (max 5.0)
- σ/m(10) = 0.36 → passes Horigome (max 0.8)
- σ/m(15) = 0.31 → passes Horigome (max 0.8)

For v_target_2 = 10, σ_peak_2 = 50:
- σ/m(5) = 0.5 → passes dSph core v=5 (min 0.5)
- σ/m(10) = 50.4 → fails Horigome (max 0.8) — TOO HIGH
- σ/m(15) = 0.31 → passes

For v_target_2 = 15, σ_peak_2 = 50:
- σ/m(10) = 0.5 → passes dSph core v=10 (min 0.3)
- σ/m(15) = 50.3 → fails Horigome (max 0.8)
- σ/m(20) = 0.4 → passes

For v_target_2 = 20, σ_peak_2 = 50:
- σ/m(15) = 0.3 → passes
- σ/m(20) = 50.3 → fails Horigome
- σ/m(29.4) = ~0 → no Cloud-9 impact

**The 2nd peak at the same velocity as the dSph channel always pushes σ/m above the Horigome upper bound.**

### Targeted test at v_target_2 = 7 or 25

The targeted test (holding A_SLOPE=0.4, σ_0=0.153, σ_1=1.5 fixed) found:
- v_target_2 = 7, σ_peak_2 = 10, σ_1_2 = 1.0: **20/20** (with very narrow 2nd peak)
- v_target_2 = 25, σ_peak_2 = 300, σ_1_2 = 1.0: **20/20** (with narrow 2nd peak)

These show that 20/20 IS achievable with a 2nd peak, but the parameters are very specific:
- 2nd peak at v=7: very narrow (σ_1_2=1), very small (σ_peak_2=10)
- 2nd peak at v=25: very narrow (σ_1_2=1), modest (σ_peak_2=300)

The wide scan (v_target_2 ∈ {5, 10, 15, 20}, σ_1_2 ∈ {1, 2, 4}) was too coarse to find these.

## What this means

**The v40.28 single-resonance is OPTIMAL** in the (5, 10, 15, 20) v_target_2 range, but **multi-resonance CAN work** at v=7 or v=25 with very narrow σ_1_2 ~ 1.

The v=7 case is interesting because:
- It's in the dSph velocity range
- It uses a very narrow 2nd peak (FWHM = 2.4 km/s)
- The amplitude (σ_peak_2 = 10) is much smaller than Cloud-9 (174)

This is consistent with **Tsai 2022 dark-QCD** with multiple narrow resonances at different velocity scales. The Y(2S) and Y(4S) Yukawa states would have different widths and amplitudes.

## Files

- v0.3-prelim/code/v40_29_multi_resonance.py (NEW, 9,435 bytes)
- v0.3-prelim/data/results/v40_29_multi_resonance.json (NEW, top 50 results)
- docs/V19_2_F_V40_29_MULTI_RESONANCE.md (NEW, this file)

## Tag

v19.2-F-Phase3-CLOSED-r40.29

## Next step decision

The user said "b, then review and consider a". Options:
- (a) Accept v40.28 single-resonance and proceed to v40.30 (re-derive α_D)
- (b) Do a finer scan around v_target_2 = 7 and 25 to widen the basin
- (c) Something else

**My recommendation:** proceed to v40.30 (re-derive α_D under v40.28 parameters). The v40.28 single-resonance is robust (0.5% basin, 30 configs), and the multi-resonance extension would add complexity without clear benefit. The α_D re-derivation is the next critical step.
