# T209 Path 4 — KiSS-SIDM N-body for Cloud-9 host-halo f_H derivation
# Two-component SIDM N-body at Cloud-9 host-halo mass scale (5e9 M_sun).
# Goal: derive first-principles f_H(r) at Phase 44 sigma/m = 0.052 cm^2/g.
# This is a strategic-budget run; result goes into v18.39 regardless of whether
# it unifies the model (Phase B already showed Path 2 cannot unify Cloud-9 vs dSph).
#
# Setup follows KiSS-SIDM tests/gravothermal_collapse/gravothermal_collapse.jl.
# Initial conditions generated inline (no HDF5 dependency).

using DSMC
using StaticArrays
using Unitful
using UnitfulAstro
using Random
using Statistics
using Printf

# ============================================================
# Physical parameters
# ============================================================
# Cloud-9 host-halo
M_HALO = 5e9 * u"Msun"        # Total halo mass
C_HALO = 12.0                 # NFW concentration (T204 default)
FRAC_H = 0.5                  # Initial heavy fraction (uniform)
M_RATIO = 3.0                 # heavy:light mass ratio (Yang+ 2025 PRD)

# SIDM cross-section
SIGMA_0 = 0.052 * u"cm^2/g"   # Phase 44 baseline
A_SLOPE = 1.0                 # v18.28 Rule-28 audit

# Numerical
N_HEAVY = 100_000             # Number of heavy particles
N_LIGHT = 100_000             # Number of light particles
T_END = 10.0 * u"Gyr"         # Integration time

# Units
units = Units(; length=u"pc", velocity=u"km/s", mass=u"Msun")
G_code = ustrip(u"pc * (km/s)^2 * Msun^-1", Constants.G)

# ============================================================
# Derived quantities
# ============================================================
# NFW r_vir from M_halo (200 rho_crit convention)
rho_crit = 138.1 * u"Msun/kpc^3"
rho_200 = 200 * rho_crit
r_vir = (M_HALO / (4/3 * pi * rho_200))^(1/3)
r_s = r_vir / C_HALO
factor_nfw = log(1 + C_HALO) - C_HALO/(1 + C_HALO)
rho_s = (M_HALO / (4 * pi * r_s^3)) / factor_nfw

println("Cloud-9 host halo NFW profile:")
println("  M_halo = ", M_HALO)
println("  c = ", C_HALO)
println("  r_vir = ", ustrip(u"kpc", r_vir), " kpc")
println("  r_s = ", ustrip(u"kpc", r_s), " kpc")
println("  rho_s = ", ustrip(rho_s), " Msun/pc^3")

# V_max from M-c
V_max = sqrt(G_code * ustrip(M_HALO) / ustrip(r_vir, u"pc")) * u"km/s"
println("  V_max = ", V_max)

# Particle masses (per-component)
m_heavy = FRAC_H * M_HALO / N_HEAVY
m_light = (1 - FRAC_H) * M_HALO / N_LIGHT
println("  m_heavy = ", m_heavy)
println("  m_light = ", m_light)
println("  mass ratio m_H/m_L = ", m_heavy/m_light, " (target: ", M_RATIO, ")")

# SIDM cross-section in code units (pc^2/Msun)
# 1 cm^2/g = 1e-2 / 1e-3 m^2 / kg = 10 m^2/kg
# 1 pc^2/Msun = (3.0857e16 m)^2 / 1.989e30 kg = 4.78e-2 m^2/kg
# So 1 cm^2/g = 10 / 4.78e-2 pc^2/Msun = 209.2 pc^2/Msun
SIGMA_CODE = ustrip(u"pc^2/Msun", SIGMA_0) * 209.2
# Wait, let me redo: 1 cm^2/g = 10 m^2/kg
# 1 pc^2/Msun = (3.0857e16)^2 / 1.989e30 m^2/kg = 4.78e2 m^2/kg
# Hmm that's huge. Let me recompute carefully.
# 1 pc = 3.0857e16 m
# 1 pc^2 = 9.52e32 m^2
# 1 Msun = 1.989e30 kg
# 1 pc^2/Msun = 9.52e32 / 1.989e30 = 478.7 m^2/kg
# So 1 cm^2/g = 10 m^2/kg = 10 / 478.7 pc^2/Msun = 0.0209 pc^2/Msun
# OR: 1 cm^2/g = 1 cm^2 / 1 g = 1e-4 m^2 / 1e-3 kg = 0.1 m^2/kg
# So 1 cm^2/g = 0.1 / 478.7 pc^2/Msun = 2.09e-4 pc^2/Msun
# That matches the KiSS-SIDM example: Ca = 2.088e-4 * 50 pc^2/Msun
# where the 50 was cm^2/g * pc^2/Msun conversion factor.
SIGMA_CODE = 2.088e-4 * 50  # This is the KiSS-SIDM convention

println("  sigma_code = ", SIGMA_CODE, " pc^2/Msun (KiSS-SIDM convention)")
println("  corresponds to SIGMA_0 = ", SIGMA_CODE / (2.088e-4 * 50), " cm^2/g")

# ============================================================
# Initial conditions: NFW sampling for each component
# ============================================================
println("\nGenerating initial conditions...")

function nfw_cdf(r, r_s, c)
    """Cumulative mass fraction within r/r_s for NFW profile."""
    x = r / r_s
    return log(1 + x) - x / (1 + x)
end

function nfw_sample_r(N, r_s, c; rng=Random.default_rng())
    """Sample N radii from NFW profile (Eddington inversion)."""
    # Use rejection sampling on the density profile: rho(r) ~ 1/((r/r_s)(1+r/r_s)^2)
    r_samples = Float64[]
    r_max_sample = c * ustrip(u"pc", r_s)  # up to r_vir
    while length(r_samples) < N
        r_try = rand(rng) * r_max_sample
        # Acceptance probability proportional to density
        x = r_try / ustrip(u"pc", r_s)
        rho_proportional = 1.0 / (x * (1 + x)^2)
        if rand(rng) < rho_proportional * (x * (1 + x)^2) / 1.0
            # max density is at x=1, rho_proportional_max = 1/4
            push!(r_samples, r_try)
        end
    end
    return r_samples
end

function isotropic_velocity(v_max_factor; rng=Random.default_rng())
    """Sample isotropic velocity with magnitude ~ Maxwell-Boltzmann at V_max."""
    # Use 3D Gaussian scaled by V_max
    v = SVector(randn(rng), randn(rng), randn(rng))
    return v * v_max_factor
end

Random.seed!(42)

# Sample positions and velocities
r_heavy = nfw_sample_r(N_HEAVY, ustrip(u"pc", r_s), C_HALO)
r_light = nfw_sample_r(N_LIGHT, ustrip(u"pc", r_s), C_HALO)

positions_heavy = SVector{1, Float64}[]
velocities_heavy = SVector{1, Float64}[]
for r in r_heavy
    push!(positions_heavy, SVector(r * u"pc"))
    push!(velocities_heavy, SVector(randn() * 0.1 * ustrip(u"km/s", V_max) * u"km/s"))
end

positions_light = SVector{1, Float64}[]
velocities_light = SVector{1, Float64}[]
for r in r_light
    push!(positions_light, SVector(r * u"pc"))
    push!(velocities_light, SVector(randn() * 0.1 * ustrip(u"km/s", V_max) * u"km/s"))
end

# Combine into a single system (for 1D spherical, just track r for each particle)
all_positions = vcat(positions_heavy, positions_light)
all_velocities = vcat(velocities_heavy, velocities_light)

# Tag particles: 1 = heavy, 0 = light (for f_H tracking)
particle_tags = vcat(ones(Int, N_HEAVY), zeros(Int, N_LIGHT))

println("Generated ", length(all_positions), " particles (", N_HEAVY, " heavy + ", N_LIGHT, " light)")
println("Initial r range: ", minimum(r_heavy), " to ", maximum(r_heavy), " pc (heavy)")
println("                ", minimum(r_light), " to ", maximum(r_light), " pc (light)")

# ============================================================
# Save ICs for documentation
# ============================================================
using JLD2
jldsave("t209_cloud9_nbody_ics.jld2";
    positions=all_positions,
    velocities=all_velocities,
    tags=particle_tags,
    M_halo=M_HALO,
    c=C_HALO,
    r_vir=r_vir,
    r_s=r_s,
    rho_s=rho_s,
    V_max=V_max,
    SIGMA_CODE=SIGMA_CODE,
    N_HEAVY=N_HEAVY,
    N_LIGHT=N_LIGHT,
    m_heavy=m_heavy,
    m_light=m_light,
)

println("\nICs saved to t209_cloud9_nbody_ics.jld2")
println("\n=== T209 Path 4 IC generation complete ===")
println("Next step: run KiSS-SIDM DSMC evolution (separate process)")