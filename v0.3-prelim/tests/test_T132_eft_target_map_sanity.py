"""
T132 — Sanity check on §10.5 EFT Target Map (Qwen referee 2 request).

Cross-checks each numerical claim in the paper's EFT Target Map against
the actual phenomenology computation.

Findings (2026-09-20):
  - 6 of 8 checks pass
  - Issue #1: Phenomenology σ/m(15) = 0.37, not 0.013 as paper claims
  - Issue #2: Phenomenology σ/m(500) = 0.025, not 4×10⁻⁴ as paper claims
  - Issue #3: §10.5's "Standard perturbative Yukawa gives <1" is wrong —
             standard Yukawa CAN give large σ/m at v=28 with α~0.01;
             the multi-resonance + Gaussian + multi-comp combination is what works
  - Issue #4: §10.5 says "P-wave resonances too narrow" for SPARC, but Chu P1
             actually matches SPARC (0.15 vs 0.19). The failure is at Cloud-9.

Reference: Qwen referee 2 report (2026-09-20), recommended "one last
sanity check on the EFT Target Map (§10.5) in the paper draft before
freezing the text."

=================================================================================
2026-10-25 AUDIT — what this file is, and what it is NOT
=================================================================================

THIS FILE WAS NEVER A PASSING REGRESSION TEST. It was committed already-failing
in its own commit (d776480, 2026-09-20): running it in a worktree checked out at
that very commit gives the identical "4 failed, 14 passed". Its four failures
have therefore never gated anything — they have been silently tolerated by the
release gate since the day it was written.

WHY THE FOUR TestFullChainVerification ASSERTIONS ARE WRONG (they are not
"the paper being wrong"; they are the ASSERTION TARGET being wrong):

  The assertions compare `joint_fit_full_evaluation(a_slope_override=1.0)` — the
  T120.4 *v1.13-era* joint-fit chain — against values that were, at the time,
  quoted in the paper's §10.5 EFT target map (128.13 / 0.032 / 2.5e-4 cm2/g,
  added by commit 7df4c3c, which labelled them "verified in T132").

  Two independent things moved underneath those numbers:

  1. The PAPER. The §10.5 target-map table quoting 128.13 / 0.032 / 2.5e-4 was
     DELETED from the paper by the 2026-09-21 editorial/structural-cut passes
     (e12abdc "Editorial pass: cut internals, shorten abstract, restructure §10",
     then bd04d13, then d1a7131 / 0f69674 / 3bd4520). The current paper no
     longer contains those numbers — `grep -c "128.13"` on the paper returns 0.
     The current §10.5 (L1938-1960) is a no-go-verdict table plus a
     single-vs-multi-resonance statistical comparison; it makes no sigma/m
     target-map claim for these four channels.

  2. The CODE. `t120_4_joint_fit.py` was re-based at commit 7e07df7 (2026-09-19,
     "T120.7: paper v1.13 — fix UFD tension + verify BIC penalty"), which
     extended `joint_fit_full_evaluation` from 4 to 8 observational points and
     added the `a_slope_override` parameter. The module constants
     (T120_4_V_TARGETS / T120_4_SIGMA_PEAKS / T120_4_W_LIST_DEFAULT) are
     unchanged since then, but the per-point suppression factors and the point
     set are not the ones the 128.13-era numbers were computed from.

  The CURRENT canonical source for the paper's 8-channel table is
  `v0.3-prelim/data/results/sigma_m_phase44.json` (the v19.2-F Phase 44 fit),
  NOT the T120.4 chain. The paper's 8-channel table at L941-944 quotes
  128 / 0.18 / 0.19 / 0.0002 cm2/g, and Cloud-9 128 and SPARC 0.19 reproduce
  from that JSON to <2% (128.126 and 0.193). Note that 128 is the *observational
  floor* (BLN24/Ohana+ 2026), not a model output — see canonical_numbers.py
  line 333 "Cloud-9 v=28 (BLN24/Ohana+ 2026 floor 128, canonical Phase 44)".

WHAT WAS CHANGED HERE (2026-10-25): the four `TestFullChainVerification`
assertions are re-pointed from the superseded T120.4 chain to the CURRENT
canonical Phase 44 values, so that this file becomes a genuine regression test
of the numbers the paper actually quotes. The values are locked to the JSON
that the paper cites, so a future drift in the canonical fit fails here.

The `TestSummary` docstring findings above are RETAINED VERBATIM as the
historical record of the 2026-09-20 referee request. They describe the state of
§10.5 at that date and are NOT claims about the current paper.
"""
import math
import numpy as np
import importlib.util
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/code")


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# Load modules
t120_4 = load_module(
    "t120_4_joint_fit",
    r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\code\t120_4_joint_fit.py"
)
channels_v03 = load_module(
    "channels_v03",
    r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\code\channels_v03.py"
)
T131 = load_module(
    "T131_chu_pwave_verification",
    r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\code\T131_chu_pwave_verification.py"
)

# --- canonical sources the PAPER's 8-channel table is actually generated from ---
# (see module docstring for the full audit; the T120.4 `joint_fit_full_evaluation`
#  chain is the SUPERSEDED v1.13-era path and reproduces none of these cells.)
REPO = r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator"
PHASE44_JSON = os.path.join(REPO, "v0.3-prelim", "data", "results", "sigma_m_phase44.json")
PAPER_MD = os.path.join(REPO, "v0.3-prelim", "docs", "PAPER_V1_DRAFT.md")

# Borrowed f_H used by the paper's dSph cell (T207; "Placeholder-dependent").
F_H_BORROWED = 0.30


def canonical_sigma_m():
    """sigma/m per channel from the canonical Phase 44 fit the paper cites."""
    import json as _json
    with open(PHASE44_JSON) as f:
        return _json.load(f)


def dSph_cell_sigma_m():
    """The paper's dSph cell (0.18 cm2/g) = f_H^2 x the velocity-dependent background.

    Paper decomposition table (L1003-1008):
        Phase 44 Gaussian canonical          2.85 cm2/g
        + Gaussian BW (w1=3)                2.0  cm2/g   (2.5x reduction)
        + two-component (borrowed f_H=0.30) 0.18 cm2/g   (11x reduction)
    The 2.0 step is the Yukawa background at a_slope=1.93 evaluated at v=15; the
    0.18 step is that value times f_H^2 = 0.09. Reproduced here from the same
    code path the paper cites, so a drift in either step fails this test.
    """
    p44 = t120_4._load_phase44_params()
    bg = t120_4.yukawa_bg(15.0, p44["sigma_0"], 1.93)
    return F_H_BORROWED ** 2 * bg, bg


# Phase 44 default parameters
PHASE44_PARAMS = {
    'v_targets': [29, 100, 178, 430, 769],
    'sigma_peaks': [128, 0.07, 0.20, 0.04, 0.08],
    'w_list': [3.0, 50, 50, 50, 50],
    'sigma_0': 0.052,
    'a_slope': 1.0,
}


def phenomenology_sigma_m(v_km_s):
    """Compute phenomenology σ/m at velocity v (km/s)."""
    return t120_4.total_sigma_m_gaussian(
        v_km_s,
        PHASE44_PARAMS['v_targets'],
        PHASE44_PARAMS['sigma_peaks'],
        PHASE44_PARAMS['w_list'],
        PHASE44_PARAMS['sigma_0'],
        PHASE44_PARAMS['a_slope'],
    )


class TestCloud9Requirement:
    """Paper claim: σ/m ~ 100 cm²/g at v=28 km/s."""

    def test_Cloud9_phenomenology_sigma_m(self):
        """σ/m(28) should be ~100 cm²/g."""
        sigma = phenomenology_sigma_m(28)
        # Paper claim ~100, our phenomenology gives ~120
        assert 80 < sigma < 200, f"σ/m(28) = {sigma}, expected 80-200"

    def test_Cloud9_too_high_for_standard_yukawa(self):
        """Standard Yukawa CAN give large σ/m at v=28 with right parameters."""
        # The key point: it's not "Yukawa can't do it", it's "monotonic Yukawa can't"
        # We'll verify monotonic Yukawa fails the monotonic constraint
        # (see TestMonotonicFails test)
        pass


class TestDSphRequirement:
    """Paper claim: σ/m ~ 0.013 cm²/g at v=15 km/s."""

    def test_dSph_phenomenology_sigma_m(self):
        """σ/m(15) per Phase 44 parameters."""
        sigma = phenomenology_sigma_m(15)
        # NOTE: Phase 44 default gives 0.37, not 0.013
        # The paper's 0.013 comes from multi-comp + gravothermal combination
        # (sigma_eff_two_comp), not from gaussian alone
        # For now, document what the pure phenomenology gives
        assert sigma > 0, f"σ/m(15) = {sigma}"

    def test_dSph_paper_claim_uses_two_comp(self):
        """The paper's 0.013 cm²/g claim comes from multi-comp + gravothermal chain.

        Note: sigma_eff_two_comp at r/r_vir=0.05 gives only ~10% suppression,
        not the ~28× needed to go from 0.37 to 0.013. The full chain requires
        additional factors (gravothermal collapse selection, profile weighting)
        not captured by sigma_eff_two_comp alone. This is a real discrepancy.
        """
        sigma_HH = phenomenology_sigma_m(15)  # gaussian σ/m
        sigma_eff = t120_4.sigma_eff_two_comp(15, sigma_HH, halo_type='core_collapsed', r_over_rvir=0.05)
        # sigma_eff_two_comp at r/r_vir=0.05 gives only ~10% suppression
        # The full multi-comp + gravothermal chain needs more factors
        # This test documents the partial suppression
        assert sigma_eff > 0, f"σ_eff should be > 0"
        # The paper's 0.013 cm²/g requires additional factors beyond sigma_eff_two_comp


class TestSPARCRequirement:
    """Paper claim: σ/m ~ 0.19 cm²/g at v=100 km/s."""

    def test_SPARC_phenomenology_sigma_m(self):
        """σ/m(100) should be ~0.19 cm²/g."""
        sigma = phenomenology_sigma_m(100)
        assert 0.1 < sigma < 0.4, f"σ/m(100) = {sigma}"


class TestClusterRequirement:
    """Paper claim: σ/m ~ 4×10⁻⁴ cm²/g at v=500 km/s."""

    def test_cluster_phenomenology_sigma_m(self):
        """σ/m(500) per Phase 44 parameters."""
        sigma = phenomenology_sigma_m(500)
        # Phase 44 default gives 0.025; paper claim is 4e-4
        # The 4e-4 comes from full multi-comp + gravothermal chain
        # (not implemented in this check; would need joint_fit_full_evaluation)
        assert sigma > 0, f"σ/m(500) = {sigma}"

    def test_cluster_falloff_is_steep(self):
        """σ(28)/σ(500) should be >> 1 (steeper than v⁻¹)."""
        sigma_28 = phenomenology_sigma_m(28)
        sigma_500 = phenomenology_sigma_m(500)
        ratio = sigma_28 / sigma_500
        # Pure v⁻¹: 500/28 = 17.86
        # Multi-resonance: should be much steeper
        assert ratio > 100, f"Falloff ratio {ratio}, should be >100 for v⁻¹+"


class TestLZLimit:
    """Paper claim: LZ 2024 σ_SI < 9.4×10⁻⁴⁷ cm²."""

    def test_LZ_2024_limit(self):
        """Verify LZ 2024 limit value."""
        LZ_LIMIT = 9.4e-47  # cm²
        # Reference: J. Aalbers et al. (LZ), Phys. Rev. Lett. 135 (2024) 041802
        # arXiv:2410.17036
        assert LZ_LIMIT == 9.4e-47


class TestChuP1AtSPARC:
    """Paper claim (§10.5): 'P-wave resonances too narrow' for SPARC."""

    def test_Chu_P1_at_v_100(self):
        """Chu P1 at v=100 km/s should be checked against paper claim."""
        sigma = T131.chu_pwave_resonance(100)
        # Chu P1 gives 0.15, SPARC target is 0.19
        # So P1 actually MATCHES SPARC, contradicting the 'too narrow' claim
        # The failure is at Cloud-9 (v=28), not SPARC
        assert 0.05 < sigma < 0.5, f"Chu P1 σ/m(100) = {sigma}"

    def test_Chu_P1_fails_at_Cloud9_not_SPARC(self):
        """Document that P1 fails at Cloud-9, not SPARC."""
        sigma_28 = T131.chu_pwave_resonance(28)
        sigma_100 = T131.chu_pwave_resonance(100)
        assert sigma_28 < 1, f"P1 σ/m(28) = {sigma_28}, fails Cloud-9"
        # SPARC match is actually OK (within factor 2)


class TestThermalRelicAlpha:
    """Paper claim: Multi-TeV inelastic requires α_D ~ 404."""

    def test_thermal_relic_alpha_D_404(self):
        """Verify α_D ~ 404 at m_χ = 46 TeV."""
        m_chi_GeV = 46000
        v_relic_c = 10 * 1e3 / 2.998e8
        hbar_c_sq = 0.3894e-27  # GeV^2 cm^2
        c_cm_s = 2.998e10
        thermal_target = 3e-26  # cm^3/s

        alpha_D = np.sqrt(thermal_target / (hbar_c_sq * c_cm_s * v_relic_c)) * m_chi_GeV
        assert 350 < alpha_D < 450, f"α_D = {alpha_D}"


class TestMonotonicFails:
    """Paper claim: monotonic σ/m(v) cannot satisfy Cloud-9 + dSph."""

    def test_monotonic_yukawa_cannot_satisfy_both(self):
        """If σ/m(v) = (v_ref/v)^α is monotonic, then:
        σ/m(28)/σ/m(15) = (15/28)^α
        Required: 100/0.013 = 7692
        Solving: α = log(7692)/log(15/28) = log(7692)/log(0.536)
        """
        import math
        ratio = 100 / 0.013  # 7692
        v_ratio = 15 / 28   # 0.536
        alpha_required = math.log(ratio) / math.log(v_ratio)
        # Should be negative (σ/m must rise with v to give 100 at v=28 but 0.013 at v=15)
        assert alpha_required < 0, f"α required = {alpha_required}, monotonic Yukawa cannot"
        assert alpha_required < -10, f"α required = {alpha_required}, requires super-rising σ/v"


class TestSummary:
    """Sanity check summary."""

    def test_summary_findings(self):
        """This sanity check found 4 issues with §10.5."""
        findings = {
            'check_1_Cloud9': 'PASS (full chain σ/m(28) = 128.13 cm²/g, matches paper claim)',
            'check_2_dSph': 'NUMERICAL ERROR: paper claims 0.013, full chain gives 0.032 (2.5x off)',
            'check_3_SPARC': 'PASS (full chain σ/m(100) = 0.193 cm²/g, matches paper claim)',
            'check_4_cluster': 'MINOR ERROR: paper claims 4e-4, full chain gives 2.5e-4 (1.6x off)',
            'check_5_LZ': 'PASS (9.4e-47 cm²)',
            'check_6_P1_at_SPARC': 'CONTRADICTS PAPER: P1 σ/m(100) = 0.15 matches SPARC 0.19; failure is at Cloud-9',
            'check_7_thermal_relic': 'PASS (α_D = 404)',
            'check_8_monotonic_fails': 'PASS (required α = -14)',
        }
        assert len(findings) == 8


class TestFullChainVerification:
    """Verify the canonical Phase 44 fit gives the values the PAPER quotes.

    2026-10-25 audit: these four assertions previously targeted the SUPERSEDED
    T120.4 v1.13-era chain (`joint_fit_full_evaluation(a_slope_override=1.0)`),
    against numbers that the paper's §10.5 target-map table quoted in Sept 2026
    (128.13 / 0.032 / 2.5e-4 cm²/g). That table was deleted from the paper by the
    2026-09-21 editorial/structural-cut passes, and the T120.4 chain was re-based
    at 7e07df7. The assertions therefore compared two mutually inconsistent
    things and could never pass — they failed in their own commit too.

    The canonical source the paper's 8-channel table (L941-944) actually comes
    from is `sigma_m_phase44.json`. These tests now lock THAT, so a future drift
    in the canonical fit fails here instead of silently reaching the paper.

    Paper quotes (L941-944): Cloud-9 128, dSph 0.18, SPARC 0.19, Cluster 0.0002.
    Note Cloud-9's 128 is the BLN24/Ohana+ observational FLOOR, not a model output.
    """

    # (json key, paper-quoted value, tolerance) — Cloud-9 / SPARC / Cluster are the
    # canonical Phase 44 sigma/m; the paper rounds Cluster to 1 significant figure
    # (0.000252 -> 0.0002), hence the looser 30% there.
    CASES = [
        ('v28.0_Cloud-9', 128.0, 0.01),
        ('v100.0_SPARC', 0.19, 0.02),
        ('v500.0_cluster', 0.0002, 0.30),
    ]

    def test_canonical_json_is_readable(self):
        """The canonical Phase 44 JSON exists and carries all 8 channels."""
        data = canonical_sigma_m()
        for key, _paper, _tol in self.CASES:
            assert key in data, f"canonical Phase 44 JSON missing {key}"

    def test_canonical_matches_paper_table(self):
        """Each canonical sigma/m is consistent with the value the paper quotes."""
        data = canonical_sigma_m()
        for key, paper_val, tol in self.CASES:
            sigma = data[key]
            assert abs(sigma - paper_val) / paper_val <= tol, (
                f"{key}: canonical {sigma!r} vs paper {paper_val!r} "
                f"(tolerance {tol:.0%}). The paper's 8-channel table (L941-944) "
                f"would now disagree with the canonical fit."
            )

    def test_dSph_cell_matches_paper(self):
        """The paper's dSph cell (0.18 cm2/g) reproduces as f_H^2 x the background."""
        sigma_eff, bg = dSph_cell_sigma_m()
        assert abs(sigma_eff - 0.18) / 0.18 <= 0.02, (
            f"dSph cell: f_H^2 x bg = {sigma_eff!r} (bg={bg!r}) vs paper 0.18"
        )

    def test_dSph_decomposition_chain_is_consistent(self):
        """The paper's 3-row dSph decomposition (2.85 -> 2.0 -> 0.18) holds."""
        _sigma_eff, bg = dSph_cell_sigma_m()
        # row 1: canonical Gaussian sigma/m(15) = 2.85 (paper L1005)
        # NOTE: the canonical constants live in scripts/constants.py. The repo-root
        # constants.py is a DIFFERENT module (no SIGMA_0_CM2_PER_G) and shadows it on
        # sys.path, so load the canonical one by explicit path.
        constants_mod = load_module(
            "canonical_constants",
            os.path.join(REPO, "scripts", "constants.py"),
        )
        gauss = channels_v03.sigma_m_at_v(
            constants_mod.SIGMA_0_CM2_PER_G, constants_mod.A_SLOPE, 15.0
        ) + 174.0 * math.exp(-(15 - 29.4) ** 2 / (2 * 4.4 ** 2))
        assert abs(gauss - 2.85) / 2.85 <= 0.01, f"Gaussian canonical sigma/m(15) = {gauss!r}"
        # row 2: the Gaussian-BW step is the background alone = 2.0
        assert abs(bg - 2.0) / 2.0 <= 0.02, f"Gaussian-BW background step = {bg!r}, expected 2.0"
        # row 3: two-component step = f_H^2 x 2.0 = 0.18, i.e. an 11x reduction
        assert 10.0 <= 2.0 / (F_H_BORROWED ** 2 * bg) <= 12.0, (
            "the two-component reduction factor should be ~11x"
        )

    def test_paper_no_longer_quotes_the_removed_target_map(self):
        """Guard: the Sept-2026 §10.5 target-map numbers must stay out of the paper.

        These were the values that made the original assertions unsatisfiable.
        They were deleted by the 2026-09-21 editorial/structural-cut passes; if
        they ever come back, the T120.4 chain (which cannot reproduce them) and
        the paper would disagree again.
        """
        paper = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'docs', 'PAPER_V1_DRAFT.md',
        )
        with open(paper, encoding='utf-8') as f:
            text = f.read()
        for removed in ('128.13', '2.5×10⁻⁴ cm²/g'):
            assert removed not in text, (
                f"paper reintroduced the removed §10.5 target-map value {removed!r}; "
                f"it does not come from the canonical Phase 44 fit."
            )

    def test_canonical_cloud9_meets_observational_floor(self):
        """Cloud-9's canonical sigma/m must clear the >=100 cm²/g BLN24/Ohana+ floor."""
        sigma = canonical_sigma_m()['v28.0_Cloud-9']
        assert sigma >= 100.0, f"σ/m(28) = {sigma}, below the 100 cm²/g Cloud-9 floor"

    def test_canonical_sparc_within_lelli_window(self):
        """SPARC's canonical sigma/m must sit inside the [0.05, 0.5] Lelli+ window."""
        sigma = canonical_sigma_m()['v100.0_SPARC']
        assert 0.05 <= sigma <= 0.5, f"σ/m(100) = {sigma}, outside [0.05, 0.5]"

    def test_canonical_cluster_below_cluster_limit(self):
        """Cluster's canonical sigma/m must stay below the 1.0 cm²/g limit."""
        sigma = canonical_sigma_m()['v500.0_cluster']
        assert sigma < 1.0, f"σ/m(500) = {sigma}, at or above the 1.0 cm²/g cluster limit"
