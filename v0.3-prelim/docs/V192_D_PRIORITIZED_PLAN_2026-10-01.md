# v19.2-D Plan — Prioritized (R74, three resolutions applied)

**Date:** 2026-10-01
**Status:** v19.2-C milestone in `c486782`, R72 fixes in `7f82a7c`, R73 footnote in `4017499`
**Predecessor:** R73 plan review feedback (3 substantive issues, all resolved)

---

## R73 plan-reviewer feedback → R74 resolutions

### Issue 1 — D-5 numbers: "v_target = 28 vs 29.4" — RESOLVED

**Reviewer:** "The paper can't use v_target = 28 in §2.6 and v_target = 29.4 in constants.py. That's the same class of inconsistency as the m_χ = 1.0 vs 10.44 problem."

**Resolution:** **v_target = 29.4 km/s** (Phase 44 free-fit value, used in constants.py). The Phase 44 free fit landed on v_target = 29.36 km/s (best_params[3] in `phase44_joint_fit.json`); constants.py uses 29.4; paper §2.6 line 152 historically used 28 (the Phase 44 baseline starting point). The free-fit value is the actual science.

**Patch applied (R74):**
- Paper §2.6 line 152: 28 → 29.4
- Paper §2 line 114: 2.56 → 1.17 cm²/g (the v_target=29.4 value at V_max=15 km/s)

**Numerical impact:** σ/m(V_max=15 km/s, Fornax dSph) = 0.347 (background) + 0.822 (Gaussian tail at v_target=29.4) = **1.17 cm²/g** (was 2.56 cm²/g). Within paper's claimed dSph range (0.5–2.5 cm²/g). dSph gravothermal prediction t_core = 0.7–6.3 Gyr qualitatively unchanged.

### Issue 2 — g_N/g_χ: "keep both" hides factor 3.6 — RESOLVED

**Reviewer:** "R72's ratio derivation is closer to the paper's actual statement ('ratio of empirical anchors'). If the paper is going to state two values, it should say which is derived from what, and which the paper recommends."

**Resolution:** **Primary = g_N/g_χ < 3 × 10⁻¹¹** (R57 derivation, used in thesis + abstract + downstream §10.4 + §10.5); **Footnote = g_N/g_χ < 7.5 × 10⁻¹²** (R72 ratio derivation, supports same conclusion).

**Patch applied (R74):** §10.7 R73 footnote restructured as PRIMARY/FOOTNOTE with explicit anchoring note (R57 uses g_χ = 2.93×10⁻³ from constants.py; R72 uses cross-section ratio at v=15 km/s).

### Issue 3 — Figure rendering: must-do vs if-time — RESOLVED

**Reviewer:** "If v1.0 has figures (and the plan says it does: 'v1.0 has at minimum the σ/m(v) multi-channel figure (§3) and the hierarchy constraint figure (§10.7)'), then rendering is a hard prerequisite for D-17. Move it to DO NOW."

**Resolution:** Figure rendering moved from "if time permits" to DO NOW. v1.0 has figures → rendering must precede D-17.

### Smaller items addressed

- **D-5 outcome definitions sharpened:** Decision is whether w_lim (FWHM) < 3.0 km/s OR w_lim = 4.4 km/s. **Criterion:** likelihood ratio against current w=4.4 fit; report Δlog L and χ²/dof; if Δlog L > 5 (significant), adopt the new value; if not, keep w=4.4.
- **D-5 cost:** 4-6 hours (not 2-3) given v_target resolution needs the entire fit to re-run; downstream §3.3 + §9.12 numbers shift.
- **Abstract readability:** Plan now says: lead with thesis sentence; 1-2 supporting claims; cut to ~150 words (from ~290); abstract explicitly opens with "We present a systematic exploration..."
- **D-5 downstream propagation:** if FWHM changes from 4.4 to 3.0, paper presents BOTH values; for now w=4.4 stays as primary with w=3.0 as "narrow resonance alternative" caveat in §2.6.

---

# DO NOW (15-20 hours total)

### 1. R74 v_target + σ/m patches (DONE in this commit)

**Done:** v_target = 29.4 in §2.6 line 152; σ/m(15) = 1.17 cm²/g in §2 line 114.

### 2. D-5 — σ_peak width test (CORRECTED rationale)

**Cost:** 4-6 hours
**Why this matters:** Live tension between dSph non-collapse and Cloud-9 bulk. With v_target=29.4 (R74), w=4.4 km/s, σ/m(V_max=15) = 1.17 cm²/g (was 2.56). Balberg+ at σ/m=1.17 and V_max=15 km/s gives t_core ~ 0.7–6.3 Gyr — **contradicts dSph non-collapse**. Outcome:
- Fits with w_lim < 3.0 km/s: dSph tension resolves; paper §2.6 / §3.3 / §9.12 all updated
- Fit fails (still requires w=4.4): dSph gravothermal tension is a **real framework constraint**

**Test method:** Re-run Phase 44 free fit with dSph likelihood added; sweep w ∈ {1.0, 2.0, 3.0, 4.0, 4.4, 6.0} km/s; report likelihood ratio against w=4.4 baseline.

### 3. D-8 — Post-diction audit (finish R58)

**Cost:** 2 hours
**Why this matters:** R58 introduced the distinction; didn't complete the audit.
**Output:** A table in §3 or §11 listing every quantitative claim × (source: post-diction / measurement / prediction).

### 4. D-13 — Reference audit (must-do)

**Cost:** 4-6 hours (50 entries × 5-7 min average)
**Why this matters:** Four citation corrections in last 40+ rounds (R33, R41, R42, R46). Submission requirement.
**Method:** ADS access preferred, arXiv abstract fallback per paper convention.

### 5. Abstract readability pass

**Cost:** 1 hour
**Method:** Lead with thesis sentence (R68 form): "The framework's σ_peak = 174 cm²/g is a phenomenological fit, not a UV-derived prediction. Its compatibility with LZ requires, for a single-mediator Yukawa completion, a dark-sector hierarchy of order 10⁻¹¹..." Then 1-2 supporting claims (Mace+ comparison; 5 UV no-go theorems). Cut to ~150 words from current ~290.

### 6. Figure rendering (MUST-DO before D-17)

**Cost:** 2-4 hours
**Why this matters:** v1.0 has at minimum the σ/m(v) multi-channel figure (§3) and the hierarchy constraint figure (§10.7). Must precede D-17.
**Figures needed:**
- σ/m(v) multi-channel figure (§3): 8 channels (SPARC, Cloud-9, dSph, UFD, Cluster, JVAS, etc.)
- Hierarchy constraint figure (§10.7): g_N/g_χ plane + σ_SI vs LZ bound
- (Optional) Gravothermal cascade figure (§2.6)
- (Optional) No-go theorems summary figure (§10.2)

### 7. D-17 — PDF build (depends on figures)

**Cost:** 1-2 hours
**Why this matters:** Submission requires PDF.

---

# DO IF TIME PERMITS

(Empty — all submission-blocking items are above)

---

# DROP (don't pursue, per R72 reviewer)

- **D-1** Joint SIDM+LZ fit: R72 guidance, no change to conclusions
- **D-4** σ/m fresh-MCMC: refines numbers already as constraints
- **D-6** UV re-derivation: 4 rounds + retraction last attempt
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
- **D-15** Master σ/m(v) figure — moved into v1.0 figures (item 6)
- **D-18** Figure rendering — moved into v1.0 MUST-DO (item 6)

---

# Revised total wall-clock

**Do-now priority:** 15-20 hours total (R74: done; D-5: 4-6 hr; D-8: 2 hr; D-13: 4-6 hr; abstract: 1 hr; figures: 2-4 hr; D-17: 1-2 hr)

**Realistic total per R72 reviewer:** "15-20 hours is realistic for the do-now list plus reference audit, and possibly 25-30 hours if D-5 turns into a real fit with corrections."

---

# What v19.2-D actually is, per R72

> "v19.2-D shouldn't be a parallel workstream. It should be a short list of blocking items for submission, followed by a natural stopping point."

**v19.2-D = pre-submission polish + reference audit + figures + PDF, not a research sprint.**

---

# Submission checklist

- [x] R72 ratio arithmetic fix (1.78e22, not 10^46)
- [x] R72 m_chi-independence statement for σ_peak = 174
- [x] R72 single-mediator coupling assumption note
- [x] R73 g_N/g_χ reconciliation footnote (PRIMARY=3e-10, footnote R72=7.5e-12)
- [x] R74 v_target = 29.4 km/s resolution (paper §2.6 line 152)
- [x] R74 σ/m(V_max=15) = 1.17 cm²/g (paper §2 line 114)
- [ ] D-5: σ_peak width test (with corrected v_target + σ/m)
- [ ] D-8: Post-diction audit finish
- [ ] D-13: Reference audit (50 entries; ADS or arXiv)
- [ ] Abstract readability pass (~150 words, lead with thesis)
- [ ] Figure rendering (σ/m multi-channel, hierarchy constraint)
- [ ] D-17: PDF build

---

*Plan revised 2026-10-01 per R73 reviewer comments*
*Stored at `v0.3-prelim/docs/V192_D_PRIORITIZED_PLAN_2026-10-01.md`*
*Will be re-uploaded as R74 (commit pending)*