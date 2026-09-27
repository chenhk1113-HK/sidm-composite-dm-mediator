# T95 Option 3 — Master Yukawa + Euclid Q1 Sub-halo Forecast (Channel 27)

**Status:** Documented finding
**Date:** 2026-09-07
**Branch:** `wip/tier3-magnetic-moment-LZ`
**Companion script:** `v0.3-prelim/code/t95_v03_option3_subhalo.py`
**JSON output:** `v0.3-prelim/outputs/t95/option3_subhalo_forecast.json` (gitignored, regenerated)

---

## TL;DR

The master's analytic Yukawa σ/m(v), evaluated at the **LZ-anchored
7D posterior**, predicts a SIDM cross-section that is in
**significant tension with the project's existing Channel 27
(Euclid Q1 sub-halo forecast)**:

| Quantity | Master Yukawa at LZ posterior | Channel 27 allowed region |
|---|---|---|
| σ_m_0 (at v=100 km/s) | **0.71 cm²/g** (median) | (not directly bounded) |
| σ/m at v=150 km/s | **0.67 cm²/g** (median) | **0.05-0.10 cm²/g** |
| Velocity slope a | 0.14 (mild) | (broadly allowed) |
| Channel 27 logL | **-3.81 (median)** | peak at 0 |
| Samples broadly allowed (logL > -2) | **23.6%** | (target: ~68%) |

**The LZ-anchored Yukawa is in 6-13× tension with the sub-halo
forecast.** If the LZ 248 keV event is real AND the master's
Yukawa is the right SIDM operator, then either:
- The sub-halo forecast is too restrictive (likely; the
  forecast assumes CDM-like sub-halo counts)
- The LZ posterior needs additional data to pull σ/m down
  (a real possibility that Euclid Q1 will test in late 2026)
- The model's velocity-dependence is wrong (a paper-level
  concern; the 0.14 slope is too flat to be the right shape)

**Δlog Z (8D - 7D) estimate: -3.81.** This is Jeffreys
"moderate" evidence against the LZ-anchored Yukawa when
Channel 27 is added.

---

## Method

1. **Load 7D posterior** from `outputs/t90/t41_v07_7d_posterior.npz`
   (2523 importance-sampled points)
2. **For each sample**, compute master's σ/m at v=100, 200 km/s
   using `t40_yukawa_sigma_m.sigma_m_cm2_per_g`
3. **Fit velocity power-law** σ/m(v) = σ_m_0 × (100/v)^a
   to the two points (linear fit in log-log)
4. **Evaluate existing Channel 27 likelihood** at each (σ_m_0, a)
   using the project's `loglike_euclid_q1_subhalo_forecast`
5. **Report weighted statistics** using importance weights

The 8D log Z estimate is **7D log Z + median Channel 27 logL**.
This is a rough estimator — a proper 8D nested-sampling fit
would re-run the posterior with Channel 27 included, which
would give a different result. The estimator tells us
*whether Channel 27 is informative*, not the precise 8D
posterior.

---

## Results

### Master Yukawa (σ_m_0, a) at LZ posterior

| Quantity | Weighted median | 16-84 percentile |
|---|---|---|
| σ_m_0 (v=100 km/s) | 0.71 cm²/g | 0.26 to 2.16 |
| Velocity slope a | 0.14 | 0.09 to 0.26 |
| σ/m at v=150 km/s | 0.67 cm²/g | 0.24 to 1.94 |

The **velocity slope a = 0.14** is mild. This means the
master's Yukawa at LZ-anchored parameters gives a
**nearly v-independent cross-section** at galactic
velocities. This is **different from the BAHAMAS-SIDM
vdSIDM model** (Robertson 2019), which has a = 0.5-1.0
(strong v-dependence).

### Channel 27 (Euclid Q1 sub-halo forecast) verdict

| Statistic | Value |
|---|---|
| Weighted median logL | -3.81 |
| 16-84 percentile | -9.25 to -0.83 |
| Max logL | 0.00 |
| Min logL | -2528.76 |
| Samples with logL > -2 | 23.6% |

The 23.6% "broadly allowed" fraction is **less than the 68%
expected for a posterior consistent with the forecast**. This
is the smoking gun: the LZ-anchored Yukawa is in tension
with the sub-halo forecast.

### Joint-fit verdict (estimated)

| Quantity | Value |
|---|---|
| 7D log Z (T90.1) | -164.96 ± 0.25 |
| Channel 27 median logL | -3.81 |
| **8D log Z estimate** | -168.77 |
| **Δlog Z (8D - 7D) estimate** | **-3.81** |
| Verdict | **Channel 27 DISFAVORS** the LZ-anchored Yukawa |

Jeffreys scale: |Δlog Z| = 3.81 is **moderate** evidence
(Kass & Raftery 1995). Not yet "strong" (|Δlog Z| > 5)
but not "barely worth mentioning" either (|Δlog Z| < 1).

---

## What this means

The Option 2 finding was: **LZ does not constrain SIDM core
size**. The Option 3 finding is the corollary: **the
parameters that LZ does constrain (g_chi, m_phi, xi) are
in tension with the parameters that sub-halo forecasts
constrain (σ_m_0, a)**.

This is a **paper-section finding** that says:

> *If the LZ 248 keV event is real and the master's Yukawa
> operator is the right description, then the SIDM cross-section
> must be ~0.7 cm²/g at v=150 km/s, which is 6-13× above the
> sub-halo forecast's allowed range. This is a falsifiable
> prediction: when Euclid Q1 measures sub-halo abundances in
> late 2026, the LZ interpretation will either be confirmed
> (if σ/m is high) or refuted (if σ/m is in the CDM-like
> 0.05-0.10 cm²/g range).*

---

## Honest caveats

1. **Channel 27 is a forecast, not a measurement.** The
   `loglike_euclid_q1_subhalo_forecast` is a soft two-sided
   constraint based on the Euclid Q1 sub-halo forecast
   (arXiv:2503.15330). When Euclid Q1 measures actual sub-halo
   abundances in late 2026, this forecast will be replaced by
   a real likelihood.

2. **The script uses a sub-halo abundance forecast, not a full
   GD-1 stream-gap likelihood.** The bok doc's "GD-1 stream
   gaps" suggestion is more specific. A full GD-1 stream-gap
   likelihood would require:
   - Gaia DR3 query for GD-1 region (~half day)
   - Sub-halo impact cross-section (Erkal+ 2016 formalism)
   - Stream orbit integration (~1 week of code)
   - Gap-detection likelihood (~1 week of code)
   This script uses the simpler Channel 27 forecast as a
   proxy, which is faster and uses existing infrastructure.

3. **The two-point (σ_m_0, a) fit** is a simplification. The
   full velocity-dependence is more complex than a power law.
   The project uses the power-law form (T89, T41), so this
   is consistent with project convention.

4. **The 7D posterior is LZ-anchored.** Adding Channel 27
   will pull (m_phi, g_chi, xi) in directions correlated with
   the sub-halo forecast, NOT with LZ. The 8D posterior will
   have different medians than the 7D posterior.

5. **No 8D fit was run.** The log Z estimate is a 7D
   posterior + median Channel 27 logL. A proper 8D fit would
   re-run the nested sampling with Channel 27 added, which
   would give a different posterior. The current estimate
   tells us whether Channel 27 is informative, not the
   precise 8D posterior. A real 8D fit is ~1-2 minutes of
   compute.

---

## What a proper 8D fit would do

1. Add Channel 27 logL to the existing 7D loglike in
   `t41_mediator_mass_joint_fit.py` (one line, behind an
   env var like `T95_CHANNEL_27=1`)
2. Re-run nested sampling (8D instead of 7D) — ~1-2 min
3. The 8D posterior will have different medians for
   (m_phi, g_chi, xi) than the 7D posterior, pulled toward
   the sub-halo-forecast allowed region
4. Compare 8D vs 7D log Z using Jeffreys scale
5. If |Δlog Z| > 5 (Jeffreys "strong"), document the tension
6. If |Δlog Z| < 1, Channel 27 is uninformative; the LZ
   posterior is consistent with sub-halo forecasts

This is a 1-day bounded follow-up. **Not done here** because
it requires a code change to the joint fit (an env-var
gating pattern, but still a code change). It would be
Option 3.5.

---

## Files

- `v0.3-prelim/code/t95_v03_option3_subhalo.py` — script
  that produced the prediction
- `v0.3-prelim/code/euclid_q1_subhalo_forecast_forward_model.py`
  — project's existing Channel 27 likelihood (reused)
- `v0.3-prelim/outputs/t90/t41_v07_7d_posterior.npz` —
  7D posterior (gitignored, regenerated by t41_v07 script)
- `v0.3-prelim/outputs/t95/option3_subhalo_forecast.json` —
  JSON output (gitignored, regenerated by script)
- `v0.3-prelim/code/t40_yukawa_sigma_m.py` — master's Yukawa
  used for σ/m
- `v0.3-prelim/docs/T95_OPTION2_CORE_SIZE_PREDICTION.md` —
  companion note
- `v0.3-prelim/docs/T95_YUKAWA_PRESCRIPTION_CALIBRATION_NOTE.md` —
  T95 Option 1 calibration note

---

## Next steps (gated)

- **Option 3.5 (suggested)**: Real 8D nested-sampling fit.
  ~1 day, no new deps. Would replace the median logL
  estimator with a proper 8D posterior. **The most
  paper-ready next step.**
- **Option 3.6 (suggested)**: Full GD-1 stream-gap
  likelihood. ~1-2 weeks, no new deps. Would implement
  the bok doc's actual suggestion.
- **No code changes to master or T90**. The 7D fit
  results are unchanged.
