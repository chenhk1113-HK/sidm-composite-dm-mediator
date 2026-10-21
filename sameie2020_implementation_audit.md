# Sameie+ 2020 Implementation Physical Reasonableness Audit

## Verdict
**PARTIALLY REASONABLE / NOT VERIFIABLE** — The Sameie+ 2020 implementation correctly captures the *qualitative* finding that c_200 INCREASES in deep collapse (cuspy collapse), opposite to Elbert+ 2015 and Burkert-style. However, the quantitative c-τ prescription (slope=0.40, saturation τ=5, ceiling=2×NFW) is **not derived from the paper** — the paper provides no quantitative c-τ formula. A critical implementation bug causes the "increase" to actually be a decrease from the Yang+ τ=1 value (26.4 for c₀=12) to the 2×NFW ceiling (24.0).

---

## Parameter Comparison Table

| Parameter | Paper (Sameie+ 2020) | Implementation (`sameie2020_c_tau_prescription.py`) | Verdict |
|---|---|---|---|
| **σ/m for diverse rotation curves** | 3 cm²/g (abstract, §1) | Used as context only; not in c-τ formula | MATCH (context) |
| **σ/m threshold for core collapse** | >5 cm²/g (abstract, §1) | Implicit via τ mapping; not explicit | NOT VERIFIABLE |
| **Direction of c_200 in deep collapse** | INCREASES (cuspy) — §1, §4, Conclusions | INCREASES (positive slope +0.40/τ) | MATCH (qualitative) |
| **Halo mass definition** | M_200 (throughout) | M_200 via Diemer+ 2019 c-M relation | MATCH |
| **Concentration definition** | c_200 (throughout) | c_200 consistent | MATCH |
| **Initial c_200 values (simulated)** | Dwarf 1: 29.5; Dwarf 2: 22.9; Draco: 28; Fornax: 12 | c₀ = 12.0 (Cloud-9 NFW) | NOT VERIFIABLE (different halo) |
| **c_200 ceiling in deep collapse** | Not stated quantitatively; Dwarf 1 initial c_200=29.5 is 2.5× median | 2× NFW (ceiling = c₀ × 2.0) | NOT VERIFIABLE |
| **c-τ slope in deep collapse** | No quantitative formula provided | +0.40 per τ-unit (SAMEIE_C_TAU_SLOPE) | NOT VERIFIABLE |
| **Saturation τ** | Not stated | τ = 5.0 (SAMEIE_C_TAU_SATURATION) | NOT VERIFIABLE |
| **Continuity at τ=1** | N/A (no prescription) | Continuous by construction (uses Yang+ at τ≤1) | MATCH (internal) |
| **Mass loss rate independence of σ/m** | "Almost identical for SIDM and CDM" (§4) | Not modeled | NOT VERIFIABLE |

---

## Specific Discrepancies Found

### 1. **Ceiling Below Yang+ τ=1 Value — Implementation Bug**
**File:** `scripts/sameie2020_c_tau_prescription.py:63-65, 88-95`  
**Issue:** `SAMEIE_C_TAU_CEILING = 2.0` (2× NFW = 24.0 for c₀=12), but Yang+ Eq. 5 at τ=1 gives c_200 = 26.393. The linear interpolation for τ>1 goes **down** from 26.393 to 24.0, contradicting the stated "c_200 INCREASES" intent.  
**Physical consequence:** At Cloud-9's τ ≈ 46, c_200 = 24.0 (ceiling), but at τ=1 it would be 26.4. The "cuspy collapse" prescription actually predicts a *lower* concentration at deep collapse than at the max-core transition.

### 2. **Quantitative Prescription Not in Paper**
**File:** `scripts/sameie2020_c_tau_prescription.py:30-44, 62-65`  
**Issue:** Parameters `SAMEIE_C_TAU_SLOPE = 0.40`, `SAMEIE_C_TAU_SATURATION = 5.0`, `SAMEIE_C_TAU_CEILING = 2.0` are prescription choices acknowledged in comments as "SIMPLIFIED prescription... does not provide a quantitative c_tau formula."  
**Physical consequence:** The marginalization result (Sameie+ tension = -1.39σ vs Elbert+ +0.32σ) depends entirely on these unvalidated choices. A different ceiling (e.g., 2.5× NFW matching Dwarf 1's 2.5× median) would change the tension magnitude.

### 3. **σ/m–τ Mapping Not Anchored to Paper**
**File:** `scripts/v19_2_f_cloud9_cM_three_prescriptions.py:64-76`  
**Issue:** τ is computed from `t_core` via `T_HUBBLE_GYR / t_core` using the Yang+ gravothermal formula. The paper's core-collapse timescale scaling is `t_c ∝ 1/(σ/m) × M_200 × c_200` (Eq. from ref [59], Essig+ 2018), but the project uses a different t_c formula (Yang+ 2024). The paper's σ/m > 5 cm²/g threshold for collapse is not explicitly mapped to τ > 1.  
**Physical consequence:** The τ=46 for Cloud-9 corresponds to an effective σ/m that cannot be directly verified against the paper's σ/m = 3, 5, 10 cm²/g simulation grid.

### 4. **Cloud-9 vs Paper Halo Parameters Mismatch**
**File:** `scripts/v19_2_f_cloud9_cM_three_prescriptions.py:42-44`  
**Issue:** Cloud-9 uses `CLOUD9_C_0 = 12.0`, `CLOUD9_M_HALO = 4.7e9 M☉`. The paper simulates Dwarf 1 (M_200=2e9, c_200=29.5), Dwarf 2 (M_200=2e9, c_200=22.9), Draco (M_200=4e9, c_200=28). Cloud-9's NFW concentration (12) is far below the paper's high-concentration dwarfs (22–29).  
**Physical consequence:** The paper emphasizes core collapse is "extremely sensitive to initial halo concentration" (§4). Applying a prescription calibrated to high-c_200 halos to a low-c_200 halo (Cloud-9) is an extrapolation beyond the paper's regime.

---

## Scope: What Was Checked vs. What Could NOT Be Checked

### ✅ Checked (Verifiable)
- Paper's qualitative finding: c_200 INCREASES in deep collapse (cuspy) — MATCHES implementation intent
- Paper's σ/m = 3 cm²/g for rotation curves; σ/m > 5 cm²/g for core collapse — CONSISTENT with project usage
- Paper's halo definitions: M_200, c_200 — MATCH implementation conventions
- Paper's emphasis on concentration sensitivity for collapse — ACKNOWLEDGED but not quantified in implementation
- Implementation continuity at τ=1 — VERIFIED (code self-test passes)
- Implementation ceiling enforcement — VERIFIED (c_200 never exceeds 2×NFW)

### ❌ NOT VERIFIABLE (Paper Does Not Provide)
- Quantitative c-τ relation (slope, saturation, ceiling) — **Paper has no formula**
- Mapping from σ/m to τ for specific halos — **Paper uses N-body, not τ parameterization**
- Final c_200 values for collapsed halos as multiple of NFW — **Paper shows density profiles, not c_200 evolution**
- Whether 2×NFW ceiling is physically motivated — **Paper's Dwarf 1 has c_200=29.5 (2.5× median), not 2×NFW**
- Burkert 1995 / Balberg+ 2002 connection to Sameie+ — **Unrelated papers; implementation mixes frameworks**

### ⚠️ PARTIALLY CHECKED
- Yang+ Eq. 5 polynomial behavior at τ=1 — VERIFIED numerically (gives c_200=26.4 for c₀=12), but **Eq. 5 is calibrated only for τ≤1** (per Nemotron review), making the τ=1 anchor questionable for deep-collapse extrapolation.

---

## Recommendation
**Do NOT cite Sameie+ 2020 as a quantitatively validated prescription for the 3-prescription marginalization.** The paper supports only the *qualitative direction* (c_200 increases in deep collapse for high-concentration halos). The quantitative implementation parameters (slope, ceiling, saturation) are project-invented placeholders. The marginalization's conclusion that "c-M tension is prescription-dependent" is valid, but the Sameie+ branch's specific tension value (-1.39σ) has no empirical anchor in the cited paper. Recommend framing the Sameie+ branch as a "qualitative sign-flip test" only, not a calibrated physical model.