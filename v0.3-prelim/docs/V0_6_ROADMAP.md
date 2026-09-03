# v0.6 Roadmap — Deferred Items from R14

> **Status (2026-08-26):** Two R14 reviewer recommendations deferred to v0.6+ remain on this roadmap. Both are **multi-day/multi-week scope** and cannot ship in a single round. This document is the handoff for whoever picks them up.

**Repo:** `sidm-composite-dm-mediator` @ GitHub, `master` @ T70.9 (post-R14)
**Scope source:** R14 reviewer recommendations [R14 #9, R14 #10]
**Standing-version when written:** v0.3-prelim+T70.9

---

## Items on this roadmap

1. **Item 1 — External Boltzmann solver (micrOMEGAs)** (R14 Rec #1, Tier-2, ~2-4 weeks)
2. **Item 2 — Hierarchical per-galaxy SPARC likelihood** (R14 Rec #2, Tier-2, ~2-4 weeks)
3. **Item 3 — Composite-DM direct-detection forward prediction (T87)** (T86.7k+C, Tier-2, ~5-6 hours; registered 2026-09-03 after `consider4.docx` review)

| # | Item | R14 rec | Scope estimate | Status |
|---|---|---|---|---|
| 1 | **micrOMEGAs interface** for coupled Boltzmann solver | R14 Rec #9 | Multi-month | Deferred |
| 2 | **Hierarchical per-galaxy SPARC likelihood** | R14 Rec #10 | Multi-week | Deferred |
| 3 | **Inelastic scattering in primary production run** | R15 P075 | ~30 min wall | ✅ Shipped T71.1 |
| 4 | **T41 at nlive=2000** for publication-grade BFs | R15 P074 | ~50-100 min wall | ✅ Shipped T71.1 |
| 5 | **CMB spectral-distortion Channel 16** | R14 Rec #3 | (already shipped in T70.8) | ✅ Shipped |
| 6 | **runtime-guard against legacy v0.1/v0.2 imports** | R13 M1 | (already shipped in T70.4) | ✅ Shipped |
| 7 | **KSFR mask version logging** (`ksfr_mask_max_at_runtime` field) | R16 #5 | ~1 day | ✅ Shipped T71.2 |
| 8 | **config_hash field** for cross-version audit | R16 #11 | ~1 day | ✅ Shipped T71.2 |
| 9 | **Hierarchical per-galaxy SPARC likelihood** | R14 Rec #10, R16 #1 | Multi-week | ✅ Shipped T71.4 (hierarchical selected via T41_SPARC_HIERARCHICAL=1; log Z shift +0.10 vs calibrated) |
| 10 | **Proper Boltzmann relic-density calculation** | R14 Rec #9, R16 #4 | Multi-month | ⚠️ Partial T71.6 (t59_production_boltzmann.py: real scipy.integrate.solve_ivp Radau solver; single-component s-wave shipped. Production-grade with micrOMEGAs/DarkSUSY still deferred per AGENTS.md rule 17) |
| 11 | **External domain-expert review** | R16 #10 | Out-of-band | User action required |
| 12 | **Drobczyk 2025 quantitative cross-validation** | R16 #8 | ~1 week | ✅ Shipped T71.5 (t68b: chi²=213 on 1 dof; cluster-scale 526× disagreement — see V0_6_TIER_B_CLOSURE.md) |
| 13 | **Bullet Cluster likelihood upgrade** | R15 P077, R16 #2 | 1 day (sensitivity case) | ✅ Shipped T71.4 (sensitivity_0p2 variant via T41_BULLET_VARIANT env var; +1.74 log Z vs default) |
| 14 | **Reduce reliance on contested channels** (UDG, cosmic-web radio) | R16 #12 | ~1 day (tag-only) | ✅ Shipped T71.4 (CHANNEL_STATUS dict + t13 JSON fields) |
| 15 | **Higher-nlive (N_c, N_f) scan at nlive=2000** | R16 #5(b) | ~40 min wall | ✅ Shipped T71.3 (10 min via 7-way parallel runner) |
| 16 | **LZ WS2024 / Fermi-LAT full posterior shapes** | R16 #3 | ~2 weeks | ✅ Shipped T71.5 (already in production since R12 via t30_lz_real_posterior.py; stale roadmap item — see V0_6_TIER_B_CLOSURE.md) |
| 17 | **KiSS-SIDM UFD fidelity** | R16 #9 | Multi-week | ⚠️ Partial-closure T71.7: wrapper patch (KISS_SIDM_TIMEOUT_S env var) shipped; T38a N=5e4 dwarf re-run TIMED OUT at 7200s with only 2/10 snapshots. Honest verdict: UFD KiSS-SIDM is structurally compute-prohibitive at single-session budget. Defer to v0.7+ requires architectural change (smaller N or fewer snapshots). See V0_6_KISS_SIDM_TIMEOUT_VERDICT.md |
| 18 | **Form-factor ansatz uncertainty sampling** | R16 #5(c) | Multi-week | ✅ Shipped T71.6 (H4.2 sweep already on disk: log Z range = 0.375 < 1 → ROBUST; see V0_6_LATTICE_FORMFACTOR_CLOSURE.md) |
| 19 | **Lattice-informed KSFR ratios** | R16 #5(d) | Out-of-band | ⚠️ Partial T83 (2026-09-03): (3, 2) fundamental promoted to LATTICE per Shindler 2019; (2, 3) fundamental demoted to AF_EXCLUDED (asymptotic-freedom violation: SU(2) Nf=3 is IR conformal, KSFR undefined); 5/7 combos now have a defensible class (3 LATTICE, 2 ANALYTICAL, 0 ESTIMATED for the row reach-arounds, 1 N/A); (3, 4) ESTIMATED remains until a continuum-chiral reference for SU(3) Nf=4 appears. See V0_6_LATTICE_FORMFACTOR_CLOSURE.md → T83_KSFR_LATTICE_PROMOTION.md |
| 20 | **Composite-DM direct-detection forward prediction (T87)** | T86.7k+C, post-Consider4 | ~5-6 hrs wall | ⏸️ Deferred — see Item 3 below. Premature at LZ 2.6σ but allowed if user has bandwidth and wants the publishable claim. |

### Current stand-ins (good enough for v0.5/T70.x results)

- **For #1 (micrOMEGAs)**: `v0.3-prelim/code/t55_wimp_relic_calibration.py` provides a **calibrated inverse-proportionality mapping** `Ω h² ∝ 1/<σv>`, calibrated at `<σv> = 3×10⁻²⁶ cm³/s → Ω h² ≈ 0.12` (Steigman+ 2012 Eq. 12). This is the WIMP-miracle calibration, NOT a Boltzmann solver. It is sufficient for the current `T39 ε/α` posterior because the relic-density constraint is applied as a one-sided Gaussian prior, not as a forward-simulation output.
- **For #2 (hierarchical SPARC)**: `v0.3-prelim/code/t11_vdep_aggregate.py` provides a **175-galaxy calibrated saturation score** computed via the v0.3-era per-galaxy SIDM fits (`t10_vdep_per_galaxy.py` exists but was scoped out of the v0.3 joint fit per peer review of 2026-08-10). The saturation score is used as a single aggregated "SPARC compatibility" number rather than a full hierarchical likelihood.

Both stand-ins are documented in the relevant T55/T10/T11 module docstrings + `v0.3-prelim/docs/MODEL_ASSUMPTIONS_AND_LIMITATIONS.md §7`.

---

## Item 1 — External Boltzmann solver (micrOMEGAs)

**R14 Rec #9 wording:** *"Wire in micrOMEGAs (or DarkSUSY) for the relic-density calculation instead of the calibrated inverse-proportionality in T55."*

### Why this matters

The current T55 calibration assumes a **thermal freeze-out scenario with s-wave annihilation** (`<σv> ≈ const`). This is correct for a secluded WIMP at the canonical 3×10⁻²⁶ cm³/s but is **wrong for**:

1. **p-wave annihilation** (`<σv> ∝ v²`, suppressed at freeze-out T ~ m_χ/20)
2. **co-annihilation** with other dark-sector states (changes the effective yield)
3. **resonant annihilation** through a near-threshold mediator
4. **freeze-in / FIMP scenarios** (different sign of the inverse-proportionality)

The current v0.5 result (`ε ~ 4×10⁻³⁵`) sits in regime 1 territory — the mediator mass `m_A' ~ 750 MeV` is comparable to the freeze-out temperature for `m_χ ~ 800 GeV`, so p-wave corrections are O(1) and the calibrated inverse-proportionality may be off by a factor of ~2-3.

### Scope estimate (multi-month)

| Phase | Task | Wall | Risk |
|---|---|---|---|
| **1.1** | Decide solver: micrOMEGAs (C, GPL), DarkSUSY (Fortran, custom license), or hand-written Boltzmann integrator (Python, scipy) | 1 day | High — license + dependency choice |
| **1.2** | Port the dark-sector Lagrangian from `v0.3-prelim/docs/DARK_SECTOR_LAGRANGIAN.md §9` (Benchmark A) into the chosen solver's input format | 3-5 days | High — model-file authoring is the most error-prone step |
| **1.3** | Cross-validate: solver output at the canonical (3,3) point must reproduce T55's calibration to within 20% | 2-3 days | Medium |
| **1.4** | Re-run T39 (ε/α marginalization) with the new relic-density likelihood | 1 day (nlive=500) | Low |
| **1.5** | Re-run T41 with the new relic-density likelihood | 30-60 min (nlive=500) | Low |
| **1.6** | Update CHANGELOG [v0.6.0], README, LAYMAN_SUMMARY_R15 (or whatever supersedes R14) | 1 day | Low |

**Total: ~10-15 days wall, assuming no surprises.** Most of the time is in Phase 1.2 (model-file authoring).

### Dependencies to add (per AGENTS.md rule 17 — requires user approval)

- **micrOMEGAs**: external C library, ~50 MB, requires manual install via `hepmc` + `SLHAplus` + the project-specific model file. Not on pip.
- **DarkSUSY**: Fortran, custom license, requires a separate `DarkSUSY` directory in the repo.
- **Alternative**: write a hand-rolled Boltzmann integrator using `scipy.integrate.solve_ivp` (~200 lines, well-tested pattern). Pros: no external deps. Cons: p-wave/coannihilation corrections must be hand-coded (no CalCHEP help).

### Recommendation

For this user's setup (Windows + WSL, v0.3-prelim Python 3.12 env), the **hand-rolled Boltzmann integrator** is the most pragmatic option. It avoids the micrOMEGAs install headache, gives full control over the dark-sector-specific corrections, and produces a paper-grade result if the integrator is cross-validated against the Steigman 2012 analytic solution. Reference: `DarkSUSY`'s `src/da/rdr/` Fortran is a good template; the equivalent Python is ~150-300 lines depending on which freeze-out corrections are included.

---

## Item 2 — Hierarchical per-galaxy SPARC likelihood

**R14 Rec #10 wording:** *"Replace the v0.3 SPARC saturation heuristic with a full hierarchical per-galaxy forward model. Each SPARC galaxy should contribute its own velocity-curve likelihood rather than a single aggregated score."*

### Why this matters

The current v0.3 SPARC contribution is a **calibrated score** (one number, the saturation fraction). This is fast but loses information:

1. **Per-galaxy σ/m_0 posteriors** — the v0.3 model assumes all 175 galaxies share one (σ/m_0, a). A hierarchical model would let each galaxy have its own (ρ_c, r_core) and marginalize over them.
2. **Selection effects** — the v0.3 score doesn't account for the SPARC galaxy selection criteria (distance, inclination, HI quality). A full forward model with selection-function priors would correct for Malmquist bias.
3. **Galaxy-by-galaxy comparison with σ_SI** — the LZ direct-detection constraint and the SPARC constraint are correlated (both depend on the σ/m_0 → σ_SI mapping). The current model treats them as independent; a hierarchical SPARC fit could quantify the correlation.

### Scope estimate (multi-week)

| Phase | Task | Wall | Risk |
|---|---|---|---|
| **2.1** | Audit existing per-galaxy fit infrastructure: `t10_vdep_per_galaxy.py` exists but is scoped out of v0.3. Verify it runs on the 175 SPARC galaxies at the v0.5 posterior point. | 1-2 days | Medium — the per-galaxy fits have not been re-run since the v0.4 era |
| **2.2** | Define the hierarchical model: galaxy-level params (log_rho_c_i, log_r_core_i) shared with a hyper-prior (mean σ/m_0, std σ/m_0 across galaxies). Pick an emulator for the per-galaxy rotation curves (Burkert + per-galaxy baryonic correction). | 3-5 days | High — the emulator choice is the biggest source of systematic uncertainty |
| **2.3** | Wire the hierarchical SPARC likelihood into T41 (replace the saturation score with a sum of per-galaxy log-likelihoods). | 2-3 days | Medium |
| **2.4** | Re-run T41 with the new SPARC likelihood at nlive=500. Wall will increase from ~5 min to ~30-60 min (each SPARC galaxy adds a likelihood call). | 1 day compute + 2 days analysis | Low |
| **2.5** | Compare the new v0.6 posterior to the v0.5 result. If σ/m_0 shifts by > 1σ, write a "v0.5 superseded by v0.6" finding. If within 1σ, write "v0.5 confirmed" finding. | 2-3 days | Low |
| **2.6** | Update CHANGELOG + README + LAYMAN_SUMMARY | 1 day | Low |

**Total: ~2-4 weeks wall.** Most of the time is in Phase 2.2 (emulator choice + validation).

### Dependencies to add (per AGENTS.md rule 17)

- **SPARC database Lelli+ 2016** (~5 MB rotmod data) — already in `v0.1-prelim/data/Rotmod_LTG/` (175 files, synced in T70.9). No new deps.
- **Emulator framework**: `gpflow` or `botorch` (both heavy) OR hand-rolled RBF kernel regression (~300 lines). The hand-rolled option is recommended for this user's setup.

### Recommendation

This is **the more impactful of the two deferred items**. The current v0.5 result places σ/m_0 ~ 0.1 cm²/g at v=100 km/s with a factor-of-2 systematic budget driven mostly by the SPARC saturation heuristic. A hierarchical model would shrink that systematic by ~3-5×, which would push the (sigma/m_0 vs LZ sigma_SI) tension into the "decisive Bayes factor" regime if the result is as expected.

---

## Item 3 — Composite-DM direct-detection forward prediction (T87)

Added 2026-09-03 in response to user review (`consider4.docx`) and the LZ
2026-09-02 preprint's 2.6σ single-event observation at 248 keV.

### Motivation

The project's v0.7 MAP (log Z = −163.29 ± 0.085; m_χ = 770 GeV; σ/m = 0.27
cm²/g; m_φ = 453 MeV; ε ~ 10⁻³⁷) sits in the same mass window as the LZ
paper's best-fit (1000 GeV/c² Ls₁₀ EFT operator). The 248 keV single-event
observation has 2.6σ global / 3.4σ local significance, and the LZ paper
itself flags the event as requiring non-standard (inelastic or SD) interactions
to explain.

**The project's elastic-SI σ_DM-nucleon ~ 10⁻¹¹¹ cm² is 66 orders of magnitude
below LZ's sensitivity**, which means the model is "evading" LZ in the
elastic-SI channel (T62/T76 framing). But LZ is *actually* probing inelastic and
SD channels (NREFT operators O₁ˢ, O₄ᵛ, Ls₁₀; inelastic DM with mass
splitting δ ≈ 200-300 keV). The project has inelastic σ_DM-DM (T43,
T41_INELASTIC toggle) but has **not computed inelastic σ_DM-nucleon** — the
quantity that determines whether composite DM can produce the observed 248
keV recoil at the observed rate.

### What T87 will compute

1. **Inelastic σ_DM-nucleon** with composite-mediator coupling
   (Tucker-Smith & Weiner 2001 PRD 64, 043502 formalism + composite-DM
   mediator from KSFR sector). Standard NREFT O₁ˢ operator selection (no
   custom SD decomposition — uses established NREFT literature).
   Returns σ_inel_nuc(m_χ, m_φ, α_χ, δ, E_R) at the LZ event energy
   E_R = 248 keV.

2. **Forward-predicted LZ event count** at v0.7 MAP. Inputs:
   σ_inel_nuc, LZ detector parameters (2.84 tonne-years, 5.5 tonne active
   xenon mass), χ₂ threshold kinematics. Output: expected N_events with
   Poisson uncertainty.

3. **Verdict** based on data-driven comparison:
   - If predicted N_events = 1 ± Poisson_uncertainty → "predicts LZ event"
   - If predicted N_events >> 1 → "constrains composite-DM parameter space"
   - If predicted N_events << 1 → "LZ event not explained by composite DM
     at v0.7 MAP; revisit microphysics"

### Scope estimate (single-session)

| Phase | Task | Wall | Risk |
|---|---|---|---|
| **3.1** | Audit existing inelastic-DM modules: `t43_inelastic_dm.py`, `t43_inelastic_joint_fit.py`, `h4_inelastic_sweep.py`. Confirm what's reusable | 30 min | Low |
| **3.2** | Implement `t87_composite_inelastic_nucleon.py`: T&S+W inelastic formula + composite-mediator coupling + O₁ˢ NREFT operator + form-factor F²(q) at E_R = 248 keV | 1.5-2 hrs | Medium (operator selection) |
| **3.3** | Implement `t87_lz_event_rate.py`: differential rate dR/dE_R with χ₂ threshold, integrate to expected N_events in 2.84 tonne-years | 1-1.5 hrs | Low |
| **3.4** | Tests: `test_t87_inelastic_nucleon.py` — elastic-limit recovery, kinematic threshold, event-rate smoke test | 1 hr | Low |
| **3.5** | Smoke test at v0.7 MAP (m_χ = 770 GeV, m_φ = 453 MeV, g_χ = 1.19, ε ~ 10⁻³⁷, α_χ ~ 0.11). Sweep δ ∈ [50, 500] keV (matches LZ paper's 200-300 keV). | 30 min | Low |
| **3.6** | Write `T87_LZ_FORWARD_PREDICTION.md` with verdict + quantitative basis | 30 min | Low |

**Total: ~5-6 hours wall** (single-session effort, but multi-hour).

### Dependencies to add (per AGENTS.md rule 17)

**None.** Uses only existing project deps (T43, T79, T62/T76) + stdlib
(numpy, scipy.stats for Poisson). No new pip installs.

### Why this matters (the upside)

The project currently claims "compatible with LZ" (T77-T80 + T86.7j). T87
elevates this to one of three outcomes:

| Outcome | Scientific claim |
|---|---|
| **Predicts N_events ≈ 1** | **Composite DM explains the LZ event.** Transformative upgrade from "compatible" to "predicts." Publishable in PRL/PRD. |
| **Predicts N_events >> 1** | **Composite DM is constrained.** The model's inelastic channel is too strong at v0.7 MAP — falsification signal for the (m_χ, m_φ, δ) combination. |
| **Predicts N_events << 1** | **Composite DM does not explain the LZ event at v0.7 MAP.** The model remains a valid SIDM candidate but cannot claim the LZ event. |

Each outcome is a *positive scientific result* (prediction, constraint, or
null result) rather than an evasion. This is the Tier-2 effort that closes
the "10⁷¹× below LZ is a red herring" critique raised in `consider4.docx`.

### Why this can wait (the downside)

- LZ 2.6σ is **below the project's pre-registered ≥3σ trigger** (T78).
- The event may be statistical fluke or background (LZ paper itself
  expresses internal tension: "very unlikely to observe a single recoil
  at this energy without also observing several more events at lower
  energies").
- LZ has ≥3× more unanalyzed data already on disk; XENONnT and PandaX-4T
  are re-examining archives. A definitive answer may emerge from the
  collaboration within 6-12 months, independent of this project's effort.

### Recommendation

**Run T87 in a follow-up round** (not in the current T86.7k+C round, which
is docs-only). This matches the project's pre-registered T78 trigger
discipline: <3σ → doc-only (current); ≥3σ → run the analysis. T87 is the
analysis that would run at ≥3σ; running it now is *premature* but
*allowed* if the user has the bandwidth and wants the publishable claim.

---

## Priority ordering (recommendation)

If multiple items are picked up:

- **#2 first** (hierarchical SPARC) — wall-time shortest, headline-impact largest.
- **#3 second** (composite-DM direct-detection forward prediction) — single-session scope (~5-6 hrs); would elevate "compatible with LZ" to "predicts LZ event" if successful. Premature at LZ 2.6σ but allowed if user has bandwidth.
- **#1 last** (micrOMEGAs) — multi-month scope, awaits explicit user interest or v0.5 falsification of calibrated inverse-proportionality.

If only one is picked up: **#2** (still the right choice for v0.5/v0.6 headline update).

**#1 (micrOMEGAs) should wait** until either (a) the user has explicit interest in relic-density precision, or (b) the v0.5 result is shown to be in a freeze-out regime where the calibrated inverse-proportionality is provably wrong (factor of >2 shift in σ/m_0 or ε when the new solver is applied).

---

## Cross-references

- `v0.3-prelim/docs/REVIEWER_AUDIT_R14.md` — the source audit recommending these items
- `v0.3-prelim/docs/MODEL_ASSUMPTIONS_AND_LIMITATIONS.md §7` — current stand-in documentation
- `v0.3-prelim/code/t55_wimp_relic_calibration.py` — the calibrated inverse-proportionality used in place of micrOMEGAs
- `v0.3-prelim/code/t10_vdep_per_galaxy.py` — per-galaxy SIDM fit, scoped out of v0.3
- `v0.3-prelim/code/t11_vdep_aggregate.py` — the saturation-score aggregator
- `v0.3-prelim/docs/T86_PLAUSIBILITY_AUDIT.md` — LZ + Planck-scale plausibility audit (T86.7j)
- `v0.3-prelim/docs/consider4_review/` — the `consider4.docx` review that motivated Item #3
- `v0.3-prelim/code/t43_inelastic_dm.py` — inelastic σ_DM-DM (reusable for T87)
- `v0.3-prelim/code/t62_lz_direct_detection.py` + `t76_reframe_direct_detection.py` — direct-detection evasion framing
- `v0.3-prelim/code/t79_*` — composite form-factor F²(q) at LZ energies

---

**Last updated:** 2026-09-03 (T86.7k+C — added Item 3, registered T87 forward-prediction as Tier-2)
**Next action:** none scheduled — await user direction. T87 is registered but not initiated.