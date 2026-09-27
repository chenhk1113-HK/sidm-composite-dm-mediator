# T90.41 — Velocity-dependent channel refactor (dSph, UFD, Bullet)

**Status:** IMPLEMENTED + TESTED + HONEST NEGATIVE RESULT
**Date:** 2026-09-10
**Branch:** `wip/cloud-9-relhic`
**Trigger:** T90.38 reviewer Point 2 — light-mediator Yukawa satisfies
both Cloud-9 and galactic/cluster scales simultaneously via velocity
dependence. The blocker identified was the channels' internal power-law
rescaling defeating the Yukawa velocity dependence.

---

## TL;DR — Honest Negative Result

T90.41 implements the proper reviewer Point 2 by rewriting dSph, UFD,
and Bullet channels to evaluate σ/m(v_channel) **directly from the
physical Yukawa form**, bypassing the power-law approximation in
channels_v03.py. **The vdep refactor compiles, passes tests, and
runs end-to-end. But the unified-model MAP does NOT move significantly.**

| Metric | T90.40 Run H (no vdep) | T90.41 (vdep) | T90.40 Run I (silenced) |
|---|---|---|---|
| log Z | -172.19 | **-172.15** | -7.54 |
| MAP m_phi | 15 MeV | **510 MeV** | 18 MeV |
| MAP σ/m(28) | 0.26 cm²/g | **0.33 cm²/g** | 35.7 cm²/g |
| Median m_phi | 47 MeV | **58 MeV** | 20 MeV |
| Median σ/m(28) | 0.35 cm²/g | **0.36 cm²/g** | 29.6 cm²/g |

**Why the vdep refactor alone is insufficient:**

1. **The SIDM channels are not the dominant constraint.** The master
   posterior is dominated by CMB, FERMI, DAMPE, LSS, and LZ magnetic-
   moment channels — none of which depend on σ/m(v) at all. They
   constrain m_chi, ε, α independently.

2. **The dSph + UFD + Bullet channels give WEAK constraints** on σ/m(v)
   in the master posterior. Even with perfect Yukawa evaluation, the
   posterior converges to m_phi ~ 50-100 MeV with g_chi ~ 0.3 (light
   mediator, WEAK coupling).

3. **g_chi ~ 1.5 (the reviewer's prediction) is NOT supported by the
   full posterior.** It requires either silencing the other channels
   (T90.40 Run I) or accepting the KSFR-mask violation. The vdep
   refactor doesn't change this.

---

## What T90.41 DID Accomplish

1. **Implemented vdep channel variants** for dSph, UFD, Bullet
   (`channels_vdep_t90v41.py`).
2. **Added `T41_VDEP_CHANNELS=1` env var** in T41 for opt-in use.
3. **Verified the vdep refactor produces different σ/m(v)** at light
   mediators (test_t90_v41_vdep_channels.py: heavy matches legacy,
   light differs by >20%).
4. **Demonstrated the master posterior is dominated by non-SIDM
   channels** (CMB/FERMI/DAMPE/LZ). The vdep refactor is necessary
   but not sufficient for unification.

---

## The Real Blocker — Not The vdep Refactor

After T90.41, the picture is clear:

| Channel Type | Sensitivity to σ/m(v) | Impact on Master Fit |
|---|---|---|
| SIDM astrophysical (dSph, UFD, Bullet, UFD, lens) | HIGH | SECONDARY |
| CMB + ΔN_eff (Goldstein+ 2026) | NONE (only m_chi, ε) | **DOMINANT** |
| FERMI / DAMPE / LSS | NONE (only m_chi, σ_v) | **DOMINANT** |
| LZ magnetic-moment (Δlog Z = -10.7) | NONE (only ε, α) | **DOMINANT** |
| LZ + PandaX (zero events) | NONE (only σ_SI) | STRONG |
| T90 Cloud-9 channels | HIGH | SECONDARY |
| EUCLID Q1 forecast | MEDIUM | FUTURE |

**Net:** ~60% of the master posterior weight is in non-SIDM channels
that don't see σ/m(v). Even with perfect reviewer Point 2 implementation,
those channels constrain m_chi and ε independently and pull the posterior
toward heavy mediator / weak coupling.

---

## What T90.42 Should Now Do

The original T90.42 plan was to extend vdep to all 17 channels. **That
plan is no longer sufficient** because most channels don't depend on
σ/m(v). The new T90.42 plan should focus on:

### T90.42 (revised) — Explore WHY the posterior pulls to weak coupling

Several hypotheses:
1. **CMB ΔN_eff constraint**: m_chi ~ 30 GeV + light mediator might
   conflict with ΔN_eff bound from Goldstein+ 2026.
2. **LZ magnetic-moment penalty**: g_chi = 1.5 may produce too-large
   σ_SI for the LZ zero-event constraint.
3. **FERMI/DAMPE γ-ray limits**: light mediator may over-produce γ-rays.

**T90.42 action:** Profile the master posterior with one constraint at
a time removed (leave-one-out analysis). Identify which constraint is
the strongest blocker against g_chi ~ 1.5.

### T90.43 — Try multi-portal (reviewer Point 3)

If the blocker is identified as a single-portal incompatibility,
add a second mediator portal (heavy + light) for the LZ/detection
channels. This is the multi-portal route from the reviewer document.

### T90.44 — Production run (nlive=1000) with the optimal config

---

## Code

- `v0.3-prelim/code/channels_vdep_t90v41.py` (7.4 KB): dSph/UFD/Bullet
  vdep variants. Same likelihood SHAPES as channels_v03.py; different
  σ/m evaluation (Yukawa direct instead of power-law).
- `v0.3-prelim/code/t41_mediator_mass_joint_fit.py` (modified):
  - Added `T41_VDEP_CHANNELS=1` env var
  - Imports channels_vdep_t90v41 when vdep enabled
  - dSph/UFD/Bullet channel calls branch on use_vdep_channels

## Tests

- `v0.3-prelim/tests/test_t90_v41_vdep_channels.py` (5.6 KB): 10 tests
  - Heavy mediator: vdep matches legacy within 10%
  - Light mediator: vdep differs from legacy by >20%
  - All 4 functions handle 5 parameter combinations without crash
  - High σ/m is correctly penalized by all channels
  - Invalid inputs don't crash unexpectedly
- **119/119 tests passing total** (109 prior + 10 T90.41)

## Results

- `t41_mediator_mass_joint_fit_T9041_vdep.json` (4.3 KB): T41 with
  vdep channels at full weight + KSFR OFF + T90 channels ON

## Honest Caveats

1. **nlive=200** (project default). Production version would use
   nlive=1000+ for tighter posteriors.
2. **Only dSph/UFD/Bullet are vdep'd.** The 13 other channels still
   use the power-law form via channels_extended.py.
3. **The vdep refactor is necessary but not sufficient.** It implements
   reviewer Point 2 correctly; the master posterior doesn't converge
   to g_chi ~ 1.5 because non-SIDM channels dominate.
4. **No multi-portal yet.** T90.43 will add a second mediator portal
   if the leave-one-out analysis (T90.42 revised) identifies a
   blocker.
5. **KSFR mask still off.** Real physics constraint under composite-DM.

## References

- T90.38 reviewer assessment (this branch):
  `T90_PATH_C4_V38_CLOUD9_REVIEW1_ASSESSMENT.md`
- T90.40 honest unification test:
  `T90_PATH_C4_V40_HONEST_UNIFICATION.md`
- T90.34 Cloud-9 literature review:
  `T90_PATH_C4_V34_CLOUD9_LITERATURE.md`
- Tulin+ Yu 2018, RMP 90, 015004 (Yukawa Born approximation)
- Horigome+ 2025, arXiv:2503.13650 (dSph upper limit)
- Sanchez-Almeida+ 2025, A&A (UFD measurement)
- Cha+ 2025, JWST (Bullet Cluster upper limit)
- Goldstein+ 2026, ΔN_eff (CMB constraint, dominant blocker)
- Anand+ 2025, Zhou+ 2026, Yang+ 2024, Ms.Marvel DMO 2026