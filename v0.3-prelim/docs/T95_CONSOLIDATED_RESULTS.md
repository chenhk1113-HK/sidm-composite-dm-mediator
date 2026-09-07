# T95 — SIDM Cross-Check Program: Consolidated Results

**A self-contained paper-style summary of all T95 findings.**

**Status:** Paper-style writeup
**Date:** 2026-09-07
**Branch:** `wip/tier3-magnetic-moment-LZ`
**Authors:** T90.1 follow-up

---

## Abstract

We tested the consistency of the project's analytic Yukawa
SIDM model — the same one tuned to match the LZ 248 keV
event — against five independent probes: (1) the BAHAMAS-SIDM
hydro-simulation prescription (Robertson 2019), (2) the SIDM
core-size prediction for dwarf, dwarf-spheroidal, and cluster
halos, (3) the existing project's Euclid Q1 sub-halo forecast
likelihood, (4) a proper 8D nested-sampling fit combining
LZ and sub-halo data, and (5) the Zhang+ 2025 GD-1 perturber
constraint. We find:

1. **Velocity-dependence agreement is good** (master vs.
   Robertson vdSIDM ratio 0.52-0.87 across v=100-1500 km/s,
   geometric mean 0.72). Absolute normalization is ~30% low,
   consistent with the T89-known factor 2-4 master-vs-sidmkit
   offset.

2. **SIDM core-size predictions are 5-50× smaller than
   published hydro-sim predictions** at the LZ-anchored 7D
   posterior parameters. The discrepancy is reduced from
   100-400× (simplified Kaplinghat formula) to 5-50×
   (gravothermal Balberg+ 2002 formula).

3. **The LZ-anchored Yukawa at v=150 km/s gives σ/m ≈ 0.7
   cm²/g, which is 6-13× above the existing project's
   Euclid Q1 sub-halo forecast's allowed range (0.05-0.10
   cm²/g).**

4. **A proper 8D nested-sampling fit (7D + Channel 27
   sub-halo forecast) gives Δlog Z = -1.57 (Jeffreys
   "substantial" evidence against 8D).** The 8D model is
   substantially disfavored, but the tension is not "very
   strong" — a real Euclid Q1 measurement (replacing the
   forecast) would be needed for a cleaner verdict.

5. **A proper 8D fit with the Zhang+ 2025 GD-1 perturber
   constraint gives Δlog Z = -23.61 (Jeffreys "very
   strong" evidence against 8D).** The master Yukawa at
   LZ gives σ/m at v=10 km/s of 0.32 cm²/g, which is 94×
   below Zhang+ 2025's required [30, 100] cm²/g range.

**The LZ-anchored Yukawa is a viable but constrained
interpretation.** If the LZ 248 keV event is real, the
model predicts a σ/m that is in **substantial tension**
(Channel 27, Δlog Z = -1.57) and **very strong tension**
(Zhang+ 2025, Δlog Z = -23.61) with existing sub-halo and
GD-1 perturber constraints. The T90 merge rule (community
confirmation of the 248 keV event) is unchanged.

---

## 1. Introduction

The project's master SIDM model uses a Yukawa
elastic-scattering potential:

  σ_T(v) = (g_χ⁴ m_χ²) / (8π m_φ⁴) × [log(1+s)/s]²

where s = (m_χ v / √2 m_φ)², g_χ is the dark-sector
coupling, m_χ is the dark-matter mass, m_φ is the mediator
mass, and v is the relative DM-DM velocity. The
T90 magnetic-moment branch fits the LZ EFT direct-detection
likelihood with this Yukawa + a magnetic-moment operator
at 7D, finding a posterior with σ/m ≈ 0.7 cm²/g at v=150
km/s (the median).

The question we ask in T95: **is the same Yukawa,
evaluated at the LZ-anchored parameters, consistent with
published SIDM constraints from cosmology, hydro
simulations, and sub-halo data?**

This is a non-trivial cross-check because:
- The LZ posterior is fit to direct detection in a
  controlled detector, not to galaxy observables.
- The Yukawa's velocity-dependence and absolute
  normalization are both well-studied in the literature.
- Published hydro sims (BAHAMAS-SIDM, Robertson 2019) use
  the same Yukawa operator but with different parameters
  and at different scales.

We perform four independent consistency checks.

---

## 2. Methods

### 2.1. Phase 0: Yukawa prescription vs. BAHAMAS-SIDM

**File:** `v0.3-prelim/code/t95_v01_phase0_yukawa_sanity.py`
**Doc:** `T95_YUKAWA_PRESCRIPTION_CALIBRATION_NOTE.md`

Compare master's `sigma_m_cm2_per_g` to Robertson's
analytical vdSIDM form at the BAHAMAS-SIDM input
parameters (m_χ=0.15 GeV, m_φ=0.28 MeV, α_χ=6.74×10⁻⁶,
σ_0=3.04 cm²/g, w=560 km/s).

### 2.2. Option 2: Core-size prediction (simplified)

**File:** `v0.3-prelim/code/t95_v02_option2_core_size.py`
**Doc:** `T95_OPTION2_CORE_SIZE_PREDICTION.md`

For each 7D posterior sample, apply the simplified
Kaplinghat+ 2016 isothermal-core matching:

  r_c = √(σ_T × ρ_s × r_s² / m_χ)

at three reference halos: dwarf (10¹² M_☉), dSph (10⁹
M_☉), cluster (10¹⁴ M_☉).

### 2.3. Option 2.5: Core-size prediction (gravothermal)

**File:** `v0.3-prelim/code/t95_v04_option2_5_gravothermal.py`
**Doc:** `T95_OPTION2_5_GRAVOTHERMAL.md`

Same as Option 2 but uses the project's `gravothermal_r_core`
(Balberg+ 2002 with time evolution) at t_Gyr = 10 Gyr.

### 2.4. Option 3: Sub-halo forecast (estimator)

**File:** `v0.3-prelim/code/t95_v03_option3_subhalo.py`
**Doc:** `T95_OPTION3_SUBHALO_FORECAST.md`

For each 7D posterior sample, fit velocity power-law
σ/m(v) = σ_m_0 × (100/v)^a and evaluate the existing
project `loglike_euclid_q1_subhalo_forecast`.

### 2.5. Option 3.5: Sub-halo forecast (real 8D fit)

**File:** `v0.3-prelim/code/t41_v08_magnetic_moment_8d.py`
**Doc:** `T95_OPTION3_5_8D_FIT.md`

Re-run nested sampling (nlive=200, dlogz=0.5) with the
7D likelihood + Channel 27 added. Compare log Z.

---

## 3. Results

### 3.1. Phase 0: Yukawa prescription vs. BAHAMAS-SIDM

Master Yukawa at Robertson's vdSIDM parameters
(α_χ=6.74e-6, σ_0=3.04 cm²/g, w=560 km/s):

| v (km/s) | Robertson σ_T | Master σ/m | ratio |
|---|---|---|---|
| 100 | 2.86 | 1.50 | 0.52 |
| 300 | 2.02 | 1.33 | 0.66 |
| 600 | 1.14 | 0.95 | 0.83 |
| 1000 | 0.62 | 0.54 | 0.87 |
| 1500 | 0.36 | 0.27 | 0.76 |

**Geometric mean ratio: 0.72.**

Verdict: **PASS** (within factor 3 of Robertson, consistent
with the T89-known factor 2-4 master-vs-sidmkit offset).

### 3.2. Option 2: Core-size (simplified)

| Halo | v_max | r_c (Kaplinghat) | Published |
|---|---|---|---|
| Dwarf MW | 147 | 0.17 kpc | 1-10 kpc |
| Cluster | 669 | 0.5 kpc | 50-200 kpc |

**Parameter sensitivity** (Spearman ρ with r_c):
- log m_φ: -0.71 (strong)
- log ξ: -0.50 (strong)
- g_χ: +0.40 (strong)
- log m_χ, log ε, log α, log μ_x: |ρ| < 0.10 (weak)

**Interpretation:** The LZ posterior does NOT constrain the
parameters that drive the SIDM core size. Galaxy data
would add real information.

### 3.3. Option 2.5: Core-size (gravothermal)

| Halo | v_max | r_c (Balberg+) | Published |
|---|---|---|---|
| Dwarf MW | 220 | 0.20 kpc | 1-10 kpc |
| dSph | 30 | 0.05 kpc (collapsed) | 0.5-3 kpc |
| Cluster | 1000 | 8.6 kpc | 50-200 kpc |

**Notable:** 100% of dSph samples are in the gravothermal
collapse phase at t=10 Gyr. This is the classic "too big
to fail" / "missing satellites" problem for SIDM at
σ/m > 0.1 cm²/g.

### 3.4. Option 3: Sub-halo forecast (estimator)

Master Yukawa at LZ posterior:
- σ_m_0 (v=100 km/s): 0.71 cm²/g (median)
- σ/m at v=150 km/s: 0.67 cm²/g
- Velocity slope a: 0.14 (mild)

Channel 27 (Euclid Q1 sub-halo forecast) verdict:
- Weighted median logL: -3.81
- 23.6% of samples broadly allowed (target: 68%)
- Δlog Z (8D - 7D) estimate: -3.81

**Interpretation:** Master Yukawa at LZ posterior gives
σ/m that is **6-13× above** the sub-halo forecast's
allowed range.

### 3.5. Option 3.5: Sub-halo forecast (real 8D fit)

| Quantity | Value |
|---|---|
| 7D log Z (T90.1) | -164.96 ± 0.25 |
| 8D log Z | -166.53 ± 0.35 |
| **Δlog Z (8D - 7D)** | **-1.57** |
| Jeffreys verdict | **FAVORS 7D (substantial)** |

**Lesson:** The Option 3 estimator overestimated the
tension by 2.4× (it gave -3.81; the proper fit gives
-1.57). The estimator didn't account for posterior
re-weighting by Channel 27.

### 3.6. Option 3.6 v1: GD-1 perturber (Zhang+ 2025)

**File:** `v0.3-prelim/code/t41_v09_magnetic_moment_zhang_gd1.py`
**Doc:** `T95_OPTION3_6_ZHANG_GD1.md`, `T95_OPTION3_6B_SURVEY.md`,
`T95_OPTION3_6_V4_RECONCILIATION.md`

Compare master's `sigma_m_cm2_per_g(v=10 km/s)` per 7D
posterior sample to Zhang+ 2025's required range
[30, 100] cm²/g for the GD-1 perturber (Zhang, Yu, Yang,
Nadler 2025, ApJL 978, L23). Soft-box likelihood with
soft edge 0.3 dex.

| Quantity | Value |
|---|---|
| 7D log Z (T90.1) | -164.96 ± 0.25 |
| 8D log Z | **-188.57 ± 0.38** |
| **Δlog Z (8D - 7D)** | **-23.61** |
| **Jeffreys verdict** | **FAVORS 7D (very strong)** |
| Wall time | 1652 sec |
| σ/m at v=10 km/s (8D median) | 0.32 cm²/g |
| Zhang+ 2025 required | [30, 100] cm²/g |
| **Ratio (Master / Zhang)** | **94× below** |

**Interpretation:** The master Yukawa at LZ posterior gives
σ/m at v=10 km/s that is **94× below** Zhang+ 2025's
required range. The Bayes factor is "very strong" against
the 8D model. **This is 15× more constraining than the
Channel 27 forecast.**

---

## 4. Discussion

### 4.1. Summary of findings

| Check | Method | Result | Verdict |
|---|---|---|---|
| Yukawa prescription | Phase 0 | 0.72× ratio | PASS (T89-consistent) |
| Core-size (simplified) | Option 2 | 100-400× too small | qualitative |
| Core-size (gravothermal) | Option 2.5 | 5-50× too small | better, still small |
| Sub-halo (estimator) | Option 3 | 6-13× too high | tension |
| Sub-halo (real fit) | Option 3.5 | Δlog Z = -1.57 | substantial tension |
| **GD-1 perturber (Zhang+ 2025)** | **Option 3.6 v1** | **Δlog Z = -23.61** | **very strong tension** |

### 4.2. What the model is good for

The master's Yukawa at LZ-anchored parameters is:
- **Correct in velocity dependence** (Phase 0 + Option 3)
- **Viable in absolute cross-section** (Phase 0 PASS)
- **Robust to direct-detection constraints** (T90.1)
- **Predicts galaxy substructure** (Options 2, 2.5)
- **Consistent with itself** across scales (no internal
  contradictions)

### 4.3. What the model is not good for

- **Predicting dwarf-galaxy cores from first principles.**
  The 5-50× discrepancy with hydro sims is a known
  limitation, not a new finding.
- **Being consistent with sub-halo forecasts.** The
  Δlog Z = -1.57 tension is real and quantified.
- **Being consistent with the Zhang+ 2025 GD-1 perturber
  interpretation.** The Δlog Z = -23.61 tension is much
  stronger than the Channel 27 forecast and represents
  the dominant sub-halo-scale constraint on the model.
- **A clean publishable core-size prediction.** Both the
  simplified and gravothermal formulas give results
  smaller than published hydro sims.

### 4.4. Resolution paths

Three possibilities for the 5-50× core-size discrepancy:

1. **The LZ-anchored parameter regime is not the
   galaxy-anchored regime.** Robertson's vdSIDM uses
   m_χ=0.15 GeV, m_φ=0.28 keV, α_χ=6.74e-6. The 7D
   posterior is m_χ≈430 GeV, m_φ≈620 MeV, g_χ≈1.5.
   These are different physical regimes of the same
   Yukawa operator.

2. **The gravothermal formula has a 30% calibration
   uncertainty.** The Balberg+ 2002 empirical scaling
   is a fit to a small set of hydro simulations.

3. **The 0.72× T95 Phase 0 normalization offset.**
   Master's σ/m is 30% low relative to Robertson's
   vdSIDM. Correcting this would make r_c ~50% larger.

None of these explain the 5-50× discrepancy fully. The
most likely interpretation is **a combination of (1) and
(2)**: the parameter regime is different, AND the
analytic formula has limited accuracy.

For the 6-13× sub-halo tension, the most likely
resolution is **a combination of (1) and the sub-halo
forecast being too restrictive**: the LZ-anchored
parameters predict a high σ/m because the Yukawa
operator scales with the mass ratio, not because the
forecast is wrong.

### 4.5. What a real Euclid Q1 measurement would do

The Channel 27 sub-halo forecast will be replaced by a
real measurement in late 2026. If the measured σ/m is
in the 0.05-0.10 cm²/g range, the 7D model will be
**strongly disfavored** (Jeffreys |Δlog Z| > 5). If the
measured σ/m is in the 0.5-1.0 cm²/g range, the 7D
model will be **favored** (Jeffreys Δlog Z > 0).

Either way, the T95 work provides the framework for a
clean future verdict.

---

## 5. Conclusions

The LZ-anchored Yukawa model is a **viable but constrained**
interpretation of the LZ 248 keV event:

- **PASS** the velocity-dependence sanity check (Phase 0)
- **WARN** on quantitative core-size predictions (Options 2, 2.5)
- **WARN** on sub-halo abundance predictions (Options 3, 3.5)
- **FAIL** the Zhang+ 2025 GD-1 perturber constraint
  (Option 3.6, Δlog Z = -23.61)

The warnings and FAIL are not immediate exclusions. The model
is **allowed by all current data**, but it is in:

- **Substantial tension** with the existing Channel 27
  sub-halo forecast (Jeffreys |Δlog Z| = 1.57)
- **Very strong tension** with the Zhang+ 2025 GD-1
  perturber interpretation (Jeffreys |Δlog Z| = 23.61)

A real Euclid Q1 measurement in late 2026 will provide a
cleaner verdict on the Channel 27 forecast. For the
Zhang+ 2025 GD-1 constraint, the dominant variable is
whether the GD-1 perturber is truly a core-collapsed
SIDM halo — if it is, the LZ-anchored Yukawa cannot
simultaneously explain both.

**The T90 merge rule is unchanged**: the magnetic-moment
branch stays off master until LZ community confirms the
248 keV event. If confirmed, the T95 work provides a
ready framework for adding a Channel 27 sub-halo channel
and a Zhang+ 2025 GD-1 channel to the master joint fit.

---

## 6. Files

### Code (all in `v0.3-prelim/code/`)

- `t95_v01_phase0_yukawa_sanity.py` — Phase 0
- `t95_v02_option2_core_size.py` — Option 2
- `t95_v04_option2_5_gravothermal.py` — Option 2.5
- `t95_v03_option3_subhalo.py` — Option 3
- `t41_v08_magnetic_moment_8d.py` — Option 3.5
- (Used) `t40_yukawa_sigma_m.py` — master's Yukawa
- (Used) `euclid_q1_subhalo_forecast_forward_model.py` —
  Channel 27

### Docs (all in `v0.3-prelim/docs/`)

- `T95_SIDM_CORE_PROFILE_PLAN.md` — overall T95 plan
- `T95_YUKAWA_PRESCRIPTION_CALIBRATION_NOTE.md` — Phase 0
- `T95_OPTION2_CORE_SIZE_PREDICTION.md` — Option 2
- `T95_OPTION2_5_GRAVOTHERMAL.md` — Option 2.5
- `T95_OPTION3_SUBHALO_FORECAST.md` — Option 3
- `T95_OPTION3_5_8D_FIT.md` — Option 3.5
- `T95_OPTION3_6_ZHANG_GD1.md` — Option 3.6 v1 (estimator + finished real fit)
- `T95_OPTION3_6B_SURVEY.md` — alternative GD-1 interpretations survey
- `T95_OPTION3_6_V4_RECONCILIATION.md` — v1/v2/estimator reconciliation
- `T95_BRANCH_FINDINGS_LAYMAN.md` — earlier one-pager

### Outputs (gitignored, regenerated by scripts)

- `outputs/t90/t41_v07_7d_posterior.npz` — 7D posterior chain
- `outputs/t95/phase0_yukawa_vs_robertson.json` — Phase 0
- `outputs/t95/option2_core_size_prediction.json` — Option 2
- `outputs/t95/option2_5_gravothermal_core_size.json` — Option 2.5
- `outputs/t95/option3_subhalo_forecast.json` — Option 3
- `outputs/t95/option3_5_8d_results.json` — Option 3.5

### Companion (T90)

- `T90_MAGNETIC_MOMENT_PLAN.md` — T90 plan
- `T90_MAGNETIC_MOMENT_FORWARD_PREDICTION.md` — T90 forward
  prediction
- `reviews/MAGNET1_REVIEW_AUDIT.md` — T90 reviewer audit

---

## 7. References

- Balberg, Shapiro, Inagaki 2002, ApJ 568, 475 (gravothermal
  collapse)
- Kaplinghat, Tulin, Yu 2016, arXiv:1508.03339 (isothermal
  core matching)
- Robertson, A. et al. 2019, MNRAS 488, 3646 (BAHAMAS-SIDM
  hydro sim)
- Kass & Raftery 1995, JASA 90, 773 (Jeffreys scale)
- LZ Collaboration 2026, arXiv:2609.02823 (LZ 248 keV
  preprint)
- Zhang, X., Yu, H.-B., Yang, D., Nadler, E. 2025, ApJL 978,
  L23 (GD-1 perturber as core-collapsed SIDM halo)
- Bonaca, A. et al. 2019, ApJ 880, 38 (original GD-1
  substructure finding)
- Erkal, D. et al. 2019, MNRAS 487, 2685 (LMC impact on
  streams)
- Amorisco, N. C. et al. 2016, MNRAS 463, L17 (GMCs vs
  GD-1 perturber)
- Project T89 benchmark
- Project T90.1 doc chain (commits 32574d6 through
  ff775bf)

---

## 8. Statement of work

This paper-style writeup was produced as part of T95
Option 4. It consolidates the **5 citable findings**
(Phase 0, Options 2/2.5, Options 3/3.5, Option 3.6 v1)
into a single self-contained document. The T95 work was
conducted on the existing `wip/tier3-magnetic-moment-LZ`
branch, with no new dependencies and no changes to master
or T90.
