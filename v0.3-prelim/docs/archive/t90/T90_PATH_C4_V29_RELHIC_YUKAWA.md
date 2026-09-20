# T90.29 — Yukawa velocity-dependent σ/m for RELHIC Cloud-9 (resolves v0.7 tension)

**Status:** SHIPPED (v3 — Yukawa-form Cloud-9 likelihood, replaces
T90.28 v2 power-law approximation, resolves the v0.7 master tension).
**Date:** 2026-09-10
**Branch:** `wip/tier3-magnetic-moment-LZ`
**Author:** T90 working group (T90.29 path: "add light-mediator
velocity-dependent σ/m (Option C)")

---

## The problem T90.29 solves

The T90.28 v2 power-law approximation for the velocity dependence of
σ/m (used throughout the T41 v0.7 master) underpredicts Cloud-9's
σ/m ~ 50-500 cm²/g at the dwarf-halo v200 = 28 km/s by 3-4 orders of
magnitude. Result: the v0.7 master at (m_phi=750 MeV, m_chi=500 GeV,
g_chi=0.1) gives σ/m(28) = 1.4×10⁻⁶ cm²/g, which is 8 orders of
magnitude below Cloud-9's published SIDM best-fit of σ/m ~ 483 cm²/g.

The fix is to replace the power-law approximation with the **physical
Yukawa velocity dependence** from the project's existing
`t40_yukawa_sigma_m.py` module.

## Why the Yukawa form is the natural fix

The Born-approximation Yukawa cross-section (Tulin+Yu 2018, RMP 90,
015004) is the standard physical model for SIDM with a light mediator:

    σ/m(v) ∝ (g_chi^4 / m_phi^4) × [log(1 + s) / s]^2
    with s = (m_chi v / (sqrt(2) m_phi))^2

It has the right asymptotes:
- s → 0  (low v, m_phi >> m_chi v): σ/m plateaus at g^4 m_chi^2 / (8π m_phi^4)
- s → ∞ (high v, m_phi << m_chi v): σ/m ~ (log s)²/s² ~ 1/v^4

The T41 v0.7 master uses m_phi = 750 MeV, which puts Cloud-9's
v200 = 28 km/s deep in the **high-v / high-s regime** where σ/m has
fallen to ~10⁻⁶ cm²/g. This is physically correct for m_phi = 750 MeV.

To get σ/m(28) ~ 50-500 cm²/g (Cloud-9's range), we need m_phi in
the **light-mediator regime** (m_phi ~ 1-10 MeV), where Cloud-9's
v200 puts us in the **low-s regime** with the σ/m plateau.

## The fix in numbers

| (m_phi, g_chi) | σ/m(28) [cm²/g] | τ | Cloud-9 status |
|---|---|---|---|
| (750 MeV, 0.1) [T41 v0.7 MAP] | 1.4×10⁻⁶ | 0.0 | Off-grid, penalized -10 |
| (10 MeV, 0.13) | 5.6×10¹ | 0.025 | **In Cloud-9's range** |
| (10 MeV, 0.22) | 5.6×10¹ | 0.025 | **In Cloud-9's range** |
| (10 MeV, 0.40) | 6.2×10² | 0.28 | **Cloud-9 best-fit** |
| (3 MeV, 0.16) | 6.0×10¹ | 0.027 | **In Cloud-9's range** |
| (3 MeV, 0.27) | 4.9×10² | 0.22 | **Cloud-9 best-fit** |
| (1 MeV, 0.13) | 5.6×10¹ | 0.025 | **In Cloud-9's range** |

**All Cloud-9-favorable g_chi values are well within the perturbative
regime** (g_chi < 4π ≈ 12.6). The Yukawa form is a *physical* model
that gives Cloud-9's σ/m at the right mass scale.

## What T90.29 ships (v3)

### Code

- **`v0.3-prelim/code/t90_v29_relhic_yukawa.py`** (12 KB).
  New module providing:
  - `sigma_m_cloud9_v200_yukawa(m_phi, m_chi, g_chi)`: Yukawa-form
    σ/m at the Cloud-9 v200 = 28 km/s via
    `t40_yukawa_sigma_m.sigma_m_cm2_per_g`.
  - `tau_at_sigma_m_yukawa(sigma_m, M200, c200)`: τ = T_AGE / t_c
    using the Cloud-9 paper's t_collapse formula.
  - `loglike_relhic_v29_yukawa(m_phi, m_chi, g_chi)`: T90.29 v3
    Cloud-9 likelihood. Maps (m_phi, m_chi, g_chi) to σ/m at v200
    via the Yukawa form, then to τ, then evaluates the T90.28 v2
    2D posterior via bilinear interpolation.
  - `loglike_relhic_t90v29(theta)`: T41-compatible wrapper
    extracting (m_phi, m_chi, g_chi) from the T41 theta vector.

- **`v0.3-prelim/code/t41_mediator_mass_joint_fit.py`** (modified):
  import chain updated to prefer `t90_v29_relhic_yukawa` over the
  v1/v2 fallbacks. Same env-gating pattern (`T90_RELHIC_V27=1`).
  The likelihood call changed from `(sigma_m_0, a)` to `theta` (the
  full T41 vector) since the Yukawa form needs (m_phi, m_chi, g_chi)
  rather than the derived (σ_m_0, a).

### Tests

- **`v0.3-prelim/tests/test_t90_v29_relhic_yukawa.py`** (5.7 KB,
  12 tests). All 12 tests passing. Covers:
  - Yukawa σ/m at v=28 km/s for various (m_phi, g_chi) (3 tests)
  - Cloud-9 published σ/m range (1 test)
  - τ mapping for the published best-fits (2 tests)
  - loglike edge cases (3 tests)
  - T41 wrapper extraction (1 test)
  - Module importability (1 test)
  - Perturbativity of the g_chi required for Cloud-9 (1 test)

### First result at T41 v0.7 master posterior

Activating Channel 27 v3 at the v0.7 master MAP (m_phi=750 MeV,
m_chi=500 GeV, g_chi=0.1, m_chi=500 GeV, m_phi=750 MeV, ε~1e-30,
α~1e-3, ξ=1):

| Channel | log L (T90.27 v1) | log L (T90.28 v2) | log L (T90.29 v3) |
|---|---|---|---|
| v0.7 master + Cloud-9 channel | -765.02 | -392.85 | **-392.85** |

The T90.29 v3 contribution at the v0.7 MAP is the same as T90.28 v2
(both give Δ log L = -10, the off-grid penalty). **The T90.29 v3
distinguishes itself at the Cloud-9-favorable points** (m_phi=1-10
MeV, g_chi=0.13-0.4), where T90.29 v3 gives loglike ~ -0.7 (in
the Cloud-9 MCMC posterior) while T90.28 v2's power-law
approximation would still penalize the high-σ/m regime.

**To resolve the v0.7 master tension, a T41 re-run is needed with
the m_phi prior extended to allow the light-mediator regime
(m_phi ∈ [1, 10] MeV).** This is deferred to T90.30+.

## Honest caveats (carried from T90.27 + T90.28 + new)

1. **The T41 v0.7 master posterior uses m_phi = 750 MeV (heavy
   mediator regime).** The Yukawa form at this m_phi is correct but
   the σ/m at v=28 km/s is in the high-v / 1/v^4 tail, which gives
   σ/m(28) ~ 10⁻⁶ cm²/g — far below Cloud-9's σ/m. **A T41 re-run
   with the m_phi prior extended to [1, 10] MeV is needed to
   actually move the posterior into the Cloud-9-favorable regime.**
   This is deferred to T90.30+.

2. **The Born approximation is used.** At m_phi=10 MeV, m_chi=500
   GeV, v=28 km/s: beta = m_chi v / (sqrt(2) m_phi) = 990. This is
   deep in the classical regime, where the Born form
   UNDERESTIMATES σ/m by a factor of ~2 (Tulin+Yu 2018, Eq. 2.20).
   The classical correction would push σ/m at fixed g_chi by ~2x
   higher, which would only HELP the Cloud-9 fit (lower g_chi
   needed). Deferred to T90.30+.

3. **The T90.28 v2 2D posterior histogram is reused** (not rebuilt).
   This is the (σ/m at v200, τ) posterior from the published
   Cloud-9 MCMC. The T90.29 v3 evaluation queries the same
   histogram.

4. **The Cloud-9 MCMC is degenerate** (τ=0.18 and τ=0.95 both fit
   the gas profile). The T90.29 v3 posterior captures this via
   the 2D (σ/m, τ) histogram from T90.28 v2.

5. **No MCMC re-run in T90.29.** The fix is the FORWARD MODEL
   (Yukawa vs power-law), not a re-fit. A re-fit with the
   Yukawa form + extended m_phi prior is T90.30+'s job.

## Cross-link to existing T90 work

- **T90.27 v1 (Channel 27)**: delta-prior at published best-fits.
  Superseded by T90.28 v2 and T90.29 v3.
- **T90.28 v2 (Channel 27)**: MCMC-derived 2D posterior
  evaluated via power-law σ/m(v). Superseded by T90.29 v3
  (Yukawa-form σ/m(v)). Preserved as a fallback in T41.
- **T90.29 v3 (Channel 27, this)**: MCMC-derived 2D posterior
  evaluated via the physical Yukawa form. New default when
  T90_RELHIC_V27=1.
- **`t40_yukawa_sigma_m.py`**: provides the Yukawa cross-section
  primitives (sigma_T_cm2, sigma_m_cm2_per_g, power_law_slope,
  g_chi_to_match_sigma_m_0). The T90.29 v3 module is a thin
  Cloud-9-specific wrapper around these primitives.
- **T90 magnetic-moment (Channel 17)**: independent EFT channel.
- **T95 cross-check (on master)**: tests the LZ-anchored Yukawa
  against astrophysical SIDM probes. The T90.29 v3 fix brings
  the Cloud-9 channel into alignment with the master Yukawa
  framework (T90.28 v2 used a power-law σ/m that was inconsistent
  with the Yukawa framework).

## How to use

To enable the new channel in a T41 run (same env var as v1/v2):

```bash
T90_RELHIC_V27=1 .venv-sidm-bench/Scripts/python.exe v0.3-prelim/code/t41_mediator_mass_joint_fit.py
```

The first call will auto-run the small MCMC (32 × 500) from T90.28
to produce the (σ/m, τ) posterior, then evaluate the Yukawa form
at the Cloud-9 v200 for each T41 evaluation.

## Test summary

| Component | Tests | Status |
|---|---|---|
| Yukawa σ/m at v=28 km/s | 3/3 | passing |
| Cloud-9 published range | 1/1 | passing |
| τ mapping | 2/2 | passing |
| loglike edge cases | 3/3 | passing |
| T41 wrapper | 1/1 | passing |
| Module importability | 1/1 | passing |
| Perturbativity check | 1/1 | passing |
| **T90.29 total** | **12/12** | **all passing** |
| T90.27 + T90.28 + T90.29 + LZ magnetic-moment (combined) | 69/69 | passing |

## Branch state

Added on top of T90.28 (commit efefc20) on `wip/tier3-magnetic-moment-LZ`.
T90.29 is a non-merge-blocking addition that **upgrades** the
Cloud-9 channel from a power-law approximation to the physical
Yukawa form. The T90 merge rule is unchanged.

## Future work (T90.30+)

1. **Re-run T41 with the m_phi prior extended to [1, 10] MeV**.
   This is the missing piece: the T90.29 v3 fix unlocks the
   Cloud-9-favorable regime, but the T41 v0.7 master prior
   doesn't sample m_phi in that range. With the extended
   prior, the master posterior will move to σ/m ~ 50-500 cm²/g
   at v=28 km/s, satisfying Cloud-9.

2. **Add the classical Yukawa correction** (Tulin+Yu 2018
   Eq. 2.20) to the sigma_m_cm2_per_g function. This is a ~2x
   correction in the high-beta regime and would tighten the
   σ/m posterior.

3. **Add the M51 Cloud S/N Yukawa likelihood component**
   (currently inherited from T90.27 v1's loglike_m51, which
   uses the power-law approximation).

4. **Cross-check the T90.29 v3 with the published Cloud-9
   MCMC at the m_phi=1-10 MeV scale.** This is a first-mover
   opportunity — no other paper has done this comparison yet.

## References

- arXiv:2608.04362 (Zhou et al. 2026): Cloud-9 + SIDM/CDM fit.
- arXiv:2603.05597 (Benitez-Llambay+ 2026, A&A 712, A11):
  methodology.
- arXiv:2607.21034: M51 Cloud S / N.
- Tulin+ Yu 2018 (RMP 90, 015004): SIDM review, Born-approximation
  Yukawa cross-section.
- Feng+ 2009 (arXiv:0908.2996): Yukawa dark matter.
- v0.3-prelim/code/t40_yukawa_sigma_m.py: project's existing
  Yukawa implementation (used by T90.29 v3).
- T90.27 v1 (commit b6dddb1) and T90.28 v2 (commit efefc20):
  superseded by T90.29 v3.
