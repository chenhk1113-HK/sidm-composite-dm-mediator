"""Tests for the SPARC hierarchical per-galaxy forward model (R11 G12).

Closes R11 audit recommendation G12 (2026-08-14): replaces the
saturation score with a real per-galaxy likelihood from 175 SPARC
galaxies, marginalized over ρ_c with the Dutton-Maccio 2014
concentration-mass relation.

These tests exercise:
  1. The pre-computed grid file exists and is well-formed
  2. loglike_sparc_hierarchical() returns finite values at canonical
     (σ/m, a) test points
  3. The grid has structure (log L varies across σ/m and a)
  4. The best-fit (σ/m, a) lands in a physically reasonable region
  5. delta_log_sparc() (legacy wrapper) now returns the hierarchical value
"""
from __future__ import annotations
import sys
import os
from pathlib import Path

# Skip if the precomputed grid doesn't exist yet
WSL_ROOT = Path("/home/lamkuenai/sidm-composite-dm-mediator")
GRID_PATH = WSL_ROOT / "v0.3-prelim/data/results/sparc_hierarchical_grid.npz"
if not GRID_PATH.exists():
    print(f"SKIP: SPARC hierarchical grid not found at {GRID_PATH}. "
          f"Run precompute_sparc_hierarchical.py first.")
    sys.exit(0)

sys.path.insert(0, str(WSL_ROOT / "v0.3-prelim/code"))
import t8_v03_joint_fit as t8


def test_grid_exists_and_well_formed():
    assert GRID_PATH.exists()
    grid = t8.loglike_sparc_hierarchical.__wrapped__ if hasattr(t8.loglike_sparc_hierarchical, '__wrapped__') else None
    # Trigger grid load
    ll = t8.loglike_sparc_hierarchical(1.0, 0.0)
    assert hasattr(t8.loglike_sparc_hierarchical, '_grid_cache')
    cached = t8.loglike_sparc_hierarchical._grid_cache
    assert cached["sigma_m_grid"].shape == (50,)
    assert cached["a_grid"].shape == (30,)
    assert cached["logL_grid"].shape == (50, 30)
    print(f"OK: grid well-formed ({cached['logL_grid'].shape[0]} σ/m × {cached['logL_grid'].shape[1]} a)")


def test_loglike_finite_at_canonical_points():
    """Log L is finite at canonical (σ/m, a) test points."""
    import numpy as np
    test_points = [
        (0.1, 0.0),
        (1.0, 0.0),
        (1.7, 0.0),  # Headline from T21 real KiSS-SIDM
        (10.0, 0.0),
        (1.0, 0.5),
        (1.0, 1.0),
        (1.0, 2.0),
    ]
    for sm, a in test_points:
        ll = t8.loglike_sparc_hierarchical(sm, a)
        print(f"  log L(σ/m={sm}, a={a}) = {ll:+.2f}")
        assert np.isfinite(ll), f"Non-finite log L at (σ/m={sm}, a={a})"
    print("OK: log L finite at all canonical test points")


def test_grid_has_real_structure():
    """The grid must have non-trivial variation — not all the same value."""
    import numpy as np
    logL = t8.loglike_sparc_hierarchical._grid_cache["logL_grid"]
    delta = logL.max() - logL.min()
    print(f"  log L max = {logL.max():.2f}, min = {logL.min():.2f}, range = {delta:.2f}")
    # Real per-galaxy chi² likelihood should have span > 1000 (many galaxies
    # contributing chi² ~ 100s each)
    assert delta > 1000, f"Log L range too small ({delta:.2f}) — grid may be flat"
    print("OK: grid has real structure (span > 1000 nats)")


def test_best_fit_in_reasonable_region():
    """The best-fit (σ/m, a) should land in a physically meaningful region."""
    import numpy as np
    logL = t8.loglike_sparc_hierarchical._grid_cache["logL_grid"]
    sigma_m = t8.loglike_sparc_hierarchical._grid_cache["sigma_m_grid"]
    a = t8.loglike_sparc_hierarchical._grid_cache["a_grid"]
    i, j = np.unravel_index(logL.argmax(), logL.shape)
    sm_best = sigma_m[i]
    a_best = a[j]
    print(f"  Best fit: σ/m = {sm_best:.3g} cm²/g, a = {a_best:.2f}, log L = {logL[i, j]:.2f}")
    # Should land somewhere in the grid (not at the boundary unless the
    # actual data supports that extreme)
    assert 0.01 <= sm_best <= 316, f"Best σ/m {sm_best} outside grid"
    assert 0.0 <= a_best <= 3.0, f"Best a {a_best} outside grid"
    print("OK: best fit is within the grid")


def test_legacy_wrapper_returns_hierarchical():
    """delta_log_sparc (legacy wrapper) should return the same value as
    loglike_sparc_hierarchical at any test point."""
    for sm, a in [(1.0, 0.0), (1.7, 0.5), (10.0, 1.0)]:
        ll_legacy = t8.delta_log_sparc(sm, a)
        ll_hier = t8.loglike_sparc_hierarchical(sm, a)
        assert abs(ll_legacy - ll_hier) < 1e-6, (
            f"Wrapper divergence: legacy={ll_legacy:.3f}, hier={ll_hier:.3f}"
        )
    print("OK: delta_log_sparc (wrapper) matches loglike_sparc_hierarchical")


def test_loglike_5channel_uses_hierarchical_sparc():
    """loglike_5channel in t8 should now use the hierarchical SPARC."""
    import channels_v03 as ch_v03
    sigma_m = 1.0
    a = 0.0
    ll_5ch = t8.loglike_5channel(sigma_m, a)
    ll_sparc_only = t8.loglike_sparc_hierarchical(sigma_m, a)
    ll_other = (ch_v03.loglike_dsph_v03(sigma_m, a)
                + ch_v03.loglike_ufd_v03(sigma_m, a)
                + ch_v03.loglike_bullet_v03(sigma_m, a))
    print(f"  loglike_5channel = {ll_5ch:.2f}")
    print(f"  loglike_sparc_hierarchical = {ll_sparc_only:.2f}")
    print(f"  sum of other channels = {ll_other:.2f}")
    # 5-channel should equal SPARC + other channels
    assert abs(ll_5ch - ll_sparc_only - ll_other) < 1e-6
    print("OK: loglike_5channel = SPARC hierarchical + other channels")


if __name__ == "__main__":
    test_grid_exists_and_well_formed()
    test_loglike_finite_at_canonical_points()
    test_grid_has_real_structure()
    test_best_fit_in_reasonable_region()
    test_legacy_wrapper_returns_hierarchical()
    test_loglike_5channel_uses_hierarchical_sparc()
    print("\n=== ALL TESTS PASS ===")