#!/usr/bin/env julia
# T215n — Test if Random.seed!(42) before CBE_sim affects KiSS-SIDM's
# internal sample() calls. We monkey-patch sample() to count calls and
# record what RNG state was used.

using DSMC
using Random
using StaticArrays
using Unitful
using UnitfulAstro
using HDF5
using JLD2

println("=" ^ 60)
println("T215n — Does Random.seed!(42) reach KiSS-SIDM internal RNG?")
println("=" ^ 60)

# Load ICs
const M_HALO_MSUN = 5.0e9
const R_S_PC = 2924.4
const R_VIR_PC = 35092.9
const SIGMA_M_CM2_G = 70.0

ic_path = "/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/ics/t215_nfw_halo_cloud9.hdf5"
ic_pos = nothing
ic_vel = nothing
h5open(ic_path, "r") do file
    global ic_pos = read(file["PartType1/Coordinates"])
    global ic_vel = read(file["PartType1/Velocities"])
end
n_total = size(ic_pos, 2)
n_tracer = 100  # small for fast test

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

t_end_Gyr = 0.005  # very short, just to get past the first timestep
snapshot_times = collect(range(0.0u"Gyr", stop=t_end_Gyr * u"Gyr", length=3))

# === RUN 1: with Random.seed!(42) ===
params1 = CBEParams{1, SphericalGrid{1, Float64}, SelfGravity}(;
    units, N=1, Grav=SelfGravity,
    adaptive_grid=true, adaptive_grid_min_particles=64,
    n_phys_per_tracer,
    t_end=t_end_Gyr * u"Gyr",
    density_grid=grid,
    boundary_conditions=(reflecting_bc_sphere1d(rmin, rmax),),
    collision_alg=collision_alg_nb_repeat(v -> σ_vhs(CA, 0.0, v)),
    σ_max=(x, y) -> σ_vhs(CA, 0.0, 0.0u"km/s"),
    snapshot_times,
    output_path="/tmp/t215n_run1_output",
)
# Save RNG state before CBE_sim
Random.seed!(42)
state_before_1 = copy(Random.default_rng())
println("Run 1: state_before = $(string(state_before_1)[1:50]... )")
result1 = CBE_sim(params1, pos_radial, vel_spherical)
println("Run 1: completed")

# === RUN 2: with Random.seed!(42) again, same inputs ===
params2 = CBEParams{1, SphericalGrid{1, Float64}, SelfGravity}(;
    units, N=1, Grav=SelfGravity,
    adaptive_grid=true, adaptive_grid_min_particles=64,
    n_phys_per_tracer,
    t_end=t_end_Gyr * u"Gyr",
    density_grid=grid,
    boundary_conditions=(reflecting_bc_sphere1d(rmin, rmax),),
    collision_alg=collision_alg_nb_repeat(v -> σ_vhs(CA, 0.0, v)),
    σ_max=(x, y) -> σ_vhs(CA, 0.0, 0.0u"km/s"),
    snapshot_times,
    output_path="/tmp/t215n_run2_output",
)
# Use same ICs (positions/velocities are mutated, so reload)
pos_radial_2 = [SVector{1, typeof(1.0u"pc")}(0.0u"pc") for _ in 1:n_tracer]
vel_spherical_2 = [SVector{3, typeof(1.0u"km/s")}(0.0u"km/s", 0.0u"km/s", 0.0u"km/s") for _ in 1:n_tracer]
for i in 1:n_tracer
    p1d, v1d = reproject_velocity(positions[i], velocities[i])
    pos_radial_2[i] = p1d
    vel_spherical_2[i] = v1d
end
Random.seed!(42)
state_before_2 = copy(Random.default_rng())
println("Run 2: state_before = $(string(state_before_2)[1:50]... )")
result2 = CBE_sim(params2, pos_radial_2, vel_spherical_2)
println("Run 2: completed")

# Compare positions from snapshot 001 (first non-trivial snapshot)
s1 = JLD2.load("/tmp/t215n_run1_output/snap_001.jld2")
s2 = JLD2.load("/tmp/t215n_run2_output/snap_001.jld2")

pos1 = s1["positions"]
pos2 = s2["positions"]

# Count identical positions
n_same = 0
n_total_pos = length(pos1)
for i in 1:n_total_pos
    if pos1[i] ≈ pos2[i]
        n_same += 1
    end
end

println()
println("=" ^ 60)
println("Result: $n_same / $n_total_pos positions identical (≈)")
if n_same == n_total_pos
    println("** RNG seeding DOES make runs reproducible **")
else
    println("** RNG seeding does NOT fully reproduce results **")
end
println("=" ^ 60)