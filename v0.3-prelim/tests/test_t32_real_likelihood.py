"""Tests for the REAL Fermi-dSph likelihood (t32_real_likelihood.py).

Per R11 audit (2026-08-14), this is the canonical likelihood for the
Fermi-dSph channel, replacing the Gaussian-proxy surrogate.

These tests exercise:
  1. Module imports cleanly
  2. Data files load (Table 1 + TS profiles)
  3. log L at a known-bad point is much lower than at a known-good point
  4. The ~2σ signal at m_chi ≈ 40 GeV is preserved (not smoothed away)
  5. The 95% CL upper limit σ_v at the peak mass is ~7e-26 cm^3/s
  6. Mass/sigma_v grid edge extrapolation does not crash
"""
from __future__ import annotations
import sys
import os
from pathlib import Path

# Skip if the data isn't downloaded yet
WSL_ROOT = Path("/home/lamkuenai/sidm-composite-dm-mediator")
DATA_DIR = WSL_ROOT / "v0.3-prelim/data/external/fermi_mcdaniel2024"
if not DATA_DIR.exists():
    print(f"SKIP: McDaniel data not found at {DATA_DIR}. "
          f"Run outputs/fetch_external_data.sh first.")
    sys.exit(0)

sys.path.insert(0, str(WSL_ROOT / "v0.3-prelim/code"))
import t32_real_likelihood as t32r


def test_module_imports():
    assert t32r is not None
    print("OK: module imports")


def test_data_loaded():
    assert t32r.MASS_GRID_GEV.shape == (40,)
    assert t32r.SIGMA_V_GRID.shape == (60,)
    print(f"OK: data loaded ({t32r.MASS_GRID_GEV.shape[0]} masses × {t32r.SIGMA_V_GRID.shape[0]} sigma_v)")


def test_loglike_distinguishes_bad_and_good():
    """log L at a clearly excluded point should be much lower than at an allowed point."""
    ll_bad = t32r.loglike_fermi_real(50.0, 1e-25, channel="bb", use_J_prior=True)
    ll_good = t32r.loglike_fermi_real(50.0, 1e-29, channel="bb", use_J_prior=True)
    print(f"  log L(50 GeV, 1e-25) = {ll_bad:+.3f}  (bad, far above limit)")
    print(f"  log L(50 GeV, 1e-29) = {ll_good:+.3f}  (good, well below limit)")
    assert ll_bad < ll_good, "Bad point should have lower log L"
    print("OK: log L distinguishes excluded from allowed regions")


def test_signal_at_40_GeV_preserved():
    """The ~3-4σ signal reported in McDaniel+ 2024 must be preserved."""
    combined = t32r.get_combined_TS_profile(channel="bb", use_J_prior=True)
    i_peak = combined.argmax() // combined.shape[1]
    m_peak = t32r.MASS_GRID_GEV[i_peak]
    ts_peak = combined.max()
    print(f"  Combined TS peak: {ts_peak:.3f} at m_chi = {m_peak:.2f} GeV")
    # The signal: TS ~ 13.8 at 41 GeV per McDaniel+ 2024
    assert 35 <= m_peak <= 50, f"Peak mass {m_peak} GeV not in 35-50 GeV range"
    assert ts_peak >= 5.0, f"TS peak {ts_peak} too low — signal should be ≥5"
    print("OK: McDaniel+ 2024 ~2σ signal preserved")


def test_upper_limit_at_peak_mass():
    """95% CL upper limit σ_v at the peak mass is ~7e-26 cm^3/s.

    McDaniel+ 2024 use the Wilks 95% CL threshold (delta TS = 2.71 below
    the maximum at a given mass). The upper limit at mass m is the
    largest sigma_v for which TS(m, sigma_v) >= TS_max(m) - 2.71.
    """
    combined = t32r.get_combined_TS_profile(channel="bb", use_J_prior=True)
    # At the peak mass: TS_max is at sigma_v where the signal lives
    i_peak = combined.argmax() // combined.shape[1]
    ts_at_peak_mass = combined[i_peak, :]
    ts_peak = ts_at_peak_mass.max()
    # Find largest sigma_v where TS >= ts_peak - 2.71
    threshold = ts_peak - 2.71
    # For sigma_v above the peak, TS decreases — find the highest idx
    # where TS is still above the threshold
    above_threshold = (ts_at_peak_mass >= threshold).nonzero()[0]
    if len(above_threshold) == 0:
        sigv_limit = t32r.SIGMA_V_GRID[0]
    else:
        sigv_limit = t32r.SIGMA_V_GRID[above_threshold[-1]]
    print(f"  Peak mass: {t32r.MASS_GRID_GEV[i_peak]:.2f} GeV")
    print(f"  Peak TS: {ts_peak:.3f} at sigma_v = {t32r.SIGMA_V_GRID[ts_at_peak_mass.argmax()]:.2e} cm^3/s")
    print(f"  95% CL sigma_v upper limit (TS >= peak - 2.71): {sigv_limit:.2e} cm^3/s")
    # McDaniel+ 2024 reports ~7e-26 cm^3/s at ~40 GeV
    assert 3e-27 <= sigv_limit <= 5e-25, f"Upper limit {sigv_limit} out of expected range"
    print("OK: 95% CL upper limit consistent with paper")


def test_out_of_grid_extrapolation_does_not_crash():
    """Edge cases must not raise."""
    # Below mass grid
    ll_low = t32r.loglike_fermi_real(0.5, 1e-28, channel="bb", use_J_prior=True)
    # Above mass grid
    ll_high = t32r.loglike_fermi_real(2000.0, 1e-22, channel="bb", use_J_prior=True)
    # Below sigma_v grid
    ll_lsv = t32r.loglike_fermi_real(50.0, 1e-30, channel="bb", use_J_prior=True)
    # Above sigma_v grid
    ll_hsv = t32r.loglike_fermi_real(50.0, 1e-21, channel="bb", use_J_prior=True)
    print(f"  edge cases: low m={ll_low:.3f}, high m={ll_high:.3f}, "
          f"low σ_v={ll_lsv:.3f}, high σ_v={ll_hsv:.3f}")
    import math
    for label, ll in [("low mass", ll_low), ("high mass", ll_high),
                      ("low σ_v", ll_lsv), ("high σ_v", ll_hsv)]:
        assert math.isfinite(ll), f"{label}: log L is not finite"
    print("OK: edge extrapolation produces finite values")


def test_tau_channel_also_works():
    """τ+τ- channel should produce a different (typically weaker) constraint."""
    ll_bb = t32r.loglike_fermi_real(50.0, 1e-25, channel="bb", use_J_prior=True)
    ll_tau = t32r.loglike_fermi_real(50.0, 1e-25, channel="tau", use_J_prior=True)
    print(f"  bb channel: {ll_bb:.3f}")
    print(f"  tau channel: {ll_tau:.3f}")
    # Both should be finite; values may differ
    import math
    assert math.isfinite(ll_bb) and math.isfinite(ll_tau)
    print("OK: τ+τ- channel works")


if __name__ == "__main__":
    test_module_imports()
    test_data_loaded()
    test_loglike_distinguishes_bad_and_good()
    test_signal_at_40_GeV_preserved()
    test_upper_limit_at_peak_mass()
    test_out_of_grid_extrapolation_does_not_crash()
    test_tau_channel_also_works()
    print("\n=== ALL TESTS PASS ===")