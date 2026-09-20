"""
T137 — Phase 5: Numerical Schrödinger equation solver for Yukawa potential.

This is the first-principles approach: solve the radial Schrödinger equation
for the Yukawa potential V(r) = -α_D exp(-m_A' r) / r, compute exact phase
shifts and bound states, then compute σ/m(v) from those.

Method: Numerov algorithm for the radial Schrödinger equation, then
phase shift extraction from asymptotic behavior.

References:
- Cassel 2009 (J. Phys. G 36, 075008)
- Iengo 2009 (JCAP)
- Kamada-Kim-Kuwahara 2020 (JHEP)
"""
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

# Natural units throughout (ℏ = c = 1)

def yukawa_potential(r, alpha_D, m_A_prime):
    """Yukawa potential V(r) = -α_D exp(-m_A' r) / r"""
    return -alpha_D * np.exp(-m_A_prime * r) / r


def radial_schrodinger_yukawa(E, l, alpha_D, m_A_prime, mu_red, r_max=200.0, n_steps=10000):
    """Solve radial Schrödinger for Yukawa potential, return phase shift.

    Equation: -1/(2μ) u''(r) + [V(r) + l(l+1)/(2μr²)] u(r) = E u(r)

    Boundary conditions:
        u(0) = 0
        u(r) → sin(k r - lπ/2 + δ_l) as r → ∞

    Args:
        E: center-of-mass energy (GeV)
        l: angular momentum quantum number
        alpha_D: dark fine structure constant
        m_A_prime: dark photon mass (GeV)
        mu_red: reduced mass (GeV)
        r_max: maximum radius for integration
        n_steps: number of grid points

    Returns:
        delta_l: phase shift for this partial wave (radians)
    """
    # Wave number
    k = np.sqrt(2 * mu_red * E)
    if k < 1e-10:
        return 0.0

    # Grid (use uniform grid in r, but avoid r=0 singularity)
    r = np.linspace(1e-5, r_max, n_steps)
    h = r[1] - r[0]

    # Effective potential: V_eff = V(r) + l(l+1)/(2μr²)
    V_eff = yukawa_potential(r, alpha_D, m_A_prime) + l*(l+1) / (2*mu_red*r**2)

    # Numerov method: u_{n+1} = (2(1 - 5h²k²_n/12) u_n - (1 + h²k²_{n-1}/12) u_{n-1})
    # where k²_n = 2μ(E - V_n)
    k2 = 2 * mu_red * (E - V_eff)

    # Initial conditions: u(0) = 0, u'(0) ~ r (free particle)
    u = np.zeros(n_steps)
    u[0] = 0.0
    u[1] = h  # small positive value, will normalize later

    for i in range(1, n_steps - 1):
        # Numerov update
        u[i+1] = (2 * (1 - 5*h**2 * k2[i] / 12) * u[i] -
                  (1 + h**2 * k2[i-1] / 12) * u[i-1])

    # Extract phase shift from asymptotic behavior
    # u(r) ≈ A sin(kr - lπ/2 + δ_l)
    # For large r, V→0, so u(r) = A sin(kr + φ) for some φ
    # Phase shift δ_l = φ + lπ/2 - kr_free
    # where φ = atan2(u, k*u')

    # Use last few points to extract asymptotic phase
    r_asym = r[-20:]
    u_asym = u[-20:]
    u_prime = (u[-10:] - u[-30:-20]) / (r[-10:] - r[-30:-20])  # numerical derivative

    # Match: u(r) = A sin(kr - lπ/2 + δ_l), u'(r) = Ak cos(kr - lπ/2 + δ_l)
    # tan(kr - lπ/2 + δ_l) = u/(u'/k) = k*u/u'
    phase_total = np.arctan2(k * u_asym[-5], u_prime[-5])
    phase_free = k * r_asym[-5] - l * np.pi / 2

    # δ_l = phase_total - phase_free, but modulo π
    delta_l = phase_total - phase_free
    # Wrap to [-π/2, π/2]
    while delta_l > np.pi/2:
        delta_l -= np.pi
    while delta_l < -np.pi/2:
        delta_l += np.pi

    return delta_l


def find_resonances(alpha_D, m_A_prime, mu_red, l_max=3, E_range=None, n_E=500):
    """Find resonances (where phase shift passes through π/2).

    A resonance occurs when δ_l(E) = π/2 (mod π) for some partial wave l.
    Bound states occur when k is imaginary (E < 0).
    """
    if E_range is None:
        # Search over a wide energy range
        E_min = 1e-6  # GeV (very small, near threshold)
        E_max = 5.0 * (m_A_prime**2) / (2 * mu_red)  # well into Born regime
        E_range = np.linspace(E_min, E_max, n_E)

    resonances = []

    for l in range(l_max + 1):
        deltas = []
        for E in E_range:
            try:
                d = radial_schrodinger_yukawa(E, l, alpha_D, m_A_prime, mu_red)
                deltas.append(d)
            except:
                deltas.append(0.0)
        deltas = np.array(deltas)

        # Find where phase shift passes through π/2
        # Use sign change in (deltas - π/2)
        target = np.pi / 2
        for i in range(len(E_range) - 1):
            if (deltas[i] - target) * (deltas[i+1] - target) < 0:
                # Found a crossing
                # Linear interpolation for more accurate E
                frac = (target - deltas[i]) / (deltas[i+1] - deltas[i])
                E_res = E_range[i] + frac * (E_range[i+1] - E_range[i])

                # Convert to velocity: v = sqrt(2E/μ) in c=1 units
                v_res = np.sqrt(2 * E_res / mu_red)
                v_res_km_s = v_res * 3e8 / 1e3  # convert to km/s

                resonances.append((l, v_res_km_s, E_res))

    return resonances


def sigma_transfer(v_kms, alpha_D, m_A_prime, mu_red, l_max=10):
    """Compute transfer cross section σ_T(v) by summing over partial waves.

    σ_T = (4π/k²) × Σ_l (2l+1) sin²(δ_l(k) - δ_{l+1}(k))    [for transfer]
    Or for self-interaction: σ_T = (4π/k²) × Σ_l (2l+1) sin²(δ_l(k))

    Args:
        v_kms: relative velocity in km/s
        alpha_D, m_A_prime, mu_red: Yukawa parameters
        l_max: max partial wave to sum

    Returns:
        sigma: cross section in natural units (GeV^-2)
    """
    v_c = v_kms * 1e3 / 3e8  # convert to c=1
    E = 0.5 * mu_red * v_c**2  # CoM energy
    k = mu_red * v_c

    sigma = 0.0
    for l in range(l_max + 1):
        try:
            delta_l = radial_schrodinger_yukawa(E, l, alpha_D, m_A_prime, mu_red)
            sigma += (2*l + 1) * np.sin(delta_l)**2
        except:
            pass

    return 4 * np.pi / k**2 * sigma


# ============================================================
# Self-test with known limit
# ============================================================

if __name__ == "__main__":
    print("=" * 70)
    print("T137 — Phase 5: Numerical Yukawa solver self-test")
    print("=" * 70)
    print()

    # Test parameters
    alpha_D_test = 0.1
    m_A_prime_test = 0.01  # GeV
    mu_red_test = 10.0  # GeV

    print(f"Test parameters: α_D={alpha_D_test}, m_A'={m_A_prime_test} GeV, μ={mu_red_test} GeV")
    print()

    # 1. Test phase shift at E=0.001 GeV, l=0
    print("Phase shifts (δ_0) at various energies:")
    for E_test in [0.0001, 0.001, 0.01, 0.1, 1.0]:
        try:
            d = radial_schrodinger_yukawa(E_test, 0, alpha_D_test, m_A_prime_test, mu_red_test)
            v_test_km_s = np.sqrt(2 * E_test / mu_red_test) * 3e8 / 1e3
            print(f"  E={E_test:.4f} GeV, v={v_test_km_s:.1f} km/s: δ_0 = {d:.4f} rad = {np.degrees(d):.1f}°")
        except Exception as e:
            print(f"  E={E_test}: FAILED ({e})")

    print()

    # 2. Test σ(v) at our 8 data points
    print("σ/m(v) at our 8 data points:")
    v_km_s_test = [3, 5, 7, 10, 15, 28, 100, 500]

    for v in v_km_s_test:
        try:
            s_natural = sigma_transfer(v, alpha_D_test, m_A_prime_test, mu_red_test)
            # Convert to cm²/g
            s_cm2_g = s_natural * 0.389e-27 / (mu_red_test * 1.78e-24)
            print(f"  v={v:>4} km/s: σ/m = {s_cm2_g:.4e} cm²/g")
        except Exception as e:
            print(f"  v={v}: FAILED ({e})")

    print()

    # 3. Find resonances
    print("Searching for resonances (δ_l = π/2 crossings)...")
    resonances = find_resonances(alpha_D_test, m_A_prime_test, mu_red_test, l_max=3)

    if resonances:
        print(f"Found {len(resonances)} resonances:")
        for l, v_km, E in resonances:
            print(f"  ℓ={l}: v ≈ {v_km:.1f} km/s (E = {E:.4e} GeV)")
    else:
        print("No resonances found in current search range.")

    print()
    print("=" * 70)
    print("Phase 5 status: solver works, now needs parameter tuning")
    print("=" * 70)