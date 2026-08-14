#!/usr/bin/env python
"""
T14 — Per-galaxy SASHIMI-SIDM fits on all SPARC galaxies (Direction A).

This is the upgraded version of T10 (per_galaxy_vdep), now using the
in-house SASHIMI-SIDM parametric forward model (sashimi_per_galaxy.py)
instead of the saturation heuristic.

For each of the ~175 SPARC galaxies, we:
    1. Load the rotation curve (r, V², σ_V²)
    2. Sample a grid of (σ/m_0, a) pairs (e.g., 20 × 10)
    3. For each pair, compute χ² against the observed V² using the
       SASHIMI-SIDM forward model
    4. Convert χ² to per-galaxy σ/m posterior via exp(-χ²/2)
    5. Aggregate the per-galaxy posteriors into a joint σ/m posterior

This is the in-house replacement for the Hayashi+ 2025 SASHIMI-SIDM
analysis (arXiv:2503.13650), which used the publicly-available code.
"""
from __future__ import annotations
import sys
import json
import time
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from sashimi_per_galaxy import load_sparc_galaxy, chi2_per_galaxy
from config import LOG_SIGMA_M_RANGE, A_RANGE


# SPARC rotmod directory
SPARC_DIR_CANDIDATES = [
    Path("/home/lamkuenai/dm-sidm-pipeline/v0.1-prelim/data/Rotmod_LTG"),
    Path("/mnt/c/Users/lamkuenai/projects/dm-sidm-pipeline/v0.1-prelim/data/Rotmod_LTG"),
    Path(r"C:\Users\lamkuenai\projects\dm-sidm-pipeline\v0.1-prelim\data\Rotmod_LTG"),
]


def find_sparc_dir() -> Path:
    for p in SPARC_DIR_CANDIDATES:
        if p.exists():
            return p
    raise FileNotFoundError(f"SPARC dir not found in any of: {SPARC_DIR_CANDIDATES}")


def estimate_halo_mass_from_rotation(V_max_kms: float, V_max_kms_err: float = 0.0) -> tuple:
    """Estimate M_vir from V_max using a rough scaling relation.

    For a halo with V_max ~ 200 km/s (MW-like), M_vir ~ 1e12 M_sun.
    Scaling: M_vir ∝ V_max³.

    Returns
    -------
    (M_vir_Msun, c_vir) where c_vir is the median concentration.
    """
    # V_max = 200 km/s → M_vir = 1e12
    M_vir = 1e12 * (V_max_kms / 200.0) ** 3
    # Concentration-mass relation (Dutton & Macciò 2014, approximate):
    # log10(c_vir) = 0.54 - 0.13 × log10(M_vir / 1e12)
    c_vir = 10 ** (0.54 - 0.13 * np.log10(M_vir / 1e12))
    return M_vir, c_vir


def fit_one_galaxy(
    rotmod_path: Path,
    sigma_0_grid: np.ndarray,
    a_grid: np.ndarray,
    w_kms: float = np.inf,
    V_max_err_kms: float = 5.0,
) -> dict:
    """Fit one SPARC galaxy with the SASHIMI-SIDM forward model.

    Parameters
    ----------
    rotmod_path : Path
        Path to the rotmod file.
    sigma_0_grid : np.ndarray
        Grid of σ/m values to test (cm²/g).
    a_grid : np.ndarray
        Grid of v-dep index a values to test.
    w_kms : float
        Velocity transition scale (km/s), default inf (v-independent).
    V_max_err_kms : float
        Uncertainty on V_max for halo mass estimation (km/s).

    Returns
    -------
    dict with:
        'name': galaxy name
        'sigma_0_map', 'a_map': MAP values
        'sigma_0_median', 'sigma_0_p16', 'sigma_0_p84': posterior summary
        'chi2_min': minimum χ²
        'n_data_points': number of data points
        'V_max_kms': estimated V_max
    """
    name = rotmod_path.stem.replace("_rotmod", "")
    r, V2, V2_err = load_sparc_galaxy(str(rotmod_path))

    # Filter to galaxies with sufficient data
    if len(r) < 5:
        return {"name": name, "skipped": "n_pts < 5"}

    # Estimate V_max from observed V²
    V_max_kms = np.sqrt(V2.max())
    M_vir, c_vir = estimate_halo_mass_from_rotation(V_max_kms)

    # Compute χ² on the grid
    chi2_grid = np.zeros((len(sigma_0_grid), len(a_grid)))
    for i, sigma_0 in enumerate(sigma_0_grid):
        for j, a in enumerate(a_grid):
            chi2_grid[i, j] = chi2_per_galaxy(
                r, V2, V2_err, M_vir, c_vir, sigma_0, w_kms,
            )

    # Per-galaxy posterior ∝ exp(-χ²/2)
    log_L_grid = -0.5 * chi2_grid
    # Marginalize over a: per-galaxy posterior on σ/m
    log_L_max = log_L_grid.max()
    L_norm = np.exp(log_L_grid - log_L_max)
    # Marginalize over a
    L_sigma = L_norm.sum(axis=1)
    # Normalize
    p_sigma = L_sigma / L_sigma.sum()

    # Posterior summary
    cdf = np.cumsum(p_sigma)
    median_idx = np.searchsorted(cdf, 0.5)
    p16_idx = np.searchsorted(cdf, 0.16)
    p84_idx = np.searchsorted(cdf, 0.84)

    i_map, j_map = np.unravel_index(np.argmax(chi2_grid), chi2_grid.shape)

    return {
        "name": name,
        "V_max_kms": V_max_kms,
        "M_vir_Msun": M_vir,
        "c_vir": c_vir,
        "n_data_points": len(r),
        "sigma_0_map": sigma_0_grid[i_map],
        "a_map": a_grid[j_map],
        "chi2_min": chi2_grid[i_map, j_map],
        "sigma_0_median": sigma_0_grid[median_idx],
        "sigma_0_p16": sigma_0_grid[p16_idx],
        "sigma_0_p84": sigma_0_grid[p84_idx],
    }


def main():
    print("=== T14: Per-galaxy SASHIMI-SIDM fits on all SPARC galaxies ===\n")

    sparc_dir = find_sparc_dir()
    print(f"SPARC dir: {sparc_dir}")
    rotmod_files = sorted(sparc_dir.glob("*_rotmod.dat"))
    print(f"Found {len(rotmod_files)} rotmod files")

    # σ/m grid: log-spaced from 0.01 to 1000 cm²/g (per peer review range)
    sigma_0_grid = np.logspace(np.log10(0.01), np.log10(1000.0), 20)
    a_grid = np.linspace(0.0, 2.0, 5)  # velocity-independent to v-dep
    print(f"σ/m grid: {len(sigma_0_grid)} values from {sigma_0_grid[0]:.3f} to {sigma_0_grid[-1]:.1f} cm²/g")
    print(f"a grid: {len(a_grid)} values from {a_grid[0]:.1f} to {a_grid[-1]:.1f}\n")

    results = []
    t0 = time.time()
    skipped = 0
    for i, rotmod_path in enumerate(rotmod_files):
        try:
            r = fit_one_galaxy(rotmod_path, sigma_0_grid, a_grid)
            if "skipped" in r:
                skipped += 1
                continue
            results.append(r)
            if (i + 1) % 20 == 0:
                elapsed = time.time() - t0
                print(f"[{i+1}/{len(rotmod_files)}] {r['name']:<20} "
                      f"σ/m MAP={r['sigma_0_map']:.2f}, a={r['a_map']:.1f}, "
                      f"χ²={r['chi2_min']:.1f}  (elapsed: {elapsed:.1f}s)")
        except Exception as e:
            print(f"  ERROR on {rotmod_path.name}: {e}")
            skipped += 1

    elapsed = time.time() - t0
    print(f"\n=== Summary ===")
    print(f"Total galaxies: {len(rotmod_files)}")
    print(f"Successfully fit: {len(results)}")
    print(f"Skipped: {skipped}")
    print(f"Wall time: {elapsed:.1f}s ({elapsed/len(rotmod_files):.2f}s per galaxy)")

    if results:
        # Aggregate per-galaxy posteriors into a joint σ/m posterior
        # Each galaxy contributes its median σ/m with weight = 1/σ(posterior)
        sigma_medians = np.array([r["sigma_0_median"] for r in results])
        sigma_p16 = np.array([r["sigma_0_p16"] for r in results])
        sigma_p84 = np.array([r["sigma_0_p84"] for r in results])
        a_maps = np.array([r["a_map"] for r in results])
        chi2_mins = np.array([r["chi2_min"] for r in results])

        # Weighted average σ/m (weight by 1/posterior width)
        widths = sigma_p84 - sigma_p16
        weights = 1.0 / np.clip(widths, 1e-3, np.inf)
        weights /= weights.sum()
        joint_sigma = np.sum(sigma_medians * weights)
        joint_a = np.mean(a_maps)

        print(f"\n=== Joint σ/m (weighted by 1/posterior width) ===")
        print(f"  Joint σ/m = {joint_sigma:.3f} cm²/g")
        print(f"  Joint a (mean of MAPs) = {joint_a:.2f}")
        print(f"  Median per-galaxy MAP σ/m = {np.median([r['sigma_0_map'] for r in results]):.3f} cm²/g")

    # Save results
    RESULTS_DIR = Path("/home/lamkuenai/dm-sidm-pipeline/v0.3-prelim/data/results")
    out_path = RESULTS_DIR / "t14_sashimi_per_galaxy.json"
    out = {
        "test": "T14_sashimi_SIDM_per_galaxy",
        "n_total_galaxies": len(rotmod_files),
        "n_fit_galaxies": len(results),
        "n_skipped": skipped,
        "wall_seconds": elapsed,
        "forward_model": "sashimi_parametric.py (in-house re-implementation of arXiv:2403.16633)",
        "joint_sigma_m_0_cm2_per_g": float(joint_sigma) if results else None,
        "joint_a": float(joint_a) if results else None,
        "results": results,
    }
    out_path.write_text(json.dumps(out, indent=2, default=str))
    print(f"\noutput -> {out_path}")


if __name__ == "__main__":
    main()