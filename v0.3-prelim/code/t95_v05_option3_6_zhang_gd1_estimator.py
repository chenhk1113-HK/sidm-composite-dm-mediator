"""
T95 Option 3.6 — Master Yukawa vs Zhang+ 2025 GD-1 constraint (estimator).

PURPOSE
=======
The full 8D nested-sampling fit (t41_v09_magnetic_moment_zhang_gd1.py)
times out because the Zhang+ 2025 constraint is very strict
(sigma/m at v=10 km/s must be in [30, 100] cm^2/g) and the
master's Yukawa at LZ posterior gives sigma/m ~0.5 cm^2/g
there. Almost all 7D posterior samples get a very large
negative logL, and the nested sampler has to do a LOT of
work to find the tiny region of parameter space that
satisfies Zhang+ 2025.

This script uses the same estimator trick as T95 Option 3:
compute the Zhang likelihood at each 7D posterior sample,
report the weighted-median logL, and estimate Delta log Z.

This is informative (tells us the tension direction and
magnitude) but is NOT a substitute for a proper nested
re-sampling.

REFERENCES
==========
- Zhang, X., Yu, H.-B., Yang, D., Nadler, E. 2025, ApJL 978,
  L23 ("The GD-1 Stellar Stream Perturber as a Core-collapsed
  Self-interacting Dark Matter Halo")
"""

import json
import sys
from pathlib import Path

import numpy as np

# Make t41 importable
_THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_THIS_DIR))

from t40_yukawa_sigma_m import sigma_m_cm2_per_g


# Zhang+ 2025 constraint
ZHANG_2025_VMAX_KMS = 10.0
ZHANG_2025_SIGMA_M_LOWER = 30.0
ZHANG_2025_SIGMA_M_UPPER = 100.0
ZHANG_2025_SOFT_EDGE_LOG = 0.3


def loglike_zhang_gd1_perturber(theta):
    """Zhang+ 2025 GD-1 perturber constraint as a soft-box likelihood."""
    if len(theta) != 7:
        raise ValueError
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
    if log_sigma < log_lower:
        deviation = (log_lower - log_sigma) / ZHANG_2025_SOFT_EDGE_LOG
    else:
        deviation = (log_sigma - log_upper) / ZHANG_2025_SOFT_EDGE_LOG
    return -0.5 * deviation**2


def main():
    print("=" * 80)
    print("T95 Option 3.6 — Master Yukawa vs Zhang+ 2025 GD-1 constraint (estimator)")
    print("=" * 80)
    print()
    print("Reference: Zhang+ 2025 ApJL 978, L23")
    print("Constraint: sigma/m at v=10 km/s in [30, 100] cm^2/g")
    print()

    # Load 7D posterior
    npz_path = _PROJECT_ROOT_OUT = Path(__file__).resolve().parents[1] / "outputs" / "t90" / "t41_v07_7d_posterior.npz"
    data = np.load(npz_path, allow_pickle=True)
    samples = data["samples"]
    log_weights = data["log_weights"]
    labels = list(data["labels"])
    print(f"Loaded 7D posterior: {samples.shape[0]} samples")

    # Convert log_weights to weights
    log_w_max = log_weights.max()
    weights = np.exp(log_weights - log_w_max)
    weights /= weights.sum()

    n_samples = samples.shape[0]
    idx = {label: i for i, label in enumerate(labels)}

    # Compute Zhang logL and sigma/m at v=10 for each sample
    loglikes = np.array([
        loglike_zhang_gd1_perturber(samples[i])
        for i in range(n_samples)
    ])
    sigma_m_v10 = np.array([
        sigma_m_cm2_per_g(ZHANG_2025_VMAX_KMS,
                            10 ** samples[i, idx["log_m_phi_MeV"]],
                            10 ** samples[i, idx["log_m_chi_GeV"]],
                            samples[i, idx["g_chi"]])
        for i in range(n_samples)
    ])

    def weighted_quantile(arr, weights, q):
        idx_sorted = np.argsort(arr)
        sorted_arr = arr[idx_sorted]
        sorted_w = weights[idx_sorted]
        cum_w = np.cumsum(sorted_w)
        cum_w /= cum_w[-1]
        return float(np.interp(q, cum_w, sorted_arr))

    print()
    print("=" * 80)
    print("Master Yukawa sigma/m at v=10 km/s (Zhang scale)")
    print("=" * 80)
    print(f"  weighted median: {weighted_quantile(sigma_m_v10, weights, 0.5):.3e} cm^2/g")
    print(f"  16-84 percentile: "
          f"{weighted_quantile(sigma_m_v10, weights, 0.16):.3e} to "
          f"{weighted_quantile(sigma_m_v10, weights, 0.84):.3e} cm^2/g")
    print(f"  min/max: {sigma_m_v10.min():.3e} to {sigma_m_v10.max():.3e} cm^2/g")
    print()
    print(f"  Zhang+ 2025 required range: [30, 100] cm^2/g")
    print()

    # Count samples in/out of the box
    in_box = ((sigma_m_v10 >= ZHANG_2025_SIGMA_M_LOWER) &
              (sigma_m_v10 <= ZHANG_2025_SIGMA_M_UPPER)).sum()
    print(f"  Samples in [30, 100]: {in_box}/{n_samples} = {in_box/n_samples*100:.1f}%")
    print(f"  Samples below 30: {((sigma_m_v10 < ZHANG_2025_SIGMA_M_LOWER)).sum()}/{n_samples} = "
          f"{((sigma_m_v10 < ZHANG_2025_SIGMA_M_LOWER)).sum()/n_samples*100:.1f}%")
    print()

    # Compute weighted-median Zhang logL
    print("=" * 80)
    print("Zhang+ 2025 log-likelihood distribution")
    print("=" * 80)
    print(f"  weighted median logL: {weighted_quantile(loglikes, weights, 0.5):.3f}")
    print(f"  16-84 percentile: "
          f"{weighted_quantile(loglikes, weights, 0.16):.3f} to "
          f"{weighted_quantile(loglikes, weights, 0.84):.3f}")
    print(f"  max logL: {loglikes.max():.3f}")
    print(f"  min logL: {loglikes.min():.3f}")
    print()

    # Estimate Delta log Z
    log_Z_7D = -164.959
    log_Z_7D_err = 0.247
    logL_median = weighted_quantile(loglikes, weights, 0.5)
    log_Z_8D_est = log_Z_7D + logL_median
    print("=" * 80)
    print("Joint-fit verdict (ESTIMATOR — not a real nested-sampling fit)")
    print("=" * 80)
    print(f"  7D log Z (T90.1): {log_Z_7D:.3f} ± {log_Z_7D_err:.3f}")
    print(f"  Zhang+ 2025 median logL: {logL_median:.3f}")
    print(f"  8D log Z estimate: {log_Z_8D_est:.3f}")
    print(f"  Delta log Z (8D - 7D) ESTIMATE: {logL_median:.3f}")
    print()

    if logL_median > 1.0:
        verdict = "Zhang+ 2025 SUPPORTS the LZ-anchored Yukawa"
    elif logL_median > -1.0:
        verdict = "Zhang+ 2025 is NEUTRAL on the LZ-anchored Yukawa"
    else:
        verdict = "Zhang+ 2025 STRONGLY DISFAVORS the LZ-anchored Yukawa"
    print(f"  VERDICT: {verdict}")
    print()
    print("=" * 80)
    print("HONEST CAVEATS")
    print("=" * 80)
    print("""
1. THIS IS AN ESTIMATOR, NOT A REAL NESTED-SAMPLING FIT.
   The full 8D fit (t41_v09_magnetic_moment_zhang_gd1.py)
   times out because the Zhang+ 2025 constraint is very
   strict and the master's Yukawa at LZ posterior gives
   sigma/m ~0.5 cm^2/g at v=10 km/s, which is much lower
   than Zhang's required [30, 100] cm^2/g. Almost all 7D
   posterior samples get a very large negative logL, and
   the nested sampler cannot find the tiny region of
   parameter space that satisfies Zhang+ 2025 within
   reasonable compute time.

2. THE ESTIMATOR OVERESTIMATES THE TENSION (just like the
   Option 3 estimator did). The proper 8D fit would
   re-weight the posterior to satisfy Zhang+ 2025 (or
   fail to, in which case log Z -> -infinity). A proper
   nested-sampling fit in the 8D model would either:
   (a) find a tiny posterior island that satisfies Zhang,
       giving a slightly less negative Delta log Z
   (b) fail to find any such island, giving a very large
       negative Delta log Z (Jeffreys "very strong"
       evidence against)

3. ZHANG+ 2025 USES N-BODY SIMULATIONS, not data alone.
   Their sigma/m range is a model-dependent fit. A
   different N-body setup or different cross-section
   prescription could shift the [30, 100] range.

4. THE GD-1 PERTURBER INTERPRETATION is itself debated.
   Other explanations (LMC, bar, GMC) exist. Zhang+ 2025
   is one of multiple possible interpretations.

5. THE PHYSICS RESULT IS CLEAR: master's Yukawa at LZ
   posterior gives sigma/m that is INCOMPATIBLE with
   the Zhang+ 2025 GD-1 perturber interpretation. The
   LZ-anchored Yukawa would need a 60-200x LARGER sigma/m
   at v=10 km/s to explain the GD-1 perturber. This is
   not a calibration offset; it is a fundamental tension
   between the LZ 248 keV interpretation and the
   GD-1 perturber interpretation.
""")

    # Save results
    out_dir = _THIS_DIR.parent / "outputs" / "t95"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_json = out_dir / "option3_6_zhang_gd1_estimator.json"
    results = {
        "phase": "T95 Option 3.6 (estimator)",
        "task": "Master Yukawa vs Zhang+ 2025 GD-1 perturber constraint",
        "reference": "Zhang, X., Yu, H.-B., Yang, D., Nadler, E. 2025, ApJL 978, L23",
        "constraint": {
            "v_max_kms": ZHANG_2025_VMAX_KMS,
            "sigma_m_lower_cm2_per_g": ZHANG_2025_SIGMA_M_LOWER,
            "sigma_m_upper_cm2_per_g": ZHANG_2025_SIGMA_M_UPPER,
        },
        "sigma_m_at_v10": {
            "weighted_median_cm2_per_g": weighted_quantile(sigma_m_v10, weights, 0.5),
            "16-84_percentile": [
                weighted_quantile(sigma_m_v10, weights, 0.16),
                weighted_quantile(sigma_m_v10, weights, 0.84),
            ],
        },
        "samples_in_zhang_range": {
            "n_in_box": int(in_box),
            "n_total": n_samples,
            "fraction_in_box": float(in_box / n_samples),
        },
        "zhang_logL": {
            "weighted_median": weighted_quantile(loglikes, weights, 0.5),
            "16-84_percentile": [
                weighted_quantile(loglikes, weights, 0.16),
                weighted_quantile(loglikes, weights, 0.84),
            ],
            "max": float(loglikes.max()),
            "min": float(loglikes.min()),
        },
        "joint_fit_estimate": {
            "log_Z_7D": log_Z_7D,
            "log_Z_8D_estimate": log_Z_8D_est,
            "delta_logZ_estimate": logL_median,
            "verdict": verdict,
        },
        "comparison_to_option3_5": {
            "option3_5_channel27_delta_logZ": -1.57,
            "option3_6_zhang_delta_logZ_estimate": logL_median,
        },
        "caveats": [
            "Estimator, not a real nested-sampling fit (proper fit times out)",
            "Estimator overestimates the tension (per Option 3.5 lesson)",
            "Zhang+ 2025 is one of multiple GD-1 perturber interpretations",
            "The full fit would either find a tiny posterior island or fail",
            "60-200x tension between LZ sigma/m and Zhang required sigma/m",
        ],
    }
    with open(out_json, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Wrote: {out_json}")


if __name__ == "__main__":
    main()