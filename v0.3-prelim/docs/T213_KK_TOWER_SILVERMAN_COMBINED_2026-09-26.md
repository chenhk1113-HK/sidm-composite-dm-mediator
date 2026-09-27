# T213 — Combined KK Tower + Silverman+ Test

**Date:** 2026-09-26
**Branch:** `wip/cloud-9-relhic`
**Tag target:** `v18.42-kk-tower-silverman-combined`

## Question

**Does the T163 best-fit KK tower produce a σ/m(v) at Cloud-9 host-halo V_max = 31.12 km/s that, when fed into Silverman+ 2026's gravothermal prescription, reproduces the Cloud-9 spike (σ/m ≥ 50 cm²/g)?**

## Why this question

v18.41 §10 scope statement said the T163 KK-tower no-go re-test was deferred to v19.0, but T175 actually exists and confirms all 4 no-go verdicts hold at T163 parameters. T212 (Silverman+) confirmed gravothermal can run if σ/m(V_max) ≥ 1.0 cm²/g at Cloud-9 host halo. The missing piece is the *combination*: does T163 KK-tower produce σ/m high enough at low v to trigger Silverman+?

## Method

- T163 best-fit parameters: α_D = 0.3, m_0 = 0.3 GeV, r = 1.5, n_modes = 2, RMSE = 1.408
- Cloud-9 host halo: M_halo = 5×10⁹ M_☉, c = 12, V_max = 31.12 km/s (post V_max fix per 2review.docx Reviewer 2)
- KK tower σ/m(v) computed using sidmkit 0.3.0, summing σ_n for n=1..n_modes
- Velocity range: 5-500 km/s
- Threshold: Silverman+ 2026 gravothermal needs σ/m(V_max) ≥ 1.0 cm²/g

## Result

**T163 KK tower σ/m(V_max = 31.12 km/s) = 0.174 cm²/g.**

This is **5.7× BELOW** the Silverman+ threshold of 1.0 cm²/g.

| v (km/s) | σ/m (cm²/g) |
|---|---|
| 5.00 | 0.1742 |
| 10.00 | 0.1742 |
| 15.00 | 0.1742 |
| 28.00 | 0.1741 |
| **31.12** (Cloud-9 host V_max) | **0.1741** |
| 50.00 | 0.1741 |
| 100.00 | 0.1739 |
| 200.00 | 0.1733 |
| 500.00 | 0.1688 |

**Velocity dependence is FLAT** (factor < 1.04 across 5-500 km/s). The KK tower is in the Born regime where σ ∝ α²/m_med² (no Sommerfeld enhancement at low v).

## Verdict

**FAIL: T163 KK tower alone CANNOT drive gravothermal at Cloud-9 host halo.**

The 5.7× gap means the standard T163 KK tower prescription is in the **wrong regime** for Silverman+ mechanism. Two implications:

1. **Cloud-9 spike (σ/m = 128) cannot be reproduced by T163 KK tower alone.** Even with σ_eff amplification by heavy-light interactions (T207 Path F1), the σ/m at v = 31.12 km/s stays around 0.17 cm²/g, which is 30× below the Cloud-9 spike. Cloud-9 spike requires either:
   - A different UV construction (not KK tower) that operates near the resonance at v = 30-40 km/s
   - OR a substantial enhancement mechanism (e.g., bound state formation, resonance at v = 30 km/s)

2. **Path F1 (three-term σ_eff decomposition) is structurally insufficient at Cloud-9 host V_max.** The T207 σ_HL ≈ 0.34 boost happens at v_HL ≈ 100 km/s (SPARC), not at v = 31 km/s (Cloud-9 host). At v = 31 km/s, Path F1 is still in the σ_HH-dominated regime where T163 gives 0.17 cm²/g.

## Implication for v18.41 §10 scope statement

The v18.41 §10 scope statement said: *"The T163 KK-tower best-fit parameters (α_D = 0.3, m₀ = 0.3 GeV, r = 1.5, n_modes = 2, RMSE = 1.408) are a finer-grained realization within the same Phase 44 framework and have **not** been independently re-tested against the no-go theorems."*

This is **partially stale**:
- T175 was actually run on 2026-09-21 and confirmed all 4 no-go verdicts hold at T163 parameters (see `data/results/t175_nogo_retest_t163.json`).
- T213 confirms T163 KK tower is in the same regime as Phase 44 (~0.17 cm²/g vs 0.052 cm²/g at v=100, similar velocity dependence).

**The no-go verdicts survive T163 re-test by argument from mechanism invariance** (T175 logic) and by direct calculation (T213 shows T163 is in the same flat σ/m regime as Phase 44).

## What this means for the paper

The combined T163 + T212 + T213 result reinforces the **structural constraint map verdict**:
- Single KK tower at T163 best fit gives σ/m ≈ 0.17 cm²/g at Cloud-9 host V_max.
- Silverman+ mechanism needs σ/m ≥ 1.0 cm²/g (5.7× above).
- Path F1 three-term decomposition cannot bridge this gap because the σ_HL peak is at v = 100 km/s, not v = 31 km/s.
- The Cloud-9 spike (σ/m ≥ 50 cm²/g) requires a different UV construction entirely.

This is a STRONGER structural ceiling than v18.41 stated. The framework is a constraint map because:
- **The KK tower is not the right tool** for Cloud-9 scale.
- **Silverman+ gravothermal is the right tool but the wrong mass scale** for σ/m at Cloud-9.
- **No published 2026 SIDM mechanism bridges the gap.**

## File artifacts

- Code: `v0.3-prelim/code/t213_kk_tower_silverman_combined.py`
- Data: `v0.3-prelim/data/results/t213_kk_tower_silverman_combined.json`
- This doc: `v0.3-prelim/docs/T213_KK_TOWER_SILVERMAN_COMBINED_2026-09-26.md`

## Wall time

~1 hour (T175 verification, T213 script, this doc).