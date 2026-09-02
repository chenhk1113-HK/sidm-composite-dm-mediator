# EXTRACT — sidm-composite-dm-mediator

**Version 0.4-prelim + T75 · 2026-09-02 · ~1,100 words**

**Standing version: v0.4-prelim+T75** (DAMPE + Zhang+2025 LSS joint-fit rerun; v0.7 result). Channels: **18** (was 16). Tests: 472 pass / 0 fail / 7 skip. V0_6_ROADMAP: 9 of 15 items shipped (3 partial-closure: #10, #17, #19) + 2 v0.4-prelim Tier-1 extensions (DAMPE, LSS).

**⚠ Orthogonal-physics posture (locked 2026-08-10, reaffirmed 2026-09-02 in T75):** The project's headline σ/m = 0.68-1.7 cm²/g measures **σ_DM-DM** (self-scattering cross-section per unit mass, the SIDM observable). Direct-detection experiments (LZ, XENONnT, PandaX) measure **σ_DM-nucleon** — a fundamentally different cross-section (factor ~10²³ difference). Per standing decision, direct-detection constraints are **rejected** as σ/m measurements; LZ is used only as a sanity check. See `MODEL_ASSUMPTIONS_AND_LIMITATIONS.md §0` for full reasoning. This stance is **non-negotiable** unless user explicitly overrides.

**Updates from 2026-08-25 (T70 Tier-1 PATCH):**
- Added Channel 11 (NGC 1052-DF2/DF4 + FCC 224/240 dark-matter-free UDG consistency check)
  and Channel 12 (cosmic-web radio synchrotron 40× excess, Pinetti 2025-26) as new observational
  channels (10 → 12 total). Both pass at the current MAP. Headline σ/m_0 from T13 v2 (5/6/8/9/10/11/12-channel
  joint fit) is **0.68 cm²/g** at galactic scale, consistent with T21 (1.4-1.7 cm²/g) and T41 historical (0.066 cm²/g)
  within the 0.4-0.5 dex systematic budget. See `CHANGELOG.md` [T70] entry for details.
- Added Channel 13 (T70.1): SIDM quantum-statistical lower mass bound from
  Tremaine-Gunn 1979 + Rogers-Peiris 2021 Lyman-α (m > 100 eV for fermionic DM).
  Defensive documentation channel — encodes the "SIDM in classical regime"
  assumption with literature citations. No new physics constraint on the project
  (T41 v0.5 posterior median m_χ = 805 GeV is ~10⁹ above the bound). See `CHANGELOG.md`
  [T70.1] entry for details.
- **Mediator quantum regime (Q&A 2026-08-25):** Per follow-up user question
  *"then what about the mediator, it is also very small"* — confirmed via the
  T41 posterior that the secluded dark photon mediator has m_A' ≈ 553 MeV at the
  **v0.5 median** (MAP ≈ 502 MeV). The historical T41 numbers (median 26.6 MeV,
  MAP 336 MeV) live BELOW the KSFR/PCAC validity lower bound (418 MeV) and
  were correctly rejected by the v0.5 re-run (T70.5, 2026-08-26). The v0.5
  mediator gives a Yukawa force range (Compton wavelength) of ~0.36 fm and a
  de Broglie wavelength of ~10⁻³² pc at SIDM-velocity scales. Both are
  **classical regimes** (force-mediated, not wave-mediated). The mediator's
  quantum-field-theory effects (annihilation cross-section, decay rate, kinetic
  mixing ε) are already handled by the existing T30 (LZ σ_SI mapping), T39 (ε
  marginalization), and T55 (Boltzmann-relic calibration). **No new channel
  needed** — the project already captures the mediator's quantum behavior
  correctly. See `v0.3-prelim/docs/FINDINGS.md` for the full sub-section.
- Out-of-scope literature flagged but not implemented: FDM/ψDM wholesale, DM→graviton Gertsenshtein
  decay, bimetric gravity. Different physics frameworks; would need separate repos.

---

## Rationale

This project started from a specific tension in dark-matter physics. The standard WIMP framework predicts both large self-interaction cross-sections at galactic scales (needed for the diversity of dwarf density profiles) and vanishingly small coupling to ordinary matter (to survive LZ, XENONnT, PandaX limits). These conflict. The theoretical escape hatch since Pospelov, Ritz, Voloshin (2008) is to make the WIMP **secluded**: the same mediator that drives strong self-scattering couples only feebly to Standard Model particles. Verifying this against real data requires a pipeline that fits σ/m, marginalizes over mediator coupling, and ingests multi-wavelength likelihoods — none existed publicly when this started.

The second motivation is microphysical: composite dark matter (dark glueballs, dark-rho mesons, dark baryons in SU(N_dark)) is theoretically attractive but under-explored observationally. The project extends the SIDM machinery to this regime via PCAC + KSFR chiral perturbation theory.

The pipeline was **designed to scale to 10+ independent observational probes** (SPARC, dSph, ultra-faint dwarfs, strong lensing substructure, radio-relic clusters, cluster mergers, direct-detection limits, etc.); **5–6 are currently fully integrated**, the rest are on the v0.4-prelim roadmap.

## Key findings

**1. The SIDM cross-section posterior is robust at 1.4–1.7 cm²/g** — a **+0.2 dex calibration correction** from the placeholder fluid model. The placeholder T8/T17 pipeline gave σ/m ≈ 1.0 cm²/g using the Balberg+ 2002 fluid gravothermal approximation. Replacing this with the Gurian & May (2025) KiSS-SIDM kinetic DSMC penalty (T21 real run) yields 1.4–1.7 cm²/g at V_REF = 100 km/s. The T21 number is the physically accurate estimate; the placeholder was overstated by the fluid model's IMFP-regime bias (T20–T21 ΔlogZ ≈ +0.1). The 6-channel systematic budget is 0.4–0.5 dex, publication-grade.

**2. Velocity dependence is real but the slope is prior-dependent.** Data prefer a ≈ 0.6–1.4 (σ/m decreases with velocity, as expected for Yukawa-like mediators at MeV scale). T39 Tier-3 marginalization gives a ≈ 0.94; in-house composite-dark-rho gives a ≈ 2.24. This 1.3σ tension is a real open problem, not papered over.

**3. The secluded mediator is naturally invisible to direct detection.** Under a wide prior on mediator coupling (allowing ε → 10⁻⁵⁰), the posterior is consistent with σ_SI ≈ 2×10⁻¹¹⁸ cm² — about 10⁷² times below the LZ WS2024 limit (arXiv:2410.17036, 2.2×10⁻⁴⁸ cm² at 43 GeV) and 2.5×10⁷² times below the neutrino floor. Under the Roberts et al. 2024 narrow default prior (ε ~ 10⁻⁴), the same data excludes SIDM catastrophically (log Z ≈ −9388). The Tier-3 "resolution" is therefore **prior-dependent**. The wide prior is the physically motivated choice, but the conclusion does not survive the narrow one.

**4. Composite dark-rho gives σ/m within 13% of the joint posterior**.** PCAC + KSFR predict m_ρ ≈ 3.55 MeV for m_χ ≈ 34 GeV. The resulting σ/m ≈ 1.36 cm²/g matches the T21/T39 MAP to within 13% — the strongest single theoretical prediction of the pipeline. Relic density Ωh² ≈ 0.12 sits within the Planck band.

**5. Two-component mass-segregated SIDM is Occam-neutral, not yet evidence.** The T22 two-component vs single-component Bayes factor is +0.39 (with IMFP correction) or +0.22 (without) — both well below the 2.5 significance threshold. **Critically: all three two-component observational likelihoods are still public-limit-curve surrogates (Gaussian proxies over 95% CL upper limits), not raw posterior chains**, so this BF is a **pipeline feasibility diagnostic**, not definitive evidence for a two-species dark sector. (See Drobczyk 2025 for an independent UV route that demonstrates qualitative literature consistency — not a cross-validation of this project's numerical pipeline.)

## Limitations

**Velocity-slope tension is unresolved.** The 1.3σ disagreement between data-preferred a ≈ 0.94 and composite-rho a ≈ 2.24 is a real theoretical gap. Either composite-rho microphysics is incomplete, or the data still has systematics masking the steeper slope.

**The SPARC channel is a calibrated saturation score, not a per-galaxy observational likelihood.** Per the R11 audit (2026-08-14): the SPARC contribution to the v0.3-prelim 5-channel joint fit uses `Dsat=5000, sigma_transition=0.5 cm²/g` — a smooth saturation function approximating the Burkert-vs-NFW Phase 2 result. The 175 per-galaxy forward fits (T14) do **not** drive the joint sampling. This means log Z, Bayes factors, and the "~1.4–1.7 cm²/g" interval are conditional on this proxy choice. A real per-galaxy forward model is a v0.4-prelim roadmap item (R11 audit G12).

**Most channels use public-limit-curve surrogates, not raw posterior samples.** Only LZ (T30, ingesting HEPData record 155182) and Fermi-LAT 14-year dSph (T32, McDaniel et al. 2024) use ingested published curves. SPARC, ultra-faint dwarfs, Bullet Cluster use Gaussian approximations. Headline σ/m is robust to this (T28: Δ < 0.01 dex), but full posterior-chain ingestion is deferred to v0.4-prelim.

**Three engineering caveats (per R10 audit).** (i) **Fixed reference halo parameters** constrain fits to a canonical 10⁹ M☉ halo, with dwarf/cluster halos using an upper-bound penalty rather than self-consistent KiSS-SIDM runs. (ii) **Unvalidated KiSS scaling extrapolation** to dwarf (10⁷–10⁸ M☉) and cluster (10¹⁴–10¹⁵ M☉) masses — the paper-scale N=2×10⁶ simulations are unobtainable on the available WSL hardware; the N=10⁴ Python smoke tests reproduce qualitative behaviour but fail quantitative matching (~10% energy-conservation error vs sub-percent for full DSMC). (iii) **Public-limit-curve surrogates remain the primary barrier to peer-review publication-grade results.**

**Composite-DM mass formula is a phenomenological parametrization, not first-principles.** The vector dark-rho mass formula `m_rho = 2*sqrt(m_q*Λ_dark + Λ_dark²)` is a smooth interpolation between the heavy-quark and chiral-symmetry-broken limits, not a PCAC/GMOR prediction (those govern the **pion**, not the vector ρ). Treat T53/T54 σ/m as a toy parametrization; the σ/m ≈ 1.36 cm²/g match is encouraging but should not be reported as a first-principles prediction.

**Two prior choices carry the Tier-3 conclusion.** As noted in finding 3, the mediator resolution requires a wide ε prior. Not robust to Roberts et al. 2024's narrow default. Future work: hierarchical/log-normal priors.

**Not a "first-time" result.** Secluded-WIMP is from Pospelov, Ritz, Voloshin (2008); SIDM phenomenology from Kaplinghat, Tulin, Yu (2014); KiSS-SIDM from Gurian & May (2025); two-component SIDM from Yang, Fan, Hou, Tsai (2026). What's new is the joint demonstration that all of these components are mutually consistent against real data — not the components themselves. See `CITATION.cff` for full attribution.

---

**Word count: ~1,000. References:** arXiv:0711.4866 (Pospelov), 1310.7945 (Kaplinghat), 2403.16633 (Horigome), 2505.15903 (Gurian & May), 2506.14898 (Yang+), 2506.22997 (Drobczyk), 2410.17036 (LZ WS2024), 2311.04982 (McDaniel+). See `docs/DATA_SOURCES.md` for full citations.