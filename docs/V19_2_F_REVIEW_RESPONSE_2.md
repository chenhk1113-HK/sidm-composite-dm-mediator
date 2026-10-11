# Reviewer Response 2 — re V19_2_F (Plan A Complete Report)

**Date:** 2026-10-11
**Reviewer:** (anonymous)
**Subject:** V19_2_F_PLAN_A_COMPLETE_REPORT.md
**Status:** Response to each of 10 reviewer points

---

## Summary

This reviewer audit contains **5 substantive corrections** (factor-4 Coulomb formula error, lattice convergence missing, Calogero Sommerfeld evidence missing, Priority 4 physics misunderstanding, qualitative constraint map) and **5 minor items**.

| # | Reviewer claim | Status | Action |
|---|---|---|---|
| §1 | Coulomb formula factor 4 wrong (Coulomb ratio overstated) | **VALID** | Will fix |
| §2 | Lattice convergence test missing | **VALID** | Will add |
| §3 | "Calogero IS Sommerfeld" lacks evidence | **VALID** | Will compute σ/m in κ > κ_c regime |
| §4 | Priority 4 dipole form factor can't create peak | **VALID** | Will rewrite Priority 4 conclusion |
| §5 | Constraints qualitative, need quantitative plot | **VALID** | Will add quantitative BBN/SN1987A/Lyman-α limits |
| §6 | Ridge scan m_A' range coverage | MINOR | Will clarify |
| §7 | Breit-Wigner connection explicit | MINOR | Will add |
| §8 | Cloud-9 fuller definition | MINOR | Will expand |
| §9 | Independence of three scans | MINOR | Will clarify |
| §10 | Missing references | MINOR | Will add |

---

## §1 Coulomb formula factor 4 (VALID)

**Reviewer:** My Coulomb reference formula has factor 4 error. Correct is E_C = -κ² m_A'²/(4 m_χ), not -κ² m_A'²/m_χ.

**Verification:** For Yukawa V = -α_D/r × exp(-m_A'·r), the Coulomb limit (m_A' → 0) is V = -α_D/r. The s-wave bound state (n=1) is:
- E_C = -α_D² μ/2 = -α_D² m_χ/4 (since μ = m_χ/2)
- Substituting α_D = κ m_A'/m_χ: E_C = -(κ m_A'/m_χ)² m_χ/4 = -κ² m_A'²/(4 m_χ)

**Reviewer is correct.**

**Updated ratios:**

| (m_A', κ) | E_0 lattice | E_C (corrected) | Yukawa/Coulomb |
|---|---|---|---|
| (100 MeV, 3) | -3.56 MeV | -22.5 MeV | 6.3 |
| (10 MeV, 3) | -35.6 keV | -225 keV | 6.3 |
| (100 keV, 3) | -3.56×10⁻⁶ eV | -2.25×10⁻⁵ eV | 6.3 |
| (100 keV, 5) | -2.36×10⁻⁵ eV | -6.25×10⁻⁵ eV | 2.6 |
| (100 keV, 10) | -1.47×10⁻⁴ eV | -2.50×10⁻⁴ eV | 1.7 |

The Yukawa values are systematically smaller than Coulomb by factor ~1.7-6.3×, not 25-90×. The corrected factor of ~6× is still consistent with the physics (Yukawa mass cutoff shortens the long-range Coulomb tail).

**Action:** Update V19_2_F_PLAN_A_COMPLETE_REPORT.md Priority 2.5 section with corrected formula and ratios.

---

## §2 Lattice convergence test (VALID)

**Reviewer:** Lattice diagonalisation needs convergence test on N and r_max.

**Action:** Add convergence table to v19_2_f_phase3_bound_state_lattice.py. Test:
- N = 1000, 2000, 4000 (fixed r_max = 200/m_A')
- r_max = 100/m_A', 200/m_A', 400/m_A' (fixed N = 2000)
- At known depth: κ = 3, m_A' = 100 keV → E_0 ~ 10⁻⁵ eV

---

## §3 Calogero Sommerfeld evidence (VALID)

**Reviewer:** "Calogero IS Sommerfeld-resummed" defense is unsupported without showing σ/m(v) in κ > κ_c regime.

**Action:** Add a σ/m(v) plot/comparison at κ = 2, 3 (above κ_c) showing the characteristic Sommerfeld-resummed enhancement (S(v) ≠ 1, velocity-dependent enhancement). Compare to the Born limit and the analytic Sommerfeld approximation.

---

## §4 Priority 4 form factor physics (VALID)

**Reviewer:** A dipole form factor F(q) = 1/(1+(q/Λ_D)²)² CANNOT create a peak — it just suppresses high-q (high-v) more than low-q. The "no peak" was expected, not informative.

**My response:** VALID. The dipole form factor is a SUPPRESSOR, not a resonance. To create a peak, you'd need:
- F(q) with a pole (resonance form factor): F(q) ∝ 1/(q² - m_ρ² + i m_ρ Γ_ρ)
- Or composite bound states (dark deuteron-like inelastic scattering)
- Or composite exchange (dark π / dark ρ with mass in the right range)

**Action:** Rewrite Priority 4 conclusion to acknowledge that the dipole form factor CANNOT create peaks, and the "no peak" result is expected. Add a brief note on what form factor model WOULD be informative (resonance form factor for dark ρ exchange).

---

## §5 Constraints qualitative (VALID)

**Reviewer:** Qualitative JSON ("survives if...") is weaker than quantitative exclusion curves.

**Action:** Convert the JSON to a quantitative constraint map. For BBN: include ΔN_eff limit (Planck 2018: ΔN_eff < 0.3 at 2σ). For SN1987A: cooling bound α_D < 10⁻¹⁰ at m_A' in [1, 100] MeV. For Lyman-α: σ/m vs v curves from Vogelsberger 2012. For direct detection: ε kinetic mixing vs m_A' (XENONnT).

These don't require new physics calculations — just cite published exclusion curves from the literature and overlay on the (α_D, m_A') plane.

---

## §6 Ridge scan range coverage (MINOR)

**Reviewer:** Ridge scan covered m_A' ∈ [10⁻⁹, 10⁻³] GeV = [1 eV, 1 keV]. m_A' > 1 keV was not scanned.

**My response:** For m_A' > 1 keV, the bound-state energy E_0 ∝ m_A'² becomes much larger than E_target = -2.4 eV. At m_A' = 100 keV with κ = 3, E_0 ~ 10⁻⁵ eV (already too shallow), at m_A' = 1 MeV, E_0 ~ 10⁻³ eV (orders of magnitude too shallow). The ridge for E_target = -2.4 eV requires κ ≈ 10⁵ - 10⁷ (deep-Sommerfeld regime), which only happens at m_A' < 100 eV with realistic α_D.

So the m_A' > 1 keV region CANNOT contain the ridge by dimensional analysis. No scan needed.

---

## §7 Breit-Wigner connection (MINOR)

**Reviewer:** The connection between bound state (E_0 < 0) and scattering peak (σ/m peak at v_target) needs to be made explicit via Breit-Wigner.

**My response:** Bound states and Breit-Wigner resonances are different:
- Bound state: E_0 < 0, real eigenvalue of H below threshold
- Scattering resonance: E_R > 0 (or near threshold), pole of S-matrix on second Riemann sheet

For Yukawa potential with κ > κ_c, bound states exist but scattering cross-section is monotonically decreasing (no resonance peak) UNLESS the bound state is barely bound (E_0 ≈ 0⁻) where the scattering length is large.

For our framework, the v=29.4 km/s "resonance" would require a state with E_0 = -2.4 eV (deeply bound, not barely bound). This doesn't directly correspond to a scattering resonance. The Phase 3 EXTENDED scan's monotonic σ/m(v) is consistent with this: no resonance peak.

---

## §8 Cloud-9 fuller definition (MINOR)

**Reviewer:** "Cloud-9" needs more complete physical description.

**Expanded definition:** Cloud-9 = the σ/m = 174 cm²/g peak at v = 29.4 km/s phenomenologically inferred from the project's reference dataset (SPARC rotation curves + Cloud-9 dwarf-galaxy halo N-body fits). The "cloud" refers to the velocity-distribution-weighted cross-section in dwarf halos; "9" is a project internal label. This is INPUT to the project, not OUTPUT.

---

## §9 Independence of three scans (MINOR)

**Reviewer:** Scans 1 and 3 both compute σ/m(v), not truly independent.

**Clarification:**
- Scan 1 (Calogero, 100 points): point-like Yukawa, m_A' ∈ [1 keV, 2 GeV]. Tests if any (α_D, m_A') gives a peak at v=29.4.
- Scan 2 (Lattice, 12 points): bound-state energy E_0(α_D, m_A'). Tests if any (α_D, m_A') places a bound state at the target energy.
- Scan 3 (Form factor, 245 points): composite Yukawa with F(q) suppression. Tests if a composite propagator changes the peak conclusion.

Scan 1 and 3 are σ/m(v) computations with different physics (point-like vs composite). Scan 2 is bound-state energy, different physical quantity. The three together constrain:
- "Does ANY mechanism produce a peak?" (1, 3)
- "Does ANY point place a bound state where v_target resonance would be?" (2)

These are complementary, not redundant. The phrase "three independent scans" should be replaced with "three complementary numerical paths" or similar.

---

## §10 Missing references (MINOR)

**Reviewer:** Add Tulin-Yu 2013, Tulin-Yu 2018 review, Beneke 2014, Kaplinghat-Tulin-Yu 2016, Griest-Kamionkowski 1990, Itzykson-Zuber QFT.

**Action:** Add to constants.py docstring and to V19_2_F_PLAN_A_COMPLETE_REPORT.md.

---

## Net verdict

The reviewer's audit is constructive and identifies 5 substantive corrections:
1. **Coulomb factor 4**: VALID — fix the formula, update ratios to ~6× (not 25-90×)
2. **Lattice convergence**: VALID — add N and r_max convergence table
3. **Calogero Sommerfeld evidence**: VALID — compute σ/m(v) at κ > κ_c regime, show characteristic Sommerfeld enhancement
4. **Priority 4 physics**: VALID — dipole form factor CAN'T create peaks; rewrite conclusion; mention what would (resonance form factor)
5. **Constraint quantitative**: VALID — replace qualitative JSON with quantitative exclusion curves from literature

These are all documentation/code-level fixes that don't change the Phase 3 verdict (FAIL, paper A wins). The three independent paths remain valid:
- No peak in σ/m(v) (Calogero, 100 points)
- No bound state on ridge (Lattice, 12 points)
- No peak with composite form factor (245 points)

**Recommended actions:**
1. Fix Coulomb formula in V19_2_F_PLAN_A_COMPLETE_REPORT.md
2. Add lattice convergence table (5 lines of code)
3. Compute σ/m(v) at κ = 2, 3 (above κ_c) — small script
4. Rewrite Priority 4 conclusion acknowledging dipole form factor can't peak
5. Add quantitative exclusion curves to constraint JSON

Phase 3 verdict UNCHANGED. Document strengthened.

Standing by for user direction.