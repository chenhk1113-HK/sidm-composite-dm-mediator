"""
T164: Fixed T159 — heavy DM parameter scan with timeout protection.
"""
import numpy as np
import sidmkit
import json
import warnings
warnings.filterwarnings('ignore')
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

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

TIMEOUT = 20

def sigma_with_timeout(alpha, m_A, m_chi, timeout=20):
    def compute():
        model = sidmkit.YukawaModel(m_chi_gev=m_chi, m_med_gev=m_A, alpha=alpha,
                                      potential=sidmkit.PotentialType.ATTRACTIVE)
        return sidmkit.sigma_over_m(v_arr, model, method='partial_wave')

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(compute)
        try:
            return future.result(timeout=timeout)
        except FuturesTimeoutError:
            return None
        except:
            return None


print("=" * 70)
print("T164: Fixed heavy DM parameter scan")
print("=" * 70)
print()

# Heavy DM parameter scan
test_params = []
for alpha in [0.01, 0.05, 0.1, 0.3]:
    for m_A in [0.001, 0.01, 0.1]:
        for m_chi in [100, 300, 1000, 10000]:
            test_params.append((alpha, m_A, m_chi))

print(f"Testing {len(test_params)} heavy-DM configurations (timeout={TIMEOUT}s each)")
print()

results = []
timeouts = 0
t0 = time.time()
for i, (alpha, m_A, m_chi) in enumerate(test_params):
    sigma = sigma_with_timeout(alpha, m_A, m_chi, timeout=TIMEOUT)
    if sigma is None:
        timeouts += 1
    elif np.all(np.isfinite(sigma)) and np.all(sigma > 0):
        residuals = np.log10(sigma) - np.log10(s_arr)
        if np.all(np.isfinite(residuals)):
            rmse = np.sqrt(np.mean(residuals**2))
            results.append((alpha, m_A, m_chi, rmse))

    elapsed = time.time() - t0
    if (i + 1) % 5 == 0:
        print(f"  [{i+1}/{len(test_params)}] {len(results)} valid, {timeouts} timeouts, {elapsed:.0f}s")

results.sort(key=lambda x: x[3])
total_elapsed = time.time() - t0
print(f"\nCompleted: {len(results)} valid in {total_elapsed:.1f}s ({timeouts} timeouts)")
print()

# Save results
import os
output_file = r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\t164_heavy_dm.json"
os.makedirs(os.path.dirname(output_file), exist_ok=True)
with open(output_file, 'w') as f:
    json.dump({
        'best_10': [(float(a), float(mA), float(mC), float(r)) for a, mA, mC, r in results[:10]],
        'total_valid': len(results),
        'total_tested': len(test_params),
        'timeouts': timeouts,
        'elapsed_s': total_elapsed,
    }, f, indent=2)

print("Top 10 heavy-DM configurations:")
print(f"{'rank':>5} {'α_D':>8} {'m_A (GeV)':>10} {'m_χ (GeV)':>10} {'RMSE':>10}")
for i, (alpha, m_A, m_chi, rmse) in enumerate(results[:10]):
    print(f"{i+1:>5} {alpha:>8.3f} {m_A:>10.4f} {m_chi:>10.1f} {rmse:>10.3f}")

# Show best
if results:
    alpha, m_A, m_chi, rmse = results[0]
    print()
    print(f"BEST HEAVY: α_D={alpha}, m_A={m_A} GeV, m_χ={m_chi} GeV, RMSE={rmse:.3f}")
    sigma = sigma_with_timeout(alpha, m_A, m_chi, timeout=30)
    if sigma is not None:
        print(f"{'v':>6} {'data':>12} {'pred':>12} {'ratio':>10}")
        for v, s_obs, s_pred in zip(v_arr, s_arr, sigma):
            ratio = s_obs / s_pred if s_pred > 0 else float('inf')
            print(f"{v:>6.1f} {s_obs:>12.4e} {s_pred:>12.4e} {ratio:>10.4f}")