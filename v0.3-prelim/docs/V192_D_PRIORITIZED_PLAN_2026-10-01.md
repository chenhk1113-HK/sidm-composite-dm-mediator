# v19.2-D Plan — Prioritized (R79, headline framing fixed)

**Date:** 2026-10-01
**Status:** v19.2-C milestone in `c486782`, R72-R78 in `7f82a7c`/`4017499`/`03888ab`/`7aa10d7`/`d4e464c`/`51d6fcc`/`e90d0e6`, R79 in this commit

---

## R78 plan-reviewer feedback → R79 resolutions

### Issue 1 — Headline framing backwards — RESOLVED

**Reviewer:** "If 15 is the outlier and 18 is canonical, then the paper's headline is the most generous case, not the representative one. For a framework limitation, the honest headline is: 'The framework predicts collapse for Fornax-like halos in 0.25-5 Gyr, with canonical Fornax parameters (V_max = 18 km/s) giving t_core ≈ 0.8 Gyr.'"

**Resolution:** **R79 §3.3** now states the framework tension as a **range** (0.25–5.07 Gyr) with the **canonical V_max = 18 km/s giving t_core ≈ 0.78 Gyr as the representative tension** (not the V_max = 15 headline). Headline V_max = 15 km/s is explicitly labeled "generous lower bound."

### Issue 2 — σ_peak sensitivity "±15%" → "±10%" — RESOLVED

**Reviewer:** "The range 4.59–5.62 is ±10% around 5.07, not ±15%. If '±15%' refers to the σ_peak variation, then that's correct, but the sentence should say 't_core is stable to within ±10% for ±15% changes in σ_peak.'"

**Resolution:** R79 §3.3 now reads: "t_core is stable to within ±10% for ±15% changes in σ_peak (4.59 Gyr at σ_peak=200 → 5.62 Gyr at σ_peak=150, both around the 5.07 Gyr headline)."

### Issue 3 — σ = 4.4 km/s sourcing — RESOLVED

**Reviewer:** "If it's a free parameter chosen to satisfy the eight channels, state that: 'σ = 4.4 km/s is the value that best fits the eight-channel constraint set; it is treated as a phenomenological input.'"

**Resolution:** R79 §3.3: σ = 4.4 km/s is the value that best fits the eight-channel constraint set; treated as phenomenological input.

---

# DO NOW (unchanged from R78)

1. R79 patches DONE in this commit:
   - Framework tension range stated (0.25–5.07 Gyr)
   - Canonical V_max = 18 km/s → t_core = 0.78 Gyr (representative)
   - σ_peak sensitivity ±10% for ±15% changes (corrected)
   - σ = 4.4 km/s: phenomenological input for 8-channel fit

2. D-5 σ_peak width test
3. D-8 post-diction audit
4. D-13 reference audit
5. Abstract readability (200 words)
6. Figure rendering
7. D-17 PDF build

---

# Submission checklist (R79)

- [x] R72 ratio arithmetic fix
- [x] R72 m_chi-independence statement
- [x] R72 single-mediator coupling assumption note
- [x] R73 g_N/g_χ PRIMARY=3e-11 (state at R73)
- [x] R74 v_target = 29.4 km/s
- [x] R75 g_N/g_χ FLIP PRIMARY=7.5e-12 (current)
- [x] R75 σ/m(Fornax V_max=15) = 1.17 cm²/g, t_core = 5.07 Gyr
- [x] R76 constants.py FWHM_KMS → SIGMA_KMS rename
- [x] R76 σ_peak = 174 CAUSALITY CAP
- [x] R76 t_core = 5.07 Gyr: explicit derivation
- [x] R76 FWHM/σ_peak independence
- [x] R77 Walker+ 2009 → Mateo+ 1998 citation fix
- [x] R77 σ_peak sensitivity added
- [x] R77 Fornax canonical sensitivity added
- [x] R77 Balberg+ 2002 ApJ 568, 475 Eq. 22 citation
- [x] R78 σ/m RECOMPUTED at each V_max (not assumed fixed)
- [x] R78 Fornax V_max = 18 gives t_core = 0.78 Gyr (6.5× worse)
- [x] R78 σ = 4.4 km/s explicitly phenomenological
- [x] R78 σ_peak sensitivity RECOMPUTED (5.62/5.07/4.59)
- [x] R79 Framework tension range stated (0.25-5.07 Gyr); canonical V_max = 18 = 0.78 Gyr is REPRESENTATIVE
- [x] R79 σ_peak sensitivity ±10% for ±15% changes (corrected)
- [x] R79 σ = 4.4 km/s: phenomenological input for 8-channel fit
- [ ] D-5: σ_peak width test
- [ ] D-8: Post-diction audit
- [ ] D-13: Reference audit
- [ ] Abstract 200 words
- [ ] Figure rendering
- [ ] D-17: PDF build

---

*Plan revised 2026-10-01 per R78 reviewer feedback*
*Stored at `v0.3-prelim/docs/V192_D_PRIORITIZED_PLAN_2026-10-01.md`*
*Will be re-uploaded as R79 (commit pending)*