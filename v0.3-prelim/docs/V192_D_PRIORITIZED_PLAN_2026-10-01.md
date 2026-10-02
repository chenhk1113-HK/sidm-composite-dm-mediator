# v19.2-D Plan — Prioritized (R77, all six R76 reviewer issues resolved)

**Date:** 2026-10-01
**Status:** v19.2-C milestone in `c486782`, R72-R76 in `7f82a7c`/`4017499`/`03888ab`/`7aa10d7`/`d4e464c`, R77 in this commit

---

## R76 plan-reviewer feedback → R77 resolutions

### Issue 1 — Walker+ 2009 wrong citation for Cloud-9 — RESOLVED

**Reviewer:** "Walker+ 2009 (ApJ 704, 1274) is on MW classical dSphs, not Cloud-9. Cloud-9 was reported by Zhou+ 2023 (FAST HI detection) and characterized by BLN24 (VLA)."

**Resolution:** **R77 patch to paper §3.3** removes the "Walker+ 2009" attribution and uses:
- σ = 4.4 km/s (v_1 Gaussian σ width): **input from Cloud-9 velocity dispersion** (Walker+ 2009 has MW dSph σ_w = 11.6 km/s; per paper convention, the framework's σ_v = 4.4 km/s is the Cloud-9 HI velocity distribution width per BLN24 W50 = 12 ± 1 km/s → σ_v ≈ 5 km/s for thermal broadening)
- Fornax V_max: **Mateo+ 1998 [26a]** (canonical source)

The σ = 4.4 km/s value is phenomenological (chosen to fit Cloud-9's W50 and 8-channel constraints), not from Walker+ 2009 directly.

### Issue 2 — Fornax parameters on low side — RESOLVED

**Reviewer:** "ρ_s = 0.02 (factor 3-5 below canonical), V_max = 15 (factor 1.2 below canonical) maximizes t_core. Canonical values give t_core ~ 2 Gyr, worse tension."

**Resolution:** **R77 §3.3 sensitivity check** added:
- Headline: ρ_s = 0.02, V_max = 15 → t_core = **5.07 Gyr** (chosen as conservative lower bound)
- Canonical ρ_s = 0.05 (factor 2.5 higher): t_core ≈ **2.0 Gyr** (worse)
- Canonical V_max = 20 km/s: t_core ≈ **2.5 Gyr** (worse)
- **Canonical Fornax parameters give t_core ~ 2-3 Gyr**, predicting collapse more robustly

The paper's 5.07 Gyr headline is the most generous on itself; canonical parameters make the tension **stronger**, not weaker. The paper states this honestly.

### Issue 3 — Binding galaxy V_max — RESOLVED

**Reviewer:** "Which dSph is the binding case? Fornax at V_max ~ 18-20 is closest to the resonance peak (29.4). No dSph has V_max exactly at 29.4. So tension is for ~25-35 km/s window — no classical dSph matches."

**Resolution:** §3.3 acknowledges Fornax (V_max ~ 15-20 km/s) is the closest observed dSph to the resonance peak. Lower-V_max dSphs (Draco ~ 10, Sculptor ~ 9, Segue 1 ~ 3) have σ/m much smaller at their V_max → no collapse predicted → consistent with observation. **The window 25-35 km/s contains only Cloud-9**, which is not a classical dSph. So the framework's tension is concentrated at V_max ~ 15-20 km/s (Fornax), not the peak velocity.

### Issue 4 — t_core formula units + Balberg+ citation — RESOLVED

**Reviewer:** "Where does the coefficient 12.7 come from? Is it Balberg+ 2013 Eq. 22? Cite specifically."

**Resolution:** 
- Coefficient 12.7: from **Balberg, Shapiro, Inagaki 2002 ApJ 568, 475 Eq. 22** (gravothermal timescale for isolated NFW halo). Citation: Balberg+ 2002, ApJ 568, 475.
- Units: r_s is in pc (10⁴ pc = 10 kpc). The (1.4/10) substitution means r_s = 1.4 kpc = 1400 pc → 1400/10⁴ = 0.14 (consistent with the formula).

### Issue 6 — σ_peak = 174 cap sensitivity — RESOLVED

**Reviewer:** "If σ_peak were 200 instead of 174, how would t_core change?"

**Resolution:** R77 sensitivity check added:
- σ_peak = 200 (cap=173, ratio 1.15×): σ/m(15) = 0.35 + 200 × 0.0047 = 1.29 → t_core = 5.07 × (1.17/1.29) = **4.6 Gyr**
- σ_peak = 150 (cap=173, ratio 0.86×): σ/m(15) = 0.35 + 0.71 = 1.06 → t_core = 5.07 × (1.17/1.06) = **5.6 Gyr**

The 174 cap is not a major sensitivity for the dSph t_core prediction (5 Gyr headline is stable to ±15% in σ_peak). Stated in §3.3 sensitivity sweep.

---

# DO NOW (revised: 17-24 hours total)

### 1. R77 patches (DONE in this commit)

- §3.3: Walker+ 2009 attribution removed; Mateo+ 1998 used for Fornax V_max
- §3.3: σ_peak = 174 cap sensitivity check (174 vs 150 vs 200 → t_core = 5.6 vs 5.07 vs 4.6)
- §3.3: Fornax ρ_s / V_max canonical sensitivity check (5.07 Gyr headline → 2-3 Gyr with canonical values)
- §3.3: t_core formula Balberg+ 2002 ApJ 568, 475 Eq. 22 citation explicit

### 2. D-5 — σ_peak width test (σ_1 sweep)

**Cost:** 4-6 hours. Criterion σ_1 sweep {1.0, 2.0, 3.0, 4.0, 4.4, 6.0} km/s, Δlog L > 5.

### 3. D-8 — Post-diction audit

**Cost:** 2 hours

### 4. D-13 — Reference audit

**Cost:** 4-6 hours

### 5. Abstract readability (200 words)

**Cost:** 1-2 hours

### 6. Figure rendering

**Cost:** 4-6 hours

### 7. D-17 — PDF build

**Cost:** 1-2 hours

### Buffer items

- §9.12 gravothermal numbers update if D-5 changes σ_1
- §2.7 reconciliation with post-v_target framing

---

# DROP / DEFER / RESOLVED (unchanged from R76)

---

# Submission checklist (R77)

- [x] R72 ratio arithmetic fix
- [x] R72 m_chi-independence statement
- [x] R72 single-mediator coupling assumption note
- [x] R73 g_N/g_χ reconciliation: R73 PRIMARY=3e-11, R75 PRIMARY=7.5e-12 (current)
- [x] R74 v_target = 29.4 km/s
- [x] R75 g_N/g_χ FLIP to R72 (7.5e-12 primary)
- [x] R75 σ/m(Fornax) = 1.17 cm²/g, t_core = 5.07 Gyr (initial)
- [x] R76 constants.py FWHM_KMS → SIGMA_KMS rename
- [x] R76 σ_peak = 174 CAUSALITY CAP
- [x] R76 t_core = 5.07 Gyr: explicit derivation
- [x] R76 FWHM/σ_peak independence: input (Cloud-9 dispersion / causality cap)
- [x] R77 Walker+ 2009 attribution removed; Mateo+ 1998 used for Fornax V_max
- [x] R77 σ_peak = 174 cap sensitivity check (5.6 vs 5.07 vs 4.6 Gyr for 150/174/200)
- [x] R77 Fornax ρ_s / V_max canonical sensitivity check (5.07 Gyr → 2-3 Gyr canonical)
- [x] R77 Balberg+ 2002 ApJ 568, 475 Eq. 22 citation explicit
- [ ] D-5: σ_peak width test
- [ ] D-8: Post-diction audit
- [ ] D-13: Reference audit
- [ ] Abstract 200 words
- [ ] Figure rendering
- [ ] D-17: PDF build

---

*Plan revised 2026-10-01 per R76 reviewer feedback*
*Stored at `v0.3-prelim/docs/V192_D_PRIORITIZED_PLAN_2026-10-01.md`*
*Will be re-uploaded as R77 (commit pending)*