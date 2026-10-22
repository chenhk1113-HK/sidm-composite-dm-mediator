# Nemotron 550B Review (Loop 3)

**Model:** `nvidia/nemotron-3-ultra-550b-a55b:free` (OpenRouter free tier)  
**Transport:** Hermes `delegate_task` child  
**Delegation:** `deleg_03fb72e0`  
**Subagent session:** `20261022_092657_8ae2c2`

> **Status: UNVERIFIED SECOND OPINION.** Every numerical claim below must be
> recomputed in Python before it is acted on. Where the OpenCode/DeepSeek
> reviewer disagrees, that disagreement is the claim to compute first.

## Review

Now I have all the context. Let me compute the unit conversion precisely and answer each question.

**Unit trace for denominator:**
- σ: cm²/g
- ρ: M☉/kpc³  
- r: kpc
- G: kpc³/(M☉·Gyr²) [code line 66: `G_KPC3_PER_MSUN_GYR2 = 4.4987e-6`]
- √(4πGρ): √(kpc³/(M☉·Gyr²) × M☉/kpc³) = 1/Gyr

Denominator units: (cm²/g) × (M☉/kpc³) × kpc × (1/Gyr) = **(cm²/g)(M☉/kpc²)/Gyr**

The denominator does NOT have units of 1/Gyr — it carries an extra **(cm²/g)(M☉/kpc²)** factor.

**Pure unit conversion:**
1 M☉ = 1.98847×10³³ g  
1 kpc = 3.08568×10²¹ cm  
1 M☉/kpc² = 1.98847×10³³ / (3.08568×10²¹)² = **2.088×10⁻¹⁰ g/cm²**

Reciprocal: 1 / 2.088×10⁻¹⁰ = **4.788×10⁹** (kpc²/M☉)/(g/cm²)

This is the pure unit-conversion factor to make (cm²/g)(M☉/kpc²) dimensionless.

**Paper's ~8.9×10⁹ vs pure factor:**
Code line 283: "factor of ~8.7e9"; line 300: "~8.9e9"  
Code line 80-82: literal 150×C formula gives 15.77 Gyr for BM2, N-body = 28.7 Gyr → ratio **1.82** (BM2-specific calibration)

8.9×10⁹ / 4.79×10⁹ ≈ **1.86** ≈ BM2 calibration factor (1.82)

The paper's ~8.9×10⁹ = (pure unit conversion ~4.8×10⁹) × (BM2 calibration ~1.82)

**CALIBRATED_PREFACTOR decomposition:**
Line 301: `CALIBRATED_PREFACTOR = 1.34e12`  
Effective prefactor = 1.34e12 × 0.75 = 1.005e12  
Published prefactor = 150 × 0.75 = 112.5  
Ratio = 1.005e12 / 112.5 = **8.93×10⁹**

Implied pure unit factor = 8.93×10⁹ / 1.82 = **4.91×10⁹** (matches calculated 4.79×10⁹ within constant precision)

---

[ERR] v0.3-prelim/code/gravothermal_yang2024.py:300 — Comment claims "implicit unit conversion factor of ~8.9e9" but this conflates pure unit conversion (~4.8e9) with BM2-specific N-body calibration (~1.82). The pure unit conversion is 1 M☉/kpc² = 2.088e-10 g/cm² → reciprocal 4.79e9.

[ERR] PAPER_V1_DRAFT.md (context lines 90-93) — States "prefactor 150 needs an implicit unit conversion of ~8.9e9" without disclosing this includes a halo-specific calibration factor. A reader cannot reproduce the formula from the paper alone.

[Q] Dimension of 'C' in '150*C' — Code line 61 defines `C_CALIBRATION = 0.75` as "calibrated constant" (line 75: "we fix C = 0.75"). Paper excerpt does not specify dimensions of C; it is treated as dimensionless but absorbs unit-system assumptions.

[ERR] v0.3-prelim/code/gravothermal_yang2024.py:272-296 — Function `collapse_time_gyr` docstring claims output in Gyr but the formula `CALIBRATED_PREFACTOR * C_CALIBRATION / denom` only yields Gyr because CALIBRATED_PREFACTOR=1.34e12 implicitly carries units (g/cm²)(kpc²/M☉). This is not documented in the function signature.

[OK] Code lines 115-150 (`collapse_time_SI_gyr`) correctly implements the formula in pure SI units and returns 15.77 Gyr for BM2 with the published 150×C prefactor, confirming the unit mismatch is ~4.8e9 (pure) × 1.82 (BM2 calibration).

[Q] Whether the paper's quoted t_c = 28.7 Gyr for BM2 (context line 31, code line 112) refers to the N-body result or the calibrated formula — the code comment line 80-82 confirms 28.7 Gyr is the N-body value, and the calibrated formula is tuned to match it.