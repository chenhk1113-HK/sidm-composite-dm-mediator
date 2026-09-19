# T120.6 — Reviewer T120review1.docx Response (2026-09-19)

**Reviewer:** T120review1.docx
**Date received:** 2026-09-19
**Date response:** 2026-09-19
**Status:** Addressed; v1.12 paper §9.5 needs update with honest caveats.

## Summary of reviewer's 5 critical points

| # | Point | Status |
|---|---|---|
| 1 | Does two-component model break the kinematic 1/v² floor? | ❌ NO — different mechanism |
| 2 | Quantitative tension numbers (correct v_eff) | ⚠️ MOSTLY PASS — UFD v<7 km/s FAILS |
| 3 | Occam / complexity cost (BIC) | ⚠️ +34 BIC (T120 worse by Occam) |
| 4 | Relation to existing literature | ✓ Yang+ 2025 PRD, Yu 2026 PRL cited |
| 5 | Test coverage for simultaneous Cloud-9+dSph | ✓ tests_t120_4_joint_fit.py enforces all 4 simultaneously |

## Detailed response to each point

### [1] Does the two-component model actually break the kinematic 1/v² floor?

**Answer: NO.** The two-component model does NOT break unitarity. It uses a
DIFFERENT mechanism: mass segregation + halo evolutionary-state selection.

**Mechanism (not loophole around 1/v²):**

  sigma/m_eff(v, r, halo_type) = f_H(r, halo_type)² × sigma_HH(v)

Both Cloud-9 and dSph see the SAME underlying sigma_HH(v) (which respects
1/v² kinematics from the Yukawa background). What differs is the f_H
profile at the OBSERVATION radius:

  - Cloud-9 (core-forming, f_H(r=0.05) = 0.85): sigma_eff at v=28 = 0.85² × sigma_HH
  - dSph (core-collapsed, f_H(r=0.20) = 0.30): sigma_eff at v=15 = 0.30² × sigma_HH

The 11× reduction (0.30/0.85)² = 0.125 comes from halo evolutionary state,
NOT from breaking the 1/v² floor. The unitarity limit at v=15 km/s for
m_chi = 10.44 GeV is sigma_max ≈ 1.4×10⁶ cm²/g (Phase 44 sigma_0 ×
(v_ref/v)^a_slope = 0.052 × 38.6 = 2.0 cm²/g is well below this).

### [2] Quantitative tension numbers (with correct v_eff convention)

**Horigome+ 2025 limit** (velocity-dependent, w=10): sigma/m < 0.8 cm²/g
applies at v_eff = 0.64 × V_max.

| v_eff | halo | v1.11 single-comp | v1.12 two-comp | Limit | v1.12 violation |
|---|---|---|---|---|---|
| 5 km/s | UFD | 18.4 | **1.50** | 0.8 | **1.87× (FAILS)** |
| 7 km/s | UFD | — | 0.78 | 0.8 | 0.98× (borderline) |
| 10 km/s | UFD | 6.5 | **0.39** | 0.8 | 0.49× (PASSES) |
| 15 km/s | dSph | 5.0 | **0.18** | 0.8 | 0.23× (PASSES) |
| 28 km/s | Cloud-9 | 100 | **128** | 100 (req) | 1.28× (PASSES) |
| 100 km/s | SPARC | 0.07 | 0.19 | 0.5 | 0.39× (PASSES) |
| 500 km/s | Cluster | 0.0002 | 0.0002 | 1.0 | 0.0002× (PASSES) |

**HONEST FINDING:** v1.12 PASSES at v_eff >= 7 km/s but FAILS at v_eff < 7 km/s
(the most extreme UFDs, V_max ~ 5 km/s → v_eff ~ 3 km/s).

**Cause:** The Yukawa background sigma_0 × (v_ref/v)^a_slope with
sigma_0 = 0.052, a_slope = 1.93 grows without bound at low v. The
two-component f_H suppression (factor 0.09) is not enough to offset the
background at v < 7 km/s.

**Progression:** 800× (v1.9) → 25-92× (v1.10) → 6-23× (v1.11) → **PASS at v≥7, FAILS at v<7** (v1.12)

### [3] Occam / complexity cost (BIC/AIC)

**Estimated BIC change (assuming same logL improvement at v=15, 28, 100, 500):**

| Model | n_params | BIC (n_data=127) |
|---|---|---|
| Phase 44 single-comp | 11 | 69.49 |
| Phase 53 v2 (clockwork) | 7 | 50.62 |
| T120 +two-comp +grav +Gauss | 18 | 103.40 |
| **Delta BIC (T120 vs Phase 44)** | **+7** | **+33.91** (T120 WORSE) |

**HONEST FINDING:** T120 is WORSE by Occam's razor (BIC penalty +34 for
~7 additional parameters) unless the joint logL improvement is at least
+17 (BIC = -2*logL + k*log(n), so improvement must exceed k*log(n)/2).

**Refit needed:** The current BIC estimate assumes the same logL as Phase 44.
A proper joint fit including dSph + UFD data would give the true Delta logL.
Until that refit is done, the complexity penalty is a real concern that
must be honestly reported.

**Caveats:**
- The +7 params is an upper bound; some are degenerate or fixed by theory
  (e.g., m_H/m_L ratio can be fixed at 3:1 from Yang+ 2025 PRD).
- Some parameters are JUSTIFIED by independent measurements (gravothermal
  evolution time is constrained by cluster density profiles).
- The model has ADDITIONAL predictive power: UFD sigma/m scaling,
  dSph radial sigma/m profile, cluster sigma/m scaling with mass.

### [4] Relation to existing literature

The T120 construction builds directly on:

- **Yang, Tsai, Fan 2025 PRD 112, 083011** [42] (arXiv:2504.02303) —
  Two-component asymmetric DM with mass ratio 3:1, cross-component
  Møller/Rutherford scattering drives mass segregation. Our f_H(r)
  profiles are derived from their Fig. 2.
- **Yu+ 2026 PRL** [23] (arXiv:2510.11006) — Core-collapsed SIDM halos
  explain JVAS B1938+666 perturber, Fornax 6 globular clusters, GD-1
  stream. Our gravothermal selection (f_H drops at observation radius
  for core-collapsed halos) is a direct application of their framework.
- **Yang, Nadler, Yu, Zhong 2024 JCAP** [43] (arXiv:2305.16176) —
  Universal analytical density profile for SIDM halos. Our f_H profile
  parametrization follows their evolutionary-state classification.

**Positioning:** T120 is not a NEW mechanism — it's an APPLICATION of
peer-reviewed frameworks to our Phase 44 multi-resonance model. The novel
contribution is the COMBINATION:
  Phase 44 multi-resonance + Yang+ 2025 PRD two-component + Yu+ 2026 PRL
  gravothermal + Gaussian BW profile
which simultaneously satisfies all 4 observational constraints.

### [5] Test coverage enforcing Cloud-9 + dSph simultaneously

The test file `v0.3-prelim/tests/test_t120_4_joint_fit.py` includes
`test_all_pass_with_default` which asserts:

```python
def test_all_pass_with_default(self):
    """Default w1=3 km/s should satisfy ALL constraints simultaneously."""
    r = joint_fit_evaluation()
    assert r["all_pass"], f"Not all constraints pass: {r}"
```

Where `all_pass` is computed as:
```python
"all_pass": (
    sm_cloud9 >= 100
    and sm_dsph <= 0.8
    and 0.05 <= sm_sparc <= 0.5
    and sm_cluster < 1.0
)
```

This is a CONJUNCTION test — if ANY of the four constraints fails,
the test fails. 15 total tests in this file, all PASS.

**Additional mechanism tests:**
- `test_combination_works`: verifies that the COMBINATION of gravothermal
  selection AND Gaussian BW is what enables the resolution (each alone
  is insufficient).
- `test_w1_10_fails_dsph`: verifies that the model fails when Gaussian
  width is too wide (transition from "all pass" to "dSph fails" at w1 ≈ 7 km/s).

## Recommendations for v1.13

To fully address the reviewer's points, v1.13 should:

1. **Update §9.5 limitations:** Add UFD v<7 km/s failure with quantitative
   numbers and explain that the Yukawa background σ_0 × v^-a_slope with
   a_slope = 1.93 is too steep at low v. Possible fix: lower a_slope to
   ~1.0 (constant background) or use a hard cutoff below v_min ~ 10 km/s.

2. **Add §9.7 Occam's razor discussion:** Compute true Delta logL from
   a joint fit including dSph/UFD data. Show that T120's complexity cost
   is justified by additional predictive power (UFD radial profile,
   cluster mass-dependence).

3. **Add §9.8 comparison with Yang+ 2025 PRD directly:** Show that our
   f_H profiles agree with their Fig. 2 to within ~20%, and that the
   Phase 44 multi-resonance sigma_HH is consistent with their cross-
   component sigma_HL when rescaled.

4. **Refit dSph + UFD jointly:** Currently we use Phase 44 best-fit
   parameters from SPARC + JVAS + Cloud-9. A joint fit including dSph
   and UFD data would give the true logL improvement.

## Headline

**v1.12 PASSES at v_eff >= 7 km/s (Cloud-9, dSph, SPARC, cluster)**
**v1.12 FAILS at v_eff < 7 km/s (extreme UFDs)**
**BIC penalty +34 (T120 worse by Occam until proper joint fit done)**
**Three mechanisms working together: NOT a loophole, a real physical framework**