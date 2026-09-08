"""
Tests for t90_v21_lz_mixture.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))


def test_v17_posteriors_match_baseline():
    """v17 posteriors should match the documented 47% MM / 47% HIG."""
    from t90_v21_lz_mixture import lz_v17_posteriors
    posterior = lz_v17_posteriors()
    posts = posterior['posteriors']
    assert abs(posts['magnetic_moment_DM'] - 0.47) < 0.02
    assert abs(posts['higgsino_inelastic'] - 0.47) < 0.02


def test_sigma_m_magnetic_moment_at_reference():
    """sigma/m for magnetic-moment at v=100 km/s should be 0.7 cm^2/g."""
    from t90_v21_lz_mixture import sigma_m_magnetic_moment
    s = sigma_m_magnetic_moment(100)
    assert abs(s - 0.7) / 0.7 < 1e-6


def test_sigma_m_higgsino_constant():
    """sigma/m for Higgsino is constant 0.05 cm^2/g."""
    from t90_v21_lz_mixture import sigma_m_higgsino
    assert sigma_m_higgsino(10) == 0.05
    assert sigma_m_higgsino(1000) == 0.05


def test_sigma_m_mixture_in_range():
    """Mixture sigma/m should be between Higgsino and magnetic-moment."""
    from t90_v21_lz_mixture import sigma_m_mixture, sigma_m_magnetic_moment, sigma_m_higgsino
    for v in [10, 100, 150, 1000]:
        s_mix = sigma_m_mixture(v)['sigma_m_eff']
        s_hig = sigma_m_higgsino(v)
        s_mm = sigma_m_magnetic_moment(v)
        assert s_hig <= s_mix <= s_mm


def test_mixture_reduces_sigma_m():
    """Mixture should reduce sigma/m vs pure magnetic-moment."""
    from t90_v21_lz_mixture import sigma_m_mixture, sigma_m_magnetic_moment
    for v in [10, 100, 150, 1000]:
        s_mix = sigma_m_mixture(v)['sigma_m_eff']
        s_mm = sigma_m_magnetic_moment(v)
        assert s_mix < s_mm


def test_reduction_factor_about_2x():
    """Reduction factor should be ~2x since Higgsino ~0.05 << MM ~0.7."""
    from t90_v21_lz_mixture import sigma_m_mixture
    for v in [10, 100, 150, 1000]:
        mix = sigma_m_mixture(v)
        assert 1.5 < mix['reduction_factor'] < 2.5


def test_t95_tension_mixture_output():
    """T95 tension output should be a complete dict."""
    from t90_v21_lz_mixture import t95_tension_mixture
    t = t95_tension_mixture(150)
    assert 'master_single_component' in t
    assert 'mixture_effective' in t
    assert 'reduction_factor' in t
    assert 'rough_log_z_master' in t
    assert 'rough_log_z_mixture' in t
    assert t['reduction_factor'] > 1.0


def test_t95_tension_improvement():
    """T95 tension should improve (less negative log Z) under mixture."""
    from t90_v21_lz_mixture import t95_tension_mixture
    t = t95_tension_mixture(150)
    # Mixture should be less negative than master (less tension)
    assert t['rough_log_z_mixture'] > t['rough_log_z_master']


def test_dwarf_tension_unchanged():
    """Dwarf tension should NOT improve (Higgsino also has weak SIDM)."""
    from t90_v21_lz_mixture import t95_tension_mixture
    t_dwarf = t95_tension_mixture(10)
    # Both should be far below Zhang+ 2025 [30, 100]
    assert t_dwarf['master_single_component'] < 30
    assert t_dwarf['mixture_effective'] < 30


def test_posteriors_normalized():
    """Posteriors should sum to 1."""
    from t90_v21_lz_mixture import lz_v17_posteriors
    posterior = lz_v17_posteriors()
    total = sum(posterior['posteriors'].values())
    assert abs(total - 1.0) < 1e-6