"""T207c_extended_free_emcee.py — extended free_f_H emcee (50000 steps for 50τ convergence)."""
import sys
import json
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
import emcee

from T207_three_term_fit import (
    log_likelihood_for_params,
    PARAM_NAMES,
    BOUNDS,
)


def log_probability(params):
    """Posterior = bounds check + log_likelihood. Free fit: no f_H fixed."""
    for low, high in BOUNDS:
        if not (low <= params[BOUNDS.index((low, high))] <= high):
            return -np.inf
    # Direct loop to avoid re-index issue
    for i, (low, high) in enumerate(BOUNDS):
        if not (low <= params[i] <= high):
            return -np.inf
    ll = log_likelihood_for_params(params)
    if not np.isfinite(ll):
        return -np.inf
    return ll


def main():
    n_walkers = 32
    n_steps = 50000
    n_dim = len(PARAM_NAMES)

    # Read DE result for init
    de_path = Path(r'C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\t207_three_term_fit.json')
    de = json.loads(de_path.read_text())
    de_params_dict = de['free_f_H']['best_params']
    de_params = np.array([de_params_dict[p] for p in PARAM_NAMES])

    rng = np.random.default_rng(42)
    init = np.zeros((n_walkers, n_dim))
    for i in range(n_walkers):
        init[i] = de_params * (1 + 0.02 * rng.standard_normal(n_dim))
        # Clamp to bounds
        for j, (low, high) in enumerate(BOUNDS):
            init[i, j] = np.clip(init[i, j], low + 1e-6, high - 1e-6)

    sampler = emcee.EnsembleSampler(n_walkers, n_dim, log_probability)

    print(f'\n=== emcee: free_f_H EXTENDED ({n_walkers} walkers × {n_steps} steps) ===')
    t0 = time.time()
    sampler.run_mcmc(init, n_steps, progress=False)
    elapsed = time.time() - t0
    print(f'  Elapsed: {elapsed:.1f} s')

    chain = sampler.get_chain()
    acceptance = np.mean(sampler.acceptance_fraction)
    print(f'  Acceptance: {acceptance:.3f}')

    try:
        tau = emcee.autocorr.integrated_time(sampler.get_chain(), quiet=True)
        max_tau = float(np.max(tau))
        flat = sampler.get_chain(discard=n_steps // 4, flat=True)
        medians = np.median(flat, axis=0)
        stds = np.std(flat, axis=0)
        q16 = np.percentile(flat, 16, axis=0)
        q84 = np.percentile(flat, 84, axis=0)
        n_steps_50tau = int(50 * max_tau)
        converged = bool(n_steps > n_steps_50tau)
        print(f'  Max τ: {max_tau:.1f}, n_steps: {n_steps}, n_50τ: {n_steps_50tau}')
        print(f'  Converged (50τ criterion): {converged}')
        print(f'  Convergence ratio: {n_steps / n_steps_50tau:.2f}')
    except Exception as e:
        print(f'  Autocorr failed: {e}')
        tau = None
        medians = np.full(n_dim, np.nan)
        stds = np.full(n_dim, np.nan)
        q16 = np.full(n_dim, np.nan)
        q84 = np.full(n_dim, np.nan)
        max_tau = None
        converged = False

    ll_at_median = log_likelihood_for_params(medians)

    result = {
        'mode': 'free_f_H_extended',
        'n_walkers': n_walkers,
        'n_steps': n_steps,
        'elapsed_s': float(elapsed),
        'acceptance': float(acceptance),
        'converged_50tau': converged,
        'convergence_ratio_n_steps_over_50tau': float(n_steps / n_steps_50tau) if max_tau else None,
        'autocorr_times': tau.tolist() if tau is not None else None,
        'posterior_medians': dict(zip(PARAM_NAMES, medians.tolist())),
        'posterior_stds': dict(zip(PARAM_NAMES, stds.tolist())),
        'posterior_q16': dict(zip(PARAM_NAMES, q16.tolist())),
        'posterior_q84': dict(zip(PARAM_NAMES, q84.tolist())),
        'log_L_at_median': float(ll_at_median),
    }

    out_path = Path(r'C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\t207c_extended_free_emcee.json')
    out_path.write_text(json.dumps(result, indent=2))
    print(f'\nSaved: {out_path} size={out_path.stat().st_size}B')


if __name__ == '__main__':
    main()
