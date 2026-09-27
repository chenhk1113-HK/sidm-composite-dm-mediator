"""
Tests for t105_uv_consistency.

T105 checks whether the project's composite-DM UV completion can
produce BOTH Portal A (kinetic mixing ε ~ 10^-37) AND Portal B
(hyperfine splitting δ ~ 100-400 keV) from the same composite
structure (m_ψ, Λ_D, α_D).

Sweep (m_ψ, Λ_D, α_D, suppression) parameter space and check
volume fraction that satisfies both constraints.
"""
from __future__ import annotations

import json
from pathlib import Path
import pytest

_T105_PATH = (Path(__file__).resolve().parents[1] / "outputs" / "t95" /
              "t105_uv_consistency.json")


def _skip_if_no_t105():
    if not _T105_PATH.exists():
        pytest.skip("No T105 results; run t105_uv_consistency.py")


def test_t105_outputs_present():
    _skip_if_no_t105()
    out = json.load(open(_T105_PATH))
    assert out["test"] == "T105_uv_consistency_two_portal"
    assert "sweep_results" in out
    assert "verdict" in out


def test_t105_naive_kinetic_mixing_too_large():
    """Document the suppressed-vs-naive kinetic mixing finding.

    The naive one-loop composite-DM kinetic mixing is ε ~ 10^-2 to 10^-4,
    but the v0.7 MAP requires ε ~ 10^-37. The 30+ order gap must be
    bridged by some UV suppression mechanism.
    """
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))
    import warnings
    warnings.filterwarnings("ignore")
    from t105_uv_consistency import log_epsilon_from_composite

    # Naive: m_psi=500 GeV, Lambda_D=1 GeV, alpha_D=0.3, no suppression
    naive_log_eps = log_epsilon_from_composite(500, 1.0, 0.3, 2, suppression_orders=0.0)
    # Should be much larger (less negative) than v0.7 MAP
    assert naive_log_eps > -10.0, (
        f"Naive ε = 10^{naive_log_eps:.1f} should be > 10^-10. "
        "If not, the formula may be wrong."
    )


def test_t105_delta_in_range_with_sensible_params():
    """Hyperfine splitting can be in the LZ target range with sensible parameters."""
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))
    import warnings
    import math
    warnings.filterwarnings("ignore")
    from t105_uv_consistency import log_delta_hyperfine_keV

    # m_psi=100 GeV, Lambda_D=1 GeV, alpha_D=1.0
    log_delta = log_delta_hyperfine_keV(100, 1.0, 1.0)
    delta_keV = 10 ** log_delta
    assert 50 <= delta_keV <= 500, (
        f"Hyperfine δ = {delta_keV:.1f} keV at m_psi=100 GeV, Lambda_D=1 GeV, "
        "alpha_D=1.0 should be in 50-500 keV range"
    )


def test_t105_sweep_finds_some_satisfying_both():
    """The 4D sweep (with suppression) should find some satisfying-both points."""
    _skip_if_no_t105()
    out = json.load(open(_T105_PATH))
    n_both = out["sweep_results"]["sat_both_count"]
    assert n_both > 0, (
        f"T105 sweep found 0 points satisfying both ε and δ constraints. "
        "Expected at least some. Check formula or parameter ranges."
    )


def test_t105_volume_fraction_is_small():
    """If volume fraction is very small, verdict should be TIGHT."""
    _skip_if_no_t105()
    out = json.load(open(_T105_PATH))
    v_both = out["sweep_results"]["volume_fraction_sat_both"]
    assert v_both < 0.5, (
        f"Volume fraction sat_both = {v_both:.3f}. "
        "If > 50%, the constraints are weak. Check LZ target range."
    )


def test_t105_module_importable():
    """Module imports without error."""
    import warnings
    warnings.filterwarnings("ignore")
    import t105_uv_consistency  # noqa: F401
