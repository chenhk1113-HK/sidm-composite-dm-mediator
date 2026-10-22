# OpenCode CLI Review

**Model:** `opencode/deepseek-v4.1-flash-free`  
**Generated:** 2026-10-22 09:29:10 China Standard Time  
**Duration:** 189.0s  
**Transport:** `opencode run --model <id>` (OpenCode free tier is CLI-only; direct API returns HTTP 403 FreeTierError)  
**Reviewer role:** second independent reviewer, different model family from the Nemotron/OpenRouter reviewer  

> **Status: UNVERIFIED SECOND OPINION.** This is one reviewer's critique. Every specific numerical claim below must be recomputed in Python before it is acted on -- the free-tier models fabricate plausible numbers. Compare against the Nemotron review: where they agree, the finding is likely real; where they disagree, that is the claim to compute first.

**Prompt source:** `scripts\review_prompt_loop2_tcore_two_values.txt`

## Priority chain attempt log

| Model | Result | Seconds |
|---|---|---|
| `opencode/deepseek-v4.1-flash-free` | OK | 189.0 |

## Review

[ERR] Breit–Wigner normalization: PAPER_V1_DRAFT.md:34 gives BW=(Γ/2)²/[(v²−v_t²)²+(Γv_t/2)²]. At v=v_t this is 1/v_t², not 1; with σ_peak=174, v_t=29.4 (PAPER_V1_DRAFT.md:840), the peak is 174/29.4²=0.20 cm²/g, not 174. Numerator needs (Γv_t/2)². Also :35 calls Γ an FWHM in v²-space, inconsistent with the Γv_t term.

[ERR] Horigome limit: PAPER_V1_DRAFT.md:949 gives the velocity-independent (w→∞) limit as 0.04 cm²/g, while :950 gives 0.2 for w=30. Yet :38 calls 0.2 the “velocity-independent (w→∞, 0.2 cm²/g)” limit, and :117–123 use 0.2. At v=9, σ/m=5.43 (:845), so 5.43/0.04=136×, not 27×; at v=40, 9.86/0.04=247×, not 49×. :958 itself says 0.04 gives 115–460×, contradicting :38.

[ERR] Hierarchy arithmetic: PAPER_V1_DRAFT.md:143 quotes ratio 5.2×10⁴⁴ and g_N/g_χ<4.4×10⁻²³ at σ/m(100)=0.052. From :2103–2104, σ_DM=174×1.78×10⁻²⁴=3.10×10⁻²² cm², σ_SI=9.4×10⁻⁴⁸, ratio=3.3×10²⁵, g_N/g_χ=1.7×10⁻¹³. At v=100: 0.052×1.78×10⁻²⁴=9.3×10⁻²⁶; /9.4×10⁻⁴⁸=9.9×10²¹, giving ≈1.0×10⁻¹¹. :144’s 6.5×10⁴⁷/1.2×10⁻²⁴ is ~22 orders off; :145’s 10⁻¹¹ also conflicts with :38’s 1.7×10⁻¹³.

[ERR] PAPER_V1_DRAFT.md:92 attributes σ/m(15)=2.56 to v_target=28 versus 2.85 at 29.4. At fixed a=1.93, v_t=28 gives 0.052(100/15)^1.93 +174exp(−169/38.72)=2.02+2.21=4.23. The 2.56 value requires a=1.0: 0.052(100/15)+2.21=0.347+2.21=2.56. The change is not v_target alone.

[ERR] PAPER_V1_DRAFT.md:117 states exp[−(15−29.4)²/(2×3²)]≈8×10⁻⁵; it is exp(−207.36/18)=1.0×10⁻⁵, as :158 correctly says.

[Q] Cloud-9 benchmark is ≥50 cm²/g at PAPER_V1_DRAFT.md:11,:173,:826,:1891 but ≥100 at :38,:862,:864,:960,:1003; :828 treats 50 as the Elbert value. This changes the pass/fail line (87 vs 100).

[Q] σ_peak provenance: PAPER_V1_DRAFT.md:162 says Phase 44 prefers 196.3; :894 lists 178.5 (Phase 4) and 196.3; :2076 says 178.5 is the Phase 44 best fit; :38 calls 174 the Phase 44 value, though :2258 says 174 is the causality cap, not a fit.

[OK] PAPER_V1_DRAFT.md:92: 0.052(100/15)^1.93=2.02; 174exp(−207.36/38.72)=0.823; sum=2.85. :105: 0.297²×2.85=0.252. :2104: 174×1.78×10⁻²⁴=3.10×10⁻²²; /9.4×10⁻⁴⁸=3.3×10²⁵; 1/√=1.7×10⁻¹³. :938: 0.052(100/200)^1.93=0.014; (100/300)^1.93 gives 0.0062.
