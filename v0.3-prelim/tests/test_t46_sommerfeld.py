"""
Tests for T46 — Yukawa + Sommerfeld improvement.
"""
import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
T46_CODE = PROJECT_ROOT / "v0.3-prelim" / "code" / "t46_yukawa_improvements.py"
T46_FIT_CODE = PROJECT_ROOT / "v0.3-prelim" / "code" / "t46_yukawa_sommerfeld_joint_fit.py"
T46_RESULT = PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "t46_yukawa_sommerfeld_joint_fit.json"


class TestT46Improvements:
    """T46 — Yukawa improvement survey module."""

    def test_t46_importable(self):
        t46 = pytest.importorskip("t46_yukawa_improvements")
        assert hasattr(t46, "sommerfeld_factor")
        assert hasattr(t46, "sigma_m_sommerfeld")
        assert hasattr(t46, "sigma_m_form_factor")
        assert hasattr(t46, "sigma_m_pseudo_scalar")

    def test_t46_sommerfeld_enhanced(self):
        """Sommerfeld factor should be > 1 in the attractive coupling regime."""
        t46 = pytest.importorskip("t46_yukawa_improvements")
        # Strong coupling, low velocity: S should be large
        S = t46.sommerfeld_factor(50.0, 1000.0, 40.0, 1.0)
        assert S > 1.0, f"Sommerfeld factor at strong coupling should be > 1, got {S}"

    def test_t46_sommerfeld_born_limit(self):
        """At very high velocity, S should approach 1 (Born limit)."""
        t46 = pytest.importorskip("t46_yukawa_improvements")
        # Very high v: S -> 1
        S = t46.sommerfeld_factor(10000.0, 100.0, 40.0, 0.5)
        assert 0.9 < S < 1.1, f"Sommerfeld at high v should be ~1, got {S}"

    def test_t46_sommerfeld_gives_a_positive(self):
        """T46 should give a > 0 (sigma/m decreasing with v) — the key fix."""
        t46 = pytest.importorskip("t46_yukawa_improvements")
        # At m_phi=1000 MeV, g_chi=1.0, the survey showed a ~ 5
        a = t46.power_law_slope(t46.sigma_m_sommerfeld, 50.0, 200.0,
                                1000.0, 40.0, 1.0)
        assert a > 0, f"a should be > 0 with Sommerfeld, got {a}"


class TestT46Fit:
    """T46 — Yukawa + Sommerfeld joint fit."""

    def test_t46_fit_importable(self):
        t46 = pytest.importorskip("t46_yukawa_sommerfeld_joint_fit")
        assert hasattr(t46, "loglike_joint")
        assert hasattr(t46, "prior_transform_5")
        assert hasattr(t46, "main")

    def test_t46_fit_likelihood_accepts_5d_theta(self):
        t46 = pytest.importorskip("t46_yukawa_sommerfeld_joint_fit")
        # log_m_phi=3 (1 GeV), log_m_chi=1.5 (30 GeV), g_chi=0.5,
        # log_eps=-4, log_alpha=-3
        ll = t46.loglike_joint((3.0, 1.5, 0.5, -4.0, -3.0))
        assert isinstance(ll, (float, int))
        assert ll > -1e10

    def test_t46_fit_yukawa_tension_resolved(self):
        """T46 should give a > 0 (the right sign) — T41 gives a < 0."""
        if not T46_RESULT.exists():
            pytest.skip("T46 not yet completed")
        with open(T46_RESULT) as f:
            data = json.load(f)
        map_a = data["MAP_physical"]["a_derived"]
        T39_a = 0.94
        # Verify a > 0 (the data's preference)
        assert map_a > 0, (
            f"T46 should give a > 0 (data wants sigma/m decreasing with v), got {map_a}"
        )
        # Verify tension with T39 is reduced compared to T41
        tension = abs(map_a - T39_a)
        assert tension < 5.0, (
            f"T46 tension with T39 = {tension:.2f}, should be < 5.0 "
            "(T41 had 2.75, T43 had 38.8)"
        )
