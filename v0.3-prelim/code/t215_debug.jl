#!/usr/bin/env julia
# T215_debug — Debug version of T215 run with memory monitoring and final status marker.
# Goal: figure out why the previous T215 run died silently at t = 8.67 Myr.

using DSMC
using StaticArrays
using Unitful
using UnitfulAstro
using HDF5
using JLD2
using JSON
using Dates

const IC_PATH = "/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/ics/t215_nfw_halo_cloud9.hdf5"
const M_HALO_MSUN = 5.0e9
const C_HALO = 12.0
const V_MAX_KMS = 31.12
const R_S_PC = 2924.4
const R_VIR_PC = 35092.9
const SIGMA_M_CM2_G = 70.0

# Helper: log memory usage
function log_mem(label)
    rss_mb = 0
    try
        open("/proc/self/status") do f
            for line in eachline(f)
                if startswith(line, "VmRSS:")
                    rss_kb = parse(Int, split(line)[2])
                    rss_mb = rss_kb ÷ 1024
                    break
                end
            end
        end
    catch
    end
    println("[$(label)] Memory: $(rss_mb) MB RSS")
    return rss_mb
end

println("=" ^ 60)
println("T215_debug — KiSS-SIDM with memory monitoring")
println("=" ^ 60)
log_mem("startup")

# Read ICs
println("Reading IC file: $IC_PATH")
log_mem("before_read")
positions_3d = nothing
velocities_raw = nothing
h5open(IC_PATH, "r") do file
    global positions_3d = read(file["PartType1/Coordinates"])
    global velocities_raw = read(file["PartType1/Velocities"])
end
n_particles = size(positions_3d, 2)
println("  Read $n_particles particles")
log_mem("after_read_ic")

# KiSS-SIDM setup
units = Units(; length=u"pc", velocity=u"km/s", mass=u"Msun")
G_code = ustrip(u"pc * (km/s)^2 / Msun", Constants.G)
const VELOCITY_SCALING = sqrt(G_code) / 207.832

positions = [SVector{3, typeof(1.0u"pc")}(positions_3d[:, i] * u"pc") for i in 1:n_particles]
velocities = [SVector{3, typeof(1.0u"km/s")}(velocities_raw[:, i] * u"km/s" * VELOCITY_SCALING) for i in 1:n_particles]

println("Reprojecting 3D -> spherical...")
pos_radial = [SVector{1, typeof(1.0u"pc")}(0.0u"pc") for _ in 1:n_particles]
vel_spherical = [SVector{3, typeof(1.0u"km/s")}(0.0u"km/s", 0.0u"km/s", 0.0u"km/s") for _ in 1:n_particles]
for i in 1:n_particles
    p1d, v1d = reproject_velocity(positions[i], velocities[i])
    pos_radial[i] = p1d
    vel_spherical[i] = v1d
end
log_mem("after_reproject")

# Grid
rmin = 0.0u"pc"
rmax = 1.5 * R_VIR_PC * u"pc"
rhogrid = vcat(0.0, 10 .^ range(log10(20.0), stop=log10(ustrip(rmax)), length=21))u"pc"

n_phys_per_tracer = M_HALO_MSUN / n_particles * u"Msun"
const CA = 2.088e-4 * SIGMA_M_CM2_G * u"pc^2/Msun"

grid = SphericalGrid((rhogrid,))

# Targeted run: 0.005 Gyr = 5 Myr (~2.8% of Balberg t_core)
# Lower than before to avoid potential OOM
t_end_Gyr = 0.005
n_snapshots = 10  # every 0.5 Myr
snapshot_times = collect(range(0.0u"Gyr", stop=t_end_Gyr * u"Gyr", length=n_snapshots+1))

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
    output_path="/tmp/t215_debug_output",
)

println("\nRunning KiSS-SIDM with $n_particles tracers, t_end=$(t_end_Gyr) Gyr")
println("  Output dir: /tmp/t215_debug_output")
println("  Cross-section: $SIGMA_M_CM2_G cm^2/g")
println("  Balberg t_core = 0.176 Gyr (running for $(round(t_end_Gyr/0.176*100, digits=2))% of t_core)")
log_mem("before_run")

println("\nStarting CBE_sim...")

# Wrap in try/catch to capture any final error
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
    Base.show_backtrace(stdout, catch_backtrace())
    println()
end
log_mem("after_run")

println("\n" * "=" ^ 60)
println("FINAL: Run completed (or errored).")
println("Total collisions: $local_total_collisions")
log_mem("end")

# Save summary with explicit end marker
summary = Dict(
    "status" => "COMPLETED_OR_ERRORED",
    "n_particles" => n_particles,
    "t_end_Gyr" => t_end_Gyr,
    "balberg_t_core_Gyr" => 0.176,
    "fraction_of_t_core" => t_end_Gyr / 0.176,
    "sigma_m_cm2_g" => SIGMA_M_CM2_G,
    "halo_M_Msun" => M_HALO_MSUN,
    "halo_c" => C_HALO,
    "halo_V_max_kms" => V_MAX_KMS,
    "total_collisions" => local_total_collisions,
    "timestamp" => string(now()),
)

out_path = "/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results/t215_debug_summary.json"
mkpath(dirname(out_path))
open(out_path, "w") do f
    JSON.print(f, summary, 2)
end
println("\nSaved summary to: $out_path")
println("END OF SCRIPT - NORMAL EXIT")