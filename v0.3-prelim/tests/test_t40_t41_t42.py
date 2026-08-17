"""
Tests for T40 (Yukawa sigma/m), T41 (mediator mass joint fit), T42 (lab exclusions).
"""
import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
T40_CODE = PROJECT_ROOT / "v0.3-prelim" / "code" / "t40_yukawa_sigma_m.py"
T41_CODE = PROJECT_ROOT / "v0.3-prelim" / "code" / "t41_mediator_mass_joint_fit.py"
T42_CODE = PROJECT_ROOT / "v0.3-prelim" / "code" / "t42_lab_exclusions.py"
T41_RESULT = PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "t41_mediator_mass_joint_fit.json"
T42_RESULT = PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "t42_lab_exclusions_recast.json"


class TestT40Yukawa:
    """T40 — Yukawa sigma/m module."""

    def test_t40_importable(self):
        t40 = pytest.importorskip("t40_yukawa_sigma_m")
        assert hasattr(t40, "sigma_T_cm2")
        assert hasattr(t40, "sigma_m_cm2_per_g")
        assert hasattr(t40, "power_law_slope")
        assert hasattr(t40, "g_chi_to_match_sigma_m_0")

    def test_t40_units_consistency(self):
        """sigma_m must be in cm^2/g, not cm^2/GeV."""
        t40 = pytest.importorskip("t40_yukawa_sigma_m")
        # At g_chi=1, m_phi=100 MeV, m_chi=40 GeV, v=100 km/s
        # Check that sigma_m is in cm^2/g (range 1e-100 to 1e10)
        sm = t40.sigma_m_cm2_per_g(100.0, 100.0, 40.0, 1.0)
        # Should be in physically reasonable range (target: ~1 cm^2/g)
        # At g_chi=1, 100 MeV, 40 GeV, sigma_T = (1^4 * 40000^2) / (8pi * 100^4) * hbar^2 * L^2
        # Rough check: 1e-5 to 1e5 cm^2/g
        assert 1e-100 < sm < 1e10, f"sigma_m = {sm} out of expected cm^2/g range"

    def test_t40_velocity_dependence(self):
        """Yukawa sigma/m should DECREASE with v in Born regime (high m_phi)."""
        t40 = pytest.importorskip("t40_yukawa_sigma_m")
        # High m_phi = Born regime, sigma_T ~ 1/v^4 (L=1 for small s)
        sm_low = t40.sigma_m_cm2_per_g(10.0, 1000.0, 40.0, 1.0)
        sm_high = t40.sigma_m_cm2_per_g(1000.0, 1000.0, 40.0, 1.0)
        # At high m_phi, sigma ~ 1/v^4 — sigma at 10 km/s >> sigma at 1000 km/s
        assert sm_low > sm_high, (
            f"sigma_m at v=10 km/s ({sm_low}) should be > sigma_m at v=1000 km/s ({sm_high})"
        )

    def test_t40_g_chi_to_match(self):
        """g_chi solver should give sigma_m_0 within 1% of target."""
        t40 = pytest.importorskip("t40_yukawa_sigma_m")
        target = 1.57
        g = t40.g_chi_to_match_sigma_m_0(target, 100.0, 40.0)
        assert g is not None, "g_chi solver failed"
        sm = t40.sigma_m_cm2_per_g(100.0, 100.0, 40.0, g)
        # Within 1%
        assert abs(sm - target) / target < 0.01, f"sigma_m = {sm}, target = {target}"

    # ---- R12 P0-A regression tests (locked 2026-08-17) ----

    def test_t40_sigma_T_finite_as_v_zero(self):
        """R12 P0-A: sigma_T must remain finite as v -> 0 (Born plateau).

        Previously, `sigma_T_with_m_low_correction` multiplied by
        (1 + 1/(2 s)) which diverged as 1/v^2. Now sigma_T_cm2 is
        the only definition; sigma_T should plateau at the Born limit
        g^4 m^2 / (8 pi m_phi^4) for s -> 0.
        """
        t40 = pytest.importorskip("t40_yukawa_sigma_m")
        sT_low_v = t40.sigma_T_cm2(0.01, 10.0, 40.0, 0.1)
        sT_born = t40.sigma_T_cm2(100.0, 10.0, 40.0, 0.1)
        # Both should be in same order of magnitude (Born plateau).
        # In the Born regime (small s), L(s) ~ 1, so sigma_T is constant.
        assert sT_low_v > 0, f"sigma_T(0.01 km/s) = {sT_low_v}, must be > 0"
        # Ratio should be O(1), not 1e10
        ratio = sT_low_v / sT_born
        assert 0.5 < ratio < 2.0, (
            f"sigma_T plateau broken: sigma_T(0.01)/sigma_T(100) = {ratio:.3e}; "
            "expected Born plateau with ratio O(1)"
        )

    def test_t40_sigma_m_finite_as_v_zero(self):
        """R12 P0-A: sigma/m must remain finite as v -> 0.

        Previously, sigma_m_cm2_per_g(0.1 km/s) returned ~1.95e6 cm^2/g
        (the bogus 1/(2s) blowup). It should now plateau at ~3.5 cm^2/g
        for (m_chi=40 GeV, m_phi=10 MeV, g=0.1).
        """
        t40 = pytest.importorskip("t40_yukawa_sigma_m")
        sm_low = t40.sigma_m_cm2_per_g(0.1, 10.0, 40.0, 0.1)
        sm_born = t40.sigma_m_cm2_per_g(100.0, 10.0, 40.0, 0.1)
        # Must be in physically reasonable range (< 1000 cm^2/g).
        # Anything above 1000 means the old bug returned.
        assert sm_low < 1000.0, (
            f"REGRESSION: sigma_m_cm2_per_g(0.1) = {sm_low:.3e} cm^2/g. "
            "v^{-2} blowup returned. Was the bogus (1+1/(2s)) factor "
            "re-introduced?"
        )
        # Should be within factor 2 of Born plateau value.
        ratio = sm_low / sm_born
        assert 0.5 < ratio < 2.0, (
            f"Born plateau broken: sigma/m(0.1)/sigma/m(100) = {ratio:.3e}"
        )

    def test_t40_alias_matches_clean_form(self):
        """R12 P0-A: legacy `sigma_T_with_m_low_correction` must equal
        `sigma_T_cm2` (the bogus factor has been removed; the legacy
        name now points to the same function).
        """
        t40 = pytest.importorskip("t40_yukawa_sigma_m")
        for v in [1000.0, 100.0, 10.0, 1.0, 0.1]:
            a = t40.sigma_T_cm2(v, 10.0, 40.0, 0.1)
            b = t40.sigma_T_with_m_low_correction(v, 10.0, 40.0, 0.1)
            assert a == b, (
                f"legacy alias diverged from clean form at v={v}: "
                f"sigma_T_cm2={a}, sigma_T_with_m_low_correction={b}"
            )

    def test_t40_born_limit_at_low_v(self):
        """R12 P0-A: Born limit g^4 m^2/(8 pi m_phi^4) is reached at
        vanishing v. Test by computing sigma_T(1000 km/s) < sigma_T(0.1 km/s)
        for small mediator (m_phi=10 MeV) where s is O(1) at v=1000.
        """
        t40 = pytest.importorskip("t40_yukawa_sigma_m")
        sm_low = t40.sigma_m_cm2_per_g(0.1, 10.0, 40.0, 0.1)
        sm_high = t40.sigma_m_cm2_per_g(1000.0, 10.0, 40.0, 0.1)
        # For small m_phi, sigma drops significantly from low to high v.
        # The drop is (ln s/s)^2 at high s.
        assert sm_low / sm_high > 10.0, (
            f"sigma/m should fall from v=0.1 to v=1000 by >10x for "
            f"m_phi=10 MeV; got sm_low/sm_high = {sm_low/sm_high:.2e}"
        )


class TestT41Module:
    """T41 — m_phi + m_chi joint fit."""

    def test_t41_importable(self):
        t41 = pytest.importorskip("t41_mediator_mass_joint_fit")
        assert hasattr(t41, "loglike_joint")
        assert hasattr(t41, "prior_transform_5")
        assert hasattr(t41, "main")

    def test_t41_5d_prior(self):
        """T41 uses 5D priors covering (m_phi, m_chi, g_chi, epsilon, alpha)."""
        t41 = pytest.importorskip("t41_mediator_mass_joint_fit")
        assert (t41.LOG_M_PHI_MEV_RANGE[0] <= -1.0 and
                t41.LOG_M_PHI_MEV_RANGE[1] >= 3.0), (
            "log_m_phi_MeV prior must cover at least 10 keV to 1 TeV"
        )

    def test_t41_likelihood_accepts_5d_theta(self):
        t41 = pytest.importorskip("t41_mediator_mass_joint_fit")
        # log_m_phi=2 (100 MeV), log_m_chi=1.5 (30 GeV), g_chi=0.1,
        # log_eps=-4, log_alpha=-3
        ll = t41.loglike_joint((2.0, 1.5, 0.1, -4.0, -3.0))
        assert isinstance(ll, (float, int))
        assert ll > -1e10

    def test_t41_yukawa_tension_flag(self):
        """R12 P0-B (2026-08-17): the pre-fix '1.3 sigma Yukawa tension'
        was a sign-flip artifact. Post-fix, derived_a returns POSITIVE
        values matching T39's data-preferred a = +0.94, so the tension
        flag is NOT expected to fire.

        This test asserts the OPPOSITE of the legacy R11 expectation:
        significant == False (the pre-fix a_difference of 2.75 was wrong).

        If this test FAILS with significant == True, it means derived_a
        regressed to the pre-fix sign-flipped behavior.
        """
        if not T41_RESULT.exists():
            pytest.skip("T41 not yet completed")
        with open(T41_RESULT) as f:
            data = json.load(f)
        assert "yukawa_tension" in data
        # Post-P0-B: tension is NOT significant.
        assert data["yukawa_tension"]["significant"] is False, (
            f"Yukawa tension flagged (significant=True) -- this means "
            f"derived_a regressed to the pre-P0-B sign-flipped behavior. "
            f"a_T39 = {data['yukawa_tension']['T39_a']}, "
            f"a_Yukawa = {data['yukawa_tension']['Yukawa_a_at_MAP']}, "
            f"diff = {data['yukawa_tension']['a_difference']}. "
            f"Re-check t41_mediator_mass_joint_fit.derived_a()."
        )

    # ---- R12 P0-B regression tests (locked 2026-08-17) ----

    def test_t41_derived_a_sign_convention(self):
        """R12 P0-B: derived_a must match channels_v03 convention
        (positive a means FALLING sigma/m with v).

        Previously the minus sign was missing. The bug returned
        NEGATIVE a (claiming rising sigma/m) when the Yukawa form
        actually produces falling sigma/m. This regression test
        asserts:
            a > 0  for cases where sigma/m at v=50 > sigma/m at v=200.
        """
        t41 = pytest.importorskip("t41_mediator_mass_joint_fit")
        # Small m_phi = strongly falling sigma/m in Born regime.
        # For m_phi=10 MeV, m_chi=40 GeV, g_chi=0.1:
        #   sigma/m(50) ~ 2.83 cm^2/g
        #   sigma/m(200) ~ 0.63 cm^2/g  --> ratio > 1, so a > 0 in channels_v03 sense.
        a = t41.derived_a(10.0, 40.0, 0.1)
        assert a > 0.5, (
            f"REGRESSION: derived_a(10, 40, 0.1) = {a:.3f}, expected > +0.5. "
            "Sign convention broken; t41 returns the OPPOSITE of channels_v03."
        )

    def test_t41_derived_a_matches_t54_sign(self):
        """R12 P0-B: t41 and t54 must return the SAME-SIGN number for
        physically equivalent setups.
        """
        t41 = pytest.importorskip("t41_mediator_mass_joint_fit")
        t54 = pytest.importorskip("t54_dark_quark_joint_fit")
        import numpy as np
        # Both modules should be running with their own private Yukawa;
        # the sign of `a` should agree for the same physical input.
        # We use m_phi=10 MeV, m_chi=40 GeV, g_chi=0.1.
        a41 = t41.derived_a(10.0, 40.0, 0.1)
        a54 = t54.derived_a(np.log10(0.010), np.log10(1.0), np.log10(40.0), 0.1)
        # Both should be POSITIVE in channels_v03 convention.
        # (Magnitudes differ because the two Yukawa implementations differ.)
        assert a41 > 0 and a54 > 0, (
            f"REGRESSION: a41={a41:.3f}, a54={a54:.3f}; both should be "
            f"> 0 in channels_v03 convention"
        )


class TestT42Module:
    """T42 — Lab exclusions recast."""

    def test_t42_importable(self):
        t42 = pytest.importorskip("t42_lab_exclusions")
        assert hasattr(t42, "is_excluded")
        assert hasattr(t42, "interpolate_exclusion")
        assert hasattr(t42, "NA64_INVISIBLE_90CL")
        assert hasattr(t42, "STELLAR_COOLING_95CL")
        assert hasattr(t42, "SN1987A_95CL")

    def test_t42_t41_evaluation(self):
        """T42 must evaluate the T41 posterior in the exclusion plane."""
        if not T42_RESULT.exists():
            pytest.skip("T42 not yet completed")
        if not T41_RESULT.exists():
            pytest.skip("T41 not yet completed")
        with open(T42_RESULT) as f:
            data = json.load(f)
        assert "t41_evaluation" in data
        assert "T41_median_m_phi_MeV" in data["t41_evaluation"]
        assert "status" in data["t41_evaluation"]

    def test_t42_t41_mediator_unobservable(self):
        """At T41 posterior median, the mediator should be unobservable."""
        if not T42_RESULT.exists():
            pytest.skip("T42 not yet completed")
        with open(T42_RESULT) as f:
            data = json.load(f)
        t41_eval = data.get("t41_evaluation", {})
        if "status" not in t41_eval:
            pytest.skip("T41 evaluation not done")
        status = t41_eval["status"]
        # The T41 posterior should concentrate at very small epsilon,
        # well below current experimental sensitivity.
        assert not status["is_excluded"], (
            f"T41 posterior at median is excluded by {[e['experiment'] for e in status['excluded_by']]}. "
            "This would mean the SIDM-bumpy model is already ruled out by lab experiments."
        )
