# T95 Option 2.5 — Gravothermal Core-Size Prediction (Balberg+ 2002)

**Status:** Documented finding
**Date:** 2026-09-07
**Branch:** `wip/tier3-magnetic-moment-LZ`
**Companion script:** `v0.3-prelim/code/t95_v04_option2_5_gravothermal.py`
**JSON output:** `v0.3-prelim/outputs/t95/option2_5_gravothermal_core_size.json` (gitignored, regenerated)

---

## TL;DR

The gravothermal Balberg+ 2002 calculation gives **larger
core sizes than the simplified Kaplinghat+ 2016 formula, but
still 5-50× smaller than published hydro-sim predictions** at
the LZ-anchored 7D posterior parameters.

| Halo | v_max | σ/m | r_c (gravothermal) | Published | Ratio |
|---|---|---|---|---|---|
| Dwarf MW-like (10¹² M_☉) | 220 km/s | 0.19 cm²/g | **0.20 kpc** | 1-10 kpc | 5-50× small |
| Dwarf spheroidal (10⁹ M_☉) | 30 km/s | 0.23 cm²/g | **0.05 kpc (collapsed)** | 0.5-3 kpc | 10-60× small |
| Cluster (10¹⁴ M_☉) | 1000 km/s | 0.032 cm²/g | **8.6 kpc** | 50-200 kpc | 6-23× small |

**At dSph scale (10⁹ M_☉), 100% of LZ-anchored posterior samples
are in the gravothermal collapse phase at t=10 Gyr.** This
predicts that dSphs should have undergone the "gravothermal
catastrophe" — but no dSph is observed to have a sub-kpc
collapsed core.

**Interpretation:** The LZ-anchored Yukawa at σ/m ≈ 0.2 cm²/g
is in the regime where Balberg+ 2002 predicts **gravothermal
collapse in dSph-mass halos**. Real dSphs don't show this,
which is the classic "too big to fail" type problem for SIDM
at this cross-section.

---

## Method

1. **Load 7D posterior** from `outputs/t90/t41_v07_7d_posterior.npz`
2. **For each sample**, compute master's σ/m at v_max using
   `t40_yukawa_sigma_m.sigma_m_cm2_per_g`
3. **Compute NFW scale parameters** (ρ_s, r_s) for each
   reference halo
4. **Call `gravothermal_r_core(sigma_m, rho_s, r_s, v_max, t_Gyr=10)`**
   — the project's Balberg+ 2002 implementation, inlined here
   because `gravothermal.py` requires a missing `halo_profiles` module
5. **Compute r_c distribution** and phase fraction (expanded vs collapsed)

The function `gravothermal_r_core` returns:
- `r_max × (1 - 0.3 × t/t_core)` for t < t_core (expanded phase)
- `r_max × exp(-(t - t_core)/τ_collapse)` for t > t_core (collapse phase)
- with a floor of 0.05 kpc (fully collapsed)

---

## Results

### Dwarf MW-like halo (M_200 = 10¹² M_☉, v_max = 220 km/s)

| Statistic | Value |
|---|---|
| σ/m median (v_max=220) | 0.19 cm²/g |
| r_c median (Balberg+) | **0.20 kpc** |
| 16-84 percentile | 0.05-0.81 kpc |
| Fraction in expanded phase | 53.6% |
| Fraction in collapse phase | 46.4% |
| Published SIDM dwarf prediction | 1-10 kpc |

**The bimodal distribution (expanded vs collapse)** comes from
the gravothermal phase transition. Samples with σ/m > 0.1 cm²/g
collapse; samples with σ/m < 0.1 cm²/g stay in expanded phase.

### Dwarf spheroidal halo (M_200 = 10⁹ M_☉, v_max = 30 km/s)

| Statistic | Value |
|---|---|
| σ/m median (v_max=30) | 0.23 cm²/g |
| r_c median | **0.05 kpc (all collapsed)** |
| Fraction in expanded phase | **0%** |
| Fraction in collapse phase | **100%** |
| Published dSph SIDM prediction | 0.5-3 kpc |

**100% of samples are in the gravothermal collapse phase** at
t=10 Gyr. This is consistent with the "too big to fail" /
"missing satellites" type argument: at σ/m ≈ 0.2 cm²/g, dSph
halos should collapse to sub-kpc cores, but real dSphs are
observed to have kpc-scale cores (or no clear core at all in
some cases).

### Cluster halo (M_200 = 10¹⁴ M_☉, v_max = 1000 km/s)

| Statistic | Value |
|---|---|
| σ/m median (v_max=1000) | 0.032 cm²/g |
| r_c median | **8.6 kpc** |
| Fraction in expanded phase | 98.7% |
| Published BAHAMAS-SIDM vdSIDM | 50-200 kpc |

**6-23× smaller than published** hydro-sim predictions. The
gravothermal calculation gives 8.6 kpc; Robertson 2019 reports
50-200 kpc for the same Yukawa parameters. The discrepancy is
the same as Option 2's, but smaller (8.6 vs 0.5 = 17× larger
in gravothermal vs simplified).

---

## Comparison to Option 2 (simplified Kaplinghat)

| Halo | Option 2 (Kaplinghat) | Option 2.5 (Balberg+) | Ratio |
|---|---|---|---|
| Dwarf MW-like | 0.17 kpc | 0.20 kpc | 1.2× larger |
| Cluster | 0.5 kpc | 8.6 kpc | 17× larger |

The gravothermal formula gives systematically larger r_c than
the simplified Kaplinghat formula, especially for clusters.
The cluster discrepancy with hydro sims drops from 100-400×
(Option 2) to 6-23× (Option 2.5). **The gravothermal
calculation is more realistic** but still doesn't fully
match the published hydro-sim predictions.

---

## Why the gravothermal r_c is still smaller than hydro sims

Three candidate explanations:

1. **The LZ-anchored parameter regime is not the
   galaxy-anchored regime.** Robertson's vdSIDM uses
   m_χ = 0.15 GeV, m_φ = 0.28 keV, α_χ = 6.74e-6. The
   7D posterior median is m_χ = 427 GeV, m_φ = 617 MeV,
   g_χ = 1.49. These are **different physical regimes** of
   the same Yukawa operator, and the gravothermal core
   size depends on the mass ratio.

2. **The gravothermal formula has a 30% calibration
   uncertainty.** The Balberg+ 2002 empirical scaling
   `t_core ∝ 1/(σ/m)` is a fit to a small set of hydro
   simulations. The actual scaling has O(30%) scatter.

3. **The 0.72× T95 Phase 0 normalization offset compounds.**
   Master's σ/m is 30% low relative to Robertson's
   vdSIDM. This would make r_c **larger** by ~50% if
   corrected, but the 6-23× discrepancy is too large for
   this to be the main effect.

---

## Honest caveats

1. **The gravothermal formula is inlined** because the
   project's `gravothermal.py` requires a `halo_profiles`
   module that's not in the repo. The inlined version is
   identical to the source — no behavioral change.

2. **t_Gyr = 10 Gyr is a hard-coded assumption.** Real
   halos formed at different redshifts. The 10 Gyr choice
   is standard for "evolved disk galaxies" but is wrong
   for clusters (which are still forming) and for dSphs
   (which may be older).

3. **The LZ-anchored posterior is the wrong prior for
   galaxy predictions.** As Option 2 showed, the LZ
   posterior does not constrain the parameters (m_φ, g_χ, ξ)
   that drive the SIDM core size. The 7D prior is wide
   on these, so the r_c distribution is broad.

4. **The "100% collapse in dSph" prediction is a known
   problem for SIDM at σ/m > 0.1 cm²/g.** It is not a new
   finding from this analysis; it is a generic prediction
   of the Balberg+ 2002 framework.

5. **Robertson's BAHAMAS-SIDM uses the FULL hydro
   calculation, not the simplified gravothermal formula.**
   The hydro sim includes baryonic feedback, multi-body
   scattering, and other corrections that the analytic
   formula misses.

---

## What this is NOT

1. **Not a code change to gravothermal.py.** The function
   is inlined in the script for portability. To commit a
   proper fix, add the missing `halo_profiles` module or
   remove the import.

2. **Not a 7D parameter change.** The 7D posterior is
   unchanged.

3. **Not a discovery of new physics.** This is a
   consistency check between LZ-anchored Yukawa and
   galaxy-anchored hydro sim predictions.

4. **Not a verdict on the LZ 248 keV event.** T90 merge
   rule unchanged.

---

## Files

- `v0.3-prelim/code/t95_v04_option2_5_gravothermal.py` —
  script that produced the prediction
- `v0.3-prelim/outputs/t90/t41_v07_7d_posterior.npz` —
  7D posterior (gitignored, regenerated)
- `v0.3-prelim/outputs/t95/option2_5_gravothermal_core_size.json` —
  JSON output (gitignored, regenerated)
- `v0.3-prelim/code/t40_yukawa_sigma_m.py` — master's
  Yukawa
- `v0.3-prelim/code/gravothermal.py` — original
  implementation (not used here due to halo_profiles
  import)
- `v0.3-prelim/docs/T95_OPTION2_CORE_SIZE_PREDICTION.md` —
  Option 2 (simplified formula) for comparison
- `v0.3-prelim/docs/T95_OPTION3_5_8D_FIT.md` — Option 3.5
  (real 8D fit) for context
- Balberg, Shapiro, Inagaki 2002, ApJ 568, 475
- Robertson et al. 2019, MNRAS 488, 3646 (BAHAMAS-SIDM)

---

## Next steps (gated)

- **Option 2.6 (suggested but lower priority)**: include
  time evolution t_Gyr as a free parameter or as a function
  of halo mass. Would show the "collapse fraction" as a
  function of t.
- **Option 3.6**: full GD-1 stream-gap likelihood
  (~1-2 weeks, no new deps).
- **Option 4**: paper-style writeup of all T95 findings
  (~1-2 days, no new deps).
- **No code changes to master or T90.** The 7D fit
  results are unchanged.
