"""T207c_priored_free_emcee.py — 50k-step emcee for free_f_H with v18.38 prior.

Loads DE init from t207_priored_free_de.json (the v18.38-priored DE result).
Saves to t207c_priored_free_emcee.json.

Expected wall time: ~60-70 min.
"""
import sys
import json
import time
from pathlib import Path

sys.path.insert(0, r'C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\code')

import numpy as np
import emcee

from T207_three_term_fit import (
    log_likelihood_for_params, BOUNDS, PARAM_NAMES,
)


DE_PATH = Path(r'C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\t207_priored_free_de.json')
OUT_PATH = Path(r'C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\t207c_priored_free_emcee.json')


def log_probability(params):
    """Posterior = bounds check + log_likelihood. v18.38: f_H_cc >= 0.05 enforced via BOUNDS."""
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
    n_burn = 2000
    n_dim = len(PARAM_NAMES)

    # Load DE init from the v18.38-priored DE result
    de = json.loads(DE_PATH.read_text())
    de_params_dict = de['best_params']
    de_params = np.array([de_params_dict[p] for p in PARAM_NAMES])
    print(f"Loaded DE init from {DE_PATH}")
    print(f"  DE best_params.f_H_cc = {de_params_dict['f_H_cc']:.4f}")
    print(f"  DE best_params.v_HL = {de_params_dict['v_HL']:.2f} km/s")

    rng = np.random.default_rng(42)
    init = np.zeros((n_walkers, n_dim))
    for i in range(n_walkers):
        # Wider init (5% Gaussian) than original 2% to allow exploration of f_H_cc space
        init[i] = de_params * (1 + 0.05 * rng.standard_normal(n_dim))
        for j, (low, high) in enumerate(BOUNDS):
            init[i][j] = np.clip(init[i][j], low, high)

    # Affine invariant sampler
    sampler = emcee.EnsembleSampler(n_walkers, n_dim, log_probability)
    print(f"\nStarting emcee: {n_walkers} walkers x {n_steps} steps (burn-in {n_burn})")
    t0 = time.time()
    sampler.run_mcmc(init, n_steps, progress=False)
    elapsed = time.time() - t0

    # Drop burn-in, compute posterior stats
    chain = sampler.get_chain(discard=n_burn, flat=True)
    log_probs = sampler.get_log_prob(discard=n_burn, flat=True)
    log_L_at_median = float(log_probs[chain.shape[0] // 2])  # approx

    print(f"\nemcee elapsed: {elapsed:.1f} s")
    print(f"  total samples after burn-in: {chain.shape[0]}")
    print(f"  acceptance: {np.mean(sampler.acceptance_fraction):.4f}")
    try:
        tau = sampler.get_autocorr_time(quiet=True)
        tau_max = float(np.max(tau))
        # v18.38 FIX: convergence ratio is n_steps / (50 * tau_max), not n_steps / tau_max.
        # The variable name n_over_50tau means "n over 50 tau" — divide by 50*tau_max.
        n_over_50tau = n_steps / (50.0 * tau_max)
        print(f"  tau_max: {tau_max:.1f}, n/(50*tau) = {n_over_50tau:.3f}, converged_50tau = {n_over_50tau >= 1.0}")
    except Exception as e:
        print(f"  autocorrelation estimation failed: {e}")
        tau = None
        tau_max = None
        n_over_50tau = None

    # Per-parameter posterior statistics
    q16 = np.percentile(chain, 16, axis=0)
    q50 = np.percentile(chain, 50, axis=0)
    q84 = np.percentile(chain, 84, axis=0)
    medians = q50
    stds = 0.5 * (q84 - q16)

    posterior_medians = {p: float(medians[i]) for i, p in enumerate(PARAM_NAMES)}
    posterior_stds = {p: float(stds[i]) for i, p in enumerate(PARAM_NAMES)}
    posterior_q16 = {p: float(q16[i]) for i, p in enumerate(PARAM_NAMES)}
    posterior_q84 = {p: float(q84[i]) for i, p in enumerate(PARAM_NAMES)}

    # Per-channel log L at posterior median
    median_params = np.array([posterior_medians[p] for p in PARAM_NAMES])
    per_ch = log_likelihood_for_params(median_params, return_per_channel=True)

    out = {
        'metadata': {
            'description': 'free_f_H emcee with v18.38 prior (f_H_cc >= 0.05)',
            'n_walkers': n_walkers,
            'n_steps': n_steps,
            'n_burn': n_burn,
            'elapsed_s': elapsed,
            'init_source': str(DE_PATH),
        },
        'mode': 'free_f_H_priored',
        'posterior_medians': posterior_medians,
        'posterior_stds': posterior_stds,
        'posterior_q16': posterior_q16,
        'posterior_q84': posterior_q84,
        'per_channel_log_L_at_median': per_ch,
        'acceptance': float(np.mean(sampler.acceptance_fraction)),
        'autocorr_times': [float(t) for t in (tau if tau is not None else [None]*n_dim)],
        'tau_max': tau_max,
        # v18.38 FIX: convergence ratio is n_steps / (50 * tau_max), not n_steps / tau_max.
        # Variable name n_over_50tau means "n over 50 tau" — the original buggy code
        # computed n / tau_max instead. Corrected value below (re-derived from stored
        # tau_max without re-running emcee).
        'convergence_ratio_n_steps_over_50tau': float(n_steps / (50.0 * tau_max)) if tau_max is not None else None,
        'converged_50tau': bool(n_steps / (50.0 * tau_max) >= 1.0) if tau_max is not None else None,
        'log_L_at_median': float(per_ch[min(per_ch, key=per_ch.get)]),  # worst channel
        'log_L_total_at_median': float(sum(per_ch.values())),
        'comparison_to_v18_37': {
            'v18_37_emcee': 't207c_extended_free_emcee.json',
            'v18_37_f_H_cc_median': 0.00501,
            'v18_37_convergence_ratio': 0.58,
            'v18_37_log_L_at_median': -0.113,
            'note': 'v18.37 hit f_H_cc -> 0 boundary; v18.38 should sit at f_H_cc ~ 0.05-0.20',
        },
    }

    print()
    print("Posterior medians (with std):")
    for p in PARAM_NAMES:
        print(f"  {p:18s} = {posterior_medians[p]:8.4f} +/- {posterior_stds[p]:.4f}")
    print()
    print(f"log L total at median = {out['log_L_total_at_median']:.4f}")
    print(f"convergence: ratio = {n_over_50tau}, converged_50tau = {out['converged_50tau']}")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, indent=2))
    print(f"\nSaved: {OUT_PATH}")


if __name__ == '__main__':
    main()