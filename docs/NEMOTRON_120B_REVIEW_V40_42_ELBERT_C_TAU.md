"""
Nemotron 120B qualitative review of the v40.42 Elbert+ 2015 c-tau prescription.

Model: nvidia/nemotron-3-super-120b-a12b:free via OpenRouter free tier.
Date: 2026-10-19.
Session: v40.42.
Reviewer: Nemotron 120B (qualitative, not a computational check).

KEY FINDINGS:
1. Elbert+ 2015 c-tau prescription is PHYSICALLY REASONABLE as first-order
   extrapolation. Retains Yang+ Eq. 5 in calibrated regime (tau <= 1),
   then forces concentration toward NFW value as halo undergoes deep
   core-collapse. Matches the N-body finding that even relatively
   strong self-interactions (sigma/m ~= 50 cm^2/g) only modestly
   reduce c_200.

2. The drop in c-M tension from 3.2 sigma (Ohana+ 2026) to 0.3 sigma
   (v19.2-F under Elbert+) is NOT MERELY AN ARTIFACT. It reflects the
   physically motivated expectation that deep core-collapse drives
   c_200 toward NFW baseline, erasing the spurious high-concentration
   bias introduced by extrapolating Yang+ Eq. 5.

3. RECOMMENDATION: marginalize over at least two physically motivated
   prescriptions (Elbert+ 2015 AND Burkert+ 2020) to demonstrate that
   the tension reduction persists across reasonable model variations.
   The single Elbert+ 2015 model is itself a simplification.

4. QUALITATIVE VERDICT UNCHANGED: Cloud-9 in deep collapse (tau >> 1)
   remains in tension with Ohana+ 2026's max-core (tau = 0.18). This
   suggests either the effective cross-section is overestimated, or
   additional physics (baryonic heating, velocity-dependent scattering)
   is needed.

5. The deep-collapse scenario should be presented as "plausible but
   not definitive" until such effects are modeled.

REVISED v40.42 VERDICT (incorporating Nemotron review):
  Before Nemotron review: "Elbert+ 2015 prescription gives c_200=6.0,
                            c-M tension 0.32 sigma (better than Ohana+)"
  After Nemotron review:  "Elbert+ 2015 prescription is physically
                            reasonable. c-M tension reduction is not
                            an artifact. RECOMMENDATION: marginalize
                            over Elbert+ 2015 AND Burkert+ 2020 for
                            robust claim. Qualitative verdict unchanged:
                            Cloud-9 in deep collapse vs Ohana+ max-core
                            remains a real tension."

NEXT-SESSION CANDIDATE (v40.43):
  Implement Burkert+ 2020 c-tau prescription and marginalize over
  BOTH prescriptions (Elbert+ 2015 and Burkert+ 2020) to demonstrate
  the tension reduction is robust across model variations.
"""

# Full review text
NEMOTRON_REVIEW = """
The Elbert+ 2015 c-tau prescription is physically reasonable as a
first-order extrapolation: it retains the Yang+ Eq. 5 behavior in the
calibrated regime (tau <= 1) and then forces the concentration to
approach the NFW value as the halo undergoes deep core-collapse, which
matches the N-body finding that even relatively strong self-interactions
(sigma/m ~= 50 cm^2/g) only modestly reduce c_200. The linear
interpolation to a 50% NFW floor and the saturation at tau >= 5 are
simple, monotonic bounds that avoid the unphysical rise of the Yang+
polynomial outside its domain.

The resulting drop in c-M tension from ~3.2 sigma (Ohana+ 2026) to
~0.3 sigma is therefore not merely an artifact of the prescription;
it reflects the physically motivated expectation that deep core-collapse
drives c_200 toward the NFW baseline, erasing the spurious
high-concentration bias introduced by extrapolating Yang+ Eq. 5.
However, because the Elbert+ 2015 model is itself a simplification--
anchored to a single sigma/m = 50 point and using a linear taper--it
does not capture the full possible range of c-tau relations (e.g.,
Burkert+ 2020 or more recent hydrodynamic simulations). For a robust
claim, the paper should marginalize over at least two physically
motivated prescriptions (Elbert+ 2015 and Burkert+ 2020) to
demonstrate that the tension reduction persists across reasonable
model variations.

Finally, the qualitative conclusion that Cloud-9 resides in deep
collapse (tau >> 1) remains unchanged and is in tension with Ohana+
2026's inferred tau ~= 0.18 (max-core). This discrepancy suggests
that either the effective cross-section adopted here is overestimated
or that additional physics (e.g., baryonic heating, velocity-dependent
scattering) is needed to reconcile the lensing-derived concentration
with the Ohana+ tau estimate. Until such effects are modeled, the
deep-collapse scenario should be presented as a plausible but not
definitive interpretation.
"""

if __name__ == "__main__":
    print(NEMOTRON_REVIEW)
