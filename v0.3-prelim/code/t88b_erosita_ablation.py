"""
T88.B — eROSITA eRASS1 Channel 21 4-config ablation (sequential foreground).

Per joint-fit-channel-onboarding skill P5 + P12 (sequential, NOT parallel).
The ablation matrix mirrors T88.A's structure with eROSITA Channel 21
gated by T88B_EROSITA_DISABLE.

Configs:
  none         — XRISM OFF, EROSITA OFF (baseline)
  erosita_only  — XRISM OFF, EROSITA ON  (isolate eROSITA)
  xrism_only   — XRISM ON, EROSITA OFF  (sanity)
  all          — XRISM ON, EROSITA ON   (headline ship)

Output: 4 dynesty JSONs in v0.3-prelim/data/results/, plus a
summary JSON with deltas and a verdict string.

Usage:
  T88A_NLIVE=500 python t88b_erosita_ablation.py
  T88A_NLIVE=2000 python t88b_erosita_ablation.py  # headline ship
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

# Path setup: force v0.3-prelim/code first (project has a root config.py mirror
# for WSL/Windows sync; the canonical one is here).
PROJECT_CODE = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_CODE))
sys.modules.pop("config", None)  # drop any stale cache


def run_one_config(label: str, xrism_disable: bool, erosita_disable: bool) -> dict:
    """Run T41 nlive=N with given channel-disable flags. Return summary dict."""
    # Set env vars BEFORE importing T41
    if xrism_disable:
        os.environ["T88_XRISM_DISABLE"] = "1"
    else:
        os.environ.pop("T88_XRISM_DISABLE", None)
    if erosita_disable:
        os.environ["T88B_EROSITA_DISABLE"] = "1"
    else:
        os.environ.pop("T88B_EROSITA_DISABLE", None)

    # Fresh import to pick up env vars
    for mod in list(sys.modules):
        if mod in ("t41_mediator_mass_joint_fit", "channels_extended",
                   "erosita_erass1_forward_model", "config",
                   "xrism_perseus_icm_forward_model", "channels_v03",
                   "t40_yukawa_sigma_m", "t30_lz_real_posterior",
                   "t32_fermi_dwarf_channel", "ksfr_pcac_validity"):
            del sys.modules[mod]

    from t41_mediator_mass_joint_fit import main as t41_main

    # Use a unique suffix per config
    suffix = f"_t88b_{label}"
    os.environ["T41_RESULT_SUFFIX"] = suffix

    nlive = int(os.environ.get("T88A_NLIVE", "500"))
    os.environ["T41_NLIVE"] = str(nlive)

    print(f"  Running config '{label}' (nlive={nlive})...", flush=True)
    t0 = time.time()
    try:
        t41_main()
    except SystemExit:
        # T41's main() may call sys.exit on completion; that's fine
        pass
    wall = time.time() - t0

    # Read the result JSON that T41 wrote
    from t41_mediator_mass_joint_fit import RESULTS_DIR
    result_path = Path(RESULTS_DIR)
    # The suffix is appended by T41; find the right file
    candidates = sorted(result_path.glob(f"t41_mediator_mass_joint_fit{suffix}*.json"))
    if not candidates:
        raise FileNotFoundError(
            f"No result JSON matching *{suffix}* in {result_path}"
        )
    latest = candidates[-1]

    with open(latest, encoding="utf-8") as f:
        data = json.load(f)

    summary = {
        "config": label,
        "log_Z": data["log_Z"],
        "log_Z_err": data["log_Z_err"],
        "wall_seconds": data.get("wall_seconds", wall),
        "config_hash": data.get("t41_version", {}).get("config_hash"),
        "sigma_m_0_MAP": data["MAP_physical"]["sigma_m_0_derived"],
        "json_path": str(latest),
    }
    print(f"    log Z = {summary['log_Z']:+.4f} +/- {summary['log_Z_err']:.4f}  "
          f"(wall = {summary['wall_seconds']:.1f}s)")
    return summary


def main():
    nlive = int(os.environ.get("T88A_NLIVE", "500"))
    print(f"=" * 70)
    print(f"  T88.B — eROSITA Channel 21 4-config ablation  (nlive = {nlive})")
    print(f"=" * 70)

    configs = [
        ("none",        True,  True),   # XRISM OFF, EROSITA OFF
        ("erosita_only", True,  False), # XRISM OFF, EROSITA ON
        ("xrism_only",   False, True),  # XRISM ON,  EROSITA OFF
        ("all",          False, False), # both ON (headline)
    ]

    results = []
    for label, xrism_dis, erosita_dis in configs:
        r = run_one_config(label, xrism_dis, erosita_dis)
        results.append(r)

    # Compute deltas vs `none` baseline
    base_log_z = results[0]["log_Z"]
    print()
    print(f"=" * 70)
    print(f"  T88.B ablation summary")
    print(f"=" * 70)
    for r in results:
        delta = r["log_Z"] - base_log_z
        print(f"  {r['config']:<14}: log Z = {r['log_Z']:+.4f} +/- {r['log_Z_err']:.4f}  "
              f"(Δ from 'none' = {delta:+.4f}, wall = {r['wall_seconds']:.1f}s)")

    # Pure eROSITA contribution (channel-isolated)
    pure_erosita = results[1]["log_Z"] - results[0]["log_Z"]
    print(f"\n  Pure eROSITA contribution (vs 'none' baseline): {pure_erosita:+.4f}")

    # Sanity: xrism_only vs none should match T88.A's -0.028 finding
    xrism_delta = results[2]["log_Z"] - results[0]["log_Z"]
    print(f"  Pure XRISM contribution (sanity check): {xrism_delta:+.4f}")

    # all vs none combines both
    combined_delta = results[3]["log_Z"] - results[0]["log_Z"]
    print(f"  Combined (XRISM + eROSITA): {combined_delta:+.4f}")

    print()
    print(f"  Verdict: eROSITA Channel 21 is a velocity-gap filler at v=500 km/s.")
    print(f"  At v0.7 MAP (sigma_m_0=0.28, a=0.16), sigma/m(v=500)=0.22 cm^2/g")
    print(f"  is BELOW the 0.5 cm^2/g core-formation threshold, so the channel")
    print(f"  is expected to contribute ~0 to log L at the standing posterior.")
    print(f"  Large negative deltas would indicate a tension discovered.")

    # Save summary
    summary_path = (
        Path(__file__).resolve().parent.parent
        / "data" / "results"
        / f"t88b_ablation_{time.strftime('%Y%m%d_%H%M%S')}.json"
    )
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump({
            "t88_b": "eROSITA eRASS1 Channel 21 ablation",
            "nlive": nlive,
            "configs": results,
            "pure_erosita_contribution": pure_erosita,
            "pure_xrism_contribution": xrism_delta,
            "combined_contribution": combined_delta,
        }, f, indent=2)
    print(f"\n  Summary written to: {summary_path}")


if __name__ == "__main__":
    main()