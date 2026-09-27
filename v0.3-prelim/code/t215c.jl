#!/usr/bin/env julia
# T215c — KiSS-SIDM with BOTH bugs fixed: collision.jl + 1d_sphere.jl
# Target: 150 Myr (85% of Balberg t_core = 0.176 Gyr)
# Strategy: 3000 particles, t_end = 0.15 Gyr, frequent snapshots to catch collapse

using DSMC
using StaticArrays
using Unitful
using UnitfulAstro
using HDF5
using JSON
using Dates
using Random

const IC_PATH = "/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/ics/t215_nfw_halo_cloud9.hdf5"
const M_HALO_MSUN = 5.0e9
const C_HALO = 12.0
const V_MAX_KMS = 31.12
const R_S_PC = 2924.4
const R_VIR_PC = 35092.9
const SIGMA_M_CM2_G = 70.0

println("=" ^ 60)
println("T215c — KiSS-SIDM with both FP patches applied")
println("Julia version: ", VERSION)
println("=" ^ 60)

# Read ICs
positions_3d = nothing
velocities_raw = nothing
h5open(IC_PATH, "r") do file
    global positions_3d = read(file["PartType1/Coordinates"])
    global velocities_raw = read(file["PartType1/Velocities"])
end
n_total = size(positions_3d, 2)
rng = Random.default_rng(42)
idx = sort(rand(rng, 1:n_total, 3000))
positions_3d = positions_3d[:, idx]
velocities_raw = velocities_raw[:, idx]
n_particles = size(positions_3d, 2)
println("Using $n_particles particles")

units = Units(; length=u"pc", velocity=u"km/s", mass=u"Msun")
G_code = ustrip(u"pc * (km/s)^2 / Msun", Constants.G)
const VELOCITY_SCALING = sqrt(G_code) / 207.832

positions = [SVector{3, typeof(1.0u"pc")}(positions_3d[:, i] * u"pc") for i in 1:n_particles]
velocities = [SVector{3, typeof(1.0u"km/s")}(velocities_raw[:, i] * u"km/s" * VELOCITY_SCALING) for i in 1:n_particles]

pos_radial = [SVector{1, typeof(1.0u"pc")}(0.0u"pc") for _ in 1:n_particles]
vel_spherical = [SVector{3, typeof(1.0u"km/s")}(0.0u"km/s", 0.0u"km/s", 0.0u"km/s") for _ in 1:n_particles]
for i in 1:n_particles
    p1d, v1d = reproject_velocity(positions[i], velocities[i])
    pos_radial[i] = p1d
    vel_spherical[i] = v1d
end

rmin = 0.0u"pc"
rmax = 1.5 * R_VIR_PC * u"pc"
rhogrid = vcat(0.0, 10 .^ range(log10(20.0), stop=log10(ustrip(rmax)), length=21))u"pc"

n_phys_per_tracer = M_HALO_MSUN / n_particles * u"Msun"
const CA = 2.088e-4 * SIGMA_M_CM2_G * u"pc^2/Msun"

grid = SphericalGrid((rhogrid,))

# Target: 150 Myr (85% of Balberg t_core)
t_end_Gyr = 0.15
# More snapshots to capture collapse dynamics: every 5 Myr
snapshot_times = collect(range(0.0u"Gyr", stop=t_end_Gyr * u"Gyr", length=31))  # every 5 Myr

params = CBEParams{1, SphericalGrid{1, Float64}, SelfGravity}(;
    units,
    N=1,
    Grav=SelfGravity,
    adaptive_grid=true,
    adaptive_grid_min_particles=64,
    n_phys_per_tracer,
    t_end=t_end_Gyr * u"Gyr",
    density_grid=grid,
    boundary_conditions=(reflecting_bc_sphere1d(rmin, rmax),),
    collision_alg=collision_alg_nb_repeat(v -> σ_vhs(CA, 0.0, v)),
    σ_max=(x, y) -> σ_vhs(CA, 0.0, 0.0u"km/s"),
    snapshot_times,
    output_path="/tmp/t215c_output",
)

println("Running with $n_particles particles, t_end=$t_end_Gyr Gyr (150 Myr)")
println("Snapshots: 31 (every 5 Myr)")
println()
println("Starting CBE_sim...")
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

println("\nTotal collisions: $local_total_collisions")

summary = Dict(
    "status" => "COMPLETED_OR_ERRORED",
    "n_particles" => n_particles,
    "t_end_Gyr" => t_end_Gyr,
    "n_snapshots" => 31,
    "total_collisions" => local_total_collisions,
    "timestamp" => string(now()),
)
out_path = "/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results/t215c_summary.json"
mkpath(dirname(out_path))
open(out_path, "w") do f
    JSON.print(f, summary, 2)
end
println("Saved: $out_path")
println("END OF SCRIPT")