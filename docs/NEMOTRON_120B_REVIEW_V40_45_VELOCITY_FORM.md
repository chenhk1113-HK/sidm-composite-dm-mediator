"""
Nemotron 120B qualitative review of the v40.45 velocity-form sensitivity.

Model: nvidia/nemotron-3-super-120b-a12b:free via OpenRouter free tier.
Date: 2026-10-19.
Session: v40.45.
Reviewer: Nemotron 120B (qualitative, not a computational check).

KEY FINDINGS:
1. The v40.45 result is CORRECT: only the canonical v19.2-F form
   (Gaussian Breit-Wigner peak anchored at v ~ 29.4 km/s) yields
   sigma/m ~ 166 cm^2/g and tau ~ 16 Gyr (deep core collapse).
   All three alternative forms (Yukawa-only, resonance at v=50,
   resonance at v=100) produce sigma/m ~ 0.6 cm^2/g and tau ~ 0.06
   Gyr, fully consistent with Ohana+ 2026 max-core benchmark.

2. If the Gaussian peak truly represents a dark-QCD resonance (Tsai 2022),
   then the tension would be structural. However, the peak is presently
   a PHENOMENOLOGICAL FIT to the Cloud-9 point with NO INDEPENDENT
   DETECTION or theoretical prediction fixing its width, amplitude,
   or velocity location. It functions as a PLACEHOLDER that can be
   moved or removed without affecting the Yukawa tail. Given this
   lack of corroborating evidence, the more plausible interpretation
   is that the peak is an ARTIFACT of the current parametrization,
   and the tension arises from over-fitting a single data point.

3. v40.45 IS the "additional physics" Nemotron envisioned in v40.44:
   it systematically explores alternative velocity-dependent sigma/m
   forms, testing whether the tension persists when the assumed
   resonance is altered or removed. The analysis focuses on the SIDM
   sector rather than baryonic effects.

4. RECOMMENDATION: "The framework should reconsider or downgrade the
   peak's status -- preferably treating it as a PHENOMENOLOGICAL
   NUISANCE PARAMETER THAT CAN BE SET TO ZERO, thereby alleviating
   the c-M tension without invoking new baryonic physics."

REVISED v40.45 VERDICT (incorporating Nemotron review):
  Before Nemotron review: "c-M tension entirely driven by Gaussian
                            peak assumption"
  After Nemotron review:  "CONFIRMED -- Gaussian peak is more likely
                            a phenomenological placeholder than a
                            real resonance. Framework should downgrade
                            peak status to nuisance parameter that can
                            be set to zero."

FRAMEWORK IMPLICATIONS (v19.2-F core assumption):
  - The framework's published position (§2.1) treats the Gaussian
    peak as a real dark-QCD resonance. Nemotron's review suggests
    this should be downgraded.
  - If the peak is removed (Yukawa-only form), the c-M tension is
    resolved at the cost of the dark-QCD resonance interpretation.
  - The framework would need to be re-evaluated:
    (a) Re-derive sigma/m(v) without the Gaussian peak
    (b) Re-run all v40.x analyses with the new formula
    (c) Update paper §2.1 to reflect the new interpretation
  - This is a MAJOR framework shift, but Nemotron's review
    suggests it is the most likely resolution.

FRAMEWORK VALIDATION (8-VERSION ARC):
v40.39 (Yang+ over-claim) -> v40.40 (Nemotron 1st: known artifact) ->
v40.41 (f_H sensitivity: structural) -> v40.42 (Elbert+ prescription:
c-M 0.32 sigma) -> v40.43 (2-prescription: ROBUST 0.32-0.93 sigma) ->
v40.43a (3-prescription: ROBUST REFUTED, sign-flip) -> v40.44
(Silverman+ 2026: c-M tension NOT resolved) -> v40.45 (velocity-form
sensitivity: c-M tension ENTIRELY DRIVEN by Gaussian peak)

NEXT-SESSION CANDIDATE (v40.46):
Per Nemotron recommendation, DOWNGRADE the Gaussian peak status to
"phenomenological nuisance parameter". This is a MAJOR framework shift
that requires:
(a) Updating scripts/constants.py: separate the peak amplitude as a
    fit parameter (can be set to 0)
(b) Re-running v19.2-F canonical analysis without the peak
(c) Updating paper §2.1 to reflect the new interpretation
(d) Re-running the c-M tension analysis with the new formula
(e) Re-evaluating the paper's central claims
"""

# Full review text
NEMOTRON_REVIEW = """
1. The v40.45 result is correct: only the canonical v19.2-F form, which
includes the Gaussian Breit-Wigner peak anchored at v~29.4 km/s, yields
a huge central cross-section (sigma/m ~ 166 cm^2/g) and a collapse
timescale tau ~ 16 Gyr (deep core collapse). All three alternative
forms--Yukawa-only, a resonance shifted to v=50 km/s, and a resonance
at v=100 km/s--produce sigma/m ~ 0.6 cm^2/g at the same velocity, giving
tau ~ 0.06 Gyr, fully consistent with the Ohana+ 2026 max-core
benchmark. Hence the c-M tension is entirely driven by the assumption
of that narrow peak.

2. If the Gaussian peak truly represents a dark-QCD resonance (as
Tsai 2022 suggests), then the tension would be structural and would
require new particle-physics input to reconcile SIDM with observations.
However, the peak is presently a phenomenological fit to the Cloud-9
point with no independent detection or theoretical prediction fixing
its width, amplitude, or velocity location; it functions as a
placeholder that can be moved or removed without affecting the Yukawa
tail. Given this lack of corroborating evidence, the more plausible
interpretation is that the peak is an artifact of the current
parametrization, and the tension arises from over-fitting a single
data point rather than from a fundamental shortcoming of SIDM.

3. In v40.44 I called for "additional physics (e.g., baryonic feedback
or velocity-dependent self-interactions)" to alleviate the c-M
tension. The v40.45 analysis directly addresses the latter: it
systematically explores alternative velocity-dependent sigma/m forms,
testing whether the tension persists when the assumed resonance is
altered or removed. Thus v40.45's velocity-form sensitivity is
precisely the "additional physics" inquiry I envisioned--though it
focuses on the SIDM sector rather than baryonic effects.

4. The framework's published stance (§2.1) treats the Gaussian peak as
a real resonance. v40.45 shows that this assumption alone creates the
deep-collapse discrepancy, while any reasonable variation (including
removing the peak) restores agreement with observed dwarf cores.
Unless independent confirmation of a ~30 km/s dark-QCD resonance
emerges, the framework should reconsider or downgrade the peak's
status--preferably treating it as a phenomenological nuisance
parameter that can be set to zero, thereby alleviating the c-M
tension without invoking new baryonic physics.
"""

if __name__ == "__main__":
    print(NEMOTRON_REVIEW)
