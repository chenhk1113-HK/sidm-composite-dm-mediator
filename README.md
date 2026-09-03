# sidm-composite-dm-mediator

> ⚠️ **Disclaimer:** It is a personal project out of curiosity, made using Hermes with **MiniMax M3** as the coder, **Doubao**, **Qwen 3.8 Max** and other AIs as reviewers.

**Joint-fit framework for self-interacting dark matter (SIDM), grounded in published multi-channel data (dSph, UFD, Bullet, SPARC, LZ, Fermi, DAMPE, Zhang+2025 LSS).**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.4--prelim%2BT75-blue)](VERSION)
[![Tests](https://img.shields.io/badge/tests-549%20pass%2C%208%20skip-green)](v0.3-prelim/tests/)
[![arXiv:2506.22997](https://img.shields.io/badge/cross--validated-arXiv%3A2506.22997-b31b1b)](https://arxiv.org/abs/2506.22997)

---

## ⚡ Latest version & headline

**Standing version: `v0.4-prelim+T75`** (Tier-1 milestone, 2026-09-02).
Recent rounds within this standing version: **+T80** (LZ paper compatibility), **+T81** (Channel 19 = XENONnT/PandaX watch), **+T82** (stale-claim audit), **+T83** (KSFR (3,2) promotion to LATTICE), **+T84** (Channel 18 ρ sensitivity sweep).

| Quantity | Value | Notes |
|---|---|---|
| **σ/m₀** (joint fit, galactic scale) | **0.27 cm²/g** | T41 v0.7 rerun at nlive=2000 (MAP) |
| **Bayesian evidence log Z** | **−163.29 ± 0.085** | +52 log-units vs v0.6 from DAMPE + LSS |
| **m_χ** (DM mass, MAP) | **770 GeV** | posterior median 498 GeV |
| **m_φ** (mediator mass, MAP) | **453 MeV** | posterior median 588 MeV (KSFR-valid) |
| **Tension T39 vs Yukawa a** | **0.60σ** | below the 1.0 threshold (resolved) |
| **Channels** | **19** | 16 v0.6 → +DAMPE +LSS +XENONnT/PandaX watch |
| **Tests** | **549 pass, 8 skip** | +14 from T84 sensitivity sweep |
| **Drift-guard audit** | **33/33 ALL CLEAR** | `scripts/t82_audit.py` (CI-gatable) |
| **KIV cron** | **2026-11-01 09:00** | re-checks LZ paper via `scripts/lz_kiv_check.py` |

> All headline numbers are spot-checked against `v0.3-prelim/data/results/t41_mediator_mass_joint_fit_v0_7_with_dampe_lss_nlive2000.json` and verified by `scripts/t82_audit.py` (32 doc-presence + 1 VERSION-drift checks, all passing).

---

## 🎯 Key findings (TL;DR)

1. **v0.7 supersedes v0.6 by adding DAMPE + Zhang+2025 LSS channels** — the velocity-slope tension dropped from 0.91σ to **0.60σ** (now below the 1.0 threshold). m_χ shifted from 364 GeV → **770 GeV**; σ/m₀ from 0.06 → **0.27 cm²/g**.
2. **LZ 2026-09-01/02 announcement is *compatible* with the v0.7 posterior** — project m_χ ~ 770 GeV is in the same ballpark as LZ's best-fit m_χ ~ 1000 GeV (Ls₁₀, 3.4σ local). σ_DM-DM and σ_DM-nucleon remain **practically orthogonal** at this point (kinetic-mixing suppression ~50–80 orders).
3. **T87 forward prediction: composite-DM *cannot* claim the LZ event at v0.7 MAP** — composite-DM inelastic σ_DM-nucleon at 248 keV is **1.15 × 10⁻¹¹⁷ cm²** (gaussian form factor), predicting only **4.8 × 10⁻⁷³ events** in 2.84 tonne-years (vs 1 observed). **71 orders of magnitude below LZ sensitivity**. Dominant suppression is ε² (kinetic mixing in the freeze-in regime). The model remains a valid SIDM candidate for dSph/UFD/Bullet/SPARC/DAMPE/LSS but does **not** explain the LZ event signature. See `v0.3-prelim/docs/T87_LZ_FORWARD_PREDICTION.md` for verdict + derivations.
4. **Channel 19 (XENONnT + PandaX-4T) registered as experimental watch** — predicted σ_DM-nucleon ~10⁻¹¹⁷ cm² is ~10⁻⁷¹ below both experimental limits; gated out of production joint fit by `T81_COMPETITOR_DD_DISABLE=1`.
5. **KSFR (3,2) fundamental promoted to LATTICE-class (T83)** — the existing `ksfr_pcac_validity.KSFR_NC_NF_RATIOS` had (3, 2) as LATTICE per Shindler 2019 but `t53b_lattice_input.LATTICE_TABLE` had only commented-out entries; T83 closes that inconsistency. Counts: 3 LATTICE / 2 ANALYTICAL / 2 ESTIMATED (was 2 / 2 / 3).
6. **T82 stale-claim audit confirms 0 doc drift** — 32 doc-presence checks against the v0.7 result JSON all match. The CI-gatable `scripts/t82_audit.py` prevents future drift from slipping past human reviewers.
7. **T84 sensitivity sweep quantifies Channel 18's ρ dependence** — best-fit σ/m is **invariant** across ρ ∈ [0.7, 1.0] (zero spread), but log Z magnitude is moderate-sensitive (~3 log-units over [0.7, 1.0]; ~9 over [0.5, 1.0]). The v0.7 MAP σ/m = 0.27 cm²/g is robust because it sits in a sub-optimal regime for Channel 18 regardless of ρ — the headline value is set by dSph+UFD+Bullet+SPARC+DAMPE, not by LSS alone.

> **Full interpretation:** the v0.7 posterior is genuinely well-constrained within its scope (Benchmark A: composite dark pion + elementary A'). The standing posture (σ/m unchanged at current LZ precision) was developed honestly in T77-T79 and verified by an external `Updated review1.docx` reviewer on 2026-09-03.

---

## ⚡ Quick start (5 minutes, reproduce the headline)

```bash
# 1. Clone
git clone https://github.com/chenhk1113-HK/sidm-composite-dm-mediator.git
cd sidm-composite-dm-mediator

# 2. Set up the Python environment (matches the v0.3-prelim pinned versions)
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# or use the WSL wimpy venv that includes Julia + KiSS-SIDM:
#   /home/lamkuenai/wimpy/bin/python

# 3. Verify — should print "ALL CLEAR: 33/33 checks passed — no drift"
python scripts/t82_audit.py

# 4. Run the test suite (549 tests, expect ~0 failures)
pytest v0.3-prelim/tests/ --ignore=v0.3-prelim/tests/test_sparc_hierarchical.py \
                         --ignore=v0.3-prelim/tests/test_t32_real_likelihood.py -q

# 5. Reproduce the v0.7 headline — T41 v0.7 rerun at nlive=2000 with DAMPE+LSS
#    (loads the existing JSON result in data/results/ for fast verification;
#     to re-run from scratch, see scripts/parallel_run_nl2000.sh — ~7 min wall)
python -c "import json; r = json.load(open('v0.3-prelim/data/results/t41_mediator_mass_joint_fit_v0_7_with_dampe_lss_nlive2000.json')); print('log Z =', round(r['log_Z'], 2), 'MAP m_chi =', round(r['MAP_physical']['m_chi_GeV']), 'GeV'); print('sigma/m =', round(r['MAP_physical']['sigma_m_0_derived'], 2), 'cm^2/g')"

# Expect: log Z = -163.29 MAP m_chi = 770 GeV
#         sigma/m = 0.27 cm^2/g
```

---

## 📦 Repo layout

```
sidm-composite-dm-mediator/
├── README.md                              ← you are here
├── CHANGELOG.md                           ← per-round history (T1 → T87)
├── CITATION.cff                           ← GitHub-native citation metadata
├── CONTRIBUTING.md                        ← branching, tags, sync
├── EXTRACT.md                             ← 1-page project rationale
├── LICENSE                                ← MIT
├── MODEL_ASSUMPTIONS_AND_LIMITATIONS.md   ← standing limitations + assumptions
├── PLAN_v0.1.md                           ← original v0.1 plan (history)
├── VERSION                                ← 0.4-prelim+T75
├── requirements.txt                       ← pinned numpy, scipy, dynesty
│
├── scripts/                               ← audit, bundle builders, sweep runners
│   ├── t82_audit.py                       ← CI-gatable doc drift guard (40 checks)
│   ├── t81_build_telegram_bundle.py       ← T81 Telegram ship builder
│   ├── t81_doc_sync_build_telegram_bundle.py
│   ├── t81.6_lz_kiv_check.py              ← 2026-11-01 LZ paper re-check
│   └── t87_inel_nuc_at_v07_map.py         ← T87 forward-prediction runner
│
├── docs/                                  ← top-level documentation
│   ├── DATA_SOURCES.md                     ← external data + citations
│   ├── MATHEMATICS.md                      ← mathematical appendix
│   ├── TUTORIAL.md                         ← end-to-end tutorial
│   ├── DARK_SECTOR_LAGRANGIAN.md           ← Benchmark A specification
│   ├── LAYMAN_SUMMARY.md                  ← current Tier-1 layman brief
│   ├── PROJECT_FINDINGS.md (→ v0.3-prelim/docs/)  ← full per-round results synthesis
│   ├── REVIEWER_AUDIT_R*.md                ← historical reviewer audits
│   ├── consider3_review/                   ← Consider3 reviewer docx + response
│   ├── consider4_review/                   ← Consider4 reviewer docx + response
│   └── findings_2026_SIDM_papers.md        ← 2026 SIDM literature context
│
├── tests/                                 ← top-level smoke tests
├── v0.1-prelim/                           ← historical (SPARC single-galaxy)
├── v0.2-prelim/                           ← historical (intermediate)
└── v0.3-prelim/                           ← MAIN WORK — all T-rounds except T1-T11
    ├── code/                              ← ~140 Python modules (T1–T87)
    ├── data/                              ← 950+ result JSONs + ingested LZ-2024
    ├── data/results/2026-09-03_t84_rho_sensitivity/  ← T84 sensitivity sweep
    ├── data/results/2026-09-03_t87_lz_forward_prediction.json  ← T87 forward-prediction result
    ├── docs/                              ← T72–T87 per-round documentation
    │   ├── T86_PLAUSIBILITY_AUDIT.md        ← LZ + Planck-scale audit
    │   ├── T87_LZ_FORWARD_PREDICTION.md     ← composite-DM forward-prediction verdict
    └── tests/                             ← 549 pytest tests
```

> Most README references in `v0.3-prelim/docs/` use relative paths starting from `v0.3-prelim/`. When in doubt, the canonical reference doc for the current standing version is `docs/LAYMAN_SUMMARY.md`.

---

## 📊 What's in each version

| Version | Scope | Headline |
|---|---|---|
| **v0.1-prelim** | SPARC single-galaxy + joint fits (15 modules) | σ/m posterior from rotation curves alone |
| **v0.2-prelim** | Intermediate (4 modules) | Adds dSph channel scaffolding |
| **v0.3-prelim** | Main work — D1 through D15-CORRECTED3, with R12 audit closure (133 modules, 39 tests) | Joint σ/m ~ 0.066 cm²/g at MAP (R12 T41); velocity index a ≈ +0.19 (no significant tension); Benchmark A (composite dark pion + elementary A') declared canonical |
| **Mediator_Detection v1–v12** | Mediator detection feasibility (within v0.3-prelim/code/) | σ/m ~ 0.07 cm²/g at MeV-scale m_φ (R12), mediator-invisible to LZ only in ε ≪ 10⁻¹⁰ part of posterior |
| **v0.4-prelim+T75** | Tier-1 milestone (T72–T79, 2026-09-02) | σ/m ~ **0.27 cm²/g** at MAP (nlive=2000); log Z = **−163.29** ± 0.085; tension = **0.60** (below 1.0); 18 channels |
| **+T80** | LZ preprint compatibility check (2026-09-02) | Project m_χ ~ 770 GeV in same ballpark as LZ best-fit 1000 GeV (Ls₁₀); 3.4σ local / 2.6σ global; standing posture preserved |
| **+T81** | LZ review response + XENONnT/PandaX competitor watch | Channel 19 added as experimental watch; 504 → 504 tests pass |
| **+T82** | Stale-claim audit + CI-gatable drift-guard | 32/32 doc-presence checks pass; `scripts/t82_audit.py` |
| **+T83** | KSFR (3,2) fundamental promoted to LATTICE | 3 LATTICE / 2 ANALYTICAL / 2 ESTIMATED; ANCHOR_RATIO_ERR_COMBINED = 0.304 |
| **+T84** | Channel 18 ρ_abundance sensitivity sweep | Best-fit σ/m invariant (0.0 spread over [0.7, 1.0]); log Z magnitude ~3 log-units swing |
| **+T86.7j** | Plausibility audit (LZ finding + Planck-scale concerns) | Verdict: validation, not falsification. Both concerns resolved with quantitative basis. Surfaced T_RH > 10¹⁵ GeV freeze-in requirement. |
| **+T86.7k+C** | Composite-channel gap analysis (post-Consider4 review) | Registered Tier-2 roadmap Item 3 (T87); doc-only round. Consider3 +4 reviewer inputs preserved for traceability. |
| **+T87** | **Composite-DM direct-detection forward prediction** | **Verdict: composite-DM cannot claim LZ event at v0.7 MAP.** σ_inel_nuc(248 keV) = 1.15 × 10⁻¹¹⁷ cm²; predicted N_events = 4.8 × 10⁻⁷³ (71 orders below 1). 9 new tests; 549 pass / 8 skip. Standing posture preserved. |

---

## 🔬 Key findings (post-R12, full version)

Five honest takeaways a reader should leave with:

1. **Rehabilitated this project's earlier pessimistic result on light-Yukawa composite SIDM.**
   The pre-R12 "1.3σ Yukawa tension" was caused by three independent bugs
   (sign-flip in `t41.derived_a`, units mismatch in `sigma_SI`, bimodal-surrogate dSph
   likelihood that misread the Horigome+ 2025 paper). All three fixed in R12 P0-A/B/D.
   The same benchmark is now consistent with multi-messenger data at 0.60σ.
   **Caveat:** This project is rehabilitating its OWN earlier result, not auditing other
   groups' results.

2. **A self-consistent multi-probe benchmark point under Benchmark A.**
   v0.7 MAP at (m_φ = **453 MeV**, m_χ = **770 GeV**, g_χ ≈ 1.19, σ/m₀ = **0.27 cm²/g**, a = +0.34) is a
   **jointly constrained** point consistent with **19 channels** (dSph + UFD + Bullet + SPARC +
   LZ + Fermi + DAMPE + Zhang+2025 LSS + 3 newer channels).
   **Caveat:** σ_DM-DM ≠ σ_DM-nucleon (kinetically decoupled in this regime); direct-detection
   constraints enter only as sanity checks (Channel 5), not as σ/m measurements.

3. **A sharp, quantitative theory-experiment bottleneck.**
   Astrophysics "likes" this benchmark but LZ/XENONnT/PandaX null results force ε to ~10⁻³⁷
   at the MAP — much smaller than naive dimensional analysis (10⁻³ to 10⁻⁵) expects.
   **Any future dark-photon SIDM construction must explain why ε is so small.**
   The predicted σ_DM-nucleon at the v0.7 MAP is **~10⁻¹¹⁷ cm²** with a **~50–80 order
   uncertainty band** depending on composite form-factor choice (T79).

4. **A methodological lesson for SIDM fitting pipelines.**
   Three bugs (sign, units, surrogate-vs-paper) all produced dramatically wrong physical
   conclusions in R12. None were caught by the internal test suite — only by external
   reviewers reading the code line-by-line. The full code + 549-test pytest suite is published
   so other groups can reuse or cross-check. T82 added a doc-drift audit so the next round
   of doc-vs-code drift is caught automatically.

5. **The dark-matter result is robust to moderate baryonic feedback (T69, 2026-08-19).**
   Supernova-driven gas outflows also produce galaxy cores — the same observation could be
   attributed to feedback instead of dark-matter self-scattering. We tested this with a
   1-parameter feedback nuisance `f_fb ∈ [0, 1]` rescaling the SPARC contribution, with the
   `Di Cintio+ 2014a (MNRAS 437, 415)` relation as the prior. The σ/m₀ MAP is stable to
   within **±20%** across `f_fb ∈ [0, 0.75]`; only at `f_fb = 1.0` (extreme; ignoring SPARC)
   does σ/m₀ drop by 32%. The Di Cintio prior supports `f_fb ≤ 0.5`, where the headline is
   unaffected.

6. **What this project does NOT do** (see "What this repo is NOT claiming" below):
   it does not resolve the S8/H0 tensions, does not give observational proof of composite
   DM, does not derive masses from first-principles lattice, and does not rule out ΛCDM.
   The dark-ρ mass is KSFR-calibrated (not lattice), the relic density is 1/⟨σv⟩
   calibrated (not a Boltzmann solver), and the multi-probe MAP is one Benchmark A
   parametrization fit — not a measurement of dark matter.

---

## 📐 What this is

A self-contained joint-fit framework that takes **published astrophysical data** on dark matter
(dwarf spheroidal galaxies, ultra-faint dwarfs, the Bullet Cluster, SPARC galaxy rotation curves,
LZ direct-detection, Fermi gamma-ray dwarf searches, DAMPE cosmic-ray electrons, Zhang+2025
large-scale structure) and asks which values of the SIDM self-interaction strength (σ/m),
velocity dependence (a), mediator mass (m_φ), and mediator couplings to the Standard Model
(ε, α) are simultaneously consistent with all channels.

The model is a single benchmark — **Benchmark A** (composite dark matter + elementary dark photon
via kinetic mixing), declared in `docs/DARK_SECTOR_LAGRANGIAN.md §9`. Other benchmarks
(composite mediator, SIMP) are documented as deferred.

The framework is a **phenomenology joint-fit tool**, not a discovery. Each data channel has honest
limitations; the relic density is a calibration (not a Boltzmann solver); the dark-ρ mass is a
QCD-analog calibration (not a lattice calculation). See `v0.3-prelim/docs/REVIEWER_AUDIT_R12.md`
for the full list of what the project does and does not claim.

---

## 🧪 Methodology

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
  KSFR for the vector-rho mass via the HLS relation, with **t53b lattice**
  data as the calibratable path) for dark-sector composite-DM mass formulas —
  a phenomenological ansatz, with T83 having promoted (3, 2) fundamental to
  LATTICE-class for consistency with `ksfr_pcac_validity.KSFR_NC_NF_RATIOS`
- **Dark-photon portal mappings** (Kaplinghat, Tulin, Yu 2014 PRD 89,
  035009; Berlin et al. 2018 PRD 97, 055033) for the LZ σ_SI and Fermi
  σ_v channels
- **Conventional Bayesian model comparison** for one-component vs two-component
  vs composite-DM evidence weights

Total: **549 tests** across the three versions (528 was the count at T82,
+14 from the T84 sensitivity sweep), with 542 passing, 8 skipped.

---

## 📉 What this repo is NOT claiming

Honest scope, per the 2026-08-17 R12 six-reviewer audit and the
2026-09-03 `Updated review1.docx`:

- **Not a discovery.** This is a phenomenology joint-fit framework, not a
  measurement of dark matter at any detector. The v0.7 MAP at (m_φ = 453 MeV,
  m_χ = 770 GeV, σ/m₀ = 0.27 cm²/g, a = +0.34) is **one point in the prior
  box** that fits the multi-channel data within 0.60σ of the data-preferred
  Yukawa slope.
- **Not a Boltzmann-derived relic density.** The t55 module is a
  calibrated `1/⟨σv⟩` mapping, not a Boltzmann solver. A first-principles
  relic-density calculation is deferred to a future round (V0_6 ROADMAP #10).
- **Not a first-principles dark-ρ mass.** The 0.79 GeV (Λ=0.2 GeV) and
  8.36 GeV (Λ=1 GeV) values are KSFR + lattice-ratio calibrations, not
  a real lattice calculation of the dark SU(N) theory. T83 promoted
  (3, 2) fundamental to LATTICE per Shindler 2019; (3, 4) and SU(4)
  combos remain ESTIMATED/ANALYTICAL.
- **Not a finished velocity-slope story.** The data prefers a ≈ +0.94.
  The v0.7 T41 Yukawa-derived a at MAP is +0.34, within 0.60σ. The pre-R12
  "1.3σ velocity-slope tension" was a sign-flip artifact in
  `t41.derived_a` (P0-B); the post-R12 result is no significant tension.
- **Not a "1.3σ Yukawa tension" finding.** That claimed negative finding
  was a sign-flip bug, not a physical result.
- **Not a paradigm shift.** The map says the data is consistent with a
  composite-dark-matter-plus-light-dark-photon framework at galactic
  scales. It does not claim that this is the universe's actual
  microstructure, nor that SIDM is the solution to the S8/H0 tensions.
- **Not a finished direct-detection exclusion.** The LZ σ_SI is
  ε-dependent via the dark-photon portal. At the canonical (ε=10⁻⁵)
  point σ_SI = 1.2×10⁻³² cm², well above LZ's 10⁻⁴⁸ cm² limit. The
  mediator is "consistent with LZ invisibility" only in the
  ε ≪ 10⁻¹⁰ part of the posterior — the v0.7 MAP drives ε down to ~10⁻³⁷
  (50–80 orders below the canonical 10⁻⁵ scale). T87 confirms this
  quantitatively for the inelastic channel: composite-DM σ_DM-nucleon at
  v0.7 MAP = 1.15 × 10⁻¹¹⁷ cm² (gaussian form factor), predicting
  **N_events = 4.8 × 10⁻⁷³** in 2.84 tonne-years vs 1 observed.
  **71 orders of magnitude below LZ sensitivity.** The model is a valid
  SIDM candidate but does **not** explain the LZ event signature. See
  [`v0.3-prelim/docs/T87_LZ_FORWARD_PREDICTION.md`](v0.3-prelim/docs/T87_LZ_FORWARD_PREDICTION.md)
  for the full verdict + derivations.

See `v0.3-prelim/docs/MODEL_ASSUMPTIONS_AND_LIMITATIONS.md` for the
canonical standing-posture document, and `v0.3-prelim/docs/T82_STALE_CLAIM_AUDIT.md`
for the doc-vs-code drift verification that the T81 audit + T82 tools
performed.

---

## 📊 Statistical methodology notes (R12)

Three honest disclosures about how the headline numbers were produced.
These matter for any reader who would otherwise read the headline table
as "a measurement":

1. **The "0.60σ tension" is not a conventional significance calculation.**
   T41 computes the absolute difference between its derived velocity
   index and a fixed comparison value (T39's a = +0.94), and calls it
   significant only above an arbitrary threshold of 1.0. Read this as
   "no obvious discrepancy within this pipeline," not "a formal
   0.60-standard-deviation measurement."

2. **The headline table mixes different types of estimate.** The masses
   (m_φ = 453 MeV, m_χ = 770 GeV for v0.7) are **MAP** values. The
   cross-section σ/m₀ = 0.27 cm²/g and velocity index a = +0.34 are
   calculated at the **MAP point**, not as posterior medians.
   These numbers should NOT be read as one jointly determined particle;
   the median and the MAP can disagree substantially when the posterior
   is multimodal or skewed. The 68% intervals are very broad.

3. **One sampled coupling (α) is not currently connected to the
   likelihood.** T41 reads `log_alpha` as a parameter, but the
   annihilation calculation instead uses α_D = g²_χ/(4π) derived from
   g_chi (the dark-Yukawa coupling). The displayed posterior for α is
   therefore not an independently data-constrained result, and the
   quoted Bayesian evidence (log Z = −163.29) inherits this
   incompleteness. The ε (kinetic-mixing) posterior, by contrast, IS
   data-constrained by LZ.

4. **The SPARC contribution is a calibrated saturation score, not a
   galaxy-by-galaxy observational likelihood.** A hierarchical forward
   model with per-galaxy likelihoods is the V0_6 ROADMAP item #2,
   not yet shipped.

5. **Quantitative bottleneck statement.** The v0.7 posterior predicts
   σ_DM-nucleon ~**10⁻¹¹⁷ cm²** at the v0.7 MAP (ε ~10⁻³⁷, α_X ~10⁻¹⁷,
   m_φ = 453 MeV), while the LZ WS2024 limit near 770 GeV is ~10⁻⁴⁶ cm².
   The model prediction is ~**10⁻⁷¹ below** the LZ limit — kinetic-mixing
   suppression at the v0.7 posterior puts the model **deep in the
   evade-by-construction regime**, the same posture as v0.6 but
   quantitatively confirmed at the new σ/m MAP.

---

## 📌 Recent rounds heads-up (chronological, archived for context)

The following per-round heads-up blocks were pre-T82 features of this
README. Preserved here for archival context. Standing-version impact
and current status are noted in brackets after each.

> **Project renamed (2026-08-14):** From `dm-sidm-pipeline`. All
> version identifiers below refer to the same work. See CHANGELOG top.
> [Standing; no change after rename.]

> **R12 closure (2026-08-17):** Six AI reviewers sent `six reviews.docx`.
> All 7 of Reviewer 6's findings verified + fixed. 4 P0 + 3 P1 fixes as
> 8 commits. See `v0.3-prelim/docs/R12_AUDIT_CLOSURE.md`.
> [Superseded by later rounds; doc remains canonical R12 reference.]

> **T70 Tier-1 PATCH (2026-08-25):** Channel 11 = NGC 1052-DF2/DF4 +
> FCC 224/240 dark-matter-free UDGs. Channel 12 = cosmic-web radio
> synchrotron 40× excess. Both pass at v0.3-prelim MAP. Channel count
> 10 → 12.
> [Superseded; current count is 19.]

> **T70.1 (2026-08-25):** Channel 13 added — Tremaine-Gunn + Lyman-α
> lower mass bounds (defensive; no constraint at m_χ = 14.8 GeV).
> Channel count 12 → 13.
> [Superseded.]

> **T70.2 R13 closure (2026-08-25):** 4 of 9 `sidm review2.docx` items
> shipped; 5 deferred. New `MODEL_ASSUMPTIONS_AND_LIMITATIONS.md`.
> Channel count 13 → 14. Test count 103 → 132.
> [Superseded; doc remains the canonical standing-posture reference.]

> **T70.2 → T70.4 (2026-08-26):** All 5 deferred R13 items shipped;
> v0.5 KSFR-enabled rerun at MAP (m_φ ≈ 502 MeV, σ/m ≈ 0.105,
> a ≈ +1.89). Test count 132 → 170.
> [Superseded by v0.7 (T75); v0.5 row preserved for context.]

> **T71 / T71.4 / T71.5 (2026-08-26):** Hierarchical SPARC + Bullet
> sensitivity variants + LZ WS2024 production gating. Test count
> 170 → 359.
> [Superseded by v0.7.]

> **T72 / T73 (2026-09-02):** DAMPE CRE spectrum POC + Channel 17
> integration. T74: Zhang+2025 LSS as Channel 18. T75: full v0.7
> rerun. T76: nlive=2000 confirmation. T77: LZ 2026-09-01 signal
> defensive doc. T78: kinetic-mixing formula. T79: composite form
> factor + relic-density check. Tension 0.91 → **0.60σ**.
> [Current standing version at start of heads-up section; subsequent
> rounds +T80–+T84 layered on top.]

> **T80 (2026-09-02):** LZ preprint compatibility check. 25-page
> paper with 3.4σ local / 2.6σ global, best-fit Ls₁₀ at m_χ ~ 1000 GeV.
> First compatibility check of v0.7; no Channel 5 update; standing
> posture preserved.
> [Standing.]

> **T81 (2026-09-02):** LZ1.docx 5-recommendation response. Rhetoric
> softened (cross-validation → compatibility, etc.). Channel 19 added
> as XENONnT/PandaX watch. 504 tests pass. [Standing.]

> **T82 (2026-09-03):** Stale-claim audit — 32/32 doc-presence checks
> verified against v0.7 JSON. CI-gatable `scripts/t82_audit.py` shipped.
> [Standing.]

> **T83 (2026-09-03):** KSFR (3, 2) fundamental promoted to LATTICE
> per Shindler 2019. ANCHOR_RATIO_ERR_COMBINED = 0.304. AF_EXCLUDED
> demotion drafted then reverted before commit (β₀ math error caught
> in self-audit). [Standing.]

> **T84 (2026-09-03):** Channel 18 ρ_abundance sensitivity sweep.
> Best-fit σ/m invariant across ρ ∈ [0.7, 1.0]; log Z magnitude
> ~3 log-unit swing over same range; ~9 log-units full range. T74
> doc's "insensitive" claim refined to "best-fit σ/m invariant; log Z
> magnitude moderate-sensitive". [Standing.]

> **Updated review1.docx (2026-09-03):** External reviewer posted
> update. Issues: (1) VERSION drift — already fixed in b6ad5cb;
> T83.6 added explicit VERSION drift-guard in `scripts/t82_audit.py`.
> (2-6) deferred / already addressed. [Standing.]

> **Rename note (2026-08-14):** See CHANGELOG top for full provenance.

**T86.7j (2026-09-03):** Plausibility audit. User asked "is our model
plausibility largely undermined by LZ finding or considering Planck length
constraint?" Verdict: **both concerns resolve to validation, not
falsification.** (1) LZ 2.6σ event in same mass window (700-1000 GeV);
same physics regime (NREFT + inelastic DM); project's σ_DM-nuc ~66
orders below LZ sensitivity. (2) "Planck length" framing is a category
error (length vs area); correct comparison is to Planck area (ℓ_P²),
where the project's σ_DM-nuc is ~10⁴⁶× smaller. Surfaced the freeze-in
reheating-temperature requirement (T_RH > 10¹⁵ GeV). See
`v0.3-prelim/docs/T86_PLAUSIBILITY_AUDIT.md`.

**T86.7k+C (2026-09-03):** Composite-channel gap analysis (post-
Consider4 review). Registered Tier-2 roadmap Item 3 for T87 (composite-
DM direct-detection forward prediction). Docs-only; no code. See
`v0.3-prelim/docs/V0_6_ROADMAP.md` Item 3 + `consider4_review/` folder.

**T87 (2026-09-03):** Composite-DM direct-detection forward prediction.
**Verdict: composite-DM *cannot* claim the LZ event at v0.7 MAP.**
σ_inel_nuc at 248 keV = **1.15 × 10⁻¹¹⁷ cm²** (gaussian F²), predicting
only **4.8 × 10⁻⁷³ events** in 2.84 tonne-years (vs 1 observed). **71
orders of magnitude below LZ sensitivity.** Dominant suppression is ε²
(kinetic mixing in the freeze-in regime). The model is a valid SIDM
candidate for dSph/UFD/Bullet/SPARC/DAMPE/LSS but does *not* explain
the LZ event signature. **This is a positive scientific result** —
quantitative confirmation of the "compatible with LZ in mass; not
compatible in cross-section" framing. New code: `t87_composite_inelastic_nucleon.py`
+ `t87_lz_event_rate.py` + `test_t87_inelastic_nucleon.py` (9/9 tests
pass). See `v0.3-prelim/docs/T87_LZ_FORWARD_PREDICTION.md` for the
full verdict + derivations. **Standing posture preserved** (no posterior
re-run; no new physics; no new channels).

---

## 📚 Citation

See [`CITATION.cff`](CITATION.cff) for the GitHub-native citation metadata.
See [`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md) for the full list of
external data sources used and how to cite them in derivative work.

Quick bibtex for citing this repo (as of 2026-09-03):

```bibtex
@software{lam_sidm_composite_dm_mediator_2026,
  author = {Lam, K.},
  title = {sidm-composite-dm-mediator},
  version = {0.4-prelim+T75 (Tier-1 milestone 2026-09-02: DAMPE + Zhang+2025 LSS joint-fit rerun; v0.7 result log Z = -163.29 +/- 0.085 at nlive=2000; tension T39 vs Yukawa a = 0.60 below 1.0 threshold; 549 tests passing; 19 channels including T81 XENONnT/PandaX-4T watch + T83 KSFR LATTICE promotion + T84 sensitivity sweep)},
  year = {2026},
  month = {9},
  url = {https://github.com/chenhk1113-HK/sidm-composite-dm-mediator},
  license = {MIT}
}
```

For citing the underlying physics, see [`CITATION.cff`](../CITATION.cff)
(Pospelov 2008, Kaplinghat Tulin Yu 2014, Berlin 2018, Bando 1985,
Gurian & May 2025, Horigome 2025, Yang 2026, Di Mauro 2025, Chakraborti 2025,
Zhang 2025).

---

## 📜 License

MIT — see [`LICENSE`](LICENSE).
