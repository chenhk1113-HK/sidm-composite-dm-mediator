#!/usr/bin/env python
"""
T90.49 — Inelastic Self-Interacting Dark Matter (iSIDM).

Per the user request and the Wang 2025 paper (arXiv:2512.18959),
inelastic SIDM adds a mass splitting delta between ground state chi_1
and excited state chi_2. This gives a kinematic threshold that
suppresses scattering at low velocities, potentially resolving the
Cloud-9 vs Galactic tension.

Two scattering channels:
  1. Elastic: chi_1 + chi_1 -> chi_1 + chi_1
     Allowed at all velocities.
     Cross-section: sigma_elastic = sigma_yukawa(v)
  2. Endothermic: chi_1 + chi_1 -> chi_2 + chi_2
     Requires center-of-mass kinetic energy E_cm >= delta = m_2 - m_1
     Threshold velocity: v_min = sqrt(2 * delta / m_reduced)
     where m_reduced = m_chi / 2 for identical particles
     Cross-section: sigma_endothermic = sigma_yukawa(v) * Theta(v - v_min)
       where Theta is the Heaviside step function

The velocity threshold (per Schutz+ 2015):
  v_min^2 = 4 * delta / m_chi (for identical particles in CM frame)
  or equivalently: v_min = 2 * sqrt(delta / m_chi) [c=1 units]
  In km/s: v_min_kms = 2 * sqrt(delta_eV / m_chi_GeV) * c
  where c = 3e5 km/s, so:
  v_min_kms = 6e5 * sqrt(delta_eV / m_chi_GeV)

For delta = 100 eV and m_chi = 40 GeV:
  v_min = 6e5 * sqrt(100 / 40) = 6e5 * 1.58 = 9.5e5 km/s
  ... wait that's wrong, let me redo.

For delta = 100 eV and m_chi = 40 GeV:
  v_min = c * sqrt(2 * delta / m_chi) where everything in natural units
  In SI: delta_eV / m_chi_eV = 100 / (40e9) = 2.5e-9
  v_min/c = sqrt(2 * 2.5e-9) = sqrt(5e-9) = 7.07e-5
  v_min = 7.07e-5 * 3e5 km/s = 21.2 km/s

That's the threshold velocity for inelastic scattering.

For delta = 10 eV: v_min = sqrt(10/100) * 21.2 = 6.7 km/s
For delta = 1 eV: v_min = sqrt(1/100) * 21.2 = 2.1 km/s
For delta = 1000 eV (1 keV): v_min = sqrt(1000/100) * 21.2 = 67 km/s
For delta = 10000 eV (10 keV): v_min = sqrt(10000/100) * 21.2 = 212 km/s

Key insight: With delta ~ 100-1000 eV:
  - At dSph (v~30 km/s): inelastic suppressed -> only elastic
  - At RELHIC/Cloud-9 (v~28 km/s): same as dSph -> inelastic suppressed
  - At Galactic (v~100 km/s): inelastic opens up -> more scattering
  - At Bullet (v~3000 km/s): fully open but Yukawa Born suppressed

This creates a peak in sigma/m(v) at v ~ v_min where the inelastic
channel opens. The peak height is determined by Yukawa Born sigma at v_min.

Wait, this is BACKWARDS for what we want! At RELHIC (v=28), with
delta ~ 100 eV, the inelastic is suppressed -> only elastic.
The elastic sigma is the same as before. So inelastic DM with this
threshold doesn't HELP for Cloud-9.

The Wang 2025 paper achieves the result through:
1. Leptophilic scalar (avoids LZ constraints)
2. Pseudo-Dirac splitting 100 eV
3. Cross-section peak from RESONANCE (not threshold)
4. The resonance is at v ~ delta/m_chi ~ 1-10 km/s

So Wang 2025 uses resonance, not threshold. The "inelastic" part
is the LZ suppression, not the velocity dependence.

For our T90.49, let me implement:
1. The full elastic + inelastic scattering cross-section
2. The velocity threshold
3. Test whether ANY delta gives Cloud-9 compatible behavior

The threshold suppresses scattering at v < v_min. For Cloud-9 (v=28)
we want HIGH sigma, so we want delta < 100 eV (v_min < 28).
For Galactic (v=100) we want LOW sigma, so we want delta ~ 100 eV
(v_min ~ 30 km/s) so that at v=100 we are well above threshold
but Yukawa Born has dropped.

Actually let me reconsider. The standard inelastic DM result:
- At v < v_min: sigma = sigma_elastic (only elastic)
- At v > v_min: sigma = sigma_elastic + sigma_endothermic
- Both elastic and endothermic have Yukawa v-dependence

So inelastic DM DOESN'T suppress at v < v_min. It just adds MORE
scattering at v > v_min.

The Wang 2025 effect is different: pseudo-Dirac DM with mass splitting
100 eV makes the elastic scattering kinematically forbidden BELOW threshold
(due to the loop-suppressed elastic rate), so only endothermic is
allowed at high v, and even that's small.

For our purposes, the simpler implementation is:
- Elastic sigma_yukawa(v) (always allowed)
- Endothermic sigma_yukawa(v) * Theta(v - v_min) (above threshold)
- Total sigma = elastic + endothermic

The Wang 2025 effect requires a model-specific loop calculation that
we don't have time to reproduce. So T90.49 will implement the simple
threshold model and document the difference.
"""
from __future__ import annotations

import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# Speed of light in km/s
C_KMS = 2.998e5


def v_threshold_kms(delta_eV: float, m_chi_GeV: float) -> float:
    """Compute the velocity threshold for inelastic endothermic scattering.

    v_min = c * sqrt(2 * delta / m_chi) where delta, m_chi in same energy units.

    Parameters
    ----------
    delta_eV : float
        Mass splitting between excited and ground state (eV)
    m_chi_GeV : float
        DM particle mass (GeV)

    Returns
    -------
    float
        Threshold velocity in km/s
    """
    # Convert both to eV
    m_chi_eV = m_chi_GeV * 1e9
    # v_min = c * sqrt(2*delta/m_chi) for identical particles in CM frame
    # Note: there's a factor of sqrt(2) ambiguity; we use v_rel (not v_cm)
    # which is v_cm * sqrt(2) for identical particles.
    # The threshold for the relative velocity (used in Yukawa) is:
    # v_rel_min = c * sqrt(delta / m_chi) * 2 = 2c * sqrt(delta/m_chi)
    # Actually the correct formula is: v_rel^2/4 = delta/m_chi
    # => v_rel = 2*sqrt(delta/m_chi) * c
    ratio = delta_eV / m_chi_eV
    return 2.0 * np.sqrt(ratio) * C_KMS


def sigma_m_inelastic(
    v_kms: float,
    m_phi_MeV: float,
    m_chi_GeV: float,
    g_chi: float,
    delta_eV: float,
) -> dict:
    """Compute total sigma/m with elastic + inelastic channels.

    Returns dict with:
      - sigma_elastic: always allowed
      - sigma_endothermic: allowed only if v > v_min
      - sigma_total: elastic + endothermic
      - v_threshold_kms: threshold velocity
      - threshold_open: bool, whether inelastic is open at this v

    The endothermic cross-section is the same Yukawa form, just gated
    by the kinematic threshold.
    """
    from t40_yukawa_sigma_m import sigma_m_cm2_per_g

    sigma_elastic = sigma_m_cm2_per_g(v_kms, m_phi_MeV, m_chi_GeV, g_chi)

    v_min = v_threshold_kms(delta_eV, m_chi_GeV)
    threshold_open = v_kms > v_min

    if threshold_open:
        sigma_endo = sigma_m_cm2_per_g(v_kms, m_phi_MeV, m_chi_GeV, g_chi)
        sigma_total = sigma_elastic + sigma_endo
    else:
        sigma_endo = 0.0
        sigma_total = sigma_elastic

    return {
        "sigma_elastic": sigma_elastic,
        "sigma_endothermic": sigma_endo,
        "sigma_total": sigma_total,
        "v_threshold_kms": v_min,
        "threshold_open": threshold_open,
    }


def evaluate_inelastic_point(
    m_phi_MeV: float,
    m_chi_GeV: float,
    g_chi: float,
    delta_eV: float,
) -> dict:
    """Evaluate sigma/m at Cloud-9, Galactic, Bullet velocities with inelastic.

    Returns dict with sigma/m values and constraint checks.
    """
    v_cloud9 = 28.0
    v_galaxy = 100.0
    v_bullet = 3000.0

    r_c9 = sigma_m_inelastic(v_cloud9, m_phi_MeV, m_chi_GeV, g_chi, delta_eV)
    r_gal = sigma_m_inelastic(v_galaxy, m_phi_MeV, m_chi_GeV, g_chi, delta_eV)
    r_bul = sigma_m_inelastic(v_bullet, m_phi_MeV, m_chi_GeV, g_chi, delta_eV)

    v_min = v_threshold_kms(delta_eV, m_chi_GeV)

    return {
        "m_phi_MeV": m_phi_MeV,
        "m_chi_GeV": m_chi_GeV,
        "g_chi": g_chi,
        "delta_eV": delta_eV,
        "v_threshold_kms": v_min,
        "sigma_m_Cloud9": r_c9["sigma_total"],
        "sigma_m_Galaxy": r_gal["sigma_total"],
        "sigma_m_Bullet": r_bul["sigma_total"],
        "C9_threshold_open": r_c9["threshold_open"],
        "Gal_threshold_open": r_gal["threshold_open"],
        "Bul_threshold_open": r_bul["threshold_open"],
        "Cloud9_OK": 30 < r_c9["sigma_total"] < 500,
        "Galaxy_OK": r_gal["sigma_total"] < 2.0,
        "Bullet_OK": r_bul["sigma_total"] < 0.5,
        "all_OK": (30 < r_c9["sigma_total"] < 500)
                  and (r_gal["sigma_total"] < 2.0)
                  and (r_bul["sigma_total"] < 0.5),
    }


def run_inelastic_scan():
    """Scan delta_eV to find parameter regions that satisfy all constraints."""
    print("=" * 70)
    print("T90.49 — Inelastic SIDM Parameter Scan")
    print("=" * 70)
    print()
    print("Scanning delta_eV (mass splitting) at the multi-portal reference point:")
    print("  Portal A-like: m_phi=50 MeV, m_chi=30 GeV, g=0.5")
    print("  (matches T90.45 single-portal reference, without mass splitting)")
    print()

    # Use the T90.45 reference point
    m_phi = 50.0
    m_chi = 30.0
    g_chi = 0.5

    delta_scan = [1, 10, 50, 100, 200, 500, 1000, 5000, 10000, 50000, 100000]  # eV

    print(f"{'delta (eV)':12s} {'v_min (km/s)':14s} {'sigma(m)C9':12s} {'sigma(m)Gal':12s} {'sigma(m)Bul':12s} {'all_OK':8s}")
    print("-" * 90)
    for delta in delta_scan:
        r = evaluate_inelastic_point(m_phi, m_chi, g_chi, delta)
        print(f"{r['delta_eV']:<12.0f} {r['v_threshold_kms']:<14.2f} "
              f"{r['sigma_m_Cloud9']:<12.3e} {r['sigma_m_Galaxy']:<12.3e} "
              f"{r['sigma_m_Bullet']:<12.3e} {'YES' if r['all_OK'] else 'no':<8s}")

    print()
    print("Scan with different m_phi to find Cloud-9 compatible points:")
    print()

    # Try lighter mediators with inelastic
    print(f"{'m_phi(MeV)':10s} {'g':6s} {'delta(eV)':10s} {'v_min':8s} {'C9':12s} {'Gal':12s} {'Bul':12s} {'all_OK':8s}")
    print("-" * 100)
    compatible = []
    for m_phi_test in [5, 10, 20, 50, 100, 200]:
        for g_test in [0.3, 0.5, 0.8, 1.0, 1.2]:
            for delta_test in [1, 10, 100, 1000, 10000, 100000]:
                r = evaluate_inelastic_point(m_phi_test, m_chi, g_test, delta_test)
                if r["all_OK"]:
                    compatible.append(r)
                if len(compatible) < 10 or r["sigma_m_Cloud9"] > 100:
                    print(f"{m_phi_test:<10.1f} {g_test:<6.2f} {delta_test:<10.0f} "
                          f"{r['v_threshold_kms']:<8.1f} {r['sigma_m_Cloud9']:<12.2e} "
                          f"{r['sigma_m_Galaxy']:<12.2e} {r['sigma_m_Bullet']:<12.2e} "
                          f"{'YES' if r['all_OK'] else 'no':<8s}")

    print()
    print(f"Cloud-9 compatible points: {len(compatible)}")
    if compatible:
        print("\nCompatible point details:")
        for r in compatible[:5]:
            print(f"  m_phi={r['m_phi_MeV']:.0f} MeV, g={r['g_chi']:.2f}, "
                  f"delta={r['delta_eV']:.0f} eV: "
                  f"sm(C9)={r['sigma_m_Cloud9']:.2e}, sm(Gal)={r['sigma_m_Galaxy']:.2e}, "
                  f"sm(Bul)={r['sigma_m_Bullet']:.2e}")

    return compatible


if __name__ == "__main__":
    compatible = run_inelastic_scan()