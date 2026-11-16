"""One-off script: peek at NPZ sample file structures."""
import numpy as np
from pathlib import Path

WSL_RESULTS = Path("/home/lamkuenai/sidm-composite-dm-mediator/v0.3-prelim/data/results")

for fname in [
    "t8_v03_posterior_samples.npz",
    "t17_kiss_sidm_corrected_samples.npz",
    "t18_two_component_samples.npz",
    "sparc_hierarchical_grid.npz",
]:
    p = WSL_RESULTS / fname
    if not p.exists():
        print(f"  MISSING: {fname}")
        continue
    d = np.load(p, allow_pickle=True)
    print(f"\n=== {fname} ({p.stat().st_size:,} bytes) ===")
    print(f"  keys: {list(d.keys())}")
    for k in d.keys():
        a = d[k]
        shape = a.shape if hasattr(a, "shape") else type(a).__name__
        dtype = a.dtype if hasattr(a, "dtype") else None
        print(f"    {k}: shape={shape}, dtype={dtype}")
