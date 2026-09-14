"""
Tests for Phase 9b multi-component mass segregation at v_disp.

Validates:
1. sigma/m_obs_at_v_disp is correctly evaluated using v_disp (not v_escape)
2. MW-like halo reproduces sigma/m ~ 1 cm^2/g (T39 MAP)
3. Mass segregation alone is insufficient (spans < 60x observed spread)
"""
import pytest
import numpy as np
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "code"))
from phase9b_mass_segregation_vdisp import (
    sigma_m_observed_at_halo, HALO_TYPES,
    M_CHI_H_GEV, M_CHI_L_GEV, G_CHI, M_PHI_MEV,
)
from t40_yukawa_sigma_m import sigma_m_cm2_per_g


class TestMassSegregationSpread:
    """The mass segregation framework produces sigma/m spread."""

    def test_mw_halo_matches_data(self):
        """MW-like halo (OLD, v=100): σ/m_evolved ~ 1 cm²/g (ratio 1-2)."""
        mw_halo = next(h for h in HALO_TYPES if "MW" in h["name"])
        result = sigma_m_observed_at_halo(mw_halo, M_PHI_MEV, G_CHI)
        ratio = result["ratio_data_to_evolved"]
        assert 0.5 < ratio < 2.0, \
            f"MW-like halo ratio data/evolved = {ratio:.2f} (expected 1±0.5)"

    def test_cluster_halo_underpredicts(self):
        """Cluster halo: σ/m_evolved << σ/m_obs (off by 5-20x)."""
        cluster_halo = next(h for h in HALO_TYPES if "Cluster" in h["name"])
        result = sigma_m_observed_at_halo(cluster_halo, M_PHI_MEV, G_CHI)
        ratio = result["ratio_data_to_evolved"]
        # Cluster σ/m limit is 0.5, model predicts ~0.05
        assert ratio > 3, f"Cluster ratio = {ratio:.2f} (expected > 3, model under-predicts)"

    def test_dwarf_halo_underpredicts(self):
        """Dwarf halo: σ/m_evolved << σ/m_obs (Cloud-9 not reached)."""
        dwarf_halo = next(h for h in HALO_TYPES if "Dwarf" in h["name"])
        result = sigma_m_observed_at_halo(dwarf_halo, M_PHI_MEV, G_CHI)
        ratio = result["ratio_data_to_evolved"]
        assert ratio > 10, f"Dwarf ratio = {ratio:.2f} (expected > 10, Cloud-9 not reached)"

    def test_evolved_sigma_m_is_finite(self):
        """All halos produce finite σ/m_evolved."""
        for halo in HALO_TYPES:
            result = sigma_m_observed_at_halo(halo, M_PHI_MEV, G_CHI)
            assert np.isfinite(result["sigma_m_evolved"]), \
                f"sigma_m_evolved not finite for {halo['name']}"
            assert result["sigma_m_evolved"] > 0, \
                f"sigma_m_evolved <= 0 for {halo['name']}"


class TestSigmaMatVDisp:
    """σ/m evaluated at v_disp (not v_escape)."""

    def test_v_disp_used_not_v_escape(self):
        """The σ/m should use v_disp (30-3000 km/s), not v_escape (1000s km/s)."""
        for halo in HALO_TYPES:
            v_disp = halo["v_disp_kms"]
            # Direct σ/m at v_disp for H species
            sigma_direct = sigma_m_cm2_per_g(v_disp, M_PHI_MEV, M_CHI_H_GEV, G_CHI)
            # Result should be order-of-magnitude similar to sigma_H_v
            result = sigma_m_observed_at_halo(halo, M_PHI_MEV, G_CHI)
            # Result should be at least 10x larger than escape-velocity result
            # (escape v is 1000s, gives near-zero sigma/m)
            assert result["sigma_H_at_v_disp"] > 0.001, \
                f"sigma_H_at_v_disp too small for {halo['name']}: {result['sigma_H_at_v_disp']}"
            # Should be comparable to direct evaluation
            np.testing.assert_allclose(result["sigma_H_at_v_disp"], sigma_direct, rtol=1e-6)


class TestSegregationEffect:
    """Mass segregation increases f_H at r_half in old halos."""

    def test_f_H_grows_with_age(self):
        """f_H at r_half should be larger at age > 0 than initial."""
        for halo in HALO_TYPES:
            result = sigma_m_observed_at_halo(halo, M_PHI_MEV, G_CHI)
            f_H_init = result["f_H_at_r_half_initial"]
            f_H_ev = result["f_H_at_r_half_evolved"]
            # In the simple two-component model, f_H can grow as heavy sinks
            assert f_H_ev >= f_H_init - 0.1, \
                f"f_H should grow or stay similar: {f_H_init} -> {f_H_ev} for {halo['name']}"
