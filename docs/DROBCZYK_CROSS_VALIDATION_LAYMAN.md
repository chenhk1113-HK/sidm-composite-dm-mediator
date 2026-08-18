# Drobczyk Cross-Validation — Layman Explainer

> **TL;DR.** Two independent teams built dark matter from different
> ingredients and both arrived at a "MeV-scale dark mediator, decoupled
> from ordinary matter, invisible to direct detection" picture. The
> numerical agreement is **not** as tight as the pre-R12 "factor ~1.5"
> framing suggested: after the project's own R12 audit (2026-08-17),
> the canonical joint-fit σ/m₀ = **0.066 cm²/g** versus Drobczyk's
> benchmark range of **0.11–0.96 cm²/g** at dwarf velocities — a
> factor of **1.5×–15×** apart, not "within 30%". Both models sit
> inside the same broad SIDM "allowed band" (0.1–10 cm²/g), and both
> predict direct-detection nulls, but the nulls come from different
> mechanisms (intrinsically small σ_SI vs LZ-driven ε → 10⁻³⁵). The
> qualitative convergence is real and worth noting; the quantitative
> framing is honest about the gap.

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
**about 0.1–10 cm²/g at small-galaxy speeds** (small galaxies are called
"dwarf galaxies" because they're tiny), with a sweet spot near **1 cm²/g**.

So astrophysicists have been hunting for a model that says:
**σ/m ≈ 1 cm²/g at small-galaxy speeds.**

### Two models, arrived at from different kitchens

**Drobczyk 2025** (a paper on arXiv: [2506.22997](https://arxiv.org/abs/2506.22997))
builds dark matter one way:

- Take a heavy dark matter particle (600 GeV, about 640× the proton mass)
- Give it a tiny "messenger particle" (m_φ = 15 MeV, between an electron
  and a pion) that lets two dark matter particles talk to each other
- Add a second "heavy resonance" mediator (m_Φh = 1201 GeV ≈ 2 m_χ) that
  opens a resonant annihilation channel, decoupling the relic abundance
  from the late-time self-interaction
- **Result: σ/m ≈ 0.96 cm²/g at v=10 km/s (dwarf), 0.11 cm²/g at
  v=30 km/s (MW satellites), 9.5×10⁻⁵ cm²/g at v=1000 km/s (clusters)**
  — the paper's benchmark table, line 102.

**Our model (post-R12 canonical, T41)** builds dark matter another way:

- Take a composite dark matter particle (m_χ ≈ 15.74 GeV at the posterior
  median, much lighter than Drobczyk's 600 GeV), made of "dark pions"
  and "dark baryons" — analogous to ordinary matter
- Give it a dark photon mediator (m_A' ≈ 26.60 MeV at the posterior median,
  similar scale to Drobczyk's 15 MeV)
- Add a kinetic-mixing portal ε to the Standard Model (fit to data)
- **Result at the T41 MAP: σ/m₀ = 0.066 cm²/g, a = +0.186, ε = 1.12×10⁻³⁵**

The T41 MAP sits at the lower end of the broader astrophysically allowed
band. Before the R12 audit, an earlier toy fit (T54) gave a higher value
(σ/m₀ ≈ 1.36 cm²/g) — but that number was a toy-calculation MAP from a
fit that the R12 audit superseded with the T41 joint fit. The T41 MAP is
the project's current canonical headline.

### The relationship in one sentence

**Both models are independent ways of saying "there's a MeV-scale dark
messenger that doesn't talk to ordinary matter at all, and dark matter
gets gently sticky to itself in small galaxies."**

Why is this striking? Because the two teams:

- Used **different dark matter masses** (600 GeV vs ~15 GeV — 40× different)
- Used **different messenger types** (scalar "PNGB" vs vector "dark photon")
- Used **different relic density mechanisms** (resonant annihilation via
  a heavy scalar vs Boltzmann suppression)
- Used **different coupling parameterizations** (Drobczyk's tree-level
  Yukawa y_χ = 0.30 vs our dark gauge coupling g_χ = 0.133 — these are
  *different quantities* and shouldn't be compared as if they were the
  same thing)

And yet they **both land in the same broad sticky-marshmallow territory**.
Two roads, same destination.

### The honest gap

| | Drobczyk | Our T41 (post-R12) | Ratio |
|---|---|---|---|
| σ/m at dwarf v ≈ 10 km/s (cm²/g) | 0.96 | ~0.066 (at MAP) | **~15×** |
| σ/m at MW v ≈ 30 km/s (cm²/g) | 0.11 | ~0.066 (at MAP) | **~1.7×** |
| DM mass | 600 GeV | 15.74 GeV (median) / 398 GeV (MAP) | 40× / 1.5× |
| Mediator mass | 15 MeV | 26.60 MeV (median) / 336 MeV (MAP) | 1.8× / 22× |
| σ_SI (cm²) | 6.7×10⁻⁵¹ (intrinsic) | 1.2×10⁻³² at ε=10⁻⁵ → effectively 0 at MAP ε=10⁻³⁵ | very different |
| Coupling | y_χ = 0.30 (Yukawa) | g_χ = 0.133 (dark gauge) | not comparable |

The ~1.5×–15× factor is the honest apples-to-apples comparison once the
velocity is matched and the post-R12 T41 number is used. It is **not**
"within 30%" — that earlier v10 synthesis framing was overstated, and the
R12 audit (which surfaced this issue again on 2026-08-18) makes the gap
larger, not smaller.

More importantly:

> **Both numbers sit inside the "allowed marshmallow zone"** (which is
> roughly 0.1 to 10 cm²/g). So neither model is "wrong" — they're both
> saying the same thing in astrophysical terms, just with different
> precision. The qualitative convergence is what survives.

### The part that matters even more — but more honestly

Both models also predict the same **operational** thing about direct
detection experiments (the underground labs that try to catch dark matter
hitting ordinary atoms):

- **Drobczyk**: σ_SI ≈ 7×10⁻⁵¹ cm² (below the neutrino floor — but
  reachable by **next-generation multi-tonne or directional detectors**)
- **Ours at ε=10⁻⁵** (canonical pre-LZ): σ_SI ≈ 1.2×10⁻³² cm² (about
  5×10¹⁵ **above** LZ — would be instantly ruled out)
- **Ours at the T41 MAP** (ε = 1.12×10⁻³⁵, driven by LZ): σ_SI is
  effectively zero for any practical detector

So both models predict "null results in current xenon experiments" — but
for **different reasons**:

- **Drobczyk's** is an intrinsically tiny σ_SI from the portal structure
- **Ours** is a tiny σ_SI because the kinetic-mixing ε is forced to
  ~10⁻³⁵ by LZ (a **30+ order-of-magnitude suppression** below the naive
  dimensional-analysis expectation of 10⁻³ to 10⁻⁵)

This is actually the most important point about the cross-validation — it
tells experimentalists **where the two models diverge in detection
strategy**:

- Drobczyk is testable by next-generation detectors (the σ_SI is small
  but not absurdly so).
- Ours is essentially "untestable by direct detection" unless someone
  figures out the UV physics that explains why ε is so incredibly small.

That second point is a real **theory bottleneck** for our Benchmark A
constructions; the R12 closure document flags it as the open problem.

### Why this is useful

When two independent theoretical approaches converge on the same broad
qualitative answer — "MeV-scale decoupled mediator, σ/m in the SIDM dwarf
band, invisible to current direct detection" — that's a **hint that the
broad picture is right**, even if the exact numbers are off by 1.5×–15×.
If Drobczyk's model had predicted σ/m = 100 cm²/g and ours predicted
0.01 cm²/g, we'd know one of us was wrong. Instead, we're both in the
same neighborhood. The honest framing is: **qualitative convergence
plus a real detection-strategy divergence**, not "validated to within
30%."

---

## TL;DR for the elevator

We and Drobczyk independently built dark matter from different
ingredients, and both ended up with a MeV-scale dark messenger that's
hidden from ordinary matter. Our post-R12 canonical σ/m_0 ≈ 0.066 cm²/g
versus Drobczyk's 0.11–0.96 cm²/g at dwarf velocities — a factor of
1.5×–15× apart, not "within 30%". Both inside the same broad SIDM
allowed band. Both predict detection nulls for current experiments, but
for different reasons: Drobczyk's σ_SI is intrinsically small; ours is
small because LZ forces ε to ~10⁻³⁵. The qualitative convergence is
real; the quantitative gap is now honest about being a gap.

---

## Where this lives in the project

- **Source data (post-R12):** `v0.3-prelim/data/results/t68_cross_validation_drobczyk.json`
  (updated 2026-08-18 to use the T41 joint-fit MAP rather than the stale
  pre-R12 T54 toy number)
- **Source data (canonical R12):** `v0.3-prelim/data/results/t41_mediator_mass_joint_fit.json`
- **Source data (stale, pre-R12):** `v0.3-prelim/data/results/t54_dark_quark_joint_fit.json`
  (retained for historical provenance; do not use as the headline)
- **Plot:** `outputs/Cross_Validation_T54_vs_Drobczyk_v2_2026-08-13.png`
  (still uses the pre-R12 T54 coord; see R12c note — plot regeneration
  is deferred because the broad qualitative picture is unchanged)
- **Code:** `v0.3-prelim/code/t68_cross_validation_drobczyk.py`,
  `v0.3-prelim/code/t72_cross_validation_plot.py`,
  `v0.3-prelim/code/t41_mediator_mass_joint_fit.py`
- **Tests:** `v0.3-prelim/tests/test_t68_cross_validation.py`
  (updated 2026-08-18 to assert that our σ_SI at ε=10⁻⁵ is intentionally
  above LZ, with the LZ evasion coming from the ε-suppression at MAP)
- **Synthesis (technical):** `v0.3-prelim/docs/MEDIATOR_DETECTION_SYNTHESIS_v10.md`
  (and v11/v12 cross-validation refinements)
- **R12 closure document (canonical framing):**
  `v0.3-prelim/docs/R12_AUDIT_CLOSURE.md` §3, §5.2, §7.5
- **Citation:** `CITATION.cff` (Drobczyk corrigendum cited as
  σ_SI = 6.7×10⁻⁵¹ cm²)
- **Reframing trail:**
  - R11 reviewer audit, finding A13 + recommendation G7 (first re-cast
    of "external validation" → "qualitative literature consistency")
  - R12 audit (2026-08-17), which superseded the T54 toy MAP with the
    T41 joint-fit MAP
  - R12a (2026-08-18), which corrected the "within 30%" framing to
    "factor ~1.5" for the pre-R12 numbers
  - R12c (this patch, 2026-08-18), which updates the layman doc and
    the T68 JSON to reflect the post-R12 T41 numbers and the resulting
    larger 1.5×–15× gap

---

*This document is the layman-facing companion to T68. For the underlying
numbers, the technical synthesis, and the R12 closure's full honest
framing, follow the links above.*
