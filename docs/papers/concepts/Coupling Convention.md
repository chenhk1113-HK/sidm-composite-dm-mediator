# Coupling Convention (LOCKED)

The v19.2-F project uses the **α_D ≡ g²/(4π)** convention, locked per ClawsGO #9/#10/#11 recommendations (2026-10-11).

## Definitions
- **g:** dark gauge coupling (dimensionless)
- **α_D:** dark fine-structure constant (dimensionless), defined as g²/(4π)
- **This is the standard convention** used in Tulin-Yu (2013), Kaplinghat et al. (2016), Chu+ 2018, etc.

## Why this matters
Using α = g² instead of α = g²/(4π) gives σ/m values that differ by **factors of 4π ≈ 12.57**. The v19.2-F project had three different σ/m(100) values (0.052, 2.84, 41.0) for the same point before the convention was locked.

## κ resonance criterion
- **κ = α_D × m_χ / m_ρ** (dimensionless)
- **κ_c = 1.6798** (analytic) or **1.68** (rounded)
- The Tamm 1947 (ZhETF 17, 884) threshold is cited; this is the s-wave bound-state formation threshold for the Yukawa potential V(r) = -(α_D / r) × exp(-m_ρ × r).

## Born vs κ regimes (INDEPENDENT)
- **Born valid:** α_D ≪ 1 (weak-coupling, perturbative)
- **Bound state:** κ > κ_c (deep enough potential)
- A coupling can be Born-valid (α_D = 6.8e-7 ≪ 1) yet still form a bound state (κ = 3.4 > κ_c) — different physics, not a single threshold

## G_CHI = sqrt(4π × α_D) = sqrt(4π × 5.55e-6) = 8.351e-3
- Bare gauge coupling, derived from α_D under the locked convention
- This is checked at import time in `constants.py` (`_run_convention_checks`)

## Used by
- `constants.py` (root, LOCKED)
- All scripts that import from `constants.py`

## Backlinks
- [[Concepts/SIDM Framework]] — Yukawa potential, resonance behavior
- [[Concepts/Resonance Cross-Section]] — uses α_D in σ/m formula
