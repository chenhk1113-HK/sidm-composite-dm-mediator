# v40.30: α_D Re-derivation — Framework Inconsistency Found

**Date:** 2026-10-17
**Commit:** (pending)
**Status:** MAJOR FINDING — the v19.2-F framework has TWO incompatible sub-models
**Previous:** v40.28 (20/20 breakthrough) + v40.29 (multi-resonance doesn't widen basin)

## The Question

The user asked to re-derive α_D under v40.28 parameters. The v19.2-F framework has:
- v40.24 α_D = 5.55×10⁻⁶ (from Phase 44 fit, A_SLOPE=1.93, σ_0=0.052, σ_1=4.4)
- v40.28 winning config: A_SLOPE=0.400, σ_0=0.153, σ_1=1.500, σ_peak=174

Does the same α_D work for both parameter sets?

## The Answer: NO

The v19.2-F framework has **two different σ/m formulas** that are not directly compatible:

### Formula 1: Full Breit-Wigner (v19_2_f_priority1_resonance_helpers.py)
```
σ_m(v) = α_D² × Born_baseline × F²(v, γ/ρ)
where:
  Born_baseline = (2π α_D²/μ²) × ∫d(cos θ) [(1-cos θ)/(q² + m_ρ²)²] × (ℏc)² / m_χ
  F² = (q² + m_ρ²)² / [(q² - m_ρ²)² + (m_ρ Γ)²]
```
- Used in v40.5/v40.10 IN BAND analysis (loop 2 regenerator)
- α_D is a fundamental parameter
- σ_m(29.4) = 5,918 cm²/g with α_D = 5.55×10⁻⁶, Γ/ρ = 1
- σ_m(29.4) = 174 cm²/g with α_D = 1.87×10⁻⁶, Γ/ρ = 1

### Formula 2: Paper Canonical (Gaussian Breit-Wigner)
```
σ_m(v) = σ_0 × (100/v)^A_SLOPE + σ_peak × exp(-(v-v_target)²/(2σ_1²))
```
- Used in v40.28 3D parameter scan
- σ_peak, σ_0, A_SLOPE, σ_1 are independent fit parameters
- σ_m(29.4) = 174 cm²/g BY CONSTRUCTION (σ_peak = 174)
- α_D is NOT used in this formula

## Critical Finding: α_D Shifts by 3x

If we force Formula 1 to give σ_m(29.4) = 174 (the v40.28 target), we need:
- **α_D = 1.87×10⁻⁶** (with Γ/ρ = 1)
- This is **0.34× the v40.24 value** of 5.55×10⁻⁶
- Ratio: 1.87e-6 / 5.55e-6 = 0.337

So moving from v40.24 parameters to v40.28 parameters **shifts α_D by a factor of 3**.

## Off-Resonance Behavior

At v = 1458 km/s (cluster scale):
- Formula 1 (Breit-Wigner) with α_D = 1.87×10⁻⁶: σ_m ≈ 5×10⁻⁵ cm²/g
- Formula 2 (Gaussian) with σ_0 = 0.153: σ_m = 0.153 × (100/1458)^0.4 = 0.052 cm²/g

The off-resonance is dominated by **σ_0** (the phenomenological background), not by α_D. The α_D is essentially decoupled from the off-resonance behavior.

## The Framework is Split

The v19.2-F framework has been **de facto split** into two sub-models:

**Sub-model 1 (v40.24 IN BAND analysis):**
- Full Breit-Wigner formula
- α_D = 5.55×10⁻⁶
- A_SLOPE = 1.93, σ_0 = 0.052, σ_1 = 4.4
- σ_peak = 5,918 (at v=29.4)
- IN BAND at Γ/ρ ∈ {6, 7, 8, 9, 10}

**Sub-model 2 (v40.28 parameter scan):**
- Gaussian Breit-Wigner + power-law background
- σ_peak = 174 (by construction)
- A_SLOPE = 0.4, σ_0 = 0.153, σ_1 = 1.5
- No α_D (set independently)
- 20/20 channels pass

**These sub-models are NOT directly compatible.** They use different formulas, different parameters, and different methodologies.

## What This Means

The α_D re-derivation reveals that the v19.2-F framework is now in an **inconsistent state**:

1. **Two different σ/m formulas** coexist in the codebase
2. **The "α_D = 5.55×10⁻⁶" parameter** is tied to Sub-model 1 only
3. **The v40.28 "σ_peak = 174" parameter** is tied to Sub-model 2 only
4. **The two have different predictions** at all velocities

To "re-derive α_D" requires choosing ONE formula. There are two options:

**Option A: Keep Breit-Wigner formula**
- Re-run all v40.28 channels with the new α_D = 1.87×10⁻⁶
- The v40.28 "σ_peak = 174" would become σ_m(29.4) = 174 IN THE BREIT-WIGNER FRAMEWORK
- But the v40.28 channel checks use the GAUSSIAN formula, so this would require re-coding
- The IN BAND analysis (v40.5/v40.10) would need to be re-run with α_D = 1.87×10⁻⁶

**Option B: Keep Gaussian formula**
- Drop the α_D parameter from the framework
- The v19.2-F becomes a phenomenological fit (no UV motivation)
- The IN BAND analysis (v40.5/v40.10) becomes inconsistent with v40.28
- The 22-channel framework becomes a "fit parameters" exercise

Neither option is clean. The framework needs a **decisive choice**.

## What to Do Next (v40.31+)

The user should decide:
1. **Option A:** Re-run all v40.28 channels with Breit-Wigner formula + α_D = 1.87×10⁻⁶
2. **Option B:** Drop α_D, embrace phenomenological fit
3. **Option C:** Try to find a unified formula that bridges both
4. **Option D:** Document the inconsistency and accept the framework as exploratory

## Files

- v0.3-prelim/code/v40_30_alpha_d_derive.py (NEW, 11,315 bytes)
- v0.3-prelim/data/results/v40_30_alpha_d_deriv.json (NEW)
- docs/V19_2_F_V40_30_ALPHA_D.md (NEW, this file)

## Tag

v19.2-F-Phase3-CLOSED-r40.30
