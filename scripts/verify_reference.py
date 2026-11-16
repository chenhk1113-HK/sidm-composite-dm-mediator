"""Verify reference data integrity after compression."""
import sys
import numpy as np
from pathlib import Path

# Migrated 2026-11-16 out of gitignored outputs/ into scripts/ (CG-16 live scope, so no host
# absolute path may appear here). Paths resolve from the repository root instead.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths  # noqa: E402  (REPO_ROOT honours DM_SIDM_PROJECT_ROOT)

ROOT = paths.REPO_ROOT
REF_DIR = ROOT / "data" / "reference"
SRC = ROOT / "v0.3-prelim" / "data" / "results"

# 1. SPARC grid: float16 overflow check
print("=== SPARC grid integrity (float16 overflow check) ===")
d_ref = np.load(REF_DIR / "sparc_hierarchical_grid_reference.npz", allow_pickle=True)
d_src = np.load(SRC / "sparc_hierarchical_grid.npz", allow_pickle=True)

logL_src = d_src["logL_per_galaxy"]
logL_ref = d_ref["logL_per_galaxy"]
print(f"  src shape={logL_src.shape}, dtype={logL_src.dtype}")
print(f"  ref shape={logL_ref.shape}, dtype={logL_ref.dtype}")
print(f"  src min={logL_src.min():.2f}, max={logL_src.max():.2f}")
print(f"  ref min={logL_ref.min():.2f}, max={logL_ref.max():.2f}")
# Float16 range is roughly [-65504, 65504]
overflow_cells_src = np.sum((logL_src < -65504) | (logL_src > 65504))
print(f"  src cells outside float16 range: {overflow_cells_src} / {logL_src.size}")
if overflow_cells_src > 0:
    print(f"  WARNING: {overflow_cells_src} cells would be clipped by float16")

# Check that useful values (log L > -1000) round-trip OK
useful_mask = logL_src > -1000
useful_max_diff = np.max(np.abs(logL_src[useful_mask] - logL_ref[useful_mask].astype(np.float32)))
print(f"  max abs diff on useful cells (logL > -1000): {useful_max_diff:.4f}")

# 2. Sample thinning sanity
print("\n=== Thinned samples sanity ===")
for name in ["t8_v03_posterior_samples", "t17_kiss_sidm_corrected_samples",
             "t18_two_component_samples"]:
    src = np.load(SRC / f"{name}.npz", allow_pickle=True)
    ref = np.load(REF_DIR / f"{name}_reference.npz", allow_pickle=True)
    for k in src.keys():
        s, r = src[k], ref[k]
        if s.dtype.kind == 'f':
            # check mean preserved within tolerance (weighted samples)
            if k in ("weights",):
                continue
            mean_diff = abs(float(s.mean()) - float(r.mean()))
            max_diff = float(np.max(np.abs(s[:len(r)] - r.astype(s.dtype)))) if s.shape[0] >= r.shape[0] else 0.0
            print(f"  {name}/{k}: src n={len(s)}, ref n={len(r)}, "
                  f"mean_src={float(s.mean()):.4f}, mean_ref={float(r.mean()):.4f}, diff={mean_diff:.4f}")
        else:
            print(f"  {name}/{k}: src n={len(s)}, ref n={len(r)}, dtype={s.dtype}")
