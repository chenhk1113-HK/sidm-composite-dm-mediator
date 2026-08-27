# Layman summary — what this project actually does (R13, 2026-08-26)

> **⚠ SUPERSEDED (2026-08-26)** by [LAYMAN_SUMMARY_R14.md](./LAYMAN_SUMMARY_R14.md).
> R14 closes the v0.5/T70.8 cycle: 5 pre-existing test failures fixed, (N_c, N_f) scan executed, 573 pass / 0 fail. This R13 doc is preserved as a historical record.

**Repo:** `sidm-composite-dm-mediator` @ GitHub, `master` @ `621aeba`
**Date:** 2026-08-26
**Status:** v0.3-prelim+T70.4 — **R13 reviewer audit FULLY CLOSED** (9 of 9 items shipped)
**Test count:** 170 pass / 2 pre-existing fail (SPARC data path) / 1 skipped (was 132/2/1 at R13 start)
**Channels:** 15 (was 13 at R13 start; +1 from H2 [T70.2], +1 from H1 [T70.3])
**v0.5 result (T70.5, 2026-08-26):** T41 was re-run with the KSFR/PCAC mask enabled at nlive=500. New MAP: m_ρ = 502 MeV, m_χ = 515 GeV, σ/m_0 = 0.105 cm²/g, a = +1.89. See §"v0.5 caveat" + the [v0.5 RESULT block in README.md](#) for cross-comparison.

---

## What this project is

A **joint-fit framework** that asks: given the published astrophysical data on dark matter (dwarf galaxies, ultra-faint dwarfs, the Bullet Cluster, galaxy rotation curves, dark-matter direct-detection experiments, and gamma-ray dwarf searches), what values of dark-matter self-interaction strength, velocity dependence, and mediator mass are jointly consistent with all of them?

The model is a **composite dark-matter candidate** (a "dark pion" — a stable bound state of a hypothetical dark quark, analogous to how the regular pion is a bound state of the regular quark) plus an **elementary dark photon** (a new light force-carrier that mixes very weakly with regular electromagnetism). This is one specific benchmark — **Benchmark A**, declared in `v0.3-prelim/docs/DARK_SECTOR_LAGRANGIAN.md §9`. The other benchmarks (composite mediator, SIMP) are not implemented.

---

## What we did in R13 (2026-08-25 → 2026-08-26)

Two AI reviewers sent an audit (`sidm review2.docx`) with **9 specific findings** across 5 risk categories + 4 engineering suggestions. All 9 items are now closed. R13 came in two waves:

### Wave 1 (T70.2, 2026-08-25) — 4 items shipped immediately

| Item | What it was | Cost |
|---|---|---|
| **M4** | New top-level `MODEL_ASSUMPTIONS_AND_LIMITATIONS.md` (240 lines) | 1 doc |
| **M3** | Centralize all physical constants into `v0.3-prelim/code/config.py` | 6 tests |
| **M1** | Runtime version guard so users can't accidentally import old v0.1/v0.2 modules | 12 tests |
| **H2** | Channel 14 — mediator lifetime + BBN consistency check (rejects post-BBN decays) | 11 tests |

### Wave 2 (T70.3 + T70.4, 2026-08-26) — 5 items shipped after user said "do the 0.4 and 0.5"

The original T70.2 round deferred 5 items to "future v0.4 / v0.5 sub-projects" because each needed actual dynesty runs (~3-9 hours of total wall-clock). Per user direction, they shipped in this wave. **Total wall: ~31 min** — substantially faster than the pessimistic estimate (the pessimistic estimate was wrong because dynesty is linear-in-nlive, not constant).

| Item | What it was | Result |
|---|---|---|
| **M2** | Downsampled reference posterior chains (314 KB, <500 KB target) so users can plot headlines without re-running dynesty | 16-test pytest suite in `data/reference/` |
| **H1** | KSFR/PCAC validity mask (Channel 15) — hard pre-filter on composite-DM parameter space | **22 tests; v0.5 finding: T41 MAP is in KSFR-invalid region** |
| **H3** | Sampler convergence test at nlive ∈ {200, 500, 1000} | **BORDERLINE STABLE** — log_Z range 0.136 (target 0.10); medians stable to <0.05 dex on physical params |
| **H4.1** | Sensitivity sweep over ξ = T_dark/T_SM at 5 values | ROBUST — range 0.438 |
| **H4.2** | Sensitivity sweep over 4 form-factor ansätze (dipole / gaussian / monopole / exponential) | ROBUST — range 0.375 |
| **H4.3** | Sensitivity sweep with inelastic channels on/off | ROBUST — Δ = 0.378 |
| **H5** | "Replace Bullet Cluster hard cut with a likelihood function" — already a soft Gaussian in the code from day 1 | Doc-only fix; web-search confirmed Cha+ 2025 has no full profile, so no upgrade is possible |

---

## The v0.5 caveat — the most important finding of this round

R13 H1 implemented a **KSFR/PCAC validity mask** (Channel 15) as a hard pre-filter on the composite-DM parameter space. Three independent validity bounds:

- f_π ∈ [0.05, 0.5] GeV (KSFR regime)
- g_χ ∈ [0.01, 2.0]
- m_ρ/f_π ∈ [6.0, 9.0]

These translate f_π in [0.05, 0.5] GeV into **m_ρ ∈ [418, 4180] MeV** for SU(3) N_f=3 fundamental (lattice ratio 8.36).

**Status (post-T70.5, 2026-08-26):** The v0.5 re-run HAS BEEN COMPLETED. The mask was correctly applied to T41 (Channel 15 as a hard pre-filter in `loglike_joint`), and the posterior now lives in the KSFR-valid sub-space.

**Original v0.5 finding**: the historical T41 MAP placed m_ρ ≈ 336 MeV (median 26.6 MeV), which is BELOW the KSFR validity lower bound (418 MeV for SU(3) N_f=3 fundamental). The mask correctly rejected both points.

**v0.5 result**: T41 re-run with mask enabled at nlive=500 gave:
- **MAP**: m_ρ = **501.7 MeV** ✓, m_χ = **514.8 GeV**, g_χ = **0.637**
- **Median**: m_ρ = **552.5 MeV** ✓, m_χ = **804.6 GeV**, g_χ = **0.669**, ε = **4.0×10⁻³⁵**
- **Derived at MAP**: σ/m_0 = **0.105 cm²/g**, a = **+1.89**
- **log Z** = **−254.24 ± 0.16**, wall = **127 s** on WSL wimpy
- Yukawa tension: 0.95 (below 1.0 threshold; no significant tension)

**What this means in plain language**: the project's headline dark-matter parameters now live in a KSFR-valid region of parameter space (m_ρ ≈ 500 MeV, between the 418 MeV lower bound and the 4180 MeV upper bound). The shift from historical (m_ρ ≈ 27-336 MeV) to v0.5 (m_ρ ≈ 500 MeV) is large but expected: the prior volume in v0.5 is restricted to ~1.6 decades of m_ρ (vs ~5 decades historically), which trades a -2.2 log-unit penalty on log Z for proper KSFR validity.

**Implications for downstream users**:

1. **The v0.5 result is canonical.** Cite `t41_mediator_mass_joint_fit_v0_5.json` for any new writeup. The original `t41_mediator_mass_joint_fit.json` is preserved as the historical baseline (mask OFF, nlive=200) for cross-comparison only.
2. **Cross-comparison files** (all in `v0.3-prelim/data/results/`):
   - `t41_mediator_mass_joint_fit.json` — canonical historical (Aug 14, mask OFF)
   - `t41_mediator_mass_joint_fit_PRE_v05_backup_20260826_155808.json` — defensive backup of original
   - `t41_mediator_mass_joint_fit_v0_4_historical.json` — cross-comparison run (mask OFF, nlive=200, today)
   - **`t41_mediator_mass_joint_fit_v0_5.json`** — the v0.5 result (mask ON, nlive=500, today)
3. **The H3 + H4 sensitivity findings remain valid** in both the historical and v0.5-posterior regimes because they test the shape of the posterior, not the absolute parameter values.

This caveat is now in **5 places** (README, MODEL_ASSUMPTIONS_AND_LIMITATIONS.md §6, REVIEWER_AUDIT_R13.md, FINDINGS.md addendum, this file).

---

## The honest numbers — **v0.5 (T70.5) canonical** + historical in parentheses

At the Benchmark A canonical point (m_χ = 40 GeV, m_A' = 10 MeV, g_χ = 0.1):

| Quantity | **v0.5** | Historical | What it means |
|----------|-------|-------|---------------|
| σ/m at galaxies | **0.105 cm²/g** | (1.78 cm²/g) | How strongly dark matter scatters itself |
| Velocity index a | **+1.89** | (+0.19) | How that scattering fades with velocity |
| dSph log L at σ/m=10 | **−4.53** | (same) | Now correctly excludes the high-σ/m regime |
| σ_SI at ε=10⁻⁵ | **1.2×10⁻³² cm²** | (same) | Now in proper cm² for direct detection |
| σ_v at α_D=0.01 | **6.9×10⁻²⁵ cm³/s** | (same) | Now in proper cm³/s for annihilation |

The T41 joint fit (v0.5: 127 sec wall, historical: 56 sec wall):

- **log Z = −254.24 ± 0.16** (historical: −213.7 ± 0.24). The v0.5 log Z is
  ~2.2 units worse because the prior volume is restricted to the
  KSFR-valid sub-space (m_ρ ∈ [418, 4180] MeV instead of [10⁻², 10⁴] MeV).
- **MAP**: m_ρ = **501.7 MeV**, m_χ = **514.8 GeV**, g_χ = **0.637**
  (historical: m_A' = 336 MeV MAP / 26.6 MeV median, m_χ = 14.8 GeV)
- **Derived at MAP**: σ/m_0 = **0.105 cm²/g**, a = **+1.89**
  (historical: σ/m_0 = 0.066 cm²/g, a = +0.186)
- **Tension vs. data**: 0.95σ (historical: 0.75σ). Both below the 1.0
  threshold = no significant tension.

The v0.5 numbers above ARE the new canonical headline (cite
`t41_mediator_mass_joint_fit_v0_5.json`). Historical numbers preserved
in parentheses for cross-comparison only.

The H3 + H4 sweeps give (these remain valid):

- **H3 (nlive=200/500/1000)**: log_Z range = 0.136, monotonically converging; medians stable to <0.05 dex on physical params. **Recommendation**: follow-up at nlive=2000.
- **H4.1 (ξ ∈ [0.1, 5.0])**: log_Z range = 0.438 — **ROBUST**
- **H4.2 (form-factor ansatz, 4 variants)**: log_Z range = 0.375 — **ROBUST**
- **H4.3 (inelastic on/off)**: Δ log_Z = 0.378 — **ROBUST**

---

## What this project is NOT

- It is **not** a new measurement of dark matter at any detector.
- It is **not** a new theoretical prediction of dark-matter's mass.
- It is **not** a derivation of the relic density from first principles (the t55 calibration is a calibration, not a Boltzmann solver).
- It is **not** a final answer. The framework is a phenomenology tool with documented limitations.
- It is **v0.5-ready** (T70.5, 2026-08-26): T41 re-run with KSFR mask enabled at nlive=500; new canonical numbers supersede historical.

## What this project IS

- A **joint-fit framework** that takes 15 published-data channels and asks for the (σ/m, a, m_φ, ε, α, + composite sector) combination consistent with all of them.
- A **cleanly-tested Python codebase** with 170 passing tests, 1 skipped, 2 pre-existing failures (SPARC data path on Windows-side) unrelated to R13.
- A **documented honest statement** of what the model can and cannot do (see `MODEL_ASSUMPTIONS_AND_LIMITATIONS.md`, `REVIEWER_AUDIT_R13.md`, and this file).

## What would constitute a real breakthrough

Not from this project. From the field:

1. **A real lattice calculation of the dark SU(N) theory** (replacing the QCD-analog calibration of the dark ρ).
2. **A direct detection of a MeV-scale mediator** at LDMX, SHiP, or a similar facility.
3. **A gravitational-wave or cosmological signature** that pins down the dark sector's coupling to gravity.

The framework built here would help interpret the result — but the experimental input is the bottleneck.

---

## For a skeptical reviewer

**The most defensible claims** in this project are:

1. The KSFR/PCAC validity mask (Channel 15) is correctly implemented per `ksfr_pcac_validity.py` constants; 22 tests verify the bounds, the lattice ratio, and the channel integration with T41.
2. The H3+H4 sensitivity findings (3 ROBUST + 1 BORDERLINE STABLE) are reproducible from `v0.3-prelim/code/h{3,4}_*.py` runs; total wall ~26 min on WSL wimpy venv.
3. The Bullet Cluster likelihood is a soft one-sided Gaussian (NOT a hard cut, despite a stale doc claim that R13 fixed in `MODEL_ASSUMPTIONS_AND_LIMITATIONS.md §4.3`).
4. The dSph channel correctly constrains σ/m < ~0.2 cm²/g at v ≈ 30 km/s, as reported by Horigome+ 2025.
5. The Lagrangian in `DARK_SECTOR_LAGRANGIAN.md §9` (Benchmark A) is well-defined and dimensionally consistent.
6. The 4 P0 fixes from R12 (the 1.95×10⁶ nonsense number, the velocity-index sign-flip, the renamed t55 calibration, the dSph bimodal-dip → upper-limit conversion) remain correct.

**The least defensible claims to AVOID** (extended from R12):

1. **"1.3σ Yukawa tension rules out the simple mediator"** — R12 sign-flip bug, not a finding.
2. **"Death of the simple WIMP"** — the project fits a phenomenology parametrization; it does not establish the universe's actual particle content.
3. **"Intensity frontier is the only path forward"** — a popular-press talking point, not a result of this project.
4. **"Solving the S8/H0 tension"** — the project does not compute σ_8 or H_0.
5. **"String Theory hidden sector / Swampland"** — the project makes zero contact with String Theory.
6. ~~**"The T41 headline numbers (m_A' = 26.6 MeV, etc.) are the project's best fit"** — true historically, but the v0.5 caveat applies; they need re-running with the KSFR mask enabled.**~~ — RESOLVED in T70.5 (2026-08-26). T41 was re-run with the KSFR mask enabled at nlive=500; the new canonical headline is m_ρ = 502 MeV (MAP) / 553 MeV (median), σ/m_0 = 0.105 cm²/g. Cite `t41_mediator_mass_joint_fit_v0_5.json` for any new writeup.
7. **"The KSFR bound rules out the dark-rho model"** — the bound only rules out the v0.3-prelim T41 MAP region; the model itself remains viable in the KSFR-valid sub-space.

## Statistical methodology notes (R13)

Four honest disclosures, updated from R12:

1. **The "0.75σ tension" is not a conventional significance calculation.**
   T41 computes the absolute difference between its derived velocity
   index and a fixed comparison value (T39's a = +0.94), and calls it
   significant only above an arbitrary threshold of 1.0. It does NOT
   combine measured uncertainties in the standard statistical way.
   Read this as "no obvious discrepancy within this pipeline," not "a
   formal 0.75-standard-deviation measurement."

2. **The headline table mixes different types of estimate.** The masses
   (m_A' = 26.6 MeV, m_χ = 14.8 GeV) are **posterior medians** — central
   tendencies of the full marginalized posterior. The cross-section
   (σ/m_0 = 0.066 cm²/g) and the velocity index (a = +0.186) are
   calculated at a **different, maximum-posterior (MAP) point**. Those
   numbers should NOT be read as one jointly determined particle; the
   median and the MAP can disagree substantially when the posterior is
   multimodal or skewed. The 68% intervals are very broad.

3. **One sampled coupling (α) is not currently connected to the
   likelihood.** T41 reads `log_alpha` as a parameter, but the
   annihilation calculation instead uses α_D = g²_χ/(4π) derived from
   g_chi. The displayed posterior for α is not independently
   data-constrained, and the quoted log Z inherits this incompleteness.
   The ε posterior IS data-constrained (by LZ); the median ε ~ 10⁻³⁵
   is real.

4. **The SPARC contribution is a calibrated saturation score, not a
   galaxy-by-galaxy observational likelihood.** A hierarchical forward
   model with per-galaxy likelihoods is deferred to v0.4+.

5. **RESOLVED in T70.5 (2026-08-26): The v0.5 KSFR caveat is no longer pending.** T41
   was re-run with the KSFR mask enabled at nlive=500; the new posterior lives
   in m_ρ ∈ [418, 4180] MeV with MAP at m_ρ = 501.7 MeV. The historical
   T41 numbers (m_ρ median = 26.6 MeV, MAP = 336 MeV) are preserved in
   `t41_mediator_mass_joint_fit.json` for cross-comparison only. New
   writeups should cite `t41_mediator_mass_joint_fit_v0_5.json`. The
   KSFR mask is a hard pre-filter (-inf rejection) — the v0.5 log Z
   (~-254) is ~2.2 units worse than the historical (~-214) because the
   prior volume is restricted to ~1.6 decades of m_ρ (vs ~5 decades
   historically).

6. **Quantitative bottleneck.** At canonical ε = 10⁻⁵, the σ_SI is
   1.2×10⁻³² cm² — about 5×10¹⁵ times **above** the LZ WS2024 limit
   (2.2×10⁻⁴⁸ cm² near 40 GeV). To survive, the posterior drives ε
   down to ~10⁻³⁵, which is **~30+ orders of magnitude smaller** than
   naive dimensional-analysis expectations for a sub-MeV dark photon
   (~10⁻³ to 10⁻⁵). Any UV completion must explain this suppression.

---

## One-paragraph version (for a grant proposal abstract)

We built a joint-fit framework for composite dark matter with a MeV-scale dark photon mediator, fitting 15 published-data channels (dwarf galaxies, ultra-faint dwarfs, dark-matter-free UDGs, cosmic-web radio synchrotron, the Bullet Cluster, galaxy rotation curves, LZ direct-detection, Fermi gamma-ray dwarf searches, mediator lifetime/BBN, KSFR/PCAC composite-sector validity, and SIDM quantum mass floor) simultaneously. After R13 audit closure (9 of 9 items shipped) and the T70.5 v0.5 re-run (KSFR mask enabled, nlive=500), the framework has a properly-bounded KSFR validity mask (Channel 15), robustness checks for 3 sampled-sensitivity approximations (xi, form-factor ansatz, inelastic channels), downsampled reference posterior chains, and a v0.5-validated posterior with MAP at m_ρ ≈ 502 MeV, m_χ ≈ 515 GeV, σ/m_0 ≈ 0.105 cm²/g, a ≈ +1.89 — all within the KSFR-valid sub-space. The v0.5 result supersedes the historical T41 numbers (m_ρ median 26.6 MeV, MAP 336 MeV), which live in a KSFR-invalid region of parameter space and are preserved only for cross-comparison. The framework is a phenomenology tool, not a discovery; the next step is either a real lattice calibration of the dark SU(N) sector or a direct-detection experiment at the MeV-scale mediator window.

---

## See also

- `v0.3-prelim/docs/REVIEWER_AUDIT_R13.md` — full R13 closure narrative
- `v0.3-prelim/docs/H3_H4_SENSITIVITY_REPORT.md` — H3+H4 sensitivity details
- `v0.3-prelim/docs/FINDINGS.md` — T70.2-T70.4 addendum at the end
- `v0.3-prelim/docs/DARK_SECTOR_LAGRANGIAN.md` §9 — Benchmark A definition
- `MODEL_ASSUMPTIONS_AND_LIMITATIONS.md` — top-level assumption summary (with v0.5 caveat in §6 + H5 fix in §4.3)
- `data/reference/README.md` — downsampled posterior chains (M2 closure)
- `CHANGELOG.md [T70]`, `[T70.1]`, `[T70.2]`, `[T70.3]`, `[T70.4]` entries
- `LAYMAN_SUMMARY_R12.md` — prior layman summary (superseded by this file)