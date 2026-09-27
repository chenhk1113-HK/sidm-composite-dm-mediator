# T101.4 Decision Gate Report

**Date**: 2026-09-19
**Branch**: wip/T101-partial-wave
**HEAD**: <commit>
**Path**: (a) Phase 44 re-fit — keep v1.8 form, refit data

## Honest Finding (load-bearing)

During T101.4 evaluation I discovered a **factor-of-2 bug** in the kinematics formula used by the test suite. This bug has masked the actual dSph tension magnitude in the paper.

### The bug

The file `v0.3-prelim/tests/test_physical_constraints.py` line 52 builds resonances with:

```python
E_R_eV = 0.5 * m_chi_eV * (v_cm_s / c) ** 2  # INCORRECT
```

The CORRECT relativistic kinematics for equal-mass scattering is:

```python
E_R_eV = 0.25 * m_chi_eV * (v_cm_s / c) ** 2  # CORRECT
```

This is because the relative velocity in the CM frame is `v_rel / 2`, so:
`E_cm = (1/2) m_red (v_rel)^2 = (1/2)(m_chi/2)(v_rel)^2 = (1/4) m_chi v_rel^2`

### Effect of the bug

| Quantity | Test version (WRONG) | Correct | Difference |
|---|---|---|---|
| σ/m(v=30) | 7.54 cm²/g | **160.62 cm²/g** | 21.3× |
| Paper's "38× dSph violation" | matches | actually **803×** | 21× |
| σ/m(v=29) | 6.70 cm²/g | 183.70 cm²/g | 27× |
| σ/m at v_peak | ~0.9 | 196.3 | ~218× |

The bug moves the BW resonance peak away from v=29-30 (where v_target=29 with E_R wrong → peak at lower v). With correct E_R, the peak coincides with v=29-30, putting huge σ/m in the dSph velocity range.

### Where the bug originated

The bug was introduced in commit `259275a` (Layer D extended anchors test) when the anchor file was created. The anchor `dsph_v30_actual_upper_limit` claims "Phase 44 actual: sigma/m(v=30) ~ 7.5 cm²/g", which only holds under the buggy kinematics. The anchor file was calibrated to the buggy formula and then propagated as if correct.

The paper v1.8 §3.6 cites "σ/m(v=30) ≈ 7.5 cm²/g, factor of ~38×" — this is **based on the buggy formula** and is INCORRECT.

## Decision Gate Evaluation (with correct kinematics)

| Criterion | Required | Actual (correct E_R) | Pass? |
|---|---|---|---|
| Peak σ/m | ≥ 50 cm²/g | 196.3 | ✅ PASS |
| Cloud-9 anchor σ/m(v=28) | ≥ 50 | 100.07 | ✅ PASS |
| Peak position | ~41 km/s | 29.4 km/s | ⚠️ at v_target, not at v_peak=41 |
| dSph upper limit σ/m(v=30) | < 0.2 | 160.62 (**803×**) | ❌ FAIL |

## Interpretation

**T101.4 path (a) — Phase 44 re-fit — does NOT resolve the dSph tension.** The re-fit with the existing parameterization form gives the same results as the original Phase 44 fit (it's the same functional form). The actual dSph tension is **803×, not 38× as the paper claims**.

The Cloud-9 anchor (σ/m(v=28) = 100) is genuine — but it's at the kinematic v_target, not at v_peak = 41. The peak σ/m at v_peak = 29 is 196 cm²/g, NOT at v=41.

## Recommendation: T101.4 STOP HERE

Per plan2.docx Reviewer1: "If criteria 1-3 met → continue to T100 + T102. Otherwise → stop, keep v1.8."

**Only 1.5 of 4 criteria pass** (peak height and Cloud-9 anchor; peak position partially). The dSph tension is 21× worse than the paper claims.

### Three paths forward

**(α) Stop here, fix paper** — correct the §3.6 dSph tension claim from 38× to 803×, fix the peak location from "v_peak ≈ 41 km/s" to "v_peak = v_target ≈ 29 km/s". Keep v1.8 with corrected numbers.

**(β) Tighten the v_target BW** — narrow gamma_frac from 0.184 to ~0.05 to reduce σ/m at v=30 below 1 cm²/g. This breaks Cloud-9 (σ/m at v=28 drops from 100 to ~1). Not viable.

**(γ) Move v_target to higher v** — try v_target ≈ 50-60 km/s, which would put the BW peak out of the dSph velocity range. This requires re-fitting Cloud-9, JVAS, and SPARC data simultaneously. Probably 2-3 weeks. May or may not succeed.

**Recommended: path (α) STOP and FIX PAPER** — the framework is honest about its limitations. Correcting the 38× → 803× number is more honest than masking it. The paper is then appropriate for a "mixed-verdict" venue (PRD/JCAP/JHEP) with the actual tension quantified.

## What T101 produced

| Sub-task | Status | Output |
|---|---|---|
| T101.1: infrastructure | ✅ DONE | partial_wave_sigma.py (~440 lines) |
| T101.2: Born validation | ✅ DONE | 7 tests, ratio 1.008 |
| T101.3: BW profile + honest finding | ✅ DONE | 5 tests + additive form documented |
| T101.4: decision gate | ✅ DONE | 4 tests + bug discovery + paper correction needed |

**The T101 partial-wave infrastructure is complete and correct** (verified via Born approximation). It does NOT replace the phenomenological multi-resonance model — the solver matches Born in the weak-coupling limit and does not generate resonances from Yukawa scattering alone. The Phase 44 architecture is genuinely phenomenological, not first-principles.

**The T101.4 evaluation uncovered a real bug in the test suite** (factor-of-2 in E_R formula) that masked the actual dSph tension magnitude.

## Files produced

- `v0.3-prelim/code/partial_wave_sigma.py` — partial-wave σ/m solver (440 lines)
- `v0.3-prelim/tests/test_t101_partial_wave.py` — 7 tests (T101.2)
- `v0.3-prelim/tests/test_t101_resonances.py` — 5 tests (T101.3)
- `v0.3-prelim/tests/test_t101_decision_gate.py` — 4 tests (T101.4) + bug documentation

## Next steps (T101.5+ blocked pending user decision)

Per the decision-gate logic: STOP at T101.4 and report. User should decide:

1. Accept the bug discovery and fix paper v1.8 → v1.9 with corrected numbers
2. Pursue path (γ) — refit with v_target > 50 km/s
3. Stop T101 entirely and keep paper v1.8 (with bug as known limitation)
