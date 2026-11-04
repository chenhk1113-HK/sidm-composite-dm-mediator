# docs/INDEX.md — Navigation

> **For:** Anyone who has read CURRENT.md (or README.md) and wants to
> dig deeper. Organised by purpose, not chronology. Updated 2026-11-03
> (the "per-round" section below documents the Tier-1 v0.4-prelim+T75/T88E
> milestone; the active chain is the one added at the top).

---

## 🎯 Top-level (current state)

| Doc | Purpose | Read if you want |
|---|---|---|
| [`../CURRENT.md`](../CURRENT.md) | Version-of-record (standing section at the top; 1,167-line round history below) | The 60-second answer |
| [`../README.md`](../README.md) | Project description + quick-start | The 5-minute answer |
| [`LAYMAN_SUMMARY.md`](LAYMAN_SUMMARY.md) | Non-expert overview (Tier-1 milestone) | A readable summary |
| [`MATHEMATICS.md`](MATHEMATICS.md) | Mathematical appendix (formulas, derivations) | The derivation chain |
| [`TUTORIAL.md`](TUTORIAL.md) | End-to-end tutorial | To reproduce from scratch |
| [`DATA_SOURCES.md`](DATA_SOURCES.md) | External data catalog + citations | To verify data provenance |
| [`DARK_SECTOR_LAGRANGIAN.md`](DARK_SECTOR_LAGRANGIAN.md) | Benchmark A specification (canonical: §9) | The model definition |
| [`../MODEL_ASSUMPTIONS_AND_LIMITATIONS.md`](../MODEL_ASSUMPTIONS_AND_LIMITATIONS.md) | What the project does NOT claim | Honest scope |
| [`../EXTRACT.md`](../EXTRACT.md) | 1-page project extract + key findings | The new-reader TL;DR |
| [`../CHANGELOG.md`](../CHANGELOG.md) | Per-round ship history (T1 → T86) | To see what got shipped when |

## 🧭 Active chain — 2026-11-03 (v19.2-F audit record + v19.2-E research)

Read [`../CURRENT.md`](../CURRENT.md) first — it already summarises this. This table is for when a
specific claim needs its source document.

| Doc | Purpose |
|---|---|
| [`V19_2_E_CONSOLIDATED_REPORT_2026-11-03.md`](V19_2_E_CONSOLIDATED_REPORT_2026-11-03.md) | Running consolidation of the current four-stage chain (stages 1-2 complete, stage 3 pending IllustrisTNG) |
| [`NEW_DATA_SWEEP_2026-11-03.md`](NEW_DATA_SWEEP_2026-11-03.md) | New-data adjudication: 31 unique cited arXiv IDs (the doc's own header says 32/32; no 32-entry list exists), tiered intake, what fired and what did not |
| [`INTEGRITY_FINDINGS_2026-11-04.md`](INTEGRITY_FINDINGS_2026-11-04.md) | Local integrity sweep: the σ/m-inert SIDM core radius, the kpc/Gyr-vs-km/s unit fix, Phase 40 scoring contradiction, gate teeth, citation KB closure, and the open owner decisions |
| [`STAGE3_TNG_FEASIBILITY_2026-11-04.md`](STAGE3_TNG_FEASIBILITY_2026-11-04.md) | IllustrisTNG Stage-3 measurement: resolution wall per run, RELHIC-band candidate counts, merger-tree access and payload sizes, and the recommended sample |
| [`STAGE3_TNG_SAMPLE_2026-11-04.md`](STAGE3_TNG_SAMPLE_2026-11-04.md) | IllustrisTNG Stage-3 sample as built (115 halos, 0.18 MB), the measured V_max ceiling of the Cloud-9 anchor cell, and the newly verified silently-ignored API filters |
| [`CLOUD9_HIGHSIGMA_TIMING_RECHECK_2026-11-03.md`](CLOUD9_HIGHSIGMA_TIMING_RECHECK_2026-11-03.md) | Cloud-9 optical-depth / collapse-timing recheck after the lookback-time fix |
| [`V19_2_E_A1_REAL_LIKELIHOOD_PROMOTION.md`](V19_2_E_A1_REAL_LIKELIHOOD_PROMOTION.md) … [`V19_2_E_D_CANONICAL_NUMBERS.md`](V19_2_E_D_CANONICAL_NUMBERS.md) | The A.1 / A.2 / B / C / D work packages behind the canonical numbers (real-likelihood promotion, 5-param DE fit, per-halo gravothermal calibration, data-only σ/m(v), machine-generated canonical values) |
| [`FUTURE_WORK_PLAN_V19_2_E.md`](FUTURE_WORK_PLAN_V19_2_E.md) | What v19.2-E is for, in order |
| [`TRANSITION_V19_2_D_TO_V19_2_E.md`](TRANSITION_V19_2_D_TO_V19_2_E.md) | Why the R88(N) sub-round convention stopped and conventional versioning started |
| [`dual_review_5loop/README.md`](dual_review_5loop/README.md) | Index of the closed n18→n26 audit chain: which report version is the record, which are superseded, what each evidence folder certifies |
| [`V19_2_F_REFERENCE_DATA_REGISTRY.md`](V19_2_F_REFERENCE_DATA_REGISTRY.md) | Single source of truth for every numerical value and its verification status |
| [`papers/00_HOME.md`](papers/00_HOME.md) | Literature knowledge base home (`verified/` + `to_verify/`, intake rule) |
| [`FINDINGS_FOR_FUTURE_DELIBERATION.md`](FINDINGS_FOR_FUTURE_DELIBERATION.md) | Open findings carried forward, drift-guarded |
| [`CITATION_AUDIT_V19_2_D.md`](CITATION_AUDIT_V19_2_D.md) | Citation integrity for the v19.2-D record |

## 🔬 Per-round documentation (current Tier-1 milestone)

These document rounds T72–T84 (the v0.4-prelim+T75 milestone):

| Round | File | Summary |
|---|---|---|
| T72 | `../v0.3-prelim/docs/T72_DAMPE_POC.md` | DAMPE CRE spectrum POC |
| T73 | `../v0.3-prelim/docs/T73_DAMPE_V04_INTEGRATION.md` | DAMPE → joint fit Channel 17 |
| T74 | `../v0.3-prelim/docs/T74_LSS_ZHANG_2025.md` | Zhang+2025 LSS → Channel 18 |
| T75 | `../v0.3-prelim/docs/T75_V07_FULL_T41_RERUN.md` | v0.7 full joint-fit rerun |
| T76 | `../v0.3-prelim/docs/T76_V07_NLIVE2000.md` | nlive=2000 convergence check |
| T77 | `../v0.3-prelim/docs/T77_LZ_2026_09_UPDATE.md` | LZ signal defensive doc |
| T78 | `../v0.3-prelim/docs/T78_KINETIC_MIXING_LZ_LINK.md` | Kahlhoefer kinetic-mixing |
| T79 | `../v0.3-prelim/docs/T79_COMPOSITE_FORM_FACTOR_REMNANT.md` | Composite form-factor + relic |
| T80 | `../v0.3-prelim/docs/T80_LZ_PAPER_UPDATE.md` | LZ paper compatibility |
| T81 | `../v0.3-prelim/docs/T81_LZ_REVIEW_RESPONSE.md` | LZ1.docx review response |
| T82 | `../v0.3-prelim/docs/T82_STALE_CLAIM_AUDIT.md` | Doc-vs-code drift audit |
| T83 | `../v0.3-prelim/docs/T83_KSFR_LATTICE_PROMOTION.md` | KSFR (3,2) fundamental LATTICE |
| T84 | `../v0.3-prelim/docs/T84_LSS_RHO_SENSITIVITY.md` | Channel 18 ρ sensitivity sweep |

## 🗂 Reference tables & scientific data

- [`../v0.3-prelim/docs/KSFR_NC_NF_TABLE.md`](../v0.3-prelim/docs/KSFR_NC_NF_TABLE.md)
  — KSFR ratio table for 7 (Nc, Nf) combos with LATTICE/ANALYTICAL/ESTIMATED confidence classes.
- [`../v0.3-prelim/code/channels_extended.py`](../v0.3-prelim/code/channels_extended.py)
  — All 19 channel likelihoods (production code).
- [`../v0.3-prelim/code/t41_mediator_mass_joint_fit.py`](../v0.3-prelim/code/t41_mediator_mass_joint_fit.py)
  — Joint-fit runner (T41).

## 📦 Standing-version roadmap

- [`../v0.3-prelim/docs/V0_6_ROADMAP.md`](../v0.3-prelim/docs/V0_6_ROADMAP.md)
  — Items #10 / #17 / #19 deferred from R14/R15/R16 reviews;
  T83 advanced #19 (3 LATTICE / 2 ANALYTICAL / 2 ESTIMATED).

## 🧪 Code, data, scripts

- Code: `../v0.3-prelim/code/` (Python, ~135 modules)
- Data: `../v0.3-prelim/data/` (result JSONs + ingested LZ-2024)
- Scripts: `../scripts/` (audit, bundle builders, smoke tests)

## ⏸ Historical (archived)

Older audit cycles and superseded docs are preserved **in git history only**:
- REVIEWER_AUDIT_R9.md, R10.md, R11.md (R9-R11) — pre-R12 reviewer cycles
- LAYMAN_SUMMARY_R12.md / R13.md / R14.md / T71_8.md — superseded by LAYMAN_SUMMARY.md
- MEDIATOR_DETECTION_SYNTHESIS_v2.md → v11.md — superseded by v12
- V0_6_BROWER_PROBE_SCOPE, V0_6_TIER_B_CLOSURE, etc. — closure narratives

To access any of these (preserved in git history):
```bash
git log --all -- <path>
git show <commit>:<path>
```

Bundled archives (in-tree, collapsed `<details>` view):
- R12/R13/R14/T71.8 layman summaries →
  [`v0.3-prelim/docs/LAYMAN_SUMMARIES_HISTORICAL.md`](v0.3-prelim/docs/LAYMAN_SUMMARIES_HISTORICAL.md)
- V0_6 closures (TIER_B, BROWER, KISS_SIDM, LATTICE) →
  [`v0.3-prelim/docs/V0_6_CLOSURES_HISTORICAL.md`](v0.3-prelim/docs/V0_6_CLOSURES_HISTORICAL.md)
- Mediator Detection Synthesis v2-v11 →
  [`v0.3-prelim/docs/MEDIATOR_SYNTHESES_HISTORICAL.md`](v0.3-prelim/docs/MEDIATOR_SYNTHESES_HISTORICAL.md)

`FINDINGS.md` was renamed to `PROJECT_FINDINGS.md` in T86.7f to break
a basename collision with `docs/findings_2026_SIDM_papers.md`.

## How to get oriented quickly

1. **First-time visitor:** `CURRENT.md` → `README.md` (5 min) → `LAYMAN_SUMMARY.md` (10 min)
2. **Drive-by reviewer:** `CURRENT.md` + `MATHEMATICS.md` + `DARK_SECTOR_LAGRANGIAN.md §9`
3. **Reproducer:** `TUTORIAL.md` (end-to-end)
4. **Returning developer:** `CHANGELOG.md` → per-round T7X/T8X docs → `v0.3-prelim/data/results/`
5. **External auditor:** git tags + git log + per-round T7X docs

## Maintenance note

This index is regenerated whenever a T-round ships or a doc is
renamed. Archive re-index refresh: 2026-11-03 (supersedes the 2026-09-03 (T86) index).
