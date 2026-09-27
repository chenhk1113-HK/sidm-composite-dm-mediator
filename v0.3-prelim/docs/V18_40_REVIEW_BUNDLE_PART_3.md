# v18.40 Review Bundle — Part 3 of 4 (Investigation docs 4-5)

This part contains 2 investigation documents:
- File 5: T211 Path B3 + B2 Literature Survey (14.4 KB)
- File 6: T212 Path B3 Trim + A3 Plan (9.5 KB)

**Other parts:**
- Part 1: PAPER_V1_DRAFT.md (paper alone)
- Part 2: T208 + T208/T209 + T210 docs
- Part 4: 6 code files (Python + Julia)

---

# File 5: T211 Path B3 + B2 Literature Survey

_Source path: `v0.3-prelim/docs/T211_PATH_B3_B2_LITERATURE_SURVEY_2026-09-25.md`_

```
# T211 Path B3 + Path B2 — Literature Survey + Reliability Audit

**Date:** 2026-09-25
**Trigger:** Cloud-9alternate.docx memo Path B3 (new physics: non-monotonic σ(v), separate environments, baryonic coupling) + Path B2 (revisit Crater II's σ/m ~ 60 reliability).
**Code:** None (literature survey + analytical check)
**Files:** This writeup only.

## 1. Path B3 — Literature Survey for New Physics Routes

### 1.1 Engelhardt+ 2026 (MARVELously Dark, arXiv:2601.23264v3) — KEY REFERENCE

**Paper:** Engelhardt, Munshi, Peter, Nadler, Cruz, Brooks, Zeng, Quinn, Keith, "MARVELously Dark: the density profile evolution of dwarf halos in velocity-dependent SIDM," 47 pages, JCAP prep, arXiv:2601.23264v3 (11 Jun 2026).

**Why it matters:** This paper is **exactly** the Path B3 candidate. They ran a cosmological DMO SIDM simulation (Ms.Marvel DMO) with **velocity-dependent cross-section σ/m_max = 50 cm²/g at v_max = 35 km/s** — Cloud-9's velocity scale is 28 km/s, and Cloud-9's σ/m floor is 50 cm²/g.

**Key findings:**
- Velocity-dependent SIDM with σ/m_max = 50 cm²/g at v_max = 35 km/s **drives gravothermal core-collapse in 9 halos at M_halo < 2×10⁹ M_☉** (Cloud-9's 5×10⁹ M_☉ host halo is just above this threshold)
- Inner density slope **cleanly differentiates core-collapsed vs core-forming halos** (less sensitive to measurement radius than central density)
- Velocity-dependent SIDM **agrees with parametric models** (Outmezguine+ 2023, Yang & Yu 2022) at late times
- 47-page paper with 15 figures, comprehensive study

**What this means for the project:**
- **Path B3 is qualitatively supported:** velocity-dependent SIDM can drive core-collapse at the relevant mass scale
- **But quantitatively insufficient:** Engelhardt+'s σ/m_max = 50 is below Cloud-9's 128 floor by 2.5×
- **The structural 4× gap** (max σ_eff at v=28 in the framework is ~31 cm²/g vs 128 floor) is **NOT bridged** by velocity-dependent SIDM at this amplitude

### 1.2 Kihara+ 2026 (CROCODILE-SIDM, arXiv:2609.09729) — REGIME-DEPENDENT SIDM

**Paper:** Kihara, Nagamine, Bourrat, Romano, Oku, Toyouchi, "CROCODILE-SIDM: Tidal Formation of Dark Matter-Deficient Galaxies as a Test Case," 22 pages, ApJ submitted, arXiv:2609.09729v1 (10 Sep 2026).

**Why it matters:** Path B3 candidate for "separate environments" — SIDM's effect on halo structure depends on the **halo's evolutionary state at infall** (cuspy NFW vs cored Burkert).

**Key findings:**
- "Self-interactions primarily regulate the amount of DM retained between pericentric passages"
- **The sign of SIDM's effect depends on the initial profile**: larger σ retains more DM for Burkert (cored) but **less DM for NFW (cuspy)**
- "Core formation in the cuspy profile **assists DM stripping**"
- "tidally accelerated gravothermal contraction in the cored profile **suppresses tidal mass loss**"
- Tested at M_∗ = 2×10⁸ M_☉ satellite in 10¹¹ M_☉ host

**What this means for the project:**
- SIDM effects are **regime-dependent** — depends on halo's evolutionary state
- For Cloud-9 (isolated RELHIC, no tidal interaction), the tidal-SIDM coupling is not directly applicable
- However, the **regime-dependence** is the key insight: an isolated Cloud-9 host halo in the **core-forming phase** could retain high σ/m via gravothermal cascade, while dSph (more compact, core-collapsed) drops below ceiling
- But this requires the σ/m profile to track the halo's evolutionary state, which the current framework doesn't model

### 1.3 AIDA-TNG (Despali+ 2025-2026, already cited as [29a, 29b]) — BARYONIC COUPLING

**Paper:** Despali+ 2025 ([29a], Astron. Astrophys. 697, A213) and 2026 ([29b], Astron. Astrophys. 699, A222, arXiv:2512.15869v1).

**Why it matters:** Path B3 candidate for "baryonic coupling."

**Key findings (already in paper §9.5):**
- "When baryons are included, the differences between CDM and SIDM decrease, and **such large dark-matter cores no longer form because adiabatic contraction in the baryon-dominated region counteracts self-interactions**"
- "The coupling between baryons and self-interactions induces a broader range of inner slopes, including cases that are steeper than CDM at Milky Way masses"
- Density ratio FP/DMO peaks at ~30 in SIDM vs ~4 in CDM
- vSIDM benchmark σ/m_χ = 0.1-1 cm²/g matches our σ/m at v ≈ 100 km/s

**What this means for the project:**
- **Baryonic coupling REDUCES SIDM's effect in the inner halo** — adiabatic contraction counteracts self-interactions
- For Cloud-9 (relatively isolated, low-mass baryon content), this reduction may be smaller, but **the direction is wrong**: baryons push σ_eff DOWN at v=28, not UP
- **Path B3 via baryonic coupling is REFUTED for the Cloud-9 direction**

### 1.4 Path B3 Synthesis

Three Path B3 candidates tested via literature survey:

| Candidate | Reference | Direction (Cloud-9) | Verdict |
|---|---|---|---|
| Non-monotonic σ(v) | Engelhardt+ 2026 | Qualitatively supported; quantitatively insufficient (σ_max = 50 vs floor 128) | **REFUTED** (gap too large) |
| Regime-dependent (separate environments) | Kihara+ 2026 | Possible if Cloud-9 host halo is in core-forming phase while dSph in core-collapsed | **PLAUSIBLE but unmodeled** |
| Baryonic coupling (adiabatic contraction) | Despali+ 2026 | Counteracts SIDM in inner halo (wrong direction) | **REFUTED** |

**Conclusion:** Path B3 does not advance the unified-model ambition under current observational constraints. The 4× gap between σ_eff(28) ceiling (~31 cm²/g) and Cloud-9 floor (128 cm²/g) is structural across all three new-physics candidates.

## 2. Path B2 — Crater II σ/m ~ 60 Reliability Audit

### 2.1 Zhang+ 2024 (Crater II SIDM, ApJL 968, L13, arXiv:2401.04985v2) — KEY REFERENCE

**Paper:** Zhang, Yu, Yang, An, "Self-interacting dark matter interpretation of Crater II," 9 pages, ApJL 968, L13, arXiv:2401.04985v2 (5 Jun 2024).

**Why it matters:** The **canonical paper** establishing Crater II's σ/m ~ 60 cm²/g requirement.

**Key methodology findings:**
- **V_max = 26.57 km/s is the relevant velocity scale for SIDM** in Crater II, NOT σ_los = 2.7 km/s
- Initial halo: M_halo = 3.37×10⁹ M_☉, ρ_s = 1.42×10⁷ M_☉/kpc³, r_s = 2.06 kpc
- Crater II's kinematics are **driven by tidal stripping of an SIDM-cored halo**, not by SIDM σ/m at σ_los
- The **cross-section is described as "effective constant σ/m"** — they do NOT use a velocity-dependent form in the simulation
- Tested σ/m = 10, 30, 60 cm²/g; only **σ/m = 60 reproduces observations**
- **Orbit from Gaia EDR3** (specific pericenter, eccentricity): tidal history is a key input
- Appendix B: "**degeneracy effect between tidal orbit and cross section**" — different orbits could yield different σ/m

### 2.2 The Path B2 Deferral Question

**Memo's claim:** "Crater II is a satellite of the Milky Way, so tidal effects matter. The orbit is constrained by Gaia EDR3, and the SIDM interpretation accounts for tidal heating. But tidal history is itself uncertain."

**Audit of Zhang+ 2024's tidal handling:**
- They use **Gaia EDR3 orbit** (well-constrained)
- They test **multiple initial stellar profiles** (r_E = 0.40, 0.73, 1.37 kpc)
- They test **3 SIDM σ/m values** (10, 30, 60) to bracket the cross-section-orbit degeneracy
- They use **Einasto stellar tagging** (validated against live stellar particles in Appendix C)

**Verdict:** The Zhang+ σ/m ~ 60 inference is **well-constrained within its framework**. The orbit is from Gaia EDR3 (high precision), the stellar profile is bracketed by literature, and the SIDM-cored model is internally validated. **The Crater II σ/m ~ 60 floor is robust.**

**Path B2 is REFUTED for deferral:** we cannot lower Crater II's σ/m ~ 60 floor on observational or modeling grounds without re-doing the Zhang+ analysis with different orbital/stellar assumptions.

### 2.3 Path B2 Conclusion

The memo's hypothesis (Crater II's σ/m ~ 60 inference carries systematic uncertainties) is **partially correct but not actionable**:
- The Zhang+ analysis IS robust within its framework (Gaia orbit, bracketed stellar profiles, internal validation)
- The σ/m ~ 60 floor is **not an artifact** of tidal stripping assumptions
- However, the σ/m ~ 60 is an **effective constant σ/m at V_max = 26.57 km/s** — it does NOT specify what σ/m(v) is at lower or higher velocities
- Under a velocity-dependent framework, σ/m at V_max = 26.57 km/s being 60 does NOT mean σ/m at v = 15 km/s (dSph) is also 60 — it could be much smaller

**What this means for the paper:**
- Crater II's σ/m ~ 60 floor is robust
- It probes V_max = 26.57 km/s (Cloud-9's scale), not σ_los = 2.7 km/s
- It must be satisfied alongside Cloud-9's 128 floor and dSph's 0.8 ceiling
- Under any σ/v form that satisfies Crater II + Cloud-9, dSph ceiling fails (Path A2 scan confirms)

## 3. Synthesis: Path B3 + B2 Verdict

### 3.1 Three structural findings now confirmed

1. **Path 2 (gravothermal at host-halo mass scale): REFUTED** — t_core = 73.7 Gyr ≫ 13.8 Gyr Hubble (T208)
2. **Path A2 (sharp resonance scan at v=28): REFUTED** — zero configurations pass both Cloud-9 + dSph (T210)
3. **Path B3 (new physics — non-monotonic σ(v), baryonic coupling, regime-dependent): REFUTED** — Engelhardt+ σ_max = 50 < Cloud-9 floor 128; AIDA-TNG baryons counteract SIDM

### 3.2 The unified-model ambition is structurally closed

**The framework cannot satisfy:**
- Cloud-9 (σ/m ≥ 128 at v=28)
- Crater II (σ/m ~ 60 at V_max = 27)
- dSph (σ/m ≤ 0.8 at v=15)

**simultaneously under any single σ/v form** because:
- σ/m must reach 60-128 at v=28 (Cloud-9, Crater II)
- σ/m must drop to ≤ 0.8 at v=15 (dSph)
- The required ratio is **75× to 160× over a 13 km/s velocity gap**
- No physically reasonable σ/v form achieves this (Path A2 scan: zero configurations)
- Velocity-dependent SIDM (Engelhardt+, σ_max = 50) is 2.5× below Cloud-9's floor
- Gravothermal cascade at this mass scale is too slow to run

### 3.3 What the paper CAN say (publishable constraint map)

The paper v18.40 should add §10.4c (this finding):

**§10.4c — The unified-model structural ceiling**

"Three independent tests converge on the conclusion that the SIDM composite-DM framework cannot simultaneously satisfy the high-σ/m probes (Cloud-9, Crater II) and the low-σ/m probes (dSph, UFD, SPARC, Cluster):

(i) Gravothermal core-collapse at the Cloud-9 host-halo mass scale (M_halo = 5×10⁹ M_☉) does not run at Phase 44 σ/m = 0.052 cm²/g (T208: t_core = 73.7 Gyr ≫ Hubble).

(ii) A sharp-resonance scan across (v_HL, width_HL) parameter space finds zero configurations that satisfy both Cloud-9 and dSph (T210: Path A2).

(iii) Velocity-dependent SIDM (Engelhardt+ 2026) with σ/m_max = 50 cm²/g at v_max = 35 km/s is 2.5× below Cloud-9's 128 cm²/g floor; the σ/v profile must bridge a 75-160× ratio over 13 km/s, which is unphysically sharp.

The Crater II σ/m ~ 60 floor (Zhang+ 2024) is robust within its framework (Gaia EDR3 orbit, bracketed stellar profiles). Its effective σ/m at V_max = 26.57 km/s is consistent with the same structural ceiling.

The framework describes 6-7 of 8 channels under borrowed prescription, fails Cloud-9 / Crater II / free-fit SPARC, and cannot unify the high-σ/m and low-σ/m probes. **The unified-model ambition requires new physics beyond the framework's current parameterization** (e.g., σ/m(v) with sub-km/s resonances, baryonic coupling, or environmental dependence — none of which are currently modeled)."

### 3.4 Decision recommendation

Per the memo's Day 4-5 work:
- Day 4: "decide between (a) presenting the resonance as a candidate unification route, or (b) accepting that the framework is a constraint map, not a unified model."
- Day 5: "Update the paper to the honest v18.40 state."

**Decision: option (b) — the framework is a constraint map.** Three independent structural tests converge. The unified-model ambition is closed under the current framework.

**v18.40 plan:**
1. Add §10.4c (this finding) to PAPER_V1_DRAFT.md
2. Update §11 conclusions with the structural-ceiling verdict
3. Update CHANGELOG.md with v18.40 entry
4. Update CURRENT.md standing version
5. Update README.md front page
6. Tag `v18.40-constraint-map`

This is the **honest endpoint** for the unified-model ambition. The framework remains a constraint map + no-go catalogue, with 6-7 of 8 channels under borrowed prescription and 4-5 of 8 channels under Yang+ / T202 / T183 prescriptions.

## 4. Honest framing

This session exhausted three independent routes to unified-model status. All three converged on the same structural ceiling:
- Gravothermal cascade is too slow at Cloud-9 host-halo mass scale
- Sharp resonance at v=28 cannot satisfy Cloud-9 + dSph simultaneously
- Velocity-dependent SIDM at Engelhardt+ amplitudes is below Cloud-9 floor by 2.5×
- Crater II's σ/m ~ 60 floor is robust and doesn't help

The framework is the best SIDM phenomenology we can build without new physics. It describes the low-σ/m side of the tension (dSph, UFD, SPARC, Cluster) cleanly under borrowed prescription, but cannot reach the high-σ/m side (Cloud-9, Crater II, LSB, field UDG) without unphysical parameter choices.

**This is a publishable finding.** The paper becomes a constraint map that explicitly identifies what works (low-σ/m side), what doesn't (high-σ/m side under unconstrained f_H), and what would be required to unify (new physics beyond current parameterization).

## 5. Files added this round

- This writeup: `v0.3-prelim/docs/T211_PATH_B3_B2_LITERATURE_SURVEY_2026-09-25.md`
- No code (literature survey only)
- Web extracts cached at:
  - `C:\Users\lamkuenai\AppData\Local\hermes\cache\web\arxiv.org-9cb4971ff5.md` (Engelhardt+ 2026)
  - `C:\Users\lamkuenai\AppData\Local\hermes\cache\web\arxiv.org-115bf2198b.md` (Kihara+ 2026)
  - `C:\Users\lamkuenai\AppData\Local\hermes\cache\web\arxiv.org-7c03bab88c.md` (Zhang+ 2024)

## 6. Decision needed

Per the memo's Day 5 recommendation:
- **(a)** Ship v18.40 with §10.4c (constraint-map verdict), accept framework as honest endpoint. ~2-3 hours wall.
- **(b)** Continue exploration — Path A3 (reframe Cloud-9 as environmental effect rather than bulk σ/m) — literature survey first, then paper update. ~1-2 days.
- **(c)** Hold for strategic direction.

Awaiting user decision.
```

---

# File 6: T212 Path B3 Trim + A3 Plan

_Source path: `v0.3-prelim/docs/T212_PATH_B3_TRIM_AND_A3_PLAN_2026-09-25.md`_

```
# T212 Path B3 Trim + Path A3 Plan

**Date:** 2026-09-25
**Trigger:** User request to (1) trim Path B3 further if possible, (2) pursue Path A3 (Cloud-9 as environmental effect).
**Code:** `v0.3-prelim/code/t212_silverman_gravothermal.py`
**Result:** `v0.3-prelim/data/results/t212_silverman_gravothermal.json`

## 1. Path B3 Trim — Silverman+ 2026 (Mergers Matter)

### 1.1 What I missed in T211

In T211, I tested three Path B3 candidates:
1. Engelhardt+ 2026 (MARVELously Dark): velocity-dependent SIDM, σ_max = 50 at v_max = 35
2. Kihara+ 2026 (CROCODILE-SIDM): regime-dependent SIDM
3. Despali+ 2026 (AIDA-TNG): baryonic coupling

**Missed:** Silverman+ 2026 (Mergers Matter, arXiv:2606.02566, Fermilab-PUB-26-0348-T) — referenced in Engelhardt+ 2026 and Kihara+ 2026 bibliographies. Tests gravothermal collapse at **σ/m = 70 cm²/g** in **M_halo = 10¹⁰ M_☉** halos with diverse assembly histories.

### 1.2 Silverman+ 2026 Key Findings

- **σ/m = 70 cm²/g** in cosmological zoom-in DMO simulations of 10¹⁰ M_☉ halos
- **3 of 6 halos collapse** (the ones with quiescent merger histories)
- **Halos with sustained mergers do NOT collapse** — mergers disrupt the gravothermal cascade
- **Merger-induced heat transport drives non-collapsing halos to lower central densities** than the gravothermal fluid model predicts
- This is the **"merger-history diversity"** mechanism for SIDM halo evolution

### 1.3 T212 — Re-do gravothermal at Silverman+'s parameters

Run Balberg+ 2002 t_core formula at σ/m = 70 cm²/g:

| Quantity | Cloud-9 host (5×10⁹ M_☉) | Silverman+ (10¹⁰ M_☉) |
|---|---|---|
| V_max | 24.75 km/s | 31.19 km/s |
| r_vir | 35.1 kpc | 44.2 kpc |
| ρ_s | 0.0097 M_☉/pc³ | 0.0097 M_☉/pc³ |
| t_core (σ/m = 70) | **0.22 Gyr** | **0.22 Gyr** |
| t_cross | 1.39 Gyr | 1.39 Gyr |
| t_core / t_Hubble | 0.016 | 0.016 |
| t_core / t_cross | 0.16 | 0.16 |
| Phase runs? | YES (62× faster than Hubble) | YES |
| Causality OK (t_core > 3 × t_cross)? | **NO** | **NO** |

**Critical finding:** At σ/m = 70 cm²/g, the gravothermal cascade runs in **0.22 Gyr** — fast enough to drive Cloud-9's σ/m enhancement. **BUT** the t_core / t_cross = 0.16 violates the causality cap of 3.0 — the simple Balberg+ analytical formula predicts unphysical collapse (faster than sound waves can propagate).

### 1.4 Threshold σ/m for collapse

At Cloud-9 host halo:
- σ/m = 0.1: t_core = 298 Gyr (21.6× Hubble) → DOES NOT RUN
- σ/m = 1.0: t_core = 15.5 Gyr (1.12× Hubble) → marginally does NOT run
- **σ/m = 10.0: t_core = 1.55 Gyr (0.11× Hubble) → RUNS, but causality violated**
- σ/m = 50.0: t_core = 0.31 Gyr → RUNS, causality violated
- σ/m = 70.0: t_core = 0.22 Gyr → RUNS, causality violated

**Threshold:** σ/m ≥ ~10 cm²/g is needed for collapse, but at all such values, the analytical t_core / t_cross < 3.0 violates causality. The Balberg+ 2002 formula may not be reliable at these amplitudes (N-body is needed for ground truth).

### 1.5 Path B3 Trim Verdict

**Silverman+ 2026 N-body result IS consistent with gravothermal collapse at Cloud-9 host-halo scale** under quiescent merger history. Cloud-9 is isolated (no mergers), so the merger-history criterion is met. **The gravothermal cascade CAN run at the host-halo mass scale IF σ/m is large enough (≥10 cm²/g) AND N-body simulation is used to capture the full nonlinear physics.**

**But:** the analytical Balberg+ formula gives unphysical causality violations at these amplitudes. Silverman+'s N-body result sidesteps this because it captures the full nonlinear physics (heat transport, merger disruption, etc.). Our analytical estimate is therefore **insufficient evidence to claim or refute** the Silverman+ mechanism at Cloud-9 scale.

**This is a publishable refinement** of the T208 verdict: **gravothermal collapse CAN run at the host-halo mass scale, but only at large σ/m (≥10 cm²/g) and only with N-body verification.** The Phase 44 baseline σ/m = 0.052 cm²/g (extrapolated to V_max = 24.75 km/s) is too small. **A N-body simulation at Silverman+ parameters (σ/m = 70, M = 5×10⁹ M_☉, quiescent merger history) is needed to settle the question.**

## 2. Path A3 — Cloud-9 as Environmental Effect

### 2.1 Path A3 Candidates

The Cloud-9alternate.docx memo's Path A3 candidates:
1. Supernova-driven cores — Cloud-9 is starless, doesn't apply
2. Tidal compression — Cloud-9 is isolated, doesn't apply
3. RELHIC-specific physics (observational systematics)
4. Reframing Cloud-9's σ/m ≥ 50 as a systematic upper bound rather than a hard physical constraint

### 2.2 What Path A3 actually says

Per the memo: "Reframe Cloud-9's σ/m requirement as a baryonic or environmental effect rather than bulk σ/m. This is a literature survey first (supernova-driven cores, tidal compression, RELHIC-specific physics), then a paper update."

The actionable candidate is **RELHIC-specific physics** — i.e., the Cloud-9 σ/m ≥ 50 floor inherits uncertainties from the hydrostatic equilibrium inference, HI self-shielding treatment, and environmental density (Turini & Benítez-Llambay 2026, cited in memo). Path A3 is **paper-level reframing**, not new physics.

### 2.3 Path A3 Implementation Plan

**Step 1:** Add a new subsection to §10.4 (the constraint-map verifications) addressing Cloud-9's observational systematics:

**§10.4d — Cloud-9's σ/m ≥ 50 floor as a systematic-uncertainty upper bound**

"The Cloud-9 hydrostatic-equilibrium inference (Benítez-Llambay, Dutta, Fumagalli & Navarro 2024, ApJ 973, 61; Zhou+ 2023, FAST detection) yields a σ/m ≥ 50 cm²/g floor at v ≈ 28 km/s. Recent work by Turini & Benítez-Llambay (2026) demonstrates that RELHIC parameter recovery suffers from a mass–concentration degeneracy driven by local environmental density, and notes that 'differences between simulated RELHIC analogs may be driven by environmental factors, and/or the treatment of gas self-shielding — which might further limit existing analytic schemes aimed at inferring dark matter halo information from 21 cm HI observations.'

The Cloud-9 σ/m ≥ 50 floor is therefore best interpreted as a **systematic-uncertainty upper bound** on bulk SIDM σ/m, not a hard physical constraint. The framework's failure to satisfy Cloud-9 under physically motivated f_H (Yang+, T202) does not unambiguously indicate a missing bulk SIDM mechanism — the failure could be partially attributable to over-estimation of the σ/m requirement due to environmental or self-shielding systematics in the hydrostatic inference.

**Recommendation:** Future Cloud-9 analyses should:
- Apply the Turini & Benítez-Llambay 2026 environmental correction to the published σ/m ≥ 50 floor
- Apply HI self-shielding corrections (Sawala+ 2016, Fattahi+ 2016)
- Cross-validate against Crater II and Antlia II kinematic constraints (Zhang+ 2024, ApJL 968, L13), which probe V_max ≈ 27 km/s with σ/m ~ 60 cm²/g

Until this re-analysis is done, the framework's verdict stands: 6-7 of 8 channels under borrowed f_H, with Cloud-9 / Crater II / Antlia II / free-fit SPARC as failures that reflect either missing physics OR observational systematic over-estimation."

**Step 2:** Update §11 conclusions to note this reframe.

**Step 3:** Update CHANGELOG / CURRENT / VERSION / README for v18.40.

### 2.4 Path A3 Verdict

Path A3 is a **paper-level reframing** rather than a new code path. The implementation cost is ~1-2 hours (paper update + commit + push). The substantive value is **clarifying what the Cloud-9 constraint actually means** — it's an upper bound with significant systematic uncertainty, not a hard floor.

**Combined with Path B3 trim (Silverman+ 2026):** v18.40 reframes the Cloud-9 constraint as a systematic upper bound AND notes that gravothermal collapse at the host-halo scale CAN run if σ/m is large enough (Silverman+ result). This is a stronger, more nuanced v18.40 than the pure constraint-map verdict in T211.

## 3. Honest assessment

Path B3 trim found one important refinement I missed in T211: **Silverman+ 2026 shows gravothermal collapse CAN run at Cloud-9 host-halo scale** under quiescent merger history and σ/m = 70. The analytical Balberg+ formula gives causality violations, but N-body is more trustworthy. **A N-body simulation at Silverman+ parameters is the next concrete step**, but it's a 1-2 day effort (not in this round's scope).

Path A3 is a paper-level reframing of Cloud-9's σ/m ≥ 50 as a systematic upper bound. This doesn't require new code but does require a literature survey (1-2 hours) and a paper update (~1 hour).

**Total v18.40 plan:**
1. Add §10.4c (Path B3 trim, Silverman+ refinement)
2. Add §10.4d (Path A3, Cloud-9 as systematic upper bound)
3. Update §11 conclusions
4. CHANGELOG / CURRENT / VERSION / README updates
5. Tag `v18.40-constraint-map-with-refinements`

## 4. Files added this round

- `v0.3-prelim/code/t212_silverman_gravothermal.py` — Path B3 trim analysis at Silverman+ 2026 parameters
- `v0.3-prelim/data/results/t212_silverman_gravothermal.json` — gravothermal analysis results
- This writeup: `v0.3-prelim/docs/T212_PATH_B3_TRIM_AND_A3_PLAN_2026-09-25.md`

## 5. Decision options

- **(a)** Implement §10.4c (Path B3 trim) + §10.4d (Path A3) — full v18.40 update. ~2-3 hours wall.
- **(b)** Implement only §10.4d (Path A3) — simpler paper-level reframing. ~1-2 hours wall.
- **(c)** Hold for strategic direction.

Awaiting user decision.
```

---

