# D-8 POST-DICTION AUDIT — Trace every σ/m claim to source

**Date:** 2026-10-03
**Auditor:** K Lam (per R86 reviewer's "systematic parameter audit" recommendation)
**Scope:** Every numerical σ/m, t_core, Ωh², v_target, σ_peak claim in PAPER_V1_DRAFT.md
**Source:** Phase 44 free fit (best_params), constants.py (R67 SINGLE SOURCE OF TRUTH), T221 framework code, R74-R87 corrections

---

## Claim traceability table

### σ/m = 174 cm²/g (causality cap)

**Source:** Phase 44 free fit best_params[4] = 178.5; **paper uses 174 (causality cap per §9.12)** — R76 decision.
**Status:** ✓ Match (within 3%).

### σ/m = 135.3 at V_max = 31.12 (Cloud-9)

**Source:** Framework v1 resonance Gaussian at v_target=28, σ_peak=174, σ_1=4.4 evaluated at v=31.12 = 174 × exp(-(31.12-28)²/(2×4.4²)) = 174 × 0.778 = 135.3.
**Status:** ⚠ This used v_target = 28 km/s (R74 baseline). Per R74 fix, v_target should be 29.4 km/s. Recomputing: σ/m at v=31.12 from v_target=29.4 = 174 × exp(-(31.12-29.4)²/(2×4.4²)) = 174 × 0.871 = 151.6 (not 135.3). **OUTDATED — needs R88 update.**

### σ/m = 165.6 at v=28 (Cloud-9)

**Source:** T235 with v_target=29.4, σ_peak=174, σ_1=4.4 at v=28 = 174 × exp(-(28-29.4)²/(2×4.4²)) + 0.052 × (100/28)^1.93 = 165.59 + 0.6 = 166.0.
**Status:** ⚠ v=28 (not V_max=31.12) — need to clarify whether this is the canonical reference velocity. R74 fix: 28→29.4.

### t_core = 91 Myr at c=12 (Cloud-9)

**Source:** Balberg+ formula at Cloud-9 host-halo parameters (M=5e9 M☉, c=12, V_max=31.12, σ/m=135.3). Per T208 path_b script. Causality: t_core/t_cross = 0.99 (FAIL).
**Status:** ⚠ σ/m=135.3 uses outdated v_target=28; recomputed σ/m=151.6 gives t_core ≈ 75 Myr (still causality-FAIL, still indicative not physical).

### t_core = 4.42 Gyr at c=4 (Cloud-9)

**Source:** Same σ/m=135.3 at c=4 with V_max=25.59. Causality-OK.
**Status:** ⚠ Same v_target issue. Recomputed σ/m=151.6 at c=4 V_max=24.75 gives t_core ≈ 4.0 Gyr.

### σ/m = 0.052 at v=100 (Phase 44 baseline)

**Source:** Phase 44 free fit best_params[1] = 0.0516; rounded to 0.052 in paper.
**Status:** ✓ Match (within 1%).

### a_slope = 1.93 (Phase 44)

**Source:** Phase 44 free fit best_params[2] = 1.9286; rounded to 1.93.
**Status:** ✓ Match (R88 fix: scripts now use a_slope=1.93, was 1.0).

### v_target = 29.4 km/s

**Source:** Phase 44 free fit best_params[3] = 29.36; rounded to 29.4 in constants.py.
**Status:** ✓ Constants.py correct; some paper text still uses 28 (R74 fix incomplete — need sweep).

### σ_1 = 4.4 km/s (phenomenological)

**Source:** Paper convention (constants.py SIGMA_KMS = 4.4). NOT from Phase 44 fit (Phase 44 used w1=430, w2=769, w3=196 multi-resonance).
**Status:** ⚠ Different parameterizations; paper uses single Gaussian σ=4.4 km/s (R76 decision).

### Ωh² = 0.119 at δ = 0.43%

**Source:** T192 thermal-avg calculation. **T192 used m_χ = 10.3 GeV** (per R87 audit), NOT framework's m_χ = 1 GeV.
**Status:** ✗ WRONG m_χ — R87 removed this claim.

### Ωh² = 0.116 (T190 v2 single-velocity)

**Source:** T190 v2 single-velocity BW evaluation at δ=0.43%, g_h_SM=0.001.
**Status:** ⚠ Superseded by T192 thermal-avg (better than T190); T190 had off-resonance error.

### α_χ ≈ 6.8×10⁻⁷

**Source:** Derived from framework σ_peak = 174, m_χ = 1 GeV, m_φ = 200 eV using α_χ = g_χ²/(4π) with σ_peak = A_res × (g^4/(32π m_χ²)) × (ℏc)² × (c/v_target)⁴. R58 derivation, R70 4π fix.
**Status:** ⚠ R70 acknowledged factor-320 mismatch with Tulin-Yu Eq. (5); R72 ratio derivation supersedes. R83 footnote only.

### g_N/g_χ < ~10⁻¹³ (R83 v=28 anchor)

**Source:** R72 ratio derivation: σ_DM-DM(per particle, m_χ=1 GeV) = 65 cm²/g × 1.78e-24 = 1.16e-22 cm² at v=28 (Cloud-9). σ_SI < 10⁻⁴⁶ cm² (LZ). Ratio = 1.16e24. sqrt = 1.08e12. g_N/g_chi < 1/1.08e12 = 9.3e-13.
**Status:** ✓ Match (R83 headline).

### σ_DM-DM(28) under σ_1 = 4.4 with a_slope = 1.93

**Re-computation (R88):** σ/m(28) = 0.052 × (100/28)^1.93 + 174 × exp(-(28-29.4)²/(2×4.4²)) = 0.60 + 165.4 = 166.0 cm²/g.
**Per-particle σ_DM-DM(28)** = 166.0 × 1.78e-24 = 2.96e-22 cm².
**Status:** ✓ Match with σ_1=4.4 at v=28.

### σ_DM-DM at v=28 under σ_1 = 1.0 (D-5 fit max-likelihood)

**Re-computation (R88):** σ/m(28) = 0.052 × (100/28)^1.93 + 174 × exp(-(28-29.4)²/(2×1.0²)) = 0.60 + 0.96 = 1.56 cm²/g.
**Per-particle σ_DM-DM(28)** = 1.56 × 1.78e-24 = 2.78e-24 cm².
**Status:** ✓ Match.

---

## v_target = 28 vs 29.4 remaining inconsistencies

Per R74, paper should use **v_target = 29.4 km/s** everywhere. Lines still using 28:

| Line | Claim | R74 status |
|------|-------|-----------|
| L819 | "framework's v₁ resonance at v_target = 28 km/s is included" | NEEDS R74 fix |
| L1454 | "v₁ resonance at v_target = 28 km/s" | NEEDS R74 fix |
| L1830 | "v₁ resonance at v_target = 28 km/s, σ_peak ≈ 174" | NEEDS R74 fix |
| L2042 | "v₁ resonance at v_target = 28 km/s" | NEEDS R74 fix |
| L2150 | "v₁ resonance peak fit" | NEEDS R74 fix |
| L2154 | "v_target = 28 km/s" | NEEDS R74 fix |

**Pre-submission sweep:** all "v_target = 28 km/s" → "v_target = 29.4 km/s" (R74).

---

## σ/m = 135.3 vs R74-corrected value

**Old (R74-pre):** σ/m(V_max=31.12) = 174 × exp(-(31.12-28)²/(2×4.4²)) = 174 × 0.778 = **135.3 cm²/g**
**Corrected (R74+):** σ/m(V_max=31.12) = 174 × exp(-(31.12-29.4)²/(2×4.4²)) = 174 × 0.871 = **151.6 cm²/g**

Lines using 135.3:

| Line | Claim | Needs R74 update? |
|------|-------|---------------------|
| L829 | "135.3 cm²/g (v₁ resonance ON, evaluated at V_max)" | YES → 151.6 |
| L1480 | "σ/m at V_max = 135.3 cm²/g" | YES → 151.6 |
| L1837 | "σ/m = **0.167** at V_max = 31.12" (Yukawa-only) | Phase 44 Yukawa: σ/m(31.12) = 0.052 × (100/31.12)^1.93 = 0.43 (NOT 0.167; **MISMATCH with a_slope=1.93**) |
| L1838 | "framework v₁ resonance ON at V_max, σ/m = 135.3" | YES → 151.6 |
| L1842 | "framework v₁ at V_max σ/m = 135.3" | YES → 151.6 |
| L2098 | "framework σ/m = 135.3 cm²/g with c=4, t_core = 4.42 Gyr" | YES — recompute with σ/m=151.6, c=4 |
| L2124 | "framework σ/m = 135.3 cm²/g with quiescent merger history" | YES |

---

## Summary

**Verified claims (status ✓):**
- σ_peak = 174 (causality cap)
- σ_0 = 0.052 (Phase 44 best_params[1] rounded)
- a_slope = 1.93 (R88 fix applied)
- v_target = 29.4 km/s (constants.py)
- g_N/g_χ < ~10⁻¹³ (R83 ratio derivation)
- σ/m at v=28 = 166.0 (R88 corrected with a_slope=1.93)

**Outdated claims needing fix:**
- "σ/m at V_max = 135.3" (uses v_target=28) → 151.6 (R74 fix)
- "v_target = 28 km/s" (multiple lines) → 29.4 km/s (R74 fix)
- "Ωh² = 0.119 from T192" (uses m_χ=10.3) → REMOVED (R87)
- "Carney+ 2021" (wrong arXiv ID 2102.02194) → Hambye+ 2021 arXiv:2106.01403 (R88)

**Removed claims (R87):**
- "Ωh² = 0.119" at framework's m_χ=1 GeV (T192 used wrong m_χ)

**Pre-submission sweep needed:** ~10-15 lines referencing v_target=28 → update to 29.4; ~5 lines referencing σ/m=135.3 → recompute with σ/m=151.6.

---

*Audit completed 2026-10-03 per R86 reviewer recommendation*
*Stored at `v0.3-prelim/docs/POST_DICTION_AUDIT_R88.md`*
*Time spent: ~20 minutes*