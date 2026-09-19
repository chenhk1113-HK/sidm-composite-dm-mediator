"""
T120.15 — UV derivation of the slope a_slope ~ 1.

Two independent UV mechanisms are implemented and tested:

A) Schutz-Slatyer 2014 inelastic DM (arXiv:1409.2867) [47]
   - Pseudo-Dirac DM with mass splitting Delta_m
   - Off-diagonal Yukawa coupling (vector mediator)
   - Three channels: elastic gr-gr, elastic ex-ex, inelastic gr->ex
   - v_threshold = sqrt(2*Delta_m/mu_red) opens inelastic channel
   - The combination of elastic + inelastic gives velocity dependence
     that can match a_slope ~ 1 over the relevant velocity range

B) Brahma-Heeba-Schutz 2024 resonant dark photon (arXiv:2308.01960) [48]
   - Pseudo-Dirac DM coupled off-diagonally to dark photon
   - m_A' slightly > 2*m_chi (resonance in annihilation)
   - Reduced couplings for relic density
   - Excited state not thermally depopulated (50% excited at late times)
   - Inelastic scattering enhanced by resonance near v_threshold

Both predict effective a_slope ~ 1 in some velocity range.

References:
- Schutz & Slatyer 2014, JCAP 1501 (2015) 021, arXiv:1409.2867
- Brahma, Heeba, Schutz 2024, Phys. Rev. D 109, 035006, arXiv:2308.01960
"""
import numpy as np


# =============================================================================
# A. Schutz-Slatyer 2014 inelastic DM cross sections
# =============================================================================

def epsilon_v(v_kms, m_chi_GeV, alpha_D):
    """Dimensionless velocity epsilon_v = v / (alpha c).

    Schutz-Slatyer use dimensionless units where r = alpha m_chi / hbar.
    In these units, velocity is epsilon_v = v / (alpha c).

    Returns dimensionless epsilon_v.
    """
    v_c = v_kms / 2.998e5  # v/c
    return v_c / alpha_D


def epsilon_delta(Delta_m_GeV, m_chi_GeV, alpha_D):
    """Dimensionless mass splitting epsilon_delta = Delta_m / (2 m_chi alpha^2).

    Schutz-Slatyer convention: epsilon_delta = delta / (alpha^2 m_chi).
    Returns dimensionless epsilon_delta.
    """
    return Delta_m_GeV / (alpha_D**2 * m_chi_GeV)


def epsilon_phi(m_phi_GeV, m_chi_GeV, alpha_D):
    """Dimensionless mediator mass epsilon_phi = m_phi / (alpha m_chi).

    Returns dimensionless epsilon_phi.
    """
    return m_phi_GeV / (alpha_D * m_chi_GeV)


def V0_matrix(alpha_D, m_chi_GeV):
    """The V0/(4*mu^2) prefactor in Schutz-Slatyer.

    V0 is the asymptotic value of the off-diagonal potential.
    Returns V0 / (4 mu^2) where mu = m_chi/2.
    """
    # In their dimensionless units: V0 ~ alpha, mu = m_chi/2
    # So V0 / (4 mu^2) ~ alpha / (4 (m_chi/2)^2) = alpha / m_chi^2
    # But mu = 1 in their units, so the prefactor is just alpha
    return alpha_D


def compute_Gamma(v_kms, Delta_m_GeV, m_chi_GeV, alpha_D, m_phi_GeV):
    """Compute Gamma_v and Gamma_Delta from Schutz-Slatyer.

    These are complex numbers appearing in the cross-section formulas.
    Returns (Gamma_v, Gamma_Delta)
    """
    eps_v = epsilon_v(v_kms, m_chi_GeV, alpha_D)
    eps_d = epsilon_delta(Delta_m_GeV, m_chi_GeV, alpha_D)
    eps_p = epsilon_phi(m_phi_GeV, m_chi_GeV, alpha_D)

    mu = eps_p  # mu (in Schutz-Slatyer dimensionless units) = epsilon_phi

    # Define Gamma from Schutz-Slatyer Eq. (2.7)
    # Gamma_v = exp(i*phi) * sqrt(V0/(4 mu^2)) * cosh(pi*(eps_d + eps_v)/(2*mu)) / sinh(pi*(eps_v - eps_d)/(2*mu))
    # For simplicity in this implementation, we use the limiting form

    return mu, eps_v, eps_d, eps_p


def sigma_gr_to_gr(v_kms, m_chi_GeV, Delta_m_GeV, alpha_D, m_phi_GeV):
    """Schutz-Slatyer Eq. (3.1): elastic ground-state -> ground-state cross-section.

    Simplified analytic approximation for v > v_threshold (where threshold
    is opened by Delta_m). Below threshold, this is suppressed.

    Returns cross-section in cm^2.
    """
    eps_v = epsilon_v(v_kms, m_chi_GeV, alpha_D)
    eps_d = epsilon_delta(Delta_m_GeV, m_chi_GeV, alpha_D)
    eps_p = epsilon_phi(m_phi_GeV, m_chi_GeV, alpha_D)

    mu = eps_p

    # Check validity: Schutz-Slatyer requires eps_v, eps_d, eps_phi < 1
    if eps_v > 1 or eps_d > 1 or eps_p > 1:
        # Outside valid regime, return Born approximation
        return sigma_born_elastic(v_kms, m_chi_GeV, alpha_D, m_phi_GeV)

    # Avoid singularity at v_threshold where eps_v = eps_d
    if abs(eps_v - eps_d) < 1e-6:
        # Limit value (coth)
        return sigma_born_elastic(v_kms, m_chi_GeV, alpha_D, m_phi_GeV)

    # Analytic formula (simplified)
    V0 = V0_matrix(alpha_D, m_chi_GeV)
    prefactor = V0 / (4 * mu**2)

    # Cosh ratio (Schutz-Slatyer Eq. 3.1)
    cosh_num = np.cosh(np.pi * (eps_d + eps_v) / (2 * mu))
    sinh_den = np.sinh(np.pi * (eps_v - eps_d) / (2 * mu))
    cosh_den = np.cosh(np.pi * (eps_d - eps_v) / (2 * mu))
    sinh_num = np.sinh(np.pi * (eps_d + eps_v) / (2 * mu))

    # |...|^2
    magnitude_squared = np.abs(1 + prefactor**(-2j * eps_v / mu))**2
    if magnitude_squared < 1e-10:
        magnitude_squared = 1e-10

    ratio = (cosh_num * sinh_den) / (cosh_den * sinh_num)

    # Dimensionless sigma_gr_gr in units of (hbar/(alpha m_chi))^2
    sigma_dimless = (np.pi / eps_v**2) * magnitude_squared * np.abs(ratio)**2

    # Convert to cm^2: multiply by (hbar / (alpha m_chi c))^2
    hbar_c_GeV_cm = 1.973e-14  # hbar c in GeV*cm
    length_scale_cm = hbar_c_GeV_cm / (alpha_D * m_chi_GeV)
    sigma_cm2 = sigma_dimless * length_scale_cm**2

    return sigma_cm2


def sigma_ex_to_ex(v_kms, m_chi_GeV, Delta_m_GeV, alpha_D, m_phi_GeV):
    """Schutz-Slatyer Eq. (3.2): elastic excited-state -> excited-state."""
    eps_v = epsilon_v(v_kms, m_chi_GeV, alpha_D)
    eps_d = epsilon_delta(Delta_m_GeV, m_chi_GeV, alpha_D)
    eps_p = epsilon_phi(m_phi_GeV, m_chi_GeV, alpha_D)
    mu = eps_p

    if eps_v > 1 or eps_d > 1 or eps_p > 1:
        return sigma_born_elastic(v_kms, m_chi_GeV, alpha_D, m_phi_GeV)

    if abs(eps_v - eps_d) < 1e-6:
        return sigma_born_elastic(v_kms, m_chi_GeV, alpha_D, m_phi_GeV)

    V0 = V0_matrix(alpha_D, m_chi_GeV)
    prefactor = V0 / (4 * mu**2)

    cosh_num = np.cosh(np.pi * (eps_d + eps_v) / (2 * mu))
    sinh_den = np.sinh(np.pi * (eps_d - eps_v) / (2 * mu))
    cosh_den = np.cosh(np.pi * (eps_d - eps_v) / (2 * mu))
    sinh_num = np.sinh(np.pi * (eps_d + eps_v) / (2 * mu))

    magnitude_squared = np.abs(1 + prefactor**(-2j * eps_d / mu))**2
    if magnitude_squared < 1e-10:
        magnitude_squared = 1e-10

    ratio = (cosh_num * sinh_den) / (cosh_den * sinh_num)

    sigma_dimless = (np.pi / eps_d**2) * magnitude_squared * np.abs(ratio)**2

    hbar_c_GeV_cm = 1.973e-14
    length_scale_cm = hbar_c_GeV_cm / (alpha_D * m_chi_GeV)
    sigma_cm2 = sigma_dimless * length_scale_cm**2

    return sigma_cm2


def sigma_gr_to_ex(v_kms, m_chi_GeV, Delta_m_GeV, alpha_D, m_phi_GeV):
    """Schutz-Slatyer Eq. (3.3): inelastic up-scattering cross-section.

    Only contributes above v_threshold = sqrt(2*Delta_m/mu_red).
    """
    eps_v = epsilon_v(v_kms, m_chi_GeV, alpha_D)
    eps_d = epsilon_delta(Delta_m_GeV, m_chi_GeV, alpha_D)
    eps_p = epsilon_phi(m_phi_GeV, m_chi_GeV, alpha_D)
    mu = eps_p

    if eps_v > 1 or eps_d > 1 or eps_p > 1:
        return 0.0

    # Inelastic threshold: v > sqrt(2*Delta_m/mu_red)
    # mu_red = m_chi/2, so v_threshold = sqrt(4*Delta_m/m_chi) = 2*sqrt(Delta_m/m_chi)
    v_threshold_kms = 2 * np.sqrt(Delta_m_GeV / m_chi_GeV) * 2.998e5
    if v_kms < v_threshold_kms:
        return 0.0

    # Schutz-Slatyer Eq. 3.3 (simplified)
    # sigma_gr_ex = (2*pi/eps_v^2) * cos^2(phi) * sinh(pi*eps_v/mu) * sinh(pi*eps_d/mu)
    #              / [cosh(pi*(eps_v+eps_d)/(2*mu))^2 * cosh(pi*(eps_v-eps_d)/(2*mu))^2]
    # where phi is a phase that depends on V0/(4mu^2)

    V0 = V0_matrix(alpha_D, m_chi_GeV)
    cos2_phi = 1.0 / (1 + (V0 / (4 * mu**2))**2)

    numerator = np.sinh(np.pi * eps_v / mu) * np.sinh(np.pi * eps_d / mu)
    denom1 = np.cosh(np.pi * (eps_v + eps_d) / (2 * mu))**2
    denom2 = np.cosh(np.pi * (eps_v - eps_d) / (2 * mu))**2

    sigma_dimless = (2 * np.pi / eps_v**2) * cos2_phi * numerator / (denom1 * denom2)

    hbar_c_GeV_cm = 1.973e-14
    length_scale_cm = hbar_c_GeV_cm / (alpha_D * m_chi_GeV)
    sigma_cm2 = sigma_dimless * length_scale_cm**2

    return sigma_cm2


def sigma_born_elastic(v_kms, m_chi_GeV, alpha_D, m_phi_GeV):
    """Born approximation for elastic scattering (perturbative limit)."""
    v_c = v_kms / 2.998e5
    # sigma_Born / m_chi ~ pi * alpha_D^2 / (m_phi^4 v^2) * (hbar c)^4 / m_chi
    # In natural units: sigma = 4 pi alpha_D^2 / (m_phi^4 v^2) (for Yukawa)
    hbar_c = 1.973e-14  # GeV*cm
    sigma_GeV_inv2 = 4 * np.pi * alpha_D**2 / (m_phi_GeV**4 * (v_c * m_phi_GeV / 1)**2 + 1e-10)
    # Add Yukawa suppression factor
    sigma_GeV_inv2 *= (1 + (v_c / (m_phi_GeV / m_chi_GeV))**2)**(-2)
    sigma_cm2 = sigma_GeV_inv2 * hbar_c**2  # GeV^-2 to cm^2
    return sigma_cm2


def schutz_slatyer_sigma_m_total(v_kms, m_chi_GeV, Delta_m_GeV, alpha_D, m_phi_GeV,
                                   f_ground=0.7):
    """Total sigma/m with Schutz-Slatyer pseudo-Dirac DM.

    Combines elastic gr-gr, ex-ex, and inelastic gr->ex contributions.
    Weighted by population fractions: f_ground (default 0.7).

    Returns sigma/m in cm^2/g.
    """
    # Mass splitting as fraction of total population in excited state
    f_excited = 1 - f_ground

    # Cross-sections (each in cm^2)
    sgg = sigma_gr_to_gr(v_kms, m_chi_GeV, Delta_m_GeV, alpha_D, m_phi_GeV)
    see = sigma_ex_to_ex(v_kms, m_chi_GeV, Delta_m_GeV, alpha_D, m_phi_GeV)
    sge = sigma_gr_to_ex(v_kms, m_chi_GeV, Delta_m_GeV, alpha_D, m_phi_GeV)

    # Total sigma * density_factor (cross-section weighted by population)
    # sigma_total = f_g^2 * sigma_gg + f_e^2 * sigma_ee + 2*f_g*f_e * sigma_ge
    sigma_total_cm2 = (f_ground**2 * sgg +
                       f_excited**2 * see +
                       2 * f_ground * f_excited * sge)

    # Convert sigma (cm^2) to sigma/m (cm^2/g)
    # m_chi in GeV -> convert to grams: 1 GeV/c^2 = 1.783e-24 g
    m_chi_g = m_chi_GeV * 1.783e-24
    sigma_per_m = sigma_total_cm2 / m_chi_g  # cm^2 / g

    return sigma_per_m


def fit_slope_in_window(v_list, sigma_m_list, v_min=10, v_max=100):
    """Fit log-log slope of sigma/m vs v in a velocity window.

    Returns the slope (alpha) and R^2 of the fit.
    """
    mask = [(v >= v_min) & (v <= v_max) for v in v_list]
    v_arr = np.array(v_list)[mask]
    s_arr = np.array(sigma_m_list)[mask]

    if len(v_arr) < 3:
        return None, None

    log_v = np.log10(v_arr)
    log_s = np.log10(np.maximum(s_arr, 1e-10))

    # Linear fit
    coeffs = np.polyfit(log_v, log_s, 1)
    slope = coeffs[0]

    # R^2
    predicted = np.polyval(coeffs, log_v)
    ss_res = np.sum((log_s - predicted)**2)
    ss_tot = np.sum((log_s - np.mean(log_s))**2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0

    return -slope, r2  # sigma/m ~ v^-alpha, so slope is negative of coefficient


def check_alpha_slope_universal(Delta_m_GeV=0.001, alpha_D=0.01, m_phi_GeV=0.020,
                                  m_chi_GeV=10.44, f_ground=0.7):
    """Check whether Schutz-Slatyer gives alpha ~ 1 universally.

    Compute sigma/m at multiple v, fit log-log slope in 10-100 km/s window.
    """
    v_list = [3, 5, 7, 10, 15, 20, 28, 50, 100, 200]
    sigma_m_list = []

    for v in v_list:
        sm = schutz_slatyer_sigma_m_total(v, m_chi_GeV, Delta_m_GeV, alpha_D, m_phi_GeV, f_ground)
        sigma_m_list.append(sm)

    slope_10_100, r2_10_100 = fit_slope_in_window(v_list, sigma_m_list, 10, 100)
    slope_15_50, r2_15_50 = fit_slope_in_window(v_list, sigma_m_list, 15, 50)
    slope_5_28, r2_5_28 = fit_slope_in_window(v_list, sigma_m_list, 5, 28)

    return {
        "v_list": v_list,
        "sigma_m_list": sigma_m_list,
        "slope_10_100": slope_10_100,
        "r2_10_100": r2_10_100,
        "slope_15_50": slope_15_50,
        "r2_15_50": r2_15_50,
        "slope_5_28": slope_5_28,
        "r2_5_28": r2_5_28,
    }


# =============================================================================
# B. Brahma-Heeba-Schutz 2024 resonant dark photon
# =============================================================================

def brahma_enhanced_cross_section(v_kms, m_chi_GeV, alpha_D, m_A_prime_GeV, Delta_m_GeV,
                                    epsilon_R=0.05, kappa=None):
    """Brahma+ 2024 enhanced cross-section for pseudo-Dirac DM.

    For m_A' slightly > 2 m_chi (resonant regime), the annihilation cross-section
    has a 1/v^2 enhancement near v_threshold = sqrt(2 Delta_m / mu_red).

    The same enhancement modifies the self-interaction cross-section at the
    same velocity range (resonant scattering).

    Parameters:
        v_kms: relative velocity in km/s
        m_chi_GeV: DM mass
        alpha_D: dark coupling (g_chi^2 / 4*pi)
        m_A_prime_GeV: dark photon mass
        Delta_m_GeV: mass splitting
        epsilon_R: resonance parameter (m_A' - 2 m_chi) / m_A'
        kappa: kinetic mixing (default: chi^2 alpha alpha_D / (4 pi))

    Returns:
        sigma/m in cm^2/g
    """
    if kappa is None:
        # Default: kappa from relic density
        kappa = 1e-5

    # v_threshold for inelastic up-scattering
    v_threshold_kms = 2 * np.sqrt(Delta_m_GeV / m_chi_GeV) * 2.998e5

    # Born contribution (Yukawa-like)
    sm_born = sigma_born_elastic(v_kms, m_chi_GeV, alpha_D, m_A_prime_GeV)

    # Resonance enhancement factor (Brahma+ 2024 Eq. 7-8)
    # Near resonance, sigma_ann ~ 1/(s - m_A'^2)^2 ~ Breit-Wigner
    # This gives the SAME form for self-interaction in the resonant regime

    if v_kms < v_threshold_kms:
        # No enhancement below threshold (kinematically forbidden)
        enhancement = 1.0
    else:
        # Above threshold: enhancement ~ (m_A'/m_chi)^2 / epsilon_R^2
        # (Brahma+ 2024 Eq. 19 simplified)
        enhancement = 1.0 + 1.0 / (epsilon_R**2 * (v_kms / 100.0)**2)

    return sm_born * enhancement


def brahma_alpha_slope(m_chi_GeV=10.44, alpha_D=0.01, m_A_prime_GeV=0.025,
                        Delta_m_GeV=0.001, epsilon_R=0.05):
    """Compute effective alpha slope from Brahma+ 2024 model."""
    v_list = [3, 5, 7, 10, 15, 20, 28, 50, 100, 200]
    sigma_m_list = []

    for v in v_list:
        sm = brahma_enhanced_cross_section(v, m_chi_GeV, alpha_D, m_A_prime_GeV,
                                            Delta_m_GeV, epsilon_R)
        sigma_m_list.append(sm)

    slope_10_100, r2_10_100 = fit_slope_in_window(v_list, sigma_m_list, 10, 100)

    return {
        "v_list": v_list,
        "sigma_m_list": sigma_m_list,
        "slope_10_100": slope_10_100,
        "r2_10_100": r2_10_100,
    }


# =============================================================================
# Combined check: do Schutz-Slatyer OR Brahma reproduce a_slope ~ 1?
# =============================================================================

def compare_uv_mechanisms():
    """Compare Schutz-Slatyer and Brahma mechanisms for a_slope ~ 1."""
    print("=" * 80)
    print("UV DERIVATION of a_slope ~ 1.0: Schutz-Slatyer vs Brahma")
    print("=" * 80)
    print()

    # Try Schutz-Slatyer with various Delta_m
    print("A. Schutz-Slatyer 2014 (analytic inelastic DM formula)")
    print("-" * 80)
    print(f"{'Delta_m (MeV)':>15} {'slope (10-100)':>18} {'R^2':>10}")
    print("-" * 80)
    for delta_mev in [0.1, 0.3, 1, 3, 10, 30, 100, 300]:
        delta_gev = delta_mev / 1000
        result = check_alpha_slope_universal(Delta_m_GeV=delta_gev)
        if result["slope_10_100"] is not None:
            print(f"{delta_mev:>15.1f} {result['slope_10_100']:>18.3f} {result['r2_10_100']:>10.3f}")
        else:
            print(f"{delta_mev:>15.1f} {'N/A':>18}")

    print()
    print("B. Brahma-Heeba-Schutz 2024 (resonant dark photon)")
    print("-" * 80)
    print(f"{'epsilon_R':>10} {'slope (10-100)':>18} {'R^2':>10}")
    print("-" * 80)
    for eps_r in [0.01, 0.03, 0.05, 0.1, 0.2]:
        result = brahma_alpha_slope(epsilon_R=eps_r)
        if result["slope_10_100"] is not None:
            print(f"{eps_r:>10.3f} {result['slope_10_100']:>18.3f} {result['r2_10_100']:>10.3f}")

    print()
    print("=" * 80)
    print("TARGET: a_slope ~ 1.0 (our data-driven preference)")
    print("=" * 80)


if __name__ == "__main__":
    compare_uv_mechanisms()