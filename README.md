# sidm-composite-dm-mediator

> ⚠️ **Disclaimer:** It is a personal project out of curiosity, made using Hermes with **MiniMax M3** as the coder, **Doubao** and **Qwen 3.8 Max** as reviewers.

**Bayesian constraint pipeline for self-interacting dark matter (SIDM) with a composite-DM microphysics extension and a secluded-mediator detection feasibility survey.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.3--prelim--D15--CORRECTED3-blue)](VERSION)
[![arXiv:2506.22997](https://img.shields.io/badge/cross--validated-arXiv%3A2506.22997-b31b1b)](https://arxiv.org/abs/2506.22997)

> **Heads-up (2026-08-14):** Project renamed from `dm-sidm-pipeline`. All
> version identifiers below (`v0.X-prelim-DYY`, `Mediator_Detection_vN`)
> refer to the same work — just under a more descriptive name. See the
> rename note at the top of `CHANGELOG.md` for details.

---

## What this is

A self-contained Bayesian analysis pipeline that:

1. **Constrains the SIDM cross-section** σ/m from five observational channels:
   SPARC rotation curves, dwarf spheroidal kinematics, ultra-faint dwarfs,
   the Bullet Cluster, and LZ direct-detection limits — with KiSS-SIDM
   gravothermal collapse as the physical anchor.

2. **Tests two-component SIDM** with mass segregation (heavy→centre,
   light→outskirts) against single-component models using Bayes factors
   on real published SIDM2v curves from Yang, Fan, Hou, Tsai 2026.

3. **Extends to composite DM** (dark glueballs, dark rho, dark baryons
   in SU(N_dark)) and computes σ/m, relic density, and direct-detection
   cross-sections from first-principles PCAC + chiral perturbation theory.

4. **Surveys mediator detection feasibility** for a secluded MeV-scale
   mediator: cross-section magnitude AND velocity slope against
   stellar cooling, BBN ΔN_eff, beam dumps, fifth-force, and direct-detection
   evading-everything bounds.

---

## Headline result

**σ/m ≈ 1–3 cm²/g at galactic velocity scales** (V_REF = 100 km/s), with
velocity index **a ≈ 0.6–1.4** (σ/m decreases with velocity, as expected
for Yukawa-like mediators at MeV scale).

| Quantity | Value | Source |
|---|---|---|
| Joint posterior σ/m (5 channels, real KiSS-SIDM) | 1.4–1.7 cm²/g | T21 (v0.3-prelim-D5) |
| Velocity index a | 0.6–1.4 (data prefers +0.94) | T39 Tier-3 marginalization |
| Mediator mass m_φ | MeV-scale (m_φ ≪ m_χ) | T41 joint fit |
| Mediator coupling ε to SM | 10⁻⁵⁰ to 10⁻⁵³ (≪ all bounds) | T42 lab exclusions |
| LZ σ_SI | ~2×10⁻¹¹⁸ cm² (below neutrino floor by 10⁴⁶) | T62 LZ direct-detection |
| Composite dark-ρ σ/m | 1.36 cm²/g (within 13% of joint posterior) | T54 PCAC + KSFR |
| 6-channel systematic budget | 0.4–0.5 dex (publication-grade) | FINDINGS.md §S.7 |
| Cross-validation vs Drobczyk 2025 | σ/m within 30%; both predict mediator invisible to direct detection | T68 + [plot](v0.3-prelim/plots/Cross_Validation_T54_vs_Drobczyk_v2_2026-08-13.png) |

The mediator is **naturally below all direct-detection bounds** by construction: ε ~ 10⁻⁵⁰ is 30+ orders of magnitude below stellar cooling bounds and ~10⁷² times below the LZ WS2024 limit (2.2×10⁻⁴⁸ cm² at 43 GeV). The published LZ result was used for the comparison. This is not a failure of detection — it is a **prediction** of the secluded-WIMP framework (Pospelov, Ritz, Voloshin 2008) that the data supports: SIDM cross-section is consistent with multi-channel observational constraints, **conditional on a prior that includes the SM-decoupled regime**. With the Roberts et al. 2024 narrow default prior (ε ~ 10⁻⁴), the same data would exclude SIDM; the resolution is therefore prior-dependent, as documented in T39.

The composite-DM extension (T56–T63) shows that the dark-ρ meson mass
from PCAC + KSFR gives a σ/m within 13% of the joint posterior — the
strongest single result of the entire analysis. Velocity slope tension
remains (a ≈ 2.24 from dark-ρ vs a ≈ 0.94 data preference) and is
documented as a real, future-work item rather than papered over.

---

## Repo layout

```
sidm-composite-dm-mediator/
├── README.md                              ← you are here
├── CHANGELOG.md                           ← per-round history (D1 → D15-CORRECTED3)
├── CITATION.cff                           ← GitHub-native citation metadata
├── CONTRIBUTING.md                        ← how to contribute (branching, tags, sync)
├── LICENSE                                ← MIT
├── PLAN_v0.1.md                           ← original v0.1 plan (kept for history)
├── VERSION                                ← 0.3-prelim
├── requirements.txt                       ← pinned numpy 2.4.6, scipy 1.18.0, dynesty 3.0.0
│
├── docs/                                  ← top-level documentation
│   ├── DATA_SOURCES.md                     ← single authoritative list of all data + citations
│   ├── MATHEMATICS.md                      ← mathematical appendix (formulas, derivations)
│   ├── TUTORIAL.md                         ← end-to-end tutorial (fresh-checkout → reproduce T21)
│   ├── FINDINGS.md (→ v0.3-prelim/docs/)   ← full results synthesis
│   ├── REVIEWER_AUDIT_R2.md                ← audit trail from the R2 external review
│   └── findings_2026_SIDM_papers.md        ← 2026 SIDM literature context (Yang+ 2024, Yang+ 2026)
│
├── tests/                                 ← top-level test files
├── v0.1-prelim/                           ← v0.1 work (SPARC single-galaxy + joint fits)
│   ├── code/                              ← 15 Python modules
│   ├── data/                              ← SPARC external data tables (committed for reproducibility)
│   ├── data/results/                      ← JSON result files
│   ├── docs/                              ← v0.1-specific docs
│   └── tests/                             ← v0.1-specific tests
├── v0.2-prelim/                           ← v0.2 work (intermediate, 4 .py)
└── v0.3-prelim/                           ← v0.3 work — main bulk of the analysis
    ├── code/                              ← 133 Python modules (T1–T76)
    ├── data/                              ← 958 result JSONs + LZ-2024 ingested data
    ├── data/external_data/lz_2024/        ← ingested LZ WS2024 posterior (HEPData sourced)
    ├── docs/                              ← MEDIATOR_DETECTION_SYNTHESIS_v{1..12}, FINDINGS.md
    ├── plots/                             ← Cross-validation + publication plots
    └── tests/                             ← 39 v0.3-specific test files
```

The `outputs/` directory exists locally but is gitignored — it holds 113 MB
of Telegram-shipped PDFs and ZIPs from each release round (D2 through
D15-CORRECTED3), plus the scaffolding `build_*.py` scripts. These are
reproducible from `v0.*-prelim/code/` on demand.

---

## Quick start (5 minutes, reproduce the headline)

```bash
# 1. Clone
git clone https://github.com/chenhk1113-HK/sidm-composite-dm-mediator
cd sidm-composite-dm-mediator

# 2. Set up the Python environment (matches the v0.3-prelim pinned versions)
python -m venv .venv
source .venv/bin/activate         # bash/zsh; or .venv\Scripts\activate on Windows
pip install -r requirements.txt

# 3. (Optional) Install Julia 1.11.5 + KiSS-SIDM for the gravothermal penalty
juliaup add 1.11.5 && juliaup default 1.11.5
julia +1.11.5 -e 'using Pkg; Pkg.activate("KiSS-SIDM"); Pkg.instantiate()'

# 4. Run the test suite (290+ tests, expect ~0 failures)
pytest tests/ v0.3-prelim/tests/ v0.1-prelim/tests/

# 5. Reproduce the headline — T21 single-component SIDM with real KiSS-SIDM
cd v0.3-prelim/code
python t21_real_kiss_sidm_5channel_joint_fit.py
# Expect: σ/m ≈ 1.4–1.7 cm²/g at MAP
```

For the full walkthrough see [`docs/TUTORIAL.md`](docs/TUTORIAL.md).
For the math behind the fits see [`docs/MATHEMATICS.md`](docs/MATHEMATICS.md).
For the per-round history see [`CHANGELOG.md`](CHANGELOG.md).

---

## What's in each version

| Version | Scope | Headline |
|---|---|---|
| **v0.1-prelim** | SPARC single-galaxy + joint fits (15 modules) | σ/m posterior from rotation curves alone |
| **v0.2-prelim** | Intermediate (4 modules) | Adds dSph channel scaffolding |
| **v0.3-prelim** | Main work — D1 through D15-CORRECTED3 (133 modules, 39 tests) | Joint σ/m ~ 1.4–1.7 cm²/g with KiSS-SIDM gravothermal anchor; Tier-3 marginalization; Mediator Detection workstream (T40–T76) |
| **Mediator_Detection v1–v12** | Mediator detection feasibility (within v0.3-prelim/code/) | σ/m ~ 1 cm²/g at MeV-scale m_φ, mediator invisible to all direct-detection |

---

## Methodology

The pipeline is built on the **WIMpy Bayesian methodology** (dynesty nested
sampling + BIC + Bayes factors + mock-data validation), adapted from
dark-energy model comparison to dark-matter microphysics. Key pieces:

- **dynesty 3.0.0** for nested sampling posteriors
- **KiSS-SIDM** (Gurian & May 2025, PRL 135, 221001) for the gravothermal
  collapse penalty — replaces over-strong placeholder fluid approximation
- **Real published likelihoods** for LZ WS2024 (arXiv:2410.17036) and Fermi-LAT
  14-year dSph stacking (McDaniel et al. 2024) — replaces Gaussian proxies
- **Welch t-test** for null-result verification across rounds
- **PCAC + KSFR** for first-principles composite-DM mass predictions
- **Conventional Bayesian model comparison** for one-component vs two-component
  vs composite-DM evidence weights

Total: **~316 tests** across the three versions (`tests/` + `v0.*/tests/`).

---

## What this repo is NOT claiming

Honest scope, per the 2026-08-13 reviewer audit:

- **Not a "first-time" result on secluded WIMP.** The framework is from
  Pospelov, Ritz, Voloshin (2008). What's new here is the joint
  demonstration that mediator coupling marginalization reconciles the
  catastrophic LZ + Fermi + SIDM tension.
- **Not a finished velocity-slope story.** Data prefers a ≈ 0.94; the
  composite-DM dark-ρ gives a ≈ 2.24. This 1.3σ tension is real and
  documented as future work, not papered over.
- **Not paper-grade posteriors for LZ/Fermi channels yet.** The Gaussian
  proxies were replaced with real published curves in T30/T32, but the
  raw posterior chains (recommended in the R2 review) are deferred to
  v0.4-prelim. Headline σ/m is robust to the Gaussian-proxy vs
  posterior choice (T28 finding: Δ < 0.01 dex).
- **Not a full KiSS-SIDM dwarf-galaxy run.** Dwarf-mass (10⁷–10⁸ M_sun)
  KiSS-SIDM at N=10⁴ fails (T31, T38b); the canonical 10⁹ M_sun halo
  penalty is used as an upper bound on dwarf-mass collapse. The N=2×10⁶
  paper-scale run is launched in D14 as a background process for
  future sessions to pick up.

See `v0.3-prelim/docs/MEDIATOR_DETECTION_SYNTHESIS_v12.md` for the
honest assessment of every reviewer recommendation, and
`docs/REVIEWER_AUDIT_R2.md` for the original audit trail.

---

## Relationship to other projects

| Project | Path | Relationship |
|---|---|---|
| WIMpy (cosmology) | `C:\Users\lamkuenai\projects\wimpy\` | Sister project — shares Bayesian methodology |
| FUSE MAST-U | `C:\Users\lamkuenai\projects\fuse-mast-u-patch-loop\` | Unrelated (fusion, not cosmology) |
| FUSE sandbox | `C:\Users\lamkuenai\projects\fuse-sandbox-nt\` | Unrelated (fusion active repo) |

Methodology reuse from WIMpy is explicit (see `CONTRIBUTING.md` and
`docs/TUTORIAL.md` § "Methodology reuse"). The Python venv is shared
(`/home/lamkuenai/wimpy/bin/python` on WSL).

---

## Citation

See [`CITATION.cff`](CITATION.cff) for the GitHub-native citation metadata.
See [`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md) for the full list of
external data sources used and how to cite them in derivative work.

Quick bibtex for citing this repo:

```bibtex
@software{lam_sidm_composite_dm_mediator_2026,
  author = {Lam, K.},
  title = {sidm-composite-dm-mediator},
  version = {0.3-prelim-D15-CORRECTED3},
  year = {2026},
  month = {8},
  url = {https://github.com/chenhk1113-HK/sidm-composite-dm-mediator},
  license = {MIT}
}
```

For citing the underlying physics, see [`CITATION.cff`](../CITATION.cff)
(Pospelov 2008, Kaplinghat 2014, Gurian & May 2025, Horigome 2025,
Yang 2026, Di Mauro 2025, Chakraborti 2025).

---

## License

MIT — see [`LICENSE`](LICENSE).