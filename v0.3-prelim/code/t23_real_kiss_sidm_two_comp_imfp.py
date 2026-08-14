"""
T23 — TIER 3: 2-comp SIDM + KISS-SIDM IMFP correction, with REAL KISS-SIDM
gravothermal penalty (instead of placeholder).

This is the publication-quality replacement for t20_two_comp_kiss_sidm_fit.py.
Same structure as T22 but adds the IMFP correction (factor 0.778 in IMFP regime)
to the gravothermal penalty, mirroring T20's combined approach.

Key insight: with REAL KISS-SIDM (smaller r_core = 0.0085 r_s vs placeholder
0.05 r_s), the gravothermal penalty is LESS severe. Combined with IMFP
correction (which reduces the penalty further at high sigma/m), this
should shift the posterior toward LARGER sigma_eff.
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


# Same prior box as T19, T20, T22
LOG_SIGMA1_RANGE = (-2.0, 2.0)
LOG_SIGMA2_RANGE = (-3.0, 1.0)
F1_RANGE = (0.01, 0.99)
A_RANGE = (-2.0, 2.0)

NLIVE = 200
DLOGZ = 0.1

# Reference halo (same as t17/t20/t22)
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


def loglike_two_comp_real_kiss_imfp(theta):
    """T20-style combined fit with REAL KISS-SIDM penalty + IMFP correction.

    The IMFP correction reduces the gravothermal penalty in the IMFP regime,
    which has the effect of allowing LARGER sigma_eff at cluster scale.
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

    # Yang+ 2026 published likelihood (3 channels)
    ll = yl.loglike_yang2026_full(sigma1, sigma2, f1, a)

    # Real KISS-SIDM penalty + IMFP correction, applied to both components
    sigma1_v_ref = tc.sigma_at_v(sigma1, a, 100.0)
    sigma2_v_ref = tc.sigma_at_v(sigma2, a, 100.0)
    corr1 = kiss_sidm_correction_at_sigma(sigma1_v_ref)
    corr2 = kiss_sidm_correction_at_sigma(sigma2_v_ref)
    pen1 = _real_kiss_penalty(sigma1_v_ref) * corr1
    pen2 = _real_kiss_penalty(sigma2_v_ref) * corr2
    # Weighted by mass fraction (heavy=sigma1, light=sigma2)
    kiss_prior = -1.0 * (f1 * pen1 + (1 - f1) * pen2)

    return ll + kiss_prior


def loglike_two_comp_real_kiss_no_imfp(theta):
    """Same but WITHOUT IMFP correction (fluid baseline with real r_core)."""
    log_sigma1, log_sigma2, f1, a = theta
    sigma1 = 10 ** log_sigma1
    sigma2 = 10 ** log_sigma2
    if sigma1 <= 0 or sigma2 <= 0:
        return -np.inf
    if not (F1_RANGE[0] <= f1 <= F1_RANGE[1]):
        return -np.inf
    if not (A_RANGE[0] <= a <= A_RANGE[1]):
        return -np.inf

    ll = yl.loglike_yang2026_full(sigma1, sigma2, f1, a)
    pen1 = _real_kiss_penalty(sigma1)
    pen2 = _real_kiss_penalty(sigma2)
    kiss_prior = -1.0 * (f1 * pen1 + (1 - f1) * pen2)

    return ll + kiss_prior


def prior_transform_4(u):
    return [
        LOG_SIGMA1_RANGE[0] + u[0] * (LOG_SIGMA1_RANGE[1] - LOG_SIGMA1_RANGE[0]),
        LOG_SIGMA2_RANGE[0] + u[1] * (LOG_SIGMA2_RANGE[1] - LOG_SIGMA2_RANGE[0]),
        F1_RANGE[0] + u[2] * (F1_RANGE[1] - F1_RANGE[0]),
        A_RANGE[0] + u[3] * (A_RANGE[1] - A_RANGE[0]),
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
    print("T23 — TIER 3: 2-comp SIDM with REAL KISS-SIDM penalty + IMFP correction")
    print("=" * 80)
    kiss_data = _get_kiss_data()
    r_core_real = t21._compute_real_r_core(kiss_data, t_target_Gyr=HALO_T_GYR)
    print(f"Real KISS-SIDM r_core at t={HALO_T_GYR} Gyr: {r_core_real:.4f} r_s")
    print(f"Reference halo: rho_s={HALO_RHO_S:.0e} M_sun/kpc^3, "
          f"r_s={HALO_R_S} kpc, v_max={HALO_V_MAX} km/s, t={HALO_T_GYR} Gyr")
    print()

    print("Running T23 A (2-comp, with IMFP, REAL KISS-SIDM)...")
    A = run_one(loglike_two_comp_real_kiss_imfp, prior_transform_4, 4,
                "two_comp_real_kiss_with_imfp")
    print(f"  log Z = {A['log_Z']:.3f} +/- {A['log_Z_err']:.3f} "
          f"MAP = {[f'{v:.3f}' for v in A['MAP']]}  (wall {A['wall_seconds']:.1f}s)")

    print("Running T23 B (2-comp, no IMFP, REAL KISS-SIDM)...")
    B = run_one(loglike_two_comp_real_kiss_no_imfp, prior_transform_4, 4,
                "two_comp_real_kiss_no_imfp")
    print(f"  log Z = {B['log_Z']:.3f} +/- {B['log_Z_err']:.3f} "
          f"MAP = {[f'{v:.3f}' for v in B['MAP']]}  (wall {B['wall_seconds']:.1f}s)")

    # Compare to T22 (2-comp without IMFP correction baked into gravothermal;
    # T22 B is the right comparison for T23 B, T22 A for T23 A)
    print()
    print("=" * 80)
    print("Comparison:")
    print(f"  T20 placeholder + IMFP: log Z = -5.47 (placeholder gravothermal penalty)")
    print(f"  T22 A REAL + IMFP:      log Z = -7.82 (penalty applied to each comp separately)")
    print(f"  T22 B REAL no IMFP:     log Z = -7.95 (penalty applied to each comp separately)")
    print(f"  T23 A REAL + IMFP:      log Z = {A['log_Z']:.3f} (this fit, with sigma_at_v)")
    print(f"  T23 B REAL no IMFP:     log Z = {B['log_Z']:.3f} (this fit, with sigma_at_v)")

    delta_A_B = A['log_Z'] - B['log_Z']
    print(f"\nIMFP correction effect (T23 A - T23 B): {delta_A_B:+.3f}")
    if delta_A_B > 0.5:
        imfp_verdict = "IMFP correction substantially improves fit"
    elif delta_A_B > 0:
        imfp_verdict = "IMFP correction mildly improves fit"
    else:
        imfp_verdict = "IMFP correction does NOT improve fit (penalty was already weak)"
    print(f"  Verdict: {imfp_verdict}")

    out = {
        "test": "T23_real_kiss_sidm_two_comp_imfp",
        "direction": "TIER 2 STEP 2: Re-run T20 (combined) with REAL KISS-SIDM gravothermal penalty",
        "kiss_data_source": str(t21._REAL_KISS_PATH),
        "kiss_r_core_real_at_t10Gyr_over_rs": r_core_real,
        "fits": {
            "A_two_comp_with_imfp": A,
            "B_two_comp_no_imfp": B,
        },
        "t22_comparison": {
            "T22_A_REAL_with_IMFP": -7.82,
            "T22_B_REAL_no_IMFP": -7.95,
        },
        "t20_placeholder_summary": {
            "log_Z": -5.47,
            "MAP": [0.0, -0.5, 0.5, 0.5],  # placeholder
        },
        "imfp_correction_effect": {
            "delta_log_Z_A_minus_B": delta_A_B,
            "verdict": imfp_verdict,
        },
        "verdict": (
            f"With REAL KISS-SIDM gravothermal penalty + IMFP correction:\n"
            f"  T23 A (with IMFP): log Z = {A['log_Z']:.3f}\n"
            f"  T23 B (no IMFP):   log Z = {B['log_Z']:.3f}\n"
            f"  IMFP correction effect: {delta_A_B:+.3f}\n"
            f"  Verdict: {imfp_verdict}\n"
            f"Compare to T20 placeholder log Z = -5.47 and T22 (no sigma_at_v) values."
        ),
    }
    out_path = RESULTS_DIR_V03 / "t23_real_kiss_sidm_two_comp_imfp.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, default=str))
    win_path = Path("/mnt/c/Users/lamkuenai/projects/dm-sidm-pipeline/v0.3-prelim/data/results/t23_real_kiss_sidm_two_comp_imfp.json")
    win_path.write_text(json.dumps(out, indent=2, default=str))
    print(f"\noutput -> {out_path}")
    print(f"        -> {win_path}")


if __name__ == "__main__":
    main()