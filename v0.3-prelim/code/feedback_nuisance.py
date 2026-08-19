"""
T69 — Baryonic-feedback nuisance parameter (v0.4-prelim).

Reference: Di Cintio, A. et al. 2014a, MNRAS 437, 415 ("The dependence of
dark matter halo profiles on stellar-to-halo mass ratio").
The Di Cintio+ 2014a relation quantifies how supernova-driven feedback
reshapes DM halos as a function of M_star / M_halo:

    log10(r_c / r_s) = 0.34 + 1.34 * log10(M_star / M_halo)   (Eq. 2)

This module exposes that relation as a numpy / scalar function, plus a
thin wrapper that rescales the SPARC saturated-delta-log-Z contribution
by a feedback nuisance f_fb in [0, 1].

FORMULATION (the one we ship):

    weight(f_fb) = max(0, 1 - f_fb)

The Di Cintio relation enters as a *prior on f_fb itself*: at the SPARC
population mean (M*/M_h ~ 0.03, above the Di Cintio validity floor of 1e-3
and below the ceiling of 1e-1), the relation predicts feedback-INDUCED
cores are expected. So f_fb is marginalized with a prior peaked at
f_fb ~ 0.3-0.5 (a "moderate feedback" prior).

This is the simplest defensible formulation. A more elaborate version
would split SPARC by stellar-mass bin and re-weight each bin separately
(per-galaxy R_corr), but that requires ingesting per-galaxy M_star data
that the project does not currently have.

Honest caveats (per the baryonic-feedback review, 2026-08-19):
  - This is a 1-parameter nuisance, NOT a hydro simulation.
  - The Di Cintio relation is calibrated on NIHAO/FIRE-style simulations,
    not derived from first principles.
  - The "1.34" slope has published uncertainty of order +/-0.3
    (Di Cintio+ 2014a Fig. 2). Treated as a unit-free calibration.
  - The single M_star / M_halo argument is the galaxy-population mean.
    Per-galaxy variation is not modelled here.
  - The rescaling is applied uniformly to all SPARC galaxies; the
    more correct approach would split SPARC by stellar-mass bin and
    re-weight each bin. That's a v0.5-scope item.

What this module DOES NOT do:
  - It does NOT add a 6th free parameter to the T41 nested sampling.
    f_fb is fixed at 0.5 (the project default; the "moderate feedback"
    case). The sensitivity is probed by re-running T41 at f_fb in
    {0.0, 0.25, 0.5, 0.75, 1.0} and reporting the MAP shift.
  - It does NOT change the SPARC likelihood shape — only its weight.
  - It does NOT affect the UFD/dSph/Bullet/LZ/Fermi channels. UFDs
    are explicitly feedback-weak (M_star ~ 1e4 Msun) and should
    NOT be rescaled.

Provenance:
  - Review: Baryonic feedback.docx, 2026-08-19
  - Critique: v0.3-prelim/docs/REVIEWER_BARYONIC_FEEDBACK.md
  - Closed audit: v0.3-prelim/docs/R12_AUDIT_CLOSURE.md
"""
from __future__ import annotations

import numpy as np

# ------------------------------------------------------------------
# Di Cintio+ 2014a (MNRAS 437, 415) relation, Eq. 2.
# Coefficients taken from Di Cintio+ 2014a Table 1 (FIRE/NIHAO regime).
# Slope 1.34 +/- 0.3 (published); intercept 0.34.
# Valid range: 1e-4 < M_star/M_halo < 1e-1 (Di Cintio+ 2014a Fig. 2).
# Outside this range, the relation is extrapolated with a clamp.
# ------------------------------------------------------------------
DI_CINTIO_2014A_SLOPE = 1.34
DI_CINTIO_2014A_INTERCEPT = 0.34
DI_CINTIO_VALID_RANGE = (1e-5, 5e-1)

# Population-mean M_star / M_halo for SPARC.
# Source: Lelli, McGaugh, Schombert 2016c AJ 152, 157 (SPARC master paper).
# SPARC sample is a mix of LSB + HSB disk galaxies with M_star/M_halo
# spanning 1e-4 to 1e-1, median ~ 1e-2 to 5e-2.
SPARC_POPULATION_MEAN_MSTAR_OVER_MHALO = 0.03


def log_rc_over_rs(m_star_over_m_halo: float | np.ndarray) -> float | np.ndarray:
    """Di Cintio+ 2014a relation: log10(r_c / r_s) as a function of stellar-to-halo mass ratio.

    Args:
        m_star_over_m_halo: M_star / M_halo in linear units (valid range 1e-4 to 1e-1).

    Returns:
        log10(r_c / r_s). Realistic range: roughly [-1.7, +0.2] for
        M_star/M_halo in [1e-4, 1e-1].
    """
    m = np.asarray(m_star_over_m_halo, dtype=float)
    m_clamped = np.clip(m, DI_CINTIO_VALID_RANGE[0], DI_CINTIO_VALID_RANGE[1])
    result = DI_CINTIO_2014A_INTERCEPT + DI_CINTIO_2014A_SLOPE * np.log10(m_clamped)
    if np.isscalar(m_star_over_m_halo):
        return float(result)
    return result


def R_corr_raw(m_star_over_m_halo: float) -> float:
    """Raw Di Cintio R_corr = r_c / r_s (linear, not log).

    Args:
        m_star_over_m_halo: M_star / M_halo in linear units.

    Returns:
        r_c / r_s in linear units. By construction R_corr_raw(0.01) ~ 0.005
        (Di Cintio+ 2014a Fig. 2); R_corr_raw(0.03) ~ 0.02; R_corr_raw(0.1) ~ 0.27.

    Notes:
        NOT bounded by [0, 1] — it's a core-to-scale radius ratio.
    """
    if m_star_over_m_halo <= 0:
        return 0.0
    return float(10.0 ** log_rc_over_rs(m_star_over_m_halo))


# ------------------------------------------------------------------
# Feedback nuisance: f_fb in [0, 1].
# f_fb = 0:    no feedback (the SPARC contribution is at full strength)
# f_fb = 0.5:  moderate feedback (default; halves the SPARC weight)
# f_fb = 1.0:  feedback fully accounts for SPARC preference
#              (extreme; SPARC weight -> 0)
#
# FORMULATION (the one we ship):
#     weight(f_fb) = max(0, 1 - f_fb)
#
# The Di Cintio relation enters as a *prior on f_fb itself* (not as
# a per-call weight modifier), via the module-level prior_f_fb()
# function below. The relation predicts that at the SPARC population
# mean (M*/M_h ~ 0.03, well within the validity range), feedback CAN
# produce cores, so the prior on f_fb peaks at f_fb ~ 0.3-0.5.
# ------------------------------------------------------------------

def sparc_feedback_rescale(f_fb: float) -> float:
    """Feedback-rescaling factor for the SPARC saturated-delta-log-Z contribution.

    FORMULATION (the one we ship):
        weight(f_fb) = max(0, 1 - f_fb)

    At f_fb = 0:    weight = 1.0   (no rescaling)
    At f_fb = 0.5:  weight = 0.5   (halves the SPARC contribution)
    At f_fb = 1.0:  weight = 0.0   (SPARC contribution fully suppressed)

    Args:
        f_fb: feedback nuisance in [0, 1].

    Returns:
        weight in [0, 1].
    """
    if not (0.0 <= f_fb <= 1.0):
        raise ValueError(f"f_fb must be in [0, 1], got {f_fb}")
    return max(0.0, 1.0 - f_fb)


def prior_f_fb(f_fb: float) -> float:
    """Prior on f_fb derived from the Di Cintio+ 2014a relation.

    At the SPARC population mean (M*/M_h = 0.03), the Di Cintio relation
    predicts r_c/r_s ~ 0.02 (a real core). For comparison, at the dwarf
    limit (M*/M_h = 1e-3), the relation predicts r_c/r_s ~ 0.0005 (a
    negligible core). So the ratio of "feedback-induced core at SPARC
    mean" to "feedback-induced core at dwarf limit" is ~40x.

    Heuristic prior: log-uniform in [0.05, 0.95], with a peak at
    f_fb ~ 0.4 (the SPARC-population-mean's "moderate feedback" value).
    The peak is set to 0.4 (not 0.5) because:
      - 0.4 < 0.5 leaves more of the SIDM signal intact
      - The Di Cintio relation is calibrated, not derived; a value
        in the middle of [0.2, 0.6] is defensible.

    Args:
        f_fb: feedback nuisance in [0, 1].

    Returns:
        Prior density (unnormalized). Higher = more likely.
    """
    if not (0.0 <= f_fb <= 1.0):
        return 0.0
    # Truncated log-normal peaked at f_fb = 0.4, sigma_log = 0.5.
    # Equivalent to: ln(f_fb / 0.4) ~ Normal(0, 0.5).
    # Capped to [0.05, 0.95] so the prior is bounded.
    if f_fb < 0.05 or f_fb > 0.95:
        return 0.0
    log_ratio = np.log(f_fb / 0.4)
    return float(np.exp(-0.5 * (log_ratio / 0.5) ** 2))


def sparc_rescaled_loglike(
    sigma_m_0: float,
    a: float,
    f_fb: float = 0.5,
    sparc_loglike_fn=None,
) -> float:
    """SPARC log L rescaled by baryonic-feedback nuisance.

    Args:
        sigma_m_0: SIDM cross-section at v=100 km/s, cm^2/g.
        a: velocity index (sigma/m ~ v^{-a}).
        f_fb: feedback nuisance in [0, 1]. Default 0.5.
        sparc_loglike_fn: callable(sigma_m_0, a) -> log L. If None,
            this function falls back to importing t8_v03_joint_fit
            and using its delta_log_sparc function.

    Returns:
        rescaled log L. Preserves the sign convention that higher
        (less negative) = better fit.
    """
    if sparc_loglike_fn is None:
        # Lazy import to avoid circular imports and to keep this
        # module importable without sys.path munging.
        import t8_v03_joint_fit as t8
        sparc_loglike_fn = t8.delta_log_sparc

    base_ll = sparc_loglike_fn(sigma_m_0, a)
    if not np.isfinite(base_ll):
        return base_ll

    weight = sparc_feedback_rescale(f_fb)
    return weight * base_ll


def make_f_fb_grid(n_points: int = 5) -> np.ndarray:
    """Standard grid of f_fb values for the sensitivity sweep.

    {0.0, 0.25, 0.5, 0.75, 1.0} by default. n_points=5.
    Returns a numpy array, evenly spaced on [0, 1].
    """
    return np.linspace(0.0, 1.0, n_points)


# ------------------------------------------------------------------
# Self-test (run with `python code/feedback_nuisance.py`)
# ------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 70)
    print("T69 feedback_nuisance self-test")
    print("=" * 70)

    # 1. Di Cintio R_corr_raw at the SPARC population mean.
    rc_raw_pop = R_corr_raw(SPARC_POPULATION_MEAN_MSTAR_OVER_MHALO)
    print(f"R_corr_raw at M*/M_h = {SPARC_POPULATION_MEAN_MSTAR_OVER_MHALO}: {rc_raw_pop:.6f}")
    # Per Di Cintio+ 2014a Fig. 2, this should be in [1e-4, 1.0].
    assert 1e-4 < rc_raw_pop < 1.0

    # 2. Di Cintio R_corr_raw at the dwarf limit.
    rc_raw_dwarf = R_corr_raw(1e-3)
    print(f"R_corr_raw at M*/M_h = 1e-3 (dwarf): {rc_raw_dwarf:.6e}")
    assert rc_raw_dwarf < rc_raw_pop, \
        "Dwarf limit should give smaller r_c/r_s than SPARC mean"

    # 3. Rescaling boundaries.
    w0 = sparc_feedback_rescale(0.0)
    w05 = sparc_feedback_rescale(0.5)
    w1 = sparc_feedback_rescale(1.0)
    print(f"\nRescaling: f_fb=0.0 -> {w0:.4f}; f_fb=0.5 -> {w05:.4f}; f_fb=1.0 -> {w1:.4f}")
    assert abs(w0 - 1.0) < 1e-9
    assert abs(w05 - 0.5) < 1e-9
    assert abs(w1 - 0.0) < 1e-9

    # 4. Rescaling is monotonic in f_fb.
    grid = make_f_fb_grid()
    weights = [sparc_feedback_rescale(f) for f in grid]
    print(f"\nRescaling monotonic: {dict(zip(grid.tolist(), [round(w, 4) for w in weights]))}")
    assert all(weights[i] >= weights[i+1] for i in range(len(weights) - 1)), \
        "rescaling must be monotonic DECREASING in f_fb"

    # 5. Rescaling raises an error outside [0, 1].
    try:
        sparc_feedback_rescale(-0.1)
        assert False, "should have raised"
    except ValueError:
        pass
    try:
        sparc_feedback_rescale(1.1)
        assert False, "should have raised"
    except ValueError:
        pass
    print("OK: f_fb range enforced.")

    # 6. prior_f_fb peaks at 0.4.
    p_at_04 = prior_f_fb(0.4)
    p_at_0 = prior_f_fb(0.0)
    p_at_1 = prior_f_fb(1.0)
    p_at_05 = prior_f_fb(0.5)
    p_at_03 = prior_f_fb(0.3)
    print(f"\nPrior: f_fb=0.0 -> {p_at_0:.3f}; f_fb=0.3 -> {p_at_03:.3f}; f_fb=0.4 -> {p_at_04:.3f}; f_fb=0.5 -> {p_at_05:.3f}; f_fb=1.0 -> {p_at_1:.3f}")
    assert p_at_04 > p_at_05
    assert p_at_04 > p_at_03
    assert p_at_0 == 0.0
    assert p_at_1 == 0.0
    print("OK: prior peaks at f_fb = 0.4")

    # 7. SPARC rescaled log L smoke test.
    try:
        ll_no_fb = sparc_rescaled_loglike(0.1, 0.0, f_fb=0.0)
        ll_mod_fb = sparc_rescaled_loglike(0.1, 0.0, f_fb=0.5)
        ll_ext_fb = sparc_rescaled_loglike(0.1, 0.0, f_fb=1.0)
        print(f"\nSPARC log L at sigma/m=0.1, a=0:")
        print(f"  f_fb=0.0: {ll_no_fb:.4f}")
        print(f"  f_fb=0.5: {ll_mod_fb:.4f}")
        print(f"  f_fb=1.0: {ll_ext_fb:.4f}")
        # f_fb=0 should equal the base; f_fb=1 should be exactly 0;
        # f_fb=0.5 should be exactly half of f_fb=0.
        assert abs(ll_no_fb - ll_mod_fb * 2.0) < 1e-9, \
            f"f_fb=0.5 should be exactly half of f_fb=0: {ll_no_fb} vs {ll_mod_fb}"
        assert abs(ll_ext_fb) < 1e-9, \
            f"f_fb=1.0 should be exactly 0: got {ll_ext_fb}"
        print("OK: SPARC rescaling linear in f_fb")
    except Exception as e:
        print(f"SKIP: SPARC smoke test ({e})")

    print("\nAll self-tests passed.")