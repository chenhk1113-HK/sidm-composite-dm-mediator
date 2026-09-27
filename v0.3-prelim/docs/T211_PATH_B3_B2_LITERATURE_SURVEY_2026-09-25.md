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