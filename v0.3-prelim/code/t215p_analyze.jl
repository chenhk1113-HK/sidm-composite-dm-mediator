using JLD2, Unitful, UnitfulAstro, Printf, JSON

# Per-run density analysis. Takes run_idx from command line.

run_idx = parse(Int, ARGS[1])
SNAP_DIR = "/tmp/t215p_run$(run_idx)_output"
OUT_PATH = "/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results/t215p_run$(run_idx)_density.json"

const R_S_PC = 2924.4
const R_VIR_PC = 35092.9

const PC_PER_KMS_TO_MYR = 0.9777922216807892

snap_files = sort(filter(p -> endswith(p, ".jld2"), readdir(SNAP_DIR, join=true)))
println("Run $run_idx: Found $(length(snap_files)) snapshots")

n_bins = 15
r_bins = 10 .^ range(log10(50.0), stop=log10(R_VIR_PC), length=n_bins+1)

first_snap = JLD2.load(snap_files[1])
npart_first = length(first_snap["positions"])
M_HALO_MSUN = 5.0e9
n_phys_per_tracer = M_HALO_MSUN / npart_first

profiles = []
for snap_path in snap_files
    s = JLD2.load(snap_path)
    positions = s["positions"]
    t_q = s["time"]
    t_pc = ustrip(uconvert(u"pc * s / km", t_q))
    t_myr = t_pc * PC_PER_KMS_TO_MYR
    npart = length(positions)

    radii = [ustrip(pos.data[1][1]) for pos in positions]

    rho_bins = Float64[]
    rho_err_bins = Float64[]
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
            rho_err = rho / sqrt(n_in)
            push!(rho_bins, rho)
            push!(rho_err_bins, rho_err)
        else
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
    "run_idx" => run_idx,
    "n_snapshots" => length(snap_files),
    "n_phys_per_tracer_Msun" => n_phys_per_tracer,
    "profiles" => profiles,
)
mkpath(dirname(OUT_PATH))
open(OUT_PATH, "w") do f
    JSON.print(f, output, 2)
end

# Print summary at key radii
println("\n=== Run $run_idx Summary ===")
println("Density at r=287 pc:")
for p in profiles
    idx = argmin(abs.(p["r_bins_pc"] .- 287.0))
    n = p["n_in_bin"][idx]
    rho = p["rho_Msun_pc3"][idx]
    @printf "  t=%6.3f Myr: rho=%.4e Msun/pc^3 (N=%d)\n" p["t_myr"] rho n
end
println("\nDensity at r=444 pc:")
for p in profiles
    idx = argmin(abs.(p["r_bins_pc"] .- 444.0))
    n = p["n_in_bin"][idx]
    rho = p["rho_Msun_pc3"][idx]
    @printf "  t=%6.3f Myr: rho=%.4e Msun/pc^3 (N=%d)\n" p["t_myr"] rho n
end
println("\nDensity at r=r_s:")
for p in profiles
    idx = argmin(abs.(p["r_bins_pc"] .- R_S_PC))
    n = p["n_in_bin"][idx]
    rho = p["rho_Msun_pc3"][idx]
    @printf "  t=%6.3f Myr: rho=%.4e Msun/pc^3 (N=%d)\n" p["t_myr"] rho n
end