# OpenCode CLI Review

**Model:** `opencode/deepseek-v4.1-flash-free`  
**Generated:** 2026-10-22 09:27:44 China Standard Time  
**Duration:** 102.4s  
**Transport:** `opencode run --model <id>` (OpenCode free tier is CLI-only; direct API returns HTTP 403 FreeTierError)  
**Reviewer role:** second independent reviewer, different model family from the Nemotron/OpenRouter reviewer  

> **Status: UNVERIFIED SECOND OPINION.** This is one reviewer's critique. Every specific numerical claim below must be recomputed in Python before it is acted on -- the free-tier models fabricate plausible numbers. Compare against the Nemotron review: where they agree, the finding is likely real; where they disagree, that is the claim to compute first.

**Prompt source:** `scripts\review_prompt_loop5_sigma_window_channels.txt`

## Priority chain attempt log

| Model | Result | Seconds |
|---|---|---|
| `opencode/deepseek-v4.1-flash-free` | OK | 102.4 |

## Review

[ERR] Stale JSON `V_max`. `json:7` gives 24.754551 km/s. That is the old virial approximation: sqrt(4.3009e-3 × 5e9 / 35092.9) = 24.75 km/s (`json:3,5`; G from `py:70`). The current script (`py:72-81`) uses `r_max = 2.1626 r_s` (`py:73`); with r_s = 2924.408 pc (`json:6`), M(<r_max)/M_vir = 0.2848, giving V_max = sqrt(4.3009e-3 × 1.424e9 / 6324.5) = 31.12 km/s. Paper `PAPER_V1_DRAFT.md:1162,167` uses 31.12. So the JSON predates the Reviewer-2 fix.

[OK] t_core is unchanged by the correction. `py:97,104`: t_core = 12.7/σ(V_max) × (ρ_s/1e-2)^-1 × (r_s/1e4) × (100/V_max), and `py:122` gives σ(V_max) = 0.052(100/V_max)^1.0. Thus t_core ∝ (V_max/100)(100/V_max) = 1. Recomputing both ways gives 73.71 Gyr: `json:14` = 73.71088497; `PAPER:1170` = 73.71. The verdict survives (`json:17-18`; `PAPER:1162`). This is why the stale JSON was not caught.

[ERR] But the V_max-dependent JSON fields are stale and disagree with the paper: σ(V_max) = 0.210062 (`json:10`) should be 0.052×100/31.12 = 0.1671 (`PAPER:1162`); t_cross = 0.115516 Gyr (`json:15`) should be r_s/V_max = 3.0857e13×2924.408/31.12/3.1557e16 = 0.09189 Gyr; t_core/t_cross = 638.10 (`json:16`) should be 73.71/0.09189 = 802, which is what `PAPER:1170` already quotes. The JSON and paper are inconsistent.

[ERR] The subhalo block is stale too: V_max = 1.447655 (`json:24`) is again virial-only; the corrected function gives 1.924 km/s. Then σ(V_max) = 3.59202 (`json:25`) becomes 2.702, and t_cross = 0.092413 (`json:27`) becomes 0.0695 Gyr. t_core = 1.97342 (`json:26`) is invariant; `matches_T204:false` (`json:29`) remains false.

[OK] V_max-independent fields are correct: 0.185714 at v=28 (`json:11`), 0.346667 at v=15 (`json:12`), 18.5714/34.6667 enhanced (`json:33-34`), 43.333 dSph factor (`json:38`), and t_core/t_Hubble = 73.7109/13.8 = 5.341 (`json:17`).

[Q] `py:159` computes t_cross with a dimensionally wrong expression, overwritten at `py:166`; confirm nothing downstream reads it.

[Q] The invariance holds only for a_slope = 1.0 (`py:38`); `PAPER:164` elsewhere uses 1.93. Is T208's 1.0 the intended baseline?

[Q] `json:29` says the 10^6 M_sun cross-check does not match T204. Should this be resolved before citing the cross-check?
