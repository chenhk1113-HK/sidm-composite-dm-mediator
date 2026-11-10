# sidm-composite-dm-mediator

> ⚠️ **Disclaimer:** a personal project built out of curiosity, using Hermes with **MiniMax M3** as the coder and **Grok**, **Doubao**, **Qwen 3.8 Max** and other AIs as reviewers.

**Standing:** branch `wip/v19.2-F-init` (also the GitHub default branch) · record save `v19.2-F-RecordSave-2026-11-10` → commit `4098d01` · paper `v0.3-prelim/docs/PAPER_V1_DRAFT.md` · 15-layer release gate **15/15 PASS**. Round-by-round history is in [`CHANGELOG.md`](CHANGELOG.md), [`CURRENT.md`](CURRENT.md), the branch front page [`v0.3-prelim/README.md`](v0.3-prelim/README.md) and [`v0.3-prelim/docs/archive/phases/`](v0.3-prelim/docs/archive/phases/), not on this page.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![WIP Paper](https://img.shields.io/badge/wip_paper-v19.2--F--init-blueviolet)](v0.3-prelim/docs/PAPER_V1_DRAFT.md)
[![Gate](https://img.shields.io/badge/gate-15%2F15_layers_pass-green)](scripts/verify_release_gate.py)
[![Tests](https://img.shields.io/badge/tests-3643_pass%20%7C%2026%20skip%20%7C%2040%20deselect-green)](scripts/verify_release_gate.py)

**Pairing declaration (findings F26/F33):** this document quotes amplitudes in two pairings. The LIVE canonical pair is f_H = 0.7501856343179664 with σ_0 = 0.008150396851725193 cm²/g and σ_peak = 27.272481773080454 cm²/g. The ARCHIVED pair is f_H = 0.297 with σ_0 = 0.052 cm²/g and σ_peak = 174.0 cm²/g. Unless a sentence says otherwise, an amplitude quoted below is an ARCHIVED-pair raw amplitude. Both pairs give the same halo-level σ_eff = f_H² × (σ/m) = 15.348366 cm²/g at the 29.4 km/s resonance, so no effective prediction changes. Sources: scripts/constants.py, v0.3-prelim/data/results/canonical_numbers.json, v0.3-prelim/data/results/fH_pairing_registry.json.

---

## Abstract

A velocity-dependent self-interacting dark matter (SIDM) architecture — a multi-resonance σ/m(v), a two-component dark sector, and gravothermal halo evolution — tested against published observations spanning four orders of magnitude in velocity, from ultra-faint dwarfs (v ≈ 3 km/s) to galaxy clusters (v ≈ 500 km/s). Posteriors come from dynesty nested sampling with published likelihoods (LZ, Fermi-LAT, SPARC, Horigome+ 2025, DAMPE, Zhang+ 2025 large-scale structure, Euclid Q1), not Gaussian proxies.

What the project produces is a **constraint map and a no-go catalogue**, not a unified particle model. At the current best fit — the v19.2-E A.2 5-parameter differential-evolution fit under the published σ_unc convention — it clears **5 PASS / 2 MARGINAL / 1 FAIL** on the 8 published channel slots the likelihood evaluates.

The standing joint fit (T41 v0.8 rerun, nlive=2000) sits at **σ/m₀** = **0.06 cm²/g**, m_χ = **478 GeV**, m_φ = **488 MeV**, g_χ = 0.964, Bayesian evidence log Z = **−164.87 ± 0.084**, and a velocity-slope tension of **0.81σ** against the Yukawa-predicted slope — under the 1.0 threshold the project set for itself.

Two results survive every forward path that was tested (§2.6a, §9.17b). Five UV-completion routes are excluded. The attempt to derive the phenomenological σ/m(v) from a single-Yukawa UV sector **failed**: three independent numerical paths converge on the same negative verdict (v19.2-F Phase 3).

---

## Key findings

### 1. Channel coverage at the v19.2-E A.2 best fit — 5 PASS / 2 MARGINAL / 1 FAIL

Canonical tally at `v19_2_E_A2_5param_DE_best_fit`, published σ_unc convention (`v0.3-prelim/data/results/canonical_numbers.json`). The 8 slots are velocity bins drawn from published analyses, not 8 independent measurements.

| Channel | v (km/s) | Published constraint | Verdict |
|---|---|---|---|
| UFD | 3 | < 0.155 (Horigome+ 2025) | MARGINAL |
| UFD | 5 | < 0.093 (Horigome+ 2025) | PASS |
| UFD | 7 | < 0.067 (Horigome+ 2025) | PASS |
| UFD | 10 | < 0.047 (Horigome+ 2025) | PASS |
| dSph | 15 | < 0.032 (Horigome+ 2025) | PASS |
| Cloud-9 (M94 RELHIC) | 28 | > 128 floor (internal anchor, finding F21) | PASS |
| SPARC | 100 | 0.193 (Lelli+ 2016) | FAIL |
| Cluster | 500 | < 2.5×10⁻⁴ (Randall+ 2008) | MARGINAL |

### 2. Two first-class structural results

- **§2.6a — Cloud-9 vs dSph tension (v = 28 ↔ 15 km/s).** The ratio σ/m(28)/σ/m(15) that Cloud-9 demands is incompatible with the dSph ceiling at Phase-44 parameters. It is a ratio argument, so it survives multi-resonance ansätze. The framework maps this tension rather than explaining it away.
- **§9.17b — the f_H(r) trade-off.** A centre-peaked heavy-component profile (SIDM2c, e.g. f_H(0.5 r_s) = 0.03) fails Cloud-9 and SPARC at observation radii by factors ~300× and ~1900×. This is the framework's fundamental limit, and it is a parameterisation result, not this project's own N-body.

### 3. Two things deliberately NOT counted as no-gos

- **§9.17a (v = 150 km/s)** is a **tuning statement**, not a structural exclusion: one chosen peak height overshoots Sameie+ 2020 by 1.5×, and a peak in (1.11, 3.33) cm²/g satisfies both constraints.
- **§2.8 (background UV derivation)** is an **open requirement**, not another exclusion.

### 4. Five UV-completion exclusions

Magnetic dipole DM; hidden U(1) with a 10 MeV pseudo-Dirac partner; GeV-scale inelastic DM; the published best-fit p-wave resonance; and the one-mediator UV scaling argument — the least specific of the five, an exclusion at the Phase-44 baseline rather than a theorem. A two-mediator Drobczyk 2025 candidate survives at δ = 0.43% fine-tuning but does not resolve the Cloud-9 vs dSph tension.

### 5. Numbers of record

Historical, superseded (v0.7 MAP, pre-T88.E): log Z **−163.29**, m_χ 770 GeV, m_φ 453 MeV, velocity index a +0.34, tension **0.60σ**. The table below is the v0.8 MAP.

| Quantity | Value | Note |
|---|---|---|
| **σ/m₀** (joint fit, galactic scale) | **0.06 cm²/g** | T41 v0.8 MAP, nlive=2000 |
| Bayesian evidence log Z | **−164.87 ± 0.084** | v0.8 posterior |
| m_χ | **478 GeV** | posterior median 503 GeV (68% CI 338–770 GeV) |
| m_φ | **488 MeV** | posterior median 598 MeV (68% CI 472–759 MeV) |
| g_χ | 0.964 | MAP; posterior median 1.549 |
| Velocity index a | +0.132 | tension vs the Yukawa slope **0.81σ** |
| Channels | **22** | catalog count; 8 slots are what the likelihood evaluates |
| Test badge (T89-era, historical) | **677 pass, 8 skip** | live count in the verification section below |

Provenance: `v0.3-prelim/data/results/t41_mediator_mass_joint_fit_t88ce_v08_with_euclid_lensing_and_subhalo_forecast_nlive2000.json`, mirrored in `v0.3-prelim/data/results/canonical_numbers.json`. `scripts/t82_audit.py` re-checks these numbers against those artifacts on every run.

### 6. The direct-detection bottleneck

Astrophysics likes this benchmark; direct detection does not see it. LZ, XENONnT and PandaX null results push the kinetic-mixing parameter to ε ~ 10⁻³⁷ at the MAP — far below what naive dimensional analysis (10⁻³–10⁵) expects. The predicted composite-DM σ_DM-nucleon is ~10⁻¹¹⁷ cm², with a 50–80 order form-factor uncertainty band, i.e. ~71 orders below LZ sensitivity. Any future dark-photon SIDM construction has to explain why ε is that small.

### 7. The c–M anchor is reduced, not resolved

Under the Elbert+ 2015 c-tau prescription the framework puts Cloud-9 at c_200 = 6.0 against Ohana+ 2026's measured 4.0: **+0.75σ** against the Diemer+ 2019 relation and **+2.06σ** against Ohana+ 2026's own relation. An earlier "3.2σ → 0.32σ" statement subtracted across two different c–M relations and is withdrawn.

### 8. Mixed statistics, honestly disclosed

Multi-resonance wins the raw joint log-likelihood (+6.08 log-units over constant σ/m) and loses on BIC (+3.22 favouring the simpler model). The earlier Phase 44 headline of +8.10 log-units for the free joint fit is SPARC-dominated under leave-one-out (Phase 47). On rotation curves alone, Burkert wins decisively (log Z −963 vs −3300). The Bayes factor on the joint channels is moderate (log B = 2.41). The σ/m₀ MAP is stable to ±20% under a baryonic-feedback nuisance parameter up to f_fb = 0.75.

---

## Layman summary

**What was tried.** Dark matter may scatter off itself. The project writes down one concrete recipe for that — a scattering strength that changes with the speed of the colliding particles, with resonance peaks at dwarf-galaxy, disk-galaxy and cluster speeds — and asks whether a single recipe can fit every published measurement at once.

**What happened.** It fits most of them. Out of eight measured velocity bins, five agree, two are borderline, and one — the rotation curves of disk galaxies — clearly disagrees.

**What was ruled out.** Five ways of building the recipe out of known particles each fail. If this recipe is real, the dark sector is not a simple copy of the Standard Model. Trying to derive the recipe from first principles also failed: three separate calculations all said no.

**What it does NOT do.** It does not prove dark matter self-interacts. It does not offer a working particle model. It does not resolve the S8 or H0 tensions, and it does not rule out ΛCDM. It is a map of what is allowed, what is excluded, and where the model breaks.

**Why that is still worth publishing.** A constraint map with named exclusions and a documented failure tells the next person where to dig. Every number is tied to a public dataset, a seed-pinned sampler run, and a script that re-checks the documents against the code.

---

## Where to read next

| If you want | Read |
|---|---|
| 60-second status | [`CURRENT.md`](CURRENT.md) |
| One-page extract | [`EXTRACT.md`](EXTRACT.md) |
| The paper | [`v0.3-prelim/docs/PAPER_V1_DRAFT.md`](v0.3-prelim/docs/PAPER_V1_DRAFT.md) |
| Assumptions and limits before quoting any number | [`MODEL_ASSUMPTIONS_AND_LIMITATIONS.md`](MODEL_ASSUMPTIONS_AND_LIMITATIONS.md) |
| Known defects and the honesty ledger | [`docs/INTEGRITY_FINDINGS_2026-11-04.md`](docs/INTEGRITY_FINDINGS_2026-11-04.md) |
| Document map | [`docs/INDEX.md`](docs/INDEX.md) |
| Plain-language walkthrough | [`docs/LAYMAN_SUMMARY.md`](docs/LAYMAN_SUMMARY.md) |
| Round-by-round history | [`CHANGELOG.md`](CHANGELOG.md) |

---

## Quick start

```bash
git clone https://github.com/chenhk1113-HK/sidm-composite-dm-mediator.git
cd sidm-composite-dm-mediator

# Required: config.py needs this, otherwise the suite cannot find the project root.
# Use the Windows form: an MSYS path like /c/Users/... is joined naively by three
# test modules and yields C:\c\Users\... -> 3 collection errors.
export DM_SIDM_PROJECT_ROOT="$(cygpath -w "$PWD")"

python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Docs-vs-code drift audit — should print "ALL CLEAR: N/N checks passed"
python scripts/t82_audit.py

# Test suite (no --ignore flags: the gate's ignore list is empty)
pytest v0.3-prelim/tests/ -q

# The 15-layer release gate used for every record commit
python scripts/verify_release_gate.py --quick
```

The headline fit is a stored artifact, not a re-run: read `v0.3-prelim/data/results/t41_mediator_mass_joint_fit_t88ce_v08_with_euclid_lensing_and_subhalo_forecast_nlive2000.json` for log Z and the MAP. That stored run records `wall_seconds` = 751.7 s (~12.5 min). The documented nlive=2000 driver is `scripts/t76_run_nlive2000.py`, which writes T41's fixed output path; the headline file above is the renamed result plus `scripts/t88ce_postprocess.py`.

---

## Repo layout

| Path | What is in it |
|---|---|
| `v0.3-prelim/code/` | the main code — likelihoods, forward models, fits, constants |
| `v0.3-prelim/data/results/` | result JSONs; `canonical_numbers.json` is the single source of truth |
| `v0.3-prelim/tests/` | the pytest suite |
| `v0.3-prelim/docs/` | the paper, per-round reports, referee responses, archive |
| `docs/` | integrity ledger, consolidated reviews, evidence folders, literature KB |
| `scripts/` | `verify_release_gate.py`, `t82_audit.py`, `drift_guard.py`, re-derivation scripts |
| `v0.1-prelim/`, `v0.2-prelim/` | historical earlier fits, kept for provenance |
| `CURRENT.md`, `EXTRACT.md` | standing status, one-page extract |

---

## How this repo is verified

- **15-layer release gate** (`scripts/verify_release_gate.py`) runs on every record commit; its 15 layers are pytest, `audit_units.py`, `drift_guard.py`, `t82_audit.py`, `audit_claims.py`, `check_fabrication.py`, `check_breakthrough_label.py`, `audit_doc_anchors.py`, `audit_model_provenance.py`, `audit_hierarchy_chain.py`, `audit_pdf_render.py`, `triage_pdf_advisory_flags.py`, `audit_stale_strings.py`, `audit_glyph_coverage.py`, `audit_register_state.py`. Current head: **15/15 PASS**, pytest layer **3,644 passed / 25 skipped / 40 deselected**, drift audit **120/120 ALL CLEAR**.
- **Run alongside the gate:** `audit_markdown_tables.py` and `scripts/run_round13_self_check.py` (8 layers, currently 8/8 PASS) are not gate layers; the self-check runs in the GitHub `Self-check` workflow.
- **Evidence folders** carry the raw logs of each record commit, for example `docs/dual_review_5loop/evidence_CMAnchor_20261110/`.
- **GitHub Actions CI is disabled** (decision D12, 2026-11-08): it had been red since 2026-10-11 and its ignore list certified less than the local gate, whose ignore list is empty. The `Self-check` workflow still runs.
- **Standing disclosures travel with every green run:** the gate asserts its enumerated layers, not the whole document, and skipped or deselected tests prove nothing on their own.

---

## What this repo is NOT claiming

- Not a discovery. The MAP is one point in a prior box that fits multi-channel data, not a measurement.
- Not a Boltzmann-derived relic density. The mapping is a calibrated 1/⟨σv⟩.
- Not a first-principles dark-quark mass. The vector-meson mass is KSFR plus lattice-ratio calibration.
- Not a finished velocity-slope story. The data prefers a ≈ +0.94, the fit lands at +0.132, and the earlier "1.3σ tension" was a sign-flip bug, not physics.
- Not an explanation of the LZ event. The predicted count is 4.8 × 10⁻⁷³ events in 2.84 tonne-years (derivation: `v0.3-prelim/docs/archive/other/T87_LZ_FORWARD_PREDICTION.md`).

Full ledger: [`MODEL_ASSUMPTIONS_AND_LIMITATIONS.md`](MODEL_ASSUMPTIONS_AND_LIMITATIONS.md).

---

## Citation

See [`CITATION.cff`](CITATION.cff) for GitHub-native citation metadata and [`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md) for the external data sources used and how to cite them in derivative work.

```bibtex
@software{lam_sidm_composite_dm_mediator_2026,
  author = {Lam, K.},
  title = {sidm-composite-dm-mediator},
  version = {v19.2-F-RecordSave-2026-11-10},
  year = {2026},
  url = {https://github.com/chenhk1113-HK/sidm-composite-dm-mediator},
  license = {MIT}
}
```

---

## License

MIT — see [`LICENSE`](LICENSE).
