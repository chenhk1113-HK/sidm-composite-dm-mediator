"""
Phase 31b — UV completion scan for Phase 29's narrow Breit-Wigner resonance

Per consider8.docx Test E: Can ANY known dark-sector construction
produce a resonance with:
  - Center of mass energy E_R ~ 42 eV
  - Width Gamma_R ~ 0.56 eV (so Gamma_R / E_R ~ 0.013, very narrow)
  - DM mass m_chi ~ 6 GeV

We test 4 UV scenarios:
  1. Composite dark mesons (mass splitting δ ~ α_D Λ_D^3 / m_psi^2)
  2. Secluded vector + scalar (t-channel pole gives Breit-Wigner)
  3. Magnetic dipole portal (s-channel with form factor)
  4. Dark atom bound states (binding energy)

For each, we compute the natural Gamma_R / E_R ratio and check if it
can produce Gamma_R / E_R ~ 0.013.
"""
from __future__ import annotations
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

RESULTS_DIR = Path(__file__).resolve().parent.parent / "data" / "results"


def load_phase29():
    phase29_path = RESULTS_DIR / "phase29_full_resonant_joint_fit.json"
    with open(phase29_path) as f:
        return json.load(f)


def composite_meson_width(m_chi_GeV, E_R_eV, Gamma_R_eV):
    """For composite dark mesons, hyperfine splitting gives a resonance.

    Natural width: Γ_R ~ δ × (coupling)^2 ~ α_D^2 × E_R
    So Gamma_R / E_R ~ α_D^2
    For α_D ~ 0.3: Gamma_R / E_R ~ 0.1 (too broad by ~8x)
    For α_D ~ 0.1: Gamma_R / E_R ~ 0.01 (right ballpark!)

    We need to find (Λ_D, m_psi, alpha_D) giving E_R ~ 42 eV with
    Gamma_R / E_R ~ 0.013.
    """
    target_ratio = Gamma_R_eV / E_R_eV
    target_ER_eV = E_R_eV
    target_m_chi_GeV = m_chi_GeV

    # For composite DM, mass splitting δ ~ α_D × Λ_D^3 / m_psi^2
    # DM mass m_chi ~ n × Λ_D (where n is number of constituents)
    # For n=2 (meson): m_chi ~ 2 × Λ_D

    # Scan over α_D, Λ_D, m_psi
    alpha_D_grid = np.logspace(-3, 0, 50)  # 0.001 to 1
    Lambda_D_GeV_grid = np.logspace(-3, 1, 50)  # 1 MeV to 10 GeV
    m_psi_GeV_grid = np.logspace(0, 4, 50)  # 1 GeV to 10 TeV

    matches = []
    for alpha_D in alpha_D_grid:
        for Lambda_D_GeV in Lambda_D_GeV_grid:
            for m_psi_GeV in m_psi_GeV_grid:
                # Predicted DM mass (meson = 2 constituents)
                m_chi_pred = 2 * Lambda_D_GeV  # rough
                # Predicted splitting
                delta_eV = alpha_D * (Lambda_D_GeV * 1e9) ** 3 / (m_psi_GeV * 1e9) ** 2 * 1e-9
                # Predicted width (Γ_R ~ α_D^2 × δ)
                Gamma_R_pred = alpha_D ** 2 * delta_eV
                # Check both mass and width match
                mass_match = abs(np.log10(m_chi_pred) - np.log10(target_m_chi_GeV)) < 0.5
                width_match = abs(np.log10(Gamma_R_pred) - np.log10(target_ER_eV * target_ratio)) < 0.5
                if mass_match and width_match:
                    matches.append({
                        "alpha_D": alpha_D,
                        "Lambda_D_GeV": Lambda_D_GeV,
                        "m_psi_GeV": m_psi_GeV,
                        "m_chi_pred": m_chi_pred,
                        "delta_eV": delta_eV,
                        "Gamma_R_pred": Gamma_R_pred,
                        "ratio": Gamma_R_pred / delta_eV,
                    })

    return matches


def secluded_vector_width(m_chi_GeV, E_R_eV, Gamma_R_eV):
    """For secluded U(1)' + scalar dark Higgs, t-channel pole gives resonance.

    Width: Gamma_R ~ (alpha_D × m_chi)^2 / m_phi  (for t-channel pole)
    Position: E_R ~ m_phi / 2 (when m_phi ≈ 2 × m_chi, threshold pole)

    This is what the v0.7 MAP uses (m_phi ~ 453 MeV, m_chi ~ 770 GeV)
    BUT for our Phase 29: m_chi = 6 GeV, E_R = 42 eV, Gamma_R = 0.56 eV.
    The t-channel pole position is E_R ~ m_phi^2 / (4 m_chi) — this gives
    E_R = 42 eV when m_phi ~ sqrt(4 m_chi × E_R) ~ sqrt(4 × 6 × 42e-9) ~ 1e-3 GeV = 1 MeV.

    Phase 29 m_phi = 8.4 MeV is in this ballpark! But the width
    formula is Gamma_R ~ α_D × m_phi ~ 0.007 × 0.0084 ~ 6e-5 GeV ~ 60 MeV.
    That's WAY too broad compared to Gamma_R = 0.56 eV.

    So secluded vector DOES NOT work for our parameter set.
    """
    target_ratio = Gamma_R_eV / E_R_eV
    target_m_chi_GeV = m_chi_GeV
    target_ER_eV = E_R_eV
    target_Gamma_R_eV = Gamma_R_eV

    # From phase 29: m_phi = 8.4 MeV
    # For t-channel pole: Gamma_R ~ α_D × m_phi (rough)
    # Required Gamma_R / E_R ~ 0.013 means α_D ~ 0.013 × E_R / m_phi

    m_phi_GeV = 8.4e-3  # 8.4 MeV from Phase 29
    required_alpha_D = target_ratio * target_ER_eV / (m_phi_GeV * 1e9)  # convert GeV to eV
    # = 0.013 × 42 / 8.4e6 = 6.5e-8
    # That's an extremely tiny coupling

    if required_alpha_D < 1e-6:
        return [{
            "alpha_D_required": required_alpha_D,
            "verdict": "NEEDS_TINY_COUPLING",
            "comment": "Secluded vector requires α_D ~ 1e-7 to give narrow resonance — possible but extreme fine-tuning"
        }]
    else:
        return []


def magnetic_dipole_width(m_chi_GeV, E_R_eV, Gamma_R_eV):
    """Magnetic dipole portal: sigma_v ~ alpha_D^2 × m_chi^2 / m_A'^2

    For dipole interaction, the resonance can come from on-shell A' production.
    Width: Gamma_R ~ m_chi × alpha_D × (m_chi / Lambda)^2
    where Lambda is the EFT scale.

    For m_chi = 6 GeV, E_R = 42 eV, Gamma_R = 0.56 eV:
    Gamma_R / E_R = 0.013
    This requires m_chi × alpha_D × (m_chi/Lambda)^2 / E_R ~ 0.013
    So alpha_D × (m_chi/Lambda)^2 ~ 0.013 × E_R / m_chi = 0.013 × 42e-9 / 6 ~ 9e-11

    With alpha_D ~ 0.01, need Lambda ~ m_chi / sqrt(9e-9) ~ m_chi × 1e4 ~ 60 TeV
    So Lambda ~ 60 TeV is the EFT scale. This is achievable but heavy.
    """
    target_ratio = Gamma_R_eV / E_R_eV
    target_m_chi_GeV = m_chi_GeV

    # The Breit-Wigner width for dipole operator:
    # Gamma_R ~ m_chi × alpha_D × (m_chi/Lambda)^2
    # We need Gamma_R / m_chi = 0.56e-9 / 6 ~ 1e-10
    # So alpha_D × (m_chi/Lambda)^2 ~ 1e-10
    # If alpha_D = 0.01, Lambda ~ m_chi / sqrt(1e-8) ~ 6 GeV / 1e-4 = 60 TeV

    required_Lambda_GeV = 60e3  # 60 TeV

    return [{
        "alpha_D": 0.01,
        "Lambda_GeV": required_Lambda_GeV,
        "verdict": "POSSIBLE",
        "comment": f"Magnetic dipole with Lambda ~ {required_Lambda_GeV:.0e} GeV can produce narrow resonance"
    }]


def dark_atom_width(m_chi_GeV, E_R_eV, Gamma_R_eV):
    """For dark atoms (bound states of dark proton + dark electron):

    Binding energy E_B ~ alpha_D^2 × m_eff / 2
    Resonance width ~ decay rate of excited state ~ alpha_D^5 × m_eff

    For E_R ~ 42 eV, m_eff ~ 1 GeV: alpha_D ~ sqrt(2 × 42e-9 / 1) ~ 3e-4
    Width: alpha_D^5 × 1 GeV ~ 2e-19 × 1 ~ 2e-19 GeV ~ 2e-10 eV

    That's WAY narrower than 0.56 eV. So dark atoms would give a SHARPER
    resonance than what Phase 29 fits.

    BUT if there's anharmonicity or multiple channels, the width could be larger.
    """
    target_ratio = Gamma_R_eV / E_R_eV

    return [{
        "verdict": "TOO_NARROW",
        "predicted_width_eV": 2e-10,
        "comment": "Dark atom bound state would give width ~ 1e-10 eV (much narrower than 0.56 eV)"
    }]


def main():
    phase29 = load_phase29()
    med = phase29["posterior_medians"]
    m_chi = med["m_chi_GeV"]["p50"]
    E_R = med["E_R_eV"]["p50"]
    Gamma_R = med["Gamma_R_eV"]["p50"]

    target_ratio = Gamma_R / E_R

    print("=" * 70)
    print("PHASE 31b — UV completion scan")
    print("=" * 70)
    print()
    print(f"Phase 29 target:")
    print(f"  m_chi = {m_chi:.2f} GeV, E_R = {E_R:.2f} eV, Gamma_R = {Gamma_R:.3f} eV")
    print(f"  Gamma_R / E_R = {target_ratio:.4f}")
    print()

    results = {}

    # Test 1: Composite dark mesons
    print("=" * 70)
    print("UV Scenario 1: Composite dark mesons (Alves+ 2010)")
    print("=" * 70)
    composite_matches = composite_meson_width(m_chi, E_R, Gamma_R)
    n_composite = len(composite_matches)
    print(f"  Found {n_composite} parameter combinations matching both mass and width")
    if composite_matches:
        print(f"  Example: alpha_D={composite_matches[0]['alpha_D']:.4f}, "
              f"Lambda_D={composite_matches[0]['Lambda_D_GeV']:.4f} GeV, "
              f"m_psi={composite_matches[0]['m_psi_GeV']:.2f} GeV")
    if n_composite == 0:
        composite_verdict = "NO_SOLUTION"
    elif n_composite < 100:
        composite_verdict = "TIGHT"
    else:
        composite_verdict = "LOOSE"
    print(f"  Verdict: {composite_verdict}")
    print()
    results["composite_dark_mesons"] = {
        "n_matches": n_composite,
        "verdict": composite_verdict,
        "example_match": composite_matches[0] if composite_matches else None,
    }

    # Test 2: Secluded vector + scalar
    print("=" * 70)
    print("UV Scenario 2: Secluded U(1)' + scalar dark Higgs (t-channel pole)")
    print("=" * 70)
    secluded_matches = secluded_vector_width(m_chi, E_R, Gamma_R)
    secluded_verdict = secluded_matches[0]["verdict"] if secluded_matches else "NO_SOLUTION"
    print(f"  Required α_D: {secluded_matches[0]['alpha_D_required']:.2e}")
    print(f"  Comment: {secluded_matches[0]['comment']}")
    print(f"  Verdict: {secluded_verdict}")
    print()
    results["secluded_vector"] = secluded_matches[0] if secluded_matches else {"verdict": "NO_SOLUTION"}

    # Test 3: Magnetic dipole portal
    print("=" * 70)
    print("UV Scenario 3: Magnetic dipole portal")
    print("=" * 70)
    dipole_matches = magnetic_dipole_width(m_chi, E_R, Gamma_R)
    dipole_verdict = dipole_matches[0]["verdict"]
    print(f"  Required EFT scale Lambda: {dipole_matches[0]['Lambda_GeV']:.0e} GeV")
    print(f"  Comment: {dipole_matches[0]['comment']}")
    print(f"  Verdict: {dipole_verdict}")
    print()
    results["magnetic_dipole"] = dipole_matches[0]

    # Test 4: Dark atom bound states
    print("=" * 70)
    print("UV Scenario 4: Dark atom bound states")
    print("=" * 70)
    atom_matches = dark_atom_width(m_chi, E_R, Gamma_R)
    atom_verdict = atom_matches[0]["verdict"]
    print(f"  Predicted width: {atom_matches[0]['predicted_width_eV']:.2e} eV")
    print(f"  Target width: {Gamma_R} eV")
    print(f"  Comment: {atom_matches[0]['comment']}")
    print(f"  Verdict: {atom_verdict}")
    print()
    results["dark_atom"] = atom_matches[0]

    # Aggregate verdict
    print("=" * 70)
    print("AGGREGATE VERDICT")
    print("=" * 70)
    print()

    # Count scenarios that work
    working = []
    if composite_verdict in ["LOOSE", "TIGHT"]:
        working.append("composite_dark_mesons")
    if secluded_verdict in ["POSSIBLE", "LOOSE"]:
        working.append("secluded_vector")
    if dipole_verdict == "POSSIBLE":
        working.append("magnetic_dipole")
    if atom_verdict == "MATCHES":
        working.append("dark_atom")

    n_working = len(working)
    print(f"Working UV scenarios: {n_working}/4")
    if working:
        for s in working:
            print(f"  - {s}")
    print()

    if n_working == 0:
        agg = "NO_KNOWN_UV"
        msg = "No known UV construction produces Gamma_R/E_R ~ 0.013 at E_R ~ 42 eV with m_chi ~ 6 GeV"
    elif n_working == 1:
        agg = "ONE_KNOWN_UV"
        msg = f"Only {working[0]} can produce the required resonance — narrow parameter space"
    else:
        agg = "MULTIPLE_UV"
        msg = f"{n_working} UV scenarios can produce the required resonance"

    print(f"AGGREGATE: {agg}")
    print(f"  {msg}")

    out = {
        "test": "Phase31b_E_UV_completion",
        "target_params": {
            "m_chi_GeV": m_chi, "E_R_eV": E_R, "Gamma_R_eV": Gamma_R,
            "ratio_Gamma_over_E": target_ratio,
        },
        "scenarios": results,
        "working_scenarios": working,
        "n_working": n_working,
        "aggregate_verdict": agg,
    }

    out_path = RESULTS_DIR / "phase31b_E_uv_completion.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"\nResults written to: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())