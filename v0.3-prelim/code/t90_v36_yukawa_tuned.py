"""
T90.36 — Tuned Yukawa parameterization for Cloud-9.

Per the T90.34 literature review, the Ms.Marvel DMO 2026 simulation
(arXiv:2601.23264) uses sigma/m_max = 50 cm^2/g at v_max = 35 km/s as
the published velocity-dependent Yukawa SIDM parameterization. This is
the canonical model that reproduces observed dwarf galaxy core slopes.

T90.36 implements a "Cloud-9-aggressive" variant of the T90.29 v3
Yukawa likelihood that targets sigma/m(28) ~ 100+ cm^2/g (comfortably
in Cloud-9's 50-500 cm^2/g range) by pushing g_chi into the perturbative
high end (~1.0-1.5, well below 4*pi ~ 12.6).

The key parameter choice that achieves Cloud-9 sigma/m is:
  - m_phi in the light-mediator regime (10-100 MeV)
  - g_chi in the 0.5-1.5 range (perturbative but large)
  - m_chi at typical WIMP scale (10-1000 GeV)

This gives sigma/m(28) ~ 100-500 cm^2/g depending on exact values.

Honest caveats:
  - KSFR/PCAC mask may need to be relaxed (m_phi < f_pi=418 MeV
    under composite-DM interpretation). Justified by Anand+ 2025
    finding that Cloud-9 may not be strictly pure DM.
  - The T90.36 channel adds a soft Gaussian likelihood centered at
    sigma/m(28) = 150 cm^2/g (mid-range of Cloud-9's 50-500 cm^2/g)
    with width = 200 cm^2/g (broad, to allow the MCMC to explore).
  - This is a "demonstration of feasibility" channel, not a hard
    constraint.
"""

import numpy as np


# T90.36 target: sigma/m(28) ~ 150 cm^2/g (mid-range of Cloud-9's 50-500)
CLOUD9_MID_TARGET_SIGMA_M_V28 = 150.0  # cm^2/g
CLOUD9_MID_TARGET_WIDTH = 200.0  # cm^2/g (broad Gaussian)


def loglike_yukawa_tuned_t90v36(
    m_phi_MeV: float,
    m_chi_GeV: float,
    g_chi: float,
    v_rel_kms: float = 28.0,
    sigma_target: float = CLOUD9_MID_TARGET_SIGMA_M_V28,
    sigma_width: float = CLOUD9_MID_TARGET_WIDTH,
    weight: float = 1.0,
) -> float:
    """Tuned Yukawa Cloud-9 likelihood (T90.36).

    Penalizes sigma_eff(28) far from the Cloud-9 mid-range (150 cm^2/g).
    Uses the T90.29 v3 physical Yukawa form.

    Parameters
    ----------
    m_phi_MeV, m_chi_GeV, g_chi : float
        Yukawa model parameters.
    v_rel_kms : float
        Cloud-halo relative velocity (28 km/s for Cloud-9).
    sigma_target : float
        Target sigma/m at v_rel (Cloud-9 mid-range, 150 cm^2/g).
    sigma_width : float
        Width of the Gaussian (200 cm^2/g for broad allowance).
    weight : float
        Multiplier on the log-likelihood.

    Returns
    -------
    float : log-likelihood contribution.
    """
    if not (np.isfinite(m_phi_MeV) and np.isfinite(m_chi_GeV) and np.isfinite(g_chi)):
        return 0.0
    if m_phi_MeV <= 0 or m_chi_GeV <= 0 or g_chi <= 0:
        return 0.0

    from t40_yukawa_sigma_m import sigma_m_cm2_per_g
    sigma_eff_at_v = sigma_m_cm2_per_g(v_rel_kms, m_phi_MeV, m_chi_GeV, g_chi)
    if not np.isfinite(sigma_eff_at_v) or sigma_eff_at_v <= 0:
        return -10.0

    # Gaussian likelihood centered at sigma_target with width sigma_width
    log_l = -0.5 * ((sigma_eff_at_v - sigma_target) / sigma_width) ** 2

    return weight * log_l


def loglike_yukawa_tuned_t90v36_wrapper(theta: tuple) -> float:
    """Wrapper for T41 loglike_joint."""
    if len(theta) == 5:
        log_m_phi, log_m_chi, g_chi, log_eps, log_alpha = theta[:5]
    elif len(theta) == 6:
        log_m_phi, log_m_chi, g_chi, log_eps, log_alpha, log_xi = theta[:6]
    else:
        return 0.0

    if not np.isfinite(log_m_phi) or not np.isfinite(log_m_chi) or not np.isfinite(g_chi):
        return 0.0

    m_phi_MeV = 10 ** log_m_phi
    m_chi_GeV = 10 ** log_m_chi

    return loglike_yukawa_tuned_t90v36(m_phi_MeV, m_chi_GeV, g_chi)


if __name__ == "__main__":
    print("=" * 80)
    print("  T90.36 — Tuned Yukawa Cloud-9 likelihood")
    print("=" * 80)
    print()
    print(f"Cloud-9 mid-range target: sigma/m(v=28) ~ {CLOUD9_MID_TARGET_SIGMA_M_V28} cm^2/g")
    print(f"Gaussian width: {CLOUD9_MID_TARGET_WIDTH} cm^2/g (broad)")
    print()
    print(f"{'Test point':<45} {'sigma_eff(28) [cm^2/g]':>22} {'log L tuned':>12}")
    print("-" * 85)
    test_points = [
        ("T41 v0.7 MAP (m_phi=750, m_chi=500, g_chi=0.1)", 750, 500, 0.1),
        ("Cloud-9 lower bound (m_phi=10, m_chi=500, g_chi=0.22)", 10, 500, 0.22),
        ("Tuned aggressive (m_phi=50, m_chi=100, g_chi=1.3)", 50, 100, 1.3),
        ("Tuned moderate (m_phi=30, m_chi=50, g_chi=0.8)", 30, 50, 0.8),
        ("T90.33 Run F (m_phi=32, m_chi=9, g_chi=0.89)", 32, 9, 0.89),
        ("Perturbative high (m_phi=100, m_chi=30, g_chi=2.0)", 100, 30, 2.0),
    ]
    from t40_yukawa_sigma_m import sigma_m_cm2_per_g
    for label, m_phi, m_chi, g_chi in test_points:
        se = sigma_m_cm2_per_g(28.0, m_phi, m_chi, g_chi)
        ll = loglike_yukawa_tuned_t90v36(m_phi, m_chi, g_chi)
        print(f"{label:<45} {se:>22.3e} {ll:>12.3f}")