"""
T95 Option 3.6 — Master Yukawa + Zhang+ 2025 GD-1 perturber constraint.

PURPOSE
=======
Replace the existing Channel 27 (Euclid Q1 sub-halo FORECAST)
with a real published MEASUREMENT: Zhang, Yu, Yang, Nadler
2025 (ApJL 978, L23), "The GD-1 Stellar Stream Perturber as a
Core-collapsed Self-interacting Dark Matter Halo".

KEY FINDING FROM ZHANG+ 2025:
  For SIDM to explain the GD-1 stream's gap+spur features,
  the perturber must be a CORE-COLLAPSED SIDM subhalo. The
  paper's N-body simulations find that for
  sigma/m ~ 30-100 cm^2/g at v_max ~ 10 km/s,
  the enclosed mass within 10 pc of the perturber is increased
  by >1 order of magnitude compared to CDM, matching the
  Bonaca+ 2019 high-density requirement.

THIS SCRIPT:
  1. For each 7D posterior sample, compute master's
     sigma/m at v=10 km/s (the sub-halo inner velocity
     scale).
  2. Compare to Zhang+ 2025's required range
     [30, 100] cm^2/g.
  3. Compute a soft-box likelihood: logL=0 if in range,
     logL=-k*(deviation from boundary) if outside.
  4. Re-run the 8D fit (7D + Zhang constraint) and report
     the new Delta log Z.

This is the bok doc's actual suggestion, simplified to
use Zhang+ 2025's published constraint directly rather
than re-deriving the GD-1 likelihood from Gaia data.

REFERENCES
==========
- Zhang, X., Yu, H.-B., Yang, D., Nadler, E. 2025, ApJL 978,
  L23, "The GD-1 Stellar Stream Perturber as a Core-collapsed
  Self-interacting Dark Matter Halo"
  (doi: 10.3847/2041-8213/ada02b)
- Bonaca, A. et al. 2019, ApJ 880, 38 (original GD-1
  perturber high-density argument)
- Erkal, D. et al. 2016, MNRAS 463, 102 (stream-gap
  formalism for sub-halo impacts)
- T95 Option 3.5 (real 8D fit with Channel 27) for context
"""

import json
import os
import sys
import time
from pathlib import Path

import numpy as np

# Make t41 importable
_THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_THIS_DIR))

import t41_mediator_mass_joint_fit as t41
from t40_yukawa_sigma_m import sigma_m_cm2_per_g

from dynesty import NestedSampler


# Zhang+ 2025: SIDM to explain GD-1 requires
# sigma/m ~ 30-100 cm^2/g at v_max ~ 10 km/s
# (the inner velocity scale of the sub-halo)
ZHANG_2025_VMAX_KMS = 10.0  # sub-halo inner velocity
ZHANG_2025_SIGMA_M_LOWER = 30.0   # cm^2/g
ZHANG_2025_SIGMA_M_UPPER = 100.0  # cm^2/g
# Soft-edge width (log-space): likelihood drops smoothly
# outside the box over this range
ZHANG_2025_SOFT_EDGE_LOG = 0.3  # ~factor 2 in linear space


def loglike_zhang_gd1_perturber(theta):
    """
    Zhang+ 2025 GD-1 perturber constraint as a likelihood.

    For the 7D parameter theta, compute master's sigma/m at
    v=10 km/s (sub-halo inner velocity scale). Soft-box
    likelihood: logL=0 if sigma/m in [30, 100] cm^2/g,
    logL=-((log sigma/m - log boundary)/soft_edge)^2
    otherwise.
    """
    if len(theta) != 7:
        raise ValueError(f"loglike_zhang expects 7-D theta, got {len(theta)}")
    m_phi_MeV = 10 ** theta[0]
    m_chi_GeV = 10 ** theta[1]
    g_chi = theta[2]
    sigma_m_at_v10 = sigma_m_cm2_per_g(ZHANG_2025_VMAX_KMS, m_phi_MeV,
                                          m_chi_GeV, g_chi)
    if sigma_m_at_v10 <= 0:
        return -np.inf
    log_sigma = np.log10(sigma_m_at_v10)
    log_lower = np.log10(ZHANG_2025_SIGMA_M_LOWER)
    log_upper = np.log10(ZHANG_2025_SIGMA_M_UPPER)
    if log_lower <= log_sigma <= log_upper:
        return 0.0
    # Soft falloff outside the box
    if log_sigma < log_lower:
        deviation = (log_lower - log_sigma) / ZHANG_2025_SOFT_EDGE_LOG
    else:
        deviation = (log_sigma - log_upper) / ZHANG_2025_SOFT_EDGE_LOG
    # Quadratic penalty
    return -0.5 * deviation**2


def loglike_joint_7d_with_zhang(theta):
    """
    7D log-likelihood + Zhang+ 2025 GD-1 perturber constraint.
    """
    if len(theta) != 7:
        raise ValueError(f"loglike_joint_7d_with_zhang expects 7-D theta, got {len(theta)}")
    log_mu_x = theta[6]
    mu_x = 10.0 ** log_mu_x
    os.environ["T90_MAGNETIC_MOMENT_MU_X"] = repr(mu_x)
    try:
        ll_7d = t41.loglike_joint(theta[:6])
    finally:
        os.environ.pop("T90_MAGNETIC_MOMENT_MU_X", None)
    ll_zhang = loglike_zhang_gd1_perturber(theta)
    return ll_7d + ll_zhang


def main():
    print("=" * 80)
    print("T41 v0.9 — 8D model comparison (7D + Zhang+ 2025 GD-1 constraint)")
    print("=" * 80)
    print()
    print("Reference: Zhang, Yu, Yang, Nadler 2025, ApJL 978, L23")
    print("  'The GD-1 Stellar Stream Perturber as a Core-collapsed")
    print("   Self-interacting Dark Matter Halo'")
    print()
    print("Constraint:")
    print(f"  sigma/m at v_max = {ZHANG_2025_VMAX_KMS} km/s in "
          f"[{ZHANG_2025_SIGMA_M_LOWER:.0f}, {ZHANG_2025_SIGMA_M_UPPER:.0f}] cm^2/g")
    print(f"  Soft-edge width: {ZHANG_2025_SOFT_EDGE_LOG} dex in log space")
    print()
    print("Model comparison:")
    print("  7D: T41 v0.6 + Channel 26 magnetic-moment (T90.1)")
    print("  8D: 7D + Zhang+ 2025 GD-1 perturber constraint")
    print()

    nlive = 200
    ndim = 7
    print(f"Running 8D nested sampling with nlive={nlive}, ndim={ndim}...")
    from t41_v07_magnetic_moment_7d import prior_transform_7

    t0 = time.time()
    sampler = NestedSampler(
        loglike_joint_7d_with_zhang,
        prior_transform_7,
        ndim=ndim,
        nlive=nlive,
        bound='multi',
    )
    sampler.run_nested(dlogz=0.5)
    res = sampler.results
    wall_time = time.time() - t0
    print(f"Wall time: {wall_time:.1f} sec")
    print()

    log_Z_8D = float(res.logz[-1])
    log_Z_8D_err = float(res.logzerr[-1])
    print(f"log Z (8D, with Zhang constraint) = {log_Z_8D:.3f} ± {log_Z_8D_err:.3f}")

    log_Z_7D = -164.959
    log_Z_7D_err = 0.247
    delta_logZ = log_Z_8D - log_Z_7D
    print(f"log Z (7D, T90.1) = {log_Z_7D:.3f} ± {log_Z_7D_err:.3f}")
    print(f"Delta log Z (8D - 7D) = {delta_logZ:.3f}")
    print()

    if abs(delta_logZ) < 1.0:
        jeffreys = "barely worth mentioning"
    elif abs(delta_logZ) < 3.0:
        jeffreys = "substantial"
    elif abs(delta_logZ) < 5.0:
        jeffreys = "strong"
    else:
        jeffreys = "very strong"
    direction = "FAVORS 8D" if delta_logZ > 0 else "FAVORS 7D"
    print(f"Jeffreys verdict: {direction} ({jeffreys})")

    # Importance-sampled posterior
    samples_equal = res.samples
    log_w = res.logwt
    weights = np.exp(log_w - log_w.max())
    weights /= weights.sum()
    median_params = np.array([
        np.median(samples_equal[:, k]) for k in range(7)
    ])

    print()
    print("=" * 80)
    print("8D posterior medians (with Zhang constraint)")
    print("=" * 80)
    labels = ["log_m_phi_MeV", "log_m_chi_GeV", "g_chi", "log_epsilon",
              "log_alpha", "log_xi", "log_mu_x"]
    for label, med in zip(labels, median_params):
        print(f"  {label:>20s} = {med:.4f}")

    # Compute median sigma/m at v=10 km/s
    print()
    print("=" * 80)
    print("Master Yukawa sigma/m at v=10 km/s (Zhang scale)")
    print("=" * 80)
    sigma_m_v10_arr = np.array([
        sigma_m_cm2_per_g(ZHANG_2025_VMAX_KMS, 10 ** samples_equal[i, 0],
                            10 ** samples_equal[i, 1], samples_equal[i, 2])
        for i in range(samples_equal.shape[0])
    ])

    def weighted_quantile(arr, weights, q):
        idx_sorted = np.argsort(arr)
        sorted_arr = arr[idx_sorted]
        sorted_w = weights[idx_sorted]
        cum_w = np.cumsum(sorted_w)
        cum_w /= cum_w[-1]
        return float(np.interp(q, cum_w, sorted_arr))

    print(f"  weighted median: {weighted_quantile(sigma_m_v10_arr, weights, 0.5):.3e} cm^2/g")
    print(f"  16-84 percentile: "
          f"{weighted_quantile(sigma_m_v10_arr, weights, 0.16):.3e} to "
          f"{weighted_quantile(sigma_m_v10_arr, weights, 0.84):.3e} cm^2/g")
    print()
    print(f"  Zhang+ 2025 required range: "
          f"[{ZHANG_2025_SIGMA_M_LOWER:.0f}, {ZHANG_2025_SIGMA_M_UPPER:.0f}] cm^2/g")
    median_sm = weighted_quantile(sigma_m_v10_arr, weights, 0.5)
    if median_sm < ZHANG_2025_SIGMA_M_LOWER:
        print(f"  Master Yukawa median is {ZHANG_2025_SIGMA_M_LOWER/median_sm:.0f}x BELOW the Zhang range")
    elif median_sm > ZHANG_2025_SIGMA_M_UPPER:
        print(f"  Master Yukawa median is {median_sm/ZHANG_2025_SIGMA_M_UPPER:.0f}x ABOVE the Zhang range")
    else:
        print(f"  Master Yukawa median is within the Zhang range")
    print()

    # Save results
    out_dir = _THIS_DIR.parent / "outputs" / "t95"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_json = out_dir / "option3_6_zhang_gd1_results.json"
    summary = {
        "phase": "T95 Option 3.6",
        "task": "Master Yukawa + Zhang+ 2025 GD-1 perturber constraint",
        "reference": ("Zhang, X., Yu, H.-B., Yang, D., Nadler, E. 2025, "
                       "ApJL 978, L23. doi: 10.3847/2041-8213/ada02b"),
        "constraint": {
            "v_max_kms": ZHANG_2025_VMAX_KMS,
            "sigma_m_lower_cm2_per_g": ZHANG_2025_SIGMA_M_LOWER,
            "sigma_m_upper_cm2_per_g": ZHANG_2025_SIGMA_M_UPPER,
            "soft_edge_log": ZHANG_2025_SOFT_EDGE_LOG,
        },
        "model_comparison": {
            "log_Z_7D": log_Z_7D,
            "log_Z_7D_err": log_Z_7D_err,
            "log_Z_8D": log_Z_8D,
            "log_Z_8D_err": log_Z_8D_err,
            "delta_logZ": delta_logZ,
            "jeffreys_verdict": jeffreys,
            "direction": direction,
        },
        "wall_time_sec": wall_time,
        "posterior_medians": {
            label: float(med) for label, med in zip(labels, median_params)
        },
        "sigma_m_at_v10": {
            "weighted_median_cm2_per_g": weighted_quantile(sigma_m_v10_arr, weights, 0.5),
            "16-84_percentile": [
                weighted_quantile(sigma_m_v10_arr, weights, 0.16),
                weighted_quantile(sigma_m_v10_arr, weights, 0.84),
            ],
        },
        "comparison_to_option3_5": {
            "option3_5_channel27_delta_logZ": -1.57,
            "option3_6_zhang_delta_logZ": delta_logZ,
        },
        "caveats": [
            "Zhang+ 2025 uses N-body simulations; their sigma/m range is a model-dependent fit",
            "Soft-box likelihood with arbitrary soft-edge width (0.3 dex)",
            "Bounded by 7D posterior; no new dimensions added",
            "Master's 6D canonical fit and 7D T90.1 fit are unchanged",
        ],
    }
    with open(out_json, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Wrote: {out_json}")


if __name__ == "__main__":
    main()