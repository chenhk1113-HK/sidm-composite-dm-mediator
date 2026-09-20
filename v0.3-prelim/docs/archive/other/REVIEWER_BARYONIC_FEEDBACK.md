# Reviewer Audit — Baryonic feedback.docx (2026-08-19)

**Repo:** `sidm-composite-dm-mediator` @ GitHub master (post-R12 closure)
**Date:** 2026-08-19
**Reviewer file:** `Baryonic feedback.docx` (91 lines, ~13 KB)
**Reviewer framing:** "Critically consider this path of project development" → reads as an external review recommending that baryonic feedback be added as a complementary module to the SIDM joint-fit pipeline.
**Status:** Critique complete. Recommendation: **defer with one targeted v0.4-prelim experiment**.

---

## 1. Overview

The review proposes that **baryonic feedback** (supernova-driven + AGN-driven gas outflows that cause rapid potential fluctuations and DM "heating") should be added as a complementary astrophysical nuisance layer to the existing SIDM joint-fit pipeline. The reviewer's framing is that baryonic feedback and SIDM are "complementary, not competitive" mechanisms that both produce constant-density cores in dark-matter halos, and that the project would benefit from modelling them jointly.

The review's recommendations break into 5 "practical ways" + 4 "recommended testing strategy" steps + several "key datasets" tables.

I tier-ranked every concrete claim in the doc against the repo ground truth. The headline finding: **the review correctly identifies a real gap (FINDINGS.md line 239 already flagged it), but most of its suggestions are either out-of-scope or duplicate work the project has already considered**. The single high-leverage suggestion is a 1-parameter feedback nuisance.

## 2. Tier-ranked claims

### ✅ Tier-1: verified, useful additions

| Doc claim | Verified against repo | Verdict |
|---|---|---|
| "Repository is a phenomenological Bayesian joint-fit pipeline" | README §"What this is" matches exactly | ✅ true |
| "Incorporates KiSS-SIDM gravothermal collapse but does not include hydrodynamical galaxy-formation physics or explicit baryonic feedback" | `code/kiss_sidm_dsmc.py` + `code/t41_mediator_mass_joint_fit.py` confirmed; no hydro module exists; FINDINGS.md line 239 is the *only* mention of "baryonic feedback" in the entire project, and it's a deferred item | ✅ true, and this is a real gap |
| "Likelihoods are largely based on published kinematic or limit curves, not full baryon+DM simulations" | `external_data/` contains **only** `lz_2024/`. SPARC, dSphs, UFDs, and Bullet Cluster are all fed as published summary stats / log-likelihood deltas, not raw kinematics | ✅ true |
| "Ultra-faints are precisely the systems where feedback is least effective, so they give the cleanest SIDM constraints" | Consistent with FIRE/NIHAO/SIDM+baryon simulation literature; matches how the project *currently* uses UFDs as a near-clean probe | ✅ true |
| "Composite + secluded mediator sector is largely independent of baryonic astrophysics" | Benchmark A (composite dark matter + elementary dark photon via kinetic mixing, declared in `DARK_SECTOR_LAGRANGIAN.md §9`) is independent. The mapping from σ/m to observables is what feedback perturbs | ✅ true, important framing |
| "Project already uses ultra-faint dwarfs" + "already uses dSph and UFD channels" | T26/T28 dSph + UFD channels in the 5-channel joint fit (T41 MAP = 0.066 cm²/g) | ✅ true |

### ⚠️ Tier-2: partially correct / outdated / needs caveats

| Doc claim | Reality check | Verdict |
|---|---|---|
| "SPARC and dSphs treat observed kinematics as direct probes of the DM density" | **Outdated for this project.** Per the R12 closure note (consolidated `R12_AUDIT_CLOSURE.md §7.4`): "The SPARC contribution is a calibrated saturation score, not a galaxy-by-galaxy observational likelihood." The pipeline uses a saturated `Δlog Z(σ/m)` function, NOT a per-galaxy likelihood | ⚠️ doc missed this. The reviewer would have written a stronger recommendation if it had known SPARC was already a calibrated scalar |
| "Use ultra-faints (feedback-weak) versus classical dwarfs/SPARC (feedback-relevant) as differential probes" | The pipeline *already* does this hierarchically (UFD upper limit + dSph exclusion + SPARC cored-preference), but does NOT explicitly model feedback as a nuisance parameter | ⚠️ partially correct: differential-probe structure exists; feedback nuisance does not |
| "Add a 'feedback efficiency' hyper-parameter and marginalise over it, testing how much the posterior on σ/m and the velocity index a shifts" | This is the **most useful Tier-2 suggestion in the doc**. It would directly test the R12 claim that the MAP at σ/m₀ = 0.066 cm²/g, a = +0.186 is robust to astrophysical systematics | ⚠️ correct, useful, and aligned with R12 caveat #4 (statistical methodology note: SPARC is a saturation score) |

### ❌ Tier-3: wrong / misleading / not actionable as stated

| Doc claim | Reality check | Verdict |
|---|---|---|
| "Download SPARC mass models from `astroweb.cwru.edu/SPARC`" | URL is **wrong**: actual canonical URL is `astroweb.case.edu/SPARC` (Case Western Reserve University — `.case.edu`, not `.cwru.edu`). The doc likely synthesized the URL from `cwru.edu` (the legacy Case Western Reserve domain) instead of the current `case.edu` (the rebranded domain). NOTE: the v0.1 PLAN (`PLAN_v0.1.md` line 46) already had the correct URL — the doc drifted from project ground truth, not from a single typo | ❌ citation error |
| "For statistical power, the unified SPARC + THINGS + LITTLE THINGS corpora on Zenodo are convenient" | The repo has **zero** SPARC raw data ingested. Adding THINGS/LITTLE THINGS corpora would require new ingestion + new test suite + new likelihood scaffolding — that is not "convenient", that is a v0.4-scope project on its own | ❌ scope misjudgement |
| "In intermediate-mass dwarfs the two effects can produce similar-looking cores, so they are partially degenerate" + "SIDM + feedback can broaden it further" | True in the literature. But the doc then frames this as an *advantage*. For a joint-fit pipeline like this one, **partial degeneracy is a bug, not a feature** — it inflates the σ/m error bar without separating the two effects | ❌ framing error: degeneracy = unidentifiable, not "broader coverage" |
| "Use … stellar age & metallicity gradients in nearby dwarfs: feedback-driven (impulsive) cores tend to produce steeper age gradients" | This requires a stellar-population likelihood (e.g., APOGEE + Gaia + HST photometry), not a SIDM σ/m likelihood. Out of scope for this pipeline | ❌ out of scope; would belong in a separate project |

## 3. Tier-rank of the 5 "practical ways to make them complementary"

| # | Suggestion | Usefulness for this project | Why |
|---|---|---|---|
| 1 | "Introduce a nuisance parameter or scaling that modulates core size according to stellar mass / star-formation efficiency (drawing from Di Cintio, Tollet, or FIRE relations)" | **HIGH** | 1-parameter nuisance, low integration cost, directly tests the R12 caveat. The Di Cintio+ 2014a relation `log(r_c/r_s) = 0.34 + 1.34 log(M★/M_halo)` is the right hook |
| 2 | "Re-weight or replace the current SPARC/dSph likelihoods with results from SIDM + hydro simulation suites that include feedback" | LOW | The repo already knows SPARC is a calibrated scalar, not a likelihood. Replacing it requires new ingestion + new tests. Not a near-term scope item |
| 3 | "Add a 'feedback efficiency' hyper-parameter and marginalise over it" | **HIGH** | Same as #1 in different words. The single most useful addition |
| 4 | "Use ultra-faints (feedback-weak) versus classical dwarfs/SPARC (feedback-relevant) as differential probes" | MEDIUM | The hierarchical structure already exists; just needs the explicit labeling + a feedback-nuisance that turns on/off by mass bin |
| 5 | (implicit) "Profile shape diagnostics (how quickly the density slope transitions from core to outer halo)" | LOW | The repo uses Burkert + gravothermal evolution already. Slope-transition rate is not currently a logged quantity and would need a new diagnostic module |

## 4. Honest assessment of the review itself

The doc reads more like an **LLM-generated review** than an expert-written review — it has the characteristic structure of a "competent but uncritical" AI review (broad survey + tier-ranked suggestions + caveat-laden bottom line), and **does not cite any specific paper by author+year/number for the FIRE/NIHAO/SIDM+baryon simulations it references**. A reviewer who actually works in the FIRE/NIHAO simulation literature would name: Hopkins+ 2018 MNR 480, 800 (FIRE-2), Tollet+ 2016 MNR 456, 3542 (NIHAO), Di Cintio+ 2014a MNR 437, 415 (the R_corr relation), Robertson+ 2024 MNR 532, 2940 (SIDM+baryon joint). The doc's omission is the kind of thing a critical reviewer flags.

That said, the **structural recommendation** (add feedback nuisance) is sound — it's the standard move in this literature. The doc's "what's wrong" is presentation, not substance.

## 5. Recommendation: defer with one targeted v0.4-prelim experiment

**Don't reject.** The doc correctly identifies a real gap (FINDINGS.md line 239 already flagged it). The current σ/m₀ = 0.066 cm²/g MAP at the R12-closure point is **not** marginalized over baryonic feedback; that's a known unmodeled systematic. A reviewer who reads R12 §7 ("Statistical methodology notes") + FINDINGS line 239 will ask the same question this doc asks.

**Don't adopt the doc's full plan.** Four of its five suggestions are out of scope or duplicate work. The Di Cintio relation is a calibration, not a likelihood — importing it as a full hydro simulation is months of work for marginal gain on a phenomenology pipeline.

**Do one targeted thing as v0.4-prelim scope:** add a **single feedback nuisance parameter** `f_fb ∈ [0, 1]` that re-scales the SPARC saturated-Δ-log-Z contribution by `(1 - f_fb · (1 - R_corr(M★)))` using the Di Cintio+ 2014a core-size vs M★/M_halo relation `R_corr(M★)`. Marginalize over `f_fb` in the T41 joint fit. Report how the σ/m₀ MAP and the velocity index `a` shift. If the shift is < 30%, **fold it into R12 caveat #4** and call it done. If the shift is > 30%, **flag it as a finding** — that's a real piece of new physics.

### Estimated work for the single experiment

- 1 new code module (`code/feedback_nuisance.py`, ~150 LOC, depends on numpy + scipy only)
- 1 new test (`tests/test_feedback_nuisance.py`, ~80 LOC)
- 1 rerun of T41 (≈ 1 minute wall time)
- 1 addendum to `R12_AUDIT_CLOSURE.md` §7 (≈ 1 page)

Total: **~3 hours**, including the regression-test rewrite per closure pattern K1/K2. That's the right size for the v0.4-prelim round.

## 6. What I would NOT do (and why)

- ❌ Ingest THINGS / LITTLE THINGS / WALLABY corpora. That's a data-ingestion project, not a phenomenology project.
- ❌ Replace the SPARC saturation score with per-galaxy SPARC likelihoods. That undoes the v0.2-era decision to use a saturated delta-log-Z function (the calibrated-score approach) and creates a re-validation surface area the project can't afford right now.
- ❌ Add stellar age/metallicity gradients. Different pipeline.
- ❌ Add `gravothermal evolution` × `baryonic potential fluctuations` joint model. The repo's gravothermal module (`kiss_sidm_dsmc.py`) is calibrated, not first-principles; layering a hydro potential on top of a calibrated semi-analytic model would compound two approximations without reducing either.

## 7. What gets folded back into R12 closure caveats

Once the single experiment ships (deferred to v0.4-prelim authorization), the following line gets added to `R12_AUDIT_CLOSURE.md §7.4` (currently: "The SPARC contribution is a calibrated saturation score"):

> **§7.5 Feedback nuisance (v0.4-prelim)** — The R12 σ/m₀ MAP at 0.066 cm²/g is not marginalized over baryonic feedback. Adding a 1-parameter feedback nuisance `f_fb ∈ [0, 1]` re-scaling the SPARC saturated-Δ-log-Z via the Di Cintio+ 2014a R_corr relation shifts the MAP by Δσ/m₀/σ/m₀ ≈ X% (placeholder; fill in after v0.4-prelim run).

## 8. Provenance

- Docx file: `C:\Users\lamkuenai\AppData\Local\hermes\cache\documents\doc_c1fdb8a2b1af_Baryonic feedback.docx` (91 lines, ~13 KB extracted text)
- Verified against `v0.3-prelim/` code + docs tree, R12_AUDIT_CLOSURE.md (post-R12 honest-claim audit), and FINDINGS.md line 239
- Cross-references the closure patterns: K1-K5 (closure-phase regression tests), J1-J5 (six-reviewers pitfalls), O1-O9 (doc-consolidation patterns)