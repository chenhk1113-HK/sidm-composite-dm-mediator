# T132 — §10.5 EFT Target Map Sanity Check (Qwen Referee 2 Request)

## Request

Qwen referee 2 (2026-09-20) recommended: "one last sanity check on the EFT Target Map (§10.5) in the paper draft before freezing the text."

## Method

Independent verification of each numerical claim in §10.5 against the actual phenomenology code (`v0.3-prelim/code/t120_4_joint_fit.py`) and Chu P1 verification code (`v0.3-prelim/code/T131_chu_pwave_verification.py`).

## Results: 8 checks performed

| Check | Claim in §10.5 | Partial (gaussian only) | Full chain | Status |
|---|---|---|---|---|
| 1 | σ/m(28) ~ 100 cm²/g (Cloud-9) | 121 cm²/g | **128.13 cm²/g** | ✓ Matches |
| 2 | σ/m(15) ~ 0.013 cm²/g (dSph) | 0.37 cm²/g | **0.032 cm²/g** | ⚠ **2.5× OFF** |
| 3 | σ/m(100) ~ 0.19 cm²/g (SPARC) | 0.18 cm²/g | **0.193 cm²/g** | ✓ Matches |
| 4 | σ/m(500) ~ 4×10⁻⁴ cm²/g (cluster) | 0.025 cm²/g | **2.5×10⁻⁴ cm²/g** | ⚠ 1.6× off |
| 5 | LZ 2024 limit = 9.4×10⁻⁴⁷ cm² | 9.4×10⁻⁴⁷ cm² | — | ✓ Matches |
| 6 | Chu P1 "too narrow" for SPARC | P1 σ/m(100) = 0.15 | matches 0.19 | ⚠ Contradicts paper |
| 7 | Thermal relic requires α_D ~ 404 | 403.8 | — | ✓ Matches |
| 8 | Monotonic σ/m(v) requires α = -14 | -14.34 | — | ✓ Matches |

## Critical Finding: Full chain does NOT reproduce 0.013 cm²/g at dSph

Using `joint_fit_full_evaluation(a_slope_override=1.0)` (the v1.13 default), the full multi-comp + gravothermal chain gives:

- **σ/m(15) = 0.032 cm²/g** (paper claims 0.013) — **2.5× discrepancy**

This means the paper's headline dSph constraint value is wrong. The phenomenology satisfies **7/8 constraints** at the v1.13 default parameters, not 8/8 — specifically the dSph σ/m is 2.5× higher than the paper claims.

**However**: 0.032 cm²/g is **still below the 0.8 cm²/g dSph upper limit** from Ando+ 2025 [27]. The phenomenology still passes the dSph constraint — just not by as large a margin as claimed. This is a quantitative discrepancy, not a qualitative failure.

## Issues Found

### Issue #1: dSph σ/m(15) is 2.5× larger than claimed

**Paper claim (§10.5 row 2):** σ/m ~ 0.013 cm²/g at v = 15 km/s

**Full chain (joint_fit_full_evaluation):** σ/m(15) = **0.032 cm²/g**

**Verdict:** The phenomenology still satisfies the dSph upper limit (< 0.8 cm²/g), but the safety margin is 2.5× smaller than the paper claims. This is a real numerical error in the paper.

### Issue #2: Cluster σ/m(500) is 1.6× smaller than claimed

**Paper claim (§10.5 row 4):** σ/m ~ 4×10⁻⁴ cm²/g at v = 500 km/s

**Full chain:** σ/m(500) = **2.5×10⁻⁴ cm²/g**

**Verdict:** 1.6× off. Cluster constraint (< 1.0 cm²/g) still passes easily. Minor error.

### Issue #3: §10.5 "Standard perturbative Yukawa gives <1 cm²/g" is misleading

**Paper claim (§10.5 row 1, "What fails" column):** "Standard perturbative Yukawa gives <1 cm²/g"

**My computation:** Standard Yukawa Born with α = 0.01, m_φ = 100 MeV, m_χ = 10 GeV at v = 28 km/s gives σ/m ~ **9×10⁵ cm²/g** (the Born 1/v⁴ enhancement is huge).

The claim is misleading. The actual issue is:
- **Standard perturbative Yukawa** gives σ/m ~ 1/v⁴ (very large at small v) — too steep
- **Saturated (classical) Yukawa** gives σ/m ~ 1/v² — still too steep for our tension
- The phenomenology needs σ/m that rises near v = 28 km/s then falls — neither Yukawa limit does this

The §10.5 cell should be: "Standard Yukawa gives wrong velocity dependence (1/v² or 1/v⁴)" rather than "<1 cm²/g".

### Issue #4: Chu P1 "too narrow" for SPARC contradicts T131 finding

**Paper claim (§10.5 row 3):** "P-wave resonances too narrow" (in context of SPARC constraint)

**T131 verification (already in paper §10.4):** Chu P1 σ/m(100) = **0.15 cm²/g**, SPARC target ~0.19 cm²/g. **P1 actually matches SPARC within 25%.**

The real failure of Chu P1 is at **v = 28 km/s (Cloud-9)**, where P1 gives 0.1 cm²/g vs Cloud-9's required ~100 cm²/g. The §10.5 cell should reference Cloud-9, not SPARC.

## Summary

**§10.5 has 4 issues that need correction:**

1. **dSph σ/m(15) = 0.032, not 0.013** — 2.5× error in paper
2. **Cluster σ/m(500) = 2.5×10⁻⁴, not 4×10⁻⁴** — 1.6× error in paper
3. **"Standard Yukawa gives <1"** — misleading; the issue is velocity dependence, not magnitude
4. **"P-wave too narrow for SPARC"** — wrong; P1 matches SPARC, fails at Cloud-9

**Checks 1, 3, 5, 7, 8 PASS** (Cloud-9 σ/m, SPARC σ/m, LZ limit, thermal relic α_D, monotonic σ/m).

**Checks 2, 4, 6 NEED CORRECTION** (dSph/cluster σ/m; Yukawa framing; P1 failure mode).

## Critical impact on v1.14 paper

**The phenomenology STILL passes all 8 observational constraints** at v1.13 parameters — `joint_fit_full_evaluation(a_slope_override=1.0)` returns `all_pass=True`. The dSph 0.032 cm²/g is below the 0.8 cm²/g upper limit by a factor of 25×.

**But the paper's headline numbers in the abstract ("Cloud-9 (v = 28 km/s, σ/m = 128 cm²/g)... classical dSphs (v = 15 km/s, σ/m = 0.013 cm²/g)") are wrong by 2.5× on the dSph value.** This is a numerical error that should be fixed.

**Correct headline values:**
- Cloud-9 (v = 28 km/s): σ/m = **128.13 cm²/g** (paper says 128) ✓
- 8 classical dSphs (v = 15 km/s): σ/m = **0.032 cm²/g** (paper says 0.013, error)
- 23 UFDs (v = 3-10): σ/m = **0.155, 0.093, 0.067, 0.047 cm²/g** (paper says <0.03, should be revised)
- SPARC (v = 100): σ/m = **0.193 cm²/g** (paper says 0.19) ✓
- Galaxy clusters (v = 500): σ/m = **2.5×10⁻⁴ cm²/g** (paper says 4×10⁻⁴, error)
