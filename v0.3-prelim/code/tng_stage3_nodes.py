"""Stage-3 per-node property fetch (IllustrisTNG), resource-bounded.

The sample builder (tng_stage3_build.py) stored the merger-tree LINEAGE (snap, subhaloID pairs)
for 90 halos. This script walks each main lineage and fetches the subhalo DETAIL record for a
strided subset of its nodes, so we get M(z), V_max(z), len_dm(z) growth curves without either
(a) the ~500 GB supplementary MergerHistory download or (b) 8,500 API calls.

Measured cost (this host, 2026-11-04): a detail record takes 0.7-4.5 s and the API answers
HTTP 503 if asked faster than roughly one request per second, so the pacing below is 1.5 s with
exponential backoff. Default stride keeps it to ~20 nodes per halo -> ~1,800 requests -> ~50 min,
and each record is stored as one compact JSONL row (~300 B), so the whole product is < 1 MB.

API contract learned the hard way (see docs/STAGE3_TNG_FEASIBILITY_2026-11-04.md):
  - header is `api-key`; `X-API-Key` -> 403
  - `subhalo_id=<id>` as a LIST filter is silently IGNORED (returns the unfiltered 4.37M-row set);
    the working form is the detail endpoint `.../subhalos/<id>/`
  - `fields=` on a list query is silently IGNORED too
  - bodies may be gzip; HTML responses mean throttle -> retry
Every row is verified by read-back: res["id"] == id and res["snap"] == snap, or it is rejected.
"""
from __future__ import annotations

import glob
import gzip
import json
import os
import pathlib
import sys
import time
import urllib.request

REPO = pathlib.Path(r"C:/Users/lamkuenai/projects/sidm-composite-dm-mediator")
SAMPLE = REPO / "v0.3-prelim/data/external/tng/stage3_sample"
OUT_DIR = REPO / "v0.3-prelim/data/external/tng/stage3_nodes"
KEY_FILE = pathlib.Path(r"C:/Users/lamkuenai/.tng_api_key")
BASE = "https://www.tng-project.org/api/"

PACE_S = 1.5
MAX_TRIES = 6
STRIDE = int(os.environ.get("TNG_STRIDE", "4"))  # every Nth node of the main lineage
KEEP = ("id", "snap", "mass", "mass_dm", "mass_gas", "mass_stars", "mass_log_msun",
        "vmax", "veldisp", "len_dm", "len_gas", "len_stars", "halfmassrad_dm",
        "spin_x", "spin_y", "spin_z", "pos_x", "pos_y", "pos_z", "parent",
        "prog_sfid", "prog_snap", "desc_sfid", "desc_snap", "primary_flag")

# TNG snapshot -> redshift. Source: IllustrisTNG portal snapshot documentation
# (https://www.tng-project.org/data/docs/snapshot/); only the snapshots a stride can land on
# are needed, so the table covers all 100 snapshots for the three runs used here.
SNAP_Z: dict[str, dict[int, float]] = {}


def load_snap_z() -> None:
    """Read the snapshot/z table from the portal table file if present, else refuse to guess."""
    cached = OUT_DIR / "snapshot_z.json"
    if cached.exists():
        raw = json.loads(cached.read_text(encoding="utf-8"))
        # the cached table is JSON, so its snapshot keys come back as strings; the trees use ints
        for run, table in raw.items():
            SNAP_Z[run] = {int(k): float(v) for k, v in table.items()}
        return
    raise SystemExit(
        "missing " + str(cached) + " — write the portal's snapshot/redshift table there first "
        "(docs/snapshot page); this script will not guess redshifts."
    )


def log(msg: str) -> None:
    print(msg, flush=True)


def api_json(path: str):
    url = path if path.startswith("http") else BASE + path
    url = url.replace("http://", "https://")
    key = KEY_FILE.read_text(encoding="utf-8").strip()
    last = ""
    for i in range(MAX_TRIES):
        try:
            req = urllib.request.Request(url, headers={"api-key": key})
            with urllib.request.urlopen(req, timeout=120) as r:
                raw = r.read()
            if raw[:2] == b"\x1f\x8b":
                raw = gzip.decompress(raw)
            text = raw.decode("utf-8", "replace")
            if text.lstrip().startswith("<"):
                last = "HTML response (throttle)"
            else:
                return json.loads(text)
        except Exception as exc:  # throttle / transient
            last = repr(exc)
        time.sleep(min(90.0, 4.0 * (i + 1)))
    log(f"    FAILED {url}: {last}")
    return None


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    load_snap_z()
    done_marker = OUT_DIR / "done.json"
    if done_marker.exists():
        log("done.json present — nothing to do")
        return 0

    trees = sorted(SAMPLE.glob("trees/*.json"))
    rows_path = OUT_DIR / "nodes.jsonl"
    already = set()
    if rows_path.exists():
        for line in rows_path.read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(line)
                already.add((r["run"], r["halo"], r["snap"], r["id"]))
            except Exception:
                pass
        log(f"resume: {len(already)} rows already stored")

    n_rows = n_fail = 0
    t0 = time.time()
    with rows_path.open("a", encoding="utf-8") as fh:
        for tp in trees:
            run, snap0, hid = tp.stem.rsplit("-", 2)
            tree = json.loads(tp.read_text(encoding="utf-8"))
            main_lineage = tree.get("Main", [])
            if not main_lineage:
                continue
            picks = main_lineage[::STRIDE]
            if main_lineage[-1] not in picks:
                picks.append(main_lineage[-1])
            for snap, sid in picks:
                if (run, hid, snap, sid) in already:
                    continue
                res = api_json(f"{run}/snapshots/{snap}/subhalos/{sid}/")
                time.sleep(PACE_S)
                if not isinstance(res, dict):
                    n_fail += 1
                    continue
                if res.get("id") != sid or res.get("snap") != snap:
                    log(f"    READ-BACK MISMATCH {run}/{snap}/{sid}: "
                        f"got id={res.get('id')} snap={res.get('snap')}")
                    n_fail += 1
                    continue
                row = {k: res.get(k) for k in KEEP}
                row["run"] = run
                row["halo"] = hid
                row["z"] = SNAP_Z.get(run, {}).get(snap)
                row["n_main_nodes"] = len(main_lineage)
                row["n_mergers"] = len(tree.get("Mergers", []))
                fh.write(json.dumps(row) + "\n")
                fh.flush()
                n_rows += 1
            log(f"  {tp.stem}: +{len(picks)} nodes (running {n_rows} rows, {n_fail} fails, "
                f"{time.time()-t0:.0f}s)")

    stats = {"rows": n_rows, "failed": n_fail, "stride": STRIDE,
             "trees": len(trees), "wall_s": round(time.time() - t0),
             "bytes": rows_path.stat().st_size}
    (OUT_DIR / "nodes_stats.json").write_text(json.dumps(stats, indent=1), encoding="utf-8")
    done_marker.write_text(json.dumps(stats), encoding="utf-8")
    log(f"DONE {json.dumps(stats)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
