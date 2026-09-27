# 2review.docx — Review of v18.40 Review Bundle

**Source:** `C:\Users\lamkuenai\AppData\Local\hermes\cache\documents\doc_59774f53a511_2review.docx`
**Date received:** 2026-09-26
**Reviewers:** 2 (anonymous, "reviewer 1" + "reviewer 2")

This document captures verbatim reviewer feedback on the v18.40 review bundle. Processed per Rule 29 (reviewer checklist as literal TODO list).

---

## Reviewer 1 — High-Level Assessment

### Standing Claim
> "still a **constraint map + no-go catalogue**, not a unified model. 6–7 of 8 under borrowed f_H; Cloud-9 vs dSph still open at Phase 44. v18.40's real additions are boundary refinements (T208–T212), not a new positive unification. That is the right direction after Path F1."

### What Improved

| Item | Assessment |
|---|---|
| T208 host-halo gravothermal | Strong, publishable negative: at Phase 44, t_core >> t_H; boosting σ/m enough to collapse breaks dSph. Closes a natural loophole. |
| T212 / Silverman+ 2026 | Important correction: collapse *can* run at σ/m ~ 10–70 cm²/g in ~ 10^10 M_sun halos. v18.40 correctly **trims** the claim. |
| Path A3 (Turini & Benítez-Llambay 2026) | Healthy epistemic move if literature supports treating Cloud-9's σ/m ≥ 50 as systematic upper-bound. Softens overcommitment to a single number. |
| Process | Negative results + literature recalibration after F1 is ordered science. |
| Honest front matter | Bundle header matches the mixed verdict; avoids "unified model achieved." |

### T210 (Crater II / Antlia II + Path A2) — Useful but Fragile

**Gating (Crater / Antlia):** Reasonable to ask whether Path F1 under borrowed f_H also hits other UDG-like systems. Scenario dependence on V_max (A–D) is right caution.

**Path A2 (sharp HL resonance near v~28):** Conceptually clear. The scan is a legitimate parameter probe.

**Concerns:**
1. **Cloud-9 floor is carried by σ_HH (Phase 44 peak), not by σ_HL.** The decompose script shows σ_peak,HL of order 0.3 contributes almost nothing toward σ_eff ≥ 50–128; you need huge σ_peak,HL or the HH Cloud-9 peak.
2. **Assigning Crater/Antlia floors of 30 at v=28** is memo-driven, not standard published σ/m(v) in same sense as Horigome-style dSph ceilings. Treat as **exploratory**, not as new hard channels in the abstract.
3. **Borrowed f_H still does the heavy lifting** for any "PASS." Same epistemic status as before.

**Verdict on T210:** Good diagnostic, not a new solution. Paper should not elevate Crater/Antlia to co-equal with Cloud-9/dSph without a dedicated observational methods section.

### T212 vs T208 — How to Phrase It

| Statement | Keep? |
|---|---|
| At Phase 44 σ/m, Cloud-9 host halo does not gravothermally collapse in Hubble time | **Yes** (T208) |
| At Silverman-like σ/m ≳ 10–70, collapse **can** run in similar-mass halos | **Yes** (T212) |
| Therefore gravothermal **never** unifies Cloud-9 and dSph | **Too strong** |
| Therefore gravothermal **at Phase 44 parameters** does not unify them; high-σ regimes that do collapse **overproduce** dSph σ_eff under naive enhancement | **Yes** |

v18.40's "Path B3 trim" is the right fix. Write it as a **regime split**, not a full retraction of T208.

### Path A3 (Cloud-9 as Systematic Upper Bound)

**Pros:** Reduces pressure to fit an extreme spike; aligns with "constraint map."

**Cons / duties:**
- Cite precisely (what they bound, assumptions, baryons vs SIDM).
- Do not silently drop Cloud-9 from the 8-channel story while still advertising Cloud-9 in the abstract.
- Either demote the channel in the table or keep it with an explicit "interpretation-dependent floor" flag.
- Without that precision, A3 looks like motivated softening.

### Bundle / Paper Hygiene Issues

1. **Version drift inside the bundle:** embedded paper status still says **v18.38** while tag is **v18.40**. Fix status line, abstract, §11, badges together.
2. **Windows absolute paths** in T210/T212 scripts (`C:\Users\...`) — break reproducibility; use relative `Path(__file__)`.
3. **Dual branch mention** (`wip/cloud-9-relhic` + multi-component) — fine if synced; say which is canonical for `df9aadd`.
4. **Abstract length / LZ digression** still dominates early reading; v18.40 refinements belong in §10, not a second abstract.
5. **"6–7 of 8"** remains tied to **borrowed** f_H; every headline table should keep that qualifier.

### Scientific Bottom Line for v18.40

```
Path F1 (v18.38): SPARC formula fixed; data resolution still f_H-dependent
T208: Host-halo gravothermal OFF at Phase 44
T212: Host-halo gravothermal ON at Silverman-like σ/m → high-σ collapse conflicts with dSph if applied naively
T210: Extra UDG-like systems + sharp-resonance scan = diagnostics
Path A3: Possible demotion of Cloud-9 floor to systematic bound
Net: Map refined; unification not achieved; honesty preserved
```

That is **progress of the right kind**: tighter boundaries, not a forced 8/8.

### Recommendations

1. **Ship v18.40** as "constraint map + refinements," with T208 and T212 as a **paired** §9.12/§10.4 subsection (regime-dependent gravothermal).
2. **Path A3:** only if Turini paper is quoted accurately; otherwise keep Cloud-9 as a disputed floor.
3. **T210:** appendix or short §3.x "related systems," not abstract-level channels, until V_max and published σ/m are settled.
4. **Do not** restart multi-week KiSS two-species work for unification; T208/T212 already frame the gravothermal story.
5. **One freeze:** status = v18.40 everywhere; relative paths; single canonical branch pointer.

### Reviewer 1 Overall Grade

| Dimension | Comment |
|---|---|
| Honesty | Strong — still constraint map |
| New physics claims | Appropriately modest |
| Negative results | High value (T208 + regime trim T212) |
| Risk of overclaim | Medium on Crater/Antlia and A3 if under-cited |
| Publishability direction | Better as a **tension + no-go** paper than as a solution paper |

**Summary:** v18.40 is a solid refinement release. The important scientific content is the **Phase-44 vs high-σ gravothermal split** and the continued refusal to claim unification. Polish version consistency and keep new UDG/Cloud-9 reinterpretations carefully scoped, and the bundle is in good shape to stand as the current scientific position.

---

## Reviewer 2 — High-Level Assessment

### Overall

This is an exceptionally thorough and unusually honest research bundle. The authors have done something rare: they've documented a multi-year investigation whose central ambition (unifying Cloud-9's high σ/m with dSph upper limits) fails, and they've catalogued exactly why, with multiple independent lines of evidence. The "constraint map + no-go catalogue" framing is accurate.

**However**, this is not one paper — it's at least two, possibly three, and the current monolithic draft undermines its own strongest content.

### 1. Scientific Content

#### 1.1 The Core Structural Tension Is Real and Well-Established

The central problem — Cloud-9 requires σ/m ≥ 50 cm²/g at v ≈ 28 km/s while dSph kinematics require σ/m ≤ 0.8 cm²/g at v ≈ 15 km/s — is a genuine ~60× ratio across a 13 km/s gap. T208/T210/T211/T212 investigations converge on this being structural.

**Verdict:** The structural ceiling is well-supported. The paper's honest verdict (6–7 of 8 channels under borrowed f_H; 4 of 8 under physically motivated f_H) is defensible.

#### 1.2 The "Borrowed f_H" Prescription Is Doing Too Much Work

**Strongest scientific criticism.** The paper's headline "6–7 of 8 channels" number is entirely dependent on hand-picked f_H values (~0.85 / 0.30) that:
- Were initially attributed to Yang+ 2025 Fig. 2
- Were shown (v18.29) to not match Yang+ 2025 Fig. 2
- Are not reproduced by the project's own T202 N-body check (f_H ≈ 0.92 uniform)
- Are not reproduced by T183 fluid (f_H ≈ 0.61)

The paper is admirably explicit about this in §9.6 and §9.7, but the abstract and introduction still lead with "6–7 of 8." A reader who stops at the abstract will come away with a misleading impression.

**Recommendation:** Lead with "4 of 8 under physically motivated f_H; 7 of 8 only under retracted borrowed f_H." The honest framing should be the headline, not the caveat.

#### 1.3 The Five No-Go Theorems Are Solid but Narrow

Each is individually well-argued. However:
- They target specific UV constructions, not the framework itself.
- T184 ("one-mediator UV systematic") is qualitatively different — it's a general statement, not a specific construction. The "five" count is slightly inflated; it's more like four specific + one systematic.
- The no-gos are tested against the Phase 44 single-component baseline, not the T163 KK-tower best fit. The paper acknowledges this (§10.2 scope caveat) but doesn't re-run them. **Real gap.**

**Recommendation:** Either re-run the no-gos against T163 parameters or clearly state they apply to Phase 44 only. Current framing "All five verdicts are independent of the specific cross-section values" is asserted but not demonstrated.

#### 1.4 The Two-Mediator Candidate Is the Strongest Positive Result

Drobczyk two-mediator UV completion is genuinely interesting: decouples annihilation (heavy Φh resonance) from self-scattering (light φ), achieving Ωh² = 0.119 with CHARM-compliant g_h_SM = 0.00040. The δ = 0.43% detuning is 5× broader than Drobczyk's benchmark, borderline-natural but not fatal.

**However:** This addresses thermal relic density only, not Cloud-9. The paper is explicit about this (§10.3 scope clarification), but the abstract's "three independent observational anchors" framing could mislead. The two-mediator candidate is a relic solution, not a Cloud-9 solution.

#### 1.5 The LZ Section Is Disproportionate

The LZ September 2026 event analysis (§3.5a, supplementary §S6) is ~10% of the paper's length for a 2.6σ marginal single-event observation that the model doesn't explain anyway.

**Recommendation:** Compress to a single paragraph; move audit trail to supplementary or a separate note.

### 2. Technical Issues in the Code

#### 2.1 T208 (T208_path_b_cloud9_host_halo_gravothermal.py)

- **Unit conversion inconsistency:** SIGMA_CODE = 2.088e-4 * 50 works through contradictory conversions; final value is correct for KiSS-SIDM convention but derivation is muddled.
- **v_max_from_M_c takes c but doesn't use it:** Function signature includes c but formula V_max = sqrt(G·M/r_vir) ignores concentration. For NFW, V_max occurs at r_s, not r_vir, so this systematically underestimates V_max by ~20–30%. Propagates into t_core.
- **Causality check:** t_core / t_cross computed but "causality cap" of 3.0 is asserted without derivation. Where does 3.0 come from? Should be referenced (Balberg+ 2002 §III?).

#### 2.2 T209 (t209_cloud9_nbody_setup.jl)

- **NFW sampling bug:** In nfw_sample_r, acceptance condition `if rand(rng) < rho_proportional * (x * (1 + x)^2) / 1.0` evaluates to rand() < 1.0 always, because rho_proportional = 1/(x(1+x)²). The function accepts every sample — uniform sampling, not NFW sampling. **Significant bug.**
- **Velocity sampling is not NFW phase-space:** randn() * 0.1 * V_max gives cold Gaussian, not proper NFW distribution function.
- **Particle count:** 100,000 heavy + 100,000 light is at low end for resolving gravothermal core-collapse. KiSS-SIDM examples use 10⁶–10⁷.
- **M_RATIO = 3.0 vs m_heavy/m_light:** If FRAC_H = 0.5 and N_HEAVY = N_LIGHT, then m_heavy = m_light, violating 3:1 ratio.

**Verdict:** T209 setup is not ready to run as-is. These are fixable bugs, but suggest N-body path was not carefully validated before the architectural discovery (KiSS-SIDM is single-component) halted it.

#### 2.3 T210 (t210_gating_test_crater_antlia.py)

- **width_HL = 50.0 hardcoded** in evaluate_sigma_eff, inconsistent with scan script where width_HL is free parameter.
- **σ_unc = 10.0 for Crater II/Antlia II** is asserted without justification.
- **V_max scenarios A–D:** Scenarios C (15 km/s) and D (28 km/s) are not derived from observations. Memo acknowledges but scan uses 28 km/s for "floor" comparison, which biases toward failure.

#### 2.4 T212 (t212_silverman_gravothermal.py)

- **t_cross_Gyr_from_r_vir_vmax uses r_vir, not r_s:** Crossing time should be defined at scale radius (where V_max occurs), not virial radius. Using r_vir overestimates t_cross by factor of ~c ≈ 12. **Affects causality check.**
- **Threshold σ/m values:** Coarse step size (0.052 → 1 → 10 → 50 → 70 → ...) misses actual threshold (1.12 cm²/g per T208).

### 3. Presentation and Structure

#### 3.1 The Paper Is Too Long and Too Repetitive

157 KB of markdown for a paper that is, at its core, a constraint map with negative results. "Honest verdict" stated at least a dozen times across abstract, introduction, §9, §10, §11. LZ section is disproportionate. §10.4 subsections (a through e) are essentially a lab notebook.

**Recommendation:** Split into:
- Paper 1: Multi-resonance phenomenology + constraint map + five no-go theorems (main paper)
- Paper 2: Two-mediator UV completion (Drobczyk extension) — deserves its own focused treatment
- Technical notes: T208–T212 as supplementary or separate notes

#### 3.2 The "6–7 of 8" Headline Should Be Retired

Number is:
- Prescription-dependent (7 under borrowed, 4 under Yang+/T202)
- Based on retracted f_H values
- Undermined by SPARC structural failure
- Not a "model dominates data" claim (Burkert wins on rotation curves)

The paper knows all this. But the abstract still leads with "6–7 of 8."

**Replace with:** "4 of 8 channels under physically motivated f_H; 7 of 8 only under retracted borrowed f_H."

#### 3.3 The Writing Style Is Lab-Notebook, Not Paper

"per the v18.32 honest phenomenological audit," "per DeepSeek review2," "per Reviewer15 R2," "per the 2026-09-17 user decision" — everywhere. Useful for internal audit trail but do not belong in a journal submission.

**Recommendation:** Move all "per X review" attributions to acknowledgements or supplementary.

#### 3.4 The Abstract Is Enormous

~1,200 words. Journal abstract should be 150–250 words.

**Recommendation:** Cut to ~250 words covering: (1) what framework is, (2) what it achieves (4–7 of 8 channels), (3) what it fails to achieve (Cloud-9 vs dSph), (4) five no-gos, (5) two-mediator candidate.

### 4. Specific Claims That Need Attention

| Claim | Issue | Recommendation |
|---|---|---|
| "6–7 of 8 channels" | Depends on retracted f_H | Lead with 4 of 8; put 7 of 8 in caveats |
| "Five no-go theorems" | T184 is systematic, not specific | Say "four specific + one systematic" |
| "log B = 2.41 (moderate evidence)" | T205 σ_unc choices somewhat arbitrary | Show sensitivity to σ_unc; report range |
| "115/127 = 90.6% SPARC pass" | Consistency, not preference (Burkert wins) | Already caveated; keep |
| "Path F1 resolved under borrowed" | Borrowed f_H is retracted | State clearly that F1 resolves only under retracted prescription |
| "Thermal relic density solved" | Only for two-mediator candidate; not Cloud-9 | Already caveated; keep |
| "Cloud-9 4000× spike" | The 4000× number is never derived | Either derive it or drop the number |
| "MCMC recovers parameters within 1σ" | f_H posterior is prior-dominated | State explicitly |

### 5. What's Genuinely Valuable

1. **Structural tension result** (Cloud-9 vs dSph cannot be unified under standard Yukawa) — publishable negative result.
2. **Five no-go theorems** — useful for community, even if narrow.
3. **Two-mediator candidate** — genuine constructive result. CHARM-compliant parameter point is concrete target for B-factory/beam-dump searches.
4. **T208/T212 gravothermal analysis** — careful application of Balberg+ 2002 to new regime. Silverman+ 2026 refinement is important nuance.
5. **Audit trail** — exemplary. T135 retraction, T196–T201 LZ rate-calculation bugs documented honestly. This is how science should be done.

### 6. Recommendations

#### Immediate (before v18.41)

1. Fix T209 NFW sampling bug — current ICs are uniform, not NFW.
2. Fix T208 V_max formula — use r_s, not r_vir, for V_max.
3. Fix T212 t_cross definition — use r_s, not r_vir.
4. Re-run no-gos against T163 parameters (or clearly scope them to Phase 44).
5. Retire "6–7 of 8" headline — replace with "4 of 8 under physically motivated f_H."

#### Medium-term (v19.0)

6. Split the paper: phenomenology + no-gos (Paper 1); two-mediator UV completion (Paper 2).
7. Cut abstract to 250 words.
8. Move all "per X review" attributions to supplementary.
9. Compress LZ section to one paragraph + supplementary.
10. Add sensitivity analysis for T205 Bayes factor (σ_unc dependence).

#### Long-term

11. Run N-body simulation at Silverman+ parameters (σ/m = 70, M = 5×10⁹ M_sun, quiescent merger history) — the one concrete test that could settle whether gravothermal can produce Cloud-9 spike.
12. Implement full three-term decomposition with proper σ_HL velocity dependence (not just Lorentzian) — current Path F1 uses Lorentzian, which may not be physically motivated.
13. Consider whether unified-model ambition is the right goal. Paper's own evidence suggests it may not be achievable under standard Yukawa physics. If so, constraint map is honest endpoint, and paper should be framed accordingly from the start.

### 7. Summary

This is a rigorous, honest, and thorough investigation that has produced:
- **Negative result** (no unified model)
- **Positive result** (two-mediator relic candidate)

The negative result is publishable and valuable. The positive result deserves its own paper.

**Main weaknesses:**
- Presentation: too long, too repetitive, too much lab-notebook style
- Headline: "6–7 of 8" is misleading; "4 of 8" is the honest number
- Code bugs: T209 NFW sampling, T208 V_max formula, T212 t_cross definition
- Scope: no-gos are narrower than claimed; LZ section is disproportionate

**Main strengths:**
- Intellectual honesty: retractions documented, failures not hidden
- Multiple independent lines of evidence: T208/T210/T211/T212 all converge
- Constructive UV completion: two-mediator candidate is genuine contribution
- Audit trail: self-check protocol is exemplary

**Bottom line:** Framework is a constraint map, not a unified model. Paper should say so from first sentence of abstract. Presentation should be tightened to match substance. Two-mediator candidate should be spun out as its own paper. With these changes, this is a solid contribution to the SIDM literature.

---

## TODO: Process This Review (per Rule 29)

To be addressed in subsequent rounds. Critical items:

### Reviewer 1 — Immediate Fixes (Quick Wins)
- [ ] Verify version drift: embedded paper status says v18.38 vs tag v18.40 — check PAPER_V1_DRAFT.md, README.md, CURRENT.md, VERSION (re-verify all say v18.40)
- [ ] Windows absolute paths in T210/T212 — convert to `Path(__file__)`-relative
- [ ] Single canonical branch pointer for `df9aadd`
- [ ] T208 + T212 as **paired** §9.12/§10.4 subsection (regime-dependent gravothermal)
- [ ] v18.40 refinements stay in §10, not second abstract

### Reviewer 2 — Scientific Substance
- [ ] T209 NFW sampling bug fix (if we ever run it again)
- [ ] T208 V_max formula: use r_s not r_vir
- [ ] T212 t_cross: use r_s not r_vir
- [ ] Code the causality cap 3.0 reference (Balberg+ 2002 §III)
- [ ] Retire "6–7 of 8" headline → "4 of 8 under physically motivated f_H; 7 of 8 only under retracted borrowed f_H"
- [ ] Re-run no-gos against T163 (or scope to Phase 44)
- [ ] Cut abstract to 250 words
- [ ] Move "per X review" attributions to supplementary
- [ ] Compress LZ section

### Both reviewers agree on
- T208 + T212 is the right scientific story
- Honest framing preserved
- Two-mediator candidate deserves its own paper
- Audit trail is exemplary
- Ship as v18.40 with refinements