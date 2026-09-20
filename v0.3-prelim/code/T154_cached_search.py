"""
T154: Cached + incremental parameter search.

Strategy:
1. Cache sidmkit results so we don't re-compute
2. Use NESTED LOOP starting from low-v (which we know how to fit)
3. Add KK modes incrementally
4. Stop early if we hit a good fit (RMSE < 1)

Use only parameters where sidmkit converges (avoid hanging).
"""
import numpy as np
import sidmkit
import warnings
warnings.filterwarnings('ignore')
import json
import time
import os

# Load data
with open(r"C:\Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results/sigma_m_phase44.json") as f:
    data = json.load(f)

v_data = {}
for k, v in data.items():
    if k.startswith('v') and isinstance(v, (int, float)):
        v_str = k.split('_')[0]
        v_val = float(v_str[1:])
        v_data[v_val] = v

v_arr = np.array(sorted(v_data.keys()))
s_arr = np.array([v_data[v] for v in v_arr])

# Cache file
cache_file = r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\cache\sidmkit_predictions.npz"
os.makedirs(os.path.dirname(cache_file), exist_ok=True)

# Try loading cache
cache = {}
if os.path.exists(cache_file):
    try:
        cached = np.load(cache_file, allow_pickle=True)
        cache = dict(cached)
        print(f"Loaded {len(cache)} cached predictions")
    except:
        pass


def sigma_kk_cached(v_arr, alpha_D, m_0_GeV, r_mass, m_chi_GeV, n_modes):
    """KK tower with caching."""
    key = (round(alpha_D, 4), round(m_0_GeV, 6), round(r_mass, 2),
           round(m_chi_GeV, 4), n_modes)
    if key in cache:
        return cache[key]

    sigma_total = np.zeros_like(v_arr, dtype=float)
    for n in range(1, n_modes + 1):
        m_n = m_0_GeV * (r_mass ** n)
        c_n = 1.0 / n
        try:
            model = sidmkit.YukawaModel(m_chi_gev=m_chi_GeV, m_med_gev=m_n, alpha=alpha_D * c_n,
                                          potential=sidmkit.PotentialType.ATTRACTIVE)
            sigma_n = sidmkit.sigma_over_m(v_arr, model, method='partial_wave')
            sigma_total += sigma_n
        except:
            return None

    cache[key] = sigma_total
    return sigma_total


def rmse_log(sigma, target):
    valid = np.isfinite(sigma) & (sigma > 0) & (target > 0)
    if np.sum(valid) < 3:
        return 1e9
    residuals = np.log10(sigma[valid]) - np.log10(target[valid])
    if not np.all(np.isfinite(residuals)):
        return 1e9
    return np.sqrt(np.mean(residuals**2))


# Phase 1: small parameter space, fast search
print("=" * 70)
print("T154: Cached parameter search")
print("=" * 70)
print()

t0 = time.time()
results = []
tested = 0

# First do single Yukawa (most reliable)
print("Phase 1: Single Yukawa parameter search")
for alpha in [0.05, 0.1, 0.2, 0.3, 0.5]:
    for m_A in [0.001, 0.003, 0.01, 0.03, 0.1]:
        for m_chi in [0.5, 1.0, 3.0, 10.0]:
            try:
                sigma = sigma_kk_cached(v_arr, alpha, m_A, 1.0, m_chi, 1)  # n_modes=1 = single
                if sigma is not None:
                    rmse = rmse_log(sigma, s_arr)
                    results.append((alpha, m_A, 1.0, 1, rmse))
                    tested += 1
            except:
                pass

results.sort(key=lambda x: x[4])
elapsed = time.time() - t0
print(f"  Tested {tested} single-Yukawa in {elapsed:.1f}s, best RMSE = {results[0][4]:.3f}")
print(f"  Best: alpha={results[0][0]}, mA={results[0][1]}, mChi=varies, RMSE={results[0][4]:.3f}")

# Save cache
np.savez(cache_file, **cache)
print(f"\nCache now has {len(cache)} entries")