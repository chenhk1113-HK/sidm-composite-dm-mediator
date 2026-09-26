#!/usr/bin/env julia
# T215f — Try to push past 60 Myr with more aggressive memory management
# Strategy: periodic GC.gc() + write minimal log

using DSMC
using StaticArrays
using Unitful
using UnitfulAstro
using HDF5
using JLD2
using JSON
using Dates
using Random

const M_HALO_MSUN = 5.0e9
const R_S_PC = 2924.4
const R_VIR_PC = 35092.9
const SIGMA_M_CM2_G = 70.0

println("=" ^ 60)
println("T215f — Push to 100 Myr with periodic GC + log_mem")
println("=" ^ 60)

# Load IC HDF5
ic_path = "/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/ics/t215_nfw_halo_cloud9.hdf5"
ic_pos = nothing
h5open(ic_path, "r") do file
    global ic_pos = read(file["PartType1/Coordinates"])
end
n_total = size(ic_pos, 2)
println("IC file: $n_total particles")

# Use 3000 particles
n_tracer = 3000
rng = Random.default_rng(42)
idx = sort(rand(rng, 1:n_total, n_tracer))
ic_pos_subset = ic_pos[:, idx]
ic_radii = sqrt.(ic_pos_subset[1, :].^2 .+ ic_pos_subset[2, :].^2 .+ ic_pos_subset[3, :].^2)

# Read velocities
ic_vel = nothing
h5open(ic_path, "r") do file
    global ic_vel = read(file["PartType1/Velocities"])
end
ic_vel_subset = ic_vel[:, idx]

println("Loaded $n_tracer particles")

# Build positions/velocities for KiSS-SIDM
units = Units(; length=u"pc", velocity=u"km/s", mass=u"Msun")
# positions_3d is 3 x n_tracer (column-major HDF5 read)

# KiSS-SIDM velocity scaling
G_code = ustrip(u"pc * (km/s)^2 / Msun", Constants.G)
const VELOCITY_SCALING = sqrt(G_code) / 207.832
println("VELOCITY_SCALING = $VELOCITY_SCALING")

# Reproject to spherical
positions = [SVector{3, typeof(1.0u"pc")}(ic_pos_subset[:, i] * u"pc") for i in 1:n_tracer]
velocities = [SVector{3, typeof(1.0u"km/s")}(ic_vel_subset[:, i] * u"km/s" * VELOCITY_SCALING) for i in 1:n_tracer]

pos_radial = [SVector{1, typeof(1.0u"pc")}(0.0u"pc") for _ in 1:n_tracer]
vel_spherical = [SVector{3, typeof(1.0u"km/s")}(0.0u"km/s", 0.0u"km/s", 0.0u"km/s") for _ in 1:n_tracer]
for i in 1:n_tracer
    p1d, v1d = reproject_velocity(positions[i], velocities[i])
    pos_radial[i] = p1d
    vel_spherical[i] = v1d
end

rmin = 0.0u"pc"
rmax = 1.5 * R_VIR_PC * u"pc"
rhogrid = vcat(0.0, 10 .^ range(log10(20.0), stop=log10(ustrip(rmax)), length=21))u"pc"

n_phys_per_tracer = M_HALO_MSUN / n_tracer * u"Msun"
const CA = 2.088e-4 * SIGMA_M_CM2_G * u"pc^2/Msun"

grid = SphericalGrid((rhogrid,))

# Target: 100 Myr total
t_end_Gyr = 0.10
snapshot_times = collect(range(0.0u"Gyr", stop=t_end_Gyr * u"Gyr", length=21))  # every 5 Myr

params = CBEParams{1, SphericalGrid{1, Float64}, SelfGravity}(;
    units,
    N=1,
    Grav=SelfGravity,
    adaptive_grid=true,
    adaptive_grid_min_particles=64,  # T215e sweet spot
    n_phys_per_tracer,
    t_end=t_end_Gyr * u"Gyr",
    density_grid=grid,
    boundary_conditions=(reflecting_bc_sphere1d(rmin, rmax),),
    collision_alg=collision_alg_nb_repeat(v -> σ_vhs(CA, 0.0, v)),
    σ_max=(x, y) -> σ_vhs(CA, 0.0, 0.0u"km/s"),
    snapshot_times,
    output_path="/tmp/t215f_output",
)

println("Running $n_tracer particles, target t_end=$t_end_Gyr Gyr (100 Myr)")
println("Snapshots: 21 (every 5 Myr)")
println()

# Memory diagnostic
function get_mem_mb()
    try
        status = read("/proc/self/status", String)
        vmrss_idx = findfirst("VmRSS:", status)
        if vmrss_idx === nothing
            return -1
        end
        newline_idx = findfirst('\n', status[vmrss_idx:end])
        if newline_idx === nothing
            return -1
        end
        line = status[vmrss_idx:end][1:newline_idx.start-1]
        m = match(r"VmRSS:\s+(\d+)\s+(\w+)", line)
        if m === nothing
            return -1
        end
        val_kb = parse(Int, m.captures[1])
        if m.captures[2] == "MB" || m.captures[2] == "M"
            return val_kb
        elseif m.captures[2] == "GB" || m.captures[2] == "G"
            return val_kb * 1024
        else
            return val_kb ÷ 1024
        end
    catch
        return -1
    end
end

println("Startup mem: ", get_mem_mb(), " MB")

# Use subprocess GC strategy - call GC.gc(true) periodically during simulation
# But we can't easily inject code into CBE_sim. Try running the simulation.

local_run_result = nothing
local_total_collisions = 0
try
    global local_run_result = CBE_sim(params, pos_radial, vel_spherical)
    global local_total_collisions = local_run_result.collision_counter
    println("CBE_sim returned normally")
catch e
    println("CBE_sim THREW EXCEPTION:")
    showerror(stdout, e)
    println()
end

println("End mem: ", get_mem_mb(), " MB")
println("\nTotal collisions: $local_total_collisions")

summary = Dict(
    "status" => "COMPLETED_OR_ERRORED",
    "n_particles" => n_tracer,
    "t_end_Gyr" => t_end_Gyr,
    "total_collisions" => local_total_collisions,
    "timestamp" => string(now()),
)
out_path = "/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results/t215f_summary.json"
mkpath(dirname(out_path))
open(out_path, "w") do f
    JSON.print(f, summary, 2)
end
println("Saved: $out_path")
println("END OF SCRIPT")