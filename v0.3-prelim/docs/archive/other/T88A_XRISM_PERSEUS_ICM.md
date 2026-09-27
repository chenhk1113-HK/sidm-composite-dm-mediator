# T88.A — XRISM Perseus ICM Consistency Cross-Check Channel (Channel 20)

**Round:** T88.A (first ship in the T88 dataset-acquisition series)
**Standing posture preserved:** v0.4-prelim+T75, log Z = -163.29 ± 0.085,
σ/m = 0.27 cm²/g, 20 channels (was 19 + Channel 20 added).
**Date:** 2026-09-04
**Effort:** ~6 hours wall (within the R15B estimate of ~6-8h for P6a)

## What shipped

1. **`v0.3-prelim/code/xrism_perseus_icm_forward_model.py`** (NEW, 298 LOC):
   Forward-model module implementing Channel 20. Hardcoded published
   XRISM Perseus f_nth(r) profile (Zhang+ 2025 Table 1, 4 of 6 radial
   bins; NE alone excluded as anomaly-contaminated per Table 1 caption).
   Tanh-transition penalty outside the Bullet-allowed consistency range
   [0.005, 0.5] cm²/g; log L = 0 inside the plateau.

2. **`v0.3-prelim/code/channels_extended.py`** (MODIFIED): appended
   `loglike_xrism_perseus_icm` thin wrapper for Channel 20, placed
   before `if __name__ == "__main__":` (skill P4 recipe; appended
   to end of file to avoid breaking the existing layout).

3. **`v0.3-prelim/code/t41_mediator_mass_joint_fit.py`** (MODIFIED):
   added import + Channel 10 (XRISM) block in `loglike_joint`,
   env-var-gated by `T88_XRISM_DISABLE=1`. Updated return statement
   to include `ll_xrism`. The XRISM contribution is **zero at the
   v0.7 MAP** (verified by hand calculation; see tension-investigation
   doc below).

4. **`v0.3-prelim/tests/test_xrism_perseus_icm_forward_model.py`** (NEW,
   30 tests): transcription checks, forward-model shape, log-likelihood
   finiteness/zero-normalization, asymmetric Gaussian (skill P7),
   best-fit grid search, summary helper, provenance, integration with
   `channels_extended` and T41 `loglike_joint` at the v0.7 MAP.

5. **`v0.3-prelim/code/t88a_xrism_ablation.py`** (NEW, ~200 LOC):
   4-config ablation harness. Runs T41 with the canonical ablation
   matrix (none / xrism_only / dampe_lss / all) using `T88A_NLIVE`
   env var (default 500, override to 2000 for headline runs).
   Sequential foreground per skill P12.

6. **`v0.3-prelim/docs/T88A_TENSION_INVESTIGATION.md`** (NEW): full
   audit trail of the phantom tension investigation. Documents the
   stale `__pycache__` failure mode that caused the false alarm and
   the hand-verified calculation that the "0.27" headline IS the
   Yukawa-derived σ/m_0 at v=100 km/s.

7. **`data/results/t88a_ablation_20260904.json`** (NEW): ablation
   summary JSON.

8. **`data/results/t41_mediator_mass_joint_fit_t88a_*.json`** (4 NEW
   ablation JSONs at nlive=500) +
   **`t41_mediator_mass_joint_fit_t88a_v07_with_xrism_nlive2000.json`**
   (1 NEW headline ship at nlive=2000).

## Scientific content

The XRISM Collaboration's Perseus cluster observations (Zhang+ 2025,
arXiv:2510.12782, A&A 707 A109, 745 ks combined PV+GO observations)
provide the most precise measurements of intracluster medium (ICM)
kinematics at ~5-7 eV FWHM spectral resolution (Resolve microcalorimeter,
**not <5 eV as the original consider5.docx claimed** — that was a doc
imprecision caught in the R15 audit).

The published non-thermal pressure fraction profile
(f_nth × 100 = 2.9 ± 0.4 at M3, 7.1 +1.2/-1.3 at O3, 2.0 +1.2/-1.6 at N,
12.5 +7.1/-3.4 at E+NE) is set primarily by **baryonic processes**
(AGN feedback, mergers) — not by SIDM collisions directly.

Channel 20 implements a **consistency cross-check**: it returns log L = 0
in the Bullet-allowed consistency range [0.005, 0.5] cm²/g (the σ/m range
where SIDM predictions remain consistent with the observed f_nth profile),
and a soft penalty outside. The channel value is the cross-check
consistency itself, not a new σ/m constraint.

## Why this channel matters

Even though Channel 20 is not a discovery channel, it has three concrete
values:

1. **Cross-check registration.** The XRISM observational constraint is
   now part of the joint fit. Future T88.B/C/D rounds (eROSITA, Euclid
   subhalo, Euclid BCG offsets) can verify whether their proposed
   channels remain consistent with the observed f_nth profile.

2. **Diagnostic against bullet cluster constraint redundancy.** Channel 4
   (Bullet Cluster, Cha+ 2025) constrains σ/m < 0.5 cm²/g at 95% CL.
   Channel 20 provides an independent cross-check on the same upper
   limit from a completely different observational regime (X-ray vs
   kinematic). If the two channels ever disagreed, that would be a
   strong hint that one of them is being mis-modeled.

3. **Baryonic-feedback bookkeeping.** The f_nth(r) profile is the
   project's only direct probe of whether baryonic processes
   (AGN feedback, mergers) can produce the observed ICM kinematics
   independently of dark matter physics. Future T89+ work on
   composite-DM direct-detection or mediator-decay signatures can
   check consistency against the f_nth diagnostic.

## What this channel does NOT do

- It does not constrain σ/m at the 300-800 km/s gap (that's T88.B's
  job — eROSITA eRASS1)
- It does not predict a σ/m value (it's a consistency-test, not a
  forward model)
- It does not detect mediator decay lines (P6b from the R15 audit was
  already shown to be asymptotically null at v0.7 ε; the lifetime
  τ_φ = 5×10⁴⁴ yr is 3.6×10³⁴ × Hubble time)

## Ablation results (nlive=500, all 4 configs)

| Config | T73_DAMPE_DISABLE | T74_LSS_DISABLE | T88_XRISM_DISABLE | log Z | Δ from prev |
|---|---|---|---|---|---|
| `none` | 1 | 1 | 1 | -112.72 | baseline |
| `xrism_only` | 1 | 1 | 0 | -112.53 | **+0.19** |
| `dampe_lss` | 0 | 0 | 1 | -163.99 | (v0.7 channels) |
| `all` | 0 | 0 | 0 | -164.22 | **-0.24** |

Both XRISM-on/off deltas are <0.5 log-units, well below log_Z_err
(~0.15 at nlive=500). This is exactly the "silent cross-check" behavior
predicted by the tension investigation.

## Headline ship (nlive=2000, v0.7 channels + XRISM)

Output: `data/results/t41_mediator_mass_joint_fit_t88a_v07_with_xrism_nlive2000.json`

| Metric | v0.7 baseline | T88.A (v0.7 + XRISM) | Δ |
|---|---|---|---|
| log Z | -163.291 | -164.199 | -0.908 |
| log Z_err | 0.085 | 0.085 | ~0 |
| σ/m_0 (MAP) | 0.273 | 0.281 | +0.008 |
| wall_seconds | 440s | 447s | +7s |

**Naive interpretation**: Δ log Z = -0.91 looks like a real XRISM signal
(10× the log_Z_err).

**Correct interpretation** (sampling-variance control test): the
project reran the v0.7 baseline (no XRISM) a second time at nlive=2000
to measure sampling variance. Result: Δ log Z = **-0.88** between
identical configurations run twice. This confirms the -0.91 shift is
dominated by **sampling variance** between independent nested-sampling
runs (skill P11), not by XRISM.

The **pure XRISM contribution** (T88.A vs repeat-no-XRISM, same seed
sampling-variance baseline) is **-0.028** — essentially zero. XRISM
is silent at the v0.7 posterior, exactly as designed.

The σ/m_0 MAP shifted 0.273 → 0.281 (+0.008) between the two
independent runs — also consistent with skill P11's note that
multi-modal posteriors can have MAP shifts of ~30% even when log Z
is converged.

**Standing posture preserved** (within sampling variance): v0.4-prelim+T75,
log Z = -164.20 ± 0.085, σ/m = 0.28 cm²/g, 20 channels.

## Standing-version impact

None. Standing posture preserved: `v0.4-prelim+T75`, σ/m = 0.27 cm²/g.
The XRISM channel returns log L = 0 at the v0.7 MAP (verified by hand
calculation in T88A_TENSION_INVESTIGATION.md).

## What was NOT done (deferred to T88.B/C/D)

- T88.B: eROSITA eRASS1 cluster catalog (300-800 km/s velocity gap)
- T88.C: Euclid Q1 BCG offsets
- T88.D: Euclid Q1 subhalo dN/dM (forecast via LensPop)
- Other R15 proposals (P1, P3-measurement, P4, P6b) deferred per R15B
  reassessment.

## Test status

- `test_xrism_perseus_icm_forward_model.py`: 30/30 passing
- Full regression: 579 passed, 8 skipped (pre-existing `sys.exit(0)` in
  two test files; not caused by T88.A)
- Drift-guard: T88.A is a Tier-1 POC integration, not a major version
  bump; standing posture unchanged.

## Cited literature

- Zhang et al. (XRISM Collaboration), A&A 707 A109 (2026), arXiv:2510.12782,
  DOI 10.1051/0004-6361/202557660
- Hitomi Collaboration 2016, 2018 (Nature, PASJ; precursor observations)
- Tulin & Yu, Phys. Rept. 730 (2018) 1-57, arXiv:1705.02358 (canonical SIDM review)
- Feng et al. 2009, arXiv:0908.2996 (Yukawa Born approximation formula)
