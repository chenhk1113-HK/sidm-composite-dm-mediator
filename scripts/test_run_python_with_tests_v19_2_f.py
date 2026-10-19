"""Real v19.2-F smoke test for run_python_with_tests.

Imports from TWO constants files (the project has them split):
  - root constants.py:  ALPHA_D, G_CHI, M_CHI_GEV (convention lock)
  - scripts/constants.py: V_TARGET_KMS, SIGMA_PEAK_CM2_PER_G, SIGMA_KMS (v19.2-F phenomenology)
"""
import sys
sys.path.insert(0, r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\scripts")
from run_python_with_tests import run_python_with_tests
import json

production_code = r'''
import math
import importlib.util
from pathlib import Path

# Load root constants.py (convention: alpha_D, g, kappa) by absolute path
_spec_root = importlib.util.spec_from_file_location(
    "root_constants",
    r"C:/Users/lamkuenai/projects/sidm-composite-dm-mediator/constants.py"
)
_root_c = importlib.util.module_from_spec(_spec_root)
_spec_root.loader.exec_module(_root_c)

# Load scripts/constants.py (v19.2-F phenomenology: V_TARGET_KMS, etc.) by absolute path
_spec_v19 = importlib.util.spec_from_file_location(
    "v19_constants",
    r"C:/Users/lamkuenai/projects/sidm-composite-dm-mediator/scripts/constants.py"
)
_v19 = importlib.util.module_from_spec(_spec_v19)
_spec_v19.loader.exec_module(_v19)

# Convention constants
ALPHA_D = _root_c.ALPHA_D
G_CHI = _root_c.G_CHI
M_CHI_GEV = _root_c.M_CHI_GEV

# v19.2-F phenomenological constants
V_TARGET_KMS = _v19.V_TARGET_KMS
SIGMA_PEAK_CM2_PER_G = _v19.SIGMA_PEAK_CM2_PER_G
SIGMA_KMS = _v19.SIGMA_KMS

def sigma_m_flexible(v_kms, a_slope, sigma_0, v_target, sigma_peak, sigma_1):
    background = sigma_0 * (100.0 / v_kms) ** a_slope
    resonance = sigma_peak * math.exp(-0.5 * ((v_kms - v_target) / sigma_1) ** 2)
    return background + resonance
'''

test_code = r'''
def test_alpha_d_convention():
    """alpha_D must satisfy g^2 = 4*pi*alpha_D."""
    import math
    expected_g = math.sqrt(4.0 * math.pi * ALPHA_D)
    assert abs(G_CHI - expected_g) < 1e-14, f"G_CHI mismatch: {G_CHI} vs {expected_g}"

def test_cloud9_peak():
    """At v=V_TARGET_KMS, sigma_m should be near SIGMA_PEAK_CM2_PER_G."""
    sm = sigma_m_flexible(V_TARGET_KMS, 0.3, 0.07, V_TARGET_KMS, SIGMA_PEAK_CM2_PER_G, SIGMA_KMS)
    assert 150 < sm < 200, f"Cloud-9 peak out of range: {sm}"

def test_born_limit():
    """At high v (cluster scale), sigma_m should be small."""
    sm = sigma_m_flexible(1000, 0.3, 0.07, V_TARGET_KMS, SIGMA_PEAK_CM2_PER_G, SIGMA_KMS)
    assert sm < 0.1, f"Cluster-scale sigma_m too large: {sm}"

def test_dSph_exclusion():
    """At v=10 km/s (dSph scale), sigma_m should be small (Horigome bound)."""
    sm = sigma_m_flexible(10, 0.3, 0.07, V_TARGET_KMS, SIGMA_PEAK_CM2_PER_G, SIGMA_KMS)
    assert sm < 1.0, f"dSph sigma_m too large: {sm}"
'''

print("=== Real v19.2-F physics test (split constants via importlib) ===")
r = run_python_with_tests(production_code, test_code)
print(f"status: {r['status']}")
print(f"message: {r['message']}")
if r['failed_tests']:
    print("failed tests:")
    for t in r['failed_tests']:
        print(f"  {t}")
print()
print("--- stdout (last 2000 chars) ---")
print(r['stdout'][-2000:])
