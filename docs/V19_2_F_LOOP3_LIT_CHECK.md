# v40.6 — Literature cross-check: 2022-2025 SIDM σ/m constraints (Loop 3)

**Date:** 2026-10-17
**Branch:** `wip/v19.2-F-init`
**Tag:** `v19.2-F-Phase3-CLOSED-r40.6` (pending)

---

## TL;DR

Recent external literature (2022-2025) provides σ/m constraints on the same parameter space the v19.2-F project operates in. The most directly relevant is **Gilman+ 2023 (arXiv:2207.13111, PRD 107, 103008)**, which uses strong gravitational lensing to constrain **core-collapse timing** (not σ/m directly) for resonant SIDM models — the same framework the v19.2-F project uses.

**Important clarification (Nemotron 120B review):** Gilman+ 2023 is **not a direct σ/m constraint**. The paper disfavors scenarios where "a majority of halos core collapse" by z~0.5. A high σ/m is only disfavored *if* it leads to common core collapse. So whether the v19.2-F model is in tension with Gilman+ 2023 depends on the model's predicted core-collapse timing — not just the σ/m value.

**What this means for v40.1-v40.5:** The v40.1-v40.5 IN BAND analysis showed σ/m = 174 cm²/g at v = 29.4 km/s is achievable in the model. This is **necessary but not sufficient** to be consistent with Gilman+ 2023. A complete analysis would compute the model's core-collapse timing and check whether halos in the lensing sample have time to collapse.

**The v19.2-F Phase 3 "FAIL" verdict is a different claim** (no first-principles UV sector reproduces the canonical σ/m at v_target = 29.4 km/s) and is NOT directly comparable to the Gilman+ 2023 observation-based constraint. They address different failure modes (UV completion vs astrophysical prediction).

---

## Method

Searched arXiv and Google Scholar for 2022-2026 SIDM σ/m constraints. Focused on:
- Resonant SIDM (the framework the v19.2-F project uses)
- Constraints on σ/m at velocities relevant to UFDs/dSphs (v < 30 km/s)
- Recent 2025-2026 cluster and lensing constraints

---

## Key external constraints found

### Gilman+ 2023 (arXiv:2207.13111, PRD 107, 103008)

**Title:** "Constraining resonant dark matter self-interactions with strong gravitational lenses"
**Method:** Quadruply-imaged quasars (11 lenses), core-collapse timing analysis
**Framework:** Yukawa potential V(r) = ±α_χ e^(-m_φ r) / r (SAME as v19.2-F)
**Key result (verbatim from abstract):** "Our data strongly disfavors scenarios in which a majority of halos core collapse, with the strongest constraints obtained for cross section strengths exceeding 100 cm²/g at relative velocities below 30 km/s."

**Critical clarification (Nemotron 120B review):** Gilman+ 2023 is a **core-collapse TIMING constraint, not a direct σ/m constraint**. The paper's observable is the fraction of core-collapsed halos in the strong-lensing sample. The constraint disfavors scenarios where this fraction is high at z~0.5. A high σ/m is only disfavored *if* it leads to common core collapse — i.e., the constraint is on the combination (σ/m × core-collapse time) for the relevant halo mass range, not on σ/m alone.

**Implication for v40.1-v40.5:** The IN BAND analysis finds σ/m = 174 cm²/g at v = 29.4 km/s. This is **necessary but not sufficient** to be consistent with Gilman+ 2023. To check consistency, the project's model would need to predict the core-collapse timing at the relevant halo masses (~10⁷-10⁹ M☉) and check whether the predicted fraction of collapsed halos matches Gilman+ 2023's allowed region.

The v19.2-F project has a gravothermal t_c analysis (`v19_2_e_b_per_halo_gravothermal.py`) but it uses a different σ_m formula (Gaussian) than the IN BAND analysis (Breit-Wigner resonance). A coherent gravothermal t_c with the Breit-Wigner formula would be needed to fully address the Gilman+ 2023 constraint. This is a follow-up loop.

### O'Donnell+ 2025 (arXiv:2508.20179)

**Title:** "A Constraint on Dark Matter Self-Interaction from Combined Strong Lensing and Stellar Kinematics in MACS J0138-2155"
**Method:** Strong lensing + stellar kinematics on a single galaxy cluster
**Key result:** New constraint on σ/m in the cluster regime (v ~ 1000 km/s)
**Implication for v19.2-F:** Adds to the cluster-side constraint (σ/m < 0.1-1.0 cm²/g at v ~ 1000 km/s). Not directly relevant to the IN BAND analysis at v < 30 km/s, but constrains the high-velocity end of any velocity-dependent σ/m model.

### Sánchez Almeida+ 2025 (A&A 2025/12/aa57040)

**Title:** "Constraints on dark matter models from the stellar cores"
**Method:** Stellar core observations in dwarf galaxies
**Key result:** Constraints on σ/m in the dwarf regime (v ~ 10 km/s)
**Implication for v19.2-F:** 8 citations as of 2026-10-17. Provides observational context for the dwarf-σ/m tension.

### arXiv 2605.00093 (cluster double radio relic, 2025)

**Title:** "A New Robust Constraint on the Self-interaction Cross-section of Dark Matter with Double Radio Relic Clusters"
**Method:** 352 cluster regions from TNG-Cluster (1 Gpc)³ simulation
**Key result:** "Constraint in mild tension with existing SIDM models that require σ/m ≳ 1 cm²/g to resolve small-scale discrepancies in dwarf and spiral galaxies"
**Implication for v19.2-F:** Cluster-side constraints continue to tighten. The 2025 result is in **mild tension** with dwarf-side requirements. The v19.2-F IN BAND analysis at σ/m = 174 cm²/g, v = 29.4 km/s is on the high-σ/m side of the dwarf requirement, and is therefore in additional tension with this cluster constraint (because a velocity-dependent σ/m must decrease from 174 cm²/g at v = 30 km/s to < 1 cm²/g at v = 1000 km/s — a 174× drop over 30× velocity increase).

---

## Tension matrix (revised per Nemotron 120B review)

| v19.2-F claim | External constraint | Status |
|---|---|---|
| σ/m = 174 cm²/g at v = 29.4 km/s (IN BAND) | Gilman+ 2023: core-collapse timing disfavored (high σ/m disfavored only if many halos collapse) | **POTENTIAL TENSION** (depends on model's predicted core-collapse timing; not yet computed) |
| Same model, cluster side | O'Donnell+ 2025 + arXiv 2605.00093: σ/m < 0.1-1.0 cm²/g at v ~ 1000 km/s | **NO DIRECT TENSION** (project hasn't claimed a cluster-scale result; v_target = 29.4 km/s, not 1000 km/s) |
| Segue 1 IN BAND (v40.4) | Same as Cloud-9 above (lower v, same regime) | **POTENTIAL TENSION** (same caveat) |
| Phase 3 "FAIL" verdict | Gilman+ 2023, O'Donnell+ 2025, etc. | **DIFFERENT CLAIMS** (FAIL = UV sector shortcoming; Gilman+ = observational core-collapse timing; not directly comparable) |

The original draft marked several rows as "TENSION" or "CONSISTENT"; the more accurate framing is **POTENTIAL TENSION** (depends on uncalculated core-collapse timing) and **DIFFERENT CLAIMS** (FAIL verdict is about UV sector, not about lensing data). The v19.2-F IN BAND analysis is not in direct conflict with external constraints, but it is not yet fully compared against them either.

---

## Implication for the v40.1-v40.5 work

The v40.1-v40.5 IN BAND analysis showed that the canonical α_D=5.55e-6 (with Breit-Wigner resonance formula) gives σ/m = 174 cm²/g at v = 29.4 km/s at Γ/ρ ∈ {5, 6, 7, 8}, and is IN BAND at all 10 UFDs/dSphs tested. **External constraints (Gilman+ 2023, O'Donnell+ 2025) suggest this parameter space is disfavored if many halos have already core-collapsed.** The v19.2-F Phase 3 verdict is consistent with this external tension.

**The v40.1-v40.5 work should be re-interpreted in light of the external constraints:**
- The IN BAND analysis shows the model can match the data, but does not show that the model is observationally viable in the lensing/cluster regime.
- A more complete analysis would: (a) compute core-collapse timing across the halo mass range, (b) check against Gilman+ 2023's core-collapse disfavoring, (c) check the velocity-dependent σ/m at v = 1000 km/s against the cluster constraints.

This is consistent with the v19.2-F Phase 3 verdict and the "look-elsewhere" caveat in v40.5 (Loop 2): the IN BAND analysis is a consistency check, not a discrimination test against external data.

---

## What the v19.2-F project should compare against (revised per Nemotron 120B review)

External SIDM constraint papers that should be cited/compared:
- **Gilman+ 2023** (arXiv:2207.13111, PRD 107, 103008) — strong lensing, resonant SIDM, core-collapse timing ← **most relevant, same framework**
- **O'Donnell+ 2025** (arXiv:2508.20179) — single cluster, lensing+kinematics
- **Sánchez Almeida+ 2025** (A&A 2025/12/aa57040) — stellar cores
- **arXiv:2605.00093** (2025) — double radio relic clusters
- **Andrade+ 2022** (MNRAS 510, 54) — "stringent upper limit on dark matter self-interaction cross-section" (149 citations) — established the dwarf-vs-cluster tension
- **Kaplinghat+ 2016** (the original velocity-dependent SIDM paper, ~600 citations) — should be in the v19.2-F bibliography

**Recommended next step (revised):** before adding a Gilman+ comparison section to the v19.2-F paper, the project should:
1. Compute the model's predicted core-collapse timing at the relevant halo masses (~10⁷-10⁹ M☉) using the Breit-Wigner resonance σ/m formula (this is a separate, non-trivial calculation).
2. Compare the predicted collapsed-halo fraction to Gilman+ 2023's allowed region.
3. If the model is disfavored, discuss the implications for the canonical α_D.
4. If the model is allowed, cite Gilman+ 2023 as an external consistency check.

This is **out of scope for Loop 3** but is the natural follow-up loop that would close the comparison with external literature.

---

## Files

- **This doc:** `docs/V19_2_F_LOOP3_LIT_CHECK.md`
- **Saved reference:** `~/.hermes/cache/web/arxiv.org-61f7c5945d.md` (Gilman+ 2023 full text)
