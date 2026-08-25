"""
Test class for Channel 13 — SIDM mass lower bound from quantum-statistical
constraints (Tremaine-Gunn 1979 + Rogers & Peiris 2021 Lyman-alpha).

Per T70.1 Tier-1 PATCH 2026-08-25 (response to user question
"I am puzzled, given both sidm and fdm are particles, then shouldn't sidm
also be subject to the quantum effect of fdm?"):

This channel documents the implicit assumption in the SIDM joint-fit pipeline
that "SIDM is in the classical regime, quantum effects negligible." It does
so by encoding the published lower mass bounds on quantum-statistically
relevant DM:

  1. Tremaine-Gunn bound (Tremaine & Gunn 1979; revisited by many, see
     e.g. arXiv:2302.10246): m_chi > 100 eV for fermionic DM with
     dynamical-friction correction (m > 300-400 eV without).
  2. Lyman-alpha bound (Rogers & Peiris 2021 PRL 126, 071302):
     m_chi > 2e-20 eV for bosonic ultralight DM.

Both bounds are FAR below the project's T41 posterior median
m_chi = 14.8 GeV (sigma > 10 sigma above the strongest bound), so this
channel is effectively a no-op in the relevant parameter regime. It is
shipped for documentation/audit purposes per AGENTS.md rule 14
(source-of-information priority) + scientific-code-verification skill.

References (verified HTTP 200 in 2026-08-25 feasibility brief):
  - Tremaine & Gunn 1979 (original bound)
  - arXiv:2302.10246 - Boyarsky+, 2023 (revisit with mass-varying particles)
  - arXiv:2008.11221 - Rogers & Peiris 2021 PRL 126, 071302
    (Lyman-alpha constraint, m > 2e-20 eV at 95% CL)

This is the FIRST channel that depends ONLY on m_chi (no sigma/m_0 or a).
The aggregator signature accepts (sigma_m_0, a, m_chi) for API uniformity
with other channels; sigma_m_0 and a are passed through but not used.
"""
from __future__ import annotations
import math
import sys
from pathlib import Path

import numpy as np
import pytest

# Add project root + v0.1/v0.3 code dirs to sys.path (same as test_halo_and_likelihoods.py)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "v0.1-prelim" / "code"))
sys.path.insert(0, str(PROJECT_ROOT / "v0.3-prelim" / "code"))

from channels_extended import (
    loglike_sidm_mass_lower,
    TREMAINE_GUNN_MASS_BOUND_EV,
    ROGERS_PEIRIS_LYMAN_ALPHA_BOUND_EV,
    SIDM_MASS_CLASSICAL_FLOOR_EV,
)


class TestSidmMassLower:
    """Tests for Channel 13 (SIDM quantum-statistical lower mass bound)."""

    def test_constants_are_finite(self):
        """Module-level constants should be finite positive numbers."""
        assert math.isfinite(TREMAINE_GUNN_MASS_BOUND_EV)
        assert math.isfinite(ROGERS_PEIRIS_LYMAN_ALPHA_BOUND_EV)
        assert math.isfinite(SIDM_MASS_CLASSICAL_FLOOR_EV)
        # All bounds must be positive (mass cannot be negative)
        assert TREMAINE_GUNN_MASS_BOUND_EV > 0
        assert ROGERS_PEIRIS_LYMAN_ALPHA_BOUND_EV > 0
        assert SIDM_MASS_CLASSICAL_FLOOR_EV > 0

    def test_classical_floor_is_maximum_of_bounds(self):
        """The classical floor (the actual bound we enforce) is the
        MAXIMUM of the two published bounds. For SIDM at GeV scale,
        the fermionic Tremaine-Gunn bound (100 eV) is the binding one."""
        assert SIDM_MASS_CLASSICAL_FLOOR_EV == max(
            TREMAINE_GUNN_MASS_BOUND_EV,
            ROGERS_PEIRIS_LYMAN_ALPHA_BOUND_EV,
        )

    def test_at_project_posterior_no_penalty(self):
        """At the project's T41 MAP m_chi = 14.8 GeV (14800 MeV = 1.48e10 eV),
        the channel returns ~0 (m_chi is ~10^8 times above the bound)."""
        result = loglike_sidm_mass_lower(
            sigma_m_0=0.68, a=1.48, m_chi=14.8e9  # eV
        )
        assert math.isfinite(result)
        # Should be exactly 0 (well above the floor)
        assert result >= -0.01, f"got {result}, expected ~0 (above floor)"

    def test_just_below_floor_returns_neg_inf(self):
        """At m_chi just below the Tremaine-Gunn floor (100 eV), the
        channel returns -inf (particle is in the quantum regime where
        our classical fluid approximation breaks down)."""
        result = loglike_sidm_mass_lower(
            sigma_m_0=0.68, a=1.48, m_chi=50.0  # 50 eV, below 100 eV floor
        )
        assert result == -np.inf

    def test_finite_across_classical_regime(self):
        """Channel 13 should return finite log-L (=0) across the entire
        classical regime (m_chi from floor up to Planck scale)."""
        for log_m in np.linspace(2, 19, 30):  # 100 eV to 10^19 eV
            m_chi = 10 ** log_m
            result = loglike_sidm_mass_lower(sigma_m_0=0.68, a=1.48, m_chi=m_chi)
            assert math.isfinite(result), (
                f"non-finite at log_m_chi={log_m}: {result}"
            )
            assert result >= -0.01, (
                f"unexpected penalty at log_m_chi={log_m}: {result}"
            )

    def test_negative_m_chi_returns_neg_inf(self):
        """Negative mass is unphysical; return -inf."""
        result = loglike_sidm_mass_lower(
            sigma_m_0=0.68, a=1.48, m_chi=-1.0
        )
        assert result == -np.inf

    def test_nan_inf_input_returns_neg_inf(self):
        """NaN/inf inputs must return -inf per project convention."""
        assert loglike_sidm_mass_lower(0.68, 1.48, np.nan) == -np.inf
        assert loglike_sidm_mass_lower(0.68, 1.48, np.inf) == -np.inf
        assert loglike_sidm_mass_lower(0.68, 1.48, 0.0) == -np.inf

    def test_sigma_m_0_and_a_dont_matter(self):
        """Channel 13 depends only on m_chi. At fixed m_chi, varying
        sigma_m_0 or a should not change the result."""
        r1 = loglike_sidm_mass_lower(sigma_m_0=0.01, a=0.0, m_chi=14.8e9)
        r2 = loglike_sidm_mass_lower(sigma_m_0=10.0, a=3.0, m_chi=14.8e9)
        assert abs(r1 - r2) < 1e-10, f"r1={r1}, r2={r2}, expected identical"