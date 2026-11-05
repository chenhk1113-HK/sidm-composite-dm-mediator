"""t120_cloud9_bound.py — re-derive the Cloud-9 cross-section bound from the source papers.

Why this file exists
--------------------
The T120 joint fit grades the Cloud-9 channel against `sigma_eff(v=28) >= 100 cm^2/g`, and the
T205 published-likelihood channel list carries `(28.0, 128.0, 30.0, 'floor', 'Cloud-9 v=28',
'BLN24 / Ohana+ 2026')`. Neither number is a published measurement. This producer measures what
the model actually gives, in every convention the repo uses, and records what the cited papers
actually publish, with the PDF line each value came from.

Measured model quantities at v = 28 km/s
  Q_total   : five-peak T120.4 parameter set, sigma_0 * (100/v)^a + sum Gaussian peaks
  Q_canonic : the paper's canonical Gaussian convention (sigma_peak 174 at 29.4, w 4.4)
  Q_effective : f_H^2 * Q_total, the quantity T120.4 actually compares to the 100 bar
              (f_H = 0.7501856 for a core-forming halo at r = 0.05 r_vir)

Published anchors (read from the local PDFs, `pdftotext` line numbers quoted)
  Elbert+ 2015  arXiv:1412.1477  : 0.5-50 cm^2/g alleviates TBTF; 5-10 gives the largest,
                                  lowest-density cores; the 50 cm^2/g run shows mild core
                                  collapse; "cross sections as large or larger than 50 cm^2/g
                                  remain viable" at v_rms ~ 40 km/s. A viability demonstration,
                                  not a required floor.
  BLN24         arXiv:2406.18643  : models Cloud-9 as a CDM (NFW) RELHIC, M200 = 4-6e9 Msun,
                                  cNFW = 10-17, "all consistent with the CDM mass-concentration
                                  relation". Contains no self-interaction cross section at all.
  Ohana+ 2026   arXiv:2608.04362  : cross-section posterior peaks at ~200 cm^2/g and "disfavors
                                  both very small and very large cross sections"; concentration
                                  deviation minimised at ~3 sigma for sigma/m ~ 200; SIDM
                                  concentration posterior peaks 3.3 sigma below the cosmological
                                  median; CDM requires 7.3 sigma (>6.7 sigma allowing for fit
                                  uncertainty); a tau-based inference gives 483 cm^2/g.

Verdict this producer encodes: no source publishes a 100 cm^2/g floor or a 128 +/- 30 cm^2/g
Cloud-9 measurement. Both are project-internal anchors. The published preferred region peaks near
200 cm^2/g, which the framework's Q_total sits inside.
"""
from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path

_CODE_DIR = Path(__file__).resolve().parent
if str(_CODE_DIR) not in sys.path:
    sys.path.insert(0, str(_CODE_DIR))

_RESULTS_DIR = _CODE_DIR.parent / "data" / "results"
ARTIFACT = _RESULTS_DIR / "t120_cloud9_bound_rederivation.json"

# The repo has TWO files named `constants.py` (root layer and scripts/ layer) that define
# different values for the same flat name.  Loading the scripts layer under a PRIVATE module
# name (importlib, not `import constants`) is the only way to compare them deterministically;
# a plain `import constants` resolves by sys.path order and has already produced bugs here.
_SCRIPTS_CONSTANTS_PATH = _CODE_DIR.parent.parent / "scripts" / "constants.py"


def _load_scripts_constants():
    spec = importlib.util.spec_from_file_location("_scripts_constants_layer", _SCRIPTS_CONSTANTS_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

import t120_4_joint_fit as T120  # noqa: E402
from phase44_two_component import f_H_at_r  # noqa: E402

V_CLOUD9_KMS = 28.0
INTERNAL_BAR_CM2_PER_G = 100.0  # T120.4 grade line; project-internal
INTERNAL_T205_ANCHOR_CM2_PER_G = 128.0
INTERNAL_T205_ANCHOR_UNC_CM2_PER_G = 30.0
HALO_TYPE = "core_forming"
R_OVER_RVIR = 0.05

PUBLISHED = {
    "elbert_2015": {
        "arxiv": "1412.1477",
        "pdf_lines_quoted": [13, 14, 44, 96, 205],
        "what_it_publishes": [
            "sigma/m = 0.5-50 cm^2/g alleviates TBTF and produces 300-1000 pc cores",
            "largest, lowest-density cores at sigma/m = 5-10 cm^2/g",
            "the 50 cm^2/g run is denser in its core than the 5 cm^2/g run: mild core collapse",
            "cross sections as large or larger than 50 cm^2/g remain viable at v_rms ~ 40 km/s",
            "the viable range spans at least two orders of magnitude: no fine-tuning",
        ],
        "is_100_a_floor_in_this_paper": False,
        "role_of_50": "largest simulated cross section / mild-collapse onset, plus a viability statement",
    },
    "benitez_llambay_2024_bln24": {
        "arxiv": "2406.18643",
        "pdf_lines_quoted": [263, 319],
        "what_it_publishes": [
            "Cloud-9 modelled as a CDM (NFW) RELHIC in hydrostatic + UVB thermal equilibrium",
            "M200 in 4-6 x 10^9 Msun and cNFW in 10-17, 'all consistent with the CDM "
            "mass-concentration relation'",
            "W50 = 12 km/s line profile",
        ],
        "contains_any_self_interaction_cross_section": False,
        "grep_evidence": "0 occurrences of 'sigma' and 0 of 'SIDM'/'self-interact' in the extracted text",
        "is_128_or_100_from_this_paper": False,
    },
    "ohana_2026": {
        "arxiv": "2608.04362",
        "pdf_lines_quoted": [253, 356, 404, 464],
        "what_it_publishes": [
            "cross-section posterior is right-skewed log-normal peaking around 200 cm^2/g",
            "the posterior 'disfavors both very small and very large cross sections'",
            "concentration deviation minimised at ~3 sigma below the median at sigma/m ~ 200 cm^2/g",
            "SIDM concentration posterior peaks 3.3 sigma below the cosmological median",
            "CDM requires 7.3 sigma below the median, still >6.7 sigma allowing for fit uncertainty",
            "a tau-based inference quotes sigma/m = 483 cm^2/g",
        ],
        "is_100_a_floor_in_this_paper": False,
        "published_preferred_region_cm2_per_g": [50.0, 500.0],
        "published_posterior_peak_cm2_per_g": 200.0,
        "caveat": "concentration is constrained only through the cosmological c-M prior; the gas "
                  "profile alone is degenerate between CDM and SIDM",
    },
}


def model_quantities(a_slope=None):
    """Return the three Cloud-9 quantities the repo actually computes at v = 28 km/s."""
    p44 = T120._load_phase44_params()
    a = p44["a_slope"] if a_slope is None else a_slope
    q_total = T120.total_sigma_m_gaussian(
        V_CLOUD9_KMS, T120.T120_4_V_TARGETS, T120.T120_4_SIGMA_PEAKS,
        T120.T120_4_W_LIST_DEFAULT, p44["sigma_0"], a,
    )
    q_canonic = (
        174.0 * math.exp(-(V_CLOUD9_KMS - 29.4) ** 2 / (2 * 4.4 ** 2))
        + 0.052 * (100.0 / V_CLOUD9_KMS) ** 1.93
    )
    f_h = f_H_at_r(R_OVER_RVIR, HALO_TYPE)
    q_effective = T120.sigma_eff_two_comp(V_CLOUD9_KMS, q_total, HALO_TYPE, R_OVER_RVIR)
    return {
        "a_slope": a,
        "sigma_0_cm2_per_g": p44["sigma_0"],
        "Q_total_cm2_per_g": q_total,
        "Q_canonical_gaussian_cm2_per_g": q_canonic,
        "Q_effective_fH_squared_cm2_per_g": q_effective,
        "f_H": f_h,
        "f_H_squared": f_h * f_h,
        "margin_vs_internal_bar_pct": {
            "Q_total": (q_total - INTERNAL_BAR_CM2_PER_G) / INTERNAL_BAR_CM2_PER_G * 100.0,
            "Q_canonical": (q_canonic - INTERNAL_BAR_CM2_PER_G) / INTERNAL_BAR_CM2_PER_G * 100.0,
            "Q_effective": (q_effective - INTERNAL_BAR_CM2_PER_G) / INTERNAL_BAR_CM2_PER_G * 100.0,
        },
    }


def f_H_conventions(q_total_default: float) -> dict:
    """The same physical quantity, sigma_eff = f_H^2 * sigma/m, has TWO live values in this repo.

    Measured, not asserted: both are read from the files that define them.
    """
    live_f_h = f_H_at_r(R_OVER_RVIR, HALO_TYPE)          # used by every T120 entry point
    scripts_layer = _load_scripts_constants()
    legacy_f_h = scripts_layer.F_H                        # scripts/constants.py: F_H_PLACEHOLDER_G7
    return {
        "quantity": "f_H (heavy fraction entering sigma_eff = f_H^2 * sigma/m)",
        "live_value_used_by_t120": {
            "value": live_f_h,
            "f_H_squared": live_f_h * live_f_h,
            "defined_in": "v0.3-prelim/code/phase44_two_component.py::f_H_at_r",
            "provenance_claimed_in_code": "Yang+ 2025 PRD 112, 083011 (arXiv:2504.02303) Fig. 2 profile",
            "consumers": ["t120_4_joint_fit.sigma_eff_two_comp", "t120_constraint_scoreboard",
                          "t120_cloud9_bound"],
            "cloud9_Q_effective_cm2_per_g": live_f_h * live_f_h * q_total_default,
        },
        "legacy_value_still_in_live_code": {
            "value": legacy_f_h,
            "f_H_squared": legacy_f_h * legacy_f_h,
            "defined_in": "scripts/constants.py (F_H_CANONICAL / F_H_PLACEHOLDER_G7 / F_H alias)",
            "provenance_claimed_in_code": "labelled in-file 'v1.13 / Phase G7 placeholder (retracted "
                                          "v18.29)' and 'DEPRECATED'; phase_g4_pipeline.py calls the "
                                          "same number 'Yang+ 2025-derived f_H'",
            "consumers": ["phase44_joint_fit_v2_real_likelihood.py:140 (sigma_eff = F_H**2 * sigma_HH)",
                          "phase_g4_pipeline.py:144 (sigma_eff = F_H**2 * sigma_mb)",
                          "scripts/canonical_numbers.py header ('canonical F_H = 0.297')"],
            "cloud9_Q_effective_cm2_per_g": legacy_f_h * legacy_f_h * q_total_default,
        },
        "ratio_between_conventions": (live_f_h * live_f_h) / (legacy_f_h * legacy_f_h),
        "finding": "F23: the Cloud-9 `>= 100 cm^2/g` verdict depends on WHICH f_H is used. "
                   "The two-component live path gives a pass; the deprecated 0.297 placeholder path "
                   "gives an effective cross section far below the bar. Both are in live code, one is "
                   "labelled retracted, and neither producer declares which convention it used.",
        "status": "UNRESOLVED_CONVENTION_SPLIT",
    }


def build_report():
    arms = {}
    for label, a in [("default_phase44", None), ("a_slope_1.0", 1.0), ("a_slope_0.8", 0.8),
                     ("a_slope_0.5", 0.5)]:
        arms[label] = model_quantities(a)

    default = arms["default_phase44"]
    return {
        "velocity_kms": V_CLOUD9_KMS,
        "internal_bar": {
            "value_cm2_per_g": INTERNAL_BAR_CM2_PER_G,
            "used_by": ["t120_4_joint_fit.joint_fit_evaluation", "t120_constraint_scoreboard",
                        "T205_full_likelihood_published channel list uses 128 +/- 30"],
            "provenance": "project-internal working anchor (labelled in the paper as 'Elbert+ 2015 "
                          "[55a] working benchmark'); NOT a published lower bound",
            "status": "INTERNAL",
        },
        "internal_t205_anchor": {
            "value_cm2_per_g": INTERNAL_T205_ANCHOR_CM2_PER_G,
            "uncertainty_cm2_per_g": INTERNAL_T205_ANCHOR_UNC_CM2_PER_G,
            "citation_label_in_code": "BLN24 / Ohana+ 2026",
            "status": "MISATTRIBUTED",
            "finding": "neither cited paper publishes a Cloud-9 cross section: BLN24 contains none, "
                       "Ohana+ 2026 publishes a posterior peaked near 200 cm^2/g with no floor",
        },
        "published_anchors": PUBLISHED,
        "model_values_by_arm": arms,
        "f_H_conventions": f_H_conventions(default["Q_total_cm2_per_g"]),
        "conventions": {
            "quantity_graded_against_100_in_t120_4": "Q_effective_fH_squared",
            "quantity_the_paper_quotes_as_166": "Q_canonical_gaussian",
            "convention_factor": 1.0 / default["f_H_squared"],
            "note": "the same model differs by a factor ~1.78 between the quantity the paper quotes "
                    "as passing (canonical 166) and the quantity the joint fit grades (effective ~100); "
                    "that factor dwarfs the 0.2% near-miss",
        },
        "verdict": {
            "against_internal_bar_100": {
                "Q_total": "passes by "
                           f"{default['margin_vs_internal_bar_pct']['Q_total']:.1f}%",
                "Q_canonical": "passes by "
                               f"{default['margin_vs_internal_bar_pct']['Q_canonical']:.1f}%",
                "Q_effective": "near-miss, "
                               f"{default['margin_vs_internal_bar_pct']['Q_effective']:+.2f}%",
            },
            "against_published_posterior_peak_200": (
                "Q_total sits inside the published preferred region (peak ~200, broad intermediate "
                "range, both tails penalised); no published floor is crossed"
            ),
            "honest_limit": "this shows the model is consistent with the published Cloud-9 inference, "
                            "not that Cloud-9 confirms the model: the published constraint is weak, "
                            "prior-driven, and the profile alone does not discriminate CDM from SIDM",
        },
    }


def main():
    report = build_report()
    _RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(ARTIFACT, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
    print(f"wrote {ARTIFACT}")
    d = report["model_values_by_arm"]["default_phase44"]
    print(f"  Q_total(v=28)        = {d['Q_total_cm2_per_g']:.2f} cm^2/g")
    print(f"  Q_canonical          = {d['Q_canonical_gaussian_cm2_per_g']:.2f} cm^2/g")
    print(f"  Q_effective (f_H^2)  = {d['Q_effective_fH_squared_cm2_per_g']:.2f} cm^2/g "
          f"(f_H = {d['f_H']:.4f})")
    print("  published: Ohana+ 2026 posterior peak ~200 cm^2/g; no 100 or 128 +/- 30 published")


if __name__ == "__main__":
    main()
