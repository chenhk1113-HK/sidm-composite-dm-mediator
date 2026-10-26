# SIDM v19.2-F — Round 5 Changed Code Companion (v1.4, 2026-10-26)

**Companion to:** `SIDM_ROUND5_CONSOLIDATED_FIXES_v1.6_2026-10-26.md`

**Supersedes v1.3 (2026-10-26).** v1.3's text is carried forward unchanged except for: the
companion pointer above, the new §6.2 Phase 3 code (per the n19 review's item 3), and the new
§7 covering the PDF-render defect fixes (per the n19 review's item 6).

**Supersedes v1.2 (2026-10-26).** v1.2 documented `scripts/fix_direct.py`, a non-reproducible
fixer from a withdrawn markup attempt. That file no longer exists; see §6.

**Branch:** `wip/v19.2-F-init`  **Commits:** `7cc8d8a` (fixes), `dd33606`, `ff16eb0` (report),
`c362658` (T132 test re-point), plus the n18 review-response commit (see §5)

**v1.4 (2026-10-26) — n19 review response.** The n19 external review (Chinese-language, 181
paragraphs, all pages of the v1.5 PDF pair read) raised 7 action items. Four produced a change
to this deliverable: the **Phase 3 implementation is now shown** (§6.2, item 3) so it can be
verified rather than taken on trust; the **PDF builder's three silent content-loss defects are
fixed and documented** (§7, item 6); the report now carries a **finding-number namespace
table** and a **tracked coverage-gap register** (report §17.3–17.4, items 1 and 4); and the
**reviewer transport section** gains a cross-platform note (report §14.6, item 7). Full
adjudication — including the one item that is a misread and the reviewer's own wrong formula —
is in report §17.

---

## v1.1 — n18.docx review response (2026-10-25)

The n18 external review raised three priority items against the v1.0 pair. All three are
**verified and fixed**; two provenance claims in the review were **corrected** (details and
the full adjudication table are in the consolidated report v1.1, §5):

| n18 item | Verdict | Action |
|---|---|---|
| Paper: `"halos is"` word order | **VALID** — introduced by Round 5 (`7cc8d8a`) | F1, fixed |
| Paper: `"cm²/g.,"` doubled punctuation | **VALID** — introduced by Round 5 (`7cc8d8a`) | F2, fixed |
| Paper: `"and 4 baseline"` lost subject | **VALID defect**, but **provenance corrected** — pre-dates Round 5 (introduced `799f4ef`) | F4, fixed |
| Generator docstring `"1.589"` vs computed `"1.518"` | **VALID**, and **not** a rounding difference (implies σ/m = 17.66 vs the canonical 16.87, a 4.7% error) | F5, fixed + regression test |
| Companion embeds 241 lines of unchanged JSON | **VALID** — the block is byte-identical to the live file | F6, replaced with a real diff |
| Diff readability (low) | **VALID** | F7, wrapped |

**Two structural changes to this document (v1.0 -> v1.1):**

1. **§3 now shows a DIFF, not the full file.** v1.0 embedded all 241 lines of
   `v192_dsph_gravothermal_sweep.json`, of which only 20 lines differed (+19/−1) in Round 5 — the
   change was buried inside 220 unchanged lines, which defeats the purpose of a
   *changed-code* companion. v1.1 shows the actual `git diff` (pre-Round-5 -> current).
   The live file remains the authority: `v0.3-prelim/data/results/v192_dsph_gravothermal_sweep.json`.

2. **§2's diff is hard-wrapped.** v1.0's diff fence contained single lines up to **3 581
   characters**, which is unreadable in a code fence. Lines are now wrapped at 108 columns.
   A `\` at the start of a line marks a **continuation** of the previous line; joining a
   continuation onto its parent reconstructs the original diff **byte-for-byte**
   (verified: 83/83 lines exact). The `+/-`/`@@` markers are preserved on every
   first-line-of-a-diff-entry, so the diff remains applicable with `git apply` after
   unwrapping.


## TL;DR

The substantive change of this round is **numerical-provenance hygiene**: four of the six
review findings traced to a single root cause — commit `79edeae` propagated `a_slope` 1.0 -> 1.93
into the *numbers* but left the *narrative strings* in the generator
`scripts/v192_dsph_gravothermal_sweep.py` stale, and the paper then quoted those stale strings
verbatim ("sigma/m ~ 0.5-2.5 cm^2/g", "|sigma_HL| < 0.05 for 7 of 8 halos").

The generator's narrative is now **computed from its own results**, so it cannot drift again, and
the paper quotes the regenerated JSON. The JSON's per-halo `dsph_halos` data is **byte-identical**
before and after — only `verdict` and `limitations` changed.

## TOC

| # | file | description |
|---|---|---|

| 1 | `scripts/v192_dsph_gravothermal_sweep.py` | dSph gravothermal sweep generator — narrative strings now COMPUTED (root-cause fix) |
| 2 | `v0.3-prelim/docs/PAPER_V1_DRAFT.md` | Paper v1 draft — 6 verified numerical/prose fixes (§1-§6 of the report)  *(diff hunks only — full file is 2383 lines)* |
| 3 | `v0.3-prelim/data/results/v192_dsph_gravothermal_sweep.json` | Regenerated sweep JSON — **shown as a DIFF in v1.1** (39 changed lines of 241); new `_derived_ranges` block, `verdict.interpretation` rewritten, `limitations` +1 |
| 4 | `docs/LOCAL_REVIEW_R5.md` | Local review (Strata) — all 6 findings annotated with audit verdicts |

---


## 1. `scripts/v192_dsph_gravothermal_sweep.py`

dSph gravothermal sweep generator — narrative strings now COMPUTED (root-cause fix)


**287 lines, 14,494 bytes**


```python
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

```


## 2. `v0.3-prelim/docs/PAPER_V1_DRAFT.md`

Paper v1 draft — 6 verified numerical/prose fixes (§1-§6 of the report)


**Changed paper lines:** 40, 102, 120, 129, 151, 195, 939, 2136, 2193


```diff
--- a/v0.3-prelim/docs/PAPER_V1_DRAFT.md
+++ b/v0.3-prelim/docs/PAPER_V1_DRAFT.md
@@ -37,7 +37,7 @@ ## 1. Introduction
 
 Velocity-dependent SIDM models resolve this tension by reducing σ/m at high velocities through one of 
\several mechanisms: Yukawa suppression (Feng, Kaplinghat & Yu 2009 [5]; Tulin, Yu & Zurek 2013 [6]), 
\threshold resonances (Chu, Hambye & Tytgat 2018 [7]; Duerr et al. 2021 [8]), or geometric mass-ladder 
\constructions (Hong, Kuranchi & Perez 2020 [9]; Girmohanta & Yasuoka 2025 [10]). This paper tests a 
\velocity-dependent framework against Cloud-9 (a starless gas cloud discovered by Zhou+ 2023 [15a] with σ/m ≥ 
\50 cm²/g is Elbert+ 2015's largest simulated cross-section for v_rms ~ 40 km/s [55a], adopted as a working 
\benchmark (BLN24 [15b] constrains Cloud-9's mass/structure, not σ/m)), dwarf galaxies, UFDs, SPARC, and 
\clusters.
 
-**Main result.** The framework's σ_peak = 174 cm²/g at v_target = 29.4 km/s (Phase 44 free fit) is 
\**consistent with Cloud-9** at the 0.16 dex scatter convention (matching Ohana+ 2026's 3.2σ SIDM tension 
\within 0.04σ) but is **in severe tension with Horigome+ 2025 preference thresholds** [27] 
\(arXiv:2503.13650): the framework's σ/m(v) exceeds Horigome+ 2025 preference thresholds by 3.6–23.7× at 
\v_eff = 5–20 km/s using their w = 10 km/s velocity-dependent limit (0.8 cm²/g) and by 27–49× at v = 9–40 
\km/s (excluding v=28 where σ/m is resonantly 830×) against their decisive CDM-preference threshold (0.2 
\cm²/g, Abstract); at v = 28 km/s (Cloud-9 anchor) σ/m = 166 cm²/g, 830× above the velocity-independent 
\threshold. **Caveat:** the 0.2 cm²/g decisive threshold is a velocity-INDEPENDENT quantity while the 
\framework's σ/m(v) is strongly velocity-dependent, so these factors are an UPPER BOUND on the true tension; 
\a definitive comparison requires re-running Horigome+'s SASHIMI likelihood with our σ(v,θ) form (§3.6). The 
\exclusion is robust to the resonance width σ_1; the background Yukawa tail (a_slope = 1.93, the Phase 44 
\free-fit value) alone exceeds the threshold. The comparison is approximate (Horigome's bound assumes a 
\different σ(v,θ) form); a definitive exclusion (deferred to dedicated SASHIMI likelihood) requires 
\re-running their SASHIMI likelihood with our σ(v,θ) form.
+**Main result.** The framework's σ_peak = 174 cm²/g at v_target = 29.4 km/s (Phase 44 free fit) is 
\**consistent with Cloud-9** at the 0.16 dex scatter convention (matching Ohana+ 2026's 3.2σ SIDM tension 
\within 0.04σ) but is **in severe tension with Horigome+ 2025 preference thresholds** [27] 
\(arXiv:2503.13650): the framework's σ/m(v) exceeds Horigome+ 2025 preference thresholds by 3.6–23.7× at 
\v_eff = 5–20 km/s using their w = 10 km/s velocity-dependent limit (0.8 cm²/g) and by 27–49× at v = 9–40 
\km/s — the v = 9 (Sculptor, 5.43 cm²/g) and v = 40 (Cluster LMC, 9.86 cm²/g) endpoint values against their 
\decisive CDM-preference threshold (0.2 cm²/g, Abstract), excluding v = 28 where σ/m is resonantly 830×. The 
\minimum over this window is 14× at v = 15 (2.85 cm²/g), and v = 10 and v = 18 give 22× and 37×; the 27–49× 
\pair is therefore the window's endpoints, not its min–max; at v = 28 km/s (Cloud-9 anchor) σ/m = 166 cm²/g, 
\830× above the velocity-independent threshold. **Caveat:** the 0.2 cm²/g decisive threshold is a 
\velocity-INDEPENDENT quantity while the framework's σ/m(v) is strongly velocity-dependent, so these factors 
\are an UPPER BOUND on the true tension; a definitive comparison requires re-running Horigome+'s SASHIMI 
\likelihood with our σ(v,θ) form (§3.6). The exclusion is robust to the resonance width σ_1; the background 
\Yukawa tail (a_slope = 1.93, the Phase 44 free-fit value) alone exceeds the threshold. The comparison is 
\approximate (Horigome's bound assumes a different σ(v,θ) form); a definitive exclusion (deferred to 
\dedicated SASHIMI likelihood) requires re-running their SASHIMI likelihood with our σ(v,θ) form.
 
 **Hierarchy constraint.** For LZ direct-detection compliance (conditional: if σ_SI were tuned to the LZ 
\bound), the framework requires a dark-sector hierarchy g_N/g_χ ≲ 1.7×10⁻¹³ (actual value, paper rounds to 
\10⁻¹³ for order-of-magnitude bound) (anchored at v = 28, σ/m = 166 cm²/g). The derived dark fine-structure 
\constant is α_χ ≈ 6.8×10⁻⁷. This is a post-diction, not a prediction: σ_peak was fixed first (causality 
\cap), then the hierarchy was derived.
 
@@ -99,7 +99,7 @@ ### 2.5 σ/m vs σ_eff: microphysical and observational cross-sections
 
  σ_eff(v) = f_H² σ_HH(v) + 2 f_H f_L σ_HL(v) + f_L² σ_LL(v)
 
-with f_H the heavy-fraction at the observation radius (f_H_cc ≈ 0.30 from T207 fit for core-collapsed dSphs; 
\the canonical single-component value is f_H = 0.297 per constants.py — 0.30 is a rounded stand-in, a 2% 
\shift in f_H²·σ/m), σ_HH the heavy-heavy cross-section (≡ σ/m above), σ_HL the cross-channel cross-section 
\(free parameter), and σ_LL the light-light cross-section (set to 0 canonical).**Per v19.2-D.3 calibration, 
\the required σ_HL to reproduce published σ_eff from this formula is given per halo in 
\`v0.3-prelim/data/results/v192_dsph_gravothermal_sweep.json`. For 7 of 8 halos, |σ_HL| < 0.05 cm²/g (small, 
\consistent with two-component model with f_H ≈ 0.30).**Fornax is the outlier:**σ_HL = -0.473 cm²/g, 
\indicating an**internal inconsistency between the framework's two curves at V_max = 15 km/s**. The 
\framework's σ/m(v) curve (paper convention, calibrated against v₁ resonance peak) and σ_eff(v) curve 
\(calibrated against channel coverage) are calibrated**independently**— the three-term mixture with f_H = 
\0.30 doesn't relate them at v=15. With σ_HL = 0, the minimum σ_eff = f_H² × σ/m = 0.09 × 2.85 = 0.257 cm²/g, 
\which is 8.0× above the framework's own published σ_eff(Fornax) = 0.032 cm²/g.**The framework still passes 
\the Fornax observational bound (σ_eff = 0.032 < 1 cm²/g) — the inconsistency is internal to the framework's 
\parameterizations, not between the framework and observations.**The root cause: the v₁ resonance Gaussian 
\width (w=4.4 km/s) is wide enough that its tail reaches dSph velocities, contributing ≳ 2 cm²/g to σ/m at 
\v=15; the f_H² = 0.09 suppression is insufficient to bring σ_eff down to the published value without 
\unphysical negative σ_HL. The earlier v19.2-D.2 "100× inconsistency" was a code bug (using 
\`phase44_sigma_HH_at_v` which uses Breit-Wigner instead of the paper's Gaussian convention, plus a unit 
\conversion error in t_cross), not this Fornax-specific internal inconsistency — which is a real constraint 
\on the framework.**Note.** The claim "gravothermal uses σ_eff at dSph scale" has been DROPPED.It is not in 
\the standard literature (Silverman+, Balberg+, Ohana+ all use σ/m) and was asserted without derivation. The 
\convention going forward is:
+with f_H the heavy-fraction at the observation radius (f_H_cc ≈ 0.30 from T207 fit for core-collapsed dSphs; 
\the canonical single-component value is f_H = 0.297 per constants.py — 0.30 is a rounded stand-in, a 2% 
\shift in f_H²·σ/m), σ_HH the heavy-heavy cross-section (≡ σ/m above), σ_HL the cross-channel cross-section 
\(free parameter), and σ_LL the light-light cross-section (set to 0 canonical).**Per v19.2-D.3 calibration, 
\the required σ_HL to reproduce published σ_eff from this formula is given per halo in 
\`v0.3-prelim/data/results/v192_dsph_gravothermal_sweep.json`. For **0 of 8** halos, |σ_HL| < 0.05 cm²/g: 
\after the a_slope = 1.93 propagation the fitted cross-channel term is negative and LARGE for every halo 
\(σ_HL = −0.53 cm²/g (Fornax, the smallest magnitude) to −3.39 cm²/g (Segue 1), per 
\`v192_dsph_gravothermal_sweep.json`). **Fornax is the least discrepant case**, not an isolated outlier: σ_HL 
\= −0.534 cm²/g, indicating an **internal inconsistency between the framework's two curves at V_max = 15 
\km/s**. The framework's σ/m(v) curve (paper convention, calibrated against v₁ resonance peak) and σ_eff(v) 
\curve (calibrated against channel coverage) are calibrated**independently**— the three-term mixture with f_H 
\= 0.30 doesn't relate them at v=15. With σ_HL = 0, the minimum σ_eff = f_H² × σ/m = 0.09 × 2.85 = 0.257 
\cm²/g, which is 8.0× above the framework's own published σ_eff(Fornax) = 0.032 cm²/g.**The framework still 
\passes the Fornax observational bound (σ_eff = 0.032 < 1 cm²/g) — the inconsistency is internal to the 
\framework's parameterizations, not between the framework and observations.**The root cause: the v₁ resonance 
\Gaussian width (w=4.4 km/s) is wide enough that its tail reaches dSph velocities, contributing ≳ 2 cm²/g to 
\σ/m at v=15; the f_H² = 0.09 suppression is insufficient to bring σ_eff down to the published value without 
\unphysical negative σ_HL. The earlier v19.2-D.2 "100× inconsistency" was a code bug (using 
\`phase44_sigma_HH_at_v` which uses Breit-Wigner instead of the paper's Gaussian convention, plus a unit 
\conversion error in t_cross), not this Fornax-specific internal inconsistency — which is a real constraint 
\on the framework.**Note.** The claim "gravothermal uses σ_eff at dSph scale" has been DROPPED.It is not in 
\the standard literature (Silverman+, Balberg+, Ohana+ all use σ/m) and was asserted without derivation. The 
\convention going forward is:
 
 - σ/m (microphysical, paper's Gaussian convention) drives gravothermal, per Silverman+ / T212 / Ohana+.
 - σ_eff is the observational constraint (Fornax upper limit).
@@ -117,7 +117,7 @@ ### 2.5 σ/m vs σ_eff: microphysical and observational cross-sections
 | v ≈ 100 km/s (SPARC) | 0.052 cm²/g | ≈ σ/m (nodes dominate) | rotation curves |
 | v ≈ 500 km/s (cluster) | ≪ 1 cm²/g | ≈ σ/m | cluster lensing |
 
-The gravothermal cascade at Cloud-9 (v ≈ 28 km/s) is driven by σ/m ≈ σ_eff ≈ 174 cm²/g (resonance peak, no 
\channel suppression — t_core = 76 Myr at c=12 / 4.97 Gyr at c=4, see §9.12).**Note (R88(30) corrected):** 
\The 3.98 Gyr value at c=4 was based on the legacy σ/m(V_max=25.59) = 150.0 cm²/g (a_slope=1.0 form). With 
\the canonical Gaussian σ/m(v) at a_slope=1.93, σ/m(V_max=25.59) = 120.32 cm²/g and t_core = 4.97 Gyr (see 
\§2.6 and §9.12).At dSph scale (v < 15 km/s), σ/m ~ 0.5–2.5 cm²/g and σ_eff ~ 0.03–0.10 cm²/g — captured by 
\three-term mixture with σ_HL typically small (|σ_HL| < 0.05 cm²/g for 7 of 8 halos).**Fornax (V_max = 15 
\km/s) is the outlier, with σ_HL = -0.47 cm²/g (required to fit published σ_eff).**This is an internal 
\inconsistency between the framework's σ/m(v) and σ_eff(v) curves .**The gravothermal prediction is the 
\strongest constraint on the framework from dSph data:**at microphysical σ/m = 2.85–18 cm²/g across the 8 
\representative dSph/UFD halos (σ/m(v) evaluated at each halo's V_max), t_core = 0.25–2.08 Gyr (well below 
\Hubble time of 13.8 Gyr) for all 8 halos. The precise per-halo range should be regenerated from 
\v192_dsph_gravothermal_sweep.py; the values here are bounded by the V_max = 20 and V_max = 15 cases in the 
\table above. : σ/m(Fornax V_max=15, v_target=29.4) = 2.85 cm²/g (canonical Gaussian), Balberg+ t_core 
\=**2.08 Gyr**with canonical Fornax halo ρ_s ~ 0.02 M☉/pc³ and r_s ~ 1.4 kpc. The paper's V_max = 15 km/s 
\value is**chosen as a conservative lower bound**(the framework's σ/m(v) decreases with decreasing v; lower v 
\→ lower σ/m → higher t_core → reduced contradiction).**This is a real framework tension:**t_core ~ 2 Gyr is 
\a fifth of the cosmic age at dSph formation (~ 10 Gyr at z=2), predicting collapse where none is observed. 
\The framework predicts collapse for Fornax-like halos in**t_core = 0.25–2.08 Gyr**, depending on the choice 
\of V_max and ρ_s.**Canonical Fornax parameters**(V_max = 18 km/s per Mateo+ 1998 [26a] stellar velocity 
\dispersion σ_w = 11.6 km/s → V_max ≈ 2σ_w = 23 km/s per Wolf+ 2010; per 's correction, V_max = 18 km/s is 
\canonical) give σ/m(Fornax) = 7.49 cm²/g,**t_core ≈ 0.66 Gyr**(factor 3.2× more collapse-prone than the 
\V_max=15 headline). this is the**representative**result, not the headline V_max = 15 km/s which is the most 
\generous self-assessment.**Since Fornax is observed to have a diffuse DM core (M_c ~ 10⁷ M☉, r_c ~ 1 kpc per 
\Walker+ 2009 / Read+ 2019 / Hayashi+ 2020 kinematic decomposition, NOT stellar core per Mateo+ 1998; 
\Peñarrubia+ 2008 gives a dynamical mass profile), the framework's prediction of collapse in <1 Gyr is a real 
\tension.**The dSph tension has three possible outcomes:
+The gravothermal cascade at Cloud-9 (v ≈ 28 km/s) is driven by σ/m ≈ σ_eff ≈ 174 cm²/g (resonance peak, no 
\channel suppression — t_core = 76 Myr at c=12 / 4.97 Gyr at c=4, see §9.12).**Note (R88(30) corrected):** 
\The 3.98 Gyr value at c=4 was based on the legacy σ/m(V_max=25.59) = 150.0 cm²/g (a_slope=1.0 form). With 
\the canonical Gaussian σ/m(v) at a_slope=1.93, σ/m(V_max=25.59) = 120.32 cm²/g and t_core = 4.97 Gyr (see 
\§2.6 and §9.12).At dSph scale (v < 15 km/s), the framework's canonical-Gaussian σ/m is **2.85–16.9 cm²/g** 
\(Fornax at V_max = 15 km/s to Segue 1 at V_max = 5 km/s; `v192_dsph_gravothermal_sweep.json`) — **not** the 
\0.5–2.5 cm²/g band quoted in earlier drafts, which predated the a_slope = 1.93 propagation (R88 full 
\pre-submission). The published observational σ_eff band is **0.032–0.093 cm²/g**. These two are NOT related 
\by σ_eff = f_H²·σ/m at the sweep's f_H = 0.30 (T207, core-collapsed dSph; rounded from the canonical 
\single-component f_H = 0.297 of `constants.py`): that identity would give σ_eff = 0.256–1.518 cm²/g, i.e. 
\**2.8–47.7× ABOVE** the published band, so the two-component mixture requires a NEGATIVE cross-channel term 
\(σ_HL = −0.53 to −3.39 cm²/g) to reconcile them — and |σ_HL| < 0.05 cm²/g holds for **0 of 8** halos, not 7 
\of 8. The F. H. assumption is explicit: the three-term mixture is σ_eff = f_H²σ_HH + 2f_Hf_Lσ_HL + f_L²σ_LL 
\with f_H = 0.30 (T207), σ_LL = 0, and σ_HL is a FREE parameter fitted to the published σ_eff, not derived 
\from the framework.**Fornax (V_max = 15 km/s) is the outlier, with σ_HL = -0.47 cm²/g (required to fit 
\published σ_eff).**This is an internal inconsistency between the framework's σ/m(v) and σ_eff(v) curves 
\.**The gravothermal prediction is the strongest constraint on the framework from dSph data:**at 
\microphysical σ/m = 2.85–18 cm²/g across the 8 representative dSph/UFD halos (σ/m(v) evaluated at each 
\halo's V_max), t_core = 0.25–2.08 Gyr (well below Hubble time of 13.8 Gyr) for all 8 halos. The precise 
\per-halo range should be regenerated from v192_dsph_gravothermal_sweep.py; the values here are bounded by 
\the V_max = 20 and V_max = 15 cases in the table above. : σ/m(Fornax V_max=15, v_target=29.4) = 2.85 cm²/g 
\(canonical Gaussian), Balberg+ t_core =**2.08 Gyr**with canonical Fornax halo ρ_s ~ 0.02 M☉/pc³ and r_s ~ 
\1.4 kpc. The paper's V_max = 15 km/s value is**chosen as a conservative lower bound**(the framework's σ/m(v) 
\decreases with decreasing v; lower v → lower σ/m → higher t_core → reduced contradiction).**This is a real 
\framework tension:**t_core ~ 2 Gyr is a fifth of the cosmic age at dSph formation (~ 10 Gyr at z=2), 
\predicting collapse where none is observed. The framework predicts collapse for Fornax-like halos in**t_core 
\= 0.25–2.08 Gyr**, depending on the choice of V_max and ρ_s.**Canonical Fornax parameters**(V_max = 18 km/s 
\per Mateo+ 1998 [26a] stellar velocity dispersion σ_w = 11.6 km/s → V_max ≈ 2σ_w = 23 km/s per Wolf+ 2010; 
\per 's correction, V_max = 18 km/s is canonical) give σ/m(Fornax) = 7.49 cm²/g,**t_core ≈ 0.66 Gyr**(factor 
\3.2× more collapse-prone than the V_max=15 headline). this is the**representative**result, not the headline 
\V_max = 15 km/s which is the most generous self-assessment.**Since Fornax is observed to have a diffuse DM 
\core (M_c ~ 10⁷ M☉, r_c ~ 1 kpc per Walker+ 2009 / Read+ 2019 / Hayashi+ 2020 kinematic decomposition, NOT 
\stellar core per Mateo+ 1998; Peñarrubia+ 2008 gives a dynamical mass profile), the framework's prediction 
\of collapse in <1 Gyr is a real tension.**The dSph tension has three possible outcomes:
 -**Resolution by narrower width (D-5):**If σ_1 ≤ 3.0 km/s (FWHM ≤ 7.1 km/s) is consistent with the 
\eight-channel dataset, the dSph gravothermal tail is suppressed while preserving the Cloud-9 bulk σ/m (σ_1 = 
\3.0 km/s gives exp(-(15-29.4)²/(2×3.0²)) = 1.0×10⁻⁵ ≈ 0 contribution at V_max = 15 km/s).**:**D-5 only 
\addresses the resonance-component tail. The framework's BACKGROUND Yukawa σ/m at all dSph velocities exceeds 
\Horigome+ 2025 [27]'s decisive CDM-preference threshold (σ/m > 0.2 cm²/g). (Phase 44 fit: σ_0 = 0.052, 
\a_slope = 1.93):
  - v = 9 (Sculptor): 5.43 cm²/g (canonical a_slope=1.93, background only) — 27× above the **0.2 cm²/g 
\decisive CDM-preference threshold**
  - v = 10 (Draco): 4.39 cm²/g (background only) — 22× above the **0.2 cm²/g decisive threshold**
@@ -126,7 +126,7 @@ ### 2.5 σ/m vs σ_eff: microphysical and observational cross-sections
  - v = 25: 0.75 cm²/g (background only) — 3.7× above the **0.2 cm²/g decisive threshold**
  - v = 28 (Cloud-9): 0.60 cm²/g (background only) — 3× above the **0.2 cm²/g decisive threshold** (resonance 
\peak: σ/m = 174, far above)
 
-**Threshold-rotation note.** Three different Horigome+ 2025 limits are in play across this paper, and each 
\quoted multiple below is against a NAMED one: the **0.8 cm²/g** w = 10 km/s velocity-dependent upper limit 
\(the appropriate comparison for this framework's strongly velocity-dependent σ/m(v), and the basis for the 
\abstract's 3.6–23.7×), the **0.2 cm²/g** decisive CDM-preference threshold (the basis for the 3–27× figures 
\above), and the **0.04 cm²/g** velocity-independent (w→∞) upper limit (the basis for the 115–460× figures in 
\§3.6). The three are NOT interchangeable: the same σ/m(15) yields 3.6×, 10×, and 50× against the 0.8, 0.2, 
\and 0.04 limits respectively.**Path B:**Horigome's Eq. 2 is dσ/dcosθ = (σ0/2) × [1 + (v/w)² sin²(θ/2)]² — 
\this IS velocity-dependent. The "velocity-independent case" cited in the abstract is the limit w → ∞. The 
\framework's σ/m is velocity-dependent (a_slope = 1.93 + resonance peak). The direct comparison "framework 
\exceeds Horigome's threshold at v < 28 km/s" is true, but the velocity-dependent comparison requires 
\re-running Horigome's likelihood with the framework's σ/m(v) profile.**For submission: state that the 
\framework's background σ/m at dSph velocities is well above Horigome's velocity-independent threshold 
\(factor ~10× at v=15, factor ~22× at v=10), and that a proper comparison requires the velocity-dependent 
\likelihood.**don't lower σ_0 to evade Horigome (parameter-fitting); instead, state the result plainly and 
\specify what the correct test would be.**| Channel | σ_1 = 4.4 baseline log L | σ_1 = 1.0 log L | Δlog L |
+**Threshold-rotation note.** Three different Horigome+ 2025 limits are in play across this paper, and each 
\quoted multiple below is against a NAMED one: the **0.8 cm²/g** w = 10 km/s velocity-dependent upper limit 
\(the appropriate comparison for this framework's strongly velocity-dependent σ/m(v), and the basis for the 
\abstract's 3.6–23.7×), the **0.2 cm²/g** decisive CDM-preference threshold (the basis for the 3–27× figures 
\above), and the **0.04 cm²/g** velocity-independent (w→∞) upper limit (the basis for the 136–246× figures in 
\§3.6). The three are NOT interchangeable: the same σ/m(15) = 2.85 cm²/g yields 3.6×, 14.2×, and 71.2× 
\against the 0.8, 0.2, and 0.04 limits respectively.**Path B:**Horigome's Eq. 2 is dσ/dcosθ = (σ0/2) × [1 + 
\(v/w)² sin²(θ/2)]² — this IS velocity-dependent. The "velocity-independent case" cited in the abstract is 
\the limit w → ∞. The framework's σ/m is velocity-dependent (a_slope = 1.93 + resonance peak). The direct 
\comparison "framework exceeds Horigome's threshold at v < 28 km/s" is true, but the velocity-dependent 
\comparison requires re-running Horigome's likelihood with the framework's σ/m(v) profile.**For submission: 
\state that the framework's background σ/m at dSph velocities is well above Horigome's velocity-independent 
\threshold (factor ~10× at v=15, factor ~22× at v=10), and that a proper comparison requires the 
\velocity-dependent likelihood.**don't lower σ_0 to evade Horigome (parameter-fitting); instead, state the 
\result plainly and specify what the correct test would be.**| Channel | σ_1 = 4.4 baseline log L | σ_1 = 1.0 
\log L | Δlog L |
 |---------|--------------------------|-----------------|---------|
 | Cloud-9 (V_max=28) | -2.4 | -0.7 | +1.7 |
 | JVAS (V_max=15) | -2.0 | -2.0 | 0 |
@@ -148,7 +148,7 @@ ### 2.5 σ/m vs σ_eff: microphysical and observational cross-sections
  Under σ_1 = 1.0, the derivation changes. anchored σ_DM-DM ~ 1 cm²/g at the "Cloud-9 benchmark"; under σ_1 = 
\4.4 this held at v ~ 100 (Gaussian tail extends that far). Under σ_1 = 1.0, σ/m at v = 100 is 0.052 cm²/g 
\(background only); σ/m at v = 28 is 65.49 cm²/g.
 - Using σ_DM-DM at v = 100 (background only, σ/m = 0.052 cm²/g): ratio σ_DM-DM/σ_SI = 9.85e+21 → g_N/g_χ < 
\1.01e-11
 - Using σ_DM-DM at v = 28 (Cloud-9, σ/m = 65.49 cm²/g at σ_1 = 1.0): ratio σ_DM-DM/σ_SI = 1.24e+25 → g_N/g_χ 
\< 2.84e-13
--**The 7.5×10⁻¹² value was anchored to σ_DM-DM ~ 1 cm²/g; under σ_1 = 1.0 the anchor shifts to σ/m = 65.49 
\cm²/g at v = 28.**The hierarchy constraint is g_N/g_χ < 2.84e-13 (v = 28) and < 1.01e-11 (v = 100, 
\background only) — i.e. the v = 28 bound is slightly LOOSER than the σ_1 = 4.4 headline g_N/g_χ < 1.74e-13, 
\not more restrictive. (Corrected: the previously quoted ratios 5.2×10⁴⁴ / 6.5×10⁴⁷ dropped the m_χ = 
\1.78×10⁻²⁴ g factor, so they were ~10²² too large and the direction of the shift was inverted.)**§10.7 
\hierarchy constraint update:**-**Primary value (used in thesis, abstract, all downstream claims):**Both new 
\values are less restrictive than the σ_1 = 4.4 headline (g_N/g_χ < 2.84e-13 vs 1.74e-13 at v = 28; 1.01e-11 
\at v = 100). The single-mediator Yukawa framework with σ_1 ≲ 3.0 km/s requires an even deeper dark-sector 
\hierarchy than the σ_1 = 4.4 baseline indicated. The footnote needs to note that the hierarchy 
\constraint**depends on σ_1**: under σ_1 = 1.0 (the D-5 fit maximum-likelihood), the ratio derivation changes 
\and 4 baseline headline value 7.5×10⁻¹² holds under the σ_1 = 4.4 phenomenological width; under σ_1 ≲ 3.0, 
\the constraint is tighter.**Outcome:**this is a parameter constraint, not framework falsification.**The 
\framework with σ_1 ≲ 3.0 km/s is**NOT falsified**— it's consistent with the 8-channel dataset if Fornax is 
\added as a no-collapse constraint. What's falsified (or constrained) is the parameter combination (σ_peak = 
\174 cm²/g, σ_1 = 4.4 km/s, m_χ = 1 GeV). Under the D-5 fit's preferred σ_1 ≲ 3.0 km/s, the framework is 
\consistent.
+-**The 7.5×10⁻¹² value was anchored to σ_DM-DM ~ 1 cm²/g; under σ_1 = 1.0 the anchor shifts to σ/m = 65.49 
\cm²/g at v = 28.**The hierarchy constraint is g_N/g_χ < 2.84e-13 (v = 28) and < 1.01e-11 (v = 100, 
\background only) — i.e. the v = 28 bound is slightly LOOSER than the σ_1 = 4.4 headline g_N/g_χ < 1.74e-13, 
\not more restrictive (like-for-like at the v = 28 anchor the baseline is 1.78e-13, so the ordering is 
\unchanged). (Corrected: the previously quoted ratios 5.2×10⁴⁴ / 6.5×10⁴⁷ dropped the m_χ = 1.78×10⁻²⁴ g 
\factor, so they were ~10²² too large and the direction of the shift was inverted.)**§10.7 hierarchy 
\constraint update:**-**Primary value (used in thesis, abstract, all downstream claims):**Both new values are 
\less restrictive than the σ_1 = 4.4 headline (g_N/g_χ < 2.84e-13 vs 1.74e-13 at v = 28; 1.01e-11 at v = 
\100). The single-mediator Yukawa framework with σ_1 ≲ 3.0 km/s therefore permits a deeper dark-sector 
\hierarchy than the σ_1 = 4.4 baseline indicated (see the computed bounds below). The footnote needs to note 
\that the hierarchy constraint**depends on σ_1**: under σ_1 = 1.0 (the D-5 fit maximum-likelihood), the ratio 
\derivation changes and the σ_1 = 4.4 baseline headline value 7.5×10⁻¹² holds under the σ_1 = 4.4 
\phenomenological width. **Direction of the shift, computed from the same hierarchy formula (g_N/g_χ < 
\1/√(σ/m·m_χ/σ_SI)), all three at a like-for-like v = 28 anchor:** σ_1 = 4.4 → σ/m(28) = 166.0 cm²/g → 
\g_N/g_χ < 1.78×10⁻¹³; σ_1 = 3.0 → σ/m(28) = 156.7 cm²/g → g_N/g_χ < 1.84×10⁻¹³; σ_1 = 1.0 → σ/m(28) = 65.49 
\cm²/g → g_N/g_χ < 2.84×10⁻¹³. Narrowing σ_1 therefore LOWERS the framework's σ/m at v = 28 and 
\correspondingly LOOSENS the allowed g_N/g_χ at that anchor (a larger permitted g_N/g_χ is a deeper 
\dark-sector hierarchy, not a tighter constraint on it); it also suppresses the dSph tail, which is the point 
\of the D-5 resolution. **Anchor bookkeeping:** the σ_1 = 4.4 headline 1.74×10⁻¹³ is quoted at the 
\*resonance-peak* anchor (σ_peak = 174 cm²/g at v = 29.4), whereas the 2.84×10⁻¹³ D-5 value is quoted at the 
\*v = 28* anchor, so the headline-vs-D-5 pair as printed compares two different anchors. The like-for-like v 
\= 28 comparison is 2.84×10⁻¹³ (σ_1 = 1.0) vs 1.78×10⁻¹³ (σ_1 = 4.4); the direction is the same under either 
\anchoring (the D-5 value is looser), so the conclusion is unchanged.**Outcome:**this is a parameter 
\constraint, not framework falsification.**The framework with σ_1 ≲ 3.0 km/s is**NOT falsified**— it's 
\consistent with the 8-channel dataset if Fornax is added as a no-collapse constraint. What's falsified (or 
\constrained) is the parameter combination (σ_peak = 174 cm²/g, σ_1 = 4.4 km/s, m_χ = 1 GeV). Under the D-5 
\fit's preferred σ_1 ≲ 3.0 km/s, the framework is consistent.
 -**Open question (N-body resolution):**Silverman+ 2026 merger-history mechanism (sustained mergers suppress 
\gravothermal collapse in roughly half of halos) may apply at dSph scale. Requires N-body with realistic 
\merger histories.
 -**Falsification:**If no narrower width is consistent with the eight-channel dataset AND no merger-history 
\correction applies, the framework is falsified at dSph scales.**D-5 partial result: σ_1 = 3.0 km/s is a 
\viable resolution; whether the eight-channel fit prefers 3.0 over 4.4 requires a full likelihood refit 
\(deferred to v19.2-D; sensitivity analysis above shows the dSph channel strongly prefers 3.0).**Interim 
\conclusion:**The framework predicts collapse for Fornax-like halos on timescales of <1 Gyr (canonical V_max 
\= 18). This is a real tension with observations.**The framework's phenomenological width σ_1 = 4.4 km/s may 
\be too broad; σ_1 = 3.0 km/s suppresses the dSph tail while preserving the Cloud-9 bulk.**The framework is 
\NOT falsified if σ_1 ≤ 3.0 km/s is consistent with the eight-channel dataset; this requires a full 
\likelihood refit to confirm.
 
@@ -192,7 +192,7 @@ ### 2.6 σ_peak_HH_1 Sensitivity Sweep**Question:**Different Phase 44 fits give
 | 250 | 238.27 | 232.11 | 172.56 | 53 Myr | 92 Myr | 0.58 | 3.47 Gyr | 335 Myr | 10.34 | −0.68 (substantive) 
\| (R88(31) regenerated table: σ/m(V_max) computed from canonical Gaussian σ/m(v) at a_slope=1.93, 
\v_target=29.4, FWHM=4.4; t_cross uses r_s/V_max convention (T204-style, consistent with §2.5 and §9.12); 
\"below cap" = t_core/t_cross < 3, fails causality criterion.)**Three key results (R88(31) with canonical 
\Gaussian σ/m(v)):** 1. **At c = 12 (ΛCDM-conservative, §9.12 analytical-only):** the continuous viable 
\σ_peak window is **EMPTY** with canonical σ/m(v). Floor requires σ_peak ≥ 51.96; causality requires σ_peak ≤ 
\47.67 (interpolated from ratio = 2.86 at σ_peak = 50); σ_peak_min > σ_peak_max. On the swept grid {30, 50, 
\75, 100, 125, 150, 174, 200, 250}, σ_peak = 50 cm²/g is the closest to passing both (ratio = 2.86, just 
\below cap; σ/m(28) = 48.14 just below floor 50). σ_peak = 30 fails the floor; σ_peak ≥ 75 fail c = 12 
\causality (ratio < 3). The framework's canonical σ_peak = 174 fails c = 12 causality (ratio = 0.83, below 
\cap by factor ~3.6). **The grid result is a discretization check; the EMPTY continuous window is the 
\physical c-M tension at ΛCDM-standard concentration** (see §2.6a for synthesis). 2. **At c = 4 (Ohana+ 
\physical anchor, §9.12):** on the swept grid, σ_peak ∈ {75, 100, 125, 150, 174, 200, 250} pass the floor 
\σ/m(28) ≥ 50 cm²/g (σ_peak = 30 gives σ/m(28) = 29.13, σ_peak = 50 gives σ/m(28) = 48.14, both FAIL the 
\floor). All σ_peak ∈ {30, ..., 250} pass the causality criterion (ratio > 3 at every σ_peak). Continuous 
\intersection: [51.96, 250] cm²/g (limited by sweep range). At σ_peak = 174: σ/m(V_max = 25.59) = 120.32 
\cm²/g, t_core = 4.97 Gyr, ratio = 14.83 (well above cap).
 
 3.**Fornax σ_HL outlier:**At σ_peak ∈ {30, 50}, σ_HL_required is marginal (−0.08, −0.13 — could be 
\rounding/systematic). At σ_peak ≥ 75, σ_HL is substantive (≤ −0.20). At σ_peak = 174 (canonical), σ_HL = 
\−0.47.**The outlier is structural**— consequence of v₁ Gaussian tail reaching dSph 
\velocities.**Reconciliation with §9.12:**§9.12 reports σ_peak = 174, t_core = 76 Myr at c = 12 (this sweep 
\reproduces**exactly**: t_core = 0.076 Gyr; σ/m(V_max=31.12) = 161.70 matches §9.12's 161.70 (exact match)). 
\At c = 4, §9.12 reports t_core = 4.97 Gyr (canonical). This sweep computes**t_core = 4.97 Gyr (consistent 
\with §9.12's canonical σ/m=120.32 at c=4)**. **§9.12's "same σ/m = 161.70 at c = 4" is internally 
\inconsistent (σ/m depends on V_max which differs at each c)**(σ/m depends on V_max which differs at each c). 
\The canonical-NFW sweep gives the self-consistent answer: 0.076 Gyr at c=12 (exact match), 4.97 Gyr at c=4 
\(canonical self-consistent σ/m(V_max=25.59) = 120.32).** :**§9.12 uses V_max = 31.12 (NFW V_max at r_max = 
\2.16 r_s). The Cloud-9 / Elbert working benchmark is defined at v = 28 (resonance peak, BLN24). Two 
\different velocities serving two purposes; both used correctly here. The V_max now varies at each c per 
\canonical NFW, rather than held fixed.**SPARC consistency:**σ/m(v = 100) = 0.052 cm²/g constant across the 
\sweep. SPARC is not a constraint on σ_peak under the paper convention.**Parameterization comparison (sanity 
\check):**The Breit-Wigner parameterization used in v19.2-A v1 (and the Phase 44 multi-channel fit) gives σ/m 
\values that differ from the paper's Gaussian by up to ~17× at UFD velocities. The Gaussian (paper 
\convention) is what §2.5 and §9.12 state.**Bottom line:**Under the paper's own σ/m convention (Gaussian w = 
\4.4) and causality criterion (ratio > 3), with self-consistent canonical NFW at each c:
--**At c = 12:** the continuous viable σ_peak window is **EMPTY** with the canonical Gaussian σ/m(v). Floor 
\requires σ_peak ≥ 51.96; causality requires σ_peak ≤ 47.67 (interpolated from ratio = 2.86 at σ_peak = 50). 
\On the swept grid, σ_peak = 50 is closest to satisfying both (ratio = 2.86, just below the 3.0 cap; σ/m(28) 
\= 48.14, just below the 50 floor).
+-**At c = 12:** the continuous viable σ_peak window is **EMPTY** with the canonical Gaussian σ/m(v). Floor 
\requires σ_peak ≥ 51.96; causality requires σ_peak ≤ 47.67 (interpolated from ratio = 2.86 at σ_peak = 50; 
\the interpolation assumes the causality ratio ∝ 1/σ_peak, i.e. ratio = 143/σ_peak with 143 = 2.86 × 50 — 
\this scaling reproduces the swept table's ratio column to within 1.4% at σ_peak = 50, 150, 174, 200 and 250, 
\so the assumption holds on the grid). On the swept grid, σ_peak = 50 is closest to satisfying both (ratio = 
\2.86, just below the 3.0 cap; σ/m(28) = 48.14, just below the 50 floor).
 -**At c = 4**(Ohana+ anchor, §9.12 physical anchor): continuous window is [51.96, 250] cm²/g. On the swept 
\grid, σ_peak ∈ {75, ..., 250} pass both (σ_peak = 30, 50 FAIL the floor). **Framework is consistent at c = 4 
\for σ_peak ≥ 51.96.**-**Fornax σ_HL outlier**is marginal for σ_peak ≤ 50, substantive for σ_peak ≥ 75.
 
 The c = 12 vs c = 4 distinction is itself the c-M tension against ΛCDM (Ohana+ 2026). At c = 12, the 
\Balberg+ analytical formula is unreliable for σ_peak ≥ 75; N-body is required, as §9.12 
\acknowledges.**Synthesis — what σ_peak reconciles Cloud-9 with the framework's causality criterion?**The 
\framework is asking: given the published σ/m ≥ 50 cm²/g working benchmark (Elbert+ 2015 [55a]) and the 
\paper's own causality criterion (ratio > 3), what σ_peak values satisfy both? At ΛCDM-standard concentration 
\(c = 12), no value of σ_peak satisfies both constraints — the floor and causality requirements are disjoint 
\(σ_peak ≥ 51.96 vs σ_peak ≤ 47.67 (interpolated from ratio = 2.86 at σ_peak = 50)). On the swept grid, 
\σ_peak = 50 is closest (ratio = 2.86, just below the 3.0 cap; σ/m(28) = 48.14, just below the 50 floor). At 
\Ohana+ concentration (c = 4), the answer is an open interval**[51.96, 250] cm²/g**across the entire swept 
\range. The framework's canonical σ_peak = 174 satisfies the floor and passes causality only at c = 4 (Ohana+ 
\physical anchor) — not at c = 12 (ΛCDM-conservative).**The synthesis: the σ_peak is not a free parameter 
\once both the Cloud-9 floor and the causality criterion are imposed; at c = 12, it is constrained to ~50 
\cm²/g (a factor of 3.5× below the canonical framework value of 174); at c = 4, it is constrained to σ_peak ≥ 
\~50 cm²/g (consistent with the canonical framework value).**Footnote — V_max = 31.12 derivation:**V_max = 
\31.12 at c = 12 is**derived**from the canonical NFW profile at M_200 = 5×10⁹ M☉, ρ_crit = 1.381×10⁻⁷ M☉/pc³, 
\evaluated at r_max = 2.1626 r_s. This is the same derivation §9.12 used (r_max = 2.16 r_s, post v18.43 T215 
\IC correction). The match is a consistency check, not a coincidence. At c = 4, the same derivation gives 
\V_max = 25.59 km/s — §9.12 implicitly holds σ/m(V_max) constant across c rather than re-deriving V_max, 
\which is the source of the 11% t_core discrepancy this sweep corrects.
@@ -936,7 +936,7 @@ ### 3.6 dSph upper-limit tension (Horigome+ 2025)**Data:**Horigome+ 2025 [27] (a
 
 [Historical σ/m(v) table removed from main text in R88(20); moved to Appendix A.12.] This table used the 
\v1.13 placeholder f_H, retracted v18.29 — superseded by the canonical Gaussian form (above). For the 
\historical record and rationale, see Appendix A.12.
 
-If we instead use the velocity-independent limit (0.04 cm²/g), the violations are higher (115–460×), but 
\this is not the appropriate limit for a strongly velocity-dependent model like ours.**Note on earlier 
\versions:**v1.6–v1.9 of this paper applied the w = 30 km/s velocity-dependent limit (0.2 cm²/g, Eq. 13 of 
\[27]) at v=30 km/s, giving a "800× violation" which was based on both (a) the wrong velocity convention AND 
\(b) the wrong limit for a velocity-dependent model. v1.10 corrects the velocity convention (v_eff = 0.64 × 
\V̂_max); the limit choice was further refined in to use the w=10 km/s case appropriate for our model. The 
\combined effect is to reduce the apparent tension from ~800× to**3.6–23.7×**at v_eff = 5–20 km/s (R88(30) 
\corrected from 6-23×).**Status :**The 3.6–23.7× violation reported in v1.11 (recomputed in R88(30); was 
\previously reported as 6-23×) was nominally resolved in v1.12 by the combined two-component asymmetric DM 
\(Yang+ 2025 PRD [42]) + gravothermal core-collapse selection effect (Yu+ 2026 PRL [23]) + Gaussian 
\Breit-Wigner profile.**However, per the v18.32 honest phenomenological audit, this resolution depends on f_H 
\values that are not first-principles derived and not reproduced by the project's own N-body check.**The 
\Channel-by-Channel table below used**hand-picked f_H values**(~0.85 / 0.30) that were initially attributed 
\to Yang+ 2025 Fig. 2 but were later shown to**not actually match Yang+ Fig. 2**. With Yang+ 2025-derived f_H 
\(Phase 44 σ/m → no significant gravothermal cascade), the multi-resonance profile**does not simultaneously 
\satisfy**the Cloud-9 (σ/m ≥ 50) and dSph (σ/m ≤ 0.8) channels at Phase 44 parameters. Furthermore, the 
\heavy-channel-only decomposition σ_eff = f_H² × σ_HH(v) cannot match SPARC's σ/m ≈ 0.193 at v = 100 km/s for 
\any f_H (max achievable σ_eff = 0.069) — a structural limitation.**See §9.6 (Limitations) for the full 
\honest discussion and §9.7 for the per-f_H-prescription channel table.**| Channel | Constraint | σ/m_eff 
\(with borrowed f_H, v1.12) | σ/m_eff | σ/m_eff (Yang+ 2025-derived f_H) | Status |
+If we instead use the velocity-independent limit (0.04 cm²/g), the violations are higher (**136–246×** for 
\the v = 9–40 km/s range — σ/m = 5.43 and 9.86 cm²/g from the canonical table above), but this is not the 
\appropriate limit for a strongly velocity-dependent model like ours. (The 115–460× figure quoted in earlier 
\drafts was computed from the RETRACTED A.12 table and is not reproducible from the current canonical σ/m(v); 
\it is superseded here.)**Note on earlier versions:**v1.6–v1.9 of this paper applied the w = 30 km/s 
\velocity-dependent limit (0.2 cm²/g, Eq. 13 of [27]) at v=30 km/s, giving a "800× violation" which was based 
\on both (a) the wrong velocity convention AND (b) the wrong limit for a velocity-dependent model. v1.10 
\corrects the velocity convention (v_eff = 0.64 × V̂_max); the limit choice was further refined in to use the 
\w=10 km/s case appropriate for our model. The combined effect is to reduce the apparent tension from ~800× 
\to**3.6–23.7×**at v_eff = 5–20 km/s (R88(30) corrected from 6-23×).**Status :**The 3.6–23.7× violation 
\reported in v1.11 (recomputed in R88(30); was previously reported as 6-23×) was nominally resolved in v1.12 
\by the combined two-component asymmetric DM (Yang+ 2025 PRD [42]) + gravothermal core-collapse selection 
\effect (Yu+ 2026 PRL [23]) + Gaussian Breit-Wigner profile.**However, per the v18.32 honest phenomenological 
\audit, this resolution depends on f_H values that are not first-principles derived and not reproduced by the 
\project's own N-body check.**The Channel-by-Channel table below used**hand-picked f_H values**(~0.85 / 0.30) 
\that were initially attributed to Yang+ 2025 Fig. 2 but were later shown to**not actually match Yang+ Fig. 
\2**. With Yang+ 2025-derived f_H (Phase 44 σ/m → no significant gravothermal cascade), the multi-resonance 
\profile**does not simultaneously satisfy**the Cloud-9 (σ/m ≥ 50) and dSph (σ/m ≤ 0.8) channels at Phase 44 
\parameters. Furthermore, the heavy-channel-only decomposition σ_eff = f_H² × σ_HH(v) cannot match SPARC's 
\σ/m ≈ 0.193 at v = 100 km/s for any f_H (max achievable σ_eff = 0.069) — a structural limitation.**See §9.6 
\(Limitations) for the full honest discussion and §9.7 for the per-f_H-prescription channel table.**| Channel 
\| Constraint | σ/m_eff (with borrowed f_H, v1.12) | σ/m_eff | σ/m_eff (Yang+ 2025-derived f_H) | Status |
 |---|---|---|---|---|---|
 | Cloud-9 (v=28, core-forming) | ≥100 cm²/g |**128 cm²/g**✓ |**92 cm²/g**✗ (below floor) |**87 cm²/g**✗ 
\(below floor) | Pass with borrowed; fail with Yang+-derived |
 | dSph (v=15, core-collapsed, r_obs=0.2 r_vir) | ≤0.8 cm²/g |**0.18 cm²/g**✓ |**4.2 cm²/g**✗ (above ceiling) 
\|**3.1 cm²/g**✗ (above ceiling) | Pass with borrowed; fail with Yang+-derived |
@@ -2133,7 +2133,7 @@ ### A.7 f_H retraction (R88)
 
 ### A.8 Horigome+ 2025 comparison caveat (R88)
 
-The '3.6–23.7× at v_eff = 5–20 km/s (using Horigome+'s w = 10 km/s velocity-dependent limit of 0.8 cm²/g) 
\and 27–49× at v = 9–40 km/s (against their decisive CDM-preference threshold of 0.2 cm²/g, Abstract); 830× 
\at v = 28 km/s' comparison is approximate:
+The '3.6–23.7× at v_eff = 5–20 km/s (using Horigome+'s w = 10 km/s velocity-dependent limit of 0.8 cm²/g) 
\and 27–49× at v = 9–40 km/s (against their decisive CDM-preference threshold of 0.2 cm²/g, Abstract; the v = 
\9 and v = 40 endpoint values — the window minimum is 14× at v = 15); 830× at v = 28 km/s comparison is 
\approximate:
 
 - The 0.2 cm²/g reference used above is Horigome+'s **decisive CDM-preference threshold** (Abstract), which 
\applies to a velocity-independent cross-section
 - Our σ/m(v) is velocity-dependent (Gaussian + power-law background)
@@ -2190,7 +2190,7 @@ ## A.12 Historical σ/m(v) table (moved from §3.6 main text, R88(20))
 | v_eff = 15 km/s (classical dSphs) | 5.0 cm²/g | 0.03 cm²/g | 0.8 cm²/g | 6× | ✓ PASS |
 | v_eff = 20 km/s (high-V_max dSphs) | 6.8 cm²/g | 0.04 cm²/g | 0.8 cm²/g | 8× | ✓ PASS |
 
-**Caveat:** the v1.13 ✓ PASS values in this table use the **hand-picked placeholder f_H**. With Yang+ 
\2025-derived or T202 N-body-derived f_H values, the dSph v=15 channel fails (σ/m_eff ≈ 3.1 cm²/g vs 0.8 
\ceiling; see §9.3 table). The table is retained here for archival purposes; the current honest status is 
\documented in §3.6 status line (canonical Gaussian: Cloud-9 anchor satisfied at σ/m(28) = 166 cm²/g; dSph 
\Horigome+ comparison violated by 3.6-23.7× at w=10 (R88(30) corrected from 6-23×) / 27–49× at their decisive 
\CDM-preference threshold of 0.2 cm²/g (R88(30) corrected from 10-49×)).
+**Caveat:** the v1.13 ✓ PASS values in this table use the **hand-picked placeholder f_H**. With Yang+ 
\2025-derived or T202 N-body-derived f_H values, the dSph v=15 channel fails (σ/m_eff ≈ 3.1 cm²/g vs 0.8 
\ceiling; see §9.3 table). The table is retained here for archival purposes; the current honest status is 
\documented in §3.6 status line (canonical Gaussian: Cloud-9 anchor satisfied at σ/m(28) = 166 cm²/g; dSph 
\Horigome+ comparison violated by 3.6-23.7× at w=10 (R88(30) corrected from 6-23×) / 27–49× at their decisive 
\CDM-preference threshold of 0.2 cm²/g (R88(30) corrected from 10-49×; the v = 9 / v = 40 endpoint values, 
\with the window minimum 14× at v = 15)).
 
 ### A.13 Citation corrections (R88(82))
 
```


## 3. `v0.3-prelim/data/results/v192_dsph_gravothermal_sweep.json`

Regenerated sweep JSON — new `_derived_ranges` block; `dsph_halos` data unchanged.

**v1.1 change (n18 review item 3): this section now shows the DIFF, not the full file.**
v1.0 embedded all 241 lines of the JSON (10,135 bytes) even though only 20 lines differed (+19/−1) in
Round 5 — the change was buried inside 220 unchanged lines, which defeats the purpose of a
*changed-code* companion. The live file is the authority:
`v0.3-prelim/data/results/v192_dsph_gravothermal_sweep.json` (241 lines, 10,135 bytes).

**Diff shown:** pre-Round-5 (`7cc8d8a^`) -> current. 3 changes, 39 diff lines:

1. **`_derived_ranges` added** (18 lines) — the machine-readable single source of truth for
   the σ/m range, the published σ_eff band, the σ_HL range, and the halo count.
2. **`verdict.interpretation` rewritten** — the stale `"sigma/m ~0.5-2.5 cm^2/g"` replaced by
   the computed `"sigma/m ~2.85-16.87 cm^2/g"`.
3. **`limitations` +1 entry** — the caveat that the paper's quoted 0.5-2.5 cm²/g dSph band
   predates the a_slope propagation.

```diff
--- a/v0.3-prelim/data/results/v192_dsph_gravothermal_sweep.json
+++ b/v0.3-prelim/data/results/v192_dsph_gravothermal_sweep.json
@@ -205,17 +205,35 @@
       "consistency": "MIXED"
     }
   },
+  "_derived_ranges": {
+    "note": "computed from dsph_halos; regenerate the file rather than hand-editing",
+    "sigma_m_cm2_per_g": {
+      "min": 2.8454570671911887,
+      "max": 16.865226429437705
+    },
+    "sigma_eff_published_cm2_per_g": {
+      "min": 0.0318,
+      "max": 0.0931
+    },
+    "sigma_HL_cm2_per_g": {
+      "min": -3.392310425355699,
+      "max": -0.5340265143981119
+    },
+    "n_halos": 8,
+    "n_halos_abs_sigma_HL_below_0.05": 0
+  },
   "verdict": {
     "all_dSphs_pass_observational": true,
     "all_dSphs_pass_gravothermal_no_collapse": false,
     "all_dSphs_pass_causality": false,
-    "interpretation": "Per r20.docx Bug 1 fix: paper convention (Gaussian w=4.4) gives sigma/m ~0.5-2.5 
\cm^2/g at dSph scale (not 5-18 cm^2/g from phase44_sigma_HH_at_v). This is closer to published sigma_eff. 
\Per r20.docx Bug 2 fix: t_cross now uses canonical T212 function (r_s = r_vir/c), giving physically 
\meaningful values (~0.05-0.5 Gyr). Causality verdict is now meaningful. Per r20.docx recommendation 5: 'NEW 
\DISCOVERY' marked as PROVISIONAL. After Bug fixes, the 100x microphysical-vs-observational inconsistency 
\shrinks significantly. The picture is now: framework sigma/m and sigma_eff_published are within ~10x at dSph 
\scale, not 100x. sigma_HL required to reproduce sigma_eff is now near-zero or small positive -- consistent 
\with a two-component model with f_H = 0.30."
+    "interpretation": "Per r20.docx Bug 1 fix: paper convention (Gaussian w=4.4) gives sigma/m ~2.85-16.87 
\cm^2/g at dSph scale (not 5-18 cm^2/g from phase44_sigma_HH_at_v), over the 8 halos listed. Published 
\sigma_eff spans 0.032-0.093 cm^2/g. NOTE: this sigma/m range and the published sigma_eff range are NOT 
\related by sigma_eff = f_H^2*sigma/m with f_H = 0.3: that identity would give sigma_eff = 0.256-1.518 
\cm^2/g, i.e. 2.8-47.7x ABOVE the published band. Reconciling the two therefore requires a NEGATIVE 
\cross-channel term. The fitted sigma_HL spans -3.392 to -0.534 cm^2/g, and 0/8 halos satisfy |sigma_HL| < 
\0.05 cm^2/g. Per r20.docx Bug 2 fix: t_cross now uses canonical T212 function (r_s = r_vir/c), giving 
\physically meaningful values (~0.05-0.5 Gyr). Causality verdict is now meaningful. Per r20.docx 
\recommendation 5: 'NEW DISCOVERY' marked as PROVISIONAL. The magnitude of the microphysical-vs-observational 
\gap is LARGE, and is bridged only by a large negative sigma_HL -- not by a near-zero or small-positive one."
   },
   "limitations": [
     "Analytical Balberg+ formula; no N-body at dSph scale.",
     "sigma_HL calibrated to match sigma_eff_published; should be fit from SPARC / cluster data.",
     "Halo parameters from Read+ 2019 [29d], Walker+ 2009, Wolf+ 2010.",
     "f_H_cc = 0.30 from T207 fit; alternative f_H values (~0.45-0.50) exist in extended fits.",
+    "The halo-mass (M_halo) assumption is fixed per halo from Read+ 2019 / Walker+ 2009 / Wolf+ 2010; the 
\paper's quoted 0.5-2.5 cm^2/g dSph band predated the a_slope 1.0->1.93 propagation and is superseded by 
\sigma_m_paper_convention_cm2_per_g above.",
     "Paper convention uses Gaussian; phase44 uses Breit-Wigner -- two different parameterizations.",
     "Removed UMa-II (UDG) from dSph list per p1.docx Smaller item 3.",
     "NEW DISCOVERY from v19.2-D.2 is now RESOLVED as bugs (per r20.docx review)."
```


## 4. `docs/LOCAL_REVIEW_R5.md`

Local review (Strata) — all 6 findings annotated with audit verdicts


**63 lines, 9,341 bytes**


```markdown
# Local Review (Reviewer 1, Round 5)

**Model:** `qwen3.8-flash-next-iq3_xxs` (strata (deep, :8080))  
**Generated:** 2026-10-25 14:10:36  
**Transport:** direct local OpenAI-compatible `/v1/chat/completions`  
**Why local:** OpenRouter free tier is account-blocked for this host today (HTTP 429 `free-models-per-day` on every free model, including the delegated Nemotron 3 Ultra 550B).  
**Reviewer role:** second independent reviewer, different model family from the OpenCode-side reviewer (DeepSeek/GLM/MiMo).  
**Excerpt source:** `R5_EXCERPT.md` (36199 chars, inlined — the local endpoint has no tool support).  

> **Status: UNVERIFIED SECOND OPINION — AUDITED 2026-10-25.** Every specific numerical claim below must be recomputed in Python before it is acted on.
>
> **Audit result:** all six findings verified against the canonical code and the paper on disk; all six are actionable and the corresponding paper fixes are applied. Corrections to THIS document are marked **Audit note (2026-10-25)** inline. Two of the reviewer’s own supporting calculations were wrong (the “9.85/0.2 = 49.25×” division has no referent in the paper; the “~22×” lower end is not the window minimum, which is 14× at v=15), and the L117 line references are off by one (the quoted text is at excerpt L116 / paper L120). Consolidated record: `docs/dual_review_5loop/SIDM_ROUND5_CONSOLIDATED_FIXES_v1.0_2026-10-25.md`.

## Review

[OK] F1: L11 distinguishes microphysical σ/m from σ_eff = f_H²·σ/m and states σ_eff(15)=0.251 cm²/g is below 0.8 cm²/g. Coherent.

[OK] F2: L36 labels 0.2 cm²/g as decisive CDM-preference threshold and 0.8 cm²/g as w=10 km/s velocity-dependent limit. L2210 repeats 3.6–23.7× vs 0.8 and 27–49× vs 0.2. Against 0.2: 5.43/0.2=27.15 (L118), 4.39/0.2=21.95 (L119), so “27–49×” is not fully supported by the quoted L118–119 values. [Q]
  → **Audit note (2026-10-25):** the *labeling* is correct, but the trailing `[Q]` is a stray — the substantive objection raised here is the L36 finding below, not a new question. Both ceilings are correctly named, and the 3.6–23.7× range IS reproducible from the canonical table (σ/m(15)/0.8 = 3.56×, σ/m(20)/0.8 = 23.65×), unlike the retracted-A.12-based 115–460× range. **Note:** an earlier draft of this review computed the upper end as “9.85/0.2 = 49.25×”; there is no 9.85 cm²/g anywhere in the paper (L143's 9.85e+21 is a dimensionless ratio, and the v=40 σ/m is 9.86), so that division had no referent. Correct value: 9.86/0.2 = 49.3×.

[OK] F3: L117 computes exp[-(15-29.4)²/(2×3.0²)] = exp[-207.36/18] = exp[-11.52] = 9.9e-6 ≈ 1.0e-5. Correct.

[OK] F4: L144 gives 2.84e-13; L145 says this is LOOSER than headline 1.74e-13. Since 2.84e-13 > 1.74e-13, “looser” is correct.

[OK] F5: L57 states unit peak at v=v_t and notes code uses energy-space unit-peak form. Correct.

[OK] F6: L82 uses v_res = c·sqrt(8·ΔM/(2·m_χ)). With ΔM/(2m_χ)=1.2e-9 (L82, L807): v = 299792 km/s × sqrt(8×1.2e-9) = 299792 × 9.798e-5 = 29.4 km/s. Correct.

[OK] F7: L82 says v1 is only physical resonance; v2–v4 are bookkeeping nodes. L896–898 also label them bookkeeping nodes, not physical resonances. Correct.

[OK] F8: L189–190 cap 47.67. If ratio(50)=2.86 and cap ratio=3.0, linear interpolation gives σ_cap = 50×3.0/2.86 = 52.45, not 47.67. If instead ratio ∝ 1/σ_peak, cap = 50×2.86/3.0 = 47.67. The paper does not state the proportionality, but 47.67 is arithmetically consistent with ratio ∝ 1/σ_peak. [OK]

[OK] F9: L1012 frames “7 of 8” as retracted v1.12/v1.13 placeholder, and L1012–1015 state SPARC cannot be matched. No contradiction.

[OK] F10: L1602–1604 and L2264 list 4 PASS: Cluster v=500, dSph v=10, Cloud-9 v=28, SPARC v=100; 3 MARGINAL: UFD v=3, v=5, v=15; 1 FAIL: dSph v=7. Sum = 8. Consistent.

[OK] F11: L189 floor: 50×50/48.14 = 51.96. Cap: 143/3 = 47.67. Since 51.96 > 47.67, EMPTY conclusion is correct.

[ERR] L36: “27–49× at v=9–40 km/s” is not supported by the excerpt’s own numbers. L118 gives 5.43/0.2=27.15×; L119 gives 4.39/0.2=21.95×. The lower end should be ~22× unless additional v=9–40 values are supplied.
  → **Audit note (2026-10-25): FINDING VALID, proposed correction superseded.** 27–49× is not a min–max over the v=9–40 km/s window, so the objection stands. But the window minimum is **14× at v=15** (σ/m = 2.85 cm²/g), not ~22×: the full canonical row set is 27.1× (v=9), 22.2× (v=10), 14.2× (v=15), 37.4× (v=18), 830× (v=28, excluded), 49.3× (v=40). 27–49× is the **v=9 / v=40 endpoint pair**. **FIXED** in the paper: L40 now labels 27–49× as the endpoint pair and states the 14× in-window minimum.

[ERR] L117: “σ/m ~ 0.5–2.5 cm²/g and σ_eff ~ 0.03–0.10 cm²/g” conflicts with L118–119, which give background σ/m = 5.43 and 4.39 cm²/g at v=9–10. If σ_eff = f_H²·σ/m, σ_eff cannot be 0.03–0.10 for σ/m=4.39–5.43 unless f_H≈0.08–0.15, which is not stated.
  → **Audit note (2026-10-25): FINDING VALID, and the defect is worse than stated.** Line reference is off by one — the quoted text is at excerpt **L116** (paper L120), not L117. More importantly the 0.5–2.5 cm²/g band is **STALE**: it predates the `a_slope` 1.0→1.93 propagation (commit 79edeae) and is not reproducible from the canonical Gaussian. The framework’s dSph-scale σ/m is **2.85–16.87 cm²/g**; the published σ_eff band **0.032–0.093 cm²/g** is an *observational* quantity, and at the sweep’s f_H = 0.30 the identity would give σ_eff = 0.256–1.518 cm²/g, i.e. **2.8–47.7× above** published. Reconciliation therefore requires a LARGE NEGATIVE σ_HL. **FIXED** in the paper (canonical band, explicit f_H assumption, negative-σ_HL statement) **and at the generator** — the script’s hardcoded narrative is now computed from the results so it cannot drift again.

[Q] L117: “7 of 8 halos” appears again in a non-retracted context. L1012 retracts “7 of 8 channels,” but L117 uses “7 of 8 halos” for |σ_HL|<0.05. Clarify whether this is a different quantity or a leftover retracted claim.
  → **Audit note (2026-10-25): ANSWERED — and the count itself is wrong.** “7 of 8 channels” (observational channels) and “7 of 8 halos” (dSph halos in the σ_HL fit) are **different quantities**, so L116 is not a resurrection of the retracted L1012 claim. But the “7 of 8” figure no longer holds at all: after the `a_slope` propagation the fitted σ_HL is |σ_HL| ≥ 0.53 cm²/g for every halo, so **0 of 8** satisfy |σ_HL| < 0.05, and Fornax (−0.534) is the *least* discrepant rather than an outlier. **FIXED** in the paper (L102 and L120) and in the JSON’s own verdict/interpretation strings.

[ERR] L145: “Both new values are less restrictive than the σ1=4.4 headline” conflicts with the next sentence: “under σ1≲3.0, the constraint is tighter.” L144–145 already show v=28 bound 2.84e-13 is looser than 1.74e-13. The “tighter” statement is inconsistent unless it refers to a different σ1 regime not shown.
  → **Audit note (2026-10-25): CONFIRMED, and the contradiction is sharper than stated.** σ1 = 1.0 *is* inside “σ1 ≲ 3.0”, so the sentence assigned opposite properties to a single regime. Computed from the paper’s own hierarchy formula g_N/g_χ < 1/√(σ/m·m_χ/σ_SI) at anchor v = 28: σ1=4.4 → σ/m = 166.0 → g < 1.78e-13; σ1=3.0 → 156.7 → g < 1.84e-13; σ1=1.0 → 65.5 → g < 2.83e-13. Narrowing σ1 *lowers* σ/m(28) and therefore *loosens* the allowed g_N/g_χ (a larger permitted g is a deeper hierarchy, not a tighter constraint on it). **FIXED** in the paper: the three computed bounds and the direction of the shift are now stated explicitly.

[Q] L189: “interpolated from ratio=2.86 at σ_peak=50” to cap 47.67 assumes ratio ∝ 1/σ_peak. State that assumption explicitly.
  → **Audit note (2026-10-25): CORRECT, and the assumption holds on the grid.** ratio = 143/σ_peak (143 = 2.86 × 50) reproduces the swept table’s ratio column to within 1.4% at σ_peak = 50, 150, 174, 200 and 250, and 143/3.0 = 47.67 reproduces the cap exactly. **FIXED** in the paper: the assumption and its grid check are now stated.

[Q] L2210: “dSph Horigome+ comparison violated by 3.6–23.7× at w=10” and “27–49× at decisive threshold” are archival, but the 27–49× range remains unsupported by L118–119.
  → **Audit note (2026-10-25): ANSWERED.** Both ranges are reproducible from the canonical σ/m table: 3.6–23.7× vs 0.8 comes from σ/m(15)/0.8 = 3.56× and σ/m(20)/0.8 = 23.65×, and 27–49× vs 0.2 is the v=9 / v=40 endpoint pair (5.43 and 9.86 cm²/g). The archival *staleness* was in the 115–460× range quoted against the 0.04 ceiling at paper L939 and L129 — that came from the **retracted A.12 table** and is superseded by **136–246×** from the canonical table. **FIXED** at L939 and L129.

[OK] L2270: dSph v=15 factor 7.8× above ceiling is internally consistent with L11 abstract range 3.6–23.7×.

[OK] L2275: canonical Phase 44 headline 1 PASS / 0 MARGINAL / 7 FAIL is consistent with L1606 caveat.

---
**Duration:** 246.4s  
**Usage:** {'prompt_tokens': 14292, 'completion_tokens': 1816, 'total_tokens': 16108, 'prompt_tokens_details': {'cached_tokens': 14287}}

```


---

## 6. Markup pass — `scripts/fix_markup.py` (built, verified, not applied)

### 6.1 What this file is

`scripts/fix_markup.py` repairs the paper's emphasis markers so that CommonMark renders them as
bold rather than as literal `**`. It is **not applied**: per user direction (2026-10-26) the
residual markup defect is purely presentational and is deferred, because it changes no prose, no
number, no unit and no citation.

The file is committed so the pass can be finished later without re-deriving the analysis.

### 6.2 Structure

| phase | functions (`scripts/fix_markup.py`) | what it does | why it is safe |
|---|---|---|---|
| 1 | `build_history_index`, `git_revisions` (L399–453) | **Historical layout adoption** — find the revision whose non-marker text is *identical* to the current paragraph and adopt its layout | identical non-marker text means the substitution can change only emphasis and whitespace |
| 2 | `whitespace_edits`, `fix_ws`, `fix_block`, `split_cells` (L246–317) | **Cell-aware flanking repair** — move whitespace outside each marker pair; repair table rows cell by cell | whitespace-only edits; GFM parses a pipe row cell by cell, so that is the correct unit |
| 3 | `marker_edits`, `repair_marker`, `sentence_stops`, `word_starts` (L319–397) | **Renderer-validated marker repair** — re-insert a deleted marker, or split a fused run | every candidate is scored by actually rendering the document |

Phase 1 excludes commit `ef645ce` explicitly: that commit's layout came from a broken fixer that
relocated markers to the wrong places, so it is not trustworthy ground truth even where its
non-marker text happens to match.

### 6.2.1 Phase 3, in full (added v1.4 per the n19 review)

The n19 review asked for the Phase 3 implementation to be shown, so a reviewer can verify the
"re-insert a deleted marker, or split a fused run" logic instead of taking it on trust. This is
`scripts/fix_markup.py` lines 319–397, verbatim:

```python
# ------------------------------------------------------------------ phase 3

def sentence_stops(text):
    """Offsets just after a sentence terminator, ignoring known abbreviations."""
    abbrev = ('Eq.', 'Fig.', 'Sec.', 'Ref.', 'No.', 'vs.', 'i.e.', 'e.g.',
              'cf.', 'Dr.', 'Mr.', 'Ms.', 'St.', 'al.', 'approx.', 'resp.')
    out = []
    for m in re.finditer(r'[.!?](?=\s|$)', text):
        head = text[max(0, m.start() - 8):m.start() + 1]
        if any(head.endswith(a) for a in abbrev):
            continue
        out.append(m.end())
    return out


def word_starts(text):
    out = []
    for m in re.finditer(r'\S', text):
        p = m.start()
        if p > 0 and not text[p - 1].isspace():
            continue
        out.append(p)
    out.append(len(text))
    return out


def marker_edits(text):
    """Candidate marker edits: insert a missing '**', or split a fused run.

    A fused run is a '*' run of length >= 3, e.g. '***' or '****'. Splitting
    it means deleting the surplus stars, which is a marker-only change.
    """
    out = []
    # split fused runs
    for s, e in marker_runs(text):
        n = e - s
        if n > 2:
            # delete n-2 surplus stars, keeping the first two
            for k in range(s + 2, e):
                out.append((k, k + 1, ''))
    # insert a missing marker
    for p in word_starts(text):
        if p in (0, len(text)):
            continue
        out.append((p, p, '**'))
    return out


def repair_marker(text):
    """Repair a paragraph that still renders with a literal '**'.

    Candidates are scored by the renderer. Ties are broken by preferring a
    sentence-boundary insertion and then the SHORTEST resulting bold span,
    because the paper's emphasis is overwhelmingly on short labels.
    """
    base = score(text)
    if base[0] == 0:
        return text, False

    stops = set(sentence_stops(text))

    cands = []
    for a, b, rep in marker_edits(text):
        trial = apply_edits(text, [(a, b, rep)])
        if tokens(trial) != tokens(text):
            continue
        s = score(trial)
        if s[0] >= base[0] or s[1] > 0:
            continue
        spans = bold_spans(trial)
        longest = max((len(c) for c, _ in spans), default=0)
        is_stop = 1 if (rep == '**' and a in stops) else 0
        cands.append(((is_stop, longest, a), trial))

    if not cands:
        return text, False
    cands.sort(key=lambda x: x[0])
    return cands[0][1], True
```

**How the safety property is enforced here.** `marker_edits` proposes only **marker-only**
edits: deleting surplus `*` from a fused run, or inserting a `**` at a word start. The prose
between markers is never touched. Two independent checks then gate each candidate:

1. `tokens(trial) != tokens(text)` → **reject**. The word-token sequence must be identical, so
   a candidate can never alter a number, a unit or a word. This is invariant 1 applied locally,
   before the global check.
2. `s[0] >= base[0] or s[1] > 0` → **reject**. The candidate must strictly reduce the literal-`**`
   count *and* introduce no new bad span (a bold span crossing a code span, a table pipe or a
   paragraph break — invariant 5).

The tie-break `((is_stop, longest, a), trial)` prefers, in order: an insertion at a sentence
boundary, then the **shortest** resulting bold span, then the earliest position. The
shortest-span rule matters because the paper's emphasis is overwhelmingly on short labels
("**stale-value**", "**0 of 8**"); a candidate that bolds a whole sentence would also pass the
literal-count test and still be wrong. The `sentence_stops` helper exists because a naive
`[.!?]` scan treats `Eq.` and `Fig.` as sentence ends — the same class of bug that the
abandoned `fix_glued_markup.py` prototype hit.

**Phase count.** There are **three** phases, not four: `main()` runs exactly three passes
(L484 historical adoption, L504 flanking repair, L515 marker repair). An earlier draft of the report
and the script's own docstring said "four"; both were wrong and are corrected in v1.6 and in the
script.

**Note on the `word_starts` candidate set:** it proposes an insertion at *every* word start, so
the candidate space is O(words) per paragraph and O(words²) in trials. That is why Phase 3 is
scored by rendering and not by pattern matching — the renderer is the only thing that knows
whether a given insertion actually pairs the markers correctly.

### 6.3 The five hard invariants

The script **aborts rather than writing the file** if invariants 1–4 fail. Invariant 5 (span sanity)
is **advisory**: the script prints `WARN invariant 5: N bold spans cross …` and lists the offending
spans, but the write is gated only on `if lit or not stale_ok` — i.e. on invariants 3 and 4 — so a
non-zero span count is *reported*, not *enforced*:

1. **Token preservation** — the word-token sequence of the document is identical before and after.
2. **Text preservation** — the non-marker, non-whitespace text is identical before and after.
3. **Renderer oracle** — zero literal `**` survives CommonMark + GFM-table rendering.
4. **Stale-value inertness** — the occurrence count of 19 known-stale markers is unchanged.
5. **Span sanity** — no rendered bold span crosses a code span, a table pipe, or a paragraph break.

Invariant 1 is what makes the fix numerically inert **by construction** rather than by inspection.
Invariant 4 is what stops the fix from resurrecting pre-F1–F22 content — the exact failure mode of
the withdrawn v1.4 attempt.

### 6.4 Measured result on the pristine paper

| quantity | value |
|---|---|
| literal `**` before (CommonMark + GFM tables) | 179 |
| literal `**` after the three phases | 5-8 |
| damaged paragraphs fully clean | 47 of 54 |
| invariant 1 (token identity) | **green** — 61,968 tokens, unchanged |
| invariant 2 (non-marker text identity) | **green** — 284,750 chars, unchanged |
| invariant 4 (stale-value counts) | **green** — all 19 markers unchanged |

### 6.5 Why the residue is not auto-fixable

The handful of remaining paragraphs are ones whose **text was edited after the damage occurred**,
so no clean historical twin exists for them and the authorial intent for the missing marker cannot
be recovered mechanically — it has to be judged. The script deliberately does not guess.

### 6.6 Files removed in this correction

| file | why removed |
|---|---|
| `scripts/fix_direct.py` | the fixer from the withdrawn v1.4 attempt. Not reproducible: run independently on pristine input it yields 111 lines with a literal `**`, worse than the 70 of the original, because it depends on a deleted multi-stage pipeline. |
| `scripts/fix_glued_markup.py` | early prototype of the same withdrawn attempt (sentence-end closer heuristic). Superseded by `scripts/fix_markup.py`. |

### 6.7 Paper restoration

`v0.3-prelim/docs/PAPER_V1_DRAFT.md` is restored **byte-for-byte** to the pristine `ef645ce^`
state (2,383 lines, 61,968 tokens). Verified with `diff` against `git show ef645ce^:<path>` — no
output. The invalid commit `ef645ce` remains in history (audit trail preserved) but is superseded.

---

## 7. PDF-render defect fixes — `scripts/build_round5_report_pdfs.py` (added v1.4)

Added in response to the n19 review's item 6 ("check PDF rendering integrity"). The n19
reviewer read the v1.5 PDF pair and reported that "§0 TL;DR is truncated, cut off after
'Strata /'". **That specific claim is a misread** — §0 is complete on page 1. But checking it
properly found **three real bugs in this project's own PDF builder**, each of which silently
**lost** content. The class is the same one this project already has a name for: *the pipeline
reports success while the artifact is wrong*.

| # | defect | root cause | how many | how it was found |
|---|---|---|---|---|
| **D1** | CJK ideographs rendered as **empty boxes** | DejaVu Sans has **no** CJK glyphs. The Chinese characters quoting the n18 review became `.notdef` — a null byte in the content stream, a blank box on the page. Text extraction returned the null byte too, so a box-count check passes while the text is gone. | **26 chars** (report pp. 7–8) | counted every non-ASCII character in both documents and checked it against the actual cmap of each registered face |
| **D2** | long code lines **clipped off the page** | reportlab's `Preformatted` does **not** wrap: the line is drawn past the frame edge and truncated, so its tail vanishes from the page **and** from text extraction, with no warning. | **34 lines** (companion; longest 867 chars) | word-level containment test of every source block against the extracted PDF text |
| **D3** | a paragraph **split mid-sentence** | the paragraph gatherer treated any line starting with `-` or `*` as a structural break, so a wrapped line like `*mechanism* — the band is …` was detached from the paragraph above it | 13 (report) + 15 (companion) | same containment test, then a page render |

**D3 is very likely what the n19 reviewer saw as "truncated"** — a visible blank gap in the
middle of the TL;DR paragraph. It is worth recording that the reviewer's inference ("check PDF
rendering integrity") was the right instruction even though the specific observation was
wrong.

### 7.1 The fixes

| fix | change | why |
|---|---|---|
| **F-CJK** | register a CJK face (`find_cjk()` → `C:/Windows/Fonts/simhei.ttf`, which covers all 26 characters) and wrap CJK runs in it via `wrap_cjk()` | without a fallback face the characters are not merely ugly — they are **absent** |
| **F-WRAP** | `wrap_code_lines()` hard-wraps code at `CODE_WRAP = 108` columns, breaking at a space where one exists | `Preformatted` clips; every source character must survive, so the break must not delete a space |
| **F-PARA** | the paragraph gatherer's `is_block()` now treats `-`/`*`/`+` as structural **only when followed by a space** (a real bullet), with horizontal rules handled explicitly | a wrapped line may legitimately begin with `*` |
| **F-MONO** | `fold_mono()` substitutes ASCII for `≪` (U+226A) | DejaVu Sans Mono lacks it although DejaVu Sans has it — one glyph was `.notdef` in a code block |

### 7.2 Verification of the rebuilt PDFs

Every source block was checked against the extracted PDF text **word by word**, which is
stronger than a glyph-count check and would have caught all three defects:

| check | report | companion |
|---|---|---|
| source blocks missing from the PDF | **0 of 695** | **0 of 884** |
| `.notdef` null bytes | **0** | **0** |
| box glyphs (`■` / `□`) | **0** | **0** |
| CJK rendered and readable | **27 chars** (visual, p. 7) | n/a |
| §0 TL;DR is one continuous paragraph | **yes** (visual, p. 1) | — |
| code blocks wrap with no clipping | — | **yes** (visual, p. 9) |

### 7.3 The generalisable lesson

A PDF that is *missing* content and a PDF that is *wrong* look the same to every check that
reads text: both are "the bytes that are there". The three checks that caught this — per-glyph
cmap coverage, word-level source↔PDF containment, and rasterising the page and **looking** at
it — are now the required gate for any PDF deliverable in this project. Text extraction alone
is not sufficient, and neither is a box-glyph count.
