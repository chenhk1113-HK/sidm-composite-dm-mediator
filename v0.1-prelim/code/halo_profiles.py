#!/usr/bin/env python
"""
Halo profile models for SPARC SIDM-pipeline v0.1.

Two profiles are implemented:

1. NFW (Navarro, Frenk, White 1997) — standard CDM cuspy halo
   rho(r) = rho_s / ((r/r_s) * (1 + r/r_s)^2)
   V^2(r) = 4 pi G * rho_s * r_s^3 / r * [ln(1 + r/r_s) - r/r_s/(1 + r/r_s)]

   Free params: log_rho_s (log central density), log_r_s (log scale radius)

2. Burkert (Burkert 1995) — empirical cored profile, often preferred in
   SIDM models (matches isothermal core in gravothermal equilibrium)
   rho(r) = rho_c * r_c^3 / ((r + r_c) * (r^2 + r_c^2))
   V^2(r) = 2 pi G * rho_c * r_c^2 * [ln(1 + (r/r_c)^2) + 2/(1 + r_c/r) - 2]

   Free params: log_rho_c (log core density), log_r_c (log core radius)

Both profiles are normalized to V_CIRCULAR at each radius.
"""
from __future__ import annotations
import numpy as np

G_KPC_KMS = 4.302e-6  # G in (kpc km^2 / (M_sun s^2))


def V_NFW(r: np.ndarray, rho_s: float, r_s: float) -> np.ndarray:
    """NFW circular velocity squared. r in kpc, returns (km/s)^2."""
    r = np.atleast_1d(r).astype(float)
    x = r / r_s
    # NFW circular velocity squared (Binney & Tremaine Eq. 2.62 + standard form)
    V2 = (4.0 * np.pi * G_KPC_KMS * rho_s * r_s**3 / np.maximum(r, 1e-10)
          * (np.log(1.0 + x) - x / (1.0 + x)))
    V2[r <= 0] = 0.0
    return V2


def V_Burkert(r: np.ndarray, rho_c: float, r_c: float) -> np.ndarray:
    """Burkert circular velocity squared. r in kpc, returns (km/s)^2.

    Closed form (derived via sympy integration):
        M(r) = pi * r_c^3 * rho_c *
               [ln((r + r_c)^2 * (r^2 + r_c^2) / r_c^4) - 2 * atan(r / r_c)]
        V^2(r) = G * M(r) / r

    The earlier closed-form from Salucci & Burkert (2000) was 2.7x too large
    because of a sign error in the arctan term; this version is exact.
    """
    r = np.atleast_1d(r).astype(float)
    # Guard against r=0 (atan(0)=0, log(1)=0, so V^2(0) -> 0 by construction)
    safe_r = np.maximum(r, 1e-10)
    arg = (safe_r + r_c)**2 * (safe_r**2 + r_c**2) / r_c**4
    M = np.pi * r_c**3 * rho_c * (np.log(arg) - 2.0 * np.arctan(safe_r / r_c))
    V2 = G_KPC_KMS * M / safe_r
    V2[r <= 0] = 0.0
    return V2


# ---------------------------------------------------------------------------
# Parameter priors (log-uniform, astronomical units)

NFW_LOG_RHO_S_RANGE = (2.0, 10.0)   # log10(rho_s) [M_sun / kpc^3]
NFW_LOG_R_S_RANGE   = (-1.0, 2.5)   # log10(r_s) [kpc]
BURKERT_LOG_RHO_C_RANGE = (2.0, 10.0)  # log10(rho_c) [M_sun / kpc^3]
BURKERT_LOG_R_C_RANGE   = (-1.0, 2.5)  # log10(r_c) [kpc]


def log_prior_NFW(theta: np.ndarray) -> float:
    """Uniform prior on (log_rho_s, log_r_s). Returns 0 if in bounds, -inf else."""
    log_rho_s, log_r_s = theta
    if not (NFW_LOG_RHO_S_RANGE[0] <= log_rho_s <= NFW_LOG_RHO_S_RANGE[1]):
        return -np.inf
    if not (NFW_LOG_R_S_RANGE[0] <= log_r_s <= NFW_LOG_R_S_RANGE[1]):
        return -np.inf
    return 0.0


def log_prior_Burkert(theta: np.ndarray) -> float:
    """Uniform prior on (log_rho_c, log_r_c)."""
    log_rho_c, log_r_c = theta
    if not (BURKERT_LOG_RHO_C_RANGE[0] <= log_rho_c <= BURKERT_LOG_RHO_C_RANGE[1]):
        return -np.inf
    if not (BURKERT_LOG_R_C_RANGE[0] <= log_r_c <= BURKERT_LOG_R_C_RANGE[1]):
        return -np.inf
    return 0.0


def V2_total(r: np.ndarray, Vbar_sq: np.ndarray, halo_V2: np.ndarray) -> np.ndarray:
    """Total circular velocity squared = Vbar^2 + V_halo^2."""
    return Vbar_sq + halo_V2


# ---------------------------------------------------------------------------
# Likelihood (Gaussian residuals on Vobs)

def chi2_sparc(ga, V_total: np.ndarray) -> float:
    """Chi^2 = sum ((Vobs - V_total) / errV)^2."""
    return float(np.sum(((ga.Vobs - V_total) / np.maximum(ga.errV, 1e-3))**2))


def loglike_profile(ga, theta: np.ndarray, halo_fn, log_prior_fn) -> float:
    """Log-likelihood for a halo profile on one galaxy."""
    lp = log_prior_fn(theta)
    if not np.isfinite(lp):
        return -np.inf
    rho, r_scale = 10**theta[0], 10**theta[1]
    halo_V2 = halo_fn(ga.Rad, rho, r_scale)
    V_total = np.sqrt(V2_total(ga.Rad, ga.Vbar_sq, halo_V2))
    return -0.5 * chi2_sparc(ga, V_total)


if __name__ == "__main__":
    # Smoke test
    import sys
    sys.path.insert(0, str(__file__).rsplit("/", 1)[0])
    from sparc_loader import load_one_sparc
    g = load_one_sparc("/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.1-prelim/data", "CamB")
    # Test NFW at a reasonable point: log_rho_s=7, log_r_s=0.5
    theta_nfw = np.array([7.0, 0.5])
    ll = loglike_profile(g, theta_nfw, V_NFW, log_prior_NFW)
    V2 = V_NFW(g.Rad, 10**7.0, 10**0.5)
    V_total = np.sqrt(g.Vbar_sq + V2)
    print(f"NFW at theta={theta_nfw}: loglike={ll:.3f}")
    print(f"  chi^2 = {chi2_sparc(g, V_total):.3f}")
    print(f"  V_total at 3 radii: {V_total[:3]}")
    print(f"  Vobs at 3 radii:    {g.Vobs[:3]}")
    # Test Burkert
    theta_bur = np.array([7.0, 0.5])
    ll2 = loglike_profile(g, theta_bur, V_Burkert, log_prior_Burkert)
    V2_b = V_Burkert(g.Rad, 10**7.0, 10**0.5)
    V_total_b = np.sqrt(g.Vbar_sq + V2_b)
    print(f"Burkert at theta={theta_bur}: loglike={ll2:.3f}")
    print(f"  chi^2 = {chi2_sparc(g, V_total_b):.3f}")
    print(f"  V_total at 3 radii: {V_total_b[:3]}")