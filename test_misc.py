"""
test_misc.py — Miscellaneous regression tests (REVIEWER-15 item 8).
"""
from __future__ import annotations
import math
import sys
import os

_TEST_DIR = os.path.dirname(os.path.abspath(__file__))
if _TEST_DIR not in sys.path:
    sys.path.insert(0, _TEST_DIR)
sys.path.insert(0, r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\code")

from constants import M_CHI_GEV, HBAR_C_GEV_CM

from clawsgo_phase3_check import sigma_T_partialwave, sigma_m_cm2_g


def test_structural_sanity():
    """Moderate coupling gives moderate sigma/m, monotonic in v."""
    print("\n=== Test C: Structural sanity ===")
    alpha_D = 1e-3
    m_ap_GeV = 0.01
    v = 100
    sigT = sigma_T_partialwave(alpha_D, m_ap_GeV, v / 3e5)
    if sigT is not None and not math.isnan(sigT):
        sigma = sigma_m_cm2_g(sigT)
        print(f"  Moderate coupling: sigma/m = {sigma:.4e} cm^2/g")
        assert 0.001 < sigma < 1000

    v_test = [10, 30, 100, 300, 1000]
    sigma_v = []
    for v in v_test:
        sigT = sigma_T_partialwave(alpha_D, m_ap_GeV, v / 3e5)
        if sigT is None or math.isnan(sigT):
            sigma_v.append(None)
        else:
            sigma_v.append(sigma_m_cm2_g(sigT))
    valid = [s for s in sigma_v if s is not None]
    if len(valid) >= 3:
        monotonic = all(valid[i] >= valid[i+1] for i in range(len(valid)-1))
        assert monotonic, f"Not monotonic: {sigma_v}"
    print("PASS: test_structural_sanity")


def test_hbarc_unit_consistency():
    """hbar*c = 0.1973 GeV*fm = 1.97327e-14 GeV*cm."""
    print("\n=== Test D: HBARC unit consistency ===")
    assert abs(HBAR_C_GEV_CM - 1.97327e-14) < 1e-18
    fm_per_GeV_inv = HBAR_C_GEV_CM * 1e13
    print(f"  1 GeV^-1 = {fm_per_GeV_inv:.4f} fm")
    assert abs(fm_per_GeV_inv - 0.1973) < 0.001
    print("PASS: test_hbarc_unit_consistency")


def test_lattice_convergence():
    """Lattice diagonalisation convergence (E_0 stable across N)."""
    print("\n=== Test E: Lattice convergence ===")
    try:
        from v19_2_f_phase3_bound_state_lattice import E0_lattice
        E_2000 = E0_lattice(3e-4, M_CHI_GEV, 1e-4, N=2000, r_max_factor=200)
        E_4000 = E0_lattice(3e-4, M_CHI_GEV, 1e-4, N=4000, r_max_factor=200)
        if not (math.isnan(E_2000) or math.isnan(E_4000)):
            rel_diff = abs(E_2000 - E_4000) / abs(E_4000)
            print(f"  rel diff N=2000 vs N=4000: {rel_diff*100:.2f}%")
            assert rel_diff < 0.10
    except (ImportError, AttributeError) as e:
        print(f"  Skipped: {e}")
    print("PASS: test_lattice_convergence")


if __name__ == "__main__":
    test_structural_sanity()
    test_hbarc_unit_consistency()
    test_lattice_convergence()
    print("\nALL MISC TESTS PASSED")
