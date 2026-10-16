"""
test_v31_post_sweep.py — Unit tests for v31 post-processing (REVIEWER-33 item 4)

Run with:  python -m pytest test_v31_post_sweep.py -v
Or:        python test_v31_post_sweep.py

Tests verify the v31 Lyman-alpha post-sweep pipeline:
  1. alpha_D^2 scaling — sigma(2 alpha_D) / sigma(alpha_D) ≈ 4 (Born regime)
  2. Unitarity bound arithmetic — v_target=29.4 km/s, m_chi=1 GeV gives ~1.14e6 cm^2/g
  3. IN-BAND count at Cloud-9 calibration — exactly 2 across the 9 Gamma/rho values
     (Gamma/rho = 5.0 and 6.0 at alpha_D = 5.55e-6)
"""
from __future__ import annotations
import importlib.util
import json
import math
import os
import sys

_TEST_DIR = os.path.dirname(os.path.abspath(__file__))
if _TEST_DIR not in sys.path:
    sys.path.insert(0, _TEST_DIR)

# Load constants.py
constants_spec = importlib.util.spec_from_file_location(
    "constants", os.path.join(_TEST_DIR, "constants.py")
)
constants = importlib.util.module_from_spec(constants_spec)
constants_spec.loader.exec_module(constants)

# Load v19_2_f_priority1_resonance_helpers.py
HELPER_PATH = os.path.join(
    _TEST_DIR, "v0.3-prelim", "code", "v19_2_f_priority1_resonance_helpers.py"
)
helpers_spec = importlib.util.spec_from_file_location(
    "v19_2_f_priority1_resonance_helpers", HELPER_PATH
)
helpers = importlib.util.module_from_spec(helpers_spec)
helpers_spec.loader.exec_module(helpers)

# Load v19_2_f_lyman_alpha_post_v31.py
V31_SCRIPT = os.path.join(
    _TEST_DIR, "v0.3-prelim", "code", "v19_2_f_lyman_alpha_post_v31.py"
)


def _load_v31_module():
    spec = importlib.util.spec_from_file_location(
        "v19_2_f_lyman_alpha_post_v31", V31_SCRIPT
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ============================================================
# Test 1: alpha_D^2 scaling
# ============================================================
def test_alpha_d_squared_scaling():
    """sigma(2 alpha_D) / sigma(alpha_D) ≈ 4 in the Born-valid regime."""
    v31 = _load_v31_module()
    m_chi = 1.0
    m_rho = 0.05e-3
    v_target = 29.4
    # Use a moderate Gamma/rho where the cross-section is well below unitarity
    Gamma_rho = 5.0 * m_rho

    # Use alpha_D values deep in the Born-valid regime (no unitarity saturation)
    base = 1e-7
    doubled = 2e-7
    sig_base = v31.sigma_m_resonance(v_target, base, m_rho, Gamma_rho)
    sig_doubled = v31.sigma_m_resonance(v_target, doubled, m_rho, Gamma_rho)
    ratio = sig_doubled / sig_base
    # Predicted ratio for exact alpha_D^2 scaling: (2)^2 = 4
    # Allow 0.5% tolerance for the Gauss-Legendre quadrature
    assert 3.98 < ratio < 4.02, (
        f"alpha_D^2 scaling violated: sigma(2*alpha_D)/sigma(alpha_D) = {ratio}, "
        f"expected 4.0 ± 2% (s={sig_base:.4e}, s2={sig_doubled:.4e})"
    )
    print(f"PASS: test_alpha_d_squared_scaling  (ratio = {ratio:.6f})")


# ============================================================
# Test 2: Unitarity bound arithmetic
# ============================================================
def test_unitarity_bound_arithmetic():
    """unitarity_bound(1.0 GeV, 29.4 km/s) ≈ 1.14e6 cm^2/g."""
    v31 = _load_v31_module()
    sigma_max = v31.unitarity_bound(1.0, 29.4)
    # Expected: (4*pi / k^2) * (hbar*c)^2 / m_chi
    # k = (1/2) * 1.0 GeV * (29.4 km/s / c)  ≈ 4.9e-5 GeV
    # (4*pi / k^2) ≈ 5.2e9 GeV^-2
    # (hbar*c)^2 ≈ 3.89e-27 GeV^2 cm^2
    # / m_chi / (1.78e-27 GeV/g) ≈ 1.14e6 cm^2/g
    expected = 1.14e6
    rel_err = abs(sigma_max - expected) / expected
    assert rel_err < 0.01, (
        f"Unitarity bound off: {sigma_max:.4e} vs expected {expected:.2e} (rel_err {rel_err:.4%})"
    )
    print(f"PASS: test_unitarity_bound_arithmetic  "
          f"(sigma_max = {sigma_max:.4e} cm^2/g, expected ~{expected:.2e})")


# ============================================================
# Test 3: IN-BAND count at Cloud-9 calibration
# ============================================================
def test_in_band_count_cloud9():
    """At alpha_D=5.55e-6, exactly 2 Gamma/rho values achieve IN BAND (5.0 and 6.0)."""
    v31 = _load_v31_module()
    sigma_target = 174.0
    alpha_d = 5.55e-6
    m_chi = 1.0
    m_rho = 0.05e-3
    v_target = 29.4
    in_band = []
    for gamma_frac in v31.GAMMA_RHO_OVER_M_RHO_GRID:
        Gamma_rho = gamma_frac * m_rho
        sig = v31.sigma_m_resonance(v_target, alpha_d, m_rho, Gamma_rho)
        r_t = sig / sigma_target
        if 0.5 < r_t < 2.0:
            in_band.append((gamma_frac, sig, r_t))
    # Expected: IN BAND only at Gamma/rho = 5.0 (sigma/m=237, ratio=1.36)
    #                          and Gamma/rho = 6.0 (sigma/m=165, ratio=0.95)
    assert len(in_band) == 2, (
        f"Expected exactly 2 IN BAND points, got {len(in_band)}: {in_band}"
    )
    gamma_fracs = [g for g, _, _ in in_band]
    assert 5.0 in gamma_fracs, f"Gamma/rho=5.0 not IN BAND: {in_band}"
    assert 6.0 in gamma_fracs, f"Gamma/rho=6.0 not IN BAND: {in_band}"
    print(f"PASS: test_in_band_count_cloud9  "
          f"(IN BAND at Gamma/rho = {gamma_fracs})")


# ============================================================
# Test 4 (bonus): v31 JSON metadata contract
# ============================================================
def test_v31_json_metadata_contract():
    """v31 JSON has all required metadata fields per r33 item 6."""
    json_path = os.path.join(
        _TEST_DIR, "v0.3-prelim", "data", "results", "v19_2_f_lyman_alpha_post_v31.json"
    )
    if not os.path.exists(json_path):
        print(f"SKIP: test_v31_json_metadata_contract  "
              f"(JSON not yet generated: {json_path})")
        return
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    required = {
        "function_version", "precision", "generated_at", "script_sha256",
        "total_computed", "filtered_out", "alpha_D_grid_size", "gamma_rho_grid_size",
        "expected_entries",
    }
    actual = set(data.get("metadata", {}).keys())
    missing = required - actual
    assert not missing, f"v31 JSON missing metadata fields: {missing}"
    # Sanity-check counts
    md = data["metadata"]
    assert md["total_computed"] == md["expected_entries"], (
        f"total_computed {md['total_computed']} != expected {md['expected_entries']}"
    )
    assert md["alpha_D_grid_size"] * md["gamma_rho_grid_size"] == md["expected_entries"], (
        f"alpha_D_grid_size * gamma_rho_grid_size != expected_entries"
    )
    print(f"PASS: test_v31_json_metadata_contract  "
          f"(total={md['total_computed']}, filtered={md['filtered_out']})")


# ============================================================
# Test 5 (bonus): 126 entries in scan
# ============================================================
def test_v31_total_entries():
    """v31 JSON all_scan_results has exactly 9 Gamma/rho keys each with 14 entries = 126."""
    json_path = os.path.join(
        _TEST_DIR, "v0.3-prelim", "data", "results", "v19_2_f_lyman_alpha_post_v31.json"
    )
    if not os.path.exists(json_path):
        print(f"SKIP: test_v31_total_entries  (JSON not yet generated)")
        return
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    scan = data["all_scan_results"]
    assert len(scan) == 9, f"Expected 9 Gamma/rho keys, got {len(scan)}"
    for g_frac, entries in scan.items():
        assert len(entries) == 14, (
            f"Gamma/rho={g_frac} has {len(entries)} entries, expected 14"
        )
    print(f"PASS: test_v31_total_entries  (9 keys × 14 entries = 126 total)")


if __name__ == "__main__":
    print("=" * 75)
    print("v31 post-sweep tests (REVIEWER-33 item 4)")
    print("=" * 75)
    print()
    test_alpha_d_squared_scaling()
    test_unitarity_bound_arithmetic()
    test_in_band_count_cloud9()
    test_v31_json_metadata_contract()
    test_v31_total_entries()
    print()
    print("ALL TESTS PASSED")
