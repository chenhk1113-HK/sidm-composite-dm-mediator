# v40.7 — Gravothermal t_c with Breit-Wigner σ/m (Loop 4, follow-up to Loops 1 & 3)

**Date:** 2026-10-17
**Branch:** `wip/v19.2-F-init`
**Tag:** `v19.2-F-Phase3-CLOSED-r40.7` (pending)

---

## TL;DR

At the canonical α_D = 5.55×10⁻⁶ with the **Breit-Wigner resonance σ/m formula** (the v40.1-v40.5 IN BAND framework), the predicted gravothermal collapse time **t_c is much longer than 13.8 Gyr for all 5 UFDs tested** (Segue 1, Tucana II, Hercules, Draco, Bootes I) across the full Γ/ρ ∈ [1, 20] sweep.

**Implication:** the v19.2-F model is **consistent with the observed non-collapse** of UFDs, and is also consistent with the **Gilman+ 2023 (arXiv:2207.13111) lensing constraint** (which disfavors models where many halos core collapse). The v19.2-F Phase 3 "FAIL" verdict is about the UV-sector derivation of the σ/m(v) curve, not about the σ/m value being unphysical.

**This closes the Loop 1 follow-up** (v40.4 noted: "a proper gravothermal t_c analysis using the resonance σ/m formula (with full Γ/ρ sweep) would need to be done to make a coherent statement about Segue 1's collapse status"). With Loop 4, that analysis is done.

---

## Method

For each halo, compute:
1. **NFW profile parameters** (r_s, ρ_s) from M_200, c_200, V_max using `gravothermal_yang2024.nfw_rho_s_from_vmax`. Specifically: ρ_s is the NFW scale density (M_⊙/kpc³), r_s is the NFW scale radius (kpc). These are obtained from V_max and r_s via the NFW relation ρ_s = (V_max / (1.648 r_s))² / G.
2. **Velocity-weighted σ_eff** using the Breit-Wigner `sigma_m_resonance` formula (the same as v40.1-v40.5), with full Γ/ρ ∈ [1, 20] sweep. σ_eff is in cm²/g.
3. **Gravothermal t_c** using `gravothermal_yang2024.collapse_time_SI_gyr(sigma_eff_per_m, rho_eff=ρ_s, r_eff=r_s)`. The function `collapse_time_SI_gyr` takes (σ_eff in cm²/g, ρ_eff in M_⊙/kpc³, r_eff in kpc) and applies Yang+ 2024 eq. 2.2 with the literal 150×C = 112.5 prefactor:
   ```
   t_c = 150 * C / (σ_eff/m × ρ_eff × r_eff × sqrt(4π G ρ_eff))
   ```
   In Loop 4, ρ_eff = ρ_s (NFW scale density) and r_eff = r_s (NFW scale radius).

Compare t_c to the 13.8 Gyr Hubble time. If t_c > 13.8 Gyr, the halo is predicted to NOT have core-collapsed — consistent with observation.

---

## Halo parameters

| Halo | M_200 (M☉) | c_200 | V_max (km/s) | σ_v (km/s) | r_s (kpc) | ρ_s (M☉/kpc³) |
|---|---|---|---|---|---|---|
| Segue 1 | 1.0×10⁸ | 25.0 | 8.0 | 3.7 | 39.3 | 3.25×10³ |
| Tucana II | 5.7×10⁶ | 28.0 | 6.5 | 8.2 | 13.5 | 1.82×10⁴ |
| Hercules | 1.0×10⁷ | 25.0 | 6.0 | 3.7 | 18.2 | 8.48×10³ |
| Draco | 2.0×10⁹ | 20.0 | 17.0 | 10.6 | 133.3 | 1.27×10³ |
| Bootes I | 1.0×10⁷ | 25.0 | 6.5 | 6.5 | 18.2 | 9.95×10³ |

σ_v values from Simon+ 2011, Walker+ 2016, Adén+ 2009, Walker+ 2007, Koposov+ 2011.

---

## Results: t_c vs Γ/ρ

For each halo, t_c in Gyr at canonical α_D = 5.55×10⁻⁶ and Breit-Wigner σ/m. The "Consistent" column is YES iff t_c > 13.8 Gyr (halo not yet collapsed, consistent with observation).

### Segue 1 (M_200 = 10⁸, σ_v = 3.7 km/s)

| Γ/ρ | σ_eff (cm²/g) | t_c (Gyr) | Consistent (>13.8)? |
|---|---|---|---|
| 1.0 | 6,694 | 1,473 | YES |
| 5.0 | 495 | 19,924 | YES |
| 6.0 | 347 | 28,380 | YES |
| 7.0 | 257 | 38,374 | YES |
| 8.0 | 198 | 49,905 | YES |
| 9.0 | 157 | 62,974 | YES |
| 10.0 | 127 | 77,580 | YES |
| 11.0 | 105 | 93,724 | YES |
| 12.0 | 88 | 111,405 | YES |
| 15.0 | 57 | 173,673 | YES |
| 20.0 | 32 | 308,204 | YES |

### Tucana II (M_200 = 5.7×10⁶, σ_v = 8.2 km/s)

| Γ/ρ | σ_eff (cm²/g) | t_c (Gyr) | Consistent? |
|---|---|---|---|
| 1.0 | 5,970 | 364 | YES |
| 5.0 | 383 | 5,665 | YES |
| 8.0 | 152 | 14,268 | YES |
| 10.0 | 98 | 22,209 | YES |
| 15.0 | 44 | 49,782 | YES |
| 20.0 | 25 | 88,385 | YES |

### Hercules (M_200 = 10⁷, σ_v = 3.7 km/s)

| Γ/ρ | σ_eff (cm²/g) | t_c (Gyr) | Consistent? |
|---|---|---|---|
| 1.0 | 6,694 | 752 | YES |
| 5.0 | 495 | 10,175 | YES |
| 8.0 | 198 | 25,486 | YES |
| 10.0 | 127 | 39,619 | YES |
| 20.0 | 32 | 157,394 | YES |

### Draco (M_200 = 2×10⁹, σ_v = 10.6 km/s)

| Γ/ρ | σ_eff (cm²/g) | t_c (Gyr) | Consistent? |
|---|---|---|---|
| 1.0 | 5,824 | 2,031 | YES |
| 5.0 | 340 | 34,740 | YES |
| 8.0 | 135 | 87,779 | YES |
| 10.0 | 87 | 136,735 | YES |
| 20.0 | 22 | 544,706 | YES |

### Bootes I (M_200 = 10⁷, σ_v = 6.5 km/s)

| Γ/ρ | σ_eff (cm²/g) | t_c (Gyr) | Consistent? |
|---|---|---|---|
| 1.0 | 6,157 | 643 | YES |
| 5.0 | 421 | 9,404 | YES |
| 8.0 | 168 | 23,632 | YES |
| 10.0 | 108 | 36,765 | YES |
| 20.0 | 27 | 146,207 | YES |

---

## Summary: at canonical α_D, model predicts no UFD core collapse

For all 5 halos and all tested Γ/ρ ∈ [1, 20], the predicted t_c is much longer than the 13.8 Gyr Hubble time. **No halo in this set would have core-collapsed by today**, consistent with the observed un-collapsed state of all 5 UFDs.

The shortest t_c is for Tucana II at Γ/ρ=1 (364 Gyr, 26× the Hubble time). Even this is much longer than 13.8 Gyr.

---

## Implication for Gilman+ 2023 (Loop 3 follow-up, revised per Nemotron 120B review)

Gilman+ 2023 disfavors scenarios where a **population-level fraction** of halos in their strong-lensing sample have core-collapsed by z~0.5 (corresponding to ~5 Gyr lookback time for low-z halos). The Loop 4 result shows that at canonical α_D, the v19.2-F model predicts t_c >> 13.8 Gyr for 5 specific UFDs across the full Γ/ρ sweep — these individual halos would NOT have collapsed.

**But:** showing 5 specific UFDs have t_c >> 13.8 Gyr does NOT directly address Gilman+ 2023's population-level constraint. A complete Gilman+ 2023 test would require:
- Integration over the halo mass function (Gilman+ 2023 uses ~10⁷-10⁹ M☉ halos for lensing, but the fraction depends on the full mass distribution).
- The predicted collapsed-halo fraction in the lensing sample (a number Gilman+ 2023 directly constrains).
- Comparison to Gilman+ 2023's allowed region in the (σ/m, core-collapse-fraction) plane.

What Loop 4 shows: **at the canonical α_D, the model does NOT predict early UFD core collapse.** This is a necessary condition for consistency with Gilman+ 2023, but not a sufficient one. The full Gilman+ 2023 test would need a population-level analysis (out of scope for Loop 4).

**Caveat (honest limitation):** the Loop 4 calculation uses the **literal Yang+ 2024 prefactor** (150×C = 112.5). The actual gravothermal t_c from N-body simulations is 1.82× longer (BM2-calibrated). So t_c values should be 1.82× larger than shown — all still > 13.8 Gyr. The conclusion is robust to this calibration.

**Caveat 2:** the calculation uses NFW profile parameters (r_s, ρ_s) derived from M_200 and c_200. For Tucana II, the M_200 and c_200 are uncertain; the choice here (5.7×10⁶, 28) is one of several literature values. Other choices would shift r_s and ρ_s by factors of a few, which would shift t_c by similar factors. All shifts keep t_c > 13.8 Gyr.

**Caveat 3 (LMC/MW-mass halos):** the Loop 4 analysis is for UFD/dSph mass halos (M_200 ~ 10⁶-10⁹ M☉). At MW-mass (M_200 ~ 10¹² M☉) or cluster (M_200 ~ 10¹⁴ M☉), the t_c formula gives different values (much shorter for the same σ/m because ρ_s is higher). A complete analysis would test the model across all halo mass scales, including MW-mass (where strong cluster constraints apply).

---

## What this Loop 4 does NOT do

1. **Does not check the cluster-scale.** Gilman+ 2023's cluster constraints (σ/m < 0.1-1.0 cm²/g at v ~ 1000 km/s) and O'Donnell+ 2025 (single cluster) are at v ~ 1000 km/s, not at UFD v ~ 5 km/s. The Breit-Wigner σ/m at v = 1000 km/s is way off-resonance and would give the Born baseline, which is α_D² × constant. At α_D = 5.55e-6, this would be very small (~10⁻³ cm²/g or less), consistent with the cluster constraints. This should be verified explicitly.
2. **Does not derive σ/m from a UV sector.** The Phase 3 "FAIL" verdict (no first-principles UV sector reproduces the canonical σ/m) is unchanged. This Loop 4 shows the σ/m VALUE is consistent with observations, but the UV-sector derivation is still missing.
3. **Does not include the BM2-calibrated prefactor.** Uses the literal Yang+ 2024 prefactor. The BM2-calibrated (1.82×) would shift t_c by a constant factor, all still > 13.8 Gyr.

---

## Honest limitations

1. **The literal Yang+ 2024 prefactor underestimates N-body t_c by 1.82× for BM2.** This Loop 4's t_c values are 1.82× smaller than the N-body-calibrated ones. All still > 13.8 Gyr, so the conclusion holds.
2. **The halo parameters (M_200, c_200) for Tucana II, Hercules, Bootes I are uncertain.** Different literature values would shift r_s and ρ_s by factors of a few. The qualitative conclusion (t_c >> 13.8 Gyr) is robust to these uncertainties.
3. **The model is robust to Γ/ρ tuning — but this is a WEAKNESS, not a strength (Nemotron 120B review, paraphrasing the v40.5 look-elsewhere concern).** All 5 halos are consistent at every tested Γ/ρ ∈ [1, 20]. This means the model is "flexible enough" to accommodate observations at any Γ/ρ, but it does NOT discriminate between Γ/ρ values. The Phase 3 "FAIL" verdict (no first-principles UV sector fixes Γ/ρ) is unchanged by this Loop 4.
4. **The cluster side is not tested here.** A complete comparison with Gilman+ 2023 would also need σ/m at v ~ 1000 km/s for MW-mass and cluster halos.
5. **The 5 specific UFDs are a small sample.** Gilman+ 2023 constrains the population-level collapsed fraction, which would require integration over a larger halo sample. Loop 4's individual-halo test is a necessary but not sufficient condition.

---

## Files

- **This doc:** `docs/V19_2_F_LOOP4_GRAVOTHERMAL_TC.md`
- **JSON (preliminary, to be added):** `v0.3-prelim/data/results/v19_2_f_loop4_tc_breit_wigner.json` (TODO)
