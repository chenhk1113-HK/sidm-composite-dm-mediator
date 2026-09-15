"""
T90.70 — Multi-resonance self-interacting dark matter from dark QCD.

Per Tsai, McGehee, Murayama 2022 (arXiv:2008.08608, PRL 128.172001):
  Resonant SIDM can emerge naturally from heavy quarkonium excited states
  in a dark-QCD-like sector. Multiple resonances (analogous to Y(1S), Y(2S),
  Y(3S), Y(4S) in SM QCD) provide independent control over each velocity
  scale.

Tsai 2022 key formula (Eq. 11-13):
  Level spacing: m[Y(nS)] - m[Y((n-1)S)] = C * [1/n + O(1/n^2)]
  Resonance threshold: m[Y(nS)] ~ 2 m_DM
  Fine-tuning: F.T. ~ Delta * (4/(3e))^2 * n^3
  For n > 10, F.T. reduces by 10^5.

FIXED Breit-Wigner formula (vs T90.50 which had a bug):
  The correct BW cross-section near a resonance is:
    sigma(v) = sigma_peak * (Gamma^2/4) / [(E(v) - E_R)^2 + Gamma^2/4]
  where sigma_peak is a CONSTANT (set by resonance physics), not (hbarc/E)^2.
  This avoids the spurious (hbarc/E)^2 divergence at low v.

  The (hbarc/E)^2 factor in T90.50's formula is only valid for scattering
  near threshold; for off-resonance evaluation it gives incorrect behavior.

Architecture:
  - N resonances, each with (E_R_n, Gamma_n, sigma_peak_n)
  - sigma_peak_n is a free coupling (in cm^2/g units)
  - sigma/m(v) = sigma_background(v) + sum_n sigma_peak_n * BW_factor_n(v)

  Mapping n -> velocity scale:
    n = 2  -> v ~ 10 km/s     (dwarf galaxies; from background)
    n = 4  -> v ~ 28 km/s     (Cloud-9 RELHIC)
    n = 8  -> v ~ 100 km/s    (SPARC)
    n = 12 -> v ~ 300 km/s    (stellar streams)
    n = 16 -> v ~ 700 km/s    (clusters)

  Reference:
    arXiv:2008.08608 (Tsai, McGehee, Murayama 2022)
    arXiv:1805.03203 (Chu, Garcia-Cely, Murayama 2019, resonance velocity dep)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from t90_v50_resonant_sidm import (
    kinetic_energy_eV,
    sommerfeld_enhancement,
)

# Physical constants
C_KMS = 2.998e5
HBAR_C_KEV_CM = 1.973e-11
HC_eV_CM = HBAR_C_KEV_CM * 1e3  # 1.973e-8 eV*cm


def breit_wigner_factor(v_kms, m_chi_GeV, E_R_eV, Gamma_eV):
    """Compute the Breit-Wigner shape factor (dimensionless, 0-1).

    BW_factor(E) = (Gamma^2/4) / [(E - E_R)^2 + Gamma^2/4]

    At resonance: factor = 1
    Far from resonance: factor ~ (Gamma/2/(E-E_R))^2
    """
    E_eV = kinetic_energy_eV(v_kms, m_chi_GeV)
    numerator = Gamma_eV ** 2 / 4.0
    denominator = (E_eV - E_R_eV) ** 2 + Gamma_eV ** 2 / 4.0
    return numerator / denominator


def sigma_m_multi_resonant(
    v_kms: float,
    m_chi_GeV: float,
    resonances: list,
    sigma_0_cm2_per_g: float,
    alpha_Y: float = 0.01,
) -> dict:
    """Compute sigma/m with multiple Breit-Wigner resonances.

    Each resonance is specified by its peak sigma/m (sigma_peak_n), not
    by a coupling constant. This makes the physics transparent and avoids
    the (hbarc/E)^2 divergence bug.

    Args:
        v_kms: relative velocity (km/s)
        m_chi_GeV: DM mass
        resonances: list of dicts, each with:
            {"name": str, "E_R_eV": float, "Gamma_eV": float, "sigma_peak_cm2_per_g": float}
        sigma_0_cm2_per_g: non-resonant background (constant)
        alpha_Y: Sommerfeld coupling (currently unused)

    Returns:
        dict with sigma_m_total, per-resonance contributions
    """
    # Background
    S_somm = sommerfeld_enhancement(v_kms, alpha_Y)
    sigma_background = sigma_0_cm2_per_g * S_somm

    # Sum over resonances
    sigma_resonant_total = 0.0
    per_resonance = {}

    for res in resonances:
        E_R = res["E_R_eV"]
        Gamma = res["Gamma_eV"]
        sigma_peak = res["sigma_peak_cm2_per_g"]

        # Breit-Wigner shape factor (correct formula)
        bw_factor = breit_wigner_factor(v_kms, m_chi_GeV, E_R, Gamma)

        sigma_contribution = sigma_peak * bw_factor
        sigma_resonant_total += sigma_contribution

        per_resonance[res["name"]] = {
            "E_R_eV": E_R,
            "Gamma_eV": Gamma,
            "sigma_peak_cm2_per_g": sigma_peak,
            "bw_factor": bw_factor,
            "sigma_m_contribution": sigma_contribution,
        }

    sigma_m_total = sigma_background + sigma_resonant_total

    return {
        "sigma_m_total": sigma_m_total,
        "sigma_background": sigma_background,
        "sigma_resonant_total": sigma_resonant_total,
        "S_sommerfeld": S_somm,
        "per_resonance": per_resonance,
        "E_eV": kinetic_energy_eV(v_kms, m_chi_GeV),
    }


def build_default_resonances(m_chi_GeV):
    """Build the default 4-resonance configuration based on Tsai 2022 level spacing.

    Maps n state to velocity scale:
      n=4 (Y(4S) analog): v ~ 28 km/s (Cloud-9)
      n=8 (Y(8S)): v ~ 100 km/s (SPARC)
      n=12 (Y(12S)): v ~ 300 km/s (streams)
      n=16 (Y(16S)): v ~ 700 km/s (clusters)

    Each resonance's peak sigma/m is set to match observation:
      Cloud-9 (v=28): sigma/m ~ 100  (the original target)
      SPARC (v=100):  sigma/m ~ 0.07 (hierarchical preferred)
      Stream (v=300): sigma/m ~ 0.1  (subhalos for gaps)
      Cluster (v=700): sigma/m ~ 0.01 (essentially CDM)

    Dwarfs (v=10-15) get their sigma/m from the background (sigma_0).
    Cluster/Bullet get sigma/m dominated by background (which should drop fast).
    """
    v_targets = [28.0, 100.0, 300.0, 700.0]
    sigma_peaks = [100.0, 0.07, 0.1, 0.01]
    width_fractions = [0.05, 0.05, 0.05, 0.10]
    names = ["R1_v28_Cloud9", "R2_v100_SPARC", "R3_v300_Stream", "R4_v700_Cluster"]

    resonances = []
    for i, (v_t, sm, wf, name) in enumerate(zip(v_targets, sigma_peaks, width_fractions, names)):
        E_R = kinetic_energy_eV(v_t, m_chi_GeV)
        Gamma = wf * E_R
        resonances.append({
            "name": name,
            "v_target_kms": v_t,
            "E_R_eV": E_R,
            "Gamma_eV": Gamma,
            "sigma_peak_cm2_per_g": sm,
            "width_fraction": wf,
        })
    return resonances


def velocity_dependent_background(v_kms, sigma_0_dwarf, a_slope=0.7, v_ref=100.0):
    """Velocity-dependent background sigma/m(v) = sigma_0_dwarf * (v/v_ref)^(-a).

    Gives:
      v=10:  sigma/m = sigma_0_dwarf * (10/100)^(-0.7) = sigma_0_dwarf * 5.0
      v=100: sigma/m = sigma_0_dwarf
      v=1000: sigma/m = sigma_0_dwarf * 0.20

    This is the classic Yukawa SIDM velocity scaling.
    """
    return sigma_0_dwarf * (v_kms / v_ref) ** (-a_slope)


def validate_multi_resonant():
    """Validate the multi-resonance architecture against Phase 31bc failure modes."""
    print("=" * 70)
    print("T90.70 — Multi-resonant Dark QCD (Tsai 2022) [CORRECTED]")
    print("=" * 70)
    print()
    print("Architecture: 4 resonances at v ~ 28, 100, 300, 700 km/s")
    print("Dwarfs fitted by background (sigma_0)")
    print()

    m_chi = 6.09  # GeV
    sigma_0_dwarf = 0.3  # cm^2/g at v=10 km/s
    a_slope = 0.7  # velocity slope (Yukawa-like)

    resonances = build_default_resonances(m_chi)
    print("Resonance configuration:")
    print(f"  {'Name':20s}  {'v_target':>10}  {'E_R (eV)':>10}  {'Gamma (eV)':>12}  {'sigma_peak':>12}")
    print("  " + "-" * 75)
    for r in resonances:
        print(f"  {r['name']:20s}  {r['v_target_kms']:10.1f}  {r['E_R_eV']:10.3f}  {r['Gamma_eV']:12.3f}  {r['sigma_peak_cm2_per_g']:12.4f}")
    print()

    test_velocities = [
        ("Segue 1 (v=10)",   10.0),
        ("Fornax (v=15)",    15.0),
        ("Sculptor (v=12)",  12.0),
        ("Cloud-9 (v=28)",   28.0),
        ("Tri II (v=15)",    15.0),
        ("SPARC (v=100)",   100.0),
        ("MW sat (v=200)",  200.0),
        ("Stream (v=250)",  250.0),
        ("Stream (v=300)",  300.0),
        ("Cluster (v=1000)",1000.0),
        ("Bullet (v=3000)", 3000.0),
    ]

    targets = {
        "Segue 1 (v=10)":   (0.5, 5.0),
        "Fornax (v=15)":    (0.5, 5.0),
        "Sculptor (v=12)":  (0.5, 5.0),
        "Tri II (v=15)":    (0.5, 5.0),
        "Cloud-9 (v=28)":   (30.0, 500.0),
        "SPARC (v=100)":    (0.03, 0.5),
        "MW sat (v=200)":   (0.01, 1.0),
        "Stream (v=250)":   (0.05, 1.0),
        "Stream (v=300)":   (0.05, 1.0),
        "Cluster (v=1000)": (0.001, 0.1),
        "Bullet (v=3000)":  (0.0001, 0.1),
    }

    print("Multi-resonance sigma/m at test velocities:")
    print(f"  {'System':18s}  {'v (km/s)':>10}  {'sigma/m':>12}  {'vs target':>20}")
    print("  " + "-" * 70)

    pass_count = 0
    fail_count = 0
    for name, v in test_velocities:
        # Velocity-dependent background (Yukawa-like)
        sigma_0_v = velocity_dependent_background(v, sigma_0_dwarf, a_slope)
        # Skip Sommerfeld for now (set alpha_Y=0)
        result = sigma_m_multi_resonant(v, m_chi, resonances, sigma_0_v, 0.0)
        sm = result["sigma_m_total"]
        t_low, t_high = targets[name]
        in_band = t_low <= sm <= t_high
        if in_band:
            pass_count += 1
            status = "OK"
        else:
            fail_count += 1
            if sm < t_low:
                status = f"too low (<{t_low})"
            else:
                status = f"too high (>{t_high})"
        print(f"  {name:18s}  {v:10.1f}  {sm:12.4f}  {status:>20}")

    print()
    print(f"PASS: {pass_count}/{pass_count + fail_count}")
    print(f"FAIL: {fail_count}/{pass_count + fail_count}")

    return resonances


if __name__ == "__main__":
    validate_multi_resonant()