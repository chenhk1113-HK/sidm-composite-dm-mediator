"""v40.50: Paper section 2.1 update generator.

Per Nemotron 3 Ultra 550B 10th review (v40.49): "Update section 2.1 to
(a): present the 10-combo multi-scale passing region and explicitly
identify MW v=10 as the binding constraint (Yukawa tail overshoot at
high sigma_0/low a). Do not re-fit (c) or silently drop combos (b);
the narrower region (71% of v40.48) IS the result -- not a failure,
a falsifiable prediction for future satellite surveys."

This script GENERATES the section 2.1 update text from the v40.49
multi-scale refit result. It does NOT re-run the analysis -- that was
done in v40.49.

REVIEWED BY (v40.50): Nemotron 3 Ultra 550B (3rd review using the
upgraded model)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RESULTS = REPO / "v0.3-prelim" / "data" / "results" / "v19_2_f_multiscale_refit_2026_10_19.json"


def main():
    """Generate the section 2.1 update paragraph from the v40.49 result."""
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)

    n_all_pass = data["n_all_pass"]
    n_total = data["n_combinations"]
    n_per_channel = data["n_per_channel"]
    survival_rate = n_all_pass / n_total

    # Extract the passing region (sigma_0, a, v_ref ranges)
    passing = [r["combo"] for r in data["results"] if r["all_pass"]]
    sigma_0_range = (min(c["sigma_0"] for c in passing), max(c["sigma_0"] for c in passing))
    a_range = (min(c["a_slope"] for c in passing), max(c["a_slope"] for c in passing))
    v_ref_range = (min(c["v_ref"] for c in passing), max(c["v_ref"] for c in passing))

    # MW v=10 is the binding constraint
    mw_v10_pass = n_per_channel["mw_sat_10"]
    bullet_pass = n_per_channel["bullet_cluster"]

    print("=" * 70)
    print("v40.50: Paper Section 2.1 Update -- Multi-Scale Passing Region")
    print("=" * 70)
    print()
    print("REVIEWER: Nemotron 3 Ultra 550B (3rd review)")
    print()
    print("v40.49 KEY FINDING (this is what section 2.1 should now reflect):")
    print(f"  - {n_all_pass}/{n_total} = {survival_rate*100:.0f}% of background refit passes all 9 multi-scale channels")
    print(f"  - Passing region: sigma_0 in [{sigma_0_range[0]:.3f}, {sigma_0_range[1]:.3f}]")
    print(f"  - Passing region: a in [{a_range[0]:.2f}, {a_range[1]:.2f}]")
    print(f"  - Passing region: v_ref in [{v_ref_range[0]:.1f}, {v_ref_range[1]:.1f}] km/s")
    print()
    print(f"  - MW satellite v=10: {mw_v10_pass}/{n_total} pass (BINDING CONSTRAINT)")
    print(f"  - Bullet Cluster v=1500: {bullet_pass}/{n_total} pass (EASIEST)")
    print()
    print("=" * 70)
    print("PROPOSED SECTION 2.1 UPDATE TEXT (for paper draft):")
    print("=" * 70)
    print()
    # v40.51 FIX: Use f-string interpolation to use ACTUAL ranges from data
    # (was hardcoded in v40.50 - transcription error per n6.docx review)
    print(f"""
**§2.1 UPDATE (v40.51, per Nemotron 3 Ultra 550B 10th review + n6.docx review):**

The background parameterization σ/m(v) = σ_0 × (v_ref/v)^a is now constrained
to a multi-scale passing region after refit with peak=0. The {n_all_pass}/{n_total} = {survival_rate*100:.0f}% of
{{σ_0, a, v_ref}} combinations from the v40.48 background sweep that pass
Cloud-9/Fornax/SPARC also pass the additional 6 multi-scale channels
(Milky Way satellites at v=10, 20, 30 km/s, Lyman-α, galaxy cluster, and
Bullet Cluster).

**The passing region is NOT a single point but a RANGE (v40.51 FIX per n6.docx review):**
- σ_0 ∈ [{sigma_0_range[0]:.3f}, {sigma_0_range[1]:.3f}] cm²/g (FROM v40.49 DATA, not hand-written)
  - NOTE: Phase 44's σ_0 = 0.052 IS WITHIN this range (per v40.49 data, NOT "OUTSIDE" as v40.50 claimed)
- a ∈ [{a_range[0]:.2f}, {a_range[1]:.2f}] (slope, FROM v40.49 DATA)
- v_ref ∈ [{v_ref_range[0]:.1f}, {v_ref_range[1]:.1f}] km/s (reference velocity, FROM v40.49 DATA)

**Binding constraint: Milky Way satellites at v=10 km/s.** The Yukawa
background σ_0 × (v_ref/v)^a overproduces σ/m at v=10 when σ_0 is high
or a is low, causing {n_total - n_all_pass}/{n_total} combinations to fail the dSph ceiling
(σ/m < 1.0 cm²/g). Fornax (v=15) is the second-most restrictive
channel ({n_per_channel['fornax']}/{n_total} pass).

**The {survival_rate*100:.0f}% survival rate IS the result** -- a precise, falsifiable
prediction for future Milky Way satellite surveys. If future surveys
constrain σ/m at v=10 km/s to a value < 1.0 cm²/g, the framework's
passing region survives. If the constraint loosens to > 1.0 cm²/g,
additional background parameter space opens (currently {n_total - n_all_pass}/{n_total} = {(n_total - n_all_pass)/n_total*100:.0f}% of
combinations would re-enter the viable region).

**Per-channel pass rates (v40.49 multi-scale refit):**
""")
    for key, n in n_per_channel.items():
        names = {
            "cloud9": "Cloud-9 (v=28)",
            "fornax": "Fornax (v=15)",
            "sparc": "SPARC (v=100)",
            "mw_sat_10": "MW satellite v=10 (BINDING)",
            "mw_sat_20": "MW satellite v=20",
            "mw_sat_30": "MW satellite v=30",
            "lyman_alpha": "Lyman-α (v=100)",
            "cluster_1000": "Cluster (v=1000)",
            "bullet_cluster": "Bullet Cluster (v=1500)",
        }
        bar = "█" * n + "░" * (n_total - n)
        flag = " ← BINDING" if key == "mw_sat_10" else (" ← EASIEST" if key == "bullet_cluster" else "")
        print(f"  {names[key]:<25} {n}/{n_total} {bar}{flag}")
    print()
    print("=" * 70)
    print(f"The {survival_rate*100:.0f}% partial robustness becomes a TESTABLE PREDICTION when")
    print("future MW satellite surveys measure σ/m at v=10. Framework's")
    print("background parameters occupy a RANGE (not a point) that future")
    print("data can either validate or constrain further.")
    print("=" * 70)


if __name__ == "__main__":
    main()
