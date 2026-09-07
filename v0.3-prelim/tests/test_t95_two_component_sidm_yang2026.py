"""
Tests for t95_two_component_sidm_yang2026.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))


def test_yang_parameters_match_paper():
    """Verify Yang+ 2026 SIDM2v parameters match Table 1 of the paper."""
    from t95_two_component_sidm_yang2026 import (
        SIGMA_H_INTRA_M_H_CM2_G,
        W_H_KMS,
        SIGMA_L_INTRA_M_L_CM2_G,
        W_L_KMS,
        SIGMA_X_INTER_M_H_CM2_G,
        W_X_KMS,
        M_H_OVER_M_L,
    )
    assert SIGMA_H_INTRA_M_H_CM2_G == 6.89
    assert W_H_KMS == 275.0
    assert abs(SIGMA_L_INTRA_M_L_CM2_G - 6.89 / 3.0) < 1e-6
    assert W_L_KMS == 3.0 * W_H_KMS
    assert SIGMA_X_INTER_M_H_CM2_G == 1.125
    assert W_X_KMS == 2200.0
    assert M_H_OVER_M_L == 3.0


def test_intra_heavy_at_velocity_scale():
    """At v = w_H = 275 km/s, intra-HH should be sigma_0/4 (1/(1+1)^2 = 1/4)."""
    from t95_two_component_sidm_yang2026 import (
        sigma_intra_heavy,
        SIGMA_H_INTRA_M_H_CM2_G,
        W_H_KMS,
    )
    s = sigma_intra_heavy(W_H_KMS)
    expected = SIGMA_H_INTRA_M_H_CM2_G / 4.0  # 1/(1+1)^2
    assert abs(s - expected) / expected < 1e-6


def test_intra_heavy_high_velocity_suppressed():
    """At v >> w_H, intra-HH should be heavily suppressed."""
    from t95_two_component_sidm_yang2026 import sigma_intra_heavy
    s = sigma_intra_heavy(2000)  # v/w = 7.27
    assert s < 0.05  # very suppressed


def test_inter_hl_dominates_at_high_v():
    """Inter-species (HL) is designed to dominate at v ~ 1000 km/s."""
    from t95_two_component_sidm_yang2026 import (
        sigma_intra_heavy,
        sigma_intra_light,
        sigma_inter,
    )
    v = 1000
    s_hh = sigma_intra_heavy(v)
    s_ll = sigma_intra_light(v)
    s_xl = sigma_inter(v)
    assert s_xl > s_hh  # inter > intra_HH at v=1000
    assert s_xl > s_ll  # inter > intra_LL at v=1000


def test_mass_segregation_enhancement_dwarf():
    """Mass-segregation enhancement should be large for dwarf halos (5x)."""
    from t95_two_component_sidm_yang2026 import mass_segregation_enhancement
    enh = mass_segregation_enhancement(30, 1e11)
    assert enh >= 4.0  # expect ~5x for dwarfs


def test_mass_segregation_enhancement_cluster():
    """Mass-segregation enhancement should be small for clusters (1x)."""
    from t95_two_component_sidm_yang2026 import mass_segregation_enhancement
    enh = mass_segregation_enhancement(1000, 1e15)
    assert enh == 1.0  # no enhancement for clusters


def test_effective_sigma_m_at_dwarf_high():
    """Effective sigma/m at v=30 km/s should be high (mass segregation)."""
    from t95_two_component_sidm_yang2026 import sigma_m_with_segregation
    s = sigma_m_with_segregation(30, 1e11)
    assert s > 1.0  # significant sigma/m at dwarf scales


def test_effective_sigma_m_at_cluster_lower():
    """Effective sigma/m at v=1000 km/s should be smaller than dwarf."""
    from t95_two_component_sidm_yang2026 import sigma_m_with_segregation
    s_dwarf = sigma_m_with_segregation(30, 1e11)
    s_cluster = sigma_m_with_segregation(1000, 1e15)
    assert s_cluster < s_dwarf


def test_master_yukawa_at_reference():
    """Master Yukawa at v = 100 km/s should be sigma_m_0 = 0.7 cm^2/g."""
    from t95_two_component_sidm_yang2026 import master_yukawa_sigma_m
    s = master_yukawa_sigma_m(100)
    assert abs(s - 0.7) / 0.7 < 1e-6


def test_json_serializable():
    """Output dict should be JSON-serializable (no np.bool_ errors)."""
    from t95_two_component_sidm_yang2026 import (
        effective_sigma_m_two_component,
        sigma_m_with_segregation,
        master_yukawa_sigma_m,
    )
    import json
    test_dict = {
        'two_comp': float(effective_sigma_m_two_component(150)),
        'with_segregation': float(sigma_m_with_segregation(150, 1e11)),
        'master_yukawa': float(master_yukawa_sigma_m(150)),
        'is_satisfied': bool(sigma_m_with_segregation(150, 1e15) < 0.1),
    }
    json_str = json.dumps(test_dict)
    assert 'two_comp' in json_str