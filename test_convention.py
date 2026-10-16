"""
test_convention.py — Unit tests for constants.py coupling convention locking
==============================================================================

Run with:  python -m pytest test_convention.py -v
Or:        python test_convention.py

Tests verify:
  1. Import-time self-consistency checks pass
  2. alpha_D ≡ g²/(4π) convention is correctly implemented
  3. compute_kappa() returns correct values
  4. Convention conversion helpers are inverses
  5. Framework point kappa > kappa_c (Born outside domain)
  6. No g² vs g²/(4π) confusion anywhere
"""
from __future__ import annotations
import importlib.util
import math
import os
import sys

# v36 r38 Code-3: use importlib instead of sys.path.insert to match the
# pattern used in test_v31_post_sweep.py (v33 Code-1 fix).
_TEST_DIR = os.path.dirname(os.path.abspath(__file__))


def _load_module_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


constants = _load_module_from_path("constants", os.path.join(_TEST_DIR, "constants.py"))


# ============================================================
# Test 1: Import-time checks pass
# ============================================================

def test_import_checks_pass():
    """constants.py should import without raising AssertionError."""
    # If we got here, _run_convention_checks() passed
    assert constants.ALPHA_D == 5.55e-6
    assert constants.M_CHI_GEV == 1.0
    assert constants.C_KMS == 2.998e5
    print("PASS: test_import_checks_pass")


# ============================================================
# Test 2: g_chi = sqrt(4π * alpha_D) is correct
# ============================================================

def test_g_chi_computation():
    """Verify G_CHI = sqrt(4π * ALPHA_D)."""
    expected_g = math.sqrt(4.0 * math.pi * constants.ALPHA_D)
    assert abs(constants.G_CHI - expected_g) < 1e-15, (
        f"G_CHI={constants.G_CHI:.6e} != sqrt(4π*ALPHA_D)={expected_g:.6e}"
    )
    # Numerical check: alpha_D = 5.55e-6 -> g = sqrt(4π * 5.55e-6) ≈ 0.00835
    assert 0.008 < constants.G_CHI < 0.009, f"G_CHI={constants.G_CHI} out of expected range"
    print("PASS: test_g_chi_computation")


# ============================================================
# Test 3: compute_kappa returns correct value
# ============================================================

def test_compute_kappa():
    """Verify kappa = alpha_D * m_chi / m_A'."""
    # Framework point: alpha=6.8e-7, m_chi=1GeV, m_A'=200eV=2e-7 GeV
    kappa = constants.compute_kappa(6.8e-7, 1.0, 200e-9)
    expected = 6.8e-7 * 1.0 / 200e-9  # = 3.4
    assert abs(kappa - expected) < 1e-10, f"kappa={kappa} != {expected}"
    assert kappa == 3.4, f"kappa should be exactly 3.4, got {kappa}"

    # Best-fit point: alpha_D=5.55e-6, m_chi=1GeV, need m_A' for ratio check
    # At best point: m_A'/m_chi = 1.26e-4 -> m_A' = 1.26e-4 GeV = 126 keV
    kappa_best = constants.compute_kappa(5.55e-6, 1.0, 1.26e-4)
    expected_best = 5.55e-6 * 1.0 / 1.26e-4
    assert abs(kappa_best - expected_best) < 1e-10
    print("PASS: test_compute_kappa")


# ============================================================
# Test 4: kappa_c analytic value is in correct range
# ============================================================

def test_kappa_c_analytic():
    """Verify kappa_c is the standard s-wave Yukawa bound-state threshold.

    Standard references (per reviewer revV19_2_F.docx, 2026-10-11):
      - Simonov, Yu. A. (1964)  original analytic treatment
      - Tulin, Yu, Zurek (2013)  arXiv:1306.5010  modern review
    The value 1.6798 is NOT from Bethe-Fano (Coulomb potential) or Simonov
    (1964) as a "Bethe-Fano/Simonov" derivation; the threshold is for the
    Yukawa potential specifically, not Coulomb.
    """
    # The analytic value should be ~1.6798 (not 1.68*4π or 1.68/(4π))
    assert abs(constants.KAPPA_C_ANALYTIC - 1.6798) < 0.001
    assert constants.KAPPA_C == 1.68
    # If someone mistakenly used α=g² convention, kappa_c would be ~21.1
    # This test catches that mistake
    assert constants.KAPPA_C_ANALYTIC < 2.0, (
        "KAPPA_C_ANALYTIC seems too large — possible convention mixup "
        "(α=g² vs α=g²/(4π))"
    )
    print("PASS: test_kappa_c_analytic")


# ============================================================
# Test 5: Framework point is outside Born domain
# ============================================================

def test_framework_point_outside_born_domain():
    """Framework point (alpha=6.8e-7, m_A'=200eV) has kappa=3.4 > kappa_c=1.68."""
    kappa_fw = constants.compute_kappa(6.8e-7, constants.M_CHI_GEV, 200e-9)
    assert kappa_fw > constants.KAPPA_C, (
        f"kappa={kappa_fw:.3f} should be > kappa_c={constants.KAPPA_C} "
        f"(Born formula outside domain)"
    )
    print("PASS: test_framework_point_outside_born_domain")


# ============================================================
# Test 6: Convention conversion helpers are inverses
# ============================================================

def test_convention_conversion_inverses():
    """alpha_g2_to_g24pi and alpha_g24pi_to_g2 should be inverses."""
    alpha_g2_test = 1.0e-5
    # g² -> g²/(4π) -> g² should return original
    converted = constants.alpha_g2_to_g24pi(alpha_g2_test)
    recovered = constants.alpha_g24pi_to_g2(converted)
    assert abs(recovered - alpha_g2_test) < 1e-20, (
        f"Conversion round-trip failed: {alpha_g2_test} -> {converted} -> {recovered}"
    )
    # g²/(4π) -> g² -> g²/(4π) should return original
    alpha_D_test = 5.55e-6
    converted2 = constants.alpha_g24pi_to_g2(alpha_D_test)
    recovered2 = constants.alpha_g2_to_g24pi(converted2)
    assert abs(recovered2 - alpha_D_test) < 1e-20, (
        f"Conversion round-trip failed: {alpha_D_test} -> {converted2} -> {recovered2}"
    )
    print("PASS: test_convention_conversion_inverses")


# ============================================================
# Test 7: No g²/g²(4π) confusion — specific numerical checks
# ============================================================

def test_no_convention_confusion():
    """Spot-check that key numbers match expected values under α=g²/(4π)."""
    # The best-fit point from the scan: alpha_D = 5.55e-6 (under g²/(4π))
    # If someone mistakenly used g², they'd get alpha_D * 4π ≈ 6.98e-5
    # This test ensures the stored value is the g²/(4π) one
    assert constants.ALPHA_D == 5.55e-6

    # The framework's alpha_chi = 6.8e-7 was ambiguous.
    # Under g²/(4π): g = sqrt(4π * 6.8e-7) ≈ 0.00292
    # Under g²: g = sqrt(6.8e-7) ≈ 8.25e-4
    g_from_4pi = math.sqrt(4.0 * math.pi * 6.8e-7)
    g_from_g2 = math.sqrt(6.8e-7)
    # Verify our compute_kappa uses the right convention
    kappa_4pi = constants.compute_kappa(6.8e-7, 1.0, 200e-9)
    assert abs(kappa_4pi - 3.4) < 1e-10, f"Expected kappa=3.4, got {kappa_4pi}"
    print("PASS: test_no_convention_confusion")


# ============================================================
# Test 8: Physical constants are correct
# ============================================================

def test_physical_constants():
    """Verify key physical constants."""
    assert abs(constants.C_KMS - 2.998e5) < 1e2
    assert abs(constants.HBAR_C_GEV_CM - 1.97327e-14) < 1e-18
    assert constants.M_CHI_GEV == 1.0
    assert constants.MU_RED_GEV == 0.5
    print("PASS: test_physical_constants")


# ============================================================
# Run all tests
# ============================================================

if __name__ == "__main__":
    tests = [
        test_import_checks_pass,
        test_g_chi_computation,
        test_compute_kappa,
        test_kappa_c_analytic,
        test_framework_point_outside_born_domain,
        test_convention_conversion_inverses,
        test_no_convention_confusion,
        test_physical_constants,
    ]

    failed = []
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"FAIL: {test.__name__}: {e}")
            failed.append(test.__name__)

    print()
    if failed:
        print(f"FAILED: {len(failed)} test(s) failed: {failed}")
        sys.exit(1)
    else:
        print("ALL TESTS PASSED")
        sys.exit(0)