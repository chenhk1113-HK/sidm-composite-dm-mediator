"""
Tests for T39 (Tier-3 ε/α marginalization joint fit) and T36b (5-config c_vir sweep).
"""
import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
T39_RESULT_PATH = PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "t39_tier3_epsilon_alpha_joint_fit.json"
T36B_RESULT_PATH = PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "t36b_5config_c_vir_sweep.json"


class TestT39Module:
    """t39_tier3_epsilon_alpha_joint_fit.py is importable and structured correctly."""

    def test_t39_importable(self):
        t39 = pytest.importorskip("t39_tier3_epsilon_alpha_joint_fit")
        assert hasattr(t39, "loglike_joint")
        assert hasattr(t39, "prior_transform_4")
        assert hasattr(t39, "main")
        assert hasattr(t39, "LOG_EPSILON_RANGE")
        assert hasattr(t39, "LOG_ALPHA_RANGE")

    def test_t39_4d_prior(self):
        """T39 uses 4D priors covering (sigma_m, a, epsilon, alpha)."""
        t39 = pytest.importorskip("t39_tier3_epsilon_alpha_joint_fit")
        # Range of epsilon: must extend to < 10^-50 to satisfy LZ (full SM decoupling).
        # Range of alpha: must extend to < 10^-26 to satisfy Fermi (full SM decoupling).
        assert t39.LOG_EPSILON_RANGE[0] <= -50.0, (
            f"epsilon prior lower bound {t39.LOG_EPSILON_RANGE[0]} must extend below -50 "
            f"to allow LZ-decoupled regime."
        )
        assert t39.LOG_ALPHA_RANGE[0] <= -25.0, (
            f"alpha prior lower bound {t39.LOG_ALPHA_RANGE[0]} must extend below -25 "
            f"to allow Fermi-decoupled regime."
        )

    def test_t39_likelihood_accepts_4d_theta(self):
        """loglike_joint should accept (log_sigma_m, a, log_epsilon, log_alpha)."""
        t39 = pytest.importorskip("t39_tier3_epsilon_alpha_joint_fit")
        # Default: log_sigma_m=-2 (1 cm²/g), a=1.5 (dimensionless velocity
        # power-law index — NOT km/s), log_epsilon=-4, log_alpha=-3.
        # Note: a is dimensionless; A_RANGE=(-2,2); values outside this
        # range return -inf. Previously this test passed a=20, which is
        # outside range AND unit-confused. Fixed per R11 audit.
        ll = t39.loglike_joint((-2.0, 1.5, -4.0, -3.0))
        assert isinstance(ll, (float, int))
        # Should NOT return -inf for these in-range values
        assert ll > -1e10

    # ---- R12 P1-C regression tests (2026-08-17) ----

    def test_t39_sigma_SI_dimensions(self):
        """R12 P1-C: sigma_SI_from_dark_photon must return a value with
        units of cm^2 (NOT cm^2/g like the legacy epsilon*sigma_m_0).

        Sanity check: for epsilon=1e-5, m_chi=40 GeV, m_A'=10 MeV, alpha_D=0.01:
          sigma_SI = 16 pi alpha_D alpha_em epsilon^2 mu^2 / m_A'^4 in cm^2.
        Expected magnitude: ~10^-32 cm^2 (well above the LZ limit ~10^-46,
        so the model is in tension with LZ at this epsilon — exactly the
        point of the test).
        """
        t39 = pytest.importorskip("t39_tier3_epsilon_alpha_joint_fit")
        sigma = t39.sigma_SI_from_dark_photon(
            epsilon=1e-5, m_chi_GeV=40.0, m_A_prime_MeV=10.0, alpha_D=0.01
        )
        # Must be in cm^2 range: ~1e-32 to 1e-30 for these inputs.
        assert 1e-34 < sigma < 1e-29, (
            f"sigma_SI = {sigma:.3e}; expected ~1e-32 cm^2 (NOT cm^2/g). "
            "If sigma ~ 1e-25 it might be the legacy epsilon*sigma_m_0 mapping."
        )

    def test_t39_sigma_SI_eps_scaling(self):
        """R12 P1-C: sigma_SI must scale as epsilon^2 (NOT epsilon)."""
        t39 = pytest.importorskip("t39_tier3_epsilon_alpha_joint_fit")
        s1 = t39.sigma_SI_from_dark_photon(epsilon=1e-5, m_chi_GeV=40.0, m_A_prime_MeV=10.0)
        s2 = t39.sigma_SI_from_dark_photon(epsilon=1e-6, m_chi_GeV=40.0, m_A_prime_MeV=10.0)
        # Ratio should be (1e-5 / 1e-6)^2 = 100.
        ratio = s1 / s2
        assert 90 < ratio < 110, (
            f"sigma_SI ratio at epsilon 1e-5 vs 1e-6 = {ratio:.2f}; "
            "expected ~100 (epsilon^2 scaling). Linear scaling (legacy "
            "bug) would give ratio = 10."
        )

    def test_t39_sigma_v_dimensions(self):
        """R12 P1-C: sigma_v_from_dark_photon must return cm^3/s.

        Sanity check: at alpha_D=0.01, m_chi=40 GeV, m_A'=10 MeV, the
        natural-units prefactor pi alpha_D^2 / m_chi^2 gives
        sigma_v ~ 7e-25 cm^3/s (well above WIMP miracle 3e-26, indicating
        the model would over-annihilate and under-produce DM at this
        alpha_D — exactly the point).
        """
        t39 = pytest.importorskip("t39_tier3_epsilon_alpha_joint_fit")
        sigma_v = t39.sigma_v_from_dark_photon(
            m_chi_GeV=40.0, m_A_prime_MeV=10.0, alpha_D=0.01
        )
        assert 1e-27 < sigma_v < 1e-20, (
            f"sigma_v = {sigma_v:.3e}; expected ~7e-25 cm^3/s. "
            "If sigma_v ~ 5e3 cm^3/s the legacy alpha*sigma_m^2 was returned."
        )

    def test_t39_sigma_v_forbidden_channel(self):
        """R12 P1-C: when m_A' >= 2 m_chi, annihilation is kinematically
        forbidden; return the floor (1e-30 cm^3/s).
        """
        t39 = pytest.importorskip("t39_tier3_epsilon_alpha_joint_fit")
        # m_A' = 100 GeV with m_chi = 40 GeV: 2 m_chi = 80 GeV, so forbidden.
        sigma_v = t39.sigma_v_from_dark_photon(
            m_chi_GeV=40.0, m_A_prime_MeV=100000.0, alpha_D=0.01
        )
        assert sigma_v <= 1e-25, (
            f"sigma_v at forbidden kinematics = {sigma_v:.3e}; expected floor ~1e-30"
        )


class TestT39Result:
    """If T39 result JSON exists, validate it."""

    def test_t39_result_or_skip(self):
        if not T39_RESULT_PATH.exists():
            pytest.skip("T39 not yet completed; running in background")
        with open(T39_RESULT_PATH) as f:
            data = json.load(f)
        assert "test" in data
        assert data["test"] == "T39_tier3_epsilon_alpha_joint_fit"
        assert "log_Z" in data
        assert "MAP" in data
        assert "verdict" in data

    def test_t39_log_z_improves_or_warns(self):
        """T39's log Z should be substantially better than the catastrophic T30/T32 values."""
        if not T39_RESULT_PATH.exists():
            pytest.skip("T39 not yet completed")
        with open(T39_RESULT_PATH) as f:
            data = json.load(f)
        log_Z = data["log_Z"]
        # T30 catastrophic exclusion was -9207; Tier-3 should improve significantly.
        # We allow either "resolved" (log_Z > -100) or "not resolved" (log_Z < -100),
        # but log_Z must NOT be exactly the catastrophic -9207.
        assert log_Z > -1000, (
            f"T39 log_Z = {log_Z:.3f} is within 1 dex of T30 catastrophic exclusion (-9207). "
            f"Marginalization did not work."
        )

    def test_t39_verdict_classifies(self):
        """T39's verdict must classify as RESOLVED or NOT RESOLVED."""
        if not T39_RESULT_PATH.exists():
            pytest.skip("T39 not yet completed")
        with open(T39_RESULT_PATH) as f:
            data = json.load(f)
        verdict = data.get("verdict", "")
        assert any(kw in verdict.upper() for kw in ("RESOLVED", "RESOLVE", "TENSION")), (
            f"T39 verdict unparseable: {verdict!r}"
        )


class TestT36bModule:
    """t36b_5config_c_vir_sweep.py is importable."""

    def test_t36b_importable(self):
        t36b = pytest.importorskip("t36b_5config_c_vir_sweep")
        assert hasattr(t36b, "C_VIR_RELATIONS")
        assert hasattr(t36b, "main")
        # 5 relations
        assert len(t36b.C_VIR_RELATIONS) == 5


class TestT36bResult:
    """If T36b result JSON exists, validate it."""

    def test_t36b_result_or_skip(self):
        if not T36B_RESULT_PATH.exists():
            pytest.skip("T36b result not yet generated")
        with open(T36B_RESULT_PATH) as f:
            data = json.load(f)
        assert "configs_run" in data
        assert len(data["configs_run"]) == 5

    def test_t36b_five_configs_run(self):
        if not T36B_RESULT_PATH.exists():
            pytest.skip("T36b result not yet generated")
        with open(T36B_RESULT_PATH) as f:
            data = json.load(f)
        labels = [c["config_label"] for c in data["configs_run"]]
        for needed in ("A1", "A2", "A3", "A4", "A5"):
            assert any(label.startswith(needed) for label in labels), (
                f"T36b missing {needed}; ran: {labels}"
            )

    def test_t36b_best_gap_publication_grade(self):
        """The BEST config's gap to Hayashi+ 2025 should be < 1 dex (publication-grade)."""
        if not T36B_RESULT_PATH.exists():
            pytest.skip("T36b result not yet generated")
        with open(T36B_RESULT_PATH) as f:
            data = json.load(f)
        gap = data.get("best_gap_in_dex")
        if gap is None:
            pytest.skip("No best config (no crossings found)")
        assert gap < 1.0, (
            f"Best T36b config ({data['best_config']}) gap = {gap:.2f} dex; "
            f"need < 1 dex for publication-grade."
        )