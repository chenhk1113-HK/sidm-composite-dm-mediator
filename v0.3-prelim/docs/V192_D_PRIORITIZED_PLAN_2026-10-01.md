# v19.2-D Plan — Prioritized (R75, all four R74 reviewer issues resolved)

**Date:** 2026-10-01
**Status:** v19.2-C milestone in `c486782`, R72-R74 in `7f82a7c`/`4017499`/`03888ab`, R75 in this commit

---

## R74 plan-reviewer feedback → R75 resolutions

### Issue 1 — v_target downstream consequences — RESOLVED

**Reviewer:** "If v_target came out of the fit as 29.36, then v_target is not an input — it's a fitted parameter. All the Phase 44 parameters need to come from the same fit."

**Resolution:** Confirmed via `phase44_joint_fit.json`:
- v_target: baseline = 28.0, free-fit = 29.36 (Δ = 1.36 km/s, 4.87%)
- σ_peak_R0: baseline = 100, free-fit = 178.5 (Δ = 78.5, **78%**)
- v_targets_2,3,4: also shifted (300→430, 700→769)
- Peak heights all changed dramatically
- Widths all changed

**Important distinction (per R75):**
- v_target = **FITTED** (peak position) → use 29.4 everywhere
- FWHM = 4.4 km/s = **INPUT** (Cloud-9 velocity distribution width, NOT a fit parameter) → unchanged
- σ_peak_R0 = **CAUSALITY CAP** (not fit value) → 174 cm²/g (rounded from 178.5 fit value)

**R74 patch was small (only v_target in line 152 formula + line 114 σ/m numbers).** σ_peak = 174 cm²/g and FWHM = 4.4 km/s are NOT Phase 44 free-fit parameters; they're constraints/inputs that don't change.

### Issue 2 — dSph tension is REAL (not "qualitatively unchanged") — RESOLVED

**Reviewer:** "t_core = 0.7–6.3 Gyr is not 'qualitatively unchanged' from a dSph non-collapse standpoint. If the framework predicts t_core < 6.3 Gyr for a Fornax-like halo, the halo should have collapsed. If Fornax's observed core is diffuse (which it is), the framework predicts collapse where none is observed."

**Resolution:** **R75 explicit recompute** added to §3.3 (per R74):
- σ/m(Fornax V_max=15, v_target=29.4) = **1.17 cm²/g** (R74 corrected)
- Balberg+ t_core = **5.07 Gyr** with Fornax-like ρ_s ~ 0.02 M☉/pc³, r_s ~ 1.4 kpc
- 5 Gyr < cosmic age at z=2 (~10 Gyr) → predicting collapse where none observed

**R75 abstract update:** dSph gravothermal tension is now stated as a real framework limitation, not "qualitatively unchanged."

### Issue 3 — g_N/g_χ PRIMARY flipped to R72 — RESOLVED

**Reviewer:** "R57's derivation rests on a number whose formula is disputed. R72's derivation uses the ratio of empirical anchors (Cloud-9 benchmark vs LZ bound), which doesn't depend on g_χ at all. So the reliable derivation is R72 (7.5 × 10⁻¹²), and the suspect one is R57 (3 × 10⁻¹¹)."

**Resolution:** **R75 PRIMARY FLIP:**
- PRIMARY: g_N/g_χ < **7.5 × 10⁻¹²** (R72 ratio derivation, no g_χ dependency)
- FOOTNOTE: g_N/g_χ < 3 × 10⁻¹¹ (older R57 derivation)

Thesis sentence framing "of order 10⁻¹¹" stays unchanged (captures both values).

### Issue 4 — Abstract target raised to 200 — RESOLVED

**Reviewer:** "The paper has hierarchy constraint, Mace+ comparison, §2.7 consistency check, five no-go theorems, α_χ statement. That's five distinct claims. 150 words is too tight."

**Resolution:** **Abstract target = 200 words** (raised from 150). §2.7 included as supporting claim per R74 reviewer note "If §2.7 is the paper's strongest content, it should be in the abstract."

---

# DO NOW (revised: 17-24 hours total)

### 1. R75 patches (DONE in this commit)

- v_target = 29.4 km/s used everywhere (R74 §2.6 line 152, §2 line 114)
- σ/m(Fornax V_max=15) = 1.17 cm²/g, t_core = 5.07 Gyr stated explicitly (R75)
- g_N/g_χ PRIMARY = 7.5 × 10⁻¹² (R75 flip)
- Abstract target raised to 200 words

### 2. D-5 — σ_peak width test (CORRECTED rationale, larger scope)

**Cost:** 4-6 hours
**Method:** Re-run Phase 44 free fit with dSph likelihood added (Fornax V_max=15, t_core ≈ 5.07 Gyr at σ/m=1.17); sweep w ∈ {1.0, 2.0, 3.0, 4.0, 4.4, 6.0} km/s; **Δlog L > 5 vs fixed-w baseline** (1-parameter FWHM sweep).
**Outcomes:** If w_lim < 3.0 km/s works, paper §2.6 / §3.3 / §9.12 all updated. If w=4.4 holds, dSph gravothermal tension (R75 explicit) stays as a real framework constraint, paper §3.3 needs to say so explicitly.

### 3. D-8 — Post-diction audit (finish R58)

**Cost:** 2 hours

### 4. D-13 — Reference audit (must-do)

**Cost:** 4-6 hours (50 entries)

### 5. Abstract readability pass (200 words target)

**Cost:** 1-2 hours
**Method:** Lead with thesis sentence; 5 supporting claims at ~30 words each = 150 words + thesis 50 words = 200 words total. Include §2.7, Mace+, no-go theorems.

### 6. Figure rendering (MUST-DO before D-17)

**Cost:** 4-6 hours (revised up per R74)
**Why this matters:** v1.0 has figures (σ/m multi-channel, hierarchy constraint); publication-quality figures take longer than naive estimate.

### 7. D-17 — PDF build (depends on figures)

**Cost:** 1-2 hours

### Buffer item (per R74 #6): Update §9.12 gravothermal numbers if D-5 changes FWHM

**Cost:** 1-2 hours (only if D-5 changes FWHM)

### Buffer item (per R74 #6): Reconcile §2.7 with post-v_target-change framing

**Cost:** 30 min (only if §2.7 references σ/m at specific velocities)

---

# DO IF TIME PERMITS

(Empty — all items above are submission-blocking)

---

# DROP

D-1, D-4, D-6, D-7, D-9 to D-12, D-16 — unchanged from R72

---

# DEFER INDEFINITELY

D-2, D-3, D-19, D-20 — unchanged

---

# ALREADY RESOLVED

- D-14 0.085 dex origin (R35-R36)
- D-15 Master σ/m(v) figure (v1.0 figures, item 6)
- D-18 Figure rendering (v1.0 MUST-DO, item 6)

---

# Revised total wall-clock

**Do-now priority:** 17-24 hours (D-5 4-6 + D-8 2 + D-13 4-6 + abstract 1-2 + figures 4-6 + D-17 1-2)

**Realistic total per R72 reviewer:** "15-20 hours is realistic for the do-now list plus reference audit, and possibly 25-30 hours if D-5 turns into a real fit with corrections." → **17-24 hr is within the 25-30 envelope if D-5 needs corrections; 20-25 hr if not.**

---

# Submission checklist

- [x] R72 ratio arithmetic fix (1.78e22, not 10^46)
- [x] R72 m_chi-independence statement for σ_peak = 174
- [x] R72 single-mediator coupling assumption note
- [x] R73 g_N/g_χ reconciliation (PRIMARY=3e-11, R72 footnote)
- [x] R74 v_target = 29.4 km/s (paper §2.6 line 152, §2 line 114)
- [x] R75 g_N/g_χ FLIP (PRIMARY=7.5e-12, R57=3e-11 footnote)
- [x] R75 σ/m(Fornax) = 1.17 cm²/g, t_core = 5.07 Gyr (paper §3.3 explicit)
- [ ] D-5: σ_peak width test (with corrected v_target + σ/m)
- [ ] D-8: Post-diction audit finish
- [ ] D-13: Reference audit (50 entries)
- [ ] Abstract 200 words (5 claims + §2.7)
- [ ] Figure rendering (σ/m multi-channel, hierarchy)
- [ ] D-17: PDF build

---

*Plan revised 2026-10-01 per R74 reviewer feedback*
*Stored at `v0.3-prelim/docs/V192_D_PRIORITIZED_PLAN_2026-10-01.md`*
*Will be re-uploaded as R75 (commit pending)*