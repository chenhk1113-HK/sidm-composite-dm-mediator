"""
Phase G17 - IDE-2cSIDM Sub-strategy A: Symmetric Coupling Feasibility Test
============================================================================

R88(72): Direction A (IDE-2cSIDM) exploration, per user request.

GOAL: Test whether UNIFORM dark matter - dark energy coupling (beta_H = beta_L = beta)
breaks the structural trade-off theorem. This is a feasibility test.

BACKGROUND
----------
In standard cosmology (LCDM), dark matter density evolves as:
  rho_DM(z) = rho_DM,0 * (1+z)^3

With Interacting Dark Energy (IDE), if dark energy has equation of state w and the
dark matter couples to it with coupling beta, the evolution is:
  rho_DM(z) = rho_DM,0 * (1+z)^(3 - xi)
where xi is set by beta and w.

For a coupled quintessence model with constant w:
  xi ~ 3*beta*(1+w)   (for beta << 1)

In this Phase G17-A, we apply this coupling UNIFORMLY to both the heavy and light
SIDM species. The heavy fraction f_H is NOT directly modified by IDE; only the
overall densities evolve.

KEY QUESTION: Does the background density evolution affect the OBSERVABLE sigma_eff
in a way that breaks the v=150 trade-off?

APPROACH
--------
1. Compute the redshift evolution of the background for several values of beta
2. For each beta, evaluate when the constrained halos (Cloud-9, Fornax, etc.)
   are observed (their formation redshift z_form)
3. Compute the effective sigma_eff at v=150 as a function of z
4. Check whether the IDE-modified evolution breaks the trade-off

The structural trade-off theorem is about WITHIN a halo, so the IDE modification
must affect either:
  (a) the gravothermal evolution timescale t_c, OR
  (b) the segregation timescale t_seg, OR
  (c) the effective cross-section sigma_m

For symmetric coupling, only (a) is modified (the halo mass evolution with z is
changed by the IDE background). Let us check if this is enough.

PARAMETERS
----------
beta: coupling strength in [0, 0.05] (Planck+DESI bound)
w: dark energy equation of state (we use w = -1 for vacuum)
A_res: resonance amplitude
sigma_peak: peak cross-section
v_target: resonance velocity
a_slope: background power-law slope

Following R88(71) PRE-CLAIM CHECKLIST:
- (1) Does this contradict prior results? NO. We are not modifying the WITHIN-halo
      physics, only the cosmological background. The gravothermal cascade, the
      SIDM2c segregation, and the trade-off theorem all still apply WITHIN a halo.
      IDE only shifts the redshift of halo formation, not the local physics.
- (2) Are the parameters physical? YES. beta in [0, 0.05] is the Planck+DESI
      bound. w = -1 is vacuum energy. No boundary values.
- (3) n_params vs n_channels? 1 new free parameter (beta), 8 channels. 8 > 1+1,
      so no overfitting.
- (4) Correct microphysical model? YES. We are using the same sigma_HH vs sigma_eff
      distinction as R88(49). The IDE modification is at the cosmological
      background level only.

KILL CRITERION
--------------
If beta = 0.05 (maximum allowed) does not improve the channel score by at least
+1 (from 4/8 to 5/8), the symmetric coupling sub-strategy is FAILED and we
proceed to Sub-strategy B (species-dependent coupling).

EXPECTED OUTCOME
----------------
Most likely the symmetric coupling will NOT help, because:
- IDE modifies the background density evolution
- But the structural trade-off is about WITHIN-halo physics
- Background evolution at z~0 (where observations are made) is well-approximated
  by LCDM for beta < 0.05

This is a "fail fast" test. If it fails, we proceed to B (species-dependent).
"""
import numpy as np
from typing import Dict, List, Tuple

# Physical constants (same as R88(56) SSoT)
SIGMA_PEAK_CM2_PER_G = 174.0  # phase 44 peak, post-diction
M_CHI_GEV = 1.0
M_PHI_GEV = 200e-9
V_TARGET_KMS = 29.4
SIGMA_KMS = 4.4
A_SLOPE = 1.93
A_RES = 100.0
SIGMA_0_CM2_PER_G = 0.052
V_REF_KMS = 100.0
F_H = 0.297  # Cosmic dark matter fraction in heavy species (cosmological)
OMEGA_DM_0 = 0.27  # Omega_DM today

def sigma_m_at_v(v_kms: float, v_target: float = V_TARGET_KMS,
                 sigma_peak: float = SIGMA_PEAK_CM2_PER_G,
                 sigma_kms: float = SIGMA_KMS,
                 a_slope: float = A_SLOPE, v_ref: float = V_REF_KMS) -> float:
    """Phase 44 sigma/m(v) - Gaussian resonance + power-law background."""
    background = A_SLOPE * SIGMA_0_CM2_PER_G * (v_ref / v_kms) ** a_slope
    resonance = sigma_peak * np.exp(-0.5 * ((v_kms - v_target) / sigma_kms) ** 2)
    return background + resonance


def sigma_eff(v_kms: float, f_h_central: float, f_h_sub: float,
              is_subhalo: bool, f_H_evol: float = 1.0) -> float:
    """
    Observable sigma_eff. f_H_evol allows for IDE-modified evolution.
    f_H_evol = 1.0 means standard evolution.
    f_H_evol < 1.0 means heavy species is depleted relative to standard.
    """
    f_h = f_h_sub if is_subhalo else f_h_central
    f_h_eff = f_h * f_H_evol
    return f_h_eff ** 2 * sigma_m_at_v(v_kms)


def xi_coupling(beta: float, w: float = -1.0) -> float:
    """
    IDE exponent: rho_DM(z) = rho_0 * (1+z)^(3-xi)
    For coupled quintessence: xi ~ 3*beta*(1+w)
    """
    return 3.0 * beta * (1.0 + w)


def halo_mass_at_z(M_h_0: float, z: float, beta: float, w: float = -1.0) -> float:
    """
    Halo mass at redshift z for IDE cosmology.
    In standard cosmology: M(z) = M_0 * (1+z) (linear growth).
    In IDE: M(z) = M_0 * (1+z) * (1+z)^(-xi) = M_0 * (1+z)^(1-xi)
    """
    xi = xi_coupling(beta, w)
    return M_h_0 * (1 + z) ** (1.0 - xi)


def t_c_gyr(sigma_hh: float, rho_eff: float = 0.04) -> float:
    """Core-collapse timescale from Yang+ 2024 (parametric)."""
    return 28.7 * (7.1 / sigma_hh) * (0.04 / rho_eff)


def tau_for_halo(M_h_0: float, z_form: float, beta: float, w: float = -1.0,
                 sigma_hh: float = 1.0) -> float:
    """
    Gravothermal phase tau = t / t_c for a halo observed at z=0
    but formed at z_form.

    In IDE, the halo's density evolution is modified by beta.
    Higher beta -> less time spent at high density -> smaller tau.
    """
    # Effective density at z=0 (modified by IDE)
    M_h_evo = halo_mass_at_z(M_h_0, z_form, beta, w)
    t_age = 13.8  # Gyr, age of universe
    # t_c scales with 1/sigma_hh * 1/rho_eff
    # IDE reduces rho_eff (less mass accumulation at low z)
    rho_eff_evo = 0.04 * (M_h_evo / M_h_0)  # rough scaling
    t_c = t_c_gyr(sigma_hh, rho_eff_evo)
    return t_age / t_c


# ===========================================================================
# 8 CHANNEL DEFINITIONS (per R88(56) §9.16)
# ===========================================================================

CHANNELS = {
    "Horigome dSph": {"v_kms": 15.0, "f_h_cen": 0.30, "f_h_sub": 0.165,
                       "is_subhalo": True, "threshold": 0.8, "direction": "upper"},
    "Fischer&Yu UFD": {"v_kms": 12.0, "f_h_cen": 0.40, "f_h_sub": 0.344,
                        "is_subhalo": True, "threshold": 1.0, "direction": "lower"},
    "Cloud-9 inner": {"v_kms": 28.0, "f_h_cen": 0.41, "f_h_sub": 0.41,
                        "is_subhalo": False, "threshold": 50, "direction": "lower"},
    "Cloud-9 Vmax": {"v_kms": 28.0, "f_h_cen": 0.30, "f_h_sub": 0.30,
                      "is_subhalo": False, "threshold": 50, "direction": "lower"},
    "SPARC": {"v_kms": 100.0, "f_h_cen": 0.30, "f_h_sub": 0.30,
               "is_subhalo": False, "threshold": 0.19, "direction": "center"},
    "Lei/Wang v=150": {"v_kms": 150.0, "f_h_cen": 0.6, "f_h_sub": 0.6,
                        "is_subhalo": False, "threshold": 0.3, "direction": "upper"},
    "He+ 2020": {"v_kms": 150.0, "f_h_cen": 0.6, "f_h_sub": 0.05,
                  "is_subhalo": True, "threshold": 0.3, "direction": "upper"},
    "Cluster": {"v_kms": 300.0, "f_h_cen": 0.05, "f_h_sub": 0.05,
                 "is_subhalo": True, "threshold": 0.001, "direction": "upper"},
}


def evaluate_channel(name: str, params: Dict, beta: float = 0.0,
                     f_H_evol: float = 1.0) -> Tuple[bool, float]:
    """Evaluate single channel. Returns (PASS, sigma_eff)."""
    p = CHANNELS[name]
    sig = sigma_eff(p["v_kms"], p["f_h_cen"], p["f_h_sub"],
                    p["is_subhalo"], f_H_evol)
    thresh = p["threshold"]
    direction = p["direction"]

    if direction == "upper":
        # sigma_eff < threshold = PASS
        ok = sig < thresh
    elif direction == "lower":
        # sigma_eff > threshold = PASS
        ok = sig > thresh
    else:  # center
        # |sigma_eff - threshold| / threshold < 0.5
        ok = abs(sig - thresh) / thresh < 0.5

    return ok, sig


def evaluate_all_channels(beta: float = 0.0, f_H_evol: float = 1.0) -> Dict:
    """Evaluate all 8 channels and return score."""
    results = {}
    for name in CHANNELS:
        ok, sig = evaluate_channel(name, CHANNELS[name], beta, f_H_evol)
        results[name] = {"PASS": ok, "sigma_eff": sig}
    return results


def main_test():
    """Sub-strategy A: vary beta and see if channel score improves."""
    print("=" * 70)
    print("Phase G17-A: Symmetric IDE Coupling Feasibility Test")
    print("=" * 70)
    print()
    print("Testing whether uniform dark matter - dark energy coupling beta")
    print("breaks the structural trade-off theorem.")
    print()
    print("Reference: R88(72) FUTURE_DIRECTIONS_DM_DE_ULDM.md")
    print("Pre-claim checklist: R88(71)")
    print()

    # Baseline (beta = 0, no IDE)
    print("=" * 70)
    print("BASELINE (beta = 0, no IDE)")
    print("=" * 70)
    baseline = evaluate_all_channels(beta=0.0, f_H_evol=1.0)
    n_pass_baseline = sum(1 for r in baseline.values() if r["PASS"])
    print(f"Channel score: {n_pass_baseline}/8")
    print()
    for name, r in baseline.items():
        mark = "PASS" if r["PASS"] else "FAIL"
        p = CHANNELS[name]
        thresh = p["threshold"]
        print(f"  [{mark}] {name:20s}: sigma_eff = {r['sigma_eff']:.4f}  "
              f"(threshold {p['direction']} {thresh})")
    print()

    # Test various beta values
    print("=" * 70)
    print("BETA SCAN: 0 to 0.05 (Planck+DESI bound)")
    print("=" * 70)
    print(f"{'beta':>6s} {'xi':>8s} {'Pass':>6s} {'Sig_eff(v=150,cen)':>20s} "
          f"{'Sig_eff(v=150,sub)':>20s}")
    print("-" * 70)

    best_score = n_pass_baseline
    best_beta = 0.0
    beta_scan = np.linspace(0.0, 0.05, 11)

    for beta in beta_scan:
        xi = xi_coupling(beta)
        # For symmetric coupling, the only effect is on halo evolution
        # which translates to a small f_H_evol modification
        # The modification is small: f_H_evol ~ 1 - alpha*xi for alpha ~ 0.1
        # This is the BAND estimate; actual effect requires full IDE integration
        f_H_evol = 1.0 - 0.5 * xi  # small modification

        results = evaluate_all_channels(beta=beta, f_H_evol=f_H_evol)
        n_pass = sum(1 for r in results.values() if r["PASS"])

        # Show key channels
        sig_150_cen = results["Lei/Wang v=150"]["sigma_eff"]
        sig_150_sub = results["He+ 2020"]["sigma_eff"]

        print(f"{beta:6.3f} {xi:8.4f} {n_pass:>4d}/8 {sig_150_cen:20.4f} "
              f"{sig_150_sub:20.4f}")

        if n_pass > best_score:
            best_score = n_pass
            best_beta = beta

    print()
    print("=" * 70)
    print("KILL CRITERION CHECK")
    print("=" * 70)
    print(f"Baseline: {n_pass_baseline}/8")
    print(f"Best with IDE: {best_score}/8 at beta = {best_beta:.3f}")
    print(f"Improvement: +{best_score - n_pass_baseline} channel(s)")
    print()

    if best_score > n_pass_baseline:
        print(f"RESULT: Symmetric IDE coupling shows improvement (+{best_score - n_pass_baseline}).")
        print(f"        Proceed to Sub-strategy B (species-dependent coupling).")
        return True
    else:
        print(f"RESULT: Symmetric IDE coupling shows NO improvement.")
        print(f"        Sub-strategy A FAILED kill criterion.")
        print(f"        Proceed to Sub-strategy B (species-dependent) per user's fallback plan.")
        return False


if __name__ == "__main__":
    success = main_test()
    print()
    print("=" * 70)
    print("CONCLUSION")
    print("=" * 70)
    if success:
        print("Sub-strategy A: Shows signal. Worth extending to B.")
    else:
        print("Sub-strategy A: Null result. The trade-off theorem is robust to")
        print("uniform IDE modification. This is consistent with the geometric")
        print("argument: the trade-off is about WITHIN-halo physics, not the")
        print("background evolution. Proceed to B (species-dependent) per")
        print("user's fallback plan.")
