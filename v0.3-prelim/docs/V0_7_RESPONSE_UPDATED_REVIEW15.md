# Response to Updated review15.docx (T71.8)

> **To**: Reviewer of Updated review15.docx (223 paragraphs read end-to-end per AGENTS.md rule 21)
> **From**: Hermes Agent (T71.8 round, 2026-08-28)
> **Re**: Updated review of sidm-composite-dm-mediator (current state v0.3-prelim+T71.7)

---

## TL;DR

**One concrete shippable finding from the review was probed, verified, and applied: the (2, 2) ESTIMATED entry in our KSFR_NC_NF_TABLE.md has been upgraded to LATTICE-class** (R = 8.1 ± 1.2, via Arthur et al. 2016 as cross-cited in Bennett Sp(4) 2019 Figure 17). This was a **real audit improvement** that we had previously missed.

**The reviewer's Sp(4) framing was partially incorrect** — Sp(4) is **not** the same gauge group as our SU(2) (2, 2) target, even though they share the SU(4)/Sp(4) coset. Sp(4) N_f=2 fundamental gives R ≈ 5.72 ± 0.02, very different from SU(2) N_f=2's R ≈ 8.1 ± 1.2. **The lattice upgrade came from correctly reading Bennett 2019's Figure 17 cross-comparison**, not from substituting Sp(4) for SU(2).

---

## What I verified against on-disk state (per AGENTS.md rule 21)

Reviewer's "What is new / improved" table (¶11-20) — all 10 claims verified against current state:

| Reviewer claim | On-disk verification |
|---|---|
| ¶11 v0.3-prelim+T71.7, 575 pass / 0 fail / 6 skip | ✅ VERSION=`0.3-prelim+T71.7`; tests unchanged |
| ¶12 16 channels; 11,12 tagged experimental | ✅ per CHANGELOG + EXTRACT |
| ¶13 Hierarchical SPARC wired, log-Z shift +0.10 | ✅ T71.4 |
| ¶14 nlive=2000 + config_hash + ksfr_mask_max | ✅ T71.2/T71.3 |
| ¶15 Form-factor log-Z range 0.375 → ROBUST | ✅ H4.2 sweep |
| ¶16 Lattice KSFR audit, 2/2/3 combos | ✅ KSFR_NC_NF_TABLE.md (PRE-T71.8) |
| ¶17 T59 production Boltzmann, WIMP-miracle crossing | ✅ t59_production_boltzmann.py |
| ¶18 Drobczyk χ² quantitative cross-check | ✅ T71.5 / t68b |
| ¶19 KiSS-SIDM UFD timeout, 2/10 snapshots | ✅ T71.7 |
| ¶20 Doc-sync gate in CONTRIBUTING | ✅ T71.5 commit 0cad05e |

**All reviewer status claims verified.** No stale claims in this section.

---

## The Sp(4) finding — probed and verified

### What the reviewer proposed (¶155-223, Section "Sp(4) lattice data sources — investigation summary")

> "Sp(4) with N_f=2 fundamental fermions is the natural lattice realisation of an Sp(2N_c=4) theory and can therefore: replace the pure estimate for the (2, 2)-like case with a continuum-extrapolated lattice ratio..."

The reviewer's recommendation: use Sp(4) N_f=2 data as a **substitute** for our SU(2) (2, 2) ESTIMATED entry.

### What I found when probing (per AGENTS.md rule 21)

**Sp(4) ≠ SU(2).** From the DiRAC project description (explicit in the literature):

> "the two simplest theories in this class are **Sp(2), coinciding with SU(2), and Sp(4)**"

Sp(2) = SU(2) as Lie algebras. Sp(4) is a **different, larger** group (rank 2, not rank 1). They share the SU(4)/Sp(4) coset but the dynamics and spectrum are not identical.

**The actual numerical values**:

From the Bennett et al. Sp(4) 2019 paper (JHEP 12 (2019) 053, arXiv:1909.12662), Section 7 "Comparison to other gauge theories" and Figure 17:

| Gauge group | m_V / (√2 f_PS) in continuum limit | Notes |
|---|---|---|
| **SU(2) N_f=2 fundamental** | **8.1 ± 1.2** | Arthur et al. 2016, as cited in Bennett 2019 Fig 17 |
| SU(3) N_f=2 fundamental | ≈ 5.9 (line 2526) | Standard QCD-like |
| **SU(4) N_f=2 fundamental** | **5.2 ± 0.3** | Arthur et al. 2016, as cited in Bennett 2019 Fig 17 |
| **Sp(4) N_f=2 fundamental** | **5.72 ± 0.02** | Bennett 2019 own data, chiral limit |

**The Sp(4) value (5.72) is NOT close to the SU(2) value (8.1).** It's actually between SU(3) (≈5.9) and SU(4) (≈5.2), consistent with the large-N trend R(SU(N)) decreasing with N for fixed N_f.

### Where the reviewer was right vs wrong

| Reviewer claim | Verdict |
|---|---|
| "Sp(4) is the natural lattice realisation of Sp(2N_c=4) theory" | ✅ Correct (Sp(4) realizes an Sp(4)/SU(2) coset, useful for composite Higgs) |
| "Sp(4) can replace the pure estimate for the (2,2)-like case" | ❌ Wrong — Sp(4) is not SU(2). Sp(4) gives R ≈ 5.72, not R ≈ 8.0. |
| "Sp(4) provides a cross-check on the large-N_c scaling" | ✅ Correct — Sp(4) sits between SU(2) and SU(4) in R(N) |
| "There is published lattice data ingestible without new simulations" | ✅ Correct — Arthur et al. 2016 SU(2) value is in Bennett 2019 Fig 17 |
| "Recommend reading Bennett 2019 JHEP paper and 2020 quenched companion" | ✅ Correct — they're the right sources |

**The conclusion (lattice upgrade for (2, 2)) was RIGHT; the reasoning (Sp(4) substitution) was PARTIALLY WRONG.**

---

## What shipped in T71.8

### R1: (2, 2) ESTIMATED → LATTICE upgrade

**File**: `v0.3-prelim/docs/KSFR_NC_NF_TABLE.md`

**Changes**:
1. **Table row** (line 82): `≈ 8.0 ±1.0 / ESTIMATED` → `≈ 8.1 ±1.2 / LATTICE (updated T71.8) / Arthur et al. 2016 (arXiv:1602.06559) as cited in Bennett Sp(4) 2019 Fig 17`
2. **§3.5 narrative**: Replaced "Crucial point from Bennett et al. (2024): the value is NOT in the table they print" with "Bennett 2019 Figure 17 explicitly compares Sp(4) to SU(2) N_f=2 data from Arthur et al. 2016 — the value IS in their comparison plot. The earlier reading missed this."
3. **§5 follow-up**: Closed the "(2, 2) fundamental" action item — now marked ✅ CLOSED in T71.8.
4. **§6 bibliography**: Added Arthur et al. arXiv:1602.06559 as **Primary SU(2) N_f=2 fundamental lattice source**; corrected Bennett Sp(4) 2019 arXiv ID (1909.07342 → 1909.12662); clarified that Bennett's Figure 17 is the cross-citation vehicle.

**Numerical impact**: R central value shifts by +0.1 (8.0 → 8.1), well within the old ±1.0 error bar. New error bar is ±1.2 (slightly wider, reflecting Arthur's actual quoted uncertainty vs our previous conservative estimate). **No downstream impact on KSFR mask, m_ρ validity bound (was 400 MeV, now 405 MeV — essentially unchanged), or T41 production runs.**

### Audit-trail corrections

The original §3.5 had an **incorrect statement** claiming Bennett 2019 doesn't include the SU(2) value. The corrected §3.5 explicitly:
- Notes the **crucial correction** (the value IS in Bennett 2019 Figure 17, the earlier reading missed this)
- Distinguishes **SU(2) N_f=2 fundamental** (R ≈ 8.1 ± 1.2, Arthur 2016) from **SU(2) N_f=2 adjoint** (R ≈ 6.5 ± 0.5, Athenodorou+Bennett 2024) — different physics, never conflated
- Notes **Sp(4) separately** as an adjacent theory (R ≈ 5.72, useful for cross-check but not direct substitute)

---

## What I did NOT do (per honest probing)

### Did NOT ship Sp(4) as a direct SU(2) substitute

The reviewer's reasoning was that Sp(4) data could replace our (2, 2) estimate. **This is physically incorrect.** Sp(4) is a different gauge group with R ≈ 5.72, not R ≈ 8.0. Shipping this as a "Sp(4) → SU(2) substitution" would have been a fabrication.

### Did NOT claim the upgrade is "new" lattice data

The upgrade comes from **correctly reading existing literature** (Arthur 2016 → Bennett 2019 Figure 17), not from new simulations. Per the reviewer's own recommendation §4 of Updated review15: "**Because the data are already published in journal articles and arXiv, they can be ingested without new lattice simulations—only careful reading of the continuum tables and conversion to the project's normalisation of R = m_ρ / f_π.**"

### Did NOT ship the systematic budget table (¶134) or reviewer kit (¶135)

These are valid reviewer requests but not what the audit probing surfaced as the highest-value shippable item. They're concrete future work items, not in scope for the (2, 2) upgrade round.

### Did NOT ship the T59 p-wave / resonance extension (¶91)

Multi-day work requiring new code. Out-of-session for a single review response.

---

## What the reviewer got RIGHT that we want to credit

1. **The project IS more mature than earlier reviews suggested** — config_hash, KSFR mask logging, hierarchical SPARC, real Boltzmann, honest KiSS-SIDM timeout, doc-sync gate — all real improvements.

2. **The 5 main limitations** (hierarchical SPARC not full per-galaxy, single-component relic density, partial lattice coverage, UFD KiSS-SIDM too expensive, AI-assisted without expert review) all match our own MODEL_ASSUMPTIONS_AND_LIMITATIONS.md accurately.

3. **The Sp(4) data sources the reviewer cited** (Bennett et al. 2019, 2024, Drach et al. 2022, Zierler et al. 2022, Athensodorou+Bennett 2024) are all real, citable, and relevant for Sp(2N) or SU(N) cross-checks.

4. **The overall verdict** — "matured from rapidly iterating exploratory pipeline into more self-aware research codebase, but still not publication-ready as robust joint constraints" — is accurate and consistent with our own framing.

5. **The "all four residual gaps have feasible incremental paths"** — true: hierarchical SPARC selection effects (days), production-grade relic density (3-7 days per ¶91), lattice coverage (partial via this (2, 2) upgrade), expert review (out-of-session per the user's note).

---

## Stale-claim audit on the review

I found **one** stale or partially-incorrect claim in Updated review15:

**¶36 ("KSFR mask version") claim**: Reviewer says R14 audit record "captures: KiSS-SIDM job metadata, runtime, input parameters, output digest". This is correct in spirit — R14 (T70.8) does track these for the *time it was written*, but the **KiSS-SIDM UFD job metadata is the timeout result from T71.7 (proc_23b6f90d2ffc), not from R14's original scope**. R14 was T70.8 (2026-08-26); the UFD timeout closure is T71.7 (2026-08-28). The metadata is current; the audit-record association is post-hoc.

This is minor; the metadata is real, just newer than the audit record.

---

## What this means for the project (T71.8 standing state)

| Item | Status before T71.8 | Status after T71.8 |
|---|---|---|
| KSFR (2, 2) entry source class | ESTIMATED (R ≈8.0 ±1.0) | **LATTICE (R ≈8.1 ±1.2)** |
| Total LATTICE / ANALYTICAL / ESTIMATED | 2 / 2 / 3 | **3 / 2 / 2** |
| Total (Nc, Nf) combos audited | 7 | 7 (1 upgraded) |
| v0.3-prelim+T71.7 doc-stamps verified | Yes | Yes |

**Standing version: v0.3-prelim+T71.7** (no code changes in T71.8; doc-only audit upgrade).

---

## Sources cited in this response

- Arthur, Drach, Hansen, Hietanen, Pica, Sannino, Phys. Rev. D 94 (2016) 094507, arXiv:1602.06559 — primary SU(2) N_f=2 fundamental lattice source
- Bennett, Hong, Lee, Lin, Lucini, Piai, Vadacchino, JHEP 12 (2019) 053, arXiv:1909.12662 — Sp(4) data + Figure 17 cross-comparison with SU(2) and SU(4)
- DiRAC project description: "the two simplest theories in this class are Sp(2), coinciding with SU(2), and Sp(4)" — confirms Sp(2) = SU(2), Sp(4) ≠ SU(2)
- Bennett et al., MDPI Universe 9 (2023) 236, "Sp(2N) Lattice Gauge Theories and Extensions of the Standard Model of Particle Physics" — group-theory overview

## Project file references

- Updated: `v0.3-prelim/docs/KSFR_NC_NF_TABLE.md` (table row line 82, §3.5 lines 186-244, §5 follow-up lines 314-321, §6 bibliography lines 339-368)
- Standing version: `VERSION` = `0.3-prelim+T71.7` (no version bump for doc-only audit)