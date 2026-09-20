"""
T166: Leave-one-out robustness check.

For each of our 8 data points, refit with that point excluded.
Determines which data points are "load-bearing" for our fit.

If excluding Cloud-9 gives similar RMSE → Cloud-9 is not critical.
If excluding low-v points gives much worse RMSE → low-v points are critical.
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
print("T166: Leave-one-out robustness check")
print("=" * 70)
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

# Best params from T163 KK tower
# Single Yukawa: alpha=0.3, m_0=0.3 GeV, m_chi=30 GeV, RMSE=1.408
# For LOO, use a range of params
test_params = []
for alpha in [0.05, 0.1, 0.2, 0.3]:
    for m_A in [0.03, 0.1, 0.3]:
        for m_chi in [10, 30, 100]:
            test_params.append((alpha, m_A, m_chi))

print(f"Testing {len(test_params)} parameter combinations per LOO iteration")
print()

results = {}

# Full fit (all 8 points)
print("Full fit (all 8 points):")
best_full_rmse = float('inf')
best_full_params = None
for alpha, m_A, m_chi in test_params:
    sigma = sigma_with_timeout(alpha, m_A, m_chi, v_arr)
    if sigma is None or not np.all(np.isfinite(sigma)) or not np.all(sigma > 0):
        continue
    residuals = np.log10(sigma) - np.log10(s_arr)
    if np.all(np.isfinite(residuals)):
        rmse = np.sqrt(np.mean(residuals**2))
        if rmse < best_full_rmse:
            best_full_rmse = rmse
            best_full_params = (alpha, m_A, m_chi)
print(f"  Best RMSE: {best_full_rmse:.3f} at {best_full_params}")
results['all_8_points'] = {
    'excluded': None,
    'best_rmse': best_full_rmse,
    'best_params': list(best_full_params) if best_full_params else None,
}

print()
print("Leave-one-out fits:")
print()

for i, v in enumerate(v_arr):
    mask = np.arange(len(v_arr)) != i
    v_sub = v_arr[mask]
    s_sub = s_arr[mask]

    best_rmse = float('inf')
    best_params = None

    for alpha, m_A, m_chi in test_params:
        sigma = sigma_with_timeout(alpha, m_A, m_chi, v_sub)
        if sigma is None or not np.all(np.isfinite(sigma)) or not np.all(sigma > 0):
            continue
        residuals = np.log10(sigma) - np.log10(s_sub)
        if np.all(np.isfinite(residuals)):
            rmse = np.sqrt(np.mean(residuals**2))
            if rmse < best_rmse:
                best_rmse = rmse
                best_params = (alpha, m_A, m_chi)

    delta = best_rmse - best_full_rmse
    print(f"  Exclude v={v:>6.1f}: RMSE = {best_rmse:.3f}  (delta = {delta:+.3f})")

    results[f'exclude_v_{v}'] = {
        'excluded': float(v),
        'best_rmse': best_rmse,
        'best_params': list(best_params) if best_params else None,
        'delta_from_full': delta,
    }

# Save results
import os
output_file = r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\t166_loo.json"
os.makedirs(os.path.dirname(output_file), exist_ok=True)
with open(output_file, 'w') as f:
    json.dump(results, f, indent=2)

print()
print("=" * 70)
print("INTERPRETATION")
print("=" * 70)
print()
print(f"Full fit RMSE: {best_full_rmse:.3f}")
print()
print("Most influential points (largest |delta|):")
sorted_loo = sorted(
    [(k, v) for k, v in results.items() if k != 'all_8_points'],
    key=lambda x: abs(x[1]['delta_from_full']),
    reverse=True,
)
for k, v in sorted_loo[:3]:
    print(f"  Exclude v={v['excluded']:>6.1f}: delta = {v['delta_from_full']:+.3f}")

print()
print(f"\nResults saved to {output_file}")