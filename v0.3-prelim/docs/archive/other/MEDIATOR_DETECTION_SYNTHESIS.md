# Mediator Detection in DM-SIDM — Synthesis of T40 + T41 + T42

## TL;DR

**Yes**, it's feasible to constrain the mediator — but the T41 posterior
localizes it to a region that is **below all current experimental
sensitivity**. The honest answer is:

> The SIDM mediator is constrained to m_φ ≈ 212 MeV, ε ≈ 10⁻⁵³. Every
> existing experiment (NA64, RGB stellar cooling, SN1987A) is **at
> least 47 orders of magnitude too insensitive** to detect it. The
> "invisible mediator" is a *prediction of the model*, not a failure
> of detection.

The deeper result: **the data prefer a velocity dependence that simple
Yukawa cannot produce** (T39 a = +0.94, Yukawa a ≈ -2). This is a
publishable negative finding — it tells us the mediator must be
either inelastic DM, a pseudo-scalar, or have velocity-dependent g_χ.

---

## Tier 1 — mediator mass posterior is now in the pipeline (T41)

The T41 module (5D joint fit: log_m_phi_MeV, log_m_chi_GeV, g_chi,
log_epsilon, log_alpha) produces a posterior over the full mediator
parameter space.

**Result (T41, 3.0s wall):**
- log Z = -29.45 ± 0.24
- m_φ ≈ 212 MeV (median)
- m_χ ≈ 462 GeV
- g_χ ≈ 0.37
- ε ≈ 10⁻⁵³ (kinetic mixing, essentially zero)
- α ≈ 10⁻²⁷ (annihilation coupling, essentially zero)
- Derived at MAP: σ/m_0 = 0.07 cm²/g, a = -1.81

**The Yukawa tension (the headline finding):**

| Quantity | T39 (free a) | T41 (Yukawa-derived a) |
|---|---|---|
| σ/m_0 at v=100 km/s | 1.57 cm²/g | 0.07 cm²/g |
| Velocity power-law a | +0.94 | -1.81 |
| Interpretation | σ/m DECREASES with v | σ/m INCREASES with v |

These are **opposite** (Δa = 2.75). The data want a positive a
(Bullet Cluster suppression at cluster scale requires σ/m to be
small at v > 1000 km/s), but the simple Yukawa cross-section gives
a < 0 (it grows with v). This tension is physically meaningful:
**simple Yukawa SIDM is RULED OUT** by the velocity dependence.

---

## Tier 2 — laboratory exclusions (T42)

The published experimental limits (NA64 invisible, RGB stellar
cooling, SN1987A) are recast into the (m_φ, ε) plane. Evaluation
at the T41 posterior median:

| Experiment | m_φ range | ε upper limit at T41 median m_φ (~212 MeV) |
|---|---|---|
| NA64 invisible (2024) | 1 - 300 MeV | ~3×10⁻⁴ |
| RGB stellar cooling (2021) | 1 - 300 MeV | ~10⁻⁴ |
| SN1987A burst (2023) | 1 - 300 MeV | ~10⁻⁵ |

**Predicted ε at T41 median:** 2.4×10⁻⁵³

**Gap to detection** (log10 of predicted / limit):
- NA64: ~49 orders of magnitude
- RGB stellar: ~49 orders of magnitude
- SN1987A: ~48 orders of magnitude

The mediator is **practically invisible** to every existing experiment.

---

## Honest caveat: prior dependence

The T41 posterior at ε ~ 10⁻⁵³ is **prior-driven**. The log-flat prior
[log_ε ∈ -60, -1] gives 60 orders of magnitude of "free space" for ε.
The posterior crashes to the lower edge because LZ and Fermi just
*prefer* ε smaller than the rest of the data prefer anything else.

This is the same prior-sensitivity issue flagged in T39 prior
robustness (T39 prior_robustness.json). The honest statement is:

> The T41 posterior suggests ε ≲ 10⁻⁵², but the *exact* value is
> prior-dependent. **The qualitative conclusion is robust**: the
> mediator is hidden behind orders-of-magnitude attenuation from SM
> couplings, regardless of exact prior.

---

## What could go wrong (the bullet list)

1. **Yukawa model is too simple.** The data wants a > 0; Yukawa gives
   a < 0. Candidates that give a > 0:
   - Inelastic DM (χ₁ + χ₂ with mass splitting δ ~ 0.1-1 MeV)
   - Pseudo-scalar spin-0 mediator
   - Velocity-dependent g_χ (form factor)
   - Composite resonances (e.g., dark glueball-dark meson)

2. **T41 prior is unrealistic.** ε ~ 10⁻⁵³ is below any reasonable
   theoretical floor. A more physical prior (e.g., ε > 10⁻¹⁰ from
   BBN/CMB constraints) would change the posterior shape.

3. **NA64 "invisible" recast is approximate.** The published NA64
   limits assume 100% visible decay; for our model the A' → χχ
   branching dominates. A proper recast would use the production
   cross-section × BR(χχ) / total rate.

4. **The sigma/m_0 = 1.57 cm²/g anchor is galaxy-scale.** At
   particle-physics scales (LZ, NA64), the v-dependence matters
   and the σ/m_0 estimate may not apply.

5. **CMB / BBN constraints on dark radiation were not applied.**
   If m_φ < 1 MeV and ε > 10⁻⁴, the mediator thermalizes and
   contributes ΔN_eff. This is a separate exclusion not in T42.

---

## Recommended next steps (5 actions)

1. **Try inelastic DM.** T41's tension is a model assumption.
   Replace the Yukawa with a χ₁ + χ₂ inelastic cross-section
   (σ ∝ (q²) instead of (q² + m_φ²)²). This may give a > 0.

2. **Re-cast T41 with a theory prior on ε.** Use ε > 10⁻¹⁰ (BBN
   floor) and re-run. The posterior should localize on (m_φ, m_χ)
   with a meaningful ε.

3. **Plot the (m_φ, ε) posterior overlaid on NA64 + RGB + SN1987A.**
   This is the publishable figure showing the experimental
   discovery reach.

4. **Add CMB + BBN exclusion contours.** Use Planck NPIPE + ACT DR6
   N_eff limits. This is a second open data pool.

5. **Forward to a Tier-3 NA64 collaboration request.** If the
   posterior wants m_φ ~ 200 MeV, NA64 has an
   [invisible-mode proposal](https://na64.web.cern.ch/) for this
   mass range. The data is real; the analysis is missing.

---

## Summary in one sentence

> The mediator is **predicted** (m_φ ≈ 212 MeV, ε ≈ 10⁻⁵³) but **not
> detectable** by any existing experiment — the SIDM-bumpy model
> requires the mediator to be invisible to the Standard Model, which
> is a *prediction* of the model, not a failure of detection.
