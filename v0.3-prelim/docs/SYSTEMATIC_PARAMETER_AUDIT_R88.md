# SYSTEMATIC_PARAMETER_AUDIT_R88 — Pre-Submission Cross-Check

**Date:** 2026-10-03
**Auditor:** K Lam (per R86 reviewer recommendation)
**Scope:** Every numerical parameter in PAPER_V1_DRAFT.md vs phase44_joint_fit.json best_params
**Trigger:** R66, R74, R76, R85, R86, R87 — six rounds of parameter-value corrections, all in the same direction (paper used one value, Phase 44 fit produced another).

---

## Cross-check table

| Parameter | Paper uses | Phase 44 best | Status | Round |
|-----------|------------|---------------|--------|-------|
| **m_χ (GeV)** | 1.0 (constants.py) | 10.44 (baseline) | Discrepancy | R66 |
| **v_target (km/s)** | 29.4 (constants.py) | 29.36 (free fit) | Match (within 1%) | R74 |
| **σ_0 (background, cm²/g)** | 0.052 (passed in scripts) | 0.0516 (free fit) | Match (within 1%) | — |
| **a_slope** | **1.0** (scripts hard-code) | **1.93** (free fit) | **CRITICAL MISMATCH** | **R86** |
| **σ_peak (cm²/g)** | 174 (causality cap) | 178.5 (free fit) | Match (within 3%) | R76 |
| **σ_1 (Gaussian σ, km/s)** | 4.4 (single Gaussian) | 430/769/196 (3 widths) | Different parameterizations | R76 |
| **m_φ (light mediator, GeV)** | 200e-9 (constants.py) | Not fit (fixed) | Not in fit | — |
| **m_Φh (heavy mediator, GeV)** | 2.0 (T221 framework) | Not fit | T192 used 20.7 (R87 wrong m_χ) | R87 |
| **α_χ** | 6.8e-7 (R58 derivation) | Not fit | Derived | — |
| **g_N/g_χ hierarchy** | ~10⁻¹³ (R83 v=28 anchor) | Not fit | Derived | R72-R83 |
| **T192 Ωh²** | 0.119 (claimed) | T192 used m_χ=10.3 | **WRONG m_χ** | R87 |

---

## Detailed audit of each "convenient" parameter

### 1. m_χ (DM mass) — Discrepancy [R66]

**Paper uses:** 1.0 GeV (constants.py M_CHI_GEV)
**Phase 44 best fit:** 10.44 GeV (baseline_params[0] = 6.58, but interpretation as m_χ is implicit; the free-fit was over a different parametrization)

Per R66 fix: paper uses 1.0 GeV; Phase 44's multi-resonance fit used 10.44. These are different parametrizations, not directly comparable. R66 chose to use 1.0 GeV as a simpler standard WIMP assumption.

**Effect on σ/m:** σ_DM-DM per particle = (σ/m) × m_χ [g]. At m_χ = 1 GeV, σ_DM-DM(per particle) is factor 10× smaller than at m_χ = 10 GeV. The R72 ratio derivation uses σ_DM-DM at m_χ = 1 GeV; the Phase 44 fit was at m_χ = 10.44.

**Implication:** The R72/R83 hierarchy constraint < 10⁻¹³ was derived at m_χ = 1 GeV. If we instead used m_χ = 10.44 GeV, the constraint would be different (factor of ~10√10 = ~32 different).

### 2. v_target (Cloud-9 resonance velocity) — MATCH [R74]

**Paper uses:** 29.4 km/s (constants.py V_TARGET_KMS)
**Phase 44 free fit:** 29.36 km/s (best_params[3])

Match within 1%. R74 fix: paper §2.6 line 152 used 28 (Phase 44 baseline) — corrected to 29.4.

### 3. σ_0 (Yukawa background normalization) — Match

**Paper uses:** 0.052 cm²/g (passed in scripts as sigma_0=0.052)
**Phase 44 free fit:** 0.0516 cm²/g (best_params[1])

Match within 1%. Scripts accept sigma_0 as a parameter.

### 4. a_slope (Yukawa background velocity exponent) — **CRITICAL MISMATCH [R86]**

**Scripts use:** a_slope = 1.0 (hard-coded in sigma_m_at_v calls)
**Phase 44 free fit:** a_slope = 1.93 (best_params[2])

This is the **biggest single quantitative error** in the paper's parameter usage.

**Effect on framework's σ/m at dSph velocities:**
- At a_slope = 1.0: σ/m(v=15) = 0.347 cm²/g
- At a_slope = 1.93: σ/m(v=15) = 2.01 cm²/g (6× larger)

**Effect on Horigome comparison (R86):** Factor 14-830× above threshold at dSph velocities, not factor 1.4-3× as R85 reported.

**Fix required:** Update all scripts (T235, T236, build_population_sigma_eff_map.py, build_species_dependent_sigma.py, plot_sigma_m_v.py) to use a_slope = 1.93 instead of 1.0.

### 5. σ_peak (resonance amplitude) — Match within 3% [R76]

**Paper uses:** 174 cm²/g (causality cap, constants.py SIGMA_PEAK_CM2_PER_G)
**Phase 44 free fit:** 178.5 cm²/g (best_params[4])

Paper uses 174 (the causality cap, per §9.12); Phase 44 free fit gave 178.5 unconstrained. Difference 3%. **R76 fix: use 174 (causality cap) consistently.**

### 6. σ_1 (Gaussian σ width) — Different parameterization [R76]

**Paper uses:** σ_1 = 4.4 km/s (single Gaussian)
**Phase 44 fit:** w1 = 430 km/s, w2 = 769 km/s, w3 = 196 km/s (three different widths for three resonances)

These are not directly comparable: Phase 44 used a 3-resonance parameterization (different channels with different widths), the paper uses a single Gaussian. R76: the paper's σ_1 = 4.4 is "phenomenological input chosen to satisfy the 8-channel dataset" — NOT from Phase 44 fit.

**Effect on dSph:** σ_1 = 4.4 gives some resonance contribution at v=15 (Gaussian tail). σ_1 → 0 would suppress it entirely.

### 7. T192 Ωh² — **WRONG m_χ [R87]**

**Paper claims:** Ωh² = 0.119 at δ = 0.43%
**T192 source:** thermal_avg_sigma_v(m_chi=10.3) — hard-coded default
**Framework uses:** m_χ = 1.0 GeV

T192 was computed at m_χ = 10.3 GeV, NOT the framework's m_χ = 1.0 GeV. The T221 Drobczyk-style construction at m_χ = 1 GeV gives a different (lower) Ωh² that was never computed.

**Per R86 reviewer:** "If Drobczyk's parameters don't match the framework's, then Drobczyk's relic density result doesn't apply to the framework at all."

**Fix:** Re-run T192 at m_χ = 1.0 GeV, m_Φh = 2.0 GeV; or remove the Ωh² claim entirely (R87 already removed from L1758 and abstract).

---

## Recommendations for pre-submission

1. **Update a_slope to 1.93 in all σ/m scripts.** (R86 critical.) 
   - Update scripts: T235, T236, build_population_sigma_eff_map.py, build_species_dependent_sigma.py, plot_sigma_m_v.py
   - Re-run R83 hierarchy derivation with a_slope = 1.93 (this changes σ_DM-DM(per particle) at v=28: 174 × 1.78e-24 = 3.1e-22, vs current σ_0 × (100/28)^1.93 = 0.60 cm²/g × 1.78e-24 = 1.07e-24 g. The hierarchy constraint is dominated by the resonance peak, but background now exceeds Horigome's threshold.)
2. **Re-run T192 at m_χ = 1.0 GeV.** (R87.) Or remove Ωh² claim.
3. **Verify σ_peak = 174 (causality cap) is used everywhere.** (R76.) Skip narrative verification.
4. **Document the m_χ choice explicitly in §2.6.** (R66.) The paper should state "we adopt m_χ = 1 GeV as a simplifying choice, distinct from Phase 44's 10.44 GeV baseline; this is a single-mediator Yukawa construction, not Phase 44's multi-resonance fit."
5. **Run a fresh Horigome comparison with a_slope = 1.93.** (R86 Path A or Path B.)

---

## Time estimate

- Update a_slope in 5 scripts: ~30 min
- Re-run hierarchy derivation: ~30 min
- Re-run T192 at m_χ = 1 GeV (T237): ~1 hr
- Update paper §2.6 with m_χ choice: ~15 min
- Update paper §10.7 hierarchy with a_slope = 1.93: ~15 min
- Total: ~2.5 hr

---

## Decision: which paper is this?

Per R86 reviewer's framing question:
- **Option (a): Negative-result paper.** Framework is excluded at dSph by Horigome at 10-27× threshold. Cloud-9 consistency check passed. Hierarchy constraint 10⁻¹³. The paper says "here's a framework that was built for Cloud-9, and here's the data that excludes it."
- **Option (b): Parameter-space paper.** Map the parameter space; identify which parameter combinations survive Horigome; specify conditions for viability.

**R88 recommendation:** Option (a) is honest. The framework's current parameters are not viable at dSph. A negative result that constrains the field is publishable.

---

*Audit completed 2026-10-03 per R86 reviewer recommendation*
*Stored at `v0.3-prelim/docs/SYSTEMATIC_PARAMETER_AUDIT_R88.md`*
*Time spent: ~15 minutes (Phase 44 fit read + parameter-by-parameter cross-check)*
*Estimated remaining work: ~2.5 hours for full pre-submission parameter fix*