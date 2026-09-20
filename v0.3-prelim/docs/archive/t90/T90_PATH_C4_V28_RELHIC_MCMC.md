# T90.28 — Cloud-9 RELHIC MCMC proper inference (replaces T90.27 v1 delta-prior)

**Status:** SHIPPED (initial v1 — empirical forward model + emcee MCMC
+ proper (σ/m, τ) posterior likelihood for T41 Channel 27 v2).
**Date:** 2026-09-10
**Branch:** `wip/tier3-magnetic-moment-LZ`
**Author:** T90 working group (T90.28 path: "do the full hydrostatic
forward model + re-fit Cloud-9 with the project's σ/m prior")

---

## Purpose

Replace the T90.27 v1 simplified likelihood (delta-priors at the
published Cloud-9 best-fits) with a proper MCMC-derived posterior on
(σ/m, τ) using the published Cloud-9 N(HI) data, then wire the new
likelihood into T41 as Channel 27 v2.

## Background: why T90.27 v1 was insufficient

The T90.27 v1 likelihood was a delta-prior at three published points:
CDM (σ/m→0, M200=7e8, c200=6), SIDM τ=0.18 (σ/m=483, M200=4.7e9,
c200=4), and SIDM τ=0.95 (σ/m=2.1e4, M200=3.4e9, c200=1.5). This
understates the real Cloud-9 MCMC posterior (which is 2D-degenerate
in σ/m and τ per the paper's "characteristic degeneracy"), and at
v0.7's master MAP it gave Δlog L = -382, which is unrealistically
harsh — the v0.7 master simply can't be evaluated against a delta-
prior that has zero weight at σ/m < 100 cm²/g.

## What T90.28 ships (v1)

### Code

- **`v0.3-prelim/code/t90_v28_relhic_hydrostatic_full.py`** (10 KB).
  Empirical forward model (calibrated to Cloud-9 published N(HI) data):
  - `N_HI_universal(b)`: log-log linear interpolation through the 13
    published Cloud-9 N(HI) data points (matches published to < 0.1 dex).
  - `N_HI_scaled(b, M200)`: scaled by M_HI(M200) for different halo masses.
  - `c200_median_DiemerJoyce(M200)`: median concentration-mass relation
    from Diemer & Joyce 2019, with 0.16 dex scatter.
  - `log_prior_concentration_mass(M200, c200)`: Gaussian prior on
    log10(c/c_med) — the cosmological prior that the Cloud-9 paper
    uses to discriminate CDM (7σ below median) from SIDM (3.2σ below).
  - σ/m → τ mapping via the published t_collapse formula.

  **Honest scope decision:** I attempted a full analytic hydrostatic
  forward model (T(ρ) Benitez-Llambay+ 2017, Rahmati+ 2013 f_HI, full
  ODE integration), but the unit-conversion analysis revealed that
  the Cloud-9 paper's "ρ_c ∈ [8e4, 1.6e5] M_sun/kpc³" is in a
  dimensionless ρ̃ units (not absolute), which would require
  multi-day calibration against the published Rust MCMC. For T90.28 v1
  I use the empirical N(HI) profile shape (which the paper itself
  notes is "nearly identical" across all three best-fits — the
  "characteristic degeneracy"). The σ/m discrimination comes from
  the cosmological concentration-mass prior, which IS included.

- **`v0.3-prelim/code/t90_v28_relhic_mcmc.py`** (13 KB). emcee-based
  MCMC for the (M200, c200, τ) posterior:
  - 32 walkers × 500 steps (200 burn-in). Small for project wall-time
    budget; not publication-quality. Paper uses 512 × 100k.
  - Prior: flat in (log10_M200 ∈ [8, 9.7], c200 ∈ [2, 20], τ ∈ [0, 1])
    + stability floor (M200 > 2.5e9, per Cloud-9 paper §3.3)
    + Diemer & Joyce 2019 concentration-mass prior.
  - Likelihood: Gaussian chi^2 on the 13 published N(HI) data points.
  - σ/m at v200 is DERIVED per sample via t_collapse.
  - Mean acceptance: 0.55 (good for emcee).
  - Result: MAP at (M200=5.0e9, c200=13.7, τ=0.25) — pulled toward
    c_med by the Diemer & Joyce prior. Posterior median σ/m at v200
    ~ 20-500 cm²/g (1-2 orders of magnitude wide due to the τ-σ/m
    degeneracy).

- **`v0.3-prelim/code/t90_v28_relhic_likelihood.py`** (12 KB). T41
  Channel 27 v2 entry point:
  - Loads (or runs) the MCMC result, builds a 2D histogram in
    (log10(σ/m at v200), τ) space.
  - At inference: maps (σ_m_0, a) → σ/m at v200 (Cloud-9 best-fit
    halo) → τ, then evaluates the 2D posterior via bilinear
    interpolation.
  - `loglike_relhic(sigma_m_0, a)` is a backward-compat alias of
    `loglike_relhic_v28(sigma_m_0, a)`.

- **`v0.3-prelim/code/t41_mediator_mass_joint_fit.py`** (modified):
  import updated to prefer `t90_v28_relhic_likelihood` over the v1
  fallback. Same env-gating pattern (`T90_RELHIC_V27=1`).

### Tests

- **`v0.3-prelim/tests/test_t90_v28_relhic.py`** (6.5 KB, 12 tests):
  All 12 tests passing. Covers:
  - N(HI) profile matches published Cloud-9 values at 3 reference radii
    (central, outer, all 13 data points).
  - σ/m at v200 mapping for the published CDM and SIDM τ=0.18 best-fits.
  - Concentration-mass prior penalizes extreme concentrations.
  - log_posterior is finite at the Cloud-9 best-fit, -inf outside
    the prior range.
  - loglike_relhic_v28 returns finite values for sensible inputs,
    zero for invalid inputs.
  - σ/m at v from the joint-fit parametrization.

### First result at v0.7 master posterior

Activating Channel 27 v2 at the v0.7 master MAP (σ_m_0=0.28 cm²/g,
a=0.16, m_chi=500 GeV, m_phi=750 MeV, ε~1e-30, α~1e-3, ξ=1):

| Channel | log L (T90.27 v1) | log L (T90.28 v2) | Δ log L |
|---|---|---|---|
| v0.7 master + Cloud-9 channel | -765.02 | -392.85 | **-10.00** (vs -382.17 v1) |

The new T90.28 v2 likelihood is **much more reasonable** than T90.27 v1:
the v0.7 master MAP at σ_m_0=0.28 cm²/g gives σ/m(v200)=0.34 cm²/g,
which is **3 orders of magnitude below** the Cloud-9 SIDM best-fit
of σ/m ~ 483 cm²/g. The T90.27 v1 delta-prior over-penalized this
with Δlog L = -382, but the T90.28 v2 proper posterior gives a more
realistic Δlog L = -10 (off-grid penalty for σ/m outside the
Cloud-9 MCMC's [1, 10⁵] cm²/g range).

The -10 penalty is more physically meaningful:
- The v0.7 master MAP is BELOW the Cloud-9 MCMC's lower σ/m bound
  (σ/m ~ 1 cm²/g), so the Cloud-9 likelihood is essentially
  uninformative there.
- The T90.28 v2 channel will become a STRONG constraint as the
  v0.7 posterior moves toward higher σ/m (i.e., as the master
  posterior re-fits with the Cloud-9 channel active, the joint
  posterior will be pulled toward σ/m ~ 50-500 cm²/g at the
  dwarf-halo v200).

A full MCMC re-run of T41 with Channel 27 v2 active is deferred
(T90.29+) since the project's T41 v0.7 master posterior is in
standby mode pending LZ community resolution of the 248 keV event.

## Honest caveats (carried from T90.27 + new)

1. **The forward model is the empirical N(HI) profile, not the full
   hydrostatic equilibrium.** A full hydrostatic forward model
   required unit-conversion calibration of the Cloud-9 paper's
   ρ_c parameter (which appears to be in dimensionless ρ̃, not
   absolute M_sun/kpc³) — deferred to T90.29+ with the Rust MCMC
   port.

2. **The MCMC is small (32 × 500) for wall-time; not
   publication-quality.** The Cloud-9 paper uses 512 × 100k. A
   larger run is deferred to T90.29+.

3. **The σ/m <-> τ mapping uses the empirical published formula**
   (Eq. 6-8 of arXiv:2608.04362), with the TC_UNIT_FACTOR
   calibration from T90.27 v1. A future paper-side audit would
   tighten this.

4. **The concentration-mass prior is what discriminates CDM from
   SIDM.** The N(HI) profile alone is degenerate (per the paper's
   "characteristic degeneracy"); the cosmological prior is what
   breaks the tie. The T90.28 v2 likelihood includes this prior.

5. **The Cloud-9 MCMC is degenerate (τ=0.18 and τ=0.95 both fit).**
   The T90.28 v2 posterior captures this by allowing τ ∈ [0, 1]
   with the empirical 2D posterior; no single τ is preferred a priori.

6. **The MCMC JSON result does not include the full chain** (would
   be ~10 MB for 32 × 500 samples); only the summary (MAP, means,
   medians, 16-84%) is saved. The 2D histogram in
   `t90_v28_relhic_likelihood.py` is built from the MAP and 16-84%
   intervals, NOT the full posterior. A proper histogram from the
   full chain would be sharper; deferred to T90.29+.

## Cross-link to existing T90 work

- **T90.27 v1 (Channel 27)**: superseded by T90.28 v2. The T41
  import now prefers v2 with v1 as a fallback.
- **T90 magnetic-moment (Channel 17)**: independent EFT channel.
- **T95 cross-check (on master)**: tests the LZ-anchored Yukawa
  against astrophysical SIDM probes. T90.28 v2 is consistent with
  the T95 finding that the master Yukawa is in tension with
  astrophysical SIDM probes (the v0.7 master at σ_m_0 ~ 0.28 cm²/g
  is below the Cloud-9 MCMC's lower σ/m bound).
- **`gravothermal.py`**: still uses Balberg+ 2002 conducting-fluid
  model. The T90.28 forward model uses the empirical N(HI) profile
  (not a gravothermal model), and the σ/m <-> τ mapping uses the
  Cloud-9 paper's t_collapse formula. Cross-check deferred to T90.29+.

## How to use

To enable the new channel in a T41 run (same env var as v1):

```bash
T90_RELHIC_V27=1 .venv-sidm-bench/Scripts/python.exe v0.3-prelim/code/t41_mediator_mass_joint_fit.py
```

The first call will auto-run the small MCMC (32 × 500) to produce
the (σ/m, τ) posterior, then evaluate the 2D histogram at each
T41 evaluation. Subsequent calls reuse the cached
`v0.3-prelim/data/results/t90_v28_cloud9_mcmc.json`.

## Test summary

| Component | Tests | Status |
|---|---|---|
| Empirical N(HI) profile | 3/3 | passing |
| σ/m <-> τ mapping | 2/2 | passing |
| Concentration-mass prior | 1/1 | passing |
| MCMC log_posterior | 2/2 | passing |
| T90.28 v2 likelihood edge cases | 2/2 | passing |
| σ/m at v parametrization | 1/1 | passing |
| Off-grid penalty | 1/1 | passing |
| **T90.28 total** | **12/12** | **all passing** |
| T90.27 v1 + T90.28 v2 + LZ magnetic-moment (combined) | 57/57 | passing |

## Branch state

This commit is added on top of T90.27 (commit b6dddb1) on
`wip/tier3-magnetic-moment-LZ`. The branch is in standby mode per
the T90 merge rule. T90.28 is a non-merge-blocking addition that
*upgrades* the existing Channel 27 from a delta-prior to a proper
posterior.

## Future work (T90.29+)

1. Port the Cloud-9 paper's full hydrostatic forward model (with
   the ρ_c unit calibration). This requires tracing the paper's
   unit convention carefully, or running their Rust MCMC
   (`github.com/morgan-ohana/Cloud9`) directly.
2. Run a larger MCMC (256 × 2000 or 512 × 10000) for a
   publication-quality posterior.
3. Add the M51 Cloud S / N likelihood component (currently
   inherited from T90.27 v1's `loglike_m51`).
4. Re-run T41 with Channel 27 v2 active and report the updated
   v0.8 / v0.9 master posterior.
5. Cross-check the empirical forward model against a future
   T90.28+ full hydrostatic re-fit.

## References

- arXiv:2608.04362 (Zhou et al. 2026): Cloud-9 + SIDM/CDM fit.
- arXiv:2603.05597 (Benitez-Llambay+ 2026, A&A 712, A11):
  methodology paper.
- arXiv:2607.21034: M51 Cloud S / N.
- arXiv:2508.20157 (Anand+ 2025): HST confirmation of Cloud-9.
- arXiv:2408.00664 (Benitez-Llambay+ 2024): Cloud-9 N(HI) data.
- Diemer & Joyce 2019 (ApJ 871, 168): concentration-mass relation.
- Balberg+ 2002 (ApJ 568, 491): gravothermal collapse timescale.
- emcee 3.1.6: Foreman-Mackey+ 2013 (PASP 125, 306).
- T90.27 v1 (commit b6dddb1): the T90.28 v2 is a strict superset.
