# Referee Response: Major Revision Required

**Reviewer:** Anonymous (Referee Report.docx, 2026-09-19)
**Paper:** Multi-Component SIDM with Hidden U(1) UV Completion (v1.13.5)
**Decision:** Major revision required — three of the abstract's pillars do not survive scrutiny.

---

## Executive Summary

The referee is **correct on all three make-or-break items (M1, M2, M3)**. The Hidden U(1) + pseudo-Dirac UV completion with Δm = 10 MeV does NOT preserve self-interaction at galactic velocities; the ΔBIC = -170 is a scoring rule, not a likelihood; and the α_slope = 0.5 "UV verification" is a tautology. We accept these findings and outline what needs to change before resubmission.

This document does **not** attempt to defend claims we now know are broken. It acknowledges them, verifies them independently, and proposes concrete next steps.

---

## M1: Hidden U(1) self-interaction is kinematically forbidden — REFEREE IS CORRECT

### Independent verification

We independently computed KE_CM for the four channels of interest:

| Channel | v (km/s) | KE_CM (eV) | Δm / KE_CM | Verdict |
|---|---|---|---|---|
| Cloud-9 (UDG) | 28 | 23.3 | **4.29 × 10⁵** | **FORBIDDEN** |
| dSph (core) | 15 | 6.7 | 1.49 × 10⁶ | **FORBIDDEN** |
| UFD (edge) | 7 | 1.46 | 6.86 × 10⁶ | **FORBIDDEN** |
| UFD (deep) | 3 | 0.27 | 3.73 × 10⁷ | **FORBIDDEN** |
| SPARC (L*) | 100 | 297 | 3.36 × 10⁴ | **FORBIDDEN** |
| Cluster (BCG) | 500 | 7440 | 1.34 × 10³ | **FORBIDDEN** |

**At every astrophysically relevant velocity, Δm = 10 MeV exceeds the available CM kinetic energy by 3-7 orders of magnitude.**

### The V_max error

We previously claimed `V_max = α_D × m_χ ≈ 16 MeV > Δm`. The referee correctly identifies that this formula is wrong.

We then investigated Zhang 2016's actual paper. The correct formula is `V_max ~ α_D² × m_χ`, NOT α_D × m_χ (our claim) and NOT α_D × m_φ (referee's correction):

- **Our (wrong) claim**: V_max = α_D × m_χ = 0.0015 × 10.7 GeV = **16.05 MeV**
- **Referee (closer but still wrong)**: V_max = α_D × m_φ = 0.0015 × 30 MeV = **0.045 MeV**
- **Zhang 2016 actual formula**: V_max = α_D² × m_χ = 0.0015² × 10.7 GeV = **0.0241 MeV**

Our formula overstated the well depth by a factor of `m_χ/m_φ ≈ 357`; the referee's correction by `1/α_D ≈ 667`.

### Zhang 2016's actual claim

Zhang 2016 explicitly identifies the allowed parameter regime: **self-interaction is preserved when Δm ≲ α_D² × m_χ**. For our parameters, this means:

- **Allowed regime**: Δm < α_D² × m_χ = **24.1 keV**
- **Our choice**: Δm = 10 MeV
- **Ratio**: Our Δm is **415× beyond** Zhang's allowed regime

This is consistent with Zhang's own conclusion:

> "If we further increase the mass splitting beyond α²_D m_D, the quantum mechanical effect stops being effective. As a result, the up-scattering is forbidden everywhere and the dark matter self-interaction potential becomes genuinely loop suppressed."

**We chose parameters exactly in the regime where Zhang 2016's mechanism does not work.**

### The deeper issue

With V_max = 0.045 MeV ≪ Δm = 10 MeV:
1. Tree-level χ₁χ₁ → χ₁χ₁ (elastic) is **loop-suppressed** (off-diagonal-only coupling)
2. χ₁χ₁ → χ₂χ₂ (inelastic) is **kinematically forbidden** (Δm >> KE_CM)
3. There is **no tree-level contribution** to σ_DM-DM/m at galactic velocities

**Therefore σ_DM-DM/m ≈ 0.044 cm²/g cannot come from this UV completion.** The whole T120.11 → T120.15.B chain collapses.

### Why this happened

We did not check the kinematic threshold before claiming σ_DM-DM/m ≈ 0.044 cm²/g. This is the standard "scale check" that should have been the first calculation. We deferred to Zhang 2016's formulation without verifying that the regime he considered (early-universe, high-v) actually applies at galactic velocities.

### Recovery paths

We now have three options, ordered by feasibility:

**(a) Drop the pseudo-Dirac splitting entirely and use a different DD-evasion mechanism.** The simplest honest path: pure elastic mediator (no Majorana mass), with DD evasion via a different mechanism (e.g. blind mediator, anapole moment, magnetic dipole moment — though we showed the latter is RULED OUT in T120.10). This requires finding a mechanism that:
- Preserves σ_DM-DM/m ~ 0.04 cm²/g at v = 100 km/s (Cloud-9, SPARC)
- Has σ_SI below LZ 2024 limit (9.4 × 10⁻⁴⁷ cm²)
- Does not require a 10 MeV Majorana mass

**(b) Reduce Δm to keV scale and find alternative DD evasion.** Per Zhang 2016's actual regime, Δm ≈ 24 keV is the maximum allowed for self-interaction preservation. At this scale, DD evasion no longer works via kinematic forbiddance (since DD recoil energy is also ~100 keV). A different evasion mechanism is needed — possibly momentum-suppressed scattering, blind mediator, or inelastic-nuclear recoil.

**(c) Retire the UV completion claim.** Keep the phenomenology (multi-resonance + two-component + gravothermal) and present v1.13.5 as a **phenomenology paper without UV completion**. This is the most honest path given current state. The phenomenology still satisfies all 8 observational constraints.

### Our recommendation

**Pursue (c) immediately**, then (a) in parallel. (b) requires more theoretical work and is the longest path.

The Hidden U(1) + pseudo-Dirac + 10 MeV parameter choice was a mistake. We chose Δm = 10 MeV because it neatly evaded DD (~100 keV recoil vs 10⁷ eV threshold), but did not verify that this regime is consistent with Zhang's mechanism for self-interaction preservation. **The first calculation should have been the kinematic threshold check.**

---

## M2: ΔBIC = -170 is a scoring rule, not a likelihood — REFEREE IS CORRECT

### The problem

Our "logL" was constructed as:
- +1.0 per passing data point
- -1.8 to -2.5 per failing data point

These are **arbitrary scores, not probability densities**. A legitimate BIC requires a maximized log-likelihood from an actual probability model with units.

The referee's circularity argument is also valid: T120 was engineered to pass the 31 dSph/UFD points, then declared the winner because it passes them.

### Recovery paths

**(a) Use real per-point likelihoods.** A Gaussian likelihood with measurement uncertainty for σ/m measurements; a one-sided limit likelihood (truncated Gaussian or half-Cauchy) for the Horigome/Ando upper limits. Compute maximized logL from these.

**(b) Use the SPARC forward model.** Per Phase 47 LOO analysis, SPARC drives the +8 log-unit gain. A proper forward model of the SPARC rotation-curve sample (mass-model likelihood with baryonic priors) would give a defensible BIC.

**(c) Drop the BIC claim entirely.** Present the model as "passes all 8 constraints" without quantifying statistical evidence vs simpler baselines. This is honest given current state.

---

## M3: The α = 0.5 "UV verification" is a tautology — REFEREE IS CORRECT

### The problem

§9.8.4's table compared:
- Column A: σ/m computed from `zhang2016_self_scattering(v)`
- Column B: `(100/v)^0.5 × 0.766`

These matched to 4 decimals because **Column B is exactly Column A's analytic form**. We did not independently compute σ/m(v) and then fit a power law; we generated data from the power law and showed it fits itself. R² = 1.0 by construction.

The "v^(3/2) factor" that converts Born slope 2 → 0.5 was asserted without derivation. The full derivation in `T120_15_UV_SLOPE_DERIVATION.md` (cited as containing it) does **not actually derive this factor**; it asserts it.

### Recovery paths

**(a) Numerically compute σ/m(v) from the actual pseudo-Dirac potential.** Start with `V(r) = (α_D / r) × [exp(-m_φ r) × M₁(r)]` where M₁(r) is the off-diagonal matrix element; solve the Schrödinger equation; integrate over impact parameter. Then fit a power law. The fit will NOT match to 4 decimals (it won't be a pure power law). That's the honest result.

**(b) Show the matrix-element derivation.** Starting from `M[χ₁(p₁)χ₁(p₂) → χ₂(p₃)χ₂(p₄)]`, derive the v^(3/2) factor explicitly. This is a real computation, not an assertion.

**(c) Acknowledge the slope is phenomenologically tuned.** The Hidden U(1) model does predict a slope, but it's the **transition** slope between Born (2) and saturated (0), which depends on α_D sitting in a specific range. So α_slope = 0.5 is conditional, not unique.

---

## M4-M7: Also valid

- **M4 (v₂-v₄ are not resonances)**: Correct. Breit-Wigner is strictly positive; cannot suppress. Either call them what they are (interpolation) or remove them.
- **M5 (SPARC gain is binary)**: Correct. Per Phase 47 §4.1, SPARC score is "175 pass/fail at fixed σ/m."
- **M6 (inconsistent parameter counting)**: Correct. 15/18/5 quotes contradict. Need a single definitive ledger.
- **M7 (three incompatible benchmarks)**: Correct. master (770 GeV), T90 cloud-9 (6-7 GeV), T120 Hidden U(1) (10.7 GeV) all coexist. A reader cannot tell which is "the model."

---

## Minor issues: also valid

- "8 constraints" overstates independence (Horigome/Ando is one dataset → 4-5 truly independent)
- Cloud-9 σ/m = 100 is internal target = 2× published floor (should also quote against 50)
- §9.8.4 typo: 0.766 vs 0.0766
- T101.4 √2 error — worth a sanity pass over other ½/¼ factors

---

## Honest assessment

The referee's overall verdict — **"Major revision — not ready as is"** — is correct.

The v1.13.5 abstract's three pillars:

| Pillar | Status |
|---|---|
| ΔBIC = -170 vs Phase 44 | **INVALID** (scoring rule) |
| σ_SI 2400× below LZ | **Math right but for a model that doesn't work** |
| UV-derived α = 0.5 | **Tautology** (fitted to itself) |

are not on firm ground. The science is interesting and the project's culture of self-falsification is genuine, but **the abstract overstates what is currently proven**.

---

## Proposed next steps

**Phase A (immediate):**
1. Add a banner to v1.13.5 marking it as **failing referee review** and superseded
2. Add this document as `REFEREE_RESPONSE_v1.md` and a `CHANGELOG_v1.13.6_FALSIFIED.md`
3. Mark v1.13.5 as "RETIRED — see referee response" in README and paper status line

**Phase B (M1 investigation):**
4. Investigate Δm ≈ keV-scale pseudo-Dirac (per Brahma 2024 [48])
5. If keV-scale works, redo the UV completion with proper kinematic analysis
6. If not, retire the Hidden U(1) UV completion

**Phase C (statistical machinery):**
7. Build real per-point Gaussian/half-Cauchy likelihoods
8. Build SPARC forward model
9. Recompute BIC with real likelihoods

**Phase D (presentation):**
10. Single parameter ledger (resolve M6)
11. Single benchmark choice (resolve M7)
12. Honest framing of phenomenology vs UV claims

---

## What v1.13.5 SHOULD have said (in retrospect)

A defensible v1.13.5 might read:

> "We present a phenomenology of multi-component SIDM that satisfies 8 observational constraints. The velocity slope α_slope ≈ 1 is a phenomenologically-tuned compromise that satisfies all 8 channels. We do not claim a UV completion at this stage; the multi-channel convergence is suggestive but not proof of a specific UV model."

This would have been honest, defensible, and not required retraction.

---

## Acknowledgment

The referee's identification of M1 (the V_max formula error and the kinematic threshold) is **exactly the kind of self-falsification** the project has committed to throughout. We thank the referee for catching what should have been the first calculation done. The next iteration will treat this kind of scale-check as the first step, not the last.
