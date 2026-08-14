"""
T25 — Marginalize over c_vir scatter (T2.5 from R2 review).

SASHIMI-SIDM forward model takes c_vir as a fixed input (from Duffy+ 2008
mass-concentration relation). Real halos have scatter of ~0.1-0.2 dex
around the median relation. The T-series fits use the median c_vir,
which introduces systematic error.

This script runs a representative SASHIMI fit on a single SPARC-like
galaxy and compares:
  (A) Fixed c_vir at the median (the current approach)
  (B) Marginalized over c_vir with prior log10(c_vir) ~ N(median, 0.2 dex)

If the MAP sigma/m shifts by more than 0.2 dex, the c_vir assumption is
a real source of systematic uncertainty. If less, it's a minor effect.

References:
  Duffy et al. 2008 (mass-concentration relation, R^200 definition)
  Dutton & Macciò 2014 (updated relation with relaxation)
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "v0.1-prelim" / "code"))

import numpy as np
import dynesty

import sashimi_parametric as sp
import config

from config import RESULTS_DIR_V03


# Representative MW-like halo (the canonical test case)
M_VIR_FIXED = 1e12  # M_sun
Z_FORM = 2.0  # formation redshift
V_MAX = 200.0  # km/s


def estimate_cvir_median(M_vir: float) -> float:
    """Dutton & Macciò 2014 median mass-concentration relation."""
    return 10 ** (0.54 - 0.13 * np.log10(M_vir / 1e12))


def forward_model_sashimi(M_vir, z_form, c_vir, sigma_0, a):
    """Run SASHIMI forward model and return predicted V_max.

    The forward model:
      1. NFW profile from (M_vir, z, c_vir) → (r_s, rho_s)
      2. Core-collapse timescale → (r_c, rho_c)
      3. SASHIMI analytic r_core(V) relation
      4. Effective sigma/m at galaxy V_max via velocity dependence
    """
    rho_s_nfw, r_s_nfw = sp.NFW_profile_params(M_vir, z_form, c_vir)
    if sigma_0 <= 0:
        return 0.0
    # Compute the effective sigma at V_max
    sigma_m_at_v = sigma_0 * (V_MAX / config.V_REF) ** (-a)
    # Collapse timescale (Eq. 21 in SASHIMI paper, simplified)
    # t_cc ~ 30 * (sigma/m_eff)^{-1} * (r_s / 10 kpc) * (rho_s / 10^7)^-0.5 Gyr
    r_s_kpc = r_s_nfw
    rho_s_Msun_kpc3 = rho_s_nfw
    t_cc = 30.0 * (sigma_m_at_v / 1.0) ** (-1) * (r_s_kpc / 10.0) * (rho_s_Msun_kpc3 / 1e7) ** (-0.5)
    # Age of universe at z_form (rough): 3.3 Gyr at z=2
    t_universe_at_form = 3.3  # Gyr
    # If t_cc < t_age, full collapse; else partial
    t_tilde = t_universe_at_form / t_cc if t_cc > 0 else 0.0
    t_tilde = min(t_tilde, 1.5)  # cap at 1.5 (full collapse)
    # Vmax ratio from SASHIMI analytic
    Vmax_ratio = sp.Vmax_ratio(t_tilde)
    # New Vmax = Vmax_initial * Vmax_ratio
    # But Vmax_initial is determined by NFW params; for our purpose
    # Vmax_at_present = Vmax_initial * Vmax_ratio
    Vmax_initial = sp.vmax_kms_for_halo(M_vir, z_form, c_vir)
    return Vmax_initial * Vmax_ratio


def loglike_with_fixed_cvir(theta):
    """5D fit with c_vir FIXED at the median.

    theta = [log_sigma_0, a, M_vir_log, z_form, fixed c_vir doesn't matter]
    Here we use a simplified version: 2D fit, M_vir and z_form fixed,
    c_vir fixed at median.
    """
    log_sigma_0, a = theta
    sigma_0 = 10 ** log_sigma_0
    if sigma_0 <= 0:
        return -np.inf
    c_vir = estimate_cvir_median(M_VIR_FIXED)
    Vmax_pred = forward_model_sashimi(M_VIR_FIXED, Z_FORM, c_vir, sigma_0, a)
    # Toy likelihood: prefer Vmax_pred close to V_MAX
    sigma_V_kms = 20.0  # observational uncertainty in V_max
    return -0.5 * ((Vmax_pred - V_MAX) / sigma_V_kms) ** 2


def loglike_with_marginalized_cvir(theta):
    """2D fit with c_vir MARGINALIZED over a Gaussian prior.

    We use a Gaussian quadrature approximation to integrate over c_vir.
    The c_vir prior: log10(c_vir) ~ N(log10(c_vir_median), 0.2 dex)
    """
    log_sigma_0, a = theta
    sigma_0 = 10 ** log_sigma_0
    if sigma_0 <= 0:
        return -np.inf

    c_vir_median = estimate_cvir_median(M_VIR_FIXED)
    # 5-point quadrature over c_vir (log-uniform between 0.5x and 2x median)
    log_cv_med = np.log10(c_vir_median)
    log_cv_samples = log_cv_med + np.array([-0.4, -0.2, 0.0, 0.2, 0.4])
    weights = np.array([0.0625, 0.25, 0.375, 0.25, 0.0625])  # Simpson-like

    # Marginalize: log Z_cvir = log mean(exp(loglike(c_vir)))
    log_likes = []
    for log_cv in log_cv_samples:
        cv = 10 ** log_cv
        Vmax_pred = forward_model_sashimi(M_VIR_FIXED, Z_FORM, cv, sigma_0, a)
        ll = -0.5 * ((Vmax_pred - V_MAX) / 20.0) ** 2
        log_likes.append(ll)
    log_likes = np.array(log_likes)
    return np.log(np.sum(weights * np.exp(log_likes - np.max(log_likes)))) + np.max(log_likes)


def run_one(loglike, prior_transform, ndim, label):
    t0 = time.time()
    sampler = dynesty.NestedSampler(
        loglikelihood=loglike, prior_transform=prior_transform,
        ndim=ndim, nlive=200, bound='multi', sample='auto', bootstrap=0,
    )
    sampler.run_nested(dlogz=0.1, print_progress=False)
    res = sampler.results
    log_Z = float(res.logz[-1])
    samples = res.samples
    weights = np.exp(res.logwt - res.logz[-1])
    imap = int(np.argmax(weights))
    MAP = samples[imap].tolist()
    wall = time.time() - t0
    return {"label": label, "log_Z": log_Z, "MAP": MAP, "wall_seconds": wall}


def prior_transform_2(u):
    return [
        config.LOG_SIGMA_M_RANGE[0] + u[0] * (config.LOG_SIGMA_M_RANGE[1] - config.LOG_SIGMA_M_RANGE[0]),
        config.A_RANGE[0] + u[1] * (config.A_RANGE[1] - config.A_RANGE[0]),
    ]


def main():
    print("=" * 80)
    print("T25 — Marginalize over c_vir scatter (T2.5)")
    print("=" * 80)
    print(f"Reference halo: M_vir = {M_VIR_FIXED:.1e} M_sun, z_form = {Z_FORM}, V_max = {V_MAX} km/s")
    print(f"Median c_vir (Dutton & Macciò 2014): {estimate_cvir_median(M_VIR_FIXED):.2f}")
    print()

    print("Running fit A: c_vir FIXED at median...")
    A = run_one(loglike_with_fixed_cvir, prior_transform_2, 2, "fixed_cvir")
    print(f"  log Z = {A['log_Z']:.3f}  MAP = {[f'{v:.3f}' for v in A['MAP']]}  (wall {A['wall_seconds']:.1f}s)")

    print("Running fit B: c_vir MARGINALIZED (5-point Gaussian quadrature, 0.2 dex)...")
    B = run_one(loglike_with_marginalized_cvir, prior_transform_2, 2, "marginalized_cvir")
    print(f"  log Z = {B['log_Z']:.3f}  MAP = {[f'{v:.3f}' for v in B['MAP']]}  (wall {B['wall_seconds']:.1f}s)")

    delta_log_Z = B["log_Z"] - A["log_Z"]
    delta_map_sm = B["MAP"][0] - A["MAP"][0]
    delta_map_a = B["MAP"][1] - A["MAP"][1]

    def verdict(d_sm):
        if abs(d_sm) < 0.05:
            return "NEGLIGIBLE (shift < 0.05 dex)"
        elif abs(d_sm) < 0.2:
            return "MINOR (0.05-0.2 dex shift)"
        elif abs(d_sm) < 0.5:
            return "MODERATE (0.2-0.5 dex shift)"
        else:
            return "MAJOR (shift > 0.5 dex)"

    print()
    print("=" * 80)
    print("Comparison:")
    print(f"  log Z change (marginalized - fixed): {delta_log_Z:+.3f}")
    print(f"  Δ log σ/m (marginalized - fixed):    {delta_map_sm:+.3f}  {verdict(delta_map_sm)}")
    print(f"  Δ a      (marginalized - fixed):    {delta_map_a:+.3f}")

    out = {
        "test": "T25_cvir_marginalization",
        "direction": "T2.5: Marginalize over c_vir scatter in SASHIMI forward model",
        "halo": {
            "M_vir_Msun": M_VIR_FIXED,
            "z_form": Z_FORM,
            "V_max_kms": V_MAX,
            "c_vir_median": estimate_cvir_median(M_VIR_FIXED),
        },
        "fits": {
            "A_fixed_cvir": A,
            "B_marginalized_cvir": B,
        },
        "comparison": {
            "delta_log_Z": delta_log_Z,
            "delta_log_sm_MAP": delta_map_sm,
            "delta_a_MAP": delta_map_a,
            "verdict": verdict(delta_map_sm),
        },
        "interpretation": (
            f"Marginalizing over c_vir (5-point quadrature, 0.2 dex prior):\n"
            f"  Δ log σ/m = {delta_map_sm:+.3f} ({verdict(delta_map_sm)})\n"
            f"  Δ log Z   = {delta_log_Z:+.3f}\n"
            f"If the verdict is NEGLIGIBLE or MINOR, the c_vir assumption is not a"
            f" major source of systematic error.\n"
            f"If MODERATE or MAJOR, marginalization is recommended for production fits."
        ),
    }
    out_path = RESULTS_DIR_V03 / "t25_cvir_marginalization.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, default=str))
    win_path = Path("/mnt/c/Users/lamkuenai/projects/dm-sidm-pipeline/v0.3-prelim/data/results/t25_cvir_marginalization.json")
    win_path.write_text(json.dumps(out, indent=2, default=str))
    print(f"\noutput -> {out_path}")
    print(f"        -> {win_path}")


if __name__ == "__main__":
    main()