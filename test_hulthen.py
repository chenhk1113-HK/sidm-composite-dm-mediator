"""
test_hulthen.py — Hulthen solver regression tests (REVIEWER-15 item 8).
"""
from __future__ import annotations
import math
import sys
import os

_TEST_DIR = os.path.dirname(os.path.abspath(__file__))
if _TEST_DIR not in sys.path:
    sys.path.insert(0, _TEST_DIR)
sys.path.insert(0, r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\code")

from constants import M_CHI_GEV


def test_hulthen_framework_fails():
    """Hulthen solver: framework point sigma/m(29.4) << target."""
    print("\n=== Test G: Hulthen framework-point verdict ===")
    from v19_2_f_priority2_hulthen_solver import sigma_m_hulthen_cm2_g

    alpha_D = 6.8e-7
    m_chi = M_CHI_GEV
    m_ap = 200e-9
    v_test = 29.4

    sig = sigma_m_hulthen_cm2_g(v_test, m_ap, alpha_D, m_chi)
    assert sig == sig, f"NaN: {sig}"
    assert sig > 0, f"Non-positive: {sig}"
    assert 1e-10 < sig < 1e-2, f"Out of range: {sig}"
    print(f"  Hulthen sigma/m(29.4) = {sig:.4e} cm^2/g, ratio to 174 = {sig/174:.3e}")

    alpha_best = 5.55e-6
    m_ap_best = 1.26e-4
    sig_best = sigma_m_hulthen_cm2_g(v_test, m_ap_best, alpha_best, m_chi)
    assert sig_best > sig * 100, f"Best-fit should be >> framework"

    alpha_weak = 1e-7
    sig_weak = sigma_m_hulthen_cm2_g(v_test, m_ap, alpha_weak, m_chi)
    expected_ratio = (alpha_weak / alpha_D)**2
    assert 0.5 * expected_ratio < sig_weak/sig < 2.0 * expected_ratio
    print("PASS: test_hulthen_framework_fails")


def test_hulthen_asymptotic():
    """Hulthen asymptotic at large xi + a_0(kappa) scattering length."""
    print("\n=== Test H: Hulthen asymptotic at large xi ===")
    from v19_2_f_priority2_hulthen_solver import delta_l_hulthen, scattering_length_yukawa

    k = 1e-3
    m_ap = 200e-9
    xi = k / m_ap
    eta = 1e-7 * m_ap / k
    assert xi > 50 / math.pi
    delta = delta_l_hulthen(0, k, m_ap, 1e-7, 1.0)
    assert math.isfinite(delta), f"delta_l not finite: {delta}"
    print(f"  Large xi ({xi:.0f}): delta_l = {delta:.4f}")

    m_phi_GeV = 50e-6
    for kappa in [0.5, 1.0, 1.5, 2.0]:
        a_0 = scattering_length_yukawa(kappa, m_phi_GeV)
        if kappa < 1.6798:
            assert a_0 < 0
        else:
            assert a_0 > 0
        a_0_fm = a_0 * 1e-13 / 1.97327e-14
        print(f"  kappa={kappa}: a_0 = {a_0_fm:+.2f} fm")

    print("PASS: test_hulthen_asymptotic")


if __name__ == "__main__":
    test_hulthen_framework_fails()
    test_hulthen_asymptotic()
    print("\nALL HULTHEN TESTS PASSED")
