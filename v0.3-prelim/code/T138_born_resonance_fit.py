"""
T138 — Phase 6: Use Born + Breit-Wigner resonance structure

After T137 showed that pure Born-Yukawa gives slope -2 to -4, but our
data needs slope -1, the missing piece is RESONANCE STRUCTURE.

Plan:
1. Use Born approximation as background
2. Add Breit-Wigner resonances for n bound states (n=1, 2, 3, 4)
3. Tune (alpha_D, m_A', mu_red, resonance positions, widths) to match data
4. Search parameter space systematically
5. Test if any natural choice gives alpha_gamma ≈ 1

This is semi-analytical but captures the essential non-perturbative physics.
"""
import numpy as np
import json

# Load our phenomenology data
with open(r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\sigma_m_phase44.json") as f:
    data = json.load(f)

v_data = []
s_data = []
for k, v in data.items():
    if k.startswith('v') and isinstance(v, (int, float)) and 'Cloud-9' not in k:
        v_data.append(float(k.split('_')[0][1:]))
        s_data.append(v)

# Sort by v
indices = np.argsort(v_data)
v_data = np.array(v_data)[indices]
s_data = np.array(s_data)[indices]

print("Our data (excluding Cloud-9):")
for v, s in zip(v_data, s_data):
    print(f"  v={v:>6.1f}: σ/m = {s:.4e}")
print()

# Try fitting: σ/m(v) = Born_bg + Σ_n BW_n(v)
# Born background: σ_bg ~ v^(-a) where a is the slope
# BW: σ_res ~ BW(v; v_res, width, peak)

# From T132 we know the phenomenology has:
# - 4 BW peaks at v = 28, 100, 178, 430, 769 km/s (Cloud-9 + others)
# - Background slope ≈ 1
# - BUT: Cloud-9 is in our data, not in v_data above

# Let's fit all 8 points including Cloud-9
v_all = []
s_all = []
for k, v in data.items():
    if k.startswith('v') and isinstance(v, (int, float)):
        v_all.append(float(k.split('_')[0][1:]))
        s_all.append(v)

indices = np.argsort(v_all)
v_all = np.array(v_all)[indices]
s_all = np.array(s_all)[indices]

# Model: σ/m(v) = A × v^(-a) + Σ_n (P_n × Γ_n² / ((v - v_n)² + Γ_n²))
# Parameters: A, a, v_n, P_n, Γ_n

# Fit with scipy.optimize
from scipy.optimize import curve_fit

def model(v, A, a, v1, P1, G1, v2, P2, G2, v3, P3, G3, v4, P4, G4):
    """4-peak + power-law background model."""
    bg = A * v**(-a)
    peaks = sum(
        P_n * G_n**2 / ((v - v_n)**2 + G_n**2)
        for v_n, P_n, G_n in [(v1, P1, G1), (v2, P2, G2), (v3, P3, G3), (v4, P4, G4)]
    )
    return bg + peaks

# Initial guess
p0 = [
    0.1, 1.0,           # A, a
    28, 100, 5,         # v1, P1, G1
    100, 0.2, 30,       # v2
    178, 0.05, 30,      # v3
    430, 0.001, 50,     # v4
]

# Bounds
bounds = (
    [1e-6, 0.01, 10, 0, 0.1, 50, 0, 0.1, 100, 0, 0.1, 200, 0, 0.1],
    [1e3, 4.0, 50, 1000, 50, 200, 1000, 200, 300, 1000, 500, 600, 1000]
)

try:
    popt, pcov = curve_fit(model, v_all, s_all, p0=p0, bounds=bounds, maxfev=10000)
    print("=" * 70)
    print("FIT RESULT (T138 Phase 6: 4-peak + power-law)")
    print("=" * 70)
    print()
    labels = ['A', 'a', 'v1', 'P1', 'G1', 'v2', 'P2', 'G2', 'v3', 'P3', 'G3', 'v4', 'P4', 'G4']
    for label, val in zip(labels, popt):
        print(f"  {label:>4}: {val:>12.4e}" if val < 0.01 or val > 100 else f"  {label:>4}: {val:>12.4f}")

    print()
    predicted = model(v_all, *popt)
    residuals = np.log10(predicted) - np.log10(s_all)
    rmse = np.sqrt(np.mean(residuals**2))
    print(f"  RMSE: {rmse:.4f}")
    print()
    print("Comparison (data vs model):")
    print(f"{'v':>6} {'data':>12} {'model':>12} {'ratio':>10}")
    for v, s_obs, s_pred in zip(v_all, s_all, predicted):
        ratio = s_obs / s_pred if s_pred > 0 else float('inf')
        print(f"{v:>6.1f} {s_obs:>12.4e} {s_pred:>12.4e} {ratio:>10.4f}")
except Exception as e:
    print(f"Fit failed: {e}")

# Also test: what if we use just Born background (no peaks)?
print()
print("=" * 70)
print("PURE POWER-LAW FIT (no peaks):")
print("=" * 70)

# Use only non-Cloud-9 points
mask = v_data < 30  # exclude Cloud-9 (28 km/s with peak)
if np.sum(mask) >= 2:
    log_v = np.log10(v_data[mask])
    log_s = np.log10(s_data[mask])
    slope, intercept = np.polyfit(log_v, log_s, 1)
    print(f"Slope: {slope:.3f}")
    print(f"Intercept: {intercept:.3f} (log10 scale)")
    print(f"Equation: log10(σ/m) = {intercept:.3f} + {slope:.3f} * log10(v)")
    print()
    print("Our data points used:")
    for v, s in zip(v_data[mask], s_data[mask]):
        pred = 10**(intercept + slope*np.log10(v))
        ratio = s / pred
        print(f"  v={v:>6.1f}: data={s:.4e}, fit={pred:.4e}, ratio={ratio:.4f}")