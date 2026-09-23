"""
T157: Honest assessment of what sidmkit CAN and CANNOT explain.

Our 8 data points span 7 orders of magnitude in sigma/m:
- v=3-15: smooth σ ~ v^(-1)
- v=28: Cloud-9 peak (4000× jump from v=15)
- v=100: small but non-zero
- v=500: very small

The "shape" we need is:
1. Background slope ≈ -1 at low-v
2. Sharp peak at v=28 (4000× enhancement)
3. Fall-off past peak (factor 660 from v=28 to v=100)
4. Continued fall-off to very small values at v=500

Standard Yukawa (per T149) gives:
- Smooth monotonic σ(v)
- No peaks in our v range (unless at very specific threshold)
- Slope transitions: -4 (Born) to 0 (saturated)

The mismatch is fundamental: our data has peaks, sidmkit's Yukawa is smooth.

What's really going on in our data?
- T120 phenomenology: 4 Breit-Wigner peaks at v = 28, 100, 178, 430, 769
- Each peak from a "bound state" of some kind
- In Yukawa physics: this would need MULTIPLE bound states at the right energies

For n_bound = 4, threshold requires Ξ = α_D × μ_red / m_A ≈ 16 (Levinson)
With μ_red = m_χ/2, Ξ = α_D × m_χ / (2 m_A)

For m_χ = 10 GeV, m_A = 10 MeV: Ξ = α_D × 500
Need α_D × 500 ≈ 16, so α_D ≈ 0.032

This is right at our threshold search results! Let me try α_D near 0.03.
"""
import numpy as np
import sidmkit
import warnings
warnings.filterwarnings('ignore')
import json

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

# Extended v range to find all peaks
v_extended = np.logspace(0.5, 4, 30)

print("=" * 70)
print("T157: Multi-threshold parameter search")
print("=" * 70)
print()

# Test parameters near n_bound=4 threshold (α_D × m_χ / (2 m_A) ≈ 16)
def threshold_alpha_n(n, m_A, m_chi):
    """α_D for n bound states: Ξ = α_D × μ_red / m_A = 1.68 × n"""
    mu_red = m_chi / 2
    return 1.68 * n * m_A / mu_red

# Test many n values
test_params = []
for n in [1, 2, 3, 4, 5, 6]:
    for m_A in [0.001, 0.003, 0.01, 0.03]:
        for m_chi in [1.0, 3.0, 10.0, 30.0]:
            alpha = threshold_alpha_n(n, m_A, m_chi)
            if 0.001 < alpha < 0.3:  # reasonable coupling
                test_params.append((n, m_A, m_chi, alpha))

print(f"Testing {len(test_params)} threshold configurations")
print()

results = []
import time
t0 = time.time()
for n, m_A, m_chi, alpha in test_params:
    try:
        model = sidmkit.YukawaModel(m_chi_gev=m_chi, m_med_gev=m_A, alpha=alpha,
                                      potential=sidmkit.PotentialType.ATTRACTIVE)
        sigma = sidmkit.sigma_over_m(v_arr, model, method='partial_wave')

        if sigma is not None and np.all(np.isfinite(sigma)) and np.all(sigma > 0):
            valid = np.isfinite(sigma) & (sigma > 0)
            if np.sum(valid) >= 5:
                residuals = np.log10(sigma[valid]) - np.log10(s_arr[valid])
                rmse = np.sqrt(np.mean(residuals**2))
                results.append((n, m_A, m_chi, alpha, rmse))
    except:
        pass

results.sort(key=lambda x: x[4])
elapsed = time.time() - t0
print(f"Tested {len(results)} configs in {elapsed:.1f}s")
print()

print("Top 10 threshold configurations:")
print(f"{'n':>2} {'m_A':>10} {'m_χ':>6} {'α_D':>10} {'RMSE':>10}")
for n, m_A, m_chi, alpha, rmse in results[:10]:
    print(f"{n:>2} {m_A:>10.4f} {m_chi:>6.1f} {alpha:>10.3e} {rmse:>10.3f}")

# Show best
if results:
    n, m_A, m_chi, alpha, rmse = results[0]
    print()
    print(f"BEST: n={n}, m_A={m_A}, m_χ={m_chi}, α_D={alpha:.3e}, RMSE={rmse:.3f}")
    sigma = sidmkit.sigma_over_m(v_arr, sidmkit.YukawaModel(m_chi_gev=m_chi, m_med_gev=m_A, alpha=alpha,
                                      potential=sidmkit.PotentialType.ATTRACTIVE), method='partial_wave')
    print(f"{'v':>6} {'data':>12} {'pred':>12} {'ratio':>10}")
    for v, s_obs, s_pred in zip(v_arr, s_arr, sigma):
        ratio = s_obs / s_pred if s_pred > 0 else float('inf')
        print(f"{v:>6.1f} {s_obs:>12.4e} {s_pred:>12.4e} {ratio:>10.4f}")