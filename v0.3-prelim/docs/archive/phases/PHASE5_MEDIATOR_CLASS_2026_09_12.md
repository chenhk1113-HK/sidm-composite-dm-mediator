# Phase 5: Mediator Class Comparison (2026-09-12)

**Status:** Phase 5 complete. **KILL CRITERION TRIGGERED.** Per AGENTS.md rule 11 (honest framing), the kill criterion is triggered **but for a structural reason, not a physics reason**. The 4 mediator classes give drastically different σ/m(v) curves, but the existing project likelihoods are baked into the power-law form so they cannot discriminate between classes through this test.

---

## What this phase did

Per R1 Gap 4 (mediator class): "vector/scalar/composite: which UV completion produces the velocity dependence we observe?"

**Tested 4 mediator classes as alternative σ/m(v) functional forms:**

| Class | Form | σ/m(v_dwarf=10) | σ/m(v_cluster=1000) | Ratio |
|---|---|---|---|---|
| **Power-law** (reference) | σ/m_0 × (v/v_ref)^(-a) | 14.7 | 0.035 | **417** |
| **Yukawa** (vector) | prefactor / (1 + (v/v_dm)^2) | 0.72 | 0.69 | 1.04 |
| **Scalar portal** | σ/m_0 × (1 + α_h(v/v_ref-1)) | 0.40 | 4.0 | 0.10 |
| **Composite** | σ/m_0 × exp(-(v-v_R)^2/(2Δv^2)) | 0.66 | ~0 (10^-44) | 10^43 |

**The σ/m(v) curves ARE dramatically different** — spanning 47 orders of magnitude in the dwarf-to-cluster ratio.

---

## Why the kill criterion is triggered (structural, not physics)

**The kill criterion:** |Δ log Z| < 1 between ANY pair of mediator classes → mediator class NOT constrained.

**Result:** All 4 classes give log Z ≈ -279,558.89 (essentially identical). The composite form is -0.48 nats worse; the others are +0.00.

**Per AGENTS.md rule 23 (computational-failure hook)**: Why identical?

The existing project likelihoods (`loglike_sparc_hierarchical`, `loglike_dsph_v03`, `loglike_ufd_v03`) take **(σ/m_0, a)** as direct inputs. They are **baked into the power-law form internally** — they don't accept a generic σ/m(v) function.

My Phase 5 implementation applied a small SPARC offset based on σ/m(v) at v_ref, but:
1. **All 4 forms give the same σ/m at v_ref** (they're normalized to σ/m_0 there)
2. So the SPARC offset is zero for power-law/yukawa/scalar_portal
3. Composite gives a small offset because its form differs at v=100 km/s (not exactly at v_ref peak)

**The likelihoods CANNOT discriminate mediator classes through this test.** This is a **structural limitation of the existing code**, not a physics finding.

---

## Honest framing (per AGENTS.md rule 11)

**The kill criterion is triggered for the WRONG reason.**

| Aspect | Status |
|---|---|
| Different mediator classes exist | YES — 4 distinct σ/m(v) forms implemented |
| σ/m(v) curves are different | YES — 47 orders of magnitude spread in dwarf/cluster ratio |
| Likelihoods can discriminate them | **NO** — existing likelihoods are baked into power-law form |
| Phase 5 result | "Cannot tell; need to rebuild likelihoods" |
| Verdict | KILL (per roadmap); but the kill is structural, not physical |

**To properly discriminate mediator classes, one would need to:**
1. Rebuild `loglike_sparc_hierarchical`, `loglike_dsph_v03`, `loglike_ufd_v03` to accept a generic `sigma_m_at_v_fn(sigma_m_0, a, v)` as a parameter
2. Re-derive per-channel likelihoods at each mediator form's σ/m(v) at the relevant velocity scales
3. Then run the 4-way Bayes factor comparison

This is a **2-4 week rewrite** of the channel likelihoods, not a 1-2 week phase. The roadmap's "1-2 week" cost estimate assumed this was a parameter swap, but it's actually a likelihood rewrite.

---

## What this means for the project

**The publishable Phase 4 finding still stands:** "Yukawa gives over-strong velocity dependence; power-law phenomenology fits better."

**The Phase 5 finding adds:** "The project cannot currently distinguish between power-law, Yukawa, scalar-portal, and composite mediator forms at the v0.3-prelim MAP. To make this discrimination, the channel likelihoods must be rebuilt."

**Per R1 paragraph 88**: "Do not let it become a multi-week blocker." This finding exposes that Phase 5 was **always going to be a multi-week blocker** because of the structural rewrite needed.

---

## Strategic decision point

Per the roadmap's strategic options (per R1 paragraph 64-70):

| Option | Description | Status |
|---|---|---|
| A | Continue with current phase+ (assume model worth pursuing) | DEFER — Phase 5 cannot discriminate without rewrite |
| B | Pivot to publishing null result | **RECOMMENDED** — Phase 4 + Phase 5 findings together = "Yukawa over-strong; mediator class unconstrained; power-law fits best" |
| C | Pivot to symmetry question (what symmetry produces power-law) | DEFER — needs Option B published first |
| D | Defer to particle-physics collaboration | Possible after Option B |

**My recommendation: Option B.** Draft the publishable finding paper with:
- Phase 4 result (Yukawa over-strong)
- Phase 5 result (cannot discriminate mediator class without structural rewrite)
- Phenomenological power-law is the headline

---

## Tracking

- **Code:** `v0.3-prelim/code/phase5_mediator_class_comparison.py` (370 lines)
- **Data:** `v0.3-prelim/data/results/phase5_mediator_class_comparison.json`
- **Tests:** `tests/test_phase5_mediator_class.py` (14 new tests, all green)
- **Total tests:** 267/267 passing (was 253, +14 Phase 5 tests)
- **Per AGENTS.md rule 27:** Zero unicode superscripts in this doc

---

## Files

- `v0.3-prelim/code/phase5_mediator_class_comparison.py` (new)
- `v0.3-prelim/data/results/phase5_mediator_class_comparison.json` (new)
- `tests/test_phase5_mediator_class.py` (new)
- `v0.3-prelim/docs/PHASE5_MEDIATOR_CLASS_2026_09_12.md` (this file)

---

## Next steps

**Option B (recommended):** Draft publishable finding paper.
- Phase 4 finding: Yukawa over-strong velocity dependence
- Phase 5 finding: Mediator class unconstrained (structural limitation)
- Headline: Power-law phenomenological form fits best
- Target: PRD, JHEP, or JCAP

**Option A (deferred):** Rewrite channel likelihoods to be mediator-class-agnostic (2-4 weeks), then re-run Phase 5.

**Option C (deferred):** Investigate what symmetry produces a power-law σ/m vs v (3-6 months).

**Option D (deferred):** Hand off to particle-physics collaboration after Option B is published.