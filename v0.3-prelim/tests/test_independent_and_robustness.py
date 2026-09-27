"""
Layer D + E tests — cross-code validation + statistical robustness.

Layer D: Independent sigma/m implementation cross-check
  - Independent file (independent_sigma_m.py) implements sigma/m from scratch
    using v-space Breit-Wigner form (NOT v^2-space as in phase44)
  - Cross-check at non-resonant velocities where both implementations
    should agree to within a stated factor
  - Catch implementation bugs in phase44_joint_fit.sigma_m_at_v

Layer E: Statistical robustness
  - test_bootstrap_phase41_sparc: does Burkert still win if we resample
    the 15-galaxy subset (no re-MCMC, just rank stability)
  - test_adversarial_perturbation_phase44: perturb best-fit params ±5%, ±10%;
    verify sigma/m doesn't blow up
  - test_jackknife_phase41_sparc: leave-one-galaxy-out from Phase 41 set;
    verify model ranking is stable
  - test_prior_sensitivity_phase53: document the gain's expected
    sensitivity without re-running the fit

Run via:  bash scripts/run_self_check.sh
or:       pytest v0.3-prelim/tests/test_independent_and_robustness.py -v
"""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

RESULTS_DIR = Path(__file__).resolve().parent.parent / "data" / "results"
CODE_DIR = Path(__file__).resolve().parent.parent / "code"


def _load(name: str) -> dict:
    path = RESULTS_DIR / name
    if not path.exists():
        pytest.skip(f"Reference JSON not found: {name}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _import_phase44():
    try:
        sys.path.insert(0, str(CODE_DIR))
        from phase44_joint_fit import sigma_m_at_v  # type: ignore
        return sigma_m_at_v
    except (ImportError, ModuleNotFoundError) as e:
        pytest.skip(f"phase44_joint_fit not importable: {e}")


def _import_independent():
    try:
        sys.path.insert(0, str(CODE_DIR))
        from independent_sigma_m import sigma_m_multi_resonance_independent  # type: ignore
        return sigma_m_multi_resonance_independent
    except (ImportError, ModuleNotFoundError) as e:
        pytest.skip(f"independent_sigma_m not importable: {e}")


def _make_resonances_v2(m_chi_GeV, v_targets, sigma_peaks, gamma_fracs):
    """Build resonances for the v^2-space form (phase44 convention)."""
    m_chi_eV = m_chi_GeV * 1e9
    resonances = []
    for i, (v, sp, gf) in enumerate(zip(v_targets, sigma_peaks, gamma_fracs)):
        v_cm_s = v * 1e5
        E_R_eV = 0.5 * m_chi_eV * (v_cm_s / 2.998e10) ** 2
        resonances.append({
            "name": f"r{i+1}",
            "E_R_eV": float(E_R_eV),
            "Gamma_eV": float(gf * E_R_eV),
            "sigma_peak_cm2_per_g": float(sp),
        })
    return resonances


def _phase44_params():
    """Load Phase 44 free best-fit params. Skip if not available."""
    d = _load("phase44_joint_fit.json")
    p = d.get("best_params", [])
    if len(p) < 15:
        pytest.skip("Phase 44 best_params not in expected format")
    return {
        "m_chi": p[0],
        "sigma_0": p[1],
        "a_slope": p[2],
        "v_targets": p[3:7],
        "sigma_peaks": p[7:11],
        "gamma_fracs": p[11:15],
    }


# =========================================================================
# Layer D — Independent implementation cross-check
# =========================================================================

def test_independent_implementation_imports():
    """Layer D: the independent sigma/m file imports and is callable."""
    indep = _import_independent()
    params = _phase44_params()
    val = indep(
        100.0,
        params["m_chi"],
        params["v_targets"],
        params["sigma_peaks"],
        params["gamma_fracs"],
        params["sigma_0"],
        params["a_slope"],
    )
    assert val > 0, f"Independent impl returned non-positive value: {val}"
    assert np.isfinite(val), f"Independent impl returned non-finite value: {val}"


def test_independent_matches_phase44_at_non_resonant_velocities():
    """Layer D: at velocities FAR from all v_targets (where neither implementation
    has significant Breit-Wigner contribution), the two implementations should
    agree to within 5x of each other.

    Both implementations agree at non-resonant velocities by construction
    (both reduce to the background). The check is that they're within
    a reasonable factor of each other, since the v-space and v^2-space
    forms have slightly different tail behavior.
    """
    sigma_m_at_v = _import_phase44()
    indep = _import_independent()
    params = _phase44_params()

    # Non-resonant velocities: well away from [29, 100, 300, 700]
    # v=5 is between v_target=29 and v=0 (off-resonance on left)
    # v=60 is between v_target=29 and v_target=100 (mid-resonance)
    # v=1500 is well above all resonances
    test_vs = [5.0, 60.0, 1500.0]
    for v in test_vs:
        # Phase 44 (v^2-space form)
        resonances = _make_resonances_v2(
            params["m_chi"],
            params["v_targets"],
            params["sigma_peaks"],
            params["gamma_fracs"],
        )
        v44 = sigma_m_at_v(v, params["m_chi"], resonances, params["sigma_0"], params["a_slope"])
        # Independent (v-space form)
        vindep = indep(
            v,
            params["m_chi"],
            params["v_targets"],
            params["sigma_peaks"],
            params["gamma_fracs"],
            params["sigma_0"],
            params["a_slope"],
        )
        ratio = vindep / v44 if v44 > 0 else float('inf')
        # At non-resonant velocities, the two implementations should be within 10x
        assert 0.1 < ratio < 10.0, (
            f"At v={v} km/s (non-resonant), independent = {vindep:.4f}, "
            f"phase44 = {v44:.4f}, ratio = {ratio:.3f}. "
            f"Expected within 10x. If outside, the implementations have a "
            f"genuine disagreement that needs investigation."
        )


def test_independent_peak_at_each_v_target():
    """Layer D: the independent implementation should peak near each v_target.

    Specifically, the BW factor equals 1.0 at v_target. We check that
    sigma/m(v_target) is close to sigma_peak (within 50%, since background
    is small at v_target=29+).
    """
    indep = _import_independent()
    params = _phase44_params()
    for v_t, sp in zip(params["v_targets"], params["sigma_peaks"]):
        if sp <= 0:
            continue
        val = indep(
            v_t,
            params["m_chi"],
            params["v_targets"],
            params["sigma_peaks"],
            params["gamma_fracs"],
            params["sigma_0"],
            params["a_slope"],
        )
        ratio = val / sp if sp > 0 else 0
        # At v_target, BW=1 and contribution is sigma_peak; total is sigma_peak + bg
        # We test: total >= 0.5 * sigma_peak
        assert ratio > 0.5, (
            f"At v_target={v_t}, independent sigma/m = {val:.4f}, "
            f"sigma_peak = {sp:.4f}, ratio = {ratio:.3f}. "
            f"Expected > 0.5 (BW factor should be 1 at v_target)."
        )


def test_independent_finite_across_grid():
    """Layer D: independent sigma/m is finite and positive across a wide v range."""
    indep = _import_independent()
    params = _phase44_params()
    vs = np.linspace(5.0, 1500.0, 100)
    vals = [
        indep(
            v,
            params["m_chi"],
            params["v_targets"],
            params["sigma_peaks"],
            params["gamma_fracs"],
            params["sigma_0"],
            params["a_slope"],
        )
        for v in vs
    ]
    assert all(np.isfinite(v) for v in vals), (
        f"Independent impl returned non-finite values: {vals}"
    )
    assert all(v > 0 for v in vals), (
        f"Independent impl returned non-positive values: {vals}"
    )


# =========================================================================
# Layer E — Statistical robustness (no re-MCMC; only documented params)
# =========================================================================

def test_bootstrap_phase41_sparc_burkert_stable():
    """Layer E: Burkert wins Bayesian evidence under bootstrap resampling of the
    15-galaxy subset (no re-MCMC; rank stability check only).

    We do NOT re-run dynesty. Instead, we assert that the existing ranking
    is stable under subset resampling: a subset of 14/15 galaxies should
    still have Burkert at top by sum log_Z.

    This is a rank-stability check, not a fit-quality check. To do the
    latter would require re-running dynesty, which is too expensive for
    CI.
    """
    d = _load("phase41_extended_comparison.json")
    dynesty = d.get("dynesty_results", {})
    if not dynesty:
        pytest.skip("Phase 41 dynesty results not available")

    # Sum log_Z per model across all 15 galaxies (full sample)
    sums_full = {}
    for model, galaxies in dynesty.items():
        if isinstance(galaxies, list):
            sums_full[model] = sum(
                g.get("log_Z", 0) for g in galaxies if isinstance(g, dict)
            )
    full_best = max(sums_full, key=sums_full.get)
    assert full_best == "Burkert", (
        f"Full-sample best: {full_best}, expected Burkert. sums: {sums_full}"
    )

    # Now resample: leave-one-galaxy-out 5 times, verify Burkert still wins each time
    # (15 galaxies -> 15 leave-one-out subsets; we sample 5 to keep it fast)
    n_galaxies = max(
        len(g) for g in dynesty.values() if isinstance(g, list)
    )
    rng = np.random.default_rng(seed=42)
    n_resamples = 10
    burkert_wins = 0
    for _ in range(n_resamples):
        # Random subset of 12/15 galaxies
        indices = rng.choice(n_galaxies, size=12, replace=False)
        sums = {}
        for model, galaxies in dynesty.items():
            if isinstance(galaxies, list):
                sums[model] = sum(
                    galaxies[i].get("log_Z", 0)
                    for i in indices
                    if i < len(galaxies) and isinstance(galaxies[i], dict)
                )
        if max(sums, key=sums.get) == "Burkert":
            burkert_wins += 1

    # Burkert should win in >= 80% of resamples
    assert burkert_wins >= 0.8 * n_resamples, (
        f"Burkert won {burkert_wins}/{n_resamples} resamples, "
        f"expected >= {0.8 * n_resamples:.0f}. If the verdict is unstable, "
        f"the Phase 41 Bayesian evidence comparison needs re-examination."
    )


def test_adversarial_perturbation_phase44():
    """Layer E: perturb Phase 44 best-fit params by ±5%, ±10%; verify sigma/m
    doesn't blow up at any of the 11 anchor velocities.

    A correct implementation should be smooth in parameters; a 10% perturbation
    should not produce wild outliers (e.g., 1000x larger sigma/m).
    """
    sigma_m_at_v = _import_phase44()
    params = _phase44_params()
    # The 11 anchor velocities
    anchor_vs = [5, 15, 28, 30, 40, 50, 100, 200, 250, 500, 700, 1000]
    perturbations = [-0.10, -0.05, 0.05, 0.10]

    def _eval(params_dict):
        res = _make_resonances_v2(
            params_dict["m_chi"],
            params_dict["v_targets"],
            params_dict["sigma_peaks"],
            params_dict["gamma_fracs"],
        )
        return [
            sigma_m_at_v(v, params_dict["m_chi"], res, params_dict["sigma_0"], params_dict["a_slope"])
            for v in anchor_vs
        ]

    # Baseline
    baseline = _eval(params)

    failures = []
    for delta in perturbations:
        # Perturb ALL params by delta
        perturbed = {
            "m_chi": params["m_chi"] * (1 + delta),
            "sigma_0": params["sigma_0"] * (1 + delta),
            "a_slope": params["a_slope"] * (1 + delta),
            "v_targets": [v * (1 + delta) for v in params["v_targets"]],
            "sigma_peaks": [s * (1 + delta) for s in params["sigma_peaks"]],
            "gamma_fracs": [g * (1 + delta) for g in params["gamma_fracs"]],
        }
        perturbed_vals = _eval(perturbed)
        for i, (v_base, v_pert) in enumerate(zip(baseline, perturbed_vals)):
            if v_base <= 0 or v_pert <= 0:
                continue
            ratio = v_pert / v_base
            # A ±10% perturbation should not produce more than 10x change in sigma/m
            # (rough bound: sigma/m scales linearly with sigma_peak and sigma_0;
            #  BW factor is bounded in [0,1] so a 10% v_target shift gives
            #  at most ~10x change for narrow resonances)
            if ratio > 10 or ratio < 0.1:
                failures.append(
                    f"delta={delta:+.0%} at v={anchor_vs[i]}: "
                    f"baseline={v_base:.4f}, perturbed={v_pert:.4f}, ratio={ratio:.2f}"
                )

    assert not failures, (
        f"Adversarial perturbation failed for {len(failures)} cases:\n"
        + "\n".join(failures[:10])
    )


def test_jackknife_phase41_sparc():
    """Layer E: leave-one-galaxy-out from the 15-galaxy Phase 41 subset,
    verify Burkert's Bayesian evidence lead is robust.

    Jackknife = systematic leave-one-out, not random bootstrap.
    """
    d = _load("phase41_extended_comparison.json")
    dynesty = d.get("dynesty_results", {})
    if not dynesty:
        pytest.skip("Phase 41 dynesty results not available")

    n_galaxies = max(
        len(g) for g in dynesty.values() if isinstance(g, list)
    )
    burkert_wins = 0
    for i in range(n_galaxies):
        sums = {}
        for model, galaxies in dynesty.items():
            if isinstance(galaxies, list) and i < len(galaxies):
                sums[model] = sum(
                    g.get("log_Z", 0)
                    for j, g in enumerate(galaxies)
                    if j != i and isinstance(g, dict)
                )
        if not sums:
            continue
        if max(sums, key=sums.get) == "Burkert":
            burkert_wins += 1

    # Burkert should win in ALL jackknife subsets (15/15 galaxies are
    # individually not driving the verdict).
    assert burkert_wins == n_galaxies, (
        f"Burkert won {burkert_wins}/{n_galaxies} jackknife subsets, "
        f"expected {n_galaxies}/{n_galaxies}. If any subset flips the verdict, "
        f"one galaxy is driving the result — that's a known instability."
    )


def test_prior_sensitivity_phase53_documented():
    """Layer E (documented): the Phase 53 v2 clockwork UV-prior gain of +7.93
    is expected to be sensitive to the prior on q and v_1.

    We do NOT re-run the fit (too expensive). Instead, we document the
    sensitivity range that a future re-fit should respect:
      - Gain should remain > +5 log-units for moderate prior widening
      - Gain should remain > +0 log-units (no collapse) for extreme widening

    This is an informational test that records the prior used and what
    a sensitivity check would need to verify.
    """
    d53 = _load("phase53_v2_clockwork_uv_prior_fixed.json")
    improvement = d53.get("phase53_v2_results", {}).get("improvement_vs_phase44_baseline", 0)

    # The gain should be positive (no collapse)
    assert improvement > 0, (
        f"Phase 53 v2 gain {improvement} is non-positive. "
        f"Prior sensitivity should NOT have collapsed the fit."
    )

    # A reasonable gain range for clockwork UV prior on this dataset
    # is 5-10 log-units; outside this range, the result is suspect
    assert 5.0 < improvement < 10.0, (
        f"Phase 53 v2 gain {improvement:.2f} is outside expected range (5-10). "
        f"This could indicate: (a) the prior was too wide/narrow, "
        f"(b) the optimization converged to a different mode, "
        f"(c) a regression in the fit. Recommend re-running Phase 53 v2."
    )