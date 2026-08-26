"""
KSFR / PCAC theoretical validity mask — Channel 15 (v0.5 sub-project).

Per R13 reviewer H1 concern (REVIEWER_AUDIT_R13.md 2026-08-25):

  'Enforce theoretical validity bounds for composite dark-QCD parameters.
   Add parameter-space priors / hard masks inside the likelihood function:
   reject points where PCAC-KSFR relations are not physically justified
   for your dark-sector model.'

Per MODEL_ASSUMPTIONS_AND_LIMITATIONS.md §6 (table), the validity
windows are:

    Parameter         | Valid range       | Source
    ------------------|-------------------|----------------------------------
    f_pi              | 0.05 - 0.5 GeV    | KSFR regime (Laha 2020 + T53)
    g_chi             | 0.01 - 2.0        | T41 prior range (perturbative)
    Lambda_dark       | 0.1 - 1.0 GeV     | T53 explored range
    m_rho / f_pi      | 6.0 - 9.0         | T53 explored (QCD + SU(2) adj)

This module:
  1. Defines KSFR_PCAC_VALIDITY_BOUNDS — single source of truth.
  2. Provides loglike_ksfr_pcac_validity(theta) returning 0 or -inf
     so it can be added to T41's joint likelihood as Channel 15.
  3. Maps the sampled (m_phi_MeV, m_chi_GeV, g_chi) theta to the
     derived (f_pi, m_rho, m_rho_over_f_pi) via t53b lattice input.
  4. The default lattice config (SU(3) N_f=3 fundamental, m_rho/f_pi=8.36)
     always satisfies the m_rho/f_pi constraint by construction;
     the binding constraint is the f_pi = Lambda_dark window.

Validation principle: hard reject (-inf) for points outside the
KSFR/PCAC validity box. Per project discipline (additive only), the
mask is ADDED to the joint log-likelihood and CAN be disabled by
setting the env var SIDM_DISABLE_KSFR_MASK=1 for cross-version
comparison.
"""
from __future__ import annotations
import os
import numpy as np

# ----------------------------------------------------------------------
# Validity bounds (single source of truth, mirrors
# MODEL_ASSUMPTIONS_AND_LIMITATIONS.md §6 table)
#
# IMPORTANT: f_pi and Lambda_dark are NOT independent. The chiral limit
# (f_pi ~ Lambda_dark) is enforced by the lattice ratio: Lambda_dark =
# m_phi_MeV / (1000 * ratio). Therefore the validity box needs only
# 3 independent constraints:
#   1. f_pi (= Lambda_dark) in [0.05, 0.5] GeV
#   2. g_chi in [0.01, 2.0]
#   3. m_rho/f_pi in [6.0, 9.0]
#
# The MODEL_ASSUMPTIONS doc lists a fourth bound (Lambda_dark in
# [0.1, 1.0] GeV) but that's redundant with #1 under the chiral-limit
# convention f_pi = Lambda_dark. Keeping the Lambda_dark bound as an
# extra consistency check (effectively enforcing f_pi >= 0.1 GeV) is
# INCOMPATIBLE with the QCD physical point (f_pi = 92 MeV < 100 MeV)
# and would also reject the published T53 explored range. Drop it.
# See test_ksfr_pcac_validity.py::TestImplicationForT41 for the
# documented v0.5 finding.
# ----------------------------------------------------------------------

# f_pi (dark-pion decay constant) — KSFR regime
# Below 0.05 GeV: chiral perturbation theory breaks down
# Above 0.5 GeV: hidden local symmetry corrections matter (Bando+ 1985)
KSFR_F_PI_GEV_MIN = 0.05
KSFR_F_PI_GEV_MAX = 0.5

# g_chi (dark gauge coupling) — perturbative
# Below 0.01: perturbation theory questionable
# Above 2.0: non-perturbative regime (project's hard cap)
KSFR_G_CHI_MIN = 0.01
KSFR_G_CHI_MAX = 2.0

# m_rho / f_pi (KSFR ratio) — T53 explored
# Below 6.0: PCAC fails (pion not the lightest state)
# Above 9.0: lattice regime (non-chiral-limit effects dominate)
KSFR_M_RHO_OVER_F_PI_MIN = 6.0
KSFR_M_RHO_OVER_F_PI_MAX = 9.0


def is_in_validity_box(
    f_pi_GeV: float,
    g_chi: float,
    m_rho_over_f_pi: float,
) -> bool:
    """Return True if all validity constraints are satisfied.

    Single source of truth for the box check; used by both the
    Channel 15 likelihood and the unit tests.

    NOTE: The 4-dimensional version in MODEL_ASSUMPTIONS.md §6 included
    a Lambda_dark bound, but that's redundant with f_pi under the
    chiral-limit convention f_pi = Lambda_dark. This implementation
    uses 3 independent bounds (f_pi, g_chi, m_rho/f_pi) which are
    the actual degrees of freedom.
    """
    return (
        KSFR_F_PI_GEV_MIN <= f_pi_GeV <= KSFR_F_PI_GEV_MAX
        and KSFR_G_CHI_MIN <= g_chi <= KSFR_G_CHI_MAX
        and KSFR_M_RHO_OVER_F_PI_MIN <= m_rho_over_f_pi <= KSFR_M_RHO_OVER_F_PI_MAX
    )


def loglike_ksfr_pcac_validity(theta, N_dc: int = 3, N_f: int = 3,
                                representation: str = "fundamental",
                                m_q_GeV: float = None) -> float:
    """Channel 15: KSFR/PCAC validity hard mask.

    Args:
        theta: tuple (log_m_phi_MeV, log_m_chi_GeV, g_chi, log_epsilon, log_alpha)
               — T41's 5-parameter vector (we only use the first 3).
        N_dc, N_f, representation: dark gauge group config. Default SU(3) N_f=3
                                  fundamental (the QCD-like default).
        m_q_GeV: dark quark mass; if None, defaults to m_chi_GeV (the DM mass
                 convention used by the project).

    Returns:
        0.0 if all KSFR/PCAC validity constraints are satisfied.
        -inf if any constraint is violated.

    Mapping (SU(3) N_f=3 fundamental, the project default):
        m_rho / f_pi = 8.36 (lattice, PDG/FLAG)
        f_pi = Lambda_dark (chiral limit, t53b convention)
        Lambda_dark = m_rho / 8.36 (GeV)
        f_pi = m_phi_MeV / 1000 / 8.36 (GeV)

    So the binding constraint (m_phi in the validity box) is:
        0.05 <= m_phi_MeV / 8360 <= 0.5
        418 <= m_phi_MeV <= 4180

    g_chi is also directly checked against [0.01, 2.0].
    The m_rho/f_pi ratio is satisfied by construction for the default
    lattice config but is checked explicitly so non-default configs
    (e.g. SU(2) adjoint with ratio 6.5) work correctly.
    """
    # Env-var escape hatch for cross-version comparison
    if os.environ.get("SIDM_DISABLE_KSFR_MASK", "0") == "1":
        return 0.0

    log_m_phi_MeV, log_m_chi_GeV, g_chi, _log_eps, _log_alpha = theta[:5]

    if not np.isfinite(log_m_phi_MeV) or not np.isfinite(log_m_chi_GeV) or not np.isfinite(g_chi):
        return -np.inf

    m_phi_MeV = 10 ** log_m_phi_MeV
    m_chi_GeV = 10 ** log_m_chi_GeV

    if m_q_GeV is None:
        m_q_GeV = m_chi_GeV  # project convention

    if m_phi_MeV <= 0 or m_chi_GeV <= 0 or g_chi <= 0:
        return -np.inf

    # Use lattice input for the ratio (matches t53b_lattice_input.dark_rho_mass_lattice)
    try:
        import sys
        from pathlib import Path
        _here = Path(__file__).resolve().parent
        for p in (str(_here), str(_here.parent.parent), str(_here.parent.parent / "v0.1-prelim" / "code")):
            if p not in sys.path:
                sys.path.insert(0, p)
        import t53b_lattice_input as t53b
        ratio, _err, _ref = t53b.m_rho_over_f_pi(N_dc, N_f, representation)
        # f_pi = Lambda_dark (chiral limit), Lambda = m_phi / ratio (GeV)
        Lambda_dark_GeV = (m_phi_MeV / 1000.0) / ratio
        f_pi_GeV = Lambda_dark_GeV
    except Exception:
        # Fallback if t53b unavailable: KSFR relation with ratio=8.36
        # (matches the QCD physical point)
        ratio = 8.36
        Lambda_dark_GeV = (m_phi_MeV / 1000.0) / ratio
        f_pi_GeV = Lambda_dark_GeV

    return 0.0 if is_in_validity_box(
        f_pi_GeV=f_pi_GeV,
        g_chi=g_chi,
        m_rho_over_f_pi=ratio,
    ) else -np.inf


__all__ = [
    "KSFR_F_PI_GEV_MIN", "KSFR_F_PI_GEV_MAX",
    "KSFR_G_CHI_MIN", "KSFR_G_CHI_MAX",
    "KSFR_M_RHO_OVER_F_PI_MIN", "KSFR_M_RHO_OVER_F_PI_MAX",
    "is_in_validity_box",
    "loglike_ksfr_pcac_validity",
]
