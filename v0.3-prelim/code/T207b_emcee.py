"""T207b — emcee posterior estimation for the three-term decomposition fit.

Per user direction (2026-09-23): "DM, then emcee" — Differential Evolution first
(already done, saved to t207_three_term_fit.json), then emcee to refine and
characterize the posterior.

Strategy:
  1. Initialize emcee walkers around the DE best-fit (small Gaussian ball).
  2. Run 32 walkers × 5000 steps (with burn-in of 1000).
  3. Compute posterior mean, std, 16/50/84 percentiles.
  4. Report convergence (autocorrelation time, acceptance fraction).

Three modes:
  - free_f_H: 9 free parameters, around DE free-fit result
  - borrowed: 7 free parameters (f_H fixed), around DE borrowed result
  - yang:     7 free parameters (f_H fixed), around DE yang result
  - t202:     7 free parameters (f_H fixed), around DE t202 result

Per "Plan for further dev.docx" §4: "The posterior will be interior but broad.
That is acceptable; the current boundary-peaked posterior is the worse outcome."
"""

from __future__ import annotations

import json
import sys
import time
import warnings
from pathlib import Path

import numpy as np

warnings.filterwarnings("ignore")
sys.path.insert(0, r'C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\code')

import emcee

from two_component_three_term import (
    sigma_eff_three_term,
    f_H_prescription,
    _phase44_params,
)
from T207_three_term_fit import (
    log_likelihood_for_params, BOUNDS, PARAM_NAMES,
)


# =========================================================================
# Log-prior (uniform within bounds, hard zero outside)
# =========================================================================
def log_prior(arr):
    """Uniform prior within BOUNDS."""
    for i, (lo, hi) in enumerate(BOUNDS):
        if not (lo <= arr[i] <= hi):
            return -np.inf
    return 0.0


def log_posterior(arr, f_H_cf_fixed=None, f_H_cc_fixed=None):
    """Log posterior = log prior + log likelihood."""
    lp = log_prior(arr)
    if not np.isfinite(lp):
        return -np.inf
    try:
        ll = log_likelihood_for_params(arr, f_H_cf_fixed=f_H_cf_fixed,
                                       f_H_cc_fixed=f_H_cc_fixed)
    except Exception:
        return -np.inf
    if not np.isfinite(ll):
        return -np.inf
    return lp + ll


# =========================================================================
# Initial walker positions
# =========================================================================
def init_walkers_around(arr_center, n_walkers, scale=0.05, seed=42):
    """Initialize walkers in a small Gaussian ball around arr_center.

    Args:
        arr_center: 9-parameter vector (the DE best-fit)
        n_walkers: number of walkers
        scale: relative scale (0.05 = 5% of each param's range)

    Returns:
        arr of shape (n_walkers, 9)
    """
    rng = np.random.default_rng(seed)
    arrs = []
    while len(arrs) < n_walkers:
        cand = arr_center * (1.0 + scale * rng.standard_normal(len(arr_center)))
        # Clamp to bounds
        for i, (lo, hi) in enumerate(BOUNDS):
            cand[i] = np.clip(cand[i], lo, hi)
        # Check that this candidate has finite log-probability
        if np.isfinite(log_prior(cand)):
            arrs.append(cand)
    return np.array(arrs)


# =========================================================================
# Run emcee for a single mode
# =========================================================================
def run_emcee_mode(mode_name: str, arr_center: np.ndarray, n_walkers: int = 32,
                   n_steps: int = 5000, burn_in: int = 1000, verbose: bool = True):
    """Run emcee for the given mode.

    Args:
        mode_name: 'free_f_H', 'borrowed', 'yang', 't202'
        arr_center: 9-param DE best-fit to initialize walkers around
        n_walkers: number of walkers (default 32, must be > 2*ndim)
        n_steps: total steps per walker
        burn_in: steps to discard as burn-in
    """
    ndim = len(arr_center)

    # Fixed f_H for prescription modes
    f_H_cf_fixed = None
    f_H_cc_fixed = None
    if mode_name in ('borrowed', 'yang', 't202'):
        presc = f_H_prescription(mode_name)
        f_H_cf_fixed = presc['f_H_cf']
        f_H_cc_fixed = presc['f_H_cc']

    # Initialize walkers
    init = init_walkers_around(arr_center, n_walkers, scale=0.05, seed=42)
    print(f"  init walker positions: shape {init.shape}")

    sampler = emcee.EnsembleSampler(
        n_walkers, ndim, log_posterior,
        args=(f_H_cf_fixed, f_H_cc_fixed),
    )

    t0 = time.time()
    sampler.run_mcmc(init, n_steps, progress=False)
    elapsed = time.time() - t0

    # Get chain, discard burn-in
    chain = sampler.get_chain(discard=burn_in)
    flat_chain = sampler.get_chain(discard=burn_in, flat=True)
    log_probs = sampler.get_log_prob(discard=burn_in, flat=True)

    # Posterior stats
    p16 = np.percentile(flat_chain, 16, axis=0)
    p50 = np.percentile(flat_chain, 50, axis=0)
    p84 = np.percentile(flat_chain, 84, axis=0)
    std = np.std(flat_chain, axis=0)

    # Autocorrelation time (rough)
    try:
        tau = sampler.get_autocorr_time(quiet=True)
        tau = np.asarray(tau)
        converged = (tau * 10 < n_steps - burn_in).all()
    except Exception:
        tau = np.full(ndim, np.nan)
        converged = False

    acceptance = np.mean(sampler.acceptance_fraction)

    out = {
        'mode': mode_name,
        'n_walkers': n_walkers,
        'n_steps': n_steps,
        'burn_in': burn_in,
        'arr_center_init': arr_center.tolist(),
        'posterior_p16': dict(zip(PARAM_NAMES, p16.tolist())),
        'posterior_p50': dict(zip(PARAM_NAMES, p50.tolist())),
        'posterior_p84': dict(zip(PARAM_NAMES, p84.tolist())),
        'posterior_std': dict(zip(PARAM_NAMES, std.tolist())),
        'posterior_max_log_L': float(np.max(log_probs)),
        'autocorr_time': dict(zip(PARAM_NAMES, tau.tolist())),
        'converged': bool(converged),
        'acceptance_fraction': float(acceptance),
        'elapsed_sec': float(elapsed),
    }

    if verbose:
        print(f"\n=== emcee: {mode_name} ({n_walkers} walkers x {n_steps} steps) ===")
        print(f"  Elapsed: {elapsed:.1f} s")
        print(f"  Acceptance: {acceptance:.3f}")
        print(f"  Converged: {converged}")
        print(f"  Max log L: {np.max(log_probs):.4f}")
        print(f"  Posterior median ± std:")
        for k in PARAM_NAMES:
            print(f"    {k:18s} = {p50[PARAM_NAMES.index(k)]:>10.4f} ± {std[PARAM_NAMES.index(k)]:.4f}  "
                  f"[{p16[PARAM_NAMES.index(k)]:.4f}, {p84[PARAM_NAMES.index(k)]:.4f}]")
        print(f"  Autocorrelation times:")
        for k in PARAM_NAMES:
            print(f"    {k:18s} tau = {tau[PARAM_NAMES.index(k)]:.1f}")

    return out


# =========================================================================
# Main: run emcee on all 4 modes
# =========================================================================
def main():
    print("=" * 80)
    print("T207b — emcee posterior refinement on T207 free fit + prescription modes")
    print("=" * 80)

    # Load DE results
    de_results_path = Path(r'C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\t207_three_term_fit.json')
    with open(de_results_path) as f:
        de_results = json.load(f)

    emcee_results = {}

    # 1. Free f_H emcee
    print("\n--- emcee on free f_H fit ---")
    arr_center_free = np.array([de_results['free_f_H']['best_params'][k]
                                 for k in PARAM_NAMES])
    emcee_results['free_f_H'] = run_emcee_mode(
        'free_f_H', arr_center_free, n_walkers=32, n_steps=5000, burn_in=1000)

    # 2. Borrowed prescription emcee
    print("\n--- emcee on borrowed prescription ---")
    arr_center_borrowed = np.array([de_results['prescription_borrowed']['best_params'][k]
                                     for k in PARAM_NAMES])
    emcee_results['borrowed'] = run_emcee_mode(
        'borrowed', arr_center_borrowed, n_walkers=24, n_steps=3000, burn_in=600)

    # 3. Yang prescription emcee
    print("\n--- emcee on yang prescription ---")
    arr_center_yang = np.array([de_results['prescription_yang']['best_params'][k]
                                 for k in PARAM_NAMES])
    emcee_results['yang'] = run_emcee_mode(
        'yang', arr_center_yang, n_walkers=24, n_steps=3000, burn_in=600)

    # 4. T202 prescription emcee
    print("\n--- emcee on t202 prescription ---")
    arr_center_t202 = np.array([de_results['prescription_t202']['best_params'][k]
                                 for k in PARAM_NAMES])
    emcee_results['t202'] = run_emcee_mode(
        't202', arr_center_t202, n_walkers=24, n_steps=3000, burn_in=600)

    # Save
    out_path = Path(r'C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\t207b_emcee.json')
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(emcee_results, indent=2))
    print(f"\nSaved: {out_path}")


if __name__ == '__main__':
    main()