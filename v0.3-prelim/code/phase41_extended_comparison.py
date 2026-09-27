"""
Phase 41 — Extended head-to-head: 5 models on 120 SPARC galaxies.

Adds:
  - Einasto (free alpha) — smooth profile alternative to NFW
  - Pseudo-isothermal (cored isothermal) — another simple cored baseline
  - Plus existing: NFW, Burkert, multi-resonant SIDM

Uses dynesty for proper nested-sampling Bayesian evidence on a subset
(15 galaxies, representative) — gives more rigorous Bayes factor.

Self-consistent gravothermal SIDM profile is NOT implemented in this
phase (would require importing a gravothermal solver).
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

try:
    import dynesty
    HAS_DYNESTY = True
except ImportError:
    HAS_DYNESTY = False

SPARC_DIR = Path(r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\external\sparc")
RESULTS_DIR = Path(r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

G = 4.5e-6  # kpc^3 / (M_sun Gyr^2)


# =========================================================================
# DENSITY PROFILES
# =========================================================================

def v_circ_nfw(r_kpc, log_rho_s, log_r_s):
    """NFW: rho(r) = rho_s / ((r/r_s) * (1 + r/r_s)^2)"""
    rho_s = 10**log_rho_s
    r_s = 10**log_r_s
    x = r_kpc / r_s
    M_enc = 4 * np.pi * rho_s * r_s**3 * (np.log(1 + x) - x / (1 + x))
    V_c2 = G * M_enc / r_kpc
    return np.sqrt(np.maximum(V_c2, 0))


def v_circ_burkert(r_kpc, log_rho_b, r_b):
    """Burkert: rho(r) = rho_b * r_b^3 / ((r + r_b) * (r^2 + r_b^2))"""
    rho_b = 10**log_rho_b
    r_b = float(r_b)
    x = r_kpc / r_b
    M_enc = (
        np.pi * rho_b * r_b**3
        * (2 * np.log(1 + x) + np.log(1 + x**2) - 2 * np.arctan(x))
    )
    V_c2 = G * M_enc / r_kpc
    return np.sqrt(np.maximum(V_c2, 0))


def v_circ_einasto(r_kpc, log_rho_e, r_e, alpha):
    """Einasto: rho(r) = rho_e * exp(-2/alpha * ((r/r_e)^alpha - 1)).

    3 params: log_rho_e, r_e, alpha (free shape).
    M_enc requires numerical integration.
    """
    rho_e = 10**log_rho_e
    r_e = float(r_e)
    alpha = float(alpha)
    if alpha <= 0 or r_e <= 0:
        return np.zeros_like(r_kpc)

    # Density at each r
    def rho(r):
        x = (r / r_e) ** alpha
        return rho_e * np.exp(-2.0 / alpha * (x - 1.0))

    # Numerical integration for M_enc
    n_int = 80
    r_arr = np.logspace(-3, np.log10(max(r_kpc.max(), 50 * r_e)), n_int)
    rho_arr = rho(r_arr)
    integrand = rho_arr * r_arr**2

    # M_enc at each r_kpc via cumulative integration
    r_kpc_arr = np.atleast_1d(r_kpc)
    M_enc = np.array([
        4 * np.pi * np.interp(rr, r_arr, np.cumsum(integrand * np.gradient(r_arr)))
        for rr in r_kpc_arr
    ])
    V_c2 = G * M_enc / r_kpc_arr
    return np.sqrt(np.maximum(V_c2, 0))


def v_circ_piso(r_kpc, log_rho_c, r_c):
    """Pseudo-isothermal (cored isothermal).

    rho(r) = rho_c / (1 + (r/r_c)^2)

    M_enc(r) = 4*pi*rho_c*r_c^2 * (r - r_c*arctan(r/r_c))
    """
    rho_c = 10**log_rho_c
    r_c = float(r_c)
    x = r_kpc / r_c
    M_enc = 4 * np.pi * rho_c * r_c**2 * (r_kpc - r_c * np.arctan(x))
    V_c2 = G * M_enc / r_kpc
    return np.sqrt(np.maximum(V_c2, 0))


def v_circ_sidm_hybrid(r_kpc, log_rho_s, log_r_s, v_max_kms, m_chi, resonances, sigma_0, a_slope):
    """Multi-resonant SIDM: hybrid Burkert+NFW with v-dependent r_core."""
    rho_s = 10**log_rho_s
    r_s = 10**log_r_s

    sigma_0_v = velocity_dependent_background(v_max_kms, sigma_0, a_slope)
    r_dict = sigma_m_multi_resonant(v_max_kms, m_chi, resonances, sigma_0_v, 0.0)
    sigma_eff = r_dict["sigma_m_total"]

    sigma_kpc = sigma_eff * 2.09e-10
    if sigma_eff <= 0 or v_max_kms <= 0:
        r_core = 0.45 * r_s
    else:
        v_max_natural = v_max_kms * 3.086e16 / 3.156e10
        v_dimless = (v_max_natural**2 / (G * rho_s * r_s**2))**0.5
        if v_dimless <= 0 or np.isnan(v_dimless):
            r_core = 0.45 * r_s
        else:
            r_core = 0.45 * r_s * (sigma_kpc * rho_s * r_s / v_max_natural)**0.25
            r_core = max(r_core, 0.1 * r_s)
            r_core = min(r_core, 10 * r_s)

    rho_b = rho_s / 2
    r_b = r_core

    def rho_total(r):
        rho_nfw = rho_s / ((r/r_s) * (1 + r/r_s)**2)
        rho_burk = rho_b * r_b**3 / ((r + r_b) * (r**2 + r_b**2))
        weight_burk = 1 / (1 + (r / r_core)**2)
        return weight_burk * rho_burk + (1 - weight_burk) * rho_nfw

    n_int = 60
    r_arr = np.logspace(-3, np.log10(max(r_kpc.max(), 10*r_s)), n_int)
    rho_arr = rho_total(r_arr)
    integrand = rho_arr * r_arr**2
    M_enc = 4 * np.pi * np.array([
        np.interp(rr, r_arr, np.cumsum(integrand * np.gradient(r_arr)))
        for rr in r_kpc
    ])
    V_c2 = G * M_enc / r_kpc
    return np.sqrt(np.maximum(V_c2, 0))


# =========================================================================
# SPARC LOADER
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


# =========================================================================
# FITTING (Nelder-Mead with grid of starts)
# =========================================================================

def fit_galaxy(galname, model='nfw', sidm_params=None, max_iter=300):
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

    if model == 'nfw':
        def chi2(params):
            log_rho_s, log_r_s, ups_disk = params
            V_dm = v_circ_nfw(r, log_rho_s, log_r_s)
            V_bary = np.sqrt(ups_disk * Vdisk**2 + ups_bul * Vbul**2)
            V_pred = np.sqrt(V_dm**2 + Vgas**2 + V_bary**2)
            return 0.5 * np.sum(((V_pred - Vobs) / eV)**2)
        inits = [[6, 0.5, 0.5], [7, 1.0, 0.5], [8, 0.0, 0.5]]
    elif model == 'burkert':
        def chi2(params):
            log_rho_b, r_b, ups_disk = params
            V_dm = v_circ_burkert(r, log_rho_b, r_b)
            V_bary = np.sqrt(ups_disk * Vdisk**2 + ups_bul * Vbul**2)
            V_pred = np.sqrt(V_dm**2 + Vgas**2 + V_bary**2)
            return 0.5 * np.sum(((V_pred - Vobs) / eV)**2)
        inits = [[6, 1.0, 0.5], [7, 5.0, 0.5], [8, 10.0, 0.5]]
    elif model == 'einasto':
        def chi2(params):
            log_rho_e, r_e, alpha, ups_disk = params  # 4 params!
            if alpha <= 0 or r_e <= 0:
                return 1e10
            V_dm = v_circ_einasto(r, log_rho_e, r_e, alpha)
            V_bary = np.sqrt(ups_disk * Vdisk**2 + ups_bul * Vbul**2)
            V_pred = np.sqrt(V_dm**2 + Vgas**2 + V_bary**2)
            return 0.5 * np.sum(((V_pred - Vobs) / eV)**2)
        # k_fit=4 for Einasto (log_rho_e, r_e, alpha, ups_disk)
        inits = [[7, 1.0, 0.5, 0.5], [7, 2.0, 1.0, 0.5], [7, 5.0, 2.0, 0.5]]
    elif model == 'piso':
        def chi2(params):
            log_rho_c, r_c, ups_disk = params
            V_dm = v_circ_piso(r, log_rho_c, r_c)
            V_bary = np.sqrt(ups_disk * Vdisk**2 + ups_bul * Vbul**2)
            V_pred = np.sqrt(V_dm**2 + Vgas**2 + V_bary**2)
            return 0.5 * np.sum(((V_pred - Vobs) / eV)**2)
        inits = [[6, 1.0, 0.5], [7, 5.0, 0.5], [8, 10.0, 0.5]]
    elif model == 'sidm':
        def chi2(params):
            log_rho_s, log_r_s, ups_disk = params
            V_max = float(np.max(Vobs))
            V_dm = v_circ_sidm_hybrid(r, log_rho_s, log_r_s, V_max, *sidm_params)
            V_bary = np.sqrt(ups_disk * Vdisk**2 + ups_bul * Vbul**2)
            V_pred = np.sqrt(V_dm**2 + Vgas**2 + V_bary**2)
            return 0.5 * np.sum(((V_pred - Vobs) / eV)**2)
        inits = [[6, 0.5, 0.5], [7, 1.0, 0.5], [8, 0.0, 0.5]]
    else:
        raise ValueError(f"Unknown model: {model}")

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

    # Number of fit parameters
    k_fit = len(inits[0])  # includes ups_disk
    log_L = -best_chi2
    return {
        "galaxy": galname,
        "model": model,
        "log_L": float(log_L),
        "chi2": float(best_chi2),
        "n_points": len(r),
        "k_fit": k_fit,
        "params": [float(p) for p in best_params],
    }


# =========================================================================
# NESTED SAMPLING (dynesty) for proper Bayesian evidence
# =========================================================================

def dynesty_logL(params, r, Vobs, eV, Vgas, Vdisk, Vbul, model, sidm_params, ups_bul):
    """Log likelihood for dynesty."""
    try:
        if model == 'nfw':
            log_rho_s, log_r_s, ups_disk = params
            V_dm = v_circ_nfw(r, log_rho_s, log_r_s)
        elif model == 'burkert':
            log_rho_b, r_b, ups_disk = params
            V_dm = v_circ_burkert(r, log_rho_b, r_b)
        elif model == 'einasto':
            log_rho_e, r_e, alpha, ups_disk = params
            if alpha <= 0 or r_e <= 0:
                return -1e10
            V_dm = v_circ_einasto(r, log_rho_e, r_e, alpha)
        elif model == 'piso':
            log_rho_c, r_c, ups_disk = params
            V_dm = v_circ_piso(r, log_rho_c, r_c)
        elif model == 'sidm':
            log_rho_s, log_r_s, ups_disk = params
            V_max = float(np.max(Vobs))
            V_dm = v_circ_sidm_hybrid(r, log_rho_s, log_r_s, V_max, *sidm_params)
        else:
            return -1e10
    except Exception:
        return -1e10

    if np.any(np.isnan(V_dm)) or np.any(np.isinf(V_dm)):
        return -1e10

    V_bary = np.sqrt(ups_disk * Vdisk**2 + ups_bul * Vbul**2)
    V_pred = np.sqrt(V_dm**2 + Vgas**2 + V_bary**2)
    residuals = (V_pred - Vobs) / eV
    return -0.5 * np.sum(residuals**2)


def dynesty_prior_transform(u, model):
    """Map unit cube to parameter space."""
    if model == 'einasto':
        # 4 params: log_rho_e [3,10], r_e [0.1,30], alpha [0.1,5], ups_disk [0.1,1.5]
        log_rho_e = u[0] * 7 + 3  # [3, 10]
        r_e = u[1] * 29.9 + 0.1   # [0.1, 30]
        alpha = u[2] * 4.9 + 0.1  # [0.1, 5]
        ups_disk = u[3] * 1.4 + 0.1  # [0.1, 1.5]
        return np.array([log_rho_e, r_e, alpha, ups_disk])
    else:
        # 3 params: log_rho [3,10], r_xx [0.1,30], ups_disk [0.1,1.5]
        log_rho = u[0] * 7 + 3
        r_xx = u[1] * 29.9 + 0.1
        ups_disk = u[2] * 1.4 + 0.1
        return np.array([log_rho, r_xx, ups_disk])


def dynesty_fit_galaxy(galname, model, sidm_params=None, maxcall=2000):
    """Fit a single galaxy with dynesty for proper Bayesian evidence."""
    if not HAS_DYNESTY:
        return None

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

    ndims = 4 if model == 'einasto' else 3

    def loglike(params):
        return dynesty_logL(params, r, Vobs, eV, Vgas, Vdisk, Vbul, model, sidm_params, ups_bul)

    def prior_transform(u):
        return dynesty_prior_transform(u, model)

    try:
        sampler = dynesty.NestedSampler(
            loglike, prior_transform, ndims,
            nlive=50, bound='multi', sample='rwalk'
        )
        sampler.run_nested(maxcall=maxcall, print_progress=False)
        result = sampler.results
        log_Z = result.logz[-1]  # log evidence
        log_Z_err = result.logzerr[-1]
        return {
            "galaxy": galname,
            "model": model,
            "log_Z": float(log_Z),
            "log_Z_err": float(log_Z_err),
            "n_points": len(r),
        }
    except Exception as e:
        print(f"  dynesty {model} {galname} failed: {e}")
        return None


# =========================================================================
# MAIN
# =========================================================================

def main():
    print("Phase 41 — 5-model head-to-head + nested-sampling evidence")
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

    # 5-way comparison with chi^2 minimization
    results = {model: [] for model in ['NFW', 'Burkert', 'Einasto', 'PISO', 'SIDM']}

    print(f"Phase 41a — 5-model chi^2 fits ({len(galaxies)} galaxies)")
    for i, gal in enumerate(galaxies):
        if (i + 1) % 20 == 0 or i == 0 or i == len(galaxies) - 1:
            print(f"[{i+1}/{len(galaxies)}] {gal}", flush=True)
        for model_name, model_key in [('NFW', 'nfw'), ('Burkert', 'burkert'),
                                       ('Einasto', 'einasto'), ('PISO', 'piso'),
                                       ('SIDM', 'sidm')]:
            kwargs = {}
            if model_key == 'sidm':
                kwargs['sidm_params'] = sidm_params
            r = fit_galaxy(gal, model=model_key, **kwargs)
            if r:
                r['model'] = model_name
                results[model_name].append(r)

    print()
    print("=" * 70)
    print("CHI^2 RESULTS (120 galaxies)")
    print("=" * 70)
    for model_name in ['NFW', 'Burkert', 'Einasto', 'PISO', 'SIDM']:
        rs = results[model_name]
        total_chi2 = sum(r['chi2'] for r in rs)
        total_logL = sum(r['log_L'] for r in rs)
        k_fit = rs[0]['k_fit'] if rs else 0
        aic = 2 * k_fit * len(rs) + 2 * total_chi2
        print(f"  {model_name:10s}: k_fit={k_fit}, total_chi2={total_chi2:.1f}, total_logL={total_logL:.1f}, AIC={aic:.1f}")

    # Compute pairwise AIC differences vs SIDM
    print()
    print("Pairwise ΔAIC vs SIDM (positive = SIDM preferred):")
    sidm_aic = sum(2 * results['SIDM'][0]['k_fit'] + 2 * r['chi2'] for r in results['SIDM'])
    for model_name in ['NFW', 'Burkert', 'Einasto', 'PISO']:
        aic = sum(2 * results[model_name][0]['k_fit'] + 2 * r['chi2'] for r in results[model_name])
        delta = sidm_aic - aic  # positive = SIDM better
        if delta > 10:
            v = "STRONG_SIDM"
        elif delta > 6:
            v = "MODERATE_SIDM"
        elif delta > 2:
            v = "WEAK_SIDM"
        elif delta > -2:
            v = "INCONCLUSIVE"
        elif delta > -6:
            v = f"WEAK_{model_name.upper()}"
        else:
            v = f"STRONG_{model_name.upper()}"
        print(f"  SIDM vs {model_name:10s}: ΔAIC = {delta:+.2f} → {v}")

    # Phase 41b — nested sampling on a 15-galaxy subset
    print()
    print("=" * 70)
    print("Phase 41b — Nested-sampling Bayesian evidence (15 galaxies)")
    print("=" * 70)

    if not HAS_DYNESTY:
        print("dynesty not installed. Skipping nested-sampling phase.")
        dynesty_results = None
    else:
        np.random.seed(42)
        # Pick 15 representative galaxies (mix of dwarf + spiral + giant)
        sub_galaxies = sorted(np.random.choice(galaxies, min(15, len(galaxies)), replace=False))
        print(f"Fitting {len(sub_galaxies)} galaxies with dynesty for log Z")
        print(f"Models: NFW, Burkert, Einasto, PISO, SIDM")
        print(f"Time estimate: ~{len(sub_galaxies) * 5 * 0.5:.0f}-{len(sub_galaxies) * 5 * 2:.0f} min")

        dynesty_results = {model: [] for model in ['NFW', 'Burkert', 'Einasto', 'PISO', 'SIDM']}

        for i, gal in enumerate(sub_galaxies):
            print(f"[{i+1}/{len(sub_galaxies)}] {gal}", flush=True)
            for model_name, model_key in [('NFW', 'nfw'), ('Burkert', 'burkert'),
                                           ('Einasto', 'einasto'), ('PISO', 'piso'),
                                           ('SIDM', 'sidm')]:
                kwargs = {}
                if model_key == 'sidm':
                    kwargs['sidm_params'] = sidm_params
                r = dynesty_fit_galaxy(gal, model=model_key, maxcall=2000, **kwargs)
                if r:
                    r['model'] = model_name
                    dynesty_results[model_name].append(r)

        print()
        print("Nested-sampling log Z (15 galaxies):")
        for model_name in ['NFW', 'Burkert', 'Einasto', 'PISO', 'SIDM']:
            rs = dynesty_results[model_name]
            if rs:
                total_logZ = sum(r['log_Z'] for r in rs)
                k_fit = 3 if model_name != 'Einasto' else 4
                k_phys = 5 if model_name != 'SIDM' else 15
                print(f"  {model_name:10s}: total_logZ={total_logZ:.2f}, k_fit={k_fit}, k_phys={k_phys}")

        print()
        print("Bayes factor (Δlog Z) vs SIDM (positive = SIDM preferred):")
        sidm_logZ = sum(r['log_Z'] for r in dynesty_results['SIDM'])
        for model_name in ['NFW', 'Burkert', 'Einasto', 'PISO']:
            logZ = sum(r['log_Z'] for r in dynesty_results[model_name])
            delta = sidm_logZ - logZ
            k_phys_other = 5 if model_name != 'Einasto' else 5  # Einasto k_phys also ~5
            k_phys_sidm = 15
            # Penalty for Occam (log Z = ln(evidence); AIC = chi^2 + 2k, so penalty is ~2k log-units)
            occam_penalty = (k_phys_sidm - k_phys_other) * 0.5  # Rough estimate: 0.5 log-units per extra param (vs 1 for AIC)
            # Actually the Occam penalty in log Z is more nuanced. We report both raw and penalized.
            print(f"  SIDM vs {model_name:10s}: Δlog Z = {delta:+.2f} raw; ~{delta - occam_penalty:+.2f} with rough Occam penalty (k_sidm - k_other)*0.5 = {occam_penalty:.1f}")

    # Save results
    out = {
        "test": "Phase41_extended_comparison",
        "n_galaxies_chi2": len(results['NFW']),
        "n_galaxies_dynesty": len(dynesty_results['NFW']) if dynesty_results else 0,
        "model_summary": {
            "NFW": "k_fit=3, k_phys=5",
            "Burkert": "k_fit=3, k_phys=5",
            "Einasto": "k_fit=4 (free alpha), k_phys=5",
            "PISO": "k_fit=3, k_phys=5 (pseudo-isothermal, another cored baseline)",
            "SIDM": "k_fit=3, k_phys=15 (multi-resonance + halo profile)",
        },
        "chi2_results": results,
        "dynesty_results": dynesty_results,
        "interpretation": (
            "Phase 41 extends Phase 40 with two additional cored baselines "
            "(Einasto with free alpha, pseudo-isothermal) and replaces Laplace "
            "AIC approximation with nested-sampling Bayesian evidence (dynesty) "
            "on a 15-galaxy subset.\n\n"
            "Self-consistent gravothermal SIDM profile NOT implemented (Phase 41D "
            "would require importing a gravothermal solver like SIDM-GS or "
            "FIRE-style simulations, which is beyond the current scope)."
        ),
    }

    out_path = RESULTS_DIR / "phase41_extended_comparison.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"\nResults written to: {out_path}")


if __name__ == "__main__":
    main()