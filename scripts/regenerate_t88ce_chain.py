#!/usr/bin/env python3
"""Regenerate the whole T88.CE standing-fit chain under the corrected Born transfer factor.

Why this exists (2026-11-11): scripts/t88ce_postprocess.py assembles the standing headline from
three upstream artifacts, and the flow that produced them was only half-documented — the ablation
driver v0.3-prelim/code/t88b_erosita_ablation.py still exists, but the step that copied its fit
outputs to the canonical artifact names was manual. This script makes the whole chain reproducible.

Configuration identity comes from scripts/t88ce_postprocess.py's own comments and from the channel
gates in v0.3-prelim/code/t41_mediator_mass_joint_fit.py (all default ON; ablation via env var):

  role      artifact                                   channels ON
  v0.7      ..._v0_7_with_dampe_lss_nlive2000.json     DAMPE + LSS only (XRISM/EROSITA/T88.D/C/E OFF)
  t88b      ..._t88b_v07_with_erosita_nlive2000.json   DAMPE + LSS + XRISM + EROSITA
  control   ..._t88ce_sampling_variance_control.json   DAMPE + LSS + XRISM + EROSITA + T88.D + T88.C (T88.E OFF)
  headline  ..._t88ce_v08_..._nlive2000.json           all five ON (the script defaults)

nlive = 2000 to match every existing artifact name.

Honesty guard: a re-run is only comparable to the artifact it replaces if the model is the same.
Channel sets evolve, so each role prints the OLD log Z next to the NEW one. A large delta means the
current code's channel set no longer equals the historical configuration, and the chain should be
read as a new measurement rather than a refresh. Nothing here assumes they match.

Each fit writes v0.3-prelim/data/results/t41_mediator_mass_joint_fit.json, which is copied to the
role's canonical name. Every artifact being replaced is copied first to the scratch backup dir and
its sha256 recorded in the chain report.

Usage:
  python scripts/regenerate_t88ce_chain.py            # full chain, nlive=2000 (~4 x 26 min)
  python scripts/regenerate_t88ce_chain.py --nlive 200   # smoke test of the mechanism first
  python scripts/regenerate_t88ce_chain.py --roles v0.7,t88b
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RESULTS = REPO / "v0.3-prelim" / "data" / "results"
FIT = REPO / "v0.3-prelim" / "code" / "t41_mediator_mass_joint_fit.py"
FIT_OUT = RESULTS / "t41_mediator_mass_joint_fit.json"
BACKUP = REPO / "v0.3-prelim" / "data" / "results" / "_chain_backup_20261111"

GATES = {
    "T88_XRISM_DISABLE": "xrism",
    "T88B_EROSITA_DISABLE": "erosita",
    "T88D_PHI_DECAY_DISABLE": "t88d_phi_decay",
    "T88C_EUCLID_LENSING_DISABLE": "t88c_euclid_lensing",
    "T88E_EUCLID_SUBHALO_DISABLE": "t88e_euclid_subhalo",
}

# role -> (canonical artifact filename, env gates that are DISABLED)
ROLES = {
    "v0.7": (
        "t41_mediator_mass_joint_fit_v0_7_with_dampe_lss_nlive2000.json",
        ["T88_XRISM_DISABLE", "T88B_EROSITA_DISABLE", "T88D_PHI_DECAY_DISABLE",
         "T88C_EUCLID_LENSING_DISABLE", "T88E_EUCLID_SUBHALO_DISABLE"],
    ),
    "t88b": (
        "t41_mediator_mass_joint_fit_t88b_v07_with_erosita_nlive2000.json",
        ["T88D_PHI_DECAY_DISABLE", "T88C_EUCLID_LENSING_DISABLE", "T88E_EUCLID_SUBHALO_DISABLE"],
    ),
    "control": (
        "t41_mediator_mass_joint_fit_t88ce_sampling_variance_control.json",
        ["T88E_EUCLID_SUBHALO_DISABLE"],
    ),
    "headline": (
        "t41_mediator_mass_joint_fit_t88ce_v08_with_euclid_lensing_and_subhalo_forecast_nlive2000.json",
        [],
    ),
}


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16] if p.exists() else "MISSING"


def summarize(p: Path) -> dict:
    if not p.exists():
        return {}
    d = json.loads(p.read_text(encoding="utf-8"))
    m = d.get("MAP_physical") or {}
    return {
        "log_Z": d.get("log_Z"),
        "log_Z_err": d.get("log_Z_err"),
        "a_derived": m.get("a_derived"),
        "sigma_m_0_derived": m.get("sigma_m_0_derived"),
        "m_phi_MeV": m.get("m_phi_MeV"),
        "m_chi_GeV": m.get("m_chi_GeV"),
        "g_chi": m.get("g_chi"),
        "seed": d.get("seed"),
    }


def fmt(s: dict) -> str:
    if not s:
        return "no artifact"
    return (f"logZ {s.get('log_Z') if s.get('log_Z') is None else round(s['log_Z'], 3)}"
            f"+/-{s.get('log_Z_err') if s.get('log_Z_err') is None else round(s['log_Z_err'], 3)}"
            f" a {s.get('a_derived') if s.get('a_derived') is None else round(s['a_derived'], 4)}"
            f" sm0 {s.get('sigma_m_0_derived') if s.get('sigma_m_0_derived') is None else round(s['sigma_m_0_derived'], 4)}"
            f" mphi {s.get('m_phi_MeV') if s.get('m_phi_MeV') is None else round(s['m_phi_MeV'], 1)}"
            f" mchi {s.get('m_chi_GeV') if s.get('m_chi_GeV') is None else round(s['m_chi_GeV'], 1)}"
            f" g {s.get('g_chi') if s.get('g_chi') is None else round(s['g_chi'], 3)}")


def run_fit(role: str, nlive: int, log_path: Path) -> int:
    env = dict(os.environ)
    for gate in ROLES[role][1]:
        env[gate] = "1"
    for gate in GATES:
        if gate not in ROLES[role][1]:
            env.pop(gate, None)  # fall through to the script's default (ON)
    env["T41_NLIVE"] = str(nlive)
    # Record which channels were active, so the artifact is interpretable without reading this script.
    env["T41_CHAIN_ROLE"] = role
    print(f"  [{role}] disabled: {', '.join(ROLES[role][1]) or '(none — all channels ON)'}")
    with open(log_path, "a", encoding="utf-8") as log:
        return subprocess.call([sys.executable, "-u", str(FIT)], env=env, cwd=str(REPO),
                               stdout=log, stderr=subprocess.STDOUT)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--nlive", type=int, default=2000)
    ap.add_argument("--roles", default="v0.7,t88b,control,headline")
    ap.add_argument("--skip-postprocess", action="store_true")
    ap.add_argument("--staging", action="store_true",
                    help="write artifacts to the backup/staging dir instead of replacing the real ones "
                         "(use with a small --nlive to validate the mechanism without touching the record)")
    args = ap.parse_args()
    roles = [r.strip() for r in args.roles.split(",") if r.strip()]
    for r in roles:
        if r not in ROLES:
            raise SystemExit(f"unknown role {r!r}; choose from {', '.join(ROLES)}")

    BACKUP.mkdir(parents=True, exist_ok=True)
    if args.staging:
        (BACKUP / "staging").mkdir(parents=True, exist_ok=True)
        print("STAGING MODE: artifacts will NOT replace the record")
    log_path = BACKUP / f"chain_{time.strftime('%Y%m%d_%H%M%S')}.log"
    report = {"nlive": args.nlive, "chain_started": time.strftime("%Y-%m-%dT%H:%M:%S"),
              "python": sys.executable, "roles": {}}

    print(f"chain regeneration: roles={roles} nlive={args.nlive}")
    print(f"logs/backups -> {BACKUP}")

    for role in roles:
        fname, _ = ROLES[role]
        target = (BACKUP / "staging" / fname) if args.staging else (RESULTS / fname)
        # 1. back up what we are about to replace (staging mode never touches the real artifacts)
        if not args.staging and target.exists():
            shutil.copy2(target, BACKUP / target.name)
        old = summarize(RESULTS / fname)  # always compare against the historical artifact
        print(f"\n=== role {role} -> {fname}")
        print(f"  OLD: {fmt(old)}   sha {sha256(RESULTS / fname)}")
        # 2. run the fit with this role's channel gates
        t0 = time.time()
        rc = run_fit(role, args.nlive, log_path)
        wall = round(time.time() - t0, 1)
        if rc != 0 or not FIT_OUT.exists():
            print(f"  FIT FAILED rc={rc}; chain aborted, no artifact replaced.")
            return 1
        # 3. copy the fit output to the canonical name
        new = summarize(FIT_OUT)
        shutil.copy2(FIT_OUT, target)
        print(f"  NEW: {fmt(new)}   wall {wall}s   rc={rc}")
        dl = None
        if old.get("log_Z") is not None and new.get("log_Z") is not None:
            dl = round(new["log_Z"] - old["log_Z"], 3)
            print(f"  log Z delta vs historical artifact: {dl:+.3f}"
                  + ("  (large -> the current channel set is NOT the historical configuration;"
                     " read this as a new measurement, not a refresh)" if abs(dl) > 2.0 else ""))
        report["roles"][role] = {"artifact": fname, "old": old, "new": new,
                                 "old_sha256_16": sha256(BACKUP / target.name) if (BACKUP / target.name).exists() else "MISSING",
                                 "new_sha256_16": sha256(target), "wall_s": wall, "log_Z_delta": dl}

    if not args.skip_postprocess:
        for script in ("t88ce_postprocess.py", "canonical_numbers.py"):
            p = REPO / "scripts" / script
            rc = subprocess.call([sys.executable, "-u", str(p)], cwd=str(REPO),
                                 stdout=open(log_path, "a"), stderr=subprocess.STDOUT)
            print(f"  {script}: rc={rc}")
            report.setdefault("postprocess", {})[script] = rc

    out = BACKUP / f"chain_report_{time.strftime('%Y%m%d_%H%M%S')}.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nchain report: {out}")
    print("next: python scripts/audit_claims.py && python scripts/drift_guard.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
