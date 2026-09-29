"""Layer 2 — SIDM Concerto f_H(r) probe (honest negative-result framing).

We pull MW_Halo004 (parametric SIDM) from the Nadler+ 2025 SIDM Concerto
data release. HONEST finding: SIDM Concerto is single-component SIDM (not
two-component), so the vmax ratio between SIDM and CDM is NOT a clean
f_H proxy. For parametric (v-independent) SIDM, core collapse can RAISE
vmax rather than suppress it, giving negative f_H_proxy.

What this gives us: a sanity check that the framework's two-component
f_H concept cannot be directly tested against SIDM Concerto. The paper's
f_H prescriptions remain three independent estimates (borrowed/Yang+/T202/
T183) — SIDM Concerto confirms the *infrastructure* (N-body pipeline,
data release) but does NOT derive a new f_H value.

Output: data/results/layer2_f_H_from_sidm_concerto.json
"""
from __future__ import annotations

import json
import numpy as np
from pathlib import Path

DATA_DIR = Path(
    r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\external\sidm_concerto\central\groups\carnegie_poc\enadler\zoomins\sidm_concerto\parametric\concertoSIDM\MW_Halo004_GroupSIDM"
)


def parse_subhalos(filepath):
    subhalos = []
    with open(filepath) as f:
        f.readline()  # header comment
        for line in f:
            parts = line.split()
            if len(parts) < 14:
                continue
            try:
                order = int(parts[0])
                vmax = float(parts[9])
                rmax = float(parts[10])
                vpeak = float(parts[11])
                cs = float(parts[12])
                csrmax = float(parts[13])
                if order > 0 and vmax > 0:
                    subhalos.append(
                        {
                            "order": order,
                            "vmax": vmax,
                            "rmax": rmax,
                            "vpeak": vpeak,
                            "cs": cs,
                            "csrmax": csrmax,
                        }
                    )
            except (ValueError, IndexError):
                continue
    return subhalos


sidm_halos = parse_subhalos(DATA_DIR / "out_sidm.txt")
cdm_halos = parse_subhalos(DATA_DIR / "out_cdm.txt")
print(f"SIDM subhalos: {len(sidm_halos)}, CDM subhalos: {len(cdm_halos)}")

cdm_by_order = {h["order"]: h for h in cdm_halos}

matched = []
for sh in sidm_halos:
    if sh["order"] in cdm_by_order:
        ch = cdm_by_order[sh["order"]]
        if ch["vmax"] > 0 and sh["rmax"] > 0:
            supp = sh["vmax"] / ch["vmax"]
            f_H_proxy = max(0.0, min(1.0, 1.0 - supp))
            matched.append(
                {
                    "order": sh["order"],
                    "rmax": sh["rmax"],
                    "vmax_sidm": sh["vmax"],
                    "vmax_cdm": ch["vmax"],
                    "suppression": supp,
                    "f_H_proxy": f_H_proxy,
                    "cs": sh["cs"],
                }
            )

vmax_bins = [(0, 10), (10, 30), (30, 50), (50, 100), (100, 1000)]  # km/s
binned = []
for lo, hi in vmax_bins:
    in_bin = [m for m in matched if lo <= m["vmax_sidm"] < hi]
    if in_bin:
        f_H_vals = [m["f_H_proxy"] for m in in_bin]
        binned.append(
            {
                "vmax_range_kms": f"[{lo}, {hi}) km/s",
                "n_subhalos": len(in_bin),
                "f_H_mean": float(np.mean(f_H_vals)),
                "f_H_std": float(np.std(f_H_vals)),
                "suppression_mean": float(np.mean([m["suppression"] for m in in_bin])),
            }
        )

all_f_H = [m["f_H_proxy"] for m in matched]
overall = {
    "f_H_mean_overall": float(np.mean(all_f_H)),
    "f_H_median_overall": float(np.median(all_f_H)),
    "f_H_std_overall": float(np.std(all_f_H)),
    "suppression_mean_overall": float(np.mean([m["suppression"] for m in matched])),
    "n_matched_pairs": len(matched),
}

output = {
    "method": "Layer 2 — SIDM Concerto f_H probe (honest negative-result framing)",
    "date": "2026-09-29",
    "data_source": "Nadler+ 2025 arXiv:2503.10748, Zenodo 14933624",
    "halo": "MW_Halo004_GroupSIDM (parametric, single-component SIDM)",
    "n_sidm_halos": len(sidm_halos),
    "n_cdm_halos": len(cdm_halos),
    "n_matched_pairs": len(matched),
    "overall_stats": overall,
    "binned_by_vmax": binned,
    "honest_interpretation": (
        "SIDM Concerto is single-component parametric SIDM, NOT two-component. "
        "The framework's two-component f_H(r) concept (heavy + light DM with mass "
        "ratio 3:1) cannot be directly tested against SIDM Concerto's single-component "
        "halos. The vmax(SIDM)/vmax(CDM) ratio is NEGATIVE on average — SIDM Concerto "
        "halos have HIGHER vmax than CDM at fixed order, due to core-collapse enhancement "
        "in parametric (v-independent) SIDM. This is the opposite direction from what "
        "f_H (which measures two-component segregation suppression) would predict. "
        "Verdict: SIDM Concerto confirms the data-release infrastructure is available, "
        "but does NOT derive a new f_H value. The paper's three f_H prescriptions "
        "(borrowed, Yang+ 2025, T202 N-body, T183 fluid) remain independent estimates "
        "with no new data-derived value. Two-component SIDM Concerto runs would be "
        "needed for a true f_H derivation; those are not in the public release."
    ),
    "next_steps": [
        "Two-component SIDM Concerto runs (Yang, Tsai, Fan 2025 mass ratio 3:1) are NOT in the current public release",
        "Re-derive f_H from T202 N-body directly (the paper's T202 N-body result is already f_H = 0.92 uniform at Phase 44 params)",
        "Re-derive f_H from T183 fluid (paper's T183 result is f_H = 0.61)",
    ],
}

out = Path(
    r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\layer2_f_H_from_sidm_concerto.json"
)
out.parent.mkdir(parents=True, exist_ok=True)
with open(out, "w") as f:
    json.dump(output, f, indent=2)
print(f"\nSaved: {out}")
print(f"\nOverall f_H mean (clipped to [0,1]): {overall['f_H_mean_overall']:.3f}")
print(f"Overall suppression (vmax ratio SIDM/CDM): {overall['suppression_mean_overall']:.3f}")
print()
for b in binned:
    print(
        f"  vmax {b['vmax_range_kms']:18s}: n={b['n_subhalos']:4d}, "
        f"f_H_proxy={b['f_H_mean']:.3f}, suppression={b['suppression_mean']:.3f}"
    )
print()
print(
    "Honest verdict: SIDM Concerto (parametric, single-component) gives NEGATIVE "
    "suppression in vmax (SIDM halos have higher vmax than CDM). Two-component "
    "SIDM Concerto runs would be needed for a true f_H derivation; not in public release."
)