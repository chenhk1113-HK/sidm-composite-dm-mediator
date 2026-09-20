"""
T142: Resonance search — fast version using vectorized ODE.
"""
import numpy as np
from scipy.integrate import solve_ivp
import json
import sys

# Use a cached approach: pre-compute on a coarse grid, then refine near crossings

def delta_l_fast(E, l, alpha_D, m_A_prime, mu_red, r_max=200.0):
    k = np.sqrt(2 * mu_red * E)
    if k < 1e-10:
        return 0.0

    def rhs(r, y):
        u, v = y
        r_eff = max(r, 1e-8)
        V = -alpha_D * np.exp(-m_A_prime * r_eff) / r_eff
        V_cent = l*(l+1) / (2 * mu_red * r_eff**2)
        V_eff = V + V_cent
        return [v, 2 * mu_red * (V_eff - E) * u]

    r0 = 1e-5
    u0 = r0**(l+1)
    v0 = (l+1) * r0**l

    sol = solve_ivp(rhs, [r0, r_max], [u0, v0], method='RK45',
                     rtol=1e-8, atol=1e-10, max_step=r_max/20)

    if not sol.success:
        return np.nan

    u_final = sol.y[0, -1]
    v_final = sol.y[1, -1]
    phase = np.arctan2(k * u_final, v_final)
    target = k * r_max - l * np.pi / 2
    raw_diff = phase - target
    delta_l = raw_diff % np.pi
    if delta_l > np.pi/2:
        delta_l -= np.pi
    return delta_l

# Coarse scan
alpha_D = 0.1
m_A = 0.01
mu = 10.0

print("=" * 70)
print("T142: Coarse resonance scan (Yukawa, xi = 100)")
print("=" * 70)
print()
print(f"Parameters: α_D={alpha_D}, m_A'={m_A} GeV, μ={mu} GeV")
print(f"Coupling strength: xi={alpha_D * mu / m_A:.1f}")
print()

E_range = np.logspace(-5, 1, 50)
v_range = np.sqrt(2 * E_range / mu) * 3e8 / 1e3

print(f"{'E (GeV)':>10} {'v (km/s)':>10} {'d_0':>10} {'d_1':>10}")
import time
t0 = time.time()
results = []
for i, E in enumerate(E_range):
    d0 = delta_l_fast(E, 0, alpha_D, m_A, mu, r_max=150.0)
    d1 = delta_l_fast(E, 1, alpha_D, m_A, mu, r_max=150.0)
    results.append((E, d0, d1))
    if i % 10 == 0:
        elapsed = time.time() - t0
        print(f"{E:>10.3e} {v_range[i]:>10.2e} {d0:>10.4f} {d1:>10.4f}  ({elapsed:.1f}s)")

print(f"\nTotal time: {time.time() - t0:.1f}s")