"""
T156-fast: Reduced threshold parameter search.
"""
import numpy as np
import sidmkit
import warnings
warnings.filterwarnings('ignore')
import json
import time

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

# Wider v range
v_extended = np.concatenate([v_arr, np.array([50, 75, 200, 600])])

print("=" * 70)
print("T156-fast: Threshold search")
print("=" * 70)
print()

# Threshold α_D for first 3 s-wave bound states
def threshold_alpha(m_A, m_chi, n_bound=1):
    mu_red = m_chi / 2
    xi_c = 1.68 * n_bound
    return xi_c * m_A / mu_red

# Just a few key test cases
test_cases = [
    (0.001, 1.0, 1),
    (0.001, 3.0, 1),
    (0.001, 10.0, 1),
    (0.01, 1.0, 1),
    (0.01, 10.0, 1),
    (0.01, 30.0, 1),
    (0.03, 10.0, 1),
    (0.001, 1.0, 2),
    (0.001, 10.0, 2),
    (0.01, 30.0, 2),
]

results = []
t0 = time.time()
for m_A, m_chi, n in test_cases:
    alpha = threshold_alpha(m_A, m_chi, n)
    try:
        model = sidmkit.YukawaModel(m_chi_gev=m_chi, m_med_gev=m_A, alpha=alpha,
                                      potential=sidmkit.PotentialType.ATTRACTIVE)
        sigma = sidmkit.sigma_over_m(v_extended, model, method='partial_wave')

        if sigma is not None and np.all(np.isfinite(sigma)) and np.all(sigma > 0):
            # RMSE on data
            valid = np.isfinite(sigma[:8]) & (sigma[:8] > 0)
            if np.sum(valid) >= 5:
                residuals = np.log10(sigma[:8][valid]) - np.log10(s_arr[valid])
                rmse = np.sqrt(np.mean(residuals**2))

                # Find peaks in extended range
                peaks = []
                for i in range(1, len(sigma) - 1):
                    if sigma[i] > sigma[i-1] and sigma[i] > sigma[i+1] and sigma[i] > 1:
                        peaks.append((v_extended[i], sigma[i]))

                results.append((m_A, m_chi, n, alpha, rmse, peaks))
    except:
        pass

results.sort(key=lambda x: x[4])
elapsed = time.time() - t0
print(f"Tested {len(results)} configurations in {elapsed:.1f}s")
print()

print("Results:")
print(f"{'m_A':>10} {'m_χ':>6} {'n':>2} {'α_D':>10} {'RMSE':>10} {'peaks':>40}")
for m_A, m_chi, n, alpha, rmse, peaks in results:
    peak_str = ", ".join([f"v={v:.0f}:σ={s:.1e}" for v, s in peaks[:3]])
    print(f"{m_A:>10.4f} {m_chi:>6.1f} {n:>2} {alpha:>10.3e} {rmse:>10.3f} {peak_str:>40}")

# Show best
if results:
    m_A, m_chi, n, alpha, rmse, peaks = results[0]
    print()
    print(f"BEST: m_A={m_A}, m_χ={m_chi}, n={n}, α_D={alpha:.3e}, RMSE={rmse:.3f}")
    _, sigma_best = None, sidmkit.sigma_over_m(v_arr, sidmkit.YukawaModel(m_chi_gev=m_chi, m_med_gev=m_A, alpha=alpha,
                                      potential=sidmkit.PotentialType.ATTRACTIVE), method='partial_wave')
    print(f"{'v':>6} {'data':>12} {'pred':>12} {'ratio':>10}")
    for v, s_obs, s_pred in zip(v_arr, s_arr, sigma_best):
        ratio = s_obs / s_pred if s_pred > 0 else float('inf')
        print(f"{v:>6.1f} {s_obs:>12.4e} {s_pred:>12.4e} {ratio:>10.4f}")