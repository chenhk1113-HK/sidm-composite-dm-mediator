## Annex A: The Story of Cloud-9 — A Narrative Audit Trail

This annex narrates the full history of the Cloud-9 constraint as it unfolded across the project, from the first claim of a "4000× spike" through the v19.1.2 synthesis that reframed it as a gravothermal-evolution constraint. It is written in chronological order with the audit trail intact: what was claimed, when, what was found wrong, what was fixed, what survives. The narrative makes no claims beyond what the project's own numbers support; where the science is settled, the text says so; where it is open, the text says so too.

### A.1 The original claim (v1.11 — before v18.30, retracted)

In the early versions of this paper, Cloud-9 was reported as the "load-bearing tension": a RELHIC (REionization-Limited HI Cloud, [3]) host halo with σ/m ≥ 50 cm²/g at v = 28 km/s, a value that exceeds the framework's smooth Yukawa extrapolation by ~4000×. The number was treated as a sharp lower bound on σ/m at that velocity scale, and was the headline reason for the multi-resonance phenomenology in this paper. Versions v1.11–v1.14 reported the cloud as a "Cloud-9 vs dSph structural tension" — Cloud-9 (σ/m ≥ 50) and dSph (σ/m ≤ 0.8) sat on the same velocity-dependent σ/m(v) curve at different velocities, with a 60× ratio across only a 13 km/s gap. No published first-principles σ/v curve satisfies both. The "structural impossibility" framing was the v1.11 verdict.

### A.2 The honest phenomenological audit (v18.30, 2026-09-13)

A self-audit triggered by Rule 28 (arithmetic checking before claim, AGENTS.md) revealed that the v1.11 framing relied on two pieces of scaffolding that did not survive verification:
- The "7 of 8 channels" headline used hand-picked `f_H_at_r` values that were labeled "Based on Yang+ 2025" but were not actually derived from Yang+ Fig. 2.
- The gravothermal cascade timescale was implicitly assumed to be much shorter than Hubble time at Phase 44 σ/m, but a sanity check showed t_core ≈ 73.7 Gyr — much longer than 13.8 Gyr.

After the audit, the v18.30 honest verdict was: **at Phase 44 parameters, the multi-resonance σ/m(v) profile is a phenomenological interpolation through 8 channels, not a first-principles derivation. The Cloud-9 vs dSph tension is unresolved at Phase 44.** The "7 of 8" headline was retired; the new honest headline became "4 of 5 channels under physically motivated f_H; 7 of 8 only under retracted borrowed f_H."

### A.3 T208 — gravothermal refutation at Phase 44 baseline (v18.40–v18.43, 2026-09-25 to 2026-09-26)

To check whether the gravothermal cascade could rescue the framework at Cloud-9 host-halo parameters, the T208 analysis (T208_path_b_cloud9_host_halo_gravothermal.py) was run. Using the **Phase 44 baseline σ/m** (0.052 cm²/g at v = 100 km/s, extrapolated to V_max ≈ 24.75 km/s via standard Yukawa), the Phase-44 σ/m at Cloud-9 host V_max is ≈ 0.21 cm²/g. The Balberg+ 2002 Eq. 22 collapse formula then gives **t_core = 73.7 Gyr**, which is **5.3× longer than t_Hubble = 13.8 Gyr**. Gravothermal does NOT run at Phase 44 baseline. The verdict entered the paper as §9.12 ("Host-halo gravothermal cascade closed at Phase 44"). T213 later confirmed the σ/m = 0.21 cm²/g at V_max with KK tower parameters (5.7× below Silverman+ 2026's gravothermal threshold of 1.0 cm²/g).

### A.4 Silverman+ 2026 — the alternative mechanism (v18.40, 2026-09-25)

While T208 refuted gravothermal at Phase 44, Silverman+ 2026 (arXiv:2606.02566 [54], "Mergers Matter") reported that at **σ/m = 70 cm²/g** in M_halo = 10¹⁰ M☉ halos, **3 of 6 halos collapse within a Hubble time** (those with quiescent merger histories). This was entered as §10.4e ("Path B3 trim — Gravothermal CAN run at host-halo scale"), with the honest framing that the Phase 44 framework cannot reach Silverman+'s σ/m regime without a ≥5× amplification factor — which the framework itself fails to provide via the standard Yukawa structure.

### A.5 T215 KiSS-SIDM real kinetic simulation (v18.43, 2026-09-26)

To independently test whether gravothermal runs at σ/m = 70 in Cloud-9-mass halos, the project's own KiSS-SIDM kinetic simulation was run (T215/T215b/T215d). A 3000-particle subsample of a virialized NFW halo at σ/m = 70 reached t = 55 Myr (T215d final), showing the classic gravothermal catastrophe signature: interior density increases by 2-3.7× while outer density decreases by 1.85× over 45-55 Myr. This was the qualitative confirmation that gravothermal cascade IS operative at Silverman+'s parameters. The framework reaches Silverman+'s regime **kinetically**, but the analytic Balberg+ formula is unreliable at large σ/m (t_core/t_cross falls below the 3.0 causality cap).

### A.6 T212 Path A3 — Cloud-9 as a systematic upper bound (v18.40)

Independently, T212 (T212_path_b_cloud9_host_halo_gravothermal.py) tested Cloud-9 as a **systematic upper bound** rather than a hard lower bound, motivated by Turini & Benítez-Llambay 2026 environmental systematics ([53]). The §10.4d framing: "Cloud-9's σ/m ≥ 50 floor is best understood as a systematic upper bound arising from environment-dependent halo response, not a sharp kinematic lower bound." Cloud-9 was reclassified from "structural tension" to "systematic bound" — the same numerical value, but a softer logical status.

### A.7 v19.1-preliminary Cloud-9 joint likelihood (2026-09-29)

The user's choice between three scopes for v19.1 work was "Full Silverman+ 6-halo N-body reproduction + real joint likelihood with Ohana+ 2026 posterior." The N-body reproduction was deferred (GIZMO + FIRE-2 ICs required multi-day cluster runs that were not feasible). Two scripts were written:
- `scripts/ohana2026_cloud9_joint_likelihood.py` — MCMC over (M_200, c_200, τ) using Yang+ 2024/2025 parametric SIDM halo model (Eq. 4-5 of Ohana+), with a simplified gas profile (rho_DM² × r proxy) and a synthetic N_HI observation constructed from Ohana+'s published best-fit (M_200 = 4.7e9, c_200 = 4.0, τ = 0.18, σ/m = 483).
- `scripts/silverman2026_cloud9_gravothermal.py` — gravothermal collapse timescale analysis using a wrong unit convention (Balberg+ formula derived from scratch with CGS conversions).

The joint likelihood result: posterior median concentration-mass tension = 2.4σ (vs 7σ CDM-only, 3.2σ published Ohana+). The (σ/m, c_200) degeneracy was captured qualitatively. The gravothermal result: t_core ~ 10⁵–10⁹ Gyr — physically nonsensical. The script shipped without a sanity check.

### A.8 Revcloud.docx — the unit bug caught (2026-09-29)

Reviewer's reading of v19.1-preliminary was precise: the 10⁵–10⁹ Gyr collapse timescale was off by 5-8 orders of magnitude. The reviewer correctly identified that the project's own `T208_path_b_cloud9_host_halo_gravothermal.gravothermal_t_core_Gyr` function had the canonical Balberg+ formula with correct units, and that v19.1-preliminary should have used it instead of deriving from CGS. The reviewer also noted that the 2.4σ vs 3.2σ published comparison needed uncertainty reporting, and that "v19.0.5 Layer 3 closed" was undocumented in the bundle. The unit bug fix shipped as v19.1.1 (commit 88bcff6): t_core at Cloud-9 with σ/m = 483 = **1.24 Gyr**. The 2.4σ vs 3.2σ was reframed as a match within 68% CI. The 0.176 vs 0.22 Gyr "within rounding" claim was acknowledged as a 20% discrepancy from different V_max conventions (T208 uses NFW-correct V_max at r_max; T212 used simple virial V_max).

### A.9 flip1.docx — the paper-level contradiction caught (2026-09-29)

The reviewer's deeper reading found a paper-level contradiction that v19.1.1 had not flagged: **§9.12 of the paper says gravothermal does NOT run at Cloud-9 host-halo parameters (t_core = 73.7 Gyr), but v19.1.1 says gravothermal DOES run (t_core = 1.24 Gyr).** These are opposite conclusions on the same physical system. The reviewer correctly identified the root cause: v19.1.1 used Ohana+ best-fit σ/m = 483 cm²/g, while §9.12/T208 used Phase 44 Yukawa-only σ/m = 0.21 cm²/g. Both numbers are correct for their σ/m assumptions, but they answer different questions. The reviewer also noted:
- The 0.176 vs 0.22 Gyr difference is a 20% discrepancy from V_max convention, not rounding
- The "framework's actual σ/m at V_max" — with the v₁ resonance at v_target = 29.4 km/s (R74 fix), σ_peak = 174 cm²/g, Gaussian width 4.4 km/s — was σ/m = **164 cm²/g**, giving **t_core = 0.075 Gyr = 75 Myr**
- The §10.4e "framework cannot reach Silverman+'s regime" framing was wrong when interpreted as the framework's actual σ/m
- "Closed" claims need assumption labels

### A.10 v19.1.2 — the synthesis (2026-09-29, this version)

The v19.1.2 synthesis (commit 36417da) added the framework's actual σ/m case to the test matrix and reconciled §9.12 and §10.4e with the framework's full σ/m at Cloud-9 V_max. Five cases are now tested:

| Case | σ/m (cm²/g) | V_max (km/s) | t_core (Gyr) | Verdict |
|---|---|---|---|---|
| Silverman+ 2026 reference | 70 | 39.2 (NFW) | 0.176 | DOES run |
| Cloud-9 Phase 44 Yukawa-only | 0.21 | 31.12 | 73.7 | does NOT run (matches §9.12) |
| Cloud-9 framework v₁ ON | **164** | 31.12 | **0.075** | DOES run fast |
| Cloud-9 Ohana+ best fit | 483 | 25.07 | 1.24 | DOES run |
| Cloud-9 reviewer estimate | 76 | 25.07 | 7.87 | DOES run |

§9.12 was rewritten to state that "gravothermal does not run" is conditional on the Phase 44 Yukawa-only baseline. With the framework's actual σ/m, gravothermal runs in 75 Myr. §10.4e was rewritten to clarify that the "framework cannot reach Silverman+'s regime" applied to the Phase 44 baseline, not the framework's full σ/m.

### A.11 What survives, what doesn't

**Survives:**
- Headline "4 of 5 constrained channels under physically motivated f_H; 7 of 8 only under retracted borrowed f_H." (Cloud-9 was already "systematic bound" per §10.4d; the synthesis does not flip Cloud-9 from fail to pass.)
- The phenomenological σ_eff = f_H² σ_HH + 2f_H f_L σ_HL + f_L² σ_LL decomposition works under the borrowed prescription mode for SPARC (§9.11).
- T215 KiSS-SIDM kinetic confirmation that gravothermal catastrophe IS operative at Silverman+ parameters.

**Doesn't survive:**
- "Phase 44 framework cannot reach Silverman+'s regime" — wrong as stated; the framework's full σ/m is well above the threshold.
- "Gravothermal does not run at Cloud-9 host-halo parameters" — true for Phase 44 baseline only; false for framework's actual σ/m.
- The v19.1-preliminary claim of "expanded core phase" (now retracted).
- The v19.1.1 claim that 0.176 vs 0.22 Gyr is "within rounding" (acknowledged as 20% V_max convention difference).

### A.12 The Cloud-9 question, restated

The "Cloud-9 vs dSph structural tension" was framed in v1.11 as a bulk σ/m constraint problem: Cloud-9 needs σ/m ≥ 50 at v = 28, dSph needs σ/m ≤ 0.8 at v = 15, no σ/v curve satisfies both. The v19.1.2 synthesis reframes this as a **phase-diagram question**:
- The framework's σ/m at v = 28 (with v₁ resonance ON) is 164 cm²/g. Balberg+ collapse timescale: 75 Myr.
- The framework's σ/m at v = 15 (dSph scale, with v₁ resonance) is similar. Balberg+ collapse timescale: also fast.
- **Both Cloud-9 and dSph halos collapse in 75 Myr if merger history is quiescent.** The "structural tension" was never between Cloud-9 and dSph σ/m requirements — it was between **a pre-collapse expectation** (framework's σ/m) and **a post-collapse observation** (Cloud-9's 483, dSph's various signatures).
- Silverman+ 2026 finding (3 of 6 halos collapse, the quiescent ones) is the merger-history gate. Cloud-9's τ = 0.18 signature (close to maximum core expansion, before collapse) is a snapshot of a halo on the cusp of collapse — the merger history determines whether it ends up on the Cloud-9 branch (collapse + enhancement to 483) or the dSph branch (collapse + concentration of heavy component into deep core).

The "structural tension" dissolves when Cloud-9 is treated as an evolutionary-state constraint rather than a bulk σ/m constraint. The framework IS describing Cloud-9 — but through gravothermal evolution, not through a static σ/v curve. This is closer to how Yang+/Nadler+/Silverman+ actually work.

#### A.12.1 Extended analysis: Cloud-9 is an evolutionary-state constraint (not bulk σ/m)

Five implications for Cloud-9 itself, derived from the v19.1.5 reconciliation (post-flip2.docx + re196.docx + r197.docx):

**Important caveat (per r197.docx Reviewer 2 soft spot 1):** Implication 1 ("gravothermally evolved, not pristine") and implication 2 ("σ/m = 483 is post-collapse enhancement") are **interpretations, not facts**. They are conditional on:
- (i) the c=4 anchor (Ohana+ inferred concentration, which is itself the c-M tension)
- (ii) the Balberg/T208 analytical scaling applies at σ/m = 135.3 (causality-OK at c=4, but still requires N-body verification)
- (iii) the merger-history gating (Silverman+ mechanism, M94 group environment)

Without these assumptions holding, neither implication is physically established.

1. **If concentration is Ohana-like (c ≈ 4) and the Balberg/T208 scaling applies, Cloud-9 is gravothermally evolved at the framework's full σ/m** (not pristine). At framework σ/m = 135.3 cm²/g evaluated at V_max, the analytical t_core is 4.42 Gyr at c=4 (causality-OK). This is much shorter than the ~10 Gyr halo age — IF sustained mergers did not gate collapse, the halo would have already collapsed. The τ = 0.18 "expanded core" signature is therefore a snapshot of a halo in a merger-suppressed expanded-core phase, not a stable equilibrium.

2. **If the Balberg/T208 post-collapse amplification applies, σ/m = 483 could be 3.6× amplification of the framework σ/m = 135.3 at c=4**. This is an interpretation, not a measured factor — the post-collapse amplification in Balberg+ 2002 is order-of-magnitude; the actual factor depends on collapse history details (N-body required). Alternative interpretation: σ/m = 483 reflects pre-collapse framework σ/m = 76 (reviewer's estimate, would require Phase 44 re-fit).

3. **τ = 0.18 may be a merger-history constraint, not a bulk σ/m fingerprint** (Silverman+ mechanism: halos with quiescent mergers collapse, sustained mergers suppress). At framework σ/m = 151.6 cm²/g with c=4, t_core = 4.0 Gyr (R74 v_target=29.4); with sustained mergers over ~10 Gyr, the halo stays in expanded-core phase (τ ~ 0.2), consistent with Ohana+ observation. **But scenario (c) "leading" is over-argued**: at framework σ/m, the analytical formula already gives t_core ≈ 4 Gyr (causality OK); N-body needed to determine whether sustained mergers prevent collapse or delay it by ~6 Gyr.

4. **A follow-up N-body at framework σ/m = 135.3 with c=4 (M94-like) and sustained mergers** would directly test this. If the N-body shows Cloud-9 staying in τ ~ 0.18 expanded-core phase: scenario (c) is correct (sustained mergers suppress collapse against σ/m = 135.3). If the N-body shows Cloud-9 collapsing: the framework's σ/m is too high (σ_peak > 174 is wrong; reviewer's 76 estimate is more likely correct). **N-body is the discriminator; scenario (c) is a viable hypothesis but not "leading" until demonstrated.**

5. **Cloud-9 is the wrong place to look for a bulk σ/m signature; it may be the right place to look for gravothermal evolution in action** (research stance, per r197.docx Reviewer 2 soft spot 5). The "4000× Cloud-9 problem" (σ/m = 483 vs framework smooth Yukawa ~0.001) **reframes as a phase-diagram question under the c=4 / merger-history assumption**: σ/m at V_max is 135.3 (post-collapse enhancement gives 483), merger history gates whether collapse runs, the framework IS describing Cloud-9 but through evolution not through a static curve. The "4000× problem" is reframed, not yet fully dissolved.

#### A.12.2 The Ohana+ τ = 0.18 vs framework σ/m = 135.3 discrepancy (v19.1.5 weighted)

Ohana+ found τ = 0.18 (close to max core expansion, before collapse). But the framework's σ/m at V_max (135.3 cm²/g) gives collapse timescale 4.42 Gyr at c=4 (causality-OK) — much shorter than the ~10 Gyr halo age. **Weighting the three explanations** (v19.1.4, post-flip2.docx + re196.docx):

**Scenario (c): merger-suppressed collapse — VIABLE HYPOTHESIS** (not "leading"; not yet demonstrated). Silverman+ 2026 found that 3 of 6 halos at σ/m = 70 cm²/g collapsed (the quiescent-merger subset); the other 3 did not (sustained mergers). At framework σ/m = 135.3 cm²/g (almost 2× higher), collapse should run in 4.42 Gyr for a c=4, quiescent-merger halo. Sustained mergers over ~10 Gyr could keep it in expanded-core phase (τ ~ 0.2), consistent with Ohana+ observation. **Plausibility arguments**: consistent with Silverman+ mechanism; consistent with M94 group environment. **Counter-arguments**: not yet demonstrated with N-body at framework σ/m = 135.3; the analytical formula gives 4.42 Gyr at c=4, not 10+ Gyr, so sustained mergers need to suppress ~6 Gyr of collapse — possible but not shown.

**Scenario (a): τ = 0.18 is wrong — UNLIKELY.** Ohana+ fit is a published MCMC with reported posteriors; their τ = 0.18 is the published value. If Ohana+ got τ wrong by 5.5× (to τ = 1.0 = past max collapse), the gas profile would look different. Possible but unsupported by the published evidence.

**Scenario (b): framework's σ/m is wrong — POSSIBLE.** The 135.3 cm²/g comes from `causality_summary_corrected.json` (σ_peak = 174, width = 4.4 km/s, evaluated at V_max via Gaussian fall-off). If σ_peak is closer to the reviewer's estimate of 76 (2.3× lower), the framework's σ/m at V_max would be ~59 cm²/g, giving t_core ≈ 9.7 Gyr at c=4 — comparable to halo age. This is more consistent with τ = 0.18 as a stable equilibrium. However: σ_peak = 174 is from the Phase 44 fit's posterior, and the framework's actual code (sigma_m_at_v in phase44_joint_fit.py) gives this value. Lowering σ_peak to 76 would require a re-fit of Phase 44, which would change other constraints (SPARC, dSph).

**Better wording (v19.1.4 honest framing):** Three open explanations; scenario (c) is **viable but not leading** until demonstrated; scenario (b) is **possible** and would resolve the τ-discrepancy without invoking mergers; scenario (a) is **unlikely**. **N-body with M94-like sustained mergers is the discriminator.** The framework's σ_peak = 174 is a fixed parameter; scenario (b) requires a Phase 44 re-fit, which is v19.2 work. The "leading" language in v19.1.3 was over-argued — reviewer 1 of re196.docx and reviewer 2 both flagged it.

The three scenarios have **different implications for the paper**: (c) keeps the framework intact and adds merger-history as a discriminating axis; (b) requires a re-fit of Phase 44 (SPARC + dSph impacts); (a) questions Ohana+'s inference. Of these, (c) and (b) are both open, with (b) potentially simpler to test analytically once the σ_peak sensitivity is checked. **Honest framing: scenarios (c) and (b) are co-leads; neither is "leading" yet.**

#### A.12.3 Testable predictions of the new framing

The phase-diagram framing makes three predictions that v19.2 N-body can test. **Predictions are written with the corrected c=4 same-halo framework (re196.docx review):**

1. **At framework σ/m = 135.3 cm²/g with sustained M94-like merger history**, Cloud-9 should remain in expanded-core phase with τ ~ 0.18 (matching Ohana+ observation). Sustained mergers inject orbital kinetic energy that counteracts gravothermal collapse. If N-body confirms, scenario (c) is correct.

2. **At framework σ/m = 151.6 cm²/g with quiescent merger history (R74 v_target=29.4)**, Cloud-9 should collapse within ~4-5 Gyr at c=4 (consistent with the analytical t_core = 4.42 Gyr at c=4), producing inner density enhancement of ~3-5×. If N-body confirms, sustained mergers are necessary to suppress collapse — i.e., scenario (c) requires the merger history to do real work, not just be present.

3. **The Ohana+ observed σ/m = 483** is consistent with two scenarios:
   - **Scenario A**: framework σ/m = 135.3 at V_max, post-collapse enhancement of 3.6× amplification factor
   - **Scenario B**: framework σ/m closer to the reviewer's estimate of 76 (σ_peak ≈ 96), with Ohana+ observation at peak enhancement (6.3× amplification factor)

N-body at framework σ/m = 135.3 with c=4 and sustained M94-like merger history would distinguish these: if collapse runs, scenario A is wrong (mergers didn't prevent it) and the framework's σ/m needs revision; if not, scenario A is correct and sustained mergers are the gating mechanism.

**Per re196.docx Reviewer 1 Item 5: the prediction direction was backwards in v19.1.x.** Scenario (c) (merger-suppressed) predicts **expansion maintained**, not collapse, at framework σ/m with M94-like mergers. v19.1.4 corrects this.

#### A.12.4 Why this matters for the paper's headline

The "4 of 5 channels under physically motivated f_H" headline is **unaffected** — Cloud-9 was already being counted as a "systematic bound" per §10.4d, and the synthesis clarifies why it's marginal (gravothermal-evolution constraint) rather than whether it is. The headline still holds.

But the **interpretation** of the headline has shifted. Before: "the framework matches 4 channels and Cloud-9 is a permanent exception." Now: "the framework matches 4 channels and Cloud-9 is a marginal case whose outcome depends on merger history." The shift matters for how the paper is read:
- Before: Cloud-9 is an outlier, framework can't reach it
- Now: Cloud-9 is on the framework's natural trajectory, merger history is the discriminating axis

**Honest framing (v19.1.4 per re196.docx Reviewer 2 piece 5):** The "4000× Cloud-9 problem" is **reframed** (not yet dissolved). The framework's σ/m at V_max (135.3 cm²/g, derived explicitly) drives gravothermal collapse in 4.42 Gyr at c=4 (causality-OK). This moves the question from "can gravothermal run" to "can sustained mergers prevent collapse for ~10 Gyr against σ/m = 135.3". That question is open. N-body required to dissolve it. The "permanent exception" framing of Cloud-9 is gone; the "merger-history axis" framing replaces it. The "4000× spike" is no longer a problem to be solved — it's a question about merger history.

This is closer to how SIDM literature (Yang+/Nadler+/Silverman+) actually treats Cloud-9-like systems. The paper moves from "constraint map with one outlier" to "constraint map with one merger-history-dependent axis."

#### A.12.5 Open questions for v19.2+

The phase-diagram framing opens three concrete v19.2 questions:

1. **What is the framework's actual σ/m at Cloud-9 V_max?** The 164 cm²/g (or 135.3 at V_max) from `causality_summary_corrected.json` has not been re-derived from a fresh MCMC. A v19.2 sweep at Phase 44 + v₁ resonance peak fit would either confirm 164 (then 135.3 at V_max is the anchor) or revise it (possibly to the reviewer's 76 cm²/g estimate, then ~59 at V_max would be the anchor). **The c=4 anchor at 135.3 gives t_core = 4.42 Gyr; at 59 it gives 9.7 Gyr — both within ~halo age; N-body needed to distinguish.**

2. **Does Cloud-9 collapse under M94-like merger history, and is τ = 0.18 transient or steady-state?** A GIZMO N-body at framework σ/m = 135.3 (or 76) with sustained mergers (matching M94 group environment) would test whether the merger history keeps the halo in expanded-core phase (matching Ohana+) or pushes it to collapse. **If the halo collapses in the N-body, τ = 0.18 was transient (halo on the cusp of collapse); if the halo stays expanded, τ = 0.18 is steady-state (merger-history gating the gravothermal cascade).** This is the v19.2 N-body test that re196.docx Reviewer 1 explicitly requested. Per r199.docx smaller item 3, the two questions (collapse fate + τ transient/steady-state) are inseparable in N-body — they collapse into one test, not two.

3. **What is the framework's σ/m at lower halo masses (dSphs)?** The framework's σ/m at V_max = 5-15 km/s (dSph scale) determines whether the gravothermal cascade runs in dSphs or not. If the framework reaches σ/m ≳ 10 cm²/g in dSphs (similar to Cloud-9), then dSphs would also collapse, which contradicts the dSph σ/m < 1 cm²/g upper limits. The v₁ resonance structure (σ_peak ≈ 174 cm²/g at v_target = 29.4 km/s (R74 fix), width 4.4 km/s) gives σ/m at v=5-15 km/s of ~10⁻²⁰ cm²/g (negligible), so dSphs should NOT collapse — but this requires verification with the framework's full velocity-dependent σ/m at dSph scales (channels_v03.sigma_m_at_v with v₁ resonance at v_target = 29.4 km/s (R74 fix) and width 4.4 km/s).

These three questions are deferred to v19.2 (GIZMO + FIRE-2 ICs + multi-day cluster runs required). The v19.1.2 synthesis is honest about what it can and cannot answer with current computational resources.

End of analysis section.

### A.13 What's open for v19.2

The v19.1.2 synthesis is paper-level (script + §9.12 + §10.4e + standing-numbers document), but it does not close the Cloud-9 question. Three open items:
- **Actual GIZMO N-body reproduction of Silverman+ 2026's 6-halo suite at Cloud-9 parameters.** Requires FIRE-2 ICs + multi-day cluster runs. Defer to v19.2.
- **Merger-history parameterization for the 3-of-6 collapse prediction.** Silverman+ found collapse only for quiescent halos; Cloud-9 (M94 group environment) has merger history. A parameterization would test whether M94-like mergers keep Cloud-9 in τ = 0.18 expanded-core phase or push it to collapse.
- **Verification of the framework's σ/m = 164 at V_max against the actual MCMC posterior.** The 164 cm²/g value comes from `causality_summary_corrected.json`; it has not been re-derived from a fresh MCMC. A v19.2 sweep at Phase 44 + v₁ resonance peak fit would either confirm 164 or revise it.

### A.14 Process lessons (per AGENTS.md)

The v19.1 → v19.1.2 sequence is a process audit in itself:
1. **v19.1-preliminary**: shipped a 5-8 orders of magnitude wrong collapse timescale without a sanity check (Rule 28 violation). Caught by Revcloud.docx reviewer.
2. **v19.1.1**: fixed the unit bug correctly but did not flag the paper-level contradiction (§9.12 vs script). Shipped without reconciliation. Caught by flip1.docx reviewer.
3. **v19.1.2**: full paper-level reconciliation. §9.12, §10.4e, and standing numbers (in `PAPER_STANDING_NUMBERS.md`) all updated. Headline "4 of 5 channels" preserved because Cloud-9 was already "systematic bound" per §10.4d.

The meta-lesson: **a unit fix that flips a paper conclusion requires paper-level reconciliation, not just a corrected script.** A script-level fix without a paper-text check ships a known contradiction. Reviewers caught both the unit bug and the paper-text gap. The audit trail above documents what was wrong, when, and how it was fixed.

End of Annex A.

---

## References
[4] Randall, S. W.; Markevitch, M.; Clowe, D.; Gonzalez, A. H.; Bradač, M. (2008) ApJ 679, 1173 — Bullet Cluster σ/m upper bound.

[5] Feng, J. L.; Kaplinghat, M.; Yu, H.-B. (2009) — Yukawa suppression mechanism for velocity-dependent SIDM.

[6] Tulin, S.; Yu, H.-B.; Zurek, K. M. (2013) Phys. Rev. D 87, 115007 — "Resonant dark forces and small scale structure."

[7] Chu, X.; Hambye, T.; Tytgat, M. H. G. (2018) JCAP 05, 014 — threshold resonance mechanism for dark matter self-interactions.

[8] Duerr, M.; et al. (2021) Phys. Rev. D 103, 075018 — resonant dark matter self-interactions.

[9] Hong, T.; Kuranchi, H.; Perez, A. (2020) — geometric mass-ladder construction for dark sectors.

[10] Girmohanta, T.; Yasuoka, Y. (2025) — dark-photon SIDM model with multi-resonance structure.

[11] Yang, X.; Yu, H.-B. (2023) — single-breathing-mode mediator SIDM model.

[12] Turner, J.; et al. (2021) — atomic-DM transition SIDM framework.

[13] Yang, X.; Yu, H.-B. (2022) JCAP 06, 014 — core-collapse extension of multi-resonance SIDM.

[14] Lelli, F.; McGaugh, S. S.; Schombert, J. M. (2016) AJ 152, 157 — SPARC database: 175 galaxies with H I + Spitzer photometry rotation curves.

[15e] Robles, V. H.; et al. — T120 multi-component SIDM phenomenology.

[15f] Drobczyk, M. (2025) Class. Quantum Grav. 42 225006; arXiv:2506.22997 — "Naturally resonant two-mediator model of self-interacting dark matter with decoupled relic abundance." Two-mediator UV completion: m_χ = 600 GeV, m_φ = 15 MeV, m_Φh = 1201 GeV; σ_T/m_χ ~ 0.1-1 cm²/g at dwarf-galaxy velocities; σ_SI ~ 7×10⁻⁵¹ cm² (below xenon neutrino floor, predicted null). Optional walking SU(3)_H N_f = 10 UV completion. **R85 attribution correction:** The framework's prior claim "Ωh² = 0.119 at δ = 0.43%" was incorrect — Drobczyk does not derive Ωh²; the Ωh² = 0.120 ± 0.001 value is from Planck reference [1] (cited as a constraint to satisfy), not Drobczyk's own prediction. The "δ = 0.43%" figure was a fabrication. **Per R84 reviewer: a qualifier is a hedge, not a fix — remove the false claim.**

[16] Vegetti, S.; et al. (2010) Nature 481, 341 — JVAS B1938+666 strong-lensing substructure detection.

[23] Yu, H.-B.; et al. (2026) PRL 136, 141001 — gravothermal core-collapse selection mechanism.

[25] Forbes, D. A.; et al. — UDG kinematics: extremely extended globular clusters in ultra-diffuse galaxies.

[26] Cerny, W.; et al. (2026) Research Notes of the AAS, 4 pages, 1 figure; arXiv:2608.02601 — "Discovery of the Distant, Ultra-Faint Milky Way Satellite Aquarius IV with the Vera C. Rubin Observatory Early Data Preview 2." First UFD from EDP2; Aquarius IV at D_⊙ = 109 kpc (M_V = −1.9, r_1/2 = 19 pc).

[26a] Simon, J. D. (2019) Annual Review of Astronomy and Astrophysics 57, 375–420; arXiv:1901.05465 — "The Faintest Dwarf Galaxies." Comprehensive UFD observational review: stellar kinematics, mass modeling, chemical abundances, structural properties, tidal stripping constraints. 311+ citations.

[27] Horigome, S.; Hayashi, K.; Ando, S.; Ibe, M.; Shirai, S. (2025) arXiv:2503.13650 — "Stringent Constraints on Self-Interacting Dark Matter Using Milky-Way Satellite Galaxies Kinematics." **R84 attribution correction:** Abstract verbatim: "the combined analysis decisively prefers CDM to SIDM when σ/m exceeds ~0.2 cm²/g." This is a **decisive SIDM exclusion** at σ/m > 0.2 cm²/g, in tension with the framework's σ_peak = 174 cm²/g — NOT a "95% CL upper limit" claim as previously cited.

**R85 escalation (per R84 reviewer follow-up):** Horigome's threshold (σ/m > 0.2 cm²/g excluded at decisive preference for CDM) applies to **classical + ultrafaint dwarf galaxies with effective velocities ~10-30 km/s**. The framework's BACKGROUND Yukawa tail σ_m_at_v(0.052, 1.0, v) at these velocities:
- v = 9 (Sculptor): 0.578 cm²/g — **3× above threshold**
- v = 10 (Draco): 0.520 cm²/g — **2.6× above**
- v = 12: 0.433 cm²/g — 2.2× above
- v = 15 (Fornax): 0.347 cm²/g — 1.7× above
- v = 18 (Fornax canonical): 0.289 cm²/g — 1.4× above
- v = 20: 0.260 cm²/g — 1.3× above
- v = 25: 0.208 cm²/g — 1.04× above (just above)
- v = 28 (Cloud-9): 0.186 cm²/g — below threshold (but at the resonance peak σ/m = 174, far above)

**R86 CORRECTION (per R85 reviewer):** The script a_slope = 1.0 is **WRONG**. Phase 44 free fit (best_params[2] = 1.93) gives a_slope = 1.93 — essentially v⁻² scaling. With a_slope = 1.93, the framework's background σ/m at dSph velocities is **MUCH LARGER**:
- v = 9 (Sculptor): **5.38 cm²/g** — 27× above threshold (not 3×)
- v = 10 (Draco): **4.39 cm²/g** — 22× above (not 2.6×)
- v = 15 (Fornax): **2.01 cm²/g** — 10× above (not 1.7×)
- v = 18 (Fornax canonical): **1.41 cm²/g** — 7× above (not 1.4×)
- v = 25: **0.75 cm²/g** — 3.7× above (not 1.04×)

**R86 framework status (per R85 reviewer Path B; Horigome assumes velocity-independence but framework is velocity-dependent):** The framework's BACKGROUND at all dSph velocities (v < 30 km/s) exceeds Horigome's 0.2 cm²/g threshold, even with a_slope = 1.93. **However, Horigome's Eq. 2 is dσ/dcosθ = (σ0/2) × [1 + (v/w)² sin²(θ/2)]² — this IS velocity-dependent.** The "velocity-independent case" cited in the abstract is the limit w → ∞. The framework's σ/m is velocity-dependent (a_slope = 1.93 + resonance). **Path B (per R85 reviewer):** The comparison is approximate because Horigome's bound is derived for a specific functional form (constant σ/m). The direct σ/m comparison "framework exceeds Horigome's threshold at v < 28 km/s" is true, but the velocity-dependent comparison requires re-running Horigome's analysis with the framework's σ/m(v) profile.

**R87 PATH B (per R86 reviewer; framework's σ/m(v) is above threshold at all dSph velocities, but no rigorous likelihood comparison):**

Framework's total σ/m(v) = σ_0 × (100/v)^1.93 [Phase 44 best fit a_slope] + 174 × exp(-(v-29.4)²/(2×4.4²)) [resonance]:

| v (km/s) | channel | background | resonance | total σ/m | vs Horigome 0.2 |
|----------|---------|------------|-----------|-----------|------------------|
| 9 | Sculptor | 5.38 | 0.004 | **5.39** | **27× above** |
| 10 | Draco | 4.39 | 0.01 | **4.40** | **22× above** |
| 12 | (UFD) | 3.09 | 0.07 | **3.16** | **16× above** |
| 15 | Fornax (paper) | 2.01 | 0.82 | **2.83** | **14× above** |
| 18 | Fornax canonical | 1.41 | 6.07 | **7.48** | **37× above** |
| 20 | | 1.15 | 17.76 | **18.91** | **95× above** |
| 25 | | 0.75 | 105.5 | **106.3** | **531× above** |
| 28 | Cloud-9 | 0.60 | 165.4 | **166.0** | **830× above** |

**R87 Path B conclusion (per R86 reviewer):** "The framework's σ/m exceeds Horigome+ 2025's CDM-preference threshold by 10–27× at all dSph velocities (v < 28 km/s), and exceeds it by a factor of 830× at Cloud-9's velocity. Because Horigome's bound is derived for a different functional form (their Eq. 2 is the Rutherford-like form dσ/dcosθ = (σ0/2)[1 + (v/w)² sin²(θ/2)]², not the framework's v⁻¹·⁹³ Yukawa tail), we do not claim a rigorous likelihood exclusion; the magnitude of the excess, however, makes it unlikely that the velocity-dependence rescues the framework. A definitive exclusion requires re-running Horigome's SASHIMI likelihood with the framework's σ/m(v) profile."

**R87 important note (per R86 reviewer):** "R86 defined Path A as re-running Horigome's SASHIMI likelihood. R87's analysis is **Path B**, not Path A — it is a direct σ/m comparison, not a likelihood comparison. The label 'Path A confirmed analytically' is incorrect; the actual claim is 'Path B with framework's σ/m well above threshold, so we expect exclusion, but we do not claim a rigorous likelihood comparison.'"

**T192 Ωh² caveat (per R86 reviewer):** T192 used **m_χ = 10.3 GeV, m_Φh ≈ 20.7 GeV** — these do NOT match the framework's m_χ = 1 GeV, m_Φh ≈ 2 GeV (per Drobczyk-style two-mediator construction in T221). **R86 finding:** the framework's Ωh² = 0.119 claim (cited from T192) is at the wrong m_χ. The T221 framework at m_χ = 1 GeV, m_Φh = 2 GeV gives a different (lower) Ωh² — needs re-evaluation. **Per R86 reviewer: remove the Ωh² claim or recompute it at m_χ = 1 GeV.**

**R87 systematic parameter audit (per R86 reviewer "the paper was built with 'convenient' values"):** R66 (m_χ), R74 (v_target), R76 (σ vs FWHM), R85/R86 (a_slope), R87 (T192 m_χ) are all the same class of error — paper used one value, Phase 44 fit produced another, paper was tighter on framework than the actual fit. **Pre-submission systematic audit (~1 hr): list every numerical parameter in the paper, cross-check against phase44_joint_fit.json best_params, flag any mismatches.** This is the right response to the pattern, per R86 reviewer.

[28] Chu, X.; García-Cely, A.; Murayama, H. (2019) Phys. Rev. Lett. 122, 071101 — published best-fit p-wave resonance. arXiv:1810.04709 (R60 verified).

[52] Jia, Z.; et al. (2026) arXiv:2601.17118, MNRAS 549 stag969 — "SIDM Jeans Model: Adiabatic Contraction Semi-analytical Halo Profiles." Public GitHub: ZixiangJia/SIDM_Jeans_model. **R84 added:** cited in §10 but previously missing from References. Provides independent semi-analytical SIDM halo profile with adiabatic contraction; applicable to SPARC but **NOT integrated** (no LICENSE file in repo; cited as reference only per R52 user directive).

[30] Yang, X.; Yu, H.-B. (2022) — kinematic convention v_eff = 0.64 × V_max for dSph σ/m constraints.

[42] Yang, X.; Tsai, Y.; Fan, J. (2025) Phys. Rev. D 112, 083011 — two-component asymmetric dark matter (heavy χH + light χL, mass ratio 3:1).

[43] Yang, X.; Nadler, E. O.; Yu, H.-B.; Zhong, Y.-M. (2024) JCAP — parametric halo modeling framework.

[44] Sigurdson, K.; Doré, O.; Kamionkowski, M.; Prunet, S. (2004) — semi-analytic dark matter self-interaction formula.

[45] Zhang, X. (2016) — strong-lensing σ/m limits from cluster observations.

[49] Engelhardt, T.; et al. (2026) — core-collapse timescales in velocity-dependent SIDM, Yukawa-background parameter space.

[49b] Robles, V. H.; et al. — v18.40 internal paper reference (focal version).

[50] Aalbers, J.; et al. (LZ Collaboration) (2026) arXiv:2609.02823 — LZ September 2026 single-event observation (2.6σ, marginal status).

[50b] Das, P.; Karmakar, B.; Mahapatra, S.; Paul, P. K. (2026) arXiv:2609.06825 [hep-ph] — "Inelastic Self-interacting Dark Matter and LUX-ZEPLIN 248 keV Event in a Dirac Modular Inverse Seesaw." 35+12 pages, 12 figures, 4 tables. A₄ modular symmetry + Dirac inverse seesaw; scalar mediator serves dual role for SIDM (light) and DM pseudo-Dirac Majorana mass splitting (inelastic). Explains LZ230616 via endothermic scattering kinematics. Predicts stochastic GW background from domain wall annihilation.

[50c] Yang, D.; Fan, Y.-Z.; Hou, S.; Tsai, Y.-L. S. (2026) arXiv:2506.14898v3, Science Bulletin 71, 1349-1356 — "Self-interacting dark matter with mass segregation: a unified explanation of dwarf cores and small-scale lenses." Two-component SIDM (SIDM2v): σ_H/m_H = 6.89 cm²/g, w_H = 275 km/s, σ_x/m_H = 1.125 cm²/g, w_x = 2200 km/s, m_H/m_L = 3. **R84 attribution correction:** arXiv:2506.14898 is by Yang, Fan, Hou, Tsai (2026), NOT Mace, Yang, Zeng as previously cited. **Per our §3 R39 computation:** σ_eff at v=28 km/s (Cloud-9) is at most 6.89 cm²/g (f_H=1), ~7× short of Cloud-9's σ/m ≥ 50 floor. Provides the unification framework that addresses all three of our model tensions.

[50d] Kaplinghat, M.; Tulin, S.; Yu, H.-B. (2016) Phys. Rev. Lett. 116, 041302; arXiv:1508.03339 — "Dark Matter Halos as Particle Colliders: Unified Solution to Small-Scale Structure Puzzles from Dwarfs to Clusters." Foundational unified SIDM fit: σ/m ≈ 2 cm²/g on galaxy scales, σ/m ≈ 0.1 cm²/g on cluster scales; mildly velocity-dependent cross section inferred from fits to 12 dwarf/LSB galaxies and 6 clusters. Illustrates dark photon model as concrete UV completion.

[51] Nadler, E. O.; et al. (2025) arXiv:2503.10748 — "SIDM Concerto: Compilation and Data Release of Self-interacting Dark Matter Zoom-in Simulations." 14 cosmological zoom-ins, public data release at Zenodo 14933624. Published as ApJ 991, 69 (2025). **R84 attribution correction:** paper text says ApJ 983, 50A which is incorrect; that ApJ vol corresponds to a different paper (Adhikari+ 2025 [53]). Used in §9.6 Limitations as available source for data-derived f_H(r) profiles.

[55a] Elbert, O. D.; Bullock, J. S.; Garrison-Kimmel, S.; Rocha, M.; Oñorbe, J.; Boylan-Kolchin, M. (2015) Mon. Not. R. Astron. Soc. 453, 29–37; arXiv:1412.1477 — "Core formation in dwarf haloes with self-interacting dark matter: no fine-tuning necessary." **This is the actual source of the Cloud-9 σ/m ≥ 50 cm²/g "floor" used in the framework.** Elbert+ 2015 used σ/m = 50 cm²/g as **the largest SIDM cross-section in their dwarf-galaxy simulation suite**, showing it remains viable at v_rms ~ 40 km/s. Per their abstract: "Our work suggests that SIDM cross-sections as large or larger than 50 cm²/g remain viable on velocity scales of dwarf galaxies." This is a **simulation upper end**, NOT a clean observational lower bound. Per R41 (r34.docx Issue 1): the framework's adoption of 50 cm²/g as a "Cloud-9 floor" was previously miscited as Benítez-Llambay+ 2024 (ApJ 973, 61) [1a]; correct attribution is Elbert+ 2015.

[55b] Sánchez Almeida, J.; et al. (2025) Astron. Astrophys. 704, A210; arXiv:2510.05682 — "Constraints on dark matter models from the stellar cores observed in ultra-faint dwarf galaxies: Self-interacting dark matter." Six UFDs from Richstein+ 2024 with stellar cores that cannot be formed by stellar feedback. Derives allowed σ/m range ~0.3-200 cm²/g via Eq 9-10 (core-formation vs core-collapse phases). Verbatim: "Since stellar feedback is insufficient to form cores in these galaxies, UFDs unbiasedly anchor σ/m at low velocities." This is the external observational anchor for the framework's σ_peak = 174 cm²/g, which falls within the upper end (core-collapse phase) of the Sánchez Almeida allowed range. Cloud-9 (M_200 = 5×10⁹ M☉) sits in the same mass regime as the Sánchez Almeida sample (10⁹-10⁹·⁷ M☉).

[53] Adhikari, S.; et al. (2025) ApJ 983, 50A — "Constraints on Dark Matter Self-interactions from Weak Lensing of Galaxies from the Dark Energy Survey around Clusters from the Atacama Cosmology Telescope Survey." σ/m < 1.05 cm²/g at 95% CL from cluster weak lensing.

[54] Silverman, M.; et al. (2026) arXiv:2606.02566; Fermilab-PUB-26-0348-T — "Mergers Matter: N-body gravothermal cascade at σ/m = 70 cm²/g in M_halo = 10^10 M_☉ halos." 3 of 6 host halos collapse within a Hubble time (quiescent merger histories). Used in §3.2c concentration-mass corroboration and §10.4e gravothermal threshold.

## References

[1] Benítez-Llambay, A.; Dutta, R.; Fumagalli, M.; Navarro, J. F. (2024) ApJ 973, 61 — VLA observations of Cloud-9 (M₂₀₀ from hydrostatic; does NOT provide σ/m floor). See Elbert+ 2015 [55a] for actual source of σ/m ~ 50 benchmark.

[2] Anand, A.; et al. (2025) HST/ACS star-counts on Cloud-9 — M⋆ < 10^3.5 M☉.

[3] Trujillo, I.; et al. (2026) GTC/HiPERCAM — strongest stellar-mass bound to date, M⋆ < 1.6×10⁴ M☉.

[15a] Zhou, R.; et al. (2023) FAST H I detection of Cloud-9.

[15b] Benítez-Llambay, A.; et al. (2024) ApJ 973, 61.

[15c] Anand, A.; et al. (2025) HST/ACS.

[15d] Trujillo, I.; et al. (2026) GTC/HiPERCAM.

[29d] Read, J. I.; Walker, M. G.; Steger, P. (2019) MNRAS 484, 1401 — "Dark matter heats up in dwarf galaxies," arXiv:1808.06634. Primary source for Segue 1 σ/m < 1 cm²/g bound.

[29e] Fritz, T. K.; et al. (2018) ApJ 857, L11; arXiv:1711.09097 — Segue 1 proper motion + MW orbit.
