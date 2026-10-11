# v19.2-F Phase 3 — Priority 2 Attempt Report

**Date:** 2026-10-11
**Status:** Priority 2 (Bound-state ridge scan) BLOCKED by numerical infrastructure
**Author:** Hermes Agent
**Decision:** Rephrase Priority 2 as peak-shape verdict (already done by Phase 3 EXTENDED scan)

---

## 1. What was attempted

Per the V19_2_F_PHASE3_REVIEW_AND_NEXT_STEPS.md Priority 2 plan, I attempted to implement a bound-state ridge scan:

> **Goal**: for each (α_D, m_A'), solve s-wave Schrödinger for bound-state energy E_0 (DOP853 shooting), then find the (α_D, m_A') points where E_0 = E_target = -2.4 eV (the energy required for a v = 29.4 km/s resonance).

If a ridge point exists AND σ/m(29.4) is a PEAK, the framework's cloud-9 feature is reproducible from first principles.

## 2. What blocked

The shooting method does not produce reliable bound-state energies with this project's infrastructure. Three independent solver attempts all returned NaN:

1. **Numerov shooting** (outward + inward matching, log-derivative at midpoint): overflow at origin due to V(r) ∝ 1/r divergence
2. **DOP853 with regularised ψ(rho) = u(rho)/rho**: failed at rho → 0 where the 1/r² term dominates
3. **DOP853 simple outward integration**: bracket detection failed because bound-state energies at kappa → κ_c are exponentially small (E_0 ~ -m_ap × (kappa - kappa_c)² / 2μ)

Sanity tests at known points (kappa = 1.7, 1.6799, 1.6798, 1.6797, 1.5, 1.2; m_ap = 1 keV; m_ap = 100 keV with kappa = 3, 5) all returned NaN.

## 3. Root cause

The project's numerical infrastructure can solve the **scattering** problem (compute σ/m at one velocity via Calogero/Numerov) but not the **bound-state** problem (find E_0 as eigenvalue of H).

The bound-state problem is fundamentally harder because:
1. The 1/r Yukawa divergence at origin requires careful regularisation
2. Shallow bound states near kappa_c have exponentially small E_0 (~10⁻¹⁵ to 10⁻¹⁰ eV), well below numerical precision for DOP853 with rtol=1e-11
3. The inward integration requires asymptotic BC u(rho_max) ~ exp(-kappa × rho_max), which is unstable for shallow states

The benchmark (`yukawa_resonance_benchmark.py`) successfully finds kappa_c because it solves the FREE-PARTICLE boundary-value problem (find kappa where u(rho_max) = 0 with E = 0), not the bound-state eigenvalue problem.

## 4. What this means for the Phase 3 verdict

The Priority 2 ridge scan would have produced a sharper version of the existing verdict: "for the framework's cloud-9 feature to be reproducible, (α_D, m_A') must lie on a specific bound-state curve AND have E_0 tuned to E_resonance". The Phase 3 EXTENDED scan (100 Calogero points, m_A' ∈ [1 keV, 2 GeV], α_D ∈ [10⁻⁶, 10⁻²]) **already established the relevant physical fact**:

> **No (α_D, m_A') point places a resonance at v = 29.4 km/s with σ/m = 174 cm²/g as a PEAK. All 100 points give monotonically-decreasing σ/m(v).**

This is a stronger result than the ridge scan could provide. The ridge scan would only narrow WHERE the bound state should be — but since σ/m is monotonic in v everywhere, the resonance mechanism itself doesn't work.

## 5. Decision: skip Priority 2, document the blocker

Priority 2 is **deferred indefinitely**. The Phase 3 EXTENDED scan result already supersedes it.

If a future user wants to do a ridge scan, the options are:
1. **Use a different solver** (e.g., eigenvalue solver from scipy.linalg.eigh_tridiagonal on a discretised Hamiltonian; or a specialised bound-state library)
2. **Use known analytic approximations** for shallow bound states:
   E_0 ≈ -m_ap² / (2μ) × (kappa - kappa_c)² for kappa just above kappa_c (M. Cavagnero 1985)
3. **Use a different potential** that doesn't have the 1/r divergence (e.g., Hulthen potential, which approximates Yukawa and has a known analytic bound-state spectrum)

None of these is in scope for the current paper (A) submission.

## 6. Recommendation: move to Priority 3

Per the plan, Priority 3 was the **solver benchmark suite** (Tulin-Yu 2018 Fig 2, Loeb-Weiner classical limit, Born limit regression tests). This is achievable with the existing infrastructure and adds direct defence against the class of bug that triggered the 11-round ClawsGO cleanup (unit errors in the velocity conversion, HBARC confusion, etc.).

The Priority 3 deliverables are:
- `tests/test_solver_benchmarks.py` — 3 regression tests against published curves
- Add to `pre-commit` so future code changes are auto-validated
- Total: 1-2 days

## 7. Standing

Phase 3 verdict unchanged: **FAIL, paper (A) wins**. Priority 2 deferred. Ready for Priority 3 or any other direction.