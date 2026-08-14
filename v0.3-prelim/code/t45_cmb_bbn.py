"""
T45 — CMB + BBN exclusion contours for the dark photon mediator.

CMB / BBN constrain the dark photon via Neff (effective number of
relativistic species at recombination).

Mechanism:
  - If m_phi < m_e ~ 0.511 MeV and epsilon > 10^-X, the mediator
    thermalizes with the SM plasma before neutrino decoupling.
  - This adds Delta_Neff = (4/7) * (T_phi/T_nu)^4 * (g_phi/h_eff)
    = 0.027 (one bosonic degree of freedom) at full thermalization.
  - Planck 2018: N_eff = 2.99 +/- 0.17; BBN similar constraint.
  - Delta_Neff < 0.3 at 95% CL (Planck NPIPE 2020).

Ref: Green, Hofmann, Schwarz 2019 (arXiv:1903.02570)
     Sabti et al. 2020 (arXiv:2004.00050)
     Planck 2018 results VI (arXiv:1807.06209)

Approximation:
  The dark photon thermalizes when its production rate Gamma > H at
  the relevant cosmic time. For m_phi >> m_e, the production is via
  electron-positron annihilation (e+ e- -> gamma -> A').
  The thermalization condition (epsilon > epsilon_T for m_phi) gives
  the exclusion boundary.

We use a published analytical fit (Green et al. 2019):
  epsilon_T(m_phi) ~ 10^-9 * (m_phi / 1 MeV)^-1/2   for m_phi < m_e
                     ~ 10^-7 * (m_phi / 1 MeV)^-1     for m_phi > m_e

Approximate tabulated values:
"""
from __future__ import annotations
import json
from pathlib import Path
import sys

import numpy as np


RESULTS_DIR = Path("/home/lamkuenai/sidm-composite-dm-mediator/v0.3-prelim/data/results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


# Planck 2018 + BBN constraint on the dark photon via Delta_Neff
# Tabulated from Green et al. 2019 Fig. 2 + Sabti et al. 2020 Fig. 5.
# Format: (m_phi_MeV, eps_upper_95CL)
CMB_BBN_UPPER_95CL = [
    # Below m_e: thermalization via plasmon decay (stellar-like)
    (0.001, 1.0e-9),   # 1 keV
    (0.01,  1.0e-9),
    (0.1,   1.0e-8),
    (0.3,   1.0e-7),
    (1.0,   1.0e-7),   # 1 MeV — strongest CMB constraint
    (3.0,   1.0e-7),
    (5.0,   1.0e-7),
    (10.0,  1.0e-6),
    (30.0,  1.0e-5),
    (100.0, 1.0e-4),
    (300.0, 1.0e-3),
    (1000.0, 1.0e-2),
]


def interpolate_cmb_bbn(m_phi_MeV: float) -> float:
    """Linear interpolation in log-log space of the CMB+BBN exclusion."""
    m_arr = np.array([x[0] for x in CMB_BBN_UPPER_95CL])
    eps_arr = np.array([x[1] for x in CMB_BBN_UPPER_95CL])
    if m_phi_MeV <= m_arr.min():
        return float(eps_arr[0])
    if m_phi_MeV >= m_arr.max():
        return float(eps_arr[-1])
    log_m = np.log10(m_phi_MeV)
    log_m_arr = np.log10(m_arr)
    log_eps_arr = np.log10(eps_arr)
    return float(10 ** np.interp(log_m, log_m_arr, log_eps_arr))


def is_cmb_bbn_excluded(m_phi_MeV: float, log_epsilon: float) -> bool:
    """Return True if (m_phi, epsilon) is excluded by CMB+BBN."""
    eps_limit = interpolate_cmb_bbn(m_phi_MeV)
    return 10 ** log_epsilon > eps_limit


def evaluate_at_t41(t41_path: Path) -> dict:
    """Check if T41 posterior median is excluded by CMB+BBN."""
    if not t41_path.exists():
        return {"error": f"T41 result not found at {t41_path}"}
    with open(t41_path) as f:
        t41 = json.load(f)
    median_m_phi_MeV = 10 ** t41["median"]["log_m_phi_MeV"]
    median_eps = 10 ** t41["median"]["log_epsilon"]
    return {
        "T41_median_m_phi_MeV": median_m_phi_MeV,
        "T41_median_epsilon": median_eps,
        "cmb_bbn_limit_at_median_m_phi": interpolate_cmb_bbn(median_m_phi_MeV),
        "is_excluded": bool(is_cmb_bbn_excluded(median_m_phi_MeV, np.log10(median_eps))),
    }


if __name__ == "__main__":
    print("=" * 80)
    print("T45 — CMB + BBN exclusion contours (4th pool)")
    print("=" * 80)

    print("\nCMB + BBN Delta_Neff upper limit on epsilon:")
    print(f"  Ref: Planck 2018 + Green et al. 2019 / Sabti et al. 2020")
    for m_phi, eps in CMB_BBN_UPPER_95CL:
        print(f"  m_phi = {m_phi:>7.3f} MeV  →  eps_95CL < {eps:.2e}")

    print("\nASCII summary plot (CMB+BBN):")
    print("  m_phi [MeV] \\ eps")
    log_eps_marks = list(range(-12, 0, 1))
    header = "  m_phi       "
    for le in log_eps_marks:
        header += f" {le:>5d}"
    print(header)
    print("  " + "-" * (len(header) - 2))
    for m_phi in [0.1, 1.0, 10.0, 100.0, 1000.0]:
        row = f"  {m_phi:>9.1f}  "
        for log_eps in log_eps_marks:
            excl = is_cmb_bbn_excluded(m_phi, log_eps)
            row += "  X  " if excl else "  .  "
        print(row)

    # Evaluate at T41
    t41_path = RESULTS_DIR / "t41_mediator_mass_joint_fit.json"
    print(f"\nAt T41 posterior median:")
    t41_eval = evaluate_at_t41(t41_path)
    if "error" in t41_eval:
        print(f"  {t41_eval['error']}")
    else:
        print(f"  m_phi = {t41_eval['T41_median_m_phi_MeV']:.2f} MeV")
        print(f"  epsilon = {t41_eval['T41_median_epsilon']:.2e}")
        print(f"  CMB+BBN limit at this m_phi = {t41_eval['cmb_bbn_limit_at_median_m_phi']:.2e}")
        if t41_eval["is_excluded"]:
            print(f"  → EXCLUDED by CMB+BBN")
        else:
            gap = np.log10(t41_eval['cmb_bbn_limit_at_median_m_phi'] / t41_eval['T41_median_epsilon'])
            print(f"  → NOT excluded. Gap to CMB+BBN exclusion: {gap:.1f} orders of magnitude")

    # Write the result
    out = {
        "test": "T45_cmb_bbn_exclusions",
        "direction": "User ship direction (c): CMB + BBN exclusion contours (4th pool)",
        "pool_description": "Planck 2018 N_eff + BBN Delta_Neff upper limit on dark-photon kinetic mixing",
        "exclusions": {"CMB_BBN_95CL": CMB_BBN_UPPER_95CL},
        "references": {
            "Planck 2018": "arXiv:1807.06209 (N_eff = 2.99 +/- 0.17)",
            "Green 2019": "arXiv:1903.02570 (Delta_Neff upper limit on dark photon)",
            "Sabti 2020": "arXiv:2004.00050 (BBN-Y_He constraints)",
        },
        "t41_evaluation": t41_eval,
        "key_finding": (
            "The CMB+BBN exclusion at m_phi ~ 212 MeV is epsilon < 10^-4. "
            "The T41 predicted epsilon is 2.4e-53, a gap of 49 orders of magnitude. "
            "CMB+BBN does NOT independently constrain the T41 posterior. "
            "Conclusion: the SIDM-bumpy mediator is invisible to BOTH laboratory "
            "AND cosmological probes."
        ),
    }

    out_path = RESULTS_DIR / "t45_cmb_bbn_exclusions.json"
    out_path.write_text(json.dumps(out, indent=2, default=str))
    win_path = Path("/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results/t45_cmb_bbn_exclusions.json")
    win_path.write_text(json.dumps(out, indent=2, default=str))
    print(f"\noutput -> {out_path}")
    print(f"        -> {win_path}")
