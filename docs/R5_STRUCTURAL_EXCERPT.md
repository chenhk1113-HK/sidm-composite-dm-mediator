===== §2.6a full block (L200-L226) =====
200| ### 2.6a σ_peak viability at ΛCDM-standard concentration (headline tension)
201| 
202| **First-class result (R88(26)) — the paper's most important internal tension, elevated from §2.6.**
203| 
204| At ΛCDM-standard concentration (c = 12), the framework's canonical σ_peak = 174 cm²/g fails the paper's own causality criterion (t_core >= 3 × t_cross) by a factor of ~3.5. This is a structural circularity: the framework claims to explain the Cloud-9 c-M tension, but the headline parameter works only if Cloud-9 has an anomalously low concentration (c ~ 4), which is itself the c-M tension the framework is trying to explain.
205| 
206| **Quantitative summary of the tension:**
207| 
208| | Quantity | c = 12 (ΛCDM-standard) | c = 4 (Ohana+ inferred) |
209| |---|---|---|
210| | Continuous viable σ_peak window | **EMPTY** (no viable σ_peak at c=12 with canonical Gaussian) | [51.96, 250] cm²/g |
211| | Canonical σ_peak = 174 cm²/g | **fails causality** (t_core/t_cross = 0.83, factor ~3.6 below cap, r_s/V_max convention) | passes (ratio = 14.83, well above cap) |
212| | σ/m(28) at canonical σ_peak | 166.02 cm²/g (well above 50 cm²/g floor) | 166.02 cm²/g |
213| | σ/m(V_max) at canonical σ_peak | σ/m(31.12) = 161.70 cm²/g | σ/m(25.59) = 120.32 cm²/g |
214| | t_core at canonical σ_peak | 76 Myr (causality violated) | 4.97 Gyr |
215| | Verdict at headline parameter | framework **incompatible with ΛCDM at any σ_peak** | framework internally consistent (marginally) |
216| 
217| **Implications for the paper's central claims:**
218| 
219| 1. **Cloud-9 c-M tension:** The paper's headline (Cloud-9 c-M tension at 3.16σ against Ohana+ 2026's 3.2σ at the 0.16 dex DK14 convention) is itself the tension whose resolution would normally require σ_peak ≈ 174 cm²/g at the Ohana+ inferred c ~ 4. At c = 12 (the Ohana+ paper's population-median concentration), the framework cannot sustain σ_peak = 174 cm²/g.
220| 
221| 2. **dSph non-collapse:** Fornax σ_HL outlier (σ_HL_required = −0.47 cm²/g, unphysical negative) is a consequence of the v₁ Gaussian tail (σ₁ = 4.4 km/s) reaching v = 15. This is robust against c = 12 vs c = 4 selection. The Fornax tension is independent of the σ_peak viability tension at c = 12.
222| 
223| 3. **Path forward (gravothermal roadmap):** The c = 12 tension may resolve under phase-aware gravothermal modeling (G1-G6 in §A.10b and `GRAVOTHERMAL_ROADMAP.md`). The phase-diversity hypothesis predicts that halos at the same σ/m(v) but different gravothermal phases (core-expansion vs. collapse) should have different central densities. If Cloud-9 is in core-expansion phase and Fornax is in collapse phase, the same canonical σ_peak can satisfy both observations without requiring σ_HL_required < 0.
224| 
225| **Honest framing:** This tension is not fatal for a constraint map + no-go catalogue paper. It does, however, imply that the framework's headline σ_peak = 174 cm²/g value is conditional on Cloud-9 having c ~ 4. A reader should encounter this before the dSph tension discussion in §3.6, because the dSph prediction depends on the same canonical σ_peak.
226| 

===== §9.13 opening (L1206) =====
1206| ### 9.13 Gravothermal evolution: a proposed resolution pathway for the §2.6a circularity (Phase G4-G6 forward work, not yet a result)
1207| 
1208| **Status:** This section is **forward-looking**. The argument below is supported by Phase G1 Yang+ 2024 calibration (`gravothermal_yang2024.py`) and existing N-body literature (Fischer & Yu 2026; Silverman+ 2026), but a complete resolution requires Phase G4 (massive-halo gravothermal pipeline) which is currently scoped but not implemented.
1209| 
1210| **The circularity (§2.6a restated):** The framework's canonical σ_peak = 174 cm²/g satisfies the causality criterion only at c ≈ 4 (Ohana+ inferred concentration); at ΛCDM-standard c = 12, the framework violates causality by a factor of ~3.6 (ratio = 0.83). This means the framework's headline parameter works only at the very concentration it claims to explain. A static-σ/m(v) framing makes this look circular: the framework explains Cloud-9's anomalous low concentration using parameters that only work at that low concentration.
1211| 

===== §9.18 opening (L1590) =====
1590| ### 9.18 Forward-path exploration summary (R88(72)-(78)) — exhaustive search completed
1591| 
1592| **Status:** R88(72)-(78) documented the exploration of four forward paths to test the trade-off's f_H(r) compatibility result (§9.17b, R88(88) restated). **ALL FOUR PATHS FAILED** — the trade-off holds because no tested modification can give a physically-derived centre-peaked f_H(r) the high f_H(r_obs) needed at Cloud-9 and SPARC observation radii. This section consolidates the evidence.
1593| 

===== '## 10.' header location (L1685) =====
1685| ## 10. UV Completion: No-Go Theorems, Two-Mediator Candidate, Cloud-9 Robustness
1686| **Scope :**The five no-go theorems below apply specifically to the**Phase 44 single-component σ/m = 0.052 cm²/g at v = 100 km/s baseline**with standard Yukawa physics. The T163 KK-tower best-fit parameters (α_D = 0.3, m₀ = 0.3 GeV, r = 1.5, n_modes = 2, RMSE = 1.408) are a finer-grained realization within the same Phase 44 framework.**T175 was run on 2026-09-21 and confirms all 4 no-go verdicts hold at T163 parameters**. The failure mechanisms (LZ direct detection, kinematic forbiddance, unitarity violation, flat velocity dependence) are independent of the specific σ/m value.**T213 (KK tower + Silverman+ combined, 2026-09-26) confirms T163 KK tower σ/m(V_max = 31.12 km/s) = 0.174 cm²/g, which is 5.7× below the Silverman+ 2026 gravothermal threshold of 1.0 cm²/g.**The KK tower is in the Born regime where σ ∝ α²/m_med² (no Sommerfeld enhancement at low v); the velocity dependence is flat across 5-500 km/s (factor < 1.04). T184 one-mediator UV systematic is qualitatively different from the other four: it is a general scaling argument rather than a specific UV construction.**T213 structural implication:**The Cloud-9 spike (σ/m ≥ 50 cm²/g) cannot be reproduced by T163 KK tower alone, and Path F1 three-term σ_eff decomposition cannot bridge the 5.7× gap because the σ_HL peak is at v_HL ≈ 100 km/s (SPARC scale), not v = 31 km/s (Cloud-9 host V_max). The combined T163 + T212 + T213 result reinforces the**structural constraint map verdict**: single KK tower is the wrong tool for Cloud-9 scale, Silverman+ gravothermal is the right mechanism but wrong mass scale, and no published 2026 SIDM mechanism bridges the gap.**T215 KiSS-SIDM real N-body simulation:**T215 IC generator produces 10⁴-particle virialized NFW halo (v_rms = 33 km/s = V_max = 31.12 km/s). KiSS-SIDM runs at σ/m = 70 cm²/g with 3000-particle subsample reach t = 26 Myr (15% of Balberg t_core = 0.176 Gyr). Density at r = r_s decreases by 23% over 24 Myr (from 1.83×10⁻³ to 1.41×10⁻³ M☉/pc³), consistent with gravothermal**core expansion**(Kaplinghat+ 2016 isothermal core formation), NOT collapse. Core collapse (gravothermal phase) NOT directly observed within run window. The 5.7× gap from T213 and the silent-crash limitation of KiSS-SIDM at long simulated times mean the v18.43 kinetic simulation confirms the qualitative SIDM physics (core expansion under high σ/m) but does NOT close the Cloud-9 gap. T215 results at [`v0.3-prelim/docs/T215_KISS_SIDM_CLOUD9_GRAVOTHERMAL_2026-09-26.md`] .**T215b KiSS-SIDM breakthrough:**Root cause of silent crash identified — KiSS-SIDM `collision.jl` calls `sqrt(v_rms^2 - sum(vbar.^2))` without float-protection. When adaptive grid splits a cell, FP rounding causes `sum(vbar.^2)` to exceed `v_rms^2` by 2.27×10⁻¹³, throwing `DomainError`.**Patched 3 lines in collision.jl**(identical to existing time_step.jl fix).**Result: KiSS-SIDM run extended from 26 Myr to 45 Myr (1.7× improvement).**More importantly,**gravothermal catastrophe IS observed**in the kinetic simulation:
1687| 

===== §10.1 opening (L1688) =====
1688| ### 10.1 UV completion: general framework and constraints
1689| 
1690| The phenomenology is consistent with **4 of 7 constrained channels** (SPARC, Cloud-9, dSph, Cluster, JVAS, Lei+ 2026 [55b], Wang+ 2026 [55c]) under physically motivated f_H; **7 of 10** only under retracted borrowed f_H** (§9.3, §9.7). The two counts describe different f_H assumptions: physically motivated vs. retracted borrowed f_H. With the borrowed (hand-picked placeholder, retracted v18.29) f_H values, 7 of 8 channels pass; with Yang+ 2025-derived or T202 N-body-derived f_H, only 4 of 8 pass. The Cloud-9 vs dSph tension is**unresolved at Phase 44 parameters**when f_H is derived from a first-principles source. The 8th channel (the Elbert+ 2015 σ/m ≥ 50 working benchmark floor at v=28 km/s) is published and confirmed independently by Ohana, Zhang & Yu 2026 [15e] via MCMC, but cannot be derived from standard Yukawa physics; the heavy-channel-only σ_eff = f_H² × σ_HH(v) decomposition also cannot match SPARC's σ/m ≈ 0.193 at v = 100 km/s. This is honest: we present**a constraint map, not a self-consistent derivation**, and document what UV physics would need to look like to reproduce the full 8 channels.**Path F1 addresses the SPARC structural limitation**by adding the σ_HL term: the three-term decomposition σ_eff = f_H² σ_HH + 2 f_H f_L σ_HL + f_L² σ_LL reaches σ_eff(100) ≈ 0.19 via the heavy-light cross-section under borrowed prescription mode (v_HL ≈ 100 km/s, σ_peak_HL ≈ 0.34). The free fit with Yang+ 2025 f_H_cc ≥ 0.05 prior lands at v_HL = 105 ± 39 km/s but fails SPARC at the posterior median (log L = -2.03, z ≈ 2.0); Path F1 is therefore**structurally sufficient but not automatically data-satisfying**without prescription-mode f_H.**Layer 3 real σ_pred re-derivation at v=100:**A real verification of the §9.11 verdict split — computing σ_pred(v=100) from the paper's three-term Path F1 model using each prescription's fitted parameters and comparing to the paper's reported per-channel log L values. SPARC v=100 uses `halo_class='intermediate'`, so f_H_int = 0.5 × (f_H_cf + f_H_cc):

===== §10.3 table (L1748) =====
1748| ### 10.3 Two-mediator candidate (Drobczyk 2025): thermal relic density**§10.3 — Thermal relic density UV completion . Note: §10.3.1 referenced in earlier drafts as a sub-subsection; consolidated into §10.3 in this version.**Scope clarification:**This section
1749| addresses the**thermal relic density**problem (Ωh² = 0.12), NOT the**Cloud-9 4000× spike**which remains an open problem requiring physics
1750| beyond standard Yukawa . The two-mediator framework decouples annihilation from
1751| self-scattering but does not produce Cloud-9's specific spike — that
1752| remains substructure physics per Yu 2026 [23] (§3.3, §10.4c.A5).
1753| 
1754| T181 established that the SIDM phenomenology σ_HH = 0.05 cm²/g is the**elastic self-scattering cross-section**, distinct from the annihilation
1755| cross-section <σv>_ann that determines relic density.**One-mediator UV completions ruled out :**A purely thermal WIMP-miracle UV completion with ONE mediator is**NOT
1756| viable**at our SIDM parameters . See §10.2a-d for the systematic no-go theorems.**T185 — Two-mediator resolution (positive result):**The two-mediator solution proposed by Drobczyk (arXiv:2506.22997v3,
1757| CQG 42 (2025) 225006)**resolves**the tension via s-channel Breit-Wigner

===== abstract framework score line =====
23| **Framework score (per A.15 canonical, R88(52) honest + v19.2-E A.1 caveat):** 8 constrained channels. Under the canonical (self-normalized σ_unc) accounting: **4 PASS / 3 MARGINAL / 1 FAIL** (PASS = Cluster v=500, dSph v=10, Cloud-9 v=28, SPARC v=100; MARGINAL = UFD v=3, UFD v=5, UFD v=15; FAIL = dSph v=7; see §A.15 Block 1). Under the promoted published-σ_unc likelihood (T205, v19.2-E A.1) the SAME canonical parameters give **1 PASS / 0 MARGINAL / 7 FAIL** (Cluster v=500 only); the 5-parameter DE best-fit reaches 5/8 at that likelihood (§A.15 Blocks 2–3). **Both counts are stated here because they differ only by likelihood convention, and a reader who sees only one of them would draw a materially different conclusion.** The Lei/Wang v=150 entry is the **R88(87) TUNING statement, not a separate PASS** (ClawsGO #7 §2b: Lei/Wang and Sameie+ 2020 are the same v=150 constraint counted under different names; the "no-go" is a tuning statement about Phase G7's specific σ_peak2 = 5.0 choice, NOT a structural constraint of the framework). **v19.2-E A.1 caveat:** under the promoted real likelihood (T205 8-channel published-σ_unc), the **canonical Phase 44 parameters** (σ₀=0.052, a=1.93, σ_peak=174, v_target=29.4, σ₁=4.4) pass **1 of 8 channels** (Cluster v=500 only). The 5-parameter DE best-fit (v19.2-E A.2) at the same likelihood passes **5 of 8** (σ_peak=2026, σ₁=1.2). The "canonical" σ(v) presented in this paper is the v1 free-fit result; v19.2-E shows the data prefer a different (5-param DE) point at 5/8. The counts 1/8 and 5/8 use the SAME 8 channels under different parameter priors. This caveat belongs wherever "canonical" appears. The framework is a constraint map, not a unified SIDM model.
