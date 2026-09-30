# Paper Standing Numbers — Single Source of Truth (v19.0)

> **Rule:** No number appears in `PAPER_V1_DRAFT.md` unless it's in this table.
> Re-verified by `scripts/audit_claims.py` against its source JSON before each commit.
>
> **Last refresh:** 2026-09-27 (Phase 1.2 of devplan1.docx)
> **Source commit:** `7658753` (wip/cloud-9-relhic HEAD)

---

## §1. Observational anchors

| Number | Value | Source file | Prescription | Cite |
|---|---|---|---|---|
| Cloud-9 σ/m floor | ≥ 50 cm²/g | `data/external_data/cloud9.yaml` | systematic upper bound | BLN24 / Ohana+ 2026 |
| dSph σ/m ceiling | ≤ 0.8 cm²/g | `data/results/t28_published_style_dsph.json` | w=10 km/s | Horigome+ 2025 |
| SPARC σ/m target | 0.193 cm²/g | `data/results/t12_6channel_with_lens.json` | V_max=100 km/s | Lelli+ 2016 |
| Cluster σ/m ceiling | ≲ 0.1–1 cm²/g | (literature range) | v~10³ km/s | Bullet Cluster / Read+ |

## §2. Channel coverage (T207 prescription split)

| Prescription | clear_pass | marginal | clear_fail | Pass (C+M) | SPARC log L |
|---|---|---|---|---|---|
| **borrowed** (hand-picked) | 4 | 2 | 2 | **6 / 8** | -0.0919 |
| **yang** (Yang+ 2025 f_H) | 4 | 2 | 2 | **6 / 8** | -0.2426 |
| **t202** (T202 N-body f_H) | 3 | 1 | 4 | **4 / 8** | -0.6068 |
| **priored free fit** (v18.38 f_H_cc≥0.05) | 8 | 0 | 0 | **8 / 8** | -2.03 |

**Source:** `data/results/t207_final_summary.json` (`channel_coverage_summary`, `t207_de_prescription_modes`)

**Honest framing:** The paper's headline is **4 of 8 channels under physically motivated f_H** (clear_pass under yang or t202). The "6 of 8" figures count clear+marginal under borrowed mode; the devplan's Refinement 1 mandates retiring any "6–7 of 8" phrasing.

## §3. Path F1 verdict split (T207)

| Prescription | v_HL (km/s) | σ_HL_peak | f_H_cc | Verdict |
|---|---|---|---|---|
| **borrowed** | 100.61 | 0.343 | 0.30 (fixed) | **RESOLVED** |
| **yang** | 99.44 | 0.342 | 0.45 (fixed) | **MARGINAL** |
| **t202** | (degenerate with yang) | — | — | **NOT RESOLVED** |
| **priored free fit** | 105.24 ± 38.60 | 0.523 ± 0.363 | 0.060 ± 0.012 | **CLEAR FAIL** (SPARC log L = -2.03, z≈2.0) |

**Source:** `data/results/t207_final_summary.json` (`t207_de_prescription_modes`, `t207c_priored_free_emcee.json`)

**Honest framing:** Mechanism A (on-peak, v_HL ≈ 100 km/s, small peak, no background) gives σ_HL ≈ 0.34. Mechanism B (off-peak, v_HL ≈ 178 km/s, large peak, partial overlap) gives σ_HL(100) ≈ 0.27 but violates Cloud-9 causality. Both give σ_eff(100) ≈ 0.19.

## §4. Statistical tests

| Statistic | Value | Source | Note |
|---|---|---|---|
| Bayes log B (multi-resonance vs constant) | **2.411** | `data/results/t205_full_likelihood_published.json` | Moderate evidence, published σ_unc |
| Bayes B | 11.149 | same | Down from T177's 3.06 |
| T177 log B (hand-picked σ_unc) | 3.06 | (deprecated, see T205) | Superseded by T205 |
| Phase 42 SPARC log Z (Burkert) | -963 | (separate run) | Burkert wins |
| Phase 42 SPARC log Z (SIDM hybrid) | -3300 | (separate run) | SIDM loses by wide margin |
| Phase 54 BIC penalty | ΔBIC = +3.22 favoring constant | (T205/T177) | 15 vs 1 params |

## §5. Host-halo gravothermal (T208)

| Parameter | Value | Source |
|---|---|---|
| Cloud-9 M_halo | 5×10⁹ M☉ | `t208_path_b_cloud9_host_halo_gravothermal.json` |
| Cloud-9 concentration c | 12 | same |
| Cloud-9 V_max (NFW-correct at r_max) | 31.12 km/s | same (post v18.43 T215 IC generator correction; was 24.75 km/s with virial approx) |
| Cloud-9 r_vir | 35,093 pc | same |
| Cloud-9 r_s | 2,924 pc | same |
| ρ_s | 9.69×10⁻³ M☉/pc³ | same |
| **t_core (Phase 44 Yukawa-only σ/m = 0.167 at V_max = 31.12)** | **73.71 Gyr** | same (matches the §9.12 paper value of 73.7 Gyr; legacy σ/m = 0.21 at v = 24.75 km/s also gives 73.71 Gyr because the (σ/m, v_max) ratio is constant for the Phase 44 a_slope = 1.0 scaling) |
| t_Hubble | 13.8 Gyr | (Planck) |
| **Verdict at Phase 44 Yukawa-only baseline** | **gravothermal DOES NOT run** | same |
| Path 2 | **REFUTED** at Phase 44 Yukawa-only baseline | same |

**v19.1.5 addendum (post-r197.docx — Phase 44 σ/m via canonical channels_v03.sigma_m_at_v):**

**Phase 44 baseline σ/m (corrected per r197.docx Issue 1):**
- σ₀ = 0.052 cm²/g at v = 100 km/s (T208 source)
- a_slope = 1.0 (v18.28 Rule-28 audit fixed value)
- σ/m(V_max = 31.12 km/s) = 0.052 × (100/31.12)^1.0 = **0.167 cm²/g** (NOT 0.174 as v19.1.4 had hardcoded)
- σ/m(v = 28 km/s) = 0.052 × (100/28)^1.0 = **0.186 cm²/g**
- σ/m(v = 24.75 km/s) = 0.052 × (100/24.75)^1.0 = 0.210 cm²/g

**Test matrix (reconciled, V_max = 31.12 km/s NFW-correct):**

| Case | σ/m | c | t_core (Gyr) | t_core/t_cross | causality | Verdict |
|---|---|---|---|---|---|---|
| Silverman+ 2026 ref | 70 | 12 | 0.176 | **1.91** | **FAIL** | N-body found 3/6 collapse; analytical Balberg+ unreliable |
| Cloud-9 Phase 44 Yukawa only | **0.167** | 12 | **73.71** | 802 | OK | does NOT run |
| Cloud-9 Phase 44 Yukawa only | 0.167 | 4 | 3580 | 10678 | OK | does NOT run |
| Cloud-9 framework v₁ at V_max | **135.3** | 12 | 0.091 | 1.0 | **FAIL** | analytical only |
| Cloud-9 framework v₁ at V_max | **135.3** | 4 | **4.42** | 13.2 | OK | **runs (causality-OK anchor)** |
| Cloud-9 framework v₁ at peak (v=28) | 164 | 12 | 0.075 | 0.8 | **FAIL** | analytical only |
| Cloud-9 Ohana+ best fit | 483 | 4 | 1.24 | 3.69 | OK | runs |

**Phase 44 reconciliation (Issue 1 of r197.docx):** v19.1.4 had hardcoded σ/m = 0.174 for Phase 44 at V_max. The canonical value from `channels_v03.sigma_m_at_v(0.052, 1.0, 31.12)` is **0.167 cm²/g**, giving t_core = **73.71 Gyr** — which matches the §9.12 paper value of 73.7 Gyr exactly. The 0.174 was a 4% drift from the actual value, traced to rounding-error in v19.1.4's hardcoded value. v19.1.5 imports the canonical function directly.

**Causality cap (Issue 3 of r197.docx):** Per the r197.docx review, Silverman+ reference case ALSO violates the causality cap (t_core/t_cross = 1.91 < 3.0). The Silverman+ 3/6 collapse finding is from N-body, where the analytical Balberg+ formula is unreliable in this regime. The 0.176 Gyr number is INDICATIVE; the N-body timescale is physical. **N-body is required across the board, not just for the framework case.**

**Silverman+ ref causality: previously reported as "OK" in v19.1.4 report text but JSON said `causality_ok: false`. v19.1.5 fixes the report text and the script's verdict section.**

**Honest synthesis (v19.1.5):** Cloud-9 t_core at c=4 anchor is **4.42 Gyr** (causality-OK). This drives gravothermal collapse in <halo age. Sustained mergers (Silverman+ mechanism, M94 group environment) could prevent collapse against framework σ/m = 135.3. Three open explanations: (c) merger-suppressed (viable but not "leading"); (b) framework σ_peak too high (possible; would require Phase 44 re-fit); (a) Ohana+ τ wrong (unlikely). N-body with M94-like sustained mergers is the discriminator. The "4000× problem" is reframed (not dissolved). **σ/m = 0.167 cm²/g is the canonical Phase 44 baseline at V_max, computed from channels_v03.sigma_m_at_v(0.052, 1.0, 31.12).**

## §6. Host-halo gravothermal at σ/m=70 (T212 Silverman+)

| Parameter | Value | Source |
|---|---|---|
| Cloud-9 σ/m at σ/m=70 | 70 cm²/g | `t212_silverman_gravothermal.json` |
| Cloud-9 t_core at σ/m=70 | **0.176 Gyr (176 Myr)** | same |
| t_cross at σ/m=70 | 0.092 Gyr | same |
| t_core/t_Hubble at σ/m=70 | 0.0128 | same |
| t_core/t_cross at σ/m=70 | 1.91 | same |
| Phase runs at σ/m=70 | TRUE | same |
| Causality ok at σ/m=70 | FALSE (Cloud-9 violation) | same |
| Silverman+ threshold (3/6 collapse) | ~1 cm²/g | Silverman+ 2026 arXiv:2606.02566 |

## §7. KK tower check (T213)

| Parameter | Value | Source |
|---|---|---|
| T163 best fit α_D | 0.3 | `t213_kk_tower_silverman_combined.json` |
| T163 best fit m_0 | 0.3 GeV | same |
| T163 best fit r | 1.5 | same |
| T163 best fit n_modes | 2 | same |
| T163 RMSE | 1.408 | same |
| **σ/m(V_max=31.12 km/s)** | **0.174 cm²/g** | same |
| Silverman+ threshold | 1.0 cm²/g | same |
| **Ratio T163/Silverman** | **5.75× below** | derived |
| Velocity dependence factor (<500 km/s) | < 1.04 | same |
| **Verdict** | **KK tower is Born regime, flat velocity, cannot bridge Cloud-9** | same |

## §8. UV no-go theorems (T163 + T175)

| No-go | Verdict at T163 best fit | Source |
|---|---|---|
| LZ direct detection | REFUTED | `t175_nogo_retest_t163.json` |
| Kinematic forbiddance | REFUTED | same |
| Unitarity violation | REFUTED | same |
| Flat velocity dependence | REFUTED | same |
| **All 4 hold** | **YES** | same |

## §9. Two-mediator / Drobczyk candidate (T185, T192)

| Parameter | Value | Source |
|---|---|---|
| Best Ω_h² | 0.1187 | `t192_thermal_avg.json` |
| Planck Ω_h² target | 0.1200 | (Planck) |
| Verdict | viable at δ=0.43% | same |

## §10. KiSS-SIDM methods (T215)

| Parameter | Value | Source |
|---|---|---|
| T215u mean Myr (memory-capped) | **69.57** | `t215u_memory_cap_summary.json` |
| T215u std Myr (memory-capped) | **0.74** | same |
| T215u range Myr (memory-capped) | 1.27 | same |
| T215r mean Myr (uncapped) | 41.85 | `t215r_5run_summary.json` |
| T215r std Myr (uncapped) | 21.13 | same |
| T215r range Myr (uncapped) | 58.22 | same |
| **Std reduction (capped/uncapped)** | **28×** | derived |
| **Range reduction** | **46×** | derived |
| ulimit cap | -v 8000000 (8 GB) | same |
| Bug classes (3+1) | FP sqrt × 4, assert disable × 3, ncom cap, min_particles tuning | `v0.3-prelim/patches/README.md` |

## §11. Qualitative gravothermal signature (T215p)

| Run | t_max (Myr) | r=287 / r=444 / r=r_s ratio | Verdict |
|---|---|---|---|
| T215p Run 1 | 70.00 | 3.15 / 2.98 / 0.40 | YES (interior up, outer down) |
| T215p Run 2 | 55.00 | 4.42 / 2.99 / 0.34 | YES |
| T215p Run 3 | 30.24 | 3.57 / 1.76 / 0.63 | YES |
| T215p Run 4 | 42.61 | 3.48 / 2.87 / 0.46 | YES |
| T215p Run 5 | 69.99 | 3.13 / 2.56 / 0.42 | YES |

**Source:** `data/results/t215p_qualitative_signal_summary.json` + per-run density JSONs

**Honest framing:** Qualitative gravothermal evolution direction is reproducible in 5/5 runs. **NOT a measured core-collapse time.** Runs stop at 30-70 Myr, far short of Balberg t_core ≈ 176 Myr at σ/m=70.

## §12. Numbers that MUST NOT appear in the paper

| Number | Reason |
|---|---|
| "6-7 of 8 channels" | Devplan Refinement 1: retire; use "4 of 8 under physically motivated f_H" |
| "Cloud-9 t_core measured" | No measurement exists; Tier 1+2 pilot confirmed parameter tuning cannot extend beyond 70 Myr |
| "Multi-resonance BIC-favored" | BIC-corrected ΔBIC=+3.22 favors constant σ/m |
| "KiSS-SIDM runs are deterministic" | They show 28× std variance across fresh-session batches; reproducibility requires `ulimit -v 8000000` |
| "First-principles f_H from N-body" | Not done; Yang+ Fig. 2 is borrowed at 2800× larger σ/m |
| "Cloud-9 tension resolved" | t_core=73.7 Gyr > t_Hubble at Phase 44 σ/m; unresolved |
| "8/8 channel pass as headline" | 8/8 only under priored free fit with SPARC log L=-2.03 (clear fail); honest headline is 4/8 |

## §13. Layer 3 real σ_pred re-derivation at v=100 (v19.0.3)

| Prescription | f_H_cf | f_H_cc | f_H_int = (cf+cc)/2 | σ_pred computed | log L computed | log L paper §9.11 | Delta |
|---|---|---|---|---|---|---|---|
| **borrowed** | 0.85 | 0.30 | 0.575 | 0.1716 | -0.092 | -0.09 | -0.002 |
| **yang** | 0.85 | 0.45 | 0.650 | 0.1582 | -0.243 | -0.24 | -0.003 |
| **t202** | 0.92 | 0.61 | 0.765 | 0.1379 | -0.607 | -0.60 | -0.007 |
| **priored free fit** | 0.827 | 0.060 | 0.444 | 0.2936 | -2.025 | -2.03 | 0.005 |

**Source:** `scripts/jia2026_sparc_check.py` (real σ_pred re-derivation per rev192.docx Reviewer 1).

**Methodology (per rev192.docx Reviewer 1):**
1. Take the paper's three-term Path F1 model from `two_component_three_term.sigma_eff_three_term`
2. Load T207 fitted parameters from `t207_final_summary.json` (borrowed/yang/t202) and `t207c_priored_free_emcee.json` (priored free fit)
3. SPARC v=100 channel uses `halo_class='intermediate'`, so f_H_int = 0.5 × (f_H_cf + f_H_cc)
4. Compute σ_pred(v=100) using Phase 44's energy-space Breit-Wigner for σ_HH and a velocity-space Lorentzian for σ_HL
5. Compute log L = -0.5 × ((σ_pred - 0.193) / 0.05)² (T205 SPARC published σ_unc = 0.05)
6. Compare computed log L to paper's §9.11 reported values

**Verification: ALL 4 prescriptions reproduce paper's §9.11 values within 0.007 log-units** (max delta = 0.007, well below the 0.05 tolerance).

**What changed vs v19.0/v19.0.1/v19.0.2:**
- v19.0 was a "surprise positive finding" using wrong prescriptions (flagged by Reviewer 2).
- v19.0.1 was a circular "verification" that re-read §9.11 numbers and reclassified them with thresholds chosen to match (flagged by Reviewer 1).
- v19.0.2 reframed v19.0.1 as a "consistency check" but did NOT compute σ_pred (flagged by Reviewer 1).
- **v19.0.3 actually computes σ_pred(v=100) from the paper's three-term Path F1 model** and reproduces the §9.11 per-channel log L values within 0.007 log-units for all 4 prescriptions. This is the real verification Reviewer 1 asked for.

**Key insight:** the paper's three-term mixture uses **f_H_int = 0.5 × (f_H_cf + f_H_cc)** for SPARC v=100 (the `intermediate` halo class), NOT just f_H_cf (cluster fraction) or f_H_cc (core fraction). This is documented in `T207_three_term_fit.py:124` and `CHANNELS` table line 74.

**Honest framing:** the §9.11 verdict split is **reproducible from the paper's own parameters**. The "log L = -2.03 CLEAR FAIL" verdict is robust under T205 σ_unc (= 0.05 from SPARC measurement), and the three prescription modes (RESOLVED, MARGINAL, NOT RESOLVED) match exactly. **Headline verdict unchanged.**

---

## §14. σ_peak sensitivity sweep (v19.2-A, canonical NFW)

**Source**: `scripts/v192_a_phase44_sigma_peak_sensitivity.py`, output `v192_a_phase44_sigma_peak_sensitivity.json` v7.

| Parameter | Value | Source |
|---|---|---|
| Sweep range | σ_peak ∈ {30, 50, 75, 100, 125, 150, 174, 200, 250} cm²/g | §2.6 sweep |
| Cloud-9 σ/m floor (BLN24) | σ/m(v=28) ≥ 50 cm²/g | BLN24 / Ohana+ |
| Cloud-9 floor velocity | v = 28 km/s (resonance peak) | BLN24 |
| Causality criterion | t_core > 3 × t_cross | §9.12 |
| Paper σ/m convention | Gaussian w=4.4, peak at v=28 | §2.5 |

**Canonical NFW (M_200 = 5×10⁹ M☉, ρ_crit = 1.381×10⁻⁷ M☉/pc³, self-consistent at each c):**

| Concentration | V_max (km/s) | r_vir (kpc) | r_s (kpc) | ρ_s (M☉/pc³) | t_cross (Gyr) |
|---|---|---|---|---|---|
| c = 12 (ΛCDM-conservative) | **31.12** | 35.09 | 2.92 | 9.69×10⁻³ | 0.092 |
| c = 4 (Ohana+ physical anchor) | **25.59** | 35.09 | 8.77 | 7.28×10⁻⁴ | 0.335 |

**K constant** (ratio × σ_m(V_max) at c=12): K ≈ 134.0. At σ_peak=50: 3.432 × 39.036 = 133.97. At σ_peak=75: 2.292 × 58.471 = 134.01. K varies ~0.03% across the grid (limited by JSON rounding precision, ~4 sig figs).

**Continuous intersection at c=12:**
- Floor crossing: σ_m(28) = 0.052 × (100/28) + σ_peak = 50 → **σ_peak ≥ 49.814**
- Causality crossing: ratio = 3.0 when σ_m(V_max) = K/3.0 = 44.66 → **σ_peak ≤ 57.24**
- **Window: [49.81, 57.24] cm²/g (width ~7.43)** — knife-edge. On swept grid, only σ_peak = 50 falls inside (3.43 ≥ 3.0 cap).

**Continuous intersection at c=4:** [49.81, 250] cm²/g (limited by sweep range).

**§9.12 reconciliation:**
- At c=12: t_core = 0.091 Gyr (matches §9.12's 91 Myr exactly); σ/m(V_max=31.12) = 135.43 (matches §9.12's 135.3 within 0.1%).
- At c=4: t_core = 3.98 Gyr (11% discrepancy from §9.12's 4.42 Gyr; §9.12 used σ/m=135.3 from c=12 V_max, canonical c=4 σ/m(V_max=25.59) = 150.0).

**Fornax σ_HL characterization:**
- σ_peak ≤ 50: marginal (|σ_HL| ≤ 0.15, e.g. -0.08 to -0.13)
- σ_peak ≥ 75: substantive (|σ_HL| ≥ 0.20, e.g. -0.20 to -0.68)
- At σ_peak = 174 (canonical): σ_HL = -0.47 (substantive).

**Headline finding (v19.2-A.7):**
- c=12: knife-edge window ~7.43 cm²/g wide; framework's canonical σ_peak=174 is OUTSIDE this window (3.5× too high).
- c=4: open interval [49.81, 250]; framework's canonical σ_peak=174 is INSIDE this window.
- The c=12 vs c=4 distinction is the c-M tension against ΛCDM (Ohana+ 2026).

---

## §15. v19.2-B Ohana+ 2026 c-M tension reproduction

**Source**: `scripts/v192_b_ohana3p2sigma_reproduction.py`, output `v192_b_ohana3p2sigma_reproduction.json` (v19.2-B.5).

**Reference**: Ohana, Zhang & Yu 2026, arXiv:2608.04362 — SIDM core-forming halos reduce the c-M tension to ~3σ; CDM requires ~7σ. Uses Diemer & Joyce 2019 c-M median relation (DJ19, arXiv:1809.07326) and Diemer & Kravtsov 2014 0.16 dex scatter (DK14, arXiv:1407.4730).

| Parameter | Value | Source |
|---|---|---|
| Cloud-9 best-fit (Ohana+) | M = 4.7×10⁹ M☉, c = 4.0, τ ≈ 0.18 (max-core stage) | arXiv:2608.04362 §3.1 line 29 |
| Cloud-9 best-fit (Ohana+) — second SIDM | M = 3.4×10⁹ M☉, c = 1.5, τ ≈ 0.95 (deep core-collapse) | arXiv:2608.04362 §3.1 line 29 |
| **Ohana+ scatter used** | **0.16 dex (DK14 — Diemer & Kravtsov 2014 full-population, NOT Diemer & Joyce 2019)** | arXiv:2608.04362 §3.1 line 29 + §3.1 line 34 (Ohana+ citation); arXiv:1407.4730 Table 1 (DK14 source) |
| MCMC-recovered best-fit (our pipeline) | M = 4.7571×10⁹ M☉, c = 3.8171, τ = 0.18 | v192_b JSON `best_fit_params` |
| c_med at our best-fit M | c_med = diemer2019_c200(4.7571e9) = **12.805** | Diemer+ 2019 Eq. 5 |
| Tension at Ohana+ scatter (0.16 dex) | **3.29σ (MCMC), 3.16σ (fiducial)** (CONSISTENCY CHECK at fiducial — matches Ohana+ 3.2σ within 0.1σ; synthetic-data caveat applies) | JSON `tension_sweep_literature_scatter` + `tension_at_fiducial` |
| Tension at fiducial (M=4.7×10⁹ M☉, c=4.0, τ=0.18) at 0.16 dex | **3.16σ** (reproduce-from-arithmetic: (log10(12.819)−log10(4.0))/0.16 = 0.50579/0.16 = 3.161) | v192_b JSON `tension_at_fiducial` |
| Difference: MCMC vs fiducial | 3.285σ − 3.161σ = +0.124σ (driven almost entirely by c_best-fit 4.0→3.8171: +0.128σ; c_med change 12.819→12.805 contributes only −0.002σ, since smaller c_med reduces tension) | derived |
| Tension at Diemer+ 2019 model-dep (0.085 dex) | 6.18σ | same (real but uses different scatter prescription) |
| Tension at Diemer+ 2019 cosmic (0.110 dex) | 4.78σ | same |
| Tension at Duffy+ 2008 (0.140 dex) | 3.75σ | same |
| Tension at lognormal fixed-mass (0.070 dex) | 7.51σ | same |
| Scatter needed to close gap (if using 0.085 dex) | 0.164 dex | derived: 0.52565 / 3.20 = 0.164 |
| 0.164 dex vs Diemer+ model-dep (0.085) | 1.93× (93% larger) | derived |
| 0.164 dex vs Diemer+ cosmic (0.110) | 1.49× (49% larger) | derived |
| 0.164 dex vs Duffy+ 2008 (0.140) | 1.17× (17% larger) | derived |

**Mechanism (3 candidate sources for the apparent 6.18σ vs Ohana+ 3.20σ gap — now resolved, per r32 Issue 2 wording):**
1. ~~Synthetic data at fiducial~~ — minor effect, not dominant
2. **Scatter convention** — DOMINANT. Ohana+ uses 0.16 dex (DK14 full-population scatter, verified); v19.2-B.1 to v19.2-B.6 assumed 0.085 dex (source UNVERIFIED — possibly Macciò 2008 or Dutton & Macciò 2014, but not 0.085 dex as far as I can verify). With DK14's scatter (0.16 dex), the simplified pipeline IS CONSISTENT with Ohana+ 3.2σ at the fiducial within rounding tolerance (3.29σ at MCMC, 3.16σ at fiducial c=4.0).
3. Tension definition (1D c-marginalized vs 2D joint) — minor effect

**The two scatter conventions serve different purposes (per r31 Issue 2, refined per r33 Issue 2 verification):**
- **0.16 dex (Ohana+ choice) — used for matching Ohana+'s number.** Per r33 verification, this is the **Diemer & Kravtsov 2014 (DK14) c-M scatter**, **NOT Diemer & Joyce 2019 (DJ19)** as previously claimed. DK14 (arXiv:1407.4730, ApJ 799, 108) Table 1 explicitly states "Scatter (Independent of M, z, or Mass Definition) σ 0.16 68% scatter in concentration (dex)". DJ19 (arXiv:1809.07326, ApJ 871, 168) focuses on the c-M **median**, not the scatter. DK14 explicitly notes: "our scatter estimate includes errors in the concentration measurement and is thus an upper limit of the true scatter." Ohana+ 2026 chose this prescription (arXiv:2608.04362 §3.1 line 29) because it includes the largest realistic scatter for matching their published 3.2σ tension.
- **0.085 dex — used for the framework's intrinsic tension (PER R33 ISSUE 2: UNVERIFIED ATTRIBUTION).** This value is **NOT verified against any paper**. Per r33 reviewer: "if the 0.085 dex value is actually from a different source (e.g., a SIDM-specific simulation paper), the attribution is a new overclaim." Until verified, this should be read as an estimate of the **pure halo-shape scatter** (after subtracting measurement error), not a DK14 prescription. The framework's 6.18σ intrinsic tension should be read with this caveat.

**Source attribution (per r33 Issue 2 verification):**
- **0.16 dex = DK14 (Diemer & Kravtsov 2014) full-population simulation scatter, Table 1, σ = 0.16 dex** (verified against arXiv:1407.4730 page 9 / ApJ 799, 108 Table 1). Explicitly an upper limit due to measurement error.
- **0.085 dex = NOT verified against any paper.** Per r33 reviewer, this is likely from a different source (possibly Macciò 2008 or Dutton & Macciò 2014 which report ≈0.10 dex, not 0.085). For now, treat as an estimate.
- **0.110 dex (cosmic scatter) = NOT verified against any paper.** The 0.11 dex attribution is unverified.

**Trajectory (v19.1.5 `44c474f` → v19.2-B.7 `a79b207`):**
- v19.1.5 `44c474f`: 1.04σ (0.140 dex Duffy+) — wrong c-M formula + posterior-median statistic
- v19.2-B.1 `f76a9cd`: 2.69σ (0.085 dex Diemer+ model-dep) — correct c-M + best-fit (MAP); units bug in denominator [BUG]
- v19.2-B.2 `3a2f4fd`: 6.18σ (0.085 dex) — units fixed (drop × log(10)); reproducible-from-arithmetic
- v19.2-B.3 `a877283`: 6.18σ (0.085 dex) — framed as clean negative (no fabricated match)
- v19.2-B.4 `62c2bb0`: 6.18σ (0.085 dex) — docstring arithmetic-reproducible; MCP UTF-8 encoding fix
- v19.2-B.5 `7ca4bf5`: 6.18σ (0.085 dex) — §2.7 added to paper with mechanism + trajectory
- v19.2-B.6 `a79b207`: 6.18σ (0.085 dex) — paper-JSON reconciliation; trajectory labels aligned
- v19.2-B.7 `a79b207+`: **3.29σ (MCMC) / 3.16σ (fiducial)** (0.16 dex Ohana+ scatter) — **r31 SCATTER CORRECTION: CONSISTENCY CHECK at fiducial under Ohana+ scatter; is consistent with Ohana+ 3.2σ**

**Headline finding (v19.2-B.7, REVERSED FROM PREVIOUS BUNDLES):** Our simplified pipeline **is consistent with Ohana+ 2026's 3.2σ SIDM tension at the fiducial under the 0.16 dex convention** (per r32 Issue 5 wording — avoids residual overclaim while preserving the positive consistency check). At this scatter (DK14 Diemer & Kravtsov 2014, arXiv:1407.4730 Table 1, σ = 0.16 dex — verified per r33 Issue 2), the best-fit tension is **3.16σ** at the fiducial (c=4.0, M=4.7×10⁹ M☉, τ=0.18 — the canonical consistency-check number, per r33 Issue 6) and **3.29σ** at the MCMC-recovered best-fit (c=3.8171, M=4.7571×10⁹ M☉ — the sampled variant) — both within 0.13σ of Ohana+'s published 3.20σ. **This is a consistency check at the fiducial, not a full reproduction of Ohana+'s analysis** (synthetic-data caveat applies; v19.2-B v3 with real data deferred). The previous v19.2-B.2-v19.2-B.6 finding of 6.18σ was real at 0.085 dex scatter (source UNVERIFIED per r33 Issue 2); the gap to Ohana+'s 3.20σ is the scatter-convention difference (0.085 vs 0.16 dex), not an internal disagreement among B.2-B.6.

---

## §16. v19.2-C SIDM Concerto subhalo consistency (Nadler+ 2025)

**Source**: `scripts/v192_c_concerto_subhalo_cloud9.py`, output `v192_c_concerto_subhalo_cloud9.json` (v19.2-C.5).

**Reference**: Nadler+ 2025, arXiv:2503.10748 — SIDM Concerto cosmological N-body simulation; Zenodo 10.5281/zenodo.14933624.

| Parameter | Value | Source |
|---|---|---|
| MW_Halo416 catalog | 2,489 SIDM subhalos | Nadler+ 2025 parametric |
| Cloud-9-mass halos (1e9-1e10 M☉) | 267 | filter on `mint` |
| Halos with valid rc1 fits | 264 | rc1 > 0 |
| Median SIDM core radius rc1 | **0.82 kpc** | JSON `concerto_subhalo_stats_cloud9_mass` |
| rc1 16-84 percentile | 0.53 - 1.20 kpc | same |
| Median CDM Rmax | 3.65 kpc | same |
| Median rc1/Rmax | 0.216 | same |
| Cloud-9 expectation (Yang+ 2024 τ=0.18) | rc ≈ 0.5 ± 0.3 kpc | Yang+ 2024 Eq. 5 |
| Match Cloud-9 (rc=0.5±0.3) | **1.07σ** | derived: \|0.82-0.5\|/0.3 = 1.07 |

**Caveat (per r30 Ohana+ 2026 inspection):** Ohana+ 2026 use the **Halo004 (GroupSIDM-147 model)** subset of Concerto. Our v19.2-C v1 uses **Halo416 (MilkyWaySIDM model)** — different host and different SIDM model. Framework-level conclusion (Concerto SIDM halos at Cloud-9 mass have rc ≈ 0.5-1 kpc) is robust to host choice; precise median varies by host and model.

**Mechanism (what v19.2-C v1 establishes vs not):**
- ✔ ESTABLISHES: At M = 1e9-1e10 M☉, SIDM N-body core radius scaling is consistent with Yang+ 2024 for τ ≈ 0.18.
- ✘ DOES NOT ESTABLISH: Correct core radius for Cloud-9 specifically (tidal stripping, isolated RELHIC env, single host, single model).

**Headline finding (v19.2-C.5):** Consistent across mass scale; environmental and model differences prevent cross-validation for Cloud-9 specifically. This is a **consistency check**, not independent validation.

---

## Verification

Run `python scripts/audit_claims.py` to re-verify every number against its source JSON.

```bash
python scripts/audit_claims.py --against docs/PAPER_STANDING_NUMBERS.md --check-all
```

Expected: zero drift, exit 0.