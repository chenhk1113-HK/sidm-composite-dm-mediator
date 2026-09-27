"""T207b_long_emcee.py — Run emcee with chains long enough for 50τ convergence.

For each mode, target chain length such that L/τ > 50.
With τ ≈ 200-300, that means L = 10000-15000.
Strategy: run 32 walkers × 15000 steps (≈ 50τ for τ=300, ≥ 50τ for τ=200).

Reads DE results from t207_three_term_fit.json to initialize walkers near DE peak.
Saves to t207b_long_emcee.json.
"""
import sys
import json
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
import emcee

from two_component_three_term import (
    sigma_eff_three_term,
    f_H_prescription,
)
from T207_three_term_fit import (
    CHANNELS,
    log_likelihood_for_params as fit_log_likelihood,
    PARAM_NAMES,
    BOUNDS,
)


def log_probability(params, fixed_f_H=None, free_f_H=False):
    """Posterior = log_prior (bounds check) + log_likelihood."""
    # Bounds check (log prior)
    for i, (low, high) in enumerate(BOUNDS):
        if not (low <= params[i] <= high):
            return -np.inf
    if fixed_f_H is not None:
        f_H_cf_fixed = fixed_f_H.get('f_H_cf')
        f_H_cc_fixed = fixed_f_H.get('f_H_cc')
    else:
        f_H_cf_fixed = None
        f_H_cc_fixed = None
    ll = fit_log_likelihood(params, f_H_cf_fixed=f_H_cf_fixed,
                             f_H_cc_fixed=f_H_cc_fixed)
    if not np.isfinite(ll):
        return -np.inf
    return ll


def run_emcee_mode(mode_name, de_params, de_log_L, n_walkers=32, n_steps=15000,
                   seed_offset=0):
    """Run emcee for a single mode."""
    rng = np.random.default_rng(42 + seed_offset)
    fixed_f_H = None if mode_name == 'free_f_H' else f_H_prescription(mode_name)
    free_f_H = (mode_name == 'free_f_H')

    # Initialize walkers near DE best-fit
    n_dim = len(PARAM_NAMES)
    if de_params is None:
        # Default init
        de_params = np.array([0.05, 100.0, 0.05, 0.5, 100.0, 0.001, 1.0, 0.7, 0.3])

    init = np.zeros((n_walkers, n_dim))
    for i in range(n_walkers):
        init[i] = de_params * (1 + 0.05 * rng.standard_normal(n_dim))

    sampler = emcee.EnsembleSampler(n_walkers, n_dim, log_probability,
                                     args=(fixed_f_H, free_f_H))

    print(f'\n=== emcee: {mode_name} ({n_walkers} walkers × {n_steps} steps) ===')
    t0 = time.time()
    sampler.run_mcmc(init, n_steps, progress=False)
    elapsed = time.time() - t0
    print(f'  Elapsed: {elapsed:.1f} s')

    chain = sampler.get_chain()
    acceptance = np.mean(sampler.acceptance_fraction)
    print(f'  Acceptance: {acceptance:.3f}')

    # Compute integrated autocorrelation time
    try:
        tau = emcee.autocorr.integrated_time(sampler.get_chain(), quiet=True)
        # Flat posterior medians from second half of chain
        flat = sampler.get_chain(discard=n_steps // 4, flat=True)
        medians = np.median(flat, axis=0)
        stds = np.std(flat, axis=0)
        q16 = np.percentile(flat, 16, axis=0)
        q84 = np.percentile(flat, 84, axis=0)

        # Convergence: chain length > 50 × tau
        max_tau = np.max(tau)
        n_steps_50tau = int(50 * max_tau)
        converged = (n_steps > n_steps_50tau)
        print(f'  Max τ: {max_tau:.1f}, n_steps: {n_steps}, n_50τ: {n_steps_50tau}')
        print(f'  Converged (50τ criterion): {converged}')
    except Exception as e:
        print(f'  Autocorr failed: {e}')
        tau = None
        medians = np.full(n_dim, np.nan)
        stds = np.full(n_dim, np.nan)
        q16 = np.full(n_dim, np.nan)
        q84 = np.full(n_dim, np.nan)
        converged = False

    # Per-channel log L at posterior median
    if fixed_f_H is not None:
        f_H_cf_fixed = fixed_f_H.get('f_H_cf')
        f_H_cc_fixed = fixed_f_H.get('f_H_cc')
    else:
        f_H_cf_fixed = None
        f_H_cc_fixed = None
    ll_at_median = fit_log_likelihood(medians, f_H_cf_fixed=f_H_cf_fixed,
                                       f_H_cc_fixed=f_H_cc_fixed)

    result = {
        'mode': mode_name,
        'n_walkers': n_walkers,
        'n_steps': n_steps,
        'elapsed_s': elapsed,
        'acceptance': acceptance,
        'converged_50tau': bool(converged),
        'autocorr_times': tau.tolist() if tau is not None else None,
        'posterior_medians': dict(zip(PARAM_NAMES, medians.tolist())),
        'posterior_stds': dict(zip(PARAM_NAMES, stds.tolist())),
        'posterior_q16': dict(zip(PARAM_NAMES, q16.tolist())),
        'posterior_q84': dict(zip(PARAM_NAMES, q84.tolist())),
        'log_L_at_median': ll_at_median,
    }
    return result


def main():
    # Read DE results
    de_path = Path(r'C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\t207_three_term_fit.json')
    de = json.loads(de_path.read_text())

    PARAM_ORDER = ['sigma_0', 'sigma_peak_HH_1', 'sigma_0_HL', 'sigma_peak_HL',
                   'v_HL', 'sigma_0_LL', 'a_slope', 'f_H_cf', 'f_H_cc']

    results = {}
    for mode in ['borrowed', 'yang', 't202', 'free_f_H']:
        if mode in de:
            de_params_dict = de[mode].get('best_params', {})
            de_params = np.array([de_params_dict.get(p, 0.0) for p in PARAM_ORDER])
            de_log_L = de[mode].get('log_L_peak', None)
        else:
            de_params = None
            de_log_L = None
        results[mode] = run_emcee_mode(mode, de_params, de_log_L)

    out_path = Path(r'C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\t207b_long_emcee.json')
    out_path.write_text(json.dumps(results, indent=2))
    print(f'\nSaved: {out_path} size={out_path.stat().st_size}B')


if __name__ == '__main__':
    main()
