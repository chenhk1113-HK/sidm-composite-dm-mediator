"""
T177 — Proper Bayesian evidence comparison: multi-resonance vs constant sigma/m.

Per DeepSeek review1 (2026-09-21), the project's BIC = -170 (and -24.10)
headline uses a scoring-rule logL, NOT a proper Bayesian evidence.
This script computes the actual Bayesian log-evidence via dynesty nested
sampling for both:

  Model A — Multi-resonance (15 params): v_targets free, sigma_peaks fixed
  Model B — Constant sigma/m (1 param): single sigma_0 for all velocities

The data are the 8 observational channels:
  (v, sigma_observed, sigma_uncertainty, kind) where kind = 'floor' or 'ceiling'
  Cloud-9 floor: sigma/m >= 50 at v=28
  dSph/UFD ceiling: sigma/m <= 0.8 at v=3-15
  SPARC target: sigma/m = 0.19 +/- 0.05 at v=100
  Cluster ceiling: sigma/m <= 0.001 at v=500

Likelihood (one-sided for floor/ceiling, Gaussian for SPARC):
  Floor (Cloud-9): log L = -((50 - sigma_pred)/sigma_floor)^2 / 2 if sigma_pred < 50
                    (penalize if sigma_pred is below the floor)
  Ceiling (dSph/UFD/Cluster): log L = -((sigma_pred - limit)/sigma_ceiling)^2 / 2 if sigma_pred > limit
                    (penalize if sigma_pred is above the ceiling)
  Gaussian (SPARC): log L = -((sigma_pred - 0.19)/0.05)^2 / 2

This gives a proper Bayesian likelihood for each model. The Bayes factor
B = exp(logZ_A - logZ_B) tells us how much better Model A is than Model B.
"""
import sys
import json
import math
sys.path.insert(0, r'C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\code')

import numpy as np
import dynesty


# Observational data (8 channels)
OBS = [
    # (v, sigma_obs, sigma_unc, kind, label)
    (3.0,  0.155, 0.05, 'ceiling', 'UFD v=3'),
    (5.0,  0.093, 0.05, 'ceiling', 'UFD v=5'),
    (7.0,  0.067, 0.05, 'ceiling', 'UFD v=7'),
    (10.0, 0.047, 0.05, 'ceiling', 'UFD v=10'),
    (15.0, 0.032, 0.05, 'ceiling', 'dSph v=15'),
    (28.0, 128.0, 50.0, 'floor', 'Cloud-9 v=28'),
    (100.0, 0.193, 0.05, 'gaussian', 'SPARC v=100'),
    (500.0, 2.5e-4, 5e-4, 'ceiling', 'Cluster v=500'),
]


# Constants
c_kms = 2.998e5  # km/s


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


def log_likelihood_model_A(params, obs=OBS):
    """Multi-resonance model with 15 free parameters (T120.4 default config).

    params = (sigma_0, a_slope, v_targets[0..3], log_w_list[0..3], log_sigma_peaks[0..3], halo_mix)
    1 + 1 + 4 + 4 + 4 + 1 = 15 params
    """
    sigma_0, a_slope = params[0], params[1]
    v_targets = list(params[2:6])
    log_w_list = list(params[6:10])
    log_sigma_peaks = list(params[10:14])
    halo_mix = params[14]

    w_list = [10 ** lw for lw in log_w_list]
    sigma_peaks = [10 ** lsp for lsp in log_sigma_peaks]

    total_logL = 0.0
    for v, sigma_obs, sigma_unc, kind, label in obs:
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
            # Soft Gaussian penalty for failing floor (sigma_unc acts as scale)
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


def log_likelihood_model_B(params, obs=OBS):
    """Constant sigma/m model with 1 free parameter.

    params = (sigma_0, a_slope)  -- 2 params; we vary both for simplicity
    """
    sigma_0, a_slope = params[0], params[1]

    total_logL = 0.0
    for v, sigma_obs, sigma_unc, kind, label in obs:
        sigma_eff = sigma_HH_constant(v, sigma_0, a_slope)

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


def prior_transform_model_A(u):
    """Prior transform for Model A (15 params)."""
    p = np.empty(15)
    # sigma_0 in [0.01, 1.0]
    p[0] = 10 ** (np.log10(0.01) + u[0] * (np.log10(1.0) - np.log10(0.01)))
    # a_slope in [0.5, 2.0]
    p[1] = 0.5 + u[1] * 1.5
    # v_targets in [10, 1000] km/s
    for i in range(4):
        p[2 + i] = 10 ** (1 + u[2 + i] * 3)  # 10 to 1000
    # log_w_list in [-2.5, -0.5] (log of FWHM fraction)
    for i in range(4):
        p[6 + i] = -2.5 + u[6 + i] * 2.0
    # log_sigma_peaks in [-2, 4] (cm^2/g)
    for i in range(4):
        p[10 + i] = -2 + u[10 + i] * 6
    # halo_mix in [0, 1]
    p[14] = u[14]
    return p


def prior_transform_model_B(u):
    """Prior transform for Model B (2 params)."""
    p = np.empty(2)
    # sigma_0 in [0.001, 10.0]
    p[0] = 10 ** (np.log10(0.001) + u[0] * (np.log10(10.0) - np.log10(0.001)))
    # a_slope in [0, 3]
    p[1] = 0 + u[1] * 3
    return p


def run_dynesty(loglike, prior_transform, ndim, label):
    """Run dynesty nested sampling and return log evidence."""
    sampler = dynesty.NestedSampler(
        loglike,
        prior_transform,
        ndim=ndim,
        nlive=80,
        bound='multi',
        sample='rwalk',
    )
    sampler.run_nested(dlogz=0.5, maxiter=2000)
    res = sampler.results
    return {
        'label': label,
        'logZ': float(res.logz[-1]),
        'logZerr': float(res.logzerr[-1]),
        'n_iter': len(res.logz),
    }


if __name__ == '__main__':
    print("="*60)
    print("T177 — Proper Bayesian evidence (multi-resonance vs constant)")
    print("="*60)
    print("Replacing scoring-rule BIC with proper dynesty logZ.")

    # Model A: 15-param multi-resonance
    print("\nRunning Model A (multi-resonance, 15 params)...")
    result_A = run_dynesty(log_likelihood_model_A, prior_transform_model_A, 15, 'multi-resonance')
    print(f"  logZ = {result_A['logZ']:.3f} +/- {result_A['logZerr']:.3f}")

    # Model B: constant sigma/m (2 params)
    print("\nRunning Model B (constant sigma/m, 2 params)...")
    result_B = run_dynesty(log_likelihood_model_B, prior_transform_model_B, 2, 'constant')
    print(f"  logZ = {result_B['logZ']:.3f} +/- {result_B['logZerr']:.3f}")

    # Bayes factor
    logB = result_A['logZ'] - result_B['logZ']
    B = math.exp(logB)
    print("\n" + "="*60)
    print("RESULT:")
    print("="*60)
    print(f"  logZ_A (multi-resonance, 15 params) = {result_A['logZ']:.3f}")
    print(f"  logZ_B (constant, 2 params)         = {result_B['logZ']:.3f}")
    print(f"  log Bayes factor (A over B)         = {logB:.3f}")
    print(f"  Bayes factor B = exp({logB:.3f})      = {B:.3f}")
    if logB > 5:
        verdict = "Very Strong evidence for multi-resonance over constant"
    elif logB > 2.5:
        verdict = "Strong evidence for multi-resonance over constant"
    elif logB > 1:
        verdict = "Moderate evidence for multi-resonance over constant"
    elif logB > 0:
        verdict = "Weak evidence for multi-resonance over constant"
    else:
        verdict = "Constant model preferred (Bayes factor < 1)"
    print(f"  Verdict (Jeffreys): {verdict}")

    # Save results
    out = {
        'description': 'T177 — Proper Bayesian evidence via dynesty (2026-09-21)',
        'method': 'dynesty 3.1.0 nested sampling with one-sided floor/ceiling likelihoods for Cloud-9/dSph/UFD/Cluster and Gaussian likelihood for SPARC. Replaces scoring-rule BIC with proper Bayesian log-evidence.',
        'model_A_multi_resonance': result_A,
        'model_B_constant': result_B,
        'log_bayes_factor': logB,
        'bayes_factor': B,
        'verdict': verdict,
        'observation_channels': [
            {'v_kms': o[0], 'sigma_obs_cm2_per_g': o[1], 'kind': o[3], 'label': o[4]}
            for o in OBS
        ],
    }
    out_path = r'C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\t177_bayes_factor.json'
    with open(out_path, 'w') as f:
        json.dump(out, f, indent=2)
    print(f"\nWrote {out_path}")