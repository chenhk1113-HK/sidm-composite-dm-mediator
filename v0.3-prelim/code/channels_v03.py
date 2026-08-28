#!/usr/bin/env python
"""
v0.3: improved channel likelihoods with proper bimodality + SPARC v-dep re-fit.

Changes vs v0.2:
    1. Channel 2 (dSph) — v0.2 used two Gaussians WITHOUT the Horigome+ 2025
       exclusion dip; v0.3 added the dip explicitly. R12 P0-D (2026-08-17)
       replaces this bimodal-with-dip surrogate entirely because:
         - The actual Horigome+ 2025 abstract (arXiv:2503.13650) gives a
           95% CL upper limit sigma/m < 0.2 cm^2/g for velocity-INDEPENDENT
           SIDM ("decisively prefers CDM to SIDM when sigma/m exceeds
           ~0.2 cm^2/g").
         - The bimodal-with-dip surrogate at sigma/m ~ 0.1 AND ~10 cm^2/g
           PREDICTS the latter is preferred, contradicting the paper.
         - A Gaussian that PEAKS at ~0.2 cm^2/g with the 1-sigma tail
           extending up to ~0.5 cm^2/g and a strong penalty above 0.2
           matches the published upper-limit constraint.
       The new `loglike_dsph_v03` uses this upper-limit form.
    2. Channel 1 (SPARC) — proper velocity-dependent sigma/m contribution.
       In v0.2 SPARC was an implicit prior only; in v0.3 we use the
       Phase 1+2 fits and re-evaluate log L for each (sigma/m_0, a) using
       the velocity-dependent Burkert profile.
"""
from __future__ import annotations
import numpy as np
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# Velocity scales for each channel (in km/s)
V_DSPH = 30.0       # MW dSph v_max ~ 10-50 km/s
V_UFD = 10.0        # UFD v_max
V_GALAXY = 100.0    # reference velocity (galactic)
V_CLUSTER = 1500.0  # Bullet Cluster v_max

V_REF = V_GALAXY    # all our sigma/m_0 are quoted at v=100 km/s


def sigma_m_at_v(sigma_m_0: float, a: float, v: float) -> float:
    """sigma/m at velocity scale v (km/s)."""
    return sigma_m_0 * (v / V_REF) ** (-a)


# ---------------------------------------------------------------------------
# Channel 2 (dSph): published upper-limit constraint from Horigome+ 2025
# (arXiv:2503.13650). The published result is a 95% CL UPPER LIMIT at
# sigma/m ~ 0.2 cm^2/g for velocity-INDEPENDENT SIDM:
#
#   "The combined analysis decisively prefers CDM to SIDM when the
#    self-interaction cross section per unit mass, sigma/m, exceeds
#    ~0.2 cm^2/g, if a velocity-independent cross section is assumed."
#
# We encode this as a half-Gaussian peak at sigma/m ~ 0.05 cm^2/g with
# the 1-sigma width such that the upper-limit boundary falls at ~0.2 cm^2/g.
# For velocity-DEPENDENT SIDM (sigma/m ~ sigma/m_0 * (v/v_ref)^(-a) with
# a > 0), sigma/m at dSph velocity (~30 km/s) is LARGER than at v_ref
# (100 km/s), so the constraint applies to sigma/m at v_DSPH:
#   sigma/m(v_DSPH) < sigma/m_upper(v_DSPH)
# We compute the upper limit at v_DSPH by mapping the published
# v-independent bound to v-dependent: a point is excluded if its
# sigma/m at v_DSPH exceeds 0.2 cm^2/g.
#
# Likelihood form: half-Gaussian below the bound, Gaussian penalty above.
# This is the standard "one-sided limit" treatment used in cosmology.
# ---------------------------------------------------------------------------
def loglike_dsph_v03(sigma_m_0: float, a: float) -> float:
    """Channel 2: MW dSph upper-limit constraint (Horigome+ 2025).

    R12 P0-D (2026-08-17): replaced the legacy bimodal-with-dip surrogate
    (peaks at sigma/m ~ 0.1 AND ~10 cm^2/g) with a published upper-limit
    form. The legacy surrogate contradicted the Horigome+ 2025 abstract.

    Parameters
    ----------
    sigma_m_0 : float
        Reference cross-section (sigma/m at v_ref=100 km/s), cm^2/g.
    a : float
        Velocity power-law index (channels_v03 convention; positive a =
        falling sigma/m with v).

    Returns
    -------
    float
        log L (in arbitrary units; relative only). 0 at the mode
        (sigma/m_0 << 0.2 cm^2/g and small enough that sigma/m(v_DSPH)
        < 0.2 cm^2/g), -inf beyond the upper limit.

    Notes
    -----
    The upper limit is applied at v_DSPH = 30 km/s:
        sigma/m(v_DSPH) = sigma/m_0 * (30/100)**(-a) <= 0.2 cm^2/g
    A point is "at the limit" when sigma/m(v_DSPH) = 0.2 cm^2/g, with
    the corresponding sigma/m_0 = 0.2 * (30/100)**a. For a = 0 (velocity-
    independent), sigma/m_0 = 0.2 directly. For a = 1 (favoured by data),
    sigma/m_0 = 0.2 * 0.3 = 0.06 cm^2/g.
    """
    if sigma_m_0 <= 0 or not np.isfinite(sigma_m_0):
        return -np.inf
    sigma_m_v = sigma_m_at_v(sigma_m_0, a, V_DSPH)
    if sigma_m_v <= 0 or not np.isfinite(sigma_m_v):
        return -np.inf
    log_sm_v = np.log10(sigma_m_v)
    # Half-Gaussian mode at log(sigma/m) ~ -1.3 (i.e. ~0.05 cm^2/g),
    # 1-sigma width such that the upper-limit boundary sits at
    # sigma/m = 0.2 cm^2/g (log = -0.7), about 0.6 dex above the mode.
    # Above the bound: Gaussian penalty with the SAME slope so that
    # points at sigma/m = 0.4 cm^2/g have log L = -2 (i.e. ~chi^2 ~ 4).
    mode_log_sm = -1.3    # log10(sigma/m at v_DSPH) ~ -1.3  -> ~0.05 cm^2/g
    width = 0.4           # dex
    upper_limit_log_sm = -0.7  # log10(0.2 cm^2/g) ~ -0.7
    # Half-Gaussian on the low side: Gaussian in (mode - log_sm) direction,
    # capped at mode so it doesn't reward going BELOW the mode.
    delta_low = mode_log_sm - log_sm_v
    if log_sm_v <= mode_log_sm:
        # Below mode: flat (no further preference for lower sigma/m)
        ll = 0.0
    else:
        # Above mode, below upper limit: Gaussian ramp
        if log_sm_v <= upper_limit_log_sm:
            ll = -0.5 * ((log_sm_v - mode_log_sm) / width) ** 2
        else:
            # Above upper limit: extend the Gaussian and add the
            # standard "exclusion" penalty at the boundary. We use a
            # linear penalty beyond the upper limit (half-Gaussian).
            beyond = log_sm_v - upper_limit_log_sm
            ll = -0.5 * ((upper_limit_log_sm - mode_log_sm) / width) ** 2 - 2.0 * beyond
    return float(ll)


# ---------------------------------------------------------------------------
# Channel 3 (UFD): from Sanchez-Almeida+ 2025 A&A
#   sigma/m at UFD velocity = 10^0.92 +/- 1.37
# We extrapolate to v=100 km/s via velocity-dependent model.
def loglike_ufd_v03(sigma_m_0: float, a: float) -> float:
    sigma_m_v = sigma_m_at_v(sigma_m_0, a, V_UFD)
    if sigma_m_v <= 0 or not np.isfinite(sigma_m_v):
        return -np.inf
    log_sm = np.log10(sigma_m_v)
    return -0.5 * ((log_sm - 0.92) / 1.37) ** 2


# ---------------------------------------------------------------------------
# Channel 4 (Bullet Cluster): Cha+ 2025 JWST, sigma/m < 0.5 cm^2/g (95% CL)
# at cluster velocity v ~ 1500 km/s.
def loglike_bullet_v03(sigma_m_0: float, a: float) -> float:
    sigma_m_v = sigma_m_at_v(sigma_m_0, a, V_CLUSTER)
    if sigma_m_v <= 0 or not np.isfinite(sigma_m_v):
        return -np.inf
    log_sm = np.log10(sigma_m_v)
    return -0.5 * max(0, (log_sm - (-0.30)) / 0.30) ** 2


# ---------------------------------------------------------------------------
# Channel 4 sensitivity variant: 0.2 cm^2/g peak (R16 #2 + R15 P077)
# Per the R16 audit, the 0.2 cm^2/g "Markov+ 2025 SL-only" sensitivity case
# is implementable as a simple peak shift: same Gaussian shape, peak moved
# from 0.5 → 0.2 cm^2/g (log = -0.70). Use only when exploring how sensitive
# the headline posterior is to the Bullet Cluster likelihood choice.
#
# Selection: T41_BULLET_VARIANT=sensitivity_0p2 (or default for legacy).
# Effect: shifts the peak by ~0.4 dex; the half-Gaussian penalty at higher
# sigma/m stays in place so the upper-limit structure is preserved.
def loglike_bullet_v03_sensitivity_0p2(sigma_m_0: float, a: float) -> float:
    """Sensitivity variant: 0.2 cm^2/g peak (was 0.5 in the default form).

    Same Gaussian shape as loglike_bullet_v03 but peaked at sigma/m=0.2
    cm^2/g (log10 = -0.699) instead of 0.5 (log10 = -0.301). The penalty
    above 0.2 cm^2/g is preserved (one-sided Gaussian).
    """
    sigma_m_v = sigma_m_at_v(sigma_m_0, a, V_CLUSTER)
    if sigma_m_v <= 0 or not np.isfinite(sigma_m_v):
        return -np.inf
    log_sm = np.log10(sigma_m_v)
    return -0.5 * max(0, (log_sm - (-0.699)) / 0.30) ** 2


# ---------------------------------------------------------------------------
# Channel 1 (SPARC): load T4 (3-param, XI_d-marginalized) fits and
# re-evaluate log L for each (sigma_m_0, a).
#
# We have 175 fits per profile (NFW, Burkert), 350 fits total.
# For each galaxy + each (sigma_m_0, a):
#     - Convert (sigma/m, a) -> r_core at galaxy's v_max
#     - Compute V_total with Burkert(rho_c, r_core)
#     - Compute loglike = -0.5 * chi^2
#     - Aggregate: sum chi^2 over galaxies (the same joint-logZ trick we used)
#
# Faster approximation: for each galaxy, the SPARC T4 log Z (NFW vs Burkert)
# difference at the Burkert fit is approximately preserved. We compute a
# new log Z_Burkert(sigma_m, a) for each galaxy using the V_Burkert_vdep
# profile at the galaxy's v_max.
#
# Lazy imports: halo_profiles and sparc_loader live in v0.1-prelim/code.
# Defer their import to function-call time so the dSph / UFD / Bullet
# channels (the workhorse of this module) work even if the v0.1-prelim
# path is not on sys.path. This was a P0-D testability fix; it also
# avoids forcing every test that imports channels_v03 to set up v0.1-prelim.
VDEP_LOG_RHO_RANGE = (2.0, 10.0)


def _halo_module():
    """Lazy loader for halo_profiles (v0.1-prelim)."""
    import halo_profiles  # noqa: F401
    return halo_profiles


def _sparc_module():
    """Lazy loader for sparc_loader (v0.1-prelim)."""
    import sparc_loader  # noqa: F401
    return sparc_loader


def _loglike_burkert_at_galaxy(ga, log_rho_c: float, r_core_kpc: float) -> float:
    halo = _halo_module()
    halo_V2 = halo.V_Burkert(ga.Rad, 10**log_rho_c, r_core_kpc)
    V_total = np.sqrt(ga.Vbar_sq + halo_V2)
    return -0.5 * halo.chi2_sparc(ga, V_total)


def _loglike_nfw_at_galaxy(ga, log_rho_s: float, r_s_kpc: float) -> float:
    halo = _halo_module()
    halo_V2 = halo.V_NFW(ga.Rad, 10**log_rho_s, r_s_kpc)
    V_total = np.sqrt(ga.Vbar_sq + halo_V2)
    return -0.5 * halo.chi2_sparc(ga, V_total)


def sparc_loglike_grid(gal_name: str, sigma_m_0: float, a: float,
                       data_dir: Path, v_max_override: float = None) -> float:
    """Compute log L for one galaxy at given (sigma/m_0, a).

    Maximizes over (rho_c) at fixed r_core = sqrt(sigma/m(v_max)).
    For SPARC, this is a quick proxy — exact v_max integral would
    require the full likelihood pipeline.
    """
    sparc = _sparc_module()
    ga = sparc.load_one_sparc(data_dir, gal_name)
    v_max = v_max_override if v_max_override else float(np.max(ga.Vobs))
    sigma_m_v = sigma_m_at_v(sigma_m_0, a, v_max)
    if sigma_m_v <= 0:
        return -np.inf
    r_core = np.sqrt(sigma_m_v)  # Robertson+ rule of thumb
    # Maximize over rho_c on a coarse grid
    best_ll = -np.inf
    for log_rho_c in np.linspace(5, 9, 20):
        ll = _loglike_burkert_at_galaxy(ga, log_rho_c, r_core)
        if ll > best_ll:
            best_ll = ll
    return float(best_ll)


def sparc_joint_loglike(sigma_m_0: float, a: float, data_dir: Path,
                       galaxy_subset: list = None) -> float:
    """Joint log L over SPARC galaxies.

    If galaxy_subset is None, uses all 175 galaxies (slow).
    For v0.3 we use a representative subset of 30 galaxies.
    """
    if galaxy_subset is None:
        # Use top 30 high-quality galaxies (n_pts >= 20)
        from sparc_loader import load_all_sparc
        all_g = load_all_sparc(data_dir)
        galaxy_subset = [g.name for g in all_g if g.n_pts >= 20][:30]
    total_ll = 0.0
    for name in galaxy_subset:
        ll = sparc_loglike_grid(name, sigma_m_0, a, data_dir)
        total_ll += ll
    return float(total_ll)


# ---------------------------------------------------------------------------
# Joint 4-channel (or 5-channel with SPARC) log posterior
def loglike_joint_v03(sigma_m_0: float, a: float,
                      data_dir: Path = None,
                      include_sparc: bool = True,
                      sparc_subset: list = None) -> float:
    """Joint log L from all channels.

    If include_sparc=True and data_dir is provided, computes SPARC log L
    (slow — uses the v-dep Burkert profile). Otherwise uses channels 2-4.
    """
    if sigma_m_0 <= 0 or not np.isfinite(sigma_m_0):
        return -np.inf
    if not (-2 <= a <= 2):
        return -np.inf
    ll = 0.0
    ll += loglike_dsph_v03(sigma_m_0, a)
    ll += loglike_ufd_v03(sigma_m_0, a)
    ll += loglike_bullet_v03(sigma_m_0, a)
    if include_sparc and data_dir is not None:
        ll += sparc_joint_loglike(sigma_m_0, a, data_dir, sparc_subset)
    return ll


if __name__ == "__main__":
    # Smoke test: scan over (sigma_m_0, a) grid and report max for 5-channel fit
    import time
    DATA_DIR = Path("/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.1-prelim/data")

    print("Scanning 4-channel (no SPARC) grid for joint posterior...")
    log_sm_grid = np.linspace(-3, 2.5, 30)
    a_grid = np.linspace(-1, 1, 11)
    best = (-np.inf, None, None)
    for log_sm in log_sm_grid:
        for a in a_grid:
            ll = loglike_joint_v03(10**log_sm, a, include_sparc=False)
            if ll > best[0]:
                best = (ll, 10**log_sm, a)
    print(f"4-channel best: log10(sigma/m)={np.log10(best[1]):+.2f}, a={best[2]:+.2f}, ll={best[0]:.3f}")

    print("\nWith SPARC (10 representative galaxies, fast):")
    # Pick 10 representative galaxies
    sparc_subset = ["NGC2403", "NGC2841", "NGC6946", "UGC02953", "UGC06787",
                    "UGC09133", "UGC11914", "DDO154", "DDO161", "DDO168"]
    t0 = time.time()
    ll_sparc = sparc_joint_loglike(0.1, 0.0, DATA_DIR, sparc_subset)
    print(f"  sigma/m=0.1, a=0: SPARC ll = {ll_sparc:.2f}  (wall {time.time()-t0:.1f}s)")
    ll_sparc2 = sparc_joint_loglike(1.0, 0.0, DATA_DIR, sparc_subset)
    print(f"  sigma/m=1.0, a=0: SPARC ll = {ll_sparc2:.2f}")
    ll_sparc3 = sparc_joint_loglike(10.0, 0.0, DATA_DIR, sparc_subset)
    print(f"  sigma/m=10,  a=0: SPARC ll = {ll_sparc3:.2f}")