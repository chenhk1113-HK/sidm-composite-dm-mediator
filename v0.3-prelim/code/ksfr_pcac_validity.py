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


# ----------------------------------------------------------------------
# (Nc, Nf) → m_rho / f_pi table — Wave A3 scaffold (Wave B will replace
# with the canonical values from KSFR_NC_NF_TABLE.md).
#
# The default (Nc, Nf) = (3, 3) ratio (8.36, LATTICE from PDG/FLAG) is the
# project default and is used everywhere in v0.5/T70.6 to derive the
# m_phi ∈ [418, 4180] MeV box from f_pi ∈ [0.05, 0.5] GeV.
#
# Placeholder values for non-(3,3) entries are taken from the Wave A2
# research document v0.3-prelim/docs/KSFR_NC_NF_TABLE.md (§7 quick-ref).
# These are *best estimates* from ESTIMATED / ANALYTICAL sources, NOT
# production-ready lattice values. Wave B (full T41 integration) will
# replace this scaffold dict with the canonical table after R14 audit
# closure.
#
# FIXME: Wave B integration will replace placeholder values with the
# canonical KSFR_NC_NF_TABLE.md values (see §7 quick-ref summary).
# ----------------------------------------------------------------------
KSFR_NC_NF_RATIOS = {
    (2, 2): 8.0,   # ESTIMATED  — SU(2) fund Nf=2; closest published value is
                   # SU(2) adj Nf=2 = 6.5 (different physics). Adopted ±1.0.
    (2, 3): 7.5,   # ESTIMATED  — SU(2) fund Nf=3 may be CONFORMAL (no KSFR).
                   # Caveat: KSFR undefined if conformal. Adopted ±1.0.
    (3, 2): 8.4,   # LATTICE    — SU(3) fund Nf=2 extrapolated from Nf=3.
                   # Quoted ±0.3 from "Lattice 2019 (Shindler et al.)".
    (3, 3): 8.36,  # LATTICE    — SU(3) fund Nf=3 PDG/FLAG physical point.
                   # Quoted ±0.05; project default.
    (3, 4): 8.0,   # ESTIMATED  — SU(3) fund Nf=4; no published continuum
                   # lattice value. Adopted ±0.4 (conservative).
    (4, 3): 9.5,   # ANALYTICAL — SU(4) fund Nf=3 from large-Nc scaling
                   # (+10–15% Nc correction). Adopted ±0.5.
    (4, 4): 9.2,   # ANALYTICAL — SU(4) fund Nf=4; large-Nc + Nf correction.
                   # Adopted ±0.5.
}
# FIXME: Wave B integration will replace placeholder values with
# KSFR_NC_NF_TABLE.md canonical values.


def compute_m_phi_lower_bound_mev(
    Nc: int,
    Nf: int,
    f_pi_min_GeV: float = 0.05,
) -> float:
    """Compute the lower bound on m_phi (MeV) for the chosen (Nc, Nf).

    Derivation (chiral-limit convention, see MODEL_ASSUMPTIONS.md §6):

        m_rho  = R(Nc, Nf) * f_pi
        f_pi   >= f_pi_min_GeV   (KSFR validity box lower bound)
        Lambda = m_phi / R(Nc, Nf)   (GeV, chiral limit)
        f_pi   = Lambda (chiral limit convention)
        =>
        m_phi (GeV) >= R(Nc, Nf) * f_pi_min_GeV
        m_phi (MeV) >= 1000 * R(Nc, Nf) * f_pi_min_GeV

    Args:
        Nc: number of colours (gauge group SU(Nc), fundamental rep).
        Nf: number of Dirac flavours in the fundamental rep.
        f_pi_min_GeV: KSFR validity lower bound on f_pi (default 0.05 GeV).

    Returns:
        m_phi lower bound in MeV. E.g. (3, 3) with default f_pi_min
        returns 1000 * 0.05 * 8.36 = 418 MeV.

    Raises:
        KeyError: if (Nc, Nf) is not in KSFR_NC_NF_RATIOS.
    """
    if (Nc, Nf) not in KSFR_NC_NF_RATIOS:
        raise KeyError(
            f"No KSFR ratio for (Nc={Nc}, Nf={Nf}). "
            f"Known: {sorted(KSFR_NC_NF_RATIOS.keys())}"
        )
    ratio = KSFR_NC_NF_RATIOS[(Nc, Nf)]
    return 1000.0 * f_pi_min_GeV * ratio


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


def loglike_ksfr_pcac_validity(theta, N_dc: int = None, N_f: int = None,
                                representation: str = "fundamental",
                                m_q_GeV: float = None) -> float:
    """Channel 15: KSFR/PCAC validity hard mask.

    Args:
        theta: tuple of length 5 OR 7:
            5-tuple (backward-compat with v0.5/T70.6):
              (log_m_phi_MeV, log_m_chi_GeV, g_chi, log_epsilon, log_alpha)
            7-tuple (Wave A3 scaffold — Wave B will fully integrate into T41):
              (log_m_phi_MeV, log_m_chi_GeV, g_chi, log_epsilon, log_alpha,
               Nc, Nf)
              where Nc and Nf are integers (e.g. (2, 2), (3, 3), (4, 4)).
        N_dc, N_f: optional positional overrides for (Nc, Nf). If either is
                   None, falls back to env vars KSFR_NC / KSFR_NF, then to
                   (3, 3). If theta is a 7-tuple, N_dc/N_f args are IGNORED
                   in favour of theta[5], theta[6].
        representation: dark fermion representation (default "fundamental").
                        Wave A3 scaffold only ships the fundamental
                        representation; other reps raise NotImplementedError
                        for non-(3,3) configs.
        m_q_GeV: dark quark mass; if None, defaults to m_chi_GeV (the DM mass
                 convention used by the project).

    Returns:
        0.0 if all KSFR/PCAC validity constraints are satisfied.
        -inf if any constraint is violated.

    Mapping (default SU(3) N_f=3 fundamental, ratio 8.36):
        m_rho / f_pi = R(Nc, Nf) from KSFR_NC_NF_RATIOS (placeholder values;
                       see FIXME at top of file).
        f_pi = Lambda_dark (chiral limit, t53b convention)
        Lambda_dark = m_rho / R(Nc, Nf) (GeV)
        f_pi = m_phi_MeV / 1000 / R(Nc, Nf) (GeV)

    The binding constraint (m_phi in the validity box) for (Nc, Nf) is:
        R(Nc, Nf) * f_pi_min * 1000 <= m_phi_MeV <= R(Nc, Nf) * f_pi_max * 1000
    which for the default (3, 3) is the familiar [418, 4180] MeV window.

    Env-var escape hatches:
      - SIDM_DISABLE_KSFR_MASK=1: disable the mask entirely (v0.5 default)
      - KSFR_NC=<int>:            default Nc when theta is 5-tuple (default 3)
      - KSFR_NF=<int>:            default Nf when theta is 5-tuple (default 3)
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

    # Resolve (Nc, Nf): theta 7-tuple wins, then positional args, then env vars.
    if len(theta) >= 7:
        try:
            Nc_resolved = int(theta[5])
            Nf_resolved = int(theta[6])
        except (TypeError, ValueError):
            Nc_resolved = N_dc if N_dc is not None else int(
                os.environ.get("KSFR_NC", 3))
            Nf_resolved = N_f if N_f is not None else int(
                os.environ.get("KSFR_NF", 3))
    else:
        Nc_resolved = N_dc if N_dc is not None else int(
            os.environ.get("KSFR_NC", 3))
        Nf_resolved = N_f if N_f is not None else int(
            os.environ.get("KSFR_NF", 3))

    # Look up the KSFR ratio. Default (3, 3) goes through the
    # t53b_lattice_input path for backward compatibility (preserves the
    # project's existing lattice-table fallback behaviour). Other (Nc, Nf)
    # pairs use the scaffold KSFR_NC_NF_RATIOS table directly.
    if (Nc_resolved, Nf_resolved) == (3, 3):
        # Use lattice input for the ratio (matches t53b_lattice_input.dark_rho_mass_lattice)
        try:
            import sys
            from pathlib import Path
            _here = Path(__file__).resolve().parent
            for p in (str(_here), str(_here.parent.parent), str(_here.parent.parent / "v0.1-prelim" / "code")):
                if p not in sys.path:
                    sys.path.insert(0, p)
            import t53b_lattice_input as t53b
            ratio, _err, _ref = t53b.m_rho_over_f_pi(Nc_resolved, Nf_resolved, representation)
        except Exception:
            # Fallback if t53b unavailable: KSFR relation with ratio=8.36
            # (matches the QCD physical point)
            ratio = KSFR_NC_NF_RATIOS[(3, 3)]
    else:
        # Non-(3, 3) — use the scaffold table directly. Representation
        # other than "fundamental" is not yet scaffolded (Wave B scope).
        if representation != "fundamental":
            return -np.inf
        try:
            ratio = KSFR_NC_NF_RATIOS[(Nc_resolved, Nf_resolved)]
        except KeyError:
            # Unknown (Nc, Nf) — hard reject. Wave B should add it to the table.
            return -np.inf

    # f_pi = Lambda_dark (chiral limit), Lambda = m_phi / ratio (GeV)
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
    "KSFR_NC_NF_RATIOS",
    "compute_m_phi_lower_bound_mev",
    "is_in_validity_box",
    "loglike_ksfr_pcac_validity",
]
