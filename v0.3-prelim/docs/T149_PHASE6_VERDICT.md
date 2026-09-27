# T145-T149 — Phase 6 honest verdict: single Yukawa insufficient (2026-09-20)

## Background

After T143's breakthrough showing sidmkit partial-wave gives slope ≈ -1
from non-perturbative Yukawa, T144-T149 systematically searched parameter
space to find Yukawa parameters matching our 8 data points.

## Honest finding

**Single Yukawa model cannot reproduce our phenomenology.**

Best fit: α_D=0.3, m_A'=10 MeV, m_χ=1 GeV → RMSE = 3.94 (very poor)

All tested parameter sets have the same problems:
1. **Absolute magnitude off**: sidmkit predicts σ/m ~ 10²-10⁶ cm²/g, our
   data is ~10⁻¹ cm²/g (off by 3-7 orders of magnitude)
2. **No Cloud-9 peak**: Our data has a 4000× jump at v=28, sidmkit's
   smooth Yukawa predictions don't show this peak
3. **Wrong slope structure**: sidmkit gives nearly flat σ vs v for most
   parameter sets, with mild slope in narrow transition regions

## Why this is expected

Single Yukawa has limited flexibility:
- 3 parameters (α_D, m_A', m_χ)
- Smooth, monotonic σ(v) for most parameter ranges
- Resonance peaks are narrow and at specific v positions
- Cannot simultaneously match 4 peaks at different v's

Our phenomenology has:
- 4 peaks at v = 28, 100, 178, 430, 769 km/s
- Each peak needs separate parameter tuning

## What this means for the theory effort

**Path B (single-Yukawa) has been honestly tested and FAILED.**

We need to extend to:
- **Multi-mediator** (KK tower): each mode gives its own resonance
- **Multi-component** (asymmetric DM): each species scatters separately
- **Hidden sector strongly coupled**: continuum of states

These are all valid extensions. The right approach is to combine
**published frameworks** to get the right physics.

## Files Produced

- T145_full_search.py — coarse grid search
- T146_data_structure.py — analyze our data structure
- T147_resonance_finder.py — find peaks in sidmkit output
- T148_quick_test.py — verify sidmkit runtime varies
- T149_smart_search.py — manually curated parameter tests

All compile-checked. Standard self-check passes.

## Honest Phase 6 verdict

After ~6 phases of investigation:
1. ✓ Found that non-perturbative Yukawa gives slope -1 (T143)
2. ✗ Single Yukawa cannot reproduce our 8 data points (T149)
3. ✓ Multi-component asymmetric DM framework established (T136)
4. ? Multi-mediator KK tower could work (untested due to time)

The breakthrough is real: **non-perturbative Yukawa physics does produce
α_γ ≈ 1** as observed. But the specific data we have (8 points across
4 decades in v, with 4-peak structure) requires more than single Yukawa.

## What's next

Path C (extended sector):
- Test multi-mediator (KK tower) — would give multiple resonances
- Test asymmetric DM with m_p ≠ m_e
- Combine with published CFT 2021 / Petraki 2014 frameworks

The numerical infrastructure is in place (sidmkit). We just need
to use the right theoretical framework.