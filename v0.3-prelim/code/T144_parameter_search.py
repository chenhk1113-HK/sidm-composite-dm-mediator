"""
T144: Find Yukawa parameters that match our 8 data points.

We know sidmkit's partial_wave gives slope ≈ -1 (correct!).
Now find parameters that give:
- 4 peaks at v = 28, 100, 178, 430, 769 km/s (or near them)
- Right absolute magnitude

This is a 3-parameter search: (α_D, m_A', m_χ).
Use coarse grid then refine.
"""
import numpy as np
import sys
import sidmkit
import json

# Load our data
with open(r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\sigma_m_phase44.json") as f:
    data = json.load(f)

v_data = {}
for k, v in data.items():
    if k.startswith('v') and isinstance(v, (int, float)):
        v_str = k.split('_')[0]
        v_val = float(v_str[1:])
        v_data[v_val] = v

v_data_sorted = sorted(v_data.keys())
v_data_arr = np.array(v_data_sorted)
s_data_arr = np.array([v_data[v] for v in v_data_sorted])

print("=" * 70)
print("T144: Parameter search to match our 8 data points")
print("=" * 70)
print()

# Coarse scan
results = []
for log_alpha in [-2.5, -2.0, -1.5, -1.0, -0.5, 0.0]:  # 0.003 to 1.0
    for log_mA in [-3, -2, -1, 0, 1]:  # 1 MeV to 100 GeV
        for log_mChi in [-1, 0, 1, 2]:  # 0.1 to 100 GeV
            alpha = 10**log_alpha
            mA = 10**(log_mA - 3)  # GeV
            mChi = 10**log_mChi  # GeV

            model = sidmkit.YukawaModel(
                m_chi_gev=mChi,
                m_med_gev=mA,
                alpha=alpha,
                potential=sidmkit.PotentialType.ATTRACTIVE
            )

            try:
                sigma_pred = sidmkit.sigma_over_m(v_data_arr, model, method='partial_wave')
                # RMSE on log scale
                mask = (sigma_pred > 1e-30) & (s_data_arr > 0)
                if np.sum(mask) >= 4:
                    residuals = np.log10(sigma_pred[mask]) - np.log10(s_data_arr[mask])
                    rmse = np.sqrt(np.mean(residuals**2))
                    results.append((alpha, mA, mChi, rmse))
            except Exception as e:
                pass

# Sort and show top 10
results.sort(key=lambda x: x[3])
print(f"Top 10 fits (out of {len(results)} candidates):")
print(f"{'α_D':>10} {'m_A (GeV)':>10} {'m_χ (GeV)':>10} {'RMSE':>10}")
for alpha, mA, mChi, rmse in results[:10]:
    print(f"{alpha:>10.3e} {mA:>10.3e} {mChi:>10.3e} {rmse:>10.3f}")

# Show the best fit in detail
if results:
    alpha, mA, mChi, rmse = results[0]
    print()
    print(f"Best fit: α_D={alpha:.3e}, m_A={mA:.3e} GeV, m_χ={mChi:.3e} GeV, RMSE={rmse:.3f}")
    print()
    print(f"{'v (km/s)':>10} {'data':>12} {'model':>12} {'ratio':>10}")
    model = sidmkit.YukawaModel(m_chi_gev=mChi, m_med_gev=mA, alpha=alpha,
                                  potential=sidmkit.PotentialType.ATTRACTIVE)
    sigma_pred = sidmkit.sigma_over_m(v_data_arr, model, method='partial_wave')
    for v, s_obs, s_pred in zip(v_data_arr, s_data_arr, sigma_pred):
        ratio = s_obs / s_pred if s_pred > 0 else float('inf')
        print(f"{v:>10.1f} {s_obs:>12.4e} {s_pred:>12.4e} {ratio:>10.4f}")