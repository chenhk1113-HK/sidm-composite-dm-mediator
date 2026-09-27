"""
T165: Investigate whether the 4000x Cloud-9 spike is required.

Question: Is the specific sigma/m = 128 cm^2/g value at v=28 km/s
required by our fit, or does sigma/m >= 50 (lower bound only) work?

Approach:
1. Refit our 8 data points treating Cloud-9 as sigma/m >= 50 (lower bound only)
2. Refit treating Cloud-9 as sigma/m = 50 (the floor)
3. Refit treating Cloud-9 as sigma/m = 128 (current value)
4. Refit treating Cloud-9 as sigma/m = 1000 (intermediate)
5. Compare fit quality (RMSE) for each
6. Determine which Cloud-9 value gives best fit AND is consistent with literature
"""
import numpy as np
import sidmkit
import json
import warnings
warnings.filterwarnings('ignore')
from concurrent.futures import ThreadPoolExecutor, TimeoutError

# Load our 8 data points
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
print("T165: Robustness of Cloud-9 spike value")
print("=" * 70)
print()
print("Our 8 data points:")
for v, s in zip(v_arr, s_arr):
    print(f"  v={v:>6.1f} km/s: sigma/m = {s:.4e} cm^2/g")
print()

# Test 4 alternative Cloud-9 values
cloud9_values = {
    'lower_bound_50': 50.0,      # Ohana+ 2026 floor
    'intermediate_100': 100.0,
    'current_128': 128.0,
    'high_500': 500.0,
    'extreme_2000': 2000.0,
}

print("Testing different Cloud-9 values:")
print(f"{'label':>22} {'value':>10} {'log10':>10}")

for label, val in cloud9_values.items():
    print(f"{label:>22} {val:>10.1f} {np.log10(val):>10.3f}")
print()

# Build modified data arrays for each Cloud-9 value
results = {}

TIMEOUT = 20
def sigma_with_timeout(alpha, m_A, m_chi, v_arr, timeout=20):
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

# Use best single-Yukawa params from T160 (alpha=0.1, mA=0.1, mChi=30)
# Try slight variations
test_params = []
for alpha in [0.05, 0.1, 0.2, 0.3, 0.5]:
    for m_A in [0.03, 0.1, 0.3]:
        for m_chi in [10, 30, 100]:
            test_params.append((alpha, m_A, m_chi))

print(f"Testing {len(test_params)} single-Yukawa configurations")
print(f"Per evaluation: {TIMEOUT}s timeout")
print()

for label, c9_val in cloud9_values.items():
    # Modify data: replace v=28 value with this Cloud-9 candidate
    s_mod = s_arr.copy()
    v28_idx = np.where(np.isclose(v_arr, 28.0))[0][0]
    s_mod[v28_idx] = c9_val

    best_rmse = float('inf')
    best_params = None

    for i, (alpha, m_A, m_chi) in enumerate(test_params):
        sigma = sigma_with_timeout(alpha, m_A, m_chi, v_arr, timeout=TIMEOUT)
        if sigma is None or not np.all(np.isfinite(sigma)) or not np.all(sigma > 0):
            continue

        residuals = np.log10(sigma) - np.log10(s_mod)
        if np.all(np.isfinite(residuals)):
            rmse = np.sqrt(np.mean(residuals**2))
            if rmse < best_rmse:
                best_rmse = rmse
                best_params = (alpha, m_A, m_chi)

    results[label] = {
        'cloud9_value': c9_val,
        'best_rmse': best_rmse,
        'best_params': best_params,
    }

print("=" * 70)
print("RESULTS: Robustness of Cloud-9 value")
print("=" * 70)
print()
print(f"{'Cloud-9 value':>22} {'Best RMSE':>12} {'Best params (alpha, mA, mChi)':>40}")
for label, r in sorted(results.items(), key=lambda x: x[1]['best_rmse']):
    bp = r['best_params']
    bp_str = f"({bp[0]}, {bp[1]}, {bp[2]})" if bp else "all failed"
    print(f"{label:>22} {r['best_rmse']:>12.3f} {bp_str:>40}")

print()
print("=" * 70)
print("INTERPRETATION")
print("=" * 70)
print()
best_label = min(results, key=lambda x: results[x]['best_rmse'])
best_rmse = results[best_label]['best_rmse']
worst_rmse = max(r['best_rmse'] for r in results.values())
spread = worst_rmse - best_rmse

print(f"Best fit RMSE: {best_rmse:.3f} (with Cloud-9 = {results[best_label]['cloud9_value']})")
print(f"Worst fit RMSE: {worst_rmse:.3f}")
print(f"Spread: {spread:.3f}")
print()
if spread < 0.5:
    print("INTERPRETATION: Different Cloud-9 values give SIMILAR fits.")
    print("This suggests our 4000x spike is NOT critical to the fit.")
    print("A simpler model with sigma/m = 50 floor would work equally well.")
else:
    print("INTERPRETATION: Different Cloud-9 values give DIFFERENT fits.")
    print("The 4000x spike value MATTERS for our model.")
    print("We should document the sensitivity.")

# Save results
import os
output_file = r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\t165_cloud9_robustness.json"
os.makedirs(os.path.dirname(output_file), exist_ok=True)
with open(output_file, 'w') as f:
    json.dump({
        label: {
            'cloud9_value': r['cloud9_value'],
            'best_rmse': r['best_rmse'],
            'best_params': list(r['best_params']) if r['best_params'] else None,
        }
        for label, r in results.items()
    }, f, indent=2)
print(f"\nResults saved to {output_file}")