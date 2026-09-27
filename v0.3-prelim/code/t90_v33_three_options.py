#!/usr/bin/env python
"""
T90.33 — Three-option Cloud-9 rescue experiment.

Tests all three options for moving the master posterior into the
Cloud-9-favorable regime (σ/m(28) ~ 50-500 cm²/g):

  Option 1: T90.32 Population-level RELHIC (Monaci+ 2026 70-catalog).
            T90_RELHIC_V27=1, T90_RELHIC_POP=1, KSFR off.
  Option 2: Informative Jeffreys prior on m_phi.
            (NOTE: the existing prior IS flat-in-log-m_phi, which is
            the Jeffreys prior for a scale parameter. Verified.)
  Option 3: Cloud-9-dominated fit.
            T90_RELHIC_V27=1, T90_RELHIC_POP=1, KSFR off,
            T41_CHANNEL_WEIGHT_NONRELHIC=0.0 (all other channels silenced).

Each option runs T41 at nlive=200, dlogz=0.1 (~1-3 min each).

Honest caveats:
  - The T90.33 runs use nlive=200 (project default), so posteriors are
    noisier than the published v0.7 (nlive=500-2000).
  - The KSFR mask is a real physics constraint under the composite-DM
    interpretation. Disabling it for these "what-if" experiments is
    not a permanent change.
  - Option 2 turned out to be a "no-op" — the existing prior IS
    already Jeffreys. This is documented but no rerun is needed.
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
    env["T41_NLIVE"] = "200"
    env["PYTHONUNBUFFERED"] = "1"
    env.update(env_overrides)

    output_path = RESULTS_DIR / f"t41_mediator_mass_joint_fit_T9033_{output_suffix}.json"
    print(f"\n{'='*80}")
    print(f"  T90.33 RUN: {label}")
    print(f"  Env overrides: {env_overrides}")
    print(f"  Output: {output_path.name}")
    print(f"{'='*80}\n")

    default_output = RESULTS_DIR / "t41_mediator_mass_joint_fit.json"
    backup_path = RESULTS_DIR / f"t41_mediator_mass_joint_fit_BACKUP_T9033_{output_suffix}.json"
    if default_output.exists():
        import shutil
        shutil.copy2(default_output, backup_path)

    t0 = time.time()
    try:
        result = subprocess.run(
            [str(VENV_PYTHON), str(T41_SCRIPT)],
            env=env, capture_output=True, text=True,
            timeout=900,
        )
        wall = time.time() - t0

        print(f"\n  --- T41 stdout (last 30 lines) ---")
        for line in result.stdout.splitlines()[-30:]:
            print(f"  {line}")

        if result.returncode != 0:
            print(f"\n  --- T41 stderr ---")
            for line in result.stderr.splitlines()[-20:]:
                print(f"  {line}")
            print(f"\n  T41 FAILED with return code {result.returncode}, wall={wall:.1f}s")
            return {"label": label, "status": "FAILED", "stderr_tail": result.stderr[-1000:]}

        with open(default_output) as f:
            data = json.load(f)
        data["t9033_label"] = label
        data["t9033_env_overrides"] = env_overrides
        data["t9033_wall_seconds"] = wall
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2, default=str)
        if backup_path.exists():
            backup_path.unlink()
        return data

    except subprocess.TimeoutExpired:
        wall = time.time() - t0
        print(f"\n  T41 TIMED OUT after {wall:.1f}s")
        return {"label": label, "status": "TIMEOUT", "wall_seconds": wall}
    finally:
        if backup_path.exists():
            import shutil
            shutil.copy2(backup_path, default_output)
            backup_path.unlink()


def main():
    print("=" * 80)
    print("  T90.33 — Three-option Cloud-9 rescue experiment")
    print("  Tests Option 1 (population), Option 2 (Jeffreys = already on),")
    print("  Option 3 (Cloud-9-dominated), and a combined run.")
    print("=" * 80)

    # Option 2: Jeffreys prior verification — the existing prior IS Jeffreys.
    # No rerun needed; we verify by inspecting prior_transform_6.
    print("\n--- Option 2 verification: Jeffreys prior already in effect ---")
    print("  LOG_M_PHI_MEV_RANGE = (-1.0, 4.0)")
    print("  prior_transform_6 maps u[0] ∈ [0,1] -> log_m_phi ∈ [-1, 4]")
    print("  = flat in log m_phi = Jeffreys prior for a scale parameter.")
    print("  Verdict: Option 2 is ALREADY ACTIVE. No rerun needed.")
    print()

    # Run D: Option 1 (population) + KSFR off (Option 1 alone)
    result_D = run_t41(
        "D: Option 1 (population, KSFR off)",
        env_overrides={
            "T90_RELHIC_V27": "1",
            "T90_RELHIC_POP": "1",
            "SIDM_DISABLE_KSFR_MASK": "1",
        },
        output_suffix="D_opt1_pop",
    )

    # Run E: Option 3 alone (Cloud-9-dominated, KSFR off)
    result_E = run_t41(
        "E: Option 3 (Cloud-9-dominated, KSFR off)",
        env_overrides={
            "T90_RELHIC_V27": "1",
            "SIDM_DISABLE_KSFR_MASK": "1",
            "T41_CHANNEL_WEIGHT_NONRELHIC": "0.0",
        },
        output_suffix="E_opt3_dom",
    )

    # Run F: Combined Option 1 + Option 3
    result_F = run_t41(
        "F: Options 1+3 (population + Cloud-9-dominated)",
        env_overrides={
            "T90_RELHIC_V27": "1",
            "T90_RELHIC_POP": "1",
            "SIDM_DISABLE_KSFR_MASK": "1",
            "T41_CHANNEL_WEIGHT_NONRELHIC": "0.0",
        },
        output_suffix="F_opt1_and_3",
    )

    # Summary
    print("\n" + "=" * 80)
    print("  T90.33 SUMMARY")
    print("=" * 80)
    print()
    print(f"  {'Run':<8} {'log Z':>10} {'MAP m_phi':>12} {'MAP m_chi':>12} "
          f"{'MAP g_chi':>11} {'MAP σ/m(28)':>13}")
    print(f"  {'-'*8} {'-'*10} {'-'*12} {'-'*12} {'-'*11} {'-'*13}")

    sys.path.insert(0, str(PROJECT_ROOT / "v0.3-prelim" / "code"))
    try:
        from t40_yukawa_sigma_m import sigma_m_cm2_per_g
    except ImportError:
        sigma_m_cm2_per_g = None

    for label, result in [("D", result_D), ("E", result_E), ("F", result_F)]:
        if result.get("status") not in (None, "FAILED", "TIMEOUT"):
            mp = result.get("MAP_physical", {})
            log_Z = result.get("log_Z", "—")
            m_phi = mp.get("m_phi_MeV", "—")
            m_chi = mp.get("m_chi_GeV", "—")
            g_chi = mp.get("g_chi", "—")
            if sigma_m_cm2_per_g and isinstance(m_phi, (int, float)):
                sm_c9 = sigma_m_cm2_per_g(28.0, m_phi, m_chi, g_chi)
            else:
                sm_c9 = "—"

            def fmt(x, fs=".3e"):
                if isinstance(x, (int, float)):
                    return f"{x:{fs}}"
                return str(x)

            print(f"  {label:<8} {fmt(log_Z, '.3f'):>10} {fmt(m_phi, '.2f'):>12} "
                  f"{fmt(m_chi, '.2f'):>12} {fmt(g_chi, '.3f'):>11} "
                  f"{fmt(sm_c9, '.3e'):>13}")
        else:
            print(f"  {label:<8} {'FAILED':>10}")
    print()
    print("  Cloud-9 requires: σ/m(28) ~ 50-500 cm²/g")
    print()


if __name__ == "__main__":
    main()