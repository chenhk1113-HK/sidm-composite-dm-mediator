"""T207c — Smarter DE runs on prescription modes with Phase 44 best-fit init.

Per user direction (2026-09-23): DE then emcee. The first DE run found local minima
(borrowed/yang/t202 converged to σ_peak_HH_1 ~ 10-20). This script seeds DE at the
Phase 44 best-fit (σ_peak_HH_1=196.3, a_slope=1.93, σ_0=0.052) which is the
Cloud-9 regime — should converge to the true optimum in fewer iterations.

Three prescription runs (borrowed, yang, t202), each ~3 min with maxiter=80.
"""

from __future__ import annotations

import json
import sys
import time
import warnings
from pathlib import Path

import numpy as np
from scipy.optimize import differential_evolution

warnings.filterwarnings("ignore")
sys.path.insert(0, r'C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\code')

from two_component_three_term import (
    sigma_eff_three_term,
    f_H_prescription,
    _phase44_params,
)
from T207_three_term_fit import (
    log_likelihood_for_params, BOUNDS, PARAM_NAMES,
)


# Phase 44 best-fit init point (the Cloud-9 regime)
PHASE44_INIT = {
    'sigma_0': 0.052,
    'sigma_peak_HH_1': 196.3,  # Cloud-9: phase 44 best-fit
    'sigma_0_HL': 0.02,
    'sigma_peak_HL': 0.33,
    'v_HL': 100.0,
    'sigma_0_LL': 0.05,
    'a_slope': 1.93,  # phase 44 best-fit
    'f_H_cf': 0.85,  # default borrowed
    'f_H_cc': 0.45,  # default yang-ish
}


def smart_init_center(presc_name: str) -> np.ndarray:
    """Phase 44 best-fit init, with f_H values from prescription."""
    presc = f_H_prescription(presc_name)
    init = dict(PHASE44_INIT)
    init['f_H_cf'] = presc['f_H_cf']
    init['f_H_cc'] = presc['f_H_cc']
    return np.array([init[k] for k in PARAM_NAMES])


def seeded_de(name: str, maxiter: int = 80, popsize: int = 30, seed: int = 42,
              verbose: bool = True) -> dict:
    """DE seeded at Phase 44 best-fit, with init population around it."""
    presc = f_H_prescription(name)
    f_H_cf_fixed = presc['f_H_cf']
    f_H_cc_fixed = presc['f_H_cc']

    free_bounds = [BOUNDS[i] for i in [0, 1, 2, 3, 4, 5, 6]]

    # Init vector: Phase 44 best-fit (only the 7 free params)
    center = np.array([
        PHASE44_INIT['sigma_0'],
        PHASE44_INIT['sigma_peak_HH_1'],
        PHASE44_INIT['sigma_0_HL'],
        PHASE44_INIT['sigma_peak_HL'],
        PHASE44_INIT['v_HL'],
        PHASE44_INIT['sigma_0_LL'],
        PHASE44_INIT['a_slope'],
    ])

    def neg_log_L_free(arr_free):
        full = np.array([
            arr_free[0], arr_free[1], arr_free[2], arr_free[3],
            arr_free[4], arr_free[5], arr_free[6],
            f_H_cf_fixed, f_H_cc_fixed,
        ])
        return -log_likelihood_for_params(full)

    # Generate init population: small Gaussian ball around Phase 44 best-fit
    rng = np.random.default_rng(seed)
    init_pop = []
    for _ in range(popsize * len(free_bounds)):
        cand = center * (1.0 + 0.10 * rng.standard_normal(len(center)))
        for i, (lo, hi) in enumerate(free_bounds):
            cand[i] = np.clip(cand[i], lo, hi)
        init_pop.append(cand)
    init_pop = np.array(init_pop[:popsize * len(free_bounds)])

    t0 = time.time()
    result = differential_evolution(
        neg_log_L_free, bounds=free_bounds,
        maxiter=maxiter, popsize=popsize, seed=seed,
        tol=1e-8, polish=True, workers=1,
        updating='deferred', init=init_pop,
    )
    elapsed = time.time() - t0

    best_full = np.array([
        result.x[0], result.x[1], result.x[2], result.x[3],
        result.x[4], result.x[5], result.x[6],
        f_H_cf_fixed, f_H_cc_fixed,
    ])
    log_L_peak = -result.fun
    per_ch = log_likelihood_for_params(best_full, return_per_channel=True)

    out = {
        'prescription': name,
        'f_H_cf': f_H_cf_fixed,
        'f_H_cc': f_H_cc_fixed,
        'best_params': dict(zip(PARAM_NAMES, best_full.tolist())),
        'log_L_peak': float(log_L_peak),
        'per_channel_log_L': per_ch,
        'de_result_success': bool(result.success),
        'de_result_message': result.message,
        'de_elapsed_sec': float(elapsed),
        'init_strategy': 'phase44_best_fit',
    }

    if verbose:
        print(f"\n=== T207c / Prescription: {name} (Phase 44 seeded DE) ===")
        print(f"  f_H_cf = {f_H_cf_fixed}, f_H_cc = {f_H_cc_fixed}")
        print(f"  log L_peak = {log_L_peak:.4f}")
        print(f"  DE success: {result.success}, message: {result.message}")
        print(f"  Elapsed: {elapsed:.1f} s")
        print(f"  Best params:")
        for k, v in out['best_params'].items():
            print(f"    {k:18s} = {v:.4f}")
        sorted_ch = sorted(per_ch.items(), key=lambda x: x[1])
        print(f"  Per-channel log L contributions:")
        for n, ll in sorted_ch:
            mark = '***' if ll < -0.5 else ''
            print(f"    {n:18s} log L = {ll:+.4f}  {mark}")

    return out


def main():
    print("=" * 80)
    print("T207c — Smarter DE (Phase 44 best-fit seeded) on prescription modes")
    print("=" * 80)

    results = {}
    for name in ['borrowed', 'yang', 't202']:
        print(f"\n--- Prescription: {name} ---")
        results[name] = seeded_de(name)

    out_path = Path(r'C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\t207c_smart_de.json')
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, indent=2))
    print(f"\nSaved: {out_path}")


if __name__ == '__main__':
    main()