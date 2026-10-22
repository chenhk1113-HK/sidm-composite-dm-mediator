# OpenCode CLI Review

**Model:** `opencode/glm-5.3-flash-free`  
**Generated:** 2026-10-22 12:41:17 China Standard Time  
**Duration:** 242.0s  
**Transport:** `opencode run --model <id>` (OpenCode free tier is CLI-only; direct API returns HTTP 403 FreeTierError)  
**Reviewer role:** second independent reviewer, different model family from the Nemotron/OpenRouter reviewer  

> **Status: UNVERIFIED SECOND OPINION.** This is one reviewer's critique. Every specific numerical claim below must be recomputed in Python before it is acted on -- the free-tier models fabricate plausible numbers. Compare against the Nemotron review: where they agree, the finding is likely real; where they disagree, that is the claim to compute first.

**Prompt source:** `scripts\review_prompt_r5_excerpt.md`

## Priority chain attempt log

| Model | Result | Seconds |
|---|---|---|
| `opencode/glm-5.3-flash-free` | OK | 242.0 |

## Review

I've read the full manuscript (`v0.3-prelim/docs/PAPER_V1_DRAFT.md`, 2400 lines, draft v19.2-F Phase 3 / paper-A at HEAD `598c975`, plus the supplementary and A.15 canonical context). Here is my review.

---

# Reviewer 2 Report — "Multi-Component SIDM: Joint Multi-Channel Constraints and UV Completion No-Gos" (draft v19.2-F Phase 3)

**Recommendation: Major revision — do not send out for submission until Items 1–4 are addressed.** The scientific honesty is genuinely commendable (the retraction trail, the R88(87) demotion, the peak-as-nuisance downgrade are all the right calls), but the manuscript is currently a lab notebook, not a paper, and it still contains internal contradictions that mislead a reader about what the framework actually claims.

## Major issues

**1. The document contains an entire AI-review-response workflow embedded in the body text.**
Sections §2.6b–§2.6l are version-by-version response logs to "Nemotron 120B / 3 Ultra 550B" reviews, with verbatim LLM blockquotes ("Per Nemotron 120B review (v40.42, 17.0s response)…"), response latency timestamps, "user directive: proceed v40.44", and "next-session candidate" to-do items (lines 222–300, 415–456, 722–778, etc.). Similarly, §3.5a and §9.18 carry T-round chatter and "sent to Telegram msg 77375"-style process artifacts (in CURRENT.md). None of this can appear in a submitted manuscript. Extract the one-paragraph final verdict of each sub-section, move the full audit trail to supplementary/appendix, and delete response latencies and reviewer-model names.

**2. The headline channel-count is self-contradicting and buried.**
The abstract states **8 constrained channels (4 PASS / 3 MARGINAL / 1 FAIL)** (line 19), but §A.15 Block 2 (line 2275) states that at the *published-σ_unc* likelihood the same canonical parameters give **1 PASS / 0 MARGINAL / 7 FAIL** (Cluster only), with 5/8 only for the alternative 5-param DE fit. The 4/3/1 count therefore lives under a σ_unc convention that the paper itself flags as "self-normalized" (§9.6). A reader who stops at the abstract walks away with a materially rosier verdict than the paper's own most defensible accounting. I acknowledge v19.2-E A.1 discloses this, but a caveat attached to a headline is not the same as a headline. The abstract must lead with the likelihood-convention question and state both counts explicitly, or adopt one convention throughout.

**3. §9.17b "first-class structural result" undercuts itself.**
The trade-off is promoted to one of the paper's two first-class results while the text simultaneously discloses that the project's **own N-body (Phase G9, f_H drop 0.94–1.01×) is "not subject to the trade-off"** (§9.17b caveat, §A.15 Block 2). So the second headline result amounts to: "the Yang+ 2025 SIDM2c parameterization, applied outside its validated regime, fails our benchmarks." That is a critique of one external parameterization, presented at factor-300×/1900× strength in the abstract. Either (a) demonstrate why SIDM2c is the physically relevant case and Phase G9's flat result is the artifact, or (b) demote §9.17b to map-entry status alongside the v=150 tuning statement. As written, the abstract claims two first-class results; I count one (§2.6a) at full strength.

**4. Cloud-9 is simultaneously declared PASS and "no observational lower bound exists."**
§3's channel preamble (line 826) candidly states Cloud-9's data impose **no σ/m lower bound** — the ≥50 cm²/g number is Elbert+ 2015's largest *simulated* cross-section adopted as a benchmark, and the genuinely observational constraint is an *upper* bound requiring N-body. Yet the canonical accounting (§A.15 Block 1) counts "Cloud-9 v=28 PASS" against the 50 floor. Pass/fail verdicts against a benchmark the paper itself has disclaimed as observational should not be counted in headline PASS tallies. Recount all headline numbers with the benchmark's status (simulation anchor vs. observation) stated per channel.

**5. The gravothermal machinery that drives key verdicts is self-flagged as unreliable exactly where it is used.**
- §9.12: at the canonical point (σ/m ≈ 162 cm²/g, c=12), Balberg+ violates the paper's own causality cap by ~3.6× and is "analytical only, not physical" (lines 1172, 1181–1183).
- §A.16: the calibrated prefactor is halo-specific and underestimates the only independent halo (Cosmo-501) by ~10×; §2.5 accordingly reduces Fornax t_core claims to "order-of-magnitude, factor 2–10× halo-specific uncertainty."
- And σ_peak = 174 is a "causality cap" **derived from Balberg+ at the very point Balberg+ is declared unreliable** (§A.14). The cap is post-diction-consistent internally, but its evidentiary status is weak: the framework's headline parameter inherits the failure mode of the formula that set it. State this explicitly in §2.6a, not just in A.16.

**6. Broken document structure.**
- §2.6a appears twice nearly verbatim (lines 194–219 and 695–718).
- §9.13–§9.18 are physically located *inside* §10 (after the §10 header at line 1185), breaking the announced organization (§1→§2→§3→§9→§10→§11).
- §9.14 contains a duplicated sentence-block ("The R88(40)/(42) Phase G4 pipeline had a systematic error…" appears twice, lines 1316 and 1329).
- The abstract is ~1000+ words (lines 9–27); the v18.41 changelog claims it was compressed to 282 words. It has regrown.
- The References section has 28 of 41 entries as "[NEEDS CITATION]" (lines 2019–2063) — not submittable.

**7. The "Bayes-favored 11×" verdict in §10.5 (line 1977) has the reasoning backwards.**
The text argues multi-resonance wins "because the prior volume in the 7-parameter space is 3.6× larger." All else equal, a *larger* prior volume *dilutes* the evidence; a Bayes-factor win comes from likelihood concentration relative to prior mass, not from volume per se (Occam factor). Combined with BIC disfavoring the same model, this is the classic configuration where the evidence ratio must be shown, not narrated. Please show Z_multi and Z_single with the prior definitions, and reconcile honestly — this may flip the verdict. The line "Independent verification required before citing" is itself an admission the table is not yet a result.

## Moderate issues

**8. Inconsistent f_H "canonical" bookkeeping.** constants.py fixes f_H = 0.297 as the single canonical value (§2.5 note, line 105); §2.5/§2.6 tables use 0.297 and 0.30 interchangeably (0.09 vs 0.0882 suppression — a 3.4% drift); §9.11 uses f_H_int per prescription (0.444–0.765); §9.17b uses SIDM2c f_H(r). Each switch is footnoted, but the cumulative effect means "the canonical σ_eff" is not one number. One master table (parameter → value → which scripts consume it) belongs in §3.4.

**9. σ/m(15) tension factors vary in-text: "10× above" (0.8 ceiling, §2.5 D-5 list), "14× above" (0.2 threshold, §3 table), "3.6–23.7×" (abstract, w=10 ceiling at v_eff 5–20 with 0.8-σ₁ tail?).** I verified the arithmetic 0.052·(100/15)^1.93 + 174·exp(−(15−29.4)²/38.72) ≈ 2.84 — the σ/m values are right; the *multiples* quoted for the same velocity differ across sections because three different thresholds silently rotate (0.8, 0.2, and 0.06). A single table listing σ/m, each published threshold with its own citation and the resulting factor per threshold would fix this permanently.

**10. Gaussian vs Breit-Wigner conventions "differ by up to ~30×" (§A.2)** yet specific numbers are asserted under whichever convention the section prefers. A 30× convention sensitivity at UFD velocities is not a "qualitative-unchanged" matter for near-threshold (MARGINAL) channels. Fix the convention once and quote one set of numbers everywhere (the paper half-does this; finish the job).

**11. Option A vs Option B in the hierarchy derivation (§A.3).** The headline g_N/g_χ ≲ 1.7×10⁻¹³ is the LZ-tuned post-diction; under the framework's own portal (Option B), LZ excludes it at ≈21 orders (line 928, A.3). This is earth-shattering for the model claim and resides in an appendix footnote. §1 states only Option A. Promote the Option B conditional into §1 or §11 with equal typographic weight.

**12. Horigome comparison.** §A.8 correctly notes the 27–49× factors apply a velocity-*independent* decisive threshold to a velocity-*dependent* σ/m(v), so the comparison is an upper bound on tension — yet the abstract quotes "in severe tension… 3.6–23.7×" without that qualifier. Add the qualifier where the number is quoted.

## Minor issues

- Line 1007/1013: "extreme UFD (v=3): 0.94 ✗" in the Yang+ row of §9.3 contradicts line 1076 ("with Yang+-derived f_H … 4 of 8 pass; Cloud-9, dSph, extreme-UFD, SPARC all fail") — consistent, but line 1013's parenthetical should also list extreme-UFD (it names only Cloud-9, dSph, SPARC; the row shows extreme-UFD failing too).
- §2.2 title has a typo: "One resonance + three bookkeeping interpolation nodes**UV status of node positions:**" — markup collapse from the bold-runaway editing style; there are many such run-together sentences (§2.5, §2.7, §9.12). A full de-boldening and re-typesetting pass is needed.
- §10.3 table: T185's g_h_SM row shows four pre-fix values plus the canonical in the wrong column position (0.01 | 0.002 | 0.001 | 0.00040 with column labels off by one).
- "The σ/m ≥ 50 cm²/g working benchmark is Elbert+ 2015's largest simulated cross-section for v_rms ~ 40 km/s" — benchmark semantics matter here; consider naming it more precisely ("simulated upper reference value").
- ASCII "d<σv>/dv_rel" plot (§10.3) — replace with a real figure.
- Fig. 1 reference (line 78) points to a PNG in `v0.3-prelim/data/results/`; for submission the figure and its caption need to be in the document, with the f_H = 0.297 vs 0.30 distinction footnoted.
- The truncation artifacts (lines ending "(line truncated to 2000 chars)") indicate unsplit paragraphs of 2000+ chars — a formatting bug in the draft generator that also hampers review.

## What I consider salvageable and worth keeping

The two genuinely valuable deliverables are (i) the **§2.6a c=12 vs c=4 σ_peak viability analysis** (empty viable window at ΛCDM concentration — a clean ratio argument) and (ii) the **Phase 3 FAIL verdict** (no single-/t-channel Yukawa UV sector reproduces the phenomenological σ/m(v)), plus the unusually disciplined retraction process. If the paper were rewritten as: Introduction → model as phenomenology (§2.1, one page) → the §2.6a tension → Phase 3 UV scan results → no-go list with the CONSTRAINT/SCALING_ARGUMENT taxonomy → honest channel table at one likelihood convention → the A.15 machine-generated table as THE accounting — it would be a compact, defensible ~25-page paper. That rewrite is a real task and I'd be happy to review it.

Please respond point-by-point; items 2, 3, 4, and 7 change the paper's claims, items 1 and 6 change its form.
