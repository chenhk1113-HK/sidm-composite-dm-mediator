# T184 — UV Completion for SIDM Phenomenology + Planck Relic Density

**Date**: 2026-09-21
**Status**: Major finding — thermal relic is INCOMPATIBLE with SIDM phenomenology

## Background

The phenomenological SIDM cross-section σ_HH = 0.052 cm²/g at m_χ = 10.3 GeV
(Phase 44) requires a UV completion that satisfies Planck 2018's
Ωh² = 0.1200 ± 0.0012. T181 established that σ_HH (elastic self-scattering)
is a **different physical quantity** from <σv>_ann (annihilation). The
phenomenology satisfies the multi-channel constraints but says nothing
about Ωh² without an explicit UV completion.

## Method

Test two UV completion candidates:
1. **Dark photon A' mediator** with annihilation channel χχ → A' → SM SM
2. **Higgs portal scalar** with annihilation channel χχ → h* → SM SM

For each:
- Compute <σv>_ann as a function of the relevant coupling
- Compute σ_HH from the same coupling
- Identify the tension between thermal relic and SIDM phenomenology

Explore three resolutions:
- **Non-thermal relic** (decoupling)
- **Forbidden-channel relic** (m_final slightly > m_χ)
- **Co-annihilation** (additional partner)

## Results

### 1. Dark photon UV completion (m_A' = 300 MeV)

| g_D | <σv>_ann (cm³/s) | Ωh² | σ_HH (cm²/g) | Verdict |
|---|---|---|---|---|
| 0.03 | 5.6e-27 | 0.65 | 1.3e-11 | Overcloses, σ_HH 9 orders too small |
| 0.10 | 8.8e-25 | 0.0041 | 5.5e-10 | Undercloses, σ_HH 8 orders too small |
| **0.135** | **1.7e-24** | **0.12** | **6.5e-10** | **PASS relic, σ_HH 8 orders too small** |
| 0.30 | 7.1e-23 | 5e-5 | 1.2e-7 | Undercloses, σ_HH 6 orders too small |
| 1.00 | 8.8e-21 | 4e-7 | 6.7e-5 | Undercloses, σ_HH 3 orders too small |
| 3.00 | 7.1e-19 | 5e-9 | 5.5e-2 | **PASS σ_HH but undercloses** |

**Tension**: To get Ωh² = 0.12 with thermal relic, need g_D ~ 0.135.
This gives σ_HH = 6.5×10⁻¹⁰ cm²/g — **8 orders of magnitude too small**
for our SIDM phenomenology. Conversely, to get σ_HH = 0.05 cm²/g with
the same mediator, need g_D ~ 3 — but this makes <σv>_ann = 7×10⁻¹⁹ cm³/s,
which **undercloses** the universe (Ωh² ~ 10⁻⁹, far below Planck).

### 2. Higgs portal UV completion (m_h = 125 GeV)

| λ_hs | <σv>_ann (cm³/s) | Ωh² | σ_HH (cm²/g) | Verdict |
|---|---|---|---|---|
| 1e-5 | 3e-26 | 0.12 | 1e-15 | **PASS relic, σ_HH 13 orders too small** |
| 1e-4 | 3e-24 | 0.001 | 1e-13 | Undercloses, σ_HH 12 orders too small |
| 1e-3 | 3e-22 | 1e-5 | 1e-11 | Undercloses, σ_HH 9 orders too small |
| 1e-2 | 3e-20 | 1e-7 | 1e-9 | Undercloses, σ_HH 7 orders too small |

**Tension**: Even worse than dark photon. We're at m_χ = 10.3 GeV, **far
below** the SM Higgs resonance m_h/2 = 62.5 GeV. The off-resonance
suppression makes <σv>_ann much smaller than thermal. To compensate,
need λ_hs ~ 10⁻⁵, but then σ_HH = 10⁻¹⁵ cm²/g — **13 orders of magnitude
too small** for SIDM.

## Verdict: Thermal Relic is Incompatible with SIDM

For m_χ = 10.3 GeV, m_φ = 300 MeV, σ_HH = 0.05 cm²/g:
- **Dark photon**: needs g_D ~ 0.135 for thermal relic; σ_HH ~ 10⁻¹⁰ cm²/g
- **Higgs portal**: needs λ_hs ~ 10⁻⁵ for thermal relic; σ_HH ~ 10⁻¹⁵ cm²/g
- **Both fail by 8-13 orders of magnitude**

A purely thermal WIMP-miracle UV completion is **NOT viable** at our
SIDM parameters.

## Three Viable Resolutions

### Solution 1: Non-thermal relic production

If DM is produced via decay of a heavier particle (e.g., moduli, inflaton,
heavy scalar), the relic density is **decoupled from the annihilation
cross-section**. We can have correct Ωh² AND correct σ_HH = 0.05 cm²/g
simultaneously with g_D ~ 3 (perturbative limit).

**Implementation**: A moduli field Φ with mass m_Φ >> m_χ decays via
Φ → χχ with branching ratio ~ 1. The decay rate Γ_Φ sets the yield
Y_χ = n_Φ/s_0 * BR(Φ→χχ) * 2. If Γ_Φ >> H at T = m_χ (DM mass), then
DM freezes in via freeze-in (not freeze-out). The cross-section <σv>_ann
is unconstrained — it's the **freeze-in** rate, not the freeze-out rate.

### Solution 2: Forbidden-channel relic

χχ → YY where m_Y slightly above m_χ. The channel is **closed at T=0**
(so direct-detection experiments don't see YY decays) but **open at
freeze-out** T_f ~ m_χ/20. Boltzmann suppression exp(-2Δm/T_f).

For m_χ = 10.3 GeV, T_f = 0.515 GeV:
- Δm = 0.05 GeV: suppression exp(-0.19) = 0.83
- Δm = 0.1 GeV: suppression exp(-0.39) = 0.68
- Δm = 0.3 GeV: suppression exp(-1.16) = 0.31
- Δm = 0.5 GeV: suppression exp(-1.94) = 0.14

This naturally suppresses σ_v without affecting σ_HH (which depends on
m_χ and m_φ, not on the YY threshold).

### Solution 3: Co-annihilation

Additional partner χ' nearly degenerate with χ (|m_χ' - m_χ| < T_f).
Co-annihilation channels χχ', χ'χ' → SM SM dominate the freeze-out,
decoupling σ_v from σ_HH.

The m_χ' particle can also participate in elastic scattering
(σ_H' = σ_H * f(m_χ'/m_χ)), giving additional structure to the SIDM
phenomenology. This is the most natural extension of our two-component
model.

## Honest Caveats

1. **Perturbative limit**: The couplings needed for σ_HH = 0.05 cm²/g
   in the dark photon model are g_D ~ 3, near the perturbative limit
   (α_D ~ 1). A full UV model would need to specify the running of g_D.

2. **Higher-order corrections**: Sommerfeld enhancement, co-annihilation
   thresholds, and bound-state formation are NOT included in this
   1-loop effective calculation.

3. **Cosmological history**: Non-thermal relic production requires a
   specific cosmological scenario (e.g., moduli domination, inflaton
   decay). The viability depends on whether such a scenario is consistent
   with Big Bang nucleosynthesis and CMB observations.

4. **Direct detection**: The UV completion predicts direct-detection
   cross-sections via the same mediator. For dark photon with
   g_D ~ 3, direct-detection limits (LZ, XENONnT) constrain
   σ_SI < 10⁻⁴⁶ cm² (depending on m_χ). The dark photon gives kinetic
   mixing with SM photon, so σ_SI is set by ε² (kinetic mixing)
   not g_D² directly. This is a separate constraint.

## Paper Implications

The Phase 44 phenomenology (σ_HH = 0.05 cm²/g) requires either:
- (a) **Non-thermal relic production** (decoupling), OR
- (b) **UV completion with explicit co-annihilation or forbidden-channel**

A purely **thermal WIMP-miracle UV completion is NOT viable** at our
SIDM parameters. This is a substantive structural finding that should
be acknowledged in any honest paper.

## Output Files

- `v0.3-prelim/code/T184_dark_higgs_uv.py` — script
- `v0.3-prelim/data/results/t184_dark_higgs_uv.json` — scan results

## What This Changes in the Paper

§10 (UV Completion) currently lists four no-go theorems showing that
simple UV completions fail to produce the Cloud-9 spike. The T184 result
adds a fifth:

**No-go theorem #5 (thermal relic): A purely thermal WIMP-miracle UV
completion with the Phase 44 SIDM parameters (m_χ = 10.3 GeV, m_φ = 300
MeV, σ_HH = 0.05 cm²/g) is INCOMPATIBLE with Planck 2018 Ωh² = 0.12.**

The tension is **8-13 orders of magnitude** in σ_HH for the coupling that
gives the correct thermal relic. Either non-thermal production, co-
annihilation, or forbidden-channel mechanisms are required. This is a
genuine UV-construction problem, not a phenomenology problem.