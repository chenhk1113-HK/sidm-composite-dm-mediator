"""
T149: Smart parameter search using insights from T143-T148.

Insights:
- sidmkit gives slope -1 in some configs (T143)
- Cloud-9 peak requires bound state near threshold
- Multiple resonances needed for full phenomenology
- Wider v range (3-1000 km/s) to find peaks

Strategy:
1. Scan v over wide range for several parameter sets
2. Look for resonance peaks
3. Compute RMSE on log scale
4. Identify best parameter set
"""
import numpy as np
import sidmkit
import warnings
warnings.filterwarnings('ignore')
import json
import time

# Load our data
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

# Test specific promising parameters
# 1. Light mediator, low coupling (Born limit)
# 2. Heavy mediator, high coupling (classical regime)
# 3. Threshold parameters (resonance regime)
test_cases = [
    # (alpha, mA_GeV, mChi_GeV, label)
    (0.1, 0.001, 1.0, "Born: alpha=0.1, mA=1 MeV, mChi=1 GeV"),
    (0.1, 0.001, 0.1, "Born: alpha=0.1, mA=1 MeV, mChi=100 MeV"),
    (0.5, 0.001, 0.1, "Classical: alpha=0.5, mA=1 MeV, mChi=100 MeV"),
    (0.5, 0.001, 1.0, "Classical: alpha=0.5, mA=1 MeV, mChi=1 GeV"),
    (0.1, 0.01, 0.1, "Threshold: alpha=0.1, mA=10 MeV, mChi=100 MeV"),
    (0.3, 0.01, 1.0, "Threshold: alpha=0.3, mA=10 MeV, mChi=1 GeV"),
    (1.0, 0.001, 0.1, "Strong: alpha=1.0, mA=1 MeV, mChi=100 MeV"),
]

print("=" * 70)
print("T149: Test parameter combinations for our 8 data points")
print("=" * 70)

for alpha, mA, mChi, label in test_cases:
    print(f"\n{label}")
    try:
        model = sidmkit.YukawaModel(m_chi_gev=mChi, m_med_gev=mA, alpha=alpha,
                                      potential=sidmkit.PotentialType.ATTRACTIVE)
        sigma = sidmkit.sigma_over_m(v_arr, model, method='partial_wave')

        # Check valid
        valid = np.isfinite(sigma) & (sigma > 0)
        if np.sum(valid) >= 5:
            residuals = np.log10(sigma[valid]) - np.log10(s_arr[valid])
            rmse = np.sqrt(np.mean(residuals**2))
            print(f"  RMSE = {rmse:.3f}")
            print(f"  Predictions:")
            for v, s_obs, s_pred in zip(v_arr, s_arr, sigma):
                if np.isfinite(s_pred) and s_pred > 0:
                    ratio = s_obs / s_pred
                    print(f"    v={v:>5}: data={s_obs:.2e}, pred={s_pred:.2e}, ratio={ratio:.2e}")
                else:
                    print(f"    v={v:>5}: data={s_obs:.2e}, pred=invalid")
        else:
            print(f"  Too few valid points: {np.sum(valid)}")
    except Exception as e:
        print(f"  Error: {e}")