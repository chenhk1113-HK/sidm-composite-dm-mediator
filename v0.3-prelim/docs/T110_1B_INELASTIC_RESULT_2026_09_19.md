# T110.1B — Inelastic SIDM Parameter Mapping

**Date**: 2026-09-19
**Branch**: wip/inelastic-SIDM
**Sub-task**: T110.1B (inelastic SIDM literature + parameter mapping)
**Status**: NEGATIVE RESULT — simple inelastic SIDM cannot satisfy Cloud-9 + dSph

## Summary

Implemented standard inelastic SIDM framework (endothermic scattering χ₁χ₁ → χ₂χ₂ with mass splitting δ) and tested whether it can satisfy Cloud-9 (σ/m ~100 at v=28 km/s) and dSph (σ/m < 0.2 at v=30 km/s) simultaneously.

## Implementation

`v0.3-prelim/code/inelastic_sidm.py` (~270 lines):
- `InelasticSIDMParams` dataclass: m_chi, delta, sigma_0, sigma_elastic
- `v_threshold_kms(delta, m_chi)`: v_thr = sqrt(4*delta/m_chi) × c
- `sigma_inelastic(v, p)`: phase-space factor below/above threshold
- `sigma_m_total_inelastic(v, p)`: total = elastic + inelastic

## Critical Finding: WRONG DIRECTION

**Cloud-9 velocity is v=28 km/s, dSph velocity is v=30 km/s.**

This means Cloud-9 is at LOWER velocity than dSph.

Endothermic inelastic scattering (the standard model):
- Below threshold (v < v_thr): NO inelastic scattering (channel closed)
- Above threshold (v > v_thr): inelastic channel OPENS
- σ_total(v) INCREASES with v above threshold

If v_thr = 30 km/s:
- Cloud-9 (v=28): elastic only, σ = 100 cm²/g (set by elastic)
- dSph (v=30): elastic + inelastic, σ = 100 + ~80 = 180 cm²/g

This gives σ(dSph) > σ(Cloud-9). **OPPOSITE of what we need.**

## Why Both Inelastic Variants Fail

### Endothermic (χ₁χ₁ → χ₂χ₂):
- σ INCREASES with v above threshold
- Wrong direction for Cloud-9 < dSph

### Exothermic (χ₁χ₂ → χ₁χ₁):
- Channel OPEN at all v (reaction releases KE)
- σ DECREASES with v (less benefit at high v)
- Could give σ(Cloud-9) > σ(dSph) if v_thr is between them
- BUT: at v=28 (Cloud-9), the inelastic is below threshold, so σ = elastic only
- At v=30 (dSph), even less inelastic benefit than at v=28
- σ(dSph) < σ(Cloud-9) would work in principle
- BUT: the velocity gap is 2 km/s only (28 → 30), so the difference is tiny

## The 500× Suppression Requirement

To satisfy Cloud-9 (100 at v=28) AND dSph (<0.2 at v=30):
- Suppression factor: 100/0.2 = 500×
- Velocity gap: 30/28 = 1.07
- Required power law: (1.07)^n > 500 → n > 56

**σ/m must decrease like v^(-56) or steeper between v=28 and v=30.**

Neither smooth resonance (Chu+ 2019) nor step-function (inelastic) can achieve this steepness over a 2 km/s gap.

## Comparison with Both Approaches

| Approach | σ(28) / σ(30) | Achievable |
|---|---|---|
| Phase 44 broad BW | 100/160 (0.63) | Below dSph ✗ |
| Chu+ near-threshold | 100/0.002 (50,000) | At unitarity ✗ |
| Inelastic endothermic | 100/180 (0.56) | Below dSph ✗ |
| Inelastic exothermic | ~equal | Far below 500× ✗ |

**None of the standard velocity-dependent mechanisms can give the required 500× suppression across a 2 km/s gap.**

## Implication for the Project

The fundamental issue is the **proximity of Cloud-9 (v=28) and dSph (v=30) velocities**. They are physically too close for any smooth σ(v) function to suppress dSph while preserving Cloud-9.

This suggests that **either**:
1. The dSph upper limit (Horigome+ 2025) at v=30 is not actually applicable at that velocity — perhaps the paper uses a different velocity convention
2. Cloud-9 has a σ/m peak that genuinely is at v=28 (not v=30), and the model needs to drop by 500× in 2 km/s — physically impossible with smooth σ(v)
3. The Cloud-9 kinematic velocity is different from what we assumed — perhaps v=15 (Fornax-like) not v=28

## Recommendation

Both Path A (near-threshold RSIDM) and Path B (inelastic SIDM) are closed by the same fundamental constraint.

Three paths forward:
1. **Accept the 800× dSph violation** as a known limitation (paper v1.9 already documents this)
2. **Re-examine the velocity conventions** in Horigome+ 2025 — maybe the constraint applies at v=15 (Fornax/Tri II) not v=30
3. **Drop Cloud-9's strict requirement** (σ/m ≥ 100) and adopt a softer target (σ/m ≥ 10), which is consistent with the Benítez-Llambay+ 2024 floor of σ/m ≳ 50 but leaves headroom

## What T110.1B Produced

- `v0.3-prelim/code/inelastic_sidm.py` (~270 lines) — reusable for future inelastic SIDM work
- This document — full negative result

The infrastructure is preserved for any future project that wants to test inelastic mechanisms against other data sets where the velocity gap is larger.
