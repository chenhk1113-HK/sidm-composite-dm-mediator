#!/usr/bin/env python
"""
T90.42 (revised) — Leave-one-out (LOO) profiling to identify the dominant
non-SIDM blocker against g_chi ~ 1.5.

Per T90.41 negative result, the master posterior is dominated by non-SIDM
channels (CMB, FERMI, DAMPE, LSS, LZ magnetic-moment). The vdep SIDM
refactor alone doesn't move g_chi to 1.5.

T90.42 profiles by removing one non-SIDM constraint at a time and
measuring how MAP g_chi changes. The channel whose removal most
increases g_chi is the dominant blocker.

Configuration (same as T90.41):
- T90_RELHIC_V27=1 (Cloud-9)
- T90_RELHIC_POP=1 (Monaci+ 2026 population)
- T90_YANG_CLOUD9=1 (Yang+ 2024)
- T90_YUKAWA_TUNED=1 (tuned Yukawa)
- T90_ANAND_MSTAR=1 (Anand+ 2025)
- SIDM_DISABLE_KSFR_MASK=1 (allow light mediator)
- T41_VDEP_CHANNELS=1 (vdep dSph/UFD/Bullet)
- T41_NLIVE=200

Channel removal via env vars:
- T41_LEAVE_OUT_LZ=1: skip ll_lz
- T41_LEAVE_OUT_FERMI=1: skip ll_fermi
- T41_LEAVE_OUT_CMB=1: skip ll_cmb
- T41_LEAVE_OUT_DAMPE=1: skip ll_dampe
- T41_LEAVE_OUT_LSS=1: skip ll_lss
- T41_LEAVE_OUT_LZ_MAGNETIC=1: skip ll_magnetic_moment

LOO config matrix:
  baseline (no leave-out)         -> reference
  L_LZ: remove LZ direct detection
  L_FERMI: remove FERMI dwarf
  L_CMB: remove CMB DeltaN_eff
  L_DAMPE: remove DAMPE CRE
  L_LSS: remove LSS assembly bias
  L_LZ_MAGNETIC: remove LZ magnetic moment

The dominant blocker is the channel whose removal most increases MAP g_chi.
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


def run_t41_loo(label, env_overrides, output_suffix):
    """Run T41 with given env, save output, return parsed JSON."""
    env = os.environ.copy()
    env["T41_NLIVE"] = "200"
    env["PYTHONUNBUFFERED"] = "1"
    # Always enable T90 channels + KSFR off + vdep
    env.update({
        "T90_RELHIC_V27": "1",
        "T90_RELHIC_POP": "1",
        "T90_YANG_CLOUD9": "1",
        "T90_YUKAWA_TUNED": "1",
        "T90_ANAND_MSTAR": "1",
        "SIDM_DISABLE_KSFR_MASK": "1",
        "T41_VDEP_CHANNELS": "1",
    })
    env.update(env_overrides)

    output_path = RESULTS_DIR / f"t41_mediator_mass_joint_fit_T9042_{output_suffix}.json"
    print(f"\n{'='*80}")
    print(f"  T90.42 LOO: {label}")
    print(f"  Env overrides: {env_overrides}")
    print(f"{'='*80}\n")

    default_output = RESULTS_DIR / "t41_mediator_mass_joint_fit.json"
    backup_path = RESULTS_DIR / f"t41_mediator_mass_joint_fit_BACKUP_T9042_{output_suffix}.json"
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

        if result.returncode != 0:
            print(f"\n  T41 FAILED: {result.stderr[-500:]}")
            if backup_path.exists():
                shutil.copy2(backup_path, default_output)
                backup_path.unlink()
            return {"label": label, "status": "FAILED"}

        with open(default_output) as f:
            data = json.load(f)
        data["t9042_label"] = label
        data["t9042_env"] = env_overrides
        data["t9042_wall_seconds"] = wall
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2, default=str)
        if backup_path.exists():
            shutil.copy2(backup_path, default_output)
            backup_path.unlink()
        return data
    except subprocess.TimeoutExpired:
        wall = time.time() - t0
        if backup_path.exists():
            import shutil
            shutil.copy2(backup_path, default_output)
            backup_path.unlink()
        return {"label": label, "status": "TIMEOUT", "wall_seconds": wall}


def main():
    print("=" * 80)
    print("  T90.42 (revised) — Leave-one-out profiling")
    print("=" * 80)
    print()
    print("  Goal: identify which non-SIDM channel is the dominant blocker")
    print("  against g_chi ~ 1.5 (reviewer's unified-model prediction).")
    print()
    print("  6 LOO configurations + 1 baseline = 7 runs (~25 min total)")
    print()

    loo_configs = [
        ("baseline", {}, "baseline"),
        ("L_LZ (no LZ direct)", {"T41_LEAVE_OUT_LZ": "1"}, "no_lz"),
        ("L_FERMI (no FERMI dwarf)", {"T41_LEAVE_OUT_FERMI": "1"}, "no_fermi"),
        ("L_CMB (no CMB dN_eff)", {"T41_LEAVE_OUT_CMB": "1"}, "no_cmb"),
        ("L_DAMPE (no DAMPE CRE)", {"T41_LEAVE_OUT_DAMPE": "1"}, "no_dampe"),
        ("L_LSS (no LSS assembly)", {"T41_LEAVE_OUT_LSS": "1"}, "no_lss"),
        ("L_LZ_MAGNETIC (no LZ mm)", {"T41_LEAVE_OUT_LZ_MAGNETIC": "1"}, "no_lz_mag"),
    ]

    results = {}
    for label, env, suffix in loo_configs:
        results[suffix] = run_t41_loo(label, env, suffix)

    # Summary
    sys.path.insert(0, str(PROJECT_ROOT / "v0.3-prelim" / "code"))
    from t40_yukawa_sigma_m import sigma_m_cm2_per_g
    print("\n" + "=" * 80)
    print("  T90.42 LOO SUMMARY")
    print("=" * 80)
    print()
    print(f"  {'Config':<25} {'log Z':>10} {'MAP m_phi':>10} {'MAP g_chi':>10} "
          f"{'MAP σ/m(28)':>14} {'Med m_phi':>10} {'Med g_chi':>10}")
    print(f"  {'-'*25} {'-'*10} {'-'*10} {'-'*10} {'-'*14} {'-'*10} {'-'*10}")
    for cfg, data in results.items():
        if data.get("status") in (None,):
            mp = data.get("MAP_physical", {})
            med = data.get("median", {})
            log_Z = data.get("log_Z", "—")
            m_phi = mp.get("m_phi_MeV", 0)
            m_chi = mp.get("m_chi_GeV", 0)
            g_chi = mp.get("g_chi", 0)
            sm28 = sigma_m_cm2_per_g(28.0, m_phi, m_chi, g_chi)
            med_m_phi = 10 ** med.get("log_m_phi_MeV", 0) if med else 0
            med_g_chi = med.get("g_chi", 0) if med else 0
            def fmt(x, fs=".2f"):
                if isinstance(x, (int, float)):
                    return f"{x:{fs}}"
                return str(x)
            print(f"  {cfg:<25} {fmt(log_Z, '.3f'):>10} {fmt(m_phi):>10} "
                  f"{fmt(g_chi, '.3f'):>10} {fmt(sm28, '.3e'):>14} "
                  f"{fmt(med_m_phi):>10} {fmt(med_g_chi, '.3f'):>10}")
        else:
            print(f"  {cfg:<25} {'FAILED':>10}")
    print()
    print("  Cloud-9 needs sigma/m(28) ~ 50-500 cm^2/g")
    print("  Reviewer predicts g_chi ~ 1.0-1.5 for unified model")
    print()
    print("  Dominant blocker = config with HIGHEST MAP g_chi")
    print("  (the channel whose removal most relaxes g_chi)")


if __name__ == "__main__":
    main()