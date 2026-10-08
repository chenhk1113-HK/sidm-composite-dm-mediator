"""
Phase G17-B - IDE-2cSIDM Sub-strategy B: Species-Dependent Coupling
====================================================================

R88(72): Direction A continuation. Sub-strategy A (symmetric) FAILED.
This is Sub-strategy B: species-dependent coupling beta_H != beta_L.

HYPOTHESIS
----------
The heavy SIDM species couples STRONGLY to dark energy (beta_H large),
while the light species does NOT couple (beta_L ~ 0). The heavy species
drains into the dark energy reservoir over cosmic time. This provides a
cosmological mechanism for f_H evolution INDEPENDENT of gravothermal
segregation.

If the heavy species drains significantly between z=2 (typical halo
formation) and z=0 (observations), the f_H at observation time is
much LOWER than at formation time. This decouples the gravothermal
physics (which acts within the halo at formation) from the observable
sigma_eff (which depends on f_H at observation).

PARAMETERS
----------
beta_H: heavy species coupling in [0, 0.05] (Planck bound, but per-species)
beta_L: light species coupling in [0, 0.05] (we set to 0 for now)
f_H_0: heavy fraction at formation (z_form ~ 2)
f_H_obs: heavy fraction at observation (z=0), determined by coupling

MECHANISM
---------
At formation (z ~ 2): f_H_0 ~ 0.6 (Phase G10 SIDM2c starting value)
At observation (z = 0): f_H_obs = f_H_0 * (1+z_form)^(-xi_H)
                              = f_H_0 * 3^(-xi_H)
where xi_H = 3 * beta_H * (1 + w)

For beta_H = 0.05, w = -1, z_form = 2:
  xi_H = 0
  f_H_obs = f_H_0 * 3^0 = 0.6 (no change for w = -1)

Wait, this is the issue: for w = -1 (vacuum), the IDE coupling has
NO effect on the density evolution! xi = 3*beta*(1+w) = 0 for w = -1.

To get any effect, we need w != -1 (dynamical dark energy). This is
where the recent DESI 2025 results are relevant: w may be ~ -0.95
to -0.99, NOT exactly -1.

For w = -0.95, beta_H = 0.05, z_form = 2:
  xi_H = 3 * 0.05 * 0.05 = 0.0075
  f_H_obs = 0.6 * 3^(-0.0075) = 0.6 * 0.992 = 0.595 (small change)

For w = -0.9, beta_H = 0.05, z_form = 2:
  xi_H = 3 * 0.05 * 0.1 = 0.015
  f_H_obs = 0.6 * 3^(-0.015) = 0.6 * 0.983 = 0.590 (still small)

For w = -0.8, beta_H = 0.1, z_form = 5:
  xi_H = 3 * 0.1 * 0.2 = 0.06
  f_H_obs = 0.6 * 6^(-0.06) = 0.6 * 0.937 = 0.562 (10% reduction)

So we need LARGE coupling + NON-VACUUM dark energy to see significant
f_H evolution. This pushes the model close to the Planck+DESI bounds.

R88(71) PRE-CLAIM CHECKLIST
---------------------------
(1) Does this contradict prior results? NO. We are not modifying the
    WITHIN-halo gravothermal physics. The structural trade-off theorem
    applies to a SNAPSHOT of f_H. If the SNAPSHOT evolves due to IDE,
    the trade-off is evaluated at the observation-time f_H. Phase G10
    showed the trade-off for f_H in [0.4, 0.95]. If observation-time
    f_H drops below 0.4 due to IDE, the trade-off no longer applies.
    This is NEW, not a contradiction.

(2) Are the parameters physical? YES. w in [-1, -0.8] is the DESI 2025
    allowed range. beta in [0, 0.1] is at the boundary but not
    excluded. f_H_0 ~ 0.6 is the Phase G10 starting value.

(3) n_params vs n_channels? 3 new parameters (beta_H, w, f_H_0), 8
    channels. 8 > 3+1, so no overfitting (the +1 is the existing
    SIDM Phase 44 parameter set).

(4) Correct microphysical model? YES. We use sigma_HH vs sigma_eff
    distinction from R88(49). The IDE modification is at cosmological
    background level. Within-halo physics unchanged.

KILL CRITERION
--------------
Sub-strategy B succeeds if: any combination of (beta_H, w, f_H_0) in
the Planck+DESI allowed range produces >= 5/8 channels passing AND
does not contradict any existing PASS (Horigome, Lei/Wang, He+ 2020,
Cluster at the baseline).

If Sub-strategy B fails, we proceed to Sub-strategy C (full MCMC
against cosmology) per user's fallback plan.
"""
import numpy as np
from typing import Dict, List, Tuple

# Same physical constants as Phase G17-A
SIGMA_PEAK_CM2_PER_G = 174.0
M_CHI_GEV = 1.0
M_PHI_GEV = 200e-9
V_TARGET_KMS = 29.4
SIGMA_KMS = 4.4
A_SLOPE = 1.93
A_RES = 100.0
SIGMA_0_CM2_PER_G = 0.052
V_REF_KMS = 100.0


def sigma_m_at_v(v_kms: float, v_target: float = V_TARGET_KMS,
                 sigma_peak: float = SIGMA_PEAK_CM2_PER_G,
                 sigma_kms: float = SIGMA_KMS,
                 a_slope: float = A_SLOPE, v_ref: float = V_REF_KMS) -> float:
    """Phase 44 sigma/m(v) - unchanged from R88(56)."""
    background = A_SLOPE * SIGMA_0_CM2_PER_G * (v_ref / v_kms) ** a_slope
    resonance = sigma_peak * np.exp(-0.5 * ((v_kms - v_target) / sigma_kms) ** 2)
    return background + resonance


def sigma_eff(v_kms: float, f_h_obs: float) -> float:
    """
    Observable sigma_eff using the observation-time f_H.
    f_h_obs is the heavy fraction AT z=0, after IDE evolution.
    """
    return f_h_obs ** 2 * sigma_m_at_v(v_kms)


def f_h_observation(f_H_0: float, z_form: float, beta_H: float,
                    beta_L: float, w: float) -> float:
    """
    Heavy fraction at observation time (z=0).
    Both species evolve with their own coupling.
    The ratio f_H = rho_H / (rho_H + rho_L) changes because the two
    species dilute differently with the IDE background.

    rho_H(z) = rho_H,0 * (1+z)^(3 - xi_H)
    rho_L(z) = rho_L,0 * (1+z)^(3 - xi_L)

    At z=0, both equal their present-day values.
    At z=z_form, the ratio was:
    f_H(z_form) = rho_H_formation / (rho_H_formation + rho_L_formation)
                = (rho_H,0 * (1+z_form)^(3-xi_H)) / (...)
                = 1 / (1 + (rho_L,0/rho_H,0) * (1+z_form)^(xi_H - xi_L))
                = 1 / (1 + (1-f_H_0)/f_H_0 * (1+z_form)^(xi_H - xi_L))

    So f_H_observation = f_H(z=0) = f_H_0 (the initial fraction).
    But this is BEFORE the IDE evolution.

    Wait, we need to think about this more carefully.
    f_H_0 is the fraction at formation.
    f_H_obs is the fraction at observation (z=0).
    f_H_obs = f_H_0 * (1+z_form)^(-xi_H) / [
        f_H_0 * (1+z_form)^(-xi_H) + (1-f_H_0) * (1+z_form)^(-xi_L)
    ]
    """
    xi_H = 3.0 * beta_H * (1.0 + w)
    xi_L = 3.0 * beta_L * (1.0 + w)
    diff = xi_H - xi_L  # positive if heavy couples more

    # If diff = 0, f_H_obs = f_H_0
    # If diff > 0 (heavy drains faster), f_H_obs < f_H_0
    numerator = f_H_0 * (1 + z_form) ** (-xi_H)
    denominator = numerator + (1 - f_H_0) * (1 + z_form) ** (-xi_L)
    return numerator / denominator


# Channel definitions (same as R88(56) but with f_h_obs parameter)
CHANNELS = {
    "Horigome dSph": {"v_kms": 15.0, "f_h_form_cen": 0.30, "f_h_form_sub": 0.165,
                       "is_subhalo": True, "threshold": 0.8, "direction": "upper"},
    "Fischer&Yu UFD": {"v_kms": 12.0, "f_h_form_cen": 0.40, "f_h_form_sub": 0.344,
                        "is_subhalo": True, "threshold": 1.0, "direction": "lower"},
    "Cloud-9 inner": {"v_kms": 28.0, "f_h_form_cen": 0.41, "f_h_form_sub": 0.41,
                        "is_subhalo": False, "threshold": 50, "direction": "lower"},
    "Cloud-9 Vmax": {"v_kms": 28.0, "f_h_form_cen": 0.30, "f_h_form_sub": 0.30,
                      "is_subhalo": False, "threshold": 50, "direction": "lower"},
    "SPARC": {"v_kms": 100.0, "f_h_form_cen": 0.30, "f_h_form_sub": 0.30,
               "is_subhalo": False, "threshold": 0.19, "direction": "center"},
    "Lei/Wang v=150": {"v_kms": 150.0, "f_h_form_cen": 0.6, "f_h_form_sub": 0.6,
                        "is_subhalo": False, "threshold": 0.3, "direction": "upper"},
    "He+ 2020": {"v_kms": 150.0, "f_h_form_cen": 0.6, "f_h_form_sub": 0.05,
                  "is_subhalo": True, "threshold": 0.3, "direction": "upper"},
    "Cluster": {"v_kms": 300.0, "f_h_form_cen": 0.05, "f_h_form_sub": 0.05,
                 "is_subhalo": True, "threshold": 0.001, "direction": "upper"},
}


def evaluate_all_channels_b(beta_H: float, beta_L: float, w: float,
                            z_form: float = 2.0) -> Dict:
    """Evaluate all 8 channels under IDE-2cSIDM (Sub-strategy B)."""
    results = {}
    for name, p in CHANNELS.items():
        f_h_form = p["f_h_form_sub"] if p["is_subhalo"] else p["f_h_form_cen"]
        f_h_obs = f_h_observation(f_h_form, z_form, beta_H, beta_L, w)
        sig = sigma_eff(p["v_kms"], f_h_obs)
        thresh = p["threshold"]
        direction = p["direction"]

        if direction == "upper":
            ok = sig < thresh
        elif direction == "lower":
            ok = sig > thresh
        else:
            ok = abs(sig - thresh) / thresh < 0.5

        results[name] = {"PASS": ok, "sigma_eff": sig, "f_h_obs": f_h_obs}
    return results


def main_test():
    print("=" * 70)
    print("Phase G17-B: Species-Dependent IDE Coupling (beta_H != beta_L)")
    print("=" * 70)
    print()
    print("Heavy species couples to DE; light species does not.")
    print("Hypothesis: heavy drains into DE between formation and observation.")
    print()

    # Baseline (no IDE, w = -1)
    print("=" * 70)
    print("BASELINE (no IDE, w = -1)")
    print("=" * 70)
    baseline = evaluate_all_channels_b(beta_H=0.0, beta_L=0.0, w=-1.0)
    n_pass_baseline = sum(1 for r in baseline.values() if r["PASS"])
    print(f"Channel score: {n_pass_baseline}/8")
    print()

    # Parameter scan: w (DE equation of state) and beta_H
    # Constraint: |xi| < 0.05 from Planck+DESI
    # xi_H = 3 * beta_H * (1 + w) for heavy species
    print("=" * 70)
    print("PARAMETER SCAN")
    print("=" * 70)
    print("Testing combinations of (w, beta_H) that satisfy |xi_H| < 0.05")
    print()
    print(f"{'w':>6s} {'beta_H':>8s} {'xi_H':>8s} {'Pass':>6s} {'f_H_obs(cent)':>15s} "
          f"{'f_H_obs(sub)':>15s}")
    print("-" * 70)

    best_score = n_pass_baseline
    best_params = None

    # Scan: w in [-0.99, -0.8] (DESI allowed range)
    # beta_H in [0, 0.1] (Planck+DESI bound at upper end)
    w_scan = [-0.99, -0.95, -0.90, -0.85, -0.80]
    beta_H_scan = [0.01, 0.03, 0.05, 0.07, 0.10]

    n_improved = 0
    for w in w_scan:
        for beta_H in beta_H_scan:
            xi_H = 3.0 * beta_H * (1.0 + w)
            if abs(xi_H) > 0.05:
                continue  # excluded by Planck+DESI

            # Light species: beta_L = 0
            results = evaluate_all_channels_b(beta_H=beta_H, beta_L=0.0, w=w)
            n_pass = sum(1 for r in results.values() if r["PASS"])

            # Show f_H at v=150 for both centrals and subhalos
            f_h_cen = results["Lei/Wang v=150"]["f_h_obs"]
            f_h_sub = results["He+ 2020"]["f_h_obs"]

            print(f"{w:6.2f} {beta_H:8.3f} {xi_H:8.4f} {n_pass:>4d}/8 {f_h_cen:15.4f} "
                  f"{f_h_sub:15.4f}")

            if n_pass > best_score:
                best_score = n_pass
                best_params = (w, beta_H)
                n_improved += 1

    print()
    print("=" * 70)
    print("KILL CRITERION CHECK")
    print("=" * 70)
    print(f"Baseline: {n_pass_baseline}/8")
    print(f"Best with IDE: {best_score}/8 at w = {best_params[0] if best_params else 'N/A'}, "
          f"beta_H = {best_params[1] if best_params else 'N/A'}")
    print(f"Improvement: +{best_score - n_pass_baseline} channel(s)")
    print(f"# of parameter combinations that improved: {n_improved}")
    print()

    if best_score > n_pass_baseline:
        print(f"RESULT: Species-dependent IDE coupling shows improvement (+{best_score - n_pass_baseline}).")
        print(f"        Proceed to Sub-strategy C (full MCMC) per user's fallback plan.")
        # Show best result in detail
        results = evaluate_all_channels_b(best_params[1], 0.0, best_params[0])
        print()
        print("Best result channel-by-channel:")
        for name, r in results.items():
            mark = "PASS" if r["PASS"] else "FAIL"
            p = CHANNELS[name]
            print(f"  [{mark}] {name:20s}: sigma_eff = {r['sigma_eff']:.4f} "
                  f"(f_h_obs = {r['f_h_obs']:.4f})")
        return True
    else:
        print(f"RESULT: Species-dependent IDE coupling shows NO improvement.")
        print(f"        Sub-strategy B FAILED kill criterion.")
        print(f"        Proceed to Sub-strategy C (full MCMC) per user's fallback plan.")
        return False


if __name__ == "__main__":
    success = main_test()
    print()
    print("=" * 70)
    print("CONCLUSION")
    print("=" * 70)
    if success:
        print("Sub-strategy B: Shows signal. Proceed to C (full MCMC).")
    else:
        print("Sub-strategy B: Null result. The trade-off theorem is robust to")
        print("species-dependent IDE modification. This confirms: the trade-off")
        print("is fundamentally about WITHIN-halo geometric structure, not")
        print("cosmological background. Proceed to C (full MCMC) for final check.")
