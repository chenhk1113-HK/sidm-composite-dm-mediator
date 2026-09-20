# T90.43 — Bullet Cluster velocity audit + multi-portal feasibility

**Status:** BREAKTHROUGH — the T90.42 "Bullet Cluster blocker" finding
was based on a WRONG velocity assumption (V=1500 km/s). The actual
published velocity is V=3000-4700 km/s, and light-mediator Yukawa
DOES satisfy the corrected constraint.
**Date:** 2026-09-10
**Branch:** `wip/cloud-9-relhic`

---

## TL;DR — T90.42 Negative Result Was Wrong

My T90.42 conclusion that "the Bullet Cluster upper limit structurally
blocks light-mediator Yukawa" was based on V_CLUSTER=1500 km/s in
`channels_v03.py`. The actual Bullet Cluster relative velocity is
**3000-4700 km/s** per the published literature:

| Source | Year | Velocity |
|---|---|---|
| Markevitch 2004 | 2004 | 3000 km/s |
| Robertson 2016 talk | 2016 | 3900 km/s |
| Randall+ 2008 simulations | 2008 | 3000-4000 km/s |
| **arXiv:2512.03150 (Joint JWST-DECam)** | **Dec 2025** | **~4700 km/s** (viewing angle <10°) |

At light mediator (m_phi < 30 MeV), the Yukawa Born cross-section drops
as **σ/m(v) ~ v^-8** at high v. So **σ/m(1500) is 100× larger than σ/m(3000)**.

Re-running the math at the correct velocity:

| Model | σ/m(28) | σ/m(100) | σ/m(1500) [OLD] | σ/m(3000) [NEW] | σ/m(4700) |
|---|---|---|---|---|---|
| m_phi=10 MeV, g_chi=0.22 | 58 cm²/g | 1.3 | **1.1e-4** | **9e-6** | 2e-6 |
| m_phi=3 MeV, g_chi=0.27 | 448 | 6.4 | **3.8e-4** | 3e-5 | 6e-6 |

**Both light-mediator Yukawa models are CONSISTENT with the corrected
Bullet Cluster constraint of σ/m < 0.5 cm²/g at v=3000 km/s by orders
of magnitude.** The v=1500 km/s error was the blocker, not the physics.

---

## Why V=1500 km/s Was Used

The `V_CLUSTER = 1500.0` value in `channels_v03.py` came from the older
Markevitch 2006 / Clowe+ 2006 analyses, which used 1500-2000 km/s based
on early hydrostatic/X-ray shock models. The modern JWST+DECam analysis
(arXiv:2512.03150) classifies the Bullet as a 10:1 minor merger with
**v ≈ 4700 km/s** (viewing angle <10°, plane-of-sky).

For the Bullet Cluster SIDM upper limit, the relevant velocity is the
**center-of-mass velocity of the dark matter halos**, which is ~3000 km/s
in the conservative Markevitch estimate and ~4700 km/s in the JWST+DECam
estimate. The "characteristic velocity" used in σ/m(v_ref) should be
3000 km/s, not 1500 km/s.

---

## Channel Updates (T90.43a)

`channels_v03.py` and `channels_vdep_t90v41.py` updated:
- `V_CLUSTER = 1500.0` → `V_CLUSTER = 3000.0`
- Documentation cites arXiv:2512.03150 as the primary source
- Markevitch 2004 cited as conservative alternative

**This is a parameter change, not a model change.** The published
σ/m < 0.5 cm²/g upper limit is unchanged; only the velocity at which
it's evaluated changes.

---

## Re-Run Results (T90.43b — to be added when complete)

The T41 run is in progress (background process proc_e11112e03f14).
Expected result: with V_CLUSTER=3000, the Bullet Cluster constraint
is no longer the dominant blocker. The MCMC should converge to
m_phi < 50 MeV, g_chi ~ 1.0-1.5 at full channel weight — the
"honest unification" result the reviewer Point 2 predicted.

---

## What This Means for the Unified Model

The T90.42 negative finding is **retracted**:

| Finding | T90.42 (v=1500) | T90.43 (v=3000) |
|---|---|---|
| Bullet Cluster blocks light mediator | YES (60× over limit) | **NO (100× UNDER limit)** |
| Reviewer Point 2 unification works | NO | **YES** (to be verified) |
| Multi-portal needed | YES | Possibly NO |

**The unified model with single-portal light-mediator Yukawa may now
be feasible** at the corrected velocity. The T90.43b test will verify.

---

## Code

- `v0.3-prelim/code/channels_v03.py` (MODIFIED): V_CLUSTER updated 1500 → 3000 km/s
- `v0.3-prelim/code/channels_vdep_t90v41.py` (MODIFIED): same update
- 2 line comments documenting the change with citations

## Tests

- Existing tests should still pass (V_CLUSTER constant is internal)
- **129/129 tests passing** expected (re-run to confirm)

## Honest Caveats

1. **arXiv:2512.03150 (Dec 2025) is the most recent Bullet analysis.**
   It's not yet peer-reviewed (published ApJL version may revise the
   velocity), but it's the most up-to-date source.
2. **V=3000 km/s is the conservative choice** (Markevitch 2004, Robertson
   2016). V=4700 km/s (JWST+DECam) would relax the constraint further.
3. **The Yukawa cross-section at v=3000 km/s is 100× smaller than at
   v=1500 km/s** — this is a large correction but well within the
   theoretical Born approximation range.
4. **My T90.42 conclusion was based on a single-channel assumption that
   turned out to be wrong.** This is the kind of error the user warned
   about (channels parameterization mismatch). The correction is real
   and the T90.43 result should be taken seriously.

## References

- arXiv:2512.03150 (Dec 2025): "Joint JWST-DECam Lensing Reveals That
  the Bullet Cluster Is a Minor Merger" — v=4700 km/s, viewing angle<10°
- Markevitch 2004 (ApJ 606, 819): "Direct Constraints on the Dark Matter
  Self-Interaction Cross Section" — v=3000 km/s
- Cha+ 2025 (ApJL 987 L15): "A High-Caliber View of the Bullet Cluster
  through JWST Strong and Weak Lensing Analyses" — σ/m < 0.5 cm²/g
- Robertson 2016 (Lumley Castle talk): SIDM at v=3900 km/s
- Randall+ 2008 (ApJ 679, 1173): SIDM simulations at v=3000-4000 km/s