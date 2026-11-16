"""One-off script: downsample untracked .npz posterior files into
data/reference/ for git tracking (per R13 reviewer M2).

Source files (untracked, gitignored via *.npz rule):
  v0.3-prelim/data/results/t8_v03_posterior_samples.npz       100 KB
  v0.3-prelim/data/results/t17_kiss_sidm_corrected_samples.npz 383 KB
  v0.3-prelim/data/results/t18_two_component_samples.npz       43 KB
  v0.3-prelim/data/results/sparc_hierarchical_grid.npz        872 KB

Output target: data/reference/ (NEW dir, git-allow via .gitignore exception).
Compression strategy: float64 -> float32 where possible; thin to 500
samples by resampling per weights; cap total <500 KB.
"""
import json
import sys
import numpy as np
from pathlib import Path

# Migrated 2026-11-16 out of the gitignored outputs/ directory into scripts/, which CG-16
# defines as live scope: live-scope code may not spell a host absolute path. The repository root
# is resolved instead, so the script runs from a checkout anywhere (Windows, WSL, a CI clone).
sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths  # noqa: E402  (REPO_ROOT honours DM_SIDM_PROJECT_ROOT)

ROOT = paths.REPO_ROOT
REF_DIR = ROOT / "data" / "reference"
REF_DIR.mkdir(parents=True, exist_ok=True)

SRC = ROOT / "v0.3-prelim" / "data" / "results"

# Strategy per file:
PLAN = {
    # thin to 500 weighted samples (preserves posterior shape)
    "t8_v03_posterior_samples.npz": {"thin_n": 500, "fmt": "float32"},
    "t17_kiss_sidm_corrected_samples.npz": {"thin_n": 500, "fmt": "float32"},
    "t18_two_component_samples.npz": {"thin_n": 500, "fmt": "float32"},
    # grid: compress logL_per_galaxy from (175,50,30) f32 to (175,50,30) f16
    "sparc_hierarchical_grid.npz": {"compress_per_galaxy": "float16"},
}

def thin_samples(samples, weights, n_target):
    """Weighted resampling to n_target samples."""
    if len(samples) <= n_target:
        return samples, weights
    rng = np.random.default_rng(42)
    # Resample by weights
    p = weights / weights.sum()
    idx = rng.choice(len(samples), size=n_target, replace=False, p=p)
    return samples[idx], weights[idx]


def process_thin(src_name, n_target, fmt):
    src = SRC / src_name
    d = np.load(src, allow_pickle=True)
    out = {}
    for k in d.keys():
        a = d[k]
        if k == "weights":
            # normalize then thin
            w = a / a.sum() * len(a)
            _, w_thin = thin_samples(a.reshape(-1, 1), a, n_target)
            out[k] = w_thin.astype(fmt)
        elif a.dtype.kind == 'f':
            samples_thin, _ = thin_samples(a.reshape(-1, 1) if a.ndim == 1 else a, np.ones(len(a)), n_target)
            out[k] = samples_thin.astype(fmt)
        else:
            # string arrays (treatment, galaxy_names): keep as-is
            samples_thin, _ = thin_samples(a.reshape(-1, 1) if a.ndim == 1 else a, np.ones(len(a)), n_target)
            out[k] = samples_thin
    return out


def process_grid_compress(src_name, dtype):
    src = SRC / src_name
    d = np.load(src, allow_pickle=True)
    out = {}
    for k in d.keys():
        a = d[k]
        if k == "logL_per_galaxy":
            # Clamp to float16 range before cast to preserve inf-as-strong-rejection semantics.
            # float16 max = 65504. Cells with logL < -65504 represent chi^2 > 1.3e5
            # (i.e. utterly rejected configurations); they are NOT meaningful likelihood values,
            # but we clamp them rather than letting them silently become -inf, so downstream
            # code can still distinguish "very bad fit" from "truly undefined".
            a_clamped = np.clip(a, -65504.0, 65504.0)
            out[k] = a_clamped.astype(dtype)
        elif a.dtype.kind == 'f':
            out[k] = a.astype("float32")
        else:
            out[k] = a
    return out


print("Downsampling for data/reference/ ...")
manifest = {"files": [], "total_bytes": 0}

for src_name, plan in PLAN.items():
    src = SRC / src_name
    if not src.exists():
        print(f"  SKIP (missing): {src_name}")
        continue
    out_name = src_name.replace(".npz", "_reference.npz")
    out_path = REF_DIR / out_name
    if "thin_n" in plan:
        out = process_thin(src_name, plan["thin_n"], plan["fmt"])
    elif "compress_per_galaxy" in plan:
        out = process_grid_compress(src_name, plan["compress_per_galaxy"])
    else:
        raise ValueError(f"unknown plan for {src_name}")
    np.savez_compressed(out_path, **out)
    sz = out_path.stat().st_size
    manifest["files"].append({
        "source": f"v0.3-prelim/data/results/{src_name}",
        "reference": f"data/reference/{out_name}",
        "source_bytes": src.stat().st_size,
        "reference_bytes": sz,
        "compression_ratio": round(sz / src.stat().st_size, 3),
        "schema": {k: (list(a.shape) if hasattr(a, "shape") else str(type(a)),
                      str(a.dtype)) for k, a in out.items()},
    })
    manifest["total_bytes"] += sz
    print(f"  {src_name} -> {out_name}: {src.stat().st_size:,}B -> {sz:,}B "
          f"({sz / src.stat().st_size:.1%})")

manifest["total_kb"] = round(manifest["total_bytes"] / 1024, 1)
manifest["target_total_kb"] = 500
manifest["under_target"] = manifest["total_bytes"] < 500 * 1024

manifest_path = REF_DIR / "MANIFEST.json"
manifest_path.write_text(json.dumps(manifest, indent=2))

print(f"\nTotal: {manifest['total_kb']} KB (target < {manifest['target_total_kb']} KB)")
print(f"Under target: {manifest['under_target']}")
print(f"Manifest: {manifest_path}")
