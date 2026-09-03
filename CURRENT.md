# CURRENT — Version-of-Record (1 page)

> **For:** Anyone who has 60 seconds and wants to know what this project
> is, what it claims, and what the current best numbers are.
> Updated with each version-bump round. Last refresh: 2026-09-03 (T86).

---

## Standing: v0.4-prelim+T75 (Tier-1 milestone)

The project is a joint-fit framework for self-interacting dark matter
(SIDM), grounded in published astrophysical data. The standing version
(`v0.4-prelim+T75`) is the result of rounds **T72–T79** adding DAMPE and
Zhang+2025 LSS channels; **T80** confirming LZ paper compatibility;
**T81** adding XENONnT/PandaX watch; **T82** stale-claim audit;
**T83** KSFR (3,2) fundamental LATTICE promotion; **T84** Channel 18 ρ
sensitivity sweep. All within one standing version — no re-run of the
joint fit after T75.

## What the project measures

A 6-dimensional Bayesian posterior over Benchmark A parameters:
`(log_ε, log_α, m_φ, m_χ, g_χ, log_ξ)`, sampling via dynesty nested
sampling. **19 channels** of observational data constrain the posterior.

## v0.7 posterior headline (nlive=2000, ~7 min wall)

| Quantity | Value | Source |
|---|---|---|
| **Bayesian evidence log Z** | **−163.29 ± 0.085** | T41 nlive=2000 |
| DM mass **m_χ** (MAP) | **770 GeV** (median 498) | T41 posterior |
| Mediator mass **m_φ** (MAP) | **453 MeV** ✓ KSFR-valid (median 588) | T41 posterior |
| **σ/m₀** at galactic scale (MAP) | **0.27 cm²/g** | T41 derived |
| Velocity index **a** (Yukawa, at MAP) | +0.344 | T41 derived |
| Tension T39 vs Yukawa a | **0.60σ** (below 1.0 threshold) | T41 vs T39 |
| Bare **ε** (median posterior) | **1.4×10⁻³⁷** | T41 posterior |
| Bare **α_X** (median posterior) | 3.5×10⁻¹⁶ | T41 posterior |
| Dark Yukawa **g_χ** (MAP) | 1.19 | T41 MAP |
| Form-factor suppression **ξ** (MAP) | 0.17 | T41 MAP |

## Channels in production

1. dSph kinematics
2. UFD kinematics
3. Bullet Cluster
4. SPARC rotation curves (calibrated saturation; Tier-2 hierarchical upgrade pending)
5. LZ WS2024 direct detection (sanity check only — orthogonal posture)
6. Fermi gamma-ray dwarf stacking
7. H3 convergence & H4 form-factor sweeps
8. **DAMPE CRE** (T72-T73)
9. **Zhang+2025 LSS** assembly bias (T74)
10. **XENONnT + PandaX-4T** competitor watch (T81)

(Plus ~9 internal/auxiliary channels: KSFR mask, mediator lifetime, etc.)

## Standings posture — what σ/m does and doesn't say

- **σ/m = 0.27 cm²/g measures σ_DM-DM** (SIDM observable, galactic scale).
- **σ_DM-nucleon** (LZ/XENONnT/PandaX observable) is suppressed by
  **~50–80 orders of magnitude** at this posterior due to kinetic-mixing
  ε ~ 10⁻³⁷. Direct-detection constraints enter as sanity checks only.
- **σ_DM-DM ≠ σ_DM-nucleon in practice** at this point in parameter space,
  despite being theoretically linked via the dark-photon portal. They
  become linked only at ε ≫ 10⁻¹⁰, which the posterior excludes.

## Standing test count

- **542 pass / 6 skip** (post-T84)
- Drift-guard audit (`scripts/t82_audit.py`): **32/32 ALL CLEAR**
- Standing version file: `0.4-prelim+T75` (verified by audit)

## Where to read deeper

- README.md — full project description + quick-start (440 lines)
- docs/LAYMAN_SUMMARY.md — non-expert overview
- docs/MATHEMATICS.md — formulas & derivations
- docs/DARK_SECTOR_LAGRANGIAN.md — Benchmark A specification (§9 is canonical)
- MODEL_ASSUMPTIONS_AND_LIMITATIONS.md — what the project does NOT claim
- docs/INDEX.md — full navigation
- v0.3-prelim/data/results/2026-09-02_dampe_poc/ — T75/T76/T84 result JSONs
- v0.3-prelim/docs/T72_*.md → T84_*.md — per-round documentation

## Provenance

> Generated 2026-09-03 (T86) as a 1-page version-of-record. Numbers
> spot-checked against `v0.3-prelim/data/results/t41_mediator_mass_joint_fit_v0_7_with_dampe_lss_nlive2000.json`.
> Standing version `v0.4-prelim+T75` (no bump in T82-T86).
