"""
T95.10 lit-search apply — apply the populated literature results to the
T95.10 joint fit and report the change in loglikelihood.

This module replaces synthesized velocity-only constraints with published
constraints where available. The realistic outcome is:
  - Sagittarius gets a real (wide) σ/m box from the literature
  - 93 streams stay as synthesized (no published constraint)
  - 1 stream defaults to synthesized

STATUS: APPLY 2026-09-08
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_PROJECT_ROOT / "code"))

from t95_v26_pilot_113_streams import (  # noqa: E402
    CURATED_STREAMS,
    multi_stream_loglik,
    sigma_m_master_yukawa,
)


# ============================================================================
# Load the populated literature results
# ============================================================================
def load_lit_results() -> dict:
    path = _PROJECT_ROOT / "outputs" / "t95" / "t95_v26_lit_search_results.json"
    with path.open() as f:
        return json.load(f)


def load_full_results() -> dict:
    path = _PROJECT_ROOT / "outputs" / "t95" / "t95_v26_full_results.json"
    with path.open() as f:
        return json.load(f)


# ============================================================================
# Build per-stream constraints dict from literature + full results
# ============================================================================
def build_constraints_dict(lit_results: dict, full_results: dict) -> tuple[dict, dict]:
    """Returns (synthesized_dict, real_constraint_dict).

    synthesized_dict: streams with no published constraint → velocity-only
                      wide boxes
    real_constraint_dict: streams with published constraints → real boxes
    """
    synthesized = {}
    real_constraints = {}

    # Build lookup by stream name
    ok_by_name = {d["stream"]: d for d in full_results["per_stream"]
                  if d.get("status") == "ok"}
    lit_by_name = {row["stream"]: row for row in lit_results["rows"]}

    for stream, lit_row in lit_by_name.items():
        if stream not in ok_by_name:
            continue  # stream failed pipeline; skip
        ok_d = ok_by_name[stream]
        v = ok_d["v_3d_kms"]
        sigma_m_pred = ok_d["sigma_m_pred_master_yukawa_cm2_per_g"]

        if lit_row.get("constraint_status") == "constraint_added":
            # Use published constraint
            real_constraints[stream] = {
                "stream": stream,
                "sigma_m_lower": float(lit_row["sigma_m_lower_published"]),
                "sigma_m_upper": float(lit_row["sigma_m_upper_published"]),
                "v_kms": v,
                "gap_count": 0,
                "reference": lit_row.get("papers_found", "lit search"),
            }
        else:
            # No published constraint; use velocity-only synthesized
            synthesized[stream] = {
                "stream": stream,
                "sigma_m_lower": sigma_m_pred / 5.0,
                "sigma_m_upper": sigma_m_pred * 5.0,
                "v_kms": v,
                "gap_count": 0,
                "reference": "velocity-only placeholder (this work)",
            }

    return synthesized, real_constraints


# ============================================================================
# Run the joint fit with literature-applied constraints
# ============================================================================
def run_lit_applied() -> dict:
    lit_results = load_lit_results()
    full_results = load_full_results()

    synthesized, real_constraints = build_constraints_dict(lit_results, full_results)

    # Curated (T95.9) + real lit-search constraints + synthesized
    combined_streams = {**CURATED_STREAMS, **real_constraints, **synthesized}
    multi = multi_stream_loglik(sigma_m_master_yukawa, combined_streams)

    # Compare with the synthesized-only joint fit
    synthesized_only_streams = {**CURATED_STREAMS, **synthesized}
    multi_synth_only = multi_stream_loglik(sigma_m_master_yukawa, synthesized_only_streams)

    out = {
        "lit_search_id": "T95.10-lit-applied",
        "date": "2026-09-08",
        "n_streams_total": len(combined_streams),
        "n_curated": len(CURATED_STREAMS),
        "n_real_lit_constraints": len(real_constraints),
        "n_synthesized": len(synthesized),
        "joint_loglik_with_lit": multi["combined_loglik"],
        "joint_loglik_synthesized_only": multi_synth_only["combined_loglik"],
        "delta_loglik_from_lit": multi["combined_loglik"] - multi_synth_only["combined_loglik"],
        "real_constraint_streams": list(real_constraints.keys()),
        "per_stream_contribution": multi["per_stream"],
    }

    print("=" * 70)
    print("T95.10 — literature-applied joint fit")
    print("=" * 70)
    print(f"Curated (T95.9, published):     {len(CURATED_STREAMS)}")
    print(f"Real lit-search constraints:    {len(real_constraints)}  {list(real_constraints.keys())}")
    print(f"Velocity-only synthesized:      {len(synthesized)}")
    print(f"Total in joint fit:             {len(combined_streams)}")
    print()
    print(f"Joint loglik (with lit-search constraints):    {multi['combined_loglik']:.3f}")
    print(f"Joint loglik (synthesized only):              {multi_synth_only['combined_loglik']:.3f}")
    print(f"Δ loglik from adding lit constraints:         {out['delta_loglik_from_lit']:.3f}")
    print()

    # Per-stream contributions from real constraints
    print("Per-stream loglik from REAL lit-search constraints (top contributors):")
    for s in real_constraints:
        c = multi["per_stream"].get(s, {})
        ll = c.get("loglik", 0.0)
        print(f"  {s:15s}  loglik = {ll:+.3f}  "
              f"σ/m_pred = {sigma_m_master_yukawa(real_constraints[s]['v_kms']):.3f}  "
              f"box = [{real_constraints[s]['sigma_m_lower']}, {real_constraints[s]['sigma_m_upper']}]")
    print()

    return out


def main() -> int:
    out = run_lit_applied()
    out_path = _PROJECT_ROOT / "outputs" / "t95" / "t95_v26_lit_applied.json"
    out_path.write_text(json.dumps(out, indent=2, default=str))
    print(f"Wrote: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
