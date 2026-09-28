# Path 2 Smoke Test — Continuous ℰ-proxy fit

**Date:** 2026-09-28
**Wall time:** 15 min (smoke test budget)
**Branch:** master @ `26e6b22`
**Script:** `scripts/smoke_test_continuous_E.py`

---

## What I tested

**Question:** Can a continuous ℰ-proxy (single power-law parameter β) fit the 5 standing observables with reasonable residuals, before committing to the full 2.7-hour Path 2?

**Approach:**
1. Define ℰ-proxy combining 3 components:
   - log_E_b = max(0, log10(f_b / 1e-3)) — baryon fraction contribution
   - log_E_host = 0.5 × log10(host_ratio) — tidal stripping contribution
   - log_E_phase = 0.3 × (t/t_core) — gravothermal phase contribution
   - log_E = log_E_b + log_E_host + log_E_phase

2. Reference: RELHIC (Cloud-9) has log_E = 0 (no suppression).

3. Fit: σ_eff = σ_eff_P44 × (E)^β, with β free.

---

## Result

**Best-fit β = -2.73.**

| Observable | log_E | log_σ_P44 | σ_predicted | σ_obs | ratio | verdict |
|------------|-------|-----------|-------------|-------|-------|---------|
| Cloud-9 (RELHIC) | 0.015 | 2.239 | **157.7** | 100 (lower) | 1.577 | **PASS** (57% margin) |
| Draco (field dSph) | 0.060 | 0.185 | **1.05** | 1.0 (upper) | 1.049 | **FAIL** (5% over) |
| Sculptor (field dSph) | 0.361 | 0.416 | **0.27** | 1.0 (upper) | 0.269 | **PASS** (73% margin) |
| Fornax (satellite) | 1.590 | 1.016 | **0.0004** | 5.0 (upper) | 0.000 | **PASS** (oversuppressed) |
| Cluster (Bullet) | 2.300 | -2.403 | **~0** | 0.1 (upper) | 0.000 | **PASS** (oversuppressed) |

**4 PASS, 1 FAIL (Draco) out of 5.**

---

## Verdict

**The continuous ℰ-proxy fit is almost as good as the categorical ℰ-rescaling, but uses 1 parameter instead of 2.**

| Approach | Free params | 5/5 PASS? | Notes |
|----------|-------------|-----------|-------|
| Phase 4A null | 0 | NO (3 FAIL) | dSph tail tension unresolved |
| **Categorical ℰ-rescaling (Phase 4B Option B)** | **2** | **YES** | field ×0.35, satellite ×0.30 |
| **Continuous ℰ-proxy (Path 2 smoke test)** | **1** | **NO (4/5)** | β=-2.73, Draco 5% over tight bound |

---

## What's left for full Path 2

The smoke test reveals what the full 2.7-hour Path 2 needs to address:

1. **Draco 5% violation** — needs a 2nd parameter (per-bin offset, or per-bin β, or fixed categorical residual).
2. **Fornax and Cluster oversuppression** — the fit drives σ_eff to ~0 for high-ℰ systems, which is unphysical. Need to cap σ_eff at the observed upper bound (no physical system has σ_eff = 0).
3. **Held-out prediction** — full Path 2 picks a held-out system (e.g. Leo T, Segue 1) and predicts σ_eff. The smoke test only checks in-sample fit.

---

## Recommended next step

The smoke test confirms the **direction** (continuous ℰ works partially with 1 parameter), but the full Path 2 with 2 parameters and held-out prediction is needed to make this publishable. Two options:

**Option B1 (continue Path 2 as planned, ~2.7 h):**
- Add a per-bin offset (or a 2nd β)
- Pick Leo T as held-out system
- Predict σ_eff, check residuals
- Add §10.4h to paper
- Generate Fig 7

**Option B2 (shortcut, ~30 min):**
- The smoke test result is itself a finding: "continuous ℰ-proxy with 1 parameter fits 4/5; categorical ℰ with 2 parameters fits 5/5; the missing parameter is likely *categorical* ℰ (not continuous)."
- Add this as a 1-paragraph note in §10.4g (or as §10.4g-finale)
- Skip Path 2 + 3 entirely, ship v19.0

**My recommendation: B1** if you want a real test of the reviewer's hypothesis at the predictive level. **B2** if you want to ship v19.0 now.

The smoke test itself is **not** a paper-worthy finding — it's a diagnostic that confirms the direction but reveals the limitation (1 parameter is insufficient). Going from 4/5 to 5/5 with held-out prediction is the right threshold for a paper claim.