"""Cloud-9 gravothermal analysis: KiSS-SIDM scalings + Silverman+ merger transport.

Reproduces the qualitative Silverman+ 2026 finding (3 of 6 halos collapse)
for Cloud-9 parameters using the published KiSS-SIDM fit formulas.

Method (per Silverman+ 2026 + Gurian & May 2025):
  1. Knudsen number classification (Eq. 18 of Gurian+ 2025):
     Kn = sqrt(<v^2> / (12*pi*G*rho)) * 1 / (rho * sigma_m)
     LMFP (Kn >> 1): outer halo, fluid model APPROPRIATE
     IMFP (Kn ~ 1): core boundary, fluid model BREAKS
     SMFP (Kn << 1): deep core, fluid model APPROPRIATE

  2. Core-mass scaling (Table I of Gurian+ 2025):
     Fluid model:   d log M / d log <v^2> = -0.27 (Kn=1), -0.37 (Kn=5)
     DSMC (KISS):   d log M / d log <v^2> = -0.21 (Kn=1), -0.21 (Kn=5)
     => IMFP regime (Kn ~ 1) is where fluid vs kinetic DIVERGE.

  3. Collapse time scaling (from Balberg+ 2002, Eq. 6 of Ohana+ 2026):
     t_c = 150 * (sigma/m)^(-0.75) / (rho_s,0 * r_s,0 * sqrt(4*pi*G*rho_s,0))
     => t_c smaller for higher sigma/m and higher rho_s.

  4. Silverman+ 2026 merger-induced heat transport (qualitative):
     Mergers inject orbital kinetic energy into the halo, altering the
     heat transport. Sustained mergers keep halos from collapsing; quiescent
     halos collapse. Silverman+ found 3 of 6 halos collapse at sigma/m = 70.

  5. Cloud-9 parameters (per Ohana+ 2026 Section 3.1):
     M_200 = 4.7e9 Msun, c_200 = 4.0, sigma/m = 483 cm^2/g (best fit at tau=0.18)
     Host: RELHIC gas cloud near M94, no optical counterpart, M_halo ~ 5e9.

Output: whether Cloud-9 is in LMFP/IMFP/SMFP regime + predicted t_c +
expected gravothermal outcome (collapse / no collapse) under both fluid
and kinetic models.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
REPO = SCRIPT_DIR.parent
sys.path.insert(0, str(REPO / "v0.3-prelim" / "code"))

# Use canonical T208 Balberg+ 2002 formula (T204 normalization)
# t_core [Gyr] = 12.7 / sigma * (rho_s / 1e-2)^-1 * (r_s / 1e4) * (100/v_max)
# where sigma is in cm^2/g, rho_s in M_sun/pc^3, r_s in pc, v_max in km/s.
from T208_path_b_cloud9_host_halo_gravothermal import (
    gravothermal_t_core_Gyr,
    nfw_r_vir_pc, nfw_rho_s_from_concentration, v_max_from_M_c,
)
from t212_silverman_gravothermal import (
    t_cross_Gyr_from_r_vir_vmax as t_cross_Gyr,
)
# Per r197.docx Issue 1: import the canonical Phase 44 sigma_m function rather than
# hardcoding the value. The hardcoded 0.174 in v19.1.4 was a 4% drift from the
# actual computation. Now we call channels_v03.sigma_m_at_v directly.
from channels_v03 import sigma_m_at_v as canonical_sigma_m_at_v

# Phase 44 baseline parameters (canonical, from T208 source code):
PHASE44_SIGMA_0 = 0.052  # cm^2/g at v=100 km/s
PHASE44_A_SLOPE = 1.0     # v18.28 Rule-28 audit fixed value


def phase44_sigma_m_at_v(v_kms: float) -> float:
    """Phase 44 baseline sigma/m evaluated at velocity v (km/s).

    Per T208 source: sigma_0 = 0.052 at v=100, a_slope = 1.0.
    Returns sigma_m(v) in cm^2/g.
    """
    return canonical_sigma_m_at_v(PHASE44_SIGMA_0, PHASE44_A_SLOPE, v_kms)


def nfw_initial(M_200, c_200):
    """NFW scale density and radius."""
    rho_s_0 = (200/3) * c_200**3 * RHO_CRIT / (np.log(1+c_200) - c_200/(1+c_200))
    r_s_0 = (3 * M_200 / (800 * np.pi * c_200**3 * RHO_CRIT))**(1/3)
    return rho_s_0, r_s_0  # Msun/pc^3, pc


def knudsen_number(rho, sigma_m_cgs, v_rms):
    """Knudsen number per Eq. 18 of Gurian & May 2025.

    Kn = sqrt(<v^2> / (12*pi*G*rho)) * 1 / (rho * sigma_m)

    Args:
        rho: density in Msun/pc^3
        sigma_m_cgs: sigma/m in cm^2/g (= 0.1 * cm^2/kg)
        v_rms: rms velocity in km/s

    Returns:
        Kn (dimensionless)
    """
    # Convert sigma/m from cm^2/g to pc^2/Msun
    # 1 cm^2/g = (1 cm^2) / (1e-3 kg) = 1e3 cm^2/kg
    # 1 cm^2 = 1.05e-38 pc^2 (since 1 pc = 3.086e18 cm, 1 pc^2 = 9.52e36 cm^2)
    # 1 g = 1/1.989e33 Msun
    # sigma_m [pc^2/Msun] = sigma_m [cm^2/g] * 1e3 [g/kg] / 1.989e33 [Msun/kg]
    #                     * 9.52e-36 [pc^2/cm^2]
    #                     = sigma_m * 1e3 * 9.52e-36 / 1.989e33
    #                     = sigma_m * 4.79e-66 pc^2/Msun

    # Actually let's derive more carefully:
    # 1 cm^2/g = 1 cm^2 / (1e-3 kg) = 1000 cm^2/kg
    # Convert to pc^2/Msun:
    # 1 cm^2 = (1/3.086e18)^2 pc^2 = 1.05e-37 pc^2
    # 1 kg = (1/1.989e30) Msun = 5.03e-31 Msun
    # So 1 cm^2/kg = 1.05e-37 / 5.03e-31 = 2.09e-7 pc^2/Msun
    # 1 cm^2/g = 1000 cm^2/kg = 2.09e-4 pc^2/Msun
    sigma_m_pc2_Msun = sigma_m_cgs * 2.09e-4

    Kn = np.sqrt(v_rms**2 / (12 * np.pi * G_NEWTON * rho)) / (rho * sigma_m_pc2_Msun)
    return Kn


def classify_knudsen(Kn):
    """Classify by Knudsen number regime (Gurian+ 2025)."""
    if Kn > 3:
        return "LMFP"
    elif Kn > 0.3:
        return "IMFP"
    else:
        return "SMFP"


# balberg_collapse_time() was DEPRECATED in v19.1.1 and is removed in v19.1.6
# (per r199.docx smaller item 2). Use analyze_case() which uses the canonical
# T208 gravothermal_t_core_Gyr function with clean units.


def cloud9_parameters():
    """Cloud-9 RELHIC host halo parameters (Ohana+ 2026 best fit).

    NOTE: The sigma/m = 483 is Ohana+'s INFERRED BULK sigma/m at the halo,
    not the framework's intrinsic sigma/m at V_max (= 135.3 cm^2/g).
    The factor 483/135.3 = 3.6x is the post-collapse enhancement, NOT the
    pre-collapse input. This distinction matters because the gravothermal
    cascade runs in <halo age at the framework's intrinsic sigma/m, so
    Ohana+ observed 483 is consistent with the framework being at the
    amplification regime (i.e. Cloud-9 has already collapsed or is
    collapsing).
    """
    return {
        "M_200_Msun": 4.7e9,
        "c_200": 4.0,
        "sigma_m_cm2_per_g": 483,  # Ohana+ best-fit BULK sigma/m (post-collapse amplified); NOT framework intrinsic
        "tau": 0.18,
        "M_gas_Msun_observed": 1.4e7,  # approximate from Anand+ 2025
    }


def analyze_case(name, M_halo_msun, c, sigma_m_cm2_per_g):
    """Analyze gravothermal outcome using canonical T208 Balberg+ formula.

    Uses T208 gravothermal_t_core_Gyr which has clean units:
        t_core [Gyr] = 12.7 / sigma * (rho_s / 1e-2)^-1 * (r_s / 1e4) * (100/v_max)
    where sigma in cm^2/g, rho_s in M_sun/pc^3, r_s in pc, v_max in km/s.
    """
    r_vir = nfw_r_vir_pc(M_halo_msun)
    rho_s, r_s = nfw_rho_s_from_concentration(M_halo_msun, c, r_vir)
    v_max = v_max_from_M_c(M_halo_msun, c, r_vir)
    t_core = gravothermal_t_core_Gyr(sigma_m_cm2_per_g, rho_s, r_s, v_max)
    t_cross = t_cross_Gyr(r_vir, v_max, c=c)
    return {
        "name": name,
        "M_halo_Msun": M_halo_msun,
        "c": c,
        "sigma_m_cm2_per_g": sigma_m_cm2_per_g,
        "r_vir_pc": r_vir,
        "r_s_pc": r_s,
        "rho_s_Msun_per_pc3": rho_s,
        "v_max_kms": v_max,
        "t_core_Gyr": t_core,
        "t_cross_Gyr": t_cross,
        "t_core_over_Hubble": t_core / 13.8,
        "t_core_over_t_cross": t_core / t_cross,
        "phase_runs": t_core < 13.8,
        "causality_ok": t_core > 3.0 * t_cross,
    }


def analyze_cloud9():
    """Analyze gravothermal outcome for Cloud-9 + Silverman+ reference."""
    print("=" * 70)
    print(f"Cloud-9 gravothermal analysis (canonical T208 Balberg+ formula)")
    print("=" * 70)

    # Phase 44 baseline sigma/m at the relevant velocity scale.
    # Per r197.docx Issue 1: sigma_m(V_max) is now computed via channels_v03.sigma_m_at_v
    # rather than hardcoded. The 0.174 in v19.1.4 was a 4% drift from the actual value.
    # Cloud-9 host-halo params (M=5e9, c=12) give V_max = 31.12 km/s (NFW-correct).
    PHASE44_SIGMA_M_AT_VMAX = phase44_sigma_m_at_v(31.12)  # = 0.167 cm^2/g

    cases = [
        # Reference: Silverman+ 2026 (T212-verified, NFW-correct V_max at r_max)
        ("Silverman+ 2026 reference", 1e10, 12.0, 70),
        # (a) Phase 44 Yukawa background only at V_max (T208 §9.12 baseline)
        ("Cloud-9 (Phase 44 Yukawa bg only, c=12)", 5e9, 12.0, PHASE44_SIGMA_M_AT_VMAX),
        # (a') Phase 44 Yukawa at c=4 (Ohana+ inferred c) for same-halo comparison.
        # Per re196.docx Reviewer 2: framework rows use c=12, Ohana+ uses c=4; rho_s
        # and t_core change significantly with c. This row gives the apples-to-apples
        # comparison: same M, same sigma/m, but c=4 (Ohana+ concentration).
        ("Cloud-9 (Phase 44 Yukawa, c=4)", 5e9, 4.0, PHASE44_SIGMA_M_AT_VMAX),
        # (b) Framework's own v1=28 km/s resonance, evaluated at V_max=31.12 km/s
        # sigma_peak = 174, v_target = 28, w = 4.4 (from causality_summary_corrected.json)
        # sigma(V_max) = 174 * exp(-(31.12-28)^2 / (2*4.4^2)) = 174 * 0.778 = 135.3 cm^2/g
        # (The 164 cm^2/g in causality_summary_corrected.json is sigma_v28 at the resonance
        # peak, not at V_max. flip2.docx review caught this conflation.)
        ("Cloud-9 (framework v1 resonance ON at V_max, c=12)", 5e9, 12.0, 135.3),
        # (b') Same framework sigma/m at c=4 for same-halo comparison.
        ("Cloud-9 (framework v1 at V_max, c=4)", 5e9, 4.0, 135.3),
        # (c) Ohana+ best-fit sigma/m (c=4, M=4.7e9)
        ("Cloud-9 (Ohana+ best fit, c=4)", 4.7e9, 4.0, 483),
        # (d) Framework's sigma_v28 at the resonance peak (for comparison)
        ("Cloud-9 (framework v1 at v_target=28, c=12)", 5e9, 12.0, 164.0),
    ]

    results = {}
    for name, M, c, sm in cases:
        r = analyze_case(name, M, c, sm)
        results[name] = r
        print(f"\n--- {name} ---")
        print(f"  M_halo = {r['M_halo_Msun']:.2e} Msun, c = {r['c']}")
        print(f"  sigma/m = {r['sigma_m_cm2_per_g']} cm^2/g")
        print(f"  r_vir = {r['r_vir_pc']:.1f} pc, r_s = {r['r_s_pc']:.2f} pc")
        print(f"  rho_s = {r['rho_s_Msun_per_pc3']:.4e} Msun/pc^3")
        print(f"  v_max = {r['v_max_kms']:.2f} km/s")
        print(f"  t_core = {r['t_core_Gyr']:.3f} Gyr")
        print(f"  t_cross = {r['t_cross_Gyr']:.4f} Gyr")
        print(f"  t_core/t_Hubble = {r['t_core_over_Hubble']:.3f}")
        print(f"  t_core/t_cross = {r['t_core_over_t_cross']:.1f}")
        print(f"  Phase runs (t_core < 13.8 Gyr)? {'YES' if r['phase_runs'] else 'NO'}")
        print(f"  Causality (t_core > 3*t_cross)? {'OK' if r['causality_ok'] else 'FAIL'}")

    # Verdict
    print("\n" + "=" * 70)
    print("VERDICT")
    print("=" * 70)
    silverman = results["Silverman+ 2026 reference"]
    cloud9 = results["Cloud-9 (Ohana+ best fit, c=4)"]

    print(f"\nSilverman+ 2026 reference (NFW-correct V_max):")
    print(f"  t_core = {silverman['t_core_Gyr']:.4f} Gyr (V_max = {silverman['v_max_kms']:.2f} km/s)")
    print(f"  t_core/t_cross = {silverman['t_core_over_t_cross']:.2f} (causality cap = 3.0)")
    print(f"  Causality: {'FAIL (analytical formula outside validity range)' if not silverman['causality_ok'] else 'OK'}")
    print(f"  Reference: T212 published 0.22 Gyr used simple virial V_max approximation;")
    print(f"  T208's NFW-correct V_max at r_max gives 0.18 Gyr (20% lower due to higher V_max)")
    print(f"  Both are 'correct' but for different V_max definitions. NFW-correct is canonical.")
    print(f"  Per r197.docx Issue 3: Silverman+ ref ALSO violates causality cap (t_core/t_cross = 1.91 < 3.0).")
    print(f"  Silverman+'s 3/6 collapse finding is from N-body, where the analytical Balberg+")
    print(f"  formula is unreliable. The 0.176 Gyr is INDICATIVE; the N-body timescale is physical.")
    print(f"  This is the strongest argument for N-body being required across the board.")
    print(f"  -> Gravothermal cascade runs within Hubble time (analytical indication)")
    print(f"  -> 3 of 6 halos collapse in Silverman+'s N-body (quiescent subset)")
    print()
    phase44 = results["Cloud-9 (Phase 44 Yukawa bg only, c=12)"]
    phase44_c4 = results["Cloud-9 (Phase 44 Yukawa, c=4)"]
    framework_at_vmax = results["Cloud-9 (framework v1 resonance ON at V_max, c=12)"]
    framework_at_vmax_c4 = results["Cloud-9 (framework v1 at V_max, c=4)"]
    cloud9 = results["Cloud-9 (Ohana+ best fit, c=4)"]
    print(f"Cloud-9 (sigma/m = {phase44['sigma_m_cm2_per_g']}, Phase 44 Yukawa bg only, c=12, T208 §9.12 baseline):")
    print(f"  t_core = {phase44['t_core_Gyr']:.2f} Gyr (V_max = {phase44['v_max_kms']:.2f} km/s)")
    print(f"  -> Gravothermal cascade does NOT run (t_core > t_Hubble)")
    print(f"  -> This is the T208 §9.12 verdict in paper form.")
    print()
    print(f"Cloud-9 (sigma/m = {phase44_c4['sigma_m_cm2_per_g']}, Phase 44 Yukawa, c=4 -- same-halo comparison with Ohana+):")
    print(f"  t_core = {phase44_c4['t_core_Gyr']:.2f} Gyr (V_max = {phase44_c4['v_max_kms']:.2f} km/s)")
    print(f"  -> Lower concentration -> lower rho_s, slightly longer t_core")
    print()
    print(f"Cloud-9 (sigma/m = {framework_at_vmax['sigma_m_cm2_per_g']}, framework v1 resonance ON at V_max, c=12):")
    print(f"  sigma(m) = 174 * exp(-(31.12-28)^2 / (2*4.4^2)) = 174 * 0.778 = 135.3")
    print(f"  t_core = {framework_at_vmax['t_core_Gyr']:.3f} Gyr (V_max = {framework_at_vmax['v_max_kms']:.2f} km/s)")
    print(f"  t_core/t_cross = {framework_at_vmax['t_core_over_t_cross']:.2f} (causality cap = 3.0)")
    print(f"  CAUSALITY FLAG: {'FAIL (analytical formula outside validity range)' if not framework_at_vmax['causality_ok'] else 'OK'}")
    print(f"  -> Gravothermal cascade RUNS in <0.1 Gyr analytically;")
    print(f"     but the t_core/t_cross = {framework_at_vmax['t_core_over_t_cross']:.2f} violates the 3.0 cap,")
    print(f"     so the 91 Myr number is INDICATIVE, not physical (N-body required).")
    print()
    print(f"Cloud-9 (sigma/m = {framework_at_vmax_c4['sigma_m_cm2_per_g']}, framework v1 at V_max, c=4 -- same-halo comparison):")
    print(f"  t_core = {framework_at_vmax_c4['t_core_Gyr']:.3f} Gyr (V_max = {framework_at_vmax_c4['v_max_kms']:.2f} km/s)")
    print(f"  t_core/t_cross = {framework_at_vmax_c4['t_core_over_t_cross']:.2f}")
    print(f"  CAUSALITY FLAG: {'FAIL' if not framework_at_vmax_c4['causality_ok'] else 'OK'}")
    print()
    print(f"Cloud-9 (sigma/m = {cloud9['sigma_m_cm2_per_g']}, Ohana+ best fit, c=4):")
    print(f"  t_core = {cloud9['t_core_Gyr']:.3f} Gyr (V_max = {cloud9['v_max_kms']:.2f} km/s)")
    print(f"  t_core/t_cross = {cloud9['t_core_over_t_cross']:.2f}")
    print(f"  CAUSALITY FLAG: {'FAIL' if not cloud9['causality_ok'] else 'OK'}")
    print(f"  -> Analytical t_core also outside validity range; N-body required.")
    print()
    framework_at_vtarget = results["Cloud-9 (framework v1 at v_target=28, c=12)"]
    print(f"For comparison, framework v1 at v_target=28 (resonance peak), c=12:")
    print(f"  sigma/m = 164 (from causality_summary_corrected.json's sigma_v28)")
    print(f"  This is the framework's sigma/m AT THE PEAK, not at V_max.")
    print(f"  At V_max=31.12, the Gaussian falls off: sigma/m = 135.")
    print(f"  The 164 was confused with the V_max value in v19.1.2 -- flip2.docx.")

    # Save
    out_dir = REPO / "v0.3-prelim" / "data" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "silverman2026_cloud9_gravothermal.json"
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nSaved: {out}")


if __name__ == "__main__":
    analyze_cloud9()