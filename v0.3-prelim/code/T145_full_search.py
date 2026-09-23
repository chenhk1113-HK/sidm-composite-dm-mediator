"""
T145: Full parameter search using sidmkit partial-wave solver.

Background: T143 showed sidmkit gives slope -1 from non-perturbative
Yukawa. T144 ran but no clean output. Let me make a more robust search.

Strategy:
- Use partial_wave method on a coarse grid
- Filter out overflow cases (sidmkit doesn't always converge)
- Score by RMSE in log-space on the 7 data points excluding Cloud-9
- Find best (alpha_D, m_A', m_chi) match
"""
import numpy as np
import sidmkit
import json
import warnings
warnings.filterwarnings('ignore')

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

# Exclude Cloud-9 (v=28) for slope comparison
mask_no_c9 = v_arr < 25

print("=" * 70)
print("T145: Full parameter search")
print("=" * 70)
print(f"Data: {len(v_arr)} points, v range {v_arr[0]}-{v_arr[-1]} km/s")
print()

# Coarse grid
results = []
tested = 0
print("Testing parameter combinations...")
for log_alpha in [-2.5, -2.0, -1.5, -1.0, -0.5, 0.0]:
    for log_mA in [-3, -2, -1, 0, 1]:
        for log_mChi in [-1, 0, 1, 2]:
            alpha = 10**log_alpha
            mA = 10**(log_mA - 3)
            mChi = 10**log_mChi

            try:
                model = sidmkit.YukawaModel(
                    m_chi_gev=mChi,
                    m_med_gev=mA,
                    alpha=alpha,
                    potential=sidmkit.PotentialType.ATTRACTIVE
                )
                sigma_pred = sidmkit.sigma_over_m(v_arr, model, method='partial_wave')

                # Check for valid predictions
                valid = (sigma_pred > 0) & np.isfinite(sigma_pred) & (sigma_pred < 1e10)
                if np.sum(valid & mask_no_c9) >= 3:
                    residuals = np.log10(sigma_pred[mask_no_c9 & valid]) - np.log10(s_arr[mask_no_c9 & valid])
                    if np.all(np.isfinite(residuals)):
                        rmse = np.sqrt(np.mean(residuals**2))
                        results.append((alpha, mA, mChi, rmse))
                        tested += 1
            except:
                pass

results.sort(key=lambda x: x[3])
print(f"Tested {tested} valid combinations")
print()
print(f"{'rank':>5} {'α_D':>10} {'m_A (GeV)':>12} {'m_χ (GeV)':>12} {'RMSE':>10}")
for i, (alpha, mA, mChi, rmse) in enumerate(results[:10]):
    print(f"{i+1:>5} {alpha:>10.3e} {mA:>12.3e} {mChi:>12.3e} {rmse:>10.3f}")

# Show best fit in detail
if results:
    print()
    print("=" * 70)
    print("BEST FIT DETAILS:")
    print("=" * 70)
    alpha, mA, mChi, rmse = results[0]
    print(f"α_D = {alpha:.4e}, m_A = {mA:.4e} GeV, m_χ = {mChi:.4e} GeV")
    print(f"RMSE (log space) = {rmse:.3f}")
    print()
    print(f"{'v (km/s)':>10} {'data':>12} {'model':>12} {'ratio':>10}")
    model = sidmkit.YukawaModel(m_chi_gev=mChi, m_med_gev=mA, alpha=alpha,
                                  potential=sidmkit.PotentialType.ATTRACTIVE)
    sigma_pred = sidmkit.sigma_over_m(v_arr, model, method='partial_wave')
    for v, s_obs, s_pred in zip(v_arr, s_arr, sigma_pred):
        if s_pred > 0 and np.isfinite(s_pred):
            ratio = s_obs / s_pred
            print(f"{v:>10.1f} {s_obs:>12.4e} {s_pred:>12.4e} {ratio:>10.4f}")
        else:
            print(f"{v:>10.1f} {s_obs:>12.4e} {s_pred:>12.4e} {'inf':>10}")
else:
    print("No valid fits found")