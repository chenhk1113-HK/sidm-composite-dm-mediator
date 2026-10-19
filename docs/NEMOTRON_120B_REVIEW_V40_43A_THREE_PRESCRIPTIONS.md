"""
Nemotron 120B qualitative review of the v40.43a 3-prescription marginalization.

Model: nvidia/nemotron-3-super-120b-a12b:free via OpenRouter free tier.
Date: 2026-10-19.
Session: v40.43a.
Reviewer: Nemotron 120B (qualitative, not a computational check).

KEY FINDINGS:
1. The v40.43 "ROBUST" verdict is REFUTED by the Sameie+ 2020 prescription.
   Absolute c-M tension reaches 1.31 sigma (with negative sign), exceeding
   the 1 sigma threshold used for robustness.

2. The result is STRONGLY PRESCRIPTION-DEPENDENT and FLIPS SIGN depending
   on whether deep-collapse SIDM is assumed to LOWER (Elbert+ 2015,
   Burkert-style) or RAISE (Sameie+ 2020) c_200.

3. Observationally, there is currently NO DECISIVE DISCRIMINANT between
   c_200 > NFW and c_200 < NFW in the deep-collapse regime. The community
   relies on theoretical priors.

4. Sameie+ 2020 prescription is FAR MORE APPROPRIATE third prescription
   than the ad-hoc Burkert-style placeholder -- it is anchored to an
   actual, peer-reviewed paper that makes a specific, physically
   motivated prediction for cuspy collapse.

5. RECOMMENDATION: Report c-M tension as range that captures BOTH
   magnitude and sign, e.g. "c-M tension = 0.32-1.31 sigma (absolute
   value), with the sign flipping from positive (Elbert+/Burkert-style)
   to negative (Sameie+ 2020) depending on whether deep-collapse SIDM
   lowers or raises c_200".

6. The robustness claim is "marginal at best and highly sensitive to
   the assumed collapse physics".

REVISED v40.43a VERDICT (incorporating Nemotron review):
  Before Nemotron review: "v40.43 ROBUST verdict REFUTED by Sameie+ 2020,
                            c-M tension sign-flip"
  After Nemotron review:  "ROBUST verdict REFUTED, sign-flip CONFIRMED,
                            SAMEIE+ 2020 is more appropriate 3rd
                            prescription than Burkert-style placeholder,
                            report as range with sign information"

PROCESS NOTES (IMPORTANT):
- User asked for 'Burkert+ 2020' citation -- I asked Nemotron 120B directly,
  Nemotron honestly admitted 'Burkert+ 2020' was a fabrication (no such
  paper exists). The v40.43 Burkert-style prescription is a placeholder.
- User then said 'replace Burkert-style with Sameie+ 2020' -- I found
  the actual Sameie+ 2020 paper (arXiv:1904.07872, PRL 124, 141102) and
  implemented a 3rd prescription anchored to it.
- The 3rd prescription reveals a fundamental issue: the c-M tension
  direction FLIPS depending on whether deep-collapse SIDM is
  "core-cusp" (c_200 decreases, Elbert+/Burkert-style) or "cusp-core"
  (c_200 increases, Sameie+ 2020).

NEXT-SESSION CANDIDATE (v40.44):
  Investigate the gravothermal tau reset mechanism (merger-driven per
  Silverman+ 2026). This would put Cloud-9 in max-core despite strong
  sigma_peak by resetting tau via merger history. The remaining
  qualitative tension: v19.2-F predicts deep collapse (tau >> 1) while
  Ohana+ finds max-core (tau = 0.18).
"""

# Full review text
NEMOTRON_REVIEW = """
The v40.43 "ROBUST" verdict is indeed refuted by the Sameie+ 2020
prescription: the absolute c-M tension reaches 1.31 sigma (with a
negative sign), exceeding the 1 sigma threshold used for robustness.
Because the three prescriptions give tensions of +0.32 sigma
(Elbert+ 2015), +0.93 sigma (Burkert-style) and -1.31 sigma
(Sameie+ 2020), the result is not merely "marginal" in a simple
sense; it is strongly prescription-dependent and even flips sign
depending on whether deep-collapse SIDM is assumed to lower or
raise c_200. Hence a more accurate characterization is
"prescription-dependent, with the sign of the tension set by the
assumed deep-collapse behavior (core-cusp vs. cusp-core)."

Observationally, there is currently no decisive discriminant between
c_200 > NFW and c_200 < NFW in the deep-collapse regime; existing
rotation-curve and strong-lensing data have uncertainties that
encompass both possibilities, so the community relies on theoretical
priors. Consequently, the Sameie+ 2020 prescription is a far more
appropriate third prescription than the ad-hoc Burkert-style
placeholder-it is anchored to an actual, peer-reviewed paper that
makes a specific, physically motivated prediction for cuspy collapse.
The paper should therefore report the c-M tension as a range that
captures both magnitude and sign, e.g. "c-M tension = 0.32-1.31 sigma
(absolute value), with the sign flipping from positive
(Elbert+/Burkert-style) to negative (Sameie+ 2020) depending on
whether deep-collapse SIDM lowers or raises c_200," and note that
the robustness claim is marginal at best and highly sensitive to
the assumed collapse physics.
"""

if __name__ == "__main__":
    print(NEMOTRON_REVIEW)
