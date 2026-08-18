# Drobczyk Cross-Validation — Layman Explainer

> **TL;DR.** Two independent teams built dark matter from different
> ingredients and both ended up with the same picture: dark matter is
> slightly sticky to itself (~1 cm²/g in small galaxies) and completely
> invisible to every detector on Earth. The numbers agree on the
> neighborhood, not on the exact house — **factor of ~1.5 apart, not 30%
> apart** — but the qualitative convergence is the meaningful part.

---

## The whole Drobczyk thing in plain English

Imagine you're trying to figure out what dark matter is made of. Neither
you nor anyone else has ever caught a dark matter particle in a lab. So
instead, you watch how dark matter behaves in space — especially in small
galaxies, where it bumps into *itself* and smears out a bit. The question
is: **how sticky is dark matter to itself?**

That stickiness is called **σ/m**. The σ (sigma) is how often two dark
matter particles collide when they meet. The m (mass) is how heavy each
one is. The ratio σ/m tells you **how sticky the dark matter is, per
gram of it**. Big ratio = sticky dark matter. Small ratio = slippery dark
matter.

### The puzzle this number solves

For about 20 years, astronomers have noticed that **small galaxies look
"fluffier" than they should**. The standard "cold, slippery" dark matter
predicts galaxies with sharp, dense centers. But real small galaxies have
soft, spread-out centers — like a **marshmallow instead of a marble**. The
simplest fix: **dark matter particles bounce off each other a tiny bit,
smearing themselves out**. The "right amount" of stickiness for this is
**about 1 cm²/g at small-galaxy speeds** (small galaxies are called
"dwarf galaxies" because they're tiny).

So astrophysicists have been hunting for a model that says:
**σ/m ≈ 1 cm²/g at small-galaxy speeds.**

### Two models, arrived at from different kitchens

**Drobczyk 2025** (a paper on arXiv: [2506.22997](https://arxiv.org/abs/2506.22997))
builds dark matter one way:

- Take a heavy dark matter particle (600× heavier than a proton)
- Give it a tiny "messenger particle" (15 MeV, between an electron and a
  pion) that lets two dark matter particles talk to each other
- Tune the system's resonance so the right amount of dark matter survives
  from the Big Bang
- **Result: σ/m ≈ 1 cm²/g at small-galaxy speeds ✓**

**Our model (T54)** builds dark matter another way:

- Take a composite dark matter particle (34× heavier than a proton, made of
  smaller pieces stuck together — like a proton, but in the dark sector)
- Give it a "dark rho" messenger (3.55 MeV, similar scale to Drobczyk's)
- **Result: σ/m ≈ 1.36 cm²/g at small-galaxy speeds ✓**

### The relationship in one sentence

**Both models are independent ways of saying "dark matter is a bit sticky
to itself, with a MeV-scale messenger that doesn't talk to ordinary matter
at all."**

Why is this striking? Because the two teams:

- Used **different dark matter masses** (600 vs 34 GeV — 18× different)
- Used **different messenger types** (scalar "PNGB" vs vector "dark ρ")
- Used **different relic density mechanisms** (resonant freeze-out vs
  Boltzmann suppression)
- Used **different coupling strengths** (y_χ = 0.3 vs 1.5)

And yet they **both land on roughly the same sticky-marshmallow answer**.
Two roads, same destination.

### The honest gap

| | Drobczyk | Our T54 | Ratio |
|---|---|---|---|
| σ/m at v=30 km/s (cm²/g) | 0.96 | 1.36 | **factor ~1.4** |
| DM mass (GeV) | 600 | 34.16 | 17.6× |
| Mediator mass (MeV) | 15 | 3.55 | 4.2× |
| σ_SI (direct detection) | 7×10⁻⁵¹ cm² | 2×10⁻¹⁰⁴ cm² | both ≪ ν-floor |

The "factor ~1.4" is the on-disk apples-to-apples comparison at the same
v=30 km/s (the velocity the T72 cross-validation plot places both points
at). It is **not** "within 30%" — the earlier v10 synthesis overstated
that number — but it is **the same order of magnitude**, and more
importantly:

> **Both numbers sit comfortably inside the "allowed marshmallow zone"**
> (which is roughly 0.1 to 10 cm²/g). So neither model is "wrong" — they're
> both saying the same thing in astrophysical terms, just with slightly
> different precision.

### The part that matters even more

Both models also predict the same thing about **direct detection experiments**
(the underground labs that try to catch dark matter hitting ordinary atoms):

- Drobczyk: ~7×10⁻⁵¹ cm² (well below the neutrino floor — basically invisible)
- Ours: ~2×10⁻¹⁰⁴ cm² (essentially zero)

**Both say: dark matter is invisible to every experiment we've built.**
This is actually the most important point — it tells experimentalists
*where not to look*, and it tells theorists why we need a different
approach (gravitational lensing, galaxy shapes, etc.) to test these models.

### Why this is useful

When two independent theoretical approaches converge on the same qualitative
answer, that's a **hint that the broad picture is right**, even if the
exact numbers are off by 40%. If Drobczyk's model had predicted σ/m = 100
cm²/g and ours predicted 0.01 cm²/g, we'd know one of us was wrong.
Instead, we're both saying **"a MeV-scale decoupled messenger gives the
right astrophysics"** — and that's a useful piece of evidence that this
corner of dark matter theory is worth exploring further.

---

## TL;DR for the elevator

We and Drobczyk independently built dark matter from different ingredients,
and both ended up with dark matter that's slightly sticky to itself
(σ/m ~ 1 cm²/g) and completely invisible to detectors. The agreement is
at the **"same neighborhood, not same house"** level — **factor-of-1.5,
not factor-of-1.0** — but the qualitative picture is consistent, which is
the meaningful part.

---

## Where this lives in the project

- **Source data:** `v0.3-prelim/data/results/t68_cross_validation_drobczyk.json`
- **Plot:** `outputs/Cross_Validation_T54_vs_Drobczyk_v2_2026-08-13.png`
- **Code:** `v0.3-prelim/code/t68_cross_validation_drobczyk.py`,
  `v0.3-prelim/code/t72_cross_validation_plot.py`
- **Tests:** `v0.3-prelim/tests/test_t68_cross_validation.py`
- **Synthesis (technical):** `v0.3-prelim/docs/MEDIATOR_DETECTION_SYNTHESIS_v10.md`
  (and v11/v12 cross-validation refinements)
- **Citation:** `CITATION.cff` (Drobczyk corrigendum cited as
  σ_SI = 6.7×10⁻⁵¹ cm²)
- **Reframing note:** R11 reviewer audit, finding A13 + recommendation G7
  — the original "within 30% on cross-section" framing was re-cast as
  "qualitative literature consistency" (see `docs/REVIEWER_AUDIT_R11.md`).

---

*This document is the layman-facing companion to T68. For the underlying
numbers and the technical synthesis, follow the links above.*
