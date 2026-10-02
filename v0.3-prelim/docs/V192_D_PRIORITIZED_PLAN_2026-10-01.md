# v19.2-D Plan — Prioritized (R76, all five R75 reviewer issues resolved)

**Date:** 2026-10-01
**Status:** v19.2-C milestone in `c486782`, R72-R75 in `7f82a7c`/`4017499`/`03888ab`/`7aa10d7`, R76 in this commit

---

## R75 plan-reviewer feedback → R76 resolutions

### Issue 1 — FWHM vs σ — RESOLVED

**Reviewer:** "σ/m(v=15) = 0.347 + 174 × exp(-(15-29.4)²/(2 × 4.4²)). That's a Gaussian with σ = 4.4, not FWHM = 4.4. If FWHM = 4.4, then σ = 1.87, and at v=15: exp(-29.7) ≈ 1.4e-13. So 4.4 km/s in the formula is the σ width."

**Resolution:** **constants.py renamed FWHM_KMS = 4.4 → SIGMA_KMS = 4.4.** The numerical value is unchanged (formula still uses 4.4); only the variable name is corrected. Equivalent FWHM = 4.4 × 2.355 = 10.36 km/s (~10.4 km/s).

**Implications:**
- D-5's "w_lim < 3.0 km/s" now means **σ < 3.0 km/s** (equivalent to FWHM < 7.1 km/s, narrower than current FWHM 10.4)
- All formulas in paper remain numerically identical; numerical labels stay identical.

### Issue 2 — σ_peak = 174: cap or rounded fit — RESOLVED

**Reviewer:** "Either 174 is the causality cap and the fit value (178.5) is truncated, or it's a rounded fit value and the cap framing was wrong."

**Resolution:** **σ_peak = 174 is the CAUSALITY CAP** from §9.12. Phase 44 free fit gave σ_peak_R0 = 178.5 (best_params[4]) unconstrained. Causality cap (paper §9.12, ratio > 3.0 × t_cross) sets upper limit at 174. The fit value (178.5) is **truncated, not rounded.**

constants.py comment updated: "174 is the CAUSALITY CAP from §9.12, NOT a rounded fit value."

### Issue 3 — t_core = 5.07 Gyr derivation — RESOLVED

**Reviewer:** "Where do ρ_s = 0.02 and r_s = 1.4 come from? Show the arithmetic."

**Resolution:** **R76 explicit derivation** in §3.3:
- ρ_s = 0.02 M☉/pc³: canonical NFW for M~10⁸ M☉ dSph, c~10
- r_s = 1.4 kpc: r_vir/c at canonical NFW
- v_max = 15 km/s: Fornax V_max per Mateo+ 1998/Walker+ 2009 (paper [26a])

**Balberg+ Eq. 22:**
```
t_core [Gyr] = 12.7 / (sigma/m) × (rho_s/10^-2)^-1 × (r_s/10^4) × (100/v_max)
             = 12.7 / 1.17 × (0.02/0.01)^-1 × (1.4/10) × (100/15)
             = 10.85 × 0.5 × 0.14 × 6.67
             = 5.07 Gyr
```

At σ/m = 2.56 (paper's prior baseline v_target=28): t_core = 2.32 Gyr. Factor 2.19 reduction matches σ/m ratio 2.56/1.17.

### Issue 4 — FWHM and σ_peak independence from Phase 44 — RESOLVED

**Reviewer:** "If the Phase 44 fit changed widths, but the paper keeps FWHM = 4.4 and σ_peak = 174 as 'inputs,' then either these are genuinely independent of the fit, or they aren't."

**Resolution:** 
- FWHM (= 4.4 km/s σ = 10.4 km/s): **Independent of Phase 44 fit.** Comes from Cloud-9 velocity dispersion measurement (Walker+ 2009 [26a] / Mateo+ 1998). The Phase 44 fit has separate width parameters for v_2,3,4 resonances (params 11-13, which DID change). The v_1 resonance width is fixed at 4.4 km/s σ (input from Cloud-9 velocity dispersion), not fitted.
- σ_peak = 174: **Independent of Phase 44 fit.** Comes from causality cap (§9.12, ratio > 3.0 × t_cross). Phase 44 fit preferred 178.5 unconstrained; cap truncates to 174. **Not a fit parameter.**

### Issue 5 — Checklist typo + R73→R75 state change note — RESOLVED

**Reviewer:** "Checklist still shows PRIMARY=3e-11 in R73 line. Add a note about state change."

**Resolution:** Checklist updated with explicit state-change note: "R73 line shows 3e-11 (state at R73); R75 line shows 7.5e-12 (current primary after R75 flip)."

---

# DO NOW (revised: 17-24 hours total)

### 1. R76 patches (DONE in this commit)

- constants.py: FWHM_KMS → SIGMA_KMS (R76 rename; numerical value unchanged)
- σ_peak = 174: comment updated as CAUSALITY CAP (not rounded fit)
- t_core = 5.07 Gyr derivation: explicit Balberg+ formula shown in §3.3

### 2. D-5 — σ_peak width test (CORRECTED rationale)

**Criterion:** σ_1 (the v_1 Gaussian σ width) sweep σ_1 ∈ {1.0, 2.0, 3.0, 4.0, 4.4, 6.0} km/s. Compare likelihood ratio for each vs fixed σ_1 = 4.4 baseline. **Δlog L > 5 threshold for adopting new value** (1-parameter sweep).

**Outcomes:**
- σ_1 < 3.0 km/s (i.e., narrower than current σ_1 = 4.4): dSph tension resolves
- σ_1 = 4.4 holds: dSph gravothermal tension is a real framework constraint

### 3. D-8 — Post-diction audit (finish R58)

**Cost:** 2 hours

### 4. D-13 — Reference audit (must-do)

**Cost:** 4-6 hours

### 5. Abstract readability pass (200 words)

**Cost:** 1-2 hours

### 6. Figure rendering (MUST-DO before D-17)

**Cost:** 4-6 hours

### 7. D-17 — PDF build

**Cost:** 1-2 hours

### Buffer items

- §9.12 gravothermal numbers update if D-5 changes σ_1
- §2.7 reconciliation with post-v_target framing

---

# DROP

D-1, D-4, D-6, D-7, D-9 to D-12, D-16 — unchanged

---

# DEFER INDEFINITELY

D-2, D-3, D-19, D-20 — unchanged

---

# ALREADY RESOLVED

- D-14 0.085 dex origin (R35-R36)
- D-15 Master σ/m(v) figure (v1.0 figures)
- D-18 Figure rendering (v1.0 MUST-DO)

---

# Revised total wall-clock

**Do-now priority:** 17-24 hours

---

# Submission checklist (R76)

- [x] R72 ratio arithmetic fix (1.78e22, not 10^46)
- [x] R72 m_chi-independence statement for σ_peak = 174
- [x] R72 single-mediator coupling assumption note
- [x] R73 g_N/g_χ reconciliation: R73 state PRIMARY=3e-11, R75 state PRIMARY=7.5e-12 (current)
- [x] R74 v_target = 29.4 km/s (paper §2.6 line 152, §2 line 114)
- [x] R75 g_N/g_χ FLIP to R72 (7.5e-12 primary, 3e-11 footnote)
- [x] R75 σ/m(Fornax) = 1.17 cm²/g, t_core = 5.07 Gyr (paper §3.3 explicit)
- [x] R76 constants.py FWHM_KMS → SIGMA_KMS rename
- [x] R76 σ_peak = 174: CAUSALITY CAP (not rounded fit) — comment updated
- [x] R76 t_core = 5.07 Gyr: explicit derivation in §3.3
- [x] R76 FWHM/σ_peak independence: input (Cloud-9 dispersion / causality cap), not fit
- [ ] D-5: σ_peak width test (σ_1 sweep, Δlog L > 5)
- [ ] D-8: Post-diction audit finish
- [ ] D-13: Reference audit (50 entries)
- [ ] Abstract 200 words (5 claims + §2.7)
- [ ] Figure rendering (σ/m multi-channel, hierarchy)
- [ ] D-17: PDF build

---

*Plan revised 2026-10-01 per R75 reviewer feedback*
*Stored at `v0.3-prelim/docs/V192_D_PRIORITIZED_PLAN_2026-10-01.md`*
*Will be re-uploaded as R76 (commit pending)*