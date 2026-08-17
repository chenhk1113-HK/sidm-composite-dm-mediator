#!/usr/bin/env python
"""
Velocity-dependent SIDM halo model (Phase 3, v0.2-prelim).

The standard SIDM parametrization is:
    sigma/m (v) = (sigma/m)_0 * (v / v_ref)^(-a)

where v_ref = 100 km/s is the reference velocity (typical galactic scale),
(sigma/m)_0 is the cross-section at v_ref, and a is the velocity power-law index.
a = 0 is velocity-independent; a > 0 means cross-section decreases with velocity
(cluster scales have higher v → lower sigma/m).

The core radius in a Burkert-like profile is roughly:
    r_core (v) ~ sqrt(sigma/m(v)) * constant

For a galaxy with v_max, the EFFECTIVE cross-section is:
    (sigma/m)_eff = (sigma/m)_0 * (v_max / v_ref)^(-a)

We use this to construct a velocity-dependent Burkert profile.

This is a simplified analytic treatment. The full SASHIMI-SIDM analysis
(Horigome+ 2025, arXiv:2503.13650) gives a 95% CL upper limit
sigma/m < 0.2 cm^2/g for velocity-INDEPENDENT SIDM; we delegate the
dSph channel to channels_v03.loglike_dsph_v03 (R12 P0-D).

NOTE (R12 P0-D, 2026-08-17): the legacy docstring claimed Horigome+ 2025
"bimodal posterior, sigma/m ~ 0.1 vs ~10 cm^2/g is robust" -- this was a
misread of the paper. The paper actually gives a UPPER LIMIT at 0.2 cm^2/g,
not a bimodal posterior. This was the most consequential scientific-
plausibility defect in the v0.3-prelim pipeline, fixed by replacing the
bimodal surrogate in channels_v03.loglike_dsph_v03 and propagating the
fix to this module and t28_published_style_dsph.
"""
from __future__ import annotations
import numpy as np
import channels_v03 as ch_v03


def _halo_module():
    """Lazy loader for halo_profiles (v0.1-prelim).

    sidm_velocity_dependent needs V_Burkert and G_KPC_KMS, which live
    in v0.1-prelim/code. Defer the import to function-call time so this
    module can be imported in test runners that don't have v0.1-prelim
    on sys.path. Same pattern as channels_v03 (R12 P0-D testability fix).
    """
    import halo_profiles  # noqa: F401
    return halo_profiles


# Reference velocity (galactic-scale, where σ/m is conventionally quoted)
V_REF = 100.0  # km/s
V_UFD = 10.0   # km/s, typical UFD v_max
V_CLUSTER = 1500.0  # km/s, Bullet Cluster v_max


def sigma_m_effective(sigma_m_0: float, a: float, v_max: float) -> float:
    """Effective cross-section at the galaxy's v_max.
    sigma/m(v) = sigma_m_0 * (v / v_ref)^(-a).
    """
    return sigma_m_0 * (v_max / V_REF) ** (-a)


def r_core_from_sigma_m(sigma_m: float) -> float:
    """Robertson+ 2021 rule of thumb: r_core [kpc] = sqrt(sigma/m)."""
    return np.sqrt(sigma_m)


def V_Burkert_vdep(r: np.ndarray, rho_c: float, sigma_m_0: float,
                   a: float, v_max: float) -> np.ndarray:
    """Burkert-like profile with velocity-dependent cross-section.

    Args:
        r: radii [kpc]
        rho_c: core density [M_sun/kpc^3]
        sigma_m_0: cross-section at v_ref [cm^2/g]
        a: velocity power-law index
        v_max: galaxy's maximum circular velocity [km/s]
    Returns:
        V^2(r) [km/s]^2
    """
    sigma_eff = sigma_m_effective(sigma_m_0, a, v_max)
    r_core = r_core_from_sigma_m(sigma_eff)
    halo = _halo_module()
    return halo.V_Burkert(r, rho_c, r_core)


# ---------------------------------------------------------------------------
# v_max estimator from SPARC (Vobs peak)
def estimate_v_max(ga) -> float:
    """Estimate v_max from peak of observed rotation curve."""
    return float(np.max(ga.Vobs))


# ---------------------------------------------------------------------------
# dSph kinematics likelihood (from Correa+ 2021 + Horigome+ 2025)

# Published upper-limit from Horigome+ 2025 (arXiv:2503.13650):
# "decisively prefers CDM to SIDM when sigma/m exceeds ~0.2 cm^2/g,
#  if a velocity-independent cross section is assumed."
# This is a 95% CL UPPER LIMIT, NOT a bimodal posterior. The legacy
# "bimodal at sigma/m ~ 0.1 and ~ 10 cm^2/g" surrogate was a misread of
# the paper (R12 P0-D, 2026-08-17).
def loglike_dsph_published(sigma_m_0: float, a: float) -> float:
    """Published upper-limit constraint from Horigome+ 2025.

    Delegates to channels_v03.loglike_dsph_v03 which encodes the
    upper-limit form (peak at sigma/m ~ 0.05 cm^2/g, half-Gaussian
    up to the 0.2 cm^2/g 95% CL bound, with velocity-dependence).
    """
    return ch_v03.loglike_dsph_v03(sigma_m_0, a)


# ---------------------------------------------------------------------------
# UFD likelihood (from Sánchez-Almeida+ 2025 A&A)
# Result: sigma/m = 10^0.92 ± 1.37 cm^2/g from UFD cores
# Encoded as a Gaussian on log(sigma/m)
def loglike_ufd_published(sigma_m_0: float, a: float) -> float:
    """Approximate likelihood from Sánchez-Almeida+ 2025 A&A.

    sigma/m at v_ref ~ 10 km/s (UFD velocity scale).
    We extrapolate to v_ref = 100 km/s using the velocity-dependent model:
        sigma_m_0 = sigma_m_UFD * (100 / 10)^a = sigma_m_UFD * 10^a
    And approximate UFD posterior as Gaussian on log(sigma_m_UFD):
        log sigma_m_UFD = 0.92 +/- 1.37

    For a given (sigma_m_0, a), the UFD-inferred cross-section is:
        sigma_m_UFD = sigma_m_0 * (v_UFD / v_ref)^a = sigma_m_0 * 10^(-a)
    """
    V_UFD = 10.0  # km/s, typical UFD v_max
    sigma_m_UFD = sigma_m_0 * (V_UFD / V_REF) ** a
    if sigma_m_UFD <= 0 or not np.isfinite(sigma_m_UFD):
        return -np.inf
    log_sm = np.log10(sigma_m_UFD)
    return -0.5 * ((log_sm - 0.92) / 1.37) ** 2


# ---------------------------------------------------------------------------
# Bullet Cluster likelihood (from Cha+ 2025 ApJ 987 L15)
# Result: sigma/m < 0.5 cm^2/g (95% CL) at cluster scale
# Cluster v_max ~ 1500 km/s
def loglike_bullet_cluster_published(sigma_m_0: float, a: float) -> float:
    """Approximate one-sided upper limit from Cha+ 2025 JWST Bullet Cluster.

    sigma/m at v_cluster ~ 1500 km/s must be < 0.5 cm^2/g.
    Encoded as a Gaussian centered at the limit with width 0.3 dex (95% CL ~ 0.6 dex).
    """
    V_CLUSTER = 1500.0  # km/s, Bullet Cluster v_max
    sigma_m_cluster = sigma_m_0 * (V_CLUSTER / V_REF) ** a
    if sigma_m_cluster <= 0 or not np.isfinite(sigma_m_cluster):
        return -np.inf
    log_sm = np.log10(sigma_m_cluster)
    # One-sided: penalty if log(sigma/m) > log(0.5) = -0.30
    return -0.5 * max(0, (log_sm - (-0.30)) / 0.30) ** 2


# ---------------------------------------------------------------------------
# Joint 4-channel log-posterior
def loglike_joint_4channel(sigma_m_0: float, a: float,
                           sparc_total_log_Z: float = 0.0) -> float:
    """Combined likelihood from channels 2-4 plus an optional SPARC prior.

    Args:
        sigma_m_0: cross-section at v_ref=100 km/s
        a: velocity power-law index
        sparc_total_log_Z: optional summed log Z from SPARC fits
            (this is a delta function — SPARC alone doesn't constrain sigma/m,
             so this is included for completeness only if you want to add it)
    """
    if sigma_m_0 <= 0 or not np.isfinite(sigma_m_0):
        return -np.inf
    if not (-2 <= a <= 2):
        return -np.inf
    ll = 0.0
    ll += loglike_dsph_published(sigma_m_0, a)
    ll += loglike_ufd_published(sigma_m_0, a)
    ll += loglike_bullet_cluster_published(sigma_m_0, a)
    return ll


if __name__ == "__main__":
    # Smoke test: scan over (sigma_m_0, a) grid and report max
    import sys
    log_sm_grid = np.linspace(-3, 2.5, 50)
    a_grid = np.linspace(-0.5, 1.5, 30)
    print("Scanning (log_sigma_m_0, a) grid...")
    best = (-np.inf, None, None)
    for log_sm in log_sm_grid:
        for a in a_grid:
            ll = loglike_joint_4channel(10**log_sm, a)
            if ll > best[0]:
                best = (ll, 10**log_sm, a)
    print(f"Best (log_sigma_m_0, a): log10(sigma/m)={np.log10(best[1]):.2f}, a={best[2]:.2f}, ll={best[0]:.3f}")
    # Check 2D marginalized posterior at best a
    print("\nlog L vs log_sigma_m_0 at best a:")
    for log_sm in np.linspace(-3, 2.5, 12):
        ll = loglike_joint_4channel(10**log_sm, best[2])
        bar = "#" * int(20 + ll)
        print(f"  log sigma/m = {log_sm:+5.2f}: ll = {ll:+7.3f} {bar}")