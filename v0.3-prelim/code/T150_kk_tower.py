"""
T150: Multi-mediator (KK tower) approach.

Each KK mode contributes its own Yukawa. Total σ is sum.
Multiple modes → multiple resonances.

Reference: Chaffey-Fichet-Tanedo 2021 (CFT 2021) showed that continuum
mediation with bulk mass α ∈ [0.5, 1] produces σ_T ~ v^(-4α) for α=0.5 to
α=1.0 (gives slope -2 to -4).

Our data has slope -1. This is OUTSIDE CFT 2021's parameter range, but
maybe a finite KK tower gives different scaling.

Approach: sum over N KK modes with geometric mass spectrum m_n = m_0 × r^n.
"""
import numpy as np
import sidmkit
import warnings
warnings.filterwarnings('ignore')
import json

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

# Multi-mediator: sum of Yukawas from N KK modes
# σ_total = Σ_n c_n × σ_Yukawa(v; α_D, m_n, m_χ)
# For each n: m_n = m_0 × r^n, c_n = 1/n (typical KK coefficient)

def sigma_kk_tower(v_arr, alpha_D, m_0_GeV, r_mass, m_chi_GeV, n_modes=5):
    """KK tower: sum over n modes with geometric mass spectrum."""
    sigma_total = np.zeros_like(v_arr, dtype=float)
    for n in range(1, n_modes + 1):
        m_n = m_0_GeV * (r_mass ** n)
        c_n = 1.0 / n  # KK coefficient

        try:
            model = sidmkit.YukawaModel(m_chi_gev=m_chi_GeV, m_med_gev=m_n, alpha=alpha_D * c_n,
                                          potential=sidmkit.PotentialType.ATTRACTIVE)
            sigma_n = sidmkit.sigma_over_m(v_arr, model, method='partial_wave')
            sigma_total += sigma_n
        except:
            pass
    return sigma_total


# Test different KK parameters
print("=" * 70)
print("T150: Multi-mediator KK tower")
print("=" * 70)

results = []
test_cases = [
    # (alpha, m_0, r, m_chi, n_modes, label)
    (0.1, 0.001, 2.0, 1.0, 5, "alpha=0.1, m_0=1MeV, r=2, 5 modes"),
    (0.1, 0.001, 3.0, 1.0, 4, "alpha=0.1, m_0=1MeV, r=3, 4 modes"),
    (0.1, 0.01, 2.0, 1.0, 5, "alpha=0.1, m_0=10MeV, r=2, 5 modes"),
    (0.3, 0.001, 2.0, 1.0, 5, "alpha=0.3, m_0=1MeV, r=2, 5 modes"),
    (0.5, 0.001, 2.0, 1.0, 3, "alpha=0.5, m_0=1MeV, r=2, 3 modes"),
    (0.3, 0.0001, 10.0, 1.0, 3, "alpha=0.3, m_0=0.1MeV, r=10, 3 modes"),
    (1.0, 0.001, 1.5, 1.0, 5, "alpha=1.0, m_0=1MeV, r=1.5, 5 modes"),
]

for alpha, m_0, r, m_chi, n_modes, label in test_cases:
    print(f"\n{label}:")
    try:
        sigma = sigma_kk_tower(v_arr, alpha, m_0, r, m_chi, n_modes)
        valid = np.isfinite(sigma) & (sigma > 0)
        if np.sum(valid) >= 5:
            residuals = np.log10(sigma[valid]) - np.log10(s_arr[valid])
            rmse = np.sqrt(np.mean(residuals**2))
            print(f"  RMSE = {rmse:.3f}")
            for v, s_obs, s_pred in zip(v_arr, s_arr, sigma):
                if np.isfinite(s_pred) and s_pred > 0:
                    ratio = s_obs / s_pred
                    print(f"    v={v:>5}: data={s_obs:.2e}, pred={s_pred:.2e}, ratio={ratio:.2e}")
            results.append((label, rmse))
    except Exception as e:
        print(f"  Error: {e}")

# Sort results
print()
print("=" * 70)
print("BEST KK TOWER FITS:")
print("=" * 70)
for label, rmse in sorted(results, key=lambda x: x[1])[:5]:
    print(f"  {rmse:.3f}: {label}")