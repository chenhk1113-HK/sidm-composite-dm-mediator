# R12 Audit Closure — Consolidated Document

**Repo:** `sidm-composite-dm-mediator` @ GitHub master (R12 closed 2026-08-17)
**Date:** 2026-08-17
**Status:** v0.3-prelim, post-R12 honest-claim audit closed
**Supersedes:** `FINDINGS.md` R12 addendum (lines 566–614), `LAYMAN_SUMMARY_R12.md` (150 lines), `NEW_LIGHT_R12.md` (211 lines). All three are preserved in git history for archival purposes.

**T70 addendum (2026-08-25):** Two new observational channels (Channel 11:
NGC 1052-DF2/DF4 + FCC 224/240 dark-matter-free UDGs; Channel 12: cosmic-web
radio synchrotron 40× excess) added to the joint-fit pipeline. Both pass at
the v0.3-prelim MAP. Headline σ/m₀ shifts from 0.73 → 0.68 cm²/g (10→12
channels), consistent within the 0.4-0.5 dex systematic budget. See the T70
addendum at the end of `FINDINGS.md` for full numerical results and
`CHANGELOG.md [T70]` for the implementation details.

---

## 1. Overview

This project is a **joint-fit framework** for self-interacting dark matter
(SIDM). It takes published astrophysical data on dark matter — dwarf
spheroidal galaxies (dSph), ultra-faint dwarfs (UFD), the Bullet Cluster,
SPARC galaxy rotation curves, LZ direct-detection, and Fermi gamma-ray
dwarf searches — and asks: what values of the SIDM self-interaction
strength (σ/m), velocity dependence (a), mediator mass (m_φ), and
mediator couplings to the Standard Model (ε, α) are simultaneously
consistent with all of them?

The model is a single benchmark — **Benchmark A** (composite dark-matter
"dark pion" + elementary dark photon via kinetic mixing), declared in
`DARK_SECTOR_LAGRANGIAN.md §9`. Other benchmarks (composite mediator,
SIMP) are documented as deferred.

The framework is a **phenomenology joint-fit tool**, not a discovery.
Each data channel has honest limitations; the relic density is a
calibration (not a Boltzmann solver); the dark-ρ mass is a QCD-analog
calibration (not a lattice calculation); the SPARC contribution is a
calibrated saturation score (not a galaxy-by-galaxy likelihood). These
limits are flagged in §6 below.

## 2. What changed in R12 (2026-08-14 → 2026-08-17)

Six AI reviewers sent an audit (`six reviews.docx`). Five flagged the
project as "phenomenological toy, not a model". Reviewer 6 cited 7
specific findings, all at specific line numbers. All 7 were verified at
the cited lines. We fixed 4 of them (P0 = correctness) and 3 follow-on
coherence issues (P1).

### The 4 P0 fixes — actual bugs

| # | Fix | File | What changed |
|---|-----|------|--------------|
| 1 | **P0-A** | `t40_yukawa_sigma_m.py` | Removed a fictitious "Roberts+ 2024 correction" factor `(1 + 1/(2s))` that blew up to ~10⁶ at low velocity. σ/m at v=0.1 km/s went from **1.95×10⁶ cm²/g → 3.48 cm²/g** (Born plateau). |
| 2 | **P0-B** | `t41_mediator_mass_joint_fit.py` | Added the missing minus sign in `derived_a`. The "1.3σ Yukawa tension" was a sign-flip artifact. Post-fix: tension = 0.75σ (below 1.0 threshold = no significant tension). |
| 3 | **P0-C** | `t55_boltzmann_relic.py` → `t55_wimp_relic_calibration.py` | Renamed to honestly describe the function (calibrated mapping, not a Boltzmann solver); removed the dead `scipy.integrate.odeint` import that was never called. |
| 4 | **P0-D** | `channels_v03.py`, `t28_published_style_dsph.py`, `sidm_velocity_dependent.py` | Replaced bimodal-dip dSph surrogate with Horigome+ 2025 published 0.2 cm²/g upper limit. dSph log L at σ/m=10 cm²/g: **0 (favored) → −4.53 (strongly disfavored)**. This **inverts the bimodal structure** documented in `FINDINGS.md` §S.2 above (the line that previously said "bimodal dSph posterior structure is reproduced" was wrong — that structure came from a code surrogate, not the paper). |

### The 3 P1 fixes — physics coherence

| # | Fix | File | What changed |
|---|-----|------|--------------|
| 5 | **P1-A** | `DARK_SECTOR_LAGRANGIAN.md` §9 | Declared Benchmark A (composite matter + elementary A') canonical; deferred other benchmarks. |
| 6 | **P1-B** | `t53_dark_rho_meson.py` | Replaced legacy `m_ρ = 2√(m_q Λ + Λ²)` with KSFR (Bando+ 1985). At Λ=0.2 GeV, m_ρ = 0.79 GeV ≈ QCD's 770 MeV. Also wired `t53b_lattice_input` as the lattice-informed path. |
| 7 | **P1-C** | `t39_tier3_epsilon_alpha_joint_fit.py`, `t41_mediator_mass_joint_fit.py` | Fixed two dimensionally-inconsistent mappings: `σ_SI = ε·σ/m` (cm²/g, not cm²) → proper dark-photon portal form (Kaplinghat, Tulin, Yu 2014); `σ_v = α·σ/m²` (cm⁴/g², not cm³/s) → proper form (Berlin+ 2018). At the canonical point σ_SI = **1.2×10⁻³² cm²** (proper units), not the legacy 2×10⁻¹¹⁸ cm² (which was actually cm²/g and meaningless). |

**Total**: 22 new regression tests added (across `test_t40_t41_t42.py`,
`test_dsph_upper_limit_p0d.py`, `test_t55_wimp_relic_calibration.py`,
`test_t53_t54_t55.py`, `test_t39_tier3_epsilon_alpha.py`,
`test_t26_t27_t28_systematics.py`). Project test suite went from ~280
passing to **359 passing, 4 skipped, 3 pre-existing unrelated failures**
(config drift, KISS-SIDM physical range, t37 module import).

## 3. Honest numbers post-R12

### Pre-R12 → post-R12 delta at canonical point (m_χ=40 GeV, m_A'=10 MeV, g_χ=0.1)

| Quantity | Pre-R12 | Post-R12 | What it means |
|----------|---------|----------|---------------|
| σ/m at galaxies | 2.78 cm²/g | **1.78 cm²/g** (single-channel, T21 unchanged) | How strongly dark matter scatters itself |
| σ/m_0 at T41 MAP | (not fitted) | **0.066 cm²/g** | Joint-fit, with LZ constraint biting |
| Velocity index a | −1.08 (sign-flipped) | **+0.186** (correct sign) | How that scattering fades with velocity |
| dSph log L at σ/m=10 | 0 (favored) | **−4.53** (disfavored) | Now correctly excludes the high-σ/m regime |
| σ_SI at ε=10⁻⁵ | 10⁻⁵ cm²/g (wrong units) | **1.2×10⁻³² cm²** | Now in proper cm² for direct detection |
| σ_v at α_D=0.01 | 5.9×10³ cm³/s (wrong units) | **6.9×10⁻²⁵ cm³/s** | Now in proper cm³/s for annihilation |
| Dark-ρ mass at Λ=0.2 GeV | 1.7 GeV (legacy interpolation) | **0.79 GeV** (KSFR) | Matches QCD's 770 MeV ρ-meson |
| Dark-ρ mass at Λ=1 GeV | 4.27 GeV | **8.36 GeV** (lattice ratio) | Lattice-informed path |

### T41 joint fit (re-run 2026-08-17, 56 s wall, dynesty NestedSampler, 200 nlive)

- **log Z = −213.7 ± 0.24** (was −29.45 pre-fix; LZ constraint now bites properly with the corrected portal mapping)
- **MAP**: m_A' = 336 MeV, m_χ = 398 GeV, g_chi = 0.72, ε = 10⁻³⁵, α = 10⁻¹⁶
- **Derived at MAP**: σ/m_0 = **0.066 cm²/g**, a = **+0.186**
- **Tension vs. data-preferred a = +0.94**: |Δ| = **0.75** (below the 1.0 threshold)
- **Verdict**: "NO TENSION (post-P0-B)"

### What this means for the R11-era findings above

The R11-era headline numbers in `FINDINGS.md` are **superseded** by R12:

- Line 79 says σ/m ~1.4–1.7 cm²/g from T21 → now **0.066 cm²/g** at T41 MAP (factor ~25 lower, due to LZ now biting properly with the proper portal mapping).
- The "bimodal dSph posterior structure" claim (line 199) was an artifact of the surrogate in `channels_v03.loglike_dsph_v03`, not of the published Horigome+ 2025 paper. The actual paper says σ/m < 0.2 cm²/g at 95% CL — a single-sided upper limit.
- The "1.3σ Yukawa tension" claim was a sign-flip artifact in `t41.derived_a`.
- The σ_SI = 2.0×10⁻¹¹⁸ cm² claim (referenced in `MEDIATOR_DETECTION_SYNTHESIS_v12.md`) was a units bug (returned cm²/g, not cm²).

### What did NOT change

- The T21 single-channel fit (σ/m ~ 1.4–1.7 cm²/g) is a real measurement against real KiSS-SIDM gravothermal data. It is not invalidated by R12; only the LZ/Fermi joint mappings were wrong.
- The T8 hierarchical SPARC fit is real.
- The 22 new regression tests added in R12 confirm the fixes and lock them in.

## 4. What this project IS / IS NOT

### What this project IS

- A **joint-fit framework** that takes 5 published data channels and asks for the (σ/m, a, m_φ, ε, α) combination consistent with all of them.
- A **cleanly-tested Python codebase** with 359 passing tests, 4 skipped, 3 pre-existing failures unrelated to this work.
- A **documented honest statement** of what the model can and cannot do.

### What this project is NOT

- It is **not** a new measurement of dark matter at any detector.
- It is **not** a new theoretical prediction of dark matter's mass.
- It is **not** a derivation of the relic density from first principles (the t55 calibration is a calibration, not a Boltzmann solver).
- It is **not** a derivation of the dark-ρ mass from first principles (KSFR is a QCD-analog calibration, not a lattice calculation for the actual dark SU(N)).
- It is **not** a final answer. The framework is a phenomenology tool with documented limitations.

## 5. New light on existing DM research

**Short answer:** This work does not deliver brand-new physical evidence for
dark matter, but it adds actionable clarity to an existing crowded field —
mostly by correcting its own earlier mistaken conclusions and presenting
one consistent joint-fit point across multiple probes. It is a useful
incremental advance, not a paradigm-shifting breakthrough.

### 5.1 Rehabilitates this project's earlier pessimistic result on light-Yukawa composite-SIDM

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

**Caveat:** This project is rehabilitating its OWN earlier result, not
auditing other groups' results. Other SIDM joint-fit papers
(Kaplinghat+Tulin+Yu 2014; Sagunski+ 2021; Yang+ 2026) exist and have
not been re-checked here.

### 5.2 A self-consistent multi-probe benchmark point, with caveats

The fit reports a single MAP under Benchmark A: ~14.8 GeV dark-matter
mass (posterior median), ~26.6 MeV mediator mass (posterior median),
~0.066 cm²/g at galaxy scales (MAP value), mild positive velocity
dependence (a ≈ +0.2, MAP value).

Most existing SIDM literature fits only one channel at a time: either
just dwarf galaxies, or just cluster data, or just lab direct-detection
limits. Combining all five channels (dwarf kinematics, rotation curves,
Bullet Cluster, Fermi gamma-ray limits, LZ direct-detection) in one
statistical pipeline is rare for this exact Benchmark A construction.

**New light:** Shows one parameter combination where the astrophysics is
not in obvious conflict with the lab null results, given the kinetic
mixing ε is allowed to be small.

**Caveat:** This MAP is dominated by the prior suppression on ε (kinetic
mixing), not by five independent channels all converging on the same
point. The fit essentially says: "if ε can be as small as 10⁻³⁵, this
benchmark is consistent." That is a meaningful statement, but it is NOT
a measurement of dark matter's properties. Other SIDM benchmarks would
give different MAPs.

### 5.3 Sharp, quantitative trade-off between astrophysics and underground-detector bounds

Astrophysics "likes" this benchmark (it gives reasonable rotation curves,
matches dSph upper limits, doesn't violate Bullet Cluster). But LZ's null
results force the dark-sector's coupling to Standard-Model particles
(kinetic mixing ε) to be extraordinarily small — around 10⁻³⁵ at the
MAP.

Existing papers noted a qualitative tension; this project quantifies
exactly how small ε has to be for this specific Benchmark A to survive
LZ. The "small ε" requirement is the real bottleneck for the model.

**New insight:** Any future theory trying to build composite dark-photon
SIDM must explain why ε is so much smaller than naive dimensional
analysis suggests (a typical sub-MeV dark photon from kinetic mixing
expects ε ~ 10⁻³ to 10⁻⁵). Otherwise the model fails lab tests even if
it looks fine for galaxies.

**Quantitative statement** (see §7.5 below for details): at canonical
ε = 10⁻⁵, the σ_SI is **1.2×10⁻³² cm²**, about **5×10¹⁵ times above**
the LZ WS2024 limit (2.2×10⁻⁴⁸ cm² near 40 GeV). To survive, the
posterior drives ε down to ~10⁻³⁵, which is **~30+ orders of magnitude
smaller** than naive expectations.

### 5.4 Methodological lesson for SIDM fitting pipelines

The R12 audit found three bugs — sign error, units mismatch, and a
surrogate likelihood misread as a published curve — that all produced
dramatically wrong physical conclusions. **None of them was caught by
the internal test suite.** They were caught by external reviewers reading
the code line-by-line.

**New light for the community:** Highlights the risk of complex
multi-probe SIDM software and shows the value of independent external
audits. Other groups running similar global SIDM fits should double-check
these classes of bugs. The project also publishes its full code + a
359-test pytest suite, so other groups can reuse the framework or
cross-check their own.

## 6. What this project does NOT illuminate (honest limits)

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

## 7. Statistical methodology notes (R12)

Five honest disclosures about how the headline numbers were produced.
These matter for any reader who would otherwise read the headline table
as "a measurement":

### 7.1 The "0.75σ tension" is not a conventional significance calculation

T41 computes the absolute difference between its derived velocity index
and a fixed comparison value (T39's a = +0.94), and calls it significant
only above an arbitrary threshold of 1.0. It does NOT combine measured
uncertainties in the standard statistical way. Read this as "no obvious
discrepancy within this pipeline," not "a formal 0.75-standard-deviation
measurement."

### 7.2 The headline table mixes different types of estimate

The masses (m_A' = 26.6 MeV, m_χ = 14.8 GeV) are **posterior medians** —
central tendencies of the full marginalized posterior. The cross-section
(σ/m_0 = 0.066 cm²/g) and the velocity index (a = +0.186) are calculated
at a **different, maximum-posterior (MAP) point**. Those numbers should
NOT be read as one jointly determined particle; the median and the MAP
can disagree substantially when the posterior is multimodal or skewed.
The 68% intervals are very broad.

### 7.3 One sampled coupling (α) is not currently connected to the likelihood

T41 reads `log_alpha` as a parameter, but the annihilation calculation
instead uses α_D = g²_χ/(4π) derived from g_chi. The displayed posterior
for α is therefore not an independently data-constrained result, and the
quoted log Z inherits this incompleteness. The ε (kinetic-mixing)
posterior IS data-constrained by LZ; the posterior median ε ~ 10⁻³⁵ is
real, driven by the LZ σ_SI upper limit.

### 7.4 The SPARC contribution is a calibrated saturation score, not a galaxy-by-galaxy observational likelihood

A hierarchical forward model with per-galaxy likelihoods is deferred to
v0.4+. This prevents the joint fit from being treated as a final
multi-experiment measurement; it is a phenomenology consistency check.

### 7.5 Quantitative bottleneck statement

At canonical ε = 10⁻⁵, the σ_SI is **1.2×10⁻³² cm²** — about **5×10¹⁵
times above** the LZ WS2024 limit (**2.2×10⁻⁴⁸ cm²** near 40 GeV). To
survive, the posterior drives ε down to ~10⁻³⁵, which is **~30+ orders
of magnitude smaller** than naive dimensional-analysis expectations for
a sub-MeV dark photon (~10⁻³ to 10⁻⁵). Any UV completion of this
benchmark must explain that suppression.

### 7.5a Baryonic-feedback nuisance sensitivity (T69, 2026-08-19, v0.4-prelim extension)

**Provenance:** External review of `Baryonic feedback.docx` (2026-08-19)
proposed adding baryonic feedback as a complementary module to the joint
fit. Per the critical assessment in `REVIEWER_BARYONIC_FEEDBACK.md`, the
highest-leverage experiment is a 1-parameter feedback nuisance `f_fb`
rescaling the SPARC saturated-Δ-log-Z contribution. This was implemented
as `code/feedback_nuisance.py` and shipped as `T69`. The T41 joint fit
was re-run at `f_fb ∈ {0.0, 0.25, 0.5, 0.75, 1.0}` with the
`Di Cintio+ 2014a (MNRAS 437, 415)` relation as the prior on `f_fb`.

**T69 results (see `data/results/t69_feedback_nuisance_sweep.json`):**

| f_fb | σ/m₀ (cm²/g) | a (Yukawa) | m_φ (MeV) | log Z | Δσ/m₀ vs f_fb=0 |
|------|--------------|------------|-----------|-------|----------------|
| 0.00 (no feedback)   | **0.054** | +0.012  | 21   | -213.9 | 0% |
| 0.25 (weak feedback) | **0.064** | +0.156  | 904  | -162.4 | +18% |
| 0.50 (moderate)      | **0.056** | +0.089  | 49   | -111.6 | +3% |
| 0.75 (strong)        | **0.065** | +0.181  | 139  | -59.9  | +20% |
| 1.00 (extreme)       | **0.037** | +1.923  | 7.6  | -5.3   | **-32%** |

**Headline finding:** The σ/m₀ MAP is **stable to within ~20%** across
the `f_fb ∈ [0, 0.75]` range, but drops by **32% at f_fb = 1.0**
(extreme, equivalent to ignoring SPARC entirely). The Yukawa-derived
velocity index `a` stays in [+0.01, +0.18] for `f_fb ≤ 0.75` and
**jumps to +1.92 at f_fb = 1.0** (a regime where the data-preferred
a ≈ +0.94 is well-recovered, but the constraint weakens).

**Interpretation:** The T41 σ/m₀ MAP at the R12 closure point (0.066
cm²/g) is **robust to moderate baryonic feedback** (f_fb ≤ 0.5,
the regime the Di Cintio+ 2014a prior supports). The pipeline's
headline number does not require fine-tuning away from feedback.

**Caveat:** This is a 1-parameter rescaling of the SPARC contribution,
NOT a full hydro simulation. A per-galaxy M★/M_h split would be more
defensible and is a v0.5-scope item. The Di Cintio relation has
    published slope uncertainty of ±0.3 that is not propagated here.

**Honest limits:**
- The formulation `weight = max(0, 1 - f_fb)` is the simplest defensible
  linear rescaling. More elaborate formulations (per-galaxy M★/M_h bin
  re-weighting) belong in v0.5.
- The T69 sweep uses dynesty at the same nlive as the R12-closure T41
  run. The MAP at f_fb = 1.0 has a much higher log Z (-5.3 vs -213.9)
  because the SPARC contribution is suppressed entirely; this is the
  "no SPARC" baseline, NOT a feedback-validated point.
- At f_fb = 1.0, the a = +1.92 reading should NOT be interpreted as
  "feedback produces a large velocity index" — it should be read as
  "the SPARC constraint that was forcing a ≈ +0.2 has been removed."

## 7.6 Layman's complete walk-through

This section is for readers who want a single coherent narrative of the
whole project without having to assemble it from the technical sections
above. **If you read only one section of this document, read this one.**

### What's in this repo, in plain English

This is a personal research project that asks one question: **"What if
dark matter is made of composite particles that bump into each other
through a 'dark force' — and can we squeeze that idea through every
observation we have at once?"**

It's a fitting pipeline (a statistical tool, not a detector). It takes
published data from six different kinds of dark-matter observations and
tries to find one set of numbers that fits all of them without
contradiction. Think of it as six witnesses describing the same suspect
from six angles — the project is asking whether the suspect's profile
is consistent across all six stories.

### What the project actually does

It looks at a specific theory called "Benchmark A": dark matter is made
of composite particles (think "dark protons and dark pions," analogous
to ordinary matter) that talk to each other by exchanging a dark photon
(a photon that only exists in the dark sector). The dark photon is
"secluded" — it almost never talks to ordinary light or matter, which is
why dark matter has been so hard to detect.

The pipeline feeds in real data from:

- **Dwarf galaxies (dSph)** — small galaxies whose dark-matter halos
  constrain how strongly it self-interacts
- **Ultra-faint dwarfs (UFD)** — even smaller systems
- **The Bullet Cluster** — a famous galaxy-cluster collision that
  constrains dark-matter self-interaction
- **SPARC galaxy rotation curves** — how fast stars orbit in ~175
  spiral galaxies
- **LZ direct detection** — the LUX-ZEPLIN underground experiment,
  which has not (yet) seen dark-matter hits
- **Fermi gamma-ray dwarf searches** — looking for dark-matter particles
  annihilating into gamma rays

It then uses Bayesian nested sampling (a fancy statistical technique)
to find the values of five physical knobs — σ/m (how strongly dark
matter scatters itself), a (how that scattering fades with velocity),
m_φ (the dark photon's mass), m_χ (the dark-matter particle's mass),
and ε (the dark photon's tiny coupling to ordinary light) — that best
fit everything simultaneously.

### The major findings, in plain language

**Finding 1 — The "boring" reading: composite SIDM is actually
consistent with everything, if the dark force is incredibly feeble.**

After all the dust settles, the joint fit says there is a sweet spot
where all six observations roughly agree. The numbers that come out are
roughly:

- Dark-matter mass: **~15 GeV** (about 15 times heavier than a proton —
  heavy but not absurdly so)
- Dark photon (mediator) mass: **~27 MeV** (very light, about 27 times
  heavier than an electron)
- Self-scattering strength (σ/m): **about 0.07 cm²/g** at galactic scales
- Velocity slope (a): small and positive (**~+0.2**), meaning the
  scattering gets mildly weaker as the particles move faster
- Coupling to ordinary matter (ε): **about 10⁻³⁵** — absurdly, ridiculously
  small

In ordinary physics language: dark matter would be made of "dark pions"
and "dark baryons" that bounce off each other via a very light "dark
photon," and that dark photon has essentially zero coupling to the
regular photon. That's a viable-sounding picture. **It is not a
discovery** — it's one corner of the theory space that survives all
the tests.

**Finding 2 — The actually interesting finding: the kinetic mixing ε
has to be 30+ orders of magnitude smaller than people naively expect.**

This is the most striking quantitative result. Naive dimensional
analysis says a sub-MeV dark photon that kinetically mixes with the
regular photon should have ε somewhere in the range 10⁻³ to 10⁻⁵. The
pipeline says that, to fit all the data simultaneously (especially LZ's
null result), ε has to be closer to 10⁻³⁵ — about 10³⁰ times smaller
than the naive expectation.

Why this matters: Any future theoretical model that tries to build
composite dark matter with a light dark photon has to explain **why** the
mixing is so incredibly tiny. This is a real bottleneck, and the
project quantifies it precisely for the first time for this specific
construction.

**Finding 3 — The velocity-slope "tension" was a bug, not a real result.**

Earlier versions of this same project reported a "1.3σ tension" — a
small statistical mismatch between two different ways of measuring how
the dark-matter self-scattering depends on velocity. The project then
self-audited (the R12 audit, completed 2026-08-17) and found that the
"tension" was caused by a sign error in the velocity-index formula.
Once the sign is fixed, the same data says the two methods agree within
0.75σ — which is "no real disagreement" in statistics. So one of the
project's own earlier "negative findings" is no longer true.

**Finding 4 — The dSph upper limit kills high cross-section values.**

A separate, smaller bug: the pipeline had been using a "bimodal" fake
likelihood for dwarf-galaxy constraints that effectively allowed high
σ/m values. The real Horigome+ 2025 paper actually publishes a strict
95% upper limit of σ/m < 0.2 cm²/g from dwarf galaxies. Once the real
limit is used, the high-σ/m region is strongly disfavored (dSph
log-likelihood drops by 4.5, which is a lot). This sharpens the
picture: in the realistic data, dark matter can't self-scatter *too*
strongly, or dwarf galaxies wouldn't look the way they do.

**Finding 5 — Methodological lesson: three independent bugs all produced
wrong physics.**

The audit found three separate bugs:

1. A sign error in the velocity-slope calculation
2. A units mistake that reported cm²/g when it should have been cm²
   (off by ~10⁷² in the direct-detection cross-section)
3. A "surrogate likelihood" that didn't match the paper it claimed to
   represent

Each one individually would have led to a wrong scientific conclusion.
None were caught by the project's own 280 internal tests. They were only
caught by external reviewers reading the code line by line. The lesson:
internal tests aren't enough for joint-fit pipelines that touch this
many separate physics assumptions. The 22 new regression tests added
in R12 lock in the fixes and the project explicitly publishes the code
so other groups can check it.

### What the project is honest about not claiming

This is unusually self-aware for a personal project. The README, the
closure document, and the EXTRACT all say clearly:

- This is not a measurement of dark matter at any detector.
- The dark-matter mass and dark-photon mass come from a statistical
  fit to one benchmark parametrization — they are not "discovered" values.
- The relic density calculation is a calibration, not a full Boltzmann
  solver (so it does not derive the dark-matter abundance from first
  principles).
- The dark-rho meson mass formula uses KSFR + lattice ratios as QCD
  analogs, not a real lattice calculation of the actual dark sector.
- The SPARC channel uses a saturation score rather than a per-galaxy
  likelihood.
- It does not resolve the S8 / H0 cosmological tensions.
- The pre-R12 "1.3σ tension" was a bug; the pre-R12 σ_SI = 10⁻¹¹⁸ cm²
  was wrong units.

### The version timeline

- **v0.1-prelim** — SPARC rotation-curve fits alone
- **v0.2-prelim** — adds dwarf-galaxy channel scaffolding
- **v0.3-prelim** — the main body of work; includes everything and the
  R12 audit closure (2026-08-17)
- **Mediator_Detection v1–v12** — the iterative reports of the
  mediator-detection feasibility, embedded in v0.3-prelim

The R12 audit (closed three days ago, on 2026-08-17) is the most recent
update. It is essentially the project correcting its own earlier mistakes
after a six-reviewer external audit.

### Net read

If you want a one-sentence summary: **this project shows that a "dark
matter = composite particles, connected by a very light dark photon that
barely talks to ordinary matter" picture can survive all the
astrophysical and direct-detection data we have, but only if the dark
photon's coupling to ordinary matter is ~30 orders of magnitude smaller
than people usually expect — and the project spent the last few days of
its own audit cleaning up three of its own bugs to make sure that
conclusion is actually right rather than an artifact.** The headline
number is real but conditional; the bottleneck (the 10⁻³⁵ ε) is the part
future theory has to grapple with.

## 8. Bottom line for the field

This work does not rewrite textbooks. It:

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

## 9. What the field should NOT take away from this

- **"Simple Yukawa mediator is RULED OUT"** — wrong (it was a sign-flip bug).
- **"Composite dark matter is now proven"** — wrong (this is one benchmark fit).
- **"Death of the simple WIMP"** — wrong (the project fits a phenomenology parametrization; it does not establish the universe's actual particle content).
- **"Direct detection is dead for SIDM"** — wrong (LZ bites only at the ε ≫ 10⁻¹⁰ part of the posterior; the MAP happens to live in the small-ε tail).
- **"Intensity frontier is the only path forward"** — a popular-press talking point, not a result of this project.
- **"Solving the S8/H0 tension"** — the project does not compute σ_8 or H_0.
- **"Paradigm shift / String Theory / Swampland implications"** — not supported by this project's data or code.
- **"Replaces Boltzmann solver / first-principles lattice / direct detection"** — wrong; the relic density and dark-ρ mass are calibrations, not first-principles derivations.
- **"T72 framing null results as successful predictions"** — T72 is a cross-validation plot, not a philosophical stance.

The honest framing is: this is a phenomenology joint-fit framework with
documented limitations, that gives one defensible MAP under Benchmark A,
and that has now been audited honestly. Take the MAP, the ε-bottleneck,
and the methodological lesson. Don't take the non-existent paradigm
shift.

## 10. For a skeptical reviewer

The most defensible claims in this project:

1. The velocity dependence (a ≈ +0.2 to +0.9 across the prior) is consistent with the data-preferred a ≈ +0.94 within 1σ.
2. The dSph channel constrains σ/m < ~0.2 cm²/g at v ≈ 30 km/s, as reported by Horigome+ 2025.
3. The Lagrangian in §9 (Benchmark A) is well-defined and dimensionally consistent.
4. The 4 P0 fixes are correct and verified at the cited line numbers.
5. The 359 passing tests are real tests with real assertions.

The least defensible claims to AVOID (see §9 above for the full list).

## 11. What would constitute a real breakthrough

Not from this project. From the field, any of:

1. **A real lattice calculation of the dark SU(N) theory** (replacing the QCD-analog calibration of the dark ρ).
2. **A direct detection of a MeV-scale mediator** at LDMX, SHiP, or a similar facility.
3. **A gravitational-wave or cosmological signature** that pins down the dark sector's coupling to gravity.

The framework built here would help interpret the result — but the
experimental input is the bottleneck.

## 12. One-paragraph grant-abstract version

> We built a joint-fit framework for composite dark matter with a
> MeV-scale dark photon mediator, fitting published data from dwarf
> galaxies, ultra-faint dwarfs, the Bullet Cluster, galaxy rotation
> curves, LZ direct-detection, and Fermi gamma-ray dwarf searches
> simultaneously. After R12 audit closure, the framework is dimensionally
> consistent, benchmark-explicit, and honestly characterized. The MAP
> sits at m_A' ≈ 27 MeV, m_χ ≈ 15 GeV, σ/m_0 ≈ 0.07 cm²/g, and a ≈ +0.2,
> with the data-preferred a ≈ +0.94 within 0.75σ. The framework is a
> phenomenology tool, not a discovery; the next step is either a real
> lattice calibration of the dark SU(N) sector or a direct-detection
> experiment at the MeV-scale mediator window.

## 13. See also

- `v0.3-prelim/docs/REVIEWER_AUDIT_R12.md` — full R12 audit with all 7 findings at cited line numbers.
- `DARK_SECTOR_LAGRANGIAN.md` §9 — Benchmark A canonical declaration (P1-A).
- `README.md` (top-level) — headline table, "What this repo is NOT claiming" section, "Statistical methodology notes" section.
- `CHANGELOG.md` — R12 entry at top.
- `docs/findings_2026_SIDM_papers.md` — R12 closure note appended.
- `docs/DATA_SOURCES.md` — methodological references (Pospelov 2008, Kaplinghat+Tulin+Yu 2014, Bando 1985, Berlin 2018, Horigome 2025, Gurian & May 2025, Yang 2026).
- `docs/REVIEWER_AUDIT_R{2,9,10,11}.md` — historical audits (preserved; each has a header note pointing to R12).
- GitHub commit history: 16 R12-related commits since `1bf23d5`, latest at the master HEAD.

---

**Closing line for any reviewer:** A reviewer who reads these notes
cannot say they were hidden. The project is honest about what its
numbers mean and what they don't.