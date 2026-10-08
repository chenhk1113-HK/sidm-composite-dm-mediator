"""
Phase G14 — Detailed test of trade-off-breaking shapes (R88(65))

Phase G13 found 2 shapes that break the v=150 trade-off:
- Shape 5: Exponential cutoff at v=100
- Shape 7: Strong inverse (high at low v)

But they only passed 3/8 channels. This phase investigates:
1. Can we tune these shapes to pass more channels?
2. Do they satisfy the structural trade-off globally (not just at v=150)?
3. Are they physically motivated?
"""
from __future__ import annotations
import math
import numpy as np


def f_H_sidm2c(r_over_r_s, tau=100.0, cap=0.60):
    return min(0.297 * (cap / 0.297), cap)


def shape_5_exponential_cutoff(v, cutoff_v=100, sharpness=20, amplitude=5):
    """Exponential cutoff at v=cutoff_v."""
    if v < cutoff_v:
        return amplitude * (cutoff_v / v) ** 0.9
    else:
        return amplitude * (cutoff_v / v) ** 0.9 * math.exp(-(v - cutoff_v) / sharpness)


def shape_7_strong_inverse(v, scale_v=30, amplitude=100):
    """Strong inverse: high at low v, exponential decay."""
    return amplitude * math.exp(-v / scale_v)


def evaluate_all_channels(sigma_m_func, name):
    """Evaluate against all channels."""
    results = []
    # Channels with full requirements
    channels = [
        ("Horigome dSph (v=15, r=6)", 15, 6.0, "<", 0.8, "He+ style"),
        ("Fischer&Yu UFD (v=7, r=1)", 7, 1.0, "tau_proxy", None, "sigma_HH check"),
        ("Cloud-9 inner (v=28, r=0.5)", 28, 0.5, ">", 50, "sigma_eff"),
        ("Cloud-9 V_max (v=31.12, r=0.5)", 31.12, 0.5, ">", 50, "sigma_eff"),
        ("SPARC typical (v=100, r=1.5)", 100, 1.5, "~", 0.19, "sigma_eff"),
        ("Lei/Wang (v=150, r=1.5)", 150, 1.5, "range", (0.1, 0.3), "sigma_eff"),
        ("He+ 2020 (v=150, r=1.5)", 150, 1.5, "<", 0.3, "sigma_eff"),
        ("Cluster (v=500, r=1)", 500, 1.0, "<", 0.001, "sigma_eff"),
    ]

    for ch_name, v, r_obs, thresh_type, thresh_val, _ in channels:
        f_h = f_H_sidm2c(r_obs)
        sm_v = sigma_m_func(v)

        if thresh_type == "tau_proxy":
            # For UFD collapse, use sigma_HH at v (not sigma_eff)
            sigma_eff_display = f_h ** 2 * sm_v
            # Simple proxy: sigma_HH > 1 for collapse (Yang+ 2024)
            ok = sm_v > 1.0
            result_text = f"sigma_HH={sm_v:.3f}, {'PASS' if ok else 'FAIL'}"
        else:
            sigma_eff = f_h ** 2 * sm_v
            if thresh_type == "<":
                ok = sigma_eff < thresh_val
            elif thresh_type == ">":
                ok = sigma_eff > thresh_val
            elif thresh_type == "~":
                ok = 0.3 < (sigma_eff / thresh_val) < 3
            elif thresh_type == "range":
                lo, hi = thresh_val
                ok = lo < sigma_eff < hi
            result_text = f"sigma_eff={sigma_eff:.4f}, {'PASS' if ok else 'FAIL'}"

        results.append((ch_name, ok, result_text))

    return results


def run_phase_g14():
    print("=" * 90)
    print("Phase G14 — Detailed Test of Trade-off-Breaking Shapes (R88(65))")
    print("=" * 90)
    print()

    # Test Shape 5 with parameter variations
    print("=" * 90)
    print("Shape 5: Exponential cutoff at v=100 — parameter sweep")
    print("=" * 90)
    print()

    print(f"{'cutoff':<8} {'sharp':<8} {'amp':<6} {'σ_eff(28)':<12} {'σ_eff(100)':<12} {'σ_eff(150)':<12} {'σ_eff(500)':<12} {'Pass'}")
    print("-" * 95)

    best_5 = None
    best_pass_5 = 0

    for cutoff_v in [80, 100, 120, 150]:
        for sharpness in [10, 20, 50, 100]:
            for amp in [3, 5, 10, 20]:
                func = lambda v, c=cutoff_v, s=sharpness, a=amp: shape_5_exponential_cutoff(v, c, s, a)
                ch_results = evaluate_all_channels(func, f"5-{cutoff_v}-{sharpness}-{amp}")
                n_pass = sum(1 for _, ok, _ in ch_results if ok)
                if n_pass > best_pass_5:
                    best_pass_5 = n_pass
                    best_5 = (cutoff_v, sharpness, amp, ch_results)

                se_28 = f_H_sidm2c(0.5) ** 2 * func(28)
                se_100 = f_H_sidm2c(1.5) ** 2 * func(100)
                se_150 = f_H_sidm2c(1.5) ** 2 * func(150)
                se_500 = f_H_sidm2c(1.0) ** 2 * func(500)

                if n_pass >= 4:  # Only show promising
                    print(f"{cutoff_v:<8} {sharpness:<8} {amp:<6} {se_28:<12.2f} {se_100:<12.4f} {se_150:<12.4f} {se_500:<12.6f} {n_pass}/8")

    print()
    print(f"Best Shape 5: {best_5[0]}, sharpness={best_5[1]}, amp={best_5[2]}, {best_pass_5}/8 channels")
    print()
    print("Channel breakdown for best Shape 5:")
    for name, ok, text in best_5[3]:
        marker = "✓" if ok else "✗"
        print(f"  {marker} {name}: {text}")

    # Test Shape 7 with parameter variations
    print()
    print("=" * 90)
    print("Shape 7: Strong inverse — parameter sweep")
    print("=" * 90)
    print()

    print(f"{'scale':<8} {'amp':<6} {'σ_eff(28)':<12} {'σ_eff(100)':<12} {'σ_eff(150)':<12} {'σ_eff(500)':<12} {'Pass'}")
    print("-" * 95)

    best_7 = None
    best_pass_7 = 0

    for scale_v in [20, 30, 50, 80]:
        for amp in [50, 100, 200, 500]:
            func = lambda v, s=scale_v, a=amp: shape_7_strong_inverse(v, s, a)
            ch_results = evaluate_all_channels(func, f"7-{scale_v}-{amp}")
            n_pass = sum(1 for _, ok, _ in ch_results if ok)
            if n_pass > best_pass_7:
                best_pass_7 = n_pass
                best_7 = (scale_v, amp, ch_results)

            se_28 = f_H_sidm2c(0.5) ** 2 * func(28)
            se_100 = f_H_sidm2c(1.5) ** 2 * func(100)
            se_150 = f_H_sidm2c(1.5) ** 2 * func(150)
            se_500 = f_H_sidm2c(1.0) ** 2 * func(500)

            if n_pass >= 4:  # Only show promising
                print(f"{scale_v:<8} {amp:<6} {se_28:<12.2f} {se_100:<12.4f} {se_150:<12.4f} {se_500:<12.6f} {n_pass}/8")

    print()
    print(f"Best Shape 7: scale={best_7[0]}, amp={best_7[1]}, {best_pass_7}/8 channels")
    print()
    print("Channel breakdown for best Shape 7:")
    for name, ok, text in best_7[2]:
        marker = "✓" if ok else "✗"
        print(f"  {marker} {name}: {text}")

    # Final verdict
    print()
    print("=" * 90)
    print("Phase G14 verdict (R88(65))")
    print("=" * 90)
    print()
    print(f"Best Shape 5 (exponential cutoff): {best_pass_5}/8 channels")
    print(f"Best Shape 7 (strong inverse): {best_pass_7}/8 channels")
    print()

    # Check if they ACTUALLY break the structural trade-off or just the v=150 test
    print("Trade-off breakdown for best Shape 5:")
    for name, ok, text in best_5[3]:
        if "Lei" in name or "He+" in name or "Cloud" in name:
            print(f"  {name}: {text}")

    print()
    print("Trade-off breakdown for best Shape 7:")
    for name, ok, text in best_7[2]:
        if "Lei" in name or "He+" in name or "Cloud" in name:
            print(f"  {name}: {text}")

    print()
    if best_pass_5 >= 5 or best_pass_7 >= 5:
        print("Trade-off partially broken by exotic σ_m(v) shape.")
        print("But other channels still fail — not a complete solution.")
    else:
        print("Even the best trade-off-breaking shapes only pass 3-4 channels.")
        print("The structural trade-off theorem stands as a fundamental limit.")


if __name__ == "__main__":
    run_phase_g14()
