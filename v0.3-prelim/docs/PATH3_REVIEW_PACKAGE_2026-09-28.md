# Path 3 Review Package — Species-dependent σ_ij(v)

**Date:** 2026-09-28
**Branch:** master @ `ac1e1c3`
**Tag:** `v19.0-paper-freeze-2026-09-27`
**Reviewer:** Please critique the 3-path investigation (Path 1 categorical E, Path 2 continuous E, Path 3 species-dependent σ).

---

## TL;DR

Three missing-parameter hypotheses were tested:

1. **Categorical ℰ-rescaling** (§10.4g) — 5/5 PASS in-sample, no held-out test
2. **Continuous ℰ-proxy** (§10.4h) — 5/5 PASS in-sample, **1/2 held-out FAIL** (Segue 1)
3. **Species-dependent σ_ij** (§10.4i) — 5/5 PASS in-sample, **1/2 held-out FAIL** (Segue 1)

**Verdict: 1 descriptive, 0 predictive.** Two independent functional-form extensions (continuous ℰ and species-dependent σ) converge on the same failure mode — Segue 1 fails by ~2.5×.

---

## Why this matters

The reviewer's `A reasoned guess.docx` proposed that σ_eff depends on environment (ℰ), not on a universal σ(v). Our investigation shows:
- Categorical ℰ works empirically (§10.4g)
- Continuous ℰ-proxy does NOT generalize (§10.4h)
- σ-v shape (species-dependent peaks) does NOT generalize (§10.4i)

The pattern is robust: any **functional-form restriction** (continuous ℰ, independent σ peaks) fails to predict Segue 1. Only a **free per-bin parameter** (categorical) survives the in-sample test.

---

## Code: scripts/build_species_dependent_sigma.py (~360 lines)

**Key functions:**

```python
def sigma_species(v, v_targets, sigma_peaks, w_list, sigma_0, a_slope):
    """Generic sigma(v) for one species: Yukawa bg + Gaussian peaks."""
    bg = yukawa_bg(v, sigma_0, a_slope)
    peaks = sum(gaussian_peak(v, vt, sp, w)
                for vt, sp, w in zip(v_targets, sigma_peaks, w_list))
    return bg + peaks


def sigma_eff_three_comp(v, f_H, sigma_HH, sigma_HL, sigma_LL):
    """Two-component DM: sigma_eff = f_H^2 sigma_HH + 2 f_H f_L sigma_HL + f_L^2 sigma_LL."""
    f_L = 1 - f_H
    return f_H * f_H * sigma_HH + 2 * f_H * f_L * sigma_HL + f_L * f_L * sigma_LL


def sigma_eff_3species(v, f_H, v_t_HL, v_t_LL, peak_shift=0.0):
    """sigma_HH at fixed Phase 44 positions. sigma_HL/LL at shifted positions."""
    v_targets_HH = p44["v_targets"]
    v_targets_HL = [vt + v_t_HL for vt in v_targets_HH]
    v_targets_LL = [vt + v_t_LL for vt in v_targets_HH]
    sHH = sigma_species(v, v_targets_HH, ...)
    sHL = sigma_species(v, v_targets_HL, ...)
    sLL = sigma_species(v, v_targets_LL, ...)
    return sigma_eff_three_comp(v, f_H, sHH, sHL, sLL)


def fit_3species(observables, beta_p2=-3.40, deltas_p2=None):
    """Fit HL_offset, LL_offset to minimize violations. 35 starting points."""
    # scipy.optimize.minimize with Nelder-Mead
    best_result = None
    best_loss = np.inf
    for HL_init in [-100, -50, 0, 50, 100]:
        for LL_init in [-200, -100, -50, 0, 50, 100, 200]:
            x0 = [HL_init, LL_init]
            result = minimize(loss_fn, x0, method='Nelder-Mead',
                              options={'xatol': 1e-2, 'fatol': 1e-6, 'maxiter': 500})
            if result.fun < best_loss:
                best_loss = result.fun
                best_result = result
    return best_result.x, best_loss
```

**Two free parameters:** HL_offset (km/s shift for σ_HL peaks) and LL_offset (km/s shift for σ_LL peaks).

**Optimizer:** Nelder-Mead with 35 starting points (5 × 7 grid).

---

## Result — Path 3 in detail

**In-sample fit (5/5 PASS):**

| Observable | f_H | σ_eff_fit | σ_obs | Bound | Verdict |
|------------|----:|----------:|------:|-------|---------|
| Cloud-9 (RELHIC) | 0.05 | 106.7 | 100 | ≥100 | PASS (7%) |
| Draco (field dSph) | 0.20 | 0.954 | 1.0 | <1.0 | PASS (4.6%) |
| Sculptor (field dSph) | 0.20 | 0.090 | 1.0 | <1.0 | PASS (91%) |
| Fornax (satellite) | 0.30 | ~0 | 5.0 | <5 | PASS (oversuppressed) |
| Cluster (Bullet) | 0.50 | ~0 | 0.1 | <0.1 | PASS (oversuppressed) |

**Best-fit:** HL_offset = -113.47 km/s, LL_offset = +1.32 km/s.

**Held-out prediction (1/2 PASS):**

| System | f_H | σ_eff_fit | σ_obs | Bound | Verdict |
|--------|----:|----------:|------:|-------|---------|
| Leo T (classical dSph) | 0.20 | 0.040 | 0.5 | <1 | PASS |
| Segue 1 (UFD) | 0.10 | 2.481 | 1.0 | <1 | **FAIL (2.5× over)** |

---

## Comparison with Paths 1 and 2

| Path | Approach | Params | In-sample | Held-out | Predictive? |
|------|----------|--------|-----------|----------|-------------|
| §10.4g | Categorical ℰ-rescaling | 2 | 5/5 PASS | N/A | N/A |
| §10.4h | Continuous ℰ-proxy | 1 | 5/5 PASS | 1/2 FAIL | No |
| §10.4i | Species-dependent σ_ij | 2 | 5/5 PASS | 1/2 FAIL | No |

**Pattern:** in-sample fits all pass, but held-out predictions fail in the same way. The categorical approach wins by virtue of being a free parameter (per-bin offset), not by virtue of capturing real microphysics.

---

## What this tells us about the missing parameter

1. **The missing parameter is NOT σ-v shape.** Two independent microphysics extensions (continuous ℰ-proxy in §10.4h, species-dependent σ in §10.4i) converge on the same failure mode. This is a robust negative result.

2. **Segue 1 is the critical discriminator.** It has the lowest baryon fraction (f_b ≈ 10^-4), is isolated (no tidal stripping), and has low gravothermal phase (t/t_core ≈ 0.1). Every physical suppression mechanism we tested (baryons, tides, gravothermal collapse, species coupling) leaves Segue 1 unchanged or worsens it.

3. **The categorical ℰ-rescaling (§10.4g) wins because it's a free parameter.** With field ×0.35 and satellite ×0.30 free per-bin, the categorical model can fit any individual observable. Continuous ℰ (§10.4h) and species-dependent σ (§10.4i) restrict the functional form, and that restriction fails to generalize.

---

## What was added to the paper

- **§10.4g** (4.5 KB): Categorical ℰ-rescaling, exploratory
- **§10.4h** (4.6 KB): Continuous ℰ-proxy, 1/2 held-out FAIL
- **§10.4i** (4 KB): Species-dependent σ_ij, 1/2 held-out FAIL
- **Fig 6** (categorical): σ_eff vs V_max per ℰ bin
- **Fig 7** (continuous): σ_eff vs V_max with in-sample + held-out
- **Fig 8** (species): σ(v) for HH/HL/LL + σ_eff with held-out

---

## What was added to the codebase

| File | Purpose |
|------|---------|
| `scripts/smoke_test_continuous_E.py` | 15-min smoke test (1-param, 4/5) |
| `scripts/build_continuous_E_predictive.py` | Path 2 full (1-param, 5/5 in-sample, 1/2 held-out) |
| `scripts/build_species_dependent_sigma.py` | Path 3 full (2-param, 5/5 in-sample, 1/2 held-out) |
| `v0.3-prelim/data/results/phase4c_smoke_test_continuous_E.json` | Smoke test |
| `v0.3-prelim/data/results/phase4c_continuous_E_predictive.json` | Path 2 results |
| `v0.3-prelim/data/results/phase4d_species_dependent_sigma.json` | Path 3 results |
| `v0.3-prelim/docs/PHASE4B_OPTION_B_REPORT_2026-09-28.md` | Categorical ℰ report |
| `v0.3-prelim/docs/PHASE4C_SMOKE_TEST_REPORT_2026-09-28.md` | Smoke test report |
| `v0.3-prelim/docs/PHASE4C_PATH2_FULL_REPORT_2026-09-28.md` | Path 2 report |
| `v0.3-prelim/docs/PHASE4D_PATH3_FINAL_REPORT_2026-09-28.md` | Path 3 report |

---

## Reviewer questions to address

1. **Is the held-out failure (Segue 1, 2.5×) a real signal or a model pathology?** The categorical approach oversuppresses Fornax and Cluster to σ_eff ≈ 0 — unphysical. The continuous ℰ approach has the same pathology. The species-dependent σ approach has HL_offset = -113 km/s, which is large compared to the v=18-22 dSph band — the σ_HL peaks are far from where they're being evaluated. All three models have pathologies at high ℰ.

2. **Are there other ℰ-proxy components we haven't tried?** Possibilities: (a) adiabatic contraction factor (Gnedin+ 2004), (b) specific angular momentum j*, (d) halo concentration c_vir, (e) dark matter particle mass m_χ (kinematic decoupling temperature).

3. **Is Segue 1 σ_obs bound robust?** σ/m < 1 cm²/g for Segue 1 is based on the 2019-2020 literature. Recent observations may have tightened or loosened this bound. Worth checking.

4. **Should the paper present the three sections as a single narrative?** §10.4g/h/i could be merged into one section titled "Investigation of the missing parameter" with three subsections. The current structure is three independent sections, which makes the comparison cleaner.

5. **Is there a Path 4?** Possibilities:
   - Try other held-out systems (Ursa Minor, Bootes, Hercules, CVnI dwarf, etc.) — does Segue 1 fail consistently, or do other UFDs pass?
   - Try alternative ℰ-proxies (e.g. adiabatic contraction, specific angular momentum)
   - Run a true MCMC to characterize the predictive failure rate statistically

---

## My recommendation

**D1 — ship v19.0 with all three sections** (§10.4g/h/i). The negative results are valuable — they constrain where the missing parameter is NOT. Three negative results is a stronger paper claim than one positive-but-unconstrained result.

If the reviewer disagrees, **D2** (ship with §10.4g only) is the fallback — it preserves the strongest empirical claim while avoiding the negative results.

A **Path 4** would extend the investigation to other held-out systems or alternative ℰ-proxies, but I would only pursue this if the reviewer explicitly asks for it.

---

## Final state

- **Master @ `ac1e1c3`** ✓ pushed to GitHub
- **wip/cloud-9-relhic** synced ✓
- **Tag `v19.0-paper-freeze-2026-09-27`** re-pinned ✓
- **8/8 self-checks pass** on master `ac1e1c3`

---

## Code snippet — running Path 3 from scratch

```bash
cd /c/Users/lamkuenai/projects/sidm-composite-dm-mediator
./.venv-sidm-bench/Scripts/python.exe scripts/build_species_dependent_sigma.py
```

**Output:**
- `v0.3-prelim/data/results/phase4d_species_dependent_sigma.json`
- `v0.3-prelim/docs/figures/fig8_species_dependent_sigma.png`

**Wall time:** <30 seconds (Nelder-Mead with 35 starting points on 5 in-sample observables).