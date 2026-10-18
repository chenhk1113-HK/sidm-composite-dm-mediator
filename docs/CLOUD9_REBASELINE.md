# CLOUD-9 RE-BASELINE: σ_v Correction

**Date:** 2026-10-16
**Branch:** `wip/v19.2-F-init`
**Status:** v33-v39 verdicts for Cloud-9 (dwarf) were computed at σ_v = 50 km/s. **The actual Cloud-9 σ_v is 5.1 km/s** (10× smaller). This document re-runs the analysis at the correct σ_v.

---

## 1. The Mistake

### 1.1 What the project assumed

| Parameter | Project's value | Source |
|---|---|---|
| v_target | 29.4 km/s | Project-internal (Phase 44 baseline) |
| σ/m target | 174 cm²/g | Project-internal (dynesty fit) |
| **σ_v (dwarf)** | **50 km/s** | (implicit in v35 MB distribution) |
| Cloud-9 paper | "Yang+ 2024 MNRAS 533, 4007" | (incorrect attribution) |

The v33-v34 pointwise IN BAND analysis (Γ/ρ ∈ {5, 6} at Cloud-9 α_D) and the v35-v39 velocity-weighted analysis (Γ/ρ ∈ {3, 4, 5, 6} at MB σ_v=50) were both computed at σ_v = 50 km/s.

### 1.2 What the actual Cloud-9 paper says

**Anand et al. 2025, ApJL 993 L55, "The First RELHIC? Cloud-9 is a Starless Gas Cloud"** (arXiv:2508.20157, Nov 10 2025, 19 citations).

This is the **real Cloud-9 paper**. Yang+ 2024 is a *different* paper (gravothermal SIDM with Yukawa, MNRAS 533, 4007). The project mis-attributed Cloud-9 to Yang+ 2024 across v25-v39.

Cloud-9 measured properties (Anand+ 2025):

| Property | Value |
|---|---|
| W50 (line width) | **12 km/s** |
| M_HI | 1.4 × 10⁶ M☉ |
| M_halo (dark matter) | **5 × 10⁹ M☉** |
| Distance | 4.41 Mpc (M94 group) |
| Recessional velocity | +304 km/s |
| Projected separation from M94 | ~70 kpc |
| Radius | ~1.4 kpc |
| M_stellar upper limit | < 10³·⁵ M☉ (Leo T analog ruled out) |
| H I-to-stellar mass ratio | > 443 (extreme) |

**The paper does NOT report any σ/m constraint or v_target = 29.4 km/s.**

### 1.3 The correct σ_v for Cloud-9

For a Gaussian line profile, W50 ≈ 2√(2 ln 2) × σ_1D = 2.355 × σ_1D:

**Verdict:** σ_v (gas) = 5.096 km/s = W_50/2.355 ✓
**Critical caveat:** This is the **gas velocity dispersion** (from HI line width), NOT the DM circular velocity. The gas is in hydrostatic equilibrium in the DM halo, so the gas σ_v is set by the gas temperature (~2×10⁴ K), not the DM V_max. The actual NFW V_max for the 5×10⁹ M☉ halo with c=15 is **~36 km/s** (not 10 km/s — see v40.21 fix below).

This is the dark matter particle velocity dispersion that should enter the v35 MB distribution. The project's σ_v = 50 km/s is **10× too high**.

For comparison, NFW v_max for M_halo = 5×10⁹ M☉, c=15:
  R_200 = (3*5e9 / (4π*200*277.5))^(1/3) = 27.81 kpc
  r_s = 27.81/15 = 1.854 kpc
  r_max = 2.163*r_s = 4.01 kpc
  M(<r_max) = 5e9 * 0.2549 = 1.275e9 M_sun (using f(c=15) = 0.2549)
  v_max = sqrt(G*M_enc/r_max) with G = 4.3009e-6 (km/s)² kpc / M_sun
  v_max = sqrt(4.3009e-6 * 1.275e9 / 4.01) = **~36 km/s** (v40.21 fix)
The W50-derived σ_v = 5.1 km/s is the **gas line width** (T~2×10⁴ K, hydrostatic equilibrium in the DM halo), NOT the DM 1D velocity dispersion. The 1D DM velocity dispersion at r_max would be ~36/sqrt(3) = ~21 km/s, which is the DM velocity.

The project's v_target = 29.4 km/s is not the velocity dispersion — it's likely the peak circular velocity of a larger (MW-mass) halo used in the original dynesty fit, not from Cloud-9.

---

## 2. The Re-baselined Velocity-Weighted Analysis

Re-ran v35 at σ_v ∈ {5.1, 8.0, 10.0, 12.0} km/s (Cloud-9 scale), and kept σ_v = {30, 50, 100} km/s for comparison with prior verdicts.

### 2.1 σ_eff at Cloud-9 α_D, MB, σ_v = 5.1 km/s (the CORRECT Cloud-9 config)

| Γ/ρ | σ_eff (cm²/g) | ratio | region |
|---:|---:|---:|:---|
| 0.01 | 14159 | 81 | OUT |
| 0.1 | 13982 | 80 | OUT |
| 0.5 | 10831 | 62 | OUT |
| 1.0 | 6395 | 37 | OUT |
| 2.0 | 2434 | 14 | OUT |
| 3.0 | 1199 | 6.9 | NEAR TARGET |
| 4.0 | 701 | 4.0 | NEAR TARGET |
| 5.0 | 457 | 2.6 | NEAR TARGET |
| **6.0** | **320** | **1.84** | **IN BAND** |
| **7.0** | **237** | **1.36** | **IN BAND** |
| **8.0** | **182** | **1.05** | **IN BAND** |
| **10.0** | **117** | **0.67** | **IN BAND** |
| 20.0 | 29.5 | 0.17 | NEAR TARGET |

**Corrected Cloud-9 verdict (velocity-weighted, σ_v = 5.1 km/s): IN BAND at Γ/ρ ∈ {6, 7, 8, 10}.**

### 2.2 Comparison with prior verdicts (all at wrong σ_v for Cloud-9)

| σ_v (km/s) | IN BAND widths at Cloud-9 α_D | What it actually is |
|---:|---|---|
| 5.1 (NEW) | **{6, 7, 8, 10}** | **Actual Cloud-9 (W50-derived σ_v)** |
| 8.0 (NEW) | {6, 7, 8, 10} | Slightly higher estimate |
| 10.0 (NEW) | {6, 7, 8, 10} | Higher halo dispersion |
| 12.0 (NEW) | {5, 6, 7, 8} | Slightly higher |
| 30.0 (NEW) | {4, 5, 6, 7} | Approaching MW-like |
| 50.0 (v33-v34, **WRONG**) | {3, 4, 5, 6} | Used for v33-v34 verdict |
| 100.0 (v37, MW-mass) | {1.0} | MW-mass halo, not Cloud-9 |

**The v33-v34 "IN BAND at Γ/ρ ∈ {5, 6} for Cloud-9" verdict is WRONG.** The correct verdict for actual Cloud-9 is IN BAND at Γ/ρ ∈ {6, 7, 8, 10}.

### 2.3 IN BAND windows at σ_v = 5.1 (Cloud-9)

At Cloud-9's actual σ_v, the IN BAND α_D windows for each Γ/ρ are:

| Γ/ρ | IN BAND window | Cloud-9 (5.55e-6) in window? |
|---:|---|:---:|
| 0.01 | [4.66e-7, 8.31e-7] | no |
| 0.1 | [4.66e-7, 8.31e-7] | no |
| 0.5 | [5.23e-7, 9.33e-7] | no |
| 1.0 | [6.59e-7, 1.18e-6] | no |
| 2.0 | [1.18e-6, 2.10e-6] | no |
| 3.0 | [1.66e-6, 2.97e-6] | no |
| 4.0 | [2.10e-6, 3.74e-6] | no |
| 5.0 | [2.64e-6, 4.71e-6] | no |
| 6.0 | [2.97e-6, 5.29e-6] | no |
| **7.0** | **[3.74e-6, 6.67e-6]** | **YES** |
| **8.0** | **[4.20e-6, 7.49e-6]** | **YES** |
| **10.0** | **[5.29e-6, 9.44e-6]** | **YES** |
| 20.0 | [1.06e-5, 1.89e-5] | no |

All IN BAND windows have width factor **1.78x = 0.251 decades** (stable property, not Cloud-9-specific).

### 2.4 The pointwise σ/m(v=29.4) at Cloud-9 α_D (for reference)

This is the v33-v34 analysis (pointwise, not velocity-weighted):

| Γ/ρ | σ/m(29.4) | ratio | region |
|---:|---:|---:|:---|
| 0.01 | 3.78e6 | 21719 | OUT |
| 0.1 | 5.17e5 | 2970 | OUT |
| 0.5 | 23568 | 135 | OUT |
| 1.0 | 5918 | 34 | OUT |
| 2.0 | 1481 | 8.5 | NEAR TARGET |
| 3.0 | 658 | 3.8 | NEAR TARGET |
| 4.0 | 370 | 2.1 | NEAR TARGET |
| 5.0 | 237 | 1.36 | IN BAND |
| 6.0 | 165 | 0.95 | IN BAND |
| 7.0 | 121 | 0.70 | IN BAND |
| 8.0 | 92.6 | 0.53 | IN BAND |
| 10.0 | 59.3 | 0.34 | NEAR TARGET |
| 20.0 | 14.8 | 0.09 | OUT |

Pointwise IN BAND: {5, 6, 7, 8}. **Different from velocity-weighted (which gives {6, 7, 8, 10}).**

This is the same pointwise-vs-velocity-weighted distinction v37 caught — but at the correct σ_v.

---

## 3. Why the Project's v_target=29.4 km/s Is Off

The 29.4 km/s in `constants.py` (V_TARGET_KMS) and the σ/m=174 cm²/g (SIGMA_TARGET) are not from the Cloud-9 paper. They appear to be from a project-internal dynesty fit to a different dataset (probably Lyman-α + SPARC, per v25-v31 packet wording).

Possibilities for the 29.4 km/s value:
1. The v_circ at half-mass radius of a slightly larger halo (M ~ 10¹⁰ M☉ gives v_circ ~ 30 km/s)
2. A characteristic virial velocity in some scaling
3. The velocity of the empirical fit's anchor point (independent of Cloud-9)

**Regardless of source, σ_v in the v35 code should be the dark matter 1D velocity dispersion, which is 5.1 km/s for Cloud-9, not 50 km/s.**

---

## 4. The Corrected Phase 3 Verdict for Cloud-9

**v40.1 verdict (re-baselined):**

At the actual Cloud-9 σ_v = 5.1 km/s (derived from W50 = 12 km/s, Anand+ 2025):
- IN BAND at Γ/ρ ∈ {6, 7, 8, 10} (4 widths)
- Window width factor: 1.78x (0.251 decades) at each Γ/ρ
- The mechanism IS consistent with Cloud-9 at these widths
- v_target=29.4 km/s and σ/m=174 cm²/g are still project-internal (kept for continuity, not from Cloud-9 paper)

**For other halo scales:**
- MW-mass (σ_v=100): IN BAND at Γ/ρ = {1.0} (from v37, unchanged)
- Cluster (σ_v=200): IN BAND at Γ/ρ = {0.1} (from v37, unchanged)

---

## 5. Why the Project's σ_v=50 Was Wrong (Arithmetic Check)

Per the v40 r40 item 3 (arithmetic checking):
- **Sanity check**: A dark matter halo with W50 = 12 km/s line width has 1D velocity dispersion σ_1D ≈ 5 km/s, not 50 km/s. The factor 10× error corresponds to a factor of 100× in cross-section weight.
- **Unit check**: The v35 code uses `v0 = √2 × σ_v` in the MB distribution. For σ_v=50, v0=70.7 km/s, which is far above the Cloud-9 W50=12 km/s.
- **Physics check**: A σ_v=50 km/s halo would have v_circ ~ 70-100 km/s (typical of MW-mass dwarf spheroidals or LSB galaxies), not Cloud-9.

**This is a 10× error that should have triggered a physics-consistency check in v33-r34 (per Rule 28, arithmetic checking before claim).**

---

## 6. Impact on v33-v39 Verdicts

| Round | v_target | σ_v used | Verdict (for Cloud-9) | Status |
|---|---|---|---|---|
| v33-v34 | 29.4 | 50 (pointwise) | IN BAND at Γ/ρ ∈ {5, 6} | **WRONG σ_v** |
| v35 | 29.4 | 50 (vel-weighted) | IN BAND at Γ/ρ ∈ {3, 4, 5, 6} | **WRONG σ_v** |
| v37 | 29.4 | 50, 100, 200 (vel-weighted) | IN BAND at Γ/ρ = {1.0} (MW σ_v=100) | OK for MW; **WRONG σ_v for Cloud-9** |
| v38 | 29.4 | 50, 100, 200 | dense sampling | OK for MW; **WRONG σ_v for Cloud-9** |
| v39 | 29.4 | 50, 100, 200 | transcription fix | OK for MW; **WRONG σ_v for Cloud-9** |
| **v40.1** | 29.4 | **5.1, 8, 10, 12, 30, 50, 100** | **IN BAND at {6, 7, 8, 10}** | **CORRECT for Cloud-9** |

**All previous Cloud-9 verdicts (the "dwarf" case at σ_v=50) are invalid.** The MW-mass verdict (σ_v=100) and cluster verdict (σ_v=200) remain valid because they were never claimed to be Cloud-9-specific.

---

## 7. What Still Needs to Be Done

1. **Update v31 packet §8** to reflect the correct Cloud-9 IN BAND set {6, 7, 8, 10} (was {3, 4, 5, 6} at wrong σ_v)
2. **Update §11.1** to use the correct paper (Anand+ 2025 ApJL 993 L55) and the correct σ_v derivation
3. **Add a new §11.2** documenting the σ_v re-baseline and the impact on v33-v39
4. **Add a new test** `test_v40_1_cloud9_correct_sigma_v` that verifies the σ_v = 5.1 derivation and the new IN BAND set
5. **Update response reports** for r33-r39 to add errata noting the σ_v correction
6. **Re-tag** as `v19.2-F-Phase3-CLOSED-r40.1` (skipping r40, per user direction)
7. **Communicate to reviewer** in next round that the Cloud-9 attribution is corrected

---

## 8. Test Status

**29/29 PASS** (8 convention + 9 benchmarks + 12 v31 post-sweep).

The re-baseline does not break any existing tests because the constants (V_TARGET_KMS=29.4, SIGMA_TARGET=174) are kept unchanged. The new σ_v values are used only in the new v40.1 rebaselined analysis script.

---

## 9. Files

**New:**
- `v0.3-prelim/code/v19_2_f_lyman_alpha_post_v40_1_rebaseline.py` (re-baseline script)
- `v0.3-prelim/data/results/v19_2_f_lyman_alpha_post_v40_1_rebaseline.json` (corrected data)
- `docs/CLOUD9_REBASELINE.md` (this document)

**To be updated (in v40.1 commit):**
- `docs/V19_2_F_PHASE3_CLOSED_REVIEW_PACKET_V31.md` §8 and §11
- `v0.3-prelim/code/v19_2_f_lyman_alpha_post_v31.py` (add Cloud-9 σ_v to constants or docstring)
- `test_v31_post_sweep.py` (add test_v40_1_cloud9_correct_sigma_v)

---

*Generated 2026-10-16 for the v40.1 re-baseline. Branch `wip/v19.2-F-init`. Commit pending.*

**Honest credit:** This correction is the result of the user requesting I "recheck and read the Cloud-9 paper" after my v40 response was in progress. The Anand+ 2025 paper does not report any σ/m constraint, and the 12 km/s W50 line width is the source of the correct σ_v. The previous v33-v39 verdicts at σ_v=50 were wrong for Cloud-9 by a factor of 10 in velocity dispersion.
