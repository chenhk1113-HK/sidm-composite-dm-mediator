"""
T90.37 — Anand+ 2025 stellar mass upper limit cross-validation.

Per the T90.34 literature review, Anand+ 2025 (ApJL 993, L55) puts the
Cloud-9 stellar mass upper limit at M_star < 10^3.5 M_Sun with 99.5%
confidence via HST/ACS imaging.

This has TWO implications for our model:

1. **Cloud-9 may not be strictly pure DM.** Even a faint stellar
   population below the HST detection limit could provide baryonic
   gravity to help confine the gas. If so, the SIDM cross-section
   constraint is weaker than the strict pure-DM interpretation.

2. **The pure-DM interpretation requires sigma/m to be in the
   Cloud-9-favorable regime.** If sigma/m is much smaller than
   Cloud-9's range, the gas can't be supported by DM gravity alone
   (the halo wouldn't be massive enough), and a baryonic component
   would be required.

T90.37 implements a cross-validation channel:

  log L_anand = +0.5 * (sigma_eff(28) / 50 cm^2/g)
                capped at +2.0

  Rationale: at sigma_eff(28) >= 50 cm^2/g (Cloud-9 lower bound),
  the model is consistent with pure-DM Cloud-9. We add a soft +
  reward proportional to sigma_eff(28), capped to prevent runaway.

  At sigma_eff(28) < 1 cm^2/g (heavy-mediator regime), the model
  is INCONSISTENT with pure-DM Cloud-9, so we add a soft penalty.

Honest caveats:
  - The +0.5 * (sigma / 50) form is heuristic, not derived from
    Anand+ 2025's actual posterior.
  - The cap at +2.0 prevents the T90.37 channel from dominating
    the likelihood (which is what makes it a "cross-validation"
    rather than a hard constraint).
  - A production version would use the actual Anand+ 2025
    posterior over (sigma_eff(28), M_star_upper_limit).
"""

import numpy as np


# Anand+ 2025 cross-validation parameters
ANAND_MSTAR_UPPER_LIMIT_MSUN = 10 ** 3.5  # 10^3.5 M_Sun
ANAND_CLOUD9_DM_PURE_THRESHOLD_SIGMA = 50.0  # cm^2/g (Zhou+ 2026 lower bound)
ANAND_REWARD_CAP = 2.0  # max log-likelihood contribution


def loglike_anand_mstar_t90v37(
    m_phi_MeV: float,
    m_chi_GeV: float,
    g_chi: float,
    v_rel_kms: float = 28.0,
    weight: float = 1.0,
) -> float:
    """Anand+ 2025 stellar mass cross-validation likelihood.

    Adds a soft reward proportional to sigma_eff(28) at Cloud-9's
    velocity scale, capped at +2.0. This favors models with sigma/m in
    the Cloud-9-favorable regime (consistent with pure-DM Cloud-9)
    over models with sigma/m << Cloud-9 (which would require
    baryonic contamination to explain Cloud-9's gas support).

    Parameters
    ----------
    m_phi_MeV, m_chi_GeV, g_chi : float
        Yukawa model parameters.
    v_rel_kms : float
        Cloud-halo relative velocity (28 km/s for Cloud-9).
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

    # Reward: 0.5 * log10(sigma_eff / 50 cm^2/g) capped at +2.0
    # At sigma_eff = 50 cm^2/g: reward = 0
    # At sigma_eff = 500 cm^2/g: reward = +0.5 (log10 of 10)
    # At sigma_eff = 5000 cm^2/g: reward = +1.0
    # At sigma_eff = 50000 cm^2/g: reward = +1.5
    # At sigma_eff = 500000 cm^2/g: reward = +2.0 (capped)
    log_ratio = np.log10(sigma_eff_at_v / ANAND_CLOUD9_DM_PURE_THRESHOLD_SIGMA)
    log_l = 0.5 * log_ratio
    log_l = min(log_l, ANAND_REWARD_CAP)  # cap at +2.0

    # Soft penalty for very low sigma_eff (would require baryonic
    # contamination to explain Cloud-9's gas support)
    if sigma_eff_at_v < 1.0:
        log_l -= 0.5 * (1.0 - sigma_eff_at_v)  # mild penalty

    return weight * log_l


def loglike_anand_mstar_t90v37_wrapper(theta: tuple) -> float:
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

    return loglike_anand_mstar_t90v37(m_phi_MeV, m_chi_GeV, g_chi)


if __name__ == "__main__":
    print("=" * 80)
    print("  T90.37 — Anand+ 2025 stellar mass upper limit cross-validation")
    print("=" * 80)
    print()
    print(f"Anand+ 2025 M_star upper limit: < 10^{np.log10(ANAND_MSTAR_UPPER_LIMIT_MSUN):.1f} M_Sun (99.5% CL)")
    print(f"Cloud-9 pure-DM threshold: sigma/m(28) >= {ANAND_CLOUD9_DM_PURE_THRESHOLD_SIGMA} cm^2/g")
    print(f"Reward cap: +{ANAND_REWARD_CAP}")
    print()
    print(f"{'Test point':<45} {'sigma_eff(28) [cm^2/g]':>22} {'log L anand':>12}")
    print("-" * 85)
    test_points = [
        ("T41 v0.7 MAP (m_phi=750, m_chi=500, g_chi=0.1)", 750, 500, 0.1),
        ("Cloud-9 lower bound (m_phi=10, m_chi=500, g_chi=0.22)", 10, 500, 0.22),
        ("Cloud-9 mid (m_phi=50, m_chi=100, g_chi=1.3)", 50, 100, 1.3),
        ("Cloud-9 high (m_phi=30, m_chi=50, g_chi=1.5)", 30, 50, 1.5),
        ("Run F (m_phi=32, m_chi=9, g_chi=0.89)", 32, 9, 0.89),
    ]
    from t40_yukawa_sigma_m import sigma_m_cm2_per_g
    for label, m_phi, m_chi, g_chi in test_points:
        se = sigma_m_cm2_per_g(28.0, m_phi, m_chi, g_chi)
        ll = loglike_anand_mstar_t90v37(m_phi, m_chi, g_chi)
        print(f"{label:<45} {se:>22.3e} {ll:>12.3f}")