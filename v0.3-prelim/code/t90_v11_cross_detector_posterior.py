"""
T90 Path C.4.1 — Integrate cross-detector predictor over the 7D posterior.

PURPOSE
=======
Extends t90_v10_cross_detector.py to integrate over the
full T90.1 7D posterior (2523 samples) instead of using
the central tuned value. Produces:

  - Median predicted N_events per detector with 16/84 percentile
  - Credible interval for the at-limit ratio
  - Joint verdict (consistency across the posterior, not
    just the MAP point)

OUTPUT
  - outputs/t90/cross_detector_posterior_predictive.json
  - Includes per-detector percentiles + Joint verdict

CONSTRAINTS
  - No new dependencies
  - Branch-local on wip/tier3-magnetic-moment-LZ

REFERENCE
  - t90_v10_cross_detector.py (the central-value predictor)
  - t41_v07_magnetic_moment_7d.py (the 7D posterior source)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

# Project imports
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_PROJECT_ROOT / "code"))
from t90_v10_cross_detector import (
    DETECTORS,
    predicted_events_for_detector,
)


def posterior_predictive_for_detector(
    samples: np.ndarray,
    detector: dict,
    n_max_samples: int = 500,
) -> dict:
    """Compute the posterior-predictive distribution of N_events
    for one detector, integrating over the 7D posterior.

    Args:
      samples: shape (N, 7) array of 7D posterior samples
        (log_m_phi_MeV, log_m_chi_GeV, g_chi, log_epsilon,
         log_alpha, log_xi, log_mu_x)
      detector: dict from DETECTORS
      n_max_samples: subsample to this many samples for speed

    Returns:
      dict with median, 16, 84 percentiles, plus the joint
      verdict (consistency across the posterior).
    """
    # Subsample if the posterior is too large (N=2523 is OK
    # but the WIMpy call is slow)
    if len(samples) > n_max_samples:
        idx = np.random.choice(len(samples), n_max_samples, replace=False)
        samples = samples[idx]

    log_mu_x = samples[:, 6]
    log_m_chi = samples[:, 1]
    mu_x_array = 10.0 ** log_mu_x
    m_chi_array = 10.0 ** log_m_chi

    # Compute N_predicted for each sample
    n_pred_array = np.zeros(len(samples))
    for i, (mu_x, m_chi) in enumerate(zip(mu_x_array, m_chi_array)):
        # Per-sample detector prediction
        # Note: This is slow because each call invokes WIMpy.
        # For 500 samples * 5 Xe detectors = 2500 WIMpy calls.
        result = predicted_events_for_detector(mu_x, m_chi, detector)
        n_pred_array[i] = result['N_predicted']

    median_n = float(np.median(n_pred_array))
    p16_n = float(np.percentile(n_pred_array, 16))
    p84_n = float(np.percentile(n_pred_array, 84))

    out = {
        'detector': detector['name'],
        'N_predicted_median': median_n,
        'N_predicted_16_84': [p16_n, p84_n],
        'N_samples_used': len(samples),
    }

    # If the detector has a published limit, also compute the
    # posterior predictive for the at-limit ratio.
    if detector.get('published_limit_mu_x') is not None:
        # Per-sample: what's the predicted / at-limit ratio?
        ratio_array = (mu_x_array / detector['published_limit_mu_x'])**2
        out['ratio_predicted_to_at_limit_median'] = float(np.median(ratio_array))
        out['ratio_predicted_to_at_limit_16_84'] = [
            float(np.percentile(ratio_array, 16)),
            float(np.percentile(ratio_array, 84)),
        ]
        # Joint verdict: what fraction of the posterior is
        # consistent with each verdict?
        median_ratio = out['ratio_predicted_to_at_limit_median']
        frac_below = float(np.mean(ratio_array < 1e-3))
        frac_near = float(np.mean((ratio_array >= 1e-3) & (ratio_array < 1)))
        frac_above = float(np.mean(ratio_array >= 1))
        out['fraction_much_below_limit'] = frac_below
        out['fraction_near_limit'] = frac_near
        out['fraction_at_or_above_limit'] = frac_above
        # Joint verdict: based on median
        if median_ratio < 1e-3:
            out['joint_verdict'] = 'much_below_limit'
        elif median_ratio < 1:
            out['joint_verdict'] = 'near_limit'
        else:
            out['joint_verdict'] = 'at_or_above_limit'

    return out


def load_7d_posterior(path: str) -> np.ndarray:
    """Load the T90 7D posterior samples. Returns shape (N, 7)."""
    npz = np.load(path, allow_pickle=True)
    return npz['samples']


def main():
    print("=" * 70)
    print("T90 Path C.4.1 — Posterior-predictive cross-detector")
    print("=" * 70)
    print()

    posterior_path = (
        _PROJECT_ROOT / "outputs" / "t90" / "t41_v07_7d_posterior.npz"
    )
    if not posterior_path.exists():
        print(f"ERROR: posterior not found at {posterior_path}")
        return

    samples = load_7d_posterior(str(posterior_path))
    print(f"Loaded {len(samples)} posterior samples from {posterior_path}")
    print()

    # Subsample to 500 for speed (WIMpy is slow)
    n_max = 500
    if len(samples) > n_max:
        rng = np.random.default_rng(42)  # reproducible
        idx = rng.choice(len(samples), n_max, replace=False)
        samples = samples[idx]
        print(f"Subsampled to {n_max} samples for speed")
        print()

    print(f"Per-detector posterior-predictive predictions:")
    print()

    results = {}
    for det_key, det_cfg in DETECTORS.items():
        result = posterior_predictive_for_detector(samples, det_cfg, n_max_samples=n_max)
        results[det_key] = result
        print(f"  {det_cfg['name']}:")
        print(f"    N_predicted median = {result['N_predicted_median']:.4e}")
        print(f"    N_predicted 16-84   = [{result['N_predicted_16_84'][0]:.4e}, {result['N_predicted_16_84'][1]:.4e}]")
        if 'ratio_predicted_to_at_limit_median' in result:
            print(f"    ratio median        = {result['ratio_predicted_to_at_limit_median']:.4e}")
            print(f"    ratio 16-84         = [{result['ratio_predicted_to_at_limit_16_84'][0]:.4e}, {result['ratio_predicted_to_at_limit_16_84'][1]:.4e}]")
            print(f"    joint_verdict       = {result['joint_verdict']}")
            print(f"    fraction_above      = {result['fraction_at_or_above_limit']:.3f}")
        print()

    out_path = _PROJECT_ROOT / "outputs" / "t90" / "cross_detector_posterior_predictive.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    output = {
        'phase': 'T90 Path C.4.1 (posterior predictive)',
        'posterior_source': str(posterior_path),
        'n_samples_total': int(len(samples)),
        'n_samples_used_per_detector': n_max,
        'detectors': results,
    }
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"Wrote: {out_path}")


if __name__ == '__main__':
    main()
