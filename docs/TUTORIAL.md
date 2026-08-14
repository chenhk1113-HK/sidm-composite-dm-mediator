# Tutorial — dm-sidm-pipeline v0.3-prelim

**Purpose:** End-to-end guide for running the SIDM cross-section constraint
pipeline from a fresh checkout. This is the T3.6 deliverable from the
Full Codebase R2 review.

**Audience:** A new developer or collaborator who needs to reproduce the
D5/D6/D7 results or run new fits.

**Last updated:** 2026-08-11 (v0.3-prelim-D7)

---

## Quick Start (5 minutes)

```bash
# 1. Clone the repository
git clone <repo_url> dm-sidm-pipeline
cd dm-sidm-pipeline

# 2. Set up the Python environment (pinned to numpy 2.4.6 etc.)
python -m venv wimpy
source wimpy/bin/activate
pip install -r requirements.txt

# 3. Run the test suite (should show 240+ tests passing)
pytest tests/ v0.3-prelim/tests/

# 4. Reproduce the headline: T21 single-component SIDM with real KISS-SIDM
cd v0.3-prelim/code
python t21_real_kiss_sidm_gravothermal.py
# Output: v0.3-prelim/data/results/t21_real_kiss_sidm_gravothermal.json
```

**Expected runtime:** T21 takes ~10 seconds on a modern laptop.

---

## What's Where

```
dm-sidm-pipeline/
├── README.md                        # Project status + headline
├── CHANGELOG.md                     # Version history (D, D2, D3, ...)
├── requirements.txt                 # Pinned Python deps (numpy 2.4.6, ...)
├── docs/
│   ├── FINDINGS.md                  # Scientific findings (D5, D6, D7)
│   ├── MATHEMATICS.md               # Math appendix (D8)
│   ├── REVIEWER_AUDIT_R2.md         # Audit of R2 review
│   └── TUTORIAL.md                  # This file
├── v0.1-prelim/code/                # Halo profiles, SPARC loader (used by all)
├── v0.2-prelim/code/                # SPARC rotation curve fits (T4)
├── v0.3-prelim/
│   ├── code/                        # T-series fits (T8, T17, T19-T29)
│   ├── tests/                       # Tests for v0.3 code
│   └── data/results/                # Output JSON files
├── tests/                           # Cross-version tests
└── outputs/                         # PDF + ZIP delivery artifacts
    ├── dm-sidm-pipeline_v0.3-D7_CODEBASE_WITH_README.pdf
    └── dm-sidm-pipeline_v0.3-D7_SOURCE_BUNDLE.zip
```

---

## Headline Fits (reproduce D5 results)

### Single-component SIDM (T21)

```bash
cd v0.3-prelim/code
python t21_real_kiss_sidm_gravothermal.py
```

**Input:** `data/results/real_kiss_sidm_aggregated.json` (4781 KISS-SIDM snapshots)

**Output:** `data/results/t21_real_kiss_sidm_gravothermal.json`

**Headline:** MAP log σ/m = 0.236 → σ/m = **1.72 cm²/g** at galactic scale (with IMFP correction).

### Two-component SIDM (T22)

```bash
cd v0.3-prelim/code
python t22_real_kiss_sidm_two_comp.py
```

**Headline:** 2-comp SIDM NOT preferred over 1-comp; Bayes factor Δ log Z = +0.48 (was +0.57 in placeholder T19).

### T19/T20 with placeholder gravothermal (for comparison)

```bash
python t19_yang2026_fit.py          # T19 with placeholder
python t20_two_comp_kiss_sidm_fit.py  # T20 with placeholder
```

These give the "what if we still used the placeholder" baselines.

---

## Systematics Tests (D6, D7)

### T24: Likelihood-width sensitivity (no KISS-SIDM)

```bash
cd v0.3-prelim/code
python t24_likelihood_width_sensitivity.py
```

**Headline:** widening Gaussian widths by 2x shifts MAP σ/m by **factor of 10** (Δ log Z = +12.5). This is the worst case (no gravothermal anchor).

### T25: c_vir marginalization

```bash
python t25_cvir_marginalization.py
```

**Headline:** marginalizing over c_vir scatter shifts MAP by 0.19 dex (MINOR). c_vir is not a major source of systematic error.

### T26: T21 width sensitivity (with KISS-SIDM)

```bash
python t26_t21_width_sensitivity.py
```

**Headline:** KISS-SIDM dampens width sensitivity by **5×** (Δ log σ/m = +0.198 vs T24's -1.006). The gravothermal penalty is doing real physics work.

### T27: Multi-resolution KISS-SIDM

```bash
python t27_multiresolution_kiss_sidm.py
```

**Headline:** r_core/r_s **converged** at N=1e4 (identical to N=1e5 to 4 decimals). No need for paper's N=2e6 to validate qualitative behavior.

### T28: Published-style non-Gaussian dSph

```bash
python t28_published_style_dsph.py
```

**Headline:** MAP σ/m **unchanged** (Δ < 0.01 dex) when replacing Gaussian dSph placeholder with non-Gaussian published-style posterior. The publication-readiness work is to refine log Z, not relocate the headline.

### T29: β_seg as fitted free parameter

```bash
python t29_beta_seg_fitted.py
```

**Headline:** β_seg fitted MAP = **0.899** (NOT the hardcoded 0.25). The Bayes factor is unchanged (Δ log Z ≈ 0), but absolute σ1, σ2 differ.

---

## Running the Test Suite

```bash
# All tests
pytest tests/ v0.3-prelim/tests/

# Just the unit conversion tests (D6 Tier 2.1)
pytest v0.3-prelim/tests/test_unit_conversion.py

# Just the systematics tests (D6/D7)
pytest v0.3-prelim/tests/test_t24_t25_systematics.py
pytest v0.3-prelim/tests/test_t26_t27_t28_systematics.py
pytest v0.3-prelim/tests/test_t29_beta_seg.py

# Just the split-brain regression tests (D6 audit fix)
pytest v0.3-prelim/tests/test_config_split_brain.py
```

**Expected:** 240 passed, 1 skipped (the Windows-only test) in WSL Python.

---

## Working with the Real KISS-SIDM Data

The D5+ results use real KiSS-SIDM simulation outputs. If you want to re-run the KISS-SIDM simulation itself (e.g., for a different halo mass or cross-section):

### Prerequisites
1. Julia 1.11.5 (NOT 1.12.6 — incompatible with KiSS-SIDM)
   ```bash
   juliaup add 1.11.5
   juliaup default 1.11.5
   ```
2. KiSS-SIDM repo at `~/KiSS-SIDM/`
   ```bash
   git clone https://gitlab.com/Socob/KiSS-SIDM.git ~/KiSS-SIDM
   cd ~/KiSS-SIDM
   julia +1.11.5 -e 'using Pkg; Pkg.instantiate()'  # ~6 min, 348 packages
   ```

### Run a new simulation

```python
# From WSL Python:
from kiss_sidm_julia_bridge import run_canonical_kiSS_sidm

result = run_canonical_kiSS_sidm(
    N=10000,                    # particles
    t_end_Gyr=10.0,             # simulation time
    sigma_m_cm2_per_g=50.0,     # cross-section
    rho_s_Msun_per_kpc3=2.73e7, # NFW scale density
    r_s_kpc=1.18,               # NFW scale radius
    seed=42,
    snapshot_count=20,
)
print(result)
# Output: aggregated JLD2 snapshots in /tmp/kiss_sidm_output/
# Plus /tmp cleanup happens automatically (D6 T1.5 fix)
```

Then convert snapshots to JSON:
```python
from kiss_sidm_julia_reader import aggregate_kiss_snapshots
aggregate_kiss_snapshots(
    snap_dir="/tmp/kiss_sidm_output",
    out_path="v0.3-prelim/data/results/my_new_kiss_run.json",
)
```

Then re-run T21 with the new data (edit `t21_real_kiss_sidm_gravothermal.py:_REAL_KISS_PATH`).

---

## Common Pitfalls

### 1. Running scripts from the wrong directory

All T-series scripts use absolute paths via `config.RESULTS_DIR_V03`. If you cd into `v0.3-prelim/code/` directly, it should work. If you run from elsewhere, set:
```bash
export DM_SIDM_PROJECT_ROOT=/c/Users/lamkuenai/projects/dm-sidm-pipeline
```

### 2. config.py not found

If `from config import RESULTS_DIR_V03` fails, the config.py isn't on your Python path. The Windows-side copy of config.py lives at `v0.3-prelim/code/config.py`. If running from a fresh checkout, copy it from WSL side or check the audit log.

### 3. Julia version mismatch

If you have Julia 1.12.6 installed, KiSS-SIDM will fail to instantiate. **Use 1.11.5 explicitly:**
```bash
juliaup add 1.11.5
julia +1.11.5 ...
```

### 4. dynesty vs emcee

This pipeline uses **dynesty** (nested sampling) throughout, NOT emcee (MCMC). The headline Bayes factors are dynesty log Z values. Do not interpret them as MCMC posteriors.

### 5. KISS-SIDM N=2e6 unavailable

The paper uses N=2e6 particles which would take hours per run. Our results use N=500–N=1e5. The gravothermal penalty shape is converged at N=1e4 (T27 finding), so this is acceptable for the qualitative conclusions.

---

## Where to Read the Results

| Result file | What it contains |
|---|---|
| `t21_real_kiss_sidm_gravothermal.json` | Headline single-comp σ/m = 1.4-1.7 cm²/g |
| `t22_real_kiss_sidm_two_comp.json` | 2-comp vs 1-comp BF = +0.48 (NOT preferred) |
| `t23_real_kiss_sidm_two_comp_imfp.json` | IMFP correction effect = -0.04 (essentially zero) |
| `t9_prior_variation.json` | Prior sensitivity (MAP σ/m varies 0.77 dex) |
| `t24_likelihood_width_sensitivity.json` | Width scan (MAJOR shift) |
| `t25_cvir_marginalization.json` | c_vir scan (MINOR shift) |
| `t26_t21_width_sensitivity.json` | T21 width scan with KISS (5× damped) |
| `t27_multiresolution_kiss_sidm.json` | N=1e4 vs N=1e5 (converged) |
| `t28_published_style_dsph.json` | Non-Gaussian dSph (MAP unchanged) |
| `t29_beta_seg_fitted.json` | β_seg fitted (data prefers 0.9, not 0.25) |
| `real_kiss_sidm_aggregated.json` | KISS-SIDM 4781 snapshots (raw data) |
| `kiss_sidm_canonical_simulation.json` | N=1e4 canonical sim |
| `kiss_sidm_canonical_simulation_N1e5.json` | N=1e5 canonical sim (T27) |

---

## Citation

If you use this pipeline, please cite:
- **KiSS-SIDM**: Gurian & May 2025, arXiv:2505.15903v2
- **Two-component SIDM**: Yang+ 2026, arXiv:2506.14898v3
- **SASHIMI**: Horigome+ 2025, arXiv:2403.16633

---

## Getting Help

If you encounter issues:
1. Check this tutorial's "Common Pitfalls" section
2. Read `docs/MATHEMATICS.md` for the underlying formulas
3. Read `docs/FINDINGS.md` for the scientific context
4. Read `docs/REVIEWER_AUDIT_R2.md` for known caveats from the R2 review

The T-series scripts have inline docstrings explaining each step.