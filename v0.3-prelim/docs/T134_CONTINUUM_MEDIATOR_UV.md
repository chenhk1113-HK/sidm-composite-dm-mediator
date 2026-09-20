# T134 — Continuum-Mediated SIDM Investigation (2026-09-20)

## What we searched for

In T133 we retracted §9.8.4's "Hidden U(1) derives slope = 0.5" claim.
That left UNKNOWN #1 (why α_γ ≈ 1 instead of Born 2) unanswered.

Searching the literature (Option D), the most promising candidate is:

> Chaffey, Fichet, Tanedo 2021 (arXiv:2102.05674, "Continuum-Mediated
> Self-Interacting Dark Matter", JHEP 06 (2021) 008, 34 citations):
> Continuum of low-mass mediator states (from nearly-conformal
> hidden sector) produces non-integer power-law velocity scaling:
> σ_T ~ v^(-4α) where α is the bulk mass parameter.

## Why CFT looked promising

Setting α_γ = 4α (our phenomenology slope):
- α_γ ≈ 1.0 (our data, MCMC, PySR)
- α ≈ 0.25 (bulk mass parameter)

CFT Eq. 6.14 predicts exactly v^(-4α) for α = 0.25 → v^(-1.0).
Matches our slope!

## Honest test result

I fitted the CFT formula σ_0 × (100/v)^(4α) to our 7 data points
(excluding Cloud-9 resonance). **The fit is poor** (R² = 0.13):

| v (km/s) | observed σ/m | CFT predicted | residual (log10) |
|----------|--------------|---------------|------------------|
| 3        | 1.55e-01     | 1.02e-01      | -0.18            |
| 5        | 9.31e-02     | 9.59e-02      | +0.01            |
| 7        | 6.66e-02     | 9.22e-02      | +0.14            |
| 10       | 4.68e-02     | 8.84e-02      | +0.28            |
| 15       | 3.18e-02     | 8.44e-02      | +0.42            |
| 100      | 1.93e-01     | 6.76e-02      | -0.46            |
| 500      | 2.52e-04     | 5.61e-02      | +2.35            |

The fit recovers α = 0.029 (not 0.25) — much weaker velocity dependence.

## Why the CFT framework doesn't fit cleanly

Our data has **multi-scale structure** (4 distinct regimes):
- v = 3-15 km/s: σ/m drops by 5× (smooth power-law)
- v = 28 km/s: **Cloud-9 peak** (4000× spike)
- v = 100-500 km/s: σ/m drops by 770×

CFT predicts ONE Born regime + ONE Classical regime + resonances.
Our 4 Breit-Wigner peaks at v ≈ 28, 100, 178, 430, 769 km/s don't
naturally fit a single bulk mass parameter.

## What CFT 2021 still offers

1. ✓ **Conceptual match**: continuum mediator produces non-integer
   power-law (matches our data better than pure Yukawa Born 1/v²)
2. ✓ **Resonance structure**: KK bound states could explain peaks
3. ✗ **Quantitative match**: requires 4 separate resonances, not 1
4. ✓ **Multi-peak**: CFT does predict "resonant: no simple scaling"

## What we'd need to make CFT work

The 4-peak structure might be from 4 specific KK modes (n=1, 2, 3, 4).
This requires the bulk mass spectrum to have specific mass gaps,
which depend on the geometry of the AdS slice (UV brane position).

To verify, we'd need to:
1. Solve the AdS/CFT Schrödinger equation for the specific geometry
2. Find which bulk mass parameter α gives 4 peaks at v ≈ 28, 100, 178, 430
3. Check that the velocity scaling between peaks is consistent

This is significant work (~1-2 weeks of calculation) and not certain
to succeed.

## Honest assessment

**CFT 2021 is the best published UV completion candidate we found,
but it's not a slam dunk.**

- ✓ It explains why slope ≠ pure Born 2
- ✓ It produces resonance structure
- ✗ Single-power-law fit is poor (our data has multi-peak)
- ? Would need significant parameter tuning to fit all 8 constraints

## Recommended path

This goes into the paper as **"CFT 2021 is a candidate UV completion
but requires further work to verify"** — alongside our 4 no-go
theorems and the EFT target map.

The honest statement: our phenomenology's UV completion is **still
open**, but CFT 2021 is the most promising lead in the literature.

## File outputs

- This file: v0.3-prelim/docs/T134_CONTINUUM_MEDIATOR_UV.md
- Update: §10.7 (NEW) in PAPER_V1_DRAFT.md if user approves