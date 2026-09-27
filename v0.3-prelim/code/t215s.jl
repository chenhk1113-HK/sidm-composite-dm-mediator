#!/usr/bin/env julia
# T215s — Same-session 3-run degradation test
# Per Rv18.4 Round 7 rec: "Run 3 short runs (30 Myr target) in one process.
# Report which ones complete."

using DSMC
using StaticArrays
using Unitful
using UnitfulAstro
using HDF5
using JLD2
using Random

const M_HALO_MSUN = 5.0e9
const R_S_PC = 2924.4
const R_VIR_PC = 35092.9
const SIGMA_M_CM2_G = 70.0

println("=== T215s — Same-Session 3-Run Degradation Test ===")

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

# Short target (30 Myr) so all 3 runs might fit in same process
t_end_Gyr = 0.03
snapshot_times = collect(range(0.0u"Gyr", stop=t_end_Gyr * u"Gyr", length=8))

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
    return CBE_sim(params, pos_radial_in, vel_spherical_in)
end

# Run 3 short runs in same process
for run_num in 1:3
    println()
    println("--- Run $run_num ---")
    pos_r, vel_s = make_fresh_ic()
    result = make_run("/tmp/t215s_run$(run_num)_output", pos_r, vel_s)
    println("Run $run_num complete")
    GC.gc(true); GC.gc(true)
end

# Report
function last_t(dir)
    snap_files = sort(filter(p -> endswith(p, ".jld2"), readdir(dir, join=true)))
    if isempty(snap_files)
        return "no_snapshots", 0
    end
    s = JLD2.load(snap_files[end])
    t = ustrip(Unitful.uconvert(s["Time"] * u"pc * s / km", s["time"]))
    return t, length(snap_files)
end

println()
println("=== Results ===")
for i in 1:3
    t, n = last_t("/tmp/t215s_run$(i)_output")
    println("Run $i: t_final = $t pc*s/km, snapshots = $n")
end

println()
println("END")