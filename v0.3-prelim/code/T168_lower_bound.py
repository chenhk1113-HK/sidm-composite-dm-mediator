"""
T168: Alternative phenomenology — treat Cloud-9 as lower bound.

Instead of single point sigma/m = 128 at v=28, treat as a CONSTRAINT:
sigma/m >= 50 at v=28 (lower bound only).

Then check if our 7 remaining points (excluding Cloud-9 from RMSE)
give a better fit without the spike constraint.

This tests: is our model forced to fit a specific high Cloud-9 value,
or does it naturally accommodate the lower bound?
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
print("T168: Cloud-9 as lower-bound constraint (sigma/m >= 50)")
print("=" * 70)
print()

# Exclude Cloud-9 from RMSE
mask_no_c9 = v_arr < 25
v_no_c9 = v_arr[mask_no_c9]
s_no_c9 = s_arr[mask_no_c9]

print(f"Fitting {np.sum(mask_no_c9)} data points (excluding Cloud-9)")
print("Cloud-9 constraint: sigma/m >= 50 at v=28")
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
for alpha in [0.05, 0.1, 0.2, 0.3, 0.5]:
    for m_A in [0.03, 0.1, 0.3]:
        for m_chi in [10, 30, 100]:
            test_params.append((alpha, m_A, m_chi))

# Phase 1: Find best fit on 7 points (excluding Cloud-9)
print("Phase 1: Best fit on 7 points (Cloud-9 excluded)")
print()

best_rmse_7 = float('inf')
best_params_7 = None
best_sigma_7 = None

for alpha, m_A, m_chi in test_params:
    sigma = sigma_with_timeout(alpha, m_A, m_chi, v_no_c9)
    if sigma is None or not np.all(np.isfinite(sigma)) or not np.all(sigma > 0):
        continue
    residuals = np.log10(sigma) - np.log10(s_no_c9)
    if np.all(np.isfinite(residuals)):
        rmse = np.sqrt(np.mean(residuals**2))
        if rmse < best_rmse_7:
            best_rmse_7 = rmse
            best_params_7 = (alpha, m_A, m_chi)
            best_sigma_7 = sigma

print(f"  Best 7-point RMSE: {best_rmse_7:.3f}")
print(f"  Best params: alpha={best_params_7[0]}, mA={best_params_7[1]} GeV, mChi={best_params_7[2]} GeV")
print()

# Phase 2: Check if Cloud-9 constraint (sigma/m >= 50) is satisfied
# Need to evaluate sigma at v=28 using best_params
print("Phase 2: Check Cloud-9 lower-bound constraint at v=28")
print()

v_28 = np.array([28.0])
sigma_28 = sigma_with_timeout(best_params_7[0], best_params_7[1], best_params_7[2], v_28)

if sigma_28 is not None:
    sigma_28_val = sigma_28[0]
    print(f"  Predicted sigma/m at v=28: {sigma_28_val:.4f} cm^2/g")
    print(f"  Constraint: sigma/m >= 50")
    print()

    if sigma_28_val >= 50:
        print("  CONSTRAINT SATISFIED: model is consistent with Cloud-9 floor")
        print("  → Can use this simpler phenomenology (no specific spike value)")
    else:
        print("  CONSTRAINT VIOLATED: model underpredicts at v=28")
        print(f"  Shortfall: {50 - sigma_28_val:.3f} cm^2/g")
        print("  → Need extension (gravothermal, multi-mediator, etc.)")
else:
    print("  Failed to evaluate at v=28")

# Phase 3: Compare with full 8-point fit RMSE
print()
print("Phase 3: Compare 7-point RMSE vs full 8-point RMSE")
print()
sigma_8 = sigma_with_timeout(best_params_7[0], best_params_7[1], best_params_7[2], v_arr)
if sigma_8 is not None:
    residuals_8 = np.log10(sigma_8) - np.log10(s_arr)
    rmse_8 = np.sqrt(np.mean(residuals_8**2))
    print(f"  7-point RMSE (Cloud-9 excluded): {best_rmse_7:.3f}")
    print(f"  8-point RMSE (Cloud-9 included): {rmse_8:.3f}")
    print(f"  Degradation from including Cloud-9: {rmse_8 - best_rmse_7:+.3f}")
    print()
    if rmse_8 > 2.0:
        print("  Including Cloud-9 HURTS the fit significantly")
        print("  → Suggests Cloud-9 is genuinely different physics")
    else:
        print("  Including Cloud-9 does not hurt much")
        print("  → Model can accommodate Cloud-9 floor")

import os
output_file = r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\t168_lower_bound.json"
os.makedirs(os.path.dirname(output_file), exist_ok=True)
with open(output_file, 'w') as f:
    json.dump({
        'best_params_7pt': list(best_params_7) if best_params_7 else None,
        'best_rmse_7pt': best_rmse_7,
        'sigma_at_v28': float(sigma_28_val) if sigma_28 is not None else None,
        'constraint_satisfied': bool(sigma_28_val >= 50) if sigma_28 is not None else None,
        'full_rmse_8pt': float(rmse_8) if sigma_8 is not None else None,
    }, f, indent=2)
print(f"\nResults saved to {output_file}")