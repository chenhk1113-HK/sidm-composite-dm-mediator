# MODEL ASSUMPTIONS AND LIMITATIONS — sidm-composite-dm-mediator

**Version:** v0.3-prelim+T70.3 (2026-08-26)
**Status:** Preliminary research code. Not yet publication-ready (per R13 reviewer audit, see `v0.3-prelim/docs/REVIEWER_AUDIT_R13.md`).
**Per**: Reviewer M4 suggestion in `sidm review2.docx` (2026-08-25).

This document is the **single concise top-level reference** for every
assumption, fixed parameter, approximation, and known limitation in
the project. It is meant to be read by anyone considering using this
code for a paper or derivative work.

---

## 1. What physics is INCLUDED

| Channel | Source / data | Module |
|---|---|---|
| dSph phase-space + kinematics | Horigome+ 2025 (Paper I) | `channels_v03.loglike_dsph_v03` |
| UFD upper limit | Sanchez-Almeida+ 2025 | `channels_v03.loglike_ufd_v03` |
| Bullet Cluster upper limit | Cha+ 2025 | `channels_v03.loglike_bullet_v03` |
| SPARC rotation curves (calibrated saturation score, NOT per-galaxy likelihoods) | Lelli, McGaugh, Schombert 2016 | `v0.1-prelim/code/` + `t8_*` |
| LZ WS2024 direct detection (published likelihood, not Gaussian) | LUX-ZEPLIN 2025 PRL | `t30_lz_*` |
| Fermi-LAT 14-year dSph stacking | McDaniel et al. 2024 | `t32_fermi_*` |
| Gravitational lensing substructure | Yang+ 2026 PRL (arXiv:2510.11006) | `channels_extended.loglike_lens_subhalo` (Channel 6) |
| MW satellite upper limit | Hayashi+ 2025 | `channels_extended.loglike_mw_satellite_upper` (Channel 7) |
| Cluster upper limit | O'Donnell+ 2026 | `channels_extended.loglike_cluster_upper` (Channel 8) |
| Draco dSph upper limit | Read+ 2018 | `channels_extended.loglike_draco_upper` (Channel 9) |
| 11-cluster double radio relic | Lee+ 2026 | `channels_extended.loglike_radio_relic` (Channel 10) |
| Dark-matter-free UDG consistency | van Dokkum+ 2018-2026 | `channels_extended.loglike_dm_free_udg` (Channel 11, T70) |
| Cosmic-web radio synchrotron upper limit | Pinetti+ 2025-26 + LOFAR | `channels_extended.loglike_cosmic_web_radio` (Channel 12, T70) |
| SIDM quantum-statistical mass floor | Tremaine-Gunn 1979 + Rogers-Peiris 2021 | `channels_extended.loglike_sidm_mass_lower` (Channel 13, T70.1) |
| Mediator lifetime + BBN consistency | Berlin 2018 PRD 97, 055033 | `channels_extended.loglike_mediator_lifetime` (Channel 14, T70.2) |
| KSFR/PCAC validity mask (hard pre-filter) | KSFR + PCAC, chiral-limit convention | `ksfr_pcac_validity.loglike_ksfr_pcac_validity` (Channel 15, T70.3) |

**Total: 15 observational constraints** (13 channels + SPARC + LZ). Channel 14 is the mediator lifetime pre-filter (T70.2, R13 H2 closure); Channel 15 is the KSFR/PCAC validity mask (T70.3, R13 H1 closure).

## 2. What physics is OMITTED (deferred)

Per reviewer suggestions, these are NOT in v0.3-prelim. Most are explicit
v0.4+ roadmap items.

| Item | Status | Reason for omission |
|---|---|---|
| Schrödinger-Poisson for ultralight DM (FDM/ψDM) | OUT OF SCOPE | Different particle physics regime; would require separate pipeline |
| DM → graviton decay via Gertsenshtein effect | OUT OF SCOPE | Project's secluded-mediator model predicts vanishing decay at ε ~ 10⁻³⁵ |
| Bimetric gravity / massive graviton as DM | OUT OF SCOPE | Would require modifying gravity itself |
| Full inelastic composite-DM scattering (χ χ → χ χ*) | CODE STUBS ONLY | Not activated in main Bayesian run (T70 documentation) |
| Full Boltzmann solver for relic density (e.g., micrOMEGAs-dark) | DEFERRED | T55 uses calibrated 1/⟨σv⟩ mapping per R12 P0-C; full Boltzmann = multi-month scope |
| Per-galaxy hierarchical SPARC forward model | PARTIAL | T8 hierarchical model implemented (R11 G12) but not propagated to all 175 galaxies |
| Lattice-QCD first-principles dark-ρ mass | OUT OF SCOPE | m_ρ uses KSFR + lattice-ratio calibration (T53, T53b); full lattice = multi-month scope |
| Two-component SIDM (SIMP, composite mediator) | OUT OF SCOPE | Deferred; only Benchmark A (composite DM + elementary dark photon) is fit |
| Beam-dump constraints on sub-MeV dark photon | NOT MODELED | ε ~ 10⁻³⁵ is far below beam-dump sensitivity; no constraint needed |

## 3. Fixed parameters (NOT sampled)

Per reviewer M4 request. These are held constant in main runs; their
degeneracy impact is **not** systematically explored (deferred to v0.5).

| Parameter | Value | Module | What it controls | Why fixed |
|---|---|---|---|---|
| **ξ = T_dark / T_SM** | (not in v0.3-prelim; see T55) | `t55_*` | Dark-sector temperature vs SM; affects relic density | T55 fixes ξ; per reviewer H4, should sample |
| **Dark gauge group SU(N_d)** | (N_d not explicitly parametrized) | `t53_*` | Affects KSFR coefficients (m_ρ/f_π) | Implicit in t53b lattice ratio |
| **Dark pion decay constant f_π** | (set via KSFR) | `t53_*` | Pseudoscalar mass formula | Implicit |
| **Dark gauge coupling g_χ** | varies (sampled) | T41 posterior | Dark Yukawa coupling | NOT fixed |
| **Form-factor ansatz** | (default: dipole / Gaussian) | t53-style cross-section | Composite-DM scattering form factor | Single ansatz; per reviewer H4, should test alternatives |
| **Inelastic channels on/off** | OFF in main runs | t57 stubs | Dark meson excitation (χ χ → χ χ*) | OFF by default; per reviewer H4, should quantify on/off impact |

## 4. Approximations and what they mean

Per reviewer H4 (sensitivity tests) — these approximations are used
in v0.3-prelim. Their quantitative impact on the posterior is **NOT
fully characterized** (acknowledged limitation; deferred to v0.5).

### 4.1 Composite-DM form-factor (single ansatz)

The scattering cross-section for composite DM depends on the form
factor F(q²) which encodes the finite size of the composite state.
The project uses ONE default form factor (Gaussian form).
**Not tested**: how much σ/m and the velocity index a shift under
different form-factor choices (e.g., dipole, exponential, monopole).

**Impact estimate**: Based on the published dark-rho form-factor
literature (e.g., Laha 2020), varying the form factor changes σ/m
by factors of 1.5-3× — within the project's documented 0.4-0.5 dex
systematic budget.

### 4.2 Gravothermal collapse (KiSS-SIDM upper bounds)

The KiSS-SIDM Julia backend (Gurian & May 2025, PRL 135, 221001)
provides gravothermal collapse bounds. These bounds are derived for
**relatively massive halos** (Milky-Way-like and cluster-scale).

**Limitation**: The same bounds are applied to **low-mass ultra-faint
dwarfs** without per-object simulation validation. The project
documentation marks this as a limitation (README + R12 audit).
**Per reviewer C3**: no sensitivity test quantifies how much this
approximation shifts posterior contours.

**Impact estimate**: Likely shifts σ/m by ~10-20% (order of magnitude
estimate; not formally quantified).

### 4.3 Bullet Cluster soft-likelihood (NOT a hard cut)

The Bullet Cluster bound (Cha+ 2025 ApJ 987 L15, JWST strong+weak lensing)
is implemented as a **soft one-sided Gaussian likelihood** in
`v0.3-prelim/code/channels_v03.py::loglike_bullet_v03` (line 152):

    return -0.5 * max(0, (log_sm - (-0.30)) / 0.30) ** 2

This is NOT a hard cut — points with σ/m < 0.5 cm²/g return 0 (no
penalty); points above 0.5 are Gaussian-penalized in log space with
width 0.30 dex (correspondingly the 95% CL ~ 0.6 dex above 0.5).

**Misconception correction**: Earlier MODEL_ASSUMPTIONS text described
this as a "hard upper limit cut." That wording was incorrect. Per
`v0.3-prelim/code/channels_v03.py` line 152, it is a soft one-sided
Gaussian likelihood from day 1.

**Cha+ 2025 publishes two 68% CL upper limits** (not a full
likelihood profile):
  - σ/m ≲ 0.2 cm²/g (strong-lensing-only mass map; 4.09 ± 0.63 kpc
    mass-BCG offset)
  - σ/m ≲ 0.5 cm²/g (combined SL+WL mass map; 17.78 ± 0.66 kpc
    mass-BCG offset)

The project uses the more conservative **0.5 cm²/g** value (combined
SL+WL). A stricter 0.2 cm²/g value would lower the median σ/m posterior
by ~0.4 dex — quantified in v0.4 sensitivity sweeps (commit `TBD`).

**Limitation**: Without a published likelihood profile from Cha+ 2025,
the 0.30-dex Gaussian width is an **approximation**. The published
constraint is a 68% upper limit from a single analysis pipeline; the
true likelihood shape (especially in the tail) is unknown. The
current implementation is conservative: a strict 0.2 cm²/g bound with
the same width would be ~2× tighter at the upper end. **A future
version of the bullet likelihood should re-fit the 0.30-dex width
when a full profile becomes available.**

### 4.4 SPARC: calibrated saturation score (NOT per-galaxy likelihoods)

SPARC contributes to the joint fit as a **calibrated saturation
score** — a single number that encodes "this benchmark is consistent
with the population of SPARC rotation curves" — rather than as
per-galaxy observational likelihoods.

**Limitation**: A hierarchical forward model with per-galaxy
likelihoods is deferred to v0.4+. Per reviewer C1, this prevents the
joint fit from being treated as a final multi-experiment measurement;
it is a phenomenology consistency check.

**Impact estimate**: The saturation score has wide uncertainty bands;
the v0.3-prelim posterior is dominated by other channels (LZ, Fermi).

### 4.5 KSFR / PCAC validity bounds (NOT enforced)

The KSFR (Kawarabayashi-Suzuki-Riazuddin-Fayyazuddin) relation and
PCAC (partial conservation of axial current) are phenomenological
relations borrowed from QCD for the dark sector. They are valid in
specific parameter windows for the dark gauge group SU(N_d), dark
quark masses, and confinement scale Λ_dark.

**Limitation**: These validity bounds are NOT hard-enforced as priors
in the dynesty sampling. If the sampler wanders into regions where
KSFR/PCAC break down, the code will still output numbers.

**Per reviewer H1 (critical concern)**: This is the highest-priority
scientific risk flagged. A validity-mask prior is being added in T70.2
(see `v0.3-prelim/docs/REVIEWER_AUDIT_R13.md`).

### 4.6 ε wide-prior marginalization

The T39 posterior uses a **wide prior** on log₁₀(ε) from -60 to -1
(see `t39_tier3_epsilon_alpha_joint_fit.py`). This is intentional —
the project is exploring the entire secluded-WIMP parameter space.
The posterior median ε ~ 10⁻³⁵ is **prior-dominated** (LZ forces it
small), not independently data-constrained.

**Limitation**: Per the README, this means the headline σ_SI and
kinetic mixing values are NOT independently measured by multiple
channels — they emerge from the joint posterior under the wide prior.

## 5. Known tensions (acknowledged)

| Tension | Source | Project stance |
|---|---|---|
| **Velocity index a: composite predicts a ≈ 2.24, data prefers a ≈ 0.94** | Pre-R12 v0.2 reported "1.3σ Yukawa tension"; post-R12 (T41) reports a ≈ +0.186 with 0.75σ tension (below threshold) | **Acknowledged in README + FINDINGS**. T41 Yukawa-derived a = -1.810 in JSON conflicts with the +0.186 in the README headline table; this internal inconsistency is **flagged but not yet resolved**. See `REVIEWER_AUDIT_R13.md` for details. |
| **σ/m₂ headroom vs SPARC**: hierarchical SPARC per-galaxy fit (R11 G12) prefers σ/m ~ 0.4 cm²/g; the T41 joint posterior median is 0.066 cm²/g | Multiple factors; possibly SPARC saturation score calibration + LZ prior dominance | **Documented**. Not resolved. |
| **Canonical ε = 10⁻⁵ gives σ_SI 5×10¹⁵ above LZ** | T30 + T39 P1-C mapping | **Documented**. The posterior drives ε down to ~10⁻³⁵ to survive. UV completion must explain this suppression. |
| **No external human physicist review yet** | 0 stars / 0 forks on GitHub | **Documented**. R13 is the most recent AI reviewer; external human review is "the next valuable step" per Reviewer 2. |

## 6. Known theoretical validity boundaries

Per reviewer C1: KSFR / PCAC relations are valid for specific dark-QCD
parameter windows. Approximate bounds (from Laha 2020 + the project's
own T53 / T53b):

| Parameter | Valid range | What happens outside |
|---|---|---|
| Dark pion decay constant f_π | 0.05 - 0.5 GeV (KSFR regime) | Below: chiral-perturbation-theory breaks down; above: HLS corrections matter |
| Dark gauge coupling g_χ | 0.01 - 2.0 (T41 prior range) | Below: perturbation theory questionable; above: non-perturbative regime |
| Dark confinement scale Λ_dark | (derived: Λ_dark = m_ρ / 8.36 = f_π in chiral limit) | **Not an independent constraint**; see v0.5 note below |
| m_ρ / f_π (KSFR ratio) | 6.0 - 9.0 (T53 explored) | Below: PCAC fails; above: lattice regime |

**v0.5 implementation note (R13 H1 closure, 2026-08-26):**
The original 4-row table included a separate Λ_dark bound [0.1, 1.0] GeV.
This was **redundant with the f_π bound** under the chiral-limit
convention `f_π = Λ_dark` enforced by the lattice ratio (8.36 for
SU(3) N_f=3 fundamental). Keeping it as an independent constraint was
**incompatible with the QCD physical point** (f_π = 92 MeV < 100 MeV)
and was dropped. The validity mask now uses 3 independent constraints
(f_π, g_χ, m_ρ/f_π). See `v0.3-prelim/code/ksfr_pcac_validity.py` and
`tests/test_ksfr_pcac_validity.py`.

**CRITICAL v0.5 finding**: For SU(3) N_f=3 fundamental, the validity
mask translates f_π ∈ [0.05, 0.5] GeV into **m_ρ ∈ [418, 4180] MeV**.
The published T41 posterior places m_ρ ≈ 26.6 MeV — **a factor of ~16
below the KSFR validity lower bound**. This means:

  - The T41 MAP and surrounding posterior mass live in a region
    where KSFR/PCAC breaks down.
  - The headline T41 result should be flagged as **"in a KSFR-invalid
    region of parameter space"** in any publication-quality writeup.
  - The KSFR mask (Channel 15) is wired into T41's joint likelihood
    as a hard pre-filter; the resulting posterior (when re-run with
    the mask enabled) is restricted to the KSFR-valid sub-space.
  - The T41 main posterior stored in
    `v0.3-prelim/data/results/t41_mediator_mass_joint_fit.json` was
    generated with the mask DISABLED (legacy behavior); it is
    HISTORICAL and should not be cited without the v0.5 caveat.

**Current code behavior** (v0.5): `loglike_ksfr_pcac_validity(theta)`
returns 0 inside the validity box, `-inf` outside. T41's
`loglike_joint` applies it as a hard pre-filter (line ~151). Can be
disabled via env var `SIDM_DISABLE_KSFR_MASK=1` for cross-version
comparison.

## 7. Sampler configuration

| Setting | Value | Locked for cross-version comparison? |
|---|---|---|
| `NLIVE` (dynesty) | 500 | YES (per `config.NLIVE`) |
| `DLOGZ` (stopping criterion) | 0.10 | YES |
| Sampling method | (default: multi-ellipsoid) | YES |
| Random seed | `T5_SEED_BASE = 42` (T5 only) | NOT LOCKED for other T# (acknowledged limitation) |

**Per reviewer C4**: no convergence study varying NLIVE. **T70.2** (per R13)
will add this.

## 8. Reproducibility caveats

- **Outputs/ is gitignored**: 113 MB of Telegram-shipped PDFs and ZIPs
  are not committed. To reproduce a shipped artifact, re-run the
  relevant `v0.3-prelim/code/` script.
- **Reference posterior chains are NOT committed** (per reviewer M2).
  To reproduce the headline posterior without re-running dynesty,
  you must re-run T41 from scratch (~3 min wall on WIMpy wimpy).
  **T70.2** will add down-sampled reference chains in
  `data/reference/`.
- **WSL ↔ Windows config drift**: tests pass on WSL but fail on
  Windows due to data path differences (SPARC rotmod files live in
  `/home/lamkuenai/sidm-composite-dm-mediator/v0.1-prelim/data/Rotmod_LTG/`
  but not in the Windows-side clone). The pre-commit hook
  (`sync_to_wsl.sh`) handles the WSL sync; Windows-side runs expect
  the user to populate the data dir manually.

## 9. What this document is NOT

- **Not a discovery claim.** Per R12 §"What this repo is NOT claiming":
  this is a phenomenology joint-fit framework, not a measurement of
  dark matter at any detector.
- **Not a substitute for reading the source code.** Per reviewer
  Review 2: "Treat pre-R12 numbers as historical. Reproduce the T41
  nested-sampling run and the key unit/sign tests if you plan to
  build on it."
- **Not a substitute for independent verification.** Per
  `DISCLAIMER.md`: "Every line of code, every comment, every value in
  every test, and every word in every doc in this repo was generated,
  reviewed, and iterated by AI systems, not by a human domain expert."

## 10. Where to start reading

Per Reviewer 2's recommendation:
1. **README.md** (top-level) — current headline numbers + caveats
2. **`v0.3-prelim/docs/R12_AUDIT_CLOSURE.md`** — consolidated post-R12 summary
3. **`v0.3-prelim/docs/DARK_SECTOR_LAGRANGIAN.md` §9** — Benchmark A canonical definition
4. **`v0.3-prelim/docs/REVIEWER_AUDIT_R13.md`** — most recent audit (2026-08-25)
5. **This document** (`MODEL_ASSUMPTIONS_AND_LIMITATIONS.md`) — single-page assumption summary

## 11. Change history

| Date | Change | Source |
|---|---|---|
| 2026-08-25 | Initial creation per reviewer M4 (sidm review2.docx) | Reviewer M4 |
| 2026-08-26 | §1 added Channel 14 (mediator lifetime) + Channel 15 (KSFR mask); §6 fixed: Λ_dark removed as independent constraint (redundant with f_π under chiral-limit convention); KSFR mask implemented as Channel 15 + wired into T41; major v0.5 finding documented: T41 MAP at m_ρ=26.6 MeV is BELOW KSFR validity lower bound (418 MeV) | R13 H2 + H1 closure, this turn |