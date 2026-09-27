using JLD2, Unitful, UnitfulAstro, Printf, JSON

const SNAP_DIR = "/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/snapshots_t215_safe"
const OUT_PATH = "/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results/t215_density_profiles_safe.json"
const R_S_PC = 2924.4
const R_VIR_PC = 35092.9
const M_HALO_MSUN = 5.0e9

snap_files = sort(filter(p -> endswith(p, ".jld2"), readdir(SNAP_DIR, join=true)))
println("Found $(length(snap_files)) snapshots")

n_bins = 15
r_bins = 10 .^ range(log10(50.0), stop=log10(R_VIR_PC), length=n_bins+1)

profiles = []
for snap_path in snap_files
    s = JLD2.load(snap_path)
    positions = s["positions"]
    t_q = s["time"]
    t_pc = ustrip(uconvert(u"pc * s / km", t_q))
    t_myr = t_pc * 0.978
    npart = length(positions)

    radii = [ustrip(pos.data[1][1]) for pos in positions]

    rho_bins = Float64[]
    for i in 1:n_bins
        r_in = r_bins[i]
        r_out = r_bins[i+1]
        in_shell = (radii .>= r_in) .& (radii .< r_out)
        n_in = sum(in_shell)
        shell_vol = (4.0/3.0) * pi * (r_out^3 - r_in^3)
        n_phys_per_tracer = M_HALO_MSUN / 3000.0
        mass_in = n_in * n_phys_per_tracer
        rho = mass_in / shell_vol
        push!(rho_bins, rho)
    end

    push!(profiles, Dict(
        "snap" => basename(snap_path),
        "t_myr" => t_myr,
        "npart" => npart,
        "r_bins_pc" => r_bins[1:end-1],
        "rho_Msun_pc3" => rho_bins,
    ))
end

output = Dict(
    "halo_params" => Dict("M_Msun" => M_HALO_MSUN, "r_s_pc" => R_S_PC, "r_vir_pc" => R_VIR_PC),
    "n_snapshots" => length(snap_files),
    "profiles" => profiles,
)
mkpath(dirname(OUT_PATH))
open(OUT_PATH, "w") do f
    JSON.print(f, output, 2)
end

println()
println("Density evolution at r = r_s ($R_S_PC pc):")
for p in profiles
    idx = argmin(abs.(p["r_bins_pc"] .- R_S_PC))
    @printf "  t=%6.3f Myr: rho=%.4e Msun/pc^3\n" p["t_myr"] p["rho_Msun_pc3"][idx]
end

println()
println("Density at small r (interior):")
for p in profiles
    idx = argmin(abs.(p["r_bins_pc"] .- 500.0))
    @printf "  t=%6.3f Myr: rho(500pc)=%.4e Msun/pc^3\n" p["t_myr"] p["rho_Msun_pc3"][idx]
end

println("END")