# v40.31: Unified Formula — NEGATIVE Result

**Date:** 2026-10-17
**Commit:** (pending)
**Status:** NEGATIVE — the unified Breit-Wigner formula CANNOT pass all 20 channels
**Previous:** v40.30 (framework inconsistency) → v40.31 (unified formula attempt)

## Hypothesis Tested

A unified formula can bridge v40.24 (Breit-Wigner with α_D) and v40.28 (Gaussian phenomenological):

```
σ_m(v) = σ_0 × (100/v)^A_SLOPE         [phenomenological background]
       + σ_peak × Γ² / (4(v-v_peak)² + Γ²)  [Breit-Wigner peak]
```

This is a "phenomenological Breit-Wigner" with:
- Free amplitude (σ_peak) — matches v40.28
- Free width (Γ) — new parameter (replaces σ_1)
- Phenomenological background — matches v40.28
- Physical motivation: Tsai 2022 dark-QCD with narrow resonances

## Result: 19/20, NOT 20/20

The 4D scan (1,512 configurations) found:
- **Best score: 19/20** (not 20/20)
- 67 configurations pass 19/20 (4.4% basin)
- The 1 failure is **Cloud-9 kinematic at v=28**

The failure is **fundamental**, not a tuning issue. For every (σ_peak, Γ) tested:
- Cloud-9 kinematic passes only when Γ is large enough (Γ > 2 km/s)
- But dSph Horigome passes only when Γ is small enough (Γ < 1.5 km/s)
- **No (σ_peak, Γ) satisfies both simultaneously**

## Why the Trade-off is Real

The Cloud-9 IN BAND requires σ_m(28) ∈ [87, 348]. For a Breit-Wigner:
```
σ_m(28) = σ_peak × Γ² / (4×(28-29.4)² + Γ²) = σ_peak × Γ² / (15.68 + Γ²)
```

For σ_m(28) ≥ 87 with σ_peak = 174:
- Γ² = 87 × 15.68 / (174 - 87) = 7.84
- **Γ = 2.8 km/s** (minimum to pass Cloud-9 kinematic)

But with Γ = 2.8, the dSph tail at v=20 is:
```
σ_m(20) = 174 × 7.84 / (4×88.4 + 7.84) = 174 × 0.0217 = 3.78
```

This **FAILS** the Horigome v=20 upper limit (0.8).

The fundamental issue: the Breit-Wigner tail decays as 1/q⁴, which is too slow. To be wide enough for Cloud-9 IN BAND, the resonance pollutes dSph velocities.

## Why the Gaussian is Better

The v40.28 Gaussian (σ_1 = 1.5) achieves 20/20 because:
- The Gaussian has FWHM = 2.355 × 1.5 = 3.53 km/s (similar to Γ = 1.77 Breit-Wigner)
- But the Gaussian TAIL is exp(-(v-v_peak)²/2σ²) — exponentially small
- At v=20 (1.4 km/s from peak in FWHM units, 6.3σ away), Gaussian is essentially 0
- At v=15, similar — Gaussian is essentially 0

The Gaussian's exponential cutoff is the key feature that the Breit-Wigner lacks.

## The v19.2-D Trade-off Theorem — REPRODUCED

This is a **reproduction of the v19.2-D trade-off theorem** in the Breit-Wigner formula:

> Any single σ/m(v) curve with a single resonance cannot simultaneously satisfy:
> - Cloud-9 IN BAND: σ_m(28) ≥ 87
> - dSph Horigome: σ_m(20) < 0.8
> 
> with the same (σ_peak, Γ).

The trade-off is **fundamental**, not specific to the Gaussian formula. The v40.28 Gaussian evades this by having an exponentially small tail at v=20 — but the Gaussian is phenomenological, not UV-motivated.

## What This Means for the v19.2-F Framework

The "unified formula" approach **does not work**. The v19.2-F has two formulas because they have different uses:

| Formula | Use | Strength | Weakness |
|---|---|---|---|
| Gaussian (v40.28) | Data-driven fit to channels | Exponential cutoff, fits 20/20 | Not UV-motivated |
| Breit-Wigner (v40.24) | IN BAND analysis | Physically motivated (Tsai 2022) | 1/q⁴ tails fail dSph |

The framework must choose ONE formula:
- **Gaussian:** better for fitting data, but phenomenological
- **Breit-Wigner:** better for UV motivation, but fails 20/20 channels

## What Could Work

The unified formula approach fails because no single-resonance curve can pass both. To unify, we would need:

1. **Fano profile** (asymmetric line shape) — could have a peak at v=29.4 and a dip at v=20
2. **Multi-resonance with proper UV** (Tsai 2022 with v_target_2 at v=7 or v=25) — already tried in v40.29, only works in narrow regions
3. **Different f_H(r)** — affects the MB-weighted σ_eff, not the σ/m(v) per se
4. **Density-dependent scattering** — different mechanism at different scales

The most promising is **Fano profile**, which has both peak and dip. This is a known physics phenomenon (atomic physics, photonic crystals) but has not been explored in SIDM.

## Files

- v0.3-prelim/code/v40_31_unified_formula.py (NEW, 9,076 bytes)
- v0.3-prelim/data/results/v40_31_unified.json (NEW)
- docs/V19_2_F_V40_31_UNIFIED_FORMULA.md (NEW, this file)

## Tag

v19.2-F-Phase3-CLOSED-r40.31

## Conclusion

The v19.2-F framework's two sub-models (Gaussian for v40.28, Breit-Wigner for v40.24) are **fundamentally different formulas** that cannot be unified. The trade-off theorem is real and reproduces in both formulas. The Gaussian is empirically better but lacks UV motivation.

This is a **negative result** for the unified formula approach. The framework should either:
- Accept the duality (Gaussian for data, Breit-Wigner for UV)
- Try Fano profile (Option C extension)
- Document the trade-off and move on (Option D)
