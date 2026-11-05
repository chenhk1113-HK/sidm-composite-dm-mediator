"""
T90.60 -- Barbieri-Giudice-style naturalness measure for the T90 hybrid
posterior (T90.57 KSFR-on, nlive=500) and the v0.8 T41 joint fit.

This addresses reviewer recommendation #6 from the 2026-09-11 review:
"Quantify fine-tuning (e.g., a naturalness measure over ε, α_Y, E_R/Γ_R)
rather than citing log Z alone."

We use a coarse proxy for the full Barbieri-Giudice measure:

    coarse_naturalness_i = log10(prior_width_i) / log10(posterior_width_i)

where:
    prior_width_i = max(prior) / min(prior)  (in linear units)
    posterior_width_i = p84 / p16  (in linear units)

The standard Barbieri-Giudice measure requires evaluating the gradient of
log L at each point in the chain. We don't have raw dynesty samples on
disk (only summary stats), so this coarse proxy is the best we can do
without re-running the sampler.

For a log-flat prior with a Gaussian-ish posterior, the ratio
log(prior)/log(posterior) is approximately proportional to BG sensitivity
to within O(1). Bigger ratio = more fine-tuning.

Reference: Barbieri & Giudice 1988, "Upper Bounds on SUSY Particle Masses
from the Precision Fermi Laboratory Measurements"
(10.1016/0550-3213(88)90062-2, or equivalently the Higgs mass sensitivity
measure used in many SUSY papers).
"""

import json
import os
from pathlib import Path

# 2026-11-05 fix: the data paths below were CWD-relative ('data/results/...'), so this
# module only worked when launched from v0.3-prelim/. Run from the repo root (which is
# how pytest and the release gate invoke it) every read raised FileNotFoundError, and the
# whole module sat on the gate ignore list as if it were an environment problem.
# Anchor to the module's own project root instead.
_RESULTS_DIR = Path(__file__).resolve().parents[1] / "data" / "results"

def coarse_naturalness_from_percentiles(prior_lo_log, prior_hi_log,
                                        p16_log, p50_log, p84_log):
    """
    Compute coarse naturalness ratio.

    For parameters with LOG-FLAT priors (log_m_phi, log_m_chi, log_eps,
    etc.), the naturalness measure is:
        N = (prior_hi_log - prior_lo_log) / (p84_log - p16_log)

    This is the "linear in log-space" form, equivalent to the standard
    Barbieri-Giudice measure for log-flat priors.

    Returns:
        N (float): naturalness ratio.
                   N = 1: posterior fills prior (no fine-tuning)
                   N > 1: posterior is narrower than prior (fine-tuning)
                   N < 1: posterior is wider than prior (unconstrained)
                   N >> 1: severely fine-tuned
    """
    prior_log_width = abs(prior_hi_log - prior_lo_log)
    post_log_width = p84_log - p16_log
    if post_log_width <= 0:
        return float('inf')  # delta-function posterior
    if prior_log_width <= 0:
        return 0.0  # prior is degenerate (shouldn't happen)
    return prior_log_width / post_log_width


# Production-scale thresholds for the T90.57 hybrid chain (10 dimensions).
# A run below these cannot support a fine-tuning verdict, so the producer says so out loud
# instead of returning numbers that look like verdicts.
T90_57_NLIVE_MIN_PRODUCTION = 500
T90_57_SAMPLES_MIN_PRODUCTION = 2000


def analyze_t90_57():
    """Naturalness for the T90.57 hybrid 5-channel posterior.

    Run quality is READ FROM THE ARTIFACT, not assumed. The tracked
    `t90_v57_hybrid_5ch_joint_posterior.json` is a smoke-scale run (nlive=50, ~237 samples,
    wimpy_available=False, 1 of 3 channels satisfied at the median) — it has been that way
    since commit c447e7b (2026-09-14), which replaced the nlive=500 / 4,959-sample production
    run from ed72a35 (2026-09-11). The archived "mu_x EXTREME (N=19.7)" and "m_chi severe"
    verdicts belong to that superseded production run. On a degraded chain the numbers below
    are descriptors of an under-sampled posterior, NOT fine-tuning verdicts; `run_quality`
    and `verdict_scope` carry that boundary so no consumer can drop it.
    """
    fp = _RESULTS_DIR / 't90_v57_hybrid_5ch_joint_posterior.json'
    with open(fp) as f:
        d = json.load(f)

    nlive = d.get('nlive')
    n_samples = d.get('n_samples')
    wimpy_available = d.get('wimpy_available')
    channels = d.get('channel_satisfaction_at_median')
    reasons: list[str] = []
    if isinstance(nlive, int) and nlive < T90_57_NLIVE_MIN_PRODUCTION:
        reasons.append(f"nlive={nlive} < production minimum {T90_57_NLIVE_MIN_PRODUCTION}")
    if isinstance(n_samples, int) and n_samples < T90_57_SAMPLES_MIN_PRODUCTION:
        reasons.append(f"n_samples={n_samples} < production minimum {T90_57_SAMPLES_MIN_PRODUCTION}")
    if wimpy_available is False:
        reasons.append("wimpy_available=False (the WIMpy likelihood arm fell back)")
    if isinstance(channels, dict) and isinstance(channels.get('n_satisfied_3ch'), int):
        if channels['n_satisfied_3ch'] < 3:
            reasons.append(
                f"only {channels['n_satisfied_3ch']} of 3 channels satisfied at the median"
            )
    run_quality = {
        'artifact': fp.name,
        'framework_in_artifact': d.get('framework'),
        'nlive': nlive,
        'n_samples': n_samples,
        'ndim': d.get('ndim'),
        'wall_seconds': d.get('wall_seconds'),
        'wimpy_available': wimpy_available,
        'channel_satisfaction_at_median': channels,
        'degraded_run': bool(reasons),
        'degraded_reasons': reasons,
        'production_thresholds': {
            'nlive_min': T90_57_NLIVE_MIN_PRODUCTION,
            'samples_min': T90_57_SAMPLES_MIN_PRODUCTION,
        },
    }

    # Priors for the T90.57 hybrid (from t90_v57_hybrid_ksfr.py)
    priors = {
        'log_m_chi_GeV': (0.5, 3.0),           # log10(GeV), so 3.16 to 1000 GeV
        'log_m_phi_A_MeV': (-0.5, 2.0),       # 0.316 to 100 MeV
        'g_chi_A': (0.0, 2.0),                # linear
        'log_m_phi_B_MeV': (-0.5, 2.0),       # 0.316 to 100 MeV
        'g_chi_B': (0.0, 2.0),                # linear
        'log_E_R_eV': (0.5, 5.0),             # 3.16 to 100000 eV
        'log_Gamma_R_eV': (-0.5, 3.0),        # 0.316 to 1000 eV
        'log_sigma_0': (-9.5, -4.5),          # 3.16e-10 to 3.16e-5
        'log_alpha_Y': (-9.5, -4.5),          # 3.16e-10 to 3.16e-5
        'log_mu_x': (-15.0, -4.0),            # 1e-15 to 1e-4 mu_N
    }

    results = []
    medians = d['posterior_medians']

    for param in priors:
        if param not in medians:
            continue
        prior_lo_log, prior_hi_log = priors[param]
        p16_log = medians[param]['p16']
        p50_log = medians[param]['median']
        p84_log = medians[param]['p84']

        N = coarse_naturalness_from_percentiles(prior_lo_log, prior_hi_log,
                                                 p16_log, p50_log, p84_log)

        # Natural units interpretation:
        # - N < 0.5: posterior is wider than prior (unconstrained)
        # - N = 1: posterior fills prior (no fine-tuning)
        # - 1 < N < 2: mildly informative
        # - N > 2: fine-tuned (posterior is <50% of prior width)
        # - N > 5: severely fine-tuned (posterior is <20% of prior width)
        # - N > 20: extremely fine-tuned (posterior is <5% of prior width)
        results.append({
            'parameter': param,
            'prior_range_log10': [prior_lo_log, prior_hi_log],
            'posterior_16_50_84_log': (p16_log, p50_log, p84_log),
            'posterior_16_50_84_linear': (10**p16_log, 10**p50_log, 10**p84_log),
            'naturalness_N': N,
            'fine_tuning_level': (
                'unconstrained' if N < 0.5 else
                'mild' if N < 1.5 else
                'moderate' if N < 2.5 else
                'severe' if N < 5 else
                'extreme'
            ),
        })

    label_claimed_nlive_500 = 'nlive=500' in str(run_quality['framework_in_artifact'] or '')
    return {
        'framework': d.get('framework', 'T90.57 hybrid 5-channel'),
        'framework_label_note': (
            "This producer used to hard-code 'T90.57 hybrid (KSFR-on, nlive=500)' regardless of "
            "what the artifact actually said. The label now comes from the artifact itself."
        ),
        'label_matches_artifact': (
            'nlive=500' not in str(d.get('framework', '')) or label_claimed_nlive_500
        ),
        'log_Z': d['log_Z'],
        'log_Z_err': d['log_Z_err'],
        'n_samples': d['n_samples'],
        'naturalness_results': results,
        'run_quality': run_quality,
        'verdict_scope': (
            "Naturalness verdicts from this posterior are NOT supportable while "
            f"degraded_run={run_quality['degraded_run']}: "
            + ("; ".join(run_quality['degraded_reasons']) if run_quality['degraded_reasons']
               else "run meets the production thresholds")
            + ". The coarse measure is prior_width / posterior_width, and an under-sampled chain "
            "inflates posterior width, which biases N DOWNWARD (toward 'mild'), never upward."
        ),
        'method': (
            'coarse proxy: log10(prior_width) / log10(posterior_p84/p16). '
            'Proportional to Barbieri-Giudice within O(1) for log-flat priors. '
            'Cannot distinguish "well-measured" from "fine-tuned" without raw chains.'
        ),
    }


T41_NLIVE_MIN_PRODUCTION = 2000


def analyze_t41_v08():
    """Naturalness for T41 v0.8 (nlive=2000, with Euclid).

    The nlive=2000 claim is checked against the artifact's own `t41_version` block rather than
    taken from the filename.
    """
    fp = str(_RESULTS_DIR / 't41_mediator_mass_joint_fit_t88ce_v08_with_euclid_lensing_and_subhalo_forecast_nlive2000.json')
    with open(fp) as f:
        d = json.load(f)

    tv = d.get('t41_version') or {}
    t41_nlive = tv.get('nlive')
    run_quality = {
        'artifact': Path(fp).name,
        'nlive': t41_nlive,
        'ndim': d.get('ndim') or tv.get('ndim'),
        'dlogz': tv.get('dlogz'),
        'wall_seconds': d.get('wall_seconds'),
        'nlive_claim_matches_artifact': t41_nlive == T41_NLIVE_MIN_PRODUCTION,
        'degraded_run': bool(isinstance(t41_nlive, int) and t41_nlive < T41_NLIVE_MIN_PRODUCTION),
        'production_thresholds': {'nlive_min': T41_NLIVE_MIN_PRODUCTION},
    }

    # Priors for T41 v0.8 (from JSON 'priors' key)
    priors = {p: tuple(d['priors'][p]) for p in d['priors']}

    results = []
    q = d['quantiles_16_50_84']

    for param in priors:
        if param not in q:
            continue
        prior_lo_log, prior_hi_log = priors[param]
        p16_log, p50_log, p84_log = q[param]

        N = coarse_naturalness_from_percentiles(prior_lo_log, prior_hi_log,
                                                 p16_log, p50_log, p84_log)
        results.append({
            'parameter': param,
            'prior_range_log10': [prior_lo_log, prior_hi_log],
            'posterior_16_50_84_log': (p16_log, p50_log, p84_log),
            'posterior_16_50_84_linear': (10**p16_log, 10**p50_log, 10**p84_log),
            'naturalness_N': N,
            'fine_tuning_level': (
                'unconstrained' if N < 0.5 else
                'mild' if N < 1.5 else
                'moderate' if N < 2.5 else
                'severe' if N < 5 else
                'extreme'
            ),
        })

    return {
        'framework': 'T41 v0.8 (with Euclid, nlive=2000)',
        'log_Z': d['log_Z'],
        'n_parameters': len(priors),
        'naturalness_results': results,
        'run_quality': run_quality,
        'method': 'coarse proxy as above',
    }


def main():
    out_dir = str(_RESULTS_DIR)
    os.makedirs(out_dir, exist_ok=True)

    t90 = analyze_t90_57()
    t41 = analyze_t41_v08()

    out = {
        't90_57_naturalness': t90,
        't41_v08_naturalness': t41,
    }

    fp = os.path.join(out_dir, 't90_v60_naturalness_analysis.json')
    with open(fp, 'w') as f:
        json.dump(out, f, indent=2)
    print(f'Wrote {fp}')

    # Print summary
    print()
    print('=' * 78)
    print(f'T90.57 (KSFR-on) naturalness: log Z = {t90["log_Z"]:.3f}')
    print('=' * 78)
    for r in t90['naturalness_results']:
        param = r['parameter']
        N = r['naturalness_N']
        level = r['fine_tuning_level']
        p16, p50, p84 = r['posterior_16_50_84_log']
        print(f'  {param:20s}  N = {N:5.2f}  [{level:11s}]  '
              f'p16/p50/p84 = {p16:7.2f}/{p50:7.2f}/{p84:7.2f}')

    print()
    print('=' * 78)
    print(f'T41 v0.8 naturalness: log Z = {t41["log_Z"]:.3f}')
    print('=' * 78)
    for r in t41['naturalness_results']:
        param = r['parameter']
        N = r['naturalness_N']
        level = r['fine_tuning_level']
        p16, p50, p84 = r['posterior_16_50_84_log']
        print(f'  {param:20s}  N = {N:5.2f}  [{level:11s}]  '
              f'p16/p50/p84 = {p16:7.2f}/{p50:7.2f}/{p84:7.2f}')

    return out


if __name__ == '__main__':
    main()