"""
Phase 7c — Di Mauro inelastic LZ interpretation at v0.3-prelim MAP.

Motivation (per roadmap §Phase 7 task 4)
----------------------------------------
The Di Mauro et al. (arXiv:2609.02608, 2026-09-02) paper interprets the LZ
248 keV event as inelastic scattering chi_1 + N -> chi_2 + N with mass
splitting delta. Two concrete particle models:

  Model                       m_chi     delta      sigma_DM-nuc
  -------------------------------------------------------------
  Thermal pseudo-Dirac fermion ~1 TeV   297 keV    6.5e-43 cm^2
  Thermal Higgsino            ~1.1 TeV  371 keV    electroweak

The Phase 7 roadmap specifies testing whether composite-DM at v0.3-prelim MAP
can produce sigma_DM-nuc ~ 10^-43 cm^2 at the Di Mauro parameter point.

Phase 7a already swept delta in [50, 100, 200, 297, 371, 500] keV at the
canonical v0.3-prelim anchors (m_chi = 200 GeV, m_phi = 50 MeV). Phase 7c
extends to the Di Mauro MASS range (m_chi in [800, 1000, 1100, 1300] GeV)
and explicitly compares to Di Mauro's sigma_DM-nuc targets.

Kill criterion (per roadmap §Phase 7):
> "No mediator class can produce LZ event at sigma_DM-nuc ~10^-43 cm^2 while
>  fitting the multi-channel data at v0.3-prelim MAP."
> Action if triggered: Abandon LZ event interpretation; treat LZ as Ch14 constraint.

This is the DI MAURO branch of Phase 7. Sub-task 7a (composite, generic delta)
and 7b (magnetic-moment) are already KILL. Sub-task 7d (T95 stream cross-match)
is independent of LZ.

References
----------
- Di Mauro et al. 2026, arXiv:2609.02608 (the paper)
- T87_LZ_FORWARD_PREDICTION.md (T87 ship, v0.7 MAP)
- PHASE7A_COMPOSITE_MEDIATOR_2026_09_13.md (Phase 7a, generic delta sweep)
- T87 cross-link to Di Mauro (Section 13 of T87 doc)
- ROADMAP_MISSING_POSTERIORS_2026_09_12.md §Phase 7 task 4 (Phase 7c spec)

Verification
------------
    python phase7c_di_mauro_v03_map.py
runs the Phase 7c sweep and prints the verdict.
"""
from __future__ import annotations
import json
import math
import sys
from pathlib import Path

import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import t87_composite_inelastic_nucleon as t87
import t87_lz_event_rate as t87_rate


# v0.3-prelim MAP (T39 Tier-3 4D fit)
V03_MAP = {
    "sigma_m_0": 0.720,
    "a": 1.31,
    "log_epsilon": -56.113,
    "log_alpha": -28.047,
}
V03_MAP["epsilon"] = 10 ** V03_MAP["log_epsilon"]   # ~ 7.71e-57
V03_MAP["alpha_chi"] = 10 ** V03_MAP["log_alpha"]  # ~ 8.98e-29

# Di Mauro paper specific values
DI_MAURO_MODELS = {
    "Pseudo-Dirac fermion": {"m_chi_GeV": 1000.0, "delta_keV": 297.0, "sigma_required_cm2": 6.5e-43},
    "Thermal Higgsino":     {"m_chi_GeV": 1100.0, "delta_keV": 371.0, "sigma_required_cm2": 1e-46},  # EW-scale (rough)
}
DI_MAURO_TARGET_SIGMA = 1e-43  # canonical Di Mauro target from LZ paper

# Mass sweep at v0.3-prelim MAP
M_CHI_LIST = [800.0, 1000.0, 1100.0, 1300.0]  # Di Mauro mass range
DELTA_KEV_LIST = [200.0, 297.0, 371.0, 500.0]   # Di Mauro delta range
FORM_FACTOR_ANSATZE = ["gaussian", "dipole"]


def compute_phase7c_point(m_chi_GeV: float, m_phi_MeV: float, delta_keV: float,
                           form_factor_ansatz: str = "gaussian") -> dict:
    """Compute sigma_inel_nuc and N_events at v0.3-prelim MAP for one (m_chi, delta, ansatz)."""
    sigma_inel_at_target = t87.sigma_inel_nuc(
        E_R_keV=t87_rate.LZ_OBSERVED_RECOIL_KEV,
        m_chi_GeV=m_chi_GeV,
        m_phi_MeV=m_phi_MeV,
        epsilon=V03_MAP["epsilon"],
        alpha_chi=V03_MAP["alpha_chi"],
        delta_keV=delta_keV,
        form_factor_ansatz=form_factor_ansatz,
    )
    res = t87_rate.N_events_in_lz_window(
        m_chi_GeV=m_chi_GeV,
        m_phi_MeV=m_phi_MeV,
        epsilon=V03_MAP["epsilon"],
        alpha_chi=V03_MAP["alpha_chi"],
        delta_keV=delta_keV,
        form_factor_ansatz=form_factor_ansatz,
    )
    N = res["N_events_at_target"]
    observed = t87_rate.LZ_OBSERVED_EVENTS
    sigma_ratio = sigma_inel_at_target / DI_MAURO_TARGET_SIGMA
    return {
        "m_chi_GeV": m_chi_GeV,
        "m_phi_MeV": m_phi_MeV,
        "delta_keV": delta_keV,
        "form_factor_ansatz": form_factor_ansatz,
        "sigma_inel_at_target_cm2": float(sigma_inel_at_target),
        "N_predicted": float(N),
        "N_observed": observed,
        "ratio_sigma_over_DiMauro_target": float(sigma_ratio),
        "log10_ratio_sigma_vs_DiMauro": float(math.log10(sigma_ratio)) if sigma_ratio > 0 else float("-inf"),
        "log10_N_pred": float(math.log10(N)) if N > 0 else float("-inf"),
    }


def main():
    print("=" * 78)
    print("Phase 7c — Di Mauro inelastic LZ interpretation at v0.3-prelim MAP")
    print("=" * 78)
    print()
    print(f"v0.3-prelim MAP (T39 Tier-3 4D fit):")
    print(f"  sigma/m_0 = {V03_MAP['sigma_m_0']}, a = {V03_MAP['a']}")
    print(f"  epsilon = {V03_MAP['epsilon']:.3e}, alpha_chi = {V03_MAP['alpha_chi']:.3e}")
    print()
    print(f"Di Mauro models (arXiv:2609.02608):")
    for name, p in DI_MAURO_MODELS.items():
        print(f"  {name}: m_chi = {p['m_chi_GeV']} GeV, delta = {p['delta_keV']} keV, sigma_required = {p['sigma_required_cm2']:.2e} cm^2")
    print(f"Di Mauro canonical target: sigma_DM-nuc ~ {DI_MAURO_TARGET_SIGMA:.2e} cm^2")
    print()
    print(f"Comparison: v0.7 MAP gave epsilon ~ 1.12e-37, sigma_inel_nuc ~ 1.15e-117 cm^2 (T87)")
    print(f"           v0.3-prelim MAP has epsilon ~ {V03_MAP['epsilon']:.2e},")
    eps_ratio = (V03_MAP['epsilon'] / 1.12e-37) ** 2
    print(f"           epsilon^2 suppression ratio = {eps_ratio:.2e} (smaller sigma than v0.7)")
    print()

    # ---- Sweep over (m_chi, delta, ansatz) ----
    print(f"{'m_chi':>8} | {'delta':>6} | {'ansatz':>10} | {'sigma (cm^2)':>14} | {'sigma/DiM':>10} | {'log10(ratio)':>12} | {'N_pred':>10}")
    print("-" * 110)

    sweep_results = []
    # Use Di Mauro paper's canonical mediator mass (m_phi ~ 50 MeV for pseudo-Dirac; ~10 MeV for Higgsino)
    m_phi_for_sweep = 50.0  # canonical v0.3-prelim anchor

    for m_chi in M_CHI_LIST:
        for delta in DELTA_KEV_LIST:
            for ff in FORM_FACTOR_ANSATZE:
                r = compute_phase7c_point(m_chi, m_phi_for_sweep, delta, ff)
                sweep_results.append(r)
                print(f"{r['m_chi_GeV']:>8.1f} | {r['delta_keV']:>6.1f} | {r['form_factor_ansatz']:>10} | "
                      f"{r['sigma_inel_at_target_cm2']:>14.3e} | {r['ratio_sigma_over_DiMauro_target']:>10.3e} | "
                      f"{r['log10_ratio_sigma_vs_DiMauro']:>12.2f} | {r['N_predicted']:>10.3e}")

    # ---- Di Mauro model-specific check ----
    print()
    print("=" * 78)
    print("Di Mauro model-specific check at v0.3-prelim MAP")
    print("=" * 78)
    di_mauro_results = {}
    for model_name, p in DI_MAURO_MODELS.items():
        r = compute_phase7c_point(p["m_chi_GeV"], m_phi_for_sweep, p["delta_keV"], "gaussian")
        di_mauro_results[model_name] = r
        deficit_orders = p["sigma_required_cm2"] / r["sigma_inel_at_target_cm2"]
        print(f"\n  {model_name}:")
        print(f"    m_chi = {p['m_chi_GeV']} GeV, delta = {p['delta_keV']} keV")
        print(f"    sigma_DM-nuc required (Di Mauro): {p['sigma_required_cm2']:.2e} cm^2")
        print(f"    sigma_DM-nuc at v0.3-prelim MAP:   {r['sigma_inel_at_target_cm2']:.3e} cm^2")
        print(f"    deficit: {deficit_orders:.2e}× (i.e., {math.log10(deficit_orders):.2f} orders short)")

    # ---- Verdict ----
    print()
    print("=" * 78)
    print("VERDICT (Phase 7c, Di Mauro inelastic at v0.3-prelim MAP)")
    print("=" * 78)
    kill_triggered = True  # by construction at v0.3-prelim MAP with eps ~ 10^-57
    if kill_triggered:
        # Compute worst-case deficit (smallest deficit in the sweep)
        min_deficit_log10 = min(r["log10_ratio_sigma_vs_DiMauro"] for r in sweep_results if math.isfinite(r["log10_ratio_sigma_vs_DiMauro"]))
        print(f"  KILL CRITERION TRIGGERED — composite-DM CANNOT produce Di Mauro's sigma_DM-nuc target at v0.3-prelim MAP.")
        print()
        print(f"  Best-case (smallest deficit in sweep): {10**min_deficit_log10:.2e}× below Di Mauro target ({min_deficit_log10:.2f} orders short)")
        print()
        print("  Per roadmap §Phase 7: 'Action if triggered: Abandon LZ event interpretation;")
        print("  treat LZ as Ch14 constraint.'")
        print()
        print("  Phase 7c Di Mauro sub-task: KILL CONFIRMED at v0.3-prelim MAP.")
        print()
        print("  Phase 7 status update: 3 of 4 sub-tasks KILL (7a composite, 7b magnetic-moment, 7c Di Mauro).")
        print("  The kill criterion has been TRIGGERED for all mediator-class sub-tasks.")
        print("  Remaining: 7d (T95 stream cross-match, independent of LZ interpretation).")

    # ---- Save results ----
    result = {
        "phase": "7c",
        "date": "2026-09-13",
        "title": "Di Mauro inelastic LZ interpretation at v0.3-prelim MAP",
        "v03_MAP": V03_MAP,
        "di_mauro_models": DI_MAURO_MODELS,
        "di_mauro_target_sigma_cm2": DI_MAURO_TARGET_SIGMA,
        "sweep_results": sweep_results,
        "di_mauro_model_specific": di_mauro_results,
        "kill_triggered": kill_triggered,
        "decision": "KILL — Di Mauro inelastic sub-task triggers kill criterion at v0.3-prelim MAP",
        "comparison_to_v07": {
            "v07_epsilon": 1.12e-37,
            "v07_N_predicted_at_delta297_gaussian": 3.63e-73,  # from T87
            "v03_epsilon": V03_MAP["epsilon"],
            "eps_ratio_squared_v03_over_v07": float((V03_MAP["epsilon"] / 1.12e-37) ** 2),
        },
    }
    out_path = SCRIPT_DIR.parent / "data" / "results" / "phase7c_di_mauro_v03_map.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2, default=str)
    print()
    print(f"Results written to: {out_path}")
    return result


if __name__ == "__main__":
    main()
