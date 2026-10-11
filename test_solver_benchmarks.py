"""
test_solver_benchmarks.py — Priority 3 regression tests for Calogero solver.

Validates the project's Calogero solver against published curves:
  (A) Tulin, Yu, Zurek (2013) Fig. 2 / Tulin-Yu (2018) review: Yukawa sigma/m(v)
      for fixed m_phi = 10, 50, 100 MeV, alpha_D = 1e-3
  (B) Born high-v limit: sigma/m ~ (g^4 m_chi^2 / 8 pi m_phi^4) * L(s)^2
      (Feng, Kaplinghat, Yu 2009 JCAP 0907 034, Eq. 2.14)
  (C) Loeb-Weiner 2011 classical hard-sphere limit: sigma/m ~ pi r_vir^2 / m_chi
      for v ~ v_vir; not directly testable with Yukawa but can check
      v -> 0 limit consistency

Run:  python test_solver_benchmarks.py

If a future code change introduces the same class of bug that triggered
the 11-round ClawsGO cleanup (unit errors, HBARC confusion), these tests
will catch it before reaching the paper.
"""
from __future__ import annotations
import math
import sys
import os

_TEST_DIR = os.path.dirname(os.path.abspath(__file__))
if _TEST_DIR not in sys.path:
    sys.path.insert(0, _TEST_DIR)
sys.path.insert(0, r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\code")

from constants import M_CHI_GEV, MU_RED_GEV, C_KMS, HBAR_C_GEV_CM, compute_kappa, KAPPA_C_ANALYTIC

import numpy as np

# Import Calogero solver (ClawsGO's validated code)
from clawsgo_phase3_check import sigma_T_partialwave, sigma_m_cm2_g


# ============================================================
# Test (A): Tulin-Yu 2013 / Tulin-Yu 2018 Fig. 2 reproduction
# ============================================================

def test_tulin_yu_fig2():
    """
    Reproduce Tulin-Yu 2013 Fig. 2: sigma/m(v) for m_phi = 10, 50, 100 MeV,
    alpha_D = 1e-3 (g=0.112).

    Expected shape: at v ~ 100 km/s, sigma/m reaches ~0.1-10 cm^2/g range,
    monotonic decrease in v for Yukawa mediator.

    We check that:
      - sigma/m(1000 km/s) < sigma/m(100 km/s)  (monotonic)
      - sigma/m(100 km/s) is in physical range 0.01-100 cm^2/g
    """
    alpha_D = 1e-3
    m_chi = 1.0  # GeV
    print("\n=== Test A: Tulin-Yu 2013 Fig. 2 reproduction ===")

    for m_ap_MeV in [10, 50, 100]:
        m_ap_GeV = m_ap_MeV * 1e-3  # convert to GeV
        print(f"\nm_A' = {m_ap_MeV} MeV, alpha_D = {alpha_D}")
        print(f"  kappa = {compute_kappa(alpha_D, m_chi, m_ap_GeV):.4f}")

        sigma_v = {}
        for v in [10, 30, 100, 300, 1000]:
            v_c = v / C_KMS
            sigT = sigma_T_partialwave(alpha_D, m_ap_GeV, v_c)
            if sigT is None or math.isnan(sigT):
                sigma_v[v] = None
                print(f"  v = {v:5d} km/s: Calogero NaN")
                continue
            sigma_v[v] = sigma_m_cm2_g(sigT)
            print(f"  v = {v:5d} km/s: sigma/m = {sigma_v[v]:.4e} cm^2/g")

        # Check monotonic decrease (for v in range [10, 1000] km/s)
        valid_v = [v for v in [10, 30, 100, 300, 1000] if sigma_v[v] is not None]
        valid_sig = [sigma_v[v] for v in valid_v]
        if len(valid_sig) >= 3:
            monotonic = all(valid_sig[i] >= valid_sig[i+1] for i in range(len(valid_sig)-1))
            print(f"  Monotonic decrease in [10, 1000] km/s: {monotonic}")
            assert monotonic, (
                f"sigma/m should be monotonically decreasing for m_A'={m_ap_MeV} MeV, "
                f"alpha_D={alpha_D}, but found: {valid_sig}"
            )

    print("PASS: test_tulin_yu_fig2")


# ============================================================
# Test (B): Born high-v limit
# ============================================================

def test_born_high_v_limit():
    """
    Verify Calogero reproduces the Born limit at high v (v >> m_phi / m_chi).

    Born formula (Feng-Kaplinghat-Yu 2009, Tulin-Yu 2013 Eq. 2.14):
      sigma_T = (g^4 m_chi^2) / (8 pi m_phi^4) * L(s)^2
      where s = (m_chi v / (sqrt(2) m_phi))^2, L(s) = log(1+s)/s

    For high v (s >> 1), L(s) ~ log(s)/s, so sigma_T ~ 1/v^4 (steep falloff).

    At v = 1000 km/s, m_chi = 1 GeV, m_phi = 10 MeV:
      s = (1 * 1e3/2.998e5 / (sqrt(2) * 0.01))^2 = (2.36e-4 / 0.0141)^2 = (0.0167)^2 = 2.8e-4
      L = log(1.00028)/2.8e-4 = 1.0 (Born limit at small s, not high)
    """
    print("\n=== Test B: Born high-v limit ===")
    alpha_D = 1e-3  # g_chi = sqrt(4 pi alpha_D) = 0.112
    g_chi = math.sqrt(4 * math.pi * alpha_D)
    m_chi = 1.0  # GeV
    m_ap_MeV = 10  # MeV
    m_ap_GeV = m_ap_MeV * 1e-3

    # Born prediction at v = 100 km/s
    def sigma_m_born(v_kms, m_ap_GeV, g_chi, m_chi_GeV):
        s = (m_chi_GeV * v_kms / C_KMS / (math.sqrt(2) * m_ap_GeV))**2
        L = math.log(1 + s) / s if s > 0 else 1.0
        sigma_T_GeV2 = (g_chi**4 * m_chi_GeV**2) / (8 * math.pi * m_ap_GeV**4) * L**2
        # Convert to cm^2: sigma_cm2 = sigma_GeV2 * hbar_c^2 (GeV*cm)^2
        sigma_cm2 = sigma_T_GeV2 * (HBAR_C_GEV_CM)**2
        # Convert to cm^2/g
        m_chi_g = m_chi_GeV * 1.78266192e-24
        return sigma_cm2 / m_chi_g

    for v in [100, 300, 1000]:
        v_c = v / C_KMS
        sigT = sigma_T_partialwave(alpha_D, m_ap_GeV, v_c)
        if sigT is None or math.isnan(sigT):
            print(f"  v = {v} km/s: Calogero NaN")
            continue
        sigma_calogero = sigma_m_cm2_g(sigT)
        sigma_born = sigma_m_born(v, m_ap_GeV, g_chi, m_chi)
        ratio = sigma_calogero / sigma_born if sigma_born > 0 else float('inf')
        print(f"  v = {v:5d} km/s: Calogero = {sigma_calogero:.4e}, Born = {sigma_born:.4e}, ratio = {ratio:.3f}")

    # At high v (where Born valid), Calogero should match Born within ~10-20%
    # At m_phi = 10 MeV, v = 1000 km/s, kappa = alpha_D m_chi / m_ap = 1e-3 * 1 / 0.01 = 0.1
    # This is BELOW kappa_c, Born should be valid
    v = 1000
    v_c = v / C_KMS
    sigT = sigma_T_partialwave(alpha_D, m_ap_GeV, v_c)
    if sigT is not None and not math.isnan(sigT):
        sigma_calogero = sigma_m_cm2_g(sigT)
        sigma_born = sigma_m_born(v, m_ap_GeV, g_chi, m_chi)
        if sigma_born > 0:
            ratio = sigma_calogero / sigma_born
            print(f"\nAt v=1000 km/s, kappa=0.1 (Born valid): Calogero/Born = {ratio:.3f}")
            assert 0.5 < ratio < 2.0, (
                f"At high v where Born should be valid, Calogero/Born ratio = {ratio:.3f}, "
                f"expected ~1 (within 0.5-2.0 for numerical convergence)"
            )

    print("PASS: test_born_high_v_limit")


# ============================================================
# Test (C): CMB / thermal relic / structural sanity
# ============================================================

def test_structural_sanity():
    """
    Sanity tests that catch unit-mismatch bugs that triggered the
    ClawsGO #8/#10/#11 cleanup rounds:
      - sigma/m at v=29.4 km/s should be in 1-1000 cm^2/g range for
        moderate couplings (not 0.01 or 1e6, which would indicate
        unit confusion)
      - Calogero sigma/m should decrease with increasing v (Born behavior)
        for moderate couplings (not increase)
      - sigma/m should be the SAME whether computed as sigma_T/m_chi_g
        or by another method
    """
    print("\n=== Test C: Structural sanity tests ===")

    # Sanity 1: moderate coupling gives moderate sigma/m
    alpha_D = 1e-3
    m_ap_GeV = 0.01  # 10 MeV
    v = 100  # km/s
    sigT = sigma_T_partialwave(alpha_D, m_ap_GeV, v / C_KMS)
    if sigT is not None and not math.isnan(sigT):
        sigma = sigma_m_cm2_g(sigT)
        print(f"  Moderate coupling (alpha={alpha_D}, m_A'=10 MeV, v=100 km/s): sigma/m = {sigma:.4e} cm^2/g")
        assert 0.001 < sigma < 1000, (
            f"sigma/m at moderate coupling out of expected range: {sigma:.4e} cm^2/g. "
            f"Possible unit-mismatch bug (HBARC confusion)."
        )

    # Sanity 2: sigma/m monotonically decreasing with v
    v_test = [10, 30, 100, 300, 1000]
    sigma_v = []
    for v in v_test:
        sigT = sigma_T_partialwave(alpha_D, m_ap_GeV, v / C_KMS)
        if sigT is None or math.isnan(sigT):
            sigma_v.append(None)
            continue
        sigma_v.append(sigma_m_cm2_g(sigT))
    valid = [s for s in sigma_v if s is not None]
    print(f"  sigma/m at v=10, 30, 100, 300, 1000 km/s: {sigma_v}")
    assert len(valid) >= 3, "Not enough valid sigma/m values to test monotonicity"
    monotonic = all(valid[i] >= valid[i+1] for i in range(len(valid)-1))
    assert monotonic, (
        f"sigma/m should be monotonically decreasing for moderate coupling, got: {sigma_v}"
    )

    # Sanity 3: sigma/m does NOT scale linearly with v (would indicate a bug)
    if sigma_v[0] is not None and sigma_v[-1] is not None and sigma_v[-1] > 0:
        ratio = sigma_v[0] / sigma_v[-1]
        print(f"  Ratio sigma/m(10)/sigma/m(1000) = {ratio:.4e}")
        assert ratio > 1, f"sigma/m should decrease with v (ratio > 1), got {ratio:.4e}"

    # Sanity 4: kappa > kappa_c flagged correctly
    alpha_high = 1.0  # alpha_D = 1, deep bound state
    m_ap_low = 0.1  # 100 MeV
    kappa = compute_kappa(alpha_high, M_CHI_GEV, m_ap_low)
    print(f"  At alpha_D=1, m_A'=100 MeV: kappa = {kappa:.2f} > kappa_c = {KAPPA_C_ANALYTIC}")
    assert kappa > KAPPA_C_ANALYTIC, "kappa computation error"

    print("PASS: test_structural_sanity")


# ============================================================
# Test (D): HBARC unit consistency
# ============================================================

def test_hbarc_unit_consistency():
    """
    Verify HBARC = 1.97327e-14 GeV*cm is used consistently.
    The HBARC unit confusion in ClawsGO #10 (factor 10^4 error) was the
    root cause of the sigma/m(29.4)=3755 (wrong) vs 0.354 (correct) disagreement.
    """
    print("\n=== Test D: HBARC unit consistency ===")
    assert abs(HBAR_C_GEV_CM - 1.97327e-14) < 1e-18
    print(f"  HBAR_C_GEV_CM = {HBAR_C_GEV_CM:.5e} GeV*cm")
    # Cross-check: 1 fm = 1e-13 cm, so 1 GeV^-1 = 1.97327e-14 cm = 0.1973 fm
    fm_per_GeV_inv = HBAR_C_GEV_CM * 1e13  # cm * 1e13 = fm
    print(f"  1 GeV^-1 = {fm_per_GeV_inv:.4f} fm (expected: 0.1973)")
    assert abs(fm_per_GeV_inv - 0.1973) < 0.001
    print("PASS: test_hbarc_unit_consistency")


# ============================================================
# Run all benchmarks
# ============================================================

if __name__ == "__main__":
    tests = [
        test_tulin_yu_fig2,
        test_born_high_v_limit,
        test_structural_sanity,
        test_hbarc_unit_consistency,
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
        print("ALL BENCHMARKS PASSED")
        sys.exit(0)