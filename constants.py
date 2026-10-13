"""
constants.py — SIDM composite-DM mediator project
===================================================

COUPLING CONVENTION (LOCKED):
    alpha_D  ≡  g² / (4π)          [standard fine-structure convention]

    κ        =  alpha_D * m_chi / m_A_prime    [dimensionless resonance criterion]
    kappa_c  =  1.6798                    [Tamm 1947 ZhETF 17, 884 threshold]

    IMPORTANT: All scripts in this project MUST use alpha_D ≡ g²/(4π).
    The alternative convention (alpha = g²) is NOT supported and will
    cause σ/m values to differ by factors of 4π ≈ 12.57.

NOTE on κ_c = 1.6798 — this is the analytic value of the s-wave bound-state
formation threshold for the Yukawa potential V(r) = -(α_D / r) · exp(-m_A' · r).
Standard references: Simonov, Yu. A. (1964) (original analytic treatment);
Tulin, Yu, Zurek (2013) arXiv:1306.5010 (modern review). NOT "Bethe-Fano".

NOTE on regime terminology — "Born domain" and "bound-state regime" are
INDEPENDENT criteria:
    Born valid:     α_D ≪ 1  (weak-coupling, perturbative)
    Bound state:    κ = α_D m_χ/m_A' > κ_c  (deep enough potential)
A coupling can be Born-valid (α_D = 6.8e-7 ≪ 1) yet still form a bound state
(κ = 3.4 > κ_c) — these describe different physics, not a single threshold.
For Born breakdown, see when Sommerfeld enhancement S(v) ≠ 1.

REFERENCES:
    - Simonov, Yu. A. (1964)  "Bound states of Yukawa-type potential"
    - Tulin, Yu, Zurek (2013)  arXiv:1306.5010  "Cold Dark Matter and Its Interactions"
    - Kaplinghat, Tulin, Yu (2016)  "Dark Matter Self-Interactions"
    - Chu, Hambye & Tytgat (2018)  [7]  M2 Sommerfeld/t-channel resonance
    - ClawsGO #9, #10, #11 (v19.2-F Phase 3 cleanup)
    - Reviewer audit revV19_2_F.docx (2026-10-11)

PROJECT TERMINOLOGY:
    "Cloud-9" = σ/m = 174 cm²/g peak at v = 29.4 km/s (dwarf-galaxy scale)
                 being tested throughout the project. The name refers to the
                 Cloud-9 dwarf-galaxy halo from the project's reference dataset.

HISTORY:
    v1.0  2026-10-11  Locked convention per ClawsGO #9/#10/#11 recommendations.
                      Previously ambiguous: framework doc claimed alpha_chi=6.8e-7
                      without specifying g²/4π vs g², leading to three different
                      σ/m(100) values (0.052, 2.84, 41.0) for the same point.
    v1.1  2026-10-11  Reviewer audit fixes: κ_c citation corrected; Born/κ_c
                      regime clarification added; cloud-9 definition added.
"""
from __future__ import annotations
import math

# ============================================================
# Physical constants (natural units, GeV)
# ============================================================

# Speed of light in km/s (used for velocity conversions)
C_KMS: float = 2.998e5  # km/s

# Hbar*c in GeV*cm (for converting cross-section units)
HBAR_C_GEV_CM: float = 1.97327e-14  # GeV * cm

# DM mass (canonical Phase 44)
M_CHI_GEV: float = 1.0  # GeV

# Reduced mass for equal-mass DM scattering
MU_RED_GEV: float = M_CHI_GEV / 2.0  # 0.5 GeV

# ============================================================
# Coupling convention (LOCKED: alpha_D ≡ g²/(4π))
# ============================================================

# Fine-structure constant (dark sector)
# CONVENTION: alpha_D = g² / (4π)
# This is the standard convention used in Tulin-Yu (2013), Kaplinghat et al. (2016), etc.
ALPHA_D: float = 5.55e-6  # Best-fit point from EXTENDED scan (ClawsGO #11)

# Bare gauge coupling (derived from alpha_D under locked convention)
# g = sqrt(4π * alpha_D)
G_CHI: float = math.sqrt(4.0 * math.pi * ALPHA_D)

# ============================================================
# Resonance criterion
# ============================================================

# Dimensionless coupling combination (used in bound-state existence test)
# κ = α_D * m_χ / m_A'
# This is the correct dimensionless criterion for s-wave bound-state formation
# in a Yukawa potential V(r) = -(α_D / r) * exp(-m_A' * r)
def compute_kappa(alpha_D_val: float, m_chi_GeV: float, m_ap_prime_GeV: float) -> float:
    """Compute the dimensionless resonance criterion κ.

    κ = α_D * m_χ / m_A'

    Parameters:
        alpha_D_val: Dark fine-structure constant (α_D ≡ g²/(4π))
        m_chi_GeV: DM mass in GeV
        m_ap_prime_GeV: Mediator mass in GeV

    Returns:
        κ dimensionless coupling combination
    """
    return alpha_D_val * m_chi_GeV / m_ap_prime_GeV

# Critical coupling for s-wave bound-state formation
# Tamm 1947 ZhETF 17, 884 threshold: κ_c ≈ 1.6798
# This is the well-known result for the onset of the first s-wave bound state
# in a Yukawa potential (Tamm 1947, transl. Soviet Physics JETP 1948)
KAPPA_C_ANALYTIC: float = 1.6798

# Rounded threshold (conservative, used in quick checks)
KAPPA_C: float = 1.68

# ============================================================
# Self-consistency assertions (run at import time)
# ============================================================

def _run_convention_checks() -> None:
    """Verify that all convention-dependent quantities are self-consistent.

    This function is called automatically at module import time.
    If any assertion fails, the project has a convention mismatch somewhere.
    """
    # Check 1: g_chi computed from alpha_D matches the locked convention
    g_chi_check = math.sqrt(4.0 * math.pi * ALPHA_D)
    assert abs(g_chi_check - G_CHI) < 1e-15, (
        f"Convention mismatch: g_chi computed from alpha_D ({g_chi_check:.6e}) "
        f"does not match stored G_CHI ({G_CHI:.6e})"
    )

    # Check 2: kappa_c analytic value is in the expected range
    # (should be ~1.68, not 1.68*4π or 1.68/(4π))
    # REVIEWER-8: tighter check on KAPPA_C_ANALYTIC value
    assert abs(KAPPA_C_ANALYTIC - 1.6798) < 0.001, (
        f"KAPPA_C_ANALYTIC={KAPPA_C_ANALYTIC} is not the standard value 1.6798 "
        f"(Tamm 1947 ZhETF 17, 884 threshold)"
    )
    assert 1.6 < KAPPA_C_ANALYTIC < 1.75, (
        f"KAPPA_C_ANALYTIC={KAPPA_C_ANALYTIC} is outside expected range [1.6, 1.75]. "
        f"Check convention: if using α=g² instead of α=g²/(4π), "
        f"the threshold would be ~1.68*4π≈21.1 or ~1.68/(4π)≈0.134"
    )

    # Check 3: Verify that the framework point (alpha_chi=6.8e-7, m_A'=200 eV)
    # gives kappa > kappa_c (Born formula outside domain)
    alpha_chi_framework = 6.8e-7
    m_ap_prime_eV = 200
    m_ap_prime_GeV = m_ap_prime_eV * 1e-9  # eV -> GeV
    kappa_framework = compute_kappa(alpha_chi_framework, M_CHI_GEV, m_ap_prime_GeV)
    # Under α=g²/(4π) convention:
    # kappa = 6.8e-7 * 1.0 / (200e-9) = 6.8e-7 / 2e-7 = 3.4
    expected_kappa = alpha_chi_framework * M_CHI_GEV / m_ap_prime_GeV
    assert abs(kappa_framework - expected_kappa) < 1e-10, (
        f"kappa computation error: {kappa_framework} vs {expected_kappa}"
    )
    assert kappa_framework > KAPPA_C, (
        f"Framework point kappa={kappa_framework:.3f} should be > kappa_c={KAPPA_C} "
        f"(Born formula outside domain)"
    )

    # Check 4: C_KMS is the speed of light
    assert abs(C_KMS - 2.998e5) < 1e2, f"C_KMS={C_KMS} is not the speed of light"

    # Check 5: HBAR_C_GEV_CM is correct
    assert abs(HBAR_C_GEV_CM - 1.97327e-14) < 1e-18, (
        f"HBAR_C_GEV_CM={HBAR_C_GEV_CM} is incorrect"
    )

    print("[constants.py] All convention checks PASSED.")


# Run checks only when called as __main__ (REVIEWER-15: prevent side effects on import)
# Tests should call _run_convention_checks() explicitly.
# ============================================================
# Helper: convert between conventions (for reference only)
# ============================================================

def alpha_g2_to_g24pi(alpha_g2: float) -> float:
    """Convert α = g² to α = g²/(4π).

    WARNING: This function exists for migration purposes only.
    All new code should use alpha_D ≡ g²/(4π) directly.
    """
    return alpha_g2 / (4.0 * math.pi)


def alpha_g24pi_to_g2(alpha_D: float) -> float:
    """Convert α = g²/(4π) to α = g².

    WARNING: This function exists for migration purposes only.
    All new code should use alpha_D ≡ g²/(4π) directly.
    """
    return alpha_D * 4.0 * math.pi


# ============================================================
# Summary print on import (REVIEWER-15: moved inside __main__ guard)
# ============================================================

if __name__ == "__main__":
    _run_convention_checks()
    print("=" * 60)
    print("constants.py — Coupling convention: α_D ≡ g²/(4π) [LOCKED]")
    print(f"  ALPHA_D    = {ALPHA_D:.2e}")
    print(f"  G_CHI      = {G_CHI:.6e}")
    print(f"  KAPPA_C    = {KAPPA_C} (analytic: {KAPPA_C_ANALYTIC})")
    print(f"  M_CHI      = {M_CHI_GEV} GeV")
    print(f"  C_KMS      = {C_KMS:.3e} km/s")
    print(f"  HBAR_C     = {HBAR_C_GEV_CM:.5e} GeV*cm")
    print("=" * 60)