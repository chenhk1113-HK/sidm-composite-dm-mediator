#!/usr/bin/env python
"""
T90.30 — T41 re-run with the T90.29 v3 Yukawa Cloud-9 channel.

Per the T90.29 doc, the v0.7 master MAP at (m_phi=750 MeV, m_chi=500 GeV,
g_chi=0.1) is in the heavy-mediator regime, where the Yukawa σ/m at
v=28 km/s is 1.4e-6 cm²/g (8 orders of magnitude below Cloud-9's
σ/m ~ 483). To move the master posterior into the Cloud-9-favorable
regime (m_phi = 1-10 MeV), we need to:

1. Turn on the T90.29 v3 channel (T90_RELHIC_V27=1).
2. Allow m_phi in the light-mediator regime. The existing
   LOG_M_PHI_MEV_RANGE = (-1, 4) covers [10 keV, 10 TeV], which
   INCLUDES m_phi = 1-10 MeV. So the prior is already wide enough.
3. Address the KSFR/PCAC validity mask. The v0.5 sub-project found
   that the mask correctly rejects m_phi < f_pi (418 MeV) under the
   composite-DM interpretation. But Cloud-9 uses a fundamental
   Yukawa mediator (not composite), so the mask is over-restrictive
   for Cloud-9-favorable m_phi. The mask can be disabled via
   SIDM_DISABLE_KSFR_MASK=1.

This driver runs T41 three times:
  Run A: Baseline (no T90.29 channel, KSFR mask ON)
  Run B: T90.29 channel ON, KSFR mask ON (default)
  Run C: T90.29 channel ON, KSFR mask OFF (allow m_phi < f_pi)

The comparison shows whether the T90.29 v3 channel moves the
posterior toward the Cloud-9-favorable regime.

Wall-time: each T41 run with nlive=200, dlogz=0.1 takes ~5-10 min.
The T90.29 v3 channel adds negligible per-evaluation cost (a
few function calls).

Honest caveats:
  - The T90.30 runs use nlive=200 (the project default). The
    published T41 v0.7 baseline uses nlive=500-2000. The T90.30
    posteriors will be noisier than the published v0.7, but
    sufficient to demonstrate the trend.
  - The KSFR/PCAC mask is a real physics constraint under the
    composite-DM interpretation. Disabling it for the T90.30
    demo is a "what-if" experiment, not a permanent change.
  - Run C's posterior is conditional on "the mediator is
    fundamental Yukawa, not composite" — which is a model
    assumption, not a free choice.
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


def run_t41(label: str, env_overrides: dict, output_suffix: str) -> dict:
    """Run T41 with the given env overrides, save output, return parsed JSON."""
    env = os.environ.copy()
    env["T41_NLIVE"] = "200"  # Project default; faster than nlive=500
    env["PYTHONUNBUFFERED"] = "1"
    env.update(env_overrides)

    output_path = RESULTS_DIR / f"t41_mediator_mass_joint_fit_T9030_{output_suffix}.json"
    print(f"\n{'='*80}")
    print(f"  T90.30 RUN: {label}")
    print(f"  Env overrides: {env_overrides}")
    print(f"  Output: {output_path.name}")
    print(f"{'='*80}\n")

    # The T41 main() writes to a fixed filename (t41_mediator_mass_joint_fit.json).
    # To avoid clobbering the existing file, we need to either:
    #   (a) Pass an env var to T41 to override the output path.
    #   (b) Back up the existing file and restore it.
    # T41 doesn't have an env var for output path, so use (b).
    default_output = RESULTS_DIR / "t41_mediator_mass_joint_fit.json"
    backup_path = RESULTS_DIR / f"t41_mediator_mass_joint_fit_BACKUP_{output_suffix}.json"
    if default_output.exists():
        import shutil
        shutil.copy2(default_output, backup_path)

    t0 = time.time()
    try:
        result = subprocess.run(
            [str(VENV_PYTHON), str(T41_SCRIPT)],
            env=env, capture_output=True, text=True,
            timeout=900,  # 15 min max
        )
        wall = time.time() - t0

        print(f"\n  --- T41 stdout (last 60 lines) ---")
        for line in result.stdout.splitlines()[-60:]:
            print(f"  {line}")

        if result.returncode != 0:
            print(f"\n  --- T41 stderr ---")
            for line in result.stderr.splitlines()[-30:]:
                print(f"  {line}")
            print(f"\n  T41 FAILED with return code {result.returncode}, wall={wall:.1f}s")
            return {"label": label, "status": "FAILED", "stderr_tail": result.stderr[-1000:],
                    "stdout_tail": result.stdout[-1000:]}

        # Load the output JSON
        with open(default_output) as f:
            data = json.load(f)
        data["t9030_label"] = label
        data["t9030_env_overrides"] = env_overrides
        data["t9030_wall_seconds"] = wall
        # Save with our suffix
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2, default=str)
        # Clean up backup (we've saved the labeled copy)
        if backup_path.exists():
            backup_path.unlink()
        return data

    except subprocess.TimeoutExpired:
        wall = time.time() - t0
        print(f"\n  T41 TIMED OUT after {wall:.1f}s (15 min limit)")
        return {"label": label, "status": "TIMEOUT", "wall_seconds": wall}
    finally:
        # Always restore the original default file from backup
        if backup_path.exists():
            import shutil
            shutil.copy2(backup_path, default_output)
            backup_path.unlink()


def main():
    print("=" * 80)
    print("  T90.30 — T41 re-run with T90.29 v3 Yukawa Cloud-9 channel")
    print("  Three runs to demonstrate the T90.29 fix's effect on the master posterior:")
    print("    Run A: baseline (no T90.29, KSFR mask ON)")
    print("    Run B: T90.29 ON, KSFR mask ON (default)")
    print("    Run C: T90.29 ON, KSFR mask OFF (allow m_phi < f_pi)")
    print("=" * 80)

    # Run A: Baseline
    result_A = run_t41(
        "A: baseline (no T90.29, KSFR ON)",
        env_overrides={},
        output_suffix="A_baseline",
    )

    # Run B: T90.29 ON, KSFR mask ON
    result_B = run_t41(
        "B: T90.29 ON, KSFR mask ON (default)",
        env_overrides={"T90_RELHIC_V27": "1"},
        output_suffix="B_t90v29_ksfr_on",
    )

    # Run C: T90.29 ON, KSFR mask OFF
    result_C = run_t41(
        "C: T90.29 ON, KSFR mask OFF (allow light mediator)",
        env_overrides={
            "T90_RELHIC_V27": "1",
            "SIDM_DISABLE_KSFR_MASK": "1",
        },
        output_suffix="C_t90v29_ksfr_off",
    )

    # Summary
    print("\n" + "=" * 80)
    print("  T90.30 SUMMARY")
    print("=" * 80)
    print()
    print(f"  {'Run':<10} {'log Z':>10} {'m_phi (MeV)':>15} {'m_chi (GeV)':>15} {'g_chi':>10} "
          f"{'σ_m_0':>10} {'Cloud-9 σ/m(28)':>15}")
    print(f"  {'-'*10} {'-'*10} {'-'*15} {'-'*15} {'-'*10} {'-'*10} {'-'*15}")
    for label, result in [("A", result_A), ("B", result_B), ("C", result_C)]:
        if result.get("status") not in (None, "FAILED", "TIMEOUT"):
            map_phys = result.get("MAP_physical", {})
            log_Z = result.get("log_Z", "—")
            m_phi = map_phys.get("m_phi_MeV", "—")
            m_chi = map_phys.get("m_chi_GeV", "—")
            g_chi = map_phys.get("g_chi", "—")
            sigma_m_0 = map_phys.get("sigma_m_0_derived", "—")
            # Compute Cloud-9 σ/m at v=28 km/s for this MAP
            try:
                from t40_yukawa_sigma_m import sigma_m_cm2_per_g
                sm_cloud9 = sigma_m_cm2_per_g(28.0, m_phi, m_chi, g_chi)
            except Exception:
                sm_cloud9 = "—"
            # Format
            def fmt(x, fmt_str=".3e"):
                if isinstance(x, (int, float)):
                    return f"{x:{fmt_str}}"
                return str(x)
            print(f"  {label:<10} {fmt(log_Z, '.3f'):>10} {fmt(m_phi, '.2f'):>15} "
                  f"{fmt(m_chi, '.2f'):>15} {fmt(g_chi, '.3f'):>10} "
                  f"{fmt(sigma_m_0, '.3e'):>10} {fmt(sm_cloud9, '.3e'):>15}")
        else:
            print(f"  {label:<10} {'FAILED':>10}")
    print()
    print("  Interpretation:")
    print("    Cloud-9 requires σ/m(28) ~ 50-500 cm²/g.")
    print("    A: baseline (heavy mediator) gives σ/m(28) << 50 — off-grid for Cloud-9.")
    print("    B: T90.29 ON, KSFR ON: KSFR mask rejects m_phi < f_pi=418 MeV,")
    print("       so MAP stays in heavy-mediator regime. Same as A.")
    print("    C: T90.29 ON, KSFR OFF: mask disabled, MCMC can explore m_phi < f_pi.")
    print("       If MAP moves to m_phi ~ 1-10 MeV, the Yukawa form gives")
    print("       σ/m(28) ~ 50-500 cm²/g = Cloud-9 compatible.")


if __name__ == "__main__":
    main()
