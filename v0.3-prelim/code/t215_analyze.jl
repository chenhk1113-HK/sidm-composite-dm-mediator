#!/usr/bin/env julia
# T215_analyze — Read KiSS-SIDM snapshots and compute density profiles.
# Diagnostic analysis to see what evolved before Julia died.

using JLD2
using StaticArrays
using Unitful
using UnitfulAstro
using JSON
using Printf

const SNAP_DIR = "/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/snapshots_t215_small"
const OUT_PATH = "/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results/t215_density_profiles_small.json"

# Cloud-9 host params
const R_S_PC = 2924.4
const R_VIR_PC = 35092.9
const M_HALO_MSUN = 5.0e9

println("=" ^ 60)
println("T215_analyze — Density profile evolution from KiSS-SIDM snapshots")
println("=" ^ 60)

# Read all snapshots
snap_files = sort(filter(p -> endswith(p, ".jld2"), readdir(SNAP_DIR, join=true)))
println("Found $(length(snap_files)) snapshots")

# For each snapshot, compute density profile
# Density = total mass in shell / shell volume
# Mass = sum of n_phys_per_tracer for particles in shell
# Shell volume = 4/3 pi (r_out^3 - r_in^3)

# Radial bins (log-spaced)
n_bins = 15
r_bins = 10 .^ range(log10(50.0), stop=log10(R_VIR_PC), length=n_bins+1)  # pc

profiles = []
for snap_path in snap_files
    s = JLD2.load(snap_path)
    positions = s["positions"]  # Vector{SVector{1, ...Quantity{pc}}}
    velocities = s["velocities"]  # Vector{SVector{3, ...Quantity{km/s}}}
    t_q = s["time"]  # Quantity with units pc*s/km
    t_pc = ustrip(uconvert(u"pc * s / km", t_q))
    t_myr = t_pc * 0.978
    npart = length(positions)
    # collisions counter is not in the snapshot; only available from CBE_sim return value

    # Extract radii (positions are 1D spherical)
    radii = [ustrip(pos[1]) for pos in positions]

    # Compute density in each bin
    rho_bins = Float64[]
    for i in 1:n_bins
        r_in = r_bins[i]
        r_out = r_bins[i+1]
        in_shell = (radii .>= r_in) .& (radii .< r_out)
        n_in = sum(in_shell)
        shell_vol = (4.0/3.0) * π * (r_out^3 - r_in^3)  # pc^3
        n_phys_per_tracer = M_HALO_MSUN / 10000.0  # Msun per particle
        mass_in = n_in * n_phys_per_tracer  # Msun
        rho = mass_in / shell_vol  # Msun/pc^3
        push!(rho_bins, rho)
    end

    push!(profiles, Dict(
        "snap" => basename(snap_path),
        "t_myr" => t_myr,
        "t_pc" => t_pc,
        "npart" => npart,
        "r_bins_pc" => r_bins[1:end-1],
        "rho_Msun_pc3" => rho_bins,
    ))

    # Print summary
    println()
    @printf "Snapshot %s: t=%.3f Myr, N=%d\n" basename(snap_path) t_myr npart
    @printf "  Density at r=%.0f pc: rho=%.4e Msun/pc^3\n" r_bins[8] rho_bins[8]
    @printf "  Density at r=%.0f pc: rho=%.4e Msun/pc^3\n" r_bins[12] rho_bins[12]
end

# Save all profiles
output = Dict(
    "halo_params" => Dict(
        "M_Msun" => M_HALO_MSUN,
        "r_s_pc" => R_S_PC,
        "r_vir_pc" => R_VIR_PC,
    ),
    "n_snapshots" => length(snap_files),
    "profiles" => profiles,
)

mkpath(dirname(OUT_PATH))
open(OUT_PATH, "w") do f
    JSON.print(f, output, 2)
end
@printf "\nSaved profiles to: %s\n" OUT_PATH

# Quick summary: density evolution at r = r_s
println()
println("Density evolution at r ≈ r_s (", R_S_PC, " pc):")
for p in profiles
    idx = argmin(abs.(p["r_bins_pc"] .- R_S_PC))
    @printf "  t=%6.3f Myr: rho=%.4e Msun/pc^3\n" p["t_myr"] p["rho_Msun_pc3"][idx]
end

println()
println("=" ^ 60)
println("END OF ANALYSIS")