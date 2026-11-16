"""Inspect the SPARC hierarchical pre-computed grid."""
import numpy as np
grid = np.load("/home/lamkuenai/sidm-composite-dm-mediator/v0.3-prelim/data/results/sparc_hierarchical_grid.npz")
sigma_m = grid["sigma_m_grid"]
a = grid["a_grid"]
logL = grid["logL_grid"]
print(f"sigma_m_grid: {len(sigma_m)} cells from {sigma_m.min():.3g} to {sigma_m.max():.3g}")
print(f"a_grid: {len(a)} cells from {a.min():.2f} to {a.max():.2f}")
print(f"logL_grid shape: {logL.shape}")
print(f"logL range: {logL.min():.2f} to {logL.max():.2f}")
print()

# Find best-fit
i_sm, i_a = np.unravel_index(logL.argmax(), logL.shape)
print(f"Best-fit (raw max): σ/m = {sigma_m[i_sm]:.3g}, a = {a[i_a]:.2f}, log L = {logL[i_sm, i_a]:.2f}")

# Check a few canonical points
# Reference points: T21 real KiSS-SIDM MAP = 1.722 cm²/g, T8 nominal = 1.0 cm²/g, T17 placeholder = 1.095 cm²/g
for sm_target in [0.1, 1.0, 1.7, 10.0, 100.0]:
    i = np.argmin(np.abs(sigma_m - sm_target))
    # Find best a at this sigma_m
    j_best = logL[i, :].argmax()
    print(f"  σ/m = {sigma_m[i]:.3g} cm²/g: best a = {a[j_best]:.2f}, log L = {logL[i, j_best]:.2f}")

# Marginalized log L over a (sum)
logL_sm_marg = np.log(np.sum(np.exp(logL - logL.max()), axis=1)) + logL.max()
i_best = logL_sm_marg.argmax()
print(f"\nMarginalized over a: best σ/m = {sigma_m[i_best]:.3g}, max log L = {logL_sm_marg[i_best]:.2f}")
# 95% CL on sigma_m after marginalizing over a
threshold = logL_sm_marg.max() - 2.71
mask = logL_sm_marg >= threshold
i_lo = mask.argmax()
i_hi = len(mask) - 1 - mask[::-1].argmax()
print(f"95% CL on σ/m after marginalizing over a: "
      f"[{sigma_m[i_lo]:.3g}, {sigma_m[i_hi]:.3g}] cm²/g")

# Compare to the saturation score baseline
def delta_log_sparc_baseline(sigma_m_0, a):
    """The OLD saturation score from t8_v03_joint_fit.py."""
    sigma_m_v = sigma_m_0 * (100.0 / 100.0) ** a  # V_GALAXY = 100 km/s
    if sigma_m_v <= 0:
        return 0.0
    Dsat = 5000.0
    sigma_transition = 0.5
    return Dsat * (1.0 - np.exp(-sigma_m_v / sigma_transition))

print("\nBaseline (saturation score) at canonical points:")
for sm_target in [0.1, 1.0, 1.7, 10.0]:
    print(f"  σ/m = {sm_target}: Δlog_Z = {delta_log_sparc_baseline(sm_target, 0):.1f}")

print(f"\nFile size: {grid.files}")