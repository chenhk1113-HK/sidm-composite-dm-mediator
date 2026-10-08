"""
Phase G15 — Environment-dependent σ_m(v) with different shapes (R88(66))

Phase G13 found that simple shapes don't break the trade-off.
Phase G14 confirmed that even trade-off-breaking shapes fail other channels.

This phase tests ENVIRONMENT-DEPENDENT σ_m(v):
- Centrals: have all peaks (Cloud-9, massive galaxy, UFD)
- Subhalos: missing some peaks (heavy particles stripped, lose resonance capability)

This is the "exotic UV" scenario where the dark sector structure changes
based on whether the particle is in a central or subhalo environment.

The test:
- For each constrained halo, determine if central or subhalo
- Apply appropriate σ_m(v)
- Check if v=150 trade-off is broken for the PAIR (central vs subhalo)
- Check other channels
"""
from __future__ import annotations
import math
import numpy as np


OMEGA_M = 0.315
HUBBLE_H = 0.674


def dutton_maccio_2014_concentration(M_200, z=0.0):
    M_pivot = 2e12 / HUBBLE_H
    M_200_h = M_200 * HUBBLE_H
    log_c = math.log10(7.40) + (-0.091) * math.log10(M_200_h / M_pivot) + (-0.69) * math.log10(1 + z)
    return 10 ** log_c


def v_max_nfw(M_200, c_200):
    G = 4.302e-6
    R_200 = (G * M_200 / (100 * HUBBLE_H ** 2)) ** (1.0 / 3.0)
    r_s = R_200 / c_200
    r_max = 2.163 * r_s
    x = 2.163
    M_enc = M_200 * (math.log(1 + x) - x / (1 + x)) / (math.log(1 + c_200) - c_200 / (1 + c_200))
    return math.sqrt(G * M_enc / r_max)


def sigma_m_central(v):
    """σ_m(v) for central halos: ALL peaks present."""
    bg = 0.07 * (100 / v) ** 0.9
    cloud9 = 350 * math.exp(-((v - 28) ** 2) / 32)
    massive = 5 * math.exp(-((v - 150) ** 2) / 1500)
    ufd = 60 * math.exp(-((v - 10) ** 2) / 12.5)
    return bg + cloud9 + massive + ufd


def sigma_m_subhalo(v):
    """σ_m(v) for subhalos: heavy particles stripped, lose heavy-peaked resonances.

    The physics: if heavy particles (which carry the resonance peak) are preferentially
    stripped from subhalos (per R88(53) Direction A mechanism), then the σ_m(v)
    measured in subhalos is the light-component σ_m only.

    For this test: subhalo σ_m has only the background + UFD peak (which is from
    light species, not heavy).
    """
    bg = 0.07 * (100 / v) ** 0.9
    # Only UFD peak (assumed to be light-component)
    ufd = 5 * math.exp(-((v - 10) ** 2) / 12.5)  # reduced amplitude
    return bg + ufd


def f_H_sidm2c(r_over_r_s, tau=100.0, cap=0.60):
    return min(0.297 * (cap / 0.297), cap)


def test_environment_dependent():
    """Test environment-dependent σ_m(v) against all channels."""
    print("=" * 90)
    print("Phase G15 — Environment-Dependent σ_m(v) (R88(66))")
    print("=" * 90)
    print()
    print("Physics:")
    print("  Central halos: heavy + light species present")
    print("  Subhalos: heavy stripped (per R88(53) Direction A)")
    print("  Result: σ_m(v) differs between centrals and subhalos")
    print()

    # Channel classifications
    central_channels = [
        ("Lei/Wang massive galaxies (centrals)", 150, 1.5, "range", (0.1, 0.3)),
        ("Cloud-9 inner (central)", 28, 0.5, ">", 50),
        ("Cloud-9 V_max (central)", 31.12, 0.5, ">", 50),
        ("SPARC typical (central annulus)", 100, 1.5, "~", 0.19),
    ]

    subhalo_channels = [
        ("He+ 2020 (subhalo)", 150, 1.5, "<", 0.3),
        ("Horigome dSph (subhalo or isolated)", 15, 6.0, "<", 0.8),
        ("Fischer&Yu UFD (subhalo)", 7, 1.0, "tau_proxy", None),
    ]

    common_channels = [
        ("Cluster (central, but big)", 500, 1.0, "<", 0.001),
    ]

    print("=" * 90)
    print("CENTRAL HALO channels")
    print("=" * 90)
    print()
    print(f"{'Channel':<45} {'v':<6} {'r/r_s':<6} {'sigma_eff':<12} {'Threshold':<12} {'Verdict'}")
    print("-" * 95)

    n_central_pass = 0
    for name, v, r_obs, thresh_type, thresh_val in central_channels:
        f_h = f_H_sidm2c(r_obs)
        sm_v = sigma_m_central(v)
        sigma_eff = f_h ** 2 * sm_v

        if thresh_type == "<":
            ok = sigma_eff < thresh_val
            thresh_str = f"<{thresh_val}"
        elif thresh_type == ">":
            ok = sigma_eff > thresh_val
            thresh_str = f">{thresh_val}"
        elif thresh_type == "~":
            ok = 0.3 < (sigma_eff / thresh_val) < 3
            thresh_str = f"~{thresh_val}"
        elif thresh_type == "range":
            lo, hi = thresh_val
            ok = lo < sigma_eff < hi
            thresh_str = f"{lo}-{hi}"

        marker = "✓" if ok else "✗"
        if ok: n_central_pass += 1
        print(f"{name:<45} {v:<6.1f} {r_obs:<6.2f} {sigma_eff:<12.4f} {thresh_str:<12} {marker}")

    print()
    print("=" * 90)
    print("SUBHALO channels")
    print("=" * 90)
    print()
    print(f"{'Channel':<45} {'v':<6} {'r/r_s':<6} {'sigma_eff':<12} {'Threshold':<12} {'Verdict'}")
    print("-" * 95)

    n_subhalo_pass = 0
    for name, v, r_obs, thresh_type, thresh_val in subhalo_channels:
        f_h = f_H_sidm2c(r_obs)
        sm_v = sigma_m_subhalo(v)
        sigma_eff = f_h ** 2 * sm_v

        if thresh_type == "tau_proxy":
            # For UFD, check sigma_HH
            sigma_hh = sm_v
            ok = sigma_hh > 1.0
            thresh_str = "sigma_HH>1"
            print(f"{name:<45} {v:<6.1f} {r_obs:<6.2f} {sigma_hh:<12.3f} {thresh_str:<12} {'✓' if ok else '✗'}")
        else:
            if thresh_type == "<":
                ok = sigma_eff < thresh_val
                thresh_str = f"<{thresh_val}"
            elif thresh_type == ">":
                ok = sigma_eff > thresh_val
                thresh_str = f">{thresh_val}"

            marker = "✓" if ok else "✗"
            if ok: n_subhalo_pass += 1
            print(f"{name:<45} {v:<6.1f} {r_obs:<6.2f} {sigma_eff:<12.4f} {thresh_str:<12} {marker}")

    # Total score
    n_total = len(central_channels) + len(subhalo_channels) + len(common_channels)
    n_pass_total = n_central_pass + n_subhalo_pass

    print()
    print("=" * 90)
    print("v=150 TRADE-OFF TEST")
    print("=" * 90)
    print()
    print(f"  Lei/Wang (CENTRAL, σ_m_central at v=150):")
    print(f"    σ_eff = {f_H_sidm2c(1.5)**2 * sigma_m_central(150):.4f}")
    lei_pass = 0.1 < f_H_sidm2c(1.5)**2 * sigma_m_central(150) < 0.3
    print(f"    Lei/Wang constraint (0.1-0.3): {'PASS' if lei_pass else 'FAIL'}")
    print()
    print(f"  He+ 2020 (SUBHALO, σ_m_subhalo at v=150):")
    print(f"    σ_eff = {f_H_sidm2c(1.5)**2 * sigma_m_subhalo(150):.4f}")
    he_pass = f_H_sidm2c(1.5)**2 * sigma_m_subhalo(150) < 0.3
    print(f"    He+ 2020 constraint (<0.3): {'PASS' if he_pass else 'FAIL'}")
    print()

    trade_off_broken = lei_pass and he_pass
    print(f"Trade-off satisfied: {'YES' if trade_off_broken else 'NO'}")
    print()
    print(f"Total channels passing: {n_pass_total}/{n_total}")
    print()

    if trade_off_broken and n_pass_total >= 5:
        print("=" * 90)
        print("Phase G15 verdict (R88(66))")
        print("=" * 90)
        print()
        print("SUCCESS: Environment-dependent σ_m(v) BREAKS the structural trade-off")
        print(f"  v=150 trade-off satisfied: YES")
        print(f"  Lei/Wang: {f_H_sidm2c(1.5)**2 * sigma_m_central(150):.4f}")
        print(f"  He+ 2020: {f_H_sidm2c(1.5)**2 * sigma_m_subhalo(150):.4f}")
        print(f"  Other channels passing: {n_pass_total}/{n_total}")
        print()
        print("This is the FIRST shape that breaks the trade-off while satisfying")
        print("both Lei/Wang AND He+ 2020 simultaneously.")
        print()
        print("Mechanism: heavy species carry the v=150 resonance peak.")
        print("In centrals, both species present -> high σ_eff(150) for Lei/Wang.")
        print("In subhalos, heavy stripped -> σ_m(150) drops to background -> He+ satisfied.")
    else:
        print("=" * 90)
        print("Phase G15 verdict (R88(66))")
        print("=" * 90)
        print()
        print(f"Trade-off {'BROKEN' if trade_off_broken else 'STANDS'} with environment-dependent σ_m")
        print(f"Other channels passing: {n_pass_total}/{n_total}")
        if not trade_off_broken:
            print("Even environment-dependent shapes don't break the trade-off.")


if __name__ == "__main__":
    test_environment_dependent()
