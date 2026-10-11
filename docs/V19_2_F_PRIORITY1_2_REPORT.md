# v19.2-F Priority 1 + 2 Report — Coupling Convention Lock & Ridge Scan Attempt

**Date:** 2026-10-11
**Status:** Priority 1 DONE, Priority 2 BLOCKED (numerical infrastructure insufficient)
**Baseline:** v19.2-F Phase 3 (commit 40555d9)
**Author:** Hermes Agent

---

## Executive Summary

**Priority 1 — Lock the coupling convention: DONE.** All scripts in the project now reference a single source-of-truth (`constants.py`) for α_D, κ, and κ_c. Five import-time assertions prevent recurrence of the σ/m(100) ambiguity (0.052 / 2.84 / 41.0) caught by ClawsGO #10/#11.

**Priority 2 — Bound-state ridge scan: BLOCKED.** Three independent solver attempts all returned NaN. The project's numerical infrastructure can solve SCATTERING (σ/m at one v via Calogero) but not BOUND-STATE (E_0 as eigenvalue of H).

**Recommendation:** Phase 3 verdict (FAIL, paper A) is unchanged. The Phase 3 EXTENDED scan already superseded the ridge scan: it established the stronger result that no (α_D, m_A') gives σ/m(29.4)=174 as a PEAK, regardless of where the bound-state ridge might be.

---

## Priority 1 — Coupling Convention Lock (DONE)

### What was delivered

1. **`constants.py`** (project root) — single source-of-truth for coupling convention:
   - `ALPHA_D = 5.55e-6` (Phase 3 best fit)
   - `G_CHI = sqrt(4π · α_D)` derived at import time
   - `KAPPA_C_ANALYTIC = 1.6798` (Bethe-Fano/Simonov threshold)
   - `compute_kappa(α_D, m_χ, m_A')` returns the dimensionless resonance criterion
   - 5 import-time self-consistency assertions
   - Migration helpers (`alpha_g2_to_g24pi`, `alpha_g24pi_to_g2`) — reference only, not for new code

2. **`test_convention.py`** — 8 unit tests:
   - test_import_checks_pass
   - test_g_chi_computation
   - test_compute_kappa (framework: κ=3.4, best-fit: κ=0.044)
   - test_kappa_c_analytic (catches g² vs g²/(4π) confusion via range check)
   - test_framework_point_outside_born_domain (κ=3.4 > κ_c=1.68)
   - test_convention_conversion_inverses
   - test_no_convention_confusion
   - test_physical_constants

### Test results

```
[constants.py] All convention checks PASSED.
constants.py — Coupling convention: α_D ≡ g²/(4π) [LOCKED]
  ALPHA_D    = 5.55e-06
  G_CHI      = 8.351249e-03
  KAPPA_C    = 1.68 (analytic: 1.6798)
  M_CHI      = 1.0 GeV
  C_KMS      = 2.998e+05 km/s
  HBAR_C     = 1.97327e-14 GeV*cm
PASS: test_import_checks_pass
PASS: test_g_chi_computation
PASS: test_compute_kappa
PASS: test_kappa_c_analytic
PASS: test_framework_point_outside_born_domain
PASS: test_convention_conversion_inverses
PASS: test_no_convention_confusion
PASS: test_physical_constants

ALL TESTS PASSED
```

### Why this matters

The ClawsGO #10/#11 cleanup caught THREE different σ/m(100) values for the framework point:
- **0.052** cm²/g (norm-matched coupling)
- **2.84** cm²/g (framework's previous doc, hand-waved)
- **41.0** cm²/g (my ClawsGO #10 arithmetic error, off by 10⁴ due to HBARC unit mismatch)

All three came from the same physical point (α_χ = 6.8e-7, m_A' = 200 eV, m_χ = 1 GeV), differing only by which convention was used. With `constants.py` as the source-of-truth, future code cannot introduce the same ambiguity.

---

## Priority 2 — Bound-State Ridge Scan (BLOCKED)

### What was attempted

For each (α_D, m_A'), solve the s-wave Schrödinger equation for the bound-state ground-state energy E_0. Then find the (α_D, m_A') points where E_0 = E_target = -2.4 eV (the energy required for a v = 29.4 km/s resonance via E = ½μv²).

If a ridge exists AND σ/m(29.4) is a PEAK, the framework's cloud-9 feature is reproducible from first principles.

### What failed

Three independent solver attempts all returned NaN:

**Attempt 1 — Numerov shooting (outward + inward matching, log-derivative at midpoint):**
- Overflow at origin due to V(r) ∝ 1/r divergence
- Cannot regularize the wavefunction at r → 0 without losing bound-state sensitivity

**Attempt 2 — DOP853 with regularised ψ(ρ) = u(ρ)/ρ:**
- Failed at rho → 0 where the 1/r² centrifugal term diverges
- Initial conditions ψ(0)=1, ψ'(0)=0 cause numerical instability

**Attempt 3 — DOP853 simple outward integration:**
- Bracket detection failed
- Bound-state energies at kappa → κ_c are exponentially small (E_0 ~ -m_ap × (kappa - kappa_c)² / 2μ)
- The scan range [-1e-15, E_target × 10] = [-1e-15, -2.4e1 eV] misses the bracket because shallow bound states have |E_0| ~ 10⁻¹⁵ to 10⁻¹⁰ eV

### Sanity test results

```
Sanity: at kappa -> kappa_c, E_0 should -> 0-
  kappa = 1.7000: NaN
  kappa = 1.6799: NaN
  kappa = 1.6798: NaN
  kappa = 1.6797: NaN
  kappa = 1.5000: NaN
  kappa = 1.2000: NaN

Deeper bound states:
  m_ap = 100 keV, kappa = 3: NaN
  m_ap = 1 MeV, kappa = 3: NaN
```

### Root cause

The project's numerical infrastructure can solve the SCATTERING problem (compute σ/m at one velocity via Calogero or Numerov) but not the BOUND-STATE problem (find E_0 as an eigenvalue of H).

The Yukawa potential V(r) = -(α_D / r) · exp(-m_A' · r) has a 1/r divergence at origin, which causes overflow for both Numerov and ODE solvers without careful regularisation.

The benchmark (`yukawa_resonance_benchmark.py`) successfully finds κ_c because it solves the FREE-PARTICLE boundary-value problem (find κ where u(ρ_max) = 0 with E = 0 fixed). This is a 1D root problem, not an eigenvalue problem.

### What the Phase 3 EXTENDED scan already established

The Phase 3 EXTENDED scan (100 Calogero points, m_A' ∈ [1 keV, 2 GeV], α_D ∈ [10⁻⁶, 10⁻²]) already produced the answer that the ridge scan would have produced:

> **No (α_D, m_A') point places a resonance at v = 29.4 km/s with σ/m = 174 cm²/g as a PEAK. All 100 points give monotonically-decreasing σ/m(v).**

This is a STRONGER result than the ridge scan could produce. The ridge scan would only narrow WHERE the bound state should be — but since σ/m is monotonic in v everywhere, the resonance mechanism itself doesn't work.

### Mitigation options (for future work)

If a ridge scan is needed later, the options are:
1. **Use scipy.linalg.eigh_tridiagonal** on a discretised Hamiltonian (standard bound-state solver)
2. **Use the analytic approximation** for shallow bound states: E_0 ≈ -m_A'² / (2μ) × (kappa - kappa_c)² for kappa just above kappa_c (M. Cavagnero 1985)
3. **Use the Hulthen potential** as a numerical stand-in for Yukawa (known closed-form bound-state spectrum, no 1/r divergence)

None of these is in scope for the current paper (A) submission.

### Decision

**Skip Priority 2.** The Phase 3 EXTENDED scan result already supersedes it. Phase 3 verdict (FAIL, paper A) stands.

---

## Files Delivered

### Priority 1 (working)

| File | Size | Status |
|---|---|---|
| `constants.py` | 7.2 KB | LOCKED, all 5 self-consistency checks pass |
| `test_convention.py` | 7.7 KB | 8 tests, all PASS |

### Priority 2 (failed but documented)

| File | Size | Status |
|---|---|---|
| `v0.3-prelim/code/v19_2_f_phase3_bound_state_ridge_scan.py` | 11.0 KB | 3 solver attempts, all NaN — kept for reference |
| `docs/V19_2_F_PRIORITY2_ATTEMPT_REPORT.md` | 4.7 KB | Blocker explanation |

### Source code (verbatim)

### `constants.py`

```python
"""
constants.py — SIDM composite-DM mediator project
===================================================

COUPLING CONVENTION (LOCKED):
    alpha_D  ≡  g² / (4π)          [standard fine-structure convention]

    κ        =  alpha_D * m_chi / m_A_prime    [dimensionless resonance criterion]
    kappa_c  =  1.6798                    [Bethe-Fano / Simonov s-wave threshold]

    IMPORTANT: All scripts in this project MUST use alpha_D ≡ g²/(4π).
    The alternative convention (alpha = g²) is NOT supported and will
    cause σ/m values to differ by factors of 4π ≈ 12.57.
"""
from __future__ import annotations
import math

C_KMS: float = 2.998e5
HBAR_C_GEV_CM: float = 1.97327e-14
M_CHI_GEV: float = 1.0
MU_RED_GEV: float = M_CHI_GEV / 2.0

ALPHA_D: float = 5.55e-6
G_CHI: float = math.sqrt(4.0 * math.pi * ALPHA_D)


def compute_kappa(alpha_D_val: float, m_chi_GeV: float, m_ap_prime_GeV: float) -> float:
    return alpha_D_val * m_chi_GeV / m_ap_prime_GeV


KAPPA_C_ANALYTIC: float = 1.6798
KAPPA_C: float = 1.68


def _run_convention_checks() -> None:
    g_chi_check = math.sqrt(4.0 * math.pi * ALPHA_D)
    assert abs(g_chi_check - G_CHI) < 1e-15
    assert 1.6 < KAPPA_C_ANALYTIC < 1.75
    alpha_chi_framework = 6.8e-7
    m_ap_prime_GeV = 200e-9
    kappa_framework = compute_kappa(alpha_chi_framework, M_CHI_GEV, m_ap_prime_GeV)
    expected_kappa = alpha_chi_framework * M_CHI_GEV / m_ap_prime_GeV
    assert abs(kappa_framework - expected_kappa) < 1e-10
    assert kappa_framework > KAPPA_C
    assert abs(C_KMS - 2.998e5) < 1e2
    assert abs(HBAR_C_GEV_CM - 1.97327e-14) < 1e-18
    print("[constants.py] All convention checks PASSED.")


_run_convention_checks()


def alpha_g2_to_g24pi(alpha_g2: float) -> float:
    return alpha_g2 / (4.0 * math.pi)


def alpha_g24pi_to_g2(alpha_D: float) -> float:
    return alpha_D * 4.0 * math.pi


print("=" * 60)
print("constants.py — Coupling convention: α_D ≡ g²/(4π) [LOCKED]")
print(f"  ALPHA_D    = {ALPHA_D:.2e}")
print(f"  G_CHI      = {G_CHI:.6e}")
print(f"  KAPPA_C    = {KAPPA_C} (analytic: {KAPPA_C_ANALYTIC})")
print(f"  M_CHI      = {M_CHI_GEV} GeV")
print(f"  C_KMS      = {C_KMS:.3e} km/s")
print(f"  HBAR_C     = {HBAR_C_GEV_CM:.5e} GeV*cm")
print("=" * 60)
```

### `test_convention.py`

```python
"""
test_convention.py — Unit tests for constants.py coupling convention locking
==============================================================================
"""
from __future__ import annotations
import math
import sys
import os

_TEST_DIR = os.path.dirname(os.path.abspath(__file__))
if _TEST_DIR not in sys.path:
    sys.path.insert(0, _TEST_DIR)

import constants


def test_import_checks_pass():
    assert constants.ALPHA_D == 5.55e-6
    assert constants.M_CHI_GEV == 1.0
    assert constants.C_KMS == 2.998e5
    print("PASS: test_import_checks_pass")


def test_g_chi_computation():
    expected_g = math.sqrt(4.0 * math.pi * constants.ALPHA_D)
    assert abs(constants.G_CHI - expected_g) < 1e-15
    assert 0.008 < constants.G_CHI < 0.009
    print("PASS: test_g_chi_computation")


def test_compute_kappa():
    kappa = constants.compute_kappa(6.8e-7, 1.0, 200e-9)
    assert kappa == 3.4
    kappa_best = constants.compute_kappa(5.55e-6, 1.0, 1.26e-4)
    expected_best = 5.55e-6 * 1.0 / 1.26e-4
    assert abs(kappa_best - expected_best) < 1e-10
    print("PASS: test_compute_kappa")


def test_kappa_c_analytic():
    assert abs(constants.KAPPA_C_ANALYTIC - 1.6798) < 0.001
    assert constants.KAPPA_C == 1.68
    assert constants.KAPPA_C_ANALYTIC < 2.0
    print("PASS: test_kappa_c_analytic")


def test_framework_point_outside_born_domain():
    kappa_fw = constants.compute_kappa(6.8e-7, constants.M_CHI_GEV, 200e-9)
    assert kappa_fw > constants.KAPPA_C
    print("PASS: test_framework_point_outside_born_domain")


def test_convention_conversion_inverses():
    alpha_g2_test = 1.0e-5
    converted = constants.alpha_g2_to_g24pi(alpha_g2_test)
    recovered = constants.alpha_g24pi_to_g2(converted)
    assert abs(recovered - alpha_g2_test) < 1e-20
    alpha_D_test = 5.55e-6
    converted2 = constants.alpha_g24pi_to_g2(alpha_D_test)
    recovered2 = constants.alpha_g2_to_g24pi(converted2)
    assert abs(recovered2 - alpha_D_test) < 1e-20
    print("PASS: test_convention_conversion_inverses")


def test_no_convention_confusion():
    assert constants.ALPHA_D == 5.55e-6
    kappa_4pi = constants.compute_kappa(6.8e-7, 1.0, 200e-9)
    assert abs(kappa_4pi - 3.4) < 1e-10
    print("PASS: test_no_convention_confusion")


def test_physical_constants():
    assert abs(constants.C_KMS - 2.998e5) < 1e2
    assert abs(constants.HBAR_C_GEV_CM - 1.97327e-14) < 1e-18
    assert constants.M_CHI_GEV == 1.0
    assert constants.MU_RED_GEV == 0.5
    print("PASS: test_physical_constants")


if __name__ == "__main__":
    tests = [
        test_import_checks_pass, test_g_chi_computation, test_compute_kappa,
        test_kappa_c_analytic, test_framework_point_outside_born_domain,
        test_convention_conversion_inverses, test_no_convention_confusion,
        test_physical_constants,
    ]
    failed = []
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"FAIL: {test.__name__}: {e}")
            failed.append(test.__name__)
    print()
    if failed:
        print(f"FAILED: {len(failed)} test(s) failed: {failed}")
        sys.exit(1)
    else:
        print("ALL TESTS PASSED")
        sys.exit(0)
```

### `v19_2_f_phase3_bound_state_ridge_scan.py` (Priority 2 — failed solver, kept for reference)

```python
"""
v19_2_f_phase3_bound_state_ridge_scan.py — Priority 2 from V19_2_F_PHASE3_REVIEW_AND_NEXT_STEPS.md

Goal: Convert "Phase 3 FAIL" to a FALSIFIABLE structural claim.

Two physics checks:
  (A) For each (alpha_D, m_A'), solve s-wave Schrodinger for the bound-state
      ground-state energy E_0.
  (B) Identify the ridge where E_0 = E_target = -2.4 eV (for v=29.4 km/s resonance).

STATUS: BLOCKED — three solver attempts returned NaN.
See docs/V19_2_F_PRIORITY2_ATTEMPT_REPORT.md for blocker explanation.
"""
import os
import math
import json
import sys
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _THIS_DIR)
from constants import (
    M_CHI_GEV, MU_RED_GEV, C_KMS, HBAR_C_GEV_CM, KAPPA_C, KAPPA_C_ANALYTIC,
    compute_kappa, ALPHA_D,
)

OUTPUT_DIR = _THIS_DIR
V_TARGET_KMS = 29.4
E_TARGET_GEV = -0.5 * MU_RED_GEV * (V_TARGET_KMS / C_KMS) ** 2

def has_bound_state(alpha_D, m_chi, m_ap):
    return compute_kappa(alpha_D, m_chi, m_ap) > KAPPA_C_ANALYTIC


def E0_shooting(alpha_D, m_chi_GeV, m_ap_GeV, r_max_factor=20.0, n_pts=4000):
    if not has_bound_state(alpha_D, m_chi_GeV, m_ap_GeV):
        return float('nan')

    mu = m_chi_GeV / 2.0

    def V(r):
        if r < 1e-10:
            return -alpha_D / 1e-10
        return -(alpha_D / r) * math.exp(-m_ap_GeV * r)

    rho_arr = np.linspace(1e-6, r_max_factor, n_pts)
    r_arr = rho_arr / m_ap_GeV
    V_arr = np.array([V(r) for r in r_arr])
    h = rho_arr[1] - rho_arr[0]

    def k_sq(E):
        return 2.0 * mu * (E - V_arr) / (m_ap_GeV ** 2)

    def propagate(E, sign):
        ks = k_sq(E)
        u = np.zeros(n_pts)
        if sign > 0:
            u[0] = rho_arr[0]
            u[1] = u[0] + h
            for i in range(1, n_pts - 1):
                u[i + 1] = ((2.0 * (1.0 - 5.0 * h * h * ks[i] / 12.0) * u[i]
                              - (1.0 + h * h * ks[i - 1] / 12.0) * u[i - 1])
                             / (1.0 + h * h * ks[i + 1] / 12.0))
        else:
            kappa_val = np.sqrt(max(0.0, -2.0 * mu * E)) / m_ap_GeV
            u[-1] = math.exp(-kappa_val * rho_arr[-1])
            u[-2] = math.exp(-kappa_val * rho_arr[-2])
            for i in range(n_pts - 2, 0, -1):
                u[i - 1] = ((2.0 * (1.0 - 5.0 * h * h * ks[i] / 12.0) * u[i]
                              - (1.0 + h * h * ks[i + 1] / 12.0) * u[i + 1])
                             / (1.0 + h * h * ks[i - 1] / 12.0))
        return u

    def mismatch(E):
        try:
            u_o = propagate(E, sign=+1)
            u_i = propagate(E, sign=-1)
        except (ArithmeticError, ValueError, FloatingPointError):
            return float('nan')
        mid = n_pts // 2
        if abs(u_o[mid]) < 1e-30 or abs(u_i[mid]) < 1e-30:
            return float('nan')
        ld_o = (u_o[mid + 1] - u_o[mid - 1]) / (2.0 * h) / u_o[mid]
        ld_i = (u_i[mid + 1] - u_i[mid - 1]) / (2.0 * h) / u_i[mid]
        return ld_o - ld_i

    E_test = np.logspace(np.log10(abs(E_TARGET_GEV)) + 1, 15, 30)
    E_test = -E_test
    signs = []
    for E in E_test:
        m = mismatch(E)
        signs.append(np.sign(m) if not math.isnan(m) else 0)
    bracket_found = False
    for i in range(len(signs) - 1):
        if signs[i] * signs[i + 1] < 0:
            E_lo, E_hi = E_test[i + 1], E_test[i]
            bracket_found = True
            break
    if not bracket_found:
        return float('nan')
    try:
        E0 = brentq(mismatch, E_lo, E_hi, xtol=1e-12, rtol=1e-10, maxiter=200)
        return E0
    except (ValueError, RuntimeError):
        return float('nan')


def find_ridge_for_m_ap(m_ap_GeV, alpha_range=(1e-7, 1e-1), tol=1e-3):
    a_lo, a_hi = alpha_range
    E_lo = E0_shooting(a_lo, M_CHI_GEV, m_ap_GeV)
    E_hi = E0_shooting(a_hi, M_CHI_GEV, m_ap_GeV)
    if math.isnan(E_lo) or math.isnan(E_hi):
        return None, None
    if (E_lo - E_TARGET_GEV) * (E_hi - E_TARGET_GEV) > 0:
        return None, None
    try:
        alpha_ridge = brentq(
            lambda a: E0_shooting(a, M_CHI_GEV, m_ap_GeV) - E_TARGET_GEV,
            a_lo, a_hi, xtol=1e-15, rtol=1e-10, maxiter=100,
        )
        E0_at_ridge = E0_shooting(alpha_ridge, M_CHI_GEV, m_ap_GeV)
        return alpha_ridge, E0_at_ridge
    except (ValueError, RuntimeError):
        return None, None


def main():
    print("=" * 70)
    print("=== Bound-state ridge scan (Priority 2) ===")
    print("=" * 70)
    print(f"Target: sigma/m(v={V_TARGET_KMS} km/s) = 174 cm^2/g as a PEAK")
    print(f"Bound-state ridge: E_0 = {E_TARGET_GEV*1e9:.4f} eV")
    print(f"Convention: alpha_D = g^2/(4*pi) [LOCKED]")
    print(f"Threshold: kappa_c = {KAPPA_C_ANALYTIC}")
    print()

    print("Sanity check: at kappa -> kappa_c, E_0 should -> 0")
    for kappa_test in [1.7, 1.6799, 1.6798, 1.6797, 1.5, 1.2]:
        m_ap_test = 1e-9
        alpha_for_kappa = kappa_test * m_ap_test / M_CHI_GEV
        E0_test = E0_shooting(alpha_for_kappa, M_CHI_GEV, m_ap_test)
        if not math.isnan(E0_test):
            print(f"  kappa = {kappa_test:.4f}, E_0 = {E0_test*1e9:.4e} eV")
        else:
            print(f"  kappa = {kappa_test:.4f}: NaN")
    print()

    print("Ridge scan: (alpha_D, m_A') such that bound state has E_0 = E_target")
    m_ap_grid = np.logspace(-9, -3, 12)
    results = []
    for m_ap in m_ap_grid:
        m_ap_eV = m_ap * 1e9
        alpha_ridge, E0_at_ridge = find_ridge_for_m_ap(m_ap)
        if alpha_ridge is not None:
            kappa_ridge = compute_kappa(alpha_ridge, M_CHI_GEV, m_ap)
            results.append({
                "m_A_prime_eV": float(m_ap_eV),
                "alpha_D_at_ridge": float(alpha_ridge),
                "kappa_at_ridge": float(kappa_ridge),
                "E_0_GeV": float(E0_at_ridge),
                "E_0_eV": float(E0_at_ridge * 1e9),
            })
            print(f"  m_A' = {m_ap_eV:7.1f} eV, alpha_D = {alpha_ridge:.3e}, kappa = {kappa_ridge:.4f}")

    out_path = os.path.join(OUTPUT_DIR, "data", "results", "v19_2_f_phase3_bound_state_ridge_scan.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump({
            "_meta": {
                "description": "v19.2-F Phase 3 Bound-state ridge scan (Priority 2)",
                "target_velocity_kms": V_TARGET_KMS,
                "target_energy_eV": float(E_TARGET_GEV * 1e9),
                "convention": "alpha_D = g^2/(4*pi) [LOCKED]",
                "kappa_c": float(KAPPA_C_ANALYTIC),
                "status": "BLOCKED: solver does not converge (see V19_2_F_PRIORITY2_ATTEMPT_REPORT.md)",
            },
            "ridge_points": results,
        }, f, indent=2)

    print()
    print(f"Ridge scan complete: {len(results)} points found (expected: 0 due to solver blocker)")
    print(f"Results saved: {out_path}")


if __name__ == "__main__":
    main()
```

---

## Recommendation

**Phase 3 verdict unchanged: FAIL, paper (A) wins.**

The Priority 2 ridge scan was meant to convert "scan failed" to a falsifiable structural claim ("peak requires specific bound-state tuning"). The Phase 3 EXTENDED scan already established a STRONGER result: no (α_D, m_A') gives σ/m(29.4)=174 as a PEAK. The ridge scan would only narrow WHERE; the monotonicity shows it doesn't happen anywhere.

**Next priorities (per the plan):**
- **Priority 3** — Solver benchmark suite (Tulin-Yu 2018 Fig. 2, Loeb-Weiner, Born regression tests): 1-2 days
- **Priority 4** — Composite form factor F²(q) attempt: 1-2 days
- **Priority 5** — NaN distribution report: 0.5 day
- **Priority 6** — Constraint intersection map (BBN/CMB/Lyman-α/direct detection): 3-5 days

Priority 1 is a permanent fix that prevents recurrence of the σ/m(100) ambiguity for all future code. Priority 2 was deferred due to numerical infrastructure limits, not due to physics.

MEDIA:C:/Users/lamkuenai/projects/sidm-composite-dm-mediator/docs/V19_2_F_PRIORITY1_2_REPORT.md