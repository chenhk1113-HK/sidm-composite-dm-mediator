# SIDM dark-matter pipeline — project plan v0.1 (2026-08-10)
#
# Note 2026-08-14: project renamed to `sidm-composite-dm-mediator`. The
# content below is preserved verbatim — it describes the original v0.1 plan
# that established the project structure.

## What this is

A separate Bayesian model-comparison pipeline for **self-interacting dark matter (SIDM)** cross-section constraints. Uses the **WIMpy methodology** (dynesty nested sampling + BIC + BMA) but applies it to **dark-matter microphysics** rather than dark-energy macro-evolution.

The WIMpy project asks: "Is dark energy a constant, or does it evolve?" — answered with a Bayes-factor comparison of dark-energy models.

**This project asks: "Is dark matter collisionless, or does it self-scatter?"** — answered with a Bayes-factor comparison of dark-matter halo profiles on rotation-curve + dwarf-kinematic + cluster-lensing data.

## Why a separate project (not a WIMpy extension)

WIMpy's domain is **dark-energy model comparison** — its headline result
(dynamic DE > LCDM at B=12-14) is a statement about w₀ evolution. SIDM
is a **dark-matter** question with different datasets (galactic dynamics
and gravitational lensing, not BAO/SNe), different parameters
(σ/m cross-section, not w₀), different systematics (baryonic feedback,
not photo-z). Folding SIDM into WIMpy would either:

1. Add a model that competes on the wrong axis (no overlap with the
   dark-energy likelihood), giving a meaningless Bayes factor, OR
2. Force a hybrid pipeline that no single reviewer can evaluate cleanly.

Separation keeps each project's Bayes factors interpretable and the
scientific claims defensible.

## Scope (v0.1 — this plan)

Four observational channels, in priority order:

1. **SPARC rotation curves** — galactic-scale SIDM signatures
2. **Milky Way dwarf spheroidal (dSph) stellar kinematics** — most sensitive
3. **Ultra-faint dwarf (UFD) stellar cores** — most extreme
4. **Bullet Cluster (JWST 2025)** — cluster-scale upper limit

The headline question: **does SIDM (σ/m > 0) win over CDM (σ/m = 0) at galactic scales, dwarf scales, or both?**

## Data sources

| Channel | Dataset | Where | Size | Status |
|---|---|---|---|---|
| Channel 1 | SPARC | astroweb.case.edu/SPARC | 175 galaxies, ~120 KB zip | Free, public, cite Lelli+2016c |
| Channel 2 | MW dSph kinematics | Multiple papers — see below | ~9 galaxies, ~few MB JSON | Cite Correa+2021 MNR 503, 920 |
| Channel 3 | UFD stellar cores | Sánchez-Almeida+ 2024 ApJL 973 L15 | Sample table | Already published as Table |
| Channel 4 | Bullet Cluster JWST | Cha+ 2025 ApJ 987 L15 (arXiv 2503.21870) | σ/m < 0.5 cm²/g upper limit | Public, in literature |

**Channel 1 — SPARC:**
- Master file: `SPARC_Lelli2016c.mrt` (28 KB)
- Mass models: `MassModels_Lelli2012016c.mrt` (270 KB)
- Rotation curves: `Rotmod_LTG.zip` (111 KB)
- Database zip: `sparc_database.zip` (120 KB)
- All from `https://astroweb.case.edu/SPARC` or Zenodo mirror `10.5281/zenodo.16284118`

**Channel 2 — MW dSph:** We will NOT re-derive stellar kinematics. The
Correa+ 2021 sample (9 galaxies: Draco, Ursa Minor, Sculptor, Fornax,
Carina, Sextans, Leo I, Leo II, Sagittarius) is the standard literature
set. We will:
- Tabulate v_max and half-light radii from the published tables
- Build a simple Jeans-equation likelihood (or use tabulated
  σ_los(σ/m) curves from Correa+ 2021 Fig. 4)
- Compare against σ/m = 0 CDM prediction from NFW expectation

**Channel 3 — UFD:** Use the Sánchez-Almeida+ 2025 A&A table directly
(published constraint: σ/m = 10^0.92 ± 1.37 cm²/g). We replicate the
table, then build an independent Bayesian aggregation that does NOT
assume the Yang+2024 veff = 0.64 v_max prescription.

**Channel 4 — Bullet Cluster:** Use the Cha+ 2025 published constraint
σ/m < 0.5 cm²/g (95% CL). This is a published upper limit, not a
Bayes factor; we incorporate it as a one-sided prior on the joint fit.

## Models

Four nested models, increasing in complexity (matches WIMpy's
LCDM → w0waCDM → tCPL → Quintom philosophy):

| Model | DM type | Free params | Hypothesis |
|---|---|---|---|
| **CDM-NFW** | Cold collisionless | 5 | Standard ΛCDM halo |
| **SIDM-Burkert** | Self-interacting, cored | 6 (+ σ/m) | SIDM with constant cross-section |
| **SIDM-vdep** | Self-interacting, velocity-dependent | 7 (+ σ/m, v_ref) | σ/m = σ_ref × (v/v_ref)^-a |
| **SIDM-2comp** | Two-component (mass segregation) | 8 | Yang+ 2025 PRD, Purple Mountain |

For each channel, fit each model. Compute Bayes factor B_SIDM/CDM
per channel. Then compute model-averaged σ/m with BMA weights.

## Bayesian methodology (lifted 1:1 from WIMpy)

- **Sampler**: `dynesty` nested sampling (same package WIMpy uses,
  in `/home/lamkuenai/wimpy/bin/python` on the WSL venv).
- **Evidence integration**: dynamic nested sampling, nlive = 200
  (matches WIMpy v4b baseline), dlogz = 0.10.
- **Model comparison**: BIC + BMA weights (matches WIMpy's BIC+BMA
  aggregator at `wimpy_results/scripts/test33_model_averaging.py`).
- **Honest uncertainty**: Welch's t-test for σ/m differences across
  the 4 channels (matches WIMpy's v7 vs v8 Welch t-test convention).
- **Pre-shipping verification**: PDF-JSON consistency check
  (15/15 PASS pattern from v2.2 PATCH).

## Proposed test plan

| Test | What it measures | Output | WIMpy analog |
|---|---|---|---|
| **T1** | Single-galaxy SPARC fit, CDM-NFW | Per-galaxy log Z, σ_post | Test 30 single-model |
| **T2** | Single-galaxy SPARC fit, SIDM-Burkert | Per-galaxy log Z, σ_post | Test 30 single-model |
| **T3** | Joint 175-galaxy SPARC fit, all 4 models | log Z per model + BIC + BMA | Test 33 model averaging |
| **T4** | Per-channel Bayes factor (galaxy vs dSph vs UFD vs cluster) | B_SIDM/CDM per channel | Test 34 cross-test |
| **T5** | Mock-data validation challenge (inject known σ/m, recover) | σ/m within Xσ of input | WIMpy v2.1 mock-data pattern |
| **T6** | Sensitivity to SPARC priors (Υ_d, inclination, distance) | Δlog Z | WIMpy v2.2 systematic bands |
| **T7** | Combined 4-channel joint fit | Joint log Z + BMA σ/m | (new — combines all datasets) |

**Honest scope check**: T7 (combined 4-channel joint fit) is the
publishable endpoint. It's NOT a 4-week project. Estimated work:

- T1-T3 (SPARC single-galaxy + joint): 2-4 weeks
- T4 (per-channel B): 1 week (reuses T1-T3 outputs)
- T5 (mock-data validation): 1 week (mandatory before shipping)
- T6 (sensitivity): 1 week (mandatory before shipping)
- T7 (joint): 2 weeks (custom likelihood, not just aggregation)

**Total: 7-10 weeks for v0.1 PATCH** if SPARC data + WIMpy venv
infrastructure can be reused directly.

## Infrastructure reuse from WIMpy

- **Python venv**: `/home/lamkuenai/wimpy/bin/python` already has
  dynesty + numpy + scipy. **Do NOT create a new venv** unless we
  hit a missing-package wall.
- **Bayes factor aggregator pattern**: copy `test33_model_averaging.py`
  from WIMpy and adapt the JSON schema (replace w₀/Bayes factors with
  σ/m/Bayes factors).
- **PDF + bundle ship pattern**: reuse the `_build_pdf.py` + ZIP
  builder from WIMpy, adapt the cover for SIDM-specific numbers.
- **Project-doc structure**: same `code/data/docs/plots/logs/notes/`
  convention (per the project-doc structure rule).
- **Git workflow**: same `wip/v0.1` branch pattern with VC framework.

## Reference papers (verified, July-Aug 2025 publications)

**Channel 1 (SPARC + SIDM):**
- Li+ 2020 ApJS 247, 31 — "A Comprehensive Catalog of Dark Matter
  Halo Models for SPARC Galaxies" — 175 galaxies, 7 profiles, MCMC.
  **The blueprint for T1-T3.**
- Lelli+ 2016c AJ 152, 157 — SPARC master paper. **Cite for data.**
- Kraken+ 2024 (arXiv 2401.10202) — "SPARC galaxies prefer Dark Matter
  over MOND" — Bayesian, dynesty, methodology template.

**Channel 2 (MW dSph):**
- Correa+ 2021 MNR 503, 920 — "Constraining velocity-dependent
  SIDM..." — 9 MW dSph galaxies, standard methodology.
- arXiv 2503.13650 (Mar 2025) — "Stringent Constraints on SIDM
  Using Milky-Way Satellite Galaxies Kinematics" — **most recent,
  gravothermal core-collapse + bimodal posterior.** Blueprint for T4.

**Channel 3 (UFD):**
- Sánchez-Almeida+ 2024 ApJL 973 L15 — "Stellar Distribution in
  UFDs Suggests Deviations from Collisionless CDM".
- Sánchez-Almeida+ 2025 A&A — follow-up with σ/m = 10^0.92 ± 1.37 cm²/g.

**Channel 4 (Bullet Cluster):**
- Cha+ 2025 ApJ 987 L15 (arXiv 2503.21870) — "A High-Caliber View
  of the Bullet Cluster through JWST Strong and Weak Lensing".
  **σ/m < 0.5 cm²/g (95% CL) — tightest cluster constraint.**
- Eckert+ 2022 A&A — σ/m < 0.19 cm²/g (X-COP clusters, slightly older).

## What this plan does NOT cover (deferred)

- **Two-component SIDM (mass segregation)** — Yang+ 2025 PRD
  Purple Mountain model. Add as v0.2 if T3 results are ambiguous.
- **Direct detection cross-checks** (XENONnT, LZ) — completely separate
  pipeline. Note that WIMpy Track 1 (LZ/DM direct detection) already
  exists at `wimpy_results/scripts/sweep_vs_LZ*.py` and could be
  cross-linked in v0.2.
- **Cosmological N-body simulations** — we use analytic/semi-analytic
  SIDM profiles (Burkert + velocity-dependent), not cosmological
  sims. Adds 2-3 months of compute + validation if added.
- **Fermi GCE (Channel 5 from the dark-glueball doc)** — completely
  separate gamma-ray likelihood. **This is the dark-glueball-specific
  channel and is OUT of scope for v0.1.** Add in v1.0 if a downstream
  review demands it.

## Risks (honest)

1. **CDM vs SIDM degeneracy**: at fixed v_max, both NFW (with baryonic
   feedback) and SIDM produce cored profiles. A pure-rotation-curve
   analysis cannot distinguish them. Mitigation: include T5 mock-data
   validation where σ/m is INJECTED into a SIDM profile and
   RECOVERED. If the recovery is degenerate, declare it as a finding.

2. **Baryonic feedback confounders**: supernovae-driven feedback also
   cores NFW halos. The "core vs cusp" question is NOT a clean SIDM
   vs CDM test. Mitigation: include T6 sensitivity to baryonic-feedback
   prescription (match Katz+ 2016 or Li+ 2020 methodology).

3. **Velocity-dependent cross-section model-dependence**: the
   σ/m = σ_ref × (v/v_ref)^-a form is a parametrization, not a
   microphysical prediction. Different microphysical models (Yukawa,
   Born-Infeld, atomic-dark-matter) map to different (σ_ref, a)
   values. Mitigation: T4 tests the velocity-dependent model and
   reports the inferred σ_ref for the velocity range of each channel.

4. **Bullet Cluster upper limit may be in tension with galactic
   σ/m constraints.** The literature shows σ/m ~ 0.5-2 cm²/g at
   galactic scales vs σ/m < 0.5 cm²/g at cluster scales. This
   "scale tension" is itself a finding — it's the SMOKING GUN for
   velocity-dependent models. Mitigation: report the scale-tension
   finding in T4, don't paper over it.

5. **Compute budget**: SPARC single-galaxy fit is fast (~30 s). 175
   galaxies × 4 models = 700 fits × 30 s = ~6 hours. Joint fit (T3)
   needs custom likelihood; maybe 1-2 h. Total v0.1: ~10 h compute.

## Deliverable shape (v0.1 PATCH)

Following the WIMpy convention:
- `code/` — Python scripts (1 per test + aggregators)
- `data/` — per-fit JSON + posterior .npy
- `docs/` — README, CHANGELOG, FINDINGS, REVIEWER notes
- `plots/` — rotation-curve overlays + Bayes-factor corner plots
- `logs/` — dynesty live logs
- `notes/` — decision notes (especially the T7 joint-fit decisions)

Git branch `wip/v0.1`, tag `v0.1-prelim` after T5 passes, tag
`v0.1-final` after mock-data validation + sensitivity both pass.

## Why the WIMpy methodology transfers cleanly

WIMpy answers "is the dark-energy equation-of-state w₀ ≠ -1?" via
dynesty nested sampling on (H(z), μ(z)) data. SIDM-pipeline answers
"is the dark-matter cross-section σ/m ≠ 0?" via dynesty nested
sampling on (v(r), σ_los) data.

Both pipelines share:
- Evidence integration via nested sampling
- Bayes factor comparison via BIC/BMA
- Honest uncertainty quantification (Welch t-test for cross-channel
  comparisons)
- Pre-shipping verification (mock-data validation, PDF-JSON consistency)
- Per-test JSON schema (log Z, posterior samples, per-channel diagnostics)

The differences are domain-specific (cosmology vs galactic dynamics),
not methodological.

## What I recommend

**Proceed in 3 phases:**

1. **Phase 1 (T1-T3, 2-4 weeks):** SPARC single-galaxy fits + joint
   175-galaxy fit. Ship as v0.1-prelim. Answer: "Does SIDM beat CDM
   on the SPARC rotation-curve ensemble?"

2. **Phase 2 (T4-T6, 3 weeks):** Add dSph + UFD + Bullet Cluster
   per-channel Bayes factors + mock-data + sensitivity. Ship as
   v0.1-final. Answer: "Does SIDM beat CDM at galactic, dwarf, and
   cluster scales — and is there scale tension?"

3. **Phase 3 (T7, 2 weeks):** Joint 4-channel fit. Ship as v0.2.
   Answer: "What is the model-averaged σ/m with full systematics?"

**Skip for now:** two-component SIDM (Yang+ 2025), direct detection
cross-check, Fermi GCE channel. These belong in v1.0+.

**Decision point after Phase 2:** if the headline B_SIDM/CDM across
channels is consistent (no scale tension), publish as v0.1-final and
move to Phase 3. If there's significant scale tension (galactic σ/m
>> cluster σ/m), the headline becomes the scale tension itself, and
v0.2 should be a velocity-dependent model.

## What changes about the WIMpy project

Nothing. This is a separate project at
`C:\Users\lamkuenai\projects\dm-sidm-pipeline\` (new folder).
WIMpy's cosmological-DE result is independent of whether SIDM exists.

## Update history

- 2026-08-10 — v0.1 plan created from dark-glueball.docx feasibility analysis.