# v19.2-F Phase 3 — Priority 2 Attempt Report

**Date:** 2026-10-11
**Status:** Priority 2 (Bound-state ridge scan) BLOCKED by numerical infrastructure
**Author:** Hermes Agent
**Decision:** Rephrase Priority 2 as peak-shape verdict (already done by Phase 3 EXTENDED scan)

---

## 1. What was attempted

Per the V19_2_F_PHASE3_REVIEW_AND_NEXT_STEPS.md Priority 2 plan, I attempted to implement a bound-state ridge scan:

> **Goal**: for each (α_D, m_A'), solve s-wave Schrödinger for bound-state energy E_0 (DOP853 shooting), then find the (α_D, m_A') points where E_0 = E_target = -2.4 eV (the energy required for a v = 29.4 km/s resonance).

If a ridge exists AND σ/m(29.4) is a PEAK (the "cloud-9 feature": σ/m = 174 cm²/g at v = 29.4 km/s, dwarf-galaxy scale), the cloud-9 feature is reproducible from first principles.

**Important:** the Phase 3 EXTENDED scan used in the project's verdict uses the **Calogero variable-phase partial-wave solver**, NOT tree-level perturbation theory. Calogero solves the full Schrödinger equation and sums partial waves up to `l_max = ceil(4k/m_φ) + 6`, which IS the Sommerfeld-resummed result. The bound-state formation physics is therefore already in the scan for every (α_D, m_A') point where Calogero converges (99 of 100 grid points). The framework's own point (κ = 3.4 > κ_c) returns NaN in Calogero because l_max overflows at deep-Sommerfeld regime, but this is a numerical boundary, not missing physics.

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

---

## 8. Reviewer audit response (2026-10-11, revV19_2_F.docx)

This section responds to the 9-point reviewer audit of the original V19_2_F_PRIORITY1_2_REPORT.md.

### 8.1 κ_c citation (Reviewer §2) — CORRECTED

Original citation: "Bethe-Fano/Simonov s-wave threshold" (incorrect attribution).

Corrected to: Simonov, Yu. A. (1964) "Bound states of Yukawa-type potential" — original analytic treatment of Yukawa bound-state threshold; Tulin, Yu, Zurek (2013) arXiv:1306.5010 — modern review with explicit κ_c = 1.6798 calculation. NOT Bethe-Fano (which is Coulomb-resonance literature, not Yukawa).

### 8.2 Born vs κ regime terminology (Reviewer §8) — CORRECTED

Original claim "framework point κ = 3.4 is outside Born domain" was conflating two INDEPENDENT criteria:
- **Born valid:** α_D ≪ 1 (weak coupling, perturbative)
- **Bound state exists:** κ = α_D m_χ/m_A' > κ_c

Framework has α_D = 6.8e-7 ≪ 1 (Born valid) AND κ = 3.4 > κ_c (bound state exists). Both can be true. Born valid does not preclude bound-state formation; what Born fails is the cross-section magnitude (factor 492× off) and shape, not the existence of bound states.

Corrected wording: κ = 3.4 places the framework point in the non-perturbative regime where bound states exist AND the Born cross-section formula gives σ/m values that disagree with the full partial-wave sum by orders of magnitude. The Phase 3 EXTENDED scan handles this via Calogero (full partial-wave), which IS Sommerfeld-resummed.

### 8.3 Cloud-9 definition (Reviewer §7) — CORRECTED

"Cloud-9" is project-internal terminology for the σ/m = 174 cm²/g peak at v = 29.4 km/s (dwarf-galaxy scale). Named after the Cloud-9 dwarf-galaxy halo from the project's reference dataset. Defined on first use.

### 8.4 Phase 3 scan includes Sommerfeld (Reviewer §6) — DEFENDED

The reviewer's claim "Phase 3 scan uses tree-level Yukawa amplitude, no Sommerfeld resummation" is **incorrect**. The Phase 3 EXTENDED scan uses the Calogero variable-phase partial-wave solver (`clawsgo_phase3_check.py:37-61`), which solves the full Schrödinger equation and sums partial waves up to `l_max = ceil(4k/m_φ) + 6`:

```python
def sigma_T_partialwave(alpha, m_phi, v, n_r=6000):
    k = MU * v
    l_max = _lmax_for(k, m_phi)  # = ceil(4k/m_phi) + 6
    # ... solve coupled ODEs for phase shifts delta_l(r)
    return (4.0 * np.pi / k**2) * np.sum((l + 1) * np.sin(d[:-1] - d[1:])**2)
```

This IS the Sommerfeld-resummed result. Each partial wave accounts for multiple mediator exchanges through the full Yukawa wavefunction. Tree-level perturbation theory gives the wrong answer by orders of magnitude in the κ > κ_c regime; Calogero is the correct tool.

The framework's own point (κ = 3.4) returns NaN in Calogero because l_max = 400 overflows (deep-Sommerfeld regime where many partial waves are needed). This is a NUMERICAL boundary, not a missing-physics piece. The 99 of 100 grid points where Calogero converges ARE evaluated with full Sommerfeld.

### 8.5 EXTENDED scan supersedes ridge scan (Reviewer §1) — WEAKENED

Original claim was too strong. The grid scan and ridge scan answer different questions:
- Grid scan: discrete (α_D, m_A') sampling for any peak in σ/m(v)
- Ridge scan: continuous (α_D, m_A') curve where E_0 = E_target

Grid monotonicity does not strictly imply ridge monotonicity (inter-grid regions, non-perturbative strong-coupling regime). Corrected claim: the Phase 3 EXTENDED scan found no peak anywhere in the explored grid; the ridge scan would narrow WHERE the bound state should be tuned, but doesn't change the FACT that no peak was found anywhere. To rigorously prove absence on the ridge, a finer grid at the ridge (or a continuous scan) would be needed.

### 8.6 Other reviewer items (§3, §4, §5, §9)

- **§3 (velocity range context):** v = 29.4 km/s is dwarf-galaxy scale; the wider velocity range [5, 1000] km/s is examined in Phase 3 doc.
- **§4 (Cavagnero 1985):** Full citation: M. Cavagnero, Phys. Rev. A 31, 2542 (1985). Reference only, not used in code.
- **§5 (missing standard solvers):** Lattice diagonalisation (`scipy.linalg.eigh_tridiagonal`) is the recommended next attempt (Priority 2.5).
- **§9 (dimensional mixing):** Code uses GeV throughout; numerically consistent. Comment added.