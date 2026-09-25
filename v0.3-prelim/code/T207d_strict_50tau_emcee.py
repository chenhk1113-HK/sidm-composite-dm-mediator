"""T207d_strict_50tau_emcee.py — strict 50τ convergence test for free_f_H emcee.

Runs 100,000 steps (slightly above 50τ=86,858 estimated at 50k) with 64 walkers
(double the previous run's 32 for better mixing) to test whether strict
convergence can be reached.

Estimated runtime: 100k × 64 × 3e-3 s = ~19000 s ≈ 5.3 hours.
"""
import sys
import json
import time
import warnings
from pathlib import Path

import numpy as np
warnings.filterwarnings('ignore', category=RuntimeWarning)
np.random.seed(42)

sys.path.insert(0, str(Path(__file__).parent))
from T207_three_term_fit import (
    CHANNELS, log_likelihood_for_params as fit_log_likelihood, PARAM_NAMES, BOUNDS
)

import emcee

# Load DE best-fit for init
de_path = Path(r'C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\t207_three_term_fit.json')
de_data = json.loads(de_path.read_text())
de_best = de_data['free_f_H']['best_params']

n_params = len(PARAM_NAMES)
n_walkers = 64
n_steps = 100_000

def log_probability(params):
    """Posterior = bounds check + log_likelihood."""
    for i, (low, high) in enumerate(BOUNDS):
        if not (low <= params[i] <= high):
            return -np.inf
    arr = [params[0], params[1], params[2], params[3], params[4], params[5], params[6]]
    fixed_f_H = {'f_H_cf': params[7], 'f_H_cc': params[8]}
    ll = fit_log_likelihood(arr, f_H_cf_fixed=params[7], f_H_cc_fixed=params[8])
    return ll

def main():
    start = time.time()
    print(f'=== emcee: free_f_H STRICT 50τ ({n_walkers} walkers × {n_steps} steps) ===')

    # Init at DE best-fit with small perturbation
    p0 = np.array([
        de_best['sigma_0'],
        de_best['sigma_peak_HH_1'],
        de_best['sigma_0_HL'],
        de_best['sigma_peak_HL'],
        de_best['v_HL'],
        de_best['sigma_0_LL'],
        de_best['a_slope'],
        de_best['f_H_cf'],
        de_best['f_H_cc'],
    ])
    pos = p0[None, :] + 0.01 * np.abs(p0[None, :]) * np.random.randn(n_walkers, n_params)

    sampler = emcee.EnsembleSampler(n_walkers, n_params, log_probability)
    sampler.run_mcmc(pos, n_steps, progress=False)

    elapsed = time.time() - start
    print(f'  Elapsed: {elapsed:.1f} s')

    # Get chain + autocorrelation
    chain = sampler.get_chain()
    print(f'  Acceptance: {np.mean(sampler.acceptance_fraction):.3f}')

    try:
        tau = sampler.get_autocorr_time(quiet=True)
        max_tau = float(np.max(tau))
        n_50tau = 50 * max_tau
        print(f'  Max τ: {max_tau:.1f}, n_steps: {n_steps}, n_50τ: {n_50tau:.0f}')
        converged = (n_steps > n_50tau)
        print(f'  Converged (50τ criterion): {converged}')
    except Exception as e:
        print(f'  autocorr failed: {e}')
        max_tau = -1
        n_50tau = -1
        converged = False

    # Posterior
    flat_chain = sampler.get_chain(discard=n_steps // 4, flat=True)
    medians = {n: float(np.median(flat_chain[:, i])) for i, n in enumerate(PARAM_NAMES)}
    stds = {n: float(np.std(flat_chain[:, i])) for i, n in enumerate(PARAM_NAMES)}
    p16 = {n: float(np.percentile(flat_chain[:, i], 16)) for i, n in enumerate(PARAM_NAMES)}
    p84 = {n: float(np.percentile(flat_chain[:, i], 84)) for i, n in enumerate(PARAM_NAMES)}

    # Save
    out = {
        'mode': 'free_f_H',
        'n_walkers': n_walkers,
        'n_steps': n_steps,
        'burn_in': n_steps // 4,
        'elapsed_s': elapsed,
        'acceptance': float(np.mean(sampler.acceptance_fraction)),
        'tau_max': max_tau,
        'tau_per_param': [float(t) for t in tau] if max_tau > 0 else None,
        'n_50tau': n_50tau,
        'converged_50tau': converged,
        'posterior_medians': medians,
        'posterior_stds': stds,
        'posterior_p16': p16,
        'posterior_p84': p84,
        'max_log_L': float(np.max(flat_chain[:, 0])),  # proxy
    }
    out_path = Path(r'C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\t207d_strict_50tau.json')
    out_path.write_text(json.dumps(out, indent=2))
    print(f'\nSaved: {out_path} size={out_path.stat().st_size}B')
    print(f'\nPosterior medians:')
    for n in PARAM_NAMES:
        print(f'  {n}: {medians[n]:.4f} ± {stds[n]:.4f}')

if __name__ == '__main__':
    main()