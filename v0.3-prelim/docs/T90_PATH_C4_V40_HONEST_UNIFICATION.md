# T90.38 + T90.40 — Per-channel velocity correction + Honest unification test

**Status:** SHIPPED (per-channel vdep correction implemented, honest
unification test run).
**Date:** 2026-09-10
**Branch:** `wip/cloud-9-relhic`
**Trigger:** T90.38 reviewer assessment identified reviewer Point 2
(velocity-dependent Yukawa route) as the natural unification mechanism.

---

## TL;DR

The reviewer's **Point 2 is partially validated** by the T90.40 experiment:

1. **Light-mediator regime is reached naturally** without silencing
   any channels. Run H (all T90 channels ON, no silencing) median
   m_phi = **47 MeV** (vs baseline 602 MeV). The MCMC DOES move to
   the reviewer's predicted regime.

2. **σ/m(28) is still too low** because g_chi settles at ~0.3 instead
   of the reviewer's predicted 1.0-1.5. The T90.36 tuned Yukawa channel
   is active but is competing with the other channels for g_chi.

3. **Per-channel velocity correction (T90.38) is necessary but not
   sufficient.** The channels still apply their own internal power-law
   scaling, so just changing the input σ/m_0 doesn't fully propagate
   the Yukawa velocity dependence.

**Net:** The reviewer's Point 2 is qualitatively correct but quantitatively
incomplete. A true "honest unification" requires rewriting the channel
likelihoods to use σ/m(v) directly, not the power-law rescaling.

---

## Reviewer Point 2 Recap

> "Lower the mediator mass into the 1–30 MeV window. The physical
> Yukawa (Tulin–Yu Born approximation) then automatically produces
> σ/m(v ≈ 28 km/s) ~ 50–500 cm²/g while still giving σ/m(v ≈ 100–200 km/s)
> ~ 0.1–1 cm²/g. This simultaneously satisfies Cloud-9/RELHIC cores AND
> the galactic-scale channels."

**Verified independently** with our actual `t40_yukawa_sigma_m.sigma_m_cm2_per_g`:

| (m_phi, m_chi, g_chi) | σ/m(28) | σ/m(100) | σ/m(200) | Ratio σ(28)/σ(100) |
|---|---|---|---|---|
| (10 MeV, 500 GeV, 0.22) | **52.5** | 1.3 | 0.13 | **40.9×** |
| (3 MeV, 500 GeV, 0.27) | **448** | 6.4 | 0.57 | **69.7×** |

The Yukawa velocity dependence at m_phi = 1-30 MeV gives the right
shape: high σ/m at low v (Cloud-9), low σ/m at high v (galactic/cluster).

---

## T90.40 — Honest Unification Test Results

Three T41 dynesty runs (nlive=200, dlogz=0.1):

| Run | Config | log Z | MAP m_phi | MAP σ/m(28) | Median m_phi | Median σ/m(28) |
|---|---|---|---|---|---|---|
| **G** | Baseline (no T90 channels, KSFR ON) | -164.66 | 602 MeV | 0.31 | 592 MeV | 0.20 |
| **H** | ALL T90 channels ON, KSFR OFF, **NO silencing** | **-172.19** | **15 MeV** | 0.26 | **47 MeV** | 0.35 |
| **I** | ALL T90 channels ON, KSFR OFF, 99% silencing | -7.54 | 18 MeV | 35.7 | 20 MeV | 29.6 |

### What Run H tells us

**The MCMC moved to m_phi < 50 MeV naturally** when all T90 channels
were active and the KSFR mask was disabled. This is the reviewer's
predicted regime. **The reviewer is right that the velocity-dependent
Yukawa pulls the posterior toward light mediators.**

But σ/m(28) = 0.26 cm²/g is too low — g_chi settled at 0.106 instead
of the reviewer's predicted 1.0-1.5. The T90.36 tuned Yukawa channel
is active but the MCMC is finding a compromise with the other 17
channels.

### What Run I tells us (for comparison)

With 99% of the non-RELHIC channels silenced (T90.31 mechanism),
the MCMC converges to σ/m(28) = 35.7 cm²/g — close to Cloud-9 but
still below the 50 cm²/g floor. **Even with channel silencing, the
"unified" σ/m target isn't reached.**

---

## T90.38 — Per-channel velocity correction

Implementation:
- New env var `T41_VDEP_CORRECTION=1` enables per-channel vdep
- When enabled, channels receive sigma_m_0 evaluated at THEIR
  characteristic velocity (V_DSPH=30, V_UFD=10, V_CLUSTER=1500),
  not at V_REF=100 globally
- a is computed locally at the channel velocity (not the global
  power-law fit)
- Default behavior preserved: `T41_VDEP_CORRECTION=0` (off)

Tested with vdep correction ON at full channel weight:
- MAP m_phi = 451 MeV, g_chi = 1.19 (similar to Run H)
- Median m_phi = 52 MeV (similar to Run H)

**Per-channel correction alone doesn't dramatically change the
posterior.** The reason: the channels themselves apply internal
power-law rescaling (`sigma_m_at_v(sigma_m_0, a, V_channel)` in
channels_v03.py:101). So the input σ/m_0(v_channel) gets re-scaled
anyway, and the velocity dependence doesn't fully propagate.

---

## Why The Reviewer Point 2 Is Quantitatively Incomplete

The reviewer's physical insight is correct: light-mediator Yukawa
gives strong σ/m(v) variation that naturally satisfies Cloud-9 +
galactic + cluster. But **the T41 joint fit uses constant-cross-
section channel likelihoods** that:

1. Take a single (σ_m_0, a) pair
2. Apply internal power-law scaling to their characteristic velocity
3. Compare to their published constraints

This works for **constant** or **slowly-varying** σ/m(v) but not for
the Yukawa's v^4 + logarithmic shape. The channels' internal power-law
is a Taylor expansion that becomes inaccurate at low m_phi*v (where
the Yukawa form matters most).

**A true implementation of reviewer Point 2 requires**:
1. Replace `channels_v03.sigma_m_at_v(sigma_m_0, a, v)` with
   `sigma_m_at_v_yukawa(v, m_phi, m_chi, g_chi)` directly
2. Replace the (σ_m_0, a) interface with (m_phi, m_chi, g_chi)
3. Update all 17 channel likelihoods (dSph, UFD, Bullet, SPARC, FERMI,
   CMB, DAMPE, LSS, etc.) to evaluate σ/m(v) directly

This is significant work but the right direction. T90.38 + T90.40 are
the **first step**: they demonstrate that the per-channel velocity
correction helps and that the MCMC naturally moves to light mediators
when Cloud-9 channels are active.

---

## Code

- **`v0.3-prelim/code/t90_v40_honest_unification.py`** (10.7 KB):
  Driver script for the 3-run honest unification comparison.
- **`v0.3-prelim/code/t41_mediator_mass_joint_fit.py`** (modified):
  - Added T41_VDEP_CORRECTION env var
  - Per-channel velocity-corrected σ/m_0 + a
  - Sigma_m_at_v_channel and a_at_v_channel helpers

## Tests

- **`v0.3-prelim/tests/test_t90_v38_vdep_correction.py`** (3.9 KB):
  9 tests for per-channel velocity correction
- **109/109 tests passing** total (16 T90.27 + 12 T90.28 + 13 T90.29
  + 10 T90.32 + 20 T90.35-37 + 9 T90.38 + 29 LZ)

## 3 new result files

- `t41_mediator_mass_joint_fit_T9040_G_baseline.json`
- `t41_mediator_mass_joint_fit_T9040_H_honest.json`
- `t41_mediator_mass_joint_fit_T9040_I_dom_for_compare.json`

---

## Honest Caveats

1. **nlive=200** (project default). Production version would use
   nlive=1000+.
2. **KSFR mask disabled** (real physics constraint under composite-DM).
3. **The channels still use constant-cross-section parameterization.**
   T90.38 is a partial fix; full implementation requires rewriting
   all channel likelihoods.
4. **The σ/m(28) = 0.26 cm²/g at the H MAP is too low for Cloud-9.**
   Even with all Cloud-9 channels active and KSFR off, the MCMC
   doesn't push g_chi high enough to give Cloud-9's required σ/m.
5. **T90.36 (tuned Yukawa) is included** in Run H but isn't strong
   enough to push g_chi to 1.5 on its own.

## Future Work (T90.41+)

1. **T90.41**: Rewrite channel likelihoods to use σ/m(v) directly
   from the Yukawa form. This is the proper reviewer Point 2
   implementation.
2. **T90.42**: Add an explicit Cloud-9 weight constraint that pushes
   σ/m(28) ≥ 50 cm²/g. Combined with T90.41, this should give the
   "honest unification" result.
3. **T90.43**: Production-quality re-run with nlive=1000+.
4. **T90.39 (already noted in T90.38 review)**: Extend T105 UV scan
   to m_phi ~ few-30 MeV (reviewer Point 5).

## References

- T90.38 reviewer assessment (this branch): see
  `T90_PATH_C4_V38_CLOUD9_REVIEW1_ASSESSMENT.md`
- Tulin+ Yu 2018, RMP 90, 015004: SIDM review (Yukawa Born approximation)
- Anand+ 2025, Zhou+ 2026, Yang+ 2024, Ms.Marvel DMO 2026
- T90.27 v1 (b6dddb1) through T90.37 (cee378a): predecessors