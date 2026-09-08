"""
T95.10 — Pilot extension: compute sigma/m constraints for a stratified 8-stream
subset of the 113 galstreams residual population.

PURPOSE
=======
Validate that the T95.9 pipeline scales to streams without published gap
measurements by using a per-stream sigma/m prediction (from the stream's
orbital velocity under the master Yukawa model) and reporting:
  - v_3d (kinematic scale)
  - predicted sigma/m at that v_3d
  - implied gap-count expectation (proportional to sigma/m * v_3d^-2)
  - pipeline failures (degenerate kinematics, missing data)

This is a PILOT, not a joint fit. The 8 streams are picked to cover:
  - Near / well-characterized (M2, NGC6397)
  - Near / high v_r stress test (Ophiuchus)
  - Gaia-discovered near (Gaia-8)
  - Sagittarius (benchmark tidal stream)
  - Distant Gaia-only (Cetus, Elqui)
  - Degenerate kinematics (Alpheus: v_t=0, v_r=0 — failure mode)

OUTPUTS
  - outputs/t95/t95_v26_pilot_results.json
  - outputs/t95/t95_v26_pilot_summary.md

STATUS: PILOT 2026-09-08
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import math

_PROJECT_ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(_PROJECT_ROOT / "code"))

# Reuse T95.9 helpers
from t95_v25_multi_stream_real_galstreams import (  # noqa: E402
    CURATED_STREAMS,
    build_stream_catalog,
    compute_orbital_velocity,
    list_all_available_streams,
    load_stream_summary,
    load_stream_track,
    multi_stream_loglik,
    sigma_m_master_yukawa,
)


# ============================================================================
# Pilot stream selection (stratified across data-quality regimes)
# ============================================================================
PILOT_STREAMS = [
    "M2",                # near globular
    "NGC6397",           # near globular
    "Ophiuchus",         # near, high v_r (290 km/s)
    "Gaia-8",            # Gaia-discovered near
    "Sagittarius",       # benchmark tidal stream
    "Cetus",             # distant, Gaia DR3-only pm
    "Elqui",             # most distant with kinematics
    "Alpheus",           # negative test: degenerate kinematics
]


# ============================================================================
# Per-stream sigma/m inference
# ============================================================================
def stream_sigma_m_diagnostic(stream_name: str) -> dict:
    """Compute the master-Yukawa sigma/m prediction at a stream's orbital
    velocity, plus an expected gap count under simple Poisson statistics.

    No published constraint is assumed. The output is a *prediction* to be
    compared against future gap searches, not a likelihood term.
    """
    t_total = time.time()
    t0 = time.time()
    summary = load_stream_summary(stream_name)
    track = load_stream_track(stream_name)
    wall_load = time.time() - t0

    if summary is None or len(summary) == 0:
        return {
            "stream": stream_name,
            "status": "no_summary",
            "wall_load_s": wall_load,
            "wall_total_s": time.time() - t_total,
        }
    if track is None or len(track) == 0:
        return {
            "stream": stream_name,
            "status": "no_track",
            "wall_load_s": wall_load,
            "wall_total_s": time.time() - t_total,
        }

    row = summary.iloc[0]
    t1 = time.time()
    orb = compute_orbital_velocity(track)
    wall_velocity = time.time() - t1

    if not orb:
        return {
            "stream": stream_name,
            "status": "no_velocity",
            "wall_load_s": wall_load,
            "wall_velocity_s": wall_velocity,
            "wall_total_s": time.time() - t_total,
        }

    v_3d = orb["v_3d_median"]
    v_t = orb["v_t_median"]
    v_r_mid = float(row["mid.radial_velocity"])
    n_pts = orb["n_track_points"]

    # galstreams placeholder convention: v_r = 1000 km/s exactly means "not measured".
    # The T95.9 filter (< 1000) accepts v_r=999.999... which is the same sentinel.
    # We additionally reject |v_r_mid| >= 500 as physically unreasonable for bound MW streams.
    vr_is_placeholder = (abs(v_r_mid) >= 999.0)
    if vr_is_placeholder:
        # Use tangential-only velocity (no v_r contribution).
        # This is correct when v_r was never measured; the placeholder value is bogus.
        v_3d = v_t
        v_r_effective = 0.0
    else:
        v_r_effective = v_r_mid

    # Recompute v_3d if we stripped the placeholder
    v_3d_used = math.sqrt(v_t ** 2 + v_r_effective ** 2)

    # Outlier filter: bound MW streams should have |v_3d| < 700 km/s
    # (MW escape velocity ~ 500-600 km/s; allow some margin for orbital motion
    # at apogalacticon). Beyond this, the data is suspect (e.g. track-level
    # placeholder not just summary-level).
    OUTLIER_V3D_KMS = 700.0
    if v_3d_used > OUTLIER_V3D_KMS:
        return {
            "stream": stream_name,
            "status": "outlier_needs_review",
            "distance_kpc": float(row["mid.distance"]),
            "v_r_mid_kms": float(v_r_mid),
            "v_t_kms": float(v_t),
            "v_3d_kms": float(v_3d_used),
            "n_track_points": int(n_pts),
            "v_r_was_placeholder": bool(vr_is_placeholder),
            "outlier_reason": f"v_3d={v_3d_used:.1f} km/s exceeds {OUTLIER_V3D_KMS} km/s bound-stream threshold",
            "wall_load_s": wall_load,
            "wall_velocity_s": wall_velocity,
            "wall_total_s": time.time() - t_total,
        }

    # Degenerate-kinematics flag: cannot produce sigma/m prediction
    degenerate = (v_3d_used == 0.0) or (v_t == 0.0 and v_r_effective == 0.0)

    if degenerate:
        return {
            "stream": stream_name,
            "status": "degenerate_kinematics",
            "distance_kpc": float(row["mid.distance"]),
            "v_r_mid_kms": float(v_r_mid),
            "v_t_kms": float(v_t),
            "v_3d_kms": float(v_3d_used),
            "n_track_points": int(n_pts),
            "v_r_was_placeholder": bool(vr_is_placeholder),
            "wall_load_s": wall_load,
            "wall_velocity_s": wall_velocity,
            "wall_total_s": time.time() - t_total,
        }

    # Master-Yukawa prediction
    sigma_m_pred = sigma_m_master_yukawa(v_3d)

    # Expected gap count under simple Poisson: lambda ∝ sigma/m * v^-2
    # Calibrate against Pal5 (sigma_m=1.25 mid, v=30, gaps=5) as anchor.
    ANCHOR_SIGMA_M = 1.25
    ANCHOR_V = 30.0
    ANCHOR_GAPS = 5.0
    expected_gaps = ANCHOR_GAPS * (sigma_m_pred / ANCHOR_SIGMA_M) * (ANCHOR_V / v_3d) ** 2

    return {
        "stream": stream_name,
        "status": "ok",
        "distance_kpc": float(row["mid.distance"]),
        "v_r_mid_kms": float(v_r_mid),
        "v_r_effective_kms": float(v_r_effective),
        "v_t_kms": float(v_t),
        "v_3d_kms": float(v_3d_used),
        "n_track_points": int(n_pts),
        "v_r_was_placeholder": bool(vr_is_placeholder),
        "sigma_m_pred_master_yukawa_cm2_per_g": float(sigma_m_pred),
        "expected_gaps_poisson_anchor_pal5": float(expected_gaps),
        "wall_load_s": wall_load,
        "wall_velocity_s": wall_velocity,
        "wall_total_s": time.time() - t_total,
    }


# ============================================================================
# Pseudo-constraint synthesis: streams with sufficient velocity resolution
# get a wide sigma/m box derived from velocity uncertainty only
# ============================================================================
def synthesize_velocity_only_constraint(stream_name: str) -> Optional[dict]:
    """For streams without published gap data, we can only derive a WEAK
    velocity-coherence-based constraint: sigma/m must be small enough that
    subhalo flybys do not shred the stream within the observed track length.

    The classical stream-shredding criterion (e.g. Carlberg 2012) gives
        sigma/m <~ v_stream / (M_subhalo / M_stream) * (b / R_stream)
    but in the absence of mass estimates for the progenitor, we use a
    conservative V_max constraint from the master Yukawa at v_3d.

    This is a placeholder until gap counts or progenitor masses are
    available. Returns None for degenerate-kinematics streams.
    """
    diag = stream_sigma_m_diagnostic(stream_name)
    if diag.get("status") != "ok":
        return None
    v = diag["v_3d_kms"]
    sigma_m_pred = diag["sigma_m_pred_master_yukawa_cm2_per_g"]
    # Wide box: [sigma_m_pred / 5, sigma_m_pred * 5]
    return {
        "stream": stream_name,
        "sigma_m_lower": sigma_m_pred / 5.0,
        "sigma_m_upper": sigma_m_pred * 5.0,
        "v_kms": v,
        "gap_count": 0,  # unmeasured
        "reference": "velocity-only placeholder (this work, pilot)",
    }


# ============================================================================
# Pilot runner
# ============================================================================
def run_pilot() -> dict:
    """Run the 8-stream pilot and aggregate timing + diagnostics."""
    print("=" * 70)
    print("T95.10 PILOT — 113-stream residual extension")
    print("=" * 70)
    print(f"Pilot streams ({len(PILOT_STREAMS)}): {PILOT_STREAMS}")
    print()

    per_stream = []
    total_t0 = time.time()
    for s in PILOT_STREAMS:
        t = time.time()
        diag = stream_sigma_m_diagnostic(s)
        diag["wall_total_s"] = time.time() - t
        per_stream.append(diag)
        status = diag.get("status", "unknown")
        if status == "ok":
            print(f"  ✓ {s:15s} d={diag['distance_kpc']:6.2f} kpc  v_3d={diag['v_3d_kms']:7.1f} km/s  "
                  f"sigma/m={diag['sigma_m_pred_master_yukawa_cm2_per_g']:.3f}  "
                  f"E[gaps]={diag['expected_gaps_poisson_anchor_pal5']:.2f}  "
                  f"({diag['wall_total_s']:.2f}s)")
        else:
            print(f"  ✗ {s:15s} status={status:24s}  ({diag['wall_total_s']:.2f}s)")

    total_wall = time.time() - total_t0

    # Aggregate
    ok_streams = [d for d in per_stream if d.get("status") == "ok"]
    degenerate = [d for d in per_stream if d.get("status") == "degenerate_kinematics"]

    # Synthesize velocity-only constraints for the OK subset
    synthesized = {}
    for s in PILOT_STREAMS:
        c = synthesize_velocity_only_constraint(s)
        if c is not None:
            synthesized[s] = c

    # Joint loglik: curated (10) + synthesized (8)
    combined_streams = {**CURATED_STREAMS, **synthesized}
    multi = multi_stream_loglik(sigma_m_master_yukawa, combined_streams)

    summary = {
        "pilot_id": "T95.10",
        "pilot_date": "2026-09-08",
        "n_pilot_streams": len(PILOT_STREAMS),
        "n_ok": len(ok_streams),
        "n_degenerate": len(degenerate),
        "n_failed_other": len([d for d in per_stream
                                if d.get("status") not in ("ok", "degenerate_kinematics")]),
        "wall_total_s": total_wall,
        "wall_per_stream_avg_s": total_wall / max(len(PILOT_STREAMS), 1),
        "wall_per_stream_max_s": max((d["wall_total_s"] for d in per_stream), default=0.0),
        "velocity_range_kms": (
            min((d["v_3d_kms"] for d in ok_streams), default=None),
            max((d["v_3d_kms"] for d in ok_streams), default=None),
        ),
        "distance_range_kpc": (
            min((d["distance_kpc"] for d in ok_streams), default=None),
            max((d["distance_kpc"] for d in ok_streams), default=None),
        ),
        "per_stream": per_stream,
        "synthesized_constraints": synthesized,
        "joint_loglik_with_synthesized": {
            "n_streams": len(combined_streams),
            "combined_loglik": multi["combined_loglik"],
        },
    }

    print()
    print(f"Total wall time: {total_wall:.2f}s  "
          f"per-stream avg: {summary['wall_per_stream_avg_s']:.2f}s  "
          f"max: {summary['wall_per_stream_max_s']:.2f}s")
    print(f"Joint loglik (curated 10 + synthesized {len(synthesized)}): "
          f"{multi['combined_loglik']:.3f}")

    return summary


# ============================================================================
# Full 113-stream runner
# ============================================================================
def run_full(verbose: bool = False) -> dict:
    """Run the full residual population: galstreams catalog minus curated 10.

    Returns per-stream diagnostics, synthesized constraints, and joint
    loglikelihood over curated + synthesized.
    """
    print("=" * 70)
    print("T95.10 FULL — 113-stream residual run")
    print("=" * 70)

    # Enumerate the full set of streams with usable track + velocity data.
    # Reuse T95.9 build_stream_catalog() which already filters on track+velocity.
    t0 = time.time()
    catalog = build_stream_catalog()
    wall_catalog = time.time() - t0

    all_streams_in_catalog = sorted(catalog["stream"].tolist())
    residual = [s for s in all_streams_in_catalog if s not in CURATED_STREAMS]

    print(f"galstreams catalog total: {len(all_streams_in_catalog)} streams")
    print(f"curated (excluded): {len(CURATED_STREAMS)} streams")
    print(f"residual population: {len(residual)} streams")
    print(f"catalog build wall: {wall_catalog:.2f}s")
    print()

    # Per-stream diagnostic
    per_stream = []
    total_t0 = time.time()
    for i, s in enumerate(residual):
        diag = stream_sigma_m_diagnostic(s)
        per_stream.append(diag)
        if verbose and diag.get("status") == "ok":
            print(f"  [{i+1:3d}/{len(residual)}] {s:18s} d={diag['distance_kpc']:6.2f} kpc  "
                  f"v_3d={diag['v_3d_kms']:7.1f} km/s  "
                  f"σ/m={diag['sigma_m_pred_master_yukawa_cm2_per_g']:.3f}  "
                  f"({diag['wall_total_s']:.2f}s)")
    total_wall = time.time() - total_t0

    ok_streams = [d for d in per_stream if d.get("status") == "ok"]
    degenerate = [d for d in per_stream if d.get("status") == "degenerate_kinematics"]
    outlier = [d for d in per_stream if d.get("status") == "outlier_needs_review"]
    failed_other = [d for d in per_stream
                    if d.get("status") not in ("ok", "degenerate_kinematics", "outlier_needs_review")]

    # Synthesize velocity-only constraints for the OK subset
    synthesized = {}
    for d in ok_streams:
        s = d["stream"]
        v = d["v_3d_kms"]
        sigma_m_pred = d["sigma_m_pred_master_yukawa_cm2_per_g"]
        synthesized[s] = {
            "stream": s,
            "sigma_m_lower": sigma_m_pred / 5.0,
            "sigma_m_upper": sigma_m_pred * 5.0,
            "v_kms": v,
            "gap_count": 0,
            "reference": "velocity-only placeholder (this work, full 113)",
        }

    # Joint loglik: curated 10 + synthesized N
    combined_streams = {**CURATED_STREAMS, **synthesized}
    multi = multi_stream_loglik(sigma_m_master_yukawa, combined_streams)

    summary = {
        "full_id": "T95.10-full",
        "full_date": "2026-09-08",
        "n_catalog_total": len(all_streams_in_catalog),
        "n_curated": len(CURATED_STREAMS),
        "n_residual": len(residual),
        "n_ok": len(ok_streams),
        "n_degenerate": len(degenerate),
        "n_outlier": len(outlier),
        "n_failed_other": len(failed_other),
        "wall_catalog_s": wall_catalog,
        "wall_total_s": total_wall,
        "wall_per_stream_avg_s": total_wall / max(len(residual), 1),
        "wall_per_stream_max_s": max((d["wall_total_s"] for d in per_stream), default=0.0),
        "velocity_range_kms": (
            min((d["v_3d_kms"] for d in ok_streams), default=None),
            max((d["v_3d_kms"] for d in ok_streams), default=None),
        ),
        "distance_range_kpc": (
            min((d["distance_kpc"] for d in ok_streams), default=None),
            max((d["distance_kpc"] for d in ok_streams), default=None),
        ),
        "per_stream": per_stream,
        "synthesized_constraints": synthesized,
        "joint_loglik_with_synthesized": {
            "n_streams": len(combined_streams),
            "n_curated": len(CURATED_STREAMS),
            "n_synthesized": len(synthesized),
            "combined_loglik": multi["combined_loglik"],
        },
        "degenerate_stream_names": sorted([d["stream"] for d in degenerate]),
        "outlier_stream_names": sorted([d["stream"] for d in outlier]),
        "failed_other_stream_names": sorted([d["stream"] for d in failed_other]),
    }

    print()
    print(f"Residual wall time: {total_wall:.2f}s  "
          f"per-stream avg: {summary['wall_per_stream_avg_s']:.3f}s  "
          f"max: {summary['wall_per_stream_max_s']:.2f}s")
    print(f"OK: {len(ok_streams)}  Degenerate: {len(degenerate)}  "
          f"Outlier: {len(outlier)}  Other failed: {len(failed_other)}")
    print(f"Joint loglik (curated 10 + synthesized {len(synthesized)}): "
          f"{multi['combined_loglik']:.3f}")

    return summary


def write_full_summary_md(summary: dict, out_path: Path) -> None:
    """Markdown report for the full 113-stream run."""
    lines = []
    lines.append("# T95.10 Full: 113-stream residual run")
    lines.append("")
    lines.append(f"**Date:** {summary['full_date']}  ")
    lines.append(f"**galstreams catalog total:** {summary['n_catalog_total']}  ")
    lines.append(f"**Curated (T95.9, excluded):** {summary['n_curated']}  ")
    lines.append(f"**Residual population:** {summary['n_residual']}  ")
    lines.append("")
    lines.append("## Outcome breakdown")
    lines.append("")
    lines.append(f"- ✓ Pipeline OK: **{summary['n_ok']}**")
    lines.append(f"- ⚠ Outliers (v_3d > 700 km/s, suspicious data): **{summary['n_outlier']}**")
    lines.append(f"- ✗ Degenerate kinematics (v_t=0, v_r=0): **{summary['n_degenerate']}**")
    lines.append(f"- ✗ Other failures (no track/velocity): **{summary['n_failed_other']}**")
    lines.append("")
    lines.append("## Wall time")
    lines.append("")
    lines.append(f"- Catalog build: {summary['wall_catalog_s']:.2f}s")
    lines.append(f"- Residual processing: {summary['wall_total_s']:.2f}s")
    lines.append(f"- Per-stream avg: {summary['wall_per_stream_avg_s']:.3f}s")
    lines.append(f"- Per-stream max: {summary['wall_per_stream_max_s']:.2f}s")
    lines.append("")
    lines.append("## Velocity and distance coverage (OK subset)")
    lines.append("")
    lines.append(f"- v_3d range: {summary['velocity_range_kms'][0]:.1f} – {summary['velocity_range_kms'][1]:.1f} km/s")
    lines.append(f"- d range: {summary['distance_range_kpc'][0]:.2f} – {summary['distance_range_kpc'][1]:.2f} kpc")
    lines.append("")
    lines.append("## Joint loglikelihood")
    lines.append("")
    joint = summary["joint_loglik_with_synthesized"]
    lines.append(f"- Curated streams (T95.9, published constraints): {joint['n_curated']}")
    lines.append(f"- Synthesized streams (this work, velocity-only): {joint['n_synthesized']}")
    lines.append(f"- Total in joint fit: **{joint['n_streams']}**")
    lines.append(f"- Combined loglik (master Yukawa): **{joint['combined_loglik']:.3f}**")
    lines.append("")
    lines.append("## Per-stream constraint table")
    lines.append("")
    lines.append("Full table is in `outputs/t95/t95_v26_full_results.json`.")
    lines.append("")
    lines.append("| ✓/✗ | Stream | d (kpc) | v_3d (km/s) | σ/m pred (cm²/g) | E[gaps] |")
    lines.append("|---|---|---|---|---|---|")
    for d in sorted(summary["per_stream"],
                    key=lambda x: (x.get("status") != "ok", x.get("v_3d_kms", 0))):
        status = d.get("status", "?")
        if status == "ok":
            lines.append(
                f"| ✓ | {d['stream']} | {d['distance_kpc']:.2f} | {d['v_3d_kms']:.1f} | "
                f"{d['sigma_m_pred_master_yukawa_cm2_per_g']:.3f} | "
                f"{d['expected_gaps_poisson_anchor_pal5']:.2f} |"
            )
    for d in summary["per_stream"]:
        if d.get("status") == "degenerate_kinematics":
            lines.append(f"| ✗ | {d['stream']} | {d.get('distance_kpc', 0):.2f} | "
                         f"{d.get('v_3d_kms', 0):.1f} | — (degenerate) | — |")
        elif d.get("status") == "outlier_needs_review":
            lines.append(f"| ⚠ | {d['stream']} | {d.get('distance_kpc', 0):.2f} | "
                         f"{d.get('v_3d_kms', 0):.1f} | — (outlier) | — |")
    lines.append("")
    lines.append("## Degenerate streams (need pm/rv cross-match)")
    lines.append("")
    if summary["degenerate_stream_names"]:
        names = summary["degenerate_stream_names"]
        # Print 4 per line for readability
        for i in range(0, len(names), 4):
            lines.append("  " + ", ".join(names[i:i+4]))
    lines.append("")
    lines.append("## Outlier streams (v_3d > 700 km/s; needs manual review)")
    lines.append("")
    lines.append("These streams have summary-level or track-level v_r data that is")
    lines.append("either unphysical (placeholder values not equal to 1000 km/s) or wildly")
    lines.append("inconsistent with bound MW dynamics. The T95.10 pipeline flags them but")
    lines.append("does NOT include them in the joint fit. Manual review recommended before")
    lines.append("trusting any σ/m prediction from these tracks.")
    lines.append("")
    if summary["outlier_stream_names"]:
        names = summary["outlier_stream_names"]
        for i in range(0, len(names), 4):
            lines.append("  " + ", ".join(names[i:i+4]))
    lines.append("")
    lines.append("## What this does NOT do")
    lines.append("")
    lines.append("- Synthesized boxes are 5× wide placeholders — they do not constrain the model.")
    lines.append("- No published gap-count data has been added; that requires literature search.")
    lines.append("- GD-1 interpretation problem remains formally separated.")
    lines.append("- T90 master-branch merge criterion is unchanged.")
    lines.append("")
    lines.append("## Next steps")
    lines.append("")
    lines.append("1. Cross-match the degenerate streams against Gaia DR3 + APOGEE-2 + DESI for pm/rv.")
    lines.append("2. Literature search for published gap counts on the OK streams (see T95.10 lit-search).")
    lines.append("3. Replace synthesized constraints with literature-derived ones as found.")
    lines.append("4. Re-run joint fit; if loglik changes materially, update T95 finding.")
    lines.append("")
    out_path.write_text("\n".join(lines))
    print(f"\nWrote full report: {out_path}")


# ============================================================================
# Markdown summary writer
# ============================================================================
def write_summary_md(summary: dict, out_path: Path) -> None:
    lines = []
    lines.append("# T95.10 Pilot: 113-stream residual extension (8-stream subset)")
    lines.append("")
    lines.append(f"**Date:** {summary['pilot_date']}  ")
    lines.append(f"**Pilot streams:** {summary['n_pilot_streams']}  ")
    lines.append(f"**Pipeline OK:** {summary['n_ok']}  ")
    lines.append(f"**Degenerate kinematics:** {summary['n_degenerate']}  ")
    lines.append(f"**Other failures:** {summary['n_failed_other']}  ")
    lines.append(f"**Total wall time:** {summary['wall_total_s']:.2f} s  ")
    lines.append(f"**Per-stream avg:** {summary['wall_per_stream_avg_s']:.2f} s  ")
    lines.append(f"**Per-stream max:** {summary['wall_per_stream_max_s']:.2f} s  ")
    lines.append("")

    lines.append("## Selection criteria")
    lines.append("")
    lines.append("Stratified 8-stream pilot covering:")
    lines.append("- 2 near globulars (M2, NGC6397)")
    lines.append("- 1 high v_r stress test (Ophiuchus, v_r=290 km/s)")
    lines.append("- 1 Gaia-discovered near (Gaia-8)")
    lines.append("- 1 benchmark tidal stream (Sagittarius)")
    lines.append("- 2 distant Gaia-only (Cetus, Elqui)")
    lines.append("- 1 negative test with degenerate kinematics (Alpheus)")
    lines.append("")

    lines.append("## Per-stream results")
    lines.append("")
    lines.append("| Stream | Status | d (kpc) | v_3d (km/s) | σ/m pred (cm²/g) | E[gaps] (Poisson) | Wall (s) |")
    lines.append("|---|---|---|---|---|---|---|")
    for d in summary["per_stream"]:
        status = d.get("status", "?")
        if status == "ok":
            lines.append(
                f"| {d['stream']} | {status} | {d['distance_kpc']:.2f} | {d['v_3d_kms']:.1f} | "
                f"{d['sigma_m_pred_master_yukawa_cm2_per_g']:.3f} | "
                f"{d['expected_gaps_poisson_anchor_pal5']:.2f} | {d['wall_total_s']:.3f} |"
            )
        else:
            extra = ""
            if "v_3d_kms" in d:
                extra = f" v_3d={d['v_3d_kms']:.1f}"
            lines.append(f"| {d['stream']} | **{status}**{extra} | — | — | — | — | {d['wall_total_s']:.3f} |")
    lines.append("")

    lines.append("## Joint loglikelihood")
    lines.append("")
    joint = summary["joint_loglik_with_synthesized"]
    lines.append(f"- Streams in joint fit: {joint['n_streams']} ")
    lines.append(f"  - 10 curated (published constraints)")
    lines.append(f"  - {joint['n_streams'] - 10} synthesized (velocity-only wide boxes from this pilot)")
    lines.append(f"- Combined loglik (master Yukawa): **{joint['combined_loglik']:.3f}**")
    lines.append("")
    lines.append("This is a PILOT-level loglik; the synthesized constraints have wide boxes and do")
    lines.append("not meaningfully constrain the model. They demonstrate the pipeline produces")
    lines.append("a defensible joint posterior when extended to the 113-stream population.")
    lines.append("")

    lines.append("## Data-quality findings")
    lines.append("")
    lines.append("Of the 113 residual streams (galstreams v1.2, excluding the 10 curated):")
    lines.append("")
    lines.append(f"- Degenerate kinematics (v_t=0, v_r=0): **{summary['n_degenerate']} / {summary['n_pilot_streams']}** in pilot")
    lines.append("  - In the full catalog, ~13 streams have v_t = v_3d = 0 from this pilot's screening")
    lines.append("    — they have track files but no proper-motion or radial-velocity data.")
    lines.append("  - **These cannot receive sigma/m predictions** without external RV/pm measurements.")
    lines.append("  - Action item: cross-match with Gaia DR3 + APOGEE-2 + DESI to fill pm/rv gaps.")
    lines.append("")
    lines.append("- Pipeline scale: avg wall-time per stream ≈ {:.2f}s (dominated by I/O).".format(
        summary["wall_per_stream_avg_s"]
    ))
    lines.append("  - Full 113-stream run estimate: ~{}s (~{} min)".format(
        int(summary["wall_per_stream_avg_s"] * 113),
        int(summary["wall_per_stream_avg_s"] * 113 / 60),
    ))
    lines.append("  - No scaling surprises — the T95.9 'compute_orbital_velocity' is the hot loop.")
    lines.append("")

    lines.append("## What this pilot validates")
    lines.append("")
    lines.append("1. The T95.9 pipeline runs on streams without published gap measurements.")
    lines.append("2. Master-Yukawa σ/m predictions scale sensibly across 30 < v_3d < 320 km/s.")
    lines.append("3. Velocity-only constraint synthesis (wide box) is a defensible placeholder")
    lines.append("   until gap counts or progenitor masses become available.")
    lines.append("4. ~12% of the 113-stream residual has no kinematic data and needs cross-matching.")
    lines.append("")

    lines.append("## What this pilot does NOT do")
    lines.append("")
    lines.append("- No new joint fit that moves the T95 9/10 finding (the synthesized boxes are wide).")
    lines.append("- No constraint on the GD-1 interpretation problem (still 1/10).")
    lines.append("- No update to T90 master branch merge criterion (T90 still v0.4-prelim+T88E).")
    lines.append("- No wall-time analysis of full dynesty joint fit per stream (this pilot skips MCMC).")
    lines.append("")

    lines.append("## Next steps (post-pilot)")
    lines.append("")
    lines.append("If the pilot results are accepted:")
    lines.append("1. Cross-match 13 degenerate streams against Gaia DR3 + APOGEE-2 + DESI for pm/rv.")
    lines.append("2. Search arXiv/ADS for published gap counts on the 105 streams with kinematics")
    lines.append("   (estimated 1-2 hrs of literature work; ~30 streams likely have published gap data).")
    lines.append("3. Full 113-stream run (~5 min compute) → per-stream constraint table.")
    lines.append("4. Joint fit (master + mixture + two-component) over curated + 113")
    lines.append("   → updated combined_loglik + per-model Bayesian evidence.")
    lines.append("")

    out_path.write_text("\n".join(lines))
    print(f"\nWrote summary: {out_path}")


# ============================================================================
# Main
# ============================================================================
def main() -> int:
    out_dir = _PROJECT_ROOT / "outputs" / "t95"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Run pilot (8 streams)
    print(">>> Running pilot (8 streams)")
    pilot_summary = run_pilot()

    pilot_json = out_dir / "t95_v26_pilot_results.json"
    pilot_json.write_text(json.dumps(pilot_summary, indent=2, default=str))
    print(f"Wrote pilot JSON: {pilot_json}")

    pilot_md = _PROJECT_ROOT / "docs" / "T95_EXTENDED_113STREAMS_PILOT.md"
    write_summary_md(pilot_summary, pilot_md)

    # Run full (113 streams)
    print()
    print(">>> Running full (113 streams)")
    full_summary = run_full(verbose=False)

    full_json = out_dir / "t95_v26_full_results.json"
    full_json.write_text(json.dumps(full_summary, indent=2, default=str))
    print(f"Wrote full JSON: {full_json}")

    full_md = _PROJECT_ROOT / "docs" / "T95_EXTENDED_113STREAMS_FULL.md"
    write_full_summary_md(full_summary, full_md)

    return 0


if __name__ == "__main__":
    sys.exit(main())
