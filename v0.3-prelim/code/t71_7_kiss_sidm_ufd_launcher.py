#!/usr/bin/env python3
"""
T71.7 launcher — run KiSS-SIDM T38a N=5e4 dwarf at extended timeout.

This script invokes kiss_sidm_julia_bridge.run_canonical_kiSS_sidm with the
dwarf halo parameters from T38a, but with KISS_SIDM_TIMEOUT_S=7200 (2 hr)
to allow the simulation to actually complete (T38a hit our wrapper's 3600s
timeout previously).

Output: v0.3-prelim/data/results/t71_7_kiss_sidm_ufd_n5e4.json
"""
import json
import os
import sys
import time
from pathlib import Path

PROJECT = Path("/home/lamkuenai/sidm-composite-dm-mediator")
sys.path.insert(0, str(PROJECT / "v0.3-prelim" / "code"))

# CRITICAL: set env var BEFORE importing the bridge
os.environ["KISS_SIDM_TIMEOUT_S"] = "7200"  # 2 hours

from kiss_sidm_julia_bridge import run_canonical_kiSS_sidm

# Dwarf halo parameters from T38a (v0.3-prelim/data/results/t38_dwarf_kiss_sidm_higher_N.json)
DWARF_PARAMS = dict(
    N=50_000,
    t_end_Gyr=10.0,
    sigma_m_cm2_per_g=5.0,         # dwarf-scale sigma/m (T38a)
    rho_s_Msun_per_kpc3=2.73e7,    # dwarf halo scale density
    r_s_kpc=0.5477,                # dwarf halo scale radius
    seed=42,
    snapshot_count=10,
)

RESULTS_DIR = PROJECT / "v0.3-prelim" / "data" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 80)
print("T71.7 — KiSS-SIDM UFD N=5e4 re-run with extended timeout")
print("=" * 80)
print(f"  N = {DWARF_PARAMS['N']}")
print(f"  t_end = {DWARF_PARAMS['t_end_Gyr']} Gyr")
print(f"  sigma/m = {DWARF_PARAMS['sigma_m_cm2_per_g']} cm^2/g")
print(f"  rho_s = {DWARF_PARAMS['rho_s_Msun_per_kpc3']:.2e} Msun/kpc^3")
print(f"  r_s = {DWARF_PARAMS['r_s_kpc']:.4f} kpc")
print(f"  KISS_SIDM_TIMEOUT_S = {os.environ['KISS_SIDM_TIMEOUT_S']}s (2 hr)")
print(f"  Upstream: /home/lamkuenai/KiSS-SIDM (DSMC v0.0.1, Gurian+May 2025)")
print()

t0 = time.time()
print(f"[{time.strftime('%H:%M:%S')}] Launching KiSS-SIDM dwarf N=5e4 simulation...")
sys.stdout.flush()

result = run_canonical_kiSS_sidm(**DWARF_PARAMS)
elapsed = time.time() - t0

# Attach meta
result["test"] = "T71_7_kiss_sidm_ufd_n5e4"
result["direction"] = (
    "T71.7: Re-run T38a dwarf KiSS-SIDM at N=5e4 with extended timeout "
    "(3600s -> 7200s) via KISS_SIDM_TIMEOUT_S env var. Goal: complete the "
    "dwarf simulation that T38a (2026-08-22) killed at 1 hour."
)
result["upstream_repo"] = "https://gitlab.com/Socob/KiSS-SIDM"
result["upstream_local_path"] = "/home/lamkuenai/KiSS-SIDM"
result["upstream_package_version"] = "DSMC v0.0.1"
result["wrapper_timeout_seconds"] = 7200
result["wall_seconds_actual"] = elapsed
result["wall_human"] = f"{elapsed/60:.1f} min"

out_path = RESULTS_DIR / "t71_7_kiss_sidm_ufd_n5e4.json"
out_path.write_text(json.dumps(result, indent=2, default=str))
win_path = Path("/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results/t71_7_kiss_sidm_ufd_n5e4.json")
if win_path.parent.exists():
    win_path.write_text(json.dumps(result, indent=2, default=str))

print()
print(f"[{time.strftime('%H:%M:%S')}] Completed in {elapsed/60:.1f} min ({elapsed:.1f}s)")
print(f"Result status: {result.get('status', 'unknown')}")
if result.get('status') == 'success':
    print(f"  core_rho = {result.get('core_rho')}")
    print(f"  core_r   = {result.get('core_r')}")
    print(f"  r_core/r_s = {result.get('r_core_over_rs')}")
    print(f"  snapshots produced = {result.get('n_snapshots', 'unknown')}")
elif result.get('status') == 'error':
    print(f"  returncode = {result.get('returncode')}")
    print(f"  stderr (last 500 chars) = {result.get('stderr', '')[-500:]}")
elif result.get('status') == 'error_timeout':
    print(f"  STILL hit 7200s timeout — even 2 hr not enough at N=5e4 dwarf")
print(f"\nResult written to: {out_path}")
print(f"                   {win_path}")