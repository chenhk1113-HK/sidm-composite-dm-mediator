using JLD2, Unitful, UnitfulAstro, Printf, JSON

const SNAP_DIR = "/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/snapshots_t215e"
const OUT_PATH = "/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results/t215_density_profiles_t215e_v2.json"
const R_S_PC = 2924.4
const R_VIR_PC = 35092.9

# pc*s/km → Myr conversion factor:
#   The Unitful dimension pc*s/km represents parsec·second per kilometer.
#   1 pc = 3.0856775814913673e13 km
#   1 yr = 3.15576e7 s
#   1 pc * 1 s / 1 km = (3.0856775814913673e13 km) * s / km = 3.0857e13 s
#                     = 3.0857e13 / 3.15576e7 yr ≈ 977.79 yr = 0.97779 Myr
# So 1 pc·s/km = 0.97779 Myr ≈ 0.978 Myr.
# Source: NIST + Unitful conversion. The factor 0.978 is a unit conversion,
# NOT a free parameter. Verified with `uconvert(u"Myr", 1.0 * u"pc*s/km")`
# in Julia which returns 0.9778 Myr.
const PC_PER_KMS_TO_MYR = 0.9777922216807892

snap_files = sort(filter(p -> endswith(p, ".jld2"), readdir(SNAP_DIR, join=true)))
println("Found $(length(snap_files)) snapshots")

n_bins = 15
r_bins = 10 .^ range(log10(50.0), stop=log10(R_VIR_PC), length=n_bins+1)

# Read M_halo and n_particles from first snapshot to compute n_phys_per_tracer
first_snap = JLD2.load(snap_files[1])
npart_first = length(first_snap["positions"])
println("Particles per snapshot: $npart_first")

# Try to read M_halo from params (may not be stored)
# Default to 5e9 Msun (Cloud-9 host) — this matches t215_safe.jl config
M_HALO_MSUN = 5.0e9
n_phys_per_tracer = M_HALO_MSUN / npart_first
println("M_halo: $M_HALO_MSUN Msun, n_phys_per_tracer: $n_phys_per_tracer Msun")

profiles = []
for snap_path in snap_files
    s = JLD2.load(snap_path)
    positions = s["positions"]
    t_q = s["time"]
    t_pc = ustrip(uconvert(u"pc * s / km", t_q))
    t_myr = t_pc * PC_PER_KMS_TO_MYR  # CORRECT conversion (was 0.978 in v1)
    npart = length(positions)

    radii = [ustrip(pos.data[1][1]) for pos in positions]

    # Density profile + Poisson errors
    rho_bins = Float64[]
    rho_err_bins = Float64[]  # Poisson: sigma_N = sqrt(N); sigma_rho = rho * sqrt(1/N) for N > 0
    n_in_bins = Int[]
    for i in 1:n_bins
        r_in = r_bins[i]
        r_out = r_bins[i+1]
        in_shell = (radii .>= r_in) .& (radii .< r_out)
        n_in = sum(in_shell)
        push!(n_in_bins, n_in)
        shell_vol = (4.0/3.0) * pi * (r_out^3 - r_in^3)
        if n_in > 0
            mass_in = n_in * n_phys_per_tracer
            rho = mass_in / shell_vol
            # Poisson error: sqrt(N) on count, propagated to density
            rho_err = rho / sqrt(n_in)
            push!(rho_bins, rho)
            push!(rho_err_bins, rho_err)
        else
            # Empty bin — density undefined, but report upper limit from 1 particle
            push!(rho_bins, 0.0)
            push!(rho_err_bins, n_phys_per_tracer / shell_vol)
        end
    end

    push!(profiles, Dict(
        "snap" => basename(snap_path),
        "t_myr" => t_myr,
        "npart" => npart,
        "r_bins_pc" => r_bins[1:end-1],
        "n_in_bin" => n_in_bins,
        "rho_Msun_pc3" => rho_bins,
        "rho_err_Msun_pc3" => rho_err_bins,
    ))
end

output = Dict(
    "halo_params" => Dict("M_Msun" => M_HALO_MSUN, "r_s_pc" => R_S_PC, "r_vir_pc" => R_VIR_PC),
    "n_snapshots" => length(snap_files),
    "n_phys_per_tracer_Msun" => n_phys_per_tracer,
    "pc_per_kms_to_myr" => PC_PER_KMS_TO_MYR,
    "profiles" => profiles,
)
mkpath(dirname(OUT_PATH))
open(OUT_PATH, "w") do f
    JSON.print(f, output, 2)
end

println()
println("Saved to: $OUT_PATH")
println()
println("Density evolution at r ≈ 200 pc (with Poisson errors):")
for p in profiles
    idx = argmin(abs.(p["r_bins_pc"] .- 200.0))
    n = p["n_in_bin"][idx]
    rho = p["rho_Msun_pc3"][idx]
    rho_err = p["rho_err_Msun_pc3"][idx]
    rel_err = n > 0 ? rho_err / rho : Inf
    @printf "  t=%6.3f Myr: rho(200pc)=%.4e ± %.4e Msun/pc^3 (N_in=%d, rel_err=%.0f%%)\n" p["t_myr"] rho rho_err n (rel_err * 100)
end

println()
println("Density evolution at r ≈ 500 pc (with Poisson errors):")
for p in profiles
    idx = argmin(abs.(p["r_bins_pc"] .- 500.0))
    n = p["n_in_bin"][idx]
    rho = p["rho_Msun_pc3"][idx]
    rho_err = p["rho_err_Msun_pc3"][idx]
    rel_err = n > 0 ? rho_err / rho : Inf
    @printf "  t=%6.3f Myr: rho(500pc)=%.4e ± %.4e Msun/pc^3 (N_in=%d, rel_err=%.0f%%)\n" p["t_myr"] rho rho_err n (rel_err * 100)
end

println()
println("Density evolution at r ≈ r_s = $R_S_PC pc (with Poisson errors):")
for p in profiles
    idx = argmin(abs.(p["r_bins_pc"] .- R_S_PC))
    n = p["n_in_bin"][idx]
    rho = p["rho_Msun_pc3"][idx]
    rho_err = p["rho_err_Msun_pc3"][idx]
    rel_err = n > 0 ? rho_err / rho : Inf
    @printf "  t=%6.3f Myr: rho(r_s)=%.4e ± %.4e Msun/pc^3 (N_in=%d, rel_err=%.0f%%)\n" p["t_myr"] rho rho_err n (rel_err * 100)
end

println()
println("END")