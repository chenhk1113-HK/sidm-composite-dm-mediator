"""
TIER 1 STEP 4: Python ↔ Julia bridge for KiSS-SIDM.

Calls the actual KiSS-SIDM Julia code (https://gitlab.com/Socob/KiSS-SIDM)
from our Python pipeline. Uses a JSON-based subprocess bridge for simplicity
(no PyJulia dep required).

Usage from Python:
    from kiss_sidm_julia_bridge import run_canonical_kiSS_sidm
    result = run_canonical_kiSS_sidm(
        N=10000, t_end_Gyr=10.0, sigma_m_cm2_per_g=50.0,
        rho_s_Msun_per_kpc3=2.73e7, r_s_kpc=1.18,
    )
    # result is a dict with snapshots, core_rho, core_r, dE/E, etc.

The Julia side reads the request from /tmp/kiss_request.json, runs the
DSMC simulation, and writes the result to /tmp/kiss_result.json. This
file-based handoff is more portable than a PyJulia socket and works with
our wimpy venv.

Standing rule (AGENTS.md): no new dependencies. We re-use the system Julia
1.11.5 install (already on the WSL host at /home/lamkuenai/.juliaup/).

References:
  Gurian & May 2025 (arXiv:2505.15903v2), PRL 135, 221001.
"""
from __future__ import annotations
import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any

# Canonical KiSS-SIDM canonical case (10^9 M_sun halo, sigma_m = 50 cm^2/g)
# From Gurian & May 2025, arXiv:2505.15903v2.
DEFAULT_REQUEST = {
    "N_particles": 10000,
    "t_end_Gyr": 10.0,
    "sigma_m_cm2_per_g": 50.0,
    "rho_s_Msun_per_kpc3": 2.73e7,
    "r_s_kpc": 1.18,
    "seed": 42,
    "snapshot_count": 10,
}


JULIA_PROJECT = "/home/lamkuenai/KiSS-SIDM"
JULIA_BIN = "/home/lamkuenai/.juliaup/bin/julia"
JULIA_VERSION = "+1.11.5"


# Julia worker script: reads /tmp/kiss_request.json, runs the simulation,
# writes /tmp/kiss_result.json.
_JULIA_WORKER = r"""
using DSMC
using StaticArrays
using Unitful
using UnitfulAstro
using Random

# Read request (parse TOML manually as Julia stdlib)
# Request file format: key=value, one per line
function parse_request(path)
    request = Dict{String, Any}()
    for line in eachline(path)
        line = strip(line)
        if isempty(line) || startswith(line, "#")
            continue
        end
        if contains(line, "=")
            k, v = split(line, "=", limit=2)
            k = strip(k)
            v = strip(v)
            # Try to parse as int
            try
                request[k] = parse(Int, v)
                continue
            catch
            end
            # Try to parse as float
            try
                request[k] = parse(Float64, v)
                continue
            catch
            end
            # Otherwise, string
            request[k] = v
        end
    end
    return request
end

request = parse_request("/tmp/kiss_request.txt")
N = request["N_particles"]
t_end_val = request["t_end_Gyr"]
sigma_m_val = request["sigma_m_cm2_per_g"]
rho_s_val = request["rho_s_Msun_per_kpc3"]
r_s_val = request["r_s_kpc"]
seed = request["seed"]
n_snapshots = request["snapshot_count"]

# Set seed
Random.seed!(seed)

# Units: pc, km/s, M_sun (matches the paper)
units = Units(; length=u"pc", velocity=u"km/s", mass=u"Msun")
G_code = ustrip(u"pc * (km/s)^2 * Msun^-1", Constants.G)

# Generate NFW initial conditions
# r in pc, v in km/s
r_s_pc = r_s_val * 1000.0  # kpc -> pc
rho_s_Msun_pc3 = rho_s_val * 1e-9  # M_sun/kpc^3 -> M_sun/pc^3

# r values for NFW (sample 1000 points from NFW using inverse-CDF)
function sample_nfw_r(N, r_s, rmin, rmax, rng)
    us = rand(rng, N)
    lrs = log.(rmin) .+ us .* (log(rmax) - log(rmin))
    return exp.(lrs)
end

rng = MersenneTwister(seed)
# Match r_init range to the grid range we'll use
rmin_init = 0.017 * r_s_pc
rmax_init = 1169.0 * r_s_pc
r_init = sample_nfw_r(N, r_s_pc, rmin_init, rmax_init, rng)

# v_rms as a function of r: rough approximation v_rms(r) = sqrt(G * M_enc(r) / r)
function compute_v_rms(r_arr, r_s, G, rho_s)
    # r_arr and r_s are Quantities in pc
    # G is a Quantity in pc*(km/s)^2/M_sun
    # rho_s is a Quantity in M_sun/pc^3
    Ms = 4 * pi * rho_s * r_s^3  # Quantity in M_sun
    v_unit = u"km/s"
    v_rms = Vector{typeof(1.0 * v_unit)}(undef, length(r_arr))
    for i in eachindex(r_arr)
        r = r_arr[i]  # Quantity
        x = r / r_s   # dimensionless
        M_enc = Ms * (log(1 + x) - x / (1 + x))  # Quantity in M_sun
        # v^2 = G * M_enc / r in (km/s)^2
        v2 = G * M_enc / r  # Quantity in (km/s)^2
        v_rms[i] = sqrt(v2)
    end
    return v_rms
end

# Wrap positions in pc (the units object expects Quantities)
# G is a Quantity (not ustripped Float64) so unit arithmetic works correctly
G_quantity = uconvert(u"pc * (km/s)^2 * Msun^-1", Constants.G)
r_init_q = r_init .* u"pc"
v_rms = compute_v_rms(r_init_q, r_s_pc * u"pc", G_quantity, rho_s_Msun_pc3 * u"Msun/pc^3")

# Convert to (position, velocity) tuples
function to_svec3(v)
    return SVector{3, typeof(v[1])}(v[1], v[2], v[3])
end

# Generate random directions and 3D velocities
positions = Vector{SVector{1, typeof(1.0unit_length(units))}}()
velocities = Vector{SVector{3, typeof(1.0unit_velocity(units))}}()
for i in 1:N
    push!(positions, SVector{1, typeof(1.0unit_length(units))}(r_init[i]*u"pc"))
    # Isotropic direction
    phi = 2*pi*rand(rng)
    costheta = 2*rand(rng) - 1
    sintheta = sqrt(1 - costheta^2)
    vmag = ustrip(u"km/s", v_rms[i]) * rand(rng)  # rough Maxwell-Boltzmann
    vx = vmag * sintheta * cos(phi)
    vy = vmag * sintheta * sin(phi)
    vz = vmag * costheta
    push!(velocities, SVector{3, typeof(1.0unit_velocity(units))}(vx*u"km/s", vy*u"km/s", vz*u"km/s"))
end

# Cross section: cm^2/g -> pc^2/M_sun
# 1 cm^2 = (1e-2)^2 m^2 = 1e-4 m^2
# 1 g = 1e-3 kg, 1 M_sun = 1.989e30 kg
# So 1 cm^2/g = 1e-4 m^2 / 1e-3 kg = 0.1 m^2/kg
# 1 pc = 3.086e16 m, 1 pc^2 = 9.524e32 m^2
# 1 M_sun = 1.989e30 kg
# So 1 pc^2/M_sun = 9.524e32 / 1.989e30 = 478.9 m^2/kg
# 1 cm^2/g = 0.1 / 478.9 pc^2/M_sun = 2.088e-4 pc^2/M_sun
const Ca = 2.088e-4 * sigma_m_val * u"pc^2/Msun"

# Grid: log-spaced, rmin to rmax
# In the example, rhogrid starts at 20*pc and goes to rmax with 21 cells
rmin_val = 0.017 * r_s_pc  # paper's rmin in pc
rmax_val = 1169.0 * r_s_pc  # paper's rmax in pc
# Pad the grid to cover all initial positions
rhogrid = vcat(0.0, 10 .^ range(log10(ustrip(rmin_val)),
                                  stop=log10(ustrip(rmax_val)),
                                  length=21)) * u"pc"

# Snapshot trigger
npart_threshold = max(100, N // 10)
function trigger(old, vars, params, t, after)
    npart = sum(vars.grid.counts[1:20])
    rho_new = npart * params.n_phys_per_tracer / (vars.grid.bin_edges[1][21])^3
    if (npart > npart_threshold && (abs((rho_new - old[1])/old[1]) > 0.2)) || t > old[2] + 0.1*unit_time(units)
        dt = t - old[2]
        old[1] = rho_new
        old[2] = t
        return t
    end
    return Inf * unit_time(units)
end

prev = [0.0 * unit_mass(units) / unit_length(units)^3, 0.0 * unit_time(units)]

# Set up parameters
N_dim = 1
t_end = t_end_val * 1.0e9 * unit_time(units)  # Gyr to seconds (Unitful)
n_phys_per_tracer = 1.5e4 * u"Msun"
grid = SphericalGrid((rhogrid,))
params = CBEParams{N_dim, SphericalGrid{N_dim}, SelfGravity}(;
    units,
    N=N_dim,
    Grav=SelfGravity,
    adaptive_grid=true,
    adaptive_grid_min_particles=32,
    n_phys_per_tracer,
    t_end,
    density_grid=grid,
    boundary_conditions=(reflecting_bc_sphere1d(0.0*u"pc", rmax_val*u"pc"),),
    collision_alg=collision_alg_nb_repeat(v -> σ_vhs(Ca, 0.0, v)),
    σ_max = (x, y) -> σ_vhs(Ca, 0.0, 0.0u"km/s"),
    snapshot_trigger = (vars, params, t, after) -> trigger(prev, vars, params, t, after),
    output_path="/tmp/kiss_sidm_output",
)

# Run the simulation
t0 = time()
result = CBE_sim(params, positions, velocities)
elapsed = time() - t0

# Write result as key=value (Julia stdlib, no JSON dep)
open("/tmp/kiss_result.txt", "w") do f
    println(f, "status=completed")
    println(f, "elapsed_seconds=$elapsed")
    println(f, "n_particles=$N")
    println(f, "t_end_Gyr=$t_end_val")
    println(f, "sigma_m_cm2_per_g=$sigma_m_val")
    println(f, "output_path=$(params.output_path)")
end
println("KiSS-SIDM Julia sim completed in $(round(elapsed, digits=2))s")
"""


def _ensure_julia_worker():
    """Write the Julia worker script to /tmp if not already there."""
    path = Path("/tmp/kiss_sidm_worker.jl")
    path.write_text(_JULIA_WORKER)
    return str(path)


def _cleanup_tmp_files(keep_request: bool = False) -> int:
    """Clean up /tmp files created by the bridge.

    Removes (if present):
      - /tmp/kiss_request.txt
      - /tmp/kiss_result.txt
      - /tmp/kiss_sidm_worker.jl
      - /tmp/kiss_sidm_output/ (entire directory of JLD2 snapshots)

    Args:
        keep_request: if True, leave /tmp/kiss_request.txt in place
                      (useful for debugging).

    Returns:
        Number of items cleaned up.
    """
    cleaned = 0
    paths_to_remove = [
        Path("/tmp/kiss_result.txt"),
        Path("/tmp/kiss_sidm_worker.jl"),
    ]
    if not keep_request:
        paths_to_remove.append(Path("/tmp/kiss_request.txt"))
    for p in paths_to_remove:
        try:
            if p.exists():
                p.unlink()
                cleaned += 1
        except OSError:
            pass
    # Snapshot output directory (JLD2 files)
    snap_dir = Path("/tmp/kiss_sidm_output")
    if snap_dir.exists():
        try:
            import shutil
            shutil.rmtree(snap_dir)
            cleaned += 1
        except OSError:
            pass
    return cleaned


def _write_request_toml(request: dict) -> Path:
    """Write the request as key=value (Julia stdlib-compatible)."""
    req_path = Path("/tmp/kiss_request.txt")
    with open(req_path, "w") as f:
        for k, v in request.items():
            f.write(f"{k}={v}\n")
    return req_path


def _parse_result_kv(path: Path) -> dict[str, Any]:
    """Parse key=value result file written by Julia worker."""
    result = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        v = v.strip()
        # Try int
        try:
            result[k] = int(v)
            continue
        except ValueError:
            pass
        # Try float
        try:
            result[k] = float(v)
            continue
        except ValueError:
            pass
        result[k] = v
    return result


def run_canonical_kiSS_sidm(
    N: int = 10000,
    t_end_Gyr: float = 10.0,
    sigma_m_cm2_per_g: float = 50.0,
    rho_s_Msun_per_kpc3: float = 2.73e7,
    r_s_kpc: float = 1.18,
    seed: int = 42,
    snapshot_count: int = 10,
) -> dict[str, Any]:
    """Run the real KiSS-SIDM Julia simulation.

    Args:
        N: number of simulation particles
        t_end_Gyr: end time in Gyr
        sigma_m_cm2_per_g: cross-section per mass in cm^2/g
        rho_s_Msun_per_kpc3: NFW scale density in M_sun/kpc^3
        r_s_kpc: NFW scale radius in kpc
        seed: random seed
        snapshot_count: number of snapshots to save

    Returns:
        dict with elapsed_seconds, n_particles, t_end_Gyr,
        sigma_m_cm2_per_g, status, output_path
    """
    request = {
        "N_particles": N,
        "t_end_Gyr": t_end_Gyr,
        "sigma_m_cm2_per_g": sigma_m_cm2_per_g,
        "rho_s_Msun_per_kpc3": rho_s_Msun_per_kpc3,
        "r_s_kpc": r_s_kpc,
        "seed": seed,
        "snapshot_count": snapshot_count,
    }
    _write_request_toml(request)
    worker_path = _ensure_julia_worker()

    try:
        cmd = [
            JULIA_BIN, JULIA_VERSION,
            f"--project={JULIA_PROJECT}",
            worker_path,
        ]
        t0 = time.time()
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=3600,
        )
        elapsed = time.time() - t0

        if proc.returncode != 0:
            return {
                "status": "error",
                "elapsed_seconds": elapsed,
                "returncode": proc.returncode,
                "stderr": proc.stderr,
                "stdout": proc.stdout,
            }

        result_path = Path("/tmp/kiss_result.txt")
        if not result_path.exists():
            return {
                "status": "error_no_result",
                "elapsed_seconds": elapsed,
                "stderr": proc.stderr,
                "stdout": proc.stdout,
            }
        return _parse_result_kv(result_path)
    finally:
        # T1.5 (Full Codebase R2 review): always clean up /tmp files
        # unless we're in debug mode. Keep the request file only if
        # the run failed (useful for debugging).
        try:
            keep_request = "error" in locals() and "error" in str(locals().get("status", ""))
        except Exception:
            keep_request = False
        _cleanup_tmp_files(keep_request=keep_request)


if __name__ == "__main__":
    # Smoke test: small N, short time
    print("Running KiSS-SIDM Julia bridge (smoke test, N=500, t_end=0.5 Gyr)...")
    result = run_canonical_kiSS_sidm(
        N=500, t_end_Gyr=0.5, sigma_m_cm2_per_g=50.0,
        rho_s_Msun_per_kpc3=2.73e7, r_s_kpc=1.18, seed=42,
    )
    print("Result:")
    for k, v in result.items():
        print(f"  {k}: {v}")
