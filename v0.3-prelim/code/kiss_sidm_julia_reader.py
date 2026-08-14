"""
TIER 1 STEP 5: Read KISS-SIDM JLD2 snapshots into a Python dict.

The KiSS-SIDM Julia code writes JLD2 snapshots to a directory. Each
snapshot has:
  - time: simulation time
  - positions: N particles (radial)
  - velocities: N particles (3D)
  - density_grid: 22 bin edges
  - metadata: git, julia, time info

This module reads all snapshots, computes the density profile, the
velocity dispersion, and writes a summary JSON to the project results
directory.

Standing rule (AGENTS.md): no new dependencies. The Julia stack is
already installed for the bridge, so we just spawn a Julia worker
to read JLD2 files (no Python library can do that natively without
h5py + the right JLD2 schema knowledge).

References:
  Gurian & May 2025 (arXiv:2505.15903v2), PRL 135, 221001.
"""
from __future__ import annotations
import json
import subprocess
import time
from pathlib import Path
from typing import Any

# Reuse bridge settings
JULIA_PROJECT = "/home/lamkuenai/KiSS-SIDM"
JULIA_BIN = "/home/lamkuenai/.juliaup/bin/julia"
JULIA_VERSION = "+1.11.5"


# Julia reader: reads JLD2 snapshots, aggregates, writes JSON
_JULIA_READER = r"""
using DSMC, JLD2, Unitful, UnitfulAstro

snap_dir = ARGS[1]
out_path = ARGS[2]

# Manual JSON writer (no JSON.jl dependency)
function json_escape(s::AbstractString)
    s = replace(s, "\\" => "\\\\")
    s = replace(s, "\"" => "\\\"")
    s = replace(s, "\n" => "\\n")
    return s
end

function write_json_value(f, v, indent::Int)
    if v isa Number
        print(f, v)
    elseif v isa AbstractString
        print(f, "\"", json_escape(v), "\"")
    elseif v isa AbstractVector
        print(f, "[")
        for (i, x) in enumerate(v)
            i > 1 && print(f, ",")
            write_json_value(f, x, indent)
        end
        print(f, "]")
    elseif v isa AbstractDict
        print(f, "{")
        first = true
        for (k, x) in v
            first || print(f, ",")
            first = false
            print(f, "\"", json_escape(string(k)), "\":")
            write_json_value(f, x, indent)
        end
        print(f, "}")
    else
        # Fallback: stringify
        print(f, "\"", json_escape(string(v)), "\"")
    end
end

# Read all snap_*.jld2 files, sorted numerically (not lexically)
function parse_snap_num(fname)
    m = match(r"snap_(\d+)\.jld2", fname)
    return m === nothing ? 0 : parse(Int, m.captures[1])
end
files = sort(filter(f -> startswith(f, "snap_") && endswith(f, ".jld2"),
                readdir(snap_dir)), by=parse_snap_num)
println("Reading ", length(files), " snapshots from ", snap_dir)

if isempty(files)
    println("ERROR: no snapshots found")
    exit(1)
end

# Read first snapshot for grid and metadata
data1 = load(joinpath(snap_dir, files[1]))
grid_edges = data1["density_grid"].bin_edges[1]  # 22 bin edges
n_bins = length(grid_edges) - 1

# Bin centers in pc
r_bins_pc = [(ustrip(u"pc", grid_edges[i]) + ustrip(u"pc", grid_edges[i+1])) / 2 for i in 1:n_bins]
r_over_rs = r_bins_pc ./ 1180.0  # r_s = 1.18 kpc = 1180 pc

# Initialize aggregation
n_snaps = length(files)
time_Gyr = zeros(Float64, n_snaps)
rho_over_rhos = zeros(Float64, n_snaps, n_bins)
v2_mean = zeros(Float64, n_snaps, n_bins)
n_per_bin = zeros(Int64, n_snaps, n_bins)

for (i, fname) in enumerate(files)
    data = load(joinpath(snap_dir, fname))
    t_s = ustrip(u"s", data["time"])
    time_Gyr[i] = t_s / (3.15576e16)  # s to Gyr
    positions = data["positions"]
    velocities = data["velocities"]
    N = length(positions)

    # Bin particles by radius
    for j in 1:N
        r = ustrip(u"pc", positions[j][1])
        v = velocities[j]
        v2 = ustrip(u"km^2/s^2", v[1]^2 + v[2]^2 + v[3]^2)
        # Find bin
        bin_idx = searchsortedlast(grid_edges, r * u"pc")
        if 1 <= bin_idx <= n_bins
            n_per_bin[i, bin_idx] += 1
            v2_mean[i, bin_idx] += v2
        end
    end

    # Compute density per bin
    for b in 1:n_bins
        V_shell = (4 * pi / 3) * (ustrip(u"pc", grid_edges[b+1])^3 - ustrip(u"pc", grid_edges[b])^3)
        m_per_particle = data1["params"].n_phys_per_tracer
        m_Msun = ustrip(u"Msun", m_per_particle)
        rho_Msun_pc3 = n_per_bin[i, b] * m_Msun / V_shell
        rho_s_Msun_pc3 = 2.73e-2
        rho_over_rhos[i, b] = rho_Msun_pc3 / rho_s_Msun_pc3
        if n_per_bin[i, b] > 0
            v2_mean[i, b] /= n_per_bin[i, b]
        end
    end
end

# Write JSON manually
open(out_path, "w") do f
    print(f, "{")
    print(f, "\"test\":\"real_kiSS_sidm_aggregated\",")
    print(f, "\"n_snapshots\":", n_snaps, ",")
    print(f, "\"r_over_rs\":")
    write_json_value(f, r_over_rs, 0)
    print(f, ",")
    print(f, "\"time_Gyr\":")
    write_json_value(f, time_Gyr, 0)
    print(f, ",")
    print(f, "\"rho_over_rhos\":")
    write_json_value(f, rho_over_rhos, 0)
    print(f, ",")
    print(f, "\"v2_mean_km2_s2\":")
    write_json_value(f, v2_mean, 0)
    print(f, ",")
    print(f, "\"n_per_bin\":")
    write_json_value(f, n_per_bin, 0)
    print(f, ",")
    print(f, "\"canonical_halo\":{\"M_halo_Msun\":1e9,\"rho_s_Msun_kpc3\":2.73e7,\"r_s_kpc\":1.18,\"sigma_m_cm2_per_g\":50.0}")
    print(f, "}")
end
println("Wrote ", out_path)
println("n_snapshots = ", n_snaps)
println("n_bins = ", n_bins)
println("time range = ", time_Gyr[1], " to ", time_Gyr[end], " Gyr")
println("max rho/rho_s = ", maximum(rho_over_rhos))
nonzero_rho = rho_over_rhos[rho_over_rhos .> 0]
println("min nonzero rho/rho_s = ", isempty(nonzero_rho) ? 0 : minimum(nonzero_rho))
"""


def aggregate_kiss_snapshots(snap_dir: str | Path, out_path: str | Path) -> dict[str, Any]:
    """Read all JLD2 snapshots from snap_dir and write aggregated JSON to out_path.

    Returns the dict written to out_path.
    """
    snap_dir = Path(snap_dir)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Write Julia reader to a temp file
    reader_path = Path("/tmp/kiss_sidm_reader.jl")
    reader_path.write_text(_JULIA_READER)

    cmd = [
        JULIA_BIN, JULIA_VERSION,
        f"--project={JULIA_PROJECT}",
        str(reader_path),
        str(snap_dir),
        str(out_path),
    ]
    t0 = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    elapsed = time.time() - t0

    if proc.returncode != 0:
        raise RuntimeError(
            f"Julia reader failed (rc={proc.returncode}, elapsed={elapsed:.1f}s)\n"
            f"stdout: {proc.stdout[-2000:]}\n"
            f"stderr: {proc.stderr[-2000:]}"
        )

    return json.loads(out_path.read_text())


if __name__ == "__main__":
    snap_dir = "/tmp/kiss_sidm_output"
    out_path = "v0.3-prelim/data/results/real_kiss_sidm_aggregated.json"
    if not Path(snap_dir).exists():
        print(f"Snapshot dir {snap_dir} does not exist; run kiss_sidm_julia_bridge first")
    else:
        result = aggregate_kiss_snapshots(snap_dir, out_path)
        print(f"n_snapshots: {result['n_snapshots']}")
        print(f"n_bins: {len(result['r_over_rs'])}")
        print(f"time range: {result['time_Gyr'][0]:.3f} to {result['time_Gyr'][-1]:.3f} Gyr")
        print(f"max rho/rho_s: {max(map(max, result['rho_over_rhos'])):.3e}")
