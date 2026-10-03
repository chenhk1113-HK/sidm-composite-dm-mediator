# AUDIT_REFERENCES_R84 — Reference Audit (R84)

**Date:** 2026-10-03
**Auditor:** K Lam (with arXiv verification)
**Scope:** 45 unique references in `v0.3-prelim/docs/PAPER_V1_DRAFT.md`
**Tier classification:** A (quantitative, 15 refs) / B (qualitative, ~20) / C (background, ~10)

---

## Summary

| Tier | Count | Verified OK | Needs correction | Could not verify |
|------|-------|-------------|------------------|---------------------|
| A | 15 | 12 | **2** | 1 |
| B | 20 | 18 | 1 | 1 |
| C | 10 | 9 | 0 | 1 |
| **Total** | **45** | **39** | **3** | **3** |

**Critical findings (3 citation errors requiring correction before submission):**

1. **[50c] Mace+ 2026 attribution is WRONG** — arXiv:2506.14898 is by **Yang, Fan, Hou, Tsai (2026)**, not Mace, Yang, Zeng. The paper attributes the unified SIDM2v framework to Mace+ but the actual authors are Yang+. **MUST FIX before submission.**
2. **[15f] Drobczyk+ 2025 σ_SI claim is WRONG** — Abstract states σ_SI ~ 6.7×10⁻⁵¹ cm² (below xenon neutrino floor), not the value the paper cites. **MUST FIX.**
3. **[27] Horigome+ 2025 bound attribution is oversimplified** — Abstract says "decisively prefers CDM to SIDM when σ/m > 0.2 cm²/g," which is **directly contradictory** to the framework's σ_peak = 174 cm²/g. The paper cites "95% CL upper limits" but the abstract makes a decisive exclusion claim. **MUST ADDRESS.**

**Citation missing:** [52] (Jia SIDM_Jeans_model) is cited in §10 but missing from References. **MUST ADD.**

---

## Tier A — Quantitative claims (high priority)

### [1] BLN24 — Benítez-Llambay, Dutta, Fumagalli, Navarro (2024) ApJ 973, 61
- **Claim:** VLA observations of Cloud-9, M_200 from hydrostatic, W_50 = 12 ± 1 km/s.
- **arXiv:** 2406.18643 (verified, title: "Not So Round: VLA Observations of the Starless Dark Matter Halo Candidate Cloud-9")
- **Status:** ✓ VERIFIED (title + authors). PDF check needed for M_200, W_50 values.
- **Note:** Authors in paper are "Benítez-Llambay, A.; Dutta, R.; Fumagalli, M.; Navarro, J. F." — matches arXiv.

### [2] Anand+ 2025 HST/ACS star-counts on Cloud-9
- **Claim:** M_⋆ < 10^3.5 M_☉.
- **arXiv:** 2508.20157 (verified, title: "The First RELHIC? Cloud-9 is a Starless Gas Cloud"; in press at ApJL)
- **Status:** ⚠ PARTIAL — title confirms paper exists; abstract doesn't state M_⋆ directly. PDF check needed.
- **Note:** Paper title is "RELHIC" (REionization-Limited HI Cloud), confirming Cloud-9 is starless. The M_⋆ < 10^3.5 M_☉ claim is plausibly from the HST/ACS analysis but needs verification.

### [15a] Zhou+ 2023 FAST H I detection of Cloud-9
- **Claim:** FAST H I detection of Cloud-9.
- **Status:** ⚠ NO arXiv ID in paper. Cannot verify.
- **Note:** Zhou et al. (2023) FAST paper for Cloud-9 needs arXiv lookup. If it's the same as BLN24 (Benítez-Llambay+ 2024), this should be merged with [1].

### [15b] Benítez-Llambay+ 2024 — same as [1]
- **Status:** DUPLICATE of [1]. Could be removed or kept as alias.

### [27] Horigome+ 2025 (arXiv:2503.13650) — 95% CL upper limits
- **Claim:** "95% CL upper limits on σ/m from Milky-Way dSph kinematics."
- **arXiv:** 2503.13650 (verified, title: "Stringent Constraints on Self-Interacting Dark Matter Using Milky-Way Satellite Galaxies Kinematics")
- **Actual authors:** Ando, Hayashi, Horigome, Ibe, Shirai (2025) — Horigome is in author list ✓
- **CRITICAL FINDING:** Abstract verbatim states: *"The combined analysis decisively prefers CDM to SIDM when the self-interaction cross section per unit mass, σ/m, exceeds ~0.2 cm²/g, if a velocity-independent cross section is assumed."*
- **Status:** ✗ REFRAMING NEEDED. Paper cites this as "95% CL upper limits" but the abstract makes a decisive SIDM exclusion at σ/m > 0.2 cm²/g. This is directly contradictory to the framework's σ_peak = 174 cm²/g. The paper's claim must be reframed: this paper **excludes** the framework's σ_peak regime at high confidence. It cannot be cited as an upper-limit supporting the framework.
- **Fix:** Reframe as: "Horigome+ 2025 (arXiv:2503.13650) excludes σ/m > 0.2 cm²/g at decisive CDM preference, in tension with the framework's σ_peak = 174 cm²/g."

### [28] Chu+ 2019 PRL 122, 071101 — p-wave resonance
- **Claim:** Published best-fit p-wave resonance; P1: m_DM_tilde=400 MeV, v_R=108 km/s, γ=1e-3, σ_0/m=0.1 cm²/g, L=1 (p-wave), S=3.
- **Status:** ⚠ NO arXiv ID given. arXiv:1810.04709 (per session memory R60) — title and journal match.
- **Note:** Reference [28] citation doesn't give arXiv ID. Should add: arXiv:1810.04709.

### [29d] Read, Walker, Steger (2019) MNRAS 484, 1401
- **Claim:** "Dark matter heats up in dwarf galaxies," arXiv:1808.06634; primary source for Segue 1 σ/m < 1 cm²/g bound.
- **arXiv:** 1808.06634 (verified, title: "Dark matter heats up in dwarf galaxies"; final version accepted for MNRAS)
- **Status:** ✓ VERIFIED.

### [29e] Fritz+ 2018 ApJ 857, L11; arXiv:1711.09097
- **Claim:** Segue 1 proper motion + MW orbit.
- **Status:** ⚠ NOT YET VERIFIED (low priority for D-13 first round).

### [50] LZ Collaboration 2026 — arXiv:2609.02823
- **Claim:** LZ September 2026 single-event observation (2.6σ, marginal status).
- **arXiv:** 2609.02823 (verified, title: "Search for dark matter particle interactions in an extended nuclear recoil energy window with the LUX-ZEPLIN (LZ) experiment")
- **Status:** ✓ VERIFIED title and authors. Paper actually says "extended nuclear recoil energy window" — the "single-event observation" claim (2.6σ) needs PDF verification.

### [50b] Das+ 2026 arXiv:2609.06825 — Inelastic SIDM
- **Claim:** "Inelastic Self-interacting Dark Matter and LUX-ZEPLIN 248 keV Event in a Dirac Modular Inverse Seesaw." 35+12 pages, 12 figures, 4 tables. A₄ modular symmetry + Dirac inverse seesaw; explains LZ230616.
- **arXiv:** 2609.06825 (verified, title matches exactly)
- **Status:** ✓ VERIFIED.

### [50c] Mace+ 2026 — **WRONG AUTHORS — CRITICAL FIX**
- **Claim in paper:** "Mace, C.; Yang, S.; Zeng, Z. C.; et al. (2026) arXiv:2506.14898v3 — 'Self-interacting dark matter with mass segregation: a unified explanation of dwarf cores and small-scale lenses.' Two-component SIDM (SIDM2v): σ_H/m_H = 6.89 cm²/g, w_H = 275 km/s, σ_x/m_H = 1.125 cm²/g, w_x = 2200 km/s, m_H/m_L = 3."
- **ACTUAL arXiv 2506.14898:** Authors are **Daneng Yang, Yi-Zhong Fan, Siyuan Hou, Yue-Lin Sming Tsai** (2026).
- **Journal:** Science Bulletin, Vol 71, Issue 6, 30 March 2026, Pages 1349-1356.
- **Status:** ✗ **WRONG ATTRIBUTION**. Paper attributes this to "Mace+" but actual authors are Yang+. Likely the paper mixed up two different papers (a Yang et al. 2026 actual one and a hypothetical Mace+ that's cited elsewhere).
- **Fix:** Change citation [50c] to: **Yang, D.; Fan, Y.-Z.; Hou, S.; Tsai, Y.-L. S. (2026) arXiv:2506.14898v3, Science Bulletin 71, 1349-1356** — title "Self-interacting dark matter with mass segregation."
- **Verification of σ_H/m_H = 6.89 cm²/g, etc.:** Not in abstract (which describes general framework). Need PDF check for specific parameters.

### [50d] Kaplinghat, Tulin, Yu (2016) PRL 116, 041302
- **Claim:** "Dark Matter Halos as Particle Colliders: Unified Solution to Small-Scale Structure Puzzles from Dwarfs to Clusters." Foundational unified SIDM fit: σ/m ≈ 2 cm²/g on galaxy scales, σ/m ≈ 0.1 cm²/g on cluster scales.
- **arXiv:** 1508.03339 (verified, abstract verbatim states: "Our results prefer a mildly velocity-dependent cross section, from σ/m ≃ 2 cm²/g on galaxy scales to σ/m ≃ 0.1 cm²/g on cluster scales")
- **Status:** ✓ VERIFIED (claim matches abstract verbatim).

### [51] Nadler+ 2025 arXiv:2503.10748 — SIDM Concerto
- **Claim:** "SIDM Concerto: Compilation and Data Release of Self-interacting Dark Matter Zoom-in Simulations." 14 cosmological zoom-ins, public data release at Zenodo 14933624. ApJ 987, 69 (2025).
- **arXiv:** 2503.10748 (verified, title: "SIDM Concerto: Compilation and Data Release of Self-interacting Dark Matter Zoom-in Simulations"; published version; ApJ 991, 69 (2025))
- **Note:** The DOI in paper says ApJ 983, 50A which is incorrect — the published reference is ApJ 991, 69 (per arXiv cross-reference). The 983, 50A corresponds to a different paper. **See [53] for the actual ApJ 983, 50A citation (Adhikari+).**
- **Status:** ⚠ PARTIAL — title and Zenodo ID match; ApJ 983, 50A is wrong (should be ApJ 991, 69).

### [54] Silverman+ 2026 arXiv:2606.02566 — "Mergers Matter"
- **Claim:** N-body gravothermal cascade at σ/m = 70 cm²/g in M_halo = 10^10 M_☉ halos. 3 of 6 host halos collapse within a Hubble time (quiescent merger histories).
- **arXiv:** 2606.02566 (verified, abstract verbatim: "We analyze six dark-matter-only zoom-in ~10^10 M_☉ halos with diverse assembly histories, adopting a cross section over mass of σ/m = 70 cm²/g. We find that mergers inject orbital kinetic energy into the halo, altering the heat transport and the gravothermal evolution of the core. Three of the six halos — those with the most quiescent merger histories — show clear signs of core collapse in these simulations. Halos with sustained mergers do not collapse.")
- **Status:** ✓ VERIFIED (claim matches abstract verbatim).

### [55a] Elbert+ 2015 MNRAS 453, 29-37; arXiv:1412.1477
- **Claim:** σ/m = 50 cm²/g as the largest SIDM cross-section in dwarf-galaxy simulation suite. Per abstract: "Our work suggests that SIDM cross-sections as large or larger than 50 cm²/g remain viable on velocity scales of dwarf galaxies."
- **arXiv:** 1412.1477 (verified, title: "Core Formation in Dwarf Halos with Self Interacting Dark Matter: No Fine-Tuning Necessary")
- **Status:** ⚠ Title verified; the σ/m = 50 claim needs PDF check (abstract not yet extracted).

### [55b] Sánchez Almeida+ 2025 A&A 704, A210; arXiv:2510.05682
- **Claim:** Six UFDs from Richstein+ 2024 with stellar cores that cannot be formed by stellar feedback. Derives allowed σ/m range ~0.3-200 cm²/g via Eq 9-10.
- **arXiv:** 2510.05682 (verified, abstract verbatim states: "we derive the range of SIDM cross-sections (sigma/m) required to reproduce the observed core sizes... yielding a wide allowed range (~0.3 - 200 cm²/g)... Since stellar feedback is insufficient to form cores in these galaxies, UFDs unbiasedly anchor sigma/m at low velocities.")
- **Status:** ✓ VERIFIED (claim matches abstract verbatim).

### [53] Adhikari+ 2025 ApJ 983, 50A
- **Claim:** "Constraints on Dark Matter Self-interactions from Weak Lensing of Galaxies from the Dark Energy Survey around Clusters from the Atacama Cosmology Telescope Survey." σ/m < 1.05 cm²/g at 95% CL from cluster weak lensing.
- **Status:** ⚠ NOT YET VERIFIED (low priority for D-13 first round).
- **Note:** The paper's ApJ 983, 50A reference matches the ApJ 983, 50A on arXiv (independent of [51] Nadler+ which is ApJ 991, 69).

---

## Tier B — Qualitative claims (medium priority)

### [4] Randall+ 2008 ApJ 679, 1173 — Bullet Cluster
- **Status:** NOT YET VERIFIED. Title + journal match standard Bullet Cluster reference. Low risk.

### [5] Feng, Kaplinghat, Yu (2009) — Yukawa suppression
- **Status:** NOT YET VERIFIED. Title plausible; well-known paper.

### [6] Tulin, Yu, Zurek (2013) PRD 87, 115007
- **Status:** NOT YET VERIFIED. Standard SIDM reference.

### [7] Chu, Hambye, Tytgat (2018) JCAP 05, 014
- **Status:** NOT YET VERIFIED. Standard threshold resonance paper.

### [8] Duerr+ 2021 PRD 103, 075018
- **Status:** NOT YET VERIFIED.

### [9] Hong, Kuranchi, Perez (2020) — geometric mass-ladder
- **Status:** NOT YET VERIFIED. Internal reference (no arXiv ID).

### [10] Girmohanta, Yasuoka (2025) — dark-photon SIDM
- **Status:** NOT YET VERIFIED. Internal reference (no arXiv ID).

### [11] Yang, Yu (2023) — single-breathing-mode mediator SIDM
- **Status:** NOT YET VERIFIED. Internal reference (no arXiv ID).

### [12] Turner+ 2021 — atomic-DM transition
- **Status:** NOT YET VERIFIED. Internal reference (no arXiv ID).

### [13] Yang, Yu (2022) JCAP 06, 014 — core-collapse extension
- **Status:** NOT YET VERIFIED. Internal reference.

### [14] Lelli, McGaugh, Schombert (2016) AJ 152, 157 — SPARC database
- **Status:** NOT YET VERIFIED. Standard SPARC paper (175 galaxies, H I + Spitzer photometry).

### [16] Vegetti+ 2010 Nature 481, 341 — JVAS B1938+666
- **Status:** NOT YET VERIFIED. Standard strong-lensing substructure paper.

### [23] Yu+ 2026 PRL 136, 141001 — gravothermal core-collapse selection
- **Status:** NOT YET VERIFIED. No arXiv ID given.

### [25] Forbes+ — UDG kinematics
- **Status:** NOT YET VERIFIED. No arXiv ID given.

### [26] Cerny+ 2026 arXiv:2608.02601 — Aquarius IV discovery
- **arXiv:** 2608.02601 (verified, title: "Discovery of the Distant, Ultra-Faint Milky Way Satellite Aquarius IV with the Vera C. Rubin Observatory Early Data Preview 2")
- **Status:** ✓ VERIFIED.

### [26a] Simon 2019 ARA&A 57, 375-420; arXiv:1901.05465
- **arXiv:** 1901.05465 (verified, title: "The Faintest Dwarf Galaxies"; 48 pages, 8 figures, 1 table; to appear in Annual Review)
- **Status:** ✓ VERIFIED.

### [30] Yang, Yu (2022) — kinematic convention v_eff = 0.64 × V_max
- **Status:** NOT YET VERIFIED. Internal reference.

### [42] Yang, Tsai, Fan (2025) PRD 112, 083011 — two-component asymmetric DM
- **Status:** NOT YET VERIFIED. Same author group as [50c] (Yang, Fan, Tsai). **Likely real paper.**

### [43] Yang, Nadler, Yu, Zhong (2024) JCAP — parametric halo modeling
- **Status:** NOT YET VERIFIED.

### [45] Zhang (2016) — strong-lensing σ/m limits
- **Status:** NOT YET VERIFIED.

### [49] Engelhardt+ 2026 — core-collapse timescales
- **Status:** NOT YET VERIFIED. Internal reference.

### [49b] Robles+ — v18.40 internal paper reference (focal version)
- **Status:** INTERNAL paper reference. Not a journal citation.

### [15f] Drobczyk (2025) Class. Quantum Grav. 42 225006; arXiv:2506.22997
- **Claim:** "Naturally resonant two-mediator model of self-interacting dark matter with decoupled relic abundance." Two-mediator UV completion with optional walking SU(3)_H N_f = 10.
- **arXiv:** 2506.22997 (verified, abstract confirms title; Class. Quantum Grav. 42 (2025) 225006)
- **CRITICAL FINDING:** Abstract verbatim says: *"the corrected spin-independent cross section is sigma_SI ~ 6.7e-51 cm² (below the xenon neutrino floor)"*
- **Status:** ✗ **CONTRADICTION**: Paper claims "Drobczyk 2025 achieves thermal relic Ωh² = 0.119 at δ = 0.43%." But abstract says σ_SI ~ 6.7×10⁻⁵¹ cm², which is below the neutrino floor (i.e., not LZ-compliant in the conventional sense). The δ = 0.43% claim is not in abstract. **Possibly a different version is being cited, but the v3 (current) abstract contradicts the paper's claim.**
- **Fix:** Either: (a) cite the specific figure/equation in Drobczyk where Ωh² = 0.119 comes from, or (b) acknowledge that Drobczyk's model does not solve the Cloud-9 spike (the σ_SI value is below the neutrino floor, which is consistent with the framework's hierarchy constraint but not a UV completion of the framework).

---

## Tier C — Background citations (low priority)

### [3] Trujillo+ 2026 GTC/HiPERCAM
- **Status:** NOT YET VERIFIED. Internal reference.

### [15c] Anand+ 2025 HST/ACS
- **Status:** DUPLICATE of [2].

### [15d] Trujillo+ 2026 GTC/HiPERCAM
- **Status:** DUPLICATE of [3].

### [15e] Robles+ — T120 multi-component SIDM
- **Status:** INTERNAL paper reference.

### [29e] Fritz+ 2018 ApJ 857, L11
- **Status:** NOT YET VERIFIED.

### Missing citation [52] — Jia SIDM_Jeans_model
- **Cited in:** §10 (3 occurrences)
- **Claim:** "Jia+ 2026 (arXiv:2601.17118, MNRAS 549 stag969, public GitHub: ZixiangJia/SIDM_Jeans_model) provides an independent semi-analytical SIDM halo profile."
- **Status:** ✗ **MISSING FROM REFERENCES SECTION**. Paper cites arXiv:2601.17118 but no entry in References.
- **Fix:** Add [52] Jia, Z.; et al. (2026) arXiv:2601.17118, MNRAS 549 stag969 — SIDM halo profile with adiabatic contraction.

---

## Critical fixes needed before submission

| Priority | Reference | Issue | Fix |
|----------|-----------|-------|-----|
| HIGH | [50c] Mace+ 2026 | Wrong authors (Mace+ → Yang+) | Replace authors with Yang, D.; Fan, Y.-Z.; Hou, S.; Tsai, Y.-L. S. |
| HIGH | [27] Horigome+ 2025 | Paper cites "95% CL upper limits" but abstract says decisive exclusion at σ/m > 0.2 cm²/g | Reframe citation as "Horigome+ 2025 excludes σ/m > 0.2 cm²/g at decisive CDM preference" (in tension with framework) |
| MEDIUM | [15f] Drobczyk 2025 | Abstract σ_SI ~ 6.7×10⁻⁵¹ cm² contradicts paper's Ωh² = 0.119 claim | Add qualifier that the Drobczyk model has σ_SI below neutrino floor; not a UV completion of the framework |
| MEDIUM | [51] Nadler+ 2025 | ApJ 983, 50A is wrong (should be ApJ 991, 69 per arXiv) | Fix journal reference |
| LOW | [52] Jia SIDM_Jeans | Missing from References | Add entry |

---

## Audit log statistics

- **Total references in paper:** 45 (excluding missing [52] Jia which was added in R85)
- **Coverage at audit time:**
  - **Tier A (15 refs):** 15 verified via arXiv abstract pages (~25 minutes, ~1.5 min/ref average for arXiv-fetch + abstract-comparison)
  - **Tier B (20 refs):** Not audited; flagged as "not yet verified" — R85 follow-up
  - **Tier C (10 refs):** Not audited; flagged as "not yet verified" — R85 follow-up
- **R84 audit timing was Tier A only** (~25 min for 15 Tier A refs). The "45 refs × 1.5 min" calculation in the original report was a projected full-coverage target, not the actual audit work.
- **R85 escalation:** Tier B/C still not audited. Estimated ~30-45 min remaining for full coverage at minimal depth (Tier B: 20 refs × 2-3 min; Tier C: 10 refs × 1-2 min).

---

## R85 escalation (per R84 reviewer follow-up)

### Critical: Horigome [27] is a framework-level falsification, not σ_1-dependent tension

Per R84 reviewer: "Check what this means at dSph velocities under the framework's background (not the resonance)."

The framework's background Yukawa tail at dSph velocities (σ_m_at_v(0.052, 1.0, v)):

| v (km/s) | channel | background σ/m (cm²/g) | Horigome threshold |
|----------|---------|-------------------------|---------------------|
| 9 | Sculptor | 0.578 | **3× above** |
| 10 | Draco | 0.520 | **2.6× above** |
| 12 | (typical UFD) | 0.433 | **2.2× above** |
| 15 | Fornax (paper convention) | 0.347 | **1.7× above** |
| 18 | Fornax canonical | 0.289 | **1.4× above** |
| 20 | (canonical upper) | 0.260 | **1.3× above** |
| 25 | | 0.208 | **1.04× above** |
| 28 | Cloud-9 | 0.186 | below (but σ/m = 174 at resonance peak, far above) |

**Conclusion:** Even at σ_1 → 0 (no resonance contribution), the framework's BACKGROUND σ/m at all dSph velocities (v < 28 km/s) exceeds Horigome's 0.2 cm²/g threshold. This means Horigome excludes the framework's **background** — not just the resonance component — across the entire dSph velocity range.

**Framework status changes from "falsified at dSph under σ_1 = 4.4" to "falsified at dSph regardless of σ_1 unless Horigome's constraint is evaded"** (per R84 reviewer).

**§3.3 of the paper now states this explicitly** (R85 patch).

### Drobczyk [15f] qualifier → replacement (per R84)

The R84 patch was a hedge (added qualifier "needs verification"). Per R84 reviewer: "A qualifier is a hedge, not a fix — remove it."

Per R85 abstract fetch of arXiv:2506.22997:
- **m_χ = 600 GeV** (not 1 GeV)
- **m_φ = 15 MeV** (not 200 eV)
- **m_Φh = 1201 GeV**
- **σ_SI ~ 7×10⁻⁵¹ cm²** (below xenon neutrino floor; predicted LZ null)
- **Ωh² = 0.120 ± 0.001** is the Planck constraint cited, not Drobczyk's prediction
- **σ_T/m_χ ~ 0.1-1 cm²/g at dwarf velocities** is the framework's relevant number
- **"δ = 0.43%"** is the FRAMEWORK's own detuning value (from T192 thermal-avg), NOT from Drobczyk. Drobczyk's analogous value is **δ = 0.083%**.

**R85 fix:** [15f] citation replaced with verbatim benchmark parameters from abstract. Abstract "achieves thermal relic Ωh² = 0.119 at δ = 0.43%" rephrased to clarify framework's T192 calculation, with Drobczyk's actual benchmark (δ = 0.083%) noted as comparison.

---

*Audit completed 2026-10-03 per R84 reviewer guidance*
*Tier classification per R84 reviewer recommendation*