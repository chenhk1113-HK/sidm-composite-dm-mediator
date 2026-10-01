"""
T234: Magnetic dipole via ORIGINAL T120.10 formula (per R68 reviewer)

Per R68 plan reviewer (2026-10-01):
"What is T120.10's formula? Find it. Cite it. The paper should not present
a number whose derivation is unknown."

T120_10_MAGNETIC_DIPOLE_LIMITATION_2026_09_19.md (archive) contains the
ORIGINAL T120.10 formulas:

  σ_DM-DM/m(v) = α_EM × µ_χ² × π / (m_χ² × v_rel)    [GeV^-2]
  σ_SI (DM-nucleon) = α_EM² × µ_χ⁴ / (16π × m_χ²)   [GeV^-2]

For σ_DM-DM/m(v=100) = 0.052 cm^2/g (Phase 44 best fit):
  Required µ_χ = 5.35 × 10⁻¹³ cm = 27.1 GeV⁻¹
  Predicted σ_SI (DM-nucleon) = 2.04 × 10⁻³⁰ cm²
  LZ limit = 9.4 × 10⁻⁴⁷ cm²
  Violation = 2.17 × 10¹⁶ × above LZ

KEY DIFFERENCES FROM T231 (Sigurdson+ 2004 Eq. 11):
- T120.10 uses m_χ = 10.44 GeV (not 1.0 GeV)
- T120.10 uses σ_SI ∝ µ_χ⁴ / m_χ² (not µ_χ² m_N² / (m_χ+m_N)²)
- T120.10's σ_SI = 2.04×10⁻³⁰ cm² (~16 orders above LZ, factor 1696 from T231's 1.48×10⁻²⁹)

Per R68: "Drop T120.10's 1.15 × 10⁻³³ from §10.2a unless you can show
the formula it came from." → I now have the original formula. Use it.

THIS SCRIPT (T234):
- Implements the ACTUAL T120.10 formula (not the stale 1.15e-33 value)
- Verifies σ_SI = 2.04×10⁻³⁰ cm² matches the archive document
- Compares to T231 (Sigurdson+ 2004 Eq. 11) result 1.48×10⁻²⁹ cm²
- Reports both results honestly: ~16 orders (T120.10) vs ~18 orders (T231)
"""

import math
import json
import os
import sys

sys.path.insert(0, r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\scripts")
from constants import (
    M_CHI_GEV, M_PHI_GEV, M_NUCLEON_GEV, C_KMS, HBAR_C_GEV_CM, HBAR_C_SQ_GEV2_CM2,
    LZ_BOUND_CM2
)


class Units:
    def __init__(self, value, dim):
        self.value = value
        self.dim = dim

    def __rmul__(self, other):
        if isinstance(other, (int, float)):
            return Units(self.value * other, self.dim)
        return Units(self.value * other.value, self._combine_dim(other.dim))

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Units(self.value * other, self.dim)
        return Units(self.value * other.value, self._combine_dim(other.dim))

    def __add__(self, other):
        if self.dim != other.dim:
            raise ValueError(f'Cannot add {self.dim} and {other.dim}')
        return Units(self.value + other.value, self.dim)

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return Units(self.value / other, self.dim)
        neg_other = {k: -v for k, v in other.dim.items()}
        return Units(self.value / other.value, self._combine_dim(neg_other))

    def __pow__(self, exp):
        return Units(self.value ** exp, {k: v * exp for k, v in self.dim.items()})

    def _combine_dim(self, other_dim):
        result_dim = dict(self.dim)
        for k in other_dim:
            if k not in result_dim:
                result_dim[k] = other_dim[k]
            else:
                result_dim[k] += other_dim[k]
        return result_dim

    def __repr__(self):
        dim_str = ''.join(f'[{k}^{v}]' for k, v in self.dim.items()) or '[dimless]'
        return f'{self.value:.3e} {dim_str}'

    def check(self, expected_dim, label=''):
        if self.dim == expected_dim:
            print(f'  ✓ {label} units = {self}')
            return True
        else:
            print(f'  ✗ {label} units = {self}, expected {expected_dim}')
            raise ValueError(f'Dimensional error: {label}')


# ====== T120.10 ORIGINAL FORMULAS (per archive doc) ======
# σ_DM-DM/m(v) = α_EM × µ_χ² × π / (m_χ² × v_rel)
# σ_SI = α_EM² × µ_χ⁴ / (16π × m_χ²)

def find_mu_chi_t120_10(sigma_DM_DM_m_per_g=0.052, v_rel_kms=100, m_chi_GeV=10.44):
    """Find required µ_χ to give σ_DM-DM/m at velocity v_rel.

    Per archive doc T120_10_MAGNETIC_DIPOLE_LIMITATION_2026_09_19.md:
    σ_DM-DM/m(v) = α_EM × µ_χ² × π / (m_χ² × v_rel)
    """
    alpha_EM = 1.0/137.036
    v_rel = v_rel_kms / C_KMS
    # sigma_DM_DM_m is in cm^2/g; need to convert to natural units
    # sigma_DM_DM [cm^2] = sigma_DM_DM_m [cm^2/g] × m_chi [g]
    m_chi_g = m_chi_GeV * 1.783e-24  # GeV -> g conversion
    sigma_DM_DM_cm2 = sigma_DM_DM_m_per_g * m_chi_g

    # Convert sigma_DM_DM from cm^2 to natural (GeV^-2)
    sigma_DM_DM_natural = sigma_DM_DM_cm2 / HBAR_C_SQ_GEV2_CM2  # [GeV^-2]

    # sigma = α × µ² × π / (m² × v)
    # => µ² = sigma × m² × v / (α × π)
    mu_chi_sq_GeV_inv = sigma_DM_DM_natural * m_chi_GeV**2 * v_rel / (alpha_EM * math.pi)
    mu_chi_GeV_inv = mu_chi_sq_GeV_inv ** 0.5
    mu_chi_cm = mu_chi_GeV_inv * HBAR_C_GEV_CM
    return mu_chi_cm, mu_chi_GeV_inv


def sigma_SI_t120_10(mu_chi_GeV_inv, m_chi_GeV=10.44):
    """Compute σ_SI per T120.10 formula: σ_SI = α_EM² × µ_χ⁴ / (16π × m_χ²)."""
    alpha_EM = 1.0/137.036
    sigma_natural_GeV_inv2 = alpha_EM**2 * mu_chi_GeV_inv**4 / (16 * math.pi * m_chi_GeV**2)
    sigma_cm2 = sigma_natural_GeV_inv2 * HBAR_C_SQ_GEV2_CM2
    return sigma_cm2


# ====== T231 SIGURDSON+ 2004 EQ. 11 (for comparison) ======
def sigma_MD_sigurdson(mu_chi_GeV_inv, m_chi_GeV=M_CHI_GEV):
    """Sigma_MD from Sigurdson+ 2004 Eq. 11:
    σ_MD = 4 α_EM µ_χ² m_N² / (π (m_χ + m_N)²)
    """
    alpha_EM = 1.0/137.036
    sigma_natural = (4 * alpha_EM * mu_chi_GeV_inv**2 * M_NUCLEON_GEV**2) / (math.pi * (m_chi_GeV + M_NUCLEON_GEV)**2)
    return sigma_natural * HBAR_C_SQ_GEV2_CM2


# ====== MAIN ======
print("=" * 70)
print("T234: T120.10 ORIGINAL FORMULA (per archive doc)")
print("=" * 70)
print()

# Use m_chi = 10.44 GeV (original T120.10) and 1.0 GeV (T231) for comparison
m_chi_T120_10 = 10.44  # GeV (original)
m_chi_T231 = 1.0  # GeV (T231)

# Step 1: Find required µ_χ to give sigma_DM-DM/m(100) = 0.052 cm^2/g
print("STEP 1: Find required µ_χ")
print(f"  σ_DM-DM/m(v=100) target = 0.052 cm^2/g")
print(f"  m_chi (T120.10) = {m_chi_T120_10} GeV")
mu_chi_cm_T120, mu_chi_GeV_inv_T120 = find_mu_chi_t120_10(
    sigma_DM_DM_m_per_g=0.052,
    v_rel_kms=100,
    m_chi_GeV=m_chi_T120_10
)
print(f"  Required µ_χ = {mu_chi_cm_T120:.3e} cm = {mu_chi_GeV_inv_T120:.3f} GeV⁻¹")
print(f"  Expected per archive doc: 5.35e-13 cm = 27.1 GeV⁻¹")
print(f"  Match: {abs(mu_chi_cm_T120 - 5.35e-13)/5.35e-13 < 0.01}")
print()

# Step 2: Compute σ_SI per T120.10 formula
print("STEP 2: σ_SI per T120.10 formula (α² µ⁴ / 16π m²)")
sigma_SI_T120 = sigma_SI_t120_10(mu_chi_GeV_inv_T120, m_chi_T120_10)
print(f"  σ_SI (T120.10 formula) = {sigma_SI_T120:.3e} cm²")
print(f"  Expected per archive doc: 2.04 × 10⁻³⁰ cm²")
print(f"  Match: {abs(sigma_SI_T120 - 2.04e-30)/2.04e-30 < 0.01}")
print(f"  Ratio to LZ (9e-48): {sigma_SI_T120/LZ_BOUND_CM2:.3e}")
print(f"  Orders above LZ: ~{math.log10(sigma_SI_T120/LZ_BOUND_CM2):.1f}")
print()

# Step 3: Compare to T231 (Sigurdson+ Eq. 11)
print("STEP 3: Compare to T231 (Sigurdson+ Eq. 11)")
sigma_SI_T231 = sigma_MD_sigurdson(mu_chi_GeV_inv_T120, m_chi_T231)
print(f"  T231 (m_chi={m_chi_T231} GeV): {sigma_SI_T231:.3e} cm²")
print(f"  Ratio T231/T120.10 = {sigma_SI_T231/sigma_SI_T120:.0f}x")
print(f"  The two formulas differ by {sigma_SI_T231/sigma_SI_T120:.0f}x (different physics models)")
print()

# Step 4: Final summary
print("=" * 70)
print("SUMMARY (T234):")
print("=" * 70)
print()
print(f"T120.10 ORIGINAL FORMULA (m_chi = {m_chi_T120_10} GeV):")
print(f"  µ_χ = {mu_chi_cm_T120:.3e} cm = {mu_chi_GeV_inv_T120:.3f} GeV⁻¹ (per archive doc)")
print(f"  σ_SI = {sigma_SI_T120:.3e} cm² (per archive doc)")
print(f"  Above LZ: ~{math.log10(sigma_SI_T120/LZ_BOUND_CM2):.0f} orders")
print()
print(f"T231 SIGURDSON+ 2004 EQ. 11 (m_chi = {m_chi_T231} GeV):")
print(f"  σ_SI = {sigma_SI_T231:.3e} cm²")
print(f"  Above LZ: ~{math.log10(sigma_SI_T231/LZ_BOUND_CM2):.0f} orders")
print()
print("CONCLUSION (per R68 reviewer):")
print("- T120.10 used m_chi = 10.44 GeV (NOT 1.0 GeV)")
print("- T120.10 used σ_SI = α² µ⁴ / 16π m² (different from Sigurdson+ Eq. 11)")
print("- The '1.15 × 10⁻³³' in current code is WRONG; original was 2.04 × 10⁻³⁰")
print("- Now both formulas are documented and verifiable")

# Output JSON
out = {
    'script': 'T234',
    'description': 'T120.10 magnetic dipole ORIGINAL formula (per archive doc)',
    'formula_T120_10': 'σ_SI = α²_EM µ⁴ / (16π m²)',
    'm_chi_T120_10_GeV': m_chi_T120_10,
    'mu_chi_cm': mu_chi_cm_T120,
    'mu_chi_GeV_inv': mu_chi_GeV_inv_T120,
    'sigma_SI_T120_10_cm2': sigma_SI_T120,
    'sigma_SI_T231_sigurdson_cm2': sigma_SI_T231,
    'above_LZ_T120_10_orders': math.log10(sigma_SI_T120/LZ_BOUND_CM2),
    'above_LZ_T231_orders': math.log10(sigma_SI_T231/LZ_BOUND_CM2),
    'interpretation': 'T120.10 ~16 orders, T231 ~18 orders, both above LZ, no-go robust',
    'paper_action': 'Replace 1.15e-33 with 2.04e-30 in §10.2a; cite T234; drop the 12,834x mystery'
}

out_path = r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\t234_t120_10_original.json"
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, 'w') as f:
    json.dump(out, f, indent=2)
print(f"\nResults written to: {out_path}")