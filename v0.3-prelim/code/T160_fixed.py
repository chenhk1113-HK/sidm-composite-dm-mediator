"""
T160-fixed: Fast comprehensive search using multiprocessing timeout.
"""
import numpy as np
import sidmkit
import warnings
warnings.filterwarnings('ignore')
import json
import time
from multiprocessing import Pool, TimeoutError as MPTimeoutError

def sigma_single(args):
    """Single sidmkit evaluation."""
    alpha, m_A, m_chi, v_arr_list = args
    v_arr = np.array(v_arr_list)
    try:
        model = sidmkit.YukawaModel(m_chi_gev=m_chi, m_med_gev=m_A, alpha=alpha,
                                      potential=sidmkit.PotentialType.ATTRACTIVE)
        sigma = sidmkit.sigma_over_m(v_arr, model, method='partial_wave')
        if sigma is None:
            return None
        return (alpha, m_A, m_chi, sigma.tolist())
    except:
        return None


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

# Comprehensive parameter space
test_params = []
for alpha in [0.01, 0.05, 0.1, 0.2]:
    for m_A in [0.001, 0.003, 0.01, 0.03, 0.1]:
        for m_chi in [1.0, 3.0, 10.0, 30.0]:
            test_params.append((alpha, m_A, m_chi, v_arr.tolist()))

print(f"Testing {len(test_params)} configurations sequentially")

results = []
t0 = time.time()
tested = 0
for params in test_params:
    alpha, m_A, m_chi = params[:3]
    res = sigma_single(params)
    tested += 1

    if res is not None:
        _, _, _, sigma_list = res
        sigma = np.array(sigma_list)
        if np.all(np.isfinite(sigma)) and np.all(sigma > 0):
            valid = np.isfinite(sigma) & (sigma > 0)
            if np.sum(valid) >= 5:
                residuals = np.log10(sigma[valid]) - np.log10(s_arr[valid])
                if np.all(np.isfinite(residuals)):
                    rmse = np.sqrt(np.mean(residuals**2))
                    results.append((alpha, m_A, m_chi, rmse))

    elapsed = time.time() - t0
    if tested % 5 == 0:
        print(f"  Tested {tested}/{len(test_params)} in {elapsed:.0f}s, {len(results)} valid")

results.sort(key=lambda x: x[3])
elapsed = time.time() - t0
print(f"\nTotal: tested {tested}, valid {len(results)} in {elapsed:.1f}s")
print()

print("Top 15:")
print(f"{'α_D':>8} {'m_A':>10} {'m_χ':>8} {'RMSE':>10}")
for alpha, m_A, m_chi, rmse in results[:15]:
    print(f"{alpha:>8.3f} {m_A:>10.4f} {m_chi:>8.1f} {rmse:>10.3f}")

# Show best
if results:
    alpha, m_A, m_chi, rmse = results[0]
    print()
    print(f"BEST: α_D={alpha}, m_A={m_A}, m_χ={m_chi}, RMSE={rmse:.3f}")
    res = sigma_single((alpha, m_A, m_chi, v_arr.tolist()))
    sigma = np.array(res[3])
    print(f"{'v':>6} {'data':>12} {'pred':>12} {'ratio':>10}")
    for v, s_obs, s_pred in zip(v_arr, s_arr, sigma):
        ratio = s_obs / s_pred if s_pred > 0 else float('inf')
        print(f"{v:>6.1f} {s_obs:>12.4e} {s_pred:>12.4e} {ratio:>10.4f}")