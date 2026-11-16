"""Diagnose which galaxy has the catastrophic -1e9 log L."""
import numpy as np
grid = np.load("/home/lamkuenai/sidm-composite-dm-mediator/v0.3-prelim/data/results/sparc_hierarchical_grid.npz")
logL_per_galaxy = grid["logL_per_galaxy"]
galaxy_names = grid["galaxy_names"]
sigma_m = grid["sigma_m_grid"]
a = grid["a_grid"]
print(f"logL_per_galaxy shape: {logL_per_galaxy.shape}")

# Find the worst-case cell in each galaxy
worst_per_galaxy = logL_per_galaxy.min(axis=(1, 2))
worst_galaxy_idx = np.argmin(worst_per_galaxy)
print(f"\nWorst galaxy: {galaxy_names[worst_galaxy_idx]} (idx {worst_galaxy_idx})")
print(f"  worst log L = {worst_per_galaxy[worst_galaxy_idx]:.3g}")

# Distribution of worst log L per galaxy
print(f"\nWorst log L per galaxy: min = {worst_per_galaxy.min():.3g}, "
      f"max = {worst_per_galaxy.max():.3g}, median = {np.median(worst_per_galaxy):.2f}")

# Top-5 worst galaxies
worst_5_idx = np.argsort(worst_per_galaxy)[:5]
print(f"\nTop-5 worst galaxies:")
for idx in worst_5_idx:
    print(f"  {galaxy_names[idx]}: worst log L = {worst_per_galaxy[idx]:.3g}")

# At sigma_m = 0.1 cm²/g (where the suspicious value is), find the galaxies contributing
i_sm = np.argmin(np.abs(sigma_m - 0.1))
print(f"\nAt sigma_m = {sigma_m[i_sm]:.3g} cm²/g (cell {i_sm}):")
logL_at_sm = logL_per_galaxy[:, i_sm, :]
print(f"  log L range: {logL_at_sm.min():.3g} to {logL_at_sm.max():.2f}")
worst_at_sm_idx = logL_at_sm.argmin() // logL_at_sm.shape[1]
worst_at_sm_j = logL_at_sm.argmin() % logL_at_sm.shape[1]
print(f"  worst galaxy: {galaxy_names[worst_at_sm_idx]} (log L = {logL_at_sm[worst_at_sm_idx, worst_at_sm_j]:.3g} at a={a[worst_at_sm_j]:.2f})")
# Print top-5 contributors to the bad cell
sorted_idx = np.argsort(logL_at_sm.min(axis=1))[:5]
print(f"  top-5 worst at this σ/m:")
for idx in sorted_idx:
    print(f"    {galaxy_names[idx]}: log L = {logL_at_sm[idx].min():.3g}")

# Summed log L = sum over galaxies at this cell
summed_at_sm = logL_per_galaxy[:, i_sm, :].sum(axis=0)
print(f"\nSummed log L at σ/m = {sigma_m[i_sm]:.3g}:")
print(f"  range: {summed_at_sm.min():.3g} to {summed_at_sm.max():.2f}")
print(f"  suspicious outlier value: {summed_at_sm.min():.3g}")
# This is what -1.08e9 is

# Check the actual logL_grid value at i_sm
logL_grid = grid["logL_grid"]
print(f"\nlogL_grid[{i_sm}, best_a]: {logL_grid[i_sm, logL_grid[i_sm].argmax()]:.3g}")