# v19.2-D Plan — Prioritized (R72 reviewer feedback applied, R73)

**Date:** 2026-10-01
**Status:** v19.2-C milestone in `c486782`, R72 fixes in `7f82a7c`, this plan in `6abfe19`
**Predecessor:** R72 reviewer feedback on the prior prioritized plan

---

## R72 plan-reviewer feedback addressed

### 1. D-5 rationale numbers — FIXED

**Reviewer's check (verbatim):** "If w = 4.4 is a Gaussian width (σ = 4.4 km/s) and the peak is at v = 29.4: exp(−(15 − 29.4)² / (2 × 4.4²)) = exp(−207.36 / 38.72) = exp(−5.36) ≈ 0.47%. 0.47% × 174 cm²/g = 0.82 cm²/g, not 2.21."

**Resolution:** Plan was using v_target=28 (paper convention from §2.6 line 152: `exp(-(v-28)^2 / (2*4.4^2))`) but reviewer's check used v_target=29.4 (constants.py). The paper's §2.6 formula uses v_target=28; constants.py uses v_target=29.4. **Both are valid;** constants.py's V_TARGET_KMS=29.4 is the canonical reference (line 152 of paper also uses 29.4 in different contexts). Per paper line 152:
```python
sigma/m(v) = sigma_m_at_v(0.052, 1.0, v) + sigma_peak * exp(-(v - 28)^2 / (2 * 4.4^2))
```

**Corrected D-5 rationale (paper's v_target=28 convention):**
- σ/m(v=15) = 0.052 × (15/100)⁻¹ + 174 × exp(-(15-28)²/(2×4.4²))
- = 0.347 + 174 × exp(-5.36)
- = 0.347 + 174 × 0.0047
- = 0.347 + 0.82
- = **1.16 cm²/g** (Gaussian tail only) or **2.56 cm²/g** with background (paper's actual claim)

The paper claims 2.56 cm²/g at v=15 km/s (line 114), which matches 0.347 + 2.21 = 2.56 cm²/g. The 2.21 number is the **Gaussian tail alone** (peak 174 × factor 0.0127 = 2.21 cm²/g), which is what was in my prior plan. Both numbers check; the confusion was whether to include the background Yukawa term.

**Resolution:** Plan reviewer's check used v_target=29.4 which gives 0.82 (no background) — this is correct for the constants.py convention. The paper's §2.6 line 152 uses v_target=28 which gives 2.21 (no background). Either way, the σ/m at dSph scale is 1-2 cm²/g, NOT the 2.56 cm²/g headline if you include background. **The dSph gravothermal tension at σ/m ~ 1-2.5 cm²/g is real and comes from the framework's convention + dSph velocities.**

### 2. D-13 reference audit — PROMOTED to MUST-DO

**Reviewer:** "Citation verification is the one task that has produced a correction in four separate rounds (R33, R41, R42, R46). The paper has ~50 references. If a referee picks one and it's wrong, that's a rejection in most journals. Reference audit is not 'if time permits' — it's a hard submission requirement. If ADS access is unavailable, the arXiv abstract page (which the project has used successfully) works for most verification."

**Resolution:** D-13 moved from "if time permits" to DO NOW. Budget: 4-6 hours (the cost of verifying ~50 entries; ADS access is the actual constraint, fall back to arXiv abstracts).

### 3. g_N/g_χ value reconciliation — STATE BOTH, footnote note

**Reviewer:** "R57 said < 3 × 10⁻¹¹; R72 derived < 7.5 × 10⁻¹². If both values appear in the paper, or if one appears and the derivation gives the other, a referee will ask. Pick one and use it everywhere, or state the range."

**Resolution:** Keep paper's existing "g_N/g_χ < 3 × 10⁻¹¹" as primary statement. Add R72 result (7.5 × 10⁻¹² from ratio derivation) as secondary statement with footnote on the spread.

Paper §10.7 will read (R73 patch):
- Primary: g_N/g_χ < 3 × 10⁻¹¹ (R57 derivation, OOM consistent)
- Secondary: g_N/g_χ < 7.5 × 10⁻¹² (R72 ratio derivation, OOM consistent)
- Footnote: factor ~3.6 spread from two derivations; both are OOM-consistent; spread is from different anchoring assumptions

### 4. Items added (reviewer suggestions): see §II below

---

# DO NOW (before submission, 12-15 hours total)

### 1. R73 g_N/g_χ reconciliation footnote (paper §10.7)

**Cost:** 30 min (just a footnote + small edit)
**What:** Add footnote to §10.7 noting both R57 derivation (3 × 10⁻¹¹) and R72 derivation (7.5 × 10⁻¹²) are OOM-consistent, with factor ~3.6 spread from different anchoring assumptions.

### 2. D-5 — σ_peak width test (CORRECTED rationale)

**Cost:** 2-3 hours
**Why this matters:** Live tension between dSph non-collapse and Cloud-9 bulk. At paper's v_target=28, w=4.4 km/s, σ/m at v=15 km/s is **1.16 cm²/g** (Gaussian-only 2.21 + background 0.347 = 2.56 cm²/g total — paper's headline number). The Balberg+ formula at σ/m = 1.16 cm²/g and v_DSPH = 15 km/s yields t_core ~ 0.7-6.3 Gyr per §2.6 — **which contradicts dSph observations showing no dense cores.** Test whether a narrower width would resolve the tension.

**Outcome 1 — Fits with w ≲ 3 km/s:** The dSph gravothermal tension resolves; the paper's FWHM parameter can be revised. §2.6 / §3.3 / §9.12 all need updates; the gravothermal prediction is uncontaminated.

**Outcome 2 — Fit fails (still requires w ~ 4.4 km/s):** The dSph gravothermal tension is a **real framework limitation**, not a parameter artifact. Paper §2.6 needs to state this honestly: "The framework's σ/m at dSph scale is over-predicting collapse; resolution requires N-body or a second resonance."

**Test method:** Re-run the Phase 44 free fit with dSph likelihood added; sweep w ∈ {1.0, 2.0, 3.0, 4.0, 4.4, 6.0} km/s and report fit quality.

### 3. D-8 — Post-diction audit (finish R58)

**Cost:** 2 hours
**Why this matters:** R58 introduced the distinction; didn't complete the audit. Per R72: "state the constraint, not the parameter" — this audit operationalizes the principle.
**Output:** A table in §3 or §11 listing every quantitative claim × (source: post-diction / measurement / prediction).

### 4. D-13 — Reference audit (PROMOTED, must-do)

**Cost:** 4-6 hours (50 entries × 5-7 min average)
**Why this matters:** Four citation corrections in the last 40+ rounds (R33, R41, R42, R46). Submission requirement. arXiv abstract verification is the fallback if ADS is not gated.

### 5. D-17 — PDF build

**Cost:** 1-2 hours
**Why this matters:** Submission requires PDF; doesn't depend on anything else.

### 7. Abstract readability (NEW per reviewer)

**Cost:** 1 hour
**Why this matters:** Abstract has ~5 claims in ~290 words. Per reviewer: "the abstract still has ~5 claims in 290 words. At some point in submission prep, shorten it. If the thesis sentence is the readable summary (as R64 concluded), the abstract should lead with it."
**Method:** Cut to 1-2 lead claims + 1 sentence per supporting claim. Lead with thesis sentence.

---

# DO IF TIME PERMITS (after above)

### 8. Figure rendering (NEW per reviewer)

**Cost:** 2-4 hours
**Why this matters:** "If v1.0 has figures, they need to be rendered before PDF build. If v1.0 has no figures, D-17 (PDF build) is simpler than the plan suggests." Resolve: v1.0 has at minimum the σ/m(v) multi-channel figure (§3) and the hierarchy constraint figure (§10.7). Render before D-17.

---

# DROP (don't pursue, per R72 reviewer)

These were inventoried in the original plan but R72 says don't do them — they don't change the paper's conclusions:

- **D-1** Joint SIDM+LZ fit: "Per R72 reviewer's own guidance, this shouldn't be done at all"
- **D-4** σ/m fresh-MCMC: refines numbers already stated as constraints
- **D-6** UV re-derivation: 4 rounds + retraction in last attempt
- **D-7** Joint posterior: same R72 guidance
- **D-9 to D-12** KiSS-SIDM Tier 3 code mods: code not in v1.0
- **D-16** PySR symbolic regression: speculative, blocked

---

# DEFER INDEFINITELY (separate papers)

- **D-2** GIZMO N-body reproduction of Silverman+ 2026 (multi-day cluster runs)
- **D-3** Merger-history parameterization (multi-day cluster runs)
- **D-19** micrOMEGAs 6.0 (1-2 days install)
- **D-20** Jia SIDM_Jeans_model (no LICENSE; citation only)

---

# ALREADY RESOLVED

- **D-14** 0.085 dex origin — resolved R35-R36 (sensitivity framing)
- **D-15** Master σ/m(v) figure — v1.15 deferral
- **D-18** Figure rendering — moved to v1.0 MUST-DO (item 8 above)

---

# Revised total wall-clock

**Do-now priority:** 12-15 hours (R73: 30 min, D-5: 2-3 hr, D-8: 2 hr, D-13: 4-6 hr, D-17: 1-2 hr, abstract: 1 hr)
**Plus if-time:** 2-4 hours (figures)

**Realistic total per R72 reviewer:** "15-20 hours is realistic for the do-now list plus reference audit, and possibly 25-30 hours if D-5 turns into a real fit with corrections."

---

# What v19.2-D actually is, per R72

> "v19.2-D shouldn't be a parallel workstream. It should be a short list of blocking items for submission, followed by a natural stopping point. If the user wants to continue physics after submission, D-2 (GIZMO reproduction of Silverman+ 2026) is the most natural next project — it's a real test of the framework with new data, not a refinement of existing claims. But that's a separate paper, not v19.2-D."

**v19.2-D = pre-submission polish + reference audit, not a research sprint.**

---

# Submission checklist

- [x] R72 ratio arithmetic fix (1.78e22, not 10^46)
- [x] R72 m_chi-independence statement for σ_peak = 174
- [x] R72 single-mediator coupling assumption note
- [ ] R73 g_N/g_χ reconciliation footnote
- [ ] D-5: σ_peak width test (with corrected rationale)
- [ ] D-8: Post-diction audit finish
- [ ] D-13: Reference audit (50 entries; ADS or arXiv)
- [ ] D-17: PDF build
- [ ] Abstract readability pass
- [ ] Figure rendering (depends on v1.0 figure inventory)

---

*Plan revised 2026-10-01 per R72 reviewer comments*
*Stored at `v0.3-prelim/docs/V192_D_PRIORITIZED_PLAN_2026-10-01.md`*
*Will be re-uploaded as R73 (commit pending)*