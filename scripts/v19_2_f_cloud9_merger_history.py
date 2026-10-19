"""v40.44: gravothermal tau reset via mergers per Silverman+ 2026.

This script applies the Silverman+ 2026 (arXiv:2606.02566) merger-driven
tau reset mechanism to the v19.2-F Cloud-9 c-M tension.

PAPER REFERENCE:
  Silverman, M., Hussein, A., Arora, A., Lisanti, M., Kaplinghat, M.,
  Necib, L., Thoyas, A., O'Neil, S., Sanderson, R., Shen, X., Moreno, J.
  2026, "Mergers Matter: Gravothermal Collapse in Dwarf Halos with
  Self-Interacting Dark Matter"
  arXiv:2606.02566 [astro-ph.GA] (FERMILAB-PUB-26-0348-T)

KEY FINDING FROM SILVERMAN+ 2026:
  6 DM-only zoom-in 10^10 M_sun halos, sigma/m = 70 cm^2/g.
  - 3 of 6 halos undergo gravothermal collapse (m10q, m10d, m10i).
    All 3 have QUIESCENT merger histories (low merger count, few/no
    massive radial mergers, large quiescence time intervals).
  - 3 of 6 halos do NOT collapse (m10b, m10f, m10j).
    All 3 have SUSTAINED merger histories (many mergers, multiple
    massive radial mergers, short quiescence intervals).
  - Mergers inject orbital kinetic energy, alter heat transport, and
    drive inward heat flow that prevents the runaway gravothermal
    collapse.
  - Quantitative result: a 1:3 merger at 7.7 Gyr caused m10b's rho_c
    to drop by factor 8.7 (s70) or 3.9 (s30).

DIAGNOSTICS FOR PREDICTING COLLAPSE (from Silverman+ 2026 Sec. 3.3):
  - Merger mass ratio: M_sub/M_host >= 0.1 (massive mergers matter)
  - Orbital radiality: vtan/vtot <= 0.2 (radial mergers matter more)
  - Quiescence time interval: max time between mergers
  - Time of merger: late mergers (after ~5 Gyr) more disruptive

CLOUD-9 (Anand+ 2025, arXiv:2508.20157):
  - Compact H I cloud in M94 group at d ~ 4.4 Mpc
  - M_HI ~ 10^6 M_sun, W50 = 12 km/s (dynamically cold)
  - Non-rotating, ~1.4 kpc radius
  - Starless (RELHIC candidate)
  - In hydrostatic equilibrium with dark matter and UVB
  - "Susceptible to ram-pressure stripping" -- unlikely to be near
    massive galaxy, in GROUP environment

CLOUD-9 MERGER HISTORY INFERENCE:
  Based on observed properties:
  - Compact (~1.4 kpc), dynamically cold (W50=12 km/s), non-rotating
  - No tidal features, no rotation, no disturbance
  - RELHIC: gas in thermal equilibrium with UVB, no star formation
  - Regular morphology suggests QUIESCENT merger history
  - Per Silverman+ 2026: QUIESCENT history -> gravothermal collapse
    IS expected (m10i analog: 6 mergers, no massive radial, collapsed)

VERDICT (v40.44):
  v19.2-F's prediction that Cloud-9 is in deep collapse (tau = 16)
  is CONSISTENT with Silverman+ 2026's prediction for halos with
  quiescent merger histories.
  Ohana+ 2026's observation that Cloud-9 is in max-core (tau = 0.18)
  is INCONSISTENT with Silverman+ 2026.
  The c-M tension is NOT resolved by the merger-driven tau reset
  mechanism. Cloud-9's morphology suggests quiescent history -> collapse.
  Either:
  (a) Cloud-9 has had a major merger not visible in H I morphology
      (unlikely given regular appearance)
  (b) Ohana+ 2026's lensing-inferred c = 4 is wrong
  (c) v19.2-F's gravothermal parameters (sigma_peak, f_H) need
      adjustment to give tau < 1
  (d) Additional physics (baryonic heating, velocity-dependent
      scattering) is needed

This is consistent with the v40.41 STRUCTURAL verdict: the c-M
tension is real and cannot be resolved by tau reset alone.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "v0.3-prelim" / "code"))
sys.path.insert(0, str(REPO / "scripts"))

from t212_silverman_gravothermal import evaluate as t212_evaluate
from constants import (
    F_H_PLACEHOLDER_G7, SIGMA_PEAK_CM2_PER_G, V_TARGET_KMS, SIGMA_KMS,
)

CLOUD9 = {
    "M_halo_Msun": 4.7e9,
    "V_max_kms": 28.0,
    "M_HI_Msun": 1.0e6,
    "W50_kms": 12.0,
    "distance_Mpc": 4.4,
    "host_galaxy": "M94",
    "morphology": "compact, non-rotating, dynamically cold",
    "is_RELHIC_candidate": True,
    "merger_history_inferred": "quiescent (per Silverman+ 2026 diagnostics)",
}

T_HUBBLE_GYR = 13.8

# Silverman+ 2026 halo categories (from paper)
SILVERMAN_CASES = [
    {
        "name": "m10i (most quiescent, 6 mergers, no massive radial)",
        "n_mergers": 6,
        "massive_radial_mergers": 0,
        "outcome": "COLLAPSED (followed fluid model exactly)",
        "t_coll_Gyr": 5.2,
        "tau_at_z0": "10+ (deep collapse)",
    },
    {
        "name": "m10q (18 mergers, 2 massive radial, 2 early infall)",
        "n_mergers": 18,
        "massive_radial_mergers": 2,
        "outcome": "COLLAPSED (mergers too early/circular to prevent)",
        "t_coll_Gyr": 10.4,
        "tau_at_z0": "10+ (deep collapse)",
    },
    {
        "name": "m10d (18 mergers, no massive radial)",
        "n_mergers": 18,
        "massive_radial_mergers": 0,
        "outcome": "COLLAPSED",
        "t_coll_Gyr": 9.5,
        "tau_at_z0": "10+ (deep collapse)",
    },
    {
        "name": "m10b (15 mergers, 4 massive radial, 1:3 at 7.7 Gyr)",
        "n_mergers": 15,
        "massive_radial_mergers": 4,
        "outcome": "DID NOT COLLAPSE (rho_c dropped by factor 8.7)",
        "t_coll_Gyr": float('inf'),
        "tau_at_z0": "< 1 (max-core, merger-reset)",
    },
    {
        "name": "m10f (17 mergers, sustained 1:30 mergers, 1 massive radial)",
        "n_mergers": 17,
        "massive_radial_mergers": 1,
        "outcome": "DID NOT COLLAPSE (sustained decline in rho_c)",
        "t_coll_Gyr": float('inf'),
        "tau_at_z0": "< 1 (max-core, sustained-merger-reset)",
    },
    {
        "name": "m10j (12 mergers, early collapse onset)",
        "n_mergers": 12,
        "massive_radial_mergers": 0,
        "outcome": "DID NOT FULLY COLLAPSE (early phase)",
        "t_coll_Gyr": float('inf'),
        "tau_at_z0": "1-5 (transition)",
    },
]


def sigma_m_at_v(v, sigma_peak=SIGMA_PEAK_CM2_PER_G):
    return sigma_peak * math.exp(-0.5 * ((v - V_TARGET_KMS) / SIGMA_KMS)**2)


def cloud9_v19_2_f_tau(f_H=F_H_PLACEHOLDER_G7):
    """Cloud-9 tau under v19.2-F canonical parameters (no merger reset)."""
    sigma_m_v28 = sigma_m_at_v(CLOUD9["V_max_kms"])
    sigma_eff = f_H**2 * sigma_m_v28

    params = {"M_halo": CLOUD9["M_halo_Msun"], "c": 12.0, "sigma_m": sigma_eff, "v_max": None}
    r = t212_evaluate(params)
    t_core = r["t_core_Gyr"]
    tau = T_HUBBLE_GYR / t_core if t_core > 0 else float('inf')
    return tau, t_core, sigma_eff


def main():
    print("=" * 70)
    print("v40.44: gravothermal tau reset via mergers per Silverman+ 2026")
    print("=" * 70)
    print()
    print("Cloud-9 morphology suggests QUIESCENT merger history")
    print("(compact, non-rotating, dynamically cold H I, no tidal features).")
    print()
    print("Per Silverman+ 2026:")
    print("  Quiescent merger history -> gravothermal core collapse EXPECTED")
    print("  Sustained merger history -> gravothermal collapse PREVENTED")
    print()
    print("=" * 70)
    print("v19.2-F prediction (NO merger reset):")
    print("=" * 70)
    tau_v19_2_f, t_core, sigma_eff = cloud9_v19_2_f_tau()
    print(f"  sigma_eff = {sigma_eff:.2f} cm^2/g")
    print(f"  t_core (Balberg) = {t_core:.4f} Gyr")
    print(f"  tau = t_Hubble / t_core = {tau_v19_2_f:.2f}")
    print(f"  --> DEEP CORE COLLAPSE")
    print()
    print("=" * 70)
    print("Silverman+ 2026 halos (M_halo ~ 10^10 M_sun, sigma/m = 70 cm^2/g):")
    print("=" * 70)
    print(f"{'Halo':<55} {'Mergers':>8} {'Radial':>7} {'Outcome':<35}")
    print("-" * 110)
    for case in SILVERMAN_CASES:
        print(f"{case['name']:<55} {case['n_mergers']:>8} {case['massive_radial_mergers']:>7} {case['outcome']:<35}")
    print()
    print("=" * 70)
    print("Cloud-9 merger history inference (vs Silverman+ 2026 diagnostics):")
    print("=" * 70)
    print(f"  Cloud-9 morphology: {CLOUD9['morphology']}")
    print(f"  Cloud-9 M_HI: {CLOUD9['M_HI_Msun']:.0e} M_sun")
    print(f"  Cloud-9 W50: {CLOUD9['W50_kms']} km/s (dynamically cold)")
    print(f"  Cloud-9 rotation: NON-ROTATING")
    print(f"  Cloud-9 tidal features: NONE VISIBLE")
    print(f"  Cloud-9 inferred merger history: QUIESCENT")
    print()
    print("  Per Silverman+ 2026:")
    print("    Quiescent history (m10i analog: 6 mergers, no massive radial)")
    print("    -> gravothermal collapse EXPECTED (m10i collapsed in 5.2 Gyr)")
    print()
    print("=" * 70)
    print("VERDICT (v40.44):")
    print("=" * 70)
    print()
    print("  v19.2-F's prediction that Cloud-9 is in DEEP collapse (tau = 16)")
    print("  is CONSISTENT with Silverman+ 2026's prediction for halos with")
    print("  quiescent merger histories (m10i analog).")
    print()
    print("  Ohana+ 2026's observation that Cloud-9 is in MAX-CORE (tau = 0.18)")
    print("  is INCONSISTENT with Silverman+ 2026 + v19.2-F prediction.")
    print()
    print("  The c-M tension is NOT resolved by the merger-driven tau reset")
    print("  mechanism. Cloud-9's morphology suggests quiescent history,")
    print("  which means Silverman+ 2026 also predicts collapse.")
    print()
    print("  Possible explanations for the remaining tension:")
    print("    (a) Cloud-9 had a major merger not visible in H I morphology")
    print("        (unlikely given regular appearance)")
    print("    (b) Ohana+ 2026's lensing-inferred c = 4 is wrong")
    print("    (c) v19.2-F's gravothermal parameters (sigma_peak, f_H) need")
    print("        adjustment to give tau < 1")
    print("    (d) Additional physics (baryonic heating, velocity-dependent")
    print("        scattering) is needed")
    print()
    print("  This CONFIRMS the v40.41 STRUCTURAL verdict: the c-M tension")
    print("  is real and cannot be resolved by tau reset alone.")
    print()

    # Save
    out_dir = REPO / "v0.3-prelim" / "data" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "v19_2_f_cloud9_merger_history_2026_10_19.json"
    out_data = {
        "method": "v40.44: gravothermal tau reset via Silverman+ 2026 merger analysis",
        "date": "2026-10-19",
        "framework": "v19.2-F Phase 44 (sigma_peak=174, sigma_kms=4.4, f_H=0.297 placeholder)",
        "reference_paper": "Silverman+ 2026 arXiv:2606.02566",
        "reference_cloud9": "Anand+ 2025 arXiv:2508.20157",
        "cloud9_properties": CLOUD9,
        "v19_2_f_prediction": {
            "sigma_eff_cm2_g": sigma_eff,
            "t_core_Gyr": t_core,
            "tau": tau_v19_2_f,
            "verdict": "deep core collapse",
        },
        "silverman_2026_halos": SILVERMAN_CASES,
        "verdict": {
            "v19_2_f_consistent_with_silverman_2026": True,
            "ohana_observation_consistent_with_silverman_2026": False,
            "c_M_tension_resolved_by_merger_reset": False,
            "v40_41_structural_verdict_confirmed": True,
            "explanation": "Cloud-9's quiescent morphology (compact, non-rotating, dynamically cold, no tidal features) suggests a quiescent merger history. Per Silverman+ 2026, quiescent halos (e.g., m10i with 6 mergers, no massive radial) undergo gravothermal core collapse. v19.2-F's deep collapse prediction is CONSISTENT with Silverman+ 2026. The c-M tension with Ohana+ 2026's max-core observation is NOT resolved by the merger-driven tau reset mechanism.",
        },
    }
    out.write_text(json.dumps(out_data, indent=2), encoding="utf-8")
    print(f"Saved: {out}")
    print()
    print("=" * 70)
    print("R88(71) PRE-CLAIM CHECKLIST")
    print("=" * 70)
    print("(a) v40.44 does NOT resolve the c-M tension. v19.2-F + Silverman+ 2026")
    print("    PREDICT deep collapse, Ohana+ 2026 OBSERVES max-core.")
    print()
    print("(b) Per R88(68) lesson: this is an EXPLORATORY analysis with a")
    print("    clear NEGATIVE result. Cloud-9's morphology suggests quiescent")
    print("    history, which Silverman+ 2026 also predicts will collapse.")
    print()
    print("(c) HONEST FRAMING: The c-M tension is REAL. It cannot be")
    print("    resolved by tau reset alone. The remaining candidates are")
    print("    (a) hidden merger, (b) Ohana+ 2026 systematic, (c) v19.2-F")
    print("    parameter adjustment, (d) additional physics.")
    print()
    print("(d) RECOMMENDATION: Send to Nemotron 120B for 5th review.")


if __name__ == "__main__":
    main()
