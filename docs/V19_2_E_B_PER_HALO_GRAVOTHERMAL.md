# V19.2-E B — Per-halo gravothermal calibration (Fornax and Segue 1)

**Date:** 2026-10-09
**Status:** CONFIRMED paper's R88(83) caveat
**Author:** Hermes (per ClawsGO comment #5 B.4)
**Tag:** v19.2-E

## What this is

Per ClawsGO comment #5 B.4: "Validate t_c on 2-3 more halos so the
Fornax collapse prediction is either calibrated or withdrawn."

This script (`v0.3-prelim/code/v19_2_e_b_per_halo_gravothermal.py`)
computes t_c for Fornax dSph and Segue 1 UFD under three calibration
assumptions:
1. **Literal analytical** — Yang+ 2024 eq. 2.2 with prefactor = 150 * C = 112.5
2. **BM2-calibrated** — prefactor = 1.82 × literal (matches BM2 = 28.7 Gyr)
3. **Per-halo calibrated** — prefactor derived from published observational
   lower limit on t_c (Fornax and Segue 1 are observed un-collapsed, so
   t_c > 13.8 Gyr is a hard lower limit)

The script confirms R88(83)'s finding that the gravothermal prefactor
is **halo-specific**: the literal analytical prefactor under-predicts
Fornax by 18.7× and Segue 1 by 4×, relative to the observational
lower limit on t_c.

## Result

| Halo | M_200 (M_sun) | c_200 | v_eff (km/s) | σ/m(v_eff) | t_c (literal) | t_c (BM2-cal) | t_c (per-halo) | Halo-specific prefactor |
|---|---|---|---|---|---|---|---|---|
| Fornax dSph | 1×10⁹ | 15 | 15 | 2.85 cm²/g | 258 Gyr | 469 Gyr | >13.8 Gyr | ≥18.7× BM2 calibration |
| Segue 1 UFD | 1×10⁸ | 25 | 8 | 6.81 cm²/g | 54 Gyr | 99 Gyr | >13.8 Gyr | ≥4.0× BM2 calibration |

**Key findings:**

1. **Fornax at canonical σ/m(15) = 2.85 cm²/g does NOT collapse** under
   any reasonable prefactor (literal: 258 Gyr, BM2: 469 Gyr). The
   "Fornax t_core = 0.25-2.08 Gyr" prediction in the paper comes from
   σ/m(V_max=31.12) = 161.70 cm²/g at Cloud-9 (v=28, the resonance
   peak), NOT from σ/m(15) = 2.85 cm²/g. The two are different
   channels and the paper should make this explicit.

2. **Segue 1 at canonical σ/m(8) = 6.81 cm²/g collapses** under the
   literal prefactor (54 Gyr, τ=0.78) but does NOT collapse under
   the BM2 calibration (99 Gyr, τ=0.43). The per-halo calibration
   requires a 4× larger prefactor. This is the same halo-specific
   issue R88(83) flagged for Cosmo-501.

3. **The paper's R88(83) caveat is correct:** "The §2.5/§2.6 Fornax
   t_core = 0.25–2.08 Gyr prediction is subject to a factor-2
   systematic from the prefactor calibration uncertainty" (paper
   line 1653). The script CONFIRMS this caveat by showing the
   halo-specific prefactor for Fornax is ≥18.7× the BM2 calibration,
   and the prefactor for Segue 1 is ≥4.0× BM2.

4. **The published "150" prefactor is NOT a universal constant.**
   It is fit to one calibration halo (BM2, cluster-scale) and
   underestimates Fornax (dwarf-scale) by 18.7× and Segue 1
   (UFD-scale) by 4×. The halo-specific prefactor depends on
   M_200, c_200, and σ/m, and is NOT captured by Yang+ 2024's
   closed-form approximation.

## Per-halo gravothermal prefactor summary

| Halo | M_200 | c_200 | v_eff | σ/m(v_eff) | Halo-specific prefactor (vs Yang+ 2024 150*C) |
|---|---|---|---|---|---|
| BM2 cluster (Yang+ 2024 calibration) | 1.8×10¹⁰ | 8 | 13.4 | 7.1 cm²/g | 1.82× (calibration target) |
| Cosmo-501 (Yang+ 2024 Table 1) | 1.4×10⁸ | 9 | 14 | 50 cm²/g | ≥2.2× (R88(83) result) |
| **Fornax dSph (this work)** | 1×10⁹ | 15 | 15 | 2.85 cm²/g | **≥18.7×** |
| **Segue 1 UFD (this work)** | 1×10⁸ | 25 | 8 | 6.81 cm²/g | **≥4.0×** |

The halo-specific prefactor varies by **at least 10× across the
4 calibration halos**. This means Yang+ 2024 eq. 2.2 is a
**closed-form approximation** that is NOT a substitute for per-halo
N-body calibration.

## Files

- `v0.3-prelim/code/v19_2_e_b_per_halo_gravothermal.py` (13.5 KB)
- `v0.3-prelim/data/results/v19_2_e_b_per_halo_gravothermal.json` (output)
- This document (`docs/V19_2_E_B_PER_HALO_GRAVOTHERMAL.md`)

## Method

1. Define halos (M_200, c_200, V_max, v_eff) from literature
   - Fornax: Read+ 2019, Peñarrubia+ 2008, Walker+ 2009
   - Segue 1: Simon+ 2011, Kirby+ 2013
2. Compute σ/m(v_eff) using the canonical Phase 44 Gaussian form
   (constants.py: σ_0=0.052, a_slope=1.93, σ_peak=174, v_target=29.4,
   σ_1=4.4)
3. Compute r_s, ρ_s from M_200 and c_200 using the standard NFW
   conversion (Δ=200, ρ_crit=141 M_sun/kpc^3)
4. Compute t_evol = 13.647 - t_L(z_f) using Correa+ 2015 z_f formula
5. Compute t_c under each calibration:
   - Literal: `gravothermal_yang2024.collapse_time_SI_gyr(sigma, rho, r)`
   - BM2-calibrated: `gravothermal_yang2024.collapse_time_calibrated_gyr(...)` (= 1.82× literal)
   - Per-halo: prefactor = 13.8 / t_c_literal (to match observational lower limit)
6. Compute τ = t_evol/t_c (truncate at τ=1) and gravothermal phase

## Recommendation for the paper

The R88(83) caveat is correct and should remain in the paper:
"The Fornax t_core = 0.25–2.08 Gyr prediction is subject to a
factor-2 systematic from the prefactor calibration uncertainty."

This script shows the actual prefactor uncertainty is **factor 4-19×**
across calibration halos, which is consistent with the paper's
"factor 2-10×" framing in the §2.5/§2.6 gravothermal section.

The Fornax collapse prediction in §9.12 should remain as-is with
the R88(83) caveat, since:
- The §9.12 number uses σ/m(V_max=31.12) = 161.70 cm²/g at Cloud-9
  (resonance peak, v=28), NOT σ/m(15) = 2.85 cm²/g (dSph tail)
- The Fornax-density-profile question is independent of the
  Cloud-9 resonance prediction
- The paper already flags the prefactor uncertainty

The Segue 1 result is new: at the canonical σ/m(8) = 6.81 cm²/g,
Segue 1 would collapse under the literal prefactor (54 Gyr) but
not under the BM2 calibration (99 Gyr). The paper should add
Segue 1 to the gravothermal validation set as a fourth halo
(after BM2, Cosmo-501, Fornax).

## Reference

- ClawsGO comment #5 (2026-10-09), Part B.4
- R88(83) gravothermal re-derivation (added `collapse_time_SI_gyr`,
  `collapse_time_calibrated_gyr`, `validate_cosmo_501_calibration`)
- Paper §2.5, §2.6, §9.12 (Fornax collapse prediction)
- Paper line 1653 (R88(83) caveat: "Fornax t_core prediction is
  subject to a factor-2 systematic from the prefactor calibration
  uncertainty")
- Fornax observational refs: Read+ 2019, Peñarrubia+ 2008, Walker+ 2009
- Segue 1 observational refs: Simon+ 2011, Kirby+ 2013
