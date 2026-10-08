# Future Directions: DM-DE Coupling and Ultra-Light DM

**Status:** Research note. Not part of v19.2-D paper. Two adjacent research directions that could provide a path forward if the SIDM Phase 44 framework is genuinely at its structural limit.

**Context:** R88(56) honest synthesis establishes the structural trade-off theorem as a fundamental limit of the SIDM Phase 44 framework. R88(70) confirms CDG-2 is non-constraining. R88(71) tightens the pre-claim checklist. The user has asked whether the trade-off could be relaxed by introducing (a) dark energy-dark matter coupling or (b) ultra-light scalar field dark matter (chameleon / soliton). This note assesses both.

---

## Direction A: Interacting Dark Energy + Two-Component SIDM (IDE-2cSIDM)

### The idea

What if the heavy and light SIDM species couple differently to dark energy? Concretely: the heavy species has a coupling β_H to the dark energy field, and the light species has β_L. The energy exchange between DM and DE is then species-dependent. This changes how the two populations dilute with cosmic expansion:

- Standard cosmology: ρ_DM ∝ a⁻³ (matter dilutes as volume grows)
- IDE: ρ_DM ∝ a⁻³⁺ξ where ξ is set by the coupling strength
- Species-dependent: ρ_heavy ∝ a⁻³⁺ξ_H, ρ_light ∝ a⁻³⁺ξ_L, with ξ_H ≠ ξ_L

If ξ_H > 0 (heavy species dilutes FASTER than standard matter), the heavy fraction f_H = ρ_heavy/(ρ_heavy + ρ_light) drops with cosmic time even without tidal stripping. This provides a *cosmological* mechanism for f_H evolution, in addition to the *gravothermal* mechanism the project currently considers.

### Why this could break the trade-off

The structural trade-off theorem (R88(56) §9.17b) is derived under ΛCDM background — f_H evolves only via gravothermal segregation and tidal stripping. With IDE:

- Different halos at different redshifts see different f_H
- The "saturation cap" at f_H = 0.95 from gravothermal evolution is *not* the only limit
- The f_H vs radius profile could be modified by ξ_H ≠ ξ_L

Specifically: if heavy species drains into DE at high z, then low-z clusters (Perseus, etc.) have lower f_H than the Phase 44 baseline. This could simultaneously:
- Reduce σ_eff(150) for subhalos (He+ 2020 satisfied)
- Keep σ_eff(150) moderate for centrals (Lei/Wang satisfied)

Because the f_H profile is no longer determined by gravothermal segregation alone, the trade-off theorem's geometric argument (heavy concentrates at center → light dominates at r>0.2 r_s) may not apply.

### What the literature says

- **Zhao+ 2025 (arXiv:2501.03750):** Halo spin and orientation in IDE cosmology. Shows IDE changes halo assembly history and angular momentum. The coupling β ≲ 0.05 is currently allowed by Planck + DESI.
- **Beltrán Jiménez+ 2026 (A&A 707 A269):** Non-linear structure formation with elastic dark-sector interactions. Develops the perturbation theory for IDE with non-zero sound speed in DE.
- **Low+ 2026 (MNRAS 546 staf2259):** Hydrodynamic simulations of flavour-mixed 2cDM with IllustrisTNG baryonic physics. First simulation of two-component inelastic DM with realistic baryons. They find ~10-15% modifications to inner density profiles — not enough to break SIDM trade-offs on its own, but suggests the framework is computationally tractable.
- **Teixeira+ 2026 (PRD via APS):** Hybrid dark sector from inflation. Provides a particle physics motivation for the coupling. Coupling strength is model-dependent but testable.

### What would need to be true for this to work

1. **Cosmological motivation:** A Lagrangian that gives ξ_H ≠ ξ_L. The simplest model: heavy species has a dark U(1) charge that mediates coupling to the DE quintessence field. Specificity required.

2. **Halo-mass dependence:** Different mass halos should see different f_H evolution. This requires the coupling to depend on halo environment, not just cosmic time. Possible if the DE field is inhomogeneous on cluster scales.

3. **Avoiding ΛCDM violations:** β ≲ 0.05 from Planck constraints. Need to verify that the IDE-2cSIDM combined model doesn't exceed these bounds in the CMB or large-scale structure.

4. **Survival of gravothermal physics:** The Yang+ 2024 / Fischer+ 2025 / Gurian & May 2025 / van den Bosch & Dattathri 2026 gravothermal cascade must still work. The IDE modification should not destroy the core formation mechanism that explains the existing PASS channels (Horigome, SPARC, Cloud-9).

### Kill criteria

- If Planck + DESI + Euclid DR1 (Nov 2026) jointly constrain β to <0.01: too small to break trade-off
- If the IDE-2cSIDM model can't be built from a consistent Lagrangian: theoretical dead-end
- If the modification breaks the existing PASS channels (Horigome, SPARC, Cloud-9): regression

### Resource estimate

~2-3 months computational work:
- 1 month: derive IDE-2cSIDM Lagrangian, identify free parameters, test viability
- 1 month: implement the modified σ_eff calculation, rerun all 8 channels
- 0.5 month: compare with Phase 44 baseline, write up

Code extension: add IDE coupling terms to existing `phase_g10_sidm2c_f_h.py` and `phase_g12_multi_species_uv.py` modules. Reuse infrastructure.

### Verdict

**PROMISING but unproven.** The literature has the cosmological-perturbation infrastructure. The 2cDM simulation work (Low+ 2026) shows it's computationally tractable. The key question is whether the IDE modification is strong enough (β ~ 0.05) to break the trade-off without breaking existing constraints. This is a Direction-D-like path: cheap to test (~2-3 months), high information value even if it fails.

**Priority:** Medium. Worth a Phase G17 or G18 if no other path forward emerges.

---

## Direction B: Ultra-Light (Scalar Field) Dark Matter — Soliton Cores

### The idea

Replace SIDM (a particle DM with velocity-dependent cross-section) with ULDM (a classical scalar field with mass m_φ ~ 10⁻²² eV). The field has a de Broglie wavelength λ_dB = h/(m_φ v) ~ kpc at galactic velocities, which naturally produces cored density profiles via soliton formation.

The soliton-halo relation (Bar+ 2018, Blum+ 2025): soliton mass M_sol ∝ M_halo^1/2, soliton radius r_sol ∝ M_halo^(-1/2). This is a single power-law that connects small and large halo mass scales.

### Why this could break the trade-off

The structural trade-off theorem is specific to SIDM with two species and gravothermal evolution. ULDM is a fundamentally different framework:

- **No σ_eff vs σ_HH distinction:** ULDM is a wave equation, not a Boltzmann equation. The "observable cross-section" concept doesn't apply.
- **No gravothermal cascade:** The soliton is the ground state, not a phase. There's no "core formation → core collapse" sequence.
- **Halo mass diversity comes from the soliton relation, not gravothermal timing:** All halos have solitons, but the soliton size scales as M^(-1/2). Massive halos have small dense solitons; dwarf halos have large diffuse solitons.

If ULDM successfully explains the same channels as SIDM (Horigome cores, Cloud-9, SPARC, etc.) and additionally explains the channels SIDM fails (Lei/Wang vs He+ 2020 at v=150), it would be a more successful framework. The "trade-off" only applies within the SIDM parameter space; ULDM is a different parameter space.

### What the literature says

- **Bar, Blas, Blum, Sibiryakov 2018 (PRD 98 083027):** Galactic rotation curves vs ULDM. The original soliton-host halo analysis. Found a doubly-peaked rotation curve when the soliton-host transition is sharp enough.
- **Bar, Blum, Sun 2022 (PRD 105 083015):** Systematic comparison with SPARC data. The ULDM fit to SPARC is competitive with NFW but with one free parameter (m_φ) instead of two (concentration, mass).
- **Blum+ 2025 (JCAP 06 050):** Bracketing the soliton-halo relation. Tighter constraints on the M_sol vs M_halo relation from numerical simulations. Fits data with ~10% precision.
- **Teodori+ 2026 (PRD via APS):** ULDM simulations of stellar dynamics in dwarf galaxies. First direct simulation of stellar orbits in a soliton-halo system. Finds that the soliton produces a flat velocity dispersion profile at small radii — consistent with observed dSphs.
- **Cisneros+ 2026 (Galaxies 14 12):** Single-parameter model for galaxy rotation curves. Demonstrates ULDM with a single m_φ value fits a wide range of galaxy types.

### What would need to be true for ULDM to replace SIDM here

1. **Soliton at all mass scales:** The soliton-halo relation must hold from M_h ~ 10⁸ M☉ (dSphs) to M_h ~ 10¹⁴ M☉ (clusters). Current literature: well-tested for M_h ~ 10⁹-10¹², extrapolated to cluster scale. Cluster scale is the gap.

2. **He+ 2020 subhalo prediction:** Subhalos in ULDM should not have enhanced scattering (no σ_m concept). The relevant prediction is the projected soliton density at the subhalo center. If subhalos have less concentrated solitons (because they're tidally stripped), this would satisfy He+ 2020's "low σ_eff" prediction naturally.

3. **Lei/Wang prediction:** The 0.1-0.3 cm²/g prediction at v=150 km/s doesn't directly map to ULDM. The ULDM prediction would be: soliton size at M_h corresponding to v_max ~ 150 km/s. The soliton-halo relation gives r_sol ~ M_h^(-1/2) ~ 0.5-1 kpc for these masses. This is consistent with the observed core sizes of massive galaxies.

4. **m_φ value:** The ULDM particle mass is constrained to m_φ ~ 10⁻²¹ to 10⁻²² eV from dwarf galaxy cores (Schive+ 2014). This is a single number that determines the entire framework.

### Kill criteria

- If ULDM solitons can't form in cluster-mass halos (V_max > 300 km/s): framework fails for massive systems
- If the soliton-halo relation doesn't reproduce the observed core-size diversity: framework incomplete
- If Lyman-alpha forest constraints exclude m_φ < 10⁻²¹ eV: parameter space too narrow
- If ULDM and SIDM Phase 44 are observationally indistinguishable at all available channels: switching frameworks adds no information

### Resource estimate

~3-4 months:
- 1 month: re-derive all 8 channels under ULDM framework, identify which SIDM parameters map to ULDM observables
- 1.5 months: implement soliton profile + soliton-halo relation, replace SIDM σ_eff with ULDM density predictions
- 1 month: compare with SIDM Phase 44, identify which channels ULDM does better or worse

This is a more substantial project than Direction A because it requires a new framework, not just a new parameter.

### Verdict

**ALSO PROMISING but at higher cost.** The literature has the simulation infrastructure (Teodori+ 2026). The single-parameter economy is attractive. The main risk is that ULDM and SIDM Phase 44 may be observationally indistinguishable at the channels the project can test, in which case the project is just changing frameworks without adding information.

The bigger question: is ULDM a *better* explanation of the small-scale structure puzzles than SIDM? If yes, the project should consider whether to add a ULDM comparison chapter. If no (and they're observationally equivalent), the project should stay with SIDM as its chosen framework.

**Priority:** Lower than Direction A. Worth considering if the user wants to explore alternative frameworks, but it changes the project's scope significantly.

---

## Comparison

| Criterion | Direction A (IDE-2cSIDM) | Direction B (ULDM) |
|---|---|---|
| Modifies existing framework? | Yes (adds IDE to SIDM) | No (replaces SIDM with ULDM) |
| Trade-off theorem still applies? | Maybe (depends on β) | No (different framework) |
| Cost | 2-3 months | 3-4 months |
| Kill criteria clear? | Yes (Planck β limit) | Mixed (soliton-cluster test) |
| Existing literature support | Strong (Low+ 2026, Zhao+ 2025) | Strong (Blum+ 2025, Teodori+ 2026) |
| Particle physics motivation | Yes (hybrid inflation, Teixeira+ 2026) | Yes (axion-like, string theory) |
| Risk of new trade-off emerging | Medium | High (ULDM has its own tensions) |

## Recommendation

**For the SIDM v19.2-D project as currently scoped:** Neither direction changes the paper. R88(56) honest synthesis is the correct final state.

**For the future v19.2-E project (per FUTURE_WORK_PLAN_V19_2_E.md):**
- Add Direction A (IDE-2cSIDM) as a new path: ~2-3 months, low-to-medium cost, clear kill criteria. Could be tagged as Path 4.
- Direction B (ULDM) is a different research program entirely. Don't add as a "path" within SIDM; consider as a separate project if the user wants to explore alternative frameworks.

**For the user (decision now):**
- If the goal is "find any way to break the trade-off": try Direction A first (cheaper, closer to existing work)
- If the goal is "compare alternative frameworks": Direction B is more appropriate
- If the goal is "ship v19.2-D as-is": neither is needed

Standing by for next direction.
