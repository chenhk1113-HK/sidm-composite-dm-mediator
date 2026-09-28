# Path 2 Final Report — Continuous ℰ-proxy + Held-out prediction

**Date:** 2026-09-28
**Branch:** master @ `ca71831`
**Wall time:** ~30 min (smoke test 15 min + full Path 2 30 min)
**Result:** 5/5 in-sample PASS, **1/2 held-out FAIL**

---

## What I tested (Path 2)

**Goal:** replace categorical ℰ-rescaling (Phase 4B Option B) with a **continuous** ℰ-proxy, fit to 5 standing observables, then **predict** a held-out system.

**ℰ-proxy formula (3 components):**

log_E = max(0, log10(f_b / 10^-3)) + 0.5 × log10(host_M_vir / M_dwarf) + 0.3 × (t / t_core)

**Model:** log10(σ_eff) = log10(σ_eff_P44) + β × log_E + δ_bin (per-bin offset)

**Fit method:** scipy.optimize.minimize Nelder-Mead, 6 starting points

**Held-out systems (not in fit):**
- Leo T (classical dSph, V_max=15 km/s, σ_obs<0.5 cm²/g)
- Segue 1 (UFD, V_max=12 km/s, σ_obs<1.0 cm²/g)

---

## Result

**In-sample fit (5/5 PASS):**

| Observable | log_E | σ_eff_fit | σ_obs | Verdict |
|------------|------:|----------:|------:|---------|
| Cloud-9 (RELHIC) | 0.015 | 154.1 | 100 (lower) | PASS |
| Draco (field dSph) | 0.060 | 0.96 | 1.0 (upper) | PASS (4% margin) |
| Sculptor (field dSph) | 0.361 | 0.15 | 1.0 (upper) | PASS (85% margin) |
| Fornax (satellite) | 1.590 | ~0 | 5.0 (upper) | PASS (oversuppressed) |
| Cluster (Bullet) | 2.300 | ~0 | 0.1 (upper) | PASS (oversuppressed) |

**β = -3.40, all 4 δ_bin offsets converged to ≈ 0** (per-bin offsets are underdetermined with only 5 data points; the model reduces to a 1-parameter power-law).

**Held-out prediction (1/2 PASS):**

| System | log_E | σ_eff_fit | σ_obs | Verdict |
|--------|------:|----------:|------:|---------|
| Leo T (classical dSph) | 0.507 | 0.037 | 0.5 (upper) | PASS |
| Segue 1 (UFD) | 0.030 | 2.38 | 1.0 (upper) | **FAIL (2.4× over)** |

---

## Verdict

**The continuous ℰ-proxy with this 3-component form is NOT predictive.** Segue 1 fails by 2.4× on the tight upper bound.

### What this tells us about the missing parameter

1. **Categorical ℰ structure (§10.4g) is real but is NOT captured by f_b + host-ratio + t/t_core alone.**
   Either (i) a different continuous ℰ variable is needed, or (ii) the missing parameter is genuinely categorical (not derivable from a smooth ℰ-proxy), or (iii) the missing parameter lives elsewhere (e.g. independent resonance peaks per species — Path 3).

2. **Segue 1 is a critical test.** If the missing parameter were baryon-driven, Segue 1 (lowest f_b, isolated, lowest log_E) should PASS easily. The FAIL by 2.4× suggests the simple continuous-ℰ form does not capture the physical suppression mechanism.

3. **The fit's oversuppression of high-ℰ systems is a model pathology.** The power-law σ_eff = σ_eff_P44 × E^β with β = -3.40 drives σ_eff to negligible values for log_E > 1.5. A physically sensible model should floor at the observed upper bound.

### Comparison with categorical ℰ-rescaling

| Approach | Free params | In-sample 5/5? | Held-out predictive? |
|----------|-------------|----------------|---------------------|
| Phase 4A null | 0 | NO (3 FAIL) | N/A |
| Categorical ℰ-rescaling (Phase 4B Option B) | 2 | YES | N/A (no held-out test) |
| Continuous ℰ-proxy (Path 2) | 1 (β) | YES | **NO (1/2)** |

---

## What was added to the paper

- **§10.4h** (new section, 4.6 KB): continuous ℰ-proxy + held-out prediction + verdict
- **Fig 7** (replaces smoke-test Fig 7): σ_eff vs V_max with circles=in-sample, squares=held-out
- **scripts/build_continuous_E_predictive.py** (300 lines): 2-param fit with scipy.optimize.minimize
- **v0.3-prelim/data/results/phase4c_continuous_E_predictive.json** (in-sample + held-out predictions)

---

## What's next

This is a **strong negative result** for the continuous ℰ-proxy hypothesis. Three options:

**Option C1: Push to Path 3** (independent HH/HL/LL resonance peaks, ~2.2 h)
- Test whether the missing parameter lives in σ-v *shape*, not ℰ
- Independent peak positions per species may resolve the dSph tension without ℰ

**Option C2: Shortcut — ship as final §10.4h** (~30 min)
- This negative result is publishable as is
- §10.4g (categorical, 2-param, 5/5) + §10.4h (continuous, 1-param, fails held-out) tells a complete story
- Ship v19.0 with both

**Option C3: Stop, document, ship v19.0** (~10 min)
- §10.4g already in paper (categorical, post-hoc, exploratory)
- §10.4h as a final note: "continuous ℰ-proxy not yet predictive; deeper microphysics deferred"
- Skip Path 3

**My recommendation: C1 if you want to test the species-dependent hypothesis; C3 if you want to ship now.**

---

## Code and data references

| File | Purpose |
|------|---------|
| `scripts/smoke_test_continuous_E.py` | 15-min smoke test (1-param, 4/5) |
| `scripts/build_continuous_E_predictive.py` | 2-param fit + held-out |
| `v0.3-prelim/data/results/phase4c_smoke_test_continuous_E.json` | Smoke test results |
| `v0.3-prelim/data/results/phase4c_continuous_E_predictive.json` | Full Path 2 results |
| `v0.3-prelim/docs/figures/fig7_continuous_E_predictive.png` | In-sample + held-out plot |
| `v0.3-prelim/docs/PAPER_V1_DRAFT.md` §10.4h | Paper section |
| `v0.3-prelim/docs/PHASE4C_SMOKE_TEST_REPORT_2026-09-28.md` | Smoke test report |

---

## Verification

- 8/8 Round 13 self-checks pass on master `ca71831`
- pytest test_paper_claims.py: 12/12 pass
- audit_claims.py: 24/24 standing numbers clean
- walk_paper_tables.py: tables clean (Phase 4B + Phase 4C keywords covered)