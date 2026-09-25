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