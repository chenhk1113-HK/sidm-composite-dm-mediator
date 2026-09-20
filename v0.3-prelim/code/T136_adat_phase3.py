"""
T136 — Phase 3: Multi-channel asymmetric DM scattering

Phase 1-2 showed: simple Born-Yukawa doesn't give α_γ ≈ 1.
Phase 2 showed: simple Yukawa doesn't easily give 4 resonances.

Phase 3 hypothesis: MULTI-CHANNEL asymmetric DM
  - p_D (dark proton): Yukawa with one set of resonances
  - e_D (dark electron): Yukawa with another set
  - HD (dark atom): bound-state-enhanced

Each channel contributes σ/m(v), and total is sum.
Different masses → different velocity scales for resonances.
This could give 4-peak structure with α_γ ≈ 1.

Reference: Petraki-Pearce-Kusenko 2014 (multi-species DM)
            Cline et al. (atomic DM self-scattering)
"""
import numpy as np
import json

# ============================================================
# Multi-channel asymmetric DM framework
# ============================================================

# Component masses (from asymmetric relic density):
# m_p (dark proton): heavier, sets most of DM mass
# m_e (dark electron): lighter, balances charges
# m_HD = m_p + m_e - Δ (binding): atomic bound state

# Our phenomenology has 3:1 mass ratio (T120.13).
# In ADAT (Asymmetric Dark Atom Theory), this comes from:
# m_p/m_e such that HD binding energy is stable

# ============================================================
# Non-perturbative σ/m(v) for asymmetric Yukawa
# ============================================================

def sigma_yukawa_resonance(v_kms, alpha_D, m_A_prime_GeV, m_chi_GeV, v_target_kms, width_kms):
    """Yukawa cross-section with Breit-Wigner resonance at v_target.
    
    σ/m = σ_0 × BW_factor + Born_background
    
    BW_factor: resonance enhancement at v_target
    Born_background: off-resonance, σ ∝ v^(-4) or v^(-2)
    """
    # Convert v to natural units
    v_natural = v_kms * 1e3 / 3e8
    
    # Born-Yukawa background (per Cassel 2009)
    # σ_Born ≈ 4π α_D² / (m_A'^4 v²)  for v << m_A'/μ
    sigma_born = 4 * np.pi * alpha_D**2 / (m_A_prime_GeV**4 * v_natural**2)
    
    # Breit-Wigner resonance enhancement
    # σ_resonance = σ_peak × (Γ/2)² / ((v - v_target)² + (Γ/2)²)
    v_target_natural = v_target_kms * 1e3 / 3e8
    width_natural = width_kms * 1e3 / 3e8
    sigma_peak = 4 * np.pi / (m_A_prime_GeV * v_target_natural)**2
    
    bw_factor = sigma_peak * (width_natural/2)**2 / ((v_natural - v_target_natural)**2 + (width_natural/2)**2)
    
    return sigma_born + bw_factor

def sigma_yukawa_4peaks(v_kms, alpha_D, m_A_prime_GeV, m_chi_GeV):
    """4-resonance model: peaks at 28, 100, 178, 430 km/s.
    
    Each resonance corresponds to a different bound state or partial wave.
    """
    # 4 resonances at specific velocities
    peaks = [
        (28, 15),    # Cloud-9 peak (narrow, σ/m = 128 cm²/g)
        (100, 50),   # SPARC peak
        (178, 60),   # subhalo peak
        (430, 80),   # cluster peak (broad)
    ]
    
    sigma_total = np.zeros_like(v_kms, dtype=float)
    for v_target, width in peaks:
        sigma_total += sigma_yukawa_resonance(
            v_kms, alpha_D, m_A_prime_GeV, m_chi_GeV, v_target, width
        )
    
    return sigma_total

# ============================================================
# Test: does this give our 8 data points?
# ============================================================

# Our 8 data points (from phenomenology)
v_data_km_s = np.array([3, 5, 7, 10, 15, 28, 100, 500])
sigma_over_m_data = np.array([0.155, 0.093, 0.067, 0.047, 0.032, 128.0, 0.193, 2.5e-4])

# Test 1: Tune alpha_D and m_A_prime
print("=" * 70)
print("T136 — PHASE 3: MULTI-CHANNEL ADAT TEST")
print("=" * 70)
print()

# Try a few parameter combinations
results = []
for alpha_D_test, m_A_prime_test in [
    (0.01, 0.001),
    (0.05, 0.01),
    (0.1, 0.05),
    (0.3, 0.1),
]:
    sigma_pred = sigma_yukawa_4peaks(v_data_km_s, alpha_D_test, m_A_prime_test, m_chi_GeV=20)
    
    # Convert to cm²/g
    sigma_pred_cm2_g = sigma_pred / (20 * 1.78e-24 * 0.197e-13)
    
    # Compute residuals
    residuals = np.log10(sigma_pred_cm2_g) - np.log10(sigma_over_m_data)
    rmse = np.sqrt(np.mean(residuals**2))
    
    print(f"\nα_D={alpha_D_test}, m_A'={m_A_prime_test} GeV:")
    print(f"  RMSE = {rmse:.3f}")
    for v, obs, pred in zip(v_data_km_s, sigma_over_m_data, sigma_pred_cm2_g):
        print(f"  v={v:>4}: observed={obs:.3e}, predicted={pred:.3e}, ratio={obs/pred:.2e}")
    
    results.append((alpha_D_test, m_A_prime_test, rmse))

# ============================================================
# Honest assessment
# ============================================================

print()
print("=" * 70)
print("PHASE 3 FINDING")
print("=" * 70)
print()

best = min(results, key=lambda x: x[2])
print(f"Best fit: α_D={best[0]}, m_A'={best[1]}, RMSE={best[2]:.3f}")
print()

# Check if our 4-peak model can match the data structure
# The Cloud-9 peak (v=28) is 5 orders of magnitude above other points
# The cluster point (v=500) is 3 orders of magnitude below SPARC (v=100)

print("Honest assessment:")
print("  - Our 4-peak phenomenology is highly tuned (specific v values)")
print("  - Simple Yukawa + BW doesn't naturally produce these peaks")
print("  - The 'best fit' is likely over-fitting with arbitrary parameters")
print()
print("Need deeper theory:")
print("  1. Atomic DM + ion DM (multi-component)")
print("  2. Bound-state formation cross-section enhancement")
print("  3. Sommerfeld enhancement from long-range force")
print()
print("NEXT: Phase 4 — Explicit multi-species calculation")
print("       with p_D-e_D-HD channels")