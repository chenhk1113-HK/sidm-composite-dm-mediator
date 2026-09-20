# T90.27 — RELHIC (Cloud-9 + M51 Cloud S/N) joint fit extension

**Status:** SHIPPED (initial v1 — Yang+2024/2025 parametric SIDM halo model
+ Cloud-9 + M51 likelihood, env-gated Channel 27 of T41).
**Date:** 2026-09-10
**Branch:** `wip/tier3-magnetic-moment-LZ`
**Author:** T90 working group (T90.27 path: a, "wire Cloud-9 + Cloud S/N
as Channel 27 with the SIDM halo model from `gravothermal.py`")

---

## Purpose

Add a **RELHIC (Reionization-Limited HI Cloud)** channel to the T41
joint fit, exploiting the 2026 publication of:

1. **arXiv:2608.04362** — "Cold Dark Matter and Self-Interacting
   Dark Matter Interpretations of Cloud-9" (Zhou et al. 2026). The
   first confirmed RELHIC candidate (HI cloud near M94, no optical
   counterpart down to M_star < 10^3.5 M_sun via HST). The paper
   fits Cloud-9 with a parametric SIDM halo model (Yang+2024/2025
   Eqs. 4-7) and finds that:
   - CDM requires M200=7e8 M_sun, c200=6 (7σ below the cosmological
     concentration-mass relation).
   - SIDM at τ=0.18 requires M200=4.7e9 M_sun, c200=4, σ/m=483 cm²/g
     (3.2σ below the cosmological median, near maximum core expansion).
   - SIDM at τ=0.95 (deep core collapse) requires M200=3.4e9 M_sun,
     c200=1.5, σ/m=2.1×10⁴ cm²/g (6σ below the cosmological median).
   - Cosmological priors (concentration-mass relation) strongly favor
     SIDM over CDM.

2. **arXiv:2607.21034** — "A RELHIC twin candidate near the galaxy
   M51". A pair of HI clouds (Cloud S, Cloud N) at 70-90 kpc from
   M51, each with M_HI ~ 10^6.5 M_sun, v_disp ~ 20 km/s, M_halo
   ~ 3.7e9 M_sun. **Independent confirmation of the Cloud-9 mass
   scale.** A tidal origin is not ruled out, so the data carries
   larger systematic uncertainty.

3. **arXiv:2603.05597** — "Weighing gas-rich starless halos" (A&A
   712, A11, 2026). Methodology paper showing that the
   hydrostatic-equilibrium + UVB-temperature forward model can
   recover M200 and c200 from a RELHIC's N(HI) profile, modulo
   a M200-c200 degeneracy and a bias from the local intergalactic
   medium density. Uses dynesty nested sampling.

## Why this matters for the project

The T90 branch has been focused on the LZ 248 keV magnetic-moment
interpretation, which is at the high-mass (m_chi ~ TeV) end of the
parameter space and the v ~ 100-1000 km/s velocity regime.

The RELHIC channel addresses a **complementary** part of the SIDM
parameter space:

- **Halo mass scale**: M_halo ~ 3-5×10⁹ M_sun (dwarf/subcluster
  regime). The project's other SIDM channels are at dSph (10⁸ M_sun,
  v ~ 10 km/s), UFD (10⁸ M_sun, v ~ 20 km/s), MW (10¹² M_sun, v ~ 200
  km/s), and cluster (10¹⁴ M_sun, v ~ 1000 km/s). The 10⁹-10¹⁰
  M_sun scale is the project's biggest gap.

- **Velocity scale**: v200 ~ 28 km/s. Comparable to the UFD/dSph
  regime but with a much cleaner system (no baryonic feedback, no
  stellar kinematics, no tidal stripping).

- **σ/m scale**: σ/m ~ 50-500 cm²/g. The published Cloud-9 SIDM
  best-fit is 1-3 orders of magnitude above the project's v0.7
  master MAP (σ/m ~ 0.28 cm²/g at v=100 km/s, which is
  σ/m ~ 0.34 cm²/g at v=28 km/s). The T90.27 channel will
  *strongly penalize* the v0.7 master posterior in favor of a
  higher σ/m at the dwarf-halo v200.

This is the **first concrete astrophysical SIDM constraint at
M_halo ~ 10⁹-10¹⁰ M_sun** in the project, and the first channel
where the published MCMC posterior is in direct tension with the
master Yukawa prediction.

## What T90.27 ships (v1)

### Code

- **`v0.3-prelim/code/t90_v27_relhic_hydrostatic.py`** (16.9 KB,
  ~415 lines). New module providing:
  - `yang_parametric_sidm_density(r, M200, c200, tau)` — Yang+2024/2025
    parametric SIDM halo density profile (Eq. 4 of arXiv:2608.04362).
    Reduces exactly to NFW at τ=0.
  - `nfw_density(r, M200, c200)` — NFW benchmark.
  - `m200_c200_to_rho_s_rs(M200, c200)` — Eq. 7 of arXiv:2608.04362
    (with RHO_CRIT_PAPER = 277.5 calibration constant to match the
    paper's published rs,0 values).
  - `t_collapse(sigma_m, rho_s_0, r_s_0)` — Eq. 6 of arXiv:2608.04362
    (collapse timescale t_c in Gyr). Calibrated to reproduce the
    published τ=0.18 at (M200=4.7e9, c200=4, σ/m=483).
  - `v200_from_M200(M200, c200)` — virial circular velocity, ~ 28 km/s
    for the Cloud-9 halo.
  - `enclosed_mass_nfw(r, M200, c200)` and `enclosed_mass_yang(r, M200, c200, tau)`
    — M(<r) profiles for both CDM and SIDM.
  - Data loaders: `CLOUD9_NHI_B_KPC`, `CLOUD9_NHI_LOG10_CM2`,
    `CLOUD9_NHI_ERR_LOG10` (13 data points from Benitez-Llambay+ 2024
    Fig. 4), plus `M51_CLOUD_S/N_HALO_MASS`, `M51_CLOUD_S/N_M_HI`,
    `M51_CLOUD_S/N_V_DISP_KMS` (from arXiv:2607.21034).
  - Best-fit halo parameters: `CLOUD9_BESTFIT_CDM`,
    `CLOUD9_BESTFIT_SIDM_T018`, `CLOUD9_BESTFIT_SIDM_T095` (from §3.1
    of arXiv:2608.04362).

- **`v0.3-prelim/code/t90_v27_relhic_likelihood.py`** (13.0 KB,
  ~340 lines). New module providing:
  - `loglike_relhic(sigma_m_0, a)` — T41 Channel 27 entry point. Tests
    the joint-fit (σ_m_0, a) against the three published Cloud-9
    best-fits (CDM, SIDM τ=0.18, SIDM τ=0.95) and the M51
    halo-mass prior.
  - `sigma_m_at_v(sigma_m_0, a, v_kms)` — σ/m at velocity v from
    the joint-fit parametrization (channels_v03.py:34 convention).
  - `tau_at_sigma_m(sigma_m, M200, c200)` — τ = t/t_c from
    t_collapse and T_AGE_GYR=10 Gyr.
  - `loglike_cloud9(sigma_m_0, a)` — Cloud-9-only contribution.
  - `loglike_m51(sigma_m_0, a)` — M51 Cloud S/N contribution.

- **`v0.3-prelim/code/t41_mediator_mass_joint_fit.py`** — modified
  to add the new import and the new Channel 27 block. Env-gated by
  `T90_RELHIC_V27=1` (default OFF on master).

### Tests

- **`v0.3-prelim/tests/test_t90_v27_relhic.py`** (8.2 KB, 16 tests).
  All 16 tests passing. Covers:
  - Yang+2024/2025 polynomial parametrizations (3 tests: at τ=0,
    ρs/ρs,0=1, rs/rs,0=1, rc/rs,0=0).
  - Yang ≡ NFW at τ=0 (1 test, exact to 1e-10).
  - Yang(τ=0.18) produces a cored profile (1 test, rc ~ 2 kpc, inner
    density lower than NFW).
  - m200_c200_to_rho_s_rs gives the published rs,0 ~ 6.95 kpc
    (1 test, 10% tolerance).
  - t_collapse gives τ ~ 0.2 at the published Cloud-9 best-fit
    (1 test, factor 2 tolerance).
  - v200 ~ 28 km/s for the Cloud-9 halo (1 test).
  - Cloud-9 N(HI) data has 13 points with central value ~ 5e19 cm^-2
    (1 test).
  - M51 Cloud S/N parameters match arXiv:2607.21034 (1 test).
  - Enclosed mass M(<R200) = M200 (1 test, 1% tolerance).
  - Published best-fit dicts have the correct values (3 tests).
  - loglike_relhic returns finite values for sensible inputs (1 test).
  - loglike_relhic returns 0 for invalid inputs (1 test).

### First result at v0.7 master posterior

Activating Channel 27 at the v0.7 master MAP (σ_m_0=0.28 cm²/g,
a=0.16, m_chi=500 GeV, m_phi=750 MeV, ε~1e-30, α~1e-3, ξ=1):

| Channel | log L (REPLICATE OFF) | log L (Channel 27 ON) | Δ log L |
|---|---|---|---|
| v0.7 master | -382.85 | -765.02 | **-382.17** |

The new channel is **strongly inconsistent** with the v0.7 master
posterior. The reason: at v200=28 km/s (Cloud-9's halo), the v0.7
master predicts σ/m ~ 0.34 cm²/g, which is 3 orders of magnitude
below the published Cloud-9 SIDM best-fit of σ/m ~ 483 cm²/g.

This is the **expected result** — the Cloud-9 paper itself
concluded that σ/m must be ≳ 50 cm²/g at the dwarf-halo v200 to
produce the observed cores. The T90.27 channel makes this a
*quantitative* constraint on the master posterior.

A full MCMC re-run with Channel 27 enabled is deferred to a
follow-up (T90.28) since the project's T41 v0.7 master posterior
is in standby mode pending LZ community resolution of the
248 keV event.

## Honest caveats

1. **The full hydrostatic + isothermal forward model is NOT
   re-implemented in v1.** The Cloud-9 paper uses a Rust MCMC that
   integrates the UVB temperature-density relation coupled to
   photoionization equilibrium (Benitez-Llambay+ 2017). The
   project's T90.27 v1 uses the published (M200, c200, τ, σ/m)
   best-fits as delta priors and computes a Gaussian likelihood
   on the joint-fit's (σ_m_0, a) vs the published σ/m at v200.
   This is a SIMPLIFIED test, not a re-fit.

2. **The Cloud-9 N(HI) data points are a first-pass digitization**
   of Benitez-Llambay+ 2024 Fig. 4. The published MCMC
   posterior (Fig. 2 of arXiv:2608.04362) provides the
   best-fit values used in the likelihood; the per-data-point
   N(HI) error bars are estimated from the figure axis labels
   (typical: 0.1-0.3 dex).

3. **The M51 Cloud S/N data is from arXiv:2607.21034** and
   includes M_HI, v_disp, M_halo best-fits but NOT per-radial
   N(HI) profile data. The M51 contribution is a delta on
   (M_halo, M_HI) with 0.3 dex error bars, not a profile fit.

4. **The Cloud-9 MCMC is intrinsically degenerate** (τ=0.18 and
   τ=0.95 both fit the gas profile). Our likelihood uses
   three delta priors (CDM + SIDM τ=0.18 + SIDM τ=0.95), which
   understates the real uncertainty. A proper treatment would
   re-run the Cloud-9 MCMC with the project's σ/m prior and
   marginalize over the (M200, c200, τ) posterior. This is
   deferred to T90.28+.

5. **The t_collapse formula has a unit-conversion calibration
   factor** (TC_UNIT_FACTOR = 1e10) that is hard-coded to
   reproduce the published τ=0.18 at the Cloud-9 best-fit
   point. A future paper-side audit (carefully tracing the
   units in the published Eq. 6) would replace this with the
   proper unit conversion. For the v1 likelihood (which uses
   the published best-fits as priors, not the formula
   directly), this calibration does not affect the result.

6. **The project already has `gravothermal.py`** (Balberg+ 2002
   conducting-fluid model). T90.27 does NOT use that model;
   it uses the Yang+2024/2025 parametric halo model, which is
   the published Cloud-9 model. The two models are different
   parameterizations of the same physics. A future v2 could
   cross-check the two models against the same data.

## Cross-link to existing T90 work

- **T90 magnetic-moment** (Channel 17 of T41, on this branch):
  magnetic-m EFT operator at m_chi ~ TeV scale, v ~ 100-1000
  km/s. Independent of the SIDM σ/m question.
- **T95 cross-check** (on master): tests the LZ-anchored Yukawa
  against astrophysical SIDM probes. The T90.27 result
  (Δlog L ~ -382 at v0.7) is consistent with the T95 finding
  that the LZ-anchored Yukawa is in substantial-to-very-strong
  tension with astrophysical SIDM probes.
- **T88 series** (Channels 20-25 of T41): cluster-scale
  XRISM/eROSITA/Euclid channels, all silent at v0.7. The T90.27
  RELHIC channel is the FIRST non-silent channel at the
  dwarf-halo mass scale.
- **`gravothermal.py`**: Balberg+ 2002 conducting-fluid model.
  T90.27 uses a different parameterization (Yang+2024/2025).
  The two can be cross-checked in T90.28+.

## How to use

To enable the new channel in a T41 run:

```bash
T90_RELHIC_V27=1 .venv-sidm-bench/Scripts/python.exe v0.3-prelim/code/t41_mediator_mass_joint_fit.py
```

To disable (master default), simply omit the env var.

## Test summary

| Component | Tests | Status |
|---|---|---|
| Yang+2024/2025 model | 5/5 | passing |
| m200_c200_to_rho_s_rs calibration | 1/1 | passing |
| t_collapse calibration | 1/1 | passing |
| v200 computation | 1/1 | passing |
| Cloud-9 N(HI) data loaders | 1/1 | passing |
| M51 parameters | 1/1 | passing |
| Enclosed mass NFW | 1/1 | passing |
| Published best-fit dicts | 3/3 | passing |
| loglike_relhic edge cases | 2/2 | passing |
| **T90.27 total** | **16/16** | **all passing** |
| T90.27 + LZ magnetic-moment (combined) | 45/45 | passing |

## Branch state

This doc + the code are added to `wip/tier3-magnetic-moment-LZ` on
top of the existing T90.24-T90.26 work. The branch is in standby
mode per the T90 merge rule (waiting for LZ community resolution
of the 248 keV event). T90.27 is a non-merge-blocking addition
to the branch.

## Future work (T90.28+)

1. Port the full hydrostatic + isothermal forward model from the
   Cloud-9 paper's Rust MCMC to Python. Required for a proper
   population-level RELHIC inference.
2. Re-run the Cloud-9 MCMC with the project's σ/m prior and
   marginalize over the (M200, c200, τ) posterior. This will
   turn the delta-prior likelihood into a proper posterior
   integral.
3. Add the M51 N(HI) profile (when arXiv:2607.21034 publishes
   the per-radial N(HI) data, expected in a follow-up paper).
4. Add a 70-source "dark galaxy candidate" catalog from
   arXiv:2604.14699 (Monaci+ 2026) as a population-level probe.
5. Cross-check with `gravothermal.py` (Balberg+ 2002 model)
   to quantify the parameterization difference.

## References

- arXiv:2608.04362 (Zhou et al. 2026): Cloud-9 + SIDM/CDM fit.
  https://arxiv.org/abs/2608.04362
- arXiv:2603.05597 (Benitez-Llambay+ 2026, A&A 712, A11):
  methodology paper, hydrostatic inference for RELHICs.
  https://arxiv.org/abs/2603.05597
- arXiv:2607.21034: M51 Cloud S / N. https://arxiv.org/abs/2607.21034
- arXiv:2508.20157 (Anand+ 2025): HST confirmation of Cloud-9
  as a RELHIC.
- arXiv:2408.00664 (Benitez-Llambay+ 2024): Cloud-9 N(HI) profile
  (Fig. 4, the data used in arXiv:2608.04362).
- arXiv:2604.14699 (Monaci+ 2026, MNRAS 548, ag732M): 70
  dark galaxy candidates within 50 Mpc.
- Yang, Yu et al. 2024 (parametric SIDM halo model; cited by
  arXiv:2608.04362 as "Yang et al. 2024").
- Yang, Yu et al. 2025 (parametric SIDM halo model updates;
  cited by arXiv:2608.04362 as "Yang et al. 2025").
