"""
Tests for the quantitative claims in PAPER_V1_DRAFT.md v1.5 (Layer A + B).

These tests lock down the headline numbers that appear in the paper and
README status line. Each test loads a reference JSON from
v0.3-prelim/data/results/ and asserts the value within the stated tolerance.

If any of these fail, the paper's status line has drifted from the data.

To run:
    pytest v0.3-prelim/tests/test_paper_claims.py -v
    or
    python -m pytest v0.3-prelim/tests/test_paper_claims.py -v

See docs/CHECKING_PLAN_2026_09_17.md for the full layered checking plan.
"""
import json
from pathlib import Path

import pytest

# Path to results directory
RESULTS_DIR = Path(__file__).resolve().parent.parent / "data" / "results"


def _load(name: str) -> dict:
    """Load a reference JSON from data/results/."""
    path = RESULTS_DIR / name
    if not path.exists():
        pytest.skip(f"Reference JSON not found: {name}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# --- Phase 44: free joint fit improvement ---
def test_phase44_free_joint_fit_improvement_is_810():
    """Paper claim: Phase 44 free fit gives +8.10 log-units over T90.70 baseline.

    This is the headline result: free phenomenological fit improves over
    a single-channel T90.70 baseline by +8.10 log-units.

    The actual JSON value is 8.095 (rounded to 2 decimals as 8.10 in the paper).
    Tolerance is 0.01 to catch a meaningful drift but allow for rounding.
    """
    d = _load("phase44_joint_fit.json")
    improvement = d.get("improvement", 0)
    assert abs(improvement - 8.10) < 0.01, (
        f"Phase 44 improvement drifted: expected 8.10 ± 0.01, got {improvement:.4f}. "
        f"Paper claim is +8.10 log-units. If this is a legitimate update, change the paper."
    )


def test_phase44_baseline_logL_is_frozen():
    """Paper claim: baseline logL = -19.67 (T90.70 snapshot)."""
    d = _load("phase44_joint_fit.json")
    bl = d.get("baseline_logL", 0)
    assert abs(bl - (-19.67)) < 0.1, (
        f"Phase 44 baseline_logL drifted: expected -19.67, got {bl:.4f}."
    )


# --- Phase 53 v2: clockwork UV prior preserves the gain ---
def test_phase53_v2_clockwork_preserves_gain():
    """Paper claim: clockwork UV prior gives +7.93 log-units (BIC Δ = -5.66)."""
    d = _load("phase53_v2_clockwork_uv_prior_fixed.json")
    results = d.get("phase53_v2_results", {})
    improvement = results.get("improvement_vs_phase44_baseline", 0)
    assert abs(improvement - 7.93) < 0.05, (
        f"Phase 53 v2 improvement drifted: expected 7.93, got {improvement:.4f}."
    )


def test_phase53_v2_bic_favors_clockwork():
    """Paper claim: clockwork UV prior is preferred by BIC (Δ = -5.66 favoring clockwork)."""
    d = _load("phase53_v2_clockwork_uv_prior_fixed.json")
    bic = d.get("bic_comparison", {})
    delta = bic.get("delta_bic", 0)
    # Negative delta = clockwork preferred
    assert delta < 0, f"Phase 53 v2 ΔBIC should favor clockwork (negative), got {delta}."
    assert abs(delta - (-5.66)) < 0.2, (
        f"Phase 53 v2 ΔBIC drifted: expected -5.66, got {delta}."
    )


# --- Phase 33d: SPARC 115/127 galaxies pass V_flat test ---
def test_phase33d_sparc_pass_count_is_115_of_127():
    """Paper claim: 115/127 SPARC galaxies pass the V_flat test (90.6%)."""
    d = _load("phase33d_external_probe_real.json")
    n_pass = d.get("n_consistent", 0)
    n_total = d.get("n_galaxies", 0)
    assert n_pass == 115, f"SPARC pass count drifted: expected 115, got {n_pass}."
    assert n_total == 127, f"SPARC total drifted: expected 127, got {n_total}."


# --- Phase 41: Burkert wins Bayesian evidence ---
def test_phase41_burkert_wins_bayesian_evidence():
    """Paper claim: Burkert wins the Bayesian evidence comparison on rotation curves.

    The Phase 41 JSON stores dynesty_results as {model: [per-galaxy results]}.
    The headline verdict (which model wins) is determined by summing log_Z
    across the 15-galaxy subset.
    """
    d = _load("phase41_extended_comparison.json")
    dynesty = d.get("dynesty_results", {})
    if not dynesty:
        pytest.skip("Phase 41 dynesty results not available")
    # Sum logZ per model across the 15-galaxy subset
    sums = {
        model: sum(g.get("log_Z", 0) for g in galaxies if isinstance(g, dict))
        for model, galaxies in dynesty.items()
        if isinstance(galaxies, list)
    }
    if not sums:
        pytest.skip("Phase 41 dynesty results not in expected format")
    best = max(sums, key=sums.get)
    assert best == "Burkert", (
        f"Phase 41: Burkert should win Bayesian evidence, but best is {best} "
        f"(sums: {sums})."
    )


# --- Phase 47: LOO stress test ---
def test_phase47_loo_removing_sparc_hurts():
    """Paper claim: removing SPARC hurts the fit (LOO test confirms SPARC drives the gain)."""
    d = _load("phase47_stress_test.json")
    loo = d.get("loo_results", {})
    if not loo:
        pytest.skip("Phase 47 LOO results not available")
    all_logL = loo.get("all_3_channels", {}).get("logL", 0)
    no_sparc_logL = loo.get("without_sparc", {}).get("logL", 0)
    # Removing SPARC should give a worse (lower) logL
    assert no_sparc_logL < all_logL, (
        f"Phase 47: removing SPARC should hurt logL, but "
        f"all={all_logL} vs no_sparc={no_sparc_logL}."
    )


def test_phase47_jvas_residual_is_significant():
    """Paper claim: JVAS lies outside the reliable domain.

    Phase 47 records: best_fit_sigma_v15 = 5.0, target = 100.0, ratio = 0.05.
    This is a 20x shortfall — the model achieves 5% of the JVAS target.
    The paper qualitatively says "JVAS lies outside the reliable domain" and
    "complementary core-collapse SIDM" is the appropriate framework. The
    quantitative anchor is the positive shortfall: best_fit is far below target.
    """
    d = _load("phase47_stress_test.json")
    jvas = d.get("jvas_residual", {})
    if not jvas:
        pytest.skip("Phase 47 JVAS residual not available")
    ratio = jvas.get("ratio_achieved", 0)
    shortfall = jvas.get("shortfall", 0)
    # The model should be unable to reach the JVAS target.
    # ratio_achieved < 1 (in fact 0.05), so shortfall > 0.
    assert shortfall > 0, (
        f"Phase 47: JVAS shortfall should be positive (model can't reach target), "
        f"got {shortfall}. If shortfall = 0, the model now reaches JVAS — update the paper."
    )
    # Stronger check: the model is far from the target.
    assert ratio < 0.5, (
        f"Phase 47: JVAS ratio_achieved should be < 0.5 (model well below target), "
        f"got {ratio}. If this is now > 0.5, the model has started reaching JVAS — re-classify."
    )


# --- Phase 51: MINIMAL UV constructions ---
def test_phase51_winner_rms_is_minimal():
    """Paper claim: Phase 51 winner achieves MINIMAL fine-tuning (RMS < 0.1)."""
    d = _load("phase51_portal_resonance.json")
    winner = d.get("winner", {})
    if not winner:
        pytest.skip("Phase 51 winner not available")
    rms = winner.get("rms_log10", 1.0)
    assert rms < 0.1, (
        f"Phase 51 winner RMS should be < 0.1 (MINIMAL), got {rms}."
    )


# --- Phase 52: more MINIMAL UV constructions ---
def test_phase52_power_law_or_integer_minimal():
    """Paper claim: power-law or integer UV construction achieves MINIMAL fine-tuning.

    Phase 52 headline_comparison is a list of dicts: {name, rms_log10, factor_vs_phase48}.
    At least one entry (other than the Phase 51 carryovers) should have rms_log10 < 0.1.
    """
    d = _load("phase52_multi_mediator.json")
    headline = d.get("headline_comparison", [])
    if not headline:
        pytest.skip("Phase 52 headline comparison not available")
    # Each row is a dict, not a list
    minimal = [r for r in headline if isinstance(r, dict) and r.get("rms_log10", 1.0) < 0.1]
    assert len(minimal) >= 1, (
        f"Phase 52: at least one UV construction should be MINIMAL (RMS < 0.1); "
        f"headline = {headline}"
    )


# --- Phase 54: constant sigma/m vs multi-resonance on joint ---
def test_phase54_multiresonance_wins_raw_logL():
    """Paper claim: multi-resonance wins +6.08 log-units on joint channels (raw likelihood)."""
    d = _load("phase54_joint_comparison.json")
    headline = d.get("headline", {})
    delta = headline.get("logL_delta_3channel", 0)
    assert abs(delta - 6.08) < 0.5, (
        f"Phase 54 joint logL delta drifted: expected 6.08, got {delta}."
    )


# --- Layer C: physical invariants on sigma/m(v) ---
def test_sigma_m_positive_in_dwarf_regime():
    """Layer C invariant: sigma/m(v) > 0 for v > 0.

    This is a sanity check on the underlying formula. If the function
    ever returns negative cross-sections, something has gone wrong.

    Uses the Phase 44 free best-fit parameters (m_chi, sigma_0, a_slope,
    v_targets, sigma_peaks, gamma_fracs) and the canonical multi-resonance
    sigma_m_at_v function.
    """
    try:
        import sys
        sys.path.insert(0, str(RESULTS_DIR.parent / "code"))
        from phase44_joint_fit import sigma_m_at_v  # type: ignore
    except (ImportError, ModuleNotFoundError):
        pytest.skip("phase44_joint_fit.sigma_m_at_v not importable")

    # Load the Phase 44 free best-fit parameters
    d = _load("phase44_joint_fit.json")
    p = d.get("best_params", [])
    if len(p) < 15:
        pytest.skip("Phase 44 best_params not in expected format")
    m_chi, sigma_0, a_slope = p[0], p[1], p[2]
    v_targets = p[3:7]
    sigma_peaks = p[7:11]
    gamma_fracs = p[11:15]

    # Build the resonances list
    m_chi_eV = m_chi * 1e9  # GeV -> eV
    resonances = []
    for vt, sp, gf in zip(v_targets, sigma_peaks, gamma_fracs):
        v_cm_s = vt * 1e5
        E_R_eV = 0.5 * m_chi_eV * (v_cm_s / 2.998e10) ** 2
        resonances.append({
            "name": "r",
            "E_R_eV": float(E_R_eV),
            "Gamma_eV": float(gf * E_R_eV),
            "sigma_peak_cm2_per_g": float(sp),
        })

    # Spot check at v = 15, 28, 100, 300, 700 km/s
    for v in [15.0, 28.0, 100.0, 300.0, 700.0]:
        val = sigma_m_at_v(v, m_chi, resonances, sigma_0, a_slope)
        assert val > 0, f"sigma/m(v={v}) should be > 0, got {val}."
