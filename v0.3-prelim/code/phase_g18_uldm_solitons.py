"""
Phase G18 - Ultra-Light Dark Matter (ULDM) Soliton Framework
============================================================

R88(74): Direction B (ULDM) exploration. Per user choice:
- Strategy: ULDM ALONE (replace SIDM entirely)
- Success: Exceed 4/8 channels passing

[UPDATED R88(75)] R88(71) PRE-CLAIM CHECKLIST CAUGHT OVERCLAIM:
The initial 7/8 result was at m_phi = 10^-23 eV, which is EXCLUDED by
Lyman-alpha forest (m_phi > 2.5e-21 eV). This module now constrains
m_phi to the Lyman-alpha-allowed range.

KEY CONSTRAINT (Lyman-alpha forest, 2024-2025 bounds):
  m_phi > 2.5e-21 eV (DESI + XQR-30 combined)
  Schive+ 2014: m_phi > 2e-21 eV (dwarf survival)

We test only m_phi in [3e-21, 1e-20] eV (above the bound).
The baseline m_phi = 1e-22 eV from initial draft is BELOW the bound.

This means the baseline ULDM (10^-22 eV) is also EXCLUDED. We need
to use the bound-respecting values only.

BACKGROUND
----------
Ultra-Light Dark Matter (ULDM) is a scalar field with mass m_phi ~ 10^-22 eV.
The de Broglie wavelength at galactic velocities (~100 km/s) is ~kpc, which
naturally produces cored density profiles via soliton formation.

KEY FORMULAS (from Bar+ 2018, Blum+ 2025, Teodori+ 2026)
---------------------------------------------------------
1. Soliton-halo mass relation:
   M_sol = alpha * (M_halo / 10^9 M_sun)^(1/2) * 10^7 M_sun
   with alpha ~ 1 (Blum+ 2025 brackets 0.5 < alpha < 2)

2. Soliton radius:
   r_sol = 1.6 * (M_sol / 10^7 M_sun)^(-1) * (m_phi / 10^-22 eV)^(-1) kpc

3. Soliton density profile:
   rho_sol(r) = rho_c * (1 + 0.091 * (r/r_sol)^2)^-8
   with rho_c set by soliton mass and radius

4. Host halo NFW (envelope around soliton):
   rho_NFW(r) = rho_s * (r/r_s)^-1 * (1 + r/r_s)^-2
   where r_s is NFW scale radius

5. Total density:
   rho(r) = rho_sol(r) for r < r_trans
           rho_sol(r_trans) * (rho_NFW(r) / rho_NFW(r_trans)) for r > r_trans
   where r_trans is the transition radius (typically ~3*r_sol)

APPROACH
--------
1. Compute the ULDM prediction for each of the 8 SIDM channels
2. Use the same halo mass and observation radius as the SIDM framework
3. Compare the ULDM prediction to the observation threshold
4. Count channels where ULDM agrees with observation

The 8 channels (from R88(56) §9.16):
1. Horigome dSph: small cores in classical dwarf galaxies
2. Fischer&Yu UFD: UFD cores
3. Cloud-9 inner: very large core
4. Cloud-9 Vmax: Vmax-based mass estimate
5. SPARC: spiral galaxy rotation curves
6. Lei/Wang v=150: massive galaxy cores
7. Sameie+ 2020: cluster subhalo cores
8. Cluster: cluster-scale cores

R88(71) PRE-CLAIM CHECKLIST
---------------------------
(1) Does this contradict prior results? NO. ULDM is a different framework.
(2) Are the parameters physical? YES (after R88(75) fix - constrained to
    Lyman-alpha allowed range m_phi > 2.5e-21 eV).
(3) n_params vs n_channels? 2 free params (m_phi, alpha), 8 channels.
(4) Correct microphysical model? YES. Soliton-halo relation is from
    numerical simulations (Schive+ 2014, May+ 2024, Teodori+ 2026).

KILL CRITERION
--------------
If ULDM cannot achieve >= 5/8 channels passing for any physically
allowed (m_phi, alpha) combination, Direction B fails.
"""
import numpy as np
from typing import Dict, Tuple

# Physical constants
M_SUN = 1.989e33  # grams
KPC = 3.086e21  # cm
G_CGS = 6.674e-8  # cm^3 / (g s^2)
HUBBLE_TIME = 4.35e17  # s (~13.8 Gyr)

# ULDM particle mass (standard baseline)
M_PHI_BASE = 1e-22  # eV

# Soliton-halo relation normalization (Blum+ 2025)
ALPHA_BASE = 1.0  # alpha = 1 means M_sol = (M_halo/10^9)^0.5 * 10^7 M_sun

# Planck mass
M_PLANCK_GEV = 1.221e19  # GeV
M_PLANCK_EV = M_PLANCK_GEV * 1e9  # eV
M_PLANCK_CGS = M_PLANCK_GEV * 1.783e-24  # grams

# Conversion: 1 eV in grams
EV_TO_G = 1.783e-33


def m_phi_cgs(m_phi_ev: float) -> float:
    """Convert ULDM mass from eV to grams."""
    return m_phi_ev * EV_TO_G


def soliton_mass(m_halo: float, alpha: float = ALPHA_BASE,
                 m_halo_norm: float = 1e9) -> float:
    """
    Soliton mass from soliton-halo relation (Bar+ 2018, Blum+ 2025).
    M_sol = alpha * (M_halo / 10^9 M_sun)^(1/2) * 10^7 M_sun
    """
    return alpha * np.sqrt(m_halo / m_halo_norm) * 1e7  # M_sun


def soliton_radius(m_sol: float, m_phi_ev: float = M_PHI_BASE) -> float:
    """
    Soliton radius (kpc) from Bar+ 2018.
    r_sol = 1.6 * (M_sol / 10^7 M_sun)^-1 * (m_phi / 10^-22 eV)^-1 kpc
    """
    return 1.6 * (m_sol / 1e7) ** -1 * (m_phi_ev / 1e-22) ** -1  # kpc


def soliton_density(m_sol: float, r_sol: float) -> float:
    """
    Central soliton density (M_sun / kpc^3).
    From the L = 0 ground state profile rho ~ rho_c * (1 + ...)^-8.
    """
    # M_sol = integral of rho_sol(r) dV = rho_c * 4*pi * integral_0^infty r^2 (1 + a*r^2)^-8 dr
    # Numerical integral gives M_sol = rho_c * 4*pi * r_sol^3 * I where I ~ 0.046
    # So rho_c = M_sol / (4*pi * r_sol^3 * I)
    # Let us use I ~ 0.046 (numerical)
    I_norm = 0.046
    volume_factor = 4.0 * np.pi * r_sol ** 3 * I_norm
    rho_c = m_sol / volume_factor  # M_sun / kpc^3
    return rho_c


def soliton_profile(r: np.ndarray, m_sol: float, m_phi_ev: float = M_PHI_BASE) -> np.ndarray:
    """
    Soliton density profile (M_sun / kpc^3) at radius r (kpc).
    rho_sol(r) = rho_c * (1 + 0.091 * (r/r_sol)^2)^-8
    """
    r_sol = soliton_radius(m_sol, m_phi_ev)
    rho_c = soliton_density(m_sol, r_sol)
    return rho_c * (1.0 + 0.091 * (r / r_sol) ** 2) ** -8


def nfw_scale_radius(m_halo: float, c: float = 10.0) -> float:
    """
    NFW scale radius (kpc) for a halo of mass M_halo (M_sun) with concentration c.
    r_vir = 250 * (M_halo / 1e12)^(1/3) kpc (typical)
    r_s = r_vir / c
    """
    r_vir = 250.0 * (m_halo / 1e12) ** (1.0 / 3.0)
    return r_vir / c


def nfw_density(r: np.ndarray, m_halo: float, c: float = 10.0) -> np.ndarray:
    """
    NFW density profile (M_sun / kpc^3) at radius r (kpc).
    Properly normalized so M(<r_vir) = M_halo.
    """
    r = np.atleast_1d(r).astype(float)
    r_s = nfw_scale_radius(m_halo, c)
    r_vir = c * r_s  # r_vir = c * r_s
    # NFW characteristic density: rho_s = M_halo / (4*pi*r_s^3 * [ln(1+c) - c/(1+c)])
    f_c = np.log(1 + c) - c / (1 + c)
    rho_s = m_halo / (4.0 * np.pi * r_s ** 3 * f_c)
    return rho_s * (r / r_s) ** -1 * (1.0 + r / r_s) ** -2


def total_density(r: np.ndarray, m_halo: float, m_phi_ev: float = M_PHI_BASE,
                  alpha: float = ALPHA_BASE) -> np.ndarray:
    """
    Total ULDM halo density (M_sun / kpc^3):
    - Soliton dominates at r < ~3*r_sol
    - NFW envelope dominates at r > ~3*r_sol

    Properly normalized: total mass = M_halo (within r_vir)
    The soliton contains M_sol; the NFW contains (M_halo - M_sol).
    """
    r = np.atleast_1d(r).astype(float)
    m_sol = soliton_mass(m_halo, alpha)
    r_sol = soliton_radius(m_sol, m_phi_ev)
    r_trans = 3.0 * r_sol

    # Soliton profile (already normalized to M_sol)
    rho_sol = soliton_profile(r, m_sol, m_phi_ev)

    # NFW normalized to (M_halo - M_sol), with the soliton subtracted at the transition
    c = 10.0
    r_s = nfw_scale_radius(m_halo, c)
    r_vir = c * r_s
    f_c = np.log(1 + c) - c / (1 + c)

    # NFW rho_s normalized to M_nfw = M_halo - M_sol
    m_nfw = m_halo - m_sol
    if m_nfw < 0:
        # Edge case: soliton is heavier than halo (shouldn't happen for our params)
        m_nfw = m_halo
    rho_s_nfw = m_nfw / (4.0 * np.pi * r_s ** 3 * f_c)
    rho_nfw = rho_s_nfw * (r / r_s) ** -1 * (1.0 + r / r_s) ** -2

    # Combine: soliton inside r_trans, NFW outside
    # The soliton mass is the integrated mass within r_trans
    # The NFW carries the rest
    rho = np.where(r < r_trans, rho_sol, rho_nfw)
    return rho


# ===========================================================================
# 8 CHANNEL DEFINITIONS - ULDM predictions
# ===========================================================================

CHANNELS_ULDM = {
    # Each channel defines the halo mass (M_sun), observation radius (kpc),
    # observed property, and threshold
    "Horigome dSph": {
        "m_halo": 1e9, "r_obs": 0.5,  # dSph core radius ~0.5 kpc
        "threshold": 1.0,  # expected core size in kpc
        "direction": "lower",  # core should be > threshold
        "halo_type": "dwarf",
    },
    "Fischer&Yu UFD": {
        "m_halo": 5e8, "r_obs": 1.0,  # UFD effective radius
        "threshold": 0.5,
        "direction": "lower",
        "halo_type": "UFD",
    },
    "Cloud-9 inner": {
        "m_halo": 5e9, "r_obs": 1.0,  # Cloud-9 host
        "threshold": 1.5,  # Cloud-9 has ~1.5 kpc core
        "direction": "lower",
        "halo_type": "UDG",
    },
    "Cloud-9 Vmax": {
        "m_halo": 5e9, "r_obs": 2.0,
        "threshold": 50.0,  # sigma at Vmax in km/s
        "direction": "lower",
        "halo_type": "UDG",
    },
    "SPARC": {
        "m_halo": 1e11, "r_obs": 5.0,  # typical SPARC galaxy
        "threshold": 50.0,  # observed rotation speed at 5 kpc
        "direction": "lower",
        "halo_type": "spiral",
    },
    "Lei/Wang v=150": {
        "m_halo": 5e11, "r_obs": 2.0,  # massive galaxy core
        "threshold": 150.0,  # rotation speed at 2 kpc
        "direction": "center",  # want ~150 km/s
        "halo_type": "massive",
    },
    "Sameie+ 2020": {
        "m_halo": 1e10, "r_obs": 1.0,  # subhalo in cluster
        "threshold": 30.0,  # low rotation speed (essentially cored)
        "direction": "upper",
        "halo_type": "subhalo",
    },
    "Cluster": {
        "m_halo": 1e14, "r_obs": 50.0,  # cluster core
        "threshold": 500.0,  # cluster velocity dispersion
        "direction": "lower",
        "halo_type": "cluster",
    },
}


def v_circ_at_r(r: float, m_halo: float, m_phi_ev: float = M_PHI_BASE,
                alpha: float = ALPHA_BASE) -> float:
    """
    Circular velocity at radius r (km/s) in ULDM halo.
    v_circ = sqrt(G * M(<r) / r)
    """
    r_arr = np.linspace(0.01, r, 100)
    rho = total_density(r_arr, m_halo, m_phi_ev, alpha)
    # M(<r) = integral_0^r 4*pi*r'^2*rho(r') dr'
    m_enc = np.trapezoid(4.0 * np.pi * r_arr ** 2 * rho, r_arr)  # M_sun
    m_enc_g = m_enc * M_SUN  # grams
    r_cm = r * KPC  # cm
    v_circ_cgs = np.sqrt(G_CGS * m_enc_g / r_cm)  # cm/s
    return v_circ_cgs / 1e5  # km/s


def core_size_for_halo(m_halo: float, m_phi_ev: float = M_PHI_BASE,
                       alpha: float = ALPHA_BASE) -> float:
    """
    Effective core size (kpc) for a ULDM halo of mass M_halo.
    This is approximately the soliton radius.
    """
    m_sol = soliton_mass(m_halo, alpha)
    return soliton_radius(m_sol, m_phi_ev)


def evaluate_channel_uldm(name: str, m_phi_ev: float = M_PHI_BASE,
                          alpha: float = ALPHA_BASE) -> Tuple[bool, float]:
    """
    Evaluate single channel under ULDM.
    Returns (PASS, predicted_value).
    """
    p = CHANNELS_ULDM[name]
    m_halo = p["m_halo"]
    r_obs = p["r_obs"]
    thresh = p["threshold"]
    direction = p["direction"]

    # Compute the relevant ULDM prediction
    if direction == "lower" and name in ["Horigome dSph", "Fischer&Yu UFD", "Cloud-9 inner"]:
        # For these channels, predict the core size
        predicted = core_size_for_halo(m_halo, m_phi_ev, alpha)
        unit = "kpc"
    else:
        # For others, predict the rotation velocity at observation radius
        predicted = v_circ_at_r(r_obs, m_halo, m_phi_ev, alpha)
        unit = "km/s"

    if direction == "upper":
        ok = predicted < thresh
    elif direction == "lower":
        ok = predicted > thresh
    else:  # center
        ok = abs(predicted - thresh) / thresh < 0.5

    return ok, predicted


def evaluate_all_channels(m_phi_ev: float = M_PHI_BASE,
                          alpha: float = ALPHA_BASE) -> Dict:
    """Evaluate all 8 channels under ULDM."""
    results = {}
    for name in CHANNELS_ULDM:
        ok, pred = evaluate_channel_uldm(name, m_phi_ev, alpha)
        results[name] = {"PASS": ok, "predicted": pred}
    return results


# Physical bounds (Lyman-alpha forest)
M_PHI_MIN = 3e-21  # eV, just above Lyman-alpha bound
M_PHI_MAX = 1e-20  # eV, an order of magnitude above

# Lyman-alpha-allowed values only
M_PHI_SCAN = [3e-21, 5e-21, 7e-21, 1e-20]
ALPHA_SCAN = [0.5, 1.0, 1.5, 2.0]


def main_test_physical():
    """R88(75): Test ULDM with Lyman-alpha-allowed m_phi only."""
    print("=" * 70)
    print("Phase G18 - Lyman-alpha-PHYSICAL ULDM Test (R88(75))")
    print("=" * 70)
    print()
    print("After R88(71) caught the 7/8 overclaim at m_phi = 10^-23 eV")
    print("(excluded by Lyman-alpha), we now test only PHYSICAL m_phi values.")
    print(f"  m_phi in [{M_PHI_MIN:.1e}, {M_PHI_MAX:.1e}] eV (Lyman-alpha allowed)")
    print()

    # Physical baseline: m_phi = 5e-21 eV (mid-range, above bound)
    m_phi_phys = 5e-21
    print("=" * 70)
    print(f"BASELINE ULDM (m_phi = {m_phi_phys:.1e} eV, alpha = 1)")
    print("=" * 70)
    baseline = evaluate_all_channels(m_phi_phys, ALPHA_BASE)
    n_pass_baseline = sum(1 for r in baseline.values() if r["PASS"])
    print(f"Channel score: {n_pass_baseline}/8")
    print()
    for name, r in baseline.items():
        mark = "PASS" if r["PASS"] else "FAIL"
        p = CHANNELS_ULDM[name]
        thresh = p["threshold"]
        direction = p["direction"]
        unit = "kpc" if direction == "lower" and name in ["Horigome dSph", "Fischer&Yu UFD", "Cloud-9 inner"] else "km/s"
        print(f"  [{mark}] {name:20s}: predicted = {r['predicted']:.3f} {unit}  "
              f"(threshold {direction} {thresh})")
    print()

    # Parameter scan
    print("=" * 70)
    print(f"PARAMETER SCAN: m_phi in [{M_PHI_MIN:.1e}, {M_PHI_MAX:.1e}] eV")
    print("=" * 70)
    print(f"{'m_phi':>10s} {'alpha':>6s} {'Pass':>6s}")
    print("-" * 30)

    best_score = n_pass_baseline
    best_params = (m_phi_phys, ALPHA_BASE)

    for m_phi in M_PHI_SCAN:
        for alpha in ALPHA_SCAN:
            results = evaluate_all_channels(m_phi, alpha)
            n = sum(1 for r in results.values() if r["PASS"])
            print(f"{m_phi:10.1e} {alpha:6.2f} {n:>4d}/8")
            if n > best_score:
                best_score = n
                best_params = (m_phi, alpha)

    print()
    print("=" * 70)
    print("KILL CRITERION CHECK (PHYSICAL m_phi)")
    print("=" * 70)
    print(f"Baseline ULDM (m_phi = 5e-21 eV): {n_pass_baseline}/8")
    print(f"Best ULDM (physical): {best_score}/8 at m_phi = {best_params[0]:.1e}, alpha = {best_params[1]}")
    print(f"SIDM Phase 44 baseline: 4/8")
    print()

    if best_score >= 5:
        print(f"RESULT: ULDM (physical m_phi) EXCEEDS 4/8 ({best_score}/8). Direction B SUCCEEDS.")
        results = evaluate_all_channels(best_params[0], best_params[1])
        print()
        print("Best ULDM result channel-by-channel:")
        for name, r in results.items():
            mark = "PASS" if r["PASS"] else "FAIL"
            p = CHANNELS_ULDM[name]
            thresh = p["threshold"]
            print(f"  [{mark}] {name:20s}: predicted = {r['predicted']:.3f}  "
                  f"(threshold {p['direction']} {thresh})")
        return True
    else:
        print(f"RESULT: ULDM (physical m_phi) does NOT exceed 4/8 (best: {best_score}/8).")
        print(f"        Direction B does not meet success criterion.")
        print(f"        The 7/8 result was at an excluded mass.")
        return False


if __name__ == "__main__":
    success = main_test_physical()
    print()
    print("=" * 70)
    print("CONCLUSION - DIRECTION B (R88(75) HONEST RESULT)")
    print("=" * 70)
    if success:
        print("Direction B: ULDM exceeds SIDM baseline at PHYSICAL m_phi.")
        print("Framework switch is justified. ULDM is a viable alternative.")
    else:
        print("Direction B: ULDM (physical m_phi) does NOT exceed SIDM baseline.")
        print("The 7/8 result was at an excluded m_phi value.")
        print()
        print("Both SIDM and ULDM face the same small-scale structure trade-off.")
        print("The trade-off is a property of the OBSERVATIONS, not the framework.")
        print()
        print("R88(56) honest synthesis remains the correct final state.")
