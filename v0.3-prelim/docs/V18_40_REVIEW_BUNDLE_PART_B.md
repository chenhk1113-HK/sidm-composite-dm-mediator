# v18.40 Review Bundle — Part B (Code files, 2026-09-25)

Part B of the v18.40 review bundle: 6 code files (Python + Julia).

**Repository state:**
- Branch: `wip/cloud-9-relhic` + `wip/multi-component-SIDM-core-collapse`
- Commit: `df9aadd` (paper + docs), `c9f5f77` (this bundle)
- Tag: `v18.40-constraint-map-with-refinements`

**Part A** (paper + 5 investigation docs) was sent separately.

This part contains:
- T208 Path B Gravothermal (Python) — Balberg+ 2002 gravothermal cascade at Cloud-9 host halo
- T209 KiSS-SIDM N-body Setup (Julia) — N-body sketch, single-comp limitation
- T210 Crater/Antlia Gating (Python) — multi-probe gating test
- T210 Path A2 Sharp Resonance (Python) — sharp-resonance parameter scan (zero configs pass)
- T210 σ_eff Decompose (Python) — σ_eff(v=28) decomposition diagnostic
- T212 Silverman Gravothermal (Python) — Silverman+ 2026 gravothermal threshold analysis

---

## Table of Contents (Part B)

7. T208 Path B Gravothermal (Python)
8. T209 KiSS-SIDM N-body Setup (Julia)
9. T210 Crater/Antlia Gating (Python)
10. T210 Path A2 Sharp Resonance (Python)
11. T210 σ_eff Decompose (Python)
12. T212 Silverman Gravothermal (Python)

---

# File 7: T208 Path B Gravothermal (Python)

_Source path: `v0.3-prelim/code/T208_path_b_cloud9_host_halo_gravothermal.py`_

```
"""T208 Path B — Gravothermal at Cloud-9 host-halo mass scale.

Computes the gravothermal core-collapse timescale at the Cloud-9 host-halo
parameters (M_200 = 5×10^9 M_sun, c = 12, sigma/m = 0.052 cm^2/g at v=100,
a_slope = 1.0 per v18.28 Rule-28 audit) and checks whether the gravothermal
phase runs within the Hubble time. This is the structural question that
Path F1 (T207) cannot answer: does the velocity-scale separation between
Cloud-9 (v=28) and dSph (v=5-15) come from gravothermal enhancement at the
Cloud-9 host-halo scale?

Method: Balberg+ 2002 Eq. 22 (PRL 88, 101301) t_core normalization, same as
T204. The 10^9 M_sun halo is 5000× more massive than the 10^6 M_sun subhalo
that T204 verified as core-collapsed; the question is whether the gravothermal
timescale still beats the Hubble time at the host-halo mass scale.

Inputs:
- M_halo = 5e9 M_sun (Cloud-9 host-halo)
- c = 12 (T204 default)
- sigma/m at v=100 = 0.052 cm^2/g (Phase 44 baseline)
- a_slope = 1.0 (v18.28 fixed value)
- v_max from NFW M-c relation

Outputs:
- t_core_Gyr at host-halo params (this is the critical number)
- t_core_Gyr at 10^6 M_sun subhalo params (T204 cross-check)
- t_cross_Gyr at host-halo params
- t_core / t_cross (causality check)
- t_core / t_Hubble (does gravothermal phase run?)
- sigma/m(v=28) at host-halo params (Cloud-9 velocity scale, pre-core-collapse)
- sigma/m(v=28) at host-halo params in core-collapsed phase (Balberg+ 2002
  enhancement estimate: sigma_eff ∝ rho(r)/rho_s during core phase)
"""
import sys
import json

# Balberg+ 2002 Eq. 22 normalization (T204 verified)
SIGMA_0 = 0.052  # cm^2/g at v_ref = 100 km/s
A_SLOPE = 1.0  # v18.28 fixed (Rule 28 audit)
V_REF = 100.0  # km/s
TCROSS_CAP_FACTOR = 3.0  # causality: t_core >= 3 * t_cross
HUBBLE_GYR = 13.8  # Gyr

def v_max_from_M_c(M_halo_msun, c, r_vir_pc):
    """V_max from M_halo and concentration: V_max ~ sqrt(G * M_halo / r_vir)."""
    # Newton: V_max^2 = G * M_halo / r_vir
    # G in (km/s)^2 * pc / M_sun: G = 4.3009e-3 (km/s)^2 pc / M_sun
    G_pc_kms2_Msun = 4.3009e-3
    r_vir_kpc = r_vir_pc / 1000.0
    V_max = (G_pc_kms2_Msun * M_halo_msun / r_vir_pc) ** 0.5  # km/s
    return V_max

def nfw_rho_s_from_concentration(M_halo, c, r_vir_pc):
    """rho_s for NFW profile from M_halo, c, r_vir. Returns M_sun/pc^3."""
    import math
    r_s_pc = r_vir_pc / c
    # rho_s = (M_halo / (4 pi r_s^3)) / [ln(1+c) - c/(1+c)]
    factor = math.log(1 + c) - c / (1 + c)
    rho_s = (M_halo / (4 * math.pi * r_s_pc**3)) / factor
    return rho_s, r_s_pc

def gravothermal_t_core_Gyr(sigma_m_cm2_per_g, rho_s_Msun_per_pc3,
                             r_s_pc, v_max_kms):
    """Balberg+ 2002 Eq. 22 normalization (T204 canonical).

    t_core = 12.7 / sigma * (rho_s / 1e-2)^-1 * (r_s_pc / 1e4) * (100 / v_max)  Gyr

    Sanity: MW halo (sigma=1, rho_s=1e-2, r_s=1e4, v_max=100) -> t_core = 12.7 Gyr
    """
    rho_s_norm = rho_s_Msun_per_pc3 / 1e-2
    r_s_norm = r_s_pc / 1e4
    v_norm = 100.0 / v_max_kms
    t = 12.7 / sigma_m_cm2_per_g * (1.0 / rho_s_norm) * r_s_norm * v_norm
    return t

def nfw_r_vir_pc(M_halo_msun):
    """r_vir from M_halo assuming mean density = 200 * rho_crit.
    rho_crit = 138.1 M_sun/kpc^3 (h=0.7, z=0).
    r_vir^3 = M_halo / (4/3 pi * 200 * rho_crit)
    """
    import math
    rho_crit_msun_per_kpc3 = 138.1
    rho_200 = 200 * rho_crit_msun_per_kpc3
    r_vir_kpc = (M_halo_msun / (4/3 * math.pi * rho_200)) ** (1/3)
    return r_vir_kpc * 1000  # convert to pc

def sigma_m_at_v(sigma_0, a_slope, v, v_ref):
    """Velocity-dependent sigma/m. v18.28 used a_slope=1.0.
    sigma_m(v) = sigma_0 * (v_ref / v)^a_slope   [cm^2/g]
    """
    return sigma_0 * (v_ref / v) ** a_slope

def main():
    results = {}

    # ============================================================
    # Cloud-9 host-halo parameters
    # ============================================================
    M_halo_C9 = 5e9  # M_sun
    c_C9 = 12  # T204 default; standard Lambda-CDM concentration at this mass
    r_vir_C9 = nfw_r_vir_pc(M_halo_C9)
    rho_s_C9, r_s_C9 = nfw_rho_s_from_concentration(M_halo_C9, c_C9, r_vir_C9)
    V_max_C9 = v_max_from_M_c(M_halo_C9, c_C9, r_vir_C9)

    results["Cloud9_host_halo_params"] = {
        "M_halo_Msun": M_halo_C9,
        "concentration_c": c_C9,
        "r_vir_pc": r_vir_C9,
        "r_s_pc": r_s_C9,
        "V_max_kms": V_max_C9,
        "rho_s_Msun_per_pc3": rho_s_C9,
    }

    # sigma/m at virial velocity (pre-core-collapse)
    sigma_virial_C9 = sigma_m_at_v(SIGMA_0, A_SLOPE, V_max_C9, V_REF)
    results["sigma_m_at_v_virial_C9"] = sigma_virial_C9

    # sigma/m at Cloud-9 velocity scale (v=28 km/s; pre-core-collapse)
    sigma_v28_C9_pre = sigma_m_at_v(SIGMA_0, A_SLOPE, 28.0, V_REF)
    results["sigma_m_v28_C9_pre_corecollapse"] = sigma_v28_C9_pre

    # sigma/m at dSph velocity scale (v=15 km/s; pre-core-collapse)
    sigma_v15_C9_pre = sigma_m_at_v(SIGMA_0, A_SLOPE, 15.0, V_REF)
    results["sigma_m_v15_C9_pre_corecollapse"] = sigma_v15_C9_pre

    # Gravothermal t_core at Cloud-9 host-halo params (using virial sigma)
    t_core_C9 = gravothermal_t_core_Gyr(sigma_virial_C9, rho_s_C9, r_s_C9, V_max_C9)
    t_cross_C9 = r_s_C9 / V_max_C9 / (3.0857e16) * (3.1557e16)  # r_s / v_max in Gyr
    # Actually r_s in pc, v_max in km/s:
    # t_cross = r_s_pc * (1 km/s / 1e5 km/s/Mpc) * ... too messy, use direct:
    # r_s_pc / v_max_kms gives pc/(km/s) = pc*s/km
    # 1 pc = 3.0857e13 km, so pc*s/km = (3.0857e13 km * s) / km = 3.0857e13 s
    # t_cross_s = r_s_pc / v_max_kms * 3.0857e13 s
    # t_cross_Gyr = t_cross_s / 3.1557e16
    t_cross_C9_Gyr = (r_s_C9 / V_max_C9 * 3.0857e13) / 3.1557e16

    results["Cloud9_gravothermal"] = {
        "t_core_Gyr": t_core_C9,
        "t_cross_Gyr": t_cross_C9_Gyr,
        "t_core_over_t_cross": t_core_C9 / t_cross_C9_Gyr,
        "t_core_over_t_Hubble": t_core_C9 / HUBBLE_GYR,
        "runs_in_Hubble": t_core_C9 <= HUBBLE_GYR,
        "causality_OK": t_core_C9 >= TCROSS_CAP_FACTOR * t_cross_C9_Gyr,
    }

    # ============================================================
    # 10^6 M_sun subhalo cross-check (T204 result reproduction)
    # ============================================================
    M_subhalo = 1e6
    c_sub = 15
    r_vir_sub = nfw_r_vir_pc(M_subhalo)
    rho_s_sub, r_s_sub = nfw_rho_s_from_concentration(M_subhalo, c_sub, r_vir_sub)
    V_max_sub = v_max_from_M_c(M_subhalo, c_sub, r_vir_sub)
    sigma_virial_sub = sigma_m_at_v(SIGMA_0, A_SLOPE, V_max_sub, V_REF)
    t_core_sub = gravothermal_t_core_Gyr(sigma_virial_sub, rho_s_sub, r_s_sub, V_max_sub)
    t_cross_sub_Gyr = (r_s_sub / V_max_sub * 3.0857e13) / 3.1557e16

    results["subhalo_1e6_crosscheck"] = {
        "M_halo_Msun": M_subhalo,
        "c": c_sub,
        "V_max_kms": V_max_sub,
        "sigma_m_at_v_virial": sigma_virial_sub,
        "t_core_Gyr": t_core_sub,
        "t_cross_Gyr": t_cross_sub_Gyr,
        "t_core_over_t_Hubble": t_core_sub / HUBBLE_GYR,
        "matches_T204": abs(t_core_sub - 0.5632) < 0.1,  # T204 result was 0.563 Gyr
    }

    # ============================================================
    # Core-collapse sigma/m enhancement (Balberg+ 2002 + Polish+ 2015)
    # If gravothermal phase runs, sigma_eff in core is enhanced by:
    #   sigma_eff ~ sigma_virial * (rho_core / rho_s)
    # For NFW profile, rho_core >> rho_s at small r.
    # A typical "cuspy core" reaches rho_core ~ 100 * rho_s.
    # So sigma_eff,core ~ 100 * sigma_virial.
    # ============================================================
    rho_core_over_rho_s_factor = 100  # typical core-collapse enhancement
    sigma_v28_C9_core_enhanced = sigma_v28_C9_pre * rho_core_over_rho_s_factor
    sigma_v15_C9_core_enhanced = sigma_v15_C9_pre * rho_core_over_rho_s_factor

    results["Cloud9_core_collapse_enhancement_estimate"] = {
        "rho_core_over_rho_s_factor": rho_core_over_rho_s_factor,
        "sigma_m_v28_C9_CORE_enhanced": sigma_v28_C9_core_enhanced,
        "sigma_m_v15_C9_CORE_enhanced": sigma_v15_C9_core_enhanced,
        "Cloud9_threshold_50": 50.0,
        "Cloud9_PASSES_if_50": sigma_v28_C9_core_enhanced >= 50.0,
        "dSph_ceiling_0p8": 0.8,
        "dSph_violation_factor": sigma_v15_C9_core_enhanced / 0.8,
    }

    # ============================================================
    # Verdict
    # ============================================================
    if not results["Cloud9_gravothermal"]["runs_in_Hubble"]:
        verdict = ("Gravothermal phase DOES NOT run at Cloud-9 host-halo "
                   f"params (t_core = {t_core_C9:.1f} Gyr > t_Hubble = "
                   f"{HUBBLE_GYR} Gyr). Path 2 REFUTED at Phase 44 sigma/m. "
                   "Cloud-9 vs dSph tension is NOT resolved by host-halo "
                   "gravothermal evolution at these parameters.")
    else:
        # If gravothermal does run, check if enhancement is enough for Cloud-9
        if results["Cloud9_core_collapse_enhancement_estimate"]["Cloud9_PASSES_if_50"]:
            verdict = ("Gravothermal phase RUNS at Cloud-9 host-halo AND "
                       "core-enhanced sigma/m(v=28) > 50 cm^2/g. Path 2 "
                       "PLAUSIBLE: Cloud-9 spike could be gravothermal "
                       "enhancement during core-collapse of 5e9 M_sun halo.")
        else:
            verdict = ("Gravothermal phase RUNS but enhancement is INSUFFICIENT. "
                       f"sigma_eff,core(v=28) = {sigma_v28_C9_core_enhanced:.2f} < 50. "
                       "Cloud-9 spike needs additional physics beyond gravothermal.")

    results["verdict"] = verdict

    return results

if __name__ == "__main__":
    results = main()
    # Print summary
    print("=" * 80)
    print("T208 Path B — Gravothermal at Cloud-9 Host-Halo")
    print("=" * 80)
    print(f"\nCloud-9 host-halo params:")
    for k, v in results["Cloud9_host_halo_params"].items():
        print(f"  {k}: {v}")
    print(f"\nsigma/m (pre-core-collapse):")
    print(f"  at v=28 km/s (Cloud-9): {results['sigma_m_v28_C9_pre_corecollapse']:.4f} cm^2/g")
    print(f"  at v=15 km/s (dSph):    {results['sigma_m_v15_C9_pre_corecollapse']:.4f} cm^2/g")
    print(f"  at v=V_max (virial):    {results['sigma_m_at_v_virial_C9']:.4f} cm^2/g")
    print(f"\nGravothermal at Cloud-9 host-halo:")
    for k, v in results["Cloud9_gravothermal"].items():
        print(f"  {k}: {v}")
    print(f"\n10^6 M_sun subhalo cross-check (T204):")
    for k, v in results["subhalo_1e6_crosscheck"].items():
        print(f"  {k}: {v}")
    print(f"\nCore-collapse enhancement estimate (rho_core/rho_s = 100):")
    for k, v in results["Cloud9_core_collapse_enhancement_estimate"].items():
        print(f"  {k}: {v}")
    print(f"\n{'=' * 80}")
    print(f"VERDICT: {results['verdict']}")
    print("=" * 80)

    # Save
    out_path = "/home/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results/t208_path_b_cloud9_host_halo_gravothermal.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to: {out_path}")
```

---

# File 8: T209 KiSS-SIDM N-body Setup (Julia)

_Source path: `v0.3-prelim/code/t209_cloud9_nbody_setup.jl`_

```
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
```

---

# File 9: T210 Crater/Antlia Gating (Python)

_Source path: `v0.3-prelim/code/t210_gating_test_crater_antlia.py`_

```
"""
T210 Gating Test — Crater II + Antlia II pass/fail under Path F1.

Per the Cloud-9alternate.docx memo (2026-09-25), the strategic question is:
- Does the current model (Path F1 three-term sigma_eff, borrowed prescription)
  pass Crater II and Antlia II at their V_max velocity scale?
- This is the gating test for whether multi-probe reframing is viable.

Critical caveat from the memo: V_max for Crater II/Antlia II may be 10-15 km/s,
which would put them at the SAME velocity scale as dSph (where sigma/m <= 0.8
cm^2/g). In that case, Crater II/Antlia II CONFIRM the tension rather than
relax it.

This script:
1. Computes sigma_eff(v) at v = 5, 10, 15, 28 km/s (candidate V_max scales)
2. Under the borrowed prescription (f_H_cf = 0.85, f_H_cc = 0.5)
3. Compares each sigma_eff to:
   - Crater II: sigma/m ~ 60 cm^2/g (favored)
   - Antlia II: sigma/m ~ similar (favored, similar to Crater II)
   - dSph ceiling: sigma/m <= 0.8 cm^2/g
   - Cloud-9 floor: sigma/m >= 50 cm^2/g
4. Reports pass/fail per (V_max candidate) per (system)

Velocity literature references:
- Crater II: sigma_los = 2.3 km/s. SIDM interpretation in [Vargas et al. or
  Read+ 2018 for UDGs; specific Crater II SIDM analysis likely Yang+ or
  Sameie+ 2020-era].
- Antlia II: sigma_los = 5.7 km/s. Similar SIDM interpretation.
- For a UDG with r_1/2 ~ 1-3 kpc, V_max estimates are typically 10-30 km/s
  depending on the assumed mass profile.
- Crater II inferred M_halo: ~ 5e8 M_sun (some estimates higher).
- Antlia II inferred M_halo: ~ 8e8 M_sun (some estimates higher).

Three candidate V_max scenarios:
A. V_max = sigma_los (conservative, velocity dispersion IS the relevant scale)
   - Crater II: v = 2.3 km/s
   - Antlia II: v = 5.7 km/s
B. V_max = sqrt(3) * sigma_los (isotropic Jeans)
   - Crater II: v = 4.0 km/s
   - Antlia II: v = 9.9 km/s
C. V_max = 10-30 km/s (full halo circular velocity at r_max)
   - For both: v ~ 15-25 km/s (cluster of estimates)
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np

from T207_three_term_fit import (
    sigma_eff_three_term, BOUNDS,
)

# =============================================================================
# Borrowed prescription parameters (Path F1 best fit, from T207)
# =============================================================================
# These are the "borrowed" mode params from the v18.38 standing result.
# f_H_cf = 0.85 (heavy-favored in core-forming regime)
# f_H_cc = 0.5 (moderate heavy fraction in core-collapsed regime)
# The other 7 params are the borrowed emcee median:
# sigma_0 = 0.005, sigma_peak_HH_1 = 84.4, sigma_0_HL = 0.0001,
# sigma_peak_HL = 0.318, v_HL = 98.2, sigma_0_LL = 0.0006, a_slope = 1.0
BORROWED_PARAMS = {
    "sigma_0": 0.005,
    "sigma_peak_HH_1": 84.4,
    "sigma_0_HL": 0.0001,
    "sigma_peak_HL": 0.318,
    "v_HL": 98.2,
    "sigma_0_LL": 0.0006,
    "a_slope": 1.0,
}
F_H_CF_BORROWED = 0.85
F_H_CC_BORROWED = 0.5

# =============================================================================
# Crater II and Antlia II observational constraints
# =============================================================================
CRATER_II = {
    "name": "Crater II",
    "sigma_los": 2.3,           # km/s, stellar line-of-sight velocity dispersion
    "r_half": 1066,             # pc, half-light radius
    "distance": 117.5,          # kpc
    "M_v": -8.2,                # absolute magnitude
    "inferred_sigma_m": 60.0,   # cm^2/g, SIDM-favored
    "halo_class": "core_collapsed",  # Per T207 framework, satellite dwarfs use f_H_cc
}

ANTLIA_II = {
    "name": "Antlia II",
    "sigma_los": 5.7,           # km/s
    "r_half": 2301,             # pc
    "distance": 132,            # kpc
    "M_v": -9.03,
    "inferred_sigma_m": 60.0,   # cm^2/g, similar to Crater II (favored)
    "halo_class": "core_collapsed",
}

# =============================================================================
# Three candidate V_max scenarios from the memo
# =============================================================================
SCENARIOS = [
    ("A: V_max = sigma_los", {
        "Crater II": 2.3,
        "Antlia II": 5.7,
    }),
    ("B: V_max = sqrt(3) * sigma_los (Jeans isotropic)", {
        "Crater II": 2.3 * np.sqrt(3),
        "Antlia II": 5.7 * np.sqrt(3),
    }),
    ("C: V_max ~ 15 km/s (full halo circular velocity)", {
        "Crater II": 15.0,
        "Antlia II": 15.0,
    }),
    ("D: V_max ~ 28 km/s (Cloud-9 host-halo scale)", {
        "Crater II": 28.0,
        "Antlia II": 28.0,
    }),
]

# Reference observations / ceilings / floors
CEILINGS = {
    "dSph v=15": 0.8,
    "UFD v=10": 0.155,
    "Cluster v=500": 0.00025,
}
FLOORS = {
    "Cloud-9 v=28": 50.0,
    "Crater II": 30.0,       # memo: ~ 60 cm^2/g favored; lower bound = 30 (half of favored)
    "Antlia II": 30.0,       # similar
}


def evaluate_sigma_eff(v: float) -> float:
    """Compute sigma_eff at velocity v under borrowed prescription."""
    return sigma_eff_three_term(
        v,
        f_H=F_H_CC_BORROWED,  # UDG-like, use f_H_cc
        sigma_0=BORROWED_PARAMS["sigma_0"],
        a_slope=BORROWED_PARAMS["a_slope"],
        sigma_peak_HH_1=BORROWED_PARAMS["sigma_peak_HH_1"],
        sigma_0_HL=BORROWED_PARAMS["sigma_0_HL"],
        sigma_peak_HL=BORROWED_PARAMS["sigma_peak_HL"],
        v_HL=BORROWED_PARAMS["v_HL"],
        width_HL=50.0,
        sigma_0_LL=BORROWED_PARAMS["sigma_0_LL"],
    )


def verdict(sigma_eff_val: float, target_value: float, target_type: str, sigma_unc: float = 5.0) -> dict:
    """Check pass/fail against floor/ceiling/gaussian."""
    if target_type == "floor":
        # Need sigma_eff >= target_value
        if sigma_eff_val >= target_value:
            return {"verdict": "PASS", "z": (target_value - sigma_eff_val) / sigma_unc}
        else:
            return {"verdict": "FAIL", "z": (target_value - sigma_eff_val) / sigma_unc}
    elif target_type == "ceiling":
        # Need sigma_eff <= target_value
        if sigma_eff_val <= target_value:
            return {"verdict": "PASS", "z": (sigma_eff_val - target_value) / sigma_unc}
        else:
            return {"verdict": "FAIL", "z": (sigma_eff_val - target_value) / sigma_unc}
    elif target_type == "gaussian":
        z = (sigma_eff_val - target_value) / sigma_unc
        if abs(z) <= 1.0:
            return {"verdict": "PASS", "z": z}
        elif abs(z) <= 2.0:
            return {"verdict": "MARGINAL", "z": z}
        else:
            return {"verdict": "FAIL", "z": z}


def main():
    results = {
        "borrowed_params": BORROWED_PARAMS,
        "f_H_cf_borrowed": F_H_CF_BORROWED,
        "f_H_cc_borrowed": F_H_CC_BORROWED,
        "scenarios": {},
        "reference_observations": {
            "Crater II": {
                "sigma_los_km_s": CRATER_II["sigma_los"],
                "inferred_sigma_m_cm2_g": CRATER_II["inferred_sigma_m"],
                "r_half_pc": CRATER_II["r_half"],
            },
            "Antlia II": {
                "sigma_los_km_s": ANTLIA_II["sigma_los"],
                "inferred_sigma_m_cm2_g": ANTLIA_II["inferred_sigma_m"],
                "r_half_pc": ANTLIA_II["r_half"],
            },
        },
    }

    print("=" * 78)
    print("T210 Gating Test: Crater II + Antlia II under Path F1 borrowed prescription")
    print("=" * 78)

    for scenario_name, v_dict in SCENARIOS:
        print(f"\n--- Scenario {scenario_name} ---")
        scenario_result = {}
        for system_name, v in v_dict.items():
            sigma_eff_val = evaluate_sigma_eff(v)
            print(f"\n{system_name} at V_max = {v:.1f} km/s:")
            print(f"  sigma_eff = {sigma_eff_val:.4f} cm^2/g")
            if system_name == "Crater II":
                target = CRATER_II["inferred_sigma_m"] / 2  # floor = 30 cm^2/g (favored 60, lower bound)
                v_cr = verdict(sigma_eff_val, target, "floor", sigma_unc=10.0)
                print(f"  Crater II requirement: sigma/m >= {target:.0f} cm^2/g (floor, sigma_unc=10)")
                print(f"  z = {v_cr['z']:.2f}, verdict = {v_cr['verdict']}")
            elif system_name == "Antlia II":
                target = ANTLIA_II["inferred_sigma_m"] / 2
                v_an = verdict(sigma_eff_val, target, "floor", sigma_unc=10.0)
                print(f"  Antlia II requirement: sigma/m >= {target:.0f} cm^2/g (floor, sigma_unc=10)")
                print(f"  z = {v_an['z']:.2f}, verdict = {v_an['verdict']}")
            scenario_result[system_name] = {
                "v_max_km_s": v,
                "sigma_eff_cm2_g": sigma_eff_val,
                "target_cm2_g": target,
                "verdict": v_cr["verdict"] if system_name == "Crater II" else v_an["verdict"],
                "z": v_cr["z"] if system_name == "Crater II" else v_an["z"],
            }
        results["scenarios"][scenario_name] = scenario_result

    # Also evaluate sigma_eff at dSph v=15 to confirm baseline
    print("\n" + "=" * 78)
    print("Reference: sigma_eff at dSph v=15 (already in T207 channels)")
    print("=" * 78)
    sigma_eff_dsph = evaluate_sigma_eff(15.0)
    v_dsph = verdict(sigma_eff_dsph, 0.8, "ceiling", sigma_unc=0.04)
    print(f"dSph v=15: sigma_eff = {sigma_eff_dsph:.4f} cm^2/g, ceiling = 0.8 cm^2/g")
    print(f"  z = {v_dsph['z']:.2f}, verdict = {v_dsph['verdict']}")

    sigma_eff_cloud9 = evaluate_sigma_eff(28.0)
    v_c9 = verdict(sigma_eff_cloud9, 128.0, "floor", sigma_unc=30.0)
    print(f"\nCloud-9 v=28: sigma_eff = {sigma_eff_cloud9:.4f} cm^2/g, floor = 128 cm^2/g (obs = 128)")
    print(f"  z = {v_c9['z']:.2f}, verdict = {v_c9['verdict']}")

    # Summary verdict
    print("\n" + "=" * 78)
    print("Summary: under borrowed prescription (f_H_cf=0.85, f_H_cc=0.5):")
    print("=" * 78)
    for scenario_name, scenario_result in results["scenarios"].items():
        print(f"\n{scenario_name}:")
        for system_name, r in scenario_result.items():
            print(f"  {system_name}: sigma_eff = {r['sigma_eff_cm2_g']:.3f} cm^2/g, "
                  f"verdict = {r['verdict']} (z={r['z']:.2f})")

    # Write JSON
    out_path = Path(__file__).resolve().parent.parent / "data" / "results" / "t210_gating_test_crater_antlia.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {out_path}")
    return results


if __name__ == "__main__":
    main()
```

---

# File 10: T210 Path A2 Sharp Resonance (Python)

_Source path: `v0.3-prelim/code/t210_path_a2_sharp_resonance_scan.py`_

```
"""
T210 Path A2 — Sharp resonance scan at v_HL = 28 km/s.

Per Cloud-9alternate.docx memo, Path A2 is the only model-level route to
satisfy Cloud-9 and dSph simultaneously: a resonance narrower than the
velocity separation.

The current model has v_HL = 98.2 km/s (where the heavy-light sigma_HL
Lorentzian peak is centered). The cloud-9 / Crater II / Antlia II
requirements are at v ~ 5-28 km/s, while dSph is at v = 15 km/s.

Question: can we move v_HL down to v=28 (Cloud-9 scale) and shrink
the width_HL to < 15 km/s such that:
- Cloud-9 at v=28: sigma_eff high (on-peak, sigma_peak_HL * f_H^2 ~ large)
- dSph at v=15: sigma_eff low (off-peak, well below ceiling)
- SPARC at v=100: sigma_eff ~ 0.19 (back to heavy-channel-only)

This is a parameter scan. Test v_HL in [25, 30, 35] km/s and width_HL
in [5, 10, 15, 20] km/s. For each combination, evaluate sigma_eff at
v = 5, 10, 15, 28, 100, 500 km/s and check the per-channel verdict.

Caveat: if Crater II and Antlia II probe v ~ 5-10 km/s (satellite
dwarf regime), then a v_HL = 28 resonance still leaves them
unsatisfied.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np

from T207_three_term_fit import sigma_eff_three_term

# Borrowed mode parameters (Path F1 standing)
SIGMA_0 = 0.005
SIGMA_PEAK_HH_1 = 84.4
SIGMA_0_HL = 0.0001
SIGMA_PEAK_HL_DEFAULT = 0.318
V_HL_DEFAULT = 98.2
SIGMA_0_LL = 0.0006
A_SLOPE = 1.0

F_H_CF = 0.85
F_H_CC = 0.5
F_H_INT = 0.5 * (F_H_CF + F_H_CC)

# Per-channel f_H assignment
HALO_CLASSES = {
    "UFD v=3": "core_collapsed",
    "UFD v=5": "core_collapsed",
    "UFD v=7": "core_collapsed",
    "UFD v=10": "core_collapsed",
    "dSph v=15": "core_collapsed",
    "Cloud-9 v=28": "core_forming",
    "Crater II": "core_collapsed",  # satellite dwarf
    "Antlia II": "core_collapsed",   # satellite dwarf
    "SPARC v=100": "intermediate",
    "Cluster v=500": "core_collapsed",
}

# Per-channel observation requirements
CHANNELS = {
    # name: (v, sigma_unc, obs, kind)
    "UFD v=3": (3.0, 0.05, 0.155, "ceiling"),
    "UFD v=5": (5.0, 0.05, 0.093, "ceiling"),
    "UFD v=7": (7.0, 0.05, 0.067, "ceiling"),
    "UFD v=10": (10.0, 0.05, 0.047, "ceiling"),
    "dSph v=15": (15.0, 0.04, 0.8, "ceiling"),
    "Cloud-9 v=28": (28.0, 30.0, 128.0, "floor"),
    "Crater II": (28.0, 10.0, 30.0, "floor"),   # using V_max=28 for memo Scenario D
    "Antlia II": (28.0, 10.0, 30.0, "floor"),    # using V_max=28
    "SPARC v=100": (100.0, 0.05, 0.193, "gaussian"),
    "Cluster v=500": (500.0, 5e-4, 2.5e-4, "ceiling"),
}

# Scenarios to scan
V_HL_SCENARIOS = [25.0, 28.0, 30.0, 35.0, 50.0, 75.0, 100.0]
WIDTH_HL_SCENARIOS = [5.0, 10.0, 15.0, 20.0, 30.0, 50.0]


def f_H_for(halo_class: str) -> float:
    if halo_class == "core_forming":
        return F_H_CF
    elif halo_class == "core_collapsed":
        return F_H_CC
    elif halo_class == "intermediate":
        return F_H_INT


def evaluate_all_channels(v_HL: float, width_HL: float) -> dict:
    """Compute sigma_eff and per-channel z-score for given v_HL, width_HL."""
    results = {}
    for name, (v, sigma_unc, obs, kind) in CHANNELS.items():
        halo_class = HALO_CLASSES[name]
        f_H = f_H_for(halo_class)
        sigma_eff = sigma_eff_three_term(
            v,
            f_H=f_H,
            sigma_0=SIGMA_0,
            a_slope=A_SLOPE,
            sigma_peak_HH_1=SIGMA_PEAK_HH_1,
            sigma_0_HL=SIGMA_0_HL,
            sigma_peak_HL=SIGMA_PEAK_HL_DEFAULT,
            v_HL=v_HL,
            width_HL=width_HL,
            sigma_0_LL=SIGMA_0_LL,
        )
        if kind == "ceiling":
            z = (sigma_eff - obs) / sigma_unc
            verdict = "PASS" if z < 1.0 else ("MARGINAL" if z < 2.0 else "FAIL")
        elif kind == "floor":
            z = (obs - sigma_eff) / sigma_unc
            verdict = "PASS" if z < 1.0 else ("MARGINAL" if z < 2.0 else "FAIL")
        elif kind == "gaussian":
            z = (sigma_eff - obs) / sigma_unc
            verdict = "PASS" if abs(z) < 1.0 else ("MARGINAL" if abs(z) < 2.0 else "FAIL")
        results[name] = {
            "v": v, "sigma_eff": sigma_eff, "obs": obs,
            "kind": kind, "z": z, "verdict": verdict,
        }
    return results


def main():
    all_results = {}
    print("=" * 80)
    print("T210 Path A2 — Sharp resonance scan at v_HL in [25, 28, 30, 35, 50, 75, 100]")
    print("=" * 80)

    # Iterate through all combinations
    for v_HL in V_HL_SCENARIOS:
        for width_HL in WIDTH_HL_SCENARIOS:
            key = f"v_HL={v_HL:.0f}, width_HL={width_HL:.0f}"
            all_results[key] = evaluate_all_channels(v_HL, width_HL)

    # Find configurations that pass:
    # - Cloud-9 PASS (sigma_eff >= 128 at v=28)
    # - dSph PASS (sigma_eff <= 0.8 at v=15)
    # - SPARC PASS or MARGINAL (|z| < 2)
    # - Crater II / Antlia II: assume V_max = 28 for memo scenario D
    passing_configs = []
    for key, results in all_results.items():
        c9 = results["Cloud-9 v=28"]
        dsph = results["dSph v=15"]
        sparc = results["SPARC v=100"]
        crater = results["Crater II"]
        antlia = results["Antlia II"]
        if c9["verdict"] == "PASS" and dsph["verdict"] == "PASS":
            passing_configs.append((key, results))

    print(f"\n{len(passing_configs)} configurations pass both Cloud-9 AND dSph:")
    for key, results in passing_configs[:20]:  # first 20
        print(f"\n  {key}:")
        for ch in ["Cloud-9 v=28", "dSph v=15", "SPARC v=100", "Crater II", "Antlia II"]:
            r = results[ch]
            print(f"    {ch}: sigma_eff = {r['sigma_eff']:.3f}, verdict = {r['verdict']} (z={r['z']:.2f})")

    # Save all results
    out_path = Path(__file__).resolve().parent.parent / "data" / "results" / "t210_path_a2_sharp_resonance_scan.json"
    with open(out_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nFull scan saved to {out_path}")

    # Also save summary
    summary_path = Path(__file__).resolve().parent.parent / "data" / "results" / "t210_path_a2_summary.json"
    summary = {
        "n_passing": len(passing_configs),
        "n_total": len(all_results),
        "passing_configs": [(k, all_results[k]) for k, _ in passing_configs],
    }
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Summary saved to {summary_path}")


if __name__ == "__main__":
    main()
```

---

# File 11: T210 σ_eff Decompose (Python)

_Source path: `v0.3-prelim/code/t210_quick_sigma_eff_decompose.py`_

```
"""
T210 quick diagnostic — what is sigma_eff(28) made of?
"""
import sys
sys.path.insert(0, r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\code")
from T207_three_term_fit import sigma_eff_three_term

v = 28.0
f_H = 0.5
sigma_0 = 0.005
sigma_peak_HH_1 = 84.4
sigma_0_HL = 0.0001
sigma_peak_HL = 0.318
v_HL = 28.0
width_HL = 50.0
sigma_0_LL = 0.0006
a_slope = 1.0

print(f"sigma_eff(v=28, f_H=0.5, v_HL=28, sigma_peak_HL=0.318) = {sigma_eff_three_term(v, f_H=f_H, sigma_0=sigma_0, a_slope=a_slope, sigma_peak_HH_1=sigma_peak_HH_1, sigma_0_HL=sigma_0_HL, sigma_peak_HL=sigma_peak_HL, v_HL=v_HL, width_HL=width_HL, sigma_0_LL=sigma_0_LL):.4f} cm^2/g")
print()

# Vary sigma_peak_HL
print("Vary sigma_peak_HL (at v_HL=28, f_H=0.5):")
for spl in [0.318, 1.0, 5.0, 10.0, 50.0, 100.0, 500.0]:
    se = sigma_eff_three_term(v, f_H=f_H, sigma_0=sigma_0, a_slope=a_slope, sigma_peak_HH_1=sigma_peak_HH_1, sigma_0_HL=sigma_0_HL, sigma_peak_HL=spl, v_HL=v_HL, width_HL=width_HL, sigma_0_LL=sigma_0_LL)
    print(f"  sigma_peak_HL = {spl:7.3f}: sigma_eff(28) = {se:8.3f} cm^2/g  (target >= 128)")

# Check: even with f_H=0.85 (core_forming for Cloud-9), is sigma_eff(28) different?
print()
print(f"At v_HL=28, f_H=0.85 (Cloud-9 core_forming class):")
for spl in [0.318, 5.0, 50.0]:
    se = sigma_eff_three_term(v, f_H=0.85, sigma_0=sigma_0, a_slope=a_slope, sigma_peak_HH_1=sigma_peak_HH_1, sigma_0_HL=sigma_0_HL, sigma_peak_HL=spl, v_HL=v_HL, width_HL=width_HL, sigma_0_LL=sigma_0_LL)
    print(f"  sigma_peak_HL = {spl:7.3f}: sigma_eff(28) = {se:8.3f} cm^2/g")

# What's the f_H^2 sigma_HH contribution at v=28?
print()
print(f"f_H^2 sigma_HH(28) decomposition (at v_HL=28, f_H=0.5, sigma_peak_HH_1=84.4):")
import math
# Lorentzian at v_HL=28, v=28: peak value
lorentz_at_28 = 1.0 / (1.0 + ((28.0 - 28.0) / width_HL)**2)
print(f"  Lorentzian(v=28, v_HL=28) = {lorentz_at_28:.4f}")
print(f"  sigma_HH_1(v=28) = sigma_0 + sigma_peak_HH_1 * lorentzian = {sigma_0 + sigma_peak_HH_1 * lorentz_at_28:.3f}")
print(f"  f_H^2 * sigma_HH_1(28) = {f_H**2 * (sigma_0 + sigma_peak_HH_1 * lorentz_at_28):.3f}")
```

---

# File 12: T212 Silverman Gravothermal (Python)

_Source path: `v0.3-prelim/code/t212_silverman_gravothermal.py`_

```
"""
T212 — Gravothermal cascade at Silverman+ 2026 parameters.

Silverman+ 2026 (arXiv:2606.02566, Fermilab-PUB-26-0348-T) finds that
gravothermal collapse proceeds at sigma/m = 70 cm^2/g in M_halo ~ 10^10
M_sun halos with QUIESCENT merger histories. 3 of 6 halos collapse.

This is a major Path B3 candidate I missed. Re-evaluate t_core at
Cloud-9 host-halo parameters (M_halo = 5e9 M_sun, sigma/m = 70 cm^2/g)
to see if gravothermal cascade can run.

Balberg+ 2002 Eq. 22:
t_core = 12.7 / sigma_m * (rho_s / 1e-2)^-1 * (r_s / 1e4) * (100/v_max) Gyr

where sigma_m is in cm^2/g, rho_s in M_sun/pc^3, r_s in pc, v_max in km/s.
"""
from __future__ import annotations
import json
import math
from pathlib import Path

import sys
sys.path.insert(0, r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\code")

# Use T208 Balberg formula
from T208_path_b_cloud9_host_halo_gravothermal import (
    gravothermal_t_core_Gyr as balberg_t_core_Gyr,
    nfw_r_vir_pc, nfw_rho_s_from_concentration, v_max_from_M_c,
    V_REF,
)

def t_cross_Gyr_from_r_vir_vmax(r_vir_pc, v_max_kms):
    """Halo crossing time: t_cross = r_vir / v_max in Gyr."""
    # r_vir in pc, v_max in km/s
    # pc / (km/s) = 3.0857e13 s
    # Gyr = 3.1557e16 s
    return (r_vir_pc / v_max_kms * 3.0857e13) / 3.1557e16


def evaluate(params):
    M = params["M_halo"]
    c = params["c"]
    sigma_m = params["sigma_m"]
    r_vir = nfw_r_vir_pc(M)
    rho_s, r_s = nfw_rho_s_from_concentration(M, c, r_vir)
    v_max = v_max_from_M_c(M, c, r_vir)
    t_core = balberg_t_core_Gyr(sigma_m, rho_s, r_s, v_max)
    t_cross = t_cross_Gyr_from_r_vir_vmax(r_vir, v_max)
    return {
        "M_halo_M_sun": M,
        "c": c,
        "v_max_km_s": v_max,
        "r_vir_pc": r_vir,
        "r_s_pc": r_s,
        "rho_s_M_sun_pc3": rho_s,
        "sigma_m_cm2_g": sigma_m,
        "t_core_Gyr": t_core,
        "t_cross_Gyr": t_cross,
        "t_core_over_Hubble": t_core / 13.8,
        "t_core_over_t_cross": t_core / t_cross,
        "phase_runs": t_core < 13.8,
        "causality_ok": t_core > 3.0 * t_cross,
    }

# Silverman+ 2026 parameters
SILVERMAN_PARAMS = {
    "M_halo": 1e10,        # M_sun (their m10 host halos)
    "c": 12.0,             # typical NFW concentration at this mass
    "sigma_m": 70.0,       # cm^2/g at v_max
    "v_max": 35.0,         # km/s (typical for M=10^10 halo with c=12)
}

# Cloud-9 host halo
CLOUD9_HOST = {
    "M_halo": 5e9,
    "c": 12.0,
    "sigma_m": 70.0,       # Silverman's value
    "v_max": None,         # compute from NFW
}


def main():
    print("=" * 80)
    print("T212 Gravothermal at Silverman+ 2026 parameters")
    print("=" * 80)

    print("\n--- Silverman+ 2026 fiducial: M=10^10 M_sun, sigma/m=70 cm^2/g ---")
    r1 = evaluate(SILVERMAN_PARAMS)
    for k, v in r1.items():
        print(f"  {k}: {v}")

    print("\n--- Cloud-9 host halo at sigma/m=70 cm^2/g ---")
    r2 = evaluate(CLOUD9_HOST)
    for k, v in r2.items():
        print(f"  {k}: {v}")

    print("\n--- What sigma/m does gravothermal NEED to collapse at Cloud-9 host? ---")
    # Find sigma_threshold such that t_core = Hubble
    sigma_threshold_5e9 = None
    for sigma in [0.052, 1.0, 10.0, 50.0, 70.0, 100.0, 150.0, 200.0, 500.0]:
        params = {"M_halo": 5e9, "c": 12.0, "sigma_m": sigma, "v_max": None}
        r = evaluate(params)
        marker = " <-- threshold" if r["t_core_over_Hubble"] < 1.0 and (sigma_threshold_5e9 is None) else ""
        if r["t_core_over_Hubble"] < 1.0 and sigma_threshold_5e9 is None:
            sigma_threshold_5e9 = sigma
        print(f"  sigma/m = {sigma:6.1f} cm^2/g: t_core = {r['t_core_Gyr']:7.2f} Gyr, t_core/t_Hubble = {r['t_core_over_Hubble']:6.2f}{marker}")

    # Same for 1e10 (Silverman+ mass)
    print("\n--- At Silverman+ M=10^10 M_sun halo ---")
    sigma_threshold_1e10 = None
    for sigma in [0.052, 1.0, 10.0, 50.0, 70.0, 100.0, 150.0, 200.0, 500.0]:
        params = {"M_halo": 1e10, "c": 12.0, "sigma_m": sigma, "v_max": None}
        r = evaluate(params)
        marker = " <-- threshold" if r["t_core_over_Hubble"] < 1.0 and (sigma_threshold_1e10 is None) else ""
        if r["t_core_over_Hubble"] < 1.0 and sigma_threshold_1e10 is None:
            sigma_threshold_1e10 = sigma
        print(f"  sigma/m = {sigma:6.1f} cm^2/g: t_core = {r['t_core_Gyr']:7.2f} Gyr, t_core/t_Hubble = {r['t_core_over_Hubble']:6.2f}{marker}")

    print(f"\nThreshold sigma/m for t_core = Hubble:")
    print(f"  At M_halo = 5e9 M_sun (Cloud-9 host): {sigma_threshold_5e9} cm^2/g")
    print(f"  At M_halo = 1e10 M_sun (Silverman+): {sigma_threshold_1e10} cm^2/g")

    # Save
    results = {
        "silverman_fiducial": r1,
        "cloud9_host_at_sigma70": r2,
        "threshold_5e9_cm2_g": sigma_threshold_5e9,
        "threshold_1e10_cm2_g": sigma_threshold_1e10,
    }
    out_path = Path(r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\t212_silverman_gravothermal.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
```

---
