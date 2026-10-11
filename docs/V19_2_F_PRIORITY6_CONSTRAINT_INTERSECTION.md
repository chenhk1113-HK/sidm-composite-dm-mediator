# Priority 6 — Constraint Intersection Map (BBN/CMB/SN1987A/Lyman-α/DD)

**Date:** 2026-10-11
**Purpose:** Identify which (α_D, m_A') points survive independent constraints AND match the cloud-9 feature (σ/m = 174 cm²/g at v = 29.4 km/s).

## Constraints considered

| Constraint | Applies to | Limit | Framework point (α=6.8e-7, m_A'=200 eV) | Phase 3 best fit (α=5.55e-6, m_A'=126 keV) |
|---|---|---|---|---|
| BBN | m_A'<10 MeV decaying to e⁺e⁻ | Kinetic mixing ε<10⁻¹⁰ | Survives if invisible decay | Same |
| CMB energy injection | m_A'<100 MeV decaying to e⁺e⁻ at z~1100 | τ>10²⁵ sec | Survives if invisible | Same |
| SN1987A cooling | m_A'<100 MeV in supernovae | α_D<10⁻¹⁰ for [1, 100] MeV | NOT constrained (below production threshold) | N/A (126 keV too heavy) |
| Lyman-α (subhalo survival) | σ/m>100 cm²/g at v~30 km/s | σ/m ∈ [1, 50] preferred | UNCERTAIN — Calogero NaN at κ=3.4 | UNCERTAIN — at σ/m=170 cm²/g, likely TOO HIGH (erases subhalos) |
| Direct detection (DM-electron) | dark photon with kinetic mixing | ε<10⁻⁵ | Survives if no kinetic mixing | Same |
| Thermal relic | <σv>~3×10⁻²⁶ cm³/s | N/A (not thermal) | N/A | N/A |

## Key finding: the Phase 3 best-fit point may be Lyman-α-excluded

The Phase 3 EXTENDED best-fit point (α_D = 5.55×10⁻⁶, m_A' = 126 keV) gives σ/m(29.4) = **170 cm²/g**. But σ/m(10) = 294, σ/m(100) = 16.2 cm²/g. **The peak is at v_peak = 5 km/s, not 29.4 km/s.**

Lyman-α constraint (Vogelsberger 2012, Zavala 2013): σ/m > 100 cm²/g at v ~ 30 km/s (dwarf scale) erases subhalos and conflicts with observed Lyman-α flux. The preferred range is σ/m ∈ [1, 50] cm²/g at this velocity.

**The Phase 3 best-fit point sits at the boundary** — σ/m(29.4) = 170 is above the Lyman-α preferred range. This is consistent with the project's choice to use phenomenological σ/m(174@29.4) as INPUT, not output.

## Intersection result

| Candidate | Status |
|---|---|
| Phase 3 best fit (α_D=5.55e-6, m_A'=126 keV, σ/m(29.4)=170) | Single-velocity coincidence (not a peak). Lyman-α marginal at v~30 km/s. |
| Framework (α_χ=6.8e-7, m_A'=200 eV) | κ=3.4 > κ_c, deep-Sommerfeld regime. Cannot compute with Calogero (NaN). t40 Born gives σ/m(29.4)=0.354 (UNRELIABLE). Constraint status UNKNOWN. |
| Bound-state ridge points (m_A'=3-43 eV, κ=10⁵-10⁷) | Ultra-low masses. **Likely BBN/CMB excluded for visible decay.** Survive only if A' is invisible (decays to dark sector). |

## Honest verdict

**Paper (A) — phenomenological σ/m(174@29.4) is the consistent option.** No (α_D, m_A') point simultaneously:
1. Places σ/m(29.4)=174 cm²/g as a PEAK (Phase 3 EXTENDED scan, 100 Calogero points)
2. Places a bound state with E₀ = E_target = -2.4 eV at the natural coupling (Priority 2.5 lattice scan)
3. Survives all independent constraints (BBN, CMB, SN1987A, Lyman-α, direct detection)

The "richer UV sector" path (Priority 4 composite form factor) does not produce a peak either. The "iDM resonance" hypothesis (per the original PDF report) is not first-principles derivable within the project's current scope.

**Standalone:** The cloud-9 feature remains phenomenological. Paper (A) is the honest result.

## Future work

1. **Compute σ/m at framework point with deep-Sommerfeld solver.** Hulthen approximation or imaginary-time evolution can give the true σ/m(29.4) at κ=3.4. This would resolve whether the framework point is Lyman-α-allowed or excluded.

2. **Refine Lyman-α constraint intersection** for the Phase 3 best-fit point. Use published SPARC/sigma/m fits (Kamada, Andrade, SIDM19/20/21 challenge) to get the full constraint map, not just the boundary.

3. **Invisible decay scenario for ridge points.** The bound-state ridge (m_A'=3-43 eV) requires very low mediator masses. If A' decays only to dark sector (invisible), BBN/CMB don't apply. Explore this in a future paper.

4. **Compare to published σ/m(v) curves** from Kaplinghat-Tulin-Yu 2016 for SIDM halos. Validate the phenomenological 174@29.4 against published halo fits.

## Files

- `v0.3-prelim/data/results/v19_2_f_phase3_constraint_intersection.json` (5.7 KB) — structured constraint map
- `docs/V19_2_F_PRIORITY6_CONSTRAINT_INTERSECTION.md` (this document)