"""
T169: Use published sigma/m range [50, 21000] cm^2/g (from Ohana+ 2026)
and find best model parameters that satisfy this constraint.

This tests whether our phenomenology is compatible with the full
published uncertainty range, not just our specific 128 cm^2/g point.
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
print("T169: Compatibility with published Cloud-9 range")
print("=" * 70)
print()
print("Published sigma/m range at v=28 km/s: [50, 21000] cm^2/g")
print("(Ohana, Zhang & Yu 2026, arXiv:2608.04362)")
print()

# Test each value in the published range
test_values = [50, 100, 200, 500, 1000, 5000, 21000]

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
for alpha in [0.05, 0.1, 0.2, 0.3, 0.5]:
    for m_A in [0.03, 0.1, 0.3]:
        for m_chi in [10, 30, 100]:
            test_params.append((alpha, m_A, m_chi))

print(f"Testing {len(test_values)} Cloud-9 values x {len(test_params)} params = {len(test_values)*len(test_params)} combinations")
print()

results = []

for c9_val in test_values:
    s_mod = s_arr.copy()
    v28_idx = np.where(np.isclose(v_arr, 28.0))[0][0]
    s_mod[v28_idx] = c9_val

    best_rmse = float('inf')
    best_params = None

    for alpha, m_A, m_chi in test_params:
        sigma = sigma_with_timeout(alpha, m_A, m_chi, v_arr)
        if sigma is None or not np.all(np.isfinite(sigma)) or not np.all(sigma > 0):
            continue
        residuals = np.log10(sigma) - np.log10(s_mod)
        if np.all(np.isfinite(residuals)):
            rmse = np.sqrt(np.mean(residuals**2))
            if rmse < best_rmse:
                best_rmse = rmse
                best_params = (alpha, m_A, m_chi)

    results.append({
        'cloud9_value': c9_val,
        'best_rmse': best_rmse,
        'best_params': list(best_params) if best_params else None,
    })
    print(f"  Cloud-9 = {c9_val:>6.0f}: RMSE = {best_rmse:.3f} (params: {best_params})")

# Check if all values give similar RMSE → robustness
rmses = [r['best_rmse'] for r in results]
spread = max(rmses) - min(rmses)

print()
print("=" * 70)
print("ROBUSTNESS ANALYSIS")
print("=" * 70)
print()
print(f"Cloud-9 range tested: [50, 21000] cm^2/g")
print(f"RMSE spread: {min(rmses):.3f} to {max(rmses):.3f} (delta {spread:.3f})")
print()

if spread < 0.5:
    print("VERDICT: Model is ROBUST across full Cloud-9 range")
    print("  → Any value in [50, 21000] gives similar fit quality")
    print("  → Safe to use simple phenomenology")
elif spread < 1.0:
    print("VERDICT: Model is MODERATELY ROBUST")
    print("  → Some variation across Cloud-9 range")
    print("  → But no value is catastrophically bad")
else:
    print("VERDICT: Model is SENSITIVE to Cloud-9 value")
    print("  → Need to investigate which value is most physically motivated")

# Identify which Cloud-9 value gives best fit
best = min(results, key=lambda x: x['best_rmse'])
print()
print(f"Best Cloud-9 value: {best['cloud9_value']} cm^2/g (RMSE = {best['best_rmse']:.3f})")

import os
output_file = r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\t169_published_range.json"
os.makedirs(os.path.dirname(output_file), exist_ok=True)
with open(output_file, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nResults saved to {output_file}")