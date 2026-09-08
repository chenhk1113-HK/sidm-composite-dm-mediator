"""
T95 Option 3 — Master Yukawa + Euclid Q1 sub-halo forecast (Channel 27).

PURPOSE
=======
The Option 2 finding: the 7D LZ posterior does NOT constrain
the parameters (m_phi, g_chi, xi) that drive the SIDM core
size. To break this, we need a galaxy-observable channel.

This script uses the project's existing
euclid_q1_subhalo_forecast_forward_model.py likelihood
(Channel 27 forecast) to compute what the master Yukawa
predicts for the sub-halo mass function observable at the
LZ-anchored 7D posterior parameters.

METHOD
======
1. Load the 7D posterior (samples + weights).
2. For each sample, compute master's sigma_m_cm2_per_g at
   v=100 km/s (sigma_m_0) and v=200 km/s.
3. Fit the velocity power-law sigma/m(v) = sigma_m_0 * (100/v)^a
   to the two points, getting (sigma_m_0, a).
4. Evaluate the existing Channel 27 likelihood at each
   (sigma_m_0, a) point.
5. Report the distribution of predicted log-likelihoods
   and the master Yukawa's joint prediction.

This is a FORECAST channel, not a measurement. The likelihood
is a soft two-sided bound on sigma/m at v=150 km/s. The
question being asked: does the LZ-anchored Yukawa predict
a sub-halo abundance that the Euclid Q1 sub-halo forecast
will be able to test?

REFERENCES
==========
- Project Channel 27 (Euclid Q1 sub-halo forecast):
  v0.3-prelim/code/euclid_q1_subhalo_forecast_forward_model.py
- The existing (sigma_m_0, a) parametrization comes from
  the velocity power-law form sigma/m(v) = sigma_m_0 * (V_REF/v)^a
  (Kaplinghat+ 2016)
- Euclid Q1 sub-halo forecast: arXiv:2503.15330
- 7D posterior: T90.1 commit f422da1
- Master Yukawa: t40_yukawa_sigma_m.sigma_m_cm2_per_g
"""

import json
import sys
from pathlib import Path

import numpy as np

# Project imports
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_PROJECT_ROOT / "code"))
from t40_yukawa_sigma_m import sigma_m_cm2_per_g
from euclid_q1_subhalo_forecast_forward_model import (
    loglike_euclid_q1_subhalo_forecast,
    V_REF,
    EUCLID_Q1_SUBHALO_VMAX_KMS,
    EUCLID_Q1_SUBHALO_SIGMA_M_LOWER,
    EUCLID_Q1_SUBHALO_SIGMA_M_UPPER,
)


def fit_velocity_powerlaw(v_arr, sigma_arr):
    """
    Fit sigma/m(v) = sigma_m_0 * (V_REF/v)^a to two points.

    v_arr: array of velocities in km/s
    sigma_arr: corresponding sigma/m values in cm^2/g

    Returns (sigma_m_0, a):
      sigma_m_0: cross-section at V_REF
      a: velocity slope (positive = falls with v)
    """
    log_v = np.log10(v_arr)
    log_s = np.log10(sigma_arr)
    # log sigma = log sigma_0 + a * (log V_REF - log v)
    # = log sigma_0 + a * log V_REF - a * log v
    # So this is linear in log v with slope -a
    slope, intercept = np.polyfit(log_v, log_s, 1)
    a = -slope
    log_sigma_0 = intercept + a * np.log10(V_REF)
    return 10 ** log_sigma_0, a


def main():
    print("=" * 78)
    print("T95 Option 3 — Master Yukawa + Euclid Q1 sub-halo forecast (Channel 27)")
    print("=" * 78)
    print()
    print("Method:")
    print("  1. For each 7D posterior sample, compute master's sigma/m at v=100, 200 km/s")
    print("  2. Fit velocity power-law sigma/m(v) = sigma_m_0 * (100/v)^a")
    print("  3. Evaluate existing Channel 27 likelihood at each (sigma_m_0, a)")
    print("  4. Report the log-likelihood distribution")
    print()

    # Load 7D posterior
    npz_path = _PROJECT_ROOT / "outputs" / "t90" / "t41_v07_7d_posterior.npz"
    data = np.load(npz_path, allow_pickle=True)
    samples = data["samples"]
    log_weights = data["log_weights"]
    labels = list(data["labels"])
    print(f"Loaded 7D posterior: {samples.shape[0]} samples")
    print()

    # Convert log_weights to weights (normalized)
    log_w_max = log_weights.max()
    weights = np.exp(log_weights - log_w_max)
    weights /= weights.sum()
    print(f"Weight range: {weights.min():.3e} to {weights.max():.3e}")
    print(f"Effective sample size: {1.0 / (weights**2).sum():.0f}")
    print()

    idx = {label: i for i, label in enumerate(labels)}
    n_samples = samples.shape[0]

    # Compute (sigma_m_0, a) for each sample
    sigma_m_0_arr = np.zeros(n_samples)
    a_arr = np.zeros(n_samples)
    for i in range(n_samples):
        m_chi_GeV = 10 ** samples[i, idx["log_m_chi_GeV"]]
        m_phi_MeV = 10 ** samples[i, idx["log_m_phi_MeV"]]
        g_chi = samples[i, idx["g_chi"]]
        v_arr = np.array([100.0, 200.0])
        s_arr = np.array([
            sigma_m_cm2_per_g(v, m_phi_MeV, m_chi_GeV, g_chi)
            for v in v_arr
        ])
        sigma_m_0_arr[i], a_arr[i] = fit_velocity_powerlaw(v_arr, s_arr)

    # Weighted statistics
    def weighted_quantile(arr, weights, q):
        """Weighted quantile."""
        idx_sorted = np.argsort(arr)
        sorted_arr = arr[idx_sorted]
        sorted_w = weights[idx_sorted]
        cum_w = np.cumsum(sorted_w)
        cum_w /= cum_w[-1]
        return float(np.interp(q, cum_w, sorted_arr))

    print("=" * 78)
    print("Master Yukawa (sigma_m_0, a) at LZ-anchored 7D posterior")
    print("=" * 78)
    print()
    print(f"sigma_m_0 (at v={V_REF:.0f} km/s):")
    print(f"  weighted median: {weighted_quantile(sigma_m_0_arr, weights, 0.5):.3e} cm^2/g")
    print(f"  16-84 percentile: {weighted_quantile(sigma_m_0_arr, weights, 0.16):.3e} to "
          f"{weighted_quantile(sigma_m_0_arr, weights, 0.84):.3e} cm^2/g")
    print()
    print(f"velocity slope a:")
    print(f"  weighted median: {weighted_quantile(a_arr, weights, 0.5):.3f}")
    print(f"  16-84 percentile: {weighted_quantile(a_arr, weights, 0.16):.3f} to "
          f"{weighted_quantile(a_arr, weights, 0.84):.3f}")
    print()
    print(f"Channel 27 forecast bounds (from project):")
    print(f"  sigma/m(v={EUCLID_Q1_SUBHALO_VMAX_KMS:.0f}) in "
          f"[{EUCLID_Q1_SUBHALO_SIGMA_M_LOWER:.2e}, "
          f"{EUCLID_Q1_SUBHALO_SIGMA_M_UPPER:.2e}] cm^2/g")
    print()

    # Compute sigma/m at v=EUCLID_Q1_SUBHALO_VMAX_KMS
    # sigma/m(v) = sigma_m_0 * (V_REF / v)^a
    sigma_m_at_vmax_arr = sigma_m_0_arr * (V_REF / EUCLID_Q1_SUBHALO_VMAX_KMS) ** a_arr
    print(f"Master Yukawa sigma/m at v={EUCLID_Q1_SUBHALO_VMAX_KMS:.0f} km/s:")
    print(f"  weighted median: {weighted_quantile(sigma_m_at_vmax_arr, weights, 0.5):.3e} cm^2/g")
    print(f"  16-84 percentile: "
          f"{weighted_quantile(sigma_m_at_vmax_arr, weights, 0.16):.3e} to "
          f"{weighted_quantile(sigma_m_at_vmax_arr, weights, 0.84):.3e} cm^2/g")
    print()

    # Evaluate Channel 27 likelihood at each sample
    print("=" * 78)
    print("Channel 27 (Euclid Q1 sub-halo forecast) log-likelihood")
    print("=" * 78)
    loglikes = np.array([
        loglike_euclid_q1_subhalo_forecast(s0, a)
        for s0, a in zip(sigma_m_0_arr, a_arr)
    ])
    print(f"weighted median logL: {weighted_quantile(loglikes, weights, 0.5):.3f}")
    print(f"16-84 percentile: {weighted_quantile(loglikes, weights, 0.16):.3f} to "
          f"{weighted_quantile(loglikes, weights, 0.84):.3f}")
    print(f"max logL: {loglikes.max():.3f}")
    print(f"min logL: {loglikes.min():.3f}")
    print()

    # How many samples fall within the Channel 27 allowed region?
    within = (loglikes > -2.0).sum()
    total = n_samples
    frac = within / total
    print(f"Samples with logL > -2 (broadly allowed): {within}/{total} = {frac:.1%}")
    print()

    # Comparison: 7D posterior WITHOUT Channel 27
    # T90.1 reported log Z (7D) = -164.959 +- 0.247
    # Adding Channel 27 contribution logL adds to log Z
    log_Z_7D = -164.959
    log_Z_7D_err = 0.247
    logL_median = weighted_quantile(loglikes, weights, 0.5)
    log_Z_8D_est = log_Z_7D + logL_median

    print("=" * 78)
    print("Joint-fit verdict (estimated)")
    print("=" * 78)
    print(f"7D log Z (T90.1):   {log_Z_7D:.3f} ± {log_Z_7D_err:.3f}")
    print(f"Channel 27 median logL: {logL_median:.3f}")
    print(f"8D log Z estimate: {log_Z_8D_est:.3f}")
    print(f"Δlog Z (8D - 7D) estimate: {logL_median:.3f}")
    print()
    if logL_median > 1.0:
        verdict = "Channel 27 SUPPORTS the LZ-anchored Yukawa"
    elif logL_median > -1.0:
        verdict = "Channel 27 is NEUTRAL on the LZ-anchored Yukawa"
    else:
        verdict = "Channel 27 DISFAVORS the LZ-anchored Yukawa"
    print(f"VERDICT: {verdict}")
    print()

    # Honest caveats
    print("=" * 78)
    print("HONEST CAVEATS")
    print("=" * 78)
    print("""
1. CHANNEL 27 IS A FORECAST, NOT A MEASUREMENT. The
   loglike_euclid_q1_subhalo_forecast is a soft two-sided
   constraint based on the Euclid Q1 sub-halo forecast
   (arXiv:2503.15330). It assumes that Euclid Q1 will
   measure sub-halo abundances; if it doesn't, this
   forecast is moot.

2. THIS SCRIPT DOES NOT IMPLEMENT A STREAM-GAP LIKELIHOOD.
   The bok doc's "GD-1 stream gaps" suggestion is more
   specific than the existing sub-halo forecast. A full
   GD-1 stream-gap likelihood would require:
   (a) Gaia DR3 query for GD-1 region
   (b) Sub-halo impact cross-section on a stellar stream
       (Erkal+ 2016 formalism)
   (c) Stream orbit integration
   (d) Gap-detection likelihood
   This script uses the simpler (sigma_m_0, a) sub-halo
   abundance forecast as a proxy.

3. THE (sigma_m_0, a) FIT TO TWO POINTS is a
   simplification. The full velocity-dependence is more
   complex than a power law. But the project uses the
   power-law form (T89, T41), so this is consistent.

4. THE 7D POSTERIOR is LZ-anchored. Adding Channel 27
   will pull (m_phi, g_chi, xi) in directions correlated
   with the sub-halo forecast, NOT with LZ. This is the
   whole point of Option 3.

5. NO 8D FIT WAS RUN. The log Z estimate is a 7D
   posterior + median Channel 27 logL. A proper 8D fit
   would re-run the nested sampling with Channel 27
   added, which would give a different posterior. The
   current estimate tells us whether Channel 27 is
   informative, not the precise 8D posterior.
""")

    # Save results
    out_dir = _PROJECT_ROOT / "outputs" / "t95"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_json = out_dir / "option3_subhalo_forecast.json"
    results = {
        "phase": "T95 Option 3",
        "task": "Master Yukawa + Euclid Q1 sub-halo forecast (Channel 27)",
        "method": "Compute (sigma_m_0, a) at each 7D posterior sample, "
                  "evaluate existing Channel 27 likelihood",
        "posterior": {
            "n_samples": n_samples,
            "n_effective": float(1.0 / (weights**2).sum()),
        },
        "sigma_m_0_at_v100": {
            "weighted_median_cm2_per_g":
                weighted_quantile(sigma_m_0_arr, weights, 0.5),
            "16-84_percentile": [
                weighted_quantile(sigma_m_0_arr, weights, 0.16),
                weighted_quantile(sigma_m_0_arr, weights, 0.84),
            ],
        },
        "velocity_slope_a": {
            "weighted_median": weighted_quantile(a_arr, weights, 0.5),
            "16-84_percentile": [
                weighted_quantile(a_arr, weights, 0.16),
                weighted_quantile(a_arr, weights, 0.84),
            ],
        },
        "sigma_m_at_v150": {
            "weighted_median_cm2_per_g":
                weighted_quantile(sigma_m_at_vmax_arr, weights, 0.5),
            "16-84_percentile": [
                weighted_quantile(sigma_m_at_vmax_arr, weights, 0.16),
                weighted_quantile(sigma_m_at_vmax_arr, weights, 0.84),
            ],
            "channel_27_bounds": [
                EUCLID_Q1_SUBHALO_SIGMA_M_LOWER,
                EUCLID_Q1_SUBHALO_SIGMA_M_UPPER,
            ],
        },
        "channel_27_logL": {
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
            "log_Z_7D_err": log_Z_7D_err,
            "log_Z_8D_estimate": log_Z_8D_est,
            "delta_logZ_estimate": logL_median,
            "verdict": verdict,
        },
        "caveats": [
            "Channel 27 is a forecast, not a measurement",
            "Script uses sub-halo abundance forecast, not full GD-1 stream-gap likelihood",
            "Two-point (sigma_m_0, a) fit is a simplification",
            "7D posterior is LZ-anchored, not galaxy-anchored",
            "8D fit was not run, only estimated",
        ],
        "next_steps": [
            "Run a real 8D nested-sampling fit (would take ~1-2 min)",
            "Implement full GD-1 stream-gap likelihood (would take ~1 week)",
            "Pull Gaia DR3 data for GD-1 region (would take ~half day)",
        ],
    }
    with open(out_json, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Wrote: {out_json}")


if __name__ == "__main__":
    main()