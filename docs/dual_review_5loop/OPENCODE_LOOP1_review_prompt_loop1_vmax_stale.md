# OpenCode CLI Review

**Model:** `opencode/deepseek-v4.1-flash-free`  
**Generated:** 2026-10-22 09:28:18 China Standard Time  
**Duration:** 137.1s  
**Transport:** `opencode run --model <id>` (OpenCode free tier is CLI-only; direct API returns HTTP 403 FreeTierError)  
**Reviewer role:** second independent reviewer, different model family from the Nemotron/OpenRouter reviewer  

> **Status: UNVERIFIED SECOND OPINION.** This is one reviewer's critique. Every specific numerical claim below must be recomputed in Python before it is acted on -- the free-tier models fabricate plausible numbers. Compare against the Nemotron review: where they agree, the finding is likely real; where they disagree, that is the claim to compute first.

**Prompt source:** `scripts\review_prompt_loop1_vmax_stale.txt`

## Priority chain attempt log

| Model | Result | Seconds |
|---|---|---|
| `opencode/deepseek-v4.1-flash-free` | OK | 137.1 |

## Review

[ERR] T208 JSON is stale. JSON:7 gives V_max=24.7546 km/s; the corrected `r_max=2.1626 r_s` routine gives 31.12 (T208…py:51–77; paper:167). 24.7546 = √(G M_vir/r_vir) with r_vir=35092.9 pc (JSON:5), i.e. the retired virial approximation. Consequently JSON:10 σ_vir=0.2101 (correct 0.167) and JSON:15–16 t_cross=0.11552 Gyr and ratio=638.1 (correct 0.09189 Gyr and 802; paper:1170) are also stale.

[OK] t_core and the verdict survive. t=12.7/σ·(ρ_s/10⁻²)⁻¹·(r_s/10⁴)·(100/v), σ=0.052(100/v), so (100/v)/σ=100/0.052 is V_max-independent. Recompute: (12.7/5.2)(0.01/0.0096896)(2924.4/10⁴)(100)=73.71 Gyr, matching JSON:14 and paper:1162. Regenerate JSON anyway.

[OK] ρ_s: script formula equals (200/3)ρ_crit c³/[ln(1+c)−c/(1+c)] and reproduces 9.6896e−3 (JSON:8). The alternative (200/3)ρ_crit c is dimensionally wrong (would give 1.105e−4).

[ERR] Subhalo cross-check V_max=1.44765 (JSON:24) is likewise old √(GM/r_vir); corrected value is 1.925. `matches_T204:false` (JSON:29) is unexplained; JSON:26 t_core=1.973 Gyr vs T204 0.563 Gyr (T208…py:227).

[ERR] Cap inconsistency: 47.65 (paper:186) vs 47.71 (paper:189,192). From K=2.86×50=143.0, cap=143/3=47.67; both roundings cannot be right. Floor 50×(50/48.14)=51.94, so the EMPTY-window conclusion is robust.

[ERR] "~8.9e9 unit conversion" (gravothermal_yang2024.py:283–289,300) is not a unit factor. In cgs, σ[cm²/g]·ρ[g/cm³]·r[cm]=dimensionless; ×√(4πGρ)[s⁻¹] ⇒ s⁻¹, so 150C=112.5 already yields seconds (BM2 check: 15.77 Gyr). The 1.82 is BM2 N-body calibration, not units. [Q] The current paper text no longer prints 8.9e9; paper:1291 still calls 1.34e12 “empirically calibrated,” so the two conventions coexist.

[ERR] JSON:38 dSph_violation_factor=43.333=34.6667/0.8, not 50/0.8=62.5; it is unrelated to “3.6×” (=3.0/0.83).

[Q] Channel counts conflict: 1/8 and 5/8 (paper:19), 7/8 (1084), “4 of 7” (942,1707,1876) although 2266 says that framing is RETIRED, plus 9/10-channel sets (63,1707). These are different likelihoods/prescriptions, but the text does not keep them distinct.

[OK] 73.71/0.076=969.9 vs σ ratio 161.70/0.167=968.3: consistent within 0.2% for t∝1/σ.
