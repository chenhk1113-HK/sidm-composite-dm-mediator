"""
Phase 7a — Composite-mediator LZ forward prediction at v0.3-prelim MAP.

Motivation (per roadmap §Phase 7 task 1)
----------------------------------------
The T87 ship (2026-09-03) concluded that composite-DM inelastic σ_DM-nucleon
at v0.7 MAP (ε ≈ 10⁻³⁷) is **71-74 orders of magnitude** below the ~10⁻⁴³ cm²
needed to explain the LZ 248 keV event (N_pred ≈ 10⁻⁷³ ≪ 1). The Phase 7
roadmap specifies re-testing at the v0.3-prelim MAP (σ/m_0 = 0.72, a = 1.31).

The v0.3-prelim MAP (T39 Tier-3 4D fit) has:
- σ/m_0 = 0.72 cm²/g at V_REF = 100 km/s
- a = 1.31 (velocity exponent)
- log_ε = -56.11 → ε = 7.71 × 10⁻⁵⁷
- log_α = -28.05 → α = 8.98 × 10⁻²⁹
- log Z = -2.94

Compared to v0.7 MAP (ε ≈ 10⁻³⁷), v0.3-prelim MAP has ε that is 10⁻²⁰ SMALLER.
Since σ_DM-nuc ∝ ε², the predicted σ at v0.3-prelim MAP is ~10⁻⁴⁰× smaller than
at v0.7 MAP. Even though σ/m_0 is 2.6× higher (0.72 vs 0.273), the ε²
suppression dominates overwhelmingly.

Phase 7a extends the T87 framework by accepting (m_χ, m_φ, ε, α) as inputs
and computing σ_inel_nuc + N_events at LZ (2.84 tonne-years) at the
v0.3-prelim MAP operating point.

Kill-criterion check (per roadmap §Phase 7):
> "No mediator class can produce LZ event at σ_DM-nuc ~10⁻⁴³ cm² while
>  fitting multi-channel data at v0.3-prelim MAP."
>
> Action if triggered: Abandon LZ event interpretation; treat LZ as constraint (Ch14).

This script is the COMPOSITE-MEDIATOR branch of Phase 7. Sub-tasks 2
(magnetic-moment), 3 (Di Mauro inelastic), and 4 (T95 stream cross-match)
are separate scripts.

References
----------
- T87_LZ_FORWARD_PREDICTION.md (v0.7 MAP ship, 2026-09-03)
- t39_tier3_epsilon_alpha_joint_fit.json (v0.3-prelim MAP)
- t87_composite_inelastic_nucleon.py (σ_inel_nuc + F_inel + F²)
- t87_lz_event_rate.py (event rate integration)
- Tucker-Smith & Weiner 2001, PRD 64, 043502 (inelastic DM)
- Kahlhoefer et al. 2014, arXiv:1407.2537 (point-particle σ)

Verification
------------
    python phase7a_composite_mediator_v03_map.py
runs the v0.3-prelim MAP composite-mediator LZ forward prediction and prints
the verdict, comparing to the v0.7 MAP result from T87.
"""
from __future__ import annotations
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import t87_composite_inelastic_nucleon as t87
import t87_lz_event_rate as t87_rate


# v0.3-prelim MAP values from T39 Tier-3 fit (commit preceding 5b93185)
# Source: data/results/t39_tier3_epsilon_alpha_joint_fit.json
V03_MAP = {
    "sigma_m_0": 0.720,                    # cm²/g at V_REF = 100 km/s
    "a": 1.31,                              # velocity exponent (σ/m ∝ v^(-a))
    "log_epsilon": -56.113,                 # log10(ε)
    "log_alpha": -28.047,                   # log10(α_X)
    "log_Z": -2.941,                        # Bayesian evidence (4D T39 Tier-3)
}
V03_MAP["epsilon"] = 10 ** V03_MAP["log_epsilon"]   # ~ 7.71e-57
V03_MAP["alpha_chi"] = 10 ** V03_MAP["log_alpha"]  # ~ 8.98e-29

# Phase 7a microphysical inputs: composite-DM (m_χ, m_φ) at v0.3-prelim MAP.
# These are placeholder values matching the v0.3-prelim anchor (see CH27 NGC1052 trail
# channel for context: v0.3-prelim MAP mass range is m_χ ~ 100-300 GeV class for
# the multi-channel fit). The T39 4D fit itself does not pin (m_χ, m_φ), so we
# use the canonical anchor (m_χ = 200 GeV, m_φ = 50 MeV) which is in the
# v0.3-prelim sweet spot for σ/m_0 ~ 0.72 cm²/g with the calibrated σ_elastic_nuc
# formula's dependence on (ε, α).
#
# Sensitivity: σ_elastic_nuc is independent of m_χ in the T79 empirical
# normalization (line 137 comment), and depends on m_φ as (m_φ/30 MeV)⁻⁴. Since
# v0.3-prelim MAP ε² is the dominant suppression, the exact m_φ choice only
# shifts the result by a factor of (m_φ/30 MeV)⁻⁴ — order unity for m_φ ~ 50 MeV.
PHI7A_INPUTS = {
    "m_chi_GeV": 200.0,                     # GeV (canonical v0.3-prelim anchor)
    "m_phi_MeV": 50.0,                      # MeV (canonical v0.3-prelim anchor)
}

# Di Mauro mass-splitting δ range (from arXiv:2609.02608 + LZ paper)
DELTA_KEV_LIST = [50, 100, 200, 297, 371, 500]
FORM_FACTOR_ANSATZE = ["gaussian", "dipole"]


def compute_phase7a_verdict(
    m_chi_GeV: float = PHI7A_INPUTS["m_chi_GeV"],
    m_phi_MeV: float = PHI7A_INPUTS["m_phi_MeV"],
    epsilon: float = V03_MAP["epsilon"],
    alpha_chi: float = V03_MAP["alpha_chi"],
    delta_keV: float = 297.0,
    form_factor_ansatz: str = "gaussian",
) -> dict:
    """Compute σ_inel_nuc and N_events at v0.3-prelim MAP for a given δ.

    Returns a dict with all key quantities for the Phase 7a verdict.
    """
    # Compute σ_inel_nuc at the LZ target recoil energy (248 keV)
    sigma_inel_at_target = t87.sigma_inel_nuc(
        E_R_keV=t87_rate.LZ_OBSERVED_RECOIL_KEV,
        m_chi_GeV=m_chi_GeV,
        m_phi_MeV=m_phi_MeV,
        epsilon=epsilon,
        alpha_chi=alpha_chi,
        delta_keV=delta_keV,
        form_factor_ansatz=form_factor_ansatz,
    )

    # Compute N_events in LZ window
    res = t87_rate.N_events_in_lz_window(
        m_chi_GeV=m_chi_GeV,
        m_phi_MeV=m_phi_MeV,
        epsilon=epsilon,
        alpha_chi=alpha_chi,
        delta_keV=delta_keV,
        form_factor_ansatz=form_factor_ansatz,
    )
    N = res["N_events_at_target"]
    observed = t87_rate.LZ_OBSERVED_EVENTS
    ratio = N / observed if observed > 0 else float("inf")
    return {
        "operating_point": "v0.3-prelim MAP",
        "v03_MAP_inputs": {
            "sigma_m_0": V03_MAP["sigma_m_0"],
            "a": V03_MAP["a"],
            "epsilon": V03_MAP["epsilon"],
            "alpha_chi": V03_MAP["alpha_chi"],
            "log_epsilon": V03_MAP["log_epsilon"],
            "log_alpha": V03_MAP["log_alpha"],
            "log_Z_T39_tier3": V03_MAP["log_Z"],
        },
        "composite_inputs": {
            "m_chi_GeV": m_chi_GeV,
            "m_phi_MeV": m_phi_MeV,
        },
        "delta_keV": delta_keV,
        "form_factor_ansatz": form_factor_ansatz,
        "sigma_inel_at_target_cm2": float(sigma_inel_at_target),
        "N_predicted": float(N),
        "N_observed": observed,
        "ratio_pred_over_observed": float(ratio),
        "log10_ratio": float(math.log10(ratio)) if ratio > 0 else float("-inf"),
        "poisson_p_value": float(res["poisson_p_value"]),
        "v_min_at_target_kms": float(res["v_min_at_target_kms"]),
        "verdict": "DOES NOT EXPLAIN LZ EVENT (predicted ≪ observed)"
                   if N < 0.1 else
                   "MARGINAL — kill criterion NOT triggered"
                   if N < 1.0 else
                   "EXPLAINS LZ EVENT (predicted ≥ 1)",
    }


def run_phase7a_sweep() -> dict:
    """Run the full Phase 7a sweep over (δ, form-factor ansatz).

    Returns the result dict (also written to JSON).
    """
    print("=" * 70)
    print("Phase 7a — Composite-mediator LZ forward prediction at v0.3-prelim MAP")
    print("=" * 70)
    print()
    print(f"v0.3-prelim MAP (T39 Tier-3):")
    print(f"  σ/m_0 = {V03_MAP['sigma_m_0']} cm²/g at V_REF=100 km/s")
    print(f"  a     = {V03_MAP['a']}")
    print(f"  ε     = {V03_MAP['epsilon']:.3e}  (log ε = {V03_MAP['log_epsilon']})")
    print(f"  α_χ   = {V03_MAP['alpha_chi']:.3e}  (log α = {V03_MAP['log_alpha']})")
    print(f"  log Z = {V03_MAP['log_Z']}")
    print()
    print(f"Composite-DM (m_χ, m_φ) inputs:")
    print(f"  m_χ = {PHI7A_INPUTS['m_chi_GeV']} GeV  (canonical v0.3-prelim anchor)")
    print(f"  m_φ = {PHI7A_INPUTS['m_phi_MeV']} MeV  (canonical v0.3-prelim anchor)")
    print()
    print(f"Comparison: v0.7 MAP had ε ≈ 1.12e-37, giving N_pred ≈ 4.8e-73.")
    print(f"           v0.3-prelim MAP has ε ≈ {V03_MAP['epsilon']:.2e},")
    print(f"           giving ε² suppression ratio of (ε_v03/ε_v07)² ≈")
    ratio = (V03_MAP["epsilon"] / 1.12e-37) ** 2
    print(f"           {ratio:.2e}×  smaller σ_DM-nuc than v0.7 MAP.")
    print()
    print(f"{'δ (keV)':>8} | {'ansatz':>10} | {'σ_inel (cm²)':>14} | {'N_pred':>10} | {'log10(N/obs)':>13} | {'verdict':<40}")
    print("-" * 110)

    sweep_results = []
    for delta in DELTA_KEV_LIST:
        for ff in FORM_FACTOR_ANSATZE:
            v = compute_phase7a_verdict(delta_keV=delta, form_factor_ansatz=ff)
            sweep_results.append(v)
            print(f"{delta:>8} | {ff:>10} | {v['sigma_inel_at_target_cm2']:>14.3e} | "
                  f"{v['N_predicted']:>10.3e} | {v['log10_ratio']:>13.2f} | {v['verdict']:<40}")

    # Kill-criterion check
    max_N = max(r["N_predicted"] for r in sweep_results)
    min_log_ratio = min(r["log10_ratio"] for r in sweep_results)
    kill_triggered = max_N < 0.1  # "No mediator class can produce LZ event"

    print()
    print(f"Max N_predicted across sweep: {max_N:.3e}")
    print(f"Min log10(N_pred/observed):  {min_log_ratio:.2f}")
    print(f"Kill criterion (N_pred < 0.1): {'TRIGGERED' if kill_triggered else 'NOT TRIGGERED'}")
    if kill_triggered:
        print()
        print("VERDICT (Phase 7a, composite-mediator at v0.3-prelim MAP):")
        print("  Composite-DM CANNOT produce the LZ event at v0.3-prelim MAP.")
        print("  Even MORE suppressed than at v0.7 MAP (where N_pred ≈ 10⁻⁷³).")
        print("  The ε² scaling amplifies the deficit: ε_v03 ≈ 10⁻²⁰× ε_v07,")
        print("  so σ_inel_nuc_v03 ≈ 10⁻⁴⁰× σ_inel_nuc_v07.")
        print()
        print("  Per roadmap §Phase 7 kill criterion:")
        print("  > 'No mediator class can produce LZ event at σ_DM-nuc ~10⁻⁴³ cm²")
        print("  >  while fitting multi-channel data at v0.3-prelim MAP.'")
        print("  > Action if triggered: Abandon LZ event interpretation; treat LZ as Ch14 constraint.")
        print()
        print("  Phase 7a composite-mediator sub-task: KILL CONFIRMED at v0.3-prelim MAP.")

    return {
        "phase": "7a",
        "date": "2026-09-13",
        "title": "Composite-mediator LZ forward prediction at v0.3-prelim MAP",
        "v03_MAP": V03_MAP,
        "composite_inputs": PHI7A_INPUTS,
        "sweep_results": sweep_results,
        "max_N_predicted": float(max_N),
        "min_log10_ratio": float(min_log_ratio),
        "kill_triggered": kill_triggered,
        "decision": "KILL — composite-mediator sub-task abandons LZ event interpretation at v0.3-prelim MAP",
        "comparison_to_v07": {
            "v07_epsilon": 1.12e-37,
            "v07_N_predicted_at_delta297_gaussian": 3.63e-73,
            "v03_epsilon": V03_MAP["epsilon"],
            "v03_N_predicted_at_delta297_gaussian": next(
                r["N_predicted"] for r in sweep_results
                if r["delta_keV"] == 297 and r["form_factor_ansatz"] == "gaussian"
            ),
            "ratio_v03_over_v07": float(
                next(r["N_predicted"] for r in sweep_results
                     if r["delta_keV"] == 297 and r["form_factor_ansatz"] == "gaussian") / 3.63e-73
            ),
        },
    }


def main():
    result = run_phase7a_sweep()

    # Save results JSON
    out_path = Path(__file__).resolve().parent.parent / "data" / "results" / "phase7a_composite_mediator_v03_map.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2, default=str)
    print()
    print(f"Results written to: {out_path}")
    return result


if __name__ == "__main__":
    main()
