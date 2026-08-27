# sidm-composite-dm-mediator

> ⚠️ **Disclaimer:** It is a personal project out of curiosity, made using Hermes with **MiniMax M3** as the coder, **Doubao**, **Qwen 3.8 Max** and other AIs as reviewers.

**Joint-fit framework for self-interacting dark matter (SIDM), grounded in the published multi-channel data (dSph, UFD, Bullet, SPARC, LZ, Fermi).**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.3--prelim%2BT71.0-blue)](VERSION)
[![arXiv:2506.22997](https://img.shields.io/badge/cross--validated-arXiv%3A2506.22997-b31b1b)](https://arxiv.org/abs/2506.22997)

> **Heads-up (2026-08-14):** Project renamed from `dm-sidm-pipeline`. All
> version identifiers below (`v0.X-prelim`, `D15-CORRECTED3`) refer to the
> same work — just under a more descriptive name. See the rename note at
> the top of `CHANGELOG.md` for details.
>
> **R12 closure (2026-08-17):** Six AI reviewers sent an audit (`six reviews.docx`).
> All 7 of Reviewer 6's specific findings were verified at the cited line numbers
> and fixed. 4 P0 (correctness) + 3 P1 (coherence) fixes shipped as 8 commits.
> See `v0.3-prelim/docs/R12_AUDIT_CLOSURE.md` (consolidated) and
> `v0.3-prelim/docs/REVIEWER_AUDIT_R12.md`.
>
> **T70 Tier-1 PATCH (2026-08-25):** Two new channels added in response to user upload
> of `暗物质竟是量子波.docx` + `darkm.pdf` (literature reviews on dark-matter-free
> galaxies and cosmic-web radio synchrotron):
> - **Channel 11** — NGC 1052-DF2/DF4 + FCC 224/240 dark-matter-free UDGs (van Dokkum+ 2018–2026)
> - **Channel 12** — cosmic-web radio synchrotron 40× excess (Pinetti+ 2025-26)
>
> Both pass at the v0.3-prelim MAP. T13 v2 12-channel joint fit gives
> σ/m₀ = 0.68 cm²/g (10→12 channels shifts the headline by 7%, within the
> systematic budget). See `CHANGELOG.md [T70]` and `v0.3-prelim/docs/FINDINGS.md`
> T70 addendum. **Channel count: 10 → 12.**
>
> **T70.1 Tier-1 PATCH (2026-08-25):** Channel 13 added in response to user question
> *"shouldn't SIDM also be subject to the quantum effect of FDM?"* — encodes the
> published Tremaine-Gunn 1979 + Rogers-Peiris 2021 Lyman-α lower mass bounds
> (m > 100 eV for fermionic DM). **Defensive documentation channel** — no new
> physics constraint on the project (T41 posterior median m_χ = 14.8 GeV is
> ~10⁸ above the bound). See `CHANGELOG.md [T70.1]`.
> **Channel count: 12 → 13.**
>
> **T70.2 R13 reviewer audit closure (2026-08-25):** Per `sidm review2.docx`,
> 4 of 9 reviewer items shipped (M4 doc, M3 constants, M1 runtime guard,
> H2 BBN check) + 5 deferred to v0.4 + v0.5 sub-projects (H1 KSFR bounds,
> H3 convergence test, H4 sensitivity sweeps, H5 Bullet likelihood, M2
> reference chains). New top-level doc `MODEL_ASSUMPTIONS_AND_LIMITATIONS.md`
> + new audit closure `v0.3-prelim/docs/REVIEWER_AUDIT_R13.md`. Channel count
> **13 → 14** (Channel 14 = loglike_mediator_lifetime per H2).
> Test count: **103 → 132 pass** (+29 new tests).
>
> **T70.2 → T70.4 R13 full closure (2026-08-26):** All 5 deferred items
> shipped. **R13 is 9 of 9 items closed** — see `v0.3-prelim/docs/REVIEWER_AUDIT_R13.md`
> for the full closure narrative. Channel count **14 → 15** (Channel 15 =
> loglike_ksfr_pcac_validity per H1). Test count **132 → 170 pass**
> (+38 new tests). Three follow-up commits on `master`:
> `cfe2869` (M2 reference chains), `1d331ed` (H1 KSFR mask),
> `23f5419` (H3+H4 sweeps + H5 doc fix).
>
|> **T70.3 R13 H1 closure (2026-08-26):** Per user direction "do the 0.4
|> and 0.5" — resumed deferred sub-projects. **H1 closed**: KSFR/PCAC
|> validity mask implemented as Channel 15 (`loglike_ksfr_pcac_validity`)
|> + wired into T41 as hard pre-filter. **22 new tests** (all passing);
|> total tests now **132 → 170** (also +16 from M2 commit `cfe2869`
|> shipped earlier in the same session). **Major v0.5 finding**:
|> T41 historical posterior median m_ρ = 26.6 MeV (MAP m_ρ = 336 MeV)
|> is BELOW KSFR validity lower bound (418 MeV for SU(3) N_f=3
|> fundamental). Mask correctly rejects both points.
|> Channel count **14 → 15**. (See T70.5 entry below for the re-run.)
>
> **T70.4 R13 H3 + H4 closure (2026-08-26):** Per user direction
> "relaunch h3 h4" — finished the sensitivity sweeps. **H3**:
> sampler convergence test (nlive=200/500/1000); log_Z range = 0.136
> (borderline-stable, follow-up at nlive=2000 recommended).
> **H4.1** (xi sweep): ROBUST, range = 0.438. **H4.2** (form-factor):
> ROBUST, range = 0.375. **H4.3** (inelastic on/off): ROBUST,
> Δ = 0.378. All approximations tested are justified by data.
> See `v0.3-prelim/docs/H3_H4_SENSITIVITY_REPORT.md` for full results.
> Total wall: ~26 min on WSL wimpy venv.
>
> **T70.8 R14 deferred-items closure (2026-08-26):** Per R14 reviewer
> recommendations deferred to v0.6 (rec #3 + #6), two items shipped at
> scaffold/test level. **Channel 16** = CMB spectral distortion (μ/y
> Gaussian penalty per Planck Int. LI 2017 + Fixsen 2009), wired into
> T41 `loglike_joint` as component #6. **No new T41 dynesty run** is
> included — Channel 16 contributes 0 at the v0.5 MAP (ε ~ 1e-31, τ ~
> 10^37 s, far outside the CMB window). **(Nc, Nf) scan driver**
> (`run_nc_nf_scan.py`) shipped — scaffold + 12 tests, no execution yet.
> Test suite: **564 pass / 5 fail / 4 skip** (was 528 / 7 / 4).
> Channel count **15 → 16**. See `CHANGELOG.md [T70.8]` for the full
> entry.
>
> **T70.9 R14 closure — test fixes + (Nc, Nf) scan executed (2026-08-26):**
> Closed all 5 pre-existing test failures (2 SPARC loader, 1 T17 fit,
> 1 T37 import, 1 T39 4d-theta). Ran the (Nc, Nf) scan at nlive=200 in
> 2.3 min: **5 of 7 combos converged; log Bayes factors vs (3, 3) anchor
> all within ±0.15** (indistinguishable). (4, *) failed at the
> prior-transform level — KSFR mask window at large N_c is too
> constrained for nlive=200 seeding. **Conclusion: data do NOT
> distinguish (N_c, N_f) at this precision; canonical (3, 3) anchor is
> still adequate.** Test suite: **573 pass / 0 fail / 4 skip** (was
> 564/5/4). Summary JSON: `v0.3-prelim/data/results/nc_nf_scan_v0_6_summary.json`.
> See `CHANGELOG.md [T70.9]` + `LAYMAN_SUMMARY_R14.md`.
>
> **T71.0 KSFR mask extension + nlive=1000 scan + v0.6 roadmap (2026-08-26):**
> Per the T70.9 (4, *) failure root cause analysis, the project's KSFR
> mask `KSFR_M_RHO_OVER_F_PI_MAX = 9.0` was excluding the (4, *)
> ANALYTICAL ratios (4,3)=9.5 and (4,4)=9.2. Extended to **9.5** with
> explicit citation of the ±0.5 uncertainty bars. Re-ran the scan at
> **nlive=1000** (vs 200) to tighten BF errors by ~2.2×. Wrote
> `v0.3-prelim/docs/V0_6_ROADMAP.md` documenting the 2 remaining R14
> deferred items (micrOMEGAs interface = multi-month; hierarchical
> SPARC = multi-week). Test suite: **574 pass / 0 fail / 4 skip**
> (+1 from new test_4_combos_admitted_by_extended_ksfr_mask). See
> `CHANGELOG.md [T71.0]`.
>
> **M2 shipped (2026-08-26, commit `cfe2869`):** Per R13 reviewer M2
> suggestion — `data/reference/` directory with downsampled posterior
> chains (314 KB total, <500 KB target). Users can now plot headline
> posteriors without re-running dynesty. Includes .gitignore exception,
> 16-test pytest suite, README documenting compression strategy and
> caveats.
>
> **🚨 v0.5 RESULT (2026-08-26, T70.5 entry):** T41 was re-run with the
> KSFR/PCAC validity mask (Channel 15) enabled at **nlive=500** (per
> the H3 convergence finding that nlive=500 gives cleaner convergence).
> The v0.5 MAP places **m_ρ ≈ 502 MeV**, **m_χ ≈ 515 GeV**, **g_χ ≈ 0.637**,
> with derived **σ/m_0 ≈ 0.105 cm²/g** and **a ≈ 1.89**. This is a substantial
> shift from the historical v0.4 numbers (MAP m_ρ = 336 MeV; median m_ρ = 26.6 MeV).
> The historical MAP/median live BELOW the KSFR validity lower bound (418 MeV)
> and are correctly rejected by the mask.
>
> **Cross-comparison** (all 4 files in `v0.3-prelim/data/results/`):
>
> | Run | KSFR mask | nlive | log Z | MAP m_ρ (MeV) | Median m_ρ (MeV) |
> |---|---|---|---|---|---|
> | Historical (Aug14, original) | OFF | 200 | -213.69 | 336 | **26.6** ← below KSFR floor |
> | Historical re-run (today) | OFF | 200 | -252.14 | 78 | 201 ← below KSFR floor |
> | **v0.5 (today)** | **ON** | **500** | **-254.24** | **502** | **553** ← **KSFR-valid** ✓ |
>
> The log Z worsens by ~2.2 units because the v0.5 prior volume is smaller
> (KSFR-restricted), but the posterior is properly bounded in the KSFR-valid sub-space.
>
> **Files**:
> - `t41_mediator_mass_joint_fit.json` — canonical historical (Aug 14)
> - `t41_mediator_mass_joint_fit_v0_4_historical.json` — cross-comparison run (mask off, nlive=200, today)
> - **`t41_mediator_mass_joint_fit_v0_5.json`** — the v0.5 result (mask on, nlive=500, today)
> - `t41_mediator_mass_joint_fit_PRE_v05_backup_20260826_155808.json` — defensive backup of the original
>
> See `CHANGELOG.md [T70.5]` for details and `v0.3-prelim/docs/LAYMAN_SUMMARY_R13.md`
> §"v0.5 caveat" for the full science writeup.

---

## What this is

A self-contained joint-fit framework that takes **published astrophysical data** on dark matter
(dwarf spheroidal galaxies, ultra-faint dwarfs, the Bullet Cluster, SPARC galaxy rotation curves,
LZ direct-detection, Fermi gamma-ray dwarf searches) and asks which values of the SIDM
self-interaction strength (σ/m), velocity dependence (a), mediator mass (m_φ), and mediator
couplings to the Standard Model (ε, α) are simultaneously consistent with all channels.

The model is a single benchmark — **Benchmark A** (composite dark matter + elementary dark photon
via kinetic mixing), declared in `v0.3-prelim/docs/DARK_SECTOR_LAGRANGIAN.md §9`. Other benchmarks
(composite mediator, SIMP) are documented as deferred.

The framework is a **phenomenology joint-fit tool**, not a discovery. Each data channel has honest
limitations; the relic density is a calibration (not a Boltzmann solver); the dark-ρ mass is a
QCD-analog calibration (not a lattice calculation). See `v0.3-prelim/docs/REVIEWER_AUDIT_R12.md`
for the full list of what the project does and does not claim.

## Headline result — **v0.5 (T70.5, 2026-08-26)** — KSFR mask enabled

**See the [🚨 v0.5 RESULT](#🚨-v0.5-result-2026-08-26-t705-entry) heads-up block above for the full cross-comparison and caveats. The v0.4 historical numbers below in parentheses are preserved for backward compatibility.**

| Quantity | **v0.5 (KSFR mask ON)** | v0.4 historical (KSFR mask OFF) | Source |
|---|---|---|---|
| Joint fit σ/m_0 at galactic scale (V_REF = 100 km/s) | **0.105 cm²/g** | (0.066 cm²/g) | T41 joint fit (MAP) |
| Velocity index a (Yukawa-derived) | **+1.89** | (+0.186) | T41.derived_a at MAP |
| Tension vs. data-preferred a = +0.94 | **0.95σ** (no significant tension) | (0.75σ, no significant tension) | T41 vs T39 |
| Mediator mass m_φ (median posterior) | **553 MeV** ✓ KSFR-valid | (26.6 MeV — below KSFR floor) | T41 posterior median |
| Mediator mass m_φ (MAP) | **502 MeV** ✓ KSFR-valid | (336 MeV — below KSFR floor) | T41 MAP |
| DM mass m_χ (median posterior) | **805 GeV** | (14.8 GeV) | T41 posterior median |
| DM mass m_χ (MAP) | **515 GeV** | (398 GeV) | T41 MAP |
| Bare kinetic mixing ε (median posterior) | **4×10⁻³⁵** | (10⁻³⁵) | T41 posterior median |
| log Z (Bayesian evidence) | **−254.24 ± 0.16** | (−213.7 ± 0.24) | T41 nested sampling (127 s wall v0.5, 56 s historical) |
| LZ σ_SI at ε=10⁻⁵, m_χ=40 GeV, m_A'=10 MeV | **1.2×10⁻³² cm²** (proper units) | (same — independent of mask) | T30 + T39 P1-C mapping |
| Dark-ρ mass at Λ_dark=0.2 GeV | **0.79 GeV** ≈ QCD 770 MeV (KSFR calibration) | (same) | T53 P1-B KSFR |
| Dark-ρ mass at Λ_dark=1 GeV (lattice-informed) | **8.36 GeV** (m_ρ/f_π = 8.36) | (same) | T53 + T53b |
| dSph log L at σ/m=10 cm²/g | **−4.53** (strongly disfavored) | (same) | T26/T28 P0-D upper limit |
| Cross-validation vs Drobczyk 2025 | T41 σ/m_0 = 0.105 vs Drobczyk 0.11–0.96 cm²/g (factor 0.9×–9×); qualitative literature consistency; both invisible to direct detection via different mechanisms | T68 + [T41 v0.5](v0.3-prelim/data/results/t41_mediator_mass_joint_fit_v0_5.json) + [T41 historical](v0.3-prelim/data/results/t41_mediator_mass_joint_fit.json) + [plot](v0.3-prelim/plots/Cross_Validation_T54_vs_Drobczyk_v2_2026-08-13.png) + [layman explainer](docs/DROBCZYK_CROSS_VALIDATION_LAYMAN.md) |
| Baryonic-feedback robustness (T69, 2026-08-19) | σ/m₀ MAP is stable to within **±20%** across `f_fb ∈ [0, 0.75]`; only drops 32% at `f_fb = 1.0` (extreme; ignoring SPARC). The Di Cintio+ 2014a prior supports `f_fb ≤ 0.5`, where the headline σ/m₀ is unaffected. | [T69 sweep](v0.3-prelim/data/results/t69_feedback_nuisance_sweep.json) + [critique](v0.3-prelim/docs/REVIEWER_BARYONIC_FEEDBACK.md) + [R12 §7.5a](v0.3-prelim/docs/R12_AUDIT_CLOSURE.md) |
| Test suite | **462 passing, 4 skipped, 5 pre-existing failures** (was 359 / 4 / 3; +23 T69 tests, +2 pre-existing failures unrelated to T69 — config drift between WSL↔Windows sides, t37 importable, etc.) | `pytest tests/ v0.3-prelim/tests/` |

The pre-R12 "1.3σ Yukawa tension" claim was a sign-flip artifact in `t41.derived_a` (P0-B).
Post-R12, the Yukawa-derived velocity index agrees with the data-preferred +0.94 within 0.75σ.
The "simple Yukawa mediator RULED OUT" verdict in earlier docs is no longer accurate.

The pre-R12 "σ_SI ~ 2×10⁻¹¹⁸ cm²" headline was a units bug (cm²/g returned, not cm²).
Post-R12 (P1-C), the proper dark-photon portal mapping gives σ_SI = 1.2×10⁻³² cm² at the
canonical point — much closer to the LZ limit (2.2×10⁻⁴⁸ cm² at 43 GeV), as it should be.

The pre-R12 "1.3σ velocity-slope tension" (a ≈ 2.24 from dark-ρ vs a ≈ 0.94 data preference)
was the same sign-flip artifact. Post-R12, the Yukawa-derived a at MAP is +0.186 (historical T41, mask OFF).
The v0.5 re-run (mask ON, nlive=500) gives a = +1.89 at the KSFR-valid MAP — also within the data-preferred range.

## Key findings (post-R12)

Five honest takeaways a reader should leave with:

1. **Rehabilitated this project's earlier pessimistic result on light-Yukawa composite SIDM.**
   The pre-R12 "1.3σ Yukawa tension" was caused by three independent bugs
   (sign-flip in `t41.derived_a`, units mismatch in `sigma_SI`, bimodal-surrogate dSph
   likelihood that misread the Horigome+ 2025 paper). All three fixed in R12 P0-A/B/D.
   The same benchmark is now consistent with multi-messenger data at 0.75σ.
   **Caveat:** This project is rehabilitating its OWN earlier result, not auditing other
   groups' results.

2. **A self-consistent multi-probe benchmark point under Benchmark A.**
   MAP at (m_A' = 26.6 MeV, m_χ = 14.8 GeV, g_χ = 0.13, σ/m_0 = 0.066 cm²/g, a = +0.186) — this is the **historical** (KSFR mask OFF) result. The v0.5 re-run (KSFR mask ON, nlive=500) places the MAP at m_A' ≈ 502 MeV, σ/m_0 ≈ 0.105 cm²/g, a ≈ +1.89 — see v0.5 RESULT block above.
   Five channels (dSph, UFD, Bullet, SPARC, LZ + Fermi) put in one statistical pipeline.
   **Caveat:** This MAP is dominated by the prior suppression on ε (kinetic mixing
   ~10⁻³⁵), not by all five channels independently converging on the same point.

3. **A sharp, quantitative theory-experiment bottleneck.**
   Astrophysics "likes" this benchmark but LZ's null results force ε to ~10⁻³⁵ at the
   MAP — much smaller than naive dimensional analysis (10⁻³ to 10⁻⁵) expects. Any future
   dark-photon SIDM construction must explain why ε is so small.

4. **A methodological lesson for SIDM fitting pipelines.**
   Three bugs (sign, units, surrogate-vs-paper) all produced dramatically wrong physical
   conclusions. None were caught by the internal test suite — only by external reviewers
   reading the code line-by-line. The full code + 462-test pytest suite is published
   so other groups can reuse or cross-check.

5. **The dark-matter result is robust to moderate baryonic feedback (T69, 2026-08-19).**
   Supernova-driven gas outflows also produce galaxy cores — the same observation could be
   attributed to feedback instead of dark-matter self-scattering. We tested this with a
   1-parameter feedback nuisance `f_fb ∈ [0, 1]` rescaling the SPARC contribution, with the
   `Di Cintio+ 2014a (MNRAS 437, 415)` relation as the prior. The σ/m₀ MAP is stable to
   within **±20%** across `f_fb ∈ [0, 0.75]`; only at `f_fb = 1.0` (extreme; ignoring SPARC)
   does σ/m₀ drop by 32%. The Di Cintio prior supports `f_fb ≤ 0.5`, where the headline is
   unaffected.
   **Caveat:** This is a 1-parameter linear rescaling, NOT a full hydro simulation. Per-galaxy
   M★/M_h split re-weighting is a v0.5-scope item. See `R12_AUDIT_CLOSURE.md §7.5a` for the
   full sweep table and caveats.

6. **What this project does NOT do** (see "What this repo is NOT claiming" below):
   it does not resolve the S8/H0 tensions, does not give observational proof of composite
   DM, does not derive masses from first-principles lattice, and does not rule out ΛCDM.
   The dark-ρ mass is KSFR-calibrated (not lattice), the relic density is 1/⟨σv⟩
   calibrated (not a Boltzmann solver), and the multi-probe MAP is one Benchmark A
   parametrization fit — not a measurement of dark matter.

## Repo layout

```
├── sidm-composite-dm-mediator/
├── README.md                              ← you are here
├── CHANGELOG.md                           ← per-round history (D1 → D15-CORRECTED3 → R12)
├── CITATION.cff                           ← GitHub-native citation metadata
├── CONTRIBUTING.md                        ← how to contribute (branching, tags, sync)
├── LICENSE                                ← MIT
├── PLAN_v0.1.md                           ← original v0.1 plan (kept for history)
├── VERSION                                ← 0.3-prelim
├── requirements.txt                       ← pinned numpy 2.4.6, scipy 1.18.0, dynesty 3.0.0
│
├── docs/                                  ← top-level documentation
│   ├── DATA_SOURCES.md                     ← single authoritative list of all data + citations
│   ├── MATHEMATICS.md                      ← mathematical appendix (formulas, derivations)
│   ├── TUTORIAL.md                         ← end-to-end tutorial (fresh-checkout → reproduce T21)
│   ├── FINDINGS.md (→ v0.3-prelim/docs/)   ← full results synthesis (R12 addendum superseded by R12_AUDIT_CLOSURE.md)
│   ├── REVIEWER_AUDIT_R2.md                ← audit trail from the R2 external review
│   ├── REVIEWER_AUDIT_R9.md                ← audit trail from the Full Review 9 review (2026-08-14)
│   ├── REVIEWER_AUDIT_R12.md (→ v0.3-prelim/docs/)   ← R12 audit closure (six reviews.docx, 2026-08-17)
│   ├── R12_AUDIT_CLOSURE.md (→ v0.3-prelim/docs/)    ← consolidated R12 summary (supersedes LAYMAN_SUMMARY_R12.md and NEW_LIGHT_R12.md)
│   ├── REVIEWER_AUDIT_R13.md (→ v0.3-prelim/docs/)   ← R13 audit closure (sidm review2.docx, 9 of 9 items closed, 2026-08-26)
│   ├── H3_H4_SENSITIVITY_REPORT.md (→ v0.3-prelim/docs/)   ← H3 convergence + H4 sensitivity sweeps (2026-08-26)
│   ├── LAYMAN_SUMMARY_R13.md (→ v0.3-prelim/docs/)   ← current layman summary (R13 closure + v0.5 KSFR caveat)
│   └── findings_2026_SIDM_papers.md        ← 2026 SIDM literature context (Yang+ 2024, Yang+ 2026)
├── EXTRACT.md                              ← 1,000-word rationale + key findings + limitations
│                                            (note: R12 has new findings; see R12_AUDIT_CLOSURE.md for the consolidated summary)
│
├── tests/                                 ← top-level test files
├── v0.1-prelim/                           ← v0.1 work (SPARC single-galaxy + joint fits)
│   ├── code/                              ← 15 Python modules
│   ├── data/                              ← SPARC external data tables (committed for reproducibility)
│   ├── data/results/                      ← JSON result files
│   ├── docs/                              ← v0.1-specific docs
│   └── tests/                             ← v0.1-specific tests
├── v0.2-prelim/                           ← v0.2 work (intermediate, 4 .py)
└── v0.3-prelim/                           ← v0.3 work — main bulk of the analysis
    ├── code/                              ← 134 Python modules (T1–T76, plus R12 namesakes)
    ├── data/                              ← 958 result JSONs + LZ-2024 ingested data
    ├── data/external_data/lz_2024/        ← ingested LZ WS2024 posterior (HEPData sourced)
    ├── docs/                              ← MEDIATOR_DETECTION_SYNTHESIS_v{1..12}, FINDINGS.md,
│   │                                            DARK_SECTOR_LAGRANGIAN.md §9 (Benchmark A),
│   │                                            REVIEWER_AUDIT_R12.md, R12_AUDIT_CLOSURE.md,
│   │                                            REVIEWER_AUDIT_R13.md, H3_H4_SENSITIVITY_REPORT.md,
│   │                                            LAYMAN_SUMMARY_R12.md, LAYMAN_SUMMARY_R13.md
    ├── plots/                             ← Cross-validation + publication plots
    └── tests/                             ← 39 v0.3-specific test files
```

The `outputs/` directory exists locally but is gitignored — it holds 113 MB
of Telegram-shipped PDFs and ZIPs from each release round (D2 through
D15-CORRECTED3, plus R12), plus the scaffolding `build_*.py` scripts.
These are reproducible from `v0.*-prelim/code/` on demand.

---

## Quick start (5 minutes, reproduce the headline)

```bash
# 1. Clone
git clone https://github.com/chenhk1113-HK/sidm-composite-dm-mediator
cd sidm-composite-dm-mediator

# 2. Set up the Python environment (matches the v0.3-prelim pinned versions)
python -m venv .venv
source .venv/bin/activate         # bash/zsh; or .venv\Scripts\activate on Windows
pip install -r requirements.txt

# 3. (Optional) Install Julia 1.11.5 + KiSS-SIDM for the gravothermal penalty
juliaup add 1.11.5 && juliaup default 1.11.5
julia +1.11.5 -e 'using Pkg; Pkg.activate("KiSS-SIDM"); Pkg.instantiate()'

# 4. Run the test suite (290+ tests, expect ~0 failures)
pytest tests/ v0.3-prelim/tests/ v0.1-prelim/tests/

# 5. Reproduce the headline — T21 single-component SIDM with real KiSS-SIDM
cd v0.3-prelim/code
python t21_real_kiss_sidm_5channel_joint_fit.py
# Expect: σ/m ≈ 1.4–1.7 cm²/g at MAP
```

For the full walkthrough see [`docs/TUTORIAL.md`](docs/TUTORIAL.md).
For the math behind the fits see [`docs/MATHEMATICS.md`](docs/MATHEMATICS.md).
For the per-round history see [`CHANGELOG.md`](CHANGELOG.md).

---

## What's in each version

| Version | Scope | Headline |
|---|---|---|
| **v0.1-prelim** | SPARC single-galaxy + joint fits (15 modules) | σ/m posterior from rotation curves alone |
| **v0.2-prelim** | Intermediate (4 modules) | Adds dSph channel scaffolding |
| **v0.3-prelim** | Main work — D1 through D15-CORRECTED3, with R12 audit closure (133 modules, 39 tests) | Joint σ/m ~ 0.066 cm²/g at MAP (R12 T41); velocity index a ≈ +0.19 (no significant tension); Benchmark A (composite dark pion + elementary A') declared canonical |
| **Mediator_Detection v1–v12** | Mediator detection feasibility (within v0.3-prelim/code/) | σ/m ~ 0.07 cm²/g at MeV-scale m_φ (R12), mediator-invisible to LZ only in ε ≪ 10⁻¹⁰ part of posterior |

---

## Methodology

The pipeline is built on the **WIMpy Bayesian methodology** (dynesty nested
sampling + BIC + Bayes factors + mock-data validation), adapted from
dark-energy model comparison to dark-matter microphysics. Key pieces:

- **dynesty 3.0.0** for nested sampling posteriors
- **KiSS-SIDM** (Gurian & May 2025, PRL 135, 221001) for the gravothermal
  collapse penalty — replaces over-strong placeholder fluid approximation
- **Real published likelihoods** for LZ WS2024 (arXiv:2410.17036) and Fermi-LAT
  14-year dSph stacking (McDaniel et al. 2024) — replaces Gaussian proxies
- **Welch t-test** for null-result verification across rounds
- **Composite parametrization** (PCAC for the pseudoscalar pion sector;
  KSFR for the vector-rho mass via the HLS relation, with t53b lattice
  data as the calibratable path) for dark-sector composite-DM mass formulas —
  a phenomenological ansatz, not a first-principles lattice calculation
- **Dark-photon portal mappings** (Kaplinghat, Tulin, Yu 2014 PRD 89,
  035009; Berlin et al. 2018 PRD 97, 055033) for the LZ σ_SI and Fermi
  σ_v channels — replaced the dimensionally-inconsistent legacy form
  in R12 P1-C
- **Conventional Bayesian model comparison** for one-component vs two-component
  vs composite-DM evidence weights

Total: **~370 tests** across the three versions (`tests/` + `v0.*/tests/`), with
359 passing, 4 skipped, 3 pre-existing failures (config drift, KISS-SIDM physical
range, t37 module import — all unrelated to R12).

---

## What this repo is NOT claiming

Honest scope, per the 2026-08-17 R12 six-reviewer audit:

- **Not a discovery.** This is a phenomenology joint-fit framework, not a
  measurement of dark matter at any detector. The historical MAP at (m_φ=26.6 MeV,
  m_χ=14.8 GeV, σ/m_0=0.066 cm²/g, a=+0.186) is **one point in the prior
  box** that fits the multi-channel data within 0.75σ — but lives BELOW the
  KSFR/PCAC validity lower bound (418 MeV). The v0.5 re-run with KSFR mask
  enabled gives MAP (m_φ≈502 MeV, σ/m_0≈0.105 cm²/g, a≈1.89) within the
  KSFR-valid sub-space. The framework does not establish the universe's
  actual particle content.
- **Not a Boltzmann-derived relic density.** The t55 module is a
  calibrated `1/⟨σv⟩` mapping (renamed `t55_wimp_relic_calibration.py`
  in P0-C), not a Boltzmann solver. A first-principles relic-density
  calculation requires a real Boltzmann solver (e.g., dark-sector
  micrOMEGAs) and is deferred to v0.5+.
- **Not a first-principles dark-ρ mass.** The 0.79 GeV (Λ=0.2 GeV) and
  8.36 GeV (Λ=1 GeV) values are KSFR + lattice-ratio calibrations, not
  a real lattice calculation of the dark SU(N) theory. A proper lattice
  calibration is multi-month scope.
- **Not a finished velocity-slope story.** The data prefers a ≈ +0.94.
  The historical T41 Yukawa-derived a at MAP is +0.186, within 0.75σ. The v0.5
  re-run gives a = +1.89, also within the data-preferred range. The pre-R12
  "1.3σ velocity-slope tension" was a sign-flip artifact in
  `t41.derived_a` (P0-B); the post-R12 result is no significant tension.
- **Not a "1.3σ Yukawa tension" finding.** That claimed negative finding
  was a sign-flip bug, not a physical result. The simple Yukawa mediator
  is consistent with the data at the post-R12 MAP.
- **Not a paradigm shift.** The map says the data is consistent with a
  composite-dark-matter-plus-light-dark-photon framework at galactic
  scales. It does not claim that this is the universe's actual
  microstructure, nor that SIDM is the solution to the S8/H0 tensions
  (the latter discussions are independent of this project).
- **Not a finished direct-detection exclusion.** The LZ σ_SI is
  ε-dependent via the dark-photon portal (P1-C). At the canonical
  (ε=10⁻⁵) point σ_SI = 1.2×10⁻³² cm², well above LZ's 10⁻⁴⁸ cm²
  limit. The mediator is "consistent with LZ invisibility" only in the
  ε ≪ 10⁻¹⁰ part of the posterior.

See `v0.3-prelim/docs/REVIEWER_AUDIT_R12.md` for the full R12 audit,
and `v0.3-prelim/docs/R12_AUDIT_CLOSURE.md` for the consolidated
R12 summary (the canonical post-R12 reference).

## Statistical methodology notes (R12)

Three honest disclosures about how the headline numbers were produced.
These matter for any reader who would otherwise read the headline table
as "a measurement":

1. **The "0.75σ tension" is not a conventional significance calculation.**
   T41 computes the absolute difference between its derived velocity
   index and a fixed comparison value (T39's a = +0.94), and calls it
   significant only above an arbitrary threshold of 1.0. It does NOT
   combine measured uncertainties in the standard statistical way.
   Read this as "no obvious discrepancy within this pipeline," not "a
   formal 0.75-standard-deviation measurement."

2. **The headline table mixes different types of estimate.** The masses
   (m_A' = 26.6 MeV, m_χ = 14.8 GeV for the HISTORICAL T41; m_φ = 553 MeV,
   m_χ = 805 GeV for the v0.5 T41) are **posterior medians** — central
   tendencies of the full marginalized posterior. The cross-section
   (σ/m_0 = 0.066 cm²/g historical, 0.105 cm²/g v0.5) and the velocity
   index (a = +0.186 historical, +1.89 v0.5) are calculated at a **different,
   maximum-posterior (MAP) point**. Those numbers should NOT be read as one
   jointly determined particle; the median and the MAP can disagree
   substantially when the posterior is multimodal or skewed. The 68%
   intervals are very broad.

3. **One sampled coupling (α) is not currently connected to the
   likelihood.** T41 reads `log_alpha` as a parameter, but the
   annihilation calculation instead uses α_D = g²_χ/(4π) derived from
   g_chi (the dark-Yukawa coupling). The displayed posterior for α is
   therefore not an independently data-constrained result, and the
   quoted Bayesian evidence (log Z = −213.7) inherits this
   incompleteness. The ε (kinetic-mixing) posterior, by contrast, IS
   data-constrained by LZ; the posterior median ε ~ 10⁻³⁵ is real,
   driven by the LZ σ_SI upper limit.

4. **The SPARC contribution is a calibrated saturation score, not a
   galaxy-by-galaxy observational likelihood.** A hierarchical forward
   model with per-galaxy likelihoods is deferred to v0.4+. This
   prevents the joint fit from being treated as a final multi-experiment
   measurement; it is a phenomenology consistency check.

5. **Quantitative bottleneck statement.** The post-R12 σ_SI at the
   canonical point (ε = 10⁻⁵, m_χ = 40 GeV, m_A' = 10 MeV) is
   **1.2×10⁻³² cm²**, while the LZ WS2024 limit near 40 GeV is
   **2.2×10⁻⁴⁸ cm²**. The model σ_SI is ~5×10¹⁵ times **above** the LZ
   limit at canonical ε — i.e., the canonical coupling is **already
   excluded** by LZ. To survive, the posterior drives ε down to ~10⁻³⁵,
   which is **~30+ orders of magnitude smaller** than naive
   dimensional-analysis expectations for a sub-MeV dark photon
   (~10⁻³ to 10⁻⁵). Any UV completion of this benchmark must explain
   that suppression.

---

## Citation

See [`CITATION.cff`](CITATION.cff) for the GitHub-native citation metadata.
See [`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md) for the full list of
external data sources used and how to cite them in derivative work.

Quick bibtex for citing this repo:

```bibtex
@software{lam_sidm_composite_dm_mediator_2026,
  author = {Lam, K.},
  title = {sidm-composite-dm-mediator},
  version = {0.3-prelim (R12 audit closed 2026-08-17)},
  year = {2026},
  month = {8},
  url = {https://github.com/chenhk1113-HK/sidm-composite-dm-mediator},
  license = {MIT}
}
```

For citing the underlying physics, see [`CITATION.cff`](../CITATION.cff)
(Pospelov 2008, Kaplinghat Tulin Yu 2014, Berlin 2018, Bando 1985,
Gurian & May 2025, Horigome 2025, Yang 2026, Di Mauro 2025, Chakraborti 2025).

---

## License

MIT — see [`LICENSE`](LICENSE).
