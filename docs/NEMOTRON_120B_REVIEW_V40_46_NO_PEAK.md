"""
Nemotron 120B qualitative review of the v40.46 no-peak re-analysis.

Model: nvidia/nemotron-3-super-120b-a12b:free via OpenRouter free tier.
Date: 2026-10-19.
Session: v40.46.
Reviewer: Nemotron 120B (qualitative, not a computational check).

KEY FINDINGS:
1. v40.46 result CONFIRMS the peak is a phenomenological placeholder.
   Setting peak=0 reduces tau from 16.4 to 0.06 (>250-fold drop),
   bringing the Cloud-9 c-M prediction into agreement with Ohana+ 2026.

2. The 273x tau reduction is CONSISTENT with treating the peak as a
   nuisance parameter. The observed scaling matches the expectation
   that the peak-induced contribution dominates the tension; removing
   it leaves only the Yukawa-only baseline, fully compatible with data.

3. RECOMMENDATION: UPDATE paper §2.1 to reflect that the Gaussian peak
   is a downgradable nuisance term (effectively set to zero in the
   baseline model) rather than a robust prediction of the framework.

4. PRIORITY for v40.47+: BOTH (c) -- re-derive the multi-resonance
   architecture without the peak AND re-evaluate Fornax sigma_HL under
   peak=0. Only after these updates can the paper be amended to
   present a consistent, peak-free version of v19.2-F.

REVISED v40.46 VERDICT:
  Before Nemotron review: "c-M tension FULLY RESOLVED by setting peak=0,
                            tau reduction 273x"
  After Nemotron review:  "CONFIRMED. Paper §2.1 should be updated to
                            reflect downgradable nuisance status. v40.47+
                            priority: BOTH (re-derive multi-resonance +
                            re-evaluate Fornax sigma_HL with peak=0)."

FRAMEWORK VALIDATION (9-VERSION ARC):
v40.39 (Yang+ over-claim) -> v40.40 (Nemotron 1st: known artifact) ->
v40.41 (f_H sensitivity: structural) -> v40.42 (Elbert+ prescription:
c-M 0.32 sigma) -> v40.43 (2-prescription: ROBUST 0.32-0.93 sigma) ->
v40.43a (3-prescription: ROBUST REFUTED, sign-flip) -> v40.44
(Silverman+ 2026: c-M tension NOT resolved) -> v40.45 (velocity-form
sensitivity: c-M tension ENTIRELY DRIVEN by Gaussian peak) -> v40.46
(no-peak re-analysis: c-M tension FULLY RESOLVED by setting peak=0,
273x tau reduction, paper §2.1 update recommended)

NEXT-SESSION CANDIDATE (v40.47, per Nemotron priority (c) BOTH):
  (a) Re-derive the multi-resonance architecture without the peak
      (3 interpolation nodes v2=100, v3=178, v4=430 km/s need new
      anchor since the peak is removed)
  (b) Re-evaluate Fornax sigma_HL with peak=0
      (Fornax at v=15 km/s was in the peak tail, may need re-fit)
  (c) Update paper §2.1 to reflect the downgraded peak status
      (Nemotron v40.46 recommendation)
"""

# Full review text
NEMOTRON_REVIEW = """
1. **Yes.** The v40.46 result shows that eliminating the Gaussian peak
(setting its amplitude to zero) reduces the tension metric tau from
16.4 to 0.06 -- a >250-fold drop -- and brings the Cloud-9 c-M
prediction into agreement with the Ohana 2026 upper limit. This
demonstrates that the peak was not a physically required component
but rather a phenomenological placeholder that, when removed,
resolves the discrepancy.

2. **Consistent.** Treating the peak as a nuisance parameter that can
be set to zero predicts that all observables that depend linearly on
its amplitude should scale to zero when the parameter is nulled. The
observed tau reduction of ~= 273x matches the expectation that the
peak-induced contribution dominates the tension; removing it leaves
only the Yukawa-only baseline, which is fully compatible with the
data.

3. **Update section 2.1.** The paper's section 2.1 should be revised
to reflect that the Gaussian peak is now regarded as a downgradable
nuisance term (effectively set to zero in the baseline model) rather
than a robust prediction of the framework. This aligns the
manuscript with the v40.45 recommendation and the v40.46 empirical
outcome.

4. **Priority for v40.47+.** Both the multi-resonance architecture
and the Fornax sigma_HL evaluation must be re-run with peak = 0
before claiming a full framework downgrade. Hence the priority is
(c) Both -- re-derive the multi-resonance components without the peak
and re-evaluate Fornax sigma_HL under the same condition. Only after
these updates can the paper be amended to present a consistent,
peak-free version of v19.2-F.
"""

if __name__ == "__main__":
    print(NEMOTRON_REVIEW)
