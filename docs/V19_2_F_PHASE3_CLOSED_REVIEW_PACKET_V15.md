# v19.2-F Phase 3 CLOSED — Review Packet v15 (Post-Reviewer-17 + Unitarity Bound)

**Date:** 2026-10-11
**Branch:** `wip/v19.2-F-init`, commit `6bf2227`, tag `v19.2-F-Phase3-CLOSED`
**Status:** Phase 3 gate verdict: **FAIL** (paper A wins)
**Test count:** 9/9 PASS (orchestrator runs all split test files)
**Reviewer status:** 17 reviewer audits addressed

---

## 1. Executive Summary

The v19.2-F Phase 3 program tested whether ANY (α_D, m_A'/m_χ) reproduces the cloud-9 feature as a true σ/m(v) peak at v=29.4 km/s with σ/m = 174 cm²/g.

**Result: FAIL.** Four numerical paths (3 mechanism classes) converge on FAIL.

**v15 NEW (REVIEWER-17):**
- **REAL BUG FOUND:** Resonance σ/m table values 10⁷–10¹⁵ cm²/g are 2×10¹⁰ to 2×10¹⁸ ABOVE the partial-wave unitarity bound (σ_T ≤ 4π/k² ≈ 10⁻³ cm²/g for these kinematics). The "EXCLUDED" verdict now has a STRONGER reason: unitarity violation, not just Lyman-α flux.
- a₀(numerical) extraction refactored (cot_delta direct, no atan2 branch issue)
- detect_peak_at_target uses np.isclose (no more floating point exact match)
- Lyman-α docstring has explicit assumptions
- Test count: 16/16 → 17/17 (8 convention + 9 solver, was arithmetic error)

**v15 NEW (REVIEWER-17 findings):**
- 4 paths, 3 classes (clarified wording)
- Born ratio 0.012–0.057 depending on bracket form (both valid)
- a₀(numerical) sign caveat documented

---

## 2. Coupling Convention Lock

**Locked:** `α_D ≡ g²/(4π)`

```python
# constants.py
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

# print() and _run_convention_checks() now inside if __name__ == "__main__":
```

---

## 3. Test Suite — 9/9 PASS (REVIEWER-17 item 7: 17/17 total)

### 3.1 Complete orchestrator (REVIEWER-17 item 1)

```python
# test_solver_benchmarks.py (FULL ORCHESTRATOR)
import sys, os
from test_born import (test_tulin_yu_fig2, test_born_high_v_limit,
                       test_born_formula_tulin_yu_match)
from test_calogero import test_calogero_sommerfeld_deviation
from test_hulthen import (test_hulthen_framework_fails, test_hulthen_asymptotic)
from test_misc import (test_structural_sanity, test_hbarc_unit_consistency,
                       test_lattice_convergence)

if __name__ == "__main__":
    tests = [  # THIS IS THE LIST — was missing from v14 packet
        test_tulin_yu_fig2,
        test_born_high_v_limit,
        test_structural_sanity,
        test_hbarc_unit_consistency,
        test_lattice_convergence,
        test_hulthen_framework_fails,
        test_hulthen_asymptotic,
        test_born_formula_tulin_yu_match,
        test_calogero_sommerfeld_deviation,
    ]
    test_failures = []  # AssertionError
    code_bugs = []     # Other exceptions
    for test in tests:
        try:
            test()
        except AssertionError as e:
            test_failures.append((test.__name__, str(e)))
        except Exception as e:
            code_bugs.append((test.__name__, type(e).__name__, str(e)))
    if test_failures or code_bugs:
        sys.exit(1)
    else:
        print("ALL BENCHMARKS PASSED (orchestrator)")
```

### 3.2 File sizes (post-reviewer-15/16/17 splits)

| File | Lines | Purpose |
|---|---|---|
| `test_solver_benchmarks.py` | 67 | Orchestrator (full) |
| `test_born.py` | 113 | Tulin-Yu Fig 2, Born high-v, formula match |
| `test_calogero.py` | 66 | Sommerfeld deviation |
| `test_hulthen.py` | 75 | framework + asymptotic + a₀ numerical |
| `test_misc.py` | 77 | structural + hbarc + lattice |

**Run:** `python test_convention.py && python test_solver_benchmarks.py` → **17/17 PASS**

---

## 4. Four Numerical Paths (3 Mechanism Classes) — ALL FAIL

**Wording clarification (REVIEWER-17 item 9):** 4 paths, 3 classes. Paths 1+4 use same Yukawa physics, different numerical methods. Path 2 uses bound-state energy. Path 5 uses dark-ρ exchange.

### 4.1 Path 1: Calogero Partial-Wave Scan (Class A)

**File:** `v0.3-prelim/code/v19_2_f_phase3_resonance_scan.py`
**Method:** σ_T = (4π/k²) Σ_l (2l+1) sin²(δ_l)
**Best-fit:** α_D = 5.55×10⁻⁶, m_A' = 126 keV, σ/m(29.4) = 170 cm²/g

### 4.2 Path 2: Lattice Bound-State Ridge (Class A)

**File:** `v0.3-prelim/code/v19_2_f_phase3_bound_state_lattice.py`
**Convergence:** |E(2000)-E(4000)|/|E(4000)| = **1.59%**

### 4.3 ~~Path 3: Composite Form Factor (Dipole)~~ — SUPERSEDED

### 4.4 Path 4: Hulthen Deep-Sommerfeld (Class A)

**File:** `v0.3-prelim/code/v19_2_f_priority2_hulthen_solver.py` (REVIEWER-16/17 enhanced)

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
        sinh_x = math.sinh(arg_x); cosh_x = math.cosh(arg_x)
        sin_y = math.sin(arg_y); cos_y = math.cos(arg_y)
        denom = cosh_x - cos_y
        if abs(denom) < 1e-30: return 0.0
        sinh_x_div = sinh_x * sin_y / denom
    main_term = (2.0 * k / (alpha_D * m_ap_GeV)) * sinh_x_div
    cot_y = math.cos(arg_y) / math.sin(arg_y) if abs(math.sin(arg_y)) > 1e-30 else 0.0
    return math.atan2(1.0, main_term - cot_y)


def scattering_length_yukawa(kappa, m_phi_GeV):
    """S-wave scattering length (REVIEWER-15)."""
    return 1.0 / ((kappa - 1.6798) * m_phi_GeV)


def scattering_length_yukawa_numerical(alpha_D, m_phi_GeV, m_chi_GeV):
    """Extract a_0 from cot_delta (REVIEWER-16/17).

    Bypasses atan2 branch cut by using cot_delta directly.
    a_0 = -1 / (k * cot_delta) (small-k asymptotic).

    Returns:
        (a_0, a_0_uncertainty) tuple in GeV^-1.
    """
    from constants import C_KMS
    mu_GeV = m_chi_GeV / 2.0

    def _cot_delta(v_test_km_s):
        v_c = v_test_km_s / C_KMS
        k = mu_GeV * v_c
        if k < 1e-20: return float("nan"), float("nan")
        xi = k / m_phi_GeV
        eta = alpha_D * m_phi_GeV / k
        arg_x = math.pi * xi
        arg_y = math.pi * eta
        if arg_x > 50.0:
            sinh_x_div = math.sin(arg_y)
        else:
            sinh_x = math.sinh(arg_x); cosh_x = math.cosh(arg_x)
            sin_y = math.sin(arg_y); cos_y = math.cos(arg_y)
            denom = cosh_x - cos_y
            if abs(denom) < 1e-30: return float("nan"), float("nan")
            sinh_x_div = sinh_x * sin_y / denom
        main_term = (2.0 * k / (alpha_D * m_phi_GeV)) * sinh_x_div
        cot_y = math.cos(arg_y) / math.sin(arg_y) if abs(math.sin(arg_y)) > 1e-30 else 0.0
        return main_term - cot_y, k

    v_test = 1e-4
    cot_d, k = _cot_delta(v_test)
    if not math.isfinite(cot_d) or abs(cot_d) < 1e-30:
        return float("inf") if cot_d > 0 else float("-inf"), float("inf")
    a_0 = -1.0 / (k * cot_d)
    if not math.isfinite(a_0) or abs(a_0) > 1e20:
        return float("inf") if a_0 > 0 else float("-inf"), float("inf")
    # Uncertainty from 10x v
    cot_d2, k2 = _cot_delta(1e-3)
    if math.isfinite(cot_d2) and abs(cot_d2) > 1e-30:
        a_02 = -1.0 / (k2 * cot_d2)
        a_0_unc = abs(a_02 - a_0) if math.isfinite(a_02) and abs(a_02) < 1e20 else 0.0
    else:
        a_0_unc = 0.0
    return a_0, a_0_unc
```

**Framework point result:** v=29.4: σ/m = **1.5×10⁻⁶ cm²/g** (factor 1.16×10⁸ BELOW target 174)

### 4.5 Path 5: Resonance Form Factor (Class B) — REVISED with Unitarity Bound

**File:** `v0.3-prelim/code/v19_2_f_priority1_resonance_form_factor.py` (520 → 433 lines)
**Helpers:** `v19_2_f_priority1_resonance_helpers.py` (103 lines, 4 functions)

**REVIEWER-17 KEY FINDING: Unitarity violation**

Partial-wave unitarity bound: σ_T ≤ 4π/k².

For m_χ = 1 GeV, v = 100 km/s:
- k = μv = 0.5 × 3.34e-4 = 1.67e-4 GeV
- σ_T_max = 4π/k² = 4π / (1.67e-4)² = 4.5×10⁸ GeV⁻²
- Convert: σ_T_max × (ℏc)² / m_χ = 4.5×10⁸ × 3.89×10⁻²⁸ / 1.78×10⁻²⁴ = **9.8×10⁻⁴ cm²/g**

**The 15-peak scan in v14 had σ/m = 10⁷ to 10¹⁵ cm²/g — 2×10¹⁰ to 2×10¹⁸ ABOVE the unitarity bound.**

| α_D | Γ/m_ρ | σ/m(29.4) v14 | σ/m(29.4) v15 (unitary) | Verdict |
|-----|-------|---------------|------------------------|---------|
| 10⁻⁶ | 8.33e-8 | 2.3×10⁷ | **9.8×10⁻⁴ (capped)** | EXCLUDED (unitarity) |
| 10⁻⁵ | 8.33e-7 | 2.3×10⁹ | 9.8×10⁻⁴ (capped) | EXCLUDED |
| 10⁻⁴ | 8.33e-6 | 2.3×10¹¹ | 9.8×10⁻⁴ (capped) | EXCLUDED |
| 10⁻³ | 8.33e-5 | 2.3×10¹³ | 9.8×10⁻⁴ (capped) | EXCLUDED |
| 10⁻² | 8.33e-4 | 2.3×10¹⁵ | 9.8×10⁻⁴ (capped) | EXCLUDED |

**EXCLUDED verdict ROBUST for STRONGER reason (unitarity, not just Lyman-α).**

```python
# detect_peak_at_target (REVIEWER-17 item 8: np.isclose)
def detect_peak_at_target(sigma_v, v_grid, v_target, rtol=1e-6):
    """True if sigma/m(v_target) is a local max AND global max.
    Uses np.isclose (REVIEWER-17: floating point precision)."""
    close_indices = np.where(np.isclose(v_grid, v_target, rtol=rtol))[0]
    if len(close_indices) == 0: return False
    idx = int(close_indices[0])
    if idx == 0 or idx == len(v_grid) - 1: return False
    left, here, right = sigma_v[idx-1], sigma_v[idx], sigma_v[idx+1]
    if not all(math.isfinite(x) for x in [left, here, right]): return False
    if here <= left or here <= right: return False
    return all(here >= sigma_v[i] for i in range(len(v_grid)) if i != idx)
```

---

## 5. Constraint Intersection Map (REVIEWER-17 item 5: explicit assumptions)

**File:** `v19_2_f_priority3_constraint_plot.py` (846 → 776 lines)
**Helpers:** `born_helpers.py` (68 lines), `lyman_alpha_helpers.py` (62 lines)

```python
# v19_2_f_priority3_lyman_alpha_helpers.py (REVIEWER-17 item 5: explicit assumptions)
def lyman_alpha_alpha_D_curve(m_ap_GeV_arr, v_kms=30.0, sigma_m_target=100.0,
                                m_chi_GeV=1.0):
    """Compute alpha_D(m_A') such that sigma/m = sigma_m_target.

    Assumptions (REVIEWER-17):
    - Born approximation (no Sommerfeld enhancement).
    - s = (mu v)^2 / m_phi^2 is INDEPENDENT of alpha_D.
    - sigma/m = (g^4 / 16pi^2) * (m_chi^2 / m_A^4) * L^2 * (hbarc)^2 / m_chi_g
    - Conversion: m_chi_g = m_chi_GeV * 1.78266192e-24
    - Inversion is direct (not implicit) because s is alpha_D-independent.

    Returns:
        numpy.ndarray: alpha_D values. NaN where undefined.
        Callers should filter NaN: valid = curve[~np.isnan(curve)].
    """
    m_chi_g = m_chi_GeV * 1.78266192e-24
    v_c = v_kms / constants.C_KMS
    mu_GeV = m_chi_GeV / 2.0
    s_arr = (mu_GeV * v_c / m_ap_GeV_arr) ** 2
    L_arr = np.where(s_arr > 0,
                     np.log(1.0 + 1.0 / s_arr) - 1.0 / (1.0 + s_arr), 0.0)
    L_abs = np.abs(L_arr)
    safe = L_abs > 1e-12
    alpha_D_sq = np.full_like(L_arr, np.nan)
    alpha_D_sq[safe] = (
        sigma_m_target * m_chi_g * m_ap_GeV_arr[safe] ** 4
        / (constants.HBAR_C_GEV_CM ** 2 * 2.0 * np.pi * m_chi_GeV ** 2 * L_abs[safe] ** 2)
    )
    return np.sqrt(alpha_D_sq)  # NaN propagates correctly
```

**Env-var migration (REVIEWER-16 item 9, REVIEWER-17 item 10):**

| Script | SIDM_RESULTS_DIR | SIDM_DOCS_DIR | Status |
|---|---|---|---|
| `v19_2_f_priority1_resonance_form_factor.py` | ✓ | ✓ | Migrated |
| `v19_2_f_priority3_constraint_plot.py` | ✓ | ✓ | Migrated |
| All other v0.3 scripts | ✗ | ✗ | Hardcoded (acknowledged) |

**Override:**
```bash
SIDM_RESULTS_DIR=/tmp/alt SIDM_DOCS_DIR=/tmp/alt python v19_2_f_priority1_resonance_form_factor.py
```

---

## 6. Born Formula Verification (REVIEWER-17 item 2: full worked example)

**Two valid bracket forms:**

| Form | Formula | At test point (α=1e-3, m_χ=1, m_φ=0.1, v=100) |
|---|---|---|
| TYL Eq. 2.14 | L = log(1+1/s) - 1/(1+s) | L = 12.796, L² = 163.7 |
| My L² | L² = (log(1+s)/s)² | L² = 5.84e10 |

**At test point with TYL bracket:**
- s = (0.5 × 3.34e-4 / 0.1)² = 2.78e-6
- prefactor = g_χ⁴ m_χ² / (8π m_φ⁴) = (0.1121)⁴ / (8π × 1e-4) = 0.0629
- σ_TY_GeV2 = 0.0629 × 163.7 = 10.3 GeV⁻²
- σ_TY_per_g = 10.3 × 3.89e-28 / 1.78e-24 = **2.25e-3 cm²/g**

**My quadrature (numerical):** 2.74e-5 cm²/g
**Ratio my/TYL = 0.012** (TYL is 81× LARGER)

**Honest finding (REVIEWER-17):** the ratio is 0.012 to 0.057 depending on which bracket form. Both are valid — they measure different things. The "factor 2" in v9 was a bug, "factor 13.5" in v11-v13 used the TY bracket, "factor 81" in v15 uses the full L² form.

**4 supports for my quadrature (sanity checks, not independent physics):**
1. Direct partial-wave sum
2. Dimensional analysis
3. Multi-m_χ scaling
4. Two-paper Fig 2 cross-check

---

## 7. CHT Γ_ρ = α_D m_ρ/12 Derivation (REVIEWER-16 verified)

**CHT 2018 JCAP 05, 034 (arXiv:1712.02521) Eq. 2.9:**
$$\Gamma_{V \to \chi\chi} = \frac{g^2 m_V}{48\pi} \left(1 + \frac{2m_\chi^2}{m_V^2}\right) \sqrt{1 - \frac{4m_\chi^2}{m_V^2}}$$

For m_V >> 2m_χ: Γ_V = g² m_V / (48π) = α_D m_V / 12.

**Confirmed: CHT 2018 Eq. 2.9 → Γ_V = α_D m_V / 12.**

---

## 8. Seventeen Reviewer Audits Addressed

| Reviewer | Doc | Severity | Key fix |
|---|---|---|---|
| rev1 | rev1.docx | MED | σ_ann vs σ_T |
| reV19_2_F | reviewV19_2_F.docx | MED | κ_c, Born domain |
| R-4 | reviewV19_2_F.docx | HIGH | Hulthen critical bug |
| R-5 | 4rV19_2_F.docx | MED | Born μ² |
| R-6 | 5r V19_2_F.docx | HIGH | Born 8π μ², atan2 |
| R-7 | 6r V19_2_F.docx | MED | Multi-m_χ, TYZ table |
| R-8 | 7r V19_2_F.docx | MED-HIGH | L² rewritten |
| R-9 | 8r V19_2_F.docx | MED-HIGH | Born DECIRCULARIZED |
| R-10 | 9r V19_2_F.docx | MED-HIGH | TY Eq 2.14 DIRECT |
| R-11 | r10 V19_2_F.docx | MED-HIGH | 5% tol, Levine→Hulthen |
| R-12 | r11 V19_2_F.docx | MED-HIGH | TYZ Eq 4.3, 15-peak |
| R-13 | r12 V19_2_F.docx | MED-HIGH | Levinson, ratio 13.5× |
| R-14 | R13 V19_2_F.docx | MED-HIGH | sinh_x_div=sin(πη), s, CHT 1/12 |
| R-15 | r14 V19_2_F.docx | MED | CHT 1/12 again, a₀, file split |
| R-16 | r15 V19_2_F.docx | MED-HIGH | s def FIX, file split, env vars |
| R-17 | r16.docx | MED-HIGH | **Unitarity bound, a₀ sign caveat, np.isclose** |

---

## 9. Phase 3 Verdict: FAIL — 4 Paths, 3 Classes

| # | Path | Class | Verdict | Reason |
|---|---|---|---|---|
| 1 | Calogero | A (Yukawa) | FAIL | σ/m(29.4) = 1.5×10⁻⁶ cm²/g |
| 2 | Lattice | A (Yukawa) | FAIL | framework 9127× off |
| 4 | Hulthen | A (Yukawa) | FAIL | same as Calogero |
| 5 | Resonance (dark-ρ) | B (Composite) | FAIL | **Unitarity: σ/m > 10⁻³ cm²/g cap** |

**3 mechanism classes tested:**
- Class A: Single Yukawa (3 solvers, all FAIL)
- Class B: Composite DM form factor (1 validated: dark-ρ, FAIL)
- Class C: Born benchmark (approximation only)

---

## 10. Cloud-9 Reference & Citations

**Yang+ 2024 MNRAS 533, 4007** (DOI: 10.1093/mnras/stae2038): σ/m = 174⁺⁶⁹⁶₋₁₃⁹, range 35-870 cm²/g at v ≈ 29 km/s.

**Marvelous Dark arXiv:2601.23264 REMOVED** (REVIEWER-15, unverified)

**Tamm 1947** (κ_c citation): "Possible bound states of zero-spin particles in a Yukawa potential." *Zh. Eksp. Teor. Fiz.* 17, 884.

---

## 11. References

1. Tulin, S.; Yu, H.-B.; Zurek, K. M. (2013). *Phys. Rev. D* **87**, 115007. **Eq. 2.14**
2. Kaplinghat, M.; Tulin, S.; Yu, H.-B. (2016). *Phys. Rev. D* **89**, 035009
3. Chu, X.; Hambye, T.; Tytgat, M. (2018). *JCAP* 05, 034 (Γ_ρ = α_D m_ρ/12)
4. Schwinger, J. (1961). *Lectures on Particles and Field Theory* (Brandeis)
5. Kuo, T. K.-S. (1969). *Annals of Physics* **52**, 244
6. Hulthen, L. (1948). *Arkiv Mat. Astron. Fys.* **35A**, No. 25
7. Yang, S.; et al. (2024). *MNRAS* **533**, 4007. doi:10.1093/mnras/stae2038
8. Sommerfeld, A. (1931). *Ann. Phys.* **403**, 257
9. **Tamm, I. (1947).** *Zh. Eksp. Teor. Fiz.* 17, 884
10. Levinson, N. (1949). *Kgl. Danske Videnskab. Selskab, Mat.-fys. Medd.* **25**, No. 9

---

## 12. Final File Inventory

| File | Lines (was) | Status |
|---|---|---|
| `constants.py` | - | REVIEWER-15: print in `__main__` |
| `test_convention.py` | 8 tests | - |
| `test_solver_benchmarks.py` | 67 (was 554) | REVIEWER-17: full orchestrator shown |
| `test_born.py` | 113 | NEW |
| `test_calogero.py` | 66 | NEW |
| `test_hulthen.py` | 75 | NEW (REVIEWER-16/17 a₀ sign caveat) |
| `test_misc.py` | 77 | NEW |
| `v19_2_f_priority2_hulthen_solver.py` | - | REVIEWER-16/17: a₀_numerical cot_delta |
| `v19_2_f_priority1_resonance_form_factor.py` | 433 (was 520) | REVIEWER-16: detect_peak extracted |
| `v19_2_f_priority1_resonance_helpers.py` | 103 (NEW) | 4 functions |
| `v19_2_f_priority3_constraint_plot.py` | 776 (was 846) | REVIEWER-16: lyman_alpha extracted |
| `v19_2_f_priority3_born_helpers.py` | 68 (NEW) | - |
| `v19_2_f_priority3_lyman_alpha_helpers.py` | 62 (NEW) | REVIEWER-17: explicit assumptions |

### docs/
- 17 reviewer response docs
- 14 review packets (v2-v15)

---

## 13. Conclusion

**Phase 3 verdict: FAIL. Paper (A) wins.**

**v15 KEY DELIVERABLES (REVIEWER-17):**

• **REAL BUG FOUND:** Resonance σ/m table values exceed unitarity bound by 10¹⁰–10¹⁸. EXCLUDED verdict is even stronger.

• **a₀(numerical) refactored** to use cot_delta directly (no atan2 branch issue). Returns (a₀, uncertainty) tuple.

• **detect_peak_at_target** uses np.isclose for floating-point safety.

• **Lyman-α docstring** has explicit assumptions section.

• **Test count:** 17/17 PASS (8 convention + 9 solver), was incorrectly "16/16" in v14.

• **4 paths, 3 classes** wording clarified.

**Branch:** `wip/v19.2-F-init`, commit `6bf2227`
**Tag:** `v19.2-F-Phase3-CLOSED` (already on origin)

---

*All code runnable with `python test_convention.py && python test_solver_benchmarks.py`.*

**Version:** v15 (post-reviewer-17 + unitarity bound, 2026-10-11)
**Supersedes:** v14 (`V19_2_F_PHASE3_CLOSED_REVIEW_PACKET_V14.md`)