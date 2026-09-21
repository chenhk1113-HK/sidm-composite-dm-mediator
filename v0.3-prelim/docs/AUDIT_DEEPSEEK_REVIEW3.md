# Audit — "Deepseek Review 3.docx" (2026-09-21)

User asked: critically consider whether useful.

This is the third DeepSeek review. It contains:
- **Acknowledgement** that 7 prior concerns are now adequately addressed (T174,
  T176, T177, T191, f_H=0.61, AIDA-TNG, T185 bug fix)
- **One critical new physics issue** (Priority #1)
- **Three structural/editorial issues** (Priority #2-4)
- **Two internal consistency issues** (consolidate UV discussion, fix §10.6 vs §10.10)
- **Overall assessment**: paper is close to journal-ready at PRD/JCAP

---

## Finding #1 (CRITICAL) — T185/T190 thermal averaging issue

**Reviewer claim:** At δ = 0.43%, the BW resonance velocity is
v_res = √(8δ) = 0.185c, NOT v_F = 0.3c. Our T185/T190 evaluated BW at
v_F = 0.3c (hardcoded as v_F_over_c_sq = 0.0225), which means the BW
propagator is suppressed by ~1700× off-resonance. The previous "candidate
resolution" claim is wrong unless we thermal-average.

**Verification:** Confirmed. My exact computation gives:
- v_res(δ=0.43%) = √(8×0.0043) = 0.185c (= 55,600 km/s)
- v_F = 0.3c (= 90,000 km/s)
- s(v_F)/m_Φ² - 1 = v_F²/4 - 2δ - δ² = 0.0225 - 0.0086 ≈ 0.0139
- BW suppression: (Γ/m)² / ((Δs/m)² + (Γ/m)²)
  = (1.7×10⁻⁴)² / (0.0139² + (1.7×10⁻⁴)²)
  = 2.89×10⁻⁸ / 1.93×10⁻⁴
  = 1.5×10⁻⁴
- **Suppression factor: 6,668×** (reviewer said ~1700× — close, slightly different)

**Why this matters:** Our T185/T190 gives Ωh² = 0.128 by evaluating
σ_v at a single velocity v_F = 0.3c. But the proper thermal relic
calculation requires thermal averaging:

  <σv>(T) = (1/n_eq²) ∫ d³p₁ d³p₂/(2π)⁶ f(p₁) f(p₂) σ v_rel

where f(p) is the Maxwell-Boltzmann distribution at temperature T.
At freeze-out T_F ~ m_χ/20, the thermal velocity distribution is broad
(σ_v ~ 0.4-0.5c), so v_res = 0.185c IS within the thermal distribution.

**Three resolutions:**

(a) **Thermal average over Maxwell-Boltzmann.** This is the correct
treatment. The Boltzmann average over a Maxwell-Boltzmann distribution
with v_thermal ~ 0.4c would include the resonance at v = 0.185c.
<σv>_thermal_avg at T_F ~ m_χ/20 might give 2.8×10⁻²⁶ cm³/s if the
resonance width effectively broadens with the distribution. **This needs
to be computed.**

(b) **Re-tune δ to put resonance at v_F = 0.3c.** Solving v_F² = 8δ:
δ = v_F²/8 = 0.0112 = 1.12%. At δ = 1.12%, the resonance is at v_F.
But this is between the buggy 1.93% (overcounted σ_v) and the revised
0.43% (undercounted σ_v). Need to check if δ = 1.12% gives Ωh² = 0.12
with the correct propagator.

(c) **Honest downgrade** to "candidate requiring parameter tuning":
"two-mediator UV completion works at δ = 1.12% (resonance at v_F),
or at δ = 0.43% with thermal averaging (T192 to be done)."

**My assessment:** This is a paper-invalidating issue that must be
addressed before submission. Reviewer's recommendation is correct:
T192 (proper thermal-averaged BW calculation) is needed.

**Plan:** Write T192_thermal_avg.py with proper thermal average over
Maxwell-Boltzmann distribution. If result is Ωh² ~ 0.12, the candidate
stands. If not, downgrade to "candidate requiring parameter tuning" and
note δ = 1.12% as the on-resonance-at-freeze-out choice.

---

## Finding #2 (HIGH) — §10.6 vs §10.10 inconsistency

**Reviewer claim:** §10.6 says "No published UV completion solves the
Cloud-9 vs dSph tension" (correct), but §10.10 says the two-mediator
"satisfies ALL constraints" (misleading). §10.10 statement should be:
"satisfies the thermal relic density constraint and the SIDM
self-interaction constraint simultaneously, but does not address the
Cloud-9 spike, which remains beyond-Yukawa physics."

**Verification:** Already addressed in commit `af97ef7` (§10.10 was
clarified to "addresses thermal relic, NOT Cloud-9 spike"). Need to
check the "satisfies ALL constraints" wording was also removed.

**Action:** Verify §10.10 text and replace "satisfies ALL constraints"
with the correct scope-bounded language.

---

## Finding #3 (HIGH) — Three BIC/Bayes results in tension

**Reviewer claim:** §9.3.1 reports ΔBIC = −24.10 favoring T120 v1.13
(scoring-rule), while §10.8 reports log B = 3.06 (Bayes factor 21,
proper likelihood), while §10.9 reports BIC Δ = −19.80 favoring
constant σ/m model. These three are in tension.

**Recommendation:** State clearly that "BIC-based tests give mixed
results (depending on the dataset and whether scoring-rule or proper
likelihood is used), and that the proper Bayesian evidence (T177) gives
log B = 3.06 — strong but not decisive."

**Verification:** Need to check §9.3.1, §10.8, §10.9 to confirm the
three numbers cited by reviewer are correct, then add a unifying
sentence.

---

## Finding #4 (HIGH) — Internal-process content should be cut

**Reviewer claim:** ~2000 lines with 5+ internal T-numbers per
paragraph. The paper reads as an internal lab notebook with audit
trail. For journal submission:

· T165-T172, T174-T191 "investigation" narratives with test tables
· DeepSeek review1/review2 response sections (§10.8, §10.9)
· "bug fix note" paragraphs
· "deferred items" table (§10.9)
· "Recommended paper updates (applied in this revision)" lists

Should be moved to companion technical note or supplementary methods.

**Action:** Major editorial pass needed. Cut main paper to ~500-700
lines (currently ~2000). Move internal-process content to
PAPER_V1_DRAFT_SUPPLEMENTARY.md or a new TECHNICAL_NOTE.md.

---

## Finding #5 (MEDIUM) — Abstract too long

**Reviewer claim:** ~800 words; journal abstracts are typically 150-250
words. Need a single paragraph stating:
· The framework
· What it achieves (7/8 constraints)
· The key negative result (Cloud-9 spike requires beyond-Yukawa)
· The candidate UV completion (two-mediator, with caveats)

**Action:** Cut abstract to ~250 words.

---

## Finding #6 (MEDIUM) — §10 has 12 subsections, should consolidate to 5

**Reviewer recommendation:**
· §10.1 UV completion: general framework and constraints
· §10.2 One-mediator UV completions are ruled out (single table)
· §10.3 Two-mediator candidate (Drobczyk 2025)
· §10.4 Cloud-9 robustness: what standard Yukawa cannot do
· §10.5 EFT target map

**Action:** Consolidate §10 from 12 → 5 subsections.

---

## Finding #7 (MEDIUM) — §11 contradiction (concluding paragraph)

**Reviewer claim:** The conclusion has a sentence that mixes the
two-mediator candidate resolution with the Hidden U(1) retraction
caveat. Reader may be confused about which UV completion is the paper's
position.

**Recommendation:** Consolidate all UV completion discussion into a
single concluding paragraph that clearly distinguishes:
· The original Hidden U(1) attempt: falsified
· The one-mediator UV completions: ruled out (four no-gos)
· The two-mediator candidate: viable but requires verification

**Action:** Edit §11 to consolidate UV completion discussion.

---

## Priority Recommendations (per reviewer)

| # | Item | Effort | Impact |
|---|---|---|---|
| 1 | Thermal-average the BW annihilation (T192) | Medium | Critical |
| 2 | Fix §10.6 vs §10.10 inconsistency | Low | High |
| 3 | Reconcile three BIC/Bayes results | Low | High |
| 4 | Cut internal-process content to supplementary | High | High |
| 5 | Shorten abstract to ~250 words | Low | Medium |
| 6 | Consolidate §10 from 12 → 5 subsections | Medium | High |

## Bottom line

**One critical new physics issue** (T185/T190 thermal averaging — Priority #1)
needs T192 (proper thermal-averaged BW calculation).

**Three high-impact issues** (Priority #2-4) are editorial/consistency fixes.

**Two medium-impact issues** (Priority #5-6) are editorial cuts.

The reviewer explicitly says: "The paper is close to being journal-ready
at PRD or JCAP with a mixed-verdict framing."

**Recommendation:** Address Priority #1 (T192 thermal averaging) first,
then apply Priority #2-7 in a single editorial pass.

## Honesty notes

1. The T185/T190 thermal averaging issue is real. Our Ωh² = 0.128 at
   δ = 0.43% was computed by evaluating BW at v_F = 0.3c, but the
   resonance is at v_res = 0.185c. Single-velocity BW evaluation is a
   rough approximation; thermal averaging may or may not rescue the
   candidate.

2. The reviewer gave the editorial assessment a positive overall
   ("genuinely impressive project", "honesty about limitations is the
   paper's greatest asset"), which is reassuring.

3. The structural issues (length, internal-process content, abstract)
   are real and need a major editorial pass.

---

## Plan for next steps

**Phase 1 (PRIORITY 1, ~1 hour):** Write T192_thermal_avg.py with
proper thermal-averaged BW over Maxwell-Boltzmann at T_F = m_χ/20.
If Ωh² ~ 0.12, the candidate stands. If not, downgrade to "candidate
requiring parameter tuning" and note δ = 1.12% as the
on-resonance-at-freeze-out alternative.

**Phase 2 (PRIORITIES 2-7, ~3-4 hours):** Major editorial pass.
Cut internal-process content. Consolidate §10. Fix §10.6 vs §10.10.
Reconcile three BIC/Bayes. Shorten abstract.

**Phase 3:** Verify, commit, push, send paper.