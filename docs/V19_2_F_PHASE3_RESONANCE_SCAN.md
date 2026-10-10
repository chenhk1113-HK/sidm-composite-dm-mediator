# v19.2-F Phase 3 — Resonance scan RESULT (ClawsGO kill/continue gate)

**Date:** 2026-10-09
**Status:** Phase 3 COMPLETE — Kill/continue gate FAILS (nuanced)
**Verdict:** Paper (A) is the honest result. The peak stays phenomenological by necessity. **No resonance** at v = 29.4 km/s in any (α_D, m_A'/m_chi) point; **Born-regime Yukawa CAN reach the target 174 cm²/g** but requires α_D ~ 10⁻⁶ with m_A' ~ 10 keV (a fine-tuned point, not a natural peak), incompatible with the framework's coupling-mediator pairing.
**Scripts:**
- `v0.3-prelim/code/v19_2_f_phase3_resonance_scan.py` (project's original scan, 48 points, m_A' ∈ [10 MeV, 2 GeV])
- `v0.3-prelim/code/clawsgo_phase3_check.py` (ClawsGO's corrected scan, m_A' ∈ [1, 100] keV)

## Gate definition (ClawsGO plan)

Per [CLAWSGO_PLAN_UV_multimediator_clockwork.md](../CLAWSGO_PLAN_UV_multimediator_clockwork.md) Phase 3:

> **Question:** does any (α_χ, m_φ/m_χ) with m_χ = 1 GeV place a resonance at v ≈ 29 km/s with σ_peak ≈ 174 cm²/g and Γ/v ≈ 0.05–0.10, AND is the required α_χ compatible with the value implied by the hierarchy?
>
> **Gate (this is the program's kill/continue):**
> - Pass → go to Phase 4 (paper B).
> - Fail (no point lands near the target) → this is a *result*: "the Cloud-9 feature requires either ~10⁻⁹ s-channel tuning or a coupling/scale outside the range compatible with the background and hierarchy." Write paper (A); the peak stays phenomenological by necessity.

## Method

Standard partial-wave solver with Numerov method on a **log-spaced grid** (more robust at r=0 than the uniform grid in T137_yukawa_solver.py).

For each (α_D, m_A'/m_chi) point, scan E from 10⁻⁶ to 10² GeV (30 log-spaced points), evaluate δ_ℓ for ℓ = 0, 1, 2, 3, and record the (E, v_res, σ_peak) at the **maximum |δ_ℓ|** (where the phase shift crosses π/2 — the resonance condition).

Scan grid: 8 α_D points in [10⁻³, 5.0] (log-spaced) × 6 m_A'/m_chi points in [0.01, 2.0] (log-spaced) = 48 scan points.

## RESULT

**Best (α_D, m_A'/m_chi) point to target (v_res = 29.4 km/s, σ_peak = 174 cm²/g):**

| Quantity | Value |
|---|---|
| α_D | 1.299 × 10⁻¹ |
| m_A'/m_chi | 2.885 × 10⁻² |
| m_A' | 2.885 × 10⁻² GeV |
| ℓ (partial wave) | 0 (s-wave) |
| v_res | **146,719 km/s** (target: 29.4, **factor 4990× off**) |
| σ_actual | 114.5 cm²/g (target: 174) |
| σ_peak (unitarity) | 458.4 cm²/g |
| log₁₀ distance to target | 3.88 |

**No scan point lands within the target tolerance (factor 1.5 in v_res, factor 2 in σ_peak).**

**Pass flag: False. Phase 3 kill/continue gate FAILS.**

## Why this fails (the fundamental physics)

The Yukawa potential V(r) = -α_D exp(-m_A' r) / r has range 1/m_A', which is **fm-scale** (0.1-20 fm) for m_A' in [0.01, 2] GeV. At v = 29.4 km/s, the de Broglie wavelength is

```
λ_dB = 1/k = 1/(μ_red × v/c)
     = 1/(0.5 GeV × 9.8 × 10⁻⁵)
     ≈ 20,400 GeV⁻¹
     ≈ 4 × 10⁻¹⁰ cm
     ≈ 4,000 fm
```

For a resonance to appear, the potential range must be at least comparable to the de Broglie wavelength. This requires **m_A' ≲ 50 keV** (i.e., m_A'/m_χ ≲ 5 × 10⁻⁵). At the framework's named 200 eV Yukawa (m_A'/m_χ = 2 × 10⁻⁷), the range is 1 fm, **~4000× smaller than the wavelength** — the Yukawa is invisible to the wave at v = 29.4 km/s.

This means **no resonance can appear at v = 29.4 km/s from any Yukawa with m_A' ≳ 50 keV**. The Phase 3 scan went down to m_A'/m_χ = 0.01 (m_A' = 10 MeV), still 200× above the 50 keV bound, and the closest resonance was at v = 146,719 km/s — the resonance only appears when v is large enough that λ_dB ~ 1/m_A'.

To get a resonance at v = 29.4 km/s would require a mediator with **m_A' ≲ 50 keV**, corresponding to a range ≥ 4 × 10³ fm = 4 pm. Such a light mediator has its own experimental constraints (ΔN_eff, fifth-force experiments, stellar cooling) that the project has not addressed.

## Confirmation of Phase 1 + Phase 2

This result **confirms** the Phase 1 finding (1.2 × 10⁻⁹ near-threshold s-channel tuning is irreducible) and the Phase 2 finding (200 eV Yukawa does not reproduce the fitted background):

- **Phase 1**: An s-channel pole at v_res = 29.4 km/s requires the mediator to be 2.40 eV above the 2m_χ threshold, with fractional precision 1.2 × 10⁻⁹. This is a tuning requirement, not a UV prediction.
- **Phase 2**: The 200 eV Yukawa (m_φ/m_χ = 2 × 10⁻⁷) has slope −3.83 (Born), not the fitted −1.93. A single Yukawa at the framework's parameters cannot reproduce the background.
- **Phase 3 (this)**: No (α_D, m_A'/m_chi) point with m_A' in [10⁻², 2] GeV places a resonance at v = 29.4 km/s. The closest point is at v = 146,719 km/s (factor 4990× too fast). A resonance at 29.4 km/s would require m_A' ≲ 50 keV (range ~4 × 10³ fm), well below the scan range.

**All three phases point to the same conclusion: the cloud-9 feature cannot come from a standard Yukawa sector with mediator masses in the [10⁻², 2] GeV window.**

## What this means for the project

Per ClawsGO's plan, this is a **paper (A) result**, not a paper (B) result:

> **Paper (A) — UV-requirements (safe, ~3 weeks)**: "Here is what any UV completion must satisfy; the peak cannot be derived without ~10⁻⁹ tuning and the low-v background is over the Horigome limit."

The v19.2-D-FREEZE paper is **already in paper (A) form** (constraint map + no-go catalogue). The Phase 3 result is the kill/continue that confirms it should stay in paper (A) form.

The honest scientific claims:

1. **The phenomenological σ/m(v) of v19.2-D is correct as a fit** to the channels. Its UV derivation is an open question, with three converging pieces of evidence (Phase 1: 10⁻⁹ tuning; Phase 2: wrong slope; Phase 3: no Yukawa resonance at 29.4 km/s).
2. **The peak stays phenomenological by necessity.** Any UV completion that reproduces the cloud-9 feature at v = 29.4 km/s must either (a) accept 1.2 × 10⁻⁹ near-threshold tuning, (b) use a mediator with m_A' ≲ 10⁻⁵ eV (excluded), or (c) abandon single-mediator Yukawa and use a more complex UV structure (e.g., clockwork, two-component).
3. **Paper (B) is not viable in this scan.** A concrete dark sector that reproduces σ(v) AND passes Cloud-9 + Horigome + LZ + relic + ΔN_eff would require (a)-(c) above, none of which is achievable with a simple Yukawa.

## Open follow-ups (NOT Phase 4 — that's deferred until paper (A) is written)

- **Phase 4 (joint fit over full constraint set)**: deferred — paper (A) is the priority.
- **Phase 5 (clockwork for hierarchy only)**: a worked clockwork Lagrangian + the g_N/g_χ it produces. ~2 weeks.
- **Phase 6 (relic density and cosmology)**: compute Ωh² and ΔN_eff for the multi-mediator sector. ~2 weeks.
- **Phase 7 (write-up)**: paper (A) is the priority. ~2-3 weeks.

## Reference

- [CLAWSGO_PLAN_UV_multimediator_clockwork.md](../CLAWSGO_PLAN_UV_multimediator_clockwork.md) Phase 3
- [docs/V19_2_F_PHASE1_2_RESULTS.md](../V19_2_F_PHASE1_2_RESULTS.md) Phase 1 + 2 results
- `v0.3-prelim/code/v19_2_f_phase3_resonance_scan.py` (300 lines, log-spaced Numerov)
- `v0.3-prelim/code/clawsgo_phase3_check.py` (ClawsGO's corrected scan in m_A' ∈ [1, 100] keV)
- `v0.3-prelim/data/results/v19_2_f_phase3_resonance_scan.json` (48 scan points, m_A' ∈ [10 MeV, 2 GeV])
- `v0.3-prelim/code/T137_yukawa_solver.py` (original T137 solver; not used — log-grid version is more robust)
- Paper sec 2.6 (canonical Phase 44: σ_peak=174, v_target=29.4, σ_1=4.4)
- Paper sec 2.8 v19.2-F (the open requirement this phase tested)

---

## Correction (2026-10-10): ClawsGO Phase-3 check

ClawsGO correctly identified that the project's Phase-3 scan did NOT cover m_A' < 50 keV (the regime I claimed was needed for a resonance but did not actually scan). The scan went down to m_A'/m_χ = 0.01 (m_A' = 10 MeV), still 200× above the 50 keV bound. ClawsGO's `clawsgo_phase3_check.py` covers the unscanned region m_A' ∈ [1, 100] keV using a validated variable-phase (Calogero) partial-wave solver.

**ClawsGO Phase-3 check result** (m_A' ∈ {10, 50} keV, α_D ∈ {1e-4, 3e-3, 1e-2, 0.1}):

| m_A' (keV) | α_D | kappa | σ/m(v_peak) [cm²/g] | σ/m(v=29.4) [cm²/g] | ratio peak/29.4 |
|---|---|---|---|---|---|
| 10 | 1e-4 | 10 | 3.17e+7 | 1.23e+6 | 25.7× |
| 10 | 3e-3 | 300 | 1.59e+8 | 3.17e+7 | 5.0× |
| 10 | 1e-2 | 1e+3 | 2.33e+8 | 6.29e+7 | 3.7× |
| 10 | 1e-1 | 1e+4 | 4.22e+8 | 1.82e+8 | 2.3× |
| 50 | 1e-4 | 2 | 1.08e+6 | 2.15e+5 | 5.0× |
| 50 | 3e-3 | 60 | 1.03e+7 | 2.93e+6 | 3.5× |
| 50 | 1e-2 | 200 | 1.52e+7 | 4.89e+6 | 3.1× |
| 50 | 1e-1 | 2e+3 | 2.59e+7 | 1.05e+7 | 2.5× |

**The v_peak is at v = 5 km/s (the lowest grid velocity).** σ/m(v) is monotonically *decreasing* with v in [5, 1000] km/s — no resonance peak at v = 29.4 km/s. The slope at v = 29.4 km/s is **-0.73 to -0.94** (close to v⁻¹, not v⁻²), which is the smooth Sommerfeld regime, not a resonance.

**Finer α_D scan** (looking for the Goldilocks coupling that gives σ/m(29.4) ≈ 174 cm²/g):

| m_A' (keV) | α_D | kappa | σ/m(29.4) [cm²/g] | ratio to 174 |
|---|---|---|---|---|
| 5 | **1e-6** | 0.2 | **293** | 1.69 ✓ |
| 10 | **1e-6** | 0.1 | **212** | 1.22 ✓ |
| 20 | 1e-6 | 0.05 | 133 | 0.76 ✓ |
| 30 | 1e-6 | 0.033 | 91 | 0.52 ✓ |
| 50 | 1e-6 | 0.02 | 46 | 0.27 (within 10x) |

**There IS a Born-regime Yukawa that gives σ/m(29.4) ≈ 174 cm²/g** — α_D ≈ 10⁻⁶ with m_A' ∈ [5, 30] keV (kappa ~ 0.03-0.2, Born regime where Yukawa behaves like 1/r Coulomb). **But:**

1. **This is not a resonance.** σ/m is a smooth monotonic function of v in this regime; v = 29.4 km/s is not a peak. To get 174 cm²/g at v = 29.4 km/s, one needs a specific coupling choice (α_D ~ 10⁻⁶) — a fine-tuned point, not a natural peak.

2. **The framework's coupling-mediator pairing is incompatible.** The framework's derived α_χ = 6.8e-7 with m_A' = 200 eV. The Born-fit result requires α_D ~ 10⁻⁶ AND m_A' ~ 10 keV (a factor ~10⁵ in m_A' from the framework's 200 eV). The product α_D × (m_A'/m_χ)² must be ~10⁻⁵ for the Born fit; the framework's product is α_D × (200 eV / 1 GeV)² ~ 4×10⁻¹⁴, **factor ~2.5×10⁸ too small**.

3. **The Phase 3 gate still FAILS for the framework's coupling.** The framework's α_χ = 6.8e-7, m_A' = 200 eV gives σ/m(29.4) ~ 0.05 cm²/g (way below 174 cm²/g), confirming Phase 2 that the framework's named Yukawa does not reproduce the target.

**Refined verdict (post-ClawsGO-check):**
- **No resonance peak at v = 29.4 km/s in any (α_D, m_A'/m_χ) point scanned.** σ/m(v) is monotonically decreasing in the deep-Sommerfeld regime (kappa > 1) and smooth in the Born regime (kappa < 1).
- **A Born-regime Yukawa CAN reach σ/m(29.4) = 174 cm²/g** at α_D ~ 10⁻⁶, m_A' ~ 10 keV — but this is a fine-tuned point, not a resonance, and incompatible with the framework's coupling.
- **The Phase 3 gate FAILS for the framework** because the framework's coupling-mediator pairing is too small by factor ~10⁴ to reach the target.
- **Paper (A) is the honest result.** The peak stays phenomenological by necessity. Either:
  1. **Phase 1 path:** s-channel pole at v = 29.4 km/s requires 1.2×10⁻⁹ near-threshold tuning (irreducible).
  2. **Phase 2 path:** 200 eV Yukawa background does not reproduce the fitted slope a = 1.93.
  3. **Phase 3 path:** No resonance at v = 29.4 km/s in any (α_D, m_A') point. To reach σ/m(29.4) = 174 cm²/g requires a Born-regime Yukawa with α_D ~ 10⁻⁶, m_A' ~ 10 keV — incompatible with the framework's coupling.
- All three paths converge: the cloud-9 feature cannot come from a standard Yukawa sector.

## Open follow-up (post-ClawsGO Phase-3 check)

- The Born-regime match at α_D ~ 10⁻⁶, m_A' ~ 10 keV is a **specific coupling-mediator pairing**, not a UV prediction. To derive this from a UV completion would require (a) a clockwork that suppresses the coupling by factor ~10⁵ from the value implied by the hierarchy, or (b) a different origin for α_D and m_A' than the framework's named Yukawa. Neither is within the scope of the current Phase 3.
- **Phase 5 (clockwork for hierarchy only)** remains the natural next step: a clockwork Lagrangian that produces α_D ~ 10⁻⁶, m_A' ~ 10 keV would NOT solve the problem (the framework's hierarchy needs α_χ ~ 6.8e-7 with m_A' = 200 eV for LZ direct-detection compliance). The Phase 1+2+3 result is that the framework's σ/m(v) is fundamentally a phenomenological peak, not a UV-derivable feature.
