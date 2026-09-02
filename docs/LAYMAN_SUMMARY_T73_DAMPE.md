# Layman Summary — T73 DAMPE Joint-Fit Integration (v0.4-prelim)

> **For:** Non-experts + users preferring quick summaries over technical detail.
> **Companion:** [T73 technical doc](T73_DAMPE_V04_INTEGRATION.md) for the full
> method, references, and tests.
> **Date:** 2026-09-02.

## What this is, in one sentence

We added the DAMPE cosmic-ray electron+positron spectrum (a Nature-2017
measurement) as **Channel 17** in our 17-channel joint fit, with a
**dark-matter forward model** that predicts what χχ → A' → e⁺e⁻
annihilation would look like in DAMPE's data — and confirmed our
posterior predicts a signal that is **too small to detect** (null
result, as expected).

## Why this matters

The project makes claims about a specific dark-matter model — a
composite dark sector where dark matter particles interact with each
other (self-interacting, or SIDM) via a secluded dark photon mediator.
If this model is real, dark matter particles should annihilate in our
Galaxy and produce a flux of high-energy electrons and positrons that
space telescopes like DAMPE could detect.

**Before T73:** we could only constrain the model via gamma-ray
telescopes (Fermi dwarfs) — a different annihilation channel.

**After T73:** we have **two independent indirect-detection channels**
(Fermi γ + DAMPE e⁺e⁻) cross-checking each other. Two is better than
one because:
  - If both agree → strong evidence
  - If they disagree → either new physics or a bug in one of the
    pipelines

For our model, both agree: **data don't show a sharp feature**. The
smooth broken-power-law spectrum DAMPE measured is consistent with
astrophysical backgrounds (pulsars + supernova remnants), with our
model contributing only ~10⁻⁵ of the observed flux at the dark-matter
mass scale. Too small to detect.

## What this does NOT do (honest caveats)

| Claim | Does T73 affect this? |
|---|---|
| Headline σ/m = 1.4–1.7 cm²/g | ❌ No (DAMPE constrains annihilation, not self-scattering) |
| Velocity-slope tension (1.3σ) | ❌ No (DAMPE is velocity-integrated) |
| T41 posterior (m_χ~800 GeV, m_A'~553 MeV) | ❌ No (ΔlogL = -19.7, subdominant to dSph/UFD/Bullet/LZ) |
| m_χ uncertainty | ⚠️ Subdominant penalty, but doesn't shift MAP |
| Two-component Bayes factor (+0.39) | ❌ No (DAMPE doesn't distinguish species) |

T73 is a **defensive addition** — it adds information that could rule
out the model if DAMPE showed a feature inconsistent with our
posterior. Since DAMPE doesn't show such a feature, our model survives
the test. The test is now in the test suite permanently.

## What's the next step?

The T74 ship in the same session adds the **Zhang 2025 large-scale
structure** channel — a Nature-accepted paper that constrains the SIDM
**core-size** directly. Combined with DAMPE (which constrains
annihilation), the project will have constraints on **two of the three
fundamental SIDM observables**: self-scattering cross-section (σ/m,
already constrained by T9/T13/T21/T39), annihilation cross-section
(σv, now constrained by DAMPE T73 + Fermi T31), and core-size (r_c,
about to be constrained by Zhang 2025 T74).

After T74 lands, the project's sigma/m claim goes from "constrained by
8 galaxy-clustering probes" to "constrained by 9 probes including a
Nature-accepted LSS measurement."

## How long did this take?

- **Reading + planning:** ~30 min (Cholis 2009 propagation formalism
  + DAMPE Table 1 + project posterior)
- **Forward-model implementation:** ~45 min (3 attempts at the
  propagation formula + numpy 2.x fix)
- **Channel wiring into T41:** ~15 min (1 bug: duplicate
  `if __name__` block from my first patch)
- **Tests + docs:** ~30 min
- **Total:** ~2 hours wall, 1 commit, 8 files, 1192 insertions,
  19 new tests.

## The single most important result

> **The project's posterior predicts a DAMPE signal that is ~10⁻⁵ of
> the observed flux — too small to detect. The DAMPE data are
> consistent with both our model and the standard astrophysical
> background. The model survives a new independent observational test.**

This is the same verdict we got from every other test we've added:
**the model is consistent with all available data**, **the headline
σ/m is unchanged**, and **the standing version (v0.3-prelim+T71.7) is
preserved** because T73 is a Tier-2 POC extension, not a major version
bump.

The defensive value is real: if a future experiment sees a sharp
e⁺e⁻ feature at ~800 GeV, the project can immediately test whether
our model fits it. The infrastructure (forward model + likelihood +
joint-fit wiring + tests) is now permanently in place.