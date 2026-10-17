# SIDM Framework

**SIDM = Self-Interacting Dark Matter**

The v19.2-F project studies a specific class of SIDM models: **resonant SIDM with a Yukawa potential**.

## Yukawa potential
```
V(r) = ±(α_D / r) × exp(-m_ρ × r)
```
where:
- α_D = g² / (4π) is the dark fine-structure constant (see [[Coupling Convention]])
- m_ρ is the dark ρ meson (mediator) mass

## Resonant behavior
When the scattering energy in the CM frame is close to m_ρ, the cross-section is enhanced by a Breit-Wigner resonance. This is the basis of the "IN BAND" analysis: at the resonance peak, σ/m can reach 174 cm²/g at the v_target = 29.4 km/s (Cloud-9 velocity).

## Two σ/m formulas used
1. **Breit-Wigner resonance** (Born-level + resonance factor): used in v40.1-v40.5 IN BAND
2. **Gaussian background + peak** (empirical from Cloud-9 fit): used in v40.4, v40.9, v40.12 (canonical Gaussian)

## Key papers
- [[2207.13111 Gilman+ 2023]] — strong-lensing constraints on resonant SIDM
- [[2305.05067 Yang+ 2024 (Cloud-9)]] — gravothermal/isothermal σ/m comparison
- [[1705.02358 Tulin & Yu 2018]] — foundational SIDM review
- [[1712.02521 Chu+ 2018]] — M2 model (v_resonance selection)

## v19.2-F key results
- Canonical α_D = 5.55e-6 (project-internal dynesty fit)
- m_ρ = 0.05 MeV (M2 model, Chu+ 2018)
- m_χ = 1.0 GeV (canonical Phase 44)
- IN BAND at v_target = 29.4 km/s with σ/m = 174 cm²/g for Γ/ρ ∈ {5, 6, 7, 8}

## Backlinks
- [[Concepts/Coupling Convention]] — α_D convention
- [[Concepts/Resonance Cross-Section]] — σ/m formula
- [[Concepts/Gravothermal Collapse]] — t_c formula
