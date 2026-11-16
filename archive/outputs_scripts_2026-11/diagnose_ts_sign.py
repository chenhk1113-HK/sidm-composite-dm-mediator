"""Diagnose the TS sign convention in the McDaniel+ 2024 data."""
import numpy as np
ROOT = "/home/lamkuenai/sidm-composite-dm-mediator/v0.3-prelim/data/external/fermi_mcdaniel2024"

# Load a few profiles to check the sign
files = [
    "Segue_1_noprior_bb.npy",
    "Draco_noprior_bb.npy",
    "Fornax_noprior_bb.npy",
]
masses = np.logspace(np.log10(1.0), np.log10(1000.0), 40)
sigvs = np.logspace(-28, -22, 60)

# For each profile, show:
# 1. Min and max values
# 2. Value at a "good" point (low sigma_v)
# 3. Value at a "bad" point (high sigma_v)
for f in files:
    arr = np.load(f"{ROOT}/dSphs/TS_profiles/{f}")
    # Good point: m_chi = 50 GeV (idx 22), sigma_v = 1e-29 (below grid)
    i_m = np.argmin(np.abs(np.log10(masses) - np.log10(50.0)))
    # Actually use the lowest sigma_v in the grid
    j_low = 0  # sigma_v = 1e-28
    j_high = -1  # sigma_v = 1e-22
    print(f"{f}:")
    print(f"  shape: {arr.shape}")
    print(f"  min: {arr.min():.3f}, max: {arr.max():.3f}")
    print(f"  at (50 GeV, 1e-28 cm^3/s): TS = {arr[i_m, j_low]:.3f}")
    print(f"  at (50 GeV, 1e-22 cm^3/s): TS = {arr[i_m, j_high]:.3f}")
    print()

# Combined
print("Combined TS (sum over all noprior_bb):")
combined = np.zeros((40, 60))
import os
for f in os.listdir(f"{ROOT}/dSphs/TS_profiles/"):
    if f.endswith("_noprior_bb.npy"):
        combined += np.load(f"{ROOT}/dSphs/TS_profiles/{f}")
i_m = np.argmin(np.abs(np.log10(masses) - np.log10(50.0)))
print(f"  at (50 GeV, 1e-28): TS = {combined[i_m, 0]:.3f}")
print(f"  at (50 GeV, 1e-26): TS = {combined[i_m, np.argmin(np.abs(np.log10(sigvs) - (-26)))]:.3f}")
print(f"  at (50 GeV, 1e-25): TS = {combined[i_m, np.argmin(np.abs(np.log10(sigvs) - (-25)))]:.3f}")
print(f"  at (50 GeV, 1e-24): TS = {combined[i_m, np.argmin(np.abs(np.log10(sigvs) - (-24)))]:.3f}")
print(f"  at (50 GeV, 1e-23): TS = {combined[i_m, np.argmin(np.abs(np.log10(sigvs) - (-23)))]:.3f}")
print(f"  at (50 GeV, 1e-22): TS = {combined[i_m, -1]:.3f}")
print(f"  TS max: {combined.max():.3f} at ({masses[np.unravel_index(combined.argmax(), combined.shape)[0]]:.2f} GeV, "
      f"{sigvs[np.unravel_index(combined.argmax(), combined.shape)[1]]:.2e} cm^3/s)")
print(f"  TS min: {combined.min():.3f}")
print(f"  Pixels with TS > 0 (signal-like): {np.sum(combined > 0)} / {combined.size}")
print(f"  Pixels with TS < 0 (excluded): {np.sum(combined < 0)} / {combined.size}")