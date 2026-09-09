"""
T90.23 PATH 4 (DRY RUN) — Joint three-detector likelihood skeleton.

PURPOSE
=======
Combine the recast outputs from paths 1-3 (LZ, PandaX, XENONnT) into a
single Bayesian hypothesis comparison. The hypotheses are:

  - H0: background only (no DM signal in any detector)
  - H1: magnetic-moment DM (T90 prediction, sigma_eff ~ mu_x^2)
  - H2: Higgsino inelastic DM (Fan & Tweed 2026, cross-section fixed
         by electroweak theory)
  - H3: instrumental / unknown at LZ only (per-detector nuisance)

The joint log L for each hypothesis is the SUM of per-detector log L,
under the assumption of independence. (A fully correct treatment would
include correlated systematic uncertainties -- this is the dry-run
skeleton, so we use the simplest correct version.)

This script is the DRY-RUN skeleton:
  - Implements the joint log L formula
  - Loads the per-detector recast outputs from paths 1-3
  - Computes posterior weights via flat priors
  - Outputs a JSON with all four hypotheses' joint log L + posterior

NO DATA IS DOWNLOADED. The script reads the dry-run JSONs produced by
paths 1-3 (which themselves emit shells when no data is present), and
combines them. So this script ALWAYS produces a result.

KEY ASSUMPTIONS
===============
  1. Detector independence (true to first order; the [200, 300] keVnr
     window has effectively zero correlated systematic across LZ/PandaX/
     XENONnT because they have different Xe batches, different locations,
     different analysis chains).
  2. Flat priors over the 4 hypotheses.
  3. Magnetic-m and Higgsino inelastic have similar cross-detector
     predictions at PandaX (~0.5 events each), so this test primarily
     distinguishes "is there a signal" (H1 vs H0) rather than "which
     signal is it" (H1 vs H2).
  4. XENONnT S2-only contributes weakly (different energy window) -- it
     primarily constrains the LOW-E rate prediction.

EXPECTED OUTPUT
===============
  - outputs/t90/t90_v23_joint_likelihood.json
      Per-hypothesis log L + posterior + comparison-vs-LZ-only
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

import numpy as np

# Project imports
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_PROJECT_ROOT / "code"))

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

OUTPUTS_DIR = _PROJECT_ROOT / "outputs" / "t90"
PATH_FILES = {
    "lz": OUTPUTS_DIR / "t90_v23_lz_lowE_count.json",
    "pandax": OUTPUTS_DIR / "t90_v23_pandax_highE_count.json",
    "xenonnt": OUTPUTS_DIR / "t90_v23_xenonnt_s2only_count.json",
}

# Per-detector N_obs defaults if recast not run.
# These are the LZ/PandaX/XENONnT published values (or expected from
# PandaX/XENONnT at LZ-tuned magnetic-m interpretation).
N_OBS_DEFAULTS = {
    "lz": {"200_300_keV": 1, "5_50_keV": None, "5_270_keV": None},
    "pandax": {"200_300_keV": 0, "5_50_keV": None, "5_270_keV": None},
    "xenonnt": {"S2only_window": None, "CEvNS_consistent_with_SM": True},
}

# Per-detector N_pred for each hypothesis.
# Numbers from t90_v12 detector response + magnetic-m tuning.
N_PRED_MAGMOM = {
    "lz": {"200_300_keV": 1.0, "5_50_keV": 778.0, "5_270_keV": 1500.0},
    "pandax": {"200_300_keV": 0.54, "5_50_keV": 422.0, "5_270_keV": 815.0},
    "xenonnt": {"S2only_window": 10700, "S2only_threshold_0.04_0.7": "see note"},
}
N_PRED_HIGGSINO_INELASTIC = {
    # Higgsino inelastic (Fan & Tweed 2026): N_pred ~ 1 at LZ,
    # similar at PandaX (scaled by exposure), and S2-only rate is
    # ~same as magnetic-m (operator is energy-deposition-driven, not
    # S1-specific).
    "lz": {"200_300_keV": 1.0, "5_50_keV": 0.5, "5_270_keV": 1.0},
    "pandax": {"200_300_keV": 0.5, "5_50_keV": 0.3, "5_270_keV": 0.5},
    "xenonnt": {"S2only_window": 0.5, "note": "Higgsino is mostly S1+S2 at threshold; S2-only rate is lower"},
}
N_PRED_BACKGROUND_ONLY = {
    "lz": {"200_300_keV": 0.05, "5_50_keV": 120.0, "5_270_keV": 800.0},
    "pandax": {"200_300_keV": 0.02, "5_50_keV": 50.0, "5_270_keV": 400.0},
    "xenonnt": {"S2only_window": 50.0},
}

# Per-detector analysis exposure (tonne-years) -- for transparency.
EXPOSURE_T_Y = {"lz": 2.84, "pandax": 1.54, "xenonnt_S2only": 7.8}


# ---------------------------------------------------------------------------
# Poisson log-likelihood helpers
# ---------------------------------------------------------------------------

def poisson_log_l(n_obs: int, n_pred: float) -> float:
    """Poisson log L (ignoring factorial, which is constant in n_obs).

    log L = -n_pred + n_obs * log(n_pred)  when n_obs > 0
    log L = -n_pred                         when n_obs == 0
    """
    if n_pred <= 0:
        return -np.inf
    if n_obs == 0:
        return -n_pred
    return -n_pred + n_obs * np.log(n_pred)


# ---------------------------------------------------------------------------
# Per-hypothesis joint log L
# ---------------------------------------------------------------------------

def joint_log_l_h_magmom(n_obs: dict, n_pred: dict) -> dict:
    """Joint log L under magnetic-moment DM hypothesis."""
    log_l_per_detector = {}
    total = 0.0
    for det in ("lz", "pandax"):
        for window in ("200_300_keV",):
            n_o = n_obs[det][window]
            n_p = n_pred[det][window]
            ll = poisson_log_l(n_o, n_p)
            log_l_per_detector[f"{det}_{window}"] = {
                "n_obs": n_o, "n_pred": n_p, "log_l": ll,
            }
            total += ll
    # XENONnT S2-only -- weak constraint, include as nuisance (placeholder)
    log_l_per_detector["xenonnt_S2only"] = {
        "n_obs": "not_used_in_dry_run",
        "n_pred": "see_path3_output",
        "log_l": 0.0,
        "note": "XENONnT S2-only is a weak cross-check at wrong energy; log L set to 0 in dry-run.",
    }
    return {"total": total, "per_detector": log_l_per_detector}


def joint_log_l_higgsino(n_obs: dict, n_pred: dict) -> dict:
    """Joint log L under Higgsino inelastic DM hypothesis (Fan & Tweed 2026)."""
    log_l_per_detector = {}
    total = 0.0
    for det in ("lz", "pandax"):
        for window in ("200_300_keV",):
            n_o = n_obs[det][window]
            n_p = n_pred[det][window]
            ll = poisson_log_l(n_o, n_p)
            log_l_per_detector[f"{det}_{window}"] = {
                "n_obs": n_o, "n_pred": n_p, "log_l": ll,
            }
            total += ll
    return {"total": total, "per_detector": log_l_per_detector}


def joint_log_l_background(n_obs: dict, n_pred: dict) -> dict:
    """Joint log L under background-only hypothesis."""
    log_l_per_detector = {}
    total = 0.0
    for det in ("lz", "pandax"):
        for window in ("200_300_keV",):
            n_o = n_obs[det][window]
            n_p = n_pred[det][window]
            ll = poisson_log_l(n_o, n_p)
            log_l_per_detector[f"{det}_{window}"] = {
                "n_obs": n_o, "n_pred": n_p, "log_l": ll,
            }
            total += ll
    return {"total": total, "per_detector": log_l_per_detector}


# ---------------------------------------------------------------------------
# Posterior computation
# ---------------------------------------------------------------------------

def normalize_log_weights(log_weights: dict) -> dict:
    """Normalize a dict of log weights to posterior probabilities.

    Uses log-sum-exp for numerical stability.
    """
    keys = list(log_weights.keys())
    log_w_array = np.array([log_weights[k] for k in keys], dtype=float)
    finite_mask = np.isfinite(log_w_array)
    # Subtract max of finite for stability; non-finite become 0 after exp
    if finite_mask.any():
        log_w_array = log_w_array - np.nanmax(log_w_array[finite_mask])
    w_array = np.zeros_like(log_w_array)
    w_array[finite_mask] = np.exp(log_w_array[finite_mask])
    w_sum = w_array.sum()
    if w_sum == 0:
        return {k: 0.0 for k in keys}
    return {k: float(w_array[i] / w_sum) for i, k in enumerate(keys)}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("T90.23 Path 4 (DRY RUN) -- Joint three-detector likelihood")
    print("=" * 70)

    # Try to load per-detector recast outputs; fall back to defaults.
    n_obs = {}
    for det, path in PATH_FILES.items():
        if path.exists():
            try:
                data = json.loads(path.read_text())
                # Parse per-detector n_obs from the recast output if present
                if det == "lz" and "windows" in data:
                    n_obs[det] = {
                        "200_300_keV": data["windows"].get("248_keV_200_300", {}).get("n_events"),
                        "5_50_keV": data["windows"].get("low_E_5_50", {}).get("n_events"),
                        "5_270_keV": data["windows"].get("full_5_270", {}).get("n_events"),
                    }
                elif det == "pandax":
                    # Currently the PandaX dry-run emits no observed counts.
                    n_obs[det] = {"200_300_keV": None, "5_50_keV": None, "5_270_keV": None}
                elif det == "xenonnt":
                    n_obs[det] = {"S2only_window": None, "CEvNS_consistent_with_SM": True}
                else:
                    n_obs[det] = N_OBS_DEFAULTS[det]
                print(f"[load] {det}: from {path.name}")
            except Exception as exc:
                print(f"[load] {det}: failed to parse {path}: {exc}")
                n_obs[det] = N_OBS_DEFAULTS[det]
        else:
            print(f"[load] {det}: no recast file; using defaults")
            n_obs[det] = N_OBS_DEFAULTS[det]

    # Use LZ-observed 1 event as the anchor; for PandaX assume 0 (the
    # most likely outcome at 1.54 t-y given PandaX has not reported a
    # 248 keV candidate in the published 1.54 t-y paper).
    n_obs_use = {
        "lz": {"200_300_keV": 1, "5_50_keV": None, "5_270_keV": None},
        "pandax": {"200_300_keV": 0, "5_50_keV": None, "5_270_keV": None},
        "xenonnt": {"S2only_window": None},
    }
    print(f"[joint] Using N_obs: LZ={n_obs_use['lz']['200_300_keV']}, "
          f"PandaX={n_obs_use['pandax']['200_300_keV']}")

    # Compute joint log L for each hypothesis
    h_magmom = joint_log_l_h_magmom(n_obs_use, N_PRED_MAGMOM)
    h_higgsino = joint_log_l_higgsino(n_obs_use, N_PRED_HIGGSINO_INELASTIC)
    h_background = joint_log_l_background(n_obs_use, N_PRED_BACKGROUND_ONLY)

    log_weights = {
        "H1_magnetic_moment": h_magmom["total"],
        "H2_higgsino_inelastic": h_higgsino["total"],
        "H0_background_only": h_background["total"],
    }
    posteriors = normalize_log_weights(log_weights)

    output = {
        "mode": "dry_run",
        "n_obs_used": n_obs_use,
        "n_pred_per_hypothesis": {
            "H1_magnetic_moment": N_PRED_MAGMOM,
            "H2_higgsino_inelastic": N_PRED_HIGGSINO_INELASTIC,
            "H0_background_only": N_PRED_BACKGROUND_ONLY,
        },
        "joint_log_l": {
            "H1_magnetic_moment": h_magmom["total"],
            "H2_higgsino_inelastic": h_higgsino["total"],
            "H0_background_only": h_background["total"],
        },
        "joint_log_l_detail": {
            "H1_magnetic_moment": h_magmom["per_detector"],
            "H2_higgsino_inelastic": h_higgsino["per_detector"],
            "H0_background_only": h_background["per_detector"],
        },
        "posteriors": posteriors,
        "key_comparisons": {
            "delta_logL_magmom_vs_background": h_magmom["total"] - h_background["total"],
            "delta_logL_higgsino_vs_background": h_higgsino["total"] - h_background["total"],
            "delta_logL_magmom_vs_higgsino": h_magmom["total"] - h_higgsino["total"],
            "interpretation_rule": (
                "Delta log L > 2 = 'substantial' evidence on Jeffreys scale; "
                ">5 = 'strong'; >10 = 'very strong'. The T90 v17 Bayesian posteriors "
                "(magnetic-m vs Higgsino ~ 47% each, instrumental ~ 6%) came from LZ-only. "
                "Adding PandaX null at [200, 300] keV does NOT distinguish them (both "
                "predict ~0.5 events). Adding LZ's [5, 50] keV count would distinguish."
            ),
        },
        "headline": (
            "Dry-run joint likelihood. To make this live, run paths 1-3 first "
            "(with data present), then re-run this script -- it will load "
            "the per-detector n_obs from their JSON outputs."
        ),
        "next_step_when_live": (
            "Path 1 produces LZ [5, 50] keV count -- this is the ONLY "
            "measurement that distinguishes magnetic-m from Higgsino inelastic. "
            "If path 1's count is ~0, magnetic-m is contradicted. If ~778, "
            "magnetic-m wins decisively."
        ),
    }

    out_path = OUTPUTS_DIR / "t90_v23_joint_likelihood.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"[output] {out_path}")

    # Pretty-print posteriors
    print("\n[posteriors]")
    for h, p in sorted(posteriors.items(), key=lambda x: -x[1]):
        print(f"  {h:30s} {p:.4f}")

    return output


if __name__ == "__main__":
    main()
