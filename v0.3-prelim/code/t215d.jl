#!/usr/bin/env julia
# T215d — Restart from T215b snapshot 008 (t≈45 Myr) and continue running.
# Goal: push total simulated time past 100 Myr.

using DSMC
using StaticArrays
using Unitful
using UnitfulAstro
using HDF5
using JLD2
using JSON
using Dates
using Random

const SNAP_PATH = "/tmp/t215_safe_output/snap_008.jld2"
const M_HALO_MSUN = 5.0e9
const R_S_PC = 2924.4
const R_VIR_PC = 35092.9
const SIGMA_M_CM2_G = 70.0

println("=" ^ 60)
println("T215d — Restart from T215b snapshot, continue to 200 Myr")
println("=" ^ 60)

# Load snapshot
s = JLD2.load(SNAP_PATH)
positions_prev = s["positions"]  # Vector{SVector{1, Quantity}}
velocities_prev = s["velocities"]  # Vector{SVector{3, Quantity}}
t_q = s["time"]
t_start_myr = ustrip(uconvert(u"pc * s / km", t_q)) * 0.978

n_particles = length(positions_prev)
println("Restarting from snapshot: t = $t_start_myr Myr, N = $n_particles particles")

# Reconstruct 3D positions and spherical velocities for KiSS-SIDM input
# The snapshot has positions in 1D spherical and velocities in 3D spherical coords
# We need to pass them as-is to CBE_sim
# But CBE_sim expects 3D positions + 3D velocities that get reprojected

# KiSS-SIDM takes 3D positions + 3D Cartesian velocities, then reprojects to spherical
# So we need to convert spherical -> Cartesian

# Recover Cartesian positions from spherical (r, theta, phi)
# Default theta = pi/2 (equatorial), phi = 0 if not stored
# Velocities stored in spherical (v_r, v_theta, v_phi)
# Need to reconstruct 3D Cartesian

println("Reconstructing 3D positions/velocities...")
G_code = ustrip(u"pc * (km/s)^2 / Msun", Constants.G)
const VELOCITY_SCALING = sqrt(G_code) / 207.832

# We don't know theta/phi from snapshot, but particles were distributed isotropically
# For restart, assume uniform angular distribution consistent with original ICs
# Use the SAME random seed so each particle gets a consistent (theta, phi)

# Actually simpler approach: assume (theta, phi) from original IC generator
# Read IC file to get original random angles
ic_path = "/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/ics/t215_nfw_halo_cloud9.hdf5"
ic_pos = nothing
h5open(ic_path, "r") do file
    global ic_pos = read(file["PartType1/Coordinates"])
end
# Take first n_particles — but we need to know WHICH indices were used
# From t215_safe.jl: idx = sort(rand(rng, 1:10000, 3000)) with rng = Random.default_rng(42)
# Re-run the same random selection
rng = Random.default_rng(42)
idx = sort(rand(rng, 1:10000, n_particles))
ic_pos_subset = ic_pos[:, idx]
ic_radii = sqrt.(ic_pos_subset[1, :].^2 .+ ic_pos_subset[2, :].^2 .+ ic_pos_subset[3, :].^2)
ic_theta = acos.(ic_pos_subset[3, :] ./ ic_radii)  # polar angle
ic_phi = atan.(ic_pos_subset[2, :], ic_pos_subset[1, :])  # azimuthal angle

# Reconstruct 3D positions from snapshot radii
radii_now = [ustrip(pos.data[1][1]) for pos in positions_prev]
positions_3d = zeros(3, n_particles)
positions_3d[1, :] = radii_now .* sin.(ic_theta) .* cos.(ic_phi)
positions_3d[2, :] = radii_now .* sin.(ic_theta) .* sin.(ic_phi)
positions_3d[3, :] = radii_now .* cos.(ic_theta)

# Reconstruct 3D Cartesian velocities from spherical
v_spherical = [[ustrip(vel.data[1]), ustrip(vel.data[2]), ustrip(vel.data[3])] for vel in velocities_prev]

velocities_3d = zeros(3, n_particles)
for i in 1:n_particles
    v_r, v_theta, v_phi = v_spherical[i]
    # Spherical to Cartesian velocity conversion
    # v_x = v_r sin(theta) cos(phi) + v_theta cos(theta) cos(phi) - v_phi sin(phi)
    # v_y = v_r sin(theta) sin(phi) + v_theta cos(theta) sin(phi) + v_phi cos(phi)
    # v_z = v_r cos(theta) - v_theta sin(theta)
    sin_t = sin(ic_theta[i])
    cos_t = cos(ic_theta[i])
    sin_p = sin(ic_phi[i])
    cos_p = cos(ic_phi[i])
    velocities_3d[1, i] = v_r * sin_t * cos_p + v_theta * cos_t * cos_p - v_phi * sin_p
    velocities_3d[2, i] = v_r * sin_t * sin_p + v_theta * cos_t * sin_p + v_phi * cos_p
    velocities_3d[3, i] = v_r * cos_t - v_theta * sin_t
end

# Convert to KiSS-SIDM types
units = Units(; length=u"pc", velocity=u"km/s", mass=u"Msun")
positions = [SVector{3, typeof(1.0u"pc")}(positions_3d[:, i] * u"pc") for i in 1:n_particles]
velocities = [SVector{3, typeof(1.0u"km/s")}(velocities_3d[:, i] * u"km/s" / VELOCITY_SCALING) for i in 1:n_particles]

# Reproject to spherical for KiSS-SIDM
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

# Target: 200 Myr total = 155 Myr additional
t_end_Gyr = 0.155
# Snapshots every 10 Myr
snapshot_times = collect(range(0.0u"Gyr", stop=t_end_Gyr * u"Gyr", length=17))  # every 10 Myr

params = CBEParams{1, SphericalGrid{1, Float64}, SelfGravity}(;
    units,
    N=1,
    Grav=SelfGravity,
    adaptive_grid=true,
    adaptive_grid_min_particles=32,
    n_phys_per_tracer,
    t_end=t_end_Gyr * u"Gyr",
    density_grid=grid,
    boundary_conditions=(reflecting_bc_sphere1d(rmin, rmax),),
    collision_alg=collision_alg_nb_repeat(v -> σ_vhs(CA, 0.0, v)),
    σ_max=(x, y) -> σ_vhs(CA, 0.0, 0.0u"km/s"),
    snapshot_times,
    output_path="/tmp/t215d_output",
)

println("Running $n_particles particles from t=$t_start_myr Myr, target t_end=$t_end_Gyr Gyr (additional)")
println("Snapshots: 17 (every 10 Myr)")
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
println("Total simulated time: $(t_start_myr + t_end_Gyr * 1000) Myr (if completed)")

summary = Dict(
    "status" => "COMPLETED_OR_ERRORED",
    "n_particles" => n_particles,
    "restart_t_myr" => t_start_myr,
    "additional_t_end_Gyr" => t_end_Gyr,
    "total_t_myr_if_complete" => t_start_myr + t_end_Gyr * 1000,
    "total_collisions" => local_total_collisions,
    "timestamp" => string(now()),
)
out_path = "/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results/t215d_summary.json"
mkpath(dirname(out_path))
open(out_path, "w") do f
    JSON.print(f, summary, 2)
end
println("Saved: $out_path")
println("END OF SCRIPT")