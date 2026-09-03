# docs/INDEX.md — Navigation

> **For:** Anyone who has read CURRENT.md (or README.md) and wants to
> dig deeper. Organised by purpose, not chronology. Updated 2026-09-03.

---

## 🎯 Top-level (current state)

| Doc | Purpose | Read if you want |
|---|---|---|
| [`../CURRENT.md`](../CURRENT.md) | 1-page version-of-record | The 60-second answer |
| [`../README.md`](../README.md) | Project description + quick-start | The 5-minute answer |
| [`LAYMAN_SUMMARY.md`](LAYMAN_SUMMARY.md) | Non-expert overview (Tier-1 milestone) | A readable summary |
| [`MATHEMATICS.md`](MATHEMATICS.md) | Mathematical appendix (formulas, derivations) | The derivation chain |
| [`TUTORIAL.md`](TUTORIAL.md) | End-to-end tutorial | To reproduce from scratch |
| [`DATA_SOURCES.md`](DATA_SOURCES.md) | External data catalog + citations | To verify data provenance |
| [`DARK_SECTOR_LAGRANGIAN.md`](DARK_SECTOR_LAGRANGIAN.md) | Benchmark A specification (canonical: §9) | The model definition |
| [`../MODEL_ASSUMPTIONS_AND_LIMITATIONS.md`](../MODEL_ASSUMPTIONS_AND_LIMITATIONS.md) | What the project does NOT claim | Honest scope |
| [`../EXTRACT.md`](../EXTRACT.md) | 1-page project extract + key findings | The new-reader TL;DR |
| [`../CHANGELOG.md`](../CHANGELOG.md) | Per-round ship history (T1 → T86) | To see what got shipped when |

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
renamed. Last refresh: 2026-09-03 (T86).
