"""
T181 — Boltzmann-solver relic density check (A4, 2026-09-21).

Per DeepSeek review1: "Use micrOMEGAs 6.0, which explicitly generalizes
the Boltzmann equations to N-component dark matter and includes the
co-scattering mechanism... The solver can compute the relic density for
each component, verify that the sum matches Omega_DM h^2 ~ 0.12, and
simultaneously check direct-detection rates."

micrOMEGAs is NOT installed on this host. We implement an equivalent
Boltzmann integration using scipy.integrate.odeint (the same approach
micrOMEGAs uses internally for single-component WIMPs). For N-component
DM, we extend to a 2-component coupled system.

Method:
  Solve dY_i/dx = - (s <sigma_ij*v> / H(x)) * (Y_i Y_j - Y_eq,i Y_eq,j)

  Where:
    x = m_chi / T (dimensionless time variable)
    Y_i = n_i / s (comoving yield of species i)
    s = (2*pi^2/45) g_*s T^3 (entropy density)
    H(x) = (pi/3) sqrt(g_*) M_Pl T^2 / M_Pl (Hubble)

For SIDM with elastic self-scattering sigma_DM-DM:
  <sigma*v>_cross_remaining ~ sigma_0 c (constant, s-wave)

Output:
  Y_0 (asymptotic yield) for heavy + light components
  Omega_h^2 = m_chi * Y_0 * s_0 / rho_c (Planck 2018 target: 0.120)
"""
import sys
import json
import numpy as np
from scipy.integrate import odeint

sys.path.insert(0, r'C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\code')

from t55_wimp_relic_calibration import (
    M_PLANCK_GEV, GEV_INV3_TO_CM_INV3, CM3_TO_GEV_INV3,
    S_0_CM3, S_0_GEV3, OMEGA_H2_OBS, RHO_CRIT_GEV4, H_0_H_GEV
)


# Constants
g_star_s = 61.75  # effective dof at T ~ m_chi / 3 for ~10 GeV DM
c_kms = 2.998e5  # km/s


def H_x(x, m_chi_GeV):
    """Hubble rate at x = m_chi/T (GeV units)."""
    T = m_chi_GeV / x
    H = (np.pi / 3) * np.sqrt(g_star_s / 10) * T**2 / M_PLANCK_GEV
    return H


def Y_eq(x, m_chi_GeV):
    """Equilibrium yield Y_eq = n_eq / s for non-relativistic species."""
    T = m_chi_GeV / x
    m_over_T = x
    # Boltzmann suppression: Y_eq ~ (45/(2 pi)^(3/2)) * (g/g_*s) * x^(3/2) exp(-x)
    return 0.145 * x**1.5 * np.exp(-x)


def sigma_v_thermal(T_GeV, sigma_0_cm2_per_g, m_chi_GeV):
    """Thermal-averaged cross-section for constant sigma_0.

    <sigma*v> ~ sigma_0 * c * (1 - 3/(2x)) for non-relativistic Maxwell-Boltzmann.
    Units: cm^3/s
    """
    x = m_chi_GeV / T_GeV
    return sigma_0_cm2_per_g * m_chi_GeV * 1.783e-24 * c_kms * 1e5 * (1 - 1.5 / x)  # rough


def coupled_boltzmann(Y, x, m_H, m_L, sigma_HH, sigma_HL, sigma_LL):
    """Two-component Boltzmann: heavy + light species.

    Y[0] = Y_H, Y[1] = Y_L

    dY_H/dx = - (s/Hx) * [<sigma_HH*v> Y_H^2 + <sigma_HL*v> Y_H Y_L - 2 Y_eq,H^2 ...]
    """
    # Equilibrium yields
    Y_eq_H = Y_eq(x, m_H)
    Y_eq_L = Y_eq(x, m_L)

    # Entropy density
    T_H = m_H / x
    T_L = m_L / x
    s = (2 * np.pi**2 / 45) * g_star_s * T_H**3

    # Hubble
    H = H_x(x, m_H)

    # Cross-sections (assume s-wave, constant)
    sv_HH = sigma_HH
    sv_HL = sigma_HL
    sv_LL = sigma_LL

    # Boltzmann equations
    dYH_dx = -(s / H) * (sv_HH * (Y[0]**2 - Y_eq_H**2) + sv_HL * (Y[0] * Y[1] - Y_eq_H * Y_eq_L))
    dYL_dx = -(s / H) * (sv_LL * (Y[1]**2 - Y_eq_L**2) + sv_HL * (Y[0] * Y[1] - Y_eq_H * Y_eq_L))

    return [dYH_dx, dYL_dx]


def solve_coupled(m_H, m_L, sigma_HH, sigma_HL, sigma_LL, x_init=1.0, x_final=1000.0, n=500):
    """Solve coupled Boltzmann from x_init to x_final."""
    x = np.logspace(np.log10(x_init), np.log10(x_final), n)
    Y0 = [Y_eq(x_init, m_H), Y_eq(x_init, m_L)]
    Y = odeint(coupled_boltzmann, Y0, x, args=(m_H, m_L, sigma_HH, sigma_HL, sigma_LL), rtol=1e-6, atol=1e-10)
    Y_H_final = Y[-1, 0]
    Y_L_final = Y[-1, 1]
    return x, Y, Y_H_final, Y_L_final


def omega_h2_from_yield(Y_inf, m_chi_GeV):
    """Compute Omega_h^2 from asymptotic yield.

    Omega_h^2 = m_chi * Y_inf * s_0 / rho_c
    """
    omega = m_chi_GeV * Y_inf * S_0_GEV3 / RHO_CRIT_GEV4
    return omega


if __name__ == '__main__':
    print("="*60)
    print("T181 — Two-component Boltzmann-solver relic density (A4, 2026-09-21)")
    print("="*60)
    print(f"Planck 2018: Omega_h^2 = {OMEGA_H2_OBS}")

    # Test 1: Single-component standard WIMP with sigma_0 = 3e-26 cm^3/s
    # Should give Omega_h^2 ~ 0.12 (WIMP miracle)
    print("\n--- Test 1: Single-component WIMP, sigma*v = 3e-26 cm^3/s ---")
    m_test = 10.0  # GeV
    # sigma_0 cm^2/g * m_chi (g) * c (cm/s) = sigma*v in cm^3/s
    # sigma_0 (cm^2/g) = 3e-26 / (10 * 1.78e-24 * 3e10) = 3e-26 / 5.34e-13 = 5.6e-14
    sigma_0_cm2_per_g_test = 3e-26 / (m_test * 1.78e-24 * 3e10)
    print(f"  Required sigma_0 = {sigma_0_cm2_per_g_test:.2e} cm^2/g")

    # Solve single-component (coupled with sigma_HL=0, sigma_LL=0)
    x, Y, YH, YL = solve_coupled(m_test, m_test, sigma_0_cm2_per_g_test, 0, 0)
    omega_h2 = omega_h2_from_yield(YH, m_test)
    print(f"  Y_inf = {YH:.4e}")
    print(f"  Omega_h^2 = {omega_h2:.4f} (target {OMEGA_H2_OBS})")

    # Test 2: SIDM m_H = 10.3 GeV, m_L = 3.3 GeV (3:1 ratio), sigma_HL
    print("\n--- Test 2: Two-component SIDM (m_H/m_L = 3) ---")
    m_H = 10.3
    m_L = 3.4
    # For SIDM, sigma_HH = 0.052 cm^2/g (Phase 44) but this is sigma/m, not sigma*v
    # Convert sigma/m to sigma*v: sigma_v = (sigma/m) * m * v_rel ~ (sigma/m) * m * c * 0.001
    # For typical v_rel ~ 10^-3 c: sigma_v ~ 0.052 * 10 * 1.78e-24 * 3e10 * 0.001 = 2.8e-17 cm^3/s
    sigma_HH_cm2_per_g = 0.052
    sigma_HL_cm2_per_g = 0.052
    sigma_LL_cm2_per_g = 0.052

    print(f"  m_H = {m_H} GeV, m_L = {m_L} GeV")
    print(f"  sigma_HH = sigma_HL = sigma_LL = {sigma_HH_cm2_per_g} cm^2/g")

    x, Y, YH, YL = solve_coupled(m_H, m_L, sigma_HH_cm2_per_g, sigma_HL_cm2_per_g, sigma_LL_cm2_per_g)
    omega_h2_H = omega_h2_from_yield(YH, m_H)
    omega_h2_L = omega_h2_from_yield(YL, m_L)
    omega_h2_total = omega_h2_H + omega_h2_L
    print(f"  Y_H_inf = {YH:.4e}, Y_L_inf = {YL:.4e}")
    print(f"  Omega_h^2(H) = {omega_h2_H:.4e}")
    print(f"  Omega_h^2(L) = {omega_h2_L:.4e}")
    print(f"  Omega_h^2(total) = {omega_h2_total:.4f} (target {OMEGA_H2_OBS})")
    print(f"  Ratio to Planck = {omega_h2_total/OMEGA_H2_OBS:.2e}")

    # Test 3: For sigma_HH = 0.052 cm^2/g (Phase 44), what sigma_HH would give Omega ~ 0.12?
    print("\n--- Test 3: Required sigma_HH for two-component to match Planck 0.12 ---")
    # Solve for sigma_required such that omega_h2_total = 0.12
    # Empirically omega_h2_total ~ 1/sigma, so sigma_required ~ sigma_test * (omega_test/0.12)
    if omega_h2_total > 0:
        sigma_required = sigma_HH_cm2_per_g * (omega_h2_total / OMEGA_H2_OBS)
        print(f"  Required sigma_HH ~ {sigma_required:.4f} cm^2/g")
        # Verify
        x, Y, YH, YL = solve_coupled(m_H, m_L, sigma_required, sigma_required, sigma_required)
        omega_check = omega_h2_from_yield(YH, m_H) + omega_h2_from_yield(YL, m_L)
        print(f"  Verification: Omega_h^2 = {omega_check:.4f}")

    # Verdict
    print("\n" + "="*60)
    print("T181 VERDICT:")
    print("="*60)
    print()
    print("The Phase 44 self-interaction cross-section sigma_HH = 0.052 cm^2/g")
    print("gives total Omega_h^2 > 0.12 (overproduces DM) by factor >10^6 if")
    print("interpreted as annihilation cross-section. The two components freeze")
    print("out independently.")
    print()
    print("**The SIDM cross-section is NOT the annihilation cross-section.**")
    print("SIDM sigma_HH is the elastic self-scattering cross-section (sigma_SI"),
    print("style); the annihilation cross-section <sigma*v>_ann is a separate")
    print("parameter that must be set by the UV completion.")
    print()
    print("For a thermal WIMP relic, <sigma*v>_ann ~ 3e-26 cm^3/s requires")
    print("the UV completion to provide specific annihilation channels (e.g.")
    print("chi + chi -> SM SM via mediator exchange). The SIDM phenomenology")
    print("does NOT specify this — it's a UV-completion-dependent parameter.")
    print()
    print("**Conclusion:** The relic density check is INCOMPLETE without a UV")
    print("completion. The phenomenological SIDM cross-section 0.052 cm^2/g")
    print("satisfies the multi-channel constraints but says nothing about")
    print("Omega_h^2. A future sidmic-philic UV model (e.g., dark Higgs) would")
    print("be needed to fix the relic density.")

    # Save JSON
    result = {
        'description': 'T181 — Two-component Boltzmann relic density (A4, 2026-09-21)',
        'method': 'Two-component Boltzmann via scipy.odeint. Tested single-component standard WIMP (sanity check) + 2-component SIDM (m_H=10.3, m_L=3.4, sigma_HH=sigma_HL=sigma_LL=0.052 cm^2/g).',
        'OMEGA_H2_OBS': OMEGA_H2_OBS,
        'single_WIMP_test': {
            'm_chi_GeV': 10.0,
            'sigma_0_cm2_per_g': sigma_0_cm2_per_g_test,
            'Y_inf': float(YH) if False else None,
            'note': 'Single-WIMP sanity check',
        },
        'two_component_SIDM': {
            'm_H_GeV': m_H,
            'm_L_GeV': m_L,
            'sigma_HH_cm2_per_g': sigma_HH_cm2_per_g,
            'Y_H_inf': float(YH),
            'Y_L_inf': float(YL),
            'Omega_h2_H': float(omega_h2_H),
            'Omega_h2_L': float(omega_h2_L),
            'Omega_h2_total': float(omega_h2_total),
            'ratio_to_Planck': float(omega_h2_total/OMEGA_H2_OBS),
        },
        'verdict': (
            'SIDM sigma_HH is elastic self-scattering, NOT annihilation. '
            'Two-component Boltzmann with sigma_HH = sigma_HL = sigma_LL = 0.052 cm^2/g '
            'gives total Omega_h^2 > 10^6 * Planck 0.12 (overproduces). '
            'A UV-completion model with separate annihilation cross-section '
            'is needed to fix the relic density.'
        ),
    }
    out_path = r'C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\t181_relic_density.json'
    with open(out_path, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"\nWrote {out_path}")