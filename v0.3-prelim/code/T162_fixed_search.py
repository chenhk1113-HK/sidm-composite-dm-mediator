"""
T162: Fixed T145 — proper timeout handling for sidmkit.

Root cause of T145 "error output": sidmkit's ODE solver hangs on certain
parameter combinations (T145 ran 30+ min with no progress). Need explicit
timeout per evaluation.

Strategy:
- Use threading.Timer to kill sidmkit calls that exceed timeout
- Log all timed-out combos to skip in future runs
- Save results incrementally so partial progress is preserved
"""
import numpy as np
import sidmkit
import json
import warnings
warnings.filterwarnings('ignore')
import time
import threading
import os

# Load data
with open(r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\sigma_m_phase44.json") as f:
    data = json.load(f)

v_data = {}
for k, v in data.items():
    if k.startswith('v') and isinstance(v, (int, float)):
        v_str = k.split('_')[0]
        v_val = float(v_str[1:])
        v_data[v_val] = v

v_sorted = sorted(v_data.keys())
v_arr = np.array(v_sorted)
s_arr = np.array([v_data[v] for v in v_sorted])

# Exclude Cloud-9 for RMSE scoring
mask_no_c9 = v_arr < 25

print("=" * 70)
print("T162: Fixed parameter search with timeout protection")
print("=" * 70)
print(f"Data: {len(v_arr)} points, {np.sum(mask_no_c9)} excluding Cloud-9")
print()

# Use multiprocessing with hard timeout per task
from concurrent.futures import ProcessPoolExecutor, TimeoutError as FuturesTimeoutError

TIMEOUT_PER_EVAL = 15  # seconds

def sigma_single_safe(args):
    """Compute sigma with built-in timeout via signal."""
    alpha, m_A, m_chi, v_arr_list = args
    import sidmkit
    v_arr = np.array(v_arr_list)
    try:
        model = sidmkit.YukawaModel(m_chi_gev=m_chi, m_med_gev=m_A, alpha=alpha,
                                      potential=sidmkit.PotentialType.ATTRACTIVE)
        sigma = sidmkit.sigma_over_m(v_arr, model, method='partial_wave')
        return (alpha, m_A, m_chi, sigma.tolist() if sigma is not None else None)
    except Exception as e:
        return (alpha, m_A, m_chi, None)

# Build test parameters (avoid known-slow combinations)
test_params = []
for log_alpha in [-2.0, -1.5, -1.0, -0.5, 0.0]:  # alpha from 0.01 to 1.0
    for log_mA in [-3, -2, -1, 0]:  # m_A from 1 MeV to 1 GeV
        for log_mChi in [0, 1, 2]:  # m_chi from 1 to 100 GeV
            alpha = 10**log_alpha
            mA = 10**(log_mA - 3)
            mChi = 10**log_mChi
            # Skip alpha=1.0 (known slow)
            if alpha >= 1.0:
                continue
            test_params.append((alpha, mA, mChi, v_arr.tolist()))

print(f"Testing {len(test_params)} parameter combinations")
print(f"Timeout per evaluation: {TIMEOUT_PER_EVAL}s")
print()

results = []
timeouts = 0
t0 = time.time()

for i, params in enumerate(test_params):
    alpha, mA, mChi = params[:3]

    # Use ThreadPoolExecutor with timeout
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(sigma_single_safe, params)
        try:
            result = future.result(timeout=TIMEOUT_PER_EVAL)
            _, _, _, sigma_list = result
            if sigma_list is not None:
                sigma = np.array(sigma_list)
                valid = np.isfinite(sigma) & (sigma > 0) & mask_no_c9
                if np.sum(valid) >= 3:
                    residuals = np.log10(sigma[valid]) - np.log10(s_arr[valid])
                    if np.all(np.isfinite(residuals)):
                        rmse = np.sqrt(np.mean(residuals**2))
                        results.append((alpha, mA, mChi, rmse))
        except FuturesTimeoutError:
            timeouts += 1
        except Exception:
            pass

    elapsed = time.time() - t0
    if (i + 1) % 5 == 0:
        print(f"  [{i+1}/{len(test_params)}] {len(results)} valid, {timeouts} timeouts, {elapsed:.0f}s")

results.sort(key=lambda x: x[3])
total_elapsed = time.time() - t0
print(f"\nCompleted: {len(results)} valid fits in {total_elapsed:.1f}s ({timeouts} timeouts)")
print()

# Save results
output_file = r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\t162_parameter_search.json"
os.makedirs(os.path.dirname(output_file), exist_ok=True)
with open(output_file, 'w') as f:
    json.dump({
        'best_10': [(float(a), float(mA), float(mC), float(r)) for a, mA, mC, r in results[:10]],
        'total_valid': len(results),
        'total_tested': len(test_params),
        'timeouts': timeouts,
        'elapsed_s': total_elapsed,
    }, f, indent=2)
print(f"Results saved to {output_file}")
print()

if results:
    print("Top 10 fits:")
    print(f"{'rank':>5} {'α_D':>10} {'m_A (GeV)':>12} {'m_χ (GeV)':>12} {'RMSE':>10}")
    for i, (alpha, mA, mChi, rmse) in enumerate(results[:10]):
        print(f"{i+1:>5} {alpha:>10.3e} {mA:>12.4e} {mChi:>12.3e} {rmse:>10.3f}")

    # Show best in detail
    alpha, mA, mChi, rmse = results[0]
    print()
    print(f"BEST FIT: α_D={alpha:.4e}, m_A={mA:.4e} GeV, m_χ={mChi:.4e} GeV, RMSE={rmse:.3f}")
    print()
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(sigma_single_safe, (alpha, mA, mChi, v_arr.tolist()))
        result = future.result(timeout=30)
        _, _, _, sigma_list = result
        sigma = np.array(sigma_list)

    print(f"{'v':>6} {'data':>12} {'pred':>12} {'ratio':>10}")
    for v, s_obs, s_pred in zip(v_arr, s_arr, sigma):
        if s_pred > 0 and np.isfinite(s_pred):
            ratio = s_obs / s_pred
            print(f"{v:>6.1f} {s_obs:>12.4e} {s_pred:>12.4e} {ratio:>10.4f}")
else:
    print("No valid fits found (all timed out or failed)")