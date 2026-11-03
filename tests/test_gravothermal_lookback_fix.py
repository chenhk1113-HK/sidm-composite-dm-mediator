"""Regression tests for the lookback_time_gyr / evolution_time_gyr fix
(2026-11-03; see docs/CLOUD9_HIGHSIGMA_TIMING_RECHECK_2026-11-03.md sec 4).

Anchors:
1. t_L(0) = 0 (a lookback time must vanish at z=0)
2. t_L(1.55) ~ 9.47 Gyr (Yang+ 2024 sec 3.1 Cosmo-501 worked example: z_f ~ 1.55, t_L ~ 9.48)
3. t_L(1.5116) ~ 9.50 Gyr (direct numerical integration of dz/((1+z)E(z)), H0=70, Om=0.286)
4. evolution_time_gyr(5e9) ~ 9.5 Gyr and MUST be < 13.8 (age of universe)
"""
import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                '..', 'v0.3-prelim', 'code'))

from gravothermal_yang2024 import (
    formation_redshift,
    lookback_time_gyr,
    evolution_time_gyr,
)


class TestLookbackFix:
    def test_lookback_vanishes_at_z0(self):
        assert abs(lookback_time_gyr(0.0)) < 0.01

    def test_lookback_paper_worked_example(self):
        # Yang+ 2024 sec 3.1: z_f ~ 1.55 -> t_L ~ 9.48 Gyr
        val = lookback_time_gyr(1.55)
        assert 9.3 < val < 9.65, f"t_L(1.55)={val}"

    def test_lookback_matches_numeric_integration(self):
        # tl(1.5116) by Simpson integration, H0=70 km/s/Mpc, Om=0.286, OL=0.714
        H0 = 70.0 / 977.8  # Gyr^-1  (977.8 = c/H in km/s per (Mpc/Gyr^-1) convention: 1/(100 km/s/Mpc)=9.778 Gyr)
        Om, OL = 0.286, 0.714
        z = 1.5116
        n = 20000
        h = z / n
        s = 0.0
        for i in range(n + 1):
            zi = i * h
            w = 1.0 if 0 < i < n else 0.5
            s += w / ((1.0 + zi) * math.sqrt(Om * (1.0 + zi) ** 3 + OL))
        tl = s * h / H0
        assert abs(lookback_time_gyr(z) - tl) < 0.05

    def test_evolution_time_physical(self):
        t = evolution_time_gyr(5e9)
        assert 8.0 < t < 11.0, f"evolution_time_gyr(5e9)={t}"
        assert t < 13.8  # must never exceed age of universe

    def test_formation_redshift_cloud9(self):
        z_f = formation_redshift(5e9)
        assert 1.4 < z_f < 1.7

    def test_monotonic_lookback(self):
        zs = [0.0, 0.5, 1.0, 1.5, 2.0, 3.0]
        vals = [lookback_time_gyr(z) for z in zs]
        assert all(b > a for a, b in zip(vals, vals[1:]))
