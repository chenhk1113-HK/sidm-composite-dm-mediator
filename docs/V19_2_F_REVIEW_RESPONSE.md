# Reviewer Response — `revV19_2_F.docx` Audit

**Date:** 2026-10-11
**Reviewer:** (anonymous Chinese-language reviewer)
**Subject:** V19_2_F_PRIORITY1_2_REPORT.md
**Status:** Reply to each of 9 reviewer points

---

## Summary

The reviewer's audit contains 2 substantive corrections (κ_c citation, logical gap on EXTENDED-vs-ridge), 1 physics correction (Sommerfeld NOT missing — it IS in the Calogero solver), 1 actionable suggestion (try lattice diagonalisation), and 5 minor corrections. This response addresses each in detail.

| # | Reviewer claim | My response |
|---|---|---|
| §1 | "EXTENDED scan supersedes ridge scan" is a logical gap | **VALID** — will weaken claim in updated doc |
| §2 | κ_c = 1.6798 cited as "Bethe-Fano/Simonov" | **VALID** — will fix to "Tulin-Yu 2013" or "Simonov 1964" |
| §3 | E_target = -2.4 eV needs velocity-range context | **VALID** — will add note |
| §4 | Cavagnero 1985 shallow bound state formula needs full citation | **VALID** — was used as reference only, not as code |
| §5 | Missing standard solvers (imaginary-time, lattice diagonalisation) | **VALID** — will attempt lattice diagonalisation (Priority 2.5) |
| §6 | **Sommerfeld enhancement missing from scan** | **INCORRECT** — Calogero IS the Sommerfeld-resummed solution |
| §7 | "Cloud-9" not defined | **VALID** — internal jargon, will define |
| §8 | "Born domain" vs κ > κ_c comparison | **VALID** — will clarify wording |
| §9 | Dimensional mixing in E0_shooting | **VALID** — but only relevant if solver worked |

---

## §1 — Logical gap on EXTENDED vs ridge scan (VALID)

**Reviewer:** The grid scan and the ridge scan answer different questions. Grid monotonicity does not logically imply ridge monotonicity because:
1. Ridge may pass through inter-grid regions
2. σ/m monotonicity depends on (coupling, mass) jointly; Sommerfeld enhancement may produce non-monotonic behaviour in some parameter regions
3. Even if grid points are all monotonic, ridge points correspond to non-perturbative strong-coupling regimes that perturbative extrapolation cannot predict

**My response:** VALID. The claim "EXTENDED scan supersedes ridge scan" was too strong. The accurate statement is:

> The Phase 3 EXTENDED scan found no peak anywhere in the explored grid (100 points). While this does not rigorously prove the absence of a peak on the bound-state ridge (which would require a continuous scan or a finer grid at the ridge), it strongly suggests that any peak would lie outside the explored parameter range. The ridge scan would narrow WHERE the peak might be, but does not change the FACT that no peak was found anywhere in the grid.

**Action:** Update V19_2_F_PRIORITY1_2_REPORT.md § "What the Phase 3 EXTENDED scan already established" with this weakened statement.

---

## §2 — κ_c citation (VALID)

**Reviewer:** "Bethe-Fano/Simonov" is not the standard reference. The 1.6798 value comes from Tamm (1947), Sommerfeld (1948), or Tulin-Yu 2013 [arXiv:1306.5010].

**My response:** VALID. The "Bethe-Fano/Simonov" attribution was incorrect. The standard references for the s-wave bound-state threshold of the Yukawa potential V(r) = -(α/r)e^{-mr} with α = g²/(4π) are:

- **Simonov, Yu. A. (1964)** — original analytic treatment of Yukawa bound states
- **Tamm, I. (1947); Sommerfeld, A. (1948)** — earlier analytic work
- **Tulin, Yu, Zurek (2013), arXiv:1306.5010** — modern review with explicit threshold calculation

**Action:** Update `constants.py` docstring to cite Tulin-Yu 2013 and Simonov 1964.

---

## §3 — E_target = -2.4 eV (PARTIALLY VALID)

**Reviewer:** The numerical calculation is correct (μ = 0.5 GeV, v = 9.806e-5 c, E = 2.404 eV), but the project should acknowledge that 29.4 km/s is dwarf-galaxy scale and σ/m(v) needs to be examined across the full velocity range.

**My response:** PARTIALLY VALID. The E_target value is correct. The velocity-scale context is a fair point but is already addressed in the Phase 3 doc (which examines σ/m over [5, 1000] km/s). The ridge scan would only target a single v_target, which is by design.

**Action:** Add note in V19_2_F_PRIORITY2_ATTEMPT_REPORT.md that E_target corresponds to dwarf-galaxy scale and the wider velocity range is examined in Phase 3.

---

## §4 — Cavagnero 1985 citation (MINOR)

**Reviewer:** Full citation needed for the shallow-bound-state formula E_0 ≈ -m_A'²/(2μ) × (κ - κ_c)².

**My response:** VALID. This was a reference for future work (the solver was never implemented), not for code. Full citation is: M. Cavagnero, "Variational and perturbation theory of anharmonic oscillators and the Yukawa potential", Phys. Rev. A 31, 2542 (1985). Coefficient C in front is O(1); exact value depends on Yukawa convention.

**Action:** Document full citation in V19_2_F_PRIORITY2_ATTEMPT_REPORT.md.

---

## §5 — Missing standard solvers (PARTIALLY VALID)

**Reviewer:** Imaginary-time evolution and lattice diagonalisation are standard bound-state methods that were not attempted.

**My response:** PARTIALLY VALID. The imaginary-time evolution method is indeed standard for quantum mechanics textbooks. The lattice diagonalisation (scipy.linalg.eigh_tridiagonal) is the most robust approach for this problem.

**Action:** Add lattice diagonalisation attempt to a new Priority 2.5 (small). Pseudo-code:
1. Discretise r ∈ [0, 200/m_A'] on N=2000 points
2. Construct Hamiltonian matrix: H_ij = -δ_ij/(2μ h²) + δ_i,j+1/(2μ h²) + V(r_i) δ_ij
3. Find smallest eigenvalue of H using scipy.linalg.eigh_tridiagonal
4. Compare against κ_c = 1.68 to validate
5. Use as bound-state E_0 solver for ridge scan

**Status:** To be done as part of Priority 2.5 if user requests.

---

## §6 — Sommerfeld enhancement missing (INCORRECT)

**Reviewer:** "文档的 Phase 3 scan 使用的是树图级 Yukawa 散射振幅，没有包含 Sommerfeld 重求和"

**My response:** INCORRECT. The Phase 3 EXTENDED scan uses the **Calogero variable-phase partial-wave solver** (see `clawsgo_phase3_check.py:37-61`), which solves the full Schrödinger equation for the Yukawa potential and sums partial waves up to `l_max = ceil(4k/m_φ) + 6`. This IS the Sommerfeld-resummed result. It is NOT tree-level perturbation theory.

The Calogero solver computes:
```
sigma_T_partialwave(alpha, m_phi, v):
    # Solve coupled ODEs for phase shifts delta_l(r)
    # Return sigma_T = (4 pi / k^2) * sum_l (2l+1) sin²(delta_l)
```

This is exactly the partial-wave sum that captures Sommerfeld enhancement implicitly (each partial wave accounts for multiple scatterings via the full Yukawa wavefunction).

The reviewer's confusion may stem from my Priority 2 doc using the term "tree-level" in places. This was inaccurate; the Phase 3 EXTENDED scan uses the FULL partial-wave solver, which is more sophisticated than tree-level.

**Action:** Update V19_2_F_PRIORITY1_2_REPORT.md to explicitly state that the Phase 3 EXTENDED scan uses Calogero (full partial-wave) NOT Born/tree-level. The framework point (κ = 3.4) DOES fall outside Born's domain (which is why t40 Born gives σ/m(29.4) = 0.354 cm²/g, not 174), but the EXTENDED scan goes BEYOND Born via Calogero at every (α_D, m_A') grid point.

**Net verdict:** §6 is the most consequential reviewer point and it is INCORRECT. The Sommerfeld enhancement IS in the scan. The framework's point itself cannot be evaluated by Calogero (returns NaN at l_max=400 due to deep-Sommerfeld overflow), but EVERY OTHER grid point (100 points total) IS evaluated with the full partial-wave sum.

---

## §7 — "Cloud-9" undefined (MINOR)

**Reviewer:** "Cloud-9" is internal jargon; should be defined or replaced.

**My response:** VALID. Cloud-9 refers to the σ/m = 174 cm²/g peak at v = 29.4 km/s — the feature that the Phase 3 scan was testing. It is named after the "Cloud-9" dwarf galaxy halo from Cloud-9 project.

**Action:** Define cloud-9 in V19_2_F_PRIORITY1_2_REPORT.md first use.

---

## §8 — "Born domain" wording (MINOR)

**Reviewer:** "κ = 3.4 > κ_c = 1.68" does not directly imply "Born approximation fails". Born validity is α_D ≪ 1, not κ ≪ κ_c.

**My response:** VALID. The wording in V19_2_F_PRIORITY2_ATTEMPT_REPORT.md should be clarified. The two conditions are:
- **Born valid:** α_D ≪ 1 (weak coupling, perturbative regime)
- **Bound state exists:** κ = α_D m_χ/m_A' > κ_c

Framework has α_D = 6.8e-7 ≪ 1 (Born SHOULD be valid) BUT κ = 3.4 > 1.68 (bound state exists). These two regimes can BOTH be true if the potential is short-range enough: Born treats the Yukawa as a small correction, while the bound-state formation depends on the depth/range ratio.

For framework's specific case: Born formula gives σ/m(29.4) = 0.354 (t40, factor 492× below target), but the true value would be larger due to Sommerfeld/partial-wave effects. The Calogono calculator returns NaN here (l_max overflow), so we cannot get the framework's exact σ/m(29.4) from the project's solvers.

**Action:** Update wording in V19_2_F_PRIORITY2_ATTEMPT_REPORT.md to clarify the Born vs bound-state regimes are independent criteria.

---

## §9 — Dimensional mixing in E0_shooting (MINOR)

**Reviewer:** ρ_arr is dimensionless but r_arr converts back to GeV. Physical readability could be improved.

**My response:** VALID but minor. The code uses GeV throughout (rho_arr = dimensionless, r_arr = GeV, V_arr = GeV units in GeV-scaled Schrödinger). Numerically consistent. Could be made more readable by explicit rho = m_Ap' * r substitution.

**Action:** Add comment to clarify units in E0_shooting function (if it is ever used; currently NaN).

---

## Net verdict of the reviewer audit

The reviewer's audit contains:
- **2 valid corrections** (§1 logical gap, §2 κ_c citation)
- **1 incorrect major claim** (§6 Sommerfeld missing — actually IS in Calogero)
- **5 minor valid items** (§3, §4, §5, §7, §8, §9)

**Most consequential correction:** §1 (logical gap on EXTENDED vs ridge scan). The claim was too strong and will be weakened.

**Most consequential reviewer error:** §6 (Sommerfeld missing). The reviewer conflated "Born formula breaks down at κ > κ_c" with "scan doesn't include Sommerfeld". These are different. The Calogero solver IS the Sommerfeld-resummed partial-wave sum. The framework's point (κ = 3.4) is outside Calogero's reach (NaN at l_max=400), but all other 99 grid points are evaluated correctly with full partial waves.

**Recommended actions:**
1. Update §1 wording in V19_2_F_PRIORITY1_2_REPORT.md (weaken EXTENDED supersedes ridge claim)
2. Update κ_c citation to Tulin-Yu 2013 / Simonov 1964
3. Add explicit note that Phase 3 EXTENDED scan uses Calogero (full partial-wave), not tree-level
4. Define "cloud-9" on first use
5. Add note about Born vs bound-state regime distinction

These are documentation changes only; no code changes required. The Phase 3 verdict (FAIL, paper A) is unchanged.

Standing by for user direction.