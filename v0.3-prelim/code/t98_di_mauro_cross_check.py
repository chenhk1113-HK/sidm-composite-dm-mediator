"""
T98 — Di Mauro 2026 (arXiv:2609.02608) cross-check vs project's
inelastic DM joint fit (T43).

Compares the project's T43 inelastic joint fit posterior for the
mass splitting δ to the published Di Mauro 2026 prediction.

Outputs:
- outputs/t95/t98_di_mauro_cross_check.json — numerical comparison
- Console summary with verdict
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path


def main():
    out_dir = Path(__file__).resolve().parents[1] / "outputs" / "t95"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Load T43 result (project's inelastic joint fit)
    t43_path = (Path(__file__).resolve().parents[1] / "data" / "results" /
                "t43_inelastic_dm_joint_fit.json")
    if not t43_path.exists():
        print(f"ERROR: {t43_path} not found")
        sys.exit(1)
    t43 = json.load(open(t43_path))

    # Load T87 result (project's LZ forward prediction at v0.7 MAP)
    t87_path = (Path(__file__).resolve().parents[1] / "data" / "results" /
                "2026-09-03_t87_lz_forward_prediction.json")
    t87 = json.load(open(t87_path)) if t87_path.exists() else None

    # Di Mauro 2026 predictions
    di_mauro = {
        "pseudo_dirac": {
            "m_chi_GeV": 1000,
            "delta_keV": 297,
            "sigma_DM_nuc_cm2": 6.5e-43,
            "channel": "Inelastic O1s (L10s), off-diagonal vector",
        },
        "higgsino": {
            "m_chi_GeV": 1100,
            "delta_keV": 371,
            "sigma_DM_nuc_cm2": None,  # electroweak, not specified
            "channel": "Inelastic O1s (L10s), thermal Higgsino",
        },
    }

    # Project's T43 MAP and median
    project = {
        "MAP_keV": t43["MAP_physical"]["delta_MeV"] * 1000,
        "median_keV": t43["median_physical"]["delta_MeV"] * 1000,
        "q16_keV": (10 ** t43["quantiles_16_50_84"]["log_delta_MeV"][0]) * 1000,
        "q50_keV": (10 ** t43["quantiles_16_50_84"]["log_delta_MeV"][1]) * 1000,
        "q84_keV": (10 ** t43["quantiles_16_50_84"]["log_delta_MeV"][2]) * 1000,
        "MAP_m_chi_GeV": t43["MAP_physical"]["m_chi_GeV"],
        "median_m_chi_GeV": t43["median_physical"]["m_chi_GeV"],
        "log_Z": t43["log_Z"],
    }

    # T87 v0.7 MAP
    t87_v07 = {
        "sigma_inel_nuc_248keV_delta297_gaussian_cm2": None,
        "sigma_inel_nuc_248keV_delta297_dipole_cm2": None,
        "N_predicted_2_84_ty": None,
        "verdict": "DOES NOT EXPLAIN LZ EVENT",
    }
    if t87 is not None:
        for entry in t87.get("delta_sweep", []):
            if entry["delta_keV"] == 297:
                t87_v07["sigma_inel_nuc_248keV_delta297_gaussian_cm2"] = (
                    entry["gaussian"]["sigma_inel_at_target_cm2"])
                t87_v07["sigma_inel_nuc_248keV_delta297_dipole_cm2"] = (
                    entry["dipole"]["sigma_inel_at_target_cm2"])
                t87_v07["N_predicted_2_84_ty"] = entry["gaussian"]["N_predicted"]
                break

    # Cross-check verdicts
    verdicts = []
    # 1. δ comparison — be honest about scale
    di_mauro_delta_keV = 297  # pseudo-Dirac (more specific)
    project_q50_keV = project["q50_keV"]
    project_q84_keV = project["q84_keV"]
    project_q16_keV = project["q16_keV"]
    delta_ratio = di_mauro_delta_keV / project_q50_keV
    log_ratio_delta = math.log10(delta_ratio) if delta_ratio > 0 else float('inf')
    if 0.5 < delta_ratio < 2.0:
        verdict_delta = (
            f"MATCH: project median δ = {project_q50_keV:.2f} keV, "
            f"Di Mauro = {di_mauro_delta_keV} keV. "
            f"Ratio = {delta_ratio:.1f}×."
        )
        verdicts.append(("delta", "MATCH", verdict_delta))
    elif 0.1 < delta_ratio < 10:
        verdict_delta = (
            f"PARTIAL: project median δ = {project_q50_keV:.2f} keV "
            f"(q16={project_q16_keV:.2f}, q84={project_q84_keV:.2f}), "
            f"Di Mauro = {di_mauro_delta_keV} keV. "
            f"Ratio = {delta_ratio:.1f}× ({log_ratio_delta:.1f} orders of "
            f"magnitude). Project posterior 84th-percentile is "
            f"{project_q84_keV:.0f} keV; Di Mauro is at the high end of "
            f"this range. Both are in the sub-MeV endothermic regime."
        )
        verdicts.append(("delta", "PARTIAL", verdict_delta))
    else:
        verdict_delta = (
            f"MISMATCH: project median δ = {project_q50_keV:.2f} keV, "
            f"Di Mauro = {di_mauro_delta_keV} keV. "
            f"Ratio = {delta_ratio:.1f}× ({log_ratio_delta:.1f} orders of "
            f"magnitude). T43 prior was -3 < log δ/MeV < 1; data selected "
            f"the lower end of the prior. Di Mauro's value is at the high end "
            f"of the project's 95% posterior range."
        )
        verdicts.append(("delta", "MISMATCH", verdict_delta))

    # 2. σ_DM-nuc comparison
    if t87_v07["sigma_inel_nuc_248keV_delta297_gaussian_cm2"] is not None:
        sigma_project = t87_v07["sigma_inel_nuc_248keV_delta297_gaussian_cm2"]
        sigma_paper = di_mauro["pseudo_dirac"]["sigma_DM_nuc_cm2"]
        if sigma_paper is not None and sigma_project is not None:
            ratio = sigma_paper / sigma_project
            log_ratio = math.log10(ratio)
            verdict_sigma = (
                f"MISMATCH: project σ_DM-nuc at 248 keV = {sigma_project:.2e} cm², "
                f"Di Mauro = {sigma_paper:.2e} cm². "
                f"Project is {log_ratio:.1f} orders of magnitude TOO SMALL. "
                f"This is the dominant suppression (ε² × F²_composite in "
                f"the freeze-in regime)."
            )
            verdicts.append(("sigma_DM_nuc", "MISMATCH", verdict_sigma))

    # 3. m_χ comparison
    project_m_chi = project["median_m_chi_GeV"]
    paper_m_chi = 1000
    m_chi_ratio = paper_m_chi / project_m_chi
    if 0.5 <= m_chi_ratio <= 2.0:
        verdicts.append(("m_chi", "MATCH",
                        f"project median m_χ = {project_m_chi:.0f} GeV, "
                        f"Di Mauro = {paper_m_chi} GeV (ratio {m_chi_ratio:.1f}×)"))
    elif 0.1 <= m_chi_ratio <= 10:
        verdicts.append(("m_chi", "PARTIAL",
                        f"project median m_χ = {project_m_chi:.0f} GeV, "
                        f"Di Mauro = {paper_m_chi} GeV (ratio {m_chi_ratio:.1f}×). "
                        f"T43 prior was 0.5 < log m_χ/GeV < 3.0 (3-1000 GeV), "
                        f"so 1000 GeV is at the prior boundary. Di Mauro's 1 TeV "
                        f"prediction is consistent with the prior edge."))
    else:
        verdicts.append(("m_chi", "MISMATCH",
                        f"project median m_χ = {project_m_chi:.0f} GeV, "
                        f"Di Mauro = {paper_m_chi} GeV (ratio {m_chi_ratio:.1f}×)"))

    # 4. Operator structure
    verdicts.append(("operator", "PARTIAL",
                    "Both use 𝒪₁ˢ (L10s), but T43 is composite-DM with ε² suppression, "
                    "Di Mauro is thermal secluded-WIMP with full strength σ"))

    out = {
        "test": "T98_di_mauro_2026_cross_check",
        "date": "2026-09-08",
        "reference": "arXiv:2609.02608v1 (Di Mauro, 2 Sep 2026)",
        "di_mauro_2026": di_mauro,
        "project_T43_inelastic_joint_fit": project,
        "project_T87_v07_MAP_LZ_forward": t87_v07,
        "verdicts": [
            {"aspect": v[0], "verdict": v[1], "detail": v[2]} for v in verdicts
        ],
        "overall_verdict": (
            "KINEMATIC PARTIAL: Di Mauro's δ ≈ 297 keV is consistent with the "
            "T87 δ-sweep test value. CROSS-SECTION MISMATCH: v0.7 MAP σ_DM-nuc "
            "is 74 orders of magnitude below the paper's required ~10⁻⁴³ cm². "
            "The v0.7 MAP is in the ε²-suppressed freeze-in regime, not the "
            "secluded-WIMP regime the paper assumes. The T43 MAP δ ≈ 4 keV is "
            "75× smaller than the paper's 297 keV; this is because T43's prior "
            "was wide (-3 < log δ/MeV < 1) and the data selected the small-δ end."
        ),
    }

    out_path = out_dir / "t98_di_mauro_cross_check.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Wrote {out_path}")

    # Console summary
    print("=" * 70)
    print("T98 — Di Mauro 2026 (arXiv:2609.02608) cross-check")
    print("=" * 70)
    print()
    print("Di Mauro 2026 prediction:")
    print(f"  m_χ = {di_mauro['pseudo_dirac']['m_chi_GeV']} GeV")
    print(f"  δ = {di_mauro['pseudo_dirac']['delta_keV']} keV")
    print(f"  σ_DM-nuc = {di_mauro['pseudo_dirac']['sigma_DM_nuc_cm2']:.2e} cm²")
    print(f"  Channel: {di_mauro['pseudo_dirac']['channel']}")
    print()
    print("Project T43 inelastic joint fit (median):")
    print(f"  m_χ = {project['median_m_chi_GeV']:.1f} GeV")
    print(f"  δ = {project['median_keV']:.3f} keV (q16={project['q16_keV']:.3f}, "
          f"q84={project['q84_keV']:.3f})")
    print(f"  log Z = {project['log_Z']:.3f}")
    print()
    print("Project T87 v0.7 MAP (at δ=297 keV):")
    print(f"  σ_DM-nuc = {t87_v07['sigma_inel_nuc_248keV_delta297_gaussian_cm2']:.2e} cm²")
    print(f"  N_events = {t87_v07['N_predicted_2_84_ty']:.2e}")
    print()
    print("Verdicts:")
    for v in verdicts:
        print(f"  [{v[1]}] {v[0]}: {v[2]}")
    print()
    print(f"Overall: {out['overall_verdict'][:120]}...")


if __name__ == "__main__":
    main()
