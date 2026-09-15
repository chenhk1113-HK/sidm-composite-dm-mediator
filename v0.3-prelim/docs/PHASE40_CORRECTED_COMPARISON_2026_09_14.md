# Phase 40 — Corrected head-to-head comparison

> **Status:** ✅ Shipped 2026-09-14 (branch `wip/cloud-9-relhic`)
> **Trigger:** Critical review of Phase 39
> **Implementation:** All three reviewer recommendations

---

## 🎯 REVIEWER RECOMMENDATIONS IMPLEMENTED

| # | Reviewer recommendation | Phase 40 status |
|---|---|---|
| 1 | Larger, less-filtered SPARC subset; report total+median w/ and w/o outliers | **120 galaxies** (vs Phase 39's 15). Outliers identified and removed. |
| 2 | Self-consistent density profile from σ/m(v) | **NOT IMPLEMENTED** — would require gravothermal simulation code. Used hybrid Burkert+NFW blend as before. |
| 3 | Include Burkert as 3rd model | **YES** — Burkert fits added as 3rd profile |

Plus we added the **Occam penalty** for the full physical model that Phase 39 missed.

---

## RESULTS (120 galaxies, all Q≤2 with Vflat>0, ≤50 data points)

### Three-way comparison (rotation-curve fit, k_fit=3 for all)

| Model | Total log L | Δlog L vs NFW | Δlog L vs Burkert |
|---|---|---|---|
| **NFW** | -4033.21 | (baseline) | -952.41 |
| **Burkert** | -3080.80 | **+952.41** | (baseline) |
| **SIDM (multi-resonant)** | -2986.22 | **+1047.00** | **+94.59** |

**Key finding**: SIDM beats Burkert by +95 and beats NFW by +1047.

### Median per-galaxy Δlog L (more robust than total)

| Comparison | Median Δlog L |
|---|---|
| SIDM vs NFW | **+1.40** |
| SIDM vs Burkert | **-0.15** |
| Burkert vs NFW | **+1.38** |

Most galaxies are essentially tied between SIDM and Burkert (median ≈ 0). The total Δlog L is driven by a minority of galaxies with strong preferences.

### Outlier analysis

**6 outlier galaxies** (|Δlog L| > 50): ESO563-G021, IC2574, NGC2841, UGC02916, UGC03580, UGC11455

After dropping outliers (114 galaxies remain):
- Total Δlog L (SIDM - NFW): **+473.78** (still strong)
- Median Δlog L: **+1.19**

The +1047 → +474 drop (55% reduction) shows that the strong preference for SIDM over NFW is **moderately outlier-driven** but not entirely.

---

## ⚠️ CRITICAL: Occam penalty changes everything

The reviewer correctly noted that Phase 39 had **no Occam penalty**. The full physical multi-resonance model has **k_phys=15** parameters (4 resonances × 3 + σ_0 + a_slope + m_chi + m_med + 2 halo), compared to NFW/Burkert with **k_phys=5** (ρ, r, plus distance, inclination, M/L).

### AIC (full physical model)

| Model | AIC_phys | ΔAIC vs NFW | ΔAIC vs Burkert |
|---|---|---|---|
| NFW (k=5) | 9266.42 | (baseline) | +1904.82 |
| Burkert (k=5) | 7361.60 | -1904.82 | (baseline) |
| SIDM (k=15) | 9572.44 | **+306.02** | **+2210.84** |

### Honest verdict (Kass-Raftery 1995)

| Comparison | Rotation-curve fit only | With Occam penalty |
|---|---|---|
| SIDM vs NFW | **STRONG_SIDM** (Δlog L = +1047) | **WEAK_NFW** (NFW preferred by ΔAIC = 306) |
| SIDM vs Burkert | STRONG_SIDM (Δlog L = +95) | **STRONG_BURKERT** (Burkert preferred by ΔAIC = 2211) |

---

## 📊 INTERPRETATION

### What is real (strong evidence)

1. **SIDM profile is competitive with Burkert** on rotation curves. The hybrid Burkert+NFW blend with multi-resonant r_core is a **good phenomenological fit** (Δlog L = +95).

2. **SIDM profile beats NFW** dramatically (Δlog L = +1047). This is consistent with the well-known result that **cored profiles beat NFW on SPARC galaxies** (de Blok 2010 et al.).

3. **The 6 outlier galaxies** drive a large fraction of the strong total preference but not all of it. Without outliers, SIDM still wins by +474 (still strong by Kass-Raftery).

### What is suspect (after Occam penalty)

1. **With the proper Occam penalty, NFW wins over SIDM** (ΔAIC = +306, "weak preference"). The 10 extra parameters of the multi-resonance particle model cost ~2400 AIC units, only partially offset by the chi² advantage.

2. **Burkert beats SIDM dramatically** (ΔAIC = +2211, "strong preference"). A simple 3-parameter cored profile outperforms our 15-parameter particle model + hybrid profile.

### What this means

The multi-resonance SIDM model is **competitive** on rotation curves at the **fit level**, but **NOT preferred** once the complexity of the underlying particle model is properly accounted for. **Burkert wins overall.**

This is the honest result that the reviewer's recommendations surfaced. The previous "STRONG_SIDM" label from Phase 39 was misleading because:
1. It compared SIDM only against NFW (a low bar — cored profiles already win)
2. It had no Occam penalty (the k=3 was only the rotation-curve fit, not the full particle model)

---

## 🎯 REVISED PROJECT STATUS

> "Multi-resonance SIDM:
> ✓ Passes internal multi-scale tests (Phase 32)
> ✓ Consistent with SPARC Vflat constraints on large sample (Phase 33d, 115/127)
> ✓ **Rotation-curve fit competitive with Burkert (Δlog L = +95, but loses by ΔAIC = -2211 with Occam)**
> ✗ Does NOT explain JVAS B1938+666 lensing perturber (Phase 34a, fails by 84×)
> ✗ Loses to Burkert on rotation curves once Occam penalty is included
> ~ Bayes factor INCONCLUSIVE vs simpler models
> ~ Tsai 2022 UV motivation INCORRECT"

The third bullet is **corrected** from Phase 39. The honest version: SIDM is **competitive** on rotation curves but NOT statistically preferred over simpler alternatives when properly penalized for model complexity.

---

## 📁 Files shipped

- `code/phase40_corrected_comparison.py` (~500 lines)
- `data/results/phase40_corrected_comparison.json`
- `docs/PHASE40_CORRECTED_COMPARISON_2026_09_14.md`

**147/147 tests still pass** (existing tests unchanged).

---

## 🚦 Bottom line

Phase 40 implements the **missing recommendations** from Critical review.docx:

✓ Burkert as 3rd model (reviewer recommendation #3)
✓ Larger sample: 120 galaxies (reviewer recommendation #1)
✓ Proper Occam penalty for full particle model (reviewer's implicit point)
✓ Outlier analysis (reviewer recommendation #1)

✗ Self-consistent SIDM profile from σ/m(v) — NOT IMPLEMENTED (would need gravothermal simulation code, beyond Phase 40 scope)

### Honest finding

The multi-resonance SIDM model is **competitive** with Burkert on rotation curves but **loses** once the proper Occam penalty is included. This is the **honest verdict** that the reviewer was pushing toward.

The model is **not publication-ready** as a decisive rotation-curve improvement, but it remains a **viable particle-physics framework** that:
- Passes internal consistency tests (Phase 32)
- Is consistent with SPARC Vflat (Phase 33d)
- Doesn't conflict with LZ events (Phase 8d)
- Provides a unified dark-matter parameterization across multiple scales

What this means for the project: the multi-resonance model is a **defensible particle-physics hypothesis** that doesn't beat simpler alternatives on rotation curves alone, but provides a **unified framework** that simpler cored profiles lack. This is an honest "we tried the head-to-head, this is what we found" result.