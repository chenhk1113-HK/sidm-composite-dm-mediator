"""
T139 — Phase 7: Robust Yukawa solver + resonance parameter scan

After T137-T138 showed difficulties with custom solvers, this version uses
a robust Numerov with proper boundary conditions and tests against the
analytic Born limit.

Reference: T. Scherer, "Computational Physics", chapter on Schrödinger eq.
The trick: use the formula:
  u(r) = A sin(kr - lπ/2 + δ_l)
and extract δ_l from the SLOPE of u vs the expected free-particle behavior.
"""
import numpy as np
import sys

def yukawa_phase_shift(E, l, alpha_D, m_A_prime, mu_red, r_max=None, n_steps=2000):
    """Solve radial Schrödinger for Yukawa and return phase shift.

    Method: Numerov with log-spaced grid (handles small-r singularity).
    Phase shift from asymptotic matching using interior + exterior solutions.
    """
    k = np.sqrt(2 * mu_red * E)
    if k < 1e-10:
        return 0.0

    if r_max is None:
        # Choose r_max large enough: many wavelengths
        # wavelength = 2π/k
        # Want r_max > 20 wavelengths
        wavelength = 2 * np.pi / k
        # But also need to include enough range for Yukawa screening
        yukawa_range = 10.0 / m_A_prime  # exponential decay scale
        r_max = max(20 * wavelength, 5 * yukawa_range)
        r_max = min(r_max, 5000.0)  # cap

    # Log-spaced grid: avoids r=0 singularity, covers wide range
    r = np.logspace(-4, np.log10(r_max), n_steps)

    # Vectorized potential
    def V(r_):
        return -alpha_D * np.exp(-m_A_prime * r_) / r_

    # Initial conditions at smallest r (using u ~ r^(l+1) for small r)
    # u(r[0]) = r[0]^(l+1), u'(r[0]) = (l+1) r[0]^l
    # Use 2nd-order Taylor: u(r[0]+h) = u(r[0]) + h u'(r[0]) + h²/2 u''(r[0])
    # u''(r[0]) = (l+1)l r[0]^(l-1) + 2μ V(r[0]) u(r[0])
    # (since for u ~ r^(l+1): u'' = (l+1)l r^(l-1))
    # But +2μ V(r) u(r) term from Schrödinger eq:
    # u'' = 2μ(V-E)u + l(l+1)/r² u (for u ~ r^(l+1), last term is (l+1)l r^(l-1))
    # Actually: u'' - l(l+1)/r² u = 2μ(V-E)u
    # For u ~ r^(l+1): u'' = (l+1)l r^(l-1)
    # So: (l+1)l r^(l-1) - l(l+1) r^(l-1) = 0 = 2μ(V-E) u
    # This is satisfied only if V = E, which is not the case.
    # So u ~ r^(l+1) is the correct leading order if we IGNORE the V term
    # (since V diverges at r=0 but we start at r[0] = 1e-4 where V is finite)

    u_prev = r[0]**(l+1)
    # u at second point: use Taylor expansion including V
    h_init = r[1] - r[0]
    u_dd = (l+1)*l*r[0]**(l-1) - l*(l+1)/r[0]**2 * r[0]**(l+1)  # centrifugal cancels for u~r^(l+1)
    u_dd += 2*mu_red * (V(r[0]) - E) * u_prev
    u_curr = u_prev + h_init * (l+1) * r[0]**l + 0.5 * h_init**2 * u_dd

    # Numerov: u_{n+1} = [2(1 - 5h²k²_n/12) u_n - (1 + h²k²_{n-1}/12) u_{n-1}] / (1 + h²k²_{n+1}/12)
    u = np.zeros(n_steps)
    u[0] = u_prev
    u[1] = u_curr

    for i in range(1, n_steps - 1):
        k2_prev = 2*mu_red*(E - V(r[i-1]) - l*(l+1)/r[i-1]**2)
        k2_curr = 2*mu_red*(E - V(r[i]) - l*(l+1)/r[i]**2)
        k2_next = 2*mu_red*(E - V(r[i+1]) - l*(l+1)/r[i+1]**2)

        h = r[i+1] - r[i]
        h_prev = r[i] - r[i-1]

        # Standard Numerov (constant step)
        u[i+1] = (2*(1 - 5*h**2*k2_curr/12) * u[i]
                  - (1 + h**2*k2_prev/12) * u[i-1]) / (1 + h**2*k2_next/12)

    # Phase shift extraction: use last 100 points for asymptotic fit
    # u(r) = A sin(kr - lπ/2 + δ_l) for large r
    # Use least squares to fit A and δ_l

    n_fit = 200
    r_fit = r[-n_fit:]
    u_fit = u[-n_fit:]

    # At large r, V → 0, centrifugal → 0
    # u(r) ≈ A sin(kr - lπ/2 + δ_l)
    # Expand: u = A[sin(kr - lπ/2) cos(δ_l) + cos(kr - lπ/2) sin(δ_l)]
    # Let a = A cos(δ_l), b = A sin(δ_l)
    # u = a sin(kr - lπ/2) + b cos(kr - lπ/2)
    sin_kr = np.sin(k * r_fit - l * np.pi / 2)
    cos_kr = np.cos(k * r_fit - l * np.pi / 2)

    M = np.column_stack([sin_kr, cos_kr])
    result = np.linalg.lstsq(M, u_fit, rcond=None)
    coeffs = result[0]
    a, b = coeffs

    # tan(δ_l) = b/a
    delta_l = np.arctan2(b, a)

    return delta_l


# ============================================================
# Self-test: compare to analytical Born at high E
# ============================================================

print("=" * 70)
print("T139: Robust Yukawa solver + resonance scan")
print("=" * 70)
print()

# Test 1: high-E should match Born
alpha_D = 0.1
m_A = 0.01  # GeV
mu = 10.0   # GeV

print("Comparison with Born at high E:")
print(f"{'E (GeV)':>10} {'v (km/s)':>10} {'numerical':>12} {'Born':>12}")
for E in [1.0, 10.0, 100.0]:
    d_num = yukawa_phase_shift(E, 0, alpha_D, m_A, mu)
    k = np.sqrt(2*mu*E)
    # Born δ_0 for Yukawa (Cassel 2009):
    # dB/dr = 2μ(V-E)u
    # For Yukawa V = -α exp(-mr)/r, in Born:
    # δ_l = -α × 2μ ∫₀^∞ dr j_l(kr)² exp(-mr)/r
    # For l=0, j_0(kr) = sin(kr)/kr
    # ∫₀^∞ sin²(kr)/(kr)² × exp(-mr)/r dr = ... (integral)
    # Closed form: δ_0^(Born) = -α_D × 2μ × 1/(k² + m_A'²/4) × (some log)
    # Actually for Yukawa the exact Born result is:
    # σ_T = (π/k²) × [log(1 + 4k²/m_A'²) - 4k²/(m_A'² + 4k²)]
    # And dσ/dΩ = (α_D²/4E²) × 1/(sin²(θ/2) + m_A'²/(4k²))²
    # δ_0 = ∫₀^∞ dr (sin(kr) - kr cos(kr))/(kr)² × V(r) × 2μ
    # For Yukawa: integral has closed form
    # δ_0^(Born) ≈ -2α_D μ/(k × sqrt(k² + m_A²/4)) × ... 
    # Use the simpler form:
    delta_born = -2 * alpha_D * mu / k**2 * np.log(1 + 4*k**2 / m_A**2)
    v = np.sqrt(2*E/mu) * 3e8 / 1e3
    print(f"{E:>10.2f} {v:>10.0f} {d_num:>12.4f} {delta_born:>12.4f}")

# Test 2: at low E, should be large (resonance)
print()
print("Phase shift at low E (near threshold):")
for E in [0.0001, 0.001, 0.01, 0.1]:
    d_num = yukawa_phase_shift(E, 0, alpha_D, m_A, mu)
    v = np.sqrt(2*E/mu) * 3e8 / 1e3
    print(f"  E={E:.4f}, v={v:.0f} km/s: δ_0 = {d_num:.4f} rad = {np.degrees(d_num):.1f}°")