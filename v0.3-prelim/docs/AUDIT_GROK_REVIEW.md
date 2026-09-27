# Audit — "Grok Review.docx" (2026-09-21)

User asked: critically consider whether useful.

This is a **fundamentally different review** from DeepSeek 1-6. While
DeepSeek focused on editorial issues (stale cross-refs, parameter
inconsistencies), Grok is critiquing the **scientific posture** of the
entire project — its claim of being a "model," the role of phenomenological
likelihoods, and the AI-lab process visibility.

---

## Grok's Main Points (Tier-Ranked by Severity)

### Tier 1: FUNDAMENTAL (must address)

**T1-A: "The repo and paper do not describe one stable model."**

> Releases and README still advertise "a single DM model satisfies every
> constraint" with m_χ ~ 485 GeV and magnetic moment in the LZ box; the
> v1.14.1 draft has Phase-44 / T163 parameters around 10 GeV,
> σ/m(100) ~ 0.05 cm²/g, magnetic dipole **ruled out**, and Hidden U(1)
> **falsified**. Outsiders cannot tell which number is current without
> reading thousands of lines of task notes.

**Status: TRUE.** Master README mentions m_χ ~ 485 GeV (older Phase 32);
current paper has m_χ = 10.3 GeV. Magnetic dipole was ruled out by T120.10.
Hidden U(1) was falsified per T135. This is the **most damning finding**
because it suggests the paper may be mis-representing itself to outside
readers via the README.

**Recommendation:** Either (a) freeze the README to match v1.14.1, OR
(b) add an explicit "model evolution history" panel at the top of README
listing m_χ values across versions and what's been falsified.

**T1-B: "Burkert wins once Occam is applied on rotation curves."**

> Your own Phase 40/54 results already say Burkert wins once Occam is
> applied on rotation curves. Keep that as the rotation-curve conclusion.

**Status: NEEDS VERIFICATION.** I do not remember Phase 40/54 results.
This is a Grok-specific claim that may or may not be in our task notes.
Must verify before incorporating into the paper. If true, this is a
genuinely important finding we've under-emphasized.

**Recommendation:** Search for Phase 40/54 task notes. If Burkert wins,
add this to §11 Conclusions as an honest finding.

**T1-C: "f_H(r) is borrowed from σ₀/m ~ 147, not computed at this σ/m(v)."**

> f_H(r) is recomputed at *this* σ/m(v), not borrowed from σ₀/m ~ 147

**Status: PARTIALLY TRUE.** T183 computed f_H = 0.61 at our σ/m values
via 1D fluid sim. AIDA-TNG f_H(r) was for σ₀/m ~ 147 cm²/g. We use both,
but the AIDA-TNG borrowing is a known caveat (cited in §9.5).

**Recommendation:** Make the AIDA-TNG caveat more prominent in §9.5 and
in the abstract.

### Tier 2: IMPORTANT (should address)

**T2-A: "Cut the archaeology." T-numbers, Phase 32-54, "v1.6 used wrong
kinematics" belong in appendix.**

> Hundreds of agent commits, "Hermes Agent" authorship, and task IDs in
> the paper body read as lab notebook, not a manuscript.

**Status: TRUE.** Paper currently has many "T120.10", "T163", "Phase 44"
references. For journal submission, these should be cut from the main
text and moved to a supplementary section or appendix.

**Recommendation:** For next major revision (v1.15), do a pass that
removes T-numbers and Phase IDs from main text, replaces them with
plain-language descriptions or footnote citations.

**T2-B: "Stop calling interpolation nodes resonances even in passing."**

**Status: TRUE (per memory: "T134 retracted, three bookkeeping nodes").**
We have retracted this already in §10.4a but it may still appear in
older sections.

**Recommendation:** Search paper for "resonance" near "node" and verify
all instances say "bookkeeping node, NOT a true resonance."

**T2-C: "JVAS: the Yu-substructure reframing is reasonable; then JVAS
should leave the 8-point σ/m table entirely."**

**Status: TRUE.** JVAS at ~10⁶ M☉ substructure scale is not on the same
σ/m(v) as the bulk halo. Should be removed from the 8-point fit table.

**Recommendation:** Move JVAS out of the 8-point table; note as
"complementary substructure physics."

**T2-D: "Bayes: lead with T177 log B ≈ 3, not scoring-rule ΔBIC = -170
or -24. Mixed methods should be one small table, not three headlines."**

**Status: TRUE.** We have three different model-comparison metrics
(ΔBIC, log B, RMSE). Should consolidate into one table.

**Recommendation:** Move §10.8 BIC table content to a small model-
comparison table; lead with T177 log B ≈ 3.

**T2-E: "Venue: mixed-verdict phenomenology + no-gos is closer to JCAP
than to a 'UV completion' JHEP paper."**

**Status: TRUE.** Current paper framing is "SIDM model satisfies 7 of 8
constraints." Better framing is "constraint map + no-go catalogue."

**Recommendation:** Update abstract to lead with constraint map framing;
submit to JCAP, not JHEP.

### Tier 3: SECONDARY (consider)

**T3-A: "One canonical σ/m(v) figure and one parameter table."**

**Status: PARTIALLY TRUE.** Paper has multiple σ/m(v) tables/figures
across Phase 44, T163, T120, T90.

**Recommendation:** Add a master figure showing the canonical σ/m(v) from
T163, with all other parameter sets referenced as supplementary.

**T3-B: "Literature and dates need an external audit."**

**Status: NEEDS ACTION.** Grok is right that this is needed before
journal submission. Some 2025-2026 citations may be confabulated.

**Recommendation:** Before journal submission, run an ADS/arXiv check
on every reference. Defer to submission-prep phase.

---

## What Grok Gets Right

1. The model evolution narrative is unclear to outsiders (T1-A). This is
   the most important finding and should be addressed before any
   submission.

2. The archaeology (T-numbers, Phase IDs) is lab-notebook, not
   manuscript (T2-A). Agree; needs cleanup for v1.15.

3. The interpolation nodes-as-resonances wording was a real failure mode
   that we retracted (T2-B). Should verify all instances are clean.

4. JCAP is the right venue, not JHEP "UV completion" (T2-E). Agree.

5. The mixed-verdict posture is the paper's greatest asset. Agree;
   should be the framing throughout.

## What Grok Gets Wrong (or Overstates)

1. "AI-lab process is both a feature and a liability" — Grok reads
   "Hermes Agent authorship" negatively, but this is the
   reproducibility feature. Could be reframed as "fully reproducible
   pipeline with documented audit trail."

2. The claim "Burkert wins once Occam is applied" needs verification.
   Not in current memory; need to check task notes.

3. "Cut the archaeology" — at the depth of detail we need to ship a
   reproducibility-first paper, the task IDs are actually load-bearing
   for the audit trail. Could move to supplementary rather than cut.

---

## Honest Self-Assessment

Grok's review is **substantively correct** about the repo/paper
discrepancy (T1-A) and the "AI-lab notebook" feel (T2-A). DeepSeek
focused on editorial issues; Grok focuses on scientific posture.

**Both reviews together** give a clear picture: the paper is internally
consistent (per DeepSeek) but externally unclear (per Grok). The right
next step is a major revision (v1.15) that:

1. **Freezes the README + paper to one consistent parameter set**
   (Grok T1-A).
2. **Cuts archaeology from main text, moves to supplementary** (Grok T2-A).
3. **Reframes as constraint map + no-go catalogue, not "model"** (Grok T2-E).
4. **Verifies the Burkert claim** (Grok T1-B).
5. **External reference audit** before submission (Grok T3-B).

---

## Per-Issue Action Plan

| Issue | Severity | Action | When |
|---|---|---|---|
| README / paper version drift | Tier 1 | Freeze README at v1.14.6; add evolution panel | Now (before send) |
| Burkert claim | Tier 1 | Search Phase 40/54 notes | Now |
| AIDA-TNG f_H caveat prominence | Tier 1 | Make more prominent in §9.5 | Now |
| T-numbers in main text | Tier 2 | Cut to supplementary for v1.15 | Defer to next version |
| JVAS in 8-point table | Tier 2 | Move to substructure section | Now |
| Mixed-method table consolidation | Tier 2 | Consolidate BIC/Bayes/RMSE into one table | Now |
| Abstract framing | Tier 2 | Reframe as constraint map | Now |
| External reference audit | Tier 3 | Defer to submission-prep | Before submission |
| Master σ/m(v) figure | Tier 3 | Add for v1.15 | Defer to next version |

---

## Bottom Line

Grok's review is the most useful of the seven reviews because it points
to the actual gap between the paper and the repo. DeepSeek fixed the
internal consistency; Grok identifies the external clarity problem.

For the current Telegram send: address the Tier 1 issues (README freeze,
AIDA-TNG caveat prominence) and Tier 2 low-effort items (JVAS move, mixed-
method table). Defer archaeology cleanup to v1.15.