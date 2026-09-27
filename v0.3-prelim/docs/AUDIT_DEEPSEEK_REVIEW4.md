# Audit — "Deepseek Review 4.docx" (2026-09-21)

User asked: critically consider whether useful.

This is the fourth DeepSeek review. Major issues identified:

---

## Priority 1 (CRITICAL) — Abstract vs Introduction ingredient lists contradict

**Reviewer claim:** The abstract's four ingredients are different from the
introduction's. Abstract says:
1. Velocity-dependent Breit-Wigner cross-section with two resonances
2. Multi-resonance KK-tower mass spectrum (T163 best fit)
3. Multi-channel consistency checks
4. Bayesian evidence comparison against constant σ/m

Introduction says:
1. Multi-resonance SIDM (one dominant BW peak + three bookkeeping nodes)
2. Two-component asymmetric DM
3. Gravothermal core-collapse selection
4. Gaussian Breit-Wigner profiles

**Verification:** Confirmed. The abstract describes methodology; the
introduction describes physics ingredients. This is a serious internal
contradiction.

**Action:** Rewrite abstract's ingredient paragraph to match the
introduction's list (which is the physics).

---

## Priority 2 (CRITICAL) — g_h_SM has three different values in the paper

**Reviewer claim:**
- Abstract: g_h_SM = 0.00040
- §10.3 table "T190 v2": g_h_SM = 0.001
- §10.12 predictions: g_h_SM = 0.002
- §10.3 table "T192 (thermal-avg)": g_h_SM = 0.00040

If σ_SI scales as g_h_SM², reducing g_h_SM by 5× from 0.002 to 0.00040
reduces σ_SI by 25× — the predicted null at 5×10⁻⁴⁸ cm² would become
~2×10⁻⁴⁹ cm².

**Verification:** Confirmed. Need to fix:
- §10.12 (testable predictions) — σ_SI prediction
- T189 (B-factory rates) — needs to use 0.00040

**Action:** Use 0.00040 consistently everywhere. Update §10.12 direct-
detection prediction: σ_SI = 5×10⁻⁴⁸ × (0.00040/0.002)² = 2×10⁻⁴⁹ cm².

---

## Priority 3 (HIGH) — §10 numbering mid-edit

**Reviewer claim:** Header says §10 has 5 subsections but content uses
§10.1 through §10.12. The renumbering was started but not completed:
- Old §10.10 content (T184/T185) is now labeled §10.3 in sub-header,
  but continues with "§10.3.1 — Thermal relic density UV completion"
- Old §10.8 (DeepSeek verifications) still labeled §10.8
- Summary of §10 UV no-go theorems still §10.11
- §10.12 (testable predictions) still numbered §10.12

**Fix:** Complete the renumbering. The intended structure:
- §10.1 General framework + four no-gos
- §10.2 One-mediator UV completions ruled out (T120.10, T120.16, T130, T131, T184)
- §10.3 Two-mediator candidate (T185/T190/T192)
- §10.4 Cloud-9 robustness (T165-T172, T179, T191)
- §10.5 EFT target map + testable predictions

Update all internal cross-references (e.g., "see §10.10" → "see §10.3").

---

## Priority 4 (HIGH) — §10.5 EFT target map uses Phase 44, but abstract uses T163

**Reviewer claim:** §10.5 table uses σ/m(28) = 128.13 cm²/g and Phase 44
defaults. But abstract and §10.3 reference the T163 KK-tower best fit.

**Fix:** Either update §10.5 to use T163 values, OR explicitly label
§10.5 as "Phase 44 baseline target map."

---

## Priority 5 (MEDIUM) — T184 in §10.3 (wrong section)

**Reviewer claim:** Content under "§10.3 Two-mediator candidate" header
starts with T184 (one-mediator negative result) before getting to
T185/T190/T192. This breaks the logical flow.

**Fix:** Move T184 to §10.2 (where it belongs, with the four other
no-gos).

---

## Priority 6 (MEDIUM) — T192 thermal average needs verification plot

**Reviewer claim:** Paper should demonstrate the thermal averaging more
explicitly:
- Plot ⟨σv⟩(T) vs. T around T_F, showing the resonance peak at v_res = 0.185c
  is within the thermal window
- State the fraction of ⟨σv⟩ from the resonance region (resonance recovery factor)
- Cross-check with micrOMEGAs 6.0 (ref [29c] already in bibliography)

**Fix:** Write T193_thermal_avg_visualization.py that:
- Computes d⟨σv⟩/dv_rel vs v_rel
- Identifies resonance region contribution
- Outputs plot data (or saves PNG)

---

## Priority 7 (LOW) — Abstract mentions T163, but Phase 44 elsewhere

**Reviewer claim:** Abstract cites T163 best fit but §2 and §3 use Phase
44 defaults. The relationship between Phase 44 and T163 is not stated.

**Fix:** Either:
(a) Add a sentence in §2 or §3 explaining T163 is a specific KK-tower
best fit within the Phase 44 framework
(b) Remove T163 reference from abstract

---

## Priority 8 (LOW) — Abstract's §10 cross-reference is wrong

**Reviewer claim:** Abstract says "see §10.10" but section is now
labeled §10.3.

**Fix:** Update after completing Priority 3 renumbering.

---

## Physics Verification (reviewer's positive assessment)

The T192 thermal averaging is **physically sound**:
- At δ = 0.43%, v_res = √(8δ) = 0.185c
- T_F ≈ m_χ/20 to m_χ/25, giving v_th ~ √(3/x_F) c ≈ 0.35-0.4c
- ~10-20% of annihilating pairs have v_rel ≤ 0.185c
- BW enhancement at resonance is O(100×) relative to off-resonance
- Thermal average is dominated by this tail
- g_h_SM reduction from 0.001 → 0.00040 (2.5×) is consistent with
  resonance recovery factor O(2-3×) relative to single-velocity estimate

**But:** the paper should show the explicit thermal integral. A plot of
d⟨σv⟩/dv_rel would settle this.

---

## Overall Assessment (reviewer's words)

| Concern | Status |
|---|---|
| Unitarity of Cloud-9 peak | ✅ Resolved (T174) |
| v² vs v-space ambiguity | ✅ Quantified (T176) |
| Proper Bayesian evidence | ✅ Semi-informative Bayes factor (T177) |
| f_H = 0.61 consequence | ✅ Documented honestly |
| AIDA-TNG systematic | ✅ Integrated |
| Two-mediator BW off-resonance | ✅ Fixed by T192 thermal averaging |
| Internal consistency of BIC/Bayes | ✅ Unified statement (§10.8) |
| UV completion status | ✅ Summary table (§11) |

**Remaining issues are editorial, not physics:**
- Mid-edit §10 renumbering
- Abstract/introduction ingredient mismatch
- g_h_SM inconsistency across sections
- Missing thermal-average verification plot

Reviewer says: "physics is defensible, honesty is exceptional, contributions
are genuine." "The single most important thing now: complete the edit."

---

## Plan (per reviewer's 6-day schedule)

1. **Day 1**: Complete §10 renumbering (all sections, all cross-references)
2. **Day 2**: Reconcile g_h_SM = 0.00040 everywhere; update §10.12 predictions
3. **Day 3**: Rewrite abstract's "four ingredients" to match the introduction
4. **Day 4**: Add the thermal-averaging verification plot to §10.3
5. **Day 5**: Update §10.5 EFT target map to use T163 (or explicitly label Phase 44)
6. **Day 6-7**: Full read-through for cross-references and consistency

## Honesty notes

1. The abstract's "four ingredients" mismatch is real and needs fixing.
2. The g_h_SM inconsistency is real (3 different values).
3. The §10 renumbering was started in commit `76d31f4` but not completed.
4. The T192 thermal average is correct but lacks visualization.

After fixes, paper is ready for PRD/JCAP submission with mixed-verdict framing.