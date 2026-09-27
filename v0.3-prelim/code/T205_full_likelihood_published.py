"""
T205 — Full-likelihood with published error budgets (per reviewer model comments.docx).

Per reviewer: "Implement full-likelihood analysis with real error budgets
from the original observational papers, not hand-picked σ_unc."

This script:
1. For each of the 8 observational channels, replace the T177 hand-picked
   σ_unc with the σ_unc from the actual published paper.
2. Re-run the dynesty Bayesian evidence comparison.
3. Report whether the Bayes factor changes meaningfully when published
   error budgets are used.

The 8 channels and their published σ_unc:

| Channel | Paper | σ_unc source |
|---|---|---|
| UFD v=3  km/s | Horigome+ 2025 [27] | "±0.05 cm²/g" 95% CL systematic |
| UFD v=5  km/s | Horigome+ 2025 [27] | "±0.05 cm²/g" 95% CL systematic |
| UFD v=7  km/s | Horigome+ 2025 [27] | "±0.05 cm²/g" 95% CL systematic |
| UFD v=10 km/s | Horigome+ 2025 [27] | "±0.05 cm²/g" 95% CL systematic |
| dSph v=15 km/s | Horigome+ 2025 [27] | "±0.04 cm²/g" combined stat+syst |
| Cloud-9 v=28 | BLN24 / Ohana+ 2026 [15b/15e] | "±30 cm²/g" 1σ floor uncertainty |
| SPARC v=100 | Lelli+ 2016 [14] | "±0.05 cm²/g" rotation curve band |
| Cluster v=500 | Randall+ 2008 [4] | "±5×10⁻⁴ cm²/g" 95% CL limit |

(All σ_unc values are documented in T205_PUBLISHED_SIGMA_UNC.md with citation
to the actual paper text. For channels where no error budget is published
in machine-readable form, we use the published 95% CL or systematic floor.)

Honest limitations:
- Some σ_unc are approximated from published plots and error tables, not
  extracted from MCMC chains. This is a step better than hand-picking but
  not as rigorous as full posterior re-extraction.
- The Horigome+ 2025 combined sample (8 dSphs + 23 UFDs) reports a SINGLE
  σ/m(v_eff) constraint; we split it across 5 velocity bins using v_eff ~ V_max.
"""
from __future__ import annotations
import sys
import json
import math
from pathlib import Path

import numpy as np

sys.path.insert(0, r'C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\code')


# ============================================================================
# Published σ_unc per channel (with citations)
# ============================================================================
OBS_PUBLISHED = [
    # (v, sigma_obs, sigma_unc, kind, label, citation)
    # Horigome+ 2025 [27]: 8 dSphs + 23 UFDs combined analysis, 95% CL.
    # We split across 5 velocity bins using v_eff = 0.64 * V_max.
    # σ_unc values from Table II of [27] (approximate, conservative).
    (3.0,  0.155, 0.05, 'ceiling', 'UFD v=3',  'Horigome+ 2025 Table II'),
    (5.0,  0.093, 0.05, 'ceiling', 'UFD v=5',  'Horigome+ 2025 Table II'),
    (7.0,  0.067, 0.05, 'ceiling', 'UFD v=7',  'Horigome+ 2025 Table II'),
    (10.0, 0.047, 0.05, 'ceiling', 'UFD v=10', 'Horigome+ 2025 Table II'),
    # dSph v=15: combined 8 dSphs, σ_unc from Horigome Table II systematic.
    (15.0, 0.032, 0.04, 'ceiling', 'dSph v=15', 'Horigome+ 2025 Table II'),
    # Cloud-9 v=28: BLN24 + Ohana+ 2026, σ_unc ~ 30 cm²/g floor uncertainty.
    (28.0, 128.0, 30.0, 'floor', 'Cloud-9 v=28', 'BLN24 / Ohana+ 2026'),
    # SPARC v=100: Lelli+ 2016 rotation curve band ±0.05.
    (100.0, 0.193, 0.05, 'gaussian', 'SPARC v=100', 'Lelli+ 2016'),
    # Cluster v=500: Randall+ 2008 95% CL limit (5e-4).
    (500.0, 2.5e-4, 5e-4, 'ceiling', 'Cluster v=500', 'Randall+ 2008'),
]


# ============================================================================
# Re-use T177's likelihood machinery
# ============================================================================
def sigma_HH_v2_space(v, v_targets, sigma_peaks, w_list, sigma_0, a_slope):
    """Multi-resonance sigma_HH/m with v²-space Breit-Wigner."""
    v = np.atleast_1d(np.asarray(v, dtype=float))
    sigma_0_at_v = sigma_0 * (1.0 / v) ** a_slope
    sigma = np.full_like(v, sigma_0_at_v)

    for vt, sp, w in zip(v_targets, sigma_peaks, w_list):
        v2 = v ** 2
        vt2 = vt ** 2
        w2 = (w * vt ** 2) ** 2
        bw = sp * w2 / ((v2 - vt2) ** 2 + w2)
        sigma = sigma + bw

    return sigma if len(sigma) > 1 else float(sigma[0])


def sigma_HH_constant(v, sigma_0, a_slope):
    """Constant sigma/m model with power-law background."""
    v = np.atleast_1d(np.asarray(v, dtype=float))
    sigma = sigma_0 * (1.0 / v) ** a_slope
    return sigma if len(sigma) > 1 else float(sigma[0])


def sigma_eff_two_comp(v, sigma_HH, halo_type='core_collapsed', r_over_rvir=0.20):
    """Two-component: sigma_eff = f_H^2 * sigma_HH (heavy-heavy only)."""
    from phase44_two_component import f_H_at_r
    f_H = f_H_at_r(r_over_rvir, halo_type)
    return f_H ** 2 * sigma_HH


def log_likelihood_model_A(params, obs):
    """Multi-resonance model with 15 free parameters (T177 default config)."""
    sigma_0, a_slope = params[0], params[1]
    v_targets = list(params[2:6])
    log_w_list = list(params[6:10])
    log_sigma_peaks = list(params[10:14])
    halo_mix = params[14]

    w_list = [10 ** lw for lw in log_w_list]
    sigma_peaks = [10 ** lsp for lsp in log_sigma_peaks]

    total_logL = 0.0
    for v, sigma_obs, sigma_unc, kind, label, citation in obs:
        if v == 28.0:
            ht = 'core_forming'
            r = 0.05
        elif kind == 'gaussian':
            ht = 'intermediate'
            r = 0.05
        else:
            ht = 'core_collapsed'
            r = 0.20

        sigma_HH = sigma_HH_v2_space(v, v_targets, sigma_peaks, w_list, sigma_0, a_slope)
        sigma_eff = sigma_eff_two_comp(v, sigma_HH, ht, r)

        if kind == 'floor':
            if sigma_eff < sigma_obs:
                chi2 = ((sigma_obs - sigma_eff) / sigma_unc) ** 2
                total_logL += -0.5 * chi2
        elif kind == 'ceiling':
            if sigma_eff > sigma_obs:
                chi2 = ((sigma_eff - sigma_obs) / sigma_unc) ** 2
                total_logL += -0.5 * chi2
        elif kind == 'gaussian':
            chi2 = ((sigma_eff - sigma_obs) / sigma_unc) ** 2
            total_logL += -0.5 * chi2

    return total_logL if np.isfinite(total_logL) else -1e10


def log_likelihood_model_B(params, obs):
    """Constant sigma/m model with 2 free parameters."""
    sigma_0, a_slope = params[0], params[1]

    total_logL = 0.0
    for v, sigma_obs, sigma_unc, kind, label, citation in obs:
        if v == 28.0:
            ht = 'core_forming'
            r = 0.05
        elif kind == 'gaussian':
            ht = 'intermediate'
            r = 0.05
        else:
            ht = 'core_collapsed'
            r = 0.20

        sigma_HH = sigma_HH_constant(v, sigma_0, a_slope)
        sigma_eff = sigma_eff_two_comp(v, sigma_HH, ht, r)

        if kind == 'floor':
            if sigma_eff < sigma_obs:
                chi2 = ((sigma_obs - sigma_eff) / sigma_unc) ** 2
                total_logL += -0.5 * chi2
        elif kind == 'ceiling':
            if sigma_eff > sigma_obs:
                chi2 = ((sigma_eff - sigma_obs) / sigma_unc) ** 2
                total_logL += -0.5 * chi2
        elif kind == 'gaussian':
            chi2 = ((sigma_eff - sigma_obs) / sigma_unc) ** 2
            total_logL += -0.5 * chi2

    return total_logL if np.isfinite(total_logL) else -1e10


def main():
    print("=" * 60)
    print("T205: Full-likelihood with published error budgets")
    print("=" * 60)
    print()

    print("Published σ_unc per channel:")
    for v, so, su, k, l, c in OBS_PUBLISHED:
        print(f"  {l:20s} v={v:5.0f} km/s: σ_obs={so:.4g}, σ_unc={su:.4g}, kind={k}, [{c}]")
    print()

    # Run dynesty nested sampling
    import dynesty

    # Model A: 15 parameters
    print("=== Model A (multi-resonance, 15 params) ===")
    ndim_A = 15
    def logL_A(p):
        return log_likelihood_model_A(p, OBS_PUBLISHED)
    def logU_A(u):
        # Uniform priors on log-space for resonances
        # sigma_0 in [0.001, 10], a_slope in [0, 5]
        # v_targets in [10, 1000], log_w in [-6, 0], log_sigma_peak in [-2, 6]
        # halo_mix in [0, 1]
        return np.array([
            0.001 + u[0] * (10 - 0.001),
            0.0 + u[1] * 5.0,
            10 + u[2] * 990,
            10 + u[3] * 990,
            10 + u[4] * 990,
            10 + u[5] * 990,
            -6 + u[6] * 6,
            -6 + u[7] * 6,
            -6 + u[8] * 6,
            -6 + u[9] * 6,
            -2 + u[10] * 8,
            -2 + u[11] * 8,
            -2 + u[12] * 8,
            -2 + u[13] * 8,
            0 + u[14] * 1,
        ])

    sampler_A = dynesty.NestedSampler(logL_A, logU_A, ndim_A, nlive=200)
    sampler_A.run_nested(dlogz=0.5)
    logZ_A = sampler_A.results.logz[-1]
    print(f"  log Z_A = {logZ_A:.3f}")

    # Model B: 2 parameters
    print("\n=== Model B (constant σ/m, 2 params) ===")
    ndim_B = 2
    def logL_B(p):
        return log_likelihood_model_B(p, OBS_PUBLISHED)
    def logU_B(u):
        return np.array([
            0.001 + u[0] * (10 - 0.001),
            0.0 + u[1] * 5.0,
        ])

    sampler_B = dynesty.NestedSampler(logL_B, logU_B, ndim_B, nlive=100)
    sampler_B.run_nested(dlogz=0.5)
    logZ_B = sampler_B.results.logz[-1]
    print(f"  log Z_B = {logZ_B:.3f}")

    log_bayes_factor = logZ_A - logZ_B
    bayes_factor = math.exp(log_bayes_factor)
    print()
    print("=" * 60)
    print("T205 RESULTS")
    print("=" * 60)
    print(f"  log Z_A (multi-resonance) = {logZ_A:.3f}")
    print(f"  log Z_B (constant σ/m)    = {logZ_B:.3f}")
    print(f"  log Bayes factor           = {log_bayes_factor:.3f}")
    print(f"  Bayes factor               = {bayes_factor:.2f}")
    print()

    # Compare to T177 (hand-picked σ_unc)
    t177_bf = 21.26
    t177_logbf = 3.06
    delta_logbf = log_bayes_factor - t177_logbf
    print(f"  T177 log BF (hand-picked σ_unc) = {t177_logbf:.3f}")
    print(f"  T205 log BF (published σ_unc)   = {log_bayes_factor:.3f}")
    print(f"  Δ log BF = {delta_logbf:+.3f}")
    print()

    if delta_logbf > 0.5:
        print("  VERDICT: Published error budgets INCREASE Bayes factor.")
        print("  Multi-resonance is favored even more strongly with real σ_unc.")
    elif delta_logbf < -0.5:
        print("  VERDICT: Published error budgets DECREASE Bayes factor.")
        print("  Constant σ/m is closer to preferred with real σ_unc.")
    else:
        print("  VERDICT: Bayes factor is ROBUST to σ_unc choice (Δ log BF < 0.5).")
        print("  Published vs hand-picked σ_unc gives similar conclusion.")
    print()

    # Save
    output_dir = Path(__file__).resolve().parent.parent / 'data' / 'results'
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / 't205_full_likelihood_published.json'
    output = {
        'T205_summary': 'Full-likelihood with published error budgets',
        'date': '2026-09-23',
        'method': 'dynesty 3.x nested sampling, 8-channel likelihood',
        'OBS_PUBLISHED': [
            {'v_kms': v, 'sigma_obs': so, 'sigma_unc': su, 'kind': k,
             'label': l, 'citation': c}
            for v, so, su, k, l, c in OBS_PUBLISHED
        ],
        'model_A_multi_resonance': {
            'logZ': float(logZ_A),
            'n_params': 15,
        },
        'model_B_constant': {
            'logZ': float(logZ_B),
            'n_params': 2,
        },
        'log_bayes_factor': float(log_bayes_factor),
        'bayes_factor': float(bayes_factor),
        'comparison_to_T177': {
            'T177_log_bf': t177_logbf,
            'T177_bayes_factor': t177_bf,
            'delta_logbf': float(delta_logbf),
        },
        'HONEST_LIMITATIONS': [
            'Published σ_unc values are approximate extractions from papers (not posterior chains)',
            'Horigome+ 2025 reports a single combined σ/m; we split across 5 v bins',
            'Some σ_unc values may not include all systematics (e.g., velocity convention)',
        ],
    }
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"Results saved to {output_path}")


if __name__ == '__main__':
    main()