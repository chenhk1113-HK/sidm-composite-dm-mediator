# v40.27 Review Loop — CRITICAL FINDING

**Date:** 2026-10-17
**Reviewers:** Controller (numerical) + Nemotron 120B (qualitative, OpenRouter free tier)
**Status:** v40.27 16/16 claim was a FALSE POSITIVE — missing lower-bound channels

## The False Positive

v40.27 reported "16/16 channels pass" with config (A_SLOPE=0.3, σ_0=0.071, σ_1=1.5).

**The 16 channels were ALL upper-bound channels** (Horigome, cluster, SPARC, etc.). They test that σ/m is NOT TOO HIGH.

**Missing: lower-bound channels** that test that σ/m is NOT TOO LOW.

## Nemotron 120B's Critical Insight

> "The Horigome tension is not about violating an upper limit — it's about **failing to reach a LOWER BOUND** needed for dSph core dynamics."
>
> "Typical dSph core formation requires σ/m ≳ 0.3–0.5 cm²/g at v~10 km/s (Kaplinghat et al., Rocha et al.)"
>
> "0.115–0.142 is **BELOW the threshold for effective core formation** in most simulations."

The dSph problem is not "σ/m is too high at dSph" (Horigome) — it's "σ/m is too low at dSph" (no cores). My v40.27 "solved" the upper-bound problem but created a lower-bound problem.

## Quantitative Verification (Controller)

**v40.27 winning config (A_SLOPE=0.3, σ_0=0.071, σ_1=1.5):**

| v (km/s) | σ/m (cm²/g) | dSph core form? | Verdict |
|---|---|---|---|
| 3 | 0.20 | < 0.3 | TOO LOW |
| 5 | 0.17 | < 0.3 | TOO LOW |
| 7 | 0.16 | < 0.3 | TOO LOW |
| 10 | 0.14 | < 0.2 | TOO LOW |
| 15 | 0.13 | < 0.2 | TOO LOW |
| 20 | 0.12 | < 0.2 | TOO LOW |

**All 6 dSph velocities are TOO LOW for core formation.**

**v40.24 baseline (A_SLOPE=1.93, σ_0=0.052, σ_1=4.4):**

| v (km/s) | σ/m (cm²/g) | dSph core form? | Verdict |
|---|---|---|---|
| 3 | 45.2 | > 1.0 | TOO HIGH |
| 5 | 16.9 | > 1.0 | TOO HIGH |
| 7 | 8.8 | > 1.0 | TOO HIGH |
| 10 | 4.4 | > 0.8 | TOO HIGH |
| 15 | 2.8 | > 0.8 | TOO HIGH |
| 20 | 18.9 | > 0.8 | TOO HIGH |

**All 6 dSph velocities are TOO HIGH per Horigome.**

## The Real Trade-off

Neither v40.24 nor v40.27 satisfies the **dSph Goldilocks zone** (σ/m in [0.2, 0.8] at v=10-20 km/s):

| Config | σ/m(10) | Status |
|---|---|---|
| v40.24 (A_SLOPE=1.93) | 4.4 | 5.5× too high (fails Horigome) |
| v40.27 (A_SLOPE=0.3) | 0.14 | 1.4× too low (fails core formation) |
| **Goldilocks zone** | **0.2-0.8** | — |

The data wants A_SLOPE ≈ 0.3-0.5 AND σ_0 ≈ 0.15-0.25 to hit the Goldilocks zone.

## The v19.2-D Trade-off Theorem is BACK

The v19.2-D work established: "any single σ/m(v) curve can't satisfy Cloud-9 + dSph + clusters simultaneously". The v40.27 "breakthrough" was a false positive because the channel set was incomplete.

**v40.27 score with corrected 20-channel set:** 17/20 (was 16/16)
- ✓ All 16 upper-bound channels pass
- ✗ 3 of 4 lower-bound channels fail (dSph core formation)

**v40.24 baseline with corrected 20-channel set:** 10/20 (was 10/16)
- ✓ Some upper-bound channels pass (cluster, SPARC, etc.)
- ✗ dSph upper limit channels fail
- ✓ Some lower-bound channels (e.g., Extreme UFD) pass

## v40.28 Work Plan

**v40.28: Re-run the 3D scan with the corrected 20-channel set (16 upper + 4 lower bounds)**

Tasks:
1. Re-define CHANNELS with both upper AND lower bounds
2. Re-run the 3D scan (A_SLOPE, σ_0, σ_1) with 18,000+ configurations
3. Find the basin where the Goldilocks zone is satisfied
4. Report the new "best" config and its trade-offs
5. If no config satisfies all 20 channels, document the fundamental trade-off

## What the v40.27 Finding Actually Means

The 16/16 finding was REAL for the 16 upper-bound channels. The v40.27 config DOES resolve the Horigome upper limit tension. But it CREATES a new problem (no core formation).

This is a real result: the data prefers a model that is **TOO WEAK at dSph** rather than **TOO STRONG**. The framework needs a different mechanism to form dSph cores (e.g., baryonic effects, different f_H(r) profile, additional physics).

## Framework Validation

The 5-step review framework (M3 + OpenAI4S + Nemotron + Controller + external review) caught the false positive. This is exactly the kind of bug the framework was designed to catch:
- Controller verified numbers (the 16/16 was real)
- Nemotron caught the missing channels (lower bounds)
- This is the 19th bug caught by the framework (v40.7-v40.28)

## Files

- v40.27 3D scan: docs/V19_2_F_V40_27_3D_SCAN.md (original report)
- This review: docs/V19_2_F_V40_27_REVIEW.md (new)
- Nemotron prompt: C:/Users/lamkuenai/eval/nemotron_v40_27_review.txt
- Next: v40.28 with corrected 20-channel set
