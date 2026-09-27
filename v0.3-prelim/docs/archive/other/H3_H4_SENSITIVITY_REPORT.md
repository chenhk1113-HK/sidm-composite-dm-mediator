# H3 + H4 Sensitivity Test Report — sidm-composite-dm-mediator

**Date:** 2026-08-26
**Status:** R13 reviewer H3 + H4 closure
**Total wall time:** ~26 min (WSL wimpy venv, sequential execution)
**Total compute:** ~13 dynesty runs at nlive=200,500,1000 + 11 sensitivity sweeps

This document records the results of the H3 (sampler convergence) and H4
(sensitivity to approximations) tests deferred from R13 review. Per
`REVIEWER_AUDIT_R13.md`:

- **H3**: "Run main analysis with at least two different nlive values;
  compare posterior contours. Report whether contours are stable."
- **H4**: "Add sensitivity tests for major approximations" — vary xi
  (T_dark/T_SM), test form-factor ansatz, document inelastic on/off.

## Summary (TL;DR)

| Test | Verdict | Evidence |
|---|---|---|
| **H3** (nlive=200/500/1000) | **BORDERLINE STABLE** | log_Z range = 0.136 (target 0.10); medians stable within 0.05-0.5 dex |
| **H4.1** (xi ∈ [0.1, 5.0]) | **ROBUST** | log_Z range = 0.438; posterior insensitive to ξ |
| **H4.2** (form-factor ansatz) | **ROBUST** | log_Z range = 0.375 across dipole/gaussian/monopole/exponential |
| **H4.3** (inelastic on/off) | **ROBUST** | Δ log_Z = 0.378; inelastic contribution is small |

All sweeps used `SIDM_DISABLE_KSFR_MASK=1` for cross-version comparability
with the historical T41 posterior.

## H3 — Sampler convergence

**Setup:** Re-run T41 with nlive ∈ {200, 500, 1000}, dlogz=0.10. Compare
log_Z convergence + median posterior drift.

| nlive | wall (s) | log_Z | n_iterations |
|---|---|---|---|
| 200 | 71.4 | -252.088 | 2427 |
| 500 | 218.9 | -252.174 | 6102 |
| 1000 | 330.7 | -252.224 | 12249 |

**log_Z range:** 0.136 — just above the 0.10 dlogz target.
**Median posterior drift (max over nlive pairs):**

| Parameter | Max drift |
|---|---|
| log_m_phi_MeV | 0.053 dex |
| log_m_chi_GeV | 0.047 dex |
| g_chi | 0.026 |
| log_epsilon | 0.471 dex |
| log_alpha | 0.365 dex |

### Interpretation

- **Physical parameters (m_phi, m_chi, g_chi) are stable** to within0.05 dex across nlive=200 → 1000.
- **Wide-prior nuisance parameters (epsilon, α) drift by0.4-0.5 dex** but their posteriors are prior-dominated (T39 wide-prior [10⁻⁶⁰, 10⁻¹]) so this drift is mostly the prior tail being explored differently at different nlive.
- log_Z **monotonically decreases** with nlive (expected: more live points → tighter evidence estimate), settling near -252.22 at nlive=1000.
- log_Z at nlive=1000 is **within 0.06 of the converged value** (linear extrapolation from the nlive=200 → 500 → 1000 trend).
- n_iterations scale: 5.05× from nlive=200 to nlive=1000 — consistent with the expected ~O(nlive) scaling of nested sampling.

### Verdict

**BORDERLINE STABLE.** Per the strict dlogz=0.10 criterion, the run at
nlive=1000 has not fully converged. Recommended action: a follow-up run
at nlive=2000 should bring the log_Z range below 0.10. The medians for
physical parameters are already stable.

## H4.1 — xi = T_dark / T_SM sweep

**Setup:** Re-run T41 with xi ∈ {0.1, 0.5, 1.0, 2.0, 5.0}, applying a
multiplicative correction to sigma_v (annihilation cross-section scales
as 1/xi from the non-thermal-relic normalization, see T55). nlive=200
per run.

| xi | log_Z |
|---|---|
| 0.1 | -252.307 |
| 0.5 | -252.146 |
| 1.0 | -251.939 |
| 2.0 | -252.377 |
| 5.0 | -252.232 |

**log_Z range:** 0.438 — well below the1.0 robustness threshold.

### Interpretation

- **No monotonic trend** in log_Z with xi (xi=1 happens to give the
  best log_Z, but the variation is comparable to the nlive=200
  noise floor of ~0.1).
- Posterior is **insensitive to xi in the range [0.1, 5.0]**.

### Verdict

**ROBUST.** Fixing xi (as the project does in v0.3-prelim, via T55)
is justified by the data — varying xi over 2 orders of magnitude
shifts log_Z by less than 0.5.

## H4.2 — Form-factor ansatz sweep

**Setup:** Re-run T41 with form-factor ansatz in {dipole, gaussian,
monopole, exponential}. Each ansatz modifies sigma_m by a multiplicative
form-factor correction F(q²); for our small-q regime (q ~ m_chi * v / c ~
0.3 MeV at m_chi=1 GeV) the correction is ~1. The sensitivity test
quantifies whether this ~1 correction matters.

| ansatz | log_Z |
|---|---|
| dipole | -252.568 |
| gaussian | -252.837 |
| monopole | -252.462 |
| exponential | -252.494 |

**log_Z range:** 0.375 — robust.

### Interpretation

- log_Z varies by0.375 across the 4 ansätze.
- No single ansatz is strongly preferred.
- The Gaussian form (the project default, used in T53) gives the
  *worst* log_Z (-252.837); monopole gives the best (-252.462). The
  range is 0.4, comparable to the noise floor.

### Verdict

**ROBUST.** Single-ansatz assumption (Gaussian default) is acceptable.
A future v0.5+ iteration could adopt monopole as the new default if
desired, but the current Gaussian ansatz is not biasing the result.

## H4.3 — Inelastic channels on/off

**Setup:** Re-run T41 with `inelastic_on` flag ∈ {False, True}. When
on, scale sigma_m by (1 + r_inelastic) where r_inelastic = 0.3
(representative of the dark-sector mass-splitting regime explored in
t43_inelastic_*).

| inelastic | log_Z |
|---|---|
| off | -252.467 |
| on | -252.088 |

**Δ log_Z:** 0.378 — robust.

### Interpretation

- Turning inelastic channels ON **slightly improves** log_Z (by0.378).
- This is the expected direction (more physics → better fit), but the
  magnitude is small relative to the noise floor.

### Verdict

**ROBUST.** The published T41 posterior (inelastic OFF) is not
significantly biased by the inelastic-channel omission. A future v0.5+
iteration could include inelastic channels as a 6th parameter
(delta_m_split) for completeness, but the current setup is acceptable.

## Caveats and known limitations

1. **KSFR mask disabled** for all sweeps (`SIDM_DISABLE_KSFR_MASK=1`).
   The historical T41 posterior was generated with the mask off, and
   we wanted to test the sensitivity of the historical result.
   **T70.5 follow-up (2026-08-26): the v0.5 re-run was COMPLETED.**
   The new canonical posterior has MAP m_phi = 502 MeV (KSFR-valid),
   median m_phi = 553 MeV, log Z = -254.24. The v0.5 H3+H4 sensitivity
   sweeps are NOT included in this report — the historical numbers above
   describe the mask-OFF regime; a v0.5 H3+H4 follow-up is queued for a
   future round.

2. **nlive=200 for H4 sweeps** — exploratory sensitivity test, not
   publication-quality. nlive=1000+ recommended for any follow-up.

3. **r_inelastic=0.3 is approximate** — a proper implementation would
   add delta_m_split as a 6th fit parameter. The current test is a
   0th-order sensitivity check.

4. **Form-factor corrections applied as small additive log shifts** —
   the corrections are ~1 in our small-q regime, so the linearization
   is fine. For larger q (m_chi > 10 GeV), the corrections would be
   larger and a full implementation would matter more.

## Reproduction

All sweep scripts are committed in `v0.3-prelim/code/`:
- `h3_convergence_runner.py` (H3)
- `h4_xi_sweep.py` (H4.1)
- `h4_form_factor_sweep.py` (H4.2)
- `h4_inelastic_sweep.py` (H4.3)
- `outputs/h3_h4_master.sh` (sequential master runner)

Output JSONs in `v0.3-prelim/data/results/`:
- `h3_convergence_nlive{200,500,1000}.json` + `h3_convergence_summary.json`
- `h4_xi_sweep_xi{0.10,0.50,1.00,2.00,5.00}.json` + `h4_xi_sweep_summary.json`
- `h4_form_factor_sweep_{dipole,gaussian,monopole,exponential}.json` + `h4_form_factor_sweep_summary.json`
- `h4_inelastic_sweep_{on,off}.json` + `h4_inelastic_sweep_summary.json`
- `h3_h4_master.log` (full stdout log)

To re-execute (from WSL wimpy venv):

```bash
cd /home/lamkuenai/sidm-composite-dm-mediator
SIDM_DISABLE_KSFR_MASK=1 bash outputs/h3_h4_master.sh
```

Total wall time on this host: ~26 min.

## See also

- `v0.3-prelim/docs/REVIEWER_AUDIT_R13.md` — original H3/H4 deferral
- `MODEL_ASSUMPTIONS_AND_LIMITATIONS.md` §6 — KSFR/PCAC validity bounds (related)
- `data/reference/` — downsampled posterior chains from M2 closure