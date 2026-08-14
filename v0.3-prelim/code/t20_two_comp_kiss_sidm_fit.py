"""
TIER 3: KISS-SIDM corrected 2-component fit.

Combines:
- TIER 1: KISS-SIDM IMFP correction (factor 0.778 in IMFP)
- TIER 2: real Yang+ 2026 published sigma_eff vs V_max curve

The physical insight: the KISS-SIDM correction applies to the gravothermal
collapse rate. In 2-component SIDM with mass segregation, the LIGHT
component (which dominates the cluster regime) has its OWN gravothermal
collapse, and the IMFP correction might apply to it differently than to
the heavy component (which dominates the dwarf regime).

This is a NOVEL analysis. The KISS-SIDM paper (Gurian & May 2025) only
considered single-component SIDM. We are extending it to the multi-
component case, with the simplification that the correction applies to
BOTH components (same Reg 3: IMFP at any sigma/m is corrected the same way).

If the KISS-SIDM correction applies to BOTH components uniformly, the
effect on the 2-comp posterior is to RELAX the gravothermal penalty at
high sigma_m (where IMFP regime is active), which would favor LARGER
sigma_eff at cluster scale. This could shift the cluster posterior
toward higher values.
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
import gravothermal as gth

from config import RESULTS_DIR_V03


# Same prior box as t18/t19
LOG_SIGMA1_RANGE = (-2.0, 2.0)
LOG_SIGMA2_RANGE = (-3.0, 1.0)
F1_RANGE = (0.01, 0.99)
A_RANGE = (-2.0, 2.0)

NLIVE = 200
DLOGZ = 0.1

# Reference halo (same as t17) for the KISS-SIDM correction
HALO_RHO_S = 1e7      # M_sun / kpc^3
HALO_R_S = 10.0       # kpc
HALO_V_MAX = 100.0    # km/s
HALO_T_GYR = 10.0     # Gyr


def kiss_sidm_correction_at_sigma(sigma_m: float, v_scale: float = 100.0) -> float:
    """KISS-SIDM correction factor at a given sigma/m and velocity scale.

    Uses the reference halo. The correction is in [0.778, 1.0]:
    - 1.0 in LMFP (Kn > 10) or SMFP (Kn < 0.1)
    - 0.778 in IMFP (0.1 < Kn < 10)
    """
    Kn = kss.knudsen_number(HALO_RHO_S, v_scale, sigma_m)
    return kss.knudsen_correction_factor(Kn, Kn_threshold=1.0)


def gravothermal_penalty_with_kiss(sigma_m: float, correction: float) -> float:
    """Per-halo gravothermal penalty, scaled by the KISS-SIDM correction.

    The fluid penalty is -log(r_core / r_max). The KISS-SIDM correction
    reduces this in IMFP (correction < 1.0).
    """
    sigma_m = float(sigma_m)
    if sigma_m <= 0:
        return 0.0
    r_core = gth.gravothermal_r_core(
        sigma_m, rho_s=HALO_RHO_S, r_s=HALO_R_S,
        v_max=HALO_V_MAX, t_Gyr=HALO_T_GYR,
    )
    if r_core <= 0:
        return 0.0
    r_max = 0.045 * HALO_R_S
    ratio = r_core / r_max
    if ratio <= 0:
        return 0.0
    fluid_pen = -np.log(ratio)
    return fluid_pen * correction


def loglike_two_comp_kiss_corrected(theta):
    """2-comp fit with KISS-SIDM IMFP correction applied to BOTH components.

    The correction reduces the gravothermal collapse penalty in the IMFP
    regime, which has the effect of allowing LARGER sigma_eff at cluster
    scale (where IMFP is most active).
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

    # KISS-SIDM IMFP correction as a soft prior
    # At each component's sigma_m at the reference velocity, compute the
    # correction factor and apply it to the gravothermal penalty.
    # We weight by f1 (heavy) and 1-f1 (light) since the IMFP applies to
    # the gravothermal collapse of each component.
    sigma1_v_ref = tc.sigma_at_v(sigma1, a, 100.0)
    sigma2_v_ref = tc.sigma_at_v(sigma2, a, 100.0)
    corr1 = kiss_sidm_correction_at_sigma(sigma1_v_ref, v_scale=100.0)
    corr2 = kiss_sidm_correction_at_sigma(sigma2_v_ref, v_scale=100.0)
    pen1 = gravothermal_penalty_with_kiss(sigma1_v_ref, corr1)
    pen2 = gravothermal_penalty_with_kiss(sigma2_v_ref, corr2)
    # Weighted by mass fraction
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
    print("T20 — TIER 3: 2-comp SIDM with KISS-SIDM IMFP correction")
    print("=" * 80)
    print(f"Reference halo: rho_s={HALO_RHO_S} M_sun/kpc^3, r_s={HALO_R_S} kpc,")
    print(f"                v_max={HALO_V_MAX} km/s, t={HALO_T_GYR} Gyr")
    print(f"Implements: 2-comp SIDM (sigma1, sigma2, f1, a) + Yang+ 2026 real curve")
    print(f"             + KISS-SIDM IMFP correction (gravothermal penalty relaxation)")
    print()

    print("Running T20: 2-comp with KISS-SIDM correction...")
    A = run_one(loglike_two_comp_kiss_corrected, prior_transform_4, 4, "two_comp_kiss")
    print(f"  log Z = {A['log_Z']:.3f} +/- {A['log_Z_err']:.3f}  (wall {A['wall_seconds']:.1f}s)")

    # Compare to T19 (no KISS-SIDM correction)
    t19 = json.load(open(RESULTS_DIR_V03 / "t19_yang2026_real_fit.json"))
    t19_logZ = t19["fit_A_2comp"]["log_Z"]
    delta = A["log_Z"] - t19_logZ
    print(f"  T19 (no KISS-SIDM) log Z = {t19_logZ:.3f}")
    print(f"  delta log Z (T20 - T19) = {delta:+.3f}")

    # MAP analysis
    log_s1, log_s2, f1_MAP, a_MAP = A["MAP"]
    s1_MAP = 10 ** log_s1
    s2_MAP = 10 ** log_s2
    sigma_eff_dwarf_MAP = tc.sigma_eff_dwarf(s1_MAP, s2_MAP, f1_MAP, a_MAP)
    sigma_eff_galaxy_MAP = tc.sigma_eff_galaxy(s1_MAP, s2_MAP, f1_MAP, a_MAP)
    sigma_eff_cluster_MAP = tc.sigma_eff_cluster(s1_MAP, s2_MAP, f1_MAP, a_MAP)

    print()
    print("T20 (with KISS-SIDM) MAP analysis:")
    print(f"  sigma1 = {s1_MAP:.4f} cm^2/g, sigma2 = {s2_MAP:.4f} cm^2/g")
    print(f"  f1 = {f1_MAP:.4f}, a = {a_MAP:.4f}")
    print(f"  sigma1/sigma2 = {s1_MAP/s2_MAP:.2f}")
    print(f"  sigma_eff(V_DWARF) = {sigma_eff_dwarf_MAP:.3f}  (Yang+ target: {yl.sigma_eff_yang2026(yl.V_DWARF):.3f})")
    print(f"  sigma_eff(V_GALAXY)= {sigma_eff_galaxy_MAP:.3f}  (Yang+ target: {yl.sigma_eff_yang2026(yl.V_GALAXY):.3f})")
    print(f"  sigma_eff(V_CLUSTER)= {sigma_eff_cluster_MAP:.3f}  (Yang+ target: {yl.sigma_eff_yang2026(yl.V_CLUSTER):.3f})")
    print(f"  dwarf/cluster contrast = {sigma_eff_dwarf_MAP/max(sigma_eff_cluster_MAP, 1e-9):.1f}")

    # Save
    out = {
        "test": "T20_two_comp_kiss_sidm_corrected",
        "direction": "TIER 3: KISS-SIDM IMFP correction applied to 2-comp SIDM",
        "reference_halo": {
            "rho_s": HALO_RHO_S, "r_s": HALO_R_S, "v_max": HALO_V_MAX, "t_Gyr": HALO_T_GYR,
        },
        "kiss_sidm_correction_formula": "correction = 0.778 in IMFP, 1.0 outside; weighted by f1",
        "fit_T20_with_kiss_sidm": A,
        "T19_no_kiss_baseline": t19["fit_A_2comp"],
        "delta_log_Z_T20_vs_T19": delta,
        "T20_MAP_analysis": {
            "sigma1": s1_MAP, "sigma2": s2_MAP, "f1": f1_MAP, "a": a_MAP,
            "sigma1_over_sigma2": s1_MAP / s2_MAP,
            "sigma_eff_dwarf": sigma_eff_dwarf_MAP,
            "sigma_eff_galaxy": sigma_eff_galaxy_MAP,
            "sigma_eff_cluster": sigma_eff_cluster_MAP,
            "dwarf_over_cluster_contrast": sigma_eff_dwarf_MAP / max(sigma_eff_cluster_MAP, 1e-9),
        },
        "verdict": (
            f"T20 (2-comp + KISS-SIDM IMFP correction) log Z = {A['log_Z']:.3f}; "
            f"T19 (2-comp, no correction) log Z = {t19_logZ:.3f}; "
            f"delta = {delta:+.3f}. "
            f"{'The KISS-SIDM correction IMPROVES the 2-comp fit' if delta > 0 else 'The KISS-SIDM correction is mildly disfavored (Occam)'}."
        ),
    }
    out_path = RESULTS_DIR_V03 / "t20_two_comp_kiss_sidm_fit.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2))
    print(f"\noutput -> {out_path}")


if __name__ == "__main__":
    main()
