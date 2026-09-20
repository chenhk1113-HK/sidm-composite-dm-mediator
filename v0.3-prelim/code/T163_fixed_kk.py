"""
T163: Fixed T151 — KK tower optimization with proper timeout.

Root cause of T151 issue: no per-evaluation timeout, sidmkit hangs.
T161 already found best RMSE=1.411, but let me re-run T151 with
proper timeout and wider search to confirm or beat that result.
"""
import numpy as np
import sidmkit
import json
import warnings
warnings.filterwarnings('ignore')
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

# Load data
with open(r"C:\Users/lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\sigma_m_phase44.json") as f:
    data = json.load(f)

v_data = {}
for k, v in data.items():
    if k.startswith('v') and isinstance(v, (int, float)):
        v_str = k.split('_')[0]
        v_val = float(v_str[1:])
        v_data[v_val] = v

v_arr = np.array(sorted(v_data.keys()))
s_arr = np.array([v_data[v] for v in v_arr])

TIMEOUT_PER_KK = 30  # seconds per full KK computation

def sigma_kk_with_timeout(v_arr, alpha_D, m_0, r_mass, m_chi_GeV, n_modes, timeout=30):
    """KK tower with hard timeout per full computation."""
    def compute_kk():
        sigma_total = np.zeros_like(v_arr, dtype=float)
        for n in range(1, n_modes + 1):
            m_n = m_0 * (r_mass ** n)
            c_n = 1.0 / n
            model = sidmkit.YukawaModel(m_chi_gev=m_chi_GeV, m_med_gev=m_n, alpha=alpha_D * c_n,
                                          potential=sidmkit.PotentialType.ATTRACTIVE)
            sigma_n = sidmkit.sigma_over_m(v_arr, model, method='partial_wave')
            sigma_total += sigma_n
        return sigma_total

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(compute_kk)
        try:
            return future.result(timeout=timeout)
        except FuturesTimeoutError:
            return None
        except:
            return None


print("=" * 70)
print("T163: Fixed KK tower optimization")
print("=" * 70)
print()

# T151's parameter grid (focused on best region)
test_params = []
for alpha in [0.05, 0.1, 0.2, 0.3]:
    for m_0 in [0.001, 0.005, 0.01, 0.03, 0.1, 0.3]:
        for r in [1.5, 2.0, 3.0]:
            for n_modes in [2, 3, 5]:
                m_chi = 30.0  # from T161 best
                test_params.append((alpha, m_0, r, n_modes))

print(f"Testing {len(test_params)} KK configurations")
print(f"Timeout per KK evaluation: {TIMEOUT_PER_KK}s")
print()

results = []
timeouts = 0
t0 = time.time()
for i, (alpha, m_0, r, n_modes) in enumerate(test_params):
    sigma = sigma_kk_with_timeout(v_arr, alpha, m_0, r, 30.0, n_modes, timeout=TIMEOUT_PER_KK)
    if sigma is None:
        timeouts += 1
    elif np.all(np.isfinite(sigma)) and np.all(sigma > 0):
        residuals = np.log10(sigma) - np.log10(s_arr)
        if np.all(np.isfinite(residuals)):
            rmse = np.sqrt(np.mean(residuals**2))
            results.append((alpha, m_0, r, n_modes, rmse))

    elapsed = time.time() - t0
    if (i + 1) % 10 == 0:
        print(f"  [{i+1}/{len(test_params)}] {len(results)} valid, {timeouts} timeouts, {elapsed:.0f}s")

results.sort(key=lambda x: x[4])
total_elapsed = time.time() - t0
print(f"\nCompleted: {len(results)} valid in {total_elapsed:.1f}s ({timeouts} timeouts)")
print()

# Save results
import os
output_file = r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\t163_kk_optimization.json"
os.makedirs(os.path.dirname(output_file), exist_ok=True)
with open(output_file, 'w') as f:
    json.dump({
        'best_10': [(float(a), float(m), float(r), int(n), float(rmse)) for a, m, r, n, rmse in results[:10]],
        'total_valid': len(results),
        'total_tested': len(test_params),
        'timeouts': timeouts,
        'elapsed_s': total_elapsed,
    }, f, indent=2)

print("Top 10 KK configurations:")
print(f"{'rank':>5} {'α_D':>8} {'m_0 (GeV)':>10} {'r':>5} {'n':>3} {'RMSE':>10}")
for i, (alpha, m_0, r, n_modes, rmse) in enumerate(results[:10]):
    print(f"{i+1:>5} {alpha:>8.3f} {m_0:>10.4f} {r:>5.2f} {n_modes:>3} {rmse:>10.3f}")

# Show best
if results:
    alpha, m_0, r, n_modes, rmse = results[0]
    print()
    print(f"BEST KK: α_D={alpha}, m_0={m_0} GeV, r={r}, n_modes={n_modes}, RMSE={rmse:.3f}")
    sigma = sigma_kk_with_timeout(v_arr, alpha, m_0, r, 30.0, n_modes, timeout=60)
    if sigma is not None:
        print(f"{'v':>6} {'data':>12} {'pred':>12} {'ratio':>10}")
        for v, s_obs, s_pred in zip(v_arr, s_arr, sigma):
            ratio = s_obs / s_pred if s_pred > 0 else float('inf')
            print(f"{v:>6.1f} {s_obs:>12.4e} {s_pred:>12.4e} {ratio:>10.4f}")