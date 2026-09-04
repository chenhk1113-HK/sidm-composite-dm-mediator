"""
T88.A — XRISM Perseus Channel 20 4-config ablation (sequential foreground).

Per joint-fit-channel-onboarding skill P5, the canonical 4-config ablation
matrix is:
  | Config      | T73_DAMPE_DISABLE | T74_LSS_DISABLE | T88_XRISM_DISABLE | Purpose                                |
  |-------------|-------------------|-----------------|-------------------|----------------------------------------|
  | none        | 1                 | 1               | 1                 | Baseline (no v0.7 channels + no XRISM) |
  | xrism_only  | 1                 | 1               | 0                 | Isolate XRISM contribution alone       |
  | dampe_lss   | 0                 | 0               | 1                 | v0.7 channels WITHOUT XRISM            |
  | all         | 0                 | 0               | 0                 | v0.7 channels WITH XRISM (the ship)    |

Per skill P12, dynesty 4-config ablation must run SEQUENTIALLY foreground
(dynesty processes fight for __pycache__ if parallel).

nlive is configurable via env var T88A_NLIVE (default 500 for the ablation;
override to 2000 for the headline ship).

Output: data/results/t88a_ablation_<date>.json with all 4 log_Z values,
the deltas, and the interpretation string.
"""
from __future__ import annotations
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Resolve project paths
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
CODE_DIR = PROJECT_ROOT / "code"
RESULTS_DIR = PROJECT_ROOT / "data" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


# 4-config ablation matrix
ABLATION_CONFIGS = [
    # (name, T73_DAMPE, T74_LSS, T88_XRISM, T41_RESULT_SUFFIX)
    ("none",       "1", "1", "1", "_t88a_none"),
    ("xrism_only", "1", "1", "0", "_t88a_xrism_only"),
    ("dampe_lss",  "0", "0", "1", "_t88a_dampe_lss"),
    ("all",        "0", "0", "0", "_t88a_all"),
]

# nlive for the ablation (override via T88A_NLIVE for the headline ship)
NLIVE = int(os.environ.get("T88A_NLIVE", "500"))


def run_one_config(name: str, t73: str, t74: str, t88: str, suffix: str) -> dict:
    """Run T41 once with the given env-var ablation matrix."""
    env = os.environ.copy()
    env["T73_DAMPE_DISABLE"] = t73
    env["T74_LSS_DISABLE"] = t74
    env["T88_XRISM_DISABLE"] = t88
    env["T41_RESULT_SUFFIX"] = suffix
    env["T41_NLIVE"] = str(NLIVE)
    # KSFR mask is left at its default

    out_path = RESULTS_DIR / f"t41_mediator_mass_joint_fit{suffix}.json"
    print(f"\n{'=' * 60}")
    print(f"  Config: {name}  (T73={t73}, T74={t74}, T88={t88}, nlive={NLIVE})")
    print(f"  Output: {out_path}")
    print(f"{'=' * 60}")

    t0 = time.time()
    proc = subprocess.run(
        [sys.executable, str(CODE_DIR / "t41_mediator_mass_joint_fit.py")],
        env=env,
        cwd=str(CODE_DIR),
        capture_output=True,
        text=True,
        timeout=1800,  # 30 min hard cap per config
    )
    wall = time.time() - t0

    print(f"  exit code: {proc.returncode}")
    print(f"  wall: {wall:.1f}s")
    if proc.returncode != 0:
        print(f"  STDERR (last 30 lines):")
        for line in proc.stderr.strip().splitlines()[-30:]:
            print(f"    {line}")
        return {
            "config": name,
            "exit_code": proc.returncode,
            "wall_seconds": wall,
            "ok": False,
        }

    # Read result JSON
    if not out_path.exists():
        print(f"  WARNING: expected output {out_path} not found")
        return {
            "config": name,
            "exit_code": proc.returncode,
            "wall_seconds": wall,
            "ok": False,
            "error": "output_missing",
        }

    result = json.loads(out_path.read_text())
    log_z = result.get("log_Z")
    log_z_err = result.get("log_Z_err")
    config_hash = result.get("t41_version", {}).get("config_hash")
    print(f"  log Z = {log_z:.4f} +/- {log_z_err:.4f}, hash={config_hash}")
    return {
        "config": name,
        "ok": True,
        "log_Z": log_z,
        "log_Z_err": log_z_err,
        "config_hash": config_hash,
        "wall_seconds": wall,
        "out_path": str(out_path),
        "interpretation": result.get("interpretation", "")[:500],
    }


def main() -> int:
    print("=" * 60)
    print(f"  T88.A 4-config ablation (nlive={NLIVE})")
    print("=" * 60)
    print(f"  Started: {datetime.now().isoformat(timespec='seconds')}")

    runs = []
    for name, t73, t74, t88, suffix in ABLATION_CONFIGS:
        result = run_one_config(name, t73, t74, t88, suffix)
        runs.append(result)
        if not result["ok"]:
            print(f"\n  FATAL: config {name} failed. Aborting.")
            return 1

    # Compute deltas (XRISM contribution = log_Z with XRISM - log_Z without XRISM
    # at matched v0.7 channels; baseline = log_Z without XRISM, v0.7 channels)
    by_name = {r["config"]: r for r in runs}

    # XRISM contribution at v0.7 channels (with DAMPE + LSS):
    if "dampe_lss" in by_name and "all" in by_name:
        xrism_delta_v07 = by_name["all"]["log_Z"] - by_name["dampe_lss"]["log_Z"]
    else:
        xrism_delta_v07 = None
    # XRISM contribution at baseline (no v0.7 channels):
    if "none" in by_name and "xrism_only" in by_name:
        xrism_delta_none = by_name["xrism_only"]["log_Z"] - by_name["none"]["log_Z"]
    else:
        xrism_delta_none = None

    summary = {
        "t88_round": "T88.A",
        "channel": "XRISM Perseus ICM (Channel 20)",
        "date": datetime.now().isoformat(timespec="seconds"),
        "nlive": NLIVE,
        "runs": runs,
        "delta_log_Z_xrism_at_v07_channels": xrism_delta_v07,
        "delta_log_Z_xrism_at_baseline": xrism_delta_none,
        "verdict": (
            "XRISM Channel 20 is silent at the v0.7 posterior (consistency "
            "plateau); deltas should be ~0 if (a) v0.7 channels are in their "
            "consistency range and (b) XRISM sits in its plateau. Large "
            "negative deltas would indicate a tension discovered."
        ),
    }

    # Print summary
    print("\n" + "=" * 60)
    print("  T88.A 4-config ablation SUMMARY")
    print("=" * 60)
    for r in runs:
        if r["ok"]:
            print(f"  {r['config']:<12s}: log Z = {r['log_Z']:+.4f} +/- {r['log_Z_err']:.4f}  "
                  f"({r['wall_seconds']:.1f}s, hash={r['config_hash']})")
        else:
            print(f"  {r['config']:<12s}: FAILED (exit={r.get('exit_code')})")
    print(f"\n  Delta log Z (XRISM contribution at v0.7 channels): {xrism_delta_v07:+.4f}")
    print(f"  Delta log Z (XRISM contribution at baseline):     {xrism_delta_none:+.4f}")
    print(f"\n  Verdict: {summary['verdict']}")

    # Write summary JSON
    summary_path = RESULTS_DIR / f"t88a_ablation_{datetime.now().strftime('%Y%m%d')}.json"
    summary_path.write_text(json.dumps(summary, indent=2, default=str))
    print(f"\n  Summary written to: {summary_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
