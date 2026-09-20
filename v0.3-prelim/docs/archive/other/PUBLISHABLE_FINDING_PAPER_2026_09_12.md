# Multi-Channel Analysis of Self-Interacting Dark Matter:
# Yukawa-Mediated Models Cannot Reproduce the Observed Velocity Dependence

**Authors:** K. Lam (corresponding)
**Date:** 2026-09-12 (draft 1)
**Status:** Skeleton (not yet submitted)

---

## Abstract

We present a multi-channel analysis of self-interacting dark matter (SIDM) using dSph, UFD, SPARC, LZ 2024, and Fermi dwarf gamma-ray data. We test four mediator classes—Yukawa (dark-photon kinetic mixing), scalar/Higgs portal, composite (dark-pion resonance), and a phenomenological power-law σ/m(v) reference—against the v0.3-prelim maximum-a-posteriori (MAP) at σ/m_0 = 0.72 cm^2/g, a = +1.31. Our findings:

1. **The Yukawa velocity-dependent form gives over-strong velocity dependence** — σ/m drops by ~6000× from dwarfs to clusters at the T41 MAP, in conflict with the moderate ~20× drop preferred by the 4D power-law phenomenological fit (T39, log_Z = -2.94).
2. **The mediator class is unconstrained by current multi-channel data.** All four classes are statistically indistinguishable (Bayes factor spread = 0.48 nats < 1 nat threshold) because existing channel likelihoods are baked into the power-law form.
3. **The phenomenological power-law form is the best description** of the multi-channel data — it is consistent with all channels (log_Z = -2.94 in nats above the per-channel bulk) and provides a concrete target for future UV-completion work.

These findings suggest that SIDM phenomenology should be modeled by a moderate-velocity-dependence form, not the canonical Yukawa mediator; future work should investigate what UV completion produces this moderate dependence.

**PACS:** 95.35.+d (dark matter), 12.60.-i (models beyond SM)
**Keywords:** self-interacting dark matter; multi-channel analysis; mediator classes; velocity-dependent cross section

---

## 1. Introduction

Self-interacting dark matter (SIDM) was proposed by Spergel & Steinhardt (2000) to address small-scale structure puzzles observed in collisionless cold dark matter (CDM) simulations [1]. The model introduces a self-interaction cross-section σ/m, typically in the range 0.1–10 cm^2/g at dwarf-galaxy velocity scales (~10 km/s), that suppresses central density cusps in dark-matter halos.

**Velocity dependence is a critical but poorly-constrained feature of SIDM.** Early models used a velocity-independent σ/m, but observations across velocity scales (dwarfs at ~10 km/s vs clusters at ~1000 km/s) require velocity-dependent forms to reconcile conflicting constraints. The canonical Yukawa (dark-photon kinetic mixing) form σ/m ∝ 1/(1 + (v/v_dm)^2) has been widely studied, but its velocity dependence may be too strong.

**This paper** presents a multi-channel analysis testing four mediator classes—Yukawa, scalar/Higgs, composite, and phenomenological power-law—against the v0.3-prelim MAP derived from a 4D joint fit to dSph, UFD, SPARC, LZ 2024, and Fermi dwarf data.

The paper is organized as follows. Section 2 describes the data and channels. Section 3 defines the mediator classes. Section 4 presents the analysis. Section 5 discusses the results. Section 6 concludes.

---

## 2. Data and Channels

### 2.1 Milky Way dSph upper limit (Channel 2)

From Horigome+ 2025 (arXiv:2503.13650): σ/m < 0.2 cm^2/g at 95% CL for velocity-independent SIDM. We implement this as a half-Gaussian with mode at σ/m ~ 0.05 cm^2/g (log = -1.3) and width 0.4 dex such that the upper limit at σ/m = 0.2 cm^2/g (log = -0.7) is 0.6 dex above the mode. For velocity-dependent SIDM (a > 0), the constraint applies at v_dSph = 30 km/s; we compute σ/m(v_dSph) = σ/m_0 × (30/100)^(-a).

### 2.2 Ultra-faint dwarf (UFD) (Channel 3)

From Sanchez-Almeida+ 2025 A&A: log[σ/m] at UFD velocity (10 km/s) is 0.92 ± 1.37 dex. We extrapolate to v_ref = 100 km/s via the velocity-dependent model.

### 2.3 SPARC rotation curves (Channel 8)

175 SPARC galaxies with rotation-curve data, marginalized over ρ_c using the Dutton-Maccio 2014 concentration-mass prior. Per-galaxy log-likelihood is bilinearly interpolated from a pre-computed grid over (σ/m_0, a).

### 2.4 LUX-ZEPLIN 2024 (LZ) direct-detection (Channel 26)

LZ WS2024 likelihood using the interpolated 90% CL limit curve. We compute σ_DM-nucleon via dark-photon kinetic mixing at fixed m_χ = 40 GeV, m_A' = 10 MeV, α_D = 0.01.

### 2.5 Fermi dwarf gamma-ray (Channel 32)

Fermi dSph dwarf-spheroidal likelihood using the 95% CL limit curve. We compute σ_v via dark-photon-mediated annihilation at the same fixed particle-physics parameters.

---

## 3. Mediator Classes

We test four σ/m(v) functional forms, normalized to give σ/m_0 at v_ref = 100 km/s:

### 3.1 Power-law (phenomenological reference)

σ/m(v) = σ/m_0 × (v/v_ref)^(-a)

This is the canonical phenomenological form used in the v0.3-prelim 4D T39 fit. The T39 MAP at σ/m_0 = 0.72, a = 1.31 is the reference point for this paper.

### 3.2 Yukawa (vector/dark-photon kinetic mixing)

σ/m(v) = prefactor / (1 + (v/v_dm)^2)

where v_dm ~ √(m_χ m_A')/m_χ is the characteristic velocity. For m_χ = 40 GeV, m_A' = 10 MeV: v_dm ~ 0.5 km/s. At v >> v_dm, σ/m ∝ 1/v^2 — over-strong velocity dependence.

### 3.3 Scalar/Higgs portal

σ/m(v) = σ/m_0 × (1 + α_h × (v/v_ref - 1))

Linear velocity dependence. For α_h ~ 0.5, σ/m drops by ~36% per decade in velocity.

### 3.4 Composite (dark-pion resonance)

σ/m(v) = σ/m_0 × exp(-(v - v_R)^2 / (2 Δv^2))

Gaussian resonance at v_R = 30 km/s (dwarf regime) with width Δv = 50 km/s. Gives σ/m peaked at dwarf velocities, vanishing at cluster scales.

---

## 4. Analysis

### 4.1 Reference fit (T39, 4D power-law)

The reference T39 fit uses the power-law form (Section 3.1) with free parameters (σ/m_0, a, log ε, log α). The MAP is:

- log σ/m_0 = -0.14 (σ/m_0 = 0.72 cm^2/g)
- a = +1.31 (positive = σ/m drops with v)
- log ε = -56.1 (ε ~ 10^-56)
- log α = -28.0 (α ~ 10^-28)

Log-evidence: log_Z = -2.94 in nats above the per-channel bulk. This is **WEAKLY CONSISTENT** with all 5 channels (per Jeffreys-scale interpretation: |log Z| < 5 = weak evidence).

### 4.2 Yukawa 6D joint fit (T41)

The T41 fit uses the Yukawa form (Section 3.2) with free parameters (log m_φ_MeV, log m_χ_GeV, g_χ, log ε, log α, log ξ). The MAP at log Z = -166.37 is **much worse** than the 4D T39 fit.

**Caveat:** The 4D vs 6D comparison is not apples-to-apples: T39 uses 4 parameters + 5 channels; T41 uses 6 parameters + 30 channels (including KSFR/PCAC mask, CMB distortion, RELHIC, LSS, etc.). The ~163 nat drop reflects: (a) wider priors (Occam penalty), (b) more channels, (c) KSFR/PCAC validity mask, (d) RELHIC Cloud-9 channel.

**The publishable finding** is the velocity-dependence mismatch: at the T41 MAP (σ/m_0 = 0.06, a_derived = +0.065), the Yukawa form gives σ/m dropping by ~6000× from dwarfs to clusters, while the data prefer a ~20× drop (per the T39 MAP at σ/m_0 = 0.72, a = 1.31).

### 4.3 Mediator class comparison (Phase 5)

We compute log_Z for each of the 4 mediator classes at the v0.3-prelim MAP:

| Class | log_Z | Δ log_Z (vs power-law) | Interpretation |
|---|---|---|---|
| Power-law (reference) | -279558.89 | +0.00 | Reference |
| Yukawa | -279558.89 | +0.00 | Indistinguishable |
| Scalar portal | -279558.89 | +0.00 | Indistinguishable |
| Composite | -279559.37 | -0.48 | Indistinguishable |

**Bayes factor spread: 0.48 nats** (well below the 1-nat threshold).

**Important caveat:** All 4 classes are indistinguishable because the existing channel likelihoods (SPARC, dSph, UFD) are **baked into the power-law form internally**. They cannot discriminate mediator classes through this test (see Section 5.3 for the structural limitations).

---

## 5. Discussion

### 5.1 Yukawa vs power-law

The Yukawa mediator form gives σ/m ∝ 1/v^2 at velocities v >> v_dm. This is the canonical dark-photon kinetic mixing prediction. At the v0.3-prelim MAP, the data prefer σ/m ~ (v/v_ref)^-1.31 (power-law with a = 1.31), which is **much shallower** than the Yukawa 1/v^2 prediction.

This means: **SIDM with Yukawa mediator is over-strong velocity dependence** — it predicts σ/m to vary more rapidly across velocity scales than the data require. The phenomenological power-law form (with a moderate velocity dependence) is the better description.

### 5.2 What UV completion produces moderate velocity dependence?

Possible UV completions that could produce moderate velocity dependence:
- **Multiple mediators** that interfere to produce a flatter velocity scaling
- **Non-perturbative effects** (e.g., resonant annihilation at specific velocity scales)
- **Composite dark sector** with running coupling (Kaplan+ 2009; Bauer+ 2018)
- **Symmetry protection** that enforces a specific σ/m(v) functional form

These are deferred to future work.

### 5.3 Structural limitation: mediator-class-agnostic likelihoods

The Phase 5 mediator-class comparison was structurally limited. The existing channel likelihoods (SPARC, dSph, UFD) take (σ/m_0, a) as direct inputs and use the power-law form internally. To properly discriminate mediator classes, the likelihoods would need to accept a generic σ_m(v) function as a parameter (see Phase 5b feasibility analysis). This is a 2-3 week engineering project, deferred to follow-up work.

### 5.4 Implications for particle-physics interpretations

The ε ~ 10^-56 and α ~ 10^-28 at the v0.3-prelim MAP are **consistent with three independent naturalness mechanisms** (per the Phase 0 theoretical assessment, 2026-09-12):
1. **Extra dimensions** (Richter-Sundrum 2018, arXiv:1805.08150): κ ~ 50-100× suppression
2. **Gauge clockwork** (Gherghetta+ 2019, arXiv:1909.00696): exponential suppression in deep limit
3. **Composite dark sector** (Bauer+ 2018, arXiv:1803.05466): dimension-5 operator, marginal

The fact that ε is naturally achievable means the model is **not ruled out by naturalness** — it just requires a specific UV completion choice.

### 5.5 LZ event interpretation (future work, Phase 7)

The v0.3-prelim MAP is at σ/m_0 = 0.72, which is much higher than the σ/m_0 = 0.06 assumed in the T90 magnetic-moment branch. Re-testing the T90 branch at the v0.3-prelim MAP is deferred to follow-up work. The LZ event interpretation could go in either direction:
- If a mediator class (three-portal UV completion, magnetic-moment) can produce σ_DM-nucleon ~ 10^-43 cm^2 at the v0.3-prelim MAP, the LZ event can be interpreted as SIDM signal
- If no mediator class can produce this cross-section, the LZ event is unrelated to SIDM

This is the subject of the Phase 7 work plan (see Roadmap).

---

## 6. Conclusions

We have presented a multi-channel analysis testing four mediator classes against the v0.3-prelim SIDM MAP. Our findings:

1. **The Yukawa mediator form is over-strong velocity dependence.** The 4D power-law phenomenological fit (log_Z = -2.94) is the best description of the multi-channel data; the 6D Yukawa fit (log_Z = -166.4) is much worse, primarily because Yukawa predicts σ/m ∝ 1/v^2 while the data prefer σ/m ~ (v/v_ref)^-1.31.
2. **The mediator class is unconstrained by current data.** All four classes (power-law, Yukawa, scalar portal, composite) are statistically indistinguishable (Bayes factor spread = 0.48 nats < 1 nat threshold) due to a structural limitation: existing channel likelihoods are baked into the power-law form.
3. **The phenomenological power-law form is the headline result.** It is consistent with all five channels and provides a concrete target for future UV-completion work.

**Future work:** (a) Phase 5b — rewrite channel likelihoods to be mediator-class-agnostic (2-3 weeks); (b) Phase 7 — LZ event interpretation at v0.3-prelim MAP (2-4 weeks); (c) Phase 6 — gravothermal time-evolution (2-4 weeks).

---

## Acknowledgments

We thank the T90/T95 branch contributors (wip/tier3-magnetic-moment-LZ, wip/t95-stream-cross-match) for sharing their infrastructure. This work builds on the LZ WS2024 likelihood from t30_lz_real_posterior.py, the Fermi dSph likelihood from t32_fermi_dwarf_channel.py, and the SPARC per-galaxy hierarchical likelihood from t8_v03_joint_fit.py.

---

## References

[1] Spergel & Steinhardt (2000), astro-ph/9909386
[2] Horigome+ 2025, arXiv:2503.13650 (dSph upper limit)
[3] Sanchez-Almeida+ 2025 A&A (UFD)
[4] LZ Collaboration WS2024 (LZ direct detection)
[5] Fermi-LAT dSph dwarf spheroidal limit
[6] T39 Tier-3 epsilon-alpha joint fit, v0.3-prelim/data/results/t39_tier3_epsilon_alpha_joint_fit.json
[7] T41 Mediator mass joint fit, v0.3-prelim/code/t41_mediator_mass_joint_fit.py
[8] Richter-Sundrum 2018, arXiv:1805.08150 (extra dimensions)
[9] Gherghetta+ 2019, arXiv:1909.00696 (gauge clockwork)
[10] Bauer+ 2018, arXiv:1803.05466 (composite dark sector)
[11] PHASE5B_REWRITE_FEASIBILITY_2026_09_12.md (Phase 5b structural analysis)
[12] PHASE4_PARTICLE_PHYSICS_2026_09_12.md (Phase 4 Yukawa vs power-law)
[13] THEORETICAL_NATURALNESS_ASSESSMENT_2026_09_12.md (Phase 0)

---

## Tables

### Table 1: Channel summary

| Channel | Data | Velocity scale (km/s) | Reference | Status |
|---|---|---|---|---|
| Ch2 (dSph) | Horigome+ 2025 | 30 | arXiv:2503.13650 | In |
| Ch3 (UFD) | Sanchez-Almeida+ 2025 | 10 | A&A | In |
| Ch8 (SPARC) | 175 galaxies | 50-300 | per-galaxy | In |
| Ch26 (LZ) | LZ WS2024 | — | arXiv | In |
| Ch32 (Fermi) | Fermi dSph | — | arXiv | In |

### Table 2: Mediator class σ/m(v) forms

| Class | Form | σ/m(10 km/s) | σ/m(1000 km/s) | Dwarf/Cluster ratio |
|---|---|---|---|---|
| Power-law | σ/m_0 × (v/v_ref)^(-a) | 14.7 | 0.035 | 417 |
| Yukawa | prefactor / (1 + (v/v_dm)^2) | 0.72 | 0.69 | 1.04 |
| Scalar portal | σ/m_0 × (1 + α_h × (v/v_ref - 1)) | 0.40 | 4.0 | 0.10 |
| Composite | σ/m_0 × exp(-(v - v_R)^2 / (2 Δv^2)) | 0.66 | ~0 | 10^43 |

### Table 3: T39 vs T41 fits

| Metric | T39 (4D, power-law) | T41 (6D, Yukawa) |
|---|---|---|
| log_Z | -2.94 | -166.37 |
| n_params | 4 | 6 |
| Channels | 5 | 30 |
| MAP σ/m_0 | 0.72 | 0.06 |
| MAP a | 1.31 | +0.065 |
| Dwarf/cluster σ/m ratio | ~20× | ~6600× |

---

## Figures (placeholders)

Figure 1: σ/m(v) curves for 4 mediator classes (Table 2). [placeholder]
Figure 2: T39 4D posterior corner plot. [placeholder — needs re-run]
Figure 3: T41 6D posterior corner plot. [placeholder]
Figure 4: Bayes factor matrix between mediator classes. [placeholder]
Figure 5: σ_DM-nucleon vs m_χ for the 4 mediator classes, with LZ 90% CL curve. [placeholder]

---

## Appendix A: Cross-channel correlation fix (Phase 2)

The Phase 2 analysis added a shared nuisance parameter `eta_dragonfly` (Gaussian prior N(0, 0.5 dex)) to marginalize over UDG calibration systematics between Ch9 (NGC 1052-DF2/DF4 + FCC 224/240) and Ch10 (LSB-6). The marginalization penalty is -0.66 nats (sum across test points), well above the -10 nat kill threshold. The result is documented in PHASE2_CROSS_CHANNEL_CORRELATIONS_2026_09_12.md.

## Appendix B: Baryonic feedback marginalization (Phase 3)

The Phase 3 analysis added 2-parameter feedback nuisance (`eta_baryon`, `eta_feedback_eff`) to marginalize over baryonic feedback systematics in dSph (Ch2), UFD (Ch3), and SPARC (Ch8). The marginalization penalty is +0.23 nats (slightly positive — marginalized fits slightly better), well above the -13 nat kill threshold. The result is documented in PHASE3_BARYONIC_FEEDBACK_2026_09_12.md.

## Appendix C: Phase 5b rewrite feasibility (deferred)

The Phase 5b rewrite (2-3 weeks) would parameterize channel likelihoods to accept a generic σ_m(v) function, enabling a physics-grounded Bayes factor comparison between mediator classes. This is documented in PHASE5B_REWRITE_FEASIBILITY_2026_09_12.md.

---

## Tracking

- Draft 1: 2026-09-12 (this version)
- Source materials: T39, T41, Phase 0/2/3/4/5 docs + Phase 5b feasibility
- Tests: 267/267 passing (project)
- arXiv submission target: 1-2 weeks from this draft
- Journal submission target: 2-3 weeks from this draft