# OpenCode CLI Review

**Model:** `opencode/deepseek-v4.1-flash-free`  
**Generated:** 2026-10-22 09:29:12 China Standard Time  
**Duration:** 190.7s  
**Transport:** `opencode run --model <id>` (OpenCode free tier is CLI-only; direct API returns HTTP 403 FreeTierError)  
**Reviewer role:** second independent reviewer, different model family from the Nemotron/OpenRouter reviewer  

> **Status: UNVERIFIED SECOND OPINION.** This is one reviewer's critique. Every specific numerical claim below must be recomputed in Python before it is acted on -- the free-tier models fabricate plausible numbers. Compare against the Nemotron review: where they agree, the finding is likely real; where they disagree, that is the claim to compute first.

**Prompt source:** `scripts\review_prompt_loop4_nfw_selfconsistency.txt`

## Priority chain attempt log

| Model | Result | Seconds |
|---|---|---|
| `opencode/deepseek-v4.1-flash-free` | OK | 190.7 |

## Review

**PAPER** = `v0.3-prelim/docs/PAPER_V1_DRAFT.md`

[ERR] `PAPER:36`, `:843-856` vs `:949-950` — Horigome limits are mislabeled. §3.6 states velocity-independent (w→∞) is 0.04 cm²/g, 0.2 is w=30, 0.8 is w=10. The abstract/table call 0.2 the velocity-independent limit. Thus σ/m(28)=166 (`:849`) is 166/0.2=830× as printed, but 166/0.04=4150×; the “27–49×” range (`:36`) using σ/m=5.43 at v=9 and 9.86 at v=40 (`:845`,`:851`) becomes 136–247×. Headline factors are off by ~5.

[ERR] `PAPER:11` vs `:111` — abstract says σ_eff exceeds 0.8 cm²/g by 3.6–23.7×. But 0.297²×2.85=0.251 cm²/g (`:111`), below 0.8; 3.6–23.7 is σ/m/0.8, not σ_eff. This contradicts the definition σ_eff=f_H²σ/m (`:94-98`).

[ERR] `PAPER:59` (also `:812`, `:2273`) — 0.052×54.6=2.84, not 0.156. αχ/α=6.8×10⁻⁷/9.2×10⁻⁸=7.39; squared=54.6; normalized σ/m(100)=0.052 gives 2.84. Also 0.156 at v=100 and 0.354 at v=29.4 imply σ∝v^−0.67 [ln(0.354/0.156)/ln(100/29.4)=0.67], not the stated v^−3.83 slope; with −3.83 and 0.156(100), σ(29.4)=16.9. Internally inconsistent.

[ERR] `PAPER:864` — one sentence says BLN24 hydrostatic analysis yields σ/m≳50; the next says BLN24 constrains mass/structure, not σ/m. `:34` and `:826` attribute the ≥50 to Elbert+2015. Contradictory provenance for the central Cloud-9 anchor.

[Q] `PAPER:102`/`:112` vs `:233` — at v=28 the paper sets σ_eff≈σ/m=166, but f_H=0.297 gives 0.297²×166=14.6 (`:233`). The “resonance dominance” exemption is asserted, not derived.

[Q] `PAPER:38` gives g_N/g_χ≲1.7×10⁻¹³, while `README.md:18` and `CURRENT.md:64` give <3×10⁻¹¹. Which is authoritative? Discrepancy 176×.

[OK] `PAPER:167`/`:184` — r_vir=[3(5×10⁹)/(4π·200·1.381×10⁻⁷)]^{1/3}=35.09 kpc; r_s=2.924 kpc; V_max=31.12 km/s; t_cross=2.924 kpc/31.12 km/s=92 Myr; 76/92=0.83. Verified.

[OK] `PAPER:111` — σ/m(15)=0.052(100/15)^1.93+174exp[−14.4²/(2·4.4²)]=2.02+0.82=2.85 cm²/g. Verified.

[OK] `PAPER:2104-2107` — 3.10×10⁻²²/9.4×10⁻⁴⁸=3.30×10²⁵; 1/√(3.3×10²⁵)=1.74×10⁻¹³. Arithmetic correct.

[OK] `PAPER:15`/`:2075` — for m_χ=1 GeV, ½μv² with μ=m_χ/2 gives 2.40 eV at 29.4 km/s, matching |E₀|=2.4 eV.
