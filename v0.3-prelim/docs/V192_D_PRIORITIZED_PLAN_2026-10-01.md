# v19.2-D Plan — Prioritized (post R71/R72 review)

**Date:** 2026-10-01
**Source:** R72 reviewer feedback on the v19.2-D item inventory
**Status:** v19.2-C milestone is `c486782`, R72 fixes in `7f82a7c` — DD section final

---

## R72 reviewer guidance (verbatim)

> "The paper is close to submission-ready. The v19.2-D that matters is: fix the R71 items, run D-5, finish D-8, build the PDF, audit references. Everything else is v2 material."

> "The R72 reviewer's own guidance ('state the constraint, not the parameter') suggests [D-1] shouldn't be done at all."

> "The plan treats v19.2-D as 'the deferred items.' But the reviewer's guidance (R60, R72) was that most of what was deferred was correctly deferred — either because it's future work (D-2, D-3, D-19) or because it doesn't change the paper (D-1, D-7). The plan currently treats deferral as a to-do list rather than as a set of open questions with different priorities."

---

## Pre-submission fixes (R71/R72 review items) — DONE in commit `7f82a7c`

All three R71/R72 fixes are already in the paper (committed R72, pushed):

1. **Ratio arithmetic**: R71 said "ratio 10⁴⁶ → 10¹¹". R72 said that's wrong by 10²⁴. **FIXED R72:**
   - σ_DM-DM = 1 cm²/g × 1.78×10⁻²⁴ g = 1.78×10⁻²⁴ cm² (per particle, m_χ = 1 GeV)
   - σ_SI bound = 10⁻⁴⁶ cm²
   - Ratio = **1.78×10²²** (NOT 10⁴⁶)
   - (g_χ/g_N)² = ratio → g_χ/g_N = √(1.78×10²²) = 1.34×10¹¹
   - g_N/g_χ < 7.5×10⁻¹² (consistent with paper's "3×10⁻¹¹" OOM)

2. **σ_peak = 174 vs m_χ = 1.0 reconciliation**: **FIXED R72:**
   - 174 cm²/g IS m_χ-INDEPENDENT by per-unit-mass convention
   - Both 3.0 (causality cap factor, dimensionless) and 50 cm²/g (Cloud-9 floor, per-unit-mass) are m_χ-INDEPENDENT
   - Per-particle cross section DOES depend on m_χ (σ/m × m_chi[g]), but σ/m itself doesn't
   - Paper §10.7 now states this explicitly

3. **Single-mediator coupling assumption note in §10.7**: **FIXED R72:**
   - Paper §10.7 now states: "Coupling-structure assumption: σ_DM-DM ∝ g_χ⁴, σ_SI ∝ g_χ² g_N² (single-mediator Yukawa). Other coupling structures would give different scalings."

---

## DO NOW (before submission)

### 1. D-5 — σ_peak width test (dSph tail vs Cloud-9 bulk)
**Cost:** 2-3 hours
**Why this matters:** Live tension between dSph non-collapse and Cloud-9 bulk. At w=4.4 km/s, the v₁ Gaussian reaches dSph velocities (v=15) with 1.3% of peak → 2.21 cm²/g contribution at v=15 km/s. At w=3.0 km/s, the same Gaussian reaches v=15 with exp(-169/(2×3.0²)) ≈ 8×10⁻⁵ (essentially zero) while still reaching V_max=31.12 km/s with exp(-(31.12-28)²/(2×3.0²)) ≈ 0.58 (contributes ~100 cm²/g at Cloud-9's bulk velocity). **A narrower width would suppress the dSph tail while keeping the Cloud-9 bulk contribution intact.** Test whether w ≲ 3 km/s is consistent with all 8 channels via a re-fit with dSph gravothermal constraint included.
**Output:** If consistent, paper §2.6 / §3.3 gets the refined width; if inconsistent, the gravothermal tension at dSph is a real constraint on the framework.
**Status:** Not started. Algorithm is simple — re-run existing fit with dSph likelihood added.

### 2. D-8 — Post-diction audit (finish R58)
**Cost:** 2 hours
**Why this matters:** R58 introduced the post-diction/prediction distinction but didn't trace every σ/m claim to either a fit, a measurement, or a constraint. Per R72: "state the constraint, not the parameter" — this audit operationalizes that guidance.
**Output:** A table in §3 or §11 listing every quantitative claim × (source: post-diction / measurement / prediction).
**Status:** R58 partial; needs completion. The audit itself is cheap (mostly reading existing sections).

### 3. D-17 — PDF build
**Cost:** 1-2 hours
**Why this matters:** Markdown source of truth during drafting; submission requires PDF. Doesn't depend on anything else. Independent of all other v19.2-D work.
**Output:** Paper-ready PDF for PRD or JCAP submission.
**Status:** Markdown source is the version of record; PDF build pipeline needs to be set up.

---

## DO IF TIME PERMITS

### 4. D-13 — Reference audit (Tier 3-B from Grok review)
**Cost:** 2-4 hours
**Why this matters:** Submission requires verified citations. AUDIT_REFERENCES.md already done most of the work; final ADS-access verification needed. Constraint is human + ADS access, not time.
**Output:** Confirmed bibliography for submission.
**Status:** Mostly done; needs human ADS sweep.

---

## DROP (don't pursue, per R72 reviewer)

These were inventoried in the original plan but R72 says don't do them — they don't change the paper's conclusions:

### D-1 — Joint SIDM+LZ fit (Insight Part 2 path)
- **Reason for drop:** "Per R72 reviewer's own guidance ('state the constraint, not the parameter') suggests this shouldn't be done at all." The paper's hierarchy constraint already states the relationship; a 5D dynesty fit refines numbers the paper already states as constraints.
- **Plus:** R31-R35 §2.7 likelihood was miscalibrated after being built. Same risk applies here.

### D-4 — Verification of σ/m = 135.3 cm²/g at V_max against fresh MCMC
- **Reason for drop:** σ/m = 135.3 cm²/g is at the c=4 anchor (Cloud-9 physical anchor), not c=12 (analytical). The fresh MCMC re-derivation would refine a number already stated as a constraint.

### D-6 — Re-derive σ_peak from UV physics (R44 Option 1)
- **Reason for drop:** "This is the task that produced R44 Option 1, R50, R51, R52, and the entire DD correction sequence. The last attempt took 4 rounds and ended in retraction." A UV completion, if it exists, is weeks of work. If it doesn't exist, the estimate is meaningless.

### D-7 — Joint posterior: Cloud-9 + dSph + SPARC + Cluster + JVAS
- **Reason for drop:** Per R72 guidance ("state the constraint, not the parameter"), a full joint posterior refines numbers the paper already states as constraints. Same R31-R35 calibration trap.

### D-9 to D-12 — KiSS-SIDM Tier 3 code modifications (subcycled time integration, freeze refinement, manual redistribution, anti-gravitational pressure)
- **Reason for drop:** "Plan doesn't say whether KiSS-SIDM results appear in v1.0. If they don't, this is 12-16 hr for a future paper." Per v18.43 §10.5b: "Methods contribution only" framing; KiSS-SIDM is not a v1.0 deliverable.

### D-16 — PySR symbolic regression
- **Reason for drop:** Speculative. Blocked by Julia install (~200 MB). Per AUTOCHECK_TIER_REVIEW: "PySR's risk is over-fitting: it would find a closed-form that fits, but not necessarily the right one."

---

## DEFER INDEFINITELY (these are papers of their own, not v19.2-D tasks)

### D-2 — GIZMO N-body reproduction of Silverman+ 2026's 6-halo suite
- **Reason:** "Cluster-time simulations — these are papers of their own, not v19.2-D tasks." Per A.13: "Requires FIRE-2 ICs + multi-day cluster runs." Real test of the framework with new data, but a separate paper.

### D-3 — Merger-history parameterization for 3-of-6 collapse prediction
- **Reason:** Same as D-2 — separate paper requiring multi-day cluster runs.

### D-19 — micrOMEGAs 6.0 for two-component relic density
- **Reason:** "Software/license gated — 1-2 days install + CalcHEP encoding." Future-work placeholder per AUDIT_FORNAX6_DOC.

### D-20 — Jia 2026 SIDM_Jeans_model integration
- **Reason:** "Software/license gated — Jia repo has NO LICENSE file. DO NOT INTEGRATE. Reference [52] as citation only." Per locked user directive.

---

## ALREADY RESOLVED (re-listed incorrectly)

### D-14 — 0.085 dex origin trace
- **Status:** Resolved R35-R36. Reframed as sensitivity result, not literature prediction. Currently stated in §2.7.

### D-15 — Master σ/m(v) figure for v1.15
- **Status:** Defer per Grok review Tier 3; not a v1.0 deliverable.

### D-18 — Figure rendering
- **Status:** Deferred per system audit.

---

## Total wall-clock (revised)

Per R72 reviewer: "Based on the R60-R71 pattern (every item took 2-3× the estimate once corrections are counted), a realistic estimate is 100-150 hr. Or, following the above priority list, ~10-15 hr to make the paper submission-ready."

**Do-now priority:** ~5-7 hours total (D-5: 2-3 hr, D-8: 2 hr, D-17: 1-2 hr)
**Do-if-time:** +2-4 hours (D-13 reference audit)
**Submission-ready total:** ~7-11 hours

---

## What v19.2-D actually is, per R72

> "v19.2-D shouldn't be a parallel workstream. It should be a short list of blocking items for submission, followed by a natural stopping point. If the user wants to continue physics after submission, D-2 (GIZMO reproduction of Silverman+ 2026) is the most natural next project — it's a real test of the framework with new data, not a refinement of existing claims. But that's a separate paper, not v19.2-D."

**v19.2-D = pre-submission polish, not a research sprint.**

---

## Submission checklist

- [x] R72 ratio arithmetic fix (1.78e22, not 10^46)
- [x] R72 m_chi-independence statement for σ_peak = 174
- [x] R72 single-mediator coupling assumption note
- [ ] D-5: σ_peak width test
- [ ] D-8: Post-diction audit finish
- [ ] D-17: PDF build
- [ ] D-13: Reference audit (if ADS access available)

---

*Plan generated 2026-10-01 per R72 reviewer feedback*
*All R71/R72 fixes in commit `7f82a7c`*
*Tag: v19.2-C-milestone-R71 (anchored to `c486782`)*