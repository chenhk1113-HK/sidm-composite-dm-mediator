# Nemotron 120B Review of v40.2 (Cloud-9 N1 work)

**Date:** 2026-10-17
**Branch:** `wip/v19.2-F-init`
**Reviewer:** Nemotron 3 Super 120B (nvidia/nemotron-3-super-120b-a12b:free) via OpenRouter
**Reviewer prompt:** sent the full text of `docs/CLOUD9_REBASELINE.md` (v40.1) + `docs/REVIEWER_N1_RESPONSE_REPORT.md` (v40.2) with 5 specific questions.
**Reviewer time:** 25.0 s wall, 13142 prompt + 885 completion tokens

---

## Nemotron's findings (verbatim, summarized)

| # | Severity | Finding |
|---|---|---|
| 1 | OK | σ_v = W50/2.355 = 5.1 km/s derivation correct. |
| 2 | **HIGH** | "Cloud-9 verdict" is a consistency check of the project's internal α_D (from dynesty fit), NOT a Cloud-9-derived constraint. Paper reports no α_D. The IN BAND set is presented as Cloud-9-specific when it should be presented as a project-fit-vs-Cloud-9-halo check. |
| 3 | OK | Anand+ 2025 attribution correct, Yang+ 2024 debunked. |
| 4.1 | MEDIUM | Pointwise vs velocity-weighted for Cloud-9 not explained. |
| 4.2 | LOW | 1/Γ² scaling break at Γ/ρ≪1 dismissed without quantitative threshold. |
| 4.3 | MEDIUM | Dynesty likelihood relation unclear; sensitivity to α_D posterior not stated. |
| 5 | MEDIUM | "mechanism IS consistent with Cloud-9" wording implies Cloud-9 validates the model, but it's the reverse direction. Circularity not acknowledged. |

**Overall Nemotron verdict:** "MEDIUM overall (analysis is usable for internal consistency but not for claiming Cloud-9 as evidence)."

---

## Nemotron's revision (the structural edits) — what we applied

After the review, we asked Nemotron to produce revisions to specific sections. Nemotron returned 4 sections in a Python dict format. **Three sections were correct and were applied to the doc:**

### Section 1 (applied to §0): "Crucial clarification" paragraph
> The "Cloud-9 calibration" is a project-internal consistency check. The α_D = 5.55e-6 used here is from an independent dynesty fit to Lyman-α + SPARC data, NOT from Anand+ 2025. Cloud-9 only constrains M_halo ≈ 5×10⁹ M☉ and W50 = 12 km/s. The check is therefore: is the project's fitted α_D consistent with Cloud-9's observed M_halo and W50? (project → Cloud-9 direction), NOT: does Cloud-9 constrain α_D? (which it does not). The IN BAND verdict below depends on a prior fit, not on an independent Cloud-9 calibration of α_D.

### Section 3 (applied to §2 item 4): Updated Phase 3 framing
> Velocity-weighted σ_eff is the correct metric because it averages over the Maxwell-Boltzmann distribution of dark matter particle velocities, which governs halo-scale dynamics and halo formation thresholds. This acknowledges the circularity: the project's internal α_D (from dynesty fit) drives the verdict. The reframed conclusion is: the project's dynesty-fitted α_D is consistent with Cloud-9's halo properties; Cloud-9 does NOT independently validate α_D — it only constrains M_halo and W50.

### Section 2 (skipped — see §1.1 of REVIEWER_N1_RESPONSE_REPORT.md)
The doc already had the same "Note" that Nemotron recommended adding. No further edit applied (would have been redundant).

---

## ⚠️ Nemotron's fabrication: Section 4 sensitivity claim

Nemotron's proposed §4 (added to §2 item 7) claimed:
> "If the dynesty fit's posterior on α_D shifts by ±0.1 dex, the IN BAND set would shift to {5, 6, 7, 8, 9} (lower bound) or {7, 8, 9, 10, 11} (upper bound), i.e., the conclusion is robust at 1-sigma posterior width."

**This was fabricated.** We computed the actual sensitivity (see §2 item 7 of `REVIEWER_N1_RESPONSE_REPORT.md`):

| α_D shift | α_D value | IN BAND widths (computed) |
|---|---|---|
| nominal | 5.55e-6 | {6, 7, 8, 9, 10, 11} |
| -0.1 dex | 4.41e-6 | {5, 6, 7, 8, 9} (Nemotron's lower bound: correct) |
| +0.1 dex | 6.99e-6 | **{8, 9, 10, 11, 12, 13, 14}** (Nemotron's upper bound: WRONG) |
| -0.3 dex (3σ) | 2.78e-6 | {3, 4, 5} |
| +0.3 dex (3σ) | 1.11e-5 | {12, 13, 14, 15} |

**Nemotron's lower bound (lucky match), upper bound (wrong by 3 widths), and the "robust" framing (false).** At ±0.1 dex the lower and upper IN BAND sets have only {8, 9} in common — the central conclusion {6, 7, 8, 9, 10} does NOT survive a ±0.1 dex shift. At ±0.3 dex the sets are disjoint.

**Replacement text (now in §2 item 7):**
> The IN BAND set is FRAGILE to α_D uncertainty, not robust. ... The central conclusion "IN BAND at {6, 7, 8, 9, 10}" does not survive a ±0.1 dex shift; it shifts to overlapping but different widths. At ±0.3 dex the sets become disjoint ({3, 4, 5} vs {12, 13, 14, 15}). This sensitivity means the IN BAND verdict depends critically on the precise α_D value from the dynesty fit, and should be quoted with the α_D posterior width, not as a fixed point estimate.

---

## Lessons learned

1. **Nemotron 120B is a useful first-pass reviewer** — caught a real HIGH issue (the overstated "Cloud-9 verdict") that the user (me) and the original v40.2 review missed. The structural edits it proposed were correct.

2. **But it fabricates numerical claims.** The "robust" sensitivity claim was specific (gave exact sets and the +0.1 dex shift) and looked plausible — but was wrong. The lower bound happened to be right by coincidence; the upper bound was off by 3 widths.

3. **Always verify any specific numerical claim a model makes**, even when the model is reviewing. The verification cost was 1 Python run (2 seconds). The fabrication cost would have been an unverified claim published as fact.

4. **Reasoning models are vulnerable to plausible-sounding synthesis.** Nemotron returned the fabrication as a clean "sensitivity statement" without flagging that it was synthesizing rather than computing. This is a known pattern: reasoning models often produce "intuitive" answers that look rigorous.

5. **The mixed answer (Nemotron's review found real issues + Nemotron's revision contained a fabrication) is itself useful** — it shows that the "AI reviewer" pattern is good for the review, but the revision/authoring step needs human-in-the-loop.

---

## Net result

- **1 real HIGH finding applied** (the "Cloud-9 verdict" is a consistency check, not a Cloud-9 α_D constraint)
- **1 MEDIUM finding applied** (the Phase 3 verdict rephrasing)
- **1 MEDIUM finding applied with corrected numbers** (the sensitivity table — actual values, not fabricated)
- **2 OK confirmations** (σ_v derivation, paper attribution)
- **1 LOW finding noted but not addressed** (1/Γ² scaling break threshold — not worth the time)

Tests still 32/32 PASS. No code changes, doc-only edits.
