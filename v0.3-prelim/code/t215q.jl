#!/usr/bin/env julia
# T215q — Same-session reproducibility test at FULL production N (3000 particles)
# Per Rv18.4 Round 6 rec #2: "Run t215p.jl twice in the same Julia session
# (3000 particles, 70 Myr target). If the two runs give the same t_max and
# same density profiles, you've closed the loop."

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

println("=== T215q — Full-N Same-Session Reproducibility Test ===")

ic_path = "/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/ics/t215_nfw_halo_cloud9.hdf5"
ic_pos = nothing
ic_vel = nothing
h5open(ic_path, "r") do file
    global ic_pos = read(file["PartType1/Coordinates"])
    global ic_vel = read(file["PartType1/Velocities"])
end
n_total = size(ic_pos, 2)
n_tracer = 3000

units = Units(; length=u"pc", velocity=u"km/s", mass=u"Msun")
G_code = ustrip(u"pc * (km/s)^2 / Msun", Constants.G)
const VELOCITY_SCALING = sqrt(G_code) / 207.832

rng = Random.default_rng(42)
idx = sort(rand(rng, 1:n_total, n_tracer))
ic_pos_subset = ic_pos[:, idx]
ic_vel_subset = ic_vel[:, idx]

positions = [SVector{3, typeof(1.0u"pc")}(ic_pos_subset[:, i] * u"pc") for i in 1:n_tracer]
velocities = [SVector{3, typeof(1.0u"km/s")}(ic_vel_subset[:, i] * u"km/s" * VELOCITY_SCALING) for i in 1:n_tracer]

rmin = 0.0u"pc"
rmax = 1.5 * R_VIR_PC * u"pc"
rhogrid = vcat(0.0, 10 .^ range(log10(20.0), stop=log10(ustrip(rmax)), length=21))u"pc"

n_phys_per_tracer = M_HALO_MSUN / n_tracer * u"Msun"
const CA = 2.088e-4 * SIGMA_M_CM2_G * u"pc^2/Msun"

grid = SphericalGrid((rhogrid,))

t_end_Gyr = 0.07
snapshot_times = collect(range(0.0u"Gyr", stop=t_end_Gyr * u"Gyr", length=15))

function make_run(out_dir, pos_radial_in, vel_spherical_in)
    params = CBEParams{1, SphericalGrid{1, Float64}, SelfGravity}(;
        units, N=1, Grav=SelfGravity,
        adaptive_grid=true, adaptive_grid_min_particles=64,
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
    result = CBE_sim(params, pos_radial_in, vel_spherical_in)
    return result
end

function make_fresh_ic()
    pos_r = [SVector{1, typeof(1.0u"pc")}(0.0u"pc") for _ in 1:n_tracer]
    vel_s = [SVector{3, typeof(1.0u"km/s")}(0.0u"km/s", 0.0u"km/s", 0.0u"km/s") for _ in 1:n_tracer]
    for i in 1:n_tracer
        p1d, v1d = reproject_velocity(positions[i], velocities[i])
        pos_r[i] = p1d
        vel_s[i] = v1d
    end
    return pos_r, vel_s
end

# === RUN 1 ===
println()
println("--- Run 1 ---")
pos_r1, vel_s1 = make_fresh_ic()
result1 = make_run("/tmp/t215q_run1_output", pos_r1, vel_s1)
println("Run 1: collision_counter = ", result1.collision_counter)

# Aggressive GC between runs
GC.gc(true)
GC.gc(true)
GC.gc(true)
println("GC done between runs")

# === RUN 2 (same Julia process, fresh ICs, fresh seed) ===
println()
println("--- Run 2 ---")
pos_r2, vel_s2 = make_fresh_ic()
result2 = make_run("/tmp/t215q_run2_output", pos_r2, vel_s2)
println("Run 2: collision_counter = ", result2.collision_counter)

# === Compare snapshots ===
function last_t_per_dir(dir)
    snap_files = sort(filter(p -> endswith(p, ".jld2"), readdir(dir, join=true)))
    if isempty(snap_files)
        return nothing, 0
    end
    s = JLD2.load(snap_files[end])
    return s["time"], length(snap_files)
end

t1, n1 = last_t_per_dir("/tmp/t215q_run1_output")
t2, n2 = last_t_per_dir("/tmp/t215q_run2_output")
println()
println("=== Comparison ===")
println("Run 1: t_final = $t1, snapshots = $n1")
println("Run 2: t_final = $t2, snapshots = $n2")

if t1 == t2 && n1 == n2
    println("** IDENTICAL timing and snapshot count **")
else
    println("** DIFFERENT timing: $(t1) vs $(t2) **")
end

# Compare first snapshot positions
function get_positions(dir)
    snap_files = sort(filter(p -> endswith(p, ".jld2"), readdir(dir, join=true)))
    if length(snap_files) < 2
        return nothing
    end
    s = JLD2.load(snap_files[2])  # snap_001 (first non-trivial)
    return s["positions"]
end

p1 = get_positions("/tmp/t215q_run1_output")
p2 = get_positions("/tmp/t215q_run2_output")

if p1 !== nothing && p2 !== nothing
    n = length(p1)
    n_same = 0
    for i in 1:n
        if p1[i] ≈ p2[i]
            n_same += 1
        end
    end
    println("snap_001 positions: $n_same / $n identical (≈)")
end

println()
println("END")