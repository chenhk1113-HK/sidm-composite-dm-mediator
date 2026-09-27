"""
T151: Optimize KK tower parameters to match our 8 data points.
"""
import numpy as np
import sidmkit
import warnings
warnings.filterwarnings('ignore')
import json

with open(r"C:\Users/lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\sigma_m_phase44.json") as f:
    data = json.load(f)

v_data = {}
for k, v in data.items():
    if k.startswith('v') and isinstance(v, (int, float)):
        v_str = k.split('_')[0]
        v_val = float(v_str[1:])
        v_data[v_val] = v

v_arr = np.array(sorted(v_data.keys()))
s_arr = np.array([v_data[v] for v in v_arr])

# Wider parameter scan
print("T151: Optimizing KK tower parameters")
print()

def sigma_kk_tower(v_arr, alpha_D, m_0_GeV, r_mass, m_chi_GeV, n_modes):
    """KK tower: sum over n modes with geometric mass spectrum."""
    sigma_total = np.zeros_like(v_arr, dtype=float)
    for n in range(1, n_modes + 1):
        m_n = m_0_GeV * (r_mass ** n)
        c_n = 1.0 / n
        try:
            model = sidmkit.YukawaModel(m_chi_gev=m_chi_GeV, m_med_gev=m_n, alpha=alpha_D * c_n,
                                          potential=sidmkit.PotentialType.ATTRACTIVE)
            sigma_n = sidmkit.sigma_over_m(v_arr, model, method='partial_wave')
            sigma_total += sigma_n
        except:
            pass
    return sigma_total

# Focused search around best parameters
best_rmse = 1e9
best_params = None
results = []

# 5D search: alpha, m_0, r, m_chi, n_modes
for alpha in [0.05, 0.1, 0.15, 0.2, 0.3]:
    for m_0 in [0.001, 0.005, 0.01, 0.02, 0.05]:
        for r in [1.5, 2.0, 2.5, 3.0]:
            for n_modes in [3, 5, 7, 10]:
                # Fix m_chi = 1 GeV (reasonable DM mass)
                m_chi = 1.0
                try:
                    sigma = sigma_kk_tower(v_arr, alpha, m_0, r, m_chi, n_modes)
                    valid = np.isfinite(sigma) & (sigma > 0)
                    if np.sum(valid) >= 5:
                        residuals = np.log10(sigma[valid]) - np.log10(s_arr[valid])
                        if np.all(np.isfinite(residuals)):
                            rmse = np.sqrt(np.mean(residuals**2))
                            results.append((alpha, m_0, r, n_modes, rmse))
                            if rmse < best_rmse:
                                best_rmse = rmse
                                best_params = (alpha, m_0, r, n_modes)
                except:
                    pass

# Sort
results.sort(key=lambda x: x[4])

print(f"Total fits: {len(results)}")
print()
print("Top 10 KK tower configurations:")
print(f"{'α_D':>10} {'m_0 (GeV)':>12} {'r':>5} {'n':>3} {'RMSE':>10}")
for alpha, m_0, r, n_modes, rmse in results[:10]:
    print(f"{alpha:>10.3f} {m_0:>12.4f} {r:>5.2f} {n_modes:>3} {rmse:>10.3f}")

if results:
    alpha, m_0, r, n_modes, rmse = results[0]
    print()
    print(f"Best fit: α_D={alpha}, m_0={m_0} GeV, r={r}, n_modes={n_modes}, RMSE={rmse:.3f}")
    print()
    print("Detail:")
    sigma = sigma_kk_tower(v_arr, alpha, m_0, r, 1.0, n_modes)
    print(f"{'v':>6} {'data':>12} {'pred':>12} {'ratio':>10}")
    for v, s_obs, s_pred in zip(v_arr, s_arr, sigma):
        if s_pred > 0 and np.isfinite(s_pred):
            ratio = s_obs / s_pred
            print(f"{v:>6.1f} {s_obs:>12.4e} {s_pred:>12.4e} {ratio:>10.4f}")