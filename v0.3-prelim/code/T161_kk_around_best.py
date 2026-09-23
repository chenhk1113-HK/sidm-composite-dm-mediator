"""
T161: KK tower around best single-Yukawa parameters (T160).
Best: alpha=0.1, mA=0.1 GeV, m_chi=30 GeV, RMSE=1.422

Now add KK modes to see if we can capture Cloud-9 peak.
"""
import numpy as np
import sidmkit
import warnings
warnings.filterwarnings('ignore')
import json
import time

with open(r"C:\Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results/sigma_m_phase44.json") as f:
    data = json.load(f)

v_data = {}
for k, v in data.items():
    if k.startswith('v') and isinstance(v, (int, float)):
        v_str = k.split('_')[0]
        v_val = float(v_str[1:])
        v_data[v_val] = v

v_arr = np.array(sorted(v_data.keys()))
s_arr = np.array([v_data[v] for v in v_arr])

# Wider v range to find peaks
v_extended = np.concatenate([v_arr, np.array([50, 75, 200])])

def sigma_kk(v_arr, alpha_D, m_0_GeV, r_mass, m_chi_GeV, n_modes):
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
            return None
    return sigma_total


print("=" * 70)
print("T161: KK tower around T160 best")
print("=" * 70)
print()

# Try KK around T160 best
best_rmse = 1e9
best_params = None
results = []

for alpha in [0.05, 0.1, 0.2]:
    for m_0 in [0.03, 0.1, 0.3]:  # larger range around 0.1
        for r in [1.5, 2.0, 3.0]:
            for n_modes in [2, 3, 5, 7]:
                m_chi = 30.0  # use T160 best
                try:
                    sigma = sigma_kk(v_arr, alpha, m_0, r, m_chi, n_modes)
                    if sigma is not None and np.all(np.isfinite(sigma)) and np.all(sigma > 0):
                        residuals = np.log10(sigma) - np.log10(s_arr)
                        if np.all(np.isfinite(residuals)):
                            rmse = np.sqrt(np.mean(residuals**2))
                            results.append((alpha, m_0, r, n_modes, rmse))
                            if rmse < best_rmse:
                                best_rmse = rmse
                                best_params = (alpha, m_0, r, n_modes)
                except:
                    pass

results.sort(key=lambda x: x[4])
print(f"Tested {len(results)} KK configurations")
print()

print("Top 10:")
print(f"{'α_D':>8} {'m_0':>8} {'r':>5} {'n':>3} {'RMSE':>10}")
for alpha, m_0, r, n_modes, rmse in results[:10]:
    print(f"{alpha:>8.3f} {m_0:>8.4f} {r:>5.2f} {n_modes:>3} {rmse:>10.3f}")

# Show best
if results:
    alpha, m_0, r, n_modes, rmse = results[0]
    print()
    print(f"BEST: α_D={alpha}, m_0={m_0}, r={r}, n_modes={n_modes}, RMSE={rmse:.3f}")
    sigma = sigma_kk(v_arr, alpha, m_0, r, 30.0, n_modes)
    print(f"{'v':>6} {'data':>12} {'pred':>12} {'ratio':>10}")
    for v, s_obs, s_pred in zip(v_arr, s_arr, sigma):
        ratio = s_obs / s_pred if s_pred > 0 else float('inf')
        print(f"{v:>6.1f} {s_obs:>12.4e} {s_pred:>12.4e} {ratio:>10.4f}")