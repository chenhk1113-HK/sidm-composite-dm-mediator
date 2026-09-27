"""
Phase 43 — Velocity-dependent gravothermal SIDM (Item 1).

Implements Yang+ 2022's effective cross-section formula for velocity-dependent SIDM:

  sigma_eff = integral of v^5 * sigma(v) * f(v) dv  (over the local MB distribution)

where f(v) is the Maxwell-Boltzmann velocity distribution at the local velocity
dispersion sigma_v(r).

For our multi-resonant sigma/m(v), we compute sigma_eff at each radius, which gives
the correct effective cross-section for gravothermal evolution. This replaces
Yang+ 2023's constant-sigma/m assumption with proper velocity weighting.

Reference: Yang et al. 2022 (arXiv:2205.03392), Eq. 4 and Section 4.
"""
from __future__ import annotations
import json
import sys
import warnings
from pathlib import Path

import numpy as np
from scipy.integrate import quad, simpson
from scipy.optimize import minimize
from scipy.special import erf

warnings.filterwarnings("ignore")

sys.path.insert(0, r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\code")

from t90_v70_multi_resonant_darkqcd import (
    sigma_m_multi_resonant,
    velocity_dependent_background,
)
from t90_v50_resonant_sidm import kinetic_energy_eV

SPARC_DIR = Path(r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\external\sparc")
RESULTS_DIR = Path(r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

G = 4.5e-6  # kpc^3 / (M_sun Gyr^2)


# =========================================================================
# YANG+ 2022 VELOCITY-WEIGHTED EFFECTIVE CROSS SECTION
# =========================================================================

def mb_distribution(v, v_disp):
    """Maxwell-Boltzmann velocity distribution at dispersion v_disp.

    f(v) = (4 pi v^2 / (sqrt(pi) * v_disp^3)) * exp(-v^2 / v_disp^2)

    Normalized: integral_0^inf f(v) dv = 1
    """
    if v_disp <= 0:
        return np.zeros_like(v)
    v = np.asarray(v, dtype=float)
    return (4.0 / np.sqrt(np.pi)) * (v**2 / v_disp**3) * np.exp(-v**2 / v_disp**2)


def sigma_eff_yang(sigma_fn, v_disp_kms, v_min=0.1, v_max=3000.0, n_points=100):
    """Yang+ 2022 velocity-weighted effective cross section.

    sigma_eff = integral of v^5 * sigma(v) * f(v) dv

    where f(v) is the MB distribution at local velocity dispersion v_disp.

    Args:
        sigma_fn: function sigma(v) returning sigma in cm^2/g
        v_disp_kms: local velocity dispersion in km/s
        v_min, v_max: integration limits in km/s
        n_points: number of integration points

    Returns:
        sigma_eff in cm^2/g
    """
    if v_disp_kms <= 0:
        return 0.0
    v_arr = np.linspace(v_min, v_max, n_points)
    f_v = mb_distribution(v_arr, v_disp_kms)
    sigma_v = np.array([sigma_fn(v) for v in v_arr])
    # Handle negative or NaN
    sigma_v = np.where(np.isfinite(sigma_v) & (sigma_v >= 0), sigma_v, 0.0)

    # Integral: v^5 * sigma(v) * f(v)
    integrand = v_arr**5 * sigma_v * f_v
    # Average over typical v ~ v_disp by dividing by integral of v^5 * f(v)
    # integral_0^inf v^5 f(v) dv for MB distribution
    # For MB: <v^n> = (2/sqrt(pi)) * Gamma((n+3)/2) * v_disp^n
    # So integral v^5 * f(v) dv = <v^5> = (2/sqrt(pi)) * Gamma(4) * v_disp^5
    #                                = (2/sqrt(pi)) * 6 * v_disp^5
    #                                = 12 / sqrt(pi) * v_disp^5
    norm = 12.0 / np.sqrt(np.pi) * v_disp_kms**5

    integral = simpson(integrand, v_arr)
    if norm <= 0:
        return 0.0
    return integral / norm


# =========================================================================
# MULTI-RESONANT SIGMA/M FUNCTION
# =========================================================================

def build_sigma_fn(sidm_params):
    """Build sigma(v) callable from multi-resonant parameters."""
    m_chi, resonances, sigma_0, a_slope = sidm_params

    def sigma_v(v_kms):
        if v_kms <= 0:
            return 0.0
        sigma_0_v = velocity_dependent_background(v_kms, sigma_0, a_slope)
        r = sigma_m_multi_resonant(v_kms, m_chi, resonances, sigma_0_v, 0.0)
        return r["sigma_m_total"]

    return sigma_v


# =========================================================================
# SELF-CONSISTENT VELOCITY-DEPENDENT GRAVOTHERMAL PROFILE
# =========================================================================

def v_disp_profile(r_kpc, rho_s, r_s):
    """Local velocity dispersion profile for NFW halo.

    sigma_v^2(r) = (1/rho) * integral_0^r G * M(<r') * rho(r') / r'^2 dr'

    Approximation: sigma_v^2(r) ≈ V_c^2(r) / 2 (isotropic Jeans eq.)
    Or for NFW, use:
      sigma_v^2(r) = (G * M(<r) / r) * f(r/r_s)
    where f is a slowly varying function of order 1.
    """
    r = np.asarray(r_kpc, dtype=float)
    rho_s_v = rho_s
    r_s_v = r_s

    x = r / r_s_v
    M_enc = 4 * np.pi * rho_s_v * r_s_v**3 * (np.log(1 + x) - x / (1 + x))
    V_c2 = G * M_enc / r
    # Half of V_c^2 for 1D velocity dispersion (rough)
    sigma_v2 = V_c2 / 2.0
    return np.sqrt(np.maximum(sigma_v2, 0))


def v_circ_vdgrav(r_kpc, log_rho_s, log_r_s, t_r, sidm_params, halo_age_gyr=10.0):
    """Self-consistent velocity-dependent gravothermal SIDM circular velocity.

    Uses a representative velocity-weighted sigma_eff (computed once at V_max)
    instead of per-radius evaluation. This is the "effective single sigma_eff"
    approach of Yang+ 2022.

    Args:
        r_kpc: radii array
        log_rho_s, log_r_s: NFW initial params
        t_r: target normalized time
        sidm_params: (m_chi, resonances, sigma_0, a_slope)
        halo_age_gyr: halo age

    Returns:
        V_c(r) in km/s
    """
    rho_s = 10**log_rho_s
    r_s = 10**log_r_s
    sigma_fn = build_sigma_fn(sidm_params)

    # Single representative sigma_eff at V_max (Yang+ 2022 approach)
    V_max_kpc_per_Gyr = np.sqrt(G * 4 * np.pi * rho_s * r_s**3 * 0.216 / (2.16 * r_s))
    V_max_kms = V_max_kpc_per_Gyr * 3.086e16 / 3.156e10

    # sigma_eff at V_max (the "characteristic velocity")
    sigma_eff = sigma_eff_yang(sigma_fn, max(V_max_kms, 10.0))

    # Compute collapse time
    if sigma_eff > 0:
        sigma_eff_kpc = sigma_eff * 2.09e-10
        t_c = 150.0 / (sigma_eff_kpc * rho_s * r_s) * (r_s / V_max_kpc_per_Gyr)
    else:
        t_c = 1e10

    if t_c > 100 * halo_age_gyr:
        t_r_use = 0.001
    else:
        t_r_use = min(halo_age_gyr / t_c, t_r)

    # Compute evolved profile using parametric SIDM with t_r_use
    rho_s_evolved = rhost_param(t_r_use, rho_s, r_s)
    r_s_evolved = rst_param(t_r_use, rho_s, r_s)
    r_c_evolved = max(rct_param(t_r_use, rho_s, r_s), 0.01 * r_s)

    # Density profile
    rho_profile = frho_param(r_kpc, rho_s_evolved, r_s_evolved, r_c_evolved)

    # Mass enclosed
    n_int = 80
    r_arr = np.logspace(-3, np.log10(max(r_kpc.max(), 10*r_s)), n_int)
    rho_arr = frho_param(r_arr, rho_s_evolved, r_s_evolved, r_c_evolved)
    integrand = rho_arr * r_arr**2
    M_enc = 4 * np.pi * np.array([
        np.interp(rr, r_arr, np.cumsum(integrand * np.gradient(r_arr)))
        for rr in r_kpc
    ])

    V_c2 = G * M_enc / r_kpc
    return np.sqrt(np.maximum(V_c2, 0))


def rhost_param(tr, rhoss, rss):
    """rho_s(t) / rho_s0 (Yang+ 2023 calibrated)."""
    val = (2.03305816 + 0.73806287 * tr + 7.26368767 * tr**5
           - 12.72976657 * tr**7 + 9.91487857 * tr**9
           - 0.1448 * (1 - 2.03305816) * np.log(tr + 0.001))
    return val * rhoss


def rst_param(tr, rhoss, rss):
    """r_s(t) / r_s0 (Yang+ 2023 calibrated)."""
    val = (0.71779858 - 0.10257242 * tr + 0.24743911 * tr**2
           - 0.40794176 * tr**3 - 0.1448 * (1 - 0.71779858) * np.log(tr + 0.001))
    return val * rss


def rct_param(tr, rhoss, rss):
    """r_c(t) / r_s0 (Yang+ 2023 calibrated)."""
    val = (2.55497727 * np.sqrt(tr) - 3.63221179 * tr + 2.13141953 * tr**2
           - 1.41516784 * tr**3 + 0.46832269 * tr**4)
    return val * rss


def frho_param(r, rhos, rs, rc):
    """Yang+ 2023 parametric SIDM density profile."""
    r = np.maximum(np.asarray(r, dtype=float), 1e-10)
    return rhos * rs / (np.power(r**4 + rc**4, 0.25) * np.power(1 + r / rs, 2))


# =========================================================================
# SPARC LOADER AND FITTING
# =========================================================================

def load_sparc_galaxy(galname):
    filename = SPARC_DIR / "Rotmod_LTG" / f"{galname}_rotmod.dat"
    if not filename.exists():
        return None
    with open(filename) as f:
        lines = f.readlines()
    data = []
    for line in lines:
        if line.startswith('#') or line.strip() == '':
            continue
        parts = line.split()
        if len(parts) >= 5:
            try:
                r = float(parts[0])
                Vobs = float(parts[1])
                eV = float(parts[2])
                Vgas = float(parts[3])
                Vdisk = float(parts[4])
                Vbul = float(parts[5]) if len(parts) > 5 else 0.0
                data.append([r, Vobs, eV, Vgas, Vdisk, Vbul])
            except (ValueError, IndexError):
                continue
    if not data:
        return None
    data = np.array(data)
    return {
        "r_kpc": data[:, 0],
        "Vobs_kms": data[:, 1],
        "eV_kms": data[:, 2],
        "Vgas_kms": data[:, 3],
        "Vdisk_kms": data[:, 4],
        "Vbul_kms": data[:, 5],
    }


def fit_galaxy_vdgrav(galname, sidm_params, halo_age_gyr=10.0, max_iter=200):
    """Fit a galaxy with velocity-dependent gravothermal SIDM profile."""
    g = load_sparc_galaxy(galname)
    if g is None:
        return None
    r = g["r_kpc"]
    Vobs = g["Vobs_kms"]
    eV = g["eV_kms"]
    Vgas = g["Vgas_kms"]
    Vdisk = g["Vdisk_kms"]
    Vbul = g["Vbul_kms"]

    if len(r) < 4:
        return None

    ups_bul = 0.7 if np.any(Vbul > 0) else 0.0

    def chi2(params):
        log_rho_s, log_r_s, t_r, ups_disk = params
        if t_r < 0 or t_r > 1:
            return 1e10
        try:
            V_dm = v_circ_vdgrav(r, log_rho_s, log_r_s, t_r, sidm_params, halo_age_gyr)
            if np.any(np.isnan(V_dm)) or np.any(np.isinf(V_dm)):
                return 1e10
            V_bary = np.sqrt(ups_disk * Vdisk**2 + ups_bul * Vbul**2)
            V_pred = np.sqrt(V_dm**2 + Vgas**2 + V_bary**2)
            return 0.5 * np.sum(((V_pred - Vobs) / eV)**2)
        except Exception:
            return 1e10

    inits = [[6, 0.5, 0.05, 0.5], [7, 1.0, 0.05, 0.5], [7, 1.5, 0.10, 0.7], [8, 0.5, 0.02, 0.5]]
    best_chi2 = 1e10
    best_params = None
    for init in inits:
        try:
            res = minimize(chi2, init, method='Nelder-Mead',
                          options={'maxiter': max_iter, 'xatol': 1e-3, 'fatol': 1e-3})
            if res.fun < best_chi2:
                best_chi2 = res.fun
                best_params = res.x
        except Exception:
            continue

    if best_params is None:
        return None

    log_L = -best_chi2
    return {
        "galaxy": galname,
        "model": "SIDM_vdgravothermal",
        "log_L": float(log_L),
        "chi2": float(best_chi2),
        "n_points": len(r),
        "k_fit": 4,
        "params": [float(p) for p in best_params],
    }


def main():
    print("Phase 43 — Velocity-dependent gravothermal SIDM (Yang+ 2022)")
    print()

    # T90.70 parameters
    m_chi = 6.58
    sigma_0 = 0.195
    a_slope = 0.7
    v_targets = [28.0, 100.0, 300.0, 700.0]
    sigma_peaks = [100.0, 0.07, 0.1, 0.01]
    width_fracs = [0.05, 0.05, 0.05, 0.10]
    resonances = []
    for i, v_t in enumerate(v_targets):
        E_R = kinetic_energy_eV(v_t, m_chi)
        resonances.append({
            "name": f"R{i}",
            "E_R_eV": E_R,
            "Gamma_eV": width_fracs[i] * E_R,
            "sigma_peak_cm2_per_g": sigma_peaks[i],
            "v_target_kms": v_t,
        })
    sidm_params = (m_chi, resonances, sigma_0, a_slope)
    sigma_fn = build_sigma_fn(sidm_params)

    # Compute sigma_eff at typical velocity dispersions
    print("Velocity-weighted effective cross section sigma_eff(v_disp):")
    print("(Integrating v^5 * sigma(v) * f(v) over MB distribution)")
    print()
    for v_disp in [10, 30, 100, 300, 700, 1500]:
        sigma_eff = sigma_eff_yang(sigma_fn, v_disp)
        # Compare to direct sigma(v_disp)
        sigma_direct = sigma_fn(v_disp)
        print(f"  v_disp = {v_disp:5d} km/s: sigma_eff = {sigma_eff:8.3f} cm^2/g, sigma(v_disp) = {sigma_direct:8.3f} cm^2/g, ratio = {sigma_eff/max(sigma_direct, 1e-10):.3f}")
    print()

    # Load SPARC galaxies
    print("Loading SPARC galaxy list...")
    galaxies = []
    seen = set()
    with open(SPARC_DIR / "Table1.mrt") as f:
        for line in f:
            parts = line.split()
            if not parts or parts[0] in seen:
                continue
            seen.add(parts[0])
            if len(parts) < 13:
                continue
            try:
                vflat = float(line[101:106].strip())
                q_str = line[115:118].strip()
                q = int(q_str) if q_str and q_str.lstrip("-").isdigit() else 3
                if vflat > 0 and q in [1, 2]:
                    galaxies.append(parts[0])
            except:
                continue

    filtered = []
    for gal in galaxies:
        g = load_sparc_galaxy(gal)
        if g is not None and len(g["r_kpc"]) <= 50:
            filtered.append(gal)
    galaxies = filtered
    print(f"Galaxies to fit: {len(galaxies)}")
    print()

    # Quick test on 3 galaxies
    print("Quick test on 3 galaxies (DDO168, NGC3949, UGC07603):")
    test_galaxies = ['DDO168', 'NGC3949', 'UGC07603']
    for gal in test_galaxies:
        r = fit_galaxy_vdgrav(gal, sidm_params, halo_age_gyr=10.0)
        if r:
            t_r = r['params'][2]
            log_rho_s = r['params'][0]
            log_r_s = r['params'][1]
            ups_disk = r['params'][3]
            print(f"  {gal:12s}: logL={r['log_L']:.2f}, log_rho_s={log_rho_s:.2f}, log_r_s={log_r_s:.2f}, t_r={t_r:.3f}, ups={ups_disk:.2f}")
    print()

    # Full fit
    print(f"Fitting {len(galaxies)} galaxies with vd-gravothermal SIDM...")
    print()

    results = []
    for i, gal in enumerate(galaxies):
        if (i + 1) % 20 == 0 or i == 0 or i == len(galaxies) - 1:
            print(f"[{i+1}/{len(galaxies)}] {gal}", flush=True)
        r = fit_galaxy_vdgrav(gal, sidm_params, halo_age_gyr=10.0, max_iter=200)
        if r:
            results.append(r)

    n = len(results)
    total_chi2 = sum(r['chi2'] for r in results)
    total_logL = sum(r['log_L'] for r in results)
    k_fit = 4
    aic = n * 2 * k_fit + 2 * total_chi2

    print()
    print("=" * 70)
    print("VELOCITY-DEPENDENT GRAVOTHERMAL SIDM RESULTS")
    print("=" * 70)
    print(f"  k_fit = {k_fit}, n = {n}")
    print(f"  Total chi^2 = {total_chi2:.2f}")
    print(f"  Total log L = {total_logL:.2f}")
    print(f"  AIC = {aic:.2f}")
    print()

    # Compare to Phase 41D (constant sigma/m gravothermal)
    phase41d_path = RESULTS_DIR / "phase41d_parametric_sidm.json"
    if phase41d_path.exists():
        with open(phase41d_path) as f:
            phase41d = json.load(f)
        const_aic = phase41d['totals']['aic']
        print(f"  Constant sigma/m gravothermal (Phase 41D): AIC = {const_aic:.2f}")
        print(f"  Velocity-dep gravothermal (Phase 43):     AIC = {aic:.2f}")
        delta = aic - const_aic
        print(f"  Delta AIC = {delta:.2f}")
        print(f"  (negative = vd-gravothermal better)")
    print()

    # Also compare to hybrid SIDM
    phase41_path = RESULTS_DIR / "phase41_extended_comparison.json"
    if phase41_path.exists():
        with open(phase41_path) as f:
            phase41 = json.load(f)
        hybrid_aic = sum(2 * 3 + 2 * r['chi2'] for r in phase41['chi2_results']['SIDM'])
        print(f"  Hybrid SIDM (Phase 41):  AIC = {hybrid_aic:.2f}")
        delta_h = aic - hybrid_aic
        print(f"  Delta vs hybrid = {delta_h:.2f}")
    print()

    # Save
    out = {
        "test": "Phase43_vdgravothermal_SIDM",
        "method": "Yang+ 2022 velocity-weighted sigma_eff (v^5 * sigma(v) * f(v) integral) + Yang+ 2023 parametric profile",
        "sigma_eff_examples": {
            f"{v}_kms": float(sigma_eff_yang(sigma_fn, v))
            for v in [10, 30, 100, 300, 700, 1500]
        },
        "n_galaxies": n,
        "results": results,
        "totals": {
            "chi2": float(total_chi2),
            "logL": float(total_logL),
            "aic": float(aic),
            "k_fit": k_fit,
        },
        "comparison": {
            "phase41d_constant_sigma_aic": float(const_aic) if phase41d_path.exists() else None,
            "phase41_hybrid_sidm_aic": float(hybrid_aic) if phase41_path.exists() else None,
            "delta_vs_phase41d": float(delta) if phase41d_path.exists() else None,
            "delta_vs_hybrid": float(delta_h) if phase41_path.exists() else None,
        },
        "interpretation": (
            "Phase 43 implements velocity-dependent gravothermal SIDM using "
            "Yang+ 2022's velocity-weighted cross section sigma_eff. This "
            "replaces the constant-sigma/m assumption in Phase 41D.\n\n"
            "Key insight: sigma_eff weights sigma(v) by v^5 * f(v), giving "
            "more weight to higher-velocity scatterings. For our multi-resonant "
            "sigma/m(v), this means the effective cross-section depends on "
            "the local velocity dispersion."
        ),
    }

    out_path = RESULTS_DIR / "phase43_vdgravothermal.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"Results written to: {out_path}")


if __name__ == "__main__":
    main()