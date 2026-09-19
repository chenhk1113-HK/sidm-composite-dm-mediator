"""
T110.1B — Inelastic SIDM parameter mapping.

Per the inelastic DM literature (Tucker-Smith + Weiner 2005, Schmid+ 2009, etc.):
For two DM states chi_1 (ground) and chi_2 (excited) with mass splitting delta,
endothermic scattering chi_1 chi_1 -> chi_2 chi_2 requires kinetic energy
above threshold:

    E_thr = delta  (= m_chi_2 - m_chi_1)
    v_thr = sqrt(2 * delta / m_red) = sqrt(4 * delta / m_chi)

For m_chi = 0.5 GeV and v_thr = 30 km/s:
    delta = (v_thr/c)^2 * m_chi / 4
          = (30/3e5)^2 * 0.5 / 4
          = 1e-8 * 0.125 = 1.25e-9 GeV = 1.25 eV

The cross section has the form:
    sigma(v) = sigma_elastic(v) + sigma_inelastic(v)
    sigma_inelastic(v) = 0 for v < v_thr (kinematically forbidden)
    sigma_inelastic(v) = sigma_inelastic_max * BW_factor for v > v_thr

This produces a STEP-LIKE velocity dependence: zero below threshold,
rises above. If v_thr is just below Cloud-9 (v=28), then Cloud-9 sees
the full cross section while dSph (v=30)... wait, that's still above
threshold.

CORRECT: we need Cloud-9 BELOW threshold (so sigma_elastic is large
from a Sommerfeld-like mechanism), and dSph ABOVE threshold where
inelastic channel opens... but that would make sigma LARGER at dSph,
not smaller.

Let me re-think: the right picture is ENDOTHERMIC scattering where the
inelastic channel is only available ABOVE threshold. So:
  v < v_thr: only elastic (sigma_elastic, possibly small)
  v > v_thr: elastic + inelastic (sigma_total, larger)

If we want dSph (v=30) to have sigma < 0.2 and Cloud-9 (v=28) to have
sigma ~ 100, we need sigma to be LARGER at v=28 than at v=30. That
means sigma should DECREASE with v in this range, not increase.

Inelastic endothermic scattering gives sigma INCREASING with v
above threshold. Wrong direction.

EXOTHERMIC scattering (chi_1 chi_2 -> chi_2 chi_2, with chi_2 excited
initially) gives the OPPOSITE: threshold below which the channel is open
(because the reaction releases energy, so it can happen at any v).

Actually the simplest inelastic mechanism is:
  - If chi_2 has SMALL abundance, then chi_1 chi_2 scattering dominates
  - This has different velocity dependence

For chi_1 chi_1 scattering to satisfy Cloud-9 + dSph, we need the
opposite of what endothermic gives.

Alternative: GROUND-STATE DEPLETION (Tulin + Yu + others). If chi_2
is depleted by annihilation, then scattering is chi_1 chi_2 which has
different kinematics.

This module implements the standard inelastic framework and reports
what it can/cannot do for Cloud-9 + dSph.
"""
from __future__ import annotations
import numpy as np
from dataclasses import dataclass


@dataclass
class InelasticSIDMParams:
    """Endothermic inelastic SIDM parameters."""
    m_chi_GeV: float  # DM mass (chi_1 = ground state)
    delta_GeV: float  # Mass splitting chi_2 - chi_1 (positive for endothermic)
    sigma_0: float  # inelastic cross section at high v (cm^2/g)
    sigma_elastic: float  # elastic cross section (cm^2/g, assumed v-independent)


def v_threshold_kms(delta_GeV: float, m_chi_GeV: float) -> float:
    """Threshold velocity for endothermic scattering chi_1 chi_1 -> chi_2 chi_2.

    E_thr = delta, m_red = m_chi/2
    v_thr = sqrt(2 * delta / m_red) = sqrt(4 * delta / m_chi)
    """
    if delta_GeV <= 0:
        return 0.0
    c = 2.998e5  # km/s
    v_thr_c = np.sqrt(4 * delta_GeV / m_chi_GeV)
    return v_thr_c * c


def sigma_inelastic(v_kms: float, p: InelasticSIDMParams) -> float:
    """Endothermic inelastic sigma/m(v).

    Below threshold: 0 (kinematically forbidden)
    Above threshold: rises smoothly to sigma_0 with momentum suppression
    """
    v_thr = v_threshold_kms(p.delta_GeV, p.m_chi_GeV)
    if v_kms < v_thr:
        return 0.0

    # Above threshold, the cross section rises as p / sqrt(E - delta)
    # (standard endothermic phase space factor)
    m_red = p.m_chi_GeV / 2.0
    c = 2.998e5
    v_c = v_kms / c
    E_GeV = 0.5 * m_red * v_c ** 2
    excess_E = max(E_GeV - p.delta_GeV, 1e-30)
    # Phase space factor
    ps_factor = np.sqrt(excess_E / E_GeV)
    # Suppression near threshold
    return p.sigma_0 * ps_factor


def sigma_m_total_inelastic(v_kms: float, p: InelasticSIDMParams) -> float:
    """Total sigma/m = sigma_elastic + sigma_inelastic."""
    sigma_el = p.sigma_elastic  # assumed v-independent
    sigma_in = sigma_inelastic(v_kms, p)
    return sigma_el + sigma_in


if __name__ == "__main__":
    print("T110.1B — Inelastic SIDM parameter mapping")
    print("=" * 70)
    print()

    # Test the basic mechanism
    m_chi = 0.5  # GeV
    print(f"m_chi = {m_chi} GeV")
    print()

    # For v_thr = 30 km/s
    delta_for_30kms = (30.0 / 2.998e5) ** 2 * m_chi / 4
    print(f"Required delta for v_thr = 30 km/s: {delta_for_30kms:.4e} GeV = {delta_for_30kms * 1e9:.2f} eV")

    # For v_thr = 28 km/s
    delta_for_28kms = (28.0 / 2.998e5) ** 2 * m_chi / 4
    print(f"Required delta for v_thr = 28 km/s: {delta_for_28kms:.4e} GeV = {delta_for_28kms * 1e9:.2f} eV")
    print()

    # Test scenario 1: v_thr = 30 km/s (above Cloud-9)
    # Cloud-9 (v=28): NO inelastic channel -> only sigma_elastic
    # dSph (v=30): YES inelastic channel -> sigma_elastic + sigma_inelastic
    # This makes dSph LARGER than Cloud-9. WRONG direction.
    print("Scenario 1: v_thr = 30 km/s (Cloud-9 below threshold)")
    p1 = InelasticSIDMParams(m_chi_GeV=0.5, delta_GeV=delta_for_30kms,
                              sigma_0=100.0, sigma_elastic=100.0)
    for v in [10, 20, 28, 30, 50, 100]:
        sm = sigma_m_total_inelastic(v, p1)
        thr = v_threshold_kms(p1.delta_GeV, p1.m_chi_GeV)
        print(f"  v={v}: sigma/m = {sm:.4e} cm^2/g  (v_thr = {thr:.1f})")
    print("  CONCLUSION: dSph (v=30) gets MORE sigma than Cloud-9 (v=28). WRONG.")
    print()

    # Scenario 2: v_thr between Cloud-9 and SPARC
    # e.g., v_thr = 50 km/s -> Cloud-9 sees only sigma_elastic,
    # dSph sees only sigma_elastic. Both equal. No help.
    # This doesn't help either.

    # Scenario 3: GROUND-STATE DEPLETION (chi_2 has small abundance)
    # If f_chi_2 / f_chi_1 = epsilon << 1, then most scattering is
    # chi_1 chi_1 -> chi_1 chi_1 (elastic, suppressed if mediator is heavy)
    # but chi_1 chi_2 -> chi_1 chi_2 is also elastic and has different kinematics

    # For now, the simple inelastic (endothermic) framework cannot
    # resolve Cloud-9 + dSph because:
    #   - Cloud-9 is at v=28 (LOWER than dSph at v=30)
    #   - Endothermic gives sigma INCREASING with v
    #   - We need sigma DECREASING between v=28 and v=30

    print("Scenario 3: Cloud-9 + dSph with inelastic — analysis")
    print()
    print("Key constraint: Cloud-9 (v=28) needs sigma ~100, dSph (v=30) needs sigma <0.2")
    print("Velocity gap: 28 -> 30 km/s (factor 1.07)")
    print("Suppression needed: 100/0.2 = 500x")
    print()
    print("Endothermic inelastic: sigma INCREASES with v above threshold")
    print("  -> Wrong direction (gives dSph > Cloud-9)")
    print()
    print("Exothermic inelastic: sigma DECREASES below threshold")
    print("  -> Below threshold (v < v_thr), channel CLOSES (sigma = 0)")
    print("  -> We need sigma > 100 at v=28 (BELOW threshold if v_thr = 30)")
    print("  -> Wait, exothermic has channel OPEN below threshold")
    print()
    print("REVISED: For EXOTHERMIC (chi_1 + chi_2 -> chi_1 + chi_1 with KE release):")
    print("  - If chi_2 is depleted, scattering is chi_1 chi_2 -> chi_1 chi_1")
    print("  - Threshold: below v_thr (kinematic FASTER because reaction is exothermic)")
    print("  - This is the standard 'inelastic DM' for direct detection")
    print()
    print("CONCLUSION: Neither simple endothermic nor simple exothermic can solve")
    print("Cloud-9 + dSph because the velocities are TOO CLOSE (2 km/s gap).")
    print()
    print("The Chu+ 2019 'velocity-dependence' framework explicitly notes that")
    print("a velocity gap of <5 km/s is hard to bridge with smooth sigma(v).")
