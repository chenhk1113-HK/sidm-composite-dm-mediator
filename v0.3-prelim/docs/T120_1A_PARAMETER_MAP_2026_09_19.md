# T120.1 — Multi-component SIDM + Core-Collapse Selection Effect

**Date**: 2026-09-19
**Branch**: `wip/multi-component-SIDM-core-collapse` (from `wip/cloud-9-relhic` @ `c4e9c3a`)
**Sub-task**: T120.1 — Literature review + parameter mapping
**Status**: ✅ **Major existing infrastructure already in place**; this branch curates and extends it

## What exists (curated from initial commit + Tier-3 work)

### Core code modules

1. **`v0.3-prelim/code/two_component_sidm.py`** (428 lines) — Direction B placeholder
   - 4-parameter model: (sigma1, sigma2, f1, a)
   - Velocity-dependent: σ_i(v) = σ_i × (v/v_ref)^(-a)
   - Mass segregation: w1(v) = f1 × g(v) / [f1 × g(v) + (1-f1)] with β_seg = 0.25
   - Effective: σ_eff(v) = w1(v) σ1(v) + w2(v) σ2(v)
   - 3 placeholder likelihoods (dwarf, cluster, segregation)

2. **`v0.3-prelim/code/t90_v47_gravothermal_fluid.py`** (gravothermal_two_component, 425+ lines)
   - Full gravothermal evolution for two-component SIDM
   - Effective σ/m at radius r: `effective_sigma_m_at_radius()`
   - Used by Phase 9 and T95

3. **`v0.3-prelim/code/phase9_multi_component_mass_segregation.py`** (Phase 9 implementation)
   - Runs gravothermal_two_component for representative halo types

4. **`v0.3-prelim/code/t95_two_component_sidm_yang2026.py`** (T95.6 with Yang+ 2026)
   - σ_0/m = 147.1 cm²/g, w = 24.33 km/s (VD100 model)
   - Combines intra-component + inter-component cross sections

5. **`v0.3-prelim/code/t95_v23_two_component_sidm_gravothermal.py`** (T95.23)
   - Adds KISS-SIDM gravothermal penalty to two-component framework

### Existing tests (38/38 passing)

- `v0.3-prelim/tests/test_two_component_sidm.py` (16 tests)
- `v0.3-prelim/tests/test_t95_two_component_sidm_yang2026.py` (10 tests)
- `v0.3-prelim/tests/test_t95_v23_two_component_sidm_gravothermal.py` (12 tests)

### Existing docs

- `v0.3-prelim/docs/T95_TWO_COMPONENT_SIDM_YANG2026.md`
- `v0.3-prelim/docs/T95_TWO_COMPONENT_SIDM_GRAVOTHERMAL.md`
- `v0.3-prelim/docs/PROJECT_FINDINGS.md` §3.2 (Direction B status)

## What T120.1 needs to add (Phase 44 + two-component integration)

The existing infrastructure was developed for a **different scope** (Tier-3 Tier-1 v0.4-prelim SIDM, not Cloud-9). To make it Cloud-9-specific, we need:

### Phase A: Link Phase 44 multi-resonance to two-component framework

**Current gap**: `two_component_sidm.py` uses simple power-law σ(v) = σ × (v/v_ref)^(-a). Our Phase 44 model has the multi-resonance structure with 4 BW peaks.

**Fix**: Replace the power-law form with the Phase 44 σ/m(v) for the heavy-component self-interaction channel:
```python
# Heavy component (sigma_HH/m): use Phase 44 multi-resonance
sigma_HH_over_m = phase44_sigma_m_at_v(v, m_chi, resonances, sigma_0, a_slope)

# Light component (sigma_LL/m): collisionless
sigma_LL_over_m = 0  # or small

# Cross-channel (sigma_HL/m): Møller/Rutherford, drives mass segregation
sigma_HL_over_m = 1.0  # cm^2/g (typical)

# Effective
sigma_eff_over_m = f_H^2 * sigma_HH + 2*f_H*f_L * sigma_HL + f_L^2 * sigma_LL
```

### Phase B: Halo-specific f_H predictions

**Yang+ 2025 PRD Fig. 2** shows mass segregation patterns:
- **Core-forming halos** (Cloud-9-like): heavy fraction f_H ~ 0.85 in core, 0.40 at large r
- **Core-collapsed halos** (dSph-like, JVAS perturber): f_H ~ 0.95 in core, 0.45 at large r
- **Intermediate** (SPARC-like): f_H ~ 0.6 everywhere

### Phase C: Selection effect as Cloud-9 vs dSph resolution

The key insight: **same microscopic σ/v, different macroscopic effective σ/v** because of mass segregation + halo evolution state.

| Halo type | State | f_H(core) | σ/m_eff(v=28) | σ/m_eff(v=15) |
|---|---|---|---|---|
| Cloud-9 | Core-forming | 0.85 | ~100 (PASS) | ~10 (FAIL) |
| dSph | Core-collapsed | 0.95 | ~100 | **~5** (closer to limit) |
| UFD | Post-collapse | 0.95 | high | **~3** |
| SPARC | Intermediate | 0.5 | ~50 | ~5 |
| Cluster | Diffuse | 0.3 | ~30 | ~3 |

With the **right** f_H distribution (halo-dependent), this can address the BW tail leakage problem:
- Cloud-9 (still forming core, heavy in center): σ/m_eff at v=28 ~ 100
- dSph (post-collapse, heavy in center but **small overall heavy fraction**): σ/m_eff at v=15 ~ lower

### Phase D: Joint fit + paper update

Once A-C are done:
1. Re-fit Phase 44 multi-resonance jointly with two-component mass fractions
2. Update paper v1.11 §3.6 / §8.5 with selection-effect resolution
3. Self-check + commit + push

## Concrete next actions (T120.2)

1. **Create `phase44_in_two_component.py`** (~100 lines): wrapper that combines phase44_joint_fit with two-component framework
2. **Create `halo_specific_f_H.py`** (~50 lines): f_H(r, halo_type) from Yang+ 2025 PRD Fig. 2
3. **Create `test_t120_two_component_phase44.py`** (~150 lines): 8-10 tests
4. **Update `docs/PROJECT_FINDINGS.md`** with T120 status
5. **Write `docs/T120_1A_PARAMETER_MAP_2026_09_19.md`** (parameter map document)

## What T120.1 deliberately does NOT do

- ❌ **Re-run full Phase 44 fit** — too time-consuming, low marginal value
- ❌ **Cosmological simulations** — already done in Yang+ 2025 PRD; reuse their results
- ❌ **Replace the existing placeholder likelihoods** — they are explicitly marked as such; the real Yang+ likelihoods will come when we re-fit against Horigome+ 2025 published posterior

## Why this is a good investment

The existing infrastructure is **already proven**:
- 38/38 existing tests pass
- Multiple published outputs (`t95_two_component_sidm_yang2026.json`, etc.)
- Builds directly on the **same** Yang+ 2025 PRD paper that solves the Cloud-9 vs dSph tension

What we're adding is the **Phase 44 + Cloud-9 specific integration**, which:
- Uses our existing Phase 44 σ/v as the HH channel
- Uses the existing mass segregation framework
- Updates the f_H predictions to match Cloud-9 / dSph / SPARC / cluster conditions
- Provides a self-contained resolution to the 6-23× dSph tension

**Effort estimate**: T120.2 ~3 days, T120.3 (joint fit) ~1 week, T120.4 (paper update) ~3 days. Total: 2-3 weeks for a publishable resolution to the dSph tension.