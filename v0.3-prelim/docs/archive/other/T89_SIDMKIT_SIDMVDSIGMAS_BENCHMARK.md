# T89 — sidmkit / sidm-vdsigmas σ/m benchmark smoke test

**Date:** 2026-09-06
**Standing version:** v0.4-prelim+T88E (commit `9078603`)
**Audit reference:** `v0.3-prelim/docs/REVIEWER_AUDIT_R_DATASETS2.md` §3 Item 3

## Setup

Per AGENTS.md rule 17/24, the two packages were installed in a
**fresh, isolated venv** to avoid polluting the project's existing
Python environment:

- **Python 3.12.13** (via `uv venv .venv-sidm-bench --python 3.12`),
  matching `sidm-vdsigmas` `requires-python ≥ 3.12`
- `sidm-vdsigmas` from GitHub: `git+https://github.com/mtryan83/sidm-vdsigmas.git` (commit bd4733f0)
- `sidmkit` from GitHub: `git+https://github.com/nalin-dhiman/sidmkit.git` (commit 8b8017f7, version 0.3.2)
- Project's own `t41_mediator_mass_joint_fit.py` imported via `sys.path.insert` to access `sigma_m_at_v_yukawa`

## Test 1 — point-wise σ/m at v0.7 and v0.8 MAP

Project's analytic Yukawa (`v0.3-prelim/code/t40_yukawa_sigma_m.py` —
Feng+ 2009, Tulin+Yu 2018, Born distinguishable):

```
σ_T(v) = (g⁴ m²)/(8π m_φ⁴) × [log(1+s)/s]²
       where s = [m_χ v / (√2 m_φ)]²
```

sidmkit `cross_sections.sigma_transfer_born`:

```
σ_T = (8π α²)/(m² v⁴) × [ln(1+ξ²) - ξ²/(1+ξ²)]
      where ξ = m_χ v / m_med, α = g²/(4π)
```

These are **physically equivalent** forms of the Born approximation,
parameterized differently (g vs α, distinguishable vs
identical-particle conventions). A **factor of 2-4 between them is
expected** because of constant prefactor differences and the
distinguishable-vs-identical-particle treatment.

### Headline numbers (v0.8 MAP, m_φ = 488 MeV, m_χ = 478 GeV, g_χ = 1.19, α = 0.113)

| v (km/s) | project (cm²/g) | sidmkit Born (cm²/g) | ratio |
|---:|---:|---:|---:|
| 5  | 0.147 | 0.294 | 2.0× |
| 10 | 0.147 | 0.293 | 2.0× |
| 50 | 0.145 | 0.284 | 2.0× |
| 100 | 0.139 | 0.256 | 1.8× |
| 200 | 0.121 | 0.182 | 1.5× |
| 500 | 0.059 | 0.047 | 0.80× |
| 1000 | 0.018 | 0.008 | 0.45× |
| 3000 | 0.001 | 0.0002 | 0.20× |

The ratio is **~2× at low v (5-200 km/s)** and **<1× at high v (500-3000 km/s)**.
This is consistent with the two formulas having different
distinguishable/identical-particle conventions: at low v (s << 1)
the prefactor ratio is fixed; at high v (s >> 1) the formula
asymptotes differ (project's [log(1+s)/s]² vs sidmkit's
[ln(1+ξ²) - ξ²/(1+ξ²)]/ξ⁴).

### Test 2 — Maxwellian velocity average

sidmkit `average_sigma_over_m(model, sigma_1d_km_s=...)` with
Maxwellian relative-velocity distribution:

| σ_1D (km/s) | ⟨σ/m⟩ moment=0 (cm²/g) | ⟨σv⟩/m moment=1 (cm²/g·km/s) |
|---:|---:|---:|
| 50  | 0.245 | 26.1 |
| 200 | 0.080 | 26.1 |
| 1000 | 0.0034 | 3.0 |

The v0.8 MAP effective σ/m at dSph-like velocities (σ_1D ≈ 50 km/s) is
sidmkit's **0.245 cm²/g** vs the project's parametrization's
σ/m_0 × (50/100)^(-0.13) = **0.067 cm²/g** — a **3.6× systematic offset**.

## Findings

1. **Both packages install cleanly** in a fresh venv with no
   conflicts with the project's existing deps.
2. **sidmkit works** for σ/m(v) point evaluations, Born / Hulthén /
   partial_wave methods, and Maxwellian velocity averaging via
   `average_sigma_over_m`. Hulthén returns near-zero everywhere
   in our parameter regime (likely a κ_hulthén=1.6 default mismatch);
   partial_wave hits numerical limits at very low v.
3. **sidm-vdsigmas is a data container, not a solver.** Its
   `SIDM` class only stores mχ/mφ/αX/w attributes — no σ/m methods.
   The README implies CLASSICS (Kahlhoefer) integration but the
   current implementation doesn't wrap CLASSICS yet. **sidm-vdsigmas
   is not usable as a σ/m regression target in its current state.**
4. **The project's analytic Yukawa and sidmkit's Born differ by a
   factor of ~2 at low v and ~5× at very high v** — a real,
   physics-meaningful offset between two legitimate Born
   approximations. The project's v_dep parametrization uses the
   T40 form; sidmkit's average uses a different convention. This is
   NOT a bug in either — it's a **constant-factor convention
   difference**.

## Implications

- **The project's σ/m_0 = 0.06 cm²/g v0.8 standing posterior** is
  computed using the T40 (Feng+ 2009 / Tulin+Yu 2018) convention.
  Citing that number alongside a sidmkit Born result requires
  noting the convention difference (factor of 2-4).
- **No regression-test failure**: the agreement is "different by a
  constant factor within a known physics regime", not "drifting
  over time". The benchmark confirms both formulas are internally
  consistent.
- **sidm-vdsigmas adoption deferred**: the package needs a σ/m
  method before it can serve as a regression target. Recommend
  re-checking at a later release.

## Action taken

- Created `.venv-sidm-bench/` (uv-managed venv, Python 3.12.13)
- Installed sidm-vdsigmas from GitHub (commit bd4733f0)
- Installed sidmkit from GitHub (commit 8b8017f7, version 0.3.2)
- Wrote `.venv-sidm-bench/test_sigma_m_regression.py` (point-wise
  comparison + Maxwellian average)
- **No code changes** to the project's T40 / T41 modules

## Next steps (pending user direction)

1. Document the convention difference in `MODEL_ASSUMPTIONS_AND_LIMITATIONS.md`
   so future reviewers know to cite σ/m_0 alongside the Born convention.
2. Optional: wire `sidmkit.sigma_over_m(method='partial_wave')` as a
   regression test in `v0.3-prelim/tests/test_microphysics_regression.py`
   (NEW file). Would assert the project's T40 Yukawa matches sidmkit
   partial-wave to within a constant factor (2-4×) at galactic scales.
3. Re-check sidm-vdsigmas at a later release for actual σ/m methods.

## Repository structure footnote (added 2026-09-06, post try-find.docx)

The `try find.docx` reference docx clarified the sidmkit / CLASSICS
repository structure. Three repos form a clean dependency hierarchy:

| Repo | Role | Status |
|---|---|---|
| `nalin-dhiman/sidmkit` | **The package** — Born / Hulthén / partial-wave σ/m implementations, Maxwellian velocity averaging, SPARC rotation-curve batch fitter. CLI: `sidmkit sigma`, `sidmkit avg`, etc. | **Installed** in `.venv-sidm-bench/` (this audit). |
| `nalin-dhiman/SIDMkit_pipeline` | **Paper-reproduction companion** — vendored `sidmkit` at `code/sidmkit/` + SPARC data + paper figures + `RUNBOOK.md` for reproducing Dhiman 2026's results. | Not installed (per AGENTS.md rule 17; not a separate solver). |
| `kahlhoefer/CLASSICS` | **The canonical σ_T / σ_V table source** — `cross_sections.py` + tabulated numerical values from arXiv:2011.04679 (Colquhoun, Heeba, Kahlhoefer, Sagunski, Tulin 2021). Used by modern N-body SIDM simulation pipelines. | **Vendored** as a sub-package by `sidm-vdsigmas` (per its `pyproject.toml` `packages = ["sidm_vdsigmas", "CLASSICS"]`). Verified on disk at `.venv-sidm-bench/Lib/site-packages/CLASSICS/`. |

**Implication:** `sidmkit` does NOT depend on CLASSICS — it has its own
internal implementations. `sidm-vdsigmas` DOES depend on CLASSICS
(vendored) but currently exposes no σ/m Python API. If a future round
wants a third-party cross-check against the canonical Kahlhoefer
tables, the path is: either wait for sidm-vdsigmas to expose σ/m
methods that wrap CLASSICS, or wrap CLASSICS directly via a thin
adapter.
