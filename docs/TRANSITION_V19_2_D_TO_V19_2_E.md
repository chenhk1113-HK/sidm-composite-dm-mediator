# Transition: v19.2-D → v19.2-E

**Date:** 2026-10-08 (R88(82) freeze)
**Branch:** `wip/v19.2-E-init` (from master @ 37814f4)

## What v19.2-D is

The v19.2-D milestone is the **paper-freeze milestone**. The paper (`v0.3-prelim/docs/PAPER_V1_DRAFT.md`) is submission-ready as Direction C (constraint map + no-go catalogue) for Physics of the Dark Universe or JCAP.

**Three first-class structural results survive R88(82) review:**

1. **§2.6a Cloud-9 vs dSph tension (v=28↔15):** A narrow resonance at v_target=29.4 km/s satisfies Cloud-9's σ/m ≥ 50 cm²/g working benchmark but a physically-derived f_H(r) drives σ_eff at dSph velocities above Horigome+ 2025's 0.8 cm²/g limit by 3.6-23.7×. The tension partially resolves with a third narrow peak at v=10 km/s (Fischer & Yu 2026 UFD diversity).

2. **§9.17a Lei/Wang vs Sameie+ 2020 tension (v=150):** Single-species σ_m(v) cannot simultaneously satisfy Lei/Wang (σ_eff > 0.1, cores in massive galaxies) and Sameie+ 2020 (σ_eff < 0.3, subhalo survival) at v=150. Phase G7's nominal PASS sits inside a factor-3 knife-edge window.

3. **§9.17b Structural trade-off result (within the multi-resonance ansatz):** Any physically-derived f_H(r) that resolves the v=150 no-go (heavy concentrated at center) drives σ_eff at all other observation radii down by 5-300×, breaking Cloud-9, SPARC, and Lei/Wang simultaneously.

**Framework score (Phase G8):** 4 of 7 constrained channels pass; 3 MARGINAL; 1 FAIL (Sameie+ 2020 structural no-go). The framework is a constraint map, not a unified SIDM model.

**Four forward paths tested (R88(72)-(78), ALL FAILED):**
- A (IDE-2cSIDM): 4/8 → 4/8 (no improvement)
- B (ULDM): 4/8 → 2-3/8 (worse)
- C (N-body + exotic UV): deferred
- D (observation refinement): caught σ_m(150) numerical error; framework FAILS Lei/Wang at v=150 by factor 6

**Citation audit complete (R88(82)):**
- 16 of 17 arXiv IDs confirmed
- "He+ 2020" → "Sameie+ 2020" (PRL 124, 141102, arXiv:1904.07872)
- "Mace+ 2026 SIDM2v" → "Mace+ 2025 gravothermal N-body" (arXiv:2504.13004)

## What v19.2-E is (and is not)

**v19.2-E is the NEXT paper.** It is a fresh branch (`wip/v19.2-E-init`) where forward-looking research lives.

**v19.2-E is NOT:**
- A continuation of the R88(81)/(82) sub-round archaeology. **R88(N) sub-rounds stop here.**
- A correction patch for v19.2-D. v19.2-D is frozen.
- A re-do of any R88(57)-(80) work. That work is preserved in `docs/FINDINGS_FOR_FUTURE_DELIBERATION.md` and the bundle archive.

**v19.2-E IS:**
- A place to address Kimi's review points (theorem → result, sensitivity paragraph, channel table, abstract rewrite, KiSS-SIDM over-claim) as part of a v0.5 paper, not as R88(N) sub-rounds.
- A place to add the high-value forward work (SASHIMI re-run, Path C cosmological N-body) that v19.2-D deferred.
- A place to test the new SASHIMI / cosmological N-body results against the v19.2-D framework.

## Conventional version tags for v19.2-E

R88(N) sub-rounds were the convention through v19.2-D. **v19.2-E switches to conventional version tags:**

| Tag | Meaning |
|-----|---------|
| v0.5-prelim+v19.2-E-init | Branch start, v19.2-D paper frozen |
| v0.5.0 | First batch of v19.2-E work complete |
| v0.5.1 | Second batch (cite-check, rebrand, etc.) |
| ... | ... |
| v0.5-N | Final v19.2-E pre-submission |
| v0.6-prelim+v19.2-E-final | Submission-ready |
| v0.6 | Submission tag |

CI builds bundles from tags (paper + findings + plans + code archive).

## What goes in the v19.2-E plan

From `docs/FUTURE_WORK_PLAN_V19_2_E.md` and Kimi's review:

**Priority 1 — Direction D (monitoring):** zero cost, ongoing. Watch for Sameie+ 2020 and Lei/Wang follow-ups with explicit f_H(r) treatment.

**Priority 2 — Path C (cosmological N-body):** 3-4 months, requires OpenGadget3 / FIRE / IllustrisTNG data. Test if empirical merger trees break the trade-off result by providing phase diversity.

**Priority 3 — Direction B (multi-species UV):** 1-2 months, only pursued if Path C fails. Two or more dark species with environment-dependent σ_m(v). The trade-off result says this is the only path that breaks the mutual exclusion.

**Priority 4 — Open questions (Q1-Q4):** opportunistic. Q3 (Sameie+ 2020 vs Lei/Wang reliability) is most consequential.

**Priority 5 — SASHIMI re-run + SPARC re-fit (defensibility):** 1-2 months each. Convert approximate PASSes into actual ones.

**Priority 6 — KiSS-SIDM PR upstream:** days, methods contribution.

## Process change (R88(82))

The R88(N) sub-round archaeology has stopped. Going forward:

1. **CI builds bundles from tags**, not from commits. Each tag represents a coherent milestone.
2. **R88(N) sub-rounds only as milestone summaries** (e.g., R88(82) = citation audit + Kimi review fixes). R88(83), R88(84), etc. would be v0.5.1, v0.5.2, etc.
3. **Conventional version tags** (v0.5, v0.6) for substantive paper changes.
4. **Pre-claim checklist (R88(71)) continues** as the project process for catching overclaims before submission.

## Action items

1. **Create v19.2-E bundle** when v0.5.0 tag is created.
2. **Re-do Kimi review fixes as v0.5.0 changes** (theorem → result, sensitivity, channel table, abstract, KiSS-SIDM over-claim) — already applied in master @ 37814f4 as R88(82) fixes. These will be folded into v0.5.0 as the first tagged v19.2-E milestone.
3. **Document this transition** in README.md / CURRENT.md under "v19.2-D → v19.2-E process change."

## Reference

- **v19.2-D paper:** `v0.3-prelim/docs/PAPER_V1_DRAFT.md` (frozen at master @ 37814f4)
- **v19.2-D findings:** `docs/FINDINGS_FOR_FUTURE_DELIBERATION.md` (21 sections, ~57 KB)
- **v19.2-D plan:** `docs/FUTURE_WORK_PLAN_V19_2_E.md` (13 sections, 22.7 KB)
- **v19.2-D bundle:** `C:\Users\lamkuenai\sidm-v19_2-D-bundle\`
- **v19.2-D single .md:** `C:\Users\lamkuenai\sidm-v19_2-D-bundle-single.md` (553 KB, 6,303 lines)
- **v19.2-D audit:** `docs/CITATION_AUDIT_V19_2_D.md`
- **v19.2-E branch:** `wip/v19.2-E-init`
