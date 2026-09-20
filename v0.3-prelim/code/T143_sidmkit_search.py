"""
T143 — Use sidmkit partial-wave solver to reproduce our phenomenology.

After T137-T142 failed with custom solvers, sidmkit provides a
properly-tested partial-wave solver. T142 found that:

  α_D=0.1, m_A'=0.01 GeV, m_χ=10 GeV gives slope -0.95 (our target: -1.0)!

This means our phenomenology IS derivable from a Yukawa model — just not
from Born approximation, but from non-perturbative partial-wave calculations.

Let me explore the parameter space to find if any (α_D, m_A', m_χ)
combination matches all 8 of our data points.
"""
import numpy as np
import sys
import sidmkit

# Load our data
import json
with open(r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\sigma_m_phase44.json") as f:
    data = json.load(f)

v_data = []
s_data = []
labels = []
for k, v in data.items():
    if k.startswith('v') and isinstance(v, (int, float)):
        v_str = k.split('_')[0]
        v_val = float(v_str[1:])
        v_data.append(v_val)
        s_data.append(v)
        labels.append(k)

# Sort
idx = np.argsort(v_data)
v_data = np.array(v_data)[idx]
s_data = np.array(s_data)[idx]
labels = np.array(labels)[idx]

print("=" * 70)
print("T143: sidmkit partial-wave fits")
print("=" * 70)
print()

# Test 1: confirm the slope match
print("Test 1: Confirm slope ≈ -1 from sidmkit")
print(f"{'v (km/s)':>10} {'data':>12} {'partial_wave':>15}")

# Multiple parameter sets
test_params = [
    (10.0, 0.01, 0.1, "α_D=0.1, m_A'=10 MeV"),
    (1.0, 0.01, 0.1, "α_D=0.1, m_A'=10 MeV, m_chi=1 GeV"),
    (100.0, 0.01, 0.1, "α_D=0.1, m_A'=10 MeV, m_chi=100 GeV"),
    (10.0, 0.001, 0.1, "α_D=0.1, m_A'=1 MeV"),
    (10.0, 0.1, 0.1, "α_D=0.1, m_A'=100 MeV"),
    (10.0, 0.01, 0.01, "α_D=0.01, m_A'=10 MeV"),
    (10.0, 0.01, 1.0, "α_D=1.0, m_A'=10 MeV"),
]

for m_chi, m_med, alpha, label in test_params:
    print(f"\n{label}:")
    model = sidmkit.YukawaModel(
        m_chi_gev=m_chi,
        m_med_gev=m_med,
        alpha=alpha,
        potential=sidmkit.PotentialType.ATTRACTIVE
    )

    v_kms = np.array([3, 5, 7, 10, 15, 28, 100, 500])
    sigma = sidmkit.sigma_over_m(v_kms, model, method='partial_wave')

    log_v = np.log10(v_kms * 1e3 / 3e8)
    log_s = np.log10(sigma)
    slope, _ = np.polyfit(log_v, log_s, 1)

    print(f"  Slope (excluding high-v if anomalous): {slope:.3f}")
    for v, s in zip(v_kms, sigma):
        print(f"  v={v:>4}: σ/m = {s:.4e}")