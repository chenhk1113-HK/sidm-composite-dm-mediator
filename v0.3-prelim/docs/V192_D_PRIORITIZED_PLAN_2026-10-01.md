# v19.2-D Plan — Prioritized (R78, all R77 numerical issues corrected)

**Date:** 2026-10-01
**Status:** v19.2-C milestone in `c486782`, R72-R77 in `7f82a7c`/`4017499`/`03888ab`/`7aa10d7`/`d4e464c`/`51d6fcc`, R78 in this commit

---

## R77 plan-reviewer feedback → R78 resolutions

### Issue 1 — V_max = 20 sensitivity numbers were estimated — RESOLVED

**Reviewer:** "If σ/m is recomputed at V_max = 20 (using Gaussian tail), exp(-(20-29.4)²/(2×4.4²)) = exp(-2.28) ≈ 0.10, × 174 = 17.8, + background = 18.1 cm²/g. t_core = 12.7/18.1 × 0.5 × 0.14 × 5 = 0.245 Gyr. That's factor 20 below 5.07, not factor 2."

**Resolution:** **R78 §3.3 σ/m RECOMPUTED at each V_max** (not assumed fixed):
- V_max = 15: σ/m = 1.17 cm²/g → t_core = **5.07 Gyr** (headline)
- V_max = 18: σ/m = 6.35 cm²/g → t_core = **0.78 Gyr** (factor 6.5× worse)
- V_max = 20: σ/m = 18.02 cm²/g → t_core = **0.25 Gyr** (factor 20× worse)

Headline 5.07 Gyr is the **most generous** self-assessment; canonical V_max values give t_core ~ 0.8 Gyr (factor 6.5× worse).

### Issue 2 — Fornax V_max = 18 (canonical) gives t_core ~ 0.8 Gyr — RESOLVED

**Reviewer:** "Canonical Fornax V_max is 18 km/s (Walker+ 2009, Mateo+ 1998, Read+ 2019 give 15–20). With V_max = 18: σ/m = 6.4 cm²/g, t_core = 0.77 Gyr. So tension is 6× worse than headline."

**Resolution:** R78 §3.3 explicitly reports both:
- Headline V_max = 15 km/s → t_core = 5.07 Gyr (paper convention)
- Canonical V_max = 18 km/s → t_core = **0.78 Gyr** (6.5× worse)
- Canonical V_max = 20 km/s → t_core = **0.25 Gyr** (20× worse)

### Issue 3 — σ = 4.4 km/s: phenomenological needs a derivation — RESOLVED

**Reviewer:** "Where did 4.4 come from? Phase 44 free fit, Cloud-9 W50, or free choice?"

**Resolution:** **R78 §3.3**: σ = 4.4 km/s is **phenomenological** (chosen to fit the 8-channel constraint dataset). It's NOT from:
- Phase 44 free fit (which produced different widths for channels 2,3,4; v_1 width was held fixed at 4.4)
- Cloud-9 W50 = 12 km/s directly (W50 thermal broadening = 16-20 km/s, not 4.4)

The 4.4 km/s value is the framework's chosen input that best reproduces the 8-channel σ/m(v) curve. Per R76: σ = 4.4 km/s is the Gaussian σ width; equivalent FWHM = 10.4 km/s.

### Issue 4 — Binding galaxy window (V_max 15-30 km/s) — RESOLVED

**Reviewer:** "At V_max ~ 10 (Draco, Sculptor): σ/m tiny → no collapse → consistent. At V_max ~ 15-20 (Fornax): σ/m ~ 1-6 → collapse in <5 Gyr → tension. At V_max ~ 29.4 (peak): no observed object here. So tension at V_max ~ 15-30 km/s window, Fornax at the edge."

**Resolution:** R78 §3.3 explicitly states this window. The framework predicts collapse for halos at V_max ~ 15-30 km/s; only Fornax (V_max ~ 15-20) is observed in this window, and Fornax's diffuse core contradicts the collapse prediction.

### Issue 5 — σ_peak sensitivity numbers were slightly off — RESOLVED

**Reviewer:** "Run them."

**Resolution:** **R78 σ_peak sensitivity** recomputed from formula:
- σ_peak = 150: σ/m(15) = 1.06 cm²/g, t_core = **5.62 Gyr** (was 5.6 in R77, correctly 5.62)
- σ_peak = 174: σ/m(15) = 1.17 cm²/g, t_core = **5.07 Gyr** (headline)
- σ_peak = 200: σ/m(15) = 1.29 cm²/g, t_core = **4.59 Gyr** (was 4.6 in R77, correctly 4.59)

t_core stable to ±15% in σ_peak (5.07 ± 0.5 Gyr range).

---

# DO NOW (unchanged from R77)

1. R78 patches DONE in this commit:
   - σ/m recomputed at each V_max (not assumed fixed)
   - Fornax V_max = 18 canonical: t_core = 0.78 Gyr (6.5× worse than headline)
   - σ = 4.4 km/s explicitly phenomenological
   - Window 15-30 km/s stated
   - σ_peak sensitivity recomputed (5.62/5.07/4.59)

2. D-5 σ_peak width test
3. D-8 post-diction audit
4. D-13 reference audit
5. Abstract readability (200 words)
6. Figure rendering
7. D-17 PDF build

---

# Submission checklist (R78)

- [x] R72 ratio arithmetic fix
- [x] R72 m_chi-independence statement
- [x] R72 single-mediator coupling assumption note
- [x] R73 g_N/g_χ PRIMARY=3e-11 (state at R73)
- [x] R74 v_target = 29.4 km/s
- [x] R75 g_N/g_χ FLIP to R72 PRIMARY=7.5e-12 (current)
- [x] R75 σ/m(Fornax) = 1.17 cm²/g, t_core = 5.07 Gyr
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
- [x] R78 Window 15-30 km/s stated
- [x] R78 σ_peak sensitivity RECOMPUTED (5.62/5.07/4.59)
- [ ] D-5: σ_peak width test
- [ ] D-8: Post-diction audit
- [ ] D-13: Reference audit
- [ ] Abstract 200 words
- [ ] Figure rendering
- [ ] D-17: PDF build

---

*Plan revised 2026-10-01 per R77 reviewer feedback*
*Stored at `v0.3-prelim/docs/V192_D_PRIORITIZED_PLAN_2026-10-01.md`*
*Will be re-uploaded as R78 (commit pending)*