"""
Phase G12 — Multi-species UV completion (R88(61), Direction B)

The only forward path that can break the structural trade-off theorem.
Tests whether a two-species SIDM model with environment-dependent sigma(v)
can satisfy Sameie+ 2020 (subhalos) and Lei/Wang (centrals) simultaneously.

Setup:
- Species 1: heavy (H), sigma_H(v) - drives gravothermal cascade
- Species 2: light (L), sigma_L(v) - environment-independent
- f_H(r) = local heavy fraction (varies with environment)
- Centrals: both species present, f_H ~ 0.4
- Subhalos: heavy preferentially stripped, f_H ~ 0.1

Test:
- sigma_central(v) = (f_H * sigma_H + (1-f_H) * sigma_L)^2 / f_H^2 ... 
  Actually: sigma_eff at observation radius depends on local f_H(r)
- sigma_sub(v) uses subhalo-specific f_H which is reduced due to stripping

Critical test: can this break the trade-off theorem?
"""
from __future__ import annotations
import math
import numpy as np


# Two-species sigma shapes
def sigma_H(v):
    """Heavy species sigma/m(v) - has Cloud-9 resonance."""
    background_H = 0.07 * (100/v)**0.9
    cloud9 = 350 * math.exp(-((v-28)**2)/32)
    return background_H + cloud9


def sigma_L(v):
    """Light species sigma/m(v) - flat, no resonance."""
    return 0.5 * (100/v)**0.9  # background only, lower amplitude


# Combined sigma for two-species (gravothermal = sum of partial pressures)
def sigma_m_two_species(v, f_H_local):
    """Total scattering rate for two-species SIDM.

    sigma_m_total = f_H * sigma_H + (1-f_H) * sigma_L
    (sum of individual species scattering rates, weighted by abundance)
    """
    return f_H_local * sigma_H(v) + (1 - f_H_local) * sigma_L(v)


# Per-environment f_H values
F_H_CENTRAL = 0.4   # central halos: both species present
F_H_SUBHALO = 0.1   # subhalos: heavy preferentially stripped

# Observation radii
R_OBS_CENTRAL = 1.5  # r_s (typical for SPARC, Lei/Wang kinematic radii)
R_OBS_SUBHALO = 1.0  # r_s (typical for subhalo lensing)


def run_phase_g12():
    print("=" * 90)
    print("Phase G12 — Multi-Species UV Completion (R88(61), Direction B)")
    print("=" * 90)
    print()
    print("Setup:")
    print("  Species 1 (heavy): sigma_H(v) = 0.07*(100/v)^0.9 + 350*exp(-(v-28)^2/32)")
    print("  Species 2 (light): sigma_L(v) = 0.5*(100/v)^0.9")
    print("  f_H(central) = 0.4 (both species present)")
    print("  f_H(subhalo) = 0.1 (heavy preferentially stripped)")
    print()

    # Test all channels
    channels = [
        # (name, v, r_obs, environment, threshold_type, threshold_value)
        ("Horigome dSph (Fornax, r~6 r_s)", 15, 6.0, "subhalo", "<", 0.8),
        ("Fischer&Yu UFD (Tucana II, V=7)", 7, 1.0, "subhalo", "tau", 1.0),
        ("Cloud-9 inner H I (r~0.5 r_s)", 28, 0.5, "central", ">", 50),
        ("Cloud-9 V_max (v=31.12)", 31.12, 0.5, "central", ">", 50),
        ("SPARC typical (annulus avg)", 100, 1.5, "central", "~", 0.19),
        ("Lei/Wang massive (v=150)", 150, 1.5, "central", "range", (0.1, 0.3)),
        ("Sameie+ 2020 galaxy lensing (v=150)", 150, 1.5, "subhalo", "<", 0.3),
        ("Cluster (r~1 r_s)", 500, 1.0, "central", "<", 0.001),
    ]

    # Compute sigma_eff for each channel
    print("=" * 90)
    print("Channel-by-channel test with two-species sigma_m(v)")
    print("=" * 90)
    print()
    print(f"{'Channel':<42} {'v':<7} {'env':<10} {'f_H':<6} {'sigma_m':<10} {'sigma_eff':<12} {'Threshold':<14} {'Verdict'}")
    print("-" * 120)

    n_pass = 0
    n_marg = 0
    n_fail = 0
    verdicts = []

    for name, v, r_obs, env, thresh_type, thresh_val in channels:
        # f_H at observation radius (environmental dependence)
        if env == "central":
            f_H = F_H_CENTRAL
        else:
            f_H = F_H_SUBHALO

        # sigma_eff = f_H^2 * sigma_m(v) where sigma_m is two-species weighted
        sigma_m_v = sigma_m_two_species(v, f_H)
        sigma_eff = f_H ** 2 * sigma_m_v

        # Evaluate against threshold
        if thresh_type == "<":
            if sigma_eff < thresh_val / 3:
                verdict = "PASS"
                n_pass += 1
            elif sigma_eff < thresh_val:
                verdict = "MARGINAL"
                n_marg += 1
            else:
                verdict = "FAIL"
                n_fail += 1
            thresh_str = f"<{thresh_val}"
        elif thresh_type == ">":
            if sigma_eff > thresh_val * 3:
                verdict = "PASS"
                n_pass += 1
            elif sigma_eff > thresh_val:
                verdict = "MARGINAL"
                n_marg += 1
            else:
                verdict = "FAIL"
                n_fail += 1
            thresh_str = f">{thresh_val}"
        elif thresh_type == "~":
            ratio = sigma_eff / thresh_val
            if 0.3 < ratio < 3:
                verdict = "PASS"
                n_pass += 1
            else:
                verdict = "MARGINAL"
                n_marg += 1
            thresh_str = f"~{thresh_val}"
        elif thresh_type == "range":
            lo, hi = thresh_val
            if lo < sigma_eff < hi:
                verdict = "PASS"
                n_pass += 1
            elif sigma_eff < lo:
                verdict = "FAIL (below)"
                n_fail += 1
            else:
                verdict = "MARGINAL (above)"
                n_marg += 1
            thresh_str = f"{lo}-{hi}"
        else:  # tau
            # Sigma_HH at v
            sigma_hh = sigma_H(v)
            # Yang+ 2024 t_c calculation
            rho_eff = 0.01  # M_sun/pc^3 (approximate for UFD)
            t_c = 28.7 * (7.1 / sigma_hh) * (0.04 / rho_eff)
            tau = 10.0 / t_c
            if tau >= 1.0:
                verdict = "PASS"
                n_pass += 1
            elif tau >= 0.3:
                verdict = "MARGINAL"
                n_marg += 1
            else:
                verdict = "FAIL"
                n_fail += 1
            thresh_str = f"tau={tau:.3f}"
            sigma_eff = tau  # display tau as the relevant quantity

        verdicts.append((name, verdict))
        print(f"{name:<42} {v:<7.1f} {env:<10} {f_H:<6.2f} {sigma_m_v:<10.3f} {sigma_eff:<12.4f} {thresh_str:<14} {verdict}")

    print()
    print("=" * 90)
    print("Summary")
    print("=" * 90)
    print()
    print(f"{n_pass} PASS, {n_marg} MARGINAL, {n_fail} FAIL out of {len(channels)} channels")
    print()

    # Critical test: does this break the trade-off theorem?
    lei_se = F_H_CENTRAL ** 2 * sigma_m_two_species(150, F_H_CENTRAL)
    he_se = F_H_SUBHALO ** 2 * sigma_m_two_species(150, F_H_SUBHALO)

    print("v=150 trade-off test:")
    print(f"  Lei/Wang (central, f_H=0.4): sigma_eff = {lei_se:.4f}")
    print(f"  Sameie+ 2020 (subhalo, f_H=0.1): sigma_eff = {he_se:.4f}")
    print()

    if 0.1 < lei_se < 0.3 and he_se < 0.3:
        print("✓ Trade-off theorem BROKEN by multi-species UV:")
        print(f"  Lei/Wang: {lei_se:.4f} within [0.1, 0.3] window")
        print(f"  Sameie+ 2020: {he_se:.4f} below 0.3 ceiling")
        print("  Environment-dependent f_H resolves v=150 no-go")
        trade_off_verdict = "BROKEN"
    elif lei_se > 0.3 and he_se < 0.3:
        print("⚠ Lei/Wang passes, Sameie+ 2020 passes, but Lei/Wang overshoots:")
        print(f"  Lei/Wang sigma_eff = {lei_se:.4f} > 0.3 (over both bounds)")
        trade_off_verdict = "PARTIAL"
    else:
        print(f"✗ Trade-off theorem NOT broken:")
        print(f"  Either Lei/Wang ({lei_se:.4f}) or Sameie+ 2020 ({he_se:.4f}) constraint violated")
        trade_off_verdict = "STANDS"

    print()
    print("=" * 90)
    print("Direction B verdict (R88(61))")
    print("=" * 90)
    print()
    if trade_off_verdict == "BROKEN":
        print("SUCCESS: Two-species UV with environment-dependent f_H breaks trade-off")
        print("Both Sameie+ 2020 and Lei/Wang constraints can be satisfied simultaneously.")
    elif trade_off_verdict == "PARTIAL":
        print("PARTIAL: One constraint satisfied, but other overshoots")
        print("Need finer tuning of f_H values or sigma shapes")
    else:
        print("FAILURE: Two-species UV does NOT break trade-off theorem")
        print("Need different sigma shapes or different environmental dependence mechanism")

    print()
    return trade_off_verdict, lei_se, he_se


if __name__ == "__main__":
    verdict, lei, he = run_phase_g12()
    print()
    print("Final:", verdict)
    print("  Lei/Wang sigma_eff(150) =", round(lei, 4))
    print("  Sameie+ 2020 sigma_eff(150) =", round(he, 4))
