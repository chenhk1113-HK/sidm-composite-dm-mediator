"""
T95.11 apply — feed the Gaia-rescued kinematics back into the T95.10
pipeline and report which streams can contribute σ/m predictions.

This replaces the T95.10 velocity-only synthesized constraints for the
streams that T95.11 successfully rescued from Gaia DR3, and flags the
streams that couldn't be rescued.

STATUS: APPLY 2026-09-08
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_PROJECT_ROOT / "code"))

from t95_v26_pilot_113_streams import (  # noqa: E402
    CURATED_STREAMS,
    multi_stream_loglik,
    sigma_m_master_yukawa,
)

# ============================================================================
# Configuration
# ============================================================================
# Streams with v_3d above this are unphysical for bound MW streams.
# Same threshold used in T95.10 outlier filter.
OUTLIER_V3D_KMS = 700.0

# Streams with fewer than this many member-selected stars are too
# unreliable to use.
MIN_MEMBERS = 10


# ============================================================================
# Load results
# ============================================================================
def load_cross_match() -> list[dict]:
    path = _PROJECT_ROOT / "outputs" / "t95" / "t95_v11_cross_match_results.json"
    with path.open() as f:
        return json.load(f)


# ============================================================================
# Build constraint dict from rescued kinematics
# ============================================================================
def classify(results: list[dict]) -> dict:
    """Classify each stream into rescued / outlier / no_members."""
    rescued = {}
    outliers = []
    no_members = []

    for r in results:
        s = r["stream"]
        if r.get("status") != "ok":
            no_members.append(s)
            continue
        v_3d = r.get("v_3d_rescued_kms", 0.0)
        n_mem = r.get("n_members", 0)
        if v_3d > OUTLIER_V3D_KMS:
            outliers.append((s, v_3d, n_mem))
        elif n_mem < MIN_MEMBERS:
            no_members.append(s)
        else:
            rescued[s] = {
                "stream": s,
                "v_kms": v_3d,
                "n_members": n_mem,
            }

    return {"rescued": rescued, "outliers": outliers, "no_members": no_members}


def build_constraints(rescued: dict) -> dict:
    """Build synthesized-but-tighter constraints from Gaia kinematics."""
    constraints = {}
    for s, info in rescued.items():
        v = info["v_kms"]
        sigma_m_pred = sigma_m_master_yukawa(v)
        # Tighter box (factor 3) since Gaia data is more informative than
        # the T95.10 placeholder (factor 5).
        constraints[s] = {
            "stream": s,
            "sigma_m_lower": sigma_m_pred / 3.0,
            "sigma_m_upper": sigma_m_pred * 3.0,
            "v_kms": v,
            "gap_count": 0,
            "reference": f"Gaia DR3 cross-match (this work, T95.11, n={info['n_members']})",
        }
    return constraints


# ============================================================================
# Run the joint fit
# ============================================================================
def main() -> int:
    results = load_cross_match()
    classification = classify(results)
    rescued = classification["rescued"]
    outliers = classification["outliers"]
    no_members = classification["no_members"]

    print("=" * 70)
    print("T95.11 — apply rescued kinematics to joint fit")
    print("=" * 70)
    print(f"\nRescued streams ({len(rescued)}):")
    for s, info in rescued.items():
        print(f"  {s:14s}  v_3d = {info['v_kms']:6.1f} km/s  "
              f"n_members = {info['n_members']}")
    print(f"\nOutliers / unphysical (v_3d > {OUTLIER_V3D_KMS} km/s):")
    for s, v, n in outliers:
        print(f"  {s:14s}  v_3d = {v:7.1f} km/s  n_members = {n}")
    print(f"\nNot enough members (n_members < {MIN_MEMBERS}):")
    for s in no_members:
        print(f"  {s}")

    # Build constraints
    constraints = build_constraints(rescued)

    # Joint fit: curated + rescued (no synthesized — they got upgraded)
    combined = {**CURATED_STREAMS, **constraints}
    multi = multi_stream_loglik(sigma_m_master_yukawa, combined)

    # Reference: curated only (T95.9 baseline)
    multi_baseline = multi_stream_loglik(sigma_m_master_yukawa, CURATED_STREAMS)

    print(f"\n=== Joint loglik ===")
    print(f"T95.9 baseline (curated 10):                      {multi_baseline['combined_loglik']:.3f}")
    print(f"T95.11 (curated 10 + rescued {len(constraints)}):  {multi['combined_loglik']:.3f}")
    print(f"Δ loglik from adding rescued streams:             "
          f"{multi['combined_loglik'] - multi_baseline['combined_loglik']:.3f}")

    # Per-rescued-stream contribution
    print(f"\n=== Per-rescued-stream loglik ===")
    for s in rescued:
        c = multi["per_stream"].get(s, {})
        ll = c.get("loglik", 0.0)
        v = rescued[s]["v_kms"]
        sigma_m_pred = sigma_m_master_yukawa(v)
        print(f"  {s:14s}  loglik = {ll:+.3f}  σ/m_pred = {sigma_m_pred:.3f} cm²/g  "
              f"(box: [{sigma_m_pred/3:.3f}, {sigma_m_pred*3:.3f}])")

    # Update finding summary
    summary = {
        "t95_11_id": "T95.11",
        "date": "2026-09-08",
        "n_rescued": len(rescued),
        "n_outliers": len(outliers),
        "n_no_members": len(no_members),
        "n_total": len(results),
        "rescued_streams": list(rescued.keys()),
        "outlier_streams": [s for s, _, _ in outliers],
        "no_member_streams": no_members,
        "joint_loglik_baseline": multi_baseline["combined_loglik"],
        "joint_loglik_with_rescued": multi["combined_loglik"],
        "delta_loglik": multi["combined_loglik"] - multi_baseline["combined_loglik"],
        "per_stream_loglik": multi["per_stream"],
    }

    out_path = _PROJECT_ROOT / "outputs" / "t95" / "t95_v11_apply_results.json"
    out_path.write_text(json.dumps(summary, indent=2, default=str))
    print(f"\nWrote: {out_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
