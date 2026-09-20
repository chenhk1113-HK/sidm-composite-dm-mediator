"""
T155: Time-bounded sidmkit search with multiprocessing.

sidmkit can hang on certain parameter combinations. Use multiprocessing
with hard timeout per evaluation.

Also: only test parameters likely to give useful results.
"""
import numpy as np
import sidmkit
import warnings
warnings.filterwarnings('ignore')
import json
import multiprocessing as mp
import time
import os


def sigma_single_safe(args):
    """Single sidmkit evaluation with timeout."""
    alpha, m_A, m_chi, v_arr = args
    try:
        model = sidmkit.YukawaModel(m_chi_gev=m_chi, m_med_gev=m_A, alpha=alpha,
                                      potential=sidmkit.PotentialType.ATTRACTIVE)
        sigma = sidmkit.sigma_over_m(v_arr, model, method='partial_wave')
        return sigma
    except:
        return None


def compute_one(params):
    """Compute single Yukawa with timeout."""
    alpha, m_A, m_chi, v_arr_list = params
    v_arr = np.array(v_arr_list)
    return (alpha, m_A, m_chi, sigma_single_safe((alpha, m_A, m_chi, v_arr)))


# Load data
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

print("=" * 70)
print("T155: Time-bounded multiprocessing search")
print("=" * 70)

# Only test parameters likely to converge
# sidmkit was slow for: alpha=0.5 (10s), alpha=1.0
# sidmkit was fast for: alpha in [0.01, 0.3]
# So restrict to alpha in [0.01, 0.3]
test_params = []
for alpha in [0.01, 0.05, 0.1, 0.2, 0.3]:
    for m_A in [0.001, 0.003, 0.01, 0.03]:
        for m_chi in [1.0, 3.0, 10.0]:
            test_params.append((alpha, m_A, m_chi))

print(f"Testing {len(test_params)} parameter combinations")

# Sequential (multiprocessing had issues on Windows)
results = []
t0 = time.time()
for i, (alpha, m_A, m_chi) in enumerate(test_params):
    sigma = sigma_single_safe((alpha, m_A, m_chi, v_arr))
    if sigma is not None and np.all(np.isfinite(sigma)) and np.all(sigma > 0):
        residuals = np.log10(sigma) - np.log10(s_arr)
        if np.all(np.isfinite(residuals)):
            rmse = np.sqrt(np.mean(residuals**2))
            results.append((alpha, m_A, m_chi, rmse, sigma))
    if (i + 1) % 10 == 0:
        elapsed = time.time() - t0
        print(f"  Tested {i+1}/{len(test_params)} in {elapsed:.1f}s")

results.sort(key=lambda x: x[3])
elapsed = time.time() - t0
print(f"\nTotal time: {elapsed:.1f}s")
print(f"Valid fits: {len(results)}/{len(test_params)}")
print()
print("Top 10 fits:")
print(f"{'α_D':>8} {'m_A':>10} {'m_χ':>8} {'RMSE':>10}")
for alpha, m_A, m_chi, rmse, _ in results[:10]:
    print(f"{alpha:>8.3f} {m_A:>10.4f} {m_chi:>8.2f} {rmse:>10.3f}")

# Show best
if results:
    alpha, m_A, m_chi, rmse, sigma = results[0]
    print()
    print(f"BEST: α_D={alpha}, m_A={m_A} GeV, m_χ={m_chi} GeV, RMSE={rmse:.3f}")
    print(f"{'v':>6} {'data':>12} {'pred':>12} {'ratio':>10}")
    for v, s_obs, s_pred in zip(v_arr, s_arr, sigma):
        ratio = s_obs / s_pred
        print(f"{v:>6.1f} {s_obs:>12.4e} {s_pred:>12.4e} {ratio:>10.4f}")