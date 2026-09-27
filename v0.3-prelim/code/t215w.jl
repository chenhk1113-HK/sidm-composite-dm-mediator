#!/usr/bin/env julia
# T215w — Tier 1 + smarter Tier 2 pilot: N=10000, min_particles=32 (original default), t_end=0.18 Gyr
# Per R18.4 Round 11 (Consider.docx) Tier 1 + 2 future-work recommendation.
#
# Previous attempt (t215v, N=10k + min_particles=128) FAILED: bins split aggressively,
# 0 merges, dt hits floor at t < 4 Myr. Reviewer's "raise min_particles" was wrong for N=10k.
#
# Revised strategy: keep original min_particles=32 (default), add N=10k. Should give
# fewer aggressive splits, more particles per bin = stable dt.
#
# Pilot recipe:
#   ulimit -v 8000000
#   N = 10000
#   adaptive_grid_min_particles = 32 (original default, NOT 128)
#   t_end = 0.18 Gyr (180 Myr)
#   snapshots every ~10 Myr
#   fresh Julia + fixed seed + persistent output

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

run_idx = parse(Int, ARGS[1])
println("=== T215w Tier1+2 Pilot (revised) Run $run_idx ===")
println("Config: N=10000, min_particles=32 (default), t_end=0.18 Gyr, ulimit -v 8000000")
println("Started at $(now())")

ic_path = "/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/ics/t215_nfw_halo_cloud9.hdf5"
ic_pos = nothing
ic_vel = nothing
h5open(ic_path, "r") do file
    global ic_pos = read(file["PartType1/Coordinates"])
    global ic_vel = read(file["PartType1/Velocities"])
end
n_total = size(ic_pos, 2)
n_tracer = 10000  # Tier 2: 3k -> 10k

units = Units(; length=u"pc", velocity=u"km/s", mass=u"Msun")
G_code = ustrip(u"pc * (km/s)^2 / Msun", Constants.G)
const VELOCITY_SCALING = sqrt(G_code) / 207.832

rng = Random.default_rng(42)
idx = sort(rand(rng, 1:n_total, n_tracer))
ic_pos_subset = ic_pos[:, idx]
ic_vel_subset = ic_vel[:, idx]

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

t_end_Gyr = 0.18
snapshot_times = collect(range(0.0u"Gyr", stop=t_end_Gyr * u"Gyr", length=19))

out_dir = "/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/snapshots_t215w_run$(run_idx)"

params = CBEParams{1, SphericalGrid{1, Float64}, SelfGravity}(;
    units, N=1, Grav=SelfGravity,
    adaptive_grid=true, adaptive_grid_min_particles=32,  # REVISED: 32 (default), NOT 128
    n_phys_per_tracer,
    t_end=t_end_Gyr * u"Gyr",
    density_grid=grid,
    boundary_conditions=(reflecting_bc_sphere1d(rmin, rmax),),
    collision_alg=collision_alg_nb_repeat(v -> σ_vhs(CA, 0.0, v)),
    σ_max=(x, y) -> σ_vhs(CA, 0.0, 0.0u"km/s"),
    snapshot_times,
    output_path=out_dir,
)

Random.seed!(42)
println("Starting CBE_sim for run $run_idx at $(now())...")
result = CBE_sim(params, pos_radial, vel_spherical)
println("Run $run_idx completed normally at $(now())")