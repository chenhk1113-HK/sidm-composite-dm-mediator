# data/reference/ — Down-sampled posterior chains (R13 M2 fix)

**Status:** Added 2026-08-26 per R13 reviewer M2 suggestion
(`REVIEWER_AUDIT_R13.md`).

## Why this directory exists

The full posterior chain files (`.npz`) are excluded from git by
`.gitignore` (`*.npz` rule, line 47). Without downsampled reference
chains in version control, **anyone wanting to plot the headline
posteriors must re-run dynesty from scratch** (~3 min wall on WIMpy
wimpy for T41).

This directory commits **<500 KB total** of compressed reference chains
so a fresh clone can plot headline posteriors immediately.

## What's in here

| File | Source | Size | Purpose |
|---|---|---|---|
| `t8_v03_posterior_samples_reference.npz` | T8 v0.3 joint fit | 6 KB | 500-sample thinned chain of (log_sigma_m_0, a, weights) |
| `t17_kiss_sidm_corrected_samples_reference.npz` | T17 KiSS-SIDM corrected | 6 KB | 500-sample thinned chain of (log_sigma_m_0, a, weights, treatment) |
| `t18_two_component_samples_reference.npz` | T18 two-component fit | 9 KB | 500-sample thinned (samples 4-D, weights) |
| `sparc_hierarchical_grid_reference.npz` | SPARC hierarchical grid | 286 KB | logL_per_galaxy (175×50×30) compressed f32→f16 |
| `MANIFEST.json` | — | 3 KB | Compression metadata (source→ref byte counts, schemas) |
| **Total** | — | **~310 KB** | (under 500 KB target) |

## Compression strategy

| Type | Original | Reference |
|---|---|---|
| Sample chains | float64, all rows | float32, weighted-resampled to 500 rows |
| SPARC logL grid | float32 | float16 with `-65504` clamp (preserves rejection semantics) |
| String arrays | — | unchanged (treatment, galaxy_names) |

The float16 clamp matters: 322 / 262500 SPARC cells had `logL <
-65504` (chi² > 1.3 × 10⁵, utterly rejected configurations). Naive f16
cast would have made them `-inf`, losing the distinction between "very
bad fit" and "truly undefined". Clamping preserves both.

## How to use

```python
import numpy as np
from pathlib import Path

REF = Path("data/reference")
samples = np.load(REF / "t8_v03_posterior_samples_reference.npz")
log_sm = samples["log_sigma_m_0"]   # (500,)
a = samples["a"]                    # (500,)
w = samples["weights"]              # (500,) normalized
# Plot e.g. 2D posterior of (log_sigma_m_0, a)
```

For the SPARC grid:

```python
grid = np.load(REF / "sparc_hierarchical_grid_reference.npz")
logL = grid["logL_per_galaxy"]   # (175, 50, 30) f16
sigma_m_grid = grid["sigma_m_grid"]  # (50,)
a_grid = grid["a_grid"]              # (30,)
# Note: logL_per_galaxy is the per-galaxy logL NOT summed;
#       to get the joint, sum over axis 0 then take log.
```

## How to regenerate

```bash
# From a fresh clone, with WSL wimpy venv active:
python outputs/downsample_for_reference.py
```

This is idempotent — running it again produces the same files (seed=42).

## Caveats (honest)

1. **Thinning to 500 samples** reduces statistical resolution. Useful
   for quick plots; for paper-quality posteriors, re-run T41 from
   scratch (~3 min wall).
2. **Float16 SPARC logL** has ~3 decimal precision. For chi² analysis
   requiring higher precision, use the original
   `v0.3-prelim/data/results/sparc_hierarchical_grid.npz` (gitignored,
   893 KB).
3. **These are NOT the canonical joint posterior for the T41 fit.**
   T41's main posterior is `v0.3-prelim/data/results/t41_mediator_mass_joint_fit.json`
   (committed; contains weighted medians + 16/50/84 quantiles).
   The chains here are intermediate fits (T8, T17, T18) plus the SPARC
   per-galaxy grid.

## See also

- `outputs/downsample_for_reference.py` — the generator script
- `outputs/verify_reference.py` — integrity check script
- `tests/test_reference_chains.py` — 16-test pytest suite
- `v0.3-prelim/docs/REVIEWER_AUDIT_R13.md` — original M2 deferral
- `MODEL_ASSUMPTIONS_AND_LIMITATIONS.md` §8 — why these aren't in `outputs/`
