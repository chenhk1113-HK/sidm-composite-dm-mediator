"""
T171: Resonant SIDM systematic search.

T170 found:
- Resonance works! Sidmkit gives sigma/m ~ 50-90 at v=28 with appropriate params
- But best fit is RMSE=2.19 (magnitude off everywhere else)

Now do systematic search to find parameters that:
1. Give sigma/m >= 50 at v=28 (Cloud-9 satisfied)
2. Match the 7 other points (low-v shape)

Strategy: Wider parameter scan, including:
- (alpha, m_phi, m_chi) combinations that put resonance near v=28
- Allow larger alpha values to get right magnitude
- Focus on getting the resonance peak to coincide with v=28
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
print("T171: Resonant SIDM systematic search")
print("=" * 70)
print()

TIMEOUT = 30
def sigma_with_timeout(alpha, m_A_GeV, m_chi_GeV, v_arr, timeout=30):
    def compute():
        model = sidmkit.YukawaModel(m_chi_gev=m_chi_GeV, m_med_gev=m_A_GeV, alpha=alpha,
                                      potential=sidmkit.PotentialType.ATTRACTIVE)
        return sidmkit.sigma_over_m(v_arr, model, method='partial_wave')
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(compute)
        try:
            return future.result(timeout=timeout)
        except:
            return None

# Systematic search: target resonance near v=28
# For Yukawa: resonance occurs when alpha * m_chi / m_phi ~ integer
# Peak velocity v_peak ~ m_phi * (some constant)

# Wider grid
test_params = []
for alpha in [1e-3, 2e-3, 5e-3, 1e-2, 2e-2, 5e-2]:
    for m_phi_MeV in [1, 2, 3, 5, 7, 10, 15, 20, 30, 50, 100]:
        for m_chi_GeV in [1, 5, 10, 30, 100]:
            test_params.append((alpha, m_phi_MeV / 1000, m_chi_GeV))

print(f"Testing {len(test_params)} parameter combinations")
print()

results = []
t0_start = time.time() if hasattr(time, 'time') else 0

import time
t0 = time.time()

for i, (alpha, m_phi, m_chi) in enumerate(test_params):
    sigma = sigma_with_timeout(alpha, m_phi, m_chi, v_arr, timeout=TIMEOUT)
    if sigma is None or not np.all(np.isfinite(sigma)) or not np.all(sigma > 0):
        continue

    # Full fit RMSE
    residuals = np.log10(sigma) - np.log10(s_arr)
    if np.all(np.isfinite(residuals)):
        rmse_full = np.sqrt(np.mean(residuals**2))

        # Cloud-9 constraint
        v28_idx = np.where(np.isclose(v_arr, 28.0))[0][0]
        sigma_c9 = sigma[v28_idx]

        results.append({
            'alpha': alpha,
            'm_phi_MeV': m_phi * 1000,
            'm_chi_GeV': m_chi,
            'rmse_full': rmse_full,
            'sigma_at_v28': sigma_c9,
            'cloud9_satisfied': sigma_c9 >= 50,
        })

    elapsed = time.time() - t0
    if (i + 1) % 50 == 0:
        print(f"  [{i+1}/{len(test_params)}] {len(results)} valid, {elapsed:.0f}s")

results.sort(key=lambda x: x['rmse_full'])
total_elapsed = time.time() - t0
print(f"\nCompleted: {len(results)} valid fits in {total_elapsed:.1f}s")
print()

# Show top 20
print("Top 20 fits (by RMSE):")
print(f"{'rank':>5} {'alpha':>10} {'m_phi (MeV)':>12} {'m_chi (GeV)':>12} {'RMSE':>10} {'sigma(28)':>10} {'C9?':>5}")
for i, r in enumerate(results[:20]):
    c9 = 'YES' if r['cloud9_satisfied'] else 'no'
    print(f"{i+1:>5} {r['alpha']:>10.3e} {r['m_phi_MeV']:>12.3f} {r['m_chi_GeV']:>12.2f} {r['rmse_full']:>10.3f} {r['sigma_at_v28']:>10.3f} {c9:>5}")

print()
print("=" * 70)
print("INTERPRETATION")
print("=" * 70)
print()

# Find best fit that satisfies Cloud-9
c9_satisfied = [r for r in results if r['cloud9_satisfied']]
if c9_satisfied:
    best_c9 = min(c9_satisfied, key=lambda x: x['rmse_full'])
    print(f"Best fit satisfying Cloud-9 (sigma >= 50 at v=28):")
    print(f"  alpha={best_c9['alpha']:.3e}, m_phi={best_c9['m_phi_MeV']:.3f} MeV, m_chi={best_c9['m_chi_GeV']:.2f} GeV")
    print(f"  RMSE = {best_c9['rmse_full']:.3f}")
    print(f"  sigma/m at v=28 = {best_c9['sigma_at_v28']:.3f}")
else:
    print("NO configurations satisfy Cloud-9 constraint")
    best_c9 = None

print()
print(f"Best overall fit (no Cloud-9 constraint):")
if results:
    best = results[0]
    print(f"  alpha={best['alpha']:.3e}, m_phi={best['m_phi_MeV']:.3f} MeV, m_chi={best['m_chi_GeV']:.2f} GeV")
    print(f"  RMSE = {best['rmse_full']:.3f}")
    print(f"  sigma/m at v=28 = {best['sigma_at_v28']:.3f}")

# Compare with previous best (T163 = 1.408)
print()
print(f"Previous best (T163 KK tower): RMSE = 1.408")
print(f"T165 best with sigma/m(28)=50: RMSE = 1.033")

# Save results
import os
output_file = r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\t171_resonant_search.json"
os.makedirs(os.path.dirname(output_file), exist_ok=True)
with open(output_file, 'w') as f:
    json.dump({
        'best_overall': results[0] if results else None,
        'best_cloud9_satisfied': best_c9,
        'top_20': results[:20],
        'total_valid': len(results),
        'total_tested': len(test_params),
        'elapsed_s': total_elapsed,
    }, f, indent=2, default=float)
print(f"\nResults saved to {output_file}")