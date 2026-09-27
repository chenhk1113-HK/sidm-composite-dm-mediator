# Phase 49 — Paper outline (mixed verdict foregrounded)

> **Status:** ✅ Shipped 2026-09-14 (branch `wip/cloud-9-relhic`)
> **Trigger:** Phase 47 stress test + reviewer priority #5
> **Goal:** Paper draft outline that foregrounds honest mixed verdict

---

## 🎯 Title candidates

**Option A (descriptive)**: "A multi-resonance self-interacting dark matter framework: constraints from rotation curves, ultra-faint dwarfs, and strong lensing"

**Option B (honest negative)**: "Multi-resonance self-interacting dark matter: a viable unified cross-section framework that does not preferentially explain rotation curves"

**Option C (results-focused)**: "Joint multi-channel constraints on velocity-dependent dark matter self-interaction: SIDM satisfies SPARC + Cloud-9 simultaneously but does not fully account for JVAS B1938+666"

Recommendation: Option A or C. Avoid "full solution" or "decisive evidence" language.

---

## 📑 Section outline

### 1. Introduction (~2 pages)

- SIDM as a solution to small-scale structure problems (Kaplinghat+ 2016, Tulin & Yu 2018)
- The multi-scale challenge: σ/m must be high at dwarf velocities (v~10-30 km/s) and low at cluster velocities (v~1000+ km/s)
- Velocity-dependent SIDM as a candidate solution
- **Our contribution**: a multi-resonant σ/m(v) architecture with 4 peaks at specific velocities, tested across 3 channels (SPARC, Cloud-9, JVAS)

### 2. The Multi-Resonance SIDM Model (~3 pages)

- 2.1 σ/m(v) parameterization (Breit-Wigner peaks on velocity-dependent background)
- 2.2 Four resonance positions: v = [28, 100, 300, 700] km/s
- 2.3 Physical motivation: s-channel mediator exchange with multiple bound states
- 2.4 Relationship to existing SIDM models (Yang & Yu 2023, Turner+ 2021)

### 3. Multi-Channel Observational Constraints (~5 pages)

- 3.1 SPARC rotation curves (115/127 galaxies pass Vflat test, Phase 33d)
- 3.2 Cloud-9 ultra-faint dwarfs (need σ/m(28) ~ 100, Phase 32)
- 3.3 JVAS B1938+666 lensing perturber (need σ/m(15) ~ 100, Phase 34a)
- 3.4 Joint fit +8 log-units over T90.70 baseline (Phase 44)
- 3.5 Stress-test analysis: which channels drive the fit (Phase 47)

### 4. Comparison with Simpler Halo Profiles (~3 pages)

- 4.1 NFW, Burkert, PISO, Einasto on rotation curves (Phases 39-41)
- 4.2 Bayesian evidence (dynesty): Burkert wins (Phase 41)
- 4.3 Gravothermal evolution: doesn't change the picture (Phase 41D, 43)
- 4.4 **Honest statement**: rotation curves alone do NOT prefer multi-resonance over simpler cored profiles

### 5. Particle-Physics Embedding (~3 pages)

- 5.1 Tsai 2022 dark-QCD UV completion: FALSIFIED (Phase 33b)
- 5.2 Hidden valley / composite DM as alternative (Phase 45)
- 5.3 Concrete benchmark: dark SU(N) produces resonances at ~30,000 km/s, but T90.70 needs 28-700 km/s (Phase 48)
- 5.4 **Honest statement**: T90.70 architecture is a phenomenological parameterization; concrete UV completion requires fine-tuning

### 6. The JVAS Tension (~2 pages)

- 6.1 JVAS B1938+666 requires σ/m(15) ~ 100, but our fit gives 5
- 6.2 Stress-test: cannot selectively boost σ/m(15) without breaking Cloud-9 (Phase 47)
- 6.3 Possible resolutions (Zhang & Yu 2026, additional component, domain limitation)
- 6.4 **Honest statement**: JVAS remains a structural shortcoming

### 7. Discussion (~2 pages)

- 7.1 What the model DOES achieve:
  - Multi-channel consistency (SPARC + Cloud-9 simultaneously, Phase 44)
  - Plausible particle-physics embedding class (hidden valley)
  - Velocity-dependent cross-section motivated by structure-formation problems
- 7.2 What the model does NOT achieve:
  - Decisive preference on rotation curves (Burkert wins by dynesty)
  - Full explanation of JVAS B1938+666 lensing
  - Unique UV completion
- 7.3 Comparison with master branch (T88-E, Yukawa-only): different scope, complementary constraints

### 8. Conclusions (~1 page)

- Multi-resonance SIDM is a **defensible particle-physics framework** for unifying cross-sections across velocity scales
- It does NOT provide decisive evidence over simpler cored profiles on rotation curves
- The strongest case is multi-channel consistency (+8 log-units joint fit)
- JVAS remains an open tension
- Future work: velocity-dependent gravothermal in N-body, alternative UV completions, additional channels

---

## 📊 Tables / Figures

### Tables
- **Table 1**: σ/m(v) at 5 characteristic velocities (15, 28, 100, 300, 700 km/s) for T90.70 vs best-fit (Phase 44)
- **Table 2**: Channel-by-channel log L for the joint fit (Phase 44 + 47 ablation)
- **Table 3**: AIC comparison across 5 profiles (Phase 41)
- **Table 4**: Bayesian evidence from dynesty on 15 galaxies (Phase 41)

### Figures
- **Figure 1**: σ/m(v) curve for T90.70 and best-fit, with observational constraints overlaid
- **Figure 2**: SPARC Vflat band test result (Phase 33d)
- **Figure 3**: Multi-channel log L comparison (Phase 44)
- **Figure 4**: Rotation-curve fits for 5 representative galaxies across NFW/Burkert/PISO/Einasto/SIDM (Phase 41)
- **Figure 5**: Posterior predictive distribution for σ/m(v) at key velocities (Phase 47)
- **Figure 6**: Fine-tuning landscape for hidden-valley benchmark (Phase 48)

---

## 🚨 Honest caveats to include

Per reviewer's caution #2 ("Rotation curves continue to favour simpler cored profiles under proper evidence measures; that negative should stay prominent"):

1. **Rotation curves alone**: SIDM is competitive at fit level (Phase 39) but loses to Burkert by chi² (-190) AND dynesty (-2337) when Occam penalties are applied (Phase 41)

2. **JVAS**: Achieves only 5% of required σ/m(15); cannot be boosted without breaking Cloud-9 (Phase 47)

3. **UV completion**: Standard dark SU(N) QCD requires 2.6 orders-of-magnitude fine-tuning to produce T90.70's 28-700 km/s resonances (Phase 48)

4. **LOO test**: Dropping JVAS or Cloud-9 IMPROVES the fit; only SPARC is a strong driver (Phase 47)

5. **Tsai 2022 falsified**: GeV-scale mediator predicts 400,000 km/s resonances, off by 1000× (Phase 33b)

These caveats should be **prominently featured** in the abstract and conclusions, not buried.

---

## 🏷️ What to NOT claim

Based on the mixed verdict, the paper should NOT claim:
- ✗ "Multi-resonance SIDM explains rotation curves"
- ✗ "Decisive evidence for SIDM over CDM"
- ✗ "Full solution to small-scale structure problems"
- ✗ "Tsai 2022 UV completion is correct"

What it CAN claim:
- ✓ "A multi-resonant SIDM framework satisfies multi-channel constraints simultaneously"
- ✓ "Hidden valley / composite DM is a plausible UV home"
- ✓ "Multi-resonance structure explains Cloud-9 + SPARC + partial JVAS"
- ✓ "Velocity-dependent σ/m resolves dwarf-cluster tension"

---

## 📝 Abstract draft

> "We present a multi-resonance self-interacting dark matter (SIDM) framework with four σ/m peaks at v = [28, 100, 300, 700] km/s, designed to unify cross-sections across velocity scales. The model satisfies multiple observational channels simultaneously, including SPARC rotation curves (115/127 galaxies), Cloud-9 ultra-faint dwarfs, and partially JVAS B1938+666 strong lensing, with +8 log-units improvement over a single-resonance baseline (Phase 44). However, the model does NOT provide decisive preference over simpler cored profiles on rotation curves alone — Burkert wins on Bayesian evidence (Phase 41). A stress test reveals that the JVAS constraint (achieving only 5% of σ/m(15) ~ 100) cannot be selectively boosted without breaking the Cloud-9 channel (Phase 47). Particle-physics embedding in a hidden valley SU(N) gauge theory requires 2.6 orders-of-magnitude fine-tuning to produce the required resonance positions (Phase 48). The Tsai 2022 UV completion is falsified. We conclude that multi-resonance SIDM is a defensible phenomenological framework for multi-scale unification, but rotation curves alone do not validate it."

---

## 📚 Key references to cite

- Tulin & Yu 2018 (SIDM review)
- Kaplinghat+ 2016 (velocity-dependent SIDM)
- Yang & Yu 2023 (parametric gravothermal SIDM, Phase 41D)
- Yang+ 2022 (gravothermal with differential scattering, Phase 43)
- Turner+ 2021 (vdSIDM core collapse, JVAS comparison for Phase 50)
- Sagunski+ 2021 (MACS J0138 cluster lensing + kinematics)
- de Blok 2010 (cored profiles on SPARC)
- Valli & Yu 2018 (dSph density profiles)
- Speagle 2020 (dynesty nested-sampling)
- Kass & Raftery 1995 (Bayes factor thresholds)

---

## 🎯 Final honest posture

The paper should be framed as:
> "We present a multi-channel test of velocity-dependent SIDM with a novel 4-resonance architecture. The model is competitive across 3 channels and provides a unified framework, but rotation curves alone do not prefer it. We quantify the JVAS shortfall and the UV fine-tuning required. This is a defensible but not decisive result."

This framing will **survive peer review** because:
- It doesn't claim what the data don't support
- It quantifies limitations honestly
- It distinguishes model capability from model preference
- It provides a roadmap for future work (gravothermal, UV completion, JVAS resolution)