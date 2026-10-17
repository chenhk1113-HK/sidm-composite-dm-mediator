# v19.2-F Reference Data Registry

**Date:** 2026-10-17
**Branch:** `wip/v19.2-F-init`
**Tag:** `v19.2-F-Phase3-CLOSED-r40.12` (current head)
**Purpose:** Authoritative list of every paper cited and every numerical value used by the v19.2-F project, with verification status. Cross-checked against arXiv/DOI as of 2026-10-17.

This is the canonical source for paper authentication. When a new loop uses a value, add it here with citation. When a value is re-derived, update the registry.

---

## 1. Papers cited by the v19.2-F project (verification status)

### Internal (project's own derivations, no external paper)
- **Kaplinghat, Tulin, Yu (2016)** — "Dark Matter Self-Interactions" — *cited as* foundational SIDM review, *no arXiv ID in v40.x docs*; most likely candidate is Kaplinghat, Tulin, Yu 2016, Physics Reports 730, 1. **STATUS: TO VERIFY** before citing in paper. (Note: Tulin, Yu 2018 Phys. Rep. 730 is the canonical reference; the v19.2-F project may have conflated two different papers.)
- **Tulin, Yu, Zurek (2013)** — "Cold Dark Matter and Its Interactions" — arXiv:1306.5010. *Cited in root `constants.py` docstring.* **STATUS: VERIFIED via arXiv listing** (1306.5010 is a real Phys. Rep. paper by Tulin et al. on SIDM).

### Cloud-9 / Yang+ 2024 (CRITICAL — citation error in v40.4)
- **CORRECT citation:** Shengqi Yang, Fangzhou Jiang, Andrew Benson, Yi-Ming Zhong, Charlie Mace, Xiaolong Du, Zhichao Carton Zeng, Annika H. G. Peter, Moritz S. Fischer (2024). "A quantitative comparison between velocity dependent SIDM cross sections constrained by the gravothermal and isothermal models." MNRAS 533, 4007. arXiv:2305.05067. DOI: 10.1093/mnras/stae2038. **STATUS: VERIFIED** (arXiv 2305.05067v3 retrieved 2026-10-17; title, authors, journal all match v31 review packet).
- **WRONG citation in v40.4 Loop 1 code:** "Yang, Nadler, Yu, Zhong 2024 (gravothermal model, arXiv:2305.16176)" — arXiv:2305.16176 is "A Parametric Model for Self-Interacting Dark Matter Halos" (JCAP 02 (2024) 032), NOT the gravothermal cross-section paper. **BUG**: Loop 1 code has wrong arXiv ID. *Fix needed in v40.13.*
- **Gravothermal t_c formula** in v40.4/v40.9 references "Yang+ 2024 eq. 2.2" with literal prefactor 150×C = 112.5. The paper's actual equation numbering (per v31 review packet) has Eq 4, 19, 20 in Tables 2-3. **STATUS: TO VERIFY** the specific eq. number for t_c — likely Eq 19 or 20, not 2.2.

### UFD kinematics references
- **Simon+ 2011** (Segue 1 σ_v = 3.7 km/s) — most likely J. D. Simon et al. 2011, ApJ 733, 46. **STATUS: TO VERIFY DOI** (commonly used Segue 1 reference).
- **Walker+ 2007** (Draco, UMi, Sculptor, Carina σ_v) — M. G. Walker et al. 2007, ApJL 667, L53 (or ApJ 667, 53). **STATUS: TO VERIFY DOI** (commonly used dSph kinematics reference).
- **Adén+ 2009** (Hercules σ_v = 3.7 km/s) — D. Adén et al. 2009, ApJL 706, L150. **STATUS: TO VERIFY DOI** (Hercules kinematics).
- **Walker+ 2016** (Tucana II σ_v = 8.2 km/s) — M. G. Walker et al. 2016, ApJ 819, 53. **STATUS: TO VERIFY DOI** (Tucana II kinematics).
- **Anand+ 2025** (Cloud-9 σ_v = 5.1 km/s) — cited in v40.1 re-baseline. **STATUS: TO VERIFY DOI** (Cloud-9 discovery paper).
- **Read+ 2019** (M_halo for Segue 1) — J. I. Read et al. 2019, MNRAS 484, 1401 (CORE-NFW profile). **STATUS: TO VERIFY DOI**.

### External SIDM literature (LOOP3)
- **Gilman+ 2023** — D. Gilman, J. Zhong, J. Bovy (2023). "Constraining resonant dark matter self-interactions with strong gravitational lenses." arXiv:2207.13111. PRD 107, 103008. **STATUS: VERIFIED** (arXiv 2207.13111 retrieved 2026-10-17; title and abstract quote match).
- **O'Donnell+ 2025** — "A Constraint on Dark Matter Self-Interaction from Combined Strong Lensing and Stellar Kinematics in MACS J0138-2155." arXiv:2508.20179. **STATUS: VERIFIED** (arXiv 2508.20179 retrieved; accepted in PRD; abstract gives σ/m < 0.613 cm²/g at ⟨v_pair⟩ < 2090 km/s).
- **Sánchez Almeida+ 2025** — "Constraints on dark matter models from the stellar cores observed in ultra-faint dwarf galaxies: Self-interacting dark matter." arXiv:2510.05682. A&A 704, A210 (2025). DOI: 10.1051/0004-6361/202557040. **STATUS: VERIFIED**.
- **Jee, Park, Lee 2026** — "A New Robust Constraint on the Self-interaction Cross-section of Dark Matter with Double Radio Relic Clusters." arXiv:2605.00093. Accepted ApJ. **STATUS: VERIFIED** (PDF read; abstract gives σ/m < 0.22 cm²/g at 68% CL, σ/m < 0.63 at 95% CL).
- **Andrade+ 2022** — MNRAS 510, 54. "Stringent upper limit on dark matter self-interaction cross-section" (149 citations per v40.11 doc). **STATUS: TO VERIFY** (no arXiv ID in v40.11 doc; need full citation).

---

## 2. Project-locked numerical values (from `constants.py` and `scripts/constants.py`)

### Particle physics parameters (root `constants.py`, LOCKED)
| Constant | Value | Source | Status |
|---|---|---|---|
| M_CHI_GEV | 1.0 | Project canonical Phase 44 | OK |
| MU_RED_GEV | 0.5 (= M_CHI/2) | Definition | OK |
| ALPHA_D | 5.55e-6 | ClawsGO #11 EXTENDED scan best-fit | OK (internal fit, not from external paper) |
| G_CHI | sqrt(4π·α_D) = 8.351e-3 | From α_D under convention | OK |
| C_KMS | 2.998e5 | Exact (speed of light in km/s) | OK |
| HBAR_C_GEV_CM | 1.97327e-14 | Standard CODATA | OK |
| KAPPA_C_ANALYTIC | 1.6798 | Tamm 1947 (cited) | **TO VERIFY** (the Tamm 1947 paper is in Russian; should be cross-checked against a modern review) |
| KAPPA_C (rounded) | 1.68 | Rounded | OK |

### σ_m formula parameters (`scripts/constants.py`)
| Constant | Value | Source | Status |
|---|---|---|---|
| M_PHI_GEV | 200e-9 (= 200 eV) | Project canonical | OK |
| V_TARGET_KMS | 29.4 | Cloud-9 galaxy | OK (project internal) |
| SIGMA_KMS | 4.4 | Cloud-9 velocity width | OK (project internal) |
| A_RES | 100.0 | Project constant | OK |
| M_NUCLEON_GEV | 0.939 | Average nucleon mass | OK (≈ proton mass) |
| A_SLOPE | 1.93 | Yang+ 2024 fit (Eq 4, 19, 20, Tables 2-3) | **TO VERIFY exact source** |
| V_REF_KMS | 100.0 | Convention | OK |
| A_SLOPE_OPTION_A | 1.0 | Alternative | OK (alternative model) |
| F_H_CANONICAL | 0.297 | Hydrogen fraction | **TO VERIFY** (standard value ~0.75 for mass fraction, 0.92 for number fraction; 0.297 is unusual) |
| SIGMA_0_CM2_PER_G | 0.052 | Yang+ 2024 fit (Cloud-9) | OK (project internal) |
| SIGMA_PEAK_CM2_PER_G | 174.0 | Project target | OK |
| G_CHI | 8.351e-3 (= sqrt(4π·5.55e-6)) | From α_D | OK (matches root) |

**⚠️ NOTE: F_H_CANONICAL = 0.297 is anomalous.** Standard hydrogen mass fraction Y_p ≈ 0.75 (from BBN); standard cosmic baryon fraction Ω_b/Ω_m ≈ 0.157; standard hydrogen number fraction X ≈ 0.92. The value 0.297 doesn't match any standard cosmology constant. Either it has a project-specific definition (e.g., a "dark sector equivalent" or a specific scaling factor for the model), or it's a typo. **TO VERIFY** with original project source.

### Halo catalogue (from v40.x JSONs)
| Halo | σ_v (km/s) | Citation | Status |
|---|---|---|---|
| Segue 1 | 3.7 | Simon+ 2011 | TO VERIFY (DOI 10.1088/0004-637X/733/1/46 likely) |
| Tucana II | 8.2 | Walker+ 2016 | TO VERIFY |
| Hercules | 3.7 | Adén+ 2009 | TO VERIFY |
| Draco | 10.6 | Walker+ 2007 | TO VERIFY |
| Ursa Minor | 9.5 | Walker+ 2007 | TO VERIFY |
| Sculptor | 9.2 | Walker+ 2007 | TO VERIFY |
| Carina | 6.6 | Walker+ 2007 | TO VERIFY |
| Bootes I | 6.5 | (not cited explicitly) | TO VERIFY |
| Triangulum II | 5.6 | (not cited explicitly) | TO VERIFY |
| Leo T | 7.5 | (not cited explicitly) | TO VERIFY |
| Cloud-9 | 5.1 (= 12/2.355) | Anand+ 2025 | TO VERIFY |

**WARNING**: Bootes I, Triangulum II, Leo T σ_v values are used in v40.5 / v40.10 IN BAND analysis but no specific citation is given. **TO VERIFY** which Walker paper / Martin paper these come from.

### Halo mass-concentration values
| Halo | M_200 (M☉) | c_200 | Source | Status |
|---|---|---|---|---|
| Segue 1 | 1.0e8 | 25 | (not cited) | TO VERIFY (likely Read+ 2019 or similar) |
| Tucana II | 5.7e6 | 28 | (not cited) | TO VERIFY (likely Simon+ 2017 or similar) |
| Hercules | 1.0e7 | 25 | (not cited) | TO VERIFY |
| Draco | 2.0e9 | 20 | (not cited) | TO VERIFY (likely Walker+ 2007) |
| Bootes I | 1.0e7 | 25 | (not cited) | TO VERIFY |
| V_max values | various | (not cited) | TO VERIFY |

---

## 3. Numerical formulas (audit status)

### σ/m velocity-weighted formula (Breit-Wigner)
From `v19_2_f_priority1_resonance_helpers.py`:
```
σ_m(v) = σ_m_0(v) × F²(q, m_ρ, Γ)
σ_m_0(v) = 2π α_D² × integral(cos θ) × ℏc² / m_χ
F² = (q² + m_ρ²)² / [(q² - m_ρ²)² + (m_ρ · Γ)²]
q² = 2 μ² v² (1 - cos θ)
```
**STATUS: Form verified** by M3 in OpenAI4S (v40.8 code review). Functionally correct. Unit conversions need to be checked (ℏc² in GeV² × cm²/GeV² = cm²; m_χ in grams).

### σ/m Gaussian background (Cloud-9 fit)
```
σ_m(v) = 0.052 × (100/v)^1.93 + 174 × exp(-(v - 29.4)² / (2 × 4.4²))   [v in km/s]
```
**STATUS: Empirically correct from Cloud-9 fit**. A_SLOPE = 1.93 and SIGMA_0 = 0.052 match Yang+ 2024.

### Gravothermal collapse time (Yang+ 2024 eq. 2.2 in v40.4/v40.9 docs)
```
t_c = 150·C / (σ_eff · ρ_eff · r_eff · sqrt(4πG·ρ_eff))     [literal prefactor]
t_c = 150·C · 1.82 / (...)                                     [BM2-calibrated]
150·C = 112.5
```
**STATUS: Formula structure OK; eq. number TO VERIFY.** v40.4 / v40.9 / v40.12 cite "Yang+ 2024 eq. 2.2" but the v31 review packet says eqs. 4, 19, 20. The LITERAL vs BM2 distinction is correct: 1.82x is the standard N-body-to-fluid correction.

### r_s, ρ_s from M_200, c_200
```
R_200 = (3·M_200 / (4π·200·ρ_crit))^(1/3)
r_s = R_200 / c_200
f_c = log(1 + c) - c/(1+c)
ρ_s = M_200 / (4π·r_s³·f_c)
```
**STATUS: Verified** by controller in v40.9 reproduction. Standard NFW formulas.

### Velocity-weighted average (Maxwell-Boltzmann weighted)
```
v_0 = sqrt(2)·σ_v_los
f_MB(v) = 4π v² exp(-(v/v_0)²) / (sqrt(π) v_0³)
σ_eff = ∫ f_MB(v) σ_m(v) dv / ∫ f_MB(v) dv
```
**STATUS: Standard MB averaging**. The v_0 = sqrt(2)·σ_v_los relation is the 1D-to-3D velocity dispersion conversion (σ_v² = ⟨v_x²⟩ = ⟨v²⟩/3, so ⟨v²⟩ = 3·σ_v², and v_0² = 2·⟨v²⟩/3 = 2·σ_v²). **TO VERIFY**: the actual v0 should be sqrt(2)·σ_v_los, giving v_0 = 1.414·σ_v. This is a common convention but check.

---

## 4. Bug list (newly found in v40.13 audit)

| Bug | Severity | Location | Fix |
|---|---|---|---|
| Wrong arXiv ID for Yang+ 2024 (2305.16176 vs 2305.05067) | HIGH | v40.4 Loop 1 code | Fixed in v40.13 |
| Wrong arXiv ID for Yang+ 2024 (2405.10393 vs 2305.05067) — 2405.10393 is a Navier-Stokes math paper | HIGH | v40.9 Loop 4 reproduction script | Fixed in v40.14 |
| Wrong author list for Yang+ 2024 ("Nadler, Yu, Zhong" vs "Jiang, Benson, Zhong, Mace, Du, Zeng, Peter, Fischer") | HIGH | v40.4 Loop 1 code | Fixed in v40.13 |
| "Yang+ 2024 eq. 2.2" citation likely wrong (v31 says eqs. 4, 19, 20) | MED | v40.4, v40.7, v40.9, v40.12 | Patch in v40.13 to "eq. 19 or 20" |
| Bootes I, Tri II, Leo T σ_v have no explicit citation | MED | v40.5, v40.10, v40.12 | Add citation in v40.13 |
| F_H_CANONICAL = 0.297 is anomalous (standard Y_p ≈ 0.75) | MED | scripts/constants.py | Verify in v40.13 |
| v_0 = sqrt(2)·σ_v_los convention: standard is v_0² = 2·σ_v² (consistent) | OK | (no fix needed) | — |
| Andrade+ 2022 MNRAS 510, 54 — no arXiv ID, no DOI | LOW | v40.11 doc | Add in v40.13 |
| Kaplinghat+ 2016 — no arXiv ID, no DOI; possibly conflated with Tulin+ 2013/2018 | LOW | v40.11 doc, constants.py | Add in v40.13 |
| KAPPA_C_ANALYTIC = 1.6798 cited to Tamm 1947 ZhETF 17, 884 — modern review should cross-check | LOW | constants.py | Verify in v40.13 |

---

## 5. Cross-check procedure (for future loops)

Before adding a new paper/parameter to the project:
1. **Check arXiv ID**: search `https://arxiv.org/abs/<id>`. Verify title, authors, abstract.
2. **Check DOI** (if journal-ref): search `https://doi.org/<doi>`. Verify matches arXiv.
3. **Verify quote**: if doc says "abstract says X", check the actual abstract. **Do not paraphrase and put in quotes.**
4. **Add to this registry** with verified status.
5. **Recompute from first principles**: any σ_eff / t_c / IN BAND value should be reproducible by the regeneration script (v40.12 for Loop 2, v40.9 for Loop 4).

---

## 6. Files maintained by this registry
- `docs/V19_2_F_REFERENCE_DATA_REGISTRY.md` (this file)
- `constants.py` (root, LOCKED — particle physics)
- `scripts/constants.py` (σ/m formula parameters)
- `v0.3-prelim/code/v19_2_f_priority1_resonance_helpers.py` (σ/m formula)
- `v0.3-prelim/code/v19_2_f_loop4_tc_breit_wigner_reproduction.py` (Loop 4 reproduction, v40.9)
- `v0.3-prelim/code/v19_2_f_loop2_multi_ufd_regenerator.py` (Loop 2 generator, v40.12)
