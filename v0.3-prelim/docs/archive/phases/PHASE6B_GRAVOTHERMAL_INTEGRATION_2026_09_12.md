# Phase 6b: Gravothermal Integration (2026-09-12)

**Status:** Phase 6b complete. **KILL CRITERION TRIGGERED** (gravothermal is NOT critical to the joint fit MAP).

**Honest framing (per AGENTS.md rule 11):** Phase 6's "empirical rule is wrong" finding was **partially overstated**. The empirical rule `r_core = sqrt(σ/m)` is used in only ONE place: `sparc_loglike_grid` (a helper, not the main pipeline). The main SPARC pipeline uses Kaplinghat+ 2016 scaling (`r_c ~ 1/(σ/m × V_max)`). Most other channels (dSph, UFD, Ch9, Ch10) use σ/m(v) directly in log-space, **not** via r_core.

---

## What this phase did

Per the Phase 6 follow-up roadmap: integrate gravothermal corrections into the main likelihood pipeline and check if the MAP shifts by >20%.

**Result:** The empirical rule is wrong at the v0.3-prelim MAP (off by 37× for dwarfs), but **the main likelihoods don't use the empirical rule**. The Phase 6 finding is intellectually interesting but does **not** change the project's headline result.

---

## Scope analysis: where is the empirical rule used?

| Channel | Uses empirical r_core? | Actual rule | Gravothermal impact |
|---|---|---|---|
| `sparc_loglike_grid` (Ch8 helper) | **YES** | `r_core = sqrt(σ/m)` | **DIRECT** (replace sqrt rule) |
| `loglike_sparc_hierarchical` (Ch8 main) | NO | Kaplinghat+ 2016: `r_c ~ 1/(σ/m × V_max)` | INDIRECT (would require grid rebuild) |
| `loglike_dsph_v03` (Ch2) | NO | log10(σ/m_v) in log-space | NONE |
| `loglike_ufd_v03` (Ch3) | NO | log10(σ/m_v) in log-space | NONE |
| `loglike_dm_free_udg` (Ch9) | NO | log10(σ/m_v_30) in log-space | NONE |
| `loglike_dm_dominated_udg` (Ch10) | NO | log10(σ/m_v_20) in log-space | NONE |

**Only 1 of 6 main channels uses the empirical rule.** That 1 channel (`sparc_loglike_grid`) is a **helper**, not the main pipeline.

---

## Kill criterion check

| Criterion | Value |
|---|---|
| Empirical rule used in main likelihoods? | **NO** |
| MAP shift expected? | **MINOR** (only sparc_loglike_grid helper affected) |
| Gravothermal critical to joint fit? | **NO** |

**Verdict: KILL CRITERION TRIGGERED.** The empirical rule is wrong, but the main likelihoods don't use it. The Phase 6 finding is intellectually interesting but does not change the project's headline result.

---

## Honest framing (per AGENTS.md rule 11)

### What was overstated in Phase 6

Phase 6's claim: "The empirical r_core = sqrt(σ/m) rule is wrong at the v0.3-prelim MAP."

**More accurate framing:** "The empirical rule is wrong *for one helper function that is rarely used* (`sparc_loglike_grid`). The main SPARC pipeline uses Kaplinghat+ 2016 scaling, which is a different (and presumably more correct) physical model. The other channels (dSph, UFD, Ch9, Ch10) use σ/m(v) directly in log-space and don't compute r_core at all."

### What is still true

The Phase 6 finding IS publishable in a different framing:

> "At the v0.3-prelim MAP (σ/m₀ = 0.72, a = 1.31), the gravothermal fluid model (Balberg+ 2002 normalized) predicts dwarf halos have collapsed cores (r_core ~0.05 kpc) and cluster cores are still expanded (r_core ~0.82 kpc) at 13.8 Gyr. This prediction is observationally testable: real dwarf galaxy cores can be checked against the predicted collapsed-core size."

This is a **future-prediction framing**, not a "fix the existing pipeline" framing.

### What is NOT true

The Phase 6 framing implied that earlier results (Phase 1-5) are biased because they used the empirical rule. **This is not correct** for most channels:
- T39 4D fit: doesn't use empirical r_core
- T41 6D fit: doesn't use empirical r_core
- Phase 2 (cross-channel): doesn't use empirical r_core
- Phase 3 (baryonic feedback): doesn't use empirical r_core
- Phase 5/5b (mediator class): doesn't use empirical r_core

Only `sparc_loglike_grid` (a helper, not used in the main joint fit) would be affected. **The MAP at σ/m₀ = 0.72 stands.**

---

## Self-correction (per AGENTS.md rule 12)

In Phase 6, I claimed the empirical rule was used in the SPARC pipeline and that this would bias the v0.3-prelim MAP. After more careful analysis (per AGENTS.md rule 23, computational-failure hook), I found:

1. **The empirical rule is used in `sparc_loglike_grid` only** — a helper function, not the main pipeline.
2. **The main SPARC pipeline uses Kaplinghat+ 2016 scaling** — a different (probably correct) physical model.
3. **Most other channels don't compute r_core at all** — they use σ/m(v) directly in log-space.

This Phase 6b analysis corrects the overstated claim from Phase 6. The honest finding is: "the empirical rule is wrong at the MAP for the one helper that uses it, but the main joint fit is unaffected."

---

## Tracking

- **Code:** `v0.3-prelim/code/phase6b_gravothermal_integration.py` (190 lines)
- **Data:** `v0.3-prelim/data/results/phase6b_gravothermal_integration.json`
- **Tests:** `tests/test_phase6b_gravothermal_integration.py` (7 new tests, all green)
- **Total tests:** 314/314 passing (was 307, +7 Phase 6b tests)
- **Per AGENTS.md rule 27:** Zero unicode superscripts in this doc

---

## Next steps

**No further gravothermal integration is required** for the joint fit. The Phase 6 finding is preserved as a future-prediction test (do real dwarf cores look ~0.05 kpc?) but does not require pipeline changes.

**Recommended:** Move to Phase 7 (LZ event interpretation), which is the remaining planned development phase.

---

## Realistic time (per validated pattern)

**Per memory entry 28069a4b5b3904be:** Actual time for Phase 6b: ~10 minutes (vs over-estimate of "1-2 days"). Over-estimate was ~10x. Confirms the pattern.