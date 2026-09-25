"""
T207 — Three-term decomposition of two-component SIDM halo.

Extends the Phase 44 / two-component framework to the full mixture rule:

    sigma_eff(v) = f_H^2 * sigma_HH(v) + 2 f_H f_L * sigma_HL(v) + f_L^2 * sigma_LL(v)

This addresses the structural failure of the two-term truncation (sigma_eff = f_H^2 sigma_HH),
which gives a maximum sigma_eff(100) = 0.069 cm^2/g < SPARC obs 0.193 — STRUCTURALLY
impossible regardless of f_H. With the three-term decomposition and a heavy-light (HL)
resonance at v ~ 100 km/s, sigma_eff(100) can reach the SPARC observation.

Module structure (new module per user direction; phase44_two_component.py untouched):
  - sigma_HH_at_v(v, params_HH): Phase 44 multi-resonance (HH channel)
  - sigma_HL_at_v(v, params_HL): HL channel with one extra Breit-Wigner peak
  - sigma_LL_at_v(v, params_LL): LL channel (pure Yukawa background)
  - sigma_eff_three_term(v, f_H, params): full mixture rule
  - f_H prescription loaders (borrowed / Yang+ 2025 / T202 N-body)

Per "Plan for further dev.docx" (2026-09-23): structural-failure-fix F1.

Arithmetic verification (Rule 28):
  - Sigma_HH(100) = 0.069 cm^2/g, SPARC obs = 0.193: structural deficit 0.124.
  - With f_H_int = 0.65, sigma_HL(100) = 0.33, sigma_LL(100) = 0.10:
    sigma_eff(100) = 0.4225*0.069 + 0.455*0.33 + 0.1225*0.10 = 0.193 (matches SPARC).
  - BW kinematics: mu_HH = 1.5, mu_HL = 0.75, mu_LL = 0.5 m_L (mass_ratio=3);
    v_res,HL / v_res,HH = sqrt(1.5/0.75) = sqrt(2) = 1.414.

Implementation note (v18.38 fix, found via Sanity 1 FAIL during self-test):
  The Phase 44 multi-resonance evaluates BW in ENERGY space (E = 0.5 m v^2),
  not velocity space. To avoid duplicating the conversion (and matching the
  reference sigma/m at all velocities), sigma_HH_at_v here calls the Phase 44
  joint-fit machinery directly via sigma_m_at_v. Initial naive approximation
  width_kms = gamma_frac * 2 * v_target gave sigma_HH(100) = 1.217 instead of
  the correct 0.069 — caught by Sanity 1 (f_H=1 reduction test, Rule 28).
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional

import numpy as np

# Make sure we can import from sibling modules
_CODE_DIR = Path(__file__).parent
if str(_CODE_DIR) not in sys.path:
    sys.path.insert(0, str(_CODE_DIR))


# =========================================================================
# Lorentzian Breit-Wigner resonance (same as phase44_two_component.py)
# =========================================================================
def lorentzian_bw(v: float, v_target: float, w: float) -> float:
    """Standard Lorentzian Breit-Wigner profile in VELOCITY space.

    sigma(v) = sigma_peak * (w/2)^2 / ((v - v_target)^2 + (w/2)^2)

    Returns the dimensionless BW factor in [0, 1].

    NOTE: Phase 44 uses BW in ENERGY space (E = 0.5 m v^2). For sigma_HH_at_v,
    we delegate to phase44_joint_fit.sigma_m_at_v which handles the conversion
    correctly. This function is used ONLY for sigma_HL_at_v and sigma_LL_at_v,
    where the HL/LL resonances are NOT in Phase 44 and we use a simpler
    velocity-space approximation (with width_HL as a free parameter).
    """
    half_w = w / 2.0
    return (half_w**2) / ((v - v_target) ** 2 + half_w**2)


# =========================================================================
# Channel 1: sigma_HH(v) — Phase 44 multi-resonance (HH channel)
# =========================================================================
def _phase44_params() -> dict:
    """Load Phase 44 best-fit parameters (cached)."""
    data_path = _CODE_DIR.parent / "data" / "results" / "phase44_joint_fit.json"
    with open(data_path) as f:
        d = json.load(f)
    p = d["best_params"]
    return {
        "m_chi": p[0],
        "sigma_0": p[1],
        "a_slope": p[2],
        "v_targets": list(p[3:7]),
        "sigma_peaks": list(p[7:11]),
        "gamma_fracs": list(p[11:15]),
    }


def _build_phase44_resonances(override_sigma_0: Optional[float] = None,
                              override_a_slope: Optional[float] = None,
                              override_sigma_peaks: Optional[list] = None) -> list:
    """Build Phase 44 resonance list with optional overrides.

    Returns list of dicts suitable for sigma_m_at_v (Phase 44's native format):
        {'name', 'E_R_eV', 'Gamma_eV', 'sigma_peak_cm2_per_g'}
    """
    from phase44_joint_fit import sigma_m_at_v as p44_sigma_m_at_v
    from t90_v70_multi_resonant_darkqcd import kinetic_energy_eV

    p = _phase44_params()
    m_chi = p["m_chi"]
    sigma_0 = override_sigma_0 if override_sigma_0 is not None else p["sigma_0"]
    a_slope = override_a_slope if override_a_slope is not None else p["a_slope"]
    sigma_peaks = override_sigma_peaks if override_sigma_peaks is not None else p["sigma_peaks"]

    resonances = []
    for i, v_t in enumerate(p["v_targets"]):
        E_R = kinetic_energy_eV(v_t, m_chi)
        Gamma = p["gamma_fracs"][i] * E_R
        resonances.append({
            "name": f"R{i}",
            "E_R_eV": E_R,
            "Gamma_eV": Gamma,
            "sigma_peak_cm2_per_g": sigma_peaks[i],
        })
    return resonances


def sigma_HH_at_v(
    v_kms: float,
    sigma_0: Optional[float] = None,
    a_slope: Optional[float] = None,
    sigma_peak_HH_1: Optional[float] = None,
) -> float:
    """Heavy-heavy channel sigma/m(v) at velocity v.

    Calls Phase 44's sigma_m_at_v directly (handles E-vs-v conversion correctly).

    Args:
        v_kms: relative velocity in km/s
        sigma_0: HH Yukawa background normalization (default: Phase 44 best-fit)
        a_slope: Yukawa slope exponent (default: Phase 44 best-fit, ~1.93)
        sigma_peak_HH_1: override for the Cloud-9 HH peak (default: Phase 44 best-fit, ~196)

    Returns:
        sigma_HH/m in cm^2/g
    """
    from phase44_joint_fit import sigma_m_at_v as p44_sigma_m_at_v

    p = _phase44_params()
    if sigma_0 is None:
        sigma_0 = p["sigma_0"]
    if a_slope is None:
        a_slope = p["a_slope"]
    sigma_peaks = list(p["sigma_peaks"])
    if sigma_peak_HH_1 is not None:
        sigma_peaks[0] = sigma_peak_HH_1

    resonances = _build_phase44_resonances(
        override_sigma_0=sigma_0, override_a_slope=a_slope,
        override_sigma_peaks=sigma_peaks,
    )
    p["m_chi"]
    m_chi = _phase44_params()["m_chi"]
    return p44_sigma_m_at_v(v_kms, m_chi, resonances, sigma_0, a_slope)


# =========================================================================
# Channel 2: sigma_HL(v) — heavy-light channel with optional HL peak
# =========================================================================
def sigma_HL_at_v(
    v_kms: float,
    sigma_0_HL: float,
    a_slope: float,
    sigma_peak_HL: float = 0.0,
    v_HL: float = 100.0,
    width_HL: float = 50.0,
    v_ref: float = 100.0,
) -> float:
    """Heavy-light channel sigma/m(v) at velocity v.

    The HL channel has a Yukawa background PLUS an optional single Lorentzian peak
    (the HL resonance). In the multi-mediator scenario, the second mediator places
    its HL peak at v ~ 100 km/s so SPARC sees enhanced HL scattering.

    Args:
        v_kms: relative velocity in km/s
        sigma_0_HL: HL background normalization (cm^2/g) at v_ref
        a_slope: Yukawa slope exponent (shared with HH for simplicity)
        sigma_peak_HL: peak amplitude of HL resonance (cm^2/g), 0 = pure background
        v_HL: HL resonance position (km/s)
        width_HL: HL resonance width (km/s)
        v_ref: reference velocity for Yukawa (km/s)

    Returns:
        sigma_HL/m in cm^2/g
    """
    bg = sigma_0_HL * (v_ref / v_kms) ** a_slope
    peak = sigma_peak_HL * lorentzian_bw(v_kms, v_HL, width_HL)
    return bg + peak


# =========================================================================
# Channel 3: sigma_LL(v) — light-light channel (pure Yukawa background)
# =========================================================================
def sigma_LL_at_v(
    v_kms: float,
    sigma_0_LL: float,
    a_slope: float,
    v_ref: float = 100.0,
) -> float:
    """Light-light channel sigma/m(v) at velocity v (pure Yukawa background).

    No resonance structure on the LL channel — assumes the LL mediator either
    doesn't exist or is much heavier (off-channel).

    Args:
        v_kms: relative velocity in km/s
        sigma_0_LL: LL background normalization (cm^2/g) at v_ref
        a_slope: Yukawa slope exponent
        v_ref: reference velocity for Yukawa (km/s)

    Returns:
        sigma_LL/m in cm^2/g
    """
    return sigma_0_LL * (v_ref / v_kms) ** a_slope


# =========================================================================
# Three-term mixture rule
# =========================================================================
def sigma_eff_three_term(
    v_kms: float,
    f_H: float,
    sigma_0: float = None,
    a_slope: float = None,
    sigma_peak_HH_1: float = None,
    sigma_0_HL: float = None,
    sigma_peak_HL: float = None,
    v_HL: float = None,
    width_HL: float = None,
    sigma_0_LL: float = None,
) -> float:
    """Full three-term sigma_eff/v at velocity v and local heavy fraction f_H.

    sigma_eff(v) = f_H^2 * sigma_HH(v) + 2 f_H f_L * sigma_HL(v) + f_L^2 * sigma_LL(v)

    All parameters default to Phase 44 best-fit values when None.
    """
    if not (0.0 <= f_H <= 1.0):
        raise ValueError(f"f_H must be in [0, 1], got {f_H}")
    f_L = 1.0 - f_H

    s_HH = sigma_HH_at_v(v_kms, sigma_0=sigma_0, a_slope=a_slope,
                          sigma_peak_HH_1=sigma_peak_HH_1)
    s_HL = sigma_HL_at_v(
        v_kms,
        sigma_0_HL if sigma_0_HL is not None else 0.02,
        a_slope if a_slope is not None else 1.93,
        sigma_peak_HL if sigma_peak_HL is not None else 0.33,
        v_HL if v_HL is not None else 100.0,
        width_HL if width_HL is not None else 50.0,
    )
    s_LL = sigma_LL_at_v(
        v_kms,
        sigma_0_LL if sigma_0_LL is not None else 0.10,
        a_slope if a_slope is not None else 1.93,
    )

    return f_H**2 * s_HH + 2 * f_H * f_L * s_HL + f_L**2 * s_LL


# =========================================================================
# Param container for the 9 free parameters
# =========================================================================
@dataclass
class T207Params:
    """Container for the 9 free parameters of T207.

    Fixed (not free): HH resonance positions and widths from Phase 44.
    Free: sigma_0 (HH bg), 4 HH peak amplitudes, sigma_0_HL, sigma_peak_HL,
          v_HL, sigma_0_LL, alpha, f_H_cf, f_H_cc.

    Note: per the design memo, HH peaks are also partly fixed by the clockwork
    geometry (v_targets[i] for i=2,3,4). We keep them fixed at Phase 44 values
    and only vary sigma_peak_HH_1 (the Cloud-9 peak). The other 3 HH peaks are
    fixed at Phase 44 best-fit values to keep the fit manageable.
    """
    sigma_0: float              # 1. HH background normalization
    sigma_peak_HH_1: float      # 2. HH peak at 28 km/s (Cloud-9)
    sigma_0_HL: float           # 3. HL background normalization
    sigma_peak_HL: float        # 4. HL peak at v_HL
    v_HL: float                 # 5. HL resonance position
    sigma_0_LL: float           # 6. LL background normalization
    a_slope: float              # 7. Yukawa slope (shared)
    f_H_cf: float               # 8. f_H in core-forming halos
    f_H_cc: float               # 9. f_H in core-collapsed halos

    def to_array(self) -> np.ndarray:
        return np.array([
            self.sigma_0, self.sigma_peak_HH_1, self.sigma_0_HL,
            self.sigma_peak_HL, self.v_HL, self.sigma_0_LL, self.a_slope,
            self.f_H_cf, self.f_H_cc,
        ])

    @classmethod
    def from_array(cls, arr: np.ndarray) -> "T207Params":
        if len(arr) != 9:
            raise ValueError(f"Expected 9 params, got {len(arr)}")
        return cls(
            sigma_0=float(arr[0]),
            sigma_peak_HH_1=float(arr[1]),
            sigma_0_HL=float(arr[2]),
            sigma_peak_HL=float(arr[3]),
            v_HL=float(arr[4]),
            sigma_0_LL=float(arr[5]),
            a_slope=float(arr[6]),
            f_H_cf=float(arr[7]),
            f_H_cc=float(arr[8]),
        )


# =========================================================================
# Phase 44 fixed HH resonance list (now loaded lazily via _build_phase44_resonances)
# =========================================================================
# Replaced: load_phase44_HH_resonances() is deprecated; sigma_HH_at_v now
# delegates directly to Phase 44's sigma_m_at_v. See _build_phase44_resonances
# above for the canonical resonance construction.


# =========================================================================
# f_H prescription loaders
# =========================================================================
def f_H_prescription(name: str) -> Dict[str, float]:
    """Return (f_H_cf, f_H_cc) for the named prescription.

    Three prescriptions (per Plan for further dev.docx §10):
      - "borrowed": f_H_cf = 0.85, f_H_cc = 0.30 (hand-picked, RETRACTED v18.29)
      - "yang": f_H_cf = 0.85, f_H_cc = 0.45 (Yang+ 2025 Fig. 2 derived)
      - "t202": f_H_cf = 0.92, f_H_cc = 0.61 (T202 N-body, partial segregation)
    """
    prescriptions = {
        "borrowed": {"f_H_cf": 0.85, "f_H_cc": 0.30, "f_H_int": 0.575},
        "yang":     {"f_H_cf": 0.85, "f_H_cc": 0.45, "f_H_int": 0.650},
        "t202":     {"f_H_cf": 0.92, "f_H_cc": 0.61, "f_H_int": 0.765},
    }
    if name not in prescriptions:
        raise ValueError(f"Unknown prescription: {name}")
    return prescriptions[name]


# =========================================================================
# Self-test (Rule 28: known-system sanity checks)
# =========================================================================
if __name__ == "__main__":
    print("=" * 80)
    print("T207 — Three-term decomposition: known-system sanity checks")
    print("=" * 80)

    # Sanity 1: f_H = 1 reduces to sigma_HH
    print("\n=== Sanity 1: f_H = 1 => sigma_eff = sigma_HH ===")
    s_HH_100 = sigma_HH_at_v(100.0)
    s_eff_f1 = sigma_eff_three_term(
        100.0, f_H=1.0,
        sigma_0=0.052, a_slope=1.93, sigma_peak_HH_1=196.3,
        sigma_0_HL=0.02, sigma_peak_HL=0.33, v_HL=100.0, width_HL=50.0,
        sigma_0_LL=0.10,
    )
    print(f"  sigma_HH(100)        = {s_HH_100:.4f} cm^2/g")
    print(f"  sigma_eff(100, f_H=1)= {s_eff_f1:.4f} cm^2/g  (should equal sigma_HH)")
    diff = abs(s_HH_100 - s_eff_f1)
    print(f"  |difference| = {diff:.6f}  {'PASS' if diff < 1e-10 else 'FAIL'}")

    # Sanity 2: doc's worked example reproduces SPARC obs
    print("\n=== Sanity 2: SPARC observation reproduced ===")
    s_eff_sparc = sigma_eff_three_term(
        100.0, f_H=0.65,
        sigma_0=0.052, a_slope=1.93, sigma_peak_HH_1=196.3,
        sigma_0_HL=0.02, sigma_peak_HL=0.33, v_HL=100.0, width_HL=50.0,
        sigma_0_LL=0.10,
    )
    print(f"  sigma_eff(100, f_H=0.65) = {s_eff_sparc:.4f} cm^2/g  (target: 0.193)")
    diff = abs(s_eff_sparc - 0.193)
    print(f"  |difference| = {diff:.4f}  {'PASS' if diff < 0.01 else 'FAIL'}")

    # Sanity 3: dSph passes at f_H_cc = 0.1 with three-term decomposition
    # Note: doc assumed a_slope=1.0; with Phase 44 best-fit (1.93) the values
    # differ. The fit will find values that pass.
    print("\n=== Sanity 3: dSph at v=15 — doc's worked example (a_slope=1.0) ===")
    s_eff_dsph = sigma_eff_three_term(
        15.0, f_H=0.1,
        sigma_0=0.052, a_slope=1.0, sigma_peak_HH_1=196.3,
        sigma_0_HL=0.02, sigma_peak_HL=0.33, v_HL=100.0, width_HL=50.0,
        sigma_0_LL=0.03,
    )
    print(f"  sigma_eff(15, f_H=0.1, a_slope=1.0) = {s_eff_dsph:.4f} cm^2/g  (ceiling: 0.8)")
    print(f"  With doc's a_slope=1.0: {'PASS' if s_eff_dsph < 0.8 else 'FAIL'}")
    print("\n=== Sanity 3b: dSph at v=15 — Phase 44 best-fit (a_slope=1.93) ===")
    s_eff_dsph_p44 = sigma_eff_three_term(
        15.0, f_H=0.1,
        sigma_0=0.052, a_slope=1.93, sigma_peak_HH_1=196.3,
        sigma_0_HL=0.02, sigma_peak_HL=0.33, v_HL=100.0, width_HL=50.0,
        sigma_0_LL=0.03,
    )
    print(f"  sigma_eff(15, f_H=0.1, a_slope=1.93) = {s_eff_dsph_p44:.4f} cm^2/g  (ceiling: 0.8)")
    print(f"  With Phase 44 a_slope=1.93: {'PASS (FAIL — fit will find different HL/LL params)' if s_eff_dsph_p44 < 0.8 else 'FAIL — fit must adjust sigma_0_HL/sigma_0_LL downward'}")

    # Sanity 4: Cloud-9 passes floor with HH peak
    # Note: doc's override of 128 cm^2/g at peak gives sigma_eff ~47 with f_H=0.85,
    # which is below floor 50. Need override ~175 to pass. Fit will find this.
    print("\n=== Sanity 4: Cloud-9 at v=28 — doc's override (peak=128) ===")
    s_eff_c9 = sigma_eff_three_term(
        28.0, f_H=0.85,
        sigma_0=0.052, a_slope=1.0, sigma_peak_HH_1=128.0,
        sigma_0_HL=0.02, sigma_peak_HL=0.33, v_HL=100.0, width_HL=50.0,
        sigma_0_LL=0.10,
    )
    print(f"  sigma_eff(28, f_H=0.85, HH_peak=128, a_slope=1.0) = {s_eff_c9:.4f} cm^2/g  (floor: 50)")
    print(f"  {'PASS' if s_eff_c9 > 50.0 else 'FAIL — fit will find larger HH_peak'}")
    print("\n=== Sanity 4b: Cloud-9 at v=28 — Phase 44 default (peak=196.3) ===")
    s_eff_c9_default = sigma_eff_three_term(
        28.0, f_H=0.85,
        sigma_0=0.052, a_slope=1.0, sigma_peak_HH_1=196.3,
        sigma_0_HL=0.02, sigma_peak_HL=0.33, v_HL=100.0, width_HL=50.0,
        sigma_0_LL=0.10,
    )
    print(f"  sigma_eff(28, f_H=0.85, HH_peak=196.3) = {s_eff_c9_default:.4f} cm^2/g  (floor: 50)")
    print(f"  {'PASS' if s_eff_c9_default > 50.0 else 'FAIL'}")

    # Sanity 5: positivity and limits
    print("\n=== Sanity 5: sigma_eff >= 0 for all f_H in [0, 1] ===")
    all_pos = True
    for f in np.linspace(0, 1, 11):
        s = sigma_eff_three_term(
            100.0, f,
            sigma_0=0.052, a_slope=1.93, sigma_peak_HH_1=196.3,
            sigma_0_HL=0.02, sigma_peak_HL=0.33, v_HL=100.0, width_HL=50.0,
            sigma_0_LL=0.10,
        )
        if s < 0:
            all_pos = False
            print(f"  f={f:.1f}: sigma_eff={s:.4f}  NEGATIVE!")
    print(f"  All non-negative: {'PASS' if all_pos else 'FAIL'}")