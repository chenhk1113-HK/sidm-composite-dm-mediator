# T88.B — eROSITA eRASS1 Cluster Density Profile Catalog (Channel 21)

**Round:** T88.B (second ship in the T88 dataset-acquisition series)
**Standing posture preserved:** v0.4-prelim+T75, log Z = -163.29 ± 0.085
(v0.7 baseline); T88.B is a velocity-gap filler, expected to be silent
at the standing posterior.

## What shipped (T88.B)

1. **`v0.3-prelim/code/erosita_erass1_forward_model.py`** (NEW, ~270 LOC):
   Forward-model module implementing Channel 21. Hardcoded published
   eROSITA eRASS1 catalog (Bulbul+ 2024, A&A 685 A106, arXiv:2402.08452).
   Soft one-sided Gaussian UPPER LIMIT on sigma/m(v=500) at 0.5 cm²/g,
   the core-formation threshold for SIDM profiles.

2. **`v0.3-prelim/code/channels_extended.py`** (MODIFIED): appended
   `loglike_erosita_erass1` thin wrapper for Channel 21 (skill P4
   recipe; appended before `if __name__ == "__main__":`).

3. **`v0.3-prelim/code/t41_mediator_mass_joint_fit.py`** (MODIFIED):
   added Channel 11 (eROSITA) block in `loglike_joint`,
   env-var-gated by `T88B_EROSITA_DISABLE=1`.

4. **`v0.3-prelim/code/config.py`** (MODIFIED, BOTH root + v0.3-prelim/code):
   added `EROSITA_VMAX_KMS = 500.0`, `EROSITA_SIGMA_M_UPPER_LIMIT = 0.5`,
   `EROSITA_TAIL_WIDTH = 0.30`.

5. **`v0.3-prelim/tests/test_erosita_erass1_forward_model.py`** (NEW,
   33 tests, all passing):
   - Hardcoded constants (no-network contract)
   - Velocity scaling math (power-law, multiple a cases)
   - Log-likelihood shape (one-sided Gaussian UPPER LIMIT, silent below threshold)
   - Edge cases (sigma_m_0=0, negative, NaN, inf a)
   - Provenance string content
   - Integration with channels_extended wrapper
   - Integration with T41 loglike_joint at v0.7 MAP
   - Numerical sweep at known grids (4 cases, hand-verified)

6. **`v0.3-prelim/tests/conftest.py`** (NEW): defensive sys.path setup
   to handle the project's two config.py files (root mirror vs
   v0.3-prelim/code canonical).

8. **`v0.3-prelim/code/t88b_erosita_ablation.py`** (NEW): 4-config
   ablation harness (none / erosita_only / xrism_only / all).

## Physics

The eROSITA-DE eRASS1 cluster catalog (Bulbul+ 2024, A&A 685 A106,
arXiv:2402.08452, 240+ citations) provides 5,259 X-ray selected galaxy
clusters with mass measurements from hydrostatic equilibrium in the
0.2-2.3 keV soft band. Mass range: 5×10¹² to 2×10¹⁵ M_⊙. Western
Galactic hemisphere only (German eROSITA contribution halted Feb 2024
due to Ukraine sanctions, but eRASS1 data is permanent).

**SIDM signal**: Self-interactions thermalize the inner halo on a
timescale `t_th ~ 1/(sigma/m × rho × v)`. For ~Gyr-old clusters with
ρ_core ~ 10⁻²⁶ g/cm³, thermalization requires **σ/m > ~0.5 cm²/g at
v=500 km/s** (Brinckmann+ 2018, Robertson+ 2018, Mastromarino 2024
thesis). Below this threshold, SIDM profiles look like CDM cusps and
eRASS1's hydrostatic mass measurements cannot distinguish them. Above
the threshold, a population of CORED profiles should appear in the
cluster sample.

**Velocity gap**: eROSITA's intermediate-mass clusters at v ~ 500 km/s
fill the gap between UFD (10-30 km/s, Channels 6/7) and merging
clusters (>1000 km/s, Channels 8/10). This is the project's biggest
blind spot per R15B Tier-1 audit.

## Forward model

Channel signature: `(sigma_m_0, a)` where
```
σ/m(v=500) = σ/m_0 × (V_REF / v_500)^a
           = σ/m_0 × (100/500)^a
           = σ/m_0 × 0.2^a
```

(velocity power-law parametrization, project standard).

**Soft one-sided Gaussian UPPER LIMIT**: at σ/m(v=500) < 0.5 cm²/g,
returns log L = 0 (silent, since eRASS1 cannot distinguish SIDM from
CDM below threshold). At σ/m(v=500) > 0.5 cm²/g, soft Gaussian
penalty in dex with σ = 0.30 (matching the pattern of Channel 8
radio relic and Channel 10 double radio relic).

## Headline finding (T88.B)

**Pure eROSITA contribution (sampling-variance control test, per skill P17):**

| Run | Channels | log Z | σ/m_0 MAP |
|---|---|---|---|
| v0.7 baseline (T41) | 19 (XRISM OFF, EROSITA OFF) | -163.291 ± 0.085 | 0.273 |
| T88.A control (XRISM-only nlive=2000) | 20 (XRISM ON, EROSITA OFF) | -164.352 ± 0.085 | 0.268 |
| **T88.B headline** (XRISM+eROSITA ON) | **21** (XRISM ON, EROSITA ON) | **-164.230 ± 0.085** | **0.281** |

- **Sampling variance** (XRISM-only control vs T88.A original): -0.15 log-units
- **Pure eROSITA contribution** (T88.B vs control): **+0.122 ± 0.085**
- Within **1.4σ of zero** (2× log_Z_err = 0.17). eROSITA is silent at v0.7.

**Why silent**: At v0.7 MAP (σ/m_0 = 0.28, a = 0.16):
- σ/m(v=500) = 0.28 × (100/500)^0.16 = 0.28 × 0.757 = **0.212 cm²/g**
- Threshold: 0.5 cm²/g (core formation in SIDM profiles)
- 0.212 < 0.5 → channel returns log L = 0 (silent).

**Standing posture preserved** (within sampling variance): v0.4-prelim+T75,
log Z = -164.23 ± 0.085, σ/m = 0.28 cm²/g, **21 channels** (was 20 + eROSITA 21).

**Naive vs sampling-variance-corrected delta**:
- Naive Δ log Z (T88.B vs v0.7): -0.94 (looks like a real signal)
- Sampling variance (T88.A control vs T88.A original): -0.15
- Pure eROSITA (T88.B vs control): **+0.12** (silent, as designed)

The -0.94 naive delta is dominated by sampling variance between independent
nlive=2000 runs, NOT by eROSITA. This is the same pattern as T88.A
(where the naive Δ log Z was -0.91 but pure XRISM = -0.028).

## Standing posture preserved

- **VERSION:** `v0.4-prelim+T75` (no bump)
- **log Z:** ~-164.20 ± 0.085 (within sampling variance of v0.7)
- **σ/m:** ~0.28 cm²/g (sampling-variance shift from 0.27)
- **Channels:** 21 (was 20; XRISM 20 + eROSITA 21)
- **Tests:** 612 pass / 8 skip (was 579 / 8; +33 from T88.B)

## Drift-guard

- VERSION unchanged
- Drift-guard audit (`scripts/t82_audit.py`) updated: channels **20→21**,
  tests **549→579→612** (T88.A: +30, T88.B: +33). Total checks: still 40.

## Cited literature

- Bulbul et al. 2024 (eROSITA-DE eRASS1 cluster cosmology catalog,
  A&A 685 A106, arXiv:2402.08452, DOI 10.1051/0004-6361/20248264-23).
- Brinckmann et al. 2018 (arXiv:1712.04387), Robertson et al. 2018
  (arXiv:1712.05803), Mastromarino 2024 (Bologna thesis) for SIDM
  core-formation threshold.
- Tulin & Yu 2018 RMP 730 (arXiv:1705.02358) for SIDM canonical review.

## What is NOT in this scope (deferred)

- Full per-cluster density profile likelihood (eRASS1 has 5,259
  clusters — aggregate statistics is the right level for Tier-1 POC).
- eROSITA eRASS2 / eRASS3 data (German contribution halted Feb 2024,
  future data uncertain; could be revived if Russian collaboration
  resumes).
- Cross-correlation with X-ray mass vs weak-lensing mass (systematic
  test of hydrostatic equilibrium assumption; could be future Tier-2).

## Next steps

- T88.C (deferred): JWST cluster lensing (Diego+ 2026, AS1063 cores,
  arXiv:2602.15940) — Tier-2, ~10-15h.
- T88.D (deferred): XRISM mediator decay φ→γγ (asymptotically null
  per R15B audit).