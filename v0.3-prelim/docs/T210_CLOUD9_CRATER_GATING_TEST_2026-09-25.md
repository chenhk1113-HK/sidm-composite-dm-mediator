# T210 Gating Test + Path A2 Sharp Resonance Scan — Cloud-9 / Crater II / Antlia II

**Date:** 2026-09-25
**Trigger:** Cloud-9alternate.docx memo proposing Crater II + Antlia II as kinematic (more robust) alternatives to Cloud-9's hydrostatic inference, and a sharp-resonance scan as Path A2.
**Code:** `v0.3-prelim/code/t210_gating_test_crater_antlia.py` + `t210_path_a2_sharp_resonance_scan.py` + `t210_quick_sigma_eff_decompose.py`
**Results:** `v0.3-prelim/data/results/t210_gating_test_crater_antlia.json` + `t210_path_a2_sharp_resonance_scan.json` + `t210_path_a2_summary.json`

## 1. Gating Test Outcome — B (model fails Crater II + Antlia II)

The current Path F1 three-term σ_eff decomposition, evaluated under the borrowed prescription (f_H_cf = 0.85, f_H_cc = 0.5, σ_peak_HH_1 = 84.4, σ_peak_HL = 0.318, v_HL = 98.2, σ_0_LL = 0.0006), fails Crater II and Antlia II across all V_max interpretations:

| Scenario | Crater II σ_eff | z vs 30 cm²/g | Antlia II σ_eff | z vs 30 cm²/g |
|---|---|---|---|---|
| A: V_max = σ_los | 0.253 | 2.97 (FAIL) | 0.228 | 2.98 (FAIL) |
| B: V_max = √3·σ_los | 0.231 | 2.98 (FAIL) | 0.252 | 2.97 (FAIL) |
| C: V_max ≈ 15 km/s | 0.345 | 2.97 (FAIL) | 0.345 | 2.97 (FAIL) |
| D: V_max ≈ 28 km/s | 10.716 | 1.93 (FAIL) | 10.716 | 1.93 (FAIL) |

**The memo's critical caveat is resolved:** σ_eff in the current model peaks at 10.7 cm²/g around v=28 and drops to 0.23 cm²/g at v=5. Neither Crater II's nor Antlia II's kinematic constraint (σ/m ≥ 30-60 cm²/g) is satisfied at any V_max.

**Cloud-9 reference (memo comparison):** σ_eff(28) = 10.7 cm²/g vs floor 128 cm²/g → z = 3.91 (FAIL). This is the Cloud-9 vs dSph tension restated.

**dSph reference (memo comparison):** σ_eff(15) = 0.345 cm²/g vs ceiling 0.8 cm²/g → z = -11.37 (PASS). dSph is satisfied.

## 2. Path A2 — Sharp Resonance Scan

Tested whether moving v_HL (the heavy-light Lorentzian peak position) down to v=25-35 km/s and shrinking width_HL to 5-50 km/s could satisfy Cloud-9 + dSph simultaneously.

**Result: ZERO configurations pass both Cloud-9 AND dSph** across the 7 × 6 = 42 grid (v_HL ∈ {25, 28, 30, 35, 50, 75, 100}, width_HL ∈ {5, 10, 15, 20, 30, 50}).

The best configurations cluster at:
- σ_eff(28) ≈ 31 cm²/g (vs 128 floor, z = 3.23)
- σ_eff(15) PASS (dSph)
- σ_eff(100) ≈ 0.02 cm²/g (vs SPARC 0.193 target, z = -3.45 → SPARC FAILS)

**Trade-off is fundamental:** moving v_HL down to 28 satisfies Cloud-9's neighborhood (at the expense of never reaching the floor), but BREAKS SPARC because the heavy-light term no longer contributes at v=100.

## 3. Decomposition — what's in σ_eff(28)

Diagnostic run `t210_quick_sigma_eff_decompose.py` shows that σ_eff(28) is dominated by **f_H² × σ_HH_1(v=28) ≈ 0.5² × 84.4 ≈ 21.1 cm²/g**, plus the σ_HL cross-term (small, ~1 cm²/g).

To reach σ_eff = 128 at v=28, σ_peak_HL would need to be ~500 cm²/g — **physically implausible** (and would break the dSph ceiling at v=15).

**This is the structural ceiling:** the framework's σ_HH_1 Lorentzian peak of 84.4 is the dominant contributor at v=28, and even it can only push σ_eff to ~31. The 4× gap (31 vs 128) is unreachable without new physics.

## 4. Implications for the paper

### What the paper needs to acknowledge

**The multi-probe reframing the memo proposed does not work under the current framework.** Crater II and Antlia II, when evaluated against Path F1, fail the same way Cloud-9 does. Adding them as additional channels only multiplies the failure mode.

### What the paper CAN say (honest framing)

1. **Cloud-9 vs dSph tension is structural under Path F1.** σ_eff(28) cannot reach 128 cm²/g because the framework's σ_HH_1 Lorentzian peak (84.4 cm²/g) caps the heavy-heavy contribution at f_H² × 84 ≈ 21 cm²/g, and σ_peak_HL cannot bridge the gap without exceeding physical bounds.

2. **Crater II and Antlia II confirm the tension, not relax it.** At any V_max interpretation, σ_eff under borrowed mode reaches at most 10.7 cm²/g at v=28, which is 3× below Crater II's 30 cm²/g floor (z = 1.93-2.97 across scenarios).

3. **The 4 UV-completion no-go theorems + Path F1's σ_eff ceiling form a complete constraint map.** The framework describes 6-7 of 8 channels under borrowed prescription, fails Cloud-9 / Crater II / Antlia II / free fit at SPARC, and cannot unify the high-σ/m probes (Cloud-9 + Crater II + Antlia II + LSB) with the low-σ/m probes (dSph + UFD + SPARC + Cluster).

### What the paper CANNOT say

- "Multi-probe reframing strengthens the framework." It doesn't — it adds more failures.
- "Sharp resonance at v=28 unifies the model." It doesn't — Cloud-9 floor is unreachable.
- "Crater II is more accommodating than Cloud-9." It isn't, under Path F1. Both fail by similar factors.

## 5. Honest assessment

This session confirmed what Path 2 (gravothermal refutation) and Path 4 (KiSS-SIDM single-component) suggested: **the current framework cannot unify the high-σ/m and low-σ/m probes.** Three independent tests (gravothermal enhancement, sharp-resonance scan, multi-probe gating) all converge on the same structural ceiling.

The remaining options are:
- **Option A (paper-level):** Document the constraint map honestly. Add §10.4b (this finding) alongside §10.4a (gravothermal refutation). v18.40 standing = "framework describes 6-7 of 8 channels, but Cloud-9 vs dSph tension is structural across all multi-probe variations tested."
- **Option B (physics-level):** New physics required. The memo's Path B3 candidates (velocity-dependent cross-section with non-monotonic structure, separate environments, baryonic coupling) are the only routes forward. Each requires its own literature survey and validation campaign.
- **Option C (presentation-level):** Re-cast Crater II and Antlia II as upper limits rather than floor constraints. If the SIDM inference for these systems carries systematic uncertainties (tidal stripping, environment), the paper can argue the 60 cm²/g requirement is itself uncertain. This is Path B2 from the memo.

## 6. Files added this round

- `v0.3-prelim/code/t210_gating_test_crater_antlia.py` — Crater II + Antlia II gating test
- `v0.3-prelim/code/t210_path_a2_sharp_resonance_scan.py` — (v_HL, width_HL) grid scan
- `v0.3-prelim/code/t210_quick_sigma_eff_decompose.py` — σ_eff(28) decomposition diagnostic
- `v0.3-prelim/data/results/t210_gating_test_crater_antlia.json` — gating test results
- `v0.3-prelim/data/results/t210_path_a2_sharp_resonance_scan.json` — full scan results
- `v0.3-prelim/data/results/t210_path_a2_summary.json` — summary + best configs
- `v0.3-prelim/docs/T210_CLOUD9_CRATER_GATING_TEST_2026-09-25.md` — this writeup

## 7. Decision needed

The memo's Day 1-2 work is complete. Day 3 (sharp resonance scan) is also complete and confirms the framework cannot unify the probes. Per the memo's Day 4 recommendation:

> "Based on the resonance scan, decide between (a) presenting the resonance as a candidate unification route, or (b) accepting that the framework is a constraint map, not a unified model."

**Recommendation: option (b).** The framework is a constraint map. v18.40 should add §10.4b (this finding) and explicitly mark the unified-model ambition as closed under the current framework. Any future unification requires new physics (Option B) or new observational interpretation (Option C).

Awaiting direction.