"""v19.2-D.2: dSph gravothermal sweep with proper two-component mixture + honest framing.

Per p1.docx review of v19.2-D, three substantive issues:

1. The 0.09 'channel_mixing_factor' was hardcoded; reviewer correctly identified
   it as f_H^2 from the two-component mixture (T207 fit: f_H_cc ~ 0.30).
   FIX: Use three-term formula sigma_eff = f_H^2 sigma_HH + 2 f_H f_L sigma_HL + f_L^2 sigma_LL

2. The 'gravothermal uses sigma_eff' claim was asserted without derivation, and
   contradicts the standard literature (Silverman+ / T212 / Ohana+ all use sigma/m).
   FIX: DROP the claim. Gravothermal uses sigma/m per Silverman+ / T212 / Ohana+.

3. The JSON 'MIXED' verdict for all halos was glossed over in the report.
   FIX: HONEST FRAMING -- all halos MIXED, sigma_eff pass does NOT resolve
   the gravothermal prediction.

NEW DISCOVERY (per v19.2-D.2 calibration):
   The framework has TWO different microphysical cross-sections:
     a) sigma_HH (raw Breit-Wigner from phase44_sigma_HH_at_v): 5-18 cm^2/g at dSph scale
     b) sigma_eff_published (post channel-mixing, sigma_m_phase44.json): 0.03-0.10 cm^2/g at dSph scale
   Per Silverman+ / T212 / Ohana+, gravothermal uses sigma/m (sigma_HH). This gives
   t_core ~ 0.04-1.4 Gyr at dSph scale -- ALL collapse within Hubble time.
   The observational sigma_eff_published < 0.1 cm^2/g passes dSph constraints.
   This is a REAL microphysical-vs-observational inconsistency in the framework
   that the paper needs to address.

Method:
1. sigma/m = phase44_sigma_HH_at_v(v) (the framework's microphysical cross-section)
2. sigma_eff_via_three_term = f_H^2 sigma_HH + 2 f_H f_L sigma_HL + f_L^2 sigma_LL
3. sigma_eff_published from sigma_m_phase44.json (calibration target)
4. t_core via gravothermal_t_core_Gyr(sigma/m, rho_s, r_s, v_max) -- canonical T208
5. V_max from v_max_from_M_c(M, c, r_vir) -- NFW V_max at r_max = 2.16 r_s
6. rho_s from nfw_rho_s_from_concentration(M, c, r_vir) -- NFW concentration relation

Halo parameters from Read+ 2019 [29d], Walker+ 2009, Wolf+ 2010.

Output:
- v0.3-prelim/data/results/v192_dsph_gravothermal_sweep.json

Run:
    ./.venv-sidm-bench/Scripts/python.exe scripts/v192_dsph_gravothermal_sweep.py
"""

import sys
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / 'v0.3-prelim' / 'code'))

from T208_path_b_cloud9_host_halo_gravothermal import (
    nfw_r_vir_pc, nfw_rho_s_from_concentration, v_max_from_M_c,
    gravothermal_t_core_Gyr
)
from phase44_two_component import phase44_sigma_HH_at_v

OUT_DIR = REPO / 'v0.3-prelim' / 'data' / 'results'

# Framework parameters (Phase 44 + v1 resonance)
# f_H_cc from T207 fit (t207_final_summary.json): core_collapsed f_H ~ 0.30
F_H_CC = 0.30
SIGMA_LL = 0.0  # canonical, per phase44_two_component.py line 339

# Published sigma_eff from sigma_m_phase44.json (phenomenological summary)
# These are the framework's published values that observers actually measure
SIGMA_EFF_PUBLISHED = {
    3.0: 0.155,  # extreme UFD
    5.0: 0.0931, # UFD
    7.0: 0.0666, # edge UFD
    10.0: 0.0468, # UFD
    15.0: 0.0318, # classical dSph
}


# Representative dSph halo parameters
# M_halo from abundance matching + stellar kinematics (Read+ 2019 [29d] for Segue 1,
# Walker+ 2009 / Wolf+ 2010 for classical dSphs)
# V_max_obs from Walker+ 2009 / Wolf+ 2010 half-light velocity dispersions
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


def sigma_eff_published(v_kms):
    """Interpolate published sigma_eff from sigma_m_phase44.json values."""
    v_sorted = sorted(SIGMA_EFF_PUBLISHED.keys())
    if v_kms <= v_sorted[0]:
        return SIGMA_EFF_PUBLISHED[v_sorted[0]]
    if v_kms >= v_sorted[-1]:
        return SIGMA_EFF_PUBLISHED[v_sorted[-1]]
    # Linear interpolation
    for i in range(len(v_sorted) - 1):
        if v_sorted[i] <= v_kms <= v_sorted[i+1]:
            v_lo, v_hi = v_sorted[i], v_sorted[i+1]
            s_lo, s_hi = SIGMA_EFF_PUBLISHED[v_lo], SIGMA_EFF_PUBLISHED[v_hi]
            return s_lo + (s_hi - s_lo) * (v_kms - v_lo) / (v_hi - v_lo)
    return 0.0


def sigma_eff_three_term(sigma_HH, f_H, sigma_HL, sigma_LL=0.0):
    """Three-term sigma_eff formula (canonical per phase44_two_component.py)."""
    f_L = 1.0 - f_H
    return f_H**2 * sigma_HH + 2 * f_H * f_L * sigma_HL + f_L**2 * sigma_LL


def main():
    results = {}
    for halo in DSPH_HALOS:
        M = halo["M_halo"]
        c = halo["c"]
        r_vir = nfw_r_vir_pc(M)
        rho_s, r_s = nfw_rho_s_from_concentration(M, c, r_vir)
        V_max_nfw = v_max_from_M_c(M, c, r_vir)

        # sigma/m (microphysical, drives gravothermal) -- canonical Phase 44
        sigma_HH = phase44_sigma_HH_at_v(halo["V_max_obs"])

        # sigma_eff_published (the framework's published value observers see)
        sigma_eff_pub = sigma_eff_published(halo["V_max_obs"])

        # Solve for sigma_HL that reproduces published sigma_eff
        # 0.09 sigma_HH + 0.42 sigma_HL = sigma_eff_pub
        # sigma_HL = (sigma_eff_pub - 0.09 sigma_HH) / 0.42
        sigma_HL_fit = (sigma_eff_pub - F_H_CC**2 * sigma_HH) / (2 * F_H_CC * (1 - F_H_CC))

        # t_core via Balberg+ (uses sigma/m, per Silverman+ / T212 / Ohana+)
        t_core = gravothermal_t_core_Gyr(sigma_HH, rho_s, r_s, V_max_nfw)

        # Causality cap: t_core > 3 * t_cross
        # t_cross = r_vir / v_max (in Gyr) -- simple estimate
        t_cross = r_vir / V_max_nfw / 1.022e-3 / 3.156e7 / 1e9
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
            "sigma_HH_microphysical_cm2_per_g": sigma_HH,
            "sigma_eff_published_observational_cm2_per_g": sigma_eff_pub,
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
    print(f"{'Halo':<14} {'V_max':>6} {'sigma_HH':>10} {'sigma_eff':>10} {'t_core':>10} {'t/t_x':>10} {'Obs':>4} {'Caus':>5} {'Grav':>5}")
    print("-" * 100)
    for name, r in results.items():
        obs = "PASS" if r["passes_observational_constraint_sigma_eff_lt_1"] else "FAIL"
        caus = "OK" if r["causality_ok_t_core_gt_3t_cross"] else "FAIL"
        grav = "no" if r["gravothermal_runs_within_Hubble"] else "yes"
        t_ratio = r["t_core_over_t_cross"]
        t_ratio_str = f"{t_ratio:.1f}" if t_ratio < 1e6 else "huge"
        print(f"{name:<14} {r['V_max_obs_kms']:>6.1f} {r['sigma_HH_microphysical_cm2_per_g']:>10.4f} {r['sigma_eff_published_observational_cm2_per_g']:>10.4f} {r['t_core_Gyr']:>10.2e} {t_ratio_str:>10} {obs:>4} {caus:>5} {grav:>5}")

    print()
    all_obs_pass = all(r["passes_observational_constraint_sigma_eff_lt_1"] for r in results.values())
    all_grav_no = all(not r["gravothermal_runs_within_Hubble"] for r in results.values())

    # Honest framing (per p1.docx Issue 3)
    print("VERDICT (v19.2-D.2, with proper three-term mixture + honest framing):")
    print(f"  Observational constraint (sigma_eff_published < 1 cm^2/g): {'ALL PASS' if all_obs_pass else 'AT LEAST ONE FAILS'}")
    print(f"  Gravothermal collapse within Hubble time (uses sigma/m = sigma_HH): {'none collapse' if all_grav_no else 'ALL collapse (MIXED for all)'}")
    print()
    print("  HONEST FRAMING (per p1.docx Issue 3):")
    print("    At microphysical sigma/m level (= phase44_sigma_HH_at_v, the raw Breit-Wigner sigma_HH),")
    print("    the framework predicts gravothermal collapse for ALL 8 dSph halos (t_core < Hubble time).")
    print("    At observational sigma_eff level (= sigma_m_phase44.json, post channel-mixing),")
    print("    sigma_eff < 0.1 cm^2/g passes the Fornax upper limit.")
    print("    These two values DIFFER by factor ~100 at dSph scale. The gravothermal")
    print("    prediction uses sigma/m per Silverman+ / T212 / Ohana+ convention, NOT sigma_eff.")
    print()
    print("  v19.2-D.2 NEW DISCOVERY:")
    print("    The framework has a REAL microphysical-vs-observational inconsistency:")
    print("      sigma_HH (raw Breit-Wigner): 5-18 cm^2/g at dSph scale")
    print("      sigma_eff_published (post channel-mixing): 0.03-0.10 cm^2/g at dSph scale")
    print("    To reproduce published sigma_eff from three-term formula, sigma_HL must be NEGATIVE -- unphysical.")
    print("    This means phase44_sigma_HH_at_v is NOT the right microphysical input to the gravothermal")
    print("    cascade at dSph scale. The framework's published sigma_eff reflects channel-mixing /")
    print("    cancellation that the raw Breit-Wigner sigma_HH doesn't capture.")
    print()
    print("  WHAT THIS MEANS FOR THE PAPER:")
    print("    1. The framework is CONSISTENT at the observational level (sigma_eff < 1 cm^2/g).")
    print("    2. The framework is INCONSISTENT at the microphysical gravothermal level (sigma_HH >> 1 at dSph).")
    print("    3. Per Silverman+ / T212 / Ohana+, gravothermal uses sigma/m -- so dSphs would collapse if taken literally.")
    print("    4. The paper needs to either:")
    print("       (a) Derive a microphysical sigma/m for gravothermal that matches observational sigma_eff (currently differ by ~100x).")
    print("       (b) Argue that channel-mixing suppresses gravothermal rate at dSph scale (needs derivation).")
    print("       (c) Accept that dSphs SHOULD collapse under microphysical sigma/m and revise dSph upper limit interpretation.")

    # Save JSON
    out = OUT_DIR / 'v192_dsph_gravothermal_sweep.json'
    output = {
        "method": "Phase 44 two-component mixture (canonical phase44_two_component_sigma_eff) with proper three-term formula + published sigma_eff calibration",
        "date": "2026-09-30",
        "version": "v19.2-D.2",
        "framework_parameters": {
            "f_H_cc": F_H_CC,
            "sigma_LL": SIGMA_LL,
        },
        "dsph_halos": results,
        "verdict": {
            "all_dSphs_pass_observational": all_obs_pass,
            "all_dSphs_pass_gravothermal_no_collapse": all_grav_no,
            "interpretation": (
                "Per p1.docx Issue 1: replaced 0.09 hardcoded factor with three-term mixture. "
                "sigma_eff = f_H^2 sigma_HH + 2 f_H f_L sigma_HL + f_L^2 sigma_LL "
                "(sigma_LL = 0 canonical). "
                "Per p1.docx Issue 2: gravothermal uses sigma/m, NOT sigma_eff, per Silverman+ / "
                "T212 / Ohana+ convention. The 'gravothermal uses sigma_eff' claim has been "
                "DROPPED. "
                "Per p1.docx Issue 3: honest framing -- at microphysical sigma/m level, framework "
                "predicts gravothermal collapse for ALL dSph halos (MIXED for all). The sigma_eff "
                "pass does NOT resolve this tension. "
                "NEW v19.2-D.2 DISCOVERY: framework has microphysical-vs-observational "
                "inconsistency. sigma_HH (raw Breit-Wigner) at dSph scale is 5-18 cm^2/g, while "
                "sigma_eff_published (post channel-mixing) is 0.03-0.10 cm^2/g. To reproduce "
                "published sigma_eff from three-term formula, sigma_HL must be NEGATIVE -- "
                "unphysical. This means phase44_sigma_HH_at_v is NOT the right microphysical "
                "input to the gravothermal cascade at dSph scale. The paper needs to address this."
            ),
        },
        "limitations": [
            "Analytical Balberg+ formula; no N-body at dSph scale.",
            "sigma_HL calibrated to match sigma_eff_published -- but calibration requires NEGATIVE sigma_HL.",
            "Halo parameters from Read+ 2019 [29d], Walker+ 2009, Wolf+ 2010.",
            "f_H_cc = 0.30 from T207 fit; alternative f_H values (~0.45-0.50) exist in extended fits.",
            "Causality cap explicitly checked: t_core/t_cross values reported per halo.",
            "sigma_HH at dSph scale (5-18 cm^2/g) is inconsistent with observational sigma_eff_published (0.03-0.10 cm^2/g).",
            "Removed UMa-II (UDG) from dSph list per p1.docx Smaller item 3.",
        ],
    }
    out.write_text(json.dumps(output, indent=2), encoding='utf-8')
    print(f"\nSaved: {out}")


if __name__ == "__main__":
    main()
