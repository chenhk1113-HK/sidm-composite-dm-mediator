"""
T167: Bootstrap stability test.

Sample 8 points with replacement from our 8 data points.
Refit each bootstrap sample.
Determine whether best-fit parameters are stable across bootstraps.

If alpha_D, m_A, m_chi are stable across bootstraps → robust fit.
If they vary wildly → fit is data-noise-driven.
"""
import numpy as np
import sidmkit
import json
import warnings
warnings.filterwarnings('ignore')
from concurrent.futures import ThreadPoolExecutor, TimeoutError

with open(r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\sigma_m_phase44.json") as f:
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
print("T167: Bootstrap stability test")
print("=" * 70)
print()
print(f"Sampling 8 points with replacement from {len(v_arr)} originals")
print(f"Running {10} bootstrap iterations")
print()

TIMEOUT = 15
def sigma_with_timeout(alpha, m_A, m_chi, v_arr, timeout=15):
    def compute():
        model = sidmkit.YukawaModel(m_chi_gev=m_chi, m_med_gev=m_A, alpha=alpha,
                                      potential=sidmkit.PotentialType.ATTRACTIVE)
        return sidmkit.sigma_over_m(v_arr, model, method='partial_wave')
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(compute)
        try:
            return future.result(timeout=timeout)
        except:
            return None

test_params = []
for alpha in [0.05, 0.1, 0.2, 0.3]:
    for m_A in [0.03, 0.1, 0.3]:
        for m_chi in [10, 30, 100]:
            test_params.append((alpha, m_A, m_chi))

np.random.seed(42)
N_BOOTSTRAPS = 10

bootstrap_results = []

for boot_idx in range(N_BOOTSTRAPS):
    # Sample 8 points with replacement
    indices = np.random.choice(len(v_arr), size=len(v_arr), replace=True)
    v_boot = v_arr[indices]
    s_boot = s_arr[indices]

    # Check if unique velocities
    unique_v = np.unique(v_boot)
    if len(unique_v) < 4:
        continue

    best_rmse = float('inf')
    best_params = None

    for alpha, m_A, m_chi in test_params:
        sigma = sigma_with_timeout(alpha, m_A, m_chi, v_boot)
        if sigma is None or not np.all(np.isfinite(sigma)) or not np.all(sigma > 0):
            continue
        residuals = np.log10(sigma) - np.log10(s_boot)
        if np.all(np.isfinite(residuals)):
            rmse = np.sqrt(np.mean(residuals**2))
            if rmse < best_rmse:
                best_rmse = rmse
                best_params = (alpha, m_A, m_chi)

    if best_params is not None:
        bootstrap_results.append({
            'iteration': boot_idx,
            'best_rmse': best_rmse,
            'best_params': list(best_params),
        })
        print(f"  Boot {boot_idx+1:>2}: RMSE={best_rmse:.3f} alpha={best_params[0]} mA={best_params[1]} mChi={best_params[2]}")

print()
print("=" * 70)
print("STABILITY ANALYSIS")
print("=" * 70)
print()
if len(bootstrap_results) >= 3:
    alphas = [r['best_params'][0] for r in bootstrap_results]
    mAs = [r['best_params'][1] for r in bootstrap_results]
    mChis = [r['best_params'][2] for r in bootstrap_results]
    rmses = [r['best_rmse'] for r in bootstrap_results]

    print(f"alpha_D: {np.min(alphas):.3f} - {np.max(alphas):.3f} (mean {np.mean(alphas):.3f})")
    print(f"m_A: {np.min(mAs):.3f} - {np.max(mAs):.3f} (mean {np.mean(mAs):.3f})")
    print(f"m_chi: {np.min(mChis):.1f} - {np.max(mChis):.1f} (mean {np.mean(mChis):.1f})")
    print(f"RMSE: {np.min(rmses):.3f} - {np.max(rmses):.3f} (mean {np.mean(rmses):.3f})")

    print()
    alpha_spread = np.std(alphas) / np.mean(alphas)
    if alpha_spread < 0.3:
        print("VERDICT: alpha_D is STABLE across bootstraps (CV < 30%)")
        print("  → Robust fit")
    else:
        print("VERDICT: alpha_D is UNSTABLE across bootstraps")
        print("  → Fit is data-noise-driven")

import os
output_file = r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\t167_bootstrap.json"
os.makedirs(os.path.dirname(output_file), exist_ok=True)
with open(output_file, 'w') as f:
    json.dump(bootstrap_results, f, indent=2)
print(f"\nResults saved to {output_file}")