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
| Cloud-9 V_max | 24.75 km/s | same |
| Cloud-9 r_vir | 35,093 pc | same |
| Cloud-9 r_s | 2,924 pc | same |
| ρ_s | 9.69×10⁻³ M☉/pc³ | same |
| **t_core (Phase 44 σ/m)** | **73.71 Gyr** | same |
| t_Hubble | 13.8 Gyr | (Planck) |
| **Verdict** | **gravothermal DOES NOT run at Phase 44 σ/m** | same |
| Path 2 | **REFUTED** at Phase 44 σ/m | same |

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

## §13. Layer 3 paper §9.11 self-consistency check (v19.0.1)

| Prescription | f_H | log L | z | Reported | Computed (under paper threshold convention) |
|---|---|---|---|---|---|
| **borrowed** | 0.85 | -0.09 | 0.42 | RESOLVED | RESOLVED ✓ |
| **yang** | 0.79 | -0.24 | 0.69 | MARGINAL | MARGINAL ✓ |
| **t202** | 0.92 | -0.60 | 1.10 | NOT RESOLVED | NOT RESOLVED ✓ |
| **priored free fit** | 0.06 | -2.03 | 2.01 | CLEAR FAIL | CLEAR FAIL ✓ |

**Source:** `scripts/jia2026_sparc_check.py` (consistency check, NOT verification).

**SCOPE — this is a consistency check, NOT a verification** (per rev192.docx Reviewer 1):
- Takes the paper's reported log L values from §9.11 as inputs.
- Applies the paper's implicit threshold convention.
- Confirms the four reported verdicts land in the intended bins.
- Does NOT compute σ_pred(v=100) from the three-term Path F1 model.
- Does NOT independently derive log L.

A true verification would compute σ_pred(v=100) from the paper's parameters (σ_peak_HL, v_HL, widths) for each f_H prescription, then compare computed log L to the paper's reported values. That requires full Path F1 pipeline reproduction and is deferred to v19.1.

**Threshold convention (paper's implicit):**
- RESOLVED      log L >= -0.10
- MARGINAL      -0.30 <= log L < -0.10
- NOT RESOLVED  -2.00 <  log L < -0.30
- CLEAR FAIL    log L <= -2.00

**Honest framing:** §9.11 verdict split is self-consistent under the paper's stated threshold convention. The "log L = -2.03 CLEAR FAIL" verdict is robust under T205 σ_unc (= 0.05 from SPARC measurement); the earlier v19.0 claim that "this was a T206 self-normalization artifact" was incorrect (rev19.docx Reviewer 2). The single-point σ/m-only check is NOT sufficient to overturn the verdict split; full Path F1 joint likelihood remains the controlling test. **Headline verdict unchanged.**

**T183 (f_H = 0.61) is NOT in §9.11 verdict split.** T183 is a separate result (v18.32 fluid approximation) and is not part of the paper's headline table. If T183 appears elsewhere in the draft, it should be labeled non-canonical for the §9.11 verdict split.

---

## Verification

Run `python scripts/audit_claims.py` to re-verify every number against its source JSON.

```bash
python scripts/audit_claims.py --against docs/PAPER_STANDING_NUMBERS.md --check-all
```

Expected: zero drift, exit 0.