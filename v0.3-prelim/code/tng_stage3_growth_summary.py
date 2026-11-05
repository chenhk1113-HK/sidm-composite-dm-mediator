"""Stage-3 growth and merger-timing summary from the locally stored TNG products.

Inputs (all local, produced by tng_stage3_build.py and tng_stage3_nodes.py):
  v0.3-prelim/data/external/tng/stage3_{sample,anchor}/trees/*.json   Main lineage + merger list
  v0.3-prelim/data/external/tng/stage3_nodes/nodes.jsonl              per-node M, Vmax, len_dm, z
  v0.3-prelim/data/external/tng/stage3_nodes/snapshot_z.json          snapshot -> z (from the API)

Outputs:
  v0.3-prelim/data/results/tng_stage3_growth_summary.json

Why this exists: `phase_g2_merger_history.py` modulates the SIDM collapse time by a merger
history using multipliers taken from literature labels (x0.7 quiescent / x8.0 active). The trees
now on disk let the merger statistics be measured instead of asserted. This script deliberately
reports only what the stored products support: assembly fractions, V_max growth, and merger
counts/timing. It does not fit anything and does not touch the SIDM model.
"""
from __future__ import annotations

import json
import statistics as st
from pathlib import Path

REPO = Path(__file__).resolve().parents[1].parent
EXT = REPO / "v0.3-prelim" / "data" / "external" / "tng"
H = 0.6774
UNIT = 1e10 / H  # native SubhaloMass -> Msun


def load_zmaps():
    return {run: {int(k): float(v) for k, v in table.items()}
            for run, table in json.loads((EXT / "stage3_nodes" / "snapshot_z.json")
                                         .read_text(encoding="utf-8")).items()}


def halo_stats(tree_path: Path, nodes_by_halo: dict, zmap: dict) -> dict:
    tree = json.loads(tree_path.read_text(encoding="utf-8"))
    run, halo = tree_path.stem.split("-", 1)[0] + "-" + tree_path.stem.split("-")[1], None
    # filename convention: {RUN}-{SNAP}-{SUBHALO_ID}.json  (RUN contains a dash: TNG50-1)
    parts = tree_path.stem.split("-")
    run = f"{parts[0]}-{parts[1]}"
    halo = parts[3]
    z0 = zmap.get(run, {})

    mergers = [m for m in tree.get("Mergers", [])]
    mz = [(z0.get(int(m[0])), int(m[0])) for m in mergers]
    merger_z = sorted([z for z, _ in mz if z is not None], reverse=True)

    nodes = nodes_by_halo.get((run, halo), [])
    curve = sorted([(n["z"], n) for n in nodes if n.get("z") is not None], key=lambda t: t[0])
    if not curve:
        return None
    z_min, node0 = curve[0]          # curve sorted ascending in z -> first is z ~ 0
    m0 = node0["mass"] * UNIT
    vmax0 = node0["vmax"]

    def frac_at(z_target):
        """M(z)/M(0) by nearest-node interpolation on the stored (sparse) curve."""
        if m0 <= 0:
            return None
        zs = [z for z, _ in curve]
        if z_target < zs[0] or z_target > zs[-1]:
            return None
        for i in range(len(curve) - 1):
            z_a, a = curve[i]
            z_b, b = curve[i + 1]
            if z_a <= z_target <= z_b:
                if z_b == z_a:
                    return (b["mass"] * UNIT) / m0
                w = (z_target - z_a) / (z_b - z_a)
                m = a["mass"] * UNIT + w * (b["mass"] * UNIT - a["mass"] * UNIT)
                return m / m0
        return None

    def vmax_at(z_target):
        zs = [z for z, _ in curve]
        if z_target < zs[0] or z_target > zs[-1]:
            return None
        best = min(curve, key=lambda t: abs(t[0] - z_target))
        return best[1]["vmax"]

    def z_form(fraction):
        """Redshift where the main lineage last held `fraction` of its z=0 mass (None if never)."""
        prev = None
        for z, n in curve:
            f = (n["mass"] * UNIT) / m0 if m0 > 0 else None
            if f is None:
                continue
            if prev and prev[1] < fraction <= f:
                z_a, f_a = prev
                z_b, f_b = z, f
                if f_b == f_a:
                    return z_b
                return z_a + (fraction - f_a) * (z_b - z_a) / (f_b - f_a)
            prev = (z, f)
        return None

    return {
        "run": run,
        "halo": halo,
        "snap0": int(parts[2]),
        "m0_msun": m0,
        "vmax0_kms": vmax0,
        "halfmassrad0_kpc": node0.get("halfmassrad_dm"),
        "len_dm0": node0.get("len_dm"),
        "lineage_nodes_stored": len(nodes),
        "lineage_top_z": curve[-1][0],
        "assembly_frac_z0.5": frac_at(0.5),
        "assembly_frac_z1": frac_at(1.0),
        "assembly_frac_z2": frac_at(2.0),
        "assembly_frac_z3": frac_at(3.0),
        "z_form_0.5": z_form(0.5),
        "z_form_0.25": z_form(0.25),
        "vmax_at_z1": vmax_at(1.0),
        "vmax_at_z2": vmax_at(2.0),
        "n_mergers": len(mergers),
        "n_mergers_z_ge_1": sum(1 for z in merger_z if z >= 1.0),
        "n_mergers_z_lt_1": sum(1 for z in merger_z if z < 1.0),
        "earliest_merger_z": max(merger_z) if merger_z else None,
        "latest_merger_z": min(merger_z) if merger_z else None,
    }


def summarise(rows: list) -> dict:
    def med(key):
        vals = [r[key] for r in rows if r.get(key) is not None]
        return st.median(vals) if vals else None

    def q(key, p):
        vals = sorted(r[key] for r in rows if r.get(key) is not None)
        if not vals:
            return None
        i = min(len(vals) - 1, max(0, int(round(p * (len(vals) - 1)))))
        return vals[i]

    quiet = sum(1 for r in rows if r["n_mergers_z_lt_1"] == 0)
    return {
        "n_halos": len(rows),
        "m0_msun": {"min": min(r["m0_msun"] for r in rows),
                    "median": med("m0_msun"),
                    "max": max(r["m0_msun"] for r in rows)},
        "vmax0_kms": {"min": min(r["vmax0_kms"] for r in rows),
                      "median": med("vmax0_kms"),
                      "max": max(r["vmax0_kms"] for r in rows)},
        "len_dm0": {"min": min(r["len_dm0"] for r in rows if r["len_dm0"] is not None),
                    "median": med("len_dm0"),
                    "max": max(r["len_dm0"] for r in rows if r["len_dm0"] is not None)},
        "assembly_frac": {f"z{z}": {"median": med(k), "q25": q(k, 0.25), "q75": q(k, 0.75)}
                          for z, k in ((0.5, "assembly_frac_z0.5"), (1, "assembly_frac_z1"),
                                       (2, "assembly_frac_z2"), (3, "assembly_frac_z3"))},
        "z_form": {"z_form_0.5": {"median": med("z_form_0.5"), "q25": q("z_form_0.5", 0.25),
                                  "q75": q("z_form_0.5", 0.75)},
                   "z_form_0.25": {"median": med("z_form_0.25")}},
        "vmax_growth": {"median_vmax0_over_vmax_at_z1": None,
                        "per_halo_ratio_median": None},
        "mergers": {"median_total": med("n_mergers"),
                    "q25_total": q("n_mergers", 0.25),
                    "q75_total": q("n_mergers", 0.75),
                    "max_total": max(r["n_mergers"] for r in rows),
                    "median_z_ge_1": med("n_mergers_z_ge_1"),
                    "median_z_lt_1": med("n_mergers_z_lt_1"),
                    "max_z_lt_1": max(r["n_mergers_z_lt_1"] for r in rows),
                    "quiet_halos_no_merger_after_z1": quiet,
                    "quiet_fraction": quiet / len(rows) if rows else None,
                    "median_earliest_merger_z": med("earliest_merger_z"),
                    "median_latest_merger_z": med("latest_merger_z")},
    }


def main():
    zmap = load_zmaps()
    nodes_by_halo: dict = {}
    # tier-1 lineages live in stage3_nodes, the anchor-mass lineages in stage3_nodes_anchor
    nodes_paths = [EXT / d / "nodes.jsonl" for d in ("stage3_nodes", "stage3_nodes_anchor")]
    for nodes_path in nodes_paths:
        if not nodes_path.exists():
            continue
        for line in nodes_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            n = json.loads(line)
            nodes_by_halo.setdefault((n["run"], str(n["halo"])), []).append(n)

    out = {"inputs": {"trees": {}, "nodes_rows": sum(len(v) for v in nodes_by_halo.values())}}
    per_run_all = {}
    for sample in ("stage3_sample", "stage3_anchor"):
        trees = sorted((EXT / sample / "trees").glob("*.json"))
        if not trees:
            continue
        out["inputs"]["trees"][sample] = len(trees)
        rows = []
        for tp in trees:
            run = "-".join(tp.stem.split("-")[:2])
            if run not in zmap:
                continue
            r = halo_stats(tp, nodes_by_halo, zmap)
            if r:
                rows.append(r)
        by_run = {}
        for run in sorted({r["run"] for r in rows}):
            sub = [r for r in rows if r["run"] == run]
            by_run[run] = summarise(sub)
            per_run_all.setdefault(sample, {})[run] = sub
        out[sample] = {"by_run": by_run,
                       "combined": summarise(rows) if rows else None}

    # V_max growth ratio per halo (z=0 value over the z~1 value), computed after collection
    for sample, runs in per_run_all.items():
        for run, sub in runs.items():
            ratios = [r["vmax0_kms"] / r["vmax_at_z1"] for r in sub
                      if r.get("vmax_at_z1") and r["vmax_at_z1"] > 0]
            if ratios:
                out[sample]["by_run"][run]["vmax_growth"]["median_vmax0_over_vmax_at_z1"] = st.median(ratios)
                out[sample]["by_run"][run]["vmax_growth"]["n_halos_with_z1_node"] = len(ratios)

    out_path = REPO / "v0.3-prelim" / "data" / "results" / "tng_stage3_growth_summary.json"
    out_path.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "stage3_sample" and k != "stage3_anchor"},
                     indent=1))
    for sample in ("stage3_sample", "stage3_anchor"):
        if sample in out:
            print(f"\n=== {sample} ===")
            print(json.dumps(out[sample]["by_run"], indent=1))
    print(f"\nwritten: {out_path}")


if __name__ == "__main__":
    main()
