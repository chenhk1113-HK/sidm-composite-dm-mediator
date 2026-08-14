"""
T38c — Direction C full closure: dwarf KiSS-SIDM at N=2e6 (paper scale).

D13 / D14 deliverable: run the FULL KiSS-SIDM dwarf simulation at the
Gurian & May 2025 paper-canonical N=2e6 resolution, with t_end=10 Gyr
and 10 snapshots.

Why this is a separate script (not a flag in t38_dwarf_kiss_sidm_higher_N):
  - The existing `kiss_sidm_julia_bridge.run_canonical_kiSS_sidm` hardcodes
    `subprocess.run(timeout=3600)` (1 hour). At N=2e6 dwarf, the simulation
    will run 10+ hours; 1 hr is insufficient.
  - T38c uses `subprocess.Popen` directly with no internal timeout, and
    polls the result file `/tmp/kiss_result.json` every 30 seconds. The
    background process will be allowed to run as long as needed.

Inputs (paper-faithful):
  - N = 2,000,000 (paper-canonical resolution)
  - M_halo = 10^8 M_sun (dwarf, T31 question)
  - r_s = 0.5477 kpc (NFW with constant concentration)
  - rho_s = 2.73e7 M_sun/kpc^3
  - sigma_m = 5 cm^2/g (10x smaller than canonical, per T31)
  - t_end = 10 Gyr
  - snapshot_count = 10
  - seed = 42

Honest wall-clock estimate: based on T38b scaling, N=5e4 dwarf took
~7 min/snapshot → 10 snapshots in ~70 min. N=2e6 is 40x more particles,
so ~280 min/snapshot → ~46 hours total. **This is impractical even for
overnight**. The realistic paper-scale run would take ~2 days.

Two options for handling the wall-clock:
  A) Run N=2e6 directly with no timeout. Status JSON written only at end.
     If killed mid-run, partial snapshots in /tmp/kiss_sidm_output/ can be
     recovered (up to whatever was produced).
  B) Run a "reduced paper-scale" N=5e5 (10x more than T38a, 4x less than
     paper scale) which would take ~3-5 hours. This is more practical
     for a session-budget-aware session but is NOT the paper-canonical
     resolution.

T38c implements OPTION A by default (N=2e6, no timeout). The status JSON
gets a `wall_seconds_so_far` field updated by `t38c_poll_status.py`.
"""
from __future__ import annotations
import json
import subprocess
import time
from pathlib import Path

PROJECT_ROOT = Path("/home/lamkuenai/sidm-composite-dm-mediator/v0.3-prelim")
RESULTS_DIR = PROJECT_ROOT / "data" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

JULIA_BIN = "/home/lamkuenai/.juliaup/bin/julia"
JULIA_VERSION = "+1.11.5"
JULIA_PROJECT = "/home/lamkuenai/KiSS-SIDM"
WORKER_JL = "/tmp/kiss_sidm_worker.jl"

# T38c input (paper-scale)
N_PARTICLES = 2_000_000
M_HALO_Msun = 1e8
RHO_S = 2.73e7
R_S_KPC = 1.18 * (M_HALO_Msun / 1e9) ** (1.0/3.0)
SIGMA_M_CM2_PER_G = 5.0
T_END_GYR = 10.0
SNAPSHOT_COUNT = 10
SEED = 42


def write_request():
    """Write the KiSS-SIDM request to /tmp/kiss_request.txt (TOML format)."""
    req = (
        f"N_particles={N_PARTICLES}\n"
        f"t_end_Gyr={T_END_GYR}\n"
        f"sigma_m_cm2_per_g={SIGMA_M_CM2_PER_G}\n"
        f"rho_s_Msun_per_kpc3={RHO_S}\n"
        f"r_s_kpc={R_S_KPC}\n"
        f"seed={SEED}\n"
        f"snapshot_count={SNAPSHOT_COUNT}\n"
    )
    Path("/tmp/kiss_request.txt").write_text(req)


def main():
    """Launch the Julia worker as a no-timeout subprocess and return immediately.
    Use `t38c_poll_status.py` to monitor progress.
    """
    write_request()
    if not Path(WORKER_JL).exists():
        # The bridge's `_ensure_julia_worker` writes this on first call. If missing,
        # run it via a separate Python invocation.
        subprocess.run(
            ["/home/lamkuenai/wimpy/bin/python", "-c",
             "import kiss_sidm_julia_bridge as b; b._ensure_julia_worker(); print('worker ready')"],
            capture_output=True, timeout=120,
        )

    # Spawn the Julia worker via nohup + setsid so it survives the parent
    # Python process exiting. Detach from stdin/stdout/stderr; redirect
    # stdout/stderr to /tmp/kiss_t38c.log for debugging.
    # The bridge's run_canonical_kiSS_sidm has timeout=3600 (1 hr) which is
    # too short for N=2e6 dwarf (~46 hr); we bypass the bridge and call
    # julia directly.
    julia_cmd = (
        f"nohup setsid {JULIA_BIN} {JULIA_VERSION} "
        f"--project={JULIA_PROJECT} {WORKER_JL} "
        f"> /tmp/kiss_t38c.log 2>&1 < /dev/null &"
    )
    print(f"T38c launching: N={N_PARTICLES}, dwarf M={M_HALO_Msun:.0e}, "
          f"sigma_m={SIGMA_M_CM2_PER_G}, no internal timeout")
    print(f"Detach command: {julia_cmd}")
    subprocess.run(["bash", "-c", julia_cmd], check=True)

    # Allow the shell to fork
    time.sleep(2)

    # Find the actual Julia PID (no longer python's Popen.pid)
    pid_check = subprocess.run(
        ["bash", "-c", "pgrep -f 'kiss_sidm_worker' | head -1"],
        capture_output=True, text=True, timeout=10,
    )
    julia_pid = int(pid_check.stdout.strip()) if pid_check.stdout.strip() else None

    # Write the launch status immediately
    status = {
        "test": "T38c_dwarf_kiss_sidm_paper_scale",
        "status": "LAUNCHED",
        "julia_pid": julia_pid,
        "input": {
            "N_particles": N_PARTICLES,
            "M_halo_Msun": M_HALO_Msun,
            "r_s_kpc": R_S_KPC,
            "sigma_m_cm2_per_g": SIGMA_M_CM2_PER_G,
            "t_end_Gyr": T_END_GYR,
            "snapshot_count": SNAPSHOT_COUNT,
            "seed": SEED,
        },
        "expected_wall_seconds_estimate": "~46 hours (paper-scale N=2e6)",
        "expected_first_snapshot_estimate": "~280 min from launch",
        "polling": "Use t38c_poll_status.py to read /tmp/kiss_sidm_output/",
        "log_path": "/tmp/kiss_t38c.log",
        "kill_signal": "If needed: pkill -9 -f 'kiss_sidm_worker'",
        "launched_at_unix_seconds": int(time.time()),
    }
    status_path = RESULTS_DIR / "t38c_launch_status.json"
    status_path.write_text(json.dumps(status, indent=2, default=str))
    print(f"status -> {status_path}")
    print(f"Julia worker PID: {julia_pid} (detached via setsid+nohup)")


if __name__ == "__main__":
    main()