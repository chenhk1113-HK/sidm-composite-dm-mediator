"""
T156: Threshold parameter search.

Our Cloud-9 peak requires a parameter set right at the threshold for
bound state formation. This is where Yukawa resonances become large.

Strategy: For each (m_A, m_chi), find alpha_D that puts us at threshold.
Threshold: Ξ = α_D μ / m_A ≈ 1.68 (for first s-wave bound state).
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

# Extend v range to find peaks
v_extended = np.concatenate([v_arr, np.array([50, 75, 150, 250, 350, 600])])

print("=" * 70)
print("T156: Threshold parameter search")
print("=" * 70)
print()

# For each (m_A, m_chi), compute threshold α_D
def threshold_alpha(m_A, m_chi, n_bound=1):
    """Compute α_D for n_bound states.
    Critical Ξ for nth s-wave bound state in Yukawa ≈ 1.68 × n^2 (approx)
    Ξ = α_D × μ_red / m_A
    μ_red = m_chi/2 for self-scattering
    """
    # Approximate from Levinson's theorem
    # Ξ_n ≈ 1.68 × n for s-wave (rough)
    xi_c = 1.68 * n_bound
    mu_red = m_chi / 2
    return xi_c * m_A / mu_red

def sigma_at_threshold(m_A, m_chi, n_bound=1):
    """Compute σ/v at threshold α_D."""
    alpha = threshold_alpha(m_A, m_chi, n_bound)
    try:
        model = sidmkit.YukawaModel(m_chi_gev=m_chi, m_med_gev=m_A, alpha=alpha,
                                      potential=sidmkit.PotentialType.ATTRACTIVE)
        sigma = sidmkit.sigma_over_m(v_extended, model, method='partial_wave')
        return alpha, sigma
    except:
        return alpha, None

# Test parameters at threshold
test_cases = []
for m_A in [0.001, 0.003, 0.01, 0.03]:
    for m_chi in [1.0, 3.0, 10.0, 30.0]:
        for n in [1, 2, 3]:
            test_cases.append((m_A, m_chi, n))

results = []
t0 = time.time()
for m_A, m_chi, n in test_cases:
    alpha, sigma = sigma_at_threshold(m_A, m_chi, n)
    if sigma is not None and np.all(np.isfinite(sigma)) and np.all(sigma > 0):
        # RMSE on data
        valid = np.isfinite(sigma[:8]) & (sigma[:8] > 0)
        if np.sum(valid) >= 3:
            residuals = np.log10(sigma[:8][valid]) - np.log10(s_arr[valid])
            rmse = np.sqrt(np.mean(residuals**2))
            # Find peaks in extended range
            peaks = []
            for i in range(1, len(sigma) - 1):
                if sigma[i] > sigma[i-1] and sigma[i] > sigma[i+1] and sigma[i] > 10:
                    peaks.append((v_extended[i], sigma[i]))

            results.append((m_A, m_chi, n, alpha, rmse, peaks))

results.sort(key=lambda x: x[4])
elapsed = time.time() - t0
print(f"Tested {len(results)} threshold configurations in {elapsed:.1f}s")
print()

print("Top 10:")
print(f"{'m_A':>8} {'m_χ':>6} {'n':>2} {'α_D':>8} {'RMSE':>10} {'peaks':>30}")
for m_A, m_chi, n, alpha, rmse, peaks in results[:10]:
    peak_str = ", ".join([f"{v:.0f}:{s:.1e}" for v, s in peaks[:3]])
    print(f"{m_A:>8.4f} {m_chi:>6.1f} {n:>2} {alpha:>8.3e} {rmse:>10.3f} {peak_str:>30}")

# Show best in detail
if results:
    m_A, m_chi, n, alpha, rmse, peaks = results[0]
    print()
    print(f"BEST FIT: m_A={m_A}, m_χ={m_chi}, n={n}, α_D={alpha:.3e}, RMSE={rmse:.3f}")
    print()
    _, sigma = sigma_at_threshold(m_A, m_chi, n)
    print(f"{'v':>6} {'data':>12} {'pred':>12} {'ratio':>10}")
    for v, s_obs, s_pred in zip(v_arr, s_arr, sigma[:8]):
        ratio = s_obs / s_pred
        print(f"{v:>6.1f} {s_obs:>12.4e} {s_pred:>12.4e} {ratio:>10.4f}")