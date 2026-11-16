"""Smoke test for R11 audit fixes — verifies syntactic + functional correctness
without trying to replicate the project's runtime sys.path dance.

Test 1: config.py PROJECT_ROOT
Test 2: config.py honors DM_SIDM_PROJECT_ROOT env var
Test 3: Bulk-renamed modules have valid syntax (py_compile)
Test 4: T39 test fix (a=1.5 in range returns finite, a=20 out of range returns -inf)
"""
import sys
import os
import py_compile
import importlib.util
from pathlib import Path

WSL_ROOT = Path("/home/lamkuenai/sidm-composite-dm-mediator")
sys.path.insert(0, str(WSL_ROOT))

print("=== Test 1: config.py PROJECT_ROOT ===")
import config
print(f"PROJECT_ROOT = {config.PROJECT_ROOT}")
assert config.PROJECT_ROOT.exists(), f"PROJECT_ROOT does not exist: {config.PROJECT_ROOT}"
print("OK")

print()
print("=== Test 2: config.py honors DM_SIDM_PROJECT_ROOT ===")
os.environ['DM_SIDM_PROJECT_ROOT'] = '/tmp/fake_path'
del sys.modules['config']
sys.path.insert(0, str(WSL_ROOT))
import config
print(f"PROJECT_ROOT (with env var) = {config.PROJECT_ROOT}")
assert str(config.PROJECT_ROOT) == '/tmp/fake_path', f"Env var not honored: {config.PROJECT_ROOT}"
print("OK")
del os.environ['DM_SIDM_PROJECT_ROOT']

print()
print("=== Test 3: Bulk-renamed modules have valid syntax ===")
targets = [
    "v0.1-prelim/code/aggregate_sparc.py",
    "v0.1-prelim/code/fit_single_galaxy.py",
    "v0.3-prelim/code/channels_v03.py",
    "v0.3-prelim/code/t8_v03_joint_fit.py",
    "v0.3-prelim/code/t32_fermi_dwarf_channel.py",
    "v0.3-prelim/code/t53_dark_rho_meson.py",
    "v0.3-prelim/code/t39_tier3_epsilon_alpha_joint_fit.py",
    "v0.3-prelim/tests/test_t39_tier3_epsilon_alpha.py",
    "config.py",
    "batch_utils.py",
    "tests/test_halo_and_likelihoods.py",
    "tests/test_sashimi_per_galaxy.py",
]
for t in targets:
    path = WSL_ROOT / t
    try:
        py_compile.compile(str(path), doraise=True)
        print(f"  OK: {t}")
    except py_compile.PyCompileError as e:
        print(f"  FAIL: {t}: {e}")
        raise

print()
print("=== Test 4: T39 a=1.5 returns finite, a=20 returns -inf ===")
# Load t39 by path to avoid sys.path conflicts
spec = importlib.util.spec_from_file_location(
    "t39",
    str(WSL_ROOT / "v0.3-prelim/code/t39_tier3_epsilon_alpha_joint_fit.py"),
)
t39 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t39)

# In-range
ll = t39.loglike_joint((-2.0, 1.5, -4.0, -3.0))
print(f"loglike_joint(-2.0, 1.5, -4.0, -3.0) = {ll}")
import math
assert math.isfinite(ll), f"Expected finite, got {ll}"
assert ll > -1e10, f"Expected > -1e10, got {ll}"
print("OK (a=1.5 in range, returns finite)")

# Out-of-range
ll_old = t39.loglike_joint((-2.0, 20.0, -4.0, -3.0))
print(f"loglike_joint(-2.0, 20.0, -4.0, -3.0) = {ll_old}")
assert ll_old == float('-inf'), f"Expected -inf, got {ll_old}"
print("OK (a=20 out of range, returns -inf — regression check)")

# Other out-of-range
ll_neg = t39.loglike_joint((-2.0, -3.0, -4.0, -3.0))
assert ll_neg == float('-inf'), f"Expected -inf, got {ll_neg}"
print("OK (a=-3 out of range, returns -inf)")

print()
print("=== ALL SMOKE TESTS PASS ===")