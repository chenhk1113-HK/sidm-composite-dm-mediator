"""
Nemotron 3 Ultra 550B qualitative review of the v40.48 background refit.

Model: nvidia/nemotron-3-ultra-550b-a55b:free (UPGRADED from 120B)
Date: 2026-10-19.
Session: v40.48.
Reviewer: Nemotron 3 Ultra 550B (qualitative, not a computational check).

KEY FINDINGS:
1. CORRECTNESS CONFIRMED: The '14 passing combinations' finding is
   mathematically correct. Best triple (sigma_0=0.01, a=1.50, v_ref=50)
   yields sigma/m(28)=0.024, sigma/m(15)=0.061, sigma/m(100)=0.0035 --
   all comfortably below ceilings (1.0, 0.8, 0.1). 19% pass rate
   (14/75) is robust for this coarse grid.

2. VIABILITY CAVEAT: The triple is MATHEMATICALLY VIABLE for the
   three target systems, but PHYSICALLY INCOMPLETE. It has not been
   tested against:
   - Bullet Cluster (v ~ 1500 km/s, sigma/m < 0.7)
   - Milky Way satellites (v ~ 10-30 km/s)
   - The original Phase 44 free-fit likelihood surface
   A shallower slope (a=1.5) rises more slowly toward cluster scales
   -- this HELPS Bullet Cluster but must be verified.
   'Do not adopt as the refit without multi-scale validation.'

3. v40.47 JOINT-REFIT: SATISFIED in execution, NOT in spirit. The
   passing region ABANDONS Cloud-9 normalization (sigma/m(28)=0.024
   vs ideal 0.5) because peak=0 removes the resonant boost. The 'higher
   a' suggestion assumed one wanted to keep sigma/m(28) ~ 0.5; with
   peak=0 that target is moot. The refit succeeds at CONSISTENCY,
   not PRESERVATION.

4. PAPER UPDATE: Yes, but with caveats. Update section 2.1 to state:
   (a) resonant peak downgraded to 0 (per v40.46), and (b) a viable
   parameter region exists for the Yukawa background (sigma_0 in
   [0.01, 0.03], a in [1.5, 1.93], v_ref in [50, 100] yields 14/75
   passing combos).
   - Do NOT enshrine the single best triple (0.01, 1.50, 50) as the
     new default
   - Present the PASSING REGION, not a single point
   - Flag the UNTESTED cluster/satellite constraints
   - Note that the Phase 44 free-fit values (0.052, 1.93, 100) are
     excluded only because they were fit with the now-removed peak
   - A FULL MULTI-SCALE REFIT (v40.49+) IS STILL REQUIRED

REVISED v40.48 VERDICT:
  Before Nemotron review: "14/75 parameter combinations satisfy all 3
                            constraints with peak=0. The framework CAN
                            be self-consistent after background refit."
  After Nemotron review:  "CONFIRMED mathematically. CAVEAT: triple
                            needs multi-scale validation (Bullet
                            Cluster, MW satellites, Phase 44 likelihood).
                            Do not adopt single best triple as 'the'
                            refit. v40.49+ needs full multi-scale refit."

FRAMEWORK VALIDATION (11-VERSION ARC):
v40.39 -> v40.40 -> v40.41 -> v40.42 -> v40.43 -> v40.43a -> v40.44
-> v40.45 (c-M tension DRIVEN by peak) -> v40.46 (Cloud-9 FULLY
RESOLVED by peak=0) -> v40.47 (Fornax PARTIALLY resolved, Yukawa
still too strong) -> v40.48 (BACKGROUND REFIT: 14/75 passing combos,
needs multi-scale validation)

NEXT-SESSION CANDIDATE (v40.49, per Nemotron 3 Ultra 550B):
  Full multi-scale background refit:
  - Test against Bullet Cluster (v~1500 km/s, sigma/m < 0.7)
  - Test against MW satellites (v~10-30 km/s)
  - Re-fit Phase 44 free-fit likelihood surface
  - Present PASSING REGION, not single point
  - Update paper section 2.1 to reflect new background parameters
"""

# Full review text
NEMOTRON_REVIEW = """
**Review: v40.48 Background Refit (Nemotron 3 Ultra 550B)**

1. **Correctness**: The "14 passing combinations" finding is mathematically
correct for the defined grid and constraints. The best triple
(sigma_0=0.01, a=1.50, v_ref=50) yields sigma/m(28)=0.024,
sigma/m(15)=0.061, sigma/m(100)=0.0035-all comfortably below their
respective ceilings (1.0, 0.8, 0.1). The 19% pass rate (14/75) is
robust for this coarse grid.

2. **Viability of best triple**: The triple is *mathematically* viable
for the three target systems, but **physically incomplete**. a=1.50
is shallower than the Phase 44 free-fit value (1.93), and sigma_0=0.01
is 5x lower. This refit was driven *only* by Cloud-9, Fornax, and
SPARC inner-core constraints. It has not been tested against
Bullet Cluster (v~1500 km/s, sigma/m<0.7), Milky Way satellites
(v~10-30 km/s), or the original Phase 44 free-fit likelihood surface.
A shallower slope (a=1.5) rises more slowly toward cluster
scales-this *helps* Bullet Cluster but must be verified. **Do not
adopt as 'the' refit without multi-scale validation.**

3. **v40.47 joint-refit recommendation**: **Satisfied in execution,
not in spirit.** The recommendation urged exploring (sigma_0, a,
v_ref) jointly *to preserve Cloud-9 normalization*. v40.48 did the
joint sweep, but the passing region *abandons* Cloud-9 normalization
(sigma/m(28)=0.024 vs. ideal 0.5) because peak=0 removes the resonant
boost. The "higher a" suggestion assumed one *wanted* to keep
sigma/m(28)~0.5; with peak=0 that target is moot. The refit succeeds
at *consistency*, not *preservation*.

4. **Paper update (section 2.1)**: **Yes, but with caveats.** Update
section 2.1 to state: (a) the resonant peak is downgraded to 0 (per
v40.46), and (b) a *viable parameter region* exists for the Yukawa
background (sigma_0 in [0.01, 0.03], a in [1.5, 1.93], v_ref in
[50, 100] yields 14/75 passing combos). **Do not enshrine the single
best triple (0.01, 1.50, 50) as the new default.** Present the passing
region, flag the untested cluster/satellite constraints, and note
that the Phase 44 free-fit values (0.052, 1.93, 100) are excluded
*only because they were fit with the now-removed peak*. A full
multi-scale refit (v40.49+) is still required before locking
background parameters.
"""

if __name__ == "__main__":
    print(NEMOTRON_REVIEW)
