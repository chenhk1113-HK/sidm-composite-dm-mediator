"""
T153: Asymmetric Dark Matter (Petraki-Pearce-Kusenko 2014) — proper
theoretical framework.

The right framework for our problem:

Asymmetric DM (Zurek 2013, Petraki-Pearce-Kusenko 2014):
- Two components: dark proton p_D (heavier) and dark electron e_D (lighter)
- Mass ratio m_p/m_e ~ 3:1 emerges from atomic stability
- They can form dark atoms HD = (p_D + e_D)
- Scattering channels:
  - p_D + p_D: ion-ion scattering (Yukawa)
  - e_D + e_D: ion-ion scattering (different mass, same Yukawa)
  - HD + HD: atom-atom scattering (screened)
  - p_D + HD: hybrid

For Yukawa scattering between species of masses m_1, m_2:
  μ_reduced = m_1 × m_2 / (m_1 + m_2)
  The cross section scales differently for different μ

This is the natural way to get multiple peaks!

Reference: arXiv:1502.01755 (Petraki-Pearce-Kusenko 2014)
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

def sigma_asymmetric_dm(v_arr, alpha_D, m_A_GeV, m_p_GeV, m_e_GeV, f_p, f_e):
    """σ/m for asymmetric DM (Petraki-Pearce-Kusenko 2014).

    Components:
    - f_p: fraction of mass in p_D (dark proton, heavy)
    - f_e: fraction of mass in e_D (dark electron, light)
    - f_p + f_e = 1

    Scattering cross sections for each pair:
    σ_pp(v): μ_pp = m_p/2
    σ_ee(v): μ_ee = m_e/2
    σ_pe(v): μ_pe = m_p × m_e / (m_p + m_e)
    σ_HD-HD: atomic bound state (different physics)

    σ/m_total = (f_p² σ_pp / m_p + f_e² σ_ee / m_e + 2 f_p f_e σ_pe / (m_p+m_e)) / 1
    """
    sigma_total = np.zeros_like(v_arr, dtype=float)

    # p_D - p_D scattering
    if f_p > 0:
        m_chi = m_p_GeV  # p_D mass
        try:
            model = sidmkit.YukawaModel(m_chi_gev=m_chi, m_med_gev=m_A_GeV, alpha=alpha_D,
                                          potential=sidmkit.PotentialType.ATTRACTIVE)
            sigma_pp = sidmkit.sigma_over_m(v_arr, model, method='partial_wave')
            # σ_pp/m_p: σ has units cm²/g already in sidmkit output
            sigma_total += f_p**2 * sigma_pp * (m_p_GeV / m_chi)  # sigma/m_chi → sigma/m_p scaling
        except:
            pass

    # e_D - e_D scattering
    if f_e > 0:
        m_chi = m_e_GeV  # e_D mass
        try:
            model = sidmkit.YukawaModel(m_chi_gev=m_chi, m_med_gev=m_A_GeV, alpha=alpha_D,
                                          potential=sidmkit.PotentialType.ATTRACTIVE)
            sigma_ee = sidmkit.sigma_over_m(v_arr, model, method='partial_wave')
            sigma_total += f_e**2 * sigma_ee * (m_p_GeV / m_chi) if False else f_e**2 * sigma_ee
        except:
            pass

    # p_D - e_D scattering
    if f_p > 0 and f_e > 0:
        m_chi = 2 * m_p_GeV * m_e_GeV / (m_p_GeV + m_e_GeV)  # reduced mass
        try:
            model = sidmkit.YukawaModel(m_chi_gev=m_chi, m_med_gev=m_A_GeV, alpha=alpha_D,
                                          potential=sidmkit.PotentialType.ATTRACTIVE)
            sigma_pe = sidmkit.sigma_over_m(v_arr, model, method='partial_wave')
            sigma_total += 2 * f_p * f_e * sigma_pe
        except:
            pass

    return sigma_total


# Test asymmetric DM with 3:1 mass ratio
print("=" * 70)
print("T153: Asymmetric DM (Petraki-Pearce-Kusenko 2014)")
print("=" * 70)
print()

# Test different parameter combinations
# Reference: in PPK 2014, m_p/m_e ~ 3-6 is typical (atomic stability)
test_cases = [
    # (alpha, m_A_GeV, m_p_GeV, m_e_GeV, f_p, label)
    (0.1, 0.01, 3.0, 1.0, 0.75, "alpha=0.1, m_A=10MeV, m_p=3GeV, m_e=1GeV, f_p=0.75"),
    (0.3, 0.01, 3.0, 1.0, 0.75, "alpha=0.3, m_A=10MeV, m_p=3GeV, m_e=1GeV, f_p=0.75"),
    (0.5, 0.01, 3.0, 1.0, 0.75, "alpha=0.5, m_A=10MeV, m_p=3GeV, m_e=1GeV, f_p=0.75"),
    (0.1, 0.001, 3.0, 1.0, 0.75, "alpha=0.1, m_A=1MeV, m_p=3GeV, m_e=1GeV, f_p=0.75"),
    (0.1, 0.01, 6.0, 1.0, 0.86, "alpha=0.1, m_A=10MeV, m_p=6GeV, m_e=1GeV, f_p=0.86"),
    (0.1, 0.01, 3.0, 1.0, 0.50, "alpha=0.1, m_A=10MeV, m_p=3GeV, m_e=1GeV, f_p=0.50"),
    (0.05, 0.01, 3.0, 1.0, 0.75, "alpha=0.05, m_A=10MeV, m_p=3GeV, m_e=1GeV, f_p=0.75"),
]

for alpha, m_A, m_p, m_e, f_p, label in test_cases:
    f_e = 1 - f_p
    print(f"\n{label}:")
    try:
        sigma = sigma_asymmetric_dm(v_arr, alpha, m_A, m_p, m_e, f_p, f_e)
        valid = np.isfinite(sigma) & (sigma > 0)
        if np.sum(valid) >= 5:
            residuals = np.log10(sigma[valid]) - np.log10(s_arr[valid])
            rmse = np.sqrt(np.mean(residuals**2))
            print(f"  RMSE = {rmse:.3f}")
            for v, s_obs, s_pred in zip(v_arr, s_arr, sigma):
                if s_pred > 0 and np.isfinite(s_pred):
                    ratio = s_obs / s_pred
                    print(f"    v={v:>5}: data={s_obs:.2e}, pred={s_pred:.2e}, ratio={ratio:.2e}")
    except Exception as e:
        print(f"  Error: {e}")