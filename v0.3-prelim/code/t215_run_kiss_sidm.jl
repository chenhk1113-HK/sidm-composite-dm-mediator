#!/usr/bin/env julia
# T215 — Run KiSS-SIDM with T215 NFW ICs at Cloud-9 host halo, sigma/m = 70.

using DSMC
using StaticArrays
using Unitful
using UnitfulAstro
using HDF5
using JLD2
using JSON

# Read T215 IC file
const IC_PATH = "/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/ics/t215_nfw_halo_cloud9.hdf5"

# Cloud-9 host halo parameters (T212)
const M_HALO_MSUN = 5.0e9
const C_HALO = 12.0
const V_MAX_KMS = 31.12
const R_S_PC = 2924.4
const R_VIR_PC = 35092.9
const RHO_S_MSUN_PC3 = 0.00969
const SIGMA_M_CM2_G = 70.0

# Read ICs (HDF5 file from T215 generator)
println("Reading IC file: $IC_PATH")
positions_3d = nothing
velocities_raw = nothing
h5open(IC_PATH, "r") do file
    global positions_3d = read(file["PartType1/Coordinates"])
    global velocities_raw = read(file["PartType1/Velocities"])
end

n_particles = size(positions_3d, 2)
println("  Read $n_particles particles")
println("  Position shape: $(size(positions_3d))")
println("  Velocity shape: $(size(velocities_raw))")

# KiSS-SIDM units: pc, km/s, Msun
units = Units(; length=u"pc", velocity=u"km/s", mass=u"Msun")
G_code = ustrip(u"pc * (km/s)^2 / Msun", Constants.G)
println("G_code = $G_code (pc (km/s)^2 / Msun)")

# KiSS-SIDM example scaling factor
const VELOCITY_SCALING = sqrt(G_code) / 207.832  # converts km/s to internal units
println("Velocity scaling factor: $VELOCITY_SCALING")

# Convert positions and velocities to KiSS-SIDM format
positions = [SVector{3, typeof(1.0u"pc")}(positions_3d[:, i] * u"pc") for i in 1:n_particles]
velocities = [SVector{3, typeof(1.0u"km/s")}(velocities_raw[:, i] * u"km/s" * VELOCITY_SCALING) for i in 1:n_particles]

# Apply reproject_velocity (3D cartesian -> 1D radial + 3D velocity)
println("Reprojecting 3D cartesian to spherical...")
pos_radial = [SVector{1, typeof(1.0u"pc")}(0.0u"pc") for _ in 1:n_particles]
vel_spherical = [SVector{3, typeof(1.0u"km/s")}(0.0u"km/s", 0.0u"km/s", 0.0u"km/s") for _ in 1:n_particles]
for i in 1:n_particles
    p1d, v1d = reproject_velocity(positions[i], velocities[i])
    pos_radial[i] = p1d
    vel_spherical[i] = v1d
end

# Compute density grid
rmin = 0.0u"pc"
rmax = 1.5 * R_VIR_PC * u"pc"  # 1.5x r_vir buffer
rhogrid = vcat(0.0, 10 .^ range(log10(20.0), stop=log10(ustrip(rmax)), length=21))u"pc"

# Each tracer represents n_phys_per_tracer solar masses
n_phys_per_tracer = M_HALO_MSUN / n_particles * u"Msun"
println("n_phys_per_tracer = $(ustrip(n_phys_per_tracer)) Msun")

# Cross-section in pc^2/Msun units
const CA = 2.088e-4 * SIGMA_M_CM2_G * u"pc^2/Msun"
println("Cross-section: $CA pc^2/Msun (=$SIGMA_M_CM2_G cm^2/g)")

# Grid
grid = SphericalGrid((rhogrid,))

# Run time: 0.02 Gyr (= 20 Myr, ~11% of Balberg t_core = 0.176 Gyr)
# Estimated wall time: 0.02 / 0.001 * 135s = ~45 min
t_end_Gyr = 0.02

# Snapshots every 0.001 Gyr
n_snapshots = 20
snapshot_times = collect(range(0.0u"Gyr", stop=t_end_Gyr * u"Gyr", length=n_snapshots+1))

params = CBEParams{1, SphericalGrid{1, Float64}, SelfGravity}(;
    units,
    N=1,
    Grav=SelfGravity,
    adaptive_grid=true,
    adaptive_grid_min_particles=64,  # higher than earlier runs to avoid majorant>N
    n_phys_per_tracer,
    t_end=t_end_Gyr * u"Gyr",
    density_grid=grid,
    boundary_conditions=(reflecting_bc_sphere1d(rmin, rmax),),
    collision_alg=collision_alg_nb_repeat(v -> σ_vhs(CA, 0.0, v)),
    σ_max=(x, y) -> σ_vhs(CA, 0.0, 0.0u"km/s"),
    snapshot_times,
    output_path="/tmp/t215_kiss_output",
)

println("Running KiSS-SIDM with $n_particles tracers, t_end=$(t_end_Gyr) Gyr")
println("  Output dir: /tmp/t215_kiss_output")
println("  Cross-section: $SIGMA_M_CM2_G cm^2/g")
println("  Halo: M=$M_HALO_MSUN Msun, c=$C_HALO, V_max=$V_MAX_KMS km/s")
println("  Balberg t_core = 0.176 Gyr (running for $(round(t_end_Gyr/0.176*100, digits=3))% of t_core)")

# Run simulation
println()
println("Starting CBE_sim...")
@time result = CBE_sim(params, pos_radial, vel_spherical)
println()
println("SUCCESS: KiSS-SIDM completed.")
println("Total collisions: $(result.collision_counter)")

# Save summary
using JSON
summary = Dict(
    "n_particles" => n_particles,
    "t_end_Gyr" => t_end_Gyr,
    "balberg_t_core_Gyr" => 0.176,
    "fraction_of_t_core" => t_end_Gyr / 0.176,
    "sigma_m_cm2_g" => SIGMA_M_CM2_G,
    "halo_M_Msun" => M_HALO_MSUN,
    "halo_c" => C_HALO,
    "halo_V_max_kms" => V_MAX_KMS,
    "total_collisions" => result.collision_counter,
    "status" => "completed",
)

out_path = "/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results/t215_kiss_sidm_run_summary.json"
mkpath(dirname(out_path))
open(out_path, "w") do f
    JSON.print(f, summary, 2)
end
println("Saved summary to: $out_path")