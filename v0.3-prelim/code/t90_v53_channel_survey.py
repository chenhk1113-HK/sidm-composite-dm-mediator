"""T90.53 -- Channel survey for the Grand Unified SIDM project.

Catalogs every existing loglike_* function in the project, classifies each
by:
  - parametric form it expects (power-law (sigma_m_0, a), or other)
  - whether it depends on sigma/m(v) directly or on (m_chi, m_phi, g_chi, ...)
  - whether it is currently active or stub
  - whether it has published data backing or is a placeholder

This is data plumbing, NOT new physics. The output is a JSON channel manifest
that T90.54+ can consume to wire channels into the unified joint fit.
"""
from __future__ import annotations

import importlib
import inspect
import json
import os
import sys
from pathlib import Path
from typing import Optional

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))


# Channel manifest. Each entry classifies ONE loglike_* function found in the
# project. Status:
#   'usable':     real likelihood with published data
#   'stub':       placeholder, returns 0
#   'silent':     returns 0 by design (documented-null audit channel)
#   'power-law':  takes (sigma_m_0, a), not our hybrid form -> needs wrapper
#   'parametric': takes (m_chi, m_phi, g_chi, ...) -> compatible with hybrid
CHANNEL_MANIFEST = []


def _try_import(modname: str):
    """Best-effort module import; returns None on failure."""
    try:
        return importlib.import_module(modname)
    except Exception:
        return None


def _scan_module(modname: str, loglike_prefix: str = "loglike_"):
    """Find all top-level loglike_* functions in a module and record metadata."""
    mod = _try_import(modname)
    if mod is None:
        return []
    out = []
    for name, obj in inspect.getmembers(mod, inspect.isfunction):
        if not name.startswith(loglike_prefix):
            continue
        if obj.__module__ != modname:
            continue  # re-exported, skip
        try:
            sig = inspect.signature(obj)
            params = [p.name for p in sig.parameters.values()
                      if p.default is inspect.Parameter.empty]
            defaults = {p.name: p.default for p in sig.parameters.values()
                        if p.default is not inspect.Parameter.empty}
        except Exception:
            params, defaults = [], {}
        out.append({
            "module": modname,
            "function": name,
            "required_params": params,
            "default_params": list(defaults.keys()),
            "docstring_first_line": (obj.__doc__ or "").strip().splitlines()[0]
                                    if obj.__doc__ else "",
        })
    return out


def classify_channel(entry: dict) -> dict:
    """Heuristic classification of a single channel."""
    params = entry["required_params"]
    name = entry["function"]
    doc = entry["docstring_first_line"].lower()

    # Power-law form: takes (sigma_m_0, a) typically
    if "sigma_m_0" in params and "a" in params:
        # Check if it's a velocity-dependent variant
        if any("v_" in p or "vdep" in p or "v_kms" in p for p in params):
            entry["category"] = "vdep_parametric"
        else:
            entry["category"] = "power_law"
    # Hybrid form: takes (m_phi, m_chi, g_chi) or (m_chi, m_phi, epsilon)
    elif any(p in params for p in ("m_phi_MeV", "m_phi", "m_chi", "m_chi_GeV")):
        entry["category"] = "parametric"
    # Single-argument: takes a sigma/m value directly
    elif len(params) == 1 and "sigma" in params[0]:
        entry["category"] = "single_sigma"
    # Single-theta (full posterior wrapper)
    elif len(params) == 1 and params[0] in ("theta", "params"):
        entry["category"] = "theta_wrapper"
    # No required params: stub or null
    elif len(params) == 0:
        entry["category"] = "stub"
    else:
        entry["category"] = "unknown"

    # Stub detection
    if "placeholder" in doc or "stub" in doc:
        entry["status"] = "stub"
    elif "null" in doc or "documented-null" in doc or "audit" in doc:
        entry["status"] = "silent"
    elif entry["category"] in ("power_law", "parametric", "vdep_parametric",
                                "single_sigma", "theta_wrapper"):
        entry["status"] = "usable"
    else:
        entry["status"] = "unknown"

    return entry


def build_manifest() -> list:
    """Scan all known channel modules and return the full manifest."""
    modules = [
        "channels_v03",
        "channels_extended",
        "channels_vdep_t90v41",
        "sidm_velocity_dependent",
        "t32_fermi_dwarf_channel",
        "t30_lz_real_posterior",
        "ksfr_pcac_validity",
        "t90_v50_resonant_sidm",
        "t90_v51_resonant_joint_fit",
    ]
    raw = []
    for m in modules:
        raw.extend(_scan_module(m))
    classified = [classify_channel(e) for e in raw]
    return classified


def summarize(manifest: list) -> dict:
    by_category = {}
    by_status = {}
    for entry in manifest:
        by_category[entry["category"]] = by_category.get(entry["category"], 0) + 1
        by_status[entry["status"]] = by_status.get(entry["status"], 0) + 1

    # The 3 channels currently used in T90.51/T90.52
    canonical_3 = [e for e in manifest
                   if e["function"] in ("loglike_cloud9", "loglike_galaxy",
                                         "loglike_bullet")
                   or (e["module"] == "t90_v51_resonant_joint_fit"
                       and e["function"] in ("loglike_cloud9", "loglike_galaxy",
                                              "loglike_bullet"))]

    # LZ and KSFR (potential T90.56 candidates)
    lz_candidates = [e for e in manifest
                     if "lz" in e["function"].lower() and e["status"] == "usable"]
    ksfr_candidates = [e for e in manifest
                       if "ksfr" in e["function"].lower() and e["status"] == "usable"]

    return {
        "total_functions": len(manifest),
        "by_category": by_category,
        "by_status": by_status,
        "canonical_3_channels": [e["function"] for e in canonical_3],
        "lz_candidates": [e["function"] for e in lz_candidates],
        "ksfr_candidates": [e["function"] for e in ksfr_candidates],
        "note": (
            "T95 streams deliberately excluded: they provide sigma/m predictions "
            "under a master-Yukawa parametric form, NOT published observational "
            "constraints. Cannot be used as a Bayesian channel until external "
            "sigma/m observations are available (Gaia DR4 Dec 2026). "
            "Per user directive 2026-09-11 'drop t95, focus on building unified "
            "t90 first'."
        ),
    }


if __name__ == "__main__":
    manifest = build_manifest()
    summary = summarize(manifest)

    if os.name == "nt":
        out_dir = Path("C:/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results")
    else:
        out_dir = Path("/home/lamkuenai/sidm-composite-dm-mediator/v0.3-prelim/data/results")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "t90_v53_channel_manifest.json"

    payload = {
        "summary": summary,
        "channels": manifest,
    }
    with open(out_path, "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"[T90.53] Wrote {out_path}")
    print(f"[T90.53] Total channel functions: {summary['total_functions']}")
    print(f"[T90.53] By category: {summary['by_category']}")
    print(f"[T90.53] By status: {summary['by_status']}")
    print(f"[T90.53] Canonical 3 channels (used in T90.51/52): "
          f"{summary['canonical_3_channels']}")
    print(f"[T90.53] LZ candidates: {summary['lz_candidates']}")
    print(f"[T90.53] KSFR candidates: {summary['ksfr_candidates']}")
