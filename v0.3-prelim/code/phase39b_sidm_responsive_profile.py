"""
phase39b_sidm_responsive_profile.py — a SCIENTIFICALLY RESPONSIVE SIDM halo
profile for the Phase 39 / Phase 40 SPARC rotation-curve comparison.

WHAT THIS IS
------------
Phase 39 (``phase39_nfw_vs_sidm.py``) and Phase 40 (``phase40_corrected_comparison.py``)
compare NFW against a "velocity-dependent SIDM core radius" that is INERT: the raw
``r_core`` is always far below its own ``0.1*r_s`` floor, so sigma/m, the resonance
peak heights and the slope ``a_slope`` never reach the rotation curve. The stored
Phase 39 verdict ``STRONG_SIDM`` (logL_nfw = -1509.65 vs logL_sidm = -1205.14 over
15 galaxies) is really "a fixed ``0.1*r_s`` cored profile beats NFW", not evidence
about SIDM. Pinned by ``tests/test_sidm_core_radius_invariance.py``.

This module is the decision-support replacement: a SIDM halo profile whose core
radius is DERIVED from a gravothermal collapse calculation, so that sigma/m
genuinely controls the rotation curve. It uses the Yang, Nadler, Yu & Zhong (2024)
parametric model (JCAP 02 (2024) 032, arXiv:2305.16176), most of whose machinery is
already implemented in ``gravothermal_yang2024.py``:

  eq. 2.1  rho_SIDM(r) = rho_s / [ ((r^beta + r_c^beta)^(1/beta) / r_s) (1 + r/r_s)^2 ],
           beta = 4.  At r_c -> 0 this is exactly NFW.
  eq. 2.2  t_c = (150/C) / [(sigma_eff/m) rho_eff r_eff sqrt(4 pi G rho_eff)],
           C = 0.75.  Calibrated to give t_c(BM2) = 28.7 Gyr at sigma_eff/m = 7.1.
  eq. 2.3  tau = t/t_c evolution factors: f_rho(tau), f_rs(tau), f_rc(tau).

THE RESPONSIVE CHAIN (this is what the inert profile was missing)
    NFW initial (rho_s0, r_s0)
      -> V_max,NFW = 1.648 sqrt(G rho_s0 r_s0^2)
      -> sigma_eff/m = sigma/m(0.64 V_max,NFW)      [paper's nu_eff = 0.64 V_max]
      -> t_c (eq. 2.2)                              [t_c proportional to 1/sigma]
      -> t_evol = t_L(z_f(M_vir))                   [astro time, independent of sigma]
      -> tau = min(t_evol / t_c, 1)
      -> r_s = r_s0 f_rs(tau), r_c = r_s0 f_rc(tau), rho_s = rho_s0 f_rho(tau)
      -> rho_SIDM(r; rho_s, r_s, r_c)  ->  V_circ(r)

  So dV_circ/d(sigma/m) != 0 by construction: larger sigma/m -> shorter t_c ->
  larger tau -> larger r_c -> more cored. Contrast the inert profile, where the
  whole chain is short-circuited to r_c = 0.1 r_s at every grid point.

IMPORTANT CORRECTION FOUND WHILE BUILDING THIS (report, do not hide)
-------------------------------------------------------------------
``gravothermal_yang2024.rho_sidm`` does NOT implement eq. 2.1 as written in the
paper. The module computes

    rho_s * [(r^beta + r_c^beta)/(r_s^beta + r_c^beta)]^(1/beta) * (r_s/(r+r_s))^2

whereas arXiv:2305.16176 eq. 2.1 is

    rho_s * r_s / [(r^beta + r_c^beta)^(1/beta) * (1 + r/r_s)^2].

The (r^beta + r_c^beta) factor is INVERTED, so the module's profile is larger than
NFW outside r_s and smaller inside, and it does NOT reduce to NFW at r_c -> 0 (its
ratio to NFW is exactly (r/r_s)^2). Verified numerically in the scratch probe and
pinned by ``tests/test_phase39b_responsive_profile.py``. The module is off-limits
per the task's hard rules, so this file re-implements eq. 2.1 correctly as
``rho_yang2024`` and re-uses everything else (t_c, the f_* evolution factors, z_f,
t_L) unchanged. The paper's own text ("In the limit r_c -> 0, eq. (2.1) smoothly
reduces to an NFW profile") is the second, independent confirmation.

WHAT IT DELIBERATELY DOES NOT DO
--------------------------------
- No baryonic feedback / halo mass-growth history: the ordered-merger and tidal
  subhalo machinery of the paper is out of scope for a rotation-curve comparison.
- The concentration needed to turn (rho_s, r_s) into M_vir -> z_f is FIXED at
  c = 10 (a representative value for 1e9-1e12 Msun halos); z_f and therefore t_evol
  are only weakly mass-dependent (t_evol ~ 8.5-9.5 Gyr over the fitted range). The
  sensitivity to this choice is reported in the output JSON.
- sigma_eff/m is evaluated at a single characteristic velocity (0.64 V_max per the
  paper), not integrated against a Maxwell-Boltzmann kernel. The paper's own
  benchmark uses a single effective cross section, so this is consistent, but it is
  a first-order treatment of a velocity-dependent cross section.

HONESTY POSTURE
---------------
This is a decision-support prototype. Whatever the numbers say is reported —
including if responsive SIDM fits WORSE than NFW or Burkert. Nothing here is tuned
to reach a preferred verdict.

USAGE
    .venv-sidm-bench/Scripts/python.exe v0.3-prelim/code/phase39b_sidm_responsive_profile.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import warnings

warnings.filterwarnings("ignore")

_CODE_DIR = r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\code"
if _CODE_DIR not in sys.path:
    sys.path.insert(0, _CODE_DIR)

from scipy.optimize import minimize

from t90_v70_multi_resonant_darkqcd import (
    sigma_m_multi_resonant,
    velocity_dependent_background,
)
from t90_v50_resonant_sidm import kinetic_energy_eV
import gravothermal_yang2024 as gy

# Re-use Phase 39's SPARC loader and the two inert SIDM profiles for an apples-to-
# apples "inert vs responsive" comparison under one fitter.
import phase39_nfw_vs_sidm as p39
import phase40_corrected_comparison as p40

G_KPC_KMS = 4.302e-6  # kpc (km/s)^2 / M_sun  (config.py:111)
BETA = 4.0            # Yang+ 2024 eq. 2.1 transition sharpness

SPARC_DIR = Path(
    r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\external\sparc"
)

# ---- canonical particle-model parameters (identical to phase39 / phase40) ----
M_CHI_GEV = 6.58
SIGMA_0_CM2_PER_G = 0.195
A_SLOPE = 0.7
V_TARGETS = [28.0, 100.0, 300.0, 700.0]
SIGMA_PEAKS = [100.0, 0.07, 0.1, 0.01]
WIDTH_FRACS = [0.05, 0.05, 0.05, 0.10]

# ---- NFW -> M_vir conversion assumption (see module docstring) ----
CONCENTRATION = 10.0

# NFW V_max = 1.648 sqrt(G rho_s r_s^2)  (standard; re-derived and checked in tests)
NFW_VMAX_COEFF = 1.648
# Paper's characteristic dispersion: nu_eff = 0.64 V_max,NFW
NU_EFF_FRACTION = 0.64


def build_resonances(m_chi_gev: float = M_CHI_GEV) -> list:
    """Same 4-resonance configuration used by phase39 / phase40."""
    out = []
    for i, v_t in enumerate(V_TARGETS):
        e_r = kinetic_energy_eV(v_t, m_chi_gev)
        out.append({
            "name": f"R{i}",
            "E_R_eV": e_r,
            "Gamma_eV": WIDTH_FRACS[i] * e_r,
            "sigma_peak_cm2_per_g": SIGMA_PEAKS[i],
            "v_target_kms": v_t,
        })
    return out


# ===========================================================================
# Yang+ 2024 eq. 2.1 — implemented CORRECTLY (see the correction note above)
# ===========================================================================

def rho_yang2024(r_kpc, rho_s: float, r_s: float, r_c: float, beta: float = BETA):
    """Yang+ 2024 eq. 2.1 SIDM density profile (correct form).

        rho(r) = rho_s * r_s / [ (r^beta + r_c^beta)^(1/beta) * (1 + r/r_s)^2 ]

    r_c -> 0 gives exactly NFW. r << r_c gives a constant core
    rho ~ rho_s r_s / r_c. r >> r_s recovers the NFW 1/r^3 tail.

    Units: rho in Msun/kpc^3, r in kpc.
    """
    rr = np.maximum(np.asarray(r_kpc, dtype=float), 1e-12)
    rc = max(float(r_c), 0.0)
    denom = (rr ** beta + rc ** beta) ** (1.0 / beta) * (1.0 + rr / r_s) ** 2
    return rho_s * r_s / denom


def rho_nfw(r_kpc, rho_s: float, r_s: float):
    """NFW density (for validation): rho_s / [(r/r_s)(1+r/r_s)^2]."""
    rr = np.maximum(np.asarray(r_kpc, dtype=float), 1e-12)
    return rho_s / ((rr / r_s) * (1.0 + rr / r_s) ** 2)


def nfw_v_max(rho_s: float, r_s: float) -> float:
    """NFW V_max in km/s: 1.648 sqrt(G rho_s r_s^2)."""
    return NFW_VMAX_COEFF * math.sqrt(G_KPC_KMS * rho_s * r_s ** 2)


def nfw_m_vir(rho_s: float, r_s: float, c: float = CONCENTRATION) -> float:
    """NFW virial mass for concentration c (Msun)."""
    return 4.0 * math.pi * rho_s * r_s ** 3 * (math.log1p(c) - c / (1.0 + c))


def sigma_eff_at_halo(rho_s0: float, r_s0: float,
                      sigma_0: float = SIGMA_0_CM2_PER_G,
                      a_slope: float = A_SLOPE,
                      m_chi: float = M_CHI_GEV,
                      resonances: list | None = None) -> dict:
    """Canonical sigma/m evaluated at the paper's characteristic velocity 0.64 V_max."""
    if resonances is None:
        resonances = build_resonances(m_chi)
    v_max = nfw_v_max(rho_s0, r_s0)
    v_eff = max(NU_EFF_FRACTION * v_max, 1e-6)
    sigma_bg = velocity_dependent_background(v_eff, sigma_0, a_slope)
    sigma_eff = sigma_m_multi_resonant(v_eff, m_chi, resonances, sigma_bg, 0.0)["sigma_m_total"]
    return {"v_max_kms": v_max, "v_eff_kms": v_eff,
            "sigma_eff_cm2_per_g": float(sigma_eff)}


def responsive_halo(log_rho_s, log_r_s,
                    m_chi: float = M_CHI_GEV,
                    resonances: list | None = None,
                    sigma_0: float = SIGMA_0_CM2_PER_G,
                    a_slope: float = A_SLOPE,
                    concentration: float = CONCENTRATION) -> dict:
    """Evolve an NFW halo to its SIDM counterpart via the Yang+ 2024 chain.

    Argument order matches phase39's SIDM tuple ``(m_chi, resonances, sigma_0,
    a_slope)`` so ``*sidm_params`` unpacks identically for the inert and the
    responsive profiles.
    """
    rho_s0 = 10.0 ** float(log_rho_s)
    r_s0 = 10.0 ** float(log_r_s)

    sig = sigma_eff_at_halo(rho_s0, r_s0, sigma_0, a_slope, m_chi, resonances)
    sigma_eff = sig["sigma_eff_cm2_per_g"]

    # eq. 2.2 collapse time (BM2-calibrated normalisation: 28.7 Gyr for BM2).
    t_c = gy.collapse_time_calibrated_gyr(sigma_eff, rho_s0, r_s0)

    # evolution time since formation
    m_vir = nfw_m_vir(rho_s0, r_s0, concentration)
    t_evol = gy.evolution_time_gyr(m_vir)

    tau = min(t_evol / t_c, 1.0) if (t_c and math.isfinite(t_c) and t_c > 0) else 0.0

    rho_s = rho_s0 * gy.f_rho_s_over_rho_s0(tau)
    r_s = r_s0 * gy.f_rs_over_rs0(tau)
    r_c = r_s0 * gy.f_rc_over_rs0(tau)

    return {
        "rho_s0": rho_s0, "r_s0": r_s0,
        "v_max_kms": sig["v_max_kms"], "v_eff_kms": sig["v_eff_kms"],
        "sigma_eff_cm2_per_g": sigma_eff,
        "t_c_Gyr": t_c, "m_vir_msun": m_vir, "t_evol_Gyr": t_evol,
        "tau": tau,
        "rho_s": rho_s, "r_s": r_s, "r_c": r_c,
        "r_c_over_r_s0": gy.f_rc_over_rs0(tau),
        "phase": gy.classify_phase(tau),
    }


def v_circ_sidm_responsive(r_kpc, log_rho_s, log_r_s,
                           m_chi: float = M_CHI_GEV,
                           resonances: list | None = None,
                           sigma_0: float = SIGMA_0_CM2_PER_G,
                           a_slope: float = A_SLOPE,
                           n_int: int = 200, kappa: float = 0.0):
    """Circular velocity of the responsive SIDM halo, in km/s.

    Enclosed mass from numerical quadrature of eq. 2.1 on a log-radius grid, then
    V_c^2 = G M(<r) / r.  ``kappa`` is only used by tests/probes to force a fixed
    r_c = kappa * r_s (kappa=0 disables the override).

    Argument order matches phase39's SIDM tuple ``(m_chi, resonances, sigma_0,
    a_slope)``.
    """
    r = np.atleast_1d(np.asarray(r_kpc, dtype=float))
    halo = responsive_halo(log_rho_s, log_r_s, m_chi, resonances, sigma_0, a_slope)

    rho_s, r_s, r_c = halo["rho_s"], halo["r_s"], halo["r_c"]
    if kappa > 0:
        r_c = kappa * r_s

    r_lo = -4.0
    r_hi = math.log10(max(float(r.max()), 10.0 * halo["r_s0"]))
    r_arr = np.logspace(r_lo, r_hi, n_int)
    rho_arr = rho_yang2024(r_arr, rho_s, r_s, r_c)
    integrand = rho_arr * r_arr ** 2

    # cumulative trapezoid -> M(<r)
    dr = np.diff(r_arr)
    seg = 0.5 * (integrand[1:] + integrand[:-1]) * dr
    m_cum = 4.0 * np.pi * np.concatenate([[0.0], np.cumsum(seg)])
    m_enc = np.interp(r, r_arr, m_cum)

    v_c2 = G_KPC_KMS * m_enc / np.maximum(r, 1e-12)
    return np.sqrt(np.maximum(v_c2, 0.0))


# ===========================================================================
# Fitting
# ===========================================================================

# One consistent multi-start grid for ALL models, so the head-to-head is fair.
_FIT_BOUNDS = [(3.0, 10.0), (-0.5, 2.0), (0.1, 1.2)]
_FIT_INITS = [
    (6.0, 0.5, 0.5),
    (7.0, 1.0, 0.5),
    (8.0, 0.0, 0.5),
    (6.5, 1.2, 0.6),
    (7.5, 0.3, 0.4),
]


def fit_galaxy(galname, model, sidm_params=None, max_iter=600):
    """Fit one SPARC galaxy with a 3-parameter model (log_rho, log_r, ups_disk).

    Returns a result dict, or None on failure. Same likelihood as phase39/phase40:
        chi2 = 0.5 sum[ (V_pred - Vobs)^2 / eV^2 ],
        V_pred^2 = V_dm^2 + Vgas^2 + ups_disk Vdisk^2 + ups_bul Vbul^2.
    """
    g = p39.load_sparc_galaxy(galname)
    if g is None or len(g["r_kpc"]) < 4:
        return None

    r = g["r_kpc"]
    Vobs = g["Vobs_kms"]
    eV = g["eV_kms"]
    Vgas = g["Vgas_kms"]
    Vdisk = g["Vdisk_kms"]
    Vbul = g["Vbul_kms"]
    ups_bul = 0.7 if np.any(Vbul > 0) else 0.0
    v_max_obs = float(np.max(Vobs))

    def chi2(params):
        log_a, log_b, ups_disk = params
        if model == "nfw":
            V_dm = p39.v_circ_nfw(r, log_a, log_b)
        elif model == "burkert":
            V_dm = p40.v_circ_burkert(r, log_a, log_b)
        elif model == "sidm_responsive":
            V_dm = v_circ_sidm_responsive(r, log_a, log_b, *sidm_params)
        elif model == "sidm_inert":
            V_dm = p39.v_circ_sidm_multi_resonant(r, log_a, log_b, v_max_obs, *sidm_params)
        else:
            raise ValueError(f"unknown model {model}")
        V_bary = np.sqrt(ups_disk * Vdisk ** 2 + ups_bul * Vbul ** 2)
        V_pred = np.sqrt(V_dm ** 2 + Vgas ** 2 + V_bary ** 2)
        return 0.5 * float(np.sum(((V_pred - Vobs) / eV) ** 2))

    best_chi2, best_p = 1e30, None
    for init in _FIT_INITS:
        try:
            res = minimize(chi2, list(init), method="Nelder-Mead",
                           options={"maxiter": max_iter, "xatol": 1e-3, "fatol": 1e-3})
            if res.fun < best_chi2:
                best_chi2, best_p = float(res.fun), res.x
        except Exception:
            continue
    if best_p is None:
        return None

    out = {
        "galaxy": galname, "model": model,
        "log_L": -best_chi2, "chi2": best_chi2, "n_points": int(len(r)), "k_fit": 3,
        "params": [float(p) for p in best_p],
    }
    if model == "sidm_responsive":
        halo = responsive_halo(best_p[0], best_p[1], *sidm_params)  # (m_chi, res, s0, a)
        out["halo"] = {
            "v_max_kms": halo["v_max_kms"], "v_eff_kms": halo["v_eff_kms"],
            "sigma_eff_cm2_per_g": halo["sigma_eff_cm2_per_g"],
            "t_c_Gyr": halo["t_c_Gyr"], "t_evol_Gyr": halo["t_evol_Gyr"],
            "tau": halo["tau"], "r_c_over_r_s0": halo["r_c_over_r_s0"],
            "phase": halo["phase"],
        }
    return out


# ===========================================================================
# Responsiveness demonstration
# ===========================================================================

def responsiveness_report(r_grid=None, log_rho_s=7.0, log_r_s=0.5,
                          sigma_probe=(1e-6, 1e-3, 0.195, 10.0, 1000.0, 1e5)) -> dict:
    """How much does V_circ move when sigma_0 moves 11 orders of magnitude?"""
    if r_grid is None:
        r_grid = np.array([1.0, 3.0, 10.0, 30.0, 50.0])
    resp, inert = {}, {}
    for s0 in sigma_probe:
        resp[repr(s0)] = v_circ_sidm_responsive(r_grid, log_rho_s, log_r_s, sigma_0=s0)
        inert[repr(s0)] = p39.v_circ_sidm_multi_resonant(
            r_grid, log_rho_s, log_r_s, 110.0, M_CHI_GEV,
            build_resonances(), s0, A_SLOPE)
    base_r = resp[repr(sigma_probe[0])]
    base_i = inert[repr(sigma_probe[0])]
    resp_max = max(float(np.max(np.abs(resp[k] - base_r))) for k in resp)
    inert_max = max(float(np.max(np.abs(inert[k] - base_i))) for k in inert)

    # also probe the other two things the inert profile was invariant to
    res = build_resonances()
    no_peaks = [dict(r, sigma_peak_cm2_per_g=0.0) for r in res]
    ref = v_circ_sidm_responsive(r_grid, log_rho_s, log_r_s)
    slope_max = max(
        float(np.max(np.abs(v_circ_sidm_responsive(r_grid, log_rho_s, log_r_s,
                                                   M_CHI_GEV, res, SIGMA_0_CM2_PER_G, a) - ref)))
        for a in (0.0, 0.7, 3.0))
    peaks_max = float(np.max(np.abs(
        v_circ_sidm_responsive(r_grid, log_rho_s, log_r_s,
                               M_CHI_GEV, no_peaks, SIGMA_0_CM2_PER_G, A_SLOPE) - ref)))

    return {
        "sigma_probe": list(sigma_probe),
        "responsive_max_abs_dV_kms": resp_max,
        "inert_max_abs_dV_kms": inert_max,
        "responsive_a_slope_max_abs_dV_kms": slope_max,
        "responsive_zeroed_peaks_max_abs_dV_kms": peaks_max,
        "responsive_curves": {k: v.tolist() for k, v in resp.items()},
        "inert_curves": {k: v.tolist() for k, v in inert.items()},
    }


def rho_sidm_source_agreement_report(rho_s=1e7, r_s=3.0) -> dict:
    """Verify gravothermal_yang2024.rho_sidm against the paper's eq. 2.1 (raises on drift).

    HISTORY: until 2026-11-04 this reported a DEFECT - the module's rho_sidm carried the
    (r^beta + r_c^beta) factor INVERTED, so at r_c = 0 its ratio to NFW was exactly (r/r_s)^2
    (0.028 at 0.5 kpc, 100.0 at 30.0 kpc for r_s = 3 kpc). The module was corrected to eq. 2.1 on
    2026-11-04 ([LocalIntegrity-Sweep-2026-11-04] F10, decision D7). It now asserts agreement and
    fails loudly if the module ever drifts back to the inverted form. The pre-fix artifact is kept
    at data/results/superseded/phase39b_sidm_responsive_profile.pre_rhofix_2026-11-04.json.
    """
    rows = []
    for r in (0.5, 1.0, 3.0, 10.0, 30.0):
        nfw = float(rho_nfw(r, rho_s, r_s))
        correct = float(rho_yang2024(r, rho_s, r_s, 0.0))
        module = float(gy.rho_sidm(r, rho_s, r_s, 0.0))
        rows.append({"r_kpc": r, "nfw": nfw, "paper_eq2.1": correct,
                     "module_rho_sidm": module, "module_over_nfw": module / nfw})
    worst = max(abs(row["module_rho_sidm"] / row["paper_eq2.1"] - 1.0) for row in rows)
    if worst > 1e-9:
        raise AssertionError(
            "gravothermal_yang2024.rho_sidm no longer matches arXiv:2305.16176 eq. 2.1 "
            f"(max relative deviation {worst:.3e}); the module drifted from the source form "
            "(the pre-2026-11-04 variant was inverted by exactly (r/r_s)^2)")
    return {
        "note": ("gravothermal_yang2024.rho_sidm verified equal to arXiv:2305.16176 eq. 2.1; "
                 "at r_c = 0 it reproduces NFW exactly. Fixed 2026-11-04; before that it was "
                 "inverted by exactly (r/r_s)^2."),
        "rows": rows,
        "max_abs_module_over_paper_minus_1": worst,
    }


# ===========================================================================
# main
# ===========================================================================

def _build_galaxy_subset():
    """Identical 15-galaxy subset to phase39.main() (seed 42)."""
    galaxies, seen = [], set()
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
            except Exception:
                continue
    np.random.seed(42)
    if len(galaxies) > 15:
        galaxies = sorted(np.random.choice(galaxies, 15, replace=False))
    filtered = []
    for gal in galaxies:
        g = p39.load_sparc_galaxy(gal)
        if g is not None and len(g["r_kpc"]) <= 50:
            filtered.append(gal)
    return filtered


def main():
    print("Phase 39b — responsive SIDM profile (Yang+ 2024) vs NFW vs Burkert", flush=True)
    print("=" * 74, flush=True)

    # ---- sanity checks printed up front ----
    print("\n[SANITY] collapse-time calibration (expect BM2 ~ 28.7 Gyr):", flush=True)
    print(f"  collapse_time_calibrated_gyr(7.1, 2.74e8, 0.141) = "
          f"{gy.collapse_time_calibrated_gyr(7.1, 2.74e8, 0.141):.3f} Gyr", flush=True)
    print(f"  collapse_time_SI_gyr        (7.1, 2.74e8, 0.141) = "
          f"{gy.collapse_time_SI_gyr(7.1, 2.74e8, 0.141):.3f} Gyr  "
          f"(literal 150*C, underestimates BM2 by ~1.82x)", flush=True)

    defect = rho_sidm_source_agreement_report()
    print("\n[SANITY] gravothermal_yang2024.rho_sidm vs paper eq. 2.1 (r_c=0):", flush=True)
    for row in defect["rows"]:
        print(f"  r={row['r_kpc']:5.1f}  NFW={row['nfw']:11.4e}  "
              f"paper={row['paper_eq2.1']:11.4e}  module={row['module_rho_sidm']:11.4e}  "
              f"module/NFW={row['module_over_nfw']:8.3f}", flush=True)

    resp = responsiveness_report()
    print("\n[SANITY] responsiveness of V_circ to sigma_0 (1e-6 .. 1e5 cm^2/g):", flush=True)
    print(f"  responsive profile max |dV| = {resp['responsive_max_abs_dV_kms']:.6f} km/s", flush=True)
    print(f"  inert phase39   max |dV| = {resp['inert_max_abs_dV_kms']:.6f} km/s", flush=True)

    # ---- fits ----
    resonances = build_resonances()
    sidm_params = (M_CHI_GEV, resonances, SIGMA_0_CM2_PER_G, A_SLOPE)
    galaxies = _build_galaxy_subset()
    print(f"\nFitting {len(galaxies)} galaxies x 4 models "
          f"(NFW, Burkert, responsive SIDM, inert SIDM)\n", flush=True)

    models = ["nfw", "burkert", "sidm_responsive", "sidm_inert"]
    results = {m: [] for m in models}
    for i, gal in enumerate(galaxies):
        line = [f"[{i+1:2d}/{len(galaxies)}] {gal:12s}"]
        for m in models:
            try:
                r = fit_galaxy(gal, m, sidm_params=sidm_params)
            except Exception as exc:  # noqa: BLE001
                r = None
                line.append(f"{m}=EXC({exc.__class__.__name__})")
            if r is None:
                line.append(f"{m}=FAIL")
            else:
                results[m].append(r)
                line.append(f"{m}={r['log_L']:.1f}")
        print("  ".join(line), flush=True)

    # keep only galaxies fitted by all four models, consistently
    common = set(x["galaxy"] for x in results["nfw"])
    for m in models:
        common &= set(x["galaxy"] for x in results[m])
    common = sorted(common)
    for m in models:
        results[m] = sorted([x for x in results[m] if x["galaxy"] in common],
                            key=lambda x: x["galaxy"])
    n_gal = len(common)

    totals = {m: float(sum(x["log_L"] for x in results[m])) for m in models}
    delta = {m: totals[m] - totals["nfw"] for m in models}

    print("\n" + "=" * 74, flush=True)
    print("HEAD-TO-HEAD (identical 3-parameter fits, same galaxies)", flush=True)
    print("=" * 74, flush=True)
    print(f"Galaxies fitted by all four models: {n_gal}", flush=True)
    for m in models:
        print(f"  total log L ({m:16s}) = {totals[m]:10.2f}   "
              f"Delta vs NFW = {delta[m]:+9.2f}", flush=True)

    # per-galaxy medians (vs NFW and, for SIDM, vs Burkert)
    med = {}
    for m in models[1:]:
        d = np.array([s["log_L"] - n["log_L"]
                      for n, s in zip(results["nfw"], results[m])])
        med[m] = float(np.median(d))
        print(f"  median per-galaxy Delta log L ({m:16s} vs NFW) = {med[m]:+9.2f}", flush=True)
    med_resp_burk = float(np.median(np.array(
        [s["log_L"] - b["log_L"]
         for b, s in zip(results["burkert"], results["sidm_responsive"])])))
    print(f"  median per-galaxy Delta log L (sidm_responsive vs Burkert) = "
          f"{med_resp_burk:+9.2f}", flush=True)

    # ---- outlier-robust summary (phase40-style) -----------------------------
    lab = np.array([x["galaxy"] for x in results["nfw"]])
    d_resp = np.array([s["log_L"] - n["log_L"]
                       for n, s in zip(results["nfw"], results["sidm_responsive"])])
    d_inert = np.array([s["log_L"] - n["log_L"]
                        for n, s in zip(results["nfw"], results["sidm_inert"])])
    thr = 50.0
    keep = np.abs(d_resp) < thr
    outliers = [str(x) for x in lab[~keep]]
    print(f"\nOutlier-robust summary (drop galaxies with |Delta logL| > {thr:g}):", flush=True)
    print(f"  outliers (responsive vs NFW): {outliers}", flush=True)
    print(f"  responsive vs NFW: total {d_resp.sum():+9.2f} -> "
          f"no-outlier total {d_resp[keep].sum():+9.2f}, "
          f"median {np.median(d_resp):+6.2f}, no-outlier median {np.median(d_resp[keep]):+6.2f}",
          flush=True)
    print(f"  inert      vs NFW: total {d_inert.sum():+9.2f} -> "
          f"no-outlier total {d_inert[keep].sum():+9.2f}, "
          f"median {np.median(d_inert):+6.2f}, no-outlier median {np.median(d_inert[keep]):+6.2f}",
          flush=True)
    # single-galaxy leverage
    lead = lab[int(np.argmax(d_resp))]
    print(f"  largest single-galaxy contribution: {lead} = {d_resp.max():+.2f} "
          f"of a {d_resp.sum():+.2f} total", flush=True)

    taus = np.array([x["halo"]["tau"] for x in results["sidm_responsive"]])
    rcs = np.array([x["halo"]["r_c_over_r_s0"] for x in results["sidm_responsive"]])
    print(f"\nResponsive cores across the 15 best fits:", flush=True)
    print(f"  tau range [{taus.min():.5f}, {taus.max():.5f}] median {np.median(taus):.5f}", flush=True)
    print(f"  r_c/r_s0 range [{rcs.min():.3f}, {rcs.max():.3f}] median {np.median(rcs):.3f}", flush=True)
    print(f"  n galaxies with r_c/r_s0 > 0.3 (sizeable core): {int((rcs > 0.3).sum())}", flush=True)

    # responsive-halo diagnostics per galaxy
    print("\nResponsive-SIDM best-fit halo diagnostics (per galaxy):", flush=True)
    for x in results["sidm_responsive"]:
        h = x["halo"]
        print(f"  {x['galaxy']:12s} logrho={x['params'][0]:5.2f} logrs={x['params'][1]:5.2f} "
              f"Vmax={h['v_max_kms']:6.1f} sig={h['sigma_eff_cm2_per_g']:7.4f} "
              f"tc={h['t_c_Gyr']:8.2f} tau={h['tau']:.4f} rc/rs0={h['r_c_over_r_s0']:.3f} "
              f"[{h['phase']}]", flush=True)

    # sensitivity to the concentration assumption
    print("\nConcentration sensitivity of the responsive profile (t_evol, tau):", flush=True)
    conc_sens = {}
    for c in (5.0, 10.0, 15.0):
        c_taus, c_tevols = [], []
        for x in results["sidm_responsive"]:
            halo = responsive_halo(x["params"][0], x["params"][1],
                                   M_CHI_GEV, resonances, SIGMA_0_CM2_PER_G,
                                   A_SLOPE, concentration=c)
            c_taus.append(halo["tau"])
            c_tevols.append(halo["t_evol_Gyr"])
        conc_sens[str(c)] = {"tau_median": float(np.median(c_taus)),
                             "t_evol_Gyr_median": float(np.median(c_tevols))}
        print(f"  c={c:5.1f}: median tau={conc_sens[str(c)]['tau_median']:.4f}, "
              f"median t_evol={conc_sens[str(c)]['t_evol_Gyr_median']:.2f} Gyr", flush=True)

    out = {
        "test": "Phase39b_SIDM_responsive_profile",
        "model": "Yang+ 2024 (arXiv:2305.16176) eq. 2.1 profile, eq. 2.2 collapse "
                 "time, eq. 2.3 evolution factors; sigma/m evaluated at 0.64 V_max",
        "n_galaxies": n_gal,
        "galaxies": common,
        "particle_model": {
            "m_chi_GeV": M_CHI_GEV, "sigma_0_cm2_per_g": SIGMA_0_CM2_PER_G,
            "a_slope": A_SLOPE, "v_targets_kms": V_TARGETS,
            "sigma_peaks_cm2_per_g": SIGMA_PEAKS, "width_fracs": WIDTH_FRACS,
        },
        "assumptions": {
            "concentration_for_m_vir": CONCENTRATION,
            "sigma_eval_velocity": "0.64 * V_max,NFW (Yang+ 2024 nu_eff)",
            "collapse_time_normalisation": "BM2-calibrated (28.7 Gyr at 7.1 cm^2/g)",
        },
        "totals": {
            "logL_nfw": totals["nfw"],
            "logL_burkert": totals["burkert"],
            "logL_sidm_responsive": totals["sidm_responsive"],
            "logL_sidm_inert": totals["sidm_inert"],
            "delta_responsive_minus_nfw": delta["sidm_responsive"],
            "delta_responsive_minus_burkert": delta["sidm_responsive"] - delta["burkert"],
            "delta_inert_minus_nfw": delta["sidm_inert"],
            "median_delta_responsive_minus_nfw": med["sidm_responsive"],
            "median_delta_responsive_minus_burkert": med_resp_burk,
        },
        "outlier_robust": {
            "threshold": thr,
            "outliers_responsive_vs_nfw": outliers,
            "responsive_vs_nfw_no_outlier_total": float(d_resp[keep].sum()),
            "responsive_vs_nfw_no_outlier_median": float(np.median(d_resp[keep])),
            "inert_vs_nfw_no_outlier_total": float(d_inert[keep].sum()),
            "inert_vs_nfw_no_outlier_median": float(np.median(d_inert[keep])),
            "largest_single_galaxy": lead,
            "largest_single_galaxy_value": float(d_resp.max()),
            "responsive_total": float(d_resp.sum()),
        },
        "core_distribution": {
            "tau_min": float(taus.min()), "tau_max": float(taus.max()),
            "tau_median": float(np.median(taus)),
            "r_c_over_r_s0_min": float(rcs.min()), "r_c_over_r_s0_max": float(rcs.max()),
            "r_c_over_r_s0_median": float(np.median(rcs)),
            "n_with_rc_over_rs0_gt_0p3": int((rcs > 0.3).sum()),
        },
        "responsiveness": {
            "responsive_max_abs_dV_kms": resp["responsive_max_abs_dV_kms"],
            "inert_max_abs_dV_kms": resp["inert_max_abs_dV_kms"],
            "responsive_a_slope_max_abs_dV_kms": resp["responsive_a_slope_max_abs_dV_kms"],
            "responsive_zeroed_peaks_max_abs_dV_kms":
                resp["responsive_zeroed_peaks_max_abs_dV_kms"],
            "sigma_probe": resp["sigma_probe"],
        },
        "rho_sidm_source_agreement": defect,
        "concentration_sensitivity": conc_sens,
        "results": results,
        "caveats": [
            "The responsive profile IS sigma/m-responsive (see responsiveness block); "
            "the inert phase39 profile is bit-for-bit invariant.",
            "gravothermal_yang2024.rho_sidm was inverted vs paper eq. 2.1 until 2026-11-04 "
            "(corrected; see the rho_sidm_source_agreement block) - this module re-implements "
            "eq. 2.1 independently and never called the broken form.",
            "Collapse time uses the BM2-calibrated normalisation, which the module's "
            "own comments note underestimates independent halos (e.g. Cosmo-501) by ~2.15x.",
            "sigma_eff/m is evaluated at one characteristic velocity, not MB-integrated.",
            "M_vir -> z_f -> t_evol uses a fixed concentration c=10; sensitivity reported.",
            "3-parameter fits (log_rho, log_r, ups_disk) for every model; no Occam "
            "penalty applied here (phase40 covers the full-physical-model penalty).",
        ],
    }

    out_dir = Path(_CODE_DIR).parents[0] / "data" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "phase39b_sidm_responsive_profile.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"\nResults written to: {out_path}", flush=True)


if __name__ == "__main__":
    main()
