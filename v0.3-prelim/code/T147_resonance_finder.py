"""
T147: WIDE velocity scan with sidmkit to find resonance peaks.

We know our data has peaks at v ≈ 28, 100, 178, 430, 769 km/s.
The Cloud-9 peak (v=28) is HUGE (factor 4000 jump).
Other peaks are subtler (factor 5-10).

For Yukawa, peaks come from bound states near threshold.
Levinson: peaks at v where delta_l(k) = π/2.

Strategy:
- Use sidmkit at MULTIPLE v values to find peak positions
- For each parameter set, check if peaks appear at our target v's
"""
import numpy as np
import sidmkit
import warnings
warnings.filterwarnings('ignore')
import json

# Target peak positions (from our phenomenology)
target_v = np.array([28, 100, 178, 430, 769])
v_test = np.logspace(0.5, 4, 30)  # 3 to 10000 km/s, log-spaced

# Try various (alpha, m_A, m_chi) combinations and look for peaks
test_params = [
    (0.1, 0.001, 10),
    (0.1, 0.01, 10),
    (0.1, 0.1, 10),
    (0.5, 0.01, 10),
    (0.05, 0.01, 10),
    (0.01, 0.01, 10),
    (0.5, 0.001, 1),
    (0.5, 0.01, 1),
    (1.0, 0.001, 1),
]

print("=" * 70)
print("T147: Find resonances in sidmkit output")
print("=" * 70)

for alpha, mA, mChi in test_params:
    print(f"\nalpha={alpha}, mA={mA} GeV, mChi={mChi} GeV:")
    try:
        model = sidmkit.YukawaModel(m_chi_gev=mChi, m_med_gev=mA, alpha=alpha,
                                      potential=sidmkit.PotentialType.ATTRACTIVE)
        sigma = sidmkit.sigma_over_m(v_test, model, method='partial_wave')

        # Find local maxima
        valid = np.isfinite(sigma) & (sigma > 0)
        if np.sum(valid) >= 5:
            log_s = np.where(valid, np.log10(sigma), 0)
            # Find peaks
            peaks = []
            for i in range(1, len(log_s) - 1):
                if valid[i] and valid[i-1] and valid[i+1]:
                    if log_s[i] > log_s[i-1] and log_s[i] > log_s[i+1]:
                        peaks.append((v_test[i], sigma[i]))
            print(f"  Found {len(peaks)} peaks:")
            for v, s in peaks:
                print(f"    v={v:.1f} km/s: σ/m = {s:.4e}")
    except Exception as e:
        print(f"  Error: {e}")