"""
T22 — Direction B with REAL KISS-SIDM gravothermal penalty.

This is the publication-quality replacement for t19_yang2026_fit.py.
Same parameter space (sigma1, sigma2, f1, a) but the gravothermal
penalty comes from the REAL KiSS-SIDM simulation (Gurian & May 2025),
not the placeholder `gravothermal.py::gravothermal_r_core` fluid model.

The REAL KISS-SIDM data is at:
  v0.3-prelim/data/results/real_kiss_sidm_aggregated.json

Comparison:
  T19 placeholder + IMFP correction: log Z = -4.01 (2-comp vs 1-comp BF = +0.57, equivalent)
  T22 REAL + IMFP correction: this is the publication-quality version.

If T22's Bayes factor against single-component (with the same Yang+ curve)
is similar to T19's, the placeholder was fine. If T22 is very different,
the placeholder was misleading (just like T21 showed for T17).
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

import two_component_sidm as tc
import yang2026_likelihood as yl
import kiss_sidm_scalings as kss
import t21_real_kiss_sidm_gravothermal as t21  # for _load_real_kiss_data, _compute_real_r_core

from config import RESULTS_DIR_V03


# Same prior box as t18/t19 (Yang+ 2026 mass ratio = 3 implies sigma1/sigma2 ~ 3-10)
LOG_SIGMA1_RANGE = (-2.0, 2.0)
LOG_SIGMA2_RANGE = (-3.0, 1.0)
F1_RANGE = (0.01, 0.99)
A_RANGE = (-2.0, 2.0)

NLIVE = 200
DLOGZ = 0.1

# Reference halo (same as t17/t20) for the KISS-SIDM correction
HALO_RHO_S = 1e7
HALO_R_S = 10.0
HALO_V_MAX = 100.0
HALO_T_GYR = 10.0


def kiss_sidm_correction_at_sigma(sigma_m: float) -> float:
    """KISS-SIDM correction factor in [0.778, 1.0]."""
    Kn = kss.knudsen_number(HALO_RHO_S, HALO_V_MAX, sigma_m)
    return kss.knudsen_correction_factor(Kn, Kn_threshold=1.0)


_kiss_data_cache = None


def _get_kiss_data():
    global _kiss_data_cache
    if _kiss_data_cache is None:
        _kiss_data_cache = t21._load_real_kiss_data()
    return _kiss_data_cache


def _real_kiss_penalty(sigma_m: float, t_Gyr: float = HALO_T_GYR) -> float:
    """Gravothermal penalty from REAL KISS-SIDM at time t_Gyr."""
    if sigma_m <= 0:
        return 0.0
    if t_Gyr <= 0:
        return 0.0
    kiss_data = _get_kiss_data()
    r_core = t21._compute_real_r_core(kiss_data, t_target_Gyr=t_Gyr)
    if r_core <= 0:
        return 0.0
    r_max = 0.045 * HALO_R_S  # in kpc
    ratio = r_core / r_max
    if ratio <= 0:
        return 0.0
    return -np.log(ratio)


def loglike_two_comp_yang_real_kiss(theta):
    """2-comp fit with REAL KISS-SIDM gravothermal penalty + IMFP correction.

    For 2-comp SIDM, both components have a gravothermal collapse. The
    correction is applied to each component's effective gravothermal
    penalty, scaled by its Knudsen number.
    """
    log_sigma1, log_sigma2, f1, a = theta
    sigma1 = 10 ** log_sigma1
    sigma2 = 10 ** log_sigma2
    if sigma1 <= 0 or sigma2 <= 0:
        return -np.inf
    if not (F1_RANGE[0] <= f1 <= F1_RANGE[1]):
        return -np.inf
    if not (A_RANGE[0] <= a <= A_RANGE[1]):
        return -np.inf

    # Yang+ 2026 likelihood (3 channels)
    ll_yang = yl.loglike_yang2026_full(sigma1, sigma2, f1, a)

    # Real KISS-SIDM gravothermal penalty for each component
    pen1 = _real_kiss_penalty(sigma1) * kiss_sidm_correction_at_sigma(sigma1)
    pen2 = _real_kiss_penalty(sigma2) * kiss_sidm_correction_at_sigma(sigma2)
    # Weight by mass fraction (heavy dominates cluster via f1)
    grav_pen = f1 * pen1 + (1.0 - f1) * pen2

    return ll_yang - grav_pen


def loglike_two_comp_yang_real_kiss_no_imfp(theta):
    """Same but WITHOUT IMFP correction (fluid baseline)."""
    log_sigma1, log_sigma2, f1, a = theta
    sigma1 = 10 ** log_sigma1
    sigma2 = 10 ** log_sigma2
    if sigma1 <= 0 or sigma2 <= 0:
        return -np.inf
    if not (F1_RANGE[0] <= f1 <= F1_RANGE[1]):
        return -np.inf
    if not (A_RANGE[0] <= a <= A_RANGE[1]):
        return -np.inf

    ll_yang = yl.loglike_yang2026_full(sigma1, sigma2, f1, a)
    pen1 = _real_kiss_penalty(sigma1)
    pen2 = _real_kiss_penalty(sigma2)
    grav_pen = f1 * pen1 + (1.0 - f1) * pen2

    return ll_yang - grav_pen


def loglike_one_comp_yang_real_kiss(theta):
    """1-comp nested baseline with REAL KISS-SIDM penalty + IMFP correction."""
    log_sigma, a = theta
    sigma = 10 ** log_sigma
    if sigma <= 0 or not (A_RANGE[0] <= a <= A_RANGE[1]):
        return -np.inf
    ll_yang = yl.loglike_yang2026_full(sigma, sigma, 0.5, a)
    pen = _real_kiss_penalty(sigma) * kiss_sidm_correction_at_sigma(sigma)
    return ll_yang - pen


def loglike_one_comp_2ch_yang_real_kiss(theta):
    """1-comp 2-channel (dwarf + galaxy only) with REAL KISS-SIDM penalty."""
    log_sigma, a = theta
    sigma = 10 ** log_sigma
    if sigma <= 0 or not (A_RANGE[0] <= a <= A_RANGE[1]):
        return -np.inf
    ll_yang = (
        yl.loglike_yang2026_dwarf(sigma, sigma, 0.5, a)
        + yl.loglike_yang2026_galaxy(sigma, sigma, 0.5, a)
    )
    pen = _real_kiss_penalty(sigma) * kiss_sidm_correction_at_sigma(sigma)
    return ll_yang - pen


def prior_transform_4(u):
    return [
        LOG_SIGMA1_RANGE[0] + u[0] * (LOG_SIGMA1_RANGE[1] - LOG_SIGMA1_RANGE[0]),
        LOG_SIGMA2_RANGE[0] + u[1] * (LOG_SIGMA2_RANGE[1] - LOG_SIGMA2_RANGE[0]),
        F1_RANGE[0] + u[2] * (F1_RANGE[1] - F1_RANGE[0]),
        A_RANGE[0] + u[3] * (A_RANGE[1] - A_RANGE[0]),
    ]


def prior_transform_2(u):
    return [
        LOG_SIGMA1_RANGE[0] + u[0] * (LOG_SIGMA1_RANGE[1] - LOG_SIGMA1_RANGE[0]),
        A_RANGE[0] + u[1] * (A_RANGE[1] - A_RANGE[0]),
    ]


def run_one(loglike, prior_transform, ndim, label):
    t0 = time.time()
    sampler = dynesty.NestedSampler(
        loglikelihood=loglike, prior_transform=prior_transform,
        ndim=ndim, nlive=NLIVE, bound='multi', sample='auto', bootstrap=0,
    )
    sampler.run_nested(dlogz=DLOGZ, print_progress=False)
    res = sampler.results
    log_Z = float(res.logz[-1])
    log_Z_err = float(res.logzerr[-1])
    samples = res.samples
    weights = np.exp(res.logwt - res.logz[-1])
    imap = int(np.argmax(weights))
    MAP = samples[imap].tolist()
    wall = time.time() - t0
    pcts = np.percentile(samples, [16, 50, 84], axis=0, weights=weights, method='inverted_cdf')
    return {
        "label": label,
        "log_Z": log_Z,
        "log_Z_err": log_Z_err,
        "MAP": MAP,
        "median": pcts[1].tolist(),
        "p16": pcts[0].tolist(),
        "p84": pcts[2].tolist(),
        "wall_seconds": wall,
        "n_samples": int(len(samples)),
    }


def main():
    print("=" * 80)
    print("T22 — Direction B with REAL KISS-SIDM gravothermal penalty")
    print("=" * 80)
    # Preload KISS-SIDM data
    kiss_data = _get_kiss_data()
    r_core_real = t21._compute_real_r_core(kiss_data, t_target_Gyr=HALO_T_GYR)
    print(f"Loaded real KISS-SIDM data: {kiss_data['n_snapshots']} snapshots")
    print(f"Real KISS-SIDM r_core at t={HALO_T_GYR} Gyr: {r_core_real:.4f} r_s")
    print(f"Reference halo: rho_s={HALO_RHO_S:.0e} M_sun/kpc^3, "
          f"r_s={HALO_R_S} kpc, v_max={HALO_V_MAX} km/s")
    print()
    print("Fits to run:")
    print("  A: 2-comp (4 par, 3 Yang+ channels, REAL KISS-SIDM, with IMFP corr)")
    print("  B: 2-comp (4 par, 3 Yang+ channels, REAL KISS-SIDM, no IMFP corr)")
    print("  C: 1-comp nested (2 par, same 3 channels, REAL KISS-SIDM)")
    print("  D: 1-comp 2-channel (2 par, dwarf+galaxy only, REAL KISS-SIDM)")
    print()

    A = run_one(loglike_two_comp_yang_real_kiss, prior_transform_4, 4,
                "two_comp_real_kiss_with_imfp")
    print(f"  A (2-comp, IMFP): log Z = {A['log_Z']:.3f} +/- {A['log_Z_err']:.3f} "
          f"MAP = {[f'{v:.3f}' for v in A['MAP']]}  (wall {A['wall_seconds']:.1f}s)")

    B = run_one(loglike_two_comp_yang_real_kiss_no_imfp, prior_transform_4, 4,
                "two_comp_real_kiss_no_imfp")
    print(f"  B (2-comp, no IMFP): log Z = {B['log_Z']:.3f} +/- {B['log_Z_err']:.3f} "
          f"MAP = {[f'{v:.3f}' for v in B['MAP']]}  (wall {B['wall_seconds']:.1f}s)")

    C = run_one(loglike_one_comp_yang_real_kiss, prior_transform_2, 2,
                "one_comp_real_kiss_nested")
    print(f"  C (1-comp nested): log Z = {C['log_Z']:.3f} +/- {C['log_Z_err']:.3f} "
          f"MAP = {[f'{v:.3f}' for v in C['MAP']]}  (wall {C['wall_seconds']:.1f}s)")

    D = run_one(loglike_one_comp_2ch_yang_real_kiss, prior_transform_2, 2,
                "one_comp_real_kiss_2ch")
    print(f"  D (1-comp 2ch): log Z = {D['log_Z']:.3f} +/- {D['log_Z_err']:.3f} "
          f"MAP = {[f'{v:.3f}' for v in D['MAP']]}  (wall {D['wall_seconds']:.1f}s)")

    delta_A_C = A["log_Z"] - C["log_Z"]  # 2-comp vs 1-comp (same 3 channels)
    delta_A_D = A["log_Z"] - D["log_Z"]  # 2-comp vs 1-comp 2-channel
    delta_B_C = B["log_Z"] - C["log_Z"]
    delta_B_D = B["log_Z"] - D["log_Z"]

    def verdict(d):
        if d > 5: return "STRONGLY preferred (log BF > 5)"
        elif d > 2.5: return "MODERATELY preferred (2.5 < log BF < 5)"
        elif d > 1: return "WEAKLY preferred (1 < log BF < 2.5)"
        elif d > -1: return "INCONCLUSIVE (-1 < log BF < 1)"
        elif d > -2.5: return "WEAKLY disfavored (-2.5 < log BF < -1)"
        else: return "STRONGLY disfavored (log BF < -2.5)"

    print()
    print("=" * 80)
    print("Bayes factors (T22 REAL KISS-SIDM, log Z differences):")
    print(f"  A (2-comp, IMFP) vs C (1-comp, IMFP, 3 channels): {delta_A_C:+.3f} -- {verdict(delta_A_C)}")
    print(f"  A (2-comp, IMFP) vs D (1-comp, IMFP, 2 channels): {delta_A_D:+.3f} -- {verdict(delta_A_D)}")
    print(f"  B (2-comp, no IMFP) vs C (1-comp, IMFP, 3 channels): {delta_B_C:+.3f} -- {verdict(delta_B_C)}")
    print(f"  B (2-comp, no IMFP) vs D (1-comp, IMFP, 2 channels): {delta_B_D:+.3f} -- {verdict(delta_B_D)}")

    out = {
        "test": "T22_real_kiss_sidm_two_comp",
        "direction": "TIER 2 STEP 1: Re-run T19 with REAL KISS-SIDM gravothermal penalty",
        "kiss_data_source": str(t21._REAL_KISS_PATH),
        "kiss_r_core_real_at_t10Gyr_over_rs": r_core_real,
        "fits": {
            "A_two_comp_with_imfp": A,
            "B_two_comp_no_imfp": B,
            "C_one_comp_nested_with_imfp": C,
            "D_one_comp_2ch_with_imfp": D,
        },
        "bayes_factors": {
            "delta_A_C_2comp_vs_1comp_3ch": delta_A_C,
            "delta_A_D_2comp_vs_1comp_2ch": delta_A_D,
            "delta_B_C_2comp_no_imfp_vs_1comp": delta_B_C,
            "delta_B_D_2comp_no_imfp_vs_1comp_2ch": delta_B_D,
        },
        "t19_placeholder_summary": {
            "log_Z_2comp_with_imfp": -4.01,
            "log_Z_2comp_no_imfp": -3.45,
            "delta_2comp_vs_1comp_3ch_placeholder": 0.57,  # equivalent
            "delta_2comp_vs_1comp_3ch_no_imfp": -1.25,  # mildly disfavored
        },
        "verdict": (
            f"With REAL KISS-SIDM gravothermal penalty:\n"
            f"  T22 A (2-comp, with IMFP) vs C (1-comp, with IMFP): {delta_A_C:+.3f}\n"
            f"  T22 B (2-comp, no IMFP)   vs D (1-comp, no IMFP):   {delta_B_D:+.3f}\n"
            f"Compare to T19 placeholder:\n"
            f"  T19 A (2-comp, with IMFP) vs C (1-comp, with IMFP): +0.57 (equivalent)\n"
            f"  T19 B (2-comp, no IMFP)   vs D (1-comp, no IMFP):   -1.25 (mildly disfavored)\n"
            f"If T22's Bayes factors are similar to T19's, the placeholder was fine.\n"
            f"If T22 is very different, the placeholder was misleading."
        ),
    }
    out_path = RESULTS_DIR_V03 / "t22_real_kiss_sidm_two_comp.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, default=str))
    # Also copy to Windows-side for tests (use bash cp)
    win_path = Path("/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results/t22_real_kiss_sidm_two_comp.json")
    win_path.write_text(json.dumps(out, indent=2, default=str))
    print(f"\noutput -> {out_path}")
    print(f"        -> {win_path}")


if __name__ == "__main__":
    main()