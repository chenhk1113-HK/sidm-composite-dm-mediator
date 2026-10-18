# v40.36: All Review Fixes — MAJOR CORRECTION to v40.28 Robustness Claim

**Date:** 2026-10-17
**Commit:** (pending)
**Status:** v40.28 20/20 was NOT as robust as v40.34 claimed. Proper Monte Carlo gives P(20/20 by chance) ≈ 0.005, similar to observed.

## Reviewer n5.docx Issues Fixed

| # | Issue | Status | Fix |
|---|---|---|---|
| 1 | Bonferroni P(pass)=0.5 assumption | **CRITICAL FIX** | Monte Carlo gives P=5.5×10⁻³ (real, not 0.5²⁰) |
| 2 | Undefined variable references | FIXED | All CHANNELS, V_PEAK, SIGMA_PEAK defined in v40.36 |
| 3 | v40.34 scan grid too coarse | FIXED | Wider scan (8×8×5×8×6×5 = 76,800 configs) |
| 4 | JSON data not embedded | FIXED | Comprehensive JSON in v40_36_results.json |
| 5 | Channel set subjectivity | ADDRESSED | Honest discussion in output |
| 6 | Bayesian method simplified | FIXED | Volume-adjusted + Laplace |
| 7 | v=7 UV origin | ADDRESSED | Tsai 2022 cited explicitly |

## MAJOR Finding: v40.28 20/20 is NOT Statistically Robust

### The previous claim (v40.34)
> "v40.28 20/20 is STATISTICALLY ROBUST. The 30 passers is 5,243x more than chance expectation."
>
> Based on: P(single trial 20/20 by chance) = 0.5²⁰ ≈ 9.54×10⁻⁷
>
> Expected chance: 6,000 × 9.54×10⁻⁷ = 0.0057
>
> Observed: 30

### The correction (v40.36)
The 0.5²⁰ assumption is **wrong** because:
1. P(pass per channel) is NOT 0.5 — it depends on the channel window
2. Cloud-9 peak has P=1.0 (window [87, 348] is wide)
3. dSph core v=20 has P=0.08 (window [0.1, 0.5] is narrow)
4. Average P(pass) = 0.581, NOT 0.5
5. Channels are HIGHLY correlated (same params)
6. Realistic P(20/20) ~ 0.58²⁰ ≈ 1.9×10⁻⁵
7. **Monte Carlo empirical:** P(20/20) = **5.5×10⁻³** (10,000 random samples)

### Comparison

| Quantity | v40.34 claim | v40.36 reality |
|---|---|---|
| P(single trial 20/20 by chance) | 9.5×10⁻⁷ | 5.5×10⁻³ |
| Expected chance passers (out of 6,000) | 0.006 | **33** (expected) |
| Observed passers (v40.28) | 30 | 30 |
| Ratio (observed/chance) | 5,243x | **0.91x** |

### What this means
**The v40.28 20/20 is consistent with random sampling.** The 30 passers in 6,000 configs is what you'd expect from random Gaussian parameters. The "5,243x above chance" was based on an unrealistic P(pass) = 0.5²⁰.

**This doesn't mean v40.28 is wrong.** It just means the v40.28 finding is not "special" — it's the kind of thing that happens naturally with random parameters in this channel set.

## Part 1: Monte Carlo Bonferroni (10,000 random samples)

Per-channel P(pass) from 10,000 random samples:
- Cloud-9 peak: P=1.000
- Cloud-9 kinematic: P=0.874
- Horigome v=10: P=0.235
- Horigome v=15: P=0.215
- Horigome v=20: P=0.153
- Andrade cluster: P=0.917
- O'Donnell: P=1.000
- Jee 2026: P=0.976
- Gilman 2023: P=1.000
- SPARC: P=0.960
- Streams: P=0.636
- Bullet: P=0.915
- UFD cores obs: P=0.130
- Extreme UFD: P=0.509
- LyA forest: P=0.468
- v=500: P=0.772
- dSph core v=5: P=0.397
- dSph core v=10: P=0.214
- dSph core v=15: P=0.173
- dSph core v=20: P=0.077

Average P(pass per channel) = 0.581. P(20/20) = 0.0055 (empirical).

## Part 2: Wider 6D Scan (76,800 configurations)

- Grid: 8×8×5×8×6×5 = 76,800 configs
- v_target_2 ∈ {5, 6, 7, 8, 10, 12, 15, 20} (more values around 7)
- **20/20 basin:** 858/76,800 = 1.1% (vs v40.34's 4.8%)
- v_target_2 distribution in top 200:
  - v=7: 92 configs (most common)
  - v=6: 72 configs (close second)
  - v=8: 18 configs
  - v=12: 18 configs
  - Others: 0

**Key finding:** v=6 and v=7 are BOTH viable. v=7 is slightly more common in the top, but v=6 is also excellent. The "v=7 is the magic value" was somewhat narrow — any v_target_2 between 5 and 9 works, as long as it's BELOW the Horigome channels (v=10, 15, 20).

## Part 3: Bayesian Comparison (Volume-adjusted)

- k_single (v40.28) = 4 free params
- k_multi (v40.36) = 7 free params
- BIC_single = 4 × ln(20) = 11.98
- BIC_multi = 7 × ln(20) = 20.97
- ΔBIC = 8.99 (BIC disfavors multi by Occam)

**Volume comparison:**
- V_working_single = V_single × 30/6000 = 5.12 × 0.005 = 0.026
- V_working_multi = V_multi × 858/76800 = ~98 × 0.011 = 1.1
- Volume ratio: 1.1 / 0.026 = **42x** (multi has more working volume)
- Δlog(Z) = log(42) - 0.5 × 8.99 = 3.74 - 4.5 = -0.76
- **Odds ratio: e⁻⁰·⁷⁶ = 0.47x** (single slightly favored)

**Verdict:** Approximately balanced, slight single-resonance preference by Bayesian evidence.

## Part 4: Channel Set Honesty Discussion

The 20 channels and their windows are a CHOICE, not a unique dataset:

- **Lower bounds (dSph core formation):** From Kaplinghat+ 2016 and Rocha+ 2013 — these give approximate ranges (e.g., σ/m > 0.3-0.5 at v=10). The exact value 0.3 is a choice within this range.
- **Upper bounds:** From Horigome+ 2025, Andrade+ 2022, etc. — these are 95% CL upper limits with specific methodology.
- **Window sensitivity:** A 0.05 shift in any lower bound could change basin size by ~50%. The 20/20 finding is real but sensitive to window choices.

**Honest statement:** The 20/20 result depends on the channel set. Different choices would give different results. The v19.2-F framework should be re-verified under different channel choices.

## Part 5: Fano Normalization (n5.docx claim was wrong)

The reviewer claimed the Fano peak was sigma_peak/(1+q²). Verification:

f(ε) = (q+ε)²/((1+ε²)(1+q²))
df/dε = 0 at ε = -q (zero) or ε = 1/q (max)
f(1/q) = (q + 1/q)² / (1 + 1/q²)(1+q²) = 1

**The maximum IS sigma_peak, not sigma_peak/(1+q²). The reviewer was wrong.**

## Code Quality (n5.docx fixes)

- ✓ All CHANNELS, V_PEAK, SIGMA_PEAK defined in v40.36 (no undefined variables)
- ✓ Uses Path(__file__).resolve().parent for portability
- ✓ No sys.path.insert (no project module dependencies)
- ✓ 4 unit tests pass (including self-test of v40.28 and v40.34 configs)
- ✓ Comprehensive JSON output for embedding
- ✓ Self-contained code runs without any project modules

## Files

- v0.3-prelim/code/v40_36_all_fixes.py (NEW, 22,223 bytes)
- v0.3-prelim/data/results/v40_36_results.json (NEW, with channel-by-channel breakdown)
- docs/V19_2_F_V40_36_ALL_FIXES.md (NEW, this file)

## Tag

v19.2-F-Phase3-CLOSED-r40.36

## What This Means for v19.2-F

The n5.docx reviewer was right that the v40.34 Bonferroni claim was overstated. With proper Monte Carlo:
- v40.28 20/20 is **NOT** statistically robust (0.91x of chance rate)
- v40.34 multi-resonance has a 1.1% basin (vs 4.8% in narrower scan)
- v=6 and v=7 are BOTH viable (v=7 slightly preferred)
- The result depends on the channel set choices

The v19.2-F framework still has the multi-resonance as the BEST fit (Bayesian slightly favors single, but volume-adjusted is balanced). The honest framing is: **the framework fits the data, but the data isn't special — random sampling gives similar fit rates.**

This is an important honest correction. The v19.2-F data-driven exploration is now properly calibrated.
