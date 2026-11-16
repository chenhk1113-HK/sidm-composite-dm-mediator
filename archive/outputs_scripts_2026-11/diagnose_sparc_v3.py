"""Diagnose the SPARC hierarchical grid - find any remaining outliers."""
import numpy as np
grid = np.load("/home/lamkuenai/sidm-composite-dm-mediator/v0.3-prelim/data/results/sparc_hierarchical_grid.npz")
logL = grid["logL_grid"]
logL_per_galaxy = grid["logL_per_galaxy"]
galaxy_names = grid["galaxy_names"]
print(f"logL grid shape: {logL.shape}")
print(f"logL range: {logL.min():.3g} to {logL.max():.3g}")
print(f"per-galaxy log L distribution per cell:")
print(f"  median cell-wise min: {np.median(logL_per_galaxy.min(axis=(1,2))):.2f}")
print(f"  median cell-wise max: {np.median(logL_per_galaxy.max(axis=(1,2))):.2f}")

# Find galaxies where best cell is still very negative (using the -1e6 fallback a lot)
worst_max_per_galaxy = logL_per_galaxy.max(axis=(1,2))
sorted_idx = np.argsort(worst_max_per_galaxy)[:5]
print("\nTop-5 galaxies with worst max log L (most cells used the -1e6 fallback):")
for idx in sorted_idx:
    n_bad = np.sum(logL_per_galaxy[idx] == -1e6)
    print(f"  {galaxy_names[idx]}: max log L = {worst_max_per_galaxy[idx]:.2f}, "
          f"{n_bad}/{logL_per_galaxy[idx].size} cells used the fallback")

# Distribution of cell values
flat = logL.ravel()
print(f"\nSummed log L distribution:")
print(f"  min: {flat.min():.3g}")
print(f"  q1: {np.percentile(flat, 25):.2f}")
print(f"  median: {np.median(flat):.2f}")
print(f"  q3: {np.percentile(flat, 75):.2f}")
print(f"  max: {flat.max():.2f}")
print(f"  cells below -1e6 (fallback): {np.sum(flat < -1e5)}/{flat.size}")

# So the "very negative" cells come from galaxies whose all cells fell back
# What is the maximum contribution from any single galaxy?
contributions = logL_per_galaxy.max(axis=(1,2))  # per-galaxy max
top_contributors = np.argsort(contributions)[-5:]
print(f"\nTop-5 contributing galaxies (best max log L):")
for idx in top_contributors:
    print(f"  {galaxy_names[idx]}: max log L = {contributions[idx]:.2f}")