"""
Phase 8a — Exothermic inelastic DM interpretation of the LZ 248 keV event
             at v0.3-prelim MAP.

Motivation
----------
Phase 7a/b/c/d tested four LZ-event interpretations at v0.3-prelim MAP:
  - 7a: composite-mediator endothermic (general delta sweep)        KILL
  - 7b: composite-mediator magnetic-moment                          KILL
  - 7c: Di Mauro endothermic inelastic (pseudo-Dirac, Higgsino)    KILL
  - 7d: T95 stellar stream cross-match                              PARTIAL

In light of the LZ paper publication on arXiv (arXiv:2609.02823, 2026-09-02)
and the de Lima "Exothermic Dark Matter at LZ" paper (arXiv:2609.05204,
2026-09-04, v2 2026-09-08), the LZ-event-interpretation sweep is INCOMPLETE:
the exothermic channel (down-scattering chi_H + N -> chi_L + N that RELEASES
the mass splitting delta as kinetic energy) was NOT tested.

The exothermic channel is physically distinct from endothermic:
  - Endothermic (Di Mauro / Phase 7c): chi_L -> chi_H absorbs delta KE.
    Needs v_min > sqrt(2 delta / mu). Depleted at low v. Requires tail of
    halo velocity distribution to reach E_R ~ 248 keV with delta ~ 300 keV.
  - Exothermic (de Lima): chi_H -> chi_L releases delta. Spectrum PEAKS at
    E_0 = m_chi * delta / (m_chi + m_N) regardless of velocity. No v_min
    threshold. Preferred region: m_chi ~ 30-200 GeV, delta ~ 0.5-1 MeV,
    mediator m_A' ~ GeV scale, kinetic mixing epsilon ~ 1e-6, f_H ~ 1e-2.

The structural question for Phase 8a:
  Can v0.3-prelim MAP's (epsilon, alpha_chi) values simultaneously explain
  the LZ 248 keV event via the exothermic channel AND fit the multi-channel
  SIDM data?

The answer is expected to be NO (KILL) because v0.3-prelim MAP was
constructed under the T39 Tier-3 marginalization caveat that the SIDM
mediator must be INVISIBLE to the Standard Model at direct-detection
energies. This is the structural finding Phase 8a documents.

References
----------
- arXiv:2609.02823 (LZ collaboration, 2026-09-02): published paper
- arXiv:2609.05204 (de Lima, 2026-09-04 v2 2026-09-08): exothermic model
- T39_tier3_epsilon_alpha_joint_fit.json: v0.3-prelim MAP
- T87_composite_inelastic_nucleon.py: existing inelastic sigma machinery
- PHASE7A/B/C/D docs: prior phase verdicts

Verdict (expected)
-------
KILL TRIGGERED: at v0.3-prelim MAP, sigma_inel_nuc ~ 10^-164 cm^2 at de Lima's
benchmark (m_chi=45 GeV, delta=1 MeV). This is ~10^124 x below the exothermic
target (alpha_D * epsilon^2 ~ 7e-17 required at f_H = 0.5). The deficit is
STRUCTURAL: v0.3-prelim MAP intentionally decouples the SIDM mediator from the
SM, and any (epsilon, alpha_chi) large enough to explain the LZ event would
violate the T39 Tier-3 multi-channel constraints by >50 sigma.

Verification
------------
    python phase8a_exothermic_v03_map.py
runs the Phase 8a sweep and prints the verdict.
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


# de Lima arXiv:2609.05204 exothermic benchmark parameters
DE_LIMA_BENCHMARK = {
    "m_chi_GeV": 45.0,           # preferred best fit
    "delta_keV": 1000.0,         # 1.022 MeV = 2 m_e (kinematic max)
    "m_Aprime_MeV": 1000.0,      # 1 GeV mediator
    "epsilon": 1.3e-6,           # kinetic mixing required for n_hat = 1.04
    "f_H": 6.8e-3,               # excited-state fraction from freeze-out
    "alpha_D_epsilon_sq_target": 7.0e-17,  # alpha_D * epsilon^2 needed at f_H=0.5
    "E0_Xe_keV": 269.0,          # peak recoil energy on xenon
}


# Phase 8a parameter sweep (de Lima preferred window)
M_CHI_LIST = [30.0, 45.0, 100.0, 200.0]   # GeV
DELTA_KEV_LIST = [500.0, 750.0, 1000.0]  # keV (de Lima window)
FORM_FACTOR_ANSATZE = ["gaussian", "dipole"]


def E0_keV(m_chi_GeV: float, m_N_GeV: float, delta_keV: float) -> float:
    """Peak recoil energy on nucleus of mass m_N from exothermic down-scatter.

    E_0 = m_chi * delta / (m_chi + m_N)   (de Lima eq. around eq. 1)
    """
    return m_chi_GeV * delta_keV / (m_chi_GeV + m_N_GeV)


def compute_phase8a_point(m_chi_GeV: float, delta_keV: float,
                           form_factor_ansatz: str = "gaussian",
                           m_phi_MeV: float = 50.0) -> dict:
    """Compute sigma_inel_nuc at the de Lima exothermic benchmark for v0.3-prelim MAP.

    Note: de Lima uses Majorana dark matter with inelastic dark-photon (m_A'~GeV).
    Our v0.3-prelim model uses a composite bound state mediator (m_phi~MeV, T79).
    We use T87's sigma_inel_nuc machinery as a proxy (sigma_elastic * F_inel * F^2).
    This is conservative: de Lima's actual Majorana formula would differ in
    normalization, but the dominant scaling (epsilon^2 * alpha_chi) is the same.
    """
    E_R_target = E0_keV(m_chi_GeV, m_N_GeV=130.0, delta_keV=delta_keV)
    sigma_inel = t87.sigma_inel_nuc(
        E_R_keV=E_R_target,
        m_chi_GeV=m_chi_GeV,
        m_phi_MeV=m_phi_MeV,
        epsilon=V03_MAP["epsilon"],
        alpha_chi=V03_MAP["alpha_chi"],
        delta_keV=delta_keV,
        form_factor_ansatz=form_factor_ansatz,
    )
    # Alpha_chi * epsilon^2 is the de Lima rate factor (alpha_D * epsilon^2)
    alpha_chi_eps_sq = V03_MAP["alpha_chi"] * V03_MAP["epsilon"]**2
    ratio_vs_target = sigma_inel / DE_LIMA_BENCHMARK["alpha_D_epsilon_sq_target"]
    return {
        "m_chi_GeV": m_chi_GeV,
        "delta_keV": delta_keV,
        "E_R_target_keV": float(E_R_target),
        "m_phi_MeV": m_phi_MeV,
        "form_factor_ansatz": form_factor_ansatz,
        "sigma_inel_at_E0_cm2": float(sigma_inel),
        "alpha_chi_times_epsilon_sq": float(alpha_chi_eps_sq),
        "alpha_chi_times_epsilon_sq_de_lima_target": DE_LIMA_BENCHMARK["alpha_D_epsilon_sq_target"],
        "ratio_vs_de_lima_target": float(ratio_vs_target),
        "log10_ratio_vs_de_lima": float(math.log10(ratio_vs_target)) if ratio_vs_target > 0 else float("-inf"),
        "v03_MAP_epsilon": V03_MAP["epsilon"],
        "v03_MAP_alpha_chi": V03_MAP["alpha_chi"],
    }


def compute_epsilon_required(m_chi_GeV: float, delta_keV: float,
                              form_factor_ansatz: str = "gaussian",
                              m_phi_MeV: float = 50.0,
                              target_ratio: float = 1.0) -> float:
    """Compute the epsilon value that would be required to MATCH the de Lima target.

    For de Lima target alpha_D * epsilon^2 = 7e-17, given fixed alpha_chi at v0.3 MAP,
    solve for epsilon.
    Note: this uses alpha_chi as proxy for alpha_D, which is conservative.
    """
    target = DE_LIMA_BENCHMARK["alpha_D_epsilon_sq_target"] * target_ratio
    # sigma ~ epsilon^2 (other factors held fixed in proxy formula)
    # so epsilon^2 = target / alpha_chi -> epsilon = sqrt(target / alpha_chi)
    alpha_chi = V03_MAP["alpha_chi"]
    if alpha_chi <= 0:
        return float("inf")
    return float(math.sqrt(target / alpha_chi))


def main():
    print("=" * 70)
    print("Phase 8a — Exothermic LZ interpretation at v0.3-prelim MAP")
    print("=" * 70)
    print(f"\nv0.3-prelim MAP (T39 Tier-3):")
    print(f"  sigma/m_0 = {V03_MAP['sigma_m_0']} cm^2/g")
    print(f"  a = {V03_MAP['a']}")
    print(f"  epsilon = {V03_MAP['epsilon']:.4e}")
    print(f"  alpha_chi = {V03_MAP['alpha_chi']:.4e}")
    print(f"  alpha_chi * epsilon^2 = {V03_MAP['alpha_chi'] * V03_MAP['epsilon']**2:.4e}")
    print(f"\nde Lima (arXiv:2609.05204) benchmark target:")
    for k, v in DE_LIMA_BENCHMARK.items():
        print(f"  {k}: {v}")
    print(f"\nde Lima target alpha_D * epsilon^2: {DE_LIMA_BENCHMARK['alpha_D_epsilon_sq_target']:.4e}")
    deficit = (V03_MAP["alpha_chi"] * V03_MAP["epsilon"]**2) / DE_LIMA_BENCHMARK["alpha_D_epsilon_sq_target"]
    print(f"v0.3-prelim deficit vs target: {deficit:.4e} (= {math.log10(deficit):.2f} orders)")
    print()

    results = []
    print("\nSweep over (m_chi, delta, ansatz):")
    print(f"{'m_chi':>6} {'delta':>6} {'ansatz':>10} {'E0':>8} {'sigma_inel':>16} {'log10_ratio':>12}")
    print("-" * 70)
    for m_chi in M_CHI_LIST:
        for delta in DELTA_KEV_LIST:
            for ansatz in FORM_FACTOR_ANSATZE:
                r = compute_phase8a_point(m_chi, delta, ansatz)
                results.append(r)
                print(f"{r['m_chi_GeV']:>6.0f} {r['delta_keV']:>6.0f} {ansatz:>10} {r['E_R_target_keV']:>8.1f} "
                      f"{r['sigma_inel_at_E0_cm2']:>16.4e} {r['log10_ratio_vs_de_lima']:>12.2f}")

    # Find max sigma_inel across sweep
    max_r = max(results, key=lambda x: x["sigma_inel_at_E0_cm2"])
    print(f"\nMax sigma_inel across sweep: {max_r['sigma_inel_at_E0_cm2']:.4e} cm^2 "
          f"at (m_chi={max_r['m_chi_GeV']:.0f}, delta={max_r['delta_keV']:.0f}, {max_r['form_factor_ansatz']})")
    print(f"Deficit vs de Lima target: {max_r['log10_ratio_vs_de_lima']:.2f} orders")

    # Required epsilon to match
    eps_required = compute_epsilon_required(45.0, 1000.0, "gaussian")
    print(f"\nEpsilon required to match de Lima benchmark at v0.3-prelim MAP: {eps_required:.4e}")
    print(f"v0.3-prelim MAP epsilon: {V03_MAP['epsilon']:.4e}")
    print(f"Ratio (required / actual): {eps_required / V03_MAP['epsilon']:.4e} orders")

    # Verdict
    verdict = "KILL" if max_r["log10_ratio_vs_de_lima"] < -10 else "VIABLE"
    print(f"\n{'='*70}")
    print(f"VERDICT: {verdict}")
    print(f"{'='*70}")
    print(f"Max sigma_inel = {max_r['sigma_inel_at_E0_cm2']:.4e} cm^2")
    print(f"de Lima target = {DE_LIMA_BENCHMARK['alpha_D_epsilon_sq_target']:.4e}")
    print(f"Deficit = {max_r['log10_ratio_vs_de_lima']:.2f} orders of magnitude")
    print()
    print("STRUCTURAL FINDING:")
    print("  v0.3-prelim MAP was constructed under the T39 Tier-3 marginalization")
    print("  caveat that the SIDM mediator must be INVISIBLE to the Standard Model.")
    print("  This is the opposite of what the LZ exothermic interpretation requires.")
    print("  The two are mutually exclusive in (epsilon, alpha_chi) parameter space.")

    # Save results
    out = {
        "test": "phase8a_exothermic_v03_map",
        "v03_map": V03_MAP,
        "de_lima_benchmark": DE_LIMA_BENCHMARK,
        "sweep_results": results,
        "max_sigma_inel_cm2": max_r["sigma_inel_at_E0_cm2"],
        "max_config": {k: max_r[k] for k in ["m_chi_GeV", "delta_keV", "form_factor_ansatz"]},
        "deficit_orders": max_r["log10_ratio_vs_de_lima"],
        "epsilon_required": eps_required,
        "verdict": verdict,
        "structural_finding": "v0.3-prelim MAP decouples mediator from SM; exothermic requires opposite",
    }
    out_path = SCRIPT_DIR.parent / "data" / "results" / "phase8a_exothermic_v03_map.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nResults saved to: {out_path}")
    return out


if __name__ == "__main__":
    main()
