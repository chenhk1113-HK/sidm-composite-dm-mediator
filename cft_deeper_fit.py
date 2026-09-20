"""
T134 deeper investigation: CFT 2021 quantitative fit.

CFT 2021 (arXiv:2102.05674) gives a 2-parameter framework:
- α: bulk mass parameter (controls power-law slope)
- μ: mass gap (controls where resonances appear)

Velocity scaling (Eq. 6.14):
  σ_T ~ v^0       Born (low velocity)
  σ_T ~ v^(-4α)   Born (high velocity)
  σ_T ~ v^(-4/(3-2α)) Classical
  Resonant regime: no simple scaling (peaks)

Our data has 4 peaks at v ≈ 28, 100, 178, 430, 769 km/s.

The classical regime scaling: v^(-4/(3-2α))
  For α = 0.25: v^(-4/(3-0.5)) = v^(-1.6)
  For α = 0.5:  v^(-4/(3-1.0)) = v^(-2.0)
  For α = 0.0:  v^(-4/3) ≈ v^(-1.33)

The Born regime scaling: v^(-4α)
  For α = 0.25: v^(-1.0)  ← matches our slope
  For α = 0.5:  v^(-2.0)  ← matches Born
  For α = 0.0:  v^0       ← constant

Hypothesis: Our data covers BOTH regimes:
  - Low v (3-15 km/s): Born regime → σ_T ~ v^(-1) (slope = 1)
  - High v (100-500 km/s): Classical regime → σ_T ~ v^(-1.6 to -2.0)

Let's fit both regimes separately.
"""
import sys
import os
sys.path.insert(0, r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\code")

import json
import numpy as np
from scipy.optimize import curve_fit

# Load data
with open(r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\sigma_m_phase44.json") as f:
    data = json.load(f)

# Sorted by velocity
items = []
for k, v in data.items():
    if k.startswith('v') and isinstance(v, (int, float)):
        v_str = k.split('_')[0]
        v_val = float(v_str[1:])
        items.append((v_val, v, k))

items.sort()

print("=" * 80)
print("REGIME SEPARATION TEST (CFT 2021 framework)")
print("=" * 80)
print()
print("CFT prediction:")
print("  - Low velocity (Born): σ ~ v^(-4α)")
print("  - High velocity (Classical): σ ~ v^(-4/(3-2α))")
print("  - Resonance: peaks at v_R depending on μ")
print()

# Separate into low-v (UFD/dSph) and high-v (SPARC/cluster)
# Exclude Cloud-9 (resonance)
low_v = [(v, s) for v, s, lbl in items if v < 30 and 'Cloud-9' not in lbl]
high_v = [(v, s) for v, s, lbl in items if v > 30]

print(f"Low-v region (UFD/dSph, v < 30 km/s, n={len(low_v)}):")
for v, s in low_v:
    print(f"  v={v:>5.1f}: σ/m={s:.4e}")
print()
print(f"High-v region (SPARC/cluster, v > 30 km/s, n={len(high_v)}):")
for v, s in high_v:
    print(f"  v={v:>5.1f}: σ/m={s:.4e}")
print()

# Fit low-v region as Born regime
print("=" * 80)
print("LOW-V FIT (Born regime, v < 30 km/s)")
print("=" * 80)
if len(low_v) >= 2:
    v_arr = np.array([c[0] for c in low_v])
    s_arr = np.array([c[1] for c in low_v])
    log_v = np.log10(v_arr)
    log_s = np.log10(s_arr)
    slope_low, intercept_low = np.polyfit(log_v, log_s, 1)
    print(f"\nSlope in low-v Born regime: {slope_low:.3f}")
    print(f"CFT prediction: -4α = -{4*0.25:.2f} for α=0.25")
    print(f"Inferred α = {abs(slope_low)/4:.3f}")
    print(f"Match to α=0.25: {abs(abs(slope_low)/4 - 0.25):.3f}")
    print()

# Fit high-v region as Classical regime
print("=" * 80)
print("HIGH-V FIT (Classical regime, v > 30 km/s)")
print("=" * 80)
if len(high_v) >= 2:
    v_arr = np.array([c[0] for c in high_v])
    s_arr = np.array([c[1] for c in high_v])
    log_v = np.log10(v_arr)
    log_s = np.log10(s_arr)
    slope_high, intercept_high = np.polyfit(log_v, log_s, 1)
    print(f"\nSlope in high-v Classical regime: {slope_high:.3f}")
    # CFT classical: slope = -4/(3-2α)
    # slope = -4/(3-2α) → α = (3 - 4/|slope|)/2 = (3 + slope/(-|slope|)) /2
    # |slope| = 4/(3-2α) → 3-2α = 4/|slope| → α = (3 - 4/|slope|)/2
    alpha_from_classical = (3 - 4/abs(slope_high))/2
    print(f"CFT prediction: -4/(3-2α)")
    print(f"Inferred α = {alpha_from_classical:.3f}")
    print()

# Combined analysis
print("=" * 80)
print("COMBINED ANALYSIS: Born + Classical fit")
print("=" * 80)

# Use all data except Cloud-9
all_clean = [(v, s) for v, s, lbl in items if 'Cloud-9' not in lbl]
v_arr = np.array([c[0] for c in all_clean])
s_arr = np.array([c[1] for c in all_clean])

def cft_combined(v, sigma_0, alpha, mu, v_res=28):
    """
    Combined CFT formula:
    - Below resonance: Born regime, v^(-4α)
    - Above resonance: Classical regime, v^(-4/(3-2α))
    - At resonance: enhanced by factor (v/v_res)^(-2*resonance_strength)
    """
    born = sigma_0 * (100.0 / v)**(4*alpha)
    classical = sigma_0 * (100.0 / v)**(4/(3-2*alpha))
    # Transition at v ~ 30 km/s (Cloud-9 peak)
    weight = 1 / (1 + np.exp(-(v - v_res)/10))
    return (1-weight) * born + weight * classical

# Fit combined formula
try:
    popt, pcov = curve_fit(cft_combined, v_arr, s_arr, p0=[0.1, 0.25, 1.0], maxfev=10000)
    print(f"\nCFT combined fit: σ_0={popt[0]:.4f}, α={popt[1]:.4f}, μ={popt[2]:.4f}")
    predicted = cft_combined(v_arr, *popt)
    residuals = np.log10(predicted) - np.log10(s_arr)
    rmse = np.sqrt(np.mean(residuals**2))
    print(f"Log10 RMSE: {rmse:.4f}")
    print(f"R² equivalent: {1 - np.var(residuals)/np.var(np.log10(s_arr)):.4f}")
    print()
    print("Fit quality:")
    print(f"{'v (km/s)':>10} {'observed':>15} {'CFT predicted':>15} {'residual':>10}")
    for v, s_obs, s_pred in sorted(zip(v_arr, s_arr, predicted)):
        res = np.log10(s_pred) - np.log10(s_obs)
        print(f"{v:>10.1f} {s_obs:>15.4e} {s_pred:>15.4e} {res:>+10.4f}")
except Exception as e:
    print(f"Fit failed: {e}")