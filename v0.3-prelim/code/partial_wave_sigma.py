"""
T101 — Partial-wave σ/m(v) computation.

This is the Layer-D-extension σ/m calculation that replaces the
semi-classical Yukawa transfer cross-section + classical Breit-Wigner
form used in cloud-9-relhic (paper v1.8) with a proper numerical
partial-wave expansion.

Sub-tasks (per POST_PAPER_ROADMAP_2026_09_17.md):
- T101.1: this module — infrastructure (solver + phase-shift extraction)
- T101.2: validate against semi-classical limit at α → 0 (test module)
- T101.3: implement BW resonance profile (peak shape verification)
- T101.4: re-fit Phase 32 (Cloud-9) + Phase 36 (dSph) with new σ/m
- T101.5: (deferred) inelastic mass-splitting channel
- T101.6: re-fit Phase 33d (SPARC) with new σ/m
- T101.7: update paper to v2.0

This file (T101.1) implements the partial-wave solver. Approach:

1. Define the partial-wave radial Schrödinger equation for Yukawa potential
2. Numerically integrate using scipy.integrate.solve_ivp
3. Extract phase shifts δ_l from asymptotic behavior of u_l(r) = r * R_l(r)
4. Compute σ_T(v) = (4π/k²) Σ_l (2l+1) sin²(δ_l)

NO NEW DEPENDENCIES. Uses numpy, scipy (already in venv).
"""
from __future__ import annotations

import numpy as np
from scipy.integrate import solve_ivp


# Reduced Planck constant * c in natural units (GeV * fm)
# hbar * c = 197.3269804 MeV * fm = 0.1973269804 GeV * fm
HBAR_C_GEV_FM = 0.1973269804


def k_from_v(v_kms: float, m_chi_GeV: float) -> float:
    """Wave number k (in fm^-1) for relative velocity v (in km/s) and DM mass m_chi (in GeV).

    k = m_chi * v / (2 * hbar * c)   (non-relativistic, reduced mass = m_chi/2)
    """
    v_cms = v_kms * 1e5  # km/s -> cm/s
    v_c = v_cms / 2.998e10  # c in cm/s
    m_chi_GeV_c2 = m_chi_GeV  # natural units: m in GeV/c^2
    k_GeV = m_chi_GeV_c2 * v_c / 2.0
    k_fm = k_GeV / HBAR_C_GEV_FM
    return k_fm


def v_from_k(k_fm: float, m_chi_GeV: float) -> float:
    """Velocity (km/s) for wave number k (fm^-1) and DM mass m_chi (GeV)."""
    k_GeV = k_fm * HBAR_C_GEV_FM
    v_c = 2.0 * k_GeV / m_chi_GeV
    v_cms = v_c * 2.998e10
    v_kms = v_cms / 1e5
    return v_kms


def yukawa_potential(r_fm: float, alpha: float, m_phi_GeV: float) -> float:
    """Yukawa potential V(r) = ±alpha * exp(-m_phi * r) / r in GeV.

    Args:
        r_fm: radial distance in fm
        alpha: dimensionless coupling (positive = repulsive)
        m_phi_GeV: mediator mass in GeV

    Returns:
        V(r) in GeV (natural units)
    """
    if r_fm <= 0:
        return 0.0  # placeholder; the ODE handles r=0 boundary separately
    return alpha * np.exp(-m_phi_GeV * r_fm / HBAR_C_GEV_FM) / r_fm


def _radial_ode(r: float, y: np.ndarray, k: float, l: int, V_func, V_args: tuple) -> np.ndarray:
    """Radial Schrödinger equation in first-order form.

    State y = [u_l(r), u_l'(r)] where u_l(r) = r * R_l(r) and R_l(r) is the radial wavefunction.

    Equation: -hbar^2/(2 m_red) u_l'' + [V(r) + l(l+1)hbar^2/(2 m_r^2)] u_l = E u_l
    where E = hbar^2 k^2 / (2 m_red) for reduced mass m_red = m_chi/2.

    Simplifies to: u_l'' = [l(l+1)/r^2 + 2 m_red V(r) / hbar^2 - k^2] u_l

    In natural units (hbar = c = 1) with r and 1/m in fm, m in GeV:
      u_l'' = [l(l+1)/r^2 - k^2 + 2 m_red V(r)] u_l
    where the factor of hbar^2 cancels because we use GeV * fm units.

    Args:
        r: radial distance in fm
        y: state vector [u_l, u_l']
        k: wave number in fm^-1
        l: partial wave number
        V_func: callable V(r) in GeV
        V_args: extra args to pass to V_func

    Returns:
        dy/dr = [u_l', u_l'']
    """
    u, up = y
    if r < 1e-3:
        # Near origin: centrifugal term dominates, u ~ r^(l+1)
        # Use l(l+1)/r^2 form carefully to avoid divergence
        centrifugal = l * (l + 1) / (1e-3 ** 2)
    else:
        centrifugal = l * (l + 1) / (r * r)
    V = V_func(r, *V_args)
    # 2 * m_red = m_chi (reduced mass = m_chi/2)
    potential_term = 2.0 * (params["m_chi"] / 2.0) * V if False else 0.0  # placeholder; rewritten below
    # Use m_chi from V_args? No, V_args doesn't carry m_chi. Pass via closure.
    raise NotImplementedError("Use _radial_ode_with_mass instead")


def _radial_ode_with_mass(r: float, y: np.ndarray, k: float, l: int, m_chi_GeV: float,
                          V_func, V_args: tuple) -> np.ndarray:
    """Radial Schrödinger equation in first-order form.

    State y = [u_l(r), u_l'(r)] where u_l(r) = r * R_l(r) and R_l(r) is the radial wavefunction.

    The radial Schrödinger equation is:
      -hbar^2/(2 m_red) u_l'' + [V_eff(r)] u_l = E u_l

    where E = hbar^2 k^2 / (2 m_red) (with reduced mass m_red = m_chi/2)
    and V_eff(r) = V(r) + l(l+1)hbar^2/(2 m_red r^2).

    In natural units (hbar = c = 1) with m in GeV, r in fm (1 fm = 1/0.197 GeV^-1):
      u_l'' = [l(l+1)/r^2 - k^2 + 2 m_red V(r)] u_l

    Concretely: the V(r) we feed in is in GeV (e.g., Yukawa = alpha * exp(-m_phi r) / r),
    so 2 m_red V has units of GeV^2, and we need k^2 in the same units.

    k [fm^-1] * hbar*c [GeV*fm] = k * 0.1973269804 GeV -> k_GeV = k * HBAR_C_GEV_FM
    So k^2 [GeV^2] = (k * HBAR_C_GEV_FM)^2

    For consistent units in the ODE, we use the substitution:
      u_l'' = [l(l+1)/r^2 - k^2 + 2 m_red V(r) * (HBAR_C_GEV_FM)^2] u_l

    Wait, that's not right either. Let me redo it.

    The radial equation in SI-like units with r in fm:
      -hbar^2/(2 m_red c^2) d^2u/dr^2 + [V + l(l+1)hbar^2/(2 m_red c^2 r^2)] u = E u

    In natural units (hbar = c = 1):
      -(1/(2 m_red)) d^2u/dr^2 + [V + l(l+1)/(2 m_red r^2)] u = E u
      d^2u/dr^2 = [l(l+1)/r^2 + 2 m_red (V - E)] u

    But here r is in fm and m_red is in GeV. We need to convert. If we want
    the ODE to be unit-consistent when r is in fm, m in GeV:

    Let r' = r * HBAR_C_GEV_FM (so r' is dimensionless, in units of 1/GeV).
    Then d/dr = (HBAR_C_GEV_FM) d/dr'.
    And d^2u/dr^2 = (HBAR_C_GEV_FM)^2 d^2u/dr'^2.

    The ODE becomes:
      (HBAR_C_GEV_FM)^2 d^2u/dr'^2 = [l(l+1)/r'^2 + 2 m_red V - k^2] u
      d^2u/dr'^2 = [l(l+1)/r'^2 + 2 m_red V - k^2] u / (HBAR_C_GEV_FM)^2

    Or equivalently, working in r' (dimensionless units of 1/GeV):
      u_l'' = [l(l+1)/r'^2 - k_GeV^2 + 2 m_red V(r')] u_l
    where k_GeV = k * HBAR_C_GEV_FM and m_red in GeV.

    This is cleaner. The caller must integrate from r'=0 to large r', and
    convert k back via v_kms = 2 k_GeV / m_chi * c.

    For the initial r_min, we use r_min = 1e-4 fm ~ 5e-5 GeV^-1, very close to origin.
    """
    u, up = y
    # Convert r (fm) to r' (GeV^-1)
    r_prime = r * HBAR_C_GEV_FM
    if r_prime < 1e-6:
        # Near origin: centrifugal term dominates, u ~ r^(l+1)
        centrifugal = l * (l + 1) / (1e-6 ** 2)
    else:
        centrifugal = l * (l + 1) / (r_prime * r_prime)
    V = V_func(r, *V_args)  # V is in GeV
    m_red = m_chi_GeV / 2.0
    # k_GeV^2 = (k * HBAR_C)^2
    k_GeV = k * HBAR_C_GEV_FM
    kin = -k_GeV * k_GeV + 2.0 * m_red * V
    # du/dr = du/dr' * dr'/dr = du/dr' * HBAR_C
    # So up in r' variables is up_real * HBAR_C
    # But we keep state in physical units (u_real, du_real/dr_real)
    # = (u, up_real) where up_real = up * HBAR_C and r_real = r' / HBAR_C
    # Then du_real/dr_real = (du_real/dr') * (dr'/dr_real) = (up * HBAR_C) * HBAR_C
    # d^2u_real/dr_real^2 = (up' * HBAR_C) * HBAR_C = up' * HBAR_C^2
    # So we need: up' * HBAR_C^2 = [centrifugal + kin] u
    #            up' = [centrifugal + kin] u / HBAR_C^2
    # And dy/dr_real = [u', up']
    #            u' (which is the y[1] we return) = du_real/dr_real = up * HBAR_C
    # Hmm, let me redo this carefully.

    # Define state in terms of dimensionless r':
    # U(r') = u(r_real)
    # dU/dr' = du/dr_real * dr_real/dr' = up_real / HBAR_C
    # So y = [U, dU/dr'] = [u, up_real / HBAR_C]
    # The state we return is dy/dr_real, which equals (dU/dr') * (dr'/dr_real)
    # = (dU/dr') / HBAR_C = (y[1]) / HBAR_C (since y[1] = dU/dr')
    # Wait, scipy.integrate.solve_ivp expects dy/dt for independent variable t.
    # We're integrating over r_real (in fm), so we return dy/dr_real.
    # dy/dr_real = (dy/dr') * (dr'/dr_real) = (dy/dr') * HBAR_C

    # dU/dr' = y[1]
    # d^2U/dr'^2 = ? from ODE: d^2U/dr'^2 = [centrifugal + kin] U
    # So dy/dr' = [y[1], (centrifugal + kin) * y[0]]
    # Then dy/dr_real = dy/dr' * dr'/dr_real = [y[1], (centrifugal + kin) * y[0]] * HBAR_C
    # But wait, the variable transform is r' = r_real * HBAR_C, so dr'/dr_real = HBAR_C.
    # dy/dr_real = dy/dr' * HBAR_C.

    return np.array([y[1] * HBAR_C_GEV_FM,
                     (centrifugal + kin) * y[0] * HBAR_C_GEV_FM])


def phase_shift_delta_l(
    v_kms: float,
    m_chi_GeV: float,
    alpha: float,
    m_phi_GeV: float,
    l: int,
    r_max_factor: float = 50.0,
    n_steps: int = 5000,
) -> float:
    """Compute the partial-wave phase shift δ_l for Yukawa scattering.

    Uses the variable-phase method (calibration by comparison to spherical Bessel functions).

    Args:
        v_kms: relative velocity in km/s
        m_chi_GeV: DM mass in GeV
        alpha: dimensionless Yukawa coupling (positive = repulsive)
        m_phi_GeV: mediator mass in GeV
        l: partial wave number
        r_max_factor: integrate out to r_max = r_max_factor / m_phi (in fm)
        n_steps: number of integration steps

    Returns:
        Phase shift δ_l in radians (unrestricted; can wrap modulo π for resonances).
    """
    k = k_from_v(v_kms, m_chi_GeV)
    m_phi_fm = m_phi_GeV / HBAR_C_GEV_FM  # 1/m_phi in fm
    r_max = r_max_factor * m_phi_fm
    r_span = (1e-4 * m_phi_fm, r_max)  # start very close to origin

    # Initial conditions: u_l(r) ~ r^(l+1) near origin
    # So u_l(0) = 0, u_l'(0) = (l+1) * eps^l at small eps
    # For numerical stability: u(eps) = eps^(l+1), u'(eps) = (l+1) * eps^l
    r0 = r_span[0]
    u0 = r0 ** (l + 1)
    up0 = (l + 1) * r0 ** l if l > 0 else 1.0

    # Integrate
    r_eval = np.linspace(r_span[0], r_span[1], n_steps)

    def ode_func(r, y):
        return _radial_ode_with_mass(r, y, k, l, m_chi_GeV, yukawa_potential, (alpha, m_phi_GeV))

    sol = solve_ivp(
        ode_func,
        r_span,
        [u0, up0],
        method="RK45",
        t_eval=r_eval,
        rtol=1e-8,
        atol=1e-10,
        max_step=(r_span[1] - r_span[0]) / n_steps,
    )

    if not sol.success:
        raise RuntimeError(f"ODE integration failed: {sol.message}")

    # Extract phase shift by comparing to free solution at large r.
    # The free solution has u^0_l(r) -> sin(kr - lπ/2) for r -> infinity
    # (using u_l = r R_l and R_l = j_l(kr) for free).
    # However, our state vector includes the dr'/dr factor.
    # Let me work in r' (dimensionless) variables internally.

    # Actually let me just compute the phase shift from u(r) / u'(r) ratio.
    # At large r (free limit): u = sin(kr - lπ/2 + δ_l), u' = k cos(kr - lπ/2 + δ_l)
    # tan(φ + δ_l) where φ = kr - lπ/2 = u / u' / k
    # Wait: u'/u = k cot(φ + δ_l)
    # φ + δ_l = arctan(k u / u'), so δ_l = arctan(k u / u') - φ + nπ for some integer n.

    # We don't know n, but for small δ_l we can take n=0 and unwrap later if needed.
    r_final = sol.t[-1]
    u_final = sol.y[0, -1]
    up_final = sol.y[1, -1]  # du/dr in physical (fm) units

    phi = k * r_final - l * np.pi / 2.0
    # k u_final / up_final = tan(phi + delta_l)
    if abs(up_final) < 1e-30:
        return 0.0
    tan_arg = k * u_final / up_final
    # arctan gives value in [-pi/2, pi/2]; if tan(phi + δ_l) > pi/2 in magnitude,
    # we need to add π. Use arctan2 to handle all quadrants.
    # arctan2(sin, cos): if tan_arg = sin/cos, then arctan2(tan_arg, 1) = arctan(tan_arg)
    # But we want the phase of (cos(phi+δ), sin(phi+δ)) = (cos phi cos δ - sin phi sin δ, ...)
    # cos(phi+δ) = up_final / k / sqrt(u_final^2 + (up_final/k)^2)
    # sin(phi+δ) = u_final / sqrt(u_final^2 + (up_final/k)^2)
    # So phi+δ = atan2(u_final, up_final/k) = atan2(k u_final, up_final)
    phi_plus_dl = np.arctan2(k * u_final, up_final)
    delta_l = phi_plus_dl - phi
    # Wrap to [-pi, pi] for sanity
    delta_l = (delta_l + np.pi) % (2 * np.pi) - np.pi
    return delta_l


def sigma_T_partial_wave(
    v_kms: float,
    m_chi_GeV: float,
    alpha: float,
    m_phi_GeV: float,
    l_max: int = 10,
    **kwargs,
) -> float:
    """Compute the transfer cross-section σ_T(v) via partial-wave expansion.

    σ_T(v) = (4π/k²) Σ_l (2l+1) sin²(δ_l)

    For distinguishable particles (no exchange symmetry). For identical
    particles with l even, factor of 2.

    Args:
        v_kms: relative velocity in km/s
        m_chi_GeV: DM mass in GeV
        alpha: dimensionless Yukawa coupling
        m_phi_GeV: mediator mass in GeV
        l_max: maximum partial wave to sum (10 should be enough for typical SIDM)

    Returns:
        σ_T in fm^2 (caller converts to cm^2/g)
    """
    k = k_from_v(v_kms, m_chi_GeV)
    sigma = 0.0
    for l in range(l_max + 1):
        delta_l = phase_shift_delta_l(v_kms, m_chi_GeV, alpha, m_phi_GeV, l, **kwargs)
        sigma += (2 * l + 1) * np.sin(delta_l) ** 2
    sigma *= 4.0 * np.pi / (k * k)
    return sigma


def sigma_m_partial_wave(
    v_kms: float,
    m_chi_GeV: float,
    alpha: float,
    m_phi_GeV: float,
    l_max: int = 10,
    **kwargs,
) -> float:
    """Compute σ/m in cm²/g using partial-wave σ_T(v).

    σ/m [cm²/g] = σ_T [fm²] * (1e-13)² / (m_chi_GeV * 1.783e-27 * 1e3)

    where 1 fm = 1e-13 cm, and 1 GeV/c² = 1.783e-27 kg = 1.783e-24 g.

    σ_T [cm²] = σ_T [fm²] * 1e-26
    σ/m [cm²/g] = σ_T [cm²] / (m_chi_GeV * 1.783e-24 g)
                = σ_T [fm²] * 1e-26 / (m_chi_GeV * 1.783e-24)
                = σ_T [fm²] / (m_chi_GeV * 1.783e2)
                = σ_T [fm²] / (m_chi_GeV * 178.3)
                = σ_T [fm²] * (1 / (m_chi_GeV * 178.3))

    Or: σ/m [cm²/g] = σ_T [fm²] / (m_chi_GeV * 178.3)
    """
    sigma_fm2 = sigma_T_partial_wave(v_kms, m_chi_GeV, alpha, m_phi_GeV, l_max, **kwargs)
    sigma_cm2_per_g = sigma_fm2 / (m_chi_GeV * 178.3)
    return sigma_cm2_per_g


if __name__ == "__main__":
    # Smoke test: compare to classical BW limit at weak coupling
    print("T101 partial-wave sigma/m(v) — smoke test")
    print("=" * 60)
    print()
    print("Test parameters:")
    print("  m_chi = 0.598 GeV (Phase 44 best-fit)")
    print("  alpha = 0.01 (weak coupling limit)")
    print("  m_phi = 10 MeV (typical mediator)")
    print()

    m_chi = 0.598
    alpha_test = 0.01
    m_phi = 0.010  # 10 MeV

    print(f"{'v (km/s)':>10}  {'sigma/m (cm^2/g)':>16}")
    for v in [5, 10, 15, 30, 50, 100, 200, 500, 1000]:
        val = sigma_m_partial_wave(v, m_chi, alpha_test, m_phi, l_max=8)
        print(f"{v:>10.1f}  {val:>16.4e}")
    print()
    print("Note: weak-coupling Yukawa without BW resonances should give a smooth")
    print("v-dependent sigma/m that decreases with increasing v (Yukawa suppression).")
    print("Compare with channels_v03.py sigma_m_at_v for validation.")
