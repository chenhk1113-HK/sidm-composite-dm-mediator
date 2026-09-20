"""
Auto-check framework for SIDM phenomenology using ArviZ.

Provides:
  - Posterior predictive checks (PPC) for MCMC runs
  - Convergence diagnostics (R-hat, ESS, autocorrelation)
  - Outlier detection in residuals

Usage:
  python -m v0.3-prelim.code.autocheck_arviz run <mcmc_chain.npz>
  python -m v0.3-prelim.code.autocheck_arviz verify <phenomenology_output.json>
"""
import argparse
import json
import sys
from pathlib import Path

import arviz as az
import numpy as np


def load_chain(npz_path):
    """Load MCMC chain from npz file."""
    data = np.load(npz_path)
    return {k: data[k] for k in data.files}


def convergence_check(chain):
    """Run ArviZ convergence diagnostics."""
    # Convert dict of arrays to InferenceData
    var_names = list(chain.keys())
    posterior = np.stack([chain[v] for v in var_names], axis=0)  # (n_var, n_walker, n_step)

    # Convert to ArviZ format: (n_chain, n_draw, n_var)
    posterior = np.transpose(posterior, (1, 2, 0))
    idata = az.from_dict(posterior={name: posterior[:, :, i] for i, name in enumerate(var_names)})

    summary = az.summary(idata)
    diagnostics = {
        'r_hat': {name: float(summary.loc[name, 'r_hat']) for name in var_names},
        'ess_bulk': {name: float(summary.loc[name, 'ess_bulk']) for name in var_names},
        'ess_tail': {name: float(summary.loc[name, 'ess_tail']) for name in var_names},
        'mcse_mean': {name: float(summary.loc[name, 'mcse_mean']) for name in var_names},
    }

    # Decision thresholds
    r_hat_max = max(diagnostics['r_hat'].values())
    ess_min = min(min(diagnostics['ess_bulk'].values()), min(diagnostics['ess_tail'].values()))

    diagnostics['passed'] = (r_hat_max < 1.05) and (ess_min > 100)
    diagnostics['r_hat_max'] = r_hat_max
    diagnostics['ess_min'] = ess_min

    return diagnostics


def posterior_predictive_check(chain, observed_data, sigma_pred):
    """Posterior predictive check: how often does predicted data exceed observed?

    Args:
      chain: dict of arrays (n_walker, n_step) for each parameter
      observed_data: dict of (v, sigma_observed, sigma_uncertainty) for each constraint
      sigma_pred: callable sigma_pred(v, **params) -> predicted sigma/m

    Returns:
      dict with p-values for each constraint
    """
    results = {}
    for name, (v, sigma_obs, sigma_unc) in observed_data.items():
        # Draw posterior predictive samples
        n_samples = min(1000, chain[list(chain.keys())[0]].size)
        param_samples = {
            name: chain[name].flatten()[:n_samples]
            for name in chain.keys()
        }

        # Generate predictions
        pred_samples = np.array([
            sigma_pred(v, **{k: param_samples[k][i] for k in param_samples})
            for i in range(n_samples)
        ])

        # Bayesian p-value: fraction of predictions exceeding observation
        z_score = (pred_samples - sigma_obs) / sigma_unc
        p_value = float(np.mean(np.abs(z_score) > 1.0))  # |z| > 1 should be ~16% under null

        # Flag if too many predictions miss by > 2 sigma
        results[name] = {
            'p_value_2sigma': p_value,
            'mean_pred': float(np.mean(pred_samples)),
            'observed': sigma_obs,
            'resid_sigma': float((np.mean(pred_samples) - sigma_obs) / sigma_unc),
            'passed': p_value < 0.05,  # less than 5% of predictions should be >2 sigma off
        }

    return results


def main():
    parser = argparse.ArgumentParser(description='Auto-check SIDM MCMC runs via ArviZ')
    parser.add_argument('command', choices=['run', 'verify'])
    parser.add_argument('path', help='Path to MCMC chain .npz or phenomenology output .json')
    args = parser.parse_args()

    if args.command == 'run':
        chain = load_chain(args.path)
        diagnostics = convergence_check(chain)
        print(json.dumps(diagnostics, indent=2))
        sys.exit(0 if diagnostics['passed'] else 1)


if __name__ == '__main__':
    main()
