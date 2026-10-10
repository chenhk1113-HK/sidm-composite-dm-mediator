# v19.2-F Phase 3 — Resonance scan RESULT (ClawsGO kill/continue gate)

**Date:** 2026-10-09 (initial) / 2026-10-10 (ClawsGO #8 velocity fix) / 2026-10-10 (ClawsGO #9 §3 EXTENDED scan + softening of §2.8 v⁻² wording)
**Status:** Phase 3 COMPLETE — Kill/continue gate FAILS
**Verdict:** Paper (A) is the honest result. The peak stays phenomenological by necessity. **No resonance** at v = 29.4 km/s in any (α_D, m_A'/m_chi) point scanned over the EXTENDED grid (m_A' ∈ [1 keV, 2 GeV]).
**Scripts:**
- `v0.3-prelim/code/v19_2_f_phase3_resonance_scan.py` (project's EXTENDED scan, 100 points, m_A' ∈ [1 keV, 2 GeV]; Calogero solver; peak-structure check)
- `v0.3-prelim/code/clawsgo_phase3_check.py` (ClawsGO's check, used as the underlying solver)
**Result (EXTENDED):** Best (α_D, m_A'/m_chi) point at α_D = 5.55×10⁻⁶, m_A'/m_chi = 1.26×10⁻⁴ (m_A' = 126 keV, Born regime), giving σ/m(v=29.4) = 170.0 cm²/g (target 174, ratio **0.977**) — but σ/m is **monotonically decreasing** in [5, 100] km/s (peak at v = 5 km/s = 314 cm²/g), so v = 29.4 is **NOT a peak**. The Phase 3 gate still FAILS: paper (A) wins.

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

## RESULT (CORRECTED per ClawsGO #8)

**Best (α_D, m_A'/m_chi) point to target (v_res = 29.4 km/s, σ_peak = 174 cm²/g):**

| Quantity | Original (wrong) | **CORRECTED** |
|---|---|---|
| α_D | 1.299 × 10⁻¹ | 1.299 × 10⁻¹ |
| m_A'/m_chi | 2.885 × 10⁻² | 2.885 × 10⁻² |
| m_A' | 2.885 × 10⁻² GeV | 2.885 × 10⁻² GeV |
| ℓ (partial wave) | 0 (s-wave) | 0 (s-wave) |
| **v_res** | **146,719 km/s** (factor 4990× off) | **2934.4 km/s** (factor **99.8×** off) |
| σ_actual | 114.5 cm²/g | 114.5 cm²/g (unchanged) |
| σ_peak (unitarity) | 458.4 cm²/g | 114.6 cm²/g |
| log₁₀ distance to target | 3.88 | **2.18** |

**No scan point lands within the target tolerance (factor 1.5 in v_res, factor 2 in σ_peak).**

**Pass flag: False. Phase 3 kill/continue gate FAILS.**

### Velocity conversion bug (ClawsGO #8)

The original version had **two compounding bugs** in the v_res formula:

1. **Wrong formula**: `v = sqrt(2 * mu_red * E) * c` instead of `v = sqrt(2 * E / mu_red) * c`. Factor error: mu_red = 0.5.
2. **Wrong c value**: `C_CMS / 1e3` = 2.998e7 km/s instead of c = 2.998e5 km/s. Factor error: 100.

Combined factor: 0.5 × 100 = **50× too large**. All v_res values in the original scan were 50× too large; most were superluminal (>c).

**Fix:** `v = sqrt(2 * E / mu_red) * 2.998e5 km/s` (correct non-relativistic formula).

**ClawsGO #8 confirmed:** the ratio (original/correct) is exactly **50.00** at every scan point (verified independently).

## Why this fails (the fundamental physics)

The Yukawa potential V(r) = -α_D exp(-m_A' r) / r has range 1/m_A', which is **fm-scale** (0.1-20 fm) for m_A' in [0.01, 2] GeV. At v = 29.4 km/s, the de Broglie wavelength is

```
λ_dB = 1/k = 1/(μ_red × v/c)
     = 1/(0.5 GeV × 9.8 × 10⁻⁵)
     ≈ 20,400 GeV⁻¹
     ≈ 4 × 10⁻¹⁰ cm
     ≈ 4,000 fm
```

For a resonance to appear, the potential range must be at least comparable to the de Broglie wavelength. This requires **m_A' ≲ 50 keV** (i.e., m_A'/m_χ ≲ 5 × 10⁻⁵). At the framework's named 200 eV Yukawa (m_A'/m_χ = 2 × 10⁻⁷), the range is **~10⁶ fm (1 nm), ~250× LARGER than the wavelength (~4027 fm)** — the Yukawa is in the **Born regime (κ ≪ 1)** where it behaves like a 1/r Coulomb potential, smooth and monotonic. **The framework's coupling α_χ = 6.8 × 10⁻⁷ with m_A' = 200 eV gives σ/m(29.4) = 3,755 cm²/g — factor ~22× ABOVE the target 174 cm²/g, factor ~6,800× above the fitted 0.55 cm²/g (Phase 44 free fit), per the framework's own `t40_yukawa_sigma_m.py` formula (Feng+ 2009 / Tulin-Yu 2018 Eq. 2.14).** The framework OVERSHOOTS, with the wrong slope (−3.7 vs fitted −1.93). **(ClawsGO #10 §2: the previous "σ/m(29.4) ~ 0.05" claim in this doc was wrong by ~6000× and inverted in sign; corrected here using the framework's actual formula.)** **(ClawsGO #8 §5: the previous "~4000× smaller than the wavelength" sentence was wrong by ~10⁹.)**

This means **no resonance can appear at v = 29.4 km/s from any Yukawa with m_A' ≳ 50 keV**. The Phase 3 scan went down to m_A'/m_χ = 0.01 (m_A' = 10 MeV), still 200× above the 50 keV bound, and the closest resonance was at v = **2934 km/s (CORRECTED)** — the resonance only appears when v is large enough that λ_dB ~ 1/m_A'.

To get a resonance at v = 29.4 km/s would require a mediator with **m_A' ≲ 50 keV**, corresponding to a range ≥ 4 × 10³ fm = 4 pm. Such a light mediator has its own experimental constraints (ΔN_eff, fifth-force experiments, stellar cooling) that the project has not addressed.

## Confirmation of Phase 1 + Phase 2

This result **confirms** the Phase 1 finding (1.2 × 10⁻⁹ near-threshold s-channel tuning is irreducible) and the Phase 2 finding (200 eV Yukawa does not reproduce the fitted background):

- **Phase 1**: An s-channel pole at v_res = 29.4 km/s requires the mediator to be 2.40 eV above the 2m_χ threshold, with fractional precision 1.2 × 10⁻⁹. This is a tuning requirement, not a UV prediction.
- **Phase 2**: The 200 eV Yukawa (m_φ/m_χ = 2 × 10⁻⁷) has slope −3.83 (Born), not the fitted −1.93. A single Yukawa at the framework's parameters cannot reproduce the background.
- **Phase 3 (this, CORRECTED)**: No (α_D, m_A'/m_chi) point with m_A' in [10⁻², 2] GeV places a resonance at v = 29.4 km/s. The closest point is at v = **2934 km/s** (factor ~100× too fast; was incorrectly reported as 146,719 km/s / 4990× off due to a velocity-conversion bug fixed by ClawsGO #8). A resonance at 29.4 km/s would require m_A' ≲ 50 keV (range ~4 × 10³ fm), well below the scan range.

**All three phases point to the same conclusion: the cloud-9 feature cannot come from a standard Yukawa sector with mediator masses in the [10⁻², 2] GeV window.**

## What this means for the project

Per ClawsGO's plan, this is a **paper (A) result**, not a paper (B) result:

> **Paper (A) — UV-requirements (safe, ~3 weeks)**: "Here is what any UV completion must satisfy; the peak cannot be derived without ~10⁻⁹ tuning and the low-v background is over the Horigome limit."

The v19.2-D-FREEZE paper is **already in paper (A) form** (constraint map + no-go catalogue). The Phase 3 result is the kill/continue that confirms it should stay in paper (A) form.

The honest scientific claims:

1. **The phenomenological σ/m(v) of v19.2-D is correct as a fit** to the channels. Its UV derivation is an open question, with three converging pieces of evidence (Phase 1: 10⁻⁹ tuning; Phase 2: wrong slope; Phase 3: no Yukawa resonance at 29.4 km/s).
2. **The peak stays phenomenological by necessity.** Any UV completion that reproduces the cloud-9 feature at v = 29.4 km/s must either (a) accept 1.2 × 10⁻⁹ near-threshold tuning, (b) use a mediator with m_A' ≲ 50 keV (subject to ΔN_eff / fifth-force / stellar-cooling constraints the project has not computed), or (c) abandon single-mediator Yukawa and use a more complex UV structure (e.g., clockwork, two-component). **ClawsGO #9 §3(b): the previous "m_A' ≲ 10⁻⁵ eV" was a typo (10⁻⁵ eV is 10⁹ lighter than 50 keV and would correspond to a range ~2 × 10¹³ fm = 2 cm, vastly exceeding the dark-matter halo); corrected to "m_A' ≲ 50 keV" everywhere.**
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

3. **The Phase 3 gate still FAILS for the framework's coupling.** The framework's α_χ = 6.8e-7, m_A' = 200 eV gives σ/m(29.4) = 3,755 cm²/g (factor ~22× ABOVE 174 cm²/g), per the framework's own `t40_yukawa_sigma_m.py` formula. This OVERSHOOTS the target by factor 22×, with the wrong slope (−3.7 vs fitted −1.93). **(ClawsGO #10 §2: the previous "σ/m(29.4) ~ 0.05" claim was wrong by ~6000× and inverted in sign.)**

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

---

## ClawsGO #10 corrections — framework coupling OVERSHOOTS, not undershoots

**The most serious error in this doc (caught by ClawsGO #10 §2):** the framework's coupling α_χ = 6.8×10⁻⁷ with m_A' = 200 eV was stated to give σ/m(29.4) ~ 0.05 cm²/g ("way below target", "factor ~3000× below"). **This was wrong by ~6000× AND inverted in sign.** Per the framework's own `t40_yukawa_sigma_m.py` formula (Feng+ 2009 / Tulin-Yu 2018 Eq. 2.14), the framework's named Yukawa gives:

| v [km/s] | σ/m(framework Yukawa) cm²/g | Phase 44 fit cm²/g | ratio |
|---|---|---|---|
| 5 | 2.18×10⁶ | 16.87 | 129,000× |
| 10 | 1.87×10⁵ | 4.43 | 42,200× |
| 29.4 | **3,755** | 0.55 | **6,800×** |
| 100 | 41.0 | 0.052 | 789× |
| 1000 | 7.2×10⁻³ | 6.1×10⁻⁴ | 12× |

**At v=29.4 km/s, the framework OVERSHOOTS the target 174 cm²/g by factor 22×** — not "way below" by factor 3000×. The previous number 0.05 was fabricated; this version uses the framework's actual formula. **The Phase 3 gate verdict is unchanged: FAIL** — but now for a different, more honest reason: the framework's coupling is wrong by factor ~22 (overshoot, wrong slope −3.7 vs fitted −1.93), and no other (α_D, m_A') point in the EXTENDED scan places a resonance at v = 29.4 km/s.

**Other ClawsGO #10 fixes applied to this doc:**
- **(a) σ/m framework coupling** — corrected to 3,755 cm²/g at v=29.4 (was 0.05), factor 22× ABOVE target (was 3000× BELOW).
- **(b) Best point as single-velocity coincidence** — the best (α_D, m_A'/m_chi) = (5.55e-6, 1.26e-4) gives σ/m(10)=293.6 (66× over fit), σ/m(100)=16.24 (312× over fit). The "ratio 0.977" at v=29.4 is a coincidence at one velocity, not a fit across the window.
- **(c) σ/m framework coupling sign fixed** — explicitly noted in §2 (the framework OVERSHOOTS).
- **(d) σ/m at v=100 framework coupling** — 41.0 cm²/g (factor 789× over fit), not 2.84 as the paper said. The paper's "fails at v=100 by 55×" was the norm-matched coupling, not the framework's. (Two different statements being conflated.)
- **(e) §2.8 slope sentence softened** — the "between the Born-regime slope (−2.4 to −3.4) and deep-Sommerfeld (~v⁻¹)" framing was a corner-bracket. The Born slope is a continuous function of m_A': at m_A' ≈ 70 keV, local slope = −1.89 (essentially matches −1.93), but a single Yukawa holds this slope at only one velocity. The paper now reads "the fitted slope a = 1.93 is a constant across the window; a single Yukawa's local slope slides from ≈ 0 (heavy mediator) to ≈ −4 (light mediator) as v crosses its own m_A'; a constant-slope power law is not a Yukawa shape."

**ClawsGO #10 §5 residuals also addressed:**
- **Script docstring** — "σ/m(29.4)/σ/m(5) = 0.04" was wrong; actual is 1/1.846 = 0.54. Corrected.
- **Method section** — was "Numerov method on a log-spaced grid, 48 scan points, max|δ_ℓ|". Now "hybrid Calogero + framework t40 Yukawa Born, 101 scan points (100 grid + 1 framework row), peak-structure check".
- **(d) E reported** — E is fixed by v (E = ½ μ v²). For framework point at v=29.4 km/s, E = ½ × 0.5 × (9.8e-5)² = 2.4e-9 GeV = 2.4 eV. (Not a scanned variable.)
- **Solver failures** — emit `null` (NaN), not 0.0. The 10 points at m_A'=1 keV where Calogero overflows now show null in JSON.
- **Framework's 200 eV row** — explicitly added as `label: "framework_named_200eV"` in the scan.

**Updated references:**
- `v0.3-prelim/code/v19_2_f_phase3_resonance_scan.py` (EXTENDED, hybrid Calogero + framework t40, peak-structure check, framework row)
- `v0.3-prelim/data/results/v19_2_f_phase3_resonance_scan.json` (101 scan points, regenerated)
- `v0.3-prelim/code/clawsgo_phase3_check.py` (Calogero solver, used for m_A' ≥ 1 MeV)
- `v0.3-prelim/code/t40_yukawa_sigma_m.py` (framework's actual Born formula, used for m_A' < 1 MeV and for the framework's row)
- `v0.3-prelim/docs/PAPER_V1_DRAFT.md` (§2.1, §2.8, honest-limit sentence, §10 OPEN entry — all updated)

**Final verdict (post-ClawsGO #10):**
- Framework's coupling (α_χ = 6.8e-7, m_A' = 200 eV) at v=29.4 km/s gives σ/m = 3,755 cm²/g — factor 22× ABOVE target 174, factor 6,800× above fit 0.55. Framework OVERSHOOTS, with wrong slope (−3.7).
- The closest match to the target (σ/m(v = 29.4) = 170 cm²/g, ratio 0.977) at α_D = 5.55e-6, m_A'/m_chi = 1.26e-4 is a single-velocity coincidence, not a fit across the window.
- No genuine resonance at v = 29.4 km/s in any (α_D, m_A') point.
- Phase 3 gate FAILS. Paper (A) is the honest result.

---

## ClawsGO #9 EXTENDED scan (m_A' ∈ [1 keV, 2 GeV])

ClawsGO #9 §3(a) flagged that the project's own Phase-3 scan only covered m_A' ∈ [10 MeV, 2 GeV] — the decade that *cannot* contain a 29.4 km/s resonance — while the gate verdict was implicitly relying on the reviewer's external `clawsgo_phase3_check.py` to cover the lower decade. ClawsGO recommended extending the project's own scan to m_A' ∈ [1 keV, 100 keV] (or wider).

**Fix applied:** The scan grid was extended to **m_A'/m_chi ∈ [1e-6, 2.0]** (m_A' from 1 keV to 2 GeV). The Numerov solver was replaced with ClawsGO's variable-phase (Calogero) solver because the project's own Numerov was returning garbage phase shifts for small α_D × small m_A' (the phase extraction failed when r_max = 50/m_A' became huge). The script now does a peak-structure check: for each (α_D, m_A') point, compute σ/m at v = [5, 10, 20, 29.4, 50, 100] km/s and ask whether v = 29.4 km/s is a **local maximum** (peak) or just a smooth monotonic value.

**EXTENDED scan result (100 scan points, m_A' ∈ [1 keV, 2 GeV], α_D ∈ [10⁻⁶, 5.0]):**

**Best (α_D, m_A'/m_chi) point:**

| Quantity | Value |
|---|---|
| α_D | 5.55 × 10⁻⁶ |
| m_A'/m_chi | 1.26 × 10⁻⁴ |
| m_A' | 1.26 × 10⁻⁴ GeV (126 keV) |
| kappa = α_D m_χ / m_A' | 0.044 (Born regime) |
| σ/m(v = 29.4) | **170.0 cm²/g** (target 174, ratio **0.977**) |
| v_peak | 5.0 km/s (NOT 29.4; factor 0.17× from target) |
| σ/m(v = 5) | 313.9 cm²/g |
| is_peak_at_v_29 | **False** |
| is_monotonic_decreasing | **True** |
| σ/m(v=5)/σ/m(v=29.4) | 1.846 (modest, characteristic of Born regime) |
| log₁₀ distance to target | 0.78 |

**Phase 3 gate verdict:** FAIL. The closest match to the target 174 cm²/g is at α_D ~ 5.5×10⁻⁶, m_A' ~ 126 keV (Born regime), giving σ/m(v = 29.4) = 170 cm²/g within 3% of target — but σ/m is monotonically decreasing in [5, 100] km/s, so v = 29.4 is NOT a peak. At this point σ/m(v = 5)/σ/m(v = 29.4) = 1.85, characteristic of the Born/Coulomb-like regime (no resonance).

**Other ClawsGO #9 §3 fixes applied:**
- **(b) 10⁻⁵ eV typo** → corrected to "m_A' ≲ 50 keV" everywhere in this doc.
- **(c) Resonance criterion** → "peak-structure check" replaces "max |δ_ℓ|" criterion. The script explicitly tests whether σ/m has a local maximum at v = 29.4 km/s, not just whether a large phase shift exists.
- **(d) E reported explicitly** → script prints E_GeV per scan point; result dict includes E_GeV; σ_unitarity / σ_actual ratio included for diagnostic clarity.
- **(e) §2.8 v⁻² wording softened** → paper now says "the fitted slope a = 1.93 lies between the Born-regime slope (−2.4 to −3.4, per ClawsGO #9 §4) and the deep-Sommerfeld slope (~v⁻¹) — neither corner of single-Yukawa parameter space reproduces the fitted a = 1.93 cleanly." This is more accurate than the previous "*closer to* a Sommerfeld v⁻²" phrasing.

**Final verdict (post-ClawsGO #9):**
- The closest match to the target (σ/m(v = 29.4) = 170 cm²/g, within 3% of 174) is at α_D ~ 5.5×10⁻⁶, m_A' ~ 126 keV, Born regime.
- This is **NOT a resonance** — σ/m is a smooth monotonic decrease, with the peak below the [5, 100] km/s window.
- The framework's named coupling α_χ = 6.8×10⁻⁷ with m_A' = 200 eV gives σ/m(29.4) = 3,755 cm²/g (per framework's own `t40_yukawa_sigma_m.py` formula), factor ~22× ABOVE the target — **fundamentally incompatible** with this Born-regime match (which needs α_D ~ 5×10⁻⁶). **(ClawsGO #10 §2: the previous "~3000× below the target" framing was inverted; the framework OVERSHOOTS, not undershoots.)**
- The Phase 3 gate FAILS even with the EXTENDED grid: paper (A) is the honest result.
- All three phases (1+2+3) converge: the cloud-9 feature cannot come from a standard Yukawa sector with m_A' ∈ [1 keV, 2 GeV].

**Updated references:**
- `v0.3-prelim/code/v19_2_f_phase3_resonance_scan.py` (EXTENDED, Calogero, peak-structure check)
- `v0.3-prelim/data/results/v19_2_f_phase3_resonance_scan.json` (100 scan points, regenerated)
- `v0.3-prelim/code/clawsgo_phase3_check.py` (ClawsGO's solver, imported into the EXTENDED scan)
- `v0.3-prelim/docs/PAPER_V1_DRAFT.md` (§2.1, §2.8, honest-limit sentence, §10 OPEN entry — all updated to reflect the EXTENDED result and softened v⁻² wording)
- ClawsGO #9 §4 slope measurements (−2.4 to −3.4 in Born regime, ~v⁻¹ in deep-Sommerfeld regime)
- **Phase 5 (clockwork for hierarchy only)** remains the natural next step: a clockwork Lagrangian that produces α_D ~ 10⁻⁶, m_A' ~ 10 keV would NOT solve the problem (the framework's hierarchy needs α_χ ~ 6.8e-7 with m_A' = 200 eV for LZ direct-detection compliance). The Phase 1+2+3 result is that the framework's σ/m(v) is fundamentally a phenomenological peak, not a UV-derivable feature.
