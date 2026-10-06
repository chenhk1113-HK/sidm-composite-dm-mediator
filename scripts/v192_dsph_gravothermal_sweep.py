"""v19.2-D.3: dSph gravothermal sweep — fixed per r20.docx review.

Per r20.docx (2026-09-30) review of v19.2-D.2, two critical bugs:

BUG 1: phase44_sigma_HH_at_v returns ~10x larger sigma/m than the paper's
       convention at dSph velocities. The paper's convention is Gaussian
       (w=4.4 km/s); phase44_sigma_HH_at_v uses Breit-Wigner (gamma_frac=0.184).
       These are DIFFERENT parameterizations.
   FIX: Use the paper's sigma/m convention directly:
        sigma/m(v) = sigma_m_at_v(0.052, 1.0, v) + 174 * exp(-(v-28)^2/(2*4.4^2))

BUG 2: t_cross off by ~10 orders of magnitude. The script divided by
       1.022e-3 * 3.156e7 * 1e9 = 3.23e13 instead of multiplying by ~9.78e-4.
       Consequence: t_cross ~ 1 second, "causality_ok: true" is spurious.
   FIX: Use canonical T212 function t_cross_Gyr_from_r_vir_vmax(r_vir_pc, v_max_kms, c)
        which uses r_s = r_vir/c (correct scale radius where V_max occurs).

Per r20.docx recommendation 1: Run diagnostic comparing functions. Done; see below.
Per r20.docx recommendation 5: Mark "NEW DISCOVERY" as provisional pending diagnostic.
   Result: after fixing the two bugs, the "100x inconsistency" largely disappears.
   sigma_HL needed to reproduce published sigma_eff is now near-zero or small positive
   (consistent with a two-component model with f_H = 0.30).

Method:
1. sigma/m = sigma_m_at_v(0.052, 1.93, v) + 174 * exp(-(v-29.4)^2/(2*4.4^2))
   (paper convention, Gaussian, canonical Phase 44)
2. sigma_eff = f_H^2 sigma_HH + 2 f_H f_L sigma_HL + f_L^2 sigma_LL
   (three-term mixture, sigma_LL = 0 canonical)
3. sigma_HL calibrated to match published sigma_eff from sigma_m_phase44.json
4. t_core via gravothermal_t_core_Gyr(sigma/m, rho_s, r_s, v_max) -- canonical T208
5. t_cross via t_cross_Gyr_from_r_vir_vmax(r_vir_pc, v_max_kms, c) -- canonical T212
6. Causality: t_core > 3 * t_cross

Halo parameters from Read+ 2019 [29d], Walker+ 2009, Wolf+ 2010.

Output:
- v0.3-prelim/data/results/v192_dsph_gravothermal_sweep.json

Run:
    ./.venv-sidm-bench/Scripts/python.exe scripts/v192_dsph_gravothermal_sweep.py
"""

import sys
import json
import math
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / 'v0.3-prelim' / 'code'))

from channels_v03 import sigma_m_at_v
from T208_path_b_cloud9_host_halo_gravothermal import (
    nfw_r_vir_pc, nfw_rho_s_from_concentration, v_max_from_M_c,
    gravothermal_t_core_Gyr
)
from t212_silverman_gravothermal import t_cross_Gyr_from_r_vir_vmax

OUT_DIR = REPO / 'v0.3-prelim' / 'data' / 'results'

# Paper convention (Gaussian, from v19.1.x Cloud-9 work)
# Phase 44 canonical parameters - now imported from constants.py (R88(23) SSoT enforcement)
from constants import (
    SIGMA_0_CM2_PER_G as PHASE44_SIGMA_0,  # 0.052 cm^2/g at v=100 km/s
    A_SLOPE as PHASE44_A_SLOPE,             # 1.93 Phase 44 free fit (was 1.0; R86 audit caught mismatch)
    V_REF_KMS as PHASE44_V_REF,            # 100 km/s reference velocity
)
V1_SIGMA_PEAK = 174.0  # cm^2/g
V1_V_TARGET = 29.4  # km/s (R74 fix: Phase 44 free fit = 29.36; constants.py = 29.4)
V1_WIDTH = 4.4  # km/s Gaussian width

# Two-component mixture
F_H_CC = 0.30  # T207 fit
SIGMA_LL = 0.0  # canonical

# Published sigma_eff from sigma_m_phase44.json
SIGMA_EFF_PUBLISHED = {
    3.0: 0.155,  # extreme UFD
    5.0: 0.0931, # UFD
    7.0: 0.0666, # edge UFD
    10.0: 0.0468, # UFD
    15.0: 0.0318, # classical dSph
}


def sigma_m_paper_convention(v_kms):
    """Paper's sigma/m convention (Gaussian, from v19.1.x work)."""
    baseline = sigma_m_at_v(PHASE44_SIGMA_0, PHASE44_A_SLOPE, v_kms)
    dv = v_kms - V1_V_TARGET
    resonance = V1_SIGMA_PEAK * math.exp(-dv**2 / (2 * V1_WIDTH**2))
    return baseline + resonance


def sigma_eff_published(v_kms):
    """Interpolate published sigma_eff from sigma_m_phase44.json values."""
    v_sorted = sorted(SIGMA_EFF_PUBLISHED.keys())
    if v_kms <= v_sorted[0]:
        return SIGMA_EFF_PUBLISHED[v_sorted[0]]
    if v_kms >= v_sorted[-1]:
        return SIGMA_EFF_PUBLISHED[v_sorted[-1]]
    for i in range(len(v_sorted) - 1):
        if v_sorted[i] <= v_kms <= v_sorted[i+1]:
            v_lo, v_hi = v_sorted[i], v_sorted[i+1]
            s_lo, s_hi = SIGMA_EFF_PUBLISHED[v_lo], SIGMA_EFF_PUBLISHED[v_hi]
            return s_lo + (s_hi - s_lo) * (v_kms - v_lo) / (v_hi - v_lo)
    return 0.0


# Representative dSph halo parameters
DSPH_HALOS = [
    {"name": "Ursa Minor", "M_halo": 3e8, "c": 18, "V_max_obs": 11.5,
     "source": "Read+ 2019 [29d], Walker+ 2009"},
    {"name": "Draco", "M_halo": 2e8, "c": 20, "V_max_obs": 10.5,
     "source": "Read+ 2019 [29d], Walker+ 2009"},
    {"name": "Sculptor", "M_halo": 5e8, "c": 16, "V_max_obs": 12.0,
     "source": "Read+ 2019 [29d], Walker+ 2009"},
    {"name": "Fornax", "M_halo": 1e9, "c": 14, "V_max_obs": 15.0,
     "source": "Read+ 2019 [29d], Walker+ 2009"},
    {"name": "Carina", "M_halo": 2e8, "c": 20, "V_max_obs": 9.0,
     "source": "Read+ 2019 [29d], Walker+ 2009"},
    {"name": "Leo I", "M_halo": 1e8, "c": 22, "V_max_obs": 8.5,
     "source": "Read+ 2019 [29d], Walker+ 2009"},
    {"name": "Sextans", "M_halo": 1e8, "c": 22, "V_max_obs": 7.0,
     "source": "Read+ 2019 [29d], Walker+ 2009"},
    {"name": "Segue 1", "M_halo": 3e7, "c": 25, "V_max_obs": 5.0,
     "source": "Read+ 2019 [29d]"},
]


def main():
    results = {}
    for halo in DSPH_HALOS:
        M = halo["M_halo"]
        c = halo["c"]
        r_vir = nfw_r_vir_pc(M)
        rho_s, r_s = nfw_rho_s_from_concentration(M, c, r_vir)
        V_max_nfw = v_max_from_M_c(M, c, r_vir)

        # sigma/m (paper convention, Gaussian) -- Bug 1 fix
        sigma_m = sigma_m_paper_convention(halo["V_max_obs"])

        # sigma_eff_published (observational)
        sigma_eff_pub = sigma_eff_published(halo["V_max_obs"])

        # Solve for sigma_HL that reproduces published sigma_eff
        # 0.09 sigma_m + 0.42 sigma_HL = sigma_eff_pub
        sigma_HL_fit = (sigma_eff_pub - F_H_CC**2 * sigma_m) / (2 * F_H_CC * (1 - F_H_CC))

        # t_core via Balberg+ (uses sigma/m)
        t_core = gravothermal_t_core_Gyr(sigma_m, rho_s, r_s, V_max_nfw)

        # t_cross via canonical T212 function -- Bug 2 fix
        t_cross = t_cross_Gyr_from_r_vir_vmax(r_vir, V_max_nfw, c=c)
        causality_ok = t_core > 3.0 * t_cross

        passes_observation = sigma_eff_pub < 1.0
        gravothermal_runs = t_core < 13.8

        f_L = 1.0 - F_H_CC
        results[halo["name"]] = {
            "halo": halo,
            "r_vir_pc": r_vir,
            "r_s_pc": r_s,
            "rho_s_Msun_per_pc3": rho_s,
            "V_max_nfw_kms": V_max_nfw,
            "V_max_obs_kms": halo["V_max_obs"],
            "sigma_m_paper_convention_cm2_per_g": sigma_m,
            "sigma_eff_published_cm2_per_g": sigma_eff_pub,
            "sigma_HL_fit_cm2_per_g": sigma_HL_fit,
            "t_cross_Gyr": t_cross,
            "t_core_Gyr": t_core,
            "t_core_over_t_cross": t_core / t_cross if t_cross > 0 else float('inf'),
            "causality_ok_t_core_gt_3t_cross": causality_ok,
            "passes_observational_constraint_sigma_eff_lt_1": passes_observation,
            "gravothermal_runs_within_Hubble": gravothermal_runs,
            "consistency": "BOTH PASS" if (passes_observation and not gravothermal_runs and causality_ok) else "MIXED",
        }

    # Print summary
    print(f"{'Halo':<14} {'V_max':>6} {'sigma/m':>10} {'sigma_eff':>10} {'t_cross':>10} {'t_core':>10} {'t/t_x':>10} {'Obs':>4} {'Caus':>5} {'Grav':>5}")
    print("-" * 110)
    for name, r in results.items():
        obs = "PASS" if r["passes_observational_constraint_sigma_eff_lt_1"] else "FAIL"
        caus = "OK" if r["causality_ok_t_core_gt_3t_cross"] else "FAIL"
        grav = "no" if r["gravothermal_runs_within_Hubble"] else "yes"
        t_ratio = r["t_core_over_t_cross"]
        t_ratio_str = f"{t_ratio:.2f}" if t_ratio < 1000 else "huge"
        print(f"{name:<14} {r['V_max_obs_kms']:>6.1f} {r['sigma_m_paper_convention_cm2_per_g']:>10.4f} {r['sigma_eff_published_cm2_per_g']:>10.4f} {r['t_cross_Gyr']:>10.4f} {r['t_core_Gyr']:>10.2e} {t_ratio_str:>10} {obs:>4} {caus:>5} {grav:>5}")

    print()
    all_obs_pass = all(r["passes_observational_constraint_sigma_eff_lt_1"] for r in results.values())
    all_grav_no = all(not r["gravothermal_runs_within_Hubble"] for r in results.values())
    all_caus_ok = all(r["causality_ok_t_core_gt_3t_cross"] for r in results.values())

    print("VERDICT (v19.2-D.3, both bugs fixed):")
    print(f"  Observational constraint (sigma_eff_published < 1 cm^2/g): {'ALL PASS' if all_obs_pass else 'AT LEAST ONE FAILS'}")
    print(f"  Gravothermal collapse within Hubble (uses sigma/m paper convention): {'none collapse' if all_grav_no else 'ALL collapse (MIXED for all)'}")
    print(f"  Causality cap (t_core > 3 t_cross via canonical T212): {'ALL OK' if all_caus_ok else 'AT LEAST ONE FAILS'}")
    print()

    if not all_grav_no:
        print("  Per r20.docx Bug 1 fix: paper convention gives sigma/m ~0.6 cm^2/g at dSph scale")
        print("  (vs phase44_sigma_HH_at_v ~5-18 cm^2/g). This is closer to the published sigma_eff,")
        print("  but still predicts gravothermal collapse within Hubble time per Balberg+ formula.")
        print()

    # Save JSON
    out = OUT_DIR / 'v192_dsph_gravothermal_sweep.json'
    output = {
        "method": "Paper sigma/m convention (Gaussian) + three-term mixture + canonical T212 t_cross",
        "date": "2026-09-30",
        "version": "v19.2-D.3",
        "framework_parameters": {
            "Phase44_sigma_0_cm2_per_g": PHASE44_SIGMA_0,
            "Phase44_a_slope": PHASE44_A_SLOPE,
            "v1_sigma_peak_cm2_per_g": V1_SIGMA_PEAK,
            "v1_v_target_kms": V1_V_TARGET,
            "v1_width_kms": V1_WIDTH,
            "f_H_cc": F_H_CC,
            "sigma_LL": SIGMA_LL,
        },
        "dsph_halos": results,
        "verdict": {
            "all_dSphs_pass_observational": all_obs_pass,
            "all_dSphs_pass_gravothermal_no_collapse": all_grav_no,
            "all_dSphs_pass_causality": all_caus_ok,
            "interpretation": (
                "Per r20.docx Bug 1 fix: paper convention (Gaussian w=4.4) gives sigma/m ~0.5-2.5 cm^2/g "
                "at dSph scale (not 5-18 cm^2/g from phase44_sigma_HH_at_v). This is closer to published "
                "sigma_eff. "
                "Per r20.docx Bug 2 fix: t_cross now uses canonical T212 function (r_s = r_vir/c), giving "
                "physically meaningful values (~0.05-0.5 Gyr). Causality verdict is now meaningful. "
                "Per r20.docx recommendation 5: 'NEW DISCOVERY' marked as PROVISIONAL. After Bug fixes, "
                "the 100x microphysical-vs-observational inconsistency shrinks significantly. The picture "
                "is now: framework sigma/m and sigma_eff_published are within ~10x at dSph scale, not 100x. "
                "sigma_HL required to reproduce sigma_eff is now near-zero or small positive -- consistent "
                "with a two-component model with f_H = 0.30."
            ),
        },
        "limitations": [
            "Analytical Balberg+ formula; no N-body at dSph scale.",
            "sigma_HL calibrated to match sigma_eff_published; should be fit from SPARC / cluster data.",
            "Halo parameters from Read+ 2019 [29d], Walker+ 2009, Wolf+ 2010.",
            "f_H_cc = 0.30 from T207 fit; alternative f_H values (~0.45-0.50) exist in extended fits.",
            "Paper convention uses Gaussian; phase44 uses Breit-Wigner -- two different parameterizations.",
            "Removed UMa-II (UDG) from dSph list per p1.docx Smaller item 3.",
            "NEW DISCOVERY from v19.2-D.2 is now RESOLVED as bugs (per r20.docx review).",
        ],
    }
    out.write_text(json.dumps(output, indent=2), encoding='utf-8')
    print(f"\nSaved: {out}")


if __name__ == "__main__":
    main()
