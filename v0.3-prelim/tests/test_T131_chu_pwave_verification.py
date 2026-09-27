"""
Tests for T131 — Chu et al. 2019 P1 verification.

These tests verify that:
1. Chu P1 (best-fit p-wave resonance) is correctly computed
2. P1 fails on Cloud-9 (the key phenomenology constraint)
3. P1 passes dSph/UFD constraints (which is what Chu designed for)
4. P1 cannot simultaneously solve Cloud-9 + dSph tension

Reference: Chu, Garcia-Cely, Murayama, "Velocity Dependence from Resonant
Self-Interacting Dark Matter," PRL 122, 071103 (2019), arXiv:1810.04709.
"""
import numpy as np
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/code")

from T131_chu_pwave_verification import chu_pwave_resonance, PHENOMENOLOGY_TARGETS


class TestChuP1Parameters:
    """Verify Chu P1 benchmark parameters from the paper."""

    def test_P1_resonance_at_v_R_108_kms(self):
        """P1 resonance peaks at v_R = 108 km/s."""
        # At v = v_R, the resonance contribution peaks
        sigma_at_vR = chu_pwave_resonance(108)
        # Should be enhanced above background
        sigma_below = chu_pwave_resonance(50)
        sigma_above = chu_pwave_resonance(300)
        assert sigma_at_vR > sigma_below
        assert sigma_at_vR > sigma_above

    def test_P1_background_is_0_1_cm2_per_g(self):
        """At very low or high v, sigma/m approaches sigma_0/m = 0.1 cm^2/g."""
        sigma_low = chu_pwave_resonance(1.0)
        sigma_high = chu_pwave_resonance(1000.0)
        assert abs(sigma_low - 0.1) < 0.05, f"At low v: {sigma_low}, expected ~0.1"
        assert abs(sigma_high - 0.1) < 0.05, f"At high v: {sigma_high}, expected ~0.1"


class TestChuP1FailsCloud9:
    """Chu P1 fails on the Cloud-9 constraint."""

    def test_P1_at_Cloud9_velocity_gives_0_1_not_100(self):
        """Chu P1 at v=28 km/s gives 0.1 cm^2/g, but Cloud-9 needs ~100."""
        sigma = chu_pwave_resonance(28)
        assert sigma < 1.0, f"P1 at Cloud-9: {sigma}, but Cloud-9 needs ~100"
        assert abs(sigma - 0.1) < 0.1

    def test_P1_cannot_exceed_0_2_anywhere(self):
        """P1 max sigma/m < 0.2 cm^2/g (cannot reach Cloud-9's 100)."""
        max_sigma = max(chu_pwave_resonance(v) for v in range(1, 1000))
        assert max_sigma < 0.2, f"P1 max: {max_sigma}, but Cloud-9 needs 100"

    def test_P1_cannot_exceed_1_0_anywhere(self):
        """Even P1's maximum is 1 cm^2/g (vs Cloud-9's 100)."""
        max_sigma = max(chu_pwave_resonance(v) for v in np.linspace(1, 1000, 100))
        assert max_sigma < 1.0, f"P1 max: {max_sigma}, but Cloud-9 needs 100"


class TestChuP1PassesDSph:
    """Chu P1 was DESIGNED to pass dSph constraints (Kaplinghat/Tulin/Yu data)."""

    def test_P1_at_dSph_15_kms_passes(self):
        """P1 at v=15 km/s gives 0.1 cm^2/g, below 0.8 dSph upper limit."""
        sigma = chu_pwave_resonance(15)
        assert sigma < 0.8, f"P1 at dSph: {sigma}, should be < 0.8"

    def test_P1_at_UFD_3_kms_passes(self):
        """P1 at v=3 km/s (deep UFD) gives 0.1 cm^2/g, below 0.8 limit."""
        sigma = chu_pwave_resonance(3)
        assert sigma < 0.8, f"P1 at UFD: {sigma}, should be < 0.8"

    def test_P1_at_cluster_500_kms_passes(self):
        """P1 at v=500 km/s gives 0.1 cm^2/g, below 1.0 cm^2/g cluster limit."""
        sigma = chu_pwave_resonance(500)
        assert sigma < 1.0, f"P1 at cluster: {sigma}, should be < 1.0"


class TestChuP1MissesSPARC:
    """P1 marginally misses SPARC at the expected ~0.2 cm^2/g."""

    def test_P1_at_SPARC_100_kms(self):
        """P1 at v=100 km/s gives ~0.15 cm^2/g; SPARC target ~0.19."""
        sigma = chu_pwave_resonance(100)
        # Within factor of 2
        assert 0.05 < sigma < 0.5, f"P1 at SPARC: {sigma}"


class TestWhyChuP1Fails:
    """P1 fails because the p-wave resonance shape is wrong for our target."""

    def test_P1_is_too_flat_to_give_Cloud9_high_dSph_low(self):
        """P1's resonance is centered at v=108 km/s, NOT at v=28 km/s."""
        # If we shift v_R to 28 km/s, P1 might work for Cloud-9
        # But the resonance would still be too narrow to satisfy dSph below
        sigma_at_28 = chu_pwave_resonance(28)
        sigma_at_15 = chu_pwave_resonance(15)
        # P1 doesn't distinguish 15 vs 28 km/s (both ~0.1)
        assert abs(sigma_at_28 - sigma_at_15) < 0.05

    def test_P1_velocity_scale_is_dwarf_to_cluster(self):
        """Chu P1 solves dwarf-vs-cluster (older Kaplinghat tension),
        not Cloud-9-vs-dSph (our tension)."""
        # At v < 100 km/s, P1 gives ~0.1 (background-dominated)
        # At v > 100 km/s, P1 gives ~0.1 (resonance then falls off)
        # So P1 is roughly v-independent in the range we care about

        sigmas_low = [chu_pwave_resonance(v) for v in [3, 7, 15, 28]]
        sigmas_high = [chu_pwave_resonance(v) for v in [100, 300, 500]]

        # All similar (~0.1)
        all_sigmas = sigmas_low + sigmas_high
        ratio_max_min = max(all_sigmas) / min(all_sigmas)
        assert ratio_max_min < 2.0, f"P1 ratio: {ratio_max_min}, too flat for our tension"
