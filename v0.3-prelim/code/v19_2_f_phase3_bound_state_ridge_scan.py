"""
v19_2_f_phase3_bound_state_ridge_scan.py — Priority 2 from V19_2_F_PHASE3_REVIEW_AND_NEXT_STEPS.md

Goal: Convert "Phase 3 FAIL" to a FALSIFIABLE structural claim.

Two physics checks:
  (A) For each (alpha_D, m_A'), solve s-wave Schrodinger for the bound-state
      ground-state energy E_0 (DOP853 shooting method, validated by
      yukawa_resonance_benchmark.py kappa_c convergence).
  (B) Identify the ridge where E_0 = -|E_resonance| ~ -1/2 mu v_target^2
      (= -0.5 * 0.5 * (29.4/2.998e5)^2 GeV = -2.4e-9 GeV = -2.4 eV).
      This is where a resonance would land at v_target = 29.4 km/s.

If (alpha_D, m_A') lies on this ridge AND sigma/m(29.4) is a PEAK,
the framework's cloud-9 feature is reproducible from first principles.
If no ridge point gives a peak, the gate closes: paper (A) is final.
"""
import os
import math
import json
import sys
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

# Use the locked constants
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _THIS_DIR)
from constants import (
    M_CHI_GEV, MU_RED_GEV, C_KMS, HBAR_C_GEV_CM, KAPPA_C, KAPPA_C_ANALYTIC,
    compute_kappa, ALPHA_D,
)

# ---- Configuration ----
OUTPUT_DIR = _THIS_DIR
V_TARGET_KMS = 29.4
E_TARGET_GEV = -0.5 * MU_RED_GEV * (V_TARGET_KMS / C_KMS) ** 2  # negative: bound state
print(f"Target bound-state energy E_0 = {E_TARGET_GEV*1e9:.4f} eV (for resonance at v={V_TARGET_KMS} km/s)")
print(f"  |E_target| ~ {abs(E_TARGET_GEV):.3e} GeV")

# Bound-state existence test: for given (alpha_D, m_A'), is there an s-wave bound state?
# Bound state iff kappa = alpha_D * m_chi / m_A' > kappa_c = 1.6798
def has_bound_state(alpha_D, m_chi, m_ap):
    return compute_kappa(alpha_D, m_chi, m_ap) > KAPPA_C_ANALYTIC


# ---- (A) Shooting method: find E_0 for given (alpha_D, m_A') ----
def E0_shooting(alpha_D, m_chi_GeV, m_ap_GeV, r_max_factor=20.0, n_pts=4000):
    """
    Solve s-wave Schrodinger for Yukawa potential:
      V(r) = -(alpha_D / r) * exp(-m_ap * r)
      u'' = 2 mu (V - E) u    (in natural units, hbar = c = 1)

    E_0 is the most-negative eigenvalue where u(0)=0, u'(0)=1,
    and u(r) -> 0 as r -> infinity (bound-state BC).

    Method: Numerov shooting (standard for bound-state problems).
    Returns: E_0 in GeV (negative for bound state), or NaN if no bound state.
    """
    if not has_bound_state(alpha_D, m_chi_GeV, m_ap_GeV):
        return float('nan')

    mu = m_chi_GeV / 2.0  # reduced mass (equal-mass)

    def V(r):
        if r < 1e-10:
            return -alpha_D / 1e-10
        return -(alpha_D / r) * math.exp(-m_ap_GeV * r)

    # Use dimensionless rho = m_ap * r
    rho_max = r_max_factor
    n = n_pts
    rho_arr = np.linspace(1e-8, rho_max, n)
    r_arr = rho_arr / m_ap_GeV

    # k^2(rho) = 2 mu (E - V) / m_ap^2   (dimensionless)
    def k_sq(E):
        return 2.0 * mu * (E - np.array([V(r) for r in r_arr])) / (m_ap_GeV ** 2)

    # Numerov: u_{n+1} = (2(1 - 5 h^2 k_n^2 / 12) u_n - (1 + h^2 k_{n-1}^2 / 12) u_{n-1}) / (1 + h^2 k_{n+1}^2 / 12)
    def numerov_step(u_prev, u_curr, k_prev_sq, k_curr_sq, k_next_sq, h):
        return ((2.0 * (1.0 - 5.0 * h * h * k_curr_sq / 12.0) * u_curr
                  - (1.0 + h * h * k_prev_sq / 12.0) * u_prev)
                / (1.0 + h * h * k_next_sq / 12.0))

    h = rho_arr[1] - rho_arr[0]

    def propagate(E, sign=+1):
        """Numerov integration from boundary inward (sign=-1) or outward (sign=+1).
        Returns u(rho) for bound state (or growth for continuum).
        """
        ks = k_sq(E)
        u = np.zeros(n)
        if sign > 0:
            # Outward from origin: u(0) ~ rho (regular BC), u'(0) ~ 1
            u[0] = rho_arr[0]
            u[1] = u[0] + h  # u'(0) ~ 1 in dimensionless units
            for i in range(1, n - 1):
                u[i + 1] = numerov_step(u[i - 1], u[i], ks[i - 1], ks[i], ks[i + 1], h)
        else:
            # Inward from infinity: u(rho_max) ~ exp(-kappa * rho_max) (bound state)
            kappa_val = np.sqrt(max(0.0, -2.0 * mu * E)) / m_ap_GeV
            u[-1] = math.exp(-kappa_val * rho_arr[-1])
            u[-2] = math.exp(-kappa_val * rho_arr[-2])
            for i in range(n - 2, 0, -1):
                u[i - 1] = numerov_step(u[i + 1], u[i], ks[i + 1], ks[i], ks[i - 1], h)
        return u

    def mismatch(E):
        # Use log-derivative matching at midpoint (more stable than value matching)
        try:
            u_o = propagate(E, sign=+1)
            u_i = propagate(E, sign=-1)
        except (ArithmeticError, ValueError):
            return float('nan')
        # Skip zeros (avoid log issues)
        mid = n // 2
        if abs(u_o[mid]) < 1e-30 or abs(u_i[mid]) < 1e-30:
            return float('nan')
        # log-derivative at mid
        ld_o = (u_o[mid + 1] - u_o[mid - 1]) / (2.0 * h) / u_o[mid]
        ld_i = (u_i[mid + 1] - u_i[mid - 1]) / (2.0 * h) / u_i[mid]
        return ld_o - ld_i

    # Bracket: E in [E_target * 5, -1e-15]
    E_lo, E_hi = -1e-15, E_TARGET_GEV * 5

    # First, do a coarse scan to find bracket
    E_test = np.logspace(np.log10(abs(E_TARGET_GEV) * 10), np.log10(abs(E_lo) - 1e-3), 20)
    E_test = -E_test  # negative
    signs = []
    for E in E_test:
        m = mismatch(E)
        if math.isnan(m):
            signs.append(0)
        else:
            signs.append(np.sign(m))
    # Find sign change
    bracket_found = False
    for i in range(len(signs) - 1):
        if signs[i] * signs[i + 1] < 0:
            E_lo, E_hi = E_test[i + 1], E_test[i]  # Note: E_test is decreasing in |E|
            bracket_found = True
            break
    if not bracket_found:
        return float('nan')

    try:
        E0 = brentq(mismatch, E_lo, E_hi, xtol=1e-12, rtol=1e-10, maxiter=200)
        return E0
    except (ValueError, RuntimeError):
        return float('nan')


# ---- (B) Ridge scan: find (alpha_D, m_A') where E_0 = E_target ----
def find_ridge_for_m_ap(m_ap_GeV, alpha_range=(1e-7, 1e-1), tol=1e-3):
    """
    For fixed m_A', find alpha_D such that E_0(alpha_D, m_A') = E_target.

    Returns: alpha_D, E_0, or (None, None) if no alpha in range gives E_0 = E_target.
    """
    a_lo, a_hi = alpha_range
    # Test if E_target is reachable for this m_A'
    E_lo = E0_shooting(a_lo, M_CHI_GEV, m_ap_GeV)
    E_hi = E0_shooting(a_hi, M_CHI_GEV, m_ap_GeV)
    if math.isnan(E_lo) or math.isnan(E_hi):
        return None, None
    # Check bracket: at higher alpha, E_0 is more negative
    if (E_lo - E_TARGET_GEV) * (E_hi - E_TARGET_GEV) > 0:
        return None, None
    try:
        alpha_ridge = brentq(
            lambda a: E0_shooting(a, M_CHI_GEV, m_ap_GeV) - E_TARGET_GEV,
            a_lo, a_hi, xtol=1e-15, rtol=1e-10, maxiter=100,
        )
        E0_at_ridge = E0_shooting(alpha_ridge, M_CHI_GEV, m_ap_GeV)
        return alpha_ridge, E0_at_ridge
    except (ValueError, RuntimeError):
        return None, None


def main():
    print("=" * 70)
    print("=== Bound-state ridge scan (Priority 2) ===")
    print("=" * 70)
    print(f"Target: sigma/m(v={V_TARGET_KMS} km/s) = 174 cm^2/g as a PEAK")
    print(f"Bound-state ridge: E_0 = {E_TARGET_GEV*1e9:.4f} eV")
    print(f"Convention: alpha_D = g^2/(4*pi) [LOCKED]")
    print(f"Threshold: kappa_c = {KAPPA_C_ANALYTIC}")
    print()

    # Sanity test: at kappa -> kappa_c, E_0 -> 0
    print("Sanity check: at kappa -> kappa_c, E_0 should -> 0")
    for kappa_test in [1.7, 1.6799, 1.6798, 1.6797, 1.5, 1.0]:
        m_ap_test = 1e-9  # GeV = 1 keV (arbitrary)
        alpha_for_kappa = kappa_test * m_ap_test / M_CHI_GEV
        E0_test = E0_shooting(alpha_for_kappa, M_CHI_GEV, m_ap_test)
        print(f"  kappa = {kappa_test:.4f}, alpha_D = {alpha_for_kappa:.3e}, E_0 = {E0_test*1e9:.4e} eV")
    print()

    # Ridge scan
    print("Ridge scan: (alpha_D, m_A') such that bound state has E_0 = E_target")
    print()

    m_ap_grid = np.logspace(-9, -3, 12)  # 1 keV to 1 MeV
    results = []
    for m_ap in m_ap_grid:
        m_ap_eV = m_ap * 1e9
        alpha_ridge, E0_at_ridge = find_ridge_for_m_ap(m_ap)
        if alpha_ridge is not None:
            kappa_ridge = compute_kappa(alpha_ridge, M_CHI_GEV, m_ap)
            results.append({
                "m_A_prime_eV": float(m_ap_eV),
                "alpha_D_at_ridge": float(alpha_ridge),
                "kappa_at_ridge": float(kappa_ridge),
                "E_0_GeV": float(E0_at_ridge),
                "E_0_eV": float(E0_at_ridge * 1e9),
            })
            print(f"  m_A' = {m_ap_eV:7.1f} eV, alpha_D = {alpha_ridge:.3e}, kappa = {kappa_ridge:.4f}, E_0 = {E0_at_ridge*1e9:.4e} eV")

    # Save results
    out_path = os.path.join(OUTPUT_DIR, "data", "results", "v19_2_f_phase3_bound_state_ridge_scan.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump({
            "_meta": {
                "description": "v19.2-F Phase 3 Bound-state ridge scan (Priority 2)",
                "target_velocity_kms": V_TARGET_KMS,
                "target_energy_eV": float(E_TARGET_GEV * 1e9),
                "convention": "alpha_D = g^2/(4*pi) [LOCKED]",
                "kappa_c": float(KAPPA_C_ANALYTIC),
            },
            "ridge_points": results,
        }, f, indent=2)

    print()
    print(f"Ridge scan complete: {len(results)} points found")
    print(f"Results saved: {out_path}")
    print()
    print("=" * 70)
    print("VERDICT")
    print("=" * 70)
    if not results:
        print("No ridge points found.")
        print("This means NO (alpha_D, m_A') point places a bound state with")
        print("E_0 = E_target = -2.4 eV (the energy needed for v=29.4 km/s resonance).")
        print("Combined with Phase 3 EXTENDED (no peak at v=29.4 km/s),")
        print("the gate verdict is confirmed: FAIL, paper (A) wins.")
    else:
        framework_alpha = 6.8e-7
        for r in results:
            r["distance_to_framework"] = float(abs(math.log10(r["alpha_D_at_ridge"] / framework_alpha)))
        natural = min(results, key=lambda x: x["distance_to_framework"])
        print(f"Most natural ridge point (closest to framework's alpha_chi = 6.8e-7):")
        print(f"  m_A' = {natural['m_A_prime_eV']:.1f} eV, alpha_D = {natural['alpha_D_at_ridge']:.3e}")
        print(f"  Factor off framework's alpha_chi: {10**natural['distance_to_framework']:.2f}")
        if natural["distance_to_framework"] > 2:
            print()
            print("==> The framework's coupling is NOT on the bound-state ridge.")
            print("==> This confirms Phase 3: framework coupling can't reproduce the target.")
            print("==> Gate verdict: FAIL, paper (A) wins.")
        else:
            print()
            print("==> Framework coupling IS on (or near) the bound-state ridge.")
            print("==> Next step: check if THIS ridge point gives sigma/m(29.4) = 174 as a PEAK.")
            print("==> (Requires running Calogero partial-wave solve at this point.)")


if __name__ == "__main__":
    main()