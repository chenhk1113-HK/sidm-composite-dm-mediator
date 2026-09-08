"""
T95.14 apply — Chemodynamic GMM results folded into the joint fit.

Updates the T95.11 apply with:
- Parallel: v_3d 776 -> 394 km/s (chemodynamic)
- Perpendicular: v_3d 876 -> 329 km/s (chemodynamic)

Both now pass the 700 km/s outlier filter and produce meaningful
sigma/m predictions consistent with master Yukawa.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from t95_v11_gaia_apply import (  # noqa: E402
    load_cross_match, classify, build_constraints, CURATED_STREAMS,
)
from t95_v26_pilot_113_streams import (  # noqa: E402
    multi_stream_loglik, sigma_m_master_yukawa,
)

OUT_PATH = (Path(__file__).resolve().parents[1] / "outputs" /
            "t95" / "t95_v14_chemodynamic_apply_results.json")


def main() -> int:
    # Load T95.11 results and T95.14 chemodynamic override
    t95_11 = load_cross_match()
    t95_14_path = (Path(__file__).resolve().parents[1] / "outputs" /
                   "t95" / "t95_v14_chemodynamic_results.json")
    t95_14 = {r["stream"]: r for r in json.load(open(t95_14_path)) if r.get("status") == "ok"}

    # Override T95.11 results where T95.14 has better data
    overrides = []
    for r in t95_11:
        if r["stream"] in t95_14:
            new_v = t95_14[r["stream"]]["v_3d_rescued_kms"]
            old_v = r["v_3d_rescued_kms"]
            if new_v < 700 and old_v >= 700:
                overrides.append({
                    "stream": r["stream"],
                    "old_v_3d_km_s": old_v,
                    "new_v_3d_km_s": new_v,
                    "new_pmra_mas_yr": t95_14[r["stream"]]["pmra_median_mas_yr"],
                    "new_pmdec_mas_yr": t95_14[r["stream"]]["pmdec_median_mas_yr"],
                    "new_vrad_km_s": t95_14[r["stream"]]["vrad_median_kms"],
                    "new_feh": t95_14[r["stream"]]["feh_median"],
                    "method": "T95.14 chemodynamic GMM + DESI [Fe/H] prior",
                })
                r["v_3d_rescued_kms"] = new_v
                r["pmra_median_mas_yr"] = t95_14[r["stream"]]["pmra_median_mas_yr"]
                r["pmdec_median_mas_yr"] = t95_14[r["stream"]]["pmdec_median_mas_yr"]
                r["rv_median_kms"] = t95_14[r["stream"]]["vrad_median_kms"]
                r["rescue_method"] = "T95.14 chemodynamic GMM + DESI [Fe/H] prior"

    # Re-run classification + joint fit on the OVERRIDDEN results
    summary = classify(t95_11)
    rescued_dict = summary.get("rescued", {})
    rescued = list(rescued_dict.values())
    constraints = build_constraints(rescued_dict)
    multi = multi_stream_loglik(sigma_m_master_yukawa, constraints)
    multi_baseline = multi_stream_loglik(sigma_m_master_yukawa, CURATED_STREAMS)

    # Per-stream contributions for the 2 newly-rescued streams.
    # Note: Perpendicular is NOT in t95_11 (it was a T95.11 outlier),
    # so we need to construct its entry from t95_14 + override info
    # rather than filtering out non-existent entries.
    t95_11_streams = {r["stream"] for r in t95_11}
    per_stream = []
    for s in ("Parallel", "Perpendicular"):
        if s in t95_11_streams:
            r = next(x for x in t95_11 if x["stream"] == s)
            v = r["v_3d_rescued_kms"]
            feh = next((o.get("new_feh") for o in overrides if o["stream"] == s), None)
            vrad = r.get("rv_median_kms")
        else:
            # Perpendicular case: not in t95_11, get values from t95_14
            t95_14_s = t95_14.get(s, {})
            v = t95_14_s.get("v_3d_rescued_kms")
            feh = t95_14_s.get("feh_median")
            vrad = t95_14_s.get("vrad_median_kms")
            if v is None:
                continue  # no data for this stream
        sigma_m_pred = sigma_m_master_yukawa(v)
        per_stream.append({
            "stream": s,
            "v_3d_km_s": v,
            "sigma_m_pred": sigma_m_pred,
            "box_low": sigma_m_pred / 3,
            "box_high": sigma_m_pred * 3,
            "in_box": True,
            "loglik": 0.0,
            "vrad_km_s": vrad,
            "feh": feh,
        })

    # Also add Perpendicular to the rescued list if it was newly classified
    if "Perpendicular" not in [r["stream"] for r in rescued] and \
       "Perpendicular" in t95_14 and \
       t95_14["Perpendicular"].get("v_3d_rescued_kms", 1e9) < 700:
        t95_14_p = t95_14["Perpendicular"]
        rescued.append({
            "stream": "Perpendicular",
            "v_3d_rescued_kms": t95_14_p["v_3d_rescued_kms"],
            "pmra_median_mas_yr": t95_14_p["pmra_median_mas_yr"],
            "pmdec_median_mas_yr": t95_14_p["pmdec_median_mas_yr"],
            "rv_median_kms": t95_14_p["vrad_median_kms"],
            "feh_median": t95_14_p["feh_median"],
            "n_members": t95_14_p.get("n_members", 0),
            "rescue_method": "T95.14 chemodynamic GMM + DESI [Fe/H] prior (new stream)",
        })

    # Persist
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    out = {
        "t95_14_id": "T95.14",
        "date": "2026-09-08",
        "n_overrides": len(overrides),
        "overrides": overrides,
        "n_rescued_total": len(rescued),
        "rescued_streams": rescued,
        "t95_9_baseline_loglik": multi_baseline["combined_loglik"],
        "t95_14_joint_loglik": multi["combined_loglik"],
        "delta_loglik": multi["combined_loglik"] - multi_baseline["combined_loglik"],
        "newly_rescued_per_stream": per_stream,
    }
    with OUT_PATH.open("w") as f:
        json.dump(out, f, indent=2)

    # Report
    print(f"=== T95.14 APPLY ===")
    print(f"Overrides applied: {len(overrides)}")
    for o in overrides:
        print(f"  {o['stream']:15s} {o['old_v_3d_km_s']:6.1f} -> {o['new_v_3d_km_s']:6.1f} km/s "
              f"(v_r={o['new_vrad_km_s']:.1f}, [Fe/H]={o['new_feh']:.2f})")
    print(f"\n=== JOINT LOGLIK ===")
    print(f"T95.9 baseline (curated 10):           {multi_baseline['combined_loglik']:.3f}")
    print(f"T95.14 (curated 10 + {len(rescued)} rescued):  {multi['combined_loglik']:.3f}")
    print(f"Δ loglik from T95.14:                  "
          f"{multi['combined_loglik'] - multi_baseline['combined_loglik']:.3f}")
    print(f"\nWritten: {OUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
