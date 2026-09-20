"""
T144-fast: Faster parameter search.
"""
import numpy as np
import sidmkit
import json
import sys
import time

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

# Smaller coarse scan
results = []
t0 = time.time()
tested = 0
for log_alpha in [-2, -1.5, -1, -0.5, 0]:
    for log_mA in [-2, -1, 0]:
        for log_mChi in [0, 1, 2]:
            alpha = 10**log_alpha
            mA = 10**(log_mA - 3)
            mChi = 10**log_mChi

            model = sidmkit.YukawaModel(
                m_chi_gev=mChi,
                m_med_gev=mA,
                alpha=alpha,
                potential=sidmkit.PotentialType.ATTRACTIVE
            )

            try:
                sigma_pred = sidmkit.sigma_over_m(v_data_arr, model, method='partial_wave')
                mask = (sigma_pred > 1e-30) & np.isfinite(s_data_arr)
                if np.sum(mask) >= 4:
                    residuals = np.log10(sigma_pred[mask]) - np.log10(s_data_arr[mask])
                    rmse = np.sqrt(np.mean(residuals**2))
                    results.append((alpha, mA, mChi, rmse))
                    tested += 1
                    if tested % 5 == 0:
                        elapsed = time.time() - t0
                        print(f"  Tested {tested} in {elapsed:.0f}s, last RMSE={rmse:.3f}")
            except Exception as e:
                pass

# Sort
results.sort(key=lambda x: x[3])
print()
print(f"Top 10 fits (out of {tested} candidates):")
print(f"{'α_D':>10} {'m_A (GeV)':>10} {'m_χ (GeV)':>10} {'RMSE':>10}")
for alpha, mA, mChi, rmse in results[:10]:
    print(f"{alpha:>10.3e} {mA:>10.3e} {mChi:>10.3e} {rmse:>10.3f}")

if results:
    alpha, mA, mChi, rmse = results[0]
    print()
    print(f"Best fit details:")
    model = sidmkit.YukawaModel(m_chi_gev=mChi, m_med_gev=mA, alpha=alpha,
                                  potential=sidmkit.PotentialType.ATTRACTIVE)
    sigma_pred = sidmkit.sigma_over_m(v_data_arr, model, method='partial_wave')
    print(f"{'v (km/s)':>10} {'data':>12} {'model':>12} {'ratio':>10}")
    for v, s_obs, s_pred in zip(v_data_arr, s_data_arr, sigma_pred):
        ratio = s_obs / s_pred if s_pred > 0 else float('inf')
        print(f"{v:>10.1f} {s_obs:>12.4e} {s_pred:>12.4e} {ratio:>10.4f}")