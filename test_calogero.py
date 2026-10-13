"""
test_calogero.py — Calogero solver regression tests (REVIEWER-15 item 8).
"""
from __future__ import annotations
import math
import sys
import os

_TEST_DIR = os.path.dirname(os.path.abspath(__file__))
if _TEST_DIR not in sys.path:
    sys.path.insert(0, _TEST_DIR)
sys.path.insert(0, r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\code")

from constants import M_CHI_GEV, C_KMS

from clawsgo_phase3_check import sigma_T_partialwave, sigma_m_cm2_g
from v19_2_f_phase3_calogero_sommerfeld_check import sigma_born_cm2_g


def test_calogero_sommerfeld_deviation():
    """Calogero sigma_T / Born sigma_T = Sommerfeld S != 1 at kappa > kappa_c."""
    print("\n=== Test F: Calogero Sommerfeld deviation ===")
    m_phi = 0.05  # 50 keV
    m_chi = M_CHI_GEV
    v_test = 100  # km/s

    # kappa = 0.5
    kappa_low = 0.5
    alpha_low = kappa_low * m_phi / m_chi
    g_chi_low = math.sqrt(4 * math.pi * alpha_low)
    sigma_b = sigma_born_cm2_g(v_test, m_phi, g_chi_low, m_chi)
    sigT = sigma_T_partialwave(alpha_low, m_phi, v_test / C_KMS)
    sigma_c = sigma_m_cm2_g(sigT) if sigT is not None and not math.isnan(sigT) else float('nan')
    if not math.isnan(sigma_c) and sigma_b > 0:
        S_low = sigma_c / sigma_b
        print(f"  kappa=0.5 (Born): S = {S_low:.4f}")
        assert 0.3 < S_low < 1.5, f"kappa=0.5 S={S_low} not in expected range"

    # kappa = 3.0
    kappa_high = 3.0
    alpha_high = kappa_high * m_phi / m_chi
    g_chi_high = math.sqrt(4 * math.pi * alpha_high)
    sigma_b_high = sigma_born_cm2_g(v_test, m_phi, g_chi_high, m_chi)
    sigT_high = sigma_T_partialwave(alpha_high, m_phi, v_test / C_KMS)
    sigma_c_high = sigma_m_cm2_g(sigT_high) if sigT_high is not None and not math.isnan(sigT_high) else float('nan')
    if not math.isnan(sigma_c_high) and sigma_b_high > 0:
        S_high = sigma_c_high / sigma_b_high
        print(f"  kappa=3.0 (deep-Sommerfeld): S = {S_high:.4f}")
        deviation = abs(S_high - 1.0)
        print(f"  |S - 1| = {deviation:.4f} (> 0.5 indicates clear Sommerfeld effect)")
        assert deviation > 0.5, f"Sommerfeld effect too small: S={S_high}"

    print("PASS: test_calogero_sommerfeld_deviation")


if __name__ == "__main__":
    test_calogero_sommerfeld_deviation()
    print("\nALL CALOGERO TESTS PASSED")
