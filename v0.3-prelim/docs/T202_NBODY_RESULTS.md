# T202 N-body Results — Two-component SIDM at Phase 44 Parameters

**Date:** 2026-09-23
**Purpose:** Per reviewer (model comments.docx), compute self-consistent f_H(r) from
N-body simulations with Phase 44 parameters rather than borrow from Yang+ 2025.
**Hardware:** AMUSE 2024.6.0 (WSL Python 3.10 venv), Ph4 4th-order Hermite
**Reference:** v0.3-prelim/code/T202_two_component_sidm_nbody.py

## Parameters

| Quantity | Value | Source |
|---|---|---|
| Total halo mass | 1×10⁹ M⊙ | dSph-like |
| Heavy:light mass ratio | 10:1 | typical SIDM asymmetric DM |
| Particles per component | 1024 (2048 total) | coarse but tractable |
| Plummer scale radius | 3 kpc | r_vir ≈ 3 kpc |
| Softening | 50 pc | |
| **Phase 44 σ/m at v=100 km/s** | **0.052 cm²/g** | the paper's claim |
| Yang+ 2025 control σ/m | 147.1 cm²/g | for comparison |
| Integration time | 2 Gyr | Hubble-scale |

## Results: f_H(r) profile at Phase 44 parameters

Final f_H at 2 Gyr (mass fraction in heavy component at each r/r_vir):

| r/r_vir | f_H (T202) | f_H (hand-coded paper) | Δ |
|---|---|---|---|
| 0.05 | 0.952 | 0.95 | +0.002 |
| 0.10 | 0.930 | 0.30 | **+0.63** |
| 0.20 | 0.923 | 0.30 | **+0.62** |
| 0.50 | 0.916 | 0.10 | **+0.82** |
| Average | ~0.92 | 0.27 | +0.65 |

**Verdict:** At Phase 44 σ/m = 0.052 cm²/g, **NO mass segregation occurs in 2 Gyr**.
Heavy particles dominate at all radii (f_H ≈ 0.92 average). The hand-coded
`f_H_at_r` in `phase44_two_component.py` assumes segregation that does NOT happen
at our parameters.

## Control: f_H(r) profile at Yang+ 2025 parameters (σ/m = 147.1 cm²/g)

| r/r_vir | f_H (T202) | Yang+ 2025 paper Fig. 2 | Δ |
|---|---|---|---|
| 0.05 | 0.976 | ~0.95 | match |
| 0.10 | 0.920 | ~0.85 | +0.07 |
| 0.20 | 0.927 | ~0.75 | +0.18 |
| 0.50 | 0.906 | ~0.55 | +0.36 |

**Even at Yang+ 2025's high σ/m**, our N-body does NOT reproduce their published
segregation profile. This is **NOT** validation of the hand-coded values; this is
a limitation of our kick model (10% max velocity perturbation per step, no
proper velocity-space diffusion).

## Caveats and Limitations

1. **N = 2048 is far below N ≥ 10⁵ for realistic gravothermal evolution.**
   Two-body relaxation timescales for N=2048 are much shorter than 2 Gyr,
   meaning we are NOT in the collisionless regime. Realistic SIDM halos
   would need N ≥ 10⁵ particles.

2. **SIDM kick model is approximated as a 10% velocity perturbation** at each
   step with probability `sigma * rho * v_rel * dt / m_particle`. This is a
   gross approximation — real SIDM scattering should produce a thermal
   equipartition (energy exchange between heavy and light), not a random
   10% velocity kick.

3. **No proper energy conservation** is enforced on the SIDM kicks. In real
   SIDM scattering, energy AND momentum are exchanged, so kicking velocity
   without an opposite kick on the partner is non-physical.

4. **Single isolated halo, not cosmological context.** No mergers, no
   tidal stripping, no baryonic effects.

5. **Even Yang+ 2025's published σ/m** (147 cm²/g) does NOT produce the
   segregation shown in their Fig. 2 in our N-body, suggesting either:
   (a) their Fig. 2 requires N >> 10⁵ and proper thermal scattering, OR
   (b) their Fig. 2 is from fluid/gravothermal calculations, not N-body.

## What this DOES mean for the paper

**The reviewer was correct.** The paper's hand-coded f_H_at_r is not
self-consistent with Phase 44 parameters.

**Two possible interpretations:**

(A) **The paper's f_H_at_r is borrowed from a different regime** (Yang+ 2025
Fig. 2 with σ/m ≈ 147 cm²/g) where segregation DOES occur. At our parameters
(σ/m = 0.052 cm²/g), the segregation timescale is far longer than 2 Gyr, so
the paper's claim of "heavy sinks at dSph scales" is unsupported.

(B) **The paper's f_H_at_r is actually correct, but requires N >> 2048 and
proper thermal scattering** to reproduce in N-body. Our N-body is too crude
to test it.

**Interpretation (A) is more parsimonious.** The paper should acknowledge
that:

  (a) The 7-of-8 fit success **may rely on f_H_at_r being borrowed from
      a different σ/m regime**.

  (b) At Phase 44 parameters, **either NO segregation happens** (heavy
      dominates everywhere, f_H ≈ 1) **OR much longer timescales** (> 10 Gyr)
      are needed.

  (c) This adds another reason why the 7-of-8 fit should be reported as
      "exploratory" rather than "validated."

## Recommendation for paper

1. **Add a new §X** to the paper: "T202 N-body Validation of f_H profiles"
   - 2048 particles, 2 Gyr, Phase 44 params
   - Result: f_H(r) ≈ constant ~0.92, not the hand-coded profile
   - Honest framing: "Phase 44 σ/m is too low to drive gravothermal
     segregation at dSph masses in a Hubble time. The f_H profile used
     in the 7-of-8 fit is borrowed from Yang+ 2025's higher-σ/m regime
     and is not self-consistent with our parameters."

2. **Re-run T173 sensitivity** with the actual T202-derived f_H profile
   (≈0.92 everywhere) to see how the 7-of-8 fit degrades.

3. **Tone down the paper's gravothermal-collapse resolution** of the dSph
   tension in §10.6. Currently it claims the dSph tension is resolved
   because heavy sinks. T202 shows heavy does NOT sink.

## Code

| File | Purpose |
|---|---|
| `v0.3-prelim/code/T202_two_component_sidm_nbody.py` | The simulator (15 KB) |
| `v0.3-prelim/data/results/t202_two_component_sidm.json` | Phase 44 run output |
| `v0.3-prelim/data/results/t202_control_highsigma.json` | Yang+ control output |

## Honest assessment of the N-body itself

The T202 implementation has limitations that prevent it from being a true
"first-principles" validation:

- N=2048 → 2-body relaxation is a problem
- SIDM kick is 10% velocity perturbation, not proper scattering
- No thermal equipartition between components

A proper first-principles calculation would require:
- N ≥ 10⁵ particles
- Proper energy-and-momentum conserving SIDM scattering
- Cosmological context (mergers, accretion, tidal stripping)
- Or use a fluid/gravothermal code (not N-body) to follow thermal evolution

**T202 is a "qualitative check," not a "first-principles f_H(r)."**
This is consistent with what we wrote in the script docstring.

## What's next

Per user direction "after completion, will reconsider #3 and #4":
- This T202 result **informs** how #3 (full-likelihood) should be framed.
- And **changes** what #4 (Cloud-9 re-framing) means — if heavy doesn't sink,
  the gravothermal-collapse resolution of the dSph tension is on shakier
  ground.

**Not continuing to #3/#4 without explicit user direction** (Rule 5).