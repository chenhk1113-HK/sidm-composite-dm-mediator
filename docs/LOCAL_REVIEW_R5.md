# Local Review (Reviewer 1, Round 5)

**Model:** `qwen3.8-flash-next-iq3_xxs` (strata (deep, :8080))  
**Generated:** 2026-10-25 14:10:36  
**Transport:** direct local OpenAI-compatible `/v1/chat/completions`  
**Why local:** OpenRouter free tier is account-blocked for this host today (HTTP 429 `free-models-per-day` on every free model, including the delegated Nemotron 3 Ultra 550B).  
**Reviewer role:** second independent reviewer, different model family from the OpenCode-side reviewer (DeepSeek/GLM/MiMo).  
**Excerpt source:** `R5_EXCERPT.md` (36199 chars, inlined — the local endpoint has no tool support).  

> **Status: UNVERIFIED SECOND OPINION — AUDITED 2026-10-25.** Every specific numerical claim below must be recomputed in Python before it is acted on.
>
> **Audit result:** all six findings verified against the canonical code and the paper on disk; all six are actionable and the corresponding paper fixes are applied. Corrections to THIS document are marked **Audit note (2026-10-25)** inline. Two of the reviewer’s own supporting calculations were wrong (the “9.85/0.2 = 49.25×” division has no referent in the paper; the “~22×” lower end is not the window minimum, which is 14× at v=15), and the L117 line references are off by one (the quoted text is at excerpt L116 / paper L120). Consolidated record: `docs/dual_review_5loop/SIDM_ROUND5_CONSOLIDATED_FIXES_v1.0_2026-10-25.md`.

## Review

[OK] F1: L11 distinguishes microphysical σ/m from σ_eff = f_H²·σ/m and states σ_eff(15)=0.251 cm²/g is below 0.8 cm²/g. Coherent.

[OK] F2: L36 labels 0.2 cm²/g as decisive CDM-preference threshold and 0.8 cm²/g as w=10 km/s velocity-dependent limit. L2210 repeats 3.6–23.7× vs 0.8 and 27–49× vs 0.2. Against 0.2: 5.43/0.2=27.15 (L118), 4.39/0.2=21.95 (L119), so “27–49×” is not fully supported by the quoted L118–119 values. [Q]
  → **Audit note (2026-10-25):** the *labeling* is correct, but the trailing `[Q]` is a stray — the substantive objection raised here is the L36 finding below, not a new question. Both ceilings are correctly named, and the 3.6–23.7× range IS reproducible from the canonical table (σ/m(15)/0.8 = 3.56×, σ/m(20)/0.8 = 23.65×), unlike the retracted-A.12-based 115–460× range. **Note:** an earlier draft of this review computed the upper end as “9.85/0.2 = 49.25×”; there is no 9.85 cm²/g anywhere in the paper (L143's 9.85e+21 is a dimensionless ratio, and the v=40 σ/m is 9.86), so that division had no referent. Correct value: 9.86/0.2 = 49.3×.

[OK] F3: L117 computes exp[-(15-29.4)²/(2×3.0²)] = exp[-207.36/18] = exp[-11.52] = 9.9e-6 ≈ 1.0e-5. Correct.

[OK] F4: L144 gives 2.84e-13; L145 says this is LOOSER than headline 1.74e-13. Since 2.84e-13 > 1.74e-13, “looser” is correct.

[OK] F5: L57 states unit peak at v=v_t and notes code uses energy-space unit-peak form. Correct.

[OK] F6: L82 uses v_res = c·sqrt(8·ΔM/(2·m_χ)). With ΔM/(2m_χ)=1.2e-9 (L82, L807): v = 299792 km/s × sqrt(8×1.2e-9) = 299792 × 9.798e-5 = 29.4 km/s. Correct.

[OK] F7: L82 says v1 is only physical resonance; v2–v4 are bookkeeping nodes. L896–898 also label them bookkeeping nodes, not physical resonances. Correct.

[OK] F8: L189–190 cap 47.67. If ratio(50)=2.86 and cap ratio=3.0, linear interpolation gives σ_cap = 50×3.0/2.86 = 52.45, not 47.67. If instead ratio ∝ 1/σ_peak, cap = 50×2.86/3.0 = 47.67. The paper does not state the proportionality, but 47.67 is arithmetically consistent with ratio ∝ 1/σ_peak. [OK]

[OK] F9: L1012 frames “7 of 8” as retracted v1.12/v1.13 placeholder, and L1012–1015 state SPARC cannot be matched. No contradiction.

[OK] F10: L1602–1604 and L2264 list 4 PASS: Cluster v=500, dSph v=10, Cloud-9 v=28, SPARC v=100; 3 MARGINAL: UFD v=3, v=5, v=15; 1 FAIL: dSph v=7. Sum = 8. Consistent.

[OK] F11: L189 floor: 50×50/48.14 = 51.96. Cap: 143/3 = 47.67. Since 51.96 > 47.67, EMPTY conclusion is correct.

[ERR] L36: “27–49× at v=9–40 km/s” is not supported by the excerpt’s own numbers. L118 gives 5.43/0.2=27.15×; L119 gives 4.39/0.2=21.95×. The lower end should be ~22× unless additional v=9–40 values are supplied.
  → **Audit note (2026-10-25): FINDING VALID, proposed correction superseded.** 27–49× is not a min–max over the v=9–40 km/s window, so the objection stands. But the window minimum is **14× at v=15** (σ/m = 2.85 cm²/g), not ~22×: the full canonical row set is 27.1× (v=9), 22.2× (v=10), 14.2× (v=15), 37.4× (v=18), 830× (v=28, excluded), 49.3× (v=40). 27–49× is the **v=9 / v=40 endpoint pair**. **FIXED** in the paper: L40 now labels 27–49× as the endpoint pair and states the 14× in-window minimum.

[ERR] L117: “σ/m ~ 0.5–2.5 cm²/g and σ_eff ~ 0.03–0.10 cm²/g” conflicts with L118–119, which give background σ/m = 5.43 and 4.39 cm²/g at v=9–10. If σ_eff = f_H²·σ/m, σ_eff cannot be 0.03–0.10 for σ/m=4.39–5.43 unless f_H≈0.08–0.15, which is not stated.
  → **Audit note (2026-10-25): FINDING VALID, and the defect is worse than stated.** Line reference is off by one — the quoted text is at excerpt **L116** (paper L120), not L117. More importantly the 0.5–2.5 cm²/g band is **STALE**: it predates the `a_slope` 1.0→1.93 propagation (commit 79edeae) and is not reproducible from the canonical Gaussian. The framework’s dSph-scale σ/m is **2.85–16.87 cm²/g**; the published σ_eff band **0.032–0.093 cm²/g** is an *observational* quantity, and at the sweep’s f_H = 0.30 the identity would give σ_eff = 0.256–1.518 cm²/g, i.e. **2.8–47.7× above** published. Reconciliation therefore requires a LARGE NEGATIVE σ_HL. **FIXED** in the paper (canonical band, explicit f_H assumption, negative-σ_HL statement) **and at the generator** — the script’s hardcoded narrative is now computed from the results so it cannot drift again.

[Q] L117: “7 of 8 halos” appears again in a non-retracted context. L1012 retracts “7 of 8 channels,” but L117 uses “7 of 8 halos” for |σ_HL|<0.05. Clarify whether this is a different quantity or a leftover retracted claim.
  → **Audit note (2026-10-25): ANSWERED — and the count itself is wrong.** “7 of 8 channels” (observational channels) and “7 of 8 halos” (dSph halos in the σ_HL fit) are **different quantities**, so L116 is not a resurrection of the retracted L1012 claim. But the “7 of 8” figure no longer holds at all: after the `a_slope` propagation the fitted σ_HL is |σ_HL| ≥ 0.53 cm²/g for every halo, so **0 of 8** satisfy |σ_HL| < 0.05, and Fornax (−0.534) is the *least* discrepant rather than an outlier. **FIXED** in the paper (L102 and L120) and in the JSON’s own verdict/interpretation strings.

[ERR] L145: “Both new values are less restrictive than the σ1=4.4 headline” conflicts with the next sentence: “under σ1≲3.0, the constraint is tighter.” L144–145 already show v=28 bound 2.84e-13 is looser than 1.74e-13. The “tighter” statement is inconsistent unless it refers to a different σ1 regime not shown.
  → **Audit note (2026-10-25): CONFIRMED, and the contradiction is sharper than stated.** σ1 = 1.0 *is* inside “σ1 ≲ 3.0”, so the sentence assigned opposite properties to a single regime. Computed from the paper’s own hierarchy formula g_N/g_χ < 1/√(σ/m·m_χ/σ_SI) at anchor v = 28: σ1=4.4 → σ/m = 166.0 → g < 1.78e-13; σ1=3.0 → 156.7 → g < 1.84e-13; σ1=1.0 → 65.5 → g < 2.83e-13. Narrowing σ1 *lowers* σ/m(28) and therefore *loosens* the allowed g_N/g_χ (a larger permitted g is a deeper hierarchy, not a tighter constraint on it). **FIXED** in the paper: the three computed bounds and the direction of the shift are now stated explicitly.

[Q] L189: “interpolated from ratio=2.86 at σ_peak=50” to cap 47.67 assumes ratio ∝ 1/σ_peak. State that assumption explicitly.
  → **Audit note (2026-10-25): CORRECT, and the assumption holds on the grid.** ratio = 143/σ_peak (143 = 2.86 × 50) reproduces the swept table’s ratio column to within 1.4% at σ_peak = 50, 150, 174, 200 and 250, and 143/3.0 = 47.67 reproduces the cap exactly. **FIXED** in the paper: the assumption and its grid check are now stated.

[Q] L2210: “dSph Horigome+ comparison violated by 3.6–23.7× at w=10” and “27–49× at decisive threshold” are archival, but the 27–49× range remains unsupported by L118–119.
  → **Audit note (2026-10-25): ANSWERED.** Both ranges are reproducible from the canonical σ/m table: 3.6–23.7× vs 0.8 comes from σ/m(15)/0.8 = 3.56× and σ/m(20)/0.8 = 23.65×, and 27–49× vs 0.2 is the v=9 / v=40 endpoint pair (5.43 and 9.86 cm²/g). The archival *staleness* was in the 115–460× range quoted against the 0.04 ceiling at paper L939 and L129 — that came from the **retracted A.12 table** and is superseded by **136–246×** from the canonical table. **FIXED** at L939 and L129.

[OK] L2270: dSph v=15 factor 7.8× above ceiling is internally consistent with L11 abstract range 3.6–23.7×.

[OK] L2275: canonical Phase 44 headline 1 PASS / 0 MARGINAL / 7 FAIL is consistent with L1606 caveat.

---
**Duration:** 246.4s  
**Usage:** {'prompt_tokens': 14292, 'completion_tokens': 1816, 'total_tokens': 16108, 'prompt_tokens_details': {'cached_tokens': 14287}}
