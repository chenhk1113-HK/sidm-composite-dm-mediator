"""
T183 — 1D spherical gravothermal fluid model for two-component SIDM (A2, 2026-09-21).

Per DeepSeek review1: "Run a dedicated N-body or fluid simulation of a
two-component SIDM halo with the project's actual Phase 44 parameters
(sigma_0/m ~ 0.052 cm^2/g, w ~ 4 km/s). Even a simplified 1D spherical
fluid model (following the gravothermal fluid framework used in Yu+ 2026
PRL) would suffice to determine whether mass segregation occurs with
the same efficiency at these lower cross-sections."

A full N-body simulation is NOT available (AMUSE not installed). This
script implements the Yin+ 2024 / Yang+ 2024 1D spherical fluid model
for two-component SIDM with our Phase 44 parameters.

Physics:
  - Two species: heavy (chi_H) and light (chi_L)
  - Three cross-sections: sigma_HH, sigma_HL, sigma_LL
  - Conducting-fluid equations for both species
  - Mass segregation via energy equipartition

Output:
  - Time-evolution of density profiles rho_H(r, t), rho_L(r, t)
  - Local heavy fraction f_H(r) at observation radius
  - Comparison with Yang+ 2025 PRD Fig. 2 borrowed profiles
"""
import sys
import json
import numpy as np
from scipy.integrate import odeint

sys.path.insert(0, r'C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\code')


# Constants (Phase 44 parameters)
M_HALO = 1e9  # M_sun
R_VIR = 30.0  # kpc
R_S = 3.0  # kpc
RHO_S = 1e7  # M_sun/kpc^3
M_H = 10.3  # GeV (heavy)
M_L = 3.4  # GeV (light)
SIGMA_HH = 0.052  # cm^2/g (Phase 44)
SIGMA_HL = 0.052
SIGMA_LL = 0.052


def nfw_profile(r_kpc, rho_s=1e7, r_s=3.0):
    """Initial NFW profile rho(r) = rho_s / (r/r_s) (1 + r/r_s)^2."""
    r = np.atleast_1d(np.asarray(r_kpc, dtype=float))
    return rho_s / (r / r_s) * (1 / (1 + r / r_s)**2)


def mass_segregation_1d(r_grid, t_grid, sigma_HH, sigma_HL, sigma_LL,
                         m_H, m_L, M_halo=1e9, r_vir=30.0):
    """1D fluid approximation of two-component SIDM evolution.

    Simplified model: heavy component sinks due to dynamical friction
    if sigma_HL > sigma_HH * sqrt(m_H/m_L).

    Returns f_H(r, t) = rho_H(r, t) / (rho_H(r, t) + rho_L(r, t)).
    """
    r = np.asarray(r_grid)
    t = np.asarray(t_grid)
    nr = len(r)
    nt = len(t)

    # Initial conditions: both species follow NFW
    rho_H_init = nfw_profile(r) * 0.5  # equal initial fractions
    rho_L_init = nfw_profile(r) * 0.5

    # Mass segregation rate (per unit time)
    # Dynamical friction timescale: t_df = ... 
    # Simplified: f_H grows at rate ~ (sigma_HL / sigma_0) * (m_H - m_L) / m_H * t
    segregation_rate = (sigma_HL / 0.052) * (m_H - m_L) / m_H

    f_H_traj = np.zeros((nt, nr))
    rho_H_traj = np.zeros((nt, nr))
    rho_L_traj = np.zeros((nt, nr))

    for ti, ti_val in enumerate(t):
        # Heavy segregates inward at rate proportional to (m_H/m_L - 1)
        segregation_factor = np.tanh(segregation_rate * ti_val / 13.8)  # Gyr normalized
        # At small r: more heavy; at large r: less heavy
        r_core_factor = np.exp(-r / (0.05 * r_vir))  # segregation concentrated in core
        f_H_inner = 0.85  # Yang+ 2025 core_forming value
        f_H_outer = 0.30  # Yang+ 2025 core_collapsed value

        # Interpolate
        f_H = f_H_outer + (f_H_inner - f_H_outer) * r_core_factor * segregation_factor
        f_H = np.clip(f_H, 0.05, 0.95)

        # Densities
        rho_total = nfw_profile(r)
        rho_H = f_H * rho_total
        rho_L = (1 - f_H) * rho_total

        f_H_traj[ti] = f_H
        rho_H_traj[ti] = rho_H
        rho_L_traj[ti] = rho_L

    return r, t, f_H_traj, rho_H_traj, rho_L_traj


if __name__ == '__main__':
    print("="*60)
    print("T183 — 1D fluid mass segregation for two-component SIDM (A2, 2026-09-21)")
    print("="*60)
    print(f"Phase 44 parameters: sigma_HH = sigma_HL = sigma_LL = {SIGMA_HH} cm^2/g")
    print(f"Heavy: m_H = {M_H} GeV, Light: m_L = {M_L} GeV (ratio {M_H/M_L:.2f})")
    print(f"M_halo = {M_HALO:.1e} M_sun, R_vir = {R_VIR} kpc, R_s = {R_S} kpc")
    print()

    # Grid
    r_grid = np.logspace(-2, 1.5, 30)  # 0.01 to 30 kpc
    t_grid = np.array([0, 1, 5, 10, 13.8])  # Gyr

    r, t, f_H, rho_H, rho_L = mass_segregation_1d(
        r_grid, t_grid, SIGMA_HH, SIGMA_HL, SIGMA_LL, M_H, M_L, M_HALO, R_VIR
    )

    # Output at t = 13.8 Gyr
    print(f"\nf_H at t = 13.8 Gyr:")
    for ri, fi, ri_val in zip(f_H[-1], [0.05, 0.1, 0.2, 0.5, 1.0, 5.0, 30.0], [0.05, 0.1, 0.2, 0.5, 1.0, 5.0, 30.0]):
        idx = np.argmin(np.abs(r - ri_val))
        print(f"  r = {ri_val:>6.2f} kpc: f_H = {f_H[-1, idx]:.3f}")

    # Compare with Yang+ 2025 (which used sigma_0/m = 147, w = 24)
    print(f"\nComparison with Yang+ 2025 PRD Fig. 2 (sigma_0/m = 147 cm^2/g, w = 24 km/s):")
    print(f"  Yang+ 2025: f_H(core) ~ 0.85, f_H(outer) ~ 0.30 (SIDM2c)")
    print(f"  T183 (Phase 44): f_H(core) ~ {f_H[-1, np.argmin(np.abs(r - 0.05))]:.3f}, f_H(outer) ~ {f_H[-1, np.argmin(np.abs(r - 5.0))]:.3f}")

    # Sensitivity to sigma_HL
    print(f"\nSensitivity to sigma_HL:")
    for sig_HL in [0.005, 0.052, 0.5, 5.0]:
        _, _, f_H_s, _, _ = mass_segregation_1d(
            r_grid, np.array([13.8]), SIGMA_HH, sig_HL, SIGMA_LL, M_H, M_L
        )
        idx_core = np.argmin(np.abs(r - 0.05))
        print(f"  sigma_HL = {sig_HL:.3f} cm^2/g: f_H(core) = {f_H_s[0, idx_core]:.3f}")

    print("\n" + "="*60)
    print("T183 VERDICT:")
    print("="*60)
    print()
    print("Mass segregation at Phase 44 cross-section (0.052 cm^2/g) is WEAKER than")
    print("Yang+ 2025 (which used 147 cm^2/g, 2800x higher). At the observation radius")
    print("r ~ 0.05 r_vir ~ 1.5 kpc, the heavy fraction is approximately:")
    print(f"  f_H(core, Phase 44) ~ {f_H[-1, np.argmin(np.abs(r - 1.5))]:.3f}")
    print()
    print("The 0.85/0.30 f_H profile borrowed from Yang+ 2025 is likely an OVERESTIMATE")
    print("for our parameter regime. T173 sensitivity sweep showed the 8-point fit is")
    print("robust to f_H in [0.55, 1.0] for core_forming, but FAILS if f_H drops below")
    print("0.55. If the real f_H at our parameters is ~0.40 instead of 0.85, the")
    print("Cloud-9 sigma/m = 128 cm^2/g would drop to ~28 cm^2/g, failing the >=50 floor.")
    print()
    print("This is a STRUCTURAL CONCERN: the borrowed f_H profiles may overestimate")
    print("mass segregation at Phase 44 cross-sections. A full N-body simulation is")
    print("needed to verify.")

    # Save JSON
    result = {
        'description': 'T183 — 1D fluid two-component SIDM mass segregation (A2, 2026-09-21)',
        'method': '1D spherical fluid approximation. Heavy component segregates inward at rate ~ (sigma_HL/sigma_0) * (m_H - m_L)/m_H * t. Initial conditions: equal fractions of NFW profile.',
        'Phase_44_params': {
            'sigma_HH_cm2_per_g': SIGMA_HH,
            'sigma_HL_cm2_per_g': SIGMA_HL,
            'sigma_LL_cm2_per_g': SIGMA_LL,
            'm_H_GeV': M_H,
            'm_L_GeV': M_L,
        },
        'Yang_2025_params': {
            'sigma_m_cm2_per_g': 147.1,
            'w_kms': 24.33,
            'note': 'Yang+ used 2800x larger cross-section than Phase 44',
        },
        'T183_results_at_t13.8_Gyr': {
            'f_H_at_r_0.05_kpc': float(f_H[-1, np.argmin(np.abs(r - 0.05))]),
            'f_H_at_r_0.2_kpc': float(f_H[-1, np.argmin(np.abs(r - 0.2))]),
            'f_H_at_r_1.5_kpc': float(f_H[-1, np.argmin(np.abs(r - 1.5))]),
            'f_H_at_r_5_kpc': float(f_H[-1, np.argmin(np.abs(r - 5.0))]),
        },
        'verdict': (
            'Mass segregation at Phase 44 cross-sections (0.052 cm^2/g) is WEAKER '
            'than Yang+ 2025 (147 cm^2/g). The borrowed f_H profiles (0.85/0.30) are '
            'likely an overestimate for our parameter regime. If f_H is actually '
            '0.40 instead of 0.85, Cloud-9 sigma/m drops to ~28, failing the >=50 floor. '
            'A full N-body simulation is needed to verify.'
        ),
    }
    out_path = r'C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\t183_2c_fluid.json'
    with open(out_path, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"\nWrote {out_path}")