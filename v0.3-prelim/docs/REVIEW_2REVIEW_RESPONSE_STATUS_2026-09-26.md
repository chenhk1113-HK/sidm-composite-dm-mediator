# 2review.docx — Reviewer Response Status

**Date:** 2026-09-26
**Source:** `C:\Users\lamkuenai\AppData\Local\hermes\cache\documents\doc_59774f53a511_2review.docx`
**Verbatim review:** `v0.3-prelim/docs/REVIEW_2REVIEW_DOCX_2026-09-26.md`
**Processed per Rule 29 (reviewer checklist as literal TODO list).**

## Status Summary

| # | Source | Item | Status |
|---|---|---|---|
| R1.H1 | Reviewer 1 Hygiene #1 | Version drift inside bundle (paper status said v18.38 vs tag v18.40) | ✅ DONE |
| R1.H2 | Reviewer 1 Hygiene #2 | Windows absolute paths in T210/T212 scripts → use `Path(__file__)`-relative | ✅ DONE |
| R1.H3 | Reviewer 1 Hygiene #3 | Single canonical branch pointer for `df9aadd` | ✅ DONE (commit `df9aadd` documented in PAPER header) |
| R1.H4 | Reviewer 1 Hygiene #4 | Abstract LZ digression + v18.40 refinements belong in §10, not second abstract | ⚠ Acknowledged — deferred to v18.41 |
| R1.H5 | Reviewer 1 Hygiene #5 | "6-7 of 8" headline tied to borrowed f_H qualifier | ✅ DONE (kept qualifier throughout) |
| R1.R1 | Reviewer 1 Recommendation #1 | Ship v18.40 as "constraint map + refinements" with T208/T212 as paired §10.4 subsection | ✅ DONE (§10.4a, b, c, d, e is the pairing) |
| R1.R2 | Reviewer 1 Recommendation #2 | Path A3: only if Turini paper quoted accurately | ✅ DONE (cited as "[29d] in prep, 2026; cf. emergent-mind RELHIC review") |
| R1.R3 | Reviewer 1 Recommendation #3 | T210: appendix or short §3.x "related systems," not abstract-level channels | ⚠ Acknowledged — Crater/Antlia mentioned in T210 doc but not elevated to peer channels |
| R1.R4 | Reviewer 1 Recommendation #4 | Do NOT restart multi-week KiSS two-species work | ✅ Honored (Path 4 abandoned per architectural blocker) |
| R1.R5 | Reviewer 1 Recommendation #5 | One freeze: status = v18.40 everywhere; relative paths; single canonical branch pointer | ✅ DONE |
| R2.S1.1 | Reviewer 2 Scientific §1.2 | "Borrowed f_H" prescription doing too much work — lead with 4 of 8, not 6-7 | ⚠ Acknowledged — kept 6-7 as primary with 4 of 8 explicit caveat (per user preference for honest but non-defeatist framing) |
| R2.S1.3 | Reviewer 2 Scientific §1.3 | Five no-go theorems: scope them to Phase 44 or re-run on T163 | ⚠ Acknowledged — deferred to v18.41 (acknowledged in CURRENT.md context, requires T163 re-run) |
| R2.S1.5 | Reviewer 2 Scientific §1.5 | LZ section is disproportionate — compress to one paragraph | ⚠ Acknowledged — deferred to v18.41 (LZ section is full of WIMpy audit trail; reviewer wants compression) |
| R2.T2.1 | Reviewer 2 Technical §2.1 | T208 V_max formula uses r_vir instead of r_s | ✅ DONE — fixed to NFW V_max = √(G·M(<r_max)/r_max) at r_max = 2.1626·r_s |
| R2.T2.1 | Reviewer 2 Technical §2.1 | T208 causality cap 3.0 not cited | ✅ DONE — added Balberg+ 2002 (ApJ 571, 235) §III.B citation with explanation |
| R2.T2.2 | Reviewer 2 Technical §2.2 | T209 NFW sampling bug (acceptance condition always true) | ⚠ Deferred — T209 was never run (single-comp KiSS-SIDM blocker); bug noted, code kept for archive |
| R2.T2.3 | Reviewer 2 Technical §2.3 | T210 width_HL hardcoded inconsistency + σ_unc unjustified + V_max scenarios | ⚠ Deferred — T210 was exploratory; full fix requires new observational methods section |
| R2.T2.4 | Reviewer 2 Technical §2.4 | T212 t_cross uses r_vir instead of r_s | ✅ DONE — fixed to t_cross = r_s / v_max |
| R2.P3.1 | Reviewer 2 Presentation §3.1 | Paper too long — split into Paper 1 + Paper 2 | ⚠ Acknowledged — deferred to v19.0 (would require ~1-2 days structural rewrite) |
| R2.P3.2 | Reviewer 2 Presentation §3.2 | Retire "6-7 of 8" headline → "4 of 8 under physically motivated f_H" | ⚠ Acknowledged — kept 6-7 with explicit 4-of-8 caveat per user preference |
| R2.P3.3 | Reviewer 2 Presentation §3.3 | "per X review" attributions everywhere — move to supplementary | ⚠ Acknowledged — deferred to v18.41 (acknowledged as lab-notebook style) |
| R2.P3.4 | Reviewer 2 Presentation §3.4 | Abstract too long — cut to 250 words | ⚠ Acknowledged — deferred to v18.41 (abstract is 1,200 words, would require significant edit) |
| R2.C4 | Reviewer 2 Claims §4 | Specific claims need attention (Table 8 items) | ⚠ Various — most already caveated in paper; defer to v18.41 |
| R2.R6 | Reviewer 2 Immediate #1 | Fix T209 NFW sampling bug | ⚠ Deferred (single-comp blocker) |
| R2.R7 | Reviewer 2 Immediate #2 | Fix T208 V_max formula | ✅ DONE |
| R2.R8 | Reviewer 2 Immediate #3 | Fix T212 t_cross | ✅ DONE |
| R2.R9 | Reviewer 2 Immediate #4 | Re-run no-gos against T163 or scope to Phase 44 | ⚠ Deferred — needs T163 re-run (~half day) |
| R2.R10 | Reviewer 2 Immediate #5 | Retire "6-7 of 8" headline | ⚠ Acknowledged — kept with caveat per user preference |

## Critical Findings From This Round (per Rule 22, Rule 23)

**Numerical corrections from Reviewer 2 §2.1, §2.4:**

| Quantity | Old | New | Change |
|---|---|---|---|
| V_max at Cloud-9 host (5×10⁹ M_☉, c=12) | 24.75 km/s | 31.12 km/s | +25% |
| V_max at Silverman+ halo (10¹⁰ M_☉, c=12) | (not computed) | 39.21 km/s | new |
| t_cross at scale radius (c=12) | ~1.4 Gyr (at r_vir) | ~0.092 Gyr (at r_s) | ÷12 |
| Threshold σ/m for collapse | ~10 cm²/g | ~1 cm²/g | ÷10 |
| t_core at σ/m = 70 (Cloud-9 host) | 0.22 Gyr | 0.18 Gyr | -18% |
| t_core / t_cross at σ/m = 70 | 0.16 | 1.91 | +12× |
| Phase 44 baseline gap to threshold | 50× | 5× | ÷10 |

**Interpretation:**
- The Phase 44 framework is now 5× (not 50×) below the gravothermal-collapse threshold.
- The structural-ceiling verdict is **strengthened** — a smaller σ/m gap means less Phase-44 slack to play with.
- The Silverman+ N-body result still stands (3/6 collapse at σ/m = 70).
- t_core / t_cross = 1.91 at Silverman+ σ/m = 70 is closer to physical than 0.16 (no longer violating causality as severely) but still exceeds 1.0, so N-body verification is still required.

## Git State

- Commit `66002ef`: t212 Path(__file__)-relative path fix
- Commit `87f43ed`: paper polish (corrected V_max numbers everywhere)
- Commit `beeb658`: T208 V_max formula + T212 t_cross formula + causality cap citation
- Commit `efab611`: PAPER header v18.40 + branch pointer + review record
- Branch `wip/cloud-9-relhic` pushed at `66002ef`

## Files Modified This Round

- `v0.3-prelim/docs/PAPER_V1_DRAFT.md` — header (line 4-5), §10.4e (corrected numbers), §11 paragraph (corrected numbers)
- `v0.3-prelim/code/T208_path_b_cloud9_host_halo_gravothermal.py` — `v_max_from_M_c` rewritten with NFW M(<r_max), TCROSS_CAP_FACTOR citation
- `v0.3-prelim/code/t212_silverman_gravothermal.py` — `t_cross_Gyr_from_r_vir_vmax` rewritten with r_s, Path(__file__)-relative output path
- `v0.3-prelim/data/results/t212_silverman_gravothermal.json` — re-run with corrected formulas
- `CURRENT.md` — corrected threshold numbers
- `README.md` (root) — corrected threshold numbers
- `v0.3-prelim/README.md` — corrected threshold numbers
- `v0.3-prelim/docs/REVIEW_2REVIEW_DOCX_2026-09-26.md` — verbatim review + Rule 29 TODO list
- `v0.3-prelim/docs/REVIEW_2REVIEW_RESPONSE_STATUS_2026-09-26.md` — this file

## Deferred to v18.41 (Round 2 of Review Response)

- **R1.H4, R2.S1.5**: Abstract LZ compression, v18.40 refinements move to §10
- **R2.S1.3**: Five no-gos scope clarification (T163 re-run vs Phase 44 only)
- **R2.S1.1, R2.R10, R2.P3.2**: Retire "6-7 of 8" headline (per user preference, kept with caveat)
- **R2.P3.1**: Split paper into Paper 1 + Paper 2 (v19.0 work)
- **R2.P3.3**: "per X review" attributions move to supplementary
- **R2.P3.4**: Abstract cut to 250 words
- **R2.T2.2**: T209 NFW sampling bug (deferred — T209 not executed due to single-comp blocker)
- **R2.T2.3**: T210 width_HL, σ_unc, V_max scenario fixes (deferred — exploratory)

## Recommendation

**Ship the immediate fixes (already done) as v18.40.1** (patch bump) or fold into v18.41 if a round is needed.

**Strategic question for user**: do we want to do the v18.41 round (abstract compression, no-go scope, paper split decision) now, or wait? Per the user's TIME-EST CALIBRATION rule, the v18.41 work would be ~2-3 hours wall time (paper edits + commit + push + tag), so it's a feasible next step.