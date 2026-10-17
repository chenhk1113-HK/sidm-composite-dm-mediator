# v40.4 — Segue 1 σ/m bound re-derived with full Γ/ρ sweep

**Date:** 2026-10-17
**Branch:** `wip/v19.2-F-init`
**Author:** Hermes (controller) + M3 (initial draft) + Nemotron 120B (review)
**Tag:** `v19.2-F-Phase3-CLOSED-r40.4` (pending)

---

## TL;DR

At the canonical α_D = 5.55×10⁻⁶ (project-internal dynesty fit, NOT from Cloud-9), **Segue 1 is IN BAND at Γ/ρ ∈ {6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0, 10.5, 11.0, 11.5}** (11 widths), consistent across all four v_eff methodologies. This **overlaps the Cloud-9 v40.2 IN BAND set {6, 7, 8, 9, 10}** at Γ/ρ ∈ {7, 8, 9, 10} (4 widths).

**Internal-consistency check:** at the canonical α_D, the same model parameter is consistent with both a dwarf galaxy (Segue 1, M_halo~10⁸ M☉) and a starless gas cloud (Cloud-9, M_halo~5×10⁹ M☉) at overlapping resonance widths. This is **not an independent validation** — both IN BAND sets derive from the same α_D — but it does verify the model is internally self-consistent at a 50× halo-mass range. If the model were wrong, the two halos would generically be inconsistent with each other at any single α_D.

**Caveat (per v40.3):** The verdict is fragile to α_D shifts of ±0.1 dex. At α_D = 4.41×10⁻⁶ (-0.1 dex), the Segue 1 IN BAND set shifts to lower widths; at α_D = 6.99×10⁻⁶ (+0.1 dex), it shifts higher. The overlap with Cloud-9's IN BAND set requires the α_D to be in a narrow window around 5.55×10⁻⁶.

---

## Method

Following the v40.1/v40.2 Cloud-9 re-baseline methodology (velocity-weighted σ_eff = ∫f(v)σ_m(v)dv over an MB distribution, with full Γ/ρ sweep), we re-derive the Segue 1 bound.

### Halo parameters (Segue 1 UFD)
- M_200 = 1.0×10⁸ M☉
- c_200 = 25
- V_max = 8.0 km/s
- σ_v (1D, line-of-sight) = **3.7 km/s** (Simon+ 2011, Kirby+ 2013)
- M_halo reference: Read+ 2019 (NOT the Cloud-9 paper)
- Observation: low central density, not gravothermally collapsed (t_c > 13.8 Gyr)

### σ/m formula
σ_m(v; α_D, m_ρ, Γ_ρ, m_χ) = σ_Born(v; α_D, m_ρ) × F²(v; m_ρ, Γ_ρ), where:
- σ_Born = numerical quadrature of Born-level t-channel diagram with dark-rho propagator
- F² = Breit-Wigner resonance factor (1.0 at low v, 1/(1+Γ²) at v ≪ v_res, peak at v_res)
- m_ρ = 0.05×10⁻³ GeV (Chu-Hambye-Tytgat 2018, M2 model)
- m_χ = 1.0 GeV
- Γ_ρ/m_ρ swept across [0.5, 20.0] in 0.5 steps (40 points)

### v_eff methodologies tested
1. **V_max (pointwise)**: σ_m at v_eff = V_max = 8.0 km/s — *current project methodology* (v19_2_e_b_per_halo_gravothermal.py)
2. **sqrt(2)·σ_v (pointwise)**: σ_m at v_eff = √2·σ_v = 5.23 km/s — *1D → 3D MB scale parameter*
3. **σ_v_los (pointwise)**: σ_m at v_eff = σ_v_los = 3.7 km/s — *1D velocity dispersion*
4. **velocity-weighted MB**: σ_eff = ∫f_MB(v; σ_v=3.7)·σ_m(v)dv over 50 log-spaced v-points in [0.1, 50] km/s — *v40.2 Cloud-9 methodology*

### IN BAND criterion
σ/m within factor 2 of canonical target: 87 < σ/m ≤ 348 cm²/g (i.e., 0.5 < ratio ≤ 2.0).

**Note on mass-independence (Nemotron 120B review):** This criterion uses the same factor-2 window for Segue 1 (M_halo~10⁸ M☉) and Cloud-9 (M_halo~5×10⁹ M☉). The canonical σ/m target of 174 cm²/g is derived from the Cloud-9 v40.2 analysis and the Lyman-α + SPARC dynesty fit, not from a Segue 1-specific calculation. A mass-dependent scaling (e.g., t_c ∝ 1/(ρ·σ/m)) would suggest the appropriate σ/m for a 50× smaller halo could be different, but the project uses a uniform target across halos. This is a **project convention**, not a derived Segue 1 constraint.

---

## Results

| Methodology | IN BAND set at Γ/ρ | # widths |
|---|---|---|
| V_max (pointwise) | {6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0, 10.5, 11.0, 11.5} | 12 |
| √2·σ_v (pointwise) | {6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0, 10.5, 11.0, 11.5, 12.0} | 12 |
| σ_v_los (pointwise) | {6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0, 10.5, 11.0, 11.5, 12.0, 12.5} | 13 |
| velocity-weighted MB | {6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0, 10.5, 11.0, 11.5, 12.0} | 13 |

**Common IN BAND set (all 4 methods agree): {6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0, 10.5, 11.0, 11.5}** (11 widths).

**Cloud-9 v40.2 IN BAND set:** {6, 7, 8, 9, 10} (5 widths).

**Overlap (Segue 1 ∩ Cloud-9): {7, 8, 9, 10}** (4 widths).

---

## Why the existing project analysis missed this

The existing project script `v19_2_e_b_per_halo_gravothermal.py` uses **pointwise σ_m(v_eff = V_max) WITHOUT a Γ/ρ sweep**, then computes gravothermal t_c from that single value. This is a single-point analysis. The v40.1/v40.2 Cloud-9 methodology, by contrast, sweeps Γ/ρ across [0.5, 20.0] and tests the IN BAND criterion at each.

**The missing piece is the Γ/ρ sweep.** When applied to Segue 1, the full sweep reveals the IN BAND window.

---

## Cross-validation: Segue 1 vs Cloud-9

| Quantity | Segue 1 (this work) | Cloud-9 (v40.2) |
|---|---|---|
| σ_v (1D, km/s) | 3.7 (Simon+ 2011) | 5.1 (Anand+ 2025) |
| M_halo (M☉) | 10⁸ | 5×10⁹ |
| IN BAND set at α_D=5.55e-6 | Γ/ρ ∈ {6.5..11.5} | Γ/ρ ∈ {6, 7, 8, 9, 10} |
| IN BAND overlap | — | {7, 8, 9, 10} |
| Halo-mass ratio | 1 | 50× |

**The same α_D fits both halos at overlapping Γ/ρ widths**, across a 50× halo-mass range. This is a non-trivial cross-check.

**Caveat (per v40.3 sensitivity analysis):** the verdict is fragile to ±0.1 dex shifts in α_D. At α_D = 4.41e-6 (-0.1 dex), the Segue 1 IN BAND set shifts to lower widths; at α_D = 6.99e-6 (+0.1 dex), it shifts higher. The cross-check requires the canonical α_D to be in a narrow window.

---

## Numerical checks (arithmetic verification by controller)

Computed independently (not using M3's script). Sample values at v_eff = V_max = 8.0 km/s:

| Γ/ρ | σ/m (cm²/g) | ratio | IN BAND? |
|---|---|---|---|
| 1.0 | 6,383 | 36.7 | NO (way over) |
| 5.0 | 460 | 2.6 | NO (over) |
| **8.0** | **220** | **1.26** | **YES** |
| **10.0** | **118** | **0.68** | **YES** |
| 15.0 | 53 | 0.30 | NO (under) |
| 20.0 | 30 | 0.17 | NO (way under) |

The IN BAND window at Segue 1 (V_max pointwise) is at Γ/ρ ∈ {6, 6.5, ..., 11.5}, peaking around Γ/ρ ≈ 8 (ratio 1.26, closest to canonical target).

---

## Implication for the existing Segue 1 t_c analysis

**Caveat (Nemotron 120B review):** The existing project script `v19_2_e_b_per_halo_gravothermal.py` and the v40.1/v40.2 IN BAND analysis use **different σ/m formulas**:

- **Gravothermal t_c** (existing): uses a Gaussian σ_m(v) = σ_0 × exp(-(v-v_0)²/(2σ_1²)) with σ_0=0.052 cm²/g, a_slope=1.93, σ_peak=174 cm²/g, v_target=29.4 km/s, σ_1=4.4 km/s. The t_c is computed from this Gaussian σ/m at v_eff = V_max = 8.0 km/s.
- **Resonance IN BAND** (this work + v40.1/v40.2): uses σ_m_resonance(v; α_D, m_ρ, Γ_ρ) with Breit-Wigner shape, evaluated across the full Γ/ρ ∈ [0.5, 20.0] sweep.

These are not directly comparable. The gravothermal t_c does NOT depend on Γ/ρ (the Gaussian σ/m has no Γ/ρ parameter), while the resonance IN BAND set is a function of Γ/ρ. So the t_c at IN BAND Γ/ρ widths from the resonance analysis does NOT directly translate to a gravothermal t_c prediction.

**Honest correction:** the original doc claim that "at IN BAND Γ/ρ widths the predicted t_c is consistent with Segue 1's observed un-collapsed state" is **not supported by the gravothermal t_c formula**. The gravothermal t_c analysis (in `v19_2_e_b_per_halo_gravothermal.py`) is a separate calculation that uses a different σ_m formula and does not depend on Γ/ρ.

**What the gravothermal t_c at the canonical Gaussian σ/m gives** (existing analysis, at v_eff = V_max = 8.0 km/s):
- σ_m_gaussian(8.0) ≈ 174 × exp(-(8.0-29.4)²/(2·4.4²)) ≈ 174 × exp(-15.6) ≈ 174 × 1.65e-7 ≈ 2.9×10⁻⁵ cm²/g

This is essentially zero — the Gaussian is far off-resonance at v=8 km/s. The gravothermal t_c at this σ/m would be effectively infinite, consistent with Segue 1 not having collapsed.

**What the resonance σ/m at the same v gives** (this work):
- σ_m_resonance(8.0; α_D=5.55e-6, m_ρ=0.05e-3, Γ/ρ=10) ≈ 118 cm²/g (IN BAND)
- σ_m_resonance(8.0; α_D=5.55e-6, m_ρ=0.05e-3, Γ/ρ=1) ≈ 6,400 cm²/g (OUT)

So the resonance σ/m at v=8 km/s is **many orders of magnitude larger** than the Gaussian σ/m at the same v. The two formulas give very different physical predictions. The IN BAND analysis is in the resonance framework; the gravothermal t_c is in the Gaussian framework. They answer different questions.

**Implication:** a proper gravothermal t_c analysis using the resonance σ/m formula (with full Γ/ρ sweep) would need to be done to make a coherent statement about Segue 1's collapse status. This is **out of scope for Loop 1** but is a natural follow-up loop.

---

## Files

- **Script (M3 draft, partially used):** `v0.3-prelim/code/v19_2_f_loop1_segue1_veff_check.py` (18466 chars)
- **JSON (controller-computed, the actual deliverable):** `v0.3-prelim/data/results/v19_2_f_loop1_segue1_veff_check.json` (2.8 KB)
- **This doc:** `docs/V19_2_F_LOOP1_SEGUE1_BOUND.md`

---

## Honest limitations

1. **M3's script was incomplete.** It only checked Γ/ρ = 1.0 (single point). The controller re-ran the analysis with the full Γ/ρ sweep [0.5, 20.0] in 0.5 steps. M3's qualitative conclusion (Segue 1 is OUT at Γ/ρ = 1) was correct but the broader finding (Segue 1 is IN BAND at the full sweep) was missed.
2. **v40.3 caveat applies:** the IN BAND set is fragile to α_D shifts. The cross-check with Cloud-9 requires α_D ≈ 5.55e-6.
3. **The Γ/ρ sweep convention is from v40.1.** This is a project convention, not a fundamental physical parameter. Different conventions (e.g., fixing Γ/ρ = 1.0 as a "natural width" benchmark) would give different verdicts.
4. **No new physics claim.** The finding is that the canonical α_D is consistent with both halos at overlapping Γ/ρ widths. This is a consistency check, not a constraint on α_D from Segue 1.
5. **The Segue 1 t_c analysis in `v19_2_e_b_per_halo_gravothermal.py` should be re-done** with the full Γ/ρ sweep to give a proper gravothermal phase diagram.

---

## Status

- **Controller verified:** arithmetic check (3rd-party computation matches expected).
- **Nemotron 120B review:** pending (this doc sent for review).
- **M3 revision:** pending Nemotron feedback.
- **Tag:** `v19.2-F-Phase3-CLOSED-r40.4` (to be applied on commit).
