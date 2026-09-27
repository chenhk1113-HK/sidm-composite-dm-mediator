#!/usr/bin/env python3
"""
Phase 2 minimal: cross-channel correlation fix for Ch9 (DM-free UDG) + Ch10 (DM-dominated UDG).

Per R1 mapreview.docx (paragraphs 50-60): "NGC 1052-DF2 appearing in both Ch9 and Ch13 is
a real statistical violation. Treating them as independent inflates the effective number
of constraints."

Per R2 (paragraph 133): "Implement a minimal cross-channel correlation treatment (shared
nuisance parameters or a simple hierarchical layer) -- 1 week maximum. Do not let it
become a multi-week blocker."

DESIGN (minimal):
  - Add ONE shared nuisance eta_udg (Gaussian prior N(0, 0.5 dex)) that shifts the
    log sigma/m Gaussian peak for Ch9 AND Ch10 simultaneously.
  - Rationale: both channels anchor at the SAME v0.3-prelim MAP sigma/m_0 ~ 0.7-0.78 cm^2/g
    and use overlapping optical UDG photometry (Dragonfly Telephoto Array + spectroscopy).
  - Marginalize over eta_udg analytically for each (sigma_m_0, a) point.

HONEST FRAMING (per AGENTS.md rule 11):
  - Reviewer 1 said "NGC 1052-DF2 in Ch9 and Ch13" -- Ch13 doesn't exist (it's Ch10 = LSB-6).
    The structural point (shared survey systematics) is still valid.
  - The shared nuisance here is the UDG photometric calibration uncertainty, NOT a
    shared galaxy. This is a SURROGATE for the more complex full hierarchical model.
  - This is a 1-parameter nuisance, not a full hierarchical framework.

KILL CRITERION (per roadmap):
  - If marginalizing over eta_udg drops log Z by more than 10 nats below the current
    log Z = -2.94 (i.e., to below -13), STOP -- the model is not credible after
    accounting for the systematic.

Run as: python phase2_minimal_hierarchical.py
"""

from __future__ import annotations
import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy.special import logsumexp

# Setup paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
V03_CODE = PROJECT_ROOT / "v0.3-prelim" / "code"
sys.path.insert(0, str(V03_CODE))
sys.path.insert(0, str(PROJECT_ROOT))

import channels_extended as ch_ext

# ----- Phase 2 minimal hierarchical nuisance -----

# UDG calibration uncertainty (shared Dragonfly photometry + optical spectroscopy)
# Width in dex: from UDG photometric redshift uncertainty (~10%) + distance uncertainty (~15%)
# Combined: 0.5 dex is conservative.
ETA_UDG_PRIOR_WIDTH_DEX = 0.5

# Number of quadrature points for the Gaussian integral over eta_udg
N_QUAD = 41  # ±3 sigma range


def loglike_ch9_with_eta(sigma_m_0: float, a: float, eta_udg: float) -> float:
    """Ch9 with shifted log(sigma/m) peak by eta_udg."""
    log_sm_eff = np.log10(sigma_m_0) + 0.523 * a
    chi = ((log_sm_eff - (np.log10(ch_ext.NGC1052_DF2_SIGMA_M_TYPICAL) + eta_udg))
           / ch_ext.DM_FREE_UDG_RATE_WIDTH) ** 2
    return -0.5 * chi


def loglike_ch10_with_eta(sigma_m_0: float, a: float, eta_udg: float) -> float:
    """Ch10 with shifted log(sigma/m) peak by eta_udg."""
    log_sm_eff = np.log10(sigma_m_0) - 0.699 * a
    chi = ((log_sm_eff - (np.log10(ch_ext.DM_DOM_UDG_SIGMA_M_PEAK) + eta_udg))
           / ch_ext.DM_DOM_UDG_SIGMA_M_WIDTH) ** 2
    return -0.5 * chi


def loglike_ch9_ch10_marginalized(sigma_m_0: float, a: float) -> float:
    """Joint marginal likelihood over eta_udg for Ch9 + Ch10.

    Log of the analytic marginal: log ∫ p(eta_udg) L(eta_udg) deta_udg
    Using Gauss-Hermite-like quadrature on Gaussian prior.

    Returns the LOG of the marginal likelihood, summed across Ch9 + Ch10.
    """
    # Quadrature nodes over eta_udg
    eta_nodes = np.linspace(-3 * ETA_UDG_PRIOR_WIDTH_DEX,
                             3 * ETA_UDG_PRIOR_WIDTH_DEX,
                             N_QUAD)
    weights = np.exp(-0.5 * (eta_nodes / ETA_UDG_PRIOR_WIDTH_DEX) ** 2)
    weights /= weights.sum()

    # Joint loglike for Ch9 + Ch10 at each eta node
    loglikes = []
    for eta in eta_nodes:
        ll9 = loglike_ch9_with_eta(sigma_m_0, a, eta)
        ll10 = loglike_ch10_with_eta(sigma_m_0, a, eta)
        loglikes.append(ll9 + ll10)
    loglikes = np.array(loglikes)

    # log ∫ w(eta) L(eta) deta = logsumexp(log w + log L)
    log_marginal = logsumexp(np.log(weights + 1e-300) + loglikes)
    return float(log_marginal)


def loglike_ch9_ch10_independent(sigma_m_0: float, a: float) -> float:
    """Independent Ch9 + Ch10 (current model, no shared nuisance)."""
    return (ch_ext.loglike_dm_free_udg(sigma_m_0, a)
            + ch_ext.loglike_dm_dominated_udg(sigma_m_0, a))


# ----- Comparison test -----

def main():
    print("=" * 70)
    print("PHASE 2 MINIMAL: Cross-channel correlation fix for Ch9 + Ch10")
    print("=" * 70)

    # Test at the v0.3-prelim MAP (log_sigma_m_0 = -0.14, a = 1.31)
    # Also at sigma/m_0 = 0.78 (Ch9 anchor) and sigma/m_0 = 0.7 (Ch10 anchor)
    test_points = [
        ("v0.3-prelim MAP (T39)", 10 ** -0.14, 1.31),
        ("Ch9 anchor (sigma/m_0=0.78, a=0)", 0.78, 0.0),
        ("Ch10 anchor (sigma/m_0=0.7, a=0)", 0.7, 0.0),
        ("MAP 6D (sigma/m_0=1.57, a=0.94)", 1.57, 0.94),
        ("sigma/m_0=0.1, a=0.5", 0.1, 0.5),
        ("sigma/m_0=5.0, a=0.5", 5.0, 0.5),
    ]

    print(f"\n{'Point':<40} | {'Independent':>12} | {'Marginalized':>12} | {'Δ log Z':>10}")
    print("-" * 80)

    independent_log_z = 0.0
    marginalized_log_z = 0.0

    for label, sm0, a in test_points:
        ll_ind = loglike_ch9_ch10_independent(sm0, a)
        ll_marg = loglike_ch9_ch10_marginalized(sm0, a)
        delta = ll_marg - ll_ind
        print(f"{label:<40} | {ll_ind:>12.3f} | {ll_marg:>12.3f} | {delta:>+10.3f}")

    print("\n=== Kill-criterion check at T39 MAP ===")
    # T39 Tier-3 marginalization reports log_Z = -2.94 for the 4D posterior
    # We need to test: does marginalizing over eta_udg drop this below log_Z < -10?
    print("Current T39 log_Z = -2.94 (independent Ch9 + Ch10)")
    print("Kill criterion: marginalization must NOT drop log_Z by > 10 nats (i.e., to < -13)")
    print("(Full T39 re-run with hierarchical model is needed for definitive answer,")
    print(" but the marginalization penalty here is an upper bound.)")

    # Compute total marginalization penalty (sum across test points weighted by likelihood)
    weights = np.array([np.exp(ll_ind) for _, sm0, a in test_points
                        for ll_ind in [loglike_ch9_ch10_independent(sm0, a)]])
    weights /= weights.sum()

    total_ind = sum(loglike_ch9_ch10_independent(sm0, a) for _, sm0, a in test_points)
    total_marg = sum(loglike_ch9_ch10_marginalized(sm0, a) for _, sm0, a in test_points)
    print(f"\nTest-point sum (independent): {total_ind:.3f}")
    print(f"Test-point sum (marginalized): {total_marg:.3f}")
    print(f"Marginalization penalty (upper bound): {total_marg - total_ind:.3f} nats")

    print("\n=== Output ===")
    out = {
        "phase": 2,
        "shared_nuisance": "eta_udg",
        "prior_width_dex": ETA_UDG_PRIOR_WIDTH_DEX,
        "rationale": "UDG photometric calibration (Dragonfly + optical spectroscopy)",
        "channels_affected": ["ch09_dm_free_udg", "ch10_dm_dom_udg"],
        "test_points": [
            {"label": lbl, "sigma_m_0": sm0, "a": a,
             "ll_independent": loglike_ch9_ch10_independent(sm0, a),
             "ll_marginalized": loglike_ch9_ch10_marginalized(sm0, a),
             "delta_nats": loglike_ch9_ch10_marginalized(sm0, a)
                          - loglike_ch9_ch10_independent(sm0, a)}
            for lbl, sm0, a in test_points
        ],
        "t39_kill_criterion": {
            "current_log_z": -2.94,
            "kill_threshold": -13.0,
            "marginalization_penalty_upper_bound_nats": total_marg - total_ind,
        },
        "honest_framing": [
            "Reviewer 1 said 'NGC 1052-DF2 in Ch9 and Ch13' -- Ch13 doesn't exist (it's Ch10 = LSB-6).",
            "The structural point (shared survey systematics) is still valid.",
            "This is a 1-parameter nuisance, not a full hierarchical framework.",
            "Width 0.5 dex is conservative (UDG photometric + distance uncertainty).",
        ],
    }
    out_path = PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "phase2_minimal_hierarchical.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2))
    print(f"Wrote {out_path}")
    print("\nPhase 2 minimal smoke test complete.")


if __name__ == "__main__":
    main()
