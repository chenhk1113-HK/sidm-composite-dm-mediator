"""T207_priored_free_de.py — Run only the free_f_H DE with the v18.38 prior.

Saves to t207_priored_free_de.json (does NOT overwrite t207_three_term_fit.json).

Per "Plan for further dev.docx" §3a (2026-09-23): tighter f_H_cc prior to rule
out the v18.31 boundary-peak pathology.

Expected wall time: ~5-10 min.
"""
import sys
import json
import time
from pathlib import Path

sys.path.insert(0, r'C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\code')

import numpy as np
from scipy.optimize import differential_evolution

from T207_three_term_fit import (
    log_likelihood_for_params, BOUNDS, PARAM_NAMES, CHANNELS,
    negative_log_likelihood,
)

OUT_PATH = Path(r'C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\t207_priored_free_de.json')


def main():
    print("=" * 80)
    print("T207 free_f_H DE — f_H_cc >= 0.05 (Yang+ 2025 floor)")
    print("=" * 80)
    print(f"BOUNDS[8] = {BOUNDS[8]}  (f_H_cc prior)")
    print()

    t0 = time.time()
    de = differential_evolution(
        negative_log_likelihood, bounds=BOUNDS,
        maxiter=400, popsize=30, seed=42,
        tol=1e-8, polish=True, workers=1,
        updating='deferred', init='sobol',
    )
    elapsed = time.time() - t0

    log_L_peak = -de.fun
    per_ch = log_likelihood_for_params(de.x, return_per_channel=True)

    out = {
        'metadata': {
            'description': 'free_f_H DE with v18.38 prior (f_H_cc >= 0.05 per Yang+ 2025 Fig. 2)',
            'bounds_change': 'BOUNDS[8] from (0.0, 1.0) to (0.05, 1.0)',
            'expected_outcome': 'no boundary peak; f_H_cc at or above the Yang+ lower limit',
            'elapsed_s': elapsed,
        },
        'best_params': dict(zip(PARAM_NAMES, de.x.tolist())),
        'log_L_peak': float(log_L_peak),
        'per_channel_log_L': per_ch,
        'de_result_success': bool(de.success),
        'de_result_message': de.message,
        'comparison_to_v18_37': {
            'v18_37_free_f_H_log_L': -6.51e-16,  # from t207_three_term_fit.json
            'v18_37_free_f_H_f_H_cc': 0.00411,
            'v18_37_ci68_f_H_cc': [0.0, 0.061],
            'note': 'v18.37 was T206 re-run; T207 free_f_H was at boundary. v18.38 expects'
                    ' f_H_cc in [0.05, ~0.20] (Yang+ 2025 lower portion).',
        },
    }

    print()
    print(f"DE success: {de.success}, message: {de.message}")
    print(f"log L peak = {log_L_peak:.4f}")
    print(f"Elapsed: {elapsed:.1f} s")
    print()
    print("Best params:")
    for k, v in out['best_params'].items():
        print(f"  {k:18s} = {v:.6f}")
    print()
    print("Per-channel log L contributions (sorted by penalty):")
    sorted_ch = sorted(per_ch.items(), key=lambda x: x[1])
    for name_, ch_logL in sorted_ch:
        mark = '***' if ch_logL < -0.5 else ''
        print(f"  {name_:18s} log L = {ch_logL:+.4f}  {mark}")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, indent=2))
    print()
    print(f"Saved: {OUT_PATH}")


if __name__ == '__main__':
    main()