# Nemotron 550B Review (Loop 5)

**Model:** `nvidia/nemotron-3-ultra-550b-a55b:free` (OpenRouter free tier)  
**Transport:** Hermes `delegate_task` child  
**Delegation:** `deleg_b1fc89ec`  
**Subagent session:** `20261022_092709_2415c1`

> **Status: UNVERIFIED SECOND OPINION.** Every numerical claim below must be
> recomputed in Python before it is acted on. Where the OpenCode/DeepSeek
> reviewer disagrees, that disagreement is the claim to compute first.

## Review

[ERR] QUESTION 1(a): sigma_peak window at c=12 is EMPTY. Floor = 51.96 cm²/g (PAPER_V1_DRAFT.md:176,189), causality cap = 47.65 (line 176) and 47.71 (line 189). 51.96 > 47.71 → window empty. File: PAPER_V1_DRAFT.md lines 176,189.

[ERR] QUESTION 1(b): Floor calculation 50 × 50/48.14 = 51.93, not 51.96. 50 × (50/48.14) = 2500/48.14 = 51.9318. Paper quotes 51.96 (lines 176,189). Discrepancy = 0.03 cm²/g (rounding or slightly different σ/m(28) value used).

[ERR] QUESTION 1(c): Causality cap from ratio interpolation. At σ_peak=50, ratio=2.86 (line 184). K = 50 × 2.86 = 143. Cap σ_peak = 143/3 = 47.667. Paper quotes 47.65 (line 176) and 47.71 (line 189) — two values differ by 0.06. Real inconsistency: 47.65 vs 47.71 not explained.

[ERR] QUESTION 1(d): "σ_peak = 174 fails by 3.6×" refers to causality ratio (3.0/0.83 = 3.61), NOT floor ratio (174/51.96 = 3.35). Paper line 184: ratio=0.83 at σ_peak=174; line 205: "factor ~3.6 below cap". The 3.6× is correctly the cap violation, but the question's phrasing "given the floor of 51.96" conflates two different ratios.

[OK] QUESTION 2(e): Distinct channel counts with locations:
- "4 of 8" — PAPER_V1_DRAFT.md:1013,1014,1085,1086 (Yang+/T202 f_H, physically motivated)
- "4 of 7" — PAPER_V1_DRAFT.md:942 (Lei/Wang added to 4-channel fit; RETIRED per line 2266 due to double-count)
- "7 of 10" — PAPER_V1_DRAFT.md:1707 (retracted borrowed f_H, 3 placeholders unconstrained)
- "~6 of 8" — PAPER_V1_DRAFT.md:1087 (T183 fluid f_H, with caveat)
- "7 of 8" — GRAVOTHERMAL_ROADMAP.md:134 (retracted borrowed f_H)
These describe DIFFERENT f_H prescriptions/channel sets, not direct conflicts. The paper now leads with "4 of 8 under physically motivated f_H" (COVER_LETTER.md:49).

[OK] QUESTION 2(f): JSON: Cloud9_threshold_50=50.0, dSph_ceiling_0p8=0.8, dSph_violation_factor=43.333. Check: sigma_m_v15_C9_CORE_enhanced=34.667 (line 267); 34.667/0.8 = 43.333 ✓. This is the CORE-ENHANCED v=15 violation, NOT the 3.6× causality failure at σ_peak=174 (which is 3.0/0.83=3.61). Different quantities.