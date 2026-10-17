# v40.8 — Code review: v19_2_f_priority1_resonance_helpers.py (Loop 5)

**Date:** 2026-10-17
**Branch:** `wip/v19.2-F-init`
**Tag:** `v19.2-F-Phase3-CLOSED-r40.8` (pending)

---

## TL;DR

Reviewed `v0.3-prelim/code/v19_2_f_priority1_resonance_helpers.py` (105 lines), the Breit-Wigner resonance σ/m helper used by all v40+ scripts (v40.1 rebaseline, v40.2 finegrid, Loop 1, Loop 2, Loop 4). The file is **functionally correct** but has a few code-quality issues:

1. **Convention violation**: line 24 uses `sys.path.insert(0, ...)`, which the v31 review explicitly replaced with `importlib.util.spec_from_file_location`. All other v40+ scripts follow the v31 convention; this file is the exception.
2. **Unused variable**: line 50 defines `GEVSQ_TO_CM2 = HBAR_C_GEV_CM**2` but it's never used (line 60 uses `HBAR_C_GEV_CM**2` directly).
3. **Misleading comment**: line 42 says "May return NaN if v is too small for the Born approximation" — but the function never returns NaN from the Born integral (which is well-defined for v=0). The NaN return is only triggered if `sigma_m` ends up negative or non-finite, which would be a bug elsewhere.
4. **Unused import path**: `_PROJECT_ROOT` is computed but only used for the sys.path.insert.

The physics implementation (Breit-Wigner form factor, Born limit, unit conversions) is **correct** based on my verification.

---

## File reviewed

`v0.3-prelim/code/v19_2_f_priority1_resonance_helpers.py` (105 lines, 3.6 KB).

Functions:
- `F_resonance_sq(q, m_rho, Gamma_rho)`: Breit-Wigner |F(q)|²
- `sigma_m_resonance(v_kms, alpha_D, m_rho_GeV, Gamma_rho_GeV, m_chi_GeV)`: σ/m with resonance
- `velocity_at_resonance(m_rho_GeV, m_chi_GeV)`: v at resonance peak
- `detect_peak_at_target(sigma_v, v_grid, v_target, rtol)`: peak detection

---

## Issue 1 (MEDIUM): sys.path.insert violates v31 convention

**Location:** lines 22-24

```python
_THIS_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _THIS_DIR.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))
```

The v31 review (REVIEWER-33, item 5) explicitly replaced `sys.path.insert` with `importlib.util.spec_from_file_location` for both `constants` and the helper. All other v40+ scripts (`v19_2_f_lyman_alpha_post_v40_1_rebaseline.py`, `v40_2_finegrid.py`, Loop 1's M3 script) follow this convention. This helper file is the exception.

**Fix:** replace with:
```python
import importlib.util
spec = importlib.util.spec_from_file_location("constants", _PROJECT_ROOT / "constants.py")
constants = importlib.util.module_from_spec(spec)
spec.loader.exec_module(constants)
```

This is a code-cleanliness fix, not a correctness issue. The function still works.

## Issue 2 (LOW): Unused variable

**Location:** line 50

```python
GEVSQ_TO_CM2 = HBAR_C_GEV_CM ** 2  # <-- unused
```

Line 60 uses `HBAR_C_GEV_CM**2` directly:
```python
sigma_T0_cm2 = sigma_T0_GeV2 * HBAR_C_GEV_CM**2
```

So `GEVSQ_TO_CM2` is defined but never referenced. Should be removed (or `sigma_T0_cm2` should use `GEVSQ_TO_CM2` for clarity).

## Issue 3 (MEDIUM): Misleading docstring on sigma_m_resonance

**Location:** lines 41-43

```python
"""sigma/m(v) for Yukawa-like scattering with a dark-rho resonance propagator.

Returns:
    sigma/m in cm^2/g. May return NaN if v is too small for the Born approximation.
"""
```

The claim "May return NaN if v is too small for the Born approximation" is incorrect. The Born integral (lines 54-58) is well-defined for v=0:
- At v=0, q=0, q_squared=0, integrand = (1-cosθ)/m_rho^4, integral = 2/m_rho^4
- sigma_T0_GeV2 = 2π α_D² × 2/m_rho^4 — finite for any α_D, m_rho

The function returns NaN only if `sigma_m` ends up negative or non-finite, which would indicate a bug elsewhere (or extremely unusual parameters). The "v too small" explanation is misleading.

**Fix:** change the docstring to:
```python
"""sigma/m(v) for Yukawa-like scattering with a dark-rho resonance propagator.

Returns:
    sigma/m in cm^2/g. Returns NaN if the result is non-finite or negative
    (which would indicate a numerical issue, not a v-dependence).
"""
```

## Issue 4 (LOW): Unused _PROJECT_ROOT

**Location:** line 23

`_PROJECT_ROOT` is computed but only used for the `sys.path.insert`. If we apply Issue 1's fix (replace sys.path with importlib), this variable becomes unused. Either remove or keep with a comment.

## Issue 5 (POSITIVE): Physics implementation is correct

The Breit-Wigner form factor and Born limit are implemented correctly:

**F_resonance_sq** (lines 29-34): `1 / [(q² - m_rho²)² + (m_rho × Gamma_rho)²]` — standard Breit-Wigner propagator squared. Correct.

**sigma_m_resonance** (lines 37-73):
- Born baseline via numerical quadrature of `∫_-1^1 (1-cosθ)/(q²+m_rho²)² dcosθ` (line 54-58) — correct
- Unit conversion: GeV² → cm² via (ℏc)², M_chi_GeV → M_chi_g via atomic mass unit (line 60-62) — correct
- Resonance factor: (q²+m_rho²)² / [(q²-m_rho²)² + (m_rho×Gamma_rho)²] (line 65-67) — correct (this is the ratio of resonance-propagator to Born-propagator, magnitude squared)

**velocity_at_resonance** (lines 76-79): `C_KMS × m_rho / μ_red` — correct (solves q² = m_rho² for v_rel).

**detect_peak_at_target** (lines 82-105): peak detection logic — correct in concept, with the REVIEWER-17 floating-point fix (uses `np.isclose` instead of `==`).

## Issue 6 (POSITIVE): No numerical issues found

I ran the σ/m function at the canonical parameters (α_D=5.55e-6, m_rho=0.05e-3 GeV, m_chi=1.0 GeV) at v ∈ {0.1, 1, 3.7, 5.1, 8, 10.6, 29.4, 100, 1000} km/s and Γ/ρ ∈ {1, 5, 10, 20}. The function returns finite, positive values throughout. No NaN, no negative, no overflow. The σ/m values match the v40.1/v40.2 reference values within numerical precision.

## Recommendation

**Apply the 3 fixes (Issues 1, 2, 3).** They are code-quality fixes, not correctness fixes. The function is correct as-is. If applied, the file would be cleaner and more consistent with the v31 convention.

**Suggested diff:**

```python
# Issue 1 fix: replace sys.path with importlib
import importlib.util
spec = importlib.util.spec_from_file_location("constants", _PROJECT_ROOT / "constants.py")
_constants = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_constants)
M_CHI_GEV = _constants.M_CHI_GEV
# etc.
```

```python
# Issue 2 fix: remove unused variable or use it
# Either:
#   sigma_T0_cm2 = sigma_T0_GeV2 * GEVSQ_TO_CM2  # use the named constant
# Or:
#   # remove the GEVSQ_TO_CM2 = ... line entirely
```

```python
# Issue 3 fix: update docstring
"""sigma/m(v) for Yukawa-like scattering with a dark-rho resonance propagator.

Returns:
    sigma/m in cm^2/g. Returns NaN if the result is non-finite or negative
    (which would indicate a numerical issue, not a v-dependence).
"""
```

---

## Files

- **This doc:** `docs/V19_2_F_LOOP5_CODE_REVIEW.md`
- **Reviewed file:** `v0.3-prelim/code/v19_2_f_priority1_resonance_helpers.py` (no changes applied; review only)

---

## Honest limitations

1. **No code changes were applied** to the helper file. The review identified 3 code-quality issues but the function is correct as-is. Applying the fixes is a separate, low-priority cleanup task.
2. **The review is single-pass** — I read the file and verified the physics. I did not run the full test suite against the helper (the project has 32/32 tests passing, which exercises the helper indirectly).
3. **Other v40+ scripts** (v40.1 rebaseline, v40.2 finegrid, Loop 1 M3 script) have not been individually reviewed. A full code audit would include them.
4. **Performance** of `sigma_m_resonance` is not reviewed. The numerical quadrature (line 58) may be slow if called many times. The v40.1 script does 200 × 8 = 1600 calls, which is fine.
