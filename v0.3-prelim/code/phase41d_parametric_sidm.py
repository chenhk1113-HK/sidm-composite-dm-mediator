"""
Phase 41D — Self-consistent gravothermal SIDM profile.

Uses Daneng Yang's parametric SIDM model (arXiv:2305.16176) which provides
closed-form density profiles calibrated to gravothermal simulations.

The parametric form:
  rho(r) = rho_s(t) * r_s / ((r^4 + r_c(t)^4)^(1/4) * (1 + r/r_s(t))^2)

where:
  rho_s(t), r_s(t), r_c(t) are calibrated functions of normalized time t_r = t/t_collapse
  t_collapse depends on sigma/m, halo mass, and concentration

For our multi-resonant sigma/m(v), we compute an effective sigma/m at the
halo velocity dispersion, then use Yang's t_collapse formula.

Reference: Daneng Yang's parametricSIDM github repo + arXiv:2305.16176
"""
from __future__ import annotations
import json
import sys
import warnings
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

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
# PARAMETRIC SIDM MODEL (Yang et al. 2023)
# =========================================================================

def rhost(tr, rhoss, rss):
    """rho_s(t) / rho_s0 calibrated function. tr = t / t_collapse.

    Returns factor by which central density has evolved from initial value.
    At tr=0: factor = 2.03 (initial core formation density)
    At tr=1: factor grows rapidly (gravothermal collapse).
    """
    val = (
        2.03305816
        + 0.73806287 * tr
        + 7.26368767 * tr**5
        - 12.72976657 * tr**7
        + 9.91487857 * tr**9
        - 0.1448 * (1 - 2.03305816) * np.log(tr + 0.001)
    )
    return val * rhoss


def rst(tr, rhoss, rss):
    """r_s(t) / r_s0 — scale radius evolution."""
    val = (
        0.71779858
        - 0.10257242 * tr
        + 0.24743911 * tr**2
        - 0.40794176 * tr**3
        - 0.1448 * (1 - 0.71779858) * np.log(tr + 0.001)
    )
    return val * rss


def rct(tr, rhoss, rss):
    """r_c(t) / r_s0 — core radius evolution."""
    val = (
        2.55497727 * np.sqrt(tr)
        - 3.63221179 * tr
        + 2.13141953 * tr**2
        - 1.41516784 * tr**3
        + 0.46832269 * tr**4
    )
    return val * rss


def frho(r, rhos, rs, rc):
    """Parametric SIDM density profile (Yang+ 2023).

    rho(r) = rho_s * r_s / ((r^4 + r_c^4)^(1/4) * (1 + r/r_s)^2)

    Args:
        r: radius (kpc)
        rhos: characteristic density (M_sun/kpc^3)
        rs: scale radius (kpc)
        rc: core radius (kpc)
    """
    r = np.asarray(r, dtype=float)
    # Avoid r=0 singularity
    r = np.maximum(r, 1e-10)
    val = rhos * rs / (np.power(r**4 + rc**4, 0.25) * np.power(1 + r / rs, 2))
    return val


def t_collapse_parametric(sigma_eff, rho_s, r_s):
    """Collapse timescale for SIDM halo (Yang+ 2023 Eq. 5).

    t_c = (150 / (sigma_eff * rho_s * r_s)) * (r_s / V_max)

    Args:
        sigma_eff: sigma/m in cm^2/g
        rho_s: characteristic density (M_sun/kpc^3)
        r_s: scale radius (kpc)

    Returns:
        t_collapse in Gyr
    """
    if sigma_eff <= 0:
        return 1e10

    # Convert sigma/m to kpc^2/M_sun
    sigma_kpc = sigma_eff * 2.09e-10

    # V_max for NFW (approximate)
    # V_max ~ sqrt(G * M(<r_max)/r_max), with r_max ~ 2.16 r_s for NFW
    # M(<2.16 r_s) ~ 4*pi*rho_s*r_s^3 * [ln(1+2.16) - 2.16/(1+2.16)] = 4*pi*rho_s*r_s^3 * 0.216
    V_max_kpc_per_Gyr = np.sqrt(G * 4 * np.pi * rho_s * r_s**3 * 0.216 / (2.16 * r_s))
    V_max_kms = V_max_kpc_per_Gyr * 3.086e16 / 3.156e10  # kpc/Gyr -> km/s

    # Yang's t_collapse formula: t_c = 150 / (sigma_eff*kpc * rho_s * r_s) * (r_s / V_max)
    # Need to be in consistent units. sigma in cm^2/g, rho in M_sun/kpc^3, r in kpc
    t_c = 150 / (sigma_kpc * rho_s * r_s) * (r_s / V_max_kpc_per_Gyr)
    return t_c


def v_circ_parametric_sidm(r_kpc, log_rho_s, log_r_s, t_r, sidm_params, halo_age_gyr=10.0):
    """Self-consistent parametric SIDM circular velocity.

    Args:
        r_kpc: array of radii (kpc)
        log_rho_s: NFW rho_s in M_sun/kpc^3
        log_r_s: NFW r_s in kpc
        t_r: normalized time t/t_collapse [0, 1]
        sidm_params: tuple (m_chi, resonances, sigma_0, a_slope)
        halo_age_gyr: halo age (Gyr)
    """
    rho_s = 10**log_rho_s
    r_s = 10**log_r_s

    # Compute sigma/m at V_max
    m_chi, resonances, sigma_0, a_slope = sidm_params
    V_max_kms = np.sqrt(G * 4 * np.pi * rho_s * r_s**3 * 0.216 / (2.16 * r_s)) * 3.086e16 / 3.156e10
    sigma_0_v = velocity_dependent_background(V_max_kms, sigma_0, a_slope)
    r_dict = sigma_m_multi_resonant(V_max_kms, m_chi, resonances, sigma_0_v, 0.0)
    sigma_eff = r_dict["sigma_m_total"]

    # Collapse timescale
    t_c = t_collapse_parametric(sigma_eff, rho_s, r_s)

    # If sigma_eff is too small, t_c is huge, t_r ~ 0 → use NFW
    if t_c > 100 * halo_age_gyr:
        t_r_actual = 0.001  # effectively NFW
    else:
        t_r_actual = min(t_r, 1.0)

    # Compute evolved profile parameters
    rho_s_evolved = rhost(t_r_actual, rho_s, r_s)
    r_s_evolved = rst(t_r_actual, rho_s, r_s)
    r_c_evolved = max(rct(t_r_actual, rho_s, r_s), 0.01 * r_s)  # avoid r_c → 0

    # Density profile
    rho_profile = frho(r_kpc, rho_s_evolved, r_s_evolved, r_c_evolved)

    # Mass enclosed
    def M_enc(r):
        if r <= 1e-3:
            return 4.0 / 3.0 * np.pi * r**3 * frho(r, rho_s_evolved, r_s_evolved, r_c_evolved)
        r_arr = np.logspace(-3, np.log10(max(r, 10*r_s_evolved)), 60)
        rho_arr = frho(r_arr, rho_s_evolved, r_s_evolved, r_c_evolved)
        integrand = rho_arr * r_arr**2
        return 4 * np.pi * np.interp(r, r_arr, np.cumsum(integrand * np.gradient(r_arr)))

    r_arr = np.atleast_1d(r_kpc)
    M = np.array([M_enc(r) for r in r_arr])
    V_c2 = G * M / r_arr
    return np.sqrt(np.maximum(V_c2, 0))


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


def fit_galaxy_parametric(galname, sidm_params, halo_age_gyr=10.0, max_iter=300):
    """Fit a galaxy with parametric SIDM profile (4 params: log_rho_s, log_r_s, t_r, ups_disk)."""
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
            V_dm = v_circ_parametric_sidm(r, log_rho_s, log_r_s, t_r, sidm_params, halo_age_gyr)
            if np.any(np.isnan(V_dm)) or np.any(np.isinf(V_dm)):
                return 1e10
            V_bary = np.sqrt(ups_disk * Vdisk**2 + ups_bul * Vbul**2)
            V_pred = np.sqrt(V_dm**2 + Vgas**2 + V_bary**2)
            return 0.5 * np.sum(((V_pred - Vobs) / eV)**2)
        except Exception:
            return 1e10

    # 4-param fit: log_rho_s, log_r_s, t_r, ups_disk
    inits = [
        [6, 0.5, 0.05, 0.5],
        [7, 1.0, 0.05, 0.5],
        [7, 1.5, 0.10, 0.7],
        [8, 0.5, 0.02, 0.5],
    ]

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
        "model": "SIDM_parametric",
        "log_L": float(log_L),
        "chi2": float(best_chi2),
        "n_points": len(r),
        "k_fit": 4,  # log_rho_s, log_r_s, t_r, ups_disk
        "params": [float(p) for p in best_params],
    }


def main():
    print("Phase 41D — Self-consistent parametric SIDM profile (Yang+ 2023)")
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

    # Filter
    filtered = []
    for gal in galaxies:
        g = load_sparc_galaxy(gal)
        if g is not None and len(g["r_kpc"]) <= 50:
            filtered.append(gal)
    galaxies = filtered
    print(f"Galaxies to fit: {len(galaxies)}")
    print()

    # Quick test on 3 galaxies to verify profile works
    print("Quick test on 3 galaxies (DDO168, NGC3949, UGC07603):")
    test_galaxies = ['DDO168', 'NGC3949', 'UGC07603']
    for gal in test_galaxies:
        r = fit_galaxy_parametric(gal, sidm_params, halo_age_gyr=10.0)
        if r:
            t_r = r['params'][2]
            log_rho_s = r['params'][0]
            log_r_s = r['params'][1]
            ups_disk = r['params'][3]
            print(f"  {gal:12s}: logL={r['log_L']:.2f}, log_rho_s={log_rho_s:.2f}, log_r_s={log_r_s:.2f}, t_r={t_r:.3f}, ups={ups_disk:.2f}")
    print()

    # Full fit on all galaxies
    print(f"Fitting {len(galaxies)} galaxies with parametric SIDM profile...")
    print("This is slower than Phase 41 (4 params + gravothermal integration)")
    print()

    results = []
    for i, gal in enumerate(galaxies):
        if (i + 1) % 20 == 0 or i == 0 or i == len(galaxies) - 1:
            print(f"[{i+1}/{len(galaxies)}] {gal}", flush=True)
        r = fit_galaxy_parametric(gal, sidm_params, halo_age_gyr=10.0, max_iter=200)
        if r:
            results.append(r)

    n = len(results)
    total_chi2 = sum(r['chi2'] for r in results)
    total_logL = sum(r['log_L'] for r in results)
    k_fit = 4
    aic = n * 2 * k_fit + 2 * total_chi2

    print()
    print("=" * 70)
    print("PARAMETRIC SIDM RESULTS (120 galaxies)")
    print("=" * 70)
    print(f"  k_fit = {k_fit}, n = {n}")
    print(f"  Total chi^2 = {total_chi2:.2f}")
    print(f"  Total log L = {total_logL:.2f}")
    print(f"  AIC = {aic:.2f}")
    print()

    # Compare to Phase 41 (hybrid SIDM k=3)
    # Load Phase 41 results
    phase41_path = RESULTS_DIR / "phase41_extended_comparison.json"
    if phase41_path.exists():
        with open(phase41_path) as f:
            phase41 = json.load(f)

        sidm_hybrid_rs = phase41['chi2_results']['SIDM']
        if sidm_hybrid_rs:
            sidm_hybrid_chi2 = sum(r['chi2'] for r in sidm_hybrid_rs)
            sidm_hybrid_aic = len(sidm_hybrid_rs) * 2 * 3 + 2 * sidm_hybrid_chi2

            print(f"  Hybrid SIDM (Phase 41):    AIC = {sidm_hybrid_aic:.2f}")
            print(f"  Parametric SIDM (Phase 41D): AIC = {aic:.2f}")
            print(f"  Delta AIC (parametric - hybrid) = {aic - sidm_hybrid_aic:.2f}")
            print(f"  (positive = hybrid better, since hybrid has fewer params)")
            print()

    # Verdict
    delta_aic = aic - sidm_hybrid_aic if sidm_hybrid_rs else 0
    if delta_aic > 10:
        verdict = "PARAMETRIC_WORSE"
    elif delta_aic > -10:
        verdict = "PARAMETRIC_SIMILAR"
    else:
        verdict = "PARAMETRIC_BETTER"

    print(f"Verdict: {verdict}")
    print()

    # Save
    out = {
        "test": "Phase41D_parametric_SIDM",
        "method": "Yang+ 2023 parametric SIDM model, k_fit=4 (log_rho_s, log_r_s, t_r, ups_disk)",
        "n_galaxies": n,
        "model_summary": {
            "profile": "rho(r) = rho_s(t) * r_s / ((r^4 + r_c(t)^4)^(1/4) * (1 + r/r_s(t))^2)",
            "calibrated_from": "DanengYang/parametricSIDM (arXiv:2305.16176)",
            "t_collapse": "t_c = 150 / (sigma_eff * rho_s * r_s) * (r_s / V_max)",
            "multi_resonant_sigma": "T90.70 architecture: 4 resonances at v=[28, 100, 300, 700] km/s",
        },
        "results": results,
        "totals": {
            "chi2": float(total_chi2),
            "logL": float(total_logL),
            "aic": float(aic),
            "k_fit": k_fit,
        },
        "comparison_to_phase41": {
            "sidm_hybrid_aic": float(sidm_hybrid_aic),
            "parametric_aic": float(aic),
            "delta_aic": float(delta_aic),
            "verdict": verdict,
        },
        "interpretation": (
            "Phase 41D implements the self-consistent gravothermal SIDM profile "
            "from Yang+ 2023 (arXiv:2305.16176). This is a parametric model "
            "calibrated to gravothermal simulations.\n\n"
            "The model has k_fit=4 (one more parameter than the hybrid: t_r = "
            "normalized time t/t_collapse). The profile naturally evolves from "
            "NFW-like to cored to collapsed based on t_r.\n\n"
            f"Result: Parametric AIC = {aic:.1f}, Hybrid AIC = {sidm_hybrid_aic:.1f}, "
            f"delta = {delta_aic:.1f}.\n\n"
            "The parametric model adds 1 extra parameter (t_r). The extra "
            "flexibility helps if the gravothermal profile differs significantly "
            "from the hybrid Burkert+NFW blend. If the AIC delta is small, "
            "the hybrid profile is sufficient."
        ),
    }

    out_path = RESULTS_DIR / "phase41d_parametric_sidm.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"Results written to: {out_path}")


if __name__ == "__main__":
    main()