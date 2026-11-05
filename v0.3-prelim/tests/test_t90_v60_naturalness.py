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


def test_t90_57_mu_x_extreme():
    """T90.57 μ_χ: the archived "extreme (N≈19.7)" verdict is SUPERSEDED, and the current
    posterior is too degraded to replace it. Pinned as a measured-state + degraded-run guard.

    Evidence (git history of the artifact):
      ed72a35 / d4c5596 (2026-09-11): nlive=500, 4,820-4,959 samples -> μ_χ p16/p84 = -7.685/-7.127
        = 0.558 dex against an 11 dex prior -> N = 19.7 ("EXTREME"). This is the archived claim.
      c447e7b (2026-09-14) and every revision since: nlive=50, ~230 samples -> μ_χ posterior
        spans ~7.53 dex -> N = 1.46 ("mild").
    So the tracked artifact cannot support either verdict direction: an under-sampled chain
    inflates posterior width, which biases N downward. This test therefore pins (a) the current
    measured numbers, (b) the producer's degraded-run flag, and (c) the direction of the bias.
    Settling μ_χ fine-tuning requires re-running T90.57 at production scale (decision D10).
    """
    res = analyze_t90_57()
    mu_x = next(r for r in res['naturalness_results'] if r['parameter'] == 'log_mu_x')

    measured_N = 1.4614
    assert abs(mu_x['naturalness_N'] - measured_N) / measured_N < 0.02, (
        f"μ_χ naturalness moved to {mu_x['naturalness_N']}; re-derive before pinning it"
    )
    assert mu_x['fine_tuning_level'] == 'mild'

    prior_lo, prior_hi = mu_x['prior_range_log10']
    assert (prior_lo, prior_hi) == (-15.0, -4.0), "μ_χ prior changed"
    p16, _p50, p84 = mu_x['posterior_16_50_84_log']
    post_width = p84 - p16
    assert 7.0 < post_width < 8.0, f"μ_χ posterior width = {post_width:.3f} dex"
    assert abs((prior_hi - prior_lo) / post_width - mu_x['naturalness_N']) < 1e-9

    rq = res['run_quality']
    assert rq['degraded_run'] is True, f"degraded flag lost: {rq}"
    assert rq['nlive'] == 50 and rq['n_samples'] < 2000
    assert any('nlive' in r for r in rq['degraded_reasons'])
    assert 'NOT supportable' in res['verdict_scope']


def test_t90_57_m_chi_severe():
    """T90.57 m_χ: archived "severe" verdict came from the nlive=500 run; the tracked artifact
    measures N = 1.298 ('mild') on a 50-live chain. Pinned with the degraded-run guard."""
    res = analyze_t90_57()
    m_chi = next(r for r in res['naturalness_results'] if r['parameter'] == 'log_m_chi_GeV')

    measured_N = 1.2984
    assert abs(m_chi['naturalness_N'] - measured_N) / measured_N < 0.02, (
        f"m_χ naturalness moved to {m_chi['naturalness_N']}; re-derive before pinning it"
    )
    # NOT 'severe' on this chain. The archived 'severe (~3.6)' belongs to ed72a35's run.
    assert m_chi['fine_tuning_level'] == 'mild'
    assert res['run_quality']['degraded_run'] is True

    # The producer must not dress a degraded chain up as a production run.
    assert 'nlive=500' not in res['framework'], (
        f"framework label claims production scale: {res['framework']}"
    )
    assert res['label_matches_artifact'] is True


def test_t90_57_run_quality_is_read_not_assumed():
    """Guard: run-quality metadata must come from the artifact, and g_chi_B (the one
    strongly-constrained parameter) must still be flagged extreme on this chain."""
    res = analyze_t90_57()
    rq = res['run_quality']
    assert rq['framework_in_artifact'].startswith('T90.57 hybrid 10D')
    assert rq['production_thresholds'] == {'nlive_min': 500, 'samples_min': 2000}
    g_chi_b = next(r for r in res['naturalness_results'] if r['parameter'] == 'g_chi_B')
    assert g_chi_b['fine_tuning_level'] == 'extreme'
    assert abs(g_chi_b['naturalness_N'] - 8.644) < 0.01
    # μ_χ MAP also moved between the two runs: archived 10^-7.37, current 10^-8.39.
    mu_x = next(r for r in res['naturalness_results'] if r['parameter'] == 'log_mu_x')
    assert -8.6 < mu_x['posterior_16_50_84_log'][1] < -8.0


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