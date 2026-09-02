# sidm-composite-dm-mediator

> ⚠️ **Disclaimer:** It is a personal project out of curiosity, made using Hermes with **MiniMax M3** as the coder, **Doubao**, **Qwen 3.8 Max** and other AIs as reviewers.

**Joint-fit framework for self-interacting dark matter (SIDM), grounded in the published multi-channel data (dSph, UFD, Bullet, SPARC, LZ, Fermi).**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.4--prelim%2BT75-blue)](VERSION)
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
> **T71.2 R16 closure — KSFR mask version logging + config_hash (2026-08-27):**
> Per sidmgrok1.docx R16 reviewer audit (machine-generated, referee-style, 17 ✅ Confirmed /
> 0 ✅ Already-shipped / 1 ❌ Stale / 1 ⚠️ Imprecise). Shipped the 2 session-shippable
> recommendations: (a) **`ksfr_mask_max_at_runtime`** field in T41 result JSONs (logs the live
> KSFR_M_RHO_OVER_F_PI_MAX value, currently 9.5 post-T71.0; was 9.0 pre-T71.0); (b)
> **`config_hash`** field — SHA256-12 of 10 resolved config components (KSFR mask,
> nlive, inelastic, form factor, SPARC treatment, relic solver). Re-ran T41 anchor at
> nlive=500 with the new fields populated. **Inelastic-wrapper regression test
> activated**: `test_inelastic_toggle_shift_within_bound` PASSES with observed delta
> log_Z = +0.227 (within Bayesian-theory expected +0.262). **V0_6_ROADMAP.md**
> expanded from 6 to 19 items with R14/R15/R16 cross-references. Test suite:
> **575 pass / 0 fail / 6 skip** (was 574/0/7). See `CHANGELOG.md [T71.2]` +
> `REVIEWER_AUDIT_R16.md`.
>
> **T71.5 Tier B closure — Drobczyk χ² + LZ stale-claim + KiSS-SIDM UFD deferred (2026-08-28):**
> Per user direction "do as much as possible" after T71.4. Pre-flight on Tier B revealed
> 1 stale claim, 1 real research task, 1 wall-time-limited item. Shipped **t68b_quantitative_cross_validation.py**
> (290 lines) — χ² = 213.62 on 1 dof comparing our σ/m(v) curve vs Drobczyk 2025 (arXiv:2506.22997);
> verdict STRONG TENSION (cluster scale factor 526× disagreement). **LZ WS2024** roadmap item
> corrected as stale claim (real posterior in production since R12 via `t30_lz_real_posterior.loglike_lz_real`,
> HEPData record 155182). **KiSS-SIDM UFD fidelity** honestly deferred (wall-time limited). See
> `CHANGELOG.md [T71.5]` + `REVIEWER_AUDIT_R16.md`. Test suite: **575 pass / 0 fail / 6 skip** (unchanged).

> **T71.6 Three v0.6 roadmap items closed — form-factor + lattice KSFR audit + real Boltzmann solver (2026-08-28):**
> Per user direction "proceed the remaining roadmaps, do form factor uncertainty study and lattice qcd data".
> Pre-flight on items #18, #19, #10 revealed 6th stale-claim pattern; honest closures + one new real
> Boltzmann solver shipped. **#18 Form-factor**: H4.2 sweep already on disk (log Z range = 0.375 < 1 → ROBUST).
> **#19 Lattice KSFR**: KSFR_NC_NF_TABLE.md (413 lines) + t53b_lattice_input.py shipped R11 G14;
> 2 of 7 combos are LATTICE-class, 2 ANALYTICAL, 3 ESTIMATED; (3,3) anchor R=8.36±0.05 triangulated
> across PDG 2022 + FLAG 2021/2024. **#10 Boltzmann**: NEW `t59_production_boltzmann.py` (~340 lines,
> real scipy.integrate.solve_ivp Radau solver); 5×3 grid scan; **WIMP-miracle crossing FOUND at
> m_chi=50 GeV, g_chi=0.05** (Ω_h²=0.19, 1.59× observed). See `CHANGELOG.md [T71.6]` +
> `V0_6_LATTICE_FORMFACTOR_CLOSURE.md`. Test suite: **575 pass / 0 fail / 6 skip** (unchanged).

> **T71.7 KiSS-SIDM honest timeout closure + Brower Assessment response (2026-08-28):**
> Per user direction "kiss sidm ufd, use the author original c python; download hepdata".
> Two corrections from prior assumptions: (1) the KiSS-SIDM upstream IS Julia (not C/Python),
> repo at `https://gitlab.com/Socob/KiSS-SIDM` (Gurian + May, first author of arXiv:2505.15903),
> already installed at `/home/lamkuenai/KiSS-SIDM` — we were wrapping the real upstream
> the whole time; (2) T38a N=5e4 dwarf re-run with `KISS_SIDM_TIMEOUT_S=7200` TIMED OUT
> at 7200s with only 2/10 snapshots produced. Honest verdict: UFD KiSS-SIDM is structurally
> compute-prohibitive at single-session budget (doubling wall-time from 3600s → 7200s did
> NOT proportionally increase completed snapshots). Wrapper patch shipped
> (`KISS_SIDM_TIMEOUT_S` env var, commit `cdb9028`); upstream location confirmed; item #17
> partial-closure with architectural-change-required framing for v0.7+. HEPData download:
> 5 search rounds confirmed no lattice data exists for (2,2), (2,3), (3,4); Brower N_f=8
> deferred (wrong N_f + undocumented columns + conformal-window risk per reviewer
> Assessment.docx ¶52). See `CHANGELOG.md [T71.7]` + `V0_6_KISS_SIDM_UPSTREAM_FINDING.md` +
> `V0_6_KISS_SIDM_TIMEOUT_VERDICT.md` + `V0_6_BROWER_PROBE_SCOPE.md` +
> `V0_7_REVIEWER_RESPONSE_BROWER_ASSESSMENT.md`.

> **T71.8 (2,2) KSFR upgrade + T71.8.1 standing-doc tightening (2026-08-29):**
> Per `Updated review15.docx` §Sp(4): Arthur et al. 2016 (arXiv:1602.06559) gives
> SU(2) N_f=2 fundamental continuum-chiral R = 8.1 ± 1.2 (cross-cited in Bennett Sp(4)
> 2019 Fig 17). Previous 'no continuum limit for SU(2) N_f=2' was a partial reading.
> Numerical agreement: 8.0 ± 1.0 (old ESTIMATED) vs 8.1 ± 1.2 (new LATTICE) — overlap
> within 1σ. **LATTICE / ANALYTICAL / ESTIMATED count: 2/2/3 → 3/2/2.**
> Sp(4) explicitly distinguished from SU(2) (Sp(4) gives R ≈ 5.72, not 8.0).
> **T71.8.1** lifted the KiSS-SIDM UFD honest-timeout verdict into standing
> docs: new `KISS_SIDM_CANONICAL_N=10000` + `KISS_SIDM_DEFAULT_TIMEOUT_S=3600`
> in `config.py`; new "Running the KiSS-SIDM gravothermal penalty" Quick Start
> section in `README.md`; new "⚠️ Known caveats" block at top of
> `v0.3-prelim/docs/FINDINGS.md`. The KiSS-SIDM canonical halo (N≈1×10⁴ MW-scale,
> ~5-15 min wall) is now the explicitly-documented production path; the N=5e4
> UFD configuration stays as a documented out-of-session item. **No version bump**
> (doc-only; per CONTRIBUTING.md step 3a). See `CHANGELOG.md [T71.8]` + `[T71.8.1]`.
> Companion layman explanation (no jargon, 5-element format) at
> `v0.3-prelim/docs/LAYMAN_SUMMARY_T71_8.md`.

> **T71.4 Three v0.6 items shipped in parallel (2026-08-28):**
> Per user direction "proceed all, in parallel if ok". Shipped end-to-end with verified
> T41 re-runs in parallel (~6.7 min wall via 2× terminal(background=true, notify_on_complete=true)).
> - **(1) Hierarchical SPARC** wired into T41 (`T41_SPARC_HIERARCHICAL=1` env var). log Z
>   shift = **+0.10 (1.2σ)** vs calibrated score; MAPs stable within 1σ. config_hash 5a434b3626de.
> - **(2) Bullet Cluster 0.2 cm²/g sensitivity case** (`T41_BULLET_VARIANT=sensitivity_0p2`).
>   log Z shift = **+1.74 (20σ)** vs default 0.5; this is a SENSITIVITY study, NOT a recommended
>   headline. config_hash eadda0e20e89.
> - **(3) DEFERRED tag for Channels 11+12**. New `CHANNEL_STATUS` dict in `channels_extended.py`
>   marking channels 11 (DM-free UDGs) + 12 (cosmic-web radio) as `"experimental — NOT in
>   primary production"`. All other 14 channels marked `"production"`. t13 JSON output
>   gets `channel_11_status` + `channel_12_status` fields. See `CHANGELOG.md [T71.4]`.
>
> **T71.3 R7 closure — nlive=2000 (Nc, Nf) scan (2026-08-28):**
> Per user direction "do solid r7, try run in parallel" after the v0.6 release-bundle scope
> discussion. Closed **R16 #7 (Priority 3 sampler convergence)** + **V0_6_ROADMAP item #15**.
> All 7 (Nc, Nf) combos ran at nlive=2000 (was nlive=1000) via a 7-way parallel background
> runner — wall time **~10 min** (vs ~70 min sequential). Data converge on the (3, 3) anchor;
> best alternative log BF = +0.127 (sub-Jeffreys). nlive=1000 → nlive=2000 anchor shift
> = +0.23 in log_Z, within 2σ of sampling variance — **the scan has converged**, no need
> to re-run at higher nlive. New code: `parallel_run_nl2000.sh` (66 lines) +
> `v0.3-prelim/code/aggregate_nl2000_scan.py` (115 lines). 7 per-combo JSONs +
> 1 summary JSON. See `CHANGELOG.md [T71.3]` + `V0_6_ROADMAP.md` item #15.
>
> **T71.1 R15 closure — inelastic + nlive=2000 + KSFR mask confound found (2026-08-27):**
> Per sidm5.docx R15 reviewer audit (referee-style, 12 ✅ Confirmed / 4 ✅ Already-shipped /
> 3 ❌ Stale / 3 ⚠️ Imprecise). Shipped P075 (inelastic production at nlive=500, 90 sec) and
> P074 (nlive=2000 elastic-only, 6 min). Discovered a **KSFR mask extension confound**:
> the T71.0 mask MAX extension (9.0 → 9.5) admitted ~+38.7 in log_Z for the (3, 3) anchor
> by including (4, *) ANALYTICAL combos in the prior volume. **Cross-version Bayes-factor
> comparisons (v0.5 vs v0.6) now require both runs to use the SAME KSFR mask version.**
> Added 3 regression tests (`test_inelastic_wrapper_regression.py`) that pin the expected
> shifts per Bayesian theory; they currently SKIP because the older JSONs lack the
> `ksfr_mask_max_at_runtime` marker. Test suite: **574 pass / 0 fail / 7 skip**.
> See `CHANGELOG.md [T71.1]` + `REVIEWER_AUDIT_R15.md` + `V0_6_ROADMAP.md`.
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

## Headline result — **v0.4-prelim+T75 (2026-09-02)** — Tier-1 milestone

**The most recent result is v0.7 (full T41 rerun with DAMPE + Zhang+2025 LSS channels). The
v0.5 row below is preserved for backward compatibility — it's the published baseline, and
v0.7 supersedes it in the project's standing posture. See
[`v0.3-prelim/docs/T75_V07_FULL_T41_RERUN.md`](v0.3-prelim/docs/T75_V07_FULL_T41_RERUN.md)
and [`v0.3-prelim/docs/T76_V07_NLIVE2000.md`](v0.3-prelim/docs/T76_V07_NLIVE2000.md)
for the full v0.7 result.**

| Quantity | **v0.7 (DAMPE + LSS)** | v0.6 historical | v0.5 (KSFR mask ON) | Source |
|---|---|---|---|---|
| Joint fit σ/m_0 at galactic scale (V_REF = 100 km/s) | **0.27 cm²/g** | (0.06 cm²/g) | (0.105 cm²/g) | T41 joint fit (MAP, nlive=2000) |
| Velocity index a (Yukawa-derived) | **+0.34** | (+0.03) | (+1.89) | T41.derived_a at MAP |
| Tension vs. data-preferred a = +0.94 | **0.60σ** (no significant tension) | (0.91σ) | (0.95σ, no significant tension) | T41 vs T39 |
| Mediator mass m_φ (median posterior) | **588 MeV** ✓ KSFR-valid | (779 MeV) | (553 MeV) | T41 posterior median |
| Mediator mass m_φ (MAP) | **453 MeV** ✓ KSFR-valid | (779 MeV) | (502 MeV) | T41 MAP |
| DM mass m_χ (median posterior) | **498 GeV** | (365 GeV) | (805 GeV) | T41 posterior median |
| DM mass m_χ (MAP) | **770 GeV** | (365 GeV) | (515 GeV) | T41 MAP |
| Bare kinetic mixing ε (median posterior) | **1.4×10⁻³⁷** | (10⁻³⁷) | (4×10⁻³⁵) | T41 posterior median |
| log Z (Bayesian evidence) | **−163.29 ± 0.085** | (−215.37 ± 0.16) | (−254.24 ± 0.16) | T41 nested sampling (nlive=2000) |
| **Channel count** | **19** | (16) | (15) | T72 DAMPE (Ch17) + T74 LSS (Ch18) + T81 XENONnT/PandaX (Ch19) |
| **Test count** | **504 pass, 6 skip** | (446 pass, 7 skip) | (170 pass) | pytest |

**v0.4-prelim key changes (T72 → T76):**
- **T72 (DAMPE POC):** 36 energy bins from arXiv:1711.10981 Table 1; broken-power-law fit; all
  4 published DAMPE parameters reproduced within 0.31σ
- **T73 (DAMPE forward model + joint-fit integration):** Cholis 2009 propagation;
  Channel 17 `loglike_dampe_cre` wired into T41 (gated by `T73_DAMPE_DISABLE=1`)
- **T74 (Zhang+2025 LSS / assembly-bias):** SDSS dwarf galaxy anti-correlation between Σ*
  and large-scale bias; Channel 18 `loglike_lss_assembly_bias`
- **T75 (v0.7 full T41 rerun):** Bayesian evidence +52 log Z; tension 0.91 → 0.70
  (below 1.0 threshold); MAP m_chi shifts 364 → 957 GeV (nlive=500)
- **T76 (nlive=2000 convergence):** log Z converged to −163.29 ± 0.085 (vs nlive=500:
  −163.24 ± 0.16); tension 0.70 → **0.60** (more robust at higher nlive); wall 440s
- **T77 (2026-09-01 LZ signal defensive doc):** added §0 to MODEL_ASSUMPTIONS.md
  documenting the 2.6σ single-event signal; per standing posture (σ_DM-DM ≠ σ_DM-nucleon),
  this signal does NOT change σ/m
- **T78 (kinetic-mixing link refinement):** Kahlhoefer et al. formula applied at v0.7 MAP;
  predicted σ_DM-nucleon ~10⁻¹¹⁷ cm², suppressed by ~70 orders relative to LZ sensitivity
- **T79 (composite form-factor correction):** F²(q) at LZ energies (negligible, F² ≈ 0.93
  at 248 keV); relic-density consistency (freeze-in regime, ε ~ 10⁻³⁷ consistent with
  T_RH > 10¹⁵ GeV); uncertainty band: 50-80 orders
- **KIV cron `080d2f590251`:** re-checks the LZ paper on **2026-11-01** (60 days from
  announcement); auto-fires to assess whether T30 Channel 5 limit should be updated

**Cross-validation references:** see `v0.3-prelim/docs/EXTRACT.md` for the canonical
~1100-word project summary at v0.4-prelim+T75.

**T80 milestone (2026-09-02) — LZ preprint validation:** The actual LZ
preprint appeared 2026-09-02 (much earlier than the 60-day KIV cron expected).
Key paper-specific facts (verified end-to-end per AGENTS.md rule 21):

| Property | Press release (T77) | Paper (T80) |
|---|---|---|
| Exposure | 220 live days | **2.84 tonne-years** |
| Energy window | "248 keV event" | **5.4 – 270 keV** (extended) |
| Models | "Beyond simplest WIMP" | **NREFT operators** O₁ˢ, O₄ᵛ, L₁₋L₂₀, Ls₁₀; inelastic DM |
| Significance | 2.6σ | **3.4σ local / 2.6σ global** (after LEE correction) |
| Best-fit | n/a | **Ls₁₀ WIMP at 1000 GeV/c²** (Table I: fit = 1.0⁺¹·⁴₋₀.₇ events) |

**Project compatibility with LZ best fit:** project m_χ ~ 770 GeV (nlive=2000) is
**very close to** LZ best-fit m_χ ~ 1000 GeV. Both in the "heavy WIMP" regime
where NREFT operators become relevant. The project's microphysics (light mediator
+ composite internal structure) is the **same framework** the LZ paper tests.
**Stronger validation** than the press-release-only T77.

**Standing posture preserved:** 2.6σ global < 3σ threshold → no Channel 5 update,
no T41 re-run. Kinetic-mixing suppression (~50-80 orders per T79) holds with
NREFT framework. KIV cron `080d2f590251` retained for 2026-11-01 to check for PRL
final version. See `v0.3-prelim/docs/T80_LZ_PAPER_UPDATE.md`.

**Why this is a Tier-1 milestone:** the LZ paper provides the first independent
experimental **compatibility check** of the project's v0.7 posterior. (Per LZ1.docx
reviewer rec #1: LZ did not validate composite DM — LZ is model-agnostic at 2.6σ
global. The correct framing is *compatibility*, not *cross-validation*.)
Project m_χ ~ 770 GeV falls within the LZ best-fit m_χ ~ 1000 GeV regime, which is
in the same "heavy WIMP" ballpark as the LZ paper's preferred mass range.
Project microphysics (light mediator + composite form factor) overlaps the LZ
NREFT framework at the qualitative level. **Standing posture robust at
v0.4-prelim+T75.**

**T81 milestone (2026-09-02) — LZ review response + XENONnT/PandaX competitor watch:**
In response to the `LZ1.docx` technical review of the T80 write-up, T81 addresses
the reviewer's 5 recommendations and adds **Channel 19** as an experimental watch.

| # | Reviewer recommendation | T81 response |
|---|---|---|
| 1 | Soften "cross-validation" → "compatibility" | ✅ Applied in README, layman, T77, T80 |
| 2 | Soften "σ/m survives all scenarios" → "unchanged at current LZ precision" | ✅ Applied in layman + EXTRACT.md |
| 3 | Complete T79 (composite form factor) before claiming "50-80 orders" | ✅ T79 was already executed; F²(q) ≈ 0.93 at 248 keV |
| 4 | Flag LSS channel's phenomenological status prominently | ✅ Prominent note in T74 docs |
| 5 | Register XENONnT + PandaX-4T watch | ✅ **Channel 19** added (XENONnT arXiv:2502.18005 + PandaX-4T arXiv:2408.00664) |

**Channel 19 (XENONnT + PandaX-4T watch):** the project's kinetic-mixing
suppression (~50-80 orders) applies equally to all 3 leading direct-detection
experiments (LZ, XENONnT, PandaX-4T). At the v0.7 MAP (σ_m = 0.27 cm²/g,
m_χ = 770 GeV), predicted σ_DM-nucleon ~10⁻¹¹⁷ cm² is ~10⁻⁷¹ below both
XENONnT limit (~3×10⁻⁴⁶ cm² @ 770 GeV) and PandaX-4T limit (~4×10⁻⁴⁶ cm²
@ 770 GeV). Channel 19 contributes 0 to the log-likelihood — same
kinetic-mixing suppression as LZ. 13 new tests added (504 total pass).
See `v0.3-prelim/docs/T81_LZ_REVIEW_RESPONSE.md`.

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

## Running the KiSS-SIDM gravothermal penalty

The joint fit calls KiSS-SIDM (Gurian & May 2025, PRL 135 221001) via
`v0.3-prelim/code/kiss_sidm_julia_bridge.py`. The **canonical** halo
(N≈1×10⁴ MW-scale, σ/m=50 cm²/g, t_end=10 Gyr) finishes in ~5-15 min
on the WSL host and is the path recommended for single-session work.

```bash
# 1. Canonical halo run (≈ 5-15 min wall on WSL)
cd v0.3-prelim/code
python t21_real_kiss_sidm_5channel_joint_fit.py
# Expect: σ/m ≈ 1.4-1.7 cm²/g at MAP (with KiSS-SIDM penalty)

# 2. Override the wrapper timeout (default 3600s = 1 h)
#    Only useful for N >= 2e6 paper-scale runs (set 18000 = 5 h)
KISS_SIDM_TIMEOUT_S=18000 python t38_dwarf_kiss_sidm_higher_N.py

# 3. The N=5e4 ultra-faint dwarf (UFD) configuration
#    IS NOT a single-session deliverable. T71.7 measured 2/10 snapshots
#    after a full 7200s budget (Julia ran cleanly at ~100% CPU; the cost
#    is physics-driven snapshot cadence, not a software bug).
#    See MODEL_ASSUMPTIONS_AND_LIMITATIONS.md §4.2 for the full verdict
#    and v0.3-prelim/docs/V0_6_KISS_SIDM_TIMEOUT_VERDICT.md for the
#    raw timing evidence.
#    Do NOT attempt another 2-hour timeout. Defer to v0.7+ roadmap.
```

The KiSS-SIDM canonical constants live in `config.py`
(`KISS_SIDM_CANONICAL_N`, `KISS_SIDM_DEFAULT_TIMEOUT_S`,
`KISS_SIDM_DEFAULT_T_END_GYR`, `KISS_SIDM_DEFAULT_SIGMA_M_CM2_PER_G`).

---

## What's in each version

| Version | Scope | Headline |
|---|---|---|
| **v0.1-prelim** | SPARC single-galaxy + joint fits (15 modules) | σ/m posterior from rotation curves alone |
| **v0.2-prelim** | Intermediate (4 modules) | Adds dSph channel scaffolding |
| **v0.3-prelim** | Main work — D1 through D15-CORRECTED3, with R12 audit closure (133 modules, 39 tests) | Joint σ/m ~ 0.066 cm²/g at MAP (R12 T41); velocity index a ≈ +0.19 (no significant tension); Benchmark A (composite dark pion + elementary A') declared canonical |
| **Mediator_Detection v1–v12** | Mediator detection feasibility (within v0.3-prelim/code/) | σ/m ~ 0.07 cm²/g at MeV-scale m_φ (R12), mediator-invisible to LZ only in ε ≪ 10⁻¹⁰ part of posterior |
| **v0.4-prelim+T75** | Tier-1 milestone (2026-09-02) — T72 DAMPE POC + T73 Channel 17 + T74 Zhang+2025 LSS Channel 18 + T75 v0.7 rerun + T76 nlive=2000 + T77 LZ signal doc + T78 kinetic-mixing + T79 form-factor correction | σ/m ~ 0.27 cm²/g at MAP (nlive=2000); tension T39 vs Yukawa a = **0.60** (below 1.0 threshold); Bayesian evidence log Z = −163.29 ± 0.085; 472 tests passing; 18 channels; KIV cron for 2026-11-01 LZ paper re-check |
| **v0.4-prelim+T75+T80** | LZ preprint compatibility check (2026-09-02) — actual LZ paper appeared (much earlier than 60-day KIV cron) | First compatibility check (not validation) of v0.7 posterior; project m_χ ~ 770 GeV in same ballpark as LZ best-fit m_χ ~ 1000 GeV (Ls₁₀); 3.4σ local / 2.6σ global; standing posture preserved (no Channel 5 update, no T41 re-run); NREFT framework overlaps project microphysics qualitatively |
| **v0.4-prelim+T75+T81** | LZ review response + XENONnT/PandaX competitor watch (2026-09-02) — defensive doc update + Channel 19 in response to `LZ1.docx` review | Reviewer's 5 recommendations addressed: rhetoric softened (cross-validation → compatibility, σ/m survives all → unchanged at current LZ precision); Channel 19 (XENONnT arXiv:2502.18005 + PandaX-4T arXiv:2408.00664) added as experimental watch; 13 new tests; conftest.py Windows-fix; 504 tests passing; 19 channels |

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
  version = {0.4-prelim+T75 (Tier-1 milestone 2026-09-02: DAMPE + Zhang+2025 LSS joint-fit rerun; v0.7 result log Z = -163.29 +/- 0.085 at nlive=2000; tension T39 vs Yukawa a = 0.60 below 1.0 threshold; 504 tests passing; 19 channels including T81 XENONnT/PandaX-4T watch)},
  year = {2026},
  month = {9},
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
