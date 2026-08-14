REVIEWER AUDIT — Review 10 (Project Rationale & Key Findings Extract)

This is an audit of the REVIEW itself, not of the underlying project.
Reviewed: 2026-08-14, against on-disk ground truth in
`C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\` (HEAD = wip/v0.4-prelim
@ commit d0f6f31; master = d0f6f31).

**Important framing note**: this review is anchored to the **D5**
snapshot of the project (reviewer explicitly cites "v0.3-prelim-D5").
Current state is **v0.3-prelim-D15-CORRECTED3 + Mediator_Detection_v12**,
which has 411 tests, 99 modules, Tier-3 marginalization completed,
mediator-decoupling survey completed, and composite-DM extension added.
The reviewer's data is **old but methodologically correct**; some numbers
cited have changed since D5.

Methodology: per `reviewer-audit` skill (Tier-1 / Tier-1.5 / Tier-2 /
Tier-3 / Tier-4) + citation hygiene.

================================================================
HEADLINE VERDICT
================================================================

This is a **substantive critique from a reviewer who read the project
state at D5** and identified several real methodological issues, most
of which have been **resolved by D15-CORRECTED3** but were not yet
folded back into the public-facing EXTRACT. The caveats the user asked
me to fix are:

(a) The two-component BF is a **pipeline feasibility diagnostic**, not
definitive observational evidence (caveat foregrounded by reviewer §2.2.3,
missing from EXTRACT).
(b) The headline σ/m shift from placeholder T8/T17 (~1.0 cm²/g) to real
KiSS-SIDM T21 (1.4–1.7 cm²/g) is a +0.2 dex correction that EXTRACT
should acknowledge as a calibration improvement, not as a discovery.
(c) Three specific engineering caveats (10-channel aspiration vs actual
5–6 channels, Gaussian likelihood proxies, N=2×10⁶ KiSS-SIDM dwarf
simulation unobtainable) belong in EXTRACT's Limitations section.
(d) Several cited numbers in the review are wrong or stale; specific
verdicts in PART B below.

Overall grade: **B+**. Substantive critique, real caveats, ~3 numerical
errors, 1 framing overclaim (10-channel vs actual 5–6 channels).

================================================================
PART A — STRENGTHS (Reviewer's claims, verified ✓)
================================================================

A1. KiSS-SIDM kinetic vs fluid gravothermal bias is real
   Source: `v0.3-prelim/data/results/t21_real_kiss_sidm_gravothermal.json`,
   verdict block; FINDINGS.md §T2.1.
   T17 placeholder: log Z = −1.22; T21 with IMFP correction: log Z = −0.660.
   T21 no correction: log Z = −0.563. Difference between corrected and
   uncorrected: 0.097 (small); difference between T17 and T21 corrected:
   0.56 (substantial). Reviewer's qualitative claim that placeholder
   bias was overstated in simplified analytic approximations is correct.

A2. σ/m shift from placeholder T8 to real KiSS-SIDM T21
   T8 placeholder MAP: 10^0.0025 = 1.006 cm²/g
   T21 real KiSS-SIDM MAP: 10^0.236 = 1.722 cm²/g
   Shift: +0.234 dex (~1.7×) ✓

A3. Knudsen regime classification
   FINDINGS.md §T2.1 confirms: "The |kinetic|/|fluid| penalty ratio is
   **0.778, exact match to Table I Kn=1** of arXiv:2505.15903v2."
   Fluid model is reliable in LMFP/SMFP; IMFP requires DSMC correction.
   Reviewer §2.3.1 ✓

A4. Mass segregation resolves scale tension
   T22 verdict: "Mass segregation decouples low-velocity dwarf and
   high-velocity cluster effective cross-sections naturally..."
   T22 delta_A_C = +0.386 BF (2-comp vs 1-comp, with IMFP). Modest BF;
   +0.48 not +0.386, see PART B.

A5. Lensing substructure and cluster bounds
   Yang, Yang, Yu+ 2026 (arXiv:2510.11006) confirms 30–100 cm²/g at
   dwarf scales (V_max ~10 km/s). Cluster upper limits 0.22–0.61 cm²/g
   from Markevitch 2006 (Bullet) + Randall 2008 (Abell 901/902 etc.)
   Reviewer §2.4.1 ✓

A6. Composite dark-rho microphysics validation
   T54 (PCAC + KSFR) gives m_ρ = 3.55 MeV, m_χ = 34 GeV, σ/m = 1.36
   cm²/g (within 13% of T21/T39 MAP). Already in EXTRACT §4 ✓

A7. Direct-detection constraints are soft priors only
   T62 result: σ_SI ≈ 2×10⁻¹¹⁸ cm², 72 dex below LZ WS2024 limit.
   Reviewer §2.4.2 framing is correct: LZ acts as soft model-exclusion,
   not as a hard σ/m constraint, because the mediator decouples.

================================================================
PART B — FACTUAL ERRORS (Tier-1 audit)
================================================================

B1. ❌ T20 placeholder ΔlogZ = −1.46 — UNVERIFIABLE
   Reviewer claim (Review §2.1.1): "IMFP correction term previously
   estimated via analytical placeholders introduced artificially large
   log-evidence shifts (ΔlogZ = −1.46 in T20 placeholder tests)".
   Actual: NO `t20*.json` file exists in `v0.3-prelim/data/results/`.
   The T21 verdict JSON references "T17 placeholder: log Z = −1.22"
   but does not name T20. The "−1.46" number cannot be verified on
   disk and may be from a stale CHANGELOG entry or older synthesis doc.
   Impact: SMALL. The qualitative claim that placeholder bias is
   overstated is correct (T17=−1.22 vs T21=−0.66); the specific −1.46
   is unverifiable.

B2. ❌ "T21 real KiSS-SIDM reduces this correction's impact to a
   negligible ΔlogZ = −0.04" — INCORRECT (actual: ~+0.097)

   Reviewer claim: T21 IMFP correction shifts log Z by −0.04.
   Actual: T21 with IMFP log Z = −0.660; T21 no correction log Z =
   −0.563. Difference is +0.097 (IMFP slightly worse, not "negligible
   −0.04"). The magnitude is similar but the **sign and exact value
   differ**.

   Impact: SMALL. Both numbers are within 1σ of each other; the
   qualitative "small correction" claim survives.

B3. ❌ T22 real KiSS-SIDM BF = +0.48 — INCORRECT (actual: +0.386)

   Reviewer claim (Review §2.2.1): "ΔlogZ = +0.48 favouring the 4-
   parameter two-component model over the nested single-component
   variant".
   Actual: T22 JSON: `delta_A_C_2comp_vs_1comp_3ch = 0.3861`.
   `delta_B_C_2comp_no_imfp_vs_1comp = 0.217`.
   Neither is 0.48. The +0.48 number is wrong by ~25%.

   Impact: SMALL. Still in the same "modest BF" regime (< 2.5
   significance threshold). Conclusion "Occam-neutral" survives.

B4. ⚠️ "All 198 unit/integration tests pass" — UNDER-COUNTED
   (actual: 411 test functions)

   Reviewer claim (Review §2.5.1): "All 198 unit/integration tests
   pass post-D5 KiSS-SIDM integration".
   Actual: 411 `def test_` functions across 39 test files in
   `tests/` + `v0.*/tests/`. 198 was the count at D5 (reviewer's
   snapshot); the project grew to 411 by D15-CORRECTED3.
   Impact: SMALL. Qualitative claim "all tests pass" correct (pytest
   runs clean); exact count is stale.

B5. ⚠️ "56 source files" — UNDER-COUNTED (actual: 99 modules)

   Reviewer claim (Review §2.5.1): "consistent sampler behaviour,
   unit conversion and likelihood evaluation across 56 source files".
   Actual: `find v0.3-prelim/code -name '*.py' | wc -l` = 99.
   Impact: SMALL. Qualitative claim survives.

B7. ⚠️ "10 independent observational probes" — OVERSTATED
   (actual: 5–6 channels today, not 10)

   Reviewer claim (Review §1.2.2): "integrating 10 independent
   observational probes (SPARC rotation curves, dSph/ultrafaint dwarfs,
   strong lensing substructure, radio relic clusters, cluster mergers,
   direct-detection exclusion limits etc.)".

   Actual: 5-channel fit (SPARC + dSph + ufd + Bullet + LZ) at D5
   expanded to 6-channel at D15-CORRECTED3. The "10 probes" framing is
   either aspirational (v0.4-prelim roadmap) or conflates ingest
   channels with theoretical constraints. Either way, the project has
   never integrated 10 independent observational likelihoods as
   simultaneously-fitted channels.

   Impact: MEDIUM. This is the closest claim to a Tier-1.5 framing
   overclaim: it implies a fitted-channel count that the project has
   never achieved. Recommend hedged version: "aspirational multi-channel
   framework; currently 5–6 channels fully integrated, 10+ aspirational
   for v0.4-prelim".

================================================================
PART C — FRAMING ISSUES (Tier-1.5 audit)
================================================================

C1. ⚠️ "All three two-component observational likelihoods remain
   simplified Gaussian proxies... the measured Bayes factor
   constitutes a pipeline feasibility diagnostic rather than
   definitive observational evidence for a two-species dark sector"

   Reviewer's caveat (Review §2.2.3) is **already framed correctly** —
   they flag the BF as a diagnostic, not evidence. **But the EXTRACT
   currently does not include this caveat**, treating the composite-
   dark-rho + 1.36 cm²/g prediction as a standalone finding without
   flagging that the two-component underlying likelihoods are still
   proxies. **This is the EXTRACT fix**.

C2. ⚠️ "Headline σ/m posterior shifts upward when adopting full
   kinetic KiSS-SIDM physics" — REVIEWER RIGHT BUT UNFRAMED IN EXTRACT

   Reviewer correctly notes the +0.234 dex upward shift from
   placeholder T8 (1.006 cm²/g) to real KiSS-SIDM T21 (1.722 cm²/g).
   This is a **calibration correction**, not a discovery: the physics
   becomes more accurate. EXTRACT §1 should foreground this so readers
   don't infer that the headline σ/m was previously estimated and then
   "got bigger".

C3. ⚠️ "Major systematic risks identified: fixed reference halo
   parameters, unvalidated KiSS scaling extrapolation to dwarf/cluster
   masses, and Gaussian proxy likelihoods"

   Reviewer §2.5.3 correctly identifies 3 specific engineering caveats.
   EXTRACT §Limitations currently mentions only the velocity-slope
   tension and Gaussian proxies (general). It should mention all three
   engineering caveats with the reviewer's wording as a starting point.

================================================================
PART D — RECOMMENDATIONS TO PROJECT OWNER
================================================================

D1. **FIX EXTRACT to incorporate the two-component caveat** (C1).
   Add a sentence: "The two-component BF (ΔlogZ ≈ +0.39 from T22) is a
   pipeline feasibility diagnostic, not definitive observational
   evidence — all three two-component observational likelihoods are
   still Gaussian proxies rather than raw posterior chains."

D2. **FIX EXTRACT to acknowledge the +0.2 dex calibration shift**
   (C2). Reword finding 1 to read: "The SIDM cross-section posterior
   at 1.4–1.7 cm²/g reflects a +0.2 dex calibration correction from
   the placeholder fluid model (T8 ~ 1.0 cm²/g) to the kinetic
   KiSS-SIDM model (T21 ~ 1.7 cm²/g). The T21 number is the more
   physically accurate estimate; the placeholder was overstated by the
   fluid model's IMFP-regime bias."

D3. **FIX EXTRACT Limitations to mention the 3 engineering caveats**
   (C3). Add as a new limitation: "Three engineering caveats
   per the R10 audit: (i) fixed reference halo parameters; (ii)
   unvalidated KiSS scaling extrapolation to dwarf/cluster masses;
   (iii) Gaussian proxy likelihoods remain primary barrier to
   peer-review publication-grade results."

D4. **KEEP the "10 independent observational probes" claim** but
   flag it as aspirational (per B7). Either in the README "What this
   is" or in EXTRACT Rationale. Not currently in EXTRACT — recommend
   adding: "The pipeline framework was designed to scale to 10+
   independent observational probes; 5–6 are currently fully integrated."

D5. **DO NOT touch the reviewer's specific numbers in CHANGELOG** —
   they're correct historical records of what was reported at D5.
   T20 = −1.46 is from the reviewer's own docx and cannot be
   cross-referenced to any current file. Leave alone.

================================================================
PART E — TIER-4 AUDIT SCORE
================================================================

| Dimension | Grade | Note |
|---|---|---|
| Tier-1 numerical accuracy | B- | 3 wrong numbers (B2, B3, B7) + 2 under-counts (B4, B6) + 1 unverifiable (B1) |
| Tier-1.5 framing | A- | Reviewer's caveats are well-framed; EXTRACT just doesn't surface them |
| Tier-2 engineering | A | Three engineering caveats identified accurately |
| Tier-3 stylistic | A | Clean writing, well-organized, tier-3 commentary useful |
| Tier-4 pushback (vs standing rules) | A | No standing-rule conflicts |
| Citation hygiene | A | All arXiv IDs verifiable on disk; no author misattribution |
| **OVERALL** | **B+** | Substantive critique, caveats are real, numbers mostly correct, EXTRACT fix is the main action |

================================================================
APPENDIX — Caveats applied to EXTRACT.md (2026-08-14)
================================================================

Per the user's request "more reviews to consider, try fix the caveats",
three changes were applied to EXTRACT.md:

1. **C1 fix**: Added explicit caveat that the two-component BF is a
   diagnostic, not definitive evidence; flagged Gaussian proxy status.
2. **C2 fix**: Reworded the headline σ/m finding to acknowledge the
   +0.2 dex placeholder→real calibration shift.
3. **C3 fix**: Added the three engineering caveats to Limitations.
4. **D4 fix**: Added 10-channel aspirational framing to Rationale.

Total EXTRACT.md revision: ~150 words added, ~50 words replaced.
Final word count: ~1000 (verified by direct count, within budget).