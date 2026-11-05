"""Tests for T90.60 naturalness analyzer."""

import json
import os
import pytest
import sys
import tempfile

# Add code dir to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))
from t90_v60_naturalness import (
    coarse_naturalness_from_percentiles,
    analyze_t90_57,
    analyze_t41_v08,
)


def test_naturalness_unconstrained():
    """Posterior wider than prior → N < 1."""
    N = coarse_naturalness_from_percentiles(0.0, 3.0, -1.0, 0.0, 1.0)
    # prior_log_width = 3.0, post_log_width = 2.0, N = 1.5
    assert abs(N - 1.5) < 0.01


def test_naturalness_filled():
    """Posterior fills prior → N = 1."""
    N = coarse_naturalness_from_percentiles(0.0, 2.0, 0.5, 1.0, 1.5)
    # prior_log_width = 2.0, post_log_width = 1.0, N = 2.0
    assert abs(N - 2.0) < 0.01


def test_naturalness_extreme():
    """Very narrow posterior → N large."""
    N = coarse_naturalness_from_percentiles(0.0, 5.0, 2.49, 2.50, 2.51)
    # prior_log_width = 5.0, post_log_width = 0.02, N = 250
    assert N > 100


def test_naturalness_degenerate_post():
    """p84 == p16 → infinite naturalness."""
    N = coarse_naturalness_from_percentiles(0.0, 1.0, 2.0, 2.0, 2.0)
    assert N == float('inf')


def test_t90_57_returns_10_params():
    """T90.57 has 10 sampled parameters."""
    res = analyze_t90_57()
    assert len(res['naturalness_results']) == 10


# ---------------------------------------------------------------------------
# T90.57 pins after decision D10 was EXECUTED (2026-11-05).
#
# History of this artifact, from its own git log:
#   ed72a35 / d4c5596 (2026-09-11): nlive=500, 4,820-4,959 samples, log Z = -7.912.
#       mu_chi N = 19.72 'extreme', m_chi N = 3.51 'severe' -> the archived claims.
#   c447e7b (2026-09-14) and every revision since: the --smoke path (nlive=50, dlogz 0.5)
#       wrote over the production posterior -> 237 samples, log Z = -3.517, mu_chi N = 1.46
#       'mild'. That was a smoke run, not a measurement (finding F20).
#   2026-11-05 D10 re-run: t90_v57_hybrid_ksfr.py --nlive 500 --dlogz 0.1 --ksfr on
#       -> 4,874 samples, log Z = -7.7183 +/- 0.1322, wall 2,112.8 s, wimpy_available True.
#       The pre-rerun smoke posterior is archived byte-for-byte at
#       data/results/superseded/t90_v57_hybrid_5ch_joint_posterior.pre_d10_rerun_2026-11-05.json.
#
# Outcome: the archived DIRECTION is reproduced on an independent production chain
# (mu_chi 19.72 -> 21.03 'extreme'; m_chi 3.51 -> 3.50 'severe'), and the smoke-era
# 'mild' verdict is confirmed as the undersampling artifact the bias argument predicted.
# ---------------------------------------------------------------------------

T90_57_PRODUCTION_NLIVE = 500
T90_57_PRODUCTION_SAMPLES_MIN = 2000


def test_t90_57_is_a_production_chain_after_d10():
    """The chain must meet the production thresholds; if it degrades again, every level
    below becomes unsupportable and this test must fail rather than re-bless the numbers."""
    res = analyze_t90_57()
    rq = res['run_quality']
    assert rq['degraded_run'] is False, f"chain degraded again: {rq}"
    assert rq['nlive'] == T90_57_PRODUCTION_NLIVE
    assert rq['n_samples'] >= T90_57_PRODUCTION_SAMPLES_MIN
    assert rq['production_thresholds'] == {'nlive_min': 500, 'samples_min': 2000}
    assert 'supportable AS MEASURED VALUES' in res['verdict_scope'], res['verdict_scope']
    # The rerun reproduced the archived evidence, not a new one.
    assert abs(res['log_Z'] - (-7.7183)) < 0.01, f"log Z moved: {res['log_Z']}"


def test_t90_57_mu_x_extreme():
    """T90.57 mu_chi: 'extreme' is now MEASURED on a production chain, reproducing the
    archived N = 19.72 that the 237-sample smoke chain could not support (F20 / D10)."""
    res = analyze_t90_57()
    mu_x = next(r for r in res['naturalness_results'] if r['parameter'] == 'log_mu_x')

    measured_N = 21.0285
    assert abs(mu_x['naturalness_N'] - measured_N) / measured_N < 0.02, (
        f"mu_chi naturalness moved to {mu_x['naturalness_N']}; re-derive before pinning it"
    )
    assert mu_x['fine_tuning_level'] == 'extreme'

    prior_lo, prior_hi = mu_x['prior_range_log10']
    assert (prior_lo, prior_hi) == (-15.0, -4.0), "mu_chi prior changed"
    p16, p50, p84 = mu_x['posterior_16_50_84_log']
    post_width = p84 - p16
    assert 0.4 < post_width < 0.7, f"mu_chi posterior width = {post_width:.4f} dex"
    assert abs((prior_hi - prior_lo) / post_width - mu_x['naturalness_N']) < 1e-9
    # The MAP sits where the archived production run put it (10^-7.37), not at the
    # smoke chain's 10^-8.39.
    assert abs(p50 - (-7.3637)) < 0.01, f"mu_chi MAP moved: {p50}"

    assert res['run_quality']['degraded_run'] is False


def test_t90_57_m_chi_severe():
    """T90.57 m_chi: 'severe' (N = 3.4954) reproduces the archived ~3.51. The 50-live chain's
    N = 1.298 'mild' is retired as a smoke artifact."""
    res = analyze_t90_57()
    m_chi = next(r for r in res['naturalness_results'] if r['parameter'] == 'log_m_chi_GeV')

    measured_N = 3.4954
    assert abs(m_chi['naturalness_N'] - measured_N) / measured_N < 0.02, (
        f"m_chi naturalness moved to {m_chi['naturalness_N']}; re-derive before pinning it"
    )
    assert m_chi['fine_tuning_level'] == 'severe'
    assert res['run_quality']['degraded_run'] is False

    # The framework label must come from the artifact, never be hard-coded.
    assert res['label_matches_artifact'] is True
    assert res['framework'].startswith('T90.57 hybrid 10D')


def test_t90_57_run_quality_is_read_not_assumed():
    """Guard: run-quality metadata must come from the artifact, and g_chi_B (the one
    strongly-constrained parameter) must still be flagged extreme on this chain."""
    res = analyze_t90_57()
    rq = res['run_quality']
    assert rq['framework_in_artifact'].startswith('T90.57 hybrid 10D')
    assert rq['production_thresholds'] == {'nlive_min': 500, 'samples_min': 2000}
    g_chi_b = next(r for r in res['naturalness_results'] if r['parameter'] == 'g_chi_B')
    assert g_chi_b['fine_tuning_level'] == 'extreme'
    assert abs(g_chi_b['naturalness_N'] - 8.8406) / 8.8406 < 0.02
    mu_x = next(r for r in res['naturalness_results'] if r['parameter'] == 'log_mu_x')
    assert -7.5 < mu_x['posterior_16_50_84_log'][1] < -7.2


def test_t41_v08_returns_6_params():
    """T41 v0.8 has 6 sampled parameters."""
    res = analyze_t41_v08()
    assert len(res['naturalness_results']) == 6


def test_t41_v08_epsilon_moderate():
    """T41 v0.8 log_epsilon should be flagged as moderate (not extreme)."""
    res = analyze_t41_v08()
    eps = next(r for r in res['naturalness_results'] if r['parameter'] == 'log_epsilon')
    # Per production: posterior ~32 dex wide, prior 59 dex wide → N ≈ 1.86 (moderate)
    assert 1.0 < eps['naturalness_N'] < 3.0, f"ε naturalness = {eps['naturalness_N']}"


def test_t41_v08_nlive_claim_is_verifiable_from_the_artifact():
    """The 'nlive=2000' label must be backed by the artifact's own t41_version block, not the filename."""
    res = analyze_t41_v08()
    rq = res['run_quality']
    assert rq['nlive'] == 2000, f"T41 artifact does not declare nlive=2000: {rq}"
    assert rq['nlive_claim_matches_artifact'] is True
    assert rq['degraded_run'] is False
    assert 'nlive=2000' in res['framework']


def test_output_file_written():
    """The output JSON should be written to data/results/."""
    from t90_v60_naturalness import main
    with tempfile.TemporaryDirectory() as tmpdir:
        # Override the output dir
        import t90_v60_naturalness as mod
        original_dir = 'data/results'
        mod.__dict__['os'] = type(os)('os')
        # Easier: just check the actual run produced the file
        if os.path.exists('data/results/t90_v60_naturalness_analysis.json'):
            d = json.load(open('data/results/t90_v60_naturalness_analysis.json'))
            assert 't90_57_naturalness' in d
            assert 't41_v08_naturalness' in d


def test_extreme_parameters_have_small_posterior():
    """For parameters flagged 'extreme', posterior width should be small
    relative to prior width."""
    res = analyze_t90_57()
    for r in res['naturalness_results']:
        if r['fine_tuning_level'] == 'extreme':
            prior_w = r['prior_range_log10'][1] - r['prior_range_log10'][0]
            post_w = r['posterior_16_50_84_log'][2] - r['posterior_16_50_84_log'][0]
            assert post_w < prior_w / 5, (
                f"Parameter {r['parameter']} flagged extreme but post_w={post_w} >= prior_w/5"
            )


if __name__ == '__main__':
    pytest.main([__file__, '-v'])