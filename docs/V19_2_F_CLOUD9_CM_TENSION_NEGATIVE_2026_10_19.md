# v19.2-F Cloud-9 c-M Tension Test — v40.39 (2026-10-19)

## Summary

**Result: NEGATIVE.** v19.2-F canonical parameters (sigma_peak=174, f_H=0.297)
predict Cloud-9 is in **deep core collapse (tau = 16.3)**, which is INCONSISTENT
with the observed Cloud-9 c=4 (max-core, tau ~ 0.18 per Ohana+ 2026).

## What this means

The v19.2-F framework's effective cross-section at v=28 km/s is:
- sigma_m(v=28) = 174 * exp(-0.5 * ((28-29.4)/4.4)^2) = 165 cm²/g
- sigma_eff = f_H^2 * sigma_m = 0.297^2 * 165 = **14.6 cm²/g**

At this effective cross-section, the Balberg t_core for Cloud-9 (M=4.7e9, c=12,
V_max=30 km/s) is **0.84 Gyr**, giving tau = t_Hubble / t_core = **16.3** (deep
core collapse). Observationally, Ohana+ 2026 MCMC analysis finds Cloud-9 has
tau = 0.18 (max-core), which requires an effective cross-section roughly 30×
LOWER than v19.2-F's 14.6.

## Why this is a NEGATIVE result, not a "win"

Per the v19.1.5 honest framing (re196.docx), the script's R88(71) pre-claim
checklist explicitly acknowledges:

- (a) Does NOT contradict Ohana+ 2026 — both are internally consistent
      (different physical models, different parameters)
- (b) n_params=3, n_channels=1 — NOT overfitting
- (c) NEGATIVE result: v19.2-F's parameters are TOO STRONG for Cloud-9
- (d) Exploratory: Yang+ Eq. 5 polynomial is only valid for tau in [0, 1];
      v19.2-F's tau=16 is outside that range. Full N-body needed for
      deep-collapse c_200 prediction
- (e) RECOMMENDATION: Do NOT change §2.6a claim based on this. The §2.6a
      structural tension is REINFORCED, not resolved

## How to interpret the v19.2-F framework in light of this

v19.2-F's parameters (sigma_peak=174, f_H=0.297) are STRUCTURALLY INCONSISTENT
with Cloud-9 being in the max-core regime. The framework needs ONE of:
- (i) Lower sigma_peak (~50-100 instead of 174)
- (ii) Lower f_H (e.g., < 0.05)
- (iii) A different f_H(r) profile (NOT uniform 0.297)
- (iv) A merger-driven tau reset mechanism (Silverman+ 2026)

Per Ohana+ 2026: single-component SIDM with sigma/m = 483 cm²/g (no f_H factor)
puts Cloud-9 in max-core. v19.2-F's sigma_m=165 with f_H=0.297 gives
sigma_eff=14.6, which is 33× LOWER. The 33× factor is what pushes v19.2-F
into the deep-collapse regime.

## What is NOT broken

- The σ_eff = f_H^2 * σ_m observability relation (fundamental)
- The Balberg t_core formula (verified by T208/T212 review, used in Ohana+)
- The Yang+ Eq. 5 polynomial fit (only valid for tau in [0, 1])
- The v19.2-F multi-resonance architecture (Phase 44 σ_peak=174 is correct)

The negative result is about the SPECIFIC parameter choice (sigma_peak=174 +
f_H=0.297), not about the framework's mathematical structure.

## Files added in v40.39

- `scripts/v19_2_f_cloud9_cM_tension.py` (320 lines) — the analysis script
- `v0.3-prelim/data/results/v19_2_f_cloud9_cM_tension.json` — saved result
- `v0.3-prelim/tests/test_v19_2_f_cloud9_cM_negative.py` (5 regression tests)
- `scripts/review_prompt_v19_2_f_cloud9_cM_tension.txt` — Nemotron review prompt
- `docs/V19_2_F_CLOUD9_CM_TENSION_NEGATIVE_2026_10_19.md` (this file)

## Test count

- Before v40.39: 35/35 PASS (12 paper_claims + 3 TUCANA II + 7 physics + 4 Ohana+ baseline + 9 misc)
- After v40.39: **40/40 PASS** (added 5 v19.2-F Cloud-9 c-M negative-result tests)

## Pre-tag gate status

- Pre-tag gate: 7/7 PASS
- Round 13 self-check: 8/8 PASS
- arXiv fabrication check: PASS (Ohana+ 2608.04362 verified)
- R88(71) pre-claim checklist: COMPLETE in script main()
- R88(68) overfitting guard: 5 regression tests lock the negative result

## Next session

This result raises the question: is v19.2-F's f_H=0.297 a real prediction
of the multi-resonance framework, or a phenomenological placeholder? If it's
a placeholder, the framework needs a first-principles f_H(r) derivation
(Yang+ 2025 mass segregation, or T202 N-body) to put Cloud-9 in the right
regime. This is a candidate for v19.2-G next paper.
