"""
T172: Physics-guided resonant SIDM search.

T170 found resonance works (sigma/m=52 at v=28 achievable).
T171 is slow (330 configs with 30s timeout each).

Insight from Tran+ 2024: resonance peak velocity depends on
alpha * m_chi / m_phi (dimensionless coupling parameter).

For attractive Yukawa, bound states form when this parameter
exceeds critical values. The peak velocity is approximately:
v_peak ~ m_phi / (alpha * m_chi) * (some constant)

Strategy:
1. For each target velocity, calculate required alpha*m_chi/m_phi
2. Test only those combinations
3. Much faster than blind grid
"""
import numpy as np
import sidmkit
import json
import warnings
warnings.filterwarnings('ignore')
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import time

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
print("T172: Physics-guided resonant SIDM search")
print("=" * 70)
print()

TIMEOUT = 20
def sigma_with_timeout(alpha, m_A_GeV, m_chi_GeV, v_arr, timeout=20):
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

# Resonance condition: alpha * m_chi / m_phi ~ n (integer)
# For v_peak ~ 28 km/s, need to scan over different integer n
# Also vary the ratio m_phi / m_chi to find peak velocity

# Strategy 1: Fix alpha, vary m_chi and m_phi to scan coupling
# Strategy 2: For target peak velocity, scan (alpha, m_chi, m_phi) systematically

# Target: peak near v=28, but also need to match other velocities
# The resonance peak has width ~few km/s, so position matters

# Try a focused grid
test_params = []
# (alpha, m_phi_MeV, m_chi_GeV)
# Focus on parameters that gave sigma/m near 50 at v=28 from T170

# From T170:
# alpha=1.6e-3, m_phi=5.7 MeV, m_chi=10 GeV -> sigma/v=28 = 52.7 (close!)
# alpha=1.6e-3, m_phi=3.0 MeV, m_chi=31.8 GeV -> 90.9

# Try variations around these
configs = [
    # Vary alpha around 1.6e-3 with m_phi=5.7, m_chi=10
    (1e-3, 5.7, 10),
    (1.2e-3, 5.7, 10),
    (1.4e-3, 5.7, 10),
    (1.6e-3, 5.7, 10),  # T170 best
    (1.8e-3, 5.7, 10),
    (2e-3, 5.7, 10),
    (2.5e-3, 5.7, 10),
    (3e-3, 5.7, 10),
    (5e-3, 5.7, 10),
    # Vary m_phi at fixed alpha=1.6e-3, m_chi=10
    (1.6e-3, 3, 10),
    (1.6e-3, 4, 10),
    (1.6e-3, 5, 10),
    (1.6e-3, 5.7, 10),  # T170 best
    (1.6e-3, 7, 10),
    (1.6e-3, 10, 10),
    (1.6e-3, 15, 10),
    # Vary m_chi at fixed alpha=1.6e-3, m_phi=5.7
    (1.6e-3, 5.7, 3),
    (1.6e-3, 5.7, 5),
    (1.6e-3, 5.7, 8),
    (1.6e-3, 5.7, 10),  # T170 best
    (1.6e-3, 5.7, 15),
    (1.6e-3, 5.7, 20),
    # Try heavier DM with different m_phi
    (1e-2, 20, 50),
    (1e-2, 30, 50),
    (5e-3, 20, 30),
    (5e-3, 30, 30),
    (1e-2, 50, 100),
    (2e-2, 50, 100),
    # Additional attempts to get magnitude right at low-v
    (5e-2, 50, 100),  # Higher alpha for higher magnitude
    (5e-2, 100, 100),
    (1e-1, 50, 100),  # Very high alpha
    (1e-1, 100, 100),
    (2e-1, 100, 100),
]

print(f"Testing {len(configs)} focused configurations")
print()

results = []
t0 = time.time()

for i, (alpha, m_phi_MeV, m_chi_GeV) in enumerate(configs):
    m_phi_GeV = m_phi_MeV / 1000
    sigma = sigma_with_timeout(alpha, m_phi_GeV, m_chi_GeV, v_arr, timeout=TIMEOUT)
    if sigma is None or not np.all(np.isfinite(sigma)) or not np.all(sigma > 0):
        continue

    residuals = np.log10(sigma) - np.log10(s_arr)
    if np.all(np.isfinite(residuals)):
        rmse = np.sqrt(np.mean(residuals**2))

        v28_idx = np.where(np.isclose(v_arr, 28.0))[0][0]
        sigma_c9 = sigma[v28_idx]

        # Compute ratio at v=3 (low-v)
        v3_idx = np.where(np.isclose(v_arr, 3.0))[0][0]
        ratio_v3 = s_arr[v3_idx] / sigma[v3_idx] if sigma[v3_idx] > 0 else float('inf')

        results.append({
            'alpha': alpha,
            'm_phi_MeV': m_phi_MeV,
            'm_chi_GeV': m_chi_GeV,
            'rmse_full': rmse,
            'sigma_at_v28': sigma_c9,
            'sigma_at_v3': sigma[v3_idx],
            'ratio_v3': ratio_v3,
            'cloud9_satisfied': sigma_c9 >= 50,
        })

elapsed = time.time() - t0
print(f"Completed {len(results)} fits in {elapsed:.0f}s")
print()

# Sort by RMSE
results.sort(key=lambda x: x['rmse_full'])

print("Top 15 fits:")
print(f"{'rank':>5} {'alpha':>10} {'m_phi (MeV)':>12} {'m_chi (GeV)':>12} {'RMSE':>10} {'sigma(28)':>10} {'sigma(3)':>10} {'C9?':>5}")
for i, r in enumerate(results[:15]):
    c9 = 'YES' if r['cloud9_satisfied'] else 'no'
    print(f"{i+1:>5} {r['alpha']:>10.3e} {r['m_phi_MeV']:>12.3f} {r['m_chi_GeV']:>12.2f} {r['rmse_full']:>10.3f} {r['sigma_at_v28']:>10.3f} {r['sigma_at_v3']:>10.3f} {c9:>5}")

print()
print("=" * 70)
print("INTERPRETATION")
print("=" * 70)
print()

# Best Cloud-9-satisfying
c9_ok = [r for r in results if r['cloud9_satisfied']]
if c9_ok:
    best_c9 = min(c9_ok, key=lambda x: x['rmse_full'])
    print(f"Best fit with Cloud-9 (sigma >= 50 at v=28):")
    print(f"  params: alpha={best_c9['alpha']:.3e}, m_phi={best_c9['m_phi_MeV']:.3f} MeV, m_chi={best_c9['m_chi_GeV']:.2f} GeV")
    print(f"  RMSE = {best_c9['rmse_full']:.3f}")
    print(f"  sigma/v=28 = {best_c9['sigma_at_v28']:.3f}")
    print(f"  sigma/v=3 = {best_c9['sigma_at_v3']:.3f}")
    print(f"  ratio at v=3 (data/pred) = {best_c9['ratio_v3']:.3f}")
else:
    print("NO configurations satisfy Cloud-9 in this grid")

if results:
    best = results[0]
    print()
    print(f"Best overall fit (no Cloud-9 constraint):")
    print(f"  params: alpha={best['alpha']:.3e}, m_phi={best['m_phi_MeV']:.3f} MeV, m_chi={best['m_chi_GeV']:.2f} GeV")
    print(f"  RMSE = {best['rmse_full']:.3f}")
    print(f"  sigma/v=28 = {best['sigma_at_v28']:.3f}")

# Save results
import os
output_file = r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\t172_physics_guided.json"
os.makedirs(os.path.dirname(output_file), exist_ok=True)
with open(output_file, 'w') as f:
    json.dump({
        'best_overall': results[0] if results else None,
        'best_cloud9_satisfied': min(c9_ok, key=lambda x: x['rmse_full']) if c9_ok else None,
        'all_results': results,
        'total_tested': len(configs),
    }, f, indent=2, default=float)
print(f"\nResults saved to {output_file}")