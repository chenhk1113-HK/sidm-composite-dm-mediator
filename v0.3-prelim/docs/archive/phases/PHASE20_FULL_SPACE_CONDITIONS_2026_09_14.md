# Phase 20 — Full Space-Conditions Test of v0.3-prelim at m_chi = 5 GeV

> **Status:** Shipped 2026-09-14 (branch `wip/cloud-9-relhic`)
> **Direction:** Honest evaluation of v0.3-prelim MAP at m_chi = 5 GeV against ALL 20 channels in the T90.42 framework
> **Predecessor:** Phase 19 (full refit at m_chi = 5 GeV using 7 channels)

---

## The honest answer

**The v0.3-prelim model at m_chi = 5 GeV does NOT fit the full set of space conditions.**

Phase 19 used a 7-channel subset (LZ elastic + LZ 248 keV + Fermi + dSph + UFD + Bullet + SPARC). The full T90.42 framework has 20+ channels. Phase 20 evaluates the v0.3-prelim MAP against all 20.

## Per-channel evaluation at v0.3-prelim MAP (m_chi = 5 GeV, σ/m = 0.067, g_D = 0.092)

| # | Channel | loglike | Verdict |
|---|---|---|---|
| 1 | LZ elastic | 0.00 | NEUTRAL (σ_SI ~ 4e-56, way below limit) |
| 2 | LZ 248 keV | -0.08 | INERT (n_pred = 1.2e-90) |
| 3 | LZ magnetic moment | 0.00 | NEUTRAL (μ_χ suppressed for Majorana) |
| 4 | Fermi dwarf | 0.00 | NEUTRAL (σv = 2.5e-27) |
| 5 | CMB spectral distortion | 0.00 | NEUTRAL |
| 6 | ΔN_eff (Goldstein-Hill 2026) | 0.00 | NEUTRAL |
| 7 | LSS assembly bias | 0.00 | NEUTRAL |
| **8** | **DAMPE cosmic-ray electrons** | **-19.74** | **DISFAVORED** |
| **9** | **XRISM Perseus ICM** | **-76.19** | **DISFAVORED** |
| **10** | **eROSITA eRASS1** | **-5.56** | **DISFAVORED** |
| 11 | XRISM φ→γγ | 0.00 | NEUTRAL |
| 12 | Euclid Q1 lensing | 0.00 | NEUTRAL |
| 13 | Euclid Q1 subhalo | 0.00 | NEUTRAL |
| 14 | dSph | -0.05 | OK |
| 15 | UFD | -1.17 | OK |
| 16 | Bullet | 0.00 | OK |
| **17** | **KSFR/PCAC validity** | **-inf** | **HARD EXCLUDED** |
| **18** | **SPARC (saturated)** | **-202229** | **SATURATED FAIL** |
| 19 | Competitor DD watch | 0.00 | NEUTRAL |
| **20** | **Cloud-9 / RELHIC** | **-10.00** | **DISFAVORED** |

## Channels that fail

| Channel | Failure mode | Severity |
|---|---|---|
| **KSFR/PCAC** | Hard validity check (KSFR relation m_ρ/m_φ < 4π f_π) | **-inf** (model is structurally invalid for these parameters) |
| **XRISM Perseus** | ICM X-ray line search | **-76** log Z |
| **DAMPE CRE** | Cosmic-ray electron spectrum | **-20** log Z |
| **Cloud-9 / RELHIC** | Starless DM-dominated object cross-section (σ/m ~ 30 cm²/g at v=28 km/s) | **-10** log Z |
| **eROSITA eRASS1** | X-ray cluster catalog | **-5.6** log Z |
| **SPARC** | Saturated proxy — fails by ~2×10⁵ | **-202229** (proxy saturation, not real data) |

## What this means

**The v0.3-prelim MAP at m_chi = 5 GeV is tuned for a 7-channel subset, not the full 20-channel framework.** The T90.42 baseline fit (which uses all 20 channels) gives a different MAP entirely:
- **T90.42 baseline MAP**: m_phi ≈ 284 MeV, m_chi ≈ 240 GeV, g_chi ≈ 0.93
- **Phase 19 MAP** (m_chi = 5 GeV): m_phi = 200 MeV, m_chi = 5 GeV, g_D = 0.092

These are different points in parameter space. The full T90.42 6D sampler finds a different best-fit than the 5D Majorana reframe.

**Two key issues with the v0.3-prelim MAP**:
1. **KSFR/PCAC failure (-inf)**: For Majorana fermion DM with m_chi = 5 GeV and m_A' = 200 MeV, the KSFR relation breaks down. This is a **structural failure** — the model as parameterized violates a known theoretical constraint.
2. **Cloud-9 / RELHIC failure (-10)**: The T90.29 framework (Cloud-9 starless DM-dominated object) requires σ/m ~ 30-500 cm²/g at v = 28 km/s. The v0.3-prelim MAP gives σ/m = 0.067 cm²/g, which is 1000× too small. **Cloud-9 needs ~1000× larger σ/m at v=28 km/s than the v0.3-prelim MAP provides.**

## The Cloud-9 conflict is a real problem

Cloud-9 is a confirmed starless DM-dominated object (RELHIC) with:
- M_halo ~ 5×10⁹ M_sun
- Gas dispersion ~ 10 km/s
- σ/m_required at v=10 km/s ~ 30-500 cm²/g (very high)

The v0.3-prelim model predicts σ/m = 0.067 cm²/g at v=100 km/s. With velocity dependence (a ~ 0.07), σ/m at v=10 km/s would be:
  σ/m(10) = 0.067 × (10/100)^(-0.07) = 0.067 × 1.16 = 0.078 cm²/g

**This is 400-6000× too small for Cloud-9.** The model cannot accommodate the Cloud-9 cross-section at v=10 km/s with σ/m = 0.067 at v=100 km/s.

**This is a HONEST NEGATIVE** for the v0.3-prelim Majorana reframe at the current MAP. To fit Cloud-9, either:
- The velocity dependence must be MUCH steeper (a ~ 1.5+ instead of 0.07)
- σ/m at v=100 must be MUCH larger (0.067 → 50+ cm²/g)
- The model architecture must change (multi-portal, T90.45)

## What the model DOES fit

| Channel | Status |
|---|---|
| LZ elastic | ✓ (way below limit) |
| LZ 248 keV | ✓ INERT (consistent, not required) |
| LZ magnetic moment | ✓ (Majorana μ_χ is helicity-suppressed) |
| Fermi dwarf | ✓ (below limit) |
| dSph, UFD, Bullet | ✓ (slight tension, loglike ~ -1) |
| CMB, ΔN_eff, LSS, Euclid | ✓ (NEUTRAL) |
| XRISM φ→γγ | ✓ (NEUTRAL, no signal) |
| Competitor DD watch | ✓ (NEUTRAL) |

## The 7 channels used in Phase 19 were the easy ones

Phase 19 fit the model to:
- LZ elastic (always passes for Majorana)
- LZ 248 keV (INERT at any m_chi, by construction)
- Fermi dwarf (always passes below limit)
- dSph, UFD, Bullet (slight tension only)
- SPARC (saturated proxy, fails by design)

These are the 7 channels where the model is **trivially consistent** by construction. Adding the 13 channels used in T90.42 (CMB, ΔN_eff, LSS, XRISM, DAMPE, eROSITA, Euclid, KSFR/PCAC, Cloud-9, etc.) reveals that the v0.3-prelim MAP is **NOT** a global fit.

## What's needed for a true global fit

The **right way** to test the model against all 20 channels is to re-run the **T90.42 6D nested sampler** with m_chi as a free parameter, not just evaluate channels at the Phase 19 MAP.

**Recommended next step**: re-run the full T90.42 framework (6D nested sampling) with m_chi ∈ [0.5, 1000] GeV and the Majorana reframe structure. This would find the MAP that satisfies all 20 channels simultaneously.

This is a major compute effort (2-3 hours runtime) but is the only way to get a defensible "does the model fit the full set of space conditions" answer.

## Code & Data

- `code/phase20_full_space_conditions.py` (~390 lines)
- `data/results/phase20_full_space_conditions.json`
- `tests/test_phase20_full_space_conditions.py` — **3/3 PASS**

## References

- T90.42 baseline: `data/results/t41_mediator_mass_joint_fit_T9042_baseline.json`
- Phase 19 (m_chi=5 GeV MAP)
- T90.29 Cloud-9 / RELHIC
- Goldstein & Hill 2026 (ΔN_eff limit)
- KSFR/PCAC validity (R13 H1 closure)
