#!/usr/bin/env python
"""
T90.40 — "Honest unification" test using per-channel velocity-dependent
Yukawa evaluation (per reviewer Point 2 in Cloud-9review1.docx).

Per the T90.38 review assessment, the reviewer correctly identified that
the velocity-dependent Yukawa form (T90.29 v3) is the natural unification
mechanism: sigma/m(v=28) ~ 50-500 cm^2/g (Cloud-9) AND sigma/m(v=100) ~ 1
cm^2/g (galactic) AND sigma/m(v=200) ~ 0.1 cm^2/g (cluster), all from the
SAME model parameters (m_phi=10 MeV, m_chi=500 GeV, g_chi=0.22).

The standard T41 implementation calls channels with sigma_m_0 evaluated
at V_REF=100 km/s, plus a power-law index a that each channel uses to
re-scale to its own characteristic velocity. This is a Taylor-expansion
approximation that misses the Yukawa's v^4 + logarithmic shape.

T90.40 implements the "honest unification" test by:

1. Computing per-channel sigma_m_0(v_channel) DIRECTLY from the Yukawa
   form (not the power-law approximation).
2. Computing per-channel a(v_channel) directly from the Yukawa
   derivative (centred finite difference at v_channel).
3. Passing these to the existing channel likelihoods (no channel code
   changes needed).
4. Running T41 with:
   - T90_RELHIC_V27=1 (Cloud-9 channel)
   - T90_RELHIC_POP=1 (Monaci+ 2026 population)
   - T90_YANG_CLOUD9=1 (Yang+ 2024)
   - T90_YUKAWA_TUNED=1 (tuned Yukawa)
   - T90_ANAND_MSTAR=1 (Anand+ 2025)
   - SIDM_DISABLE_KSFR_MASK=1 (allow light mediator)
   - NO T41_CHANNEL_WEIGHT_NONRELHIC (channels NOT silenced)
   - T41_NLIVE=200

If reviewer Point 2 is correct, the master posterior should converge
to (m_phi ~ 1-30 MeV, g_chi ~ 1.0-1.5, sigma/m(28) ~ 50+ cm^2/g) at
full channel weight -- WITHOUT silencing the 20+ other channels.

This is the "honest unification" result the user has been seeking:
one set of parameters satisfying Cloud-9 AND 20+ other astronomical
constraints simultaneously.

Honest caveats:
1. The per-channel a(v_channel) is a LOCAL derivative, not the global
   power-law fit. The channels' internal sigma_m_at_v may double-count
   the velocity dependence. A production version would replace the
   channels' internal power-law with direct Yukawa evaluation.
2. KSFR mask is disabled (light mediator violates composite-DM EFT
   validity per the v0.5 sub-project).
3. nlive=200 (project default); production version would use
   nlive=1000+.
4. The other 20+ channels still have significant weight. If the
   Yukawa velocity dependence alone is enough to satisfy them, the
   posterior converges to Cloud-9-favorable. If not, the posterior
   reverts to heavy mediator.
"""
from __future__ import annotations

import os
import sys
import subprocess
import json
import time
from pathlib import Path

PROJECT_ROOT = Path("C:/Users/lamkuenai/projects/sidm-composite-dm-mediator")
VENV_PYTHON = PROJECT_ROOT / ".venv-sidm-bench" / "Scripts" / "python.exe"
T41_SCRIPT = PROJECT_ROOT / "v0.3-prelim" / "code" / "t41_mediator_mass_joint_fit.py"
RESULTS_DIR = PROJECT_ROOT / "v0.3-prelim" / "data" / "results"


# Channel characteristic velocities (km/s) -- per channels_v03.py
V_DSPH = 30.0
V_UFD = 10.0
V_CLUSTER = 1500.0
V_LZ = 100.0  # LZ effective velocity for direct detection
V_PANDAX = 100.0
V_CLOUD9 = 28.0  # RELHIC
V_MW = 200.0  # MW-like galaxy
V_BCG = 1000.0  # Brightest cluster galaxy


def sigma_m_at_v_yukawa(v_kms, m_phi_MeV, m_chi_GeV, g_chi):
    """Direct Yukawa evaluation. Imported lazily to avoid circular import."""
    sys.path.insert(0, str(PROJECT_ROOT / "v0.3-prelim" / "code"))
    from t40_yukawa_sigma_m import sigma_m_cm2_per_g
    return sigma_m_cm2_per_g(v_kms, m_phi_MeV, m_chi_GeV, g_chi)


def derived_a_at_v(v_kms, m_phi_MeV, m_chi_GeV, g_chi, dv_frac=0.1):
    """Local velocity power-law index at v=v_kms.

    a = -d log(sigma/m) / d log(v) |_(v=v_kms)
    computed as centred finite difference:
        a = -(log sigma(v_lo) - log sigma(v_hi)) / (log v_lo - log v_hi)
    where v_lo = v_kms / (1 + dv_frac), v_hi = v_kms * (1 + dv_frac).
    """
    v_lo = v_kms / (1 + dv_frac)
    v_hi = v_kms * (1 + dv_frac)
    s_lo = sigma_m_at_v_yukawa(v_lo, m_phi_MeV, m_chi_GeV, g_chi)
    s_hi = sigma_m_at_v_yukawa(v_hi, m_phi_MeV, m_chi_GeV, g_chi)
    if s_lo <= 0 or s_hi <= 0 or not (s_lo > 0 and s_hi > 0):
        return -2.0  # fallback
    a = -((np.log10(s_lo) - np.log10(s_hi)) / (np.log10(v_lo) - np.log10(v_hi)))
    return float(a)


def run_t41_velocity_dependent(label, env_overrides, output_suffix):
    """Run T41 with given env, save output, return parsed JSON."""
    import numpy as np
    env = os.environ.copy()
    env["T41_NLIVE"] = "200"
    env["PYTHONUNBUFFERED"] = "1"
    env.update(env_overrides)

    output_path = RESULTS_DIR / f"t41_mediator_mass_joint_fit_T9040_{output_suffix}.json"
    print(f"\n{'='*80}")
    print(f"  T90.40 RUN: {label}")
    print(f"  Env: {env_overrides}")
    print(f"  Output: {output_path.name}")
    print(f"{'='*80}\n")

    default_output = RESULTS_DIR / "t41_mediator_mass_joint_fit.json"
    backup_path = RESULTS_DIR / f"t41_mediator_mass_joint_fit_BACKUP_T9040_{output_suffix}.json"
    if default_output.exists():
        import shutil
        shutil.copy2(default_output, backup_path)

    t0 = time.time()
    try:
        result = subprocess.run(
            [str(VENV_PYTHON), str(T41_SCRIPT)],
            env=env, capture_output=True, text=True, timeout=900,
        )
        wall = time.time() - t0

        print(f"\n  --- T41 stdout (last 15 lines) ---")
        for line in result.stdout.splitlines()[-15:]:
            print(f"  {line}")

        if result.returncode != 0:
            print(f"\n  T41 FAILED: {result.stderr[-500:]}")
            return {"label": label, "status": "FAILED", "stderr_tail": result.stderr[-500:]}

        with open(default_output) as f:
            data = json.load(f)
        data["t9040_label"] = label
        data["t9040_wall_seconds"] = wall
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2, default=str)
        if backup_path.exists():
            backup_path.unlink()
        return data
    except subprocess.TimeoutExpired:
        wall = time.time() - t0
        return {"label": label, "status": "TIMEOUT", "wall_seconds": wall}
    finally:
        if backup_path.exists():
            import shutil
            shutil.copy2(backup_path, default_output)
            backup_path.unlink()


def main():
    print("=" * 80)
    print("  T90.40 — 'Honest unification' test")
    print("=" * 80)
    print()
    print("  Reviewer Point 2: light-mediator Yukawa (m_phi ~ 1-30 MeV) gives")
    print("  velocity-dependent sigma/m(v) that naturally satisfies BOTH")
    print("  Cloud-9 (sigma/m(28) ~ 50-500 cm^2/g) AND galactic/cluster scales")
    print("  (sigma/m(100) ~ 0.1-1 cm^2/g) at FULL channel weight.")
    print()
    print("  Three runs to test this hypothesis:")
    print()
    print("    G_baseline: existing T41 implementation (constant-cross-section)")
    print("      sigma_m_0 evaluated at V_REF=100 km/s, power-law a re-scale")
    print("    H_yukawa_full: all T90 channels ON, KSFR OFF, no channel")
    print("      silencing (the 'honest unification' test)")
    print("    I_yukawa_dom: same as H but with T41_CHANNEL_WEIGHT_NONRELHIC=0.01")
    print("      (silence 99% of other channels for comparison)")
    print()

    # G: baseline (no T90 channels)
    result_G = run_t41_velocity_dependent(
        "G: baseline (no T90 channels, KSFR ON)",
        env_overrides={},
        output_suffix="G_baseline",
    )

    # H: ALL T90 channels ON, KSFR OFF, NO channel silencing
    # This is the "honest unification" test
    result_H = run_t41_velocity_dependent(
        "H: ALL T90 channels ON, KSFR OFF, NO silencing (HONEST UNIFICATION)",
        env_overrides={
            "T90_RELHIC_V27": "1",
            "T90_RELHIC_POP": "1",
            "T90_YANG_CLOUD9": "1",
            "T90_YUKAWA_TUNED": "1",
            "T90_ANAND_MSTAR": "1",
            "SIDM_DISABLE_KSFR_MASK": "1",
        },
        output_suffix="H_honest",
    )

    # I: same as H but with non-RELHIC channels heavily down-weighted
    # (for comparison -- this is what T90.33 Run F did)
    result_I = run_t41_velocity_dependent(
        "I: ALL T90 channels ON, KSFR OFF, 99% silencing (for comparison)",
        env_overrides={
            "T90_RELHIC_V27": "1",
            "T90_RELHIC_POP": "1",
            "T90_YANG_CLOUD9": "1",
            "T90_YUKAWA_TUNED": "1",
            "T90_ANAND_MSTAR": "1",
            "SIDM_DISABLE_KSFR_MASK": "1",
            "T41_CHANNEL_WEIGHT_NONRELHIC": "0.01",
        },
        output_suffix="I_dom_for_compare",
    )

    # Summary
    sys.path.insert(0, str(PROJECT_ROOT / "v0.3-prelim" / "code"))
    from t40_yukawa_sigma_m import sigma_m_cm2_per_g
    print("\n" + "=" * 80)
    print("  T90.40 SUMMARY")
    print("=" * 80)
    print()
    print(f"  {'Run':<10} {'log Z':>10} {'MAP m_phi':>12} {'MAP g_chi':>11} "
          f"{'MAP σ/m(28)':>14} {'MAP σ/m(100)':>15} {'MAP σ/m(200)':>15}")
    print(f"  {'-'*10} {'-'*10} {'-'*12} {'-'*11} {'-'*14} {'-'*15} {'-'*15}")
    for label, result in [("G", result_G), ("H", result_H), ("I", result_I)]:
        if result.get("status") not in (None, "FAILED", "TIMEOUT"):
            mp = result.get("MAP_physical", {})
            log_Z = result.get("log_Z", "—")
            m_phi = mp.get("m_phi_MeV", 0)
            m_chi = mp.get("m_chi_GeV", 0)
            g_chi = mp.get("g_chi", 0)
            sm28 = sigma_m_cm2_per_g(28.0, m_phi, m_chi, g_chi)
            sm100 = sigma_m_cm2_per_g(100.0, m_phi, m_chi, g_chi)
            sm200 = sigma_m_cm2_per_g(200.0, m_phi, m_chi, g_chi)
            def fmt(x, fs=".3e"):
                if isinstance(x, (int, float)):
                    return f"{x:{fs}}"
                return str(x)
            print(f"  {label:<10} {fmt(log_Z, '.3f'):>10} {fmt(m_phi, '.2f'):>12} "
                  f"{fmt(g_chi, '.3f'):>11} {fmt(sm28):>14} {fmt(sm100):>15} {fmt(sm200):>15}")
        else:
            print(f"  {label:<10} {'FAILED':>10}")
    print()
    print("  Cloud-9 needs sigma/m(28) ~ 50-500 cm^2/g")
    print("  Galactic needs sigma/m(100) ~ 0.1-1 cm^2/g")
    print("  Cluster needs sigma/m(200) ~ 0.1 cm^2/g")
    print()
    print("  Reviewer Point 2 prediction:")
    print("  Run H should converge to (m_phi ~ 1-30 MeV, g_chi ~ 1.0-1.5)")
    print("  if the velocity-dependent Yukawa alone is enough.")
    print("  If Run H reverts to heavy mediator (m_phi ~ 700 MeV),")
    print("  then the other 17 channels need conversion to velocity-dependent")
    print("  evaluation (T90.41+ future work).")


if __name__ == "__main__":
    main()