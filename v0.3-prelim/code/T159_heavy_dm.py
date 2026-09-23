"""
T159: Wider parameter scan with VERY heavy m_chi.

Our previous searches had m_chi in [0.5, 30] GeV. Let me try heavier DM
(m_chi = 100 GeV to 10 TeV) to see if that helps.
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

# Heavy DM parameter scan
test_params = []
for alpha in [0.01, 0.05, 0.1, 0.3]:
    for m_A in [0.001, 0.01, 0.1]:
        for m_chi in [100, 300, 1000, 10000]:  # heavy!
            test_params.append((alpha, m_A, m_chi))

print("=" * 70)
print("T159: Heavy DM parameter scan")
print("=" * 70)
print(f"Testing {len(test_params)} heavy-DM configurations")
print()

results = []
t0 = time.time()
for alpha, m_A, m_chi in test_params:
    try:
        model = sidmkit.YukawaModel(m_chi_gev=m_chi, m_med_gev=m_A, alpha=alpha,
                                      potential=sidmkit.PotentialType.ATTRACTIVE)
        sigma = sidmkit.sigma_over_m(v_arr, model, method='partial_wave')

        if sigma is not None and np.all(np.isfinite(sigma)) and np.all(sigma > 0):
            valid = np.isfinite(sigma) & (sigma > 0)
            if np.sum(valid) >= 5:
                residuals = np.log10(sigma[valid]) - np.log10(s_arr[valid])
                rmse = np.sqrt(np.mean(residuals**2))
                results.append((alpha, m_A, m_chi, rmse))
    except:
        pass

results.sort(key=lambda x: x[3])
elapsed = time.time() - t0
print(f"Tested {len(results)} in {elapsed:.1f}s")
print()

print("Top 10 heavy-DM configurations:")
print(f"{'α_D':>8} {'m_A':>10} {'m_χ':>10} {'RMSE':>10}")
for alpha, m_A, m_chi, rmse in results[:10]:
    print(f"{alpha:>8.3f} {m_A:>10.4f} {m_chi:>10.1f} {rmse:>10.3f}")

# Show best
if results:
    alpha, m_A, m_chi, rmse = results[0]
    print()
    print(f"BEST: α_D={alpha}, m_A={m_A}, m_χ={m_chi}, RMSE={rmse:.3f}")
    sigma = sidmkit.sigma_over_m(v_arr, sidmkit.YukawaModel(m_chi_gev=m_chi, m_med_gev=m_A, alpha=alpha,
                                      potential=sidmkit.PotentialType.ATTRACTIVE), method='partial_wave')
    print(f"{'v':>6} {'data':>12} {'pred':>12} {'ratio':>10}")
    for v, s_obs, s_pred in zip(v_arr, s_arr, sigma):
        ratio = s_obs / s_pred if s_pred > 0 else float('inf')
        print(f"{v:>6.1f} {s_obs:>12.4e} {s_pred:>12.4e} {ratio:>10.4f}")