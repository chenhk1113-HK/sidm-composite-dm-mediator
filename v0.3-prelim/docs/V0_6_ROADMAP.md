# v0.6 Roadmap — Deferred Items from R14

> **Status (2026-08-26):** Two R14 reviewer recommendations deferred to v0.6+ remain on this roadmap. Both are **multi-day/multi-week scope** and cannot ship in a single round. This document is the handoff for whoever picks them up.

**Repo:** `sidm-composite-dm-mediator` @ GitHub, `master` @ T70.9 (post-R14)
**Scope source:** R14 reviewer recommendations [R14 #9, R14 #10]
**Standing-version when written:** v0.3-prelim+T70.9

---

## Items on this roadmap

| # | Item | R14 rec | Scope estimate | Status |
|---|---|---|---|---|
| 1 | **micrOMEGAs interface** for coupled Boltzmann solver | R14 Rec #9 | Multi-month | Deferred |
| 2 | **Hierarchical per-galaxy SPARC likelihood** | R14 Rec #10 | Multi-week | Deferred |
| 3 | **Inelastic scattering in primary production run** | R15 P075 | ~30 min wall | Ship this round (T71.1) |
| 4 | **T41 at nlive=2000** for publication-grade BFs | R15 P074 | ~50-100 min wall | Ship this round (T71.1) |
| 5 | **CMB spectral-distortion Channel 16** | R14 Rec #3 | (already shipped in T70.8) | ✅ Shipped |
| 6 | **runtime-guard against legacy v0.1/v0.2 imports** | R13 M1 | (already shipped in T70.4) | ✅ Shipped |

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

## Priority ordering (recommendation)

If both items are picked up, **do #2 first** because (a) the wall-time is shorter, (b) the impact on the headline v0.5/v0.6 result is larger, and (c) the per-galaxy fit infrastructure already partially exists.

If only one is picked up, **#2** is the right choice.

**#1 (micrOMEGAs) should wait** until either (a) the user has explicit interest in relic-density precision, or (b) the v0.5 result is shown to be in a freeze-out regime where the calibrated inverse-proportionality is provably wrong (factor of >2 shift in σ/m_0 or ε when the new solver is applied).

---

## Cross-references

- `v0.3-prelim/docs/REVIEWER_AUDIT_R14.md` — the source audit recommending these items
- `v0.3-prelim/docs/MODEL_ASSUMPTIONS_AND_LIMITATIONS.md §7` — current stand-in documentation
- `v0.3-prelim/code/t55_wimp_relic_calibration.py` — the calibrated inverse-proportionality used in place of micrOMEGAs
- `v0.3-prelim/code/t10_vdep_per_galaxy.py` — per-galaxy SIDM fit, scoped out of v0.3
- `v0.3-prelim/code/t11_vdep_aggregate.py` — the saturation-score aggregator

---

**Last updated:** 2026-08-26 (T70.9 + T71.0 cycle)
**Next action:** none scheduled — await user direction or reviewer escalation.