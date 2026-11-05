"""
Phase 7e — Unit-conversion pitfall remediation in T87 LZ event rate.

Motivation (per AGENTS.md memory entry, 2026-09-11/12)
-----------------------------------------------------
AGENTS.md memory entry flagged a unit-conversion pitfall class:
- "T90.61 used (1/hbar*c)^2 = 2.57e27 for GeV^-2->cm^2; correct is (hbar*c)^2 = 3.89e-28.
   Off by 10^55."
- "T90.63 age used 977.8 Myr; correct 977800 Myr - 1 Mpc/(km/s) = 977.8 Gyr. Off by 1000."
- "Integrating dt/dz from z=0 gives LOOKBACK TIME, not age."

This phase audits T87_lz_event_rate.py for similar unit-conversion bugs that
could produce plausible-looking but wrong N_pred values.

FINDING (per audit 2026-09-13)
------------------------------
The T87_lz_event_rate.N_events_in_lz_window() function has a unit-conversion
bug in the N_T calculation:

  Line 197: M_T_kg_days = exposure_tonne_years * 1000 * DAYS_PER_YEAR
    This computes kg * days (mass * time), not just mass.

  Line 243: N_T = M_T_kg_days * 1000 / 131 * 6.022e23
    With M_T_kg_days in kg*days, N_T comes out in 'days' (not dimensionless).
    Bug factor: 365.25 days/year (or 365.25 * exposure_tonne_years).

This means ALL T87 N_pred values (and hence Phase 7a/7c results) are
~365x too high. The kill verdicts remain valid (defects are 60+ orders of
magnitude below 1), but the quantitative comparison to LZ sensitivity needs
revision.

References
----------
- AGENTS.md memory entry "UNIT-CONVERSION PITFALL (2026-09-11/12)"
- code/t87_lz_event_rate.py (the bug)
- code/t87_composite_inelastic_nucleon.py (the σ_inel formula; CORRECT)
- T87_LZ_FORWARD_PREDICTION.md (the original ship)
- PHASE7A/B/C docs (all reference T87 N_pred)

Verification
------------
    python phase7e_unit_conversion_audit.py
runs the audit, identifies the bug, and provides the corrected formula.
"""
from __future__ import annotations
import json
import math
import sys
from pathlib import Path

import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
V03_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

import t87_composite_inelastic_nucleon as t87
import t87_lz_event_rate as t87r


def compute_N_T_CORRECT(exposure_tonne_years: float) -> float:
    """CORRECT formula: N_T = (mass_kg * 1000 g/kg) / (M_target g/mol) * N_A.

    Units: (kg * 1000 g/kg) = g, / (g/mol) = mol, * (1/mol) = dimensionless.
    """
    M_T_kg = exposure_tonne_years * 1000.0  # kg of Xe per tonne-year
    M_target_g_per_mol = 131.0  # xenon
    N_A = 6.022e23
    return M_T_kg * 1000.0 / M_target_g_per_mol * N_A


def compute_N_T_BUGGY(exposure_tonne_years: float) -> float:
    """BUGGY formula (as in T87 line 243): N_T has units of days, not dimensionless."""
    M_T_kg_days = exposure_tonne_years * 1000.0 * 365.25  # kg*days
    M_target_g_per_mol = 131.0
    N_A = 6.022e23
    return M_T_kg_days * 1000.0 / M_target_g_per_mol * N_A  # has units of days


def compute_N_total_CORRECT(exposure_tonne_years: float, m_chi_GeV: float,
                              m_phi_MeV: float, epsilon: float, alpha_chi: float,
                              delta_keV: float, form_factor_ansatz: str = "gaussian") -> dict:
    """Replicate T87 N_events_in_lz_window with the corrected N_T formula.

    Same structure as t87_rate.N_events_in_lz_window but with N_T = kg*1000/131*N_A
    (not M_T_kg_days * 1000 / 131 * N_A).
    """
    E_R_min_keV = t87r.LZ_RECOIL_MIN_KEV
    E_R_max_keV = t87r.LZ_RECOIL_MAX_KEV
    E_R_target_keV = t87r.LZ_OBSERVED_RECOIL_KEV
    n_integration_points = 100

    n_DM = t87r.RHO_DM_GEV_CM3 / m_chi_GeV
    N_T = compute_N_T_CORRECT(exposure_tonne_years)
    exposure_seconds = exposure_tonne_years * 365.25 * 86400.0

    E_R_grid_keV = np.linspace(E_R_min_keV, E_R_max_keV, n_integration_points)
    sigma_grid = np.array([
        t87.sigma_inel_nuc(E_R_keV=E, m_chi_GeV=m_chi_GeV, m_phi_MeV=m_phi_MeV,
                            epsilon=epsilon, alpha_chi=alpha_chi,
                            delta_keV=delta_keV, form_factor_ansatz=form_factor_ansatz)
        for E in E_R_grid_keV
    ])
    v_avg_grid = np.array([
        t87r.average_speed_above_threshold_kms(t87r.v_min_inelastic_kms(E, m_chi_GeV, delta_keV))
        for E in E_R_grid_keV
    ])
    v_avg_grid_cms = v_avg_grid * 1e5

    dR_dE_R_per_keV = N_T * n_DM * sigma_grid * v_avg_grid_cms  # events/s/keV
    integrand_events = dR_dE_R_per_keV * exposure_seconds  # events/keV
    N_total = np.trapezoid(integrand_events, E_R_grid_keV)

    target_mask = np.abs(E_R_grid_keV - E_R_target_keV) < t87r.LZ_OBSERVED_RECOIL_ERR_KEV
    if np.any(target_mask):
        N_target = np.trapezoid(integrand_events[target_mask], E_R_grid_keV[target_mask])
    else:
        idx = np.argmin(np.abs(E_R_grid_keV - E_R_target_keV))
        N_target = integrand_events[idx] * t87r.LZ_OBSERVED_RECOIL_ERR_KEV

    idx_target = np.argmin(np.abs(E_R_grid_keV - E_R_target_keV))
    return {
        "N_events_total": float(N_total),
        "N_events_at_target": float(N_target),
        "v_avg_at_target_kms": float(v_avg_grid[idx_target]),
        "sigma_inel_at_target_cm2": float(sigma_grid[idx_target]),
        "N_T_correct": float(N_T),
        "exposure_tonne_years": float(exposure_tonne_years),
    }


def main():
    print("=" * 78)
    print("Phase 7e — Unit-conversion audit of T87 LZ event rate formula")
    print("=" * 78)
    print()
    print("FINDING: The N_T calculation in t87_lz_event_rate.py:243 has a unit bug.")
    print()

    # Demonstrate the bug
    print("Demonstration (1 tonne-year exposure):")
    n_t_correct = compute_N_T_CORRECT(1.0)
    n_t_buggy = compute_N_T_BUGGY(1.0)
    print(f"  N_T CORRECT = {n_t_correct:.4e} (dimensionless, # of Xe nuclei)")
    print(f"  N_T BUGGY   = {n_t_buggy:.4e} (has units of 'days', off by 365.25)")
    print(f"  Ratio BUGGY/CORRECT = {n_t_buggy / n_t_correct:.4f}")
    print()

    # Run at T87 v0.7 MAP reference point
    print("=" * 78)
    print("AUDIT 1: T87 v0.7 MAP reference (m_chi=770, m_phi=453, eps=1.12e-37, alpha=6.84e-17)")
    print("=" * 78)
    print()
    print(f"{'delta (keV)':>12} | {'T87 buggy (recon.)':>20} | {'Corrected N_pred':>20} | {'ratio (bug/correct)':>20}")
    print("-" * 90)
    # The production N_T unit bug (t87_lz_event_rate.py:243, DAYS_PER_YEAR inside the
    # target-count) was FIXED, so calling the production function no longer reproduces the
    # historical 365.25x error. The "buggy" column is therefore a RECONSTRUCTION: the corrected
    # audit value multiplied by the measured N_T_buggy / N_T_correct factor from the 1 tonne-year
    # demonstration above. The live production-vs-audit difference is reported separately.
    bug_factor_measured = n_t_buggy / n_t_correct
    v07_results = []
    for delta in [50, 100, 200, 297, 371, 500]:
        # Production function as it stands today (bug already fixed)
        res_production = t87r.N_events_in_lz_window(
            m_chi_GeV=770.0, m_phi_MeV=453.0,
            epsilon=1.12e-37, alpha_chi=6.84e-17,
            delta_keV=float(delta), form_factor_ansatz='gaussian',
            exposure_tonne_years=2.84,
        )
        # Corrected (this audit's independent implementation)
        res_correct = compute_N_total_CORRECT(
            exposure_tonne_years=2.84, m_chi_GeV=770.0, m_phi_MeV=453.0,
            epsilon=1.12e-37, alpha_chi=6.84e-17,
            delta_keV=float(delta), form_factor_ansatz='gaussian',
        )
        n_production = res_production["N_events_at_target"]
        n_correct = res_correct["N_events_at_target"]
        n_buggy = n_correct * bug_factor_measured  # reconstruction of the pre-fix value
        ratio = n_buggy / n_correct if n_correct > 0 else float('inf')
        ratio_prod = n_production / n_correct if n_correct > 0 else float('inf')
        v07_results.append({
            "delta_keV": delta,
            "N_buggy": n_buggy,
            "N_correct": n_correct,
            "N_production_today": n_production,
            "ratio_buggy_over_correct": ratio,
            "ratio_production_over_correct": ratio_prod,
        })
        print(f"{delta:>12} | {n_buggy:>20.4e} | {n_correct:>20.4e} | {ratio:>20.4f}")
    print()

    # Run at v0.3-prelim MAP (Phase 7a reproduction)
    print("=" * 78)
    print("AUDIT 2: v0.3-prelim MAP (Phase 7a composite-mediator setup)")
    print("=" * 78)
    print()
    v03_eps = 7.71e-57
    v03_alpha = 8.98e-29
    print(f"  epsilon = {v03_eps:.3e}, alpha_chi = {v03_alpha:.3e}")
    print(f"  (m_chi=200 GeV, m_phi=50 MeV at v0.3-prelim canonical anchors)")
    print()
    print(f"{'delta (keV)':>12} | {'Phase 7a buggy (recon.)':>20} | {'Corrected N_pred':>20} | {'ratio (bug/correct)':>20}")
    print("-" * 90)
    v03_results = []
    for delta in [50, 100, 200, 297, 371, 500]:
        res_production = t87r.N_events_in_lz_window(
            m_chi_GeV=200.0, m_phi_MeV=50.0,
            epsilon=v03_eps, alpha_chi=v03_alpha,
            delta_keV=float(delta), form_factor_ansatz='gaussian',
            exposure_tonne_years=2.84,
        )
        res_correct = compute_N_total_CORRECT(
            exposure_tonne_years=2.84, m_chi_GeV=200.0, m_phi_MeV=50.0,
            epsilon=v03_eps, alpha_chi=v03_alpha,
            delta_keV=float(delta), form_factor_ansatz='gaussian',
        )
        n_production = res_production["N_events_at_target"]
        n_correct = res_correct["N_events_at_target"]
        n_buggy = n_correct * bug_factor_measured  # reconstruction of the pre-fix value
        ratio = n_buggy / n_correct if n_correct > 0 else float('inf')
        ratio_prod = n_production / n_correct if n_correct > 0 else float('inf')
        v03_results.append({
            "delta_keV": delta,
            "N_buggy": n_buggy,
            "N_correct": n_correct,
            "N_production_today": n_production,
            "ratio_buggy_over_correct": ratio,
            "ratio_production_over_correct": ratio_prod,
        })
        print(f"{delta:>12} | {n_buggy:>20.4e} | {n_correct:>20.4e} | {ratio:>20.4f}")
    print()

    # Verdict on impact
    print("=" * 78)
    print("IMPACT ON PHASE 7 VERDICTS")
    print("=" * 78)
    print()
    print("All Phase 7 kill verdicts remain valid (delta = 297 keV, 2.84 tonne-years):")
    v07_297 = next(r for r in v07_results if r["delta_keV"] == 297)
    v03_297 = next(r for r in v03_results if r["delta_keV"] == 297)
    prod_ratios = [r["ratio_production_over_correct"] for r in v07_results
                   if np.isfinite(r["ratio_production_over_correct"])]
    prod_audit_ratio = float(np.median(prod_ratios))
    print(f"  Phase 7 T87 v0.7 reference:  historical (reconstructed) {v07_297['N_buggy']:.4e}, "
          f"corrected {v07_297['N_correct']:.4e}, production today {v07_297['N_production_today']:.4e}")
    print(f"  Phase 7a composite v0.3-prelim: historical (reconstructed) {v03_297['N_buggy']:.4e}, "
          f"corrected {v03_297['N_correct']:.4e}, production today {v03_297['N_production_today']:.4e}")
    print("  Phase 7c (Di Mauro) inherits the same constant factor; its own values are recorded")
    print("    in PHASE7C_DI_MAURO_2026-09-13.md, not recomputed by this audit.")
    print()
    print("The unit-conversion bug was a CONSTANT 365.25x FACTOR on all N_pred values.")
    print("Relative comparisons (v0.7 vs v0.3-prelim, delta sweep, ansatz comparison) remain valid.")
    print("Absolute LZ event-rate predictions WERE 365x too high (the bug is fixed in")
    print("  production); this does NOT change the kill.")
    print(f"DISCLOSURE: production today agrees with this audit's corrected implementation to "
          f"{abs(prod_audit_ratio - 1.0) * 100:.2f}% (median ratio {prod_audit_ratio:.4f}).")
    print("  That residual is a separate implementation difference, NOT the 365.25x unit bug.")
    print()

    # Save results
    result = {
        "phase": "7e",
        "date": "2026-09-13",
        "title": "Unit-conversion audit of T87 LZ event rate formula",
        "bug_found": True,
        "bug_location": "code/t87_lz_event_rate.py:243",
        "bug_description": (
            "N_T is computed as M_T_kg_days * 1000 / 131 * N_A, where M_T_kg_days has "
            "units of kg*days (mass * time). The result has units of 'days' instead of "
            "dimensionless # of nuclei. Bug factor: 365.25x for 1 tonne-year exposure."
        ),
        "bug_factor": 365.25,
        "bug_status": (
            "FIXED in production. code/t87_lz_event_rate.py now computes "
            "N_T = M_T_kg * 1000 / 131 * N_A with no DAYS_PER_YEAR factor, so it no longer "
            "reproduces the historical 365.25x error."
        ),
        "buggy_column_provenance": (
            "N_buggy in every audit row is a RECONSTRUCTION: N_correct * (N_T_buggy / N_T_correct) "
            "= N_correct * 365.25. The production function cannot be called to obtain the buggy "
            "value because the bug was removed; N_production_today is the live production value."
        ),
        "production_vs_audit_corrected_ratio_median": prod_audit_ratio,
        "production_vs_audit_residual_percent": (prod_audit_ratio - 1.0) * 100.0,
        "residual_disclosure": (
            "Production and this audit's independent corrected implementation differ by about "
            f"{abs(prod_audit_ratio - 1.0) * 100:.2f}% on N_events_at_target. That is a separate "
            "implementation discrepancy (not the 365.25x unit bug) and remains open."
        ),
        "audit_revised": "2026-11-05 (buggy columns made explicit reconstructions; production-vs-audit residual disclosed)",
        "N_T_correct_for_1_ty": float(n_t_correct),
        "N_T_buggy_for_1_ty": float(n_t_buggy),
        "v07_MAP_audit": v07_results,
        "v03_MAP_audit": v03_results,
        "impact_on_phase_7": (
            "All kill verdicts remain valid (defects are 60+ orders of magnitude below 1). "
            "The bug is a constant 365.25x factor on N_pred values; relative comparisons "
            "are unaffected."
        ),
        "fix_recommendation": (
            "Replace line 197: M_T_kg_days = exposure_tonne_years * 1000 * DAYS_PER_YEAR "
            "with: M_T_kg = exposure_tonne_years * 1000 (remove DAYS_PER_YEAR). "
            "Then N_T in line 243 is dimensionless as intended."
        ),
        "docs_to_update": [
            "T87_LZ_FORWARD_PREDICTION.md (cite buggy N_pred values)",
            "PHASE7A_COMPOSITE_MEDIATOR_2026_09_13.md (cite T87 N_pred at delta=297)",
            "PHASE7C_DI_MAURO_2026_09_13.md (cite T87 N_pred at delta=297)",
            "data/results/2026-09-03_t87_lz_forward_prediction.json (N_predicted values)",
        ],
        "kill_verdicts_unchanged": True,
    }
    out_path = V03_ROOT / "data" / "results" / "phase7e_unit_conversion_audit.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2, default=str)
    print(f"Results written to: {out_path}")
    return result


if __name__ == "__main__":
    main()
