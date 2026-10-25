"""v19.2-D.3: dSph gravothermal sweep — fixed per r20.docx review.

Per r20.docx (2026-09-30) review of v19.2-D.2, two critical bugs:

BUG 1: phase44_sigma_HH_at_v returns ~10x larger sigma/m than the paper's
       convention at dSph velocities. The paper's convention is Gaussian
       (w=4.4 km/s); phase44_sigma_HH_at_v uses Breit-Wigner (gamma_frac=0.184).
       These are DIFFERENT parameterizations.
   FIX: Use the paper's sigma/m convention directly:
        sigma/m(v) = sigma_m_at_v(0.052, 1.93, v) + 174 * exp(-(v-29.4)^2/(2*4.4^2))  # R88(24) fix: 1.0 -> 1.93 (Phase 44 free-fit), 28 -> 29.4 (v_target)

BUG 2: t_cross off by ~10 orders of magnitude. The script divided by
       1.022e-3 * 3.156e7 * 1e9 = 3.23e13 instead of multiplying by ~9.78e-4.
       Consequence: t_cross ~ 1 second, "causality_ok: true" is spurious.
   FIX: Use canonical T212 function t_cross_Gyr_from_r_vir_vmax(r_vir_pc, v_max_kms, c)
        which uses r_s = r_vir/c (correct scale radius where V_max occurs).

Per r20.docx recommendation 1: Run diagnostic comparing functions. Done; see below.
Per r20.docx recommendation 5: Mark "NEW DISCOVERY" as provisional pending diagnostic.
   Result: after fixing the two bugs the gap SHRINKS but does NOT disappear. The
   framework's canonical-Gaussian sigma/m at dSph scale is 2.85-16.87 cm^2/g
   (computed; see `_derived_ranges` in the output JSON) while the published
   sigma_eff band is 0.032-0.093 cm^2/g. With f_H = 0.30 the identity
   sigma_eff = f_H^2 * sigma/m would give 0.256-1.518 cm^2/g -- far ABOVE
   published -- so the fitted sigma_HL is LARGE AND NEGATIVE for every halo
   (-0.53 to -3.39 cm^2/g), and 0 of 8 halos satisfy |sigma_HL| < 0.05 cm^2/g.
   (2026-10-25 correction: the earlier 'near-zero or small positive' and
   'sigma/m ~0.5-2.5 cm^2/g' statements here were hardcoded narrative that
   predated the a_slope 1.0->1.93 propagation of commit 79edeae; they are now
   computed from the results so they cannot drift again.)

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

    # --- computed summary ranges (single source of truth for every narrative string) ---
    _rv = list(results.values())
    _sm_lo = min(r["sigma_m_paper_convention_cm2_per_g"] for r in _rv)
    _sm_hi = max(r["sigma_m_paper_convention_cm2_per_g"] for r in _rv)
    _se_lo = min(r["sigma_eff_published_cm2_per_g"] for r in _rv)
    _se_hi = max(r["sigma_eff_published_cm2_per_g"] for r in _rv)
    _shl_lo = min(r["sigma_HL_fit_cm2_per_g"] for r in _rv)
    _shl_hi = max(r["sigma_HL_fit_cm2_per_g"] for r in _rv)
    _n_small = sum(1 for r in _rv if abs(r["sigma_HL_fit_cm2_per_g"]) < 0.05)

    if not all_grav_no:
        print(f"  Per r20.docx Bug 1 fix: paper convention gives sigma/m ~{_sm_lo:.2f}-{_sm_hi:.2f} cm^2/g at dSph scale")
        print(f"  (vs phase44_sigma_HH_at_v ~5-18 cm^2/g); published sigma_eff is {_se_lo:.3f}-{_se_hi:.3f} cm^2/g,")
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
        "_derived_ranges": {
            "note": "computed from dsph_halos; regenerate the file rather than hand-editing",
            "sigma_m_cm2_per_g": {"min": _sm_lo, "max": _sm_hi},
            "sigma_eff_published_cm2_per_g": {"min": _se_lo, "max": _se_hi},
            "sigma_HL_cm2_per_g": {"min": _shl_lo, "max": _shl_hi},
            "n_halos": len(_rv),
            "n_halos_abs_sigma_HL_below_0.05": _n_small,
        },
        "verdict": {
            "all_dSphs_pass_observational": all_obs_pass,
            "all_dSphs_pass_gravothermal_no_collapse": all_grav_no,
            "all_dSphs_pass_causality": all_caus_ok,
            "interpretation": (
                f"Per r20.docx Bug 1 fix: paper convention (Gaussian w={V1_WIDTH}) gives "
                f"sigma/m ~{_sm_lo:.2f}-{_sm_hi:.2f} cm^2/g at dSph scale "
                f"(not 5-18 cm^2/g from phase44_sigma_HH_at_v), over the {len(_rv)} halos listed. "
                f"Published sigma_eff spans {_se_lo:.3f}-{_se_hi:.3f} cm^2/g. "
                "NOTE: this sigma/m range and the published sigma_eff range are NOT related by "
                f"sigma_eff = f_H^2*sigma/m with f_H = {F_H_CC}: that identity would give "
                f"sigma_eff = {F_H_CC**2*_sm_lo:.3f}-{F_H_CC**2*_sm_hi:.3f} cm^2/g, i.e. "
                f"{F_H_CC**2*_sm_lo/_se_hi:.1f}-{F_H_CC**2*_sm_hi/_se_lo:.1f}x ABOVE the published band. "
                "Reconciling the two therefore requires a NEGATIVE cross-channel term. "
                f"The fitted sigma_HL spans {_shl_lo:+.3f} to {_shl_hi:+.3f} cm^2/g, and "
                f"{_n_small}/{len(_rv)} halos satisfy |sigma_HL| < 0.05 cm^2/g. "
                "Per r20.docx Bug 2 fix: t_cross now uses canonical T212 function (r_s = r_vir/c), giving "
                "physically meaningful values (~0.05-0.5 Gyr). Causality verdict is now meaningful. "
                "Per r20.docx recommendation 5: 'NEW DISCOVERY' marked as PROVISIONAL. "
                "The magnitude of the microphysical-vs-observational gap is LARGE, and is bridged only "
                "by a large negative sigma_HL -- not by a near-zero or small-positive one."
            ),
        },
        "limitations": [
            "Analytical Balberg+ formula; no N-body at dSph scale.",
            "sigma_HL calibrated to match sigma_eff_published; should be fit from SPARC / cluster data.",
            "Halo parameters from Read+ 2019 [29d], Walker+ 2009, Wolf+ 2010.",
            "f_H_cc = 0.30 from T207 fit; alternative f_H values (~0.45-0.50) exist in extended fits.",
            "The halo-mass (M_halo) assumption is fixed per halo from Read+ 2019 / Walker+ 2009 / Wolf+ 2010; the paper's quoted 0.5-2.5 cm^2/g dSph band predated the a_slope 1.0->1.93 propagation and is superseded by sigma_m_paper_convention_cm2_per_g above.",
            "Paper convention uses Gaussian; phase44 uses Breit-Wigner -- two different parameterizations.",
            "Removed UMa-II (UDG) from dSph list per p1.docx Smaller item 3.",
            "NEW DISCOVERY from v19.2-D.2 is now RESOLVED as bugs (per r20.docx review).",
        ],
    }
    out.write_text(json.dumps(output, indent=2), encoding='utf-8')
    print(f"\nSaved: {out}")


if __name__ == "__main__":
    main()
