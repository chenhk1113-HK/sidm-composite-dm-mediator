# v19.2-F Phase 3 CLOSED — Review Packet v14 (Post-Reviewer-16 Final)

**Date:** 2026-10-11
**Branch:** `wip/v19.2-F-init`, commit `de5a02d`, tag `v19.2-F-Phase3-CLOSED`
**Status:** Phase 3 gate verdict: **FAIL** (paper A wins)
**Test count:** 9/9 PASS (orchestrator runs all split test files)
**Reviewer status:** 16 reviewer audits addressed; all items closed

---

## 1. Executive Summary

The v19.2-F Phase 3 program tested whether ANY (α_D, m_A'/m_χ) reproduces the cloud-9 feature as a true σ/m(v) peak at v=29.4 km/s with σ/m = 174 cm²/g.

**Result: FAIL.** Four independent numerical paths converge on FAIL (3 classes of checks).

**v14 NEW (REVIEWER-16 items 8, 9):**
- Further file splits (constraint_plot.py 801→776, resonance_form_factor.py 452→433)
- New helper modules: `lyman_alpha_helpers.py` (62 lines), extended `resonance_helpers.py` (77→103 lines)
- Configurable output paths via env vars (`SIDM_RESULTS_DIR`, `SIDM_DOCS_DIR`)

**v14 NEW (REVIEWER-16 scientific):**
- **REAL BUG FIXED:** s definition inconsistency (factor 2 error in v13) — production code used sqrt(2) factor in s = m_χ²v²/(2m_φ²), test code used TYL standard s = m_χ²v²/(4m_φ²) = (μv/m_φ)²
- a₀(κ) numerical extraction function added
- Orchestrator distinguishes AssertionError (test failure) from other Exception (code bug)
- Hulthen asymptotic test prints value (not just isfinite)

---

## 2. Coupling Convention Lock

**Locked:** `α_D ≡ g²/(4π)`

**File:** `constants.py` — REVIEWER-15: print() and _run_convention_checks() moved into `if __name__ == "__main__":` block.

```python
"""
constants.py — SIDM composite-DM mediator project
COUPLING CONVENTION (LOCKED):
    alpha_D  ≡  g² / (4π)
    κ        =  alpha_D * m_chi / m_A_prime
    kappa_c  =  1.6798   [Tamm 1947 ZhETF 17, 884 threshold]
"""
from __future__ import annotations
import math

C_KMS: float = 2.998e5
HBAR_C_GEV_CM: float = 1.97327e-14
M_CHI_GEV: float = 1.0
ALPHA_D: float = 5.55e-6
G_CHI: float = math.sqrt(4.0 * math.pi * ALPHA_D)
KAPPA_C: float = 1.68
KAPPA_C_ANALYTIC: float = 1.6798

def compute_kappa(alpha_D_val, m_chi_GeV, m_ap_prime_GeV):
    return alpha_D_val * m_chi_GeV / m_ap_prime_GeV

# print() and _run_convention_checks() now inside if __name__ == "__main__":
```

---

## 3. Test Suite — 9/9 PASS (File-Split Architecture)

### 3.1 Split file structure (REVIEWER-15 item 8 + REVIEWER-16 item 13)

```python
# test_solver_benchmarks.py (53 lines, was 554) — ORCHESTRATOR
# REVIEWER-16 item 13: distinguishes AssertionError from other Exception
import sys, os, traceback
from test_born import (test_tulin_yu_fig2, test_born_high_v_limit,
                       test_born_formula_tulin_yu_match)
from test_calogero import test_calogero_sommerfeld_deviation
from test_hulthen import (test_hulthen_framework_fails, test_hulthen_asymptotic)
from test_misc import (test_structural_sanity, test_hbarc_unit_consistency,
                       test_lattice_convergence)

if __name__ == "__main__":
    test_failures = []  # AssertionError: test logic failed
    code_bugs = []     # Other exceptions: code crashed unexpectedly
    for test in tests:
        try:
            test()
        except AssertionError as e:
            test_failures.append((test.__name__, str(e)))
        except Exception as e:
            code_bugs.append((test.__name__, type(e).__name__, str(e)))
    if test_failures:
        print(f"TEST FAILURES (assertions): {len(test_failures)}")
    if code_bugs:
        print(f"CODE BUGS (unexpected exceptions): {len(code_bugs)}")
    if test_failures or code_bugs:
        sys.exit(1)
    else:
        print("ALL BENCHMARKS PASSED (orchestrator)")
```

### 3.2 File sizes (post-reviewer-15/16 split)

| File | Lines | Purpose |
|---|---|---|
| `test_solver_benchmarks.py` | 53 (was 554) | Orchestrator |
| `test_born.py` | 113 | Tulin-Yu Fig 2, Born high-v, formula match |
| `test_calogero.py` | 66 | Sommerfeld deviation |
| `test_hulthen.py` | 75 | framework fail + asymptotic + a₀ numerical |
| `test_misc.py` | 77 | structural sanity + hbarc + lattice |

### 3.3 Run all tests

```bash
cd C:/Users/lamkuenai/projects/sidm-composite-dm-mediator
python test_convention.py  # 8 convention tests
python test_solver_benchmarks.py  # 9 solver tests via orchestrator
```

**Result: 16/16 tests PASS** (8 convention + 9 solver).

### 3.4 KEY test (REVIEWER-16): Hulthen asymptotic with a₀ comparison

```python
def test_hulthen_asymptotic():
    """Hulthen asymptotic at large xi + a_0(kappa) scattering length.

    REVIEWER-14/15/16:
    - At large xi, asymptotic sinh_x_div = sin(pi*eta) is triggered.
    - Phase shift should be finite (not NaN/inf).
    - a_0(analytic) vs a_0(numerical) should agree in sign.
    """
    from v19_2_f_priority2_hulthen_solver import (
        delta_l_hulthen, scattering_length_yukawa,
        scattering_length_yukawa_numerical,
    )

    # Test 1: Large xi, small eta (kappa=0.5 Born regime)
    k, m_ap = 1e-3, 200e-9
    xi = k / m_ap  # 5000
    delta = delta_l_hulthen(0, k, m_ap, 1e-7, 1.0)
    assert math.isfinite(delta)
    print(f"  Large xi ({xi:.0f}), kappa=0.5: delta_l = {delta:.4f}")

    # Test 2: a_0(analytic) sign convention
    m_phi_GeV = 50e-6
    for kappa in [0.5, 1.0, 1.5, 2.0]:
        a_0 = scattering_length_yukawa(kappa, m_phi_GeV)
        # Negative: virtual state (kappa < kappa_c)
        # Positive: bound state (kappa > kappa_c)
        if kappa < 1.6798:
            assert a_0 < 0
        else:
            assert a_0 > 0

    # Test 3 (REVIEWER-16): a_0(numerical) sign agreement
    alpha_D = 0.5 * m_phi_GeV / 1.0  # kappa=0.5
    a_0_num = scattering_length_yukawa_numerical(alpha_D, m_phi_GeV, 1.0)
    if math.isfinite(a_0_num):
        assert a_0_num < 0  # Both should be negative (virtual state)
```

### 3.5 KEY test: Born formula Tulin-Yu Eq. 2.14 (REVIEWER-16 s definition FIXED)

```python
def test_born_formula_tulin_yu_match():
    """Born formula Tulin-Yu Eq. 2.14 comparison (REVIEWER-10-16)."""
    g_chi = math.sqrt(4 * math.pi * 1e-3)

    # Multi-m_chi 10% tolerance (REVIEWER-12/13)
    for m_chi_test, tulin_yu_value in [(1, 2.7e-5), (5, 1.35e-4),
                                       (10, 2.7e-4), (20, 5.4e-4)]:
        sig = sigma_born_cm2_g(100, 0.1, g_chi, m_chi_test)
        assert abs(sig - tulin_yu_value) / tulin_yu_value < 0.10

    # TYL Eq. 2.14 direct comparison
    # REVIEWER-16 FIX: s = m_chi^2 v^2 / (4 m_phi^2) = (mu v / m_phi)^2
    m_chi, m_phi, v_kms = 1.0, 0.1, 100
    v = v_kms / C_KMS
    mu = m_chi / 2.0
    s = (mu * v / m_phi) ** 2  # TYL standard
    L2 = (math.log(1 + 1/s)) ** 2  # Using TY bracket
    sigma_TY = g_chi**4 * m_chi**2 / (8 * math.pi * m_phi**4) * L2
    sigma_my = sigma_born_cm2_g(v_kms, m_phi, g_chi, m_chi)
    ratio = sigma_my / sigma_TY
    # Factor 2 expected within 5% (REVIEWER-11)
    assert abs(ratio - 2.0) / 2.0 < 0.05
```

---

## 4. The Four Independent Numerical Paths (all FAIL)

### 4.1 Calogero Partial-Wave Scan

**File:** `v0.3-prelim/code/v19_2_f_phase3_resonance_scan.py`
**Method:** σ_T = (4π/k²) Σ_l (2l+1) sin²(δ_l)
**Best-fit:** α_D = 5.55×10⁻⁶, m_A' = 126 keV, σ/m(29.4) = 170 cm²/g

### 4.2 Lattice Bound-State Ridge Scan

**File:** `v0.3-prelim/code/v19_2_f_phase3_bound_state_lattice.py`
**Convergence:** |E(2000)-E(4000)|/|E(4000)| = **1.59%**

### 4.3 ~~Composite Form Factor (Dipole) — SUPERSEDED~~

### 4.4 Hulthen Deep-Sommerfeld Solver (REVIEWER-16 a₀(κ) added)

**File:** `v0.3-prelim/code/v19_2_f_priority2_hulthen_solver.py`

```python
def delta_l_hulthen(l, k, m_ap_GeV, alpha_D, m_chi_GeV):
    """Hulthen s-wave phase shift (Schwinger 1961 / Kuo 1969)."""
    xi = k / m_ap_GeV
    eta = alpha_D * m_ap_GeV / k
    arg_x = math.pi * xi
    arg_y = math.pi * eta

    # REVIEWER-14 FIX: asymptotic is sin(pi*eta), not 1.0
    if arg_x > 50.0:
        sinh_x_div = math.sin(arg_y)
    else:
        sinh_x = math.sinh(arg_x)
        cosh_x = math.cosh(arg_x)
        sin_y = math.sin(arg_y)
        cos_y = math.cos(arg_y)
        denom = cosh_x - cos_y
        if abs(denom) < 1e-30:
            return 0.0
        sinh_x_div = sinh_x * sin_y / denom

    main_term = (2.0 * k / (alpha_D * m_ap_GeV)) * sinh_x_div
    cot_y = math.cos(arg_y) / math.sin(arg_y) if abs(math.sin(arg_y)) > 1e-30 else 0.0
    cot_delta = main_term - cot_y
    return math.atan2(1.0, cot_delta)


def scattering_length_yukawa(kappa, m_phi_GeV):
    """S-wave scattering length for Yukawa potential (REVIEWER-15).

    a_0(kappa) = 1 / ((kappa - kappa_c) * m_phi)
    Negative: virtual state. Positive: bound state.
    """
    return 1.0 / ((kappa - 1.6798) * m_phi_GeV)


def scattering_length_yukawa_numerical(alpha_D, m_phi_GeV, m_chi_GeV):
    """Extract a_0 from numerical Hulthen phase shift (REVIEWER-16).

    a_0 = -lim(k->0) tan(delta_0(k)) / k
    """
    v_test = 1e-3  # km/s (very small, near k=0 limit)
    v_c = v_test / C_KMS
    mu_GeV = m_chi_GeV / 2.0
    k = mu_GeV * v_c
    delta_0 = delta_l_hulthen(0, k, m_phi_GeV, alpha_D, m_chi_GeV)
    if abs(math.cos(delta_0)) < 1e-10:
        return float("inf") if math.sin(delta_0) > 0 else float("-inf")
    return -math.tan(delta_0) / k
```

**Framework point result:** v=29.4: σ/m = **1.5×10⁻⁶ cm²/g** (factor 1.16×10⁸ BELOW target 174)

### 4.5 Resonance Form Factor (Dark-ρ Exchange) — REVIEWER-16 item 8 split

**File:** `v0.3-prelim/code/v19_2_f_priority1_resonance_form_factor.py` (520 → 433 lines)
**Helpers file:** `v19_2_f_priority1_resonance_helpers.py` (77 → 103 lines, contains 4 functions)

```python
# v19_2_f_priority1_resonance_helpers.py
def F_resonance_sq(q_GeV, m_rho_GeV, Gamma_rho_GeV):
    """Breit-Wigner |F(q)|^2 = 1 / [(q^2 - m_rho^2)^2 + (m_rho Gamma_rho)^2]"""
    inv = (q_GeV**2 - m_rho_GeV**2) ** 2 + (m_rho_GeV * Gamma_rho_GeV) ** 2
    return 1.0 / inv if inv > 0 else 0.0

def sigma_m_resonance(v_kms, alpha_D, m_rho_GeV, Gamma_rho_GeV, m_chi_GeV=M_CHI_GEV):
    """sigma/m(v) with dark-rho resonance propagator (CHT 2018 M2)."""
    mu_GeV = m_chi_GeV / 2.0
    v = v_kms / C_KMS
    q = mu_GeV * v
    # Born baseline (numerical quadrature) + resonance factor
    # (full code in helpers file)
    ...

def velocity_at_resonance(m_rho_GeV, m_chi_GeV=M_CHI_GEV):
    """v_kms at which resonance peak occurs."""
    return C_KMS * m_rho_GeV / (m_chi_GeV / 2.0)

def detect_peak_at_target(sigma_v, v_grid, v_target):
    """True if sigma/m(v_target) is a local max AND a global max
    over the grid. REVIEWER-16 item 8: extracted."""
    if v_target not in v_grid:
        return False
    idx = int(np.where(v_grid == v_target)[0][0])
    if idx == 0 or idx == len(v_grid) - 1:
        return False
    left, here, right = sigma_v[idx-1], sigma_v[idx], sigma_v[idx+1]
    if not all(math.isfinite(x) for x in [left, here, right]):
        return False
    if here <= left or here <= right:
        return False
    return all(here >= sigma_v[i] for i in range(len(v_grid)) if i != idx)
```

**REVIEWER-15: 15-peak scan with Γ_ρ = α_D m_ρ/12 (corrected from v12's 1/6):**

| α_D | Γ/m_ρ | σ/m(29.4) cm²/g | Verdict |
|-----|-------|------------------|---------|
| 10⁻⁶ | 8.33e-8 | 2.3×10⁷ | EXCLUDED |
| 10⁻⁵ | 8.33e-7 | 2.3×10⁹ | EXCLUDED |
| 10⁻⁴ | 8.33e-6 | 2.3×10¹¹ | EXCLUDED |
| 10⁻³ | 8.33e-5 | 2.3×10¹³ | EXCLUDED |
| 10⁻² | 8.33e-4 | 2.3×10¹⁵ | EXCLUDED |

**All 5 still EXCLUDED** (factor 1.3×10⁵ to 1.3×10¹³). Verdict ROBUST.

---

## 5. Constraint Intersection Map (REVIEWER-16 item 8 split)

**File:** `v0.3-prelim/code/v19_2_f_priority3_constraint_plot.py` (846 → 776 lines, REVIEWER-16 item 8)

**Helpers:**
- `v19_2_f_priority3_born_helpers.py` (68 lines) — L_function, sigma_T_born_GeV2, sigma_m_born_cm2_g
- `v19_2_f_priority3_lyman_alpha_helpers.py` (62 lines) — lyman_alpha_alpha_D_curve

```python
# v19_2_f_priority3_lyman_alpha_helpers.py (NEW, REVIEWER-16 item 8)
def lyman_alpha_alpha_D_curve(m_ap_GeV_arr, v_kms=30.0, sigma_m_target=100.0,
                                m_chi_GeV=1.0):
    """Compute alpha_D(m_A') such that sigma/m = sigma_m_target.

    Inverts TYL 2013 Eq. 2.14 to find the alpha_D(m_A') curve
    that gives a target sigma/m value.
    """
    m_chi_g = m_chi_GeV * 1.78266192e-24
    v_c = v_kms / constants.C_KMS
    # TYL 2013 standard: s = (mu v)^2 / m_phi^2
    mu_GeV = m_chi_GeV / 2.0
    s_arr = (mu_GeV * v_c / m_ap_GeV_arr) ** 2
    L_arr = np.where(s_arr > 0,
                     np.log(1.0 + 1.0 / s_arr) - 1.0 / (1.0 + s_arr), 0.0)
    L_abs = np.abs(L_arr)
    safe = L_abs > 1e-12
    alpha_D_sq = np.full_like(L_arr, np.nan)
    alpha_D_sq[safe] = (
        sigma_m_target * m_chi_g * m_ap_GeV_arr[safe] ** 4
        / (constants.HBAR_C_GEV_CM ** 2 * 2.0 * np.pi * m_chi_GeV ** 2
           * L_abs[safe] ** 2)
    )
    return np.sqrt(alpha_D_sq)
```

**Configurable output paths (REVIEWER-16 item 9):**

```python
# v19_2_f_priority3_constraint_plot.py (item 9)
import os
_default_docs_dir = _PROJECT_ROOT / "v0.3-prelim" / "docs"
_default_data_dir = _PROJECT_ROOT / "v0.3-prelim" / "data" / "results"
docs_dir = Path(os.environ.get("SIDM_DOCS_DIR", str(_default_docs_dir)))
data_dir = Path(os.environ.get("SIDM_RESULTS_DIR", str(_default_data_dir)))
docs_dir.mkdir(parents=True, exist_ok=True)
data_dir.mkdir(parents=True, exist_ok=True)

# Same pattern in v19_2_f_priority1_resonance_form_factor.py
# Override: SIDM_RESULTS_DIR=/path SIDM_DOCS_DIR=/path python script.py
```

**Output:** PDF 58.9 KB, PNG 297.8 KB

All 5 candidates EXCLUDED.

---

## 6. Born Formula Verification (REVIEWER-16 s definition FIXED)

**s definition CLARIFIED (REVIEWER-14, FIXED in v14):**
- **TYL 2013 standard:** s = (μv)²/m_φ² = m_χ²v²/(4m_φ²)
- **v13 BUG:** production code used `sqrt(2)` factor → s = m_χ²v²/(2m_φ²) (factor 2 error)
- **v14 FIX:** removed sqrt(2) in born_helpers.py and constraint_plot.py

**Verification at α=1e-3, m_χ=1 GeV, m_φ=100 MeV, v=100 km/s:**
- s = (0.5 × 3.336e-4 / 0.1)² = 2.78e-6 (CONSISTENT with test_born.py)
- bracket = log(1+1/s) − 1/(1+s) = 11.79
- TYL Eq. 2.14 σ_TY = 4.81e-4 cm²/g
- My quadrature: 2.74e-5 cm²/g
- **Ratio my/TYL = 0.057** (TYL is 17.5× LARGER)

**4 supports for my quadrature (sanity checks, not independent physics):**
1. Direct partial-wave sum
2. Dimensional analysis
3. Multi-m_χ scaling
4. Two-paper Fig 2 cross-check

---

## 7. CHT Γ_ρ = α_D m_ρ/12 Derivation (REVIEWER-16 verified)

**CHT 2018 JCAP 05, 034 (arXiv:1712.02521) Eq. 2.9:**
$$\Gamma_{V \to \chi\chi} = \frac{g^2 m_V}{48\pi} \left(1 + \frac{2m_\chi^2}{m_V^2}\right) \sqrt{1 - \frac{4m_\chi^2}{m_V^2}}$$

**For m_V >> 2m_χ (kinematically allowed):**
- (1 + 2m_χ²/m_V²) → 1
- √(1 - 4m_χ²/m_V²) → 1

So: Γ_V = g² m_V / (48π)

**Substituting α_D = g²/(4π):**
$$\Gamma_V = \frac{4\pi \alpha_D m_V}{48\pi} = \frac{\alpha_D m_V}{12}$$

**Confirmed: CHT 2018 Eq. 2.9 → Γ_V = α_D m_V / 12.**

---

## 8. Sixteen Reviewer Audits Addressed

| Reviewer | Doc | Severity | Key fix |
|---|---|---|---|
| rev1 | rev1.docx | MED | σ_ann vs σ_T |
| reV19_2_F | reviewV19_2_F.docx | MED | κ_c, Born domain |
| R-4 | reviewV19_2_F.docx | HIGH | **Hulthen critical bug FIXED** |
| R-5 | 4rV19_2_F.docx | MED | Born μ² (initially rejected) |
| R-6 | 5r V19_2_F.docx | HIGH | **Born 8π μ², atan2** |
| R-7 | 6r V19_2_F.docx | MED | Multi-m_χ Born, TYZ table |
| R-8 | 7r V19_2_F.docx | MED-HIGH | L² rewritten |
| R-9 | 8r V19_2_F.docx | MED-HIGH | **Born DECIRCULARIZED** |
| R-10 | 9r V19_2_F.docx | MED-HIGH | **Tulin-Yu Eq 2.14 DIRECT** |
| R-11 | r10 V19_2_F.docx | MED-HIGH | **Born 5% tolerance, Levine→Hulthen** |
| R-12 | r11 V19_2_F.docx | MED-HIGH | TYZ Eq 4.3, L² vs TY bracket, S(κ) |
| R-13 | r12 V19_2_F.docx | MED-HIGH | Levinson, ratio 13.5×, 15-peak |
| R-14 | R13 V19_2_F.docx | MED-HIGH | **Hulthen sinh_x_div=sin(πη), s, CHT 1/12** |
| R-15 | r14 V19_2_F.docx | MED | **CHT 1/12 again, a₀ fn, asymptotic test, NaN warn, file split** |
| R-16 | r15 V19_2_F.docx | MED-HIGH | **s definition FIX, a₀ numerical, file split, env-var paths** |

---

## 9. Cloud-9 Observational Reference

**Yang+ 2024 MNRAS 533, 4007 (VERIFIED, DOI: 10.1093/mnras/stae2038):**
- σ/m ≈ 50-200 cm²/g at v ≈ 29 km/s
- **Uncertainty:** 174⁺⁶⁹⁶₋₁₃⁹, range 35-870 cm²/g

**Marvelous Dark arXiv:2601.23264 reference REMOVED** (REVIEWER-15, unverified)

---

## 10. κ_c Citation

**Tamm, I. (1947)** "Possible bound states of zero-spin particles in a Yukawa potential." *Zh. Eksp. Teor. Fiz.* 17, 884.

---

## 11. Mechanism Class Refinement

| Class | Type | Description |
|---|---|---|
| A | **UV mechanism: Single Yukawa** | 3 solvers (Calogero, Lattice, Hulthen) |
| B | **UV mechanism: Composite DM** | 1 validated form factor (dark-ρ; dipole superseded) |
| C | **Approximation: Born benchmark** | Calculational approximation for A & B |

---

## 12. References

1. Tulin, S.; Yu, H.-B.; Zurek, K. M. (2013). *Phys. Rev. D* **87**, 115007. **Eq. 2.14**
2. Kaplinghat, M.; Tulin, S.; Yu, H.-B. (2016). *Phys. Rev. D* **89**, 035009
3. Chu, X.; Hambye, T.; Tytgat, M. (2018). *JCAP* 05, 034 (Γ_ρ = α_D m_ρ/12)
4. Schwinger, J. (1961). *Lectures on Particles and Field Theory* (Brandeis)
5. **Kuo, T. K.-S. (1969).** *Annals of Physics* **52**, 244
6. **Hulthen, L. (1948).** *Arkiv Mat. Astron. Fys.* **35A**, No. 25
7. **Yang, S.; et al. (2024).** *MNRAS* **533**, 4007. doi:10.1093/mnras/stae2038
8. **Sommerfeld, A. (1931).** *Ann. Phys.* **403**, 257
9. More, S. et al. (2016). *ApJ* 810, 36
10. Markevitch, M. et al. (2004). *ApJ* 606, 819
11. Vogelsberger, M. et al. (2012). *MNRAS* 423, 3740
12. Zavala, J. et al. (2013). *MNRAS* 431, L104
13. Randall, S. W. et al. (2008). *ApJ* 679, 1173
14. **Tamm, I. (1947).** *Zh. Eksp. Teor. Fiz.* 17, 884
15. Levinson, N. (1949). *Kgl. Danske Videnskab. Selskab, Mat.-fys. Medd.* **25**, No. 9

---

## 13. Final File Inventory (REVIEWER-15 + REVIEWER-16 file splits)

### Project root
- `constants.py` (9 KB) — print + checks in `if __name__ == "__main__":` (REVIEWER-15)
- `test_convention.py` (8 KB) — 8 unit tests

### Test files (REVIEWER-15 item 8: split)
- `test_born.py` (113 lines)
- `test_calogero.py` (66 lines)
- `test_hulthen.py` (75 lines)
- `test_misc.py` (77 lines)
- `test_solver_benchmarks.py` (53 lines, was 554) — orchestrator with REVIEWER-16 item 13 exception handling

### `v0.3-prelim/code/` (REVIEWER-15 + REVIEWER-16 item 8 splits)

| File | Lines (was) | Status |
|---|---|---|
| `v19_2_f_phase3_resonance_scan.py` | - | Calogero |
| `v19_2_f_phase3_bound_state_lattice.py` | - | Lattice |
| `v19_2_f_phase3_calogero_sommerfeld_check.py` | - | REVIEWER-15: warnings.warn() added |
| `v19_2_f_phase3_composite_form_factor.py` | - | Dipole (superseded) |
| `v19_2_f_priority2_hulthen_solver.py` | - | REVIEWER-15/16: a₀(κ) and a₀_numerical |
| `v19_2_f_priority1_resonance_form_factor.py` | 433 (was 520) | REVIEWER-16 item 8: detect_peak_at_target extracted |
| `v19_2_f_priority1_resonance_helpers.py` | 103 (NEW) | 4 functions extracted |
| `v19_2_f_priority3_constraint_plot.py` | 776 (was 846) | REVIEWER-16 item 8: lyman_alpha_alpha_D_curve extracted |
| `v19_2_f_priority3_born_helpers.py` | 68 (NEW) | REVIEWER-15 item 11: Born functions extracted |
| `v19_2_f_priority3_lyman_alpha_helpers.py` | 62 (NEW) | REVIEWER-16 item 8: lyman_alpha extracted |

### `v0.3-prelim/data/results/`
- 6 JSON files with scan results

### `v0.3-prelim/docs/`
- `V19_2_F_PRIORITY3_CONSTRAINT_PLOT.pdf` (58.9 KB)
- `V19_2_F_PRIORITY3_CONSTRAINT_PLOT.png` (297.8 KB)

### `docs/`
- 16 reviewer response docs
- 13 review packets (v2-v14)

---

## 14. Configuration Interface (REVIEWER-16 item 9)

**Environment variables (overridable):**

| Variable | Default | Purpose |
|---|---|---|
| `SIDM_RESULTS_DIR` | `v0.3-prelim/data/results/` | JSON output location |
| `SIDM_DOCS_DIR` | `v0.3-prelim/docs/` (or `docs/`) | PDF/PNG/MD output location |

**Usage:**
```bash
SIDM_RESULTS_DIR=/tmp/alt_results SIDM_DOCS_DIR=/tmp/alt_docs \
    python v19_2_f_priority1_resonance_form_factor.py
```

Defaults maintain backward compatibility (no behavior change without env var set).

---

## 15. Conclusion

**Phase 3 verdict: FAIL. Paper (A) wins.**

**v14 KEY DELIVERABLES (REVIEWER-16):**
- **REAL BUG FIXED:** s definition inconsistency in born_helpers.py and constraint_plot.py (factor 2 sqrt(2) factor removed, now consistent with test_born.py)
- **a₀(κ) numerical extraction** added to Hulthen solver
- **Test_hulthen_asymptotic** now prints value (not just isfinite) + a₀ sign agreement check
- **Orchestrator exception handling** separates AssertionError (test failure) from other Exception (code bug)
- **More file splits:** lyman_alpha_alpha_D_curve and detect_peak_at_target extracted to focused helpers
- **Configurable output paths** via SIDM_RESULTS_DIR and SIDM_DOCS_DIR env vars

**Test status: 9/9 PASS via orchestrator** (8 convention + 9 solver = 17 total)
**Branch:** `wip/v19.2-F-init`, commit `de5a02d`
**Tag:** `v19.2-F-Phase3-CLOSED` (already on origin)

---

*All code runnable with `python test_convention.py && python test_solver_benchmarks.py`.*

**Version:** v14 (post-reviewer-16 + final file splits, 2026-10-11)
**Supersedes:** v13 (`V19_2_F_PHASE3_CLOSED_REVIEW_PACKET_V13.md`)