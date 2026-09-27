"""T207_FWHM_sensitivity.py — test how Lorentzian FWHM affects geometric degeneracy.

For each FWHM in [10, 30, 50, 100, 200] km/s, run DE and record:
- v_HL optimum
- σ_HL(100) decomposition (background vs peak contribution)
- Whether Mechanism A (on-peak) or Mechanism B (off-peak+high-bg) wins.
"""
import sys
import json
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import T207_three_term_fit as T207mod
from scipy.optimize import differential_evolution

# Test FWHMs
FWHMS = [10, 30, 50, 100, 200]

# Load DE best-fit for init
de_path = Path(r'C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\t207_three_term_fit.json')
de_data = json.loads(de_path.read_text())
de_best = de_data['free_f_H']['best_params']

BOUNDS_9 = T207mod.BOUNDS

print('=== FWHM sensitivity test ===')
results = {}

for w_test in FWHMS:
    print(f'\n--- FWHM = {w_test} km/s ---')

    def fit_log_L_fwhm(params):
        for i, (low, high) in enumerate(BOUNDS_9):
            if not (low <= params[i] <= high):
                return -1e10
        arr = [params[0], params[1], params[2], params[3], params[4], params[5], params[6], params[7], params[8]]
        ll = T207mod.log_likelihood_for_params(arr, f_H_cf_fixed=None, f_H_cc_fixed=None, width_HL_override=float(w_test))
        return ll if np.isfinite(ll) else -1e10

    res = differential_evolution(fit_log_L_fwhm, bounds=BOUNDS_9, maxiter=200, tol=1e-3, seed=42)
    params = res.x
    log_L = res.fun

    sig_0, sig_peak_HH, sig_0_HL, sig_peak_HL, v_HL, sig_0_LL, a_slope, f_H_cf, f_H_cc = params
    sigma_HL_bg = sig_0_HL
    sigma_HL_peak_at_100 = sig_peak_HL * (w_test/2)**2 / ((100 - v_HL)**2 + (w_test/2)**2)
    sigma_HL_total_100 = sigma_HL_bg + sigma_HL_peak_at_100

    # Identify mechanism
    if abs(v_HL - 100) < 30 and sigma_HL_peak_at_100 > 2 * sigma_HL_bg:
        mechanism = 'A (on-peak resonance)'
    elif abs(v_HL - 100) > 30 and sigma_HL_bg > 0.05:
        mechanism = 'B (off-peak + high bg)'
    else:
        mechanism = 'mixed'

    print(f'  log L = {log_L:.3f}')
    print(f'  v_HL={v_HL:.1f}, σ_peak_HL={sig_peak_HL:.3f}, σ_0_HL={sig_0_HL:.3f}')
    print(f'  σ_HL(100) = {sigma_HL_total_100:.4f} (bg={sigma_HL_bg:.4f}, peak={sigma_HL_peak_at_100:.4f})')
    print(f'  Mechanism: {mechanism}')

    results[f'FWHM_{w_test}'] = {
        'FWHM_kms': w_test,
        'log_L': float(log_L),
        'best_params': {
            'v_HL': float(v_HL),
            'sigma_peak_HL': float(sig_peak_HL),
            'sigma_0_HL': float(sig_0_HL),
            'sigma_peak_HH_1': float(sig_peak_HH),
            'f_H_cf': float(f_H_cf),
            'f_H_cc': float(f_H_cc),
        },
        'sigma_HL_100_decomposition': {
            'bg_contribution': float(sigma_HL_bg),
            'peak_contribution': float(sigma_HL_peak_at_100),
            'total': float(sigma_HL_total_100),
        },
        'mechanism': mechanism,
    }

# Save
out_path = Path(r'C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\t207_fwhm_sensitivity.json')
out_path.write_text(json.dumps(results, indent=2))
print(f'\nSaved: {out_path} size={out_path.stat().st_size}B')

# Summary
print('\n=== SUMMARY ===')
print(f'{"FWHM":>5} {"log L":>8} {"v_HL":>6} {"σ_peak_HL":>10} {"σ_0_HL":>8} {"σ_HL(100)":>10} {"mechanism":<25}')
for key, r in results.items():
    print(f'{r["FWHM_kms"]:>5} {r["log_L"]:>8.3f} {r["best_params"]["v_HL"]:>6.0f} {r["best_params"]["sigma_peak_HL"]:>10.3f} {r["best_params"]["sigma_0_HL"]:>8.3f} {r["sigma_HL_100_decomposition"]["total"]:>10.4f} {r["mechanism"]:<25}')