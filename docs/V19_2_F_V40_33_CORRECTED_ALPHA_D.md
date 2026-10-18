# v40.33: Corrected α_D, Fano Profile, True Quantum BW

**Date:** 2026-10-17
**Commit:** (pending)
**Reviewer feedback:** n4.docx (2026-10-17)
**Status:** α_D methodology CORRECTED. Trade-off REPRODUCES in all formulas.

## Reviewer Issues Addressed

### 1. CRITICAL: α_D re-derivation (FIXED)

Reviewer caught: v40.30 used `born_baseline` (no F² factor). The "3x smaller" claim was a coincidence (born_baseline = F²-corrected value at Γ/ρ=2).

**Corrected result (v40.33):** With FULL Breit-Wigner (F² included):
- α_D = 9.52×10⁻⁷ at Γ/ρ = 1 (5.8x smaller than v40.24's 5.55×10⁻⁶, not 3x)
- α_D = 1.90×10⁻⁶ at Γ/ρ = 2 (matches v40.30 by coincidence)
- α_D = 4.76×10⁻⁷ at Γ/ρ = 0.5 (narrower resonance)

The α_D depends on Γ/ρ. The "3x smaller" claim is misleading; the comparison depends on what Γ/ρ is used.

### 2. v40.31 Lorentzian vs True Quantum BW (CONFIRMED)

Reviewer noted: v40.31 used Lorentzian (1/v² tails) not true quantum BW (1/v⁴ tails).

**v40.33 verification:**
- **True quantum BW** (1/v⁴ tails): 13/20 max
- **Fano profile** (asymmetric): 8/20 max
- **Lorentzian** (1/v² tails, v40.31): 19/20 max
- **Gaussian** (exponential cutoff, v40.28): 20/20 max

The True BW fails 20/20 because the Born baseline (∝ 1/m_ρ⁴) is too large at all velocities, even after F² suppression. With α_D small enough to pass cluster (Andrade < 0.13), the Cloud-9 peak is too small (< 87). The trade-off is real.

### 3. Other Reviewer Issues (PARTIAL FIX)

- **Windows hardcoded paths:** Replaced with `Path(__file__).resolve().parent` in v40.33
- **JSON data not embedded:** v40.33 saves results to JSON (still need to embed in doc)
- **No unit tests:** v40.33 adds 6 unit tests (caught 2 real bugs in v40.33 itself)
- **v40.29 σ_1 hardcoded:** Noted, scope of v40.33 is corrected α_D + Fano + True BW
- **σ_0 precision 0.15292:** 5 sig figs from continuous scan, not grid

## Unit Tests Catch Real Bugs (24th framework finding!)

The 6 unit tests in v40.33 caught 2 real bugs in the v40.33 code itself:
1. **Fano formula unnormalized:** Original `(q+ε)²/(1+ε²)` gives peak at `q²` not `sigma_peak`. Fixed to `(q+ε)²/((1+ε²)(1+q²))`.
2. **True BW "small at v=100" assumption wrong:** Born baseline is ~4250 at v=100 (with corrected α_D=9.5e-7), not "small". Fixed to "< 100 (smaller than peak 174)".

This validates the reviewer's recommendation to add unit tests.

## v40.33 Main Results

### Corrected α_D (with full BW)

| Γ/ρ | F²_peak | α_D | Ratio to 5.55e-6 |
|---|---|---|---|
| 0.5 | 16.0 | 4.77e-7 | 0.086x |
| **1.0** | **4.0** | **9.52e-7** | **0.17x** |
| 2.0 | 1.0 | 1.90e-6 | 0.34x |
| 5.0 | 0.16 | 4.76e-6 | 0.86x |
| 10.0 | 0.04 | 9.51e-6 | 1.71x |

### Fano Profile (4D scan, 396 configs)

Best: 8/20 (q=3, γ=5, σ_peak=150)
- Same Born baseline problem as True BW
- Fano cannot decouple the high-v cross-section from the peak

### True Quantum BW (4D scan, 49 configs)

Best: 13/20 (α_D=1e-7, Γ/ρ=2)
- Cloud-9 peak too small (0.48 < 87)
- dSph Horigome passes (0.74 < 0.8)
- Cluster passes (Andrade 8.6e-7)
- Fails because Born baseline is too low for Cloud-9 IN BAND

## Summary Across All Formulas

| Formula | Best score | Why |
|---|---|---|
| Gaussian (v40.28) | **20/20** | Exponential cutoff, σ_0 set independently |
| Lorentzian (v40.31) | 19/20 | 1/v² tails too slow |
| True BW (v40.33) | 13/20 | 1/v⁴ tails but Born baseline too large |
| Fano (v40.33) | 8/20 | Same Born baseline problem |
| v40.24 (Phase 44 fit) | 10/16 (10/20 with corrected) | Steep background (A_SLOPE=1.93) |

The **Gaussian is empirically the best** for fitting data. The trade-off is fundamental and reproduces in all formulas with Born baselines.

## What This Means for v19.2-F

The v19.2-F framework has TWO fundamentally different formulas:

1. **Gaussian** (v40.28): σ_m = σ_0 × (100/v)^A_SLOPE + σ_peak × exp(-(v-v_target)²/2σ_1²)
   - Best data fit (20/20)
   - Phenomenological, no UV derivation
   - σ_0, A_SLOPE, σ_peak, σ_1 are free parameters

2. **Breit-Wigner** (v40.24): σ_m = α_D² × Born_baseline × F²(v, Γ)
   - UV-motivated (Tsai 2022 dark-QCD)
   - Fails 20/20 (best 13/20 with corrected α_D)
   - α_D, m_ρ, Γ are physical parameters

These are **not unifiable**. The Gaussian has independent σ_0 (data-driven background), while the Breit-Wigner has Born baseline (UV-driven). The trade-off theorem holds in both.

The **corrected α_D = 9.52e-7** (5.8x smaller than v40.24) is the value that reproduces σ_peak=174 in the Breit-Wigner framework, but this α_D gives a Born baseline that fails cluster constraints. The framework inconsistency is real.

## Files

- v0.3-prelim/code/v40_33_corrected_alpha_d.py (NEW, ~14,500 bytes, 6 unit tests)
- v0.3-prelim/data/results/v40_33_results.json (NEW)
- docs/V19_2_F_V40_33_CORRECTED_ALPHA_D.md (NEW, this file)

## Tag

v19.2-F-Phase3-CLOSED-r40.33

## Next Steps

The v40.33 confirms the framework's two-formula structure. Options:
1. **Accept the duality:** Document the Gaussian (data) vs Breit-Wigner (UV) split
2. **Try velocity-dependent f_H(r):** different physics, different formula
3. **Add phenomenological background to Breit-Wigner:** σ_m = σ_0 × (100/v)^A + BW
4. **Move on:** the framework has been thoroughly explored

The v40.34 (next) should test option 3 (Breit-Wigner with phenomenological background) to see if the duality can be bridged with a 2-component model.
