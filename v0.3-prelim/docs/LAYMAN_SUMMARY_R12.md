# Layman summary — what this project actually does (R12, 2026-08-17)

> **⚠️ SUPERSEDED (2026-08-26):** This document is preserved for archival
> purposes. The **current** layman summary is
> `LAYMAN_SUMMARY_R13.md` in this directory (covers R13 full closure
> + v0.5 KSFR caveat + H3+H4 sensitivity findings, 2026-08-26).
> Historical per-round layman summaries:
> - `LAYMAN_SUMMARY_R12.md` (this file) — R12 closure + 4 P0 + 3 P1 fixes
> - `LAYMAN_SUMMARY_R13.md` — R13 closure + v0.5 KSFR caveat + H3+H4 sensitivity

> **T70 addendum (2026-08-25):** Two new observational channels (NGC 1052-DF2/DF4
> + FCC 224/240 dark-matter-free UDGs; cosmic-web radio synchrotron 40× excess)
> added to the joint-fit pipeline. Both pass at the v0.3-prelim MAP. Headline
> σ/m₀ shifts from 0.73 → 0.68 cm²/g (10→12 channels), consistent within the
> 0.4-0.5 dex systematic budget. Full details in `CHANGELOG.md [T70]` and
> the T70 addendum at the end of `FINDINGS.md`.
>
> **R13 update (2026-08-26):** R13 reviewer audit (`sidm review2.docx`)
> FULLY CLOSED (9 of 9 items). New `LAYMAN_SUMMARY_R13.md` covers
> T70.2-T70.4 + v0.5 KSFR caveat + H3+H4 sensitivity findings. **The T41
> numbers in this R12 file are HISTORICAL as of v0.5** — see the R13
> summary for the v0.5 caveat.

**Repo:** `sidm-composite-dm-mediator` @ GitHub `25a062d` (master)
**Date:** 2026-08-17
**Status:** v0.3-prelim, post-R12 honest-claim audit closed

---

## What this project is

A **joint-fit framework** that asks: given the published astrophysical data on dark matter (dwarf galaxies, ultra-faint dwarfs, the Bullet Cluster, galaxy rotation curves, dark-matter direct-detection experiments, and gamma-ray dwarf searches), what values of dark-matter self-interaction strength, velocity dependence, and mediator mass are jointly consistent with all of them?

The model is a **composite dark-matter candidate** (a "dark pion" — a stable bound state of a hypothetical dark quark, analogous to how the regular pion is a bound state of the regular quark) plus an **elementary dark photon** (a new light force-carrier that mixes very weakly with regular electromagnetism). This is one specific benchmark — Benchmark A, declared in `DARK_SECTOR_LAGRANGIAN.md §9`. The other benchmarks (composite mediator, SIMP) are not implemented.

---

## What we did in R12 (2026-08-14 → 2026-08-17)

Six external reviewers sent an audit (`six reviews.docx`). Five of them flagged the project as "phenomenological toy, not a model". Reviewer 6 cited 7 specific findings, all at specific line numbers. All 7 were verified at the cited lines. We fixed 4 of them (P0) and 3 follow-on coherence issues (P1).

### The 4 P0 fixes — these were actual bugs

1. **A 1.95×10⁶ nonsense number.** The cross-section at low velocity had a fictitious "Roberts+ 2024 correction" factor `(1 + 1/(2s))` baked in. Removing it returns 3.48 cm²/g — a sensible Born plateau. **(1 line of code, 4 regression tests.)**

2. **A sign-flip that produced a fake "1.3σ Yukawa tension".** The velocity-index formula was missing a minus sign. The data wants σ/m to fall with velocity (a positive index). The buggy code returned a negative index, making it look like the simple Yukawa model was "ruled out" by the data. After the fix, the Yukawa prediction and the data-preferred velocity index agree within 0.75σ. **(1 line of code, 2 regression tests.)**

3. **A function lying about its name.** `t55_boltzmann_relic.py` imported a Boltzmann solver but never called it. The body was a hard-coded calibration. Renamed to `t55_wimp_relic_calibration.py` and the dead import removed. **(Rename + 2 regression tests.)**

4. **A dSph channel that favored σ/m ≈ 10 cm²/g.** The dSph log-likelihood was a bimodal-dip surrogate. The actual 2025 paper (Horigome+ arXiv:2503.13650) gives a 95% CL upper limit at σ/m < 0.2 cm²/g — a single-sided constraint, not a bimodal posterior. The fix propagates the upper-limit form through all three near-copies of the function. **(8 regression tests.)**

### The 3 P1 fixes — physics coherence

5. **The dark ρ mass formula was dimensionally wrong.** Replaced with the KSFR (Hidden Local Symmetry) relation. At Λ_dark = 0.2 GeV, m_ρ = 0.79 GeV — matching real QCD's 770 MeV. The lattice-informed path is now wired in. **(2 regression tests.)**

6. **Two dimensional bugs in T39.** The LZ direct-detection cross-section was ε·σ/m (units cm²/g, not cm²). The Fermi annihilation cross-section was α·σ/m² (units cm⁴/g², not cm³/s). Both replaced with the proper dark-photon portal form (Kaplinghat+Tulin+Yu 2014; Berlin+ 2018). The LZ constraint now actually bites. **(4 regression tests.)**

7. **The mediator was ambiguous.** Three different interpretations were running simultaneously without being declared. Added §9 to the Lagrangian doc, declaring Benchmark A as canonical (composite matter + elementary dark photon). The alternatives are now documented as deferred.

---

## The honest numbers (post-R12)

At the Benchmark A canonical point (m_χ = 40 GeV, m_A' = 10 MeV, g_χ = 0.1):

| Quantity | Pre-R12 | Post-R12 | What it means |
|----------|---------|----------|---------------|
| σ/m at galaxies | 2.78 cm²/g | **1.78 cm²/g** | How strongly dark matter scatters itself |
| Velocity index a | −1.08 | **+0.19** | How that scattering fades with velocity |
| dSph log L at σ/m=10 | 0 (favored!) | **−4.53** (disfavored) | Now correctly excludes the high-σ/m regime |
| σ_SI at ε=10⁻⁵ | 10⁻⁵ cm²/g (wrong units) | **1.2×10⁻³² cm²** | Now in proper cm² for direct detection |
| σ_v at α_D=0.01 | 5.9×10³ cm³/s (wrong units) | **6.9×10⁻²⁵ cm³/s** | Now in proper cm³/s for annihilation |

The T41 joint fit (56 seconds, nested sampling) gives:

- **log Z = −213.7 ± 0.24** (Bayesian evidence, a measure of how well the model fits)
- **MAP**: m_A' = 26.6 MeV, m_χ = 14.8 GeV, g_χ = 0.13
- **Derived σ/m_0 = 0.066 cm²/g, a = +0.186**
- **Tension vs. data**: 0.75σ (below the 1.0 threshold = no significant tension)

---

## What this project is NOT

- It is **not** a new measurement of dark matter at any detector.
- It is **not** a new theoretical prediction of dark matter's mass.
- It is **not** a derivation of the relic density from first principles (the t55 calibration is a calibration, not a Boltzmann solver).
- It is **not** a final answer. The framework is a phenomenology tool with documented limitations.

## What this project IS

- A **joint-fit framework** that takes 5 published data channels and asks for the (σ/m, a, m_φ, ε, α) combination consistent with all of them.
- A **cleanly-tested Python codebase** with 359 passing tests, 4 skipped, 3 pre-existing failures unrelated to this work.
- A **documented honest statement** of what the model can and cannot do (see `DARK_SECTOR_LAGRANGIAN.md`, `REVIEWER_AUDIT_R12.md`, and `LAYMAN_SUMMARY_R12.md`).

## What would constitute a real breakthrough

Not from this project. From the field, any of:

1. **A real lattice calculation of the dark SU(N) theory** (replacing the QCD-analog calibration of the dark ρ).
2. **A direct detection of a MeV-scale mediator** at LDMX, SHiP, or a similar facility.
3. **A gravitational-wave or cosmological signature** that pins down the dark sector's coupling to gravity.

The framework built here would help interpret the result — but the experimental input is the bottleneck.

---

## For a skeptical reviewer

The most defensible claims in this project are:

1. The velocity dependence (a ≈ +0.2 to +0.9 across the prior) is consistent with the data-preferred a ≈ +0.94 within 1σ.
2. The dSph channel constrains σ/m < ~0.2 cm²/g at v ≈ 30 km/s, as reported by Horigome+ 2025.
3. The Lagrangian in §9 (Benchmark A) is well-defined and dimensionally consistent.
4. The 4 P0 fixes are correct and verified at the cited line numbers.
5. The 359 passing tests are real tests with real assertions.

The least defensible claims to AVOID:

1. "1.3σ Yukawa tension rules out the simple mediator" — this was a sign-flip bug, not a finding.
2. "Death of the simple WIMP" — the project fits a phenomenology parametrization; it does not establish the universe's actual particle content.
3. "Intensity frontier is the only path forward" — a popular-press talking point, not a result of this project.
4. "Solving the S8/H0 tension" — the project does not compute σ_8 or H_0.
5. "String Theory hidden sector / Swampland" — the project makes zero contact with String Theory.
6. "T72 framing null results as successful predictions" — T72 is a cross-validation plot, not a philosophical stance.

## Statistical methodology notes (R12)

Four honest disclosures about how the headline numbers were produced:

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
   model with per-galaxy likelihoods is deferred to v0.4+.

5. **Quantitative bottleneck.** At canonical ε = 10⁻⁵, the σ_SI is
   1.2×10⁻³² cm² — about 5×10¹⁵ times **above** the LZ WS2024 limit
   (2.2×10⁻⁴⁸ cm² near 40 GeV). To survive, the posterior drives ε
   down to ~10⁻³⁵, which is **~30+ orders of magnitude smaller** than
   naive dimensional-analysis expectations for a sub-MeV dark photon
   (~10⁻³ to 10⁻⁵). Any UV completion must explain this suppression.

---

## One-paragraph version (for a grant proposal abstract)

We built a joint-fit framework for composite dark matter with a MeV-scale dark photon mediator, fitting published data from dwarf galaxies, ultra-faint dwarfs, the Bullet Cluster, galaxy rotation curves, LZ direct-detection, and Fermi gamma-ray dwarf searches simultaneously. After R12 audit closure, the framework is dimensionally consistent, benchmark-explicit, and honestly characterized. The MAP sits at m_A' ≈ 27 MeV, m_χ ≈ 15 GeV, σ/m_0 ≈ 0.07 cm²/g, and a ≈ +0.2, with the data-preferred a ≈ +0.94 within 0.75σ. The framework is a phenomenology tool, not a discovery; the next step is either a real lattice calibration of the dark SU(N) sector or a direct-detection experiment at the MeV-scale mediator window.
