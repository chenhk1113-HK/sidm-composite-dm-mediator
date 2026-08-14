# EXTRACT — sidm-composite-dm-mediator

**Version 0.3-prelim-D15-CORRECTED3 + Mediator_Detection_v12 · 2026-08-14 · 1,000 words**

---

## Rationale

This project started from a specific tension in dark-matter physics. The standard weakly-interacting massive particle (WIMP) framework predicts both large self-interaction cross-sections at galactic scales (needed to explain the diversity of dwarf-galaxy density profiles and the too-big-to-fail problem) AND vanishingly small coupling to ordinary matter (to survive direct-detection limits from LZ, XENONnT, and PandaX). These two requirements are in direct conflict — every conventional WIMP fails one or the other.

The theoretical escape hatch is well-known since Pospelov, Ritz, Voloshin (2008): make the WIMP **secluded**, meaning the same mediator that drives strong self-interaction couples only feebly to Standard Model particles. Self-interactions stay large; direct-detection couplings go to zero. But verifying this idea against real data requires a pipeline that simultaneously fits SIDM cross-sections, marginalizes over the mediator coupling, and ingests multi-wavelength observational likelihoods. No public pipeline did this when the project started. Building one was the motivation.

The second motivation is microphysical: composite dark matter (dark glueballs, dark rho mesons, dark baryons in a hidden SU(N_dark)) is a theoretically attractive candidate that has been under-explored observationally. The project extends the SIDM constraint machinery to this regime, computing σ/m, relic density, and direct-detection cross-sections from first-principles PCAC + KSFR chiral perturbation theory, and asking whether the same composite sector that gives the right relic density also gives the right self-interaction strength.

## Key findings

**1. The SIDM cross-section posterior is robust at 1.4–1.7 cm²/g.** A five-channel joint fit (SPARC rotation curves, dwarf spheroidal kinematics, ultra-faint dwarfs, Bullet Cluster, LZ direct-detection limits) using the Gurian & May (2025) KiSS-SIDM kinetic gravothermal-collapse penalty as the physical anchor places σ/m at galactic velocity scales (V_REF = 100 km/s) at 1.4–1.7 cm²/g at MAP. T21 single-halo and T39 global fits agree within 1σ. The 6-channel systematic-uncertainty budget is 0.4–0.5 dex, which is publication-grade.

**2. Velocity dependence is real but the slope is prior-dependent.** The data prefer a velocity index a ≈ 0.6–1.4 (σ/m decreases with velocity, as expected for Yukawa-like mediators at MeV scale). The T39 Tier-3 marginalization gives a ≈ 0.94; the in-house composite-dark-rho model gives a ≈ 2.24. This 1.3σ tension is documented as a real open problem, not papered over.

**3. The secluded mediator is naturally invisible to direct detection.** Under a wide prior on the mediator coupling (allowing ε → 10⁻⁵⁰), the joint posterior is consistent with σ_SI ≈ 2×10⁻¹¹⁸ cm² — about 10⁷² times below the LZ WS2024 limit (arXiv:2410.17036, 2.2×10⁻⁴⁸ cm² at 43 GeV) and 2.5×10⁷² times below the neutrino floor. Under the Roberts et al. 2024 narrow default prior (ε ~ 10⁻⁴), the same data excludes SIDM catastrophically (log Z ≈ −9388). The Tier-3 "resolution" is therefore **prior-dependent**, as documented in T39. The wide prior is the physically motivated choice — it allows the SM-decoupled regime the framework predicts — but the reader should know the conclusion does not survive the narrow prior.

**4. Composite dark-rho gives σ/m within 13% of the joint posterior.** Using PCAC + KSFR, the dark-rho mass is m_ρ ≈ 3.55 MeV for DM mass m_χ ≈ 34 GeV. The resulting σ/m ≈ 1.36 cm²/g is within 13% of the T21/T39 MAP, the strongest single theoretical prediction of the entire pipeline. The composite-DM extension also predicts a relic density Ωh² ≈ 0.12, within the Planck band.

**5. Independent cross-validation passes.** Drobczyk 2025 (arXiv:2506.22997, CQG 42 225006) constructs a different UV model — PNGB plus heavy resonance rather than composite dark-rho — yet predicts the same low-energy phenomenology: σ/m ~ 1 cm²/g with the mediator invisible to direct detection. This is the strongest external validation available.

## Limitations

**Velocity-slope tension is unresolved.** The 1.3σ disagreement between data-preferred a ≈ 0.94 and composite-rho prediction a ≈ 2.24 is a real theoretical gap. Either the composite-rho microphysics is incomplete, or the data still has systematics that mask the steeper slope. Either way, this is **future work**, not a solved problem.

**Most channels use Gaussian likelihood proxies, not raw posterior samples.** Only LZ (T30) and Fermi-LAT 14-year dSph stacking (T32, McDaniel et al. 2024) use ingested published curves. SPARC, ultra-faint dwarfs, and Bullet Cluster still use Gaussian approximations. The headline σ/m is robust to this (T28 showed Δ < 0.01 dex), but the **full posterior-chain ingestion** is deferred to v0.4-prelim. Per-channel error bands are 0.1–0.3 dex for the proxy channels.

**KiSS-SIDM dwarf-mass simulations are incomplete.** Dwarf-mass (10⁷–10⁸ M_sun) KiSS-SIDM at N=10⁴ fails (T31, T38b); the canonical 10⁹ M_sun halo penalty is used as an upper bound on dwarf-mass collapse. The full N=2×10⁶ paper-scale run is launched in D14 as a background process for future sessions to pick up. **All dwarf-related results are qualitative supporting evidence**, not quantitative high-N simulation, and the manuscript should label them as such.

**Composite-DM UV completion has a known break.** Chiral perturbation theory diverges at low Λ_dark ≈ 0.15 MeV (T60 finding). The composite-rho mass formula is reliable in the regime Λ_dark ≫ m_ρ but breaks down at the boundary. The 13% σ/m agreement is therefore the strongest claim that survives within the validity region; outside it, the PCAC prediction is an extrapolation.

**Two prior choices carry the conclusion.** As noted in finding 3, the Tier-3 mediator resolution requires a wide ε prior. The result is not robust to Roberts et al. 2024's narrow default. Future work: hierarchical/log-normal priors for (ε, α) covering the SM-decoupled regime without collapsing to a hard boundary.

**Not a "first-time" result.** The secluded-WIMP framework is from Pospelov, Ritz, Voloshin (2008); the SIDM phenomenology is from Kaplinghat, Tulin, Yu (2014); KiSS-SIDM is from Gurian & May (2025); two-component SIDM is from Yang, Fan, Hou, Tsai (2026). What is new here is the joint demonstration that all of these components are mutually consistent against real data, not the components themselves. See `CITATION.cff` for the full attribution.

---

**Word count: ~1,000. References:** arXiv:0711.4866 (Pospelov), 1310.7945 (Kaplinghat), 2403.16633 (Horigome), 2505.15903 (Gurian & May), 2506.14898 (Yang+), 2506.22997 (Drobczyk), 2410.17036 (LZ WS2024), 2311.04982 (McDaniel+). See `docs/DATA_SOURCES.md` for full citations and data locations.