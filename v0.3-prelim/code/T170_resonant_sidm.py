"""
T170: Resonant SIDM test for Cloud-9.

Paper: Tran et al. 2024 (arXiv:2405.02388, PRD 110, 043048)
"Gravothermal Catastrophe in Resonant Self-interacting Dark Matter Models"

Key result: With parameters m_chi=31.8 GeV, m_phi=5.7 MeV, alpha=1.6e-3,
the cross section has an ORDER-OF-MAGNITUDE RESONANT ENHANCEMENT
at v ~ 16 km/s, reaching sigma/m ~ 100 cm^2/g.

This is EXACTLY the physics regime Cloud-9 probes:
- Cloud-9: v ~ 28 km/s (close to 16)
- M_halo ~ 5e9 M_sun (matches their 1e8 M_sun simulation scaled)
- Required: sigma/m >= 50 cm^2/g

Test: Can resonant SIDM give our 8 data points simultaneously?
- Check if sidmkit with Tran+ 2024 params gives sigma/m ~ 50-100 at v=28
- Check if the velocity-dependent sigma/m curve has the right shape
- Refit our 8 data points using resonant SIDM as baseline
"""
import numpy as np
import sidmkit
import json
import warnings
warnings.filterwarnings('ignore')
from concurrent.futures import ThreadPoolExecutor, TimeoutError

# Load our 8 data points
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
print("T170: Resonant SIDM (Tran+ 2024) for Cloud-9")
print("=" * 70)
print()
print("Tran+ 2024 parameters: m_chi=31.8 GeV, m_phi=5.7 MeV, alpha=1.6e-3")
print("Reported: sigma/m ~ 100 cm^2/g at v ~ 16 km/s (resonance)")
print()

TIMEOUT = 30
def sigma_with_timeout(alpha, m_A_GeV, m_chi_GeV, v_arr, timeout=30):
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

# Test 1: Exact Tran+ 2024 parameters
print("Test 1: Exact Tran+ 2024 parameters")
print()
v_test = np.array([1, 5, 10, 16, 28, 50, 100, 200, 500, 1000], dtype=float)
sigma_tran = sigma_with_timeout(1.6e-3, 5.7e-3, 31.8, v_test, timeout=60)

if sigma_tran is not None:
    print(f"v (km/s)    sigma/m (cm^2/g)")
    for v, s in zip(v_test, sigma_tran):
        marker = " <-- resonance peak expected" if abs(v - 16) < 5 else ""
        print(f"  {v:>5.0f}        {s:>10.3f}{marker}")
else:
    print("Failed to evaluate Tran+ 2024 params")
print()

# Test 2: Try slight variations to see resonance behavior
print("Test 2: Scan m_phi to find resonances near v=28")
print()

# For m_phi ~ 5-20 MeV and m_chi ~ 10-100 GeV, alpha ~ 1e-3 to 1e-2
# Resonance peak velocity depends on (alpha * m_chi / m_phi)

# Keep m_chi fixed, vary m_phi and alpha
test_params = [
    # (alpha, m_phi_GeV, m_chi_GeV)
    (1.6e-3, 0.0057, 31.8),    # Exact Tran+ 2024 (resonance at ~16 km/s)
    (1.6e-3, 0.010, 31.8),     # Heavier mediator → lower peak velocity
    (1.6e-3, 0.020, 31.8),     # Even heavier
    (1.6e-3, 0.003, 31.8),     # Lighter mediator → higher peak velocity
    (5e-3, 0.010, 31.8),       # Higher alpha, m_phi=10 MeV
    (1e-2, 0.010, 31.8),       # Higher alpha, m_phi=10 MeV
    (5e-3, 0.020, 31.8),       # Higher alpha, m_phi=20 MeV
    (1e-2, 0.050, 31.8),       # Higher alpha, very heavy mediator
    (1.6e-3, 0.0057, 10.0),    # Lighter DM
    (1.6e-3, 0.0057, 100.0),   # Heavier DM
]

print(f"{'alpha':>10} {'m_phi (MeV)':>12} {'m_chi (GeV)':>12} {'sigma at v=28':>14}")
results_res = []
for alpha, m_phi, m_chi in test_params:
    v_28 = np.array([28.0])
    sigma_28 = sigma_with_timeout(alpha, m_phi, m_chi, v_28, timeout=20)
    sigma_28_val = sigma_28[0] if sigma_28 is not None else None

    if sigma_28_val is not None:
        print(f"{alpha:>10.3e} {m_phi*1000:>12.3f} {m_chi:>12.2f} {sigma_28_val:>14.3f}")
        results_res.append({
            'alpha': alpha,
            'm_phi_MeV': m_phi*1000,
            'm_chi_GeV': m_chi,
            'sigma_at_v28': sigma_28_val,
        })

print()

# Test 3: Find which parameters give sigma/m at v=28 closest to 50 cm^2/g
# (the published Cloud-9 lower bound)
if results_res:
    print("Test 3: Which configuration gives sigma/m closest to 50 at v=28?")
    print()
    target = 50.0
    results_sorted = sorted(results_res, key=lambda x: abs(np.log10(x['sigma_at_v28']) - np.log10(target)) if x['sigma_at_v28'] > 0 else float('inf'))
    for r in results_sorted[:5]:
        print(f"  alpha={r['alpha']:.3e}, m_phi={r['m_phi_MeV']:.2f} MeV, m_chi={r['m_chi_GeV']:.1f} GeV → sigma/m = {r['sigma_at_v28']:.3f}")

    # Check if any gives our full 8-point fit
    print()
    print("Test 4: Best resonant-SIDM fit to our 8 data points")
    print()
    best_rmse = float('inf')
    best_params = None
    best_sigma = None

    for r in results_res:
        alpha = r['alpha']
        m_phi = r['m_phi_MeV'] / 1000
        m_chi = r['m_chi_GeV']

        sigma = sigma_with_timeout(alpha, m_phi, m_chi, v_arr, timeout=60)
        if sigma is None or not np.all(np.isfinite(sigma)) or not np.all(sigma > 0):
            continue

        residuals = np.log10(sigma) - np.log10(s_arr)
        if np.all(np.isfinite(residuals)):
            rmse = np.sqrt(np.mean(residuals**2))
            if rmse < best_rmse:
                best_rmse = rmse
                best_params = (alpha, m_phi, m_chi)
                best_sigma = sigma

    if best_params is not None:
        alpha, m_phi, m_chi = best_params
        print(f"  Best RMSE: {best_rmse:.3f}")
        print(f"  Best params: alpha={alpha:.3e}, m_phi={m_phi*1000:.3f} MeV, m_chi={m_chi:.2f} GeV")
        print()
        print(f"{'v':>6} {'data':>12} {'pred':>12} {'ratio':>10}")
        for v, s_obs, s_pred in zip(v_arr, s_arr, best_sigma):
            ratio = s_obs / s_pred if s_pred > 0 else float('inf')
            print(f"{v:>6.1f} {s_obs:>12.4e} {s_pred:>12.4e} {ratio:>10.4f}")
    else:
        print("  All evaluations failed")

# Save results
import os
output_file = r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\t170_resonant_sidm.json"
os.makedirs(os.path.dirname(output_file), exist_ok=True)
with open(output_file, 'w') as f:
    json.dump({
        'tran_plus_2024_params': {
            'alpha': 1.6e-3,
            'm_phi_GeV': 5.7e-3,
            'm_chi_GeV': 31.8,
            'paper_arxiv': '2405.02388',
        },
        'resonance_scan': results_res,
        'best_params': list(best_params) if best_params else None,
        'best_rmse': float(best_rmse) if best_params else None,
    }, f, indent=2)
print(f"\nResults saved to {output_file}")