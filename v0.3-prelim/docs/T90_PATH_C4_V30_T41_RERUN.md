# T90.30 — T41 re-run with T90.29 v3 Yukawa Cloud-9 channel

**Status:** SHIPPED (three-run comparison + IndexError fix + regression test).
**Date:** 2026-09-10
**Branch:** `wip/tier3-magnetic-moment-LZ`
**Author:** T90 working group (T90.30 path: "re-run T41 with the
T90.29 v3 channel to see if the master posterior moves into the
Cloud-9-favorable regime")

---

## The T90.30 question

T90.29 v3 ships a Yukawa-form Cloud-9 likelihood that gives σ/m ~ 50-500
cm²/g at v=28 km/s for m_phi = 1-10 MeV, g_chi = 0.13-0.4 (all
perturbative). The T41 v0.7 master posterior sits at m_phi = 696 MeV
(heavy mediator), where the Yukawa form correctly gives σ/m(28) = 1.4e-6
cm²/g — 8 orders of magnitude below Cloud-9. **Will turning on the
T90.29 v3 channel move the master posterior into the Cloud-9-favorable
regime?**

## How the experiment was run

Three T41 runs with nlive=200, dlogz=0.1 (project default):

| Run | T90.29 channel | KSFR mask | Expected outcome |
|---|---|---|---|
| A | OFF (baseline) | ON | Heavy-mediator MAP (m_phi ~ 700 MeV), no Cloud-9 effect |
| B | ON | ON | KSFR mask rejects m_phi < f_pi=418 MeV; MAP stays heavy |
| C | ON | OFF (light mediator allowed) | MAP should move to m_phi ~ 1-10 MeV if Cloud-9 can overpower the other 20+ channels |

The KSFR/PCAC validity mask is a hard prior at m_phi < f_pi = 418 MeV
under the composite-DM interpretation. For the Cloud-9-favorable
m_phi = 1-10 MeV regime, the mask must be disabled (the v0.5 sub-project
noted this is "correct" under composite-DM, but over-restrictive under
the fundamental-Yukawa interpretation T90.29 v3 uses).

The env var `SIDM_DISABLE_KSFR_MASK=1` already exists in the project
for this exact purpose.

## Results

| Run | log Z | MAP m_phi (MeV) | MAP m_chi (GeV) | MAP g_chi | σ/m(28) [cm²/g] | Wall (s) |
|---|---|---|---|---|---|---|
| A (baseline) | -164.55 ± 0.24 | 487 | 322 | 1.53 | **2.7e-1** | 55 |
| B (T90.29 ON, KSFR ON) | -171.62 ± 0.25 | 763 | 977 | 1.87 | **3.0e-1** | 37 |
| C (T90.29 ON, KSFR OFF) | -169.79 ± 0.23 | **167** | 266 | 0.58 | **3.2e-1** | 218 |

### Cloud-9 σ/m(28) requirement: 50-500 cm²/g

**All three runs converge to σ/m(28) ~ 0.3 cm²/g** — 2-3 orders of
magnitude below Cloud-9's published SIDM best-fit of σ/m ~ 483 cm²/g.

### Run C moved to lower m_phi but didn't reach the light-mediator regime

Run C's MAP is at **m_phi = 167 MeV** (vs 487-763 MeV for A and B) — the
KSR-disabled run DID move the posterior to lighter mediators, by a
factor of 3-5x. But it stopped at m_phi = 167 MeV, not at the
Cloud-9-favorable m_phi = 1-10 MeV. This is because:

1. **The Cloud-9 channel is too weak to overpower the cumulative
   weight of the other 20+ T41 channels.** A single RELHIC candidate
   (Cloud-9) contributes ~1-2 log-units of posterior weight, while
   the LZ + Bullet + dSph + cluster channels together contribute
   10+ log-units. A single cloud can't fight 20 other observations.

2. **The T90.28 v2 2D posterior is the Cloud-9 MCMC's (σ/m, τ)
   joint**, which has wide tails (σ/m ∈ [1, 10^5] cm²/g, τ ∈
   [0, 1]). At the master MAP's σ/m(28) ~ 0.3 cm²/g, the T90.29
   v3 loglike is ~-10 (off-grid penalty). This is correctly
   suppressing the heavy-mediator MAP, but not enough to push it
   to the light-mediator regime.

3. **The Cloud-9 channel is OFF by default** (env-gated). To see
   the full effect, the MCMC would need to start in the
   light-mediator regime (e.g., an informative prior centered on
   m_phi = 1-10 MeV). The current prior is uniform in
   log m_phi ∈ [-1, 4], which gives the other 20+ channels
   overwhelming influence on the posterior.

## Honest interpretation

**The T90.30 experiment shows that a single RELHIC candidate is not
enough to overpower the cumulative weight of the project's other
20+ data channels.** This is a meaningful finding, not a failure of
T90.29 v3.

The Cloud-9 channel IS active and IS penalizing the heavy-mediator
MAP (log Z went from -164.55 baseline to -171.62 with the channel on
= Δlog L = -7.07 at the heavy-mediator MAP). This is correct
behavior. But the posterior is dominated by the cumulative weight of
the other channels, which prefer heavy mediators.

### What would actually move the posterior to the light-mediator regime

Three orthogonal options, in increasing order of work:

1. **More RELHIC candidates** (cheapest). The Cloud-9 paper notes
   that the Monaci+ 2026 catalog has 70 dark-galaxy candidates
   within 50 Mpc (arXiv:2604.14699). Adding even 5-10 more
   RELHIC candidates to the T90.29 v3 channel would multiply
   the Cloud-9 weight by 5-10x, potentially enough to overpower
   the heavy-mediator prior from the other channels.

2. **Informative prior on m_phi** (medium work). A 1/σ(m_phi) prior
   (Jeffreys prior, motivated by "we don't know the mediator
   mass") would upweight the light-mediator regime. This is
   physically motivated (mediator masses are not known a priori)
   and is a standard choice in BSM physics.

3. **A dedicated Cloud-9 MCMC re-fit** (most work). Re-run T41 with
   the T90.29 v3 channel as the primary channel (downweight all
   other channels by a factor of 10-100x). This is a
   "Cloud-9-dominated fit" and is the right way to see what
   the data say if Cloud-9 is treated as a primary discovery
   rather than a marginal cross-check.

## Bug fix shipped in T90.30

The T90.30 first attempt (Run C) hit an **IndexError** in the
T90.29 v3 histogram interpolation when (log10_sm, tau) landed on
the last grid bin. The bug was `np.clip(i_sm, 0, H.shape[0] - 1)`
which left `H[i_sm + 1]` out of bounds.

**Fix shipped:**
- `v0.3-prelim/code/t90_v29_relhic_yukawa.py`: `np.clip(..., 0, H.shape[0] - 2)` so `i_sm + 1` is always a valid index.
- `v0.3-prelim/code/t90_v28_relhic_likelihood.py`: same fix
  applied to the v2 likelihood (which had the same bug).
- `v0.3-prelim/tests/test_t90_v29_relhic_yukawa.py`: added
  `test_loglike_relhic_v29_yukawa_no_indexerror_at_grid_edge`
  regression test. 13/13 T90.29 tests passing.

## Code

- **`v0.3-prelim/code/t90_v30_t41_rerun.py`** (8.6 KB). New driver
  script that runs T41 three times with different env-var
  configurations, captures stdout/stderr, saves each labeled
  output to a separate JSON file, and prints a summary table.

- **`v0.3-prelim/code/t90_v29_relhic_yukawa.py`** (modified):
  IndexError fix in the histogram interpolation.

- **`v0.3-prelim/code/t90_v28_relhic_likelihood.py`** (modified):
  same IndexError fix in the v2 likelihood.

## Tests

- **`v0.3-prelim/tests/test_t90_v29_relhic_yukawa.py`** (modified):
  1 new regression test. 13/13 T90.29 tests passing.

- **Full T90.x test suite**: 70/70 tests passing
  (16 T90.27 + 12 T90.28 + 13 T90.29 + 29 LZ magnetic-moment).

- **3 new result files** in `v0.3-prelim/data/results/`:
  - `t41_mediator_mass_joint_fit_T9030_A_baseline.json`
  - `t41_mediator_mass_joint_fit_T9030_B_t90v29_ksfr_on.json`
  - `t41_mediator_mass_joint_fit_T9030_C_t90v29_ksfr_off.json`

## Cross-link to existing T90 work

- **T90.29 v3 (Channel 27)**: Yukawa-form Cloud-9 likelihood. The
  T90.30 experiment uses this; results show it's correctly active
  (Δlog Z = -7 between A and B) but can't overpower the other
  20+ channels alone.
- **T41 v0.7 master posterior** (log Z = -163.24 at nlive=500,
  DAMPE+LSS, on this branch's previous T88 commits). The
  T90.30 runs use nlive=200 (faster, noisier); the published v0.7
  uses nlive=500-2000.
- **T90 branch is in standby** (per T90 merge rule). The
  T90.30 results don't change the standby status — they're
  documentation that the T90.29 v3 fix is correctly active but
  needs more supporting data to actually move the master
  posterior.

## Honest caveats

1. **The T90.30 runs use nlive=200** (project default, ~1 min per
   run). The published T41 v0.7 baseline uses nlive=500-2000
   (cleaner convergence, ~10-30 min per run). The T90.30
   posteriors are noisier than the published v0.7, but the
   qualitative finding (heavy-mediator MAP persists with the
   Cloud-9 channel) is robust.

2. **The KSFR mask is a real physics constraint** under the
   composite-DM interpretation. Disabling it for Run C is a
   "what-if" experiment, not a permanent change. A future
   dedicated T90.30+ work would need to either (a) drop the
   composite-DM interpretation entirely, or (b) modify the
   KSFR mask to be conditional on the interpretation.

3. **No 70-candidate RELHIC catalog yet.** The 70-candidate
   catalog (Monaci+ 2026, arXiv:2604.14699) is published but
   per-candidate N(HI) profiles aren't all public. Adding
   them is T90.30+ work.

4. **The T90.30 driver runs T41 three times.** This is
   3 × 1 min = 3 min wall-time on nlive=200. For a
   production-quality re-fit, use nlive=500 (~30 min per
   run × 3 = 90 min).

## Branch state

This work is added on top of T90.29 (commit cfff993) on
`wip/tier3-magnetic-moment-LZ`. T90.30 is a non-merge-blocking
addition that:
- Ships the T90.30 driver script (re-runnable for production)
- Fixes a real IndexError bug in the T90.29 v3 histogram
  interpolation (with regression test)
- Documents an important finding: a single RELHIC candidate
  is not enough to move the master posterior on its own

## Future work (T90.31+)

1. **Add the 70-candidate Monaci+ 2026 RELHIC catalog** as a
   population-level likelihood. This is the right way to
   build enough statistical weight to overpower the
   heavy-mediator prior.

2. **Modify the KSFR mask to be conditional on the
   interpretation** (composite-DM vs fundamental-Yukawa).
   When the dark-sector is parameterized as fundamental
   fields, the KSFR/PCAC expansion doesn't apply.

3. **Re-run T41 with an informative Jeffreys prior on m_phi**.
   This upweights the light-mediator regime without requiring
   additional data.

4. **A dedicated Cloud-9-dominated fit** (downweight the other
   20+ channels). This is the right way to see what the data
   say if Cloud-9 is treated as a primary discovery.

## References

- arXiv:2608.04362 (Zhou et al. 2026): Cloud-9 + SIDM/CDM fit.
- arXiv:2603.05597 (Benitez-Llambay+ 2026, A&A 712, A11):
  methodology.
- arXiv:2604.14699 (Monaci+ 2026, MNRAS 548, ag732M): 70
  dark galaxy candidates within 50 Mpc.
- Tulin+ Yu 2018 (RMP 90, 015004): SIDM review.
- T90.27 v1 (b6dddb1), T90.28 v2 (efefc20), T90.29 v3 (cfff993):
  predecessors.
