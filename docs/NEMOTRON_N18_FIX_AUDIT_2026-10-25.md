# Independent Reviewer Audit — n18 review-response fix set

**Reviewer:** Nemotron 550B (`nvidia/nemotron-3-ultra-550b-a55b:free` via OpenRouter), delegated as an
independent reviewer with no access to the controller's reasoning.
**Date:** 2026-10-25
**Audit target:** the n18.docx review-response round (fixes F1–F9) in the SIDM v19.2-F paper project.
**Repository:** `C:\Users\lamkuenai\projects\sidm-composite-dm-mediator` (branch `wip/v19.2-F-init`)

The reviewer's verdict on each numbered claim, plus the additional findings it raised, is reproduced
verbatim below. The controller's independent adjudication of those additional findings is in
`docs/dual_review_5loop/SIDM_ROUND5_CONSOLIDATED_FIXES_v1.1_2026-10-25.md` §13.7.

---

**CLAIM 1 — VERIFIED**  
Paper line 102: `For **0 of 8** halos, |σ_HL| < 0.05 cm²/g` — grammatically correct (comma, no dangling “is”). JSON `_derived_ranges.n_halos_abs_sigma_HL_below_0.05` (line 223) = `0`. Matches.

**CLAIM 2 — VERIFIED**  
Paper line 102: `σ_HL = −0.534 cm²/g, indicating an **internal inconsistency` — punctuation correct (comma after `cm²/g`, space before `**internal`). JSON `_derived_ranges.sigma_HL_cm2_per_g.max` (line 220) = `-0.5340265143981119`; rounded to `−0.534`. Matches.

**CLAIM 3 — VERIFIED**  
Paper lines 161–164 (post-fix): `the ratio derivation changes and the σ_1 = 4.4 baseline headline value 7.5×10⁻¹² holds under the σ_1 = 4.4 phenomenological width.` Restored subject `the σ_1 = 4.4 baseline headline value` per fix script (apply_n18_review_fixes.py lines 174–176). The paragraph gives like-for-like v=28 bounds: `1.78×10⁻¹³ / 1.84×10⁻¹³ / 2.84×10⁻¹³` (lines 162–164), consistent with the stated ordering.

**CLAIM 4 — VERIFIED**  
Generator docstring line 99: `sigma_eff = f_H^2 * sigma/m would give 0.256-1.518 cm^2/g`. Recomputed: F_H_CC = 0.30 → F_H_CC² = 0.09. JSON `_derived_ranges.sigma_m_cm2_per_g.min` = 2.8454570671911887 → 0.09× = 0.256091… → 0.256. `.max` = 16.865226429437705 → 0.09× = 1.517870… → 1.518. Matches exactly.

**CLAIM 5 — VERIFIED**  
Test file `test_n18_generator_docstring_consistency.py`:  
- `test_docstring_range_matches_output_json()` reads `_derived_ranges.sigma_m_cm2_per_g` from JSON, reads `F_H_CC` from generator, computes `round(f_h**2 * rng["min"], 3)` / `round(f_h**2 * rng["max"], 3)`, asserts docstring equals those computed values.  
- `test_docstring_range_is_not_the_retracted_value()` guards against the stale `0.257-1.589`.  
- Two additional tests pin published σ_eff band and halo count to JSON.  
All assertions are dynamic (derived from generator’s own output), not hard-coded literals. Would fail if either side drifts.

**CLAIM 6 — VERIFIED**  
Companion §3 (lines 816–893) shows a unified diff (`--- a/...json +++ b/...json`) with 3 hunks: (1) added `_derived_ranges` block (18 lines), (2) rewritten `verdict.interpretation`, (3) +1 `limitations` entry. The diff header `@@ -205,17 +205,35 @@` and content match the actual changes between pre-Round-5 (`7cc8d8a^`) and current JSON. The live file (241 lines) is correctly referenced as the authority.

---

### ADDITIONAL FINDINGS (defects in the fix set not flagged by either reviewer)

1. **Paper-internal σ_HL inconsistency for Fornax** — Line 102 (fixed by n18) states `σ_HL = −0.534 cm²/g` (V_max=15 km/s). Line 523 (untouched) still states `σ_HL = -0.47 cm²/g` (V_max=18 km/s, “canonical Fornax parameters”). Both appear in the same paper without reconciliation. The n18 fixes corrected the first occurrence but left the second.

2. **Hierarchy-section σ/m(28) for σ_1=1.0 slightly mismatches generator formula** — Paper lines 149, 163, 169 quote `σ/m = 65.49 cm²/g` at v=28, σ_1=1.0. Generator formula: `baseline = 0.052*(28/100)^(-1.93) ≈ 0.61`, `resonance = 174*exp(-(28-29.4)²/(2*1.0²)) ≈ 65.30`, sum ≈ `65.91`. The 65.49 value is ~0.6% low; not in the generator/JSON, only in paper prose. Minor but unflagged numerical drift.

3. **Companion diff displays JSON newlines as literal `\n`** — The diff in §3 shows `\n` escape sequences inside the `interpretation` string (lines 871–880) rather than actual line breaks. This is a markdown rendering artifact; the underlying diff is faithful, but a human reader applying the diff manually would need to unescape.
