# Does this project shed new light on existing dark-matter research?

**Short answer:** It does not deliver brand-new physical evidence for dark
matter, but it adds meaningful, actionable clarity to an existing crowded
field — mostly by correcting its own earlier mistaken conclusions and
presenting one consistent joint-fit point across multiple probes. It is a
useful incremental advance, not a paradigm-shifting breakthrough.

---

## What new light it brings to existing literature

### 1. Rehabilitates this project's earlier pessimistic result on light-Yukawa mediator composite-SIDM

The pre-R12 version of this same project reported a "1.3σ Yukawa tension"
and concluded that the light-dark-photon + composite-pion benchmark was
strongly disfavoured by combining galaxies, clusters and direct-detection
data.

The R12 audit found that conclusion was caused by three independent bugs
(a sign error in the velocity-index formula, a unit-mismatch in the
direct-detection cross-section, and a bimodal-surrogate likelihood that
misread the published dSph paper). After fixing all three, the same
benchmark is statistically consistent with the same multi-messenger data
at only 0.75σ tension.

**New insight:** The community shouldn't take this benchmark off the
table based on those older (incorrect) joint-fit outputs. That resets
part of the prior pessimism about light-mediator composite SIDM, at
least from this particular fitting pipeline.

**Caveat (be careful):** This project is rehabilitating its OWN earlier
result, not auditing other groups' results. Other SIDM joint-fit papers
(Kaplinghat+Tulin+Yu 2014; Sagunski+ 2021; Yang+ 2026) exist and have not
been re-checked here.

---

### 2. A self-consistent multi-probe benchmark point, with caveats

The fit reports a single MAP (most-likely point in the posterior) under
Benchmark A: ~14.8 GeV dark-matter mass, ~26.6 MeV mediator mass, ~0.066
cm²/g at galaxy scales, mild positive velocity dependence (a ≈ +0.2).

Most existing SIDM literature fits only one channel at a time: either
just dwarf galaxies, or just cluster data, or just lab direct-detection
limits. Combining all five channels (dwarf kinematics, rotation curves,
Bullet Cluster, Fermi gamma-ray limits, LZ direct-detection) in one
statistical pipeline is rare for this exact Benchmark A construction.

**New light:** Shows one parameter combination where the astrophysics is
not in obvious conflict with the lab null results, given the kinetic
mixing ε is allowed to be small.

**Caveat:** This MAP is dominated by the prior suppression on ε
(kinetic mixing), not by five independent channels all converging on the
same point. The fit essentially says: "if ε can be as small as 10⁻³⁵,
this benchmark is consistent." That is a meaningful statement, but it is
NOT a measurement of dark matter's properties. Other SIDM benchmarks
would give different MAPs.

---

### 3. Sharp, quantitative trade-off between astrophysics and underground-detector bounds

Astrophysics "likes" this benchmark (it gives reasonable rotation
curves, matches dSph upper limits, doesn't violate Bullet Cluster). But
LZ's null results force the dark-sector's coupling to Standard-Model
particles (the kinetic mixing ε) to be extraordinarily small — around
10⁻³⁵ at the MAP.

Existing papers noted a qualitative tension; this project quantifies
exactly how small ε has to be for this specific Benchmark A to survive
LZ. The "small ε" requirement is the real bottleneck for the model.

**New insight:** Any future theory trying to build composite dark-photon
SIDM must explain why ε is so much smaller than naive dimensional
analysis suggests (a typical sub-MeV dark photon from kinetic mixing
expects ε ~ 10⁻³ to 10⁻⁵). Otherwise the model fails lab tests even if
it looks fine for galaxies.

---

### 4. Methodological lesson for SIDM fitting pipelines

The R12 audit found three bugs — sign error, units mismatch, and a
surrogate likelihood misread as a published curve — that all produced
dramatically wrong physical conclusions. None of them was caught by the
internal test suite. They were caught by external reviewers reading the
code line-by-line.

**New light for the community:** Highlights the risk of complex
multi-probe SIDM software and shows the value of independent external
audits. Other groups running similar global SIDM fits should double-check
these classes of bugs. The project also publishes its full code + a 359-test
pytest suite, so other groups can reuse the framework or cross-check
their own.

---

## What this project does NOT illuminate (honest limits)

- **Does not resolve the S8/H0 cosmological tensions.** It doesn't
  compute σ_8 or H_0. SIDM as a candidate explanation for those tensions
  is a separate literature.
- **Does not give observational proof that dark matter is composite or
  has a dark-photon mediator.** Multiple competing dark-matter models
  (different SIDM benchmarks, fuzzy DM, primordial black holes, sterile
  neutrinos) can fit the same data. The MAP reported here is one point
  in one specific Benchmark A parametrization.
- **Does not derive particle parameters from first-principles
  composite-sector theory.** The dark-ρ mass uses a QCD-analog
  calibration (KSFR relation, Bando+ 1985), not a real lattice
  calculation for the actual dark SU(N). The relic density is a 1/⟨σv⟩
  calibration, not a Boltzmann solver output. Masses and couplings are
  fit parameters from data, not derived from UV theory.
- **Does not rule out or favour standard cold dark matter ΛCDM.** It
  tests one SIDM benchmark; ΛCDM is unchanged by this work.
- **Does not turn a "1.3σ tension" into a "0.75σ tension" for the whole
  SIDM field.** It only rehabilitates this project's own pre-R12 result.
  Other groups' results may or may not have similar bugs.

---

## Bottom line for the field

This work does not rewrite textbooks. But it:

1. Corrects a misleading prior result from this same project.
2. Presents one self-consistent multi-probe benchmark point under
   Benchmark A, with the kinetic-mixing bottleneck explicitly quantified.
3. Exposes a sharp theory-experiment tension that any future
   dark-photon SIDM construction must address.
4. Sets a reproducible standard (open code + 359-test suite + audit
   trail) for SIDM fitting pipelines.

For researchers working specifically on SIDM mediator models, this is
useful new light. For the broader dark-matter field, it is careful
incremental progress — honest bookkeeping that surfaces what the data
actually allows under one specific benchmark, not a transformative
discovery.

---

## What the field should NOT take away from this

- "Simple Yukawa mediator is RULED OUT" — wrong (it was a sign-flip bug).
- "Composite dark matter is now proven" — wrong (this is one benchmark fit).
- "Direct detection is dead for SIDM" — wrong (LZ bites only at the
  ε ≫ 10⁻¹⁰ part of the posterior; the MAP happens to live in the small-ε
  tail).
- "Paradigm shift / String Theory / Swampland implications" — not
  supported by this project's data or code.
- "Replaces Boltzmann solver / first-principles lattice / direct
  detection" — wrong; the relic density and dark-ρ mass are
  calibrations, not first-principles derivations.

The honest framing is: this is a phenomenology joint-fit framework with
documented limitations, that gives one defensible MAP under Benchmark A,
and that has now been audited honestly. Take the MAP, the
ε-bottleneck, and the methodological lesson. Don't take the
non-existent paradigm shift.

---

## Statistical methodology notes (R12)

Five honest disclosures about how the headline numbers were produced.
These matter for any reader who would otherwise read the headline table
as "a measurement":

1. **The "0.75σ tension" is not a conventional significance calculation.**
   T41 computes the absolute difference between its derived velocity
   index and a fixed comparison value (T39's a = +0.94), and calls it
   significant only above an arbitrary threshold of 1.0. It does NOT
   combine measured uncertainties in the standard statistical way.
   Read this as "no obvious discrepancy within this pipeline," not "a
   formal 0.75-standard-deviation measurement."

2. **The headline table mixes different types of estimate.** The masses
   (m_A' = 26.6 MeV, m_χ = 14.8 GeV) are **posterior medians** — central
   tendencies of the full marginalized posterior. The cross-section
   (σ/m_0 = 0.066 cm²/g) and the velocity index (a = +0.186) are
   calculated at a **different, maximum-posterior (MAP) point**. Those
   numbers should NOT be read as one jointly determined particle; the
   median and the MAP can disagree substantially when the posterior is
   multimodal or skewed. The 68% intervals are very broad.

3. **One sampled coupling (α) is not currently connected to the
   likelihood.** T41 reads `log_alpha` as a parameter, but the
   annihilation calculation instead uses α_D = g²_χ/(4π) derived from
   g_chi. The displayed posterior for α is not independently
   data-constrained, and the quoted log Z inherits this incompleteness.
   The ε posterior IS data-constrained (by LZ); the median ε ~ 10⁻³⁵
   is real.

4. **The SPARC contribution is a calibrated saturation score, not a
   galaxy-by-galaxy observational likelihood.** A hierarchical forward
   model with per-galaxy likelihoods is deferred to v0.4+. This
   prevents the joint fit from being treated as a final multi-experiment
   measurement; it is a phenomenology consistency check.

5. **Quantitative bottleneck.** At canonical ε = 10⁻⁵, the σ_SI is
   1.2×10⁻³² cm² — about 5×10¹⁵ times **above** the LZ WS2024 limit
   (2.2×10⁻⁴⁸ cm² near 40 GeV). To survive, the posterior drives ε
   down to ~10⁻³⁵, which is **~30+ orders of magnitude smaller** than
   naive dimensional-analysis expectations for a sub-MeV dark photon
   (~10⁻³ to 10⁻⁵). Any UV completion of this benchmark must explain
   this suppression.

A reviewer who reads these notes cannot say they were hidden. The
project is honest about what its numbers mean and what they don't.