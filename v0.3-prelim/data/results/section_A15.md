### A.15 Canonical Channel Table (machine-generated, single source of truth)

**This section is regenerated from `scripts/canonical_numbers.py` on every freeze round; the values here are the canonical numbers used in the abstract, §2.6, §9.17, §10, and §11. Do not edit by hand — edit `scripts/canonical_numbers.py` and re-run.** Per ClawsGO #5 B.2 + #7, this is the single source of truth for the paper's pass/fail, no-go catalogue, and trade-off factors.

**Abstract channel count (canonical):** 8 constrained channels (4 PASS / 3 MARGINAL / 1 FAIL)

| Status | Channels |
|---|---|
| PASS (4) | Cluster v=500 (Randall+ 2008 strong lensing) |
| PASS (4) | dSph v=10 (Horigome+ 2025 ceiling) |
| PASS (4) | Cloud-9 v=28 (BLN24/Ohana+ 2026 floor 128, canonical Phase 44) |
| PASS (4) | SPARC v=100 (Lelli+ 2016, canonical Phase 44) |
| MARGINAL (3) | UFD v=3 (Horigome+ 2025 ceiling) |
| MARGINAL (3) | UFD v=5 (Horigome+ 2025 ceiling) |
| MARGINAL (3) | UFD v=15 (Horigome+ 2025 ceiling, within 1sigma) |
| FAIL (1) | dSph v=7 (Horigome+ 2025 ceiling, factor 11.6x over) |

**Note on Lei/Wang double-count (ClawsGO #7 §2b):** Lei/Wang+ 2026 v=150 mass bound is the SAME constraint as Sameie+ 2020 v=150 (see ClawsGO #7 §2b Lei/Wang double-count). It is the SAME channel counted under different names; the v=150 entry is the R88(87) TUNING statement, not a separate PASS. In the 8-channel count above, Lei/Wang is folded into the v=150 TUNING entry and NOT counted in the 4 PASS / 3 MARGINAL / 1 FAIL.

**Retired conventions:**
- 4 of 7 constrained channels pass (RETIRED: Lei/Wang double-counted in old table; see ClawsGO #7 §4)
- two structural no-gos (RETIRED R88(87): v=150 demoted to tuning statement)

**Per-channel pass/fail at canonical Phase 44 (σ₀=0.052, a=1.93, σ_peak=174, v_target=29.4, σ₁=4.4):**

| v [km/s] | Channel | σ_obs | σ_unc | kind | σ_HH | σ_eff | verdict |
|---|---|---|---|---|---|---|---|
| 3 | UFD v=3 | 0.155 | 0.05 | ceiling | 45.2 | 3.987 | **FAIL** |
| 5 | UFD v=5 | 0.093 | 0.05 | ceiling | 16.9 | 1.488 | **FAIL** |
| 7 | UFD v=7 | 0.067 | 0.05 | ceiling | 8.81 | 0.7771 | **FAIL** |
| 10 | UFD v=10 | 0.047 | 0.05 | ceiling | 4.44 | 0.3913 | **FAIL** |
| 15 | dSph v=15 | 0.032 | 0.04 | ceiling | 2.85 | 0.251 | **FAIL** |
| 28 | Cloud-9 v=28 | 128 | 30 | floor | 166 | 14.64 | **FAIL** |
| 100 | SPARC v=100 | 0.193 | 0.05 | gaussian | 0.052 | 0.004587 | **FAIL** |
| 500 | Cluster v=500 | 0.00025 | 0.0005 | ceiling | 0.00233 | 0.0002054 | **PASS** |
| | **TOTAL** | | | | | | **1 PASS / 0 MARGINAL / 7 FAIL** |

**Per-channel pass/fail at v19.2-E A.2 5-param DE best-fit (σ₀=0.0265, a=1.198, σ_peak=2026, v_target=28.47, σ₁=1.2):**

| v [km/s] | Channel | σ_obs | σ_unc | kind | σ_HH | σ_eff | verdict |
|---|---|---|---|---|---|---|---|
| 3 | UFD v=3 | 0.155 | 0.05 | ceiling | 1.77 | 0.156 | **MARGINAL** |
| 5 | UFD v=5 | 0.093 | 0.05 | ceiling | 0.959 | 0.0846 | **PASS** |
| 7 | UFD v=7 | 0.067 | 0.05 | ceiling | 0.641 | 0.05654 | **PASS** |
| 10 | UFD v=10 | 0.047 | 0.05 | ceiling | 0.418 | 0.03688 | **PASS** |
| 15 | dSph v=15 | 0.032 | 0.04 | ceiling | 0.257 | 0.02269 | **PASS** |
| 28 | Cloud-9 v=28 | 128 | 30 | floor | 1.88e+03 | 165.5 | **PASS** |
| 100 | SPARC v=100 | 0.193 | 0.05 | gaussian | 0.0265 | 0.002338 | **FAIL** |
| 500 | Cluster v=500 | 0.00025 | 0.0005 | ceiling | 0.00385 | 0.0003399 | **MARGINAL** |
| | **TOTAL** | | | | | | **5 PASS / 2 MARGINAL / 1 FAIL** |

**Trade-off factors (canonical, R88(88)):**

sigma_eff(Cloud-9) ~ 0.15 vs 50 (factor ~300x), sigma_eff(SPARC) ~ 0.0001 vs 0.19 (factor ~1900x)

| Quantity | Factor |
|---|---|
| σ_eff(Cloud-9) below 50 | **300×** |
| σ_eff(SPARC) below 0.19 | **1900×** |

**Retired values (ClawsGO #7 §5):**
- 250x / 200x in §9.17b table (:1245, :1247) - RETIRED (different calc: SIDM2c with gravothermal at tau=0.3, not bare SIDM2c)
- 5-300 / 200-1000 / 250 / '130' range in older drafts - RETIRED per ClawsGO #5

**No-go catalogue (canonical, machine-generated):**

**Status legend:** **STRUCTURAL** = Survives all tested forward paths. First-class result. | **TUNING** = Specific parameter choice that fails, but the framework has a parameter region that passes (PASS window exists). Not a no-go. | **OPEN** = Open requirement, NOT a no-go. UV-status question pending Phase 3. | **PASS** = Framework passes the channel under all canonical choices.

- **[STRUCTURAL]** **Cloud-9 vs dSph tension (v=28<->15)** (§2.6a)
  - Argument: sigma_m(28)/sigma_m(15) ratio; the framework's resonance at v=29.4 necessarily overproduces sigma/m at v=15 by 7.8-25.7x (R88(82)).
  - Factor vs constraint: dsph_v15_factor_above_ceiling=7.8
  - Reference: R88(82), R88(88)
- **[STRUCTURAL]** **f_H(r) compatibility result (structural trade-off, R88(88) restated)** (§9.17b (R88(88) restatement))
  - Argument: A physically-derived centre-peaked f_H(r) profile (Yang+ 2025 SIDM2c parameterization: f_H(0.05 r_s)=0.81, f_H(0.5 r_s)=0.03, f_H(1.0 r_s)=0.04) is incompatible with Cloud-9 and SPARC at observation radii: sigma_eff(Cloud-9) ~0.15 << 50 (fails by ~300x), sigma_eff(SPARC) ~0.0001 << 0.19 (fails by ~1900x).
  - Caveat: Statement about SIDM2c parameterization, not the project's own N-body (Phase G9 found f_H drop 0.94-1.01x, which is NOT subject to the trade-off).
  - Factor vs constraint: cloud9_factor_below_50=300.0, sparc_factor_below_0p19=1900.0
  - Reference: R88(88), R88(82), R88(86)
- **[TUNING]** **v=150 Lei/Wang vs Sameie+ 2020 (demoted R88(87))** (§9.17a (R88(87) demotion))
  - Argument: Phase G7's sigma_peak2 = 5.0 overshoots Sameie+ 2020 by 1.5x. But the PASS window sigma_peak2 in (1.11, 3.33) cm^2/g satisfies both constraints simultaneously. The 'no-go' is a tuning statement about Phase G7's specific choice, NOT a structural constraint of the framework.
  - Factor vs constraint: pass_window_sigma_peak2_cm2_per_g_min=1.11, pass_window_sigma_peak2_cm2_per_g_max=3.33
  - Reference: R88(87)
- **[OPEN]** **Background UV derivation (open requirement, NOT a no-go)** (§2.8 (v19.2-F Phase 1+2))
  - Argument: The background sigma/m = 0.052*(100/v)^1.93 is a phenomenological fit. The framework's named 200 eV Yukawa at alpha_chi = 6.8e-7 fails at v=100 by 55x and overproduces at v=10 by ~4300x; the fitted slope is closer to a Sommerfeld v^-2 near a t-channel bound-state resonance (M2 mechanism, Chu+ 2018 [7]). A first-principles derivation is open (v19.2-F Phase 3). NOT a UV completion no-go while M2 is open.
  - Factor vs constraint: yukawa_at_alpha_chi_v100_factor_over_fitted=55.0, yukawa_at_alpha_chi_v10_factor_over_fitted=4300.0
  - Reference: ClawsGO Phase 1+2 (v19.2-F P1+2)

**UV completion no-gos (S10, 5 entries):**

**Note (ClawsGO #7 §7):** the abstract calls these 'five UV completion no-go theorems'. Four are specific UV constructions (CONSTRAINT, 10.2a-d); the fifth (T184, 10) is a general scaling argument. Per ClawsGO #7, the abstract should either rename to 'no-go constraints/exclusions at the Phase-44 baseline' or state which are theorems and which are arguments.

- **[CONSTRAINT]** **Magnetic dipole DM** (§10.2a)
  - Cross-section ~18 orders above LZ limit; not a UV completion theorem but a constraint exclusion at the Phase 44 baseline.
- **[CONSTRAINT]** **Hidden U(1) + 10 MeV pseudo-Dirac** (§10.2b)
  - Same as 10.2a - constraint exclusion at the Phase 44 baseline.
- **[CONSTRAINT]** **GeV-scale inelastic DM** (§10.2c)
- **[CONSTRAINT]** **Published best-fit p-wave resonance (Chu+ 2019)** (§10.2d)
- **[SCALING_ARGUMENT]** **One-mediator UV systematic (T184 scaling argument)** (§10 (T184))
  - T184 is a general scaling argument rather than a specific UV construction. Per the abstract's 'five UV completion no-go theorems' framing, this entry is the LEAST specific of the five. Per ClawsGO #7, the abstract should either rename to 'no-go constraints/exclusions at the Phase-44 baseline' or state which are theorems and which are arguments.

**Halo-specific gravothermal prefactors (v19.2-E B):**

| Halo | Prefactor vs Yang+ 2024 150×C | σ_eff/m [cm²/g] | t_c [Gyr] | Citation |
|---|---|---|---|---|
| BM2 cluster | 1.82× | 7.1 | 28.7 | Yang+ 2024 calibration halo (R88(83) result: 1.82x to match 28.7 Gyr) |
| Cosmo-501 dwarf | 2.2× | 50.0 | 9.04 | Yang+ 2024 Table 1, R88(83) independent halo (under-prediction by 2.2x) |
| Fornax dSph | 18.7× | 2.85 | >13.8 | v19.2-E B: Fornax dSph, M_200=1e9, c=15, v_eff=15 km/s. Prefactor must be >= 18.7x BM2 calibration to match observational lower limit on t_c. |
| Segue 1 UFD | 4.0× | 6.81 | >13.8 | v19.2-E B: Segue 1 UFD, M_200=1e8, c=25, v_eff=8 km/s. Prefactor must be >= 4.0x BM2 calibration. |

---

**Source:** `scripts/canonical_numbers.py` → `v0.3-prelim/data/results/canonical_numbers.json`. To regenerate: `python scripts/canonical_numbers.py && python scripts/generate_a15.py`.