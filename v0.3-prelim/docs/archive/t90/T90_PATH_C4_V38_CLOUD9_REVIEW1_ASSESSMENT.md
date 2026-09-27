# Review of `Cloud-9review1.docx` — Reviewer Assessment

**Status:** ASSESSMENT (not implementation)
**Date:** 2026-09-10
**Reviewer:** (uploaded as `Cloud-9review1.docx`)
**Branch:** `wip/cloud-9-relhic`

---

## TL;DR

The reviewer makes 5 main points about how to satisfy all conditions
under one unified composite-DM setting. **Most points are correct and
informative; one is now outdated (branch structure); one is partially
correct (paper numbers).** The most important insight is **Point 2**
(velocity-dependent Yukawa route), which I verified independently
against our actual Yukawa formula.

---

## Point-by-Point Assessment

### Point 1 — Branch structure (OUTDATED)

**Reviewer says:** "The new Cloud-9 work is not a separate branch.
It is a recent series of commits (T90.27–T90.33, dated 2026-09-10)
added on top of the existing experimental branch
`wip/tier3-magnetic-moment-LZ`."

**Status: INCORRECT (now fixed).** After the reviewer's document was
written, I created a new branch `wip/cloud-9-relhic` branched from
`wip/tier3-magnetic-moment-LZ` at commit `cee378a`. The Cloud-9 work
IS now on a separate branch (commit `b9480cb`). The reviewer should
be informed of this.

### Point 2 — Velocity-dependent Yukawa route (CORRECT IN PRINCIPLE)

**Reviewer says:** "Lower the mediator mass into the 1–30 MeV window.
The physical Yukawa (Tulin–Yu Born approximation) then automatically
produces σ/m(v ≈ 28 km/s) ~ 50–500 cm²/g while still giving
σ/m(v ≈ 100–200 km/s) ~ 0.1–1 cm²/g."

**Status: ARCHITECTURALLY CORRECT, VERIFIED INDEPENDENTLY.**

I tested this directly against our actual `t40_yukawa_sigma_m.sigma_m_cm2_per_g`
formula (which IS the Tulin-Yu Born approximation):

| (m_phi, m_chi, g_chi) | σ/m(28) | σ/m(100) | σ/m(200) | σ(28)/σ(100) |
|---|---|---|---|---|
| (10 MeV, 500 GeV, 0.22) | **52.5 cm²/g** | 1.3 cm²/g | 0.13 cm²/g | **40.9×** |
| (3 MeV, 500 GeV, 0.27) | **448 cm²/g** | 6.4 cm²/g | 0.57 cm²/g | **69.7×** |

**The reviewer is right**: a light mediator with moderate coupling
naturally satisfies Cloud-9 (50-500 cm²/g) AND galactic (~1 cm²/g)
AND cluster (~0.1 cm²/g) simultaneously. The strong velocity dependence
is the natural unification mechanism.

**Why my T90.30/33 work missed this:** the other 17 channels in T41
use constant-cross-section parameterizations (σ_m_0, a) that don't
"see" the velocity dependence the same way. The MCMC balances
constant-σ_m_0 channels against the velocity-dependent Yukawa, and
the constant-σ_m_0 channels dominate → posterior stays at heavy
mediator (m_phi ~ 700 MeV) where Yukawa velocity dependence is flat.

**What this means for unification:** the reviewer's Point 2 is
**architecturally correct** but **practically blocked** by the
channel parameterization mismatch. A production version would need
to convert all 17 channels to velocity-dependent SIDM evaluation.
This is significant work but the right direction.

### Point 3 — Multi-portal hierarchy (AGREED, FUTURE WORK)

**Reviewer says:** "Retain a multi-component or multi-portal hierarchy
so that the light mediator + moderate coupling supplies the
velocity-dependent SIDM needed by Cloud-9 and the astrophysical cores,
a heavier or more suppressed portal can still attempt to address the
LZ 248 keV event (either via residual magnetic moment or inelastic
scattering), kinetic mixing remains tiny (ε ≲ 10⁻³⁰–10⁻³⁷)."

**Status: STRONGLY AGREED.** This is consistent with the T99/T105
multi-portal framing already in the project. The light-mediator
Yukawa + heavier suppressed portal is the natural UV-complete
picture.

### Point 4 — Population-level RELHIC statistics (DONE in T90.32)

**Reviewer says:** "A single object (Cloud-9) is insufficient.
Adding the Monaci+ 70-candidate catalog or future FAST/SKA RELHIC
samples supplies the statistical weight needed to move the global
posterior without artificially down-weighting the other channels."

**Status: ALREADY IMPLEMENTED.** T90.32 ships the Monaci+ 2026
70-candidate population likelihood (see `t90_v32_relhic_population.py`).
However, the reviewer's caveat "without artificially down-weighting
the other channels" is important — my T90.31 implementation did
silence the other channels via `T41_CHANNEL_WEIGHT_NONRELHIC`,
which is the "artificial" down-weighting the reviewer warns against.

**The cleaner T90.38+ path** would be: use the Monaci+ population
likelihood at full weight alongside the velocity-dependent Yukawa
(Point 2) AND the constant-cross-section channels at full weight.
The MCMC should naturally find the right balance if all channels
are properly specified.

### Point 5 — UV consistency check (FUTURE WORK)

**Reviewer says:** "The same composite structure that produces the
magnetic moment (lattice form factors, T90 Path C.4 v18) and the
inelastic operators must also generate a light enough mediator.
The existing T105 scan already shows that only a narrow corner of
(m_ψ, Λ_D, α_D) parameter space simultaneously yields both portals;
extending that scan to include m_phi ~ few–30 MeV is the obvious
next step."

**Status: FUTURE WORK.** This is the right next step. The T105
parameter scan needs to be extended to m_phi ~ few–30 MeV to verify
that the composite structure can simultaneously produce:
- Light mediator (m_phi ~ 1-30 MeV) for SIDM core formation
- Magnetic-moment operator (for LZ 248 keV channel)
- Inelastic mass-splitting (for inelastic door)
- Kinetic mixing ε ≲ 10⁻³⁰–10⁻³⁷ (suppressed)

---

## Reviewer's Final Assessment (AGREED)

**Reviewer says:** "A single, fully unified composite-DM point that
simultaneously reproduces Cloud-9's high σ/m at low velocity, keeps
the galactic-scale σ/m low enough for the existing multi-channel fit,
and still produces an observable LZ magnetic-moment or inelastic rate
is possible in principle but currently sits in a tight corner of
parameter space. The light-mediator Yukawa route (point 2 above) is
the cleanest way to satisfy the astrophysical side; the LZ side
remains the harder constraint because the magnetic-moment door is
already globally disfavored (Δlog Z ≈ –10.7) and the inelastic door
only mildly preferred."

**Status: AGREED.** This matches the project's current findings.

## Reviewer's Cloud-9 Paper Number (PARTIALLY CORRECT)

**Reviewer says:** "SIDM fits (Yang+2024/2025 parametric model) at
τ ≈ 0.18 give σ/m ≈ 483 cm²/g at v₂₀₀ ≈ 28 km/s (only ~3σ low);
a deep-core-collapse solution needs even larger σ/m."

**Status: PARTIALLY CORRECT.** The σ/m = 483 cm²/g is one published
acceptable fit, but Zhou+ 2026 also states that **σ/m ≳ 50 cm²/g
brings the halo concentration within3σ of cosmological median**.
The reviewer is using the best-fit point estimate; the published
lower bound (50 cm²/g) is more permissive. Worth flagging but not
critical — the reviewer's broader point (light-mediator Yukawa can
reach the Cloud-9 regime) stands.

## Recommended Actions

1. **Inform the reviewer that the Cloud-9 work IS on a separate
   branch** (`wip/cloud-9-relhic`).
2. **T90.38**: Extend the T41 channels to use velocity-dependent
   σ/m(v) consistently. This unblocks the reviewer's Point 2 and
   allows the MCMC to find the light-mediator Yukawa solution at
   full channel weight (no silencing).
3. **T90.39**: Extend the T105 UV scan to m_phi ~ few–30 MeV per
   reviewer's Point 5.
4. **T90.40**: Re-run T41 with all channels at full weight + T90.29 v3
   + T90.32 (population) + T90.35-37 (cross-validation) + KSFR off.
   This is the "honest unification" test: does the MCMC converge
   to (m_phi ~ 1-30 MeV, g_chi ~ 1.0-1.5) without artificial
   down-weighting?

---

## Summary

The reviewer's document is **informative and largely correct**. The
most actionable insight is **Point 2** — the velocity-dependent
Yukawa form (T90.29 v3) is the natural unification mechanism that
I missed in T90.30/33 because the other channels don't evaluate
velocity-dependent σ/m(v) consistently. Implementing this would
be the next major step (T90.38+).

Branch state: `wip/cloud-9-relhic` at commit `b9480cb`. 100/100
tests passing. This review document is the next planned commit
on this branch.