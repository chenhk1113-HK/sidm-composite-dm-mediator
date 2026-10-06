# Gravothermal Evolution Roadmap (R88, G1-G6)

**Companion document to the SIDM Composite DM Mediator paper (v19.2-D, R88).**

This roadmap implements the central insight from the Cloud-9 vs. dSph tension analysis:

> **The observed Cloud-9 vs. dSph tension is not a fitting failure — it is a symptom of static σ/m(v) modeling. Halos at the same σ/m(v) show diverse central densities because they are at *different gravothermal phases* (core-expansion vs. collapse). A phase-aware pipeline that incorporates merger history and formation redshift can convert the apparent tension into evidence for gravothermal evolution.**

**Sources**:
- Fischer & Yu (2026), A&A 711, A68 — UFD gravothermal collapse simulations
- Silverman et al. (2026), arXiv:2606.02566 — merger history and collapse
- Yan, Nadler, Yu & Zhong (2024), arXiv:2305.16176 — parametric density model
- Yang & Yu (2022), arXiv:2204.04356 — velocity-dependent conductivity
- Balberg, Shapiro, Inoue (2002), PRL 88, 101301 — conducting fluid model
- Koda & Shapiro (2011), MNRAS 415, 1125 — gravothermal instability
- Ohana, Zhang & Yu (2026), arXiv:2608.04362 — Cloud-9 SIDM analysis
- Gurian & May (2025), arXiv:2505.15903 — KiSS-SIDM (kinetic regime)

---

## Phase G1 — Calibrated Gravothermal Model (Weeks 1-3)

**Status**: SCAFFOLD in `v0.3-prelim/code/gravothermal_evolution.py`.

**Deliverable**: A module that, given a CDM halo (M, c, z_form) and σ/m(v), returns the central density and core radius at z = 0 by integrating the gravothermal fluid equations, calibrated against Yang+ 2024.

**Method**:
- Implementing the conducting-fluid formalism (Balberg+ 2002, Koda-Shapiro 2011) with velocity-dependent conductivity from Yang & Yu (2022).
- Calibrating against the parametric model of Yang, Nadler, Yu & Zhong (2024) arXiv:2305.16176 (analytic density profile covering core-forming, max-core-expansion, and core-collapsed phases).
- Fast parametric model for likelihood scans; numerical fluid model for working density profile.

**Immediate check**: Fornax-like parameters (M ~ 10⁹ M☉, σ/m ~ 2-5 cm²/g at V_max) should predict collapsed or near-collapsed core, consistent with the paper's t_core ≈ 0.78 Gyr finding (verified in scaffold).

---

## Phase G2 — Merger History as Stochastic Variable (Weeks 3-6)

**Status**: SCAFFOLD (merger_history_modulator() in gravothermal_evolution.py).

**Deliverable**: A merger-history sampler that assigns each halo a quiescent or active merger flag from a mass- and redshift-dependent distribution.

**Method**:
- Silverman et al. (2026) find sustained mergers suppress collapse. Implement as multiplicative delay factor on gravothermal time.
- For MW satellites: use galstreams catalog (Mateu 2023) and orbital parameters to assign pericentre distances.
- Tidal stripping acceleration (Nishikawa+ 2020) as secondary modifier.

---

## Phase G3 — Re-analyze Cloud-9 with Phase-Aware Priors (Weeks 6-9)

**Status**: NOT STARTED.

**Deliverable**: Re-analysis of Cloud-9 that does not require σ/m(28) ≥ 50 cm²/g as a hard floor. Instead: what σ/m(v) AND what phase (core-forming vs. collapsed) best reproduce the observed H I column-density profile?

**Method**:
- Use Ohana+ 2026 MCMC framework for Cloud-9, but replace static SIDM halo profile with gravothermal-evolved profile from Phase G1.
- Likelihood has two new parameters: formation redshift z_form and merger flag.
- Marginalize over both.

**Expected outcome**: Cloud-9 may be consistent with a larger σ/m than the current pipeline suggests, provided it is in core-expansion phase with a recent formation or merger-perturbed history.

---

## Phase G4 — Reframe 8-Channel Fit as Phase-Diversity Fit (Weeks 9-12)

**Status**: NOT STARTED.

**Deliverable**: Revised joint likelihood where each channel is assigned a phase prior based on observed density and kinematics. The fit then constrains σ/m(v) AND the phase distribution, not σ/m alone.

**Method**:
- For each observed halo (SPARC galaxies, dSphs, UFDs, clusters), compute phase diagnostic — e.g., central density to maximum core-expansion density ratio.
- Halos with high central densities → collapsed phase; low → core-expanding.
- Use as prior on gravothermal phase.

**Key improvement**: Removes artificial tension between Cloud-9 (low-density, expanding) and Fornax (high-density, collapsed). They no longer share the same σ/m AND phase.

**Predicted phase assignment** (R88 scaffold):

| Halo | Phase | σ/m at kinematic v (Phase 44) | Observed central density |
|------|-------|-------------------------------|---------------|
| Cloud-9 | core-expansion | 166 cm²/g at v=28 | low (RELHIC, fossil) |
| Fornax | near-collapse | 2.85 cm²/g at v=15 | high (classical dSph) |
| Sculptor | max-core-expansion | 5.43 cm²/g at v=9 | moderate |
| Draco | max-core-expansion | 4.44 cm²/g at v=10 | moderate |
| MW UFDs | varied (per Fischer & Yu 2026) | 2.85 cm²/g at v=15 | varied (pericentric-distance dependent) |

---

## Phase G5 — Validate Against UFD Diversity (Weeks 12-16)

**Status**: NOT STARTED.

**Deliverable**: Comparison of phase-aware predictions to observed UFD density diversity and dwarf rotation-curve scatter.

**Method**:
- Fischer & Yu (2026) provide simulation suite of MW UFDs; compare phase-aware density distribution.
- Also compare to "Gravothermal collapse and the diversity of galactic rotation curves" framework, σ/m ≈ 20-40 cm²/g in dwarf halos.

**Success criterion**: Phase-aware model should reproduce observed bimodality or broad scatter in dwarf central densities without requiring bimodal σ/m(v).

---

## Phase G6 — KiSS-SIDM Late-Stage Validation (Ongoing)

**Status**: NOT STARTED.

**Deliverable**: Use patched KiSS-SIDM (T215 patches: FP protection, assertion disable, min_particles increase) to validate fluid-model predictions in intermediate mean-free-path regime.

**Method**:
- Run KiSS-SIDM for representative halos (Fornax-like, Cloud-9-like, UFD-like) at σ/m values preferred by phase-aware fit.
- Compare late-time density profile to fluid-model prediction.
- If fluid overpredicts/underpredicts collapse depth, calibrate correction factor.

**Note**: The KiSS-SIDM patches developed in T215 (FP protection, assertion disable, min_particles increase) should be submitted upstream as a PR to KiSS-SIDM GitLab.

---

## Expected Impact on Project Verdict

If the phase-aware pipeline (G1-G6) is implemented, the paper's headline verdict should shift from:

> "4 of 5 constrained channels fit; Cloud-9 vs. dSph tension unresolved"

to:

> "The observed density diversity across dwarf galaxies is naturally explained by gravothermal evolution at a single, velocity-dependent σ/m(v), with Cloud-9 in core-expansion phase and classical dSphs in or near collapse. The remaining tension is between the required σ/m(v) and the Horigome+ upper limits, which must be addressed by a proper SASHIMI likelihood."

This is a stronger scientific claim than the current "constraint map" framing, because it converts an apparent failure into a positive prediction: **the model predicts that halos with quiescent merger histories and early formation should be dense (collapsed), while halos with active mergers or late formation should be diffuse (core-expanding). This is testable with the next generation of UFD observations.**

---

## Reference Papers

| Reference | arXiv |
|-----------|-------|
| Fischer & Yu (2026) A&A 711, A68 | 2603.xxxxx |
| Silverman et al. (2026) | 2606.02566 |
| Yang, Nadler, Yu & Zhong (2024) JCAP 02, 032 | 2305.16176 |
| Yang & Yu (2022) | 2204.04356 |
| Balberg, Shapiro, Inoue (2002) PRL 88, 101301 | (no arXiv) |
| Koda & Shapiro (2011) MNRAS 415, 1125 | (no arXiv) |
| Gurian & May (2025) | 2505.15903 |
| Ohana, Zhang & Yu (2026) | 2608.04362 |
| Nishikawa+ (2020) | (gravothermal + tidal) |
| Mateu (2023) | galstreams catalog |
| Nadler et al. (2025) | 2503.10748 (Concerto) |

---

## Implementation Status Summary

| Phase | Status | File |
|-------|--------|------|
| G1 (Calibrated gravothermal model) | SCAFFOLD | `v0.3-prelim/code/gravothermal_evolution.py` |
| G2 (Merger history) | SCAFFOLD | `v0.3-prelim/code/gravothermal_evolution.py` |
| G3 (Cloud-9 re-analysis) | NOT STARTED | — |
| G4 (Phase-diversity fit) | NOT STARTED | — |
| G5 (UFD diversity validation) | NOT STARTED | — |
| G6 (KiSS-SIDM validation) | NOT STARTED | — |

**Total estimated effort**: 12-16 weeks for full G1-G5 implementation; G6 is ongoing.
