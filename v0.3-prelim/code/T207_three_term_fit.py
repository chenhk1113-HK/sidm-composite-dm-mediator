"""T207 — Three-term decomposition fit (Path F1 of "Plan for further dev.docx").

9-parameter fit over the joint 8-channel likelihood with full three-term
sigma_eff = f_H^2 sigma_HH + 2 f_H f_L sigma_HL + f_L^2 sigma_LL.

Sampling strategy (per user direction):
  1. Differential evolution (DE) — global, finds the basin.
  2. emcee — local refinement, posterior estimation.

Three f_H prescriptions are run separately (per user direction):
  - "borrowed" (hand-picked, retracted v18.29 — included for comparison only)
  - "yang" (Yang+ 2025 Fig. 2 derived)
  - "t202" (T202 N-body)

Channels (per T205 published sigma_unc):
  UFD v=3,5,7,10  (ceiling)
  dSph v=15        (ceiling)
  Cloud-9 v=28     (floor)
  SPARC v=100      (gaussian)
  Cluster v=500    (ceiling)

Per "Plan for further dev.docx" (2026-09-23):
  F1 structural failure (SPARC unreachable with sigma_eff = f_H^2 sigma_HH)
  addressed by introducing sigma_HL with a single peak at v_HL ~ 100 km/s.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy.optimize import differential_evolution

sys.path.insert(0, r'C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\code')

from two_component_three_term import (
    sigma_eff_three_term,
    f_H_prescription,
    _phase44_params,
)


# =========================================================================
# Channels and constraints
# =========================================================================
# Per RevT207.docx reviewer recommendation: dSph ceiling was 0.032 (WRONG;
# that value was the velocity-INDEPENDENT 0.04 split across 5 velocity bins,
# not the appropriate limit for our velocity-dependent model).
#
# Correct value per Horigome+ 2025 [27] (arXiv:2503.13650, Results §230):
#   "we obtain 95%-percentile upper limits of 0.8 cm²/g for w=10 km/s and
#    0.04 cm²/g for the velocity-independent case."
#
# For our velocity-dependent multi-resonance model (effective w ~ 10-30 km/s
# from BW peak structure, paper §3.6), the appropriate ceiling is 0.8 cm²/g.
#
# σ_unc is the published 1σ uncertainty from Table II of [27]: ±0.04 cm²/g
# combined stat+syst for dSph v_eff ~ 15 km/s.
CHANNELS = [
    # (name, v, sigma_unc, obs_value, kind, halo_class)
    # Halo_class maps to f_H prescription:
    #   'core_forming' -> f_H_cf
    #   'core_collapsed' -> f_H_cc
    #   'intermediate' -> (f_H_cf + f_H_cc) / 2
    ('UFD v=3',   3.0,   0.05,  0.155, 'ceiling',  'core_collapsed'),
    ('UFD v=5',   5.0,   0.05,  0.093, 'ceiling',  'core_collapsed'),
    ('UFD v=7',   7.0,   0.05,  0.067, 'ceiling',  'core_collapsed'),
    ('UFD v=10', 10.0,   0.05,  0.047, 'ceiling',  'core_collapsed'),
    ('dSph v=15', 15.0,  0.04,  0.8,   'ceiling',  'core_collapsed'),  # FIXED per RevT207
    ('Cloud-9 v=28', 28.0, 30.0, 128.0, 'floor',   'core_forming'),
    ('SPARC v=100', 100.0, 0.05, 0.193, 'gaussian', 'intermediate'),
    ('Cluster v=500', 500.0, 5e-4, 2.5e-4, 'ceiling', 'core_collapsed'),
]


# =========================================================================
# Param vector layout
# =========================================================================
PARAM_NAMES = [
    'sigma_0', 'sigma_peak_HH_1', 'sigma_0_HL', 'sigma_peak_HL',
    'v_HL', 'sigma_0_LL', 'a_slope', 'f_H_cf', 'f_H_cc',
]

# Bounds (lower, upper)
BOUNDS = [
    (0.001, 0.5),      # sigma_0 (HH bg)
    (10.0, 1000.0),    # sigma_peak_HH_1 (Cloud-9 peak)
    (1e-5, 0.5),       # sigma_0_HL (HL bg)
    (0.0, 2.0),        # sigma_peak_HL (HL peak amp)
    (50.0, 200.0),     # v_HL (HL resonance position, km/s)
    (1e-5, 0.5),       # sigma_0_LL (LL bg)
    (0.5, 3.0),        # a_slope (Yukawa)
    (0.5, 1.0),        # f_H_cf
    (0.0, 1.0),        # f_H_cc
]


# =========================================================================
# Likelihood
# =========================================================================
def log_likelihood_for_params(arr, f_H_cf_fixed=None, f_H_cc_fixed=None,
                                return_per_channel=False, width_HL_override=None):
    """Joint log-likelihood for the 8-channel fit.

    If f_H_cf_fixed and f_H_cc_fixed are provided, override the fit's f_H values
    (used when running the fit under a given prescription).

    If width_HL_override is provided, override the default 50 km/s Lorentzian width
    (used for FWHM sensitivity tests).

    Returns: scalar log L (or dict if return_per_channel=True).
    """
    sigma_0, sigma_peak_HH_1, sigma_0_HL, sigma_peak_HL, v_HL, sigma_0_LL, a_slope, f_H_cf_fit, f_H_cc_fit = arr
    # Use fixed f_H values if provided (prescription mode), else from fit
    f_H_cf = f_H_cf_fixed if f_H_cf_fixed is not None else f_H_cf_fit
    f_H_cc = f_H_cc_fixed if f_H_cc_fixed is not None else f_H_cc_fit
    f_H_int = 0.5 * (f_H_cf + f_H_cc)

    halo_fH = {
        'core_forming': f_H_cf,
        'core_collapsed': f_H_cc,
        'intermediate': f_H_int,
    }

    width_HL = width_HL_override if width_HL_override is not None else 50.0

    log_L = 0.0
    per_ch = {}
    for name, v, sigma_unc, obs, kind, halo in CHANNELS:
        f_H = halo_fH[halo]
        sigma_eff = sigma_eff_three_term(
            v, f_H=f_H,
            sigma_0=sigma_0, a_slope=a_slope, sigma_peak_HH_1=sigma_peak_HH_1,
            sigma_0_HL=sigma_0_HL, sigma_peak_HL=sigma_peak_HL,
            v_HL=v_HL, width_HL=width_HL,
            sigma_0_LL=sigma_0_LL,
        )

        ch_log_L = 0.0
        if kind == 'ceiling':
            if sigma_eff > obs:
                z = (sigma_eff - obs) / sigma_unc
                ch_log_L = -0.5 * z**2
        elif kind == 'floor':
            if sigma_eff < obs:
                z = (obs - sigma_eff) / sigma_unc
                ch_log_L = -0.5 * z**2
        elif kind == 'gaussian':
            z = (sigma_eff - obs) / sigma_unc
            ch_log_L = -0.5 * z**2

        per_ch[name] = ch_log_L
        log_L += ch_log_L

    if return_per_channel:
        return per_ch
    return log_L


def negative_log_likelihood(arr):
    """For DE optimizer (minimizes)."""
    return -log_likelihood_for_params(arr)


# =========================================================================
# Fit a single prescription (Differential Evolution, no MCMC yet)
# =========================================================================
def fit_prescription(name: str, de_maxiter: int = 200, de_popsize: int = 30,
                     de_seed: int = 42, verbose: bool = True) -> dict:
    """Fit T207 under the given f_H prescription (free sigma/peak params).

    For prescription mode: f_H_cf and f_H_cc are FIXED; the other 7 params are free.
    """
    presc = f_H_prescription(name)
    f_H_cf_fixed = presc['f_H_cf']
    f_H_cc_fixed = presc['f_H_cc']

    # Bounds for the 7 free params (sigma_0, peak_HH_1, sigma_0_HL, peak_HL,
    # v_HL, sigma_0_LL, a_slope); f_H values are fixed
    free_bounds = [BOUNDS[i] for i in [0, 1, 2, 3, 4, 5, 6]]

    def neg_log_L_free(arr_free):
        # Reconstruct full 9-vec with fixed f_H
        full = np.array([
            arr_free[0], arr_free[1], arr_free[2], arr_free[3],
            arr_free[4], arr_free[5], arr_free[6],
            f_H_cf_fixed, f_H_cc_fixed,
        ])
        return -log_likelihood_for_params(full)

    t0 = time.time()
    result = differential_evolution(
        neg_log_L_free, bounds=free_bounds,
        maxiter=de_maxiter, popsize=de_popsize, seed=de_seed,
        tol=1e-7, polish=True, workers=1,
        updating='deferred', init='sobol',
    )
    elapsed = time.time() - t0

    # Reconstruct full best-fit vector
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
        'f_H_int': 0.5 * (f_H_cf_fixed + f_H_cc_fixed),
        'best_params': dict(zip(PARAM_NAMES, best_full.tolist())),
        'log_L_peak': float(log_L_peak),
        'per_channel_log_L': per_ch,
        'de_result_success': bool(result.success),
        'de_result_message': result.message,
        'de_elapsed_sec': float(elapsed),
    }

    if verbose:
        print(f"\n=== T207 / Prescription: {name} (DE fit) ===")
        print(f"  f_H_cf = {f_H_cf_fixed}, f_H_cc = {f_H_cc_fixed}")
        print(f"  log L_peak = {log_L_peak:.4f}")
        print(f"  DE success: {result.success}, message: {result.message}")
        print(f"  Elapsed: {elapsed:.1f} s")
        print(f"  Best params:")
        for k, v in out['best_params'].items():
            print(f"    {k:18s} = {v:.4f}")
        print(f"  Per-channel log L contributions:")
        sorted_ch = sorted(per_ch.items(), key=lambda x: x[1])
        for name_, ch_logL in sorted_ch:
            mark = '***' if ch_logL < -0.5 else ''
            print(f"    {name_:18s} log L = {ch_logL:+.4f}  {mark}")

    return out


# =========================================================================
# Main: run all three prescriptions + free-f_H fit
# =========================================================================
def main():
    print("=" * 80)
    print("T207 — Three-term decomposition fit (Plan for further dev.docx §F1)")
    print("=" * 80)

    results = {}

    # Three prescription modes (f_H fixed)
    for name in ['borrowed', 'yang', 't202']:
        print(f"\n--- Fitting prescription: {name} ---")
        results[f'prescription_{name}'] = fit_prescription(name)

    # Free-f_H fit (9 free params)
    print(f"\n--- Free f_H fit (9 free params) ---")

    def neg_log_L_full(arr):
        return -log_likelihood_for_params(arr)

    t0 = time.time()
    de_full = differential_evolution(
        neg_log_L_full, bounds=BOUNDS,
        maxiter=200, popsize=30, seed=42,
        tol=1e-7, polish=True, workers=1,
        updating='deferred', init='sobol',
    )
    elapsed = time.time() - t0

    full_log_L_peak = -de_full.fun
    per_ch_full = log_likelihood_for_params(de_full.x, return_per_channel=True)

    out_full = {
        'prescription': 'free_f_H',
        'best_params': dict(zip(PARAM_NAMES, de_full.x.tolist())),
        'log_L_peak': float(full_log_L_peak),
        'per_channel_log_L': per_ch_full,
        'de_result_success': bool(de_full.success),
        'de_result_message': de_full.message,
        'de_elapsed_sec': float(elapsed),
    }

    print(f"\n=== T207 / Free f_H fit (DE) ===")
    print(f"  log L_peak = {full_log_L_peak:.4f}")
    print(f"  DE success: {de_full.success}, message: {de_full.message}")
    print(f"  Elapsed: {elapsed:.1f} s")
    print(f"  Best params:")
    for k, v in out_full['best_params'].items():
        print(f"    {k:18s} = {v:.4f}")
    print(f"  Per-channel log L contributions:")
    sorted_ch = sorted(per_ch_full.items(), key=lambda x: x[1])
    for name_, ch_logL in sorted_ch:
        mark = '***' if ch_logL < -0.5 else ''
        print(f"    {name_:18s} log L = {ch_logL:+.4f}  {mark}")

    results['free_f_H'] = out_full

    # Save
    out_path = Path(r'C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\t207_three_term_fit.json')
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, indent=2))
    print(f"\nSaved: {out_path}")


if __name__ == '__main__':
    main()