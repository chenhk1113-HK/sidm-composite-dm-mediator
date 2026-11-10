# v19.2-F Reference Data Registry

**Date:** 2026-10-19 (v40.44 update)
**Branch:** `wip/v19.2-F-init`
**Tag:** `v19.2-F-Phase3-CLOSED-r40.44` (current head)
**Purpose:** Authoritative list of every paper cited and every numerical value used by the v19.2-F project, with verification status. Cross-checked against arXiv/DOI as of 2026-10-19.

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
- **Chu, Hambye, Tytgat 2012** (M2 model, vector portal) — arXiv:1112.0493, JCAP 05, 034. "The Four Basic Ways of Creating Dark Matter Through a Portal." **STATUS: VERIFIED (v40.20)** — previously v40.13/v40.14 docs had wrong year (2018) and wrong arXiv (1712.02521, which is a microscopy paper). Correct attribution: 2012, 1112.0493. ~499 citations.
- **Tulin, Yu, Zurek 2013** (SIDM foundational review) — arXiv:1302.3898, PRD 87, 115007. "Beyond Collisionless Dark Matter: Particle Physics Dynamics for Dark Matter Halo Structure." **STATUS: VERIFIED (v40.20)** — previously v40.13/v40.14 had wrong arXiv (1306.5010, which is a comet paper). Correct attribution: 1302.3898.
- **Tulin & Yu 2018** (Phys. Rep. 730) — arXiv:1705.02358. Comprehensive SIDM review, 1100+ citations. **STATUS: VERIFIED (v40.20)** — abstract confirms small-scale structure issues, N-body simulations, particle physics models, light mediator.
- **Read+ 2019** (M_halo for Segue 1) — J. I. Read et al. 2019, MNRAS 484, 1401 (CORE-NFW profile). arXiv:1808.06634. **STATUS: VERIFIED (v40.20)** — abstract confirms ρDM(150 pc) = 10^8 M☉ kpc−3 dichotomy threshold.
- **Andrade+ 2022** — MNRAS 510, 54. "Stringent upper limit on dark matter self-interaction cross-section." arXiv:2012.06611. **STATUS: VERIFIED (v40.20)** — abstract gives σ/m = 0.082+0.027/-0.021 cm²/g at v_rel = 1458+80/-81 km/s, 8 clusters analyzed.
- **Benítez-Llambay, Navarro 2023** (Cloud-9 precursor) — arXiv:2309.03253, ApJ 956, 1. **STATUS: VERIFIED (v40.20)** — abstract gives M_200 ~ 5×10^9 M☉, c_NFW ~ 13, d ~ 4.7 Mpc, v ~ 300 km/s.
- **Anand+ 2025** (Cloud-9 discovery) — arXiv:2508.20157, ApJL 993, L55. **STATUS: VERIFIED (v40.20)** — abstract confirms W_50 = 12 km/s, HI mass ~ 10^6 M☉, d ~ 4.4 Mpc, "leading RELHIC candidate".
- **Ohana, Zhang & Yu 2026** (Cloud-9 CDM/SIDM interpretation — **the paper the project's whole c-M tension investigation is measured against**) — arXiv:2608.04362, "Cold Dark Matter and Self-Interacting Dark Matter Interpretations of Cloud-9". **STATUS: VERIFIED (v40.61)** — full PDF downloaded to `docs/papers/verified/2608.04362_ohana_2026_cloud9_cdm_sidm.pdf` (2,654,775 B, 10 pp) and read; summary at `docs/papers/verified/2608.04362_ohana_2026_cloud9_cdm_sidm.md`. Live arXiv API query confirms title/authors/date. **Key values from the paper body:** CDM (NFW) best-fit concentration **7σ below** the cosmological c-M relation (posterior peak 7.3σ; still >6.7σ allowing for fit uncertainty); SIDM marginalized posterior peak **3.3σ** below the cosmological median; at fixed σ/m = 50 cm²/g, **~3σ**; deviation minimised at **~3σ** for σ/m ≈ 200 cm²/g. **The "3.2σ" quoted by the project** is the §3.1 value for the **SIDM τ = 0.18 best-fit** (M_200 = 4.7×10⁹ M☉, c_200 = 4.0, scatter 0.16 dex per Diemer+ 2019), with **σ/m = 483 cm²/g** via Eq. 8 — this matches the project's `scripts/ohana2026_cloud9_joint_likelihood.py` fiducial exactly (no citation drift). **Caveats:** the 3.2σ is τ- and model-dependent; the 0.16 dex scatter assumption is load-bearing (σ scales as log(c_dev)/0.16); the fit **loses c_200 sensitivity** once the core envelops the data, so the concentration is constrained only via the cosmological prior. **NOT an "upper limit"** — it is a posterior inference of the concentration deviation.
- **Walker+ 2016** (Tucana II) — arXiv:1511.06296, ApJ 819, 53. **STATUS: VERIFIED (v40.20)** — abstract gives σ_v = 8.6+4.4/-2.7 km/s (v19.2-F previously had 8.2, corrected in v40.20).
- **Adén+ 2009** (Hercules) — arXiv:0910.1348, ApJL 706, L150. **STATUS: VERIFIED (v40.20)** — abstract gives σ_v = 3.72 km/s (v19.2-F uses 3.7, close enough).

### External SIDM literature (LOOP3)
- **Gilman+ 2023** — D. Gilman, J. Zhong, J. Bovy (2023). "Constraining resonant dark matter self-interactions with strong gravitational lenses." arXiv:2207.13111. PRD 107, 103008. **STATUS: VERIFIED** (arXiv 2207.13111 retrieved 2026-10-17; title and abstract quote match).
- **O'Donnell+ 2025** — "A Constraint on Dark Matter Self-Interaction from Combined Strong Lensing and Stellar Kinematics in MACS J0138-2155." arXiv:2508.20179. **STATUS: VERIFIED** (arXiv 2508.20179 retrieved; accepted in PRD; abstract gives σ/m < 0.613 cm²/g at ⟨v_pair⟩ < 2090 km/s).
- **Horigome+ 2025** (NEW v40.24) — S. Ando, S. Horigome, et al. 2025. "Stringent Constraints on Self-Interacting Dark Matter Using Milky-Way Satellite Galaxies Kinematics." arXiv:2503.13650. **STATUS: VERIFIED** (arXiv 2503.13650 retrieved 2026-10-17). Key limits: 0.8 cm²/g (w=10 km/s velocity-dep), 0.04 cm²/g (w→∞ velocity-indep). **CRITICAL:** defines the dSph σ/m upper limit that v19.2-F violates by 3.6-23.7× at v_eff=5-20 km/s.
- **Sánchez Almeida+ 2025** — "Constraints on dark matter models from the stellar cores observed in ultra-faint dwarf galaxies: Self-interacting dark matter." arXiv:2510.05682. A&A 704, A210 (2025). DOI: 10.1051/0004-6361/202557040. **STATUS: VERIFIED**.
- **Jee, Park, Lee 2026** — "A New Robust Constraint on the Self-interaction Cross-section of Dark Matter with Double Radio Relic Clusters." arXiv:2605.00093. Accepted ApJ. **STATUS: VERIFIED** (PDF read; abstract gives σ/m < 0.22 cm²/g at 68% CL, σ/m < 0.63 at 95% CL).
- **Andrade+ 2022** — MNRAS 510, 54. "Stringent upper limit on dark matter self-interaction cross-section" (149 citations per v40.11 doc). **STATUS: TO VERIFY** (no arXiv ID in v40.11 doc; need full citation).
- **SASHIMI-SIDM (Ando+ 2024)** — arXiv:2403.16633, JCAP02(2025)053. "Semi-analytical subhalo modelling for self-interacting dark matter at sub-galactic scales." GitHub: shinichiroando/sashimi-si. **STATUS: TO VERIFY (v40.16 added)** — relevance LOW for current v40.x (no substructure analysis); MEDIUM if scope expands to streams/JVAS/substructure.
- **parametricSIDM (Yang et al.)** — github.com/DanengYang/parametricSIDM, accompanying arXiv:2305.16176. "A Parametric Model for SIDM Halos." **STATUS: VERIFIED 2026-10-27 (SUPERSEDES the earlier "NOT TO DOWNLOAD" marking, which was WRONG).** The PDF was downloaded and read: it is confirmed to be the paper the code implements — eq. (2.1) density profile (beta=4), eq. (2.2) collapse time (150 prefactor, C=0.75), eq. (2.3) parameter evolution, eq. (2.4) Vmax/Rmax, the BM2 calibration (t_c = 28.7 Gyr at sigma_eff/m = 7.1 cm2/g), and Cosmo-501 from Table 1. It is cited in the draft as **[43]** and is DISTINCT from arXiv:2305.05067 ([17], the gravothermal-vs-isothermal sigma/m(v) fit). See registry §7.10.

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
| F_H_CANONICAL | 0.7501856343179664 | phase44_two_component.f_H_at_r(0.05, core-forming) — **LIVE PAIR** | **RESOLVED 2026-11-06 (finding F26)**; consistent with the standard hydrogen mass fraction Y_p ~ 0.75. The 0.297 was the v18.29-retracted placeholder and is archived as `F_H_LEGACY_PLACEHOLDER_0297` |
| SIGMA_0_CM2_PER_G | 0.008150396851725193 | = 0.052 x 0.15673840099471523 — **LIVE PAIR** (finding F26) | OK (project internal); the archived-pair value 0.052 is kept as `SIGMA_0_LEGACY_PAIR_052` |
| SIGMA_PEAK_CM2_PER_G | 27.272481773080454 | = 174.0 x 0.15673840099471523 — **LIVE PAIR** (finding F26) | OK (project internal); the archived-pair value 174.0 is kept as `SIGMA_PEAK_LEGACY_PAIR_174` |
| G_CHI | 8.351e-3 (= sqrt(4π·5.55e-6)) | From α_D | OK (matches root) |

**PAIRING NOTE (RESOLVED 2026-11-06, findings F25/F26/F28; owner decision "call 1 repair").** `f_H` is exactly
degenerate with the fitted amplitudes: `sigma_eff = f_H^2 x sigma/m` is unchanged when `f_H` and both amplitudes
are rescaled together, so the three numbers above are one atomic pair and must never be mixed across pairs.
`PAIRING_K_LEGACY_TO_CANONICAL = 0.15673840099471523 = 0.297^2 / 0.7501856343179664^2`, inverse
`6.380057431067687`. The live pair is `f_H = 0.7501856343179664` with `sigma_0 = 0.008150396851725193` and
`sigma_peak = 27.272481773080454 cm^2/g`; the archived pair is `0.297 / 0.052 / 174.0`. Halo-level predictions
(`sigma_eff`) are identical between the pairs to 1.9e-16; what the choice decides is which number is the
**particle-level** cross section, and the `174 cm^2/g` causality-cap narrative belongs to the archived pair.
`scripts/constants.py` asserts the pair at import, `scripts/fH_pairing_registry.py` publishes which pairing every
module uses (`v0.3-prelim/data/results/fH_pairing_registry.json`), and an archived value may only appear in a
module under an archived-looking name. Earlier text in this registry that quotes `0.052` or `174.0` is
archived-pair raw amplitude, not the live pair.

### Halo catalogue (from v40.x JSONs)
| Halo | σ_v (km/s) | Citation | Status |
|---|---|---|---|
| Segue 1 | 3.7 | Simon+ 2011 (ApJ 733, 46, arXiv:1007.4198) | **VERIFIED (v40.20)** — paper abstract gives "3.7+1.4/-1.1 km/s" |
| Tucana II | **8.6** (was 8.2) | Walker+ 2016 (ApJ 819, 53, arXiv:1511.06296) | **VERIFIED (v40.20)** — paper abstract gives "8.6+4.4/-2.7 km/s"; v40.20 corrected numerical slip |
| Hercules | 3.7 (= 3.72) | Adén+ 2009 (ApJL 706, L150, arXiv:0910.1348) | **VERIFIED (v40.20)** — paper ADS gives "3.72 km/s"; KB had wrong "no arXiv" claim |
| Draco | 10.6 | Walker 2012 (Living Review) — NOT Walker+ 2007 (ApJL 667, L53) | **BUG (v40.15)**: v40.5 doc said "Walker+ 2007" but that paper covers Carina, Fornax, Sculptor, Sextans — NOT Draco |
| Ursa Minor | 9.5 | Walker 2012 (Living Review) — NOT Walker+ 2007 (ApJL 667, L53) | **BUG (v40.15)**: same as Draco |
| Sculptor | 9.2 | Walker+ 2007 (ApJL 667, L53) | OK |
| Carina | 6.6 | Walker+ 2007 (ApJL 667, L53) | OK |
| Bootes I | 6.5 | Koposov+ 2011 (ApJ 736, 146) | TO VERIFY |
| Triangulum II | 5.6 | Kirby+ 2017 (ApJ 838, 50) | TO VERIFY (may have binary contamination) |
| Leo T | 7.5 | Ryan-Weber+ 2008 (ApJ 678, 833) — HI gas + stellar | TO VERIFY |
| Cloud-9 | 5.1 (= 12/2.355) | Anand+ 2025 (ApJL 993, L55, arXiv:2508.20157) | TO VERIFY |

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
σ_m(v) = 0.052 × (100/v)^1.93 + 174 × exp(-(v - 29.4)² / (2 × 4.4²))   [v in km/s]   # ARCHIVED PAIR (f_H = 0.297)
```
**STATUS: Empirically correct from Cloud-9 fit**, and it is the **archived pair**: A_SLOPE = 1.93 with
`sigma_0 = 0.052` and `sigma_peak = 174` (matching Yang+ 2024) pair with `f_H = 0.297`. The live pair
(finding F26) writes the same curve as `0.008150396851725193 × (100/v)^1.93 + 27.272481773080454 × exp(...)`
with `f_H = 0.7501856343179664`, and gives the same `sigma_eff`.

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
| Cloud-9 NFW v_max: ~10 km/s (claim) vs ~36 km/s (actual) | HIGH | docs/CLOUD9_REBASELINE.md, docs/papers/concepts/Cloud-9 Galaxy.md | **Fixed in v40.21** with full derivation (M=5e9, c=15, R_200=28 kpc, r_s=1.85 kpc gives v_max=~36 km/s). The "~10 km/s" was an error; the gas W_50=12 km/s is the gas line width (T~2×10⁴ K), not the DM V_max. Nemotron 120B confirmed. |
| Bootes I, Tri II, Leo T σ_v have no explicit citation | MED | v40.5, v40.10, v40.12 | Add citation in v40.13 |
| F_H_CANONICAL = 0.297 in scripts/constants.py | SUPERSEDED 2026-11-06 (finding F26): 0.297 is now `F_H_LEGACY_PLACEHOLDER_0297`, archived; the live value is `F_H_CANONICAL = 0.7501856343179664` | verified | This is a **project-internal phenomenological fit** (Phase G7), not the standard cosmological Y_p ≈ 0.75. The docstring says: "σ_eff = f_H² × σ/m with f_H=0.297" (0.297 is the archived pair; the quoted docstring predates finding F26 and is reproduced verbatim) (paper §2.6 "σ_eff formula (R88)"). The discrepancy with Y_p is because they're different quantities: F_H is an empirical f_H that modulates σ_eff vs σ_HH, not a BBN mass fraction. R88(88) caveat: project's own N-body Phase G9 found f_H drop 0.94-1.01×, a flat f_H(r). |
| v_0 = sqrt(2)·σ_v_los convention: standard is v_0² = 2·σ_v² (consistent) | OK | (no fix needed) | — |
| Andrade+ 2022 MNRAS 510, 54 — no arXiv ID, no DOI | LOW | v40.11 doc | Add in v40.13 |
| Kaplinghat+ 2016 — no arXiv ID, no DOI; possibly conflated with Tulin+ 2013/2018 | LOW (v40.15) | v40.11 doc, constants.py | VERIFIED: Kaplinghat, Tulin, Yu 2016 is PRL 116, 041302, arXiv:1508.03339 ("Dark Matter Halos as Particle Colliders"). 797 citations (close to v40.11's "~600" claim, off by 200). The other key review is Tulin & Yu 2018, Phys. Rep. 730, 1-57, arXiv:1705.02358 (1100+ citations, already downloaded). Both references are real and worth citing; the v40.11 doc's "~600 citations" should be updated to ~800 for the PRL or to ~1100 for the Phys. Rep. |
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

---

## 7. v40.44 update — 4 new papers added (2026-10-19)

Per user directive ("I want you to do it auto, no need for my reminder"), all papers used in v40.39-v40.44 are now saved locally with .md summaries.

### 7.1 Elbert+ 2015 — Core formation in dwarf haloes with SIDM
- **arXiv:** 1412.1477v1
- **Authors:** O. D. Elbert, J. S. Bullock, S. Garrison-Kimmel, M. Rocha, J. Oñorbe, A. H. G. Peter
- **Year:** 2015 (MNRAS 453, 29)
- **Local PDF:** `docs/papers/verified/1412.1477_elbert_2015.pdf` (6.2 MB)
- **Local .md:** `docs/papers/verified/1412.1477_elbert_2015.md`
- **STATUS: VERIFIED 2026-10-19**
- **Key findings:** σ/m ∈ [0.5, 50] cm²/g alleviates TBTF, largest cores at σ/m = 5-10, mild core-collapse at σ/m = 50
- **Used in v40.42:** c-τ prescription (c_200 decreases, slope=0.10, floor=50% NFW)

### 7.2 Sameie+ 2020 — Self-Interacting Dark Matter Subhalos in the Milky Way's Tides
- **arXiv:** 1904.07872v2
- **Authors:** Omid Sameie, Hai-Bo Yu, Laura V. Sales, Mark Vogelsberger, Jesús Zavala
- **Year:** 2020 (Physical Review Letters 124, 141102)
- **Local PDF:** `docs/papers/verified/1904.07872_sameie_2020.pdf` (490 KB)
- **Local .md:** `docs/papers/verified/1904.07872_sameie_2020.md`
- **STATUS: VERIFIED 2026-10-19**
- **Key findings:** σ/m = 3 cm²/g fits diverse rotation curves, σ/m > 5 cm²/g triggers core collapse (c_200 INCREASES)
- **Used in v40.43a:** 3rd c-τ prescription (c_200 INCREASES, slope=+0.40, ceiling=2x NFW)

### 7.3 Silverman+ 2026 — Mergers Matter: Gravothermal Collapse in Dwarf Halos with SIDM
- **arXiv:** 2606.02566v1
- **Authors:** Maya Silverman, Abdelaziz Hussein, Arpit Arora, Mariangela Lisanti, Manoj Kaplinghat, Lina Necib, Andreas Thoyas, Stephanie O'Neil, Robyn E. Sanderson, Xuejian Shen, Jorge Moreno
- **Year:** 2026 (FERMILAB-PUB-26-0348-T, June 2026)
- **Local PDF:** `docs/papers/verified/2606.02566_silverman_2026.pdf` (1.0 MB)
- **Local .md:** `docs/papers/verified/2606.02566_silverman_2026.md`
- **STATUS: VERIFIED 2026-10-19**
- **Key findings:** 100% collapse fraction among quiescent halos (3/3), 0% among sustained (0/3); 1:3 merger caused ρ_c drop by factor 8.7
- **Used in v40.44:** merger history analysis (Cloud-9 QUIESCENT → collapse expected)

### 7.4 Anand+ 2025 — The First RELHIC? Cloud-9 is a Starless Gas Cloud
- **arXiv:** 2508.20157v2
- **Authors:** Gagandeep S. Anand, Alejandro Benítez-Llambay, Rachael Beaton, Andrew J. Fox, Julio F. Navarro, Elena D'Onghia
- **Year:** 2025 (in press at ApJL)
- **Local PDF:** `docs/papers/verified/2508.20157_anand_2025.pdf` (15.4 MB)
- **Local .md:** `docs/papers/verified/2508.20157_anand_2025.md`
- **STATUS: VERIFIED 2026-10-19**
- **Key findings:** Cloud-9 is compact H I cloud in M94 group (d=4.4 Mpc), non-rotating, W50=12 km/s, RELHIC candidate
- **Used in v40.44:** Cloud-9 morphology (compact, non-rotating, dynamically cold → QUIESCENT merger history inference)
- **CORRECTION:** Earlier v19.2-F notes referenced NGC 1023 as Cloud-9's host. Correct host is M94 (NGC 4736). Some scripts/notes may need updating.

### 7.5 Burkert 1995 (still no local PDF — and the 2026-10-19 status line was stale)
- **Burkert 1995** — "The Structure of Dark Matter Halos in Dwarf Galaxies", ApJ **447** (1995), DOI **10.1086/309560** (Crossref, verified 2026-11-09) — cored dark matter profile, foundational
- **STATUS: TO ADD LOCAL PDF (no arXiv preprint exists — verified: `astro-ph/9508181` is not an arXiv record)** — journal/IOP access required
- **CORRECTION (2026-11-09, registry §7.11 D4):** this line previously said "cited but no local PDF". The `PAPER_V1_DRAFT.md` reference list contained **no Burkert entry at all** at the time of writing (43 entries then; 48 now), so the paper did not cite Burkert 1995. Refinement of the "all 26 body mentions are quoted reviewer text" claim: the draft's own §2.6d anchors "Prescription B: Burkert-style" to "Burkert 1995 (ApJ 447, L25) cored profile" in the framework's own voice — a named work with volume and page but no reference entry. **Closed on 2026-11-09: slot [47] added and cited in §2.6d.**
- **Reading stand-in:** `docs/papers/verified/9703057_burkert_1997.pdf` (Burkert 1997 review, "The structure of dark matter halos. Observation versus theory") is in the KB for background only — it is a different paper and must not be cited as the 1995 profile paper.
- **Used in v40.43:** Burkert-style c-τ prescription (placeholder anchored to Burkert 1995 + Balberg 2002)

### 7.6 Citation count update
- **Total verified papers in registry: 9** (5 from v40.14 + 4 new in v40.44)
- **Local PDFs in docs/papers/verified/: 14 PDFs** (10 from prior + 4 new in v40.44)
- **Pending local PDFs: 1** (Burkert 1995 — not on arXiv, journal only)

### 7.7 Reference [10] does NOT resolve — Girmohanta & Yasuoka (2026-10-26, external evaluation)

**VERDICT: the reference as printed cannot be found. Do not cite it as-is.**

Paper L2015 prints: `[10] S. Girmohanta, Y. Yasuoka, Phys. Rev. D 111, 035005 (2025).`

**What the DOI actually resolves to.** Crossref `10.1103/physrevd.111.035005` →
*"Theoretical bounds on dark Higgs mass in a self-interacting dark matter model with
U(1)′"*, **Li, Yang, Zhang, Zhu** — a different paper, different authors.

**And no Girmohanta & Yasuoka co-authored paper exists:**

| check | result |
|---|---|
| arXiv full-text `all:Girmohanta AND all:Yasuoka` | **0 entries** |
| Crossref author-pair search (both authors required) | no PRD paper |
| arXiv's own Girmohanta listing (20 most recent, 2022-2026) | **no Yasuoka co-author**; his SIDM papers are with **Shrock** (PRD 106, 063013 (2022); PRD 107, 063006 (2023)) |

**Impact:** [10] is cited twice in the body — L38 (geometric mass-ladder constructions)
and L90 (a "dark-photon model ... different UV-completion story"). Both claims are
load-bearing for the paper's positioning.

**Same shape as the v40.4 citation-drift bug** (arXiv:2305.16176 cited instead of
2305.05067). The check was already flagged in `v0.3-prelim/docs/AUDIT_REFERENCES.md`
("Authors may not exist; PRD 111, 035005 should be checked against PRD table of
contents") and **never completed**.

**Action needed — a user decision, not an auto-fix.** Two possibilities, and the two
lead to different outcomes:
1. The intended source is a **Girmohanta & Shrock** SIDM paper (two exist, listed above)
   → re-point [10] and rewrite the two body sentences to match what that paper says.
2. The reference was **fabricated** → cut [10] and rewrite L38 and L90 without it.

**Until then [10] must not be cited.** Do not "fix" it by guessing which of the two it is.

**Metadata retrieval path (verified live 2026-10-26, no new dependency):**
`https://export.arxiv.org/api/query?id_list=<ids>` → authors, title, date, DOI,
`arxiv:journal_ref` · `https://api.crossref.org/works/<doi>` → journal, volume, page, year.
This same path is what the 32 `[NEEDS CITATION]` entries need — see
`docs/papers/to_verify/zotero_developer_api.md`.

---

## 7.9 KB COMPLIANCE ROUND — option-2 body-leaning set (2026-10-27)

**The gap this closes.** §8's rule is *"NEVER cite a paper without local PDF + .md summary + registry
entry."* An audit of the 41 cited reference slots found only **5** compliant:
[15e] Ohana+ 2026, [27] Horigome+ 2025, [54] Silverman+ 2026, [54c] Sameie+ 2020, [55a] Elbert+ 2015.
Three more ([1]/[50d] Kaplinghat+ 2016, [9] Girmohanta & Shrock 2022, [10] Girmohanta & Shrock 2023)
had a registry entry but **no PDF and no summary**. The remaining 33 slots were absent entirely.

**Scope agreed with the user:** option 2 — add the papers the PAPER BODY actually leans on (the ones
carrying numbers), not all 41. 14 papers were downloaded and summarised, plus a long-standing
missing slot.

### Newly added (PDF + .md now in `docs/papers/verified/`)

| Slot(s) | arXiv | Paper | Why it is body-leaning |
|---|---|---|---|
| [23] | 2510.11006 | Yu, "Three Birds with One Stone: Core-Collapsed SIDM Halos…" | 12 numeric citations — the most heavily used numerical reference in the draft |
| [1], [50d] | 1508.03339 | Kaplinghat, Tulin & Yu, "Dark Matter Halos as Particle Colliders" | the founding velocity-dependent SIDM result (σ/m ≈ 2 → 0.1 cm²/g) |
| [5] | 1005.4678 | Feng, Kaplinghat & Yu, "Sommerfeld Enhancements for Thermal Relic Dark Matter" | the Yukawa-suppression mechanism the draft's background term rests on |
| [7], [28] | 1810.04709 | Chu, Garcia-Cely & Murayama, "Velocity Dependence from Resonant SIDM" | the resonance mechanism; corrected authors/year |
| [1a], [15b] | 2406.18643 | Benítez-Llambay+ 2024, Cloud-9 VLA | Cloud-9's observational state (W50 ≈ 12 km/s, M200 ≈ 5×10⁹ M☉) |
| [9] | 2206.14395 | Girmohanta & Shrock 2022 | source of the revised "mass-dependent u-channel" claim |
| [10] | 2210.01132 | Girmohanta & Shrock 2023 | the dwarf-to-cluster fit the draft compares itself against |
| [55b] | 2609.16740 | Lei+ 2026 | inner-DM deficit channel, 100–300 km/s |
| [55c] | 2609.19132 | Wang+ 2026 | independent inner-DM deficit channel |
| [52] | 2601.17118 | Jia+ 2026 | the independent SPARC isothermal-Jeans framework |
| [3] | 1103.0007 | Boylan-Kolchin, Bullock & Kaplinghat, "Too big to fail?" | the TBTF problem the draft opens with |
| [8] | 1804.10385 | Duerr, Schmidt-Hoberg & Wild | the stable-vector-mediator mechanism |
| [51] | 2503.10748 | Nadler+ 2025, SIDM Concerto | establishes the draft is NOT a single-component re-parameterisation |
| [49] | 2601.23264 | Engelhardt+ 2026, MARVELously Dark | independent N-body check on the Yukawa background |

Downloaded by `docs/papers/fetch_cited_papers.sh` (idempotent; asserts it landed in the project root).

### NEW DEFECT FOUND — "Yang+ 2024" is TWO different papers

The body uses the shorthand **"Yang+ 2024" 29 times** for two distinct works:

- **[17]** (NEW slot) — arXiv:**2305.05067**, Yang, Jiang, Benson, Zhong, Mace, Du, Zeng, Peter &
  Fischer, MNRAS **533**, 4007 (2024), *"A quantitative comparison between velocity dependent SIDM
  cross sections constrained by the gravothermal and isothermal models."* Previously cited by name
  with **no reference slot at all**.
- **[43]** — arXiv:**2305.16176**, Yang, Nadler, Yu & Zhong, *"A parametric model for self-interacting
  dark matter halos,"* JCAP **02** (2024) 032. Its entry previously carried **no arXiv ID**.

This is the **same confusion the registry already records as a v40.4 bug** (wrong arXiv ID
2305.16176 vs 2305.05067, HIGH severity, fixed in v40.13). It has recurred, now as an unresolved
shorthand rather than a wrong ID. A disambiguation note has been placed in the draft at the first
mention; **the 29 sites have NOT been resolved individually.**

**Status of [43]:** the registry's §1 entry for parametricSIDM marks 2305.16176 **"NOT TO DOWNLOAD"**
(it needs re-validation), yet the draft cites it as [43] and the code implements its model in
`v40.7`-lineage work (`gravothermal_yang2024.py`). **This contradiction is unresolved:** either the
paper gets downloaded and validated, or the citation and the code's attribution both change.

### Still NOT in the KB (deliberately out of option-2 scope)

- The remaining ~19 purely-citational slots ([2], [4], [6], [14], [15a], [15c], [15d], [16], [25],
  [26a], [42], [43], [45], [50], [50c], [54c]*, [55a]*, [11], [12]) — * where already complete.
- **[42]** has an incomplete entry: *"Phys. Rev. D (2025)"* with no volume, page or arXiv ID.
- **[11]** and **[12]** remain unresolvable (see §7.8).
- **Balberg+ 2002** (11 body mentions) and **Fischer & Yu 2026** (9 mentions) are named in the body
  with **no reference slot at all** — same class of defect as the old Yang+ 2024 case.

## 7.10 USER-DIRECTED CITATION FIX ROUND (2026-10-27)

The user reviewed a 9-item outstanding-issues list and decided: **fix [16] and [14];
remove [11] and [12]; download and validate [43]; go through the "Yang+ 2024" sites;
find Balberg+/Fischer & Yu; run option 1; deliver last.**

### Four MORE citation defects found and fixed (each verified against the live record)

| Slot | Printed | Verified | Fix |
|---|---|---|---|
| [16] | "S. Vegetti, O. Czoske, L. V. E. Koopmans, *Globular Clusters as the First High-Mass Star Clusters of Dwarf Galaxies*, MNRAS 408, 430 (2010)" | Vegetti, Koopmans, Bolton, Treu & Gavazzi, *"Detection of a dark substructure through gravitational imaging"*, MNRAS 408, **1969** (2010), arXiv:0910.0760, doi 10.1111/j.1365-2966.2010.16865.x | Czoske is not an author; the title is a different paper's; page 430 is wrong. **The body use (JVAS B1938+666 perturber) was already correct** — only the entry needed re-pointing. |
| [14] | "The SPARC Dataset: A Comprehensive and High-Precision Sample of Galaxy Rotation Curves," AJ 152, **3 (2020)** | *"SPARC: Mass Models for 175 Disk Galaxies with Spitzer Photometry and Accurate Rotation Curves"*, AJ 152, **157 (2016)**, arXiv:1606.09251, doi 10.3847/0004-6256/152/6/157 | Page, year and title corrected. |
| [6] | arXiv:**1308.0009** | arXiv:**1302.3898** | 1308.0009 is *Kipping, "Efficient, uninformative sampling of limb darkening"* — a different paper. 1302.3898 was already in the local KB. |
| [15d] | Res. Notes AAS (**2024**) | Res. Notes AAS **10, 247 (2026)**, arXiv:2608.20911, doi 10.3847/2515-5172/ae9cb8 | Year wrong; volume/page/arXiv/DOI added. |

Also completed: **[42]** (was "Phys. Rev. D (2025)" with no volume, page or arXiv ID →
PRD 112, 083502 (2025), arXiv:2504.02303, doi 10.1103/9952-qf5l); **[15c]** (DOI added);
**[15a]** (arXiv:2306.05080 added); **[2]** (arXiv:1504.01437 added); **[4]** (arXiv:0704.0261 added).

### [11] and [12] REMOVED

No paper matching either description exists in arXiv, InspireHEP, Crossref, Semantic
Scholar or OpenAlex. Both reference entries were **deleted** and the L90 sentence was
**rewritten to drop the citations AND the claims they supported**, keeping the verified
[13] and [10] clauses. Neither slot appeared anywhere else in the body.

### TWO new slots added for papers named in the body with NO reference entry

- **[18]** S. Balberg, S. L. Shapiro, S. Inagaki, *"Self-Interacting Dark Matter Halos and the
  Gravothermal Catastrophe"*, ApJ 568, 475 (2002), arXiv:astro-ph/0110561 — named **11 times**
  in the body (companion PRL 88, 101301, arXiv:astro-ph/0111176 noted).
- **[19]** M. S. Fischer, H.-B. Yu, *"The dark fate of ultra-faint dwarfs: Gravothermal collapse in
  action"*, arXiv:2603.04508 (2026), doi 10.1051/0004-6361/202659748 — named **9 times**.

All 11 and all 9 body mentions now carry the slot number.

### "Yang+ 2024" RESOLVED SITE BY SITE — 34 occurrences

Both papers were downloaded and read before classifying:

- **[43] arXiv:2305.16176** *"A Parametric Model for Self-Interacting Dark Matter Halos"* — the
  paper the code implements. Confirmed from the PDF: eq. (2.1) density profile with **beta = 4**;
  eq. (2.2) collapse time with the **150** prefactor and **C = 0.75**; eq. (2.3) parameter
  evolution; eq. (2.4) Vmax/Rmax evolution; **BM2** calibration (t_c = 28.7 Gyr at
  sigma_eff/m = 7.1 cm2/g); **Cosmo-501** from Table 1; Fig. 2; sigma0/m = **147.1** cm2/g with
  **w = 24.33** km/s. **28 occurrences → [43].**
- **[17] arXiv:2305.05067** *"A quantitative comparison between velocity dependent SIDM cross
  sections constrained by the gravothermal and isothermal models"* — the **velocity-dependent
  sigma/m(v) fit** (double power law, Eq. 19-21) and the SPARC+BCG cross-section constraints.
  **1 occurrence → [17]**: the L476 line introducing the canonical sigma/m(v) form.

**The registry's earlier marking of 2305.16176 as "NOT TO DOWNLOAD" was WRONG and is
superseded.** The code's attribution was correct all along: `gravothermal_yang2024.py`
implements eq. 2.1-2.4, the BM2 calibration and the Cosmo-501 test from 2305.16176, and the
PDF confirms every one of those. The v40.4 "bug" was a *different* mistake (the wrong arXiv
ID attached to a gravothermal-model claim), not evidence that this paper is irrelevant.

### Option 1 executed — every cited paper now has a local PDF

`docs/papers/fetch_all_cited_papers.sh` (new; supersedes the option-2
`fetch_cited_papers.sh`) downloads the **full 42-slot bibliography**. PDFs are gitignored
(local-only, re-downloadable); the `.md` summaries are tracked in git.

**Standing note on the KB rule:** the summaries are the tracked artefact. A summary must state
the paper's KEY NUMBERS and how v19.2-F uses it — a title-only stub does not satisfy §8.

## 8. Standing rule for future sessions (locked 2026-10-19)

Per user directive "I want you to do it auto, no need for my reminder":

**AUTO-SAVE rule:** Every time a paper is used in v19.2-F analysis (via web_extract, web_search, or direct citation), IMMEDIATELY:
1. Download the PDF to `docs/papers/verified/<arxiv_id>_<author>_<year>.pdf` (or to `<journal>_<author>_<year>.pdf` for non-arXiv papers)
2. Write a `.md` summary to `docs/papers/verified/<arxiv_id>_<author>_<year>.md` with: arXiv ID, authors, year, local PDF path, key findings, how v19.2-F uses it, key numbers
3. Update this registry with the new paper entry
4. Commit the docs update as part of the v40.x release

**NEVER cite a paper without local PDF + .md summary + registry entry.** This rule is per R88(68) lesson (M3 has fabricated arXiv IDs in the past) and the project knowledge base rule (always refer to KB before citing).


**ADJUDICATED 2026-10-27:** reference [10] was fabricated ("Girmohanta & Yasuoka, PRD 111, 035005 (2025)"; the DOI belongs to Li, Yang, Zhang & Zhu). Reference [9] ("Hong, Kuranchi & Perez 2020") was likewise garbled. A user lead pointing at a "kuranchi" in a fuzzy-dark-matter context was checked against the primary record: the researcher is real — **Shalini Kurinchi-Vendhan** (Caltech; advisor Xiaolong Du), "Spherical Collapse of Fuzzy Dark Matter in 3-D Simulations", **BAAS 54, 347 (2022)**, plus a *Caltech Undergraduate Research Journal* article (2022) — but the lead cannot be [9] for two independent reasons: the work is *fuzzy* DM (ultralight soliton/halo-collapse structure), which has no SIDM cross-section content, and it is published only as a **BAAS meeting abstract** and a student-journal article, with no DOI, no arXiv record and no author entry in INSPIRE, Crossref, Semantic Scholar or OpenAlex. (Spelling note: **Kurinchi-Vendhan**, i after r — the widely copied "Kuranchi-Bendin" is a search-engine garble, and searching the garbled form returns nothing, which is why the name looked nonexistent.) Both slots are now re-pointed to the verified Girmohanta & Shrock papers: [9] = PRD 106, 063013 (2022), arXiv:2206.14395; [10] = PRD 107, 063006 (2023), arXiv:2210.01132. Body sentences L38 and L90 were rewritten to match what those papers actually claim.


## 7.8 REFERENCE-RESOLUTION ROUND (2026-10-27)

`scripts/resolve_references.py` (stdlib-only; arXiv + Crossref; no new dependencies) resolved the paper's blank reference slots. **36 of 38 slots now carry a publisher-verified entry.** Two slots were fabricated and are re-pointed: [10] ("Girmohanta & Yasuoka, PRD 111, 035005 (2025)" — the DOI belongs to Li, Yang, Zhang & Zhu) and [9] ("Hong, Kuranchi & Perez 2020" — no author named Kuranchi exists in arXiv, InspireHEP, Crossref, Semantic Scholar or OpenAlex; the real paper is Hong, **Kurup** & **Perelstein**). Both now cite verified Girmohanta & Shrock papers, and body sentences L38 and L90 were rewritten to match their claims. Six further body-level attribution errors were found and corrected ([5] venue, [7] authors, [50c] authors, [55a] 6th author, [13]/[30] year). Two slots — [11] ("Yang & Yu 2023") and [12] ("Turner et al. 2021") — remain unresolved because no candidate passed the author+venue+title agreement check; they are tracked as open items, not filled with substitutes. The evidence for both is recorded in `v0.3-prelim/docs/AUDIT_REFERENCES.md`; the closest real atomic-DM papers (Kaplan+ 2010 JCAP; Geller & Telem 2021 PRD 104 035010) and the closest real Yang–Yu work (PRD 104, 103031, already [13]/[30]) are documented so a future session does not re-run the same fruitless searches.

## 7.11 INTAKE + CITATION-CLEANUP ROUND (2026-11-09 — the user's "Useful papers.docx")

**Trigger.** The user supplied `Useful papers.docx`, a list of Cloud-9 / SIDM-profile literature with arXiv links, asking for KB building and citation cleanup.

**Method (what was actually done, so it can be repeated).** (1) Every arXiv ID in the doc was re-resolved against the arXiv export API before anything was downloaded — title, author list, `journal_ref`, date. (2) Journal venues, volumes, pages and DOIs were resolved against Crossref, not remembered. (3) PDFs were fetched to `to_verify/`, text extracted with pypdf, read end-to-end by two delegated readers under a schema, then **every headline number in this section was spot-grepped by the controller** against the extracted text before promotion. (4) All 8 entries were then moved to `verified/` with `_extracted_text_20261109/` kept alongside for provenance.

### New KB entries (PDF + .md now in `docs/papers/verified/`)

| KB file | arXiv | Verified record | Read level |
|---|---|---|---|
| `9611107_nfw_1997` | astro-ph/9611107v4 | ApJ 490, 493-508 (1997), DOI 10.1086/304888 (Crossref) | full text, clean layer |
| `9508025_nfw_1996` | astro-ph/9508025 | ApJ 462, 563 (1996), DOI 10.1086/177173 (Crossref) | **abstract-level only** — 1995 scan, text layer damaged |
| `9703057_burkert_1997` | astro-ph/9703057v1 | no arXiv journal_ref (review) | downloaded, text layer checked; not yet read numerically |
| `2411.11945_tran_2026` | 2411.11945v4 | PRD 113(6), March 2026 (arXiv journal_ref); 8 authors | full text |
| `2512.15869_despali_2026` | 2512.15869v2 | A&A **708, A47**, 2026-03-26, DOI 10.1051/0004-6361/202558686 | full text |
| `2501.12439_despali_introducing_aida_tng_2025` | 2501.12439v2 | A&A **697, A213**, 2025-05, DOI 10.1051/0004-6361/202553836 (InspHEP recid 2871654; PDF header "manuscript no. aa53836-25") | **bibliographic verified + full numerical read done 2026-11-10** (§2-7; numbers recorded in the KB entry with extract line anchors). **No AIDA value adopted as canonical:** their SIDM cases are σ/m = 1 cm²/g constant and Correa+ 2021 velocity-dependent, both outside the v19.2-F 50-483 cm²/g regime. Usable transfer: the NFW-vs-Einasto profile-family statement (§4.2 closing note) and the sign of the SIDM c–M effect at galaxy mass. |
| `1101.3097_koda_shapiro_2011` | 1101.3097v2 | MNRAS **415, 1125-1137**, 2011-06-27, DOI 10.1111/j.1365-2966.2011.18684.x | read for the calibration lines only: t_coll = 385 t_r,c(0), fluid C = 0.75 (b = 0.25); **contains no "150"** |
| `1501.00017_pollack_2015` | 1501.00017v1 | ApJ **804, 131**, 2015-05-12, DOI 10.1088/0004-637x/804/2/131 | read for the calibration line only: "C ≈ 290/385 ≈ 0.75" citing Koda & Shapiro as their [65]; **contains no "150"** |
| `2002.02102_yang_2020` | 2002.02102v2 | PRL 125, 111105 (2020); Daneng Yang, Hai-Bo Yu, Haipeng An | full text |
| `2403.11403_zhang_2024` | 2403.11403v2 | **no journal reference anywhere** — unrefereed preprint | full text |
| `2607.08818_sarratoalos_2026` | 2607.08818v2 | **A&A, doi:10.1051/0004-6361/202661941 (published online 2026-11-03; volume/page not yet assigned by Crossref)** | full text |

### Citation defects found by this round

**D1 — AIDA-TNG venue is wrong in `v0.3-prelim/docs/AUDIT_REFERENCES.md` (L76).** It prints "A&A 699, A222 (2026); arXiv:2512.15869v1". The correct record is **A&A 708, A47 (2026)**, arXiv current version **v2**. Crossref resolves A&A **699, A222** to a different paper entirely: "Detecting low-mass haloes with strong gravitational lensing" (2025-07). A citation with that volume/page would point a reader at the wrong paper.

**D2 — "Introducing the AIDA-TNG project" venue is wrong in the same file (L72).** It prints MNRAS (2024). Crossref resolves that exact title to **A&A 697, A213 (2025-05)**; no MNRAS record with that title was found.

**D3 — the paper uses the NFW profile with no NFW reference.** `PAPER_V1_DRAFT.md`'s References section holds 43 numbered entries. "NFW" appears **49 times** in the body, and `r_s`/`rho_s`/`c_200` are computed from M_200 and c_200 throughout `scripts/`. "Navarro" appears 4 times in the reference list, **all as a co-author of other papers** (Benítez-Llambay+ 2024 [1a]/[15b], Oman+ 2015 [2]). There is no primary NFW citation. This is the single most likely citation objection a referee would raise, and it is cheap to close: add `9611107_nfw_1997` as the profile/concentration definition.

**D4 — the registry's own §7.5 claim was stale.** §7.5 said Burkert 1995 was "cited but no local PDF". The current draft's References section contains **no Burkert entry at all**; all 26 body mentions of Burkert are "Burkert+ 2020 fits" inside quoted reviewer text. Correct record: Burkert 1995, "The Structure of Dark Matter Halos in Dwarf Galaxies", ApJ 447 (1995), DOI 10.1086/309560 (Crossref). **CORRECTION (2026-11-09, same round): the sentence "No arXiv preprint exists for it" was WRONG.** The preprint is `astro-ph/9504041` — Unpaywall lists `https://arxiv.org/pdf/astro-ph/9504041` as an open-access location for DOI 10.1086/309560, and Semantic Scholar records `externalIds.ArXiv = astro-ph/9504041` for the same DOI. The PDF has been downloaded and read (`docs/papers/verified/9504041_burkert_1995.pdf`, `.md`). Page form: the arXiv `journal_ref` gives "Astrophys.J.447:l25,1995"; Crossref and OpenAlex give vol 447 with no page field, so the citation is written ApJ 447, L25 (1995) sourced from arXiv. Also refine the "all 26 body mentions are quoted reviewer text" claim: the draft's own §2.6d anchors "Prescription B: Burkert-style" to "Burkert 1995 (ApJ 447, L25) cored profile" in the framework's voice, i.e. a named work with volume and page but no reference entry — which is exactly what slot [47] closes.

**D5 — three links in the user's doc point at unrelated papers** (recorded so they are not re-imported):
- "Moore+ 1998 minimum concentration" → `astro-ph/9810021` is actually Mendes de Oliveira+ et al., "A NIR search for high-redshift clusters" (1998).
- "Navarro+ 2004 Einasto" → `astro-ph/0403457` is Steed & Weinberg, "Explaining Low Redshift Quasar Evolution" (2004).
- "Burkert 1995, arXiv:astro-ph/9508181" → no such arXiv record exists; the doc's other link (ar5iv `astro-ph/9703057`) is Burkert's **1997 review**, not the 1995 profile paper. Its DOI 10.1086/309560 was the only correct element of that entry.
- `astro-ph/9611107` and `astro-ph/9508025` (the NFW pair) **are** correct, and the doc's labelling of them as "NFW 1997" / "NFW 1997" is loose: 9508025 is the 1996 ApJ paper, 9611107 the 1997 one.

**D6 — convention trap for whoever adds the NFW citation.** NFW 1996 states verbatim that "All physical quantities quoted in this paper assume a Hubble constant of 50 km/s/Mpc". v19.2-F uses `rho_crit = 1.381e-7 Msun/pc^3` at H_0 = 67.66 with Planck-2018 flat LambdaCDM and c_200 = r_200/r_s, i.e. the **critical-density** convention of NFW 1997 (whose eq. 1 defines rho/rho_crit with rho_crit = 3H^2/8piG). Cite **1997** for the profile and concentration definition. **RESOLVED 2026-11-09 (searched, then dropped):** the commonly repeated claim that NFW 1996 defines overdensity relative to the **mean** density is **not supported** by the 1996 text and has been removed from the [46] entry and from the open-item list. What the local 1996 text actually says (extract `docs/papers/verified/_extracted_text_20261109/astro-ph_9508025.txt`, degraded scan): it defines "rho_crit = 3H^2/8piG is the critical density", defines M_200 via "the sphere encompassing a mean overdensity of 200", scales its profile plots so that "the density is given in units of the critical density", and scales the characteristic overdensity as delta_c(z) proportional to (1+z_form)^3 with "the mean density of the universe at that redshift" as the scaling parameter. NFW 1997 states explicitly, in parentheses: "We remind the reader that delta_c is defined relative to the critical density rather than the mean density." Net: 1996 already works in units of the critical density, the mean-density framing appears in 1996 only as a redshift-scaling argument, and the project's 200 x rho_crit / c_200 = r_200/r_s convention is the 1997 one — so citing 1997 for the convention stands and the mean-vs-critical claim is not needed anywhere in the paper.

**D7 — two DOIs written from memory during this round were wrong and were corrected before commit** (10.1086/309191 → 10.1086/304888 for NFW 1997; 10.1086/176418 → 10.1086/177173 for NFW 1996). Recorded because it is the exact failure mode §8's rule exists to prevent: DOIs must be resolved, never recalled.

**D8 — the draft asks for a citation that does not exist in the form named, and the nearest real paper is a different field.** `PAPER_V1_DRAFT.md` refers five times to a "**Burkert+ 2020** c-τ prescription" (§2.6c/§2.6d, quoted from Nemotron 120B review text) and states that no such paper was found. A 2020 Burkert paper does exist: A. Burkert, "Fuzzy Dark Matter and Dark Matter Halo Cores," Astrophys. J. **904**, 161 (2020), doi:10.3847/1538-4357/abb242 (Crossref vol 904 issue 2 page 161; OpenAlex agrees; single author A. M. Burkert). It is a **fuzzy-DM** halo-core paper and contains no SIDM concentration-versus-collapse-time fit, so it cannot fill the slot. The other 2020 Burkert candidate, Burkert & Forbes, AJ 159, 56 (2020), doi:10.3847/1538-3881/ab5b0e, is a globular-cluster virial-mass paper and also cannot fill it. **Consequence:** the reviewer recommendation as named is unimplementable, and the framework already superseded it with Sameie+ 2020 [54c] in v40.43a. Recorded so a future session does not "find" Burkert 2020 and treat the open item as closed.

**D9 — the c-M sigma bookkeeping is internally inconsistent (found by the Y24 recheck, 2026-11-09). RESOLVED 2026-11-10.** Solving the paper's own pair (Ohana+ c_200 = 4 at 3.16 sigma, 0.16 dex) implies a c-M median of **12.81** at Cloud-9's mass. Under that single convention the framework's Elbert+ saturated prediction c_200 = 6.0 sits **+2.06 sigma**, not the **0.32 sigma** printed in §2.6c/§2.6d, and the retracted v40.39 value c_200 = 26.4 sits **-1.96 sigma**, not -1.42 sigma. The printed numbers imply medians of 6.75 and 15.65 respectively — three medians in one analysis — so the headline reduction "3.2 sigma -> 0.3 sigma" is not reproducible from any single median + scatter convention. **Resolution applied 2026-11-10 (owner decision):** `c_M_tension_sigma` now divides by one 0.16 dex scatter of log10(c_200) — the stray ln(10) removed — and every c-M sigma printed in the paper names the relation it is measured against: c_200 = 6.0 sits **+0.75 sigma (Diemer+ 2019, median 7.8964)** and **+2.06 sigma (Ohana+ 2026, implied median 12.81)**, and the prescription's effect is stated anchor-independently as **1.10 sigma** (the 0.176 dex shift log10(6.0/4.0)). The pre-fix behaviour is preserved as `c_M_tension_sigma_legacy()`, marked do-not-cite, so already-published numbers stay reproducible.

**Root cause (identified and fixed 2026-11-10, two independent faults):**
1. **Unit error.** `scripts/elbert2015_c_tau_prescription.py::c_M_tension_sigma()` divided the `log10` deviation by `scatter_dex * ln(10)` = 0.368 instead of `scatter_dex` = 0.16, understating every tension by a factor **ln(10) = 2.303**. With the code's own median (Diemer+ 2019, `7.4 (M/10^10)^-0.086 = 7.90` at M_200 = 4.7e9), c_200 = 6.0 gives 0.11937 dex / 0.3684 = **0.3238** — exactly the value stored in the result JSON — and / 0.16 = **0.749**. The legacy behaviour is preserved as `c_M_tension_sigma_legacy()` so old published numbers stay reproducible.
2. **Anchor mixing.** Those Diemer-anchor numbers were subtracted from Ohana+ 2026's 3.2 sigma, which is quoted against Ohana+ 2026's own c-M relation (implied median 12.81, **1.31 sigma above** the Diemer median). The two relations are not interchangeable and the draft never named either.

**Corrected numbers (1 sigma = 0.16 dex).** c_200 = 4.0 (Ohana+ measured): +1.85σ Diemer / +3.16σ Ohana. c_200 = 6.0 (Elbert+ floor): +0.75σ / +2.06σ. c_200 = 3.6 (Burkert-style floor): +2.13σ / +3.45σ. c_200 = 24.0 (Sameie+ 2020 ceiling): −3.02σ / −1.70σ. c_200 = 26.4 (retracted v40.39): −3.28σ / −1.96σ. c_200 = 12.0 (NFW baseline c_0): −1.14σ / +0.18σ.

**Consequences.** The headline claim becomes **a 1.10σ reduction** (`log10(6.0/4.0) = 0.176 dex`, identical at either anchor), not 2.9σ; the residual against the observation's own relation is **2.06σ**, i.e. reduced and not resolved. The v40.43 "ROBUST: all prescriptions < 1σ" verdict falls under the corrected convention alone (Burkert-style 2.13σ), before Sameie+ 2020 is considered, and is withdrawn.

**Where fixed:** `scripts/elbert2015_c_tau_prescription.py` (fixed `c_M_tension_sigma`, added `c_M_tension_sigma_legacy`, `C200_MEDIAN_OHANA2026_IMPLIED = 12.81`, `c_M_tension_sigma_ohana2026`, `c_M_shift_sigma`); `scripts/v19_2_f_cloud9_cM_elbert.py`, `scripts/v19_2_f_cloud9_cM_marginalized.py`, `scripts/v19_2_f_cloud9_cM_three_prescriptions.py` (emit both anchors, no hard-coded sigma literals); the three result JSONs regenerated; `v0.3-prelim/tests/test_v40_42_elbert_c_tau.py`, `test_v40_43_marginalization.py`, `test_v40_43a_three_prescriptions.py` (assertions rewritten to pin both anchors — 15/15 pass); `PAPER_V1_DRAFT.md` §2.6c, §2.6d, §2.6e, §2.7 (anchor convention paragraph). Evidence and arithmetic: `v0.3-prelim/docs/V19_2_F_Y24_PROFILE_FAMILY_RECHECK.md` §3, reproducible via `v0.3-prelim/code/v19_2_f_y24_profile_family_recheck.py`. Historical review reports dated 2026-10-19 (`SIDM_V40_50/51_FULL_REVIEW_REPORT`) still print the legacy values and are left as dated artifacts.

**D10 — phantom citation carried by the M2 vector-portal code.** `v0.3-prelim/code/v19_2_f_loop1_segue1_veff_check.py` attributes its model (m_rho = 0.05 meV, Gamma_rho/m_rho = 1) to "Chu, Hambye, Tytgat 2018 (M2 model, arXiv:1712.02521)". **arXiv:1712.02521 is "An integrated single- and two-photon non-diffracting light-sheet microscope", Rev. Sci. Instrum. 89, 043701 (2018), authors Lau, Chiu, Zhao, Zhao, Loy & Du** — an optics instrument paper. A Crossref author query for Chu+Hambye+Tytgat restricted to 2017-06 through 2019-06 returns **no** three-author 2018 paper. The body inherited the label at three sites ("Chu, Hambye & Tytgat 2018 [7]" x2, "Chu+ 2018 [7]" x1) even though slot [7] is Chu, Garcia-Cely & Murayama 2019 (PRL 122, 071103, arXiv:1810.04709); all three were corrected on 2026-11-09 and the vector portal is now cited to [29] (Chu, Hambye & Tytgat 2012, JCAP 05 (2012) 034, arXiv:1112.0493 — identity re-verified against the arXiv record and Crossref). The code header itself still carries the phantom string and has not been edited.

**D11 — stale citation slots at the "150 prefactor" line.** The body read "(Balberg+ 2002 [7], Koda+ 2011 [23], Pollack+ 2015 [48])": [7] is Chu+ 2019, [23] is Yu 2026, and [48] is Despali+ 2026, while Koda and Pollack had **no entries at all**. Corrected to Balberg+ 2002 **[18]**, Koda & Shapiro 2011 **[56]** (MNRAS 415, 1125-1137, arXiv:1101.3097, doi:10.1111/j.1365-2966.2011.18684.x) and Pollack, Spergel & Steinhardt 2015 **[57]** (ApJ 804, 131, arXiv:1501.00017, doi:10.1088/0004-637x/804/2/131), both resolved via Crossref on 2026-11-09 (Crossref carries no arXiv relation for either, so the ids came from arXiv title+author searches, one match each). "Pollack+ 2015" in this lineage is the ultra-strong-SIDM gravothermal-collapse paper, not a gravothermal-catastrophe-only paper. Both PDFs downloaded 2026-11-09, admitted only after each PDF's own first page confirmed title + authors, and summarised in `docs/papers/verified/`.

**D12 — the arXiv id carried in session notes for "Introducing the AIDA-TNG project" is a different paper.** `arXiv:2404.10440` is "Language Proficiency and F0 Entrainment: A Study of L2 English Imitation in Italian, French, and Slovak Speakers" (linguistics). It was fetched into the KB by that id, caught only because the PDF identity gate compared the file's own title page, and the file was deleted. The correct record, resolved via InspHEP (recid 2871654) and confirmed from the downloaded PDF's own header ("arXiv:2501.12439v2 ... manuscript no. aa53836-25"), is **arXiv:2501.12439v2, A&A 697, A213 (2025), doi:10.1051/0004-6361/202553836**, Despali, Moscardini, Nelson, Pillepich, Springel, Vogelsberger. Lesson: resolve arXiv ids from Crossref/InspHEP relations or an arXiv title search, never from memory, and check the PDF's first page before a PDF is admitted to `verified/`.

**D13 — the "150 prefactor" attribution in §A.16 was wrong (found 2026-11-09 by reading the three papers it named).** The draft stated the 150 in `t_c = 150 C / ((σ_eff/m) ρ_eff r_eff √(4πGρ_eff)))` "is taken from earlier gravothermal literature (Balberg+ 2002, Koda & Shapiro 2011, Pollack+ 2015)". Reading the actual papers: the token **"150" does not occur in any of the three** (0 matches in Balberg+ 2002 over 12 pages, 0 in Koda & Shapiro 2011, 0 in Pollack+ 2015). The 150 is **Yang+ 2024 [43]'s own coefficient** — extracted text of `2305.16176`: eq (2.2) prints "150 / ( C (σ_eff/m) ρ_eff r_eff √(4Gρ_eff) )" followed by "where C is constant that can be calibrated with N-body simulations [8, 9, 48, 49], and we fix C = 0.75". What the older papers supply is the **coefficient C = 0.75 and the collapse timescale in relaxation times**: Balberg+ 2002 "a typical halo has a gravothermal collapse time t_coll(SIDM) ≈ 290 t_r(SIDM)" (and "∼ 289 t_r(0)" in the large-mean-free-path limit); Koda & Shapiro 2011 "t_coll = 385 t_r,c(0) or C = 0.75" with calibrated "(C=0.75, b=0.25)"; Pollack+ 2015 "determined by N-body simulations [65] to be C ≈ 290/385 ≈ 0.75", where their [65] is Koda & Shapiro — an independent cross-confirmation of both [56] and, in the same reference list, of [18] ("Astrophys.J. 568 (2002) 475-487, arXiv:astro-ph/0110561"). §A.16 rewritten accordingly with the quotes. Net effect on the paper's own argument: none of the numbers change, but the prefactor is now correctly labelled as **an empirical constant fixed by the model being adopted ([43]), calibrated upstream by N-body work ([18]/[56]/[57])** — which strengthens, not weakens, the appendix's own conclusion that the 150×C combination is not universal.

**SLOTS APPLIED (2026-11-09, same round as §7.11 above):** the five proposed slots were added to `PAPER_V1_DRAFT.md`'s References section and cited in the body — **[44]** NFW 1997 (profile + c_200 convention; body §2.6 footnote), **[46]** NFW 1996 (companion, convention warning only), **[47]** Burkert 1995 (body §2.6d Prescription B), **[48]** Despali+ 2026 AIDA-TNG profiles (body §5 profile-family caveat), **[53]** Yang, Yu & An 2020 DF2 (body §5 published precedent for the c-M argument, with the scatter-convention caveat). The References entry count went 43 -> 48 and the section's status line was recounted from the file. Gates re-run after the edit.

### Why these papers matter to v19.2-F (not just coverage)

- **Tran+ T25 (2411.11945)** and **AIDA-TNG (2512.15869)** are both evidence that a fitted concentration depends on the profile family. AIDA-TNG states SIDM1/vSIDM **Einasto** concentrations "remain systematically lower than CDM in all masses ... a direct consequence of the inner core, whose presence is not fully absorbed" by the fit, while its Y24 (Gilman+ 2021 / Yang+ 2024) fits behave differently. The project's headline "NFW fit is 7σ below the c-M relation, SIDM reduces it to 3σ" is therefore partly a **fit-family statement** and should be checked against a Y24-style fit before being presented as a model-discrimination result.
- **Yang+ 2020 (2002.02102)** is the closest published analogue of the project's argument: a halo that is **4σ below** the c-M median (c_200 = 4) is unreproducible in CDM, and SIDM removes the deficit because core formation raises the fitted concentration and enhances tidal mass loss. It also documents the competing CDM explanation (an implausibly low concentration) rather than assuming it away.
- **Sarrato-Alós (2607.08818)** supplies the cleanest single number for the underlying mechanism: an unmodified NFW profile over-predicts the central density of cored dwarf systems by **2-3σ**, and simulated cored profiles agree with observations to <~1σ.
- **Zhang+ 2024 (2403.11403)** and Yang+ 2020 place the DF2/dwarf literature at **0.3-13 cm^2/g**, i.e. 37-1600x below the project's low-velocity amplitude. Useful as a literature-comparison sentence, not as a constraint.
- **Tran+** itself simulates at 21.94 and 31.98 cm^2/g (10^7-10^8 Msun halos) — the same decade as Cloud-9's >= 50 cm^2/g benchmark, and its Appendix A7 fit table gives r_s values of 18.4-21.2 kpc for those halos.

### Proposed slots (NOT applied — the draft was not edited in this round)

| Proposed | Entry | Where it belongs |
|---|---|---|
| new [N1] | Navarro, Frenk & White 1997, ApJ 490, 493-508 | §2.1 / wherever the NFW profile and c_200 = r_200/r_s are first used |
| new [N2] (optional) | Navarro, Frenk & White 1996, ApJ 462, 563 | same sentence, as the original halos paper |
| new [N3] (optional) | Burkert 1995, ApJ 447, L25 | wherever Burkert cores or the c-tau prescription are named |
| new [N4] (optional) | Despali+ 2026, A&A 708, A47 | §3.4 UFD cores / the c-M deviation discussion |
| new [N5] (optional) | Yang, Yu & An 2020, PRL 125, 111105 | §3.2 Cloud-9, as the published precedent for a below-median-concentration halo repaired by SIDM |

Applying these requires paper edits (reference list plus the sentences that name NFW); that is deliberately left for approval.

### Open items

1. **CLOSED 2026-11-09:** Burkert 1995 PDF obtained (`astro-ph/9504041`, 17 pp) and read; slot [47] added.
2. **CLOSED 2026-11-09 (volume/page still pending):** `2607.08818` is now Crossref-registered as **doi:10.1051/0004-6361/202661941** (Astronomy & Astrophysics, published online 2026-11-03), and the local PDF's own header reads "Astronomy & Astrophysics manuscript no. **aa61941-26**", which corroborates the DOI slug. Crossref still reports **no volume and no page**, so the citation stays "accepted, A&A, doi:10.1051/0004-6361/202661941, arXiv:2607.08818v2" until a volume appears. arXiv shows only v1/v2 (v2 = 2026-11-09); the local PDF is v2.
3. `2403.11403` has no journal reference at all — label as a preprint if used.
4. **CLOSED 2026-11-09:** see D6 — the NFW 1996 mean-vs-critical convention claim was searched against the 1996 text, found unsupported, and dropped. Nothing in the paper needs it.
5. Numbers quoted from `9508025_nfw_1996` are abstract-level only.
